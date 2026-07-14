import json
from pathlib import Path

from project_assistant.commands.template import (
    analyze_template,
)


def test_analyze_template_writes_json_cache(
    tmp_path: Path,
) -> None:
    (tmp_path / "README.md").write_text(
        "# Template\n",
        encoding="utf-8",
    )

    facts, cache_path = analyze_template(
        tmp_path,
        write_cache=True,
    )

    assert facts.name == tmp_path.name
    assert cache_path is not None
    assert cache_path.exists()

    data = json.loads(
        cache_path.read_text(encoding="utf-8")
    )

    assert data["name"] == tmp_path.name
    assert data["root"] == str(tmp_path.resolve())
