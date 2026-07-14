from pathlib import Path

from project_assistant.analyzers import DeploymentFacts
from project_assistant.generators import DeploymentDocumentGenerator
from project_assistant.models import Project


def test_deployment_generator_uses_only_structured_facts() -> None:
    project = Project(
        name="demo",
        root=Path("/tmp/demo"),
    )
    project.environment.active_environment = "dev"
    project.environment.env_symlink_target = ".env.dev"

    facts = DeploymentFacts(
        compose_files=[
            "docker-compose.dev.yml",
            "docker-compose.prod.yml",
        ],
        services=["backend", "db", "frontend"],
        external_networks=["edge"],
        named_volumes=["pgdata"],
        required_env_files=[
            ".env.dev",
            ".env.local",
            ".env.prod",
        ],
        make_targets=[
            "prod",
            "up",
            "migrate",
            "check",
            "ps",
            "restore-db",
            "test",
        ],
        traefik_enabled=True,
        prerequisites=[
            "Docker doit être installé.",
        ],
        migrations=["make migrate"],
        validation_commands=[
            "make check",
            "make ps",
        ],
    )

    content = DeploymentDocumentGenerator().generate(
        project,
        facts,
    )

    assert "# Déploiement — demo" in content
    assert "make migrate" in content
    assert "make restore" in content
    assert "`edge`" in content
    assert "revue de sécurité" not in content.casefold()
