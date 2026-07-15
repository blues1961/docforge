from pathlib import Path

import pytest

from project_assistant.analyzer_registry import (
    AnalysisContext,
    AnalyzerRegistry,
    CircularAnalyzerDependencyError,
    DuplicateAnalyzerError,
    MissingAnalyzerDependencyError,
    RegisteredAnalyzer,
    UnknownAnalyzerError,
)
from project_assistant.models import Project


def _project(tmp_path: Path) -> Project:
    return Project(
        name="demo",
        root=tmp_path,
    )


def _context(
    tmp_path: Path,
    *,
    profile_name: str = "generic",
) -> AnalysisContext:
    return AnalysisContext(
        project=_project(tmp_path),
        profile_name=profile_name,
    )


def test_registry_resolves_and_runs_analyzer(
    tmp_path: Path,
) -> None:
    registry = AnalyzerRegistry()

    registration = RegisteredAnalyzer(
        name="identity",
        analyze=lambda context: {
            "name": context.project.name,
        },
    )

    registry.register(registration)

    context = _context(tmp_path)

    assert registry.analyze(
        "identity",
        context,
    ) == {
        "name": "demo",
    }
    assert context.results["identity"] == {
        "name": "demo",
    }


def test_registry_rejects_duplicate_name() -> None:
    registry = AnalyzerRegistry()

    registration = RegisteredAnalyzer(
        name="identity",
        analyze=lambda context: context.project.name,
    )

    registry.register(registration)

    with pytest.raises(
        DuplicateAnalyzerError
    ):
        registry.register(registration)


def test_registry_rejects_unknown_analyzer() -> None:
    registry = AnalyzerRegistry()

    with pytest.raises(
        UnknownAnalyzerError
    ):
        registry.resolve("missing")


def test_registry_lists_analyzers_in_stable_order() -> None:
    registry = AnalyzerRegistry()

    registry.register(
        RegisteredAnalyzer(
            name="security",
            analyze=lambda context: None,
        )
    )
    registry.register(
        RegisteredAnalyzer(
            name="architecture",
            analyze=lambda context: None,
        )
    )

    assert [
        registration.name
        for registration in registry.registrations()
    ] == [
        "architecture",
        "security",
    ]


def test_registry_filters_analyzers_by_profile() -> None:
    registry = AnalyzerRegistry()

    registry.register(
        RegisteredAnalyzer(
            name="identity",
            analyze=lambda context: None,
        )
    )
    registry.register(
        RegisteredAnalyzer(
            name="cli",
            analyze=lambda context: None,
            profiles=frozenset({"python-cli"}),
        )
    )
    registry.register(
        RegisteredAnalyzer(
            name="api",
            analyze=lambda context: None,
            profiles=frozenset({"django-react"}),
        )
    )

    assert registry.names(
        profile_name="python-cli"
    ) == frozenset(
        {
            "identity",
            "cli",
        }
    )

    assert registry.names(
        profile_name="django-react"
    ) == frozenset(
        {
            "identity",
            "api",
        }
    )


def test_registry_executes_dependencies_first(
    tmp_path: Path,
) -> None:
    registry = AnalyzerRegistry()
    execution_order: list[str] = []

    registry.register(
        RegisteredAnalyzer(
            name="pyproject",
            analyze=lambda context: (
                execution_order.append("pyproject")
                or {"scripts": {"demo": "demo.cli:app"}}
            ),
        )
    )

    registry.register(
        RegisteredAnalyzer(
            name="cli",
            dependencies=("pyproject",),
            analyze=lambda context: (
                execution_order.append("cli")
                or context.require("pyproject")["scripts"]
            ),
        )
    )

    context = _context(
        tmp_path,
        profile_name="python-cli",
    )

    result = registry.analyze(
        "cli",
        context,
    )

    assert execution_order == [
        "pyproject",
        "cli",
    ]
    assert result == {
        "demo": "demo.cli:app",
    }


def test_registry_analyzes_each_item_once(
    tmp_path: Path,
) -> None:
    registry = AnalyzerRegistry()
    calls = {"base": 0}

    def analyze_base(
        context: AnalysisContext,
    ) -> str:
        calls["base"] += 1
        return "base"

    registry.register(
        RegisteredAnalyzer(
            name="base",
            analyze=analyze_base,
        )
    )
    registry.register(
        RegisteredAnalyzer(
            name="first",
            dependencies=("base",),
            analyze=lambda context: "first",
        )
    )
    registry.register(
        RegisteredAnalyzer(
            name="second",
            dependencies=("base",),
            analyze=lambda context: "second",
        )
    )

    registry.analyze_all(_context(tmp_path))

    assert calls["base"] == 1


def test_registry_rejects_missing_dependency(
    tmp_path: Path,
) -> None:
    registry = AnalyzerRegistry()

    registry.register(
        RegisteredAnalyzer(
            name="cli",
            dependencies=("pyproject",),
            analyze=lambda context: None,
        )
    )

    with pytest.raises(
        MissingAnalyzerDependencyError
    ):
        registry.analyze(
            "cli",
            _context(tmp_path),
        )


def test_registry_rejects_circular_dependencies(
    tmp_path: Path,
) -> None:
    registry = AnalyzerRegistry()

    registry.register(
        RegisteredAnalyzer(
            name="first",
            dependencies=("second",),
            analyze=lambda context: None,
        )
    )
    registry.register(
        RegisteredAnalyzer(
            name="second",
            dependencies=("first",),
            analyze=lambda context: None,
        )
    )

    with pytest.raises(
        CircularAnalyzerDependencyError
    ):
        registry.analyze(
            "first",
            _context(tmp_path),
        )


def test_context_require_rejects_missing_result(
    tmp_path: Path,
) -> None:
    context = _context(tmp_path)

    with pytest.raises(
        MissingAnalyzerDependencyError
    ):
        context.require("missing")


def test_analysis_context_carries_protected_documents(
    tmp_path: Path,
) -> None:
    context = AnalysisContext(
        project=_project(tmp_path),
        profile_name="python-cli",
        protected_documents=("INVARIANTS.md",),
    )

    assert context.protected_documents == (
        "INVARIANTS.md",
    )
