### Commandes d’installation

#### Créer un environnement virtuel

```bash
python -m venv .venv
```

Statut : fait dérivé; formulation prudente.

#### Activer l’environnement

```bash
source .venv/bin/activate
```

Statut : fait dérivé; formulation prudente.

#### Installer le paquet localement

```bash
python -m pip install -e .
```

Statut : fait dérivé; formulation prudente.

#### Installer les dépendances de développement

```bash
python -m pip install -e ".[dev]"
```

Statut : configuration déclarée; ce n’est pas un comportement observé.

#### Vérifier l’installation CLI

```bash
docforge --help
```

Statut : fait dérivé; formulation prudente.

#### Exécuter les tests

```bash
pytest -q
```

Statut : fait dérivé; formulation prudente.
