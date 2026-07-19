from __future__ import annotations

from docforge.manual_knowledge import ManualKnowledge


class ManualDeterministicContentBuilder:
    """Render executable facts without asking a language model to restate them."""

    FULLY_DETERMINISTIC_SECTIONS = frozenset({
        "cli-reference", "configuration", "security", "protected-documents",
        "operator-presentation", "operator-prerequisites", "operator-environments",
        "operator-installation-configuration", "operator-compose-services", "operator-make-commands",
        "operator-start-stop", "operator-migrations-administration", "operator-backup-restore",
        "operator-deployment", "operator-environment-variables", "operator-protected-documents",
        "operator-security", "operator-troubleshooting", "operator-limitations",
        "user-presentation", "user-roles", "user-access", "user-authentication",
        "user-main-features", "user-application-usage", "user-functional-administration",
        "user-troubleshooting", "user-limitations", "user-security", "operator-security", "developer-routes-api",
        "developer-presentation", "developer-architecture", "developer-services", "developer-backend",
        "developer-frontend", "developer-authentication", "developer-routes-api",
        "developer-models-capabilities", "developer-development-configuration", "developer-commands",
        "developer-invariants", "developer-security", "developer-missing-information",
    })

    _STATUS_LABELS = {
        "detected": "fait détecté",
        "derived": "fait dérivé",
        "configured": "configuration déclarée",
        "unresolved": "information non résolue",
    }

    def render_section(self, knowledge: ManualKnowledge, section_identifier: str) -> str:
        if section_identifier == "installation":
            lines = ["### Commandes d’installation", ""]
            for step in knowledge.installation.steps:
                lines.extend([f"#### {step.title}", "", "```bash", step.command, "```", "", self._status(step.source.status), ""])
            return "\n".join(lines).rstrip() + "\n"
        if section_identifier == "quick-start":
            commands = [command for workflow in knowledge.workflows if workflow.identifier in {"analyze-project", "detect-profile", "build-project-knowledge", "generate-preview"} for command in workflow.commands]
            return "\n".join(["### Commandes de démarrage rapide", "", "```bash", *dict.fromkeys(commands), "```", ""]) if commands else ""
        if section_identifier == "configuration":
            lines = ["### Chemins et fichiers de configuration démontrés", ""]
            for item in knowledge.configuration.files:
                path = item.get("path")
                if isinstance(path, str) and path:
                    description = item.get("description")
                    lines.append(f"- `{path}`" + (f" — {description}" if isinstance(description, str) and description else ""))
            return "\n".join([*lines, "", self._status(knowledge.configuration.source.status), ""])
        if section_identifier == "operator-presentation":
            name = knowledge.application.get("name", knowledge.project.name) if isinstance(knowledge.application, dict) else knowledge.project.name
            return f"{str(name).capitalize()} est une application auto-hébergée dont l’exploitation s’appuie sur les services et cibles Make démontrés dans ce guide.\n"
        if section_identifier == "operator-prerequisites":
            return "Les versions minimales des outils d’exécution ne sont pas toutes démontrées. Consultez les limites de ce guide avant l’installation.\n"
        if section_identifier == "operator-environments":
            lines = ["| Environnement | Endpoint démontré |", "|---|---|"]
            for endpoint in knowledge.service_endpoints.get("endpoints", []):
                if isinstance(endpoint, dict) and endpoint.get("validity") == "valid":
                    lines.append(f"| {endpoint.get('environment') or '—'} | {endpoint.get('url') or '—'} |")
            return "\n".join(lines) + "\n"
        if section_identifier == "operator-installation-configuration":
            return "Utilisez les cibles de préparation documentées dans **Commandes Make**. Les noms des variables de configuration démontrées figurent dans la section dédiée.\n"
        if section_identifier == "operator-start-stop":
            return "\n".join(["Les invocations nécessaires sont référencées dans **Commandes Make**.", "", "```bash", "make dev", "make up", "make down", "```"]) + "\n"
        if section_identifier == "operator-migrations-administration":
            return "\n".join(["La migration démontrée est référencée dans **Commandes Make**.", "", "```bash", "make migrate", "```"]) + "\n"
        if section_identifier == "operator-backup-restore":
            return "\n".join(["Les opérations de sauvegarde et restauration démontrées sont référencées dans **Commandes Make**.", "", "```bash", "make backup", "make restore [FILE=FILE]", "```"]) + "\n"
        if section_identifier == "operator-deployment":
            return "Les étapes de déploiement détaillées ne sont pas démontrées comme procédure complète. Utilisez les cibles Make documentées pour sélectionner l’environnement et gérer les services.\n"
        if section_identifier == "operator-troubleshooting":
            return "\n".join(["Les procédures de diagnostic démontrées sont référencées dans **Commandes Make**.", "", "```bash", "make ps", "make logs SERVICE=SERVICE", "make check", "```"]) + "\n"
        if section_identifier == "operator-limitations":
            items = [item for item in knowledge.missing_information if getattr(item, "category", None) in {"runtime", "backup", "tests"}]
            lines = [f"- {item.description}" for item in items if getattr(item, "description", None)]
            return "\n".join(lines) + ("\n" if lines else "- Aucune limite opérationnelle supplémentaire n’est démontrée.\n")
        if section_identifier == "operator-compose-services":
            lines = ["### Services Docker Compose démontrés", "", "| Environnement | Service | Rôle | Dépendances |", "|---|---|---|---|"]
            for environment in knowledge.environments.get("items", []):
                for service in environment.get("services", []):
                    lines.append("| " + " | ".join(str(value or "—").replace("|", "\\|") for value in (
                        environment.get("name") or environment.get("environment"), service.get("name"), service.get("role"), ", ".join(service.get("depends_on", [])),
                    )) + " |")
            return "\n".join([*lines, "", "Statut : fait détecté.", ""])
        if section_identifier == "operator-make-commands":
            lines = ["### Cibles Make démontrées", ""]
            commands = [command for command in knowledge.commands if command.visibility == "public" and command.documentation_policy != "exclude" and command.invocation.startswith("make ")]
            for command in commands:
                description = command.description
                summary = description.summary if description else command.help or "Résumé non résolu."
                purpose = description.user_purpose if description else "Usage opérateur non résolu."
                syntax = command.invocation
                if command.parameters:
                    syntax += " " + " ".join(f"{parameter.name}={parameter.name}" if parameter.required else f"[{parameter.name}={parameter.name}]" for parameter in command.parameters)
                lines.extend([f"#### `{command.name}`", "", f"Résumé : {summary}", f"Usage opérateur : {purpose}", "", "```bash", syntax, "```", "", "Paramètres :"])
                if command.parameters:
                    for parameter in command.parameters:
                        detail = parameter.description or parameter.help or "Paramètre démontré."
                        lines.append(f"- `{parameter.name}` ({'requis' if parameter.required else 'facultatif'}) — {detail}")
                else:
                    lines.append("- Aucun paramètre utilisateur démontré.")
                lines.append(f"Environnements : {', '.join(command.environment) or 'non précisé'}.")
                lines.append(f"Effet de bord démontré : {', '.join(command.destructive_effects) if command.destructive_effects else 'aucun effet de bord démontré'}.")
                lines.append(f"Provenance : {command.provenance or 'non précisée'}.")
                lines.append("")
            return "\n".join(lines).rstrip() + "\n"
        if section_identifier == "developer-commands":
            return "La référence complète des cibles Make est publiée dans le **Guide d’exploitation**. Aucune commande de test backend distincte n’est démontrée dans les faits disponibles.\n"
        if section_identifier in {"operator-environment-variables", "developer-development-configuration"}:
            lines = ["### Variables de configuration démontrées", ""]
            for variable in knowledge.environment_variables.get("variables", []):
                name = variable.get("name")
                if isinstance(name, str) and name:
                    lines.append(f"- `{name}`")
            return "\n".join([*lines, "", "Statut : fait détecté; noms uniquement.", ""])
        if section_identifier == "developer-presentation":
            return "Contact utilise les technologies détectées pour son application serveur et son interface web. Cette référence décrit uniquement les éléments techniques structurés disponibles.\n"
        if section_identifier == "developer-architecture":
            return "L’architecture démontrée associe une application Django à une interface React. Les routes sont centralisées dans la section **Routes et API**.\n"
        if section_identifier == "developer-services":
            lines = ["| Environnement | Service | Rôle |", "|---|---|---|"]
            for environment in knowledge.environments.get("items", []):
                for service in environment.get("services", []):
                    lines.append(f"| {environment.get('name') or environment.get('environment') or '—'} | {service.get('name') or '—'} | {service.get('role') or '—'} |")
            return "\n".join(lines) + "\n"
        if section_identifier == "developer-backend":
            apps = knowledge.django.get("installed_apps", []) if isinstance(knowledge.django, dict) else []
            return "\n".join(["Composants Django détectés :", *[f"- {item}" for item in apps]]) + "\n" if apps else "Les composants backend structurés sont décrits par les routes et capacités détectées.\n"
        if section_identifier == "developer-frontend":
            caps = knowledge.capabilities.get("capabilities", []) if isinstance(knowledge.capabilities, dict) else []
            labels = [item.get("label") for item in caps if isinstance(item, dict) and item.get("component") and item.get("label")]
            return "\n".join(["Capacités de l’interface détectées :", *[f"- {item}" for item in labels]]) + "\n" if labels else "Aucune capacité d’interface supplémentaire n’est structurée.\n"
        if section_identifier == "developer-authentication":
            django = knowledge.django if isinstance(knowledge.django, dict) else {}
            react = knowledge.react if isinstance(knowledge.react, dict) else {}
            mechanisms = list(dict.fromkeys([*django.get("auth_mechanisms", []), *react.get("auth_mechanisms", [])]))
            return "\n".join(["Mécanismes d’authentification détectés :", *[f"- {item}" for item in mechanisms], "", "Les routes et méthodes démontrées figurent dans **Routes et API**."]) + "\n"
        if section_identifier == "developer-models-capabilities":
            caps = knowledge.capabilities.get("capabilities", []) if isinstance(knowledge.capabilities, dict) else []
            lines = ["Capacités structurées démontrées :"]
            for item in caps:
                if isinstance(item, dict) and item.get("label"):
                    lines.append(f"- {item['label']}")
            return "\n".join(lines) + "\n"
        if section_identifier == "developer-missing-information":
            lines=[]
            for item in knowledge.missing_information:
                description=getattr(item, "description", "")
                if description and "pyproject.toml" not in description:
                    lines.append(f"- {description}")
            return "\n".join(lines) + ("\n" if lines else "- Aucune information technique manquante supplémentaire n’est structurée.\n")
        if section_identifier == "developer-routes-api":
            lines = ["### Routes et API démontrées", "", "| Route | Méthodes | Permissions |", "|---|---|---|"]
            routes = [
                route for route in knowledge.django.get("resolved_routes", [])
                if route.get("resolution_status") == "resolved"
            ]
            if routes:
                for route in routes:
                    lines.append("| " + " | ".join(str(value or "—").replace("|", "\\|") for value in (
                        route.get("full_path"), ", ".join(route.get("methods", [])), ", ".join(route.get("permissions", [])),
                    )) + " |")
            else:
                for endpoint in knowledge.django.get("endpoints", []):
                    lines.append("| " + " | ".join(str(value or "—").replace("|", "\\|") for value in (
                        endpoint.get("path"), ", ".join(endpoint.get("methods", [])), ", ".join(endpoint.get("permissions", [])),
                    )) + " |")
            return "\n".join([*lines, "", "Statut : fait détecté.", ""])
        if section_identifier in {"operator-protected-documents", "developer-invariants"}:
            lines = ["### Documents protégés et contrat démontré", ""]
            for document in knowledge.security.protected_documents:
                lines.append(f"- `{document}`")
            template = knowledge.template if isinstance(knowledge.template, dict) else {}
            for evidence in template.get("evidence", []):
                lines.append(f"- {evidence}")
            return "\n".join([*lines, "", "Statut : fait détecté.", ""])
        if section_identifier == "user-presentation":
            application = knowledge.application if isinstance(knowledge.application, dict) else {}
            name = application.get("name") or "L’application"
            if isinstance(name, str) and name:
                name = name[:1].upper() + name[1:]
            capabilities = knowledge.capabilities.get("capabilities", []) if isinstance(knowledge.capabilities, dict) else []
            labels = {item.get("label") for item in capabilities if isinstance(item, dict)}
            lines = [f"{name} est une application web auto-hébergée."]
            if any(isinstance(label, str) and "contacts" in label.casefold() for label in labels):
                lines.append("Elle permet la gestion de contacts et propose les fonctions utilisateur détectées dans ce guide.")
            return "\n".join(lines) + "\n"
        if section_identifier == "user-roles":
            capabilities = knowledge.capabilities.get("capabilities", []) if isinstance(knowledge.capabilities, dict) else []
            roles = {item.get("permission_condition") for item in capabilities if isinstance(item, dict)}
            lines = ["- Utilisateur connecté : accès aux fonctionnalités réservées aux utilisateurs authentifiés."] if "IsAuthenticated" in roles else []
            if "IsAdminUser" in roles:
                lines.append("- Administrateur fonctionnel : accès aux fonctions de gestion des utilisateurs.")
            return "\n".join(lines) + ("\n" if lines else "")
        if section_identifier == "user-access":
            endpoints = knowledge.service_endpoints.get("endpoints", []) if isinstance(knowledge.service_endpoints, dict) else []
            urls = [item.get("url") for item in endpoints if isinstance(item, dict) and item.get("service") == "frontend" and item.get("environment") == "prod" and item.get("validity") == "valid"]
            lines = [f"Accédez à l’application à l’adresse {urls[0]}." for _ in urls[:1]]
            lines.append("Une connexion est requise pour utiliser les fonctions protégées.")
            return "\n".join(lines) + "\n"
        if section_identifier == "user-authentication":
            return "Une connexion est requise pour utiliser les fonctions protégées de l’application.\n"
        if section_identifier == "user-main-features":
            capabilities = knowledge.capabilities.get("capabilities", []) if isinstance(knowledge.capabilities, dict) else []
            labels = {item.get("label") for item in capabilities if isinstance(item, dict)}
            facts = [
                ("Connexion", "Connexion"), ("Consulter contacts", "Consultation des contacts"),
                ("Créer contacts", "Création de contacts"), ("Modifier contacts", "Modification de contacts"),
                ("Supprimer contacts", "Suppression de contacts"), ("Recherche", "Recherche"),
                ("Aide", "Aide"), ("Changement de thème", "Changement de thème"),
                ("Gérer un coffre local chiffré côté client", "Coffre local chiffré côté client"),
                ("Révélation d’une valeur", "Affichage d’une valeur protégée"),
            ]
            lines = [f"- {rendered}" for source, rendered in facts if source in labels]
            if any(item.get("permission_condition") == "IsAdminUser" for item in capabilities if isinstance(item, dict)):
                lines.append("- Gestion des utilisateurs pour l’administrateur fonctionnel")
            return "\n".join(lines) + "\n"
        if section_identifier == "user-application-usage":
            endpoints = knowledge.service_endpoints.get("endpoints", []) if isinstance(knowledge.service_endpoints, dict) else []
            url = next((item.get("url") for item in endpoints if isinstance(item, dict) and item.get("service") == "frontend" and item.get("environment") == "prod" and item.get("validity") == "valid"), None)
            lines = []
            if url:
                lines.append(f"1. Accédez à l’application à l’adresse {url}.")
            lines.extend(["2. Connectez-vous pour accéder aux fonctions correspondant à votre rôle.", "3. Gérez vos contacts et utilisez la recherche lorsque ces fonctions sont disponibles."])
            crypto = knowledge.react.get("crypto", {}) if isinstance(knowledge.react, dict) else {}
            if crypto.get("detected"):
                lines.append("4. Utilisez le coffre local selon les comportements de verrouillage et de déverrouillage démontrés.")
            return "\n".join(lines) + "\n"
        if section_identifier == "user-functional-administration":
            capabilities = knowledge.capabilities.get("capabilities", []) if isinstance(knowledge.capabilities, dict) else []
            admin = [item.get("label") for item in capabilities if isinstance(item, dict) and item.get("permission_condition") == "IsAdminUser" and item.get("label")]
            if not admin:
                return "Aucune capacité d’administration fonctionnelle n’est démontrée.\n"
            lines = ["Les capacités suivantes sont réservées à l’administrateur fonctionnel :", *[f"- {label}" for label in admin]]
            return "\n".join(lines) + "\n"
        if section_identifier == "user-troubleshooting":
            return "Aucune procédure de dépannage destinée à l’utilisateur n’est démontrée dans les faits disponibles.\n"
        if section_identifier == "user-limitations":
            missing = knowledge.missing_information if isinstance(knowledge.missing_information, list) else []
            limitation_items = getattr(knowledge.limitations, "items", [])
            seen = set(); lines = []
            for item in [*missing, *limitation_items]:
                category = item.get("category") if isinstance(item, dict) else getattr(item, "category", None)
                affected = item.get("affected_sections", []) if isinstance(item, dict) else getattr(item, "affected_sections", [])
                # A user guide reports only user-relevant unknowns, never
                # operational or API gaps which belong to the other documents.
                if category not in {"security", "authentication", "user"} and not {"security", "authentication-accounts"}.intersection(affected or []):
                    continue
                description = item.get("description") if isinstance(item, dict) else getattr(item, "description", None)
                if isinstance(description, str) and description and description not in seen:
                    seen.add(description); lines.append(f"- {description}")
            return "\n".join(lines) + ("\n" if lines else "- Aucune limite supplémentaire n’est démontrée dans les faits disponibles.\n")
        if section_identifier in {"user-security", "operator-security", "developer-security"}:
            audience = section_identifier.removesuffix("-security")
            lines = ["### Contrôles de sécurité démontrés", ""]
            if audience == "user":
                lines.extend(["| Sujet | Consigne |", "|---|---|"])
                lines.append("| Connexion | Utilisez votre compte pour accéder aux fonctions protégées. |")
                lines.append("| Informations sensibles | Ne publiez pas d’informations sensibles dans vos échanges ou captures. |")
                crypto = knowledge.react.get("crypto", {}) if isinstance(knowledge.react, dict) else {}
                if crypto.get("detected"):
                    lines.append("| Données privées | Elles sont chiffrées côté client avant stockage et déchiffrées localement pendant l’utilisation. |")
                    if crypto.get("recovery_supported") is None:
                        lines.append("| Récupération | Aucune procédure de récupération n’est démontrée. |")
            else:
                lines.extend(["| Identifiant | Catégorie | Règle | Preuve |", "|---|---|---|"])
                for control in knowledge.security.controls:
                    evidence = control.get("evidence") or []
                    rendered_evidence = ", ".join(str(item) for item in evidence) if isinstance(evidence, list) else str(evidence)
                    lines.append("| " + " | ".join(str(value or "—").replace("|", "\\|") for value in (control.get("identifier"), control.get("category"), control.get("description"), rendered_evidence)) + " |")
            if audience == "user":
                return "\n".join([*lines, ""])
            return "\n".join([*lines, "", self._status(knowledge.security.source.status), ""])
        if section_identifier == "security":
            lines = ["### Contrôles de sécurité démontrés", "", "| Identifiant | Catégorie | Règle | Preuve |", "|---|---|---|---|"]
            for control in knowledge.security.controls:
                evidence = control.get("evidence") or []
                rendered_evidence = ", ".join(str(item) for item in evidence) if isinstance(evidence, list) else str(evidence)
                lines.append("| " + " | ".join(str(value or "—").replace("|", "\\|") for value in (control.get("identifier"), control.get("category"), control.get("description"), rendered_evidence)) + " |")
            return "\n".join([*lines, "", self._status(knowledge.security.source.status), ""])
        if section_identifier == "protected-documents":
            lines = ["### Documents protégés et application", ""]
            for document in knowledge.security.protected_documents:
                lines.append(f"- `{document}`")
            apply = next((command for command in knowledge.commands if command.command_path == "apply"), None)
            if apply is not None:
                lines.extend(["", "#### Commande d’application", "", "```bash", self._syntax(apply), "```", ""])
                for parameter in apply.parameters:
                    if parameter.kind == "option":
                        lines.append(f"- Option `{' / '.join(parameter.flags) or parameter.name}` ({'requis' if parameter.required else 'facultatif'})")
            return "\n".join([*lines, "", self._status(knowledge.security.source.status), ""])
        if section_identifier != "cli-reference":
            return ""
        lines = ["### Entrées de la référence CLI", ""]
        for command in knowledge.commands:
            if command.visibility != "public" or command.documentation_policy == "exclude" or command.reference_level == "omit":
                continue
            description = command.description
            summary = (
                description.summary
                if description is not None
                else command.help or "Description non résolue."
            )
            purpose = (
                description.user_purpose
                if description is not None
                else "Usage à préciser à partir de sources supplémentaires."
            )
            behavior = (
                description.behavior
                if description is not None
                else summary
            )
            lines.extend([
                f"#### `{command.command_path}`", "", summary, "",
                f"Quand l’utiliser : {purpose}", "", "```bash",
                self._syntax(command), "```", "", "Arguments :",
            ])
            arguments = [
                parameter for parameter in command.parameters
                if parameter.kind == "argument"
            ]
            if arguments:
                for parameter in arguments:
                    lines.append(self._parameter_line(parameter))
            else:
                lines.append("- Aucun paramètre positionnel démontré.")
            lines.extend(["", "Options :"])
            options = [
                parameter for parameter in command.parameters
                if parameter.kind == "option"
            ]
            if options:
                for parameter in options:
                    lines.append(self._parameter_line(parameter))
            else:
                lines.append("- Aucune option démontrée.")
            lines.extend(["", "Résultat ou effet :", f"- Comportement démontré : {behavior}"])
            if description is not None:
                if description.outputs:
                    lines.extend(f"- Sortie ou artefact : {item}" for item in description.outputs)
                if description.side_effects:
                    lines.extend(f"- Effet de bord : {item}" for item in description.side_effects)
                if description.next_step:
                    lines.append(f"- Étape suivante démontrée : `{description.next_step}`")
                unresolved = [
                    name for name in ("outputs", "side_effects", "next_step")
                    if description.provenance.get(name, command.source).status == "unresolved"
                ]
                if unresolved:
                    lines.append("- Sorties, effets de bord et étape suivante : non résolus dans les faits disponibles.")
            lines.extend(["", self._status(command.source.status), ""])
        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _option_expects_value(parameter) -> bool:
        annotation = (parameter.type_annotation or "").replace(" ", "")
        return annotation not in {"bool", "None", ""}

    @classmethod
    def _parameter_token(cls, parameter) -> str:
        if parameter.kind == "argument":
            return parameter.name
        primary = next(
            (flag for flag in parameter.flags if flag.startswith("--")),
            parameter.flags[0] if parameter.flags else parameter.name,
        )
        if cls._option_expects_value(parameter):
            metavar = parameter.name.lstrip("-").replace("-", "_").upper()
            return f"{primary} {metavar}"
        return primary

    @classmethod
    def _parameter_line(cls, parameter) -> str:
        token = cls._parameter_token(parameter)
        requirement = "requis" if parameter.required else "facultatif"
        detail = parameter.help or "Description non résolue."
        line = f"- `{token}` ({requirement}) — {detail}"
        aliases = [flag for flag in parameter.flags if flag != token.split()[0]]
        if aliases:
            line += " Alias : " + ", ".join(f"`{alias}`" for alias in aliases) + "."
        return line

    @classmethod
    def _syntax(cls, command) -> str:
        tokens = [command.invocation]
        for parameter in command.parameters:
            if parameter.kind not in {"argument", "option"}:
                continue
            token = cls._parameter_token(parameter)
            tokens.append(token if parameter.required else f"[{token}]")
        return " ".join(tokens)

    def _status(self, status: str) -> str:
        label = self._STATUS_LABELS.get(status, "statut non précisé")
        if status == "configured":
            return f"Statut : {label}; ce n’est pas un comportement observé."
        if status == "derived":
            return f"Statut : {label}; formulation prudente."
        if status == "unresolved":
            return f"Statut : {label}; aucune procédure supplémentaire n’est déduite."
        return f"Statut : {label}."
