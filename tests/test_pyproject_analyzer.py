from pathlib import Path

from project_assistant.analyzers import (
    PyprojectAnalyzer,
)
from project_assistant.scanners import (
    FileSystemScanner,
)


def test_pyproject_analyzer_extracts_package_metadata(
    tmp_path: Path,
) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "demo-cli"
version = "0.2.0"
description = "Outil de démonstration"
requires-python = ">=3.11"
dependencies = [
  "typer>=0.12",
  "rich>=13",
]

[project.optional-dependencies]
dev = [
  "pytest>=8",
  "ruff>=0.5",
]

[project.scripts]
demo-cli = "demo_cli.cli:app"
""",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    facts = PyprojectAnalyzer().analyze(project)

    assert facts.exists is True
    assert facts.package_name == "demo-cli"
    assert facts.version == "0.2.0"
    assert facts.requires_python == ">=3.11"
    assert facts.build_backend == "setuptools.build_meta"

    assert "typer>=0.12" in facts.dependencies
    assert "rich>=13" in facts.dependencies

    assert facts.optional_dependencies["dev"] == [
        "pytest>=8",
        "ruff>=0.5",
    ]

    assert facts.scripts == {
        "demo-cli": "demo_cli.cli:app"
    }


def test_pyproject_analyzer_handles_missing_file(
    tmp_path: Path,
) -> None:
    project = FileSystemScanner().scan(tmp_path)
    facts = PyprojectAnalyzer().analyze(project)

    assert facts.exists is False
    assert facts.package_name is None
    assert facts.dependencies == []
