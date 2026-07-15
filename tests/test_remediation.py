from pathlib import Path

from project_assistant.analyzers import (
    ComplianceFinding,
    TemplateComplianceReport,
)
from project_assistant.audit_manager import (
    ProjectAuditResult,
)
from project_assistant.project_registry import (
    RegisteredProject,
)
from project_assistant.remediation import (
    RemediationMarkdownGenerator,
    RemediationPlanner,
)


def test_remediation_plan_for_missing_specification(
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
        profile_reason="django-react",
        score=96,
        findings=[
            ComplianceFinding(
                code="DOC001",
                severity="error",
                category="documentation",
                message="Document absent.",
                path="docs/specification.md",
            )
        ],
    )

    plan = RemediationPlanner().generate(
        template_path=tmp_path / "template",
        results=[
            ProjectAuditResult(
                project=registered,
                report=report,
            )
        ],
    )

    project = plan.projects[0]

    assert len(project.actions) == 1

    action = project.actions[0]

    assert "docs/specification.md" in action.title
    assert any(
        "docforge document"
        in command
        for command in action.commands
    )
    assert any(
        "docforge apply"
        in command
        for command in action.commands
    )


def test_secret_remediation_requires_owner_approval(
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
        profile_reason="django-react",
        score=98,
        findings=[
            ComplianceFinding(
                code="ENV001",
                severity="warning",
                category="environment",
                message=".env.local absent.",
                path=".env.local",
            )
        ],
    )

    plan = RemediationPlanner().generate(
        template_path=tmp_path / "template",
        results=[
            ProjectAuditResult(
                project=registered,
                report=report,
            )
        ],
    )

    action = plan.projects[0].actions[0]

    assert action.owner_approval_required is True
    assert action.automatic_safe is False


def test_remediation_markdown_contains_commands(
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
        profile_reason="django-react",
        score=90,
        findings=[
            ComplianceFinding(
                code="ENV002",
                severity="error",
                category="environment",
                message="Lien .env invalide.",
                path=".env",
            )
        ],
    )

    plan = RemediationPlanner().generate(
        template_path=tmp_path / "template",
        results=[
            ProjectAuditResult(
                project=registered,
                report=report,
            )
        ],
    )

    content = RemediationMarkdownGenerator().generate(
        plan
    )

    assert "# Plan de mise en conformité" in content
    assert "make -C" in content
    assert "demo" in content
