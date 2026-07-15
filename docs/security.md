# Sécurité — project-assistant

<!--
Document généré en aperçu par project-assistant.
Le contenu est dérivé de SecurityFacts.
-->

## Objectif

Cette politique décrit les protections appliquées pendant l’analyse, la génération documentaire, l’application des aperçus et la gestion des invariants.

## Modèle de confiance

Un dépôt analysé est considéré comme une source potentiellement non fiable.

En conséquence :

- le code inspecté ne doit pas être exécuté;
- les modules CLI ne doivent pas être importés;
- les secrets ne doivent pas être lus;
- les aperçus ne doivent pas être appliqués automatiquement;
- les documents protégés exigent une approbation explicite.

## Actifs protégés

- secrets des projets analysés;
- documents d’invariants;
- configuration utilisateur;
- empreintes d’intégrité;
- rapports et aperçus;
- fiabilité de `ProjectKnowledge`;
- historique Git du dépôt.

## Documents protégés

- `INVARIANTS.md`

L’application d’un document protégé exige `--owner-approved`.

Exemple :

```bash
project-assistant apply \
  /chemin/du/projet \
  INVARIANTS.md \
  --owner-approved
```

## Contrôles de sécurité

| Identifiant | Catégorie | Contrôle | Preuve |
|---|---|---|---|
| `SEC-001` | secrets | Le contenu des fichiers de secrets ne doit jamais être lu, reproduit ou sérialisé. | .env.local exclu des analyses documentaires. |
| `SEC-002` | aperçu | La génération documentaire doit écrire dans .project-assistant/preview avant toute application. | .project-assistant/preview/ |
| `SEC-003` | application | Un document généré ne doit être appliqué qu’après une commande explicite. | project-assistant apply |
| `SEC-004` | invariants | Les documents protégés doivent exiger une autorisation explicite du propriétaire. | --owner-approved |
| `SEC-005` | intégrité | Les invariants approuvés doivent pouvoir être vérifiés par empreinte. | invariant-baseline.json |
| `SEC-006` | portabilité | Les documents générés ne doivent pas contenir de chemin absolu propre à une machine. | — |
| `SEC-007` | Git | Les caches, aperçus, environnements virtuels et secrets ne doivent pas être suivis par Git. | .gitignore |
| `SEC-008` | analyse statique | Les analyseurs doivent éviter d’importer ou d’exécuter le code des projets inspectés. | analyse AST du CLI |

## Protection des secrets

Règles obligatoires :

- ne jamais lire le contenu de `.env.local`;
- ne jamais sérialiser une valeur secrète;
- ne jamais écrire un secret dans un aperçu;
- ne jamais écrire un secret dans un rapport;
- ne jamais afficher un secret dans une erreur;
- ne jamais ajouter un secret au registre des projets.

Les noms de variables peuvent être documentés lorsqu’ils sont détectés dans le code, mais jamais leur valeur.

## Analyse sans exécution

Les analyseurs doivent privilégier la lecture statique des fichiers.

Exemples :

- analyse AST des commandes Typer;
- lecture structurée de `pyproject.toml`;
- lecture YAML ou JSON sans import du projet;
- scan du système de fichiers sans lancer de commande.

Un analyseur ne doit pas :

- importer le module CLI du projet;
- exécuter un script détecté;
- lancer une migration;
- démarrer un conteneur;
- évaluer une expression arbitraire.

## Aperçu sécurisé

Les documents générés sont écrits dans :

```text
.project-assistant/preview/
```

Ce mécanisme garantit que :

- le fichier cible n’est pas modifié pendant la génération;
- le contenu peut être inspecté avant application;
- un diff peut être produit;
- l’utilisateur conserve le contrôle de l’intégration.

## Intégrité des invariants

Les invariants approuvés peuvent être enregistrés dans une référence d’empreintes.

Chemin utilisateur :

```text
~/.config/project-assistant/invariant-baseline.json
```

Commandes associées :

```bash
project-assistant approve-invariants /chemin/vers/app-template --owner-approved
project-assistant verify-invariants /chemin/vers/app-template
```

Une différence d’empreinte doit être signalée comme une modification potentiellement non autorisée.

## Fichiers sensibles ignorés

- `.project-assistant/`
- `.pytest_cache/`
- `.venv/`
- `__pycache__/`

Exclusions recommandées :

```gitignore
.env.local
.env.*.local
.project-assistant/
.venv/
__pycache__/
.pytest_cache/
```

## Risques connus

- Divulgation involontaire d’un secret dans un document, un rapport ou un journal.
- Application automatique d’un aperçu non validé.
- Modification non autorisée d’un document d’invariants.
- Exécution de code lors de l’analyse d’un dépôt.
- Introduction d’un chemin local non portable dans la documentation.
- Suivi Git accidentel des caches ou des aperçus.
- Affaiblissement d’un test afin de masquer une régression de sécurité.

## Mesures de réduction des risques

- utiliser des générateurs déterministes lorsque possible;
- séparer l’aperçu de l’application;
- exiger une approbation pour les documents protégés;
- vérifier les empreintes des invariants;
- analyser le code sans l’exécuter;
- maintenir une suite de tests complète;
- vérifier `git diff` et `git status` avant commit;
- refuser les chemins absolus propres à une machine.

## Journaux et erreurs

- les messages d’erreur doivent être explicites;
- les exceptions ne doivent pas masquer un échec de sécurité;
- les valeurs sensibles doivent être expurgées;
- les chemins peuvent être affichés sans contenu secret;
- les rapports ne doivent contenir que les faits nécessaires.

## Sécurité Git

- ne pas suivre `.project-assistant/`;
- ne pas suivre `.venv/`;
- ne pas suivre les fichiers `.env.*.local`;
- examiner les fichiers non suivis avant un commit;
- ne pas utiliser `git add .` sans inspection;
- ne pas modifier les tests pour masquer une régression.

## Validation

Commandes recommandées :

```bash
pytest -q
project-assistant --help
project-assistant verify-invariants /chemin/vers/app-template
project-assistant document /chemin/du/projet --refresh --clean
git status --short
```

## Critères d’acceptation

- aucun secret n’apparaît dans `ProjectKnowledge`;
- aucun secret n’apparaît dans les aperçus;
- aucun chemin absolu local n’est généré;
- les documents protégés refusent une application non approuvée;
- les empreintes détectent les modifications non autorisées;
- les analyseurs n’exécutent pas le code inspecté;
- les caches et aperçus restent hors de Git;
- toute la suite de tests réussit.

## Réponse à un incident

En cas de secret exposé :

1. arrêter la diffusion du document ou du rapport;
2. retirer le fichier de l’historique si nécessaire;
3. révoquer ou remplacer le secret;
4. identifier l’analyseur ou le générateur responsable;
5. ajouter un test de non-régression;
6. régénérer les documents concernés;
7. vérifier les autres projets enregistrés.
