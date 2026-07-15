from __future__ import annotations

from docforge.knowledge import ProjectKnowledge
from docforge.models import Project


class PythonCliConfigurationDocumentGenerator:
    def generate(
        self,
        project: Project,
        knowledge: ProjectKnowledge,
    ) -> str:
        facts = knowledge.configuration

        lines = [
            f"# Configuration — {project.name}",
            "",
            "<!--",
            "Document généré en aperçu par docforge.",
            "Le contenu est dérivé de ConfigurationFacts.",
            "-->",
            "",
            "## Vue d’ensemble",
            "",
            (
                "`docforge` sépare la configuration "
                "utilisateur, l’état local propre à un projet "
                "et les rapports pouvant être suivis par Git."
            ),
            "",
            "Principales racines :",
            "",
            (
                f"- configuration utilisateur : "
                f"`{facts.user_config_root}/`;"
            ),
            (
                f"- état local du projet : "
                f"`{facts.project_state_root}/`;"
            ),
            (
                f"- rapports du dépôt : "
                f"`{facts.report_root}/`."
            ),
            "",
            "## Fichiers et répertoires",
            "",
            "| Chemin | Portée | Présent | Suivi Git possible | Rôle |",
            "|---|---|---:|---:|---|",
        ]

        for item in facts.files:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{self._escape(item.path)}`",
                        self._escape(item.scope),
                        "oui" if item.exists else "non",
                        (
                            "oui"
                            if item.tracked_candidate
                            else "non"
                        ),
                        self._escape(item.description),
                    ]
                )
                + " |"
            )

        lines.extend(
            [
                "",
                "## Configuration utilisateur",
                "",
                "### Registre des projets",
                "",
                "Chemin :",
                "",
                "```text",
                "~/.config/project-assistant/projects.yml",
                "```",
                "",
                (
                    "Ce fichier conserve la liste des projets "
                    "enregistrés, leur chemin local, leur profil "
                    "configuré et leur état actif."
                ),
                "",
                "Il est modifié par les commandes de gestion du registre.",
                "",
                "### Référence des invariants",
                "",
                "Chemin :",
                "",
                "```text",
                "~/.config/project-assistant/invariant-baseline.json",
                "```",
                "",
                (
                    "Ce fichier conserve les empreintes des documents "
                    "d’invariants explicitement approuvés."
                ),
                "",
                (
                    "Il ne doit pas être copié dans un dépôt de projet "
                    "ni utilisé comme substitut à une approbation."
                ),
                "",
                "## État local d’un projet",
                "",
                "### Cache",
                "",
                "```text",
                ".project-assistant/cache/",
                "```",
                "",
                "Le cache peut contenir notamment :",
                "",
                "- les faits analysés;",
                "- la représentation `ProjectKnowledge`;",
                "- les résultats intermédiaires déterministes;",
                "- les métadonnées nécessaires aux commandes.",
                "",
                (
                    "Le cache est reconstructible et ne constitue pas "
                    "une source d’autorité."
                ),
                "",
                "### Aperçus",
                "",
                "```text",
                ".project-assistant/preview/",
                "```",
                "",
                (
                    "Les documents sont générés dans ce répertoire avant "
                    "toute application explicite."
                ),
                "",
                "Règles :",
                "",
                "- un aperçu ne modifie pas le document cible;",
                "- un aperçu peut être supprimé et régénéré;",
                "- un aperçu ne doit pas être suivi par Git;",
                "- un aperçu protégé exige toujours une approbation.",
                "",
                "## Rapports",
                "",
                "```text",
                "reports/",
                "```",
                "",
                (
                    "Les rapports durables peuvent être suivis par Git "
                    "lorsqu’ils représentent un état volontairement "
                    "conservé du projet."
                ),
                "",
                "Exemples :",
                "",
                "- rapport d’audit courant;",
                "- comparaison de conformité;",
                "- plan de remédiation;",
                "- résumé d’état multi-projets.",
                "",
                (
                    "Les rapports temporaires ou contenant des données "
                    "sensibles ne doivent pas être versionnés."
                ),
                "",
                "## Métadonnées du paquet",
                "",
                "`pyproject.toml` définit notamment :",
                "",
                f"- paquet : {self._value(knowledge.pyproject.package_name)};",
                f"- version : {self._value(knowledge.pyproject.version)};",
                (
                    f"- Python requis : "
                    f"{self._value(knowledge.pyproject.requires_python)};"
                ),
                (
                    f"- backend de construction : "
                    f"{self._value(knowledge.pyproject.build_backend)};"
                ),
                (
                    f"- points d’entrée : "
                    f"{self._scripts(knowledge.pyproject.scripts)}."
                ),
                "",
                "## Variables d’environnement détectées",
                "",
            ]
        )

        if facts.environment_variables:
            for variable in facts.environment_variables:
                lines.append(f"- `{variable}`")
        else:
            lines.append(
                "- Aucune variable d’environnement explicite détectée."
            )

        lines.extend(
            [
                "",
                (
                    "Une variable détectée n’est pas nécessairement "
                    "obligatoire. Son comportement exact doit être "
                    "confirmé dans le code qui la lit."
                ),
                "",
                "## Exclusions Git attendues",
                "",
            ]
        )

        if facts.ignored_paths:
            for ignored in facts.ignored_paths:
                lines.append(f"- `{ignored}`")
        else:
            lines.append(
                "- Aucune exclusion canonique détectée dans `.gitignore`."
            )

        lines.extend(
            [
                "",
                "Les exclusions minimales recommandées sont :",
                "",
                "```gitignore",
                ".project-assistant/",
                ".venv/",
                "__pycache__/",
                "*.pyc",
                ".pytest_cache/",
                "```",
                "",
                "## Ordre d’autorité",
                "",
                "1. les invariants approuvés;",
                "2. la politique du profil détecté;",
                "3. `pyproject.toml` pour les métadonnées du paquet;",
                "4. la configuration utilisateur;",
                "5. les données locales reconstructibles;",
                "6. les valeurs par défaut du programme.",
                "",
                "## Règles de portabilité",
                "",
                "- ne pas générer de chemin absolu propre à une machine;",
                "- utiliser `Path.home()` pour la configuration utilisateur;",
                "- utiliser des chemins relatifs pour l’état d’un projet;",
                "- ne pas supposer que le dépôt se trouve sous `~/projets`;",
                "- ne pas dépendre du répertoire courant sans le documenter;",
                "- créer les répertoires locaux uniquement au besoin.",
                "",
                "## Règles de sécurité",
                "",
                "- aucun secret ne doit être stocké dans le registre;",
                "- aucun secret ne doit être écrit dans les aperçus;",
                "- aucun secret ne doit apparaître dans les rapports;",
                "- les caches doivent être considérés comme locaux;",
                "- les documents protégés nécessitent une approbation;",
                "- `.env.local` ne doit pas être analysé pour son contenu.",
                "",
                "## Diagnostic",
                "",
                "Afficher les projets enregistrés :",
                "",
                "```bash",
                "docforge projects list",
                "```",
                "",
                "Afficher le profil détecté :",
                "",
                "```bash",
                "docforge profile /chemin/du/projet",
                "```",
                "",
                "Reconstruire les aperçus :",
                "",
                "```bash",
                (
                    "docforge document "
                    "/chemin/du/projet --refresh --clean"
                ),
                "```",
                "",
                "Vérifier les invariants protégés :",
                "",
                "```bash",
                (
                    "docforge verify-invariants "
                    "/chemin/vers/app-template"
                ),
                "```",
                "",
                "## Critères de validation",
                "",
                "- les chemins utilisateur sont résolus avec `Path.home()`;",
                "- les chemins propres au projet restent relatifs;",
                "- les caches et aperçus sont ignorés par Git;",
                "- les fichiers configurés absents sont gérés explicitement;",
                "- aucun secret n’est sérialisé dans `ProjectKnowledge`;",
                "- la documentation correspond aux chemins réellement utilisés.",
                "",
            ]
        )

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _value(value: str | None) -> str:
        return f"`{value}`" if value else "`non défini`"

    @staticmethod
    def _scripts(scripts: dict[str, str]) -> str:
        if not scripts:
            return "`aucun`"

        return ", ".join(
            f"`{name}` → `{target}`"
            for name, target in scripts.items()
        )

    @staticmethod
    def _escape(value: str) -> str:
        return value.replace("|", "\\|").replace(
            "\n",
            " ",
        )
