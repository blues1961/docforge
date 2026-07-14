from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from project_assistant.commands.apply import apply_preview_documents
from project_assistant.commands.document import (
    generate_documentation_preview,
)
from project_assistant.commands.generate import (
    generate_preview_with_llm,
)
from project_assistant.commands.init import initialize_project
from project_assistant.commands.verify import verify_project
from project_assistant.detectors import TechnologyDetector
from project_assistant.scanners import FileSystemScanner

app = typer.Typer(
    name="project-assistant",
    help="Analyse et documente des projets logiciels.",
    no_args_is_help=True,
)

console = Console()


@app.callback()
def main() -> None:
    """Assistant local d'analyse et de documentation de projets."""
    return None


@app.command()
def analyze(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Chemin du projet à analyser.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Afficher le résultat complet en JSON.",
    ),
) -> None:
    """Analyser un projet sans modifier ses fichiers."""

    project = FileSystemScanner().scan(path)
    TechnologyDetector().detect(project)

    if json_output:
        console.print_json(
            json.dumps(
                project.to_dict(),
                ensure_ascii=False,
            )
        )
        return

    console.print(f"\n[bold]Projet :[/bold] {project.name}")
    console.print(f"[bold]Chemin :[/bold] {project.root}")
    console.print(f"[bold]Profil :[/bold] {project.profile}\n")

    summary = Table(title="Résumé")
    summary.add_column("Élément")
    summary.add_column("Valeur")

    summary.add_row(
        "Fichiers",
        str(project.statistics.file_count),
    )
    summary.add_row(
        "Dossiers",
        str(project.statistics.directory_count),
    )
    summary.add_row(
        "Liens symboliques",
        str(project.statistics.symlink_count),
    )
    summary.add_row(
        "Environnement actif",
        project.environment.active_environment or "non détecté",
    )
    summary.add_row(
        "Traefik",
        "oui" if project.docker.uses_traefik else "non",
    )

    console.print(summary)

    technologies = Table(title="Technologies détectées")
    technologies.add_column("Nom")
    technologies.add_column("Catégorie")
    technologies.add_column("Version")
    technologies.add_column("Preuves")

    for technology in project.technologies:
        technologies.add_row(
            technology.name,
            technology.category,
            technology.version or "—",
            ", ".join(technology.evidence),
        )

    console.print()
    console.print(technologies)

    docker = Table(title="Docker")
    docker.add_column("Élément")
    docker.add_column("Valeur")

    docker.add_row(
        "Fichiers Compose",
        ", ".join(project.docker.compose_files) or "aucun",
    )
    docker.add_row(
        "Services",
        ", ".join(
            service.name
            for service in project.docker.services
        )
        or "aucun",
    )
    docker.add_row(
        "Réseaux",
        ", ".join(project.docker.networks) or "aucun",
    )
    docker.add_row(
        "Volumes",
        ", ".join(project.docker.volumes) or "aucun",
    )

    console.print()
    console.print(docker)

    if project.findings:
        findings = Table(title="Constats")
        findings.add_column("Sévérité")
        findings.add_column("Code")
        findings.add_column("Message")
        findings.add_column("Chemin")

        for finding in project.findings:
            findings.add_row(
                finding.severity,
                finding.code,
                finding.message,
                finding.path or "—",
            )

        console.print()
        console.print(findings)
    else:
        console.print("\n[green]Aucune anomalie détectée.[/green]")


@app.command()
def verify(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Chemin du projet à vérifier.",
    ),
    profile: str | None = typer.Option(
        None,
        "--profile",
        "-p",
        help=(
            "Profil documentaire à appliquer. "
            "Par défaut, utilise la configuration locale "
            "ou la détection automatique."
        ),
    ),
) -> None:
    """Comparer un projet au standard documentaire."""

    project = verify_project(
        path=path,
        profile=profile,
    )

    console.print(
        f"\n[bold]Projet :[/bold] {project.name}"
    )
    console.print(
        f"[bold]Profil :[/bold] {project.profile}\n"
    )

    documents = Table(title="Conformité documentaire")
    documents.add_column("État")
    documents.add_column("Document")
    documents.add_column("Obligation")
    documents.add_column("Catégorie")
    documents.add_column("Taille")

    for document in project.documents:
        if document.exists:
            status = "[green]✓[/green]"
        elif document.required:
            status = "[red]✗[/red]"
        else:
            status = "[yellow]—[/yellow]"

        documents.add_row(
            status,
            document.path,
            "obligatoire" if document.required else "facultatif",
            document.category or "—",
            (
                f"{document.size_bytes} octets"
                if document.exists
                else "absent"
            ),
        )

    console.print(documents)

    documentation_findings = [
        finding
        for finding in project.findings
        if finding.code.startswith("DOC")
    ]

    if documentation_findings:
        findings = Table(title="Écarts documentaires")
        findings.add_column("Sévérité")
        findings.add_column("Code")
        findings.add_column("Document")
        findings.add_column("Message")

        for finding in documentation_findings:
            findings.add_row(
                finding.severity,
                finding.code,
                finding.path or "—",
                finding.message,
            )

        console.print()
        console.print(findings)
    else:
        console.print(
            "\n[green]"
            "Le projet respecte le standard documentaire."
            "[/green]"
        )


