# Invariants globaux des applications auto-hébergées

<!--
Document généré par project-assistant à partir du dépôt app-template.
Ne pas modifier manuellement sans mettre également à jour app-template.
-->

Source canonique : `/home/sylvain/projets/app-template`

Date de génération : `2026-07-14`

## Portée

Ces invariants s’appliquent aux applications auto-hébergées dérivées de `app-template`.

Les sites statiques, les dépôts de conception 3D et les autres catégories de projets utilisent des profils distincts et ne sont pas couverts par ce document.

## Socle technologique canonique

- Langages détectés : `CSS`, `HTML`, `JSON`, `JavaScript`, `Markdown`, `Python`, `Shell`, `YAML`.
- Frameworks détectés : `Django`, `React`, `Vite`.
- Technologies détectées : `Django`, `Docker Compose`, `PostgreSQL`, `React`, `Traefik`, `Vite`.

## Structure canonique

- Dossiers racine détectés : `backend`, `backup`, `docs`, `frontend`, `scripts`.
- Fichiers racine détectés : `.codex`, `.env.template.example`, `.gitignore`, `AGENTS.md`, `CODEX_START.md`, `INVARIANTS.md`, `Makefile`, `README.md`, `README_DEV.md`, `docker-compose.dev.yml`, `docker-compose.prod.yml`.

### Documentation présente dans le template

- `README.md`
- `README_DEV.md`
- `CODEX_START.md`
- `AGENTS.md`
- `INVARIANTS.md`
- `docs/specification.md`

### Fichiers Docker Compose

- `docker-compose.dev.yml`
- `docker-compose.prod.yml`

### Scripts canoniques

- `scripts/backup-db.sh`
- `scripts/check-invariants.sh`
- `scripts/down.sh`
- `scripts/env-switch.sh`
- `scripts/generate-env.sh`
- `scripts/generate-secrets.sh`
- `scripts/init.sh`
- `scripts/logs.sh`
- `scripts/migrate.sh`
- `scripts/ps.sh`
- `scripts/rebuild.sh`
- `scripts/restart.sh`
- `scripts/restore-db.sh`
- `scripts/up.sh`
- `scripts/update.sh`

### Interface Makefile

- `make backup`
- `make check`
- `make dev`
- `make down`
- `make help`
- `make init`
- `make logs`
- `make migrate`
- `make prod`
- `make ps`
- `make rebuild`
- `make restart`
- `make restore`
- `make up`
- `make update`

## Environnements et secrets

- Le modèle de configuration canonique est `.env.template.example`.
- Les fichiers d’environnement actifs sont générés ou initialisés à partir du modèle canonique.
- Les secrets ne doivent pas être intégrés au dépôt Git.
- Les secrets locaux appartiennent aux fichiers `.local` prévus par le projet.
- Le choix de l’environnement actif doit passer par les scripts et cibles Makefile du template.

## Architecture Docker canonique

- Services : `backend`, `db`, `frontend`.
- Réseaux : `edge`, `internal`.
- Réseaux externes : `edge`.
- Volumes : `frontend_node_modules`, `postgres_data`.
- Traefik constitue le point d’entrée HTTP/HTTPS de production.
- PostgreSQL constitue la base de données relationnelle canonique.

## Invariants explicitement définis par app-template

### Rôle

Ce fichier est le contrat technique du projet.

Il définit les règles obligatoires que doivent respecter :

* le code ;
* Docker Compose ;
* les fichiers `.env` ;
* les scripts ;
* la documentation ;
* Codex.

En cas de contradiction, ce fichier prévaut.

---

### 1. Identité du projet

Les variables suivantes doivent être définies dans `.env.dev` et `.env.prod` :

```env
APP_NAME=
APP_SLUG=
APP_DEPOT=
APP_NO=
APP_ENV=
```

Règles :

* `APP_NAME` = nom lisible de l’application ;
* `APP_SLUG` = identifiant technique court ;
* `APP_DEPOT` = nom du dépôt Git et du dossier projet ;
* `APP_NO` = numéro unique utilisé pour dériver les ports ;
* `APP_ENV` = `dev` ou `prod`.

---

### 2. Fichiers d’environnement

Structure obligatoire :

```text
.env.template.example
.env.template
.env.dev
.env.prod
.env.local
.env
```

Règles :

* `.env.template.example` est versionné ;
* `.env.template` est local et n’est jamais versionné ;
* `.env.dev` est versionné ;
* `.env.prod` est versionné ;
* `.env.local` n’est jamais versionné ;
* `.env` n’est jamais versionné ;
* `.env` doit être un lien symbolique vers `.env.dev` ou `.env.prod` ;
* `.env` ne doit jamais être modifié directement.

