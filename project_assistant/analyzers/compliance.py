from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from project_assistant.analyzers.architecture import (
    ArchitectureAnalyzer,
)
from project_assistant.analyzers.deployment import (
    DeploymentAnalyzer,
)
from project_assistant.analyzers.template import (
    TemplateFacts,
)
from project_assistant.detectors import TechnologyDetector
from project_assistant.models import Project
from project_assistant.scanners import FileSystemScanner


@dataclass(slots=True)
class ComplianceFinding:
    code: str
    severity: str
    category: str
    message: str
    path: str | None = None
    expected: str | None = None
    actual: str | None = None


@dataclass(slots=True)
class ComplianceCheck:
    code: str
    category: str
    description: str
    passed: bool
    severity: str = "error"


@dataclass(slots=True)
class TemplateComplianceReport:
    project_name: str
    project_root: str
    eligible: bool
    profile_reason: str

    checks: list[ComplianceCheck] = field(default_factory=list)
    findings: list[ComplianceFinding] = field(default_factory=list)

    passed_checks: int = 0
    total_checks: int = 0
    score: int = 0


class TemplateComplianceAnalyzer:
    def analyze(
        self,
        project_root: Path,
        template: TemplateFacts,
    ) -> TemplateComplianceReport:
        root = project_root.expanduser().resolve()

        project = FileSystemScanner().scan(root)
        TechnologyDetector().detect(project)

        eligible, reason = self._is_eligible(project)

        report = TemplateComplianceReport(
            project_name=project.name,
            project_root=str(project.root),
            eligible=eligible,
            profile_reason=reason,
        )

        if not eligible:
            return report

        architecture = ArchitectureAnalyzer().analyze(project)
        deployment = DeploymentAnalyzer().analyze(project)

        self._check_documents(project, template, report)
        self._check_compose_files(project, template, report)
        self._check_scripts(project, template, report)
        self._check_make_targets(
            deployment.make_targets,
            template.make_targets,
            report,
        )
        self._check_services(
            [service.name for service in architecture.services],
            (
                [service.name for service in template.architecture.services]
                if template.architecture
                else []
            ),
            report,
        )
        self._check_networks(
            architecture.external_networks,
            (
                template.architecture.external_networks
                if template.architecture
                else []
            ),
            report,
        )
        self._check_environment(project, template, report)
        self._check_secrets_policy(project, report)

        report.total_checks = len(report.checks)
        report.passed_checks = sum(
            1
            for check in report.checks
            if check.passed
        )

        report.score = (
            round(
                report.passed_checks
                / report.total_checks
                * 100
            )
            if report.total_checks
            else 100
        )

        return report

    @staticmethod
    def _is_eligible(
        project: Project,
    ) -> tuple[bool, str]:
        frameworks = set(project.frameworks)
        compose_files = set(project.docker.compose_files)

        if (
            "Django" in frameworks
            and "React" in frameworks
            and {
                "docker-compose.dev.yml",
                "docker-compose.prod.yml",
            }.issubset(compose_files)
        ):
            return (
                True,
                "application Django/React avec Compose dev et prod",
            )

        return (
            False,
            "projet hors du profil applicatif Django/React canonique",
        )

    def _check_documents(
        self,
        project: Project,
        template: TemplateFacts,
        report: TemplateComplianceReport,
    ) -> None:
        existing = set(project.files) | set(project.symlinks)

        required = [
            rule.path
            for rule in template.documents
            if rule.source_authoritative
        ]

        for path in required:
            passed = path in existing

            self._add_check(
                report,
                code="DOC001",
                category="documentation",
                description=f"Document canonique `{path}` présent",
                passed=passed,
                path=path,
                message=f"Document canonique absent : `{path}`.",
            )

    def _check_compose_files(
        self,
        project: Project,
        template: TemplateFacts,
        report: TemplateComplianceReport,
    ) -> None:
        existing = set(project.files)

        required = [
            rule.path
            for rule in template.compose_files
            if rule.source_authoritative
        ]

        for path in required:
            passed = path in existing

            self._add_check(
                report,
                code="CMP001",
                category="docker-compose",
                description=f"Fichier Compose `{path}` présent",
                passed=passed,
                path=path,
                message=f"Fichier Docker Compose absent : `{path}`.",
            )

    def _check_scripts(
        self,
        project: Project,
        template: TemplateFacts,
        report: TemplateComplianceReport,
    ) -> None:
        existing = set(project.files)

        for path in template.scripts:
            passed = path in existing

            self._add_check(
                report,
                code="SCR001",
                category="scripts",
                description=f"Script canonique `{path}` présent",
                passed=passed,
                path=path,
                message=f"Script canonique absent : `{path}`.",
            )

    def _check_make_targets(
        self,
        actual_targets: list[str],
        expected_targets: list[str],
        report: TemplateComplianceReport,
    ) -> None:
        actual = set(actual_targets)

        for target in expected_targets:
            passed = target in actual

            self._add_check(
                report,
                code="MAKE001",
                category="makefile",
                description=f"Cible `make {target}` disponible",
                passed=passed,
                path="Makefile",
                message=f"Cible Makefile absente : `make {target}`.",
                expected=target,
            )

    def _check_services(
        self,
        actual_services: list[str],
        expected_services: list[str],
        report: TemplateComplianceReport,
    ) -> None:
        actual = set(actual_services)

        for service in expected_services:
            passed = service in actual

            self._add_check(
                report,
                code="ARC001",
                category="architecture",
                description=f"Service Docker `{service}` présent",
                passed=passed,
                message=f"Service Docker canonique absent : `{service}`.",
                expected=service,
            )

    def _check_networks(
        self,
        actual_networks: list[str],
        expected_networks: list[str],
        report: TemplateComplianceReport,
    ) -> None:
        actual = set(actual_networks)

        for network in expected_networks:
            passed = network in actual

            self._add_check(
                report,
                code="NET001",
                category="network",
                description=f"Réseau externe `{network}` présent",
                passed=passed,
                message=f"Réseau Docker externe absent : `{network}`.",
                expected=network,
            )

    def _check_environment(
        self,
        project: Project,
        template: TemplateFacts,
        report: TemplateComplianceReport,
    ) -> None:
        expected_files = [
            ".env.dev",
            ".env.prod",
            ".env.local",
            ".env",
        ]

        if template.env_template_file:
            expected_files.append(template.env_template_file)

        for relative_path in expected_files:
            candidate = project.root / relative_path

            if relative_path == ".env":
                passed = candidate.is_symlink()
            else:
                passed = candidate.is_file()

            severity = (
                "error"
                if relative_path in {".env.dev", ".env.prod", ".env"}
                else "warning"
            )

            self._add_check(
                report,
                code="ENV001",
                category="environment",
                description=(
                    f"Fichier d’environnement `{relative_path}` présent"
                ),
                passed=passed,
                severity=severity,
                path=relative_path,
                message=(
                    f"Fichier d’environnement absent : `{relative_path}`."
                ),
            )

        env_path = project.root / ".env"
        env_target: str | None = None

        if env_path.is_symlink():
            try:
                env_target = str(env_path.readlink())
            except OSError:
                env_target = None

        valid_symlink = (
            env_path.is_symlink()
            and env_target in {".env.dev", ".env.prod"}
        )

        self._add_check(
            report,
            code="ENV002",
            category="environment",
            description=(
                "`.env` est un lien vers `.env.dev` ou `.env.prod`"
            ),
            passed=valid_symlink,
            path=".env",
            message=(
                "Le fichier `.env` doit être un lien symbolique "
                "vers `.env.dev` ou `.env.prod`."
            ),
            actual=env_target,
        )

    def _check_secrets_policy(
        self,
        project: Project,
        report: TemplateComplianceReport,
    ) -> None:
        gitignore = project.root / ".gitignore"

        try:
            content = gitignore.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except OSError:
            content = ""

        ignored = {
            line.strip()
            for line in content.splitlines()
            if line.strip()
            and not line.lstrip().startswith("#")
        }

        for required in (
            ".env",
            ".env.local",
        ):
            passed = required in ignored

            self._add_check(
                report,
                code="SEC001",
                category="security",
                description=f"`{required}` est ignoré par Git",
                passed=passed,
                path=".gitignore",
                message=(
                    f"`{required}` doit être présent dans `.gitignore`."
                ),
                expected=required,
            )

    @staticmethod
    def _add_check(
        report: TemplateComplianceReport,
        *,
        code: str,
        category: str,
        description: str,
        passed: bool,
        message: str,
        severity: str = "error",
        path: str | None = None,
        expected: str | None = None,
        actual: str | None = None,
    ) -> None:
        report.checks.append(
            ComplianceCheck(
                code=code,
                category=category,
                description=description,
                passed=passed,
                severity=severity,
            )
        )

        if passed:
            return

        report.findings.append(
            ComplianceFinding(
                code=code,
                severity=severity,
                category=category,
                message=message,
                path=path,
                expected=expected,
                actual=actual,
            )
        )
