from docforge.manual_blueprint import ManualBlueprint, ManualSectionDefinition
from docforge.validators.manual_markdown import ManualMarkdownValidator


SECTION_TITLES = [
    "Présentation",
    "Public visé",
    "Prérequis",
    "Installation",
    "Démarrage rapide",
    "Concepts essentiels",
    "Analyse d’un projet",
    "Détection du profil",
    "Construction de ProjectKnowledge",
    "Génération documentaire",
    "Génération avec Ollama",
    "Révision des aperçus",
    "Application des documents",
    "Documents protégés",
    "Gestion des projets",
    "Audits et conformité",
    "Configuration",
    "Sécurité",
    "Dépannage",
    "Limites des informations disponibles",
    "Référence CLI",
]


def _blueprint() -> ManualBlueprint:
    return ManualBlueprint(
        profile_name="python-cli",
        sections=tuple(
            ManualSectionDefinition(
                identifier=f"section-{index}",
                title=title,
                purpose="Test.",
                required_fact_paths=(),
            )
            for index, title in enumerate(SECTION_TITLES, start=1)
        ),
    )


def _knowledge() -> dict:
    return {"project": {"name": "docforge"}, "commands": []}


def _markdown_with_sections(*, duplicate: str | None = None, swap: tuple[str, str] | None = None, omit: str | None = None, extra_h2: str | None = None, canonical_h3_only: str | None = None, code_block_title: str | None = None) -> str:
    titles = [title for title in SECTION_TITLES if title != omit]
    if swap is not None:
        first, second = swap
        i = titles.index(first)
        j = titles.index(second)
        titles[i], titles[j] = titles[j], titles[i]
    lines = ["# Guide utilisateur de docforge", ""]
    for title in titles:
        lines.append(f"## {title}")
        lines.append(f"Contenu pour {title}.")
        lines.append("")
        if title == "Présentation":
            lines.append("### Configuration")
            lines.append("Sous-section homonyme autorisée.")
            lines.append("")
        if title == "Installation":
            lines.append("### Démarrage rapide")
            lines.append("Sous-section homonyme autorisée.")
            lines.append("")
        if title == "Révision des aperçus":
            lines.append("### Documents protégés")
            lines.append("Sous-section homonyme autorisée.")
            lines.append("")
    if duplicate is not None:
        lines.extend([f"## {duplicate}", "Section dupliquée.", ""])
    if extra_h2 is not None:
        lines.extend([f"## {extra_h2}", "Section supplémentaire.", ""])
    if canonical_h3_only is not None and omit == canonical_h3_only:
        lines.extend([f"### {canonical_h3_only}", "Titre canonique relégué en H3.", ""])
    if code_block_title is not None:
        lines.extend(["```markdown", f"## {code_block_title}", "```", ""])
    return "\n".join(lines).rstrip() + "\n"


def test_manual_markdown_accepts_h2_order_with_h3_homonyms_elsewhere() -> None:
    validator = ManualMarkdownValidator()
    diagnostics = validator.validate(
        markdown=_markdown_with_sections(),
        knowledge=_knowledge(),
        blueprint=_blueprint(),
    )

    assert not any(item.code in {"MANUAL003", "MANUAL004", "MANUAL016", "MANUAL017"} for item in diagnostics)


def test_manual_markdown_detects_true_h2_order_error() -> None:
    validator = ManualMarkdownValidator()
    diagnostics = validator.validate(
        markdown=_markdown_with_sections(swap=("Installation", "Prérequis")),
        knowledge=_knowledge(),
        blueprint=_blueprint(),
    )

    assert any(item.code == "MANUAL004" for item in diagnostics)


def test_manual_markdown_detects_missing_h2() -> None:
    validator = ManualMarkdownValidator()
    diagnostics = validator.validate(
        markdown=_markdown_with_sections(omit="Configuration"),
        knowledge=_knowledge(),
        blueprint=_blueprint(),
    )

    assert any(item.code == "MANUAL003" and item.section == "section-17" for item in diagnostics)


def test_manual_markdown_detects_duplicate_h2() -> None:
    validator = ManualMarkdownValidator()
    diagnostics = validator.validate(
        markdown=_markdown_with_sections(duplicate="Configuration"),
        knowledge=_knowledge(),
        blueprint=_blueprint(),
    )

    assert any(item.code == "MANUAL016" and item.fact == "Configuration" for item in diagnostics)


