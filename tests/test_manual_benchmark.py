import io
import json
import socket
import subprocess
from pathlib import Path
from types import SimpleNamespace
from urllib.error import HTTPError, URLError

import pytest

from docforge.manual_benchmark import (
    BenchmarkConfig,
    BenchmarkError,
    ManualBenchmarkRunner,
    OllamaClient,
    ReferenceError,
    ResumeMismatchError,
    load_reference_bundle,
    parse_args,
    main,
    parse_command_coverage,
    unwrap_single_markdown_fence,
    verify_reference_checksums,
)


class FakeHTTPResponse:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def read(self) -> bytes:
        return self.payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class UrlopenSequence:
    def __init__(self, responses):
        self.responses = list(responses)
        self.generate_calls = 0

    def __call__(self, request, timeout=0):
        url = request.full_url
        if url.endswith('/api/version'):
            return FakeHTTPResponse(json.dumps({'version': '0.9.0'}).encode('utf-8'))
        if url.endswith('/api/tags'):
            return FakeHTTPResponse(json.dumps({'models': [{'name': 'qwen3.5:4b', 'digest': 'sha256:test'}]}).encode('utf-8'))
        if url.endswith('/api/generate'):
            self.generate_calls += 1
            payload = self.responses.pop(0)
            if isinstance(payload, Exception):
                raise payload
            if isinstance(payload, bytes):
                return FakeHTTPResponse(payload)
            return FakeHTTPResponse(json.dumps(payload).encode('utf-8'))
        raise AssertionError(f'URL inattendue: {url}')


class NoHTTPAllowed:
    def __call__(self, request, timeout=0):
        raise AssertionError('HTTP call unexpected during reassembly')


class ValidationRunner:
    def __init__(self, *, valid: bool, returncode: int) -> None:
        self.valid = valid
        self.returncode = returncode

    def __call__(self, command, cwd=None, capture_output=False, text=False):
        results_dir = Path(command[command.index('--results-dir') + 1])
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / 'manual-validate.json').write_text(
            json.dumps(
                {
                    'markdown_file': 'guide-genere.md',
                    'knowledge_file': 'manual-knowledge.json',
                    'errors': [] if self.valid else [{'code': 'MANUAL003'}],
                    'warnings': [],
                    'valid': self.valid,
                },
                indent=2,
                ensure_ascii=False,
            ) + '\n',
            encoding='utf-8',
        )
        coverage = (
            'Commandes détectées : 2\n'
            'Couverture command_path : 2/2\n'
            'Couverture invocation exécutable : 2/2\n'
            '\n'
            'Commandes totalement absentes : aucune\n'
            'Commandes présentes seulement par command_path : aucune\n'
            'Invocations complètes manquantes : aucune\n'
        )
        (results_dir / 'command-coverage.txt').write_text(coverage, encoding='utf-8')
        (results_dir / 'command-fidelity.json').write_text(
            json.dumps(
                {
                    'documented_command_count': 2,
                    'command_path_coverage': {'present': 2, 'total': 2, 'percent': 100.0},
                    'executable_invocation_coverage': {'present': 2, 'total': 2, 'percent': 100.0},
                    'strict_error_count': 0,
                    'warning_count': 0,
                    'unknown_command_mentions': [],
                    'unknown_options': [],
                    'totally_absent_commands': [],
                    'command_path_only_commands': [],
                    'missing_full_invocations': [],
                    'strict_errors': [],
                    'warnings': [],
                    'commands': [],
                },
                indent=2,
                ensure_ascii=False,
            ) + '\n',
            encoding='utf-8',
        )
        (results_dir / 'command-fidelity.md').write_text('# Validation de fidélité des commandes\n', encoding='utf-8')
        return subprocess.CompletedProcess(command, self.returncode, stdout='validator stdout\n', stderr='validator stderr\n')


def build_smoke_resume_manifest(run_dir: Path, manifest: dict, *, running_section_19: bool = True) -> None:
    sections_dir = run_dir / 'sections'
    sections_dir.mkdir(exist_ok=True)

    for index in range(18):
        section = manifest['sections'][index]
        stem = Path(section['prompt_file']).stem
        markdown_rel = f'sections/{stem}.md'
        response_rel = f'sections/{stem}.response.json'
        markdown_path = run_dir / markdown_rel
        response_path = run_dir / response_rel
        markdown_path.write_text(f"## {section['title']}\n\nTexte {index + 1}\n", encoding='utf-8')
        response_path.write_text(
            json.dumps({'response': f'Texte {index + 1}', 'done_reason': 'stop'}, ensure_ascii=False) + '\n',
            encoding='utf-8',
        )
        section.update(
            {
                'status': 'completed',
                'started_at': '2026-07-17T00:00:00+00:00',
                'completed_at': '2026-07-17T00:00:01+00:00',
                'duration_seconds': 1.0,
                'output_markdown_file': markdown_rel,
                'output_markdown_sha256': 'done-md',
                'response_file': response_rel,
                'response_sha256': 'done-json',
                'prompt_eval_count': 1000 + index,
                'eval_count': 100 + index,
                'total_duration': 1,
                'load_duration': 1,
                'prompt_eval_duration': 1,
                'eval_duration': 1,
                'done_reason': 'stop',
                'error': None,
                'effective_generation_parameters': {
                    'num_ctx': 8192,
                    'temperature': 0.0,
                    'seed': 42,
                    'max_output_tokens': 2048,
                    'timeout_seconds': 300,
                },
            }
        )

    section_19 = manifest['sections'][18]
    section_19_stem = Path(section_19['prompt_file']).stem
    response_rel = f'sections/{section_19_stem}.response.json'
    (run_dir / response_rel).write_text(
        json.dumps({'response': 'partiel', 'done_reason': 'length'}, ensure_ascii=False) + '\n',
        encoding='utf-8',
    )
    section_19.update(
        {
            'status': 'running' if running_section_19 else 'failed',
            'started_at': '2026-07-17T00:00:00+00:00',
            'completed_at': None if running_section_19 else '2026-07-17T00:01:00+00:00',
            'duration_seconds': None if running_section_19 else 60.0,
            'output_markdown_file': None,
            'output_markdown_sha256': None,
            'response_file': response_rel,
            'response_sha256': 'failed-json',
            'prompt_eval_count': 4673,
            'eval_count': 2048,
            'total_duration': 2,
            'load_duration': 1,
            'prompt_eval_duration': 1,
            'eval_duration': 1,
            'done_reason': 'length',
            'error_type': 'generation',
            'error': 'ancienne interruption',
            'effective_generation_parameters': {
                'num_ctx': 8192,
                'temperature': 0.0,
                'seed': 42,
                'max_output_tokens': 2048,
                'timeout_seconds': 300,
            },
        }
    )

    manifest['sections'][19]['status'] = 'pending'
    manifest['sections'][20]['status'] = 'pending'
    manifest['final_state'] = 'failed'
    manifest['failure_message'] = 'ancienne interruption'
    manifest['signature'] = {
        'reference_version': manifest['reference_version'],
        'model': manifest['model'],
        'num_ctx': 8192,
        'temperature': 0.0,
        'seed': 42,
        'max_output_tokens': 2048,
        'ollama_url': manifest['ollama_url'],
        'prompt_hashes': [section['prompt_sha256'] for section in manifest['sections']],
    }


