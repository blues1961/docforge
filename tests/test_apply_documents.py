import pytest
from pathlib import Path
import subprocess

from project_assistant.commands.apply import (
    apply_preview_documents,
)


def test_apply_preview_document_to_clean_repository(
    tmp_path: Path,
) -> None:
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=tmp_path,
        check=True,
    )

    tracked = tmp_path / "README.md"
    tracked.write_text("# Test\n", encoding="utf-8")

    subprocess.run(
        ["git", "add", "README.md"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    preview = (
        tmp_path
        / ".project-assistant"
        / "preview"
        / "docs"
        / "architecture.md"
    )
    preview.parent.mkdir(parents=True)
    preview.write_text(
        "# Architecture\n",
        encoding="utf-8",
    )

    applied = apply_preview_documents(
        tmp_path,
        ["docs/architecture.md"],
    )

    assert len(applied) == 1
    assert (
        tmp_path / "docs" / "architecture.md"
    ).read_text(encoding="utf-8") == "# Architecture\n"


def test_apply_protected_invariants_requires_owner_approval(
    tmp_path: Path,
) -> None:
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=tmp_path,
        check=True,
    )

    readme = tmp_path / "README.md"
    readme.write_text("# Test\n", encoding="utf-8")

    subprocess.run(
        ["git", "add", "README.md"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    preview = (
        tmp_path
        / ".project-assistant"
        / "preview"
        / "INVARIANTS.md"
    )
    preview.parent.mkdir(parents=True)
    preview.write_text(
        "# INVARIANTS.md\n",
        encoding="utf-8",
    )

    with pytest.raises(PermissionError):
        apply_preview_documents(
            tmp_path,
            ["INVARIANTS.md"],
        )

    applied = apply_preview_documents(
        tmp_path,
        ["INVARIANTS.md"],
        owner_approved=True,
    )

    assert len(applied) == 1
    assert (
        tmp_path / "INVARIANTS.md"
    ).read_text(encoding="utf-8") == "# INVARIANTS.md\n"
