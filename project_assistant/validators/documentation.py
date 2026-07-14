from __future__ import annotations

import re
import unicodedata

from project_assistant.config import ResolvedDocumentationConfig
from project_assistant.models import Document, Project


class DocumentationValidator:
    def validate(
        self,
        project: Project,
        config: ResolvedDocumentationConfig,
    ) -> Project:
        project.profile = config.profile
        project.documents.clear()

        required_set = set(config.required_documents)

        ordered_paths = (
            config.required_documents
            + config.optional_documents
        )

        for document_path in ordered_paths:
            definition = config.document_definitions.get(
                document_path,
                {},
            )

            absolute_path = project.root / document_path
            exists = absolute_path.is_file()

            document = Document(
                path=document_path,
                exists=exists,
                required=document_path in required_set,
                category=definition.get("category"),
                size_bytes=(
                    absolute_path.stat().st_size
                    if exists
                    else 0
                ),
            )

            project.documents.append(document)

            if document.required and not exists:
                project.add_finding(
                    code="DOC001",
                    message="Document obligatoire absent.",
                    severity="error",
                    path=document_path,
                    recommendation=f"Créer le document {document_path}.",
                )

            if exists and document.size_bytes == 0:
                project.add_finding(
                    code="DOC002",
                    message="Document vide.",
                    severity="warning",
                    path=document_path,
                    recommendation=(
                        "Ajouter le contenu minimal prévu "
                        "par le standard documentaire."
                    ),
                )

        self._validate_required_sections(
            project=project,
            config=config,
        )

        return project

    def _validate_required_sections(
        self,
        project: Project,
        config: ResolvedDocumentationConfig,
    ) -> None:
        for document in project.documents:
            if not document.exists:
                continue

            definition = config.document_definitions.get(
                document.path,
                {},
            )

            required_sections = [
                section
                for section in definition.get("sections", [])
                if section.get("required") is True
            ]

            if not required_sections:
                continue

            absolute_path = project.root / document.path

            try:
                content = absolute_path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except OSError:
                project.add_finding(
                    code="DOC003",
                    message="Impossible de lire le document.",
                    severity="warning",
                    path=document.path,
                )
                continue

            headings = self._extract_headings(content)

            for section in required_sections:
                canonical_title = str(
                    section.get("title", "")
                ).strip()

                candidates = [
                    canonical_title,
                    *section.get("aliases", []),
                ]

                found_title = self._find_matching_heading(
                    headings=headings,
                    candidates=candidates,
                )

                if found_title:
                    document.sections_found.append(canonical_title)
                else:
                    document.sections_missing.append(canonical_title)

            if document.sections_missing:
                project.add_finding(
                    code="DOC004",
                    message=(
                        "Sections obligatoires potentiellement absentes : "
                        + ", ".join(document.sections_missing)
                    ),
                    severity="warning",
                    path=document.path,
                    recommendation=(
                        "Vérifier ou ajouter les sections indiquées."
                    ),
                )

    @classmethod
    def _find_matching_heading(
        cls,
        headings: set[str],
        candidates: list[str],
    ) -> str | None:
        normalized_candidates = {
            cls._normalize_heading(candidate)
            for candidate in candidates
            if candidate
        }

        for heading in headings:
            if heading in normalized_candidates:
                return heading

        return None

    @classmethod
    def _extract_headings(cls, content: str) -> set[str]:
        headings: set[str] = set()

        for line in content.splitlines():
            stripped = line.strip()

            if not stripped.startswith("#"):
                continue

            title = stripped.lstrip("#").strip()

            if title:
                headings.add(cls._normalize_heading(title))

        return headings

    @staticmethod
    def _normalize_heading(value: str) -> str:
        value = unicodedata.normalize("NFKD", value)
        value = "".join(
            character
            for character in value
            if not unicodedata.combining(character)
        )

        value = value.casefold()

        value = re.sub(
            r"^\d+(?:\.\d+)*[.)]?\s*",
            "",
            value,
        )

        value = re.sub(r"[`*_:/\\-]+", " ", value)
        value = re.sub(r"\s+", " ", value)

        return value.strip()
