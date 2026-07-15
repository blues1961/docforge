from __future__ import annotations

from pathlib import Path

from docforge.models import Project


MAX_FILE_CHARACTERS = 7_000
MAX_TOTAL_CHARACTERS = 28_000

COMMON_FILES = [
    "INVARIANTS.md",
    "README.md",
    "README_DEV.md",
    "CODEX_START.md",
    "AGENTS.md",
]

DOCUMENT_FILE_PATTERNS = {
    "docs/architecture.md": [
        "docker-compose.dev.yml",
        "docker-compose.prod.yml",
        "Makefile",
        ".env.dev",
        ".env.prod",
        "backend/requirements.txt",
        "frontend/package.json",
        "settings.py",
        "urls.py",
        "Dockerfile",
        "Dockerfile.dev",
        "Dockerfile.prod",
    ],
    "docs/deployment.md": [
        "docker-compose.prod.yml",
        "docker-compose.dev.yml",
        "Makefile",
        ".env.prod",
        ".env.dev",
        "README_DEV.md",
        "CODEX_START.md",
        "INVARIANTS.md",
        "Dockerfile",
        "Dockerfile.prod",
    ],
    "docs/api.md": [
        "urls.py",
        "views.py",
        "serializers.py",
        "models.py",
        "permissions.py",
        "docs/api.md",
    ],
}


class ProjectContextBuilder:
    def build_for_document(
        self,
        project: Project,
        document_path: str,
    ) -> str:
        selected_files = self._selected_files(
            project=project,
            document_path=document_path,
        )

        sections = [self._project_summary(project)]
        total_characters = len(sections[0])

        for relative_path in selected_files:
            if total_characters >= MAX_TOTAL_CHARACTERS:
                break

            content = self._safe_read(
                project.root / relative_path
            )

            if not content:
                continue

            remaining = MAX_TOTAL_CHARACTERS - total_characters
            content = content[: min(MAX_FILE_CHARACTERS, remaining)]

            section = (
                f"\n\n===== FICHIER: {relative_path} =====\n"
                f"{content}"
            )

            sections.append(section)
            total_characters += len(section)

        return "".join(sections)

    def _selected_files(
        self,
        project: Project,
        document_path: str,
    ) -> list[str]:
        patterns = DOCUMENT_FILE_PATTERNS.get(
            document_path,
            COMMON_FILES,
        )

        selected: list[str] = []

        for relative_path in project.files:
            path = Path(relative_path)
            name = path.name

            if relative_path in COMMON_FILES:
                selected.append(relative_path)
                continue

            if relative_path in patterns:
                selected.append(relative_path)
                continue

            if name in patterns:
                selected.append(relative_path)

        return list(dict.fromkeys(selected))

    @staticmethod
    def _project_summary(project: Project) -> str:
        technologies = ", ".join(
            technology.name
            for technology in project.technologies
        ) or "aucune"

        services = ", ".join(
            service.name
            for service in project.docker.services
        ) or "aucun"

        return f"""===== INVENTAIRE DÉTERMINISTE =====
Projet: {project.name}
Profil: {project.profile}
Langages: {", ".join(project.languages)}
Frameworks: {", ".join(project.frameworks)}
Technologies: {technologies}
Environnement actif: {project.environment.active_environment or "inconnu"}
Lien .env: {project.environment.env_symlink_target or "absent"}
Fichiers Compose: {", ".join(project.docker.compose_files) or "aucun"}
Services Docker: {services}
Réseaux Docker: {", ".join(project.docker.networks) or "aucun"}
Volumes Docker: {", ".join(project.docker.volumes) or "aucun"}
Traefik: {"oui" if project.docker.uses_traefik else "non"}
"""

    @staticmethod
    def _safe_read(path: Path) -> str:
        if path.name == ".env":
            return ""

        if path.name.endswith(".local"):
            return ""

        try:
            if path.stat().st_size > 1_000_000:
                return ""

            return path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except OSError:
            return ""
