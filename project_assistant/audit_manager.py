from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from project_assistant.analyzers import (
    TemplateAnalyzer,
    TemplateComplianceAnalyzer,
    TemplateComplianceReport,
)
from project_assistant.invariant_integrity import (
    InvariantIntegrityManager,
    InvariantIntegrityReport,
)
from project_assistant.project_registry import (
    ProjectRegistry,
    RegisteredProject,
)


class InvariantIntegrityError(RuntimeError):
    def __init__(
        self,
        report: InvariantIntegrityReport,
    ) -> None:
        self.report = report

        if not report.baseline_exists:
            message = (
                "Aucune référence approuvée des invariants "
                "n'est disponible."
            )
        else:
            changed_files = ", ".join(
                drift.path
                for drift in report.drifts
            )
            message = (
                "Les invariants protégés ont dérivé : "
                f"{changed_files}."
            )

        super().__init__(message)


@dataclass(slots=True)
class ProjectAuditResult:
    project: RegisteredProject
    report: TemplateComplianceReport | None = None
    error: str | None = None


class AuditManager:
    def __init__(
        self,
        registry: ProjectRegistry | None = None,
        integrity_manager: InvariantIntegrityManager | None = None,
    ) -> None:
        self.registry = registry or ProjectRegistry()
        self.integrity_manager = (
            integrity_manager
            or InvariantIntegrityManager()
        )

    def verify_template_integrity(
        self,
        template_path: Path,
    ) -> InvariantIntegrityReport:
        report = self.integrity_manager.verify(
            template_path
        )

        if not report.valid:
            raise InvariantIntegrityError(report)

        return report

    def audit_all(
        self,
        template_path: Path,
    ) -> list[ProjectAuditResult]:
        template_path = template_path.expanduser().resolve()

        self.verify_template_integrity(template_path)

        template = TemplateAnalyzer().analyze(
            template_path
        )
        analyzer = TemplateComplianceAnalyzer()

        results: list[ProjectAuditResult] = []

        for registered in self.registry.load():
            if not registered.enabled:
                continue

            if (
                registered.path.expanduser().resolve()
                == template_path
            ):
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
