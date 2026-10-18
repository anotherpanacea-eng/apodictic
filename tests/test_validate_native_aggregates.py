"""Behavioral contracts for native aggregation, gate launch and canonical production."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / 'plugins/apodictic/scripts'
REFERENCES = SCRIPTS.parent / 'skills/core-editor/references'


def load(name):
    spec = importlib.util.spec_from_file_location('native_test_' + name, SCRIPTS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    with patch.object(sys, 'path', [str(SCRIPTS), *sys.path]):
        spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('bad', [None, 'gate', 'contract-hash', 'argument-carve-behavior-preservation'])
def test_aggregate_runs_all_children_once_and_accounts_for_shared_gate(bad):
    module = load('validate')
    calls, lines = [], []
    def child(argv, **kwargs):
        calls.append(argv)
        assert argv[:2] == [sys.executable, str(SCRIPTS / 'validate.py')]
        assert argv[-1] == '--self-test'
        assert kwargs['stdout'] == kwargs['stderr'] == subprocess.DEVNULL
        assert kwargs['env']['PYTHONIOENCODING'] == 'utf-8'
        return subprocess.CompletedProcess(argv, 7 if argv[2] == bad else 0)
    with patch.object(module.subprocess, 'run', child), patch.object(module, '_line', lambda text='': lines.append(text)):
        assert module._self_test_all() == int(bad is not None)
    assert [call[2] for call in calls] == [command for command in module.AGG_VALIDATORS if command != 'gate-state']
    assert len(calls) == len(module.AGG_VALIDATORS) - 1
    assert sum(call[2] == 'gate' for call in calls) == 1
    expected = '  gate-state: FAIL (gate shared suite failed)' if bad == 'gate' else '  gate-state: PASS (covered by gate shared suite)'
    assert expected in lines
    assert str(len(module.AGG_VALIDATORS)) in lines[-1]


@pytest.mark.parametrize('self_status, canonical_status', [(0, 0), (1, 0), (0, 1), (1, 1)])
def test_full_aggregate_accumulates_and_canonical_only_does_not_recurse(self_status, canonical_status):
    module = load('validate')
    calls, lines = [], []
    def self_tests():
        calls.append('self-tests'); return self_status
    def canonical():
        calls.append('canonical'); return canonical_status
    with patch.dict(sys.modules, {'validate_canonical': SimpleNamespace(run_canonical=canonical)}), patch.object(module, '_self_test_all', self_tests), patch.object(module, '_line', lambda text='': lines.append(text)):
        assert module.main(['--check-all']) == int(bool(self_status or canonical_status))
        assert calls == ['self-tests', 'canonical']
        calls.clear()
        assert module.main(['--check-canonical']) == canonical_status
        assert calls == ['canonical']
    assert 'canonical shard' in lines[-1]


@pytest.mark.parametrize('command, args, wanted', [
    ('gate', ['--self-test', 'ignored'], ['--self-test']),
    ('gate-state', ['--self-test', 'ignored'], ['--self-test']),
    ('gate', ['run phase', 'folder with spaces', '--strict-warnings'], ['run phase', 'folder with spaces', '--strict-warnings']),
    ('gate-state', ['state with spaces.json', '--strict'], ['--check-state', 'state with spaces.json', '--strict']),
    ('gate', ['--attest', 'phase', 'folder'], ['--attest', 'phase', 'folder']),
])
def test_gate_wrapper_preserves_raw_arguments_and_status(command, args, wanted):
    module = load('validate')
    with patch.object(module, '_run_helper', return_value=9) as helper:
        assert module.main([command, *args]) == 9
    helper.assert_called_once_with('run_gate.py', wanted)


@pytest.mark.parametrize('status, stdout, stderr, strict, expected', [
    (0, 'ok', '', False, 'ok'), (0, '', 'WARN from stderr', False, 'warn'),
    (0, '', 'WARN from stderr', True, 'warn'), (2, '', 'bad usage', False, 'fail'),
    (7, 'WARN', '', False, 'fail'),
])
def test_gate_children_use_native_dispatcher_and_keep_result_semantics(tmp_path, status, stdout, stderr, strict, expected):
    module = load('run_gate')
    manifest = {'artifact_keys': {}, 'phases': {'phase': {'entry_requires': {'checks': [
        {'validator': 'custom-nonofficial-leaf', 'targets': ['run_folder']},
        {'validator': '--self-test-all', 'targets': []},
    ]}}}}
    calls = []
    def child(argv, **kwargs):
        calls.append(argv)
        assert kwargs['encoding'] == 'utf-8'
        return subprocess.CompletedProcess(argv, status, stdout, stderr)
    with patch.object(module.subprocess, 'run', child):
        actual, _, checks, _, _ = module.run_checks('phase', str(tmp_path), manifest, strict)
    assert actual == expected
    prefix = [sys.executable, str(SCRIPTS / 'validate.py')]
    assert calls == [prefix + ['custom-nonofficial-leaf', str(tmp_path)], prefix + ['--self-test-all']]
    assert all(row['result'] == ('error' if status else 'warn' if 'WARN' in stdout + stderr else 'ok') for row in checks)


def test_canonical_launcher_uses_fixed_sibling_and_preserves_bytes(tmp_path):
    module = load('validate_canonical')
    scripts = tmp_path / 'script directory with spaces'
    scripts.mkdir()
    shutil.copyfile(SCRIPTS / 'validate_canonical.py', scripts / 'validate_canonical.py')
    (scripts / 'validate.py').write_text("import sys\nsys.stdout.buffer.write(b'out\\x00\\xff')\nsys.stderr.buffer.write(b'err\\r\\n')\nraise SystemExit(7)\n", encoding='utf-8')
    module.__file__ = str(scripts / 'validate_canonical.py')
    with patch.dict(os.environ, {'PATH': ''}):
        result = module.run_validator('custom', tmp_path / 'argument with spaces')
    assert (result.returncode, result.stdout, result.stderr) == (7, b'out\x00\xff', b'err\r\n')


def test_original_unguarded_capture_aborts_but_guarded_checks_accumulate():
    module = load('validate_canonical')
    result = subprocess.CompletedProcess([], 9, b'', b'named failure')
    with pytest.raises(SystemExit) as error:
        module._captured(result)
    assert error.value.code == 9
    with patch.object(module, '_line'):
        assert module._summary('failed row', False) == 1
        assert module._summary('later row', True) == 0


@pytest.mark.parametrize('section, relative', [('argument_corpus', 'fixtures/argument-benchmark'), ('agd_fiction', 'fixtures/argument-agd'), ('agd_fiction', 'fixtures/fiction-benchmark')])
def test_empty_installed_required_corpus_is_not_success(tmp_path, section, relative):
    module = load('validate_canonical')
    corpus = tmp_path / relative; corpus.mkdir(parents=True)
    with patch.object(module, '_locate', side_effect=lambda name, **kwargs: corpus if name == relative else None), patch.object(module, '_line'):
        assert getattr(module, '_' + section)(REFERENCES) == 1


def test_required_hostile_aif_files_cannot_pass_as_missing_input(tmp_path):
    module = load('validate_canonical')
    fixture = tmp_path / 'final-audit'; fixture.mkdir()
    # Positive producer/consumer doubles succeed. Missing hostile inputs must still fail.
    with patch.object(module, '_locate', return_value=fixture), patch.object(module, 'run_validator', return_value=subprocess.CompletedProcess([], 0, b'', b'')), patch.object(module, '_line'):
        assert module._aif(REFERENCES) == 1


def test_exports_require_counts_and_actual_raw_golden_bytes(tmp_path):
    module = load('validate_canonical')
    refs = tmp_path / 'references'; source = refs / 'example-annotated-manuscript'
    shutil.copytree(REFERENCES / 'example-annotated-manuscript', source)
    evals = tmp_path / 'evals'; evals.mkdir()
    # Installed evals with no binary goldens must FAIL, even though real generation succeeds.
    with patch.object(module, '_evals', return_value=evals), patch.object(module, '_line'):
        assert module._exports(refs) == 1
    # A standalone package may skip only the binary golden comparisons.
    with patch.object(module, '_evals', return_value=None), patch.object(module, '_line'):
        assert module._exports(refs) == 0
    # Same-length committed text corruption must fail exact raw-byte comparison.
    golden = next((source / 'obsidian').glob('*.md'))
    data = golden.read_bytes(); golden.write_bytes(bytes([data[0] ^ 1]) + data[1:])
    with patch.object(module, '_evals', return_value=None), patch.object(module, '_line'):
        assert module._exports(refs) == 1
    # Successful child status with no produced outputs is never a clean export.
    with patch.object(module, '_producer', return_value=subprocess.CompletedProcess([], 0, b'', b'')), patch.object(module, 'run_validator', return_value=subprocess.CompletedProcess([], 0, b'', b'')), patch.object(module, '_line'):
        assert module._exports(refs) == 1


def test_final_stance_and_repository_reconstruction_missing_remain_failures(tmp_path):
    module = load('validate_canonical')
    module.HERE = tmp_path / 'scripts'; module.HERE.mkdir()
    lines = []
    with patch.object(module, '_locate', return_value=None), patch.object(module, '_evals', return_value=tmp_path), patch.object(module, 'run_validator', return_value=subprocess.CompletedProcess([], 0, b'', b'')), patch.object(module, '_line', lambda text='': lines.append(text)):
        assert module._final_checks(REFERENCES) == 1
    assert '  FAIL (fixture directory not found)' in lines
    assert '  FAIL (E7 strict fixture root not found)' in lines
    assert 'FAIL: reconstruction behavioral suite missing from repository checkout' in lines


def test_strict_gate_and_fresh_attest_use_current_child_evidence(tmp_path):
    module = load('run_gate')
    artifact = tmp_path / 'input.md'; artifact.write_text('clean', encoding='utf-8')
    manifest = {'artifact_keys': {}, 'phases': {'phase': {'entry_requires': {
        'checks': [{'validator': 'custom', 'targets': ['run_folder']}],
        'attested': [{'id': 'confirmed', 'text': 'Confirm'}],
    }}}}
    calls = []
    def child(argv, **kwargs):
        value = artifact.read_text(encoding='utf-8'); calls.append(value)
        return subprocess.CompletedProcess(argv, int(value == 'broken'), '', 'WARN' if value == 'warn' else '')
    with patch.object(module.subprocess, 'run', child):
        assert module.cmd_gate('phase', str(tmp_path), manifest)[0] == 0
        artifact.write_text('broken', encoding='utf-8')
        assert module.cmd_attest('phase', str(tmp_path), manifest)[0] == 1
        artifact.write_text('warn', encoding='utf-8')
        assert module.cmd_gate('phase', str(tmp_path), manifest, strict_warnings=True)[0] == 1
    assert calls == ['clean', 'broken', 'warn']


@pytest.mark.parametrize('first_template, second_template, first_aif, second_aif', [
    (True, True, True, True), (False, True, True, True),
    (True, False, True, False), (False, False, False, False),
])
def test_template_and_aif_mirrors_preserve_distinct_presence_order(tmp_path, first_template, second_template, first_aif, second_aif):
    module = load('validate_canonical')
    module.HERE = tmp_path / 'plugin/scripts'; module.HERE.mkdir(parents=True)
    first = module.HERE / '../skills/core-editor/references'
    second = module.HERE / '../plugins/apodictic/skills/core-editor/references'
    for root, template, aif in ((first, first_template, first_aif), (second, second_template, second_aif)):
        root.mkdir(parents=True)
        if template:
            (root / 'diagnostic-state-meta-template.json').write_text('{}', encoding='utf-8')
        if aif:
            (root / 'example-argument-aif-export.json').write_text('{}', encoding='utf-8')
    calls, lines = [], []
    def child(command, *arguments):
        calls.append((command, arguments))
        return subprocess.CompletedProcess([], 0, b'', b'')
    with patch.object(module, 'run_validator', child), patch.object(module, '_line', lambda text='': lines.append(text)):
        assert module.run_canonical() == 1  # Other required examples intentionally absent.
    templates = [args[0] for command, args in calls if command == 'structured-findings']
    expected_template = first if first_template else second if second_template else None
    assert templates == ([expected_template / 'diagnostic-state-meta-template.json'] if expected_template else [])
    aifs = [args[0] for command, args in calls if command == 'argument-aif-check']
    expected_aif = second if second_aif else first if first_aif else None
    assert aifs == ([expected_aif / 'example-argument-aif-export.json'] if expected_aif else [])
    if expected_template is None:
        assert any('could not locate reference templates' in line for line in lines)
