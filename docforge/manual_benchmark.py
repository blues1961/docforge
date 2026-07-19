from __future__ import annotations

import argparse
import hashlib
import json
import re
import socket
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

from docforge.manual_deterministic import ManualDeterministicContentBuilder
from docforge.validators import CommandFidelityValidator

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_TIMEOUT_SECONDS = 3600
DEFAULT_MAX_OUTPUT_TOKENS = 2048
SCHEMA_VERSION = 1
VALIDATION_SCHEMA_VERSION = 5


class BenchmarkError(RuntimeError):
    pass


class ReferenceError(BenchmarkError):
    pass


class ResumeMismatchError(BenchmarkError):
    pass


class OllamaError(BenchmarkError):
    pass


class OllamaTimeoutError(OllamaError):
    def __init__(self, *, timeout_seconds: int, detail: str | None = None) -> None:
        self.timeout_seconds = timeout_seconds
        self.detail = detail
        message = f"Ollama n’a pas répondu avant le délai de {timeout_seconds} secondes."
        if detail:
            message = f"{message} {detail}"
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class ReferenceSection:
    index: int
    identifier: str
    title: str
    prompt_file: str
    context_file: str
    estimated_tokens: int | None
    context_budget: int | None
    prompt_sha256: str
    context_sha256: str
    deterministic_file: str | None = None

    @property
    def stem(self) -> str:
        return Path(self.prompt_file).stem


@dataclass(frozen=True, slots=True)
class ReferenceBundle:
    version: str
    root: Path
    knowledge_file: str
    manifest_file: str
    prompt_file: str
    prompt_prepared_file: str
    guide_file: str
    sections: list[ReferenceSection]
    manifest: dict[str, Any]
    metadata: dict[str, Any]
    checksums: dict[str, str]


@dataclass(frozen=True, slots=True)
class BenchmarkConfig:
    model: str
    reference_version: str
    run_id: str
    num_ctx: int
    temperature: float
    seed: int | None
    resume: bool
    ollama_url: str
    max_output_tokens: int
    timeout_seconds: int
    dry_run: bool
    allow_resource_increase: bool = False
    reassemble: bool = False


SECTION_RECORD_DEFAULTS: dict[str, Any] = {
    "status": "pending",
    "started_at": None,
    "completed_at": None,
    "duration_seconds": None,
    "output_markdown_file": None,
    "output_markdown_sha256": None,
    "response_file": None,
    "response_sha256": None,
    "prompt_eval_count": None,
    "eval_count": None,
    "total_duration": None,
    "load_duration": None,
    "prompt_eval_duration": None,
    "eval_duration": None,
    "done_reason": None,
    "error_type": None,
    "error": None,
    "timeout_seconds": None,
    "effective_generation_parameters": None,
    "generation_mode": "ollama",
}


def normalize_section_record(section: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(section)
    for key, default in SECTION_RECORD_DEFAULTS.items():
        normalized.setdefault(key, default)
    return normalized


class RunLogger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")

    def log(self, message: str) -> None:
        line = f"[{datetime.now(UTC).replace(microsecond=0).isoformat()}] {message}\n"
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line)
        print(message)


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def benchmark_root() -> Path:
    return repo_root() / "benchmarks" / "manuals" / "docforge"


def verify_script_path() -> Path:
    return repo_root() / "scripts" / "verify_docforge_manual_reference.sh"


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(content)
        temp_name = handle.name
    Path(temp_name).replace(path)


def atomic_write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def relative_posix(path: Path, start: Path) -> str:
    return path.relative_to(start).as_posix()


