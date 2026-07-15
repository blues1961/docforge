# Configuration — docforge

<!--
Document généré en aperçu par docforge.
Le contenu est dérivé de ConfigurationFacts.
-->

## Vue d’ensemble

`docforge` sépare la configuration utilisateur, l’état local propre à un projet et les rapports pouvant être suivis par Git.

Principales racines :

- configuration utilisateur : `~/.config/docforge/`;
- état local du projet : `.docforge/`;
- rapports du dépôt : `reports/`.

## Fichiers et répertoires

| Chemin | Portée | Présent | Suivi Git possible | Rôle |
|---|---|---:|---:|---|
| `~/.config/docforge/projects.yml` | utilisateur | oui | non | Registre des projets connus par docforge. |
| `~/.config/docforge/invariant-baseline.json` | utilisateur | oui | non | Empreintes approuvées des documents d’invariants protégés. |
| `.docforge/cache/` | projet | oui | non | Cache local des faits et de ProjectKnowledge. |
| `.docforge/preview/` | projet | oui | non | Aperçus documentaires générés avant application. |
| `reports/` | dépôt | oui | oui | Rapports durables pouvant être suivis par Git. |
| `pyproject.toml` | dépôt | oui | oui | Métadonnées du paquet, dépendances et point d’entrée CLI. |
| `.gitignore` | dépôt | oui | oui | Exclusions Git, notamment caches, aperçus et environnements virtuels. |

## Configuration utilisateur

### Registre des projets

Chemin :

```text
~/.config/docforge/projects.yml
```

Ce fichier conserve la liste des projets enregistrés, leur chemin local, leur profil configuré et leur état actif.

Il est modifié par les commandes de gestion du registre.

### Référence des invariants

Chemin :

```text
~/.config/docforge/invariant-baseline.json
```

Ce fichier conserve les empreintes des documents d’invariants explicitement approuvés.

Il ne doit pas être copié dans un dépôt de projet ni utilisé comme substitut à une approbation.

## État local d’un projet

### Cache

```text
.docforge/cache/
```

Le cache peut contenir notamment :

- les faits analysés;
- la représentation `ProjectKnowledge`;
- les résultats intermédiaires déterministes;
- les métadonnées nécessaires aux commandes.

Le cache est reconstructible et ne constitue pas une source d’autorité.

### Aperçus

```text
.docforge/preview/
```

Les documents sont générés dans ce répertoire avant toute application explicite.

Règles :

- un aperçu ne modifie pas le document cible;
- un aperçu peut être supprimé et régénéré;
- un aperçu ne doit pas être suivi par Git;
- un aperçu protégé exige toujours une approbation.

## Rapports

```text
reports/
```

Les rapports durables peuvent être suivis par Git lorsqu’ils représentent un état volontairement conservé du projet.

Exemples :

- rapport d’audit courant;
- comparaison de conformité;
- plan de remédiation;
- résumé d’état multi-projets.

Les rapports temporaires ou contenant des données sensibles ne doivent pas être versionnés.

## Métadonnées du paquet

`pyproject.toml` définit notamment :

- paquet : `docforge`;
- version : `0.1.0`;
- Python requis : `>=3.11`;
- backend de construction : `setuptools.build_meta`;
- points d’entrée : `docforge` → `docforge.cli:app`.

## Variables d’environnement détectées

- Aucune variable d’environnement explicite détectée.

Une variable détectée n’est pas nécessairement obligatoire. Son comportement exact doit être confirmé dans le code qui la lit.

## Exclusions Git attendues

- `.docforge/`
- `.pytest_cache/`
- `.venv/`
- `__pycache__/`

Les exclusions minimales recommandées sont :

```gitignore
.docforge/
.venv/
__pycache__/
*.pyc
.pytest_cache/
```

## Ordre d’autorité

1. les invariants approuvés;
2. la politique du profil détecté;
3. `pyproject.toml` pour les métadonnées du paquet;
4. la configuration utilisateur;
5. les données locales reconstructibles;
6. les valeurs par défaut du programme.

## Règles de portabilité

- ne pas générer de chemin absolu propre à une machine;
- utiliser `Path.home()` pour la configuration utilisateur;
- utiliser des chemins relatifs pour l’état d’un projet;
- ne pas supposer que le dépôt se trouve sous `~/projets`;
- ne pas dépendre du répertoire courant sans le documenter;
- créer les répertoires locaux uniquement au besoin.

## Règles de sécurité

- aucun secret ne doit être stocké dans le registre;
- aucun secret ne doit être écrit dans les aperçus;
- aucun secret ne doit apparaître dans les rapports;
- les caches doivent être considérés comme locaux;
- les documents protégés nécessitent une approbation;
- `.env.local` ne doit pas être analysé pour son contenu.

## Diagnostic

Afficher les projets enregistrés :

```bash
docforge projects list
```

Afficher le profil détecté :

```bash
docforge profile /chemin/du/projet
```

Reconstruire les aperçus :

```bash
docforge document /chemin/du/projet --refresh --clean
```

Vérifier les invariants protégés :

```bash
docforge verify-invariants /chemin/vers/app-template
```

## Critères de validation

- les chemins utilisateur sont résolus avec `Path.home()`;
- les chemins propres au projet restent relatifs;
- les caches et aperçus sont ignorés par Git;
- les fichiers configurés absents sont gérés explicitement;
- aucun secret n’est sérialisé dans `ProjectKnowledge`;
- la documentation correspond aux chemins réellement utilisés.
