from pathlib import Path

import pytest

from project_assistant.analyzer_registry import (
    AnalyzerRegistry,
    DuplicateAnalyzerError,
    RegisteredAnalyzer,
    UnknownAnalyzerError,
)
from project_assistant.models import Project


def _project(tmp_path: Path) -> Project:
    return Project(
        name="demo",
        root=tmp_path,
    )


def test_registry_resolves_analyzer(
    tmp_path: Path,
) -> None:
    registry = AnalyzerRegistry()

    registration = RegisteredAnalyzer(
        name="identity",
        analyze=lambda project: {
            "name": project.name,
        },
    )

    registry.register(registration)

    resolved = registry.resolve("identity")

    assert resolved is registration
    assert registry.analyze(
        "identity",
        _project(tmp_path),
    ) == {
        "name": "demo",
    }


def test_registry_rejects_duplicate_name() -> None:
    registry = AnalyzerRegistry()

    registration = RegisteredAnalyzer(
        name="identity",
        analyze=lambda project: project.name,
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
            analyze=lambda project: None,
        )
    )
    registry.register(
        RegisteredAnalyzer(
            name="architecture",
            analyze=lambda project: None,
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
            analyze=lambda project: None,
        )
    )
    registry.register(
        RegisteredAnalyzer(
            name="cli",
            analyze=lambda project: None,
            profiles=frozenset(
                {
                    "python-cli",
                }
            ),
        )
    )
    registry.register(
        RegisteredAnalyzer(
            name="api",
            analyze=lambda project: None,
            profiles=frozenset(
                {
                    "django-react",
                }
            ),
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


def test_empty_profile_set_means_all_profiles() -> None:
    registration = RegisteredAnalyzer(
        name="identity",
        analyze=lambda project: None,
    )

    assert registration.supports_profile(
        "python-cli"
    )
    assert registration.supports_profile(
        "django-react"
    )
    assert registration.supports_profile(
        "generic"
    )
