# Validation de fidélité des commandes

## Résumé
- Commandes documentables : 23
- Couverture `command_path` : 23/23 (100.0%)
- Couverture d’invocation exécutable : 23/23 (100.0%)
- Erreurs strictes : 0
- Avertissements : 9

## Couverture
- Commandes totalement absentes : aucune
- Commandes présentes seulement par `command_path` : aucune
- Invocations complètes manquantes : aucune

## Erreurs strictes
- Aucune.

## Avertissements
- `audit-diff`: Option connue omise dans le guide assemblé : `-o`.
- `audit-report`: Option connue omise dans le guide assemblé : `-o`.
- `document`: Option connue omise dans le guide assemblé : `-p`.
- `generate`: Option connue omise dans le guide assemblé : `-m`.
- `generate-global-invariants`: Option connue omise dans le guide assemblé : `-o`.
- `knowledge`: Option connue omise dans le guide assemblé : `-o`.
- `remediation-plan`: Option connue omise dans le guide assemblé : `-o`.
- `verify`: Option connue omise dans le guide assemblé : `-p`.
- `projects add`: Option connue omise dans le guide assemblé : `-p`.

## Détail par commande
### `analyze`
- Invocation attendue : `docforge analyze`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --json
- Options connues manquantes : aucune
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : PATH
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `analyze-template`
- Invocation attendue : `docforge analyze-template`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --no-cache, --json
- Options connues manquantes : aucune
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : PATH
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `apply`
- Invocation attendue : `docforge apply`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --owner-approved, --allow-dirty
- Options connues manquantes : aucune
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH, DOCUMENTS
- Paramètres positionnels présents : PATH, DOCUMENTS
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `approve-invariants`
- Invocation attendue : `docforge approve-invariants`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --owner-approved
- Options connues manquantes : aucune
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : TEMPLATE_PATH
- Paramètres positionnels présents : TEMPLATE_PATH
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `audit-all`
- Invocation attendue : `docforge audit-all`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --show-findings, --template
- Options connues manquantes : aucune
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : aucun
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `audit-diff`
- Invocation attendue : `docforge audit-diff`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --current, --previous, --output
- Options connues manquantes : -o
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : aucun
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `audit-report`
- Invocation attendue : `docforge audit-report`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --template, --output-dir
- Options connues manquantes : -o
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : aucun
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `document`
- Invocation attendue : `docforge document`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --refresh, --clean, --profile, --write
- Options connues manquantes : -p
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : PATH
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `generate`
- Invocation attendue : `docforge generate`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --refresh, --clean, --model
- Options connues manquantes : -m
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : PATH
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `generate-global-invariants`
- Invocation attendue : `docforge generate-global-invariants`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --output
- Options connues manquantes : -o
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : TEMPLATE_PATH
- Paramètres positionnels présents : TEMPLATE_PATH
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `init`
- Invocation attendue : `docforge init`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --force
- Options connues manquantes : aucune
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : PATH
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `knowledge`
- Invocation attendue : `docforge knowledge`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --output, --json
- Options connues manquantes : -o
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : PATH
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `profile`
- Invocation attendue : `docforge profile`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : aucune
- Options connues manquantes : aucune
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : PATH
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : `profile`

### `refresh-all`
- Invocation attendue : `docforge refresh-all`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --clean
- Options connues manquantes : aucune
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : aucun
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `remediation-plan`
- Invocation attendue : `docforge remediation-plan`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --template, --output
- Options connues manquantes : -o
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : aucun
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `status-all`
- Invocation attendue : `docforge status-all`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --show-details, --template
- Options connues manquantes : aucune
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : aucun
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `verify`
- Invocation attendue : `docforge verify`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --profile
- Options connues manquantes : -p
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : PATH
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `verify-invariants`
- Invocation attendue : `docforge verify-invariants`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : aucune
- Options connues manquantes : aucune
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : TEMPLATE_PATH
- Paramètres positionnels présents : TEMPLATE_PATH
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `manual prepare`
- Invocation attendue : `docforge manual prepare`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --clean, --mode, --output-dir, --context-budget
- Options connues manquantes : aucune
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : PATH
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `manual validate`
- Invocation attendue : `docforge manual validate`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --project-root, --manual-dir, --json, --document-id
- Options connues manquantes : aucune
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : MARKDOWN_FILE
- Paramètres positionnels présents : MARKDOWN_FILE
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `projects add`
- Invocation attendue : `docforge projects add`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : --name, --profile
- Options connues manquantes : -p
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : PATH
- Paramètres positionnels présents : PATH
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `projects list`
- Invocation attendue : `docforge projects list`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : aucune
- Options connues manquantes : aucune
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : aucun
- Paramètres positionnels présents : aucun
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune

### `projects remove`
- Invocation attendue : `docforge projects remove`
- Présence : command_path=oui, invocation=oui
- Options connues présentes : aucune
- Options connues manquantes : aucune
- Options inconnues ou inventées : aucune
- Paramètres positionnels connus : IDENTIFIER
- Paramètres positionnels présents : IDENTIFIER
- Paramètres positionnels manquants : aucun
- Syntaxes potentiellement non exécutables : aucune
