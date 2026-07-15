from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from docforge.analyzer_registry import (
    AnalysisContext,
)
from docforge.analyzers import (
    ApiFacts,
    ArchitectureFacts,
    CliFacts,
    ConfigurationFacts,
    DeploymentFacts,
    PyprojectFacts,
    ReadmeFacts,
    SecurityFacts,
    SpecificationFacts,
)
from docforge.detectors import TechnologyDetector
from docforge.models import Project
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
    SCHEMA_VERSION = 1

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

        analyzer_context = AnalysisContext(
            project=project,
            profile_name=profile.name,
            protected_documents=(
                profile.document_policy.protected_documents
            ),
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
            findings=findings,
        )

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
