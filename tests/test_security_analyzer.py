from pathlib import Path

from docforge.analyzers import SecurityAnalyzer
from docforge.scanners import FileSystemScanner


def test_security_analyzer_detects_controls_and_ignored_paths(
    tmp_path: Path,
) -> None:
    (tmp_path / ".gitignore").write_text(
        """
.env.local
.env.*.local
.docforge/
.venv/
__pycache__/
.pytest_cache/
""",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)

    facts = SecurityAnalyzer().analyze(
        project,
        protected_documents=("INVARIANTS.md",),
    )

    assert "INVARIANTS.md" in facts.protected_documents
    assert ".env.local" in facts.ignored_sensitive_paths
    assert ".docforge/" in (
        facts.ignored_sensitive_paths
    )
    assert any(
        control.identifier == "SEC-004"
        for control in facts.controls
    )
    assert facts.risks
    assert "pytest -q" in facts.validation_commands


def test_security_analyzer_handles_missing_gitignore(
    tmp_path: Path,
) -> None:
    project = FileSystemScanner().scan(tmp_path)
    facts = SecurityAnalyzer().analyze(project)

    assert facts.ignored_sensitive_paths == []
    assert facts.controls
