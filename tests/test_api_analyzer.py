from pathlib import Path

from project_assistant.analyzers import ApiAnalyzer
from project_assistant.scanners import FileSystemScanner


def test_api_analyzer_discovers_paths_and_router_registrations(
    tmp_path: Path,
) -> None:
    api = tmp_path / "api"
    api.mkdir()

    (api / "urls.py").write_text(
        """
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, HealthView

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = [
    path("healthz/", HealthView.as_view(), name="health"),
]
""",
        encoding="utf-8",
    )

    (api / "views.py").write_text(
        """
class CategoryViewSet:
    def list(self, request):
        pass

    def create(self, request):
        pass

    def retrieve(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass


class HealthView:
    def get(self, request):
        pass
""",
        encoding="utf-8",
    )

    project = FileSystemScanner().scan(tmp_path)
    facts = ApiAnalyzer().analyze(project)

    assert facts.route_files == ["api/urls.py"]

    health = next(
        route
        for route in facts.routes
        if route.path == "/healthz/"
    )

    assert health.methods == ["GET"]
    assert health.name == "health"

    categories = next(
        route
        for route in facts.routes
        if route.path == "/categories/"
    )

    assert categories.methods == ["GET", "POST"]

    category_detail = next(
        route
        for route in facts.routes
        if route.path == "/categories/{id}/"
    )

    assert category_detail.methods == [
        "GET",
        "PATCH",
        "DELETE",
    ]
