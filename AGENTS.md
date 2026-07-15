# AGENTS.md

<!--
Document généré en aperçu par project-assistant.
Les instructions locales placées entre les marqueurs
project-assistant sont conservées lors des régénérations.
-->

## Portée

Ces instructions s’appliquent à tout agent logiciel intervenant dans le dépôt `project-assistant`.

Le dépôt contient un outil Python en ligne de commande chargé d’analyser, documenter et auditer d’autres projets.

## Ordre de lecture obligatoire

Avant toute modification, lire dans cet ordre :

1. `INVARIANTS.md`;
2. `CODEX_START.md`;
3. `AGENTS.md`;
4. `README.md`;
5. `README_DEV.md`;
6. `docs/architecture.md`;
7. `docs/specification.md`;
8. les tests associés au composant modifié.

## Autorité des règles

Ordre d’autorité :

1. les invariants globaux approuvés;
2. `INVARIANTS.md` du dépôt;
3. `CODEX_START.md`;
4. `AGENTS.md`;
5. la documentation technique;
6. le code existant.

Le code existant ne constitue jamais une justification pour contourner un invariant ou affaiblir une protection.

## Contexte technique

- Paquet : `project-assistant`.
- Version : `0.1.0`.
- Version Python requise : `>=3.11`.
- Backend de construction : `setuptools.build_meta`.
- Dépendances principales : `PyYAML>=6.0`, `requests>=2.31`, `rich>=13.7`, `typer>=0.12`.
- Points d’entrée CLI : `project-assistant` → `project_assistant.cli:app`.

## Architecture interne

- `project_assistant/scanners/` découvre les fichiers;
- `project_assistant/detectors/` détecte les technologies;
- `project_assistant/analyzers/` extrait des faits structurés;
- `project_assistant/profiles/` détermine la famille du projet;
- `project_assistant/knowledge.py` construit `ProjectKnowledge`;
- `project_assistant/documentation_pipeline.py` sélectionne les générateurs;
- `project_assistant/generators/` produit le Markdown;
- `project_assistant/commands/` contient les opérations;
- `project_assistant/cli.py` expose les commandes Typer;
- `tests/` valide les comportements.

## Règles non négociables

- ne jamais lire, afficher, journaliser ou intégrer le contenu d’un fichier `.env.local` analysé;
- ne jamais appliquer automatiquement un document protégé sans autorisation explicite;
- ne jamais modifier les invariants approuvés pour adapter les règles à l’état d’un projet;
- ne jamais présenter une détection heuristique comme un fait certain sans conserver ses preuves;
- ne jamais inventer une technologie, une commande, une route, un service ou une convention;
- ne jamais appeler un LLM pour remplacer une génération déterministe disponible;
- ne jamais écrire directement dans les documents cibles pendant la phase d’aperçu;
- ne jamais masquer un test, une erreur d’import ou une erreur de syntaxe;

## Règles de génération documentaire

- construire `ProjectKnowledge` avant de générer les documents déterministes;
- sélectionner les documents selon la politique du profil;
- déclarer tout document déterministe dans `DocumentationPipeline.SUPPORTED_DOCUMENTS`;
- conserver les sections locales délimitées par les marqueurs `project-assistant`;
- écrire les résultats dans `.project-assistant/preview`;
- exiger une action `apply` explicite pour intégrer un aperçu;
- protéger `INVARIANTS.md` par une approbation explicite du propriétaire;

## Règles concernant les profils

Un profil doit définir :

- un nom stable;
- un libellé lisible;
- une description;
- un niveau de confiance;
- des preuves de détection;
- ses documents obligatoires;
- ses documents optionnels;
- ses documents déterministes;
- ses documents protégés.

Le profil `generic` reste un profil de secours. Il ne doit pas être utilisé lorsqu’un profil spécialisé atteint le seuil de confiance requis.

## Règles de modification du code

- effectuer le changement minimal répondant à la demande;
- éviter les refactorisations sans lien direct;
- préserver les API internes existantes lorsque possible;
- ajouter des types et des dataclasses pour les nouveaux faits;
- centraliser les faits dans `ProjectKnowledge`;
- éviter de rescanner inutilement le même dépôt;
- traiter explicitement les fichiers absents ou invalides;
- conserver des sorties déterministes et ordonnées;

## Tests obligatoires

Toute modification doit inclure les tests appropriés :

- test unitaire du nouvel analyseur ou générateur;
- test du pipeline documentaire;
- test de sélection par profil;
- test de sérialisation de `ProjectKnowledge` si nécessaire;
- test CLI pour toute nouvelle commande;
- test de protection pour les documents ou données sensibles;
- test de non-régression pour les profils existants.

Avant de terminer :

```bash
python -m py_compile project_assistant/cli.py
pytest -q
```

Compiler également chaque nouveau fichier Python modifié.

## Actions interdites

- supprimer un test pour faire réussir la suite;
- diminuer une assertion sans justification;
- utiliser une recherche/remplacement non vérifiée sur plusieurs blocs;
- introduire un chemin absolu propre à une machine;
- coder en dur les métadonnées présentes dans `pyproject.toml`;
- ajouter `.project-assistant/` ou `.venv/` au dépôt;
- reproduire les secrets provenant des projets analysés;
- contourner le mode aperçu sécurisé;

## Validation avant livraison

Toujours vérifier :

1. `python -m py_compile` réussit;
2. `pytest -q` réussit;
3. `project-assistant --help` fonctionne;
4. `git diff` correspond à la demande;
5. `git status` ne contient aucun secret ou cache;
6. les profils existants conservent leur comportement;
7. les documents déterministes restent reproductibles;
8. la documentation reflète le code actuel.

## Instructions locales

<!-- project-assistant:local-agents:start -->

_Ajouter ici uniquement les instructions propres au développement de ce dépôt._

_Cette section est conservée lors des futures régénérations déterministes._

<!-- project-assistant:local-agents:end -->
