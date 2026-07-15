# project-assistant

<!--
Document généré en aperçu par project-assistant.
Le contenu est dérivé de l’état actuel du dépôt.
-->

## Résumé du projet

`project-assistant` est un outil Python en ligne de commande qui analyse, documente et audite des dépôts logiciels.

Il construit une représentation structurée des projets, sélectionne une politique documentaire selon leur profil et génère les documents dans un aperçu sécurisé avant toute intégration.

## Fonctionnalités principales

- détection des langages, frameworks et technologies;
- détection des profils de projet;
- construction de `ProjectKnowledge`;
- génération documentaire déterministe;
- génération assistée par un LLM local lorsque nécessaire;
- comparaison avec les invariants d’`app-template`;
- audit de conformité multi-projets;
- protection des invariants approuvés;
- génération d’aperçus avant application;
- rapports d’audit et de remédiation.

## Architecture générale

Le traitement principal suit ce flux :

1. scan du système de fichiers;
2. détection des technologies;
3. détection du profil;
4. construction de `ProjectKnowledge`;
5. sélection des documents selon le profil;
6. génération déterministe ou assistée par LLM;
7. écriture dans `.project-assistant/preview`;
8. validation puis application explicite.

Les détails sont documentés dans `docs/architecture.md`.

## Technologies utilisées

- Langages : `JSON`, `Markdown`, `Python`, `YAML`.
- Frameworks détectés : `aucun`.
- Technologies détectées : `aucun`.
- Paquet : `project-assistant`.
- Version : `0.1.0`.
- Python requis : `>=3.11`.
- Backend de construction : `setuptools.build_meta`.
- Dépendances principales : `PyYAML>=6.0`, `requests>=2.31`, `rich>=13.7`, `typer>=0.12`.
- Configuration du paquet : `pyproject.toml`.

## Installation

### Prérequis

- Python >=3.11;
- Git;
- Ollama uniquement pour les générations LLM facultatives.

### Environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Vérifier l’installation :

```bash
docforge --help
pytest -q
```

## Utilisation

Analyser un dépôt :

```bash
docforge analyze /chemin/du/projet
```

Détecter son profil :

```bash
docforge profile /chemin/du/projet
```

Construire sa connaissance structurée :

```bash
docforge knowledge /chemin/du/projet
```

Générer la documentation en aperçu :

```bash
docforge document /chemin/du/projet --refresh --clean
```

Appliquer un document validé :

```bash
docforge apply /chemin/du/projet docs/architecture.md
```

Auditer les projets enregistrés :

```bash
docforge audit-all --show-findings
```

## Configuration

- Registre multi-projets : `~/.config/project-assistant/projects.yml`.
- Référence des invariants approuvés : `~/.config/project-assistant/invariant-baseline.json`.
- Cache d’un projet : `.project-assistant/cache/`.
- Aperçus documentaires : `.project-assistant/preview/`.
- Rapports du dépôt : `reports/`.

Les fichiers de secrets des projets analysés ne doivent jamais être lus ni reproduits.

## Commandes CLI déclarées

- `docforge` → `project_assistant.cli:app`

## Dépendances optionnelles

### `dev`

- `pytest>=8.0`

## Commandes Makefile détectées

- Aucune cible Makefile significative détectée.

## Documentation complémentaire

- [`README_DEV.md`](README_DEV.md)
- [`AGENTS.md`](AGENTS.md)
- [`CODEX_START.md`](CODEX_START.md)
- [`INVARIANTS.md`](INVARIANTS.md)
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/specification.md`](docs/specification.md)
