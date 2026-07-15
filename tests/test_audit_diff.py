import json
from pathlib import Path

from docforge.audit_diff import (
    AuditDiffAnalyzer,
    AuditDiffMarkdownGenerator,
)


def _write_report(
    path: Path,
    projects: list[dict[str, object]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "summary": {},
                "projects": projects,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_audit_diff_detects_improvement_and_regression(
    tmp_path: Path,
) -> None:
    previous = tmp_path / "previous.json"
    current = tmp_path / "current.json"

    _write_report(
        previous,
        [
            {
                "name": "alpha",
                "state": "non-compliant",
                "score": 80,
                "error_count": 2,
                "warning_count": 1,
            },
            {
                "name": "beta",
                "state": "compliant",
                "score": 100,
                "error_count": 0,
                "warning_count": 0,
            },
        ],
    )

    _write_report(
        current,
        [
            {
                "name": "alpha",
                "state": "warning",
                "score": 95,
                "error_count": 0,
                "warning_count": 1,
            },
            {
                "name": "beta",
                "state": "non-compliant",
                "score": 75,
                "error_count": 2,
                "warning_count": 0,
            },
        ],
    )

    report = AuditDiffAnalyzer().compare(
        previous,
        current,
    )

    assert [item.name for item in report.improved] == [
        "alpha"
    ]
    assert [item.name for item in report.regressed] == [
        "beta"
    ]
    assert report.improved[0].score_delta == 15
    assert report.regressed[0].score_delta == -25


def test_audit_diff_detects_added_removed_and_unchanged(
    tmp_path: Path,
) -> None:
    previous = tmp_path / "previous.json"
    current = tmp_path / "current.json"

    _write_report(
        previous,
        [
            {
                "name": "stable",
                "state": "compliant",
                "score": 100,
                "error_count": 0,
                "warning_count": 0,
            },
            {
                "name": "removed",
                "state": "warning",
                "score": 90,
                "error_count": 0,
                "warning_count": 1,
            },
        ],
    )

    _write_report(
        current,
        [
            {
                "name": "stable",
                "state": "compliant",
                "score": 100,
                "error_count": 0,
                "warning_count": 0,
            },
            {
                "name": "added",
                "state": "compliant",
                "score": 100,
                "error_count": 0,
                "warning_count": 0,
            },
        ],
    )

    report = AuditDiffAnalyzer().compare(
        previous,
        current,
    )

    assert [item.name for item in report.unchanged] == [
        "stable"
    ]
    assert [item.name for item in report.added] == [
        "added"
    ]
    assert [item.name for item in report.removed] == [
        "removed"
    ]


def test_audit_diff_markdown_contains_summary(
    tmp_path: Path,
) -> None:
    previous = tmp_path / "previous.json"
    current = tmp_path / "current.json"

    _write_report(
        previous,
        [
            {
                "name": "demo",
                "state": "warning",
                "score": 90,
                "error_count": 0,
                "warning_count": 1,
            }
        ],
    )

    _write_report(
        current,
        [
            {
                "name": "demo",
                "state": "compliant",
                "score": 100,
                "error_count": 0,
                "warning_count": 0,
            }
        ],
    )

    report = AuditDiffAnalyzer().compare(
        previous,
        current,
    )

    markdown = AuditDiffMarkdownGenerator().generate(
        report
    )

    assert "# Évolution de la conformité" in markdown
    assert "Projets améliorés" in markdown
    assert "demo" in markdown
    assert "+10" in markdown
