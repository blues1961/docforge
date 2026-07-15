from pathlib import Path

from docforge.analyzers import TemplateAnalyzer
from docforge.generators import (
    GlobalInvariantsGenerator,
)


def test_global_invariants_are_generated_from_template(
    tmp_path: Path,
) -> None:
    (tmp_path / "INVARIANTS.md").write_text(
        """
# INVARIANTS

## Secrets

Les secrets résident dans `.env.local`.

## Docker Compose

Les commandes utilisent le plugin Docker Compose.
""",
        encoding="utf-8",
    )

    (tmp_path / "README.md").write_text(
        "# Template\n",
        encoding="utf-8",
    )

    (tmp_path / ".env.template.example").write_text(
        "APP_ENV=dev\n",
        encoding="utf-8",
    )

    (tmp_path / "docker-compose.dev.yml").write_text(
        "services: {}\n",
        encoding="utf-8",
    )
    (tmp_path / "docker-compose.prod.yml").write_text(
        "services: {}\n",
        encoding="utf-8",
    )

    facts = TemplateAnalyzer().analyze(tmp_path)
    content = GlobalInvariantsGenerator().generate(facts)

    assert "# Invariants globaux" in content
    assert "## Environnements et secrets" in content
    assert "Les secrets résident dans `.env.local`." in content
    assert "Les commandes utilisent le plugin Docker Compose." in content
    assert ".env.template.example" in content
