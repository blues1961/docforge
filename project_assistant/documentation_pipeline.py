from __future__ import annotations

from dataclasses import dataclass

from project_assistant.generators import (
    ApiDocumentGenerator,
    ArchitectureDocumentGenerator,
    DeploymentDocumentGenerator,
    ReadmeDocumentGenerator,
    SpecificationDocumentGenerator,
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
    SUPPORTED_DOCUMENTS = frozenset(
        {
            "README.md",
            "docs/api.md",
            "docs/architecture.md",
            "docs/deployment.md",
            "docs/specification.md",
        }
    )

    def __init__(
        self,
        knowledge: ProjectKnowledge,
    ) -> None:
        self.knowledge = knowledge

    def generate(
        self,
        project: Project,
        document_path: str,
    ) -> GeneratedDocumentContent:
        if document_path == "README.md":
            content = ReadmeDocumentGenerator().generate(
                project,
                self.knowledge.readme,
            )
            generator_name = "readme-déterministe"

        elif document_path == "docs/api.md":
            content = ApiDocumentGenerator().generate(
                project,
                self.knowledge.api,
            )
            generator_name = "api-déterministe"

        elif document_path == "docs/architecture.md":
            content = ArchitectureDocumentGenerator().generate(
                project,
                self.knowledge.architecture,
            )
            generator_name = "architecture-déterministe"

        elif document_path == "docs/deployment.md":
            content = DeploymentDocumentGenerator().generate(
                project,
                self.knowledge.deployment,
            )
            generator_name = "deployment-déterministe"

        elif document_path == "docs/specification.md":
            content = SpecificationDocumentGenerator().generate(
                project,
                self.knowledge.specification,
            )
            generator_name = "specification-déterministe"

        else:
            raise UnsupportedDeterministicDocumentError(
                f"Document déterministe non pris en charge : "
                f"{document_path}"
            )

        return GeneratedDocumentContent(
            document_path=document_path,
            generator_name=generator_name,
            content=content,
        )
