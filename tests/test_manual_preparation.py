import json
from pathlib import Path

from typer.testing import CliRunner

from docforge.cli import app
from docforge.detectors import TechnologyDetector
from docforge.knowledge import ProjectKnowledgeBuilder
from docforge.manual_blueprint import ManualBlueprintRegistry, ManualSectionDefinition
from docforge.manual_knowledge import ManualKnowledgeBuilder
from docforge.manual_prompt import ManualPromptBuilder, ManualPromptBudgetExceeded
from docforge.manual_service import ManualPreparationService
from docforge.profiles import ProfileDetector
from docforge.scanners import FileSystemScanner


runner = CliRunner()


def _create_python_cli_project(root: Path) -> None:
    package = root / "docforge"
    package.mkdir()

    (package / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )
    (package / "cli.py").write_text(
        """
from pathlib import Path
import typer

app = typer.Typer()
projects_app = typer.Typer()
app.add_typer(projects_app, name="projects")


@app.command()
def analyze(
    path: Path = typer.Argument(
        Path("."),
        help="Analyser un projet.",
    ),
) -> None:
    pass


@app.command()
def profile() -> None:
    pass


@app.command()
def knowledge() -> None:
    pass


@app.command()
def document(
    clean: bool = typer.Option(
        False,
        "--clean",
    ),
    refresh: bool = typer.Option(
        False,
        "--refresh",
    ),
) -> None:
    pass


@app.command()
def generate(
    clean: bool = typer.Option(
        False,
        "--clean",
    ),
    refresh: bool = typer.Option(
        False,
        "--refresh",
    ),
) -> None:
    pass


@app.command()
def apply() -> None:
    pass


@app.command("audit-all")
def audit_all(
    show_findings: bool = typer.Option(
        False,
        "--show-findings",
    ),
) -> None:
    pass


@app.command("audit-report")
def audit_report() -> None:
    pass


@projects_app.command("add")
def projects_add() -> None:
    pass


@projects_app.command("list")
def projects_list() -> None:
    pass


@projects_app.command("remove")
def projects_remove() -> None:
    pass
""",
        encoding="utf-8",
    )

    (root / "tests").mkdir()
    (root / ".gitignore").write_text(
        ".docforge/\n.venv/\n.pytest_cache/\n__pycache__/\n",
        encoding="utf-8",
    )
    (root / "README_DEV.md").write_text(
        "# Dev\n",
        encoding="utf-8",
    )
    (root / "pyproject.toml").write_text(
        """
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "docforge"
version = "0.1.0"
description = "Assistant local d'analyse et de documentation de projets logiciels."
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31",
    "rich>=13.7",
    "typer>=0.12",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
]

[project.scripts]
docforge = "docforge.cli:app"
""",
        encoding="utf-8",
    )


def _build_manual_knowledge(root: Path):
    project = FileSystemScanner().scan(root)
    TechnologyDetector().detect(project)
    profile = ProfileDetector().resolve(project)
    knowledge = ProjectKnowledgeBuilder().build(
        project,
        profile_instance=profile,
    )
    return (
        ManualKnowledgeBuilder().build(
            project_root=root,
            knowledge=knowledge,
            profile_instance=profile,
        ),
        profile,
    )


def test_manual_knowledge_is_json_serializable(
    tmp_path: Path,
) -> None:
    _create_python_cli_project(tmp_path)

    knowledge, _profile = _build_manual_knowledge(
        tmp_path
    )
    data = json.loads(knowledge.to_json())

    assert data["schema_version"] == 2
    assert data["project"]["name"] == "docforge"
    assert data["project"]["cli_entry_point"] == (
        "docforge -> docforge.cli:app"
    )
    assert "commands" in data
    assert "workflows" in data
    assert "source_traceability" in data


def test_manual_knowledge_filters_forbidden_references_and_paths(
    tmp_path: Path,
) -> None:
    _create_python_cli_project(tmp_path)

    knowledge, _profile = _build_manual_knowledge(
        tmp_path
    )
    payload = knowledge.to_json()

    assert "/home/" not in payload
    assert "project-assistant" not in payload
    assert ".project-assistant" not in payload


def test_manual_knowledge_uses_grouped_commands(
    tmp_path: Path,
) -> None:
    _create_python_cli_project(tmp_path)

    knowledge, _profile = _build_manual_knowledge(
        tmp_path
    )
    command_paths = {
        command.command_path
        for command in knowledge.commands
    }

    assert "projects add" in command_paths
    assert "projects list" in command_paths
    assert "projects remove" in command_paths
    assert "add" not in command_paths
    assert "list" not in command_paths
    assert "remove" not in command_paths


