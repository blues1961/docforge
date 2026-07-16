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
    document_identifier: str = "manual"
    document_title: str = "Guide utilisateur"
    document_audience: str = "user"
    document_kind: str = "user-guide"


class ManualBlueprintRegistry:
    def blueprint_for_profile(
        self,
        profile_name: str,
    ) -> ManualBlueprint:
        return self.blueprints_for_context(
            profile_name,
            project_kind=None,
        )[0]

    def blueprints_for_context(
        self,
        profile_name: str,
        *,
        project_kind: str | None,
    ) -> tuple[ManualBlueprint, ...]:
        if profile_name == "django-react" and project_kind == "application-template":
            return (
                self._django_react_template_creation_blueprint(),
                self._django_react_template_maintenance_blueprint(),
            )

        if profile_name == "python-cli":
            return (self._python_cli_blueprint(),)

        if profile_name == "django-react":
            return (self._django_react_blueprint(),)

        return (self._generic_blueprint(),)

    def blueprint_for_document(
        self,
        profile_name: str,
        *,
        project_kind: str | None,
        document_identifier: str,
    ) -> ManualBlueprint:
        for blueprint in self.blueprints_for_context(
            profile_name,
            project_kind=project_kind,
        ):
            if blueprint.document_identifier == document_identifier:
                return blueprint
        raise KeyError(
            f"Blueprint documentaire introuvable: {profile_name}/{project_kind}/{document_identifier}"
        )

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
                ("missing_information", "limitations", "source_traceability"),
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
            document_identifier="manual",
            document_title="Guide utilisateur",
            document_audience="user",
            document_kind="user-guide",
        )

    def _django_react_blueprint(self) -> ManualBlueprint:
        sections = (
            ManualSectionDefinition(
                "presentation",
                "Présentation",
                "Présenter l’application analysée et son périmètre fonctionnel en quelques phrases.",
                ("application", "project", "profile"),
            ),
            ManualSectionDefinition(
                "audience-roles",
                "Public visé et rôles",
                "Distinguer les usages utilisateur, administrateur applicatif et exploitant à partir des faits détectés.",
                ("capabilities", "react", "django"),
            ),
            ManualSectionDefinition(
                "main-features",
                "Fonctionnalités principales",
                "Présenter les capacités détectées ou dérivées avec prudence, du point de vue utilisateur.",
                ("capabilities", "django", "react"),
                omit_condition="Omettre si aucune capacité détectée ou dérivée n’est disponible.",
                omit_if_fact_paths_missing=("capabilities.capabilities",),
            ),
            ManualSectionDefinition(
                "quick-start",
                "Démarrage rapide",
                "Donner uniquement la séquence minimale pour lancer l’application en développement et atteindre l’URL principale.",
                ("workflows", "operational_commands", "service_endpoints", "missing_information"),
            ),
            ManualSectionDefinition(
                "application-usage",
                "Utilisation de l’application",
                "Décrire la connexion, la consultation, la recherche, la création, la modification, la visibilité, les contacts privés et les synchronisations réellement démontrés.",
                ("react", "capabilities", "django"),
                omit_condition="Omettre si aucun fait d’interface ou de capacité n’est disponible.",
                omit_if_fact_paths_missing=("react.pages", "react.navigation_items", "capabilities.capabilities"),
            ),
            ManualSectionDefinition(
                "administration",
                "Administration",
                "Couvrir les comptes, les permissions administratives, la réinitialisation des mots de passe et l’administration Django lorsque ces éléments sont démontrés.",
                ("django", "capabilities", "workflows", "service_endpoints"),
            ),
            ManualSectionDefinition(
                "installation-configuration",
                "Installation et configuration",
                "Regrouper les prérequis, les fichiers d’environnement, les variables importantes et la comparaison développement/production.",
                ("installation", "installation.prerequisites", "environments", "environment_variables", "service_endpoints"),
            ),
            ManualSectionDefinition(
                "operations",
                "Exploitation",
                "Regrouper démarrage, arrêt, migrations, compte administrateur, journaux, diagnostic, tests, sauvegarde, restauration, mise à jour et reconstruction.",
                ("operational_commands", "workflows", "missing_information", "limitations"),
                omit_condition="Omettre si aucune commande opérationnelle n’est détectée.",
                omit_if_fact_paths_missing=("operational_commands.commands",),
            ),
            ManualSectionDefinition(
                "technical-reference",
                "Architecture et référence technique",
                "Regrouper les services, la base de données, l’API et le chiffrement côté client sans dupliquer l’ensemble des procédures d’exploitation.",
                ("application", "environments", "service_endpoints", "django", "react", "conflicts", "limitations"),
            ),
            ManualSectionDefinition(
                "security",
                "Sécurité",
                "Présenter les contrôles détectés, les risques structurés et les limites de sécurité sans extrapolation.",
                ("security", "environment_variables", "django", "react", "conflicts", "limitations"),
            ),
            ManualSectionDefinition(
                "troubleshooting",
                "Dépannage",
                "Aider à diagnostiquer les blocages pratiques sans recopier toute la référence technique.",
                ("limitations", "missing_information", "operational_commands", "service_endpoints", "conflicts"),
            ),
            ManualSectionDefinition(
                "operational-commands-reference",
                "Référence des commandes",
                "Fournir la référence détaillée des commandes applicatives détectées, avec leurs paramètres et leur contexte.",
                ("operational_commands", "workflows"),
                omit_condition="Omettre si aucune commande opérationnelle n’est détectée.",
                omit_if_fact_paths_missing=("operational_commands.commands",),
            ),
            ManualSectionDefinition(
                "limitations",
                "Limites des informations disponibles",
                "Consolider les informations absentes, ambiguës ou incomplètes en phrases lisibles pour le lecteur final.",
                ("missing_information", "limitations", "source_traceability"),
            ),
        )
        return ManualBlueprint(
            profile_name="django-react",
            sections=sections,
            document_identifier="manual",
            document_title="Guide utilisateur",
            document_audience="user",
            document_kind="user-guide",
        )

    def _django_react_template_creation_blueprint(self) -> ManualBlueprint:
        sections = (
            ManualSectionDefinition(
                "template-creation-overview",
                "Rôle du modèle et périmètre",
                "Expliquer à quoi sert app-template, ce qu’il fournit et ce qu’il ne démontre pas encore pour une application finale.",
                ("project", "profile", "template", "application"),
            ),
            ManualSectionDefinition(
                "template-creation-prerequisites",
                "Prérequis",
                "Présenter les prérequis démontrés pour partir du modèle et préparer une nouvelle application.",
                ("installation", "template", "operational_commands"),
            ),
            ManualSectionDefinition(
                "template-creation-prepare-directory",
                "Préparer un nouveau répertoire",
                "Décrire la copie du modèle, la préparation de .env.template et les points d’attention avant la matérialisation.",
                ("template", "missing_information", "limitations"),
            ),
            ManualSectionDefinition(
                "template-creation-identity",
                "Définir l’identité de l’application",
                "Décrire les variables d’identité et d’administration à renseigner dans .env.template sans inventer de valeurs finales.",
                ("template", "environment_variables", "missing_information"),
            ),
            ManualSectionDefinition(
                "template-creation-environments",
                "Générer environnements et secrets",
                "Expliquer la sélection de l’environnement actif, la génération des fichiers .env.* et la création des secrets locaux.",
                ("template", "operational_commands", "environment_variables", "workflows"),
            ),
            ManualSectionDefinition(
                "template-creation-materialization",
                "Matérialiser la nouvelle application",
                "Décrire la matérialisation via make init, la transformation des métadonnées DocForge et les vérifications associées.",
                ("template", "operational_commands", "workflows", "limitations"),
            ),
            ManualSectionDefinition(
                "template-creation-git-transition",
                "Détacher l’historique Git",
                "Décrire le détachement Git explicite, ses avertissements et les limites encore non documentées sur le dépôt distant.",
                ("template", "missing_information", "limitations"),
            ),
            ManualSectionDefinition(
                "template-creation-start-validate",
                "Démarrer, migrer et valider",
                "Présenter le démarrage normal, les migrations, make check et la vérification du profil DocForge obtenu après matérialisation.",
                ("template", "operational_commands", "service_endpoints", "workflows", "profile"),
            ),
            ManualSectionDefinition(
                "template-creation-troubleshooting",
                "Problèmes fréquents",
                "Regrouper les blocages fréquents du bootstrap du modèle, sans inventer de procédure externe.",
                ("template", "missing_information", "limitations", "operational_commands"),
            ),
            ManualSectionDefinition(
                "template-creation-checklist",
                "Checklist finale",
                "Fournir une checklist courte de fin d’instanciation d’une nouvelle application.",
                ("template", "missing_information", "limitations"),
            ),
            ManualSectionDefinition(
                "template-creation-limitations",
                "Informations encore manquantes",
                "Consolider les points que le modèle ne démontre pas encore pour la création complète d’une nouvelle application.",
                ("missing_information", "limitations", "template", "source_traceability"),
            ),
        )
        return ManualBlueprint(
            profile_name="django-react",
            sections=sections,
            document_identifier="application-creation-guide",
            document_title="Guide de création d’une application",
            document_audience="creator",
            document_kind="template-creation-guide",
        )

    def _django_react_template_maintenance_blueprint(self) -> ManualBlueprint:
        sections = (
            ManualSectionDefinition(
                "template-maintenance-overview",
                "Rôle du squelette et publics",
                "Présenter le rôle du dépôt source app-template et le distinguer des applications créées à partir du modèle.",
                ("project", "profile", "template", "application"),
            ),
            ManualSectionDefinition(
                "template-maintenance-architecture",
                "Architecture du squelette",
                "Décrire la structure technique du modèle, ses composants, ses services et ses répertoires clés.",
                ("application", "environments", "django", "react", "template"),
            ),
            ManualSectionDefinition(
                "template-maintenance-metadata",
                "Contrat du modèle et version",
                "Décrire docforge.template.json, sa version, les cibles déclarées et la compatibilité attendue avec DocForge.",
                ("template", "operational_commands", "limitations"),
            ),
            ManualSectionDefinition(
                "template-maintenance-invariants-placeholders",
                "Invariants et placeholders",
                "Documenter les invariants du squelette, les placeholders connus et la façon de valider qu’ils restent cohérents.",
                ("template", "environment_variables", "limitations"),
            ),
            ManualSectionDefinition(
                "template-maintenance-scripts-makefile",
                "Scripts standards et Makefile",
                "Présenter les scripts standards du squelette et les responsabilités générales des cibles publiques du Makefile.",
                ("template", "operational_commands", "workflows"),
            ),
            ManualSectionDefinition(
                "template-maintenance-canonical-targets",
                "Cibles canoniques et politique documentaire",
                "Expliquer les 15 cibles canoniques, leur provenance template et leur politique documentaire.",
                ("template", "operational_commands"),
            ),
            ManualSectionDefinition(
                "template-maintenance-validation-release",
                "Validation avant publication",
                "Décrire les vérifications de maintenance du modèle, make check, make update et les tests sur copie jetable avant publication d’une nouvelle version.",
                ("template", "operational_commands", "workflows", "missing_information", "limitations"),
            ),
            ManualSectionDefinition(
                "template-maintenance-compatibility",
                "Compatibilité avec les applications créées",
                "Présenter la relation entre le dépôt source, docforge.project.json et les applications déjà matérialisées.",
                ("template", "missing_information", "limitations"),
            ),
            ManualSectionDefinition(
                "template-maintenance-limitations",
                "Informations encore manquantes",
                "Consolider les informations non démontrées sur la publication, la mise à jour descendante et les procédures externes.",
                ("missing_information", "limitations", "template", "source_traceability"),
            ),
        )
        return ManualBlueprint(
            profile_name="django-react",
            sections=sections,
            document_identifier="template-maintenance-guide",
            document_title="Guide de maintenance du modèle",
            document_audience="maintainer",
            document_kind="template-maintenance-guide",
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
            document_identifier="manual",
            document_title="Guide",
            document_audience="user",
            document_kind="generic-guide",
        )
