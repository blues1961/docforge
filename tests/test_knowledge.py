import json
from pathlib import Path

from docforge.detectors import TechnologyDetector
from docforge.knowledge import (
    ProjectKnowledgeBuilder,
    write_project_knowledge,
)
from docforge.profiles import PythonCliProfile
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
    assert "pyproject" in data
    assert "cli" in data
    assert "configuration" in data
    assert "security" in data
    assert "architecture" in data
    assert "deployment" in data
    assert "api" in data
    assert "specification" in data
    assert "readme" in data



def _create_python_cli(root: Path) -> None:
    package = root / "demo_cli"
    package.mkdir()

    (package / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )
    (package / "cli.py").write_text(
        "def main(): pass\n",
        encoding="utf-8",
    )

    (root / "tests").mkdir()

    (root / "pyproject.toml").write_text(
        """
[project]
name = "demo-cli"
version = "0.1.0"

[project.scripts]
demo-cli = "demo_cli.cli:main"
""",
        encoding="utf-8",
    )


class SpyPythonCliProfile(PythonCliProfile):
    def __init__(self) -> None:
        self.analyzer_registry_built = False

    def build_analyzer_registry(self):
        self.analyzer_registry_built = True
        return super().build_analyzer_registry()


def test_knowledge_builder_uses_profile_analyzer_registry(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    TechnologyDetector().detect(project)

    profile = SpyPythonCliProfile()
    knowledge = ProjectKnowledgeBuilder().build(
        project,
        profile_instance=profile,
    )

    assert profile.analyzer_registry_built is True
    assert knowledge.profile.name == "python-cli"


def test_project_knowledge_exposes_docforge_storage_paths(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    assert knowledge.configuration.user_config_root == "~/.config/docforge"
    assert knowledge.configuration.project_state_root == ".docforge"
    assert knowledge.configuration.project_config_file == ".docforge.yml"


def test_python_cli_knowledge_suppresses_env_convention_findings(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    knowledge = (
        ProjectKnowledgeBuilder()
        .build_from_path(tmp_path)
    )

    finding_codes = {
        finding["code"]
        for finding in knowledge.findings
    }

    assert "ENV002" not in finding_codes
    assert "ENV003" not in finding_codes
    assert "ENV004" not in finding_codes
