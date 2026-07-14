from __future__ import annotations

from dataclasses import dataclass, field

from project_assistant.analyzers.api import ApiAnalyzer
from project_assistant.analyzers.architecture import ArchitectureAnalyzer
from project_assistant.analyzers.deployment import DeploymentAnalyzer
from project_assistant.models import Project


@dataclass(slots=True)
class ReadmeFacts:
    project_name: str

    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)

    services: list[str] = field(default_factory=list)
    compose_files: list[str] = field(default_factory=list)
    external_networks: list[str] = field(default_factory=list)
    named_volumes: list[str] = field(default_factory=list)

    api_route_count: int = 0
    api_groups: list[str] = field(default_factory=list)

    make_targets: list[str] = field(default_factory=list)
    environments: list[str] = field(default_factory=list)

    documentation_files: list[str] = field(default_factory=list)

    uses_django: bool = False
    uses_react: bool = False
    uses_postgresql: bool = False
    uses_docker_compose: bool = False
    uses_traefik: bool = False

    env_symlink_target: str | None = None
    env_symlink_exists: bool = False


class ReadmeAnalyzer:
    DOCUMENTATION_FILES = (
        "README_DEV.md",
        "CODEX_START.md",
        "AGENTS.md",
        "INVARIANTS.md",
        "docs/architecture.md",
        "docs/specification.md",
        "docs/api.md",
        "docs/deployment.md",
    )

    def analyze(
        self,
        project: Project,
    ) -> ReadmeFacts:
        architecture = ArchitectureAnalyzer().analyze(project)
        deployment = DeploymentAnalyzer().analyze(project)
        api = ApiAnalyzer().analyze(project)

        technologies = sorted(
            technology.name
            for technology in project.technologies
        )

        environments: list[str] = []

        if (project.root / ".env.dev").is_file():
            environments.append("dev")

        if (project.root / ".env.prod").is_file():
            environments.append("prod")

        api_groups = sorted(
            {
                self._route_group(route.path)
                for route in api.routes
                if route.path
            },
            key=str.casefold,
        )

        documentation_files = [
            path
            for path in self.DOCUMENTATION_FILES
            if (project.root / path).is_file()
        ]

        return ReadmeFacts(
            project_name=project.name,
            languages=sorted(project.languages),
            frameworks=sorted(project.frameworks),
            technologies=technologies,
            services=sorted(
                service.name
                for service in architecture.services
            ),
            compose_files=list(architecture.compose_files),
            external_networks=list(
                architecture.external_networks
            ),
            named_volumes=list(architecture.volumes),
            api_route_count=len(api.routes),
            api_groups=api_groups,
            make_targets=list(deployment.make_targets),
            environments=environments,
            documentation_files=documentation_files,
            uses_django="Django" in project.frameworks,
            uses_react="React" in project.frameworks,
            uses_postgresql=(
                "PostgreSQL" in technologies
            ),
            uses_docker_compose=(
                "Docker Compose" in technologies
            ),
            uses_traefik=architecture.uses_traefik,
            env_symlink_target=(
                project.environment.env_symlink_target
            ),
            env_symlink_exists=(
                project.environment.env_symlink_exists
            ),
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
