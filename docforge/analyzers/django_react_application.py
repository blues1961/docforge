from __future__ import annotations

import ast
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from docforge.analyzer_registry import AnalysisContext
from docforge.analyzers.api import ApiFacts
from docforge.analyzers.architecture import ArchitectureFacts
from docforge.analyzers.deployment import DeploymentFacts
from docforge.models import Project


PLACEHOLDER_PATTERN = re.compile(
    r"\$\{([A-Za-z_][A-Za-z0-9_]*)[^}]*\}"
)

SENSITIVE_NAME_PATTERN = re.compile(
    r"(PASSWORD|SECRET|TOKEN|KEY)",
    re.IGNORECASE,
)


@dataclass(slots=True)
class ApplicationOverviewFacts:
    name: str | None = None
    category: str | None = None
    backend_framework: str | None = None
    frontend_framework: str | None = None
    source_paths: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TemplatePlaceholderFacts:
    name: str
    kind: str
    description: str | None = None
    required: bool = True
    files: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TemplateWorkflowFacts:
    identifier: str
    audience: str
    title: str
    commands: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    preconditions: list[str] = field(default_factory=list)
    expected_results: list[str] = field(default_factory=list)
    personalization_points: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TemplateStateFacts:
    project_kind: str | None = None
    template_id: str | None = None
    origin_template_id: str | None = None
    template_version: str | None = None
    manifest_source: str | None = None
    base_profile: str | None = None


@dataclass(slots=True)
class TemplateMaterializationFacts:
    supported: bool = False
    entrypoint: str | None = None
    activation_command: str | None = None
    activation_variable_name: str | None = None
    activation_variable_value: str | None = None
    git_detach_variable_name: str | None = None
    git_detach_variable_value: str | None = None
    explicit_git_detach_only: bool = False
    source_repository_protected: bool = False
    allow_source_name_override: bool = False
    skip_startup_variable_name: str | None = None
    skip_startup_variable_value: str | None = None
    skip_startup_audience: str | None = None
    skip_startup_normal_workflow: bool = True
    maintenance_command: str | None = None
    placeholders_replaced: list[str] = field(default_factory=list)
    source_metadata_file: str | None = None
    generated_metadata_file: str | None = None
    metadata_script: str | None = None
    creates_independent_git_repository: bool = False
    generated_files: list[str] = field(default_factory=list)
    removed_files: list[str] = field(default_factory=list)
    validation_commands: list[str] = field(default_factory=list)
    protections: list[str] = field(default_factory=list)
    expected_results: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ProjectTemplateFacts:
    detected: bool = False
    project_kind: str | None = None
    template_id: str | None = None
    origin_template_id: str | None = None
    template_version: str | None = None
    origin_template_version: str | None = None
    base_profile: str | None = None
    manifest_source: str | None = None
    manifest_fallback_used: bool = False
    manifest_declared_targets: list[str] = field(default_factory=list)
    manifest_verified_targets: list[str] = field(default_factory=list)
    manifest_missing_targets: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    placeholders: list[TemplatePlaceholderFacts] = field(default_factory=list)
    current_state: TemplateStateFacts | None = None
    target_state: TemplateStateFacts | None = None
    materialization: TemplateMaterializationFacts | None = None
    creator_workflows: list[TemplateWorkflowFacts] = field(default_factory=list)
    maintainer_workflows: list[TemplateWorkflowFacts] = field(default_factory=list)
    missing_steps: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    source_paths: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ComposeServiceFacts:
    name: str
    environment: str
    compose_file: str
    role: str | None = None
    image: str | None = None
    build_context: str | None = None
    command: str | None = None
    ports: list[str] = field(default_factory=list)
    exposed_ports: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    volumes: list[str] = field(default_factory=list)
    networks: list[str] = field(default_factory=list)
    env_files: list[str] = field(default_factory=list)
    env_variables: list[str] = field(default_factory=list)
    healthchecks: list[str] = field(default_factory=list)
    traefik_labels: list[str] = field(default_factory=list)
    detected_hosts: list[str] = field(default_factory=list)
    source: str = ""


@dataclass(slots=True)
class EnvironmentFacts:
    name: str
    compose_file: str
    env_files: list[str] = field(default_factory=list)
    services: list[ComposeServiceFacts] = field(
        default_factory=list
    )
    urls: list[str] = field(default_factory=list)
    available_commands: list[str] = field(
        default_factory=list
    )
    source_paths: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ProjectEnvironmentsFacts:
    items: list[EnvironmentFacts] = field(default_factory=list)


@dataclass(slots=True)
class OperationalCommandParameterFacts:
    name: str
    required: bool
    example: str | None = None
    description: str | None = None
    origin: str = "user-documented"
    source: str = "Makefile"


@dataclass(slots=True)
class OperationalCommandFacts:
    name: str
    category: str
    command: str
    source: str
    target: str | None = None
    body: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    environments: list[str] = field(default_factory=list)
    parameters: list["OperationalCommandParameterFacts"] = field(
        default_factory=list
    )
    help_text: str | None = None
    phony: bool = False
    documented: bool = False
    visibility: str = "internal"
    provenance: str = "unknown"
    documentation_policy: str = "exclude"
    exclusion_reason: str | None = None
    provenance_evidence: list[str] = field(default_factory=list)
    manifest_source: str | None = None
    manifest_destructive: bool | None = None
    manifest_destructive_effects: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MakeTargetDeclarationFacts:
    name: str
    documentation_policy: str
    audience: str | None = None
    reference_level: str | None = None
    source: str = "docforge.make-targets.json"


@dataclass(slots=True)
class ScriptAnalysisFacts:
    name: str
    path: str
    source: str
    validations: list[str] = field(default_factory=list)
    failure_conditions: list[str] = field(default_factory=list)
    creates_files: list[str] = field(default_factory=list)
    copies_files: list[str] = field(default_factory=list)
    symlinks: list[str] = field(default_factory=list)
    generated_secrets: list[str] = field(default_factory=list)
    compose_commands: list[str] = field(default_factory=list)
    django_commands: list[str] = field(default_factory=list)
    shell_commands: list[str] = field(default_factory=list)
    environment_targets: list[str] = field(default_factory=list)
    database_engine: str | None = None
    backup_destination: str | None = None
    backup_format: str | None = None
    compression: str | None = None
    auto_select_latest: bool = False
    confirmation_required: bool = False
    destructive_actions: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    metadata_actions: list[str] = field(default_factory=list)
    placeholders_replaced: list[str] = field(default_factory=list)


@dataclass(slots=True)
class OperationalCommandsFacts:
    commands: list[OperationalCommandFacts] = field(
        default_factory=list
    )
    scripts: list[ScriptAnalysisFacts] = field(
        default_factory=list
    )


@dataclass(slots=True)
class EnvironmentVariableValueFacts:
    environment: str
    value: str | None
    source: str
    comment: str | None = None


@dataclass(slots=True)
class EnvironmentVariableFacts:
    name: str
    scope: str
    environments: list[str] = field(default_factory=list)
    required: bool | None = None
    required_by_environment: dict[str, bool] = field(default_factory=dict)
    sensitive: bool = False
    default_value: str | None = None
    description: str | None = None
    comment: str | None = None
    values: list[EnvironmentVariableValueFacts] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EnvironmentVariablesFacts:
    variables: list[EnvironmentVariableFacts] = field(
        default_factory=list
    )


@dataclass(slots=True)
class ServiceEndpointFacts:
    environment: str
    service: str
    url: str
    source: str
    validity: str = "valid"
    resolution_status: str = "resolved"
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ServiceEndpointsFacts:
    endpoints: list[ServiceEndpointFacts] = field(
        default_factory=list
    )


@dataclass(slots=True)
class DjangoModelFacts:
    name: str
    fields: list[str] = field(default_factory=list)
    source: str = ""


@dataclass(slots=True)
class DjangoModelFieldChoiceFacts:
    value: str
    label: str | None = None


@dataclass(slots=True)
class DjangoModelFieldFacts:
    name: str
    field_type: str
    required: bool
    nullable: bool
    blank: bool
    default: str | None = None
    choices: list[DjangoModelFieldChoiceFacts] = field(
        default_factory=list
    )
    relation: str | None = None
    unique: bool = False
    on_delete: str | None = None
    help_text: str | None = None
    source: str = ""


@dataclass(slots=True)
class DjangoModelSchemaFacts:
    name: str
    fields: list[DjangoModelFieldFacts] = field(
        default_factory=list
    )
    source: str = ""


@dataclass(slots=True)
class DatabaseEngineFacts:
    engine: str
    context: str
    source: str


@dataclass(slots=True)
class DjangoRouteFacts:
    relative_path: str
    mount_path: str | None
    full_path: str | None
    route_type: str
    resolution_status: str
    name: str | None = None
    view: str | None = None
    methods: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DjangoEndpointFacts:
    path: str | None
    relative_path: str
    mount_path: str | None
    resolution_status: str
    methods: list[str] = field(default_factory=list)
    view: str | None = None
    permissions: list[str] = field(default_factory=list)
    authentication: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    route_parameters: list[str] = field(default_factory=list)
    ownership_controls: list[str] = field(default_factory=list)
    data_controls: list[str] = field(default_factory=list)
    custom_authentication: bool = False
    sources: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DjangoFacts:
    project_module: str | None = None
    settings_module: str | None = None
    urlconf_module: str | None = None
    settings_files: list[str] = field(default_factory=list)
    installed_apps: list[str] = field(default_factory=list)
    local_apps: list[str] = field(default_factory=list)
    models: list[DjangoModelFacts] = field(default_factory=list)
    model_schemas: list[DjangoModelSchemaFacts] = field(
        default_factory=list
    )
    routes: list[str] = field(default_factory=list)
    resolved_routes: list[DjangoRouteFacts] = field(
        default_factory=list
    )
    endpoints: list[DjangoEndpointFacts] = field(
        default_factory=list
    )
    routers: list[str] = field(default_factory=list)
    auth_mechanisms: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    admin_enabled: bool = False
    migration_commands: list[str] = field(default_factory=list)
    create_admin_commands: list[str] = field(
        default_factory=list
    )
    database_engine: str | None = None
    database_engines: list[DatabaseEngineFacts] = field(
        default_factory=list
    )
    database_configuration: list[str] = field(
        default_factory=list
    )
    source_paths: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ReactCryptoFacts:
    detected: bool = False
    algorithms: list[str] = field(default_factory=list)
    key_derivation: str | None = None
    key_derivation_hash: str | None = None
    key_derivation_iterations: int | None = None
    key_derivation_salt_template: str | None = None
    key_length_bits: int | None = None
    nonce_bytes: int | None = None
    format_version: str | None = None
    payload_fields: list[str] = field(default_factory=list)
    cleartext_fields: list[str] = field(default_factory=list)
    key_material_storage: str | None = None
    recovery_supported: bool | None = None
    lock_behavior: str | None = None
    unlock_behavior: str | None = None
    source_paths: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ReactUserFeatureFacts:
    label: str
    status: str
    component: str | None = None
    routes: list[str] = field(default_factory=list)
    api_calls: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    confidence: str | None = None


@dataclass(slots=True)
class ReactFacts:
    entry_point: str | None = None
    routes: list[str] = field(default_factory=list)
    pages: list[str] = field(default_factory=list)
    navigation_items: list[str] = field(
        default_factory=list
    )
    forms: list[str] = field(default_factory=list)
    user_features: list[ReactUserFeatureFacts] = field(default_factory=list)
    api_calls: list[str] = field(default_factory=list)
    environment_variables: list[str] = field(
        default_factory=list
    )
    auth_mechanisms: list[str] = field(
        default_factory=list
    )
    scripts: dict[str, str] = field(default_factory=dict)
    dev_command: str | None = None
    build_command: str | None = None
    crypto: ReactCryptoFacts = field(
        default_factory=ReactCryptoFacts
    )
    source_paths: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CapabilityFacts:
    identifier: str | None = None
    label: str = ""
    status: str = "unresolved"
    description: str | None = None
    audience: str | None = None
    evidence: list[str] = field(default_factory=list)
    component: str | None = None
    endpoint: str | None = None
    permission_condition: str | None = None
    confidence: str | None = None


@dataclass(slots=True)
class CapabilitiesFacts:
    capabilities: list[CapabilityFacts] = field(
        default_factory=list
    )


@dataclass(slots=True)
class DjangoReactApplicationFacts:
    application: ApplicationOverviewFacts = field(
        default_factory=ApplicationOverviewFacts
    )
    environments: ProjectEnvironmentsFacts = field(
        default_factory=ProjectEnvironmentsFacts
    )
    operational_commands: OperationalCommandsFacts = field(
        default_factory=OperationalCommandsFacts
    )
    environment_variables: EnvironmentVariablesFacts = field(
        default_factory=EnvironmentVariablesFacts
    )
    service_endpoints: ServiceEndpointsFacts = field(
        default_factory=ServiceEndpointsFacts
    )
    django: DjangoFacts = field(default_factory=DjangoFacts)
    react: ReactFacts = field(default_factory=ReactFacts)
    capabilities: CapabilitiesFacts = field(
        default_factory=CapabilitiesFacts
    )
    template: ProjectTemplateFacts = field(
        default_factory=ProjectTemplateFacts
    )


