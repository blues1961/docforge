# Validation de fidélité des commandes

## Résumé
- Commandes documentables : 23
- Couverture `command_path` : 23/23 (100.0%)
- Couverture d’invocation exécutable : 23/23 (100.0%)
- Erreurs strictes : 0
- Avertissements : 38

## Couverture
- Commandes totalement absentes : aucune
- Commandes présentes seulement par `command_path` : aucune
- Invocations complètes manquantes : aucune

## Erreurs strictes
- Aucune.

## Avertissements
- `analyze`: Groupe d’options connu omis dans le guide assemblé : `--json`.
- `analyze-template`: Groupe d’options connu omis dans le guide assemblé : `--no-cache`.
- `analyze-template`: Groupe d’options connu omis dans le guide assemblé : `--json`.
- `apply`: Groupe d’options connu omis dans le guide assemblé : `--owner-approved`.
- `apply`: Groupe d’options connu omis dans le guide assemblé : `--allow-dirty`.
- `approve-invariants`: Groupe d’options connu omis dans le guide assemblé : `--owner-approved`.
- `audit-all`: Groupe d’options connu omis dans le guide assemblé : `--template`.
- `audit-all`: Groupe d’options connu omis dans le guide assemblé : `--show-findings`.
- `audit-diff`: Groupe d’options connu omis dans le guide assemblé : `--current`.
- `audit-diff`: Groupe d’options connu omis dans le guide assemblé : `--previous`.
- `audit-diff`: Groupe d’options connu omis dans le guide assemblé : `--output / -o`.
- `audit-report`: Groupe d’options connu omis dans le guide assemblé : `--template`.
- `audit-report`: Groupe d’options connu omis dans le guide assemblé : `--output-dir / -o`.
- `document`: Groupe d’options connu omis dans le guide assemblé : `--profile / -p`.
- `document`: Groupe d’options connu omis dans le guide assemblé : `--write`.
- `generate`: Groupe d’options connu omis dans le guide assemblé : `--model / -m`.
- `generate`: Groupe d’options connu omis dans le guide assemblé : `--clean`.
- `generate`: Groupe d’options connu omis dans le guide assemblé : `--refresh`.
- `generate-global-invariants`: Groupe d’options connu omis dans le guide assemblé : `--output / -o`.
- `init`: Groupe d’options connu omis dans le guide assemblé : `--force`.
- `knowledge`: Groupe d’options connu omis dans le guide assemblé : `--output / -o`.
- `knowledge`: Groupe d’options connu omis dans le guide assemblé : `--json`.
- `refresh-all`: Groupe d’options connu omis dans le guide assemblé : `--clean`.
- `remediation-plan`: Groupe d’options connu omis dans le guide assemblé : `--template`.
- `remediation-plan`: Groupe d’options connu omis dans le guide assemblé : `--output / -o`.
- `status-all`: Groupe d’options connu omis dans le guide assemblé : `--template`.
- `status-all`: Groupe d’options connu omis dans le guide assemblé : `--show-details`.
- `verify`: Groupe d’options connu omis dans le guide assemblé : `--profile / -p`.
- `manual prepare`: Groupe d’options connu omis dans le guide assemblé : `--clean`.
- `manual prepare`: Groupe d’options connu omis dans le guide assemblé : `--mode`.
- `manual prepare`: Groupe d’options connu omis dans le guide assemblé : `--output-dir`.
- `manual prepare`: Groupe d’options connu omis dans le guide assemblé : `--context-budget`.
- `manual validate`: Groupe d’options connu omis dans le guide assemblé : `--project-root`.
- `manual validate`: Groupe d’options connu omis dans le guide assemblé : `--manual-dir`.
- `manual validate`: Groupe d’options connu omis dans le guide assemblé : `--json`.
- `manual validate`: Groupe d’options connu omis dans le guide assemblé : `--document-id`.
- `projects add`: Groupe d’options connu omis dans le guide assemblé : `--name`.
- `projects add`: Groupe d’options connu omis dans le guide assemblé : `--profile / -p`.

## Détail par commande
### `analyze`
- Invocation attendue : `docforge analyze`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --json
- Alias présentés : aucun
- Alias non présentés : --json
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : PATH
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `analyze`

### `analyze-template`
- Invocation attendue : `docforge analyze-template`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --no-cache, --json
- Alias présentés : aucun
- Alias non présentés : --no-cache, --json
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : PATH
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `analyze-template`

### `apply`
- Invocation attendue : `docforge apply`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --owner-approved, --allow-dirty
- Alias présentés : aucun
- Alias non présentés : --owner-approved, --allow-dirty
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH, DOCUMENTS
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : PATH, DOCUMENTS
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `apply`