def make_reference(tmp_path: Path, *, version: str = 'vtest', section_count: int = 2) -> Path:
    benchmark_dir = tmp_path / 'benchmarks' / 'manuals' / 'docforge'
    reference_dir = benchmark_dir / version
    (reference_dir / 'section-prompts').mkdir(parents=True)
    (reference_dir / 'section-contexts').mkdir(parents=True)

    section_prompts = []
    section_contexts = []
    guide_sections = ['# Guide utilisateur de docforge', '']
    for index in range(1, section_count + 1):
        identifier = f'section-{index}'
        title = f'Section {index}'
        prompt_rel = f'section-prompts/{index:02d}-{identifier}.md'
        context_rel = f'section-contexts/{index:02d}-{identifier}.json'
        (reference_dir / prompt_rel).write_text(f'Prompt {index}\n', encoding='utf-8')
        (reference_dir / context_rel).write_text(
            json.dumps({'identifier': identifier, 'title': title}, indent=2, ensure_ascii=False) + '\n',
            encoding='utf-8',
        )
        section_prompts.append(prompt_rel)
        section_contexts.append(
            {
                'identifier': identifier,
                'title': title,
                'prompt_file': prompt_rel,
                'context_file': context_rel,
                'estimated_tokens': 100 + index,
                'context_budget': None,
            }
        )
        guide_sections.extend([f'## {title}', '', f'Contenu {index}', ''])

    (reference_dir / 'docforge-guide-usager.md').write_text('\n'.join(guide_sections).rstrip() + '\n', encoding='utf-8')
    (reference_dir / 'manual-prompt.md').write_text('prompt complet\n', encoding='utf-8')
    (reference_dir / 'manual-prompt-prepared.md').write_text('prompt complet\n', encoding='utf-8')
    (reference_dir / 'manual-knowledge.json').write_text(
        json.dumps(
            {
                'schema_version': 2,
                'profile': {'name': 'python-cli'},
                'commands': [
                    {'command_path': 'analyze', 'visibility': 'public'},
                    {'command_path': 'manual prepare', 'visibility': 'public'},
                ],
            },
            indent=2,
            ensure_ascii=False,
        ) + '\n',
        encoding='utf-8',
    )
    (reference_dir / 'manual-manifest.json').write_text(
        json.dumps(
            {
                'schema_version': 2,
                'full_prompt': 'manual-prompt.md',
                'section_prompts': section_prompts,
                'section_contexts': section_contexts,
                'command_provenance_summary': {'total_detected': 0},
            },
            indent=2,
            ensure_ascii=False,
        ) + '\n',
        encoding='utf-8',
    )
    (reference_dir / 'reference-metadata.json').write_text(
        json.dumps(
            {
                'schema_version': 1,
                'historical_notes': ['note historique'],
            },
            indent=2,
            ensure_ascii=False,
        ) + '\n',
        encoding='utf-8',
    )

    import hashlib

    def sha(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open('rb') as handle:
            for chunk in iter(lambda: handle.read(65536), b''):
                digest.update(chunk)
        return digest.hexdigest()

    paths = [
        'docforge-guide-usager.md',
        'manual-knowledge.json',
        'manual-manifest.json',
        'manual-prompt.md',
        'manual-prompt-prepared.md',
        'reference-metadata.json',
        *section_prompts,
        *(item['context_file'] for item in section_contexts),
    ]
    (reference_dir / 'checksums.sha256').write_text(
        '\n'.join(f"{sha(reference_dir / rel)}  {rel}" for rel in sorted(paths)) + '\n',
        encoding='utf-8',
    )
    return benchmark_dir


def test_reference_v09_has_21_sections_in_lexical_order() -> None:
    reference = load_reference_bundle('v0.9')
    assert len(reference.sections) == 21
    prompt_files = [section.prompt_file for section in reference.sections]
    assert prompt_files == sorted(prompt_files)
    assert prompt_files[0] == 'section-prompts/01-presentation.md'
    assert prompt_files[-1] == 'section-prompts/21-cli-reference.md'


def test_incomplete_reference_is_detected(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path)
    missing_file = benchmark_dir / 'vtest' / 'section-prompts' / '01-section-1.md'
    missing_file.unlink()
    with pytest.raises(ReferenceError):
        load_reference_bundle('vtest', benchmark_dir=benchmark_dir)


def test_reference_checksum_mismatch_is_detected(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path)
    reference_dir = benchmark_dir / 'vtest'
    (reference_dir / 'manual-prompt.md').write_text('modifié\n', encoding='utf-8')
    with pytest.raises(ReferenceError):
        verify_reference_checksums(reference_dir)


def test_unwrap_single_markdown_fence() -> None:
    wrapped = '```markdown\n## Titre\n\nTexte\n```\n'
    assert unwrap_single_markdown_fence(wrapped) == '## Titre\n\nTexte\n'
    assert unwrap_single_markdown_fence('## Titre\n') == '## Titre\n'


def test_ollama_client_parses_successful_response() -> None:
    client = OllamaClient(base_url='http://localhost:11434', timeout_seconds=30, urlopen_impl=UrlopenSequence([{'response': 'ok', 'done_reason': 'stop'}]))
    payload = client.generate(model='qwen3.5:4b', prompt='Prompt', num_ctx=8192, temperature=0, seed=42, max_output_tokens=256)
    assert payload['response'] == 'ok'


def test_ollama_client_reports_http_error_for_missing_model() -> None:
    error = HTTPError(
        url='http://localhost:11434/api/generate',
        code=404,
        msg='Not Found',
        hdrs=None,
        fp=io.BytesIO(b'{"error":"model qwen3.5:4b not found"}'),
    )
    client = OllamaClient(base_url='http://localhost:11434', timeout_seconds=30, urlopen_impl=UrlopenSequence([error]))
    with pytest.raises(Exception):
        client.generate(model='qwen3.5:4b', prompt='Prompt', num_ctx=8192, temperature=0, seed=42, max_output_tokens=256)


def test_ollama_client_reports_invalid_json() -> None:
    client = OllamaClient(base_url='http://localhost:11434', timeout_seconds=30, urlopen_impl=UrlopenSequence([b'not-json']))
    with pytest.raises(Exception):
        client.generate(model='qwen3.5:4b', prompt='Prompt', num_ctx=8192, temperature=0, seed=42, max_output_tokens=256)


def test_ollama_client_reports_empty_response() -> None:
    client = OllamaClient(base_url='http://localhost:11434', timeout_seconds=30, urlopen_impl=UrlopenSequence([{'response': '   ', 'done_reason': 'stop'}]))
    with pytest.raises(Exception):
        client.generate(model='qwen3.5:4b', prompt='Prompt', num_ctx=8192, temperature=0, seed=42, max_output_tokens=256)




@pytest.mark.parametrize(
    ('network_error', 'run_id'),
    [
        (TimeoutError('timed out'), 'timeout-direct'),
        (socket.timeout('timed out'), 'socket-timeout'),
        (URLError(socket.timeout('timed out')), 'urlerror-timeout'),
    ],
)
def test_runner_records_timeout_failures_without_traceback(tmp_path: Path, network_error: Exception, run_id: str) -> None:
    benchmark_dir = make_reference(tmp_path)
    urlopen_impl = UrlopenSequence([network_error])
    runner = ManualBenchmarkRunner(
        repo_dir=tmp_path,
        benchmark_dir=benchmark_dir,
        urlopen_impl=urlopen_impl,
        process_runner=ValidationRunner(valid=True, returncode=0),
    )
    config = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id=run_id,
        num_ctx=12288,
        temperature=0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=600,
        dry_run=False,
    )
    assert runner.run(config) == 1
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / run_id
    manifest = json.loads((run_dir / 'run-manifest.json').read_text(encoding='utf-8'))
    state = manifest['sections'][0]
    assert manifest['final_state'] == 'failed'
    assert manifest['failure_message'].startswith('Ollama n’a pas répondu avant le délai de 600 secondes')
    assert manifest['last_attempted_section'] == {'index': 1, 'identifier': 'section-1', 'title': 'Section 1'}
    assert state['status'] == 'failed'
    assert state['completed_at'] is not None
    assert state['duration_seconds'] is not None
    assert state['error_type'] == 'timeout'
    assert state['timeout_seconds'] == 600
    assert state['response_file'] is None
    assert state['response_sha256'] is None
    assert state['error'].endswith('Reprenez l’essai avec --timeout-seconds 3600.')


