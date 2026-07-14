from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from project_assistant.models import Project


@dataclass(slots=True)
class PyprojectFacts:
    exists: bool = False
    path: str | None = None

    package_name: str | None = None
    version: str | None = None
    description: str | None = None
    requires_python: str | None = None

    dependencies: list[str] = field(default_factory=list)
    optional_dependencies: dict[str, list[str]] = field(
        default_factory=dict
    )
    scripts: dict[str, str] = field(default_factory=dict)

    build_backend: str | None = None


class PyprojectAnalyzer:
    def analyze(
        self,
        project: Project,
    ) -> PyprojectFacts:
        path = project.root / "pyproject.toml"

        if not path.is_file():
            return PyprojectFacts()

        try:
            data = tomllib.loads(
                path.read_text(encoding="utf-8")
            )
        except (
            OSError,
            UnicodeDecodeError,
            tomllib.TOMLDecodeError,
        ):
            return PyprojectFacts(
                exists=True,
                path="pyproject.toml",
            )

        project_data = data.get("project", {})
        build_system = data.get("build-system", {})

        dependencies = self._string_list(
            project_data.get("dependencies", [])
        )

        optional_dependencies: dict[str, list[str]] = {}

        raw_optional = project_data.get(
            "optional-dependencies",
            {},
        )

        if isinstance(raw_optional, dict):
            for group, values in raw_optional.items():
                if not isinstance(group, str):
                    continue

                optional_dependencies[group] = (
                    self._string_list(values)
                )

        scripts: dict[str, str] = {}
        raw_scripts = project_data.get("scripts", {})

        if isinstance(raw_scripts, dict):
            scripts = {
                str(name): str(target)
                for name, target in raw_scripts.items()
            }

        return PyprojectFacts(
            exists=True,
            path="pyproject.toml",
            package_name=self._optional_string(
                project_data.get("name")
            ),
            version=self._optional_string(
                project_data.get("version")
            ),
            description=self._optional_string(
                project_data.get("description")
            ),
            requires_python=self._optional_string(
                project_data.get("requires-python")
            ),
            dependencies=sorted(
                dependencies,
                key=str.casefold,
            ),
            optional_dependencies={
                group: sorted(values, key=str.casefold)
                for group, values
                in sorted(optional_dependencies.items())
            },
            scripts=dict(
                sorted(scripts.items())
            ),
            build_backend=self._optional_string(
                build_system.get("build-backend")
            ),
        )

    @staticmethod
    def _string_list(
        value: object,
    ) -> list[str]:
        if not isinstance(value, list):
            return []

        return [
            item
            for item in value
            if isinstance(item, str)
        ]

    @staticmethod
    def _optional_string(
        value: object,
    ) -> str | None:
        if isinstance(value, str) and value.strip():
            return value.strip()

        return None
