from __future__ import annotations

from docforge.models import Project
from docforge.profiles.base import (
    ProfileDocumentPolicy,
    ProjectProfile,
)


class HugoStaticProfile(ProjectProfile):
    """Profil des sites statiques dont Hugo construit les pages Markdown."""

    name = "hugo-static"
    label = "Site statique Hugo"
    description = (
        "Site web statique dont les pages Markdown sont construites par Hugo."
    )
    priority = 80

    def confidence(
        self,
        project: Project,
    ) -> int:
        score = 0

        if "Hugo" in project.frameworks:
            score += 70

        for directory, weight in (
            ("content", 10),
            ("layouts", 10),
            ("static", 5),
            ("themes", 5),
        ):
            if directory in project.directories:
                score += weight

        return score

    def evidence(
        self,
        project: Project,
    ) -> list[str]:
        evidence: list[str] = []

        if "Hugo" in project.frameworks:
            hugo_evidence = sorted(
                {
                    item
                    for technology in project.technologies
                    if technology.name == "Hugo"
                    for item in technology.evidence
                }
            )
            evidence.extend(
                f"configuration Hugo détectée : {path}"
                for path in hugo_evidence
            )

        for directory in ("content", "layouts", "static", "themes"):
            if directory in project.directories:
                evidence.append(
                    f"structure Hugo détectée : {directory}/"
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
                "docs/architecture.md",
                "docs/specification.md",
            ),
            optional_documents=(
                "docs/deployment.md",
                "docs/troubleshooting.md",
            ),
            deterministic_documents=(
                "README.md",
                "README_DEV.md",
                "CODEX_START.md",
                "AGENTS.md",
                "docs/architecture.md",
                "docs/specification.md",
            ),
            protected_documents=(),
        )
