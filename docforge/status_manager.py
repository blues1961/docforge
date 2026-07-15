from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from docforge.analyzers import (
    TemplateComplianceReport,
)
from docforge.audit_manager import (
    AuditManager,
    InvariantIntegrityError,
)
from docforge.project_registry import (
    ProjectRegistry,
    RegisteredProject,
)


@dataclass(slots=True)
class GitRepositoryStatus:
    is_repository: bool
    branch: str | None = None
    upstream: str | None = None
    dirty: bool = False
    modified_count: int = 0
    untracked_count: int = 0
    ahead: int = 0
    behind: int = 0
    error: str | None = None


@dataclass(slots=True)
class DocumentationPreviewStatus:
    preview_exists: bool
    preview_documents: int = 0
    changed_documents: list[str] = field(
        default_factory=list
    )
    new_documents: list[str] = field(
        default_factory=list
    )


@dataclass(slots=True)
class ProjectDailyStatus:
    project: RegisteredProject
    git: GitRepositoryStatus
    documentation: DocumentationPreviewStatus
    compliance: TemplateComplianceReport | None = None
    error: str | None = None


@dataclass(slots=True)
class EcosystemStatus:
    invariants_valid: bool
    invariant_error: str | None
    projects: list[ProjectDailyStatus]


class StatusManager:
    def __init__(
        self,
        registry: ProjectRegistry | None = None,
        audit_manager: AuditManager | None = None,
    ) -> None:
        self.registry = registry or ProjectRegistry()
        self.audit_manager = audit_manager or AuditManager(
            registry=self.registry
        )

    def collect(
        self,
        template_path: Path,
    ) -> EcosystemStatus:
        template_path = template_path.expanduser().resolve()

        try:
            audit_results = self.audit_manager.audit_all(
                template_path
            )
        except InvariantIntegrityError as error:
            return EcosystemStatus(
                invariants_valid=False,
                invariant_error=str(error),
                projects=[],
            )

        compliance_by_path = {
            result.project.path.expanduser().resolve():
            result
            for result in audit_results
        }

        statuses: list[ProjectDailyStatus] = []

        for registered in self.registry.load():
            if not registered.enabled:
                continue

            resolved_path = (
                registered.path.expanduser().resolve()
            )

            git_status = self._read_git_status(
                resolved_path
            )
            documentation = (
                self._read_documentation_status(
                    resolved_path
                )
            )

            if resolved_path == template_path:
                statuses.append(
                    ProjectDailyStatus(
                        project=registered,
                        git=git_status,
                        documentation=documentation,
                    )
                )
                continue

            audit_result = compliance_by_path.get(
                resolved_path
            )

            if audit_result is None:
                statuses.append(
                    ProjectDailyStatus(
                        project=registered,
                        git=git_status,
                        documentation=documentation,
                        error=(
                            "Projet absent du résultat d’audit."
                        ),
                    )
                )
                continue

            statuses.append(
                ProjectDailyStatus(
                    project=registered,
                    git=git_status,
                    documentation=documentation,
                    compliance=audit_result.report,
                    error=audit_result.error,
                )
            )

        return EcosystemStatus(
            invariants_valid=True,
            invariant_error=None,
            projects=statuses,
        )

    def _read_git_status(
        self,
        root: Path,
    ) -> GitRepositoryStatus:
        if not root.is_dir():
            return GitRepositoryStatus(
                is_repository=False,
                error=f"Dossier introuvable : {root}",
            )

        repository_check = self._git(
            root,
            "rev-parse",
            "--is-inside-work-tree",
        )

        if repository_check.returncode != 0:
            return GitRepositoryStatus(
                is_repository=False,
                error="Le dossier n’est pas un dépôt Git.",
            )

        branch_result = self._git(
            root,
            "branch",
            "--show-current",
        )
        branch = (
            branch_result.stdout.strip()
            or "HEAD détachée"
        )

        porcelain = self._git(
            root,
            "status",
            "--porcelain",
        )

        if porcelain.returncode != 0:
            return GitRepositoryStatus(
                is_repository=True,
                branch=branch,
                error=porcelain.stderr.strip(),
            )

        status_lines = [
            line
            for line in porcelain.stdout.splitlines()
            if line
        ]

        untracked_count = sum(
            1
            for line in status_lines
            if line.startswith("??")
        )
        modified_count = (
            len(status_lines) - untracked_count
        )

        upstream_result = self._git(
            root,
            "rev-parse",
            "--abbrev-ref",
            "--symbolic-full-name",
            "@{upstream}",
        )

        upstream: str | None = None
        ahead = 0
        behind = 0

        if upstream_result.returncode == 0:
            upstream = upstream_result.stdout.strip()

            counts = self._git(
                root,
                "rev-list",
                "--left-right",
                "--count",
                f"{upstream}...HEAD",
            )

            if counts.returncode == 0:
                parts = counts.stdout.strip().split()

                if len(parts) == 2:
                    behind = int(parts[0])
                    ahead = int(parts[1])

        return GitRepositoryStatus(
            is_repository=True,
            branch=branch,
            upstream=upstream,
            dirty=bool(status_lines),
            modified_count=modified_count,
            untracked_count=untracked_count,
            ahead=ahead,
            behind=behind,
        )

    @staticmethod
    def _read_documentation_status(
        root: Path,
    ) -> DocumentationPreviewStatus:
        preview_root = (
            root
            / ".docforge"
            / "preview"
        )

        if not preview_root.is_dir():
            return DocumentationPreviewStatus(
                preview_exists=False
            )

        preview_files = sorted(
            path
            for path in preview_root.rglob("*")
            if path.is_file()
        )

        changed: list[str] = []
        new: list[str] = []

        for preview_path in preview_files:
            relative_path = preview_path.relative_to(
                preview_root
            )
            target_path = root / relative_path

            if not target_path.exists():
                new.append(str(relative_path))
                continue

            try:
                preview_content = preview_path.read_bytes()
                target_content = target_path.read_bytes()
            except OSError:
                continue

            if preview_content != target_content:
                changed.append(str(relative_path))

        return DocumentationPreviewStatus(
            preview_exists=True,
            preview_documents=len(preview_files),
            changed_documents=changed,
            new_documents=new,
        )

    @staticmethod
    def _git(
        root: Path,
        *arguments: str,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(root), *arguments],
            capture_output=True,
            text=True,
            check=False,
        )
