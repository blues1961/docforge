from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


DEFAULT_REGISTRY_PATH = (
    Path.home()
    / ".config"
    / "project-assistant"
    / "projects.yml"
)


class ProjectRegistryError(RuntimeError):
    """Erreur liée au registre de projets."""


@dataclass(slots=True)
class RegisteredProject:
    name: str
    path: Path
    enabled: bool = True
    profile: str | None = None


class ProjectRegistry:
    def __init__(
        self,
        registry_path: Path | None = None,
    ) -> None:
        self.registry_path = (
            registry_path or DEFAULT_REGISTRY_PATH
        ).expanduser()

    def load(self) -> list[RegisteredProject]:
        if not self.registry_path.exists():
            return []

        try:
            data = yaml.safe_load(
                self.registry_path.read_text(
                    encoding="utf-8",
                )
            ) or {}
        except (OSError, yaml.YAMLError) as error:
            raise ProjectRegistryError(
                f"Impossible de lire {self.registry_path}: {error}"
            ) from error

        if not isinstance(data, dict):
            raise ProjectRegistryError(
                "La racine du registre doit être un objet YAML."
            )

        entries = data.get("projects", [])

        if not isinstance(entries, list):
            raise ProjectRegistryError(
                "'projects' doit être une liste."
            )

        projects: list[RegisteredProject] = []

        for entry in entries:
            if not isinstance(entry, dict):
                raise ProjectRegistryError(
                    "Chaque projet doit être un objet."
                )

            raw_path = entry.get("path")

            if not raw_path:
                raise ProjectRegistryError(
                    "Chaque projet doit définir 'path'."
                )

            path = Path(str(raw_path)).expanduser()

            projects.append(
                RegisteredProject(
                    name=str(
                        entry.get(
                            "name",
                            path.name,
                        )
                    ),
                    path=path,
                    enabled=bool(
                        entry.get("enabled", True)
                    ),
                    profile=(
                        str(entry["profile"])
                        if entry.get("profile")
                        else None
                    ),
                )
            )

        return projects

    def save(
        self,
        projects: list[RegisteredProject],
    ) -> None:
        self.registry_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data: dict[str, Any] = {
            "schema_version": 1,
            "projects": [
                {
                    "name": project.name,
                    "path": str(project.path),
                    "enabled": project.enabled,
                    **(
                        {"profile": project.profile}
                        if project.profile
                        else {}
                    ),
                }
                for project in sorted(
                    projects,
                    key=lambda item: item.name.casefold(),
                )
            ],
        }

        self.registry_path.write_text(
            yaml.safe_dump(
                data,
                allow_unicode=True,
                sort_keys=False,
                width=100,
            ),
            encoding="utf-8",
        )

    def add(
        self,
        path: Path,
        *,
        name: str | None = None,
        profile: str | None = None,
    ) -> RegisteredProject:
        resolved_path = path.expanduser().resolve()

        if not resolved_path.exists():
            raise FileNotFoundError(
                f"Projet introuvable : {resolved_path}"
            )

        if not resolved_path.is_dir():
            raise NotADirectoryError(
                f"Le chemin n'est pas un dossier : {resolved_path}"
            )

        projects = self.load()

        for project in projects:
            if project.path.expanduser().resolve() == resolved_path:
                project.name = name or project.name
                project.profile = profile or project.profile
                project.enabled = True
                self.save(projects)
                return project

        registered = RegisteredProject(
            name=name or resolved_path.name,
            path=resolved_path,
            enabled=True,
            profile=profile,
        )

        projects.append(registered)
        self.save(projects)

        return registered

    def remove(self, identifier: str) -> bool:
        projects = self.load()
        remaining: list[RegisteredProject] = []
        removed = False

        for project in projects:
            if (
                project.name == identifier
                or str(project.path) == identifier
            ):
                removed = True
                continue

            remaining.append(project)

        if removed:
            self.save(remaining)

        return removed
