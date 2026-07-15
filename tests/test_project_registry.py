from pathlib import Path

from docforge.project_registry import (
    ProjectRegistry,
)


def test_registry_adds_and_loads_project(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "demo"
    project_root.mkdir()

    registry_path = tmp_path / "projects.yml"
    registry = ProjectRegistry(registry_path)

    registered = registry.add(
        project_root,
        profile="django-react",
    )

    assert registered.name == "demo"
    assert registered.profile == "django-react"

    loaded = registry.load()

    assert len(loaded) == 1
    assert loaded[0].path == project_root.resolve()
    assert loaded[0].enabled is True


def test_registry_updates_existing_project(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "demo"
    project_root.mkdir()

    registry = ProjectRegistry(
        tmp_path / "projects.yml"
    )

    registry.add(project_root)
    registry.add(
        project_root,
        name="application-demo",
        profile="base",
    )

    projects = registry.load()

    assert len(projects) == 1
    assert projects[0].name == "application-demo"
    assert projects[0].profile == "base"


def test_registry_removes_project(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "demo"
    project_root.mkdir()

    registry = ProjectRegistry(
        tmp_path / "projects.yml"
    )

    registry.add(project_root)

    assert registry.remove("demo") is True
    assert registry.load() == []


def test_registry_load_migrates_legacy_user_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from docforge import storage_paths

    monkeypatch.setattr(
        storage_paths.Path,
        "home",
        classmethod(lambda cls: tmp_path),
    )

    legacy_root = tmp_path / ".config" / "project-assistant"
    legacy_root.mkdir(parents=True)
    (legacy_root / "projects.yml").write_text(
        """
schema_version: 1
projects:
  - name: demo
    path: /tmp/demo
    enabled: true
""",
        encoding="utf-8",
    )

    registry = ProjectRegistry(storage_paths.registry_path())
    projects = registry.load()

    assert len(projects) == 1
    assert projects[0].name == "demo"
    assert (tmp_path / ".config" / "docforge" / "projects.yml").is_file()
    assert (legacy_root / "projects.yml").exists() is False
