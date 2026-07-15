from pathlib import Path

from project_assistant.detectors import (
    TechnologyDetector,
)
from project_assistant.profiles import (
    DjangoReactProfile,
    GenericProfile,
    ProfileDetector,
    ProfileFacts,
    PythonCliProfile,
)
from project_assistant.scanners import (
    FileSystemScanner,
)


def _create_django_react_project(root: Path) -> None:
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

    for filename in (
        "docker-compose.dev.yml",
        "docker-compose.prod.yml",
    ):
        (root / filename).write_text(
            "services: {}\n",
            encoding="utf-8",
        )


def _create_python_cli_project(root: Path) -> None:
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


def _scan_and_detect(root: Path):
    project = FileSystemScanner().scan(root)
    TechnologyDetector().detect(project)
    return project


def test_detects_django_react_profile(
    tmp_path: Path,
) -> None:
    _create_django_react_project(tmp_path)
    project = _scan_and_detect(tmp_path)

    detector = ProfileDetector()
    profile = detector.detect(project)
    resolved = detector.resolve(project)

    assert isinstance(profile, ProfileFacts)
    assert profile.name == "django-react"
    assert profile.confidence >= 50
    assert isinstance(resolved, DjangoReactProfile)
    assert resolved.name == profile.name
    assert "docs/api.md" in (
        profile.document_policy.required_documents
    )


def test_detects_python_cli_profile(
    tmp_path: Path,
) -> None:
    _create_python_cli_project(tmp_path)
    project = _scan_and_detect(tmp_path)

    detector = ProfileDetector()
    profile = detector.detect(project)
    resolved = detector.resolve(project)

    assert isinstance(profile, ProfileFacts)
    assert profile.name == "python-cli"
    assert profile.confidence >= 50
    assert isinstance(resolved, PythonCliProfile)
    assert resolved.name == profile.name
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

    project = _scan_and_detect(tmp_path)

    detector = ProfileDetector()
    profile = detector.detect(project)
    resolved = detector.resolve(project)

    assert isinstance(profile, ProfileFacts)
    assert profile.name == "generic"
    assert profile.confidence == 1
    assert isinstance(resolved, GenericProfile)
    assert resolved.name == profile.name
