from __future__ import annotations

from docforge.models import Project
from docforge.profiles.base import (
    ProfileDocumentPolicy,
    ProjectProfile,
)


class DjangoReactProfile(ProjectProfile):
    name = "django-react"
    label = "Application Django/React"
    description = (
        "Application auto-hébergée avec backend Django, "
        "frontend React/Vite et orchestration Docker Compose."
    )
    priority = 100

    def confidence(
        self,
        project: Project,
    ) -> int:
        score = 0

        if "Django" in project.frameworks:
            score += 35

        if "React" in project.frameworks:
            score += 25

        if "Vite" in project.frameworks:
            score += 10

        if (
            project.root
            / "docker-compose.dev.yml"
        ).is_file():
            score += 10

        if (
            project.root
            / "docker-compose.prod.yml"
        ).is_file():
            score += 10

        if (project.root / "backend").is_dir():
            score += 5

        if (project.root / "frontend").is_dir():
            score += 5

        return score

    def evidence(
        self,
        project: Project,
    ) -> list[str]:
        evidence: list[str] = []

        for framework in (
            "Django",
            "React",
            "Vite",
        ):
            if framework in project.frameworks:
                evidence.append(
                    f"framework détecté : {framework}"
                )

        for path in (
            "docker-compose.dev.yml",
            "docker-compose.prod.yml",
            "backend",
            "frontend",
        ):
            if (project.root / path).exists():
                evidence.append(
                    f"structure détectée : {path}"
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
                "docs/api.md",
                "docs/deployment.md",
            ),
            deterministic_documents=(
                "README.md",
                "README_DEV.md",
                "CODEX_START.md",
                "AGENTS.md",
                "docs/architecture.md",
                "docs/specification.md",
                "docs/api.md",
                "docs/deployment.md",
            ),
            protected_documents=(),
        )

    def build_manual_knowledge_builder(self):
        from docforge.manual_django_react import (
            DjangoReactManualKnowledgeBuilder,
        )

        return DjangoReactManualKnowledgeBuilder()

    def build_manual_blueprint(self):
        from docforge.manual_blueprint import (
            ManualBlueprintRegistry,
        )

        return ManualBlueprintRegistry().blueprint_for_profile(
            self.name
        )

    def build_manual_prompt_builder(self):
        from docforge.manual_prompt import (
            DjangoReactManualPromptBuilder,
        )

        return DjangoReactManualPromptBuilder()
