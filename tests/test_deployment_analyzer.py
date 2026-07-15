from pathlib import Path

from docforge.analyzers import DeploymentAnalyzer
from docforge.models import Project


def test_deployment_analyzer_skips_compose_prerequisite_without_compose_files() -> None:
    project = Project(
        name="demo",
        root=Path("/tmp/demo"),
    )

    facts = DeploymentAnalyzer().analyze(project)

    assert facts.compose_files == []
    assert all(
        "Docker Compose" not in prerequisite
        for prerequisite in facts.prerequisites
    )
