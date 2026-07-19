from __future__ import annotations

import json
from dataclasses import dataclass, field
from math import ceil
from typing import Any

from docforge.manual_blueprint import (
    ManualBlueprint,
    ManualSectionDefinition,
)
from docforge.manual_knowledge import ManualKnowledge


@dataclass(frozen=True, slots=True)
class SectionPromptContext:
    identifier: str
    title: str
    purpose: str
    projected_facts: dict[str, Any]
    estimated_tokens: int
    context_budget: int | None = None
    fact_breakdown: dict[str, int] = field(default_factory=dict)
    missing_fact_paths: list[str] = field(default_factory=list)
    repeated_fact_paths: list[str] = field(default_factory=list)


class ManualPromptBudgetExceeded(ValueError):
    def __init__(
        self,
        *,
        section_identifier: str,
        section_title: str,
        estimated_tokens: int,
        context_budget: int,
        fact_breakdown: dict[str, int] | None = None,
        missing_fact_paths: list[str] | None = None,
        repeated_fact_paths: list[str] | None = None,
    ) -> None:
        breakdown = fact_breakdown or {}
        top_groups = ", ".join(
            f"{name}={size}" for name, size in sorted(breakdown.items(), key=lambda item: item[1], reverse=True)[:5]
        )
        details = f" Groupes principaux: {top_groups}." if top_groups else ""
        missing = f" Faits absents: {', '.join(missing_fact_paths or [])}." if missing_fact_paths else ""
        repeated = f" Chemins répétés: {', '.join(repeated_fact_paths or [])}." if repeated_fact_paths else ""
        super().__init__(
            f"Le contexte de la section {section_identifier} ({section_title}) "
            f"dépasse le budget: {estimated_tokens} > {context_budget} tokens estimés."
            f"{details}{missing}{repeated}"
        )
        self.section_identifier = section_identifier
        self.section_title = section_title
        self.estimated_tokens = estimated_tokens
        self.context_budget = context_budget
        self.fact_breakdown = breakdown
        self.missing_fact_paths = list(missing_fact_paths or [])
        self.repeated_fact_paths = list(repeated_fact_paths or [])


