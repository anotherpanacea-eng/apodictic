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


def _bindings(tree, path, names):
    """Reject rebinding, item mutation and alias escape of the protected names.

    The AST walk here only finds prohibited writes/uses. It never credits a call
    or a literal as evidence that a runtime path executes.
    """
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    for name in names:
        definitions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
                definitions.append(node)
            elif isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, (ast.Store, ast.Del)):
                definitions.append(node)
            elif isinstance(node, ast.alias) and (node.asname or node.name.split('.')[0]) == name:
                definitions.append(node)
            elif isinstance(node, ast.arg) and node.arg == name:
                definitions.append(node)
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


def _aggregate(tree, path):
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
    if _call(node, 'bool') and len(node.args) == 1:
        return bool(_value(node.args[0], values, path))
    if _call(node, 'len') and len(node.args) == 1:
        return len(_value(node.args[0], values, path))
    raise SourceError(path, 'unsupported route expression', getattr(node, 'lineno', None))


def _native_imports(tree, path):
    """Protect the small stdlib launch/path vocabulary from local replacement."""
    expected = {'sys': ('sys', None), 'subprocess': ('subprocess', None), 'Path': ('Path', 'pathlib')}
    for name, (imported, module) in expected.items():
        aliases = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if (alias.asname or alias.name) == name:
                        if node not in tree.body:
                            raise SourceError(path, 'native launch/path import is not unconditional: ' + name, node.lineno)
                        aliases.append((alias.name, node.module if isinstance(node, ast.ImportFrom) else None))
            if isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, (ast.Store, ast.Del)):
                raise SourceError(path, 'native launch/path name rebound: ' + name, node.lineno)
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name:
                raise SourceError(path, 'native launch/path callable rebound: ' + name, node.lineno)
            if isinstance(node, ast.arg) and node.arg == name:
                raise SourceError(path, 'native launch/path name shadowed: ' + name, node.lineno)
            if isinstance(node, ast.Attribute) and isinstance(node.ctx, (ast.Store, ast.Del)) and any(_name(n, name) for n in ast.walk(node.value)):
                raise SourceError(path, 'native launch/path attribute changed: ' + name, node.lineno)
        if aliases != [(imported, module)]:
            raise SourceError(path, 'native launch/path import missing or ambiguous: ' + name)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in ('len', 'bool', 'str', 'map', 'next') and isinstance(node.ctx, (ast.Store, ast.Del)):
            raise SourceError(path, 'source predicate builtin rebound', node.lineno)


def _launcher(function, path, canonical=False):
    """Require the actual direct subprocess result and native argv/return binding."""
    calls = []
    for statement in function.body:
        if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
            value = statement.value
            if isinstance(value, ast.Call) and _same(value.func, 'subprocess.run'):
                calls.append((statement.targets[0], value))
        elif isinstance(statement, ast.Return) and isinstance(statement.value, ast.Call) and _same(statement.value.func, 'subprocess.run'):
            calls.append((None, statement.value))
        if isinstance(statement, (ast.Return, ast.Raise)):
            break
    if len(calls) != 1:
        raise SourceError(path, f'{function.name}: no unique direct native subprocess')
    target, call = calls[0]
    if not call.args or not isinstance(call.args[0], ast.List):
        raise SourceError(path, f'{function.name}: native argv must be explicit')
    argv = call.args[0].elts
    expected = 'str(Path(__file__).resolve().parent / "validate.py")' if canonical else 'str(Path(__file__).resolve().parent / script)'
    if len(argv) < 3 or not _same(argv[0], 'sys.executable') or not _same(argv[1], expected):
        raise SourceError(path, f'{function.name}: native interpreter/sibling binding absent')
    if canonical:
        valid = (_name(argv[2], 'command') and len(argv) == 4 and isinstance(argv[3], ast.Starred)
                 and (_name(argv[3].value, 'arguments') or _same(argv[3].value, 'map(str, arguments)')))
    else:
        valid = len(argv) == 3 and isinstance(argv[2], ast.Starred) and _name(argv[2].value, 'args')
    if not valid or any(k.arg == 'shell' and not _same(k.value, 'False') for k in call.keywords):
        raise SourceError(path, f'{function.name}: unsupported child arguments')
    if target is not None:
        writes = [n for n in ast.walk(function) if _name(n, target.id) and isinstance(n.ctx, (ast.Store, ast.Del))]
        changed = [n for n in ast.walk(function) if isinstance(n, ast.Attribute) and isinstance(n.ctx, (ast.Store, ast.Del)) and _name(n.value, target.id)]
        if len(writes) != 1 or changed:
            raise SourceError(path, f'{function.name}: child result rebound or modified')
        expected_return = target.id if canonical else target.id + '.returncode'
        if not any(isinstance(n, ast.Return) and n.value is not None and _same(n.value, expected_return) for n in function.body):
            raise SourceError(path, f'{function.name}: child result is not returned')