def test_main_prints_timeout_error_without_traceback(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def fake_run(self, config):
        raise BenchmarkError('Ollama n’a pas répondu avant le délai de 600 secondes pour la section 19 — Dépannage. Reprenez l’essai avec --timeout-seconds 3600.')

    monkeypatch.setattr(ManualBenchmarkRunner, 'run', fake_run)
    code = main([
        '--model', 'qwen3.5:4b',
        '--reference-version', 'v0.9',
        '--run-id', 'smoke-001',
        '--num-ctx', '12288',
        '--max-output-tokens', '2048',
        '--temperature', '0',
        '--seed', '42',
        '--resume',
        '--allow-resource-increase',
        '--timeout-seconds', '3600',
    ])
    captured = capsys.readouterr()
    assert code == 1
    assert 'ERREUR: Ollama n’a pas répondu avant le délai de 600 secondes' in captured.out
    assert 'Traceback' not in captured.out
    assert captured.err == ''



def test_write_timing_accepts_historical_manifest_without_prompt_eval_duration(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir)
    manifest = runner._load_or_initialize_manifest(
        tmp_path / 'missing.json',
        load_reference_bundle('vtest', benchmark_dir=benchmark_dir),
        BenchmarkConfig(
            model='qwen3.5:4b',
            reference_version='vtest',
            run_id='timing-historical',
            num_ctx=8192,
            temperature=0,
            seed=42,
            resume=False,
            ollama_url='http://localhost:11434',
            max_output_tokens=2048,
            timeout_seconds=30,
            dry_run=True,
        ),
    )
    manifest['sections'][0].update({
        'status': 'failed',
        'duration_seconds': 12.5,
        'prompt_eval_count': 100,
        'eval_count': 200,
        'total_duration': 10,
        'load_duration': 2,
        'done_reason': 'length',
        'timeout_seconds': 30,
    })
    manifest['sections'][0].pop('prompt_eval_duration', None)
    run_dir = tmp_path / 'run'
    run_dir.mkdir()
    runner._write_timing(run_dir, manifest)
    timing = json.loads((run_dir / 'timing.json').read_text(encoding='utf-8'))
    assert timing['sections'][0]['prompt_eval_duration'] is None
    assert timing['sections'][0]['done_reason'] == 'length'
    assert timing['sections'][0]['timeout_seconds'] == 30


def test_length_failure_keeps_primary_error_when_historical_sections_lack_metrics(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    benchmark_dir = make_reference(tmp_path, section_count=21)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=True, returncode=0))
    initial = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='length-historical',
        num_ctx=12288,
        temperature=0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=3600,
        dry_run=True,
    )
    assert runner.run(initial) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'length-historical'
    manifest_path = run_dir / 'run-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    build_smoke_resume_manifest(run_dir, manifest, running_section_19=False)
    for index in range(18):
        manifest['sections'][index].pop('prompt_eval_duration', None)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    urlopen_impl = UrlopenSequence([
        {
            'response': '## Section 19\n\nTexte partiel\n',
            'done_reason': 'length',
            'prompt_eval_count': 7245,
            'eval_count': 2048,
            'total_duration': 50,
            'load_duration': 5,
            'prompt_eval_duration': 20,
            'eval_duration': 25,
        },
    ])
    runner = ManualBenchmarkRunner(
        repo_dir=tmp_path,
        benchmark_dir=benchmark_dir,
        urlopen_impl=urlopen_impl,
        process_runner=ValidationRunner(valid=True, returncode=0),
    )
    resumed = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='length-historical',
        num_ctx=12288,
        temperature=0,
        seed=42,
        resume=True,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=3600,
        dry_run=False,
        allow_resource_increase=True,
    )
    assert runner.run(resumed) == 1
    captured = capsys.readouterr()
    assert 'limite de sortie atteinte (eval_count=2048, max_output_tokens=2048)' in captured.out
    assert 'Traceback' not in captured.out
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    state = manifest['sections'][18]
    assert manifest['final_state'] == 'failed'
    assert state['status'] == 'failed'
    assert state['done_reason'] == 'length'
    assert state['response_file'] == 'sections/19-section-19.response.json'
    assert state['effective_generation_parameters']['num_ctx'] == 12288
    assert state['effective_generation_parameters']['max_output_tokens'] == 2048
    timing = json.loads((run_dir / 'timing.json').read_text(encoding='utf-8'))
    assert timing['sections'][0]['prompt_eval_duration'] is None


