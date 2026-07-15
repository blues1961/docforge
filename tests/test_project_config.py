from pathlib import Path

import pytest

from docforge.detectors import TechnologyDetector
from docforge.project_config import (
    detect_profile,
    load_project_config,
    write_project_config,
)
from docforge.scanners import FileSystemScanner


def test_detect_profile_for_django_react(
    tmp_path: Path,
) -> None:
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "manage.py").write_text("", encoding="utf-8")

    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "package.json").write_text(
        """
        {
          "dependencies": {
            "react": "^18.3.1"
          }
        }
        """,
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    TechnologyDetector().detect(project)

    assert detect_profile(project) == "django-react"


def test_write_and_load_project_config(
    tmp_path: Path,
) -> None:
    project = FileSystemScanner().scan(tmp_path)

    path = write_project_config(project)

    assert path.exists()

    config = load_project_config(tmp_path)

    assert config is not None
    assert config.name == tmp_path.name
    assert config.profile == "base"
    assert config.documentation_add == []
    assert config.documentation_remove == []


def test_write_project_config_refuses_overwrite(
    tmp_path: Path,
) -> None:
    project = FileSystemScanner().scan(tmp_path)

    write_project_config(project)

    with pytest.raises(FileExistsError):
        write_project_config(project)
