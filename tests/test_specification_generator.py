from pathlib import Path

from project_assistant.analyzers import (
    SpecificationAnalyzer,
)
from project_assistant.detectors import TechnologyDetector
from project_assistant.generators import (
    SpecificationDocumentGenerator,
)
from project_assistant.scanners import FileSystemScanner


def test_specification_generator_uses_detected_facts(
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

    (tmp_path / "docker-compose.dev.yml").write_text(
        compose,
        encoding="utf-8",
    )
    (tmp_path / "docker-compose.prod.yml").write_text(
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

    (tmp_path / "Makefile").write_text(
        """
check:
test:
ps:
""",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    TechnologyDetector().detect(project)

    facts = SpecificationAnalyzer().analyze(project)

    content = SpecificationDocumentGenerator().generate(
        project,
        facts,
    )

    assert "# Spécification —" in content
    assert "Django" in content
    assert "React" in content
    assert "PostgreSQL" in content
    assert "`healthz`" in content
    assert "`make test`" in content
    assert "`make check`" in content