def test_runner_resume_accepts_max_output_increase_to_3072_from_section_19(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path, section_count=21)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=True, returncode=0))
    initial = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='resume-3072',
        num_ctx=12288,
        temperature=0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=3600,
        dry_run=True,
    )
    assert runner.run(initial) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'resume-3072'
    manifest_path = run_dir / 'run-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    build_smoke_resume_manifest(run_dir, manifest, running_section_19=False)
    for index in range(18):
        manifest['sections'][index]['effective_generation_parameters']['num_ctx'] = 8192
        manifest['sections'][index]['effective_generation_parameters']['max_output_tokens'] = 2048
    manifest['generation_parameters']['num_ctx'] = 12288
    manifest['generation_parameters']['max_output_tokens'] = 2048
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    urlopen_impl = UrlopenSequence([
        {'response': '## Section 19\n\nTexte 19\n', 'done_reason': 'stop', 'prompt_eval_count': 9000, 'eval_count': 300},
        {'response': '## Section 20\n\nTexte 20\n', 'done_reason': 'stop', 'prompt_eval_count': 9100, 'eval_count': 310},
        {'response': '## Section 21\n\nTexte 21\n', 'done_reason': 'stop', 'prompt_eval_count': 9200, 'eval_count': 320},
    ])
    runner = ManualBenchmarkRunner(
        repo_dir=tmp_path,
        benchmark_dir=benchmark_dir,
        urlopen_impl=urlopen_impl,
        process_runner=ValidationRunner(valid=True, returncode=0),
    )
    resumed = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='resume-3072',
        num_ctx=12288,
        temperature=0,
        seed=42,
        resume=True,
        ollama_url='http://localhost:11434',
        max_output_tokens=3072,
        timeout_seconds=3600,
        dry_run=False,
        allow_resource_increase=True,
    )
    assert runner.run(resumed) == 0
    assert urlopen_impl.generate_calls == 3
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['resume_history'][-1]['from_section_index'] == 19
    for index in range(18):
        assert manifest['sections'][index]['effective_generation_parameters']['max_output_tokens'] == 2048
    for index in range(18, 21):
        assert manifest['sections'][index]['effective_generation_parameters']['num_ctx'] == 12288
        assert manifest['sections'][index]['effective_generation_parameters']['max_output_tokens'] == 3072

def test_assemble_guide_injects_canonical_h1_and_h2_order_and_preserves_body(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path, section_count=21)
    reference = load_reference_bundle('vtest', benchmark_dir=benchmark_dir)
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'assemble-order'
    sections_dir = run_dir / 'sections'
    sections_dir.mkdir(parents=True)
    for section in reference.sections:
        body = (
            f"# {section.title}\n\n"
            "## Generated Subtitle\n\n"
            f"Texte pour {section.title}.\n\n"
            "```md\n"
            "## code heading stays\n"
            "```\n"
        )
        (sections_dir / f'{Path(section.prompt_file).stem}.md').write_text(body, encoding='utf-8')
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir)
    guide = runner._assemble_guide(reference, run_dir)
    lines = guide.splitlines()
    assert lines[0] == '# Guide utilisateur de docforge'
    expected_h2_lines = [f'## {section.title}' for section in reference.sections]
    h2_lines = [line for line in lines if line in expected_h2_lines]
    assert h2_lines == expected_h2_lines
    assert '### Generated Subtitle' in guide
    assert '## Generated Subtitle' not in guide.splitlines()
    assert '## code heading stays' in guide
    assert 'Texte pour Section 1.' in guide


