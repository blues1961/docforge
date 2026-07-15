from __future__ import annotations

from dataclasses import dataclass

from project_assistant.models import Project
from project_assistant.profiles.base import (
    ProfileFacts,
    ProjectProfile,
)
from project_assistant.profiles.django_react import (
    DjangoReactProfile,
)
from project_assistant.profiles.generic import (
    GenericProfile,
)
from project_assistant.profiles.python_cli import (
    PythonCliProfile,
)


@dataclass(frozen=True, slots=True)
class ProfileCandidate:
    profile: ProjectProfile
    facts: ProfileFacts


class ProfileDetector:
    MIN_SPECIALIZED_CONFIDENCE = 50

    def __init__(
        self,
        profiles: list[ProjectProfile] | None = None,
    ) -> None:
        self.profiles = profiles or [
            DjangoReactProfile(),
            PythonCliProfile(),
            GenericProfile(),
        ]

    def profile_named(
        self,
        name: str,
    ) -> ProjectProfile:
        for profile in self.profiles:
            if profile.name == name:
                return profile

        raise ValueError(
            f"Profil inconnu : {name}"
        )

    def resolve(
        self,
        project: Project,
    ) -> ProjectProfile:
        candidates = [
            ProfileCandidate(
                profile=profile,
                facts=profile.analyze(project),
            )
            for profile in self.profiles
        ]

        specialized = [
            candidate
            for candidate in candidates
            if candidate.profile.name != "generic"
            and candidate.facts.confidence
            >= self.MIN_SPECIALIZED_CONFIDENCE
        ]

        if specialized:
            winner = max(
                specialized,
                key=lambda candidate: (
                    candidate.facts.confidence,
                    candidate.profile.priority,
                ),
            )
            return winner.profile

        generic = next(
            candidate
            for candidate in candidates
            if candidate.profile.name == "generic"
        )

        return generic.profile

    def detect(
        self,
        project: Project,
    ) -> ProfileFacts:
        return self.resolve(project).analyze(project)
