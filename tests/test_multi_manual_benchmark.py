import json
from pathlib import Path

from docforge.multi_manual_benchmark import MultiManualBenchmarkRunner, parse_args, verify_reference


def make_reference(root: Path) -> Path:
    root.mkdir()
    (root / "manual-knowledge.json").write_text(json.dumps({"application": {"name": "Demo"}, "profile": {"name": "django-react"}}))
    docs=[]
    for ident, title in (("user-guide", "Guide utilisateur"), ("operator-guide", "Guide d’exploitation"), ("developer-reference", "Référence développeur")):
        base=root/"documents"/ident; (base/"section-prompts").mkdir(parents=True); (base/"section-contexts").mkdir(); (base/"deterministic-sections").mkdir()
        prompt=f"documents/{ident}/section-prompts/01-{ident}.md"; context=f"documents/{ident}/section-contexts/01-{ident}.json"; deterministic=f"documents/{ident}/deterministic-sections/01-{ident}.md"
        (root/prompt).write_text("prompt"); (root/context).write_text(json.dumps({"facts": {}})); (root/deterministic).write_text("déterministe")
        docs.append({"identifier":ident,"title":title,"section_contexts":[{"identifier":ident,"title":"Présentation","prompt_file":prompt,"context_file":context,"deterministic_file":deterministic,"generation_mode":"deterministic"}]})
    manifest={"profile_name":"django-react","project_kind":"application","knowledge_file":"manual-knowledge.json","expected_outputs":["manual-knowledge.json", *[x for d in docs for x in [d['section_contexts'][0]['prompt_file'],d['section_contexts'][0]['context_file'],d['section_contexts'][0]['deterministic_file']]],"generated/"],"documents":docs,"full_prompts_supported":False}
    (root/"generated").mkdir(); (root/"manual-manifest.json").write_text(json.dumps(manifest))
    import hashlib
    files=[p for p in root.rglob("*") if p.is_file() and p.name!="checksums.sha256"]
    (root/"checksums.sha256").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root).as_posix()}\n" for p in files))
    return root


def test_multidocument_reference_and_single_document_dry_run(tmp_path: Path):
    root=make_reference(tmp_path/"vtest")
    assert len(verify_reference(root)["documents"]) == 3
    args=parse_args(["--reference-dir",str(root),"--model","fake","--run-id","one","--document-id","user-guide","--num-ctx","12288","--dry-run"])
    assert MultiManualBenchmarkRunner().run(args) == 0
    run=root.parent/"runs"/"vtest"/"fake"/"one"
    state=json.loads((run/"run-manifest.json").read_text())
    assert state["multidocument_validation"]["deferred"] is True
    assert (run/"documents/user-guide/sections/user-guide.md").is_file()


def test_multidocument_runner_refuses_full_prompt(tmp_path: Path):
    root=make_reference(tmp_path/"vtest")
    args=parse_args(["--reference-dir",str(root),"--model","fake","--run-id","bad","--document-id","user-guide","--num-ctx","12288","--dry-run","--use-full-prompts"])
    import pytest
    with pytest.raises(ValueError, match="prompts complets"):
        MultiManualBenchmarkRunner().run(args)


def test_runner_uses_fake_client_and_rejects_empty_or_truncated(tmp_path: Path):
    root=make_reference(tmp_path/"vtest")
    manifest=json.loads((root/"manual-manifest.json").read_text())
    entry=manifest["documents"][0]["section_contexts"][0]
    entry["generation_mode"]="hybrid"
    (root/"manual-manifest.json").write_text(json.dumps(manifest))
    import hashlib
    files=[p for p in root.rglob("*") if p.is_file() and p.name!="checksums.sha256"]
    (root/"checksums.sha256").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root).as_posix()}\n" for p in files))
    calls=[]
    def client(*args):
        calls.append(args); return {"response":"Narration réelle.","thinking":"raisonnement interne", "done_reason":"stop","eval_count":12,"prompt_eval_count":8,"model":"fake"}
    args=parse_args(["--reference-dir",str(root),"--model","fake","--run-id","ok","--document-id","user-guide","--num-ctx","12288"])
    assert MultiManualBenchmarkRunner(client=client).run(args)==1
    run=root.parent/"runs"/"vtest"/"fake"/"ok"
    state=json.loads((run/"run-manifest.json").read_text())
    section=state["documents"]["user-guide"]["sections"]["user-guide"]
    assert calls and section["ollama_called"] and section["eval_count"]==12 and state["generation_state"]=="completed" and state["final_state"]=="validation_failed"
    assert "Narration réelle" in (run/"documents/user-guide/sections/user-guide.md").read_text()
    assert "raisonnement interne" not in (run/"documents/user-guide/sections/user-guide.md").read_text()
    assert section["thinking_present"] is True and section["final_response_retained"] == "response"
    def empty(*args): return {"response":"   ","done_reason":"stop"}
    args.run_id="empty"
    assert MultiManualBenchmarkRunner(client=empty).run(args)==1
    failed=json.loads((root.parent/"runs"/"vtest"/"fake"/"empty"/"run-manifest.json").read_text())
    assert failed["final_state"]=="failed"
    def length(*args): return {"response":"texte", "done_reason":"length"}
    args.run_id="length"
    assert MultiManualBenchmarkRunner(client=length).run(args)==1


