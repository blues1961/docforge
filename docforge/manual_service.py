from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from docforge.detectors import TechnologyDetector
from docforge.knowledge import ProjectKnowledgeBuilder
from docforge.manual_blueprint import ManualBlueprint
from docforge.manual_knowledge import ManualKnowledge
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

        blueprint = (
            self.blueprint
            or profile_instance.build_manual_blueprint()
        )
        prompt_builder = (
            self.prompt_builder
            or profile_instance.build_manual_prompt_builder()
        )
        preparation_mode = ManualPreparationMode(mode)
        active_sections = tuple(
            section
            for section in blueprint.sections
            if not prompt_builder.should_omit_section(
                manual_knowledge,
                section,
            )
        )
        active_blueprint = ManualBlueprint(
            profile_name=blueprint.profile_name,
            sections=active_sections,
        )

        knowledge_file = resolved_output_dir / "manual-knowledge.json"
        knowledge_file.write_text(
            manual_knowledge.to_json(),
            encoding="utf-8",
        )

        section_contexts = [
            prompt_builder.build_section_context(
                manual_knowledge,
                section,
                context_budget=context_budget,
            )
            for section in active_blueprint.sections
        ]

        full_prompt_file: Path | None = None
        full_prompt_estimated_tokens: int | None = None
        if preparation_mode.includes_full_prompt():
            full_prompt_file = resolved_output_dir / "manual-prompt.md"
            full_prompt = prompt_builder.build_full_prompt(
                knowledge=manual_knowledge,
                blueprint=active_blueprint,
                context_budget=context_budget,
            )
            full_prompt_file.write_text(
                full_prompt,
                encoding="utf-8",
            )
            full_prompt_estimated_tokens = prompt_builder.estimate_tokens(
                full_prompt
            )

        section_prompt_files: list[Path] = []
        section_context_files: list[Path] = []
        section_artifacts: list[ManualSectionArtifact] = []
        if preparation_mode.includes_sections():
            section_root = resolved_output_dir / "section-prompts"
            section_context_root = resolved_output_dir / "section-contexts"
            section_root.mkdir(parents=True, exist_ok=True)
            section_context_root.mkdir(parents=True, exist_ok=True)
            for index, (section, context) in enumerate(
                zip(active_blueprint.sections, section_contexts, strict=True),
                start=1,
            ):
                section_path = (
                    section_root / f"{index:02d}-{section.identifier}.md"
                )
                context_path = (
                    section_context_root / f"{index:02d}-{section.identifier}.json"
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
                    )
                )

        manifest_file = resolved_output_dir / "manual-manifest.json"
        manifest_file.write_text(
            self._build_manifest(
                output_dir=resolved_output_dir,
                knowledge=manual_knowledge,
                blueprint=active_blueprint,
                knowledge_file=knowledge_file,
                full_prompt_file=full_prompt_file,
                full_prompt_estimated_tokens=full_prompt_estimated_tokens,
                section_artifacts=section_artifacts,
                generated_directory=generated_directory,
                context_budget=context_budget,
            ),
            encoding="utf-8",
        )

        return ManualPreparationResult(
            root=root,
            output_dir=resolved_output_dir,
            knowledge_file=knowledge_file,
            manifest_file=manifest_file,
            full_prompt_file=full_prompt_file,
            section_prompt_files=section_prompt_files,
            section_context_files=section_context_files,
            section_artifacts=section_artifacts,
            generated_directory=generated_directory,
        )

    def _build_manifest(
        self,
        *,
        output_dir: Path,
        knowledge: ManualKnowledge,
        blueprint: ManualBlueprint,
        knowledge_file: Path,
        full_prompt_file: Path | None,
        full_prompt_estimated_tokens: int | None,
        section_artifacts: list[ManualSectionArtifact],
        generated_directory: Path,
        context_budget: int | None,
    ) -> str:
        expected_outputs = [
            "manual-knowledge.json",
            "manual-manifest.json",
            "generated/",
        ]

        if full_prompt_file is not None:
            expected_outputs.append("manual-prompt.md")

        if section_artifacts:
            expected_outputs.extend(
                str(
                    artifact.prompt_file.relative_to(output_dir).as_posix()
                )
                for artifact in section_artifacts
            )
            expected_outputs.extend(
                str(
                    artifact.context_file.relative_to(output_dir).as_posix()
                )
                for artifact in section_artifacts
            )

        manifest = {
            "schema_version": 2,
            "project_name": knowledge.project.name,
            "profile_name": blueprint.profile_name,
            "command_provenance_summary": self._build_command_provenance_summary(knowledge),
            "generated_at": datetime.now(UTC)
            .replace(microsecond=0)
            .isoformat(),
            "context_budget": context_budget,
            "knowledge_file": str(
                knowledge_file.relative_to(output_dir).as_posix()
            ),
            "full_prompt": (
                str(
                    full_prompt_file.relative_to(output_dir).as_posix()
                )
                if full_prompt_file is not None
                else None
            ),
            "full_prompt_estimated_tokens": full_prompt_estimated_tokens,
            "section_prompts": [
                str(
                    artifact.prompt_file.relative_to(output_dir).as_posix()
                )
                for artifact in section_artifacts
            ],
            "section_contexts": [
                {
                    "identifier": artifact.identifier,
                    "title": artifact.title,
                    "prompt_file": str(
                        artifact.prompt_file.relative_to(output_dir).as_posix()
                    ),
                    "context_file": str(
                        artifact.context_file.relative_to(output_dir).as_posix()
                    ),
                    "estimated_tokens": artifact.estimated_tokens,
                    "context_budget": artifact.context_budget,
                }
                for artifact in section_artifacts
            ],
            "expected_outputs": expected_outputs,
            "generated_directory": str(
                generated_directory.relative_to(output_dir).as_posix()
            ),
        }
        return (
            json.dumps(
                manifest,
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )


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
