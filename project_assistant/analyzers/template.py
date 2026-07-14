from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from project_assistant.analyzers.architecture import (
    ArchitectureAnalyzer,
    ArchitectureFacts,
)
from project_assistant.analyzers.deployment import (
    DeploymentAnalyzer,
    DeploymentFacts,
)
from project_assistant.detectors import TechnologyDetector
from project_assistant.models import Project
from project_assistant.scanners import FileSystemScanner


DOCUMENT_CANDIDATES = [
    "README.md",
    "README_DEV.md",
    "CODEX_START.md",
    "AGENTS.md",
    "INVARIANTS.md",
    "docs/architecture.md",
    "docs/specification.md",
    "docs/api.md",
    "docs/deployment.md",
]

ENVIRONMENT_CANDIDATES = [
    ".env",
    ".env.dev",
    ".env.prod",
    ".env.local",
    ".env.dev.example",
    ".env.prod.example",
    ".env.local.example",
    ".env.template.example",
]

COMPOSE_CANDIDATES = [
    "docker-compose.dev.yml",
    "docker-compose.prod.yml",
]

GITHUB_WORKFLOW_PREFIX = ".github/workflows/"
SCRIPT_PREFIX = "scripts/"


@dataclass(slots=True)
class TemplateFileRule:
    path: str
    exists: bool
    kind: str
    source_authoritative: bool


@dataclass(slots=True)
class InvariantSection:
    level: int
    title: str
    body: str


@dataclass(slots=True)
class TemplateFacts:
    name: str
    root: str

    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)

    documents: list[TemplateFileRule] = field(default_factory=list)
    environment_files: list[TemplateFileRule] = field(
        default_factory=list
    )
    compose_files: list[TemplateFileRule] = field(
        default_factory=list
    )

    root_files: list[str] = field(default_factory=list)
    root_directories: list[str] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    github_workflows: list[str] = field(default_factory=list)

    make_targets: list[str] = field(default_factory=list)
    invariant_sections: list[InvariantSection] = field(
        default_factory=list
    )

    env_template_file: str | None = None
    env_symlink_target: str | None = None
    env_symlink_exists: bool = False
    secrets_policy_detected: bool = False
    production_host_sentinel: bool = False

    architecture: ArchitectureFacts | None = None
    deployment: DeploymentFacts | None = None


class TemplateAnalyzer:
    def analyze(self, root: Path) -> TemplateFacts:
        root = root.expanduser().resolve()

        project = FileSystemScanner().scan(root)
        TechnologyDetector().detect(project)

        architecture = ArchitectureAnalyzer().analyze(project)
        deployment = DeploymentAnalyzer().analyze(project)

        invariant_sections = self._extract_markdown_sections(
            root / "INVARIANTS.md"
        )

        env_template_file = next(
            (
                candidate
                for candidate in (
                    ".env.template.example",
                    ".env.local.example",
                    ".env.dev.example",
                )
                if (root / candidate).is_file()
            ),
            None,
        )

        return TemplateFacts(
            name=project.name,
            root=str(project.root),
            languages=sorted(project.languages),
            frameworks=sorted(project.frameworks),
            technologies=sorted(
                technology.name
                for technology in project.technologies
            ),
            documents=self._file_rules(
                project,
                DOCUMENT_CANDIDATES,
                kind="documentation",
            ),
            environment_files=self._file_rules(
                project,
                ENVIRONMENT_CANDIDATES,
                kind="environment",
            ),
            compose_files=self._file_rules(
                project,
                COMPOSE_CANDIDATES,
                kind="compose",
            ),
            root_files=self._root_files(project),
            root_directories=self._root_directories(project),
            scripts=self._files_with_prefix(
                project,
                SCRIPT_PREFIX,
            ),
            github_workflows=self._files_with_prefix(
                project,
                GITHUB_WORKFLOW_PREFIX,
            ),
            make_targets=list(deployment.make_targets),
            invariant_sections=invariant_sections,
            env_template_file=env_template_file,
            env_symlink_target=(
                project.environment.env_symlink_target
            ),
            env_symlink_exists=(
                project.environment.env_symlink_exists
            ),
            secrets_policy_detected=self._detect_secrets_policy(
                project
            ),
            production_host_sentinel=(
                project.environment.production_host_sentinel
            ),
            architecture=architecture,
            deployment=deployment,
        )

    @staticmethod
    def _file_rules(
        project: Project,
        paths: list[str],
        *,
        kind: str,
    ) -> list[TemplateFileRule]:
        project_files = set(project.files)
        project_symlinks = set(project.symlinks)

        rules: list[TemplateFileRule] = []

        for path in paths:
            exists = (
                path in project_files
                or path in project_symlinks
            )

            rules.append(
                TemplateFileRule(
                    path=path,
                    exists=exists,
                    kind=kind,
                    source_authoritative=exists,
                )
            )

        return rules

    @staticmethod
    def _root_files(project: Project) -> list[str]:
        return sorted(
            path
            for path in project.files
            if "/" not in path
        )

    @staticmethod
    def _root_directories(project: Project) -> list[str]:
        directories: set[str] = set()

        for relative_path in project.files:
            path = Path(relative_path)

            if len(path.parts) > 1:
                directories.add(path.parts[0])

        return sorted(directories)

    @staticmethod
    def _files_with_prefix(
        project: Project,
        prefix: str,
    ) -> list[str]:
        return sorted(
            path
            for path in project.files
            if path.startswith(prefix)
        )

    @staticmethod
    def _extract_markdown_sections(
        path: Path,
    ) -> list[InvariantSection]:
        try:
            lines = path.read_text(
                encoding="utf-8",
                errors="ignore",
            ).splitlines()
        except OSError:
            return []

        sections: list[InvariantSection] = []
        current_level: int | None = None
        current_title: str | None = None
        current_body: list[str] = []

        def flush() -> None:
            nonlocal current_level
            nonlocal current_title
            nonlocal current_body

            if current_level is None or current_title is None:
                return

            sections.append(
                InvariantSection(
                    level=current_level,
                    title=current_title,
                    body="\n".join(current_body).strip(),
                )
            )

        for line in lines:
            match = re.match(
                r"^(#{1,6})\s+(.+?)\s*$",
                line,
            )

            if match:
                flush()
                current_level = len(match.group(1))
                current_title = match.group(2).strip()
                current_body = []
                continue

            if current_title is not None:
                current_body.append(line)

        flush()
        return sections

    @staticmethod
    def _detect_secrets_policy(
        project: Project,
    ) -> bool:
        candidates = [
            project.root / "INVARIANTS.md",
            project.root / "README_DEV.md",
            project.root / "CODEX_START.md",
            project.root / ".gitignore",
        ]

        patterns = [
            r"\.env\.local",
            r"\bsecret\b",
            r"\bsecrets\b",
            r"ne doit jamais.*git",
            r"non versionn",
        ]

        for path in candidates:
            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                ).casefold()
            except OSError:
                continue

            if any(
                re.search(pattern, content)
                for pattern in patterns
            ):
                return True

        return False
