import subprocess
from pathlib import Path

from docforge.project_registry import (
    ProjectRegistry,
)
from docforge.status_manager import (
    StatusManager,
)


def _initialize_git_repository(root: Path) -> None:
    subprocess.run(
        ["git", "init"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "git",
            "config",
            "user.email",
            "test@example.com",
        ],
        cwd=root,
        check=True,
    )
    subprocess.run(
        [
            "git",
            "config",
            "user.name",
            "Test",
        ],
        cwd=root,
        check=True,
    )

    (root / "README.md").write_text(
        "# Projet\n",
        encoding="utf-8",
    )

    subprocess.run(
        ["git", "add", "README.md"],
        cwd=root,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial"],
        cwd=root,
        check=True,
        capture_output=True,
    )


def test_git_status_detects_clean_and_dirty_repository(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    root.mkdir()
    _initialize_git_repository(root)

    manager = StatusManager()

    clean = manager._read_git_status(root)

    assert clean.is_repository is True
    assert clean.dirty is False
    assert clean.branch in {"main", "master"}

    (root / "README.md").write_text(
        "# Projet modifié\n",
        encoding="utf-8",
    )
    (root / "new.txt").write_text(
        "nouveau\n",
        encoding="utf-8",
    )

    dirty = manager._read_git_status(root)

    assert dirty.dirty is True
    assert dirty.modified_count == 1
    assert dirty.untracked_count == 1


def test_documentation_status_detects_changed_and_new_files(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    root.mkdir()

    docs = root / "docs"
    docs.mkdir()

    (docs / "architecture.md").write_text(
        "# Ancienne architecture\n",
        encoding="utf-8",
    )

    preview = (
        root
        / ".docforge"
        / "preview"
        / "docs"
    )
    preview.mkdir(parents=True)

    (preview / "architecture.md").write_text(
        "# Nouvelle architecture\n",
        encoding="utf-8",
    )
    (preview / "deployment.md").write_text(
        "# Déploiement\n",
        encoding="utf-8",
    )

    manager = StatusManager()
    status = manager._read_documentation_status(
        root
    )

    assert status.preview_exists is True
    assert status.preview_documents == 2
    assert status.changed_documents == [
        "docs/architecture.md"
    ]
    assert status.new_documents == [
        "docs/deployment.md"
    ]


def test_documentation_status_reports_identical_preview(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    root.mkdir()

    target = root / "README.md"
    target.write_text(
        "# Projet\n",
        encoding="utf-8",
    )

    preview = (
        root
        / ".docforge"
        / "preview"
        / "README.md"
    )
    preview.parent.mkdir(parents=True)
    preview.write_text(
        "# Projet\n",
        encoding="utf-8",
    )

    manager = StatusManager()
    status = manager._read_documentation_status(
        root
    )

    assert status.preview_exists is True
    assert status.changed_documents == []
    assert status.new_documents == []
