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


def test_python_cli_invariants_uses_cli_rules(
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
        "INVARIANTS.md",
    )

    assert (
        result.generator_name
        == "invariants-python-cli-déterministe-protégé"
    )

    assert "## Invariants de connaissance" in result.content
    assert "## Invariants des profils" in result.content
    assert "## Invariants du pipeline documentaire" in result.content
    assert "## Invariants de protection" in result.content
    assert "## Invariants des générateurs" in result.content
    assert "## Invariants des commandes CLI" in result.content
    assert "## Invariants des tests" in result.content

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
    assert "/home/" not in result.content


def test_python_cli_invariants_preserves_local_sections(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    existing = """
# INVARIANTS.md

<!-- project-assistant:local-invariants:start -->

Le schéma de ProjectKnowledge doit rester rétrocompatible.

<!-- project-assistant:local-invariants:end -->

<!-- project-assistant:approved-deviations:start -->

Dérogation approuvée : compatibilité temporaire avec Python 3.11.

<!-- project-assistant:approved-deviations:end -->
"""

    (tmp_path / "INVARIANTS.md").write_text(
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
        "INVARIANTS.md",
    )

    assert (
        "Le schéma de ProjectKnowledge doit rester rétrocompatible."
        in result.content
    )
    assert (
        "Dérogation approuvée : compatibilité temporaire avec "
        "Python 3.11."
        in result.content
    )

    assert result.content.count(
        "project-assistant:local-invariants:start"
    ) == 1
    assert result.content.count(
        "project-assistant:local-invariants:end"
    ) == 1
    assert result.content.count(
        "project-assistant:approved-deviations:start"
    ) == 1
    assert result.content.count(
        "project-assistant:approved-deviations:end"
    ) == 1


def test_django_react_keeps_standard_invariants_generator(
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
        "INVARIANTS.md",
    )

    assert (
        result.generator_name
        == "invariants-déterministe-protégé"
    )
