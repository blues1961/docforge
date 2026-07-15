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

[project.optional-dependencies]
dev = [
  "pytest>=8",
]

[project.scripts]
demo-cli = "demo_cli.cli:app"
""",
        encoding="utf-8",
    )


def test_python_cli_agents_uses_cli_rules(
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
        "AGENTS.md",
    )

    assert (
        result.generator_name
        == "agents-python-cli-déterministe"
    )

    assert "## Architecture interne" in result.content
    assert "## Règles concernant les profils" in result.content
    assert "## Tests obligatoires" in result.content
    assert "ProjectKnowledge" in result.content
    assert "DocumentationPipeline.SUPPORTED_DOCUMENTS" in (
        result.content
    )
    assert "pytest -q" in result.content
    assert "demo-cli" in result.content
    assert "demo_cli.cli:app" in result.content

    assert "Traefik" not in result.content
    assert "PostgreSQL" not in result.content
    assert ".env.dev" not in result.content
    assert "make dev" not in result.content


def test_python_cli_agents_preserves_local_section(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    existing = """
# AGENTS.md

<!-- project-assistant:local-agents:start -->

Toujours tester la commande profile avant un commit.

<!-- project-assistant:local-agents:end -->
"""

    (tmp_path / "AGENTS.md").write_text(
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
        "AGENTS.md",
    )

    assert (
        "Toujours tester la commande profile avant un commit."
        in result.content
    )
    assert result.content.count(
        "project-assistant:local-agents:start"
    ) == 1
    assert result.content.count(
        "project-assistant:local-agents:end"
    ) == 1


def test_django_react_keeps_generic_agents_generator(
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
        "AGENTS.md",
    )

    assert result.generator_name == "agents-déterministe"
