from pathlib import Path
from typer.testing import CliRunner

from project_assistant.cli import app


runner = CliRunner()


def test_cli_help_lists_main_commands() -> None:
    result = runner.invoke(
        app,
        ["--help"],
    )

    assert result.exit_code == 0
    assert "status-all" in result.stdout
    assert "audit-all" in result.stdout
    assert "audit-report" in result.stdout
    assert "remediation-plan" in result.stdout
    assert "knowledge" in result.stdout
    assert "profile" in result.stdout
    assert "verify-invariants" in result.stdout


def test_document_command_distinguishes_profiles() -> None:
    source = Path(
        "project_assistant/cli.py"
    ).read_text(encoding="utf-8")

    assert "Profil documentaire :[/bold]" in source
    assert "Profil logiciel détecté :[/bold]" in source
    assert (
        'f"[bold]Profil :[/bold] {config.profile}"'
        not in source
    )
