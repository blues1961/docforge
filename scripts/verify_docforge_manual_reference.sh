#!/usr/bin/env bash
set -Eeuo pipefail

# Vérifie un guide utilisateur DocForge sans modifier les fichiers suivis par Git.
#
# Usage:
#   ./verify_docforge_manual_reference.sh GUIDE.md [PROMPT.md]
#
# Le script doit être exécuté depuis n'importe quel emplacement à l'intérieur
# du dépôt DocForge. Les artefacts temporaires sont supprimés automatiquement.

GUIDE_PATH="${1:-}"
PROMPT_PATH="${2:-}"

if [[ -z "$GUIDE_PATH" ]]; then
  echo "Usage: $0 GUIDE.md [PROMPT.md]" >&2
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
PREP_DIR="$TMP_ROOT/prepared"
RESULT_DIR="$TMP_ROOT/results"
mkdir -p "$PREP_DIR" "$RESULT_DIR"

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

run_step "Compilation de docforge/cli.py" \
  python -m py_compile docforge/cli.py

run_capture_step "Aide de la CLI" \
  "$RESULT_DIR/docforge-help.txt" \
  "${DOCFORGE[@]}" --help

run_capture_step "Suite de tests" \
  "$RESULT_DIR/pytest.txt" \
  pytest -q

run_capture_step "Préparation déterministe du manuel" \
  "$RESULT_DIR/manual-prepare.txt" \
  "${DOCFORGE[@]}" manual prepare . \
    --clean \
    --mode both \
    --output-dir "$PREP_DIR"

run_capture_step "Validation DocForge du guide" \
  "$RESULT_DIR/manual-validate.json" \
  "${DOCFORGE[@]}" manual validate "$GUIDE_PATH" \
    --project-root "$ROOT" \
    --manual-dir "$PREP_DIR" \
    --document-id manual \
    --json

run_step "Contrôles structurels complémentaires" \
  python - "$GUIDE_PATH" "$PREP_DIR" <<'PY'
import json
import re
import sys
from pathlib import Path

guide_path = Path(sys.argv[1])
prep_dir = Path(sys.argv[2])
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

expected_command_paths = []
if knowledge_path.exists():
    data = json.loads(knowledge_path.read_text(encoding="utf-8"))
    seen = set()
    for section in data.get("sections", []):
        commands = section.get("facts", {}).get("commands", [])
        for command in commands:
            command_path = command.get("command_path")
            if command_path and command_path not in seen:
                seen.add(command_path)
                expected_command_paths.append(command_path)

missing_command_references = [
    command_path
    for command_path in expected_command_paths
    if f"docforge {command_path}" not in guide
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
if missing_command_references:
    errors.append(
        "Commandes absentes de la référence : "
        + ", ".join(missing_command_references)
    )

print(f"Sections attendues présentes : {len(expected_sections) - len(missing_sections)}/{len(expected_sections)}")
print(f"Commandes attendues référencées : {len(expected_command_paths) - len(missing_command_references)}/{len(expected_command_paths)}")

if errors:
    for error in errors:
        print(f"ERREUR: {error}", file=sys.stderr)
    raise SystemExit(1)
PY

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