def test_reassemble_rebuilds_existing_run_without_http_and_preserves_validation_history(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path, section_count=21)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=False, returncode=1))
    config = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='reassemble-run',
        num_ctx=12288,
        temperature=0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=3600,
        dry_run=True,
    )
    assert runner.run(config) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'reassemble-run'
    manifest_path = run_dir / 'run-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    sections_dir = run_dir / 'sections'
    sections_dir.mkdir(exist_ok=True)
    for index, section in enumerate(manifest['sections'], start=1):
        stem = Path(section['prompt_file']).stem
        content = f"# {section['title']}\n\n## Sous-titre\n\nContenu {index}\n"
        md_rel = f'sections/{stem}.md'
        response_rel = f'sections/{stem}.response.json'
        (run_dir / md_rel).write_text(content, encoding='utf-8')
        (run_dir / response_rel).write_text(json.dumps({'response': content, 'done_reason': 'stop'}, ensure_ascii=False) + '\n', encoding='utf-8')
        section.update({
            'status': 'completed',
            'output_markdown_file': md_rel,
            'output_markdown_sha256': 'x',
            'response_file': response_rel,
            'response_sha256': 'y',
        })
    manifest['final_state'] = 'validation_failed'
    manifest['guide_sha256'] = 'old-guide-sha'
    manifest.pop('validation_schema_version', None)
    (run_dir / 'comparison.json').write_text(
        json.dumps({'validation_passed': False}, ensure_ascii=False) + '\n',
        encoding='utf-8',
    )
    validation_dir = run_dir / 'validation'
    validation_dir.mkdir(exist_ok=True)
    (validation_dir / 'manual-validate.json').write_text(
        json.dumps({'valid': False, 'errors': [{'code': 'OLD'}], 'warnings': []}, ensure_ascii=False) + '\n',
        encoding='utf-8',
    )
    (validation_dir / 'command-fidelity.json').write_text(
        json.dumps({'strict_error_count': 1, 'warnings': [], 'strict_errors': [{'code': 'OLD-FIDELITY'}]}, ensure_ascii=False) + '\n',
        encoding='utf-8',
    )
    (run_dir / 'benchmark-summary.md').write_text('# Old summary\n', encoding='utf-8')
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    runner = ManualBenchmarkRunner(
        repo_dir=tmp_path,
        benchmark_dir=benchmark_dir,
        urlopen_impl=NoHTTPAllowed(),
        process_runner=ValidationRunner(valid=True, returncode=0),
    )
    reassemble = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='reassemble-run',
        num_ctx=12288,
        temperature=0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=3600,
        dry_run=False,
        reassemble=True,
    )
    assert runner.run(reassemble) == 0
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['final_state'] == 'completed'
    assert manifest['validation_schema_version'] == 5
    assert manifest['validation_history']
    assert manifest['validation_history'][-1]['validation_schema_version'] == 1
    assert manifest['validation_history'][-1]['manual_validate_json']['errors'][0]['code'] == 'OLD'
    assert manifest['validation_history'][-1]['command_fidelity_json']['strict_errors'][0]['code'] == 'OLD-FIDELITY'
    guide_text = (run_dir / 'guide-genere.md').read_text(encoding='utf-8')
    assert guide_text.startswith('# Guide utilisateur de docforge\n\n## Section 1\n')
    comparison = json.loads((run_dir / 'comparison.json').read_text(encoding='utf-8'))
    assert comparison['validation_passed'] is True
    checksum_text = (run_dir / 'checksums.sha256').read_text(encoding='utf-8')
    assert 'guide-genere.md' in checksum_text


def test_reassemble_refuses_when_section_file_missing(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path, section_count=2)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=True, returncode=0))
    config = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='reassemble-missing',
        num_ctx=12288,
        temperature=0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=3600,
        dry_run=True,
    )
    assert runner.run(config) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'reassemble-missing'
    manifest_path = run_dir / 'run-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    sections_dir = run_dir / 'sections'
    sections_dir.mkdir(exist_ok=True)
    section = manifest['sections'][0]
    stem = Path(section['prompt_file']).stem
    md_rel = f'sections/{stem}.md'
    response_rel = f'sections/{stem}.response.json'
    (run_dir / md_rel).write_text('# Section 1\n\nBody\n', encoding='utf-8')
    (run_dir / response_rel).write_text('{}\n', encoding='utf-8')
    for item in manifest['sections']:
        item.update({'status': 'completed', 'output_markdown_file': md_rel, 'response_file': response_rel})
    # delete one physical section file to force refusal
    missing_stem = Path(manifest['sections'][1]['prompt_file']).stem
    manifest['sections'][1]['output_markdown_file'] = f'sections/{missing_stem}.md'
    manifest['sections'][1]['response_file'] = f'sections/{missing_stem}.response.json'
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, urlopen_impl=NoHTTPAllowed(), process_runner=ValidationRunner(valid=True, returncode=0))
    reassemble = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='reassemble-missing',
        num_ctx=12288,
        temperature=0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=3600,
        dry_run=False,
        reassemble=True,
    )
    assert runner.run(reassemble) == 1
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['final_state'] == 'failed'



def test_reassemble_ignores_resource_limit_changes_without_http(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path, section_count=2)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=True, returncode=0))
    config = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='reassemble-resource-diff',
        num_ctx=8192,
        temperature=0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=4096,
        timeout_seconds=3600,
        dry_run=True,
    )
    assert runner.run(config) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'reassemble-resource-diff'
    manifest_path = run_dir / 'run-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    (run_dir / 'sections').mkdir(exist_ok=True)
    for index, section in enumerate(manifest['sections'], start=1):
        stem = Path(section['prompt_file']).stem
        content = f"# {section['title']}\n\nBody {index}\n"
        md_rel = f'sections/{stem}.md'
        response_rel = f'sections/{stem}.response.json'
        (run_dir / md_rel).write_text(content, encoding='utf-8')
        (run_dir / response_rel).write_text(json.dumps({'response': content, 'done_reason': 'stop'}, ensure_ascii=False) + '\n', encoding='utf-8')
        section.update({'status': 'completed', 'output_markdown_file': md_rel, 'response_file': response_rel})
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    reassemble = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='reassemble-resource-diff',
        num_ctx=12288,
        temperature=0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=3600,
        dry_run=False,
        reassemble=True,
    )
    runner = ManualBenchmarkRunner(
        repo_dir=tmp_path,
        benchmark_dir=benchmark_dir,
        urlopen_impl=NoHTTPAllowed(),
        process_runner=ValidationRunner(valid=True, returncode=0),
    )
    assert runner.run(reassemble) == 0


