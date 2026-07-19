from docforge.manual_deterministic import ManualDeterministicContentBuilder
from docforge.manual_knowledge import ManualCommand, ManualCommandParameter, ManualConfiguration, ManualFactSource, ManualKnowledge, ManualProject
from docforge.manual_blueprint import ManualBlueprint
from docforge.validators.manual_markdown import ManualMarkdownValidator


def _knowledge():
    return ManualKnowledge(schema_version=3, project=ManualProject("demo", None, None, "python-cli", None, None, ManualFactSource("detected")), profile={}, installation=__import__("docforge.manual_knowledge", fromlist=["ManualInstallation"]).ManualInstallation(""), configuration=ManualConfiguration("~/.config/demo", ".demo", ".demo.yml", "reports", files=[{"path": ".demo.yml"}]))


def test_cli_reference_is_deterministic_and_contains_invocations():
    rendered = ManualDeterministicContentBuilder().render_section(_knowledge(), "cli-reference")
    assert rendered.startswith("### Entrées de la référence CLI")


def test_hybrid_validator_rejects_platform_path_and_automation_claims():
    diagnostics = ManualMarkdownValidator().validate(markdown="# Guide utilisateur de demo\n\nWindows utilise `~/.config/demo/unknown.yml` automatiquement.", knowledge=_knowledge(), blueprint=ManualBlueprint(profile_name="python-cli"))
    assert {item.code for item in diagnostics} >= {"MANUAL018", "MANUAL019", "MANUAL020"}


def test_protected_documents_only_associates_owner_approval_with_apply() -> None:
    knowledge = _knowledge()
    knowledge.security.protected_documents = ["INVARIANTS.md"]
    knowledge.commands = [
        ManualCommand(
            name="apply", command_path="apply", invocation="docforge apply", group=None, help=None,
            parameters=[ManualCommandParameter(name="--owner-approved", kind="option", required=False, flags=["--owner-approved"])],
        ),
        ManualCommand(
            name="document", command_path="document", invocation="docforge document", group=None, help=None,
            parameters=[ManualCommandParameter(name="--refresh", kind="option", required=False, flags=["--refresh"])],
        ),
    ]
    rendered = ManualDeterministicContentBuilder().render_section(knowledge, "protected-documents")
    assert "docforge apply" in rendered
    assert "[--owner-approved]" in rendered
    assert "docforge document" not in rendered
