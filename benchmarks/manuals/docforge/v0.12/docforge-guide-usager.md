# Guide utilisateur de docforge

## Présentation

Cette section présente uniquement les faits disponibles et leur contexte.

## Public visé

Cette section présente uniquement les faits disponibles et leur contexte.

## Prérequis

Cette section présente uniquement les faits disponibles et leur contexte.

## Installation

### Commandes d’installation

#### Créer un environnement virtuel

```bash
python -m venv .venv
```

Statut : fait dérivé; formulation prudente.

#### Activer l’environnement

```bash
source .venv/bin/activate
```

Statut : fait dérivé; formulation prudente.

#### Installer le paquet localement

```bash
python -m pip install -e .
```

Statut : fait dérivé; formulation prudente.

#### Installer les dépendances de développement

```bash
python -m pip install -e ".[dev]"
```

Statut : configuration déclarée; ce n’est pas un comportement observé.

#### Vérifier l’installation CLI

```bash
docforge --help
```

Statut : fait dérivé; formulation prudente.

#### Exécuter les tests

```bash
pytest -q
```

Statut : fait dérivé; formulation prudente.

Cette section présente uniquement les faits disponibles et leur contexte.

## Démarrage rapide

### Commandes de démarrage rapide

```bash
docforge analyze
docforge profile
docforge knowledge
docforge document . --refresh --clean
```

Cette section présente uniquement les faits disponibles et leur contexte.

## Concepts essentiels

Cette section présente uniquement les faits disponibles et leur contexte.

## Analyse d’un projet

Cette section présente uniquement les faits disponibles et leur contexte.

## Détection du profil

Cette section présente uniquement les faits disponibles et leur contexte.

## Construction de ProjectKnowledge

Cette section présente uniquement les faits disponibles et leur contexte.

## Génération documentaire

Cette section présente uniquement les faits disponibles et leur contexte.

## Génération avec Ollama

Cette section présente uniquement les faits disponibles et leur contexte.

## Révision des aperçus

Cette section présente uniquement les faits disponibles et leur contexte.

## Application des documents

Cette section présente uniquement les faits disponibles et leur contexte.

## Documents protégés

Cette section présente uniquement les faits disponibles et leur contexte.

## Gestion des projets

Cette section présente uniquement les faits disponibles et leur contexte.

## Audits et conformité

Cette section présente uniquement les faits disponibles et leur contexte.

## Configuration

### Chemins et fichiers de configuration démontrés

- `~/.config/docforge/projects.yml` — Registre des projets connus par docforge.
- `~/.config/docforge/invariant-baseline.json` — Empreintes approuvées des documents d’invariants protégés.
- `.docforge.yml` — Configuration locale du projet pour le profil, la sélection documentaire et les exclusions de scan.
- `.docforge/cache/` — Cache local des faits et de ProjectKnowledge.
- `.docforge/preview/` — Aperçus documentaires générés avant application.
- `reports/` — Rapports durables pouvant être suivis par Git.
- `pyproject.toml` — Métadonnées du paquet, dépendances et point d’entrée CLI.
- `.gitignore` — Exclusions Git, notamment caches, aperçus et environnements virtuels.

Statut : configuration déclarée; ce n’est pas un comportement observé.

Cette section présente uniquement les faits disponibles et leur contexte.

## Sécurité

Cette section présente uniquement les faits disponibles et leur contexte.

## Dépannage

Cette section présente uniquement les faits disponibles et leur contexte.

## Limites des informations disponibles

Cette section présente uniquement les faits disponibles et leur contexte.

## Référence CLI

### Entrées de la référence CLI

#### `analyze`

```bash
docforge analyze
```

- Paramètre positionnel `PATH` (facultatif)
- Groupe d’options `--json` (facultatif)

Statut : fait détecté.

#### `analyze-template`

```bash
docforge analyze-template
```

- Paramètre positionnel `PATH` (requis)
- Groupe d’options `--no-cache` (facultatif)
- Groupe d’options `--json` (facultatif)

Statut : fait détecté.

#### `apply`

```bash
docforge apply
```

- Paramètre positionnel `PATH` (facultatif)
- Paramètre positionnel `DOCUMENTS` (requis)
- Groupe d’options `--owner-approved` (facultatif)
- Groupe d’options `--allow-dirty` (facultatif)

Statut : fait détecté.

#### `approve-invariants`

