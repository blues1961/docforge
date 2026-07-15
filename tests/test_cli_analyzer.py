from pathlib import Path

from docforge.analyzers import CliAnalyzer
from docforge.scanners import FileSystemScanner


def test_cli_analyzer_extracts_typer_commands(
    tmp_path: Path,
) -> None:
    package = tmp_path / "docforge"
    package.mkdir()

    (package / "cli.py").write_text(
        '''
from pathlib import Path
import typer

app = typer.Typer()
projects_app = typer.Typer()
app.add_typer(projects_app, name="projects")


@app.command()
def analyze(
    path: Path = typer.Argument(
        ...,
        help="Projet à analyser.",
    ),
    clean: bool = typer.Option(
        False,
        "--clean",
        help="Nettoyer le cache.",
    ),
) -> None:
    """Analyser un projet local."""
    pass


@projects_app.command("add")
def projects_add() -> None:
    """Ajouter un projet."""
    pass


@projects_app.command("list")
def projects_list() -> None:
    """Lister les projets."""
    pass


@projects_app.command("remove")
def projects_remove() -> None:
    """Retirer un projet."""
    pass


@app.command("status-all")
def status_all_command() -> None:
    """Afficher l’état de tous les projets."""
    pass
''',
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    facts = CliAnalyzer().analyze(
        project,
        entry_points={
            "docforge": "docforge.cli:app"
        },
    )

    assert facts.framework == "Typer"
    assert facts.command_count == 5

    analyze = next(
        command
        for command in facts.commands
        if command.name == "analyze"
    )

    assert analyze.help == "Analyser un projet local."
    assert analyze.module == "docforge.cli"
    assert analyze.command_path == "analyze"

    path_parameter = next(
        parameter
        for parameter in analyze.parameters
        if parameter.name == "path"
    )
    assert path_parameter.kind == "argument"
    assert path_parameter.required is True
    assert path_parameter.help == "Projet à analyser."

    clean_parameter = next(
        parameter
        for parameter in analyze.parameters
        if parameter.name == "clean"
    )
    assert clean_parameter.kind == "option"
    assert clean_parameter.required is False
    assert "--clean" in clean_parameter.flags

    command_paths = {
        command.command_path
        for command in facts.commands
    }
    assert {"projects add", "projects list", "projects remove"}.issubset(
        command_paths
    )


def test_cli_analyzer_does_not_execute_module(
    tmp_path: Path,
) -> None:
    package = tmp_path / "docforge"
    package.mkdir()

    marker = tmp_path / "executed.txt"

    (package / "cli.py").write_text(
        f'''
from pathlib import Path
import typer

Path({str(marker)!r}).write_text("executed")

app = typer.Typer()


@app.command()
def check() -> None:
    pass
''',
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    facts = CliAnalyzer().analyze(project)

    assert facts.command_count == 1
    assert marker.exists() is False


def test_cli_analyzer_recognizes_explicit_ellipsis_marker(
    tmp_path: Path,
) -> None:
    package = tmp_path / "docforge"
    package.mkdir()

    (package / "cli.py").write_text(
        '''
import typer

app = typer.Typer()


@app.command()
def inspect(
    path: str = typer.Argument(
        Ellipsis,
        help="Chemin obligatoire.",
    ),
) -> None:
    pass
''',
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    facts = CliAnalyzer().analyze(project)

    parameter = facts.commands[0].parameters[0]

    assert parameter.name == "path"
    assert parameter.kind == "argument"
    assert parameter.required is True
    assert parameter.default is None
