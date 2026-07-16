from __future__ import annotations

import json
from typing import Any

from docforge.manual_blueprint import (
    ManualBlueprint,
    ManualSectionDefinition,
)
from docforge.manual_knowledge import ManualKnowledge


class ManualPromptBuilder:
    GLOBAL_RULES = (
        "Rédige un guide utilisateur en Markdown.",
        "Utilise ManualKnowledge comme source unique de vérité.",
        "Suis strictement le blueprint fourni.",
        "N’invente jamais une commande, une option, une procédure ou une fonctionnalité.",
        "Utilise toujours `command_path` pour référencer les commandes.",
        "Signale explicitement les informations manquantes.",
        "Ne produis jamais de chemin local propre à une machine.",
        "N’ajoute jamais de référence de citation interne comme `oaicite`.",
        "Retourne uniquement le Markdown du manuel.",
    )

    def rules(
        self,
        blueprint: ManualBlueprint,
    ) -> tuple[str, ...]:
        return self.GLOBAL_RULES

    def build_full_prompt(
        self,
        *,
        knowledge: ManualKnowledge,
        blueprint: ManualBlueprint,
    ) -> str:
        payload = knowledge.to_dict()
        blueprint_payload = {
            "profile_name": blueprint.profile_name,
            "sections": [
                {
                    "identifier": section.identifier,
                    "title": section.title,
                    "purpose": section.purpose,
                    "required_fact_paths": list(
                        section.required_fact_paths
                    ),
                    "optional": section.optional,
                    "omit_condition": section.omit_condition,
                    "omit_if_fact_paths_missing": list(
                        section.omit_if_fact_paths_missing
                    ),
                }
                for section in blueprint.sections
            ],
        }

        lines = [
            "BEGIN INSTRUCTIONS",
            *self.rules(blueprint or ManualBlueprint(profile_name="generic")),
            "Structure attendue :",
            json.dumps(
                blueprint_payload,
                indent=2,
                ensure_ascii=False,
            ),
            "END INSTRUCTIONS",
            "",
            "BEGIN MANUAL KNOWLEDGE",
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            "END MANUAL KNOWLEDGE",
            "",
        ]
        return "\n".join(lines)

    def build_section_prompt(
        self,
        *,
        blueprint: ManualBlueprint | None = None,
        section: ManualSectionDefinition,
        projected_facts: dict[str, Any],
    ) -> str:
        lines = [
            "BEGIN INSTRUCTIONS",
            *self.rules(blueprint or ManualBlueprint(profile_name="generic")),
            f"Titre de section : {section.title}",
            f"But : {section.purpose}",
            "Produis uniquement la section demandée, sans titre de document global, sans conclusion générale et sans contenu hors sujet.",
            "END INSTRUCTIONS",
            "",
            "BEGIN SECTION FACTS",
            json.dumps(
                {
                    "identifier": section.identifier,
                    "title": section.title,
                    "purpose": section.purpose,
                    "facts": projected_facts,
                },
                indent=2,
                ensure_ascii=False,
            ),
            "END SECTION FACTS",
            "",
        ]
        return "\n".join(lines)

    @staticmethod
    def project_section_facts(
        knowledge: ManualKnowledge,
        section: ManualSectionDefinition,
    ) -> dict[str, Any]:
        payload = knowledge.to_dict()
        projection: dict[str, Any] = {}

        for path in section.required_fact_paths:
            value = ManualPromptBuilder._extract_path(
                payload,
                path,
            )
            ManualPromptBuilder._assign_path(
                projection,
                path,
                value,
            )

        return projection

    @staticmethod
    def should_omit_section(
        knowledge: ManualKnowledge,
        section: ManualSectionDefinition,
    ) -> bool:
        if not section.omit_if_fact_paths_missing:
            return False

        payload = knowledge.to_dict()
        for path in section.omit_if_fact_paths_missing:
            value = ManualPromptBuilder._extract_path(
                payload,
                path,
            )
            if ManualPromptBuilder._has_content(value):
                return False

        return True

    @staticmethod
    def _has_content(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (list, tuple, set, dict)):
            return bool(value)
        if isinstance(value, str):
            return bool(value.strip())
        return True

    @staticmethod
    def _extract_path(
        payload: dict[str, Any],
        path: str,
    ) -> Any:
        current: Any = payload

        for part in path.split("."):
            if isinstance(current, list):
                if not current:
                    return []
                return current
            if not isinstance(current, dict):
                return None
            current = current.get(part)

        return current

    @staticmethod
    def _assign_path(
        projection: dict[str, Any],
        path: str,
        value: Any,
    ) -> None:
        parts = path.split(".")
        current = projection

        for part in parts[:-1]:
            next_value = current.get(part)

            if not isinstance(next_value, dict):
                next_value = {}
                current[part] = next_value

            current = next_value

        current[parts[-1]] = value


class DjangoReactManualPromptBuilder(ManualPromptBuilder):
    DJANGO_REACT_RULES = (
        "Le manuel concerne l’application analysée, jamais DocForge comme produit utilisateur.",
        "Les commandes DocForge ne sont pas des commandes d’utilisation de l’application analysée.",
        "Formule prudemment toute capacité marquée `derived`.",
        "Sépare strictement les environnements de développement et de production.",
        "N’affiche jamais une valeur secrète.",
        "Omet toute procédure dont une commande critique est absente.",
        "Signale explicitement les faits manquants lorsque le dépôt ne permet pas de conclure.",
    )

    def rules(
        self,
        blueprint: ManualBlueprint,
    ) -> tuple[str, ...]:
        return (*self.GLOBAL_RULES, *self.DJANGO_REACT_RULES)
