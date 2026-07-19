from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import time
from datetime import UTC, datetime
from dataclasses import asdict
from pathlib import Path
from urllib import request

from docforge.manual_benchmark import OllamaClient, model_slug
from docforge.validators import ContactUserGuideValidator, DjangoReactMultiDocumentValidator, ManualMarkdownValidator
from docforge.manual_blueprint import ManualBlueprintRegistry


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def verify_reference(root: Path) -> dict:
    checksums = {}
    for line in (root / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        digest, relative = line.split(None, 1)
        checksums[relative.strip()] = digest
    for relative, digest in checksums.items():
        path = root / relative
        if not path.is_file() or sha256(path) != digest:
            raise ValueError(f"Empreinte invalide : {relative}")
    manifest_file = root / "reference-manifest.json"
    if not manifest_file.is_file():
        manifest_file = root / "manual-manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    for relative in manifest["expected_outputs"]:
        if not relative.endswith("/") and not (root / relative).is_file():
            raise ValueError(f"Intrant attendu absent : {relative}")
    return manifest


def _request_ollama(url: str, prompt: str, model: str, num_ctx: int, max_output_tokens: int, temperature: float, seed: int | None) -> dict:
    client = OllamaClient(base_url=url, timeout_seconds=3600)
    response = client.generate(model=model, prompt=prompt, num_ctx=num_ctx, temperature=temperature, seed=seed, max_output_tokens=max_output_tokens)
    response = dict(response)
    response["_think_requested"] = client.last_think_requested
    response["_think_compatibility_fallback"] = client.last_think_compatibility_fallback
    return response


def _substantive(text: str) -> bool:
    return bool(text.strip()) and text.strip().casefold() not in {"à compléter", "todo", "tbd"}

def normalize_section_headings(markdown: str, canonical_title: str) -> str:
    """Keep canonical H2 ownership in the assembler, outside fenced code."""
    lines: list[str] = []
    in_fence = False
    canonical = canonical_title.casefold().replace("’", "'")
    for line in markdown.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            lines.append(line)
            continue
        if not in_fence:
            match = re.match(r"^(#{1,2})\s+(.+?)\s*$", stripped)
            if match:
                title = match.group(2).casefold().replace("’", "'")
                if title == canonical:
                    continue
                lines.append("### " + match.group(2))
                continue
        lines.append(line)
    return "\n".join(lines).strip()


def _h1(title: str, knowledge: dict) -> str:
    name = knowledge.get("application", {}).get("display_name") or knowledge.get("application", {}).get("name") or knowledge.get("project", {}).get("name") or "l’application"
    if title == "Guide utilisateur": return f"# Guide utilisateur de {name}"
    return f"# {title} de {name}"


class MultiManualBenchmarkRunner:
    def __init__(self, client=None) -> None:
        self.client = client or _request_ollama

    def _summary(self, state: dict, selected: set[str]) -> str:
        sections=[s for d in state["documents"].values() for s in d["sections"].values()]
        modes={mode:sum(s.get("generation_mode")==mode for s in sections) for mode in ("narrative","hybrid","deterministic")}
        completed=sum(s.get("status")=="completed" for s in sections); failed=sum(s.get("status")=="failed" for s in sections)
        calls=sum(s.get("ollama_called",False) for s in sections); duration=sum(s.get("duration_seconds") or 0 for s in sections)
        validation = state.get("validation_summary", {})
        condensed = validation.get("condensed", [])
        return "\n".join(["# Résumé benchmark", "", f"État global : {state['final_state']}", f"État de génération : {state.get('generation_state', 'inconnu')}", f"Documents sélectionnés : {', '.join(sorted(selected))}", f"Sections : réussies={completed}, échouées={failed}; narratives={modes['narrative']}, hybrides={modes['hybrid']}, déterministes={modes['deterministic']}.", f"Appels Ollama : {calls}. Durée : {duration:.3f} s.", f"Validation : erreurs={validation.get('errors', 0)}, avertissements={validation.get('warnings', 0)}.", *( ["Diagnostics :", *[f"- {item}" for item in condensed]] if condensed else [] ), f"Validation multidocument : {'différée' if state['multidocument_validation'].get('deferred') else 'exécutée'}.", ""])

    def run(self, args: argparse.Namespace) -> int:
        root=Path(args.reference_dir).resolve(); manifest=verify_reference(root); documents=manifest["documents"]
        selected=set(args.document_id or [])
        if args.all_documents: selected={d["identifier"] for d in documents}
        if not selected: raise ValueError("Sélectionnez --document-id ou --all-documents.")
        available={d["identifier"] for d in documents}
        if not selected <= available: raise ValueError("document-id inconnu")
        if not manifest.get("full_prompts_supported",True) and args.use_full_prompts: raise ValueError("Les prompts complets sont refusés par cette référence.")
        run_dir=root.parent/"runs"/root.name/model_slug(args.model)/args.run_id
        if run_dir.exists() and not args.resume and not args.reassemble: raise ValueError("run-id existant : utilisez --resume ou un nouveau run-id")
        run_dir.mkdir(parents=True,exist_ok=True); state_path=run_dir/"run-manifest.json"
        state=json.loads(state_path.read_text()) if args.resume and state_path.exists() else {"schema_version":3,"created_at":now(),"reference_dir":str(root),"model":args.model,"dry_run":bool(args.dry_run),"selected_documents":sorted(selected),"documents":{},"generation_state":"running","final_state":"running"}
        knowledge=json.loads((root/manifest["knowledge_file"]).read_text())
        try:
            for document in documents:
                ident=document["identifier"]
                if ident not in selected: continue
                destination=run_dir/"documents"/ident; destination.mkdir(parents=True,exist_ok=True)
                dstate=state["documents"].setdefault(ident,{"title":document["title"],"sections":{}})
                for entry in document["section_contexts"]:
                    sid=entry["identifier"]; out=destination/"sections"/f"{sid}.md"; previous=dstate["sections"].get(sid,{})
                    if args.resume and previous.get("status")=="completed" and out.is_file(): continue
                    declared=entry.get("generation_mode","hybrid"); mode="deterministic" if declared=="deterministic" else ("hybrid" if entry.get("deterministic_file") else "narrative")
                    fragment=(root/entry["deterministic_file"]).read_text(encoding="utf-8") if entry.get("deterministic_file") else ""
                    record={"status":"running","generation_mode":mode,"ollama_called":False,"started_at":now(),"prompt_file":entry["prompt_file"]}; dstate["sections"][sid]=record
                    started=time.monotonic()
                    if mode=="deterministic": content=fragment
                    elif args.dry_run: content=""; record["status"]="dry_run"
                    else:
                        raw=self.client(args.ollama_url,(root/entry["prompt_file"]).read_text(),args.model,args.num_ctx,args.max_output_tokens,args.temperature,args.seed)
                        record["ollama_called"]=True; record["response_file"]=f"documents/{ident}/responses/{sid}.json"
                        raw_path=run_dir/record["response_file"]; raw_path.parent.mkdir(parents=True,exist_ok=True); raw_path.write_text(json.dumps(raw,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
                        narrative=str(raw.get("response") or "")
                        for key in ("model","prompt_eval_count","eval_count","done_reason","total_duration","load_duration","prompt_eval_duration","eval_duration"): record[key]=raw.get(key)
                        record["think_requested"] = bool(raw.get("_think_requested", True))
                        record["thinking_present"] = isinstance(raw.get("thinking"), str) and bool(raw.get("thinking").strip())
                        record["think_compatibility_fallback"] = bool(raw.get("_think_compatibility_fallback", False))
                        record["final_response_retained"] = "response"
                        if not _substantive(narrative): raise ValueError(f"Réponse Ollama vide : {ident}/{sid}")
                        if raw.get("done_reason")=="length": raise ValueError(f"Réponse Ollama tronquée : {ident}/{sid}")
                        record["narrative_file"]=f"documents/{ident}/responses/{sid}.md"; (run_dir/record["narrative_file"]).write_text(narrative,encoding="utf-8")
                        content=narrative + ("\n\n"+fragment if mode=="hybrid" and fragment else "")
                    if mode=="deterministic" and not _substantive(content): raise ValueError(f"Fragment déterministe vide : {ident}/{sid}")
                    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(content,encoding="utf-8")
                    record.update({"status":"completed" if not args.dry_run else "dry_run","duration_seconds":round(time.monotonic()-started,3),"completed_at":now(),"output":str(out.relative_to(run_dir)),"output_sha256":sha256(out)})
                if not args.dry_run:
                    parts=[_h1(document["title"],knowledge),""]; bad=[]
                    for entry in document["section_contexts"]:
                        body=(destination/"sections"/f"{entry['identifier']}.md").read_text(encoding="utf-8")
                        mode=dstate["sections"][entry["identifier"]]["generation_mode"]
                        if mode != "deterministic" and not _substantive(body): bad.append(entry["identifier"])
                        parts.extend([f"## {entry['title']}","",normalize_section_headings(body, entry["title"]),""])
                    if bad: raise ValueError("Narration obligatoire absente : "+", ".join(bad))
                    guide=destination/"guide-genere.md"; guide.write_text("\n".join(parts).rstrip()+"\n",encoding="utf-8")
                    blueprint=ManualBlueprintRegistry().blueprint_for_document(manifest["profile_name"],project_kind=manifest.get("project_kind"),document_identifier=ident)
                    rendered_guide = guide.read_text(encoding="utf-8")
                    diagnostics=ManualMarkdownValidator().validate(markdown=rendered_guide,knowledge=knowledge,blueprint=blueprint)
                    if ident == "user-guide" and manifest.get("profile_name") == "django-react":
                        diagnostics.extend(ContactUserGuideValidator().validate(rendered_guide, knowledge))
                    (run_dir/"validation").mkdir(exist_ok=True); (run_dir/"validation"/f"{ident}.json").write_text(json.dumps([asdict(x) for x in diagnostics],default=str,ensure_ascii=False,indent=2),encoding="utf-8")
                    errors = [item for item in diagnostics if item.severity == "error"]
                    warnings = [item for item in diagnostics if item.severity == "warning"]
                    dstate["validation"]={"diagnostics":len(diagnostics),"errors":len(errors),"warnings":len(warnings),"substantive":True}
            multidocument_diagnostics = []
            state["multidocument_validation"]={"deferred":selected != available, "executed":False, "diagnostics":0}
            if selected == available and manifest.get("profile_name") == "django-react":
                multidocument_diagnostics = [asdict(item) for item in DjangoReactMultiDocumentValidator().validate(root=root, manifest=manifest)]
                state["multidocument_validation"]={"deferred":False, "executed":True, "diagnostics":len(multidocument_diagnostics)}
                (run_dir/"validation").mkdir(exist_ok=True)
                (run_dir/"validation"/"multidocument.json").write_text(json.dumps(multidocument_diagnostics, ensure_ascii=False, indent=2), encoding="utf-8")
            state["generation_state"]="completed"
            selected_validations = [d.get("validation", {}) for d in state["documents"].values()]
            all_diagnostics = list(multidocument_diagnostics)
            for ident, dstate in state["documents"].items():
                validation_file = run_dir / "validation" / f"{ident}.json"
                if validation_file.is_file():
                    all_diagnostics.extend(json.loads(validation_file.read_text(encoding="utf-8")))
            errors = [item for item in all_diagnostics if item.get("severity") == "error"]
            warnings = [item for item in all_diagnostics if item.get("severity") == "warning"]
            state["validation_summary"]={"errors":len(errors),"warnings":len(warnings),"condensed":[f"{item.get('code')}: {item.get('message')}" for item in [*errors, *warnings][:12]]}
            state["final_state"]="dry_run_completed" if args.dry_run else ("validation_failed" if errors else "completed")
        except Exception as error:
            state["generation_state"]="failed"; state["final_state"]="failed"; state["error"]=str(error)
            for d in state["documents"].values():
                for s in d["sections"].values():
                    if s.get("status")=="running": s["status"]="failed"; s["error"]=str(error)
        state.setdefault("multidocument_validation", {"deferred": selected != available})
        state["updated_at"]=now(); state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        (run_dir/"timing.json").write_text(json.dumps(state["documents"],ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        (run_dir/"benchmark-summary.md").write_text(self._summary(state,selected),encoding="utf-8")
        return 0 if state["final_state"] in {"completed","dry_run_completed"} else 1


def parse_args(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--reference-dir",required=True); p.add_argument("--model",required=True); p.add_argument("--run-id",required=True)
    p.add_argument("--document-id",action="append"); p.add_argument("--all-documents",action="store_true")
    p.add_argument("--num-ctx",type=int,required=True); p.add_argument("--max-output-tokens",type=int,default=2048); p.add_argument("--temperature",type=float,default=0); p.add_argument("--seed",type=int)
    p.add_argument("--ollama-url",default="http://localhost:11434"); p.add_argument("--resume",action="store_true"); p.add_argument("--reassemble",action="store_true"); p.add_argument("--dry-run",action="store_true"); p.add_argument("--use-full-prompts",action="store_true")
    return p.parse_args(argv)

def main(argv=None):
    try: return MultiManualBenchmarkRunner().run(parse_args(argv))
    except Exception as error: print(f"Erreur : {error}"); return 1
