import hashlib
import json
from pathlib import Path

from docforge.manual_benchmark import (
    load_reference_bundle,
    verify_reference_checksums,
)


def test_reference_v010_is_autonomous_and_loadable() -> None:
    reference = load_reference_bundle("v0.10")

    assert len(reference.sections) == 21
    assert reference.prompt_file == "manual-prompt.md"
    assert reference.prompt_prepared_file == "manual-prompt-prepared.md"
    assert (reference.root / "docforge-guide-usager.md").is_file()
    assert (reference.root / "validation.json").is_file()
    assert (reference.root / "command-coverage.txt").is_file()
    assert (reference.root / "command-fidelity.json").is_file()
    assert (reference.root / "command-fidelity.md").is_file()
    assert (reference.root / "reference-provenance.json").is_file()
    assert (reference.root / "preparation.txt").is_file()


def test_reference_v010_has_23_commands_and_key_entries() -> None:
    reference_root = Path("benchmarks/manuals/docforge/v0.10")
    payload = json.loads((reference_root / "manual-knowledge.json").read_text(encoding="utf-8"))

    commands = payload["commands"]
    assert len(commands) == 23

    mapping = {item["command_path"]: item for item in commands}
    assert mapping["analyze-template"]["invocation"] == "docforge analyze-template"
    assert mapping["refresh-all"]["invocation"] == "docforge refresh-all"
    assert mapping["remediation-plan"]["invocation"] == "docforge remediation-plan"
    assert mapping["verify-invariants"]["invocation"] == "docforge verify-invariants"


def test_reference_v010_prompts_and_contexts_are_complete() -> None:
    reference_root = Path("benchmarks/manuals/docforge/v0.10")
    prompt_files = sorted((reference_root / "section-prompts").glob("*.md"))
    context_files = sorted((reference_root / "section-contexts").glob("*.json"))

    assert len(prompt_files) == 21
    assert len(context_files) == 21

    sample_prompt = (reference_root / "section-prompts/21-cli-reference.md").read_text(encoding="utf-8")
    assert "Utilise `command_path` pour identifier ou titrer une commande." in sample_prompt
    assert "Utilise `invocation` pour toute commande destinée à être copiée et exécutée." in sample_prompt
    assert "Ne reconstruis jamais une syntaxe de commande à partir de `name` seul." in sample_prompt
    assert "Ne cite que les options et paramètres associés à la commande dans ManualKnowledge." in sample_prompt


def test_reference_v010_guide_provenance_is_explicit() -> None:
    reference_root = Path("benchmarks/manuals/docforge/v0.10")
    provenance = json.loads((reference_root / "reference-provenance.json").read_text(encoding="utf-8"))
    source_path = Path(provenance["source_file"])
    source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()

    assert provenance["source_reference_version"] == "v0.9"
    assert provenance["guide_content_modified"] is False
    assert provenance["prepared_with_prompt_version_v0_10"] is False
    assert provenance["compatibility_validated_against_v0_10"] is True
    assert provenance["source_sha256"] == source_sha


def test_reference_v010_validation_results_cover_all_commands() -> None:
    reference_root = Path("benchmarks/manuals/docforge/v0.10")
    validation = json.loads((reference_root / "validation.json").read_text(encoding="utf-8"))
    fidelity = json.loads((reference_root / "command-fidelity.json").read_text(encoding="utf-8"))

    assert validation["manual_markdown_validation"]["valid"] is True
    assert validation["structure"]["expected_sections"] == 21
    assert validation["structure"]["present_sections"] == 21
    assert validation["command_coverage"]["command_path"]["present"] == 23
    assert validation["command_coverage"]["command_path"]["total"] == 23
    assert validation["command_coverage"]["executable_invocation"]["present"] == 23
    assert validation["command_coverage"]["executable_invocation"]["total"] == 23
    assert fidelity["strict_error_count"] == 0
    assert fidelity["unknown_command_mentions"] == []
    assert fidelity["unknown_options"] == []


def test_reference_v010_checksums_are_valid() -> None:
    reference_root = Path("benchmarks/manuals/docforge/v0.10")
    verified = verify_reference_checksums(reference_root)

    assert "docforge-guide-usager.md" in verified
    assert "manual-knowledge.json" in verified
    assert "manual-manifest.json" in verified
    assert "manual-prompt.md" in verified
    assert "manual-prompt-prepared.md" in verified
