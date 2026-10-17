"""Nonexecution and false-proof regressions for the native source guarantees.

The inspected programs are data. None of these hostile fixtures is imported,
compiled to executable code, or run; marker files must remain absent.
"""
import ast
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / 'plugins/apodictic/scripts'
sys.path.insert(0, str(SCRIPTS))
from validate_source import (SourceError, read_aggregate, read_dispatch, read_canonical,
                             check_aggregate_count, schema_literals)


@pytest.fixture
def dispatcher(tmp_path):
    path = tmp_path / 'validate.py'
    path.write_text((SCRIPTS / 'validate.py').read_text(encoding='utf-8'), encoding='utf-8')
    return path


def mutate(path, before, after):
    source = path.read_text(encoding='utf-8')
    assert before in source
    path.write_text(source.replace(before, after, 1), encoding='utf-8')


def test_live_bound_helpers_are_command_specific(dispatcher):
    routes = read_dispatch(dispatcher)
    assert routes['ledger-check'].helper_files == ('letter_checks.py',)
    assert routes['artifact-names'].helper_files == ('config_checks.py',)
    assert routes['argument-carve-behavior-preservation'].self_test_kind == 'carve'
    assert routes['contract-hash'].self_test_kind == 'utility'
    assert routes['pdf-export'].helper_files == ('annotation_export.py',)
    assert routes['gate'].helper_files == routes['gate-state'].helper_files == ('run_gate.py',)


@pytest.mark.parametrize('body', [
    '', 'AGG_VALIDATORS = []', 'AGG_VALIDATORS = ()', "AGG_VALIDATORS = ('a', 'a')",
    "AGG_VALIDATORS = ('',)", "AGG_VALIDATORS = ('a', 4)",
    "AGG_VALIDATORS = tuple(['a'])", "AGG_VALIDATORS = (f'{1}',)",
    "AGG_VALIDATORS = ('a',)\nAGG_VALIDATORS = ('b',)",
    "AGG_VALIDATORS = ('a',)\ndef f():\n AGG_VALIDATORS = ('b',)",
    "AGG_VALIDATORS = ('a',)\ndef f():\n del AGG_VALIDATORS",
    "AGG_VALIDATORS = ('a',)\nAGG_VALIDATORS += ('b',)",
    "AGG_VALIDATORS = ('a',)\nAGG_VALIDATORS: tuple = ('b',)",
    "AGG_VALIDATORS = ('a',)\n(AGG_VALIDATORS := ('b',))",
    "AGG_VALIDATORS = ('a',)\nfrom other import x as AGG_VALIDATORS",
    "AGG_VALIDATORS = ('a',)\nalias = AGG_VALIDATORS",
    'not Python [',
])
def test_aggregate_refuses_ambiguous_or_dynamic_source(tmp_path, body):
    path = tmp_path / 'validate.py'; path.write_text(body, encoding='utf-8')
    with pytest.raises(SourceError): read_aggregate(path)


def test_reader_never_executes_registry(tmp_path):
    marker = tmp_path / 'must-not-exist'
    path = tmp_path / 'validate.py'
    path.write_text(f"AGG_VALIDATORS = (__import__('pathlib').Path({str(marker)!r}).touch(),)\n", encoding='utf-8')
    with pytest.raises(SourceError): read_aggregate(path)
    assert not marker.exists()
    with pytest.raises(SourceError): read_aggregate(tmp_path / 'missing.py')


@pytest.mark.parametrize(('before', 'after'), [
    ('"ledger-check": ("letter_checks.py",', '"ledger-check": ("letter_checks.py", 1, "x"), "ledger-check": ("letter_checks.py",'),
    ('def _helper(command, args):', 'def _helper(command, args):\n    return 0'),
    ('def _helper(command, args):', 'def _helper(command, args):\n    if False:\n        return _run_helper("letter_checks.py", ["--self-test"])\n    return 0'),
    ('return _run_helper(script, helper_args)', 'print("letter_checks.py --self-test")\n    return 0'),
    ('return _run_helper(script, helper_args)', 'return False and _run_helper(script, helper_args)'),
    ('return _run_helper(script, helper_args)', 'if command == "other":\n        return _run_helper(script, helper_args)\n    return 0'),
    ('return _run_helper(script, helper_args)', 'if unknown:\n        return _run_helper(script, helper_args)\n    return 0'),
    ('helper_args = ["--self-test", command]', 'helper_args = ["--wrong", command]'),
    ('if command in _HELPERS:', 'if command in {}:'),
    ('def main(argv=None):', 'def main(argv=None):\n    if True:\n        return 0'),
    ('return _run_helper(suite, [])', 'return 0'),
    ('suite = root / "tests/test_pdf_navigation.py"', 'suite = root / "tests/other.py"'),
    ('return _run_helper(script, helper_args)', 'return _run_helper("missing.py", [])'),
])
def test_route_decoys_do_not_supply_proof(dispatcher, before, after):
    mutate(dispatcher, before, after)
    with pytest.raises(SourceError): read_dispatch(dispatcher)


@pytest.mark.parametrize('extra', [
    '\n_run_helper = lambda *a: 0\n', '\ndef _run_helper(script, args): return 0\n',
    '\ndef f():\n _helper = lambda *a: 0\n', '\n_HELPERS["ledger-check"] = ("wrong.py",)\n',
    '\n_HELPERS.update({})\n', '\nalias = _HELPERS\n', '\ndel _HELPERS["ledger-check"]\n',
    '\nfrom other import _helper\n',
])
def test_rebinding_mutation_and_escape_refuse(dispatcher, extra):
    with dispatcher.open('a', encoding='utf-8') as handle: handle.write(extra)
    with pytest.raises(SourceError): read_dispatch(dispatcher)


def test_overwritten_helper_is_the_actual_binding(dispatcher):
    mutate(dispatcher, 'return _run_helper(script, helper_args)', 'script = "wrong.py"\n    return _run_helper(script, helper_args)')
    with pytest.raises(SourceError): read_dispatch(dispatcher)


def test_schema_literal_is_whole_nonprose_data(tmp_path):
    path = tmp_path / 'helper.py'
    path.write_text('"""apodictic.alpha.v1"""\n# apodictic.beta.v1\nSCHEMA = "apodictic.gamma.v1"\n', encoding='utf-8')
    assert schema_literals(path) == ('apodictic.gamma.v1',)


@pytest.mark.parametrize(('before', 'after'), [
    ('total = len(AGG_VALIDATORS)', 'total = 84'),
    ('    passed = 0', '    total = 84\n    passed = 0'),
    ('for command in AGG_VALIDATORS:', 'for command in (): '),
    ('command, "--self-test"],', '"wrong-command", "--self-test"],'),
    ('ok = child.returncode == 0', 'ok = True'),
    ('{failed}/{total} validators failed', '{failed}/84 validators failed'),
    ('{passed}/{total} validators)', '{passed}/84 validators)'),
])
def test_disconnected_loop_or_count_cannot_pass(dispatcher, before, after):
    mutate(dispatcher, before, after)
    with pytest.raises(SourceError): check_aggregate_count(dispatcher)


def canonical_pair(tmp_path, body, section_body=None):
    dispatcher = tmp_path / 'validate.py'
    dispatcher.write_text(textwrap.dedent('''
        from validate_canonical import run_canonical
        import sys
        def main(argv=None):
            args = list(sys.argv[1:] if argv is None else argv)
            if args and args[0] == '--check-canonical':
                result = run_canonical()
                return result
            if args and args[0] == '--check-all':
                result = run_canonical()
                return result
        if __name__ == '__main__':
            sys.exit(main())
    '''), encoding='utf-8')
    canonical = tmp_path / 'validate_canonical.py'
    source = textwrap.dedent('''
        from pathlib import Path
        import subprocess, sys
        def run_validator(command, *arguments):
            return subprocess.run([sys.executable, str(Path(__file__).resolve().parent / 'validate.py'), command, *arguments])
        def run_canonical():
            references = Path(__file__).resolve().parent / '../skills/core-editor/references'
    ''')
    source += textwrap.indent(textwrap.dedent(body).strip() + '\n', '    ')
    if section_body:
        source += '\ndef section(references):\n' + textwrap.indent(textwrap.dedent(section_body).strip() + '\n', '    ')
    canonical.write_text(source, encoding='utf-8')
    return dispatcher, canonical


