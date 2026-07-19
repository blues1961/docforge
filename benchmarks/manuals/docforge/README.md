# Benchmarks manuels DocForge

## Références

`benchmarks/manuals/docforge/v0.9/` est la référence historique. Elle reste utile pour l’archivage et pour expliquer l’origine de `smoke-001`, mais elle mélange des intrants et des diagnostics hétérogènes.

`benchmarks/manuals/docforge/v0.10/` est la première référence corrigée destinée aux comparaisons homogènes. Elle fige :

- `manual-knowledge.json`
- `manual-manifest.json`
- `manual-prompt.md`
- `manual-prompt-prepared.md`
- `section-prompts/`
- `section-contexts/`
- `docforge-guide-usager.md`
- `validation.json`
- `command-coverage.txt`
- `command-fidelity.json`
- `command-fidelity.md`
- `reference-provenance.json`
- `preparation.txt`
- `checksums.sha256`

Le guide de `v0.10` provient du contenu historique `v0.9`, recopié à l’identique puis validé contre les intrants `v0.10`. Cette provenance est documentée dans `reference-provenance.json`.

## Historique

`smoke-001` sous `benchmarks/manuals/docforge/runs/v0.9/qwen3.5-4b/` est un essai diagnostique hétérogène. Il ne doit pas être utilisé comme base de comparaison homogène avec `v0.10`.

L’incohérence historique connue de `v0.9` reste documentée dans `reference-metadata.json` : `manual-manifest.json` y conserve `command_provenance_summary.total_detected = 0`, alors que la couverture CLI réelle est `23/23`.

## Référence vs exécutions

Les références figées vivent sous `benchmarks/manuals/docforge/v0.9/` et `benchmarks/manuals/docforge/v0.10/`.

Les exécutions de benchmark vivent sous `benchmarks/manuals/docforge/runs/<version>/<modele>/<run-id>/`. Elles sont locales et ignorées par Git : elles peuvent contenir des réponses brutes Ollama, des temps d’exécution et des chemins propres à la machine. Les références figées et leurs empreintes sont les artefacts versionnés.

Une exécution conserve les réponses brutes d’Ollama, le guide assemblé, les diagnostics de validation, les temps et un résumé orienté revue humaine.

## Paramètres officiels

Pour les benchmarks homogènes `v0.10`, utiliser :

- `--num-ctx 12288`
- `--max-output-tokens 4096`
- `--temperature 0`
- `--seed 42`
- `--timeout-seconds 3600`

## Vérification sans génération

```bash
python scripts/run_docforge_manual_benchmark.py \
  --model qwen3.5:4b \
  --reference-version v0.10 \
  --run-id verification-v010 \
  --num-ctx 12288 \
  --max-output-tokens 4096 \
  --temperature 0 \
  --seed 42 \
  --timeout-seconds 3600 \
  --dry-run
```

Ce mode vérifie la référence, prépare l’arborescence d’essai et n’appelle pas Ollama.

## Premier benchmark homogène réel

```bash
python scripts/run_docforge_manual_benchmark.py \
  --model qwen3.5:4b \
  --reference-version v0.10 \
  --run-id smoke-010 \
  --num-ctx 12288 \
  --max-output-tokens 4096 \
  --temperature 0 \
  --seed 42 \
  --timeout-seconds 3600
```

## Réassemblage sans Ollama

```bash
python scripts/run_docforge_manual_benchmark.py \
  --model qwen3.5:4b \
  --reference-version v0.10 \
  --run-id smoke-010 \
  --num-ctx 12288 \
  --max-output-tokens 4096 \
  --temperature 0 \
  --seed 42 \
  --timeout-seconds 3600 \
  --reassemble
```

Ce mode relit les `sections/*.md` déjà présents, reconstruit `guide-genere.md`, relance la validation et met à jour le manifeste sans aucun appel HTTP vers Ollama. Il refuse l’opération si une section attendue est absente ou incomplète.

## Validation

Chaque essai non dry-run assemble `guide-genere.md`, puis exécute `scripts/verify_docforge_manual_reference.sh` en mode référence figée. Pour `v0.10`, la validation combine :

- la validation Markdown du guide assemblé ;
- la couverture des commandes `command_path` et `invocation` ;
- la fidélité des commandes et options à partir de `ManualKnowledge`.

## Emplacement des résultats

Chaque essai écrit au minimum :

- `run-manifest.json`
- `sections/*.md`
- `sections/*.response.json`
- `guide-genere.md`
- `validation/`
- `comparison.json`
- `timing.json`
- `benchmark-summary.md`
- `run.log`
- `checksums.sha256`

## Comparer deux essais

Comparer en priorité :

- `comparison.json`
- `benchmark-summary.md`
- `validation/command-coverage.txt`
- `validation/command-fidelity.json`
- `guide-genere.md`

La similarité textuelle seule ne constitue pas un jugement de qualité. La comparaison finale doit rester humaine face au guide ChatGPT de référence.

## Coût temporel attendu

Le protocole traite 21 sections. Sur CPU local, un modèle compact peut déjà prendre plusieurs minutes ; un modèle plus grand peut prendre sensiblement plus longtemps. La reprise permet d’éviter de rejouer les sections déjà générées après une interruption.
