"""Finite, nonexecuting readers for native validator source guarantees.

These checks establish literal routing and canonical-call associations, not the
semantic correctness of a validator. Unsupported binding syntax fails closed.
"""
import ast
from dataclasses import dataclass
from pathlib import Path
import re


class SourceError(ValueError):
    def __init__(self, path, message, line=None):
        super().__init__(f"{path}{':' + str(line) if line else ''}: {message}")


@dataclass(frozen=True)
class CommandRoute:
    helper_files: tuple
    self_test_kind: str


@dataclass(frozen=True)
class CanonicalCall:
    command: str
    reference_paths: tuple
    line: int


def _name(node, name):
    return isinstance(node, ast.Name) and node.id == name


def _call(node, name):
    return isinstance(node, ast.Call) and _name(node.func, name)


def _same(node, source):
    return ast.dump(node) == ast.dump(ast.parse(source, mode='eval').body)


def _parse(path):
    try:
        return ast.parse(Path(path).read_text(encoding='utf-8'), filename=str(path))
    except (OSError, UnicodeError, SyntaxError, ValueError) as exc:
        raise SourceError(path, f"unavailable or invalid Python source: {exc}") from None


def _literal(node, path):
    if isinstance(node, ast.Dict):
        keys = [_literal(k, path) for k in node.keys]
        if any(not isinstance(k, str) or not k for k in keys) or len(set(keys)) != len(keys):
            raise SourceError(path, 'duplicate, empty or non-string dictionary key', node.lineno)
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError):
        raise SourceError(path, 'unsupported dynamic literal', getattr(node, 'lineno', None)) from None


def _bound_name(node):
    """Python 3.10 binding forms; used only to reject replacement/shadowing."""
    if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
        return node.id
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return node.name
    if isinstance(node, ast.alias):
        return node.asname or node.name.split('.')[0]
    if isinstance(node, ast.arg):
        return node.arg
    if isinstance(node, (ast.ExceptHandler, ast.MatchAs, ast.MatchStar)):
        return node.name
    if isinstance(node, ast.MatchMapping):
        return node.rest
    return None


def _body(function):
    body = function.body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        return body[1:]
    return body


def _expect_body(body, source, path, label):
    """One closed statement form, not an interpreter or a source-derived oracle."""
    expected = ast.parse(source).body
    if [ast.dump(n) for n in body] != [ast.dump(n) for n in expected]:
        raise SourceError(path, label + ': unsupported ordered statement form')


def _signature(function, names, path, *, vararg=None, helper_input=False):
    args = function.args
    if (args.posonlyargs or [a.arg for a in args.args] != list(names) or args.defaults
            or args.kwarg or (args.vararg.arg if args.vararg else None) != vararg):
        raise SourceError(path, function.name + ': unsupported parameter binding')
    if args.kwonlyargs:
        if not (helper_input and [a.arg for a in args.kwonlyargs] == ['input']
                and len(args.kw_defaults) == 1 and _same(args.kw_defaults[0], 'None')):
            raise SourceError(path, function.name + ': unsupported keyword parameters')
    elif args.kw_defaults:
        raise SourceError(path, function.name + ': unsupported keyword defaults')
    for name in (*names, *((vararg,) if vararg else ())):
        bindings = [n for n in ast.walk(function) if _bound_name(n) == name]
        if len(bindings) != 1 or not isinstance(bindings[0], ast.arg):
            raise SourceError(path, function.name + ': parameter rebound or shadowed: ' + name)


def _bindings(tree, path, names):
    """Reject rebinding, item mutation and alias escape of the protected names.

    The AST walk here only finds prohibited writes/uses. It never credits a call
    or a literal as evidence that a runtime path executes.
    """
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    for name in names:
        definitions = [node for node in ast.walk(tree) if _bound_name(node) == name]
        if len(definitions) != 1:
            raise SourceError(path, f'{name}: missing or rebound definition')
        definition = definitions[0]
        parent = parents.get(definition)
        if isinstance(definition, ast.Name):
            if not isinstance(parent, ast.Assign) or len(parent.targets) != 1 or parents.get(parent) is not tree:
                raise SourceError(path, f'{name}: requires one simple top-level assignment')
        elif isinstance(definition, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if parent is not tree or definition.decorator_list:
                raise SourceError(path, f'{name}: requires undecorated top-level function')
        for node in ast.walk(tree):
            if not _name(node, name) or not isinstance(node.ctx, ast.Load):
                continue
            parent = parents.get(node)
            if isinstance(parent, ast.Subscript) and parent.value is node:
                if isinstance(parent.ctx, (ast.Store, ast.Del)):
                    raise SourceError(path, f'{name}: item mutation', node.lineno)
                continue
            if isinstance(parent, ast.Call) and parent.func is node:
                continue
            if isinstance(parent, ast.Compare) or isinstance(parent, (ast.For, ast.Starred)):
                continue
            if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name) and parent.func.id in ('len', 'tuple', 'frozenset'):
                continue
            # Imported canonical callable is allowed only as a direct call.
            raise SourceError(path, f'{name}: unsupported alias or use', node.lineno)


