from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from project_assistant.models import Project


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