Le contenu canonique de `.env.template.example` est :

```env
APP_NAME=
APP_SLUG=
APP_DEPOT=
APP_NO=
ADMIN_USERNAME=
ADMIN_PASSWORD=
ADMIN_EMAIL=
```

`ADMIN_USERNAME`, `ADMIN_PASSWORD` et `ADMIN_EMAIL` servent au bootstrap initial puis doivent se retrouver dans `.env.local`.

---

### 3. Secrets

Les secrets doivent être définis uniquement dans `.env.local`.

Exemples :

```env
POSTGRES_PASSWORD=
DJANGO_SECRET_KEY=
ADMIN_USERNAME=
ADMIN_EMAIL=
ADMIN_PASSWORD=
CONTACT_API_TOKEN=
CALENDRIER_API_TOKEN=
```

Interdit :

* secret dans `.env.dev` ;
* secret dans `.env.prod` ;
* secret dans Git ;
* secret dans README, AGENTS.md ou CODEX_START.md.

---

### 3.1 Authentification inter-apps

Les appels backend vers backend entre applications auto-hebergees doivent utiliser une methode universelle basee sur `APP_DEPOT`.

#### Nom canonique du token local

Chaque application possede son propre token technique inter-apps.

Le nom canonique de ce token est :

```env
<APP_DEPOT_NORMALISE>_API_TOKEN=
```

Regle de normalisation de `APP_DEPOT` :

* convertir en majuscules ;
* remplacer tout caractere non alphanumerique par `_` ;
* ne jamais utiliser un nom metier specifique si un nom derive de `APP_DEPOT` est possible.

Exemples :

```env
APP_DEPOT=contact
CONTACT_API_TOKEN=

APP_DEPOT=calendrier
CALENDRIER_API_TOKEN=

APP_DEPOT=pense-bete
PENSE_BETE_API_TOKEN=
```

#### Regles obligatoires

* le token inter-apps d'une application appartient a l'application hote ;
* ce token doit etre defini uniquement dans `.env.local` ;
* `scripts/generate-secrets.sh` doit creer automatiquement le token local de l'application courante s'il est absent ;
* ce token local doit etre genere meme si l'application n'expose encore aucune API inter-apps ;
* une application cliente qui appelle une application hote doit stocker dans son propre `.env.local` une copie du token de l'hote, sous le meme nom canonique ;
* aucun token inter-apps ne doit etre stocke dans `.env.dev`, `.env.prod`, `.env.template`, `README.md`, `README_DEV.md`, `AGENTS.md` ou `CODEX_START.md`.

#### Variables non secretes associees

Les variables non secretes de connexion vers une application hote doivent suivre la meme convention basee sur `APP_DEPOT` :

```env
<HOST_DEPOT_NORMALISE>_API_BASE=
<HOST_DEPOT_NORMALISE>_API_TIMEOUT=
```

Exemple :

```env
CALENDRIER_API_BASE=
CALENDRIER_API_TIMEOUT=
```

#### En-tete HTTP universel

L'authentification technique inter-apps doit utiliser un en-tete HTTP universel :

```text
X-Internal-Api-Token
```

Regles :

* ne pas creer un nom d'en-tete specifique au metier ;
* ne pas creer un nom d'en-tete specifique a une paire d'applications ;
* l'identite metier utile au traitement applicatif doit etre transmise dans le payload, jamais deduite du token.

#### Portee

Cette methode universelle s'applique a toute future integration backend vers backend entre applications du meme ecosysteme.

---

### 4. PostgreSQL

Convention obligatoire :

```env
POSTGRES_USER=${APP_SLUG}_pg_user
POSTGRES_DB=${APP_SLUG}_pg_db
```

`POSTGRES_PASSWORD` doit rester dans `.env.local`.

---

### 5. Ports de développement

Les ports de développement sont dérivés de `APP_NO`.

Aucun port ne doit être choisi arbitrairement.

```text
DEV_DB_PORT   = 5432 + APP_NO
DEV_VITE_PORT = 5173 + APP_NO
DEV_API_PORT  = 8000 + (APP_NO + 1)
```

Exemple avec `APP_NO=4` :

```env
DEV_DB_PORT=5436
DEV_VITE_PORT=5177
DEV_API_PORT=8005
```

---

### 6. Docker Compose

Fichiers obligatoires :

```text
docker-compose.dev.yml
docker-compose.prod.yml
```

Services standards :

```text
db
backend
frontend
```