def _route(function, command, tables, functions, path):
    values = dict(tables, command=command, args=['--self-test'])
    helpers = []
    def block(statements):
        for statement in statements:
            if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
                target, rhs = statement.targets[0], statement.value
                if _call(rhs, '_run_helper'):
                    helper = _value(rhs.args[0], values, path)
                    args = _value(rhs.args[1], values, path)
                    if '--self-test' not in args:
                        raise SourceError(path, f'{command}: stripped self-test forwarding', statement.lineno)
                    helpers.append(helper)
                    if isinstance(target, ast.Name): values[target.id] = 0
                elif _call(rhs, '_override_companion'):
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
                    helper = _value(value.args[0], values, path)
                    args = _value(value.args[1], values, path)
                    if '--self-test' not in args:
                        raise SourceError(path, f'{command}: stripped self-test forwarding', statement.lineno)
                    helpers.append(helper)
                elif _call(value, '_argument_carve') and len(value.args) == 1 and _name(value.args[0], 'args'):
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
    if function is None: raise SourceError(path, 'missing native suite')
    if carve:
        guards = [n for n in function.body if isinstance(n, ast.Assign) and any(_name(t, 'self_test') for t in n.targets)]
        if len(guards) != 1 or not _same(guards[0].value, 'bool(args and args[0] == "--self-test")'):
            raise SourceError(path, 'carve first-self-test predicate absent')
        loops = [n for n in function.body if isinstance(n, ast.For)]
        if not any(any(isinstance(s, ast.Assign) and isinstance(s.value, ast.Call) and _same(s.value.func, 'subprocess.run') for s in n.body) for n in loops):
            raise SourceError(path, 'carve golden subprocess loop absent')
    else:
        children = [n for n in function.body if isinstance(n, ast.FunctionDef) and n.name == 'run']
        if len(children) != 1 or not any(isinstance(n, ast.Return) and isinstance(n.value, ast.Call) and _same(n.value.func, 'subprocess.run') for n in children[0].body):
            raise SourceError(path, 'utility native suite child absent')
    if not any(isinstance(n, ast.Return) and _same(n.value, 'int(failed)') for n in function.body):
        raise SourceError(path, 'native suite failure result absent')


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
                if _call(value, 'frozenset') and len(value.args) == 1:
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
                    elif _call(rhs, '_navigation_scan') and len(rhs.args) == 2 and _name(rhs.args[0], 'command') and _name(rhs.args[1], 'args'):
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
                        if len(call.args) == 2 and _name(call.args[0], 'command') and _name(call.args[1], 'args'):
                            handlers.add(call.func.id)
                            if call.func.id not in functions: raise SourceError(dispatcher_path, 'missing dispatch handler')
                            return _route(functions[call.func.id], command, tables, functions, dispatcher_path)
                        if _call(call, '_self_test') and len(call.args) == 1 and _name(call.args[0], 'command'):
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
    total = [n for n in ast.walk(function) if isinstance(n, ast.Name) and n.id == 'total' and isinstance(n.ctx, (ast.Store, ast.Del))]
    if len(total) != 1:
        raise SourceError(dispatcher_path, 'aggregate total missing or overwritten')
    body = function.body
    assignment = next((n for n in body if isinstance(n, ast.Assign) and any(_name(t, 'total') for t in n.targets)), None)
    if assignment is None or not _same(assignment.value, 'len(AGG_VALIDATORS)'):
        raise SourceError(dispatcher_path, 'aggregate total is not derived')
    loop = next((n for n in body if isinstance(n, ast.For) and _name(n.iter, 'AGG_VALIDATORS')), None)
    if loop is None or body.index(loop) < body.index(assignment):
        raise SourceError(dispatcher_path, 'aggregate registry loop absent')
    # The loop must actually launch the current registry item, not be decorative.
    if not isinstance(loop.target, ast.Name): raise SourceError(dispatcher_path, 'aggregate loop target unsupported')
    item = loop.target.id
    launch = None
    for statement in loop.body:
        if isinstance(statement, ast.If) and _same(statement.test, f'{item} == "gate-state"'):
            for child in statement.orelse:
                if isinstance(child, ast.Assign) and isinstance(child.value, ast.Call) and _same(child.value.func, 'subprocess.run'):
                    launch = child
    if launch is None or len(launch.targets) != 1 or not isinstance(launch.targets[0], ast.Name):
        raise SourceError(dispatcher_path, 'aggregate registry loop does not launch a child')
    if not launch.value.args or not _same(launch.value.args[0], f'[sys.executable, str(Path(__file__).resolve()), {item}, "--self-test"]'):
        raise SourceError(dispatcher_path, 'aggregate child does not use registry item')
    child_name = launch.targets[0].id
    condition = next((n for n in loop.body if isinstance(n, ast.If) and _same(n.test, f'{item} == "gate-state"')), None)
    if not any(isinstance(n, ast.Assign) and any(_name(t, 'ok') for t in n.targets) and _same(n.value, child_name + '.returncode == 0') for n in condition.orelse):
        raise SourceError(dispatcher_path, 'aggregate child status disconnected')
    summary = next((n for n in body[body.index(loop) + 1:] if isinstance(n, ast.If) and _name(n.test, 'failed')), None)
    if summary is None:
        raise SourceError(dispatcher_path, 'aggregate status summary missing')
    for branch in (summary.body, summary.orelse):
        reports = [n.value for n in branch if isinstance(n, ast.Expr) and _call(n.value, '_line')]
        if len(reports) != 1 or not reports[0].args or not isinstance(reports[0].args[0], ast.JoinedStr):
            raise SourceError(dispatcher_path, 'aggregate summary is not the actual formatted report')
        if not any(isinstance(n, ast.FormattedValue) and _name(n.value, 'total') for n in reports[0].args[0].values):
            raise SourceError(dispatcher_path, 'aggregate summary does not use derived total')


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
            and node.func.attr in ('exists', 'is_file', 'is_dir') and not node.args
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


