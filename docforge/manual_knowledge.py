from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from docforge.analyzers import CliCommandFacts, CliParameterFacts
from docforge.knowledge import ProjectKnowledge
from docforge.profiles import ProjectProfile


@dataclass(frozen=True, slots=True)
class ManualFactSource:
    status: str
    sources: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(slots=True)
class ManualProject:
    name: str
    version: str | None
    description: str | None
    profile_type: str
    python_requires: str | None
    cli_entry_point: str | None
    source: ManualFactSource


@dataclass(slots=True)
class ManualInstallationStep:
    title: str
    command: str
    source: ManualFactSource


@dataclass(slots=True)
class ManualInstallation:
    summary: str
    prerequisites: list[str] = field(default_factory=list)
    steps: list[ManualInstallationStep] = field(default_factory=list)
    source: ManualFactSource = field(
        default_factory=lambda: ManualFactSource(
            status="derived"
        )
    )


@dataclass(slots=True)
class ManualCommandParameter:
    name: str
    kind: str
    required: bool
    flags: list[str] = field(default_factory=list)
    help: str | None = None
    type_annotation: str | None = None
    default: str | None = None
    example: str | None = None
    description: str | None = None
    allowed_values: list[str] = field(default_factory=list)
    origin: str | None = None
    source: str | None = None


@dataclass(slots=True)
class ManualCommand:
    name: str
    command_path: str
    invocation: str
    group: str | None
    help: str | None
    visibility: str = "public"
    documented: bool = False
    audience: str | None = None
    reference_level: str | None = None
    provenance: str | None = None
    documentation_policy: str | None = None
    exclusion_reason: str | None = None
    provenance_evidence: list[str] = field(default_factory=list)
    destructive: bool = False
    destructive_effects: list[str] = field(default_factory=list)
    environment: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    parameters: list[ManualCommandParameter] = field(
        default_factory=list
    )
    examples: list[str] = field(default_factory=list)
    source: ManualFactSource = field(
        default_factory=lambda: ManualFactSource(
            status="detected"
        )
    )


@dataclass(slots=True)
class ManualWorkflow:
    identifier: str
    title: str
    summary: str
    commands: list[str] = field(default_factory=list)
    operational_status: str = "operational"
    notes: list[str] = field(default_factory=list)
    source: ManualFactSource = field(
        default_factory=lambda: ManualFactSource(
            status="derived"
        )
    )




@dataclass(slots=True)
class ManualConflictFact:
    value: str
    sources: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ManualConflict:
    identifier: str
    category: str
    severity: str
    description: str
    facts: list[ManualConflictFact] = field(default_factory=list)
    affected_sections: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ManualKnowledgeGap:
    identifier: str
    category: str
    severity: str
    description: str
    affected_sections: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ManualConfiguration:
    user_config_root: str
    project_state_root: str
    project_config_file: str
    report_root: str
    files: list[dict[str, Any]] = field(default_factory=list)
    environment_variables: list[str] = field(
        default_factory=list
    )
    ignored_paths: list[str] = field(default_factory=list)
    source: ManualFactSource = field(
        default_factory=lambda: ManualFactSource(
            status="configured"
        )
    )


@dataclass(slots=True)
class ManualSecurity:
    protected_documents: list[str] = field(
        default_factory=list
    )
    controls: list[dict[str, Any]] = field(default_factory=list)
    risks: list[Any] = field(default_factory=list)
    validation_commands: list[str] = field(
        default_factory=list
    )
    source: ManualFactSource = field(
        default_factory=lambda: ManualFactSource(
            status="detected"
        )
    )


@dataclass(slots=True)
class ManualLimitations:
    items: list[Any] = field(default_factory=list)
    source: ManualFactSource = field(
        default_factory=lambda: ManualFactSource(
            status="derived"
        )
    )


@dataclass(slots=True)
class ManualDocumentationPolicy:
    required_documents: list[str] = field(
        default_factory=list
    )
    optional_documents: list[str] = field(
        default_factory=list
    )
    deterministic_documents: list[str] = field(
        default_factory=list
    )
    protected_documents: list[str] = field(
        default_factory=list
    )
    source: ManualFactSource = field(
        default_factory=lambda: ManualFactSource(
            status="configured"
        )
    )


