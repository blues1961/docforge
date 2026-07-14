from pathlib import Path

from project_assistant.analyzers import (
    ApiFacts,
    ApiRoute,
)
from project_assistant.generators import (
    ApiDocumentGenerator,
)
from project_assistant.models import Project


def test_api_generator_creates_endpoint_table() -> None:
    project = Project(
        name="demo",
        root=Path("/tmp/demo"),
    )

    facts = ApiFacts(
        route_files=["backend/api/urls.py"],
        routes=[
            ApiRoute(
                path="/api/categories/",
                source="backend/api/urls.py",
                name="category-list",
                view="CategoryViewSet",
                kind="router-list",
                methods=["GET", "POST"],
            )
        ],
    )

    content = ApiDocumentGenerator().generate(
        project,
        facts,
    )

    assert "# API — demo" in content
    assert "`GET`" in content
    assert "`POST`" in content
    assert "`/api/categories/`" in content
    assert "`CategoryViewSet`" in content
