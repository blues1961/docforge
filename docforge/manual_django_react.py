from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

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


class DjangoReactManualKnowledgeBuilder(
    ManualKnowledgeBuilder
):
    def build(
        self,
        *,
        project_root: Path,
        knowledge: ProjectKnowledge,
        profile_instance: ProjectProfile,
    ) -> ManualKnowledge:
        commands = self._build_operational_commands(
            knowledge
        )
        workflows = self._build_workflows(knowledge)
        missing_information = self._missing_information(
            knowledge
        )
        conflicts = self._build_conflicts(knowledge)
        limitations = self._build_limitations(
            knowledge,
            missing_information,
            conflicts,
        )

        return ManualKnowledge(
            schema_version=self.SCHEMA_VERSION,
            project=ManualProject(
                name=knowledge.application.name
                or knowledge.identity.name,
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
                "source_paths": list(
                    knowledge.application.source_paths
                ),
            },
            environments={
                "items": [
                    asdict(item)
                    for item in knowledge.environments.items
                ]
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
                        "environments": list(item.environments),
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
                    sources=(
                        "ProjectKnowledge",
                        "django-react",
                    ),
                ),
            ),
            documentation_policy=self._build_documentation_policy(
                profile_instance
            ),
            source_traceability=ManualSourceTraceability(
                items={
                    "application": ManualFactSource(
                        status="detected",
                        sources=tuple(
                            knowledge.application.source_paths
                        ),
                    ),
                    "environments": ManualFactSource(
                        status="detected",
                        sources=tuple(
                            item.compose_file
                            for item in knowledge.environments.items
                        ),
                    ),
                    "operational_commands": ManualFactSource(
                        status="detected",
                        sources=("Makefile", "scripts/"),
                    ),
                    "environment_variables": ManualFactSource(
                        status="detected",
                        sources=(
                            ".env",
                            ".env.dev",
                            ".env.prod",
                            ".env.template.example",
                            "backend/App/settings.py",
                            "frontend/src/api.js",
                            "scripts/generate-env.sh",
                        ),
                    ),
                    "django": ManualFactSource(
                        status="detected",
                        sources=tuple(
                            knowledge.django.source_paths
                        ),
                    ),
                    "react": ManualFactSource(
                        status="detected",
                        sources=tuple(
                            knowledge.react.source_paths
                        ),
                    ),
                    "capabilities": ManualFactSource(
                        status="derived",
                        sources=(
                            "backend/api/views.py",
                            "frontend/src/App.jsx",
                            "frontend/src/api.js",
                        ),
                    ),
                    "prepared_by": ManualFactSource(
                        status="configured",
                        sources=("DocForge manual pipeline",),
                    ),
                }
            ),
        )

    def _build_installation(
        self,
        knowledge: ProjectKnowledge,
    ) -> ManualInstallation:
        prerequisites: list[str] = []
        if knowledge.deployment.compose_files:
            prerequisites.append(
                "Docker et Docker Compose"
            )
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
            command = self._find_command(
                knowledge,
                command_name,
            )
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
                sources=("Makefile", "scripts/"),
            ),
        )

    def _build_operational_commands(
        self,
        knowledge: ProjectKnowledge,
    ) -> list[ManualCommand]:
        commands = []
        for item in knowledge.operational_commands.commands:
            commands.append(
                ManualCommand(
                    name=item.name,
                    command_path=item.command,
                    invocation=item.command,
                    group=item.category,
                    help=f"Commande opérationnelle catégorie {item.category}.",
                    parameters=[
                        ManualCommandParameter(
                            name=parameter.name,
                            kind="make-variable",
                            required=parameter.required,
                            example=parameter.example,
                            description=parameter.description,
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
            for name in required:
                item = self._find_command(knowledge, name)
                if item is None:
                    return
                commands.append(item.command)
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
                        sources=tuple(commands),
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
        if self._workflow_proves_create_admin(knowledge):
            add_if_complete(
                "create-admin",
                "Créer un administrateur",
                "Créer ou mettre à jour le compte administrateur via la procédure détectée.",
                ["migrate"],
            )
        if self._has_frontend_endpoint(knowledge, "dev"):
            add_if_complete(
                "open-frontend",
                "Ouvrir le frontend",
                "Démarrer les services puis ouvrir le frontend détecté.",
                ["dev", "up"],
            )
        if self._has_admin_endpoint(knowledge):
            add_if_complete(
                "open-django-admin",
                "Accéder à l’administration Django",
                "Démarrer les services puis ouvrir l’administration détectée.",
                ["up"],
            )
        add_if_complete(
            "view-logs",
            "Consulter les journaux",
            "Afficher les logs des services actifs.",
            ["logs"],
        )
        if "test" in knowledge.react.scripts:
            workflows.append(
                ManualWorkflow(
                    identifier="run-tests",
                    title="Lancer les tests",
                    summary="Le frontend expose un script de test, mais aucun workflow Make/Docker complet n’a été démontré pour l’ensemble de l’application.",
                    commands=["npm run test"],
                    operational_status="requires-context",
                    notes=[
                        "`make check` reste un diagnostic d’invariants et n’est pas utilisé comme workflow de tests.",
                        "Aucune commande opérationnelle de tests backend n’a été prouvée.",
                    ],
                    source=ManualFactSource(
                        status="derived",
                        sources=("frontend/package.json",),
                    ),
                )
            )
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
                sources=(
                    "docker-compose.dev.yml",
                    "docker-compose.prod.yml",
                    "backend/App/settings.py",
                ),
            ),
        )

    def _build_security(
        self,
        knowledge: ProjectKnowledge,
    ) -> ManualSecurity:
        controls: list[dict[str, str]] = []
        if knowledge.django.auth_mechanisms:
            controls.append(
                {
                    "identifier": "APP-SEC-001",
                    "category": "authentification",
                    "description": "Des mécanismes d’authentification ont été détectés côté backend et/ou frontend.",
                    "evidence": ", ".join(knowledge.django.auth_mechanisms),
                }
            )
        if knowledge.django.admin_enabled:
            controls.append(
                {
                    "identifier": "APP-SEC-002",
                    "category": "administration",
                    "description": "Une interface d’administration Django est détectée et doit être réservée aux comptes autorisés.",
                    "evidence": "backend/App/urls.py",
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
                    "evidence": "environment_variables",
                }
            )

        risks = []
        if any(
            item.name == "DJANGO_DEBUG"
            and "prod" in item.environments
            for item in knowledge.environment_variables.variables
        ):
            risks.append(
                "La valeur effective de DJANGO_DEBUG en production doit être vérifiée hors du dépôt."
            )
        if not knowledge.service_endpoints.endpoints:
            risks.append(
                "Aucune URL de service n’a pu être confirmée statiquement."
            )

        return ManualSecurity(
            protected_documents=[],
            controls=controls,
            risks=risks,
            validation_commands=[],
            source=ManualFactSource(
                status="derived",
                sources=(
                    "backend/App/settings.py",
                    "backend/App/urls.py",
                    "frontend/src/api.js",
                    "environment_variables",
                ),
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

        def add(identifier: str, category: str, description: str, *, affected_sections: list[str], sources: list[str], severity: str = "warning") -> None:
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
                sources=["pyproject.toml", "backend/Dockerfile.dev", "backend/Dockerfile.prod"],
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
            sources=["docker-compose.dev.yml", "docker-compose.prod.yml", "Makefile"],
        )
        if not any("pytest" in command.command or "manage.py test" in command.command for command in knowledge.operational_commands.commands):
            add(
                "BACKEND-TEST-COMMAND-MISSING",
                "tests",
                "Aucune commande opérationnelle de tests backend n’a été démontrée.",
                affected_sections=["tests", "backend"],
                sources=["Makefile", "scripts/", "backend/"],
            )
        add(
            "INTEGRATION-TEST-DETAILS-MISSING",
            "tests",
            "Les détails des tests d’intégration ne sont pas disponibles dans les faits structurés générés.",
            affected_sections=["tests", "api"],
            sources=["tests/", "backend/api/views.py", "frontend/src/api.js"],
        )
        add(
            "API-SCHEMA-MISSING",
            "api",
            "Les schémas détaillés de requête et de réponse des endpoints ne sont pas disponibles.",
            affected_sections=["api"],
            sources=["backend/api/urls.py", "backend/api/views.py"],
        )
        add(
            "API-ERROR-CODES-MISSING",
            "api",
            "La matrice complète des codes d’erreur API n’est pas structurée de manière exhaustive.",
            affected_sections=["api", "troubleshooting"],
            sources=["backend/api/views.py"],
        )
        if not any(field.name == "visibility" and field.choices for model in knowledge.django.model_schemas for field in model.fields):
            add(
                "VISIBILITY-VALUES-MISSING",
                "data-model",
                "Les valeurs possibles du champ visibility ne sont pas démontrées dans les faits structurés.",
                affected_sections=["api", "interface-usage"],
                sources=["backend/api/models.py"],
            )
        if knowledge.react.crypto.detected and knowledge.react.crypto.recovery_supported is None:
            add(
                "VAULT-RECOVERY-PROCEDURE-MISSING",
                "security",
                "La procédure de récupération du coffre privé n’est pas démontrée dans le code analysé.",
                affected_sections=["security", "authentication-accounts"],
                sources=["frontend/src/crypto.js", "frontend/src/App.jsx"],
            )
        add(
            "BACKUP-RETENTION-POLICY-MISSING",
            "backup",
            "La stratégie de rétention des sauvegardes n’est pas démontrée.",
            affected_sections=["backup-restore", "operations"],
            sources=["scripts/backup-db.sh", "scripts/restore-db.sh"],
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
            if service.role == "database" and ((service.image or "").casefold().startswith("postgres") or service.name == "db")
        ]
        postgres_sources.extend(
            script.path
            for script in knowledge.operational_commands.scripts
            if script.database_engine == "PostgreSQL"
        )
        if runtime_engines and any("sqlite" in item.engine for item in runtime_engines) and postgres_sources:
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
                    affected_sections=["database", "migrations", "backup", "restore", "production"],
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
                    sources=[source for fact in conflict.facts for source in fact.sources],
                )
            )
        if any(route.resolution_status != "resolved" for route in knowledge.django.resolved_routes):
            items.append(
                ManualKnowledgeGap(
                    identifier="UNRESOLVED-ROUTES",
                    category="api",
                    severity="warning",
                    description="Certaines routes Django ont été détectées sans pouvoir être résolues en chemins publics complets.",
                    affected_sections=["api"],
                    sources=["backend/App/urls.py", "backend/api/urls.py"],
                )
            )
        return items

    def _workflow_proves_create_admin(
        self,
        knowledge: ProjectKnowledge,
    ) -> bool:
        return any(
            any("python manage.py ensure_admin" in command for command in script.django_commands)
            for script in knowledge.operational_commands.scripts
        )

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
    def _has_frontend_endpoint(
        knowledge: ProjectKnowledge,
        environment: str,
    ) -> bool:
        return any(
            endpoint.environment == environment
            and endpoint.service == "frontend"
            for endpoint in knowledge.service_endpoints.endpoints
        )

    @staticmethod
    def _has_admin_endpoint(
        knowledge: ProjectKnowledge,
    ) -> bool:
        return any(
            "/admin/" in endpoint.url
            for endpoint in knowledge.service_endpoints.endpoints
        )
