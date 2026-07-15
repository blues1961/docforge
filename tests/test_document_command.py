from pathlib import Path

from docforge.commands.document import (
    generate_documentation_preview,
)


def _create_project(root: Path) -> None:
    (root / ".env.dev").write_text(
        "APP_ENV=dev\n",
        encoding="utf-8",
    )
    (root / ".env.prod").write_text(
        "APP_ENV=prod\n",
        encoding="utf-8",
    )
    (root / ".env.local").write_text(
        "POSTGRES_PASSWORD=secret\n",
        encoding="utf-8",
    )
    (root / ".env").symlink_to(".env.dev")

    backend = root / "backend"
    backend.mkdir()
    (backend / "manage.py").write_text(
        "",
        encoding="utf-8",
    )
    (backend / "requirements.txt").write_text(
        "Django==5.0\npsycopg2-binary==2.9\n",
        encoding="utf-8",
    )

    frontend = root / "frontend"
    frontend.mkdir()
    (frontend / "package.json").write_text(
        """
{
  "dependencies": {
    "react": "^18.3.1"
  },
  "devDependencies": {
    "vite": "^5.4.2"
  }
}
""",
        encoding="utf-8",
    )

    (root / "docker-compose.dev.yml").write_text(
        """
services:
  db:
    image: postgres:16-alpine
  backend:
    build: ./backend
    depends_on:
      - db
  frontend:
    image: node:20-alpine
    depends_on:
      - backend
""",
        encoding="utf-8",
    )

    (root / "docker-compose.prod.yml").write_text(
        """
services:
  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
  backend:
    build: ./backend
    depends_on:
      - db
    networks:
      - appnet
      - edge
    labels:
      - traefik.enable=true
      - traefik.http.routers.api.rule=Host(`api.example.com`)
  frontend:
    build: ./frontend
    depends_on:
      - backend
    networks:
      - appnet
      - edge

networks:
  appnet:
  edge:
    external: true

volumes:
  pgdata:
""",
        encoding="utf-8",
    )

    (root / "Makefile").write_text(
        """
dev:
\t./scripts/env-switch.sh dev

prod:
\t./scripts/env-switch.sh prod

up:
\tdocker compose up -d

migrate:
\tdocker compose exec backend python manage.py migrate

restore:
\t./scripts/restore-db.sh

check:
\t./scripts/check-invariants.sh

ps:
\tdocker compose ps

logs:
\tdocker compose logs

test:
\tpytest
""",
        encoding="utf-8",
    )

    required_documents = {
        "README.md": "# Demo\n",
        "README_DEV.md": "# Demo Dev\n",
        "CODEX_START.md": "# CODEX_START\n",
        "AGENTS.md": "# AGENTS\n",
        "INVARIANTS.md": "# INVARIANTS\n",
        "docs/specification.md": "# Specification\n",
        "docs/api.md": "# API\n",
    }

    for relative_path, content in required_documents.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    (root / ".project-assistant.yml").write_text(
        """
schema_version: 1
project:
  name: demo
  profile: django-react
documentation:
  add: []
  remove: []
scan:
  exclude: []
""",
        encoding="utf-8",
    )


def test_document_command_uses_deterministic_generators(
    tmp_path: Path,
) -> None:
    _create_project(tmp_path)

    _, _, generated = generate_documentation_preview(
        tmp_path,
        clean=True,
    )

    by_path = {
        item.document_path: item
        for item in generated
    }

    architecture = by_path["docs/architecture.md"]
    deployment = by_path["docs/deployment.md"]

    assert architecture.generator == "architecture-déterministe"
    assert deployment.generator == "deployment-déterministe"

    architecture_content = architecture.preview_path.read_text(
        encoding="utf-8"
    )
    deployment_content = deployment.preview_path.read_text(
        encoding="utf-8"
    )

    assert "# Architecture —" in architecture_content
    assert "Host(`api.example.com`)" in architecture_content

    assert "# Déploiement —" in deployment_content
    assert "make prod" in deployment_content
    assert "make migrate" in deployment_content


def test_refresh_regenerates_existing_deterministic_documents(
    tmp_path: Path,
) -> None:
    _create_project(tmp_path)

    architecture = tmp_path / "docs" / "architecture.md"
    deployment = tmp_path / "docs" / "deployment.md"

    architecture.write_text(
        "# Ancienne architecture\n",
        encoding="utf-8",
    )
    deployment.write_text(
        "# Ancien déploiement\n",
        encoding="utf-8",
    )

    _, _, generated_without_refresh = (
        generate_documentation_preview(
            tmp_path,
            clean=True,
            refresh=False,
        )
    )

    paths_without_refresh = {
        item.document_path
        for item in generated_without_refresh
    }

    assert "docs/architecture.md" not in paths_without_refresh
    assert "docs/deployment.md" not in paths_without_refresh

    _, _, generated_with_refresh = (
        generate_documentation_preview(
            tmp_path,
            clean=True,
            refresh=True,
        )
    )

    by_path = {
        item.document_path: item
        for item in generated_with_refresh
    }

    assert (
        by_path["docs/architecture.md"].generator
        == "architecture-déterministe"
    )
    assert (
        by_path["docs/deployment.md"].generator
        == "deployment-déterministe"
    )

    assert (
        by_path["docs/specification.md"].generator
        == "specification-déterministe"
    )

    assert (
        by_path["AGENTS.md"].generator
        == "agents-déterministe"
    )

    assert (
        by_path["CODEX_START.md"].generator
        == "codex-start-déterministe"
    )

    assert (
        by_path["README.md"].generator
        == "readme-déterministe"
    )

    assert (
        by_path["README_DEV.md"].generator
        == "readme-dev-déterministe"
    )

    preview_architecture = (
        tmp_path
        / ".project-assistant"
        / "preview"
        / "docs"
        / "architecture.md"
    )

    preview_deployment = (
        tmp_path
        / ".project-assistant"
        / "preview"
        / "docs"
        / "deployment.md"
    )

    assert "# Architecture —" in preview_architecture.read_text(
        encoding="utf-8"
    )
    assert "# Déploiement —" in preview_deployment.read_text(
        encoding="utf-8"
    )

    # Les documents réels ne doivent pas être modifiés.
    assert architecture.read_text(
        encoding="utf-8"
    ) == "# Ancienne architecture\n"

    assert deployment.read_text(
        encoding="utf-8"
    ) == "# Ancien déploiement\n"


def _create_python_cli_for_document_test(
    root: Path,
) -> None:
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


def test_refresh_uses_documents_supported_by_registry(
    tmp_path: Path,
) -> None:
    _create_python_cli_for_document_test(tmp_path)

    _, _, generated = generate_documentation_preview(
        path=tmp_path,
        refresh=True,
        clean=True,
    )

    generated_paths = {
        item.document_path
        for item in generated
    }

    assert "docs/cli.md" in generated_paths
    assert "docs/configuration.md" in generated_paths
    assert "docs/security.md" in generated_paths
