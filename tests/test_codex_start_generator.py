from pathlib import Path

from docforge.generators import (
    CodexStartDocumentGenerator,
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
  "dependencies": {"react": "^18"},
  "devDependencies": {"vite": "^5"}
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
  frontend:
    build: ./frontend
networks:
  edge:
    external: true
"""

    (root / "docker-compose.dev.yml").write_text(
        compose,
        encoding="utf-8",
    )
    (root / "docker-compose.prod.yml").write_text(
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
prod:
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


def test_codex_start_contains_required_context(
    tmp_path: Path,
) -> None:
    _create_application(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    content = CodexStartDocumentGenerator().generate(
        project,
        knowledge,
    )

    assert "## Mission" in content
    assert "## Ordre de lecture" in content
    assert "## Contexte du projet" in content
    assert "## Architecture essentielle" in content
    assert "## Invariants à respecter" in content
    assert "## Commandes importantes" in content
    assert "## État de l’environnement" in content
    assert "## Validation avant de terminer" in content
    assert "## Instructions locales" in content

    assert "app-template/INVARIANTS.md" in content
    assert "make check" in content
    assert "make test" in content
    assert ".env.local" in content


def test_codex_start_preserves_local_section(
    tmp_path: Path,
) -> None:
    _create_application(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    existing = """
# CODEX_START.md

<!-- project-assistant:local-codex:start -->

Vérifier le chiffrement côté client avant toute modification.

<!-- project-assistant:local-codex:end -->
"""

    content = CodexStartDocumentGenerator().generate(
        project,
        knowledge,
        existing_content=existing,
    )

    assert (
        "Vérifier le chiffrement côté client avant toute modification."
        in content
    )
    assert content.count(
        "project-assistant:local-codex:start"
    ) == 1
    assert content.count(
        "project-assistant:local-codex:end"
    ) == 1
