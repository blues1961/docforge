from pathlib import Path

from docforge.analyzer_registry import (
    AnalysisContext,
)
from docforge.default_analyzers import (
    build_default_analyzer_registry,
)
from docforge.scanners import FileSystemScanner


def _create_python_cli(root: Path) -> None:
    package = root / "docforge"
    package.mkdir()

    (package / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )

    (package / "cli.py").write_text(
        """
import typer

app = typer.Typer()


@app.command()
def check() -> None:
    pass
""",
        encoding="utf-8",
    )

    (root / "pyproject.toml").write_text(
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

    (root / ".gitignore").write_text(
        """
.docforge/
.venv/
__pycache__/
.pytest_cache/
""",
        encoding="utf-8",
    )


def test_default_registry_declares_first_analyzers() -> None:
    registry = build_default_analyzer_registry()

    assert registry.names(
        profile_name="python-cli"
    ) == frozenset(
        {
            "api",
            "architecture",
            "cli",
            "configuration",
            "deployment",
            "pyproject",
            "readme",
            "security",
            "specification",
        }
    )

    assert registry.names(
        profile_name="generic"
    ) == frozenset(
        {
            "api",
            "architecture",
            "configuration",
            "deployment",
            "pyproject",
            "readme",
            "security",
            "specification",
        }
    )


def test_default_registry_analyzes_python_cli(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    context = AnalysisContext(
        project=project,
        profile_name="python-cli",
    )

    results = (
        build_default_analyzer_registry()
        .analyze_all(context)
    )

    assert results["pyproject"].package_name == (
        "demo-cli"
    )
    assert results["configuration"].project_state_root == (
        ".docforge"
    )
    assert results["cli"].framework == "Typer"
    assert results["cli"].command_count == 1
    assert results["cli"].entry_points == {
        "demo-cli": "docforge.cli:app",
    }


def test_default_registry_skips_cli_for_generic_profile(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    context = AnalysisContext(
        project=project,
        profile_name="generic",
    )

    results = (
        build_default_analyzer_registry()
        .analyze_all(context)
    )

    assert "pyproject" in results
    assert "configuration" in results
    assert "cli" not in results


def test_default_registry_returns_second_analyzer_batch(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    context = AnalysisContext(
        project=project,
        profile_name="python-cli",
    )

    results = (
        build_default_analyzer_registry()
        .analyze_all(context)
    )

    assert "architecture" in results
    assert "deployment" in results
    assert "api" in results
    assert "specification" in results
    assert "readme" in results

    assert results["architecture"] is not None
    assert results["deployment"] is not None
    assert results["api"] is not None
    assert results["specification"] is not None
    assert results["readme"] is not None


def test_default_registry_builds_security_facts(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    context = AnalysisContext(
        project=project,
        profile_name="python-cli",
        protected_documents=("INVARIANTS.md",),
    )

    results = (
        build_default_analyzer_registry()
        .analyze_all(context)
    )

    security = results["security"]

    assert "INVARIANTS.md" in (
        security.protected_documents
    )
    assert security.controls
    assert any(
        control.identifier == "SEC-004"
        for control in security.controls
    )