def test_manual_markdown_detects_canonical_title_present_only_as_h3() -> None:
    validator = ManualMarkdownValidator()
    diagnostics = validator.validate(
        markdown=_markdown_with_sections(omit="Configuration", canonical_h3_only="Configuration"),
        knowledge=_knowledge(),
        blueprint=_blueprint(),
    )

    issue = next(item for item in diagnostics if item.code == "MANUAL003" and item.section == "section-17")
    assert "H3" in issue.message


def test_manual_markdown_detects_extra_h2_when_policy_forbids_it() -> None:
    validator = ManualMarkdownValidator()
    diagnostics = validator.validate(
        markdown=_markdown_with_sections(extra_h2="Annexe libre"),
        knowledge=_knowledge(),
        blueprint=_blueprint(),
    )

    assert any(item.code == "MANUAL017" and item.fact == "Annexe libre" for item in diagnostics)



def test_manual_markdown_ignores_titles_inside_code_fences() -> None:
    validator = ManualMarkdownValidator()
    diagnostics = validator.validate(
        markdown=_markdown_with_sections(omit="Configuration", code_block_title="Configuration"),
        knowledge=_knowledge(),
        blueprint=_blueprint(),
    )

    assert any(item.code == "MANUAL003" and item.section == "section-17" for item in diagnostics)

    assert not any(item.code == "MANUAL016" and item.fact == "Configuration" for item in diagnostics)



def _safety_knowledge(*, profile: str = "python-cli", files: list[str] | None = None, controls: list[dict] | None = None) -> dict:
    return {
        "project": {"name": "docforge", "profile_type": profile},
        "commands": [{"command_path": "docforge apply", "parameters": []}],
        "configuration": {"files": [{"path": item} for item in files or []]},
        "security": {"controls": controls or []},
    }


def _safety_diagnostics(markdown: str, **kwargs):
    return ManualMarkdownValidator().validate(
        markdown=markdown,
        knowledge=_safety_knowledge(**kwargs),
        blueprint=_blueprint(),
    )


def test_manual_markdown_ignores_python_entry_point_mapping() -> None:
    diagnostics = _safety_diagnostics("# Guide utilisateur de docforge\n\n`docforge -> docforge.cli:app`")
    assert not any(item.code == "MANUAL006" for item in diagnostics)


def test_manual_markdown_keeps_env_local_profile_scoped() -> None:
    python_cli = _safety_diagnostics("# Guide utilisateur de docforge\n\n`.env.local`", profile="python-cli")
    django_react = _safety_diagnostics(
        "# Guide utilisateur de docforge\n\n`.env.local`",
        profile="django-react",
        files=[".env.local"],
    )
    assert any(item.code == "MANUAL019" and item.fact == ".env.local" for item in python_cli)
    assert not any(item.code == "MANUAL019" and item.fact == ".env.local" for item in django_react)


def test_manual_markdown_secret_rule_does_not_authorize_env_local() -> None:
    diagnostics = _safety_diagnostics(
        "# Guide utilisateur de docforge\n\n`.env.local`",
        controls=[{"description": "Ne jamais exposer les secrets."}],
    )
    assert any(item.code == "MANUAL019" and item.fact == ".env.local" for item in diagnostics)


def test_manual_markdown_rejects_positive_automation_claim() -> None:
    diagnostics = _safety_diagnostics("# Guide utilisateur de docforge\n\nLe guide génère automatiquement les fichiers.")
    assert any(item.code == "MANUAL020" for item in diagnostics)


def test_manual_markdown_accepts_demonstrated_negative_automation_claim() -> None:
    diagnostics = _safety_diagnostics(
        "# Guide utilisateur de docforge\n\nLe document n’est jamais appliqué automatiquement.",
        controls=[{"description": "L’application exige une commande explicite docforge apply."}],
    )
    assert not any(item.code == "MANUAL020" for item in diagnostics)


def test_manual_markdown_rejects_undemonstrated_negative_automation_claim() -> None:
    diagnostics = _safety_diagnostics("# Guide utilisateur de docforge\n\nLe document n’est jamais appliqué automatiquement.")
    assert any(item.code == "MANUAL020" for item in diagnostics)


def test_manual_markdown_accepts_meta_documentary_automation_wording() -> None:
    diagnostics = _safety_diagnostics(
        "# Guide utilisateur de docforge\n\nCette règle ne représente pas un comportement observé automatiquement."
    )
    assert not any(item.code == "MANUAL020" for item in diagnostics)


