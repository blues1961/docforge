from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from project_assistant.config import (
    DocumentationConfigLoader,
    ResolvedDocumentationConfig,
)
from project_assistant.detectors import TechnologyDetector
from project_assistant.default_document_generators import (
    build_default_document_generator_registry,
)
from project_assistant.documentation_pipeline import (
    DocumentationPipeline,
)
from project_assistant.knowledge import (
    ProjectKnowledgeBuilder,
)
from project_assistant.generators import (
    DocumentationPreviewGenerator,
)
from project_assistant.models import Project
from project_assistant.project_config import (
    detect_profile,
    load_project_config,
)
from project_assistant.scanners import FileSystemScanner
from project_assistant.validators import DocumentationValidator


PREVIEW_DIRECTORY = Path(".project-assistant/preview")



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

    knowledge = ProjectKnowledgeBuilder().build(
        project
    )
    pipeline = DocumentationPipeline(knowledge)

    profile_deterministic_documents = set(
        knowledge.profile.document_policy.deterministic_documents
    )

    generator_registry = (
        build_default_document_generator_registry(
            knowledge
        )
    )

    supported_deterministic_documents = (
        profile_deterministic_documents
        & generator_registry.supported_documents(
            knowledge.profile.name
        )
    )

    if refresh:
        deterministic_targets = set(
            supported_deterministic_documents
        )
    else:
        deterministic_targets = {
            document_path
            for document_path in supported_deterministic_documents
            if (
                document_path in required_documents
                and not (
                    project.root / document_path
                ).exists()
            )
        }

    for document_path in sorted(deterministic_targets):
        preview_path = preview_root / document_path
        preview_path.parent.mkdir(parents=True, exist_ok=True)

        generated_document = pipeline.generate(
            project,
            document_path,
        )
        content = generated_document.content
        generator_name = generated_document.generator_name

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
