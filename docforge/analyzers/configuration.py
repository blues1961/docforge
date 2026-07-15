from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from docforge.models import Project
from docforge.storage_paths import (
    PROJECT_CONFIG_FILENAME,
    ensure_project_storage_migrated,
    ensure_user_storage_migrated,
    project_config_path,
    project_state_root,
    user_config_root,
)


@dataclass(slots=True)
class ConfigurationFileFacts:
    path: str
    scope: str
    exists: bool
    tracked_candidate: bool
    description: str


@dataclass(slots=True)
class ConfigurationFacts:
    user_config_root: str
    project_state_root: str
    project_config_file: str
    report_root: str

    files: list[ConfigurationFileFacts] = field(
        default_factory=list
    )
    ignored_paths: list[str] = field(default_factory=list)
    environment_variables: list[str] = field(
        default_factory=list
    )

    @property
    def existing_file_count(self) -> int:
        return sum(
            1
            for item in self.files
            if item.exists
        )


class ConfigurationAnalyzer:
    USER_CONFIG_ROOT = "~/.config/docforge"
    PROJECT_STATE_ROOT = ".docforge"
    PROJECT_CONFIG_FILE = PROJECT_CONFIG_FILENAME
    REPORT_ROOT = "reports"

    def analyze(
        self,
        project: Project,
    ) -> ConfigurationFacts:
        ensure_user_storage_migrated()
        ensure_project_storage_migrated(project.root)

        gitignore = self._read_gitignore(project.root)
        ignored_paths = self._detect_ignored_paths(
            gitignore
        )

        files = [
            ConfigurationFileFacts(
                path=(
                    "~/.config/docforge/"
                    "projects.yml"
                ),
                scope="utilisateur",
                exists=self._user_path_exists(
                    "projects.yml"
                ),
                tracked_candidate=False,
                description=(
                    "Registre des projets connus par "
                    "docforge."
                ),
            ),
            ConfigurationFileFacts(
                path=(
                    "~/.config/docforge/"
                    "invariant-baseline.json"
                ),
                scope="utilisateur",
                exists=self._user_path_exists(
                    "invariant-baseline.json"
                ),
                tracked_candidate=False,
                description=(
                    "Empreintes approuvées des documents "
                    "d’invariants protégés."
                ),
            ),
            ConfigurationFileFacts(
                path=self.PROJECT_CONFIG_FILE,
                scope="projet",
                exists=project_config_path(project.root).is_file(),
                tracked_candidate=True,
                description=(
                    "Configuration locale du projet pour le profil, "
                    "la sélection documentaire et les exclusions de scan."
                ),
            ),
            ConfigurationFileFacts(
                path=".docforge/cache/",
                scope="projet",
                exists=(
                    project_state_root(project.root)
                    / "cache"
                ).exists(),
                tracked_candidate=False,
                description=(
                    "Cache local des faits et de "
                    "ProjectKnowledge."
                ),
            ),
            ConfigurationFileFacts(
                path=".docforge/preview/",
                scope="projet",
                exists=(
                    project_state_root(project.root)
                    / "preview"
                ).exists(),
                tracked_candidate=False,
                description=(
                    "Aperçus documentaires générés avant "
                    "application."
                ),
            ),
            ConfigurationFileFacts(
                path="reports/",
                scope="dépôt",
                exists=(
                    project.root / "reports"
                ).exists(),
                tracked_candidate=True,
                description=(
                    "Rapports durables pouvant être suivis "
                    "par Git."
                ),
            ),
            ConfigurationFileFacts(
                path="pyproject.toml",
                scope="dépôt",
                exists=(
                    project.root / "pyproject.toml"
                ).is_file(),
                tracked_candidate=True,
                description=(
                    "Métadonnées du paquet, dépendances et "
                    "point d’entrée CLI."
                ),
            ),
            ConfigurationFileFacts(
                path=".gitignore",
                scope="dépôt",
                exists=(
                    project.root / ".gitignore"
                ).is_file(),
                tracked_candidate=True,
                description=(
                    "Exclusions Git, notamment caches, "
                    "aperçus et environnements virtuels."
                ),
            ),
        ]

        return ConfigurationFacts(
            user_config_root=self.USER_CONFIG_ROOT,
            project_state_root=self.PROJECT_STATE_ROOT,
            project_config_file=self.PROJECT_CONFIG_FILE,
            report_root=self.REPORT_ROOT,
            files=files,
            ignored_paths=ignored_paths,
            environment_variables=self._environment_variables(
                project.root
            ),
        )

    @staticmethod
    def _user_path_exists(filename: str) -> bool:
        return (user_config_root() / filename).exists()

    @staticmethod
    def _read_gitignore(root: Path) -> list[str]:
        path = root / ".gitignore"

        if not path.is_file():
            return []

        try:
            return path.read_text(
                encoding="utf-8",
                errors="ignore",
            ).splitlines()
        except OSError:
            return []

    @staticmethod
    def _detect_ignored_paths(
        lines: list[str],
    ) -> list[str]:
        relevant = {
            ".docforge/",
            ".venv/",
            "__pycache__/",
            "*.pyc",
            ".pytest_cache/",
        }

        normalized = {
            line.strip()
            for line in lines
            if line.strip()
            and not line.lstrip().startswith("#")
        }

        return sorted(
            value
            for value in relevant
            if value in normalized
            or value.rstrip("/") in normalized
        )

    @staticmethod
    def _environment_variables(
        root: Path,
    ) -> list[str]:
        variables: set[str] = set()

        for path in sorted(
            (root / "docforge").rglob("*.py")
        ):
            try:
                text = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except OSError:
                continue

            for line in text.splitlines():
                if "os.environ.get(" not in line:
                    continue

                fragment = line.split(
                    "os.environ.get(",
                    1,
                )[1]

                quote = (
                    '"'
                    if '"' in fragment
                    else "'"
                    if "'" in fragment
                    else None
                )

                if quote is None:
                    continue

                parts = fragment.split(quote)

                if len(parts) >= 3 and parts[1]:
                    variables.add(parts[1])

        return sorted(variables)