def has_example(calls):
    return any(c.command == 'alpha' and ('example.md',) in c.reference_paths for c in calls)


@pytest.mark.parametrize('body', [
    "run_validator('alpha', references / 'example.md')",
    "P = references / 'example.md'\nrun_validator('alpha', P)",
    "P = references / 'wrong.md'\nP = references / 'example.md'\nrun_validator('alpha', P)",
    "if (references / 'example.md').is_file():\n run_validator('alpha', references / 'example.md')",
])
def test_canonical_direct_and_ordered_one_hop(tmp_path, body):
    assert has_example(read_canonical(*canonical_pair(tmp_path, body)))


@pytest.mark.parametrize('body', [
    "print('example.md')", "'run_validator alpha example.md'", "# run_validator('alpha', references / 'example.md')\nreturn 0",
    "run_validator('beta', references / 'example.md')", "run_validator('alpha', references / 'example.md.bak')",
    "run_validator('alpha', references / 'not-example.md')",
    "P = references / 'wrong.md'\nrun_validator('alpha', P)\nP = references / 'example.md'",
    "P = references / 'example.md'\nQ = P\nrun_validator('alpha', Q)",
    "if False:\n run_validator('alpha', references / 'example.md')",
    "False and run_validator('alpha', references / 'example.md')",
    "return 0\nrun_validator('alpha', references / 'example.md')",
    "if unknown:\n P = references / 'example.md'\nrun_validator('alpha', P)",
])
def test_canonical_decoys_do_not_supply_path_proof(tmp_path, body):
    assert not has_example(read_canonical(*canonical_pair(tmp_path, body)))


def test_direct_section_and_guards(tmp_path):
    pair = canonical_pair(tmp_path, 'if references.is_dir():\n result = section(references)\nreturn 0', "run_validator('alpha', references / 'example.md')")
    assert has_example(read_canonical(*pair))
    mutate(pair[1], 'section(references)', 'section(other)')
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize('extra', [
    '\nrun_validator = lambda *a: None\n', '\ndef run_validator(*args): return None\n',
    '\ndef run_canonical(): return 0\n',
])
def test_canonical_rebound_callable_refuses(tmp_path, extra):
    pair = canonical_pair(tmp_path, "run_validator('alpha', references / 'example.md')")
    with pair[1].open('a', encoding='utf-8') as handle: handle.write(extra)
    with pytest.raises(SourceError): read_canonical(*pair)


def test_canonical_disconnected_entry_refuses(tmp_path):
    pair = canonical_pair(tmp_path, "run_validator('alpha', references / 'example.md')")
    mutate(pair[0], 'result = run_canonical()', 'result = 0')
    with pytest.raises(SourceError): read_canonical(*pair)

SELECTOR = "next((path for path in (HERE / '../skills/core-editor/references', HERE / '../plugins/apodictic/skills/core-editor/references') if path.is_dir()), HERE / '../skills/core-editor/references')"


def selector_pair(tmp_path, selector=SELECTOR, tail='result = section(references)'):
    pair = canonical_pair(tmp_path, tail, "run_validator('alpha', references / 'example.md')")
    source = pair[1].read_text(encoding='utf-8').replace('def run_validator', 'HERE = Path(__file__).resolve().parent\ndef run_validator', 1)
    source = source.replace("Path(__file__).resolve().parent / '../skills/core-editor/references'", selector, 1)
    pair[1].write_text(source, encoding='utf-8')
    return pair


def test_selector_supplies_root_not_an_anchor(tmp_path):
    pair = selector_pair(tmp_path)
    assert has_example(read_canonical(*pair))
    mutate(pair[1], 'result = section(references)', 'return 0')
    assert not has_example(read_canonical(*pair))


@pytest.mark.parametrize('selector', [
    SELECTOR.replace("HERE / '../skills/core-editor/references'", "HERE / '../extra/references'", 1),
    SELECTOR.replace("HERE / '../skills/core-editor/references'", 'dynamic_root', 1),
    SELECTOR.replace('path.is_dir()', 'side_effect()'),
    SELECTOR.replace('path.is_dir()', 'path.is_dir() or side_effect()'),
    SELECTOR.replace('path.is_dir()', "(path / 'unexpected.json').is_file()"),
    SELECTOR.replace("), HERE / '../skills/core-editor/references')", "), wrong_fallback)"),
    SELECTOR.replace('if path.is_dir()', 'if path.is_dir() for extra in other'),
])
def test_selector_unknown_shapes_fail_closed(tmp_path, selector):
    with pytest.raises(SourceError): read_canonical(*selector_pair(tmp_path, selector))


@pytest.mark.parametrize('tail', [
    'references = other\nresult = section(references)',
    'result = section(other)',
    'result = section(references)\nreferences = other',
    'if unknown:\n references = other\nresult = section(references)',
])
def test_selector_rebind_or_wrong_section_argument_refuses(tmp_path, tail):
    with pytest.raises(SourceError): read_canonical(*selector_pair(tmp_path, tail=tail))


def test_canonical_entry_early_return_refuses(tmp_path):
    pair = canonical_pair(tmp_path, "run_validator('alpha', references / 'example.md')")
    mutate(pair[0], 'def main(argv=None):', 'def main(argv=None):\n    if True:\n        return 0')
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize('extra', [
    '\nsys.executable = "bash"\n', '\nsubprocess.run = lambda *a, **k: None\n',
    '\nPath = lambda *a: None\n', '\nfrom elsewhere import subprocess\n',
])
def test_native_launch_vocabulary_cannot_be_replaced(dispatcher, extra):
    with dispatcher.open('a', encoding='utf-8') as handle: handle.write(extra)
    with pytest.raises(SourceError): read_dispatch(dispatcher)


def test_selector_side_effect_is_never_executed(tmp_path):
    marker = tmp_path / 'SIDE-EFFECT'
    pair = selector_pair(tmp_path, SELECTOR.replace('path.is_dir()', 'side_effect()'))
    with pair[1].open('a', encoding='utf-8') as handle:
        handle.write("\ndef side_effect():\n    Path(" + repr(str(marker)) + ").write_text('executed')\n    return True\n")
    with pytest.raises(SourceError): read_canonical(*pair)
    assert not marker.exists()


@pytest.mark.parametrize('extra', ["\nHERE = Path('/wrong')\n", "\ndef HERE(): return None\n"])
def test_selector_here_rebinding_refuses(tmp_path, extra):
    pair = selector_pair(tmp_path)
    with pair[1].open('a', encoding='utf-8') as handle: handle.write(extra)
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize('damage', [None, 'missing-dispatcher', 'invalid-dispatcher', 'unsupported-dispatcher', 'missing-canonical', 'invalid-canonical', 'unsupported-canonical'])
def test_missing_artifact_import_does_not_bypass_source_checks(tmp_path, monkeypatch, damage):
    import schema_coverage
    monkeypatch.setattr(schema_coverage, 'art', None)
    for name in ('validate.py', 'validate_canonical.py'):
        (tmp_path / name).write_bytes((SCRIPTS / name).read_bytes())
    if damage:
        kind, target = damage.split('-')
        path = tmp_path / ('validate.py' if target == 'dispatcher' else 'validate_canonical.py')
        if kind == 'missing': path.unlink()
        elif kind == 'invalid': path.write_text('def broken(', encoding='utf-8')
        elif target == 'dispatcher':
            with path.open('a', encoding='utf-8') as handle: handle.write('\nAGG_VALIDATORS = tuple()\n')
        else:
            with path.open('a', encoding='utf-8') as handle: handle.write('\nrun_canonical = lambda: 0\n')
    code, lines = schema_coverage.run(scripts_dir=tmp_path)
    if damage:
        assert code != 0
        assert 'source-check' in '\n'.join(lines)
    else:
        assert code == 0
        assert lines == ['schema-coverage: PASS (degraded — apodictic_artifacts unavailable)']


