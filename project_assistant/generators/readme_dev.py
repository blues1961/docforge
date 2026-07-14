from __future__ import annotations

from project_assistant.knowledge import ProjectKnowledge
from project_assistant.models import Project


class ReadmeDevDocumentGenerator:
    def generate(
        self,
        project: Project,
        knowledge: ProjectKnowledge,
    ) -> str:
        deployment = knowledge.deployment
        architecture = knowledge.architecture
        identity = knowledge.identity

        targets = set(deployment.make_targets)
        services = sorted(
            service.name
            for service in architecture.services
        )

        lines = [
            f"# {project.name} — Guide de développement",
            "",
            "<!--",
            "Document généré en aperçu par project-assistant.",
            "Le contenu est dérivé de l’état actuel du dépôt.",
            "Les secrets ne sont jamais lus ni reproduits.",
            "-->",
            "",
            "## Prérequis",
            "",
            "- Git;",
        ]

        if "Docker Compose" in identity.technologies:
            lines.append(
                "- Docker et le plugin `docker compose`;"
            )

        if "Python" in identity.languages:
            lines.append(
                "- Python pour les outils locaux du projet, "
                "lorsqu’ils sont exécutés hors conteneur;"
            )

        if "JavaScript" in identity.languages:
            lines.append(
                "- Node.js et npm uniquement lorsque les commandes "
                "frontend sont exécutées hors conteneur;"
            )

        if architecture.uses_traefik:
            lines.append(
                "- le réseau Docker externe `edge` pour reproduire "
                "le routage de production;"
            )

        lines.extend(
            [
                "- les fichiers `.env.dev` et `.env.prod`;",
                "- un fichier local `.env.local` contenant les secrets requis.",
                "",
                "Les secrets doivent rester dans `.env.local`. "
                "Ce fichier ne doit jamais être ajouté à Git ni affiché "
                "dans les journaux ou la documentation.",
                "",
                "## Installation locale",
                "",
                "Depuis la racine du dépôt :",
                "",
            ]
        )

        if "init-dev" in targets:
            self._append_command(
                lines,
                "make init-dev",
            )
        else:
            if "init" in targets:
                self._append_command(
                    lines,
                    "make init",
                )

            if "dev" in targets:
                self._append_command(
                    lines,
                    "make dev",
                )

            if "up" in targets:
                self._append_command(
                    lines,
                    "make up",
                )

        if not targets.intersection(
            {"init-dev", "init", "dev", "up"}
        ):
            lines.extend(
                [
                    "_Aucune commande standard d’initialisation "
                    "n’a été détectée dans le Makefile._",
                    "",
                ]
            )

        lines.extend(
            [
                "Après l’initialisation, vérifier l’état des services :",
                "",
            ]
        )

        if "ps" in targets:
            self._append_command(lines, "make ps")
        else:
            lines.extend(
                [
                    "```bash",
                    "docker compose ps",
                    "```",
                    "",
                ]
            )

        lines.extend(
            [
                "## Environnements",
                "",
            ]
        )

        if (project.root / ".env.dev").is_file():
            lines.append(
                "- `.env.dev` contient la configuration versionnée "
                "du développement."
            )

        if (project.root / ".env.prod").is_file():
            lines.append(
                "- `.env.prod` contient la configuration versionnée "
                "de la production."
            )

        lines.extend(
            [
                "- `.env.local` contient les secrets locaux et "
                "n’est jamais versionné.",
                "- `.env` sélectionne l’environnement actif par "
                "lien symbolique vers `.env.dev` ou `.env.prod`.",
                "",
            ]
        )

        if project.environment.env_symlink_exists:
            lines.append(
                "Environnement actif détecté : "
                f"`{project.environment.active_environment or 'inconnu'}`."
            )
            lines.append("")
            lines.append(
                "Cible actuelle du lien `.env` : "
                f"`{project.environment.env_symlink_target}`."
            )
            lines.append("")
        else:
            lines.extend(
                [
                    "Le lien `.env` n’est pas présent dans l’état "
                    "analysé du dépôt.",
                    "",
                ]
            )

        if "dev" in targets or "prod" in targets:
            lines.extend(
                [
                    "Pour changer d’environnement, utiliser les "
                    "commandes du Makefile :",
                    "",
                ]
            )

            if "dev" in targets:
                self._append_command(lines, "make dev")

            if "prod" in targets:
                self._append_command(lines, "make prod")

        lines.extend(
            [
                "## Services de développement",
                "",
            ]
        )

        if services:
            lines.append(
                "Services Docker détectés :"
            )
            lines.append("")

            for service in services:
                lines.append(f"- `{service}`")

            lines.append("")
        else:
            lines.extend(
                [
                    "Aucun service Docker n’a été détecté.",
                    "",
                ]
            )

        lines.extend(
            [
                "## Commandes de développement",
                "",
            ]
        )

        commands = self._development_commands(targets)

        if commands:
            for title, command in commands:
                lines.append(f"### {title}")
                lines.append("")
                self._append_command(lines, command)
        else:
            lines.extend(
                [
                    "_Aucune commande de développement standard "
                    "n’a été détectée._",
                    "",
                ]
            )

        lines.extend(
            [
                "## Tests",
                "",
            ]
        )

        test_commands = self._test_commands(targets)

        if test_commands:
            lines.append(
                "Exécuter les contrôles disponibles avant toute livraison :"
            )
            lines.append("")

            for command in test_commands:
                self._append_command(lines, command)
        else:
            lines.extend(
                [
                    "Aucune cible de test ou de validation standard "
                    "n’a été détectée dans le Makefile.",
                    "",
                    "Les commandes de test propres au backend et au "
                    "frontend doivent être documentées manuellement.",
                    "",
                ]
            )

        lines.extend(
            [
                "## Flux de travail Git",
                "",
                "Flux recommandé :",
                "",
                "1. vérifier que la branche locale est à jour;",
                "2. créer une branche dédiée au changement;",
                "3. effectuer une modification limitée et cohérente;",
                "4. exécuter les tests et contrôles disponibles;",
                "5. examiner `git diff` avant le commit;",
                "6. créer un commit descriptif;",
                "7. pousser la branche et utiliser une pull request "
                "lorsque le dépôt l’exige.",
                "",
                "Commandes de base :",
                "",
                "```bash",
                "git status",
                "git pull --ff-only",
                "git switch -c type/description-courte",
                "git diff",
                "git add <fichiers>",
                'git commit -m "type: description"',
                "```",
                "",
                "Ne jamais committer `.env.local`, `.env`, des "
                "sauvegardes de base de données ou des secrets.",
                "",
                "## Validation avant livraison",
                "",
            ]
        )

        validation_commands = self._validation_commands(
            targets
        )

        if validation_commands:
            lines.append(
                "Exécuter, selon les cibles disponibles :"
            )
            lines.append("")

            for command in validation_commands:
                self._append_command(lines, command)
        else:
            lines.extend(
                [
                    "Aucune commande standard de validation n’a "
                    "été détectée.",
                    "",
                ]
            )

        lines.extend(
            [
                "Vérifications manuelles minimales :",
                "",
                "- aucun secret n’apparaît dans `git diff`;",
                "- les services attendus démarrent correctement;",
                "- les migrations nécessaires ont été exécutées;",
                "- les journaux ne contiennent pas d’erreur bloquante;",
                "- la documentation correspond au comportement actuel;",
                "- les invariants globaux et locaux sont respectés.",
                "",
                "Les règles communes aux applications auto-hébergées "
                "restent définies par `app-template/INVARIANTS.md`.",
                "",
            ]
        )

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _development_commands(
        targets: set[str],
    ) -> list[tuple[str, str]]:
        mapping = (
            ("Démarrer la stack", "up", "make up"),
            ("Arrêter la stack", "down", "make down"),
            ("Redémarrer la stack", "restart", "make restart"),
            ("Reconstruire les images", "rebuild", "make rebuild"),
            ("Afficher les services", "ps", "make ps"),
            ("Suivre les journaux", "logs", "make logs"),
            ("Ouvrir un shell", "sh", "make sh"),
            ("Exécuter les migrations", "migrate", "make migrate"),
            (
                "Créer les migrations Django",
                "makemigrations",
                "make makemigrations",
            ),
            (
                "Créer un administrateur",
                "createsuperuser",
                "make createsuperuser",
            ),
        )

        return [
            (title, command)
            for title, target, command in mapping
            if target in targets
        ]

    @staticmethod
    def _test_commands(
        targets: set[str],
    ) -> list[str]:
        ordered_targets = (
            "check",
            "test",
            "test-backend",
            "test-frontend",
        )

        return [
            f"make {target}"
            for target in ordered_targets
            if target in targets
        ]

    @staticmethod
    def _validation_commands(
        targets: set[str],
    ) -> list[str]:
        ordered_targets = (
            "check",
            "test",
            "ps",
            "logs",
        )

        return [
            f"make {target}"
            for target in ordered_targets
            if target in targets
        ]

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