def test_manual_markdown_accepts_documented_deterministic_and_optional_policies() -> None:
    knowledge = _safety_knowledge()
    knowledge["documentation_policy"] = {
        "deterministic_documents": ["README.md"],
        "optional_documents": ["docs/roadmap.md"],
    }
    diagnostics = ManualMarkdownValidator().validate(
        markdown=("# Guide utilisateur de docforge\n\n"
                  "Les documents déterministes sont générés automatiquement.\n"
                  "Les documents optionnels ne sont pas régénérés automatiquement."),
        knowledge=knowledge,
        blueprint=_blueprint(),
    )
    assert not any(item.code == "MANUAL020" for item in diagnostics)


def test_manual_markdown_deduplicates_multiple_automation_words_on_one_line() -> None:
    diagnostics = _safety_diagnostics("# Guide utilisateur de docforge\n\nLe rapport est généré automatiquement sans intervention.")
    assert len([item for item in diagnostics if item.code == "MANUAL020"]) == 1


def test_manual_markdown_accepts_detected_profile_automation() -> None:
    knowledge = _safety_knowledge()
    knowledge["profile"] = {"source": {"status": "detected", "sources": ["ProfileDetector"]}}
    diagnostics = ManualMarkdownValidator().validate(
        markdown="# Guide utilisateur de docforge\n\nLe système détermine automatiquement le profil du dépôt.",
        knowledge=knowledge,
        blueprint=_blueprint(),
    )
    assert not any(item.code == "MANUAL020" for item in diagnostics)


def test_manual_markdown_accepts_configured_meta_documentary_statement() -> None:
    diagnostics = _safety_diagnostics(
        "# Guide utilisateur de docforge\n\nCes contraintes ne doivent pas être interprétées comme des comportements observés sans intervention explicite."
    )
    assert not any(item.code == "MANUAL020" for item in diagnostics)


def test_manual_markdown_accepts_application_negation_variants_only_with_apply_evidence() -> None:
    controls = [{"description": "L’application exige une commande explicite docforge apply."}]
    for sentence in (
        "Aucune modification n’est appliquée automatiquement.",
        "Les aperçus ne s’appliquent pas automatiquement.",
    ):
        diagnostics = _safety_diagnostics(f"# Guide utilisateur de docforge\n\n{sentence}", controls=controls)
        assert not any(item.code == "MANUAL020" for item in diagnostics)


def test_manual_markdown_accepts_singular_meta_documentary_negation() -> None:
    diagnostics = _safety_diagnostics(
        "# Guide utilisateur de docforge\n\nCes règles ne doivent pas être interprétées comme un comportement automatique."
    )
    assert not any(item.code == "MANUAL020" for item in diagnostics)


def test_manual_markdown_accepts_ne_se_produit_jamais_with_sec003() -> None:
    diagnostics = _safety_diagnostics(
        "# Guide utilisateur de docforge\n\nL’application ne se produit jamais automatiquement.",
        controls=[{"description": "L’application exige une commande explicite docforge apply."}],
    )
    assert not any(item.code == "MANUAL020" for item in diagnostics)


def test_manual_markdown_rejects_ne_se_produit_jamais_without_sec003() -> None:
    diagnostics = _safety_diagnostics(
        "# Guide utilisateur de docforge\n\nL’application ne se produit jamais automatiquement."
    )
    assert any(item.code == "MANUAL020" for item in diagnostics)


def test_manual_markdown_keeps_positive_apply_automation_rejected() -> None:
    diagnostics = _safety_diagnostics(
        "# Guide utilisateur de docforge\n\nL’outil applique automatiquement le document.",
        controls=[{"description": "L’application exige une commande explicite docforge apply."}],
    )
    assert any(item.code == "MANUAL020" for item in diagnostics)


def test_manual_markdown_forbidden_vocabulary_has_line_and_section() -> None:
    diagnostics = ManualMarkdownValidator().validate(
        markdown=_markdown_with_sections().replace("Contenu pour Génération documentaire.", "Le pipeline documentaire est interne."),
        knowledge=_knowledge(),
        blueprint=_blueprint(),
    )
    diagnostic = next(item for item in diagnostics if item.code == "MANUAL005")
    assert diagnostic.fact == "pipeline documentaire"
    assert diagnostic.section == "Génération documentaire"
    assert diagnostic.line is not None
