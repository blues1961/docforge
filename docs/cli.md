# Référence CLI — project-assistant

<!--
Document généré en aperçu par project-assistant.
Les commandes sont extraites du code Python avec ast.
-->

## Vue d’ensemble

- Framework détecté : `Typer`.
- Nombre de commandes : `21`.
- Fichiers contenant des commandes : `project_assistant/cli.py`.

## Points d’entrée

- `docforge` → `project_assistant.cli:app`

## Commandes

### `analyze`

Analyser un projet sans modifier ses fichiers.

- Fonction : `analyze`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| path | Path | argument | non | Path('.') | — | Chemin du projet à analyser. |
| json_output | bool | option | non | False | --json | Afficher le résultat complet en JSON. |

### `analyze-template`

Analyser le modèle canonique des applications auto-hébergées.

- Fonction : `analyze_template_command`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| path | Path | argument | oui | — | — | Chemin du dépôt app-template. |
| no_cache | bool | option | non | False | --no-cache | Analyser sans écrire template.json. |
| json_output | bool | option | non | False | --json | Afficher l'analyse complète en JSON. |

### `apply`

Copier des documents validés de l'aperçu vers le projet.

- Fonction : `apply_command`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| path | Path | argument | non | Path('.') | — | Chemin du projet. |
| documents | list[str] | argument | oui | — | — | Documents d'aperçu à intégrer. |
| owner_approved | bool | option | non | False | --owner-approved | Confirmer l’autorisation explicite du propriétaire pour appliquer un document protégé. |
| allow_dirty | bool | option | non | False | --allow-dirty | Autoriser exceptionnellement un dépôt Git modifié. |

### `approve-invariants`

Enregistrer la version approuvée des invariants globaux.

- Fonction : `approve_invariants_command`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| template_path | Path | argument | oui | — | — | Chemin du dépôt app-template. |
| owner_approved | bool | option | non | False | --owner-approved | Confirmer que le propriétaire autorise l'enregistrement de cette version. |

### `audit-all`

Comparer les applications enregistrées à app-template.

- Fonction : `audit_all_command`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| template_path | Path | option | non | Path.home() / 'projets' / 'app-template' | --template | Chemin du template canonique. |
| show_findings | bool | option | non | False | --show-findings | Afficher les écarts détaillés. |

### `audit-diff`

Comparer deux rapports de conformité.

- Fonction : `audit_diff_command`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| current | Path | option | non | Path('reports/audit-latest.json') | --current | Rapport JSON courant. |
| previous | Path \| None | option | non | None | --previous | Rapport JSON précédent. Le plus récent de reports/history est utilisé par défaut. |
| output | Path \| None | option | non | Path('reports/audit-diff-latest.md') | --output, -o | Fichier Markdown de comparaison. |

### `audit-report`

Générer un rapport persistant JSON et Markdown.

- Fonction : `audit_report_command`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| template_path | Path | option | non | Path.home() / 'projets' / 'app-template' | --template | Chemin du template canonique. |
| output_dir | Path | option | non | Path('reports') | --output-dir, -o | Répertoire de destination des rapports. |

### `document`

Générer un aperçu des documents obligatoires manquants.

- Fonction : `document`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| path | Path | argument | non | Path('.') | — | Chemin du projet à documenter. |
| profile | str \| None | option | non | None | --profile, -p | Profil documentaire explicite. Par défaut, utilise la configuration locale. |
| clean | bool | option | non | False | --clean | Supprimer l'ancien aperçu avant la génération. |
| refresh | bool | option | non | False | --refresh | Régénérer les documents déterministes même s'ils existent déjà dans le projet. |
| write | bool | option | non | False | --write | Écrire dans le projet réel. |

### `generate`

Remplir avec Ollama les documents manquants en aperçu.

- Fonction : `generate_command`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| path | Path | argument | non | Path('.') | — | Chemin du projet à documenter. |
| model | str | option | non | 'gemma4:latest' | --model, -m | Modèle Ollama utilisé. |
| clean | bool | option | non | False | --clean | Recréer entièrement le dossier d'aperçu. |
| refresh | bool | option | non | False | --refresh | Régénérer aussi les documents déterministes déjà présents. |

