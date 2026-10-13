"""CB-1(a) utility behavior and exact-byte Bash/Python differential harness.

Bash stays an independent oracle during the migration. Native byte-contract tests
also run on hosts with no Bash or external hash/count tools.
"""

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins/apodictic/scripts"
PYTHON_CLI = SCRIPTS / "validate.py"
BASH_CLI = SCRIPTS / "validate.sh"
UTILITIES = (
    "contract-hash", "contract-check", "ledger-check", "artifact-names",
    "synthesis-sections", "tone-check", "state-lines",
)
BASH = shutil.which("bash")
FIXTURES = sorted(
    path for path in (ROOT / "tests/fixtures/validators").glob("lc.*.*.*.md")
    if path.name.split(".")[2] in ("ledger-check", "synthesis-sections", "tone-check")
)


def run_python(*args, cwd=None, env=None):
    return subprocess.run(
        [sys.executable, str(PYTHON_CLI), *map(str, args)], cwd=cwd, env=env,
        capture_output=True, timeout=60,
    )


def parity(*args, cwd=None):
    if BASH is None:
        pytest.skip("Bash differential oracle unavailable; native contract tests still run")
    legacy = subprocess.run(
        [BASH, str(BASH_CLI), *map(str, args)], cwd=cwd,
        capture_output=True, timeout=60,
    )
    native = run_python(*args, cwd=cwd)
    assert (native.returncode, native.stdout, native.stderr) == (
        legacy.returncode, legacy.stdout, legacy.stderr,
    )
    return native


@pytest.mark.parametrize("payload", [
    b"", b"a", b"one\ntwo", b"one\r\ntwo\r\n", bytes(range(256)),
    b"\x00\xff\r\n" * 300000,
], ids=["empty", "unterminated", "partial-last-line", "crlf", "binary", "chunk-boundary"])
def test_native_byte_utilities_need_no_external_tools(tmp_path, payload):
    path = tmp_path / "-contráct with spaces.md"
    path.write_bytes(payload)
    env = dict(os.environ, PATH="", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    hashed = run_python("contract-hash", path.name, cwd=tmp_path, env=env)
    assert (hashed.returncode, hashed.stdout, hashed.stderr) == (0, (digest + "\n").encode(), b"")
    counted = run_python("state-lines", path.name, cwd=tmp_path, env=env)
    lf_count = payload.count(b"\n")
    assert (counted.returncode, counted.stdout, counted.stderr) == (
        0, f"{lf_count}\n".encode(), b"",
    )
    checked = run_python("contract-check", path.name, digest, cwd=tmp_path, env=env)
    assert (checked.returncode, checked.stdout, checked.stderr) == (0, b"OK: Contract unchanged.\n", b"")
    mismatch = run_python("contract-check", path.name, "wrong", cwd=tmp_path, env=env)
    assert (mismatch.returncode, mismatch.stderr) == (1, b"")
    assert mismatch.stdout == (
        "WARNING: Contract has been modified since intake.\n"
        "  Expected: wrong\n"
        f"  Actual:   {digest}\n"
        "  If this was intentional (author-requested contract revision), update the\n"
        "  contract_hash in Diagnostic_State.meta.json. If unintentional, investigate.\n"
    ).encode()


@pytest.mark.parametrize("payload", [b"", b"no newline", b"a\r\nb\nend", bytes(range(256))])
def test_byte_utilities_differential(tmp_path, payload):
    path = tmp_path / "-contráct with spaces.md"
    path.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    for args in (
        ("contract-hash", path.name), ("contract-hash", path.name, "ignored"),
        ("state-lines", path.name), ("state-lines", path.name, "ignored"),
        ("contract-check", path.name, digest), ("contract-check", path.name, digest, "ignored"),
        ("contract-check", path.name, digest.upper()), ("contract-check", path.name, ""),
    ):
        parity(*args, cwd=tmp_path)


@pytest.mark.parametrize("command", UTILITIES)
def test_migrated_self_tests_have_identical_output(command):
    result = run_python(command, "--self-test", "ignored")
    assert result.returncode == 0
    assert result.stdout.endswith(b"Self-test: PASS\n")
    if BASH is not None:
        parity(command, "--self-test", "ignored")


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda path: path.name)
def test_shipped_fixture_parity(fixture):
    command = fixture.name.split(".")[2]
    result = run_python(command, fixture)
    assert result.returncode == (0 if ".pass." in fixture.name else 1)
    if BASH is not None:
        parity(command, fixture)


@pytest.mark.parametrize("command", UTILITIES)
def test_missing_arguments_and_wrong_path_types(tmp_path, command):
    valid = tmp_path / "file.md"
    valid.write_bytes(b"body\n")
    if command == "artifact-names":
        invalid_args = [(), (str(tmp_path),), (str(tmp_path), "Project"),
                        (str(valid), "Project", "run"), ("missing", "Project", "run")]
    elif command == "contract-check":
        invalid_args = [(), (str(valid),), ("missing", "expected"), (str(tmp_path), "expected")]
    else:
        invalid_args = [(), ("missing",), (str(tmp_path),)]
    for args in invalid_args:
        native = run_python(command, *args, cwd=tmp_path)
        assert native.returncode == 2
        if BASH is not None:
            parity(command, *args, cwd=tmp_path)


def test_artifact_naming_literal_project_and_runlabel(tmp_path):
    (tmp_path / "Prój_Pass1_Reader_Experience_r1.md").write_bytes(b"")
    result = parity("artifact-names", tmp_path, "Prój", "r1", "ignored")
    assert result.returncode == 0
    (tmp_path / "Prój_Pass2_Structure_WRONG.md").write_bytes(b"")
    assert parity("artifact-names", tmp_path, "Prój", "r1").returncode == 1


@pytest.mark.parametrize("command", ["ledger-check", "synthesis-sections", "tone-check"])
def test_letter_wrappers_ignore_extra_arguments(tmp_path, command):
    path = tmp_path / "letter.md"
    path.write_text("# Letter\nThe pacing needs work.\n", encoding="utf-8")
    parity(command, path, "ignored", "also ignored")


@pytest.mark.parametrize("command", ["--self-test-all", "--check-canonical", "--check-all", "severity-floor", "bogus"])
def test_unported_entrypoints_do_not_claim_success(command):
    result = run_python(command)
    assert result.returncode == 2
    assert b"Partial migration:" in result.stdout
    assert result.stderr == b""