@app.command("init")
def init_command(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Chemin du projet à initialiser.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Remplacer une configuration locale existante.",
    ),
) -> None:
    """Créer la configuration locale d'un projet."""

    project, config_path = initialize_project(
        path=path,
        force=force,
    )

    console.print(
        f"\n[green]Configuration créée :[/green] {config_path}"
    )
    console.print(
        f"[bold]Projet :[/bold] {project.name}"
    )
    console.print(
        "[bold]Frameworks détectés :[/bold] "
        + (", ".join(project.frameworks) or "aucun")
    )


@app.command()
def document(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Chemin du projet à documenter.",
    ),
    profile: str | None = typer.Option(
        None,
        "--profile",
        "-p",
        help=(
            "Profil documentaire explicite. "
            "Par défaut, utilise la configuration locale."
        ),
    ),
    clean: bool = typer.Option(
        False,
        "--clean",
        help="Supprimer l'ancien aperçu avant la génération.",
    ),
    write: bool = typer.Option(
        False,
        "--write",
        help="Écrire dans le projet réel.",
    ),
) -> None:
    """Générer un aperçu des documents obligatoires manquants."""

    if write:
        console.print(
            "[red]Le mode --write n'est pas encore activé.[/red]"
        )
        raise typer.Exit(code=2)

    project, config, generated = (
        generate_documentation_preview(
            path=path,
            profile=profile,
            clean=clean,
        )
    )

    console.print(
        f"\n[bold]Projet :[/bold] {project.name}"
    )
    console.print(
        f"[bold]Profil :[/bold] {config.profile}"
    )
    console.print(
        "[bold]Mode :[/bold] aperçu sécurisé\n"
    )

    if not generated:
        console.print(
            "[green]"
            "Aucun document obligatoire absent à générer."
            "[/green]"
        )
        return

    table = Table(title="Documents générés en aperçu")
    table.add_column("Document cible")
    table.add_column("Aperçu")
    table.add_column("Motif")

    for item in generated:
        table.add_row(
            item.source_path,
            str(item.preview_path),
            item.reason,
        )

    console.print(table)
    console.print(
        "\n[yellow]"
        "Aucun fichier existant du projet n'a été modifié."
        "[/yellow]"
    )


@app.command("generate")
def generate_command(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Chemin du projet à documenter.",
    ),
    model: str = typer.Option(
        "gemma4:latest",
        "--model",
        "-m",
        help="Modèle Ollama utilisé.",
    ),
    clean: bool = typer.Option(
        False,
        "--clean",
        help="Recréer entièrement le dossier d'aperçu.",
    ),
) -> None:
    """Remplir avec Ollama les documents manquants en aperçu."""

    results = generate_preview_with_llm(
        path=path,
        model=model,
        clean=clean,
    )

    if not results:
        console.print(
            "[green]"
            "Aucun document obligatoire absent à générer."
            "[/green]"
        )
        return

    table = Table(title="Documentation générée par Ollama")
    table.add_column("Document")
    table.add_column("Aperçu")
    table.add_column("Débit")

    for item in results:
        table.add_row(
            item.document_path,
            str(item.preview_path),
            f"{item.tokens_per_second:.2f} tokens/s",
        )

    console.print(table)
    console.print(
        "\n[yellow]"
        "Les fichiers réels du projet n'ont pas été modifiés."
        "[/yellow]"
    )


@app.command("apply")
def apply_command(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Chemin du projet.",
    ),
    documents: list[str] = typer.Argument(
        ...,
        help="Documents d'aperçu à intégrer.",
    ),
    allow_dirty: bool = typer.Option(
        False,
        "--allow-dirty",
        help="Autoriser exceptionnellement un dépôt Git modifié.",
    ),
) -> None:
    """Copier des documents validés de l'aperçu vers le projet."""

    try:
        applied = apply_preview_documents(
            root=path,
            document_paths=documents,
            require_clean_git=not allow_dirty,
        )
    except (
        RuntimeError,
        FileNotFoundError,
        OSError,
    ) as error:
        console.print(f"[red]Erreur :[/red] {error}")
        raise typer.Exit(code=2) from error

    table = Table(title="Documents intégrés")
    table.add_column("Document")
    table.add_column("Destination")
    table.add_column("Sauvegarde")

    for item in applied:
        table.add_row(
            item.document_path,
            str(item.destination),
            str(item.backup) if item.backup else "aucune",
        )

    console.print(table)
    console.print(
        "\n[yellow]"
        "Les changements ne sont pas committés. Vérifiez avec git diff."
        "[/yellow]"
    )
