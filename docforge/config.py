from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ConfigurationError(RuntimeError):
    """Erreur de chargement ou de validation de la configuration."""


@dataclass(slots=True)
class ResolvedDocumentationConfig:
    profile: str
    required_documents: list[str]
    optional_documents: list[str]
    excluded_documents: list[str]
    document_definitions: dict[str, dict[str, Any]]


class DocumentationConfigLoader:
    def __init__(self, config_path: Path | None = None) -> None:
        if config_path is None:
            config_path = (
                Path(__file__).resolve().parent.parent
                / "defaults"
                / "documentation.yml"
            )

        self.config_path = config_path

    def load(self) -> dict[str, Any]:
        if not self.config_path.exists():
            raise ConfigurationError(
                f"Configuration introuvable : {self.config_path}"
            )

        try:
            with self.config_path.open(encoding="utf-8") as file:
                data = yaml.safe_load(file)
        except (OSError, yaml.YAMLError) as error:
            raise ConfigurationError(
                f"Impossible de lire {self.config_path}: {error}"
            ) from error

        if not isinstance(data, dict):
            raise ConfigurationError(
                "La racine de documentation.yml doit être un objet YAML."
            )

        required_keys = {
            "schema_version",
            "documents",
            "profiles",
        }

        missing_keys = required_keys - data.keys()

        if missing_keys:
            missing = ", ".join(sorted(missing_keys))
            raise ConfigurationError(
                f"Clés obligatoires absentes : {missing}"
            )

        if not isinstance(data["documents"], dict):
            raise ConfigurationError(
                "'documents' doit être un dictionnaire."
            )

        if not isinstance(data["profiles"], dict):
            raise ConfigurationError(
                "'profiles' doit être un dictionnaire."
            )

        return data

    def resolve_profile(
        self,
        profile_name: str,
    ) -> ResolvedDocumentationConfig:
        data = self.load()
        profiles = data["profiles"]

        if profile_name not in profiles:
            available = ", ".join(sorted(profiles))
            raise ConfigurationError(
                f"Profil inconnu '{profile_name}'. "
                f"Profils disponibles : {available}"
            )

        required: list[str] = []
        optional: list[str] = []
        excluded: list[str] = []

        self._collect_profile_documents(
            profile_name=profile_name,
            profiles=profiles,
            required=required,
            optional=optional,
            excluded=excluded,
            visited=set(),
        )

        required = self._deduplicate(required)
        optional = self._deduplicate(optional)
        excluded = self._deduplicate(excluded)

        required = [
            path
            for path in required
            if path not in excluded
        ]

        optional = [
            path
            for path in optional
            if path not in excluded
            and path not in required
        ]

        document_definitions = data["documents"]

        unknown_documents = [
            path
            for path in required + optional
            if path not in document_definitions
        ]

        if unknown_documents:
            unknown = ", ".join(sorted(unknown_documents))
            raise ConfigurationError(
                "Documents référencés mais non définis : "
                f"{unknown}"
            )

        return ResolvedDocumentationConfig(
            profile=profile_name,
            required_documents=required,
            optional_documents=optional,
            excluded_documents=excluded,
            document_definitions=document_definitions,
        )

    def resolve_project_profile(
        self,
        profile_name: str,
        add_documents: list[str] | None = None,
        remove_documents: list[str] | None = None,
    ) -> ResolvedDocumentationConfig:
        resolved = self.resolve_profile(profile_name)

        required = list(resolved.required_documents)
        optional = list(resolved.optional_documents)
        excluded = list(resolved.excluded_documents)

        for document in add_documents or []:
            if document not in resolved.document_definitions:
                raise ConfigurationError(
                    f"Document ajouté mais non défini : {document}"
                )

            if document not in required:
                required.append(document)

            if document in optional:
                optional.remove(document)

            if document in excluded:
                excluded.remove(document)

        for document in remove_documents or []:
            if document in required:
                required.remove(document)

            if document in optional:
                optional.remove(document)

            if document not in excluded:
                excluded.append(document)

        return ResolvedDocumentationConfig(
            profile=profile_name,
            required_documents=required,
            optional_documents=optional,
            excluded_documents=excluded,
            document_definitions=resolved.document_definitions,
        )

    def _collect_profile_documents(
        self,
        profile_name: str,
        profiles: dict[str, Any],
        required: list[str],
        optional: list[str],
        excluded: list[str],
        visited: set[str],
    ) -> None:
        if profile_name in visited:
            raise ConfigurationError(
                f"Héritage circulaire détecté pour '{profile_name}'."
            )

        visited.add(profile_name)

        profile = profiles.get(profile_name)

        if not isinstance(profile, dict):
            raise ConfigurationError(
                f"Le profil '{profile_name}' doit être un objet."
            )

        parent = profile.get("extends")

        if parent:
            if parent not in profiles:
                raise ConfigurationError(
                    f"Le profil parent '{parent}' est introuvable."
                )

            self._collect_profile_documents(
                profile_name=parent,
                profiles=profiles,
                required=required,
                optional=optional,
                excluded=excluded,
                visited=visited,
            )

        required.extend(
            profile.get("required_documents", [])
        )
        required.extend(
            profile.get("additional_documents", [])
        )
        optional.extend(
            profile.get("optional_documents", [])
        )
        excluded.extend(
            profile.get("excluded_documents", [])
        )

        visited.remove(profile_name)

    @staticmethod
    def _deduplicate(values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))
