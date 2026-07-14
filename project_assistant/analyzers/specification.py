from __future__ import annotations

from dataclasses import dataclass, field

from project_assistant.analyzers.api import (
    ApiAnalyzer,
    ApiFacts,
)
from project_assistant.analyzers.architecture import (
    ArchitectureAnalyzer,
    ArchitectureFacts,
)
from project_assistant.analyzers.deployment import (
    DeploymentAnalyzer,
    DeploymentFacts,
)
from project_assistant.models import Project


@dataclass(slots=True)
class SpecificationFacts:
    project_name: str
    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)

    frontend_services: list[str] = field(default_factory=list)
    backend_services: list[str] = field(default_factory=list)
    database_services: list[str] = field(default_factory=list)

    api_route_count: int = 0
    api_groups: list[str] = field(default_factory=list)

    compose_files: list[str] = field(default_factory=list)
    environments: list[str] = field(default_factory=list)
    make_targets: list[str] = field(default_factory=list)

    uses_django: bool = False
    uses_react: bool = False
    uses_postgresql: bool = False
    uses_docker_compose: bool = False
    uses_traefik: bool = False

    architecture: ArchitectureFacts | None = None
    deployment: DeploymentFacts | None = None
    api: ApiFacts | None = None


class SpecificationAnalyzer:
    def analyze(
        self,
        project: Project,
    ) -> SpecificationFacts:
        architecture = ArchitectureAnalyzer().analyze(project)
        deployment = DeploymentAnalyzer().analyze(project)
        api = ApiAnalyzer().analyze(project)

        service_names = {
            service.name
            for service in architecture.services
        }

        frontend_services = sorted(
            service
            for service in service_names
            if service in {"frontend", "vite", "web", "client"}
        )

        backend_services = sorted(
            service
            for service in service_names
            if service in {"backend", "api", "django", "server"}
        )

        database_services = sorted(
            service
            for service in service_names
            if service in {"db", "database", "postgres", "postgresql"}
        )

        api_groups = sorted(
            {
                self._route_group(route.path)
                for route in api.routes
                if route.path
            }
        )

        environments: list[str] = []

        if (project.root / ".env.dev").exists():
            environments.append("dev")

        if (project.root / ".env.prod").exists():
            environments.append("prod")

        technologies = sorted(
            technology.name
            for technology in project.technologies
        )

        return SpecificationFacts(
            project_name=project.name,
            languages=sorted(project.languages),
            frameworks=sorted(project.frameworks),
            technologies=technologies,
            frontend_services=frontend_services,
            backend_services=backend_services,
            database_services=database_services,
            api_route_count=len(api.routes),
            api_groups=api_groups,
            compose_files=list(architecture.compose_files),
            environments=environments,
            make_targets=list(deployment.make_targets),
            uses_django="Django" in project.frameworks,
            uses_react="React" in project.frameworks,
            uses_postgresql="PostgreSQL" in technologies,
            uses_docker_compose="Docker Compose" in technologies,
            uses_traefik=architecture.uses_traefik,
            architecture=architecture,
            deployment=deployment,
            api=api,
        )

    @staticmethod
    def _route_group(path: str) -> str:
        parts = [
            part
            for part in path.strip("/").split("/")
            if part and not part.startswith("{")
        ]

        if not parts:
            return "racine"

        if parts[0] == "api" and len(parts) > 1:
            return parts[1]

        return parts[0]
