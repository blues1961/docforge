from __future__ import annotations

from docforge.analyzers import (
    SpecificationFacts,
)
from docforge.models import Project


class SpecificationDocumentGenerator:
    def generate(
        self,
        project: Project,
        facts: SpecificationFacts,
    ) -> str:
        lines = [
            f"# Spécification — {project.name}",
            "",
            "<!--",
            "Document généré en aperçu par docforge.",
            "Le contenu est dérivé de l’état actuel du dépôt.",
            "Toute exigence métier non détectable dans le code doit être validée manuellement.",
            "-->",
            "",
            "## Objectifs",
            "",
            (
                f"`{project.name}` est une application auto-hébergée "
                "dont l’architecture détectée sépare l’interface, "
                "la logique applicative et la persistance."
            ),
            "",
            (
                "Cette spécification décrit uniquement les capacités "
                "et contraintes observables dans le dépôt."
            ),
            "",
            "## Portée",
            "",
            "La portée technique détectée comprend :",
            "",
        ]

        if facts.uses_react:
            lines.append(
                "- une interface utilisateur React;"
            )

        if facts.uses_django:
            lines.append(
                "- un backend Django;"
            )

        if facts.uses_postgresql:
            lines.append(
                "- une persistance PostgreSQL;"
            )

        if facts.uses_docker_compose:
            lines.append(
                "- une orchestration Docker Compose;"
            )

        if facts.uses_traefik:
            lines.append(
                "- une exposition de production par Traefik."
            )

        if facts.api_route_count:
            lines.append(
                f"- une API contenant `{facts.api_route_count}` "
                "route(s) détectée(s)."
            )

        lines.extend(
            [
                "",
                "Les fonctionnalités métier précises doivent être complétées "
                "à partir des vues, modèles et parcours utilisateur propres "
                "au projet.",
                "",
                "## Exigences fonctionnelles",
                "",
            ]
        )

        if facts.api_groups:
            lines.append(
                "Les domaines fonctionnels suivants sont exposés "
                "dans les routes détectées :"
            )
            lines.append("")

            for group in facts.api_groups:
                lines.append(f"- `{group}`")

            lines.append("")
        else:
            lines.extend(
                [
                    "Aucun domaine fonctionnel fiable n’a pu être "
                    "déduit automatiquement des routes.",
                    "",
                ]
            )

        lines.extend(
            [
                "Exigences générales observables :",
                "",
            ]
        )

        if facts.uses_react:
            lines.append(
                "- l’utilisateur doit pouvoir accéder à une interface web;"
            )

        if facts.uses_django:
            lines.append(
                "- le backend doit appliquer la logique métier et valider les requêtes;"
            )

        if facts.api_route_count:
            lines.append(
                "- les échanges entre le frontend et le backend doivent passer par les routes API détectées;"
            )

        if facts.uses_postgresql:
            lines.append(
                "- les données persistantes doivent être stockées dans PostgreSQL."
            )

        lines.extend(
            [
                "",
                "## Exigences techniques",
                "",
                f"- Langages : {self._code_list(facts.languages)}.",
                f"- Frameworks : {self._code_list(facts.frameworks)}.",
                f"- Technologies : {self._code_list(facts.technologies)}.",
                f"- Services frontend : {self._code_list(facts.frontend_services)}.",
                f"- Services backend : {self._code_list(facts.backend_services)}.",
                f"- Services de données : {self._code_list(facts.database_services)}.",
                f"- Fichiers Compose : {self._code_list(facts.compose_files)}.",
                f"- Environnements détectés : {self._code_list(facts.environments)}.",
                "",
                "## Contraintes",
                "",
            ]
        )

        constraints: list[str] = []

        if facts.uses_docker_compose:
            constraints.append(
                "les services doivent être démarrés avec Docker Compose"
            )

        if facts.uses_traefik:
            constraints.append(
                "Traefik doit rester le point d’entrée HTTP/HTTPS de production"
            )

        if facts.uses_postgresql:
            constraints.append(
                "PostgreSQL doit assurer la persistance relationnelle"
            )

        if facts.environments:
            constraints.append(
                "les environnements de développement et de production doivent rester séparés"
            )

        if constraints:
            for constraint in constraints:
                lines.append(f"- {constraint};")
        else:
            lines.append(
                "- les contraintes opérationnelles doivent être validées manuellement."
            )

        lines.extend(
            [
                "",
                "Les invariants globaux applicables restent définis par "
                "`app-template/INVARIANTS.md`.",
                "",
                "## Critères d’acceptation",
                "",
            ]
        )

        acceptance = [
            "les fichiers obligatoires du projet sont présents;",
            "la configuration locale est valide;",
            "les services Docker démarrent sans erreur;",
            "les migrations applicables réussissent;",
            "les contrôles du Makefile réussissent;",
        ]

        if "test" in facts.make_targets:
            acceptance.append(
                "la commande `make test` réussit;"
            )

        if "check" in facts.make_targets:
            acceptance.append(
                "la commande `make check` réussit;"
            )

        if "ps" in facts.make_targets:
            acceptance.append(
                "la commande `make ps` confirme que les services attendus sont actifs;"
            )

        for item in acceptance:
            lines.append(f"- {item}")

        lines.extend(
            [
                "",
                "## Points à valider manuellement",
                "",
                "- les objectifs métier détaillés;",
                "- les rôles et permissions des utilisateurs;",
                "- les règles métier non exprimées directement dans les routes;",
                "- les scénarios d’erreur fonctionnels;",
                "- les exigences de performance et de disponibilité;",
                "- les critères d’acceptation propres au produit.",
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
