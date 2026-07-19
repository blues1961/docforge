from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import UTC, datetime
from pathlib import Path

from docforge.detectors import TechnologyDetector
from docforge.knowledge import ProjectKnowledgeBuilder
from docforge.manual_blueprint import ManualBlueprint, ManualBlueprintRegistry
from docforge.manual_knowledge import ManualKnowledge
from docforge.manual_deterministic import ManualDeterministicContentBuilder
from docforge.validators.command_reference import CommandReferenceValidator
from docforge.validators.django_react_manual import DjangoReactMultiDocumentValidator
from docforge.manual_prompt import (
    ManualPromptBuilder,
    SectionPromptContext,
)
from docforge.profiles import ProjectProfile
from docforge.profiles import ProfileDetector
from docforge.scanners import FileSystemScanner
from docforge.storage_paths import ensure_project_storage_migrated


@dataclass(frozen=True, slots=True)
class ManualPreparationMode:
    value: str

    def includes_full_prompt(self) -> bool:
        return self.value in {"full", "both"}

    def includes_sections(self) -> bool:
        return self.value in {"sections", "both"}


@dataclass(frozen=True, slots=True)
class ManualSectionArtifact:
    identifier: str
    title: str
    prompt_file: Path
    context_file: Path
    estimated_tokens: int
    context_budget: int | None = None
    deterministic_file: Path | None = None


@dataclass(frozen=True, slots=True)
class ManualPreparedDocument:
    identifier: str
    title: str
    audience: str
    kind: str
    output_dir: Path
    blueprint: ManualBlueprint
    full_prompt_file: Path | None = None
    full_prompt_estimated_tokens: int | None = None
    section_prompt_files: list[Path] = field(default_factory=list)
    section_context_files: list[Path] = field(default_factory=list)
    section_artifacts: list[ManualSectionArtifact] = field(default_factory=list)


@dataclass(slots=True)
class ManualPreparationResult:
    root: Path
    output_dir: Path
    knowledge_file: Path
    manifest_file: Path
    full_prompt_file: Path | None = None
    section_prompt_files: list[Path] = field(default_factory=list)
    section_context_files: list[Path] = field(default_factory=list)
    section_artifacts: list[ManualSectionArtifact] = field(default_factory=list)
    generated_directory: Path | None = None
    documents: list[ManualPreparedDocument] = field(default_factory=list)


