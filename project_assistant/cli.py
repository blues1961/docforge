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
from project_assistant.project_manager import ProjectManager
from project_assistant.project_registry import ProjectRegistry
from project_assistant.commands.template import analyze_template
from project_assistant.commands.global_invariants import generate_global_invariants
from project_assistant.audit_manager import (
    AuditManager,
    InvariantIntegrityError,
)
from project_assistant.invariant_integrity import InvariantIntegrityManager
from project_assistant.audit_report import generate_audit_report
from project_assistant.audit_diff import (
    AuditDiffAnalyzer,
    AuditDiffError,
    AuditDiffMarkdownGenerator,
)
from project_assistant.status_manager import StatusManager
from project_assistant.remediation import generate_remediation_plan

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
    refresh: bool = typer.Option(
        False,
        "--refresh",
        help=(
            "Régénérer les documents déterministes même "
            "s'ils existent déjà dans le projet."
        ),
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
            refresh=refresh,
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
    table.add_column("Générateur")
    table.add_column("Motif")

    for item in generated:
        table.add_row(
            item.document_path,
            str(item.preview_path),
            item.generator,
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
    refresh: bool = typer.Option(
        False,
        "--refresh",
        help=(
            "Régénérer aussi les documents déterministes "
            "déjà présents."
        ),
    ),
) -> None:
    """Remplir avec Ollama les documents manquants en aperçu."""

    results = generate_preview_with_llm(
        path=path,
        model=model,
        clean=clean,
        refresh=refresh,
    )

    if not results:
        console.print(
            "[green]"
            "Aucun document obligatoire absent à générer."
            "[/green]"
        )
        return

    table = Table(title="Documentation générée")
    table.add_column("Document")
    table.add_column("Aperçu")
    table.add_column("Générateur")
    table.add_column("Débit")

    for item in results:
        rate = (
            f"{item.tokens_per_second:.2f} tokens/s"
            if item.tokens_per_second > 0
            else "—"
        )

        table.add_row(
            item.document_path,
            str(item.preview_path),
            item.generator,
            rate,
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


projects_app = typer.Typer(
    help="Gérer le registre des projets.",
    no_args_is_help=True,
)

app.add_typer(
    projects_app,
    name="projects",
)


@projects_app.command("add")
def projects_add(
    path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Chemin du projet à enregistrer.",
    ),
    name: str | None = typer.Option(
        None,
        "--name",
        help="Nom personnalisé du projet.",
    ),
    profile: str | None = typer.Option(
        None,
        "--profile",
        "-p",
        help="Profil documentaire explicite.",
    ),
) -> None:
    """Ajouter ou mettre à jour un projet dans le registre."""

    registered = ProjectRegistry().add(
        path=path,
        name=name,
        profile=profile,
    )

    console.print(
        f"[green]Projet enregistré :[/green] "
        f"{registered.name}"
    )
    console.print(
        f"[bold]Chemin :[/bold] {registered.path}"
    )
    console.print(
        f"[bold]Profil :[/bold] "
        f"{registered.profile or 'automatique'}"
    )


@projects_app.command("list")
def projects_list() -> None:
    """Afficher les projets enregistrés."""

    registry = ProjectRegistry()
    projects = registry.load()

    if not projects:
        console.print(
            "[yellow]Aucun projet enregistré.[/yellow]"
        )
        console.print(
            f"Registre : {registry.registry_path}"
        )
        return

    table = Table(title="Projets enregistrés")
    table.add_column("Nom")
    table.add_column("Chemin")
    table.add_column("Profil")
    table.add_column("Actif")
    table.add_column("Existe")

    for project in projects:
        table.add_row(
            project.name,
            str(project.path),
            project.profile or "automatique",
            "oui" if project.enabled else "non",
            "oui" if project.path.exists() else "non",
        )

    console.print(table)
    console.print(
        f"\nRegistre : {registry.registry_path}"
    )


@projects_app.command("remove")
def projects_remove(
    identifier: str = typer.Argument(
        ...,
        help="Nom ou chemin du projet à retirer.",
    ),
) -> None:
    """Retirer un projet du registre."""

    removed = ProjectRegistry().remove(identifier)

    if not removed:
        console.print(
            f"[red]Projet introuvable :[/red] {identifier}"
        )
        raise typer.Exit(code=2)

    console.print(
        f"[green]Projet retiré :[/green] {identifier}"
    )


@app.command("refresh-all")
def refresh_all_command(
    clean: bool = typer.Option(
        False,
        "--clean",
        help=(
            "Supprimer les anciens aperçus avant "
            "chaque régénération."
        ),
    ),
) -> None:
    """Actualiser les aperçus de tous les projets enregistrés."""

    results = ProjectManager().refresh_all(
        clean=clean,
    )

    if not results:
        console.print(
            "[yellow]Aucun projet actif dans le registre.[/yellow]"
        )
        return

    table = Table(title="Actualisation multi-projets")
    table.add_column("Projet")
    table.add_column("État")
    table.add_column("Documents")
    table.add_column("Détail")

    success_count = 0
    failure_count = 0

    for result in results:
        if result.error:
            failure_count += 1
            table.add_row(
                result.project.name,
                "[red]erreur[/red]",
                "—",
                result.error,
            )
            continue

        success_count += 1

        documents = ", ".join(
            item.document_path
            for item in result.generated
        ) or "aucun"

        table.add_row(
            result.project.name,
            "[green]succès[/green]",
            documents,
            str(
                result.project.path
                / ".project-assistant"
                / "preview"
            ),
        )

    console.print(table)
    console.print(
        f"\nSuccès : {success_count} — "
        f"Erreurs : {failure_count}"
    )

    if failure_count:
        raise typer.Exit(code=1)


@app.command("analyze-template")
def analyze_template_command(
    path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Chemin du dépôt app-template.",
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Analyser sans écrire template.json.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Afficher l'analyse complète en JSON.",
    ),
) -> None:
    """Analyser le modèle canonique des applications auto-hébergées."""

    facts, cache_path = analyze_template(
        path,
        write_cache=not no_cache,
    )

    if json_output:
        from dataclasses import asdict
        import json

        console.print_json(
            json.dumps(
                asdict(facts),
                ensure_ascii=False,
            )
        )
        return

    console.print(
        f"\n[bold]Template :[/bold] {facts.name}"
    )
    console.print(
        f"[bold]Racine :[/bold] {facts.root}"
    )

    summary = Table(title="Résumé du template")
    summary.add_column("Élément")
    summary.add_column("Valeur")

    summary.add_row(
        "Langages",
        ", ".join(facts.languages) or "aucun",
    )
    summary.add_row(
        "Frameworks",
        ", ".join(facts.frameworks) or "aucun",
    )
    summary.add_row(
        "Technologies",
        ", ".join(facts.technologies) or "aucune",
    )
    summary.add_row(
        "Cibles Makefile",
        str(len(facts.make_targets)),
    )
    summary.add_row(
        "Scripts",
        str(len(facts.scripts)),
    )
    summary.add_row(
        "Workflows GitHub",
        str(len(facts.github_workflows)),
    )
    summary.add_row(
        "Politique de secrets",
        "détectée"
        if facts.secrets_policy_detected
        else "non détectée",
    )
    summary.add_row(
        "Lien .env",
        facts.env_symlink_target or "absent",
    )

    console.print()
    console.print(summary)

    documents = Table(title="Documents canoniques")
    documents.add_column("État")
    documents.add_column("Document")

    for rule in facts.documents:
        documents.add_row(
            "[green]✓[/green]"
            if rule.exists
            else "[red]✗[/red]",
            rule.path,
        )

    console.print()
    console.print(documents)

    environment = Table(
        title="Fichiers d'environnement canoniques"
    )
    environment.add_column("État")
    environment.add_column("Fichier")

    for rule in facts.environment_files:
        environment.add_row(
            "[green]✓[/green]"
            if rule.exists
            else "[yellow]—[/yellow]",
            rule.path,
        )

    console.print()
    console.print(environment)

    if cache_path:
        console.print(
            f"\n[green]Cache créé :[/green] {cache_path}"
        )


