from pathlib import Path

from docforge.analyzers import (
    PythonCliSpecificationAnalyzer,
)
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


def test_python_cli_specification_analyzer_builds_requirements(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    facts = PythonCliSpecificationAnalyzer().analyze(
        knowledge
    )

    assert facts.package_name == "demo-cli"
    assert facts.version == "0.1.0"
    assert "python-cli" in facts.supported_profiles
    assert "README.md" in facts.required_documents
    assert "INVARIANTS.md" not in facts.protected_documents
    assert facts.functional_requirements
    assert facts.security_requirements
    assert facts.acceptance_criteria


def test_python_cli_specification_generator_uses_product_contract(
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
        "docs/specification.md",
    )

    assert (
        result.generator_name
        == "specification-python-cli-déterministe"
    )

    assert "## Objectif" in result.content
    assert "## Périmètre" in result.content
    assert "## Concepts principaux" in result.content
    assert "## Exigences fonctionnelles" in result.content
    assert "## Exigences non fonctionnelles" in result.content
    assert "## Exigences de sécurité" in result.content
    assert "## Critères d’acceptation" in result.content
    assert "## Limites connues" in result.content

    assert "EF-001" in result.content
    assert "ENF-001" in result.content
    assert "SEC-001" in result.content
    assert "ProjectKnowledge" in result.content
    assert ".docforge/preview" in result.content
    assert "owner-approved" in result.content
    assert "demo-cli" in result.content
    assert "demo_cli.cli:app" in result.content

    assert "Traefik" not in result.content
    assert "PostgreSQL" not in result.content
    assert ".env.dev" not in result.content
    assert "make dev" not in result.content
    assert "/home/" not in result.content


def test_django_react_keeps_standard_specification_generator(
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
        "docs/specification.md",
    )

    assert (
        result.generator_name
        == "specification-déterministe"
    )
