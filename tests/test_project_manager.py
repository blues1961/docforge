from pathlib import Path

from project_assistant.project_manager import ProjectManager
from project_assistant.project_registry import (
    ProjectRegistry,
)


def test_manager_reports_invalid_project_configuration(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "demo"
    project_root.mkdir()

    registry = ProjectRegistry(
        tmp_path / "projects.yml"
    )
    registry.add(
        project_root,
        profile="profil-inexistant",
    )

    manager = ProjectManager(registry)
    results = manager.refresh_all(clean=True)

    assert len(results) == 1
    assert results[0].error is not None
