from pathlib import Path

from docforge.invariant_integrity import (
    InvariantIntegrityManager,
)


def _write_protected_files(root: Path) -> None:
    for filename in (
        "INVARIANTS.md",
        "AGENTS.md",
        "CODEX_START.md",
    ):
        (root / filename).write_text(
            f"# {filename}\n",
            encoding="utf-8",
        )


def test_approved_invariants_verify_successfully(
    tmp_path: Path,
) -> None:
    template = tmp_path / "template"
    template.mkdir()
    _write_protected_files(template)

    manager = InvariantIntegrityManager(
        tmp_path / "baseline.json"
    )

    manager.approve(template)
    report = manager.verify(template)

    assert report.baseline_exists is True
    assert report.valid is True
    assert report.drifts == []


def test_modified_invariant_is_detected(
    tmp_path: Path,
) -> None:
    template = tmp_path / "template"
    template.mkdir()
    _write_protected_files(template)

    manager = InvariantIntegrityManager(
        tmp_path / "baseline.json"
    )

    manager.approve(template)

    (template / "INVARIANTS.md").write_text(
        "# Invariants modifiés\n",
        encoding="utf-8",
    )

    report = manager.verify(template)

    assert report.valid is False
    assert any(
        drift.path == "INVARIANTS.md"
        and drift.status == "modified"
        for drift in report.drifts
    )


def test_deleted_protected_file_is_detected(
    tmp_path: Path,
) -> None:
    template = tmp_path / "template"
    template.mkdir()
    _write_protected_files(template)

    manager = InvariantIntegrityManager(
        tmp_path / "baseline.json"
    )

    manager.approve(template)
    (template / "AGENTS.md").unlink()

    report = manager.verify(template)

    assert any(
        drift.path == "AGENTS.md"
        and drift.status == "deleted"
        for drift in report.drifts
    )