@pytest.mark.parametrize('replacement', [
    'if False:\n    from validate_canonical import run_canonical',
    'def unused():\n    from validate_canonical import run_canonical',
])
def test_dead_canonical_import_cannot_prove_entry_wiring(tmp_path, replacement):
    pair = canonical_pair(tmp_path, "run_validator('alpha', references / 'example.md')")
    mutate(pair[0], 'from validate_canonical import run_canonical', replacement)
    with pytest.raises(SourceError): read_canonical(*pair)


def test_dead_native_import_cannot_prove_launcher(tmp_path):
    pair = canonical_pair(tmp_path, "run_validator('alpha', references / 'example.md')")
    mutate(pair[1], 'import subprocess, sys', 'if False:\n    import subprocess, sys')
    with pytest.raises(SourceError): read_canonical(*pair)

# Round 1: actual ordered execution and bindings, not plausible later syntax.
def insert_body(path, name, body):
    source = path.read_text(encoding='utf-8')
    function = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    lines = source.splitlines(keepends=True)
    lines[function.body[0].lineno - 1:function.body[0].lineno - 1] = [textwrap.indent(body + '\n', '    ')]
    path.write_text(''.join(lines), encoding='utf-8')


def live_canonical_pair(tmp_path):
    for name in ('validate.py', 'validate_canonical.py'):
        (tmp_path / name).write_bytes((SCRIPTS / name).read_bytes())
    return tmp_path / 'validate.py', tmp_path / 'validate_canonical.py'


@pytest.mark.parametrize('body', [
    'if True:\n    return 0', 'if unknown:\n    return 0',
    'return 0', 'raise RuntimeError()', 'if True:\n    raise RuntimeError()',
    'script = "wrong.py"', 'args = []', 'del script', 'del args',
    'script, args = "wrong.py", []', 'def script(): return "wrong.py"',
    'from other import value as args',
])
def test_round1_helper_launcher_requires_ordered_unchanged_binding(dispatcher, body):
    insert_body(dispatcher, '_run_helper', body)
    with pytest.raises(SourceError): read_dispatch(dispatcher)
    import meta_lint
    assert meta_lint.check_m1(dispatcher)


@pytest.mark.parametrize('body', [
    'if True:\n    return subprocess.CompletedProcess([], 0, b"", b"")',
    'return subprocess.CompletedProcess([], 0, b"", b"")',
    'if unknown:\n    raise RuntimeError()',
    'command = "wrong-command"', 'arguments = ()', 'del command', 'del arguments',
    'def command(): return "wrong-command"', 'from other import value as arguments',
])
def test_round1_canonical_launcher_requires_ordered_unchanged_binding(tmp_path, body):
    pair = live_canonical_pair(tmp_path)
    insert_body(pair[1], 'run_validator', body)
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize('function', ['_self_test', '_argument_carve', '_self_test_all'])
@pytest.mark.parametrize('body', ['return 0', 'if True:\n    return 0', 'if unknown:\n    return 0', 'raise RuntimeError()', 'if True:\n    raise RuntimeError()'])
def test_round1_no_dead_native_suite_or_aggregate(dispatcher, function, body):
    insert_body(dispatcher, function, body)
    with pytest.raises(SourceError):
        (check_aggregate_count if function == '_self_test_all' else read_dispatch)(dispatcher)


@pytest.mark.parametrize('insertion', [
    ('    for command in AGG_VALIDATORS:', '    return 0\n'),
    ('    for command in AGG_VALIDATORS:', '    if True:\n        return 0\n'),
    ('        if command == "gate-state":', '        continue\n'),
    ('        if command == "gate-state":', '        if True:\n            break\n'),
    ('    if failed:\n        _line(f"Aggregate self-test: FAIL', '    return 0\n'),
])
def test_round1_aggregate_exits_between_proof_sites_refuse(dispatcher, insertion):
    marker, before = insertion
    mutate(dispatcher, marker, before + marker)
    with pytest.raises(SourceError): check_aggregate_count(dispatcher)


@pytest.mark.parametrize('name', ['len', 'bool', 'str', 'map', 'next'])
@pytest.mark.parametrize('binding', [
    'def {name}(value): return value', 'async def {name}(value): return value',
    'class {name}: pass', 'from builtins import repr as {name}',
    'import other as {name}', 'def unused({name}): pass',
    'try:\n    pass\nexcept Exception as {name}:\n    pass',
    'match object():\n    case {name}: pass',
])
def test_round1_builtin_binding_forms_refuse(dispatcher, name, binding):
    with dispatcher.open('a', encoding='utf-8') as handle: handle.write('\n' + binding.format(name=name) + '\n')
    with pytest.raises(SourceError): read_dispatch(dispatcher)


@pytest.mark.parametrize('body', ['return 0', 'if True:\n    return 0', 'if unknown:\n    return 0', 'raise RuntimeError()', 'if True:\n    raise RuntimeError()'])
def test_round1_canonical_entry_exit_cannot_credit_later_sections(tmp_path, body):
    pair = live_canonical_pair(tmp_path)
    insert_body(pair[1], 'run_canonical', body)
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize('body', ['return 0', 'if True:\n    return 0', 'if unknown:\n    return 0', 'raise RuntimeError()', 'if True:\n    raise RuntimeError()'])
def test_round1_section_exit_does_not_supply_later_anchor(tmp_path, body):
    pair = canonical_pair(tmp_path, 'section(references)', body + "\nrun_validator('alpha', references / 'example.md')")
    try: calls = read_canonical(*pair)
    except SourceError: return
    assert not has_example(calls)


@pytest.mark.parametrize('signature', [
    'unused', 'other, references', 'references, other', 'references=None',
    'references, /', '*references', '**references', '*, references',
    'references, *args', 'references, **kwargs', 'references, *, other=None',
])
def test_round1_section_actual_parameter_must_receive_root(tmp_path, signature):
    pair = live_canonical_pair(tmp_path)
    mutate(pair[1], 'def _framework(references):', 'def _framework(' + signature + '):')
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize('argument', ['references=references', '*[references]', 'references, references', '**{"references": references}'])
def test_round1_section_call_argument_shape_refuses(tmp_path, argument):
    pair = live_canonical_pair(tmp_path)
    mutate(pair[1], 'result = _framework(references)', 'result = _framework(' + argument + ')')
    with pytest.raises(SourceError): read_canonical(*pair)


def test_round1_actual_supported_forms_remain_live():
    routes = read_dispatch(SCRIPTS / 'validate.py')
    assert {routes[n].self_test_kind for n in ('contract-hash','contract-check','state-lines')} == {'utility'}
    assert routes['argument-carve-behavior-preservation'].self_test_kind == 'carve'
    check_aggregate_count(SCRIPTS / 'validate.py')
    calls = read_canonical(SCRIPTS / 'validate.py', SCRIPTS / 'validate_canonical.py')
    assert len(calls) == 77
    assert any(c.command == 'pass-header' for c in calls)


