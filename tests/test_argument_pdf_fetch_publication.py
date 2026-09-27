"""Black-box fetch regressions; synthetic text and fake network/converter only."""

import hashlib
import os
from pathlib import Path
import shlex
import shutil
import subprocess

import pytest


RUNNER = Path(__file__).resolve().parents[1] / "evals/fixtures/argument-benchmark/run.sh"
BODY = b"Synthetic argument body.\n"
PRIOR = b"Previous cache content.\n"
DIGEST = hashlib.sha256(BODY).hexdigest()


def shell_path(path):
    text = Path(path).resolve().as_posix()
    if os.name == "nt":
        return "/" + text[0].lower() + text[2:]
    return text


@pytest.fixture
def harness(tmp_path):
    bash = os.environ.get("TEST_BASH") or shutil.which("bash")
    if os.name == "nt" and not os.environ.get("TEST_BASH"):
        candidate = Path("C:/Program Files/Git/usr/bin/bash.exe")
        if candidate.exists():
            bash = str(candidate)
    if not bash:
        pytest.skip("fetch regressions require Bash and standard Unix utilities")
    root = tmp_path / "synthetic repo"
    script = root / "evals/fixtures/argument-benchmark/run.sh"
    script.parent.mkdir(parents=True)
    shutil.copyfile(RUNNER, script)
    audit = root / "plugins/apodictic/skills/specialized-audits/references/craft/dialectical-clarity.md"
    audit.parent.mkdir(parents=True)
    audit.write_text("Synthetic reference; never dispatched.\n", encoding="utf-8")
    cache = root / "cache with spaces"
    cache.mkdir()
    scratch = root / "temp with spaces"
    scratch.mkdir()
    bin_dir = root / "bin"
    bin_dir.mkdir()

    def command(name, body):
        path = bin_dir / name
        path.write_text("#!/bin/bash\n" + body + "\n", encoding="utf-8", newline="\n")
        path.chmod(0o755)

    # An allowlisted PATH makes missing pdftotext deterministic and prevents real
    # curl/Claude calls. Wrappers still use actual core utilities for extraction.
    real = {}
    for name in ("awk", "dirname", "date", "mkdir", "head", "grep", "sed", "cut", "cat", "rm", "mv", "mktemp", "chmod", "bash"):
        found = subprocess.run([bash, "-c", f"PATH=/usr/bin:/bin:$PATH; command -v {name}"], capture_output=True, text=True, check=True).stdout.strip()
        real[name] = found
        command(name, f"exec {shlex.quote(found)} \"$@\"")
    hash_tool = subprocess.run([bash, "-c", "PATH=/usr/bin:/bin:$PATH; command -v sha256sum || command -v shasum"], capture_output=True, text=True, check=True).stdout.strip()
    hash_command = shlex.quote(hash_tool) + (" -a 256" if hash_tool.endswith("shasum") else "")
    command("curl", """
while [ "$#" -gt 0 ]; do
  if [ "$1" = -o ]; then shift; target="$1"; fi
  shift
done
printf 'Synthetic downloaded content.\n' > "$target"
[ "${FETCH_FAIL:-0}" = 0 ]
""")
    command("pdftotext", """
[ "$1" = -layout ] && [ "$2" = -q ] && [ -s "$3" ] || exit 19
case "${CONVERT_MODE:-ok}" in
  empty) : > "$4";;
  whitespace) printf ' \n\t\n' > "$4";;
  fail) printf 'Partial converted content.\n' > "$4"; exit 7;;
  signal) kill -TERM "$PPID"; exit 7;;
  *) printf 'Synthetic argument body.\n' > "$4";;
esac
""")
    command("mktemp", f"""
n=0
[ ! -f "$CASE_ROOT/count" ] || read -r n < "$CASE_ROOT/count"
n=$((n+1)); printf '%s\n' "$n" > "$CASE_ROOT/count"
[ "${{TEMP_FAIL:-0}}" != "$n" ] || exit 9
p="$({shlex.quote(real['mktemp'])} "$@")" || exit
printf '%s\n' "$p" >> "$CASE_ROOT/allocations"
printf '%s\n' "$p"
""")
    command("shasum", f"""
if [ "${{HASH_FAIL:-0}}" = 1 ]; then printf '{DIGEST}  -\n'; exit 8; fi
exec {hash_command}
""")
    command("mv", f"""
[ "${{MOVE_FAIL:-0}}" = 0 ] || exit 10
exec {shlex.quote(real['mv'])} "$@"
""")
    env = os.environ.copy()
    for name in ("STRIP_CMD", "BASH_ENV", "ENV", "SHELLOPTS", "BASHOPTS"):
        env.pop(name, None)
    env.update(PATH=shell_path(bin_dir), SRC=shell_path(cache), REPO=shell_path(root),
               TMPDIR=shell_path(scratch), CASE_ROOT=shell_path(root), LC_ALL="C")

    class Harness:
        def run(self, *, want=DIGEST, prior=True, pdf=True, batch=False, **overrides):
            suffix = "pdf" if pdf else "txt"
            # The parser requires at least one recorded digest, even when the
            # explicitly selected source has no digest of its own.
            metadata = f"### unused\n- **RECORDED:** sha256: {DIGEST}\n### sample\n- **URL:** https://synthetic.invalid/sample.{suffix}\n"
            if want is not None:
                metadata += f"- **RECORDED:** sha256: {want}\n"
            metadata += f"### second\n- **URL:** https://synthetic.invalid/second.pdf\n- **RECORDED:** sha256: {DIGEST}\n"
            (script.parent / "SOURCES.md").write_text(metadata, encoding="utf-8")
            if prior:
                self.dest.write_bytes(PRIOR)
            slugs = ["sample", "second"] if batch else ["sample"]
            result = subprocess.run([bash, shell_path(script), "--fetch", *slugs], env=env | overrides,
                                    capture_output=True, text=True, timeout=20)
            # Every returned mktemp path must be gone, including original PDF
            # input paths that older code lost when reassigning tmp to txt.
            allocations = root / "allocations"
            if allocations.exists():
                for allocated in allocations.read_text().splitlines():
                    if os.name == "nt" and allocated.startswith("/") and allocated[2:3] == "/":
                        allocated = allocated[1] + ":" + allocated[2:]
                    assert not Path(allocated).exists(), allocated
            assert not list(scratch.iterdir())
            assert not list(cache.glob(".argument-fetch.*"))
            return result

        def fails(self, **kwargs):
            result = self.run(**kwargs)
            assert result.returncode == 1, result.stdout + result.stderr
            assert self.dest.read_bytes() == PRIOR
            assert "OK    sample" not in result.stdout
            assert "GOT   sample" not in result.stdout
            return result

    h = Harness()
    h.dest = cache / "sample.md"
    h.command = command
    h.bin = bin_dir
    h.root = root
    return h


