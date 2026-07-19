### Entrées de la référence CLI

#### `analyze`

Analyser un projet sans modifier ses fichiers.

Quand l’utiliser : Utiliser cette commande pour analyser un projet sans modifier ses fichiers.

```bash
docforge analyze [PATH] [--json]
```

Arguments :
- `PATH` (facultatif) — Chemin du projet à analyser.

Options :
- `--json` (facultatif) — Afficher le résultat complet en JSON.

Résultat ou effet :
- Comportement démontré : Analyser un projet sans modifier ses fichiers.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `analyze-template`

Analyser le modèle canonique des applications auto-hébergées.

Quand l’utiliser : Utiliser cette commande pour analyser le modèle canonique des applications auto-hébergées.

```bash
docforge analyze-template PATH [--no-cache] [--json]
```

Arguments :
- `PATH` (requis) — Chemin du dépôt app-template.

Options :
- `--no-cache` (facultatif) — Analyser sans écrire template.json.
- `--json` (facultatif) — Afficher l'analyse complète en JSON.

Résultat ou effet :
- Comportement démontré : Analyser le modèle canonique des applications auto-hébergées.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `apply`

Copier des documents validés de l'aperçu vers le projet.

Quand l’utiliser : Utiliser cette commande pour copier des documents validés de l'aperçu vers le projet.

```bash
docforge apply [PATH] DOCUMENTS [--owner-approved] [--allow-dirty]
```

Arguments :
- `PATH` (facultatif) — Chemin du projet.
- `DOCUMENTS` (requis) — Documents d'aperçu à intégrer.

Options :
- `--owner-approved` (facultatif) — Confirmer l’autorisation explicite du propriétaire pour appliquer un document protégé.
- `--allow-dirty` (facultatif) — Autoriser exceptionnellement un dépôt Git modifié.

Résultat ou effet :
- Comportement démontré : Copier des documents validés de l'aperçu vers le projet.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `approve-invariants`

Enregistrer la version approuvée des invariants globaux.

Quand l’utiliser : Utiliser cette commande pour enregistrer la version approuvée des invariants globaux.

```bash
docforge approve-invariants TEMPLATE_PATH [--owner-approved]
```

Arguments :
- `TEMPLATE_PATH` (requis) — Chemin du dépôt app-template.

Options :
- `--owner-approved` (facultatif) — Confirmer que le propriétaire autorise l'enregistrement de cette version.

Résultat ou effet :
- Comportement démontré : Enregistrer la version approuvée des invariants globaux.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `audit-all`

Comparer les applications enregistrées à app-template.

Quand l’utiliser : Utiliser cette commande pour comparer les applications enregistrées à app-template.

```bash
docforge audit-all [--template TEMPLATE] [--show-findings]
```

Arguments :
- Aucun paramètre positionnel démontré.

Options :
- `--template TEMPLATE` (facultatif) — Chemin du template canonique.
- `--show-findings` (facultatif) — Afficher les écarts détaillés.

Résultat ou effet :
- Comportement démontré : Comparer les applications enregistrées à app-template.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `audit-diff`

Comparer deux rapports de conformité.

Quand l’utiliser : Utiliser cette commande pour comparer deux rapports de conformité.

```bash
docforge audit-diff [--current CURRENT] [--previous PREVIOUS] [--output OUTPUT]
```

Arguments :
- Aucun paramètre positionnel démontré.

Options :
- `--current CURRENT` (facultatif) — Rapport JSON courant.
- `--previous PREVIOUS` (facultatif) — Rapport JSON précédent. Le plus récent de reports/history est utilisé par défaut.
- `--output OUTPUT` (facultatif) — Fichier Markdown de comparaison. Alias : `-o`.

Résultat ou effet :
- Comportement démontré : Comparer deux rapports de conformité.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `audit-report`

Générer un rapport persistant JSON et Markdown.

Quand l’utiliser : Utiliser cette commande pour générer un rapport persistant JSON et Markdown.

```bash
docforge audit-report [--template TEMPLATE] [--output-dir OUTPUT_DIR]
```

Arguments :
- Aucun paramètre positionnel démontré.

Options :
- `--template TEMPLATE` (facultatif) — Chemin du template canonique.
- `--output-dir OUTPUT_DIR` (facultatif) — Répertoire de destination des rapports. Alias : `-o`.

Résultat ou effet :
- Comportement démontré : Générer un rapport persistant JSON et Markdown.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `document`

Générer un aperçu des documents obligatoires manquants.

Quand l’utiliser : Utiliser cette commande pour générer un aperçu des documents obligatoires manquants.

```bash
docforge document [PATH] [--profile PROFILE] [--clean] [--refresh] [--write]
```

Arguments :
- `PATH` (facultatif) — Chemin du projet à documenter.

