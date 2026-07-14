from pathlib import Path

import pytest

from project_assistant.scanners import FileSystemScanner


def test_scanner_discovers_files_and_languages(
    tmp_path: Path,
) -> None:
    (tmp_path / "README.md").write_text(
        "# Projet\n",
        encoding="utf-8",
    )
    (tmp_path / "app.py").write_text(
        "print('bonjour')\n",
        encoding="utf-8",
    )

    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "main.tsx").write_text(
        "export default App;\n",
        encoding="utf-8",
    )

    scanner = FileSystemScanner()
    project = scanner.scan(tmp_path)

    assert project.name == tmp_path.name
    assert "README.md" in project.files
    assert "app.py" in project.files
    assert "frontend/main.tsx" in project.files

    assert "Python" in project.languages
    assert "TypeScript" in project.languages
    assert "Markdown" in project.languages

    assert project.statistics.file_count == 3
    assert project.statistics.directory_count == 1


def test_scanner_excludes_sensitive_and_generated_files(
    tmp_path: Path,
) -> None:
    (tmp_path / ".env.dev.local").write_text(
        "SECRET=abc\n",
        encoding="utf-8",
    )
    (tmp_path / "settings.local").write_text(
        "secret\n",
        encoding="utf-8",
    )

    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "package.js").write_text(
        "ignored\n",
        encoding="utf-8",
    )

    (tmp_path / "main.py").write_text(
        "print('ok')\n",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)

    assert project.files == ["main.py"]
    assert ".env.dev.local" in (
        project.environment.local_secret_files
    )


def test_scanner_rejects_missing_directory(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        FileSystemScanner().scan(missing)


def test_scanner_rejects_regular_file(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("contenu", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        FileSystemScanner().scan(file_path)


def test_scanner_detects_environment_symlink(
    tmp_path: Path,
) -> None:
    (tmp_path / ".env.dev").write_text(
        "APP_ENV=dev\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.prod").write_text(
        "APP_ENV=prod\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.dev.local").write_text(
        "SECRET=abc\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.dev.example").write_text(
        "SECRET=\n",
        encoding="utf-8",
    )

    (tmp_path / ".env").symlink_to(".env.dev")

    project = FileSystemScanner().scan(tmp_path)

    assert project.environment.env_symlink_exists is True
    assert project.environment.env_symlink_target == ".env.dev"
    assert project.environment.env_symlink_target_exists is True
    assert project.environment.active_environment == "dev"

    assert ".env.dev" in project.environment.versioned_files
    assert ".env.prod" in project.environment.versioned_files
    assert ".env.dev.local" in (
        project.environment.local_secret_files
    )
    assert ".env.dev.example" in (
        project.environment.example_files
    )

    assert project.symlinks[".env"] == ".env.dev"
    assert project.statistics.symlink_count == 1

    codes = {finding.code for finding in project.findings}

    assert "ENV002" not in codes
    assert "ENV003" not in codes
    assert "ENV004" not in codes
    assert "ENV005" not in codes
    assert "ENV006" not in codes


def test_scanner_reports_missing_environment_symlink(
    tmp_path: Path,
) -> None:
    (tmp_path / ".env.dev").write_text(
        "APP_ENV=dev\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.prod").write_text(
        "APP_ENV=prod\n",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)

    codes = {finding.code for finding in project.findings}

    assert "ENV004" in codes


def test_scanner_reports_broken_environment_symlink(
    tmp_path: Path,
) -> None:
    (tmp_path / ".env.dev").write_text(
        "APP_ENV=dev\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.prod").write_text(
        "APP_ENV=prod\n",
        encoding="utf-8",
    )
    (tmp_path / ".env").symlink_to(".env.missing")

    project = FileSystemScanner().scan(tmp_path)

    codes = {finding.code for finding in project.findings}

    assert "ENV005" in codes
    assert "ENV006" in codes