@app.command("generate-global-invariants")
def generate_global_invariants_command(
    template_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Chemin du dépôt app-template.",
    ),
    output: Path = typer.Option(
        Path("defaults/global-invariants.md"),
        "--output",
        "-o",
        help="Fichier Markdown à générer.",
    ),
) -> None:
    """Générer les invariants globaux depuis app-template."""

    output_path = generate_global_invariants(
        template_path=template_path,
        output_path=output,
    )

    console.print(
        f"[green]Invariants globaux générés :[/green] "
        f"{output_path}"
    )


@app.command("audit-all")
def audit_all_command(
    template_path: Path = typer.Option(
        Path.home() / "projets" / "app-template",
        "--template",
        help="Chemin du template canonique.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
    show_findings: bool = typer.Option(
        False,
        "--show-findings",
        help="Afficher les écarts détaillés.",
    ),
) -> None:
    """Comparer les applications enregistrées à app-template."""

    manager = AuditManager()

    try:
        results = manager.audit_all(template_path)
    except InvariantIntegrityError as error:
        report = error.report

        console.print("[red]Audit bloqué.[/red]")

        if not report.baseline_exists:
            console.print(
                "Aucune version approuvée des invariants "
                "n'est enregistrée."
            )
            console.print(
                "Après validation explicite du propriétaire :"
            )
            console.print(
                "project-assistant approve-invariants "
                f"{template_path} --owner-approved"
            )
            raise typer.Exit(code=2)

        console.print(
            "Les fichiers protégés du template ne "
            "correspondent plus à la version approuvée."
        )
        console.print(
            "Aucune conformité applicative ne sera évaluée "
            "tant que cette dérive n'aura pas été examinée."
        )

        drift_table = Table(title="Dérive des invariants")
        drift_table.add_column("Fichier")
        drift_table.add_column("État")
        drift_table.add_column("Empreinte approuvée")
        drift_table.add_column("Empreinte actuelle")

        for drift in report.drifts:
            drift_table.add_row(
                drift.path,
                drift.status,
                drift.expected_sha256 or "—",
                drift.actual_sha256 or "—",
            )

        console.print(drift_table)
        raise typer.Exit(code=1)

    table = Table(title="Conformité des applications auto-hébergées")
    table.add_column("Projet")
    table.add_column("État")
    table.add_column("Score")
    table.add_column("Écarts")
    table.add_column("Détail")

    errors = 0

    for result in results:
        if result.error:
            errors += 1
            table.add_row(
                result.project.name,
                "[red]erreur[/red]",
                "—",
                "—",
                result.error,
            )
            continue

        report = result.report

        if report is None:
            continue

        if not report.eligible:
            table.add_row(
                result.project.name,
                "[dim]ignoré[/dim]",
                "—",
                "—",
                report.profile_reason,
            )
            continue

        error_count = sum(
            1
            for finding in report.findings
            if finding.severity == "error"
        )
        warning_count = sum(
            1
            for finding in report.findings
            if finding.severity == "warning"
        )

        if error_count:
            state = "[red]non conforme[/red]"
        elif warning_count:
            state = "[yellow]à vérifier[/yellow]"
        else:
            state = "[green]conforme[/green]"

        table.add_row(
            result.project.name,
            state,
            f"{report.score} %",
            (
                f"{error_count} erreur(s), "
                f"{warning_count} avertissement(s)"
            ),
            report.profile_reason,
        )

    console.print(table)

    if show_findings:
        for result in results:
            report = result.report

            if (
                report is None
                or not report.eligible
                or not report.findings
            ):
                continue

            console.print(
                f"\n[bold]{report.project_name}[/bold]"
            )

            findings = Table()
            findings.add_column("Sévérité")
            findings.add_column("Code")
            findings.add_column("Catégorie")
            findings.add_column("Message")
            findings.add_column("Fichier")

            for finding in report.findings:
                findings.add_row(
                    finding.severity,
                    finding.code,
                    finding.category,
                    finding.message,
                    finding.path or "—",
                )

            console.print(findings)

    if errors:
        raise typer.Exit(code=1)


@app.command("approve-invariants")
def approve_invariants_command(
    template_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Chemin du dépôt app-template.",
    ),
    owner_approved: bool = typer.Option(
        False,
        "--owner-approved",
        help=(
            "Confirmer que le propriétaire autorise "
            "l'enregistrement de cette version."
        ),
    ),
) -> None:
    """Enregistrer la version approuvée des invariants globaux."""

    if not owner_approved:
        console.print(
            "[red]Approbation refusée.[/red] "
            "Utilisez --owner-approved uniquement après "
            "validation explicite du propriétaire."
        )
        raise typer.Exit(code=2)

    baseline = InvariantIntegrityManager().approve(
        template_path
    )

    console.print(
        "[green]Version des invariants approuvée.[/green]"
    )
    console.print(
        f"Template : {baseline.template_root}"
    )
    console.print(
        f"Date : {baseline.approved_at}"
    )

    for state in baseline.files:
        console.print(
            f"  ✓ {state.path}  {state.sha256}"
        )


