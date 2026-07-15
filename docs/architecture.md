# Architecture — project-assistant

<!--
Document généré en aperçu par project-assistant.
Le contenu est dérivé de ProjectKnowledge.
-->

## Vue d’ensemble

`project-assistant` est un outil Python en ligne de commande qui analyse des dépôts logiciels, construit une connaissance structurée, sélectionne un profil documentaire et génère des aperçus validables.

- Profil détecté : `python-cli`.
- Paquet : `project-assistant`.
- Version : `0.1.0`.
- Python requis : `>=3.11`.
- Dépendances principales : `PyYAML>=6.0`, `requests>=2.31`, `rich>=13.7`, `typer>=0.12`.
- Points d’entrée CLI : `docforge` → `project_assistant.cli:app`.

## Architecture logique

```text
Commande CLI
    │
    ▼
FileSystemScanner
    │
    ▼
TechnologyDetector
    │
    ▼
ProfileDetector
    │
    ▼
ProjectKnowledgeBuilder
    │
    ▼
DocumentationPipeline
    │
    ├── Générateur déterministe
    └── Générateur LLM optionnel
             │
             ▼
.project-assistant/preview
             │
             ▼
Application explicite
```

## Couches du système

### Scanner

`FileSystemScanner` découvre les fichiers, dossiers, extensions et structures utiles du dépôt.

Il ne doit pas interpréter la signification métier des fichiers.

### Détecteurs

Les détecteurs identifient les langages, frameworks et technologies à partir de preuves présentes dans le dépôt.

Les détections restent distinctes des règles propres aux profils.

### Analyseurs

Les analyseurs transforment les fichiers du projet en faits structurés et sérialisables.

Exemples :

- architecture Docker et services;
- routes API;
- cibles Makefile;
- configuration de déploiement;
- métadonnées de `pyproject.toml`;
- spécification fonctionnelle détectée.

### Profils

`ProfileDetector` sélectionne une famille de projet à partir d’un score de confiance et de preuves explicites.

Profils actuellement structurants :

- `django-react` : application auto-hébergée;
- `python-cli` : outil Python en ligne de commande;
- `generic` : profil de secours.

Chaque profil définit une politique documentaire :

- documents obligatoires : `README.md`, `README_DEV.md`, `CODEX_START.md`, `AGENTS.md`, `INVARIANTS.md`, `docs/architecture.md`, `docs/cli.md`, `docs/specification.md`, `docs/configuration.md`, `docs/security.md`;
- documents optionnels : `docs/roadmap.md`, `docs/workflows.md`;
- documents déterministes : `README.md`, `README_DEV.md`, `CODEX_START.md`, `AGENTS.md`, `INVARIANTS.md`, `docs/architecture.md`, `docs/cli.md`, `docs/configuration.md`, `docs/specification.md`, `docs/security.md`;
- documents protégés : `INVARIANTS.md`.

### ProjectKnowledge

`ProjectKnowledge` constitue la source de vérité structurée utilisée par les générateurs.

Il agrège notamment :

- l’identité du projet;
- le profil sélectionné;
- l’architecture détectée;
- les faits de déploiement;
- les métadonnées Python;
- les routes API;
- la spécification;
- les faits nécessaires aux README;
- les constats issus du scan.

Les générateurs ne doivent pas rescanner directement le dépôt lorsqu’un fait existe déjà dans `ProjectKnowledge`.

### Pipeline documentaire

`DocumentationPipeline` associe chaque document déterministe à son générateur.

Le pipeline :

1. reçoit un `ProjectKnowledge` déjà construit;
2. sélectionne le générateur selon le profil;
3. produit le contenu Markdown;
4. retourne le contenu et l’identité du générateur;
5. ne modifie pas directement le document cible.

### Commandes

Le dossier `project_assistant/commands/` contient les opérations réutilisables appelées par l’interface CLI.

`cli.py` doit rester une couche d’exposition Typer et ne doit pas accumuler toute la logique métier.

## Flux de génération documentaire

```text
Dépôt source
    │
    ▼
Scan et détection
    │
    ▼
ProjectKnowledge
    │
    ▼
Politique du profil
    │
    ▼
Générateur déterministe
    │
    ▼
Aperçu sécurisé
    │
    ▼
Diff et validation humaine
    │
    ▼
docforge apply
```

## Génération déterministe et LLM

La génération déterministe est prioritaire lorsqu’un générateur structuré existe.

Un LLM local peut compléter des documents non déterministes, mais il ne doit pas remplacer une génération fondée sur des faits structurés.

Conséquences :

- une sortie déterministe est reproductible;
- les faits techniques ne sont pas inventés;
- les tests peuvent valider précisément le contenu;
- les documents sensibles restent contrôlés.

## Aperçu et application

Les documents générés sont écrits dans :

```text
.project-assistant/preview/
```

La génération ne doit jamais modifier automatiquement les documents suivis par Git.

L’intégration se fait par une commande explicite :

```bash
docforge apply /chemin/du/projet <document>
```

## Protection des invariants

`INVARIANTS.md` est un document protégé.

Son application exige :

```bash
docforge apply \
  /chemin/du/projet \
  INVARIANTS.md \
  --owner-approved
```

Les versions approuvées des invariants peuvent également être enregistrées et vérifiées par empreinte.

## Persistance locale

### Configuration utilisateur

```text
~/.config/project-assistant/
├── projects.yml
└── invariant-baseline.json
```

### Données propres à un projet

```text
.project-assistant/
├── cache/
└── preview/
```

### Rapports

Les rapports durables peuvent être enregistrés dans `reports/` lorsqu’ils doivent être suivis par Git.

## Sécurité

Principes architecturaux :

- ne jamais reproduire les secrets des projets analysés;
- ne jamais lire `.env.local` pour documenter son contenu;
- ne pas suivre les caches et aperçus dans Git;
- refuser l’application non autorisée d’un document protégé;
- éviter les chemins absolus propres à une machine;
- conserver des messages d’erreur explicites;
- ne pas masquer les échecs d’analyse ou de test.

## Extensibilité

### Ajouter un analyseur

1. définir une dataclass de faits;
2. lire uniquement les fichiers nécessaires;
3. gérer les fichiers absents ou invalides;
4. ajouter les faits à `ProjectKnowledge` si réutilisables;
5. ajouter les tests.

### Ajouter un profil

1. dériver de `ProjectProfile`;
2. définir confiance et preuves;
3. définir la politique documentaire;
4. enregistrer le profil dans `ProfileDetector`;
5. ajouter les tests de détection et de non-régression.

### Ajouter un générateur

1. utiliser les faits de `ProjectKnowledge`;
2. produire une sortie stable;
3. exporter le générateur;
4. l’enregistrer dans `DocumentationPipeline`;
5. ajouter le document à la politique du profil correspondant;
6. ajouter les tests de contenu.

## Limites actuelles

- certains documents techniques restent encore génériques;
- la liste des commandes CLI n’est pas encore documentée dans un document dédié;
- les profils Hugo et conception 3D ne sont pas encore implémentés;
- la compatibilité des anciens caches doit être formalisée;
- `cli.py` devra progressivement être allégé.

## Décisions d’architecture

- `ProjectKnowledge` est la source de vérité des générateurs;
- les profils contrôlent la politique documentaire;
- la génération déterministe est prioritaire;
- l’aperçu est séparé de l’application;
- les invariants peuvent être protégés par approbation;
- les sections locales balisées sont préservées;
- les tests constituent une partie obligatoire de chaque extension.
