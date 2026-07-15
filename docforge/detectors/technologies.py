from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from docforge.models import Project, Technology


class TechnologyDetector:
    def detect(self, project: Project) -> Project:
        self._detect_django(project)
        self._detect_react_and_vite(project)
        self._detect_docker_compose(project)
        self._detect_postgresql(project)
        self._detect_traefik(project)

        return project

    def _detect_django(self, project: Project) -> None:
        evidence: list[str] = []

        for candidate in (
            "manage.py",
            "backend/manage.py",
        ):
            if candidate in project.files:
                evidence.append(candidate)

        django_settings = [
            path
            for path in project.files
            if path.endswith("/settings.py") or path == "settings.py"
        ]
        evidence.extend(django_settings)

        requirements_files = [
            path
            for path in project.files
            if Path(path).name in {
                "requirements.txt",
                "requirements-dev.txt",
                "requirements-prod.txt",
                "pyproject.toml",
            }
        ]

        for relative_path in requirements_files:
            content = self._safe_read(project.root / relative_path)

            if re.search(r"\bdjango\b", content, re.IGNORECASE):
                evidence.append(relative_path)

        if evidence:
            project.add_framework("Django")
            project.add_technology(
                Technology(
                    name="Django",
                    category="backend-framework",
                    evidence=sorted(set(evidence)),
                )
            )

    def _detect_react_and_vite(self, project: Project) -> None:
        package_files = [
            path
            for path in project.files
            if Path(path).name == "package.json"
        ]

        for relative_path in package_files:
            path = project.root / relative_path

            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                project.add_finding(
                    code="DET001",
                    message="Impossible d'analyser package.json.",
                    severity="warning",
                    path=relative_path,
                )
                continue

            dependencies = {
                **data.get("dependencies", {}),
                **data.get("devDependencies", {}),
            }

            if "react" in dependencies:
                project.add_framework("React")
                project.add_technology(
                    Technology(
                        name="React",
                        category="frontend-framework",
                        version=dependencies.get("react"),
                        evidence=[relative_path],
                    )
                )

            if "vite" in dependencies:
                project.add_framework("Vite")
                project.add_technology(
                    Technology(
                        name="Vite",
                        category="frontend-build-tool",
                        version=dependencies.get("vite"),
                        evidence=[relative_path],
                    )
                )

    def _detect_docker_compose(self, project: Project) -> None:
        compose_files = [
            path
            for path in project.files
            if Path(path).name.startswith("docker-compose")
            and Path(path).suffix in {".yml", ".yaml"}
        ]

        if not compose_files:
            return

        project.docker.compose_files = sorted(compose_files)

        project.add_technology(
            Technology(
                name="Docker Compose",
                category="orchestration",
                evidence=sorted(compose_files),
            )
        )

        for relative_path in compose_files:
            path = project.root / relative_path

            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except (OSError, yaml.YAMLError):
                project.add_finding(
                    code="DET002",
                    message="Impossible d'analyser le fichier Docker Compose.",
                    severity="warning",
                    path=relative_path,
                )
                continue

            services = data.get("services", {})

            if isinstance(services, dict):
                for service_name in services:
                    if not any(
                        service.name == service_name
                        for service in project.docker.services
                    ):
                        from docforge.models import DockerService

                        project.docker.services.append(
                            DockerService(name=service_name)
                        )

            networks = data.get("networks", {})
            if isinstance(networks, dict):
                for network_name in networks:
                    if network_name not in project.docker.networks:
                        project.docker.networks.append(network_name)

            volumes = data.get("volumes", {})
            if isinstance(volumes, dict):
                for volume_name in volumes:
                    if volume_name not in project.docker.volumes:
                        project.docker.volumes.append(volume_name)

    def _detect_postgresql(self, project: Project) -> None:
        evidence: list[str] = []

        for relative_path in project.docker.compose_files:
            content = self._safe_read(project.root / relative_path)

            if re.search(r"\bpostgres(?:ql)?\b", content, re.IGNORECASE):
                evidence.append(relative_path)

        requirements_files = [
            path
            for path in project.files
            if Path(path).name in {
                "requirements.txt",
                "requirements-dev.txt",
                "requirements-prod.txt",
                "pyproject.toml",
            }
        ]

        for relative_path in requirements_files:
            content = self._safe_read(project.root / relative_path)

            if re.search(
                r"\b(psycopg|psycopg2|postgresql)\b",
                content,
                re.IGNORECASE,
            ):
                evidence.append(relative_path)

        if evidence:
            project.add_technology(
                Technology(
                    name="PostgreSQL",
                    category="database",
                    evidence=sorted(set(evidence)),
                )
            )

    def _detect_traefik(self, project: Project) -> None:
        evidence: list[str] = []

        for relative_path in project.docker.compose_files:
            content = self._safe_read(project.root / relative_path)

            if "traefik." in content.lower() or "traefik:" in content.lower():
                evidence.append(relative_path)

        if evidence:
            project.docker.uses_traefik = True
            project.add_technology(
                Technology(
                    name="Traefik",
                    category="reverse-proxy",
                    evidence=sorted(set(evidence)),
                )
            )

    @staticmethod
    def _safe_read(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""
