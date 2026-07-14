from __future__ import annotations

from dataclasses import dataclass

from project_assistant.analyzers import (
    TemplateAnalyzer,
    TemplateComplianceAnalyzer,
    TemplateComplianceReport,
)
from project_assistant.project_registry import (
    ProjectRegistry,
    RegisteredProject,
)


@dataclass(slots=True)
class ProjectAuditResult:
    project: RegisteredProject
    report: TemplateComplianceReport | None = None
    error: str | None = None


class AuditManager:
    def __init__(
        self,
        registry: ProjectRegistry | None = None,
    ) -> None:
        self.registry = registry or ProjectRegistry()

    def audit_all(
        self,
        template_path,
    ) -> list[ProjectAuditResult]:
        template = TemplateAnalyzer().analyze(template_path)
        analyzer = TemplateComplianceAnalyzer()

        results: list[ProjectAuditResult] = []

        for registered in self.registry.load():
            if not registered.enabled:
                continue

            if registered.path.resolve() == template_path.resolve():
                continue

            try:
                report = analyzer.analyze(
                    registered.path,
                    template,
                )

                results.append(
                    ProjectAuditResult(
                        project=registered,
                        report=report,
                    )
                )
            except Exception as error:
                results.append(
                    ProjectAuditResult(
                        project=registered,
                        error=str(error),
                    )
                )

        return results
