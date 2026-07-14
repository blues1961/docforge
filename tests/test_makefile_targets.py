from pathlib import Path

from project_assistant.analyzers import DeploymentAnalyzer
from project_assistant.scanners import FileSystemScanner


def test_makefile_variables_are_not_detected_as_targets(
    tmp_path: Path,
) -> None:
    (tmp_path / "Makefile").write_text(
        """
SCRIPTS_DIR := scripts
APP_ENV ?= dev
COMPOSE = docker compose

up:
\t$(COMPOSE) up -d

check:
\t$(SCRIPTS_DIR)/check.sh
""",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    facts = DeploymentAnalyzer().analyze(project)

    assert "up" in facts.make_targets
    assert "check" in facts.make_targets

    assert "SCRIPTS_DIR" not in facts.make_targets
    assert "APP_ENV" not in facts.make_targets
    assert "COMPOSE" not in facts.make_targets
