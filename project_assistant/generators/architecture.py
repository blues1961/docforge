from __future__ import annotations

from project_assistant.analyzers import ArchitectureFacts
from project_assistant.models import Project


class ArchitectureDocumentGenerator:
    def generate(
        self,
        project: Project,
        facts: ArchitectureFacts,
    ) -> str:
        lines = [
            f"# Architecture — {project.name}",
            "",
            "<!--",
            "Document généré en aperçu par project-assistant.",
            "Le contenu doit être validé avant son intégration.",
            "-->",
            "",
            "## Vue d'ensemble",
            "",
            (
                f"`{project.name}` est une application "
                f"{self._architecture_summary(facts)}."
            ),
            "",
            f"- Langages détectés : {self._code_list(facts.languages)}.",
            f"- Frameworks détectés : {self._code_list(facts.frameworks)}.",
            f"- Technologies détectées : {self._code_list(facts.technologies)}.",
            f"- Fichiers Docker Compose : {self._code_list(facts.compose_files)}.",
            "",
            "## Composants",
            "",
        ]

        if facts.frontend_services:
            lines.extend(
                [
                    "### Frontend",
                    "",
                    (
                        "Services frontend détectés : "
                        f"{self._code_list(facts.frontend_services)}."
                    ),
                    "",
                ]
            )

        if facts.backend_services:
            lines.extend(
                [
                    "### Backend",
                    "",
                    (
                        "Services backend détectés : "
                        f"{self._code_list(facts.backend_services)}."
                    ),
                    "",
                ]
            )

        if facts.database_services:
            lines.extend(
                [
                    "### Base de données",
                    "",
                    (
                        "Services de base de données détectés : "
                        f"{self._code_list(facts.database_services)}."
                    ),
                    "",
                ]
            )

        lines.extend(
            [
                "### Services Docker",
                "",
                "| Service | Environnements | Image / build | Dépendances | Healthcheck |",
                "|---|---|---|---|---|",
            ]
        )

        for service in facts.services:
            image_or_build = self._service_source(service)

            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{service.name}`",
                        self._code_list(service.environments),
                        image_or_build,
                        self._code_list(service.depends_on),
                        "oui" if service.healthcheck else "non détecté",
                    ]
                )
                + " |"
            )

        lines.extend(
            [
                "",
                "## Flux de données",
                "",
            ]
        )

        if (
            facts.frontend_services
            and facts.backend_services
            and facts.database_services
        ):
            lines.extend(
                [
                    "Le flux applicatif principal détecté est le suivant :",
                    "",
                    "1. Le navigateur charge l’interface servie par le frontend.",
                    "2. Le frontend communique avec le backend par HTTP.",
                    "3. Le backend applique la logique métier et accède à PostgreSQL.",
                    "4. Les réponses du backend sont retournées au frontend.",
                    "",
                ]
            )
        else:
            lines.extend(["À vérifier.", ""])

        lines.extend(
            [
                "## Flux réseau",
                "",
                f"- Réseaux Docker détectés : {self._code_list(facts.networks)}.",
                f"- Réseaux externes : {self._code_list(facts.external_networks)}.",
                "",
            ]
        )

        if facts.uses_traefik:
            lines.extend(
                [
                    "Traefik agit comme point d’entrée HTTP/HTTPS en production.",
                    "Les routes détectées dans les labels Compose sont :",
                    "",
                ]
            )

            routes_found = False

            for service in facts.services:
                for route in service.traefik_routes:
                    routes_found = True
                    lines.append(
                        f"- `{service.name}` : `{route}`"
                    )

            if not routes_found:
                lines.append("- À vérifier.")

            lines.append("")
        else:
            lines.extend(
                [
                    "Aucune configuration Traefik n’a été détectée.",
                    "",
                ]
            )

        for service in facts.services:
            if not service.ports:
                continue

            lines.append(
                f"- Ports publiés par `{service.name}` : "
                f"{self._code_list(service.ports)}."
            )

        lines.extend(
            [
                "",
                "## Persistance",
                "",
                f"- Volumes nommés : {self._code_list(facts.volumes)}.",
                "",
            ]
        )

        for service in facts.services:
            if not service.volumes:
                continue

            lines.append(
                f"- Montages de `{service.name}` : "
                f"{self._code_list(service.volumes)}."
            )

        lines.extend(
            [
                "",
                "## Sécurité",
                "",
                "- Les secrets locaux sont conservés dans les fichiers se terminant par `.local`.",
                "- Le fichier `.env` est un lien symbolique vers la configuration de l’environnement actif.",
                f"- Fichiers d’environnement détectés : {self._code_list(facts.environment_files)}.",
            ]
        )

        if facts.uses_traefik:
            lines.append(
                "- Traefik assure la terminaison et le routage HTTP/HTTPS en production."
            )

        lines.extend(
            [
                "",
                "Les contraintes de sécurité détaillées restent définies dans `INVARIANTS.md` et dans la documentation spécialisée du projet.",
                "",
                "## Décisions d'architecture",
                "",
                "- Le frontend, le backend et la base de données sont séparés en services Docker.",
                "- Les environnements de développement et de production possèdent des fichiers Compose distincts.",
                "- `.env` sélectionne la configuration active par lien symbolique.",
            ]
        )

        if facts.uses_traefik:
            lines.append(
                "- Traefik est le point d’entrée réseau de la production."
            )

        if "Vite" in facts.frameworks:
            lines.append(
                "- Vite est utilisé pour le développement ou la construction du frontend."
            )

        if facts.uses_postgresql:
            lines.append(
                "- PostgreSQL assure la persistance relationnelle."
            )

        lines.extend(
            [
                "",
                "## Limites et dette technique",
                "",
                "Les limites connues et les écarts qui ne doivent pas être aggravés sont documentés dans `INVARIANTS.md`, `README_DEV.md` et `docs/specification.md`.",
                "",
            ]
        )

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _architecture_summary(
        facts: ArchitectureFacts,
    ) -> str:
        parts: list[str] = []

        if "React" in facts.frameworks:
            parts.append("avec frontend React")

        if "Django" in facts.frameworks:
            parts.append("backend Django")

        if facts.uses_postgresql:
            parts.append("base de données PostgreSQL")

        if facts.compose_files:
            parts.append("orchestrée avec Docker Compose")

        if facts.uses_traefik:
            parts.append("exposée par Traefik")

        return ", ".join(parts) or "dont l’architecture reste à vérifier"

    @staticmethod
    def _service_source(service: object) -> str:
        image = getattr(service, "image", None)
        build_contexts = getattr(
            service,
            "build_contexts",
            [],
        )

        values: list[str] = []

        if image:
            values.append(f"image `{image}`")

        values.extend(
            f"build `{context}`"
            for context in build_contexts
        )

        return "<br>".join(values) or "À vérifier"

    @staticmethod
    def _code_list(values: list[str]) -> str:
        if not values:
            return "`aucun`"

        return ", ".join(
            f"`{value}`"
            for value in values
        )
