from __future__ import annotations

import fnmatch
import os
from collections import Counter
from pathlib import Path

from docforge.models import Project


DEFAULT_EXCLUDED_PATHS = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".project-assistant",
    "data",
    "volumes",
    "backups",
}

DEFAULT_EXCLUDED_PATTERNS = {
    "*.pyc",
    "*.pyo",
    "*.sqlite3",
    "*.db",
    "*.pem",
    "*.key",
    "*.crt",
    "*.p12",
    "*.pfx",
    "*.local",
    "id_rsa*",
    "id_ed25519*",
}


class FileSystemScanner:
    def __init__(
        self,
        excluded_paths: set[str] | None = None,
        excluded_patterns: set[str] | None = None,
    ) -> None:
        self.excluded_paths = excluded_paths or DEFAULT_EXCLUDED_PATHS
        self.excluded_patterns = (
            excluded_patterns or DEFAULT_EXCLUDED_PATTERNS
        )

    def scan(self, root: Path) -> Project:
        root = root.expanduser().resolve()

        if not root.exists():
            raise FileNotFoundError(f"Le projet n'existe pas : {root}")

        if not root.is_dir():
            raise NotADirectoryError(
                f"Le chemin n'est pas un dossier : {root}"
            )

        project = Project(name=root.name, root=root)
        extensions: Counter[str] = Counter()

        self._scan_environment_metadata(project)

        for path in root.rglob("*"):
            relative_path = path.relative_to(root)

            if self._is_excluded(relative_path):
                continue

            relative_text = relative_path.as_posix()

            if path.is_symlink():
                self._register_symlink(project, path, relative_path)
                continue

            if path.is_dir():
                project.directories.append(relative_text)
                project.statistics.directory_count += 1
                continue

            if not path.is_file():
                continue

            project.files.append(relative_text)
            project.statistics.file_count += 1

            try:
                project.statistics.total_size_bytes += path.stat().st_size
            except OSError:
                project.add_finding(
                    code="FS001",
                    message="Impossible de lire les métadonnées du fichier.",
                    severity="warning",
                    path=relative_text,
                )

            extension = path.suffix.lower() or "[sans extension]"
            extensions[extension] += 1

        project.files.sort()
        project.directories.sort()
        project.symlinks = dict(sorted(project.symlinks.items()))
        project.statistics.files_by_extension = dict(
            sorted(
                extensions.items(),
                key=lambda item: (-item[1], item[0]),
            )
        )

        self._detect_languages(project)
        self._validate_environment_convention(project)

        return project

    def _is_excluded(self, relative_path: Path) -> bool:
        if any(
            part in self.excluded_paths
            for part in relative_path.parts
        ):
            return True

        name = relative_path.name

        if name == ".env":
            return False

        if name.endswith(".local"):
            return True

        return any(
            fnmatch.fnmatch(name, pattern)
            for pattern in self.excluded_patterns
        )

    def _register_symlink(
        self,
        project: Project,
        path: Path,
        relative_path: Path,
    ) -> None:
        relative_text = relative_path.as_posix()

        try:
            target = os.readlink(path)
        except OSError:
            project.add_finding(
                code="FS002",
                message="Impossible de lire la cible du lien symbolique.",
                severity="warning",
                path=relative_text,
            )
            return

        project.symlinks[relative_text] = target
        project.statistics.symlink_count += 1

    def _scan_environment_metadata(self, project: Project) -> None:
        root = project.root
        environment = project.environment

        env_link = root / ".env"

        if env_link.is_symlink():
            environment.env_symlink_exists = True

            try:
                target = os.readlink(env_link)
                environment.env_symlink_target = target

                resolved_target = (root / target).resolve()
                environment.env_symlink_target_exists = (
                    resolved_target.exists()
                )

                target_name = Path(target).name

                if target_name == ".env.dev":
                    environment.active_environment = "dev"
                elif target_name == ".env.prod":
                    environment.active_environment = "prod"
                else:
                    environment.active_environment = "unknown"

            except OSError:
                project.add_finding(
                    code="ENV001",
                    message="Impossible de lire la cible du lien .env.",
                    severity="error",
                    path=".env",
                )

        for candidate in sorted(root.glob(".env*")):
            name = candidate.name

            if name == ".env":
                continue

            if candidate.is_symlink():
                continue

            if name.endswith(".local"):
                environment.local_secret_files.append(name)
            elif name.endswith((".example", ".template")):
                environment.example_files.append(name)
            elif candidate.is_file():
                environment.versioned_files.append(name)

        environment.production_host_sentinel = (
            root / ".production_host"
        ).exists()

    def _validate_environment_convention(self, project: Project) -> None:
        environment = project.environment

        if ".env.dev" not in environment.versioned_files:
            project.add_finding(
                code="ENV002",
                message="Le fichier versionné .env.dev est absent.",
                severity="warning",
                path=".env.dev",
                recommendation="Créer .env.dev pour l'environnement local.",
            )

        if ".env.prod" not in environment.versioned_files:
            project.add_finding(
                code="ENV003",
                message="Le fichier versionné .env.prod est absent.",
                severity="warning",
                path=".env.prod",
                recommendation="Créer .env.prod pour la production.",
            )

        if not environment.env_symlink_exists:
            project.add_finding(
                code="ENV004",
                message=".env n'est pas un lien symbolique.",
                severity="warning",
                path=".env",
                recommendation=(
                    "Créer un lien .env vers .env.dev ou .env.prod."
                ),
            )
            return

        if not environment.env_symlink_target_exists:
            project.add_finding(
                code="ENV005",
                message="La cible du lien symbolique .env n'existe pas.",
                severity="error",
                path=".env",
                recommendation="Corriger la cible du lien symbolique.",
            )

        if environment.active_environment == "unknown":
            project.add_finding(
                code="ENV006",
                message=(
                    ".env pointe vers une cible différente de "
                    ".env.dev ou .env.prod."
                ),
                severity="warning",
                path=".env",
                recommendation=(
                    "Utiliser .env.dev ou .env.prod comme cible."
                ),
            )

    @staticmethod
    def _detect_languages(project: Project) -> None:
        extensions = project.statistics.files_by_extension

        language_extensions = {
            "Python": {".py"},
            "JavaScript": {".js", ".jsx", ".mjs", ".cjs"},
            "TypeScript": {".ts", ".tsx"},
            "HTML": {".html", ".htm"},
            "CSS": {".css", ".scss", ".sass"},
            "Shell": {".sh", ".bash"},
            "Markdown": {".md"},
            "YAML": {".yml", ".yaml"},
            "JSON": {".json"},
            "SQL": {".sql"},
            "Go": {".go"},
            "Rust": {".rs"},
        }

        for language, known_extensions in language_extensions.items():
            if any(
                extension in extensions
                for extension in known_extensions
            ):
                project.add_language(language)
