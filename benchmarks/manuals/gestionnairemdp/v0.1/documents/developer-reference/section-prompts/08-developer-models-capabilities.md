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
Titre de section : Modèles ou capacités démontrées
Identifiant de section : developer-models-capabilities
But : Présenter les modèles et capacités sans extrapolation.
Budget de contexte estimé : 3948/12288 tokens.
Produis uniquement la section demandée, sans titre de document global, sans conclusion générale et sans contenu hors sujet.
END INSTRUCTIONS

BEGIN SECTION FACTS
{
  "identifier": "developer-models-capabilities",
  "title": "Modèles ou capacités démontrées",
  "purpose": "Présenter les modèles et capacités sans extrapolation.",
  "facts": {
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
              "default": null,
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
              "default": null,
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "description",
              "field_type": "TextField",
              "required": false,
              "nullable": false,
              "blank": true,
              "default": "",
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
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
              "default": null,
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
              "default": null,
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "url",
              "field_type": "URLField",
              "required": false,
              "nullable": false,
              "blank": true,
              "default": "",
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "category",
              "field_type": "ForeignKey",
              "required": false,
              "nullable": true,
              "blank": true,
              "default": null,
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
              "default": null,
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "created_at",
              "field_type": "DateTimeField",
              "required": true,
              "nullable": false,
              "blank": false,
              "default": null,
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "updated_at",
              "field_type": "DateTimeField",
              "required": true,
              "nullable": false,
              "blank": false,
              "default": null,
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
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
              "default": null,
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
              "default": null,
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "environment",
              "field_type": "CharField",
              "required": true,
              "nullable": false,
              "blank": false,
              "default": null,
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "payload",
              "field_type": "JSONField",
              "required": false,
              "nullable": false,
              "blank": false,
              "default": "dict",
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "created_at",
              "field_type": "DateTimeField",
              "required": true,
              "nullable": false,
              "blank": false,
              "default": null,
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "updated_at",
              "field_type": "DateTimeField",
              "required": true,
              "nullable": false,
              "blank": false,
              "default": null,
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
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
    },
    "capabilities": {
      "capabilities": [
        {
          "label": "Aide",
          "status": "detected",
          "component": "AutofillHelp",
          "endpoint": null,
          "permission_condition": null,
          "confidence": "medium",
          "evidence": [
            "frontend/src/_archive/AutofillHelp.jsx"
          ]
        },
        {
          "label": "Changement de thème",
          "status": "detected",
          "component": "App",
          "endpoint": null,
          "permission_condition": null,
          "confidence": "medium",
          "evidence": [
            "frontend/src/App.jsx"
          ]
        },
        {
          "label": "Connexion",
          "status": "detected",
          "component": "App",
          "endpoint": "auth/jwt/create/",
          "permission_condition": null,
          "confidence": "high",
          "evidence": [
            "frontend/src/App.jsx",
            "/login",
            "POST auth/jwt/create/",
            "POST auth/jwt/logout/"
          ]
        },
        {
          "label": "Consulter les catégories",
          "status": "derived",
          "component": "CategoryGuide",
          "endpoint": "/api/categories/",
          "permission_condition": "IsOwner",
          "confidence": "high",
          "evidence": [
            "/api/categories/",
            "Category",
            "DELETE categories/{id}/",
            "DELETE passwords/{id}/"
          ]
        },
        {
          "label": "Consulter les entrées de mots de passe",
          "status": "derived",
          "component": "PasswordList",
          "endpoint": "/api/passwords/",
          "permission_condition": "IsOwner",
          "confidence": "high",
          "evidence": [
            "/api/passwords/",
            "PasswordEntry",
            "DELETE categories/{id}/",
            "DELETE passwords/{id}/"
          ]
        },
        {
          "label": "Consulter les secrets applicatifs",
          "status": "derived",
          "component": "KeyBackup",
          "endpoint": "/api/secrets/",
          "permission_condition": "IsAuthenticated",
          "confidence": "high",
          "evidence": [
            "/api/secrets/",
            "SecretBundle"
          ]
        },
        {
          "label": "Créer des catégories",
          "status": "derived",
          "component": "CategoryGuide",
          "endpoint": "/api/categories/",
          "permission_condition": "IsOwner",
          "confidence": "high",
          "evidence": [
            "/api/categories/",
            "Category",
            "DELETE categories/{id}/",
            "DELETE passwords/{id}/"
          ]
        },
        {
          "label": "Créer des entrées de mots de passe",
          "status": "derived",
          "component": "PasswordList",
          "endpoint": "/api/passwords/",
          "permission_condition": "IsOwner",
          "confidence": "high",
          "evidence": [
            "/api/passwords/",
            "PasswordEntry",
            "DELETE categories/{id}/",
            "DELETE passwords/{id}/"
          ]
        },
        {
          "label": "Créer des secrets applicatifs",
          "status": "derived",
          "component": "KeyBackup",
          "endpoint": "/api/secrets/",
          "permission_condition": "IsAuthenticated",
          "confidence": "high",
          "evidence": [
            "/api/secrets/",
            "SecretBundle"
          ]
        },
        {
          "label": "Exportation de clé",
          "status": "detected",
          "component": "App",
          "endpoint": "passwords/{id}/",
          "permission_condition": null,
          "confidence": "high",
          "evidence": [
            "frontend/src/App.jsx",
            "/vault/key-backup",
            "DELETE passwords/{id}/",
            "GET passwords/"
          ]
        },
        {
          "label": "Guide des catégories",
          "status": "detected",
          "component": "App",
          "endpoint": "categories/{id}/",
          "permission_condition": null,
          "confidence": "high",
          "evidence": [
            "frontend/src/App.jsx",
            "/vault/categories",
            "DELETE categories/{id}/",
            "GET categories/"
          ]
        },
        {
          "label": "Générateur de mots de passe",
          "status": "detected",
          "component": "PasswordEdit",
          "endpoint": "passwords/{id}/",
          "permission_condition": null,
          "confidence": "high",
          "evidence": [
            "frontend/src/components/PasswordEdit.jsx",
            "/vault/:id/edit",
            "/vault/new",
            "DELETE passwords/{id}/"
          ]
        },
        {
          "label": "Gérer un coffre local chiffré côté client",
          "status": "detected",
          "component": "frontend",
          "endpoint": null,
          "permission_condition": null,
          "confidence": "medium",
          "evidence": [
            "frontend/src/utils/crypto.js",
            "frontend/src/App.jsx"
          ]
        },
        {
          "label": "Importation de clé",
          "status": "detected",
          "component": "KeyCheck",
          "endpoint": "/login",
          "permission_condition": null,
          "confidence": "high",
          "evidence": [
            "frontend/src/components/KeyCheck.jsx",
            "/login",
            "/vault/key-backup",
            "/vault/key-check"
          ]
        },
        {
          "label": "Modifier des catégories",
          "status": "derived",
          "component": "CategoryGuide",
          "endpoint": "/api/categories/{id}/",
          "permission_condition": "IsOwner",
          "confidence": "high",
          "evidence": [
            "/api/categories/{id}/",
            "Category",
            "DELETE categories/{id}/",
            "DELETE passwords/{id}/"
          ]
        },
        {
          "label": "Modifier des entrées de mots de passe",
          "status": "derived",
          "component": "PasswordList",
          "endpoint": "/api/passwords/{id}/",
          "permission_condition": "IsOwner",
          "confidence": "high",
          "evidence": [
            "/api/passwords/{id}/",
            "PasswordEntry",
            "DELETE categories/{id}/",
            "DELETE passwords/{id}/"
          ]
        },
        {
          "label": "Modifier des secrets applicatifs",
          "status": "derived",
          "component": "KeyBackup",
          "endpoint": "/api/secrets/",
          "permission_condition": "IsAuthenticated",
          "confidence": "high",
          "evidence": [
            "/api/secrets/",
            "SecretBundle"
          ]
        },
        {
          "label": "Recherche",
          "status": "detected",
          "component": "CategorySelect",
          "endpoint": "categories/{id}/",
          "permission_condition": null,
          "confidence": "high",
          "evidence": [
            "frontend/src/components/CategorySelect.jsx",
            "/vault",
            "/vault/:id/edit",
            "/vault/categories"
          ]
        },
        {
          "label": "Révélation d’une valeur",
          "status": "detected",
          "component": "KeyCheck",
          "endpoint": "passwords/{id}/",
          "permission_condition": null,
          "confidence": "high",
          "evidence": [
            "frontend/src/components/KeyCheck.jsx",
            "/vault",
            "/vault/:id/edit",
            "/vault/categories"
          ]
        },
        {
          "label": "Supprimer des catégories",
          "status": "derived",
          "component": "CategoryGuide",
          "endpoint": "/api/categories/{id}/",
          "permission_condition": "IsOwner",
          "confidence": "high",
          "evidence": [
            "/api/categories/{id}/",
            "Category",
            "DELETE categories/{id}/",
            "DELETE passwords/{id}/"
          ]
        },
        {
          "label": "Supprimer des entrées de mots de passe",
          "status": "derived",
          "component": "PasswordList",
          "endpoint": "/api/passwords/{id}/",
          "permission_condition": "IsOwner",
          "confidence": "high",
          "evidence": [
            "/api/passwords/{id}/",
            "PasswordEntry",
            "DELETE categories/{id}/",
            "DELETE passwords/{id}/"
          ]
        },
        {
          "label": "Supprimer des secrets applicatifs",
          "status": "derived",
          "component": "KeyBackup",
          "endpoint": "/api/secrets/",
          "permission_condition": "IsAuthenticated",
          "confidence": "high",
          "evidence": [
            "/api/secrets/",
            "SecretBundle"
          ]
        },
        {
          "label": "S’authentifier à l’application",
          "status": "derived",
          "component": null,
          "endpoint": "/api/auth/jwt/create/",
          "permission_condition": null,
          "confidence": "high",
          "evidence": [
            "/api/auth/jwt/create/"
          ]
        },
        {
          "label": "Vérification de clé",
          "status": "detected",
          "component": "App",
          "endpoint": "/vault/key-check",
          "permission_condition": null,
          "confidence": "high",
          "evidence": [
            "frontend/src/App.jsx",
            "/vault/key-check"
          ]
        }
      ]
    }
  }
}
END SECTION FACTS
