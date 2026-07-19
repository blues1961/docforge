from __future__ import annotations

import re
from typing import Any

from docforge.validators.manual_markdown import ManualMarkdownDiagnostic


class ContactUserGuideValidator:
    """Audience and fact-consistency checks for the django-react user guide."""

    TECHNICAL_TERMS = re.compile(r"\b(?:IsAuthenticated|IsAdminUser|django-react|backend|frontend|Django|routes?|api_calls|variables? d[’']environnement|[A-Z][A-Z0-9_]{2,}=)\b", re.I)
    CRYPTO_OVERPROMISES = re.compile(r"confidentialité (?:garantie|préservée)|serveur (?:incapable|ne .*accéder)|zero[ -]?knowledge|aucune intervention serveur|récupération impossible|sécurité (?:auditée|garantie)", re.I)
    CORRUPTED = re.compile(r"\b(?:déchifré|révélélation|révéléation|révélément)\b", re.I)

    def validate(self, markdown: str, knowledge: dict[str, Any]) -> list[ManualMarkdownDiagnostic]:
        diagnostics: list[ManualMarkdownDiagnostic] = []
        lines = markdown.splitlines()
        section = None
        for number, text in enumerate(lines, start=1):
            if text.startswith("## "):
                section = text[3:].strip()
            if self.TECHNICAL_TERMS.search(text):
                diagnostics.append(ManualMarkdownDiagnostic("CONTACT001", "error", "Le guide utilisateur contient une terminologie technique interdite.", section, text.strip(), number))
            if self.CRYPTO_OVERPROMISES.search(text):
                diagnostics.append(ManualMarkdownDiagnostic("CONTACT002", "error", "Le guide utilisateur promet un effet cryptographique non démontré.", section, text.strip(), number))
            if self.CORRUPTED.search(text):
                diagnostics.append(ManualMarkdownDiagnostic("CONTACT003", "error", "Le guide contient une formulation française corrompue.", section, text.strip(), number))
        body = markdown.casefold()
        app = knowledge.get("application", {})
        endpoints = knowledge.get("service_endpoints", {}).get("endpoints", [])
        url = next((x.get("url") for x in endpoints if x.get("service") == "frontend" and x.get("environment") == "prod" and x.get("validity") == "valid"), None)
        crypto = knowledge.get("react", {}).get("crypto", {})
        contradictions = [
            (bool(knowledge.get("django", {}).get("auth_mechanisms") or knowledge.get("react", {}).get("auth_mechanisms")) and re.search(r"(?:n'est pas|aucune) .*authentification|required.*non", body), "L’authentification démontrée est niée."),
            (bool(crypto.get("detected")) and re.search(r"(?:coffre|vault).*?(?:inconnu|n.a été démontré|absent)", body), "Le coffre local détecté est déclaré inconnu ou absent."),
            (bool(url) and re.search(r"aucune url|url .*?(?:inconnue|absente|n.a été détectée)", body), "L’URL de production démontrée est déclarée absente."),
            (bool(app.get("name")) and re.search(r"nom .*?(?:inconnu|non identifié)", body), "Le nom de l’application démontré est déclaré inconnu."),
            (crypto.get("recovery_supported") is None and re.search(r"récupération .*?(?:impossible|n'existe pas|inexistante)", body), "Une procédure non démontrée est transformée en impossibilité."),
        ]
        for triggered, message in contradictions:
            if triggered:
                diagnostics.append(ManualMarkdownDiagnostic("CONTACT004", "error", message))
        for fact in ("coffre local", "authentification", "données privées"):
            if body.count(fact) > 4:
                diagnostics.append(ManualMarkdownDiagnostic("CONTACT006", "warning", "Un même fait est répété de manière excessive.", fact=fact))

        # A non-empty canonical section needs actual prose or a deterministic table/list.
        positions = [i for i, line in enumerate(lines) if line.startswith("## ")]
        for pos in positions:
            end = next((i for i in positions if i > pos), len(lines))
            content = [line.strip() for line in lines[pos + 1:end] if line.strip() and not line.startswith("### ")]
            if not content:
                diagnostics.append(ManualMarkdownDiagnostic("CONTACT005", "error", "Une section obligatoire est vide.", lines[pos][3:].strip(), line=pos + 1))
        return diagnostics
