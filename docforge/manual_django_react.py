from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from docforge.knowledge import ProjectKnowledge
from docforge.manual_knowledge import (
    ManualCommand,
    ManualCommandParameter,
    ManualConfiguration,
    ManualConflict,
    ManualConflictFact,
    ManualDocumentationPolicy,
    ManualFactSource,
    ManualInstallation,
    ManualInstallationStep,
    ManualKnowledge,
    ManualKnowledgeBuilder,
    ManualKnowledgeGap,
    ManualLimitations,
    ManualProject,
    ManualSecurity,
    ManualSourceTraceability,
    ManualWorkflow,
)
from docforge.profiles import ProjectProfile


class DjangoReactManualKnowledgeBuilder(ManualKnowledgeBuilder):
    def build(
        self,
        *,
        project_root: Path,
        knowledge: ProjectKnowledge,
        profile_instance: ProjectProfile,
    ) -> ManualKnowledge:
        commands = self._build_operational_commands(knowledge)
        workflows = self._build_workflows(knowledge)
        missing_information = self._missing_information(knowledge)
        conflicts = self._build_conflicts(knowledge)
        limitations = self._build_limitations(
            knowledge,
            missing_information,
            conflicts,
        )

        return ManualKnowledge(
            schema_version=self.SCHEMA_VERSION,
            project=ManualProject(
                name=knowledge.application.name or knowledge.identity.name,
                version=knowledge.pyproject.version,
                description=(
                    knowledge.pyproject.description
                    or "Application Django/React auto-hébergée."
                ),
                profile_type=knowledge.profile.name,
                python_requires=knowledge.pyproject.requires_python,
                cli_entry_point=None,
                source=ManualFactSource(
                    status="detected",
                    sources=(
                        "ProjectKnowledge.application",
                        "ProjectKnowledge.profile",
                    ),
                ),
            ),
            profile={
                "name": knowledge.profile.name,
                "label": knowledge.profile.label,
                "description": knowledge.profile.description,
                "confidence": knowledge.profile.confidence,
                "evidence": list(knowledge.profile.evidence),
                "source": asdict(
                    ManualFactSource(
                        status="detected",
                        sources=("ProfileDetector",),
                    )
                ),
            },
            installation=self._build_installation(knowledge),
            application={
                "name": knowledge.application.name,
                "category": knowledge.application.category,
                "backend_framework": knowledge.application.backend_framework,
                "frontend_framework": knowledge.application.frontend_framework,
                "prepared_by": "DocForge",
                "source_paths": list(knowledge.application.source_paths),
            },
            environments={
                "items": [asdict(item) for item in knowledge.environments.items]
            },
            operational_commands={
                "commands": [
                    {
                        "name": item.name,
                        "category": item.category,
                        "command_path": item.command,
                        "invocation": item.command,
                        "target": item.target,
                        "body": list(item.body),
                        "prerequisites": list(item.prerequisites),
                        "environments": list(item.environments),
                        "help": item.help_text,
                        "phony": item.phony,
                        "documented": item.documented,
                        "visibility": item.visibility,
                        "provenance": item.provenance,
                        "documentation_policy": item.documentation_policy,
                        "exclusion_reason": item.exclusion_reason,
                        "provenance_evidence": list(item.provenance_evidence),
                        "manifest_source": item.manifest_source,
                        "audience": self._command_audience(knowledge, item),
                        "reference_level": self._command_reference_level(item),
                        "destructive": self._command_is_destructive(item),
                        "destructive_effects": self._command_destructive_effects(item),
                        "environment": list(item.environments),
                        "parameters": [
                            {
                                "name": parameter.name,
                                "required": parameter.required,
                                "example": parameter.example,
                                "description": parameter.description,
                                "allowed_values": self._parameter_allowed_values(knowledge, parameter),
                                "origin": parameter.origin,
                                "source": parameter.source,
                            }
                            for parameter in item.parameters
                        ],
                        "source": {
                            "status": "detected",
                            "sources": [item.source],
                            "notes": [],
                        },
                    }
                    for item in knowledge.operational_commands.commands
                ]
            },
            environment_variables={
                "variables": [
                    asdict(item)
                    for item in knowledge.environment_variables.variables
                ]
            },
            service_endpoints={
                "endpoints": [
                    asdict(item)
                    for item in knowledge.service_endpoints.endpoints
                ]
            },
            django=asdict(knowledge.django),
            react=asdict(knowledge.react),
            capabilities={
                "capabilities": [
                    asdict(item)
                    for item in knowledge.capabilities.capabilities
                ]
            },
            template=asdict(knowledge.template),
            missing_information=missing_information,
            conflicts=conflicts,
            commands=commands,
            workflows=workflows,
            configuration=self._build_configuration(knowledge),
            security=self._build_security(knowledge),
            limitations=ManualLimitations(
                items=limitations,
                source=ManualFactSource(
                    status="derived",
                    sources=("ProjectKnowledge", "django-react"),
                ),
            ),
            documentation_policy=self._build_documentation_policy(
                profile_instance
            ),
            source_traceability=self._build_source_traceability(knowledge),
        )

    def _build_installation(
        self,
        knowledge: ProjectKnowledge,
    ) -> ManualInstallation:
        prerequisites: list[str] = []
        if knowledge.deployment.compose_files:
            prerequisites.append("Docker et Docker Compose")
        if any(
            command.name == "init"
            for command in knowledge.operational_commands.commands
        ):
            prerequisites.append(
                "Le dépôt doit être initialisé via les scripts et cibles Make détectés."
            )

        steps = []
        for command_name, title in (
            ("dev", "Sélectionner l’environnement de développement"),
            ("init", "Initialiser les fichiers locaux requis"),
            ("up", "Démarrer les services"),
            ("migrate", "Appliquer les migrations détectées"),
        ):
            command = self._find_command(knowledge, command_name)
            if command is None:
                continue
            steps.append(
                ManualInstallationStep(
                    title=title,
                    command=command.command,
                    source=ManualFactSource(
                        status="detected",
                        sources=(command.source,),
                    ),
                )
            )

        return ManualInstallation(
            summary="Préparation locale de l’application à partir des commandes opérationnelles détectées.",
            prerequisites=prerequisites,
            steps=steps,
            source=ManualFactSource(
                status="derived",
                sources=self._command_sources(knowledge),
            ),
        )

    def _build_operational_commands(
        self,
        knowledge: ProjectKnowledge,
    ) -> list[ManualCommand]:
        commands: list[ManualCommand] = []
        for item in knowledge.operational_commands.commands:
            if item.visibility != "public" or item.documentation_policy == "exclude":
                continue
            commands.append(
                ManualCommand(
                    name=item.name,
                    command_path=item.command,
                    invocation=item.command,
                    group=item.category,
                    help=item.help_text or f"Commande opérationnelle catégorie {item.category}.",
                    visibility=item.visibility,
                    documented=item.documented,
                    audience=self._command_audience(knowledge, item),
                    reference_level=self._command_reference_level(item),
                    provenance=item.provenance,
                    documentation_policy=item.documentation_policy,
                    exclusion_reason=item.exclusion_reason,
                    provenance_evidence=list(item.provenance_evidence),
                    destructive=self._command_is_destructive(item),
                    destructive_effects=self._command_destructive_effects(item),
                    environment=list(item.environments),
                    prerequisites=list(item.prerequisites),
                    parameters=[
                        ManualCommandParameter(
                            name=parameter.name,
                            kind="make-variable",
                            required=parameter.required,
                            example=parameter.example,
                            description=parameter.description,
                            allowed_values=self._parameter_allowed_values(knowledge, parameter),
                            origin=parameter.origin,
                            source=parameter.source,
                        )
                        for parameter in item.parameters
                    ],
                    examples=[item.command],
                    source=ManualFactSource(
                        status="detected",
                        sources=(item.source,),
                    ),
                )
            )
        return commands

    def _command_audience(self, knowledge: ProjectKnowledge, command) -> str:
        if command.visibility != "public":
            return "internal"
        if knowledge.template.project_kind == "application-template":
            if command.name in {"init", "dev", "prod", "up", "down", "restart", "rebuild", "logs", "ps", "migrate", "backup", "restore", "check"}:
                return "creator"
            if command.name in {"update"}:
                return "maintainer"
        if command.category in {"tests", "diagnostic"}:
            return "operator"
        if command.category in {"backup", "restore", "migrations", "build", "startup", "shutdown", "restart", "environment"}:
            return "operator"
        if command.name in {"createsuperuser", "create-admin"}:
            return "administrator"
        return "operator"

    def _command_reference_level(self, command) -> str:
        if command.visibility != "public" or command.documentation_policy == "exclude":
            return "omit"
        if command.documentation_policy == "advanced-reference":
            return "advanced"
        if command.documentation_policy in {"quick-start", "main-reference"}:
            return "primary"
        if command.prerequisites and not command.body:
            return "alias"
        if command.category in {"tests", "diagnostic", "backup", "restore", "migrations", "build"}:
            return "advanced"
        return "primary"

    @staticmethod
    def _command_is_destructive(command) -> bool:
        return bool(DjangoReactManualKnowledgeBuilder._command_destructive_effects(command))

    @staticmethod
    def _command_destructive_effects(command) -> list[str]:
        effects: list[str] = []
        body = "\n".join(command.body).casefold()
        if " down" in f" {body}" or command.category == "shutdown":
            effects.append("Arrêt des services actifs")
        if "psql" in body or command.category == "restore":
            effects.append("Modification ou écrasement potentiel des données PostgreSQL")
        if "rm " in body or "rm -" in body:
            effects.append("Suppression de fichiers")
        if "build" in body or command.category == "build":
            effects.append("Reconstruction des images ou services")
        return effects

    def _parameter_allowed_values(self, knowledge: ProjectKnowledge, parameter) -> list[str]:
        if parameter.name != "SERVICE":
            return []
        services = sorted({service.name for environment in knowledge.environments.items for service in environment.services})
        if not services:
            return []
        return services

    def _build_workflows(
        self,
        knowledge: ProjectKnowledge,
    ) -> list[ManualWorkflow]:
        workflows: list[ManualWorkflow] = []

        def add_if_complete(
            identifier: str,
            title: str,
            summary: str,
            required: list[str],
            *,
            operational_status: str = "operational",
            notes: list[str] | None = None,
        ) -> None:
            commands = []
            sources = []
            for name in required:
                item = self._find_command(knowledge, name)
                if item is None:
                    return
                commands.append(item.command)
                sources.append(item.source)
            workflows.append(
                ManualWorkflow(
                    identifier=identifier,
                    title=title,
                    summary=summary,
                    commands=commands,
                    operational_status=operational_status,
                    notes=notes or [],
                    source=ManualFactSource(
                        status="derived",
                        sources=tuple(dict.fromkeys(sources)),
                    ),
                )
            )

        add_if_complete(
            "prepare-dev-config",
            "Préparer la configuration de développement",
            "Sélectionner le mode dev puis initialiser les fichiers d’environnement.",
            ["dev", "init"],
        )
        add_if_complete(
            "start-development",
            "Démarrer le développement",
            "Sélectionner l’environnement dev puis démarrer les services.",
            ["dev", "up"],
        )
        add_if_complete(
            "apply-migrations",
            "Appliquer les migrations",
            "Exécuter la procédure de migration détectée.",
            ["migrate"],
        )

        create_admin = self._create_admin_workflow(knowledge)
        if create_admin is not None:
            workflows.append(create_admin)

        frontend_workflow = self._frontend_open_workflow(knowledge)
        if frontend_workflow is not None:
            workflows.append(frontend_workflow)

        admin_workflow = self._admin_open_workflow(knowledge)
        if admin_workflow is not None:
            workflows.append(admin_workflow)

        add_if_complete(
            "view-logs",
            "Consulter les journaux",
            "Afficher les logs des services actifs.",
            ["logs"],
        )

        tests_workflow = self._tests_workflow(knowledge)
        if tests_workflow is not None:
            workflows.append(tests_workflow)

        add_if_complete(
            "stop-services",
            "Arrêter les services",
            "Arrêter les services de l’environnement actif.",
            ["down"],
        )
        add_if_complete(
            "rebuild-images",
            "Reconstruire les images",
            "Reconstruire les images Docker de l’environnement actif.",
            ["rebuild"],
        )
        add_if_complete(
            "prepare-production",
            "Préparer la production",
            "Sélectionner prod puis initialiser les fichiers requis.",
            ["prod", "init"],
        )
        add_if_complete(
            "start-production",
            "Démarrer la production",
            "Sélectionner prod puis démarrer les services.",
            ["prod", "up"],
        )
        add_if_complete(
            "backup-database",
            "Sauvegarder la base",
            "Créer une sauvegarde PostgreSQL via la commande détectée.",
            ["backup"],
        )
        add_if_complete(
            "restore-database",
            "Restaurer la base",
            "Restaurer une sauvegarde PostgreSQL via la commande détectée.",
            ["restore"],
        )

        return workflows

    def _build_configuration(
        self,
        knowledge: ProjectKnowledge,
    ) -> ManualConfiguration:
        env_files = sorted(
            {
                env_file
                for environment in knowledge.environments.items
                for env_file in environment.env_files
                if env_file != ".env.local"
            }
        )
        settings_files = list(knowledge.django.settings_files)
        files = [
            {
                "path": path,
                "scope": "project",
                "exists": True,
                "tracked_candidate": True,
                "description": "Fichier de configuration détecté pour l’application.",
            }
            for path in [*env_files, *settings_files]
        ]

        config_sources = sorted(
            {
                *env_files,
                *settings_files,
                *[
                    environment.compose_file
                    for environment in knowledge.environments.items
                ],
            }
        )

        return ManualConfiguration(
            user_config_root=".",
            project_state_root=".docforge",
            project_config_file=".env",
            report_root=".docforge/manual/generated",
            files=files,
            environment_variables=[
                item.name
                for item in knowledge.environment_variables.variables
            ],
            ignored_paths=[".env.local"],
            source=ManualFactSource(
                status="derived",
                sources=tuple(config_sources),
            ),
        )

    def _build_security(
        self,
        knowledge: ProjectKnowledge,
    ) -> ManualSecurity:
        controls: list[dict[str, Any]] = []
        if knowledge.django.auth_mechanisms:
            controls.append(
                {
                    "identifier": "APP-SEC-001",
                    "category": "authentification",
                    "description": "Des mécanismes d’authentification ont été détectés côté backend et/ou frontend.",
                    "evidence": sorted(set(knowledge.django.auth_mechanisms)),
                }
            )
        if knowledge.django.admin_enabled:
            admin_sources = sorted(
                {
                    route.sources[0]
                    for route in knowledge.django.resolved_routes
                    if route.relative_path == "admin/" and route.sources
                }
            ) or list(knowledge.django.settings_files)
            controls.append(
                {
                    "identifier": "APP-SEC-002",
                    "category": "administration",
                    "description": "Une interface d’administration Django est détectée et doit être réservée aux comptes autorisés.",
                    "evidence": admin_sources,
                }
            )
        if any(
            item.sensitive
            for item in knowledge.environment_variables.variables
        ):
            controls.append(
                {
                    "identifier": "APP-SEC-003",
                    "category": "secrets",
                    "description": "Des variables sensibles sont requises et leurs valeurs ne doivent pas être publiées dans le manuel.",
                    "evidence": [item.name for item in knowledge.environment_variables.variables if item.sensitive],
                }
            )

        risks: list[dict[str, Any]] = []
        debug_var = self._environment_variable(knowledge, "DJANGO_DEBUG")
        if debug_var is not None:
            prod_values = [
                value.value
                for value in debug_var.values
                if value.environment == "prod" and value.value is not None
            ]
            if any(str(value).strip().lower() in {"1", "true", "yes", "on"} for value in prod_values):
                risks.append(
                    {
                        "identifier": "DJANGO-DEBUG-PROD-DETECTED",
                        "category": "configuration",
                        "severity": "warning",
                        "description": "DJANGO_DEBUG semble activé dans au moins un contexte de production détecté.",
                        "sources": sorted(set(debug_var.sources)),
                    }
                )
        if not any(endpoint.validity == "valid" for endpoint in knowledge.service_endpoints.endpoints):
            risks.append(
                {
                    "identifier": "NO-VALID-SERVICE-ENDPOINT",
                    "category": "network",
                    "severity": "warning",
                    "description": "Aucune URL de service valide n’a pu être confirmée statiquement.",
                    "sources": sorted({endpoint.source for endpoint in knowledge.service_endpoints.endpoints}),
                }
            )
        for endpoint in knowledge.django.endpoints:
            write_methods = {method for method in endpoint.methods if method in {"POST", "PUT", "PATCH", "DELETE"}}
            if not write_methods or "AllowAny" not in endpoint.permissions:
                continue
            if endpoint.custom_authentication:
                risks.append(
                    {
                        "identifier": "WRITE-ENDPOINT-ALLOWANY-CUSTOM-AUTH",
                        "category": "api",
                        "severity": "warning",
                        "description": f"L’endpoint {endpoint.path or endpoint.relative_path} accepte des écritures avec AllowAny et s’appuie sur une authentification personnalisée qui doit être vérifiée manuellement.",
                        "sources": sorted(set(endpoint.sources)),
                    }
                )
                continue
            if endpoint.authentication:
                continue
            risks.append(
                {
                    "identifier": "WRITE-ENDPOINT-ALLOWANY-NO-AUTH",
                    "category": "api",
                    "severity": "critical",
                    "description": f"L’endpoint {endpoint.path or endpoint.relative_path} accepte des écritures avec AllowAny sans mécanisme d’authentification démontré.",
                    "sources": sorted(set(endpoint.sources)),
                }
            )

        admin_fallback_risk = self._detect_admin_fallback_risk(knowledge)
        if admin_fallback_risk is not None:
            risks.append(admin_fallback_risk)

        security_sources = sorted(
            {
                *knowledge.django.source_paths,
                *knowledge.react.source_paths,
                *[
                    source
                    for variable in knowledge.environment_variables.variables
                    for source in variable.sources
                ],
            }
        )

        return ManualSecurity(
            protected_documents=[],
            controls=controls,
            risks=risks,
            validation_commands=[],
            source=ManualFactSource(
                status="derived",
                sources=tuple(security_sources),
            ),
        )

    @staticmethod
    def _build_documentation_policy(
        profile_instance: ProjectProfile,
    ) -> ManualDocumentationPolicy:
        return ManualDocumentationPolicy(
            required_documents=[],
            optional_documents=[],
            deterministic_documents=[],
            protected_documents=[],
            source=ManualFactSource(
                status="configured",
                sources=(f"profile:{profile_instance.name}",),
            ),
        )

    def _missing_information(
        self,
        knowledge: ProjectKnowledge,
    ) -> list[ManualKnowledgeGap]:
        missing: list[ManualKnowledgeGap] = []

        def add(
            identifier: str,
            category: str,
            description: str,
            *,
            affected_sections: list[str],
            sources: list[str],
            severity: str = "warning",
        ) -> None:
            missing.append(
                ManualKnowledgeGap(
                    identifier=identifier,
                    category=category,
                    severity=severity,
                    description=description,
                    affected_sections=affected_sections,
                    sources=sources,
                )
            )

        if not knowledge.pyproject.version:
            add(
                "PROJECT-VERSION-MISSING",
                "project",
                "La version applicative n’a pas été trouvée dans les métadonnées détectées.",
                affected_sections=["presentation", "installation"],
                sources=["pyproject.toml", "ProjectKnowledge.application"],
            )
        if not knowledge.pyproject.requires_python:
            add(
                "PYTHON-VERSION-MISSING",
                "runtime",
                "La version minimale de Python n’est pas déterminable statiquement.",
                affected_sections=["installation", "prerequisites"],
                sources=["pyproject.toml", *knowledge.django.settings_files],
            )
        add(
            "NODE-VERSION-MISSING",
            "runtime",
            "La version minimale de Node.js n’est pas documentée de manière fiable dans les faits structurés disponibles.",
            affected_sections=["installation", "prerequisites", "frontend"],
            sources=["frontend/package.json", "frontend/Dockerfile.dev"],
        )
        add(
            "DOCKER-COMPOSE-VERSION-MISSING",
            "runtime",
            "La version minimale de Docker Compose n’est pas explicitement documentée.",
            affected_sections=["installation", "prerequisites", "deployment"],
            sources=[
                *[item.compose_file for item in knowledge.environments.items],
                "Makefile",
            ],
        )
        if not self._has_backend_test_command(knowledge):
            add(
                "BACKEND-TEST-COMMAND-MISSING",
                "tests",
                "Aucune commande opérationnelle de tests backend n’a été démontrée.",
                affected_sections=["tests", "backend"],
                sources=["Makefile", *knowledge.django.source_paths],
            )
        add(
            "INTEGRATION-TEST-DETAILS-MISSING",
            "tests",
            "Les détails des tests d’intégration ne sont pas disponibles dans les faits structurés générés.",
            affected_sections=["tests", "api"],
            sources=[*knowledge.django.source_paths, *knowledge.react.source_paths],
        )
        if knowledge.django.endpoints:
            add(
                "API-SCHEMA-MISSING",
                "api",
                "Les schémas détaillés de requête et de réponse des endpoints ne sont pas disponibles.",
                affected_sections=["api"],
                sources=sorted({source for endpoint in knowledge.django.endpoints for source in endpoint.sources}),
            )
            add(
                "API-ERROR-CODES-MISSING",
                "api",
                "La matrice complète des codes d’erreur API n’est pas structurée de manière exhaustive.",
                affected_sections=["api", "troubleshooting"],
                sources=sorted({source for endpoint in knowledge.django.endpoints for source in endpoint.sources}),
            )
        visibility_fields = [
            field
            for model in knowledge.django.model_schemas
            for field in model.fields
            if field.name == "visibility"
        ]
        if visibility_fields and not any(field.choices for field in visibility_fields):
            add(
                "VISIBILITY-VALUES-MISSING",
                "data-model",
                "Les valeurs possibles du champ visibility ne sont pas démontrées dans les faits structurés.",
                affected_sections=["api", "interface-usage"],
                sources=sorted({field.source for field in visibility_fields}),
            )
        if knowledge.react.crypto.detected and knowledge.react.crypto.recovery_supported is None:
            add(
                "VAULT-RECOVERY-PROCEDURE-MISSING",
                "security",
                "La procédure de récupération du coffre privé n’est pas démontrée dans le code analysé.",
                affected_sections=["security", "authentication-accounts"],
                sources=list(knowledge.react.crypto.source_paths or knowledge.react.source_paths),
            )
        if any(command.name == "backup" for command in knowledge.operational_commands.commands) or any(
            script.database_engine == "PostgreSQL"
            for script in knowledge.operational_commands.scripts
        ):
            add(
                "BACKUP-RETENTION-POLICY-MISSING",
                "backup",
                "La stratégie de rétention des sauvegardes n’est pas démontrée.",
                affected_sections=["backup-restore", "operations"],
                sources=[
                    script.path
                    for script in knowledge.operational_commands.scripts
                    if script.name in {"backup-db.sh", "restore-db.sh"}
                ] or ["Makefile"],
            )
        return missing

    def _build_conflicts(
        self,
        knowledge: ProjectKnowledge,
    ) -> list[ManualConflict]:
        runtime_engines = [
            item
            for item in knowledge.django.database_engines
            if "test" not in item.context.casefold()
        ]
        postgres_sources = [
            environment.compose_file
            for environment in knowledge.environments.items
            for service in environment.services
            if service.role == "database"
            and (
                (service.image or "").casefold().startswith("postgres")
                or service.name == "db"
            )
        ]
        postgres_sources.extend(
            script.path
            for script in knowledge.operational_commands.scripts
            if script.database_engine == "PostgreSQL"
        )
        if (
            runtime_engines
            and any("sqlite" in item.engine for item in runtime_engines)
            and postgres_sources
        ):
            return [
                ManualConflict(
                    identifier="DATABASE-ENGINE-CONFLICT",
                    category="database",
                    severity="critical",
                    description="Le moteur Django détecté reste SQLite pour l’exécution courante alors que l’orchestration et les opérations de données utilisent PostgreSQL.",
                    facts=[
                        ManualConflictFact(
                            value=runtime_engines[0].engine,
                            sources=[runtime_engines[0].source],
                        ),
                        ManualConflictFact(
                            value="PostgreSQL",
                            sources=sorted(set(postgres_sources)),
                        ),
                    ],
                    affected_sections=[
                        "database",
                        "migrations",
                        "backup",
                        "restore",
                        "production",
                    ],
                )
            ]
        return []

    def _build_limitations(
        self,
        knowledge: ProjectKnowledge,
        missing_information: list[ManualKnowledgeGap],
        conflicts: list[ManualConflict],
    ) -> list[ManualKnowledgeGap]:
        items = list(missing_information)
        for conflict in conflicts:
            items.append(
                ManualKnowledgeGap(
                    identifier=f"LIMIT-{conflict.identifier}",
                    category=conflict.category,
                    severity=conflict.severity,
                    description=conflict.description,
                    affected_sections=list(conflict.affected_sections),
                    sources=[
                        source
                        for fact in conflict.facts
                        for source in fact.sources
                    ],
                )
            )
        unresolved_sources = sorted(
            {
                source
                for route in knowledge.django.resolved_routes
                if route.resolution_status != "resolved"
                for source in route.sources
            }
        )
        if unresolved_sources:
            items.append(
                ManualKnowledgeGap(
                    identifier="UNRESOLVED-ROUTES",
                    category="api",
                    severity="warning",
                    description="Certaines routes Django ont été détectées sans pouvoir être résolues en chemins publics complets.",
                    affected_sections=["api"],
                    sources=unresolved_sources,
                )
            )
        invalid_endpoints = [
            endpoint
            for endpoint in knowledge.service_endpoints.endpoints
            if endpoint.validity != "valid"
        ]
        if invalid_endpoints:
            items.append(
                ManualKnowledgeGap(
                    identifier="INVALID-SERVICE-ENDPOINTS",
                    category="network",
                    severity="warning",
                    description="Certaines URLs de service détectées sont invalides ou incomplètes et ne doivent pas être présentées comme points d’accès opérationnels.",
                    affected_sections=["installation", "operations", "technical-reference"],
                    sources=sorted({endpoint.source for endpoint in invalid_endpoints}),
                )
            )
        return items

    def _build_source_traceability(
        self,
        knowledge: ProjectKnowledge,
    ) -> ManualSourceTraceability:
        env_sources = sorted(
            {
                source
                for item in knowledge.environment_variables.variables
                for source in item.sources
            }
        )
        command_sources = sorted(
            {
                *[command.source for command in knowledge.operational_commands.commands],
                *[script.path for script in knowledge.operational_commands.scripts],
            }
        )
        capability_sources = sorted(
            {
                *knowledge.django.source_paths,
                *knowledge.react.source_paths,
            }
        )
        return ManualSourceTraceability(
            items={
                "application": ManualFactSource(
                    status="detected",
                    sources=tuple(knowledge.application.source_paths),
                ),
                "environments": ManualFactSource(
                    status="detected",
                    sources=tuple(
                        sorted(
                            {
                                *[
                                    item.compose_file
                                    for item in knowledge.environments.items
                                ],
                                *[
                                    source
                                    for item in knowledge.environments.items
                                    for source in item.source_paths
                                ],
                            }
                        )
                    ),
                ),
                "operational_commands": ManualFactSource(
                    status="detected",
                    sources=tuple(command_sources),
                ),
                "environment_variables": ManualFactSource(
                    status="detected",
                    sources=tuple(env_sources),
                ),
                "django": ManualFactSource(
                    status="detected",
                    sources=tuple(knowledge.django.source_paths),
                ),
                "react": ManualFactSource(
                    status="detected",
                    sources=tuple(knowledge.react.source_paths),
                ),
                "capabilities": ManualFactSource(
                    status="derived",
                    sources=tuple(capability_sources),
                ),
                "prepared_by": ManualFactSource(
                    status="configured",
                    sources=("DocForge manual pipeline",),
                ),
            }
        )

    def _create_admin_workflow(
        self,
        knowledge: ProjectKnowledge,
    ) -> ManualWorkflow | None:
        migrate_command = self._find_command(knowledge, "migrate")
        if migrate_command is not None and self._workflow_proves_create_admin(knowledge):
            return ManualWorkflow(
                identifier="create-admin",
                title="Créer un administrateur",
                summary="Créer ou mettre à jour le compte administrateur via la procédure démontrée.",
                commands=[migrate_command.command],
                operational_status="operational",
                notes=[],
                source=ManualFactSource(
                    status="derived",
                    sources=(migrate_command.source,),
                ),
            )

        for command_name in ("createsuperuser", "create-admin"):
            command = self._find_command(knowledge, command_name)
            if command is not None:
                return ManualWorkflow(
                    identifier="create-admin",
                    title="Créer un administrateur",
                    summary="La création d’un administrateur est exposée par une commande opérationnelle détectée.",
                    commands=[command.command],
                    operational_status="operational",
                    notes=[],
                    source=ManualFactSource(
                        status="derived",
                        sources=(command.source,),
                    ),
                )

        internal_commands = [
            command
            for command in knowledge.django.create_admin_commands
            if command.strip()
        ]
        if internal_commands:
            return ManualWorkflow(
                identifier="create-admin",
                title="Créer un administrateur",
                summary="Une commande interne de création d’administrateur a été détectée, mais son contexte d’exécution complet n’est pas démontré.",
                commands=[internal_commands[0]],
                operational_status="requires-context",
                notes=[
                    "La commande interne doit être exécutée dans le contexte Django approprié et n’est pas automatiquement reliée à une cible Make démontrée."
                ],
                source=ManualFactSource(
                    status="derived",
                    sources=tuple(knowledge.django.source_paths),
                ),
            )
        return None

    def _frontend_open_workflow(
        self,
        knowledge: ProjectKnowledge,
    ) -> ManualWorkflow | None:
        endpoint = self._select_endpoint(
            knowledge,
            service="frontend",
            environment="dev",
            require_valid=True,
        )
        if endpoint is None:
            return None
        up_command = self._find_command(knowledge, "up")
        dev_command = self._find_command(knowledge, "dev")
        if up_command is None or dev_command is None:
            return None
        return ManualWorkflow(
            identifier="open-frontend",
            title="Ouvrir le frontend",
            summary="Démarrer les services puis ouvrir le frontend détecté.",
            commands=[dev_command.command, up_command.command],
            operational_status="operational",
            notes=[f"URL détectée : {endpoint.url}"],
            source=ManualFactSource(
                status="derived",
                sources=tuple(dict.fromkeys([dev_command.source, up_command.source, endpoint.source])),
            ),
        )

    def _admin_open_workflow(
        self,
        knowledge: ProjectKnowledge,
    ) -> ManualWorkflow | None:
        if not knowledge.django.admin_enabled:
            return None
        up_command = self._find_command(knowledge, "up")
        if up_command is None:
            return None
        endpoint = self._select_admin_endpoint(knowledge)
        if endpoint is not None:
            return ManualWorkflow(
                identifier="open-django-admin",
                title="Accéder à l’administration Django",
                summary="Démarrer les services puis ouvrir l’administration détectée.",
                commands=[up_command.command],
                operational_status="operational",
                notes=[f"URL détectée : {endpoint.url}"],
                source=ManualFactSource(
                    status="derived",
                    sources=tuple(dict.fromkeys([up_command.source, endpoint.source])),
                ),
            )
        if any(route.relative_path == "admin/" for route in knowledge.django.resolved_routes):
            return ManualWorkflow(
                identifier="open-django-admin",
                title="Accéder à l’administration Django",
                summary="L’administration Django est détectée, mais son URL publique complète n’est pas résolue de manière fiable.",
                commands=[up_command.command],
                operational_status="requires-context",
                notes=[
                    "L’administration existe, mais son endpoint d’ouverture n’est pas confirmé comme URL publique opérationnelle."
                ],
                source=ManualFactSource(
                    status="derived",
                    sources=tuple(dict.fromkeys([up_command.source, *knowledge.django.source_paths])),
                ),
            )
        return None

    def _tests_workflow(
        self,
        knowledge: ProjectKnowledge,
    ) -> ManualWorkflow | None:
        aggregate = self._aggregate_test_command(knowledge)
        if aggregate is not None:
            notes = []
            if self._find_command(knowledge, "check") is not None:
                notes.append(
                    "`make check` reste une vérification d’invariants ou de diagnostic et n’est pas utilisé comme workflow de tests."
                )
            return ManualWorkflow(
                identifier="run-tests",
                title="Lancer les tests",
                summary="Une commande opérationnelle agrège les suites de tests démontrées pour l’application.",
                commands=[aggregate.command],
                operational_status="operational",
                notes=notes,
                source=ManualFactSource(
                    status="derived",
                    sources=(aggregate.source,),
                ),
            )

        make_test_commands = [
            command
            for command in knowledge.operational_commands.commands
            if self._command_is_backend_test(command)
            or self._command_is_frontend_test(command)
        ]
        if make_test_commands:
            notes = []
            if self._find_command(knowledge, "check") is not None:
                notes.append(
                    "`make check` reste une vérification d’invariants ou de diagnostic et n’est pas utilisé comme workflow de tests."
                )
            return ManualWorkflow(
                identifier="run-tests",
                title="Lancer les tests",
                summary="Les suites de tests démontrées sont exposées par des commandes opérationnelles distinctes.",
                commands=[command.command for command in make_test_commands],
                operational_status="operational",
                notes=notes,
                source=ManualFactSource(
                    status="derived",
                    sources=tuple(dict.fromkeys(command.source for command in make_test_commands)),
                ),
            )

        if "test" in knowledge.react.scripts:
            notes = [
                "Le script frontend a été détecté, mais son contexte d’exécution complet n’est pas démontré par une commande opérationnelle du dépôt."
            ]
            if self._find_command(knowledge, "check") is not None:
                notes.append(
                    "`make check` reste une vérification d’invariants ou de diagnostic et n’est pas utilisé comme workflow de tests."
                )
            if not self._has_backend_test_command(knowledge):
                notes.append(
                    "Aucune commande opérationnelle de tests backend n’a été prouvée."
                )
            return ManualWorkflow(
                identifier="run-tests",
                title="Lancer les tests",
                summary="Le frontend expose un script de test, mais aucun workflow opérationnel complet n’a été démontré pour l’ensemble de l’application.",
                commands=[knowledge.react.scripts["test"]],
                operational_status="requires-context",
                notes=notes,
                source=ManualFactSource(
                    status="derived",
                    sources=("frontend/package.json",),
                ),
            )
        return None

    def _detect_admin_fallback_risk(
        self,
        knowledge: ProjectKnowledge,
    ) -> dict[str, Any] | None:
        for command in knowledge.operational_commands.commands:
            if command.name not in {"createsuperuser", "create-admin", "migrate"}:
                continue
            for line in command.body:
                normalized = line.replace(" ", "")
                if "ADMIN_PASSWORD" not in normalized:
                    continue
                if (
                    ":-" in normalized
                    or ":=" in normalized
                    or "?=" in normalized
                    or ('os.getenv("ADMIN_PASSWORD")' in line and ' or "' in line)
                ):
                    return {
                        "identifier": "ADMIN-CREDENTIAL-FALLBACK-DETECTED",
                        "category": "credentials",
                        "severity": "warning",
                        "description": "La procédure de création de l’administrateur contient une valeur de secours codée en dur lorsque la variable de mot de passe est absente.",
                        "sources": [command.source],
                    }
        return None

    def _workflow_proves_create_admin(
        self,
        knowledge: ProjectKnowledge,
    ) -> bool:
        return any(
            any(
                "python manage.py ensure_admin" in command
                for command in script.django_commands
            )
            for script in knowledge.operational_commands.scripts
        )

    def _has_backend_test_command(
        self,
        knowledge: ProjectKnowledge,
    ) -> bool:
        return any(
            self._command_is_backend_test(command)
            for command in knowledge.operational_commands.commands
        )

    def _aggregate_test_command(
        self,
        knowledge: ProjectKnowledge,
    ):
        for command in knowledge.operational_commands.commands:
            if command.category != "tests":
                continue
            prerequisite_names = set(command.prerequisites)
            if prerequisite_names and any(
                self._command_is_backend_test(self._find_command(knowledge, name))
                for name in prerequisite_names
                if self._find_command(knowledge, name) is not None
            ) and any(
                self._command_is_frontend_test(self._find_command(knowledge, name))
                for name in prerequisite_names
                if self._find_command(knowledge, name) is not None
            ):
                return command
        return None

    @staticmethod
    def _command_is_backend_test(command) -> bool:
        if command is None:
            return False
        haystack = "\n".join([command.command, *command.body]).casefold()
        return "manage.py test" in haystack or "pytest" in haystack

    @staticmethod
    def _command_is_frontend_test(command) -> bool:
        if command is None:
            return False
        haystack = "\n".join([command.command, *command.body]).casefold()
        return "npm run test" in haystack or "node --test" in haystack

    @staticmethod
    def _find_command(
        knowledge: ProjectKnowledge,
        name: str,
    ):
        for command in knowledge.operational_commands.commands:
            if command.name == name:
                return command
        return None

    @staticmethod
    def _select_endpoint(
        knowledge: ProjectKnowledge,
        *,
        service: str,
        environment: str | None = None,
        require_valid: bool = False,
    ):
        for endpoint in knowledge.service_endpoints.endpoints:
            if endpoint.service != service:
                continue
            if environment is not None and endpoint.environment != environment:
                continue
            if require_valid and endpoint.validity != "valid":
                continue
            return endpoint
        return None

    def _select_admin_endpoint(
        self,
        knowledge: ProjectKnowledge,
    ):
        for endpoint in knowledge.service_endpoints.endpoints:
            if endpoint.validity != "valid":
                continue
            if endpoint.resolution_status != "resolved":
                continue
            if "/admin/" in endpoint.url:
                return endpoint
        return None

    @staticmethod
    def _environment_variable(
        knowledge: ProjectKnowledge,
        name: str,
    ):
        for variable in knowledge.environment_variables.variables:
            if variable.name == name:
                return variable
        return None

    @staticmethod
    def _command_sources(knowledge: ProjectKnowledge) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    *[command.source for command in knowledge.operational_commands.commands],
                    *[script.path for script in knowledge.operational_commands.scripts],
                }
            )
        )
