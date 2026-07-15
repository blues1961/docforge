from pathlib import Path

from docforge.config import DocumentationConfigLoader
from docforge.scanners import FileSystemScanner
from docforge.validators import DocumentationValidator


def test_validator_reports_missing_required_documents(
    tmp_path: Path,
) -> None:
    (tmp_path / ".env.dev").write_text(
        "APP_ENV=dev\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.prod").write_text(
        "APP_ENV=prod\n",
        encoding="utf-8",
    )
    (tmp_path / ".env").symlink_to(".env.dev")

    project = FileSystemScanner().scan(tmp_path)
    config = DocumentationConfigLoader().resolve_profile("base")

    DocumentationValidator().validate(project, config)

    codes = {
        finding.code
        for finding in project.findings
    }

    assert "DOC001" in codes


def test_validator_accepts_existing_readme(
    tmp_path: Path,
) -> None:
    (tmp_path / ".env.dev").write_text(
        "APP_ENV=dev\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.prod").write_text(
        "APP_ENV=prod\n",
        encoding="utf-8",
    )
    (tmp_path / ".env").symlink_to(".env.dev")

    (tmp_path / "README.md").write_text(
        """
# Démonstration

## Résumé du projet

## Fonctionnalités principales

## Architecture générale

## Technologies utilisées

## Installation

## Utilisation

## Configuration

## Documentation complémentaire
""",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    config = DocumentationConfigLoader().resolve_profile("base")

    DocumentationValidator().validate(project, config)

    readme = next(
        document
        for document in project.documents
        if document.path == "README.md"
    )

    assert readme.exists is True
    assert readme.sections_missing == []


def test_validator_accepts_documentation_aliases(
    tmp_path: Path,
) -> None:
    (tmp_path / ".env.dev").write_text(
        "APP_ENV=dev\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.prod").write_text(
        "APP_ENV=prod\n",
        encoding="utf-8",
    )
    (tmp_path / ".env").symlink_to(".env.dev")

    (tmp_path / "README.md").write_text(
        """
# Démonstration

## Démarrage rapide
## Fonctionnement métier
## Stack cible
## Conformité aux invariants
""",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    config = DocumentationConfigLoader().resolve_profile("base")

    DocumentationValidator().validate(project, config)

    readme = next(
        document
        for document in project.documents
        if document.path == "README.md"
    )

    assert readme.sections_missing == []
