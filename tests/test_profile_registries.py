from pathlib import Path

from project_assistant.analyzer_registry import (
    AnalyzerRegistry,
)
from project_assistant.document_generator_registry import (
    DocumentGeneratorRegistry,
)
from project_assistant.knowledge import (
    ProjectKnowledgeBuilder,
)
from project_assistant.profiles import (
    GenericProfile,
    PythonCliProfile,
)
from project_assistant.scanners import FileSystemScanner


def _create_python_cli(root: Path) -> None:
    package = root / "demo_cli"
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

    (root / "tests").mkdir()

    (root / "pyproject.toml").write_text(
        """
[project]
name = "demo-cli"
version = "0.1.0"
requires-python = ">=3.11"

[project.scripts]
demo-cli = "demo_cli.cli:app"
""",
        encoding="utf-8",
    )


def test_python_cli_profile_builds_analyzer_registry() -> None:
    profile = PythonCliProfile()

    registry = profile.build_analyzer_registry()

    assert isinstance(registry, AnalyzerRegistry)
    assert "pyproject" in registry.names(
        profile_name="python-cli"
    )
    assert "cli" in registry.names(
        profile_name="python-cli"
    )
    assert "security" in registry.names(
        profile_name="python-cli"
    )


def test_generic_profile_builds_analyzer_registry() -> None:
    profile = GenericProfile()

    registry = profile.build_analyzer_registry()

    assert isinstance(registry, AnalyzerRegistry)
    assert "pyproject" in registry.names(
        profile_name="generic"
    )
    assert "cli" not in registry.names(
        profile_name="generic"
    )


def test_python_cli_profile_builds_generator_registry(
    tmp_path: Path,
) -> None:
    _create_python_cli(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    knowledge = (
        ProjectKnowledgeBuilder()
        .build(project)
    )

    profile = PythonCliProfile()
    registry = (
        profile.build_document_generator_registry(
            knowledge
        )
    )

    assert isinstance(
        registry,
        DocumentGeneratorRegistry,
    )

    supported = registry.supported_documents(
        profile.name
    )

    assert "README.md" in supported
    assert "docs/cli.md" in supported
    assert "docs/configuration.md" in supported
    assert "docs/security.md" in supported


def test_profile_registry_factories_return_new_instances() -> None:
    profile = PythonCliProfile()

    first = profile.build_analyzer_registry()
    second = profile.build_analyzer_registry()

    assert first is not second
