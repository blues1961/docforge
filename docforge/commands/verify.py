from __future__ import annotations

from pathlib import Path

from docforge.config import DocumentationConfigLoader
from docforge.detectors import TechnologyDetector
from docforge.models import Project
from docforge.project_config import (
    detect_profile,
    load_project_config,
)
from docforge.scanners import FileSystemScanner
from docforge.validators import DocumentationValidator


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

    if selected_profile == "python-cli":
        project.findings = [
            finding
            for finding in project.findings
            if finding.code not in {"ENV002", "ENV003", "ENV004"}
        ]

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
