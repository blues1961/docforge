from pathlib import Path

from project_assistant.models import Project, Technology


def test_project_can_register_languages_and_frameworks() -> None:
    project = Project(name="demo", root=Path("/tmp/demo"))

    project.add_language("Python")
    project.add_language("Python")
    project.add_framework("Django")
    project.add_framework("Django")

    assert project.languages == ["Python"]
    assert project.frameworks == ["Django"]


def test_project_can_register_technology() -> None:
    project = Project(name="demo", root=Path("/tmp/demo"))

    project.add_technology(
        Technology(
            name="PostgreSQL",
            category="database",
            evidence=["docker-compose.yml"],
        )
    )
    project.add_technology(
        Technology(
            name="PostgreSQL",
            category="database",
            evidence=["requirements.txt"],
        )
    )

    assert len(project.technologies) == 1
    assert project.technologies[0].name == "PostgreSQL"


def test_project_can_be_serialized() -> None:
    project = Project(name="demo", root=Path("/tmp/demo"))
    project.add_language("Python")
    project.add_finding(
        code="DOC001",
        message="README.md absent",
        severity="warning",
        path="README.md",
    )

    data = project.to_dict()

    assert data["name"] == "demo"
    assert data["root"] == "/tmp/demo"
    assert data["languages"] == ["Python"]
    assert data["findings"][0]["code"] == "DOC001"
