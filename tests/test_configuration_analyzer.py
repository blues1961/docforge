from pathlib import Path

from docforge.analyzers import (
    ConfigurationAnalyzer,
)
from docforge.scanners import FileSystemScanner


def test_configuration_analyzer_detects_project_paths(
    tmp_path: Path,
) -> None:
    (tmp_path / ".project-assistant" / "cache").mkdir(
        parents=True
    )
    (tmp_path / ".project-assistant" / "preview").mkdir()
    (tmp_path / "reports").mkdir()

    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname='demo'\nversion='0.1.0'\n",
        encoding="utf-8",
    )

    (tmp_path / ".gitignore").write_text(
        """
.project-assistant/
.venv/
__pycache__/
*.pyc
.pytest_cache/
""",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    facts = ConfigurationAnalyzer().analyze(project)

    by_path = {
        item.path: item
        for item in facts.files
    }

    assert by_path[
        ".project-assistant/cache/"
    ].exists is True

    assert by_path[
        ".project-assistant/preview/"
    ].exists is True

    assert by_path["reports/"].exists is True
    assert by_path["pyproject.toml"].exists is True

    assert ".project-assistant/" in facts.ignored_paths
    assert ".venv/" in facts.ignored_paths


def test_configuration_analyzer_handles_missing_files(
    tmp_path: Path,
) -> None:
    project = FileSystemScanner().scan(tmp_path)
    facts = ConfigurationAnalyzer().analyze(project)

    assert facts.project_state_root == ".project-assistant"
    assert facts.existing_file_count >= 0
    assert facts.ignored_paths == []
