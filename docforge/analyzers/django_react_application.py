from __future__ import annotations

import ast
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
    source: str = "Makefile"


@dataclass(slots=True)
class OperationalCommandFacts:
    name: str
    category: str
    command: str
    source: str
    target: str | None = None
    body: list[str] = field(default_factory=list)
    environments: list[str] = field(default_factory=list)
    parameters: list["OperationalCommandParameterFacts"] = field(
        default_factory=list
    )


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


@dataclass(slots=True)
class OperationalCommandsFacts:
    commands: list[OperationalCommandFacts] = field(
        default_factory=list
    )
    scripts: list[ScriptAnalysisFacts] = field(
        default_factory=list
    )


@dataclass(slots=True)
class EnvironmentVariableFacts:
    name: str
    scope: str
    environments: list[str] = field(default_factory=list)
    required: bool | None = None
    sensitive: bool = False
    default_value: str | None = None
    description: str | None = None
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
    sources: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DjangoFacts:
    project_module: str | None = None
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
class ReactFacts:
    entry_point: str | None = None
    routes: list[str] = field(default_factory=list)
    pages: list[str] = field(default_factory=list)
    navigation_items: list[str] = field(
        default_factory=list
    )
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
    label: str
    status: str
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


class DjangoReactApplicationAnalyzer:
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
                    env_files,
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
                host_port = port.split(":", 1)[0]
                if service.name == "frontend":
                    endpoints.append(
                        ServiceEndpointFacts(
                            environment="dev",
                            service=service.name,
                            url=f"http://localhost:{host_port}",
                            source=service.source,
                        )
                    )
                if service.name == "backend":
                    endpoints.extend(
                        [
                            ServiceEndpointFacts(
                                environment="dev",
                                service=service.name,
                                url=f"http://localhost:{host_port}/api/",
                                source=service.source,
                            ),
                            ServiceEndpointFacts(
                                environment="dev",
                                service=service.name,
                                url=f"http://localhost:{host_port}/admin/",
                                source=service.source,
                            ),
                        ]
                    )

        if service.detected_hosts:
            for host in service.detected_hosts:
                base = f"https://{host}"
                candidate_paths = []
                for label in service.traefik_labels:
                    if "PathPrefix(`/api`)" in label:
                        candidate_paths.append("/api/")
                    elif "PathPrefix(`/admin`)" in label:
                        candidate_paths.append("/admin/")
                    elif "PathPrefix(`/static`)" in label:
                        candidate_paths.append("/static/")
                if not candidate_paths:
                    candidate_paths = [""]
                for path_suffix in candidate_paths:
                    endpoints.append(
                        ServiceEndpointFacts(
                            environment=service.environment,
                            service=service.name,
                            url=f"{base}{path_suffix}",
                            source=service.source,
                        )
                    )

        return endpoints

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

        help_parameters = self._extract_make_help_parameters(lines)

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

            target = line.split(":", 1)[0].strip()
            body: list[str] = []
            i += 1
            while i < len(lines):
                body_line = lines[i]
                if (
                    body_line.startswith("	")
                    or body_line.startswith(" ")
                ):
                    body.append(body_line.strip())
                    i += 1
                    continue
                break

            if not target:
                continue

            category = self.CATEGORY_BY_TARGET.get(
                target,
                "other",
            )
            commands.append(
                OperationalCommandFacts(
                    name=target,
                    category=category,
                    command=f"make {target}",
                    source="Makefile",
                    target=target,
                    body=body,
                    environments=self._command_environments(
                        target
                    ),
                    parameters=self._build_make_parameters(
                        target=target,
                        body=body,
                        help_parameters=help_parameters,
                    ),
                )
            )

        commands.sort(
            key=lambda item: (item.category, item.command)
        )
        return OperationalCommandsFacts(
            commands=commands,
            scripts=self._analyze_scripts(project),
        )

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
            sensitive: bool,
            default_value: str | None,
            description: str | None,
            source: str,
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
                )
                variables[name] = item

            item.scope = self._merge_scope(
                item.scope,
                scope,
            )
            self._extend_unique(
                item.environments,
                environments,
            )
            self._extend_unique(
                item.sources,
                [source],
            )
            item.sensitive = (
                item.sensitive or sensitive
            )
            if item.required is None:
                item.required = required
            elif required is True:
                item.required = True
            if item.default_value is None:
                item.default_value = default_value
            if item.description is None:
                item.description = description

        env_file_map = {
            ".env": ["dev", "prod"],
            ".env.dev": ["dev"],
            ".env.prod": ["prod"],
            ".env.template.example": ["dev", "prod"],
        }

        for relative_path, env_names in env_file_map.items():
            path = project.root / relative_path
            if not path.is_file():
                continue
            for name, default_value in self._read_env_keys(
                path
            ):
                upsert(
                    name,
                    scope="shared",
                    environments=env_names,
                    required=(
                        False
                        if default_value is not None
                        else None
                    ),
                    sensitive=self._is_sensitive_name(
                        name
                    ),
                    default_value=(
                        default_value
                        if not self._is_sensitive_name(name)
                        else None
                    ),
                    description=self._describe_variable(
                        name
                    ),
                    source=relative_path,
                )

        settings_path = (
            project.root / "backend" / "App" / "settings.py"
        )
        for getenv in self._extract_getenv_calls(
            settings_path
        ):
            upsert(
                getenv["name"],
                scope="backend",
                environments=["dev", "prod"],
                required=(
                    False
                    if getenv["default"] is not None
                    else True
                ),
                sensitive=self._is_sensitive_name(
                    getenv["name"]
                ),
                default_value=(
                    getenv["default"]
                    if not self._is_sensitive_name(
                        getenv["name"]
                    )
                    else None
                ),
                description=self._describe_variable(
                    getenv["name"]
                ),
                source="backend/App/settings.py",
            )

        api_path = (
            project.root / "frontend" / "src" / "api.js"
        )
        for name in self._extract_import_meta_env(api_path):
            upsert(
                name,
                scope="frontend",
                environments=["dev", "prod"],
                required=False,
                sensitive=self._is_sensitive_name(name),
                default_value=None,
                description=self._describe_variable(name),
                source="frontend/src/api.js",
            )

        script_path = (
            project.root / "scripts" / "generate-env.sh"
        )
        for name in self._extract_local_key_names(
            script_path
        ):
            upsert(
                name,
                scope="ops",
                environments=["dev", "prod"],
                required=True,
                sensitive=self._is_sensitive_name(name),
                default_value=None,
                description=self._describe_variable(name),
                source="scripts/generate-env.sh",
            )

        for environment in environments.items:
            for service in environment.services:
                for name in service.env_variables:
                    upsert(
                        name,
                        scope=service.role or "shared",
                        environments=[environment.name],
                        required=True,
                        sensitive=self._is_sensitive_name(
                            name
                        ),
                        default_value=None,
                        description=self._describe_variable(
                            name
                        ),
                        source=service.source,
                    )

        result = list(variables.values())
        result.sort(key=lambda item: item.name)
        return EnvironmentVariablesFacts(variables=result)

    def _analyze_django(
        self,
        project: Project,
        *,
        api: ApiFacts,
        operational_commands: OperationalCommandsFacts,
    ) -> DjangoFacts:
        settings_path = (
            project.root / "backend" / "App" / "settings.py"
        )
        urls_path = (
            project.root / "backend" / "App" / "urls.py"
        )
        models_path = (
            project.root / "backend" / "api" / "models.py"
        )
        views_path = (
            project.root / "backend" / "api" / "views.py"
        )
        ensure_admin_path = (
            project.root
            / "backend"
            / "api"
            / "management"
            / "commands"
            / "ensure_admin.py"
        )

        installed_apps = self._parse_installed_apps(
            settings_path
        )
        local_apps = [
            app_name
            for app_name in installed_apps
            if (project.root / "backend" / app_name).exists()
        ]
        auth_mechanisms = []
        permissions = []
        settings_text = self._read_text(settings_path)
        views_text = self._read_text(views_path)

        if "JWTAuthentication" in settings_text:
            auth_mechanisms.append("JWT")
        if "TokenObtainPairView" in self._read_text(
            project.root / "backend" / "api" / "urls.py"
        ):
            auth_mechanisms.append("SimpleJWT")
        if "Authorization: `Bearer" in self._read_text(
            project.root / "frontend" / "src" / "api.js"
        ):
            auth_mechanisms.append("Bearer token")

        for permission in (
            "IsAuthenticated",
            "IsAdminUser",
            "AllowAny",
        ):
            if permission in views_text or permission in settings_text:
                permissions.append(permission)

        model_schemas = self._parse_django_model_schemas(
            models_path
        )
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
            create_admin_commands.append(
                "python manage.py ensure_admin"
            )

        database_engines = self._extract_database_engines(
            settings_path
        )
        runtime_engines = [
            item.engine
            for item in database_engines
            if "test" not in item.context.casefold()
        ]
        database_engine = (
            runtime_engines[0]
            if runtime_engines
            else (database_engines[0].engine if database_engines else None)
        )
        database_configuration = []
        for name in (
            "POSTGRES_DB",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_HOST",
            "POSTGRES_PORT",
        ):
            if name in settings_text:
                database_configuration.append(name)

        view_details = self._collect_view_details(
            views_path
        )
        resolved_routes, endpoints = self._build_django_routes_and_endpoints(
            project=project,
            api=api,
            view_details=view_details,
            auth_mechanisms=sorted(set(auth_mechanisms)),
        )

        return DjangoFacts(
            project_module="App",
            settings_files=[
                "backend/App/settings.py"
            ],
            installed_apps=installed_apps,
            local_apps=local_apps,
            models=models,
            model_schemas=model_schemas,
            routes=sorted(
                {
                    route.path
                    for route in api.routes
                }
            ),
            resolved_routes=resolved_routes,
            endpoints=endpoints,
            routers=sorted(
                registration.prefix
                for registration in api.router_registrations
            ),
            auth_mechanisms=sorted(
                set(auth_mechanisms)
            ),
            permissions=sorted(set(permissions)),
            admin_enabled=(
                "django.contrib.admin" in installed_apps
                or "admin.site.urls" in self._read_text(
                    urls_path
                )
            ),
            migration_commands=sorted(
                set(migration_commands)
            ),
            create_admin_commands=create_admin_commands,
            database_engine=database_engine,
            database_engines=database_engines,
            database_configuration=database_configuration,
            source_paths=[
                "backend/App/settings.py",
                "backend/App/urls.py",
                "backend/api/urls.py",
                "backend/api/models.py",
                "backend/api/views.py",
                "backend/api/management/commands/ensure_admin.py",
            ],
        )

    def _analyze_react(
        self,
        project: Project,
    ) -> ReactFacts:
        package_path = (
            project.root / "frontend" / "package.json"
        )
        app_path = (
            project.root / "frontend" / "src" / "App.jsx"
        )
        api_path = (
            project.root / "frontend" / "src" / "api.js"
        )
        crypto_path = (
            project.root / "frontend" / "src" / "crypto.js"
        )
        package_data = self._read_json(package_path)
        scripts = (
            package_data.get("scripts", {})
            if isinstance(package_data, dict)
            else {}
        )

        navigation_items = []
        for label in (
            "Recherche",
            "Visibilité",
            "Administration",
            "Contact",
            "Thème",
        ):
            if label in self._read_text(app_path):
                navigation_items.append(label)

        pages = []
        app_text = self._read_text(app_path)
        for label in (
            "Accès privé",
            "Utilisateurs",
            "Nouveau contact",
            "Modifier le contact",
        ):
            if label in app_text:
                pages.append(label)

        api_calls = self._extract_frontend_api_calls(
            api_path
        )
        auth_mechanisms = []
        if "Authorization: `Bearer ${options.token}`" in self._read_text(
            api_path
        ):
            auth_mechanisms.append(
                "JWT Bearer côté frontend"
            )
        if "SESSION_STORAGE_KEY" in app_text:
            auth_mechanisms.append(
                "Session locale dans localStorage"
            )
        if "decryptPrivateFields" in app_text:
            auth_mechanisms.append(
                "Déverrouillage local du coffre privé"
            )

        routes = ["/"]
        crypto = self._analyze_react_crypto(
            crypto_path=crypto_path,
            app_path=app_path,
        )

        return ReactFacts(
            entry_point="frontend/src/main.jsx",
            routes=routes,
            pages=pages,
            navigation_items=navigation_items,
            api_calls=api_calls,
            environment_variables=self._extract_import_meta_env(
                api_path
            ),
            auth_mechanisms=auth_mechanisms,
            scripts={
                str(key): str(value)
                for key, value in scripts.items()
                if isinstance(key, str)
                and isinstance(value, str)
            },
            dev_command=(
                "npm run dev"
                if "dev" in scripts
                else None
            ),
            build_command=(
                "npm run build"
                if "build" in scripts
                else None
            ),
            crypto=crypto,
            source_paths=[
                "frontend/package.json",
                "frontend/src/main.jsx",
                "frontend/src/App.jsx",
                "frontend/src/api.js",
                "frontend/src/crypto.js",
                "frontend/vite.config.js",
            ],
        )

    def _analyze_capabilities(
        self,
        django: DjangoFacts,
        react: ReactFacts,
    ) -> CapabilitiesFacts:
        capabilities: list[CapabilityFacts] = []

        def add(
            label: str,
            *evidence: str,
            status: str = "derived",
            component: str | None = None,
            endpoint: str | None = None,
            permission_condition: str | None = None,
            confidence: str | None = None,
        ) -> None:
            capabilities.append(
                CapabilityFacts(
                    label=label,
                    status=status,
                    evidence=list(evidence),
                    component=component,
                    endpoint=endpoint,
                    permission_condition=permission_condition,
                    confidence=confidence,
                )
            )

        model_names = {model.name for model in django.models}
        api_calls = set(react.api_calls)

        if "Contact" in model_names and "GET /contacts/" in api_calls:
            add(
                "Consulter les contacts",
                "backend/api/models.py",
                "frontend/src/api.js",
                component="App",
                endpoint="/api/contacts/",
                permission_condition="IsAuthenticated",
                confidence="high",
            )
        if "POST /contacts/" in api_calls:
            add(
                "Créer un contact",
                "frontend/src/api.js",
                "backend/api/views.py",
                component="App",
                endpoint="/api/contacts/",
                permission_condition="IsAuthenticated",
                confidence="high",
            )
        if "PATCH /contacts/{id}/" in api_calls:
            add(
                "Modifier un contact",
                "frontend/src/api.js",
                "backend/api/views.py",
                component="App",
                endpoint="/api/contacts/{id}/",
                permission_condition="IsAuthenticated",
                confidence="high",
            )
        if "DELETE /contacts/{id}/" in api_calls:
            add(
                "Supprimer un contact",
                "frontend/src/api.js",
                "backend/api/views.py",
                component="App",
                endpoint="/api/contacts/{id}/",
                permission_condition="IsAuthenticated",
                confidence="high",
            )
        if "POST /contacts/{id}/sync_birthday/" in api_calls:
            add(
                "Synchroniser l’anniversaire d’un contact",
                "frontend/src/api.js",
                "backend/api/views.py",
                component="App",
                endpoint="/api/contacts/{id}/sync_birthday/",
                permission_condition="IsAuthenticated",
                confidence="medium",
            )
        if "GET /users/" in api_calls and "POST /users/{id}/reset_password/" in api_calls:
            add(
                "Administrer les utilisateurs",
                "frontend/src/App.jsx",
                "backend/api/views.py",
                component="AdminPanel",
                endpoint="/api/users/",
                permission_condition="IsAdminUser",
                confidence="high",
            )
        if "Déverrouillage local du coffre privé" in react.auth_mechanisms:
            add(
                "Gérer des contacts privés chiffrés côté client",
                "frontend/src/App.jsx",
                "frontend/src/crypto.js",
                status="detected",
                component="App",
                endpoint=None,
                permission_condition=None,
                confidence="medium",
            )
        if any(
            route.full_path == "/api/auth/login/"
            for route in django.resolved_routes
        ):
            add(
                "S’authentifier à l’application",
                "backend/api/urls.py",
                "frontend/src/api.js",
                status="detected",
                component="App",
                endpoint="/api/auth/login/",
                confidence="high",
            )
        if any(
            route.full_path and route.full_path.startswith("/api/integrations/contacts/")
            for route in django.resolved_routes
        ):
            add(
                "Exposer une intégration interne de contacts",
                "backend/api/urls.py",
                "backend/api/views.py",
                component=None,
                endpoint="/api/integrations/contacts/",
                confidence="medium",
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
                    values.setdefault(key, default)
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
    def _extract_make_help_parameters(
        lines: list[str],
    ) -> dict[str, list[tuple[str, str | None, str | None, bool]]]:
        mapping: dict[str, list[tuple[str, str | None, str | None, bool]]] = {}
        pattern = re.compile(
            r"make\s+([a-z0-9_-]+)\s+([A-Z_]+)=([^)'\s]+)"
        )
        for line in lines:
            lowered = line.casefold()
            if "make " not in lowered:
                continue
            cleaned = line.strip().strip("'\"")
            for target, param, example in pattern.findall(cleaned):
                optional = "optionnel" in lowered or "aucun fichier spécifié" in lowered
                entries = mapping.setdefault(target, [])
                entries.append(
                    (
                        param,
                        example,
                        cleaned,
                        optional,
                    )
                )
        return mapping

    def _build_make_parameters(
        self,
        *,
        target: str,
        body: list[str],
        help_parameters: dict[str, list[tuple[str, str | None, str | None, bool]]],
    ) -> list[OperationalCommandParameterFacts]:
        parameters: dict[str, OperationalCommandParameterFacts] = {}

        for entry in help_parameters.get(target, []):
            param, example, description, optional = entry
            parameters[param] = OperationalCommandParameterFacts(
                name=param,
                required=not optional,
                example=example,
                description=description,
                source="Makefile",
            )

        for line in body:
            for param in re.findall(r"\$\(([A-Z_]+)\)", line):
                if param.endswith("_DIR"):
                    continue
                item = parameters.get(param)
                if item is None:
                    parameters[param] = OperationalCommandParameterFacts(
                        name=param,
                        required=f'"$(%s)"' % param not in line,
                        example=None,
                        description=None,
                        source="Makefile",
                    )
                elif f'"$(%s)"' % param in line:
                    item.required = False

        result = list(parameters.values())
        result.sort(key=lambda item: item.name)
        return result

    def _analyze_scripts(
        self,
        project: Project,
    ) -> list[ScriptAnalysisFacts]:
        script_paths = [
            "scripts/init.sh",
            "scripts/env-switch.sh",
            "scripts/migrate.sh",
            "scripts/backup-db.sh",
            "scripts/restore-db.sh",
            "scripts/update.sh",
            "scripts/check-invariants.sh",
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
        if relative_path == "scripts/env-switch.sh":
            facts.environment_targets = ["dev", "prod"]
            facts.notes.append(
                "Le choix d’environnement repose sur un lien symbolique .env."
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

        facts.compose_commands = list(dict.fromkeys(facts.compose_commands))
        facts.django_commands = list(dict.fromkeys(facts.django_commands))
        facts.shell_commands = list(dict.fromkeys(facts.shell_commands))
        facts.validations = list(dict.fromkeys(facts.validations))
        facts.failure_conditions = list(dict.fromkeys(facts.failure_conditions))
        facts.creates_files = list(dict.fromkeys(facts.creates_files))
        facts.symlinks = list(dict.fromkeys(facts.symlinks))
        facts.generated_secrets = list(dict.fromkeys(facts.generated_secrets))
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
        views_path: Path,
    ) -> dict[str, dict[str, Any]]:
        try:
            tree = ast.parse(
                views_path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            )
        except (OSError, SyntaxError):
            return {}

        details: dict[str, dict[str, Any]] = {}
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                details[node.name] = {
                    "view": node.name,
                    "permissions": self._decorator_name_list(node.decorator_list, "permission_classes"),
                    "authentication": self._decorator_name_list(node.decorator_list, "authentication_classes"),
                    "methods": self._decorator_string_list(node.decorator_list, "api_view"),
                    "actions": [],
                    "source": "backend/api/views.py",
                }
            if isinstance(node, ast.ClassDef):
                permissions = []
                authentication = []
                methods: list[str] = []
                actions: list[dict[str, Any]] = []
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == "permission_classes":
                                permissions = self._list_literal_names(item.value)
                            if isinstance(target, ast.Name) and target.id == "authentication_classes":
                                authentication = self._list_literal_names(item.value)
                    if isinstance(item, ast.FunctionDef):
                        http_method = self._http_method_for_name(item.name)
                        if http_method:
                            methods.append(http_method)
                        action = self._extract_viewset_action(item)
                        if action is not None:
                            actions.append(action)
                details[node.name] = {
                    "view": node.name,
                    "permissions": permissions,
                    "authentication": authentication,
                    "methods": list(dict.fromkeys(methods)),
                    "actions": actions,
                    "source": "backend/api/views.py",
                }
        return details

    def _build_django_routes_and_endpoints(
        self,
        *,
        project: Project,
        api: ApiFacts,
        view_details: dict[str, dict[str, Any]],
        auth_mechanisms: list[str],
    ) -> tuple[list[DjangoRouteFacts], list[DjangoEndpointFacts]]:
        mounts = self._extract_include_mounts(project)
        frontend_methods = self._frontend_methods_by_path(
            project.root / "frontend" / "src" / "api.js"
        )
        route_entries = list(api.routes)
        for registration in api.router_registrations:
            detail = view_details.get(
                registration.viewset.split(".")[-1],
                {},
            )
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
            source_mounts = mounts.get(route.source)
            if not source_mounts:
                source_mounts = [
                    {
                        "mount_path": None if route.source.endswith("/urls.py") and route.source != "backend/App/urls.py" else route.path,
                        "resolution_status": "resolved" if route.source == "backend/App/urls.py" else "unresolved",
                        "source": route.source,
                    }
                ]
            for mount in source_mounts:
                mount_path = mount["mount_path"]
                if route.source == "backend/App/urls.py":
                    relative_path = route.path.lstrip("/")
                    full_path = route.path
                    resolution_status = "resolved"
                    sources = [route.source]
                else:
                    relative_path = route.path.lstrip("/")
                    full_path = self._combine_paths(mount_path, route.path) if mount_path else None
                    resolution_status = "resolved" if full_path else "unresolved"
                    sources = [mount["source"], route.source]
                methods = list(route.methods or frontend_methods.get(full_path or route.path, []))
                route_fact = DjangoRouteFacts(
                    relative_path=relative_path,
                    mount_path=mount_path,
                    full_path=full_path,
                    route_type=route.kind,
                    resolution_status=resolution_status,
                    name=route.name,
                    view=route.view,
                    methods=methods,
                    sources=list(dict.fromkeys(sources)),
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
                        sources=list(dict.fromkeys(sources + ([detail.get("source")] if detail.get("source") else []))),
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
        url_files = [
            path
            for path in project.files
            if Path(path).name == "urls.py"
        ]
        for relative_path in url_files:
            path = project.root / relative_path
            try:
                tree = ast.parse(
                    path.read_text(
                        encoding="utf-8",
                        errors="ignore",
                    )
                )
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
                        "resolution_status": "resolved" if mount_path is not None else "unresolved",
                        "source": relative_path,
                    }
                )
        return mounts

    def _module_to_urls_path(
        self,
        project: Project,
        module_name: str | None,
    ) -> str | None:
        if not module_name:
            return None
        relative = module_name.replace(".", "/") + ".py"
        candidates = [
            relative,
            f"backend/{relative}",
        ]
        for candidate in candidates:
            if candidate in project.files:
                return candidate
        return None

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
        api_path: Path,
    ) -> dict[str, list[str]]:
        mapping: dict[str, list[str]] = {}
        for item in self._extract_frontend_api_calls(api_path):
            method, path_value = item.split(" ", 1)
            full_path = self._combine_paths("/api", path_value)
            mapping.setdefault(full_path, [])
            if method not in mapping[full_path]:
                mapping[full_path].append(method)
        return mapping

    def _analyze_react_crypto(
        self,
        *,
        crypto_path: Path,
        app_path: Path,
    ) -> ReactCryptoFacts:
        crypto_text = self._read_text(crypto_path)
        app_text = self._read_text(app_path)
        if not crypto_text:
            return ReactCryptoFacts()
        facts = ReactCryptoFacts(
            detected=True,
            source_paths=[
                "frontend/src/crypto.js",
                "frontend/src/App.jsx",
            ],
        )
        if "AES-GCM" in crypto_text:
            facts.algorithms.append("AES-GCM")
        if "PBKDF2" in crypto_text:
            facts.key_derivation = "PBKDF2"
        if "SHA-256" in crypto_text:
            facts.key_derivation_hash = "SHA-256"
        iterations = re.search(r"iterations:\s*(\d+)", crypto_text)
        if iterations:
            facts.key_derivation_iterations = int(iterations.group(1))
        salt = re.search(r"salt:\s*encoder\.encode\(`([^`]+)`\)", crypto_text)
        if salt:
            facts.key_derivation_salt_template = salt.group(1)
        key_length = re.search(r"deriveBits\([^\)]*,\s*(\d+)\s*\)", crypto_text, re.DOTALL)
        if key_length:
            facts.key_length_bits = int(key_length.group(1))
        nonce = re.search(r"Uint8Array\((\d+)\)", crypto_text)
        if nonce:
            facts.nonce_bytes = int(nonce.group(1))
        version = re.search(r'PRIVATE_ENCRYPTION_VERSION\s*=\s*"([^"]+)"', crypto_text)
        if version:
            facts.format_version = version.group(1)
        for field_name in ("version", "iv", "ciphertext"):
            if re.search(rf'{field_name}:', crypto_text):
                facts.payload_fields.append(field_name)
        facts.cleartext_fields = []
        if "localStorage" in app_text and "SESSION_STORAGE_KEY" in app_text:
            facts.key_material_storage = "localStorage"
        if "decryptPrivateFields" in app_text:
            facts.unlock_behavior = "Les champs privés sont déchiffrés côté client lors de l’utilisation de la session locale."
        if "encryptPrivateFields" in crypto_text:
            facts.lock_behavior = "Les champs privés sont sérialisés en JSON puis chiffrés avant stockage."
        facts.recovery_supported = None
        return facts

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
    def _read_env_keys(
        path: Path,
    ) -> list[tuple[str, str | None]]:
        items: list[tuple[str, str | None]] = []
        try:
            lines = path.read_text(
                encoding="utf-8",
                errors="ignore",
            ).splitlines()
        except OSError:
            return items

        for line in lines:
            stripped = line.strip()
            if (
                not stripped
                or stripped.startswith("#")
                or "=" not in stripped
            ):
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            if not key:
                continue
            value = value.strip()
            items.append(
                (
                    key,
                    value if value else None,
                )
            )
        return items

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
