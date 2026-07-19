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
Le manuel concerne l’outil CLI analysé et ses commandes réelles, sans extrapolation sur des intégrations non démontrées.
Ne transforme jamais les commandes de maintenance interne ou de génération documentaire en commandes d’usage courant si le projet ne les expose pas comme telles.
Titre de section : Prérequis
Identifiant de section : prerequisites
But : Lister les prérequis strictement démontrés pour utiliser le dépôt localement.
Taille estimée du contexte : 505 tokens.
Produis uniquement la section demandée, sans titre de document global, sans conclusion générale et sans contenu hors sujet.
END INSTRUCTIONS

BEGIN SECTION FACTS
{
  "identifier": "prerequisites",
  "title": "Prérequis",
  "purpose": "Lister les prérequis strictement démontrés pour utiliser le dépôt localement.",
  "facts": {
    "installation": {
      "prerequisites": [
        "Python >=3.11",
        "Git",
        "Un shell compatible POSIX"
      ]
    },
    "project": {
      "python_requires": ">=3.11"
    },
    "configuration": {
      "user_config_root": "~/.config/docforge",
      "project_state_root": ".docforge",
      "project_config_file": ".docforge.yml",
      "report_root": "reports",
      "files": [
        {
          "path": "~/.config/docforge/projects.yml",
          "scope": "utilisateur",
          "exists": true,
          "tracked_candidate": false,
          "description": "Registre des projets connus par docforge."
        },
        {
          "path": "~/.config/docforge/invariant-baseline.json",
          "scope": "utilisateur",
          "exists": true,
          "tracked_candidate": false,
          "description": "Empreintes approuvées des documents d’invariants protégés."
        },
        {
          "path": ".docforge.yml",
          "scope": "projet",
          "exists": false,
          "tracked_candidate": true,
          "description": "Configuration locale du projet pour le profil, la sélection documentaire et les exclusions de scan."
        },
        {
          "path": ".docforge/cache/",
          "scope": "projet",
          "exists": true,
          "tracked_candidate": false,
          "description": "Cache local des faits et de ProjectKnowledge."
        },
        {
          "path": ".docforge/preview/",
          "scope": "projet",
          "exists": true,
          "tracked_candidate": false,
          "description": "Aperçus documentaires générés avant application."
        },
        {
          "path": "reports/",
          "scope": "dépôt",
          "exists": true,
          "tracked_candidate": true,
          "description": "Rapports durables pouvant être suivis par Git."
        },
        {
          "path": "pyproject.toml",
          "scope": "dépôt",
          "exists": true,
          "tracked_candidate": true,
          "description": "Métadonnées du paquet, dépendances et point d’entrée CLI."
        },
        {
          "path": ".gitignore",
          "scope": "dépôt",
          "exists": true,
          "tracked_candidate": true,
          "description": "Exclusions Git, notamment caches, aperçus et environnements virtuels."
        }
      ],
      "environment_variables": [],
      "ignored_paths": [
        ".docforge/",
        ".pytest_cache/",
        ".venv/",
        "__pycache__/"
      ],
      "source": {
        "status": "configured",
        "sources": [],
        "notes": []
      }
    }
  }
}
END SECTION FACTS
