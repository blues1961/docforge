from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from docforge.knowledge import ProjectKnowledge
from docforge.manual_knowledge import (
    ManualCommand,
    ManualConfiguration,
    ManualDocumentationPolicy,
    ManualFactSource,
    ManualInstallation,
    ManualInstallationStep,
    ManualKnowledge,
    ManualKnowledgeBuilder,
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
            commands=commands,
            workflows=workflows,
            configuration=self._build_configuration(knowledge),
            security=self._build_security(knowledge),
            limitations=ManualLimitations(
                items=missing_information,
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
                    parameters=[],
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
        if knowledge.django.create_admin_commands:
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
            add_if_complete(
                "run-tests",
                "Lancer les tests",
                "Exécuter les tests détectés côté application.",
                ["check"],
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
    ) -> list[str]:
        missing = []
        if not knowledge.capabilities.capabilities:
            missing.append(
                "Aucune capacité fonctionnelle suffisamment fiable n’a été détectée."
            )
        if not knowledge.environment_variables.variables:
            missing.append(
                "Aucune variable d’environnement versionnée ou statiquement détectée n’a été extraite."
            )
        if not knowledge.service_endpoints.endpoints:
            missing.append(
                "Aucune URL de service n’a pu être dérivée statiquement."
            )
        if not knowledge.operational_commands.commands:
            missing.append(
                "Aucune commande opérationnelle fiable n’a été détectée."
            )
        if not knowledge.react.api_calls:
            missing.append(
                "Les appels API côté frontend n’ont pas pu être extraits."
            )
        return missing

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
