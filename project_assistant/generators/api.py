from __future__ import annotations

from collections import defaultdict

from project_assistant.analyzers import ApiFacts, ApiRoute
from project_assistant.models import Project


class ApiDocumentGenerator:
    def generate(
        self,
        project: Project,
        facts: ApiFacts,
    ) -> str:
        lines = [
            f"# API — {project.name}",
            "",
            "<!--",
            "Document généré en aperçu par project-assistant.",
            "Les méthodes et routes doivent être validées avant intégration.",
            "-->",
            "",
            "## Vue d'ensemble de l'API",
            "",
            (
                f"L’analyse a détecté `{len(facts.routes)}` route(s) "
                f"dans `{len(facts.route_files)}` fichier(s) Django `urls.py`."
            ),
            "",
            f"- Fichiers de routes : {self._code_list(facts.route_files)}.",
            f"- Modules inclus : {self._code_list(facts.included_modules)}.",
            "",
            "## Authentification",
            "",
            (
                "Les mécanismes d’authentification ne sont pas encore "
                "déduits automatiquement par cette version de l’analyseur."
            ),
            "",
            "À vérifier.",
            "",
            "## Points de terminaison",
            "",
        ]

        grouped_routes = self._group_routes(facts.routes)

        if not grouped_routes:
            lines.extend(
                [
                    "Aucun point de terminaison exploitable n’a été détecté.",
                    "",
                ]
            )

        for group_name, routes in grouped_routes.items():
            lines.extend(
                [
                    f"### {group_name}",
                    "",
                    "| Méthode | Chemin | Vue | Nom | Source |",
                    "|---|---|---|---|---|",
                ]
            )

            for route in routes:
                methods = route.methods or ["À vérifier"]

                for method in methods:
                    lines.append(
                        "| "
                        + " | ".join(
                            [
                                f"`{method}`",
                                f"`{route.path}`",
                                f"`{route.view or 'À vérifier'}`",
                                f"`{route.name or '—'}`",
                                f"`{route.source}`",
                            ]
                        )
                        + " |"
                    )

            lines.append("")

        lines.extend(
            [
                "## Schémas de données",
                "",
                (
                    "Les serializers et leurs champs ne sont pas encore "
                    "analysés par cette version."
                ),
                "",
                "À vérifier.",
                "",
                "## Codes d'erreur",
                "",
                (
                    "Les codes d’erreur propres aux vues ne sont pas encore "
                    "déduits automatiquement."
                ),
                "",
                "À vérifier.",
                "",
                "## Exemples",
                "",
                (
                    "Les exemples de requêtes seront ajoutés lorsque "
                    "l’analyse des serializers et de l’authentification "
                    "sera disponible."
                ),
                "",
            ]
        )

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _group_routes(
        routes: list[ApiRoute],
    ) -> dict[str, list[ApiRoute]]:
        grouped: defaultdict[str, list[ApiRoute]] = defaultdict(list)

        for route in routes:
            path_parts = [
                part
                for part in route.path.strip("/").split("/")
                if part
            ]

            if not path_parts:
                group = "Racine"
            elif path_parts[0] == "api" and len(path_parts) > 1:
                group = ApiDocumentGenerator._format_group(
                    path_parts[1]
                )
            else:
                group = ApiDocumentGenerator._format_group(
                    path_parts[0]
                )

            grouped[group].append(route)

        return dict(
            sorted(
                grouped.items(),
                key=lambda item: item[0].casefold(),
            )
        )

    @staticmethod
    def _format_group(value: str) -> str:
        cleaned = (
            value.replace("-", " ")
            .replace("_", " ")
            .replace("{id}", "Détail")
        )

        return cleaned.strip().title() or "Autres"

    @staticmethod
    def _code_list(values: list[str]) -> str:
        if not values:
            return "`aucun`"

        return ", ".join(
            f"`{value}`"
            for value in values
        )
