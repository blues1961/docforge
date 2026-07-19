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
    line: int | None = None


@dataclass(frozen=True, slots=True)
class MarkdownHeading:
    level: int
    title: str
    line_number: int


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
    UNSUPPORTED_PLATFORM_PATTERNS = tuple(re.compile(pattern, re.I) for pattern in (r"\bwindows\b", r"\bpowershell\b", r"\bwsl\b", r"\bmacos\b", r"\bmac\s*os\b"))

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
        expected_h1 = self.expected_h1(payload, blueprint)

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
        diagnostics.extend(self._validate_hybrid_safety(markdown, payload))
        diagnostics.extend(self._validate_duplicates(lines))
        return diagnostics

    @staticmethod
    def expected_h1(
        payload: dict[str, Any],
        blueprint: ManualBlueprint,
    ) -> str:
        project_name = (
            payload.get("application", {}).get("name")
            or payload.get("project", {}).get("name")
            or "l’application"
        )
        # Keep technical slugs separate while rendering the canonical public name.
        project_name = project_name[:1].upper() + project_name[1:]
        template_id = payload.get("template", {}).get("template_id") or payload.get("template", {}).get("origin_template_id") or project_name
        if blueprint.document_kind == "template-creation-guide":
            return f"# Guide de création d’une application avec {template_id}"
        if blueprint.document_kind == "template-maintenance-guide":
            return f"# Guide de maintenance du modèle {template_id}"
        if blueprint.document_title == "Guide d’exploitation":
            return f"# Guide d’exploitation de {project_name}"
        if blueprint.document_title == "Référence développeur":
            return f"# Référence développeur de {project_name}"
        if blueprint.document_kind == "generic-guide":
            return f"# Guide de {project_name}"
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
        canonical_titles = {section.title for section in blueprint.sections}
        headings = self._extract_headings(markdown)
        h1_headings = [heading for heading in headings if heading.level == 1]
        if len(h1_headings) != 1:
            diagnostics.append(ManualMarkdownDiagnostic(
                code="MANUAL021", severity="error",
                message="Le manuel doit contenir exactement un H1 global.",
                fact=", ".join(str(item.line_number) for item in h1_headings),
            ))
        h2_headings = [heading for heading in headings if heading.level == 2]
        canonical_h2 = [heading for heading in h2_headings if heading.title in canonical_titles]
        canonical_deeper = [heading for heading in headings if heading.level >= 3 and heading.title in canonical_titles]
        h2_by_title: dict[str, list[MarkdownHeading]] = {}
        deeper_by_title: dict[str, list[MarkdownHeading]] = {}
        for heading in canonical_h2:
            h2_by_title.setdefault(heading.title, []).append(heading)
        for heading in canonical_deeper:
            deeper_by_title.setdefault(heading.title, []).append(heading)

        positions: list[tuple[str, int]] = []
        for section in blueprint.sections:
            matches = h2_by_title.get(section.title, [])
            if not matches:
                deeper_matches = deeper_by_title.get(section.title, [])
                if deeper_matches:
                    levels = ", ".join(f"H{item.level} ligne {item.line_number}" for item in deeper_matches)
                    message = (
                        f"La section obligatoire '{section.title}' est absente comme H2 canonique "
                        f"et n’apparaît qu’en sous-titre ({levels})."
                    )
                else:
                    message = f"La section obligatoire '{section.title}' est absente."
                diagnostics.append(ManualMarkdownDiagnostic(
                    code="MANUAL003",
                    severity="error",
                    message=message,
                    section=section.identifier,
                ))
                continue
            if len(matches) > 1:
                diagnostics.append(ManualMarkdownDiagnostic(
                    code="MANUAL016",
                    severity="error",
                    message=(
                        f"La section obligatoire '{section.title}' est dupliquée en H2 "
                        f"(lignes {', '.join(str(item.line_number) for item in matches)})."
                    ),
                    section=section.identifier,
                    fact=section.title,
                ))
            positions.append((section.identifier, matches[0].line_number))

        for index, heading in enumerate(headings[:-1]):
            following = headings[index + 1]
            if heading.level == 2 and heading.title in canonical_titles and following.level in {1, 3} and following.title == heading.title:
                diagnostics.append(ManualMarkdownDiagnostic(
                    code="MANUAL022", severity="error",
                    message=f"Le titre canonique '{heading.title}' est répété immédiatement après son H2.",
                    fact=heading.title, line=following.line_number,
                ))

        extra_h2_titles = [heading.title for heading in h2_headings if heading.title not in canonical_titles]
        for title in extra_h2_titles:
            diagnostics.append(ManualMarkdownDiagnostic(
                code="MANUAL017",
                severity="error",
                message=f"Le titre H2 supplémentaire '{title}' n’appartient pas au blueprint canonique.",
                fact=title,
            ))

        if positions != sorted(positions, key=lambda item: item[1]):
            diagnostics.append(ManualMarkdownDiagnostic(
                code="MANUAL004",
                severity="error",
                message="Les sections obligatoires du blueprint ne sont pas dans le bon ordre.",
            ))
        return diagnostics

    def _extract_headings(self, markdown: str) -> list[MarkdownHeading]:
        headings: list[MarkdownHeading] = []
        in_fence = False
        for line_number, line in enumerate(markdown.splitlines(), start=1):
            stripped = line.lstrip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            match = re.match(r"^(#{1,6})\s+(.*?)\s*$", stripped)
            if not match:
                continue
            headings.append(MarkdownHeading(
                level=len(match.group(1)),
                title=match.group(2),
                line_number=line_number,
            ))
        return headings

    def _validate_forbidden_vocabulary(self, markdown: str, profile_name: str) -> list[ManualMarkdownDiagnostic]:
        lowered = markdown.casefold()
        diagnostics: list[ManualMarkdownDiagnostic] = []
        forbidden = self.FORBIDDEN_VOCABULARY
        if profile_name == "python-cli":
            forbidden = tuple(token for token in forbidden if token not in {"ProjectKnowledge", "ManualKnowledge", "builder", "projection"})
        headings = [heading for heading in self._extract_headings(markdown) if heading.level == 2]
        for token in forbidden:
            match = re.search(re.escape(token), markdown, re.I)
            if match:
                line = markdown.count("\n", 0, match.start()) + 1
                section = next((heading.title for heading in reversed(headings) if heading.line_number <= line), None)
                diagnostics.append(ManualMarkdownDiagnostic(
                    code="MANUAL005",
                    severity="error",
                    message=f"Le vocabulaire interne interdit '{token}' apparaît dans le manuel.",
                    section=section,
                    fact=token,
                    line=line,
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
        for raw_url in set(re.findall(r'https?://[^\s)>"`]+', markdown)):
            # Sentence punctuation is not part of the endpoint. The expression
            # deliberately leaves URL-internal punctuation untouched.
            url = raw_url.rstrip(".,;:)")
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

    def _validate_hybrid_safety(self, markdown: str, payload: dict[str, Any]) -> list[ManualMarkdownDiagnostic]:
        diagnostics: list[ManualMarkdownDiagnostic] = []
        lines = markdown.splitlines()
        headings = [(index + 1, line[3:].strip()) for index, line in enumerate(lines) if line.startswith("## ")]
        def location(index: int) -> tuple[int, str | None]:
            line_number = index + 1
            section = next((title for number, title in reversed(headings) if number <= line_number), None)
            return line_number, section
        seen: set[tuple[int, str]] = set()
        for pattern in self.UNSUPPORTED_PLATFORM_PATTERNS:
            for match in pattern.finditer(markdown):
                line, section = location(markdown.count("\n", 0, match.start()))
                key = (line, match.group(0).casefold())
                if key not in seen:
                    seen.add(key)
                    diagnostics.append(ManualMarkdownDiagnostic("MANUAL018", "error", f"La plateforme '{match.group(0)}' n’est pas démontrée dans ManualKnowledge.", section, match.group(0), line))
        configuration = payload.get("configuration", {})
        files = configuration.get("files", []) if isinstance(configuration, dict) else []
        known = {str(item.get("path")).rstrip("/") for item in files if isinstance(item, dict) and item.get("path")}
        profile_name = str(payload.get("project", {}).get("profile_type") or "")
        demonstrated_env_local = ".env.local" in known
        for match in re.finditer(r"`((?:~?/)?\.?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*/?)`", markdown):
            raw = match.group(1); path = raw.rstrip("/")
            relevant = path.startswith((".docforge", "~/.config", "reports")) or path in {".gitignore", "pyproject.toml"}
            allowed = path in known or any(item.startswith(path + "/") for item in known)
            if path == ".env.local":
                # A generic secret-protection rule is not evidence for a particular
                # file. This filename is allowed only when this profile exposes it.
                relevant = profile_name == "python-cli" or not demonstrated_env_local
                allowed = demonstrated_env_local
            if relevant and not allowed:
                line, section = location(markdown.count("\n", 0, match.start()))
                diagnostics.append(ManualMarkdownDiagnostic("MANUAL019", "error", f"Le chemin de configuration '{raw}' est absent de ManualKnowledge.", section, raw, line))
        controls = payload.get("security", {}).get("controls", [])
        control_text = " ".join(
            " ".join(str(control.get(key, "")) for key in ("description", "evidence"))
            if isinstance(control, dict) else str(control)
            for control in controls
        ).casefold()
        explicit_apply = "commande explicite" in control_text or "docforge apply" in control_text
        policy = payload.get("documentation_policy", {})
        deterministic_documents = policy.get("deterministic_documents", []) if isinstance(policy, dict) else []
        optional_documents = policy.get("optional_documents", []) if isinstance(policy, dict) else []
        reported_automation_lines: set[int] = set()
        for match in re.finditer(r"\b(?:automatiquement|automatisée?|sans intervention)\b", markdown, re.I):
            line, section = location(markdown.count("\n", 0, match.start()))
            if line in reported_automation_lines:
                continue
            text = lines[line - 1].strip()
            lowered = text.casefold()
            negative = any(token in lowered for token in ("n’est jamais", "n'est jamais", "ne se produit jamais", "ne se fait jamais", "n’est jamais effectué", "n'est jamais effectué", "n'est jamais effectue", "n’est appliquée", "n'est appliquée", "n'est appliquee", "ne sont jamais", "ne sont pas", "ne s’appliquent pas", "ne s'appliquent pas", "ne doit jamais", "ne doivent jamais", "non régénéré", "non regenere", "ne représente pas", "ne represente pas"))
            meta_documentary = any(phrase in lowered for phrase in (
                "ne représente pas un comportement observé automatiquement",
                "ne représentent pas un comportement observé automatiquement",
                "ne represente pas un comportement observe automatiquement",
                "ne representent pas un comportement observe automatiquement",
                "ne doivent pas être interprétées comme des comportements observés sans intervention explicite",
                "ne doivent pas être interprétées comme un comportement automatique",
                "ne doivent pas etre interpretees comme des comportements observes sans intervention explicite",
                "ne doivent pas etre interpretees comme un comportement automatique",
            ))
            profile_source = payload.get("profile", {}).get("source", {})
            demonstrated_profile_detection = (
                "profil" in lowered
                and "détermine automatiquement" in lowered
                and isinstance(profile_source, dict)
                and profile_source.get("status") == "detected"
                and bool(profile_source.get("sources"))
            )
            applies_to_application = "appliqu" in lowered or "application" in lowered
            applies_to_optional_documents = "optionnel" in lowered and "régénér" in lowered
            applies_to_deterministic_documents = "déterministe" in lowered and "génér" in lowered
            if meta_documentary or demonstrated_profile_detection:
                continue
            if negative and ((applies_to_application and explicit_apply) or (applies_to_optional_documents and bool(optional_documents))):
                continue
            if not negative and applies_to_deterministic_documents and deterministic_documents:
                continue
            reported_automation_lines.add(line)
            diagnostics.append(ManualMarkdownDiagnostic("MANUAL020", "error", "Une affirmation d’automatisation doit être étayée explicitement par ManualKnowledge.", section, text, line))
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
        if re.match(r"^docforge\s+(?:->|=)", snippet) or snippet.startswith("docforge:"):
            return False
        return snippet.startswith(("make ", "npm ", "python ", "docker ", "docforge "))

    @staticmethod
    def _matching_command_path(snippet: str, command_map: dict[str, dict[str, Any]]) -> str | None:
        candidates = sorted(command_map, key=len, reverse=True)
        for candidate in candidates:
            if snippet == candidate or snippet.startswith(candidate + " "):
                return candidate
        return None
