from __future__ import annotations

from project_assistant.knowledge import ProjectKnowledge
from project_assistant.models import Project


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


class PythonCliInvariantsDocumentGenerator:
    def generate(
        self,
        project: Project,
        knowledge: ProjectKnowledge,
        existing_content: str | None = None,
    ) -> str:
        pyproject = knowledge.pyproject
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

        lines = [
            "# INVARIANTS.md",
            "",
            "<!--",
            "Document généré en aperçu par project-assistant.",
            "Ce document définit les invariants locaux du profil python-cli.",
            "Son application exige l’autorisation explicite du propriétaire.",
            "-->",
            "",
            "## Autorité",
            "",
            (
                "Ce fichier constitue le contrat technique local du dépôt "
                f"`{project.name}`."
            ),
            "",
            (
                "Les invariants globaux approuvés demeurent prioritaires. "
                "Le présent document peut les renforcer, mais jamais les "
                "contredire ou les assouplir."
            ),
            "",
            "Ordre d’autorité :",
            "",
            "1. les invariants globaux approuvés;",
            "2. le présent fichier `INVARIANTS.md`;",
            "3. `CODEX_START.md`;",
            "4. `AGENTS.md`;",
            "5. la documentation technique;",
            "6. le code existant.",
            "",
            (
                "Aucun agent ne doit modifier un invariant sans "
                "autorisation explicite du propriétaire."
            ),
            "",
            "## Identité du paquet",
            "",
            f"- Nom : {self._code_value(pyproject.package_name)}.",
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
                f"- Points d’entrée CLI : "
                f"{self._scripts_list(pyproject.scripts)}."
            ),
            "",
            "Le nom du paquet, sa version, les dépendances et les points "
            "d’entrée doivent être définis dans `pyproject.toml`.",
            "",
            "## Invariants de structure",
            "",
            "La structure canonique du code est :",
            "",
            "```text",
            "project_assistant/",
            "├── analyzers/",
            "├── commands/",
            "├── detectors/",
            "├── generators/",
            "├── profiles/",
            "├── scanners/",
            "├── cli.py",
            "├── documentation_pipeline.py",
            "└── knowledge.py",
            "```",
            "",
            "Règles :",
            "",
            "- les scanners découvrent les fichiers;",
            "- les détecteurs identifient les technologies;",
            "- les analyseurs extraient des faits structurés;",
            "- les profils définissent les politiques par famille de projet;",
            "- `ProjectKnowledge` centralise les faits;",
            "- les générateurs produisent le contenu documentaire;",
            "- les commandes orchestrent les opérations;",
            "- `cli.py` expose uniquement l’interface Typer;",
            "- les tests restent dans `tests/`.",
            "",
            "Une responsabilité ne doit pas être déplacée arbitrairement "
            "vers une couche différente.",
            "",
            "## Invariants de connaissance",
            "",
            "- un dépôt doit être scanné avant toute analyse;",
            "- les technologies doivent être détectées avant le profil;",
            "- le profil doit être déterminé avant la sélection documentaire;",
            "- les faits réutilisables doivent être ajoutés à `ProjectKnowledge`;",
            "- un générateur déterministe ne doit pas rescanner le dépôt;",
            "- les collections sérialisées doivent rester ordonnées;",
            "- le schéma JSON de `ProjectKnowledge` doit rester versionné;",
            "- toute évolution du schéma doit être testée.",
            "",
            "## Invariants des profils",
            "",
            "Chaque profil doit définir :",
            "",
            "- un nom stable;",
            "- un libellé;",
            "- une description;",
            "- une priorité;",
            "- un score de confiance;",
            "- les preuves de détection;",
            "- les documents obligatoires;",
            "- les documents optionnels;",
            "- les documents déterministes;",
            "- les documents protégés.",
            "",
            "Règles :",
            "",
            "- un profil spécialisé doit atteindre le seuil minimal;",
            "- `generic` constitue le profil de secours;",
            "- les preuves de détection doivent être explicites;",
            "- une heuristique ne doit pas être présentée comme une certitude;",
            "- les documents déterministes déclarés doivent être supportés "
            "par `DocumentationPipeline.SUPPORTED_DOCUMENTS`;",
            "- l’ajout d’un profil exige des tests de détection et de "
            "non-régression.",
            "",
            "## Invariants du pipeline documentaire",
            "",
            "- `ProjectKnowledge` est construit avant la génération;",
            "- les documents sont sélectionnés selon la politique du profil;",
            "- les générateurs déterministes sont prioritaires;",
            "- un LLM ne doit jamais remplacer un générateur déterministe;",
            "- les sorties sont écrites dans `.project-assistant/preview`;",
            "- aucun fichier cible n’est modifié pendant l’aperçu;",
            "- l’intégration exige une commande `apply` explicite;",
            "- les sections locales balisées doivent être préservées;",
            "- les sorties doivent être reproductibles à état de dépôt égal.",
            "",
            "## Invariants de protection",
            "",
            "- `INVARIANTS.md` est un document protégé;",
            "- son application exige `--owner-approved`;",
            "- les invariants approuvés doivent être vérifiables par empreinte;",
            "- une modification non approuvée doit être détectée;",
            "- aucune protection ne doit être contournée par une commande parallèle;",
            "- les erreurs de protection doivent être explicites.",
            "",
            "## Invariants de sécurité",
            "",
            "- ne jamais lire le contenu de `.env.local` d’un projet analysé;",
            "- ne jamais reproduire un secret dans un rapport ou un document;",
            "- ne jamais afficher une valeur secrète dans les journaux;",
            "- ne jamais committer un secret, un cache ou un aperçu;",
            "- ne jamais suivre `.project-assistant/` dans Git;",
            "- ne jamais suivre `.venv/` dans Git;",
            "- ne jamais introduire un chemin absolu propre à une machine;",
            "- traiter les fichiers illisibles ou invalides sans divulgation.",
            "",
            "## Invariants des générateurs",
            "",
            "- utiliser uniquement des faits structurés disponibles;",
            "- ne jamais inventer une fonctionnalité ou une technologie;",
            "- ne jamais coder en dur une métadonnée présente dans "
            "`pyproject.toml`;",
            "- produire du Markdown valide;",
            "- conserver un ordre stable;",
            "- préserver les sections locales;",
            "- tester les contenus obligatoires et interdits;",
            "- ne pas inclure de secret ni de chemin local absolu.",
            "",
            "## Invariants des commandes CLI",
            "",
            "- toute nouvelle commande doit apparaître dans `--help`;",
            "- toute commande doit avoir un test minimal;",
            "- les erreurs utilisateur doivent être explicites;",
            "- les opérations destructives ou protégées exigent une option "
            "claire et volontaire;",
            "- une commande ne doit pas dupliquer une logique déjà présente "
            "dans une autre couche;",
            "- les commandes doivent utiliser les gestionnaires et pipelines "
            "existants.",
            "",
            "## Invariants des tests",
            "",
            "- aucun test ne doit être supprimé pour masquer une régression;",
            "- aucune assertion ne doit être affaiblie sans justification;",
            "- chaque analyseur possède des tests de cas nominal et invalide;",
            "- chaque générateur possède des tests de contenu;",
            "- chaque profil possède des tests de détection;",
            "- les documents protégés possèdent des tests d’autorisation;",
            "- toute nouvelle commande possède un test CLI;",
            "- toute modification doit conserver la réussite de la suite complète.",
            "",
            "Commandes minimales :",
            "",
            "```bash",
            "python -m py_compile project_assistant/cli.py",
            "pytest -q",
            "docforge --help",
            "```",
            "",
            "## Invariants Git",
            "",
            "- vérifier `git status` avant et après une intervention;",
            "- examiner `git diff` avant le commit;",
            "- ne pas committer `.venv/`, `.project-assistant/` ou les caches;",
            "- ne pas committer de fichiers de secrets provenant des projets;",
            "- utiliser des commits descriptifs et limités;",
            "- ne pas mélanger une refactorisation indépendante à une correction.",
            "",
            "## Règles locales du projet",
            "",
            LOCAL_RULES_START,
        ]

        if local_rules:
            lines.append(local_rules.rstrip())
        else:
            lines.extend(
                [
                    "",
                    "_Ajouter ici les invariants propres à ce dépôt._",
                    "",
                    (
                        "_Ces règles peuvent renforcer les invariants "
                        "ci-dessus, mais jamais les contredire._"
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
                    "Toute dérogation doit préciser sa justification, "
                    "sa portée, ses risques, les tests associés et son "
                    "plan de suppression ou de migration."
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
                "Avant toute livraison :",
                "",
                "1. compiler les fichiers Python modifiés;",
                "2. exécuter les tests ciblés;",
                "3. exécuter `pytest -q`;",
                "4. vérifier `docforge --help`;",
                "5. examiner `git diff`;",
                "6. examiner `git status`;",
                "7. confirmer l’absence de secret et de cache;",
                "8. confirmer que les invariants protégés sont intacts;",
                "9. confirmer que les profils existants restent fonctionnels;",
                "10. régénérer la documentation affectée.",
                "",
                "## Règle finale",
                "",
                (
                    "Le code, les profils et les générateurs doivent "
                    "s’adapter aux invariants. Les invariants ne doivent "
                    "jamais être adaptés automatiquement pour justifier "
                    "l’état actuel du dépôt."
                ),
                "",
            ]
        )

        return "\n".join(lines).rstrip() + "\n"

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
    def _code_value(value: str | None) -> str:
        if not value:
            return "`non défini`"

        return f"`{value}`"

    @staticmethod
    def _scripts_list(scripts: dict[str, str]) -> str:
        if not scripts:
            return "`aucun`"

        return ", ".join(
            f"`{name}` → `{target}`"
            for name, target in scripts.items()
        )
