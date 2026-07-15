from pathlib import Path

from docforge.generators import (
    InvariantsDocumentGenerator,
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
check:
test:
ps:
""",
        encoding="utf-8",
    )


def test_invariants_generator_contains_protected_structure(
    tmp_path: Path,
) -> None:
    _create_application(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    content = InvariantsDocumentGenerator().generate(
        project,
        knowledge,
    )

    assert "## Autorité" in content
    assert "## Invariants d’environnement" in content
    assert "## Invariants de sécurité" in content
    assert "## Invariants d’architecture" in content
    assert "## Invariants Docker Compose" in content
    assert "## Invariants Makefile et scripts" in content
    assert "## Invariants de documentation" in content
    assert "## Règles locales du projet" in content
    assert "## Dérogations explicitement approuvées" in content
    assert "## Validation obligatoire" in content

    assert "app-template/INVARIANTS.md" in content
    assert "make check" in content
    assert ".env.local" in content


def test_invariants_generator_preserves_local_rules_and_deviations(
    tmp_path: Path,
) -> None:
    _create_application(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    existing = """
<!-- project-assistant:local-invariants:start -->

Le chiffrement doit rester côté client.

<!-- project-assistant:local-invariants:end -->

<!-- project-assistant:approved-deviations:start -->

Dérogation approuvée : port historique temporaire.

<!-- project-assistant:approved-deviations:end -->
"""

    content = InvariantsDocumentGenerator().generate(
        project,
        knowledge,
        existing_content=existing,
    )

    assert "Le chiffrement doit rester côté client." in content
    assert (
        "Dérogation approuvée : port historique temporaire."
        in content
    )
