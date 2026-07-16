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
class OperationalCommandFacts:
    name: str
    category: str
    command: str
    source: str
    target: str | None = None
    body: list[str] = field(default_factory=list)
    environments: list[str] = field(default_factory=list)


@dataclass(slots=True)
class OperationalCommandsFacts:
    commands: list[OperationalCommandFacts] = field(
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
class DjangoFacts:
    project_module: str | None = None
    settings_files: list[str] = field(default_factory=list)
    installed_apps: list[str] = field(default_factory=list)
    local_apps: list[str] = field(default_factory=list)
    models: list[DjangoModelFacts] = field(default_factory=list)
    routes: list[str] = field(default_factory=list)
    routers: list[str] = field(default_factory=list)
    auth_mechanisms: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    admin_enabled: bool = False
    migration_commands: list[str] = field(default_factory=list)
    create_admin_commands: list[str] = field(
        default_factory=list
    )
    database_engine: str | None = None
    database_configuration: list[str] = field(
        default_factory=list
    )
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
    source_paths: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CapabilityFacts:
    label: str
    status: str
    evidence: list[str] = field(default_factory=list)


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
                    body_line.startswith("\t")
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
                )
            )

        commands.sort(
            key=lambda item: (item.category, item.command)
        )
        return OperationalCommandsFacts(commands=commands)

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

        models = self._parse_django_models(models_path)
        migration_commands = [
            item.command
            for item in operational_commands.commands
            if item.category == "migrations"
        ]
        if "python manage.py ensure_admin" in self._read_text(
            project.root / "scripts" / "migrate.sh"
        ):
            create_admin_commands = [
                "python manage.py ensure_admin"
            ]
        else:
            create_admin_commands = []

        database_engine = self._extract_database_engine(
            settings_text
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

        return DjangoFacts(
            project_module="App",
            settings_files=[
                "backend/App/settings.py"
            ],
            installed_apps=installed_apps,
            local_apps=local_apps,
            models=models,
            routes=sorted(
                {
                    route.path
                    for route in api.routes
                }
            ),
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
            source_paths=[
                "frontend/package.json",
                "frontend/src/main.jsx",
                "frontend/src/App.jsx",
                "frontend/src/api.js",
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
        ) -> None:
            capabilities.append(
                CapabilityFacts(
                    label=label,
                    status=status,
                    evidence=list(evidence),
                )
            )

        model_names = {model.name for model in django.models}
        api_calls = set(react.api_calls)

        if "Contact" in model_names and "GET /contacts/" in api_calls:
            add(
                "Consulter les contacts",
                "backend/api/models.py",
                "frontend/src/api.js",
            )
        if "POST /contacts/" in api_calls:
            add(
                "Créer un contact",
                "frontend/src/api.js",
                "backend/api/views.py",
            )
        if "PATCH /contacts/{id}/" in api_calls:
            add(
                "Modifier un contact",
                "frontend/src/api.js",
                "backend/api/views.py",
            )
        if "DELETE /contacts/{id}/" in api_calls:
            add(
                "Supprimer un contact",
                "frontend/src/api.js",
                "backend/api/views.py",
            )
        if "POST /contacts/{id}/sync_birthday/" in api_calls:
            add(
                "Synchroniser l’anniversaire d’un contact",
                "frontend/src/api.js",
                "backend/api/views.py",
            )
        if "GET /users/" in api_calls and "POST /users/{id}/reset_password/" in api_calls:
            add(
                "Administrer les utilisateurs",
                "frontend/src/App.jsx",
                "backend/api/views.py",
            )
        if "Déverrouillage local du coffre privé" in react.auth_mechanisms:
            add(
                "Gérer des contacts privés chiffrés côté client",
                "frontend/src/App.jsx",
                "frontend/src/crypto.js",
            )
        if any(
            route.startswith("/auth/")
            for route in django.routes
        ):
            add(
                "S’authentifier à l’application",
                "backend/api/urls.py",
                "frontend/src/api.js",
                status="detected",
            )
        if any(
            route.startswith("/integrations/contacts/")
            for route in django.routes
        ):
            add(
                "Exposer une intégration interne de contacts",
                "backend/api/urls.py",
                "backend/api/views.py",
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
