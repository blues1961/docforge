from pathlib import Path

import pytest

from project_assistant.document_generator_registry import (
    DocumentGeneratorRegistry,
    DuplicateDocumentGeneratorError,
    RegisteredDocumentGenerator,
    UnknownDocumentGeneratorError,
)
from project_assistant.models import Project


def _generator(
    content: str,
):
    def generate(project: Project) -> str:
        return f"{project.name}: {content}"

    return generate


def _project(tmp_path: Path) -> Project:
    return Project(
        name="demo",
        root=tmp_path,
    )


def test_registry_resolves_exact_profile(
    tmp_path: Path,
) -> None:
    registry = DocumentGeneratorRegistry()

    registration = RegisteredDocumentGenerator(
        profile_name="python-cli",
        document_path="README.md",
        generator_name="readme-python-cli",
        generate=_generator("python"),
    )

    registry.register(registration)

    resolved = registry.resolve(
        profile_name="python-cli",
        document_path="README.md",
    )

    assert resolved is registration
    assert resolved.generate(_project(tmp_path)) == (
        "demo: python"
    )


def test_registry_falls_back_to_generic(
    tmp_path: Path,
) -> None:
    registry = DocumentGeneratorRegistry()

    generic = RegisteredDocumentGenerator(
        profile_name="generic",
        document_path="README.md",
        generator_name="readme-generic",
        generate=_generator("generic"),
    )

    registry.register(generic)

    resolved = registry.resolve(
        profile_name="unknown-profile",
        document_path="README.md",
    )

    assert resolved is generic
    assert resolved.generate(_project(tmp_path)) == (
        "demo: generic"
    )


def test_exact_profile_overrides_generic() -> None:
    registry = DocumentGeneratorRegistry()

    generic = RegisteredDocumentGenerator(
        profile_name="generic",
        document_path="README.md",
        generator_name="readme-generic",
        generate=_generator("generic"),
    )
    specialized = RegisteredDocumentGenerator(
        profile_name="python-cli",
        document_path="README.md",
        generator_name="readme-python-cli",
        generate=_generator("python"),
    )

    registry.register(generic)
    registry.register(specialized)

    resolved = registry.resolve(
        profile_name="python-cli",
        document_path="README.md",
    )

    assert resolved is specialized


def test_registry_rejects_duplicate_registration() -> None:
    registry = DocumentGeneratorRegistry()

    registration = RegisteredDocumentGenerator(
        profile_name="python-cli",
        document_path="README.md",
        generator_name="readme-python-cli",
        generate=_generator("python"),
    )

    registry.register(registration)

    with pytest.raises(
        DuplicateDocumentGeneratorError
    ):
        registry.register(registration)


def test_registry_rejects_unknown_document() -> None:
    registry = DocumentGeneratorRegistry()

    with pytest.raises(
        UnknownDocumentGeneratorError
    ):
        registry.resolve(
            profile_name="python-cli",
            document_path="docs/unknown.md",
        )


def test_supported_documents_combines_exact_and_generic() -> None:
    registry = DocumentGeneratorRegistry()

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="generic",
            document_path="README.md",
            generator_name="readme-generic",
            generate=_generator("generic"),
        )
    )
    registry.register(
        RegisteredDocumentGenerator(
            profile_name="python-cli",
            document_path="docs/cli.md",
            generator_name="cli-python",
            generate=_generator("cli"),
        )
    )
    registry.register(
        RegisteredDocumentGenerator(
            profile_name="django-react",
            document_path="docs/api.md",
            generator_name="api-django",
            generate=_generator("api"),
        )
    )

    assert registry.supported_documents(
        "python-cli"
    ) == frozenset(
        {
            "README.md",
            "docs/cli.md",
        }
    )


def test_registrations_have_stable_order() -> None:
    registry = DocumentGeneratorRegistry()

    registry.register(
        RegisteredDocumentGenerator(
            profile_name="python-cli",
            document_path="README.md",
            generator_name="readme",
            generate=_generator("readme"),
        )
    )
    registry.register(
        RegisteredDocumentGenerator(
            profile_name="generic",
            document_path="AGENTS.md",
            generator_name="agents",
            generate=_generator("agents"),
        )
    )

    registrations = registry.registrations()

    assert [
        (
            item.profile_name,
            item.document_path,
        )
        for item in registrations
    ] == [
        ("generic", "AGENTS.md"),
        ("python-cli", "README.md"),
    ]
