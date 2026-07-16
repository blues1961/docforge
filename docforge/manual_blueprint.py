from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ManualSectionDefinition:
    identifier: str
    title: str
    purpose: str
    required_fact_paths: tuple[str, ...]
    optional: bool = False
    omit_condition: str | None = None
    omit_if_fact_paths_missing: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ManualBlueprint:
    profile_name: str
    sections: tuple[ManualSectionDefinition, ...] = field(
        default_factory=tuple
    )


class ManualBlueprintRegistry:
    def blueprint_for_profile(
        self,
        profile_name: str,
    ) -> ManualBlueprint:
        if profile_name == "python-cli":
            return self._python_cli_blueprint()

        if profile_name == "django-react":
            return self._django_react_blueprint()

        return self._generic_blueprint()

    def _python_cli_blueprint(self) -> ManualBlueprint:
        sections = (
            ManualSectionDefinition(
                "presentation",
                "Présentation",
                "Présenter le produit, son objectif et son profil logiciel.",
                ("project", "profile"),
            ),
            ManualSectionDefinition(
                "target-audience",
                "Public visé",
                "Décrire les utilisateurs pertinents à partir du type de projet et de la CLI détectée.",
                ("project", "profile", "commands"),
            ),
            ManualSectionDefinition(
                "prerequisites",
                "Prérequis",
                "Lister les prérequis strictement démontrés pour utiliser le dépôt localement.",
                ("installation.prerequisites", "project.python_requires", "configuration"),
            ),
            ManualSectionDefinition(
                "installation",
                "Installation",
                "Décrire l’installation locale depuis une copie du dépôt.",
                ("installation",),
            ),
            ManualSectionDefinition(
                "quick-start",
                "Démarrage rapide",
                "Fournir une première séquence de commandes pour vérifier l’outil.",
                ("installation.steps", "commands", "workflows"),
            ),
            ManualSectionDefinition(
                "core-concepts",
                "Concepts essentiels",
                "Expliquer les concepts structurants du produit.",
                ("project", "profile", "documentation_policy", "security"),
            ),
            ManualSectionDefinition(
                "analyze-project",
                "Analyse d’un projet",
                "Décrire le flux d’analyse d’un projet local.",
                ("workflows", "commands"),
            ),
            ManualSectionDefinition(
                "detect-profile",
                "Détection du profil",
                "Expliquer comment le profil est déterminé et présenté.",
                ("profile", "workflows", "commands"),
            ),
            ManualSectionDefinition(
                "build-project-knowledge",
                "Construction de ProjectKnowledge",
                "Décrire la construction de la connaissance structurée.",
                ("workflows", "commands", "documentation_policy"),
            ),
            ManualSectionDefinition(
                "documentation-generation",
                "Génération documentaire",
                "Présenter la génération déterministe en aperçu.",
                ("workflows", "documentation_policy", "security", "commands"),
            ),
            ManualSectionDefinition(
                "ollama-generation",
                "Génération avec Ollama",
                "Expliquer le flux dédié à docforge generate sans le confondre avec la préparation du manuel.",
                ("workflows", "commands", "limitations"),
            ),
            ManualSectionDefinition(
                "preview-review",
                "Révision des aperçus",
                "Expliquer la validation humaine des aperçus générés.",
                ("workflows", "security", "documentation_policy"),
            ),
            ManualSectionDefinition(
                "apply-documents",
                "Application des documents",
                "Décrire l’application explicite des documents validés.",
                ("workflows", "security", "commands"),
            ),
            ManualSectionDefinition(
                "protected-documents",
                "Documents protégés",
                "Décrire le traitement spécifique des documents protégés.",
                ("security", "documentation_policy", "workflows"),
            ),
            ManualSectionDefinition(
                "project-management",
                "Gestion des projets",
                "Décrire l’enregistrement et le suivi de plusieurs projets.",
                ("commands", "workflows", "configuration"),
            ),
            ManualSectionDefinition(
                "audits-compliance",
                "Audits et conformité",
                "Présenter les commandes d’audit et les validations de conformité.",
                ("commands", "workflows", "security"),
            ),
            ManualSectionDefinition(
                "configuration",
                "Configuration",
                "Décrire les emplacements et fichiers de configuration utiles.",
                ("configuration",),
            ),
            ManualSectionDefinition(
                "security",
                "Sécurité",
                "Présenter les garde-fous documentaires et opérationnels.",
                ("security", "documentation_policy"),
            ),
            ManualSectionDefinition(
                "troubleshooting",
                "Dépannage",
                "Guider le lecteur en cas de problème connu ou d’information manquante.",
                ("limitations", "security", "commands"),
            ),
            ManualSectionDefinition(
                "limitations",
                "Limites des informations disponibles",
                "Exposer les limites de la source de vérité fournie au modèle.",
                ("limitations", "source_traceability"),
            ),
            ManualSectionDefinition(
                "cli-reference",
                "Référence CLI",
                "Fournir une référence fidèle des commandes détectées.",
                ("commands",),
            ),
        )
        return ManualBlueprint(
            profile_name="python-cli",
            sections=sections,
        )

    def _django_react_blueprint(self) -> ManualBlueprint:
        sections = (
            ManualSectionDefinition(
                "presentation",
                "Présentation",
                "Présenter l’application analysée et son périmètre technique.",
                ("application", "project", "profile"),
            ),
            ManualSectionDefinition(
                "target-audience",
                "Public visé",
                "Décrire le public visé à partir des capacités et des rôles visibles.",
                ("capabilities", "react", "django"),
            ),
            ManualSectionDefinition(
                "detected-features",
                "Fonctionnalités détectées",
                "Présenter les capacités détectées ou dérivées avec prudence.",
                ("capabilities",),
                omit_condition="Omettre si aucune capacité détectée ou dérivée n’est disponible.",
                omit_if_fact_paths_missing=("capabilities.capabilities",),
            ),
            ManualSectionDefinition(
                "general-architecture",
                "Architecture générale",
                "Présenter backend, frontend, services et environnements.",
                ("application", "environments", "django", "react"),
            ),
            ManualSectionDefinition(
                "prerequisites",
                "Prérequis",
                "Lister les prérequis démontrés pour opérer l’application.",
                ("installation.prerequisites", "environments", "environment_variables"),
            ),
            ManualSectionDefinition(
                "installation",
                "Installation",
                "Présenter la préparation initiale du dépôt et des environnements.",
                ("installation", "operational_commands"),
            ),
            ManualSectionDefinition(
                "environment-configuration",
                "Configuration des environnements",
                "Décrire la séparation dev/prod, les fichiers Compose et les fichiers d’environnement.",
                ("environments",),
            ),
            ManualSectionDefinition(
                "environment-variables",
                "Variables d’environnement",
                "Présenter les noms de variables sans exposer de valeurs sensibles.",
                ("environment_variables",),
                omit_condition="Omettre si aucune variable versionnée ou détectée statiquement n’est disponible.",
                omit_if_fact_paths_missing=("environment_variables.variables",),
            ),
            ManualSectionDefinition(
                "quick-start",
                "Démarrage rapide",
                "Donner la séquence minimale pour préparer et démarrer le développement si les commandes critiques existent.",
                ("workflows", "operational_commands"),
            ),
            ManualSectionDefinition(
                "development-environment",
                "Environnement de développement",
                "Détailler les services, ports et URLs du mode développement.",
                ("environments", "service_endpoints"),
                omit_condition="Omettre si aucun environnement dev n’est détecté.",
                omit_if_fact_paths_missing=("environments.items",),
            ),
            ManualSectionDefinition(
                "production-environment",
                "Environnement de production",
                "Détailler les services, réseaux, hôtes et URLs du mode production.",
                ("environments", "service_endpoints"),
                omit_condition="Omettre si aucun environnement prod n’est détecté.",
                omit_if_fact_paths_missing=("environments.items",),
            ),
            ManualSectionDefinition(
                "docker-services",
                "Services Docker",
                "Présenter les services par environnement avec leurs rôles probables.",
                ("environments",),
            ),
            ManualSectionDefinition(
                "database",
                "Base de données",
                "Décrire la base de données et sa configuration statiquement détectable.",
                ("django", "environments", "environment_variables"),
            ),
            ManualSectionDefinition(
                "migrations",
                "Migrations",
                "Décrire la procédure de migration uniquement si une commande fiable existe.",
                ("django", "operational_commands", "workflows"),
                omit_condition="Omettre si aucune commande de migration n’est détectée.",
                omit_if_fact_paths_missing=("django.migration_commands",),
            ),
            ManualSectionDefinition(
                "django-admin",
                "Administration Django",
                "Décrire l’accès à l’administration Django et la création d’un administrateur si elles sont démontrées.",
                ("django", "service_endpoints", "workflows"),
                omit_condition="Omettre si l’administration Django n’est pas détectée.",
                omit_if_fact_paths_missing=("django.admin_enabled",),
            ),
            ManualSectionDefinition(
                "interface-usage",
                "Utilisation de l’interface",
                "Présenter les écrans, filtres et éléments d’interface détectés sans extrapolation.",
                ("react", "capabilities"),
            ),
            ManualSectionDefinition(
                "authentication-accounts",
                "Authentification et comptes",
                "Décrire l’authentification et la gestion des comptes selon les faits backend/frontend.",
                ("django", "react", "capabilities"),
            ),
            ManualSectionDefinition(
                "api",
                "API",
                "Présenter les endpoints, l’authentification et les capacités d’intégration détectées.",
                ("django", "service_endpoints"),
            ),
            ManualSectionDefinition(
                "stop-restart",
                "Arrêt et redémarrage",
                "Décrire les opérations d’arrêt et redémarrage si des commandes fiables existent.",
                ("operational_commands", "workflows"),
                omit_condition="Omettre si aucune commande d’arrêt ou de redémarrage n’est détectée.",
                omit_if_fact_paths_missing=("operational_commands.commands",),
            ),
            ManualSectionDefinition(
                "logs-diagnostics",
                "Journaux et diagnostic",
                "Décrire les commandes de logs, statut et diagnostic si elles existent.",
                ("operational_commands", "workflows"),
                omit_condition="Omettre si aucune commande de logs ou diagnostic n’est détectée.",
                omit_if_fact_paths_missing=("operational_commands.commands",),
            ),
            ManualSectionDefinition(
                "tests",
                "Tests",
                "Présenter les commandes de test détectées côté frontend ou backend.",
                ("react", "operational_commands"),
                omit_condition="Omettre si aucune commande de test n’est détectée.",
                omit_if_fact_paths_missing=("react.scripts",),
            ),
            ManualSectionDefinition(
                "backup-restore",
                "Sauvegarde et restauration",
                "Décrire les procédures de sauvegarde et restauration si les commandes critiques existent.",
                ("operational_commands", "workflows"),
                omit_condition="Omettre si aucune commande de sauvegarde ou restauration n’est détectée.",
                omit_if_fact_paths_missing=("operational_commands.commands",),
            ),
            ManualSectionDefinition(
                "security",
                "Sécurité",
                "Présenter les points de sécurité détectés sans exposer de secret.",
                ("security", "environment_variables", "django", "react"),
            ),
            ManualSectionDefinition(
                "troubleshooting",
                "Dépannage",
                "Aider à diagnostiquer les manques d’information et les commandes opérationnelles disponibles.",
                ("limitations", "operational_commands", "service_endpoints"),
            ),
            ManualSectionDefinition(
                "limitations",
                "Limites des informations disponibles",
                "Présenter les faits réellement absents ou insuffisants.",
                ("limitations", "source_traceability"),
            ),
            ManualSectionDefinition(
                "operational-commands-reference",
                "Référence des commandes opérationnelles",
                "Fournir uniquement les commandes applicatives détectées.",
                ("operational_commands",),
                omit_condition="Omettre si aucune commande opérationnelle n’est détectée.",
                omit_if_fact_paths_missing=("operational_commands.commands",),
            ),
        )
        return ManualBlueprint(
            profile_name="django-react",
            sections=sections,
        )

    def _generic_blueprint(self) -> ManualBlueprint:
        return ManualBlueprint(
            profile_name="generic",
            sections=(
                ManualSectionDefinition(
                    "presentation",
                    "Présentation",
                    "Présenter le projet à partir des faits disponibles.",
                    ("project", "profile"),
                ),
                ManualSectionDefinition(
                    "prerequisites",
                    "Prérequis",
                    "Lister uniquement les prérequis démontrés.",
                    ("installation.prerequisites", "configuration"),
                ),
                ManualSectionDefinition(
                    "installation",
                    "Installation",
                    "Décrire l’installation locale quand elle est démontrée.",
                    ("installation",),
                ),
                ManualSectionDefinition(
                    "usage",
                    "Utilisation",
                    "Décrire les commandes ou étapes d’utilisation disponibles.",
                    ("commands", "workflows"),
                ),
                ManualSectionDefinition(
                    "limitations",
                    "Limites des informations disponibles",
                    "Exposer les limites de la connaissance disponible.",
                    ("limitations", "source_traceability"),
                ),
                ManualSectionDefinition(
                    "cli-reference",
                    "Référence CLI",
                    "Fournir la référence CLI quand des commandes sont détectées.",
                    ("commands",),
                    optional=True,
                    omit_condition="Omettre si aucune commande détectée n’est disponible.",
                    omit_if_fact_paths_missing=("commands",),
                ),
            ),
        )