```bash
docforge approve-invariants
```

- Paramètre positionnel `TEMPLATE_PATH` (requis)
- Groupe d’options `--owner-approved` (facultatif)

Statut : fait détecté.

#### `audit-all`

```bash
docforge audit-all
```

- Groupe d’options `--template` (facultatif)
- Groupe d’options `--show-findings` (facultatif)

Statut : fait détecté.

#### `audit-diff`

```bash
docforge audit-diff
```

- Groupe d’options `--current` (facultatif)
- Groupe d’options `--previous` (facultatif)
- Groupe d’options `--output / -o` (facultatif)

Statut : fait détecté.

#### `audit-report`

```bash
docforge audit-report
```

- Groupe d’options `--template` (facultatif)
- Groupe d’options `--output-dir / -o` (facultatif)

Statut : fait détecté.

#### `document`

```bash
docforge document
```

- Paramètre positionnel `PATH` (facultatif)
- Groupe d’options `--profile / -p` (facultatif)
- Groupe d’options `--clean` (facultatif)
- Groupe d’options `--refresh` (facultatif)
- Groupe d’options `--write` (facultatif)

Statut : fait détecté.

#### `generate`

```bash
docforge generate
```

- Paramètre positionnel `PATH` (facultatif)
- Groupe d’options `--model / -m` (facultatif)
- Groupe d’options `--clean` (facultatif)
- Groupe d’options `--refresh` (facultatif)

Statut : fait détecté.

#### `generate-global-invariants`

```bash
docforge generate-global-invariants
```

- Paramètre positionnel `TEMPLATE_PATH` (requis)
- Groupe d’options `--output / -o` (facultatif)

Statut : fait détecté.

#### `init`

```bash
docforge init
```

- Paramètre positionnel `PATH` (facultatif)
- Groupe d’options `--force` (facultatif)

Statut : fait détecté.

#### `knowledge`

```bash
docforge knowledge
```

- Paramètre positionnel `PATH` (facultatif)
- Groupe d’options `--output / -o` (facultatif)
- Groupe d’options `--json` (facultatif)

Statut : fait détecté.

#### `profile`

```bash
docforge profile
```

- Paramètre positionnel `PATH` (facultatif)

Statut : fait détecté.

#### `refresh-all`

```bash
docforge refresh-all
```

- Groupe d’options `--clean` (facultatif)

Statut : fait détecté.

#### `remediation-plan`

```bash
docforge remediation-plan
```

- Groupe d’options `--template` (facultatif)
- Groupe d’options `--output / -o` (facultatif)

Statut : fait détecté.

#### `status-all`

```bash
docforge status-all
```

- Groupe d’options `--template` (facultatif)
- Groupe d’options `--show-details` (facultatif)

Statut : fait détecté.

#### `verify`

```bash
docforge verify
```

- Paramètre positionnel `PATH` (facultatif)
- Groupe d’options `--profile / -p` (facultatif)

Statut : fait détecté.

#### `verify-invariants`

```bash
docforge verify-invariants
```

- Paramètre positionnel `TEMPLATE_PATH` (requis)

Statut : fait détecté.

#### `manual prepare`

```bash
docforge manual prepare
```

- Paramètre positionnel `PATH` (facultatif)
- Groupe d’options `--clean` (facultatif)
- Groupe d’options `--mode` (facultatif)
- Groupe d’options `--output-dir` (facultatif)
- Groupe d’options `--context-budget` (facultatif)

Statut : fait détecté.

#### `manual validate`

```bash
docforge manual validate
```

- Paramètre positionnel `MARKDOWN_FILE` (requis)
- Groupe d’options `--project-root` (facultatif)
- Groupe d’options `--manual-dir` (facultatif)
- Groupe d’options `--json` (facultatif)
- Groupe d’options `--document-id` (facultatif)

Statut : fait détecté.

#### `projects add`

```bash
docforge projects add
```

- Paramètre positionnel `PATH` (requis)
- Groupe d’options `--name` (facultatif)
- Groupe d’options `--profile / -p` (facultatif)

Statut : fait détecté.

#### `projects list`

```bash
docforge projects list
```


Statut : fait détecté.

#### `projects remove`

```bash
docforge projects remove
```

- Paramètre positionnel `IDENTIFIER` (requis)

Statut : fait détecté.

Cette section présente uniquement les faits disponibles et leur contexte.
