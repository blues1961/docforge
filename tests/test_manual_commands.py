import json
from pathlib import Path

import pytest

from docforge.manual_commands import publish_manual


def _build(root: Path, project: Path) -> None:
    (root / "documents" / "user-guide").mkdir(parents=True)
    guide = root / "documents" / "user-guide" / "guide-genere.md"
    guide.write_text("# Guide utilisateur de Demo\n\n## Présentation\n\nTexte.\n", encoding="utf-8")
    (root / "build-manifest.json").write_text(json.dumps({
        "project": str(project), "generation_state": "completed", "final_state": "completed",
        "documents": {"user-guide": {"title": "Guide utilisateur", "guide": "documents/user-guide/guide-genere.md"}},
    }), encoding="utf-8")


def test_publish_preview_does_not_write(tmp_path: Path):
    project = tmp_path / "project"; project.mkdir()
    build = project / ".docforge" / "manuals" / "build"; _build(build, project)
    pairs = publish_manual(project)
    assert pairs[0][1] == project / "docs" / "guide-utilisateur.md"
    assert not pairs[0][1].exists()


def test_publish_requires_write_and_replace(tmp_path: Path):
    project = tmp_path / "project"; project.mkdir()
    build = project / ".docforge" / "manuals" / "build"; _build(build, project)
    publish_manual(project, write=True)
    with pytest.raises(ValueError, match="existe déjà"):
        publish_manual(project, write=True)
    publish_manual(project, write=True, replace=True)
    assert (project / "docs/guide-utilisateur.md").is_file()


def test_publish_rejects_invalid_build(tmp_path: Path):
    project = tmp_path / "project"; project.mkdir()
    build = project / ".docforge" / "manuals" / "build"; _build(build, project)
    data = json.loads((build / "build-manifest.json").read_text())
    data["final_state"] = "validation_failed"
    (build / "build-manifest.json").write_text(json.dumps(data))
    with pytest.raises(ValueError, match="pas terminé"):
        publish_manual(project)


def test_publish_from_run_manifest(tmp_path: Path):
    project = tmp_path / "project"; project.mkdir()
    run = tmp_path / "run"; (run / "documents/user-guide").mkdir(parents=True)
    (run / "documents/user-guide/guide-genere.md").write_text("# Guide utilisateur de Demo\n", encoding="utf-8")
    (run / "run-manifest.json").write_text(json.dumps({"project": str(project), "generation_state": "completed", "final_state": "completed", "documents": {"user-guide": {}}}), encoding="utf-8")
    publish_manual(project, from_run=run, write=True)
    assert (project / "docs/guide-utilisateur.md").is_file()


def test_manual_config_project_overrides_user(tmp_path: Path, monkeypatch):
    from docforge import manual_commands
    project = tmp_path / "project"; project.mkdir()
    (project / ".docforge.yml").write_text("manual:\n  model: project-model\n  num_ctx: 9000\n", encoding="utf-8")
    monkeypatch.setattr(manual_commands.Path, "home", staticmethod(lambda: tmp_path / "home"))
    (tmp_path / "home/.config/docforge").mkdir(parents=True)
    (tmp_path / "home/.config/docforge/config.yml").write_text("manual:\n  model: user-model\n  max_output_tokens: 1000\n", encoding="utf-8")
    values = manual_commands._manual_config(project)
    assert values["model"] == "project-model"
    assert values["num_ctx"] == 9000
    assert values["max_output_tokens"] == 1000
