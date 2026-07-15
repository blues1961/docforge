from __future__ import annotations

from dataclasses import dataclass

from project_assistant.analyzers.python_cli_specification import (
    PythonCliSpecificationAnalyzer,
)
from project_assistant.generators import (
    PythonCliSecurityDocumentGenerator,
    PythonCliConfigurationDocumentGenerator,
    PythonCliCliDocumentGenerator,
    PythonCliSpecificationDocumentGenerator,
    AgentsDocumentGenerator,
    ApiDocumentGenerator,
    ArchitectureDocumentGenerator,
    CodexStartDocumentGenerator,
    DeploymentDocumentGenerator,
    InvariantsDocumentGenerator,
    PythonCliAgentsDocumentGenerator,
    PythonCliArchitectureDocumentGenerator,
    PythonCliCodexStartDocumentGenerator,
    PythonCliInvariantsDocumentGenerator,
    PythonCliReadmeDocumentGenerator,
    PythonCliReadmeDevDocumentGenerator,
    ReadmeDocumentGenerator,
    ReadmeDevDocumentGenerator,
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
            "AGENTS.md",
            "CODEX_START.md",
            "INVARIANTS.md",
            "README.md",
            "README_DEV.md",
            "docs/api.md",
            "docs/architecture.md",
            "docs/cli.md",
            "docs/configuration.md",
            "docs/deployment.md",
            "docs/security.md",
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
        if document_path == "AGENTS.md":
            existing_path = project.root / "AGENTS.md"
            existing_content = (
                existing_path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
                if existing_path.is_file()
                else None
            )

            if self.knowledge.profile.name == "python-cli":
                content = (
                    PythonCliAgentsDocumentGenerator()
                    .generate(
                        project,
                        self.knowledge,
                        existing_content=existing_content,
                    )
                )
                generator_name = (
                    "agents-python-cli-déterministe"
                )
            else:
                content = AgentsDocumentGenerator().generate(
                    project,
                    self.knowledge,
                    existing_content=existing_content,
                )
                generator_name = "agents-déterministe"

        elif document_path == "CODEX_START.md":
            existing_path = project.root / "CODEX_START.md"
            existing_content = (
                existing_path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
                if existing_path.is_file()
                else None
            )

            if self.knowledge.profile.name == "python-cli":
                content = (
                    PythonCliCodexStartDocumentGenerator()
                    .generate(
                        project,
                        self.knowledge,
                        existing_content=existing_content,
                    )
                )
                generator_name = (
                    "codex-start-python-cli-déterministe"
                )
            else:
                content = CodexStartDocumentGenerator().generate(
                    project,
                    self.knowledge,
                    existing_content=existing_content,
                )
                generator_name = "codex-start-déterministe"

        elif document_path == "INVARIANTS.md":
            existing_path = project.root / "INVARIANTS.md"
            existing_content = (
                existing_path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
                if existing_path.is_file()
                else None
            )

            if self.knowledge.profile.name == "python-cli":
                content = (
                    PythonCliInvariantsDocumentGenerator()
                    .generate(
                        project,
                        self.knowledge,
                        existing_content=existing_content,
                    )
                )
                generator_name = (
                    "invariants-python-cli-déterministe-protégé"
                )
            else:
                content = InvariantsDocumentGenerator().generate(
                    project,
                    self.knowledge,
                    existing_content=existing_content,
                )
                generator_name = (
                    "invariants-déterministe-protégé"
                )

        elif document_path == "README.md":
            if self.knowledge.profile.name == "python-cli":
                content = (
                    PythonCliReadmeDocumentGenerator()
                    .generate(
                        project,
                        self.knowledge,
                    )
                )
                generator_name = (
                    "readme-python-cli-déterministe"
                )
            else:
                content = ReadmeDocumentGenerator().generate(
                    project,
                    self.knowledge.readme,
                )
                generator_name = "readme-déterministe"

        elif document_path == "README_DEV.md":
            if self.knowledge.profile.name == "python-cli":
                content = (
                    PythonCliReadmeDevDocumentGenerator()
                    .generate(
                        project,
                        self.knowledge,
                    )
                )
                generator_name = (
                    "readme-dev-python-cli-déterministe"
                )
            else:
                content = ReadmeDevDocumentGenerator().generate(
                    project,
                    self.knowledge,
                )
                generator_name = "readme-dev-déterministe"

        elif document_path == "docs/api.md":
            content = ApiDocumentGenerator().generate(
                project,
                self.knowledge.api,
            )
            generator_name = "api-déterministe"

        elif document_path == "docs/architecture.md":
            if self.knowledge.profile.name == "python-cli":
                content = (
                    PythonCliArchitectureDocumentGenerator()
                    .generate(
                        project,
                        self.knowledge,
                    )
                )
                generator_name = (
                    "architecture-python-cli-déterministe"
                )
            else:
                content = ArchitectureDocumentGenerator().generate(
                    project,
                    self.knowledge.architecture,
                )
                generator_name = "architecture-déterministe"

        elif document_path == "docs/cli.md":
            if self.knowledge.profile.name != "python-cli":
                raise UnsupportedDeterministicDocumentError(
                    "docs/cli.md est réservé au profil python-cli."
                )

            content = (
                PythonCliCliDocumentGenerator()
                .generate(
                    project,
                    self.knowledge,
                )
            )
            generator_name = "cli-python-cli-déterministe"

        elif document_path == "docs/configuration.md":
            if self.knowledge.profile.name != "python-cli":
                raise UnsupportedDeterministicDocumentError(
                    "docs/configuration.md est réservé au profil "
                    "python-cli."
                )

            content = (
                PythonCliConfigurationDocumentGenerator()
                .generate(
                    project,
                    self.knowledge,
                )
            )
            generator_name = (
                "configuration-python-cli-déterministe"
            )

        elif document_path == "docs/deployment.md":
            content = DeploymentDocumentGenerator().generate(
                project,
                self.knowledge.deployment,
            )
            generator_name = "deployment-déterministe"

        elif document_path == "docs/security.md":
            if self.knowledge.profile.name != "python-cli":
                raise UnsupportedDeterministicDocumentError(
                    "docs/security.md est réservé au profil "
                    "python-cli."
                )

            content = (
                PythonCliSecurityDocumentGenerator()
                .generate(
                    project,
                    self.knowledge,
                )
            )
            generator_name = (
                "security-python-cli-déterministe"
            )

        elif document_path == "docs/specification.md":
            if self.knowledge.profile.name == "python-cli":
                facts = (
                    PythonCliSpecificationAnalyzer()
                    .analyze(self.knowledge)
                )
                content = (
                    PythonCliSpecificationDocumentGenerator()
                    .generate(
                        project,
                        facts,
                    )
                )
                generator_name = (
                    "specification-python-cli-déterministe"
                )
            else:
                content = (
                    SpecificationDocumentGenerator()
                    .generate(
                        project,
                        self.knowledge.specification,
                    )
                )
                generator_name = (
                    "specification-déterministe"
                )

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