def _protected_objects(tree, path):
    """Negative capability/escape check, shared by every source-proof entry.

    The inspected programs do not use dynamic namespace or reflective mutation
    facilities. Refuse the capability itself, including an alias to it; never
    evaluate a namespace, replacement object, or callable.
    """
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    capabilities = {'globals', 'locals', 'vars', 'setattr', 'delattr',
                    '__builtins__', '__import__', 'import_module', 'getattr', 'eval', 'exec'}
    reflective = {'__dict__', '__globals__', '__setattr__', '__delattr__', '__getattribute__'}
    attributes = {'sys': {'argv', 'executable', 'stdout', 'stderr', 'exit'},
                  'subprocess': {'run', 'PIPE', 'DEVNULL', 'CompletedProcess'}}
    for node in ast.walk(tree):
        # A second import is also an alias to the same mutable module/class.
        # These are the only supported native-object import forms.
        if isinstance(node, ast.Import):
            if any(a.name == 'pathlib' or (a.name in ('sys', 'subprocess') and a.asname is not None)
                   for a in node.names):
                raise SourceError(path, 'protected native object imported through an alias', node.lineno)
        if isinstance(node, ast.ImportFrom):
            if (node.module in ('sys', 'subprocess') or (node.module == 'pathlib'
                    and any(a.name != 'Path' or a.asname is not None for a in node.names))):
                raise SourceError(path, 'unsupported protected native-object import', node.lineno)
        if ((isinstance(node, ast.alias) and node.name in capabilities | reflective)
                or (isinstance(node, ast.Attribute) and node.attr in capabilities | reflective)):
            raise SourceError(path, 'unsupported reflective namespace/mutation capability', getattr(node, 'lineno', None))
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id in capabilities:
                raise SourceError(path, 'unsupported dynamic namespace/mutation capability: ' + node.id, node.lineno)
            parent = parents.get(node)
            if node.id == 'Path':
                if not (isinstance(parent, ast.Call) and parent.func is node):
                    raise SourceError(path, 'protected Path callable escapes', node.lineno)
            elif node.id in attributes:
                if not (isinstance(parent, ast.Attribute) and parent.value is node
                        and isinstance(parent.ctx, ast.Load) and parent.attr in attributes[node.id]):
                    raise SourceError(path, 'protected native object escapes or changes: ' + node.id, node.lineno)
                use = parents.get(parent)
                if parent.attr in ('run', 'exit') and not (isinstance(use, ast.Call) and use.func is parent):
                    raise SourceError(path, 'protected native callable escapes', node.lineno)
                if parent.attr == 'argv' and not (isinstance(use, ast.Subscript) and use.value is parent and isinstance(use.ctx, ast.Load)):
                    raise SourceError(path, 'protected native argv escapes or changes', node.lineno)
        if isinstance(node, (ast.Attribute, ast.Subscript)) and isinstance(node.ctx, (ast.Store, ast.Del)):
            if any(isinstance(n, ast.Name) and n.id in {'sys', 'subprocess', 'Path'} for n in ast.walk(node)):
                raise SourceError(path, 'protected native object mutation', node.lineno)


def _aggregate(tree, path):
    _protected_objects(tree, path)
    _bindings(tree, path, {'AGG_VALIDATORS'})
    node = next((n for n in tree.body if isinstance(n, ast.Assign) and _name(n.targets[0], 'AGG_VALIDATORS')), None)
    if node is None or not isinstance(node.value, ast.Tuple):
        raise SourceError(path, 'AGG_VALIDATORS must be a literal tuple')
    value = _literal(node.value, path)
    if not value or any(not isinstance(v, str) or not re.fullmatch('[a-z][a-z0-9-]*', v) for v in value) or len(set(value)) != len(value):
        raise SourceError(path, 'AGG_VALIDATORS must contain distinct nonempty command IDs')
    return value


def read_aggregate(dispatcher_path):
    return _aggregate(_parse(dispatcher_path), dispatcher_path)


def _functions(tree):
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def _value(node, values, path):
    try:
        return _route_value(node, values, path)
    except (TypeError, IndexError, KeyError) as exc:
        raise SourceError(path, 'invalid route expression: ' + str(exc), getattr(node, 'lineno', None)) from None


