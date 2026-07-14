from pathlib import Path

from project_assistant.documentation_pipeline import (
    DocumentationPipeline,
)
from project_assistant.knowledge import (
    ProjectKnowledgeBuilder,
)
from project_assistant.scanners import FileSystemScanner


def _create_python_cli(root: Path) -> None:
    package = root / "demo_cli"
    package.mkdir()

    (package / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )
    (package / "cli.py").write_text(
        "def main(): pass\n",
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
dependencies = [
  "typer>=0.12",
  "rich>=13",
]

[project.optional-dependencies]
dev = [
  "pytest>=8",
]

[project.scripts]
demo-cli = "demo_cli.cli:main"
""",
        encoding="utf-8",
    )


def test_python_cli_readme_uses_cli_content(
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
        "README.md",
    )

    assert (
        result.generator_name
        == "readme-python-cli-déterministe"
    )
    assert "outil Python en ligne de commande" in result.content
    assert "pyproject.toml" in result.content
    assert "demo-cli" in result.content
    assert "0.1.0" in result.content
    assert ">=3.11" in result.content
    assert "typer>=0.12" in result.content
    assert "rich>=13" in result.content
    assert "pytest>=8" in result.content
    assert "demo_cli.cli:main" in result.content
    assert "project-assistant profile" in result.content
    assert "Traefik" not in result.content
    assert ".env.dev" not in result.content


def test_python_cli_readme_dev_uses_python_workflow(
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
        "README_DEV.md",
    )

    assert (
        result.generator_name
        == "readme-dev-python-cli-déterministe"
    )
    assert "python -m venv .venv" in result.content
    assert "pytest -q" in result.content
    assert "project_assistant/profiles/" in result.content
    assert "PostgreSQL" not in result.content
    assert "make dev" not in result.content


def test_python_cli_readme_dev_has_no_absolute_home_path(
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
        "README_DEV.md",
    )

    assert "/home/" not in result.content
