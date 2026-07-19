BEGIN INSTRUCTIONS
Rédige un document Markdown fidèle aux faits fournis.
Utilise `manual-knowledge.json` comme source unique de vérité et n’utilise aucune connaissance externe pour compléter les procédures ou les caractéristiques du projet.
Suis strictement le blueprint fourni.
N’invente jamais une commande, une option, une procédure, une route, une URL, un paramètre, une variable, un service ou une fonctionnalité.
N’ajoute pas de bonnes pratiques générales comme si elles étaient démontrées par le projet.
Utilise `command_path` pour identifier ou titrer une commande.
Utilise `invocation` pour toute commande destinée à être copiée et exécutée.
Ne reconstruis jamais une syntaxe de commande à partir de `name` seul.
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
Titre de section : Révision des aperçus
Identifiant de section : preview-review
But : Expliquer la validation humaine des aperçus générés.
Taille estimée du contexte : 832 tokens.
Produis uniquement la section demandée, sans titre de document global, sans conclusion générale et sans contenu hors sujet.
END INSTRUCTIONS

BEGIN SECTION FACTS
{
  "identifier": "preview-review",
  "title": "Révision des aperçus",
  "purpose": "Expliquer la validation humaine des aperçus générés.",
  "facts": {
    "workflows": [
      {
        "identifier": "review-preview",
        "title": "Réviser les aperçus",
        "summary": "Contrôler les fichiers générés avant toute application.",
        "commands": [
          "docforge document . --refresh --clean",
          "git diff -- . ':(exclude).docforge'"
        ],
        "operational_status": "operational",
        "notes": []
      }
    ],
    "security": {
      "protected_documents": [
        "INVARIANTS.md"
      ],
      "controls": [
        {
          "identifier": "SEC-001",
          "category": "secrets",
          "description": "Le contenu des fichiers de secrets ne doit jamais être lu, reproduit ou sérialisé.",
          "evidence": ".env.local exclu des analyses documentaires."
        },
        {
          "identifier": "SEC-002",
          "category": "aperçu",
          "description": "La génération documentaire doit écrire dans .docforge/preview avant toute application.",
          "evidence": ".docforge/preview/"
        },
        {
          "identifier": "SEC-003",
          "category": "application",
          "description": "Un document généré ne doit être appliqué qu’après une commande explicite.",
          "evidence": "docforge apply"
        },
        {
          "identifier": "SEC-004",
          "category": "invariants",
          "description": "Les documents protégés doivent exiger une autorisation explicite du propriétaire.",
          "evidence": "--owner-approved"
        },
        {
          "identifier": "SEC-005",
          "category": "intégrité",
          "description": "Les invariants approuvés doivent pouvoir être vérifiés par empreinte.",
          "evidence": "invariant-baseline.json"
        },
        {
          "identifier": "SEC-006",
          "category": "portabilité",
          "description": "Les documents générés ne doivent pas contenir de chemin absolu propre à une machine.",
          "evidence": null
        },
        {
          "identifier": "SEC-007",
          "category": "Git",
          "description": "Les caches, aperçus, environnements virtuels et secrets ne doivent pas être suivis par Git.",
          "evidence": ".gitignore"
        },
        {
          "identifier": "SEC-008",
          "category": "analyse statique",
          "description": "Les analyseurs doivent éviter d’importer ou d’exécuter le code des projets inspectés.",
          "evidence": "analyse AST du CLI"
        }
      ],
      "risks": [
        "Divulgation involontaire d’un secret dans un document, un rapport ou un journal.",
        "Application automatique d’un aperçu non validé.",
        "Modification non autorisée d’un document d’invariants.",
        "Exécution de code lors de l’analyse d’un dépôt.",
        "Introduction d’un chemin local non portable dans la documentation.",
        "Suivi Git accidentel des caches ou des aperçus.",
        "Affaiblissement d’un test afin de masquer une régression de sécurité."
      ],
      "validation_commands": [
        "pytest -q",
        "docforge --help",
        "docforge verify-invariants /chemin/vers/app-template",
        "docforge document /chemin/du/projet --refresh --clean",
        "git status --short"
      ],
      "source": {
        "status": "detected",
        "sources": [],
        "notes": []
      }
    },
    "documentation_policy": {
      "required_documents": [
        "README.md",
        "README_DEV.md",
        "CODEX_START.md",
        "AGENTS.md",
        "INVARIANTS.md",
        "docs/architecture.md",
        "docs/cli.md",
        "docs/specification.md",
        "docs/configuration.md",
        "docs/security.md"
      ],
      "optional_documents": [
        "docs/roadmap.md",
        "docs/workflows.md"
      ],
      "deterministic_documents": [
        "README.md",
        "README_DEV.md",
        "CODEX_START.md",
        "AGENTS.md",
        "INVARIANTS.md",
        "docs/architecture.md",
        "docs/cli.md",
        "docs/configuration.md",
        "docs/specification.md",
        "docs/security.md"
      ],
      "protected_documents": [
        "INVARIANTS.md"
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
