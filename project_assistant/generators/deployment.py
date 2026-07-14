from __future__ import annotations

from project_assistant.analyzers import DeploymentFacts
from project_assistant.models import Project


class DeploymentDocumentGenerator:
    def generate(
        self,
        project: Project,
        facts: DeploymentFacts,
    ) -> str:
        lines = [
            f"# Déploiement — {project.name}",
            "",
            "<!--",
            "Document généré en aperçu par project-assistant.",
            "Le contenu doit être validé avant son intégration.",
            "-->",
            "",
            "## Prérequis",
            "",
        ]

        lines.extend(
            f"- {prerequisite}"
            for prerequisite in facts.prerequisites
            if not prerequisite.startswith("Le lien `.env`")
        )

        lines.extend(
            [
                "- Pour un déploiement de production, le lien `.env` doit pointer vers `.env.prod`.",
                "",
                "## Environnements",
                "",
                "Le projet distingue les environnements de développement et de production.",
                "",
                f"- Environnement actif détecté au moment de l’analyse : `{project.environment.active_environment or 'inconnu'}`.",
                f"- Cible actuelle du lien `.env` : `{project.environment.env_symlink_target or 'absent'}`.",
                "- `make dev` fait pointer `.env` vers `.env.dev`.",
                "- `make prod` fait pointer `.env` vers `.env.prod`.",
                f"- Fichiers Compose : {self._code_list(facts.compose_files)}.",
                f"- Fichiers d’environnement requis : {self._code_list(facts.required_env_files)}.",
                "",
                "## Déploiement",
                "",
                "Les services Docker détectés sont : "
                f"{self._code_list(facts.services)}.",
                "",
                "Sélectionner l’environnement de production :",
                "",
                "```bash",
                "make prod",
                "```",
                "",
                "Démarrer ou reconstruire la stack :",
                "",
                "```bash",
                "make up",
                "```",
                "",
            ]
        )

        if facts.traefik_enabled:
            lines.extend(
                [
                    "Traefik fournit le point d’entrée HTTP/HTTPS en production.",
                    f"Le réseau Docker externe utilisé est {self._code_list(facts.external_networks)}.",
                    "",
                ]
            )

        lines.extend(
            [
                "## Migrations",
                "",
            ]
        )

        if "migrate" in facts.make_targets:
            lines.extend(
                [
                    "Appliquer les migrations Django après le démarrage de la stack :",
                    "",
                    "```bash",
                    "make migrate",
                    "```",
                    "",
                ]
            )
        else:
            lines.extend(["À vérifier.", ""])

        lines.extend(
            [
                "## Retour arrière",
                "",
                "### Restauration de la base de données",
                "",
                "`make restore` est l’alias standard de restauration de la base de données.",
                "",
                "```bash",
                "make restore",
                "```",
                "",
                "Un fichier précis peut être fourni avec `FILE=` :",
                "",
                "```bash",
                "make restore FILE=backup/mdp_db-<timestamp>.sql.gz",
                "```",
                "",
                "La cible `restore-db` accepte également la variable `BACKUP=` et prend le dernier fichier compatible lorsqu’aucun fichier n’est fourni.",
                "",
                "Formats détectés : `.sql.gz`, `.sql` et `.dump`.",
                "",
                "### Restauration des secrets",
                "",
                "`make restore-env` est un alias vers `pull-secret`. Cette commande restaure les secrets d’environnement; elle ne restaure ni le code ni la base de données.",
                "",
                "```bash",
                "make restore-env",
                "```",
                "",
                "## Validation après déploiement",
                "",
                "Vérifier les invariants du projet :",
                "",
                "```bash",
                "make check",
                "```",
                "",
                "Vérifier l’état des conteneurs :",
                "",
                "```bash",
                "make ps",
                "```",
                "",
                "Consulter les journaux si nécessaire :",
                "",
                "```bash",
                "make logs",
                "```",
                "",
            ]
        )

        if "test" in facts.make_targets:
            lines.extend(
                [
                    "Exécuter la suite de tests principale :",
                    "",
                    "```bash",
                    "make test",
                    "```",
                    "",
                ]
            )

        if facts.named_volumes:
            lines.extend(
                [
                    "Volumes nommés détectés : "
                    f"{self._code_list(facts.named_volumes)}.",
                    "",
                ]
            )

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _code_list(values: list[str]) -> str:
        if not values:
            return "`aucun`"

        return ", ".join(f"`{value}`" for value in values)
