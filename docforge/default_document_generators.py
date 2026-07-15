from __future__ import annotations

from docforge.analyzers import (
    PythonCliSpecificationAnalyzer,
)
from docforge.document_generator_registry import (
    DocumentGeneratorRegistry,
    RegisteredDocumentGenerator,
)
from docforge.generators import (
    AgentsDocumentGenerator,
    ApiDocumentGenerator,
    ArchitectureDocumentGenerator,
    CodexStartDocumentGenerator,
    DeploymentDocumentGenerator,
    InvariantsDocumentGenerator,
    ReadmeDevDocumentGenerator,
    ReadmeDocumentGenerator,
    SpecificationDocumentGenerator,
    PythonCliAgentsDocumentGenerator,
    PythonCliCodexStartDocumentGenerator,
    PythonCliInvariantsDocumentGenerator,
    PythonCliArchitectureDocumentGenerator,
    PythonCliCliDocumentGenerator,
    PythonCliConfigurationDocumentGenerator,
    PythonCliReadmeDocumentGenerator,
    PythonCliReadmeDevDocumentGenerator,
    PythonCliSecurityDocumentGenerator,
    PythonCliSpecificationDocumentGenerator,
)
from docforge.knowledge import ProjectKnowledge


def _existing_document_content(
    project,
    document_path: str,
) -> str | None:
    path = project.root / document_path

    if not path.is_file():
        return None

    try:
        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
    except OSError:
        return None


def build_default_document_generator_registry(
    knowledge: ProjectKnowledge,
) -> DocumentGeneratorRegistry:
    registry = DocumentGeneratorRegistry()

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="python-cli",
            document_path="docs/cli.md",
            generator_name="cli-python-cli-déterministe",
            generate=lambda project: (
                PythonCliCliDocumentGenerator().generate(
                    project,
                    knowledge,
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="python-cli",
            document_path="docs/configuration.md",
            generator_name=(
                "configuration-python-cli-déterministe"
            ),
            generate=lambda project: (
                PythonCliConfigurationDocumentGenerator()
                .generate(
                    project,
                    knowledge,
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="python-cli",
            document_path="docs/security.md",
            generator_name=(
                "security-python-cli-déterministe"
            ),
            generate=lambda project: (
                PythonCliSecurityDocumentGenerator()
                .generate(
                    project,
                    knowledge,
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="python-cli",
            document_path="README.md",
            generator_name=(
                "readme-python-cli-déterministe"
            ),
            generate=lambda project: (
                PythonCliReadmeDocumentGenerator()
                .generate(
                    project,
                    knowledge,
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="python-cli",
            document_path="README_DEV.md",
            generator_name=(
                "readme-dev-python-cli-déterministe"
            ),
            generate=lambda project: (
                PythonCliReadmeDevDocumentGenerator()
                .generate(
                    project,
                    knowledge,
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="python-cli",
            document_path="docs/architecture.md",
            generator_name=(
                "architecture-python-cli-déterministe"
            ),
            generate=lambda project: (
                PythonCliArchitectureDocumentGenerator()
                .generate(
                    project,
                    knowledge,
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="python-cli",
            document_path="docs/specification.md",
            generator_name=(
                "specification-python-cli-déterministe"
            ),
            generate=lambda project: (
                PythonCliSpecificationDocumentGenerator()
                .generate(
                    project,
                    PythonCliSpecificationAnalyzer()
                    .analyze(knowledge),
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="python-cli",
            document_path="AGENTS.md",
            generator_name=(
                "agents-python-cli-déterministe"
            ),
            generate=lambda project: (
                PythonCliAgentsDocumentGenerator()
                .generate(
                    project,
                    knowledge,
                    existing_content=(
                        _existing_document_content(
                            project,
                            "AGENTS.md",
                        )
                    ),
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="python-cli",
            document_path="CODEX_START.md",
            generator_name=(
                "codex-start-python-cli-déterministe"
            ),
            generate=lambda project: (
                PythonCliCodexStartDocumentGenerator()
                .generate(
                    project,
                    knowledge,
                    existing_content=(
                        _existing_document_content(
                            project,
                            "CODEX_START.md",
                        )
                    ),
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="python-cli",
            document_path="INVARIANTS.md",
            generator_name=(
                "invariants-python-cli-"
                "déterministe-protégé"
            ),
            generate=lambda project: (
                PythonCliInvariantsDocumentGenerator()
                .generate(
                    project,
                    knowledge,
                    existing_content=(
                        _existing_document_content(
                            project,
                            "INVARIANTS.md",
                        )
                    ),
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="generic",
            document_path="README.md",
            generator_name="readme-déterministe",
            generate=lambda project: (
                ReadmeDocumentGenerator().generate(
                    project,
                    knowledge.readme,
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="generic",
            document_path="README_DEV.md",
            generator_name="readme-dev-déterministe",
            generate=lambda project: (
                ReadmeDevDocumentGenerator().generate(
                    project,
                    knowledge,
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="generic",
            document_path="AGENTS.md",
            generator_name="agents-déterministe",
            generate=lambda project: (
                AgentsDocumentGenerator().generate(
                    project,
                    knowledge,
                    existing_content=(
                        _existing_document_content(
                            project,
                            "AGENTS.md",
                        )
                    ),
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="generic",
            document_path="CODEX_START.md",
            generator_name="codex-start-déterministe",
            generate=lambda project: (
                CodexStartDocumentGenerator().generate(
                    project,
                    knowledge,
                    existing_content=(
                        _existing_document_content(
                            project,
                            "CODEX_START.md",
                        )
                    ),
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="generic",
            document_path="INVARIANTS.md",
            generator_name=(
                "invariants-déterministe-protégé"
            ),
            generate=lambda project: (
                InvariantsDocumentGenerator().generate(
                    project,
                    knowledge,
                    existing_content=(
                        _existing_document_content(
                            project,
                            "INVARIANTS.md",
                        )
                    ),
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="generic",
            document_path="docs/api.md",
            generator_name="api-déterministe",
            generate=lambda project: (
                ApiDocumentGenerator().generate(
                    project,
                    knowledge.api,
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="generic",
            document_path="docs/architecture.md",
            generator_name="architecture-déterministe",
            generate=lambda project: (
                ArchitectureDocumentGenerator().generate(
                    project,
                    knowledge.architecture,
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="generic",
            document_path="docs/deployment.md",
            generator_name="deployment-déterministe",
            generate=lambda project: (
                DeploymentDocumentGenerator().generate(
                    project,
                    knowledge.deployment,
                )
            ),
        )
    )

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="generic",
            document_path="docs/specification.md",
            generator_name="specification-déterministe",
            generate=lambda project: (
                SpecificationDocumentGenerator().generate(
                    project,
                    knowledge.specification,
                )
            ),
        )
    )

    return registry
