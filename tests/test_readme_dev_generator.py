from pathlib import Path

from docforge.generators import (
    ReadmeDevDocumentGenerator,
)
from docforge.knowledge import (
    ProjectKnowledgeBuilder,
)
from docforge.scanners import FileSystemScanner


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

  frontend:
    build: ./frontend
    depends_on:
      - backend
    labels:
      - traefik.enable=true

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
    (root / ".env.local").write_text(
        "SECRET=test\n",
        encoding="utf-8",
    )
    (root / ".env").symlink_to(".env.dev")

    (root / "Makefile").write_text(
        """
dev:
prod:
up:
down:
restart:
rebuild:
ps:
logs:
migrate:
check:
test:
test-backend:
test-frontend:
""",
        encoding="utf-8",
    )


def test_readme_dev_generator_uses_project_knowledge(
    tmp_path: Path,
) -> None:
    _create_application(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    content = ReadmeDevDocumentGenerator().generate(
        project,
        knowledge,
    )

    assert "## Prérequis" in content
    assert "## Installation locale" in content
    assert "## Environnements" in content
    assert "## Services de développement" in content
    assert "## Commandes de développement" in content
    assert "## Tests" in content
    assert "## Flux de travail Git" in content
    assert "## Validation avant livraison" in content

    assert "make dev" in content
    assert "make up" in content
    assert "make test" in content
    assert "make test-backend" in content
    assert "make test-frontend" in content
    assert ".env.local" in content
    assert "backend" in content
    assert "frontend" in content
    assert "db" in content


def test_readme_dev_never_reproduces_secret_values(
    tmp_path: Path,
) -> None:
    _create_application(tmp_path)

    secret_value = "SECRET_VALUE_MUST_NOT_APPEAR"

    (tmp_path / ".env.local").write_text(
        f"DJANGO_SECRET_KEY={secret_value}\n",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    content = ReadmeDevDocumentGenerator().generate(
        project,
        knowledge,
    )

    assert ".env.local" in content
    assert secret_value not in content
