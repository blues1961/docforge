from pathlib import Path

from docforge.documentation_pipeline import (
    DocumentationPipeline,
)
from docforge.knowledge import (
    ProjectKnowledgeBuilder,
)
from docforge.scanners import FileSystemScanner


def _create_python_cli(root: Path) -> None:
    package = root / "demo_cli"
    package.mkdir()

    (package / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )
    (package / "cli.py").write_text(
        "def app(): pass\n",
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

[project.scripts]
demo-cli = "demo_cli.cli:app"
""",
        encoding="utf-8",
    )


def test_python_cli_codex_start_uses_cli_context(
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
        "CODEX_START.md",
    )

    assert (
        result.generator_name
        == "codex-start-python-cli-déterministe"
    )

    assert "## Mission" in result.content
    assert "## Architecture essentielle" in result.content
    assert "## Invariants absolus" in result.content
    assert "## Règles pour les nouveaux profils" in result.content
    assert "## Règles pour les générateurs" in result.content

    assert "ProjectKnowledgeBuilder" in result.content
    assert "DocumentationPipeline" in result.content
    assert "pytest -q" in result.content
    assert "demo-cli" in result.content
    assert "demo_cli.cli:app" in result.content

    assert "Traefik" not in result.content
    assert "PostgreSQL" not in result.content
    assert ".env.dev" not in result.content
    assert "make dev" not in result.content
    assert "/home/" not in result.content


def test_python_cli_codex_start_preserves_local_section(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    existing = """
# CODEX_START.md

<!-- project-assistant:local-codex:start -->

Toujours exécuter le test du profil générique.

<!-- project-assistant:local-codex:end -->
"""

    (tmp_path / "CODEX_START.md").write_text(
        existing,
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    result = DocumentationPipeline(
        knowledge
    ).generate(
        project,
        "CODEX_START.md",
    )

    assert (
        "Toujours exécuter le test du profil générique."
        in result.content
    )
    assert result.content.count(
        "project-assistant:local-codex:start"
    ) == 1
    assert result.content.count(
        "project-assistant:local-codex:end"
    ) == 1


def test_django_react_keeps_standard_codex_generator(
    tmp_path: Path,
) -> None:
    backend = tmp_path / "backend"
    backend.mkdir()

    (backend / "manage.py").write_text(
        "",
        encoding="utf-8",
    )
    (backend / "requirements.txt").write_text(
        "Django\n",
        encoding="utf-8",
    )

    frontend = tmp_path / "frontend"
    frontend.mkdir()

    (frontend / "package.json").write_text(
        """
{
  "dependencies": {"react": "^18"},
  "devDependencies": {"vite": "^5"}
}
""",
        encoding="utf-8",
    )

    for filename in (
        "docker-compose.dev.yml",
        "docker-compose.prod.yml",
    ):
        (tmp_path / filename).write_text(
            "services: {}\n",
            encoding="utf-8",
        )

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    result = DocumentationPipeline(
        knowledge
    ).generate(
        project,
        "CODEX_START.md",
    )

    assert result.generator_name == "codex-start-déterministe"
