#### `help`

Affiche les cibles Make rendues disponibles par le projet.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make help
```
Environnements : dev, prod.
Effet précis non documenté.

#### `dev`

Sélectionne la configuration de développement.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make dev
```
Environnements : dev.
Effet précis non documenté.

#### `prod`

Sélectionne la configuration de production.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make prod
```
Environnements : prod.
Effet précis non documenté.

#### `init`

Initialise l’environnement de travail avec la recette détectée.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make init
```
Environnements : dev, prod.
Effet précis non documenté.

#### `up`

Démarre les services définis par le projet.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make up
```
Environnements : dev, prod.
Effet précis non documenté.

#### `ps`

Affiche l’état des services.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make ps
```
Environnements : dev, prod.
Effet précis non documenté.

#### `logs`

Affiche les journaux du service demandé.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make logs SERVICE=backend
```

Paramètres :
- `SERVICE` (requis) — valeur attendue par la recette. Exemples de services : backend, db, frontend.
Environnements : dev, prod.
Effet précis non documenté.

#### `migrate`

Applique les migrations définies par la recette du projet.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

> **Prudence :** cette commande peut modifier des services, des images ou des données. Vérifiez l’environnement actif avant son exécution.

```bash
make migrate
```
Environnements : dev, prod.
Effet précis non documenté.

#### `rebuild`

Reconstruit le ou les services demandés.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

> **Prudence :** cette commande peut modifier des services, des images ou des données. Vérifiez l’environnement actif avant son exécution.

```bash
make rebuild SERVICE=backend
```

Paramètres :
- `SERVICE` (requis) — valeur attendue par la recette. Exemples de services : backend, db, frontend.
Environnements : dev, prod.
Effet de bord : Reconstruction des images ou services.

#### `restart`

Redémarre les services en exécutant la recette de redémarrage.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

> **Prudence :** cette commande peut modifier des services, des images ou des données. Vérifiez l’environnement actif avant son exécution.

```bash
make restart
```
Environnements : dev, prod.
Effet de bord : Arrêt des services actifs.

#### `down`

Arrête les services actifs.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

> **Prudence :** cette commande peut modifier des services, des images ou des données. Vérifiez l’environnement actif avant son exécution.

```bash
make down
```
Environnements : dev, prod.
Effet de bord : Arrêt des services actifs.

#### `update`

Exécute la recette de mise à jour déclarée par le projet.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

> **Prudence :** cette commande peut modifier des services, des images ou des données. Vérifiez l’environnement actif avant son exécution.

```bash
make update
```
Environnements : dev, prod.
Effet de bord : Reconstruction des images ou services.

#### `backup`

Lance la sauvegarde de base de données démontrée.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make backup
```
Environnements : dev, prod.
Effet précis non documenté.

#### `restore`

Lance la restauration de base de données depuis le fichier fourni.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

> **Prudence :** cette commande peut modifier des services, des images ou des données. Vérifiez l’environnement actif avant son exécution.

```bash
make restore
make restore FILE=chemin/vers/sauvegarde.sql.gz
```

Paramètres :
- `FILE` (facultatif) — valeur attendue par la recette.
Environnements : dev, prod.
Effet de bord : Modification ou écrasement potentiel des données PostgreSQL.

#### `check`

Exécute le contrôle ou diagnostic déclaré par le projet.

Quand l’utiliser : À utiliser par l’exploitant lorsque cette opération est nécessaire.

```bash
make check
```
Environnements : dev, prod.
Effet précis non documenté.
