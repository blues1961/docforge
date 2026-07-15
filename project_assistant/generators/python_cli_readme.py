from __future__ import annotations

from project_assistant.knowledge import ProjectKnowledge
from project_assistant.models import Project


class PythonCliReadmeDocumentGenerator:
    def generate(
        self,
        project: Project,
        knowledge: ProjectKnowledge,
    ) -> str:
        identity = knowledge.identity
        pyproject = knowledge.pyproject
        targets = set(knowledge.deployment.make_targets)

        lines = [
            f"# {project.name}",
            "",
            "<!--",
            "Document généré en aperçu par project-assistant.",
            "Le contenu est dérivé de l’état actuel du dépôt.",
            "-->",
            "",
            "## Résumé du projet",
            "",
            (
                f"`{project.name}` est un outil Python en ligne de commande "
                "qui analyse, documente et audite des dépôts logiciels."
            ),
            "",
            (
                "Il construit une représentation structurée des projets, "
                "sélectionne une politique documentaire selon leur profil "
                "et génère les documents dans un aperçu sécurisé avant "
                "toute intégration."
            ),
            "",
            "## Fonctionnalités principales",
            "",
            "- détection des langages, frameworks et technologies;",
            "- détection des profils de projet;",
            "- construction de `ProjectKnowledge`;",
            "- génération documentaire déterministe;",
            "- génération assistée par un LLM local lorsque nécessaire;",
            "- comparaison avec les invariants d’`app-template`;",
            "- audit de conformité multi-projets;",
            "- protection des invariants approuvés;",
            "- génération d’aperçus avant application;",
            "- rapports d’audit et de remédiation.",
            "",
            "## Architecture générale",
            "",
            "Le traitement principal suit ce flux :",
            "",
            "1. scan du système de fichiers;",
            "2. détection des technologies;",
            "3. détection du profil;",
            "4. construction de `ProjectKnowledge`;",
            "5. sélection des documents selon le profil;",
            "6. génération déterministe ou assistée par LLM;",
            "7. écriture dans `.project-assistant/preview`;",
            "8. validation puis application explicite.",
            "",
            "Les détails sont documentés dans "
            "`docs/architecture.md`.",
            "",
            "## Technologies utilisées",
            "",
            f"- Langages : {self._code_list(identity.languages)}.",
            f"- Frameworks détectés : {self._code_list(identity.frameworks)}.",
            f"- Technologies détectées : {self._code_list(identity.technologies)}.",
            f"- Paquet : {self._code_value(pyproject.package_name)}.",
            f"- Version : {self._code_value(pyproject.version)}.",
            f"- Python requis : {self._code_value(pyproject.requires_python)}.",
            f"- Backend de construction : {self._code_value(pyproject.build_backend)}.",
            f"- Dépendances principales : {self._code_list(pyproject.dependencies)}.",
            "- Configuration du paquet : `pyproject.toml`.",
            "",
            "## Installation",
            "",
            "### Prérequis",
            "",
            (
                "- Python "
                + (
                    pyproject.requires_python
                    if pyproject.requires_python
                    else "compatible avec le paquet"
                )
                + ";"
            ),
            "- Git;",
            "- Ollama uniquement pour les générations LLM facultatives.",
            "",
            "### Environnement virtuel",
            "",
            "```bash",
            "python -m venv .venv",
            "source .venv/bin/activate",
            "python -m pip install --upgrade pip",
            'python -m pip install -e ".[dev]"',
            "```",
            "",
            "Vérifier l’installation :",
            "",
            "```bash",
            "docforge --help",
            "pytest -q",
            "```",
            "",
            "## Utilisation",
            "",
            "Analyser un dépôt :",
            "",
            "```bash",
            "docforge analyze /chemin/du/projet",
            "```",
            "",
            "Détecter son profil :",
            "",
            "```bash",
            "docforge profile /chemin/du/projet",
            "```",
            "",
            "Construire sa connaissance structurée :",
            "",
            "```bash",
            "docforge knowledge /chemin/du/projet",
            "```",
            "",
            "Générer la documentation en aperçu :",
            "",
            "```bash",
            "docforge document /chemin/du/projet --refresh --clean",
            "```",
            "",
            "Appliquer un document validé :",
            "",
            "```bash",
            "docforge apply /chemin/du/projet docs/architecture.md",
            "```",
            "",
            "Auditer les projets enregistrés :",
            "",
            "```bash",
            "docforge audit-all --show-findings",
            "```",
            "",
            "## Configuration",
            "",
            "- Registre multi-projets : "
            "`~/.config/project-assistant/projects.yml`.",
            "- Référence des invariants approuvés : "
            "`~/.config/project-assistant/invariant-baseline.json`.",
            "- Cache d’un projet : `.project-assistant/cache/`.",
            "- Aperçus documentaires : `.project-assistant/preview/`.",
            "- Rapports du dépôt : `reports/`.",
            "",
            "Les fichiers de secrets des projets analysés ne doivent "
            "jamais être lus ni reproduits.",
            "",
            "## Commandes CLI déclarées",
            "",
        ]

        if pyproject.scripts:
            for name, target in pyproject.scripts.items():
                lines.append(
                    f"- `{name}` → `{target}`"
                )
        else:
            lines.append(
                "- Aucun point d’entrée CLI déclaré."
            )

        lines.extend(
            [
                "",
                "## Dépendances optionnelles",
                "",
            ]
        )

        if pyproject.optional_dependencies:
            for group, dependencies in (
                pyproject.optional_dependencies.items()
            ):
                lines.append(
                    f"### `{group}`"
                )
                lines.append("")

                for dependency in dependencies:
                    lines.append(f"- `{dependency}`")

                lines.append("")
        else:
            lines.extend(
                [
                    "- Aucun groupe optionnel détecté.",
                    "",
                ]
            )

        lines.extend(
            [
                "## Commandes Makefile détectées",
                "",
            ]
        )

        if targets:
            for target in sorted(targets):
                lines.append(f"- `make {target}`")
        else:
            lines.append(
                "- Aucune cible Makefile significative détectée."
            )

        lines.extend(
            [
                "",
                "## Documentation complémentaire",
                "",
                "- [`README_DEV.md`](README_DEV.md)",
                "- [`AGENTS.md`](AGENTS.md)",
                "- [`CODEX_START.md`](CODEX_START.md)",
                "- [`INVARIANTS.md`](INVARIANTS.md)",
                "- [`docs/architecture.md`](docs/architecture.md)",
                "- [`docs/specification.md`](docs/specification.md)",
                "",
            ]
        )

        return "\n".join(lines)

    @staticmethod
    def _code_value(value: str | None) -> str:
        if not value:
            return "`non défini`"

        return f"`{value}`"

    @staticmethod
    def _code_list(values: list[str]) -> str:
        if not values:
            return "`aucun`"

        return ", ".join(
            f"`{value}`"
            for value in values
        )
