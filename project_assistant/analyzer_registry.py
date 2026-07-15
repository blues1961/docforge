from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar, cast

from project_assistant.models import Project


T = TypeVar("T")


class UnknownAnalyzerError(KeyError):
    """Aucun analyseur n’est enregistré sous ce nom."""


class DuplicateAnalyzerError(ValueError):
    """Un analyseur est déjà enregistré sous ce nom."""


class MissingAnalyzerDependencyError(RuntimeError):
    """Une dépendance d’analyse n’est pas disponible."""


class CircularAnalyzerDependencyError(RuntimeError):
    """Les dépendances d’analyse contiennent un cycle."""


@dataclass(slots=True)
class AnalysisContext:
    project: Project
    profile_name: str
    protected_documents: tuple[str, ...] = ()
    results: dict[str, Any] = field(default_factory=dict)

    def store(
        self,
        name: str,
        value: Any,
    ) -> None:
        self.results[name] = value

    def require(
        self,
        name: str,
    ) -> Any:
        if name not in self.results:
            raise MissingAnalyzerDependencyError(
                f"Résultat d’analyse absent : {name}"
            )

        return self.results[name]

    def require_as(
        self,
        name: str,
        expected_type: type[T],
    ) -> T:
        value = self.require(name)

        if not isinstance(value, expected_type):
            raise TypeError(
                f"Résultat {name!r} incompatible : "
                f"{type(value).__name__}; "
                f"attendu : {expected_type.__name__}"
            )

        return cast(T, value)


AnalyzerCallable = Callable[[AnalysisContext], Any]


@dataclass(frozen=True, slots=True)
class RegisteredAnalyzer:
    name: str
    analyze: AnalyzerCallable
    profiles: frozenset[str] = frozenset()
    dependencies: tuple[str, ...] = ()

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
        context: AnalysisContext,
    ) -> Any:
        self._analyze_registration(
            self.resolve(name),
            context,
            visiting=set(),
        )
        return context.require(name)

    def analyze_all(
        self,
        context: AnalysisContext,
    ) -> dict[str, Any]:
        for registration in self.registrations(
            profile_name=context.profile_name
        ):
            self._analyze_registration(
                registration,
                context,
                visiting=set(),
            )

        return dict(context.results)

    def _analyze_registration(
        self,
        registration: RegisteredAnalyzer,
        context: AnalysisContext,
        *,
        visiting: set[str],
    ) -> None:
        if registration.name in context.results:
            return

        if not registration.supports_profile(
            context.profile_name
        ):
            raise MissingAnalyzerDependencyError(
                "Analyseur non disponible pour le profil "
                f"{context.profile_name!r} : "
                f"{registration.name}"
            )

        if registration.name in visiting:
            cycle = " -> ".join(
                [*sorted(visiting), registration.name]
            )
            raise CircularAnalyzerDependencyError(
                f"Cycle de dépendances : {cycle}"
            )

        visiting.add(registration.name)

        for dependency_name in registration.dependencies:
            try:
                dependency = self.resolve(
                    dependency_name
                )
            except UnknownAnalyzerError as exc:
                raise MissingAnalyzerDependencyError(
                    "Dépendance non enregistrée : "
                    f"{registration.name} -> "
                    f"{dependency_name}"
                ) from exc

            self._analyze_registration(
                dependency,
                context,
                visiting=visiting,
            )

        context.store(
            registration.name,
            registration.analyze(context),
        )

        visiting.remove(registration.name)
