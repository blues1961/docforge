from pathlib import Path

import pytest

from project_assistant.documentation_pipeline import (
    DocumentationPipeline,
    UnsupportedDeterministicDocumentError,
)
from project_assistant.knowledge import (
    ProjectKnowledgeBuilder,
)
from project_assistant.scanners import FileSystemScanner


def _create_application(root: Path) -> None:
    backend = root / "backend"
    backend.mkdir()

    (backend / "manage.py").write_text(
        "",
        encoding="utf-8",
    )
    (backend / "requirements.txt").write_text(
        "Django\npsycopg2-binary\n",
        encoding="utf-8",
    )

    api = backend / "api"
    api.mkdir()

    (api / "urls.py").write_text(
        """
from django.urls import path
from .views import HealthView

urlpatterns = [
    path(
        "api/healthz/",
        HealthView.as_view(),
        name="health",
    ),
]
""",
        encoding="utf-8",
    )

    (api / "views.py").write_text(
        """
class HealthView:
    def get(self, request):
        pass
""",
        encoding="utf-8",
    )

    frontend = root / "frontend"
    frontend.mkdir()

    (frontend / "package.json").write_text(
        """
{
  "dependencies": {
    "react": "^18"
  },
  "devDependencies": {
    "vite": "^5"
  }
}
""",
        encoding="utf-8",
    )

    compose = """
services:
  db:
    image: postgres:16

  backend:
    build: ./backend
    depends_on:
      - db
    labels:
      - traefik.enable=true
      - traefik.http.routers.demo-api.rule=PathPrefix(`/api/`)

  frontend:
    build: ./frontend
    depends_on:
      - backend
    labels:
      - traefik.enable=true
      - traefik.http.routers.demo.rule=Host(`demo.local`)

networks:
  edge:
    external: true
"""

    for filename in (
        "docker-compose.dev.yml",
        "docker-compose.prod.yml",
    ):
        (root / filename).write_text(
            compose,
            encoding="utf-8",
        )

    (root / ".env.dev").write_text(
        "APP_ENV=dev\n",
        encoding="utf-8",
    )
    (root / ".env.prod").write_text(
        "APP_ENV=prod\n",
        encoding="utf-8",
    )
    (root / ".env").symlink_to(".env.dev")

    (root / "Makefile").write_text(
        """
dev:
up:
down:
ps:
logs:
migrate:
check:
test:
""",
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    ("document_path", "generator_name", "heading"),
    [
        (
            "AGENTS.md",
            "agents-déterministe",
            "## Portée",
        ),
        (
            "CODEX_START.md",
            "codex-start-déterministe",
            "## Mission",
        ),
        (
            "README.md",
            "readme-déterministe",
            "## Résumé du projet",
        ),
        (
            "README_DEV.md",
            "readme-dev-déterministe",
            "## Prérequis",
        ),
        (
            "docs/api.md",
            "api-déterministe",
            "# API",
        ),
        (
            "docs/architecture.md",
            "architecture-déterministe",
            "# Architecture",
        ),
        (
            "docs/deployment.md",
            "deployment-déterministe",
            "# Déploiement",
        ),
        (
            "docs/specification.md",
            "specification-déterministe",
            "# Spécification",
        ),
    ],
)
def test_pipeline_generates_supported_documents(
    tmp_path: Path,
    document_path: str,
    generator_name: str,
    heading: str,
) -> None:
    _create_application(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    result = DocumentationPipeline(
        knowledge
    ).generate(
        project,
        document_path,
    )

    assert result.document_path == document_path
    assert result.generator_name == generator_name
    assert heading in result.content


def test_pipeline_rejects_unsupported_document(
    tmp_path: Path,
) -> None:
    _create_application(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    pipeline = DocumentationPipeline(knowledge)

    with pytest.raises(
        UnsupportedDeterministicDocumentError
    ):
        pipeline.generate(
            project,
            "CHANGELOG.md",
        )


def test_pipeline_registry_generates_python_cli_documents(
    tmp_path: Path,
) -> None:
    package = tmp_path / "project_assistant"
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

    (tmp_path / "tests").mkdir()

    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "demo-cli"
version = "0.1.0"

[project.scripts]
demo-cli = "project_assistant.cli:app"
""",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )
    pipeline = DocumentationPipeline(knowledge)

    expected = {
        "docs/cli.md": "cli-python-cli-déterministe",
        "docs/configuration.md": (
            "configuration-python-cli-déterministe"
        ),
        "docs/security.md": (
            "security-python-cli-déterministe"
        ),
    }

    for document_path, generator_name in expected.items():
        result = pipeline.generate(
            project,
            document_path,
        )

        assert result.document_path == document_path
        assert result.generator_name == generator_name


def test_pipeline_registry_does_not_expose_python_cli_only_document(
    tmp_path: Path,
) -> None:
    _create_application(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    assert knowledge.profile.name != "python-cli"

    pipeline = DocumentationPipeline(knowledge)

    with pytest.raises(
        UnsupportedDeterministicDocumentError
    ):
        pipeline.generate(
            project,
            "docs/security.md",
        )
