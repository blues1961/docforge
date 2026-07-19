# Guide utilisateur de docforge

**Version du projet :** 0.1.0
**Profil :** Outil Python CLI
**Version Python requise :** Python 3.11 ou version ultérieure

## Présentation

`docforge` est un assistant local d’analyse et de documentation de projets logiciels. Le projet est exposé sous la forme d’une application Python en ligne de commande, avec le point d’entrée `docforge` associé à `docforge.cli:app`.

Le profil détecté est `python-cli`, avec un niveau de confiance de 95 %. Cette détection repose sur la présence de `pyproject.toml`, d’un point d’entrée CLI dans ce fichier, de code Python et d’une suite de tests dans `tests/`.

## Public visé

Ce guide s’adresse principalement aux personnes qui travaillent localement sur des dépôts logiciels et souhaitent :

- analyser un projet sans modifier ses fichiers ;
- détecter son profil documentaire ;
- construire une représentation structurée de ses faits ;
- générer et réviser des aperçus documentaires ;
- appliquer explicitement des documents validés ;
- enregistrer et suivre plusieurs projets ;
- comparer des projets à un modèle canonique et produire des rapports de conformité.

Certaines commandes concernent des opérations spécialisées sur un dépôt `app-template`, les invariants globaux ou la préparation de manuels. Elles sont documentées dans la référence CLI, mais ne constituent pas nécessairement le parcours d’usage courant d’un projet ordinaire.

## Prérequis

Les prérequis fournis pour une utilisation locale sont :

- Python 3.11 ou une version ultérieure ;
- Git ;
- un shell compatible POSIX.

La configuration documentaire prévoit également les emplacements suivants :

- `~/.config/docforge` pour l’état utilisateur ;
- `.docforge` pour l’état local au projet ;
- `.docforge.yml` pour la configuration locale du projet ;
- `reports` pour les rapports durables.

Aucune variable d’environnement requise n’est documentée dans les faits fournis.

## Installation

La procédure préparée décrit une installation locale depuis une copie du dépôt. Elle est déduite de la configuration du projet ; les faits fournis ne constituent pas un compte rendu d’exécution de cette procédure.

1. Créer un environnement virtuel :

   ```sh
   python -m venv .venv
   ```

2. Activer l’environnement :

   ```sh
   source .venv/bin/activate
   ```

3. Installer le paquet localement :

   ```sh
   python -m pip install -e .
   ```

4. Installer les dépendances de développement lorsque les tests ou les outils de développement sont nécessaires :

   ```sh
   python -m pip install -e ".[dev]"
   ```

5. Vérifier que le point d’entrée CLI est disponible :

   ```sh
   docforge --help
   ```

6. Exécuter la suite de tests :

   ```sh
   pytest -q
   ```

## Démarrage rapide

Après l’installation locale, la séquence minimale fournie pour vérifier l’outil est :

```sh
docforge --help
pytest -q
```

Le contexte de démarrage rapide ne fournit pas de workflow fonctionnel supplémentaire ni de point de service à tester. Les opérations d’analyse et de documentation sont détaillées dans les sections suivantes.

## Concepts essentiels

### Analyse locale

`docforge` est présenté comme un assistant local. La commande `docforge analyze` inspecte un projet sans modifier ses fichiers. Le contrôle de sécurité associé précise que les analyseurs doivent éviter d’importer ou d’exécuter le code des projets inspectés ; l’analyse AST du CLI est citée comme élément de preuve.

### Profil documentaire

Un profil décrit le type de projet et la politique documentaire applicable. Pour le projet analysé, le profil détecté est `python-cli`. La commande `docforge profile` affiche le profil déterminé pour un projet.

### Connaissance structurée

La commande `docforge knowledge` construit une représentation factuelle structurée du dépôt. Par défaut, le fichier JSON de destination indiqué est `.docforge/cache/project-knowledge.json`, sauf utilisation de `--output` ou affichage direct avec `--json`.

### Politique documentaire configurée

Le profil configure les documents obligatoires suivants :

- `README.md` ;
- `README_DEV.md` ;
- `CODEX_START.md` ;
- `AGENTS.md` ;
- `INVARIANTS.md` ;
- `docs/architecture.md` ;
- `docs/cli.md` ;
- `docs/specification.md` ;
- `docs/configuration.md` ;
- `docs/security.md`.

