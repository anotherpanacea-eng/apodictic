"""CB-1(a) utility behavior and exact-byte Bash/Python differential harness.

Bash stays an independent oracle during the migration. Native byte-contract tests
also run on hosts with no Bash or external hash/count tools.
"""

import hashlib
import os
import re
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
    legacy_stdout = legacy.stdout
    if args[0] == "state-lines" and re.fullmatch(rb"[ \t]*[0-9]+\n", legacy_stdout):
        # Bash counts with the host `wc -l`; BSD/macOS `wc` left-pads the number.
        legacy_stdout = legacy_stdout.lstrip(b" \t")
    assert (native.returncode, native.stdout, native.stderr) == (
        legacy.returncode, legacy_stdout, legacy.stderr,
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


def input_args(command, path):
    if command == "artifact-names":
        return command, path, "Project", "r1"
    if command == "contract-check":
        return command, path, "expected"
    return command, path


@pytest.mark.parametrize("command", UTILITIES)
def test_invalid_path_components_are_named_usage_errors(tmp_path, command):
    (tmp_path / "file.md").write_bytes(b"body\n")
    for path in ("x" * 256, "file.md/", "file.md/."):
        args = input_args(command, path)
        native = run_python(*args, cwd=tmp_path)
        kind = "Directory" if command == "artifact-names" else "File"
        assert (native.returncode, native.stdout, native.stderr) == (
            2, b"", f"Error: {kind} not found: {path}\n".encode(),
        )
        if BASH is not None:
            parity(*args, cwd=tmp_path)


@pytest.mark.skipif(os.name == "nt", reason="POSIX directory search permission regression")
@pytest.mark.parametrize("command", UTILITIES)
def test_inaccessible_parent_is_a_named_usage_error(tmp_path, command):
    parent = tmp_path / "denied"
    parent.mkdir()
    path = parent / "file.md"
    path.write_bytes(b"body\n")
    parent.chmod(0)
    try:
        if os.access(parent, os.X_OK):
            pytest.skip("host account can search mode-000 directories")
        args = input_args(command, "denied/file.md")
        native = run_python(*args, cwd=tmp_path)
        kind = "Directory" if command == "artifact-names" else "File"
        assert (native.returncode, native.stdout, native.stderr) == (
            2, b"", f"Error: {kind} not found: denied/file.md\n".encode(),
        )
        if BASH is not None:
            parity(*args, cwd=tmp_path)
    finally:
        parent.chmod(0o700)


@pytest.mark.skipif(os.name == "nt", reason="POSIX regular-file read permission regression")
@pytest.mark.parametrize("command", ["contract-hash", "contract-check", "state-lines"])
def test_unreadable_regular_file_is_a_read_failure(tmp_path, command):
    path = tmp_path / "blocked.md"
    path.write_bytes(b"body\n")
    path.chmod(0)
    try:
        if os.access(path, os.R_OK):
            pytest.skip("host account can read mode-000 files")
        args = input_args(command, "blocked.md")
        native = run_python(*args, cwd=tmp_path)
        assert (native.returncode, native.stdout) == (1, b"")
        assert native.stderr.startswith(b"Error: Cannot read file: blocked.md: ")
        assert b"Traceback" not in native.stderr
        if BASH is not None:
            legacy = subprocess.run(
                [BASH, str(BASH_CLI), *args], cwd=tmp_path,
                capture_output=True, timeout=60,
            )
            # Shell read-redirection stderr includes platform paths/line numbers.
            assert (legacy.returncode, legacy.stdout) == (native.returncode, native.stdout)
            assert legacy.stderr
    finally:
        path.chmod(0o600)


@pytest.mark.parametrize("command", UTILITIES)
def test_usage_preserves_literal_relative_invocation(command):
    python_path = "./plugins/apodictic/scripts/validate.py"
    native = subprocess.run(
        [sys.executable, python_path, command], cwd=ROOT, capture_output=True, timeout=60,
    )
    assert native.returncode == 2
    assert native.stdout.startswith(b"Usage: ./plugins/apodictic/scripts/validate.sh ")
    if BASH is not None:
        legacy = subprocess.run(
            [BASH, python_path[:-3] + ".sh", command], cwd=ROOT,
            capture_output=True, timeout=60,
        )
        assert (native.returncode, native.stdout, native.stderr) == (
            legacy.returncode, legacy.stdout, legacy.stderr,
        )


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
