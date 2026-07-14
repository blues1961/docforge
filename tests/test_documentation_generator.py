from pathlib import Path

from project_assistant.config import DocumentationConfigLoader
from project_assistant.generators import DocumentationPreviewGenerator
from project_assistant.scanners import FileSystemScanner


def _create_environment_files(root: Path) -> None:
    (root / ".env.dev").write_text(
        "APP_ENV=dev\n",
        encoding="utf-8",
    )
    (root / ".env.prod").write_text(
        "APP_ENV=prod\n",
        encoding="utf-8",
    )
    (root / ".env").symlink_to(".env.dev")


def test_generator_creates_missing_documents_in_preview(
    tmp_path: Path,
) -> None:
    _create_environment_files(tmp_path)

    project = FileSystemScanner().scan(tmp_path)
    config = DocumentationConfigLoader().resolve_profile("base")

    generated = DocumentationPreviewGenerator().generate(
        project,
        config,
    )

    generated_paths = {
        item.source_path
        for item in generated
    }

    assert "README.md" in generated_paths
    assert "docs/architecture.md" in generated_paths

    preview_readme = (
        tmp_path
        / ".project-assistant"
        / "preview"
        / "README.md"
    )

    assert preview_readme.exists()
    assert "# " in preview_readme.read_text(
        encoding="utf-8"
    )


def test_generator_does_not_replace_existing_document(
    tmp_path: Path,
) -> None:
    _create_environment_files(tmp_path)

    original_content = "# README original\n"

    (tmp_path / "README.md").write_text(
        original_content,
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    config = DocumentationConfigLoader().resolve_profile("base")

    generated = DocumentationPreviewGenerator().generate(
        project,
        config,
    )

    generated_paths = {
        item.source_path
        for item in generated
    }

    assert "README.md" not in generated_paths
    assert (
        tmp_path / "README.md"
    ).read_text(encoding="utf-8") == original_content


def test_generator_can_clean_previous_preview(
    tmp_path: Path,
) -> None:
    _create_environment_files(tmp_path)

    old_file = (
        tmp_path
        / ".project-assistant"
        / "preview"
        / "obsolete.md"
    )
    old_file.parent.mkdir(parents=True)
    old_file.write_text("ancien", encoding="utf-8")

    project = FileSystemScanner().scan(tmp_path)
    config = DocumentationConfigLoader().resolve_profile("base")

    DocumentationPreviewGenerator().generate(
        project,
        config,
        clean=True,
    )

    assert not old_file.exists()
