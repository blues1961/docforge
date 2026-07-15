from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from docforge.analyzers import (
    ComplianceFinding,
    TemplateComplianceReport,
)
from docforge.audit_manager import (
    AuditManager,
    ProjectAuditResult,
)


@dataclass(slots=True)
class RemediationAction:
    order: int
    category: str
    title: str
    description: str
    commands: list[str] = field(default_factory=list)
    automatic_safe: bool = False
    owner_approval_required: bool = False


@dataclass(slots=True)
class ProjectRemediationPlan:
    project_name: str
    project_path: str
    eligible: bool
    current_score: int | None
    actions: list[RemediationAction] = field(default_factory=list)
    blocked_reason: str | None = None


@dataclass(slots=True)
class EcosystemRemediationPlan:
    template_path: str
    projects: list[ProjectRemediationPlan] = field(
        default_factory=list
    )


class RemediationPlanner:
    DETERMINISTIC_DOCUMENTS = {
        "docs/api.md",
        "docs/architecture.md",
        "docs/deployment.md",
        "docs/specification.md",
    }

    def generate(
        self,
        *,
        template_path: Path,
        results: list[ProjectAuditResult],
    ) -> EcosystemRemediationPlan:
        plans: list[ProjectRemediationPlan] = []

        for result in results:
            plans.append(
                self._project_plan(result)
            )

        return EcosystemRemediationPlan(
            template_path=str(
                template_path.expanduser().resolve()
            ),
            projects=plans,
        )

    def _project_plan(
        self,
        result: ProjectAuditResult,
    ) -> ProjectRemediationPlan:
        registered = result.project

        if result.error:
            return ProjectRemediationPlan(
                project_name=registered.name,
                project_path=str(registered.path),
                eligible=False,
                current_score=None,
                blocked_reason=result.error,
            )

        report = result.report

        if report is None:
            return ProjectRemediationPlan(
                project_name=registered.name,
                project_path=str(registered.path),
                eligible=False,
                current_score=None,
                blocked_reason="Rapport de conformité absent.",
            )

        if not report.eligible:
            return ProjectRemediationPlan(
                project_name=report.project_name,
                project_path=report.project_root,
                eligible=False,
                current_score=None,
                blocked_reason=report.profile_reason,
            )

        actions: list[RemediationAction] = []

        for finding in report.findings:
            action = self._action_for_finding(
                report,
                finding,
            )

            if action is not None:
                actions.append(action)

        actions = self._deduplicate(actions)

        for index, action in enumerate(actions, start=1):
            action.order = index

        return ProjectRemediationPlan(
            project_name=report.project_name,
            project_path=report.project_root,
            eligible=True,
            current_score=report.score,
            actions=actions,
        )

    def _action_for_finding(
        self,
        report: TemplateComplianceReport,
        finding: ComplianceFinding,
    ) -> RemediationAction | None:
        project_path = report.project_root
        path = finding.path

        if (
            finding.code == "DOC001"
            and path in self.DETERMINISTIC_DOCUMENTS
        ):
            return RemediationAction(
                order=0,
                category="documentation",
                title=f"Générer et intégrer `{path}`",
                description=(
                    "Le document peut être généré de manière "
                    "déterministe à partir du dépôt."
                ),
                commands=[
                    (
                        "docforge document "
                        f"{project_path} --refresh --clean"
                    ),
                    (
                        "docforge apply "
                        f"{project_path} {path}"
                    ),
                    f"git -C {project_path} diff -- {path}",
                ],
                automatic_safe=False,
            )

        if finding.code == "DOC001" and path:
            return RemediationAction(
                order=0,
                category="documentation",
                title=f"Créer le document `{path}`",
                description=(
                    "Le document est obligatoire, mais aucun "
                    "générateur déterministe spécialisé n’est "
                    "encore disponible."
                ),
                commands=[
                    (
                        "docforge document "
                        f"{project_path} --clean"
                    ),
                ],
                automatic_safe=False,
            )

        if finding.code == "ENV001" and path == ".env":
            return RemediationAction(
                order=0,
                category="environment",
                title="Sélectionner l’environnement de développement",
                description=(
                    "Créer le lien symbolique `.env` vers `.env.dev` "
                    "avec la commande canonique du projet."
                ),
                commands=[
                    f"make -C {project_path} dev",
                ],
                automatic_safe=True,
            )

        if finding.code == "ENV001" and path == ".env.local":
            return RemediationAction(
                order=0,
                category="environment",
                title="Récupérer les secrets locaux",
                description=(
                    "Récupérer `.env.local` depuis la production "
                    "ou utiliser la commande spécialisée du projet. "
                    "Ne jamais afficher son contenu."
                ),
                commands=[],
                automatic_safe=False,
                owner_approval_required=True,
            )

        if finding.code == "ENV002":
            return RemediationAction(
                order=0,
                category="environment",
                title="Corriger le lien `.env`",
                description=(
                    "Le lien doit pointer vers `.env.dev` ou `.env.prod`."
                ),
                commands=[
                    f"make -C {project_path} dev",
                ],
                automatic_safe=True,
            )

        if finding.code == "SCR001" and path:
            return RemediationAction(
                order=0,
                category="scripts",
                title=f"Restaurer le script canonique `{path}`",
                description=(
                    "Comparer le script avec celui d’app-template, "
                    "adapter uniquement les paramètres propres au projet "
                    "et conserver les invariants globaux."
                ),
                commands=[
                    (
                        "diff -u "
                        f"{Path.home() / 'projets/app-template' / path} "
                        f"{Path(project_path) / path}"
                    ),
                ],
                automatic_safe=False,
            )

        if finding.code == "MAKE001":
            target = finding.expected or "inconnue"

            return RemediationAction(
                order=0,
                category="makefile",
                title=f"Ajouter la cible `make {target}`",
                description=(
                    "Reprendre la cible canonique depuis app-template "
                    "et adapter uniquement APP_SLUG, APP_DEPOT ou les "
                    "paramètres explicitement propres au projet."
                ),
                commands=[
                    (
                        "diff -u "
                        f"{Path.home() / 'projets/app-template/Makefile'} "
                        f"{Path(project_path) / 'Makefile'}"
                    ),
                ],
                automatic_safe=False,
            )

        if finding.code in {"ARC001", "NET001", "CMP001"}:
            return RemediationAction(
                order=0,
                category="architecture",
                title="Corriger la configuration Docker canonique",
                description=(
                    finding.message
                    + " Comparer les fichiers Compose du projet avec "
                    "app-template sans modifier les invariants globaux."
                ),
                commands=[
                    (
                        "diff -u "
                        f"{Path.home() / 'projets/app-template/docker-compose.dev.yml'} "
                        f"{Path(project_path) / 'docker-compose.dev.yml'}"
                    ),
                    (
                        "diff -u "
                        f"{Path.home() / 'projets/app-template/docker-compose.prod.yml'} "
                        f"{Path(project_path) / 'docker-compose.prod.yml'}"
                    ),
                ],
                automatic_safe=False,
            )

        if finding.code == "SEC001":
            return RemediationAction(
                order=0,
                category="security",
                title="Corriger `.gitignore`",
                description=(
                    finding.message
                    + " Aucun secret ne doit être ajouté à Git."
                ),
                commands=[],
                automatic_safe=False,
            )

        return RemediationAction(
            order=0,
            category=finding.category,
            title=f"Examiner l’écart {finding.code}",
            description=finding.message,
            commands=[],
            automatic_safe=False,
        )

    @staticmethod
    def _deduplicate(
        actions: list[RemediationAction],
    ) -> list[RemediationAction]:
        unique: list[RemediationAction] = []
        seen: set[tuple[str, str]] = set()

        for action in actions:
            key = (
                action.category,
                action.title,
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(action)

        return unique


class RemediationMarkdownGenerator:
    def generate(
        self,
        plan: EcosystemRemediationPlan,
    ) -> str:
        lines = [
            "# Plan de mise en conformité",
            "",
            "<!--",
            "Document généré par docforge.",
            "Aucune modification n’a été appliquée automatiquement.",
            "-->",
            "",
            f"Template canonique : `{plan.template_path}`",
            "",
        ]

        for project in plan.projects:
            lines.extend(
                [
                    f"## {project.project_name}",
                    "",
                ]
            )

            if not project.eligible:
                lines.extend(
                    [
                        f"_Projet ignoré ou bloqué : "
                        f"{project.blocked_reason or 'raison inconnue'}._",
                        "",
                    ]
                )
                continue

            lines.append(
                f"Score actuel : `{project.current_score} %`"
            )
            lines.append("")

            if not project.actions:
                lines.extend(
                    [
                        "Aucune action requise.",
                        "",
                    ]
                )
                continue

            for action in project.actions:
                lines.extend(
                    [
                        f"### {action.order}. {action.title}",
                        "",
                        action.description,
                        "",
                        (
                            "- Exécution automatique sûre : "
                            f"`{'oui' if action.automatic_safe else 'non'}`"
                        ),
                        (
                            "- Approbation du propriétaire requise : "
                            f"`{'oui' if action.owner_approval_required else 'non'}`"
                        ),
                        "",
                    ]
                )

                if action.commands:
                    lines.append("Commandes proposées :")
                    lines.append("")

                    for command in action.commands:
                        lines.extend(
                            [
                                "```bash",
                                command,
                                "```",
                                "",
                            ]
                        )

        return "\n".join(lines).rstrip() + "\n"


def generate_remediation_plan(
    *,
    template_path: Path,
    output_path: Path,
    audit_manager: AuditManager | None = None,
) -> Path:
    manager = audit_manager or AuditManager()
    results = manager.audit_all(template_path)

    plan = RemediationPlanner().generate(
        template_path=template_path,
        results=results,
    )

    content = RemediationMarkdownGenerator().generate(
        plan
    )

    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output_path.write_text(
        content,
        encoding="utf-8",
    )

    return output_path