def test_cli_reassemble_uses_exact_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    def fake_run(self, config):
        captured['config'] = config
        return 0

    monkeypatch.setattr(ManualBenchmarkRunner, 'run', fake_run)
    code = main([
        '--model', 'qwen3.5:4b',
        '--reference-version', 'v0.9',
        '--run-id', 'smoke-001',
        '--num-ctx', '12288',
        '--reassemble',
    ])
    assert code == 0
    assert captured['config'].reassemble is True


def test_runner_dry_run_creates_run_directory_and_manifest_without_absolute_home(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=True, returncode=0))
    config = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='dry-run',
        num_ctx=8192,
        temperature=0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=512,
        timeout_seconds=30,
        dry_run=True,
    )
    assert runner.run(config) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'dry-run'
    manifest_text = (run_dir / 'run-manifest.json').read_text(encoding='utf-8')
    assert '/home/sylvain' not in manifest_text
    assert 'guide_file' in manifest_text


def test_runner_preserves_raw_section_and_assembles_unwrapped_markdown(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path)
    urlopen_impl = UrlopenSequence([
        {'response': '```markdown\n## Section 1\n\nTexte 1\n```', 'done_reason': 'stop', 'prompt_eval_count': 1, 'eval_count': 2},
        {'response': '## Section 2\n\nTexte 2\n', 'done_reason': 'stop', 'prompt_eval_count': 1, 'eval_count': 2},
    ])
    runner = ManualBenchmarkRunner(
        repo_dir=tmp_path,
        benchmark_dir=benchmark_dir,
        urlopen_impl=urlopen_impl,
        process_runner=ValidationRunner(valid=True, returncode=0),
    )
    config = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='full-run',
        num_ctx=8192,
        temperature=0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=512,
        timeout_seconds=30,
        dry_run=False,
    )
    assert runner.run(config) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'full-run'
    raw_section = (run_dir / 'sections' / '01-section-1.md').read_text(encoding='utf-8')
    guide = (run_dir / 'guide-genere.md').read_text(encoding='utf-8')
    assert raw_section.startswith('```markdown')
    assert '```markdown' not in guide
    assert '## Section 1' in guide
    assert '## Section 2' in guide


def test_runner_resume_reuses_completed_sections(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=True, returncode=0))
    dry_config = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='resume-run',
        num_ctx=8192,
        temperature=0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=512,
        timeout_seconds=30,
        dry_run=True,
    )
    assert runner.run(dry_config) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'resume-run'
    manifest_path = run_dir / 'run-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    (run_dir / 'sections').mkdir(exist_ok=True)
    (run_dir / 'sections' / '01-section-1.md').write_text('## Section 1\n\nTexte 1\n', encoding='utf-8')
    (run_dir / 'sections' / '01-section-1.response.json').write_text('{}\n', encoding='utf-8')
    manifest['sections'][0].update(
        {
            'status': 'completed',
            'output_markdown_file': 'sections/01-section-1.md',
            'response_file': 'sections/01-section-1.response.json',
            'output_markdown_sha256': 'x',
            'response_sha256': 'y',
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    urlopen_impl = UrlopenSequence([
        {'response': '## Section 2\n\nTexte 2\n', 'done_reason': 'stop'},
    ])
    runner = ManualBenchmarkRunner(
        repo_dir=tmp_path,
        benchmark_dir=benchmark_dir,
        urlopen_impl=urlopen_impl,
        process_runner=ValidationRunner(valid=True, returncode=0),
    )
    resume_config = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='resume-run',
        num_ctx=8192,
        temperature=0,
        seed=42,
        resume=True,
        ollama_url='http://localhost:11434',
        max_output_tokens=512,
        timeout_seconds=30,
        dry_run=False,
    )
    assert runner.run(resume_config) == 0
    assert urlopen_impl.generate_calls == 1


def test_runner_resume_rejects_incompatible_parameters(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=True, returncode=0))
    config = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='resume-mismatch',
        num_ctx=8192,
        temperature=0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=512,
        timeout_seconds=30,
        dry_run=True,
    )
    assert runner.run(config) == 0
    mismatch = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='resume-mismatch',
        num_ctx=4096,
        temperature=0,
        seed=42,
        resume=True,
        ollama_url='http://localhost:11434',
        max_output_tokens=512,
        timeout_seconds=30,
        dry_run=True,
    )
    with pytest.raises(ResumeMismatchError):
        runner.run(mismatch)



def test_runner_records_length_failure_response_and_metrics(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path)
    urlopen_impl = UrlopenSequence([
        {
            'response': '## Section 1\n\nTexte tronqué\n',
            'done_reason': 'length',
            'prompt_eval_count': 8100,
            'eval_count': 512,
            'total_duration': 1000,
            'load_duration': 100,
            'prompt_eval_duration': 400,
            'eval_duration': 500,
        },
    ])
    runner = ManualBenchmarkRunner(
        repo_dir=tmp_path,
        benchmark_dir=benchmark_dir,
        urlopen_impl=urlopen_impl,
        process_runner=ValidationRunner(valid=True, returncode=0),
    )
    config = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='length-failure',
        num_ctx=8192,
        temperature=0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=512,
        timeout_seconds=30,
        dry_run=False,
    )
    assert runner.run(config) == 1
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'length-failure'
    manifest = json.loads((run_dir / 'run-manifest.json').read_text(encoding='utf-8'))
    state = manifest['sections'][0]
    assert manifest['final_state'] == 'failed'
    assert state['status'] == 'failed'
    assert state['completed_at'] is not None
    assert state['response_file'] == 'sections/01-section-1.response.json'
    assert state['response_sha256']
    assert state['output_markdown_file'] is None
    assert state['prompt_eval_count'] == 8100
    assert state['eval_count'] == 512
    assert state['total_duration'] == 1000
    assert state['load_duration'] == 100
    assert state['prompt_eval_duration'] == 400
    assert state['eval_duration'] == 500
    assert state['done_reason'] == 'length'
    assert 'limite de sortie atteinte' in state['error']
    assert 'fenêtre de contexte probablement pleine' in state['error']
    assert (run_dir / 'sections' / '01-section-1.response.json').is_file()
    assert not (run_dir / 'sections' / '01-section-1.md').exists()


