import json
from pathlib import Path

from project_assistant.knowledge import (
    ProjectKnowledgeBuilder,
    write_project_knowledge,
)


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


def test_knowledge_builder_combines_project_analyzers(
    tmp_path: Path,
) -> None:
    _create_application(tmp_path)

    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    assert knowledge.schema_version == 1
    assert knowledge.identity.name == tmp_path.name
    assert knowledge.profile.name == "django-react"

    assert "Django" in knowledge.identity.frameworks
    assert "React" in knowledge.identity.frameworks
    assert (
        "PostgreSQL"
        in knowledge.identity.technologies
    )

    assert {
        service.name
        for service in knowledge.architecture.services
    } == {
        "backend",
        "db",
        "frontend",
    }

    assert len(knowledge.api.routes) >= 1
    assert "up" in knowledge.deployment.make_targets
    assert knowledge.specification.uses_django is True
    assert knowledge.readme.uses_react is True


def test_project_knowledge_is_json_serializable(
    tmp_path: Path,
) -> None:
    _create_application(tmp_path)

    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    output = write_project_knowledge(
        knowledge,
        tmp_path / "cache" / "knowledge.json",
    )

    data = json.loads(
        output.read_text(encoding="utf-8")
    )

    assert data["schema_version"] == 1
    assert data["identity"]["name"] == tmp_path.name
    assert data["profile"]["name"] == "django-react"
    assert "architecture" in data
    assert "deployment" in data
    assert "api" in data
    assert "specification" in data
    assert "readme" in data
