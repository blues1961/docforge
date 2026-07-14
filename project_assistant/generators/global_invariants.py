from __future__ import annotations

from datetime import date

from project_assistant.analyzers import TemplateFacts


class GlobalInvariantsGenerator:
    def generate(self, facts: TemplateFacts) -> str:
        lines = [
            "# Invariants globaux des applications auto-hébergées",
            "",
            "<!--",
            "Document généré par project-assistant à partir du dépôt app-template.",
            "Ne pas modifier manuellement sans mettre également à jour app-template.",
            "-->",
            "",
            f"Source canonique : `{facts.root}`",
            "",
            f"Date de génération : `{date.today().isoformat()}`",
            "",
            "## Portée",
            "",
            (
                "Ces invariants s’appliquent aux applications "
                "auto-hébergées dérivées de `app-template`."
            ),
            "",
            (
                "Les sites statiques, les dépôts de conception 3D et les "
                "autres catégories de projets utilisent des profils distincts "
                "et ne sont pas couverts par ce document."
            ),
            "",
            "## Socle technologique canonique",
            "",
            f"- Langages détectés : {self._code_list(facts.languages)}.",
            f"- Frameworks détectés : {self._code_list(facts.frameworks)}.",
            f"- Technologies détectées : {self._code_list(facts.technologies)}.",
            "",
            "## Structure canonique",
            "",
            f"- Dossiers racine détectés : {self._code_list(facts.root_directories)}.",
            f"- Fichiers racine détectés : {self._code_list(facts.root_files)}.",
            "",
            "### Documentation présente dans le template",
            "",
        ]

        authoritative_documents = [
            rule.path
            for rule in facts.documents
            if rule.source_authoritative
        ]

        lines.extend(
            f"- `{path}`"
            for path in authoritative_documents
        )

        lines.extend(
            [
                "",
                "### Fichiers Docker Compose",
                "",
            ]
        )

        lines.extend(
            f"- `{rule.path}`"
            for rule in facts.compose_files
            if rule.source_authoritative
        )

        lines.extend(
            [
                "",
                "### Scripts canoniques",
                "",
            ]
        )

        lines.extend(
            f"- `{script}`"
            for script in facts.scripts
        )

        lines.extend(
            [
                "",
                "### Interface Makefile",
                "",
            ]
        )

        lines.extend(
            f"- `make {target}`"
            for target in facts.make_targets
        )

        lines.extend(
            [
                "",
                "## Environnements et secrets",
                "",
            ]
        )

        if facts.env_template_file:
            lines.append(
                f"- Le modèle de configuration canonique est `{facts.env_template_file}`."
            )

        lines.extend(
            [
                "- Les fichiers d’environnement actifs sont générés ou initialisés à partir du modèle canonique.",
                "- Les secrets ne doivent pas être intégrés au dépôt Git.",
                "- Les secrets locaux appartiennent aux fichiers `.local` prévus par le projet.",
                "- Le choix de l’environnement actif doit passer par les scripts et cibles Makefile du template.",
                "",
                "## Architecture Docker canonique",
                "",
            ]
        )

        architecture = facts.architecture

        if architecture is not None:
            lines.extend(
                [
                    f"- Services : {self._code_list([service.name for service in architecture.services])}.",
                    f"- Réseaux : {self._code_list(architecture.networks)}.",
                    f"- Réseaux externes : {self._code_list(architecture.external_networks)}.",
                    f"- Volumes : {self._code_list(architecture.volumes)}.",
                ]
            )

            if architecture.uses_traefik:
                lines.append(
                    "- Traefik constitue le point d’entrée HTTP/HTTPS de production."
                )

            if architecture.uses_postgresql:
                lines.append(
                    "- PostgreSQL constitue la base de données relationnelle canonique."
                )

        lines.extend(
            [
                "",
                "## Invariants explicitement définis par app-template",
                "",
            ]
        )

        for section in facts.invariant_sections:
            if section.level == 1:
                continue

            level = min(section.level + 1, 6)
            lines.append(
                f"{'#' * level} {section.title}"
            )
            lines.append("")

            if section.body:
                lines.append(section.body)
            else:
                lines.append("_Section sans contenu textuel._")

            lines.append("")

        lines.extend(
            [
                "## Relation entre invariants globaux et invariants locaux",
                "",
                "L’ordre d’autorité est le suivant :",
                "",
                "1. `app-template/INVARIANTS.md` définit les règles globales.",
                "2. Le profil d’application complète ces règles pour une famille technologique.",
                "3. Le fichier `INVARIANTS.md` d’une application documente ses contraintes particulières.",
                "",
                (
                    "Une application peut ajouter des règles locales, mais elle "
                    "ne doit pas contredire un invariant global sans documenter "
                    "explicitement l’écart."
                ),
                "",
            ]
        )

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _code_list(values: list[str]) -> str:
        if not values:
            return "`aucun`"

        return ", ".join(
            f"`{value}`"
            for value in values
        )
