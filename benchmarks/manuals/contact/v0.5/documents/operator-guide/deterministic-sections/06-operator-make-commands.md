### Cibles Make démontrées

#### `backup`

Résumé : Lance la sauvegarde de base de données démontrée.
Usage opérateur : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make backup
```

Paramètres :
- Aucun paramètre utilisateur démontré.
Environnements : dev, prod.
Effet de bord démontré : aucun effet de bord démontré.
Provenance : template-standard.

#### `rebuild`

Résumé : Reconstruit le ou les services demandés.
Usage opérateur : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make rebuild SERVICE=SERVICE
```

Paramètres :
- `SERVICE` (requis) — Paramètre démontré.
Environnements : dev, prod.
Effet de bord démontré : Reconstruction des images ou services.
Provenance : template-standard.

#### `update`

Résumé : Exécute la recette de mise à jour déclarée par le projet.
Usage opérateur : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make update
```

Paramètres :
- Aucun paramètre utilisateur démontré.
Environnements : dev, prod.
Effet de bord démontré : Reconstruction des images ou services.
Provenance : application-public.

#### `check`

Résumé : Exécute le contrôle ou diagnostic déclaré par le projet.
Usage opérateur : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make check
```

Paramètres :
- Aucun paramètre utilisateur démontré.
Environnements : dev, prod.
Effet de bord démontré : aucun effet de bord démontré.
Provenance : template-standard.

#### `ps`

Résumé : Affiche l’état des services.
Usage opérateur : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make ps
```

Paramètres :
- Aucun paramètre utilisateur démontré.
Environnements : dev, prod.
Effet de bord démontré : aucun effet de bord démontré.
Provenance : template-standard.

#### `dev`

Résumé : Sélectionne la configuration de développement.
Usage opérateur : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make dev
```

Paramètres :
- Aucun paramètre utilisateur démontré.
Environnements : dev.
Effet de bord démontré : aucun effet de bord démontré.
Provenance : template-standard.

#### `prod`

Résumé : Sélectionne la configuration de production.
Usage opérateur : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make prod
```

Paramètres :
- Aucun paramètre utilisateur démontré.
Environnements : prod.
Effet de bord démontré : aucun effet de bord démontré.
Provenance : template-standard.

#### `logs`

Résumé : Affiche les journaux du service demandé.
Usage opérateur : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make logs SERVICE=SERVICE
```

Paramètres :
- `SERVICE` (requis) — Paramètre démontré.
Environnements : dev, prod.
Effet de bord démontré : aucun effet de bord démontré.
Provenance : template-standard.

#### `migrate`

Résumé : Applique les migrations définies par la recette du projet.
Usage opérateur : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make migrate
```

Paramètres :
- Aucun paramètre utilisateur démontré.
Environnements : dev, prod.
Effet de bord démontré : aucun effet de bord démontré.
Provenance : template-standard.

#### `help`

Résumé : Affiche les cibles Make rendues disponibles par le projet.
Usage opérateur : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make help
```

Paramètres :
- Aucun paramètre utilisateur démontré.
Environnements : dev, prod.
Effet de bord démontré : aucun effet de bord démontré.
Provenance : application-public.

#### `restart`

Résumé : Redémarre les services en exécutant la recette de redémarrage.
Usage opérateur : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make restart
```

Paramètres :
- Aucun paramètre utilisateur démontré.
Environnements : dev, prod.
Effet de bord démontré : Arrêt des services actifs.
Provenance : template-standard.

#### `restore`

Résumé : Lance la restauration de base de données depuis le fichier fourni.
Usage opérateur : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make restore [FILE=FILE]
```

Paramètres :
- `FILE` (facultatif) — Paramètre démontré.
Environnements : dev, prod.
Effet de bord démontré : Modification ou écrasement potentiel des données PostgreSQL.
Provenance : template-standard.

#### `init`

Résumé : Initialise l’environnement de travail avec la recette détectée.
Usage opérateur : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make init
```

Paramètres :
- Aucun paramètre utilisateur démontré.
Environnements : dev, prod.
Effet de bord démontré : aucun effet de bord démontré.
Provenance : template-standard.

#### `down`

Résumé : Arrête les services actifs.
Usage opérateur : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make down
```

Paramètres :
- Aucun paramètre utilisateur démontré.
Environnements : dev, prod.
Effet de bord démontré : Arrêt des services actifs.
Provenance : template-standard.

#### `up`

Résumé : Démarre les services définis par le projet.
Usage opérateur : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make up
```

Paramètres :
- Aucun paramètre utilisateur démontré.
Environnements : dev, prod.
Effet de bord démontré : aucun effet de bord démontré.
Provenance : template-standard.
