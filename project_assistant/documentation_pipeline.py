from __future__ import annotations

from dataclasses import dataclass

from project_assistant.default_document_generators import (
    build_default_document_generator_registry,
)
from project_assistant.document_generator_registry import (
    UnknownDocumentGeneratorError,
)
from project_assistant.knowledge import ProjectKnowledge
from project_assistant.models import Project


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
    ) -> None:
        self.knowledge = knowledge
        self.registry = (
            build_default_document_generator_registry(
                knowledge
            )
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