class DjangoReactApplicationAnalyzer:
    APP_TEMPLATE_TARGET_MANIFEST = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "django_react_app_template_make_targets.json"
    )
    APPLICATION_TARGET_DECLARATION_FILE = "docforge.make-targets.json"
    LOCAL_TEMPLATE_MANIFEST_FILE = "docforge.template.json"
    LOCAL_PROJECT_METADATA_FILE = "docforge.project.json"
    CATEGORY_BY_TARGET = {
        "init": "setup",
        "dev": "environment",
        "prod": "environment",
        "up": "startup",
        "down": "shutdown",
        "restart": "restart",
        "rebuild": "build",
        "logs": "logs",
        "ps": "diagnostic",
        "check": "diagnostic",
        "migrate": "migrations",
        "update": "build",
        "backup": "backup",
        "restore": "restore",
    }

    def analyze(
        self,
        context: AnalysisContext,
    ) -> DjangoReactApplicationFacts:
        project = context.project
        architecture = context.require_as(
            "architecture",
            ArchitectureFacts,
        )
        deployment = context.require_as(
            "deployment",
            DeploymentFacts,
        )
        api = context.require_as(
            "api",
            ApiFacts,
        )

        facts = DjangoReactApplicationFacts(
            application=self._application_overview(
                project
            )
        )

        env_result = self._analyze_environments(project)
        facts.environments = env_result[0]
        facts.service_endpoints = env_result[1]
        facts.environment_variables = (
            self._analyze_environment_variables(
                project,
                facts.environments,
            )
        )
        facts.operational_commands = (
            self._analyze_operational_commands(project)
        )
        self._attach_commands_to_environments(
            facts.environments,
            facts.operational_commands,
        )
        facts.django = self._analyze_django(
            project,
            api=api,
            operational_commands=facts.operational_commands,
        )
        facts.react = self._analyze_react(project)
        facts.capabilities = self._analyze_capabilities(
            facts.django,
            facts.react,
        )
        facts.template = self._analyze_template_project(
            project,
            environments=facts.environments,
            operational_commands=facts.operational_commands,
        )

        # Keep a weak link to already detected compose/deployment facts.
        self._merge_architecture_context(
            facts.environments,
            architecture,
            deployment,
        )

        return facts

    def _application_overview(
        self,
        project: Project,
    ) -> ApplicationOverviewFacts:
        return ApplicationOverviewFacts(
            name=project.name,
            category="django-react",
            backend_framework="Django",
            frontend_framework="React/Vite",
            source_paths=[
                "backend/App/settings.py",
                "frontend/package.json",
                "docker-compose.dev.yml",
                "docker-compose.prod.yml",
            ],
        )

    def _analyze_template_project(
        self,
        project: Project,
        *,
        environments: ProjectEnvironmentsFacts,
        operational_commands: OperationalCommandsFacts,
    ) -> ProjectTemplateFacts:
        template_manifest = self._load_local_template_manifest(project.root)
        project_metadata = self._load_local_project_metadata(project.root)

        if template_manifest and project_metadata:
            return ProjectTemplateFacts(
                detected=False,
                manifest_source=(
                    f"{self.LOCAL_TEMPLATE_MANIFEST_FILE}, {self.LOCAL_PROJECT_METADATA_FILE}"
                ),
                risks=[
                    "Le dépôt contient à la fois docforge.template.json et docforge.project.json, ce qui rend la nature template/application ambiguë."
                ],
                source_paths=[
                    self.LOCAL_TEMPLATE_MANIFEST_FILE,
                    self.LOCAL_PROJECT_METADATA_FILE,
                ],
            )

        if template_manifest is not None:
            if template_manifest.get("invalid"):
                return ProjectTemplateFacts(
                    detected=False,
                    project_kind="application-template",
                    template_id=template_manifest.get("template_id"),
                    template_version=template_manifest.get("template_version"),
                    base_profile=template_manifest.get("base_profile") or "django-react",
                    manifest_source=template_manifest.get("source"),
                    manifest_fallback_used=False,
                    risks=list(template_manifest.get("errors", [])),
                    source_paths=[self.LOCAL_TEMPLATE_MANIFEST_FILE],
                )
            return self._build_template_source_facts(
                project,
                operational_commands=operational_commands,
                manifest=template_manifest,
            )

        if project_metadata is not None:
            if project_metadata.get("invalid"):
                return ProjectTemplateFacts(
                    detected=False,
                    project_kind="application",
                    origin_template_id=project_metadata.get("origin_template_id"),
                    template_version=project_metadata.get("origin_template_version"),
                    origin_template_version=project_metadata.get("origin_template_version"),
                    base_profile=project_metadata.get("base_profile") or "django-react",
                    manifest_source=project_metadata.get("source"),
                    manifest_fallback_used=False,
                    risks=list(project_metadata.get("errors", [])),
                    source_paths=[self.LOCAL_PROJECT_METADATA_FILE],
                )
            return self._build_generated_application_facts(
                project,
                operational_commands=operational_commands,
                metadata=project_metadata,
            )

        return self._detect_app_template_contract(
            project,
            environments=environments,
            operational_commands=operational_commands,
        )

    def _detect_app_template_contract(
        self,
        project: Project,
        *,
        environments: ProjectEnvironmentsFacts,
        operational_commands: OperationalCommandsFacts,
    ) -> ProjectTemplateFacts:
        """Recognize a generated app only from independent contract evidence."""
        invariants_path = project.root / "INVARIANTS.md"
        if not invariants_path.is_file():
            return ProjectTemplateFacts()

        try:
            invariants = invariants_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except OSError:
            return ProjectTemplateFacts()

        invariant_markers = (
            "contrat technique",
            "APP_DEPOT",
            "docker-compose.dev.yml",
            "docker-compose.prod.yml",
        )
        matched_markers = [
            marker for marker in invariant_markers
            if marker.casefold() in invariants.casefold()
        ]
        invariant_contract = len(matched_markers) >= 3

        standard_targets = {
            "init", "dev", "prod", "up", "down", "restart", "rebuild",
            "logs", "ps", "check", "migrate", "backup", "restore",
        }
        matched_targets = sorted(
            command.name
            for command in operational_commands.commands
            if command.name in standard_targets
            and command.provenance in {"template-standard", "app-template"}
        )
        standard_make_contract = len(matched_targets) >= 8

        compose_pair = all(
            (project.root / name).is_file()
            for name in ("docker-compose.dev.yml", "docker-compose.prod.yml")
        )
        service_names = {
            service.name
            for environment in environments.items
            for service in environment.services
        }
        standard_services = {"db", "backend", "frontend"}.issubset(service_names)

        if not (
            invariant_contract
            and standard_make_contract
            and compose_pair
            and standard_services
        ):
            return ProjectTemplateFacts()

        evidence = [
            "contrat app-template détecté dans INVARIANTS.md: "
            + ", ".join(matched_markers),
            f"cibles Make app-template vérifiées: {len(matched_targets)}",
            "docker-compose.dev.yml et docker-compose.prod.yml détectés",
            "services app-template détectés: db, backend, frontend",
        ]
        return ProjectTemplateFacts(
            detected=True,
            project_kind="application",
            origin_template_id="app-template",
            base_profile="django-react",
            manifest_source="heuristic: INVARIANTS.md + Makefile + Docker Compose",
            manifest_fallback_used=True,
            manifest_declared_targets=matched_targets,
            manifest_verified_targets=matched_targets,
            evidence=evidence,
            source_paths=[
                "INVARIANTS.md",
                "Makefile",
                "docker-compose.dev.yml",
                "docker-compose.prod.yml",
            ],
        )

    def _build_template_source_facts(
        self,
        project: Project,
        *,
        operational_commands: OperationalCommandsFacts,
        manifest: dict[str, Any],
    ) -> ProjectTemplateFacts:
        command_names = {item.name for item in operational_commands.commands}
        declared_targets = sorted(manifest.get("targets", {}).keys())
        verified_targets = [name for name in declared_targets if name in command_names]
        missing_targets = [name for name in declared_targets if name not in command_names]
        source_paths = sorted(
            {
                self.LOCAL_TEMPLATE_MANIFEST_FILE,
                "README.md",
                "README_DEV.md",
                "AGENTS.md",
                "CODEX_START.md",
                "INVARIANTS.md",
                "Makefile",
                "scripts/init.sh",
                "scripts/generate-env.sh",
                "scripts/generate-secrets.sh",
                "scripts/check-invariants.sh",
                "scripts/docforge-project-metadata.py",
            }
        )
        evidence = [
            f"template manifest detected: {manifest.get('source')}",
            f"project_kind={manifest.get('project_kind')}",
            f"template_id={manifest.get('template_id')}",
            f"template_version={manifest.get('template_version')}",
        ]
        if manifest.get("base_profile"):
            evidence.append(f"base_profile={manifest.get('base_profile')}")
        if verified_targets:
            evidence.append(
                f"verified make targets: {len(verified_targets)}/{len(declared_targets)}"
            )

        return ProjectTemplateFacts(
            detected=True,
            project_kind=manifest.get("project_kind") or "application-template",
            template_id=manifest.get("template_id"),
            template_version=manifest.get("template_version"),
            base_profile=manifest.get("base_profile") or "django-react",
            manifest_source=manifest.get("source"),
            manifest_fallback_used=False,
            manifest_declared_targets=declared_targets,
            manifest_verified_targets=verified_targets,
            manifest_missing_targets=missing_targets,
            evidence=evidence,
            placeholders=self._template_placeholders(project),
            current_state=self._template_current_state(manifest),
            target_state=self._template_target_state(manifest),
            materialization=self._template_materialization_facts(
                project,
                manifest=manifest,
                operational_commands=operational_commands,
            ),
            creator_workflows=self._template_creator_workflows(
                project,
                manifest=manifest,
                operational_commands=operational_commands,
            ),
            maintainer_workflows=self._template_maintainer_workflows(
                project,
                manifest=manifest,
                operational_commands=operational_commands,
            ),
            missing_steps=[
                "Aucune procédure démontrée de création du dépôt distant n’est documentée.",
                "Aucune procédure démontrée de premier commit du nouveau dépôt n’est documentée.",
                "Aucune procédure démontrée de mise à niveau d’une application déjà matérialisée vers une nouvelle version du modèle n’est documentée.",
            ],
            risks=[
                "Un clonage incomplet peut laisser des marqueurs __APP_NAME__ ou __APP_SLUG__ dans le frontend, l’API de santé et la documentation.",
                "L’absence de .env.template empêche make init et la génération des environnements.",
                "Une restauration PostgreSQL exécutée sans précaution remplace les données de la base active.",
                "Le détachement Git du modèle doit rester explicite et protégé pour éviter d’endommager le dépôt source.",
            ],
            source_paths=source_paths,
        )

    def _build_generated_application_facts(
        self,
        project: Project,
        *,
        operational_commands: OperationalCommandsFacts,
        metadata: dict[str, Any],
    ) -> ProjectTemplateFacts:
        command_names = {item.name for item in operational_commands.commands}
        declared_targets = sorted(metadata.get("targets", {}).keys())
        verified_targets = [name for name in declared_targets if name in command_names]
        missing_targets = [name for name in declared_targets if name not in command_names]
        origin = metadata.get("origin_template", {})
        identity = metadata.get("application_identity", {})
        evidence = [
            f"application metadata detected: {metadata.get('source')}",
            f"project_kind={metadata.get('project_kind')}",
            f"origin_template={origin.get('template_id')}",
            f"origin_template_version={origin.get('template_version')}",
        ]
        if identity.get("app_slug"):
            evidence.append(f"app_slug={identity.get('app_slug')}")
        if verified_targets:
            evidence.append(
                f"verified inherited make targets: {len(verified_targets)}/{len(declared_targets)}"
            )

        return ProjectTemplateFacts(
            detected=True,
            project_kind=metadata.get("project_kind") or "application",
            origin_template_id=origin.get("template_id"),
            template_version=origin.get("template_version"),
            origin_template_version=origin.get("template_version"),
            base_profile=metadata.get("base_profile") or "django-react",
            manifest_source=metadata.get("source"),
            manifest_fallback_used=False,
            manifest_declared_targets=declared_targets,
            manifest_verified_targets=verified_targets,
            manifest_missing_targets=missing_targets,
            evidence=evidence,
            current_state=TemplateStateFacts(
                project_kind=metadata.get("project_kind") or "application",
                origin_template_id=origin.get("template_id"),
                template_version=origin.get("template_version"),
                manifest_source=metadata.get("source"),
                base_profile=metadata.get("base_profile") or "django-react",
            ),
            source_paths=[self.LOCAL_PROJECT_METADATA_FILE],
        )

    def _template_placeholders(
        self,
        project: Project,
    ) -> list[TemplatePlaceholderFacts]:
        placeholders = [
            TemplatePlaceholderFacts(
                name="APP_NAME",
                kind="identity-variable",
                description="Nom lisible de l’application à renseigner dans .env.template.",
                required=True,
                files=[".env.template.example", "README_DEV.md"],
            ),
            TemplatePlaceholderFacts(
                name="APP_SLUG",
                kind="identity-variable",
                description="Identifiant technique court utilisé pour les conteneurs, services et variables dérivées.",
                required=True,
                files=[".env.template.example", "README_DEV.md", "docker-compose.dev.yml", "docker-compose.prod.yml"],
            ),
            TemplatePlaceholderFacts(
                name="APP_DEPOT",
                kind="identity-variable",
                description="Nom du dépôt et base de dérivation du token inter-apps local.",
                required=True,
                files=[".env.template.example", "README_DEV.md", "scripts/generate-secrets.sh"],
            ),
            TemplatePlaceholderFacts(
                name="APP_NO",
                kind="identity-variable",
                description="Numéro servant à dériver les ports de développement.",
                required=True,
                files=[".env.template.example", "README_DEV.md", "scripts/check-invariants.sh"],
            ),
            TemplatePlaceholderFacts(
                name="ADMIN_USERNAME",
                kind="bootstrap-secret",
                description="Compte administrateur initial injecté dans .env.local lors du bootstrap.",
                required=True,
                files=[".env.template.example", "scripts/generate-env.sh"],
            ),
            TemplatePlaceholderFacts(
                name="ADMIN_EMAIL",
                kind="bootstrap-secret",
                description="Courriel du compte administrateur initial.",
                required=True,
                files=[".env.template.example", "scripts/generate-env.sh"],
            ),
            TemplatePlaceholderFacts(
                name="ADMIN_PASSWORD",
                kind="bootstrap-secret",
                description="Mot de passe initial à recopier ensuite dans .env.local.",
                required=True,
                files=[".env.template.example", "scripts/generate-env.sh"],
            ),
            TemplatePlaceholderFacts(
                name="APP_HOST",
                kind="derived-variable",
                description="Domaine public de production. Le script génère ${APP_SLUG}.mon-site.ca si la valeur n’est pas fournie.",
                required=False,
                files=["scripts/generate-env.sh", "docker-compose.prod.yml"],
            ),
        ]

        token_files = self._find_placeholder_files(project, "__APP_NAME__")
        if token_files:
            placeholders.append(
                TemplatePlaceholderFacts(
                    name="__APP_NAME__",
                    kind="text-token",
                    description="Marqueur textuel restant à remplacer dans les sources et documents du squelette.",
                    required=True,
                    files=token_files,
                )
            )
        slug_files = self._find_placeholder_files(project, "__APP_SLUG__")
        if slug_files:
            placeholders.append(
                TemplatePlaceholderFacts(
                    name="__APP_SLUG__",
                    kind="text-token",
                    description="Marqueur textuel restant à remplacer dans les sources frontend et les exemples de nommage.",
                    required=True,
                    files=slug_files,
                )
            )
        return placeholders

    def _find_placeholder_files(
        self,
        project: Project,
        token: str,
    ) -> list[str]:
        matches: list[str] = []
        for rel_path in project.files:
            if not rel_path.endswith((".md", ".py", ".js", ".jsx", ".json", ".html", ".yml", ".css", ".example", ".txt")):
                continue
            try:
                content = (project.root / rel_path).read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except OSError:
                continue
            if token in content:
                matches.append(rel_path)
        return sorted(matches)

    def _template_current_state(
        self,
        manifest: dict[str, Any],
    ) -> TemplateStateFacts:
        return TemplateStateFacts(
            project_kind=manifest.get("project_kind") or "application-template",
            template_id=manifest.get("template_id"),
            template_version=manifest.get("template_version"),
            manifest_source=manifest.get("source"),
            base_profile=manifest.get("base_profile") or "django-react",
        )

    def _template_target_state(
        self,
        manifest: dict[str, Any],
    ) -> TemplateStateFacts:
        return TemplateStateFacts(
            project_kind="application",
            origin_template_id=manifest.get("template_id"),
            template_version=manifest.get("template_version"),
            manifest_source=self.LOCAL_PROJECT_METADATA_FILE,
            base_profile=manifest.get("base_profile") or "django-react",
        )

    def _template_materialization_facts(
        self,
        project: Project,
        *,
        manifest: dict[str, Any],
        operational_commands: OperationalCommandsFacts,
    ) -> TemplateMaterializationFacts:
        init_path = project.root / "scripts" / "init.sh"
        metadata_path = project.root / "scripts" / "docforge-project-metadata.py"
        init_text = self._read_text(init_path) if init_path.is_file() else ""
        metadata_text = self._read_text(metadata_path) if metadata_path.is_file() else ""
        command_names = {item.name for item in operational_commands.commands}
        activation_command = None
        if "init" in command_names:
            activation_command = "DOCFORGE_INIT_APPLICATION=1 DOCFORGE_DETACH_GIT=1 make init"
        maintenance_command = None
        if "init" in command_names:
            maintenance_command = (
                "DOCFORGE_INIT_APPLICATION=1 DOCFORGE_DETACH_GIT=1 "
                "DOCFORGE_SKIP_STARTUP=1 make init"
            )

        protections: list[str] = []
        if "DOCFORGE_INIT_APPLICATION" in init_text:
            protections.append(
                "La matérialisation de l’application n’est activée que lorsque DOCFORGE_INIT_APPLICATION=1 est fourni."
            )
        if "DOCFORGE_DETACH_GIT" in init_text and "--detach-git" in metadata_text:
            protections.append(
                "Le détachement Git reste explicite et n’est déclenché que lorsque DOCFORGE_DETACH_GIT=1 est fourni."
            )
        if "_guard_git_detach" in metadata_text or "Refus de détacher l'historique Git" in metadata_text:
            protections.append(
                "Le script refuse par défaut de détacher l’historique Git dans un répertoire portant encore le nom du modèle source."
            )
        if "Le dépôt ne doit pas contenir à la fois docforge.template.json et docforge.project.json" in metadata_text:
            protections.append(
                "La coexistence de docforge.template.json et docforge.project.json provoque une erreur bloquante."
            )
        if "APP_SLUG et APP_DEPOT ne doivent pas conserver l'identité du modèle source" in metadata_text:
            protections.append(
                "La matérialisation échoue si APP_SLUG ou APP_DEPOT conservent l’identité du modèle source."
            )

        expected_results = [
            "docforge.project.json est généré pour l’application matérialisée.",
            "docforge.template.json est retiré du dépôt matérialisé.",
            "Le project_kind attendu devient application.",
            f"origin_template_id attendu: {manifest.get('template_id')}.",
            f"template_version conservée: {manifest.get('template_version')}.",
            "Les placeholders __APP_NAME__ et __APP_SLUG__ sont remplacés dans les fichiers texte analysés.",
        ]
        if "DOCFORGE_SKIP_STARTUP" in init_text:
            expected_results.append(
                "Le démarrage Docker Compose peut être ignoré uniquement avec DOCFORGE_SKIP_STARTUP=1 dans un contexte de test ou de maintenance."
            )

        validation_commands = []
        if "check" in command_names:
            validation_commands.append("make check")
        if "validate --expect-application" in metadata_text:
            validation_commands.append(
                "./scripts/docforge-project-metadata.py validate --expect-application"
            )

        return TemplateMaterializationFacts(
            supported=bool(activation_command and metadata_text),
            entrypoint="make init" if "init" in command_names else None,
            activation_command=activation_command,
            activation_variable_name="DOCFORGE_INIT_APPLICATION" if "DOCFORGE_INIT_APPLICATION" in init_text else None,
            activation_variable_value="1" if "DOCFORGE_INIT_APPLICATION" in init_text else None,
            git_detach_variable_name="DOCFORGE_DETACH_GIT" if "DOCFORGE_DETACH_GIT" in init_text else None,
            git_detach_variable_value="1" if "DOCFORGE_DETACH_GIT" in init_text else None,
            explicit_git_detach_only="DOCFORGE_DETACH_GIT" in init_text,
            source_repository_protected="_guard_git_detach" in metadata_text or 'basename "$PWD"' in init_text,
            allow_source_name_override="allow-source-name" in metadata_text or "DOCFORGE_ALLOW_SOURCE_NAME" in init_text,
            skip_startup_variable_name="DOCFORGE_SKIP_STARTUP" if "DOCFORGE_SKIP_STARTUP" in init_text else None,
            skip_startup_variable_value="1" if "DOCFORGE_SKIP_STARTUP" in init_text else None,
            skip_startup_audience="test-maintenance" if "DOCFORGE_SKIP_STARTUP" in init_text else None,
            skip_startup_normal_workflow=False if "DOCFORGE_SKIP_STARTUP" in init_text else True,
            maintenance_command=maintenance_command,
            placeholders_replaced=[
                placeholder.name
                for placeholder in self._template_placeholders(project)
                if placeholder.name in {"__APP_NAME__", "__APP_SLUG__"}
            ],
            source_metadata_file=self.LOCAL_TEMPLATE_MANIFEST_FILE,
            generated_metadata_file=self.LOCAL_PROJECT_METADATA_FILE,
            metadata_script="scripts/docforge-project-metadata.py" if metadata_path.is_file() else None,
            creates_independent_git_repository="_detach_git_history" in metadata_text,
            generated_files=[self.LOCAL_PROJECT_METADATA_FILE],
            removed_files=[self.LOCAL_TEMPLATE_MANIFEST_FILE],
            validation_commands=validation_commands,
            protections=protections,
            expected_results=expected_results,
            sources=[
                source
                for source in (
                    "scripts/init.sh" if init_path.is_file() else None,
                    "scripts/check-invariants.sh" if (project.root / "scripts" / "check-invariants.sh").is_file() else None,
                    "scripts/docforge-project-metadata.py" if metadata_path.is_file() else None,
                    self.LOCAL_TEMPLATE_MANIFEST_FILE,
                )
                if source is not None
            ],
        )

    def _template_creator_workflows(
        self,
        project: Project,
        *,
        manifest: dict[str, Any],
        operational_commands: OperationalCommandsFacts,
    ) -> list[TemplateWorkflowFacts]:
        command_names = {item.name for item in operational_commands.commands}
        materialization = self._template_materialization_facts(
            project,
            manifest=manifest,
            operational_commands=operational_commands,
        )
        workflows: list[TemplateWorkflowFacts] = []
        workflows.append(
            TemplateWorkflowFacts(
                identifier="template-identity-setup",
                audience="creator",
                title="Préparer l’identité du nouveau projet",
                commands=["cp .env.template.example .env.template"],
                files=[".env.template.example", ".env.template"],
                preconditions=["Le dépôt a été copié ou cloné dans son nouvel emplacement."],
                expected_results=["Le fichier .env.template existe et peut être personnalisé."],
                personalization_points=["APP_NAME", "APP_SLUG", "APP_DEPOT", "APP_NO", "ADMIN_USERNAME", "ADMIN_EMAIL", "ADMIN_PASSWORD"],
                risks=["Sans .env.template, make init et les scripts de génération échouent."],
                sources=["README_DEV.md", "scripts/init.sh", "scripts/generate-env.sh"],
            )
        )
        if {"dev", "prod"} & command_names:
            workflows.append(
                TemplateWorkflowFacts(
                    identifier="template-select-environment",
                    audience="creator",
                    title="Choisir l’environnement actif",
                    commands=[command for command in ("make dev", "make prod") if command.split()[-1] in command_names],
                    files=[".env"],
                    preconditions=[".env.template a été préparé."],
                    expected_results=[".env pointe vers .env.dev ou .env.prod."],
                    personalization_points=["Choisir dev pour le premier démarrage local, prod pour préparer les variables de production."],
                    risks=["make init échoue si .env n’est pas un lien symbolique vers .env.dev ou .env.prod."],
                    sources=["README_DEV.md", "scripts/env-switch.sh", "scripts/init.sh"],
                )
            )
        workflows.append(
            TemplateWorkflowFacts(
                identifier="template-generate-environments",
                audience="creator",
                title="Générer les fichiers d’environnement et les secrets locaux",
                commands=["./scripts/generate-env.sh", "./scripts/generate-secrets.sh"],
                files=[".env.dev", ".env.prod", ".env.local"],
                preconditions=[".env.template existe et contient les variables d’identité requises."],
                expected_results=[".env.dev et .env.prod sont régénérés avec les ports dérivés.", ".env.local existe et contient les clés ADMIN_*, POSTGRES_PASSWORD, DJANGO_SECRET_KEY et le token local inter-apps."],
                personalization_points=["APP_HOST peut être laissé vide pour utiliser ${APP_SLUG}.mon-site.ca ou surchargé ensuite."],
                risks=["Les marqueurs textuels du frontend et de la documentation ne sont pas remplacés par ces scripts seuls."],
                sources=["README_DEV.md", "scripts/generate-env.sh", "scripts/generate-secrets.sh"],
            )
        )
        if "init" in command_names:
            workflows.append(
                TemplateWorkflowFacts(
                    identifier="template-first-init",
                    audience="creator",
                    title="Matérialiser l’application et lancer l’initialisation",
                    commands=[materialization.activation_command or "make init"],
                    files=["scripts/init.sh", "scripts/docforge-project-metadata.py", "docforge.template.json", "docforge.project.json"],
                    preconditions=[
                        ".env.template existe et a été personnalisé.",
                        ".env pointe déjà vers .env.dev ou .env.prod.",
                        "Le dépôt a été copié dans un nouveau répertoire avant de matérialiser l’application.",
                    ],
                    expected_results=[
                        ".env.dev, .env.prod et .env.local sont prêts.",
                        "Les métadonnées passent de docforge.template.json à docforge.project.json.",
                        "project_kind devient application.",
                        f"origin_template_id attendu: {manifest.get('template_id')}.",
                        "Les placeholders __APP_NAME__ et __APP_SLUG__ ne subsistent plus dans les fichiers texte analysés.",
                    ],
                    personalization_points=[
                        "Choisir l’environnement avant make init via make dev ou make prod.",
                        "APP_NAME, APP_SLUG, APP_DEPOT, APP_NO, ADMIN_USERNAME, ADMIN_EMAIL et ADMIN_PASSWORD doivent être renseignés dans .env.template.",
                    ],
                    risks=[
                        "Sans DOCFORGE_INIT_APPLICATION=1, make init conserve le mode template source.",
                        "Le détachement Git reste optionnel et ne se produit que si DOCFORGE_DETACH_GIT=1 est fourni explicitement.",
                    ],
                    sources=["README.md", "README_DEV.md", "scripts/init.sh", "scripts/docforge-project-metadata.py"],
                )
            )
            workflows.append(
                TemplateWorkflowFacts(
                    identifier="template-git-transition",
                    audience="creator",
                    title="Détacher explicitement l’historique Git du modèle",
                    commands=[materialization.activation_command or "DOCFORGE_INIT_APPLICATION=1 DOCFORGE_DETACH_GIT=1 make init"],
                    files=["scripts/init.sh", "scripts/docforge-project-metadata.py", ".git"],
                    preconditions=[
                        "La matérialisation est déclenchée depuis une copie de travail et non depuis le dépôt source.",
                        "DOCFORGE_DETACH_GIT=1 est fourni explicitement.",
                    ],
                    expected_results=[
                        "Un nouveau dépôt Git indépendant est initialisé pour l’application matérialisée.",
                        "Le dépôt source n’est pas modifié lorsque le répertoire conserve encore le nom du modèle source.",
                    ],
                    risks=[
                        "Le détachement Git est une opération destructive sur l’historique local et doit rester volontaire.",
                        "Un forçage éventuel avec allow-source-name doit être traité comme une exception dangereuse.",
                    ],
                    sources=["scripts/init.sh", "scripts/docforge-project-metadata.py"],
                )
            )
        if "check" in command_names:
            workflows.append(
                TemplateWorkflowFacts(
                    identifier="template-validate-invariants",
                    audience="creator",
                    title="Valider les invariants après personnalisation",
                    commands=["make check"],
                    files=["scripts/check-invariants.sh", ".gitignore", ".env.dev", ".env.prod", ".env.local", ".env"],
                    preconditions=["Les fichiers d’environnement ont été générés."],
                    expected_results=[
                        "Les variables d’identité et les ports dérivés sont vérifiés.",
                        "Le lien symbolique .env, les placeholders remplacés et l’état attendu des métadonnées DocForge sont validés.",
                    ],
                    risks=["Un APP_NO ou un POSTGRES_USER incohérent provoque un échec bloquant."],
                    sources=["README_DEV.md", "scripts/check-invariants.sh", "scripts/docforge-project-metadata.py"],
                )
            )
        if "migrate" in command_names:
            workflows.append(
                TemplateWorkflowFacts(
                    identifier="template-apply-migrations",
                    audience="creator",
                    title="Appliquer les migrations Django du squelette",
                    commands=["make migrate"],
                    files=["scripts/migrate.sh", "backend/manage.py"],
                    preconditions=["Les services backend et db sont démarrés."],
                    expected_results=["python manage.py migrate est exécuté dans le service backend de l’environnement actif."],
                    missing_information=["Aucune commande démontrée de création initiale du compte administrateur n’accompagne cette étape dans le template standard."],
                    sources=["README_DEV.md", "scripts/migrate.sh"],
                )
            )
        return workflows

    def _template_maintainer_workflows(
        self,
        project: Project,
        *,
        manifest: dict[str, Any],
        operational_commands: OperationalCommandsFacts,
    ) -> list[TemplateWorkflowFacts]:
        command_names = {item.name for item in operational_commands.commands}
        materialization = self._template_materialization_facts(
            project,
            manifest=manifest,
            operational_commands=operational_commands,
        )
        workflows: list[TemplateWorkflowFacts] = []
        if "check" in command_names:
            workflows.append(
                TemplateWorkflowFacts(
                    identifier="template-maintainer-validate",
                    audience="maintainer",
                    title="Vérifier les invariants du template",
                    commands=["make check"],
                    files=["INVARIANTS.md", "Makefile", "scripts/check-invariants.sh"],
                    expected_results=["La structure standard, les conventions d’environnement et les ports dérivés restent cohérents."],
                    risks=["Un changement non accompagné dans .gitignore ou les fichiers .env.* brise le bootstrap des futures applications."],
                    sources=["README.md", "README_DEV.md", "scripts/check-invariants.sh", "scripts/docforge-project-metadata.py"],
                )
            )
            if materialization.maintenance_command:
                workflows.append(
                    TemplateWorkflowFacts(
                        identifier="template-maintainer-disposable-copy",
                        audience="maintainer",
                        title="Valider la matérialisation sur une copie jetable",
                        commands=[
                            "cp .env.template.example .env.template",
                            "make dev",
                            materialization.maintenance_command,
                            "make check",
                        ],
                        files=[
                            ".env.template.example",
                            "scripts/init.sh",
                            "scripts/check-invariants.sh",
                            "scripts/docforge-project-metadata.py",
                        ],
                        preconditions=[
                            "Le test est exécuté sur une copie temporaire du modèle, jamais sur le dépôt source.",
                            ".env.template contient une identité complète et un bootstrap administrateur valides.",
                        ],
                        expected_results=[
                            "La copie est détectée comme application après matérialisation.",
                            "Le démarrage Docker Compose peut être ignoré pour ce test avec DOCFORGE_SKIP_STARTUP=1.",
                        ],
                        risks=[
                            "DOCFORGE_SKIP_STARTUP=1 est un mécanisme de test ou de maintenance, pas le workflow normal de création d’une application.",
                        ],
                        sources=[
                            "scripts/init.sh",
                            "scripts/check-invariants.sh",
                            "scripts/docforge-project-metadata.py",
                        ],
                    )
                )
        if "update" in command_names:
            workflows.append(
                TemplateWorkflowFacts(
                    identifier="template-maintainer-update",
                    audience="maintainer",
                    title="Exécuter la séquence standard de mise à jour du template",
                    commands=["make update"],
                    files=["scripts/update.sh", "scripts/backup-db.sh", "scripts/rebuild.sh", "scripts/up.sh", "scripts/migrate.sh", "scripts/ps.sh"],
                    expected_results=["Le dépôt local est mis à jour avec git pull --ff-only puis redémarré et validé."],
                    risks=["La séquence inclut un backup PostgreSQL puis un git pull --ff-only; elle suppose un arbre Git compatible et un environnement déjà configuré."],
                    sources=["README.md", "README_DEV.md", "scripts/update.sh"],
                )
            )
        return workflows

    def _load_local_template_manifest(

        self,
        root: Path,
    ) -> dict[str, Any] | None:
        path = root / self.LOCAL_TEMPLATE_MANIFEST_FILE
        if not path.is_file():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {
                "invalid": True,
                "source": self.LOCAL_TEMPLATE_MANIFEST_FILE,
                "errors": [f"docforge.template.json invalide: {exc}"],
                "targets": {},
            }
        targets = {
            item.get("name"): item
            for item in payload.get("make_targets", [])
            if isinstance(item, dict) and item.get("name")
        }
        errors: list[str] = []
        if payload.get("project_kind") != "application-template":
            errors.append("docforge.template.json doit déclarer project_kind=application-template")
        if not payload.get("template_id"):
            errors.append("docforge.template.json doit déclarer template_id")
        if not payload.get("template_version"):
            errors.append("docforge.template.json doit déclarer template_version")
        payload["targets"] = targets
        payload["source"] = self.LOCAL_TEMPLATE_MANIFEST_FILE
        if errors:
            payload["invalid"] = True
            payload["errors"] = errors
        return payload

    def _load_local_project_metadata(
        self,
        root: Path,
    ) -> dict[str, Any] | None:
        path = root / self.LOCAL_PROJECT_METADATA_FILE
        if not path.is_file():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {
                "invalid": True,
                "source": self.LOCAL_PROJECT_METADATA_FILE,
                "errors": [f"docforge.project.json invalide: {exc}"],
                "targets": {},
            }
        inherited = payload.get("inherited_make_targets", [])
        targets = {
            item.get("name"): item
            for item in inherited
            if isinstance(item, dict) and item.get("name")
        }
        origin = payload.get("origin_template") if isinstance(payload.get("origin_template"), dict) else {}
        errors: list[str] = []
        if payload.get("project_kind") != "application":
            errors.append("docforge.project.json doit déclarer project_kind=application")
        if not origin.get("template_id"):
            errors.append("docforge.project.json doit déclarer origin_template.template_id")
        if not origin.get("template_version"):
            errors.append("docforge.project.json doit déclarer origin_template.template_version")
        payload["targets"] = targets
        payload["source"] = self.LOCAL_PROJECT_METADATA_FILE
        payload["origin_template_id"] = origin.get("template_id")
        payload["origin_template_version"] = origin.get("template_version")
        if errors:
            payload["invalid"] = True
            payload["errors"] = errors
        return payload

    def _analyze_environments(
        self,
        project: Project,
    ) -> tuple[
        ProjectEnvironmentsFacts,
        ServiceEndpointsFacts,
    ]:
        environments: list[EnvironmentFacts] = []
        endpoints: list[ServiceEndpointFacts] = []

        for compose_file in sorted(
            path
            for path in project.files
            if path.startswith("docker-compose.")
            and path.endswith(".yml")
        ):
            compose_path = project.root / compose_file
            data = self._read_yaml(compose_path)
            if not isinstance(data, dict):
                continue

            environment_name = self._environment_name(
                compose_file
            )
            env_facts = EnvironmentFacts(
                name=environment_name,
                compose_file=compose_file,
                source_paths=[compose_file],
            )

            services = data.get("services", {})
            if isinstance(services, dict):
                for service_name, definition in services.items():
                    if not isinstance(definition, dict):
                        continue

                    service_facts = self._compose_service(
                        root=project.root,
                        service_name=str(service_name),
                        environment=environment_name,
                        compose_file=compose_file,
                        definition=definition,
                    )
                    env_facts.services.append(service_facts)
                    self._extend_unique(
                        env_facts.env_files,
                        service_facts.env_files,
                    )

                    endpoints.extend(
                        self._service_endpoints(
                            service_facts
                        )
                    )

            env_facts.services.sort(
                key=lambda item: item.name
            )
            env_facts.env_files = sorted(
                set(env_facts.env_files)
            )
            env_facts.urls = sorted(
                {
                    endpoint.url
                    for endpoint in endpoints
                    if endpoint.environment
                    == environment_name
                }
            )
            environments.append(env_facts)

        return (
            ProjectEnvironmentsFacts(items=environments),
            ServiceEndpointsFacts(endpoints=endpoints),
        )

    def _compose_service(
        self,
        *,
        root: Path,
        service_name: str,
        environment: str,
        compose_file: str,
        definition: dict[str, Any],
    ) -> ComposeServiceFacts:
        labels = self._label_list(
            definition.get("labels", [])
        )
        env_files = self._normalized_env_files(
            root,
            self._list_value(
                definition.get("env_file", [])
            ),
            environment,
        )
        service = ComposeServiceFacts(
            name=service_name,
            environment=environment,
            compose_file=compose_file,
            role=self._service_role(
                service_name,
                definition,
            ),
            image=self._optional_string(
                definition.get("image")
            ),
            build_context=self._build_context(
                definition.get("build")
            ),
            command=self._command_string(
                definition.get("command")
            ),
            ports=self._list_value(
                definition.get("ports", [])
            ),
            exposed_ports=self._exposed_ports(
                definition.get("ports", [])
            ),
            depends_on=self._depends_on(
                definition.get("depends_on", [])
            ),
            volumes=self._list_value(
                definition.get("volumes", [])
            ),
            networks=self._list_value(
                definition.get("networks", [])
            ),
            env_files=env_files,
            env_variables=sorted(
                self._env_names_from_definition(
                    definition
                )
                | self._env_names_from_files(
                    root,
                    env_files,
                )
            ),
            healthchecks=self._healthchecks(
                definition.get("healthcheck")
            ),
            traefik_labels=labels,
            detected_hosts=sorted(
                self._resolve_host_placeholders(
                    self._hosts_from_labels(labels),
                    root,
                    env_files or self._compose_interpolation_env_files(root, environment),
                )
            ),
            source=compose_file,
        )
        return service

    def _service_endpoints(
        self,
        service: ComposeServiceFacts,
    ) -> list[ServiceEndpointFacts]:
        endpoints: list[ServiceEndpointFacts] = []

        if service.environment == "dev":
            for port in service.ports:
                host_port = self._extract_host_port(port)
                if not host_port:
                    continue
                if service.name == "frontend":
                    url = self._build_url("http", "localhost", host_port)
                    endpoints.append(
                        self._endpoint_fact(
                            environment="dev",
                            service=service.name,
                            url=url,
                            source=service.source,
                        )
                    )
                if service.name == "backend":
                    for path_suffix in ("/api/", "/admin/"):
                        url = self._build_url(
                            "http",
                            "localhost",
                            host_port,
                            path_suffix,
                        )
                        endpoints.append(
                            self._endpoint_fact(
                                environment="dev",
                                service=service.name,
                                url=url,
                                source=service.source,
                            )
                        )

        if service.detected_hosts:
            for host in service.detected_hosts:
                candidate_paths = []
                for label in service.traefik_labels:
                    if "!PathPrefix(" in label:
                        continue
                    if "PathPrefix(`/api/`)" in label or "PathPrefix(`/api`)" in label:
                        candidate_paths.append("/api/")
                    elif "PathPrefix(`/admin/`)" in label or "PathPrefix(`/admin`)" in label:
                        candidate_paths.append("/admin/")
                    elif "PathPrefix(`/static/`)" in label or "PathPrefix(`/static`)" in label:
                        candidate_paths.append("/static/")
                if not candidate_paths:
                    candidate_paths = [""]
                for path_suffix in candidate_paths:
                    url = self._build_url("https", host, None, path_suffix)
                    endpoints.append(
                        self._endpoint_fact(
                            environment=service.environment,
                            service=service.name,
                            url=url,
                            source=service.source,
                        )
                    )

        deduped: dict[tuple[str, str, str], ServiceEndpointFacts] = {}
        for endpoint in endpoints:
            deduped[(endpoint.environment, endpoint.service, endpoint.url)] = endpoint
        return list(deduped.values())

    def _analyze_operational_commands(
        self,
        project: Project,
    ) -> OperationalCommandsFacts:
        commands: list[OperationalCommandFacts] = []
        makefile_path = project.root / "Makefile"

        try:
            lines = makefile_path.read_text(
                encoding="utf-8",
                errors="ignore",
            ).splitlines()
        except OSError:
            return OperationalCommandsFacts()

        help_entries = self._extract_make_help_entries(lines)
        default_target_visibility = "public" if not help_entries else "internal"
        declared_variables = self._extract_declared_make_variables(lines)
        phony_targets = self._extract_phony_targets(lines)
        local_template_manifest = self._load_local_template_manifest(project.root)
        local_project_metadata = self._load_local_project_metadata(project.root)
        local_origin_manifest = local_template_manifest or local_project_metadata
        template_manifest = (
            local_origin_manifest
            or self._load_app_template_target_manifest()
        )
        application_declarations = self._load_application_target_declarations(
            project.root
        )

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            declaration_head = line.split(":", 1)[0].strip()
            if (
                not stripped
                or line[0].isspace()
                or stripped.startswith("#")
                or stripped.startswith(".")
                or ":" not in line
                or ":=" in line
                or "?=" in line
                or "+=" in line
                or "=" in declaration_head
            ):
                i += 1
                continue

            target, remainder = line.split(":", 1)
            target = target.strip()
            prereq_part = remainder.split("##", 1)[0].strip()
            prerequisites = [item for item in prereq_part.split() if item]
            body: list[str] = []
            i += 1
            while i < len(lines):
                body_line = lines[i]
                if body_line.startswith("	") or body_line.startswith(" "):
                    body.append(body_line.strip())
                    i += 1
                    continue
                break

            if not target:
                continue

            help_text = help_entries.get(target)
            visibility = "public" if help_text else default_target_visibility
            category = self.CATEGORY_BY_TARGET.get(target, self._infer_command_category(target, prerequisites, body))
            manifest_entry = template_manifest.get("targets", {}).get(target)
            (
                provenance,
                documentation_policy,
                exclusion_reason,
                provenance_evidence,
                manifest_source,
            ) = self._classify_make_target(
                target=target,
                prerequisites=prerequisites,
                body=body,
                help_text=help_text,
                visibility=visibility,
                template_manifest=template_manifest,
                local_origin_manifest=local_origin_manifest,
                application_declarations=application_declarations,
            )
            commands.append(
                OperationalCommandFacts(
                    name=target,
                    category=category,
                    command=f"make {target}",
                    source="Makefile",
                    target=target,
                    body=body,
                    prerequisites=prerequisites,
                    environments=self._command_environments(target),
                    parameters=self._build_make_parameters(
                        target=target,
                        body=body,
                        help_entries=help_entries,
                        declared_variables=declared_variables,
                    ),
                    help_text=help_text,
                    phony=target in phony_targets,
                    documented=help_text is not None,
                    visibility=visibility,
                    provenance=provenance,
                    documentation_policy=documentation_policy,
                    exclusion_reason=exclusion_reason,
                    provenance_evidence=provenance_evidence,
                    manifest_source=manifest_source,
                    manifest_destructive=manifest_entry.get("destructive") if manifest_entry is not None else None,
                    manifest_destructive_effects=list(manifest_entry.get("destructive_effects", [])) if manifest_entry is not None else [],
                )
            )

        commands.sort(key=lambda item: (item.visibility != "public", item.category, item.command))
        return OperationalCommandsFacts(
            commands=commands,
            scripts=self._analyze_scripts(project),
        )

    def _load_app_template_target_manifest(self) -> dict[str, Any]:
        try:
            payload = json.loads(
                self.APP_TEMPLATE_TARGET_MANIFEST.read_text(
                    encoding="utf-8"
                )
            )
        except (OSError, json.JSONDecodeError):
            return {"source": None, "targets": {}}

        targets = {
            item.get("name"): item
            for item in payload.get("targets", [])
            if isinstance(item, dict) and item.get("name")
        }
        return {
            "source": str(
                self.APP_TEMPLATE_TARGET_MANIFEST.relative_to(
                    Path(__file__).resolve().parent.parent
                )
            ),
            "targets": targets,
        }

    def _load_application_target_declarations(
        self,
        root: Path,
    ) -> dict[str, MakeTargetDeclarationFacts]:
        path = root / self.APPLICATION_TARGET_DECLARATION_FILE
        if not path.is_file():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

        declarations: dict[str, MakeTargetDeclarationFacts] = {}
        for item in payload.get("targets", []):
            if not isinstance(item, dict) or not item.get("name"):
                continue
            declarations[item["name"]] = MakeTargetDeclarationFacts(
                name=item["name"],
                documentation_policy=item.get(
                    "documentation_policy",
                    "main-reference",
                ),
                audience=item.get("audience"),
                reference_level=item.get("reference_level"),
                source=self.APPLICATION_TARGET_DECLARATION_FILE,
            )
        return declarations

    def _classify_make_target(
        self,
        *,
        target: str,
        prerequisites: list[str],
        body: list[str],
        help_text: str | None,
        visibility: str,
        template_manifest: dict[str, Any],
        local_origin_manifest: dict[str, Any] | None,
        application_declarations: dict[str, MakeTargetDeclarationFacts],
    ) -> tuple[str, str, str | None, list[str], str | None]:
        if visibility != "public":
            return (
                "internal",
                "exclude",
                "Target non exposé comme commande publique.",
                ["make target visibility = internal"],
                None,
            )

        if target.startswith(("require-", "exec-")) or target in {"env-check-base", "env-check-local", "backup-dir"}:
            return (
                "internal",
                "exclude",
                "Helper interne ou garde-fou auxiliaire non retenu dans la référence utilisateur.",
                ["target classified as helper/internal make guard"],
                "Makefile",
            )

        declared = application_declarations.get(target)
        if declared is not None:
            return (
                "application-public",
                declared.documentation_policy,
                None,
                [f"declared in {declared.source}"],
                declared.source,
            )

        manifest_targets = template_manifest.get("targets", {})
        manifest_entry = manifest_targets.get(target)
        signature = self._make_target_signature(
            target=target,
            prerequisites=prerequisites,
            body=body,
            help_text=help_text,
        )
        if manifest_entry is not None:
            provenance = (
                "app-template"
                if local_origin_manifest is not None
                else "template-standard"
            )
            evidence = [
                f"declared in {template_manifest.get('source')}",
                f"origin={manifest_entry.get('origin', provenance)}",
            ]
            if signature == manifest_entry.get("signature"):
                evidence.insert(
                    0,
                    f"signature matches {template_manifest.get('source')}",
                )
            elif local_origin_manifest is not None:
                evidence.insert(
                    0,
                    "target is publicly declared by the local template manifest",
                )
            else:
                evidence.insert(
                    0,
                    "public interface matches bundled template-standard command metadata",
                )
            return (
                provenance,
                manifest_entry.get(
                    "documentation_policy",
                    "main-reference",
                ),
                None,
                evidence,
                template_manifest.get("source"),
            )

        normalized_help = (help_text or "").casefold()
        if "compatibilité" in normalized_help or "compatibility" in normalized_help:
            return (
                "legacy",
                "exclude",
                "Alias ou compatibilité historique non retenu dans la référence principale.",
                ["help text marks compatibility alias"],
                "Makefile",
            )

        return (
            "unknown",
            "exclude",
            "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
            ["no template signature match", "no application declaration"],
            template_manifest.get("source"),
        )

    @staticmethod
    def _make_target_signature(
        *,
        target: str,
        prerequisites: list[str],
        body: list[str],
        help_text: str | None,
    ) -> str:
        payload = json.dumps(
            {
                "target": target,
                "prerequisites": prerequisites,
                "body": body,
                "help_text": help_text,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _analyze_environment_variables(
        self,
        project: Project,
        environments: ProjectEnvironmentsFacts,
    ) -> EnvironmentVariablesFacts:
        variables: dict[str, EnvironmentVariableFacts] = {}

        def upsert(
            name: str,
            *,
            scope: str,
            environments: list[str],
            required: bool | None,
            required_by_environment: dict[str, bool] | None,
            sensitive: bool,
            default_value: str | None,
            description: str | None,
            comment: str | None,
            source: str,
            environment_value: EnvironmentVariableValueFacts | None = None,
        ) -> None:
            item = variables.get(name)
            if item is None:
                item = EnvironmentVariableFacts(
                    name=name,
                    scope=scope,
                    required=required,
                    sensitive=sensitive,
                    default_value=default_value,
                    description=description,
                    comment=comment,
                )
                variables[name] = item

            item.scope = self._merge_scope(item.scope, scope)
            self._extend_unique(item.environments, environments)
            self._extend_unique(item.sources, [source])
            item.sensitive = item.sensitive or sensitive
            if item.required is None:
                item.required = required
            elif required is True:
                item.required = True
            if item.default_value is None:
                item.default_value = default_value
            elif item.default_value != default_value and default_value is not None:
                item.default_value = None
            if item.description is None:
                item.description = description
            if item.comment is None:
                item.comment = comment
            if required_by_environment:
                item.required_by_environment.update(required_by_environment)
            if environment_value is not None:
                if not any(
                    existing.environment == environment_value.environment
                    and existing.source == environment_value.source
                    and existing.value == environment_value.value
                    for existing in item.values
                ):
                    item.values.append(environment_value)

        env_file_map = {
            ".env": self._environment_names_for_env_file(project.root / ".env"),
            ".env.dev": ["dev"],
            ".env.prod": ["prod"],
            ".env.template.example": ["dev", "prod"],
        }

        for relative_path, env_names in env_file_map.items():
            if not env_names:
                continue
            path = project.root / relative_path
            if not path.is_file():
                continue
            entries = self._read_env_entries(path)
            for entry in entries:
                for env_name in env_names:
                    env_value = EnvironmentVariableValueFacts(
                        environment=env_name,
                        value=None if self._is_sensitive_name(entry["key"]) else entry["value"],
                        source=relative_path,
                        comment=entry["comment"],
                    )
                    upsert(
                        entry["key"],
                        scope="shared",
                        environments=[env_name],
                        required=False if entry["value"] is not None else None,
                        required_by_environment={env_name: False if entry["value"] is not None else False},
                        sensitive=self._is_sensitive_name(entry["key"]),
                        default_value=(entry["value"] if len(env_names) == 1 and not self._is_sensitive_name(entry["key"]) else None),
                        description=self._describe_variable(entry["key"]),
                        comment=entry["comment"],
                        source=relative_path,
                        environment_value=env_value,
                    )

        settings_path = self._find_django_settings_path(project)
        settings_source = self._relative_project_path(project, settings_path)
        for getenv in self._extract_getenv_calls(settings_path):
            upsert(
                getenv["name"],
                scope="backend",
                environments=["dev", "prod"],
                required=False if getenv["default"] is not None else True,
                required_by_environment={"dev": False if getenv["default"] is not None else True, "prod": False if getenv["default"] is not None else True},
                sensitive=self._is_sensitive_name(getenv["name"]),
                default_value=(getenv["default"] if not self._is_sensitive_name(getenv["name"]) else None),
                description=self._describe_variable(getenv["name"]),
                comment=None,
                source=settings_source,
            )

        for api_source in self._frontend_source_files(project, names=("api",)):
            relative_source = self._relative_project_path(project, api_source)
            for name in self._extract_import_meta_env(api_source):
                upsert(
                    name,
                    scope="frontend",
                    environments=["dev", "prod"],
                    required=False,
                    required_by_environment={"dev": False, "prod": False},
                    sensitive=self._is_sensitive_name(name),
                    default_value=None,
                    description=self._describe_variable(name),
                    comment=None,
                    source=relative_source,
                )

        script_path = project.root / "scripts" / "generate-env.sh"
        for name in self._extract_local_key_names(script_path):
            upsert(
                name,
                scope="ops",
                environments=["dev", "prod"],
                required=True,
                required_by_environment={"dev": True, "prod": True},
                sensitive=self._is_sensitive_name(name),
                default_value=None,
                description=self._describe_variable(name),
                comment=None,
                source=self._relative_project_path(project, script_path),
            )

        compose_requirements = self._compose_variable_requirements(project, environments)
        for environment in environments.items:
            for service in environment.services:
                for name in service.env_variables:
                    required = compose_requirements.get(name, {}).get(environment.name)
                    upsert(
                        name,
                        scope=service.role or "shared",
                        environments=[environment.name],
                        required=required,
                        required_by_environment={environment.name: required if required is not None else False},
                        sensitive=self._is_sensitive_name(name),
                        default_value=None,
                        description=self._describe_variable(name),
                        comment=None,
                        source=service.source,
                    )

        result = list(variables.values())
        for item in result:
            item.values.sort(key=lambda value: (value.environment, value.source))
            if item.default_value is None and len({(value.environment, value.value) for value in item.values if value.value is not None}) == 1:
                only = next((value.value for value in item.values if value.value is not None), None)
                item.default_value = only
        result.sort(key=lambda item: item.name)
        return EnvironmentVariablesFacts(variables=result)

    def _analyze_django(
        self,
        project: Project,
        *,
        api: ApiFacts,
        operational_commands: OperationalCommandsFacts,
    ) -> DjangoFacts:
        settings_path = self._find_django_settings_path(project)
        settings_relative = self._relative_project_path(project, settings_path)
        settings_text = self._read_text(settings_path)
        settings_module = self._path_to_module(settings_path, project.root / "backend")
        urlconf_module = self._extract_root_urlconf_module(settings_path) or self._manage_default_urlconf(project)
        urls_path = self._module_to_project_path(project, urlconf_module)
        urls_relative = self._relative_project_path(project, urls_path)
        app_source_dir = urls_path.parent if urls_path is not None else settings_path.parent
        models_path = self._find_backend_file(project, "models.py")
        views_paths = self._find_backend_files(project, prefix="views")
        api_urls_path = self._find_backend_file(project, "urls.py", preferred_subdir="api")
        ensure_admin_path = self._find_backend_file(project, "ensure_admin.py")

        installed_apps = self._parse_installed_apps(settings_path)
        local_apps = [
            app_name
            for app_name in installed_apps
            if (project.root / "backend" / app_name).exists()
        ]
        auth_mechanisms = []
        permissions = []
        views_text = "\n".join(self._read_text(path) for path in views_paths)

        if "JWTAuthentication" in settings_text:
            auth_mechanisms.append("JWT")
        if api_urls_path and "TokenObtainPairView" in self._read_text(api_urls_path):
            auth_mechanisms.append("SimpleJWT")
        if any("Authorization" in self._read_text(path) and "Bearer" in self._read_text(path) for path in self._frontend_source_files(project, names=("api",))):
            auth_mechanisms.append("Bearer token")

        for permission in ("IsAuthenticated", "IsAdminUser", "AllowAny"):
            if permission in views_text or permission in settings_text:
                permissions.append(permission)

        model_schemas = self._parse_django_model_schemas(models_path)
        models = [
            DjangoModelFacts(
                name=model.name,
                fields=[field.name for field in model.fields],
                source=model.source,
            )
            for model in model_schemas
        ]
        migration_commands = [
            item.command
            for item in operational_commands.commands
            if item.category == "migrations"
        ]
        create_admin_commands = []
        if ensure_admin_path.is_file():
            create_admin_commands.append("python manage.py ensure_admin")
        if any(command.name == "createsuperuser" for command in operational_commands.commands):
            create_admin_commands.append("make createsuperuser")

        database_engines = self._extract_database_engines(settings_path)
        runtime_engines = [item.engine for item in database_engines if "test" not in item.context.casefold()]
        database_engine = runtime_engines[0] if runtime_engines else (database_engines[0].engine if database_engines else None)
        database_configuration = []
        for name in ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST", "POSTGRES_PORT"):
            if name in settings_text:
                database_configuration.append(name)

        view_details = self._collect_view_details(views_paths)
        resolved_routes, endpoints = self._build_django_routes_and_endpoints(
            project=project,
            api=api,
            view_details=view_details,
            auth_mechanisms=sorted(set(auth_mechanisms)),
            frontend_method_sources=self._frontend_methods_by_path(project),
        )
        admin_enabled = (
            "django.contrib.admin" in installed_apps
            and any((route.full_path == "/admin/" or route.relative_path == "admin/") and (route.view or "") == "admin.site.urls" for route in resolved_routes)
        )
        source_paths = [
            self._relative_project_path(project, candidate)
            for candidate in [settings_path, urls_path, api_urls_path, models_path, *views_paths, ensure_admin_path]
            if candidate is not None and candidate.is_file()
        ]

        return DjangoFacts(
            project_module=app_source_dir.name if app_source_dir else None,
            settings_module=settings_module,
            urlconf_module=urlconf_module,
            settings_files=[settings_relative] if settings_relative else [],
            installed_apps=installed_apps,
            local_apps=local_apps,
            models=models,
            model_schemas=model_schemas,
            routes=sorted({route.path for route in api.routes}),
            resolved_routes=resolved_routes,
            endpoints=endpoints,
            routers=sorted(registration.prefix for registration in api.router_registrations),
            auth_mechanisms=sorted(set(auth_mechanisms)),
            permissions=sorted(set(permissions)),
            admin_enabled=admin_enabled,
            migration_commands=sorted(set(migration_commands)),
            create_admin_commands=sorted(set(create_admin_commands)),
            database_engine=database_engine,
            database_engines=database_engines,
            database_configuration=database_configuration,
            source_paths=source_paths,
        )

    def _analyze_react(
        self,
        project: Project,
    ) -> ReactFacts:
        package_path = project.root / "frontend" / "package.json"
        package_data = self._read_json(package_path)
        scripts = package_data.get("scripts", {}) if isinstance(package_data, dict) else {}
        source_files = self._frontend_source_files(project)
        text_by_file = {
            self._relative_project_path(project, source): self._read_text(source)
            for source in source_files
        }
        combined_text = "\n".join(text_by_file.values())

        navigation_items = sorted({
            match.group(1).strip()
            for text in text_by_file.values()
            for match in re.finditer(r">([^<>{}][^<]{1,80})<", text)
            if any(keyword in match.group(1) for keyword in ("Connexion", "Catég", "Sauvegarde", "Vérif", "Recherche", "Thème", "Utilisateurs", "Aide", "Exporter", "Importer", "Génér", "Coffre"))
        })
        pages = sorted({
            match.group(1).strip()
            for text in text_by_file.values()
            for match in re.finditer(r"<h[1-3][^>]*>([^<]+)</h[1-3]>", text)
        })
        forms = self._extract_react_forms(source_files)
        routes = self._extract_react_routes(source_files)
        api_calls = self._extract_frontend_api_calls_from_files(source_files)
        user_features = self._extract_react_user_features(
            source_files=source_files,
            routes=routes,
            api_calls=api_calls,
        )
        auth_mechanisms = []
        if "Authorization" in combined_text and "Bearer" in combined_text:
            auth_mechanisms.append("JWT Bearer côté frontend")
        if "localStorage" in combined_text:
            auth_mechanisms.append("Session locale dans localStorage")
        if "sessionStorage" in combined_text:
            auth_mechanisms.append("Session locale dans sessionStorage")
        if any(token in combined_text for token in ("decryptPayload", "decryptPrivateFields", "ensureKeyPair", "encryptPayload")):
            auth_mechanisms.append("Déverrouillage local du coffre privé")

        crypto_file = self._find_react_crypto_file(source_files)
        app_path = self._find_react_app_file(source_files)
        crypto = self._analyze_react_crypto(
            crypto_path=crypto_file,
            app_path=app_path,
        )

        env_names = sorted({
            name
            for source in source_files
            for name in self._extract_import_meta_env(source)
        })
        relevant_sources = [
            self._relative_project_path(project, package_path),
            *text_by_file.keys(),
            self._relative_project_path(project, project.root / "frontend" / "vite.config.js") if (project.root / "frontend" / "vite.config.js").is_file() else None,
        ]
        relevant_sources = [item for item in relevant_sources if item]

        return ReactFacts(
            entry_point=self._relative_project_path(project, app_path) if app_path and app_path.is_file() else None,
            routes=routes or ["/"],
            pages=pages,
            navigation_items=navigation_items,
            forms=forms,
            user_features=user_features,
            api_calls=api_calls,
            environment_variables=env_names,
            auth_mechanisms=auth_mechanisms,
            scripts={str(key): str(value) for key, value in scripts.items() if isinstance(key, str) and isinstance(value, str)},
            dev_command=("npm run dev" if "dev" in scripts else None),
            build_command=("npm run build" if "build" in scripts else None),
            crypto=crypto,
            source_paths=sorted(dict.fromkeys(relevant_sources)),
        )

    def _analyze_capabilities(
        self,
        django: DjangoFacts,
        react: ReactFacts,
    ) -> CapabilitiesFacts:
        capabilities: list[CapabilityFacts] = []
        by_label: dict[str, CapabilityFacts] = {}

        def add(
            label: str,
            *evidence: str,
            status: str = "derived",
            component: str | None = None,
            endpoint: str | None = None,
            permission_condition: str | None = None,
            confidence: str | None = None,
        ) -> None:
            existing = by_label.get(label)
            if existing is not None:
                existing.evidence = list(dict.fromkeys([*existing.evidence, *evidence]))
                if existing.endpoint is None:
                    existing.endpoint = endpoint
                if existing.component is None:
                    existing.component = component
                if existing.permission_condition is None:
                    existing.permission_condition = permission_condition
                if existing.confidence != "high" and confidence == "high":
                    existing.confidence = confidence
                if existing.status != "detected" and status == "detected":
                    existing.status = status
                return
            capability = CapabilityFacts(
                identifier=re.sub(r"[^a-z0-9]+", "-", label.casefold()).strip("-") or None,
                label=label,
                status=status,
                audience="administrator" if permission_condition == "IsAdminUser" else "user",
                evidence=list(dict.fromkeys(evidence)),
                component=component,
                endpoint=endpoint,
                permission_condition=permission_condition,
                confidence=confidence,
            )
            by_label[label] = capability
            capabilities.append(capability)

        if any(route.full_path and "auth/jwt/create" in route.full_path for route in django.resolved_routes):
            add(
                "S’authentifier à l’application",
                *[route.full_path for route in django.resolved_routes if route.full_path and "auth/jwt/create" in route.full_path],
                status="derived",
                endpoint="/api/auth/jwt/create/",
                confidence="high",
            )

        if react.crypto.detected:
            add(
                "Gérer un coffre local chiffré côté client",
                *react.crypto.source_paths,
                status="detected",
                component="frontend",
                confidence="medium",
            )

        for feature in react.user_features:
            add(
                feature.label,
                *(feature.evidence + feature.routes + feature.api_calls),
                status=feature.status,
                component=feature.component,
                endpoint=(feature.api_calls[0].split(" ", 1)[1] if feature.api_calls else (feature.routes[0] if feature.routes else None)),
                confidence=feature.confidence,
            )

        frontend_components = {path.split("/")[-1].removesuffix(".jsx") for path in react.source_paths}
        resource_labels = {
            "Category": "catégories",
            "PasswordEntry": "entrées de mots de passe",
            "SecretBundle": "secrets applicatifs",
            "User": "utilisateurs",
            "Contact": "contacts",
            "Calendar": "calendriers",
            "Event": "événements",
        }
        action_labels = {
            "GET": "Consulter",
            "POST": "Créer",
            "PUT": "Modifier",
            "PATCH": "Modifier",
            "DELETE": "Supprimer",
        }

        for endpoint in django.endpoints:
            if endpoint.resolution_status != "resolved" or not endpoint.path:
                continue
            model_name = self._model_name_from_endpoint(endpoint, django.models)
            if model_name is None:
                continue
            resource_label = resource_labels.get(model_name, self._humanize_model_name(model_name))
            permission = endpoint.permissions[0] if endpoint.permissions else None
            for method in endpoint.methods:
                verb = action_labels.get(method)
                if verb is None:
                    continue
                component = self._component_for_endpoint(endpoint.path, frontend_components)
                action_label = {
                    "Consulter": f"Consulter les {resource_label}",
                    "Créer": f"Créer des {resource_label}",
                    "Modifier": f"Modifier des {resource_label}",
                    "Supprimer": f"Supprimer des {resource_label}",
                }[verb]
                add(
                    action_label,
                    endpoint.path,
                    model_name,
                    *(react.api_calls if any(self._endpoint_matches_api_call(endpoint.path, api_call) and api_call.startswith(method) for api_call in react.api_calls) else []),
                    status="derived",
                    component=component,
                    endpoint=endpoint.path,
                    permission_condition=permission,
                    confidence="medium" if not react.api_calls else "high",
                )

        capabilities.sort(key=lambda item: item.label)
        return CapabilitiesFacts(capabilities=capabilities)

    def _merge_architecture_context(
        self,
        environments: ProjectEnvironmentsFacts,
        architecture: ArchitectureFacts,
        deployment: DeploymentFacts,
    ) -> None:
        command_names = {
            item
            for item in deployment.make_targets
        }
        for environment in environments.items:
            if not environment.available_commands:
                environment.available_commands = sorted(
                    command_names
                )
            self._extend_unique(
                environment.source_paths,
                [
                    *environment.env_files,
                    environment.compose_file,
                ],
            )

    def _attach_commands_to_environments(
        self,
        environments: ProjectEnvironmentsFacts,
        operational_commands: OperationalCommandsFacts,
    ) -> None:
        env_map = {
            item.name: item
            for item in environments.items
        }

        for command in operational_commands.commands:
            target_envs = command.environments or [
                "dev",
                "prod",
            ]
            for env_name in target_envs:
                env = env_map.get(env_name)
                if env is None:
                    continue
                if command.command not in env.available_commands:
                    env.available_commands.append(
                        command.command
                    )

        for env in env_map.values():
            env.available_commands.sort()

    @staticmethod
    def _environment_name(
        compose_file: str,
    ) -> str:
        lowered = compose_file.casefold()
        if ".dev." in lowered:
            return "dev"
        if ".prod." in lowered:
            return "prod"
        return "common"

    @staticmethod
    def _service_role(
        service_name: str,
        definition: dict[str, Any],
    ) -> str:
        lowered = service_name.casefold()
        image = str(
            definition.get("image", "")
        ).casefold()
        command = str(
            definition.get("command", "")
        ).casefold()
        if "postgres" in lowered or "postgres" in image or lowered == "db":
            return "database"
        if "frontend" in lowered or "vite" in command:
            return "frontend"
        if "backend" in lowered or "manage.py" in command:
            return "backend"
        return "service"

    @staticmethod
    def _build_context(value: Any) -> str | None:
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            context = value.get("context")
            if context is not None:
                return str(context)
        return None

    @staticmethod
    def _command_string(value: Any) -> str | None:
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return " ".join(
                str(item) for item in value
            )
        return None

    @staticmethod
    def _list_value(value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, dict):
            return [str(item) for item in value]
        if isinstance(value, str):
            return [value]
        return []

    @staticmethod
    def _depends_on(value: Any) -> list[str]:
        if isinstance(value, dict):
            return [str(item) for item in value]
        if isinstance(value, list):
            return [str(item) for item in value]
        return []

    @staticmethod
    def _healthchecks(value: Any) -> list[str]:
        if isinstance(value, dict):
            test = value.get("test")
            if isinstance(test, list):
                return [str(item) for item in test]
            if isinstance(test, str):
                return [test]
            return ["defined"]
        return []

    @staticmethod
    def _label_list(value: Any) -> list[str]:
        if isinstance(value, dict):
            return [
                f"{key}={value[key]}"
                for key in value
            ]
        if isinstance(value, list):
            return [str(item) for item in value]
        return []

    @staticmethod
    def _hosts_from_labels(
        labels: list[str],
    ) -> set[str]:
        hosts: set[str] = set()
        for label in labels:
            for match in re.finditer(
                r"Host\(`([^`]+)`\)",
                label,
            ):
                hosts.add(match.group(1))
        return hosts

    @staticmethod
    def _exposed_ports(value: Any) -> list[str]:
        ports = DjangoReactApplicationAnalyzer._list_value(
            value
        )
        result: list[str] = []
        for item in ports:
            if ":" in item:
                result.append(item.rsplit(":", 1)[-1])
            else:
                result.append(item)
        return result

    def _env_names_from_definition(
        self,
        definition: Any,
    ) -> set[str]:
        names: set[str] = set()
        serialized = json.dumps(
            definition,
            ensure_ascii=False,
        )
        for match in PLACEHOLDER_PATTERN.finditer(
            serialized
        ):
            names.add(match.group(1))
        return names

    def _env_names_from_files(
        self,
        root: Path,
        env_files: list[str],
    ) -> set[str]:
        return set(
            self._env_defaults_from_files(
                root,
                env_files,
            )
        )

    def _normalized_env_files(
        self,
        root: Path,
        env_files: list[str],
        environment: str,
    ) -> list[str]:
        items = list(env_files)
        alias = f".env.{environment}"
        if (
            ".env" in items
            and (root / alias).is_file()
            and alias not in items
        ):
            items.append(alias)
        return items

    def _compose_interpolation_env_files(
        self,
        root: Path,
        environment: str,
    ) -> list[str]:
        candidates = [".env", f".env.{environment}"]
        return [
            candidate
            for candidate in candidates
            if (root / candidate).is_file()
        ]
    def _env_defaults_from_files(
        self,
        root: Path,
        env_files: list[str],
    ) -> dict[str, str]:
        values: dict[str, str] = {}
        for env_file in env_files:
            path = root / env_file
            if (
                path.name.endswith(".local")
                or not path.is_file()
            ):
                continue
            for key, default in self._read_env_keys(path):
                if default is not None:
                    values[key] = default
        return values

    def _resolve_host_placeholders(
        self,
        hosts: set[str],
        root: Path,
        env_files: list[str],
    ) -> set[str]:
        resolved: set[str] = set()
        values = self._env_defaults_from_files(
            root,
            env_files,
        )
        for host in hosts:
            match = re.fullmatch(
                r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}",
                host,
            )
            if match:
                replacement = values.get(match.group(1))
                resolved.add(replacement or host)
                continue
            resolved.add(host)
        return resolved

    @staticmethod
    def _extract_make_help_entries(
        lines: list[str],
    ) -> dict[str, str]:
        entries: dict[str, str] = {}
        for line in lines:
            match = re.match(r"^([a-zA-Z0-9_-]+):(?:[^#]|#(?!#))*##\s*(.+)$", line)
            if not match:
                continue
            entries[match.group(1).strip()] = match.group(2).strip()
        return entries

    @staticmethod
    def _extract_declared_make_variables(
        lines: list[str],
    ) -> set[str]:
        variables: set[str] = {"MAKE", "MAKEFILE_LIST", "CURDIR", "SHELL"}
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            match = re.match(r"^([A-Z_][A-Z0-9_]*)\s*[:?+]?=", stripped)
            if match:
                variables.add(match.group(1))
        return variables

    @staticmethod
    def _extract_phony_targets(
        lines: list[str],
    ) -> set[str]:
        targets: set[str] = set()
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith(".PHONY:"):
                continue
            _, _, remainder = stripped.partition(":")
            targets.update(item for item in remainder.strip().split() if item)
        return targets

    def _build_make_parameters(
        self,
        *,
        target: str,
        body: list[str],
        help_entries: dict[str, str],
        declared_variables: set[str],
    ) -> list[OperationalCommandParameterFacts]:
        parameters: dict[str, OperationalCommandParameterFacts] = {}
        help_text = help_entries.get(target, "")
        for param, example in re.findall(r"([A-Z_]+)=([^\s)]+)", help_text):
            parameters[param] = OperationalCommandParameterFacts(
                name=param,
                required=False,
                example=example,
                description=help_text,
                origin="user-documented",
                source="Makefile",
            )

        for line in body:
            for param in re.findall(r"\$\(([A-Z_]+)\)", line):
                if param.endswith("_DIR"):
                    continue
                if param in {"MAKE", "MAKEFILE_LIST", "CURDIR", "SHELL", "APP_ENV", "COMPOSE"}:
                    continue
                if param in declared_variables and not self._is_probable_user_make_parameter(line, param):
                    continue
                if param not in parameters and self._is_probable_user_make_parameter(line, param):
                    parameters[param] = OperationalCommandParameterFacts(
                        name=param,
                        required=f'"$({param})"' not in line and f'$({param})' in line,
                        example=None,
                        description=None,
                        origin="user-exposed",
                        source="Makefile",
                    )
                elif param in parameters and f'"$({param})"' in line:
                    parameters[param].required = False

        result = list(parameters.values())
        result.sort(key=lambda item: item.name)
        return result

    @staticmethod
    def _is_probable_user_make_parameter(
        line: str,
        param: str,
    ) -> bool:
        if param in {"FILE", "SERVICE", "TREE_IGNORE", "BACKUP", "OUT", "FORCE", "INIT_DEV_SSH", "INIT_DEV_REMOTE_DIR", "INIT_DEV_REMOTE_FILE"}:
            return True
        return any(
            snippet in line
            for snippet in (
                f'"$({param})"',
                f'[ -n "$({param})" ]',
                f'$({param})"',
                f'"$({param})',
            )
        )

    @staticmethod
    def _infer_command_category(
        target: str,
        prerequisites: list[str],
        body: list[str],
    ) -> str:
        lowered = target.casefold()
        joined = " ".join(body).casefold()
        if "test" in lowered or "manage.py test" in joined or "npm run test" in joined:
            return "tests"
        if "backup" in lowered:
            return "backup"
        if "restore" in lowered:
            return "restore"
        if any(part in lowered for part in ("up", "start")):
            return "startup"
        if any(part in lowered for part in ("down", "stop")):
            return "shutdown"
        if "restart" in lowered:
            return "restart"
        if "log" in lowered:
            return "logs"
        if "migrat" in lowered or "createsuperuser" in lowered:
            return "migrations"
        if "env" in lowered:
            return "environment"
        if prerequisites and not body:
            return "alias"
        return "other"

    def _analyze_scripts(
        self,
        project: Project,
    ) -> list[ScriptAnalysisFacts]:
        script_paths = [
            "scripts/init.sh",
            "scripts/env-switch.sh",
            "scripts/generate-env.sh",
            "scripts/generate-secrets.sh",
            "scripts/migrate.sh",
            "scripts/backup-db.sh",
            "scripts/restore-db.sh",
            "scripts/update.sh",
            "scripts/check-invariants.sh",
            "scripts/docforge-project-metadata.py",
            "backend/entrypoint.sh",
        ]
        scripts: list[ScriptAnalysisFacts] = []
        for relative_path in script_paths:
            path_obj = project.root / relative_path
            if not path_obj.is_file():
                continue
            scripts.append(
                self._analyze_script(
                    project=project,
                    relative_path=relative_path,
                )
            )
        scripts.sort(key=lambda item: item.path)
        return scripts

    def _analyze_script(
        self,
        *,
        project: Project,
        relative_path: str,
    ) -> ScriptAnalysisFacts:
        path = project.root / relative_path
        text = self._read_text(path)
        lines = text.splitlines()
        facts = ScriptAnalysisFacts(
            name=Path(relative_path).stem,
            path=relative_path,
            source=relative_path,
        )

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if "check-invariants.sh" in stripped:
                facts.validations.append(stripped)
            if stripped.startswith("[") and "||" in stripped:
                facts.validations.append(stripped)
            if "docker compose" in stripped:
                facts.compose_commands.append(stripped)
            if "python manage.py" in stripped:
                facts.django_commands.extend(
                    re.findall(
                        r"python manage\.py [A-Za-z0-9_:-]+",
                        stripped,
                    )
                )
            if stripped.startswith("./scripts/"):
                facts.shell_commands.append(stripped)

        facts.failure_conditions.extend(
            re.findall(r'err\("([^"]+)"\)', text)
        )
        facts.failure_conditions.extend(
            re.findall(r'fail\("([^"]+)"\)', text)
        )
        facts.failure_conditions.extend(
            re.findall(r'echo "Erreur ?:([^"]+)"', text)
        )

        for source, destination in re.findall(
            r"ln -sf\s+([^\s]+)\s+([^\s]+)",
            text,
        ):
            facts.symlinks.append(
                f"{destination} -> {source}"
            )

        for created_file in re.findall(
            r"cat >\s+([^\s]+)\s+<<EOF",
            text,
        ):
            facts.creates_files.append(created_file)

        if relative_path == "scripts/init.sh" and "generate-env.sh" in text:
            facts.generated_secrets.extend(
                self._extract_local_key_names(
                    project.root / "scripts" / "generate-env.sh"
                )
            )
            facts.notes.append(
                "Le script initialise l’environnement actif, valide les invariants et démarre les services manquants si nécessaire."
            )
            if "DOCFORGE_INIT_APPLICATION" in text:
                facts.metadata_actions.append(
                    "Matérialise docforge.project.json uniquement lorsque DOCFORGE_INIT_APPLICATION=1 est fourni."
                )
            if "DOCFORGE_DETACH_GIT" in text:
                facts.metadata_actions.append(
                    "Peut détacher explicitement l’historique Git lorsque DOCFORGE_DETACH_GIT=1 est fourni."
                )
            if "DOCFORGE_SKIP_STARTUP" in text:
                facts.metadata_actions.append(
                    "Permet d’ignorer le démarrage Docker Compose avec DOCFORGE_SKIP_STARTUP=1 dans un contexte de test ou de maintenance."
                )
        if relative_path == "scripts/env-switch.sh":
            facts.environment_targets = ["dev", "prod"]
            facts.notes.append(
                "Le choix d’environnement repose sur un lien symbolique .env."
            )
        if relative_path == "scripts/generate-env.sh":
            facts.creates_files.extend([".env.dev", ".env.prod", ".env.local"])
            facts.notes.append(
                "Le script génère les fichiers d’environnement dérivés et prépare les variables d’identité et d’administration."
            )
        if relative_path == "scripts/generate-secrets.sh":
            facts.notes.append(
                "Le script génère ou complète les secrets locaux dérivés du template."
            )
        if relative_path == "scripts/migrate.sh":
            facts.environment_targets = ["dev", "prod"]
            facts.notes.append(
                "Le script exécute les migrations dans l’environnement pointé par .env."
            )
        if relative_path == "scripts/backup-db.sh":
            facts.database_engine = "PostgreSQL"
            facts.backup_destination = "./backup"
            facts.backup_format = "sql"
            facts.compression = "gzip"
        if relative_path == "scripts/restore-db.sh":
            facts.database_engine = "PostgreSQL"
            facts.backup_destination = "./backup"
            facts.backup_format = "sql"
            facts.compression = "gzip"
            facts.auto_select_latest = "ls -1t" in text
            facts.confirmation_required = "read -r -p" in text
            if "DROP SCHEMA" in text:
                facts.destructive_actions.append(
                    "Réinitialise le schéma public avant import."
                )
        if relative_path == "backend/entrypoint.sh":
            if "collectstatic" in text:
                facts.notes.append(
                    "Collecte les fichiers statiques en production."
                )
        if relative_path == "scripts/check-invariants.sh":
            facts.metadata_actions.extend(
                [
                    "Valide l’état des métadonnées DocForge via scripts/docforge-project-metadata.py validate.",
                    "Peut exiger un état application matérialisé avec --expect-application.",
                ]
            )
            if "placeholder" in text.casefold():
                facts.notes.append(
                    "Le contrôle bloque si des placeholders connus subsistent après matérialisation."
                )
        if relative_path == "scripts/docforge-project-metadata.py":
            facts.creates_files.append(self.LOCAL_PROJECT_METADATA_FILE)
            facts.destructive_actions.append(
                "Peut supprimer l’historique Git local puis réinitialiser un nouveau dépôt Git lorsqu’il est appelé avec --detach-git."
            )
            facts.metadata_actions.extend(
                [
                    "Transforme docforge.template.json en docforge.project.json lors de la matérialisation.",
                    "Conserve origin_template_id et template_version dans les métadonnées de l’application générée.",
                    "Refuse la coexistence ambiguë de docforge.template.json et docforge.project.json.",
                ]
            )
            facts.placeholders_replaced.extend(["__APP_NAME__", "__APP_SLUG__"])
            facts.notes.append(
                "Le script remplace les placeholders textuels connus, valide les identifiants requis et protège le dépôt source contre un détachement Git accidentel."
            )

        facts.compose_commands = list(dict.fromkeys(facts.compose_commands))
        facts.django_commands = list(dict.fromkeys(facts.django_commands))
        facts.shell_commands = list(dict.fromkeys(facts.shell_commands))
        facts.validations = list(dict.fromkeys(facts.validations))
        facts.failure_conditions = list(dict.fromkeys(facts.failure_conditions))
        facts.creates_files = list(dict.fromkeys(facts.creates_files))
        facts.symlinks = list(dict.fromkeys(facts.symlinks))
        facts.generated_secrets = list(dict.fromkeys(facts.generated_secrets))
        facts.metadata_actions = list(dict.fromkeys(facts.metadata_actions))
        facts.placeholders_replaced = list(dict.fromkeys(facts.placeholders_replaced))
        return facts

    def _extract_database_engines(
        self,
        path: Path,
    ) -> list[DatabaseEngineFacts]:
        try:
            tree = ast.parse(
                path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            )
        except (OSError, SyntaxError):
            return []

        engines: list[DatabaseEngineFacts] = []
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "DATABASES":
                        engine = self._extract_database_engine_from_node(node.value)
                        if engine:
                            engines.append(
                                DatabaseEngineFacts(
                                    engine=engine,
                                    context="default",
                                    source="backend/App/settings.py",
                                )
                            )
            if isinstance(node, ast.If):
                condition = self._expression_name(node.test) or "conditional"
                for context_name, body in (
                    (f"if:{condition}", node.body),
                    (f"else:{condition}", node.orelse),
                ):
                    for child in body:
                        if not isinstance(child, ast.Assign):
                            continue
                        for target in child.targets:
                            if isinstance(target, ast.Name) and target.id == "DATABASES":
                                engine = self._extract_database_engine_from_node(child.value)
                                if engine:
                                    engines.append(
                                        DatabaseEngineFacts(
                                            engine=engine,
                                            context=context_name,
                                            source="backend/App/settings.py",
                                        )
                                    )
        unique: dict[tuple[str, str], DatabaseEngineFacts] = {}
        for item in engines:
            unique[(item.engine, item.context)] = item
        return list(unique.values())

    def _extract_database_engine_from_node(
        self,
        node: ast.AST,
    ) -> str | None:
        if not isinstance(node, ast.Dict):
            return None
        for key, value in zip(node.keys, node.values):
            if not isinstance(key, ast.Constant) or key.value != "default":
                continue
            if not isinstance(value, ast.Dict):
                continue
            for sub_key, sub_value in zip(value.keys, value.values):
                if isinstance(sub_key, ast.Constant) and sub_key.value == "ENGINE":
                    return self._literal_string(sub_value)
        return None

    def _parse_django_model_schemas(
        self,
        path: Path,
    ) -> list[DjangoModelSchemaFacts]:
        try:
            tree = ast.parse(
                path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            )
        except (OSError, SyntaxError):
            return []

        schemas: list[DjangoModelSchemaFacts] = []
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if not any(
                isinstance(base, ast.Attribute)
                and base.attr == "Model"
                for base in node.bases
            ):
                continue
            choices_map = self._collect_text_choices(node)
            fields: list[DjangoModelFieldFacts] = []
            for item in node.body:
                if not isinstance(item, ast.Assign):
                    continue
                if len(item.targets) != 1 or not isinstance(item.targets[0], ast.Name):
                    continue
                if not isinstance(item.value, ast.Call):
                    continue
                call = item.value.func
                if not isinstance(call, ast.Attribute):
                    continue
                if not call.attr.endswith("Field") and call.attr != "ForeignKey":
                    continue
                name = item.targets[0].id
                kwargs = {
                    keyword.arg: keyword.value
                    for keyword in item.value.keywords
                    if keyword.arg is not None
                }
                blank = self._ast_bool(kwargs.get("blank"), False)
                nullable = self._ast_bool(kwargs.get("null"), False)
                default = self._ast_value_to_string(kwargs.get("default"))
                choices = self._extract_field_choices(
                    kwargs.get("choices"),
                    choices_map,
                )
                required = not blank and not nullable and default is None
                fields.append(
                    DjangoModelFieldFacts(
                        name=name,
                        field_type=call.attr,
                        required=required,
                        nullable=nullable,
                        blank=blank,
                        default=default,
                        choices=choices,
                        relation=self._expression_name(item.value.args[0]) if call.attr == "ForeignKey" and item.value.args else None,
                        unique=self._ast_bool(kwargs.get("unique"), False),
                        on_delete=self._expression_name(kwargs.get("on_delete")),
                        help_text=self._literal_string(kwargs.get("help_text")) if kwargs.get("help_text") is not None else None,
                        source="backend/api/models.py",
                    )
                )
            schemas.append(
                DjangoModelSchemaFacts(
                    name=node.name,
                    fields=fields,
                    source="backend/api/models.py",
                )
            )
        schemas.sort(key=lambda item: item.name)
        return schemas

    def _collect_text_choices(
        self,
        model_node: ast.ClassDef,
    ) -> dict[str, list[DjangoModelFieldChoiceFacts]]:
        choices: dict[str, list[DjangoModelFieldChoiceFacts]] = {}
        constants: dict[str, dict[str, str]] = {}
        for item in model_node.body:
            if not isinstance(item, ast.ClassDef):
                continue
            if not any(
                isinstance(base, ast.Attribute)
                and base.attr == "TextChoices"
                for base in item.bases
            ):
                continue
            values: list[DjangoModelFieldChoiceFacts] = []
            value_map: dict[str, str] = {}
            for sub_item in item.body:
                if not isinstance(sub_item, ast.Assign):
                    continue
                if len(sub_item.targets) != 1 or not isinstance(sub_item.targets[0], ast.Name):
                    continue
                target_name = sub_item.targets[0].id
                if not isinstance(sub_item.value, ast.Tuple) or len(sub_item.value.elts) < 1:
                    continue
                value = self._literal_string(sub_item.value.elts[0])
                label = self._literal_string(sub_item.value.elts[1]) if len(sub_item.value.elts) > 1 else None
                if value is None:
                    continue
                values.append(
                    DjangoModelFieldChoiceFacts(
                        value=value,
                        label=label,
                    )
                )
                value_map[target_name] = value
            choices[item.name] = values
            constants[item.name] = value_map
        self._latest_choice_constants = constants
        return choices

    def _extract_field_choices(
        self,
        node: ast.AST | None,
        choices_map: dict[str, list[DjangoModelFieldChoiceFacts]],
    ) -> list[DjangoModelFieldChoiceFacts]:
        if isinstance(node, ast.Attribute) and node.attr == "choices":
            owner = self._expression_name(node.value)
            if owner:
                return list(choices_map.get(owner, []))
        return []

    def _collect_view_details(
        self,
        views_paths: list[Path],
    ) -> dict[str, dict[str, Any]]:
        details: dict[str, dict[str, Any]] = {}
        for views_path in views_paths:
            try:
                tree = ast.parse(
                    views_path.read_text(
                        encoding="utf-8",
                        errors="ignore",
                    )
                )
            except (OSError, SyntaxError):
                continue

            source = views_path.as_posix().split("/backend/", 1)[-1] if "/backend/" in views_path.as_posix() else views_path.as_posix()
            if not source.startswith("backend/"):
                source = f"backend/{source.lstrip('/')}"
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    body_text = self._ast_text(node)
                    details[node.name] = {
                        "view": node.name,
                        "permissions": self._decorator_name_list(node.decorator_list, "permission_classes"),
                        "authentication": self._decorator_name_list(node.decorator_list, "authentication_classes"),
                        "methods": self._decorator_string_list(node.decorator_list, "api_view"),
                        "actions": [],
                        "ownership_controls": self._ownership_controls_from_text(body_text),
                        "data_controls": self._data_controls_from_text(body_text),
                        "custom_authentication": "_authenticate_" in body_text or "hmac.compare_digest" in body_text,
                        "source": source,
                    }
                if isinstance(node, ast.ClassDef):
                    permissions = []
                    authentication = []
                    methods: list[str] = []
                    actions: list[dict[str, Any]] = []
                    ownership_controls: list[str] = []
                    data_controls: list[str] = []
                    custom_authentication = False
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name) and target.id == "permission_classes":
                                    permissions = self._list_literal_names(item.value)
                                if isinstance(target, ast.Name) and target.id == "authentication_classes":
                                    authentication = self._list_literal_names(item.value)
                        if isinstance(item, ast.FunctionDef):
                            body_text = self._ast_text(item)
                            http_method = self._http_method_for_name(item.name)
                            if http_method:
                                methods.append(http_method)
                            action = self._extract_viewset_action(item)
                            if action is not None:
                                actions.append(action)
                            ownership_controls.extend(self._ownership_controls_from_text(body_text))
                            data_controls.extend(self._data_controls_from_text(body_text))
                            if "_authenticate_" in body_text or "hmac.compare_digest" in body_text:
                                custom_authentication = True
                    details[node.name] = {
                        "view": node.name,
                        "permissions": permissions,
                        "authentication": authentication,
                        "methods": list(dict.fromkeys(methods)),
                        "actions": actions,
                        "ownership_controls": list(dict.fromkeys(ownership_controls)),
                        "data_controls": list(dict.fromkeys(data_controls)),
                        "custom_authentication": custom_authentication,
                        "source": source,
                    }
        return details

    def _build_django_routes_and_endpoints(
        self,
        *,
        project: Project,
        api: ApiFacts,
        view_details: dict[str, dict[str, Any]],
        auth_mechanisms: list[str],
        frontend_method_sources: dict[str, list[str]],
    ) -> tuple[list[DjangoRouteFacts], list[DjangoEndpointFacts]]:
        mounts = self._extract_include_mounts(project)
        route_entries = list(api.routes)
        for registration in api.router_registrations:
            detail = view_details.get(registration.viewset.split(".")[-1], {})
            for action in detail.get("actions", []):
                if not action.get("detail"):
                    continue
                route_entries.append(
                    type(api.routes[0])(
                        path=f"/{registration.prefix.strip('/')}/{{id}}/{action['url_path']}/",
                        source=registration.source,
                        name=action["name"],
                        view=registration.viewset,
                        kind="router-action",
                        methods=action["methods"],
                    ) if api.routes else __import__('types').SimpleNamespace(
                        path=f"/{registration.prefix.strip('/')}/{{id}}/{action['url_path']}/",
                        source=registration.source,
                        name=action["name"],
                        view=registration.viewset,
                        kind="router-action",
                        methods=action["methods"],
                    )
                )

        resolved_routes: list[DjangoRouteFacts] = []
        endpoints: list[DjangoEndpointFacts] = []
        for route in route_entries:
            if route.view and str(route.view).startswith("include("):
                continue
            source_mounts = mounts.get(route.source, [{"mount_path": None, "source": route.source}])
            for mount in source_mounts:
                mount_path = mount.get("mount_path")
                relative_path = route.path.lstrip("/")
                full_path = self._combine_paths(mount_path, route.path) if mount_path else (route.path if route.source == mounts.get(route.source, [{}])[0].get("source") and route.source.endswith("urls.py") and route.path.startswith("/") and route.source == self._relative_backend_candidate(project, self._module_to_project_path(project, self._extract_root_urlconf_module(self._find_django_settings_path(project)) or self._manage_default_urlconf(project))) else None)
                resolution_status = "resolved" if full_path else "unresolved"
                sources = [mount.get("source") or route.source, route.source]
                methods = list(route.methods or frontend_method_sources.get(full_path or route.path, []))
                route_fact = DjangoRouteFacts(
                    relative_path=relative_path,
                    mount_path=mount_path,
                    full_path=full_path,
                    route_type=route.kind,
                    resolution_status=resolution_status,
                    name=route.name,
                    view=route.view,
                    methods=methods,
                    sources=list(dict.fromkeys([source for source in sources if source])),
                )
                resolved_routes.append(route_fact)
                view_name = self._clean_view_name(route.view)
                detail = view_details.get(view_name or "", {})
                permissions = list(detail.get("permissions", []))
                authentication = self._endpoint_authentication(
                    detail=detail,
                    permissions=permissions,
                    auth_mechanisms=auth_mechanisms,
                )
                endpoints.append(
                    DjangoEndpointFacts(
                        path=full_path,
                        relative_path=relative_path,
                        mount_path=mount_path,
                        resolution_status=resolution_status,
                        methods=methods,
                        view=view_name,
                        permissions=permissions,
                        authentication=authentication,
                        actions=[route.name] if route.kind == "router-action" and route.name else [],
                        route_parameters=self._route_parameters(full_path or route.path),
                        ownership_controls=list(detail.get("ownership_controls", [])),
                        data_controls=list(detail.get("data_controls", [])),
                        custom_authentication=bool(detail.get("custom_authentication")),
                        sources=list(dict.fromkeys([*route_fact.sources, detail.get("source")] if detail.get("source") else route_fact.sources)),
                    )
                )
        resolved_routes.sort(key=lambda item: ((item.full_path or item.relative_path), item.route_type))
        endpoints.sort(key=lambda item: ((item.path or item.relative_path), item.view or ""))
        return resolved_routes, endpoints

    def _extract_include_mounts(
        self,
        project: Project,
    ) -> dict[str, list[dict[str, str | None]]]:
        mounts: dict[str, list[dict[str, str | None]]] = {}
        url_files = [path for path in project.files if Path(path).name == "urls.py"]
        for relative_path in url_files:
            path = project.root / relative_path
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
            except (OSError, SyntaxError):
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                function_name = self._call_name(node.func)
                if function_name not in {"path", "re_path"} or len(node.args) < 2:
                    continue
                if not isinstance(node.args[1], ast.Call):
                    continue
                include_call = node.args[1]
                if self._call_name(include_call.func) != "include" or not include_call.args:
                    continue
                module_name = self._literal_string(include_call.args[0])
                target_file = self._module_to_urls_path(project, module_name) if module_name else None
                if target_file is None:
                    continue
                mount_path = self._literal_string(node.args[0])
                mounts.setdefault(target_file, []).append(
                    {
                        "mount_path": self._normalize_path(mount_path) if mount_path is not None else None,
                        "source": relative_path,
                    }
                )
        root_urlconf = self._module_to_project_path(project, self._extract_root_urlconf_module(self._find_django_settings_path(project)) or self._manage_default_urlconf(project))
        root_relative = self._relative_project_path(project, root_urlconf)
        if root_relative and root_relative not in mounts:
            mounts[root_relative] = [{"mount_path": None, "source": root_relative}]
        return mounts

    def _module_to_urls_path(
        self,
        project: Project,
        module_name: str | None,
    ) -> str | None:
        path = self._module_to_project_path(project, module_name)
        if path is None:
            return None
        return self._relative_project_path(project, path)

    @staticmethod
    def _combine_paths(
        mount_path: str | None,
        route_path: str,
    ) -> str | None:
        if mount_path is None:
            return None
        mount = mount_path.rstrip("/")
        route = route_path.lstrip("/")
        if not route:
            return mount + "/"
        return f"{mount}/{route}"

    @staticmethod
    def _endpoint_authentication(
        *,
        detail: dict[str, Any],
        permissions: list[str],
        auth_mechanisms: list[str],
    ) -> list[str]:
        explicit = list(detail.get("authentication", []))
        if explicit == [] and "AllowAny" in permissions:
            return []
        if explicit:
            return explicit
        if permissions:
            values = []
            if "JWT" in auth_mechanisms:
                values.append("JWT")
            if "Bearer token" in auth_mechanisms:
                values.append("Bearer token")
            return values
        return []

    @staticmethod
    def _route_parameters(path: str) -> list[str]:
        return re.findall(r"\{([^}]+)\}", path)

    def _frontend_methods_by_path(
        self,
        project: Project,
    ) -> dict[str, list[str]]:
        mapping: dict[str, list[str]] = {}
        for item in self._extract_frontend_api_calls_from_files(self._frontend_source_files(project, names=("api",))):
            method, path_value = item.split(" ", 1)
            full_path = self._combine_paths("/api", path_value)
            if full_path is None:
                continue
            mapping.setdefault(full_path, [])
            if method not in mapping[full_path]:
                mapping[full_path].append(method)
        return mapping

    def _analyze_react_crypto(
        self,
        *,
        crypto_path: Path | None,
        app_path: Path | None,
    ) -> ReactCryptoFacts:
        crypto_text = self._read_text(crypto_path) if crypto_path else ""
        app_text = self._read_text(app_path) if app_path else ""
        if not crypto_text:
            return ReactCryptoFacts()
        facts = ReactCryptoFacts(
            detected=True,
            source_paths=[
                path for path in (
                    self._relative_project_path_from_candidate(crypto_path),
                    self._relative_project_path_from_candidate(app_path),
                )
                if path
            ],
        )
        if "AES-GCM" in crypto_text:
            facts.algorithms.append("AES-GCM")
        if "RSA-OAEP" in crypto_text:
            facts.algorithms.append("RSA-OAEP")
        if "PBKDF2" in crypto_text:
            facts.key_derivation = "PBKDF2"
        if "SHA-256" in crypto_text:
            facts.key_derivation_hash = "SHA-256"
        iterations = re.search(r"iterations\s*[:=]\s*(\d+)", crypto_text)
        if iterations:
            facts.key_derivation_iterations = int(iterations.group(1))
        salt = re.search(r"salt\s*[:=].*?([A-Za-z0-9:_-]{6,})", crypto_text)
        if salt:
            facts.key_derivation_salt_template = salt.group(1)
        key_length = re.search(r"length\s*[:=]\s*(\d+)", crypto_text)
        if key_length:
            facts.key_length_bits = int(key_length.group(1))
        nonce = re.search(r"Uint8Array\((\d+)\)", crypto_text)
        if nonce:
            facts.nonce_bytes = int(nonce.group(1))
        version = re.search(r'format\s*[:=]\s*"([^"]+)"|PRIVATE_ENCRYPTION_VERSION\s*=\s*"([^"]+)"', crypto_text)
        if version:
            facts.format_version = version.group(1) or version.group(2)
        for field_name in ("version", "iv", "ciphertext", "data", "key", "salt", "payload", "pub"):
            if re.search(rf"\b{field_name}\b", crypto_text) and field_name not in facts.payload_fields:
                facts.payload_fields.append(field_name)
        if "localStorage" in app_text or "localStorage" in crypto_text:
            facts.key_material_storage = "localStorage"
        elif "Dexie" in crypto_text:
            facts.key_material_storage = "IndexedDB"
        if any(token in app_text for token in ("decryptPayload", "decryptPrivateFields")):
            facts.unlock_behavior = "Des données privées sont déchiffrées côté client lors de l’utilisation de la session locale."
        if any(token in crypto_text for token in ("encryptPayload", "encryptPrivateFields")):
            facts.lock_behavior = "Des données privées sont chiffrées côté client avant stockage."
        facts.recovery_supported = True if "exportKeyBundle" in crypto_text and "importKeyBundle" in crypto_text else None
        return facts

    def _frontend_source_files(
        self,
        project: Project,
        *,
        names: tuple[str, ...] | None = None,
    ) -> list[Path]:
        root = project.root / "frontend" / "src"
        if not root.is_dir():
            return []
        suffixes = {".js", ".jsx", ".ts", ".tsx", ".mjs"}
        files = [path for path in root.rglob("*") if path.is_file() and path.suffix in suffixes and "node_modules" not in path.parts]
        if names:
            lowered = tuple(name.casefold() for name in names)
            files = [path for path in files if any(path.stem.casefold() == name or name in path.stem.casefold() for name in lowered)]
        files.sort()
        return files

    def _find_react_crypto_file(self, source_files: list[Path]) -> Path | None:
        for path in source_files:
            lowered = path.as_posix().casefold()
            if any(token in lowered for token in ("crypto", "vault", "cipher", "secret")):
                return path
        return None

    def _find_react_app_file(self, source_files: list[Path]) -> Path | None:
        for path in source_files:
            if path.name in {"App.jsx", "App.tsx", "main.jsx", "main.tsx"}:
                return path
        return source_files[0] if source_files else None

    def _extract_react_routes(self, source_files: list[Path]) -> list[str]:
        routes: set[str] = set()
        for path in source_files:
            text = self._read_text(path)
            for match in re.finditer(r'path=["\']([^"\']+)["\']', text):
                routes.add(match.group(1))
            for match in re.finditer(r'to=["\']([^"\']+)["\']', text):
                routes.add(match.group(1))
        return sorted(routes)

    def _extract_react_forms(self, source_files: list[Path]) -> list[str]:
        forms: set[str] = set()
        for path in source_files:
            if "<form" in self._read_text(path):
                forms.add(path.stem)
        return sorted(forms)

    def _extract_react_user_features(
        self,
        *,
        source_files: list[Path],
        routes: list[str],
        api_calls: list[str],
    ) -> list[ReactUserFeatureFacts]:
        features: list[ReactUserFeatureFacts] = []
        seen: set[str] = set()
        catalog = (
            ("Générateur de mots de passe", ("passwordgenerator", "générateur", "générer"), ("/vault/new", "/vault/:id/edit"), ("passwords/",)),
            ("Aide", ("help", "aide"), (), ()),
            ("Guide des catégories", ("categoryguide", "guide des catégories", "catégories"), ("/vault/categories",), ("categories/",)),
            ("Importation de clé", ("keyimportform", "importer la clé", "importkeybundle"), ("/login", "/vault/key-backup", "/vault/key-check"), ()),
            ("Exportation de clé", ("keybackup", "exporter la clé", "exportkeybundle"), ("/vault/key-backup",), ("passwords/",)),
            ("Vérification de clé", ("keycheck", "vérif clé", "key-check"), ("/vault/key-check",), ()),
            ("Révélation d’une valeur", ("revealdialog", "réimporte la clé", "impossible de déchiffrer", "decryptpayload"), ("/vault", "/vault/:id/edit"), ("passwords/",)),
            ("Changement de thème", ("themetoggle", "thème", "theme"), (), ()),
            ("Recherche", ("rechercher", "search", "vault-search", "effacer la recherche"), ("/vault",), ("passwords/", "categories/")),
            ("Connexion", ("loginform", "connexion", "current-password"), ("/login",), ("auth/",)),
        )
        for path in source_files:
            relative_path = path.as_posix()
            lowered = (relative_path + "\n" + self._read_text(path)).casefold()
            for label, keywords, route_hints, api_hints in catalog:
                if label in seen or not any(keyword in lowered for keyword in keywords):
                    continue
                related_routes = [route for route in routes if any(hint.casefold() in route.casefold() for hint in route_hints)]
                related_calls = [call for call in api_calls if any(hint.casefold() in call.casefold() for hint in api_hints)]
                features.append(
                    ReactUserFeatureFacts(
                        label=label,
                        status="detected",
                        component=path.stem,
                        routes=related_routes,
                        api_calls=related_calls,
                        evidence=[relative_path],
                        confidence="high" if related_routes or related_calls else "medium",
                    )
                )
                seen.add(label)
        return sorted(features, key=lambda item: item.label)

    def _extract_frontend_api_calls_from_files(self, source_files: list[Path]) -> list[str]:
        results: set[str] = set()
        for path in source_files:
            text = self._read_text(path)
            for method, url in re.findall(r"api\.(get|post|put|patch|delete)\(\s*[`\"]([^`\"]+)[`\"]", text, re.I):
                results.add(f"{method.upper()} {self._normalize_api_call_path(url)}")
            for method, url in re.findall(r"axios\.(get|post|put|patch|delete)\(\s*[`\"]([^`\"]+)[`\"]", text, re.I):
                results.add(f"{method.upper()} {self._normalize_api_call_path(url)}")
            for method, url in re.findall(r"\b(GET|POST|PUT|PATCH|DELETE)\b[^\n]*?[`\"](/[^`\"]+)[`\"]", text):
                results.add(f"{method} {self._normalize_api_call_path(url)}")
            for url in re.findall(r"fetch\(\s*[`\"](/[^`\"]+)[`\"]", text):
                results.add(f"GET {self._normalize_api_call_path(url)}")
            if path.stem.casefold() == "api":
                results.update(self._extract_frontend_api_calls(path))
        return sorted(results)

    def _model_name_from_endpoint(
        self,
        endpoint: DjangoEndpointFacts,
        models: list[DjangoModelFacts],
    ) -> str | None:
        path = (endpoint.path or endpoint.relative_path).casefold()
        mapping = {model.name.casefold(): model.name for model in models}
        explicit = {
            "categories": mapping.get("category"),
            "passwords": mapping.get("passwordentry"),
            "contacts": mapping.get("contact"),
            "users": "User",
            "secrets": mapping.get("secretbundle"),
        }
        for segment, model_name in explicit.items():
            if model_name and f"/{segment}/" in path:
                return model_name
        for model_name in models:
            stem = model_name.name.casefold()
            candidates = {stem + "s", stem + "es"}
            if stem.endswith("y"):
                candidates.add(stem[:-1] + "ies")
            if any(f"/{segment}/" in path for segment in candidates):
                return model_name.name
        return None

    @staticmethod
    def _humanize_model_name(model_name: str) -> str:
        value = re.sub(r"([a-z])([A-Z])", r"\1 \2", model_name).lower()
        return value + ("s" if not value.endswith("s") else "")

    @staticmethod
    def _component_for_endpoint(path: str, frontend_components: set[str]) -> str | None:
        lowered = path.casefold()
        if "categories" in lowered and "CategoryGuide" in frontend_components:
            return "CategoryGuide"
        if "password" in lowered and "PasswordList" in frontend_components:
            return "PasswordList"
        if "secret" in lowered and "KeyBackup" in frontend_components:
            return "KeyBackup"
        return None

    @staticmethod
    def _endpoint_matches_api_call(endpoint_path: str, api_call: str) -> bool:
        _method, path = api_call.split(" ", 1)
        return path.rstrip("/") in endpoint_path.rstrip("/")

    @staticmethod
    def _endpoint_fact(
        *,
        environment: str,
        service: str,
        url: str,
        source: str,
    ) -> ServiceEndpointFacts:
        validity = "valid" if DjangoReactApplicationAnalyzer._is_valid_url_value(url) else "invalid"
        resolution_status = "resolved" if validity == "valid" else "unresolved"
        notes = [] if validity == "valid" else ["URL invalide ou interpolation déséquilibrée."]
        return ServiceEndpointFacts(
            environment=environment,
            service=service,
            url=url,
            source=source,
            validity=validity,
            resolution_status=resolution_status,
            notes=notes,
        )

    @staticmethod
    def _build_url(
        scheme: str,
        host: str,
        port: str | None,
        path: str = "",
    ) -> str:
        base = f"{scheme}://{host}"
        if port:
            base += f":{port}"
        if path:
            if not path.startswith("/"):
                path = "/" + path
            return base + path
        return base

    @staticmethod
    def _extract_host_port(port_mapping: str) -> str | None:
        current = []
        depth = 0
        for char in port_mapping:
            if char == "$":
                current.append(char)
                continue
            if char == "{" and current and current[-1] == "$":
                depth += 1
                current.append(char)
                continue
            if char == "}" and depth:
                depth -= 1
                current.append(char)
                continue
            if char == ":" and depth == 0:
                return "".join(current).strip() or None
            current.append(char)
        return port_mapping.strip() or None

    @staticmethod
    def _is_valid_url_value(url: str) -> bool:
        if not url or "{" in url and "}" not in url:
            return False
        if url.count("${") != url.count("}"):
            return False
        return url.startswith("http://") or url.startswith("https://")

    def _find_django_settings_path(self, project: Project) -> Path:
        for relative_path in project.files:
            if relative_path.endswith("/settings.py") or relative_path == "settings.py":
                return project.root / relative_path
        return project.root / "backend" / "App" / "settings.py"

    def _relative_project_path(self, project: Project, path: Path | None) -> str | None:
        if path is None:
            return None
        try:
            return path.relative_to(project.root).as_posix()
        except Exception:
            return path.as_posix()

    @staticmethod
    def _relative_project_path_from_candidate(path: Path | None) -> str | None:
        if path is None:
            return None
        parts = path.parts
        if "frontend" in parts:
            index = parts.index("frontend")
            return "/".join(parts[index:])
        if "backend" in parts:
            index = parts.index("backend")
            return "/".join(parts[index:])
        return path.as_posix()

    @staticmethod
    def _path_to_module(path: Path, root: Path) -> str | None:
        try:
            relative = path.relative_to(root).with_suffix("")
        except Exception:
            return None
        return ".".join(relative.parts)

    def _extract_root_urlconf_module(self, settings_path: Path) -> str | None:
        text = self._read_text(settings_path)
        match = re.search(r"ROOT_URLCONF\s*=\s*[\"']([^\"']+)[\"']", text)
        return match.group(1) if match else None

    def _manage_default_urlconf(self, project: Project) -> str | None:
        manage_path = project.root / "backend" / "manage.py"
        text = self._read_text(manage_path)
        match = re.search(r"DJANGO_SETTINGS_MODULE',\s*'([^']+)'", text)
        if match:
            return match.group(1).rsplit(".", 1)[0] + ".urls"
        return None

    def _module_to_project_path(self, project: Project, module_name: str | None) -> Path | None:
        if not module_name:
            return None
        relative = module_name.replace(".", "/") + ".py"
        for candidate in (project.root / relative, project.root / "backend" / relative):
            if candidate.is_file():
                return candidate
        return None

    def _find_backend_file(self, project: Project, filename: str, preferred_subdir: str | None = None) -> Path:
        candidates = self._find_backend_files(project, exact_name=filename)
        if preferred_subdir:
            for candidate in candidates:
                if preferred_subdir in candidate.parts:
                    return candidate
        return candidates[0] if candidates else (project.root / "backend" / filename)

    def _find_backend_files(self, project: Project, exact_name: str | None = None, prefix: str | None = None) -> list[Path]:
        backend_root = project.root / "backend"
        if not backend_root.is_dir():
            return []
        results = []
        for path in backend_root.rglob("*.py"):
            if exact_name and path.name != exact_name:
                continue
            if prefix and not path.stem.startswith(prefix):
                continue
            results.append(path)
        results.sort()
        return results

    def _relative_backend_candidate(self, project: Project, path: Path | None) -> str | None:
        return self._relative_project_path(project, path)

    @staticmethod
    def _decorator_name_list(
        decorators: list[ast.expr],
        decorator_name: str,
    ) -> list[str]:
        for decorator in decorators:
            if not isinstance(decorator, ast.Call):
                continue
            if DjangoReactApplicationAnalyzer._call_name(decorator.func) != decorator_name:
                continue
            if not decorator.args:
                return []
            return DjangoReactApplicationAnalyzer._list_literal_names(decorator.args[0])
        return []

    @staticmethod
    def _decorator_string_list(
        decorators: list[ast.expr],
        decorator_name: str,
    ) -> list[str]:
        for decorator in decorators:
            if not isinstance(decorator, ast.Call):
                continue
            if DjangoReactApplicationAnalyzer._call_name(decorator.func) != decorator_name:
                continue
            if not decorator.args:
                return []
            values = []
            if isinstance(decorator.args[0], (ast.List, ast.Tuple)):
                for item in decorator.args[0].elts:
                    value = DjangoReactApplicationAnalyzer._literal_string(item)
                    if value is not None:
                        values.append(value)
            return values
        return []

    @staticmethod
    def _list_literal_names(node: ast.AST) -> list[str]:
        if isinstance(node, ast.Tuple):
            return [
                item
                for element in node.elts
                for item in DjangoReactApplicationAnalyzer._list_literal_names(element)
            ]
        if isinstance(node, ast.List):
            values = []
            for element in node.elts:
                name = DjangoReactApplicationAnalyzer._expression_name(element)
                if name is not None:
                    values.append(name.split(".")[-1])
            return values
        name = DjangoReactApplicationAnalyzer._expression_name(node)
        if name is None:
            return []
        return [name.split(".")[-1]]

    @staticmethod
    def _ast_text(node: ast.AST) -> str:
        try:
            return ast.unparse(node)
        except Exception:
            return ""

    @staticmethod
    def _ownership_controls_from_text(text: str) -> list[str]:
        controls: list[str] = []
        if "owner=self.request.user" in text or "filter(owner=self.request.user" in text:
            controls.append("owner scoped to request.user")
        if "filter(owner=owner" in text or "Contact.objects.filter(owner=owner" in text:
            controls.append("owner scoped to authenticated owner value")
        if "serializer.save(owner=self.request.user)" in text or "Contact.objects.create(owner=owner" in text:
            controls.append("owner assigned server-side")
        return controls

    @staticmethod
    def _data_controls_from_text(text: str) -> list[str]:
        controls: list[str] = []
        if "visibility" in text and ".filter(visibility=" in text:
            controls.append("visibility filtering detected")
        if "search" in text and "icontains" in text:
            controls.append("search filtering detected")
        if "_normalize_payload" in text:
            controls.append("payload normalization before persistence")
        return controls

    @staticmethod
    def _http_method_for_name(name: str) -> str | None:
        mapping = {
            "get": "GET",
            "post": "POST",
            "put": "PUT",
            "patch": "PATCH",
            "delete": "DELETE",
        }
        return mapping.get(name)

    def _extract_viewset_action(
        self,
        node: ast.FunctionDef,
    ) -> dict[str, Any] | None:
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            if self._call_name(decorator.func) != "action":
                continue
            detail = False
            methods = []
            url_path = node.name
            for keyword in decorator.keywords:
                if keyword.arg == "detail" and isinstance(keyword.value, ast.Constant):
                    detail = bool(keyword.value.value)
                if keyword.arg == "methods" and isinstance(keyword.value, (ast.List, ast.Tuple)):
                    methods = [
                        value.upper()
                        for element in keyword.value.elts
                        for value in [self._literal_string(element)]
                        if value is not None
                    ]
                if keyword.arg == "url_path":
                    literal = self._literal_string(keyword.value)
                    if literal:
                        url_path = literal
            return {
                "name": node.name,
                "detail": detail,
                "methods": methods,
                "url_path": url_path,
            }
        return None

    @staticmethod
    def _ast_bool(
        node: ast.AST | None,
        default: bool,
    ) -> bool:
        if isinstance(node, ast.Constant) and isinstance(node.value, bool):
            return node.value
        return default

    @classmethod
    def _ast_value_to_string(
        cls,
        node: ast.AST | None,
    ) -> str | None:
        if node is None:
            return None
        if isinstance(node, ast.Constant):
            return str(node.value)
        if isinstance(node, ast.Attribute):
            owner = cls._expression_name(node.value)
            if owner:
                constants = getattr(cls, "_latest_choice_constants", {})
                if owner in constants and node.attr in constants[owner]:
                    return constants[owner][node.attr]
            return cls._expression_name(node)
        return cls._expression_name(node)

    @staticmethod
    def _clean_view_name(view: str | None) -> str | None:
        if not view:
            return None

        value = view
        for suffix in (
            ".as_view()",
            ".as_view",
        ):
            value = value.removesuffix(suffix)
        if "(" in value:
            value = value.split("(", 1)[0]
        return value.split(".")[-1] or None

    @staticmethod
    def _literal_string(node: ast.AST | None) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    @classmethod
    def _expression_name(cls, node: ast.AST | None) -> str | None:
        if node is None:
            return None
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parent = cls._expression_name(node.value)
            if parent:
                return f"{parent}.{node.attr}"
            return node.attr
        if isinstance(node, ast.Call):
            function_name = cls._call_name(node.func)
            arguments = ", ".join(
                filter(
                    None,
                    (
                        cls._expression_name(argument)
                        or cls._literal_string(argument)
                        for argument in node.args
                    ),
                )
            )
            return f"{function_name}({arguments})"
        if isinstance(node, ast.Constant):
            return str(node.value)
        if isinstance(node, ast.Compare):
            return ast.unparse(node) if hasattr(ast, "unparse") else "compare"
        return None

    @classmethod
    def _call_name(cls, node: ast.AST) -> str:
        return cls._expression_name(node) or ""

    @staticmethod
    def _normalize_path(value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            return "/"
        cleaned = cleaned.replace("<int:pk>", "{id}")
        cleaned = cleaned.replace("<uuid:pk>", "{id}")
        cleaned = cleaned.replace("<str:pk>", "{id}")
        if not cleaned.startswith("/"):
            cleaned = "/" + cleaned
        return cleaned

    @staticmethod
    def _read_yaml(path: Path) -> Any:
        try:
            return yaml.safe_load(
                path.read_text(encoding="utf-8")
            )
        except (OSError, yaml.YAMLError):
            return None

    @staticmethod
    def _read_text(path: Path) -> str:
        try:
            return path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except OSError:
            return ""

    @staticmethod
    def _read_json(path: Path) -> Any:
        try:
            return json.loads(
                path.read_text(encoding="utf-8")
            )
        except (OSError, ValueError):
            return None

    @staticmethod
    def _read_env_entries(
        path: Path,
    ) -> list[dict[str, str | None]]:
        items: list[dict[str, str | None]] = []
        try:
            lines = path.read_text(
                encoding="utf-8",
                errors="ignore",
            ).splitlines()
        except OSError:
            return items

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, raw_value = stripped.split("=", 1)
            key = key.strip()
            if not key:
                continue
            value, comment = DjangoReactApplicationAnalyzer._split_env_value_and_comment(raw_value)
            items.append(
                {
                    "key": key,
                    "value": value,
                    "comment": comment,
                }
            )
        return items

    @staticmethod
    def _split_env_value_and_comment(
        raw_value: str,
    ) -> tuple[str | None, str | None]:
        value_chars: list[str] = []
        quote: str | None = None
        escaped = False
        comment: str | None = None
        for index, char in enumerate(raw_value):
            if escaped:
                value_chars.append(char)
                escaped = False
                continue
            if char == "\\":
                escaped = True
                value_chars.append(char)
                continue
            if quote:
                if char == quote:
                    quote = None
                value_chars.append(char)
                continue
            if char in {'"', "'"}:
                quote = char
                value_chars.append(char)
                continue
            if char == "#" and (index == 0 or raw_value[index - 1].isspace()):
                comment = raw_value[index + 1 :].strip() or None
                break
            value_chars.append(char)
        value = "".join(value_chars).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        value = value.replace(r"\#", "#").strip()
        return (value, comment)

    @staticmethod
    def _read_env_keys(
        path: Path,
    ) -> list[tuple[str, str | None]]:
        return [
            (item["key"], item["value"])
            for item in DjangoReactApplicationAnalyzer._read_env_entries(path)
        ]

    def _compose_variable_requirements(
        self,
        project: Project,
        environments: ProjectEnvironmentsFacts,
    ) -> dict[str, dict[str, bool]]:
        requirements: dict[str, dict[str, bool]] = {}
        for environment in environments.items:
            compose_path = project.root / environment.compose_file
            text = self._read_text(compose_path)
            for name, required in self._extract_placeholder_specs(text):
                requirements.setdefault(name, {})[environment.name] = required
        return requirements

    @staticmethod
    def _extract_placeholder_specs(
        text: str,
    ) -> list[tuple[str, bool]]:
        specs: list[tuple[str, bool]] = []
        for match in re.finditer(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?:(:?[-?])(.*?))?\}", text):
            name = match.group(1)
            operator = match.group(2)
            required = operator in {":?", "?"}
            specs.append((name, required))
        return specs

    @staticmethod
    def _environment_names_for_env_file(
        path: Path,
    ) -> list[str]:
        if not path.exists():
            return []
        if path.is_symlink():
            target = path.resolve().name.casefold()
            if target == ".env.dev":
                return ["dev"]
            if target == ".env.prod":
                return ["prod"]
        for item in DjangoReactApplicationAnalyzer._read_env_entries(path):
            if item["key"] == "APP_ENV" and item["value"]:
                value = item["value"].casefold()
                if value in {"dev", "prod"}:
                    return [value]
        return ["dev", "prod"]

    @staticmethod
    def _extract_getenv_calls(
        path: Path,
    ) -> list[dict[str, str | None]]:
        try:
            tree = ast.parse(
                path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            )
        except (OSError, SyntaxError):
            return []

        items: list[dict[str, str | None]] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not isinstance(func, ast.Attribute):
                continue
            if func.attr != "getenv":
                continue
            if not isinstance(func.value, ast.Name):
                continue
            if func.value.id != "os":
                continue
            if not node.args:
                continue
            first = node.args[0]
            if not isinstance(first, ast.Constant) or not isinstance(first.value, str):
                continue
            default = None
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                default_value = node.args[1].value
                if isinstance(default_value, str):
                    default = default_value
            items.append(
                {
                    "name": first.value,
                    "default": default,
                }
            )
        return items

    @staticmethod
    def _extract_import_meta_env(
        path: Path,
    ) -> list[str]:
        text = DjangoReactApplicationAnalyzer._read_text(
            path
        )
        names = sorted(
            set(
                re.findall(
                    r"import\\.meta\\.env\\.([A-Za-z_][A-Za-z0-9_]*)",
                    text,
                )
                + re.findall(
                    r"process\\.env\\.([A-Za-z_][A-Za-z0-9_]*)",
                    text,
                )
            )
        )
        return names

    @staticmethod
    def _extract_local_key_names(
        path: Path,
    ) -> list[str]:
        text = DjangoReactApplicationAnalyzer._read_text(
            path
        )
        return sorted(
            set(
                re.findall(
                    r'ensure_local_key\s+"([A-Za-z_][A-Za-z0-9_]*)"',
                    text,
                )
            )
        )

    @staticmethod
    def _parse_installed_apps(
        path: Path,
    ) -> list[str]:
        text = DjangoReactApplicationAnalyzer._read_text(
            path
        )
        match = re.search(
            r"INSTALLED_APPS\s*=\s*\[(.*?)\]",
            text,
            re.DOTALL,
        )
        if not match:
            return []

        values = [
            item[0] or item[1]
            for item in re.findall(
                r'"([^"]+)"|\'([^\']+)\'',
                match.group(1),
            )
        ]
        return sorted(set(values))

    @staticmethod
    def _parse_django_models(
        path: Path,
    ) -> list[DjangoModelFacts]:
        try:
            tree = ast.parse(
                path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            )
        except (OSError, SyntaxError):
            return []

        results: list[DjangoModelFacts] = []
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if not any(
                isinstance(base, ast.Attribute)
                and base.attr == "Model"
                for base in node.bases
            ):
                continue
            fields = []
            for item in node.body:
                if not isinstance(item, ast.Assign):
                    continue
                if len(item.targets) != 1 or not isinstance(
                    item.targets[0],
                    ast.Name,
                ):
                    continue
                if not isinstance(item.value, ast.Call):
                    continue
                call = item.value.func
                if not isinstance(call, ast.Attribute):
                    continue
                if not call.attr.endswith("Field") and call.attr != "ForeignKey":
                    continue
                fields.append(item.targets[0].id)
            results.append(
                DjangoModelFacts(
                    name=node.name,
                    fields=fields,
                    source="backend/api/models.py",
                )
            )
        results.sort(key=lambda item: item.name)
        return results

    @staticmethod
    def _extract_database_engine(
        settings_text: str,
    ) -> str | None:
        match = re.search(
            r'"ENGINE":\s*"([^"]+)"',
            settings_text,
        )
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _extract_frontend_api_calls(
        path: Path,
    ) -> list[str]:
        text = DjangoReactApplicationAnalyzer._read_text(
            path
        )
        pattern = re.compile(
            r"export function \w+\([^)]*\)\s*\{\s*return request\(\s*[`\"]([^`\"]+)[`\"]\s*,\s*\{\s*method:\s*[`\"]([A-Z]+)[`\"]",
            re.DOTALL,
        )
        results = [
            f"{method} {DjangoReactApplicationAnalyzer._normalize_api_call_path(path_value)}"
            for path_value, method in pattern.findall(text)
        ]

        # GET helpers without explicit method.
        get_pattern = re.compile(
            r"export function \w+\([^)]*\)\s*\{\s*return request\(\s*[`\"]([^`\"]+)[`\"]\s*,\s*\{\s*token",
            re.DOTALL,
        )
        for path_value in get_pattern.findall(text):
            normalized = DjangoReactApplicationAnalyzer._normalize_api_call_path(
                path_value
            )
            record = f"GET {normalized}"
            if record not in results:
                results.append(record)

        results.sort()
        return results

    @staticmethod
    def _normalize_api_call_path(path: str) -> str:
        normalized = path
        normalized = re.sub(
            r"\$\{[^}]+\}",
            "{id}",
            normalized,
        )
        return normalized

    @staticmethod
    def _describe_variable(name: str) -> str | None:
        mapping = {
            "APP_ENV": "Sélectionne l’environnement actif.",
            "APP_HOST": "Nom d’hôte public utilisé en production.",
            "VITE_API_BASE": "Base des appels API côté frontend.",
            "DJANGO_ALLOWED_HOSTS": "Hôtes autorisés par Django.",
            "DJANGO_CSRF_TRUSTED_ORIGINS": "Origines de confiance CSRF pour Django.",
            "POSTGRES_DB": "Nom de la base PostgreSQL.",
            "POSTGRES_USER": "Compte PostgreSQL utilisé par l’application.",
            "POSTGRES_PASSWORD": "Mot de passe PostgreSQL.",
            "DJANGO_SECRET_KEY": "Clé secrète Django.",
            "CONTACT_API_TOKEN": "Jeton d’accès pour l’intégration interne Contact.",
            "CALENDRIER_API_TOKEN": "Jeton d’accès pour l’intégration calendrier.",
            "CALENDRIER_API_BASE": "Base URL de l’intégration calendrier.",
        }
        return mapping.get(name)

    @staticmethod
    def _is_sensitive_name(name: str) -> bool:
        return bool(
            SENSITIVE_NAME_PATTERN.search(name)
        )

    @staticmethod
    def _optional_string(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _merge_scope(
        existing: str,
        new: str,
    ) -> str:
        if existing == new:
            return existing
        return "shared"

    @staticmethod
    def _command_environments(
        target: str,
    ) -> list[str]:
        if target == "dev":
            return ["dev"]
        if target == "prod":
            return ["prod"]
        return ["dev", "prod"]

    @staticmethod
    def _extend_unique(
        target: list[str],
        values: list[str],
    ) -> None:
        for value in values:
            if value not in target:
                target.append(value)