class ManualPreparationService:
    def __init__(
        self,
        *,
        knowledge_builder: ProjectKnowledgeBuilder | None = None,
        manual_knowledge_builder=None,
        blueprint: ManualBlueprint | None = None,
        prompt_builder: ManualPromptBuilder | None = None,
    ) -> None:
        self.knowledge_builder = (
            knowledge_builder or ProjectKnowledgeBuilder()
        )
        self.manual_knowledge_builder = manual_knowledge_builder
        self.blueprint = blueprint
        self.prompt_builder = prompt_builder

    def prepare(
        self,
        path: Path,
        *,
        clean: bool = False,
        mode: str = "both",
        output_dir: Path = Path(".docforge/manual"),
        context_budget: int | None = None,
    ) -> ManualPreparationResult:
        root = path.expanduser().resolve()
        ensure_project_storage_migrated(root)

        resolved_output_dir = (
            output_dir.expanduser().resolve()
            if output_dir.is_absolute()
            else root / output_dir
        )

        if clean and resolved_output_dir.exists():
            shutil.rmtree(resolved_output_dir)

        resolved_output_dir.mkdir(parents=True, exist_ok=True)

        generated_directory = resolved_output_dir / "generated"
        generated_directory.mkdir(parents=True, exist_ok=True)

        project = FileSystemScanner().scan(root)
        TechnologyDetector().detect(project)
        profile_instance = ProfileDetector().resolve(project)
        project_knowledge = self.knowledge_builder.build(
            project,
            profile_instance=profile_instance,
        )

        manual_knowledge_builder = (
            self.manual_knowledge_builder
            or profile_instance.build_manual_knowledge_builder()
        )
        manual_knowledge: ManualKnowledge = manual_knowledge_builder.build(
            project_root=root,
            knowledge=project_knowledge,
            profile_instance=profile_instance,
        )

        self._normalize_project_paths(manual_knowledge, root)

        prompt_builder = (
            self.prompt_builder
            or profile_instance.build_manual_prompt_builder()
        )
        preparation_mode = ManualPreparationMode(mode)

        if self.blueprint is not None:
            blueprints = (self.blueprint,)
        else:
            project_kind = None
            if isinstance(manual_knowledge.template, dict):
                template = manual_knowledge.template
                if (
                    template.get("project_kind") == "application"
                    and template.get("origin_template_id") == "app-template"
                    and str(template.get("manifest_source") or "").startswith("heuristic:")
                ):
                    project_kind = "application"
                elif template.get("project_kind") not in {None, "application"}:
                    project_kind = template.get("project_kind")
            blueprints = ManualBlueprintRegistry().blueprints_for_context(
                profile_instance.name,
                project_kind=project_kind,
            )

        knowledge_file = resolved_output_dir / "manual-knowledge.json"
        knowledge_file.write_text(
            manual_knowledge.to_json(),
            encoding="utf-8",
        )

        documents: list[ManualPreparedDocument] = []
        multiple_documents = len(blueprints) > 1
        if len(blueprints) == 3 and preparation_mode.includes_full_prompt():
            raise ValueError(
                "Les préparations multidocument django-react exigent le mode sections : "
                "les prompts complets dépassent le contexte local prévu."
            )
        documents_root = resolved_output_dir / "documents"
        if multiple_documents:
            documents_root.mkdir(parents=True, exist_ok=True)

        for blueprint in blueprints:
            document_output_dir = (
                documents_root / blueprint.document_identifier
                if multiple_documents
                else resolved_output_dir
            )
            if multiple_documents:
                document_output_dir.mkdir(parents=True, exist_ok=True)
            documents.append(
                self._prepare_document(
                    output_dir=document_output_dir,
                    knowledge=manual_knowledge,
                    blueprint=blueprint,
                    prompt_builder=prompt_builder,
                    preparation_mode=preparation_mode,
                    context_budget=context_budget,
                    legacy_root_layout=not multiple_documents,
                )
            )

        primary_document = documents[0]
        manifest_file = resolved_output_dir / "manual-manifest.json"
        manifest_text = self._build_manifest(
            output_dir=resolved_output_dir,
            knowledge=manual_knowledge,
            documents=documents,
            knowledge_file=knowledge_file,
            generated_directory=generated_directory,
            context_budget=context_budget,
        )
        manifest_file.write_text(manifest_text, encoding="utf-8")
        template = manual_knowledge.template if isinstance(manual_knowledge.template, dict) else {}
        if (
            profile_instance.name == "django-react"
            and template.get("detected") is True
            and template.get("project_kind") == "application"
            and template.get("origin_template_id") == "app-template"
            and str(template.get("manifest_source") or "").startswith("heuristic:")
        ):
            diagnostics = DjangoReactMultiDocumentValidator().validate(
                root=resolved_output_dir,
                manifest=json.loads(manifest_text),
            )
            if diagnostics:
                details = "; ".join(
                    f"{item.code}: {item.message}" for item in diagnostics
                )
                raise ValueError("Préparation multidocument django-react invalide : " + details)

        return ManualPreparationResult(
            root=root,
            output_dir=resolved_output_dir,
            knowledge_file=knowledge_file,
            manifest_file=manifest_file,
            full_prompt_file=(None if multiple_documents else primary_document.full_prompt_file),
            section_prompt_files=([] if multiple_documents else list(primary_document.section_prompt_files)),
            section_context_files=([] if multiple_documents else list(primary_document.section_context_files)),
            section_artifacts=([] if multiple_documents else list(primary_document.section_artifacts)),
            generated_directory=generated_directory,
            documents=documents,
        )

    @staticmethod
    def _normalize_project_paths(value: object, project_root: Path) -> object:
        """Replace project-local absolute paths before any manual artifact is written."""
        root_text = project_root.as_posix().rstrip("/")
        if isinstance(value, str):
            return value.replace(root_text + "/", "").replace(root_text, ".")
        if isinstance(value, list):
            for index, item in enumerate(value):
                value[index] = ManualPreparationService._normalize_project_paths(item, project_root)
            return value
        if isinstance(value, dict):
            for key, item in value.items():
                value[key] = ManualPreparationService._normalize_project_paths(item, project_root)
            return value
        if is_dataclass(value) and not isinstance(value, type):
            for item in fields(value):
                object.__setattr__(value, item.name, ManualPreparationService._normalize_project_paths(getattr(value, item.name), project_root))
        return value

    def _prepare_document(
        self,
        *,
        output_dir: Path,
        knowledge: ManualKnowledge,
        blueprint: ManualBlueprint,
        prompt_builder: ManualPromptBuilder,
        preparation_mode: ManualPreparationMode,
        context_budget: int | None,
        legacy_root_layout: bool,
    ) -> ManualPreparedDocument:
        active_sections = tuple(
            section
            for section in blueprint.sections
            if not prompt_builder.should_omit_section(
                knowledge,
                section,
            )
        )
        active_blueprint = ManualBlueprint(
            profile_name=blueprint.profile_name,
            sections=active_sections,
            document_identifier=blueprint.document_identifier,
            document_title=blueprint.document_title,
            document_audience=blueprint.document_audience,
            document_kind=blueprint.document_kind,
        )

        section_contexts = [
            prompt_builder.build_section_context(
                knowledge,
                section,
                context_budget=context_budget,
            )
            for section in active_blueprint.sections
        ]

        full_prompt_file: Path | None = None
        full_prompt_estimated_tokens: int | None = None
        if preparation_mode.includes_full_prompt():
            prompt_name = "manual-prompt.md" if legacy_root_layout else "prompt.md"
            full_prompt_file = output_dir / prompt_name
            full_prompt = prompt_builder.build_full_prompt(
                knowledge=knowledge,
                blueprint=active_blueprint,
                context_budget=context_budget,
            )
            full_prompt_file.write_text(full_prompt, encoding="utf-8")
            full_prompt_estimated_tokens = prompt_builder.estimate_tokens(
                full_prompt
            )

        section_prompt_files: list[Path] = []
        section_context_files: list[Path] = []
        section_artifacts: list[ManualSectionArtifact] = []
        deterministic_builder = ManualDeterministicContentBuilder()
        deterministic_root = output_dir / "deterministic-sections"
        if preparation_mode.includes_sections():
            section_root = output_dir / "section-prompts"
            section_context_root = output_dir / "section-contexts"
            section_root.mkdir(parents=True, exist_ok=True)
            section_context_root.mkdir(parents=True, exist_ok=True)
            deterministic_root.mkdir(parents=True, exist_ok=True)
            for index, (section, context) in enumerate(
                zip(active_blueprint.sections, section_contexts, strict=True),
                start=1,
            ):
                section_path = section_root / f"{index:02d}-{section.identifier}.md"
                context_path = section_context_root / f"{index:02d}-{section.identifier}.json"
                deterministic_path = deterministic_root / f"{index:02d}-{section.identifier}.md"
                deterministic_content = deterministic_builder.render_section(
                    knowledge,
                    section.identifier,
                )
                if section.identifier == "cli-reference":
                    diagnostics = CommandReferenceValidator().validate(
                        markdown=deterministic_content,
                        knowledge=knowledge,
                    )
                    if diagnostics:
                        details = "; ".join(
                            f"{item.code} ({item.command_path}): {item.message}"
                            for item in diagnostics
                        )
                        raise ValueError(
                            "Référence CLI déterministe invalide : " + details
                        )
                deterministic_path.write_text(
                    deterministic_content,
                    encoding="utf-8",
                )
                section_path.write_text(
                    prompt_builder.build_section_prompt(
                        blueprint=active_blueprint,
                        section=section,
                        projected_facts=context.projected_facts,
                        estimated_tokens=context.estimated_tokens,
                        context_budget=context.context_budget,
                    ),
                    encoding="utf-8",
                )
                context_path.write_text(
                    json.dumps(
                        {
                            "identifier": context.identifier,
                            "title": context.title,
                            "purpose": context.purpose,
                            "estimated_tokens": context.estimated_tokens,
                            "context_budget": context.context_budget,
                            "fact_breakdown": context.fact_breakdown,
                            "missing_fact_paths": context.missing_fact_paths,
                            "repeated_fact_paths": context.repeated_fact_paths,
                            "facts": context.projected_facts,
                        },
                        indent=2,
                        ensure_ascii=False,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                section_prompt_files.append(section_path)
                section_context_files.append(context_path)
                section_artifacts.append(
                    ManualSectionArtifact(
                        identifier=section.identifier,
                        title=section.title,
                        prompt_file=section_path,
                        context_file=context_path,
                        estimated_tokens=context.estimated_tokens,
                        context_budget=context.context_budget,
                        deterministic_file=deterministic_path,
                    )
                )

        return ManualPreparedDocument(
            identifier=active_blueprint.document_identifier,
            title=active_blueprint.document_title,
            audience=active_blueprint.document_audience,
            kind=active_blueprint.document_kind,
            output_dir=output_dir,
            blueprint=active_blueprint,
            full_prompt_file=full_prompt_file,
            full_prompt_estimated_tokens=full_prompt_estimated_tokens,
            section_prompt_files=section_prompt_files,
            section_context_files=section_context_files,
            section_artifacts=section_artifacts,
        )

    def _build_manifest(
        self,
        *,
        output_dir: Path,
        knowledge: ManualKnowledge,
        documents: list[ManualPreparedDocument],
        knowledge_file: Path,
        generated_directory: Path,
        context_budget: int | None,
    ) -> str:
        expected_outputs = [
            "manual-knowledge.json",
            "manual-manifest.json",
            "generated/",
        ]

        single_document = len(documents) == 1 and documents[0].output_dir == output_dir
        primary_document = documents[0]

        for document in documents:
            if document.full_prompt_file is not None:
                expected_outputs.append(
                    str(document.full_prompt_file.relative_to(output_dir).as_posix())
                )
            for artifact in document.section_artifacts:
                expected_outputs.extend(
                    (
                        str(artifact.prompt_file.relative_to(output_dir).as_posix()),
                        str(artifact.context_file.relative_to(output_dir).as_posix()),
                    )
                )
                if artifact.deterministic_file is not None:
                    expected_outputs.append(
                        str(artifact.deterministic_file.relative_to(output_dir).as_posix())
                    )


        manifest = {
            "schema_version": 4,
            "project_name": knowledge.project.name,
            "profile_name": knowledge.profile.get("name") if isinstance(knowledge.profile, dict) else primary_document.blueprint.profile_name,
            "project_kind": knowledge.template.get("project_kind") if isinstance(knowledge.template, dict) else None,
            "command_provenance_summary": self._build_command_provenance_summary(knowledge),
            "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
            "context_budget": context_budget,
            "recommended_generation_mode": "sections" if len(documents) > 1 else "full-or-sections",
            "full_prompts_supported": len(documents) == 1,
            "knowledge_file": str(knowledge_file.relative_to(output_dir).as_posix()),
            "full_prompt": (
                str(primary_document.full_prompt_file.relative_to(output_dir).as_posix())
                if single_document and primary_document.full_prompt_file is not None
                else None
            ),
            "full_prompt_estimated_tokens": (
                primary_document.full_prompt_estimated_tokens if single_document else None
            ),
            "section_prompts": (
                [
                    str(artifact.prompt_file.relative_to(output_dir).as_posix())
                    for artifact in primary_document.section_artifacts
                ]
                if single_document
                else []
            ),
            "section_contexts": (
                [
                    {
                        "identifier": artifact.identifier,
                        "title": artifact.title,
                        "prompt_file": str(artifact.prompt_file.relative_to(output_dir).as_posix()),
                        "context_file": str(artifact.context_file.relative_to(output_dir).as_posix()),
                        "deterministic_file": str(artifact.deterministic_file.relative_to(output_dir).as_posix()) if artifact.deterministic_file is not None else None,
                        "generation_mode": "deterministic" if artifact.identifier in ManualDeterministicContentBuilder.FULLY_DETERMINISTIC_SECTIONS else "ollama",
                        "estimated_tokens": artifact.estimated_tokens,
                        "context_budget": artifact.context_budget,
                    }
                    for artifact in primary_document.section_artifacts
                ]
                if single_document
                else []
            ),
            "documents": [
                {
                    "identifier": document.identifier,
                    "title": document.title,
                    "audience": document.audience,
                    "kind": document.kind,
                    "output_dir": str(document.output_dir.relative_to(output_dir).as_posix()),
                    "full_prompt": (
                        str(document.full_prompt_file.relative_to(output_dir).as_posix())
                        if document.full_prompt_file is not None
                        else None
                    ),
                    "full_prompt_estimated_tokens": document.full_prompt_estimated_tokens,
                    "section_prompts": [
                        str(artifact.prompt_file.relative_to(output_dir).as_posix())
                        for artifact in document.section_artifacts
                    ],
                    "section_contexts": [
                        {
                            "identifier": artifact.identifier,
                            "title": artifact.title,
                            "prompt_file": str(artifact.prompt_file.relative_to(output_dir).as_posix()),
                            "context_file": str(artifact.context_file.relative_to(output_dir).as_posix()),
                            "deterministic_file": str(artifact.deterministic_file.relative_to(output_dir).as_posix()) if artifact.deterministic_file is not None else None,
                            "generation_mode": "deterministic" if artifact.identifier in ManualDeterministicContentBuilder.FULLY_DETERMINISTIC_SECTIONS else "ollama",
                            "estimated_tokens": artifact.estimated_tokens,
                            "context_budget": artifact.context_budget,
                        }
                        for artifact in document.section_artifacts
                    ],
                }
                for document in documents
            ],
            "expected_outputs": expected_outputs,
            "generated_directory": str(generated_directory.relative_to(output_dir).as_posix()),
        }
        return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"

    def _build_command_provenance_summary(
        self,
        knowledge: ManualKnowledge,
    ) -> dict[str, object]:
        commands = []
        if isinstance(knowledge.operational_commands, dict):
            commands = knowledge.operational_commands.get("commands", [])
        totals: dict[str, int] = {}
        excluded_reasons: dict[str, int] = {}
        primary = 0
        advanced = 0
        excluded = 0
        for item in commands:
            provenance = item.get("provenance") or "unknown"
            totals[provenance] = totals.get(provenance, 0) + 1
            if item.get("documentation_policy") == "exclude" or item.get("reference_level") == "omit":
                excluded += 1
                reason = item.get("exclusion_reason") or "Aucune raison d’exclusion documentée."
                excluded_reasons[reason] = excluded_reasons.get(reason, 0) + 1
            elif item.get("reference_level") in {"advanced", "alias"}:
                advanced += 1
            else:
                primary += 1
        return {
            "total_detected": len(commands),
            "by_provenance": totals,
            "primary_documented": primary,
            "advanced_documented": advanced,
            "excluded": excluded,
            "top_exclusion_reasons": [
                {"reason": reason, "count": count}
                for reason, count in sorted(
                    excluded_reasons.items(),
                    key=lambda item: (-item[1], item[0]),
                )[:8]
            ],
        }
