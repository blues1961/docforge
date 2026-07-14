from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from project_assistant.commands.document import (
    PreviewDocumentResult,
    generate_documentation_preview,
)
from project_assistant.project_registry import (
    ProjectRegistry,
    RegisteredProject,
)


@dataclass(slots=True)
class ProjectRefreshResult:
    project: RegisteredProject
    generated: list[PreviewDocumentResult] = field(
        default_factory=list
    )
    error: str | None = None


class ProjectManager:
    def __init__(
        self,
        registry: ProjectRegistry | None = None,
    ) -> None:
        self.registry = registry or ProjectRegistry()

    def refresh_all(
        self,
        *,
        clean: bool = False,
    ) -> list[ProjectRefreshResult]:
        results: list[ProjectRefreshResult] = []

        for registered in self.registry.load():
            if not registered.enabled:
                continue

            try:
                _, _, generated = (
                    generate_documentation_preview(
                        path=registered.path,
                        profile=registered.profile,
                        clean=clean,
                        refresh=True,
                    )
                )

                results.append(
                    ProjectRefreshResult(
                        project=registered,
                        generated=generated,
                    )
                )
            except Exception as error:
                results.append(
                    ProjectRefreshResult(
                        project=registered,
                        error=str(error),
                    )
                )

        return results