### `approve-invariants`
- Invocation attendue : `docforge approve-invariants`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --owner-approved
- Alias présentés : aucun
- Alias non présentés : --owner-approved
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : TEMPLATE_PATH
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : TEMPLATE_PATH
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `approve-invariants`

### `audit-all`
- Invocation attendue : `docforge audit-all`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --template, --show-findings
- Alias présentés : aucun
- Alias non présentés : --template, --show-findings
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : aucun
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : aucun
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `audit-all`

### `audit-diff`
- Invocation attendue : `docforge audit-diff`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --current, --previous, --output / -o
- Alias présentés : aucun
- Alias non présentés : --current, --previous, --output, -o
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : aucun
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : aucun
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `audit-diff`

### `audit-report`
- Invocation attendue : `docforge audit-report`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --template, --output-dir / -o
- Alias présentés : aucun
- Alias non présentés : --template, --output-dir, -o
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : aucun
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : aucun
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `audit-report`

### `document`
- Invocation attendue : `docforge document`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : --clean, --refresh
- Groupes d’options connus absents : --profile / -p, --write
- Alias présentés : --refresh, --clean
- Alias non présentés : --profile, -p, --write
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : PATH
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `document`

### `generate`
- Invocation attendue : `docforge generate`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --model / -m, --clean, --refresh
- Alias présentés : aucun
- Alias non présentés : --model, -m, --clean, --refresh
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : PATH
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `generate`

### `generate-global-invariants`
- Invocation attendue : `docforge generate-global-invariants`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --output / -o
- Alias présentés : aucun
- Alias non présentés : --output, -o
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : TEMPLATE_PATH
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : TEMPLATE_PATH
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `generate-global-invariants`

### `init`
- Invocation attendue : `docforge init`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --force
- Alias présentés : aucun
- Alias non présentés : --force
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : PATH
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `init`

### `knowledge`
- Invocation attendue : `docforge knowledge`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --output / -o, --json
- Alias présentés : aucun
- Alias non présentés : --output, -o, --json
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : PATH
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `knowledge`

### `profile`
- Invocation attendue : `docforge profile`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : aucun
- Alias présentés : aucun
- Alias non présentés : aucun
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : PATH
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `profile`

### `refresh-all`
- Invocation attendue : `docforge refresh-all`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --clean
- Alias présentés : aucun
- Alias non présentés : --clean
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : aucun
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : aucun
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `refresh-all`

### `remediation-plan`
- Invocation attendue : `docforge remediation-plan`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --template, --output / -o
- Alias présentés : aucun
- Alias non présentés : --template, --output, -o
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : aucun
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : aucun
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `remediation-plan`

### `status-all`
- Invocation attendue : `docforge status-all`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --template, --show-details
- Alias présentés : aucun
- Alias non présentés : --template, --show-details
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : aucun
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : aucun
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `status-all`

### `verify`
- Invocation attendue : `docforge verify`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --profile / -p
- Alias présentés : aucun
- Alias non présentés : --profile, -p
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : PATH
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `verify`

### `verify-invariants`
- Invocation attendue : `docforge verify-invariants`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : aucun
- Alias présentés : aucun
- Alias non présentés : aucun
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : TEMPLATE_PATH
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : TEMPLATE_PATH
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `verify-invariants`

### `manual prepare`
- Invocation attendue : `docforge manual prepare`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --clean, --mode, --output-dir, --context-budget
- Alias présentés : aucun
- Alias non présentés : --clean, --mode, --output-dir, --context-budget
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : PATH
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `manual prepare`

### `manual validate`
- Invocation attendue : `docforge manual validate`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --project-root, --manual-dir, --json, --document-id
- Alias présentés : aucun
- Alias non présentés : --project-root, --manual-dir, --json, --document-id
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : MARKDOWN_FILE
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : MARKDOWN_FILE
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `manual validate`

### `projects add`
- Invocation attendue : `docforge projects add`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : --name, --profile / -p
- Alias présentés : aucun
- Alias non présentés : --name, --profile, -p
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : PATH
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `projects add`

### `projects list`
- Invocation attendue : `docforge projects list`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : aucun
- Alias présentés : aucun
- Alias non présentés : aucun
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : aucun
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : aucun
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `projects list`

### `projects remove`
- Invocation attendue : `docforge projects remove`
- Présence : command_path=oui, invocation=oui
- Groupes d’options connus présents : aucun
- Groupes d’options connus absents : aucun
- Alias présentés : aucun
- Alias non présentés : aucun
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : IDENTIFIER
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : IDENTIFIER
- Invocations complètes absentes : non
- Syntaxes potentiellement non exécutables : `projects remove`
