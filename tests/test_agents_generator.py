from pathlib import Path

from project_assistant.generators import (
    AgentsDocumentGenerator,
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

    (root / "Makefile").write_text(
        """
check:
test:
ps:
""",
        encoding="utf-8",
    )


def test_agents_generator_contains_required_rules(
    tmp_path: Path,
) -> None:
    _create_application(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    content = AgentsDocumentGenerator().generate(
        project,
        knowledge,
    )

    assert "## Portée" in content
    assert "## Ordre de lecture obligatoire" in content
    assert "## Priorité des sources" in content
    assert "## Règles non négociables" in content
    assert "## Architecture détectée" in content
    assert "## Actions interdites" in content
    assert "## Vérifications obligatoires" in content
    assert "## Protection des invariants" in content
    assert "## Instructions locales" in content

    assert "app-template/INVARIANTS.md" in content
    assert "make check" in content
    assert "make test" in content
    assert ".env.local" in content


def test_agents_generator_preserves_local_section(
    tmp_path: Path,
) -> None:
    _create_application(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    existing = """
# AGENTS.md

<!-- project-assistant:local-agents:start -->

Toujours vérifier le chiffrement côté client.

<!-- project-assistant:local-agents:end -->
"""

    content = AgentsDocumentGenerator().generate(
        project,
        knowledge,
        existing_content=existing,
    )

    assert (
        "Toujours vérifier le chiffrement côté client."
        in content
    )
    assert content.count(
        "project-assistant:local-agents:start"
    ) == 1
    assert content.count(
        "project-assistant:local-agents:end"
    ) == 1