@app.command("verify-invariants")
def verify_invariants_command(
    template_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Chemin du dépôt app-template.",
    ),
) -> None:
    """Vérifier que les invariants correspondent à la version approuvée."""

    report = InvariantIntegrityManager().verify(
        template_path
    )

    if not report.baseline_exists:
        console.print(
            "[red]Aucune référence approuvée n'existe.[/red]"
        )
        console.print(
            "Exécutez approve-invariants avec "
            "--owner-approved après validation."
        )
        raise typer.Exit(code=2)

    if report.valid:
        console.print(
            "[green]Les invariants protégés sont intacts.[/green]"
        )
        console.print(
            f"Référence : {report.baseline_path}"
        )
        return

    console.print(
        "[red]Dérive des invariants détectée.[/red]"
    )
    console.print(
        "Aucune correction automatique ne doit être appliquée."
    )
    console.print(
        "Une validation explicite du propriétaire est requise."
    )

    table = Table(title="Dérives détectées")
    table.add_column("Fichier")
    table.add_column("État")
    table.add_column("Empreinte approuvée")
    table.add_column("Empreinte actuelle")

    for drift in report.drifts:
        table.add_row(
            drift.path,
            drift.status,
            drift.expected_sha256 or "—",
            drift.actual_sha256 or "—",
        )

    console.print(table)
    raise typer.Exit(code=1)


