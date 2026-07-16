from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from docforge.models import Project

if TYPE_CHECKING:
    from docforge.analyzer_registry import AnalyzerRegistry
    from docforge.document_generator_registry import (
        DocumentGeneratorRegistry,
    )
    from docforge.knowledge import ProjectKnowledge
    from docforge.manual_blueprint import ManualBlueprint
    from docforge.manual_knowledge import ManualKnowledgeBuilder
    from docforge.manual_prompt import ManualPromptBuilder


@dataclass(frozen=True, slots=True)
class ProfileDocumentPolicy:
    required_documents: tuple[str, ...] = ()
    optional_documents: tuple[str, ...] = ()
    deterministic_documents: tuple[str, ...] = ()
    protected_documents: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ProfileFacts:
    name: str
    label: str
    description: str
    confidence: int
    evidence: tuple[str, ...] = ()
    document_policy: ProfileDocumentPolicy = field(
        default_factory=ProfileDocumentPolicy
    )


class ProjectProfile(ABC):
    name: str
    label: str
    description: str
    priority: int = 0

    @abstractmethod
    def confidence(
        self,
        project: Project,
    ) -> int:
        """Retourner un score de détection entre 0 et 100."""

    @abstractmethod
    def evidence(
        self,
        project: Project,
    ) -> list[str]:
        """Retourner les preuves justifiant le profil."""

    @abstractmethod
    def document_policy(
        self,
    ) -> ProfileDocumentPolicy:
        """Retourner la politique documentaire du profil."""

    def build_analyzer_registry(
        self,
    ) -> "AnalyzerRegistry":
        from docforge.default_analyzers import (
            build_default_analyzer_registry,
        )

        return build_default_analyzer_registry()

    def build_document_generator_registry(
        self,
        knowledge: "ProjectKnowledge",
    ) -> "DocumentGeneratorRegistry":
        from docforge.default_document_generators import (
            build_default_document_generator_registry,
        )

        return build_default_document_generator_registry(
            knowledge
        )

    def build_manual_knowledge_builder(
        self,
    ) -> "ManualKnowledgeBuilder":
        from docforge.manual_knowledge import (
            ManualKnowledgeBuilder,
        )

        return ManualKnowledgeBuilder()

    def build_manual_blueprint(
        self,
    ) -> "ManualBlueprint":
        from docforge.manual_blueprint import (
            ManualBlueprintRegistry,
        )

        return ManualBlueprintRegistry().blueprint_for_profile(
            self.name
        )

    def build_manual_prompt_builder(
        self,
    ) -> "ManualPromptBuilder":
        from docforge.manual_prompt import (
            ManualPromptBuilder,
        )

        return ManualPromptBuilder()

    def analyze(
        self,
        project: Project,
    ) -> ProfileFacts:
        confidence = max(
            0,
            min(100, self.confidence(project)),
        )

        return ProfileFacts(
            name=self.name,
            label=self.label,
            description=self.description,
            confidence=confidence,
            evidence=tuple(self.evidence(project)),
            document_policy=self.document_policy(),
        )
