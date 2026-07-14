from pathlib import Path

from project_assistant.detectors import (
    TechnologyDetector,
)
from project_assistant.profiles import (
    ProfileDetector,
)
from project_assistant.scanners import (
    FileSystemScanner,
)


def test_detects_django_react_profile(
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

    for filename in (
        "docker-compose.dev.yml",
        "docker-compose.prod.yml",
    ):
        (tmp_path / filename).write_text(
            "services: {}\n",
            encoding="utf-8",
        )

    project = FileSystemScanner().scan(tmp_path)
    TechnologyDetector().detect(project)

    profile = ProfileDetector().detect(project)

    assert profile.name == "django-react"
    assert profile.confidence >= 50
    assert "docs/api.md" in (
        profile.document_policy.required_documents
    )


def test_detects_python_cli_profile(
    tmp_path: Path,
) -> None:
    package = tmp_path / "demo_cli"
    package.mkdir()

    (package / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )
    (package / "cli.py").write_text(
        "def main(): pass\n",
        encoding="utf-8",
    )

    (tmp_path / "tests").mkdir()

    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "demo-cli"
version = "0.1.0"

[project.scripts]
demo-cli = "demo_cli.cli:main"
""",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    TechnologyDetector().detect(project)

    profile = ProfileDetector().detect(project)

    assert profile.name == "python-cli"
    assert profile.confidence >= 50
    assert "docs/cli.md" in (
        profile.document_policy.required_documents
    )
    assert "docs/api.md" not in (
        profile.document_policy.required_documents
    )


def test_falls_back_to_generic_profile(
    tmp_path: Path,
) -> None:
    (tmp_path / "notes.txt").write_text(
        "Projet sans structure connue.\n",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    TechnologyDetector().detect(project)

    profile = ProfileDetector().detect(project)

    assert profile.name == "generic"
    assert profile.confidence == 1
