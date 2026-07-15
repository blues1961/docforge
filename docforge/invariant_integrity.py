from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


PROTECTED_FILES = (
    "INVARIANTS.md",
    "AGENTS.md",
    "CODEX_START.md",
)

DEFAULT_MANIFEST = (
    Path.home()
    / ".config"
    / "docforge"
    / "invariant-baseline.json"
)


@dataclass(slots=True)
class ProtectedFileState:
    path: str
    exists: bool
    sha256: str | None


@dataclass(slots=True)
class InvariantBaseline:
    schema_version: int
    template_root: str
    approved_at: str
    files: list[ProtectedFileState] = field(default_factory=list)


@dataclass(slots=True)
class InvariantDrift:
    path: str
    status: str
    expected_sha256: str | None
    actual_sha256: str | None


@dataclass(slots=True)
class InvariantIntegrityReport:
    template_root: str
    baseline_path: str
    baseline_exists: bool
    valid: bool
    drifts: list[InvariantDrift] = field(default_factory=list)


class InvariantIntegrityManager:
    def __init__(
        self,
        manifest_path: Path | None = None,
    ) -> None:
        self.manifest_path = (
            manifest_path or DEFAULT_MANIFEST
        ).expanduser()

    def approve(
        self,
        template_root: Path,
    ) -> InvariantBaseline:
        root = template_root.expanduser().resolve()

        states = [
            self._state(root, relative_path)
            for relative_path in PROTECTED_FILES
        ]

        missing = [
            state.path
            for state in states
            if not state.exists
        ]

        if missing:
            raise FileNotFoundError(
                "Fichiers protégés absents : "
                + ", ".join(missing)
            )

        baseline = InvariantBaseline(
            schema_version=1,
            template_root=str(root),
            approved_at=datetime.now(
                timezone.utc
            ).isoformat(),
            files=states,
        )

        self.manifest_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.manifest_path.write_text(
            json.dumps(
                asdict(baseline),
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        return baseline

    def verify(
        self,
        template_root: Path,
    ) -> InvariantIntegrityReport:
        root = template_root.expanduser().resolve()

        if not self.manifest_path.exists():
            return InvariantIntegrityReport(
                template_root=str(root),
                baseline_path=str(self.manifest_path),
                baseline_exists=False,
                valid=False,
                drifts=[],
            )

        data = json.loads(
            self.manifest_path.read_text(
                encoding="utf-8",
            )
        )

        baseline_root = Path(
            data["template_root"]
        ).expanduser().resolve()

        drifts: list[InvariantDrift] = []

        if baseline_root != root:
            drifts.append(
                InvariantDrift(
                    path=".",
                    status="template-root-changed",
                    expected_sha256=str(baseline_root),
                    actual_sha256=str(root),
                )
            )

        expected_states = {
            item["path"]: item
            for item in data.get("files", [])
        }

        for relative_path in PROTECTED_FILES:
            expected = expected_states.get(relative_path)
            actual = self._state(root, relative_path)

            if expected is None:
                drifts.append(
                    InvariantDrift(
                        path=relative_path,
                        status="missing-from-baseline",
                        expected_sha256=None,
                        actual_sha256=actual.sha256,
                    )
                )
                continue

            expected_exists = bool(expected["exists"])
            expected_hash = expected.get("sha256")

            if expected_exists and not actual.exists:
                status = "deleted"
            elif not expected_exists and actual.exists:
                status = "created"
            elif expected_hash != actual.sha256:
                status = "modified"
            else:
                continue

            drifts.append(
                InvariantDrift(
                    path=relative_path,
                    status=status,
                    expected_sha256=expected_hash,
                    actual_sha256=actual.sha256,
                )
            )

        return InvariantIntegrityReport(
            template_root=str(root),
            baseline_path=str(self.manifest_path),
            baseline_exists=True,
            valid=not drifts,
            drifts=drifts,
        )

    @staticmethod
    def _state(
        root: Path,
        relative_path: str,
    ) -> ProtectedFileState:
        path = root / relative_path

        if not path.is_file():
            return ProtectedFileState(
                path=relative_path,
                exists=False,
                sha256=None,
            )

        digest = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        return ProtectedFileState(
            path=relative_path,
            exists=True,
            sha256=digest,
        )
