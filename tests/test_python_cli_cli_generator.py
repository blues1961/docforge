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
        '''
from pathlib import Path
import typer

app = typer.Typer()


@app.command()
def profile(
    path: Path = typer.Argument(
        ...,
        help="Projet à inspecter.",
    ),
) -> None:
    """Détecter le profil d’un projet."""
    pass
''',
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
demo-cli = "project_assistant.cli:app"
""",
        encoding="utf-8",
    )


def test_python_cli_cli_document_is_generated(
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
        "docs/cli.md",
    )

    assert (
        result.generator_name
        == "cli-python-cli-déterministe"
    )
    assert "# Référence CLI" in result.content
    assert "### `profile`" in result.content
    assert "Détecter le profil d’un projet." in result.content
    assert "Projet à inspecter." in result.content
    assert "demo-cli" in result.content
    assert "/home/" not in result.content


def test_project_knowledge_contains_cli_facts(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    assert knowledge.cli.framework == "Typer"
    assert knowledge.cli.command_count == 1
    assert knowledge.cli.commands[0].name == "profile"
