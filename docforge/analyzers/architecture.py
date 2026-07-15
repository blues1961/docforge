from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from docforge.models import Project


@dataclass(slots=True)
class ArchitectureService:
    name: str
    environments: list[str] = field(default_factory=list)
    image: str | None = None
    build_contexts: list[str] = field(default_factory=list)
    ports: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    networks: list[str] = field(default_factory=list)
    volumes: list[str] = field(default_factory=list)
    traefik_routes: list[str] = field(default_factory=list)
    healthcheck: bool = False


@dataclass(slots=True)
class ArchitectureFacts:
    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)

    compose_files: list[str] = field(default_factory=list)
    services: list[ArchitectureService] = field(default_factory=list)
    networks: list[str] = field(default_factory=list)
    external_networks: list[str] = field(default_factory=list)
    volumes: list[str] = field(default_factory=list)

    frontend_services: list[str] = field(default_factory=list)
    backend_services: list[str] = field(default_factory=list)
    database_services: list[str] = field(default_factory=list)

    uses_traefik: bool = False
    uses_postgresql: bool = False
    environment_files: list[str] = field(default_factory=list)
    architecture_documents: list[str] = field(default_factory=list)


class ArchitectureAnalyzer:
    def analyze(self, project: Project) -> ArchitectureFacts:
        facts = ArchitectureFacts(
            languages=sorted(project.languages),
            frameworks=sorted(project.frameworks),
            technologies=sorted(
                technology.name
                for technology in project.technologies
            ),
            compose_files=list(project.docker.compose_files),
            networks=sorted(project.docker.networks),
            volumes=sorted(project.docker.volumes),
            uses_traefik=project.docker.uses_traefik,
            uses_postgresql=any(
                technology.name == "PostgreSQL"
                for technology in project.technologies
            ),
            environment_files=sorted(
                project.environment.versioned_files
                + project.environment.local_secret_files
            ),
            architecture_documents=sorted(
                path
                for path in project.files
                if path.endswith(".md")
                and (
                    path in {
                        "README.md",
                        "README_DEV.md",
                        "CODEX_START.md",
                        "AGENTS.md",
                        "INVARIANTS.md",
                    }
                    or path.startswith("docs/")
                )
            ),
        )

        services_by_name: dict[str, ArchitectureService] = {}

        for compose_file in facts.compose_files:
            self._analyze_compose_file(
                project=project,
                relative_path=compose_file,
                facts=facts,
                services_by_name=services_by_name,
            )

        facts.services = sorted(
            services_by_name.values(),
            key=lambda service: service.name,
        )

        self._classify_services(facts)

        facts.external_networks = sorted(
            set(facts.external_networks)
        )
        facts.networks = sorted(set(facts.networks))
        facts.volumes = sorted(set(facts.volumes))

        return facts

    def _analyze_compose_file(
        self,
        *,
        project: Project,
        relative_path: str,
        facts: ArchitectureFacts,
        services_by_name: dict[str, ArchitectureService],
    ) -> None:
        path = project.root / relative_path

        try:
            data: dict[str, Any] = (
                yaml.safe_load(
                    path.read_text(encoding="utf-8")
                )
                or {}
            )
        except (OSError, yaml.YAMLError):
            return

        environment = self._compose_environment(relative_path)

        networks = data.get("networks", {})

        if isinstance(networks, dict):
            for network_name, definition in networks.items():
                if network_name not in facts.networks:
                    facts.networks.append(network_name)

                if (
                    isinstance(definition, dict)
                    and definition.get("external") is True
                ):
                    facts.external_networks.append(network_name)

        volumes = data.get("volumes", {})

        if isinstance(volumes, dict):
            facts.volumes.extend(
                str(name)
                for name in volumes
            )

        services = data.get("services", {})

        if not isinstance(services, dict):
            return

        for service_name, definition in services.items():
            if not isinstance(definition, dict):
                continue

            service = services_by_name.setdefault(
                service_name,
                ArchitectureService(name=service_name),
            )

            if environment not in service.environments:
                service.environments.append(environment)

            image = definition.get("image")

            if image and service.image is None:
                service.image = str(image)

            build_context = self._extract_build_context(
                definition.get("build")
            )

            if (
                build_context
                and build_context not in service.build_contexts
            ):
                service.build_contexts.append(build_context)

            self._extend_unique(
                service.ports,
                self._string_list(definition.get("ports", [])),
            )

            self._extend_unique(
                service.depends_on,
                self._depends_on_list(
                    definition.get("depends_on", [])
                ),
            )

            self._extend_unique(
                service.networks,
                self._network_list(
                    definition.get("networks", [])
                ),
            )

            self._extend_unique(
                service.volumes,
                self._string_list(
                    definition.get("volumes", [])
                ),
            )

            service.healthcheck = (
                service.healthcheck
                or isinstance(
                    definition.get("healthcheck"),
                    dict,
                )
            )

            labels = self._label_list(
                definition.get("labels", [])
            )

            for label in labels:
                if (
                    "traefik.http.routers." in label
                    and ".rule=" in label
                ):
                    route = label.split("=", 1)[1].strip()

                    if route not in service.traefik_routes:
                        service.traefik_routes.append(route)

    @staticmethod
    def _compose_environment(relative_path: str) -> str:
        name = Path(relative_path).name.casefold()

        if ".prod." in name:
            return "prod"

        if ".dev." in name:
            return "dev"

        return "commun"

    @staticmethod
    def _extract_build_context(value: Any) -> str | None:
        if isinstance(value, str):
            return value

        if isinstance(value, dict):
            context = value.get("context")

            if context is not None:
                return str(context)

        return None

    @staticmethod
    def _string_list(value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, (str, int, float)):
            return [str(value)]

        if isinstance(value, list):
            return [str(item) for item in value]

        return []

    @staticmethod
    def _depends_on_list(value: Any) -> list[str]:
        if isinstance(value, dict):
            return [str(name) for name in value]

        return ArchitectureAnalyzer._string_list(value)

    @staticmethod
    def _network_list(value: Any) -> list[str]:
        if isinstance(value, dict):
            return [str(name) for name in value]

        return ArchitectureAnalyzer._string_list(value)

    @staticmethod
    def _label_list(value: Any) -> list[str]:
        if isinstance(value, dict):
            return [
                f"{key}={label_value}"
                for key, label_value in value.items()
            ]

        return ArchitectureAnalyzer._string_list(value)

    @staticmethod
    def _extend_unique(
        destination: list[str],
        values: list[str],
    ) -> None:
        for value in values:
            if value not in destination:
                destination.append(value)

    @staticmethod
    def _classify_services(
        facts: ArchitectureFacts,
    ) -> None:
        for service in facts.services:
            normalized = service.name.casefold()
            image = (service.image or "").casefold()
            builds = " ".join(
                service.build_contexts
            ).casefold()

            if (
                normalized in {"db", "database", "postgres"}
                or "postgres" in image
            ):
                facts.database_services.append(service.name)
                continue

            if (
                normalized in {"backend", "api", "django"}
                or "backend" in builds
            ):
                facts.backend_services.append(service.name)
                continue

            if (
                normalized in {"frontend", "vite", "web"}
                or "frontend" in builds
                or "node" in image
                or "nginx" in image
                or "caddy" in image
            ):
                facts.frontend_services.append(service.name)
