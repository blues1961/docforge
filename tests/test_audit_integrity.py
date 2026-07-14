from pathlib import Path

import pytest

from project_assistant.audit_manager import (
    AuditManager,
    InvariantIntegrityError,
)
from project_assistant.invariant_integrity import (
    InvariantIntegrityManager,
)
from project_assistant.project_registry import (
    ProjectRegistry,
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


def test_audit_is_blocked_without_approved_baseline(
    tmp_path: Path,
) -> None:
    template = tmp_path / "template"
    template.mkdir()
    _write_protected_files(template)

    registry = ProjectRegistry(
        tmp_path / "projects.yml"
    )
    integrity = InvariantIntegrityManager(
        tmp_path / "baseline.json"
    )

    manager = AuditManager(
        registry=registry,
        integrity_manager=integrity,
    )

    with pytest.raises(InvariantIntegrityError) as error:
        manager.audit_all(template)

    assert error.value.report.baseline_exists is False


def test_audit_is_blocked_when_invariants_drift(
    tmp_path: Path,
) -> None:
    template = tmp_path / "template"
    template.mkdir()
    _write_protected_files(template)

    registry = ProjectRegistry(
        tmp_path / "projects.yml"
    )
    integrity = InvariantIntegrityManager(
        tmp_path / "baseline.json"
    )

    integrity.approve(template)

    (template / "INVARIANTS.md").write_text(
        "# Modification non approuvée\n",
        encoding="utf-8",
    )

    manager = AuditManager(
        registry=registry,
        integrity_manager=integrity,
    )

    with pytest.raises(InvariantIntegrityError) as error:
        manager.audit_all(template)

    assert error.value.report.baseline_exists is True
    assert error.value.report.valid is False
    assert any(
        drift.path == "INVARIANTS.md"
        for drift in error.value.report.drifts
    )


def test_audit_runs_with_approved_invariants(
    tmp_path: Path,
) -> None:
    template = tmp_path / "template"
    template.mkdir()
    _write_protected_files(template)

    registry = ProjectRegistry(
        tmp_path / "projects.yml"
    )
    integrity = InvariantIntegrityManager(
        tmp_path / "baseline.json"
    )

    integrity.approve(template)

    manager = AuditManager(
        registry=registry,
        integrity_manager=integrity,
    )

    results = manager.audit_all(template)

    assert results == []
