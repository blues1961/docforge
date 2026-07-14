from __future__ import annotations

from project_assistant.analyzers import ReadmeFacts
from project_assistant.models import Project


class ReadmeDocumentGenerator:
    def generate(
        self,
        project: Project,
        facts: ReadmeFacts,
    ) -> str:
        lines = [
            f"# {project.name}",
            "",
            "<!--",
            "Document généré en aperçu par project-assistant.",
            "Le contenu est dérivé de l’état actuel du dépôt.",
            "Les objectifs métier non détectables doivent être validés manuellement.",
            "-->",
            "",
            "## Résumé du projet",
            "",
            self._summary(facts),
            "",
            (
                "La description fonctionnelle précise doit être "
                "complétée à partir des besoins métier du projet."
            ),
            "",
            "## Fonctionnalités principales",
            "",
        ]

        features = self._features(facts)

        if features:
            lines.extend(
                f"- {feature}"
                for feature in features
            )
        else:
            lines.append(
                "- Aucune fonctionnalité fiable n’a été "
                "déduite automatiquement."
            )

        lines.extend(
            [
                "",
                "## Architecture générale",
                "",
            ]
        )

        if facts.services:
            lines.append(
                "Les services Docker détectés sont :"
            )
            lines.append("")

            for service in facts.services:
                lines.append(f"- `{service}`")

            lines.append("")

        architecture_steps = self._architecture_steps(
            facts
        )

        for index, step in enumerate(
            architecture_steps,
            start=1,
        ):
            lines.append(f"{index}. {step}")

        lines.extend(
            [
                "",
                "Les détails sont documentés dans "
                "`docs/architecture.md` lorsqu’il est présent.",
                "",
                "## Technologies utilisées",
                "",
                f"- Langages : {self._code_list(facts.languages)}.",
                f"- Frameworks : {self._code_list(facts.frameworks)}.",
                f"- Technologies : {self._code_list(facts.technologies)}.",
                f"- Fichiers Compose : {self._code_list(facts.compose_files)}.",
                f"- Réseaux externes : {self._code_list(facts.external_networks)}.",
                f"- Volumes nommés : {self._code_list(facts.named_volumes)}.",
                "",
                "## Installation",
                "",
                "### Prérequis",
                "",
            ]
        )

        prerequisites = self._prerequisites(facts)

        for prerequisite in prerequisites:
            lines.append(f"- {prerequisite}")

        lines.extend(
            [
                "",
                "### Initialisation locale",
                "",
                "Depuis la racine du dépôt :",
                "",
            ]
        )

        if "init" in facts.make_targets:
            self._append_command(
                lines,
                "make init",
            )

        if "dev" in facts.make_targets:
            self._append_command(
                lines,
                "make dev",
            )

        if "up" in facts.make_targets:
            self._append_command(
                lines,
                "make up",
            )

        if not any(
            target in facts.make_targets
            for target in ("init", "dev", "up")
        ):
            lines.extend(
                [
                    "_Aucune commande d’installation standard "
                    "n’a été détectée dans le Makefile._",
                    "",
                ]
            )

        lines.extend(
            [
                "Les secrets requis doivent être placés dans "
                "`.env.local`. Ce fichier ne doit jamais être "
                "ajouté à Git.",
                "",
                "## Utilisation",
                "",
            ]
        )

        usage_commands = self._usage_commands(facts)

        if usage_commands:
            for title, command in usage_commands:
                lines.append(f"### {title}")
                lines.append("")
                self._append_command(lines, command)
        else:
            lines.extend(
                [
                    "_Aucune commande d’utilisation standard "
                    "n’a été détectée._",
                    "",
                ]
            )

        lines.extend(
            [
                "## Configuration",
                "",
                f"- Environnements détectés : {self._code_list(facts.environments)}.",
            ]
        )

        if facts.env_symlink_exists:
            lines.append(
                f"- Le lien `.env` pointe actuellement vers "
                f"`{facts.env_symlink_target}`."
            )
        else:
            lines.append(
                "- Le lien `.env` n’est pas présent dans l’état "
                "analysé du dépôt."
            )

        lines.extend(
            [
                "- `.env.dev` et `.env.prod` contiennent la "
                "configuration non secrète propre aux environnements.",
                "- `.env.local` contient uniquement les secrets locaux.",
                "- `.env` sélectionne l’environnement actif et ne "
                "doit pas être modifié directement.",
                "",
                "Les conventions globales restent définies par "
                "`app-template/INVARIANTS.md`.",
                "",
                "## Documentation complémentaire",
                "",
            ]
        )

        if facts.documentation_files:
            for document in facts.documentation_files:
                lines.append(
                    f"- [`{document}`]({document})"
                )
        else:
            lines.append(
                "- Aucun document complémentaire n’a été détecté."
            )

        lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _summary(facts: ReadmeFacts) -> str:
        components: list[str] = []

        if facts.uses_react:
            components.append("une interface React")

        if facts.uses_django:
            components.append("un backend Django")

        if facts.uses_postgresql:
            components.append("une base de données PostgreSQL")

        if facts.uses_docker_compose:
            components.append(
                "une orchestration Docker Compose"
            )

        if facts.uses_traefik:
            components.append(
                "une exposition de production par Traefik"
            )

        if not components:
            return (
                f"`{facts.project_name}` est un projet logiciel "
                "dont les composants principaux n’ont pas pu être "
                "déterminés automatiquement."
            )

        return (
            f"`{facts.project_name}` est une application "
            "auto-hébergée comprenant "
            + ReadmeDocumentGenerator._join_french(
                components
            )
            + "."
        )

    @staticmethod
    def _features(
        facts: ReadmeFacts,
    ) -> list[str]:
        features: list[str] = []

        if facts.uses_react:
            features.append(
                "interface utilisateur web construite avec React"
            )

        if facts.uses_django:
            features.append(
                "logique applicative et API fournies par Django"
            )

        if facts.api_route_count:
            features.append(
                f"`{facts.api_route_count}` route(s) API détectée(s)"
            )

        if facts.api_groups:
            features.append(
                "domaines API détectés : "
                + ", ".join(
                    f"`{group}`"
                    for group in facts.api_groups
                )
            )

        if facts.uses_postgresql:
            features.append(
                "persistance relationnelle avec PostgreSQL"
            )

        if facts.uses_traefik:
            features.append(
                "routage HTTP/HTTPS de production avec Traefik"
            )

        if "backup" in facts.make_targets:
            features.append(
                "sauvegarde pilotée par le Makefile"
            )

        if "restore" in facts.make_targets:
            features.append(
                "restauration pilotée par le Makefile"
            )

        if "check" in facts.make_targets:
            features.append(
                "contrôle automatisé des invariants"
            )

        return features

    @staticmethod
    def _architecture_steps(
        facts: ReadmeFacts,
    ) -> list[str]:
        steps: list[str] = []

        if facts.uses_react:
            steps.append(
                "Le navigateur charge l’interface frontend."
            )

        if facts.uses_django:
            steps.append(
                "Le frontend communique avec le backend par HTTP."
            )

        if facts.uses_postgresql:
            steps.append(
                "Le backend applique la logique métier et "
                "accède à PostgreSQL."
            )

        if facts.uses_traefik:
            steps.append(
                "Traefik assure le routage public HTTP/HTTPS "
                "en production."
            )

        if not steps:
            steps.append(
                "Le flux applicatif doit être documenté manuellement."
            )

        return steps

    @staticmethod
    def _prerequisites(
        facts: ReadmeFacts,
    ) -> list[str]:
        prerequisites = [
            "Git;",
        ]

        if facts.uses_docker_compose:
            prerequisites.append(
                "Docker et le plugin Docker Compose;"
            )

        if facts.uses_traefik:
            prerequisites.append(
                "un réseau Docker externe `edge` et une instance "
                "Traefik pour la production;"
            )

        prerequisites.append(
            "les fichiers de configuration d’environnement;"
        )
        prerequisites.append(
            "un fichier `.env.local` contenant les secrets requis."
        )

        return prerequisites

    @staticmethod
    def _usage_commands(
        facts: ReadmeFacts,
    ) -> list[tuple[str, str]]:
        commands: list[tuple[str, str]] = []

        mapping = (
            ("Démarrer les services", "up", "make up"),
            ("Afficher l’état des services", "ps", "make ps"),
            ("Afficher les journaux", "logs", "make logs"),
            ("Exécuter les migrations", "migrate", "make migrate"),
            ("Exécuter les contrôles", "check", "make check"),
            ("Exécuter les tests", "test", "make test"),
            ("Arrêter les services", "down", "make down"),
        )

        for title, target, command in mapping:
            if target in facts.make_targets:
                commands.append(
                    (title, command)
                )

        return commands

    @staticmethod
    def _append_command(
        lines: list[str],
        command: str,
    ) -> None:
        lines.extend(
            [
                "```bash",
                command,
                "```",
                "",
            ]
        )

    @staticmethod
    def _code_list(values: list[str]) -> str:
        if not values:
            return "`aucun`"

        return ", ".join(
            f"`{value}`"
            for value in values
        )

    @staticmethod
    def _join_french(values: list[str]) -> str:
        if not values:
            return ""

        if len(values) == 1:
            return values[0]

        return (
            ", ".join(values[:-1])
            + " et "
            + values[-1]
        )