Les documents facultatifs configurés sont `docs/roadmap.md` et `docs/workflows.md`.

Les documents obligatoires listés ci-dessus sont également configurés comme documents déterministes. Cette liste est une règle du profil documentaire ; elle ne constitue pas une preuve que chaque document existe déjà dans un projet donné.

### Aperçu puis application explicite

Le flux documentaire distingue la génération d’un aperçu et son application au projet :

- les aperçus sont écrits dans `.docforge/preview/` ;
- un document généré ne doit être appliqué qu’après une commande explicite ;
- `INVARIANTS.md` est un document protégé et exige une autorisation explicite du propriétaire lors de son application.

### Secrets, portabilité et suivi Git

Les contrôles fournis imposent de ne jamais lire, reproduire ou sérialiser le contenu des fichiers de secrets. `.env.local` est cité comme exclu des analyses documentaires. Les documents générés ne doivent pas contenir de chemin absolu propre à une machine.

La configuration prévoit que `.docforge/`, `.pytest_cache/`, `.venv/` et `__pycache__/` soient ignorés. Les caches, aperçus, environnements virtuels et secrets ne doivent pas être suivis par Git.

## Analyse d’un projet

Le workflow d’analyse inspecte un dépôt sans modifier ses fichiers.

```sh
docforge analyze
```

Pour désigner explicitement un projet ou obtenir la représentation complète en JSON :

```text
docforge analyze [PATH] [--json]
```

- `PATH` est facultatif et désigne le projet à analyser.
- `--json` affiche le résultat complet en JSON.

Les faits fournis marquent ce workflow comme opérationnel, mais sa traçabilité globale est dérivée ; ce guide ne le présente donc pas comme un test d’exécution réalisé dans l’environnement du lecteur.

## Détection du profil

La commande suivante détecte et affiche le profil d’un projet :

```text
docforge profile [PATH]
```

`PATH` est facultatif et désigne le projet dont le profil doit être détecté.

Pour le projet décrit par ce manuel, le résultat préparé est le profil `python-cli`, libellé « Outil Python CLI », avec un niveau de confiance de 95 %. Les indices détectés sont `pyproject.toml`, le point d’entrée CLI, le langage Python et le dossier de tests.

La source ne décrit pas l’algorithme complet de classement, les autres profils possibles ni les seuils de confiance.

## Construction de ProjectKnowledge

Le workflow préparé utilise la commande suivante pour produire la représentation factuelle structurée du dépôt :

```sh
docforge knowledge
```

Sa syntaxe détectée est :

```text
docforge knowledge [PATH] [--output] [--json]
```

- `PATH` désigne facultativement le projet à analyser.
- `--output` choisit le fichier JSON de destination. La destination par défaut indiquée est `.docforge/cache/project-knowledge.json`.
- `--json` écrit le JSON pur sur la sortie standard.

Cette connaissance structurée alimente les opérations documentaires. Les faits fournis ne décrivent pas le schéma complet de ProjectKnowledge ni l’ensemble de ses champs.

## Génération documentaire

Le workflow démontré génère un aperçu déterministe sans modifier directement les documents réels :

```sh
docforge document . --refresh --clean
```

Dans cette commande :

- `.` désigne le projet courant ;
- `--clean` supprime l’ancien aperçu avant la génération ;
- `--refresh` régénère les documents déterministes même s’ils existent déjà dans le projet.

L’aperçu est associé au répertoire `.docforge/preview/`. La configuration du profil détermine les documents obligatoires, facultatifs, déterministes et protégés.

La commande `docforge document` expose aussi `--profile` pour sélectionner explicitement un profil documentaire et `--write` pour écrire dans le projet réel. Aucun workflow fourni n’utilise `--write`, et les faits disponibles ne détaillent pas son interaction exacte avec le contrôle « aperçu puis application explicite ». Le parcours démontré dans ce guide reste donc la génération en aperçu, suivie d’une révision puis de `docforge apply`.

## Génération avec Ollama

Le flux dédié aux documents manquants via Ollama utilise :

```sh
docforge generate . --refresh --clean
```

La commande `docforge generate` remplit avec Ollama les documents manquants dans l’aperçu. Elle accepte également `--model` pour désigner le modèle utilisé.

