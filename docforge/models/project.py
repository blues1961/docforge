from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Document:
    path: str
    exists: bool = False
    required: bool = False
    category: str | None = None
    size_bytes: int = 0
    sections_found: list[str] = field(default_factory=list)
    sections_missing: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Technology:
    name: str
    category: str
    version: str | None = None
    evidence: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DockerService:
    name: str
    image: str | None = None
    build_context: str | None = None
    ports: list[str] = field(default_factory=list)
    networks: list[str] = field(default_factory=list)
    volumes: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DockerConfiguration:
    compose_files: list[str] = field(default_factory=list)
    services: list[DockerService] = field(default_factory=list)
    networks: list[str] = field(default_factory=list)
    volumes: list[str] = field(default_factory=list)
    uses_traefik: bool = False


@dataclass(slots=True)
class GitRepository:
    is_repository: bool = False
    branch: str | None = None
    remote_url: str | None = None
    clean: bool | None = None
    modified_files: list[str] = field(default_factory=list)
    untracked_files: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EnvironmentConfiguration:
    env_symlink_exists: bool = False
    env_symlink_target: str | None = None
    env_symlink_target_exists: bool = False
    active_environment: str | None = None

    versioned_files: list[str] = field(default_factory=list)
    local_secret_files: list[str] = field(default_factory=list)
    example_files: list[str] = field(default_factory=list)

    production_host_sentinel: bool = False


@dataclass(slots=True)
class Finding:
    code: str
    message: str
    severity: str = "info"
    path: str | None = None
    recommendation: str | None = None


@dataclass(slots=True)
class ProjectStatistics:
    file_count: int = 0
    directory_count: int = 0
    symlink_count: int = 0
    total_size_bytes: int = 0
    files_by_extension: dict[str, int] = field(default_factory=dict)


@dataclass(slots=True)
class Project:
    name: str
    root: Path
    profile: str = "base"

    files: list[str] = field(default_factory=list)
    directories: list[str] = field(default_factory=list)
    symlinks: dict[str, str] = field(default_factory=dict)

    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    technologies: list[Technology] = field(default_factory=list)

    documents: list[Document] = field(default_factory=list)
    docker: DockerConfiguration = field(default_factory=DockerConfiguration)
    git: GitRepository = field(default_factory=GitRepository)
    environment: EnvironmentConfiguration = field(
        default_factory=EnvironmentConfiguration
    )
    statistics: ProjectStatistics = field(default_factory=ProjectStatistics)

    findings: list[Finding] = field(default_factory=list)

    def add_language(self, language: str) -> None:
        if language not in self.languages:
            self.languages.append(language)

    def add_framework(self, framework: str) -> None:
        if framework not in self.frameworks:
            self.frameworks.append(framework)

    def add_technology(self, technology: Technology) -> None:
        if not any(
            item.name == technology.name and item.category == technology.category
            for item in self.technologies
        ):
            self.technologies.append(technology)

    def add_finding(
        self,
        code: str,
        message: str,
        severity: str = "info",
        path: str | None = None,
        recommendation: str | None = None,
    ) -> None:
        self.findings.append(
            Finding(
                code=code,
                message=message,
                severity=severity,
                path=path,
                recommendation=recommendation,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["root"] = str(self.root)
        return data
