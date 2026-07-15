from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from docforge.models import Project


@dataclass(slots=True)
class SecurityControlFacts:
    identifier: str
    category: str
    description: str
    evidence: str | None = None


@dataclass(slots=True)
class SecurityFacts:
    protected_documents: list[str] = field(default_factory=list)
    ignored_sensitive_paths: list[str] = field(default_factory=list)
    controls: list[SecurityControlFacts] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    validation_commands: list[str] = field(default_factory=list)


class SecurityAnalyzer:
    SENSITIVE_PATHS = (
        ".env.local",
        ".env.*.local",
        ".project-assistant/",
        ".venv/",
        "__pycache__/",
        ".pytest_cache/",
    )

    def analyze(
        self,
        project: Project,
        *,
        protected_documents: tuple[str, ...] = (),
    ) -> SecurityFacts:
        gitignore_entries = self._gitignore_entries(
            project.root
        )

        ignored_sensitive_paths = [
            path
            for path in self.SENSITIVE_PATHS
            if self._is_ignored(
                path,
                gitignore_entries,
            )
        ]

        controls = [
            SecurityControlFacts(
                identifier="SEC-001",
                category="secrets",
                description=(
                    "Le contenu des fichiers de secrets ne doit "
                    "jamais être lu, reproduit ou sérialisé."
                ),
                evidence=".env.local exclu des analyses documentaires.",
            ),
            SecurityControlFacts(
                identifier="SEC-002",
                category="aperçu",
                description=(
                    "La génération documentaire doit écrire dans "
                    ".project-assistant/preview avant toute application."
                ),
                evidence=".project-assistant/preview/",
            ),
            SecurityControlFacts(
                identifier="SEC-003",
                category="application",
                description=(
                    "Un document généré ne doit être appliqué "
                    "qu’après une commande explicite."
                ),
                evidence="docforge apply",
            ),
            SecurityControlFacts(
                identifier="SEC-004",
                category="invariants",
                description=(
                    "Les documents protégés doivent exiger une "
                    "autorisation explicite du propriétaire."
                ),
                evidence="--owner-approved",
            ),
            SecurityControlFacts(
                identifier="SEC-005",
                category="intégrité",
                description=(
                    "Les invariants approuvés doivent pouvoir être "
                    "vérifiés par empreinte."
                ),
                evidence="invariant-baseline.json",
            ),
            SecurityControlFacts(
                identifier="SEC-006",
                category="portabilité",
                description=(
                    "Les documents générés ne doivent pas contenir "
                    "de chemin absolu propre à une machine."
                ),
            ),
            SecurityControlFacts(
                identifier="SEC-007",
                category="Git",
                description=(
                    "Les caches, aperçus, environnements virtuels et "
                    "secrets ne doivent pas être suivis par Git."
                ),
                evidence=".gitignore",
            ),
            SecurityControlFacts(
                identifier="SEC-008",
                category="analyse statique",
                description=(
                    "Les analyseurs doivent éviter d’importer ou "
                    "d’exécuter le code des projets inspectés."
                ),
                evidence="analyse AST du CLI",
            ),
        ]

        risks = [
            (
                "Divulgation involontaire d’un secret dans un "
                "document, un rapport ou un journal."
            ),
            (
                "Application automatique d’un aperçu non validé."
            ),
            (
                "Modification non autorisée d’un document "
                "d’invariants."
            ),
            (
                "Exécution de code lors de l’analyse d’un dépôt."
            ),
            (
                "Introduction d’un chemin local non portable dans "
                "la documentation."
            ),
            (
                "Suivi Git accidentel des caches ou des aperçus."
            ),
            (
                "Affaiblissement d’un test afin de masquer une "
                "régression de sécurité."
            ),
        ]

        return SecurityFacts(
            protected_documents=sorted(
                set(protected_documents)
            ),
            ignored_sensitive_paths=sorted(
                ignored_sensitive_paths
            ),
            controls=controls,
            risks=risks,
            validation_commands=[
                "pytest -q",
                "docforge --help",
                (
                    "docforge verify-invariants "
                    "/chemin/vers/app-template"
                ),
                (
                    "docforge document "
                    "/chemin/du/projet --refresh --clean"
                ),
                "git status --short",
            ],
        )

    @staticmethod
    def _gitignore_entries(root: Path) -> set[str]:
        path = root / ".gitignore"

        if not path.is_file():
            return set()

        try:
            return {
                line.strip()
                for line in path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                ).splitlines()
                if line.strip()
                and not line.lstrip().startswith("#")
            }
        except OSError:
            return set()

    @staticmethod
    def _is_ignored(
        path: str,
        entries: set[str],
    ) -> bool:
        normalized = path.rstrip("/")

        return (
            path in entries
            or normalized in entries
            or f"{normalized}/" in entries
        )
