### Cibles Make démontrées

#### `backup`

Lance la sauvegarde de base de données démontrée.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make backup
```

Paramètres utilisateur :
- Aucun paramètre utilisateur démontré.

Environnements : dev, prod.
Comportement démontré : $(SCRIPTS_DIR)/backup-db.sh
Effet destructif : aucun effet destructif démontré.
Provenance : template-standard — Statut : fait détecté.

#### `rebuild`

Reconstruit le ou les services demandés.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make rebuild SERVICE=SERVICE
```

Paramètres utilisateur :
- `SERVICE` (requis) — Paramètre exposé par la recette Make.

Environnements : dev, prod.
Comportement démontré : $(SCRIPTS_DIR)/rebuild.sh $(SERVICE)
Effet destructif : Reconstruction des images ou services.
Provenance : template-standard — Statut : fait détecté.

#### `update`

Exécute la recette de mise à jour déclarée par le projet.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make update
```

Paramètres utilisateur :
- Aucun paramètre utilisateur démontré.

Environnements : dev, prod.
Comportement démontré : $(SCRIPTS_DIR)/update.sh
Effet destructif : Reconstruction des images ou services.
Provenance : application-public — Statut : fait détecté.

#### `check`

Exécute le contrôle ou diagnostic déclaré par le projet.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make check
```

Paramètres utilisateur :
- Aucun paramètre utilisateur démontré.

Environnements : dev, prod.
Comportement démontré : $(SCRIPTS_DIR)/check-invariants.sh
Effet destructif : aucun effet destructif démontré.
Provenance : template-standard — Statut : fait détecté.

#### `ps`

Affiche l’état des services.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make ps
```

Paramètres utilisateur :
- Aucun paramètre utilisateur démontré.

Environnements : dev, prod.
Comportement démontré : $(SCRIPTS_DIR)/ps.sh
Effet destructif : aucun effet destructif démontré.
Provenance : template-standard — Statut : fait détecté.

#### `dev`

Sélectionne la configuration de développement.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make dev
```

Paramètres utilisateur :
- Aucun paramètre utilisateur démontré.

Environnements : dev.
Comportement démontré : $(SCRIPTS_DIR)/env-switch.sh dev
Effet destructif : aucun effet destructif démontré.
Provenance : template-standard — Statut : fait détecté.

#### `prod`

Sélectionne la configuration de production.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make prod
```

Paramètres utilisateur :
- Aucun paramètre utilisateur démontré.

Environnements : prod.
Comportement démontré : $(SCRIPTS_DIR)/env-switch.sh prod
Effet destructif : aucun effet destructif démontré.
Provenance : template-standard — Statut : fait détecté.

#### `logs`

Affiche les journaux du service demandé.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make logs SERVICE=SERVICE
```

Paramètres utilisateur :
- `SERVICE` (requis) — Paramètre exposé par la recette Make.

Environnements : dev, prod.
Comportement démontré : $(SCRIPTS_DIR)/logs.sh $(SERVICE)
Effet destructif : aucun effet destructif démontré.
Provenance : template-standard — Statut : fait détecté.

#### `migrate`

Applique les migrations définies par la recette du projet.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make migrate
```

Paramètres utilisateur :
- Aucun paramètre utilisateur démontré.

Environnements : dev, prod.
Comportement démontré : $(SCRIPTS_DIR)/migrate.sh
Effet destructif : aucun effet destructif démontré.
Provenance : template-standard — Statut : fait détecté.

#### `help`

Affiche les cibles Make rendues disponibles par le projet.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make help
```

Paramètres utilisateur :
- Aucun paramètre utilisateur démontré.

Environnements : dev, prod.
Comportement démontré : @printf '%s\n' \ ; 'Usage: make <target>' \ ; '' \ ; 'Cibles disponibles :' \ ; '  help      Affiche cette aide' \ ; '  init      Initialise le projet dans l’environnement pointé par .env (scripts/init.sh)' \ ; '  dev       Bascule l’environnement actif vers .env.dev' \ ; '  prod      Bascule l’environnement actif vers .env.prod' \ ; '  up        Démarre les services de l’environnement actif' \ ; '  down      Arrête les services de l’environnement actif' \ ; '  restart   Redémarre les services de l’environnement actif' \ ; '  rebuild   Reconstruit les images (optionnel : make rebuild SERVICE=backend)' \ ; '  logs      Affiche les logs (optionnel : make logs SERVICE=backend)' \ ; '  ps        Affiche l’état des services de l’environnement actif' \ ; '  check     Vérifie les invariants du template' \ ; '  migrate   Applique les migrations Django dans l’environnement actif' \ ; '  update    Met à jour l’application dans l’environnement actif' \ ; '  backup    Crée un backup PostgreSQL dans ./backup' \ ; '  restore   Restaure un backup PostgreSQL' \ ; '' \ ; 'Options pour restore :' \ ; '  make restore' \ ; '            Restaure automatiquement le backup le plus récent trouvé dans ./backup' \ ; '  make restore FILE=./backup/__APP_SLUG___db-YYYYMMDD_HHMMSS.sql.gz' \ ; '            Restaure le fichier de backup spécifié'
Effet destructif : aucun effet destructif démontré.
Provenance : application-public — Statut : fait détecté.

#### `restart`

Redémarre les services en exécutant la recette de redémarrage.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make restart
```

Paramètres utilisateur :
- Aucun paramètre utilisateur démontré.

Environnements : dev, prod.
Comportement démontré : $(SCRIPTS_DIR)/restart.sh
Effet destructif : Arrêt des services actifs.
Provenance : template-standard — Statut : fait détecté.

#### `restore`

Lance la restauration de base de données depuis le fichier fourni.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make restore [FILE=FILE]
```

Paramètres utilisateur :
- `FILE` (facultatif) — Paramètre exposé par la recette Make.

Environnements : dev, prod.
Comportement démontré : @if [ -n "$(FILE)" ]; then \ ; $(SCRIPTS_DIR)/restore-db.sh "$(FILE)"; \ ; else \ ; $(SCRIPTS_DIR)/restore-db.sh; \ ; fi
Effet destructif : Modification ou écrasement potentiel des données PostgreSQL.
Provenance : template-standard — Statut : fait détecté.

#### `init`

Initialise l’environnement de travail avec la recette détectée.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make init
```

Paramètres utilisateur :
- Aucun paramètre utilisateur démontré.

Environnements : dev, prod.
Comportement démontré : $(SCRIPTS_DIR)/init.sh
Effet destructif : aucun effet destructif démontré.
Provenance : template-standard — Statut : fait détecté.

#### `down`

Arrête les services actifs.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make down
```

Paramètres utilisateur :
- Aucun paramètre utilisateur démontré.

Environnements : dev, prod.
Comportement démontré : $(SCRIPTS_DIR)/down.sh
Effet destructif : Arrêt des services actifs.
Provenance : template-standard — Statut : fait détecté.

#### `up`

Démarre les services définis par le projet.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make up
```

Paramètres utilisateur :
- Aucun paramètre utilisateur démontré.

Environnements : dev, prod.
Comportement démontré : $(SCRIPTS_DIR)/up.sh
Effet destructif : aucun effet destructif démontré.
Provenance : template-standard — Statut : fait détecté.