def test_request_uses_historical_client_with_think_false(monkeypatch):
    import docforge.multi_manual_benchmark as module
    captured={}
    class FakeClient:
        def __init__(self, **kwargs): captured.update(kwargs); self.last_think_requested=True; self.last_think_compatibility_fallback=True
        def generate(self, **kwargs): captured["generate"]=kwargs; return {"response":"final", "thinking":"internal", "done_reason":"stop"}
    monkeypatch.setattr(module, "OllamaClient", FakeClient)
    response=module._request_ollama("http://fake", "prompt", "qwen", 12288, 12, 0, None)
    assert captured["generate"]["prompt"] == "prompt"
    assert response["_think_requested"] is True
    assert response["_think_compatibility_fallback"] is True
    assert response["response"] == "final"

def test_response_with_only_thinking_fails(tmp_path: Path):
    root=make_reference(tmp_path/"vtest")
    manifest=json.loads((root/"manual-manifest.json").read_text()); manifest["documents"][0]["section_contexts"][0]["generation_mode"]="hybrid"; (root/"manual-manifest.json").write_text(json.dumps(manifest))
    import hashlib
    files=[p for p in root.rglob("*") if p.is_file() and p.name!="checksums.sha256"]; (root/"checksums.sha256").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root).as_posix()}\n" for p in files))
    args=parse_args(["--reference-dir",str(root),"--model","fake","--run-id","thinking-only","--document-id","user-guide","--num-ctx","12288"])
    assert MultiManualBenchmarkRunner(client=lambda *args: {"response":"", "thinking":"ne pas publier", "done_reason":"stop"}).run(args)==1


def test_section_heading_normalization_ignores_code_fences() -> None:
    from docforge.multi_manual_benchmark import normalize_section_headings

    rendered = normalize_section_headings("# Présentation\n## Détail\n```bash\n# Présentation\n```\n### Valide", "Présentation")
    assert "# Présentation" not in rendered.splitlines()[:1]
    assert "### Détail" in rendered
    assert "# Présentation" in rendered.split("```bash")[1]


def test_historic_contact_guide_is_invalid() -> None:
    from docforge.validators import ContactUserGuideValidator, ManualMarkdownValidator
    from docforge.manual_blueprint import ManualBlueprintRegistry
    root = Path("benchmarks/manuals/contact/v0.1")
    markdown = "# Guide utilisateur de contact\n\n## Présentation\n# Présentation\nL’authentification n’est pas requise et le coffre local est inconnu.\n"
    knowledge = json.loads((root / "manual-knowledge.json").read_text(encoding="utf-8"))
    blueprint = ManualBlueprintRegistry().blueprint_for_document("django-react", project_kind="application", document_identifier="user-guide")
    diagnostics = ManualMarkdownValidator().validate(markdown=markdown, knowledge=knowledge, blueprint=blueprint)
    diagnostics += ContactUserGuideValidator().validate(markdown, knowledge)
    assert len(diagnostics) >= 6
    assert any(item.code == "MANUAL021" for item in diagnostics)
    assert any(item.code == "CONTACT004" for item in diagnostics)


def test_contact_user_validator_rejects_terminology_and_crypto_overpromises() -> None:
    from docforge.validators import ContactUserGuideValidator
    knowledge = json.loads(Path("benchmarks/manuals/contact/v0.2/manual-knowledge.json").read_text(encoding="utf-8"))
    markdown = "# Guide utilisateur de contact\n\n## Présentation\nLe backend Django garantit la confidentialité ; le serveur ne peut pas accéder aux données.\n"
    codes = {item.code for item in ContactUserGuideValidator().validate(markdown, knowledge)}
    assert {"CONTACT001", "CONTACT002"} <= codes