@app.command("audit-report")
def audit_report_command(
    template_path: Path = typer.Option(
        Path.home() / "projets" / "app-template",
        "--template",
        help="Chemin du template canonique.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
    output_dir: Path = typer.Option(
        Path("reports"),
        "--output-dir",
        "-o",
        help="Répertoire de destination des rapports.",
    ),
) -> None:
    """Générer un rapport persistant JSON et Markdown."""

    try:
        files = generate_audit_report(
            template_path=template_path,
            output_dir=output_dir,
        )
    except InvariantIntegrityError as error:
        console.print(
            "[red]Rapport bloqué.[/red]"
        )

        if not error.report.baseline_exists:
            console.print(
                "Aucune version approuvée des invariants "
                "n'est enregistrée."
            )
            raise typer.Exit(code=2)

        console.print(
            "Les invariants protégés ont dérivé. "
            "Aucun rapport n'a été généré."
        )
        raise typer.Exit(code=1)

    console.print(
        "[green]Rapport d'audit généré.[/green]"
    )
    console.print(
        f"JSON courant : {files.latest_json}"
    )
    console.print(
        f"Markdown courant : {files.latest_markdown}"
    )
    console.print(
        f"Historique JSON : {files.history_json}"
    )
    console.print(
        f"Historique Markdown : {files.history_markdown}"
    )


@app.command("audit-diff")
def audit_diff_command(
    current: Path = typer.Option(
        Path("reports/audit-latest.json"),
        "--current",
        help="Rapport JSON courant.",
    ),
    previous: Path | None = typer.Option(
        None,
        "--previous",
        help=(
            "Rapport JSON précédent. "
            "Le plus récent de reports/history est utilisé par défaut."
        ),
    ),
    output: Path | None = typer.Option(
        Path("reports/audit-diff-latest.md"),
        "--output",
        "-o",
        help="Fichier Markdown de comparaison.",
    ),
) -> None:
    """Comparer deux rapports de conformité."""

    analyzer = AuditDiffAnalyzer()

    current_path = current.expanduser().resolve()

    try:
        previous_path = (
            previous.expanduser().resolve()
            if previous is not None
            else analyzer.find_previous_report(
                reports_directory=current_path.parent,
                current_path=current_path,
            )
        )

        report = analyzer.compare(
            previous_path=previous_path,
            current_path=current_path,
        )
    except (
        AuditDiffError,
        FileNotFoundError,
    ) as error:
        console.print(
            f"[red]Comparaison impossible :[/red] {error}"
        )
        raise typer.Exit(code=2)

    table = Table(title="Évolution de la conformité")
    table.add_column("Projet")
    table.add_column("Évolution")
    table.add_column("État précédent")
    table.add_column("État courant")
    table.add_column("Score précédent")
    table.add_column("Score courant")
    table.add_column("Écart")

    groups = [
        ("amélioré", report.improved),
        ("dégradé", report.regressed),
        ("nouveau", report.added),
        ("retiré", report.removed),
        ("inchangé", report.unchanged),
    ]

    for label, changes in groups:
        for change in changes:
            delta = (
                f"{change.score_delta:+d}"
                if change.score_delta is not None
                else "—"
            )

            table.add_row(
                change.name,
                label,
                change.previous_state or "—",
                change.current_state or "—",
                (
                    str(change.previous_score)
                    if change.previous_score is not None
                    else "—"
                ),
                (
                    str(change.current_score)
                    if change.current_score is not None
                    else "—"
                ),
                delta,
            )

    console.print(table)

    console.print(
        "\n"
        f"Améliorés : {len(report.improved)} — "
        f"Dégradés : {len(report.regressed)} — "
        f"Inchangés : {len(report.unchanged)} — "
        f"Nouveaux : {len(report.added)} — "
        f"Retirés : {len(report.removed)}"
    )

    if output is not None:
        output_path = output.expanduser().resolve()
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        output_path.write_text(
            AuditDiffMarkdownGenerator().generate(report),
            encoding="utf-8",
        )

        console.print(
            f"\n[green]Rapport de comparaison :[/green] "
            f"{output_path}"
        )


@app.command("status-all")
def status_all_command(
    template_path: Path = typer.Option(
        Path.home() / "projets" / "app-template",
        "--template",
        help="Chemin du template canonique.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
    show_details: bool = typer.Option(
        False,
        "--show-details",
        help=(
            "Afficher les documents différents et "
            "les écarts de conformité."
        ),
    ),
) -> None:
    """Afficher l’état quotidien de tous les projets."""

    ecosystem = StatusManager().collect(
        template_path
    )

    if not ecosystem.invariants_valid:
        console.print(
            "[red]État global bloqué.[/red]"
        )
        console.print(
            ecosystem.invariant_error
            or "Les invariants ne sont pas valides."
        )
        console.print(
            "Exécutez : project-assistant "
            f"verify-invariants {template_path}"
        )
        raise typer.Exit(code=1)

    table = Table(title="État quotidien des projets")
    table.add_column("Projet")
    table.add_column("Git")
    table.add_column("Branche")
    table.add_column("Synchro")
    table.add_column("Conformité")
    table.add_column("Documentation")
    table.add_column("État")

    blocking_issues = 0

    for item in ecosystem.projects:
        git_status = item.git

        if not git_status.is_repository:
            git_label = "[red]non Git[/red]"
            branch = "—"
            sync = "—"
            blocking_issues += 1
        else:
            git_label = (
                "[yellow]modifié[/yellow]"
                if git_status.dirty
                else "[green]propre[/green]"
            )
            branch = git_status.branch or "—"

            sync_parts: list[str] = []

            if git_status.ahead:
                sync_parts.append(
                    f"+{git_status.ahead}"
                )

            if git_status.behind:
                sync_parts.append(
                    f"-{git_status.behind}"
                )

            sync = ", ".join(sync_parts) or "à jour"

        compliance = item.compliance

        if item.error:
            compliance_label = "[red]erreur[/red]"
            state = item.error
            blocking_issues += 1
        elif compliance is None:
            compliance_label = "—"
            state = "template ou projet non audité"
        elif not compliance.eligible:
            compliance_label = "[dim]ignoré[/dim]"
            state = compliance.profile_reason
        else:
            error_count = sum(
                1
                for finding in compliance.findings
                if finding.severity == "error"
            )
            warning_count = sum(
                1
                for finding in compliance.findings
                if finding.severity == "warning"
            )

            if error_count:
                compliance_label = (
                    f"[red]{compliance.score} %[/red]"
                )
                state = (
                    f"{error_count} erreur(s), "
                    f"{warning_count} avertissement(s)"
                )
                blocking_issues += 1
            elif warning_count:
                compliance_label = (
                    f"[yellow]{compliance.score} %[/yellow]"
                )
                state = (
                    f"{warning_count} avertissement(s)"
                )
            else:
                compliance_label = (
                    f"[green]{compliance.score} %[/green]"
                )
                state = "aucun écart"

        documentation = item.documentation

        difference_count = (
            len(documentation.changed_documents)
            + len(documentation.new_documents)
        )

        if not documentation.preview_exists:
            documentation_label = "aucun aperçu"
        elif difference_count:
            documentation_label = (
                f"[yellow]{difference_count} changement(s)[/yellow]"
            )
        else:
            documentation_label = (
                "[green]à jour[/green]"
            )

        table.add_row(
            item.project.name,
            git_label,
            branch,
            sync,
            compliance_label,
            documentation_label,
            state,
        )

    console.print(table)

    if show_details:
        for item in ecosystem.projects:
            documentation = item.documentation
            compliance = item.compliance

            has_details = (
                documentation.changed_documents
                or documentation.new_documents
                or (
                    compliance is not None
                    and compliance.findings
                )
                or item.error
            )

            if not has_details:
                continue

            console.print(
                f"\n[bold]{item.project.name}[/bold]"
            )

            if item.error:
                console.print(
                    f"[red]{item.error}[/red]"
                )

            if documentation.changed_documents:
                console.print(
                    "[yellow]Documents modifiés dans l’aperçu :[/yellow]"
                )

                for document in (
                    documentation.changed_documents
                ):
                    console.print(f"  - {document}")

            if documentation.new_documents:
                console.print(
                    "[yellow]Nouveaux documents dans l’aperçu :[/yellow]"
                )

                for document in (
                    documentation.new_documents
                ):
                    console.print(f"  - {document}")

            if (
                compliance is not None
                and compliance.findings
            ):
                findings_table = Table()
                findings_table.add_column("Sévérité")
                findings_table.add_column("Code")
                findings_table.add_column("Message")

                for finding in compliance.findings:
                    findings_table.add_row(
                        finding.severity,
                        finding.code,
                        finding.message,
                    )

                console.print(findings_table)

    console.print(
        f"\nProblèmes bloquants : {blocking_issues}"
    )


@app.command("remediation-plan")
def remediation_plan_command(
    template_path: Path = typer.Option(
        Path.home() / "projets" / "app-template",
        "--template",
        help="Chemin du template canonique.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
    output: Path = typer.Option(
        Path("reports/remediation-latest.md"),
        "--output",
        "-o",
        help="Fichier Markdown à générer.",
    ),
) -> None:
    """Générer un plan de mise en conformité sans appliquer de changement."""

    try:
        output_path = generate_remediation_plan(
            template_path=template_path,
            output_path=output,
        )
    except InvariantIntegrityError as error:
        console.print(
            "[red]Plan bloqué.[/red]"
        )
        console.print(str(error))
        console.print(
            "Les invariants doivent être vérifiés et approuvés "
            "avant toute proposition de mise en conformité."
        )
        raise typer.Exit(code=1)

    console.print(
        "[green]Plan de mise en conformité généré :[/green] "
        f"{output_path}"
    )
