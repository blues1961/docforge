from __future__ import annotations

import tomllib

from docforge.models import Project
from docforge.profiles.base import (
    ProfileDocumentPolicy,
    ProjectProfile,
)


class PythonCliProfile(ProjectProfile):
    name = "python-cli"
    label = "Outil Python CLI"
    description = (
        "Application Python en ligne de commande, installable "
        "depuis pyproject.toml et testée avec pytest."
    )
    priority = 90

    def confidence(
        self,
        project: Project,
    ) -> int:
        score = 0
        pyproject = project.root / "pyproject.toml"

        if pyproject.is_file():
            score += 30

        if self._has_console_script(project):
            score += 35

        if "Python" in project.languages:
            score += 15

        if (project.root / "tests").is_dir():
            score += 10

        if (project.root / "pytest.ini").is_file():
            score += 5

        if (project.root / "docforge").is_dir():
            score += 5

        if "Django" in project.frameworks:
            score -= 30

        if "React" in project.frameworks:
            score -= 20

        return max(score, 0)

    def evidence(
        self,
        project: Project,
    ) -> list[str]:
        evidence: list[str] = []

        if (project.root / "pyproject.toml").is_file():
            evidence.append(
                "configuration détectée : pyproject.toml"
            )

        if self._has_console_script(project):
            evidence.append(
                "point d’entrée CLI détecté dans pyproject.toml"
            )

        if "Python" in project.languages:
            evidence.append(
                "langage détecté : Python"
            )

        if (project.root / "tests").is_dir():
            evidence.append(
                "suite de tests détectée : tests/"
            )

        return evidence

    def document_policy(
        self,
    ) -> ProfileDocumentPolicy:
        return ProfileDocumentPolicy(
            required_documents=(
                "README.md",
                "README_DEV.md",
                "CODEX_START.md",
                "AGENTS.md",
                "INVARIANTS.md",
                "docs/architecture.md",
                "docs/cli.md",
                "docs/specification.md",
                "docs/configuration.md",
                "docs/security.md",
            ),
            optional_documents=(
                "docs/roadmap.md",
                "docs/workflows.md",
            ),
            deterministic_documents=(
                "README.md",
                "README_DEV.md",
                "CODEX_START.md",
                "AGENTS.md",
                "INVARIANTS.md",
                "docs/architecture.md",
                "docs/cli.md",
                "docs/configuration.md",
                "docs/specification.md",
                "docs/security.md",
            ),
            protected_documents=(
                "INVARIANTS.md",
            ),
        )

    @staticmethod
    def _has_console_script(
        project: Project,
    ) -> bool:
        path = project.root / "pyproject.toml"

        if not path.is_file():
            return False

        try:
            data = tomllib.loads(
                path.read_text(encoding="utf-8")
            )
        except (
            OSError,
            UnicodeDecodeError,
            tomllib.TOMLDecodeError,
        ):
            return False

        project_table = data.get("project", {})
        scripts = project_table.get("scripts", {})

        if isinstance(scripts, dict) and scripts:
            return True

        setuptools = data.get("tool", {}).get(
            "setuptools",
            {},
        )
        entry_points = setuptools.get(
            "entry-points",
            {},
        )

        return bool(entry_points)

    def build_manual_prompt_builder(self):
        from docforge.manual_prompt import (
            PythonCliManualPromptBuilder,
        )

        return PythonCliManualPromptBuilder()
