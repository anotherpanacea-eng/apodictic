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
LETTER_SIGNALS = (
    "author-facing-lint", "severity-floor", "audit-signal-propagation",
    "underdiagnosis-triggers", "ledger-consolidation", "decision-layer-check",
)
CONFIG_TIMELINES = (
    "quality-risk-triggers", "cost-floor", "audit-tier-criterion", "pass-header",
    "argument-recon-prerequisite", "timeline-diff", "timeline-arithmetic", "timeline-anchor-conflict",
)
REFERENCES = SCRIPTS.parent / "skills/core-editor/references"
BASH = shutil.which("bash")
FIXTURES = sorted(
    path for path in (ROOT / "tests/fixtures/validators").glob("*.md")
    if path.name.split(".")[2] in (
        "ledger-check", "synthesis-sections", "tone-check", *LETTER_SIGNALS, *CONFIG_TIMELINES,
    )
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


@pytest.mark.parametrize("command", UTILITIES + LETTER_SIGNALS + CONFIG_TIMELINES)
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


@pytest.mark.parametrize("command", ["--self-test-all", "--check-canonical", "--check-all", "structured-findings", "bogus"])
def test_unported_entrypoints_do_not_claim_success(command):
    result = run_python(command)
    assert result.returncode == 2
    assert b"Partial migration:" in result.stdout
    assert result.stderr == b""


@pytest.mark.parametrize("command", LETTER_SIGNALS)
def test_letter_signal_argument_forwarding_and_parser_owned_errors(tmp_path, command):
    primary = tmp_path / "input.md"
    primary.write_text("# Development Edit\n## What Needs Work\nClean prose.\n", encoding="utf-8")
    extra = tmp_path / "optional.md"
    extra.write_text("## Pass 1\n## Pass 2\n## Pass 3\n", encoding="utf-8")
    for args in (
        (), ("missing.md",), (str(tmp_path),), ("x" * 256,),
        ("input.md/",), ("--strict",), ("",),
        ("input.md",), ("input.md", "missing.md"),
        ("input.md", "optional.md", "ignored", "--strict"),
    ):
        native = run_python(command, *args, cwd=tmp_path)
        if not args or args[0] != "input.md":
            assert native.returncode == 2
        if BASH is not None:
            parity(command, *args, cwd=tmp_path)


@pytest.mark.parametrize("body, warns", [
    ("This is a Pass 11F problem and a QF-7 issue.\n", True),
    ("The consent-and-reception pass (Pass 11F) flagged weak motivation (QF-7).\n", False),
    ("<!-- override: author-facing-lint -->\nA Pass 11F / QF-7 note.\n", False),
    ("<!-- override: author-facing-lint-extra -->\nA Pass 11F / QF-7 note.\n", True),
    ("`<!-- override: author-facing-lint -->`\nA Pass 11F / QF-7 note.\n", True),
], ids=["advisory-warning", "gloss", "override", "suffix-decoy", "quoted-decoy"])
def test_native_author_lint_preserves_advisory_and_override_behavior(tmp_path, body, warns):
    path = tmp_path / "letter.md"
    path.write_text("# Development Edit\n## What Needs Work\n" + body, encoding="utf-8")
    native = run_python("author-facing-lint", path)
    assert (native.returncode, native.stderr) == (0, b"")
    assert (b"WARN:" in native.stdout) == warns
    if BASH is not None:
        parity("author-facing-lint", path)


def test_registry_defaults_and_explicit_argument_rules(tmp_path):
    refs = SCRIPTS.parent / "skills/core-editor/references"
    registry = refs / "audit-routing-table.md"
    dependencies = refs / "pass-dependencies.md"
    for args in (
        (), ("",), ("", "ignored-nonexistent-dependency.md"),
        (registry, dependencies), (registry, dependencies, "ignored"),
    ):
        native = run_python("audit-signal-propagation", "--check-registry", *args, cwd=tmp_path)
        assert native.returncode == 0
        assert native.stdout.startswith(b"Registry check: PASS (")
        assert native.stderr == b""
        if BASH is not None:
            parity("audit-signal-propagation", "--check-registry", *args, cwd=tmp_path)
    for args in ((registry,), (registry, ""), ("missing-reg.md", dependencies), (registry, tmp_path)):
        native = run_python("audit-signal-propagation", "--check-registry", *args, cwd=tmp_path)
        assert (native.returncode, native.stdout) == (2, b"")
        assert native.stderr.startswith(b"Error: registry or pass-dependencies file not found (")
        if BASH is not None:
            parity("audit-signal-propagation", "--check-registry", *args, cwd=tmp_path)


def test_registry_fragment_and_empty_registry(tmp_path):
    directory = tmp_path / "references"
    directory.mkdir()
    registry = directory / "registry.md"
    dependencies = directory / "dependencies.md"
    fragment = directory / "argument-audits-propagation.md"
    registry.write_text("<!-- registry:signal-emitting-audits:begin -->\n"
                        "- Example Audit\n<!-- registry:signal-emitting-audits:end -->\n",
                        encoding="utf-8")
    dependencies.write_text("# Dependencies\n", encoding="utf-8")

    def check(expected):
        # Explicit lexical ../ paths must remain untouched by wrapper probes.
        args = ("audit-signal-propagation", "--check-registry",
                "references/../references/registry.md", "references/../references/dependencies.md")
        native = run_python(*args, cwd=tmp_path)
        assert native.returncode == expected
        if BASH is not None:
            parity(*args, cwd=tmp_path)
        return native

    assert "no §4e propagation row".encode("utf-8") in check(1).stdout
    fragment.write_text("| Example Audit | hard gate | Must-Fix |\n", encoding="utf-8")
    assert check(0).stdout.startswith(b"Registry check: PASS (")
    registry.write_text("# No entries\n", encoding="utf-8")
    empty = check(2)
    assert empty.stdout == b""
    assert b"Error: no registry entries found in references/../references/registry.md" in empty.stderr


def native_and_optional_parity(*args, cwd=None):
    result = run_python(*args, cwd=cwd)
    if BASH is not None:
        parity(*args, cwd=cwd)
    return result


@pytest.mark.parametrize("command", CONFIG_TIMELINES)
def test_config_timeline_arity_and_invalid_primary_paths(tmp_path, command):
    for args in ((), ("missing.md",), ("",), ("x" * 256,), ("--strict",)):
        result = native_and_optional_parity(command, *args, cwd=tmp_path)
        assert result.returncode == 2
    if command == "timeline-diff":
        assert b" | --self-test" in run_python(command).stdout
        assert b" | --self-test" not in run_python(command, "prior-only.md").stdout


@pytest.mark.parametrize("command,inputs", [
    ("quality-risk-triggers", ("example-quality-risk-contract.md",)),
    ("cost-floor", ("example-cost-floor-contract.md", "example-cost-floor-preflight.md")),
    ("audit-tier-criterion", ("pass-dependencies.md",)),
    ("pass-header", ("example-pass-artifact-header.md", "pass-dependencies.md")),
    ("argument-recon-prerequisite", ("example-run-folder",)),
    ("timeline-diff", ("example-timeline.md", "example-timeline.md")),
    ("timeline-arithmetic", ("example-timeline.md",)),
    ("timeline-anchor-conflict", ("example-timeline.md",)),
])
def test_native_configuration_and_timeline_canonical_inputs(command, inputs):
    result = native_and_optional_parity(command, *(REFERENCES / path for path in inputs))
    assert (result.returncode, result.stderr) == (0, b"")


def test_quality_risk_optional_metadata_and_ignored_extras(tmp_path):
    contract = tmp_path / "contract.md"
    contract.write_text("GENRE/SUBGENRE: Literary fiction\nPOV count: 1\nGOAL: repair\n", encoding="utf-8")
    meta = tmp_path / "meta.json"
    meta.write_text('{"underdiagnosis_flag":"fired"}', encoding="utf-8")
    for extra in ((), ("missing.json",), ("",)):
        assert native_and_optional_parity("quality-risk-triggers", contract, *extra).returncode == 0
    fired = native_and_optional_parity("quality-risk-triggers", contract, meta, "ignored")
    assert fired.returncode == 1
    assert b"Q4" in fired.stdout


def test_cost_floor_strict_and_flag_filtering_preserve_argument_positions(tmp_path):
    contract = tmp_path / "-contract.md"
    contract.write_text("GENRE/SUBGENRE: Literary fiction\nPOV count: 1\nGOAL: repair\n"
                        "cost_floor_override: sequential — deliberate cap\n", encoding="utf-8")
    relaxed = native_and_optional_parity("cost-floor", contract, "missing-preflight.md", "missing-meta.json", "ignored")
    assert relaxed.returncode == 0
    assert b"WARN:" in relaxed.stdout
    for args in (
        ("--strict", contract), (contract, "--strict"),
        ("--unused", contract, "missing-preflight.md", "--strict", "missing-meta.json", "ignored"),
    ):
        assert native_and_optional_parity("cost-floor", *args).returncode == 1
    flags_only = native_and_optional_parity("cost-floor", "--unused", "--strict")
    assert (flags_only.returncode, flags_only.stdout) == (2, b"")
    assert flags_only.stderr.startswith(b"Usage: config_checks.py cost-floor ")


def test_audit_tier_default_root_and_explicit_root(tmp_path):
    root = tmp_path / "tree"
    refs = root / "core/references"
    refs.mkdir(parents=True)
    audits = root / "audits"
    audits.mkdir()
    dependencies = refs / "dependencies.md"
    dependencies.write_text("| Trigger | Example Audit | Auto-run | `audits/example.md` |\n", encoding="utf-8")
    audit = audits / "example.md"
    audit.write_text("# Example Audit\nNo floor defined.\n", encoding="utf-8")
    for extra in ((), ("",), (root, "ignored")):
        assert native_and_optional_parity("audit-tier-criterion", dependencies, *extra).returncode == 1
    audit.write_text("# Example Audit\n## Hard Gates\n", encoding="utf-8")
    assert native_and_optional_parity("audit-tier-criterion", dependencies).returncode == 0
    missing = native_and_optional_parity("audit-tier-criterion", dependencies, "missing-root")
    assert missing.returncode == 0
    assert b"WARN:" in missing.stdout


def test_pass_header_default_precedence_and_explicit_dependencies(tmp_path):
    artifact_dir = tmp_path / "install/output"
    artifact_dir.mkdir(parents=True)
    artifact = artifact_dir / "pass.md"
    artifact.write_bytes((REFERENCES / "example-pass-artifact-header.md").read_bytes())
    sibling = artifact_dir / "pass-dependencies.md"
    fallback = artifact_dir.parent / "skills/core-editor/references/pass-dependencies.md"
    fallback.parent.mkdir(parents=True)
    fallback.write_bytes((REFERENCES / "pass-dependencies.md").read_bytes())
    assert native_and_optional_parity("pass-header", artifact).returncode == 0
    sibling.write_text("# Invalid section 3\n", encoding="utf-8")
    assert native_and_optional_parity("pass-header", artifact).returncode == 2
    assert native_and_optional_parity("pass-header", artifact, fallback, "ignored").returncode == 0
    assert native_and_optional_parity("pass-header", artifact, "missing-dependencies.md").returncode == 2


def test_recon_prerequisite_autodiscovery_and_optional_letter(tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    assert native_and_optional_parity("argument-recon-prerequisite", run).returncode == 0
    (run / "Argument_State.md").write_text("# State\n", encoding="utf-8")
    assert native_and_optional_parity("argument-recon-prerequisite", run).returncode == 1
    clean = run / "A_Editorial_Letter.md"
    disclosed = run / "Z_Editorial_Letter.md"
    clean.write_text("# Letter\nClean prose.\n", encoding="utf-8")
    disclosed.write_text("# Letter\nliterature-counterevidence not surveyed\n", encoding="utf-8")
    assert native_and_optional_parity("argument-recon-prerequisite", run).returncode == 1
    assert native_and_optional_parity("argument-recon-prerequisite", run, disclosed, "ignored").returncode == 0
    assert native_and_optional_parity("argument-recon-prerequisite", run, "missing-letter.md").returncode == 1
    (run / "Field_Reconnaissance_Report.md").write_text("# Recon\n", encoding="utf-8")
    assert native_and_optional_parity("argument-recon-prerequisite", run).returncode == 0


def test_timeline_diff_pair_order_and_body_override(tmp_path):
    prior = tmp_path / "prior.md"
    current = tmp_path / "current.md"
    text = ("# Timeline\n## Section 1: Event Ledger\n| Scene ID | Anchor text | Span |\n"
            "|---|---|---|\n| Ch 1 §1 | Monday morning | 3 hours |\n"
            "## Section 8: Diff Notes\nn/a.\n")
    prior.write_text(text, encoding="utf-8")
    current.write_text(text.replace("Monday morning", "Tuesday morning"), encoding="utf-8")
    for args in ((prior, current), (current, prior), (prior, current, "ignored", "--strict")):
        assert native_and_optional_parity("timeline-diff", *args).returncode == 1
    current.write_text(current.read_text(encoding="utf-8").replace(
        "# Timeline\n", "# Timeline\n<!-- override: timeline-diff-undocumented — deferred -->\n"), encoding="utf-8")
    assert native_and_optional_parity("timeline-diff", prior, current).returncode == 0
    assert native_and_optional_parity("timeline-diff", prior, "missing.md").returncode == 2
