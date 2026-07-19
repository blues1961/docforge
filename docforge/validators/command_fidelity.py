from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from docforge.manual_knowledge import ManualKnowledge


@dataclass(frozen=True, slots=True)
class CommandSnippet:
    text: str
    kind: str


@dataclass(frozen=True, slots=True)
class OptionGroup:
    parameter_name: str
    aliases: tuple[str, ...]

    @property
    def label(self) -> str:
        return " / ".join(self.aliases)


def _unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


class CommandFidelityValidator:
    INLINE_CODE_PATTERN = re.compile(r"`([^`\n]+)`")
    FENCED_CODE_PATTERN = re.compile(r"```[^\n]*\n(.*?)```", re.S)
    FLAG_PATTERN = re.compile(r"(?<![\w-])(--[A-Za-z0-9][A-Za-z0-9-]*|-[A-Za-z])(?![\w-])")
    PLACEHOLDER_PATTERN = re.compile(r"^\[?[A-Z][A-Z0-9_]*(?:_[A-Z0-9_]+)*\]?$")
    COMMAND_PATH_TOKEN_PATTERN = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")

    def validate(
        self,
        *,
        markdown: str,
        knowledge: ManualKnowledge | dict[str, Any],
    ) -> dict[str, Any]:
        payload = knowledge.to_dict() if isinstance(knowledge, ManualKnowledge) else knowledge
        commands = self._documented_commands(payload)
        snippets = self._extract_snippets(markdown)
        command_results = [
            self._validate_command(command=command, markdown=markdown, snippets=snippets)
            for command in commands
        ]

        global_strict_errors = self._detect_unknown_command_mentions(
            snippets=snippets,
            known_invocations=self._known_invocations_with_parents(commands),
        )
        strict_errors = [
            *global_strict_errors,
            *[issue for command in command_results for issue in command["strict_errors"]],
        ]
        warnings = [issue for command in command_results for issue in command["warnings"]]
        fully_missing = [
            command["command_path"]
            for command in command_results
            if command["presence"]["totally_absent"]
        ]
        command_path_only = [
            command["command_path"]
            for command in command_results
            if command["presence"]["command_path_only"]
        ]
        missing_invocations = [
            command["command_path"]
            for command in command_results
            if not command["presence"]["invocation_present"]
        ]
        unknown_options = _unique_preserve_order(
            [
                option
                for command in command_results
                for option in command["options"]["unknown"]
            ]
        )
        unknown_commands = _unique_preserve_order(
            [
                str(issue["fact"])
                for issue in strict_errors
                if issue["code"] == "FIDELITY001" and issue.get("fact")
            ]
        )

        return {
            "documented_command_count": len(commands),
            "command_path_coverage": {
                "present": len(commands) - len(fully_missing),
                "total": len(commands),
                "percent": self._percent(len(commands) - len(fully_missing), len(commands)),
            },
            "executable_invocation_coverage": {
                "present": len(commands) - len(missing_invocations),
                "total": len(commands),
                "percent": self._percent(len(commands) - len(missing_invocations), len(commands)),
            },
            "strict_error_count": len(strict_errors),
            "warning_count": len(warnings),
            "unknown_command_mentions": unknown_commands,
            "unknown_options": unknown_options,
            "totally_absent_commands": fully_missing,
            "command_path_only_commands": command_path_only,
            "missing_full_invocations": missing_invocations,
            "strict_errors": strict_errors,
            "warnings": warnings,
            "commands": command_results,
            "classification": {
                "strict_errors": [
                    {
                        "kind": "commande inconnue",
                        "rule": "Un extrait qui invoque `docforge ...` avec un chemin absent de ManualKnowledge contredit les faits disponibles.",
                    },
                    {
                        "kind": "option inconnue",
                        "rule": "Une option absente des paramètres connus de la commande est une invention factuelle, donc une erreur stricte.",
                    },
                    {
                        "kind": "syntaxe contredisant les faits",
                        "rule": "Une invocation complète qui associe une option à la mauvaise commande ou reconstruit une syntaxe incompatible avec les faits structurés est une erreur stricte.",
                    },
                    {
                        "kind": "invocation requise mais non exécutable",
                        "rule": "Une syntaxe présentée comme copiable mais privée du préfixe exécutable documenté reste non exécutable et doit être signalée.",
                    },
                ],
                "warnings": [
                    {
                        "kind": "commande connue totalement absente",
                        "rule": "L’absence de mention n’invente rien; elle mesure une lacune de couverture documentaire.",
                    },
                    {
                        "kind": "option connue omise",
                        "rule": "Un groupe d’options démontré mais jamais documenté indique une référence incomplète, pas une contradiction.",
                    },
                    {
                        "kind": "commande présente seulement sous forme de command_path",
                        "rule": "La commande est identifiable, mais l’invocation exécutable complète manque; c’est un problème de complétude, pas un fait inventé.",
                    },
                ],
            },
        }

    def render_markdown_report(self, report: dict[str, Any]) -> str:
        lines = [
            "# Validation de fidélité des commandes",
            "",
            "## Résumé",
            f"- Commandes documentables : {report['documented_command_count']}",
            (
                "- Couverture `command_path` : "
                f"{report['command_path_coverage']['present']}/{report['command_path_coverage']['total']} "
                f"({report['command_path_coverage']['percent']}%)"
            ),
            (
                "- Couverture d’invocation exécutable : "
                f"{report['executable_invocation_coverage']['present']}/{report['executable_invocation_coverage']['total']} "
                f"({report['executable_invocation_coverage']['percent']}%)"
            ),
            f"- Erreurs strictes : {report['strict_error_count']}",
            f"- Avertissements : {report['warning_count']}",
            "",
            "## Couverture",
            "- Commandes totalement absentes : " + (", ".join(report["totally_absent_commands"]) or "aucune"),
            "- Commandes présentes seulement par `command_path` : " + (", ".join(report["command_path_only_commands"]) or "aucune"),
            "- Invocations complètes manquantes : " + (", ".join(report["missing_full_invocations"]) or "aucune"),
            "",
            "## Erreurs strictes",
        ]
        if report["strict_errors"]:
            for issue in report["strict_errors"]:
                lines.append(f"- `{issue['command_path']}`: {issue['message']}")
        else:
            lines.append("- Aucune.")
        lines.extend(["", "## Avertissements"])
        if report["warnings"]:
            for issue in report["warnings"]:
                lines.append(f"- `{issue['command_path']}`: {issue['message']}")
        else:
            lines.append("- Aucun.")
        lines.extend(["", "## Détail par commande"])
        for command in report["commands"]:
            lines.extend(
                [
                    f"### `{command['command_path']}`",
                    f"- Invocation attendue : `{command['invocation']}`",
                    (
                        "- Présence : "
                        f"command_path={'oui' if command['presence']['command_path_present'] else 'non'}, "
                        f"invocation={'oui' if command['presence']['invocation_present'] else 'non'}"
                    ),
                    "- Groupes d’options connus présents : " + (", ".join(command["options"]["known_present_groups"]) or "aucun"),
                    "- Groupes d’options connus absents : " + (", ".join(command["options"]["known_missing_groups"]) or "aucun"),
                    "- Alias présentés : " + (", ".join(command["options"]["presented_aliases"]) or "aucun"),
                    "- Alias non présentés : " + (", ".join(command["options"]["omitted_aliases"]) or "aucun"),
                    "- Options inconnues ou inventées : " + (", ".join(command["options"]["unknown"]) or "aucune"),
                    "- Paramètres positionnels connus : " + (", ".join(command["positionals"]["known"]) or "aucun"),
                    "- Paramètres positionnels présents : " + (", ".join(command["positionals"]["present"]) or "aucun"),
                    "- Paramètres positionnels manquants : " + (", ".join(command["positionals"]["missing"]) or "aucun"),
                    "- Invocations complètes absentes : oui" if not command["presence"]["invocation_present"] else "- Invocations complètes absentes : non",
                    "- Syntaxes potentiellement non exécutables : " + (", ".join(f"`{item}`" for item in command["non_executable_snippets"]) or "aucune"),
                    "",
                ]
            )
        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _percent(value: int, total: int) -> float:
        if total == 0:
            return 100.0
        return round((value * 100) / total, 2)

    def _documented_commands(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        commands: list[dict[str, Any]] = []
        for command in payload.get("commands", []):
            if not isinstance(command, dict):
                continue
            if command.get("visibility") != "public":
                continue
            if command.get("documentation_policy") == "exclude":
                continue
            if command.get("reference_level") == "omit":
                continue
            if not command.get("command_path") or not command.get("invocation"):
                continue
            commands.append(command)
        return commands

    def _validate_command(
        self,
        *,
        command: dict[str, Any],
        markdown: str,
        snippets: list[CommandSnippet],
    ) -> dict[str, Any]:
        command_path = str(command["command_path"])
        invocation = str(command["invocation"])
        related_snippets = [
            snippet
            for snippet in snippets
            if self._snippet_mentions_command(snippet.text, invocation, command_path)
        ]
        command_path_present = self._contains_command_path(markdown, command_path)
        invocation_present = any(
            stripped == invocation or stripped.startswith(invocation + " ")
            for stripped in [snippet.text.strip() for snippet in related_snippets]
        )
        totally_absent = not command_path_present and not invocation_present
        command_path_only = command_path_present and not invocation_present

        option_groups = self._option_groups(command)
        allowed_flags = _unique_preserve_order(
            [alias for group in option_groups for alias in group.aliases]
        )
        known_positionals = _unique_preserve_order(
            [
                str(parameter.get("name"))
                for parameter in command.get("parameters", [])
                if isinstance(parameter, dict)
                and parameter.get("kind") == "argument"
                and isinstance(parameter.get("name"), str)
            ]
        )
        command_section = self._command_section(markdown, command_path)
        observed_flags = _unique_preserve_order(
            [
                flag
                for snippet in related_snippets
                for flag in self.FLAG_PATTERN.findall(snippet.text)
                if not self._is_global_flag(flag)
            ]
            + [
                flag
                for flag in self.FLAG_PATTERN.findall(command_section)
                if not self._is_global_flag(flag)
            ]
        )
        presented_aliases = [flag for flag in observed_flags if flag in allowed_flags]
        unknown_flags = _unique_preserve_order([flag for flag in observed_flags if flag not in allowed_flags])
        positional_tokens = _unique_preserve_order(
            [token for snippet in related_snippets for token in self._placeholder_tokens(snippet.text)]
        )
        present_positionals = [token for token in known_positionals if token in positional_tokens]
        missing_positionals = [token for token in known_positionals if token not in positional_tokens]
        non_executable_snippets = _unique_preserve_order(
            [
                snippet.text.strip()
                for snippet in related_snippets
                if self._looks_like_non_executable_command(snippet.text, invocation, command_path)
            ]
        )

        present_groups: list[str] = []
        missing_groups: list[str] = []
        omitted_aliases: list[str] = []
        for group in option_groups:
            group_presented = [alias for alias in group.aliases if alias in presented_aliases]
            if group_presented:
                present_groups.append(group.label)
                omitted_aliases.extend(alias for alias in group.aliases if alias not in group_presented)
            else:
                missing_groups.append(group.label)
                omitted_aliases.extend(group.aliases)

        strict_errors: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []

        if totally_absent:
            warnings.append(
                self._issue(
                    code="FIDELITY101",
                    severity="warning",
                    command_path=command_path,
                    message="Commande connue totalement absente du guide assemblé.",
                )
            )
        elif command_path_only:
            warnings.append(
                self._issue(
                    code="FIDELITY103",
                    severity="warning",
                    command_path=command_path,
                    message="La commande est mentionnée par `command_path`, mais l’invocation complète exécutable est absente.",
                )
            )

        for flag in unknown_flags:
            strict_errors.append(
                self._issue(
                    code="FIDELITY002",
                    severity="error",
                    command_path=command_path,
                    message=f"Option inconnue ou inventée détectée : `{flag}`.",
                    fact=flag,
                )
            )

        for group_label in missing_groups:
            warnings.append(
                self._issue(
                    code="FIDELITY104",
                    severity="warning",
                    command_path=command_path,
                    message=f"Groupe d’options connu omis dans le guide assemblé : `{group_label}`.",
                    fact=group_label,
                )
            )

        return {
            "name": command.get("name"),
            "command_path": command_path,
            "invocation": invocation,
            "presence": {
                "command_path_present": command_path_present,
                "invocation_present": invocation_present,
                "totally_absent": totally_absent,
                "command_path_only": command_path_only,
            },
            "options": {
                "known_groups": [
                    {
                        "parameter_name": group.parameter_name,
                        "aliases": list(group.aliases),
                        "label": group.label,
                    }
                    for group in option_groups
                ],
                "known_present_groups": present_groups,
                "known_missing_groups": missing_groups,
                "presented_aliases": presented_aliases,
                "omitted_aliases": _unique_preserve_order(omitted_aliases),
                "unknown": unknown_flags,
            },
            "positionals": {
                "known": known_positionals,
                "present": present_positionals,
                "missing": missing_positionals,
            },
            "non_executable_snippets": non_executable_snippets,
            "strict_errors": strict_errors,
            "warnings": warnings,
        }

    @staticmethod
    def _command_section(markdown: str, command_path: str) -> str:
        marker = f"#### `{command_path}`"
        start = markdown.find(marker)
        if start < 0:
            return ""
        next_start = markdown.find("\n#### `", start + len(marker))
        return markdown[start:] if next_start < 0 else markdown[start:next_start]

    def _option_groups(self, command: dict[str, Any]) -> list[OptionGroup]:
        groups: list[OptionGroup] = []
        for parameter in command.get("parameters", []):
            if not isinstance(parameter, dict) or parameter.get("kind") != "option":
                continue
            aliases = tuple(
                flag
                for flag in parameter.get("flags", [])
                if isinstance(flag, str)
            )
            if not aliases:
                continue
            groups.append(OptionGroup(parameter_name=str(parameter.get("name")), aliases=aliases))
        return groups

    def _extract_snippets(self, markdown: str) -> list[CommandSnippet]:
        snippets: list[CommandSnippet] = []
        for match in self.FENCED_CODE_PATTERN.finditer(markdown):
            block_text = match.group(1).strip()
            if not block_text:
                continue
            for line in block_text.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                snippets.append(CommandSnippet(text=stripped, kind="fenced"))
        for match in self.INLINE_CODE_PATTERN.finditer(markdown):
            text = match.group(1).strip()
            if text:
                snippets.append(CommandSnippet(text=text, kind="inline"))
        return snippets

    @staticmethod
    def _known_invocations_with_parents(commands: list[dict[str, Any]]) -> set[str]:
        invocations: set[str] = set()
        for command in commands:
            invocation = str(command["invocation"])
            parts = invocation.split()
            for size in range(2, len(parts) + 1):
                invocations.add(" ".join(parts[:size]))
        return invocations

    def _detect_unknown_command_mentions(
        self,
        *,
        snippets: list[CommandSnippet],
        known_invocations: set[str],
    ) -> list[dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        seen: set[str] = set()
        for snippet in snippets:
            stripped = snippet.text.strip()
            if not self._is_command_invocation_candidate(stripped):
                continue
            if stripped == "docforge --help":
                continue
            if any(stripped == invocation or stripped.startswith(invocation + " ") for invocation in known_invocations):
                continue
            if stripped in seen:
                continue
            seen.add(stripped)
            issues.append(
                self._issue(
                    code="FIDELITY001",
                    severity="error",
                    command_path="<unknown>",
                    message=f"Commande inconnue ou non démontrée dans ManualKnowledge : `{stripped}`.",
                    fact=stripped,
                )
            )
        return issues

    def _is_command_invocation_candidate(self, text: str) -> bool:
        """Return whether text starts an executable ``docforge`` command path.

        Entry-point mappings and prose can start with ``docforge`` too (for
        example ``docforge -> package.module:app`` or ``docforge = value``).
        Only a lexical command-path token immediately following the executable
        name is eligible for command-fidelity validation.
        """
        if not text.startswith("docforge "):
            return False
        remainder = text.removeprefix("docforge ").lstrip()
        if not remainder:
            return False
        token = remainder.split(None, 1)[0]
        return bool(self.COMMAND_PATH_TOKEN_PATTERN.fullmatch(token))

    def _snippet_mentions_command(self, text: str, invocation: str, command_path: str) -> bool:
        stripped = text.strip()
        return (
            stripped == invocation
            or stripped.startswith(invocation + " ")
            or stripped == command_path
            or stripped.startswith(command_path + " ")
            or stripped.startswith(command_path + "[")
        )

    def _placeholder_tokens(self, text: str) -> list[str]:
        tokens: list[str] = []
        for raw in text.split():
            candidate = raw.strip("[](){}")
            if not candidate:
                continue
            if self.PLACEHOLDER_PATTERN.fullmatch(raw.strip()):
                tokens.append(candidate)
        return tokens

    def _contains_command_path(self, markdown: str, command_path: str) -> bool:
        pattern = re.compile(rf"(?<![\w-]){re.escape(command_path)}(?![\w-])")
        return bool(pattern.search(markdown))

    def _looks_like_non_executable_command(self, text: str, invocation: str, command_path: str) -> bool:
        stripped = text.strip()
        if stripped == invocation or stripped.startswith(invocation + " "):
            return False
        return stripped.startswith(command_path)

    @staticmethod
    def _is_global_flag(flag: str) -> bool:
        return flag in {"--help", "--short"}

    @staticmethod
    def _issue(
        *,
        code: str,
        severity: str,
        command_path: str,
        message: str,
        fact: str | None = None,
    ) -> dict[str, Any]:
        return {
            "code": code,
            "severity": severity,
            "command_path": command_path,
            "message": message,
            "fact": fact,
        }


def report_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"
