from __future__ import annotations

from dataclasses import dataclass

from docforge.manual_deterministic import ManualDeterministicContentBuilder
from docforge.manual_knowledge import ManualKnowledge


@dataclass(frozen=True, slots=True)
class CommandReferenceDiagnostic:
    code: str
    command_path: str
    message: str


class CommandReferenceValidator:
    """Validate the deterministic, user-facing CLI reference contract."""

    def validate(
        self,
        *,
        markdown: str,
        knowledge: ManualKnowledge,
        expected_command_count: int | None = None,
    ) -> list[CommandReferenceDiagnostic]:
        diagnostics: list[CommandReferenceDiagnostic] = []
        builder = ManualDeterministicContentBuilder()
        commands = [
            command for command in knowledge.commands
            if command.visibility == "public"
            and command.documentation_policy != "exclude"
            and command.reference_level != "omit"
        ]
        summaries: dict[str, str] = {}
        for command in commands:
            section = self._command_section(markdown, command.command_path)
            description = command.description
            if description is None or not description.summary.strip():
                diagnostics.append(self._issue("CLIREF001", command.command_path, "Résumé absent."))
                continue
            prior = summaries.get(description.summary)
            if prior is not None and description.summary != "Description non résolue.":
                diagnostics.append(self._issue("CLIREF002", command.command_path, f"Résumé générique identique à `{prior}`."))
            else:
                summaries.setdefault(description.summary, command.command_path)
            if description.summary not in section:
                diagnostics.append(self._issue("CLIREF003", command.command_path, "Résumé structuré absent du rendu."))
            syntax = builder._syntax(command)
            if syntax not in section:
                diagnostics.append(self._issue("CLIREF004", command.command_path, "Syntaxe canonique absente du rendu."))
            if " / " in syntax:
                diagnostics.append(self._issue("CLIREF005", command.command_path, "La syntaxe canonique mélange des alias."))
            for parameter in command.parameters:
                if parameter.kind not in {"argument", "option"}:
                    continue
                token = builder._parameter_token(parameter)
                if token not in section or (parameter.help and parameter.help not in section):
                    diagnostics.append(self._issue("CLIREF006", command.command_path, f"Paramètre insuffisamment décrit : `{parameter.name}`."))
                if parameter.kind == "option":
                    aliases = [flag for flag in parameter.flags if flag != token.split()[0]]
                    for alias in aliases:
                        if f"Alias : `{alias}`" not in section:
                            diagnostics.append(self._issue("CLIREF007", command.command_path, f"Alias séparé absent : `{alias}`."))
            for fact_name in ("behavior", "outputs", "side_effects", "next_step"):
                value = getattr(description, fact_name)
                has_value = bool(value)
                provenance = description.provenance.get(fact_name)
                if has_value and provenance is None:
                    diagnostics.append(self._issue("CLIREF008", command.command_path, f"Fait `{fact_name}` sans provenance."))
        if expected_command_count is not None and len(commands) != expected_command_count:
            diagnostics.append(self._issue("CLIREF009", "<reference>", f"Référence CLI incomplète : {len(commands)}/{expected_command_count} commandes."))
        return diagnostics

    @staticmethod
    def _command_section(markdown: str, command_path: str) -> str:
        marker = f"#### `{command_path}`"
        start = markdown.find(marker)
        if start < 0:
            return ""
        next_start = markdown.find("\n#### `", start + len(marker))
        return markdown[start:] if next_start < 0 else markdown[start:next_start]

    @staticmethod
    def _issue(code: str, command_path: str, message: str) -> CommandReferenceDiagnostic:
        return CommandReferenceDiagnostic(code=code, command_path=command_path, message=message)
