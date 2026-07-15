from __future__ import annotations

from dataclasses import dataclass, field
import re
from pathlib import Path
from typing import Any

import yaml

from docforge.models import Project


@dataclass(slots=True)
class DeploymentFacts:
    compose_files: list[str] = field(default_factory=list)
    services: list[str] = field(default_factory=list)
    external_networks: list[str] = field(default_factory=list)
    named_volumes: list[str] = field(default_factory=list)
    required_env_files: list[str] = field(default_factory=list)
    make_targets: list[str] = field(default_factory=list)
    traefik_enabled: bool = False
    prerequisites: list[str] = field(default_factory=list)
    migrations: list[str] = field(default_factory=list)
    validation_commands: list[str] = field(default_factory=list)


class DeploymentAnalyzer:
    def analyze(self, project: Project) -> DeploymentFacts:
        facts = DeploymentFacts(
            compose_files=list(project.docker.compose_files),
            services=sorted(
                service.name
                for service in project.docker.services
            ),
            named_volumes=sorted(project.docker.volumes),
            traefik_enabled=project.docker.uses_traefik,
        )

        for relative_path in project.docker.compose_files:
            self._analyze_compose(
                project.root / relative_path,
                facts,
            )

        self._analyze_makefile(project.root / "Makefile", facts)
        self._build_prerequisites(project, facts)

        return facts

    def _analyze_compose(
        self,
        path: Path,
        facts: DeploymentFacts,
    ) -> None:
        try:
            data: dict[str, Any] = (
                yaml.safe_load(
                    path.read_text(encoding="utf-8")
                )
                or {}
            )
        except (OSError, yaml.YAMLError):
            return

        networks = data.get("networks", {})

        if isinstance(networks, dict):
            for name, definition in networks.items():
                if (
                    isinstance(definition, dict)
                    and definition.get("external") is True
                    and name not in facts.external_networks
                ):
                    facts.external_networks.append(name)

        services = data.get("services", {})

        if not isinstance(services, dict):
            return

        for definition in services.values():
            if not isinstance(definition, dict):
                continue

            env_files = definition.get("env_file", [])

            if isinstance(env_files, str):
                env_files = [env_files]

            if isinstance(env_files, list):
                for env_file in env_files:
                    value = str(env_file)

                    if value not in facts.required_env_files:
                        facts.required_env_files.append(value)

    @staticmethod
    def _analyze_makefile(
        path: Path,
        facts: DeploymentFacts,
    ) -> None:
        try:
            lines = path.read_text(
                encoding="utf-8",
                errors="ignore",
            ).splitlines()
        except OSError:
            return

        targets: list[str] = []

        assignment_pattern = re.compile(
            r"^[A-Za-z_][A-Za-z0-9_]*\s*(?::=|\+=|\?=|=)"
        )

        for line in lines:
            stripped = line.strip()

            if (
                not stripped
                or line[0].isspace()
                or stripped.startswith("#")
                or ":" not in line
            ):
                continue

            if assignment_pattern.match(stripped):
                continue

            declaration = line.split(":", 1)[0].strip()

            for target in declaration.split():
                if (
                    target
                    and "%" not in target
                    and target.replace("-", "").replace("_", "").isalnum()
                ):
                    targets.append(target)

        facts.make_targets = sorted(set(targets))

        for target in ("migrate", "makemigrations"):
            if target in facts.make_targets:
                facts.migrations.append(f"make {target}")

        for target in ("check", "ps", "logs", "dps"):
            if target in facts.make_targets:
                facts.validation_commands.append(f"make {target}")

    @staticmethod
    def _build_prerequisites(
        project: Project,
        facts: DeploymentFacts,
    ) -> None:
        facts.prerequisites.append(
            "Docker et le plugin Docker Compose doivent être installés."
        )

        if facts.traefik_enabled:
            facts.prerequisites.append(
                "Le reverse proxy Traefik doit être opérationnel."
            )

        for network in sorted(facts.external_networks):
            facts.prerequisites.append(
                f"Le réseau Docker externe `{network}` doit exister."
            )

        for env_file in sorted(facts.required_env_files):
            if env_file.endswith(".local"):
                facts.prerequisites.append(
                    f"Le fichier secret `{env_file}` doit être présent localement."
                )
            else:
                facts.prerequisites.append(
                    f"Le fichier de configuration `{env_file}` doit être présent."
                )

        if project.environment.env_symlink_exists:
            target = project.environment.env_symlink_target
            facts.prerequisites.append(
                f"Le lien `.env` doit pointer vers `{target}` pour l’environnement actif."
            )
