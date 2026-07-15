from pathlib import Path

from docforge.storage_paths import migrate_legacy_path


def test_migrate_legacy_path_does_not_overwrite_existing_target(
    tmp_path: Path,
) -> None:
    legacy = tmp_path / "legacy"
    current = tmp_path / "current"

    legacy.mkdir()
    current.mkdir()

    (legacy / "data.txt").write_text(
        "legacy\n",
        encoding="utf-8",
    )
    (current / "data.txt").write_text(
        "current\n",
        encoding="utf-8",
    )

    migrated = migrate_legacy_path(
        legacy,
        current,
    )

    assert migrated is False
    assert (legacy / "data.txt").read_text(encoding="utf-8") == "legacy\n"
    assert (current / "data.txt").read_text(encoding="utf-8") == "current\n"
