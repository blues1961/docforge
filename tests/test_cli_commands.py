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
