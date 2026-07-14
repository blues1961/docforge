from __future__ import annotations

from project_assistant.models import Project
from project_assistant.profiles.base import (
    ProfileDocumentPolicy,
    ProjectProfile,
)


class GenericProfile(ProjectProfile):
    name = "generic"
    label = "Projet générique"
    description = (
        "Profil de secours utilisé lorsqu’aucune famille "
        "de projet spécialisée n’est détectée."
    )
    priority = -100

    def confidence(
        self,
        project: Project,
    ) -> int:
        return 1

    def evidence(
        self,
        project: Project,
    ) -> list[str]:
        return [
            "aucun profil spécialisé suffisamment fiable"
        ]

    def document_policy(
        self,
    ) -> ProfileDocumentPolicy:
        return ProfileDocumentPolicy(
            required_documents=(
                "README.md",
            ),
            optional_documents=(
                "README_DEV.md",
                "AGENTS.md",
                "CODEX_START.md",
                "INVARIANTS.md",
                "docs/architecture.md",
                "docs/specification.md",
            ),
            deterministic_documents=(
                "README.md",
                "docs/architecture.md",
                "docs/specification.md",
            ),
        )