Ce flux est distinct de `docforge manual prepare`, qui prépare les entrées déterministes d’un manuel utilisateur.

Les informations suivantes ne sont pas fournies :

- la procédure d’installation ou de démarrage d’Ollama ;
- le modèle utilisé par défaut ;
- les modèles acceptés ;
- une URL ou un point de service ;
- une variable d’environnement de connexion ;
- le comportement détaillé en cas d’indisponibilité d’Ollama.

Aucune de ces informations ne doit être déduite du seul nom de la commande.

## Révision des aperçus

La révision intervient avant toute application au projet. Le workflow fourni associe les commandes suivantes :

```sh
docforge document . --refresh --clean
git diff -- . ':(exclude).docforge'
```

La première commande recrée l’aperçu déterministe. La seconde affiche les différences Git en excluant `.docforge`.

Les aperçus eux-mêmes se trouvent dans `.docforge/preview/` selon la configuration fournie. Le contexte ne fournit pas de commande dédiée pour afficher leur contenu ou comparer directement chaque aperçu à son document cible. La révision humaine attendue consiste donc à contrôler les fichiers générés avant toute application, sans inventer un outil de comparaison supplémentaire.

Pendant cette révision :

- aucun secret ne doit être reproduit dans un document, un rapport ou un journal ;
- aucun chemin absolu propre à une machine ne doit être introduit ;
- `INVARIANTS.md` doit être traité comme un document protégé ;
- les caches et aperçus ne doivent pas être ajoutés au suivi Git.

## Application des documents

L’application copie explicitement des documents validés depuis l’aperçu vers le projet.

Pour un document non protégé, le workflow fourni donne l’exemple suivant :

```sh
docforge apply . README.md
```

Pour le document protégé `INVARIANTS.md`, une autorisation explicite du propriétaire est requise :

```sh
docforge apply . INVARIANTS.md --owner-approved
```

La syntaxe détectée est :

```text
docforge apply [PATH] DOCUMENTS [--owner-approved] [--allow-dirty]
```

- `PATH` désigne facultativement le projet.
- `DOCUMENTS` est requis et désigne les documents d’aperçu à intégrer.
- `--owner-approved` confirme l’autorisation explicite du propriétaire pour un document protégé.
- `--allow-dirty` autorise exceptionnellement un dépôt Git modifié.

L’option `--allow-dirty` est décrite comme exceptionnelle. Les faits fournis ne détaillent pas le message d’erreur ni le contrôle exact appliqué lorsqu’un dépôt est modifié et que cette option n’est pas présente.

## Documents protégés

Le seul document protégé configuré est :

```text
INVARIANTS.md
```

Son application exige `--owner-approved` :

```sh
docforge apply . INVARIANTS.md --owner-approved
```

Le contrôle d’intégrité prévoit également la vérification par empreinte des invariants approuvés. La configuration utilisateur indique le fichier `~/.config/docforge/invariant-baseline.json` comme emplacement des empreintes approuvées.

La CLI expose des commandes spécialisées liées aux invariants :

- `docforge generate-global-invariants` génère les invariants globaux depuis un dépôt `app-template` ;
- `docforge approve-invariants` enregistre la version approuvée des invariants globaux et expose `--owner-approved` ;
- `docforge verify-invariants` vérifie que les invariants correspondent à la version approuvée.

Aucun workflow complet d’administration des invariants n’est fourni au-delà de ces descriptions. Ce guide ne suppose donc pas un ordre d’exécution supplémentaire.

## Gestion des projets

Le registre utilisateur permet d’enregistrer, de lister et de retirer plusieurs projets.

Le workflow fourni est :

```sh
docforge projects add .
docforge projects list
docforge projects remove demo
```

- `docforge projects add` ajoute ou met à jour un projet dans le registre. Il accepte un nom personnalisé avec `--name` et un profil explicite avec `--profile`.
- `docforge projects list` affiche les projets enregistrés.
- `docforge projects remove` retire un projet à partir d’un nom ou d’un chemin.

Le registre est configuré à l’emplacement `~/.config/docforge/projects.yml`.

Deux autres commandes exploitent l’ensemble des projets enregistrés :

- `docforge refresh-all` actualise leurs aperçus ;
- `docforge status-all` affiche leur état quotidien.

Les faits fournis ne décrivent pas le format interne de `projects.yml`, les règles de résolution des doublons ni les champs affichés par `docforge projects list`.