@pytest.mark.parametrize('replacement', [
    '    if failed:\n        return 0\n        _line(f"Aggregate self-test: FAIL',
    '    if failed:\n        if True:\n            return 0\n        _line(f"Aggregate self-test: FAIL',
])
def test_round1_summary_cannot_credit_report_after_exit(dispatcher, replacement):
    mutate(dispatcher, '    if failed:\n        _line(f"Aggregate self-test: FAIL', replacement)
    with pytest.raises(SourceError): check_aggregate_count(dispatcher)


def test_round1_no_decorative_total_after_side_effect(dispatcher):
    mutate(dispatcher, 'all {total} validators:', 'all {sys.exit(0)} {total} validators:')
    with pytest.raises(SourceError): check_aggregate_count(dispatcher)


def test_round1_wildcard_import_cannot_supply_builtin_bindings(dispatcher):
    with dispatcher.open('a', encoding='utf-8') as handle: handle.write('\nfrom other import *\n')
    with pytest.raises(SourceError): read_dispatch(dispatcher)


def test_round1_unknown_while_cannot_supply_later_canonical_calls(tmp_path):
    pair = live_canonical_pair(tmp_path)
    insert_body(pair[1], 'run_canonical', 'while True:\n    pass')
    with pytest.raises(SourceError): read_canonical(*pair)


# Round2: the canonical syntax is closed, and all binding sites share the
# same enumerator. These sources are only parsed; their bodies never execute.
@pytest.mark.parametrize('statement', [
    'match True:\n case True:\n  return 0',
    'sys.exit(0)', 'assert False', 'unknown_operation()',
    'if True:\n sys.exit(0)', 'for item in (True,):\n unknown_operation()',
    '_line(sys.exit(0))', 'result = unknown_operation()',
    'with unknown_context():\n pass',
])
@pytest.mark.parametrize('site', ['entry', 'section'])
@pytest.mark.parametrize('position', ['before', 'between'])
def test_round2_unknown_control_cannot_credit_later_anchors(tmp_path, statement, site, position):
    first = "run_validator('beta', references / 'first.md')\n" if position == 'between' else ''
    body = first + statement + "\nrun_validator('alpha', references / 'example.md')"
    pair = canonical_pair(tmp_path, body if site == 'entry' else 'result = section(references)',
                          body if site == 'section' else None)
    with pytest.raises(SourceError):
        read_canonical(*pair)


@pytest.mark.parametrize('mutation', [
    'setattr(subprocess, "run", replacement)', 'delattr(subprocess, "run")',
    'mutator = setattr', 'mutator = delattr',
    'globals()["AGG_VALIDATORS"] = ()', 'del globals()["AGG_VALIDATORS"]',
    'locals()["AGG_VALIDATORS"] = ()', 'del locals()["AGG_VALIDATORS"]',
    'vars()["AGG_VALIDATORS"] = ()', 'del vars()["AGG_VALIDATORS"]',
    'namespace = globals', 'namespace = locals', 'namespace = vars',
    'alias = subprocess', 'consume(subprocess)', 'launch = subprocess.run',
    'subprocess.__dict__["run"] = replacement',
    'alias = sys', 'consume(sys)', 'exit_alias = sys.exit',
    'alias = Path', 'consume(Path)',
    'import subprocess as child_api\nchild_api.run = replacement',
    'import sys as runtime\nruntime.executable = \"wrong\"',
    'from subprocess import run as launch',
    'from pathlib import Path as OtherPath\nOtherPath.resolve = replacement',
    'import pathlib as paths\npaths.Path.resolve = replacement',
    'import importlib\nchild_api = importlib.import_module(\"subprocess\")',
    'from importlib import import_module as load_module',
])
@pytest.mark.parametrize('consumer', ['aggregate', 'dispatch', 'count', 'm1', 'm3'])
def test_round2_protected_mutation_and_escape_refuse(dispatcher, mutation, consumer):
    with dispatcher.open('a', encoding='utf-8') as handle:
        handle.write('\n' + mutation + '\n')
    if consumer in ('m1', 'm3'):
        import meta_lint
        check = meta_lint.check_m1 if consumer == 'm1' else meta_lint.check_m3
        assert check(dispatcher)
    else:
        check = {'aggregate': read_aggregate, 'dispatch': read_dispatch, 'count': check_aggregate_count}[consumer]
        with pytest.raises(SourceError): check(dispatcher)


ROUND2_BINDINGS = [
    '{name} = None', 'del {name}', '{name}: object = None', '({name} := None)',
    'def {name}():\n pass', 'async def {name}():\n pass', 'class {name}:\n pass',
    'import elsewhere as {name}', 'from elsewhere import value as {name}',
    'def other({name}):\n pass',
    'try:\n pass\nexcept Exception as {name}:\n pass',
    'match None:\n case {name}:\n  pass',
    'match []:\n case [*{name}]:\n  pass',
    'match {{}}:\n case {{**{name}}}:\n  pass',
]


@pytest.mark.parametrize('name', ['sys', 'subprocess', 'Path'])
@pytest.mark.parametrize('binding', ROUND2_BINDINGS)
def test_round2_native_names_share_complete_binding_enumerator(dispatcher, name, binding):
    with dispatcher.open('a', encoding='utf-8') as handle:
        handle.write('\n' + binding.format(name=name) + '\n')
    with pytest.raises(SourceError): read_dispatch(dispatcher)
    with pytest.raises(SourceError): check_aggregate_count(dispatcher)


@pytest.mark.parametrize('name', ['HERE', 'references', 'template_references', 'aif_references'])
@pytest.mark.parametrize('binding', ROUND2_BINDINGS)
def test_round2_canonical_roots_share_complete_binding_enumerator(tmp_path, name, binding):
    pair = live_canonical_pair(tmp_path)
    source = pair[1].read_text(encoding='utf-8')
    if name == 'HERE':
        source += '\n' + binding.format(name=name) + '\n'
    else:
        source = source.replace('def run_canonical() -> int:',
                                'def run_canonical() -> int:\n' + textwrap.indent(binding.format(name=name), '    '), 1)
    pair[1].write_text(source, encoding='utf-8')
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize('body', [
    "def unused():\n run_validator('alpha', references / 'example.md')",
    "for x in []:\n run_validator('alpha', references / 'example.md')",
])
def test_round2_unsupported_decoy_forms_refuse(tmp_path, body):
    with pytest.raises(SourceError): read_canonical(*canonical_pair(tmp_path, body))


@pytest.mark.parametrize('site', ['entry', 'section'])
def test_round2_unknown_call_never_executes_marker(tmp_path, site):
    body = "unknown_operation()\nrun_validator('alpha', references / 'example.md')"
    pair = canonical_pair(tmp_path, body if site == 'entry' else 'section(references)',
                          body if site == 'section' else None)
    marker = tmp_path / 'MUST-NOT-EXIST'
    with pair[1].open('a', encoding='utf-8') as handle:
        handle.write('\ndef unknown_operation():\n    Path(' + repr(str(marker)) + ").write_text('executed')\n")
    with pytest.raises(SourceError): read_canonical(*pair)
    assert not marker.exists()


@pytest.mark.parametrize('mutation', [
    'setattr(subprocess, "run", replacement)', 'delattr(subprocess, "run")',
    'globals()["run_validator"] = replacement', 'del locals()["HERE"]',
    'alias = subprocess', 'alias = subprocess.run', 'alias = Path',
    'namespace = vars', 'import builtins\nnamespace = builtins.globals',
    'from builtins import globals as namespace',
    'import subprocess as child_api\nchild_api.run = replacement',
    'from pathlib import Path as OtherPath\nOtherPath.resolve = replacement',
    'import importlib\nchild_api = importlib.import_module(\"subprocess\")',
])
def test_round2_canonical_mutation_refusal(tmp_path, mutation):
    pair = live_canonical_pair(tmp_path)
    with pair[1].open('a', encoding='utf-8') as handle:
        handle.write('\n' + mutation + '\n')
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize('wrapper', ['bool(section(references))', '_line(section(references))',
                                     'next((section(references) for item in (True,)))'])
