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
Ce guide est destiné à l’exploitant. Les tableaux déterministes de services, cibles Make, variables et documents protégés constituent la référence technique à conserver telle quelle.
Ne transforme jamais les noms de variables de configuration en valeurs ou en secrets.
Titre de section : Migrations et administration
Identifiant de section : operator-migrations-administration
But : Présenter les faits démontrés de migrations et d’administration.
Budget de contexte estimé : 5239/12288 tokens.
Produis uniquement la section demandée, sans titre de document global, sans conclusion générale et sans contenu hors sujet.
END INSTRUCTIONS

BEGIN SECTION FACTS
{
  "identifier": "operator-migrations-administration",
  "title": "Migrations et administration",
  "purpose": "Présenter les faits démontrés de migrations et d’administration.",
  "facts": {
    "operational_commands": {
      "primary_commands": [
        {
          "name": "ps",
          "category": "diagnostic",
          "command_path": "make ps",
          "audience": "operator",
          "reference_level": "primary",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "template-standard",
          "documentation_policy": "main-reference",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "dev",
          "category": "environment",
          "command_path": "make dev",
          "audience": "operator",
          "reference_level": "primary",
          "environment": [
            "dev"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "template-standard",
          "documentation_policy": "quick-start",
          "prerequisites": [],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "logs",
          "category": "logs",
          "command_path": "make logs",
          "audience": "operator",
          "reference_level": "primary",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "template-standard",
          "documentation_policy": "main-reference",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "migrate",
          "category": "migrations",
          "command_path": "make migrate",
          "audience": "operator",
          "reference_level": "primary",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "template-standard",
          "documentation_policy": "main-reference",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [
            "Migration ou modification du schéma ou de l’état de la base de données"
          ],
          "parameters": []
        },
        {
          "name": "help",
          "category": "other",
          "command_path": "make help",
          "audience": "operator",
          "reference_level": "primary",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "application-public",
          "documentation_policy": "main-reference",
          "prerequisites": [],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "restart",
          "category": "restart",
          "command_path": "make restart",
          "audience": "operator",
          "reference_level": "primary",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "template-standard",
          "documentation_policy": "main-reference",
          "prerequisites": [
            "env-check"
          ],
          "destructive": true,
          "destructive_effects": [
            "Arrêt des services actifs"
          ],
          "parameters": []
        },
        {
          "name": "init",
          "category": "setup",
          "command_path": "make init",
          "audience": "operator",
          "reference_level": "primary",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "template-standard",
          "documentation_policy": "quick-start",
          "prerequisites": [],
          "destructive": false,
          "destructive_effects": [
            "Initialisation de l’environnement de travail"
          ],
          "parameters": []
        },
        {
          "name": "down",
          "category": "shutdown",
          "command_path": "make down",
          "audience": "operator",
          "reference_level": "primary",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "template-standard",
          "documentation_policy": "main-reference",
          "prerequisites": [
            "env-check"
          ],
          "destructive": true,
          "destructive_effects": [
            "Arrêt des services actifs"
          ],
          "parameters": []
        },
        {
          "name": "up",
          "category": "startup",
          "command_path": "make up",
          "audience": "operator",
          "reference_level": "primary",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "template-standard",
          "documentation_policy": "quick-start",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [
            "Démarrage des services définis par le projet"
          ],
          "parameters": []
        }
      ],
      "advanced_commands": [
        {
          "name": "backup",
          "category": "backup",
          "command_path": "make backup",
          "audience": "operator",
          "reference_level": "advanced",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "template-standard",
          "documentation_policy": "advanced-reference",
          "prerequisites": [],
          "destructive": false,
          "destructive_effects": [
            "Création d’un artefact de sauvegarde de base de données"
          ],
          "parameters": []
        },
        {
          "name": "rebuild",
          "category": "build",
          "command_path": "make rebuild",
          "audience": "operator",
          "reference_level": "advanced",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "template-standard",
          "documentation_policy": "advanced-reference",
          "prerequisites": [
            "env-check"
          ],
          "destructive": true,
          "destructive_effects": [
            "Reconstruction des images ou services"
          ],
          "parameters": []
        },
        {
          "name": "update",
          "category": "build",
          "command_path": "make update",
          "audience": "operator",
          "reference_level": "advanced",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "application-public",
          "documentation_policy": "advanced-reference",
          "prerequisites": [],
          "destructive": true,
          "destructive_effects": [
            "Reconstruction des images ou services"
          ],
          "parameters": []
        },
        {
          "name": "check",
          "category": "diagnostic",
          "command_path": "make check",
          "audience": "operator",
          "reference_level": "advanced",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "template-standard",
          "documentation_policy": "advanced-reference",
          "prerequisites": [],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "prod",
          "category": "environment",
          "command_path": "make prod",
          "audience": "operator",
          "reference_level": "advanced",
          "environment": [
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "template-standard",
          "documentation_policy": "advanced-reference",
          "prerequisites": [],
          "destructive": false,
          "destructive_effects": [
            "Sélection de l’environnement de production"
          ],
          "parameters": []
        },
        {
          "name": "restore",
          "category": "restore",
          "command_path": "make restore",
          "audience": "operator",
          "reference_level": "advanced",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "template-standard",
          "documentation_policy": "advanced-reference",
          "prerequisites": [],
          "destructive": true,
          "destructive_effects": [
            "Modification ou écrasement potentiel des données PostgreSQL"
          ],
          "parameters": [
            {
              "name": "FILE",
              "required": false,
              "allowed_values": [],
              "origin": "user-exposed"
            }
          ]
        }
      ],
      "excluded_commands_summary": {
        "total": 56,
        "by_provenance": {
          "internal": 7,
          "legacy": 8,
          "unknown": 37,
          "developer-public": 4
        },
        "reasons": [
          {
            "reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
            "count": 37
          },
          {
            "reason": "Alias ou compatibilité historique non retenu dans la référence principale.",
            "count": 8
          },
          {
            "reason": "Helper interne ou garde-fou auxiliaire non retenu dans la référence utilisateur.",
            "count": 7
          },
          {
            "reason": "Aucune raison d’exclusion documentée.",
            "count": 4
          }
        ],
        "commands": [
          {
            "name": "exec-vite",
            "provenance": "internal",
            "reason": "Helper interne ou garde-fou auxiliaire non retenu dans la référence utilisateur."
          },
          {
            "name": "pull-secret-all-remote",
            "provenance": "legacy",
            "reason": "Alias ou compatibilité historique non retenu dans la référence principale."
          },
          {
            "name": "pull-secret-single",
            "provenance": "legacy",
            "reason": "Alias ou compatibilité historique non retenu dans la référence principale."
          },
          {
            "name": "push-secret-all-remote",
            "provenance": "legacy",
            "reason": "Alias ou compatibilité historique non retenu dans la référence principale."
          },
          {
            "name": "push-secret-single",
            "provenance": "legacy",
            "reason": "Alias ou compatibilité historique non retenu dans la référence principale."
          },
          {
            "name": "backup-db",
            "provenance": "unknown",
            "reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative."
          },
          {
            "name": "backup-env",
            "provenance": "unknown",
            "reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative."
          },
          {
            "name": "pull-prod-backup",
            "provenance": "unknown",
            "reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative."
          },
          {
            "name": "create-env",
            "provenance": "unknown",
            "reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative."
          },
          {
            "name": "env-check",
            "provenance": "unknown",
            "reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative."
          },
          {
            "name": "env-check-base",
            "provenance": "internal",
            "reason": "Helper interne ou garde-fou auxiliaire non retenu dans la référence utilisateur."
          },
          {
            "name": "env-check-local",
            "provenance": "internal",
            "reason": "Helper interne ou garde-fou auxiliaire non retenu dans la référence utilisateur."
          }
        ]
      }
    },
    "workflows": [
      {
        "identifier": "prepare-dev-config",
        "title": "Préparer la configuration de développement",
        "summary": "Sélectionner le mode dev puis initialiser les fichiers d’environnement.",
        "commands": [
          "make dev",
          "make init"
        ],
        "operational_status": "operational",
        "notes": []
      },
      {
        "identifier": "start-development",
        "title": "Démarrer le développement",
        "summary": "Sélectionner l’environnement dev puis démarrer les services.",
        "commands": [
          "make dev",
          "make up"
        ],
        "operational_status": "operational",
        "notes": []
      },
      {
        "identifier": "apply-migrations",
        "title": "Appliquer les migrations",
        "summary": "Exécuter la procédure de migration détectée.",
        "commands": [
          "make migrate"
        ],
        "operational_status": "operational",
        "notes": []
      },
      {
        "identifier": "create-admin",
        "title": "Créer un administrateur",
        "summary": "La création d’un administrateur est exposée par une commande opérationnelle détectée.",
        "commands": [
          "make createsuperuser"
        ],
        "operational_status": "operational",
        "notes": []
      },
      {
        "identifier": "open-frontend",
        "title": "Ouvrir le frontend",
        "summary": "Démarrer les services puis ouvrir le frontend détecté.",
        "commands": [
          "make dev",
          "make up"
        ],
        "operational_status": "operational",
        "notes": [
          "URL détectée : http://localhost:${DEV_VITE_PORT:-5174}"
        ]
      },
      {
        "identifier": "open-django-admin",
        "title": "Accéder à l’administration Django",
        "summary": "Démarrer les services puis ouvrir l’administration détectée.",
        "commands": [
          "make up"
        ],
        "operational_status": "operational",
        "notes": [
          "URL détectée : http://localhost:${DEV_API_PORT:-8002}/admin/"
        ]
      },
      {
        "identifier": "view-logs",
        "title": "Consulter les journaux",
        "summary": "Afficher les logs des services actifs.",
        "commands": [
          "make logs"
        ],
        "operational_status": "operational",
        "notes": []
      },
      {
        "identifier": "run-tests",
        "title": "Lancer les tests",
        "summary": "Une commande opérationnelle agrège les suites de tests démontrées pour l’application.",
        "commands": [
          "make test"
        ],
        "operational_status": "operational",
        "notes": [
          "`make check` reste une vérification d’invariants ou de diagnostic et n’est pas utilisé comme workflow de tests."
        ]
      },
      {
        "identifier": "stop-services",
        "title": "Arrêter les services",
        "summary": "Arrêter les services de l’environnement actif.",
        "commands": [
          "make down"
        ],
        "operational_status": "operational",
        "notes": []
      },
      {
        "identifier": "rebuild-images",
        "title": "Reconstruire les images",
        "summary": "Reconstruire les images Docker de l’environnement actif.",
        "commands": [
          "make rebuild"
        ],
        "operational_status": "operational",
        "notes": []
      },
      {
        "identifier": "prepare-production",
        "title": "Préparer la production",
        "summary": "Sélectionner prod puis initialiser les fichiers requis.",
        "commands": [
          "make prod",
          "make init"
        ],
        "operational_status": "operational",
        "notes": []
      },
      {
        "identifier": "start-production",
        "title": "Démarrer la production",
        "summary": "Sélectionner prod puis démarrer les services.",
        "commands": [
          "make prod",
          "make up"
        ],
        "operational_status": "operational",
        "notes": []
      },
      {
        "identifier": "backup-database",
        "title": "Sauvegarder la base",
        "summary": "Créer une sauvegarde PostgreSQL via la commande détectée.",
        "commands": [
          "make backup"
        ],
        "operational_status": "operational",
        "notes": []
      },
      {
        "identifier": "restore-database",
        "title": "Restaurer la base",
        "summary": "Restaurer une sauvegarde PostgreSQL via la commande détectée.",
        "commands": [
          "make restore"
        ],
        "operational_status": "operational",
        "notes": []
      }
    ],
    "django": {
      "settings_module": "gestionnaire_mdp.settings",
      "urlconf_module": "gestionnaire_mdp.urls",
      "installed_apps": [
        "api",
        "corsheaders",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.messages",
        "django.contrib.sessions",
        "django.contrib.staticfiles",
        "rest_framework",
        "rest_framework_simplejwt.token_blacklist"
      ],
      "admin_enabled": true,
      "routers": [
        "/categories",
        "/passwords"
      ],
      "auth_mechanisms": [
        "Bearer token",
        "JWT",
        "SimpleJWT"
      ],
      "models": [
        {
          "name": "Category",
          "fields": [
            "owner",
            "name",
            "description"
          ],
          "source": "backend/api/models.py"
        },
        {
          "name": "PasswordEntry",
          "fields": [
            "owner",
            "title",
            "url",
            "category",
            "ciphertext",
            "created_at",
            "updated_at"
          ],
          "source": "backend/api/models.py"
        },
        {
          "name": "SecretBundle",
          "fields": [
            "owner",
            "app",
            "environment",
            "payload",
            "created_at",
            "updated_at"
          ],
          "source": "backend/api/models.py"
        }
      ],
      "model_schemas": [
        {
          "name": "Category",
          "fields": [
            {
              "name": "owner",
              "field_type": "ForeignKey",
              "required": true,
              "nullable": false,
              "blank": false,
              "choices": [],
              "relation": "settings.AUTH_USER_MODEL",
              "unique": false,
              "on_delete": "models.CASCADE"
            },
            {
              "name": "name",
              "field_type": "CharField",
              "required": true,
              "nullable": false,
              "blank": false,
              "choices": [],
              "unique": false
            },
            {
              "name": "description",
              "field_type": "TextField",
              "required": false,
              "nullable": false,
              "blank": true,
              "default": "",
              "choices": [],
              "unique": false
            }
          ]
        },
        {
          "name": "PasswordEntry",
          "fields": [
            {
              "name": "owner",
              "field_type": "ForeignKey",
              "required": true,
              "nullable": false,
              "blank": false,
              "choices": [],
              "relation": "settings.AUTH_USER_MODEL",
              "unique": false,
              "on_delete": "models.CASCADE"
            },
            {
              "name": "title",
              "field_type": "CharField",
              "required": true,
              "nullable": false,
              "blank": false,
              "choices": [],
              "unique": false
            },
            {
              "name": "url",
              "field_type": "URLField",
              "required": false,
              "nullable": false,
              "blank": true,
              "default": "",
              "choices": [],
              "unique": false
            },
            {
              "name": "category",
              "field_type": "ForeignKey",
              "required": false,
              "nullable": true,
              "blank": true,
              "choices": [],
              "relation": "Category",
              "unique": false,
              "on_delete": "models.SET_NULL"
            },
            {
              "name": "ciphertext",
              "field_type": "JSONField",
              "required": true,
              "nullable": false,
              "blank": false,
              "choices": [],
              "unique": false
            },
            {
              "name": "created_at",
              "field_type": "DateTimeField",
              "required": true,
              "nullable": false,
              "blank": false,
              "choices": [],
              "unique": false
            },
            {
              "name": "updated_at",
              "field_type": "DateTimeField",
              "required": true,
              "nullable": false,
              "blank": false,
              "choices": [],
              "unique": false
            }
          ]
        },
        {
          "name": "SecretBundle",
          "fields": [
            {
              "name": "owner",
              "field_type": "ForeignKey",
              "required": true,
              "nullable": false,
              "blank": false,
              "choices": [],
              "relation": "settings.AUTH_USER_MODEL",
              "unique": false,
              "on_delete": "models.CASCADE"
            },
            {
              "name": "app",
              "field_type": "CharField",
              "required": true,
              "nullable": false,
              "blank": false,
              "choices": [],
              "unique": false
            },
            {
              "name": "environment",
              "field_type": "CharField",
              "required": true,
              "nullable": false,
              "blank": false,
              "choices": [],
              "unique": false
            },
            {
              "name": "payload",
              "field_type": "JSONField",
              "required": false,
              "nullable": false,
              "blank": false,
              "default": "dict",
              "choices": [],
              "unique": false
            },
            {
              "name": "created_at",
              "field_type": "DateTimeField",
              "required": true,
              "nullable": false,
              "blank": false,
              "choices": [],
              "unique": false
            },
            {
              "name": "updated_at",
              "field_type": "DateTimeField",
              "required": true,
              "nullable": false,
              "blank": false,
              "choices": [],
              "unique": false
            }
          ]
        }
      ],
      "endpoints": [
        {
          "path": "/admin/",
          "methods": [],
          "view": "urls",
          "permissions": [],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/auth/jwt/create/",
          "methods": [
            "POST"
          ],
          "view": "TokenObtainPairView",
          "permissions": [],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/auth/jwt/logout/",
          "methods": [
            "POST"
          ],
          "view": "JWTLogoutView",
          "permissions": [
            "IsAuthenticated"
          ],
          "authentication": [
            "JWT",
            "Bearer token"
          ],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/auth/jwt/refresh/",
          "methods": [],
          "view": "TokenRefreshView",
          "permissions": [],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/auth/jwt/verify/",
          "methods": [],
          "view": "TokenVerifyView",
          "permissions": [],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/auth/session/csrf/",
          "methods": [],
          "view": "csrf",
          "permissions": [],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/auth/session/login/",
          "methods": [],
          "view": "login_view",
          "permissions": [],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/auth/session/logout/",
          "methods": [],
          "view": "logout_view",
          "permissions": [],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/auth/session/whoami/",
          "methods": [],
          "view": "whoami",
          "permissions": [],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/auth/whoami/",
          "methods": [],
          "view": "jwt_whoami",
          "permissions": [
            "IsAuthenticated"
          ],
          "authentication": [
            "JWTAuthentication"
          ],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/categories/",
          "methods": [
            "GET",
            "POST"
          ],
          "view": "CategoryViewSet",
          "permissions": [
            "IsOwner"
          ],
          "authentication": [
            "JWT",
            "Bearer token"
          ],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [
            "owner scoped to request.user",
            "owner assigned server-side"
          ],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/categories/{id}/",
          "methods": [
            "GET",
            "PUT",
            "PATCH",
            "DELETE"
          ],
          "view": "CategoryViewSet",
          "permissions": [
            "IsOwner"
          ],
          "authentication": [
            "JWT",
            "Bearer token"
          ],
          "actions": [],
          "route_parameters": [
            "id"
          ],
          "ownership_controls": [
            "owner scoped to request.user",
            "owner assigned server-side"
          ],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/csrf/",
          "methods": [],
          "view": "csrf",
          "permissions": [],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/healthz/",
          "methods": [],
          "view": "healthz",
          "permissions": [],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/login/",
          "methods": [],
          "view": "login_view",
          "permissions": [],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/logout/",
          "methods": [],
          "view": "logout_view",
          "permissions": [],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/passwords/",
          "methods": [
            "GET",
            "POST"
          ],
          "view": "PasswordViewSet",
          "permissions": [
            "IsOwner"
          ],
          "authentication": [
            "JWT",
            "Bearer token"
          ],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [
            "owner scoped to request.user",
            "owner assigned server-side"
          ],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/passwords/{id}/",
          "methods": [
            "GET",
            "PUT",
            "PATCH",
            "DELETE"
          ],
          "view": "PasswordViewSet",
          "permissions": [
            "IsOwner"
          ],
          "authentication": [
            "JWT",
            "Bearer token"
          ],
          "actions": [],
          "route_parameters": [
            "id"
          ],
          "ownership_controls": [
            "owner scoped to request.user",
            "owner assigned server-side"
          ],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/secrets/",
          "methods": [
            "GET",
            "POST",
            "PUT",
            "DELETE"
          ],
          "view": "SecretsView",
          "permissions": [
            "IsAuthenticated"
          ],
          "authentication": [
            "JWT",
            "Bearer token"
          ],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/whoami/",
          "methods": [],
          "view": "jwt_whoami",
          "permissions": [
            "IsAuthenticated"
          ],
          "authentication": [
            "JWTAuthentication"
          ],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        }
      ]
    }
  }
}
END SECTION FACTS