def read_canonical(dispatcher_path, canonical_path):
    dispatcher = _parse(dispatcher_path)
    canonical = _parse(canonical_path)
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
                    elif _call(value, '_self_test_all') or _same(value, 'int(bool(self_tests or canonical))'):
                        continue
                    elif isinstance(value, ast.Constant): continue
                    else: raise SourceError(dispatcher_path, 'unsupported expression before canonical entry', statement.lineno)
                elif isinstance(statement, ast.Expr) and (_call(statement.value, '_line') or isinstance(statement.value, ast.Constant)):
                    continue
                elif isinstance(statement, ast.Return):
                    if _call(statement.value, 'run_canonical'):
                        if not imported: raise SourceError(dispatcher_path, 'canonical import is not reached before entry call')
                        reached.append(statement)
                    return True
                else:
                    raise SourceError(dispatcher_path, 'unsupported control before canonical entry', statement.lineno)
            return False
        entry_route(main.body)
        if len(reached) != 1:
            raise SourceError(dispatcher_path, f'{mode}: actual route must call canonical entry exactly once')
    _launcher(functions['run_validator'], canonical_path, canonical=True)
    if any(_name(n, 'HERE') for n in ast.walk(canonical)):
        declarations = [n for n in canonical.body if isinstance(n, ast.Assign) and len(n.targets) == 1 and _name(n.targets[0], 'HERE')]
        stores = [n for n in ast.walk(canonical) if (_name(n, 'HERE') and isinstance(n.ctx, (ast.Store, ast.Del))) or (isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == 'HERE') or (isinstance(n, ast.alias) and (n.asname or n.name) == 'HERE') or (isinstance(n, ast.arg) and n.arg == 'HERE')]
        if len(declarations) != 1 or len(stores) != 1 or not _same(declarations[0].value, 'Path(__file__).resolve().parent'):
            raise SourceError(canonical_path, 'canonical sibling root missing or rebound')
    calls, sections = [], set()
    roots = set()
    def scan(statements, values, entry=False):
        for statement in statements:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.For, ast.While, ast.Try, ast.With)):
                # Other canonical work cannot supply C5 anchors. Invalidate assignments
                # because a cross-block value must not escape as an earlier path.
                for n in ast.walk(statement):
                    if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
                        values.pop(n.id, None)
                continue
            call = statement.value if isinstance(statement, (ast.Expr, ast.Assign, ast.Return)) else None
            if isinstance(statement, ast.If):
                testcall = statement.test
                if isinstance(testcall, ast.Compare): testcall = testcall.left
                if isinstance(testcall, ast.Attribute): testcall = testcall.value
                if _call(testcall, 'run_validator'): record(testcall, values)
                if _exists_guard(statement.test, values): scan(statement.body, dict(values), entry)
                for n in ast.walk(statement):
                    if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)): values.pop(n.id, None)
            if _call(call, 'run_validator'): record(call, values)
            elif entry and isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id in functions:
                name = call.func.id
                if name not in ('run_canonical', 'run_validator'):
                    if name in sections: raise SourceError(canonical_path, 'duplicate canonical section invocation', statement.lineno)
                    if not call.args or not isinstance(call.args[0], ast.Name) or call.args[0].id not in roots:
                        raise SourceError(canonical_path, 'canonical section must receive unchanged references', statement.lineno)
                    sections.add(name)
                    for node in ast.walk(functions[name]):
                        if isinstance(node, ast.Name) and node.id == 'references' and isinstance(node.ctx, (ast.Store, ast.Del)):
                            raise SourceError(canonical_path, 'section references binding changed', node.lineno)
                    scan(functions[name].body, {})
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
            if isinstance(statement, (ast.Return, ast.Raise)): break
    def record(call, values):
        if not call.args or not isinstance(call.args[0], ast.Constant) or not isinstance(call.args[0].value, str):
            return
        paths = tuple(p for n in call.args[1:] if (p := _reference(n, values)) is not None and p)
        if paths: calls.append(CanonicalCall(call.args[0].value, paths, call.lineno))
    scan(functions['run_canonical'].body, {}, True)
    if not roots: raise SourceError(canonical_path, 'no proven canonical references root')
    for name in roots:
        stores = [n for n in ast.walk(functions['run_canonical']) if (_name(n, name) and isinstance(n.ctx, (ast.Store, ast.Del))) or (isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == name) or (isinstance(n, ast.alias) and (n.asname or n.name) == name)]
        if len(stores) != 1: raise SourceError(canonical_path, 'reference selector rebound: ' + name)
    _bindings(canonical, canonical_path, {'run_canonical', 'run_validator'} | sections)
    return tuple(calls)
