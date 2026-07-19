#!/usr/bin/env bash
set -Eeuo pipefail

# Vérifie un guide utilisateur DocForge sans modifier les fichiers suivis par Git.
#
# Usage:
#   ./verify_docforge_manual_reference.sh [--reference-dir DIR] [--prepared-dir DIR] [--fast] [--results-dir DIR] GUIDE.md [PROMPT.md]
#
# Par défaut le script reconstitue des artefacts temporaires avec `docforge manual prepare`.
# Avec --reference-dir, il réutilise une référence figée et vérifie d’abord ses sommes SHA-256.

REFERENCE_DIR=""
PREPARED_DIR=""
FAST=0
RESULT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reference-dir)
      REFERENCE_DIR="$2"
      shift 2
      ;;
    --prepared-dir)
      PREPARED_DIR="$2"
      shift 2
      ;;
    --results-dir)
      RESULT_DIR="$2"
      shift 2
      ;;
    --fast)
      FAST=1
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [--reference-dir DIR] [--prepared-dir DIR] [--fast] [--results-dir DIR] GUIDE.md [PROMPT.md]"
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Option inconnue : $1" >&2
      exit 64
      ;;
    *)
      break
      ;;
  esac
done

GUIDE_PATH="${1:-}"
PROMPT_PATH="${2:-}"

if [[ -z "$GUIDE_PATH" ]]; then
  echo "Usage: $0 [--reference-dir DIR] [--prepared-dir DIR] [--fast] [--results-dir DIR] GUIDE.md [PROMPT.md]" >&2
  exit 64
fi

if [[ ! -f "$GUIDE_PATH" ]]; then
  echo "Guide introuvable : $GUIDE_PATH" >&2
  exit 66
fi

if [[ -n "$PROMPT_PATH" && ! -f "$PROMPT_PATH" ]]; then
  echo "Prompt introuvable : $PROMPT_PATH" >&2
  exit 66
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$ROOT" ]]; then
  echo "Ce script doit être exécuté dans le dépôt Git de DocForge." >&2
  exit 69
fi

cd "$ROOT"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/docforge-manual-reference.XXXXXX")"
TEMP_PREP_DIR="$TMP_ROOT/prepared"
if [[ -n "$RESULT_DIR" ]]; then
  mkdir -p "$RESULT_DIR"
else
  RESULT_DIR="$TMP_ROOT/results"
  mkdir -p "$RESULT_DIR"
fi

cleanup() {
  if [[ "${KEEP_TEMP:-0}" == "1" ]]; then
    echo "Artefacts temporaires conservés : $TMP_ROOT"
  else
    rm -rf "$TMP_ROOT"
  fi
}
trap cleanup EXIT

if command -v docforge >/dev/null 2>&1; then
  DOCFORGE=(docforge)
else
  DOCFORGE=(python -m docforge.cli)
fi

if [[ -n "$REFERENCE_DIR" ]]; then
  REFERENCE_DIR="$(python -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$REFERENCE_DIR")"
  if [[ ! -d "$REFERENCE_DIR" ]]; then
    echo "Référence introuvable : $REFERENCE_DIR" >&2
    exit 66
  fi
  PREP_DIR="$REFERENCE_DIR"
elif [[ -n "$PREPARED_DIR" ]]; then
  PREP_DIR="$(python -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$PREPARED_DIR")"
  if [[ ! -d "$PREP_DIR" ]]; then
    echo "Répertoire préparé introuvable : $PREP_DIR" >&2
    exit 66
  fi
else
  PREP_DIR="$TEMP_PREP_DIR"
  mkdir -p "$PREP_DIR"
fi

if [[ -n "$REFERENCE_DIR" && -z "$PROMPT_PATH" && -f "$REFERENCE_DIR/manual-prompt.md" ]]; then
  PROMPT_PATH="$REFERENCE_DIR/manual-prompt.md"
fi

if [[ "$FAST" -eq 1 && -z "$REFERENCE_DIR" && -z "$PREPARED_DIR" ]]; then
  echo "--fast exige --reference-dir ou --prepared-dir." >&2
  exit 64
fi

PASS=0
FAIL=0

run_step() {
  local name="$1"
  shift
  echo
  echo "==> $name"
  if "$@"; then
    echo "[OK] $name"
    PASS=$((PASS + 1))
  else
    local status=$?
    echo "[ÉCHEC:$status] $name" >&2
    FAIL=$((FAIL + 1))
  fi
}