def _route_value(node, values, path):
    """Only the finite literal/predicate vocabulary used by first-self-test routes."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name) and node.id in values:
        return values[node.id]
    if isinstance(node, (ast.Tuple, ast.List)):
        result = []
        for item in node.elts:
            if isinstance(item, ast.Starred):
                result.extend(_value(item.value, values, path))
            else:
                result.append(_value(item, values, path))
        return result
    if isinstance(node, ast.Subscript):
        try:
            return _value(node.value, values, path)[_value(node.slice, values, path)]
        except (KeyError, IndexError, TypeError):
            raise SourceError(path, 'invalid route subscription', node.lineno) from None
    if isinstance(node, ast.IfExp):
        return _value(node.body if _value(node.test, values, path) else node.orelse, values, path)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return not _value(node.operand, values, path)
    if isinstance(node, ast.BoolOp):
        result = _value(node.values[0], values, path)
        for item in node.values[1:]:
            if (isinstance(node.op, ast.And) and result) or (isinstance(node.op, ast.Or) and not result):
                result = _value(item, values, path)
        return result
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        left, right = _value(node.left, values, path), _value(node.comparators[0], values, path)
        op = node.ops[0]
        if isinstance(op, ast.Eq): return left == right
        if isinstance(op, ast.NotEq): return left != right
        if isinstance(op, ast.In): return left in right
        if isinstance(op, ast.NotIn): return left not in right
        if isinstance(op, ast.Lt): return left < right
    if _call(node, 'bool') and len(node.args) == 1 and not node.keywords:
        return bool(_value(node.args[0], values, path))
    if _call(node, 'len') and len(node.args) == 1 and not node.keywords:
        return len(_value(node.args[0], values, path))
    raise SourceError(path, 'unsupported route expression', getattr(node, 'lineno', None))


def _native_imports(tree, path):
    """Protect the small stdlib launch/path vocabulary from local replacement."""
    expected = {'sys': ('sys', None), 'subprocess': ('subprocess', None), 'Path': ('Path', 'pathlib')}
    if any(isinstance(n, ast.ImportFrom) and any(a.name == '*' for a in n.names) for n in ast.walk(tree)):
        raise SourceError(path, 'wildcard import cannot establish native bindings')
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    for name, (imported, module) in expected.items():
        bindings = [n for n in ast.walk(tree) if _bound_name(n) == name]
        if len(bindings) != 1 or not isinstance(bindings[0], ast.alias):
            raise SourceError(path, 'native launch/path name missing, rebound or shadowed: ' + name)
        alias = bindings[0]
        declaration = parents[alias]
        if (declaration not in tree.body or alias.name != imported or alias.asname is not None
                or (declaration.module if isinstance(declaration, ast.ImportFrom) else None) != module):
            raise SourceError(path, 'native launch/path import missing or ambiguous: ' + name)
    for node in ast.walk(tree):
        if _bound_name(node) in ('len', 'bool', 'str', 'map', 'next', 'int', 'all', 'sum', 'sorted', 'enumerate', 'print'):
            raise SourceError(path, 'source predicate builtin rebound', node.lineno)


def _launcher(function, path, canonical=False):
    """Prove the supported setup -> launch -> relay -> result sequence."""
    _signature(function, ('command',) if canonical else ('script', 'args'), path,
               vararg='arguments' if canonical else None, helper_input=not canonical)
    body = list(_body(function))
    setup = []
    # Only these two literal setup assignments precede the subprocess.
    for source in ('env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")',
                   'windows = os.name == "nt"'):
        expected = ast.parse(source).body[0]
        if body and ast.dump(body[0]) == ast.dump(expected):
            setup.append(body.pop(0).targets[0].id)
    if not body:
        raise SourceError(path, function.name + ': native launch missing')
    first = body.pop(0)
    target = None
    if isinstance(first, ast.Assign) and len(first.targets) == 1 and isinstance(first.targets[0], ast.Name):
        target, call = first.targets[0].id, first.value
    elif canonical and isinstance(first, ast.Return):
        call = first.value
    else:
        raise SourceError(path, function.name + ': unsupported control before native launch')
    if not isinstance(call, ast.Call) or not _same(call.func, 'subprocess.run') or len(call.args) != 1 or not isinstance(call.args[0], ast.List):
        raise SourceError(path, function.name + ': expected one direct native subprocess')
    argv = call.args[0].elts
    sibling = 'str(Path(__file__).resolve().parent / "validate.py")' if canonical else 'str(Path(__file__).resolve().parent / script)'
    if len(argv) < 3 or not _same(argv[0], 'sys.executable') or not _same(argv[1], sibling):
        raise SourceError(path, function.name + ': native interpreter/sibling binding absent')
    if canonical:
        valid = (len(argv) == 4 and _name(argv[2], 'command') and isinstance(argv[3], ast.Starred)
                 and (_name(argv[3].value, 'arguments') or _same(argv[3].value, 'map(str, arguments)')))
    else:
        valid = len(argv) == 3 and isinstance(argv[2], ast.Starred) and _name(argv[2].value, 'args')
    if not valid:
        raise SourceError(path, function.name + ': unsupported child arguments')
    allowed = {'shell': ('False',), 'capture_output': ('True', 'False')}
    if 'windows' in setup: allowed['capture_output'] += ('windows',)
    allowed['env'] = ('dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")',)
    if 'env' in setup: allowed['env'] += ('env',)
    if not canonical and function.args.kwonlyargs: allowed['input'] = ('input',)
    keys = [k.arg for k in call.keywords]
    if len(keys) != len(set(keys)) or any(k.arg not in allowed or not any(_same(k.value, form) for form in allowed[k.arg]) for k in call.keywords):
        raise SourceError(path, function.name + ': unsupported native launch options')
    if target is None:
        if body: raise SourceError(path, function.name + ': statements after direct subprocess return')
        return
    if target in setup or target in ('script', 'args', 'command', 'arguments', 'input'):
        raise SourceError(path, function.name + ': child result overwrites launch binding')
    if not canonical and body and isinstance(body[0], ast.If):
        if 'windows' not in setup:
            raise SourceError(path, function.name + ': relay lacks platform setup')
        _expect_body(body[:1], f'''if windows:
    for stream, output in ((sys.stdout.buffer, {target}.stdout), (sys.stderr.buffer, {target}.stderr)):
        stream.write(output.replace(b"\\r\\n", b"\\n"))
        stream.flush()
''', path, 'native stream relay')
        body.pop(0)
    expected_return = target if canonical else target + '.returncode'
    _expect_body(body, 'return ' + expected_return, path, 'native result return')


def _positional(call, count, path):
    if len(call.args) != count or call.keywords:
        raise SourceError(path, 'unsupported positional call arguments', call.lineno)


def _route(function, command, tables, functions, path):
    values = dict(tables, command=command, args=['--self-test'])
    helpers = []
    def block(statements):
        for statement in statements:
            if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
                target, rhs = statement.targets[0], statement.value
                if _call(rhs, '_run_helper'):
                    _positional(rhs, 2, path)
                    helper = _value(rhs.args[0], values, path)
                    args = _value(rhs.args[1], values, path)
                    if '--self-test' not in args:
                        raise SourceError(path, f'{command}: stripped self-test forwarding', statement.lineno)
                    helpers.append(helper)
                    if isinstance(target, ast.Name): values[target.id] = 0
                elif _call(rhs, '_override_companion'):
                    _positional(rhs, 0, path)
                    values[target.id] = 0
                elif isinstance(target, (ast.Name, ast.Tuple)):
                    if _name(target, 'script') and 'script' in values:
                        raise SourceError(path, 'helper binding reassigned', statement.lineno)
                    try:
                        value = _value(rhs, values, path)
                    except SourceError:
                        # These concrete repository-path assignments only support PDF's companion.
                        if function.name == '_annotation_export' and getattr(target, 'id', '') in ('root', 'suite'):
                            continue
                        raise
                    if isinstance(target, ast.Name): values[target.id] = value
                    else:
                        if len(target.elts) != len(value): raise SourceError(path, 'invalid table row')
                        for item, part in zip(target.elts, value): values[item.id] = part
            elif isinstance(statement, ast.If):
                try:
                    condition = _value(statement.test, values, path)
                except SourceError:
                    # Exact helper-availability guard. This establishes the available route;
                    # missing-file behavior is independently tested and never an empty PASS.
                    if _same(statement.test, 'not (Path(__file__).resolve().parent / script).is_file()'):
                        condition = False
                    elif function.name == '_annotation_export' and _same(statement.test, '(root / "AGENTS.md").is_file()'):
                        _pdf_companion(statement, path)
                        return True
                    else:
                        raise
                if block(statement.body if condition else statement.orelse): return True
            elif isinstance(statement, ast.Return):
                value = statement.value
                if _call(value, '_run_helper'):
                    _positional(value, 2, path)
                    helper = _value(value.args[0], values, path)
                    args = _value(value.args[1], values, path)
                    if '--self-test' not in args:
                        raise SourceError(path, f'{command}: stripped self-test forwarding', statement.lineno)
                    helpers.append(helper)
                elif _call(value, '_argument_carve') and len(value.args) == 1 and not value.keywords and _name(value.args[0], 'args'):
                    _native_suite(functions.get('_argument_carve'), path, carve=True)
                    helpers.append(None)
                elif not helpers:
                    raise SourceError(path, f'{command}: returns without a proven suite', statement.lineno)
                return True
            elif isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant):
                continue
            else:
                raise SourceError(path, f'{command}: unsupported handler statement', statement.lineno)
        return False
    block(function.body)
    if not helpers: raise SourceError(path, f'{command}: no bound helper or suite')
    if helpers == [None]: return CommandRoute((), 'carve')
    if any(not isinstance(h, str) or not re.fullmatch('[a-z_]+[.]py', h) for h in helpers):
        raise SourceError(path, f'{command}: helper is not a literal sibling')
    return CommandRoute(tuple(dict.fromkeys(helpers)), 'helper')


def _pdf_companion(statement, path):
    expected = ast.parse('''
suite = root / "tests/test_pdf_navigation.py"
if not suite.is_file():
    _line("pdf-export: N repository navigation acceptance suite unavailable")
    return 2
return _run_helper(suite, [])
''').body
    if [ast.dump(n) for n in statement.body] != [ast.dump(n) for n in expected]:
        raise SourceError(path, 'PDF companion path, invocation or failure propagation changed', statement.lineno)


def _native_suite(function, path, carve=False):
    """The two supported native suites, in execution order.

    These positive forms include the carve fixture-unavailable branch and each
    suite's real child/assertion/report paths. Matching the whole small form
    rejects exits or replacement bindings anywhere between those proof sites.
    No source being inspected is executed, and no arbitrary Python is modeled.
    """
    if function is None: raise SourceError(path, 'missing native suite')
    _signature(function, ('args',) if carve else ('command',), path)
    if carve:
        expected = r"""
