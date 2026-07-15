from project_assistant.default_analyzers import (
    build_default_analyzer_registry,
)


def test_default_analyzer_registry_is_created() -> None:
    registry = build_default_analyzer_registry()

    assert registry.registrations() == ()
