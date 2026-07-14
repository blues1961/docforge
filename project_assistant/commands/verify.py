from __future__ import annotations

from pathlib import Path

from project_assistant.config import DocumentationConfigLoader
from project_assistant.detectors import TechnologyDetector
from project_assistant.models import Project
from project_assistant.project_config import (
    detect_profile,
    load_project_config,
)
from project_assistant.scanners import FileSystemScanner
from project_assistant.validators import DocumentationValidator


def verify_project(
    path: Path,
    profile: str | None = None,
) -> Project:
    project = FileSystemScanner().scan(path)
    TechnologyDetector().detect(project)

    local_config = load_project_config(project.root)

    if profile is not None:
        selected_profile = profile
        add_documents: list[str] = []
        remove_documents: list[str] = []
    elif local_config is not None:
        selected_profile = local_config.profile
        add_documents = local_config.documentation_add
        remove_documents = local_config.documentation_remove
    else:
        selected_profile = detect_profile(project)
        add_documents = []
        remove_documents = []

    config = DocumentationConfigLoader().resolve_project_profile(
        profile_name=selected_profile,
        add_documents=add_documents,
        remove_documents=remove_documents,
    )

    DocumentationValidator().validate(
        project=project,
        config=config,
    )

    return project
