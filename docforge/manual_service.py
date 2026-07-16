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
from docforge.manual_prompt import ManualPromptBuilder
from docforge.profiles import ProfileDetector, ProjectProfile
from docforge.scanners import FileSystemScanner
from docforge.storage_paths import ensure_project_storage_migrated


@dataclass(frozen=True, slots=True)
class ManualPreparationMode:
    value: str

    def includes_full_prompt(self) -> bool:
        return self.value in {"full", "both"}

    def includes_sections(self) -> bool:
        return self.value in {"sections", "both"}


@dataclass(slots=True)
class ManualPreparationResult:
    root: Path
    output_dir: Path
    knowledge_file: Path
    manifest_file: Path
    full_prompt_file: Path | None = None
    section_prompt_files: list[Path] = field(
        default_factory=list
    )
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
            knowledge_builder
            or ProjectKnowledgeBuilder()
        )
        self.manual_knowledge_builder = (
            manual_knowledge_builder
        )
        self.blueprint = blueprint
        self.prompt_builder = prompt_builder

    def prepare(
        self,
        path: Path,
        *,
        clean: bool = False,
        mode: str = "both",
        output_dir: Path = Path(".docforge/manual"),
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

        resolved_output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        generated_directory = (
            resolved_output_dir / "generated"
        )
        generated_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

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
        manual_knowledge: ManualKnowledge = (
            manual_knowledge_builder.build(
                project_root=root,
                knowledge=project_knowledge,
                profile_instance=profile_instance,
            )
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

        knowledge_file = (
            resolved_output_dir / "manual-knowledge.json"
        )
        knowledge_file.write_text(
            manual_knowledge.to_json(),
            encoding="utf-8",
        )

        full_prompt_file: Path | None = None
        if preparation_mode.includes_full_prompt():
            full_prompt_file = (
                resolved_output_dir / "manual-prompt.md"
            )
            full_prompt_file.write_text(
                prompt_builder.build_full_prompt(
                    knowledge=manual_knowledge,
                    blueprint=active_blueprint,
                ),
                encoding="utf-8",
            )

        section_prompt_files: list[Path] = []
        if preparation_mode.includes_sections():
            section_root = (
                resolved_output_dir / "section-prompts"
            )
            section_root.mkdir(
                parents=True,
                exist_ok=True,
            )
            for index, section in enumerate(
                active_blueprint.sections,
                start=1,
            ):
                section_path = (
                    section_root
                    / f"{index:02d}-{section.identifier}.md"
                )
                section_projection = (
                    prompt_builder.project_section_facts(
                        manual_knowledge,
                        section,
                    )
                )
                section_path.write_text(
                    prompt_builder.build_section_prompt(
                        blueprint=active_blueprint,
                        section=section,
                        projected_facts=section_projection,
                    ),
                    encoding="utf-8",
                )
                section_prompt_files.append(section_path)

        manifest_file = (
            resolved_output_dir / "manual-manifest.json"
        )
        manifest_file.write_text(
            self._build_manifest(
                output_dir=resolved_output_dir,
                knowledge=manual_knowledge,
                blueprint=active_blueprint,
                knowledge_file=knowledge_file,
                full_prompt_file=full_prompt_file,
                section_prompt_files=section_prompt_files,
                generated_directory=generated_directory,
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
        section_prompt_files: list[Path],
        generated_directory: Path,
    ) -> str:
        expected_outputs = [
            "manual-knowledge.json",
            "manual-manifest.json",
            "generated/",
        ]

        if full_prompt_file is not None:
            expected_outputs.append("manual-prompt.md")

        if section_prompt_files:
            expected_outputs.extend(
                str(
                    path.relative_to(output_dir).as_posix()
                )
                for path in section_prompt_files
            )

        manifest = {
            "schema_version": 1,
            "project_name": knowledge.project.name,
            "profile_name": blueprint.profile_name,
            "generated_at": datetime.now(UTC)
            .replace(microsecond=0)
            .isoformat(),
            "knowledge_file": str(
                knowledge_file.relative_to(output_dir).as_posix()
            ),
            "full_prompt": (
                str(
                    full_prompt_file.relative_to(
                        output_dir
                    ).as_posix()
                )
                if full_prompt_file is not None
                else None
            ),
            "section_prompts": [
                str(
                    path.relative_to(output_dir).as_posix()
                )
                for path in section_prompt_files
            ],
            "expected_outputs": expected_outputs,
        }
        return (
            json.dumps(
                manifest,
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )
