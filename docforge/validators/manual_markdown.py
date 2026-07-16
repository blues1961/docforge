from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from docforge.manual_blueprint import ManualBlueprint
from docforge.manual_knowledge import ManualKnowledge


@dataclass(frozen=True, slots=True)
class ManualMarkdownDiagnostic:
    code: str
    severity: str
    message: str
    section: str | None = None
    fact: str | None = None


class ManualMarkdownValidator:
    FORBIDDEN_VOCABULARY = (
        "workflow structuré",
        "fait structuré",
        "permission structurée",
        "requires-context",
        "ManualKnowledge",
        "ProjectKnowledge",
        "dataclass",
        "builder",
        "projection",
        "pipeline documentaire",
    )

    PLACEHOLDER_PATTERNS = (
        re.compile(r"\bTODO\b", re.I),
        re.compile(r"\bTBD\b", re.I),
        re.compile(r"\bFIXME\b", re.I),
        re.compile(r"\bXXX\b", re.I),
        re.compile(r"\[\s*à compléter\s*\]", re.I),
        re.compile(r"\{\{[^}]+\}\}"),
    )

    INTERFACE_METADATA_PATTERNS = (
        re.compile(r"^conversation id\s*:", re.I),
        re.compile(r"^model\s*:", re.I),
        re.compile(r"^assistant\s*:", re.I),
        re.compile(r"^exported\s+from\b", re.I),
    )

    WARNING_HINTS = (
        "attention",
        "avert",
        "danger",
        "destruct",
        "écrase",
        "écrasement",
        "supprime",
        "suppression",
        "prudence",
    )

    def validate(
        self,
        *,
        markdown: str,
        knowledge: ManualKnowledge | dict[str, Any],
        blueprint: ManualBlueprint,
    ) -> list[ManualMarkdownDiagnostic]:
        payload = knowledge.to_dict() if isinstance(knowledge, ManualKnowledge) else knowledge
        diagnostics: list[ManualMarkdownDiagnostic] = []
        lines = markdown.splitlines()
        first_non_empty = next((line.strip() for line in lines if line.strip()), "")
        expected_h1 = self.expected_h1(payload)

        if not first_non_empty.startswith("# "):
            diagnostics.append(ManualMarkdownDiagnostic(
                code="MANUAL001",
                severity="error",
                message="Le premier contenu non vide doit être un titre H1.",
            ))
        elif first_non_empty != expected_h1:
            diagnostics.append(ManualMarkdownDiagnostic(
                code="MANUAL012",
                severity="warning",
                message=f"Le H1 attendu est '{expected_h1}'.",
                fact=first_non_empty,
            ))

        diagnostics.extend(self._validate_interface_metadata(lines))
        diagnostics.extend(self._validate_section_order(markdown, blueprint))
        diagnostics.extend(self._validate_forbidden_vocabulary(markdown, blueprint.profile_name))
        diagnostics.extend(self._validate_placeholders(markdown))
        diagnostics.extend(self._validate_commands(lines, payload))
        diagnostics.extend(self._validate_urls_and_endpoints(markdown, payload))
        diagnostics.extend(self._validate_duplicates(lines))
        return diagnostics

    @staticmethod
    def expected_h1(payload: dict[str, Any]) -> str:
        project_name = (
            payload.get("application", {}).get("name")
            or payload.get("project", {}).get("name")
            or "l’application"
        )
        return f"# Guide utilisateur de {project_name}"

    def _validate_interface_metadata(self, lines: list[str]) -> list[ManualMarkdownDiagnostic]:
        diagnostics: list[ManualMarkdownDiagnostic] = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            for pattern in self.INTERFACE_METADATA_PATTERNS:
                if pattern.search(stripped):
                    diagnostics.append(ManualMarkdownDiagnostic(
                        code="MANUAL002",
                        severity="error",
                        message="Une ligne de métadonnées d’interface ou d’export ne doit pas apparaître dans le manuel final.",
                        fact=stripped,
                    ))
                    return diagnostics
        return diagnostics

    def _validate_section_order(self, markdown: str, blueprint: ManualBlueprint) -> list[ManualMarkdownDiagnostic]:
        diagnostics: list[ManualMarkdownDiagnostic] = []
        positions: list[tuple[str, int]] = []
        for section in blueprint.sections:
            match = re.search(rf"^##+\s+{re.escape(section.title)}\s*$", markdown, re.M)
            if not match:
                diagnostics.append(ManualMarkdownDiagnostic(
                    code="MANUAL003",
                    severity="error",
                    message=f"La section obligatoire '{section.title}' est absente.",
                    section=section.identifier,
                ))
                continue
            positions.append((section.identifier, match.start()))
        if positions != sorted(positions, key=lambda item: item[1]):
            diagnostics.append(ManualMarkdownDiagnostic(
                code="MANUAL004",
                severity="error",
                message="Les sections obligatoires du blueprint ne sont pas dans le bon ordre.",
            ))
        return diagnostics

    def _validate_forbidden_vocabulary(self, markdown: str, profile_name: str) -> list[ManualMarkdownDiagnostic]:
        lowered = markdown.casefold()
        diagnostics: list[ManualMarkdownDiagnostic] = []
        forbidden = self.FORBIDDEN_VOCABULARY
        if profile_name == "python-cli":
            forbidden = tuple(token for token in forbidden if token not in {"ProjectKnowledge", "ManualKnowledge", "builder", "projection"})
        for token in forbidden:
            if token.casefold() in lowered:
                diagnostics.append(ManualMarkdownDiagnostic(
                    code="MANUAL005",
                    severity="error",
                    message=f"Le vocabulaire interne interdit '{token}' apparaît dans le manuel.",
                    fact=token,
                ))
        return diagnostics

    def _validate_placeholders(self, markdown: str) -> list[ManualMarkdownDiagnostic]:
        diagnostics: list[ManualMarkdownDiagnostic] = []
        for pattern in self.PLACEHOLDER_PATTERNS:
            for match in pattern.finditer(markdown):
                diagnostics.append(ManualMarkdownDiagnostic(
                    code="MANUAL013",
                    severity="error",
                    message="Un placeholder ou marqueur de rédaction a été laissé dans le document final.",
                    fact=match.group(0),
                ))
        return diagnostics

    def _validate_commands(self, lines: list[str], payload: dict[str, Any]) -> list[ManualMarkdownDiagnostic]:
        diagnostics: list[ManualMarkdownDiagnostic] = []
        command_map = {command["command_path"]: command for command in payload.get("commands", [])}
        for command in payload.get("operational_commands", {}).get("commands", []):
            command_map.setdefault(command.get("command_path"), command)
        joined = "\n".join(lines)
        snippets = set(re.findall(r"`([^`]+)`", joined))
        command_snippets = [snippet for snippet in snippets if self._looks_like_command(snippet)]
        for snippet in command_snippets:
            base = self._matching_command_path(snippet, command_map)
            if base is None:
                diagnostics.append(ManualMarkdownDiagnostic(
                    code="MANUAL006",
                    severity="error",
                    message=f"La commande '{snippet}' ne correspond à aucun command_path démontré.",
                    fact=snippet,
                ))
                continue
            command = command_map[base]
            allowed_parameters = {parameter.get("name") for parameter in command.get("parameters", [])}
            allowed_flags = {flag for parameter in command.get("parameters", []) for flag in parameter.get("flags", [])}
            for parameter_name, parameter_value in re.findall(r"\b([A-Z][A-Z0-9_]*)=([^\s`]+)", snippet):
                if parameter_name not in allowed_parameters:
                    diagnostics.append(ManualMarkdownDiagnostic(
                        code="MANUAL007",
                        severity="error",
                        message=f"Le paramètre '{parameter_name}' n’est pas exposé par la commande '{base}'.",
                        fact=snippet,
                    ))
                    continue
                parameter = next((item for item in command.get("parameters", []) if item.get("name") == parameter_name), None)
                allowed_values = parameter.get("allowed_values", []) if parameter else []
                if allowed_values and parameter_value not in allowed_values:
                    diagnostics.append(ManualMarkdownDiagnostic(
                        code="MANUAL014",
                        severity="error",
                        message=f"La valeur '{parameter_value}' n’est pas autorisée pour '{parameter_name}' sur la commande '{base}'.",
                        fact=snippet,
                    ))
            for flag in re.findall(r"(--[A-Za-z0-9][A-Za-z0-9\-]*)", snippet):
                if flag not in allowed_flags:
                    diagnostics.append(ManualMarkdownDiagnostic(
                        code="MANUAL015",
                        severity="error",
                        message=f"L’option '{flag}' n’est pas démontrée pour la commande '{base}'.",
                        fact=snippet,
                    ))
            if command.get("destructive") and not self._has_warning_near_command(lines, snippet):
                diagnostics.append(ManualMarkdownDiagnostic(
                    code="MANUAL011",
                    severity="warning",
                    message=f"La commande destructive '{base}' est citée sans avertissement explicite fondé sur ses effets détectés.",
                    fact=", ".join(command.get("destructive_effects", [])) or base,
                ))
        return diagnostics

    def _validate_urls_and_endpoints(self, markdown: str, payload: dict[str, Any]) -> list[ManualMarkdownDiagnostic]:
        diagnostics: list[ManualMarkdownDiagnostic] = []
        valid_urls = {
            endpoint.get("url")
            for endpoint in payload.get("service_endpoints", {}).get("endpoints", [])
            if endpoint.get("validity") == "valid" and endpoint.get("url")
        }
        invalid_urls = {
            endpoint.get("url")
            for endpoint in payload.get("service_endpoints", {}).get("endpoints", [])
            if endpoint.get("validity") != "valid" and endpoint.get("url")
        }
        resolved_paths = {
            endpoint.get("path")
            for endpoint in payload.get("django", {}).get("endpoints", [])
            if endpoint.get("path")
        }
        for url in set(re.findall(r'https?://[^\s)>"`]+', markdown)):
            if url in invalid_urls or url not in valid_urls:
                diagnostics.append(ManualMarkdownDiagnostic(
                    code="MANUAL008",
                    severity="error",
                    message=f"L’URL '{url}' n’est pas un endpoint opérationnel valide démontré.",
                    fact=url,
                ))
        for path in set(re.findall(r"(?<![A-Za-z0-9_])(/api/[A-Za-z0-9_\-/{}/:.]+/?)(?![A-Za-z0-9_])", markdown)):
            if path not in resolved_paths:
                diagnostics.append(ManualMarkdownDiagnostic(
                    code="MANUAL009",
                    severity="error",
                    message=f"Le chemin d’endpoint '{path}' n’est pas résolu dans ManualKnowledge.",
                    fact=path,
                ))
        return diagnostics

    def _validate_duplicates(self, lines: list[str]) -> list[ManualMarkdownDiagnostic]:
        diagnostics: list[ManualMarkdownDiagnostic] = []
        technical_lines = [line.strip() for line in lines if line.strip().startswith(("- `make ", "- `http", "- `/api/"))]
        duplicates = {line for line in technical_lines if technical_lines.count(line) > 1}
        for line in sorted(duplicates):
            diagnostics.append(ManualMarkdownDiagnostic(
                code="MANUAL010",
                severity="warning",
                message="Une ligne technique est dupliquée inutilement dans le manuel.",
                fact=line,
            ))
        return diagnostics

    def _has_warning_near_command(self, lines: list[str], snippet: str) -> bool:
        for index, line in enumerate(lines):
            if snippet not in line:
                continue
            window = " ".join(lines[max(0, index - 3): min(len(lines), index + 4)]).casefold()
            if any(token in window for token in self.WARNING_HINTS):
                return True
        return False

    @staticmethod
    def _looks_like_command(snippet: str) -> bool:
        return snippet.startswith(("make ", "npm ", "python ", "docker ", "docforge "))

    @staticmethod
    def _matching_command_path(snippet: str, command_map: dict[str, dict[str, Any]]) -> str | None:
        candidates = sorted(command_map, key=len, reverse=True)
        for candidate in candidates:
            if snippet == candidate or snippet.startswith(candidate + " "):
                return candidate
        return None
