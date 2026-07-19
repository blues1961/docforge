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
Titre de section : Routes et API
Identifiant de section : developer-routes-api
But : Fournir le tableau déterministe des routes et API résolues.
Budget de contexte estimé : 2792/12288 tokens.
Produis uniquement la section demandée, sans titre de document global, sans conclusion générale et sans contenu hors sujet.
END INSTRUCTIONS

BEGIN SECTION FACTS
{
  "identifier": "developer-routes-api",
  "title": "Routes et API",
  "purpose": "Fournir le tableau déterministe des routes et API résolues.",
  "facts": {
    "django": {
      "settings_module": "calendar_project.settings",
      "urlconf_module": "calendar_project.urls",
      "installed_apps": [
        "calendar_api",
        "corsheaders",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.messages",
        "django.contrib.sessions",
        "django.contrib.staticfiles",
        "rest_framework"
      ],
      "admin_enabled": true,
      "routers": [
        "/calendars",
        "/events"
      ],
      "auth_mechanisms": [
        "Bearer token",
        "JWT",
        "SimpleJWT"
      ],
      "models": [
        {
          "name": "Calendar",
          "fields": [
            "owner",
            "name",
            "color",
            "is_default",
            "kind",
            "created_at"
          ],
          "source": "backend/api/models.py"
        },
        {
          "name": "Event",
          "fields": [
            "calendar",
            "title",
            "description",
            "start",
            "end",
            "all_day",
            "location",
            "external_contact_id",
            "external_contact_snapshot",
            "external_uid",
            "recurrence",
            "recurrence_month",
            "recurrence_day",
            "created_at",
            "updated_at"
          ],
          "source": "backend/api/models.py"
        }
      ],
      "model_schemas": [
        {
          "name": "Calendar",
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
              "name": "color",
              "field_type": "CharField",
              "required": false,
              "nullable": false,
              "blank": false,
              "default": "#1976d2",
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "is_default",
              "field_type": "BooleanField",
              "required": false,
              "nullable": false,
              "blank": false,
              "default": "False",
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "kind",
              "field_type": "CharField",
              "required": false,
              "nullable": false,
              "blank": false,
              "default": "Kind.PERSONAL",
              "choices": [
                {
                  "value": "personal",
                  "label": "Personal"
                },
                {
                  "value": "birthdays",
                  "label": "Birthdays"
                }
              ],
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
            }
          ]
        },
        {
          "name": "Event",
          "fields": [
            {
              "name": "calendar",
              "field_type": "ForeignKey",
              "required": true,
              "nullable": false,
              "blank": false,
              "default": null,
              "choices": [],
              "relation": "Calendar",
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
              "name": "description",
              "field_type": "TextField",
              "required": false,
              "nullable": false,
              "blank": true,
              "default": null,
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "start",
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
              "name": "end",
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
              "name": "all_day",
              "field_type": "BooleanField",
              "required": false,
              "nullable": false,
              "blank": false,
              "default": "False",
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "location",
              "field_type": "CharField",
              "required": false,
              "nullable": false,
              "blank": true,
              "default": null,
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "external_contact_id",
              "field_type": "CharField",
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
              "name": "external_contact_snapshot",
              "field_type": "JSONField",
              "required": false,
              "nullable": false,
              "blank": true,
              "default": "dict",
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "external_uid",
              "field_type": "CharField",
              "required": false,
              "nullable": true,
              "blank": true,
              "default": null,
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "recurrence",
              "field_type": "CharField",
              "required": false,
              "nullable": false,
              "blank": false,
              "default": "Recurrence.NONE",
              "choices": [
                {
                  "value": "none",
                  "label": "None"
                },
                {
                  "value": "yearly",
                  "label": "Yearly"
                }
              ],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "recurrence_month",
              "field_type": "PositiveSmallIntegerField",
              "required": false,
              "nullable": true,
              "blank": true,
              "default": null,
              "choices": [],
              "relation": null,
              "unique": false,
              "on_delete": null
            },
            {
              "name": "recurrence_day",
              "field_type": "PositiveSmallIntegerField",
              "required": false,
              "nullable": true,
              "blank": true,
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
          "methods": [],
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
          "path": "/api/auth/whoami/",
          "methods": [
            "GET"
          ],
          "view": "WhoAmIView",
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
          "path": "/api/calendars/",
          "methods": [
            "GET",
            "POST"
          ],
          "view": "CalendarViewSet",
          "permissions": [
            "IsAuthenticated",
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
          "path": "/api/calendars/{id}/",
          "methods": [
            "GET",
            "PUT",
            "PATCH",
            "DELETE"
          ],
          "view": "CalendarViewSet",
          "permissions": [
            "IsAuthenticated",
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
          "path": "/api/contact-integrations/contacts/",
          "methods": [
            "GET"
          ],
          "view": "ContactProxyView",
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
          "path": "/api/events/",
          "methods": [
            "GET"
          ],
          "view": "EventViewSet",
          "permissions": [
            "IsAuthenticated",
            "IsOwner"
          ],
          "authentication": [
            "JWT",
            "Bearer token"
          ],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [
            "owner scoped to request.user"
          ],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/events/{id}/",
          "methods": [
            "GET"
          ],
          "view": "EventViewSet",
          "permissions": [
            "IsAuthenticated",
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
            "owner scoped to request.user"
          ],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/health/",
          "methods": [],
          "view": "health",
          "permissions": [],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        },
        {
          "path": "/api/integrations/contact-birthdays/sync/",
          "methods": [
            "POST"
          ],
          "view": "ContactBirthdaySyncView",
          "permissions": [
            "AllowAny"
          ],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": true
        },
        {
          "path": "/api/integrations/dashboard/events/",
          "methods": [
            "GET"
          ],
          "view": "DashboardEventsView",
          "permissions": [
            "AllowAny"
          ],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": true
        },
        {
          "path": "/api/token/",
          "methods": [],
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
          "path": "/api/token/refresh/",
          "methods": [],
          "view": "TokenRefreshView",
          "permissions": [],
          "authentication": [],
          "actions": [],
          "route_parameters": [],
          "ownership_controls": [],
          "data_controls": [],
          "custom_authentication": false
        }
      ],
      "unresolved_routes": [],
      "resolved_routes": [
        {
          "full_path": "/admin/",
          "methods": [],
          "permissions": [],
          "resolution_status": "resolved"
        },
        {
          "full_path": "/api/auth/jwt/create/",
          "methods": [],
          "permissions": [],
          "resolution_status": "resolved"
        },
        {
          "full_path": "/api/auth/jwt/refresh/",
          "methods": [],
          "permissions": [],
          "resolution_status": "resolved"
        },
        {
          "full_path": "/api/auth/whoami/",
          "methods": [
            "GET"
          ],
          "permissions": [],
          "resolution_status": "resolved"
        },
        {
          "full_path": "/api/calendars/",
          "methods": [
            "GET",
            "POST"
          ],
          "permissions": [],
          "resolution_status": "resolved"
        },
        {
          "full_path": "/api/calendars/{id}/",
          "methods": [
            "GET",
            "PUT",
            "PATCH",
            "DELETE"
          ],
          "permissions": [],
          "resolution_status": "resolved"
        },
        {
          "full_path": "/api/contact-integrations/contacts/",
          "methods": [
            "GET"
          ],
          "permissions": [],
          "resolution_status": "resolved"
        },
        {
          "full_path": "/api/events/",
          "methods": [
            "GET"
          ],
          "permissions": [],
          "resolution_status": "resolved"
        },
        {
          "full_path": "/api/events/{id}/",
          "methods": [
            "GET"
          ],
          "permissions": [],
          "resolution_status": "resolved"
        },
        {
          "full_path": "/api/health/",
          "methods": [],
          "permissions": [],
          "resolution_status": "resolved"
        },
        {
          "full_path": "/api/integrations/contact-birthdays/sync/",
          "methods": [
            "POST"
          ],
          "permissions": [],
          "resolution_status": "resolved"
        },
        {
          "full_path": "/api/integrations/dashboard/events/",
          "methods": [
            "GET"
          ],
          "permissions": [],
          "resolution_status": "resolved"
        },
        {
          "full_path": "/api/token/",
          "methods": [],
          "permissions": [],
          "resolution_status": "resolved"
        },
        {
          "full_path": "/api/token/refresh/",
          "methods": [],
          "permissions": [],
          "resolution_status": "resolved"
        }
      ],
      "database_engine": "django.db.backends.postgresql",
      "database_engines": [
        {
          "engine": "django.db.backends.postgresql",
          "context": "default",
          "source": "backend/App/settings.py"
        }
      ],
      "database_configuration": [
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_HOST",
        "POSTGRES_PORT"
      ]
    }
  }
}
END SECTION FACTS
