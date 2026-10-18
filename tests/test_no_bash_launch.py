"""Shipped Python must not launch a POSIX shell: Windows runs the validators with no Bash.

The Windows CI job runs the gate with only Python on PATH, so a shell launch on a
path that job exercises fails there. This static check covers the paths it does not.
"""
import ast
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1] / "plugins/apodictic"
SHELLS = {"bash", "sh", "bash.exe", "sh.exe"}


def _is_shell(node):
    return (isinstance(node, ast.Constant) and isinstance(node.value, str) and bool(node.value.split())
            and Path(node.value.split()[0]).name in SHELLS)


def _launches_shell(node):
    """An argv literal led by a shell, a call whose command string is led by one, or shell=True."""
    if isinstance(node, (ast.List, ast.Tuple)):
        return bool(node.elts) and _is_shell(node.elts[0])
    if isinstance(node, ast.Call):
        return (any(k.arg == "shell" and not (isinstance(k.value, ast.Constant) and not k.value.value)
                    for k in node.keywords)
                or bool(node.args) and _is_shell(node.args[0]))
    return False


def test_no_shipped_python_launches_a_shell():
    offenders = [f"{path.relative_to(PLUGIN)}:{node.lineno}"
                 for path in sorted(PLUGIN.rglob("*.py"))
                 for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
                 if _launches_shell(node)]
    assert offenders == []
