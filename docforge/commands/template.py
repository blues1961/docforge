from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from docforge.analyzers import (
    TemplateAnalyzer,
    TemplateFacts,
)


CACHE_DIRECTORY = Path(".docforge/cache")
TEMPLATE_CACHE_FILENAME = "template.json"


def analyze_template(
    path: Path,
    *,
    write_cache: bool = True,
) -> tuple[TemplateFacts, Path | None]:
    facts = TemplateAnalyzer().analyze(path)

    if not write_cache:
        return facts, None

    root = Path(facts.root)
    output = (
        root
        / CACHE_DIRECTORY
        / TEMPLATE_CACHE_FILENAME
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        json.dumps(
            asdict(facts),
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return facts, output
