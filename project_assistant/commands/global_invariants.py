from __future__ import annotations

from pathlib import Path

from project_assistant.analyzers import TemplateAnalyzer
from project_assistant.generators import (
    GlobalInvariantsGenerator,
)


def generate_global_invariants(
    template_path: Path,
    output_path: Path,
) -> Path:
    facts = TemplateAnalyzer().analyze(template_path)

    content = GlobalInvariantsGenerator().generate(facts)

    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output_path.write_text(
        content,
        encoding="utf-8",
    )

    return output_path
