from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from project_assistant.config import ResolvedDocumentationConfig
from project_assistant.models import Project


PREVIEW_DIRECTORY = Path(".project-assistant/preview")


@dataclass(slots=True)
class GeneratedDocument:
    source_path: str
    preview_path: Path
    reason: str


class DocumentationPreviewGenerator:
    def generate(
        self,
        project: Project,
        config: ResolvedDocumentationConfig,
        *,
        clean: bool = False,
    ) -> list[GeneratedDocument]:
        preview_root = project.root / PREVIEW_DIRECTORY

        if clean and preview_root.exists():
            shutil.rmtree(preview_root)

        preview_root.mkdir(parents=True, exist_ok=True)

        generated: list[GeneratedDocument] = []

        for document_path in config.required_documents:
            source_path = project.root / document_path

            # Pour le moment, on ne propose que les documents absents.
            if source_path.exists():
                continue

            definition = config.document_definitions.get(
                document_path,
                {},
            )

            preview_path = self._safe_preview_path(
                preview_root=preview_root,
                document_path=document_path,
            )

            preview_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            content = self._build_skeleton(
                project=project,
                document_path=document_path,
                definition=definition,
            )

            preview_path.write_text(
                content,
                encoding="utf-8",
            )

            generated.append(
                GeneratedDocument(
                    source_path=document_path,
                    preview_path=preview_path,
                    reason="document obligatoire absent",
                )
            )

        return generated

    @staticmethod
    def _safe_preview_path(
        preview_root: Path,
        document_path: str,
    ) -> Path:
        candidate = (
            preview_root / document_path
        ).resolve()

        resolved_root = preview_root.resolve()

        if candidate != resolved_root and resolved_root not in candidate.parents:
            raise ValueError(
                f"Chemin documentaire non sécuritaire : {document_path}"
            )

        return candidate

    @staticmethod
    def _build_skeleton(
        project: Project,
        document_path: str,
        definition: dict,
    ) -> str:
        title = DocumentationPreviewGenerator._document_title(
            project=project,
            document_path=document_path,
        )

        description = str(
            definition.get("description", "")
        ).strip()

        lines = [
            f"# {title}",
            "",
        ]

        if description:
            lines.extend(
                [
                    f"> {description}",
                    "",
                ]
            )

        lines.extend(
            [
                "<!--",
                "Document généré en aperçu par project-assistant.",
                "Le contenu doit être validé avant son intégration.",
                "-->",
                "",
            ]
        )

        sections = definition.get("sections", [])

        for section in sections:
            section_title = str(
                section.get("title", "")
            ).strip()

            if not section_title:
                continue

            lines.extend(
                [
                    f"## {section_title}",
                    "",
                    (
                        "_Contenu à générer à partir de l’analyse "
                        "du projet._"
                    ),
                    "",
                ]
            )

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _document_title(
        project: Project,
        document_path: str,
    ) -> str:
        known_titles = {
            "README.md": project.name,
            "README_DEV.md": f"{project.name} — Développement",
            "CODEX_START.md": "CODEX_START",
            "AGENTS.md": "AGENTS",
            "INVARIANTS.md": "INVARIANTS",
            "docs/architecture.md": (
                f"Architecture — {project.name}"
            ),
            "docs/specification.md": (
                f"Spécification — {project.name}"
            ),
            "docs/api.md": f"API — {project.name}",
            "docs/deployment.md": (
                f"Déploiement — {project.name}"
            ),
            "docs/troubleshooting.md": (
                f"Dépannage — {project.name}"
            ),
        }

        return known_titles.get(
            document_path,
            Path(document_path).stem.replace("-", " ").title(),
        )
