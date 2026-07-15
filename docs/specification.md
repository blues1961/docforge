# Spécification — project-assistant

<!--
Document généré en aperçu par project-assistant.
Ce document définit les exigences du produit.
-->

## Objectif

Analyser des dépôts logiciels, construire une connaissance structurée, générer leur documentation et vérifier leur conformité.

## Identité du produit

- Projet : `project-assistant`.
- Paquet : `project-assistant`.
- Version : `0.1.0`.
- Python requis : `>=3.11`.

## Périmètre

- scanner des dépôts locaux;
- détecter les langages, frameworks et technologies;
- détecter un profil de projet;
- construire et sérialiser ProjectKnowledge;
- générer des documents déterministes;
- utiliser un LLM local uniquement lorsque nécessaire;
- produire des aperçus sans modifier les fichiers cibles;
- appliquer explicitement des documents validés;
- auditer plusieurs projets enregistrés;
- protéger les invariants approuvés.

## Hors périmètre

- modifier automatiquement le code métier des projets;
- déployer directement les applications analysées;
- gérer ou stocker les secrets des projets;
- remplacer une validation humaine pour les documents protégés;
- présenter une heuristique comme un fait certain.

## Concepts principaux

### Projet

Dépôt local analysé par project-assistant. Le projet reste la source des faits techniques.

### Profil

Famille de projet déterminée à partir d’un score de confiance et de preuves explicites.

### ProjectKnowledge

Modèle structuré et sérialisable regroupant les faits réutilisés par les générateurs.

### Politique documentaire

Liste des documents obligatoires, optionnels, déterministes et protégés pour un profil.

### Aperçu

Document généré sous `.project-assistant/preview` sans modification du fichier cible.

### Application

Copie explicite d’un aperçu validé vers le dépôt à l’aide de la commande `apply`.

## Profils pris en charge

- `django-react`
- `python-cli`
- `generic`

## Politique documentaire du profil

### Documents obligatoires

- `README.md`
- `README_DEV.md`
- `CODEX_START.md`
- `AGENTS.md`
- `INVARIANTS.md`
- `docs/architecture.md`
- `docs/cli.md`
- `docs/specification.md`
- `docs/configuration.md`
- `docs/security.md`

### Documents déterministes

- `README.md`
- `README_DEV.md`
- `CODEX_START.md`
- `AGENTS.md`
- `INVARIANTS.md`
- `docs/architecture.md`
- `docs/cli.md`
- `docs/configuration.md`
- `docs/specification.md`
- `docs/security.md`

### Documents protégés

- `INVARIANTS.md`

## Interface CLI

- `project-assistant` → `project_assistant.cli:app`

## Exigences fonctionnelles

- **EF-001** — Le système doit accepter le chemin d’un projet local.
- **EF-002** — Le système doit scanner le projet sans lire ses secrets.
- **EF-003** — Le système doit détecter les technologies à partir de preuves présentes dans le dépôt.
- **EF-004** — Le système doit sélectionner le profil spécialisé ayant le meilleur score valide.
- **EF-005** — Le système doit utiliser le profil generic lorsqu’aucun profil spécialisé n’atteint le seuil minimal.
- **EF-006** — Le système doit construire ProjectKnowledge une seule fois par cycle documentaire.
- **EF-007** — Le système doit sélectionner les documents selon la politique du profil.
- **EF-008** — Le système doit privilégier les générateurs déterministes.
- **EF-009** — Le système doit écrire les documents dans .project-assistant/preview.
- **EF-010** — Le système doit exiger une action apply explicite.
- **EF-011** — Le système doit préserver les sections locales balisées.
- **EF-012** — Le système doit refuser l’application d’un document protégé sans autorisation explicite.
- **EF-013** — Le système doit pouvoir enregistrer et auditer plusieurs projets.
- **EF-014** — Le système doit produire des rapports de conformité.

## Exigences non fonctionnelles

- **ENF-001** — Les sorties déterministes doivent être reproductibles.
- **ENF-002** — Les collections produites doivent avoir un ordre stable.
- **ENF-003** — Les erreurs doivent être explicites et ne doivent pas être masquées.
- **ENF-004** — Les analyseurs doivent gérer les fichiers absents ou invalides.
- **ENF-005** — L’ajout d’un profil ne doit pas modifier le comportement des profils existants.
- **ENF-006** — Les générateurs ne doivent pas rescanner le dépôt.
- **ENF-007** — La logique métier doit rester hors de cli.py lorsque possible.
- **ENF-008** — Le schéma de ProjectKnowledge doit être versionné.
- **ENF-009** — Toute fonctionnalité doit être couverte par des tests.

## Exigences de sécurité

- **SEC-001** — Le contenu de .env.local ne doit jamais être lu ou reproduit.
- **SEC-002** — Aucun secret ne doit apparaître dans un document, rapport ou journal.
- **SEC-003** — Les aperçus ne doivent jamais être appliqués automatiquement.
- **SEC-004** — INVARIANTS.md doit rester protégé par owner-approved.
- **SEC-005** — Les empreintes approuvées doivent détecter les modifications non autorisées.
- **SEC-006** — Les chemins absolus propres à une machine ne doivent pas être générés.
- **SEC-007** — Les caches et aperçus ne doivent pas être suivis par Git.

## Règles métier

1. Les faits détectés prévalent sur les descriptions inventées.
2. Un profil spécialisé valide prévaut sur le profil `generic`.
3. Un générateur déterministe prévaut sur un générateur LLM.
4. La génération d’un aperçu ne constitue pas une approbation.
5. Un document protégé exige une confirmation explicite du propriétaire.
6. Une application doit s’adapter aux invariants; les invariants ne sont pas adaptés automatiquement.

## Critères d’acceptation

- [ ] project-assistant --help s’exécute sans erreur.
- [ ] project-assistant profile détecte python-cli pour ce dépôt.
- [ ] project-assistant knowledge produit un cache JSON valide.
- [ ] project-assistant document --refresh --clean ne modifie aucun document cible.
- [ ] Les documents générés correspondent à la politique du profil.
- [ ] Une tentative d’application de INVARIANTS.md sans owner-approved échoue.
- [ ] pytest -q réussit entièrement.
- [ ] Aucun secret ou chemin absolu propre à une machine n’apparaît dans les documents générés.

## Limites connues

- Les profils hugo-static et 3d-design ne sont pas encore implémentés.
- docs/cli.md, docs/configuration.md et docs/security.md ne possèdent pas encore leurs générateurs.
- La compatibilité des anciens caches ProjectKnowledge doit encore être formalisée.
- cli.py contient encore une partie importante de l’orchestration.
- Certaines détections de technologies restent génériques.

## Évolutions prévues

- ajouter le profil `hugo-static`;
- ajouter le profil `3d-design`;
- générer `docs/cli.md`;
- générer `docs/configuration.md`;
- générer `docs/security.md`;
- alléger progressivement `cli.py`;
- versionner formellement les migrations du cache;
- ajouter des contrôles de fraîcheur documentaire.

## Validation de la spécification

La spécification est considérée respectée lorsque :

```bash
python -m py_compile project_assistant/cli.py
pytest -q
project-assistant --help
project-assistant profile .
project-assistant knowledge .
project-assistant document . --refresh --clean
```

réussissent sans compromettre les protections, les secrets ou le comportement des profils existants.
