from docforge.generators.llm_documentation import (
    LLMDocumentationGenerator,
)


def test_extracts_document_and_section_titles() -> None:
    skeleton = """
# Déploiement — démonstration

## Prérequis

Texte temporaire.

## Environnements

Texte temporaire.
"""

    assert (
        LLMDocumentationGenerator._extract_document_title(
            skeleton
        )
        == "Déploiement — démonstration"
    )

    assert (
        LLMDocumentationGenerator._extract_section_titles(
            skeleton
        )
        == ["Prérequis", "Environnements"]
    )


def test_clean_section_removes_repeated_heading() -> None:
    content = """
## Prérequis

- Docker
- Git
"""

    cleaned = (
        LLMDocumentationGenerator._clean_section_content(
            content,
            "Prérequis",
        )
    )

    assert cleaned == "- Docker\n- Git"
