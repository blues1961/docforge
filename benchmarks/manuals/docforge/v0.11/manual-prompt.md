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
Version du schéma ManualKnowledge : 2.
Structure attendue :
{
  "profile_name": "python-cli",
  "document_identifier": "manual",
  "document_title": "Guide utilisateur",
  "document_audience": "user",
  "document_kind": "user-guide",
  "sections": [
    {
      "identifier": "presentation",
      "title": "Présentation",
      "purpose": "Présenter le produit, son objectif et son profil logiciel.",
      "required_fact_paths": [
        "project",
        "profile"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "target-audience",
      "title": "Public visé",
      "purpose": "Décrire les utilisateurs pertinents à partir du type de projet et de la CLI détectée.",
      "required_fact_paths": [
        "project",
        "profile"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "prerequisites",
      "title": "Prérequis",
      "purpose": "Lister les prérequis strictement démontrés pour utiliser le dépôt localement.",
      "required_fact_paths": [
        "installation.prerequisites",
        "project.python_requires",
        "configuration"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "installation",
      "title": "Installation",
      "purpose": "Décrire l’installation locale depuis une copie du dépôt.",
      "required_fact_paths": [
        "installation"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "quick-start",
      "title": "Démarrage rapide",
      "purpose": "Fournir une première séquence de commandes pour vérifier l’outil.",
      "required_fact_paths": [
        "installation.steps",
        "commands",
        "workflows"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "core-concepts",
      "title": "Concepts essentiels",
      "purpose": "Expliquer les concepts structurants du produit.",
      "required_fact_paths": [
        "project",
        "profile",
        "documentation_policy",
        "security"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "analyze-project",
      "title": "Analyse d’un projet",
      "purpose": "Décrire le flux d’analyse d’un projet local.",
      "required_fact_paths": [
        "workflows",
        "commands"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "detect-profile",
      "title": "Détection du profil",
      "purpose": "Expliquer comment le profil est déterminé et présenté.",
      "required_fact_paths": [
        "profile",
        "workflows",
        "commands"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "build-project-knowledge",
      "title": "Construction de ProjectKnowledge",
      "purpose": "Décrire la construction de la connaissance structurée.",
      "required_fact_paths": [
        "workflows",
        "commands",
        "documentation_policy"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "documentation-generation",
      "title": "Génération documentaire",
      "purpose": "Présenter la génération déterministe en aperçu.",
      "required_fact_paths": [
        "workflows",
        "documentation_policy",
        "security",
        "commands"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "ollama-generation",
      "title": "Génération avec Ollama",
      "purpose": "Expliquer le flux dédié à docforge generate sans le confondre avec la préparation du manuel.",
      "required_fact_paths": [
        "workflows",
        "commands",
        "limitations"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "preview-review",
      "title": "Révision des aperçus",
      "purpose": "Expliquer la validation humaine des aperçus générés.",
      "required_fact_paths": [
        "workflows",
        "security",
        "documentation_policy"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "apply-documents",
      "title": "Application des documents",
      "purpose": "Décrire l’application explicite des documents validés.",
      "required_fact_paths": [
        "workflows",
        "security",
        "commands"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "protected-documents",
      "title": "Documents protégés",
      "purpose": "Décrire le traitement spécifique des documents protégés.",
      "required_fact_paths": [
        "security",
        "documentation_policy",
        "workflows"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "project-management",
      "title": "Gestion des projets",
      "purpose": "Décrire l’enregistrement et le suivi de plusieurs projets.",
      "required_fact_paths": [
        "commands",
        "workflows",
        "configuration"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "audits-compliance",
      "title": "Audits et conformité",
      "purpose": "Présenter les commandes d’audit et les validations de conformité.",
      "required_fact_paths": [
        "commands",
        "workflows",
        "security"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "configuration",
      "title": "Configuration",
      "purpose": "Décrire les emplacements et fichiers de configuration utiles.",
      "required_fact_paths": [
        "configuration"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "security",
      "title": "Sécurité",
      "purpose": "Présenter les garde-fous documentaires et opérationnels.",
      "required_fact_paths": [
        "security",
        "documentation_policy"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "troubleshooting",
      "title": "Dépannage",
      "purpose": "Guider le lecteur en cas de problème connu ou d’information manquante.",
      "required_fact_paths": [
        "limitations",
        "security"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "limitations",
      "title": "Limites des informations disponibles",
      "purpose": "Exposer les limites de la source de vérité fournie au modèle.",
      "required_fact_paths": [
        "missing_information",
        "limitations",
        "source_traceability"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    },
    {
      "identifier": "cli-reference",
      "title": "Référence CLI",
      "purpose": "Fournir une référence fidèle des commandes détectées.",
      "required_fact_paths": [
        "commands"
      ],
      "optional": false,
      "omit_condition": null,
      "omit_if_fact_paths_missing": []
    }
  ]
}
END INSTRUCTIONS

BEGIN COMPACT MANUAL CONTEXT
{
  "schema_version": 2,
  "project": {
    "name": "docforge",
    "profile_type": "python-cli"
  },
  "sections": [
    {
      "identifier": "presentation",
      "title": "Présentation",
      "purpose": "Présenter le produit, son objectif et son profil logiciel.",
      "estimated_tokens": 221,
      "facts": {
        "project": {
          "name": "docforge",
          "version": "0.1.0",
          "description": "Assistant local d'analyse et de documentation de projets logiciels.",
          "profile_type": "python-cli",
          "python_requires": ">=3.11",
          "cli_entry_point": "docforge -> docforge.cli:app",
          "source": {
            "status": "detected",
            "sources": [],
            "notes": []
          }
        },
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
        }
      }
    },
    {
      "identifier": "target-audience",
      "title": "Public visé",
      "purpose": "Décrire les utilisateurs pertinents à partir du type de projet et de la CLI détectée.",
      "estimated_tokens": 228,
      "facts": {
        "project": {
          "name": "docforge",
          "version": "0.1.0",
          "description": "Assistant local d'analyse et de documentation de projets logiciels.",
          "profile_type": "python-cli",
          "python_requires": ">=3.11",
          "cli_entry_point": "docforge -> docforge.cli:app",
          "source": {
            "status": "detected",
            "sources": [],
            "notes": []
          }
        },
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
        }
      }
    },
    {
      "identifier": "prerequisites",
      "title": "Prérequis",
      "purpose": "Lister les prérequis strictement démontrés pour utiliser le dépôt localement.",
      "estimated_tokens": 505,
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
    },
    {
      "identifier": "installation",
      "title": "Installation",
      "purpose": "Décrire l’installation locale depuis une copie du dépôt.",
      "estimated_tokens": 196,
      "facts": {
        "installation": {
          "summary": "Installation locale à partir d’une copie du dépôt.",
          "prerequisites": [
            "Python >=3.11",
            "Git",
            "Un shell compatible POSIX"
          ],
          "steps": [
            {
              "title": "Créer un environnement virtuel",
              "command": "python -m venv .venv"
            },
            {
              "title": "Activer l’environnement",
              "command": "source .venv/bin/activate"
            },
            {
              "title": "Installer le paquet localement",
              "command": "python -m pip install -e ."
            },
            {
              "title": "Installer les dépendances de développement",
              "command": "python -m pip install -e \".[dev]\""
            },
            {
              "title": "Vérifier l’installation CLI",
              "command": "docforge --help"
            },
            {
              "title": "Exécuter les tests",
              "command": "pytest -q"
            }
          ]
        }
      }
    },
    {
      "identifier": "quick-start",
      "title": "Démarrage rapide",
      "purpose": "Fournir une première séquence de commandes pour vérifier l’outil.",
      "estimated_tokens": 275,
      "facts": {
        "installation": {
          "steps": [
            {
              "title": "Créer un environnement virtuel",
              "command": "python -m venv .venv",
              "source": {
                "status": "derived",
                "sources": [],
                "notes": []
              }
            },
            {
              "title": "Activer l’environnement",
              "command": "source .venv/bin/activate",
              "source": {
                "status": "derived",
                "sources": [],
                "notes": []
              }
            },
            {
              "title": "Installer le paquet localement",
              "command": "python -m pip install -e .",
              "source": {
                "status": "derived",
                "sources": [],
                "notes": []
              }
            },
            {
              "title": "Installer les dépendances de développement",
              "command": "python -m pip install -e \".[dev]\"",
              "source": {
                "status": "configured",
                "sources": [],
                "notes": []
              }
            },
            {
              "title": "Vérifier l’installation CLI",
              "command": "docforge --help",
              "source": {
                "status": "derived",
                "sources": [],
                "notes": []
              }
            },
            {
              "title": "Exécuter les tests",
              "command": "pytest -q",
              "source": {
                "status": "derived",
                "sources": [],
                "notes": []
              }
            }
          ]
        },
        "commands": [],
        "workflows": [],
        "service_endpoints": {
          "endpoints": []
        }
      }
    },
    {
      "identifier": "core-concepts",
      "title": "Concepts essentiels",
      "purpose": "Expliquer les concepts structurants du produit.",
      "estimated_tokens": 942,
      "facts": {
        "project": {
          "name": "docforge",
          "version": "0.1.0",
          "description": "Assistant local d'analyse et de documentation de projets logiciels.",
          "profile_type": "python-cli",
          "python_requires": ">=3.11",
          "cli_entry_point": "docforge -> docforge.cli:app",
          "source": {
            "status": "detected",
            "sources": [],
            "notes": []
          }
        },
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
        },
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
        }
      }
    },
    {
      "identifier": "analyze-project",
      "title": "Analyse d’un projet",
      "purpose": "Décrire le flux d’analyse d’un projet local.",
      "estimated_tokens": 95,
      "facts": {
        "workflows": [
          {
            "identifier": "analyze-project",
            "title": "Analyser un projet",
            "summary": "Inspecter un dépôt sans modifier ses fichiers.",
            "commands": [
              "docforge analyze"
            ],
            "operational_status": "operational",
            "notes": []
          }
        ],
        "commands": []
      }
    },
    {
      "identifier": "detect-profile",
      "title": "Détection du profil",
      "purpose": "Expliquer comment le profil est déterminé et présenté.",
      "estimated_tokens": 206,
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
    },
    {
      "identifier": "build-project-knowledge",
      "title": "Construction de ProjectKnowledge",
      "purpose": "Décrire la construction de la connaissance structurée.",
      "estimated_tokens": 266,
      "facts": {
        "workflows": [
          {
            "identifier": "build-project-knowledge",
            "title": "Construire ProjectKnowledge",
            "summary": "Produire la représentation factuelle structurée du dépôt.",
            "commands": [
              "docforge knowledge"
            ],
            "operational_status": "operational",
            "notes": []
          }
        ],
        "commands": [],
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
    },
    {
      "identifier": "documentation-generation",
      "title": "Génération documentaire",
      "purpose": "Présenter la génération déterministe en aperçu.",
      "estimated_tokens": 971,
      "facts": {
        "workflows": [
          {
            "identifier": "generate-preview",
            "title": "Générer un aperçu documentaire",
            "summary": "Créer des aperçus déterministes sans modifier les documents réels.",
            "commands": [
              "docforge document . --refresh --clean"
            ],
            "operational_status": "operational",
            "notes": []
          },
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
          },
          {
            "identifier": "generate-with-ollama",
            "title": "Utiliser Ollama avec docforge generate",
            "summary": "Compléter les documents manquants via le flux LLM dédié.",
            "commands": [
              "docforge generate . --refresh --clean"
            ],
            "operational_status": "operational",
            "notes": []
          }
        ],
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
        },
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
        "commands": []
      }
    },
    {
      "identifier": "ollama-generation",
      "title": "Génération avec Ollama",
      "purpose": "Expliquer le flux dédié à docforge generate sans le confondre avec la préparation du manuel.",
      "estimated_tokens": 355,
      "facts": {
        "workflows": [
          {
            "identifier": "generate-with-ollama",
            "title": "Utiliser Ollama avec docforge generate",
            "summary": "Compléter les documents manquants via le flux LLM dédié.",
            "commands": [
              "docforge generate . --refresh --clean"
            ],
            "operational_status": "operational",
            "notes": []
          }
        ],
        "commands": [],
        "limitations": {
          "items": [
            {
              "identifier": null,
              "category": "limitation",
              "severity": "warning",
              "description": "Le manuel préparé ne contient que des faits présents dans ProjectKnowledge et dans les politiques du profil.",
              "affected_sections": [],
              "sources": []
            },
            {
              "identifier": null,
              "category": "limitation",
              "severity": "warning",
              "description": "Toute information absente ou incertaine doit être signalée comme manquante dans la rédaction finale.",
              "affected_sections": [],
              "sources": []
            },
            {
              "identifier": null,
              "category": "limitation",
              "severity": "warning",
              "description": "Les workflows proposés restent limités aux commandes détectées dans la CLI.",
              "affected_sections": [],
              "sources": []
            },
            {
              "identifier": null,
              "category": "limitation",
              "severity": "warning",
              "description": "Certains constats d’environnement non pertinents pour ce profil sont exclus de la projection manuel.",
              "affected_sections": [],
              "sources": []
            }
          ]
        }
      }
    },
    {
      "identifier": "preview-review",
      "title": "Révision des aperçus",
      "purpose": "Expliquer la validation humaine des aperçus générés.",
      "estimated_tokens": 832,
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
    },
    {
      "identifier": "apply-documents",
      "title": "Application des documents",
      "purpose": "Décrire l’application explicite des documents validés.",
      "estimated_tokens": 747,
      "facts": {
        "workflows": [
          {
            "identifier": "apply-validated-document",
            "title": "Appliquer un document validé",
            "summary": "Copier explicitement un aperçu validé dans le projet.",
            "commands": [
              "docforge apply . README.md"
            ],
            "operational_status": "operational",
            "notes": []
          },
          {
            "identifier": "apply-protected-document",
            "title": "Appliquer un document protégé",
            "summary": "Appliquer un document protégé avec autorisation explicite du propriétaire.",
            "commands": [
              "docforge apply . INVARIANTS.md --owner-approved"
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
        "commands": []
      }
    },
    {
      "identifier": "protected-documents",
      "title": "Documents protégés",
      "purpose": "Décrire le traitement spécifique des documents protégés.",
      "estimated_tokens": 836,
      "facts": {
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
        },
        "workflows": [
          {
            "identifier": "apply-protected-document",
            "title": "Appliquer un document protégé",
            "summary": "Appliquer un document protégé avec autorisation explicite du propriétaire.",
            "commands": [
              "docforge apply . INVARIANTS.md --owner-approved"
            ],
            "operational_status": "operational",
            "notes": []
          }
        ]
      }
    },
    {
      "identifier": "project-management",
      "title": "Gestion des projets",
      "purpose": "Décrire l’enregistrement et le suivi de plusieurs projets.",
      "estimated_tokens": 554,
      "facts": {
        "commands": [],
        "workflows": [
          {
            "identifier": "manage-projects",
            "title": "Gérer plusieurs projets",
            "summary": "Enregistrer, lister et retirer des projets du registre utilisateur.",
            "commands": [
              "docforge projects add .",
              "docforge projects list",
              "docforge projects remove demo"
            ],
            "operational_status": "operational",
            "notes": []
          }
        ],
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
    },
    {
      "identifier": "audits-compliance",
      "title": "Audits et conformité",
      "purpose": "Présenter les commandes d’audit et les validations de conformité.",
      "estimated_tokens": 683,
      "facts": {
        "commands": [],
        "workflows": [
          {
            "identifier": "produce-audit",
            "title": "Produire un audit",
            "summary": "Comparer les projets enregistrés et produire un rapport de conformité.",
            "commands": [
              "docforge audit-all --show-findings",
              "docforge audit-report"
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
        }
      }
    },
    {
      "identifier": "configuration",
      "title": "Configuration",
      "purpose": "Décrire les emplacements et fichiers de configuration utiles.",
      "estimated_tokens": 469,
      "facts": {
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
    },
    {
      "identifier": "security",
      "title": "Sécurité",
      "purpose": "Présenter les garde-fous documentaires et opérationnels.",
      "estimated_tokens": 766,
      "facts": {
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
        },
        "environment_variables": {
          "variables": []
        }
      }
    },
    {
      "identifier": "troubleshooting",
      "title": "Dépannage",
      "purpose": "Guider le lecteur en cas de problème connu ou d’information manquante.",
      "estimated_tokens": 837,
      "facts": {
        "limitations": {
          "items": [
            {
              "identifier": null,
              "category": "limitation",
              "severity": "warning",
              "description": "Le manuel préparé ne contient que des faits présents dans ProjectKnowledge et dans les politiques du profil.",
              "affected_sections": [],
              "sources": []
            },
            {
              "identifier": null,
              "category": "limitation",
              "severity": "warning",
              "description": "Toute information absente ou incertaine doit être signalée comme manquante dans la rédaction finale.",
              "affected_sections": [],
              "sources": []
            },
            {
              "identifier": null,
              "category": "limitation",
              "severity": "warning",
              "description": "Les workflows proposés restent limités aux commandes détectées dans la CLI.",
              "affected_sections": [],
              "sources": []
            },
            {
              "identifier": null,
              "category": "limitation",
              "severity": "warning",
              "description": "Certains constats d’environnement non pertinents pour ce profil sont exclus de la projection manuel.",
              "affected_sections": [],
              "sources": []
            }
          ]
        },
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
        }
      }
    },
    {
      "identifier": "limitations",
      "title": "Limites des informations disponibles",
      "purpose": "Exposer les limites de la source de vérité fournie au modèle.",
      "estimated_tokens": 395,
      "facts": {
        "missing_information": [],
        "limitations": {
          "items": [
            {
              "identifier": null,
              "category": "limitation",
              "severity": "warning",
              "description": "Le manuel préparé ne contient que des faits présents dans ProjectKnowledge et dans les politiques du profil.",
              "affected_sections": [],
              "sources": []
            },
            {
              "identifier": null,
              "category": "limitation",
              "severity": "warning",
              "description": "Toute information absente ou incertaine doit être signalée comme manquante dans la rédaction finale.",
              "affected_sections": [],
              "sources": []
            },
            {
              "identifier": null,
              "category": "limitation",
              "severity": "warning",
              "description": "Les workflows proposés restent limités aux commandes détectées dans la CLI.",
              "affected_sections": [],
              "sources": []
            },
            {
              "identifier": null,
              "category": "limitation",
              "severity": "warning",
              "description": "Certains constats d’environnement non pertinents pour ce profil sont exclus de la projection manuel.",
              "affected_sections": [],
              "sources": []
            }
          ]
        },
        "source_traceability": {
          "items": {
            "project": {
              "status": "detected",
              "sources": []
            },
            "profile": {
              "status": "detected",
              "sources": []
            },
            "installation": {
              "status": "derived",
              "sources": []
            },
            "commands": {
              "status": "detected",
              "sources": []
            },
            "workflows": {
              "status": "derived",
              "sources": []
            },
            "configuration": {
              "status": "configured",
              "sources": []
            },
            "security": {
              "status": "detected",
              "sources": []
            },
            "limitations": {
              "status": "derived",
              "sources": []
            }
          }
        }
      }
    },
    {
      "identifier": "cli-reference",
      "title": "Référence CLI",
      "purpose": "Fournir une référence fidèle des commandes détectées.",
      "estimated_tokens": 3870,
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
  ]
}
END COMPACT MANUAL CONTEXT