def test_round2_nested_section_cannot_hide_control(tmp_path, wrapper):
    pair = canonical_pair(tmp_path, wrapper + "\nrun_validator('alpha', references / 'example.md')",
                          'sys.exit(0)')
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize('mutation', [
    'from builtins import __dict__ as namespace',
    'namespace = unrelated.__globals__',
    'import builtins\nnamespace = builtins.globals',
    'from builtins import globals as namespace',
])
def test_round2_reflective_namespace_aliases_refuse(dispatcher, mutation):
    with dispatcher.open('a', encoding='utf-8') as handle:
        handle.write('\n' + mutation + '\n')
    with pytest.raises(SourceError): read_aggregate(dispatcher)
    with pytest.raises(SourceError): read_dispatch(dispatcher)
    with pytest.raises(SourceError): check_aggregate_count(dispatcher)


@pytest.mark.parametrize('write', [
    "P += '/wrong.md'", "P, other = references / 'wrong.md', 0",
    "del P", "for P in ():\n pass",
    "if condition:\n P = references / 'wrong.md'",
])
def test_round2_all_binding_forms_invalidate_one_hop_paths(tmp_path, write):
    body = "P = references / 'example.md'\n" + write + "\nrun_validator('alpha', P)"
    pair = canonical_pair(tmp_path, 'result = section(references)', body)
    assert not has_example(read_canonical(*pair))


@pytest.mark.parametrize('suffix', ['True', 'unexpected=True'])
def test_round2_existence_guard_rejects_unproven_call_arguments(tmp_path, suffix):
    body = "if (references / 'example.md').is_file(" + suffix + "):\n run_validator('alpha', references / 'example.md')"
    with pytest.raises(SourceError): read_canonical(*canonical_pair(tmp_path, body))


@pytest.mark.parametrize('body', [
    "run_validator('alpha', references / 'example.md', unexpected=True)",
    "if run_validator('alpha', references / 'example.md', unexpected=True).returncode == 0:\n print('done')",
])
def test_round2_canonical_validator_keywords_cannot_supply_proof(tmp_path, body):
    with pytest.raises(SourceError): read_canonical(*canonical_pair(tmp_path, body))


@pytest.mark.parametrize('name', ['_run_helper', '_override_companion', '_argument_carve',
                                  'frozenset', '_navigation_scan', '_self_test', '_helper'])
def test_round2_equivalent_native_call_keywords_refuse(dispatcher, name):
    tree = ast.parse(dispatcher.read_text(encoding='utf-8'))
    scope = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == '_helper') if name == '_run_helper' else tree
    call = next(node for node in ast.walk(scope) if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name) and node.func.id == name)
    call.keywords.append(ast.keyword(arg='unexpected', value=ast.Constant(True)))
    dispatcher.write_text(ast.unparse(tree), encoding='utf-8')
    with pytest.raises(SourceError): read_dispatch(dispatcher)


@pytest.mark.parametrize('expression', ['run_canonical(unexpected=True)', 'run_canonical(1)'])
def test_round2_returned_canonical_entry_call_shape_refuses(tmp_path, expression):
    pair = canonical_pair(tmp_path, "run_validator('alpha', references / 'example.md')")
    source = pair[0].read_text(encoding='utf-8').replace('result = run_canonical()', 'return ' + expression)
    pair[0].write_text(source, encoding='utf-8')
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize('expression', ['bool(args, unexpected=True)', 'len(args, unexpected=True)'])
def test_round2_route_predicate_keywords_refuse(tmp_path, expression):
    pair = canonical_pair(tmp_path, "run_validator('alpha', references / 'example.md')")
    source = pair[0].read_text(encoding='utf-8').replace('if args and', 'if ' + expression + ' and')
    pair[0].write_text(source, encoding='utf-8')
    with pytest.raises(SourceError): read_canonical(*pair)

# Round3 boundaries: these variants are parsed only. The marker operand is never
# imported or executed, including when it appears in a definition-time context.
def round3_consumer(name, dispatcher, canonical):
    if name == 'aggregate': return read_aggregate(dispatcher)
    if name == 'dispatch': return read_dispatch(dispatcher)
    if name == 'count': return check_aggregate_count(dispatcher)
    return read_canonical(dispatcher, canonical)


@pytest.mark.parametrize('consumer', ['aggregate', 'dispatch', 'count', 'canonical'])
@pytest.mark.parametrize(('before', 'after'), [
    ('if __name__ == "__main__":', 'sys.exit(0)\nif __name__ == "__main__":'),
    ('if __name__ == "__main__":', 'if False:'),
    ('sys.exit(main())', 'sys.exit(0)'),
    ('sys.exit(main())', 'sys.exit(main(unexpected=True))'),
    ('def main(argv=None):', 'def main(argv):'),
    ('def main(argv=None):', 'def main(argv, extra=None):'),
    ('def main(argv=None):', 'def main(argv: sys.exit(0)=None):'),
    ('def main(argv=None):', 'def main(argv=sys.exit(0)):'),
    ('def main(argv=None):', 'def main(argv=None) -> sys.exit(0):'),
    ('def _helper(command, args):', '@sys.exit(0)\ndef _helper(command, args):'),
    ('def _helper(command, args):', 'def _helper(command: sys.exit(0), args):'),
    ('def _helper(command, args):', 'def _helper(command, args=sys.exit(0)):'),
    ('def _helper(command, args):', 'def _helper(command, args) -> sys.exit(0):'),
    ('import hashlib', 'import hashlib\nassert False'),
    ('import hashlib', 'import hashlib\nwhile True: pass'),
    ('import hashlib', 'import hashlib\ntry:\n    sys.exit(0)\nexcept: pass'),
])
def test_round3_dispatcher_initialization_and_entry_refuse(dispatcher, consumer, before, after):
    mutate(dispatcher, before, after)
    with pytest.raises(SourceError):
        round3_consumer(consumer, dispatcher, SCRIPTS / 'validate_canonical.py')


@pytest.mark.parametrize('target', ['dispatcher', 'canonical'])
@pytest.mark.parametrize('definition', [
    'def unused(value=MARKER): pass', 'def unused(value: MARKER): pass',
    'def unused() -> MARKER: pass', '@MARKER\ndef unused(): pass',
    'def unused():\n def nested(value=MARKER): pass',
    'class Unused(MARKER): pass', 'MARKER',
])
def test_round3_definition_time_operands_never_execute(tmp_path, target, definition):
    pair = canonical_pair(tmp_path, "run_validator('alpha', references / 'example.md')")
    marker = tmp_path / 'must-not-exist'
    source = definition.replace('MARKER', f"Path({str(marker)!r}).touch()")
    path = pair[0 if target == 'dispatcher' else 1]
    old = path.read_text(encoding='utf-8')
    if target == 'dispatcher': old = old.replace("if __name__ == '__main__':", source + "\nif __name__ == '__main__':")
    else: old += '\n' + source + '\n'
    path.write_text(old, encoding='utf-8')
    with pytest.raises(SourceError): read_canonical(*pair)
    assert not marker.exists()


@pytest.mark.parametrize(('before', 'after'), [
    ('def run_canonical() -> int:', 'def run_canonical() -> sys.exit(0):'),
    ('def run_validator(command, *arguments)', 'def run_validator(command=sys.exit(0), *arguments)'),
    ('def _line(text=""):', 'def _line(text=sys.exit(0)):'),
    ('@contextmanager', '@sys.exit(0)'),
    ('class CanonicalAbort(SystemExit):', 'class CanonicalAbort(sys.exit(0)):'),
    ('HERE = Path(__file__).resolve().parent', 'HERE = Path(__file__).resolve().parent\nsys.exit(0)'),
])
def test_round3_canonical_initialization_refuses(tmp_path, before, after):
    canonical = tmp_path / 'validate_canonical.py'
    canonical.write_text((SCRIPTS / 'validate_canonical.py').read_text(encoding='utf-8'), encoding='utf-8')
    mutate(canonical, before, after)
    with pytest.raises(SourceError): read_canonical(SCRIPTS / 'validate.py', canonical)