## Audits et conformité

Le workflow d’audit fourni compare les projets enregistrés au modèle canonique et produit un rapport :

```sh
docforge audit-all --show-findings
docforge audit-report
```

Les commandes détectées couvrent les opérations suivantes :

- `docforge verify` compare un projet au standard documentaire ;
- `docforge audit-all` compare les applications enregistrées à `app-template` ;
- `docforge audit-report` produit un rapport persistant JSON et Markdown ;
- `docforge audit-diff` compare deux rapports de conformité ;
- `docforge remediation-plan` génère un plan de mise en conformité sans appliquer de changement ;
- `docforge status-all` affiche l’état quotidien des projets enregistrés ;
- `docforge analyze-template` analyse le modèle canonique des applications auto-hébergées ;
- `docforge verify-invariants` contrôle les invariants par rapport à la version approuvée.

Pour `docforge audit-diff`, le rapport précédent est facultatif ; le rapport le plus récent de `reports/history` est utilisé par défaut selon la description du paramètre `--previous`.

Les rapports durables sont configurés sous `reports/` et peuvent être suivis par Git. Le contexte ne précise pas le schéma des rapports JSON, la structure détaillée des rapports Markdown, les niveaux de sévérité des constats ni les codes de sortie des commandes d’audit.

## Configuration

Les emplacements ci-dessous proviennent de la configuration préparée pour le profil. Ils décrivent la règle documentaire ou l’organisation du pipeline, et non une inspection de la machine du lecteur.

| Emplacement | Portée | État indiqué | Suivi Git candidat | Rôle |
|---|---|---:|---:|---|
| `~/.config/docforge/projects.yml` | Utilisateur | Présent | Non | Registre des projets connus par docforge. |
| `~/.config/docforge/invariant-baseline.json` | Utilisateur | Présent | Non | Empreintes approuvées des documents d’invariants protégés. |
| `.docforge.yml` | Projet | Absent | Oui | Profil, sélection documentaire et exclusions de scan du projet. |
| `.docforge/cache/` | Projet | Présent | Non | Cache local des faits et de ProjectKnowledge. |
| `.docforge/preview/` | Projet | Présent | Non | Aperçus documentaires générés avant application. |
| `reports/` | Dépôt | Présent | Oui | Rapports durables pouvant être suivis par Git. |
| `pyproject.toml` | Dépôt | Présent | Oui | Métadonnées du paquet, dépendances et point d’entrée CLI. |
| `.gitignore` | Dépôt | Présent | Oui | Exclusions Git, notamment caches, aperçus et environnements virtuels. |

La commande suivante crée la configuration locale d’un projet :

```text
docforge init [PATH] [--force]
```

`--force` remplace une configuration locale existante. Le contenu exact du fichier `.docforge.yml`, ses clés autorisées et leurs valeurs ne sont pas fournis.

Les chemins configurés comme ignorés sont :

- `.docforge/` ;
- `.pytest_cache/` ;
- `.venv/` ;
- `__pycache__/`.

Aucune variable d’environnement n’est documentée.

## Sécurité

Les garde-fous détectés ou configurés sont les suivants :

| Contrôle | Catégorie | Exigence |
|---|---|---|
| `SEC-001` | Secrets | Le contenu des fichiers de secrets ne doit jamais être lu, reproduit ou sérialisé. |
| `SEC-002` | Aperçu | La génération documentaire doit écrire dans `.docforge/preview` avant toute application. |
| `SEC-003` | Application | Un document généré ne doit être appliqué qu’après une commande explicite. |
| `SEC-004` | Invariants | Un document protégé exige une autorisation explicite du propriétaire. |
| `SEC-005` | Intégrité | Les invariants approuvés doivent pouvoir être vérifiés par empreinte. |
| `SEC-006` | Portabilité | Les documents générés ne doivent pas contenir de chemin absolu propre à une machine. |
| `SEC-007` | Git | Les caches, aperçus, environnements virtuels et secrets ne doivent pas être suivis par Git. |
| `SEC-008` | Analyse statique | Les analyseurs doivent éviter d’importer ou d’exécuter le code inspecté. |

Les risques explicitement recensés sont :

