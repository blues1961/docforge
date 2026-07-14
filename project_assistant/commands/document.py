from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from project_assistant.analyzers import (
    ApiAnalyzer,
    ArchitectureAnalyzer,
    DeploymentAnalyzer,
    ReadmeAnalyzer,
    SpecificationAnalyzer,
)
from project_assistant.config import (
    DocumentationConfigLoader,
    ResolvedDocumentationConfig,
)
from project_assistant.detectors import TechnologyDetector
from project_assistant.generators import (
    ApiDocumentGenerator,
    ArchitectureDocumentGenerator,
    DeploymentDocumentGenerator,
    DocumentationPreviewGenerator,
    ReadmeDocumentGenerator,
    SpecificationDocumentGenerator,
)
from project_assistant.models import Project
from project_assistant.project_config import (
    detect_profile,
    load_project_config,
)
from project_assistant.scanners import FileSystemScanner
from project_assistant.validators import DocumentationValidator


PREVIEW_DIRECTORY = Path(".project-assistant/preview")

DETERMINISTIC_DOCUMENTS = {
    "README.md",
    "docs/api.md",
    "docs/architecture.md",
    "docs/deployment.md",
    "docs/specification.md",
}


@dataclass(slots=True)
class PreviewDocumentResult:
    document_path: str
    preview_path: Path
    generator: str
    reason: str


def prepare_project_documentation(
    path: Path,
    *,
    profile: str | None = None,
) -> tuple[Project, ResolvedDocumentationConfig]:
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

    return project, config


def generate_documentation_preview(
    path: Path,
    *,
    profile: str | None = None,
    clean: bool = False,
    refresh: bool = False,
) -> tuple[
    Project,
    ResolvedDocumentationConfig,
    list[PreviewDocumentResult],
]:
    project, config = prepare_project_documentation(
        path=path,
        profile=profile,
    )

    preview_root = project.root / PREVIEW_DIRECTORY

    if clean and preview_root.exists():
        shutil.rmtree(preview_root)

    # Génère d’abord les squelettes des documents obligatoires absents.
    skeletons = DocumentationPreviewGenerator().generate(
        project=project,
        config=config,
        clean=False,
    )

    results: dict[str, PreviewDocumentResult] = {}

    for skeleton in skeletons:
        results[skeleton.source_path] = PreviewDocumentResult(
            document_path=skeleton.source_path,
            preview_path=skeleton.preview_path,
            generator="skeleton",
            reason=skeleton.reason,
        )

    required_documents = set(config.required_documents)

    deterministic_targets = (
        DETERMINISTIC_DOCUMENTS & required_documents
    )

    if not refresh:
        deterministic_targets = {
            document_path
            for document_path in deterministic_targets
            if not (project.root / document_path).exists()
        }

    for document_path in sorted(deterministic_targets):
        preview_path = preview_root / document_path
        preview_path.parent.mkdir(parents=True, exist_ok=True)

        if document_path == "README.md":
            facts = ReadmeAnalyzer().analyze(project)
            content = ReadmeDocumentGenerator().generate(
                project,
                facts,
            )
            generator_name = "readme-déterministe"

        elif document_path == "docs/specification.md":
            facts = SpecificationAnalyzer().analyze(project)
            content = SpecificationDocumentGenerator().generate(
                project,
                facts,
            )
            generator_name = "specification-déterministe"

        elif document_path == "docs/api.md":
            facts = ApiAnalyzer().analyze(project)
            content = ApiDocumentGenerator().generate(
                project,
                facts,
            )
            generator_name = "api-déterministe"

        elif document_path == "docs/architecture.md":
            facts = ArchitectureAnalyzer().analyze(project)
            content = ArchitectureDocumentGenerator().generate(
                project,
                facts,
            )
            generator_name = "architecture-déterministe"

        elif document_path == "docs/deployment.md":
            facts = DeploymentAnalyzer().analyze(project)
            content = DeploymentDocumentGenerator().generate(
                project,
                facts,
            )
            generator_name = "deployment-déterministe"

        else:
            continue

        preview_path.write_text(
            content,
            encoding="utf-8",
        )

        results[document_path] = PreviewDocumentResult(
            document_path=document_path,
            preview_path=preview_path,
            generator=generator_name,
            reason=(
                "actualisation demandée"
                if refresh
                else "document obligatoire absent"
            ),
        )

    return (
        project,
        config,
        [
            results[path]
            for path in sorted(results)
        ],
    )
