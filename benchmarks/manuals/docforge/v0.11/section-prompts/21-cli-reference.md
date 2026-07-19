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
Dans cette section, décris séparément chaque option ou argument documenté lorsque des paramètres structurés sont fournis.
Un exemple de commande combinant plusieurs options ne suffit jamais à expliquer séparément l’effet de chacune d’elles.
N’attribue à une option que la sémantique explicitement fournie par `commands.parameters.description`, dérivée du code détecté, sans interprétation supplémentaire.
Titre de section : Référence CLI
Identifiant de section : cli-reference
But : Fournir une référence fidèle des commandes détectées.
Taille estimée du contexte : 3870 tokens.
Produis uniquement la section demandée, sans titre de document global, sans conclusion générale et sans contenu hors sujet.
END INSTRUCTIONS

BEGIN SECTION FACTS
{
  "identifier": "cli-reference",
  "title": "Référence CLI",
  "purpose": "Fournir une référence fidèle des commandes détectées.",
  "facts": {
    "commands": [
      {
        "name": "analyze",
        "command_path": "analyze",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Analyser un projet sans modifier ses fichiers.",
        "parameters": [
          {
            "name": "PATH",
            "required": false,
            "description": "Chemin du projet à analyser.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--json",
            "required": false,
            "description": "Afficher le résultat complet en JSON.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "analyze-template",
        "command_path": "analyze-template",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Analyser le modèle canonique des applications auto-hébergées.",
        "parameters": [
          {
            "name": "PATH",
            "required": true,
            "description": "Chemin du dépôt app-template.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--no-cache",
            "required": false,
            "description": "Analyser sans écrire template.json.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--json",
            "required": false,
            "description": "Afficher l'analyse complète en JSON.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "apply",
        "command_path": "apply",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Copier des documents validés de l'aperçu vers le projet.",
        "parameters": [
          {
            "name": "PATH",
            "required": false,
            "description": "Chemin du projet.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "DOCUMENTS",
            "required": true,
            "description": "Documents d'aperçu à intégrer.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--owner-approved",
            "required": false,
            "description": "Confirmer l’autorisation explicite du propriétaire pour appliquer un document protégé.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--allow-dirty",
            "required": false,
            "description": "Autoriser exceptionnellement un dépôt Git modifié.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "approve-invariants",
        "command_path": "approve-invariants",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Enregistrer la version approuvée des invariants globaux.",
        "parameters": [
          {
            "name": "TEMPLATE_PATH",
            "required": true,
            "description": "Chemin du dépôt app-template.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--owner-approved",
            "required": false,
            "description": "Confirmer que le propriétaire autorise l'enregistrement de cette version.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "audit-all",
        "command_path": "audit-all",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Comparer les applications enregistrées à app-template.",
        "parameters": [
          {
            "name": "--template",
            "required": false,
            "description": "Chemin du template canonique.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--show-findings",
            "required": false,
            "description": "Afficher les écarts détaillés.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "audit-diff",
        "command_path": "audit-diff",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Comparer deux rapports de conformité.",
        "parameters": [
          {
            "name": "--current",
            "required": false,
            "description": "Rapport JSON courant.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--previous",
            "required": false,
            "description": "Rapport JSON précédent. Le plus récent de reports/history est utilisé par défaut.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--output",
            "required": false,
            "description": "Fichier Markdown de comparaison.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "audit-report",
        "command_path": "audit-report",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Générer un rapport persistant JSON et Markdown.",
        "parameters": [
          {
            "name": "--template",
            "required": false,
            "description": "Chemin du template canonique.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--output-dir",
            "required": false,
            "description": "Répertoire de destination des rapports.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "document",
        "command_path": "document",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Générer un aperçu des documents obligatoires manquants.",
        "parameters": [
          {
            "name": "PATH",
            "required": false,
            "description": "Chemin du projet à documenter.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--profile",
            "required": false,
            "description": "Profil documentaire explicite. Par défaut, utilise la configuration locale.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--clean",
            "required": false,
            "description": "Supprimer l'ancien aperçu avant la génération.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--refresh",
            "required": false,
            "description": "Régénérer les documents déterministes même s'ils existent déjà dans le projet.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--write",
            "required": false,
            "description": "Écrire dans le projet réel.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "generate",
        "command_path": "generate",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Remplir avec Ollama les documents manquants en aperçu.",
        "parameters": [
          {
            "name": "PATH",
            "required": false,
            "description": "Chemin du projet à documenter.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--model",
            "required": false,
            "description": "Modèle Ollama utilisé.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--clean",
            "required": false,
            "description": "Recréer entièrement le dossier d'aperçu.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--refresh",
            "required": false,
            "description": "Régénérer aussi les documents déterministes déjà présents.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "generate-global-invariants",
        "command_path": "generate-global-invariants",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Générer les invariants globaux depuis app-template.",
        "parameters": [
          {
            "name": "TEMPLATE_PATH",
            "required": true,
            "description": "Chemin du dépôt app-template.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--output",
            "required": false,
            "description": "Fichier Markdown à générer.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "init",
        "command_path": "init",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Créer la configuration locale d'un projet.",
        "parameters": [
          {
            "name": "PATH",
            "required": false,
            "description": "Chemin du projet à initialiser.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--force",
            "required": false,
            "description": "Remplacer une configuration locale existante.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "knowledge",
        "command_path": "knowledge",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Construire la connaissance structurée d'un projet.",
        "parameters": [
          {
            "name": "PATH",
            "required": false,
            "description": "Projet à analyser.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--output",
            "required": false,
            "description": "Fichier JSON de destination. Par défaut, utilise .docforge/cache/project-knowledge.json.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--json",
            "required": false,
            "description": "Afficher le JSON pur sur la sortie standard.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "profile",
        "command_path": "profile",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Détecter et afficher le profil d'un projet.",
        "parameters": [
          {
            "name": "PATH",
            "required": false,
            "description": "Projet dont le profil doit être détecté.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "refresh-all",
        "command_path": "refresh-all",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Actualiser les aperçus de tous les projets enregistrés.",
        "parameters": [
          {
            "name": "--clean",
            "required": false,
            "description": "Supprimer les anciens aperçus avant chaque régénération.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "remediation-plan",
        "command_path": "remediation-plan",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Générer un plan de mise en conformité sans appliquer de changement.",
        "parameters": [
          {
            "name": "--template",
            "required": false,
            "description": "Chemin du template canonique.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--output",
            "required": false,
            "description": "Fichier Markdown à générer.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "status-all",
        "command_path": "status-all",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Afficher l’état quotidien de tous les projets.",
        "parameters": [
          {
            "name": "--template",
            "required": false,
            "description": "Chemin du template canonique.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--show-details",
            "required": false,
            "description": "Afficher les documents différents et les écarts de conformité.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "verify",
        "command_path": "verify",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Comparer un projet au standard documentaire.",
        "parameters": [
          {
            "name": "PATH",
            "required": false,
            "description": "Chemin du projet à vérifier.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--profile",
            "required": false,
            "description": "Profil documentaire à appliquer. Par défaut, utilise la configuration locale ou la détection automatique.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "verify-invariants",
        "command_path": "verify-invariants",
        "group": null,
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Vérifier que les invariants correspondent à la version approuvée.",
        "parameters": [
          {
            "name": "TEMPLATE_PATH",
            "required": true,
            "description": "Chemin du dépôt app-template.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "prepare",
        "command_path": "manual prepare",
        "group": "manual",
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Préparer les entrées déterministes d’un manuel utilisateur.",
        "parameters": [
          {
            "name": "PATH",
            "required": false,
            "description": "Chemin du projet à préparer.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--clean",
            "required": false,
            "description": "Supprimer la préparation précédente avant génération.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--mode",
            "required": false,
            "description": "Mode de génération : full, sections ou both.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--output-dir",
            "required": false,
            "description": "Répertoire cible pour les artefacts du manuel.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--context-budget",
            "required": false,
            "description": "Budget maximum estimé par contexte de section. La préparation échoue si une section dépasse ce budget.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "validate",
        "command_path": "manual validate",
        "group": "manual",
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Valider un manuel Markdown contre les artefacts préparés.",
        "parameters": [
          {
            "name": "MARKDOWN_FILE",
            "required": true,
            "description": "Fichier Markdown du manuel à valider.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--project-root",
            "required": false,
            "description": "Racine du projet correspondant aux artefacts de préparation.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--manual-dir",
            "required": false,
            "description": "Répertoire contenant manual-knowledge.json et manual-manifest.json.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--json",
            "required": false,
            "description": "Émettre les diagnostics en JSON pour l’automatisation.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--document-id",
            "required": false,
            "description": "Identifiant du document à valider lorsque plusieurs guides ont été préparés.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "add",
        "command_path": "projects add",
        "group": "projects",
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Ajouter ou mettre à jour un projet dans le registre.",
        "parameters": [
          {
            "name": "PATH",
            "required": true,
            "description": "Chemin du projet à enregistrer.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--name",
            "required": false,
            "description": "Nom personnalisé du projet.",
            "example": null,
            "allowed_values": []
          },
          {
            "name": "--profile",
            "required": false,
            "description": "Profil documentaire explicite.",
            "example": null,
            "allowed_values": []
          }
        ]
      },
      {
        "name": "list",
        "command_path": "projects list",
        "group": "projects",
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Afficher les projets enregistrés.",
        "parameters": []
      },
      {
        "name": "remove",
        "command_path": "projects remove",
        "group": "projects",
        "audience": null,
        "reference_level": null,
        "provenance": null,
        "documentation_policy": null,
        "environment": [],
        "destructive": false,
        "destructive_effects": [],
        "help": "Retirer un projet du registre.",
        "parameters": [
          {
            "name": "IDENTIFIER",
            "required": true,
            "description": "Nom ou chemin du projet à retirer.",
            "example": null,
            "allowed_values": []
          }
        ]
      }
    ]
  }
}
END SECTION FACTS