def test_manual_knowledge_avoids_docker_and_filtered_findings_for_python_cli(
    tmp_path: Path,
) -> None:
    _create_python_cli_project(tmp_path)
    (tmp_path / ".env.local").write_text(
        "SECRET=1\n",
        encoding="utf-8",
    )

    knowledge, _profile = _build_manual_knowledge(
        tmp_path
    )
    payload_text = json.dumps(
        knowledge.to_dict(),
        ensure_ascii=False,
    )

    assert "Docker" not in payload_text
    assert "Compose" not in payload_text
    assert "ENV002" not in payload_text
    assert "ENV003" not in payload_text
    assert "ENV004" not in payload_text


def test_manual_knowledge_contains_local_installation_and_workflows(
    tmp_path: Path,
) -> None:
    _create_python_cli_project(tmp_path)

    knowledge, _profile = _build_manual_knowledge(
        tmp_path
    )
    commands = [
        step.command
        for step in knowledge.installation.steps
    ]
    workflows = {
        workflow.identifier: workflow
        for workflow in knowledge.workflows
    }

    assert "python -m venv .venv" in commands
    assert "source .venv/bin/activate" in commands
    assert "python -m pip install -e ." in commands
    assert 'python -m pip install -e ".[dev]"' in commands
    assert "docforge --help" in commands
    assert "pytest -q" in commands
    assert (
        "docforge document . --refresh --clean"
        in workflows["generate-preview"].commands
    )
    assert (
        "docforge apply . INVARIANTS.md --owner-approved"
        in workflows["apply-protected-document"].commands
    )


def test_blueprints_cover_python_cli_and_generic() -> None:
    registry = ManualBlueprintRegistry()
    python_cli = registry.blueprint_for_profile(
        "python-cli"
    )
    generic = registry.blueprint_for_profile("generic")

    assert python_cli.profile_name == "python-cli"
    assert len(python_cli.sections) == 21
    assert python_cli.sections[0].title == "Présentation"
    assert (
        python_cli.sections[-1].title
        == "Référence CLI"
    )

    assert generic.profile_name == "generic"
    assert generic.sections[0].title == "Présentation"
    assert generic.sections[-1].title == "Référence CLI"


def test_prompt_builder_generates_full_and_section_prompts(
    tmp_path: Path,
) -> None:
    _create_python_cli_project(tmp_path)

    knowledge, _profile = _build_manual_knowledge(
        tmp_path
    )
    blueprint = (
        ManualBlueprintRegistry().blueprint_for_profile(
            "python-cli"
        )
    )
    builder = ManualPromptBuilder()

    full_prompt = builder.build_full_prompt(
        knowledge=knowledge,
        blueprint=blueprint,
    )
    section_projection = builder.project_section_facts(
        knowledge,
        blueprint.sections[0],
    )
    section_prompt = builder.build_section_prompt(
        section=blueprint.sections[0],
        projected_facts=section_projection,
    )

    assert "BEGIN INSTRUCTIONS" in full_prompt
    assert "END INSTRUCTIONS" in full_prompt
    assert "BEGIN COMPACT MANUAL CONTEXT" in full_prompt
    assert "END COMPACT MANUAL CONTEXT" in full_prompt
    assert "source unique de vérité" in full_prompt
    assert "aucune connaissance externe" in full_prompt
    assert "`detected` = fait directement démontré" in full_prompt
    assert "`unresolved` = fait incomplet" in full_prompt
    assert "Version du schéma ManualKnowledge : 2." in full_prompt
    assert "`oaicite`" in full_prompt
    assert "Titre de section : Présentation" in section_prompt
    assert "BEGIN SECTION FACTS" in section_prompt
    assert (
        '"project"' in json.dumps(
            section_projection,
            ensure_ascii=False,
        )
    )


