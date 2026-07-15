from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from docforge.commands.document import (
    generate_documentation_preview,
)
from docforge.generators import (
    LLMDocumentationGenerator,
)


@dataclass(slots=True)
class GeneratedDocumentResult:
    document_path: str
    preview_path: Path
    tokens_per_second: float
    generator: str


def generate_preview_with_llm(
    path: Path,
    *,
    model: str,
    clean: bool = False,
    refresh: bool = False,
) -> list[GeneratedDocumentResult]:
    project, _, generated = generate_documentation_preview(
        path=path,
        clean=clean,
        refresh=refresh,
    )

    generator = LLMDocumentationGenerator()
    results: list[GeneratedDocumentResult] = []

    for item in generated:
        if "déterministe" in item.generator:
            results.append(
                GeneratedDocumentResult(
                    document_path=item.document_path,
                    preview_path=item.preview_path,
                    tokens_per_second=0.0,
                    generator=item.generator,
                )
            )
            continue

        document = generator.generate_document(
            project=project,
            document_path=item.document_path,
            skeleton_path=item.preview_path,
            model=model,
        )

        item.preview_path.write_text(
            document.content,
            encoding="utf-8",
        )

        results.append(
            GeneratedDocumentResult(
                document_path=item.document_path,
                preview_path=item.preview_path,
                tokens_per_second=(
                    document.average_tokens_per_second
                ),
                generator="ollama",
            )
        )

    return results
