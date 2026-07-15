from __future__ import annotations

from docforge.analyzers import (
    PythonCliSpecificationFacts,
)
from docforge.models import Project


class PythonCliSpecificationDocumentGenerator:
    def generate(
        self,
        project: Project,
        facts: PythonCliSpecificationFacts,
    ) -> str:
        lines = [
            f"# Spécification — {project.name}",
            "",
            "<!--",
            "Document généré en aperçu par docforge.",
            "Ce document définit les exigences du produit.",
            "-->",
            "",
            "## Objectif",
            "",
            facts.purpose,
            "",
            "## Identité du produit",
            "",
            f"- Projet : `{facts.project_name}`.",
            f"- Paquet : {self._value(facts.package_name)}.",
            f"- Version : {self._value(facts.version)}.",
            f"- Python requis : {self._value(facts.requires_python)}.",
            "",
            "## Périmètre",
            "",
        ]

        self._append_bullets(lines, facts.scope)

        lines.extend(
            [
                "## Hors périmètre",
                "",
            ]
        )
        self._append_bullets(lines, facts.out_of_scope)

        lines.extend(
            [
                "## Concepts principaux",
                "",
                "### Projet",
                "",
                (
                    "Dépôt local analysé par docforge. "
                    "Le projet reste la source des faits techniques."
                ),
                "",
                "### Profil",
                "",
                (
                    "Famille de projet déterminée à partir d’un score "
                    "de confiance et de preuves explicites."
                ),
                "",
                "### ProjectKnowledge",
                "",
                (
                    "Modèle structuré et sérialisable regroupant les "
                    "faits réutilisés par les générateurs."
                ),
                "",
                "### Politique documentaire",
                "",
                (
                    "Liste des documents obligatoires, optionnels, "
                    "déterministes et protégés pour un profil."
                ),
                "",
                "### Aperçu",
                "",
                (
                    "Document généré sous `.docforge/preview` "
                    "sans modification du fichier cible."
                ),
                "",
                "### Application",
                "",
                (
                    "Copie explicite d’un aperçu validé vers le dépôt "
                    "à l’aide de la commande `apply`."
                ),
                "",
                "## Profils pris en charge",
                "",
            ]
        )
        self._append_code_bullets(lines, facts.supported_profiles)

        lines.extend(
            [
                "## Politique documentaire du profil",
                "",
                "### Documents obligatoires",
                "",
            ]
        )
        self._append_code_bullets(
            lines,
            facts.required_documents,
        )

        lines.extend(
            [
                "### Documents déterministes",
                "",
            ]
        )
        self._append_code_bullets(
            lines,
            facts.deterministic_documents,
        )

        lines.extend(
            [
                "### Documents protégés",
                "",
            ]
        )
        self._append_code_bullets(
            lines,
            facts.protected_documents,
        )

        lines.extend(
            [
                "## Interface CLI",
                "",
            ]
        )

        if facts.cli_commands:
            for name, target in facts.cli_commands.items():
                lines.append(f"- `{name}` → `{target}`")
            lines.append("")
        else:
            lines.extend(
                [
                    "- Aucun point d’entrée CLI déclaré.",
                    "",
                ]
            )

        lines.extend(
            [
                "## Exigences fonctionnelles",
                "",
            ]
        )
        self._append_numbered(
            lines,
            facts.functional_requirements,
            prefix="EF",
        )

        lines.extend(
            [
                "## Exigences non fonctionnelles",
                "",
            ]
        )
        self._append_numbered(
            lines,
            facts.non_functional_requirements,
            prefix="ENF",
        )

        lines.extend(
            [
                "## Exigences de sécurité",
                "",
            ]
        )
        self._append_numbered(
            lines,
            facts.security_requirements,
            prefix="SEC",
        )

        lines.extend(
            [
                "## Règles métier",
                "",
                "1. Les faits détectés prévalent sur les descriptions "
                "inventées.",
                "2. Un profil spécialisé valide prévaut sur le profil "
                "`generic`.",
                "3. Un générateur déterministe prévaut sur un générateur "
                "LLM.",
                "4. La génération d’un aperçu ne constitue pas une "
                "approbation.",
                "5. Un document protégé exige une confirmation explicite "
                "du propriétaire.",
                "6. Une application doit s’adapter aux invariants; les "
                "invariants ne sont pas adaptés automatiquement.",
                "",
                "## Critères d’acceptation",
                "",
            ]
        )
        self._append_checklist(
            lines,
            facts.acceptance_criteria,
        )

        lines.extend(
            [
                "## Limites connues",
                "",
            ]
        )
        self._append_bullets(
            lines,
            facts.known_limitations,
        )

        lines.extend(
            [
                "## Évolutions prévues",
                "",
                "- ajouter le profil `hugo-static`;",
                "- ajouter le profil `3d-design`;",
                "- générer `docs/cli.md`;",
                "- générer `docs/configuration.md`;",
                "- générer `docs/security.md`;",
                "- alléger progressivement `cli.py`;",
                "- versionner formellement les migrations du cache;",
                "- ajouter des contrôles de fraîcheur documentaire.",
                "",
                "## Validation de la spécification",
                "",
                "La spécification est considérée respectée lorsque :",
                "",
                "```bash",
                "python -m py_compile docforge/cli.py",
                "pytest -q",
                "docforge --help",
                "docforge profile .",
                "docforge knowledge .",
                "docforge document . --refresh --clean",
                "```",
                "",
                (
                    "réussissent sans compromettre les protections, "
                    "les secrets ou le comportement des profils existants."
                ),
                "",
            ]
        )

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _append_bullets(
        lines: list[str],
        values: list[str],
    ) -> None:
        if not values:
            lines.extend(["- Aucun élément.", ""])
            return

        for value in values:
            lines.append(f"- {value}")

        lines.append("")

    @staticmethod
    def _append_code_bullets(
        lines: list[str],
        values: list[str],
    ) -> None:
        if not values:
            lines.extend(["- `aucun`", ""])
            return

        for value in values:
            lines.append(f"- `{value}`")

        lines.append("")

    @staticmethod
    def _append_numbered(
        lines: list[str],
        values: list[str],
        *,
        prefix: str,
    ) -> None:
        for index, value in enumerate(values, start=1):
            lines.append(
                f"- **{prefix}-{index:03d}** — {value}"
            )

        lines.append("")

    @staticmethod
    def _append_checklist(
        lines: list[str],
        values: list[str],
    ) -> None:
        for value in values:
            lines.append(f"- [ ] {value}")

        lines.append("")

    @staticmethod
    def _value(value: str | None) -> str:
        if not value:
            return "`non défini`"

        return f"`{value}`"