def test_manual_service_manifest_and_modes_and_clean(
    tmp_path: Path,
) -> None:
    _create_python_cli_project(tmp_path)
    service = ManualPreparationService()

    both = service.prepare(
        tmp_path,
        clean=True,
        mode="both",
    )
    both_manifest = json.loads(
        both.manifest_file.read_text(encoding="utf-8")
    )

    assert both.knowledge_file.is_file()
    assert both.full_prompt_file is not None
    assert both.full_prompt_file.is_file()
    assert both.section_prompt_files
    assert both.section_context_files
    assert both.generated_directory is not None
    assert both.generated_directory.is_dir()
    assert both_manifest["knowledge_file"] == (
        "manual-knowledge.json"
    )
    assert both_manifest["full_prompt"] == "manual-prompt.md"
    assert "section-prompts/01-presentation.md" in both_manifest["section_prompts"]
    assert both_manifest["section_contexts"][0]["context_file"] == "section-contexts/01-presentation.json"

    full = service.prepare(
        tmp_path,
        clean=True,
        mode="full",
    )
    full_manifest = json.loads(
        full.manifest_file.read_text(encoding="utf-8")
    )
    assert full.full_prompt_file is not None
    assert full.section_prompt_files == []
    assert full_manifest["section_prompts"] == []
    assert full_manifest["section_contexts"] == []

    sections = service.prepare(
        tmp_path,
        clean=True,
        mode="sections",
    )
    sections_manifest = json.loads(
        sections.manifest_file.read_text(
            encoding="utf-8"
        )
    )
    assert sections.full_prompt_file is None
    assert sections.section_prompt_files
    assert sections.section_context_files
    assert sections_manifest["full_prompt"] is None