def test_runner_resume_rejects_resource_increase_without_flag_smoke_001(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path, section_count=21)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=True, returncode=0))
    initial = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='smoke-001',
        num_ctx=8192,
        temperature=0.0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=30,
        dry_run=True,
    )
    assert runner.run(initial) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'smoke-001'
    manifest_path = run_dir / 'run-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    build_smoke_resume_manifest(run_dir, manifest, running_section_19=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    resumed = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='smoke-001',
        num_ctx=12288,
        temperature=0,
        seed=42,
        resume=True,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=30,
        dry_run=False,
    )
    with pytest.raises(ResumeMismatchError, match='allow-resource-increase'):
        runner.run(resumed)


def test_runner_resume_accepts_smoke_001_resource_increase_and_starts_at_section_19(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path, section_count=21)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=True, returncode=0))
    initial = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='smoke-001',
        num_ctx=8192,
        temperature=0.0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=30,
        dry_run=True,
    )
    assert runner.run(initial) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'smoke-001'
    manifest_path = run_dir / 'run-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    build_smoke_resume_manifest(run_dir, manifest, running_section_19=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    urlopen_impl = UrlopenSequence([
        {'response': '## Section 19\n\nTexte 19\n', 'done_reason': 'stop', 'prompt_eval_count': 9000, 'eval_count': 200},
        {'response': '## Section 20\n\nTexte 20\n', 'done_reason': 'stop', 'prompt_eval_count': 9100, 'eval_count': 210},
        {'response': '## Section 21\n\nTexte 21\n', 'done_reason': 'stop', 'prompt_eval_count': 9200, 'eval_count': 220},
    ])
    runner = ManualBenchmarkRunner(
        repo_dir=tmp_path,
        benchmark_dir=benchmark_dir,
        urlopen_impl=urlopen_impl,
        process_runner=ValidationRunner(valid=True, returncode=0),
    )
    resumed = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='smoke-001',
        num_ctx=12288,
        temperature=0,
        seed=42,
        resume=True,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=3600,
        dry_run=False,
        allow_resource_increase=True,
    )
    assert runner.run(resumed) == 0
    assert urlopen_impl.generate_calls == 3

    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['final_state'] == 'completed'
    assert manifest['generation_parameters']['num_ctx'] == 12288
    assert manifest['generation_parameters']['timeout_seconds'] == 3600
    assert manifest['effective_generation_parameters']['mode'] == 'mixed'
    assert manifest['resume_history'][-1]['from_section_index'] == 19
    assert manifest['resume_history'][-1]['from_generation_parameters']['num_ctx'] == 8192
    assert manifest['resume_history'][-1]['to_generation_parameters']['num_ctx'] == 12288
    assert manifest['resume_history'][-1]['to_generation_parameters']['timeout_seconds'] == 3600
    assert manifest['sections'][18]['started_at'] is not None
    assert manifest['sections'][18]['status'] == 'completed'
    for index in range(18):
        assert manifest['sections'][index]['effective_generation_parameters']['num_ctx'] == 8192
    for index in range(18, 21):
        assert manifest['sections'][index]['effective_generation_parameters']['num_ctx'] == 12288


def test_runner_resume_rejects_context_decrease_even_when_explicitly_allowed(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path, section_count=21)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=True, returncode=0))
    initial = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='resume-decrease',
        num_ctx=8192,
        temperature=0.0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=30,
        dry_run=True,
    )
    assert runner.run(initial) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'resume-decrease'
    manifest_path = run_dir / 'run-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    build_smoke_resume_manifest(run_dir, manifest, running_section_19=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    lowered = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='resume-decrease',
        num_ctx=4096,
        temperature=0,
        seed=42,
        resume=True,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=30,
        dry_run=True,
        allow_resource_increase=True,
    )
    with pytest.raises(ResumeMismatchError, match='réduire'):
        runner.run(lowered)


def test_runner_resume_rejects_model_change(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path, section_count=21)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=True, returncode=0))
    initial = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='resume-model',
        num_ctx=8192,
        temperature=0.0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=30,
        dry_run=True,
    )
    assert runner.run(initial) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'resume-model'
    manifest_path = run_dir / 'run-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    build_smoke_resume_manifest(run_dir, manifest, running_section_19=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    changed = BenchmarkConfig(
        model='qwen3.5:9b',
        reference_version='vtest',
        run_id='resume-model',
        num_ctx=12288,
        temperature=0,
        seed=42,
        resume=True,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=30,
        dry_run=True,
        allow_resource_increase=True,
    )
    with pytest.raises(ResumeMismatchError, match='model'):
        runner.run(changed)


def test_runner_resume_rejects_temperature_change_but_accepts_0_and_0_0(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path, section_count=21)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=True, returncode=0))
    initial = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='resume-temperature',
        num_ctx=8192,
        temperature=0.0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=30,
        dry_run=True,
    )
    assert runner.run(initial) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'resume-temperature'
    manifest_path = run_dir / 'run-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    build_smoke_resume_manifest(run_dir, manifest, running_section_19=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    accepted = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='resume-temperature',
        num_ctx=12288,
        temperature=0,
        seed=42,
        resume=True,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=30,
        dry_run=True,
        allow_resource_increase=True,
    )
    runner.run(accepted)

    changed = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='resume-temperature',
        num_ctx=12288,
        temperature=0.25,
        seed=42,
        resume=True,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=30,
        dry_run=True,
        allow_resource_increase=True,
    )
    with pytest.raises(ResumeMismatchError, match='temperature'):
        runner.run(changed)


