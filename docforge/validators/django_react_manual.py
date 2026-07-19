from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class DjangoReactManualDiagnostic:
    code: str
    message: str
    document_id: str | None = None
    section: str | None = None


class DjangoReactMultiDocumentValidator:
    """Validate audience separation in a prepared django-react application manual."""

    EXPECTED_DOCUMENTS = {
        "user-guide": (
            "Guide utilisateur",
            (
                "Présentation", "Public visé et rôles", "Accès à l’application",
                "Authentification", "Fonctionnalités principales",
                "Utilisation de l’application", "Administration fonctionnelle",
                "Sécurité pour l’utilisateur", "Dépannage",
                "Limites des informations disponibles",
            ),
        ),
        "operator-guide": (
            "Guide d’exploitation",
            (
                "Présentation opérationnelle", "Prérequis démontrés",
                "Environnements développement et production",
                "Installation et configuration", "Services Docker Compose",
                "Commandes Make", "Démarrage et arrêt",
                "Migrations et administration", "Sauvegarde et restauration",
                "Déploiement", "Variables de configuration, noms uniquement",
                "Documents protégés et contrat app-template", "Sécurité",
                "Dépannage", "Limites des informations disponibles",
            ),
        ),
        "developer-reference": (
            "Référence développeur",
            (
                "Présentation technique", "Architecture Django et React",
                "Organisation des services", "Backend", "Frontend",
                "Authentification", "Routes et API",
                "Modèles ou capacités démontrées",
                "Configuration de développement",
                "Commandes de développement et de test",
                "Invariants techniques", "Sécurité",
                "Informations techniques manquantes",
            ),
        ),
    }

    def validate(self, *, root: Path, manifest: dict[str, Any]) -> list[DjangoReactManualDiagnostic]:
        diagnostics: list[DjangoReactManualDiagnostic] = []
        documents = manifest.get("documents")
        if not isinstance(documents, list):
            return [DjangoReactManualDiagnostic("DJANGO_MANUAL001", "Le manifeste ne déclare pas les documents préparés.")]

        by_id = {item.get("identifier"): item for item in documents if isinstance(item, dict)}
        if set(by_id) != set(self.EXPECTED_DOCUMENTS):
            diagnostics.append(DjangoReactManualDiagnostic(
                "DJANGO_MANUAL002",
                "Une application django-react app-template doit préparer exactement user-guide, operator-guide et developer-reference.",
            ))
            return diagnostics

        absolute_pattern = re.compile(r"(?:^|[\s\"'])/(?:home|Users)/[^\s\"']+")
        expected_outputs = manifest.get("expected_outputs", [])
        for relative in expected_outputs:
            if not isinstance(relative, str) or relative.endswith("/"):
                continue
            candidate = root / relative
            if candidate.is_file() and absolute_pattern.search(candidate.read_text(encoding="utf-8")):
                diagnostics.append(DjangoReactManualDiagnostic("DJANGO_MANUAL014", "Un artefact contient un chemin absolu propre à une machine."))
                break

        contexts: dict[str, dict[str, dict[str, Any]]] = {}
        for identifier, (title, expected_titles) in self.EXPECTED_DOCUMENTS.items():
            document = by_id[identifier]
            if document.get("title") != title:
                diagnostics.append(DjangoReactManualDiagnostic("DJANGO_MANUAL003", "Le titre du document ne correspond pas au blueprint canonique.", identifier))
            entries = document.get("section_contexts", [])
            titles = [item.get("title") for item in entries if isinstance(item, dict)]
            if tuple(titles) != expected_titles:
                diagnostics.append(DjangoReactManualDiagnostic("DJANGO_MANUAL004", "Les sections ne correspondent pas au blueprint canonique ou ne sont pas dans le bon ordre.", identifier))
            contexts[identifier] = {}
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                context_file = entry.get("context_file")
                if not isinstance(context_file, str):
                    diagnostics.append(DjangoReactManualDiagnostic("DJANGO_MANUAL005", "Un contexte de section est absent du manifeste.", identifier, entry.get("identifier")))
                    continue
                candidate = root / context_file
                if not candidate.is_file():
                    diagnostics.append(DjangoReactManualDiagnostic("DJANGO_MANUAL006", "Le fichier de contexte déclaré est introuvable.", identifier, entry.get("identifier")))
                    continue
                payload = json.loads(candidate.read_text(encoding="utf-8"))
                contexts[identifier][entry.get("identifier", "")] = payload.get("facts", {})
                deterministic = entry.get("deterministic_file")
                if not isinstance(deterministic, str) or not (root / deterministic).is_file():
                    diagnostics.append(DjangoReactManualDiagnostic("DJANGO_MANUAL007", "Le fragment déterministe associé à la section est absent.", identifier, entry.get("identifier")))

        user_facts = contexts.get("user-guide", {})
        for section, facts in user_facts.items():
            if not isinstance(facts, dict):
                continue
            if "operational_commands" in facts or "environment_variables" in facts:
                diagnostics.append(DjangoReactManualDiagnostic("DJANGO_MANUAL008", "Le guide utilisateur ne doit pas contenir de commandes d’exploitation ni de variables de configuration.", "user-guide", section))
            django = facts.get("django")
            if isinstance(django, dict) and any(django.get(key) for key in ("resolved_routes", "routers")):
                diagnostics.append(DjangoReactManualDiagnostic("DJANGO_MANUAL009", "Le guide utilisateur ne doit pas contenir une référence détaillée des routes API.", "user-guide", section))

        operator = contexts.get("operator-guide", {})
        if not operator.get("operator-make-commands", {}).get("operational_commands"):
            diagnostics.append(DjangoReactManualDiagnostic("DJANGO_MANUAL010", "Les commandes Make démontrées sont absentes du guide d’exploitation.", "operator-guide", "operator-make-commands"))
        operator_manifest = by_id.get("operator-guide", {})
        make_entry = next((item for item in operator_manifest.get("section_contexts", []) if item.get("identifier") == "operator-make-commands"), {})
        make_file = root / make_entry.get("deterministic_file", "")
        if make_file.is_file():
            rendered = make_file.read_text(encoding="utf-8")
            headings = re.findall(r"^#### `([^`]+)`", rendered, flags=re.M)
            grouped = operator.get("operator-make-commands", {}).get("operational_commands", {})
            expected_count = len(grouped.get("primary_commands", [])) + len(grouped.get("advanced_commands", []))
            if len(headings) != expected_count or len(set(headings)) != expected_count:
                diagnostics.append(DjangoReactManualDiagnostic("DJANGO_MANUAL015", "Chaque commande Make détectée doit avoir un résumé utile et distinct.", "operator-guide", "operator-make-commands"))
        developer = contexts.get("developer-reference", {})
        routes = developer.get("developer-routes-api", {}).get("django", {}).get("resolved_routes", [])
        for identifier, section in (("operator-guide", "operator-protected-documents"), ("developer-reference", "developer-invariants")):
            facts = contexts.get(identifier, {}).get(section, {})
            protected = facts.get("security", {}).get("protected_documents", []) if isinstance(facts, dict) else []
            if "INVARIANTS.md" not in protected:
                diagnostics.append(DjangoReactManualDiagnostic("DJANGO_MANUAL012", "INVARIANTS.md doit être présent pour le contrat app-template démontré.", identifier, section))

        for identifier, section in (("operator-guide", "operator-environment-variables"), ("developer-reference", "developer-development-configuration")):
            variables = contexts.get(identifier, {}).get(section, {}).get("environment_variables", {}).get("variables", [])
            if any(set(item) - {"name", "sensitive"} for item in variables if isinstance(item, dict)):
                diagnostics.append(DjangoReactManualDiagnostic("DJANGO_MANUAL013", "Les contextes de variables ne doivent contenir que les noms et leur caractère sensible.", identifier, section))
        return diagnostics
