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
Titre de section : Commandes de développement et de test
Identifiant de section : developer-commands
But : Présenter les commandes Make pertinentes pour le développement.
Budget de contexte estimé : 2103/12288 tokens.
Produis uniquement la section demandée, sans titre de document global, sans conclusion générale et sans contenu hors sujet.
END INSTRUCTIONS

BEGIN SECTION FACTS
{
  "identifier": "developer-commands",
  "title": "Commandes de développement et de test",
  "purpose": "Présenter les commandes Make pertinentes pour le développement.",
  "facts": {
    "operational_commands": {
      "primary_commands": [],
      "advanced_commands": [],
      "excluded_commands_summary": {
        "total": 68,
        "by_provenance": {
          "internal": 7,
          "legacy": 8,
          "template-standard": 13,
          "unknown": 38,
          "application-public": 2
        },
        "reasons": [
          {
            "reason": "Provenance documentaire non démontrée: cible publique hors app-template et sans déclaration applicative.",
            "count": 38
          },
          {
            "reason": "Aucune raison d’exclusion documentée.",
            "count": 15
          },
          {
            "reason": "Alias ou compatibilité historique non retenu dans la référence principale.",
            "count": 8
          },
          {
            "reason": "Helper interne ou garde-fou auxiliaire non retenu dans la référence utilisateur.",
            "count": 7
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
            "name": "backup",
            "provenance": "template-standard",
            "reason": null
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
            "name": "rebuild",
            "provenance": "template-standard",
            "reason": null
          },
          {
            "name": "update",
            "provenance": "application-public",
            "reason": null
          },
          {
            "name": "check",
            "provenance": "template-standard",
            "reason": null
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
          "pyproject.toml",
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
          "pyproject.toml",
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
    ]
  }
}
END SECTION FACTS
