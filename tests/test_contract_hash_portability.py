"""Actual contract CLI digests and fail-closed provider selection.

Successful providers delegate to an installed digest utility. When a host lacks
one interface, its adapter exercises selection, not native platform qualification.
"""

import hashlib
import os
from pathlib import Path
import shlex
import shutil
import subprocess

import pytest


VALIDATOR = Path(__file__).resolve().parents[1] / "scripts/validate.sh"


def shell_path(path):
    text = Path(path).resolve().as_posix()
    if os.name == "nt":
        return "/" + text[0].lower() + text[2:]
    return text


@pytest.fixture
def cli(tmp_path):
    bash = os.environ.get("TEST_BASH") or shutil.which("bash")
    if os.name == "nt" and not os.environ.get("TEST_BASH"):
        candidate = Path("C:/Program Files/Git/usr/bin/bash.exe")
        if candidate.exists():
            bash = str(candidate)
    if not bash:
        pytest.skip("contract CLI tests require Bash and standard Unix utilities")

    def locate(name):
        found = subprocess.run(
            [bash, "-c", f"PATH=/usr/bin:/bin:$PATH; command -v {name}"],
            capture_output=True, text=True, check=False,
        )
        return found.stdout.strip() if found.returncode == 0 else None

    real = {name: locate(name) for name in ("bash", "dirname", "awk", "shasum", "sha256sum")}
    if not all(real[name] for name in ("bash", "dirname", "awk")) or not (
        real["shasum"] or real["sha256sum"]
    ):
        pytest.skip("contract CLI tests require Unix utilities and a real SHA-256 provider")
    bin_dir = tmp_path / "isolated bin"
    bin_dir.mkdir()
    env = os.environ.copy()
    # Deliberately exclude the host PATH so absence and preference are observable.
    env["PATH"] = shell_path(bin_dir)

    def command(name, body):
        path = bin_dir / name
        path.write_text("#!" + real["bash"] + "\n" + body + "\n", encoding="utf-8", newline="\n")
        path.chmod(0o755)

    for name in ("bash", "dirname", "awk"):
        command(name, f"exec {shlex.quote(real[name])} \"$@\"")

    def provider(name):
        if real[name]:
            body = f"exec {shlex.quote(real[name])} \"$@\""
        elif name == "shasum":
            body = (
                '[ "$#" = 2 ] && [ "$1" = -a ] && [ "$2" = 256 ] || exit 90\n'
                f"exec {shlex.quote(real['sha256sum'])}"
            )
        else:
            body = f"exec {shlex.quote(real['shasum'])} -a 256 \"$@\""
        command(name, body)

    def run(*args):
        return subprocess.run(
            [bash, shell_path(VALIDATOR), *args],
            cwd=tmp_path, env=env, capture_output=True, text=True, timeout=20,
        )

    return tmp_path, provider, command, run


@pytest.mark.parametrize("provider_name", ["shasum", "sha256sum"])
@pytest.mark.parametrize("content", [b"", b"contract\r\nbytes\n", "Unchanged café: λ\n".encode()])
def test_digest_bytes_repeat_and_comparison(cli, provider_name, content):
    root, provider, _, run = cli
    provider(provider_name)
    path = root / "contract with spaces.md"
    path.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    for _ in range(2):
        result = run("contract-hash", shell_path(path))
        assert result.returncode == 0, result.stderr
        assert result.stdout == digest + "\n"
    assert run("contract-check", shell_path(path), digest).returncode == 0
    mismatch = run("contract-check", shell_path(path), "0" * 64)
    assert mismatch.returncode == 1
    assert "modified" in mismatch.stdout


@pytest.mark.parametrize("provider_name", ["shasum", "sha256sum"])
def test_leading_dash_filename_is_literal(cli, provider_name):
    root, provider, _, run = cli
    provider(provider_name)
    content = b"literal filename\n"
    (root / "-contract.md").write_bytes(content)
    result = run("contract-hash", "-contract.md")
    assert result.returncode == 0, result.stderr
    assert result.stdout == hashlib.sha256(content).hexdigest() + "\n"


def test_preferred_provider_is_used_when_both_exist(cli):
    root, provider, command, run = cli
    provider("shasum")
    # A selected fallback would fail, making preference an observable outcome.
    command("sha256sum", "exit 91")
    path = root / "contract.md"
    path.write_bytes(b"preference\n")
    result = run("contract-hash", shell_path(path))
    assert result.returncode == 0, result.stderr
    assert result.stdout == hashlib.sha256(path.read_bytes()).hexdigest() + "\n"


def test_no_provider_and_usage_precedence(cli):
    root, _, _, run = cli
    path = root / "contract.md"
    path.write_bytes(b"no supplier\n")
    for args in (("contract-hash", shell_path(path)), ("contract-check", shell_path(path), "")):
        result = run(*args)
        assert result.returncode == 127
        assert result.stdout == ""
        assert "SHA-256 tool" in result.stderr
    for args in (
        ("contract-hash",), ("contract-hash", "missing.md"),
        ("contract-check", shell_path(path)), ("contract-check", "missing.md", ""),
    ):
        assert run(*args).returncode == 2


@pytest.mark.parametrize("provider_name", ["shasum", "sha256sum"])
@pytest.mark.parametrize("emit_digest", [False, True])
def test_provider_failure_never_becomes_match_or_partial_digest(cli, provider_name, emit_digest):
    root, provider, command, run = cli
    path = root / "contract.md"
    path.write_bytes(b"provider failure\n")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if provider_name == "shasum":
        provider("sha256sum")  # A successful fallback must not mask a selected failure.
    output = f"printf '%s  -\\n' {shlex.quote(digest)}\n" if emit_digest else ""
    command(provider_name, output + "exit 73")
    result = run("contract-hash", shell_path(path))
    assert result.returncode == 73
    assert result.stdout == ""
    for expected in (digest, ""):
        result = run("contract-check", shell_path(path), expected)
        assert result.returncode == 73
        assert "unchanged" not in result.stdout
        assert "modified" not in result.stdout