run_capture_step() {
  local name="$1"
  local output_file="$2"
  shift 2
  echo
  echo "==> $name"
  if "$@" >"$output_file" 2>&1; then
    cat "$output_file"
    echo "[OK] $name"
    PASS=$((PASS + 1))
  else
    local status=$?
    cat "$output_file" >&2
    echo "[ÉCHEC:$status] $name" >&2
    FAIL=$((FAIL + 1))
  fi
}

if [[ "$FAST" -eq 0 ]]; then
  run_step "Compilation de docforge/cli.py" \
    python -m py_compile docforge/cli.py

  run_capture_step "Aide de la CLI" \
    "$RESULT_DIR/docforge-help.txt" \
    "${DOCFORGE[@]}" --help

  run_capture_step "Suite de tests" \
    "$RESULT_DIR/pytest.txt" \
    pytest -q
fi

if [[ -n "$REFERENCE_DIR" && -f "$REFERENCE_DIR/checksums.sha256" ]]; then
  run_capture_step "Vérification SHA-256 de la référence" \
    "$RESULT_DIR/reference-checksums.txt" \
    bash -lc "cd \"$REFERENCE_DIR\" && sha256sum -c checksums.sha256"
fi

if [[ -z "$REFERENCE_DIR" && -z "$PREPARED_DIR" ]]; then
  run_capture_step "Préparation déterministe du manuel" \
    "$RESULT_DIR/manual-prepare.txt" \
    "${DOCFORGE[@]}" manual prepare . \
      --clean \
      --mode both \
      --output-dir "$PREP_DIR"
fi

run_capture_step "Validation DocForge du guide" \
  "$RESULT_DIR/manual-validate.json" \
  "${DOCFORGE[@]}" manual validate "$GUIDE_PATH" \
    --project-root "$ROOT" \
    --manual-dir "$PREP_DIR" \
    --document-id manual \
    --json

run_step "Contrôles structurels complémentaires" \
  python - "$GUIDE_PATH" "$PREP_DIR" "$RESULT_DIR" <<'PYCODE'
import json
import re
import sys
from pathlib import Path

from docforge.validators import CommandFidelityValidator
from docforge.validators.command_fidelity import report_to_json

guide_path = Path(sys.argv[1])
prep_dir = Path(sys.argv[2])
results_dir = Path(sys.argv[3])
guide = guide_path.read_text(encoding="utf-8")

expected_sections = [
    "Présentation",
    "Public visé",
    "Prérequis",
    "Installation",
    "Démarrage rapide",
    "Concepts essentiels",
    "Analyse d’un projet",
    "Détection du profil",
    "Construction de ProjectKnowledge",
    "Génération documentaire",
    "Génération avec Ollama",
    "Révision des aperçus",
    "Application des documents",
    "Documents protégés",
    "Gestion des projets",
    "Audits et conformité",
    "Configuration",
    "Sécurité",
    "Dépannage",
    "Limites des informations disponibles",
    "Référence CLI",
]

headings = [
    re.sub(r"\s+#+\s*$", "", line[3:]).strip()
    for line in guide.splitlines()
    if line.startswith("## ")
]

missing_sections = [section for section in expected_sections if section not in headings]
order = [headings.index(section) for section in expected_sections if section in headings]
order_is_valid = order == sorted(order)

forbidden_patterns = {
    "chemin personnel /home": r"/home/[^/\s]+/",
    "citation interne oaicite": r"oaicite",
    "secret .env.local avec valeur": r"(?im)^\s*[A-Z][A-Z0-9_]*\s*=\s*\S+",
}

violations = [
    label for label, pattern in forbidden_patterns.items()
    if re.search(pattern, guide)
]

knowledge_path = prep_dir / "manual-knowledge.json"
manifest_path = prep_dir / "manual-manifest.json"

missing_artifacts = [
    str(path.name)
    for path in (knowledge_path, manifest_path)
    if not path.exists()
]

errors = []
if missing_sections:
    errors.append("Sections manquantes : " + ", ".join(missing_sections))
if not order_is_valid:
    errors.append("L’ordre des sections ne respecte pas le blueprint.")
if violations:
    errors.append("Motifs interdits : " + ", ".join(violations))
if missing_artifacts:
    errors.append("Artefacts de préparation manquants : " + ", ".join(missing_artifacts))

