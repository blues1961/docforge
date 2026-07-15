from pathlib import Path

import pytest

from docforge.config import (
    ConfigurationError,
    DocumentationConfigLoader,
)


def test_loader_resolves_base_profile() -> None:
    config = DocumentationConfigLoader().resolve_profile("base")

    assert config.profile == "base"
    assert "README.md" in config.required_documents
    assert "docs/specification.md" in config.required_documents
    assert "docs/api.md" not in config.required_documents


def test_loader_resolves_django_react_inheritance() -> None:
    config = DocumentationConfigLoader().resolve_profile(
        "django-react"
    )

    assert "README.md" in config.required_documents
    assert "docs/api.md" in config.required_documents
    assert "docs/deployment.md" in config.required_documents


def test_loader_rejects_unknown_profile() -> None:
    with pytest.raises(ConfigurationError):
        DocumentationConfigLoader().resolve_profile(
            "profil-inexistant"
        )


def test_loader_applies_project_document_exceptions() -> None:
    config = DocumentationConfigLoader().resolve_project_profile(
        profile_name="django-react",
        remove_documents=["docs/deployment.md"],
        add_documents=["docs/troubleshooting.md"],
    )

    assert "docs/deployment.md" not in config.required_documents
    assert "docs/troubleshooting.md" in config.required_documents