def test_runner_resume_rejects_seed_change(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path, section_count=21)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=True, returncode=0))
    initial = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='resume-seed',
        num_ctx=8192,
        temperature=0.0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=30,
        dry_run=True,
    )
    assert runner.run(initial) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'resume-seed'
    manifest_path = run_dir / 'run-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    build_smoke_resume_manifest(run_dir, manifest, running_section_19=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    changed = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='resume-seed',
        num_ctx=12288,
        temperature=0,
        seed=7,
        resume=True,
        ollama_url='http://localhost:11434',
        max_output_tokens=2048,
        timeout_seconds=30,
        dry_run=True,
        allow_resource_increase=True,
    )
    with pytest.raises(ResumeMismatchError, match='seed'):
        runner.run(changed)


def test_cli_resume_accepts_exact_resource_increase_args(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    def fake_run(self, config):
        captured['config'] = config
        return 0

    monkeypatch.setattr(ManualBenchmarkRunner, 'run', fake_run)
    code = main([
        '--model', 'qwen3.5:4b',
        '--reference-version', 'v0.9',
        '--run-id', 'smoke-001',
        '--num-ctx', '12288',
        '--max-output-tokens', '2048',
        '--temperature', '0',
        '--seed', '42',
        '--resume',
        '--allow-resource-increase',
        '--timeout-seconds', '3600',
    ])
    assert code == 0
    config = captured['config']
    assert config.num_ctx == 12288
    assert config.max_output_tokens == 2048
    assert config.temperature == 0.0
    assert config.seed == 42
    assert config.resume is True
    assert config.allow_resource_increase is True
    assert config.timeout_seconds == 3600


def test_parse_command_coverage_and_title_comparison(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path)
    reference = load_reference_bundle('vtest', benchmark_dir=benchmark_dir)
    guide = tmp_path / 'candidate.md'
    guide.write_text('# Guide utilisateur de docforge\n\n## Section 1\n\nTexte\n', encoding='utf-8')
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir)
    comparison = runner._build_comparison(
        reference,
        guide,
        {
            'exit_code': 1,
            'manual_validate_json': {'valid': False, 'errors': [{'code': 'MANUAL003'}], 'warnings': []},
            'command_coverage': parse_command_coverage(
                'Commandes détectées : 2\n'
                'Couverture command_path : 1/2\n'
                'Couverture invocation exécutable : 0/2\n'
                '\n'
                'Commandes totalement absentes : manual prepare\n'
                'Commandes présentes seulement par command_path : analyze-template\n'
                'Invocations complètes manquantes : analyze-template, manual prepare\n'
            ),
            'command_fidelity_json': {'strict_error_count': 0, 'warning_count': 2, 'unknown_options': []},
        },
    )
    assert comparison['missing_titles'] == ['Section 2']
    assert comparison['missing_commands'] == ['manual prepare']
    assert comparison['validation_passed'] is False


def test_runner_keeps_generated_guide_when_validation_fails(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path)
    urlopen_impl = UrlopenSequence([
        {'response': '## Section 1\n\nTexte 1\n', 'done_reason': 'stop'},
        {'response': '## Section 2\n\nTexte 2\n', 'done_reason': 'stop'},
    ])
    runner = ManualBenchmarkRunner(
        repo_dir=tmp_path,
        benchmark_dir=benchmark_dir,
        urlopen_impl=urlopen_impl,
        process_runner=ValidationRunner(valid=False, returncode=1),
    )
    config = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='validation-fail',
        num_ctx=8192,
        temperature=0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=512,
        timeout_seconds=30,
        dry_run=False,
    )
    assert runner.run(config) == 1
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'validation-fail'
    assert (run_dir / 'guide-genere.md').is_file()
    manifest = json.loads((run_dir / 'run-manifest.json').read_text(encoding='utf-8'))
    assert manifest['final_state'] == 'validation_failed'


def test_parse_args_uses_default_temperature() -> None:
    args = parse_args([
        '--model', 'qwen3.5:4b',
        '--reference-version', 'v0.9',
        '--run-id', 'verification',
        '--num-ctx', '8192',
        '--dry-run',
    ])
    assert args.temperature == 0.0


def test_parse_args_allows_explicit_temperature_override() -> None:
    args = parse_args([
        '--model', 'qwen3.5:4b',
        '--reference-version', 'v0.9',
        '--run-id', 'verification',
        '--num-ctx', '8192',
        '--temperature', '0.35',
        '--dry-run',
    ])
    assert args.temperature == 0.35


def test_manifest_records_effective_default_temperature(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=True, returncode=0))
    config = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='default-temperature',
        num_ctx=8192,
        temperature=0.0,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=512,
        timeout_seconds=30,
        dry_run=True,
    )
    assert runner.run(config) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'default-temperature'
    manifest = json.loads((run_dir / 'run-manifest.json').read_text(encoding='utf-8'))
    assert manifest['generation_parameters']['temperature'] == 0.0


def test_manifest_records_explicit_temperature_override(tmp_path: Path) -> None:
    benchmark_dir = make_reference(tmp_path)
    runner = ManualBenchmarkRunner(repo_dir=tmp_path, benchmark_dir=benchmark_dir, process_runner=ValidationRunner(valid=True, returncode=0))
    config = BenchmarkConfig(
        model='qwen3.5:4b',
        reference_version='vtest',
        run_id='explicit-temperature',
        num_ctx=8192,
        temperature=0.25,
        seed=42,
        resume=False,
        ollama_url='http://localhost:11434',
        max_output_tokens=512,
        timeout_seconds=30,
        dry_run=True,
    )
    assert runner.run(config) == 0
    run_dir = benchmark_dir / 'runs' / 'vtest' / 'qwen3.5-4b' / 'explicit-temperature'
    manifest = json.loads((run_dir / 'run-manifest.json').read_text(encoding='utf-8'))
    assert manifest['generation_parameters']['temperature'] == 0.25
