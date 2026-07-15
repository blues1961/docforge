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


def test_verify_migrates_legacy_manifest_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from docforge import storage_paths

    monkeypatch.setattr(
        storage_paths.Path,
        "home",
        classmethod(lambda cls: tmp_path),
    )

    template = tmp_path / "template"
    template.mkdir()
    _write_protected_files(template)

    legacy_root = tmp_path / ".config" / "project-assistant"
    legacy_root.mkdir(parents=True)
    legacy_manifest = legacy_root / "invariant-baseline.json"

    legacy_manifest.write_text(
        """
{
  "schema_version": 1,
  "template_root": "%s",
  "approved_at": "2026-01-01T00:00:00+00:00",
  "files": [
    {
      "path": "INVARIANTS.md",
      "exists": true,
      "sha256": "%s"
    },
    {
      "path": "AGENTS.md",
      "exists": true,
      "sha256": "%s"
    },
    {
      "path": "CODEX_START.md",
      "exists": true,
      "sha256": "%s"
    }
  ]
}
"""
        % (
            str(template.resolve()),
            __import__("hashlib").sha256((template / "INVARIANTS.md").read_bytes()).hexdigest(),
            __import__("hashlib").sha256((template / "AGENTS.md").read_bytes()).hexdigest(),
            __import__("hashlib").sha256((template / "CODEX_START.md").read_bytes()).hexdigest(),
        ),
        encoding="utf-8",
    )

    migrated_manager = InvariantIntegrityManager(
        storage_paths.invariant_manifest_path()
    )
    report = migrated_manager.verify(template)

    assert report.baseline_exists is True
    assert report.valid is True
    assert (
        tmp_path / ".config" / "docforge" / "invariant-baseline.json"
    ).is_file()
    assert legacy_manifest.exists() is False
