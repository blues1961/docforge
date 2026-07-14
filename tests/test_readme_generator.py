from pathlib import Path

from project_assistant.analyzers import ReadmeAnalyzer
from project_assistant.detectors import TechnologyDetector
from project_assistant.generators import (
    ReadmeDocumentGenerator,
)
from project_assistant.scanners import FileSystemScanner


def test_readme_generator_uses_detected_project_facts(
    tmp_path: Path,
) -> None:
    backend = tmp_path / "backend"
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
    path("api/healthz/", HealthView.as_view(), name="health"),
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

    frontend = tmp_path / "frontend"
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
    labels:
      - traefik.enable=true
      - traefik.http.routers.demo-api.rule=Host(`demo.local`) && PathPrefix(`/api/`)
    networks:
      - edge

  frontend:
    build: ./frontend
    labels:
      - traefik.enable=true
      - traefik.http.routers.demo.rule=Host(`demo.local`)
    networks:
      - edge

networks:
  edge:
    external: true
"""

    for filename in (
        "docker-compose.dev.yml",
        "docker-compose.prod.yml",
    ):
        (tmp_path / filename).write_text(
            compose,
            encoding="utf-8",
        )

    (tmp_path / ".env.dev").write_text(
        "APP_ENV=dev\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.prod").write_text(
        "APP_ENV=prod\n",
        encoding="utf-8",
    )
    (tmp_path / ".env").symlink_to(".env.dev")

    (tmp_path / "Makefile").write_text(
        """
dev:
up:
down:
ps:
logs:
migrate:
check:
test:
backup:
restore:
""",
        encoding="utf-8",
    )

    (tmp_path / "README_DEV.md").write_text(
        "# Développement\n",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    TechnologyDetector().detect(project)

    facts = ReadmeAnalyzer().analyze(project)
    content = ReadmeDocumentGenerator().generate(
        project,
        facts,
    )

    assert "## Résumé du projet" in content
    assert "## Fonctionnalités principales" in content
    assert "## Architecture générale" in content
    assert "## Technologies utilisées" in content
    assert "## Installation" in content
    assert "## Utilisation" in content
    assert "## Configuration" in content
    assert "## Documentation complémentaire" in content

    assert "Django" in content
    assert "React" in content
    assert "PostgreSQL" in content
    assert "Traefik" in content
    assert "make up" in content
    assert "make test" in content
    assert "README_DEV.md" in content


def test_readme_generator_does_not_invent_business_purpose(
    tmp_path: Path,
) -> None:
    project = FileSystemScanner().scan(tmp_path)
    TechnologyDetector().detect(project)

    facts = ReadmeAnalyzer().analyze(project)
    content = ReadmeDocumentGenerator().generate(
        project,
        facts,
    )

    assert (
        "La description fonctionnelle précise doit être "
        "complétée"
        in content
    )
