from __future__ import annotations

import json
from typing import Any

from docforge.manual_blueprint import (
    ManualBlueprint,
    ManualSectionDefinition,
)
from docforge.manual_knowledge import ManualKnowledge


class ManualPromptBuilder:
    GLOBAL_RULES = (
        "Rédige un guide utilisateur en Markdown.",
        "Utilise `manual-knowledge.json` comme source unique de vérité et n’utilise aucune connaissance externe pour compléter les procédures ou les caractéristiques du projet.",
        "Suis strictement le blueprint fourni.",
        "N’invente jamais une commande, une option, une procédure, une route, une URL, un paramètre, une variable, un service ou une fonctionnalité.",
        "N’ajoute pas de bonnes pratiques générales comme si elles étaient démontrées par le projet.",
        "Utilise toujours `command_path` pour référencer les commandes.",
        "Vérifie silencieusement chaque commande, paramètre, route, URL, variable, service, permission, workflow et champ cité avant de rédiger; cette vérification ne doit pas apparaître dans le manuel.",
        "Signale explicitement les informations manquantes et les limites sans reconstruire arbitrairement des faits absents.",
        "Ne produis jamais de chemin local propre à une machine.",
        "N’ajoute jamais de référence de citation interne comme `oaicite`.",
        "N’expose jamais de secret ni de valeur sensible; seuls les noms non sensibles ou les noms de variables peuvent être cités.",
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

    def rules(
        self,
        blueprint: ManualBlueprint,
    ) -> tuple[str, ...]:
        return (
            *self.GLOBAL_RULES,
            *self.FACT_STATUS_RULES,
            *self.STYLE_RULES,
        )

    def build_full_prompt(
        self,
        *,
        knowledge: ManualKnowledge,
        blueprint: ManualBlueprint,
    ) -> str:
        payload = knowledge.to_dict()
        blueprint_payload = {
            "profile_name": blueprint.profile_name,
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
            "BEGIN MANUAL KNOWLEDGE",
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            "END MANUAL KNOWLEDGE",
            "",
        ]
        return "\n".join(lines)

    def build_section_prompt(
        self,
        *,
        blueprint: ManualBlueprint | None = None,
        section: ManualSectionDefinition,
        projected_facts: dict[str, Any],
    ) -> str:
        effective_blueprint = blueprint or ManualBlueprint(
            profile_name="generic"
        )
        lines = [
            "BEGIN INSTRUCTIONS",
            *self.rules(effective_blueprint),
            *self.section_guidance(
                blueprint=effective_blueprint,
                section=section,
            ),
            f"Titre de section : {section.title}",
            f"But : {section.purpose}",
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
        return "\n".join(lines)

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
    def project_section_facts(
        knowledge: ManualKnowledge,
        section: ManualSectionDefinition,
    ) -> dict[str, Any]:
        payload = knowledge.to_dict()
        projection: dict[str, Any] = {}

        for path in section.required_fact_paths:
            value = ManualPromptBuilder._extract_path(
                payload,
                path,
            )
            ManualPromptBuilder._assign_path(
                projection,
                path,
                value,
            )

        return projection

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


class DjangoReactManualPromptBuilder(ManualPromptBuilder):
    DJANGO_REACT_RULES = (
        "Le manuel concerne l’application analysée, jamais DocForge comme produit utilisateur.",
        "Les commandes DocForge ne sont pas des commandes d’utilisation de l’application analysée.",
        "Le manuel ne doit pas commencer par Docker, les variables d’environnement ou l’infrastructure; il doit d’abord expliquer l’application et ce que l’utilisateur peut faire.",
        "Distingue clairement trois publics lorsque les faits le permettent : utilisateur de l’application, administrateur applicatif et exploitant.",
        "Formule prudemment toute capacité marquée `derived` et ne la présente jamais comme validée en fonctionnement.",
        "Sépare strictement les environnements de développement et de production.",
        "N’affiche jamais une valeur secrète.",
        "Omet toute procédure dont une commande critique est absente.",
        "Utilise `missing_information` et `limitations.items` comme source prioritaire pour la section des limites, sans reconstruire arbitrairement les absences depuis le JSON brut.",
        "Les mentions locales d’une information manquante doivent rester limitées aux cas où elles sont nécessaires à la sécurité ou à l’exécution; consolide le reste dans la section finale des limites.",
        "Lorsqu’un conflit structuré est présent dans `conflicts`, présente-le clairement, n’arbitre jamais entre les valeurs contradictoires et ne décris pas comme validée une procédure affectée par ce conflit.",
        "Pour les routes Django, utilise uniquement `full_path` lorsque `resolution_status` vaut `resolved`; ne compose jamais manuellement un chemin public à partir d’une route relative non résolue.",
        "Ne présente jamais simultanément une route relative comme `/auth/login/` et son chemin public résolu comme deux endpoints publics distincts.",
        "Pour les endpoints, utilise les méthodes, permissions, mécanismes d’authentification, paramètres de route et sources rattachés à chaque endpoint; n’attribue jamais des permissions globales à tous les endpoints ou à tous les utilisateurs.",
        "Ne déclare pas qu’un utilisateur peut créer, modifier ou supprimer une ressource sans preuve provenant de l’endpoint ou du workflow correspondant.",
        "Respecte `workflows.operational_status` : un workflow `requires-context` ne doit jamais être présenté comme immédiatement exécutable et doit garder son contexte manquant explicite.",
        "Ne présente jamais `make check` comme une suite de tests lorsqu’il correspond à une vérification d’invariants ou de diagnostic.",
        "Associe `make migrate` à la création ou mise à jour de l’administrateur uniquement si la chaîne démontrée vers `python manage.py ensure_admin` est explicitement présente dans ManualKnowledge.",
        "Pour les commandes Make, respecte les paramètres structurés de `commands.parameters`, leur caractère facultatif et leurs exemples; n’invente ni nouveaux paramètres ni nouvelles valeurs de service.",
        "Pour la base de données, respecte les contextes fournis par ManualKnowledge, par exemple exécution vs test; ne transforme pas automatiquement une différence de contexte en contradiction.",
        "Les métadonnées de `django.models.fields` priment sur toute intuition: type, `required`, `null`, `blank`, `default`, `choices`, relation, unicité et autres contraintes détectées doivent être utilisées telles quelles.",
        "Pour `react.crypto`, décris uniquement l’implémentation détectée et jamais une garantie de sécurité, un audit, une récupération existante ou un modèle zero knowledge non démontré.",
        "En mode strict, n’ajoute pas de recommandations générales de sécurité comme MFA, rotation des secrets, VPN ou sauvegarde hors site si elles ne figurent pas dans ManualKnowledge.",
        "Le manuel final doit rester lisible: le démarrage rapide est court, l’exploitation détaille les procédures nécessaires, et la référence des commandes évite de dupliquer les listes dans toutes les sections.",
        "Chaque catégorie d’information doit avoir une section principale : présentation des services dans `Architecture et référence technique`, URLs dev/prod dans `Installation et configuration`, séquence minimale dans `Démarrage rapide`, détail des commandes et paramètres Make dans `Référence des commandes`, permissions dans `Administration` ou `API`, chiffrement dans `Architecture et référence technique` ou `Sécurité`, sauvegarde et restauration dans `Exploitation`, limitations dans `Limites des informations disponibles`.",
        "Ne recopie pas intégralement la liste des commandes, des services, des variables, des URLs ou des endpoints dans plusieurs sections; ailleurs, ne fais qu’une mention brève quand c’est nécessaire à la compréhension.",
        "Le démarrage rapide doit contenir uniquement la sélection du développement, l’initialisation, le démarrage, les migrations si elles sont nécessaires, et l’URL principale; n’y explique pas tous les services, toutes les variables ni toute l’architecture.",
        "La section de référence des commandes doit contenir les détails opérationnels : commande, fonction, environnement, paramètres facultatifs, statut opérationnel et contexte requis. Les autres sections ne doivent pas recopier cette référence.",
        "N’expose pas dans le manuel final un vocabulaire interne comme `workflow structuré`, `fait structuré`, `permission structurée`, `requires-context`, `ManualKnowledge`, `ProjectKnowledge`, `dataclass`, `builder`, `projection` ou `pipeline documentaire`.",
        "Transforme toujours les identifiants techniques de limites ou d’informations manquantes en phrases lisibles, par exemple `PROJECT-VERSION-MISSING` devient une phrase telle que la version de l’application n’est pas indiquée.",
        "Décris la section d’utilisation avec un langage fonctionnel orienté utilisateur; n’invente ni boutons, ni messages affichés, ni captures d’écran, ni parcours non démontrés.",
    )

    SECTION_RULES = {
        "quick-start": (
            "Cette section reste courte et ne contient que la séquence minimale pour démarrer l’application et atteindre l’URL principale.",
            "N’y recopie pas l’inventaire complet des services, variables, paramètres Make ou procédures d’exploitation.",
        ),
        "application-usage": (
            "Cette section vient avant l’infrastructure détaillée et doit privilégier les usages concrets : connexion, consultation, recherche, création, modification, visibilité, contacts privés et synchronisation lorsque ces comportements sont démontrés.",
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
    }

    def rules(
        self,
        blueprint: ManualBlueprint,
    ) -> tuple[str, ...]:
        return (*super().rules(blueprint), *self.DJANGO_REACT_RULES)

    def additional_guidance(
        self,
        *,
        knowledge: ManualKnowledge,
        blueprint: ManualBlueprint,
    ) -> tuple[str, ...]:
        return (
            "Le flux de DocForge s’arrête à la production de `manual-knowledge.json` et du prompt de rédaction; tu ne dois pas prétendre que DocForge a rédigé ou validé le manuel final.",
            "Le document peut rester unique, mais fais apparaître sans ambiguïté les sections destinées aux utilisateurs, aux administrateurs et aux exploitants.",
            "Les URLs résolues peuvent être citées; lorsqu’une URL ou un port reste symbolique dans ManualKnowledge, conserve cette forme au lieu d’inventer une valeur.",
        )

    def section_guidance(
        self,
        *,
        blueprint: ManualBlueprint,
        section: ManualSectionDefinition,
    ) -> tuple[str, ...]:
        return self.SECTION_RULES.get(section.identifier, ())
