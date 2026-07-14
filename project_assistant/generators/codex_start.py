from __future__ import annotations

from project_assistant.knowledge import ProjectKnowledge
from project_assistant.models import Project


LOCAL_SECTION_START = "<!-- project-assistant:local-codex:start -->"
LOCAL_SECTION_END = "<!-- project-assistant:local-codex:end -->"


class CodexStartDocumentGenerator:
    def generate(
        self,
        project: Project,
        knowledge: ProjectKnowledge,
        existing_content: str | None = None,
    ) -> str:
        identity = knowledge.identity
        architecture = knowledge.architecture
        deployment = knowledge.deployment
        api = knowledge.api

        services = sorted(
            service.name
            for service in architecture.services
        )
        targets = set(deployment.make_targets)

        local_content = self._extract_local_section(
            existing_content or ""
        )

        lines = [
            "# CODEX_START.md",
            "",
            "<!--",
            "Document généré en aperçu par project-assistant.",
            "Ce fichier fournit le contexte initial aux agents logiciels.",
            "Les invariants globaux ne doivent jamais être modifiés automatiquement.",
            "-->",
            "",
            "## Mission",
            "",
            (
                f"Intervenir dans le dépôt `{project.name}` de manière "
                "limitée, vérifiable et conforme aux invariants globaux "
                "des applications auto-hébergées."
            ),
            "",
            (
                "Ne modifier que les fichiers nécessaires à la demande. "
                "Ne pas effectuer de refactorisation, migration ou "
                "standardisation supplémentaire sans justification."
            ),
            "",
            "## Ordre de lecture",
            "",
            "Avant toute modification, lire dans cet ordre :",
            "",
            "1. `INVARIANTS.md`;",
            "2. `AGENTS.md`;",
            "3. `CODEX_START.md`;",
            "4. `README.md`;",
            "5. `README_DEV.md`;",
            "6. `docs/architecture.md`;",
            "7. `docs/specification.md`;",
            "8. `docs/api.md` et `docs/deployment.md` lorsqu’ils existent.",
            "",
            "## Contexte du projet",
            "",
            f"- Nom : `{identity.name}`.",
            f"- Racine analysée : `{identity.root}`.",
            f"- Langages : {self._code_list(identity.languages)}.",
            f"- Frameworks : {self._code_list(identity.frameworks)}.",
            f"- Technologies : {self._code_list(identity.technologies)}.",
            f"- Routes API détectées : `{len(api.routes)}`.",
            "",
            "## Architecture essentielle",
            "",
            f"- Services Docker : {self._code_list(services)}.",
            f"- Fichiers Compose : {self._code_list(architecture.compose_files)}.",
            f"- Réseaux Docker : {self._code_list(architecture.networks)}.",
            f"- Réseaux externes : {self._code_list(architecture.external_networks)}.",
            f"- Volumes nommés : {self._code_list(architecture.volumes)}.",
            "",
        ]

        if architecture.uses_traefik:
            lines.append(
                "- Traefik constitue le point d’entrée HTTP/HTTPS de production."
            )

        if "PostgreSQL" in identity.technologies:
            lines.append(
                "- PostgreSQL assure la persistance relationnelle."
            )

        if "React" in identity.frameworks:
            lines.append(
                "- Le frontend React communique avec le backend par l’API."
            )

        if "Django" in identity.frameworks:
            lines.append(
                "- Le backend Django applique la logique métier et les contrôles d’accès."
            )

        lines.extend(
            [
                "",
                "## Invariants à respecter",
                "",
                (
                    "`app-template/INVARIANTS.md` constitue la source "
                    "canonique des invariants globaux."
                ),
                "",
                "Règles absolues :",
                "",
                "- ne jamais modifier, supprimer, assouplir ou contourner un invariant global;",
                "- ne jamais modifier un invariant local sans autorisation explicite du propriétaire;",
                "- corriger le projet lorsqu’il contredit un invariant;",
                "- ne jamais adapter les invariants pour justifier l’état actuel du code;",
                "- ne jamais lire, afficher ou committer `.env.local`;",
                "- conserver les secrets exclusivement dans `.env.local`;",
                "- utiliser le lien `.env` pour sélectionner `.env.dev` ou `.env.prod`;",
                "- utiliser les noms de services, scripts et cibles Makefile canoniques;",
                "- utiliser `docker compose`, jamais l’ancienne commande `docker-compose`;",
                "- ne jamais inventer une route, un port, un domaine ou une variable.",
                "",
                (
                    "Toute évolution possible d’un invariant doit être "
                    "présentée séparément avec sa justification, ses impacts "
                    "et les migrations nécessaires. Elle ne doit jamais être "
                    "appliquée sans validation explicite du propriétaire."
                ),
                "",
                "## Commandes importantes",
                "",
            ]
        )

        commands = self._important_commands(targets)

        if commands:
            for title, command in commands:
                lines.append(f"### {title}")
                lines.append("")
                self._append_command(lines, command)
        else:
            lines.extend(
                [
                    "_Aucune commande Makefile standard n’a été détectée._",
                    "",
                ]
            )

        lines.extend(
            [
                "## État de l’environnement",
                "",
            ]
        )

        if project.environment.env_symlink_exists:
            lines.extend(
                [
                    (
                        f"- Environnement actif détecté : "
                        f"`{project.environment.active_environment or 'inconnu'}`."
                    ),
                    (
                        f"- Le lien `.env` pointe vers "
                        f"`{project.environment.env_symlink_target}`."
                    ),
                ]
            )
        else:
            lines.append(
                "- Le lien `.env` n’est pas présent dans l’état analysé."
            )

        lines.extend(
            [
                "- `.env.dev` et `.env.prod` contiennent la configuration non secrète;",
                "- `.env.local` contient les secrets et ne doit jamais être lu ou affiché;",
                "",
                "## Méthode d’intervention",
                "",
                "1. comprendre la demande exacte;",
                "2. lire les documents obligatoires;",
                "3. examiner le code concerné;",
                "4. établir un changement minimal;",
                "5. modifier uniquement les fichiers nécessaires;",
                "6. exécuter les contrôles appropriés;",
                "7. examiner `git diff` et `git status`;",
                "8. résumer précisément les changements et les limites.",
                "",
                "## Validation avant de terminer",
                "",
            ]
        )

        validations = self._validation_steps(targets)

        for index, validation in enumerate(
            validations,
            start=1,
        ):
            lines.append(f"{index}. {validation}")

        lines.extend(
            [
                "",
                "Toujours confirmer :",
                "",
                "- qu’aucun secret n’apparaît dans les changements;",
                "- qu’aucun invariant n’a été modifié sans autorisation;",
                "- que les fichiers générés restent en aperçu tant qu’ils ne sont pas validés;",
                "- que les tests ou contrôles échoués sont signalés clairement;",
                "- que la documentation reste cohérente avec le comportement actuel.",
                "",
                "## Instructions locales",
                "",
                LOCAL_SECTION_START,
            ]
        )

        if local_content:
            lines.append(local_content.rstrip())
        else:
            lines.extend(
                [
                    "",
                    "_Ajouter ici le contexte de démarrage propre à cette application._",
                    "",
                    (
                        "_Cette section est conservée lors des futures "
                        "régénérations déterministes._"
                    ),
                    "",
                ]
            )

        lines.extend(
            [
                LOCAL_SECTION_END,
                "",
            ]
        )

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _important_commands(
        targets: set[str],
    ) -> list[tuple[str, str]]:
        mapping = (
            ("Sélectionner le développement", "dev", "make dev"),
            ("Sélectionner la production", "prod", "make prod"),
            ("Initialiser le développement", "init-dev", "make init-dev"),
            ("Démarrer les services", "up", "make up"),
            ("Arrêter les services", "down", "make down"),
            ("Afficher les services", "ps", "make ps"),
            ("Afficher les journaux", "logs", "make logs"),
            ("Exécuter les migrations", "migrate", "make migrate"),
            ("Vérifier les invariants", "check", "make check"),
            ("Exécuter les tests", "test", "make test"),
        )

        return [
            (title, command)
            for title, target, command in mapping
            if target in targets
        ]

    @staticmethod
    def _validation_steps(
        targets: set[str],
    ) -> list[str]:
        steps: list[str] = []

        mapping = (
            ("check", "exécuter `make check`;"),
            ("test", "exécuter `make test`;"),
            ("test-backend", "exécuter `make test-backend`;"),
            ("test-frontend", "exécuter `make test-frontend`;"),
            ("ps", "exécuter `make ps` si la stack est démarrée;"),
        )

        for target, description in mapping:
            if target in targets:
                steps.append(description)

        steps.extend(
            [
                "examiner `git diff`;",
                "examiner `git status`;",
                "vérifier que les fichiers modifiés correspondent à la demande;",
                "mettre à jour la documentation concernée si nécessaire.",
            ]
        )

        return steps

    @staticmethod
    def _extract_local_section(content: str) -> str:
        if (
            LOCAL_SECTION_START not in content
            or LOCAL_SECTION_END not in content
        ):
            return ""

        after_start = content.split(
            LOCAL_SECTION_START,
            1,
        )[1]

        return after_start.split(
            LOCAL_SECTION_END,
            1,
        )[0].strip()

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