scripts = _script_dir()
directory = next((candidate for candidate in (scripts + '/../../../evals/fixtures/argument-carve/precarve', scripts + '/../evals/fixtures/argument-carve/precarve') if os.path.isdir(candidate)), None)
self_test = bool(args and args[0] == '--self-test')
if directory is None:
    if self_test:
        _line('  fixture_present: SKIP (evals/ not present — repo-only gate)')
        _line('Self-test: PASS')
    else:
        _line('argument-carve-behavior-preservation: SKIP (evals/ not present — repo-only gate)')
    return 0
letter, ledger, propagation, decision = (directory + '/' + name for name in ('argument-editorial-letter.md', 'argument-findings-ledger.md', 'propagation-output.txt', 'decision-layer-output.txt'))
missing = False
for path in (letter, ledger, propagation, decision):
    if not os.path.isfile(path):
        if not self_test:
            _line(f'ERROR: argument-carve-behavior-preservation fixture missing: {path}')
            return 1
        _line(f'  fixture_present: FAIL (missing: {path})')
        missing = True
if missing:
    _line('Self-test: FAIL')
    return 1
if self_test:
    _line('  fixture_present: OK (4 fixture files found)')
failed = False
for command, child_args, golden, label in (('audit-signal-propagation', [letter, ledger], propagation, 'propagation_golden'), ('decision-layer-check', [letter], decision, 'decision_layer_golden')):
    child = subprocess.run([sys.executable, str(Path(__file__).resolve()), command, *child_args], env=dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8'), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if child.returncode:
        return child.returncode
    output = child.stdout[:-1] if child.stdout.endswith(b'\n') else child.stdout
    output = output.rsplit(b'\n', 1)[-1].replace(b'\x00', b'').rstrip(b'\n')
    try:
        expected = Path(golden).read_bytes().replace(b'\x00', b'').rstrip(b'\n')
    except OSError as exc:
        _line(f'Error: Cannot read file: {golden}: {exc.strerror}', error=True)
        return 1
    if output == expected:
        if self_test:
            _line(f'  {label}: OK')
    else:
        failed = True
        if self_test:
            _line(f'  {label}: FAIL')
        else:
            _line(f'ERROR: argument-carve-behavior-preservation: {command} output drifted from golden')
        indent = '    ' if self_test else '  '
        _line(indent + 'expected: ' + expected.decode('utf-8', errors='surrogateescape'))
        _line(indent + 'got:      ' + output.decode('utf-8', errors='surrogateescape'))
if self_test:
    _line('Self-test: FAIL' if failed else 'Self-test: PASS')
elif failed:
    _line('argument-carve-behavior-preservation: FAIL')
else:
    _line('argument-carve-behavior-preservation: PASS (smoke: resolvers still classify the argument fixture as Argument-DE post-carve; authoritative guarantee = audit-signal-propagation --check-registry + the byte-identical §4e diff)')
return int(failed)
"""
    else:
        expected = r"""
failed = False
def check(name, condition):
    nonlocal failed
    _line(f"  {name}: {('OK' if condition else 'FAIL')}")
    failed = failed or not condition
def run(*args):
    return subprocess.run([sys.executable, str(Path(__file__).resolve()), *args], capture_output=True)
def rc(name, expected, *args):
    result = run(*args)
    if result.returncode == expected:
        check(name, True)
    else:
        nonlocal failed
        failed = True
        _line(f'  {name}: FAIL (rc={result.returncode} want {expected})')
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'c.md'
    missing = str(Path(directory) / 'nope.md')
    if command == 'contract-hash':
        path.write_bytes(b'controlling idea\n')
        digest = run(command, str(path)).stdout.rstrip(b'\n')
        check('hash_is_64hex', re.fullmatch(b'[0-9a-f]{64}', digest) is not None)
        check('deterministic', digest == run(command, str(path)).stdout.rstrip(b'\n'))
        rc('missing_file_exit2', 2, command, missing)
        rc('no_arg_exit2', 2, command)
    elif command == 'contract-check':
        path.write_bytes(b'contract body\n')
        digest = run('contract-hash', str(path)).stdout.decode('ascii').strip()
        rc('match_exit0', 0, command, str(path), digest)
        rc('mismatch_exit1', 1, command, str(path), '0' * 64)
        rc('missing_file_exit2', 2, command, missing, digest)
        rc('missing_arg_exit2', 2, command, str(path))
    else:
        for count, label in ((5, 'counts_five'), (300, 'counts_300_warn_threshold'), (500, 'counts_500_forced_threshold')):
            path.write_bytes(''.join((f'{n}\n' for n in range(1, count + 1))).encode('ascii'))
            check(label, run(command, str(path)).stdout == f'{count}\n'.encode('ascii'))
        rc('missing_file_exit2', 2, command, missing)
        rc('no_arg_exit2', 2, command)
_line('Self-test: FAIL' if failed else 'Self-test: PASS')
return int(failed)
"""
    _expect_body(_body(function), expected, path, function.name)


def read_dispatch(dispatcher_path):
    tree = _parse(dispatcher_path)
    aggregate = _aggregate(tree, dispatcher_path)
    _native_imports(tree, dispatcher_path)
    functions = _functions(tree)
    main = functions.get('main')
    if main is None: raise SourceError(dispatcher_path, 'main missing')
    tables = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and isinstance(n.value, ast.Dict):
            tables[n.targets[0].id] = _literal(n.value, dispatcher_path)
    protected = {'main', '_run_helper'} | set(tables)
    handlers = set()
    routes = {}
    for command in dict.fromkeys((*aggregate, *(key for table in tables.values() for key in table))):
        values = dict(tables, command=command, args=[command, '--self-test'],
                      COMMANDS=(*aggregate, 'argument-aif-export'))
        # This navigation partition is an actual runtime declaration, not a helper map.
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(_name(t, '_BASH_COMMANDS_A') for t in node.targets):
                value = node.value
                if _call(value, 'frozenset') and len(value.args) == 1 and not value.keywords:
                    values['_BASH_COMMANDS_A'] = _value(value.args[0], values, dispatcher_path)
                else:
                    raise SourceError(dispatcher_path, 'unsupported navigation partition')
        def dispatch_block(statements):
            for statement in statements:
                if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
                    target, rhs = statement.targets[0], statement.value
                    if _name(target, 'args') and _same(rhs, 'list(sys.argv[1:] if argv is None else argv)'):
                        continue  # the known public main input for this command
                    if isinstance(target, ast.Tuple) and [getattr(n, 'id', '') for n in target.elts] == ['command', 'args'] and _same(rhs, '(args[0], args[1:])'):
                        values['args'] = ['--self-test']
                    elif _name(target, 'command') and _same(rhs, 'args[0]'):
                        values['command'] = command
                    elif _call(rhs, '_navigation_scan') and len(rhs.args) == 2 and not rhs.keywords and _name(rhs.args[0], 'command') and _name(rhs.args[1], 'args'):
                        values[target.id] = 0  # valid first-self-test has no navigation flag
                    else:
                        raise SourceError(dispatcher_path, 'unsupported main assignment before route', statement.lineno)
                elif isinstance(statement, ast.If):
                    condition = _value(statement.test, values, dispatcher_path)
                    result = dispatch_block(statement.body if condition else statement.orelse)
                    if result is not None: return result
                elif isinstance(statement, ast.Return):
                    call = statement.value
                    if isinstance(call, ast.Call) and isinstance(call.func, ast.Name):
                        if len(call.args) == 2 and not call.keywords and _name(call.args[0], 'command') and _name(call.args[1], 'args'):
                            handlers.add(call.func.id)
                            if call.func.id not in functions: raise SourceError(dispatcher_path, 'missing dispatch handler')
                            return _route(functions[call.func.id], command, tables, functions, dispatcher_path)
                        if _call(call, '_self_test') and len(call.args) == 1 and not call.keywords and _name(call.args[0], 'command'):
                            if command not in ('contract-hash', 'contract-check', 'state-lines'):
                                raise SourceError(dispatcher_path, f'{command}: not a native utility suite')
                            protected.add('_self_test')
                            _native_suite(functions.get('_self_test'), dispatcher_path)
                            return CommandRoute((), 'utility')
                    raise SourceError(dispatcher_path, f'{command}: returns before a proven dispatch route', statement.lineno)
                elif isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant):
                    continue
                else:
                    raise SourceError(dispatcher_path, f'{command}: unsupported control before route', statement.lineno)
            return None
        route = dispatch_block(main.body)
        if route is not None:
            routes[command] = route
        elif command in aggregate:
            raise SourceError(dispatcher_path, f'{command}: missing route')
    if any(route.self_test_kind == 'carve' for route in routes.values()): protected.add('_argument_carve')

    _bindings(tree, dispatcher_path, protected | handlers)
    _launcher(functions['_run_helper'], dispatcher_path)
    if set(aggregate) - routes.keys(): raise SourceError(dispatcher_path, 'unrouted aggregate command')
    return routes


def check_aggregate_count(dispatcher_path):
    tree = _parse(dispatcher_path)
    _aggregate(tree, dispatcher_path)
    _bindings(tree, dispatcher_path, {'_self_test_all'})
    function = _functions(tree)['_self_test_all']
    _native_imports(tree, dispatcher_path)
    _signature(function, (), dispatcher_path)
    ordered = _body(function)
    if len(ordered) != 9:
        raise SourceError(dispatcher_path, 'unsupported aggregate execution order')
    _expect_body(ordered[:4], 'total = len(AGG_VALIDATORS)\npassed = 0\nfailed = 0\ngate_ok = False', dispatcher_path, 'aggregate initialization')
    _expect_body(ordered[6:7], '_line("")', dispatcher_path, 'aggregate report separator')
    _expect_body(ordered[8:], 'return int(bool(failed))', dispatcher_path, 'aggregate result')
    _expect_body(ordered[5:6], r"""
for command in AGG_VALIDATORS:
    if command == 'gate-state':
        ok = gate_ok
        detail = ' (covered by gate shared suite)' if ok else ' (gate shared suite failed)'
    else:
        child = subprocess.run([sys.executable, str(Path(__file__).resolve()), command, '--self-test'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8'))
        ok = child.returncode == 0
        detail = ''
        if command == 'gate':
            gate_ok = ok
    _line(f"  {command}: {('PASS' if ok else 'FAIL')}{detail}")
    if ok:
        passed += 1
    else:
        failed += 1
""", dispatcher_path, 'aggregate loop and status')
    # Reports are direct calls with only literal text and the bound counters;
    # no preceding return, hidden expression call or decorative later report.
    def report(statement, fields):
        if not isinstance(statement, ast.Expr) or not _call(statement.value, '_line'):
            raise SourceError(dispatcher_path, 'aggregate report is not direct')
        call = statement.value
        if len(call.args) != 1 or call.keywords or not isinstance(call.args[0], ast.JoinedStr):
            raise SourceError(dispatcher_path, 'unsupported aggregate report')
        actual = []
        for part in call.args[0].values:
            if isinstance(part, ast.Constant) and isinstance(part.value, str): continue
            if (not isinstance(part, ast.FormattedValue) or not isinstance(part.value, ast.Name)
                    or part.conversion != -1 or part.format_spec is not None):
                raise SourceError(dispatcher_path, 'unsupported aggregate report expression')
            actual.append(part.value.id)
        if actual != list(fields):
            raise SourceError(dispatcher_path, 'aggregate report counters are disconnected')
    report(ordered[4], ('total',))
    summary = ordered[7]
    if not isinstance(summary, ast.If) or not _name(summary.test, 'failed') or len(summary.body) != 1 or len(summary.orelse) != 1:
        raise SourceError(dispatcher_path, 'aggregate summary execution order changed')
    report(summary.body[0], ('failed', 'total'))
    report(summary.orelse[0], ('passed', 'total'))


def schema_literals(path):
    tree = _parse(path)
    prose = {id(n.value) for n in ast.walk(tree) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)}
    return tuple(n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in prose)


def _reference(node, values, allow_name=True):
    if _name(node, 'references'): return ()
    if isinstance(node, ast.Name): return values.get(node.id) if allow_name else None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _reference(node.left, values, allow_name)
        if left is not None and isinstance(node.right, ast.Constant) and isinstance(node.right.value, str):
            return left + tuple(node.right.value.replace('\\', '/').split('/'))
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        parts = tuple(node.value.replace('\\', '/').split('/'))
        for root in (('plugins', 'apodictic', 'skills', 'core-editor', 'references'), ('skills', 'core-editor', 'references')):
            if parts[:len(root)] == root: return parts[len(root):]
    return None


def _exists_guard(node, values):
    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
        return all(_exists_guard(n, values) for n in node.values)
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr in ('exists', 'is_file', 'is_dir') and not node.args and not node.keywords
            and _reference(node.func.value, values) is not None)


def _root_selector(node, proven):
    """The three reviewed reference-root selectors; never a canonical anchor.

    No general generator evaluation: exactly one variable, two fixed roots,
    one existence predicate and an already proven/default fixed root.
    """
    roots = ("HERE / '../skills/core-editor/references'",
             "HERE / '../plugins/apodictic/skills/core-editor/references'")
    if any(_same(node, root.replace('HERE', 'Path(__file__).resolve().parent')) for root in roots):
        return True
    if not _call(node, 'next') or len(node.args) != 2 or node.keywords:
        return False
    generator, fallback = node.args
    if not isinstance(generator, ast.GeneratorExp) or len(generator.generators) != 1:
        return False
    clause = generator.generators[0]
    if clause.is_async or not _name(clause.target, 'path') or not _name(generator.elt, 'path') or len(clause.ifs) != 1:
        return False
    if not isinstance(clause.iter, ast.Tuple) or len(clause.iter.elts) != 2:
        return False
    choices = clause.iter.elts
    if not ((all(_same(n, r) for n, r in zip(choices, roots))) or
            (all(_same(n, r) for n, r in zip(choices, reversed(roots))))):
        return False
    predicate = clause.ifs[0]
    if not (_same(predicate, 'path.is_dir()') or
            _same(predicate, "(path / 'diagnostic-state-meta-template.json').is_file()") or
            _same(predicate, "(path / 'example-argument-aif-export.json').is_file()")):
        return False
    return ((isinstance(fallback, ast.Name) and fallback.id in proven)
            or any(_same(fallback, root) for root in roots))


def _canonical_syntax(statements, path, *, entry=False, sections=()):
    """Closed syntax vocabulary, not an evaluator of canonical Python.

    This check cannot credit anchors. It only establishes that the later scanner
    is not skipping an unknown statement or an unknown call hidden in an operand.
    Fixture-work blocks retain no anchor credit. Their explicit operations are
    admitted here so later direct reference checks can still be inspected.
    """
    calls = {'run_validator', '_line', 'print', 'int', 'bool', 'next', 'Path'}
    methods = {'resolve', 'exists', 'is_file', 'is_dir'}
    module_calls = set()
    statements_allowed = (ast.Assign, ast.AugAssign, ast.Expr, ast.If, ast.Return)
    if entry:
        calls.update(sections)
    else:
        calls.update({'_relay', '_summary', '_captured', '_text', '_check', '_temporary',
                      '_producer', '_write', '_rewrite', '_without_lines', '_copy_globs',
                      '_same_bytes', '_evals', '_locate', '_corpus_result',
                      'CanonicalAbort', 'OSError', 'len', 'all', 'sorted', 'sum', 'enumerate'})
        methods.update({'read_text', 'glob', 'mkdir', 'unlink', 'touch', 'replace',
                        'splitlines', 'join', 'append', 'extend', 'pop', 'setdefault',
                        'update', 'start', 'end', 'group'})
        module_calls.update({'json.loads', 'json.dumps', 're.search', 're.sub',
                             'shutil.copyfile', 'shutil.copytree', 'am.check',
                             'am.normalize_snapshot', 'dispatch_record.parse_model_tag_table'})
        statements_allowed += (ast.For, ast.With, ast.Try, ast.Raise, ast.Delete,
                               ast.Continue, ast.Pass, ast.Import)
    expressions_allowed = (ast.Name, ast.Constant, ast.Attribute, ast.Subscript,
                          ast.Slice, ast.List, ast.Tuple, ast.Set, ast.Dict,
                          ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare, ast.IfExp,
                          ast.JoinedStr, ast.FormattedValue, ast.Call,
                          ast.GeneratorExp, ast.ListComp)
    for statement in statements:
        parents = {child: parent for parent in ast.walk(statement) for child in ast.iter_child_nodes(parent)}
        for node in ast.walk(statement):
            if isinstance(node, ast.stmt) and not isinstance(node, statements_allowed):
                raise SourceError(path, 'unsupported canonical statement: ' + type(node).__name__, node.lineno)
            if isinstance(node, ast.expr) and not isinstance(node, expressions_allowed):
                raise SourceError(path, 'unsupported canonical expression: ' + type(node).__name__, node.lineno)
            if isinstance(node, ast.Call):
                function = node.func
                direct = isinstance(function, ast.Name) and function.id in calls
                if entry and isinstance(function, ast.Name) and function.id in sections:
                    parent = parents.get(node)
                    if not (isinstance(parent, (ast.Assign, ast.Expr)) and parent.value is node):
                        raise SourceError(path, 'canonical section call must be direct', node.lineno)
                method = (isinstance(function, ast.Attribute) and function.attr in methods
                          and not (isinstance(function.value, ast.Name)
                                   and function.value.id in {'sys', 'subprocess', 'os', 'Path'}))
                module = isinstance(function, ast.Attribute) and ast.unparse(function) in module_calls
                if not (direct or method or module):
                    raise SourceError(path, 'unsupported canonical call', node.lineno)
                if any(k.arg is None for k in node.keywords):
                    raise SourceError(path, 'unsupported canonical call expansion', node.lineno)
            if isinstance(node, ast.Import):
                if ast.dump(node) not in {ast.dump(ast.parse('import dispatch_record').body[0]),
                                         ast.dump(ast.parse('import annotation_manifest as am').body[0])}:
                    raise SourceError(path, 'unsupported canonical import', node.lineno)
            if isinstance(node, ast.ExceptHandler):
                if not _name(node.type, 'Exception') or node.name is not None:
                    raise SourceError(path, 'unsupported canonical exception binding', node.lineno)
            if isinstance(node, ast.comprehension) and node.is_async:
                raise SourceError(path, 'unsupported async canonical comprehension')


def _control_exits(node):
    """Negative evidence only: skipped control may exit this function.

    A return inside an uncalled nested definition is not an enclosing exit.
    Never use this traversal to credit calls or paths as executed.
    """
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return False
    if isinstance(node, (ast.Return, ast.Raise, ast.While)):
        return True
    return any(_control_exits(child) for child in ast.iter_child_nodes(node))


def read_canonical(dispatcher_path, canonical_path):
    dispatcher = _parse(dispatcher_path)
    canonical = _parse(canonical_path)
    _protected_objects(dispatcher, dispatcher_path)
    _protected_objects(canonical, canonical_path)
    _native_imports(canonical, canonical_path)
    functions = _functions(canonical)
    if 'run_canonical' not in functions or 'run_validator' not in functions:
        raise SourceError(canonical_path, 'canonical entry/launcher missing')
    imports = [n for n in ast.walk(dispatcher) if isinstance(n, ast.ImportFrom) and n.module == 'validate_canonical' and any(a.name == 'run_canonical' and a.asname is None for a in n.names)]
    if len(imports) != 1: raise SourceError(dispatcher_path, 'fixed canonical sibling import missing or ambiguous')
    _bindings(dispatcher, dispatcher_path, {'run_canonical'})
    main = _functions(dispatcher).get('main')
    if main is None: raise SourceError(dispatcher_path, 'canonical main missing')
    # Follow the selected mode in lexical order, rather than finding a later
    # convincing call behind an earlier return or unknown guard.
    for mode in ('--check-canonical', '--check-all'):
        values = {'args': [mode], 'command': mode}
        reached = []
        imported = imports[0] in dispatcher.body
        def entry_route(statements):
            nonlocal imported
            for statement in statements:
                if isinstance(statement, ast.If):
                    condition = _value(statement.test, values, dispatcher_path)
                    if entry_route(statement.body if condition else statement.orelse): return True
                elif isinstance(statement, ast.ImportFrom):
                    if statement is not imports[0]: raise SourceError(dispatcher_path, 'unsupported canonical route import')
                    imported = True
                elif isinstance(statement, ast.Assign):
                    if len(statement.targets) != 1: raise SourceError(dispatcher_path, 'unsupported canonical route assignment')
                    target, value = statement.targets[0], statement.value
                    if _name(target, 'args') and _same(value, 'list(sys.argv[1:] if argv is None else argv)'): continue
                    if _name(target, 'command') and _same(value, 'args[0]'): continue
                    if _call(value, 'run_canonical'):
                        if not imported: raise SourceError(dispatcher_path, 'canonical import is not reached before entry call')
                        if value.args or value.keywords: raise SourceError(dispatcher_path, 'canonical entry arguments changed')
                        reached.append(statement)
                    elif _call(value, '_self_test_all'):
                        _positional(value, 0, dispatcher_path)
                    elif _same(value, 'int(bool(self_tests or canonical))'):
                        continue
                    elif isinstance(value, ast.Constant): continue
                    else: raise SourceError(dispatcher_path, 'unsupported expression before canonical entry', statement.lineno)
                elif isinstance(statement, ast.Expr) and (_call(statement.value, '_line') or isinstance(statement.value, ast.Constant)):
                    continue
                elif isinstance(statement, ast.Return):
                    if _call(statement.value, 'run_canonical'):
                        _positional(statement.value, 0, dispatcher_path)
                        if not imported: raise SourceError(dispatcher_path, 'canonical import is not reached before entry call')
                        reached.append(statement)
                    return True
                else:
                    raise SourceError(dispatcher_path, 'unsupported control before canonical entry', statement.lineno)
            return False
        entry_route(main.body)
        if len(reached) != 1:
            raise SourceError(dispatcher_path, f'{mode}: actual route must call canonical entry exactly once')
    _signature(functions['run_canonical'], (), canonical_path)
    _launcher(functions['run_validator'], canonical_path, canonical=True)
    if any(_name(n, 'HERE') or _bound_name(n) == 'HERE' for n in ast.walk(canonical)):
        declarations = [n for n in canonical.body if isinstance(n, ast.Assign) and len(n.targets) == 1 and _name(n.targets[0], 'HERE')]
        stores = [n for n in ast.walk(canonical) if _bound_name(n) == 'HERE']
        if len(declarations) != 1 or len(stores) != 1 or not _same(declarations[0].value, 'Path(__file__).resolve().parent'):
            raise SourceError(canonical_path, 'canonical sibling root missing or rebound')
    _canonical_syntax(_body(functions['run_canonical']), canonical_path, entry=True,
                      sections={name for name, function in functions.items()
                                if function.args.args and function.args.args[0].arg == 'references'})
    calls, sections = [], set()
    roots = set()
    def scan(statements, values, entry=False):
        for statement in statements:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.For, ast.While, ast.Try, ast.With)):
                if _control_exits(statement): return True
                # Other canonical work cannot supply C5 anchors. Invalidate assignments
                # because a cross-block value must not escape as an earlier path.
                for n in ast.walk(statement):
                    if _bound_name(n) is not None:
                        values.pop(_bound_name(n), None)
                continue
            call = statement.value if isinstance(statement, (ast.Expr, ast.Assign, ast.Return)) else None
            if isinstance(statement, ast.If):
                testcall = statement.test
                if isinstance(testcall, ast.Compare): testcall = testcall.left
                if isinstance(testcall, ast.Attribute): testcall = testcall.value
                if _call(testcall, 'run_validator'): record(testcall, values)
                if _exists_guard(statement.test, values):
                    if scan(statement.body, dict(values), entry) or any(_control_exits(n) for n in statement.orelse):
                        return True
                elif _control_exits(statement):
                    return True
                for n in ast.walk(statement):
                    if _bound_name(n) is not None: values.pop(_bound_name(n), None)
            if _call(call, 'run_validator'): record(call, values)
            elif entry and isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id in functions:
                name = call.func.id
                if name not in ('run_canonical', 'run_validator'):
                    if name in sections: raise SourceError(canonical_path, 'duplicate canonical section invocation', statement.lineno)
                    if len(call.args) != 1 or call.keywords or not isinstance(call.args[0], ast.Name) or call.args[0].id not in roots:
                        raise SourceError(canonical_path, 'canonical section must receive unchanged references', statement.lineno)
                    sections.add(name)
                    _signature(functions[name], ('references',), canonical_path)
                    _canonical_syntax(_body(functions[name]), canonical_path)
                    scan(functions[name].body, {})
            if isinstance(statement, (ast.Assign, ast.AugAssign, ast.Delete)):
                for node in ast.walk(statement):
                    if _bound_name(node) is not None:
                        values.pop(_bound_name(node), None)
            if isinstance(statement, ast.Assign):
                for target in statement.targets:
                    if isinstance(target, ast.Name):
                        if target.id == 'references' and not entry: raise SourceError(canonical_path, 'references binding changed', statement.lineno)
                        if entry and _root_selector(statement.value, roots):
                            if target.id in roots: raise SourceError(canonical_path, 'reference selector rebound', statement.lineno)
                            roots.add(target.id)
                        elif entry and (target.id in roots or target.id == 'references'):
                            raise SourceError(canonical_path, 'unsupported reference root selector', statement.lineno)
                        value = _reference(statement.value, {}, allow_name=False)
                        if value is None: values.pop(target.id, None)
                        else: values[target.id] = value
            if isinstance(statement, (ast.Return, ast.Raise)): return True
        return False
    def record(call, values):
        if call.keywords:
            raise SourceError(canonical_path, 'canonical validator requires positional arguments', call.lineno)
        if not call.args or not isinstance(call.args[0], ast.Constant) or not isinstance(call.args[0].value, str):
            return
        paths = tuple(p for n in call.args[1:] if (p := _reference(n, values)) is not None and p)
        if paths: calls.append(CanonicalCall(call.args[0].value, paths, call.lineno))
    scan(functions['run_canonical'].body, {}, True)
    if not roots: raise SourceError(canonical_path, 'no proven canonical references root')
    for name in roots:
        stores = [n for n in ast.walk(functions['run_canonical']) if _bound_name(n) == name]
        if len(stores) != 1: raise SourceError(canonical_path, 'reference selector rebound: ' + name)
    _bindings(canonical, canonical_path, {'run_canonical', 'run_validator'} | sections)
    return tuple(calls)