- la divulgation involontaire d’un secret dans un document, un rapport ou un journal ;
- l’application automatique d’un aperçu non validé ;
- la modification non autorisée d’un document d’invariants ;
- l’exécution de code lors de l’analyse d’un dépôt ;
- l’introduction d’un chemin local non portable dans la documentation ;
- le suivi Git accidentel des caches ou des aperçus ;
- l’affaiblissement d’un test pour masquer une régression de sécurité.

Les commandes de validation fournies peuvent être exprimées sans chemin propre à une machine comme suit :

```sh
pytest -q
docforge --help
docforge verify-invariants TEMPLATE_PATH
docforge document PATH --refresh --clean
git status --short
```

`TEMPLATE_PATH` et `PATH` représentent les paramètres détectés des commandes concernées.

## Dépannage

Les faits fournis ne contiennent pas de catalogue d’erreurs, de messages de diagnostic ni de codes de sortie. Les actions ci-dessous restent limitées aux commandes et options détectées.

### Le point d’entrée `docforge` n’est pas disponible

Reprendre la séquence d’installation locale préparée : activer l’environnement virtuel, installer le paquet avec `python -m pip install -e .`, puis vérifier avec :

```sh
docforge --help
```

La source ne fournit pas de diagnostic plus précis pour une commande introuvable ou une erreur d’import.

### Le profil détecté n’est pas celui attendu

Afficher le profil avec :

```text
docforge profile [PATH]
```

Les commandes `docforge document` et `docforge verify` acceptent `--profile`. La configuration locale `.docforge.yml` peut également porter un profil, mais son schéma n’est pas documenté.

### La configuration locale manque ou doit être remplacée

Créer la configuration avec :

```text
docforge init [PATH]
```

Pour remplacer une configuration existante :

```text
docforge init [PATH] --force
```

Le contenu généré n’est pas décrit dans les faits fournis.

### L’aperçu doit être recréé

Pour la génération déterministe :

```text
docforge document [PATH] --clean --refresh
```

Pour le flux Ollama :

```text
docforge generate [PATH] --clean --refresh
```

`--clean` supprime ou recrée l’ancien dossier d’aperçu selon la commande ; `--refresh` régénère les documents déterministes déjà présents selon la description de chaque commande.

### L’application d’un document protégé est refusée

`INVARIANTS.md` exige une autorisation explicite du propriétaire :

```text
docforge apply [PATH] INVARIANTS.md --owner-approved
```

Cette option ne doit représenter une approbation que lorsqu’elle a réellement été donnée. Aucun autre mécanisme d’autorisation n’est documenté.

### Le dépôt Git est modifié lors de l’application

`docforge apply` expose `--allow-dirty`, décrit comme une autorisation exceptionnelle d’un dépôt Git modifié :

```text
docforge apply [PATH] DOCUMENTS --allow-dirty
```

Le comportement exact sans cette option et les critères utilisés pour considérer le dépôt comme modifié ne sont pas fournis.

### Les résultats d’audit manquent de détails

Utiliser les options détectées :

```sh
docforge audit-all --show-findings
docforge status-all --show-details
```

La forme exacte des détails affichés n’est pas documentée.

### La préparation d’un manuel dépasse le budget de contexte

`docforge manual prepare` expose `--context-budget`. La description précise que la préparation échoue si une section dépasse ce budget. Aucun intervalle accepté, aucune unité supplémentaire et aucune valeur recommandée ne sont fournis.

### La génération avec Ollama échoue

Le contexte ne fournit ni procédure de démarrage, ni URL, ni variable d’environnement, ni modèle par défaut. Il n’est donc pas possible de proposer un diagnostic opérationnel fidèle au-delà de la syntaxe de `docforge generate` et de son option `--model`.

### Une information nécessaire n’apparaît pas dans ce guide

Le manuel préparé est limité aux faits présents dans ProjectKnowledge et aux politiques du profil. Une information absente ou incertaine ne peut pas être reconstruite arbitrairement.

## Limites des informations disponibles

Aucune entrée explicite n’est présente dans la liste `missing_information`. Cela ne signifie pas que tous les comportements du produit sont documentés.

Les limites préparées sont :

- le manuel ne contient que les faits présents dans ProjectKnowledge et dans les politiques du profil ;
- toute information absente ou incertaine doit être signalée comme manquante ;
- les workflows restent limités aux commandes détectées dans la CLI ;
- certains constats d’environnement non pertinents pour le profil sont exclus de la projection du manuel.

