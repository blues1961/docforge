### Contrôles de sécurité démontrés

| Identifiant | Catégorie | Règle | Preuve |
|---|---|---|
| APP-SEC-001 | authentification | Des mécanismes d’authentification ont été détectés côté backend et/ou frontend. | Bearer token, JWT, SimpleJWT |
| APP-SEC-002 | administration | Une interface d’administration Django est détectée et doit être réservée aux comptes autorisés. | backend/calendar_project/urls.py |
| APP-SEC-003 | secrets | Des variables sensibles sont requises et leurs valeurs ne doivent pas être publiées dans le manuel. | ACCESS_TOKEN_LIFETIME_MIN, ADMIN_PASSWORD, DJANGO_SECRET_KEY, POSTGRES_PASSWORD, REFRESH_TOKEN_LIFETIME_DAYS |

Statut : fait dérivé; formulation prudente.