Les noms de services ne doivent pas être modifiés sans justification explicite.

---

### 7. Noms de conteneurs

Convention :

```text
${APP_SLUG}_${SERVICE}_${APP_ENV}
```

Exemples :

```text
con_db_dev
con_backend_dev
con_frontend_dev
```

---

### 8. Scripts obligatoires

Le dossier `scripts/` doit contenir exactement les 15 scripts standards du template applicatif :

```text
scripts/
├── backup-db.sh
├── check-invariants.sh
├── down.sh
├── env-switch.sh
├── generate-env.sh
├── generate-secrets.sh
├── init.sh
├── logs.sh
├── migrate.sh
├── ps.sh
├── rebuild.sh
├── restart.sh
├── restore-db.sh
├── up.sh
└── update.sh
```

Aucun script standard du template ne doit manquer ou être remplacé par une variante parallèle.
Le changement d’environnement doit se faire avec :

```bash
./scripts/env-switch.sh dev
./scripts/env-switch.sh prod
```

`init.sh` ne doit jamais modifier ce lien. Il doit utiliser l’environnement déjà pointé par `.env`, fonctionner aussi bien en `dev` qu’en `prod`, et pouvoir être relancé sans écraser les conteneurs déjà actifs.

### 9. Commandes Docker

Les commandes Docker Compose doivent passer par les scripts standards.

Commande de référence :

```bash
docker compose \
  --env-file .env \
  --env-file .env.local \
  -f docker-compose.${APP_ENV}.yml up
```

---

### 10. Frontend

Variable obligatoire :

```env
VITE_API_BASE=/api
```

Règles :

* pas d’URL backend absolue dans le code frontend ;
* pas de `localhost` codé dans le frontend ;
* le frontend appelle l’API via `/api`.

---

### 11. Backend

Règles :

* toutes les routes API doivent être sous `/api/` ;
* les routes privées doivent utiliser JWT ;
* le backend écoute dans le conteneur sur le port `8000` ;
* les données privées doivent être isolées par utilisateur.

---

### 12. Production

Règles :

* Traefik assure le routage public ;
* HTTPS est obligatoire ;
* les conteneurs applicatifs utilisent le réseau Docker externe `edge` ;
* `/api/` route vers le backend ;
* le frontend est servi par le service `frontend` ;
* aucun port applicatif ne doit être exposé publiquement sans justification.

---

### 13. Structure minimale

Structure attendue :

```text
.
├── AGENTS.md
├── backend
│   ├── api
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── App
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   ├── manage.py
│   └── requirements.txt
├── CODEX_START.md
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── frontend
│   ├── Dockerfile
│   ├── index.html
│   ├── node_modules
│   ├── package.json
│   └── src
│       ├── App.jsx
│       └── main.jsx
├── INVARIANTS.md
├── README_DEV.md
├── README.md
└── scripts
    ├── check-invariants.sh
    ├── down.sh
    ├── env-switch.sh
    ├── generate-env.sh
    ├── generate-secrets.sh
    ├── init.sh
    ├── logs.sh
    ├── ps.sh
    ├── restart.sh
    └── up.sh

8 directories, 34 files

```

---

### 14. Règles pour Codex

Codex doit respecter strictement ce fichier.

Interdictions :

* inventer des ports ;
* inventer des noms de services ;
* déplacer les secrets hors de `.env.local` ;
* coder une URL absolue dans le frontend ;
* modifier les conventions sans justification.

Obligations :

* lire `INVARIANTS.md` avant toute modification structurante ;
* respecter `APP_NAME`, `APP_SLUG`, `APP_DEPOT`, `APP_NO`, `APP_ENV` ;
* vérifier `.env.dev`, `.env.prod`, `.env.local.example`, `.gitignore` et Docker Compose.

---

### 15. Gitignore minimal

Le projet doit ignorer au minimum :

```gitignore
.env
.env.local
.env.template
*.bak
*.backup
*.tmp
__pycache__/
node_modules/
dist/
build/
.venv/
venv/
```

---

### 16. Règle finale

Ce fichier est la source d’autorité opérationnelle du projet.

La documentation Obsidian peut expliquer les règles, mais ne les remplace pas.

## Relation entre invariants globaux et invariants locaux

L’ordre d’autorité est le suivant :

1. `app-template/INVARIANTS.md` définit les règles globales.
2. Le profil d’application complète ces règles pour une famille technologique.
3. Le fichier `INVARIANTS.md` d’une application documente ses contraintes particulières.

Une application peut ajouter des règles locales, mais elle ne doit pas contredire un invariant global sans documenter explicitement l’écart.