La traçabilité indique :

- `project`, `profile`, `commands` et `security` comme faits détectés ;
- `installation`, `workflows` et `limitations` comme faits dérivés ;
- `configuration` comme fait configuré.

Les listes de sources associées sont vides. Le manuel ne peut donc pas fournir de chemin de fichier source ni de référence de ligne pour ces faits. Les workflows peuvent être présentés comme cohérents avec les commandes détectées, mais pas comme des scénarios testés en fonctionnement.

Les informations notamment absentes comprennent les codes de sortie, les formats complets de sortie, le schéma de `.docforge.yml`, le schéma des rapports, les détails de connexion à Ollama, les valeurs par défaut non indiquées et les messages d’erreur.

## Référence CLI

Toutes les commandes ci-dessous utilisent le `command_path` détecté. Les paramètres entre crochets sont facultatifs ; les autres sont requis.

### `docforge analyze`

Analyser un projet sans modifier ses fichiers.

```text
docforge analyze [PATH] [--json]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `PATH` | Non | Chemin du projet à analyser. |
| `--json` | Non | Afficher le résultat complet en JSON. |

### `docforge analyze-template`

Analyser le modèle canonique des applications auto-hébergées.

```text
docforge analyze-template PATH [--no-cache] [--json]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `PATH` | Oui | Chemin du dépôt app-template. |
| `--no-cache` | Non | Analyser sans écrire template.json. |
| `--json` | Non | Afficher l'analyse complète en JSON. |

### `docforge apply`

Copier des documents validés de l'aperçu vers le projet.

```text
docforge apply [PATH] DOCUMENTS [--owner-approved] [--allow-dirty]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `PATH` | Non | Chemin du projet. |
| `DOCUMENTS` | Oui | Documents d'aperçu à intégrer. |
| `--owner-approved` | Non | Confirmer l’autorisation explicite du propriétaire pour appliquer un document protégé. |
| `--allow-dirty` | Non | Autoriser exceptionnellement un dépôt Git modifié. |

### `docforge approve-invariants`

Enregistrer la version approuvée des invariants globaux.

```text
docforge approve-invariants TEMPLATE_PATH [--owner-approved]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `TEMPLATE_PATH` | Oui | Chemin du dépôt app-template. |
| `--owner-approved` | Non | Confirmer que le propriétaire autorise l'enregistrement de cette version. |

### `docforge audit-all`

Comparer les applications enregistrées à app-template.

```text
docforge audit-all [--template] [--show-findings]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `--template` | Non | Chemin du template canonique. |
| `--show-findings` | Non | Afficher les écarts détaillés. |

### `docforge audit-diff`

Comparer deux rapports de conformité.

```text
docforge audit-diff [--current] [--previous] [--output]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `--current` | Non | Rapport JSON courant. |
| `--previous` | Non | Rapport JSON précédent. Le plus récent de reports/history est utilisé par défaut. |
| `--output` | Non | Fichier Markdown de comparaison. |

### `docforge audit-report`

Générer un rapport persistant JSON et Markdown.

```text
docforge audit-report [--template] [--output-dir]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `--template` | Non | Chemin du template canonique. |
| `--output-dir` | Non | Répertoire de destination des rapports. |

### `docforge document`

Générer un aperçu des documents obligatoires manquants.

```text
docforge document [PATH] [--profile] [--clean] [--refresh] [--write]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `PATH` | Non | Chemin du projet à documenter. |
| `--profile` | Non | Profil documentaire explicite. Par défaut, utilise la configuration locale. |
| `--clean` | Non | Supprimer l'ancien aperçu avant la génération. |
| `--refresh` | Non | Régénérer les documents déterministes même s'ils existent déjà dans le projet. |
| `--write` | Non | Écrire dans le projet réel. |

### `docforge generate`

Remplir avec Ollama les documents manquants en aperçu.

```text
docforge generate [PATH] [--model] [--clean] [--refresh]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `PATH` | Non | Chemin du projet à documenter. |
| `--model` | Non | Modèle Ollama utilisé. |
| `--clean` | Non | Recréer entièrement le dossier d'aperçu. |
| `--refresh` | Non | Régénérer aussi les documents déterministes déjà présents. |

### `docforge generate-global-invariants`

Générer les invariants globaux depuis app-template.

```text
docforge generate-global-invariants TEMPLATE_PATH [--output]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `TEMPLATE_PATH` | Oui | Chemin du dépôt app-template. |
| `--output` | Non | Fichier Markdown à générer. |

