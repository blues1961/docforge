# docforge — Guide de développement

<!--
Document généré en aperçu par docforge.
-->

## Prérequis

- Python >=3.11;
- Git;
- un environnement virtuel Python;
- Ollama uniquement pour tester la génération LLM.

## Installation locale

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Structure du code

- `docforge/scanners/` : découverte des fichiers;
- `docforge/detectors/` : technologies;
- `docforge/analyzers/` : extraction des faits;
- `docforge/profiles/` : familles de projets;
- `docforge/generators/` : génération Markdown;
- `docforge/commands/` : opérations applicatives;
- `docforge/knowledge.py` : modèle central;
- `docforge/documentation_pipeline.py` : pipeline;
- `docforge/cli.py` : commandes Typer;
- `tests/` : tests automatisés.

## Environnement de développement

L’environnement Python local est isolé dans `.venv`.

Version Python déclarée : `>=3.11`.

Backend de construction : `setuptools.build_meta`.

Les caches et aperçus de test utilisent :

```text
.project-assistant/
├── cache/
└── preview/
```

## Commandes de développement

Afficher l’aide :

```bash
docforge --help
```

Compiler les fichiers modifiés :

```bash
python -m py_compile chemin/du/fichier.py
```

Lancer les tests :

```bash
pytest -q
```

Lancer un test ciblé :

```bash
pytest -q tests/test_fichier.py
```

## Ajout d’une fonctionnalité

1. créer ou modifier le modèle de faits;
2. ajouter l’analyseur ou le profil concerné;
3. ajouter le générateur déterministe;
4. intégrer le générateur au pipeline;
5. ajouter les tests unitaires;
6. ajouter un test CLI si une commande est créée;
7. exécuter toute la suite de tests.

## Ajout d’un profil

Un profil doit définir :

- son nom et son libellé;
- ses preuves de détection;
- son niveau de confiance;
- ses documents obligatoires;
- ses documents optionnels;
- ses documents déterministes;
- ses documents protégés.

Tout document déclaré déterministe doit être supporté par `DocumentationPipeline.SUPPORTED_DOCUMENTS`.

## Tests

Avant tout commit :

```bash
python -m py_compile docforge/cli.py
pytest -q
```

Les tests doivent couvrir au minimum :

- le cas nominal;
- les entrées manquantes ou invalides;
- la protection des secrets;
- la protection des invariants;
- l’import du module CLI;
- le comportement propre à chaque profil.

## Flux de travail Git

```bash
git status
git pull --ff-only
git switch -c type/description-courte
git diff
pytest -q
git add <fichiers>
git commit -m "type: description"
```

Ne pas ajouter au commit :

- `.venv/`;
- `.project-assistant/`;
- les caches Python;
- les rapports temporaires JSON;
- les fichiers de secrets provenant des projets analysés.

## Validation avant livraison

- tous les tests réussissent;
- `docforge --help` fonctionne;
- les nouvelles commandes apparaissent dans le test CLI;
- aucune ancienne référence supprimée ne subsiste;
- les profils existants conservent leur comportement;
- aucun secret n’est lu ou écrit dans les sorties;
- les invariants protégés ne sont pas modifiés;
- la documentation correspond au code.