class ManualPromptBuilder:
    DEFAULT_CONTEXT_BUDGET = 4096

    COMMON_RULES = (
        "Rédige un document Markdown fidèle aux faits fournis.",
        "Utilise `manual-knowledge.json` comme source unique de vérité et n’utilise aucune connaissance externe pour compléter les procédures ou les caractéristiques du projet.",
        "Suis strictement le blueprint fourni.",
        "N’invente jamais une commande, une option, une procédure, une route, une URL, un paramètre, une variable, un service ou une fonctionnalité.",
        "N’ajoute pas de bonnes pratiques générales comme si elles étaient démontrées par le projet.",
        "Utilise `command_path` pour identifier ou titrer une commande.",
        "Utilise `invocation` pour toute commande destinée à être copiée et exécutée.",
        "Ne reconstruis jamais une syntaxe de commande à partir de `name` seul.",
        "Les blocs Markdown déterministes fournis séparément sont la seule source des commandes exécutables, de leurs paramètres et des chemins de configuration; ne les répète, ne les reformule et ne les complète jamais.",
        "Rédige uniquement l’explication narrative qui accompagne les blocs déterministes.",
        "Conserve les statuts `detected`, `derived`, `configured` et `unresolved` dans leur sens : une configuration n’est jamais présentée comme un comportement observé automatiquement.",
        "Ne cite que les options et paramètres associés à la commande dans ManualKnowledge.",
        "Vérifie silencieusement chaque commande, paramètre, route, URL, variable, service, permission, workflow et champ cité avant de rédiger; cette vérification ne doit pas apparaître dans le manuel.",
        "Signale explicitement les informations manquantes et les limites sans reconstruire arbitrairement des faits absents.",
        "Ne produis jamais de chemin local propre à une machine.",
        "N’ajoute jamais de référence de citation interne comme `oaicite`.",
        "N’expose jamais de secret ni de valeur sensible; seuls les noms non sensibles ou les noms de variables peuvent être cités.",
        "Ne cite aucun nom concret de fichier sensible, de plateforme ou de mécanisme d’automatisation à titre d’exemple : il doit être présent dans les faits de cette section et démontré par le profil courant.",
        "Retourne uniquement le Markdown du manuel.",
    )

    FACT_STATUS_RULES = (
        "Interprétation des statuts de faits : `detected` = fait directement démontré et pouvant être présenté comme établi.",
        "`derived` = fait déduit d’éléments compatibles; emploie une formulation prudente et ne le présente jamais comme un comportement testé en fonctionnement.",
        "`configured` = fait provenant du profil ou de la configuration DocForge; présente-le comme règle documentaire ou configuration du pipeline, pas comme comportement applicatif observé.",
        "`unresolved` = fait incomplet; n’invente jamais la partie manquante et signale la limite dans la section appropriée.",
    )

    STYLE_RULES = (
        "Le manuel doit être en français, clair, pédagogique, concret, professionnel et orienté utilisateur.",
        "Ne transcris pas mécaniquement le JSON et ne mentionne pas inutilement les noms internes des dataclasses.",
        "Réduis les répétitions : le démarrage rapide reste court, la référence des commandes porte les détails, et les autres sections évitent de recopier des listes complètes sans nécessité.",
    )

    def common_rules(self) -> tuple[str, ...]:
        return (
            *self.COMMON_RULES,
            *self.FACT_STATUS_RULES,
            *self.STYLE_RULES,
        )

    def profile_rules(
        self,
        blueprint: ManualBlueprint,
    ) -> tuple[str, ...]:
        return ()

    def rules(
        self,
        blueprint: ManualBlueprint,
    ) -> tuple[str, ...]:
        return (
            *self.common_rules(),
            *self.profile_rules(blueprint),
        )

    def build_full_prompt(
        self,
        *,
        knowledge: ManualKnowledge,
        blueprint: ManualBlueprint,
        context_budget: int | None = None,
    ) -> str:
        section_contexts = [
            self.build_section_context(
                knowledge,
                section,
                context_budget=context_budget,
            )
            for section in blueprint.sections
        ]
        blueprint_payload = self._blueprint_payload(blueprint)
        compact_context = {
            "schema_version": knowledge.schema_version,
            "project": {
                "name": knowledge.project.name,
                "profile_type": knowledge.project.profile_type,
            },
            "sections": [
                {
                    "identifier": context.identifier,
                    "title": context.title,
                    "purpose": context.purpose,
                    "estimated_tokens": context.estimated_tokens,
                    "facts": context.projected_facts,
                }
                for context in section_contexts
            ],
        }

        lines = [
            "BEGIN INSTRUCTIONS",
            *self.rules(blueprint or ManualBlueprint(profile_name="generic")),
            *self.additional_guidance(knowledge=knowledge, blueprint=blueprint),
            f"Version du schéma ManualKnowledge : {knowledge.schema_version}.",
            "Structure attendue :",
            json.dumps(
                blueprint_payload,
                indent=2,
                ensure_ascii=False,
            ),
            "END INSTRUCTIONS",
            "",
            "BEGIN COMPACT MANUAL CONTEXT",
            json.dumps(
                compact_context,
                indent=2,
                ensure_ascii=False,
            ),
            "END COMPACT MANUAL CONTEXT",
            "",
        ]
        return "\n".join(lines)

    def build_section_context(
        self,
        knowledge: ManualKnowledge,
        section: ManualSectionDefinition,
        *,
        context_budget: int | None = None,
    ) -> SectionPromptContext:
        payload = knowledge.to_dict()
        projection: dict[str, Any] = {}
        fact_breakdown: dict[str, int] = {}
        missing_fact_paths: list[str] = []
        repeated_fact_paths: list[str] = []
        seen_paths: set[str] = set()

        for path in section.required_fact_paths:
            if path in seen_paths:
                repeated_fact_paths.append(path)
                continue
            seen_paths.add(path)
            value = ManualPromptBuilder._extract_path(payload, path)
            if value is None:
                missing_fact_paths.append(path)
            compact_value = ManualPromptBuilder._compact_path_value(
                path=path,
                value=value,
                payload=payload,
                section=section,
            )
            ManualPromptBuilder._assign_path(projection, path, compact_value)
            fact_breakdown[path] = self.estimate_tokens(json.dumps(compact_value, ensure_ascii=False))

        ManualPromptBuilder._deduplicate_projection(projection)
        ManualPromptBuilder._postprocess_section_projection(section.identifier, projection, payload)

        preview_payload = {
            "identifier": section.identifier,
            "title": section.title,
            "purpose": section.purpose,
            "facts": projection,
        }
        estimated_tokens = self.estimate_tokens(
            json.dumps(preview_payload, ensure_ascii=False)
        )
        effective_budget = context_budget
        if effective_budget is not None and estimated_tokens > effective_budget:
            raise ManualPromptBudgetExceeded(
                section_identifier=section.identifier,
                section_title=section.title,
                estimated_tokens=estimated_tokens,
                context_budget=effective_budget,
                fact_breakdown=fact_breakdown,
                missing_fact_paths=missing_fact_paths,
                repeated_fact_paths=repeated_fact_paths,
            )
        return SectionPromptContext(
            identifier=section.identifier,
            title=section.title,
            purpose=section.purpose,
            projected_facts=projection,
            estimated_tokens=estimated_tokens,
            context_budget=effective_budget,
            fact_breakdown=fact_breakdown,
            missing_fact_paths=missing_fact_paths,
            repeated_fact_paths=repeated_fact_paths,
        )

    def build_section_prompt(
        self,
        *,
        blueprint: ManualBlueprint | None = None,
        section: ManualSectionDefinition,
        projected_facts: dict[str, Any],
        estimated_tokens: int | None = None,
        context_budget: int | None = None,
    ) -> str:
        effective_blueprint = blueprint or ManualBlueprint(
            profile_name="generic"
        )
        if section.identifier in {"cli-reference", "configuration", "security", "protected-documents"}:
            return "BEGIN INSTRUCTIONS\nCette section est entièrement rendue depuis les faits structurés; aucun texte narratif ni syntaxe ne doit être produit.\nEND INSTRUCTIONS\n"
        lines = [
            "BEGIN INSTRUCTIONS",
            *self.rules(effective_blueprint),
            *self.section_guidance(
                blueprint=effective_blueprint,
                section=section,
            ),
            f"Titre de section : {section.title}",
            f"Identifiant de section : {section.identifier}",
            f"But : {section.purpose}",
            (
                f"Budget de contexte estimé : {estimated_tokens}/{context_budget} tokens."
                if estimated_tokens is not None and context_budget is not None
                else f"Taille estimée du contexte : {estimated_tokens} tokens."
                if estimated_tokens is not None
                else None
            ),
            "Produis uniquement la section demandée, sans titre de document global, sans conclusion générale et sans contenu hors sujet.",
            "END INSTRUCTIONS",
            "",
            "BEGIN SECTION FACTS",
            json.dumps(
                {
                    "identifier": section.identifier,
                    "title": section.title,
                    "purpose": section.purpose,
                    "facts": projected_facts,
                },
                indent=2,
                ensure_ascii=False,
            ),
            "END SECTION FACTS",
            "",
        ]
        return "\n".join(str(line) for line in lines if line is not None)

    def additional_guidance(
        self,
        *,
        knowledge: ManualKnowledge,
        blueprint: ManualBlueprint,
    ) -> tuple[str, ...]:
        return ()

    def section_guidance(
        self,
        *,
        blueprint: ManualBlueprint,
        section: ManualSectionDefinition,
    ) -> tuple[str, ...]:
        return ()

    @staticmethod
    def estimate_tokens(value: str) -> int:
        return max(1, ceil(len(value) / 4))

    @staticmethod
    def project_section_facts(
        knowledge: ManualKnowledge,
        section: ManualSectionDefinition,
    ) -> dict[str, Any]:
        return ManualPromptBuilder().build_section_context(
            knowledge,
            section,
            context_budget=None,
        ).projected_facts

    @staticmethod
    def should_omit_section(
        knowledge: ManualKnowledge,
        section: ManualSectionDefinition,
    ) -> bool:
        if not section.omit_if_fact_paths_missing:
            return False

        payload = knowledge.to_dict()
        for path in section.omit_if_fact_paths_missing:
            value = ManualPromptBuilder._extract_path(
                payload,
                path,
            )
            if ManualPromptBuilder._has_content(value):
                return False

        return True

    @staticmethod
    def _blueprint_payload(
        blueprint: ManualBlueprint,
    ) -> dict[str, Any]:
        return {
            "profile_name": blueprint.profile_name,
            "document_identifier": blueprint.document_identifier,
            "document_title": blueprint.document_title,
            "document_audience": blueprint.document_audience,
            "document_kind": blueprint.document_kind,
            "sections": [
                {
                    "identifier": section.identifier,
                    "title": section.title,
                    "purpose": section.purpose,
                    "required_fact_paths": list(section.required_fact_paths),
                    "optional": section.optional,
                    "omit_condition": section.omit_condition,
                    "omit_if_fact_paths_missing": list(
                        section.omit_if_fact_paths_missing
                    ),
                }
                for section in blueprint.sections
            ],
        }

    @staticmethod
    def _workflow_identifiers_for_section(section_identifier: str) -> set[str] | None:
        django_map = {
            "quick-start": {"prepare-dev-config", "start-development", "apply-migrations", "open-frontend"},
            "administration": {"create-admin", "open-django-admin"},
            "operations": {"apply-migrations", "create-admin", "view-logs", "run-tests", "stop-services", "rebuild-images", "prepare-production", "start-production", "backup-database", "restore-database"},
        }
        python_map = {
            "quick-start": {"analyze-project", "detect-profile", "build-project-knowledge"},
            "analyze-project": {"analyze-project"},
            "detect-profile": {"detect-profile"},
            "build-project-knowledge": {"build-project-knowledge"},
            "documentation-generation": {"generate-preview", "review-preview", "generate-with-ollama"},
            "ollama-generation": {"generate-with-ollama"},
            "preview-review": {"review-preview"},
            "apply-documents": {"apply-validated-document", "apply-protected-document"},
            "protected-documents": {"apply-protected-document"},
            "project-management": {"manage-projects"},
            "audits-compliance": {"produce-audit"},
            "troubleshooting": {"produce-audit", "review-preview"},
        }
        return django_map.get(section_identifier) or python_map.get(section_identifier)

    @staticmethod
    def _keep_only_workflows(projection: dict[str, Any], section_identifier: str) -> None:
        allowed = ManualPromptBuilder._workflow_identifiers_for_section(section_identifier)
        workflows = projection.get("workflows")
        if allowed is None or not isinstance(workflows, list):
            return
        projection["workflows"] = [item for item in workflows if item.get("identifier") in allowed]

    @staticmethod
    def _keep_only_commands_for_workflows(projection: dict[str, Any], *, key: str, grouped: bool = False) -> None:
        workflows = projection.get("workflows")
        commands_block = projection.get(key)
        if not isinstance(workflows, list) or not isinstance(commands_block, dict):
            return
        referenced = {command for workflow in workflows for command in workflow.get("commands", [])}
        commands = commands_block.get("commands")
        if isinstance(commands, list):
            commands_block["commands"] = [item for item in commands if item.get("command_path") in referenced]
            return
        if grouped:
            for group_name in ("primary_commands", "advanced_commands"):
                group = commands_block.get(group_name)
                if isinstance(group, list):
                    commands_block[group_name] = [item for item in group if item.get("command_path") in referenced]

    @staticmethod
    def _group_operational_commands(commands: list[dict[str, Any]], *, audience: str = "operator") -> dict[str, Any]:
        allowed = {"template-standard", "app-template", "application-public"} if audience == "operator" else {"developer-public"}
        documentable = [
            item
            for item in commands
            if item.get("visibility") == "public"
            and item.get("documentation_policy") != "exclude"
            and item.get("reference_level") != "omit"
            and item.get("provenance") in allowed
        ]
        primary = [
            item for item in documentable
            if item.get("reference_level") in {None, "primary"}
        ]
        advanced = [
            item for item in documentable
            if item.get("reference_level") in {"advanced", "alias"}
        ]
        excluded = [item for item in commands if item not in documentable]
        by_provenance: dict[str, int] = {}
        reasons: dict[str, int] = {}
        for item in excluded:
            provenance = item.get("provenance") or "unknown"
            by_provenance[provenance] = by_provenance.get(provenance, 0) + 1
            reason = item.get("exclusion_reason") or "Aucune raison d’exclusion documentée."
            reasons[reason] = reasons.get(reason, 0) + 1
        excluded_summary = {
            "total": len(excluded),
            "by_provenance": by_provenance,
            "reasons": [
                {"reason": reason, "count": count}
                for reason, count in sorted(
                    reasons.items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ],
            "commands": [
                {
                    "name": item.get("name"),
                    "provenance": item.get("provenance"),
                    "reason": item.get("exclusion_reason"),
                }
                for item in excluded[:12]
            ],
        }
        return {
            "primary_commands": primary,
            "advanced_commands": advanced,
            "excluded_commands_summary": excluded_summary,
        }

    @staticmethod
    def _filter_user_capabilities(capabilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            item for item in capabilities
            if item.get("permission_condition") != "IsAdminUser"
            and "administr" not in (item.get("label") or "").casefold()
            and "utilisateur" not in (item.get("label") or "").casefold()
        ]

    @staticmethod
    def _filter_admin_capabilities(capabilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            item for item in capabilities
            if item.get("permission_condition") == "IsAdminUser"
            or "administr" in (item.get("label") or "").casefold()
            or "utilisateur" in (item.get("label") or "").casefold()
        ]

    @staticmethod
    def _summarize_capabilities(capabilities: list[dict[str, Any]], *, include_evidence: bool = False) -> list[dict[str, Any]]:
        return [
            {
                "label": item.get("label"),
                "status": item.get("status"),
                "component": item.get("component"),
                "endpoint": item.get("endpoint"),
                "permission_condition": item.get("permission_condition"),
                "confidence": item.get("confidence"),
                **({"evidence": item.get("evidence", [])[:2]} if include_evidence else {}),
            }
            for item in capabilities
        ]

    @staticmethod
    def _user_view_capabilities(
        capabilities: list[dict[str, Any]], *, audience: str,
    ) -> list[dict[str, Any]]:
        """Keep only user-facing capability fields in public contexts."""
        selected = (
            ManualPromptBuilder._filter_admin_capabilities(capabilities)
            if audience == "administrator"
            else ManualPromptBuilder._filter_user_capabilities(capabilities)
        )
        rendered: list[dict[str, Any]] = []
        seen: set[str] = set()
        for index, item in enumerate(selected, start=1):
            label = item.get("label")
            if not isinstance(label, str) or not label.strip():
                continue
            normalized = label.casefold().replace("’", "'").strip()
            if normalized in seen:
                continue
            seen.add(normalized)
            rendered.append({
                "identifier": item.get("identifier") or f"capability-{index}",
                "label": label.strip(),
                "description": item.get("description") if isinstance(item.get("description"), str) else None,
                "audience": audience,
                "status": item.get("status") or "unresolved",
            })
        return rendered

    @staticmethod
    def _postprocess_section_projection(section_identifier: str, projection: dict[str, Any], payload: dict[str, Any] | None = None) -> None:
        ManualPromptBuilder._keep_only_workflows(projection, section_identifier)

        if section_identifier.startswith("user-"):
            # Build every user section from the same canonical facts; individual
            # contexts are only audience-specific slices of this view.
            source = payload or projection
            application = source.get("application", {})
            capabilities = source.get("capabilities", {}).get("capabilities", [])
            react = source.get("react", {})
            django = source.get("django", {})
            endpoints = source.get("service_endpoints", {}).get("endpoints", [])
            security = source.get("security", {})
            frontend_urls = [
                item.get("url") for item in endpoints
                if item.get("service") == "frontend" and item.get("environment") == "prod"
                and item.get("validity") == "valid" and item.get("url")
            ]
            user_capabilities = ManualPromptBuilder._filter_user_capabilities(capabilities)
            admin_capabilities = ManualPromptBuilder._filter_admin_capabilities(capabilities)
            crypto = react.get("crypto", {}) if isinstance(react, dict) else {}
            auth = []
            if isinstance(django, dict):
                auth.extend(django.get("auth_mechanisms", []))
            if isinstance(react, dict):
                auth.extend(react.get("auth_mechanisms", []))
            controls = []
            for item in security.get("controls", []) if isinstance(security, dict) else []:
                if item.get("category") in {"authentification", "secrets"}:
                    controls.append({"category": item.get("category"), "description": item.get("description")})
            canonical = {
                "application": {"name": application.get("name")},
                "production_frontend_urls": frontend_urls[:1],
                "roles": (["utilisateur connecté"] if auth else []) + (["administrateur fonctionnel"] if admin_capabilities else []),
                "capabilities": ManualPromptBuilder._user_view_capabilities(capabilities, audience="user"),
                "administration_capabilities": ManualPromptBuilder._user_view_capabilities(capabilities, audience="administrator"),
                "authentication_required": bool(auth),
                "local_encrypted_vault": bool(crypto.get("detected")),
                "lock_behavior": crypto.get("lock_behavior"),
                "unlock_behavior": crypto.get("unlock_behavior"),
                "recovery": "Aucune procédure de récupération n’est démontrée." if crypto.get("recovery_supported") is None else crypto.get("recovery_supported"),
                "security_guidance": controls,
            }
            slices = {
                "user-presentation": ("application",),
                "user-roles": ("roles",),
                "user-access": ("production_frontend_urls", "authentication_required"),
                "user-authentication": ("authentication_required", "roles"),
                "user-main-features": ("capabilities",),
                "user-application-usage": ("capabilities", "authentication_required"),
                "user-functional-administration": ("administration_capabilities",),
                "user-security": ("local_encrypted_vault", "lock_behavior", "unlock_behavior", "recovery", "security_guidance"),
                "user-troubleshooting": ("authentication_required",),
            }
            projection.clear()
            if section_identifier == "user-limitations":
                projection["limitations"] = {
                    "missing_information": [
                        {"identifier": item.get("identifier"), "category": item.get("category"), "description": item.get("description"), "affected_sections": item.get("affected_sections", [])}
                        for item in source.get("missing_information", []) if isinstance(item, dict)
                    ],
                    "items": [
                        {"identifier": item.get("identifier"), "category": item.get("category"), "description": item.get("description"), "affected_sections": item.get("affected_sections", [])}
                        for item in source.get("limitations", {}).get("items", []) if isinstance(item, dict)
                    ],
                }
            else:
                projection["user_view"] = {key: canonical[key] for key in slices.get(section_identifier, ())}
            return

        if section_identifier.startswith("operator-"):
            # Compose source traces may mention local implementation files. They
            # are not configuration facts unless ManualKnowledge exposes them.
            known_files = {
                item.get("path") for item in (payload or {}).get("configuration", {}).get("files", [])
                if isinstance(item, dict) and item.get("path")
            }
            forbidden = {item for item in {".env.local", "pyproject.toml"} if item not in known_files}
            def scrub(value: Any) -> Any:
                if isinstance(value, str):
                    return None if value in forbidden else value
                if isinstance(value, list):
                    return [clean for item in value if (clean := scrub(item)) is not None]
                if isinstance(value, dict):
                    return {key: clean for key, item in value.items() if (clean := scrub(item)) is not None}
                return value
            projection.clear() if False else None
            for key, value in list(projection.items()):
                projection[key] = scrub(value)
            if section_identifier == "operator-environment-variables":
                variables = projection.get("environment_variables")
                if isinstance(variables, dict):
                    projection["environment_variables"] = {
                        "variables": [
                            {"name": item.get("name"), "sensitive": item.get("sensitive")}
                            for item in variables.get("variables", [])
                        ]
                    }
            if section_identifier in {"operator-make-commands", "operator-start-stop", "operator-migrations-administration", "operator-backup-restore", "operator-deployment"}:
                block = projection.get("operational_commands")
                if isinstance(block, dict) and isinstance(block.get("commands"), list):
                    projection["operational_commands"] = ManualPromptBuilder._group_operational_commands(block["commands"])
            return

        if section_identifier.startswith("developer-"):
            if section_identifier == "developer-development-configuration":
                variables = projection.get("environment_variables")
                if isinstance(variables, dict):
                    projection["environment_variables"] = {
                        "variables": [
                            {"name": item.get("name"), "sensitive": item.get("sensitive")}
                            for item in variables.get("variables", [])
                        ]
                    }
            if section_identifier == "developer-routes-api":
                django = projection.get("django")
                if isinstance(django, dict):
                    django["resolved_routes"] = [
                        item for item in django.get("resolved_routes", [])
                        if item.get("resolution_status") == "resolved"
                    ]
            if section_identifier == "developer-commands":
                block = projection.get("operational_commands")
                if isinstance(block, dict) and isinstance(block.get("commands"), list):
                    projection["operational_commands"] = ManualPromptBuilder._group_operational_commands(block["commands"], audience="developer")
            return

        if section_identifier == "quick-start":
            endpoints = projection.get("service_endpoints", {}).get("endpoints", []) if isinstance(projection.get("service_endpoints"), dict) else []
            if isinstance(endpoints, list):
                preferred = [item for item in endpoints if item.get("environment") == "dev" and item.get("service") == "frontend" and item.get("validity") == "valid"]
                if not preferred:
                    preferred = [item for item in endpoints if item.get("environment") == "dev" and item.get("validity") == "valid"][:2]
                projection["service_endpoints"] = {"endpoints": preferred}
            ManualPromptBuilder._keep_only_commands_for_workflows(projection, key="operational_commands")
            if isinstance(projection.get("missing_information"), list):
                projection["missing_information"] = [item for item in projection["missing_information"] if item.get("category") in {"runtime", "network", "tests"}]

        if section_identifier == "operations":
            ManualPromptBuilder._keep_only_commands_for_workflows(projection, key="operational_commands")
            block = projection.get("operational_commands")
            if isinstance(block, dict) and isinstance(block.get("commands"), list):
                projection["operational_commands"] = ManualPromptBuilder._group_operational_commands(block["commands"])
            if isinstance(projection.get("service_endpoints"), dict):
                projection["service_endpoints"] = {"endpoints": []}

        if section_identifier == "operational-commands-reference":
            block = projection.get("operational_commands")
            if isinstance(block, dict) and isinstance(block.get("commands"), list):
                projection["operational_commands"] = ManualPromptBuilder._group_operational_commands(block["commands"])
            workflows = projection.get("workflows")
            if isinstance(workflows, list):
                projection["workflows"] = [
                    item for item in workflows
                    if item.get("identifier") in {"prepare-dev-config", "start-development", "apply-migrations", "create-admin", "view-logs", "run-tests", "backup-database", "restore-database", "prepare-production", "start-production"}
                ]

        if section_identifier in {"main-features", "application-usage", "audience-roles"}:
            capabilities = projection.get("capabilities", {}).get("capabilities", []) if isinstance(projection.get("capabilities"), dict) else []
            user_caps = ManualPromptBuilder._filter_user_capabilities(capabilities)
            if section_identifier == "audience-roles":
                projection["roles"] = {
                    "user": [item.get("label") for item in user_caps[:10]],
                    "administrator": [item.get("label") for item in ManualPromptBuilder._filter_admin_capabilities(capabilities)[:10]],
                    "operator": [item.get("title") for item in projection.get("workflows", [])[:8]] if isinstance(projection.get("workflows"), list) else [],
                }
            projection["capabilities"] = {
                "capabilities": ManualPromptBuilder._summarize_capabilities(user_caps if section_identifier != "audience-roles" else capabilities[:12], include_evidence=section_identifier == "application-usage")
            }
            react = projection.get("react")
            if isinstance(react, dict):
                react["pages"] = react.get("pages", [])[:6]
                react["navigation_items"] = react.get("navigation_items", [])[:8]
                react["forms"] = react.get("forms", [])[:6]
                react["user_features"] = react.get("user_features", [])[:10]
                react.pop("crypto", None) if section_identifier == "audience-roles" else None
            django = projection.get("django")
            if isinstance(django, dict):
                endpoints = django.get("endpoints", [])
                django["endpoints"] = [item for item in endpoints if item.get("permissions") != ["IsAdminUser"]][:8]
                schemas = django.get("model_schemas", [])
                for schema in schemas:
                    schema["fields"] = [field for field in schema.get("fields", []) if field.get("choices") or field.get("relation") or field.get("required")][:6]

        if section_identifier == "administration":
            capabilities = projection.get("capabilities", {}).get("capabilities", []) if isinstance(projection.get("capabilities"), dict) else []
            projection["capabilities"] = {"capabilities": ManualPromptBuilder._summarize_capabilities(ManualPromptBuilder._filter_admin_capabilities(capabilities), include_evidence=True)}
            django = projection.get("django")
            if isinstance(django, dict):
                django["endpoints"] = [
                    item for item in django.get("endpoints", [])
                    if "IsAdminUser" in item.get("permissions", []) or "/users/" in (item.get("path") or "") or "/auth/" in (item.get("path") or "")
                ][:10]
                django["model_schemas"] = []
            ManualPromptBuilder._keep_only_workflows(projection, section_identifier)

        if section_identifier == "installation-configuration":
            variables = projection.get("environment_variables", {}).get("variables", []) if isinstance(projection.get("environment_variables"), dict) else []
            important = []
            for item in variables:
                values = item.get("values", [])
                differing = len({(entry.get("environment"), entry.get("value")) for entry in values}) > 1
                if item.get("required") or item.get("sensitive") or differing or item.get("name") in {"APP_ENV", "APP_HOST", "FRONT_ORIGIN", "ALLOWED_HOSTS", "CSRF_TRUSTED_ORIGINS", "DJANGO_DEBUG"}:
                    important.append(item)
            projection["environment_variables"] = {"variables": important[:14]}

        if section_identifier == "technical-reference":
            envs = projection.get("environments", {}).get("items", []) if isinstance(projection.get("environments"), dict) else []
            for env in envs:
                env["services"] = [
                    {
                        "name": service.get("name"),
                        "role": service.get("role"),
                        "image": service.get("image"),
                        "ports": service.get("ports", []),
                        "depends_on": service.get("depends_on", []),
                    }
                    for service in env.get("services", [])
                ]
                env["urls"] = env.get("urls", [])[:4]
            django = projection.get("django")
            if isinstance(django, dict):
                for schema in django.get("model_schemas", []):
                    schema["fields"] = [field for field in schema.get("fields", []) if field.get("choices") or field.get("relation") or field.get("unique")][:6]
                django["endpoints"] = [
                    {
                        "path": item.get("path"),
                        "methods": item.get("methods", []),
                        "permissions": item.get("permissions", []),
                        "authentication": item.get("authentication", []),
                    }
                    for item in django.get("endpoints", [])[:12]
                ]
            react = projection.get("react")
            if isinstance(react, dict):
                react["pages"] = react.get("pages", [])[:6]
                react["navigation_items"] = react.get("navigation_items", [])[:6]
                react["user_features"] = [
                    {
                        "label": item.get("label"),
                        "routes": item.get("routes", [])[:2],
                        "api_calls": item.get("api_calls", [])[:3],
                    }
                    for item in react.get("user_features", [])[:8]
                ]
                react["api_calls"] = react.get("api_calls", [])[:12]

        if section_identifier == "security":
            variables = projection.get("environment_variables", {}).get("variables", []) if isinstance(projection.get("environment_variables"), dict) else []
            projection["environment_variables"] = {
                "variables": [
                    {
                        "name": item.get("name"),
                        "required": item.get("required"),
                        "required_by_environment": item.get("required_by_environment", {}),
                        "sensitive": item.get("sensitive"),
                        "description": item.get("description"),
                    }
                    for item in variables
                    if item.get("sensitive")
                ]
            }
            django = projection.get("django")
            if isinstance(django, dict):
                django["installed_apps"] = []
                django["models"] = []
                django["model_schemas"] = []
                django["routers"] = []
                django["endpoints"] = [
                    {
                        "path": item.get("path"),
                        "methods": item.get("methods", []),
                        "permissions": item.get("permissions", []),
                        "authentication": item.get("authentication", []),
                        "custom_authentication": item.get("custom_authentication"),
                        "ownership_controls": item.get("ownership_controls", []),
                        "data_controls": item.get("data_controls", []),
                    }
                    for item in django.get("endpoints", [])
                    if "AllowAny" in item.get("permissions", []) or item.get("custom_authentication") or any(method in {"POST", "PUT", "PATCH", "DELETE"} for method in item.get("methods", []))
                ][:8]
            react = projection.get("react")
            if isinstance(react, dict):
                projection["react"] = {
                    "auth_mechanisms": react.get("auth_mechanisms", []),
                    "crypto": react.get("crypto", {}),
                }
            if isinstance(projection.get("limitations"), dict):
                projection["limitations"]["items"] = [item for item in projection["limitations"].get("items", []) if item.get("category") in {"security", "api", "credentials", "network"}]

        if section_identifier.startswith("template-creation-"):
            template = projection.get("template")
            if isinstance(template, dict):
                template.pop("maintainer_workflows", None)
                if section_identifier == "template-creation-identity":
                    allowed_names = {"APP_NAME", "APP_SLUG", "APP_DEPOT", "APP_NO", "APP_HOST", "ADMIN_USERNAME", "ADMIN_EMAIL", "ADMIN_PASSWORD"}
                    template["placeholders"] = [
                        item for item in template.get("placeholders", [])
                        if item.get("name") in allowed_names
                    ]
                if section_identifier == "template-creation-prerequisites":
                    project_kind = template.get("project_kind")
                    current_state = template.get("current_state")
                    target_state = template.get("target_state")
                    materialization = template.get("materialization")
                    template.clear()
                    template.update({
                        "project_kind": project_kind,
                        "current_state": current_state,
                        "target_state": target_state,
                    })
                    if materialization:
                        template["materialization"] = {
                            "supported": materialization.get("supported"),
                            "entrypoint": materialization.get("entrypoint"),
                            "activation_variable_name": materialization.get("activation_variable_name"),
                            "activation_variable_value": materialization.get("activation_variable_value"),
                            "git_detach_variable_name": materialization.get("git_detach_variable_name"),
                            "git_detach_variable_value": materialization.get("git_detach_variable_value"),
                            "source_metadata_file": materialization.get("source_metadata_file"),
                            "generated_metadata_file": materialization.get("generated_metadata_file"),
                            "metadata_script": materialization.get("metadata_script"),
                            "source_repository_protected": materialization.get("source_repository_protected"),
                        }
                if section_identifier == "template-creation-materialization":
                    template["creator_workflows"] = [
                        item for item in template.get("creator_workflows", [])
                        if item.get("identifier") in {"template-generate-environments", "template-first-init", "template-git-transition", "template-apply-migrations", "template-validate-invariants"}
                    ]
                if section_identifier == "template-creation-start-validate":
                    template["creator_workflows"] = [
                        item for item in template.get("creator_workflows", [])
                        if item.get("identifier") in {"template-select-environment", "template-first-init", "template-validate-invariants", "template-apply-migrations", "template-git-transition"}
                    ]
                if section_identifier in {"template-creation-git-transition", "template-creation-checklist"}:
                    template["creator_workflows"] = [
                        item for item in template.get("creator_workflows", [])
                        if "git" in (item.get("identifier") or "") or any("git" in command.casefold() for command in item.get("commands", []))
                    ] or [
                        item for item in template.get("creator_workflows", [])
                        if item.get("identifier") in {"template-first-init", "template-validate-invariants"}
                    ]
            variables_block = projection.get("environment_variables")
            if isinstance(variables_block, dict) and isinstance(variables_block.get("variables"), list):
                if section_identifier == "template-creation-identity":
                    allowed_names = {"APP_NAME", "APP_SLUG", "APP_DEPOT", "APP_NO", "APP_HOST", "ADMIN_USERNAME", "ADMIN_EMAIL", "ADMIN_PASSWORD"}
                    filtered = []
                    for item in variables_block["variables"]:
                        if item.get("name") not in allowed_names:
                            continue
                        filtered.append({
                            "name": item.get("name"),
                            "required": item.get("required"),
                            "required_by_environment": item.get("required_by_environment", {}),
                            "sensitive": item.get("sensitive"),
                            "description": item.get("description"),
                        })
                    projection["environment_variables"] = {"variables": filtered}
                elif section_identifier == "template-creation-environments":
                    projection["environment_variables"] = {
                        "variables": [
                            {
                                "name": item.get("name"),
                                "required": item.get("required"),
                                "required_by_environment": item.get("required_by_environment", {}),
                                "sensitive": item.get("sensitive"),
                                "comment": item.get("comment"),
                            }
                            for item in variables_block["variables"]
                            if item.get("name") in {"APP_ENV", "APP_HOST", "ADMIN_USERNAME", "ADMIN_EMAIL", "ADMIN_PASSWORD"}
                        ]
                    }
                    if isinstance(template, dict):
                        template["placeholders"] = [
                            item
                            for item in template.get("placeholders", [])
                            if item.get("name") in {"APP_HOST", "ADMIN_USERNAME", "ADMIN_EMAIL", "ADMIN_PASSWORD"}
                        ]
                        creator_workflows = [
                            item
                            for item in template.get("creator_workflows", [])
                            if item.get("identifier") in {"template-select-environment", "template-generate-environments"}
                        ]
                        project_kind = template.get("project_kind")
                        materialization = template.get("materialization")
                        template.clear()
                        template.update({
                            "project_kind": project_kind,
                            "creator_workflows": creator_workflows,
                        })
                        if materialization:
                            template["materialization"] = {
                                "entrypoint": materialization.get("entrypoint"),
                                "skip_startup_variable_name": materialization.get("skip_startup_variable_name"),
                                "skip_startup_audience": materialization.get("skip_startup_audience"),
                                "skip_startup_normal_workflow": materialization.get("skip_startup_normal_workflow"),
                            }
                        template["placeholders"] = [
                            item
                            for item in variables_block.get("variables", [])
                            if item.get("name") in {"APP_HOST", "ADMIN_USERNAME", "ADMIN_EMAIL", "ADMIN_PASSWORD"}
                        ]
                    block = projection.get("operational_commands")
                    if isinstance(block, dict) and isinstance(block.get("commands"), list):
                        block["commands"] = [
                            item for item in block["commands"]
                            if item.get("name") in {"dev", "prod", "init"}
                        ]
                        projection["operational_commands"] = ManualPromptBuilder._group_operational_commands(block["commands"])
                    if isinstance(projection.get("workflows"), list):
                        projection["workflows"] = [
                            item
                            for item in projection["workflows"]
                            if item.get("identifier") in {"prepare-dev-config", "prepare-production"}
                        ]
            if section_identifier == "template-creation-identity" and isinstance(projection.get("missing_information"), list):
                projection["missing_information"] = [
                    item for item in projection["missing_information"]
                    if item.get("category") in {"template", "credentials", "runtime"}
                ]
            if section_identifier == "template-creation-materialization":
                projection["workflows"] = []
                if isinstance(projection.get("limitations"), dict):
                    projection["limitations"]["items"] = [
                        item for item in projection["limitations"].get("items", [])
                        if item.get("category") in {"template", "runtime", "workflow"}
                    ]
            if section_identifier == "template-creation-start-validate":
                projection["workflows"] = []
                if isinstance(projection.get("service_endpoints"), dict):
                    projection["service_endpoints"] = {
                        "endpoints": [
                            item for item in projection["service_endpoints"].get("endpoints", [])
                            if item.get("environment") == "dev" and item.get("validity") == "valid"
                        ][:1]
                    }
                if isinstance(projection.get("profile"), dict):
                    projection["profile"] = {
                        "name": projection["profile"].get("name"),
                        "label": projection["profile"].get("label"),
                    }
            if section_identifier == "template-creation-troubleshooting":
                if isinstance(template, dict):
                    project_kind = template.get("project_kind")
                    materialization = template.get("materialization")
                    target_state = template.get("target_state")
                    template.clear()
                    template.update({
                        "project_kind": project_kind,
                        "target_state": target_state,
                    })
                    if materialization:
                        template["materialization"] = {
                            "activation_command": materialization.get("activation_command"),
                            "maintenance_command": materialization.get("maintenance_command"),
                            "generated_metadata_file": materialization.get("generated_metadata_file"),
                            "metadata_script": materialization.get("metadata_script"),
                            "protections": materialization.get("protections", []),
                        }
                if isinstance(projection.get("missing_information"), list):
                    projection["missing_information"] = [
                        item for item in projection["missing_information"]
                        if item.get("category") in {"template", "runtime", "workflow", "project"}
                    ]
                if isinstance(projection.get("limitations"), dict):
                    projection["limitations"]["items"] = [
                        item for item in projection["limitations"].get("items", [])
                        if item.get("category") in {"template", "runtime", "workflow", "project"}
                    ]
                block = projection.get("operational_commands")
                if isinstance(block, dict) and isinstance(block.get("commands"), list):
                    block["commands"] = [
                        item for item in block["commands"]
                        if item.get("name") in {"init", "check", "dev", "prod"}
                    ]
                    projection["operational_commands"] = ManualPromptBuilder._group_operational_commands(block["commands"])
            block = projection.get("operational_commands")
            if isinstance(block, dict) and isinstance(block.get("commands"), list):
                block["commands"] = [
                    item for item in block["commands"]
                    if item.get("audience") == "creator" and item.get("visibility") == "public"
                ]
                if section_identifier == "template-creation-materialization":
                    allowed_names = {"init", "dev", "prod", "up", "migrate", "check"}
                    block["commands"] = [
                        item for item in block["commands"]
                        if item.get("name") in allowed_names
                    ]
                if section_identifier == "template-creation-start-validate":
                    allowed_names = {"dev", "prod", "up", "migrate", "check"}
                    block["commands"] = [
                        item for item in block["commands"]
                        if item.get("name") in allowed_names
                    ]
                if section_identifier == "template-creation-prerequisites":
                    block["commands"] = [
                        item for item in block["commands"]
                        if item.get("name") in {"init", "dev", "prod"}
                    ]
                projection["operational_commands"] = ManualPromptBuilder._group_operational_commands(block["commands"])

        if section_identifier.startswith("template-maintenance-"):
            template = projection.get("template")
            if isinstance(template, dict):
                template.pop("creator_workflows", None)
                if section_identifier == "template-maintenance-invariants-placeholders":
                    materialization = template.get("materialization")
                    placeholders = [
                        item
                        for item in template.get("placeholders", [])
                        if item.get("name") in {"APP_NAME", "APP_SLUG", "APP_DEPOT", "APP_NO", "__APP_NAME__", "__APP_SLUG__"}
                    ]
                    maintainer_workflows = [
                        item
                        for item in template.get("maintainer_workflows", [])
                        if item.get("identifier") in {"template-maintainer-validate", "template-maintainer-disposable-copy"}
                    ]
                    project_kind = template.get("project_kind")
                    template.clear()
                    template.update({
                        "project_kind": project_kind,
                        "placeholders": placeholders,
                        "maintainer_workflows": maintainer_workflows,
                    })
                    if materialization:
                        template["materialization"] = {
                            "generated_metadata_file": materialization.get("generated_metadata_file"),
                            "metadata_script": materialization.get("metadata_script"),
                            "protections": materialization.get("protections", []),
                        }
            block = projection.get("operational_commands")
            if isinstance(block, dict) and isinstance(block.get("commands"), list):
                block["commands"] = [
                    item for item in block["commands"]
                    if item.get("visibility") == "public"
                    and item.get("provenance") in {"app-template", "template-standard", "application-public"}
                    and item.get("reference_level") != "omit"
                    and item.get("name") != "init"
                ]
                if section_identifier == "template-maintenance-invariants-placeholders":
                    if isinstance(projection.get("environment_variables"), dict):
                        projection["environment_variables"] = {
                            "variables": [
                                {
                                    "name": item.get("name"),
                                    "required": item.get("required"),
                                    "sensitive": item.get("sensitive"),
                                    "required_by_environment": item.get("required_by_environment", {}),
                                }
                                for item in projection["environment_variables"].get("variables", [])
                                if item.get("name") in {"APP_NAME", "APP_SLUG", "APP_DEPOT", "APP_NO", "APP_HOST", "ADMIN_USERNAME", "ADMIN_EMAIL", "ADMIN_PASSWORD"}
                            ]
                        }
                    if isinstance(projection.get("limitations"), dict):
                        projection["limitations"]["items"] = [
                            item for item in projection["limitations"].get("items", [])
                            if item.get("category") in {"template", "runtime", "workflow", "project"}
                        ]
                if section_identifier == "template-maintenance-metadata":
                    if isinstance(template, dict):
                        materialization = template.get("materialization")
                        compact_template = {
                            "project_kind": template.get("project_kind"),
                            "template_id": template.get("template_id"),
                            "template_version": template.get("template_version"),
                            "manifest_source": template.get("manifest_source"),
                            "manifest_verified_targets": template.get("manifest_verified_targets", []),
                            "manifest_missing_targets": template.get("manifest_missing_targets", []),
                            "target_state": template.get("target_state"),
                        }
                        if materialization:
                            compact_template["materialization"] = {
                                "generated_metadata_file": materialization.get("generated_metadata_file"),
                                "metadata_script": materialization.get("metadata_script"),
                            }
                        projection["template"] = compact_template
                    if isinstance(projection.get("limitations"), dict):
                        projection["limitations"]["items"] = [
                            item for item in projection["limitations"].get("items", [])
                            if item.get("category") in {"template", "project"}
                        ]
                if section_identifier == "template-maintenance-scripts-makefile":
                    if isinstance(template, dict):
                        materialization = template.get("materialization")
                        maintainer_workflows = [
                            item
                            for item in template.get("maintainer_workflows", [])
                            if item.get("identifier") in {"template-maintainer-validate", "template-maintainer-disposable-copy", "template-maintainer-update"}
                        ]
                        project_kind = template.get("project_kind")
                        template.clear()
                        template.update({
                            "project_kind": project_kind,
                            "maintainer_workflows": maintainer_workflows,
                        })
                        if materialization:
                            template["materialization"] = {
                                "entrypoint": materialization.get("entrypoint"),
                                "activation_command": materialization.get("activation_command"),
                                "maintenance_command": materialization.get("maintenance_command"),
                                "metadata_script": materialization.get("metadata_script"),
                            }
                    if isinstance(projection.get("workflows"), list):
                        projection["workflows"] = []
                if section_identifier == "template-maintenance-validation-release":
                    if isinstance(template, dict):
                        materialization = template.get("materialization")
                        maintainer_workflows = [
                            item
                            for item in template.get("maintainer_workflows", [])
                            if item.get("identifier") in {"template-maintainer-validate", "template-maintainer-disposable-copy", "template-maintainer-update"}
                        ]
                        project_kind = template.get("project_kind")
                        template.clear()
                        template.update({
                            "project_kind": project_kind,
                            "maintainer_workflows": maintainer_workflows,
                        })
                        if materialization:
                            template["materialization"] = {
                                "maintenance_command": materialization.get("maintenance_command"),
                                "generated_metadata_file": materialization.get("generated_metadata_file"),
                                "metadata_script": materialization.get("metadata_script"),
                                "protections": materialization.get("protections", []),
                            }
                    if isinstance(projection.get("missing_information"), list):
                        projection["missing_information"] = [
                            item for item in projection["missing_information"]
                            if item.get("category") in {"template", "workflow", "project"}
                        ]
                    if isinstance(projection.get("limitations"), dict):
                        projection["limitations"]["items"] = [
                            item for item in projection["limitations"].get("items", [])
                            if item.get("category") in {"template", "workflow", "project"}
                        ]
                    if isinstance(projection.get("workflows"), list):
                        projection["workflows"] = []
                projection["operational_commands"] = ManualPromptBuilder._group_operational_commands(block["commands"])
                if section_identifier in {"template-maintenance-metadata", "template-maintenance-canonical-targets", "template-maintenance-scripts-makefile"}:
                    for key in ("primary_commands", "advanced_commands"):
                        projection["operational_commands"][key] = [
                            {
                                "name": item.get("name"),
                                "command_path": item.get("command_path"),
                                "provenance": item.get("provenance"),
                                "reference_level": item.get("reference_level"),
                                "documentation_policy": item.get("documentation_policy"),
                                "destructive": item.get("destructive"),
                            }
                            for item in projection["operational_commands"].get(key, [])
                        ]

        if section_identifier == "troubleshooting":
            if isinstance(projection.get("missing_information"), list):
                projection["missing_information"] = [item for item in projection["missing_information"] if item.get("category") in {"runtime", "tests", "api", "network", "backup"}]
            block = projection.get("operational_commands")
            if isinstance(block, dict) and isinstance(block.get("commands"), list):
                diag = [
                    item for item in block.get("commands", [])
                    if item.get("category") in {"diagnostic", "logs", "tests"}
                    and item.get("visibility") == "public"
                    and item.get("documentation_policy") != "exclude"
                ]
                projection["operational_commands"] = {"commands": diag[:8]}
            if isinstance(projection.get("service_endpoints"), dict):
                projection["service_endpoints"] = {"endpoints": [item for item in projection["service_endpoints"].get("endpoints", []) if item.get("validity") != "valid" or item.get("resolution_status") != "resolved"][:6]}

        if section_identifier in {"documentation-generation", "project-management", "apply-documents", "audits-compliance", "analyze-project", "detect-profile", "build-project-knowledge", "ollama-generation", "preview-review", "protected-documents", "quick-start", "troubleshooting"}:
            workflows = projection.get("workflows")
            commands = projection.get("commands")
            if isinstance(workflows, list) and isinstance(commands, list):
                referenced = {command for workflow in workflows for command in workflow.get("commands", [])}
                projection["commands"] = [item for item in commands if item.get("command_path") in referenced][:10]


    @staticmethod
    def _compact_path_value(
        *,
        path: str,
        value: Any,
        payload: dict[str, Any],
        section: ManualSectionDefinition,
    ) -> Any:
        if path == "commands":
            return ManualPromptBuilder._compact_commands(
                value,
                include_advanced=section.identifier in {"operational-commands-reference", "operations"},
            )
        if path == "operational_commands":
            commands = value.get("commands", []) if isinstance(value, dict) else []
            return {
                "commands": ManualPromptBuilder._compact_operational_commands(
                    commands,
                    include_internal=section.identifier == "technical-reference",
                )
            }
        if path == "workflows":
            return ManualPromptBuilder._compact_workflows(value)
        if path == "limitations":
            return ManualPromptBuilder._compact_limitations(value)
        if path == "missing_information":
            return ManualPromptBuilder._compact_missing_information(value)
        if path == "environment_variables":
            return ManualPromptBuilder._compact_environment_variables(value)
        if path == "environments":
            return ManualPromptBuilder._compact_environments(value)
        if path == "service_endpoints":
            return ManualPromptBuilder._compact_service_endpoints(value)
        if path == "django":
            return ManualPromptBuilder._compact_django(value, section.identifier)
        if path == "react":
            return ManualPromptBuilder._compact_react(value, section.identifier)
        if path == "capabilities":
            return ManualPromptBuilder._compact_capabilities(value)
        if path == "template":
            return ManualPromptBuilder._compact_template(value, section.identifier)
        if path == "source_traceability":
            return ManualPromptBuilder._compact_source_traceability(value)
        if path == "installation":
            return ManualPromptBuilder._compact_installation(value)
        return ManualPromptBuilder._compact_generic(value)

    @staticmethod
    def _compact_installation(value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        compact = {
            "summary": value.get("summary"),
            "prerequisites": value.get("prerequisites", []),
            "steps": [
                {
                    "title": step.get("title"),
                    "command": step.get("command"),
                }
                for step in value.get("steps", [])
            ],
        }
        return ManualPromptBuilder._compact_generic(compact)

    @staticmethod
    def _compact_commands(
        value: Any,
        *,
        include_advanced: bool,
    ) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        items = []
        for command in value:
            if command.get("reference_level") == "omit":
                continue
            if command.get("reference_level") == "advanced" and not include_advanced:
                continue
            items.append(
                {
                    "name": command.get("name"),
                    "command_path": command.get("command_path"),
                    "group": command.get("group"),
                    "audience": command.get("audience"),
                    "reference_level": command.get("reference_level"),
                    "provenance": command.get("provenance"),
                    "documentation_policy": command.get("documentation_policy"),
                    "environment": command.get("environment"),
                    "destructive": command.get("destructive"),
                    "destructive_effects": command.get("destructive_effects", []),
                    "help": command.get("help"),
                    "parameters": [
                        {
                            "name": parameter.get("name"),
                            "required": parameter.get("required"),
                            "description": (
                                parameter.get("description")
                                or parameter.get("help")
                            ),
                            "example": parameter.get("example"),
                            "allowed_values": parameter.get("allowed_values", []),
                        }
                        for parameter in command.get("parameters", [])
                    ],
                }
            )
        return ManualPromptBuilder._compact_generic(items)

    @staticmethod
    def _compact_operational_commands(
        commands: Any,
        *,
        include_internal: bool,
    ) -> list[dict[str, Any]]:
        if not isinstance(commands, list):
            return []
        items = []
        for command in commands:
            if not include_internal and command.get("visibility") != "public":
                continue
            items.append(
                {
                    "name": command.get("name"),
                    "category": command.get("category"),
                    "command_path": command.get("command_path"),
                    "audience": command.get("audience"),
                    "reference_level": command.get("reference_level"),
                    "environment": command.get("environment"),
                    "visibility": command.get("visibility"),
                    "documented": command.get("documented"),
                    "provenance": command.get("provenance"),
                    "documentation_policy": command.get("documentation_policy"),
                    "exclusion_reason": command.get("exclusion_reason"),
                    "prerequisites": command.get("prerequisites", []),
                    "destructive": command.get("destructive"),
                    "destructive_effects": command.get("destructive_effects", []),
                    "parameters": [
                        {
                            "name": parameter.get("name"),
                            "required": parameter.get("required"),
                            "description": (
                                parameter.get("description")
                                or parameter.get("help")
                            ),
                            "example": parameter.get("example"),
                            "allowed_values": parameter.get("allowed_values", []),
                            "origin": parameter.get("origin"),
                        }
                        for parameter in command.get("parameters", [])
                    ],
                }
            )
        return ManualPromptBuilder._compact_generic(items)

    @staticmethod
    def _compact_workflows(value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return ManualPromptBuilder._compact_generic(
            [
                {
                    "identifier": item.get("identifier"),
                    "title": item.get("title"),
                    "summary": item.get("summary"),
                    "commands": item.get("commands", []),
                    "operational_status": item.get("operational_status"),
                    "notes": item.get("notes", []),
                }
                for item in value
            ]
        )

    @staticmethod
    def _compact_missing_information(value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return [
            {
                "identifier": item.get("identifier"),
                "category": item.get("category"),
                "severity": item.get("severity"),
                "description": item.get("description"),
                "affected_sections": item.get("affected_sections", []),
                "sources": ManualPromptBuilder._compact_source_list(item.get("sources", [])),
            }
            for item in value
        ]

    @staticmethod
    def _compact_limitations(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {"items": []}
        items = []
        for item in value.get("items", []):
            if isinstance(item, str):
                items.append({
                    "identifier": None,
                    "category": "limitation",
                    "severity": "warning",
                    "description": item,
                    "affected_sections": [],
                    "sources": [],
                })
                continue
            items.append(
                {
                    "identifier": item.get("identifier"),
                    "category": item.get("category"),
                    "severity": item.get("severity"),
                    "description": item.get("description"),
                    "affected_sections": item.get("affected_sections", []),
                    "sources": ManualPromptBuilder._compact_source_list(item.get("sources", [])),
                }
            )
        return {"items": items}

    @staticmethod
    def _compact_environments(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {"items": []}
        items = []
        for item in value.get("items", []):
            items.append(
                {
                    "name": item.get("name"),
                    "compose_file": item.get("compose_file"),
                    "env_files": item.get("env_files", []),
                    "urls": item.get("urls", []),
                    "services": [
                        {
                            "name": service.get("name"),
                            "role": service.get("role"),
                            "image": service.get("image"),
                            "ports": service.get("ports", []),
                            "depends_on": service.get("depends_on", []),
                            "networks": service.get("networks", []),
                            "volumes": service.get("volumes", []),
                        }
                        for service in item.get("services", [])
                    ],
                }
            )
        return ManualPromptBuilder._compact_generic({"items": items})

    @staticmethod
    def _compact_environment_variables(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {"variables": []}
        variables = []
        for item in value.get("variables", []):
            values = item.get("values", [])
            differing_values = len({(entry.get("environment"), entry.get("value")) for entry in values}) > 1
            variables.append(
                {
                    "name": item.get("name"),
                    "scope": item.get("scope"),
                    "required": item.get("required"),
                    "required_by_environment": item.get("required_by_environment", {}),
                    "sensitive": item.get("sensitive"),
                    "default_value": item.get("default_value"),
                    "description": item.get("description"),
                    "comment": item.get("comment"),
                    "values": [
                        {
                            "environment": entry.get("environment"),
                            "value": entry.get("value"),
                            "source": entry.get("source"),
                        }
                        for entry in values
                    ] if differing_values or item.get("comment") else [],
                }
            )
        return ManualPromptBuilder._compact_generic({"variables": variables})

    @staticmethod
    def _compact_service_endpoints(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {"endpoints": []}
        endpoints = [
            {
                "environment": endpoint.get("environment"),
                "service": endpoint.get("service"),
                "url": endpoint.get("url"),
                "validity": endpoint.get("validity"),
                "resolution_status": endpoint.get("resolution_status"),
            }
            for endpoint in value.get("endpoints", [])
        ]
        return {"endpoints": endpoints}

    @staticmethod
    def _compact_django(value: Any, section_identifier: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {}
        unresolved_routes = [
            {
                "relative_path": route.get("relative_path"),
                "mount_path": route.get("mount_path"),
                "full_path": route.get("full_path"),
                "route_type": route.get("route_type"),
                "resolution_status": route.get("resolution_status"),
            }
            for route in value.get("resolved_routes", [])
            if route.get("resolution_status") != "resolved"
        ]
        endpoints = [
            {
                "path": endpoint.get("path"),
                "methods": endpoint.get("methods", []),
                "view": endpoint.get("view"),
                "permissions": endpoint.get("permissions", []),
                "authentication": endpoint.get("authentication", []),
                "actions": endpoint.get("actions", []),
                "route_parameters": endpoint.get("route_parameters", []),
                "ownership_controls": endpoint.get("ownership_controls", []),
                "data_controls": endpoint.get("data_controls", []),
                "custom_authentication": endpoint.get("custom_authentication"),
            }
            for endpoint in value.get("endpoints", [])
        ]
        compact = {
            "settings_module": value.get("settings_module"),
            "urlconf_module": value.get("urlconf_module"),
            "installed_apps": value.get("installed_apps", []),
            "admin_enabled": value.get("admin_enabled"),
            "routers": value.get("routers", []),
            "auth_mechanisms": value.get("auth_mechanisms", []),
            "models": value.get("models", []),
            "model_schemas": [
                {
                    "name": schema.get("name"),
                    "fields": [
                        {
                            "name": field.get("name"),
                            "field_type": field.get("field_type"),
                            "required": field.get("required"),
                            "nullable": field.get("nullable"),
                            "blank": field.get("blank"),
                            "default": field.get("default"),
                            "choices": field.get("choices", []),
                            "relation": field.get("relation"),
                            "unique": field.get("unique"),
                            "on_delete": field.get("on_delete"),
                        }
                        for field in schema.get("fields", [])
                    ],
                }
                for schema in value.get("model_schemas", [])
            ],
            "endpoints": endpoints,
        }
        if section_identifier in {"technical-reference", "troubleshooting", "developer-routes-api"}:
            compact["unresolved_routes"] = unresolved_routes
            if section_identifier == "developer-routes-api":
                compact["resolved_routes"] = [
                    {
                        "full_path": route.get("full_path"),
                        "methods": route.get("methods", []),
                        "permissions": route.get("permissions", []),
                        "resolution_status": route.get("resolution_status"),
                    }
                    for route in value.get("resolved_routes", [])
                    if route.get("resolution_status") == "resolved"
                ]
            compact["database_engine"] = value.get("database_engine")
            compact["database_engines"] = value.get("database_engines", [])
            compact["database_configuration"] = value.get("database_configuration", [])
        return ManualPromptBuilder._compact_generic(compact)

    @staticmethod
    def _compact_react(value: Any, section_identifier: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {}
        compact = {
            "entry_point": value.get("entry_point"),
            "routes": value.get("routes", []),
            "pages": value.get("pages", []),
            "navigation_items": value.get("navigation_items", []),
            "forms": value.get("forms", []),
            "user_features": value.get("user_features", []),
            "auth_mechanisms": value.get("auth_mechanisms", []),
            "crypto": value.get("crypto", {}),
        }
        if section_identifier in {"technical-reference", "security", "developer-architecture", "developer-frontend", "developer-authentication", "developer-security"}:
            compact["api_calls"] = value.get("api_calls", [])
            compact["environment_variables"] = value.get("environment_variables", [])
        return ManualPromptBuilder._compact_generic(compact)

    @staticmethod
    def _compact_capabilities(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {"capabilities": []}
        return {
            "capabilities": [
                {
                    "label": capability.get("label"),
                    "status": capability.get("status"),
                    "component": capability.get("component"),
                    "endpoint": capability.get("endpoint"),
                    "permission_condition": capability.get("permission_condition"),
                    "confidence": capability.get("confidence"),
                    "evidence": capability.get("evidence", [])[:4],
                }
                for capability in value.get("capabilities", [])
            ]
        }

    @staticmethod
    def _compact_source_traceability(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {"items": {}}
        return {
            "items": {
                key: {
                    "status": item.get("status"),
                    "sources": ManualPromptBuilder._compact_source_list(item.get("sources", [])),
                }
                for key, item in value.get("items", {}).items()
            }
        }

    @staticmethod
    def _compact_template(value: Any, section_identifier: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {}
        compact = {
            "project_kind": value.get("project_kind"),
            "template_id": value.get("template_id"),
            "origin_template_id": value.get("origin_template_id"),
            "template_version": value.get("template_version"),
            "origin_template_version": value.get("origin_template_version"),
            "base_profile": value.get("base_profile"),
            "manifest_source": value.get("manifest_source"),
            "current_state": value.get("current_state"),
            "target_state": value.get("target_state"),
            "materialization": value.get("materialization"),
            "manifest_verified_targets": value.get("manifest_verified_targets", []),
            "manifest_missing_targets": value.get("manifest_missing_targets", []),
            "missing_steps": value.get("missing_steps", []),
            "risks": value.get("risks", []),
            "placeholders": [
                {
                    "name": item.get("name"),
                    "kind": item.get("kind"),
                    "description": item.get("description"),
                    "required": item.get("required"),
                }
                for item in value.get("placeholders", [])
            ],
            "creator_workflows": [
                {
                    "identifier": item.get("identifier"),
                    "title": item.get("title"),
                    "commands": item.get("commands", []),
                    "preconditions": item.get("preconditions", []),
                    "expected_results": item.get("expected_results", []),
                    "personalization_points": item.get("personalization_points", []),
                    "risks": item.get("risks", []),
                    "missing_information": item.get("missing_information", []),
                }
                for item in value.get("creator_workflows", [])
            ],
            "maintainer_workflows": [
                {
                    "identifier": item.get("identifier"),
                    "title": item.get("title"),
                    "commands": item.get("commands", []),
                    "preconditions": item.get("preconditions", []),
                    "expected_results": item.get("expected_results", []),
                    "risks": item.get("risks", []),
                    "missing_information": item.get("missing_information", []),
                }
                for item in value.get("maintainer_workflows", [])
            ],
        }
        if section_identifier.startswith("template-creation-"):
            compact.pop("maintainer_workflows", None)
        if section_identifier.startswith("template-maintenance-"):
            compact.pop("creator_workflows", None)
        return ManualPromptBuilder._compact_generic(compact)

    @staticmethod
    def _deduplicate_projection(projection: dict[str, Any]) -> None:
        missing = projection.get("missing_information")
        limitations = projection.get("limitations")
        if isinstance(missing, list) and isinstance(limitations, dict):
            missing_ids = {item.get("identifier") for item in missing}
            items = limitations.get("items", [])
            limitations["items"] = [
                item
                for item in items
                if item.get("identifier") not in missing_ids
            ]

    @staticmethod
    def _compact_source_list(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        items = [str(item) for item in value if item]
        if len(items) <= 3:
            return items
        return [*items[:3], f"… (+{len(items) - 3} autres sources)"]

    @staticmethod
    def _compact_generic(value: Any) -> Any:
        if isinstance(value, dict):
            compact: dict[str, Any] = {}
            for key, item in value.items():
                if key in {"sources", "source_paths"}:
                    compact[key] = ManualPromptBuilder._compact_source_list(item)
                    continue
                compact[key] = ManualPromptBuilder._compact_generic(item)
            return compact
        if isinstance(value, list):
            return [ManualPromptBuilder._compact_generic(item) for item in value]
        return value

    @staticmethod
    def _has_content(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (list, tuple, set, dict)):
            return bool(value)
        if isinstance(value, str):
            return bool(value.strip())
        return True

    @staticmethod
    def _extract_path(
        payload: dict[str, Any],
        path: str,
    ) -> Any:
        current: Any = payload

        for part in path.split("."):
            if isinstance(current, list):
                if not current:
                    return []
                return current
            if not isinstance(current, dict):
                return None
            current = current.get(part)

        return current

    @staticmethod
    def _assign_path(
        projection: dict[str, Any],
        path: str,
        value: Any,
    ) -> None:
        parts = path.split(".")
        current = projection

        for part in parts[:-1]:
            next_value = current.get(part)

            if not isinstance(next_value, dict):
                next_value = {}
                current[part] = next_value

            current = next_value

        current[parts[-1]] = value


class PythonCliManualPromptBuilder(ManualPromptBuilder):
    PYTHON_CLI_RULES = (
        "Le manuel concerne l’outil CLI analysé et ses commandes réelles, sans extrapolation sur des intégrations non démontrées.",
        "Ne transforme jamais les commandes de maintenance interne ou de génération documentaire en commandes d’usage courant si le projet ne les expose pas comme telles.",
    )

    PYTHON_CLI_SECTION_RULES = {
        "cli-reference": (
            "Dans cette section, décris séparément chaque option ou argument documenté lorsque des paramètres structurés sont fournis.",
            "Un exemple de commande combinant plusieurs options ne suffit jamais à expliquer séparément l’effet de chacune d’elles.",
            "N’attribue à une option que la sémantique explicitement fournie par `commands.parameters.description`, dérivée du code détecté, sans interprétation supplémentaire.",
        ),
    }

    def profile_rules(
        self,
        blueprint: ManualBlueprint,
    ) -> tuple[str, ...]:
        return self.PYTHON_CLI_RULES

    def section_guidance(
        self,
        *,
        blueprint: ManualBlueprint,
        section: ManualSectionDefinition,
    ) -> tuple[str, ...]:
        return self.PYTHON_CLI_SECTION_RULES.get(section.identifier, ())


class DjangoReactManualPromptBuilder(ManualPromptBuilder):
    DJANGO_REACT_RULES = (
        "Le manuel concerne l’application analysée ou le dépôt modèle analysé, jamais DocForge comme produit utilisateur.",
        "Les commandes DocForge ne sont pas des commandes d’utilisation de l’application analysée.",
        "Formule prudemment toute capacité marquée `derived` et ne la présente jamais comme validée en fonctionnement.",
        "N’affiche jamais une valeur secrète.",
        "Omet toute procédure dont une commande critique est absente.",
        "Utilise `missing_information` et `limitations.items` comme source prioritaire pour la section des limites, sans reconstruire arbitrairement les absences depuis le JSON brut.",
        "Les mentions locales d’une information manquante doivent rester limitées aux cas où elles sont nécessaires à la sécurité ou à l’exécution; consolide le reste dans la section finale des limites.",
        "Lorsqu’un conflit structuré est présent dans `conflicts`, présente-le clairement, n’arbitre jamais entre les valeurs contradictoires et ne décris pas comme validée une procédure affectée par ce conflit.",
        "Pour les routes Django, utilise uniquement `full_path` lorsque `resolution_status` vaut `resolved`; ne compose jamais manuellement un chemin public à partir d’une route relative non résolue.",
        "Une URL syntaxiquement invalide ou contenant une interpolation déséquilibrée ne doit jamais être présentée comme URL d’accès opérationnelle.",
        "Pour les endpoints, utilise les méthodes, permissions, mécanismes d’authentification, paramètres de route et sources rattachés à chaque endpoint; n’attribue jamais des permissions globales à tous les endpoints ou à tous les utilisateurs.",
        "Respecte `workflows.operational_status` : un workflow `requires-context` ne doit jamais être présenté comme immédiatement exécutable et doit garder son contexte manquant explicite.",
        "Lorsqu’une cible alias délègue à des prérequis démontrés, décris l’alias à partir de cette délégation au lieu d’inventer un corps absent.",
        "Ne présente jamais `make check` comme une suite de tests lorsqu’il correspond à une vérification d’invariants ou de diagnostic.",
        "Associe `make migrate` à la création ou mise à jour de l’administrateur uniquement si la chaîne démontrée vers `python manage.py ensure_admin` est explicitement présente dans ManualKnowledge.",
        "Pour les commandes Make, respecte les paramètres structurés de `commands.parameters`, leur caractère facultatif et leurs exemples; n’invente ni nouveaux paramètres ni nouvelles valeurs de service.",
        "Les paramètres internes d’une commande ne doivent jamais être présentés comme arguments utilisateur; n’utilise que les paramètres structurés réellement exposés dans `commands.parameters`.",
        "Pour la base de données, respecte les contextes fournis par ManualKnowledge, par exemple exécution vs test; ne transforme pas automatiquement une différence de contexte en contradiction.",
        "Les métadonnées de `django.models.fields` priment sur toute intuition: type, `required`, `null`, `blank`, `default`, `choices`, relation, unicité et autres contraintes détectées doivent être utilisées telles quelles.",
        "Pour `react.crypto`, décris uniquement l’implémentation détectée et jamais une garantie de sécurité, un audit, une récupération existante ou un modèle zero knowledge non démontré.",
        "En mode strict, n’ajoute pas de recommandations générales de sécurité si elles ne figurent pas dans ManualKnowledge.",
        "Le document final doit rester lisible: le démarrage rapide est court, l’exploitation détaille les procédures nécessaires, et la référence des commandes évite de dupliquer les listes dans toutes les sections.",
        "Les helpers internes du Makefile ne doivent pas encombrer la référence principale; privilégie les commandes publiques, documentées ou réellement utilisées dans les workflows démontrés.",
        "N’expose pas dans le manuel final un vocabulaire interne ni les identifiants techniques des structures de génération.",
        "Transforme toujours les identifiants techniques de limites ou d’informations manquantes en phrases lisibles, par exemple `PROJECT-VERSION-MISSING` devient une phrase telle que la version de l’application n’est pas indiquée.",
        "Lorsque `conflicts` est vide, n’ajoute pas une phrase de remplissage disant qu’aucune contradiction n’est signalée.",
    )

    USER_GUIDE_RULES = (
        "Le manuel ne doit pas commencer par Docker, les variables d’environnement ou l’infrastructure; il doit d’abord expliquer l’application et ce que l’utilisateur peut faire.",
        "Distingue clairement trois publics lorsque les faits le permettent : utilisateur de l’application, administrateur applicatif et exploitant.",
        "Décris la section d’utilisation avec un langage fonctionnel orienté utilisateur; n’invente ni boutons, ni messages affichés, ni captures d’écran, ni parcours non démontrés.",
        "Si `capabilities.capabilities` contient des capacités backend ou frontend démontrées, conserve des sections visibles pour les fonctionnalités principales et l’utilisation de l’application.",
        "Chaque catégorie d’information doit avoir une section principale : présentation des services dans `Architecture et référence technique`, URLs dev/prod dans `Installation et configuration`, séquence minimale dans `Démarrage rapide`, détail des commandes et paramètres Make dans `Référence des commandes`, permissions dans `Administration` ou `API`, chiffrement dans `Architecture et référence technique` ou `Sécurité`, sauvegarde et restauration dans `Exploitation`, limitations dans `Limites des informations disponibles`.",
        "Ne recopie pas intégralement la liste des commandes, des services, des variables, des URLs ou des endpoints dans plusieurs sections; ailleurs, ne fais qu’une mention brève quand c’est nécessaire à la compréhension.",
        "Le démarrage rapide doit contenir uniquement la sélection du développement, l’initialisation, le démarrage, les migrations si elles sont nécessaires, et l’URL principale; n’y explique pas tous les services, toutes les variables ni toute l’architecture.",
        "La section de référence des commandes doit contenir les détails opérationnels : commande, fonction, environnement, paramètres facultatifs, statut opérationnel et contexte requis. Les autres sections ne doivent pas recopier cette référence.",
    )

    TEMPLATE_CREATION_RULES = (
        "Rédige un guide destiné au développeur qui crée une nouvelle application à partir du dépôt modèle.",
        "Ne présente pas ce document comme un guide utilisateur d’application métier.",
        "Explique clairement le rôle du modèle, ses limites et les étapes réellement démontrées pour matérialiser une nouvelle application.",
        "Toute opération Git destructive ou irréversible, notamment le détachement de l’historique ou la suppression de `.git`, doit être signalée explicitement avec un avertissement clair.",
        "Les placeholders comme `APP_NAME`, `APP_SLUG`, `APP_DEPOT`, `APP_NO`, `APP_HOST`, `ADMIN_USERNAME`, `ADMIN_EMAIL` et `ADMIN_PASSWORD` doivent être décrits comme valeurs à personnaliser, jamais comme valeurs finales à recopier telles quelles.",
        "Ne présente pas `DOCFORGE_SKIP_STARTUP=1` comme une procédure normale d’initialisation si ce mécanisme n’est démontré que pour les tests ou la maintenance.",
        "Distingue la matérialisation de l’application, la génération des environnements, la génération des secrets et la validation finale avec `make check`.",
    )

    TEMPLATE_MAINTENANCE_RULES = (
        "Rédige un guide destiné au mainteneur du dépôt modèle, pas au créateur d’une instance métier ni à l’utilisateur final.",
        "Explique l’architecture du squelette, le rôle du manifeste template, la politique documentaire des cibles Makefile et les validations avant publication d’une nouvelle version.",
        "Sépare strictement la maintenance du modèle des étapes de création d’une application à partir de ce modèle.",
        "Décris les placeholders, les scripts standards, `make check`, `make update` et les procédures de validation démontrées sans inventer de workflow de publication externe.",
        "Mets en évidence les risques de divergence entre le modèle, son manifeste, les cibles Makefile et les applications déjà matérialisées.",
    )

    MULTI_DOCUMENT_RULES = {
        "user-guide": (
            "Ce guide est destiné à l’utilisateur et à l’administrateur fonctionnel. N’y mentionne ni commandes Make, ni Docker Compose, ni déploiement, ni noms de variables d’environnement, ni liste exhaustive de routes API.",
            "N’expose l’architecture technique que lorsqu’elle aide directement à comprendre l’accès, l’authentification ou une fonction démontrée.",
        ),
        "operator-guide": (
            "Ce guide est destiné à l’exploitant. Les tableaux déterministes de services, cibles Make, variables et documents protégés constituent la référence technique à conserver telle quelle.",
            "Ne transforme jamais les noms de variables de configuration en valeurs ou en secrets.",
        ),
        "developer-reference": (
            "Cette référence est destinée au développement et à la maintenance. Les routes résolues et les invariants démontrés y sont documentés, sans inventer de contrat API ou de procédure de mise en production.",
            "Les noms de variables sont autorisés; leurs valeurs ne le sont jamais.",
        ),
    }

    SECTION_RULES = {
        "quick-start": (
            "Cette section reste courte et ne contient que la séquence minimale pour démarrer l’application et atteindre l’URL principale.",
            "N’y recopie pas l’inventaire complet des services, variables, paramètres Make ou procédures d’exploitation.",
        ),
        "application-usage": (
            "Cette section vient avant l’infrastructure détaillée et doit privilégier les usages concrets de l’interface: connexion, recherche, consultation, création, modification, guide, vérification de clé, import/export de clé, révélation de valeur et changement de thème lorsque ces comportements sont démontrés.",
            "Décris le comportement fonctionnel plutôt que de lister tous les endpoints complets; garde la référence API détaillée pour la section technique.",
        ),
        "administration": (
            "Cette section distingue la gestion des utilisateurs, les permissions administratives, l’administration Django et, si elle est démontrée, la création ou mise à jour du compte administrateur.",
        ),
        "installation-configuration": (
            "Cette section regroupe développement et production dans un même chapitre comparatif au lieu de créer plusieurs sections principales redondantes.",
            "Les URLs, ports et fichiers d’environnement doivent être présentés ici comme section principale, puis seulement rappelés brièvement ailleurs si nécessaire.",
        ),
        "operations": (
            "Cette section regroupe démarrage, arrêt, migrations, journaux, diagnostic, tests, sauvegarde, restauration, mise à jour et reconstruction sous un même chapitre d’exploitation.",
            "Lorsque des paramètres ou contextes détaillés existent, renvoie conceptuellement à la référence des commandes au lieu de recopier toute la table ici.",
        ),
        "technical-reference": (
            "Cette section sert de référence technique principale pour l’architecture, les services Docker, la base de données, l’API et le chiffrement côté client.",
            "Les sections d’ouverture du manuel ne doivent pas répéter ici tout son contenu technique.",
        ),
        "security": (
            "Dans cette section, distingue strictement contrôles détectés, risques structurés et limites d’information; ne transforme pas les faits cryptographiques en garantie de sécurité.",
        ),
        "operational-commands-reference": (
            "Dans cette section, les détails complets des commandes et paramètres peuvent apparaître; les autres sections doivent éviter de recopier cette référence mot pour mot.",
        ),
        "limitations": (
            "Dans cette section, consolide les éléments de `missing_information` et `limitations.items` sans les répéter inutilement ni en inventer de nouveaux.",
            "Remplace les identifiants techniques par des phrases lisibles destinées au lecteur final.",
        ),
        "template-creation-git-transition": (
            "Cette section doit expliciter les avertissements liés au détachement Git et au remplacement de l’historique du dépôt source.",
        ),
        "template-creation-checklist": (
            "Cette section reste courte, orientée vérification finale, et ne recopie pas tout le détail des commandes déjà documentées plus haut.",
        ),
        "template-maintenance-validation-release": (
            "Cette section regroupe les validations avant publication d’une nouvelle version du modèle et les contrôles de cohérence avec les applications matérialisées.",
        ),
    }

    def profile_rules(
        self,
        blueprint: ManualBlueprint,
    ) -> tuple[str, ...]:
        if blueprint.document_kind == "template-creation-guide":
            return (*self.DJANGO_REACT_RULES, *self.TEMPLATE_CREATION_RULES)
        if blueprint.document_kind == "template-maintenance-guide":
            return (*self.DJANGO_REACT_RULES, *self.TEMPLATE_MAINTENANCE_RULES)
        if (
            blueprint.document_identifier != "manual"
            and blueprint.document_kind in self.MULTI_DOCUMENT_RULES
        ):
            return (*self.DJANGO_REACT_RULES, *self.MULTI_DOCUMENT_RULES[blueprint.document_kind])
        return (*self.DJANGO_REACT_RULES, *self.USER_GUIDE_RULES)

    def additional_guidance(
        self,
        *,
        knowledge: ManualKnowledge,
        blueprint: ManualBlueprint,
    ) -> tuple[str, ...]:
        common = (
            "Le flux de DocForge s’arrête à la production de `manual-knowledge.json`, des contextes de section et du prompt de rédaction; tu ne dois pas prétendre que DocForge a rédigé ou validé le document final.",
            "Les URLs résolues peuvent être citées; lorsqu’une URL ou un port reste symbolique dans ManualKnowledge, conserve cette forme au lieu d’inventer une valeur.",
        )
        if blueprint.document_kind == "template-creation-guide":
            return common + (
                "Le document doit rester orienté vers la création d’une nouvelle application à partir du modèle, avec une checklist finale explicite.",
            )
        if blueprint.document_kind == "template-maintenance-guide":
            return common + (
                "Le document doit distinguer clairement les commandes et validations du mainteneur de celles du créateur d’application.",
            )
        return common + (
            "Le document peut rester unique, mais fais apparaître sans ambiguïté les sections destinées aux utilisateurs, aux administrateurs et aux exploitants.",
        )

    def section_guidance(
        self,
        *,
        blueprint: ManualBlueprint,
        section: ManualSectionDefinition,
    ) -> tuple[str, ...]:
        return self.SECTION_RULES.get(section.identifier, ())
