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
Titre de section : Documents protégés et contrat app-template
Identifiant de section : operator-protected-documents
But : Présenter le contrat et les documents protégés démontrés.
Budget de contexte estimé : 651/8192 tokens.
Produis uniquement la section demandée, sans titre de document global, sans conclusion générale et sans contenu hors sujet.
END INSTRUCTIONS

BEGIN SECTION FACTS
{
  "identifier": "operator-protected-documents",
  "title": "Documents protégés et contrat app-template",
  "purpose": "Présenter le contrat et les documents protégés démontrés.",
  "facts": {
    "template": {
      "project_kind": "application",
      "template_id": null,
      "origin_template_id": "app-template",
      "template_version": null,
      "origin_template_version": null,
      "base_profile": "django-react",
      "manifest_source": "heuristic: INVARIANTS.md + Makefile + Docker Compose",
      "current_state": null,
      "target_state": null,
      "materialization": null,
      "manifest_verified_targets": [
        "backup",
        "check",
        "dev",
        "down",
        "init",
        "logs",
        "migrate",
        "prod",
        "ps",
        "rebuild",
        "restart",
        "restore",
        "up"
      ],
      "manifest_missing_targets": [],
      "missing_steps": [],
      "risks": [],
      "placeholders": [],
      "creator_workflows": [],
      "maintainer_workflows": []
    },
    "security": {
      "protected_documents": [
        "INVARIANTS.md"
      ],
      "controls": [
        {
          "identifier": "APP-SEC-001",
          "category": "authentification",
          "description": "Des mécanismes d’authentification ont été détectés côté backend et/ou frontend.",
          "evidence": [
            "Bearer token",
            "JWT",
            "SimpleJWT"
          ]
        },
        {
          "identifier": "APP-SEC-002",
          "category": "administration",
          "description": "Une interface d’administration Django est détectée et doit être réservée aux comptes autorisés.",
          "evidence": [
            "backend/App/urls.py"
          ]
        },
        {
          "identifier": "APP-SEC-003",
          "category": "secrets",
          "description": "Des variables sensibles sont requises et leurs valeurs ne doivent pas être publiées dans le manuel.",
          "evidence": [
            "ADMIN_PASSWORD",
            "CALENDRIER_API_TOKEN",
            "DJANGO_SECRET_KEY",
            "POSTGRES_PASSWORD"
          ]
        }
      ],
      "risks": [
        {
          "identifier": "WRITE-ENDPOINT-ALLOWANY-CUSTOM-AUTH",
          "category": "api",
          "severity": "warning",
          "description": "L’endpoint /api/integrations/contacts/ accepte des écritures avec AllowAny et s’appuie sur une authentification personnalisée qui doit être vérifiée manuellement.",
          "sources": [
            "backend/App/urls.py",
            "backend/api/urls.py",
            "backend/api/views.py"
          ]
        }
      ],
      "validation_commands": [],
      "source": {
        "status": "derived",
        "sources": [],
        "notes": []
      }
    },
    "documentation_policy": {
      "required_documents": [
        "AGENTS.md",
        "CODEX_START.md",
        "INVARIANTS.md",
        "README.md",
        "README_DEV.md",
        "docs/api.md",
        "docs/architecture.md",
        "docs/deployment.md",
        "docs/specification.md"
      ],
      "optional_documents": [],
      "deterministic_documents": [
        "AGENTS.md",
        "CODEX_START.md",
        "INVARIANTS.md",
        "README.md",
        "README_DEV.md",
        "docs/api.md",
        "docs/architecture.md",
        "docs/deployment.md",
        "docs/specification.md"
      ],
      "protected_documents": [
        "INVARIANTS.md"
      ],
      "source": {
        "status": "configured",
        "sources": [],
        "notes": [
          "Contrat app-template détecté."
        ]
      }
    }
  }
}
END SECTION FACTS
