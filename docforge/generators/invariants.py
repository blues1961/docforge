from __future__ import annotations

from docforge.knowledge import ProjectKnowledge
from docforge.models import Project


LOCAL_RULES_START = (
    "<!-- project-assistant:local-invariants:start -->"
)
LOCAL_RULES_END = (
    "<!-- project-assistant:local-invariants:end -->"
)

DEVIATIONS_START = (
    "<!-- project-assistant:approved-deviations:start -->"
)
DEVIATIONS_END = (
    "<!-- project-assistant:approved-deviations:end -->"
)


class InvariantsDocumentGenerator:
    def generate(
        self,
        project: Project,
        knowledge: ProjectKnowledge,
        existing_content: str | None = None,
    ) -> str:
        identity = knowledge.identity
        architecture = knowledge.architecture
        deployment = knowledge.deployment

        existing = existing_content or ""

        local_rules = self._extract_section(
            existing,
            LOCAL_RULES_START,
            LOCAL_RULES_END,
        )
        deviations = self._extract_section(
            existing,
            DEVIATIONS_START,
            DEVIATIONS_END,
        )

        services = sorted(
            service.name
            for service in architecture.services
        )
        targets = set(deployment.make_targets)

        lines = [
            "# INVARIANTS.md",
            "",
            "<!--",
            "Document généré en aperçu par docforge.",
            "Ce document local complète les invariants globaux.",
            "Il ne peut pas contredire app-template/INVARIANTS.md.",
            "Son application exige l’autorisation explicite du propriétaire.",
            "-->",
            "",
            "## Autorité",
            "",
            (
                "`app-template/INVARIANTS.md` constitue la source "
                "canonique des invariants globaux des applications "
                "auto-hébergées."
            ),
            "",
            (
                "Le présent document définit uniquement les contraintes "
                f"locales du projet `{project.name}`."
            ),
            "",
            "Ordre d’autorité :",
            "",
            "1. `app-template/INVARIANTS.md`;",
            "2. le présent fichier `INVARIANTS.md`;",
            "3. `CODEX_START.md`;",
            "4. `AGENTS.md`;",
            "5. la documentation technique;",
            "6. le code existant.",
            "",
            (
                "Aucun agent ne doit modifier, supprimer, assouplir ou "
                "contourner un invariant sans autorisation explicite "
                "du propriétaire."
            ),
            "",
            "## Portée",
            "",
            (
                f"Ces invariants locaux s’appliquent à l’ensemble du "
                f"dépôt `{project.name}`, notamment au code, aux fichiers "
                "Docker Compose, aux environnements, aux scripts, à la "
                "documentation et aux interventions automatisées."
            ),
            "",
            "## Identité du projet",
            "",
            f"- Nom détecté : `{identity.name}`.",
            f"- Racine détectée : `{identity.root}`.",
            f"- Langages : {self._code_list(identity.languages)}.",
            f"- Frameworks : {self._code_list(identity.frameworks)}.",
            f"- Technologies : {self._code_list(identity.technologies)}.",
            "",
            (
                "Les valeurs canoniques `APP_NAME`, `APP_SLUG`, "
                "`APP_DEPOT`, `APP_NO` et `APP_ENV` doivent rester "
                "définies dans les fichiers d’environnement appropriés."
            ),
            "",
            "## Invariants d’environnement",
            "",
            "- `.env.dev` contient la configuration non secrète du développement;",
            "- `.env.prod` contient la configuration non secrète de la production;",
            "- `.env.local` contient exclusivement les secrets locaux;",
            "- `.env.local` ne doit jamais être versionné, lu ou affiché par docforge;",
            "- `.env` est un lien symbolique vers `.env.dev` ou `.env.prod`;",
            "- `.env` ne doit jamais être modifié directement;",
            "- les changements d’environnement passent par les scripts ou cibles Makefile prévus.",
            "",
        ]

        if project.environment.env_symlink_exists:
            lines.extend(
                [
                    (
                        f"État actuellement détecté : `.env` → "
                        f"`{project.environment.env_symlink_target}`."
                    ),
                    "",
                ]
            )

        lines.extend(
            [
                "## Invariants de sécurité",
                "",
                "- aucun secret dans Git;",
                "- aucun secret dans les fichiers Markdown;",
                "- aucun secret dans `.env.dev` ou `.env.prod`;",
                "- aucun secret dans les journaux applicatifs ou Docker;",
                "- aucun contenu de `.env.local` ne doit être inclus dans un rapport;",
                "- toute donnée privée doit être isolée selon les règles métier du projet;",
                "- toute route privée doit utiliser le mécanisme d’authentification prévu;",
                "",
                "## Invariants d’architecture",
                "",
                f"- Services Docker détectés : {self._code_list(services)}.",
                f"- Fichiers Compose : {self._code_list(architecture.compose_files)}.",
                f"- Réseaux : {self._code_list(architecture.networks)}.",
                f"- Réseaux externes : {self._code_list(architecture.external_networks)}.",
                f"- Volumes nommés : {self._code_list(architecture.volumes)}.",
                "",
            ]
        )

        if {"backend", "frontend", "db"}.issubset(services):
            lines.extend(
                [
                    "- les services standards restent nommés `backend`, `frontend` et `db`;",
                    "- leur responsabilité doit rester séparée;",
                ]
            )

        if architecture.uses_traefik:
            lines.append(
                "- Traefik demeure le point d’entrée HTTP/HTTPS de production;"
            )

        if "PostgreSQL" in identity.technologies:
            lines.append(
                "- PostgreSQL demeure la base relationnelle canonique;"
            )

        lines.extend(
            [
                "- aucun service, réseau, volume ou port ne doit être inventé;",
                "- toute modification structurelle doit être justifiée et documentée.",
                "",
                "## Invariants Docker Compose",
                "",
                "- utiliser la commande `docker compose`, jamais `docker-compose`;",
                "- conserver des fichiers Compose distincts pour le développement et la production;",
                "- utiliser les fichiers d’environnement prévus par le projet;",
                "- ne pas exposer publiquement un port applicatif sans justification;",
                "- ne pas créer une stack parallèle contournant le Makefile ou les scripts standards.",
                "",
                "## Invariants Makefile et scripts",
                "",
                f"- Cibles Makefile détectées : {self._code_list(sorted(targets))}.",
                "",
                "- les cibles canoniques ne doivent pas être renommées arbitrairement;",
                "- une nouvelle cible ne doit pas dupliquer une cible existante;",
                "- les scripts standards ne doivent pas être remplacés par des variantes parallèles;",
                "- les commandes sensibles doivent échouer explicitement lorsque leur environnement est invalide;",
                "",
                "## Invariants de documentation",
                "",
                "- la documentation doit refléter l’état réel du dépôt;",
                "- les faits techniques déterministes prévalent sur les descriptions inventées;",
                "- les documents générés restent dans `.docforge/preview` jusqu’à validation;",
                "- `docforge apply` ne doit pas intégrer `INVARIANTS.md` sans approbation explicite;",
                "- toute règle locale doit être placée dans la section réservée;",
                "- toute dérogation doit être placée dans la section des dérogations approuvées.",
                "",
                "## Règles locales du projet",
                "",
                LOCAL_RULES_START,
            ]
        )

        if local_rules:
            lines.append(local_rules.rstrip())
        else:
            lines.extend(
                [
                    "",
                    "_Ajouter ici les invariants propres au projet._",
                    "",
                    (
                        "_Ces règles peuvent renforcer les invariants "
                        "globaux, mais jamais les contredire._"
                    ),
                    "",
                ]
            )

        lines.extend(
            [
                LOCAL_RULES_END,
                "",
                "## Dérogations explicitement approuvées",
                "",
                (
                    "Une dérogation n’est valide que si elle a été "
                    "explicitement autorisée par le propriétaire et si elle "
                    "documente sa justification, sa portée, ses risques et "
                    "son plan de suppression ou de migration."
                ),
                "",
                DEVIATIONS_START,
            ]
        )

        if deviations:
            lines.append(deviations.rstrip())
        else:
            lines.extend(
                [
                    "",
                    "_Aucune dérogation approuvée._",
                    "",
                ]
            )

        lines.extend(
            [
                DEVIATIONS_END,
                "",
                "## Validation obligatoire",
                "",
            ]
        )

        validations = self._validation_commands(targets)

        if validations:
            lines.append(
                "Avant toute livraison ou modification structurante :"
            )
            lines.append("")

            for index, command in enumerate(
                validations,
                start=1,
            ):
                lines.append(
                    f"{index}. exécuter `{command}`;"
                )
        else:
            lines.append(
                "Aucune cible standard de validation n’a été détectée."
            )

        lines.extend(
            [
                "",
                "Toujours vérifier :",
                "",
                "- `git status`;",
                "- `git diff`;",
                "- l’absence de secrets;",
                "- la cohérence avec `app-template`;",
                "- la documentation affectée;",
                "- l’approbation explicite de toute évolution d’invariant.",
                "",
                "## Règle finale",
                "",
                (
                    "Le projet doit s’adapter aux invariants. "
                    "Les invariants ne doivent jamais être adaptés "
                    "automatiquement pour justifier le projet."
                ),
                "",
            ]
        )

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _validation_commands(
        targets: set[str],
    ) -> list[str]:
        ordered = (
            "check",
            "test",
            "test-backend",
            "test-frontend",
            "ps",
        )

        return [
            f"make {target}"
            for target in ordered
            if target in targets
        ]

    @staticmethod
    def _extract_section(
        content: str,
        start_marker: str,
        end_marker: str,
    ) -> str:
        if (
            start_marker not in content
            or end_marker not in content
        ):
            return ""

        after_start = content.split(
            start_marker,
            1,
        )[1]

        return after_start.split(
            end_marker,
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
