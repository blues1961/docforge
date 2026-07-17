from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from docforge.models import Project
from docforge.profiles import ProfileDetector
from docforge.storage_paths import (
    PROJECT_CONFIG_FILENAME,
    ensure_project_storage_migrated,
)


class ProjectConfigError(RuntimeError):
    """Erreur liée à la configuration locale d'un projet."""


@dataclass(slots=True)
class ProjectConfig:
    name: str
    profile: str
    documentation_add: list[str] = field(default_factory=list)
    documentation_remove: list[str] = field(default_factory=list)
    excluded_paths: list[str] = field(default_factory=list)


def detect_profile(project: Project) -> str:
    profile_name = ProfileDetector().resolve(project).name
    return "base" if profile_name == "generic" else profile_name


def load_project_config(root: Path) -> ProjectConfig | None:
    root = root.expanduser().resolve()
    ensure_project_storage_migrated(root)
    path = root / PROJECT_CONFIG_FILENAME

    if not path.exists():
        return None

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as error:
        raise ProjectConfigError(
            f"Impossible de lire {path}: {error}"
        ) from error

    if not isinstance(data, dict):
        raise ProjectConfigError(
            f"La racine de {PROJECT_CONFIG_FILENAME} doit être un objet YAML."
        )

    project_data = data.get("project", {})
    documentation_data = data.get("documentation", {})
    scan_data = data.get("scan", {})

    if not isinstance(project_data, dict):
        raise ProjectConfigError("'project' doit être un objet.")

    if not isinstance(documentation_data, dict):
        raise ProjectConfigError("'documentation' doit être un objet.")

    if not isinstance(scan_data, dict):
        raise ProjectConfigError("'scan' doit être un objet.")

    name = str(project_data.get("name", root.name))
    profile = str(project_data.get("profile", "base"))

    return ProjectConfig(
        name=name,
        profile=profile,
        documentation_add=_string_list(
            documentation_data.get("add", [])
        ),
        documentation_remove=_string_list(
            documentation_data.get("remove", [])
        ),
        excluded_paths=_string_list(
            scan_data.get("exclude", [])
        ),
    )


def write_project_config(
    project: Project,
    *,
    force: bool = False,
) -> Path:
    ensure_project_storage_migrated(project.root)
    path = project.root / PROJECT_CONFIG_FILENAME

    if path.exists() and not force:
        raise FileExistsError(
            f"{path} existe déjà. Utilisez --force pour le remplacer."
        )

    profile = detect_profile(project)

    data: dict[str, Any] = {
        "schema_version": 1,
        "project": {
            "name": project.name,
            "profile": profile,
        },
        "documentation": {
            "add": [],
            "remove": [],
        },
        "scan": {
            "exclude": [],
        },
    }

    path.write_text(
        yaml.safe_dump(
            data,
            allow_unicode=True,
            sort_keys=False,
            width=100,
        ),
        encoding="utf-8",
    )

    return path


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []

    if not isinstance(value, list):
        raise ProjectConfigError(
            "La valeur attendue doit être une liste."
        )

    return [str(item) for item in value]