Options :
- `--profile PROFILE` (facultatif) — Profil documentaire explicite. Par défaut, utilise la configuration locale. Alias : `-p`.
- `--clean` (facultatif) — Supprimer l'ancien aperçu avant la génération.
- `--refresh` (facultatif) — Régénérer les documents déterministes même s'ils existent déjà dans le projet.
- `--write` (facultatif) — Écrire dans le projet réel.

Résultat ou effet :
- Comportement démontré : Générer un aperçu des documents obligatoires manquants.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `generate`

Remplir avec Ollama les documents manquants en aperçu.

Quand l’utiliser : Utiliser cette commande pour remplir avec Ollama les documents manquants en aperçu.

```bash
docforge generate [PATH] [--model MODEL] [--clean] [--refresh]
```

Arguments :
- `PATH` (facultatif) — Chemin du projet à documenter.

Options :
- `--model MODEL` (facultatif) — Modèle Ollama utilisé. Alias : `-m`.
- `--clean` (facultatif) — Recréer entièrement le dossier d'aperçu.
- `--refresh` (facultatif) — Régénérer aussi les documents déterministes déjà présents.

Résultat ou effet :
- Comportement démontré : Remplir avec Ollama les documents manquants en aperçu.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `generate-global-invariants`

Générer les invariants globaux depuis app-template.

Quand l’utiliser : Utiliser cette commande pour générer les invariants globaux depuis app-template.

```bash
docforge generate-global-invariants TEMPLATE_PATH [--output OUTPUT]
```

Arguments :
- `TEMPLATE_PATH` (requis) — Chemin du dépôt app-template.

Options :
- `--output OUTPUT` (facultatif) — Fichier Markdown à générer. Alias : `-o`.

Résultat ou effet :
- Comportement démontré : Générer les invariants globaux depuis app-template.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `init`

Créer la configuration locale d'un projet.

Quand l’utiliser : Utiliser cette commande pour créer la configuration locale d'un projet.

```bash
docforge init [PATH] [--force]
```

Arguments :
- `PATH` (facultatif) — Chemin du projet à initialiser.

Options :
- `--force` (facultatif) — Remplacer une configuration locale existante.

Résultat ou effet :
- Comportement démontré : Créer la configuration locale d'un projet.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `knowledge`

Construire la connaissance structurée d'un projet.

Quand l’utiliser : Utiliser cette commande pour construire la connaissance structurée d'un projet.

```bash
docforge knowledge [PATH] [--output OUTPUT] [--json]
```

Arguments :
- `PATH` (facultatif) — Projet à analyser.

Options :
- `--output OUTPUT` (facultatif) — Fichier JSON de destination. Par défaut, utilise .docforge/cache/project-knowledge.json. Alias : `-o`.
- `--json` (facultatif) — Afficher le JSON pur sur la sortie standard.

Résultat ou effet :
- Comportement démontré : Construire la connaissance structurée d'un projet.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `profile`

Détecter et afficher le profil d'un projet.

Quand l’utiliser : Utiliser cette commande pour détecter et afficher le profil d'un projet.

```bash
docforge profile [PATH]
```

Arguments :
- `PATH` (facultatif) — Projet dont le profil doit être détecté.

Options :
- Aucune option démontrée.

Résultat ou effet :
- Comportement démontré : Détecter et afficher le profil d'un projet.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `refresh-all`

Actualiser les aperçus de tous les projets enregistrés.

Quand l’utiliser : Utiliser cette commande pour actualiser les aperçus de tous les projets enregistrés.

```bash
docforge refresh-all [--clean]
```

Arguments :
- Aucun paramètre positionnel démontré.

Options :
- `--clean` (facultatif) — Supprimer les anciens aperçus avant chaque régénération.

Résultat ou effet :
- Comportement démontré : Actualiser les aperçus de tous les projets enregistrés.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `remediation-plan`

Générer un plan de mise en conformité sans appliquer de changement.

Quand l’utiliser : Utiliser cette commande pour générer un plan de mise en conformité sans appliquer de changement.

```bash
docforge remediation-plan [--template TEMPLATE] [--output OUTPUT]
```

Arguments :
- Aucun paramètre positionnel démontré.

Options :
- `--template TEMPLATE` (facultatif) — Chemin du template canonique.
- `--output OUTPUT` (facultatif) — Fichier Markdown à générer. Alias : `-o`.

Résultat ou effet :
- Comportement démontré : Générer un plan de mise en conformité sans appliquer de changement.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `status-all`

Afficher l’état quotidien de tous les projets.

Quand l’utiliser : Utiliser cette commande pour afficher l’état quotidien de tous les projets.

```bash
docforge status-all [--template TEMPLATE] [--show-details]
```

Arguments :
- Aucun paramètre positionnel démontré.

