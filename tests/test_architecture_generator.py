from pathlib import Path

from project_assistant.analyzers import (
    ArchitectureFacts,
    ArchitectureService,
)
from project_assistant.generators import (
    ArchitectureDocumentGenerator,
)
from project_assistant.models import Project


def test_architecture_generator_uses_structured_facts() -> None:
    project = Project(
        name="demo",
        root=Path("/tmp/demo"),
    )

    facts = ArchitectureFacts(
        languages=["JavaScript", "Python"],
        frameworks=["Django", "React", "Vite"],
        technologies=[
            "Docker Compose",
            "PostgreSQL",
            "Traefik",
        ],
        compose_files=[
            "docker-compose.dev.yml",
            "docker-compose.prod.yml",
        ],
        services=[
            ArchitectureService(
                name="backend",
                environments=["dev", "prod"],
                build_contexts=["./backend"],
                depends_on=["db"],
                networks=["appnet", "edge"],
                traefik_routes=[
                    "Host(`api.example.com`)"
                ],
                healthcheck=True,
            ),
            ArchitectureService(
                name="db",
                environments=["dev", "prod"],
                image="postgres:16-alpine",
                volumes=[
                    "pgdata:/var/lib/postgresql/data"
                ],
            ),
            ArchitectureService(
                name="frontend",
                environments=["dev", "prod"],
                build_contexts=["./frontend"],
                depends_on=["backend"],
            ),
        ],
        networks=["appnet", "edge"],
        external_networks=["edge"],
        volumes=["pgdata"],
        frontend_services=["frontend"],
        backend_services=["backend"],
        database_services=["db"],
        uses_traefik=True,
        uses_postgresql=True,
        environment_files=[
            ".env.dev",
            ".env.local",
            ".env.prod",
        ],
    )

    content = ArchitectureDocumentGenerator().generate(
        project,
        facts,
    )

    assert "# Architecture — demo" in content
    assert "## Composants" in content
    assert "`backend`" in content
    assert "Host(`api.example.com`)" in content
    assert "`edge`" in content
    assert "PostgreSQL" in content
