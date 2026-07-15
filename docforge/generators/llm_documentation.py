from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from docforge.llm import (
    OllamaClient,
    OllamaResult,
    ProjectContextBuilder,
)
from docforge.models import Project


SYSTEM_PROMPT = """
Tu es un rédacteur de documentation technique factuelle.

Tu ne réalises jamais :
- de revue de code;
- d'audit de sécurité;
- d'évaluation qualitative;
- de recommandations générales;
- de comparaison avec d'autres technologies.

Tu décris uniquement l'état réel du projet à partir du contexte fourni.

Contraintes absolues :
- aucune formule de félicitation;
- aucune introduction générale;
- aucune invention;
- aucun conseil non demandé;
- aucune information provenant de tes connaissances générales;
- lorsqu'un fait n'est pas établi, écrire exactement « À vérifier »;
- répondre uniquement avec le contenu demandé.
""".strip()


@dataclass(slots=True)
class GeneratedSection:
    title: str
    content: str
    result: OllamaResult


@dataclass(slots=True)
class GeneratedMarkdownDocument:
    content: str
    sections: list[GeneratedSection]

    @property
    def average_tokens_per_second(self) -> float:
        rates = [
            section.result.tokens_per_second
            for section in self.sections
            if section.result.tokens_per_second > 0
        ]

        if not rates:
            return 0.0

        return sum(rates) / len(rates)


class LLMDocumentationGenerator:
    def __init__(
        self,
        client: OllamaClient | None = None,
    ) -> None:
        self.client = client or OllamaClient()

    def generate_document(
        self,
        *,
        project: Project,
        document_path: str,
        skeleton_path: Path,
        model: str,
    ) -> GeneratedMarkdownDocument:
        skeleton = skeleton_path.read_text(
            encoding="utf-8",
        )

        document_title = self._extract_document_title(skeleton)
        section_titles = self._extract_section_titles(skeleton)

        context = ProjectContextBuilder().build_for_document(
            project=project,
            document_path=document_path,
        )

        generated_sections: list[GeneratedSection] = []

        for section_title in section_titles:
            prompt = self._build_section_prompt(
                project=project,
                document_path=document_path,
                section_title=section_title,
                all_section_titles=section_titles,
                context=context,
            )

            result = self.client.chat(
                model=model,
                system=SYSTEM_PROMPT,
                prompt=prompt,
                num_ctx=8192,
                temperature=0.0,
                num_predict=700,
            )

            content = self._clean_section_content(
                result.response,
                section_title,
            )

            generated_sections.append(
                GeneratedSection(
                    title=section_title,
                    content=content,
                    result=result,
                )
            )

        document = self._assemble_document(
            document_title=document_title,
            document_path=document_path,
            sections=generated_sections,
        )

        return GeneratedMarkdownDocument(
            content=document,
            sections=generated_sections,
        )

    @staticmethod
    def _build_section_prompt(
        *,
        project: Project,
        document_path: str,
        section_title: str,
        all_section_titles: list[str],
        context: str,
    ) -> str:
        return f"""
PROJET
{project.name}

DOCUMENT CIBLE
{document_path}

SECTION UNIQUE À RÉDIGER
{section_title}

SECTIONS DU DOCUMENT
{", ".join(all_section_titles)}

FORMAT ATTENDU
- deux à six paragraphes courts ou une liste concrète;
- commandes exactes seulement lorsqu'elles figurent dans le contexte;
- aucun titre Markdown;
- aucune conclusion;
- aucune recommandation;
- aucune analyse de risque.

CONTEXTE AUTORISÉ
{context}
""".strip()

    @staticmethod
    def _extract_document_title(skeleton: str) -> str:
        for line in skeleton.splitlines():
            if line.startswith("# "):
                return line[2:].strip()

        return "Documentation"

    @staticmethod
    def _extract_section_titles(skeleton: str) -> list[str]:
        titles = [
            line[3:].strip()
            for line in skeleton.splitlines()
            if line.startswith("## ") and line[3:].strip()
        ]

        if not titles:
            raise ValueError(
                "Le squelette ne contient aucune section de niveau 2."
            )

        return titles

    @staticmethod
    def _clean_section_content(
        content: str,
        expected_title: str,
    ) -> str:
        content = content.strip()
        lines = content.splitlines()

        while lines and not lines[0].strip():
            lines.pop(0)

        if lines and lines[0].lstrip().startswith("#"):
            heading = re.sub(
                r"^#+\s*",
                "",
                lines[0].strip(),
            ).casefold()

            if heading == expected_title.casefold():
                lines.pop(0)

        cleaned = "\n".join(lines).strip()

        forbidden_starts = (
            "ceci est",
            "excellent",
            "voici une analyse",
            "ce document présente une revue",
            "l'architecture globale est",
        )

        if cleaned.casefold().startswith(forbidden_starts):
            return (
                "À vérifier — la génération n'a pas respecté "
                "le format documentaire demandé."
            )

        return cleaned or "À vérifier."

    @staticmethod
    def _assemble_document(
        *,
        document_title: str,
        document_path: str,
        sections: list[GeneratedSection],
    ) -> str:
        lines = [
            f"# {document_title}",
            "",
            "<!--",
            "Document généré en aperçu par docforge.",
            f"Document cible : {document_path}",
            "Le contenu doit être validé avant son intégration.",
            "-->",
            "",
        ]

        for section in sections:
            lines.extend(
                [
                    f"## {section.title}",
                    "",
                    section.content,
                    "",
                ]
            )

        return "\n".join(lines).rstrip() + "\n"
