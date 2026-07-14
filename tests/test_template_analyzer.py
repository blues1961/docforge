from pathlib import Path

from project_assistant.analyzers import TemplateAnalyzer


def test_template_analyzer_extracts_canonical_structure(
    tmp_path: Path,
) -> None:
    (tmp_path / "README.md").write_text(
        "# Template\n",
        encoding="utf-8",
    )
    (tmp_path / "README_DEV.md").write_text(
        "# Développement\nSecrets dans .env.local\n",
        encoding="utf-8",
    )
    (tmp_path / "INVARIANTS.md").write_text(
        """
# Invariants

## Environnements
## Docker Compose
## Sécurité
""",
        encoding="utf-8",
    )

    (tmp_path / ".env.dev").write_text(
        "APP_ENV=dev\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.prod").write_text(
        "APP_ENV=prod\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.local").write_text(
        "SECRET=value\n",
        encoding="utf-8",
    )
    (tmp_path / ".env").symlink_to(".env.dev")

    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "env-switch.sh").write_text(
        "#!/bin/sh\n",
        encoding="utf-8",
    )

    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "tests.yml").write_text(
        "name: tests\n",
        encoding="utf-8",
    )

    (tmp_path / "Makefile").write_text(
        """
dev:
\t./scripts/env-switch.sh dev

prod:
\t./scripts/env-switch.sh prod

up:
\tdocker compose up -d
""",
        encoding="utf-8",
    )

    (tmp_path / "docker-compose.dev.yml").write_text(
        """
services:
  db:
    image: postgres:16-alpine
""",
        encoding="utf-8",
    )

    (tmp_path / "docker-compose.prod.yml").write_text(
        """
services:
  db:
    image: postgres:16-alpine
""",
        encoding="utf-8",
    )

    facts = TemplateAnalyzer().analyze(tmp_path)

    assert facts.name == tmp_path.name
    assert facts.env_symlink_exists is True
    assert facts.env_symlink_target == ".env.dev"
    assert facts.secrets_policy_detected is True

    assert "dev" in facts.make_targets
    assert "prod" in facts.make_targets
    assert "up" in facts.make_targets

    assert "scripts/env-switch.sh" in facts.scripts
    assert (
        ".github/workflows/tests.yml"
        in facts.github_workflows
    )

    titles = {
        section.title
        for section in facts.invariant_sections
    }

    assert "Environnements" in titles
    assert "Docker Compose" in titles

    readme = next(
        rule
        for rule in facts.documents
        if rule.path == "README.md"
    )

    assert readme.exists is True