def test_matching_digest_publishes_exact_staged_bytes(harness):
    result = harness.run()
    assert result.returncode == 0, result.stderr
    assert harness.dest.read_bytes() == BODY
    assert "OK    sample" in result.stdout


@pytest.mark.parametrize("prior", [True, False])
def test_mismatch_preserves_destination_or_absence(harness, prior):
    result = harness.run(want="0" * 64, prior=prior)
    assert result.returncode == 1
    assert "HASH? sample" in result.stdout
    assert harness.dest.read_bytes() == PRIOR if prior else not harness.dest.exists()


def test_missing_converter_preserves_destination(harness):
    (harness.bin / "pdftotext").unlink()
    assert "pdftotext" in harness.fails().stdout


@pytest.mark.parametrize("mode", ["fail", "empty", "whitespace"])
def test_bad_conversion_preserves_destination(harness, mode):
    harness.fails(CONVERT_MODE=mode)


def test_fetch_failure_preserves_destination(harness):
    harness.fails(FETCH_FAIL="1")


@pytest.mark.parametrize("allocation", ["1", "2", "3"])
def test_each_allocation_failure_cleans_previous_temps(harness, allocation):
    harness.fails(TEMP_FAIL=allocation)


def test_partial_failed_extraction_is_not_published(harness):
    harness.fails(STRIP_CMD="printf 'Partial extraction.\\n'; exit 11")


@pytest.mark.parametrize("want", [DIGEST, None])
def test_hash_command_failure_is_not_a_verified_or_unverified_success(harness, want):
    harness.fails(want=want, HASH_FAIL="1")


def test_stage_write_failure_preserves_destination(harness):
    # Fault injection into Bash's write builtin; no production test seam.
    startup = harness.root / "fail-write.sh"
    startup.write_text(
        'case "$0" in */run.sh)\n'
        'printf() { if [ -f /dev/fd/1 ]; then return 12; fi; builtin printf "$@"; }\n'
        'esac\n', encoding="utf-8", newline="\n")
    result = harness.fails(BASH_ENV=shell_path(startup))
    assert "staging write failed" in result.stdout


def test_move_failure_preserves_destination(harness):
    harness.fails(MOVE_FAIL="1")


def test_no_expected_digest_publishes_explicitly_unverified(harness):
    result = harness.run(want=None)
    assert result.returncode == 0, result.stderr
    assert harness.dest.read_bytes() == BODY
    assert "GOT   sample" in result.stdout and "unverified" in result.stdout
    assert DIGEST in result.stdout


def test_non_pdf_uses_same_safe_publication_tail(harness):
    harness.fails(pdf=False, want="0" * 64)


def test_directory_destination_is_not_reported_as_published(harness):
    harness.dest.mkdir()
    result = harness.run(prior=False)
    assert result.returncode == 1
    assert list(harness.dest.iterdir()) == []
    assert "destination is a directory" in result.stdout


def test_batch_continues_after_failure_but_returns_failure(harness):
    result = harness.fails(want="0" * 64, batch=True)
    assert (harness.dest.parent / "second.md").read_bytes() == BODY
    assert "OK    second" in result.stdout


def test_interruption_cleans_owned_temps_and_stops_batch(harness):
    result = harness.run(batch=True, CONVERT_MODE="signal")
    assert result.returncode == 143, result.stdout + result.stderr
    assert harness.dest.read_bytes() == PRIOR
    assert not (harness.dest.parent / "second.md").exists()
    assert "second" not in result.stdout


@pytest.mark.skipif(os.name == "nt", reason="POSIX permission bits")
def test_published_text_follows_umask(harness):
    previous = os.umask(0o022)
    try:
        result = harness.run()
    finally:
        os.umask(previous)
    assert result.returncode == 0, result.stdout + result.stderr
    assert harness.dest.stat().st_mode & 0o777 == 0o644
