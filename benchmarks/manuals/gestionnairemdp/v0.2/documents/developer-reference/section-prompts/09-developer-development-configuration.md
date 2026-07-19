BEGIN INSTRUCTIONS
Rédige un document Markdown fidèle aux faits fournis.
Utilise `manual-knowledge.json` comme source unique de vérité et n’utilise aucune connaissance externe pour compléter les procédures ou les caractéristiques du projet.
Suis strictement le blueprint fourni.
N’invente jamais une commande, une option, une procédure, une route, une URL, un paramètre, une variable, un service ou une fonctionnalité.
N’ajoute pas de bonnes pratiques générales comme si elles étaient démontrées par le projet.
Utilise `command_path` pour identifier ou titrer une commande.
Utilise `invocation` pour toute commande destinée à être copiée et exécutée.
Ne reconstruis jamais une syntaxe de commande à partir de `name` seul.
Les blocs Markdown déterministes fournis séparément sont la seule source des commandes exécutables, de leurs paramètres et des chemins de configuration; ne les répète, ne les reformule et ne les complète jamais.
Rédige uniquement l’explication narrative qui accompagne les blocs déterministes.
Conserve les statuts `detected`, `derived`, `configured` et `unresolved` dans leur sens : une configuration n’est jamais présentée comme un comportement observé automatiquement.
Ne cite que les options et paramètres associés à la commande dans ManualKnowledge.
Vérifie silencieusement chaque commande, paramètre, route, URL, variable, service, permission, workflow et champ cité avant de rédiger; cette vérification ne doit pas apparaître dans le manuel.
Signale explicitement les informations manquantes et les limites sans reconstruire arbitrairement des faits absents.
Ne produis jamais de chemin local propre à une machine.
N’ajoute jamais de référence de citation interne comme `oaicite`.
N’expose jamais de secret ni de valeur sensible; seuls les noms non sensibles ou les noms de variables peuvent être cités.
Ne cite aucun nom concret de fichier sensible, de plateforme ou de mécanisme d’automatisation à titre d’exemple : il doit être présent dans les faits de cette section et démontré par le profil courant.
Retourne uniquement le Markdown du manuel.
Interprétation des statuts de faits : `detected` = fait directement démontré et pouvant être présenté comme établi.
`derived` = fait déduit d’éléments compatibles; emploie une formulation prudente et ne le présente jamais comme un comportement testé en fonctionnement.
`configured` = fait provenant du profil ou de la configuration DocForge; présente-le comme règle documentaire ou configuration du pipeline, pas comme comportement applicatif observé.
`unresolved` = fait incomplet; n’invente jamais la partie manquante et signale la limite dans la section appropriée.
Le manuel doit être en français, clair, pédagogique, concret, professionnel et orienté utilisateur.
Ne transcris pas mécaniquement le JSON et ne mentionne pas inutilement les noms internes des dataclasses.
Réduis les répétitions : le démarrage rapide reste court, la référence des commandes porte les détails, et les autres sections évitent de recopier des listes complètes sans nécessité.
Le manuel concerne l’application analysée ou le dépôt modèle analysé, jamais DocForge comme produit utilisateur.
Les commandes DocForge ne sont pas des commandes d’utilisation de l’application analysée.
Formule prudemment toute capacité marquée `derived` et ne la présente jamais comme validée en fonctionnement.
N’affiche jamais une valeur secrète.
Omet toute procédure dont une commande critique est absente.
Utilise `missing_information` et `limitations.items` comme source prioritaire pour la section des limites, sans reconstruire arbitrairement les absences depuis le JSON brut.
Les mentions locales d’une information manquante doivent rester limitées aux cas où elles sont nécessaires à la sécurité ou à l’exécution; consolide le reste dans la section finale des limites.
Lorsqu’un conflit structuré est présent dans `conflicts`, présente-le clairement, n’arbitre jamais entre les valeurs contradictoires et ne décris pas comme validée une procédure affectée par ce conflit.
Pour les routes Django, utilise uniquement `full_path` lorsque `resolution_status` vaut `resolved`; ne compose jamais manuellement un chemin public à partir d’une route relative non résolue.
Une URL syntaxiquement invalide ou contenant une interpolation déséquilibrée ne doit jamais être présentée comme URL d’accès opérationnelle.
Pour les endpoints, utilise les méthodes, permissions, mécanismes d’authentification, paramètres de route et sources rattachés à chaque endpoint; n’attribue jamais des permissions globales à tous les endpoints ou à tous les utilisateurs.
Respecte `workflows.operational_status` : un workflow `requires-context` ne doit jamais être présenté comme immédiatement exécutable et doit garder son contexte manquant explicite.
Lorsqu’une cible alias délègue à des prérequis démontrés, décris l’alias à partir de cette délégation au lieu d’inventer un corps absent.
Ne présente jamais `make check` comme une suite de tests lorsqu’il correspond à une vérification d’invariants ou de diagnostic.
Associe `make migrate` à la création ou mise à jour de l’administrateur uniquement si la chaîne démontrée vers `python manage.py ensure_admin` est explicitement présente dans ManualKnowledge.
Pour les commandes Make, respecte les paramètres structurés de `commands.parameters`, leur caractère facultatif et leurs exemples; n’invente ni nouveaux paramètres ni nouvelles valeurs de service.
Les paramètres internes d’une commande ne doivent jamais être présentés comme arguments utilisateur; n’utilise que les paramètres structurés réellement exposés dans `commands.parameters`.
Pour la base de données, respecte les contextes fournis par ManualKnowledge, par exemple exécution vs test; ne transforme pas automatiquement une différence de contexte en contradiction.
Les métadonnées de `django.models.fields` priment sur toute intuition: type, `required`, `null`, `blank`, `default`, `choices`, relation, unicité et autres contraintes détectées doivent être utilisées telles quelles.
Pour `react.crypto`, décris uniquement l’implémentation détectée et jamais une garantie de sécurité, un audit, une récupération existante ou un modèle zero knowledge non démontré.
En mode strict, n’ajoute pas de recommandations générales de sécurité si elles ne figurent pas dans ManualKnowledge.
Le document final doit rester lisible: le démarrage rapide est court, l’exploitation détaille les procédures nécessaires, et la référence des commandes évite de dupliquer les listes dans toutes les sections.
Les helpers internes du Makefile ne doivent pas encombrer la référence principale; privilégie les commandes publiques, documentées ou réellement utilisées dans les workflows démontrés.
N’expose pas dans le manuel final un vocabulaire interne ni les identifiants techniques des structures de génération.
Transforme toujours les identifiants techniques de limites ou d’informations manquantes en phrases lisibles, par exemple `PROJECT-VERSION-MISSING` devient une phrase telle que la version de l’application n’est pas indiquée.
Lorsque `conflicts` est vide, n’ajoute pas une phrase de remplissage disant qu’aucune contradiction n’est signalée.
Cette référence est destinée au développement et à la maintenance. Les routes résolues et les invariants démontrés y sont documentés, sans inventer de contrat API ou de procédure de mise en production.
Les noms de variables sont autorisés; leurs valeurs ne le sont jamais.
Titre de section : Configuration de développement
Identifiant de section : developer-development-configuration
But : Présenter les noms de variables et l’environnement de développement.
Budget de contexte estimé : 867/12288 tokens.
Produis uniquement la section demandée, sans titre de document global, sans conclusion générale et sans contenu hors sujet.
END INSTRUCTIONS