fidelity_report = {
    "documented_command_count": 0,
    "command_path_coverage": {"present": 0, "total": 0, "percent": 100.0},
    "executable_invocation_coverage": {"present": 0, "total": 0, "percent": 100.0},
    "strict_error_count": 0,
    "warning_count": 0,
    "unknown_command_mentions": [],
    "unknown_options": [],
    "totally_absent_commands": [],
    "command_path_only_commands": [],
    "missing_full_invocations": [],
    "strict_errors": [],
    "warnings": [],
    "commands": [],
    "classification": {},
}
if knowledge_path.exists():
    knowledge_payload = json.loads(knowledge_path.read_text(encoding="utf-8"))
    fidelity_report = CommandFidelityValidator().validate(
        markdown=guide,
        knowledge=knowledge_payload,
    )
    if "Référence CLI" in headings and not fidelity_report["documented_command_count"]:
        errors.append(
            "Aucune commande documentable trouvée dans manual-knowledge.json alors que la section Référence CLI est présente."
        )
    if fidelity_report["strict_error_count"]:
        errors.extend(
            issue["message"]
            for issue in fidelity_report["strict_errors"]
        )

command_coverage_path = results_dir / "command-coverage.txt"
coverage_lines = [
    f"Commandes détectées : {fidelity_report['documented_command_count']}",
    (
        "Couverture command_path : "
        f"{fidelity_report['command_path_coverage']['present']}/{fidelity_report['command_path_coverage']['total']}"
    ),
    (
        "Couverture invocation exécutable : "
        f"{fidelity_report['executable_invocation_coverage']['present']}/{fidelity_report['executable_invocation_coverage']['total']}"
    ),
    "",
    "Commandes totalement absentes : " + (", ".join(fidelity_report["totally_absent_commands"]) or "aucune"),
    "Commandes présentes seulement par command_path : " + (", ".join(fidelity_report["command_path_only_commands"]) or "aucune"),
    "Invocations complètes manquantes : " + (", ".join(fidelity_report["missing_full_invocations"]) or "aucune"),
]
command_coverage_path.write_text("\n".join(coverage_lines) + "\n", encoding="utf-8")
(results_dir / "command-fidelity.json").write_text(report_to_json(fidelity_report), encoding="utf-8")
(results_dir / "command-fidelity.md").write_text(
    CommandFidelityValidator().render_markdown_report(fidelity_report),
    encoding="utf-8",
)

print(f"Sections attendues présentes : {len(expected_sections) - len(missing_sections)}/{len(expected_sections)}")
print(
    "Couverture command_path : "
    f"{fidelity_report['command_path_coverage']['present']}/{fidelity_report['command_path_coverage']['total']}"
)
print(
    "Couverture invocation exécutable : "
    f"{fidelity_report['executable_invocation_coverage']['present']}/{fidelity_report['executable_invocation_coverage']['total']}"
)
if fidelity_report["totally_absent_commands"]:
    print("Commandes totalement absentes : " + ", ".join(fidelity_report["totally_absent_commands"]))
if fidelity_report["command_path_only_commands"]:
    print("Commandes présentes seulement par command_path : " + ", ".join(fidelity_report["command_path_only_commands"]))
if fidelity_report["missing_full_invocations"]:
    print("Invocations complètes manquantes : " + ", ".join(fidelity_report["missing_full_invocations"]))
if fidelity_report["unknown_options"]:
    print("Options inconnues ou inventées : " + ", ".join(fidelity_report["unknown_options"]))

if errors:
    for error in errors:
        print(f"ERREUR: {error}", file=sys.stderr)
    raise SystemExit(1)
PYCODE

echo
echo "==> Empreintes de reproductibilité"
sha256sum "$GUIDE_PATH"
if [[ -n "$PROMPT_PATH" ]]; then
  sha256sum "$PROMPT_PATH"
fi
if [[ -f "$PREP_DIR/manual-knowledge.json" ]]; then
  sha256sum "$PREP_DIR/manual-knowledge.json"
fi
if [[ -f "$PREP_DIR/manual-manifest.json" ]]; then
  sha256sum "$PREP_DIR/manual-manifest.json"
fi

echo
echo "Résultat : $PASS étape(s) réussie(s), $FAIL étape(s) en échec."

if [[ "$FAIL" -ne 0 ]]; then
  echo "La référence ne doit pas être figée tant que les échecs ne sont pas expliqués." >&2
  exit 1
fi

echo "Le guide satisfait les contrôles exécutés et peut être candidat au gel de référence."