@pytest.mark.parametrize('site', ['dispatcher', 'entry', 'section'])
@pytest.mark.parametrize('expression', [
    '_line(sys.exit(0))', '_line(print(unexpected=True))',
    '_line(int())', '_line(bool(1, 2))', '_line(next())',
    '_line(Path())', '_line(Path("x", unexpected=True))',
    '_line(*["message"])', '_line(**{"text": "message"})',
    '_line("message", unexpected=True)', '_line("one", "two")',
    'print(unexpected=True)', 'print(**{"end": ""})',
    'print(int(unexpected=True))', 'print(Path("x").is_file(True))',
    'print((lambda: 0)())',
])
def test_round3_ignored_report_call_shape_refuses(tmp_path, site, expression):
    if site == 'dispatcher':
        pair = canonical_pair(tmp_path, "run_validator('alpha', references / 'example.md')")
        mutate(pair[0], '        result = run_canonical()', '        ' + expression + '\n        result = run_canonical()')
    elif site == 'entry':
        pair = canonical_pair(tmp_path, expression + "\nrun_validator('alpha', references / 'example.md')")
    else:
        pair = canonical_pair(tmp_path, 'result = section(references)', expression + "\nrun_validator('alpha', references / 'example.md')")
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize('consumer', ['aggregate', 'dispatch', 'count', 'canonical'])
@pytest.mark.parametrize('extra', [
    'import builtins\nbuiltins.str = lambda value: "wrong.py"',
    'import builtins as replacement\nreplacement.str = str',
    'from builtins import str as render',
    'import builtins\nnamespace = builtins',
    'from private_shadow import *',
    'def unused():\n from private_shadow import *',
    'def unused():\n import builtins\n builtins.str = str',
    'def unused():\n from builtins import str',
])
def test_round3_builtin_module_and_wildcards_all_consumers(dispatcher, consumer, extra):
    mutate(dispatcher, 'if __name__ == "__main__":', extra + '\nif __name__ == "__main__":')
    with pytest.raises(SourceError): round3_consumer(consumer, dispatcher, SCRIPTS / 'validate_canonical.py')


@pytest.mark.parametrize('extra', [
    'import builtins\nbuiltins.str = lambda value: "wrong.py"',
    'from private_shadow import *',
    'def unused():\n import builtins as replacement\n namespace = replacement',
])
def test_round3_canonical_builtin_module_and_wildcards(tmp_path, extra):
    pair = canonical_pair(tmp_path, "run_validator('alpha', references / 'example.md')")
    with pair[1].open('a', encoding='utf-8') as stream: stream.write('\n' + extra + '\n')
    with pytest.raises(SourceError): read_canonical(*pair)


def test_round3_actual_modules_keep_legitimate_definition_time_forms():
    assert len(read_aggregate(SCRIPTS / 'validate.py')) == 84
    assert len(read_dispatch(SCRIPTS / 'validate.py')) == 85
    check_aggregate_count(SCRIPTS / 'validate.py')
    assert len(read_canonical(SCRIPTS / 'validate.py', SCRIPTS / 'validate_canonical.py')) == 77


@pytest.mark.parametrize('body', [
    "print('message')\nrun_validator('alpha', references / 'example.md')",
    "print(f'checking {references}')\nrun_validator('alpha', references / 'example.md')",
])
def test_round3_harmless_reporting_keeps_anchor(tmp_path, body):
    assert has_example(read_canonical(*canonical_pair(tmp_path, body)))


@pytest.mark.parametrize('mutation', ['missing', 'noop', 'required'])
def test_round3_hermetic_public_guard_is_required(tmp_path, mutation):
    pair = canonical_pair(tmp_path, "run_validator('alpha', references / 'example.md')")
    assert has_example(read_canonical(*pair))
    if mutation == 'missing': mutate(pair[0], "if __name__ == '__main__':\n    sys.exit(main())", '')
    elif mutation == 'noop': mutate(pair[0], 'sys.exit(main())', 'sys.exit(0)')
    else: mutate(pair[0], 'def main(argv=None):', 'def main(argv):')
    with pytest.raises(SourceError): read_canonical(*pair)


# Interpreter-provided bindings participate in the same negative binding check
# as explicit imports. Put sibling forms inside an unused function so a module
# statement refusal alone cannot hide a missing shadow/write check.
@pytest.mark.parametrize('target', ['dispatcher', 'canonical'])
@pytest.mark.parametrize('name', ['__name__', '__file__', '__builtins__'])
@pytest.mark.parametrize('binding', ROUND2_BINDINGS + [
    '{name} += 1', '{name}: object',
    'for {name} in []:\n pass', 'with open("unused") as {name}:\n pass',
    '[None for {name} in []]', 'def other(*{name}):\n pass',
    'def other(**{name}):\n pass',
])
def test_round4_implicit_bindings_all_supported_axes(tmp_path, target, name, binding):
    pair = live_canonical_pair(tmp_path)
    path = pair[0 if target == 'dispatcher' else 1]
    extra = 'def unused():\n' + textwrap.indent(binding.format(name=name), '    ') + '\n'
    if target == 'dispatcher':
        mutate(path, 'if __name__ == "__main__":', extra + '\nif __name__ == "__main__":')
        for consumer in ('aggregate', 'dispatch', 'count', 'canonical'):
            with pytest.raises(SourceError): round3_consumer(consumer, *pair)
    else:
        with path.open('a', encoding='utf-8') as stream: stream.write('\n' + extra)
        with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize(('target', 'before', 'extra'), [
    ('dispatcher', 'if __name__ == "__main__":', "__name__ = 'not_main'"),
    ('dispatcher', 'if __name__ == "__main__":', 'def __name__(): pass'),
    ('dispatcher', 'AGG_VALIDATORS = (', '__builtins__ = None'),
    ('dispatcher', 'if __name__ == "__main__":', "__file__ = 'alternate/validate.py'"),
    ('canonical', 'HERE = Path(__file__).resolve().parent', "__file__ = 'alternate/validate_canonical.py'"),
])
def test_round4_exact_implicit_binding_reproductions(tmp_path, target, before, extra):
    pair = live_canonical_pair(tmp_path)
    assert read_dispatch(pair[0])['ledger-check'].helper_files == ('letter_checks.py',)
    assert read_canonical(*pair)
    path = pair[0 if target == 'dispatcher' else 1]
    mutate(path, before, extra + '\n' + before)
    consumers = ('aggregate', 'dispatch', 'count', 'canonical') if target == 'dispatcher' else ('canonical',)
    for consumer in consumers:
        with pytest.raises(SourceError): round3_consumer(consumer, *pair)


ROUND4_IMPORT_USES = [
    ('from pathlib import Path', 'Path', 'HERE = Path(__file__).resolve().parent'),
    ('import subprocess', 'subprocess', 'def run_validator(command, *arguments)'),
    ('from contextlib import contextmanager', 'contextmanager', '@contextmanager'),
]


