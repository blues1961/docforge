from pathlib import Path

from docforge.manual_deterministic import ManualDeterministicContentBuilder
from docforge.manual_knowledge import ManualKnowledgeBuilder
from docforge.profiles import ProfileDetector
from docforge.scanners import FileSystemScanner
from docforge.detectors import TechnologyDetector
from docforge.knowledge import ProjectKnowledgeBuilder
from docforge.validators import CommandFidelityValidator, CommandReferenceValidator


def _docforge_manual_knowledge():
    root = Path(__file__).resolve().parents[1]
    project = FileSystemScanner().scan(root)
    TechnologyDetector().detect(project)
    profile = ProfileDetector().resolve(project)
    knowledge = ProjectKnowledgeBuilder().build(project, profile_instance=profile)
    return ManualKnowledgeBuilder().build(
        project_root=root,
        knowledge=knowledge,
        profile_instance=profile,
    )


def test_cli_reference_has_all_structured_descriptions_and_signatures():
    knowledge = _docforge_manual_knowledge()
    rendered = ManualDeterministicContentBuilder().render_section(knowledge, "cli-reference")

    assert len(knowledge.commands) == 23
    assert all(command.description and command.description.summary for command in knowledge.commands)
    assert len({command.description.summary for command in knowledge.commands if command.description}) == 23
    assert not CommandReferenceValidator().validate(markdown=rendered, knowledge=knowledge, expected_command_count=23)
    fidelity = CommandFidelityValidator().validate(markdown=rendered, knowledge=knowledge)
    assert fidelity["command_path_coverage"]["present"] == 23
    assert fidelity["executable_invocation_coverage"]["present"] == 23
    assert fidelity["warning_count"] == 0


def test_cli_reference_separates_aliases_and_uses_value_metavars():
    knowledge = _docforge_manual_knowledge()
    rendered = ManualDeterministicContentBuilder().render_section(knowledge, "cli-reference")

    assert "docforge knowledge [PATH] [--output OUTPUT] [--json]" in rendered
    assert "Alias : `-o`." in rendered
    assert "--output / -o" not in rendered
    assert "#### `projects list`" in rendered
    assert "- Aucune option démontrée." in rendered
    assert "`PATH` (requis)" in rendered


def test_cli_reference_marks_undocumented_effects_unresolved():
    knowledge = _docforge_manual_knowledge()
    rendered = ManualDeterministicContentBuilder().render_section(knowledge, "cli-reference")
    apply = next(command for command in knowledge.commands if command.command_path == "apply")

    assert apply.description is not None
    assert apply.description.outputs == []
    assert apply.description.provenance["outputs"].status == "unresolved"
    assert "Sorties, effets de bord et étape suivante : non résolus" in rendered


def test_v017_reference_persists_all_command_descriptions():
    import json

    root = Path("benchmarks/manuals/docforge/v0.17")
    payload = json.loads((root / "manual-knowledge.json").read_text(encoding="utf-8"))
    rendered = (root / "deterministic-sections/21-cli-reference.md").read_text(encoding="utf-8")

    commands = payload["commands"]
    assert payload["schema_version"] == 3
    assert len(commands) == 23
    assert all(item["description"]["summary"] for item in commands)
    assert all(item["description"]["provenance"]["behavior"]["status"] in {"detected", "derived", "configured", "unresolved"} for item in commands)
    assert "--output / -o" not in rendered
    assert "Alias : `-o`." in rendered
