from __future__ import annotations

from docforge.knowledge import ProjectKnowledge
from docforge.models import Project


class PythonCliCliDocumentGenerator:
    def generate(
        self,
        project: Project,
        knowledge: ProjectKnowledge,
    ) -> str:
        facts = knowledge.cli

        lines = [
            f"# Référence CLI — {project.name}",
            "",
            "<!--",
            "Document généré en aperçu par docforge.",
            "Les commandes sont extraites du code Python avec ast.",
            "-->",
            "",
            "## Vue d’ensemble",
            "",
            f"- Framework détecté : `{facts.framework or 'aucun'}`.",
            f"- Nombre de commandes : `{facts.command_count}`.",
            (
                "- Fichiers contenant des commandes : "
                f"{self._code_list(facts.command_files)}."
            ),
            "",
            "## Points d’entrée",
            "",
        ]

        if facts.entry_points:
            for name, target in facts.entry_points.items():
                lines.append(f"- `{name}` → `{target}`")
        else:
            lines.append("- Aucun point d’entrée déclaré.")

        lines.extend(
            [
                "",
                "## Commandes",
                "",
            ]
        )

        if not facts.commands:
            lines.extend(
                [
                    "Aucune commande Typer détectée.",
                    "",
                ]
            )
        else:
            for command in facts.commands:
                full_name = command.command_path

                lines.extend(
                    [
                        f"### `{full_name}`",
                        "",
                        (
                            command.help
                            or "Aucune description détectée."
                        ),
                        "",
                        f"- Fonction : `{command.function_name}`.",
                        f"- Module : `{command.module}`.",
                        f"- Commande : `{command.command_path}`.",
                    ]
                )

                if command.group:
                    lines.append(
                        f"- Groupe Typer : `{command.group}`."
                    )

                lines.extend(
                    [
                        "",
                        "#### Paramètres",
                        "",
                    ]
                )

                if not command.parameters:
                    lines.extend(
                        [
                            "- Aucun paramètre détecté.",
                            "",
                        ]
                    )
                    continue

                lines.extend(
                    [
                        "| Nom | Type | Nature | Requis | Défaut | Options | Description |",
                        "|---|---|---|---|---|---|---|",
                    ]
                )

                for parameter in command.parameters:
                    lines.append(
                        "| "
                        + " | ".join(
                            [
                                self._escape(parameter.name),
                                self._escape(
                                    parameter.type_annotation
                                    or "non défini"
                                ),
                                self._escape(parameter.kind),
                                (
                                    "oui"
                                    if parameter.required
                                    else "non"
                                ),
                                self._escape(
                                    parameter.default or "—"
                                ),
                                self._escape(
                                    ", ".join(parameter.flags)
                                    or "—"
                                ),
                                self._escape(
                                    parameter.help or "—"
                                ),
                            ]
                        )
                        + " |"
                    )

                lines.append("")

        lines.extend(
            [
                "## Exemples généraux",
                "",
                "```bash",
                "docforge --help",
                "docforge profile /chemin/du/projet",
                "docforge knowledge /chemin/du/projet",
                (
                    "docforge document "
                    "/chemin/du/projet --refresh --clean"
                ),
                "docforge audit-all --show-findings",
                "```",
                "",
                "## Limites de l’analyse",
                "",
                (
                    "- les commandes créées dynamiquement à l’exécution "
                    "peuvent ne pas être détectées;"
                ),
                (
                    "- les descriptions calculées dynamiquement peuvent "
                    "ne pas être disponibles;"
                ),
                (
                    "- l’analyse ne doit jamais importer ni exécuter "
                    "le module CLI;"
                ),
                "",
            ]
        )

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _code_list(values: list[str]) -> str:
        if not values:
            return "`aucun`"

        return ", ".join(
            f"`{value}`"
            for value in values
        )

    @staticmethod
    def _escape(value: str) -> str:
        return value.replace("|", "\\|").replace(
            "\n",
            " ",
        )