@pytest.mark.parametrize(('declaration', 'name', 'use'), ROUND4_IMPORT_USES)
@pytest.mark.parametrize('damage', ['missing', 'late', 'local', 'alias', 'wrong-module'])
def test_round4_module_time_import_requires_prior_actual_binding(tmp_path, declaration, name, use, damage):
    pair = live_canonical_pair(tmp_path)
    source = pair[1].read_text(encoding='utf-8')
    assert declaration + '\n' in source and use in source
    replacement = ''
    if damage == 'alias': replacement = declaration + ' as unused_import\n'
    if damage == 'wrong-module': replacement = 'from json import ' + name + '\n'
    source = source.replace(declaration + '\n', replacement, 1)
    if damage == 'late': source += '\n' + declaration + '\n'
    if damage == 'local': source += '\ndef unused():\n    ' + declaration + '\n'
    pair[1].write_text(source, encoding='utf-8')
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize('name', ['Path', 'subprocess', 'contextmanager', 'bytes', 'int', 'SystemExit'])
@pytest.mark.parametrize('binding', ROUND2_BINDINGS)
def test_round4_definition_dependencies_cannot_be_shadowed(tmp_path, name, binding):
    pair = live_canonical_pair(tmp_path)
    # Literal defaults need no name; the supported annotation/base/decorator
    # operands do. Even an otherwise ignored nested binding invalidates them.
    with pair[1].open('a', encoding='utf-8') as stream:
        stream.write('\ndef unused():\n' + textwrap.indent(binding.format(name=name), '    ') + '\n')
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize(('declaration', 'name', 'use'), ROUND4_IMPORT_USES)
def test_round4_import_immediately_before_use_and_local_function_imports_remain_valid(tmp_path, declaration, name, use):
    pair = live_canonical_pair(tmp_path)
    source = pair[1].read_text(encoding='utf-8')
    source = source.replace(declaration + '\n', '', 1)
    source = source.replace(use, declaration + '\n' + use, 1)
    source += '\ndef unused():\n    import json\n    from annotation_manifest import normalize_snapshot\n'
    pair[1].write_text(source, encoding='utf-8')
    # Canonical remains importable source: no public main guard is required.
    assert len(read_canonical(*pair)) == len(read_canonical(SCRIPTS / 'validate.py', SCRIPTS / 'validate_canonical.py'))


@pytest.mark.parametrize('target', ['dispatcher', 'canonical'])
@pytest.mark.parametrize('extra', [
    'EXTRA = ()\ndef EXTRA(): pass\nCOMPOSED = (*EXTRA,)',
    'EXTRA = 1\nCOMPOSED = (*EXTRA,)',
    'COMPOSED = (*EXTRA,)',
    'COMPOSED = (*EXTRA,)\nEXTRA = ()',
    'EXTRA = ()\nEXTRA = 1\nCOMPOSED = (*EXTRA,)',
    'EXTRA = ()\nCOMPOSED = (*EXTRA,)\nEXTRA = ()',
    'EXTRA = ()\ndef unused(EXTRA): pass\nCOMPOSED = (*EXTRA,)',
    'EXTRA = ()\ndef unused():\n from json import dumps as EXTRA\nCOMPOSED = (*EXTRA,)',
    'EXTRA = ()\ndef unused():\n del EXTRA\nCOMPOSED = (*EXTRA,)',
    'EXTRA = ()\ndef unused():\n EXTRA += ()\nCOMPOSED = (*EXTRA,)',
    'EXTRA = ()\ndef unused():\n (EXTRA := ())\nCOMPOSED = (*EXTRA,)',
    'EXTRA = ()\ndef unused():\n try: pass\n except Exception as EXTRA: pass\nCOMPOSED = (*EXTRA,)',
    'EXTRA = ()\ndef unused():\n match []:\n  case [*EXTRA]: pass\nCOMPOSED = (*EXTRA,)',
    'COMPOSED = frozenset(1)',
    'COMPOSED = frozenset(([1],))',
    'EXTRA = ([1],)\nCOMPOSED = frozenset((*EXTRA,))',
    'EXTRA = ([1],)\nCOMPOSED = {*EXTRA}',
    'COMPOSED = {[1]}',
    'COMPOSED = {(1, []): 1}',
    'EXTRA = [1]\nCOMPOSED = {(*EXTRA, []): 1}',
])
def test_round4_module_literal_composition_requires_established_iterable(tmp_path, target, extra):
    pair = live_canonical_pair(tmp_path)
    if target == 'dispatcher':
        mutate(pair[0], 'if __name__ == "__main__":', extra + '\nif __name__ == "__main__":')
        consumers = ('aggregate', 'dispatch', 'count', 'canonical')
    else:
        with pair[1].open('a', encoding='utf-8') as stream: stream.write('\n' + extra + '\n')
        consumers = ('canonical',)
    for consumer in consumers:
        with pytest.raises(SourceError): round3_consumer(consumer, *pair)


@pytest.mark.parametrize('extra', [
    "EXTRA = ('one',)\nCOMPOSED = (*EXTRA,)",
    "EXTRA = ['one']\nCOMPOSED = frozenset((*EXTRA,))",
    "EXTRA = {'one': []}\nCOMPOSED = frozenset((*EXTRA,))",
    "EXTRA = {'one'}\nCOMPOSED = frozenset((*EXTRA,))",
    "EXTRA = 'one'\nCOMPOSED = (*EXTRA,)",
    "EXTRA = b'one'\nCOMPOSED = frozenset((*EXTRA,))",
    'EXTRA = ([1],)\nCOMPOSED = (*EXTRA,)',
    'COMPOSED = {(1, 2): [1]}',
])
def test_round4_valid_literal_compositions_and_unrelated_local_data(tmp_path, extra):
    pair = live_canonical_pair(tmp_path)
    # Local data is outside this module-initialization proof.
    extra += '\ndef unused():\n    local_data = {key: value}\n'
    # Dispatcher dictionaries are command tables. Canonical module data tests
    # initialization without introducing a new, unhandled public command.
    with pair[1].open('a', encoding='utf-8') as stream: stream.write('\n' + extra)
    assert len(read_aggregate(pair[0])) == 84
    assert len(read_dispatch(pair[0])) == 85
    check_aggregate_count(pair[0])
    assert len(read_canonical(*pair)) == 77
    # Execute only these known benign controls in a separate disposable child;
    # the hostile inspected sources above remain data throughout.
    helper = tmp_path / 'letter_checks.py'
    helper.write_text("from pathlib import Path\nPath(__file__).with_suffix('.called').write_text('called')\nraise SystemExit(9)\n", encoding='utf-8')
    result = subprocess.run([sys.executable, '-B', '-c',
        "import sys; import validate_canonical as c; sys.exit(c.run_validator('ledger-check', '--self-test').returncode)"],
        cwd=tmp_path, capture_output=True, timeout=15)
    assert result.returncode == 9 and result.stdout == result.stderr == b''
    assert helper.with_suffix('.called').read_text() == 'called'


def round5_environment_pair(tmp_path):
    pair = canonical_pair(tmp_path, "run_validator('alpha', references / 'example.md')")
    mutate(pair[1], 'import subprocess, sys', 'import subprocess, sys\nimport os')
    mutate(pair[1], 'command, *arguments])',
           'command, *arguments], env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"))')
    return pair


@pytest.mark.parametrize('declaration', ['', 'import os as os', 'from json import os',
                                         'def unused():\n    import os', 'import os\nimport os'])