def test_contact_v02_user_deterministic_facts_and_limitations() -> None:
    root = Path("benchmarks/manuals/contact/v0.2/documents/user-guide/deterministic-sections")
    assert "https://con.mon-site.ca" in (root / "03-user-access.md").read_text(encoding="utf-8")
    assert "connexion est requise" in (root / "04-user-authentication.md").read_text(encoding="utf-8")
    limitations = (root / "10-user-limitations.md").read_text(encoding="utf-8")
    assert "récupération du coffre" in limitations
    assert "URL" not in limitations


def test_smoke_user_003_validation_is_a_failure() -> None:
    from docforge.validators import ContactUserGuideValidator, ManualMarkdownValidator
    from docforge.manual_blueprint import ManualBlueprintRegistry
    root = Path("benchmarks/manuals/contact/v0.2")
    guide = "# Guide utilisateur de contact\n\n## Présentation\ncontact est une application django-react.\n\n## Utilisation de l’application\n### Recherche et révéléation de données\n"
    knowledge = json.loads((root / "manual-knowledge.json").read_text(encoding="utf-8"))
    blueprint = ManualBlueprintRegistry().blueprint_for_document("django-react", project_kind="application", document_identifier="user-guide")
    diagnostics = ManualMarkdownValidator().validate(markdown=guide, knowledge=knowledge, blueprint=blueprint)
    diagnostics += ContactUserGuideValidator().validate(guide, knowledge)
    assert sum(item.severity == "error" for item in diagnostics) >= 2
    assert any(item.code == "MANUAL008" for item in diagnostics) is False


def test_url_validation_allows_sentence_punctuation_and_rejects_unknown() -> None:
    from docforge.validators import ManualMarkdownValidator
    from docforge.manual_blueprint import ManualBlueprintRegistry
    knowledge = json.loads(Path("benchmarks/manuals/contact/v0.3/manual-knowledge.json").read_text(encoding="utf-8"))
    blueprint = ManualBlueprintRegistry().blueprint_for_document("django-react", project_kind="application", document_identifier="user-guide")
    valid = ManualMarkdownValidator().validate(markdown="# Guide utilisateur de contact\n\n## Présentation\nhttps://con.mon-site.ca.\n", knowledge=knowledge, blueprint=blueprint)
    assert not any(item.code == "MANUAL008" for item in valid)
    invalid = ManualMarkdownValidator().validate(markdown="# Guide utilisateur de contact\n\n## Présentation\nhttps://inconnue.example.\n", knowledge=knowledge, blueprint=blueprint)
    assert any(item.code == "MANUAL008" for item in invalid)


def test_contact_v03_user_guide_is_all_deterministic_and_valid() -> None:
    from docforge.validators import ContactUserGuideValidator
    root = Path("benchmarks/manuals/contact/v0.3")
    manifest = json.loads((root / "manual-manifest.json").read_text(encoding="utf-8"))
    user = next(item for item in manifest["documents"] if item["identifier"] == "user-guide")
    assert len(user["section_contexts"]) == 10
    assert {item["generation_mode"] for item in user["section_contexts"]} == {"deterministic"}
    fragments = [root / entry["deterministic_file"] for entry in user["section_contexts"]]
    assert all(fragment.is_file() and fragment.read_text(encoding="utf-8").strip() for fragment in fragments)


def test_expected_h1_is_document_specific() -> None:
    from docforge.validators import ManualMarkdownValidator
    from docforge.manual_blueprint import ManualBlueprintRegistry
    knowledge = {"application": {"name": "contact"}}
    registry = ManualBlueprintRegistry()
    validator = ManualMarkdownValidator()
    assert validator.expected_h1(knowledge, registry.blueprint_for_document("django-react", project_kind="application", document_identifier="user-guide")) == "# Guide utilisateur de contact"
    assert validator.expected_h1(knowledge, registry.blueprint_for_document("django-react", project_kind="application", document_identifier="operator-guide")) == "# Guide d’exploitation de contact"
    assert validator.expected_h1(knowledge, registry.blueprint_for_document("django-react", project_kind="application", document_identifier="developer-reference")) == "# Référence développeur de contact"


def test_operator_h1_mismatch_is_reported() -> None:
    from docforge.validators import ManualMarkdownValidator
    from docforge.manual_blueprint import ManualBlueprintRegistry
    blueprint = ManualBlueprintRegistry().blueprint_for_document("django-react", project_kind="application", document_identifier="operator-guide")
    diagnostics = ManualMarkdownValidator().validate(markdown="# Guide utilisateur de contact\n", knowledge={"application": {"name": "contact"}}, blueprint=blueprint)
    assert any(item.code == "MANUAL012" for item in diagnostics)
