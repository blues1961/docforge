#### `help`

Affiche les cibles Make rendues disponibles par le projet.

Quand l’utiliser : Consulter les commandes disponibles.

> **Avertissement :** Cette opération interrompt des services ; prévenez les utilisateurs concernés.

```bash
make help
```
Environnements : dev, prod.
Effet de bord : Arrêt des services actifs.

#### `dev`

Sélectionne la configuration de développement.

Quand l’utiliser : Sélectionner la configuration de développement.

```bash
make dev
```
Environnements : dev.

#### `prod`

Sélectionne la configuration de production.

Quand l’utiliser : Sélectionner la configuration de production.

> **Avertissement :** Vous sélectionnez l’environnement de production ; vérifiez ce choix avant de poursuivre.

```bash
make prod
```
Environnements : prod.
Effet de bord : Sélection de l’environnement de production.

#### `init`

Initialise l’environnement de travail avec la recette détectée.

Quand l’utiliser : Initialiser l’environnement après sa configuration.

```bash
make init
```
Environnements : dev, prod.
Effet de bord : Initialisation de l’environnement de travail.

#### `up`

Démarre les services définis par le projet.

Quand l’utiliser : Démarrer les services.

```bash
make up
```
Environnements : dev, prod.
Effet de bord : Démarrage des services définis par le projet.

#### `ps`

Affiche l’état des services.

Quand l’utiliser : Vérifier l’état des services.

```bash
make ps
```
Environnements : dev, prod.

#### `logs`

Affiche les journaux du service demandé.

Quand l’utiliser : Examiner les journaux d’un service.

```bash
make logs SERVICE=backend
```

Paramètres :
- `SERVICE` (requis) — valeur attendue par la recette. Exemples de services : backend, db, frontend.
Environnements : dev, prod.

#### `migrate`

Applique les migrations définies par la recette du projet.

Quand l’utiliser : Appliquer les migrations.

```bash
make migrate
```
Environnements : dev, prod.
Effet de bord : Application des migrations de base de données.

#### `rebuild`

Reconstruit le ou les services demandés.

Quand l’utiliser : Reconstruire un service après un changement nécessitant une nouvelle image.

> **Avertissement :** Cette opération reconstruit des images ou services ; vérifiez le service et l’environnement actifs.

```bash
make rebuild SERVICE=backend
```

Paramètres :
- `SERVICE` (requis) — valeur attendue par la recette. Exemples de services : backend, db, frontend.
Environnements : dev, prod.
Effet de bord : Reconstruction des images ou services.

#### `restart`

Redémarre les services en exécutant la recette de redémarrage.

Quand l’utiliser : Redémarrer les services.

> **Avertissement :** Cette opération interrompt des services ; prévenez les utilisateurs concernés.

```bash
make restart
```
Environnements : dev, prod.
Effet de bord : Arrêt des services actifs.

#### `down`

Arrête les services actifs.

Quand l’utiliser : Arrêter les services.

> **Avertissement :** Cette opération interrompt des services ; prévenez les utilisateurs concernés.

```bash
make down
```
Environnements : dev, prod.
Effet de bord : Arrêt des services actifs.

#### `update`

Exécute la recette de mise à jour déclarée par le projet.

Quand l’utiliser : Exécuter la procédure de mise à jour du projet.

> **Avertissement :** Cette opération reconstruit des images ou services ; vérifiez le service et l’environnement actifs.

```bash
make update
```
Environnements : dev, prod.
Effet de bord : Reconstruction des images ou services.

#### `backup`

Lance la sauvegarde de base de données démontrée.

Quand l’utiliser : Créer une sauvegarde avant une opération risquée.

```bash
make backup
```
Environnements : dev, prod.
Effet de bord : Création d’une sauvegarde de base de données.

#### `restore`

Lance la restauration de base de données depuis le fichier fourni.

Quand l’utiliser : Restaurer les données depuis une sauvegarde.

> **Avertissement :** Cette opération peut modifier ou écraser des données ; vérifiez la sauvegarde et l’environnement actif.

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

Quand l’utiliser : Exécuter les contrôles déclarés par le projet.

```bash
make check
```
Environnements : dev, prod.
