from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from project_assistant.models import Project


GeneratorCallable = Callable[[Project], str]


class UnknownDocumentGeneratorError(ValueError):
    """Aucun générateur ne correspond au profil et au document."""


class DuplicateDocumentGeneratorError(ValueError):
    """Un générateur existe déjà pour cette combinaison."""


@dataclass(frozen=True, slots=True)
class RegisteredDocumentGenerator:
    profile_name: str
    document_path: str
    generator_name: str
    generate: GeneratorCallable


class DocumentGeneratorRegistry:
    def __init__(self) -> None:
        self._generators: dict[
            tuple[str, str],
            RegisteredDocumentGenerator,
        ] = {}

    def register(
        self,
        registration: RegisteredDocumentGenerator,
    ) -> None:
        key = (
            registration.profile_name,
            registration.document_path,
        )

        if key in self._generators:
            raise DuplicateDocumentGeneratorError(
                "Générateur déjà enregistré : "
                f"{registration.profile_name} / "
                f"{registration.document_path}"
            )

        self._generators[key] = registration

    def resolve(
        self,
        *,
        profile_name: str,
        document_path: str,
    ) -> RegisteredDocumentGenerator:
        exact_key = (
            profile_name,
            document_path,
        )

        exact = self._generators.get(exact_key)

        if exact is not None:
            return exact

        generic_key = (
            "generic",
            document_path,
        )

        generic = self._generators.get(generic_key)

        if generic is not None:
            return generic

        raise UnknownDocumentGeneratorError(
            "Aucun générateur enregistré pour "
            f"{profile_name} / {document_path}"
        )

    def supported_documents(
        self,
        profile_name: str,
    ) -> frozenset[str]:
        return frozenset(
            document_path
            for (
                registered_profile,
                document_path,
            ) in self._generators
            if registered_profile in {
                profile_name,
                "generic",
            }
        )

    def registrations(
        self,
    ) -> tuple[RegisteredDocumentGenerator, ...]:
        return tuple(
            sorted(
                self._generators.values(),
                key=lambda item: (
                    item.profile_name,
                    item.document_path,
                ),
            )
        )
