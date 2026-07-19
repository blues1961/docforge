from pathlib import Path

from docforge.documentation_pipeline import (
    DocumentationPipeline,
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
.docforge/
.venv/
__pycache__/
.pytest_cache/
""",
        encoding="utf-8",
    )


def test_python_cli_security_document_is_generated(
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
        "docs/security.md",
    )

    assert (
        result.generator_name
        == "security-python-cli-déterministe"
    )

    assert "# Sécurité" in result.content
    assert "## Modèle de confiance" in result.content
    assert "## Protection des secrets" in result.content
    assert "## Aperçu sécurisé" in result.content
    assert "## Intégrité des invariants" in result.content
    assert "## Risques connus" in result.content
    assert "## Réponse à un incident" in result.content

    assert "SEC-001" in result.content
    assert "--owner-approved" in result.content
    assert "invariant-baseline.json" in result.content
    assert ".docforge/preview/" in result.content

    assert "Traefik" not in result.content
    assert "PostgreSQL" not in result.content
    assert "/home/" not in result.content


def test_project_knowledge_contains_security_facts(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    assert knowledge.security.controls
    assert "INVARIANTS.md" not in (
        knowledge.security.protected_documents
    )
