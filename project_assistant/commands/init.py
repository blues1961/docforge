from __future__ import annotations

from pathlib import Path

from project_assistant.detectors import TechnologyDetector
from project_assistant.models import Project
from project_assistant.project_config import write_project_config
from project_assistant.scanners import FileSystemScanner


def initialize_project(
    path: Path,
    *,
    force: bool = False,
) -> tuple[Project, Path]:
    project = FileSystemScanner().scan(path)
    TechnologyDetector().detect(project)

    config_path = write_project_config(
        project,
        force=force,
    )

    return project, config_path
