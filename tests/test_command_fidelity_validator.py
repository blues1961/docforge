import json

import pytest

from docforge.validators import CommandFidelityValidator


def _knowledge_payload() -> dict:
    return {
        "commands": [
            {
                "name": "analyze-template",
                "command_path": "analyze-template",
                "invocation": "docforge analyze-template",
                "visibility": "public",
                "parameters": [
                    {"name": "PATH", "kind": "argument", "flags": []},
                    {"name": "--no-cache", "kind": "option", "flags": ["--no-cache"]},
                    {"name": "--json", "kind": "option", "flags": ["--json"]},
                ],
            },
            {
                "name": "refresh-all",
                "command_path": "refresh-all",
                "invocation": "docforge refresh-all",
                "visibility": "public",
                "parameters": [
                    {"name": "--clean", "kind": "option", "flags": ["--clean"]},
                ],
            },
            {
                "name": "projects add",
                "command_path": "projects add",
                "invocation": "docforge projects add",
                "visibility": "public",
                "parameters": [
                    {"name": "PATH", "kind": "argument", "flags": []},
                    {"name": "--name", "kind": "option", "flags": ["--name"]},
                    {"name": "--profile", "kind": "option", "flags": ["--profile", "-p"]},
                ],
            },
        ]
    }


def test_command_fidelity_distinguishes_command_path_and_invocation() -> None:
    markdown = """# Guide utilisateur de docforge

## Référence CLI

### `analyze-template`

```bash
analyze-template PATH [--no-cache] [--json]
```
"""
    report = CommandFidelityValidator().validate(
        markdown=markdown,
        knowledge=_knowledge_payload(),
    )

    analyze = next(item for item in report["commands"] if item["command_path"] == "analyze-template")
    refresh = next(item for item in report["commands"] if item["command_path"] == "refresh-all")

    assert analyze["presence"]["command_path_present"] is True
    assert analyze["presence"]["invocation_present"] is False
    assert analyze["presence"]["command_path_only"] is True
    assert "analyze-template" in report["command_path_only_commands"]
    assert "analyze-template" in report["missing_full_invocations"]
    assert refresh["presence"]["totally_absent"] is True
    assert "refresh-all" in report["totally_absent_commands"]
    analyze_warnings = [issue for issue in report["warnings"] if issue["command_path"] == "analyze-template"]
    assert len(analyze_warnings) == 1
    assert analyze_warnings[0]["code"] == "FIDELITY103"


def test_command_fidelity_accepts_full_invocation_and_nested_command() -> None:
    markdown = """# Guide utilisateur de docforge

## Référence CLI

```bash
docforge projects add PATH --name demo --profile python-cli
```
"""
    report = CommandFidelityValidator().validate(
        markdown=markdown,
        knowledge=_knowledge_payload(),
    )
    command = next(item for item in report["commands"] if item["command_path"] == "projects add")

    assert command["presence"]["invocation_present"] is True
    assert command["options"]["known_present_groups"] == ["--name", "--profile / -p"]
    assert command["options"]["presented_aliases"] == ["--name", "--profile"]
    assert command["positionals"]["present"] == ["PATH"]


def test_command_fidelity_groups_aliases_when_one_alias_is_present() -> None:
    markdown = """# Guide utilisateur de docforge

## Référence CLI

```bash
docforge projects add PATH -p python-cli
```
"""
    report = CommandFidelityValidator().validate(
        markdown=markdown,
        knowledge=_knowledge_payload(),
    )
    command = next(item for item in report["commands"] if item["command_path"] == "projects add")

    assert command["options"]["known_present_groups"] == ["--profile / -p"]
    assert command["options"]["known_missing_groups"] == ["--name"]
    assert command["options"]["presented_aliases"] == ["-p"]
    assert "--profile" in command["options"]["omitted_aliases"]
    assert not any(issue["fact"] == "--profile / -p" for issue in report["warnings"])


def test_command_fidelity_reports_missing_known_option_group_and_invented_option() -> None:
    markdown = """# Guide utilisateur de docforge

## Référence CLI

```bash
docforge projects add PATH --unknown value
```
"""
    report = CommandFidelityValidator().validate(
        markdown=markdown,
        knowledge=_knowledge_payload(),
    )
    command = next(item for item in report["commands"] if item["command_path"] == "projects add")

    assert command["options"]["known_missing_groups"] == ["--name", "--profile / -p"]
    assert command["options"]["unknown"] == ["--unknown"]
    assert any(issue["code"] == "FIDELITY002" for issue in report["strict_errors"])


def test_command_fidelity_detects_unknown_docforge_command() -> None:
    markdown = """# Guide utilisateur de docforge

## Référence CLI

`docforge unknown-command --json`
"""
    report = CommandFidelityValidator().validate(
        markdown=markdown,
        knowledge=_knowledge_payload(),
    )

    assert report["unknown_command_mentions"] == ["docforge unknown-command --json"]
    assert any(issue["code"] == "FIDELITY001" for issue in report["strict_errors"])


@pytest.mark.parametrize(
    ("markdown", "expected_unknown_mentions"),
    [
        ("`docforge -> docforge.cli:app`", []),
        ("`docforge = docforge.cli:app`", []),
        ("`docforge: commande terminale`", []),
        ("`docforge analyze-template PATH`", []),
        ("`docforge projects add PATH`", []),
        ("`docforge destroy`", ["docforge destroy"]),
        ("```bash\ndocforge analyze-template PATH --json\n```", []),
        ("Utilisez `docforge analyze-template PATH --json`.", []),
    ],
    ids=(
        "entry-point-mapping",
        "assignment",
        "colon-text",
        "known-command",
        "known-subcommand",
        "unknown-command",
        "fenced-code-invocation",
        "inline-code-invocation",
    ),
)
def test_command_fidelity_classifies_docforge_candidates(
    markdown: str,
    expected_unknown_mentions: list[str],
) -> None:
    report = CommandFidelityValidator().validate(
        markdown=markdown,
        knowledge=_knowledge_payload(),
    )


def test_command_fidelity_reads_commands_inside_code_blocks() -> None:
    markdown = """# Guide utilisateur de docforge

## Référence CLI

```bash
docforge analyze-template PATH --json
```
"""
    report = CommandFidelityValidator().validate(
        markdown=markdown,
        knowledge=_knowledge_payload(),
    )
    command = next(item for item in report["commands"] if item["command_path"] == "analyze-template")

    assert command["presence"]["invocation_present"] is True
    assert command["options"]["known_present_groups"] == ["--json"]


def test_command_fidelity_does_not_use_external_response_json_false_positive() -> None:
    guide_markdown = "# Guide utilisateur de docforge\n\n## Référence CLI\n\nAucune commande ici.\n"
    response_payload = json.dumps({"response": "docforge analyze-template PATH --json"}, ensure_ascii=False)
    assert "docforge analyze-template" in response_payload

    report = CommandFidelityValidator().validate(
        markdown=guide_markdown,
        knowledge=_knowledge_payload(),
    )

    assert "analyze-template" in report["totally_absent_commands"]
    assert "analyze-template" not in report["command_path_only_commands"]