def test_manual_service_does_not_modify_real_project_files(
    tmp_path: Path,
) -> None:
    _create_python_cli_project(tmp_path)
    before = {
        path.relative_to(tmp_path).as_posix(): path.read_text(
            encoding="utf-8"
        )
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    ManualPreparationService().prepare(
        tmp_path,
        clean=True,
        mode="both",
    )

    after = {
        path.relative_to(tmp_path).as_posix(): path.read_text(
            encoding="utf-8"
        )
        for path in tmp_path.rglob("*")
        if path.is_file()
        and ".docforge/manual" not in path.as_posix()
    }

    assert before == after


def test_manual_prepare_cli_command(
    tmp_path: Path,
) -> None:
    _create_python_cli_project(tmp_path)

    result = runner.invoke(
        app,
        [
            "manual",
            "prepare",
            str(tmp_path),
            "--clean",
            "--mode",
            "both",
        ],
    )

    assert result.exit_code == 0
    assert "manual-knowledge.json" in result.stdout
    assert "manual-manifest.json" in result.stdout
    assert (
        tmp_path
        / ".docforge"
        / "manual"
        / "manual-knowledge.json"
    ).is_file()


def test_manual_service_does_not_call_network_or_ollama(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _create_python_cli_project(tmp_path)

    def fail_network(*args, **kwargs):
        raise AssertionError("network call")

    def fail_ollama(*args, **kwargs):
        raise AssertionError("ollama call")

    monkeypatch.setattr(
        "requests.post",
        fail_network,
    )
    monkeypatch.setattr(
        "docforge.llm.ollama.OllamaClient.chat",
        fail_ollama,
    )

    ManualPreparationService().prepare(
        tmp_path,
        clean=True,
        mode="both",
    )


def test_manual_service_clean_removes_stale_files(
    tmp_path: Path,
) -> None:
    _create_python_cli_project(tmp_path)
    service = ManualPreparationService()

    result = service.prepare(
        tmp_path,
        clean=True,
        mode="both",
    )
    stale = result.output_dir / "stale.txt"
    stale.write_text("obsolete", encoding="utf-8")

    service.prepare(
        tmp_path,
        clean=True,
        mode="both",
    )

    assert stale.exists() is False


def test_manual_prepare_context_budget_is_enforced(tmp_path: Path) -> None:
    _create_python_cli_project(tmp_path)

    service = ManualPreparationService()

    try:
        service.prepare(tmp_path, clean=True, mode="sections", context_budget=10)
    except ManualPromptBudgetExceeded as exc:
        assert exc.section_identifier == "presentation"
    else:
        raise AssertionError("ManualPromptBudgetExceeded attendu")


def test_section_contexts_are_compact_relative_to_full_prompt(tmp_path: Path) -> None:
    _create_python_cli_project(tmp_path)
    result = ManualPreparationService().prepare(tmp_path, clean=True, mode="both")
    manifest = json.loads(result.manifest_file.read_text(encoding="utf-8"))

    full_prompt_tokens = manifest["full_prompt_estimated_tokens"]
    section_tokens = [item["estimated_tokens"] for item in manifest["section_contexts"]]

    assert full_prompt_tokens is not None
    assert section_tokens
    assert max(section_tokens) < full_prompt_tokens


def test_manual_prepare_context_budget_accepts_exact_limit(tmp_path: Path) -> None:
    _create_python_cli_project(tmp_path)
    knowledge, _profile = _build_manual_knowledge(tmp_path)
    blueprint = ManualBlueprintRegistry().blueprint_for_profile("python-cli")
    builder = ManualPromptBuilder()
    section = blueprint.sections[0]
    context = builder.build_section_context(knowledge, section)

    exact = builder.build_section_context(knowledge, section, context_budget=context.estimated_tokens)

    assert exact.estimated_tokens == context.estimated_tokens


def test_manual_prepare_context_budget_fails_one_token_above_limit(tmp_path: Path) -> None:
    _create_python_cli_project(tmp_path)
    knowledge, _profile = _build_manual_knowledge(tmp_path)
    blueprint = ManualBlueprintRegistry().blueprint_for_profile("python-cli")
    builder = ManualPromptBuilder()
    section = blueprint.sections[0]
    context = builder.build_section_context(knowledge, section)

    try:
        builder.build_section_context(knowledge, section, context_budget=max(1, context.estimated_tokens - 1))
    except ManualPromptBudgetExceeded as exc:
        assert exc.estimated_tokens == context.estimated_tokens
        assert exc.context_budget == max(1, context.estimated_tokens - 1)
        assert exc.fact_breakdown
    else:
        raise AssertionError("ManualPromptBudgetExceeded attendu")


def test_manual_prepare_context_tracks_missing_and_repeated_fact_paths(tmp_path: Path) -> None:
    _create_python_cli_project(tmp_path)
    knowledge, _profile = _build_manual_knowledge(tmp_path)
    builder = ManualPromptBuilder()
    section = ManualSectionDefinition(
        identifier="custom",
        title="Custom",
        purpose="Tester les chemins absents et répétés.",
        required_fact_paths=("project", "project", "missing.branch"),
    )

    context = builder.build_section_context(knowledge, section)

    assert context.repeated_fact_paths == ["project"]
    assert context.missing_fact_paths == ["missing.branch"]
    assert "project" in context.projected_facts


def test_manual_prepare_contexts_are_deterministic(tmp_path: Path) -> None:
    _create_python_cli_project(tmp_path)
    service = ManualPreparationService()

    first = service.prepare(tmp_path, clean=True, mode="sections")
    first_payloads = [path.read_text(encoding="utf-8") for path in first.section_context_files]
    second = service.prepare(tmp_path, clean=True, mode="sections")
    second_payloads = [path.read_text(encoding="utf-8") for path in second.section_context_files]

    assert first_payloads == second_payloads


def test_manual_prepare_shared_fact_paths_stay_consistent(tmp_path: Path) -> None:
    _create_python_cli_project(tmp_path)
    knowledge, _profile = _build_manual_knowledge(tmp_path)
    builder = ManualPromptBuilder()
    first = ManualSectionDefinition("first", "First", "A", ("project",))
    second = ManualSectionDefinition("second", "Second", "B", ("project",))

    assert builder.build_section_context(knowledge, first).projected_facts["project"] == builder.build_section_context(knowledge, second).projected_facts["project"]


def test_manual_validate_cli_reports_errors_and_json(tmp_path: Path) -> None:
    _create_python_cli_project(tmp_path)
    ManualPreparationService().prepare(tmp_path, clean=True, mode="both")
    blueprint = ManualBlueprintRegistry().blueprint_for_profile("python-cli")
    good_manual = tmp_path / "guide.md"
    sections = "\n\n".join(f"## {section.title}\nTexte." for section in blueprint.sections)
    good_manual.write_text(f"# Guide utilisateur de docforge\n\n{sections}\n", encoding="utf-8")

    ok = runner.invoke(app, ["manual", "validate", str(good_manual), "--project-root", str(tmp_path), "--json"])
    assert ok.exit_code == 0
    assert '"valid": true' in ok.stdout

    bad_manual = tmp_path / "guide-bad.md"
    bad_manual.write_text("Conversation id: 1\n## Présentation\nUtiliser `make unknown`\n", encoding="utf-8")
    bad = runner.invoke(app, ["manual", "validate", str(bad_manual), "--project-root", str(tmp_path)])
    assert bad.exit_code == 1
    assert "MANUAL002" in bad.stdout
    assert "MANUAL006" in bad.stdout
