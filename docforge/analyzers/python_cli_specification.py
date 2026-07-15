from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from docforge.knowledge import ProjectKnowledge




@dataclass(slots=True)
class PythonCliSpecificationFacts:
    project_name: str
    package_name: str | None
    version: str | None
    requires_python: str | None

    purpose: str
    scope: list[str] = field(default_factory=list)
    out_of_scope: list[str] = field(default_factory=list)

    supported_profiles: list[str] = field(default_factory=list)
    required_documents: list[str] = field(default_factory=list)
    deterministic_documents: list[str] = field(default_factory=list)
    protected_documents: list[str] = field(default_factory=list)

    cli_commands: dict[str, str] = field(default_factory=dict)

    functional_requirements: list[str] = field(
        default_factory=list
    )
    non_functional_requirements: list[str] = field(
        default_factory=list
    )
    security_requirements: list[str] = field(
        default_factory=list
    )
    acceptance_criteria: list[str] = field(
        default_factory=list
    )
    known_limitations: list[str] = field(
        default_factory=list
    )


class PythonCliSpecificationAnalyzer:
    def analyze(
        self,
        knowledge: "ProjectKnowledge",
    ) -> PythonCliSpecificationFacts:
        profile_policy = knowledge.profile.document_policy
        pyproject = knowledge.pyproject

        return PythonCliSpecificationFacts(
            project_name=knowledge.identity.name,
            package_name=pyproject.package_name,
            version=pyproject.version,
            requires_python=pyproject.requires_python,
            purpose=(
                "Analyser des dépôts logiciels, construire une "
                "connaissance structurée, générer leur documentation "
                "et vérifier leur conformité."
            ),
            scope=[
                "scanner des dépôts locaux;",
                "détecter les langages, frameworks et technologies;",
                "détecter un profil de projet;",
                "construire et sérialiser ProjectKnowledge;",
                "générer des documents déterministes;",
                "utiliser un LLM local uniquement lorsque nécessaire;",
                "produire des aperçus sans modifier les fichiers cibles;",
                "appliquer explicitement des documents validés;",
                "auditer plusieurs projets enregistrés;",
                "protéger les invariants approuvés.",
            ],
            out_of_scope=[
                "modifier automatiquement le code métier des projets;",
                "déployer directement les applications analysées;",
                "gérer ou stocker les secrets des projets;",
                "remplacer une validation humaine pour les documents "
                "protégés;",
                "présenter une heuristique comme un fait certain.",
            ],
            supported_profiles=[
                "django-react",
                "python-cli",
                "generic",
            ],
            required_documents=list(
                profile_policy.required_documents
            ),
            deterministic_documents=list(
                profile_policy.deterministic_documents
            ),
            protected_documents=list(
                profile_policy.protected_documents
            ),
            cli_commands=dict(pyproject.scripts),
            functional_requirements=[
                "Le système doit accepter le chemin d’un projet local.",
                "Le système doit scanner le projet sans lire ses secrets.",
                "Le système doit détecter les technologies à partir de "
                "preuves présentes dans le dépôt.",
                "Le système doit sélectionner le profil spécialisé ayant "
                "le meilleur score valide.",
                "Le système doit utiliser le profil generic lorsqu’aucun "
                "profil spécialisé n’atteint le seuil minimal.",
                "Le système doit construire ProjectKnowledge une seule fois "
                "par cycle documentaire.",
                "Le système doit sélectionner les documents selon la "
                "politique du profil.",
                "Le système doit privilégier les générateurs "
                "déterministes.",
                "Le système doit écrire les documents dans "
                ".project-assistant/preview.",
                "Le système doit exiger une action apply explicite.",
                "Le système doit préserver les sections locales balisées.",
                "Le système doit refuser l’application d’un document "
                "protégé sans autorisation explicite.",
                "Le système doit pouvoir enregistrer et auditer plusieurs "
                "projets.",
                "Le système doit produire des rapports de conformité.",
            ],
            non_functional_requirements=[
                "Les sorties déterministes doivent être reproductibles.",
                "Les collections produites doivent avoir un ordre stable.",
                "Les erreurs doivent être explicites et ne doivent pas être "
                "masquées.",
                "Les analyseurs doivent gérer les fichiers absents ou "
                "invalides.",
                "L’ajout d’un profil ne doit pas modifier le comportement "
                "des profils existants.",
                "Les générateurs ne doivent pas rescanner le dépôt.",
                "La logique métier doit rester hors de cli.py lorsque "
                "possible.",
                "Le schéma de ProjectKnowledge doit être versionné.",
                "Toute fonctionnalité doit être couverte par des tests.",
            ],
            security_requirements=[
                "Le contenu de .env.local ne doit jamais être lu ou "
                "reproduit.",
                "Aucun secret ne doit apparaître dans un document, rapport "
                "ou journal.",
                "Les aperçus ne doivent jamais être appliqués "
                "automatiquement.",
                "INVARIANTS.md doit rester protégé par owner-approved.",
                "Les empreintes approuvées doivent détecter les "
                "modifications non autorisées.",
                "Les chemins absolus propres à une machine ne doivent pas "
                "être générés.",
                "Les caches et aperçus ne doivent pas être suivis par Git.",
            ],
            acceptance_criteria=[
                "docforge --help s’exécute sans erreur.",
                "docforge profile détecte python-cli pour ce dépôt.",
                "docforge knowledge produit un cache JSON valide.",
                "docforge document --refresh --clean ne modifie "
                "aucun document cible.",
                "Les documents générés correspondent à la politique du "
                "profil.",
                "Une tentative d’application de INVARIANTS.md sans "
                "owner-approved échoue.",
                "pytest -q réussit entièrement.",
                "Aucun secret ou chemin absolu propre à une machine "
                "n’apparaît dans les documents générés.",
            ],
            known_limitations=[
                "Les profils hugo-static et 3d-design ne sont pas encore "
                "implémentés.",
                "docs/cli.md, docs/configuration.md et docs/security.md ne "
                "possèdent pas encore leurs générateurs.",
                "La compatibilité des anciens caches ProjectKnowledge doit "
                "encore être formalisée.",
                "cli.py contient encore une partie importante de "
                "l’orchestration.",
                "Certaines détections de technologies restent génériques.",
            ],
        )