BEGIN SECTION FACTS
{
  "identifier": "developer-development-configuration",
  "title": "Configuration de développement",
  "purpose": "Présenter les noms de variables et l’environnement de développement.",
  "facts": {
    "environment_variables": {
      "variables": [
        {
          "name": "ADMIN_EMAIL",
          "sensitive": false
        },
        {
          "name": "ADMIN_PASSWORD",
          "sensitive": true
        },
        {
          "name": "ADMIN_USERNAME",
          "sensitive": false
        },
        {
          "name": "ALLOWED_HOSTS",
          "sensitive": false
        },
        {
          "name": "APP_DEPOT",
          "sensitive": false
        },
        {
          "name": "APP_ENV",
          "sensitive": false
        },
        {
          "name": "APP_HOST",
          "sensitive": false
        },
        {
          "name": "APP_NAME",
          "sensitive": false
        },
        {
          "name": "APP_NO",
          "sensitive": false
        },
        {
          "name": "APP_SLUG",
          "sensitive": false
        },
        {
          "name": "CORS_ALLOWED_ORIGINS",
          "sensitive": false
        },
        {
          "name": "CSRF_TRUSTED_ORIGINS",
          "sensitive": false
        },
        {
          "name": "DEV_API_PORT",
          "sensitive": false
        },
        {
          "name": "DEV_DB_PORT",
          "sensitive": false
        },
        {
          "name": "DEV_VITE_PORT",
          "sensitive": false
        },
        {
          "name": "DJANGO_DEBUG",
          "sensitive": false
        },
        {
          "name": "DJANGO_SECRET_KEY",
          "sensitive": true
        },
        {
          "name": "FRONT_ORIGIN",
          "sensitive": false
        },
        {
          "name": "POSTGRES_DB",
          "sensitive": false
        },
        {
          "name": "POSTGRES_HOST",
          "sensitive": false
        },
        {
          "name": "POSTGRES_PASSWORD",
          "sensitive": true
        },
        {
          "name": "POSTGRES_PORT",
          "sensitive": false
        },
        {
          "name": "POSTGRES_USER",
          "sensitive": false
        },
        {
          "name": "PROD_API_BIND",
          "sensitive": false
        },
        {
          "name": "PROD_API_PORT",
          "sensitive": false
        },
        {
          "name": "PROD_DB_BIND",
          "sensitive": false
        },
        {
          "name": "PROD_DB_PORT",
          "sensitive": false
        },
        {
          "name": "PROD_FRONT_BIND",
          "sensitive": false
        },
        {
          "name": "PROD_FRONT_PORT",
          "sensitive": false
        },
        {
          "name": "TRAEFIK_DOCKER_NETWORK",
          "sensitive": false
        },
        {
          "name": "VITE_API_BASE",
          "sensitive": false
        }
      ]
    },
    "environments": {
      "items": [
        {
          "name": "dev",
          "compose_file": "docker-compose.dev.yml",
          "env_files": [
            ".env.dev",
            ".env.local"
          ],
          "urls": [
            "http://localhost:${DEV_API_PORT:-8002}/admin/",
            "http://localhost:${DEV_API_PORT:-8002}/api/",
            "http://localhost:${DEV_VITE_PORT:-5174}"
          ],
          "services": [
            {
              "name": "backend",
              "role": "backend",
              "image": "${APP_SLUG}-backend:dev",
              "ports": [
                "${DEV_API_PORT:-8002}:8000"
              ],
              "depends_on": [
                "db"
              ],
              "networks": [
                "appnet"
              ],
              "volumes": [
                "./backend:/app"
              ]
            },
            {
              "name": "db",
              "role": "database",
              "image": "postgres:16-alpine",
              "ports": [
                "${DEV_DB_PORT:-5433}:5432"
              ],
              "depends_on": [],
              "networks": [
                "appnet"
              ],
              "volumes": [
                "pgdata:/var/lib/postgresql/data"
              ]
            },
            {
              "name": "frontend",
              "role": "frontend",
              "image": "node:20-alpine",
              "ports": [
                "${DEV_VITE_PORT:-5174}:5173"
              ],
              "depends_on": [
                "backend"
              ],
              "networks": [
                "appnet"
              ],
              "volumes": [
                "./frontend:/app",
                "node_modules:/app/node_modules"
              ]
            }
          ]
        },
        {
          "name": "prod",
          "compose_file": "docker-compose.prod.yml",
          "env_files": [
            ".env.local",
            ".env.prod"
          ],
          "urls": [
            "https://mdp.mon-site.ca",
            "https://mdp.mon-site.ca/admin/",
            "https://mdp.mon-site.ca/api/"
          ],
          "services": [
            {
              "name": "backend",
              "role": "backend",
              "image": "${APP_SLUG}-backend:prod",
              "ports": [
                "${PROD_API_BIND:-127.0.0.1}:${PROD_API_PORT:-8000}:8000"
              ],
              "depends_on": [
                "db"
              ],
              "networks": [
                "appnet",
                "edge"
              ],
              "volumes": []
            },
            {
              "name": "db",
              "role": "database",
              "image": "postgres:16-alpine",
              "ports": [
                "${PROD_DB_BIND:-127.0.0.1}:${PROD_DB_PORT:-5432}:5432"
              ],
              "depends_on": [],
              "networks": [
                "appnet"
              ],
              "volumes": [
                "pgdata:/var/lib/postgresql/data"
              ]
            },
            {
              "name": "frontend",
              "role": "frontend",
              "image": "${APP_SLUG}-frontend:prod",
              "ports": [
                "${PROD_FRONT_BIND:-127.0.0.1}:${PROD_FRONT_PORT:-8080}:80"
              ],
              "depends_on": [
                "backend"
              ],
              "networks": [
                "edge"
              ],
              "volumes": []
            }
          ]
        }
      ]
    }
  }
}
END SECTION FACTS
