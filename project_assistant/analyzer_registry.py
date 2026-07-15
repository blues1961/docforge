from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from project_assistant.models import Project


AnalyzerCallable = Callable[[Project], Any]


class UnknownAnalyzerError(KeyError):
    """Aucun analyseur n’est enregistré sous ce nom."""


class DuplicateAnalyzerError(ValueError):
    """Un analyseur est déjà enregistré sous ce nom."""


@dataclass(frozen=True, slots=True)
class RegisteredAnalyzer:
    name: str
    analyze: AnalyzerCallable
    profiles: frozenset[str] = frozenset()

    def supports_profile(
        self,
        profile_name: str,
    ) -> bool:
        return (
            not self.profiles
            or profile_name in self.profiles
        )


class AnalyzerRegistry:
    def __init__(self) -> None:
        self._analyzers: dict[
            str,
            RegisteredAnalyzer,
        ] = {}

    def register(
        self,
        registration: RegisteredAnalyzer,
    ) -> None:
        if registration.name in self._analyzers:
            raise DuplicateAnalyzerError(
                "Analyseur déjà enregistré : "
                f"{registration.name}"
            )

        self._analyzers[registration.name] = registration

    def resolve(
        self,
        name: str,
    ) -> RegisteredAnalyzer:
        try:
            return self._analyzers[name]
        except KeyError as exc:
            raise UnknownAnalyzerError(
                f"Analyseur inconnu : {name}"
            ) from exc

    def registrations(
        self,
        *,
        profile_name: str | None = None,
    ) -> tuple[RegisteredAnalyzer, ...]:
        analyzers = self._analyzers.values()

        if profile_name is not None:
            analyzers = (
                registration
                for registration in analyzers
                if registration.supports_profile(
                    profile_name
                )
            )

        return tuple(
            sorted(
                analyzers,
                key=lambda item: item.name,
            )
        )

    def names(
        self,
        *,
        profile_name: str | None = None,
    ) -> frozenset[str]:
        return frozenset(
            registration.name
            for registration in self.registrations(
                profile_name=profile_name
            )
        )

    def analyze(
        self,
        name: str,
        project: Project,
    ) -> Any:
        registration = self.resolve(name)
        return registration.analyze(project)
