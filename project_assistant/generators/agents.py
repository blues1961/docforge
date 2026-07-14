from __future__ import annotations

from project_assistant.knowledge import ProjectKnowledge
from project_assistant.models import Project


LOCAL_SECTION_START = "<!-- project-assistant:local-agents:start -->"
LOCAL_SECTION_END = "<!-- project-assistant:local-agents:end -->"


class AgentsDocumentGenerator:
    def generate(
        self,
        project: Project,
        knowledge: ProjectKnowledge,
        existing_content: str | None = None,
    ) -> str:
        architecture = knowledge.architecture
        deployment = knowledge.deployment
        identity = knowledge.identity

        services = sorted(
            service.name
            for service in architecture.services
        )
        targets = set(deployment.make_targets)

        local_content = self._extract_local_section(
            existing_content or ""
        )

        lines = [
            "# AGENTS.md",
            "",
            "<!--",
            "Document généré en aperçu par project-assistant.",
            "Les invariants globaux ne sont ni copiés ni modifiés ici.",
            "Toute modification structurante doit respecter app-template/INVARIANTS.md.",
            "-->",
            "",
            "## Portée",
            "",
            (
                f"Ces instructions s’appliquent à tout agent logiciel "
                f"intervenant dans le dépôt `{project.name}`."
            ),
            "",
            (
                "Elles concernent notamment Codex, ChatGPT, Claude, "
                "Gemini et tout autre outil automatisé capable de "
                "lire ou modifier le dépôt."
            ),
            "",
            "## Ordre de lecture obligatoire",
            "",
            "Avant toute modification, lire dans cet ordre :",
            "",
            "1. `INVARIANTS.md`;",
            "2. `CODEX_START.md`;",
            "3. `AGENTS.md`;",
            "4. `README.md`;",
            "5. `README_DEV.md`;",
            "6. `docs/architecture.md`;",
            "7. `docs/specification.md`;",
            "8. `docs/api.md` et `docs/deployment.md` lorsqu’ils existent.",
            "",
            "## Priorité des sources",
            "",
            "En cas de contradiction, l’ordre d’autorité est :",
            "",
            "1. `app-template/INVARIANTS.md` — invariants globaux;",
            "2. `INVARIANTS.md` du projet — contraintes locales;",
            "3. `CODEX_START.md` — contexte opérationnel immédiat;",
            "4. `AGENTS.md` — règles de travail des agents;",
            "5. la documentation technique;",
            "6. le code existant.",
            "",
            (
                "Le code existant ne constitue pas une justification "
                "pour modifier ou contourner un invariant."
            ),
            "",
            "## Règles non négociables",
            "",
            "- Ne jamais modifier, supprimer, assouplir ou contourner un invariant global.",
            "- Ne jamais adapter `app-template` à un projet particulier sans autorisation explicite du propriétaire.",
            "- Ne jamais lire, afficher, journaliser ou committer le contenu de `.env.local`.",
            "- Ne jamais ajouter de secret dans `.env.dev`, `.env.prod`, la documentation ou le code source.",
            "- Ne jamais modifier directement le lien `.env`; utiliser les commandes prévues par le projet.",
            "- Ne jamais appliquer automatiquement un aperçu documentaire sans validation.",
            "- Ne jamais remplacer une convention canonique par une convention parallèle.",
            "- Ne jamais inventer une route, un port, un service, un volume ou une variable d’environnement.",
            "",
            "## Architecture détectée",
            "",
            f"- Projet : `{identity.name}`.",
            f"- Langages : {self._code_list(identity.languages)}.",
            f"- Frameworks : {self._code_list(identity.frameworks)}.",
            f"- Technologies : {self._code_list(identity.technologies)}.",
            f"- Services Docker : {self._code_list(services)}.",
            f"- Fichiers Compose : {self._code_list(architecture.compose_files)}.",
            f"- Réseaux externes : {self._code_list(architecture.external_networks)}.",
            "",
        ]

        if architecture.uses_traefik:
            lines.append(
                "- Traefik est détecté comme point d’entrée HTTP/HTTPS."
            )

        if "PostgreSQL" in identity.technologies:
            lines.append(
                "- PostgreSQL est détecté comme base de données relationnelle."
            )

        lines.extend(
            [
                "",
                "## Conventions de développement",
                "",
            ]
        )

        conventions = self._conventions(
            services=services,
            targets=targets,
            uses_traefik=architecture.uses_traefik,
        )

        for convention in conventions:
            lines.append(f"- {convention}")

        lines.extend(
            [
                "",
                "## Actions interdites",
                "",
                "- modifier `INVARIANTS.md` sans demande explicite du propriétaire;",
                "- créer une cible Makefile concurrente à une cible canonique;",
                "- remplacer `docker compose` par l’ancienne commande `docker-compose`;",
                "- coder une URL backend absolue dans le frontend;",
                "- exposer publiquement un port applicatif sans justification documentée;",
                "- utiliser le rôle PostgreSQL `postgres` ou un rôle arbitraire si le projet définit une convention `APP_SLUG`;",
                "- supprimer un script standard pour le remplacer par une variante non documentée;",
                "- appliquer une migration destructive sans sauvegarde et validation;",
                "- masquer une erreur de test, de build, de migration ou de déploiement;",
                "",
                "## Vérifications obligatoires",
                "",
                "Avant de terminer une intervention :",
                "",
            ]
        )

        checks = self._checks(targets)

        for index, check in enumerate(checks, start=1):
            lines.append(f"{index}. {check}")

        lines.extend(
            [
                "",
                "Vérifier également :",
                "",
                "- `git diff` ne contient aucun secret;",
                "- les fichiers modifiés correspondent exactement à la demande;",
                "- les documents générés restent dans `.project-assistant/preview` tant qu’ils ne sont pas validés;",
                "- les changements de structure sont cohérents avec `app-template`;",
                "- toute dérogation est explicitement documentée et approuvée.",
                "",
                "## Protection des invariants",
                "",
                (
                    "Toute proposition d’évolution d’un invariant doit être "
                    "présentée séparément avec sa justification, les projets "
                    "touchés, les risques et les migrations nécessaires."
                ),
                "",
                (
                    "Une proposition ne doit jamais être appliquée "
                    "automatiquement. L’autorisation explicite du propriétaire "
                    "est obligatoire."
                ),
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
                    "_Ajouter ici uniquement les instructions propres à ce projet._",
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
    def _conventions(
        *,
        services: list[str],
        targets: set[str],
        uses_traefik: bool,
    ) -> list[str]:
        conventions = [
            "utiliser les noms de services Docker détectés sans les renommer arbitrairement;",
            "utiliser les fichiers `.env.dev`, `.env.prod`, `.env.local` et le lien `.env` selon les invariants;",
            "passer par les commandes Makefile disponibles plutôt que reconstruire des commandes parallèles;",
            "maintenir une séparation stricte entre configuration versionnée et secrets locaux;",
            "préserver les fichiers et scripts canoniques du projet;",
        ]

        if {"backend", "frontend", "db"}.issubset(services):
            conventions.append(
                "préserver la séparation standard entre `backend`, `frontend` et `db`;"
            )

        if uses_traefik:
            conventions.append(
                "préserver Traefik comme point d’entrée de production;"
            )

        if "check" in targets:
            conventions.append(
                "exécuter `make check` après toute modification structurante;"
            )

        if "test" in targets:
            conventions.append(
                "exécuter `make test` avant de proposer la livraison;"
            )

        return conventions

    @staticmethod
    def _checks(targets: set[str]) -> list[str]:
        checks: list[str] = []

        mapping = (
            ("check", "exécuter `make check`;"),
            ("test", "exécuter `make test`;"),
            ("test-backend", "exécuter `make test-backend`;"),
            ("test-frontend", "exécuter `make test-frontend`;"),
            ("ps", "exécuter `make ps` si les services sont démarrés;"),
        )

        for target, description in mapping:
            if target in targets:
                checks.append(description)

        checks.extend(
            [
                "examiner `git status`;",
                "examiner `git diff`;",
                "confirmer qu’aucun fichier secret ou généré localement n’est suivi par Git;",
                "mettre à jour la documentation concernée si le comportement a changé.",
            ]
        )

        return checks

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
    def _code_list(values: list[str]) -> str:
        if not values:
            return "`aucun`"

        return ", ".join(
            f"`{value}`"
            for value in values
        )
