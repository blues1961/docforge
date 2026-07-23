from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import asdict
import yaml
from pathlib import Path
from typing import Any

from docforge.manual_benchmark import OllamaClient
from docforge.manual_deterministic import ManualDeterministicContentBuilder
from docforge.manual_service import ManualPreparationService
from docforge.manual_blueprint import ManualBlueprintRegistry
from docforge.multi_manual_benchmark import normalize_section_headings
from docforge.validators import ManualMarkdownValidator, DjangoReactMultiDocumentValidator

DOCUMENT_DESTINATIONS = {
    "user-guide": "guide-utilisateur.md",
    "operator-guide": "guide-exploitation.md",
    "developer-reference": "reference-developpeur.md",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _display_name(knowledge: dict[str, Any]) -> str:
    app = knowledge.get("application", {})
    raw = app.get("display_name") or app.get("name") or knowledge.get("project", {}).get("name") or "l’application"
    raw = str(raw)
    return raw[:1].upper() + raw[1:]


def _h1(title: str, name: str) -> str:
    return f"# {title} de {name}" if title != "Guide utilisateur" else f"# Guide utilisateur de {name}"



def _manual_config(project: Path) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for path in (Path.home() / ".config" / "docforge" / "config.yml", project / ".docforge.yml"):
        if path.is_file():
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                values = data.get("manual", {}) if isinstance(data, dict) else {}
                if isinstance(values, dict):
                    merged.update(values)
            except (OSError, yaml.YAMLError):
                continue
    return merged

def build_manual(project: Path, *, output_dir: Path | None = None, model: str | None = None,
                 num_ctx: int | None = None, max_output_tokens: int | None = None,
                 document_ids: list[str] | None = None, all_documents: bool = False,
                 dry_run: bool = False) -> dict[str, Any]:
    project = project.expanduser().resolve()
    config = _manual_config(project)
    model = model or config.get("model")
    if num_ctx is None:
        num_ctx = int(config.get("num_ctx", 12288))
    if max_output_tokens is None:
        max_output_tokens = int(config.get("max_output_tokens", 2048))
    target = (output_dir.expanduser().resolve() if output_dir else project / ".docforge" / "manuals" / "build")
    result = ManualPreparationService().prepare(project, clean=True, mode="sections", output_dir=target, context_budget=num_ctx)
    manifest = json.loads(result.manifest_file.read_text(encoding="utf-8"))
    knowledge = json.loads(result.knowledge_file.read_text(encoding="utf-8"))
    available = [d["identifier"] for d in manifest.get("documents", [])]
    selected = set(available if all_documents or not document_ids else document_ids)
    required_sections = [f"{d['identifier']}/{e['identifier']}" for d in manifest.get("documents", []) if d["identifier"] in selected for e in d.get("section_contexts", []) if e.get("generation_mode") != "deterministic"]
    deterministic_count = sum(1 for d in manifest.get("documents", []) if d["identifier"] in selected for e in d.get("section_contexts", []) if e.get("generation_mode") == "deterministic")
    print(f"Projet : {project}")
    print(f"Profil : {manifest.get('profile_name', 'inconnu')}")
    print(f"Documents : {len(selected)}")
    print(f"Sections déterministes : {deterministic_count}")
    print(f"Sections nécessitant Ollama : {len(required_sections)}")
    print(f"Modèle : {model or 'aucun appel Ollama requis' if not required_sections else (model or 'non configuré')}")
    print(f"Répertoire de prévisualisation : {target}")
    if required_sections and model:
        print(f"Appels Ollama prévus : {len(required_sections)}")
    if required_sections and not model and not dry_run:
        raise ValueError("Certaines sections nécessitent un modèle Ollama :\n- " + "\n- ".join(required_sections) + "\nRelancez avec :\ndocforge manual build . --model qwen3.5:4b")
    if not selected <= set(available):
        raise ValueError("document-id inconnu : " + ", ".join(sorted(selected - set(available))))
    state: dict[str, Any] = {"schema_version": 1, "project": str(project), "project_name": knowledge.get("project", {}).get("name"), "display_name": _display_name(knowledge), "output_dir": str(target), "generation_state": "running", "final_state": "running", "documents": {}, "multidocument_validation": {"executed": False, "deferred": selected != set(available)}}
    builder = ManualDeterministicContentBuilder()
    registry = ManualBlueprintRegistry()
    try:
        for document in manifest["documents"]:
            ident = document["identifier"]
            if ident not in selected:
                continue
            doc_dir = target / "documents" / ident
            doc_dir.mkdir(parents=True, exist_ok=True)
            section_states = {}
            blueprint = registry.blueprint_for_document(manifest["profile_name"], project_kind=manifest.get("project_kind"), document_identifier=ident)
            parts = [_h1(document["title"], state["display_name"]), ""]
            for entry in document["section_contexts"]:
                sid = entry["identifier"]
                fragment = (target / entry["deterministic_file"]).read_text(encoding="utf-8") if entry.get("deterministic_file") else ""
                mode = "deterministic" if entry.get("generation_mode") == "deterministic" else ("hybrid" if entry.get("deterministic_file") else "narrative")
                content = fragment
                if mode != "deterministic":
                    if dry_run:
                        content = ""
                    else:
                        if not model:
                            raise ValueError(f"Le modèle est requis pour la section {ident}/{sid}.")
                        prompt = (target / entry["prompt_file"]).read_text(encoding="utf-8")
                        client = OllamaClient(base_url="http://localhost:11434", timeout_seconds=3600)
                        raw = client.generate(model=model, prompt=prompt, num_ctx=num_ctx, max_output_tokens=max_output_tokens, temperature=0, seed=42)
                        content = str(raw.get("response") or "")
                        if not content.strip() or raw.get("done_reason") == "length":
                            raise ValueError(f"Réponse Ollama vide ou tronquée : {ident}/{sid}")
                        if mode == "hybrid" and fragment:
                            content += "\n\n" + fragment
                if mode == "deterministic" and not content.strip():
                    raise ValueError(f"Fragment déterministe vide : {ident}/{sid}")
                if mode != "deterministic" and not dry_run:
                    validator = ManualMarkdownValidator()
                    fragment_markdown = f"# {document['title']}\n\n## {entry['title']}\n\n{content}"
                    diagnostics = [
                        *validator._validate_forbidden_vocabulary(fragment_markdown, blueprint),
                        *validator._validate_hybrid_safety(fragment_markdown, knowledge),
                    ]
                    errors = [item for item in diagnostics if item.severity == "error"]
                    report = target / "validation" / "sections" / f"{ident}-{sid}.json"
                    report.parent.mkdir(parents=True, exist_ok=True)
                    report.write_text(json.dumps([asdict(item) for item in diagnostics], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    if errors:
                        raise ValueError(f"Validation immédiate échouée pour {ident}/{sid}. Rapport JSON : {report}")
                section_path = doc_dir / "sections" / f"{sid}.md"
                section_path.parent.mkdir(parents=True, exist_ok=True)
                section_path.write_text(content, encoding="utf-8")
                parts.extend([f"## {entry['title']}", "", normalize_section_headings(content, entry["title"]), ""])
                section_states[sid] = {"generation_mode": mode, "status": "dry_run" if dry_run else "completed", "output": str(section_path.relative_to(target)), "output_sha256": _sha256(section_path)}
            if not dry_run:
                guide = doc_dir / "guide-genere.md"
                guide.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
                diagnostics = ManualMarkdownValidator().validate(markdown=guide.read_text(encoding="utf-8"), knowledge=knowledge, blueprint=blueprint)
                errors = [d for d in diagnostics if d.severity == "error"]
                warnings = [d for d in diagnostics if d.severity == "warning"]
                (target / "validation").mkdir(exist_ok=True)
                (target / "validation" / f"{ident}.json").write_text(json.dumps([d.__dict__ if hasattr(d, "__dict__") else {"code": d.code, "severity": d.severity, "message": d.message} for d in diagnostics], ensure_ascii=False, indent=2), encoding="utf-8")
                if errors:
                    raise ValueError(
                        f"Validation échouée pour {ident} : {len(errors)} erreur(s). "
                        f"Guide : {guide}. Rapport JSON : {target / 'validation' / (ident + '.json')}"
                    )
                state["documents"][ident] = {"title": document["title"], "sections": section_states, "guide": str(guide.relative_to(target)), "errors": len(errors), "warnings": len(warnings)}
        if not dry_run and selected == set(available) and manifest.get("profile_name") == "django-react":
            multi = DjangoReactMultiDocumentValidator().validate(root=target, manifest=manifest)
            state["multidocument_validation"] = {"executed": True, "deferred": False, "diagnostics": len(multi)}
            if multi:
                raise ValueError(f"Validation multidocument échouée : {len(multi)} diagnostic(s)")
        state["generation_state"] = "completed"
        state["final_state"] = "dry_run_completed" if dry_run else "completed"
    except Exception as exc:
        state["generation_state"] = "failed"
        state["final_state"] = "failed"
        state["error"] = str(exc)
        raise
    state["manifest"] = "build-manifest.json"
    (target / "build-manifest.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


def publish_manual(project: Path, *, output_dir: Path | None = None, from_run: Path | None = None,
                   write: bool = False, replace: bool = False, allow_dirty: bool = False, dry_run: bool = False) -> list[tuple[Path, Path]]:
    project = project.expanduser().resolve()
    source = (from_run.expanduser().resolve() if from_run else project / ".docforge" / "manuals" / "build")
    state_path = source / "build-manifest.json"
    run_manifest = False
    if not state_path.is_file():
        state_path = source / "run-manifest.json"
        run_manifest = state_path.is_file()
    if not state_path.is_file():
        raise ValueError("Aucun build valide trouvé : exécutez 'docforge manual build'.")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("final_state") != "completed" or state.get("generation_state") != "completed":
        raise ValueError("Le build n’est pas terminé avec succès.")
    if Path(state.get("project", "")).resolve() != project:
        raise ValueError("Le projet du build ne correspond pas au projet cible.")
    destination = (output_dir.expanduser().resolve() if output_dir else project / "docs")
    pairs = []
    for ident, filename in DOCUMENT_DESTINATIONS.items():
        documents_state = state.get("documents", {})
        item = documents_state.get(ident)
        if ident in documents_state:
            guide_path = item.get("guide")
            if not guide_path and run_manifest:
                guide_path = f"documents/{ident}/guide-genere.md"
            src = source / guide_path
            dst = destination / filename
            if not src.is_file():
                raise ValueError(f"Fichier source absent : {src}")
            pairs.append((src, dst))
    if not pairs:
        raise ValueError("Aucun document publiable dans le build.")
    if not allow_dirty:
        try:
            dirty = subprocess.run(["git", "-C", str(project), "status", "--porcelain"], capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            dirty = ""
        if dirty:
            raise ValueError("Le dépôt cible est modifié ; utilisez --allow-dirty explicitement.")
    for src, dst in pairs:
        if dst.exists() and not replace:
            raise ValueError(f"Le fichier existe déjà : {dst} (utilisez --replace).")
    if not write or dry_run:
        return pairs
    destination.mkdir(parents=True, exist_ok=True)
    temp_paths = []
    try:
        for src, dst in pairs:
            fd, name = tempfile.mkstemp(prefix=f".{dst.name}.", dir=str(destination))
            os.close(fd)
            tmp = Path(name)
            shutil.copyfile(src, tmp)
            temp_paths.append((tmp, dst))
        for tmp, dst in temp_paths:
            os.replace(tmp, dst)
    finally:
        for tmp, _ in temp_paths:
            if tmp.exists():
                tmp.unlink()
    return pairs
