from __future__ import annotations

import shutil
from pathlib import Path


USER_CONFIG_DIRNAME = "docforge"
LEGACY_USER_CONFIG_DIRNAME = "project-assistant"
PROJECT_STATE_DIRNAME = ".docforge"
LEGACY_PROJECT_STATE_DIRNAME = ".project-assistant"
PROJECT_CONFIG_FILENAME = ".docforge.yml"
LEGACY_PROJECT_CONFIG_FILENAME = ".project-assistant.yml"


def user_config_root() -> Path:
    return (
        Path.home()
        / ".config"
        / USER_CONFIG_DIRNAME
    )


def legacy_user_config_root() -> Path:
    return (
        Path.home()
        / ".config"
        / LEGACY_USER_CONFIG_DIRNAME
    )


def registry_path() -> Path:
    return user_config_root() / "projects.yml"


def legacy_registry_path() -> Path:
    return legacy_user_config_root() / "projects.yml"


def invariant_manifest_path() -> Path:
    return user_config_root() / "invariant-baseline.json"


def legacy_invariant_manifest_path() -> Path:
    return (
        legacy_user_config_root()
        / "invariant-baseline.json"
    )


def project_state_root(root: Path) -> Path:
    return root / PROJECT_STATE_DIRNAME


def legacy_project_state_root(root: Path) -> Path:
    return root / LEGACY_PROJECT_STATE_DIRNAME


def project_config_path(root: Path) -> Path:
    return root / PROJECT_CONFIG_FILENAME


def legacy_project_config_path(root: Path) -> Path:
    return root / LEGACY_PROJECT_CONFIG_FILENAME


def migrate_legacy_path(
    legacy_path: Path,
    current_path: Path,
) -> bool:
    legacy_path = legacy_path.expanduser()
    current_path = current_path.expanduser()

    if current_path.exists() or not legacy_path.exists():
        return False

    current_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    shutil.move(
        str(legacy_path),
        str(current_path),
    )
    return True


def ensure_user_storage_migrated() -> None:
    migrate_legacy_path(
        legacy_user_config_root(),
        user_config_root(),
    )


def ensure_project_storage_migrated(root: Path) -> None:
    resolved_root = root.expanduser().resolve()

    migrate_legacy_path(
        legacy_project_state_root(resolved_root),
        project_state_root(resolved_root),
    )
    migrate_legacy_path(
        legacy_project_config_path(resolved_root),
        project_config_path(resolved_root),
    )
