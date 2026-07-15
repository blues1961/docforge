from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ProjectAuditChange:
    name: str
    change_type: str
    previous_state: str | None
    current_state: str | None
    previous_score: int | None
    current_score: int | None
    score_delta: int | None
    previous_errors: int | None
    current_errors: int | None
    previous_warnings: int | None
    current_warnings: int | None


@dataclass(slots=True)
class AuditDiffReport:
    previous_report: str
    current_report: str
    improved: list[ProjectAuditChange] = field(default_factory=list)
    regressed: list[ProjectAuditChange] = field(default_factory=list)
    unchanged: list[ProjectAuditChange] = field(default_factory=list)
    added: list[ProjectAuditChange] = field(default_factory=list)
    removed: list[ProjectAuditChange] = field(default_factory=list)


class AuditDiffError(RuntimeError):
    """Erreur de comparaison de rapports d'audit."""


class AuditDiffAnalyzer:
    STATE_RANK = {
        "error": 0,
        "non-compliant": 1,
        "warning": 2,
        "compliant": 3,
        "ignored": 4,
    }

    def compare(
        self,
        previous_path: Path,
        current_path: Path,
    ) -> AuditDiffReport:
        previous_path = previous_path.expanduser().resolve()
        current_path = current_path.expanduser().resolve()

        previous = self._load_report(previous_path)
        current = self._load_report(current_path)

        previous_projects = self._projects_by_name(previous)
        current_projects = self._projects_by_name(current)

        report = AuditDiffReport(
            previous_report=str(previous_path),
            current_report=str(current_path),
        )

        all_names = sorted(
            set(previous_projects) | set(current_projects),
            key=str.casefold,
        )

        for name in all_names:
            old = previous_projects.get(name)
            new = current_projects.get(name)

            if old is None and new is not None:
                report.added.append(
                    self._build_change(
                        name=name,
                        previous=None,
                        current=new,
                        change_type="added",
                    )
                )
                continue

            if old is not None and new is None:
                report.removed.append(
                    self._build_change(
                        name=name,
                        previous=old,
                        current=None,
                        change_type="removed",
                    )
                )
                continue

            if old is None or new is None:
                continue

            change_type = self._classify_change(old, new)

            change = self._build_change(
                name=name,
                previous=old,
                current=new,
                change_type=change_type,
            )

            if change_type == "improved":
                report.improved.append(change)
            elif change_type == "regressed":
                report.regressed.append(change)
            else:
                report.unchanged.append(change)

        return report

    def find_previous_report(
        self,
        *,
        reports_directory: Path,
        current_path: Path | None = None,
    ) -> Path:
        reports_directory = reports_directory.expanduser().resolve()
        history_directory = reports_directory / "history"

        if not history_directory.is_dir():
            raise AuditDiffError(
                f"Répertoire d'historique absent : {history_directory}"
            )

        candidates = sorted(
            history_directory.glob("audit-*.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        if current_path is not None:
            current_path = current_path.expanduser().resolve()
            candidates = [
                path
                for path in candidates
                if path.resolve() != current_path
            ]

        if not candidates:
            raise AuditDiffError(
                "Aucun rapport historique JSON n'est disponible."
            )

        return candidates[0]

    @classmethod
    def _classify_change(
        cls,
        previous: dict[str, Any],
        current: dict[str, Any],
    ) -> str:
        previous_state = str(previous.get("state", "error"))
        current_state = str(current.get("state", "error"))

        previous_rank = cls.STATE_RANK.get(previous_state, 0)
        current_rank = cls.STATE_RANK.get(current_state, 0)

        if current_rank > previous_rank:
            return "improved"

        if current_rank < previous_rank:
            return "regressed"

        previous_score = cls._optional_int(
            previous.get("score")
        )
        current_score = cls._optional_int(
            current.get("score")
        )

        if (
            previous_score is not None
            and current_score is not None
        ):
            if current_score > previous_score:
                return "improved"

            if current_score < previous_score:
                return "regressed"

        previous_errors = cls._optional_int(
            previous.get("error_count")
        ) or 0
        current_errors = cls._optional_int(
            current.get("error_count")
        ) or 0

        if current_errors < previous_errors:
            return "improved"

        if current_errors > previous_errors:
            return "regressed"

        previous_warnings = cls._optional_int(
            previous.get("warning_count")
        ) or 0
        current_warnings = cls._optional_int(
            current.get("warning_count")
        ) or 0

        if current_warnings < previous_warnings:
            return "improved"

        if current_warnings > previous_warnings:
            return "regressed"

        return "unchanged"

    @classmethod
    def _build_change(
        cls,
        *,
        name: str,
        previous: dict[str, Any] | None,
        current: dict[str, Any] | None,
        change_type: str,
    ) -> ProjectAuditChange:
        previous_score = cls._optional_int(
            previous.get("score")
            if previous is not None
            else None
        )
        current_score = cls._optional_int(
            current.get("score")
            if current is not None
            else None
        )

        score_delta = (
            current_score - previous_score
            if (
                previous_score is not None
                and current_score is not None
            )
            else None
        )

        return ProjectAuditChange(
            name=name,
            change_type=change_type,
            previous_state=(
                str(previous.get("state"))
                if previous is not None
                else None
            ),
            current_state=(
                str(current.get("state"))
                if current is not None
                else None
            ),
            previous_score=previous_score,
            current_score=current_score,
            score_delta=score_delta,
            previous_errors=cls._optional_int(
                previous.get("error_count")
                if previous is not None
                else None
            ),
            current_errors=cls._optional_int(
                current.get("error_count")
                if current is not None
                else None
            ),
            previous_warnings=cls._optional_int(
                previous.get("warning_count")
                if previous is not None
                else None
            ),
            current_warnings=cls._optional_int(
                current.get("warning_count")
                if current is not None
                else None
            ),
        )

    @staticmethod
    def _load_report(path: Path) -> dict[str, Any]:
        if not path.is_file():
            raise FileNotFoundError(
                f"Rapport introuvable : {path}"
            )

        try:
            data = json.loads(
                path.read_text(encoding="utf-8")
            )
        except json.JSONDecodeError as error:
            raise AuditDiffError(
                f"Rapport JSON invalide : {path}"
            ) from error

        if not isinstance(data, dict):
            raise AuditDiffError(
                f"Structure de rapport invalide : {path}"
            )

        if not isinstance(data.get("projects"), list):
            raise AuditDiffError(
                f"Liste de projets absente : {path}"
            )

        return data

    @staticmethod
    def _projects_by_name(
        report: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        projects: dict[str, dict[str, Any]] = {}

        for item in report["projects"]:
            if not isinstance(item, dict):
                continue

            name = item.get("name")

            if not isinstance(name, str) or not name:
                continue

            projects[name] = item

        return projects

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        if value is None:
            return None

        if isinstance(value, bool):
            return int(value)

        if isinstance(value, int):
            return value

        try:
            return int(value)
        except (TypeError, ValueError):
            return None


class AuditDiffMarkdownGenerator:
    def generate(
        self,
        report: AuditDiffReport,
    ) -> str:
        lines = [
            "# Évolution de la conformité",
            "",
            "<!--",
            "Document généré automatiquement par docforge.",
            "-->",
            "",
            f"- Rapport précédent : `{report.previous_report}`",
            f"- Rapport courant : `{report.current_report}`",
            "",
            "## Résumé",
            "",
            "| Évolution | Nombre |",
            "|---|---:|",
            f"| Amélioré | {len(report.improved)} |",
            f"| Dégradé | {len(report.regressed)} |",
            f"| Inchangé | {len(report.unchanged)} |",
            f"| Nouveau | {len(report.added)} |",
            f"| Retiré | {len(report.removed)} |",
            "",
        ]

        self._append_section(
            lines,
            "Projets améliorés",
            report.improved,
        )
        self._append_section(
            lines,
            "Régressions",
            report.regressed,
        )
        self._append_section(
            lines,
            "Nouveaux projets",
            report.added,
        )
        self._append_section(
            lines,
            "Projets retirés",
            report.removed,
        )
        self._append_section(
            lines,
            "Projets inchangés",
            report.unchanged,
        )

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _append_section(
        lines: list[str],
        title: str,
        changes: list[ProjectAuditChange],
    ) -> None:
        lines.extend(
            [
                f"## {title}",
                "",
            ]
        )

        if not changes:
            lines.extend(
                [
                    "_Aucun projet._",
                    "",
                ]
            )
            return

        lines.extend(
            [
                "| Projet | État précédent | État courant | Score précédent | Score courant | Écart |",
                "|---|---|---|---:|---:|---:|",
            ]
        )

        for change in changes:
            delta = (
                f"{change.score_delta:+d}"
                if change.score_delta is not None
                else "—"
            )

            lines.append(
                "| "
                + " | ".join(
                    [
                        change.name,
                        change.previous_state or "—",
                        change.current_state or "—",
                        (
                            str(change.previous_score)
                            if change.previous_score is not None
                            else "—"
                        ),
                        (
                            str(change.current_score)
                            if change.current_score is not None
                            else "—"
                        ),
                        delta,
                    ]
                )
                + " |"
            )

        lines.append("")
