from __future__ import annotations

from dataclasses import dataclass

from docforge.document_generator_registry import (
    DocumentGeneratorRegistry,
    UnknownDocumentGeneratorError,
)
from docforge.knowledge import ProjectKnowledge
from docforge.models import Project
from docforge.profiles import (
    ProfileDetector,
    ProjectProfile,
)


@dataclass(slots=True)
class GeneratedDocumentContent:
    document_path: str
    generator_name: str
    content: str


class UnsupportedDeterministicDocumentError(ValueError):
    """Document non pris en charge par le pipeline déterministe."""


class DocumentationPipeline:
    def __init__(
        self,
        knowledge: ProjectKnowledge,
        *,
        profile_instance: ProjectProfile | None = None,
        registry: DocumentGeneratorRegistry | None = None,
    ) -> None:
        self.knowledge = knowledge

        if registry is not None:
            self.registry = registry
            return

        profile_instance = (
            profile_instance
            or ProfileDetector().profile_named(
                knowledge.profile.name
            )
        )
        self.registry = (
            profile_instance
            .build_document_generator_registry(
                knowledge
            )
        )

    def supported_documents(
        self,
    ) -> frozenset[str]:
        return self.registry.supported_documents(
            self.knowledge.profile.name
        )

    def generate(
        self,
        project: Project,
        document_path: str,
    ) -> GeneratedDocumentContent:
        try:
            registration = self.registry.resolve(
                profile_name=self.knowledge.profile.name,
                document_path=document_path,
            )
        except UnknownDocumentGeneratorError as exc:
            raise UnsupportedDeterministicDocumentError(
                "Document déterministe non pris en charge : "
                f"{document_path}"
            ) from exc

        return GeneratedDocumentContent(
            document_path=document_path,
            generator_name=registration.generator_name,
            content=registration.generate(project),
        )
