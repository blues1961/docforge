from __future__ import annotations

from docforge.knowledge import ProjectKnowledge
from docforge.models import Project


LOCAL_SECTION_START = "<!-- project-assistant:local-codex:start -->"
LOCAL_SECTION_END = "<!-- project-assistant:local-codex:end -->"


class PythonCliCodexStartDocumentGenerator:
    def generate(
        self,
        project: Project,
        knowledge: ProjectKnowledge,
        existing_content: str | None = None,
    ) -> str:
        pyproject = knowledge.pyproject
        local_content = self._extract_local_section(
            existing_content or ""
        )

        lines = [
            "# CODEX_START.md",
            "",
            "<!--",
            "Document généré en aperçu par docforge.",
            "Ce fichier fournit le contexte initial aux agents logiciels.",
            "-->",
            "",
            "## Mission",
            "",
            (
                f"Intervenir dans `{project.name}` avec des changements "
                "minimaux, testés et conformes aux invariants du dépôt."
            ),
            "",
            (
                "`docforge` est un outil Python en ligne de commande "
                "qui analyse des dépôts, construit `ProjectKnowledge`, détecte "
                "leur profil et génère leur documentation en aperçu sécurisé."
            ),
            "",
            "## Ordre de lecture",
            "",
            "Avant toute modification, lire :",
            "",
            "1. `INVARIANTS.md`;",
            "2. `AGENTS.md`;",
            "3. `CODEX_START.md`;",
            "4. `README.md`;",
            "5. `README_DEV.md`;",
            "6. `docs/architecture.md`;",
            "7. `docs/specification.md`;",
            "8. les tests du composant concerné.",
            "",
            "## Contexte technique",
            "",
            f"- Paquet : {self._code_value(pyproject.package_name)}.",
            f"- Version : {self._code_value(pyproject.version)}.",
            (
                f"- Python requis : "
                f"{self._code_value(pyproject.requires_python)}."
            ),
            (
                f"- Backend de construction : "
                f"{self._code_value(pyproject.build_backend)}."
            ),
            (
                f"- Dépendances : "
                f"{self._code_list(pyproject.dependencies)}."
            ),
            (
                f"- Commandes CLI : "
                f"{self._scripts_list(pyproject.scripts)}."
            ),
            "",
            "## Architecture essentielle",
            "",
            "Flux principal :",
            "",
            "1. `FileSystemScanner` analyse le dépôt;",
            "2. `TechnologyDetector` détecte les technologies;",
            "3. `ProfileDetector` sélectionne un profil;",
            "4. `ProjectKnowledgeBuilder` construit la connaissance;",
            "5. `DocumentationPipeline` choisit le générateur;",
            "6. le document est écrit dans `.docforge/preview`;",
            "7. `apply` intègre uniquement les aperçus validés.",
            "",
            "Composants principaux :",
            "",
            "- `docforge/analyzers/` : faits structurés;",
            "- `docforge/profiles/` : politiques par famille;",
            "- `docforge/generators/` : documents Markdown;",
            "- `docforge/commands/` : logique applicative;",
            "- `docforge/cli.py` : interface Typer;",
            "- `tests/` : tests unitaires et d’intégration.",
            "",
            "## Invariants absolus",
            "",
            "- ne jamais lire ou reproduire les secrets des projets analysés;",
            "- ne jamais afficher le contenu de `.env.local`;",
            "- ne jamais appliquer automatiquement un document protégé;",
            "- ne jamais modifier les invariants approuvés sans autorisation;",
            "- ne jamais remplacer un générateur déterministe par un LLM;",
            "- ne jamais inventer des faits absents du dépôt;",
            "- ne jamais écrire dans un document cible pendant l’aperçu;",
            "- ne jamais supprimer ou affaiblir un test pour masquer une erreur;",
            "- ne jamais coder un chemin absolu propre à une machine;",
            "- ne jamais rescanner inutilement un projet déjà modélisé.",
            "",
            "## Méthode d’intervention",
            "",
            "1. comprendre précisément la demande;",
            "2. identifier les fichiers et tests concernés;",
            "3. vérifier les invariants applicables;",
            "4. effectuer le changement minimal;",
            "5. compiler les fichiers Python modifiés;",
            "6. lancer les tests ciblés;",
            "7. lancer toute la suite `pytest -q`;",
            "8. vérifier `git diff` et `git status`;",
            "9. résumer les changements et les limites.",
            "",
            "## Commandes importantes",
            "",
            "Installation locale :",
            "",
            "```bash",
            "python -m venv .venv",
            "source .venv/bin/activate",
            "python -m pip install -e \".[dev]\"",
            "```",
            "",
            "Validation :",
            "",
            "```bash",
            "python -m py_compile docforge/cli.py",
            "pytest -q",
            "docforge --help",
            "```",
            "",
            "Génération documentaire :",
            "",
            "```bash",
            "docforge profile /chemin/du/projet",
            "docforge knowledge /chemin/du/projet",
            "docforge document /chemin/du/projet --refresh --clean",
            "```",
            "",
            "Audit :",
            "",
            "```bash",
            "docforge audit-all --show-findings",
            "docforge status-all",
            "```",
            "",
            "## Règles pour les nouveaux profils",
            "",
            "Tout profil doit :",
            "",
            "- fournir des preuves de détection;",
            "- produire un score de confiance;",
            "- définir sa politique documentaire;",
            "- conserver un profil `generic` comme repli;",
            "- déclarer uniquement des documents supportés par le pipeline;",
            "- inclure des tests de détection et de non-régression.",
            "",
            "## Règles pour les générateurs",
            "",
            "- utiliser uniquement les faits de `ProjectKnowledge`;",
            "- ordonner les sorties pour garantir leur reproductibilité;",
            "- préserver les sections locales balisées;",
            "- produire un Markdown valide;",
            "- ne pas inclure de secret ou de chemin local absolu;",
            "- conserver la séparation entre aperçu et application;",
            "- tester explicitement les contenus interdits.",
            "",
            "## Validation avant de terminer",
            "",
            "Confirmer que :",
            "",
            "- tous les fichiers Python modifiés compilent;",
            "- tous les tests réussissent;",
            "- les commandes CLI s’importent correctement;",
            "- les profils existants gardent leur comportement;",
            "- aucun secret ou cache n’est suivi par Git;",
            "- aucun invariant protégé n’a été modifié;",
            "- la documentation correspond au code actuel.",
            "",
            "## Instructions locales",
            "",
            LOCAL_SECTION_START,
        ]

        if local_content:
            lines.append(local_content.rstrip())
        else:
            lines.extend(
                [
                    "",
                    "_Ajouter ici le contexte de démarrage propre au dépôt._",
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

    @staticmethod
    def _scripts_list(scripts: dict[str, str]) -> str:
        if not scripts:
            return "`aucune`"

        return ", ".join(
            f"`{name}` → `{target}`"
            for name, target in scripts.items()
        )