Options :
- `--template TEMPLATE` (facultatif) — Chemin du template canonique.
- `--show-details` (facultatif) — Afficher les documents différents et les écarts de conformité.

Résultat ou effet :
- Comportement démontré : Afficher l’état quotidien de tous les projets.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `verify`

Comparer un projet au standard documentaire.

Quand l’utiliser : Utiliser cette commande pour comparer un projet au standard documentaire.

```bash
docforge verify [PATH] [--profile PROFILE]
```

Arguments :
- `PATH` (facultatif) — Chemin du projet à vérifier.

Options :
- `--profile PROFILE` (facultatif) — Profil documentaire à appliquer. Par défaut, utilise la configuration locale ou la détection automatique. Alias : `-p`.

Résultat ou effet :
- Comportement démontré : Comparer un projet au standard documentaire.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `verify-invariants`

Vérifier que les invariants correspondent à la version approuvée.

Quand l’utiliser : Utiliser cette commande pour vérifier que les invariants correspondent à la version approuvée.

```bash
docforge verify-invariants TEMPLATE_PATH
```

Arguments :
- `TEMPLATE_PATH` (requis) — Chemin du dépôt app-template.

Options :
- Aucune option démontrée.

Résultat ou effet :
- Comportement démontré : Vérifier que les invariants correspondent à la version approuvée.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `manual prepare`

Préparer les entrées déterministes d’un manuel utilisateur.

Quand l’utiliser : Utiliser cette commande pour préparer les entrées déterministes d’un manuel utilisateur.

```bash
docforge manual prepare [PATH] [--clean] [--mode MODE] [--output-dir OUTPUT_DIR] [--context-budget CONTEXT_BUDGET]
```

Arguments :
- `PATH` (facultatif) — Chemin du projet à préparer.

Options :
- `--clean` (facultatif) — Supprimer la préparation précédente avant génération.
- `--mode MODE` (facultatif) — Mode de génération : full, sections ou both.
- `--output-dir OUTPUT_DIR` (facultatif) — Répertoire cible pour les artefacts du manuel.
- `--context-budget CONTEXT_BUDGET` (facultatif) — Budget maximum estimé par contexte de section. La préparation échoue si une section dépasse ce budget.

Résultat ou effet :
- Comportement démontré : Préparer les entrées déterministes d’un manuel utilisateur.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `manual validate`

Valider un manuel Markdown contre les artefacts préparés.

Quand l’utiliser : Utiliser cette commande pour valider un manuel Markdown contre les artefacts préparés.

```bash
docforge manual validate MARKDOWN_FILE [--project-root PROJECT_ROOT] [--manual-dir MANUAL_DIR] [--json] [--document-id DOCUMENT_ID]
```

Arguments :
- `MARKDOWN_FILE` (requis) — Fichier Markdown du manuel à valider.

Options :
- `--project-root PROJECT_ROOT` (facultatif) — Racine du projet correspondant aux artefacts de préparation.
- `--manual-dir MANUAL_DIR` (facultatif) — Répertoire contenant manual-knowledge.json et manual-manifest.json.
- `--json` (facultatif) — Émettre les diagnostics en JSON pour l’automatisation.
- `--document-id DOCUMENT_ID` (facultatif) — Identifiant du document à valider lorsque plusieurs guides ont été préparés.

Résultat ou effet :
- Comportement démontré : Valider un manuel Markdown contre les artefacts préparés.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `projects add`

Ajouter ou mettre à jour un projet dans le registre.

Quand l’utiliser : Utiliser cette commande pour ajouter ou mettre à jour un projet dans le registre.

```bash
docforge projects add PATH [--name NAME] [--profile PROFILE]
```

Arguments :
- `PATH` (requis) — Chemin du projet à enregistrer.

Options :
- `--name NAME` (facultatif) — Nom personnalisé du projet.
- `--profile PROFILE` (facultatif) — Profil documentaire explicite. Alias : `-p`.

Résultat ou effet :
- Comportement démontré : Ajouter ou mettre à jour un projet dans le registre.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `projects list`

Afficher les projets enregistrés.

Quand l’utiliser : Utiliser cette commande pour afficher les projets enregistrés.

```bash
docforge projects list
```

Arguments :
- Aucun paramètre positionnel démontré.

Options :
- Aucune option démontrée.

Résultat ou effet :
- Comportement démontré : Afficher les projets enregistrés.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.

#### `projects remove`

Retirer un projet du registre.

Quand l’utiliser : Utiliser cette commande pour retirer un projet du registre.

```bash
docforge projects remove IDENTIFIER
```

Arguments :
- `IDENTIFIER` (requis) — Nom ou chemin du projet à retirer.

Options :
- Aucune option démontrée.

Résultat ou effet :
- Comportement démontré : Retirer un projet du registre.
- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.

Statut : fait détecté.
