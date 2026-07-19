### Contrôles de sécurité démontrés

| Identifiant | Catégorie | Règle | Preuve |
|---|---|---|---|
| SEC-001 | secrets | Le manuel ne doit contenir aucun secret ni reproduire de valeur sensible. | — |
| SEC-002 | aperçu | La génération documentaire doit écrire dans .docforge/preview avant toute application. | .docforge/preview/ |
| SEC-003 | application | Un document généré ne doit être appliqué qu’après une commande explicite. | docforge apply |
| SEC-004 | invariants | Les documents protégés doivent exiger une autorisation explicite du propriétaire. | --owner-approved |
| SEC-005 | intégrité | Les invariants approuvés doivent pouvoir être vérifiés par empreinte. | invariant-baseline.json |
| SEC-006 | portabilité | Les documents générés ne doivent pas contenir de chemin absolu propre à une machine. | — |
| SEC-007 | Git | Les caches, aperçus, environnements virtuels et secrets ne doivent pas être suivis par Git. | .gitignore |
| SEC-008 | analyse statique | Les analyseurs doivent éviter d’importer ou d’exécuter le code des projets inspectés. | analyse AST du CLI |

Statut : fait détecté.
