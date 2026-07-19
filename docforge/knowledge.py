from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any

from docforge.analyzer_registry import AnalysisContext
from docforge.analyzers import (
    ApiFacts,
    ApplicationOverviewFacts,
    ArchitectureFacts,
    CapabilitiesFacts,
    CliFacts,
    ConfigurationFacts,
    DeploymentFacts,
    DjangoFacts,
    DjangoReactApplicationFacts,
    EnvironmentVariablesFacts,
    OperationalCommandsFacts,
    ProjectEnvironmentsFacts,
    ProjectTemplateFacts,
    PyprojectFacts,
    ReactFacts,
    ReadmeFacts,
    SecurityFacts,
    ServiceEndpointsFacts,
    SpecificationFacts,
)
from docforge.detectors import TechnologyDetector
from docforge.models import Finding, Project
from docforge.profiles import (
    ProfileDetector,
    ProfileFacts,
    ProjectProfile,
)
from docforge.scanners import FileSystemScanner


@dataclass(slots=True)
class ProjectIdentity:
    name: str
    root: str
    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ProjectKnowledge:
    schema_version: int
    identity: ProjectIdentity
    profile: ProfileFacts

    architecture: ArchitectureFacts
    deployment: DeploymentFacts
    pyproject: PyprojectFacts
    cli: CliFacts
    configuration: ConfigurationFacts
    security: SecurityFacts
    api: ApiFacts
    specification: SpecificationFacts
    readme: ReadmeFacts

    application: ApplicationOverviewFacts = field(
        default_factory=ApplicationOverviewFacts
    )
    environments: ProjectEnvironmentsFacts = field(
        default_factory=ProjectEnvironmentsFacts
    )
    operational_commands: OperationalCommandsFacts = field(
        default_factory=OperationalCommandsFacts
    )
    environment_variables: EnvironmentVariablesFacts = field(
        default_factory=EnvironmentVariablesFacts
    )
    service_endpoints: ServiceEndpointsFacts = field(
        default_factory=ServiceEndpointsFacts
    )
    django: DjangoFacts = field(default_factory=DjangoFacts)
    react: ReactFacts = field(default_factory=ReactFacts)
    capabilities: CapabilitiesFacts = field(
        default_factory=CapabilitiesFacts
    )
    template: ProjectTemplateFacts = field(
        default_factory=ProjectTemplateFacts
    )

    findings: list[dict[str, Any]] = field(
        default_factory=list
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return (
            json.dumps(
                self.to_dict(),
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )


class ProjectKnowledgeBuilder:
    SCHEMA_VERSION = 2
    SUPPRESSED_PYTHON_CLI_FINDINGS = {
        "ENV002",
        "ENV003",
        "ENV004",
    }

    def build_from_path(
        self,
        root: Path,
    ) -> ProjectKnowledge:
        project = FileSystemScanner().scan(
            root.expanduser().resolve()
        )
        TechnologyDetector().detect(project)

        return self.build(project)

    def build(
        self,
        project: Project,
        *,
        profile_instance: ProjectProfile | None = None,
    ) -> ProjectKnowledge:
        profile_instance = (
            profile_instance
            or ProfileDetector().resolve(project)
        )
        profile = profile_instance.analyze(project)
        project.findings = self._filtered_findings(
            project.findings,
            profile.name,
        )

        protected_documents = set(profile.document_policy.protected_documents)
        if (project.root / "INVARIANTS.md").is_file():
            protected_documents.add("INVARIANTS.md")
        analyzer_context = AnalysisContext(
            project=project,
            profile_name=profile.name,
            protected_documents=tuple(sorted(protected_documents)),
        )
        analyzer_results = (
            profile_instance.build_analyzer_registry()
            .analyze_all(analyzer_context)
        )

        architecture = analyzer_results["architecture"]
        deployment = analyzer_results["deployment"]
        pyproject = analyzer_results["pyproject"]
        configuration = analyzer_results["configuration"]
        api = analyzer_results["api"]
        specification = analyzer_results["specification"]
        readme = analyzer_results["readme"]
        security = analyzer_results["security"]

        cli = analyzer_results.get("cli")
        if cli is None:
            cli = CliFacts()

        application_result = analyzer_results.get(
            "application"
        )
        if application_result is None:
            application_result = DjangoReactApplicationFacts()

        profile = self._apply_template_contract_policy(
            profile,
            application_result.template,
        )

        technologies = sorted(
            technology.name
            for technology in project.technologies
        )

        findings = [
            self._finding_to_dict(finding)
            for finding in project.findings
        ]

        return ProjectKnowledge(
            schema_version=self.SCHEMA_VERSION,
            identity=ProjectIdentity(
                name=project.name,
                root=str(project.root),
                languages=sorted(project.languages),
                frameworks=sorted(project.frameworks),
                technologies=technologies,
            ),
            profile=profile,
            architecture=architecture,
            deployment=deployment,
            pyproject=pyproject,
            cli=cli,
            configuration=configuration,
            security=security,
            api=api,
            specification=specification,
            readme=readme,
            application=application_result.application,
            environments=application_result.environments,
            operational_commands=(
                application_result.operational_commands
            ),
            environment_variables=(
                application_result.environment_variables
            ),
            service_endpoints=(
                application_result.service_endpoints
            ),
            django=application_result.django,
            react=application_result.react,
            capabilities=application_result.capabilities,
            template=application_result.template,
            findings=findings,
        )

    @staticmethod
    def _apply_template_contract_policy(
        profile: ProfileFacts,
        template: ProjectTemplateFacts,
    ) -> ProfileFacts:
        """Apply app-template obligations only after contract detection."""
        if not (
            profile.name == "django-react"
            and template.detected
            and template.project_kind == "application"
            and template.base_profile == "django-react"
        ):
            return profile

        policy = profile.document_policy
        required = tuple(sorted({*policy.required_documents, "INVARIANTS.md"}))
        deterministic = tuple(
            sorted({*policy.deterministic_documents, "INVARIANTS.md"})
        )
        protected = tuple(
            sorted({*policy.protected_documents, "INVARIANTS.md"})
        )
        return replace(
            profile,
            document_policy=replace(
                policy,
                required_documents=required,
                deterministic_documents=deterministic,
                protected_documents=protected,
            ),
        )

    def _filtered_findings(
        self,
        findings: list[Finding],
        profile_name: str,
    ) -> list[Finding]:
        if profile_name != "python-cli":
            return list(findings)

        return [
            finding
            for finding in findings
            if (
                finding.code
                not in self.SUPPRESSED_PYTHON_CLI_FINDINGS
            )
        ]

    @staticmethod
    def _finding_to_dict(
        finding: object,
    ) -> dict[str, Any]:
        if hasattr(finding, "__dict__"):
            return dict(vars(finding))

        result: dict[str, Any] = {}

        for attribute in (
            "code",
            "severity",
            "message",
            "path",
        ):
            if hasattr(finding, attribute):
                result[attribute] = getattr(
                    finding,
                    attribute,
                )

        return result


def write_project_knowledge(
    knowledge: ProjectKnowledge,
    output_path: Path,
) -> Path:
    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output_path.write_text(
        knowledge.to_json(),
        encoding="utf-8",
    )

    return output_path
