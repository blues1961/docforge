# CODEX_START.md

<!--
Document généré en aperçu par project-assistant.
Ce fichier fournit le contexte initial aux agents logiciels.
-->

## Mission

Intervenir dans `project-assistant` avec des changements minimaux, testés et conformes aux invariants du dépôt.

`project-assistant` est un outil Python en ligne de commande qui analyse des dépôts, construit `ProjectKnowledge`, détecte leur profil et génère leur documentation en aperçu sécurisé.

## Ordre de lecture

Avant toute modification, lire :

1. `INVARIANTS.md`;
2. `AGENTS.md`;
3. `CODEX_START.md`;
4. `README.md`;
5. `README_DEV.md`;
6. `docs/architecture.md`;
7. `docs/specification.md`;
8. les tests du composant concerné.

## Contexte technique

- Paquet : `project-assistant`.
- Version : `0.1.0`.
- Python requis : `>=3.11`.
- Backend de construction : `setuptools.build_meta`.
- Dépendances : `PyYAML>=6.0`, `requests>=2.31`, `rich>=13.7`, `typer>=0.12`.
- Commandes CLI : `docforge` → `project_assistant.cli:app`.

## Architecture essentielle

Flux principal :

1. `FileSystemScanner` analyse le dépôt;
2. `TechnologyDetector` détecte les technologies;
3. `ProfileDetector` sélectionne un profil;
4. `ProjectKnowledgeBuilder` construit la connaissance;
5. `DocumentationPipeline` choisit le générateur;
6. le document est écrit dans `.project-assistant/preview`;
7. `apply` intègre uniquement les aperçus validés.

Composants principaux :

- `project_assistant/analyzers/` : faits structurés;
- `project_assistant/profiles/` : politiques par famille;
- `project_assistant/generators/` : documents Markdown;
- `project_assistant/commands/` : logique applicative;
- `project_assistant/cli.py` : interface Typer;
- `tests/` : tests unitaires et d’intégration.

## Invariants absolus

- ne jamais lire ou reproduire les secrets des projets analysés;
- ne jamais afficher le contenu de `.env.local`;
- ne jamais appliquer automatiquement un document protégé;
- ne jamais modifier les invariants approuvés sans autorisation;
- ne jamais remplacer un générateur déterministe par un LLM;
- ne jamais inventer des faits absents du dépôt;
- ne jamais écrire dans un document cible pendant l’aperçu;
- ne jamais supprimer ou affaiblir un test pour masquer une erreur;
- ne jamais coder un chemin absolu propre à une machine;
- ne jamais rescanner inutilement un projet déjà modélisé.

## Méthode d’intervention

1. comprendre précisément la demande;
2. identifier les fichiers et tests concernés;
3. vérifier les invariants applicables;
4. effectuer le changement minimal;
5. compiler les fichiers Python modifiés;
6. lancer les tests ciblés;
7. lancer toute la suite `pytest -q`;
8. vérifier `git diff` et `git status`;
9. résumer les changements et les limites.

## Commandes importantes

Installation locale :

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Validation :

```bash
python -m py_compile project_assistant/cli.py
pytest -q
docforge --help
```

Génération documentaire :

```bash
docforge profile /chemin/du/projet
docforge knowledge /chemin/du/projet
docforge document /chemin/du/projet --refresh --clean
```

Audit :

```bash
docforge audit-all --show-findings
docforge status-all
```

## Règles pour les nouveaux profils

Tout profil doit :

- fournir des preuves de détection;
- produire un score de confiance;
- définir sa politique documentaire;
- conserver un profil `generic` comme repli;
- déclarer uniquement des documents supportés par le pipeline;
- inclure des tests de détection et de non-régression.

## Règles pour les générateurs

- utiliser uniquement les faits de `ProjectKnowledge`;
- ordonner les sorties pour garantir leur reproductibilité;
- préserver les sections locales balisées;
- produire un Markdown valide;
- ne pas inclure de secret ou de chemin local absolu;
- conserver la séparation entre aperçu et application;
- tester explicitement les contenus interdits.

## Validation avant de terminer

Confirmer que :

- tous les fichiers Python modifiés compilent;
- tous les tests réussissent;
- les commandes CLI s’importent correctement;
- les profils existants gardent leur comportement;
- aucun secret ou cache n’est suivi par Git;
- aucun invariant protégé n’a été modifié;
- la documentation correspond au code actuel.

## Instructions locales

<!-- project-assistant:local-codex:start -->

_Ajouter ici le contexte de démarrage propre au dépôt._

_Cette section est conservée lors des futures régénérations déterministes._

<!-- project-assistant:local-codex:end -->