def test_round5_environment_dependency_requires_one_actual_module_import(tmp_path, declaration):
    pair = round5_environment_pair(tmp_path)
    mutate(pair[1], 'import os\n', declaration + '\n')
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize('binding', ROUND2_BINDINGS + [
    '{name} += 1', '{name}: object', 'for {name} in []:\n pass',
    'with open("unused") as {name}:\n pass', '[None for {name} in []]',
    'def other(*{name}):\n pass', 'def other(**{name}):\n pass',
])
def test_round5_environment_dependency_rejects_binding_siblings(tmp_path, binding):
    pair = round5_environment_pair(tmp_path)
    # One small supported program covers binding forms, without multiplying
    # every complete dispatcher/canonical source by every consumer.
    with pair[1].open('a', encoding='utf-8') as stream:
        stream.write('\ndef unused():\n' + textwrap.indent(binding.format(name='os'), '    ') + '\n')
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize('statement', [
    'alias = os\nalias.environ = None', 'consume(os)',
    'environment = os.environ\nenvironment["PYTHONHOME"] = "missing-home"',
    'consume(os.environ)', 'os.environ = None', 'del os.environ',
    'os.environ["PYTHONHOME"] = "missing-home"', 'del os.environ["PATH"]',
    'os.environ.update({"PYTHONHOME": "missing-home"})', 'environment = os.environ.copy()',
    'paths = os.path\npaths.join = replacement', 'consume(os.path)',
    'join = os.path.join', 'consume(os.path.isfile)',
    'os.path = None', 'del os.path', 'os.path.join = replacement', 'del os.path.isfile',
    'os.name = "other"', 'del os.name', 'os.chdir("missing-directory")',
    'import os as alias\nalias.environ = None', 'import os.path as paths',
    'from os import environ as environment', 'from os.path import join',
    'setattr(os, "environ", None)', 'os.__dict__["environ"] = None',
    'kind = subprocess.CompletedProcess',
])
def test_round5_native_object_capabilities_cannot_escape_through_uninspected_helpers(tmp_path, statement):
    pair = round5_environment_pair(tmp_path)
    # The unused helper supplies no anchor. It isolates the shared negative
    # object check from the narrower canonical entry statement grammar.
    with pair[1].open('a', encoding='utf-8') as stream:
        stream.write('\ndef unused():\n' + textwrap.indent(statement, '    ') + '\n')
    with pytest.raises(SourceError): read_canonical(*pair)


@pytest.mark.parametrize(('target', 'damage'), [
    ('dispatcher', 'missing'), ('dispatcher', 'rebound'),
    ('canonical', 'missing'), ('canonical', 'rebound'),
    ('canonical', 'entry-environment'), ('canonical', 'entry-object-alias'),
    ('canonical', 'entry-environment-alias'),
])
def test_round5_actual_launch_and_consumer_adoption(tmp_path, monkeypatch, target, damage):
    import meta_lint
    import schema_coverage
    pair = live_canonical_pair(tmp_path)
    path = pair[0 if target == 'dispatcher' else 1]
    if damage == 'missing':
        mutate(path, 'import os\n', '')
    elif damage == 'rebound':
        if target == 'dispatcher':
            mutate(path, 'if __name__ == "__main__":', 'os = None\nif __name__ == "__main__":')
        else:
            with path.open('a', encoding='utf-8') as stream: stream.write('\nos = None\n')
    else:
        insert_body(path, 'run_canonical', {
            'entry-environment': 'os.environ = None',
            'entry-object-alias': 'alias = os\nalias.environ = None',
            'entry-environment-alias': 'environment = os.environ\nenvironment["PYTHONHOME"] = "missing-home"',
        }[damage])
    if target == 'dispatcher':
        with pytest.raises(SourceError): read_dispatch(pair[0])
        with pytest.raises(SourceError): check_aggregate_count(pair[0])
        assert meta_lint.check_m1(pair[0]) and meta_lint.check_m3(pair[0])
        # These inspect separate data; missing launcher dependencies alone do
        # not turn inventory extraction or canonical-only association into a
        # proof of dispatcher launch execution.
        assert len(read_aggregate(pair[0])) == 84
        assert len(read_canonical(*pair)) == 77
    else:
        assert read_dispatch(pair[0])['ledger-check'].helper_files == ('letter_checks.py',)
        with pytest.raises(SourceError): read_canonical(*pair)
    monkeypatch.setattr(schema_coverage, 'art', None)
    code, lines = schema_coverage.run(scripts_dir=tmp_path)
    assert code == 1 and 'source-check' in '\n'.join(lines)


def test_round5_shared_escape_refusal_reaches_inventory_and_meta(tmp_path, monkeypatch, capsys):
    import meta_lint
    import validator_runner
    scripts = tmp_path / 'scripts'
    scripts.mkdir()
    pair = live_canonical_pair(scripts)
    schemas = tmp_path / 'schemas'
    schemas.mkdir()
    (schemas / 'validator-runtime-inventory.json').write_bytes(
        (SCRIPTS.parent / 'schemas/validator-runtime-inventory.json').read_bytes())
    monkeypatch.setattr(validator_runner, 'HERE', scripts)
    monkeypatch.setattr(sys, 'path', list(sys.path))
    assert validator_runner.check_inventory() == 0
    capsys.readouterr()
    mutate(pair[0], 'if __name__ == "__main__":',
           'def unused():\n    alias = os\n    alias.environ = None\nif __name__ == "__main__":')
    for consumer in ('aggregate', 'dispatch', 'count', 'canonical'):
        with pytest.raises(SourceError): round3_consumer(consumer, *pair)
    assert meta_lint.check_m1(pair[0]) and meta_lint.check_m3(pair[0])
    assert validator_runner.check_inventory() == 1
    assert 'Inventory source-check error:' in capsys.readouterr().out


def test_round5_environment_replacement_operand_is_never_executed(tmp_path):
    pair = round5_environment_pair(tmp_path)
    marker = tmp_path / 'must-not-exist'
    insert_body(pair[1], 'run_canonical', f'os.environ = Path({str(marker)!r}).touch()')
    with pytest.raises(SourceError): read_canonical(*pair)
    assert not marker.exists()


def test_round5_minimal_launch_and_environment_copy_remain_supported(tmp_path):
    # No unconditional dependency on os for the minimal accepted launch form.
    assert has_example(read_canonical(*canonical_pair(tmp_path, "run_validator('alpha', references / 'example.md')")))
    pair = round5_environment_pair(tmp_path)
    with pair[1].open('a', encoding='utf-8') as stream:
        stream.write('\ndef unused():\n'
                     '    environment = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")\n'
                     '    environment["EXAMPLE"] = "local copy only"\n'
                     '    platform = os.name\n')
    assert has_example(read_canonical(*pair))


@pytest.mark.parametrize(('target', 'imports'), [
    ('dispatcher', ('import os', 'import sys', 'import subprocess', 'from pathlib import Path')),
    ('canonical', ('import os', 'import sys')),
])
def test_round5_late_runtime_imports_retain_real_helper_execution(tmp_path, target, imports):
    pair = live_canonical_pair(tmp_path)
    path = pair[0 if target == 'dispatcher' else 1]
    source = path.read_text(encoding='utf-8')
    for declaration in imports:
        assert declaration + '\n' in source
        source = source.replace(declaration + '\n', '', 1)
    late = '\n'.join(imports) + '\n'
    if target == 'dispatcher': source = source.replace('if __name__ == "__main__":', late + '\nif __name__ == "__main__":', 1)
    else: source += '\n' + late
    path.write_text(source, encoding='utf-8')
    assert read_dispatch(pair[0])['ledger-check'].helper_files == ('letter_checks.py',)
    check_aggregate_count(pair[0])
    assert len(read_canonical(*pair)) == 77
    helper = tmp_path / 'letter_checks.py'
    helper.write_text("from pathlib import Path\nPath(__file__).with_suffix('.called').write_text('called')\nraise SystemExit(9)\n", encoding='utf-8')
    # Only this known benign control is executed, in its own disposable child.
    command = ([str(pair[0]), 'ledger-check', '--self-test'] if target == 'dispatcher' else
               ['-c', "import sys; import validate_canonical as c; sys.exit(c.run_validator('ledger-check', '--self-test').returncode)"])
    result = subprocess.run([sys.executable, '-B', *command], cwd=tmp_path, capture_output=True, timeout=15)
    assert result.returncode == 9 and result.stdout == result.stderr == b''
    assert helper.with_suffix('.called').read_text() == 'called'
