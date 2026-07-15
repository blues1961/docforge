from pathlib import Path

from project_assistant.documentation_pipeline import (
    DocumentationPipeline,
)
from project_assistant.knowledge import (
    ProjectKnowledgeBuilder,
)
from project_assistant.scanners import FileSystemScanner


def _create_python_cli(root: Path) -> None:
    package = root / "project_assistant"
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
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "demo-cli"
version = "0.1.0"
requires-python = ">=3.11"

[project.scripts]
demo-cli = "project_assistant.cli:app"
""",
        encoding="utf-8",
    )

    (root / ".gitignore").write_text(
        """
.project-assistant/
.venv/
__pycache__/
*.pyc
.pytest_cache/
""",
        encoding="utf-8",
    )


def test_python_cli_configuration_document_is_generated(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    result = DocumentationPipeline(
        knowledge
    ).generate(
        project,
        "docs/configuration.md",
    )

    assert (
        result.generator_name
        == "configuration-python-cli-déterministe"
    )

    assert "# Configuration" in result.content
    assert "## Configuration utilisateur" in result.content
    assert "## État local d’un projet" in result.content
    assert "## Exclusions Git attendues" in result.content
    assert "projects.yml" in result.content
    assert "invariant-baseline.json" in result.content
    assert ".project-assistant/cache/" in result.content
    assert ".project-assistant/preview/" in result.content
    assert "demo-cli" in result.content

    assert "Traefik" not in result.content
    assert "PostgreSQL" not in result.content
    assert "/home/" not in result.content


def test_project_knowledge_contains_configuration_facts(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    assert (
        knowledge.configuration.project_state_root
        == ".project-assistant"
    )
    assert knowledge.configuration.files
