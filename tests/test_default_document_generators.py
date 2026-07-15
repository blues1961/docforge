from pathlib import Path

from docforge.default_document_generators import (
    build_default_document_generator_registry,
)
from docforge.knowledge import (
    ProjectKnowledgeBuilder,
)
from docforge.scanners import FileSystemScanner


def _create_python_cli(root: Path) -> None:
    package = root / "docforge"
    package.mkdir()

    (package / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )

    (package / "cli.py").write_text(
        """
import typer

app = typer.Typer()


@app.command()
def check() -> None:
    pass
""",
        encoding="utf-8",
    )

    (root / "tests").mkdir()

    (root / "pyproject.toml").write_text(
        """
[project]
name = "demo-cli"
version = "0.1.0"
requires-python = ">=3.11"

[project.scripts]
demo-cli = "docforge.cli:app"
""",
        encoding="utf-8",
    )

    (root / ".gitignore").write_text(
        """
.env.local
.env.*.local
.project-assistant/
.venv/
__pycache__/
.pytest_cache/
""",
        encoding="utf-8",
    )


def test_default_registry_contains_python_cli_documents(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    registry = (
        build_default_document_generator_registry(
            knowledge
        )
    )

    assert registry.supported_documents(
        "python-cli"
    ) == frozenset(
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


def test_default_registry_generates_cli_document(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    registry = (
        build_default_document_generator_registry(
            knowledge
        )
    )

    registration = registry.resolve(
        profile_name="python-cli",
        document_path="docs/cli.md",
    )

    content = registration.generate(project)

    assert (
        registration.generator_name
        == "cli-python-cli-déterministe"
    )
    assert "# Référence CLI" in content
    assert "### `check`" in content


def test_default_registry_generates_configuration_document(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    registry = (
        build_default_document_generator_registry(
            knowledge
        )
    )

    registration = registry.resolve(
        profile_name="python-cli",
        document_path="docs/configuration.md",
    )

    content = registration.generate(project)

    assert (
        registration.generator_name
        == "configuration-python-cli-déterministe"
    )
    assert "# Configuration" in content


def test_default_registry_generates_security_document(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    registry = (
        build_default_document_generator_registry(
            knowledge
        )
    )

    registration = registry.resolve(
        profile_name="python-cli",
        document_path="docs/security.md",
    )

    content = registration.generate(project)

    assert (
        registration.generator_name
        == "security-python-cli-déterministe"
    )
    assert "# Sécurité" in content


def test_default_registry_generates_second_python_cli_batch(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )
    registry = (
        build_default_document_generator_registry(
            knowledge
        )
    )

    expected = {
        "README.md": (
            "readme-python-cli-déterministe",
            "## Résumé du projet",
        ),
        "README_DEV.md": (
            "readme-dev-python-cli-déterministe",
            "## Prérequis",
        ),
        "docs/architecture.md": (
            "architecture-python-cli-déterministe",
            "## Architecture logique",
        ),
        "docs/specification.md": (
            "specification-python-cli-déterministe",
            "## Exigences fonctionnelles",
        ),
    }

    for document_path, (
        generator_name,
        expected_heading,
    ) in expected.items():
        registration = registry.resolve(
            profile_name="python-cli",
            document_path=document_path,
        )

        content = registration.generate(project)

        assert (
            registration.generator_name
            == generator_name
        )
        assert expected_heading in content


def test_default_registry_generates_special_python_cli_documents(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )
    registry = (
        build_default_document_generator_registry(
            knowledge
        )
    )

    expected = {
        "AGENTS.md": (
            "agents-python-cli-déterministe",
            "# ",
        ),
        "CODEX_START.md": (
            "codex-start-python-cli-déterministe",
            "# ",
        ),
        "INVARIANTS.md": (
            (
                "invariants-python-cli-"
                "déterministe-protégé"
            ),
            "# ",
        ),
    }

    for document_path, (
        generator_name,
        heading,
    ) in expected.items():
        registration = registry.resolve(
            profile_name="python-cli",
            document_path=document_path,
        )
        content = registration.generate(project)

        assert registration.generator_name == generator_name
        assert heading in content


def test_registry_special_generator_reads_existing_content(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    (tmp_path / "AGENTS.md").write_text(
        """
# Agents

<!-- project-assistant:local-agents:start -->
Contenu local conservé.
<!-- project-assistant:local-agents:end -->
""",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )
    registry = (
        build_default_document_generator_registry(
            knowledge
        )
    )

    registration = registry.resolve(
        profile_name="python-cli",
        document_path="AGENTS.md",
    )

    content = registration.generate(project)

    assert "Contenu local conservé." in content


def test_default_registry_contains_generic_documents(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )
    registry = (
        build_default_document_generator_registry(
            knowledge
        )
    )

    expected = {
        "README.md": "readme-déterministe",
        "README_DEV.md": "readme-dev-déterministe",
        "AGENTS.md": "agents-déterministe",
        "CODEX_START.md": "codex-start-déterministe",
        "INVARIANTS.md": (
            "invariants-déterministe-protégé"
        ),
        "docs/api.md": "api-déterministe",
        "docs/architecture.md": (
            "architecture-déterministe"
        ),
        "docs/deployment.md": (
            "deployment-déterministe"
        ),
        "docs/specification.md": (
            "specification-déterministe"
        ),
    }

    for document_path, generator_name in expected.items():
        registration = registry.resolve(
            profile_name="generic",
            document_path=document_path,
        )

        assert registration.profile_name == "generic"
        assert registration.document_path == document_path
        assert registration.generator_name == generator_name


def test_default_registry_uses_generic_fallback_for_other_profile(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )
    registry = (
        build_default_document_generator_registry(
            knowledge
        )
    )

    registration = registry.resolve(
        profile_name="django-react",
        document_path="docs/api.md",
    )

    assert registration.profile_name == "generic"
    assert registration.generator_name == "api-déterministe"
