import json
from pathlib import Path

from typer.testing import CliRunner

from docforge.cli import app


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
        "docforge/cli.py"
    ).read_text(encoding="utf-8")

    assert "Profil documentaire :[/bold]" in source
    assert "Profil logiciel détecté :[/bold]" in source
    assert (
        'f"[bold]Profil :[/bold] {config.profile}"'
        not in source
    )


def test_analyze_command_displays_detected_profile(tmp_path: Path) -> None:
    package = tmp_path / "docforge"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "cli.py").write_text(
        """
import typer

app = typer.Typer()


@app.command()
def inspect() -> None:
    pass
""",
        encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "demo-cli"
version = "0.1.0"
requires-python = ">=3.11"

[project.scripts]
demo-cli = "docforge.cli:app"
""",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["analyze", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert "Profil :" in result.stdout
    assert "python-cli" in result.stdout


def test_analyze_command_suppresses_django_env_findings_for_python_cli(tmp_path: Path) -> None:
    package = tmp_path / "docforge"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "cli.py").write_text(
        """
import typer

app = typer.Typer()


@app.command()
def inspect() -> None:
    pass
""",
        encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "demo-cli"
version = "0.1.0"
requires-python = ">=3.11"

[project.scripts]
demo-cli = "docforge.cli:app"
""",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["analyze", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert "python-cli" in result.stdout
    assert "ENV002" not in result.stdout
    assert "ENV003" not in result.stdout
    assert "ENV004" not in result.stdout
    assert "Aucune anomalie détectée." in result.stdout


def test_verify_command_does_not_crash_without_template_metadata(tmp_path: Path) -> None:
    package = tmp_path / "docforge"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "cli.py").write_text(
        """
import typer

app = typer.Typer()


@app.command()
def inspect() -> None:
    pass
""",
        encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "README_DEV.md").write_text("# Dev\n", encoding="utf-8")
    (tmp_path / "CODEX_START.md").write_text("# Start\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (tmp_path / "INVARIANTS.md").write_text("# Invariants\n", encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
    (docs / "specification.md").write_text("# Specification\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "demo-cli"
version = "0.1.0"
requires-python = ">=3.11"

[project.scripts]
demo-cli = "docforge.cli:app"
""",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["verify", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert "Conformité documentaire" in result.stdout
    assert "Traceback" not in result.stdout


def test_knowledge_json_outputs_pure_json(
    tmp_path: Path,
) -> None:
    package = tmp_path / "docforge"
    package.mkdir()
    (package / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )
    (package / "cli.py").write_text(
        "def main():\n    return None\n",
        encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "demo-cli"
version = "0.1.0"
requires-python = ">=3.11"

[project.scripts]
demo-cli = "docforge.cli:main"
""",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["knowledge", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["identity"]["name"] == tmp_path.name
    assert (
        tmp_path
        / ".docforge"
        / "cache"
        / "project-knowledge.json"
    ).is_file()