### `docforge init`

Créer la configuration locale d'un projet.

```text
docforge init [PATH] [--force]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `PATH` | Non | Chemin du projet à initialiser. |
| `--force` | Non | Remplacer une configuration locale existante. |

### `docforge knowledge`

Construire la connaissance structurée d'un projet.

```text
docforge knowledge [PATH] [--output] [--json]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `PATH` | Non | Projet à analyser. |
| `--output` | Non | Fichier JSON de destination. Par défaut, utilise .docforge/cache/project-knowledge.json. |
| `--json` | Non | Afficher le JSON pur sur la sortie standard. |

### `docforge profile`

Détecter et afficher le profil d'un projet.

```text
docforge profile [PATH]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `PATH` | Non | Projet dont le profil doit être détecté. |

### `docforge refresh-all`

Actualiser les aperçus de tous les projets enregistrés.

```text
docforge refresh-all [--clean]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `--clean` | Non | Supprimer les anciens aperçus avant chaque régénération. |

### `docforge remediation-plan`

Générer un plan de mise en conformité sans appliquer de changement.

```text
docforge remediation-plan [--template] [--output]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `--template` | Non | Chemin du template canonique. |
| `--output` | Non | Fichier Markdown à générer. |

### `docforge status-all`

Afficher l’état quotidien de tous les projets.

```text
docforge status-all [--template] [--show-details]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `--template` | Non | Chemin du template canonique. |
| `--show-details` | Non | Afficher les documents différents et les écarts de conformité. |

### `docforge verify`

Comparer un projet au standard documentaire.

```text
docforge verify [PATH] [--profile]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `PATH` | Non | Chemin du projet à vérifier. |
| `--profile` | Non | Profil documentaire à appliquer. Par défaut, utilise la configuration locale ou la détection automatique. |

### `docforge verify-invariants`

Vérifier que les invariants correspondent à la version approuvée.

```text
docforge verify-invariants TEMPLATE_PATH
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `TEMPLATE_PATH` | Oui | Chemin du dépôt app-template. |

### `docforge manual prepare`

Préparer les entrées déterministes d’un manuel utilisateur.

```text
docforge manual prepare [PATH] [--clean] [--mode] [--output-dir] [--context-budget]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `PATH` | Non | Chemin du projet à préparer. |
| `--clean` | Non | Supprimer la préparation précédente avant génération. |
| `--mode` | Non | Mode de génération : full, sections ou both. |
| `--output-dir` | Non | Répertoire cible pour les artefacts du manuel. |
| `--context-budget` | Non | Budget maximum estimé par contexte de section. La préparation échoue si une section dépasse ce budget. |

### `docforge manual validate`

Valider un manuel Markdown contre les artefacts préparés.

```text
docforge manual validate MARKDOWN_FILE [--project-root] [--manual-dir] [--json] [--document-id]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `MARKDOWN_FILE` | Oui | Fichier Markdown du manuel à valider. |
| `--project-root` | Non | Racine du projet correspondant aux artefacts de préparation. |
| `--manual-dir` | Non | Répertoire contenant manual-knowledge.json et manual-manifest.json. |
| `--json` | Non | Émettre les diagnostics en JSON pour l’automatisation. |
| `--document-id` | Non | Identifiant du document à valider lorsque plusieurs guides ont été préparés. |

### `docforge projects add`

Ajouter ou mettre à jour un projet dans le registre.

```text
docforge projects add PATH [--name] [--profile]
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `PATH` | Oui | Chemin du projet à enregistrer. |
| `--name` | Non | Nom personnalisé du projet. |
| `--profile` | Non | Profil documentaire explicite. |

### `docforge projects list`

Afficher les projets enregistrés.

```text
docforge projects list
```

Cette commande ne comporte aucun paramètre détecté.

### `docforge projects remove`

Retirer un projet du registre.

```text
docforge projects remove IDENTIFIER
```

| Paramètre | Obligatoire | Description |
|---|---:|---|
| `IDENTIFIER` | Oui | Nom ou chemin du projet à retirer. |
