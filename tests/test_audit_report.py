import json
from pathlib import Path

from docforge.analyzers import (
    ComplianceFinding,
    TemplateComplianceReport,
)
from docforge.audit_manager import (
    ProjectAuditResult,
)
from docforge.audit_report import (
    AuditReportGenerator,
)
from docforge.project_registry import (
    RegisteredProject,
)


def test_audit_report_writes_json_and_markdown(
    tmp_path: Path,
) -> None:
    registered = RegisteredProject(
        name="demo",
        path=tmp_path / "demo",
    )

    report = TemplateComplianceReport(
        project_name="demo",
        project_root=str(registered.path),
        eligible=True,
        profile_reason="application Django/React",
        passed_checks=8,
        total_checks=10,
        score=80,
        findings=[
            ComplianceFinding(
                code="DOC001",
                severity="error",
                category="documentation",
                message="Document absent.",
                path="README.md",
            )
        ],
    )

    result = ProjectAuditResult(
        project=registered,
        report=report,
    )

    generator = AuditReportGenerator()
    persistent = generator.generate(
        template_path=tmp_path / "template",
        results=[result],
    )

    files = generator.write(
        report=persistent,
        output_dir=tmp_path / "reports",
    )

    assert files.latest_json.exists()
    assert files.latest_markdown.exists()
    assert files.history_json.exists()
    assert files.history_markdown.exists()

    data = json.loads(
        files.latest_json.read_text(
            encoding="utf-8"
        )
    )

    assert data["summary"]["total_projects"] == 1
    assert (
        data["summary"]["non_compliant_projects"]
        == 1
    )
    assert data["projects"][0]["name"] == "demo"

    markdown = files.latest_markdown.read_text(
        encoding="utf-8"
    )

    assert "# Rapport de conformité" in markdown
    assert "demo" in markdown
    assert "DOC001" in markdown


def test_audit_report_marks_ignored_projects(
    tmp_path: Path,
) -> None:
    registered = RegisteredProject(
        name="site",
        path=tmp_path / "site",
    )

    report = TemplateComplianceReport(
        project_name="site",
        project_root=str(registered.path),
        eligible=False,
        profile_reason="projet hors profil",
    )

    generator = AuditReportGenerator()

    persistent = generator.generate(
        template_path=tmp_path / "template",
        results=[
            ProjectAuditResult(
                project=registered,
                report=report,
            )
        ],
    )

    assert persistent.summary.ignored_projects == 1
    assert persistent.projects[0]["state"] == "ignored"
