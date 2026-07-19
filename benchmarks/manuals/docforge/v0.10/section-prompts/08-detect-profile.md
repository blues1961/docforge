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
Titre de section : Détection du profil
Identifiant de section : detect-profile
But : Expliquer comment le profil est déterminé et présenté.
Taille estimée du contexte : 206 tokens.
Produis uniquement la section demandée, sans titre de document global, sans conclusion générale et sans contenu hors sujet.
END INSTRUCTIONS

BEGIN SECTION FACTS
{
  "identifier": "detect-profile",
  "title": "Détection du profil",
  "purpose": "Expliquer comment le profil est déterminé et présenté.",
  "facts": {
    "profile": {
      "name": "python-cli",
      "label": "Outil Python CLI",
      "description": "Application Python en ligne de commande, installable depuis pyproject.toml et testée avec pytest.",
      "confidence": 95,
      "evidence": [
        "configuration détectée : pyproject.toml",
        "point d’entrée CLI détecté dans pyproject.toml",
        "langage détecté : Python",
        "suite de tests détectée : tests/"
      ],
      "source": {
        "status": "detected",
        "sources": [],
        "notes": []
      }
    },
    "workflows": [
      {
        "identifier": "detect-profile",
        "title": "Détecter son profil",
        "summary": "Identifier le profil documentaire concret du dépôt.",
        "commands": [
          "docforge profile"
        ],
        "operational_status": "operational",
        "notes": []
      }
    ],
    "commands": []
  }
}
END SECTION FACTS
