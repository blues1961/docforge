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
Titre de section : Dépannage
Identifiant de section : operator-troubleshooting
But : Présenter les diagnostics opérationnels démontrés.
Budget de contexte estimé : 9258/12288 tokens.
Produis uniquement la section demandée, sans titre de document global, sans conclusion générale et sans contenu hors sujet.
END INSTRUCTIONS

BEGIN SECTION FACTS
{
  "identifier": "operator-troubleshooting",
  "title": "Dépannage",
  "purpose": "Présenter les diagnostics opérationnels démontrés.",
  "facts": {
    "missing_information": [
      {
        "identifier": "PROJECT-VERSION-MISSING",
        "category": "project",
        "severity": "warning",
        "description": "La version applicative n’a pas été trouvée dans les métadonnées détectées.",
        "affected_sections": [
          "presentation",
          "installation"
        ],
        "sources": [
          "ProjectKnowledge.application"
        ]
      },
      {
        "identifier": "PYTHON-VERSION-MISSING",
        "category": "runtime",
        "severity": "warning",
        "description": "La version minimale de Python n’est pas déterminable statiquement.",
        "affected_sections": [
          "installation",
          "prerequisites"
        ],
        "sources": [
          "backend/gestionnaire_mdp/settings.py"
        ]
      },
      {
        "identifier": "NODE-VERSION-MISSING",
        "category": "runtime",
        "severity": "warning",
        "description": "La version minimale de Node.js n’est pas documentée de manière fiable dans les faits structurés disponibles.",
        "affected_sections": [
          "installation",
          "prerequisites",
          "frontend"
        ],
        "sources": [
          "frontend/package.json",
          "frontend/Dockerfile.dev"
        ]
      },
      {
        "identifier": "DOCKER-COMPOSE-VERSION-MISSING",
        "category": "runtime",
        "severity": "warning",
        "description": "La version minimale de Docker Compose n’est pas explicitement documentée.",
        "affected_sections": [
          "installation",
          "prerequisites",
          "deployment"
        ],
        "sources": [
          "docker-compose.dev.yml",
          "docker-compose.prod.yml",
          "Makefile"
        ]
      },
      {
        "identifier": "INTEGRATION-TEST-DETAILS-MISSING",
        "category": "tests",
        "severity": "warning",
        "description": "Les détails des tests d’intégration ne sont pas disponibles dans les faits structurés générés.",
        "affected_sections": [
          "tests",
          "api"
        ],
        "sources": [
          "backend/gestionnaire_mdp/settings.py",
          "backend/gestionnaire_mdp/urls.py",
          "backend/api/urls.py",
          "… (+31 autres sources)"
        ]
      },
      {
        "identifier": "API-SCHEMA-MISSING",
        "category": "api",
        "severity": "warning",
        "description": "Les schémas détaillés de requête et de réponse des endpoints ne sont pas disponibles.",
        "affected_sections": [
          "api"
        ],
        "sources": [
          "backend/api/urls.py",
          "backend/api/views.py",
          "backend/api/views_auth.py",
          "… (+2 autres sources)"
        ]
      },
      {
        "identifier": "API-ERROR-CODES-MISSING",
        "category": "api",
        "severity": "warning",
        "description": "La matrice complète des codes d’erreur API n’est pas structurée de manière exhaustive.",
        "affected_sections": [
          "api",
          "troubleshooting"
        ],
        "sources": [
          "backend/api/urls.py",
          "backend/api/views.py",
          "backend/api/views_auth.py",
          "… (+2 autres sources)"
        ]
      },
      {
        "identifier": "BACKUP-RETENTION-POLICY-MISSING",
        "category": "backup",
        "severity": "warning",
        "description": "La stratégie de rétention des sauvegardes n’est pas démontrée.",
        "affected_sections": [
          "backup-restore",
          "operations"
        ],
        "sources": [
          "Makefile"
        ]
      }
    ],
    "limitations": {
      "items": []
    },
    "operational_commands": {
      "commands": [
        {
          "name": "exec-vite",
          "category": "alias",
          "command_path": "make exec-vite",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "internal",
          "documentation_policy": "exclude",
          "exclusion_reason": "Helper interne ou garde-fou auxiliaire non retenu dans la référence utilisateur.",
          "prerequisites": [
            "exec-frontend"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "pull-secret-all-remote",
          "category": "alias",
          "command_path": "make pull-secret-all-remote",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "legacy",
          "documentation_policy": "exclude",
          "exclusion_reason": "Alias ou compatibilité historique non retenu dans la référence principale.",
          "prerequisites": [
            "pull-secret"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "pull-secret-single",
          "category": "alias",
          "command_path": "make pull-secret-single",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "legacy",
          "documentation_policy": "exclude",
          "exclusion_reason": "Alias ou compatibilité historique non retenu dans la référence principale.",
          "prerequisites": [
            "pull-secret"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "push-secret-all-remote",
          "category": "alias",
          "command_path": "make push-secret-all-remote",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "legacy",
          "documentation_policy": "exclude",
          "exclusion_reason": "Alias ou compatibilité historique non retenu dans la référence principale.",
          "prerequisites": [
            "push-secret"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "push-secret-single",
          "category": "alias",
          "command_path": "make push-secret-single",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "legacy",
          "documentation_policy": "exclude",
          "exclusion_reason": "Alias ou compatibilité historique non retenu dans la référence principale.",
          "prerequisites": [
            "push-secret"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
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
            "Création d’un artefact de sauvegarde de base de données",
            "Artefact de sauvegarde écrit dans le répertoire relatif `backup/`"
          ],
          "parameters": []
        },
        {
          "name": "backup-db",
          "category": "backup",
          "command_path": "make backup-db",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check",
            "backup-dir"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "backup-env",
          "category": "backup",
          "command_path": "make backup-env",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "push-secret"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "pull-prod-backup",
          "category": "backup",
          "command_path": "make pull-prod-backup",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "backup-dir"
          ],
          "destructive": false,
          "destructive_effects": [],
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
          "name": "create-env",
          "category": "environment",
          "command_path": "make create-env",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [],
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
          "name": "env-check",
          "category": "environment",
          "command_path": "make env-check",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check-base",
            "env-check-local"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "env-check-base",
          "category": "environment",
          "command_path": "make env-check-base",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "internal",
          "documentation_policy": "exclude",
          "exclusion_reason": "Helper interne ou garde-fou auxiliaire non retenu dans la référence utilisateur.",
          "prerequisites": [],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "env-check-local",
          "category": "environment",
          "command_path": "make env-check-local",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "internal",
          "documentation_policy": "exclude",
          "exclusion_reason": "Helper interne ou garde-fou auxiliaire non retenu dans la référence utilisateur.",
          "prerequisites": [],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "generate-env",
          "category": "environment",
          "command_path": "make generate-env",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
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
          "name": "require-dev-env",
          "category": "environment",
          "command_path": "make require-dev-env",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "internal",
          "documentation_policy": "exclude",
          "exclusion_reason": "Helper interne ou garde-fou auxiliaire non retenu dans la référence utilisateur.",
          "prerequisites": [],
          "destructive": false,
          "destructive_effects": [],
          "parameters": [
            {
              "name": "APP_ENV",
              "required": false,
              "description": "Garde-fou: autorise la commande uniquement si APP_ENV=dev",
              "example": "dev",
              "allowed_values": [],
              "origin": "user-documented"
            }
          ]
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
          "name": "logs-backend",
          "category": "logs",
          "command_path": "make logs-backend",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "logs-db",
          "category": "logs",
          "command_path": "make logs-db",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "logs-frontend",
          "category": "logs",
          "command_path": "make logs-frontend",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "logs-vite",
          "category": "logs",
          "command_path": "make logs-vite",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "legacy",
          "documentation_policy": "exclude",
          "exclusion_reason": "Alias ou compatibilité historique non retenu dans la référence principale.",
          "prerequisites": [
            "logs-frontend"
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
          "name": "clean",
          "category": "other",
          "command_path": "make clean",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
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
          "name": "exec-backend",
          "category": "other",
          "command_path": "make exec-backend",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "internal",
          "documentation_policy": "exclude",
          "exclusion_reason": "Helper interne ou garde-fou auxiliaire non retenu dans la référence utilisateur.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "exec-db",
          "category": "other",
          "command_path": "make exec-db",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "internal",
          "documentation_policy": "exclude",
          "exclusion_reason": "Helper interne ou garde-fou auxiliaire non retenu dans la référence utilisateur.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "exec-frontend",
          "category": "other",
          "command_path": "make exec-frontend",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "internal",
          "documentation_policy": "exclude",
          "exclusion_reason": "Helper interne ou garde-fou auxiliaire non retenu dans la référence utilisateur.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
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
          "name": "init-dev",
          "category": "other",
          "command_path": "make init-dev",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "init-root-secret",
          "category": "other",
          "command_path": "make init-root-secret",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [],
          "destructive": false,
          "destructive_effects": [],
          "parameters": [
            {
              "name": "FORCE",
              "required": false,
              "description": "Générer PULL_ROOT_SECRET dans .env.root.local (FORCE=1 pour régénérer)",
              "example": "1",
              "allowed_values": [],
              "origin": "user-documented"
            }
          ]
        },
        {
          "name": "init-secret",
          "category": "other",
          "command_path": "make init-secret",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "ps-ports",
          "category": "other",
          "command_path": "make ps-ports",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "psql",
          "category": "other",
          "command_path": "make psql",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "pull-secret",
          "category": "other",
          "command_path": "make pull-secret",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check-base",
            "require-dev-env"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "push-secret",
          "category": "other",
          "command_path": "make push-secret",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check",
            "require-dev-env"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "reseed",
          "category": "other",
          "command_path": "make reseed",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "reset-dev-db",
          "category": "other",
          "command_path": "make reset-dev-db",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "seed-dev",
          "category": "other",
          "command_path": "make seed-dev",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "sh",
          "category": "other",
          "command_path": "make sh",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "tree",
          "category": "other",
          "command_path": "make tree",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [],
          "destructive": false,
          "destructive_effects": [],
          "parameters": [
            {
              "name": "TREE_IGNORE",
              "required": false,
              "allowed_values": [],
              "origin": "user-exposed"
            }
          ]
        },
        {
          "name": "whoami",
          "category": "other",
          "command_path": "make whoami",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
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
            "Arrêt des services actifs",
            "Interruption puis redémarrage des services actifs"
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
        },
        {
          "name": "restore-db",
          "category": "restore",
          "command_path": "make restore-db",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": true,
          "destructive_effects": [
            "Modification ou écrasement potentiel des données PostgreSQL"
          ],
          "parameters": [
            {
              "name": "BACKUP",
              "required": false,
              "description": "Restaurer la DB depuis BACKUP=<fichier.{sql.gz,dump}> (dernier par défaut)",
              "example": "<fichier.{sql.gz,dump}>",
              "allowed_values": [],
              "origin": "user-documented"
            }
          ]
        },
        {
          "name": "restore-env",
          "category": "restore",
          "command_path": "make restore-env",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "pull-secret"
          ],
          "destructive": true,
          "destructive_effects": [
            "Modification ou écrasement potentiel des données PostgreSQL"
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
          "name": "stop",
          "category": "shutdown",
          "command_path": "make stop",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "down"
          ],
          "destructive": true,
          "destructive_effects": [
            "Arrêt des services actifs"
          ],
          "parameters": []
        },
        {
          "name": "stop-backend",
          "category": "shutdown",
          "command_path": "make stop-backend",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
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
          "name": "stop-db",
          "category": "shutdown",
          "command_path": "make stop-db",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
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
          "name": "stop-frontend",
          "category": "shutdown",
          "command_path": "make stop-frontend",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
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
          "name": "stop-vite",
          "category": "shutdown",
          "command_path": "make stop-vite",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "legacy",
          "documentation_policy": "exclude",
          "exclusion_reason": "Alias ou compatibilité historique non retenu dans la référence principale.",
          "prerequisites": [
            "stop-frontend"
          ],
          "destructive": true,
          "destructive_effects": [
            "Arrêt des services actifs"
          ],
          "parameters": []
        },
        {
          "name": "createsuperuser",
          "category": "startup",
          "command_path": "make createsuperuser",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "restart-backend",
          "category": "startup",
          "command_path": "make restart-backend",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "restart-db",
          "category": "startup",
          "command_path": "make restart-db",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "restart-frontend",
          "category": "startup",
          "command_path": "make restart-frontend",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "restart-vite",
          "category": "startup",
          "command_path": "make restart-vite",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "legacy",
          "documentation_policy": "exclude",
          "exclusion_reason": "Alias ou compatibilité historique non retenu dans la référence principale.",
          "prerequisites": [
            "restart-frontend"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "start",
          "category": "startup",
          "command_path": "make start",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "up"
          ],
          "destructive": false,
          "destructive_effects": [],
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
        },
        {
          "name": "up-backend",
          "category": "startup",
          "command_path": "make up-backend",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "up-db",
          "category": "startup",
          "command_path": "make up-db",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "up-frontend",
          "category": "startup",
          "command_path": "make up-frontend",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "unknown",
          "documentation_policy": "exclude",
          "exclusion_reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "up-vite",
          "category": "startup",
          "command_path": "make up-vite",
          "audience": "operator",
          "reference_level": "omit",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "legacy",
          "documentation_policy": "exclude",
          "exclusion_reason": "Alias ou compatibilité historique non retenu dans la référence principale.",
          "prerequisites": [
            "up-frontend"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "test",
          "category": "tests",
          "command_path": "make test",
          "audience": "developer",
          "reference_level": "developer",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "developer-public",
          "documentation_policy": "developer-reference",
          "prerequisites": [
            "test-backend",
            "test-frontend"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "test-backend",
          "category": "tests",
          "command_path": "make test-backend",
          "audience": "developer",
          "reference_level": "developer",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "developer-public",
          "documentation_policy": "developer-reference",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "test-frontend",
          "category": "tests",
          "command_path": "make test-frontend",
          "audience": "developer",
          "reference_level": "developer",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "developer-public",
          "documentation_policy": "developer-reference",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        },
        {
          "name": "token-test",
          "category": "tests",
          "command_path": "make token-test",
          "audience": "developer",
          "reference_level": "developer",
          "environment": [
            "dev",
            "prod"
          ],
          "visibility": "public",
          "documented": true,
          "provenance": "developer-public",
          "documentation_policy": "developer-reference",
          "prerequisites": [
            "env-check"
          ],
          "destructive": false,
          "destructive_effects": [],
          "parameters": []
        }
      ]
    }
  }
}
END SECTION FACTS
