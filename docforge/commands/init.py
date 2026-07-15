from __future__ import annotations

from pathlib import Path

from docforge.storage_paths import ensure_project_storage_migrated

from docforge.detectors import TechnologyDetector
from docforge.models import Project
from docforge.project_config import write_project_config
from docforge.scanners import FileSystemScanner


def initialize_project(
    path: Path,
    *,
    force: bool = False,
) -> tuple[Project, Path]:
    ensure_project_storage_migrated(path)
    project = FileSystemScanner().scan(path)
    TechnologyDetector().detect(project)

    config_path = write_project_config(
        project,
        force=force,
    )

    return project, config_path
