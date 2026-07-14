from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from project_assistant.audit_manager import (
    AuditManager,
    ProjectAuditResult,
)


@dataclass(slots=True)
class AuditReportSummary:
    generated_at: str
    template_path: str
    total_projects: int
    eligible_projects: int
    compliant_projects: int
    warning_projects: int
    non_compliant_projects: int
    ignored_projects: int
    failed_projects: int
    average_score: int


@dataclass(slots=True)
class PersistentAuditReport:
    summary: AuditReportSummary
    projects: list[dict[str, object]] = field(
        default_factory=list
    )


@dataclass(slots=True)
class AuditReportFiles:
    latest_json: Path
    latest_markdown: Path
    history_json: Path
    history_markdown: Path


class AuditReportGenerator:
    def generate(
        self,
        *,
        template_path: Path,
        results: list[ProjectAuditResult],
    ) -> PersistentAuditReport:
        generated_at = datetime.now(
            timezone.utc
        ).isoformat()

        project_records: list[dict[str, object]] = []
        eligible_scores: list[int] = []

        compliant = 0
        warnings = 0
        non_compliant = 0
        ignored = 0
        failed = 0
        eligible = 0

        for result in results:
            if result.error:
                failed += 1

                project_records.append(
                    {
                        "name": result.project.name,
                        "path": str(result.project.path),
                        "state": "error",
                        "eligible": False,
                        "score": None,
                        "error_count": 0,
                        "warning_count": 0,
                        "reason": result.error,
                        "findings": [],
                    }
                )
                continue

            report = result.report

            if report is None:
                failed += 1
                continue

            if not report.eligible:
                ignored += 1

                project_records.append(
                    {
                        "name": report.project_name,
                        "path": report.project_root,
                        "state": "ignored",
                        "eligible": False,
                        "score": None,
                        "error_count": 0,
                        "warning_count": 0,
                        "reason": report.profile_reason,
                        "findings": [],
                    }
                )
                continue

            eligible += 1
            eligible_scores.append(report.score)

            error_count = sum(
                1
                for finding in report.findings
                if finding.severity == "error"
            )
            warning_count = sum(
                1
                for finding in report.findings
                if finding.severity == "warning"
            )

            if error_count:
                state = "non-compliant"
                non_compliant += 1
            elif warning_count:
                state = "warning"
                warnings += 1
            else:
                state = "compliant"
                compliant += 1

            project_records.append(
                {
                    "name": report.project_name,
                    "path": report.project_root,
                    "state": state,
                    "eligible": True,
                    "score": report.score,
                    "passed_checks": report.passed_checks,
                    "total_checks": report.total_checks,
                    "error_count": error_count,
                    "warning_count": warning_count,
                    "reason": report.profile_reason,
                    "findings": [
                        asdict(finding)
                        for finding in report.findings
                    ],
                }
            )

        average_score = (
            round(
                sum(eligible_scores)
                / len(eligible_scores)
            )
            if eligible_scores
            else 0
        )

        summary = AuditReportSummary(
            generated_at=generated_at,
            template_path=str(
                template_path.expanduser().resolve()
            ),
            total_projects=len(results),
            eligible_projects=eligible,
            compliant_projects=compliant,
            warning_projects=warnings,
            non_compliant_projects=non_compliant,
            ignored_projects=ignored,
            failed_projects=failed,
            average_score=average_score,
        )

        return PersistentAuditReport(
            summary=summary,
            projects=project_records,
        )

    def write(
        self,
        *,
        report: PersistentAuditReport,
        output_dir: Path,
    ) -> AuditReportFiles:
        output_dir = output_dir.expanduser().resolve()
        history_dir = output_dir / "history"

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
        history_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = self._safe_timestamp(
            report.summary.generated_at
        )

        latest_json = output_dir / "audit-latest.json"
        latest_markdown = output_dir / "audit-latest.md"
        history_json = (
            history_dir
            / f"audit-{timestamp}.json"
        )
        history_markdown = (
            history_dir
            / f"audit-{timestamp}.md"
        )

        json_content = (
            json.dumps(
                asdict(report),
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )
        markdown_content = self.to_markdown(report)

        for path in (
            latest_json,
            history_json,
        ):
            path.write_text(
                json_content,
                encoding="utf-8",
            )

        for path in (
            latest_markdown,
            history_markdown,
        ):
            path.write_text(
                markdown_content,
                encoding="utf-8",
            )

        return AuditReportFiles(
            latest_json=latest_json,
            latest_markdown=latest_markdown,
            history_json=history_json,
            history_markdown=history_markdown,
        )

    def to_markdown(
        self,
        report: PersistentAuditReport,
    ) -> str:
        summary = report.summary

        lines = [
            "# Rapport de conformité des applications auto-hébergées",
            "",
            "<!--",
            "Document généré automatiquement par project-assistant.",
            "Ne pas modifier manuellement.",
            "-->",
            "",
            f"- Généré le : `{summary.generated_at}`",
            f"- Template canonique : `{summary.template_path}`",
            f"- Projets analysés : `{summary.total_projects}`",
            f"- Applications admissibles : `{summary.eligible_projects}`",
            f"- Score moyen : `{summary.average_score} %`",
            "",
            "## Résumé",
            "",
            "| État | Nombre |",
            "|---|---:|",
            f"| Conforme | {summary.compliant_projects} |",
            f"| À vérifier | {summary.warning_projects} |",
            f"| Non conforme | {summary.non_compliant_projects} |",
            f"| Ignoré | {summary.ignored_projects} |",
            f"| Erreur d’analyse | {summary.failed_projects} |",
            "",
            "## Projets",
            "",
            "| Projet | État | Score | Erreurs | Avertissements |",
            "|---|---|---:|---:|---:|",
        ]

        for project in report.projects:
            score = (
                f"{project['score']} %"
                if project.get("score") is not None
                else "—"
            )

            lines.append(
                "| "
                + " | ".join(
                    [
                        str(project["name"]),
                        self._state_label(
                            str(project["state"])
                        ),
                        score,
                        str(project.get("error_count", 0)),
                        str(
                            project.get(
                                "warning_count",
                                0,
                            )
                        ),
                    ]
                )
                + " |"
            )

        for project in report.projects:
            findings = project.get("findings", [])

            if not findings:
                continue

            lines.extend(
                [
                    "",
                    f"## {project['name']}",
                    "",
                    "| Sévérité | Code | Catégorie | Message | Fichier |",
                    "|---|---|---|---|---|",
                ]
            )

            for finding in findings:
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            str(finding["severity"]),
                            str(finding["code"]),
                            str(finding["category"]),
                            self._escape_table(
                                str(finding["message"])
                            ),
                            str(
                                finding.get("path")
                                or "—"
                            ),
                        ]
                    )
                    + " |"
                )

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _safe_timestamp(value: str) -> str:
        return (
            value.replace(":", "-")
            .replace("+", "_")
        )

    @staticmethod
    def _state_label(state: str) -> str:
        labels = {
            "compliant": "conforme",
            "warning": "à vérifier",
            "non-compliant": "non conforme",
            "ignored": "ignoré",
            "error": "erreur",
        }

        return labels.get(state, state)

    @staticmethod
    def _escape_table(value: str) -> str:
        return (
            value.replace("|", "\\|")
            .replace("\n", " ")
        )


def generate_audit_report(
    *,
    template_path: Path,
    output_dir: Path,
    audit_manager: AuditManager | None = None,
) -> AuditReportFiles:
    manager = audit_manager or AuditManager()

    results = manager.audit_all(template_path)

    generator = AuditReportGenerator()
    report = generator.generate(
        template_path=template_path,
        results=results,
    )

    return generator.write(
        report=report,
        output_dir=output_dir,
    )