def model_slug(model: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", model.strip())
    slug = slug.strip("-._")
    return slug or "model"


def _is_timeout_exception(error: BaseException | None) -> bool:
    if error is None:
        return False
    if isinstance(error, (TimeoutError, socket.timeout)):
        return True
    cause = getattr(error, "reason", None)
    return isinstance(cause, (TimeoutError, socket.timeout))


def parse_checksum_file(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        checksum, relpath = stripped.split(None, 1)
        entries[relpath.strip()] = checksum
    return entries


def extract_h2_titles(markdown: str) -> list[str]:
    titles: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            titles.append(re.sub(r"\s+#+\s*$", "", line[3:]).strip())
    return titles


def count_words(markdown: str) -> int:
    return len(re.findall(r"\S+", markdown))


def extract_first_h1_title(markdown: str) -> str | None:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or None
    return None


def normalize_section_body_headings(markdown: str) -> str:
    lines = markdown.splitlines()
    normalized: list[str] = []
    in_fence = False
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            normalized.append(line)
            continue
        if in_fence:
            normalized.append(line)
            continue
        match = re.match(r"^(?P<indent>\s*)(?P<hashes>#{1,6})(?P<rest>\s+.*)$", line)
        if not match:
            normalized.append(line)
            continue
        hashes = match.group("hashes")
        target_level = max(3, len(hashes))
        normalized.append(f"{match.group('indent')}{'#' * target_level}{match.group('rest')}")
    return "\n".join(normalized) + ("\n" if markdown.endswith("\n") or markdown == "" else "")


def unwrap_single_markdown_fence(markdown: str) -> str:
    match = re.fullmatch(r"\s*```(?:markdown)?[ \t]*\n(?P<body>.*)\n```\s*", markdown, re.S)
    if not match:
        return markdown
    body = match.group("body")
    if body and not body.endswith("\n"):
        body += "\n"
    return body


def parse_command_coverage(text: str) -> dict[str, Any]:
    detected = None
    referenced = None
    command_path_present = None
    executable_invocation_present = None
    total = None
    missing: list[str] = []
    command_path_only: list[str] = []
    missing_invocations: list[str] = []
    for line in text.splitlines():
        if line.startswith("Commandes détectées :"):
            detected = int(line.split(":", 1)[1].strip())
        elif line.startswith("Commandes référencées :"):
            payload = line.split(":", 1)[1].strip()
            matched = re.fullmatch(r"(\d+)/(\d+)", payload)
            if matched:
                referenced = int(matched.group(1))
                total = int(matched.group(2))
        elif line.startswith("Couverture command_path :"):
            payload = line.split(":", 1)[1].strip()
            matched = re.fullmatch(r"(\d+)/(\d+)", payload)
            if matched:
                command_path_present = int(matched.group(1))
                total = int(matched.group(2))
        elif line.startswith("Couverture invocation exécutable :"):
            payload = line.split(":", 1)[1].strip()
            matched = re.fullmatch(r"(\d+)/(\d+)", payload)
            if matched:
                executable_invocation_present = int(matched.group(1))
                total = int(matched.group(2))
        elif line.startswith("Commandes absentes :") or line.startswith("Commandes totalement absentes :"):
            payload = line.split(":", 1)[1].strip()
            missing = [item.strip() for item in payload.split(",") if item.strip() and item.strip() != 'aucune']
        elif line.startswith("Commandes présentes seulement par command_path :"):
            payload = line.split(":", 1)[1].strip()
            command_path_only = [item.strip() for item in payload.split(",") if item.strip() and item.strip() != 'aucune']
        elif line.startswith("Invocations complètes manquantes :"):
            payload = line.split(":", 1)[1].strip()
            missing_invocations = [item.strip() for item in payload.split(",") if item.strip() and item.strip() != 'aucune']
    if command_path_present is None and referenced is not None:
        command_path_present = referenced
    if executable_invocation_present is None and referenced is not None:
        executable_invocation_present = referenced
    command_path_percent = None if not total else round((command_path_present or 0) * 100 / total, 2)
    executable_percent = None if not total else round((executable_invocation_present or 0) * 100 / total, 2)
    return {
        "detected": detected,
        "referenced": referenced if referenced is not None else command_path_present,
        "total": total,
        "missing": missing,
        "coverage_percent": command_path_percent,
        "command_path_present": command_path_present,
        "command_path_coverage_percent": command_path_percent,
        "executable_invocation_present": executable_invocation_present,
        "executable_invocation_coverage_percent": executable_percent,
        "totally_absent": missing,
        "command_path_only": command_path_only,
        "missing_invocations": missing_invocations,
    }


def expected_reference_checksum_paths(reference_root: Path, manifest: dict[str, Any]) -> set[str]:
    paths = {
        "docforge-guide-usager.md",
        "manual-knowledge.json",
        "manual-manifest.json",
        "manual-prompt.md",
        "manual-prompt-prepared.md",
    }
    for relpath in manifest.get("section_prompts", []):
        if isinstance(relpath, str) and relpath:
            paths.add(relpath)
    for item in manifest.get("section_contexts", []):
        if not isinstance(item, dict):
            continue
        if item.get("context_file"):
            paths.add(item["context_file"])
        if item.get("deterministic_file"):
            paths.add(item["deterministic_file"])
    metadata_path = reference_root / "reference-metadata.json"
    if metadata_path.is_file():
        paths.add("reference-metadata.json")
    return paths


def verify_reference_checksums(reference_root: Path) -> dict[str, str]:
    checksums_path = reference_root / "checksums.sha256"
    manifest_path = reference_root / "manual-manifest.json"
    if not checksums_path.is_file():
        raise ReferenceError(f"Fichier de sommes absent : {checksums_path}")
    if not manifest_path.is_file():
        raise ReferenceError(f"Manifeste de référence absent : {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = parse_checksum_file(checksums_path)
    required_paths = expected_reference_checksum_paths(reference_root, manifest)
    missing = sorted(required_paths - entries.keys())
    if missing:
        raise ReferenceError(
            "checksums.sha256 ne couvre pas tous les intrants figés requis : " + ", ".join(missing)
        )
    verified: dict[str, str] = {}
    for relpath, expected in entries.items():
        candidate = reference_root / relpath
        if not candidate.is_file():
            raise ReferenceError(f"Fichier référencé introuvable : {relpath}")
        actual = sha256_file(candidate)
        if actual != expected:
            raise ReferenceError(
                f"Empreinte SHA-256 invalide pour {relpath} : attendu {expected}, obtenu {actual}"
            )
        verified[relpath] = actual
    return verified


def load_reference_bundle(reference_version: str, *, benchmark_dir: Path | None = None) -> ReferenceBundle:
    bench_root = benchmark_dir or benchmark_root()
    reference_root = bench_root / reference_version
    if not reference_root.is_dir():
        raise ReferenceError(f"Référence introuvable : {reference_root}")
    checksums = verify_reference_checksums(reference_root)
    manifest = json.loads((reference_root / "manual-manifest.json").read_text(encoding="utf-8"))
    metadata_path = reference_root / "reference-metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.is_file() else {}
    section_contexts = manifest.get("section_contexts")
    section_prompts = manifest.get("section_prompts")
    if not isinstance(section_contexts, list) or not isinstance(section_prompts, list) or not section_contexts:
        raise ReferenceError("Le manifeste de référence ne décrit pas de sections exploitables.")
    if section_prompts != sorted(section_prompts):
        raise ReferenceError("Les prompts de section de la référence ne sont pas dans l’ordre lexical.")
    sections: list[ReferenceSection] = []
    for index, section in enumerate(section_contexts, start=1):
        if not isinstance(section, dict):
            raise ReferenceError("Entrée de contexte de section invalide dans le manifeste.")
        prompt_file = section.get("prompt_file")
        context_file = section.get("context_file")
        identifier = section.get("identifier")
        title = section.get("title")
        if not all(isinstance(value, str) and value for value in (prompt_file, context_file, identifier, title)):
            raise ReferenceError("Une section de référence est incomplète dans le manifeste.")
        prompt_path = reference_root / prompt_file
        context_path = reference_root / context_file
        if not prompt_path.is_file() or not context_path.is_file():
            raise ReferenceError(
                f"Section de référence incomplète : prompt={prompt_file!r}, contexte={context_file!r}"
            )
        sections.append(
            ReferenceSection(
                index=index,
                identifier=identifier,
                title=title,
                prompt_file=prompt_file,
                context_file=context_file,
                estimated_tokens=section.get("estimated_tokens"),
                context_budget=section.get("context_budget"),
                prompt_sha256=checksums[prompt_file],
                context_sha256=checksums[context_file],
                deterministic_file=section.get("deterministic_file"),
            )
        )
    return ReferenceBundle(
        version=reference_version,
        root=reference_root,
        knowledge_file="manual-knowledge.json",
        manifest_file="manual-manifest.json",
        prompt_file=manifest.get("full_prompt") or "manual-prompt.md",
        prompt_prepared_file="manual-prompt-prepared.md",
        guide_file="docforge-guide-usager.md",
        sections=sections,
        manifest=manifest,
        metadata=metadata,
        checksums=checksums,
    )


class OllamaClient:
    def __init__(self, *, base_url: str, timeout_seconds: int, urlopen_impl=None) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.urlopen_impl = urlopen_impl or urllib_request.urlopen

    def _request_json(self, path: str, *, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        url = self.base_url + path
        body = None
        headers: dict[str, str] = {}
        method = "GET"
        if payload is not None:
            method = "POST"
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib_request.Request(url, data=body, headers=headers, method=method)
        try:
            with self.urlopen_impl(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="replace")
            raise OllamaError(f"HTTP {exc.code} sur {path}: {body_text.strip() or exc.reason}") from exc
        except TimeoutError as exc:
            raise OllamaTimeoutError(timeout_seconds=self.timeout_seconds) from exc
        except socket.timeout as exc:
            raise OllamaTimeoutError(timeout_seconds=self.timeout_seconds) from exc
        except urllib_error.URLError as exc:
            if _is_timeout_exception(exc):
                raise OllamaTimeoutError(timeout_seconds=self.timeout_seconds) from exc
            raise OllamaError(f"Ollama inaccessible sur {self.base_url}: {exc.reason}") from exc
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise OllamaError(f"Réponse JSON invalide renvoyée par {path}.") from exc
        if not isinstance(data, dict):
            raise OllamaError(f"Réponse JSON inattendue renvoyée par {path}.")
        return data

    def version(self) -> str | None:
        try:
            payload = self._request_json("/api/version")
        except OllamaError:
            return None
        value = payload.get("version")
        return value if isinstance(value, str) else None

    def model_digest(self, model: str) -> str | None:
        try:
            payload = self._request_json("/api/tags")
        except OllamaError:
            return None
        models = payload.get("models")
        if not isinstance(models, list):
            return None
        for item in models:
            if isinstance(item, dict) and item.get("name") == model:
                digest = item.get("digest")
                return digest if isinstance(digest, str) else None
        return None

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        num_ctx: int,
        temperature: float,
        seed: int | None,
        max_output_tokens: int,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": num_ctx,
                "temperature": temperature,
                "num_predict": max_output_tokens,
            },
        }
        if seed is not None:
            payload["options"]["seed"] = seed
        self.last_think_requested = True
        self.last_think_compatibility_fallback = False
        response = self._generate_with_optional_think(payload, include_think=True)
        text = response.get("response")
        if not isinstance(text, str):
            raise OllamaError("Réponse Ollama sans champ 'response' textuel.")
        if not text.strip():
            raise OllamaError("Réponse Ollama vide.")
        return response

    def _generate_with_optional_think(self, payload: dict[str, Any], *, include_think: bool) -> dict[str, Any]:
        request_payload = dict(payload)
        if include_think:
            request_payload["think"] = False
        request = urllib_request.Request(
            self.base_url + "/api/generate",
            data=json.dumps(request_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self.urlopen_impl(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="replace")
            lowered = body_text.lower()
            if include_think and exc.code in {400, 404, 422} and "think" in lowered and ("unknown" in lowered or "invalid" in lowered):
                self.last_think_compatibility_fallback = True
                return self._generate_with_optional_think(payload, include_think=False)
            if exc.code == 404 and "not found" in lowered and str(payload.get("model")) in body_text:
                raise OllamaError(f"Modèle Ollama absent : {payload.get('model')}") from exc
            if "context" in lowered and ("window" in lowered or "length" in lowered):
                raise OllamaError(f"Limite de contexte Ollama atteinte : {body_text.strip()}") from exc
            raise OllamaError(f"HTTP {exc.code} sur /api/generate: {body_text.strip() or exc.reason}") from exc
        except TimeoutError as exc:
            raise OllamaTimeoutError(timeout_seconds=self.timeout_seconds) from exc
        except socket.timeout as exc:
            raise OllamaTimeoutError(timeout_seconds=self.timeout_seconds) from exc
        except urllib_error.URLError as exc:
            if _is_timeout_exception(exc):
                raise OllamaTimeoutError(timeout_seconds=self.timeout_seconds) from exc
            raise OllamaError(f"Ollama inaccessible sur {self.base_url}: {exc.reason}") from exc
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise OllamaError("Réponse JSON invalide renvoyée par /api/generate.") from exc
        if not isinstance(data, dict):
            raise OllamaError("Réponse JSON inattendue renvoyée par /api/generate.")
        return data


class ManualBenchmarkRunner:
    def __init__(
        self,
        *,
        repo_dir: Path | None = None,
        benchmark_dir: Path | None = None,
        verify_script: Path | None = None,
        urlopen_impl=None,
        process_runner=None,
    ) -> None:
        self.repo_dir = repo_dir or repo_root()
        self.benchmark_dir = benchmark_dir or benchmark_root()
        self.verify_script = verify_script or verify_script_path()
        self.urlopen_impl = urlopen_impl or urllib_request.urlopen
        self.process_runner = process_runner or subprocess.run

    def run(self, config: BenchmarkConfig) -> int:
        reference = load_reference_bundle(config.reference_version, benchmark_dir=self.benchmark_dir)
        run_dir = self.benchmark_dir / "runs" / reference.version / model_slug(config.model) / config.run_id
        manifest_path = run_dir / "run-manifest.json"
        if config.resume and not manifest_path.is_file():
            alternate_manifest_path = self._find_alternate_resume_manifest(reference, config)
            if alternate_manifest_path is not None:
                manifest_path = alternate_manifest_path
                run_dir = manifest_path.parent
        if run_dir.exists() and not config.resume and not config.reassemble:
            raise BenchmarkError(f"Le répertoire d’essai existe déjà : {run_dir}")
        run_dir.mkdir(parents=True, exist_ok=True)
        logger = RunLogger(run_dir / "run.log")
        logger.log(f"Référence chargée : {reference.version}")
        logger.log(f"Sections détectées : {len(reference.sections)}")
        logger.log("Empreintes de la référence vérifiées.")
        manifest = self._load_or_initialize_manifest(manifest_path, reference, config)
        if config.reassemble:
            try:
                return self._reassemble_existing_run(reference, run_dir, manifest_path, manifest, config, logger)
            except BenchmarkError as exc:
                logger.log(f"Échec du benchmark : {exc}")
                manifest["completed_at"] = utc_now()
                manifest["final_state"] = "failed"
                manifest["failure_message"] = str(exc)
                self._write_manifest(manifest_path, manifest)
                self._finalize_diagnostics(run_dir, manifest)
                return 1
        manifest["final_state"] = "running"
        manifest["failure_message"] = None
        if not config.resume:
            manifest["generation_parameters"] = self._generation_parameters_dict(config)
        self._write_manifest(manifest_path, manifest)

        if config.dry_run:
            logger.log("Mode dry-run : aucune requête Ollama ne sera envoyée.")
            manifest["completed_at"] = utc_now()
            manifest["final_state"] = "dry-run"
            self._write_manifest(manifest_path, manifest)
            self._finalize_diagnostics(run_dir, manifest)
            return 0

        client = OllamaClient(
            base_url=config.ollama_url,
            timeout_seconds=config.timeout_seconds,
            urlopen_impl=self.urlopen_impl,
        )
        manifest["ollama_version"] = client.version()
        manifest["model_digest"] = client.model_digest(config.model)
        self._write_manifest(manifest_path, manifest)

        sections_dir = run_dir / "sections"
        sections_dir.mkdir(parents=True, exist_ok=True)
        start_index = 0
        if config.resume:
            start_index = self._prepare_resume_state(manifest, reference, run_dir, config, logger)
            self._write_manifest(manifest_path, manifest)

        try:
            for offset, section in enumerate(reference.sections):
                state = manifest["sections"][offset]
                if offset < start_index and state.get("status") == "completed":
                    logger.log(f"Section déjà terminée, reprise sans régénération : {section.prompt_file}")
                    continue
                if self._is_fully_deterministic(section):
                    section_file = sections_dir / f"{section.stem}.md"
                    atomic_write_text(section_file, "")
                    state.update({
                        "status": "completed",
                        "started_at": utc_now(),
                        "completed_at": utc_now(),
                        "duration_seconds": 0.0,
                        "output_markdown_file": relative_posix(section_file, run_dir),
                        "output_markdown_sha256": sha256_file(section_file),
                        "response_file": None,
                        "response_sha256": None,
                        "prompt_eval_count": None,
                        "eval_count": None,
                        "total_duration": None,
                        "load_duration": None,
                        "prompt_eval_duration": None,
                        "eval_duration": None,
                        "done_reason": "deterministic",
                        "error_type": None,
                        "error": None,
                        "generation_mode": "deterministic",
                        "effective_generation_parameters": None,
                    })
                    manifest["last_attempted_section"] = {"index": section.index, "identifier": section.identifier, "title": section.title}
                    self._write_manifest(manifest_path, manifest)
                    logger.log(f"Section déterministe assemblée sans Ollama : {section.title}")
                    continue
                prompt_text = (reference.root / section.prompt_file).read_text(encoding="utf-8")
                state["status"] = "running"
                state["started_at"] = utc_now()
                state["error_type"] = None
                state["error"] = None
                state["timeout_seconds"] = config.timeout_seconds
                state["generation_mode"] = "ollama"
                manifest["last_attempted_section"] = {"index": section.index, "identifier": section.identifier, "title": section.title}
                self._write_manifest(manifest_path, manifest)
                logger.log(f"Génération de la section {section.index:02d} : {section.title}")
                wall_start = time.perf_counter()
                try:
                    response = client.generate(
                        model=config.model,
                        prompt=prompt_text,
                        num_ctx=config.num_ctx,
                        temperature=config.temperature,
                        seed=config.seed,
                        max_output_tokens=config.max_output_tokens,
                    )
                except OllamaTimeoutError as exc:
                    duration_seconds = round(time.perf_counter() - wall_start, 6)
                    message = self._build_timeout_message(section=section, timeout_seconds=config.timeout_seconds)
                    state.update(
                        {
                            "status": "failed",
                            "completed_at": utc_now(),
                            "duration_seconds": duration_seconds,
                            "response_file": None,
                            "response_sha256": None,
                            "output_markdown_file": None,
                            "output_markdown_sha256": None,
                            "prompt_eval_count": None,
                            "eval_count": None,
                            "total_duration": None,
                            "load_duration": None,
                            "prompt_eval_duration": None,
                            "eval_duration": None,
                            "done_reason": None,
                            "error_type": "timeout",
                            "error": message,
                            "timeout_seconds": config.timeout_seconds,
                            "effective_generation_parameters": self._generation_parameters_dict(config),
                        }
                    )
                    self._write_manifest(manifest_path, manifest)
                    raise BenchmarkError(message) from exc
                except OllamaError as exc:
                    duration_seconds = round(time.perf_counter() - wall_start, 6)
                    message = self._build_network_error_message(section=section, detail=str(exc))
                    state.update(
                        {
                            "status": "failed",
                            "completed_at": utc_now(),
                            "duration_seconds": duration_seconds,
                            "response_file": None,
                            "response_sha256": None,
                            "output_markdown_file": None,
                            "output_markdown_sha256": None,
                            "prompt_eval_count": None,
                            "eval_count": None,
                            "total_duration": None,
                            "load_duration": None,
                            "prompt_eval_duration": None,
                            "eval_duration": None,
                            "done_reason": None,
                            "error_type": "network",
                            "error": message,
                            "timeout_seconds": config.timeout_seconds,
                            "effective_generation_parameters": self._generation_parameters_dict(config),
                        }
                    )
                    self._write_manifest(manifest_path, manifest)
                    raise BenchmarkError(message) from exc
                duration_seconds = round(time.perf_counter() - wall_start, 6)
                section_file = sections_dir / f"{section.stem}.md"
                response_file = sections_dir / f"{section.stem}.response.json"
                atomic_write_json(response_file, response)
                state.update(
                    {
                        "completed_at": utc_now(),
                        "duration_seconds": duration_seconds,
                        "response_file": relative_posix(response_file, run_dir),
                        "response_sha256": sha256_file(response_file),
                        "prompt_eval_count": response.get("prompt_eval_count"),
                        "eval_count": response.get("eval_count"),
                        "total_duration": response.get("total_duration"),
                        "load_duration": response.get("load_duration"),
                        "prompt_eval_duration": response.get("prompt_eval_duration"),
                        "eval_duration": response.get("eval_duration"),
                        "done_reason": response.get("done_reason"),
                        "error_type": None,
                        "timeout_seconds": config.timeout_seconds,
                        "effective_generation_parameters": self._generation_parameters_dict(config),
                    }
                )
                try:
                    response_text = self._validate_generation_response(
                        response=response,
                        section=section,
                        config=config,
                    )
                except BenchmarkError as exc:
                    state.update(
                        {
                            "status": "failed",
                            "output_markdown_file": None,
                            "output_markdown_sha256": None,
                            "error_type": "generation",
                            "error": str(exc),
                        }
                    )
                    self._write_manifest(manifest_path, manifest)
                    raise
                atomic_write_text(section_file, response_text)
                state.update(
                    {
                        "status": "completed",
                        "output_markdown_file": relative_posix(section_file, run_dir),
                        "output_markdown_sha256": sha256_file(section_file),
                        "error": None,
                    }
                )
                self._write_manifest(manifest_path, manifest)

            guide_path = run_dir / "guide-genere.md"
            guide_text = self._assemble_guide(reference, run_dir)
            atomic_write_text(guide_path, guide_text)
            manifest["guide_file"] = relative_posix(guide_path, run_dir)
            manifest["guide_sha256"] = sha256_file(guide_path)
            self._write_manifest(manifest_path, manifest)

            validation = self._run_validation(reference, run_dir, guide_path, logger)
            comparison = self._build_comparison(reference, guide_path, validation)
            atomic_write_json(run_dir / "comparison.json", comparison)
            atomic_write_text(run_dir / "benchmark-summary.md", self._build_summary_markdown(comparison))
            manifest["completed_at"] = utc_now()
            manifest["final_state"] = "completed" if comparison["validation_passed"] else "validation_failed"
            self._write_manifest(manifest_path, manifest)
            self._finalize_diagnostics(run_dir, manifest)
            return 0 if comparison["validation_passed"] else 1
        except BenchmarkError as exc:
            logger.log(f"Échec du benchmark : {exc}")
            manifest["completed_at"] = utc_now()
            manifest["final_state"] = "failed"
            manifest["failure_message"] = str(exc)
            self._write_manifest(manifest_path, manifest)
            self._finalize_diagnostics(run_dir, manifest)
            return 1

    @staticmethod
    def _is_fully_deterministic(section: ReferenceSection) -> bool:
        return section.identifier in ManualDeterministicContentBuilder.FULLY_DETERMINISTIC_SECTIONS and bool(section.deterministic_file)

    def _find_alternate_resume_manifest(self, reference: ReferenceBundle, config: BenchmarkConfig) -> Path | None:
        runs_root = self.benchmark_dir / "runs" / reference.version
        if not runs_root.is_dir():
            return None
        matches = sorted(runs_root.glob(f"*/{config.run_id}/run-manifest.json"))
        if not matches:
            return None
        expected = runs_root / model_slug(config.model) / config.run_id / "run-manifest.json"
        if expected in matches:
            return expected
        if len(matches) == 1:
            return matches[0]
        raise ResumeMismatchError(
            "Plusieurs essais portant le même run-id existent sous des modèles différents; reprenez avec le modèle initial."
        )

    def _load_or_initialize_manifest(
        self,
        manifest_path: Path,
        reference: ReferenceBundle,
        config: BenchmarkConfig,
    ) -> dict[str, Any]:
        if manifest_path.is_file():
            manifest = self._normalize_manifest(json.loads(manifest_path.read_text(encoding="utf-8")))
            if not config.resume and not config.reassemble:
                raise BenchmarkError(f"Un manifeste existe déjà pour cet essai : {manifest_path}")
            self._validate_resume_immutables(manifest, reference, config)
            if not config.reassemble:
                self._validate_resume_parameters(manifest, config)
            return manifest
        return self._normalize_manifest({
            "schema_version": SCHEMA_VERSION,
            "validation_schema_version": VALIDATION_SCHEMA_VERSION,
            "reference_version": reference.version,
            "reference_dir": relative_posix(reference.root, self.repo_dir),
            "reference_guide_file": reference.guide_file,
            "reference_prompt_file": reference.prompt_file,
            "historical_reference_notes": reference.metadata.get("historical_notes", []),
            "model": config.model,
            "model_slug": model_slug(config.model),
            "model_digest": None,
            "ollama_url": config.ollama_url,
            "ollama_version": None,
            "started_at": utc_now(),
            "completed_at": None,
            "signature": self._signature(reference, config),
            "initial_generation_parameters": self._generation_parameters_dict(config),
            "generation_parameters": {
                "num_ctx": config.num_ctx,
                "temperature": config.temperature,
                "seed": config.seed,
                "max_output_tokens": config.max_output_tokens,
                "timeout_seconds": config.timeout_seconds,
            },
            "effective_generation_parameters": {
                "mode": "pending",
                "distinct_parameter_sets": [],
            },
            "reference_checksums": {
                "checksums_file": "checksums.sha256",
                "verified_files": sorted(reference.checksums),
            },
            "guide_file": None,
            "guide_sha256": None,
            "validation_dir": "validation",
            "final_state": "pending",
            "last_attempted_section": None,
            "sections": [
                {
                    "index": section.index,
                    "identifier": section.identifier,
                    "title": section.title,
                    "prompt_file": section.prompt_file,
                    "context_file": section.context_file,
                    "prompt_sha256": section.prompt_sha256,
                    "context_sha256": section.context_sha256,
                    "estimated_tokens": section.estimated_tokens,
                    "context_budget": section.context_budget,
                    "status": "pending",
                    "started_at": None,
                    "completed_at": None,
                    "duration_seconds": None,
                    "output_markdown_file": None,
                    "output_markdown_sha256": None,
                    "response_file": None,
                    "response_sha256": None,
                    "prompt_eval_count": None,
                    "eval_count": None,
                    "total_duration": None,
                    "load_duration": None,
                    "prompt_eval_duration": None,
                    "eval_duration": None,
                    "done_reason": None,
                    "error_type": None,
                    "error": None,
                    "timeout_seconds": None,
                    "effective_generation_parameters": None,
                    "generation_mode": "deterministic" if self._is_fully_deterministic(section) else "ollama",
                }
                for section in reference.sections
            ],
        })

    def _normalize_manifest(self, manifest: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(manifest)
        sections = normalized.get("sections")
        if isinstance(sections, list):
            normalized["sections"] = [
                normalize_section_record(section)
                for section in sections
                if isinstance(section, dict)
            ]
        normalized.setdefault("last_attempted_section", None)
        normalized.setdefault("validation_schema_version", 1)
        normalized.setdefault("validation_history", [])
        return normalized

    def _signature(self, reference: ReferenceBundle, config: BenchmarkConfig) -> dict[str, Any]:
        return {
            "reference_version": reference.version,
            "model": config.model,
            "temperature": self._normalize_temperature(config.temperature),
            "seed": config.seed,
            "timeout_seconds": config.timeout_seconds,
            "ollama_url": config.ollama_url,
            "prompt_hashes": [section.prompt_sha256 for section in reference.sections],
        }

    def _normalize_temperature(self, value: Any) -> float | None:
        if value is None:
            return None
        return float(value)

    def _immutable_resume_parameters(self, manifest: dict[str, Any]) -> dict[str, Any]:
        generation = manifest.get("generation_parameters") if isinstance(manifest.get("generation_parameters"), dict) else {}
        return {
            "reference_version": manifest.get("reference_version"),
            "model": manifest.get("model"),
            "temperature": self._normalize_temperature(generation.get("temperature")),
            "seed": generation.get("seed"),
            "prompt_hashes": [section.get("prompt_sha256") for section in manifest.get("sections", []) if isinstance(section, dict)],
        }

    def _validate_resume_immutables(
        self,
        manifest: dict[str, Any],
        reference: ReferenceBundle,
        config: BenchmarkConfig,
    ) -> None:
        previous = self._immutable_resume_parameters(manifest)
        current = {
            "reference_version": reference.version,
            "model": config.model,
            "temperature": self._normalize_temperature(config.temperature),
            "seed": config.seed,
            "prompt_hashes": [section.prompt_sha256 for section in reference.sections],
        }
        mismatches: list[str] = []
        for key in ("reference_version", "model", "temperature", "seed"):
            if previous.get(key) != current.get(key):
                mismatches.append(f"{key}: manifeste={previous.get(key)!r}, reprise={current.get(key)!r}")
        if previous.get("prompt_hashes") != current.get("prompt_hashes"):
            mismatches.append("prompt_hashes: la référence figée ne correspond plus aux sections enregistrées")
        if mismatches:
            raise ResumeMismatchError(
                "Les paramètres immuables diffèrent de l’essai existant : " + "; ".join(mismatches)
            )

    def _generation_parameters_dict(self, config: BenchmarkConfig) -> dict[str, Any]:
        return {
            "num_ctx": config.num_ctx,
            "temperature": self._normalize_temperature(config.temperature),
            "seed": config.seed,
            "max_output_tokens": config.max_output_tokens,
            "timeout_seconds": config.timeout_seconds,
        }

    def _validate_resume_parameters(self, manifest: dict[str, Any], config: BenchmarkConfig) -> None:
        previous = manifest.get("generation_parameters")
        if not isinstance(previous, dict):
            raise ResumeMismatchError("Le manifeste existant ne contient pas de paramètres de génération exploitables.")
        seen = self._max_seen_resource_limits(manifest)
        changes: dict[str, str] = {}
        for key, new_value in (("num_ctx", config.num_ctx), ("max_output_tokens", config.max_output_tokens)):
            old_value = previous.get(key)
            baseline = seen[key] if seen[key] else old_value
            if old_value == new_value and baseline == new_value:
                continue
            if baseline is not None and new_value < baseline:
                changes[key] = f"decrease:{baseline}->{new_value}"
                continue
            if old_value is not None and new_value < old_value:
                changes[key] = f"decrease:{old_value}->{new_value}"
                continue
            if baseline is not None and new_value > baseline:
                changes[key] = f"increase:{baseline}->{new_value}"
                continue
            if old_value is not None and new_value > old_value:
                changes[key] = f"increase:{old_value}->{new_value}"
        decreases = {key: value for key, value in changes.items() if value.startswith("decrease:")}
        increases = {key: value for key, value in changes.items() if value.startswith("increase:")}
        if decreases:
            raise ResumeMismatchError(
                "Une reprise ne peut pas réduire les limites déjà utilisées : "
                + ", ".join(f"{key} ({value.split(':', 1)[1]})" for key, value in decreases.items())
            )
        if increases and not config.allow_resource_increase:
            raise ResumeMismatchError(
                "Les limites de ressources augmentent pour la reprise et exigent --allow-resource-increase : "
                + ", ".join(f"{key} ({value.split(':', 1)[1]})" for key, value in increases.items())
            )

    def _max_seen_resource_limits(self, manifest: dict[str, Any]) -> dict[str, int]:
        num_ctx_values: list[int] = []
        max_output_values: list[int] = []
        top_level = manifest.get("generation_parameters")
        if isinstance(top_level, dict):
            if isinstance(top_level.get("num_ctx"), int):
                num_ctx_values.append(top_level["num_ctx"])
            if isinstance(top_level.get("max_output_tokens"), int):
                max_output_values.append(top_level["max_output_tokens"])
        manifest = self._normalize_manifest(manifest)
        for state in manifest.get("sections", []):
            if not isinstance(state, dict):
                continue
            effective = state.get("effective_generation_parameters")
            if not isinstance(effective, dict):
                continue
            if isinstance(effective.get("num_ctx"), int):
                num_ctx_values.append(effective["num_ctx"])
            if isinstance(effective.get("max_output_tokens"), int):
                max_output_values.append(effective["max_output_tokens"])
        return {
            "num_ctx": max(num_ctx_values) if num_ctx_values else 0,
            "max_output_tokens": max(max_output_values) if max_output_values else 0,
        }

    def _prepare_resume_state(
        self,
        manifest: dict[str, Any],
        reference: ReferenceBundle,
        run_dir: Path,
        config: BenchmarkConfig,
        logger: RunLogger,
    ) -> int:
        for state in manifest.get("sections", []):
            if not isinstance(state, dict):
                continue
            if state.get("status") == "running":
                state["status"] = "pending"
                state["completed_at"] = None
                state["duration_seconds"] = None
                state["output_markdown_file"] = None
                state["output_markdown_sha256"] = None
                state["error"] = "Reprise après interruption ou échec géré; section remise en attente."
        start_index = self._resume_index(manifest, reference, run_dir, logger)
        history = manifest.setdefault("resume_history", [])
        if isinstance(history, list):
            previous_generation = manifest.get("generation_parameters") if isinstance(manifest.get("generation_parameters"), dict) else {}
            history.append(
                {
                    "resumed_at": utc_now(),
                    "from_section_index": start_index + 1 if start_index < len(reference.sections) else None,
                    "from_generation_parameters": dict(previous_generation),
                    "to_generation_parameters": self._generation_parameters_dict(config),
                }
            )
        manifest["generation_parameters"] = self._generation_parameters_dict(config)
        return start_index

    def _resume_index(self, manifest: dict[str, Any], reference: ReferenceBundle, run_dir: Path, logger: RunLogger) -> int:
        for index, (state, section) in enumerate(zip(manifest["sections"], reference.sections, strict=True)):
            if state.get("prompt_sha256") != section.prompt_sha256:
                raise ResumeMismatchError(f"Le prompt de section a changé : {section.prompt_file}")
            if state.get("status") != "completed":
                logger.log(f"Reprise à partir de la section {section.index:02d} : {section.title}")
                return index
            output_file = state.get("output_markdown_file")
            response_file = state.get("response_file")
            if not output_file or (state.get("generation_mode") != "deterministic" and not response_file):
                logger.log(f"Section marquée terminée mais artefacts manquants : {section.prompt_file}")
                return index
            output_exists = (run_dir / output_file).is_file() if output_file else False
            response_exists = (run_dir / response_file).is_file() if response_file else False
            if not output_exists or (state.get("generation_mode") != "deterministic" and not response_exists):
                logger.log(f"Section marquée terminée mais fichiers absents : {section.prompt_file}")
                return index
        return len(reference.sections)

    def _build_timeout_message(self, *, section: ReferenceSection, timeout_seconds: int) -> str:
        suggested_timeout = max(3600, timeout_seconds)
        return (
            f"Ollama n’a pas répondu avant le délai de {timeout_seconds} secondes pour la section "
            f"{section.index:02d} — {section.title}. Reprenez l’essai avec --timeout-seconds {suggested_timeout}."
        )

    def _build_network_error_message(self, *, section: ReferenceSection, detail: str) -> str:
        return f"Erreur réseau Ollama pendant la section {section.index:02d} — {section.title}: {detail}"

    def _validate_generation_response(
        self,
        *,
        response: dict[str, Any],
        section: ReferenceSection,
        config: BenchmarkConfig,
    ) -> str:
        text = response.get("response")
        if not isinstance(text, str):
            raise BenchmarkError("Réponse Ollama sans champ 'response' textuel.")
        done_reason = response.get("done_reason")
        if done_reason in {"length", "max_tokens", "context_length"}:
            raise BenchmarkError(
                self._build_length_limit_message(
                    section=section,
                    response=response,
                    num_ctx=config.num_ctx,
                    max_output_tokens=config.max_output_tokens,
                )
            )
        if not text.strip():
            raise BenchmarkError("Réponse Ollama vide.")
        return text

    def _build_length_limit_message(
        self,
        *,
        section: ReferenceSection,
        response: dict[str, Any],
        num_ctx: int,
        max_output_tokens: int,
    ) -> str:
        prompt_eval_count = response.get("prompt_eval_count")
        eval_count = response.get("eval_count")
        reasons: list[str] = []
        if isinstance(eval_count, int) and eval_count >= max_output_tokens:
            reasons.append(
                f"limite de sortie atteinte (eval_count={eval_count}, max_output_tokens={max_output_tokens})"
            )
        if isinstance(prompt_eval_count, int):
            projected_total = prompt_eval_count + max_output_tokens
            if prompt_eval_count >= num_ctx or projected_total > num_ctx:
                reasons.append(
                    "fenêtre de contexte probablement pleine "
                    f"(prompt_eval_count={prompt_eval_count}, num_ctx={num_ctx}, prompt_eval_count+max_output_tokens={projected_total})"
                )
        if not reasons:
            reasons.append(
                "limite Ollama atteinte sans diagnostic certain "
                f"(prompt_eval_count={prompt_eval_count}, eval_count={eval_count}, num_ctx={num_ctx}, max_output_tokens={max_output_tokens})"
            )
        estimated = f", estimation_docforge={section.estimated_tokens}" if section.estimated_tokens is not None else ""
        return (
            f"Génération arrêtée par Ollama pour la section {section.index:02d} "
            f"({section.identifier}) avec done_reason={response.get('done_reason')}{estimated}: "
            + "; ".join(reasons)
            + "."
        )

    def _assemble_guide(self, reference: ReferenceBundle, run_dir: Path) -> str:
        reference_text = (reference.root / reference.guide_file).read_text(encoding="utf-8")
        canonical_h1 = extract_first_h1_title(reference_text)
        if not canonical_h1:
            raise BenchmarkError(f"Titre H1 canonique introuvable dans {reference.guide_file}")
        assembled: list[str] = [f"# {canonical_h1}"]
        for section in reference.sections:
            path = run_dir / "sections" / f"{section.stem}.md"
            if not path.is_file():
                raise BenchmarkError(f"Section générée absente : {path}")
            raw = path.read_text(encoding="utf-8")
            body = unwrap_single_markdown_fence(raw).strip()
            body = normalize_section_body_headings(body).strip() if body else ""
            deterministic = ""
            if section.deterministic_file:
                deterministic_path = reference.root / section.deterministic_file
                if not deterministic_path.is_file():
                    raise BenchmarkError(f"Fragment déterministe absent : {deterministic_path}")
                deterministic = deterministic_path.read_text(encoding="utf-8").strip()
            assembled.append(f"## {section.title}")
            if deterministic:
                assembled.append(deterministic)
            if body:
                assembled.append(body)
        return "\n\n".join(assembled).rstrip() + "\n"

    def _snapshot_previous_validation(self, manifest: dict[str, Any], run_dir: Path) -> None:
        history = manifest.setdefault("validation_history", [])
        if not isinstance(history, list):
            return
        validation_dir = run_dir / "validation"
        comparison_path = run_dir / "comparison.json"
        summary_path = run_dir / "benchmark-summary.md"
        entry = {
            "captured_at": utc_now(),
            "final_state": manifest.get("final_state"),
            "validation_schema_version": manifest.get("validation_schema_version"),
            "guide_sha256": manifest.get("guide_sha256"),
            "comparison": None,
            "manual_validate_json": None,
            "command_fidelity_json": None,
            "benchmark_summary_sha256": sha256_file(summary_path) if summary_path.is_file() else None,
        }
        if comparison_path.is_file():
            entry["comparison"] = json.loads(comparison_path.read_text(encoding="utf-8"))
        validate_json_path = validation_dir / "manual-validate.json"
        if validate_json_path.is_file():
            entry["manual_validate_json"] = json.loads(validate_json_path.read_text(encoding="utf-8"))
        command_fidelity_path = validation_dir / "command-fidelity.json"
        if command_fidelity_path.is_file():
            entry["command_fidelity_json"] = json.loads(command_fidelity_path.read_text(encoding="utf-8"))
        if entry["comparison"] is not None or entry["manual_validate_json"] is not None or entry["command_fidelity_json"] is not None or entry["benchmark_summary_sha256"] is not None:
            history.append(entry)

    def _reassemble_existing_run(
        self,
        reference: ReferenceBundle,
        run_dir: Path,
        manifest_path: Path,
        manifest: dict[str, Any],
        config: BenchmarkConfig,
        logger: RunLogger,
    ) -> int:
        if any(section.get("status") != "completed" for section in manifest.get("sections", [])):
            missing = [section.get("title") for section in manifest.get("sections", []) if section.get("status") != "completed"]
            raise BenchmarkError("Réassemblage impossible : sections incomplètes ou absentes : " + ", ".join(str(item) for item in missing))
        self._snapshot_previous_validation(manifest, run_dir)
        guide_path = run_dir / "guide-genere.md"
        guide_text = self._assemble_guide(reference, run_dir)
        atomic_write_text(guide_path, guide_text)
        manifest["guide_file"] = relative_posix(guide_path, run_dir)
        manifest["guide_sha256"] = sha256_file(guide_path)
        manifest["validation_schema_version"] = VALIDATION_SCHEMA_VERSION
        manifest["completed_at"] = utc_now()
        manifest["final_state"] = "reassembling"
        self._write_manifest(manifest_path, manifest)
        validation = self._run_validation(reference, run_dir, guide_path, logger)
        comparison = self._build_comparison(reference, guide_path, validation)
        atomic_write_json(run_dir / "comparison.json", comparison)
        atomic_write_text(run_dir / "benchmark-summary.md", self._build_summary_markdown(comparison))
        manifest["completed_at"] = utc_now()
        manifest["final_state"] = "completed" if comparison["validation_passed"] else "validation_failed"
        manifest["failure_message"] = None if comparison["validation_passed"] else "Validation automatique échouée après réassemblage."
        self._write_manifest(manifest_path, manifest)
        self._finalize_diagnostics(run_dir, manifest)
        return 0 if comparison["validation_passed"] else 1

    def _run_validation(self, reference: ReferenceBundle, run_dir: Path, guide_path: Path, logger: RunLogger) -> dict[str, Any]:
        validation_dir = run_dir / "validation"
        validation_dir.mkdir(parents=True, exist_ok=True)
        prompt_path = reference.root / reference.prompt_file
        command = [
            str(self.verify_script),
            "--reference-dir",
            str(reference.root),
            "--fast",
            "--results-dir",
            str(validation_dir),
            str(guide_path),
            str(prompt_path),
        ]
        logger.log("Validation du guide généré contre la référence figée.")
        completed = self.process_runner(command, cwd=self.repo_dir, capture_output=True, text=True)
        atomic_write_text(validation_dir / "verify.stdout.txt", completed.stdout)
        atomic_write_text(validation_dir / "verify.stderr.txt", completed.stderr)
        payload: dict[str, Any] = {
            "exit_code": completed.returncode,
            "stdout_file": "validation/verify.stdout.txt",
            "stderr_file": "validation/verify.stderr.txt",
            "manual_validate_json": None,
            "command_fidelity_json": None,
            "command_coverage": {
                "detected": None,
                "referenced": None,
                "total": None,
                "missing": [],
                "coverage_percent": None,
                "command_path_present": None,
                "command_path_coverage_percent": None,
                "executable_invocation_present": None,
                "executable_invocation_coverage_percent": None,
                "totally_absent": [],
                "command_path_only": [],
                "missing_invocations": [],
            },
        }
        validate_json_path = validation_dir / "manual-validate.json"
        if validate_json_path.is_file():
            payload["manual_validate_json"] = json.loads(validate_json_path.read_text(encoding="utf-8"))
        coverage_path = validation_dir / "command-coverage.txt"
        if coverage_path.is_file():
            payload["command_coverage"] = parse_command_coverage(coverage_path.read_text(encoding="utf-8"))
        else:
            payload["command_coverage"] = parse_command_coverage(completed.stdout)
        fidelity_path = validation_dir / "command-fidelity.json"
        if fidelity_path.is_file():
            payload["command_fidelity_json"] = json.loads(fidelity_path.read_text(encoding="utf-8"))
        return payload

    def _build_comparison(self, reference: ReferenceBundle, guide_path: Path, validation: dict[str, Any]) -> dict[str, Any]:
        generated = guide_path.read_text(encoding="utf-8")
        reference_text = (reference.root / reference.guide_file).read_text(encoding="utf-8")
        expected_titles = [section.title for section in reference.sections]
        present_titles = extract_h2_titles(generated)
        missing_titles = [title for title in expected_titles if title not in present_titles]
        additional_titles = [title for title in present_titles if title not in expected_titles]
        validation_json = validation.get("manual_validate_json") if isinstance(validation.get("manual_validate_json"), dict) else {}
        errors = validation_json.get("errors", [])
        warnings = validation_json.get("warnings", [])
        coverage = validation.get("command_coverage") or {}
        fidelity = validation.get("command_fidelity_json") if isinstance(validation.get("command_fidelity_json"), dict) else {}
        validation_passed = bool(validation_json.get("valid")) and validation.get("exit_code") == 0
        factual_guardrail_passed = (
            validation_passed
            and not missing_titles
            and not coverage.get("totally_absent")
            and not fidelity.get("strict_error_count")
        )
        return {
            "validation_passed": validation_passed,
            "validator_exit_code": validation.get("exit_code"),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
            "commands_detected": coverage.get("detected"),
            "commands_referenced": coverage.get("referenced"),
            "command_total": coverage.get("total"),
            "command_coverage_percent": coverage.get("coverage_percent"),
            "missing_commands": coverage.get("missing") or [],
            "command_path_coverage": {
                "present": coverage.get("command_path_present"),
                "total": coverage.get("total"),
                "percent": coverage.get("command_path_coverage_percent"),
            },
            "executable_invocation_coverage": {
                "present": coverage.get("executable_invocation_present"),
                "total": coverage.get("total"),
                "percent": coverage.get("executable_invocation_coverage_percent"),
            },
            "totally_absent_commands": coverage.get("totally_absent") or [],
            "command_path_only_commands": coverage.get("command_path_only") or [],
            "missing_full_invocations": coverage.get("missing_invocations") or [],
            "command_fidelity": fidelity,
            "expected_titles": expected_titles,
            "present_titles": present_titles,
            "missing_titles": missing_titles,
            "additional_titles": additional_titles,
            "generated_line_count": len(generated.splitlines()),
            "reference_line_count": len(reference_text.splitlines()),
            "generated_word_count": count_words(generated),
            "reference_word_count": count_words(reference_text),
            "generated_bytes": len(generated.encode("utf-8")),
            "reference_bytes": len(reference_text.encode("utf-8")),
            "line_count_delta": len(generated.splitlines()) - len(reference_text.splitlines()),
            "word_count_delta": count_words(generated) - count_words(reference_text),
            "byte_delta": len(generated.encode("utf-8")) - len(reference_text.encode("utf-8")),
            "structure_summary": {
                "missing_titles": missing_titles,
                "additional_titles": additional_titles,
                "manual_validator_errors": len(errors),
                "manual_validator_warnings": len(warnings),
            },
            "factual_guardrail": {
                "passed": factual_guardrail_passed,
                "notes": [
                    "Le garde-fou repose sur le validateur Markdown existant, la couverture distincte des commandes et la fidélité CLI calculée à partir du guide assemblé.",
                    "Il ne mesure pas la qualité rédactionnelle ni l’utilité pédagogique.",
                ],
            },
        }

    def _build_summary_markdown(self, comparison: dict[str, Any]) -> str:
        fidelity = comparison.get("command_fidelity") or {}
        return "\n".join(
            [
                "# Résumé du benchmark",
                "",
                f"- Validation automatique : {'réussie' if comparison['validation_passed'] else 'échouée'}.",
                f"- Erreurs : {comparison['error_count']}.",
                f"- Avertissements : {comparison['warning_count']}.",
                "",
                "## Structure du manuel",
                f"- Titres manquants : {', '.join(comparison['missing_titles']) or 'aucun'}.",
                f"- Titres supplémentaires : {', '.join(comparison['additional_titles']) or 'aucun'}.",
                f"- Diagnostics du validateur Markdown : {comparison['error_count']} erreur(s), {comparison['warning_count']} avertissement(s).",
                "",
                "## Couverture des commandes",
                (
                    f"- Couverture `command_path` : {comparison['command_path_coverage']['present']}/{comparison['command_path_coverage']['total']} "
                    f"({comparison['command_path_coverage']['percent']}%)."
                ),
                (
                    f"- Couverture d’invocation exécutable : {comparison['executable_invocation_coverage']['present']}/{comparison['executable_invocation_coverage']['total']} "
                    f"({comparison['executable_invocation_coverage']['percent']}%)."
                ),
                f"- Commandes totalement absentes : {', '.join(comparison['totally_absent_commands']) or 'aucune'}.",
                f"- Commandes présentes seulement par `command_path` : {', '.join(comparison['command_path_only_commands']) or 'aucune'}.",
                f"- Invocations complètes manquantes : {', '.join(comparison['missing_full_invocations']) or 'aucune'}.",
                "",
                "## Fidélité des commandes et options",
                f"- Erreurs strictes : {fidelity.get('strict_error_count', 0)}.",
                f"- Avertissements de fidélité : {fidelity.get('warning_count', 0)}.",
                f"- Options inconnues ou inventées : {', '.join(fidelity.get('unknown_options', [])) or 'aucune'}.",
                "",
                "La qualité rédactionnelle, la clarté et l’utilité du manuel doivent encore être évaluées manuellement par comparaison avec le guide ChatGPT de référence.",
                "",
            ]
        )

    def _finalize_diagnostics(self, run_dir: Path, manifest: dict[str, Any]) -> None:
        try:
            self._write_timing(run_dir, manifest)
        except Exception:
            pass
        try:
            self._write_run_checksums(run_dir)
        except Exception:
            pass

    def _write_manifest(self, path: Path, payload: dict[str, Any]) -> None:
        payload = self._normalize_manifest(payload)
        self._refresh_effective_generation_summary(payload)
        atomic_write_json(path, payload)

    def _refresh_effective_generation_summary(self, manifest: dict[str, Any]) -> None:
        parameter_sets: list[dict[str, Any]] = []
        for state in manifest.get("sections", []):
            if not isinstance(state, dict):
                continue
            effective = state.get("effective_generation_parameters")
            if isinstance(effective, dict):
                parameter_sets.append(effective)
        distinct = sorted(
            {json.dumps(item, sort_keys=True, ensure_ascii=False) for item in parameter_sets}
        )
        manifest["effective_generation_parameters"] = {
            "mode": "pending" if not distinct else ("uniform" if len(distinct) == 1 else "mixed"),
            "distinct_parameter_sets": [json.loads(item) for item in distinct],
            "attempted_sections": len(parameter_sets),
        }

    def _write_timing(self, run_dir: Path, manifest: dict[str, Any]) -> None:
        manifest = self._normalize_manifest(manifest)
        sections = [
            {
                "identifier": section.get("identifier"),
                "title": section.get("title"),
                "duration_seconds": section.get("duration_seconds"),
                "prompt_eval_count": section.get("prompt_eval_count"),
                "eval_count": section.get("eval_count"),
                "total_duration": section.get("total_duration"),
                "load_duration": section.get("load_duration"),
                "prompt_eval_duration": section.get("prompt_eval_duration"),
                "eval_duration": section.get("eval_duration"),
                "done_reason": section.get("done_reason"),
                "timeout_seconds": section.get("timeout_seconds"),
            }
            for section in manifest["sections"]
        ]
        total_wall = sum(item["duration_seconds"] or 0 for item in sections)
        atomic_write_json(
            run_dir / "timing.json",
            {
                "started_at": manifest.get("started_at"),
                "completed_at": manifest.get("completed_at"),
                "wall_clock_seconds": round(total_wall, 6),
                "sections": sections,
            },
        )

    def _write_run_checksums(self, run_dir: Path) -> None:
        checksum_path = run_dir / "checksums.sha256"
        entries: list[str] = []
        for path in sorted(run_dir.rglob("*")):
            if not path.is_file() or path == checksum_path:
                continue
            entries.append(f"{sha256_file(path)}  {relative_posix(path, run_dir)}")
        atomic_write_text(checksum_path, "\n".join(entries) + ("\n" if entries else ""))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Exécuter un benchmark reproductible du manuel DocForge section par section contre une référence figée.",
    )
    parser.add_argument("--model", required=True, help="Nom exact du modèle Ollama, par exemple qwen3.5:4b.")
    parser.add_argument("--reference-version", required=True, help="Version de référence figée, par exemple v0.9.")
    parser.add_argument("--run-id", required=True, help="Identifiant stable de l’essai.")
    parser.add_argument("--num-ctx", required=True, type=int, help="Taille du contexte Ollama pour chaque section.")
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Température de génération Ollama (défaut : 0.0).",
    )
    parser.add_argument("--seed", type=int, default=None, help="Graine de génération Ollama.")
    parser.add_argument("--resume", action="store_true", help="Reprendre un essai interrompu si les paramètres structurants sont identiques.")
    parser.add_argument(
        "--allow-resource-increase",
        action="store_true",
        help="Autoriser avec --resume uniquement une augmentation de num_ctx ou max_output_tokens pour les sections échouées ou non commencées.",
    )
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL, help=f"URL de base d’Ollama (défaut : {DEFAULT_OLLAMA_URL}).")
    parser.add_argument("--max-output-tokens", type=int, default=DEFAULT_MAX_OUTPUT_TOKENS, help=f"Limite de génération par section (défaut : {DEFAULT_MAX_OUTPUT_TOKENS}).")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS, help=f"Délai maximal pour chaque requête HTTP (défaut : {DEFAULT_TIMEOUT_SECONDS}).")
    parser.add_argument("--dry-run", action="store_true", help="Vérifier la référence et préparer l’essai sans appeler Ollama.")
    parser.add_argument("--reassemble", action="store_true", help="Réassembler et revalider un essai existant sans rappeler Ollama.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = BenchmarkConfig(
        model=args.model,
        reference_version=args.reference_version,
        run_id=args.run_id,
        num_ctx=args.num_ctx,
        temperature=args.temperature,
        seed=args.seed,
        resume=args.resume,
        ollama_url=args.ollama_url,
        max_output_tokens=args.max_output_tokens,
        timeout_seconds=args.timeout_seconds,
        dry_run=args.dry_run,
        allow_resource_increase=args.allow_resource_increase,
        reassemble=args.reassemble,
    )
    runner = ManualBenchmarkRunner()
    try:
        return runner.run(config)
    except BenchmarkError as exc:
        print(f"ERREUR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
