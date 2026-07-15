from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


PREVIEW_DIRECTORY = Path(".project-assistant/preview")
BACKUP_DIRECTORY = Path(".project-assistant/backups")


@dataclass(slots=True)
class AppliedDocument:
    document_path: str
    source: Path
    destination: Path
    backup: Path | None


def _git_is_clean(root: Path) -> bool:
    result = subprocess.run(
        [
            "git",
            "status",
            "--porcelain",
            "--",
            ".",
            ":(exclude).project-assistant",
            ":(exclude).project-assistant/**",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"{root} n'est pas un dépôt Git accessible."
        )

    return not result.stdout.strip()


def apply_preview_documents(
    root: Path,
    document_paths: list[str],
    *,
    require_clean_git: bool = True,
    owner_approved: bool = False,
) -> list[AppliedDocument]:
    root = root.expanduser().resolve()

    protected_documents = {
        "INVARIANTS.md",
    }

    requested_protected = sorted(
        protected_documents.intersection(document_paths)
    )

    if requested_protected and not owner_approved:
        raise PermissionError(
            "Document protégé : "
            + ", ".join(requested_protected)
            + ". Une autorisation explicite du propriétaire "
            "est requise pour l'appliquer."
        )

    if require_clean_git and not _git_is_clean(root):
        raise RuntimeError(
            "Le dépôt Git contient des modifications. "
            "Committez ou remisez-les avant d'appliquer l'aperçu."
        )

    preview_root = root / PREVIEW_DIRECTORY
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = root / BACKUP_DIRECTORY / timestamp

    applied: list[AppliedDocument] = []

    for document_path in document_paths:
        source = preview_root / document_path
        destination = root / document_path

        if not source.is_file():
            raise FileNotFoundError(
                f"Aperçu introuvable : {source}"
            )

        backup: Path | None = None

        if destination.exists():
            backup = backup_root / document_path
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, backup)

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

        applied.append(
            AppliedDocument(
                document_path=document_path,
                source=source,
                destination=destination,
                backup=backup,
            )
        )

    return applied