### `generate-global-invariants`

Générer les invariants globaux depuis app-template.

- Fonction : `generate_global_invariants_command`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| template_path | Path | argument | oui | — | — | Chemin du dépôt app-template. |
| output | Path | option | non | Path('defaults/global-invariants.md') | --output, -o | Fichier Markdown à générer. |

### `init`

Créer la configuration locale d'un projet.

- Fonction : `init_command`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| path | Path | argument | non | Path('.') | — | Chemin du projet à initialiser. |
| force | bool | option | non | False | --force | Remplacer une configuration locale existante. |

### `knowledge`

Construire la connaissance structurée d'un projet.

- Fonction : `knowledge_command`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| path | Path | argument | non | Path('.') | — | Projet à analyser. |
| output | Path \| None | option | non | None | --output, -o | Fichier JSON de destination. Par défaut, utilise .project-assistant/cache/project-knowledge.json. |
| print_json | bool | option | non | False | --json | Afficher également le JSON dans le terminal. |

### `profile`

Détecter et afficher le profil d'un projet.

- Fonction : `profile_command`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| path | Path | argument | non | Path('.') | — | Projet dont le profil doit être détecté. |

### `refresh-all`

Actualiser les aperçus de tous les projets enregistrés.

- Fonction : `refresh_all_command`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| clean | bool | option | non | False | --clean | Supprimer les anciens aperçus avant chaque régénération. |

### `remediation-plan`

Générer un plan de mise en conformité sans appliquer de changement.

- Fonction : `remediation_plan_command`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| template_path | Path | option | non | Path.home() / 'projets' / 'app-template' | --template | Chemin du template canonique. |
| output | Path | option | non | Path('reports/remediation-latest.md') | --output, -o | Fichier Markdown à générer. |

### `status-all`

Afficher l’état quotidien de tous les projets.

- Fonction : `status_all_command`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| template_path | Path | option | non | Path.home() / 'projets' / 'app-template' | --template | Chemin du template canonique. |
| show_details | bool | option | non | False | --show-details | Afficher les documents différents et les écarts de conformité. |

### `verify`

Comparer un projet au standard documentaire.

- Fonction : `verify`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| path | Path | argument | non | Path('.') | — | Chemin du projet à vérifier. |
| profile | str \| None | option | non | None | --profile, -p | Profil documentaire à appliquer. Par défaut, utilise la configuration locale ou la détection automatique. |

### `verify-invariants`

Vérifier que les invariants correspondent à la version approuvée.

- Fonction : `verify_invariants_command`.
- Module : `project_assistant.cli`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| template_path | Path | argument | oui | — | — | Chemin du dépôt app-template. |

### `projects_app add`

Ajouter ou mettre à jour un projet dans le registre.

- Fonction : `projects_add`.
- Module : `project_assistant.cli`.
- Groupe Typer : `projects_app`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| path | Path | argument | oui | — | — | Chemin du projet à enregistrer. |
| name | str \| None | option | non | None | --name | Nom personnalisé du projet. |
| profile | str \| None | option | non | None | --profile, -p | Profil documentaire explicite. |

### `projects_app list`

Afficher les projets enregistrés.

- Fonction : `projects_list`.
- Module : `project_assistant.cli`.
- Groupe Typer : `projects_app`.

#### Paramètres

- Aucun paramètre détecté.

### `projects_app remove`

Retirer un projet du registre.

- Fonction : `projects_remove`.
- Module : `project_assistant.cli`.
- Groupe Typer : `projects_app`.

#### Paramètres

| Nom | Type | Nature | Requis | Défaut | Options | Description |
|---|---|---|---|---|---|---|
| identifier | str | argument | oui | — | — | Nom ou chemin du projet à retirer. |

## Exemples généraux

```bash
docforge --help
docforge profile /chemin/du/projet
docforge knowledge /chemin/du/projet
docforge document /chemin/du/projet --refresh --clean
docforge audit-all --show-findings
```

## Limites de l’analyse

- les commandes créées dynamiquement à l’exécution peuvent ne pas être détectées;
- les descriptions calculées dynamiquement peuvent ne pas être disponibles;
- l’analyse ne doit jamais importer ni exécuter le module CLI;