@dataclass(slots=True)
class ManualSourceTraceability:
    items: dict[str, ManualFactSource] = field(
        default_factory=dict
    )


@dataclass(slots=True)
class ManualKnowledge:
    schema_version: int
    project: ManualProject
    profile: dict[str, Any]
    installation: ManualInstallation
    application: dict[str, Any] = field(default_factory=dict)
    environments: dict[str, Any] = field(default_factory=dict)
    operational_commands: dict[str, Any] = field(default_factory=dict)
    environment_variables: dict[str, Any] = field(default_factory=dict)
    service_endpoints: dict[str, Any] = field(default_factory=dict)
    django: dict[str, Any] = field(default_factory=dict)
    react: dict[str, Any] = field(default_factory=dict)
    capabilities: dict[str, Any] = field(default_factory=dict)
    missing_information: list[Any] = field(default_factory=list)
    conflicts: list[ManualConflict] = field(default_factory=list)
    commands: list[ManualCommand] = field(default_factory=list)
    workflows: list[ManualWorkflow] = field(default_factory=list)
    configuration: ManualConfiguration = field(
        default_factory=lambda: ManualConfiguration(
            user_config_root="~/.config/docforge",
            project_state_root=".docforge",
            project_config_file=".docforge.yml",
            report_root="reports",
        )
    )
    security: ManualSecurity = field(
        default_factory=ManualSecurity
    )
    limitations: ManualLimitations = field(
        default_factory=ManualLimitations
    )
    documentation_policy: ManualDocumentationPolicy = field(
        default_factory=ManualDocumentationPolicy
    )
    source_traceability: ManualSourceTraceability = field(
        default_factory=ManualSourceTraceability
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return (
            json.dumps(
                self.to_dict(),
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )


class ManualKnowledgeBuilder:
    SCHEMA_VERSION = 2

    def build(
        self,
        *,
        project_root: Path,
        knowledge: ProjectKnowledge,
        profile_instance: ProjectProfile,
    ) -> ManualKnowledge:
        entry_point = next(
            iter(knowledge.pyproject.scripts.items()),
            None,
        )
        command_lookup = {
            command.command_path: command
            for command in knowledge.cli.commands
        }
        commands = [
            self._build_command(command)
            for command in knowledge.cli.commands
        ]
        documentation_policy = (
            knowledge.profile.document_policy
        )

        return ManualKnowledge(
            schema_version=self.SCHEMA_VERSION,
            project=ManualProject(
                name=knowledge.pyproject.package_name
                or knowledge.identity.name,
                version=knowledge.pyproject.version,
                description=knowledge.pyproject.description,
                profile_type=knowledge.profile.name,
                python_requires=(
                    knowledge.pyproject.requires_python
                ),
                cli_entry_point=(
                    f"{entry_point[0]} -> {entry_point[1]}"
                    if entry_point
                    else None
                ),
                source=ManualFactSource(
                    status="detected",
                    sources=(
                        "pyproject.toml",
                        "ProjectKnowledge.pyproject",
                    ),
                ),
            ),
            profile={
                "name": knowledge.profile.name,
                "label": knowledge.profile.label,
                "description": knowledge.profile.description,
                "confidence": knowledge.profile.confidence,
                "evidence": list(knowledge.profile.evidence),
                "source": asdict(
                    ManualFactSource(
                        status="detected",
                        sources=(
                            "ProfileDetector",
                            *knowledge.profile.evidence,
                        ),
                    )
                ),
            },
            installation=self._build_installation(
                knowledge
            ),
            commands=commands,
            workflows=self._build_workflows(
                command_lookup
            ),
            configuration=ManualConfiguration(
                user_config_root=(
                    knowledge.configuration.user_config_root
                ),
                project_state_root=(
                    knowledge.configuration.project_state_root
                ),
                project_config_file=(
                    knowledge.configuration.project_config_file
                ),
                report_root=knowledge.configuration.report_root,
                files=[
                    {
                        "path": item.path,
                        "scope": item.scope,
                        "exists": item.exists,
                        "tracked_candidate": (
                            item.tracked_candidate
                        ),
                        "description": item.description,
                    }
                    for item in knowledge.configuration.files
                    if "project-assistant" not in item.path
                    and ".project-assistant" not in item.path
                ],
                environment_variables=list(
                    knowledge.configuration.environment_variables
                ),
                ignored_paths=[
                    path
                    for path in knowledge.configuration.ignored_paths
                    if "project-assistant" not in path
                    and ".project-assistant" not in path
                ],
                source=ManualFactSource(
                    status="configured",
                    sources=(
                        "ConfigurationAnalyzer",
                        ".docforge.yml",
                        ".gitignore",
                    ),
                ),
            ),
            security=ManualSecurity(
                protected_documents=list(
                    knowledge.security.protected_documents
                ),
                controls=[
                    {
                        "identifier": item.identifier,
                        "category": item.category,
                        "description": item.description,
                        "evidence": item.evidence,
                    }
                    for item in knowledge.security.controls
                ],
                risks=list(knowledge.security.risks),
                validation_commands=list(
                    knowledge.security.validation_commands
                ),
                source=ManualFactSource(
                    status="detected",
                    sources=(
                        "SecurityAnalyzer",
                        *knowledge.security.protected_documents,
                    ),
                ),
            ),
            limitations=ManualLimitations(
                items=self._build_limitations(
                    knowledge,
                    profile_instance=profile_instance,
                ),
                source=ManualFactSource(
                    status="derived",
                    sources=(
                        "ProjectKnowledge",
                        "ProfileDetector",
                    ),
                ),
            ),
            documentation_policy=ManualDocumentationPolicy(
                required_documents=list(
                    documentation_policy.required_documents
                ),
                optional_documents=list(
                    documentation_policy.optional_documents
                ),
                deterministic_documents=list(
                    documentation_policy.deterministic_documents
                ),
                protected_documents=list(
                    documentation_policy.protected_documents
                ),
                source=ManualFactSource(
                    status="configured",
                    sources=(
                        f"profile:{knowledge.profile.name}",
                    ),
                ),
            ),
            source_traceability=ManualSourceTraceability(
                items={
                    "project": ManualFactSource(
                        status="detected",
                        sources=(
                            "pyproject.toml",
                            "ProjectKnowledge.identity",
                        ),
                    ),
                    "profile": ManualFactSource(
                        status="detected",
                        sources=(
                            "ProfileDetector",
                        ),
                    ),
                    "installation": ManualFactSource(
                        status="derived",
                        sources=(
                            "pyproject.toml",
                        ),
                    ),
                    "commands": ManualFactSource(
                        status="detected",
                        sources=(
                            "CliAnalyzer",
                            "docforge/cli.py",
                        ),
                    ),
                    "workflows": ManualFactSource(
                        status="derived",
                        sources=(
                            "CliAnalyzer",
                            "ProfileDocumentPolicy",
                        ),
                    ),
                    "configuration": ManualFactSource(
                        status="configured",
                        sources=(
                            "ConfigurationAnalyzer",
                        ),
                    ),
                    "security": ManualFactSource(
                        status="detected",
                        sources=(
                            "SecurityAnalyzer",
                        ),
                    ),
                    "limitations": ManualFactSource(
                        status="derived",
                        sources=(
                            "ProjectKnowledge.findings",
                            "ProjectProfile",
                        ),
                    ),
                }
            ),
        )

    def _build_installation(
        self,
        knowledge: ProjectKnowledge,
    ) -> ManualInstallation:
        has_dev_group = (
            "dev"
            in knowledge.pyproject.optional_dependencies
        )

        steps = [
            ManualInstallationStep(
                title="Créer un environnement virtuel",
                command="python -m venv .venv",
                source=ManualFactSource(
                    status="derived",
                    sources=("pyproject.toml",),
                ),
            ),
            ManualInstallationStep(
                title="Activer l’environnement",
                command="source .venv/bin/activate",
                source=ManualFactSource(
                    status="derived",
                    sources=("README_DEV.md",),
                ),
            ),
            ManualInstallationStep(
                title="Installer le paquet localement",
                command="python -m pip install -e .",
                source=ManualFactSource(
                    status="derived",
                    sources=("pyproject.toml",),
                ),
            ),
            ManualInstallationStep(
                title="Installer les dépendances de développement",
                command='python -m pip install -e ".[dev]"',
                source=ManualFactSource(
                    status=(
                        "configured"
                        if has_dev_group
                        else "missing"
                    ),
                    sources=("pyproject.toml",),
                    notes=(
                        ()
                        if has_dev_group
                        else (
                            "Le groupe optionnel dev n’a pas été détecté.",
                        )
                    ),
                ),
            ),
            ManualInstallationStep(
                title="Vérifier l’installation CLI",
                command="docforge --help",
                source=ManualFactSource(
                    status="derived",
                    sources=("CliAnalyzer",),
                ),
            ),
            ManualInstallationStep(
                title="Exécuter les tests",
                command="pytest -q",
                source=ManualFactSource(
                    status="derived",
                    sources=("tests/",),
                ),
            ),
        ]

        prerequisites = [
            f"Python {knowledge.pyproject.requires_python or '>=3.11'}",
            "Git",
            "Un shell compatible POSIX",
        ]

        return ManualInstallation(
            summary=(
                "Installation locale à partir d’une copie du dépôt."
            ),
            prerequisites=prerequisites,
            steps=steps,
            source=ManualFactSource(
                status="derived",
                sources=("pyproject.toml", "README_DEV.md"),
            ),
        )

    def _build_command(
        self,
        command: CliCommandFacts,
    ) -> ManualCommand:
        examples = [f"docforge {command.command_path}"]

        has_clean = any(
            "--clean" in parameter.flags
            for parameter in command.parameters
        )
        has_refresh = any(
            "--refresh" in parameter.flags
            for parameter in command.parameters
        )

        if has_clean and has_refresh:
            examples.append(
                f"docforge {command.command_path} . --refresh --clean"
            )

        return ManualCommand(
            name=command.name,
            command_path=command.command_path,
            invocation=f"docforge {command.command_path}",
            group=command.group,
            help=command.help,
            parameters=[
                self._build_parameter(parameter)
                for parameter in command.parameters
            ],
            examples=examples,
            source=ManualFactSource(
                status="detected",
                sources=(command.module, command.function_name),
            ),
        )

    @staticmethod
    def _build_parameter(
        parameter: CliParameterFacts,
    ) -> ManualCommandParameter:
        return ManualCommandParameter(
            name=parameter.name,
            kind=parameter.kind,
            required=parameter.required,
            flags=list(parameter.flags),
            help=parameter.help,
            type_annotation=parameter.type_annotation,
            default=parameter.default,
        )

    def _build_workflows(
        self,
        command_lookup: dict[str, CliCommandFacts],
    ) -> list[ManualWorkflow]:
        workflows: list[ManualWorkflow] = []

        def add_workflow(
            identifier: str,
            title: str,
            summary: str,
            commands: list[str],
        ) -> None:
            workflows.append(
                ManualWorkflow(
                    identifier=identifier,
                    title=title,
                    summary=summary,
                    commands=commands,
                    source=ManualFactSource(
                        status="derived",
                        sources=tuple(commands),
                    ),
                )
            )

        add_workflow(
            "analyze-project",
            "Analyser un projet",
            "Inspecter un dépôt sans modifier ses fichiers.",
            self._commands_for(
                command_lookup,
                "analyze",
            ),
        )
        add_workflow(
            "detect-profile",
            "Détecter son profil",
            "Identifier le profil documentaire concret du dépôt.",
            self._commands_for(
                command_lookup,
                "profile",
            ),
        )
        add_workflow(
            "build-project-knowledge",
            "Construire ProjectKnowledge",
            "Produire la représentation factuelle structurée du dépôt.",
            self._commands_for(
                command_lookup,
                "knowledge",
            ),
        )
        add_workflow(
            "generate-preview",
            "Générer un aperçu documentaire",
            "Créer des aperçus déterministes sans modifier les documents réels.",
            self._commands_for(
                command_lookup,
                "document",
                "document",
                variant=". --refresh --clean",
            ),
        )
        add_workflow(
            "review-preview",
            "Réviser les aperçus",
            "Contrôler les fichiers générés avant toute application.",
            [
                "docforge document . --refresh --clean",
                "git diff -- . ':(exclude).docforge'",
            ],
        )
        add_workflow(
            "apply-validated-document",
            "Appliquer un document validé",
            "Copier explicitement un aperçu validé dans le projet.",
            [
                "docforge apply . README.md",
            ]
            if "apply" in command_lookup
            else [],
        )
        add_workflow(
            "apply-protected-document",
            "Appliquer un document protégé",
            "Appliquer un document protégé avec autorisation explicite du propriétaire.",
            [
                "docforge apply . INVARIANTS.md --owner-approved",
            ]
            if "apply" in command_lookup
            else [],
        )
        add_workflow(
            "generate-with-ollama",
            "Utiliser Ollama avec docforge generate",
            "Compléter les documents manquants via le flux LLM dédié.",
            [
                "docforge generate . --refresh --clean",
            ]
            if "generate" in command_lookup
            else [],
        )
        add_workflow(
            "manage-projects",
            "Gérer plusieurs projets",
            "Enregistrer, lister et retirer des projets du registre utilisateur.",
            [
                "docforge projects add .",
                "docforge projects list",
                "docforge projects remove demo",
            ]
            if {
                "projects add",
                "projects list",
                "projects remove",
            }.issubset(command_lookup)
            else [],
        )
        add_workflow(
            "produce-audit",
            "Produire un audit",
            "Comparer les projets enregistrés et produire un rapport de conformité.",
            [
                "docforge audit-all --show-findings",
                "docforge audit-report",
            ]
            if {
                "audit-all",
                "audit-report",
            }.issubset(command_lookup)
            else [],
        )

        return workflows

    @staticmethod
    def _commands_for(
        command_lookup: dict[str, CliCommandFacts],
        required_path: str,
        invocation_path: str | None = None,
        *,
        variant: str | None = None,
    ) -> list[str]:
        if required_path not in command_lookup:
            return []

        base = f"docforge {invocation_path or required_path}"

        if variant:
            return [f"{base} {variant}".replace("  ", " ")]

        return [base]

    @staticmethod
    def _build_limitations(
        knowledge: ProjectKnowledge,
        *,
        profile_instance: ProjectProfile,
    ) -> list[str]:
        items = [
            (
                "Le manuel préparé ne contient que des faits présents "
                "dans ProjectKnowledge et dans les politiques du profil."
            ),
            (
                "Toute information absente ou incertaine doit être "
                "signalée comme manquante dans la rédaction finale."
            ),
            (
                "Les workflows proposés restent limités aux commandes "
                "détectées dans la CLI."
            ),
        ]

        if knowledge.profile.name == "generic":
            items.append(
                "Le profil generic est un repli et peut manquer de "
                "détails spécialisés."
            )

        if not knowledge.cli.commands:
            items.append(
                "Aucune commande CLI exploitable n’a été détectée."
            )

        if not knowledge.security.protected_documents:
            items.append(
                "Aucun document protégé n’a été déclaré par le profil."
            )

        findings = [
            finding.get("code")
            for finding in knowledge.findings
            if isinstance(finding, dict)
            and finding.get("code")
        ]
        if findings:
            items.append(
                "Constats encore présents dans le projet : "
                + ", ".join(sorted(findings))
                + "."
            )

        if profile_instance.name == "python-cli":
            items.append(
                "Certains constats d’environnement non pertinents pour ce profil sont exclus de la projection manuel."
            )

        return items
