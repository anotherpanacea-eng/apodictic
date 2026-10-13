"""CB-1(a) utility behavior and exact-byte Bash/Python differential harness.

Bash stays an independent oracle during the migration. Native byte-contract tests
also run on hosts with no Bash or external hash/count tools.
"""

import hashlib
import json
import os
from pathlib import Path
import re
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
STRUCTURED_INTEGRITY = (
    "structured-findings", "softness-check", "deficit-lock", "artifacts-schema",
    "finding-trace", "feedback-triage", "editor-scaffolding", "diagnostic-vocabulary",
)
RUN_INTEGRITY = (
    "escalation-check", "dispatch-record", "disposition-check", "synthesis-coverage", "specificity-floor",
)
PLANNING_DIFFS = ("retcon-plan", "state-card-diff", "revision-arc", "regression-diff")
REFUTATION = ("refutation-coverage", "refutation-evidence", "refutation-write-scope")
REFERENCES = SCRIPTS.parent / "skills/core-editor/references"
BASH = shutil.which("bash")


def fixture_command(path):
    if path.name.startswith("sf."):
        return "structured-findings"
    return path.name.split(".")[2]


FIXTURES = sorted(
    path for path in (ROOT / "tests/fixtures/validators").iterdir()
    if path.is_file() and fixture_command(path) in (
        "ledger-check", "synthesis-sections", "tone-check", *LETTER_SIGNALS, *CONFIG_TIMELINES, *STRUCTURED_INTEGRITY,
    )
)


def run_python(*args, cwd=None, env=None):
    return subprocess.run(
        [sys.executable, str(PYTHON_CLI), *map(str, args)], cwd=cwd, env=env,
        capture_output=True, timeout=60,
    )


def parity(*args, cwd=None, env=None):
    if BASH is None:
        pytest.skip("Bash differential oracle unavailable; native contract tests still run")
    legacy = subprocess.run(
        [BASH, str(BASH_CLI), *map(str, args)], cwd=cwd, env=env,
        capture_output=True, timeout=60,
    )
    native = run_python(*args, cwd=cwd, env=env)
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


@pytest.mark.parametrize("command", UTILITIES + LETTER_SIGNALS + CONFIG_TIMELINES + STRUCTURED_INTEGRITY + RUN_INTEGRITY + PLANNING_DIFFS + REFUTATION)
def test_migrated_self_tests_have_identical_output(command):
    result = run_python(command, "--self-test", "ignored")
    assert result.returncode == 0
    assert result.stdout.endswith(b"Self-test: PASS\n")
    if BASH is not None:
        parity(command, "--self-test", "ignored")
    if command in ("specificity-floor", *REFUTATION):
        assert b"Error: cannot read" not in result.stdout


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda path: path.name)
def test_shipped_fixture_parity(fixture):
    command = fixture_command(fixture)
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


@pytest.mark.parametrize("command", ["--self-test-all", "--check-canonical", "--check-all", "legal-risk", "bogus"])
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


def native_and_optional_parity(*args, cwd=None, env=None):
    if BASH is not None:
        return parity(*args, cwd=cwd, env=env)
    return run_python(*args, cwd=cwd, env=env)


@pytest.mark.parametrize("command", ["specificity-floor", *REFUTATION])
@pytest.mark.parametrize("temp_name", ["PASS-cache", "BYPASS-cache", "line\nbreak"])
def test_negative_self_test_diagnostics_ignore_valid_temp_root_text(tmp_path, command, temp_name):
    temp_root = tmp_path / temp_name
    try:
        temp_root.mkdir()
    except OSError:
        if "\n" in temp_name:
            pytest.skip("Host forbids newline directory names")
        raise
    env = dict(os.environ, TMPDIR=str(temp_root), TEMP=str(temp_root), TMP=str(temp_root))
    result = native_and_optional_parity(command, "--self-test", env=env)
    assert result.stderr == b""
    if command == "specificity-floor":
        assert b"non_utf8_letter_fails_closed: OK\n" in result.stdout
        assert b"non_utf8_ledger_fails_closed: OK\n" in result.stdout
        assert result.returncode == 0
    else:
        assert b"non_utf8_coverage_cli_degrades: OK\n" in result.stdout
        if "\n" in temp_name:
            # The shared suite's separate synthetic JSON still embeds a newline
            # path unescaped. Preserve that inherited failure outside this repair.
            assert result.returncode == 1
            assert b"v2_absolute_snapshot_path_refused: FAIL" in result.stdout
            assert result.stdout.endswith(b"Self-test: FAIL\n")
            return
        assert result.returncode == 0
    assert result.stdout.endswith(b"Self-test: PASS\n")


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


@pytest.mark.parametrize("command", STRUCTURED_INTEGRITY)
def test_structured_integrity_empty_arguments_and_flags_only(command):
    assert native_and_optional_parity(command).returncode == 2
    result = native_and_optional_parity(command, "--strict")
    assert result.returncode == (1 if command == "structured-findings" else 2)


@pytest.mark.parametrize("command,inputs", [
    ("structured-findings", ("diagnostic-state-meta-template.json", "findings-ledger-format.md")),
    ("softness-check", ("example-editorial-letter.md", "example-findings-ledger.md")),
    ("deficit-lock", ("example-findings-ledger.md",)),
    ("finding-trace", ("example-findings-ledger.md", "example-editorial-letter.md")),
    ("feedback-triage", ("example-feedback-triage.md", "example-findings-ledger.md", "--strict")),
    ("editor-scaffolding", ("example-editorial-letter-scaffolded.md",)),
    ("diagnostic-vocabulary", ("example-vocabulary-guide.md",)),
])
def test_native_structured_integrity_canonical_inputs(command, inputs):
    args = [path if path.startswith("--") else REFERENCES / path for path in inputs]
    result = native_and_optional_parity(command, *args)
    assert (result.returncode, result.stderr) == (0, b"")


def test_structured_findings_raw_argv_and_all_file_errors(tmp_path):
    clean = tmp_path / "plain.md"
    clean.write_text("# Plain file\n", encoding="utf-8")
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{", encoding="utf-8")
    result = native_and_optional_parity("structured-findings", clean, invalid, "missing.md")
    assert result.returncode == 1
    assert b"invalid JSON" in result.stdout and b"cannot read" in result.stdout
    late_test = native_and_optional_parity("structured-findings", clean, "--self-test")
    assert late_test.returncode == 1
    assert b"Self-test:" not in late_test.stdout
    assert b"--self-test: cannot read" in late_test.stdout
    native_and_optional_parity("structured-findings", "--self-test", "ignored")


@pytest.mark.parametrize("command", ["softness-check", "deficit-lock"])
def test_honesty_wrapper_arity_extras_and_read_errors(tmp_path, command):
    letter = REFERENCES / "example-editorial-letter.md"
    ledger = REFERENCES / "example-findings-ledger.md"
    valid = (letter, ledger) if command == "softness-check" else (ledger,)
    assert native_and_optional_parity(command, *valid, "--self-test", "ignored").returncode == 0
    assert native_and_optional_parity(command, "missing.md", *valid[1:]).returncode == 2
    bad = tmp_path / "bad.md"
    bad.write_bytes(b"\xff\xfe")
    invalid = (bad, ledger) if command == "softness-check" else (bad,)
    unreadable = native_and_optional_parity(command, *invalid)
    assert (unreadable.returncode, unreadable.stderr) == (2, b"")
    assert unreadable.stdout.startswith(b"Error: ")
    if command == "softness-check":
        assert native_and_optional_parity(command, letter).returncode == 2
        assert native_and_optional_parity(command, letter, "--self-test").returncode == 2


@pytest.mark.parametrize("args", [("file.md",), ("file.md", "--self-test"), ("--strict", "--self-test")])
def test_schema_module_surface_refuses_nonfirst_self_test(args):
    result = native_and_optional_parity("artifacts-schema", *args)
    assert (result.returncode, result.stderr) == (2, b"")
    assert result.stdout.startswith(b"Usage: ")


@pytest.mark.parametrize("command", ["finding-trace", "feedback-triage", "editor-scaffolding", "diagnostic-vocabulary"])
def test_helper_owned_late_self_test_and_command_token_filtering(command):
    late = native_and_optional_parity(command, "--strict", "--self-test", "ignored.md")
    assert late.returncode == 0
    assert late.stdout.endswith(b"Self-test: PASS\n")
    filtered = native_and_optional_parity(command, command, "--strict", "--unknown")
    assert filtered.returncode == 2
    assert filtered.stdout.startswith(b"Usage: ")


@pytest.mark.parametrize("flags,inputs", [
    (("--dual",), ("example-editorial-letter-scaffolded.md", "example-editorial-letter-dual-author.md")),
    (("--dual", "--per-pass"), ("example-editorial-letter-scaffolded.md", "example-editorial-letter-dual-author.md")),
    (("--per-pass", "--strict"), ("example-pass-scaffolded.md",)),
    (("--strict",), ("example-blindspot-ranked",)),
])
def test_editor_modes_keep_helper_precedence_and_canonical_contract(flags, inputs):
    assert native_and_optional_parity("editor-scaffolding", *flags, *(REFERENCES / path for path in inputs)).returncode == 0


@pytest.mark.parametrize("flag,count", [("--dual", 1), ("--dual", 3), ("--per-pass", 2)])
def test_editor_mode_arity_is_owned_by_helper(flag, count):
    path = REFERENCES / "example-editorial-letter-scaffolded.md"
    result = native_and_optional_parity("editor-scaffolding", flag, *([path] * count))
    assert result.returncode == 2
    assert b"need exactly" in result.stdout


@pytest.mark.parametrize("command,source,filename,invalid", [
    ("feedback-triage", "example-feedback-triage.md", "Demo_Feedback_Triage_r1.md",
     "<!-- apodictic:feedback_item\n{\n-->\n"),
    ("editor-scaffolding", "example-editorial-letter-scaffolded.md", "Demo_Editorial_Letter_r1.md",
     "<!-- mode: editor-scaffolding -->\n# Wrong\n"),
    ("diagnostic-vocabulary", "example-vocabulary-guide.md", "Demo_Vocabulary_Guide_r1.md", "# Missing mode\n"),
])
def test_run_folder_resolution_and_newest_file_selection(tmp_path, command, source, filename, invalid):
    path = tmp_path / filename
    path.write_bytes((REFERENCES / source).read_bytes())
    # Supply the optional ledger in the same folder for cross-artifact consumers.
    (tmp_path / "Demo_Findings_Ledger_r1.md").write_bytes((REFERENCES / "example-findings-ledger.md").read_bytes())
    os.utime(path, (100, 100))
    assert native_and_optional_parity(command, tmp_path).returncode == 0
    newer = tmp_path / filename.replace("r1", "r2")
    newer.write_bytes(path.read_bytes())
    path.write_text(invalid, encoding="utf-8")
    os.utime(path, (100, 100))
    os.utime(newer, (200, 200))
    assert native_and_optional_parity(command, tmp_path, "--strict").returncode == 0
    newer.unlink()
    assert native_and_optional_parity(command, tmp_path, "--strict").returncode == 1


def test_finding_trace_folder_and_bounded_sidecar_discovery(tmp_path):
    root = tmp_path / "project"
    run = root / "runs/current"
    run.mkdir(parents=True)
    ledger = run / "Demo_Findings_Ledger_r1.md"
    letter = run / "Demo_Editorial_Letter_r1.md"
    ledger.write_bytes((REFERENCES / "example-findings-ledger.md").read_bytes())
    letter.write_bytes((REFERENCES / "example-editorial-letter.md").read_bytes())
    assert native_and_optional_parity("finding-trace", run).returncode == 0
    sidecar = root / "Diagnostic_State.meta.json"
    sidecar.write_text("{", encoding="utf-8")
    found = native_and_optional_parity("finding-trace", run)
    assert found.returncode == 1
    assert b"unparseable sidecar" in found.stdout
    sidecar.unlink()
    far = tmp_path / "Diagnostic_State.meta.json"
    far.write_text("{", encoding="utf-8")
    # Four examined directories include tmp_path for this run-folder depth.
    assert native_and_optional_parity("finding-trace", run).returncode == 1
    deeper = run / "nested"
    deeper.mkdir()
    (deeper / ledger.name).write_bytes(ledger.read_bytes())
    (deeper / letter.name).write_bytes(letter.read_bytes())
    # The same sidecar is now beyond the four examined directories.
    assert native_and_optional_parity("finding-trace", deeper).returncode == 0


@pytest.mark.parametrize("command", RUN_INTEGRITY)
def test_run_integrity_wrapper_arity_flags_and_late_self_test(command):
    assert native_and_optional_parity(command).returncode == 2
    assert native_and_optional_parity(command, "--strict", "--strict").returncode == 2
    assert native_and_optional_parity(command, command, "--unknown").returncode == 2
    late = native_and_optional_parity(command, "--strict", "--self-test", "ignored")
    assert late.returncode == 0
    assert late.stdout.endswith(b"Self-test: PASS\n")


@pytest.mark.parametrize("command,inputs", [
    ("escalation-check", ("example-run-folder",)),
    ("dispatch-record", ("example-run-folder-coverage", "--strict")),
    ("disposition-check", ("example-run-folder-dispositions", "--strict")),
    ("synthesis-coverage", ("example-run-folder-coverage", "--strict")),
    ("synthesis-coverage", ("example-run-folder-coverage-degraded", "--strict")),
    ("specificity-floor", ("example-regrounded-letter.md", "example-regrounded-ledger.md", "--strict")),
])
def test_native_run_integrity_canonical_inputs(command, inputs):
    args = [path if path.startswith("--") else REFERENCES / path for path in inputs]
    result = native_and_optional_parity(command, *args)
    assert (result.returncode, result.stderr) == (0, b"")


@pytest.mark.parametrize("command", ["gate", "gate-state"])
@pytest.mark.parametrize("args", [(), ("--self-test",), ("--strict", "--self-test")])
def test_gate_pair_is_explicitly_deferred_until_nested_children_ready(command, args):
    result = run_python(command, *args)
    assert (result.returncode, result.stderr) == (2, b"")
    assert b"Partial migration:" in result.stdout


def test_escalation_advisory_strict_and_sidecar_discovery(tmp_path):
    run = tmp_path / "runs/current"
    run.mkdir(parents=True)
    sidecar = tmp_path / "Diagnostic_State.meta.json"
    sidecar.write_text(json.dumps({
        "last_session": {"execution_mode": "sequential"},
        "complexity_signals": {"pov_count": 4},
    }), encoding="utf-8")
    for path in (run, sidecar):
        advisory = native_and_optional_parity("escalation-check", path)
        assert advisory.returncode == 0
        assert b"RECOMMEND escalate sequential -> hybrid" in advisory.stdout
        assert native_and_optional_parity("escalation-check", "--strict", path).returncode == 1


def test_dispatch_report_ordering_and_ignored_normal_extras(tmp_path):
    folder = REFERENCES / "example-run-folder-coverage"
    assert native_and_optional_parity("dispatch-record", folder, "ignored", "--strict").returncode == 0
    assert native_and_optional_parity("dispatch-record", "--report", tmp_path).returncode == 0
    assert native_and_optional_parity("dispatch-record", "--report").returncode == 2
    # The report branch removes only --report before choosing its first token.
    # It deliberately does not share normal-mode positional flag filtering.
    for args in (("--strict", "--report", tmp_path), ("--report", "--strict", tmp_path)):
        result = native_and_optional_parity("dispatch-record", *args, cwd=tmp_path)
        assert result.returncode == 2
        assert b"not a directory: --strict" in result.stdout


def test_dispatch_model_tag_default_and_invalid_local_table(tmp_path):
    sidecar = tmp_path / "Diagnostic_State.meta.json"
    sidecar.write_bytes((REFERENCES / "example-run-folder-coverage/Diagnostic_State.meta.json").read_bytes())
    # A local table overrides the shipped source; zero parsed rows must refuse.
    (tmp_path / "output-structure.md").write_text("# No model table\n", encoding="utf-8")
    refused = native_and_optional_parity("dispatch-record", tmp_path)
    assert refused.returncode == 2
    assert b"model-tag-table-unparseable" in refused.stdout
    (tmp_path / "output-structure.md").unlink()
    # Falls back to the shipped model table; the R2 growth warning is not promoted.
    assert native_and_optional_parity("dispatch-record", tmp_path).returncode == 0
    assert native_and_optional_parity("dispatch-record", tmp_path, "--strict").returncode == 0
    # Present-but-empty dispatch_log is an R1 warning promoted by --strict.
    sidecar.write_text('{"dispatch_log": []}', encoding="utf-8")
    assert native_and_optional_parity("dispatch-record", tmp_path).returncode == 0
    assert native_and_optional_parity("dispatch-record", tmp_path, "--strict").returncode == 1


def test_disposition_sidecar_classification_and_bad_shape(tmp_path):
    sidecar = tmp_path / "Diagnostic_State.meta.json"
    sidecar.write_text("{", encoding="utf-8")
    for path in (sidecar, tmp_path):
        invalid = native_and_optional_parity("disposition-check", path, "--strict")
        assert invalid.returncode == 1
    assert native_and_optional_parity("disposition-check", "missing.json").returncode == 1


def test_synthesis_exact_directory_arity_and_advisory_strict(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    assert native_and_optional_parity("synthesis-coverage", empty).returncode == 0
    strict_empty = native_and_optional_parity("synthesis-coverage", empty, "--strict")
    assert strict_empty.returncode == 0
    assert b"no coverage obligation" in strict_empty.stdout
    # A real full letter creates a manifest obligation; missing manifest is advisory.
    source = REFERENCES / "example-run-folder-coverage"
    letter = next(source.glob("*_Core_DE_Synthesis_*.md"))
    (empty / letter.name).write_bytes(letter.read_bytes())
    assert native_and_optional_parity("synthesis-coverage", empty).returncode == 0
    assert native_and_optional_parity("synthesis-coverage", empty, "--strict").returncode == 1
    for args in (("missing",), (empty, empty), (REFERENCES / "example-editorial-letter.md",)):
        assert native_and_optional_parity("synthesis-coverage", *args).returncode == 2


def test_specificity_exact_file_arity_and_read_refusal(tmp_path):
    letter = REFERENCES / "example-regrounded-letter.md"
    ledger = REFERENCES / "example-regrounded-ledger.md"
    for args in ((letter,), (letter, ledger, letter), ("missing.md", ledger), (tmp_path, ledger)):
        assert native_and_optional_parity("specificity-floor", *args).returncode == 2
    bad = tmp_path / "bad.md"
    bad.write_bytes(b"\xff\xfe")
    for args in ((bad, ledger), (letter, bad)):
        result = native_and_optional_parity("specificity-floor", *args)
        assert (result.returncode, result.stderr) == (2, b"")
        assert b"Error: cannot read" in result.stdout


@pytest.mark.parametrize("command", PLANNING_DIFFS)
def test_planning_wrapper_flags_and_late_self_test(command):
    assert native_and_optional_parity(command).returncode == 2
    assert native_and_optional_parity(command, command, "--strict", "--unknown").returncode == 2
    late = native_and_optional_parity(command, "--strict", "--self-test", "ignored")
    assert (late.returncode, late.stderr) == (0, b"")
    assert late.stdout.endswith(b"Self-test: PASS\n")


@pytest.mark.parametrize("command,count", [("refutation-coverage", 3), ("refutation-evidence", 1), ("refutation-write-scope", 2)])
def test_refutation_raw_wrapper_minimum(command, count):
    for argc in range(count):
        result = native_and_optional_parity(command, *(["missing"] * argc))
        assert (result.returncode, result.stderr) == (2, b"")
        assert result.stdout.startswith(b"Usage: ")


@pytest.mark.parametrize("command,inputs,expected", [
    ("retcon-plan", ("example-retcon-plan.md", "--strict"), 0),
    ("state-card-diff", ("example-state-card.md", "--strict"), 0),
    ("state-card-diff", ("example-state-card.md", "example-state-card-round2.md", "--strict", "ignored"), 0),
    ("revision-arc", ("example-revision-arc.md", "--strict"), 0),
    ("regression-diff", ("example-run-folder-r1", "example-run-folder-r2"), 0),
    ("regression-diff", ("--strict", "example-run-folder-r1", "example-run-folder-r2", "ignored"), 1),
    ("regression-diff", ("example-run-folder-r1", "--strict"), 0),
    ("regression-diff", ("example-run-folder-r1", "example-run-folder-r1"), 1),
    ("state-card-diff", ("example-state-card-round2.md", "example-state-card.md"), 1),
])
def test_native_planning_canonical_single_pair_and_strict(command, inputs, expected):
    args = [path if path.startswith("--") or path == "ignored" else REFERENCES / path for path in inputs]
    assert native_and_optional_parity(command, *args).returncode == expected


@pytest.mark.parametrize("command,glob_name,canonical,block", [
    ("retcon-plan", "Project_Retcon_Plan_r1.md", "example-retcon-plan.md", "retcon_item"),
    ("state-card-diff", "Project_State_Card_r1.md", "example-state-card.md", "state_card"),
    ("revision-arc", "Project_Revision_Arc_r1.md", "example-revision-arc.md", "revision_arc"),
])
def test_planning_newest_file_discovery_and_parsed_carrier(tmp_path, command, glob_name, canonical, block):
    folder = tmp_path / "run"
    folder.mkdir()
    old = folder / glob_name
    old.write_text(f"<!-- apodictic:{block}\n{{\n-->\n", encoding="utf-8")
    fresh = folder / glob_name.replace("r1", "r2")
    fresh.write_bytes((REFERENCES / canonical).read_bytes())
    os.utime(old, (100, 100))
    os.utime(fresh, (200, 200))
    assert native_and_optional_parity(command, folder, "--strict").returncode == 0
    os.utime(old, (300, 300))
    assert native_and_optional_parity(command, folder).returncode == 1
    if command != "state-card-diff":
        prose = tmp_path / "prose.md"
        prose.write_text(f"This prose names apodictic:{block} but carries no block.\n", encoding="utf-8")
        assert native_and_optional_parity(command, prose, fresh, "--strict").returncode == 0


def test_revision_arc_sibling_ledger_precedes_explicit_and_embedded(tmp_path):
    arc = tmp_path / "Project_Revision_Arc_r1.md"
    arc.write_bytes((REFERENCES / "example-revision-arc.md").read_bytes())
    assert native_and_optional_parity("revision-arc", arc, "--strict").returncode == 0
    sibling = tmp_path / "Project_Findings_Ledger_r1.md"
    sibling.write_bytes((REFERENCES / "example-regrounded-ledger.md").read_bytes())
    # The sibling ledger overrides both embedded findings and the explicit carrier.
    assert native_and_optional_parity("revision-arc", arc, REFERENCES / "example-revision-arc.md").returncode == 1


@pytest.mark.parametrize("command", PLANNING_DIFFS)
def test_planning_missing_and_non_utf8_inputs(tmp_path, command):
    assert native_and_optional_parity(command, tmp_path).returncode == 2
    assert native_and_optional_parity(command, tmp_path / "missing.md").returncode == 2
    bad = tmp_path / "bad.md"
    bad.write_bytes(b"\xff\xfe")
    result = native_and_optional_parity(command, bad)
    # Preserve the existing regression single-round zero-finding behavior.
    assert result.returncode == (0 if command == "regression-diff" else 2)


@pytest.fixture
def refutation_run(tmp_path):
    source = REFERENCES / "example-run-folder"
    paths = {}
    for key, suffix in (
        ("letter", "Core_DE_Synthesis"), ("ledger", "Findings_Ledger"),
        ("record", "Refutation_Record"), ("snapshot", "Manuscript_Snapshot"),
    ):
        original = source / f"Example_{suffix}_2026-01-01_opus46.md"
        paths[key] = tmp_path / original.name
        paths[key].write_bytes(original.read_bytes())
    return paths


def edit_artifact_block(path, kind, edit):
    text = path.read_text(encoding="utf-8")
    def replace(match):
        obj = json.loads(match[2])
        edit(obj)
        return match[1] + json.dumps(obj, ensure_ascii=False) + match[3]
    changed, count = re.subn(rf"(<!-- apodictic:{kind}\s*)(.*?)(\s*-->)", replace, text, count=1, flags=re.S)
    assert count == 1
    path.write_text(changed, encoding="utf-8")


def test_refutation_canonical_and_distinct_flag_positions(refutation_run):
    p = refutation_run
    assert native_and_optional_parity("refutation-coverage", p["letter"], p["ledger"], p["record"], "--self-test").returncode == 0
    assert native_and_optional_parity("refutation-write-scope", p["ledger"], p["record"], "--self-test").returncode == 0
    for args in ((p["record"],), ("--require-snapshot", p["record"]), (p["record"], p["snapshot"], "--require-snapshot", "ignored")):
        assert native_and_optional_parity("refutation-evidence", *args).returncode == 0
    # Refutation has no generic late-self-test, strict or command-token filtering.
    assert native_and_optional_parity("refutation-evidence", p["record"], "--self-test").returncode == 1
    assert native_and_optional_parity("refutation-evidence", "--strict", p["record"]).returncode == 2
    assert native_and_optional_parity("refutation-evidence", "refutation-evidence", p["record"]).returncode == 2
    assert native_and_optional_parity("refutation-evidence", "--require-snapshot").returncode == 2


def test_refutation_snapshot_missing_optional_required_and_run_shape(refutation_run):
    p = refutation_run
    p["snapshot"].unlink()
    # Core/full letter shape requires the implicit snapshot even without a flag.
    assert native_and_optional_parity("refutation-evidence", p["record"]).returncode == 1
    p["letter"].unlink()
    optional = native_and_optional_parity("refutation-evidence", p["record"])
    assert optional.returncode == 0
    assert b"VOID" in optional.stdout
    assert native_and_optional_parity("refutation-evidence", p["record"], "--require-snapshot").returncode == 1
    assert native_and_optional_parity("refutation-write-scope", p["ledger"], p["record"]).returncode == 0


@pytest.mark.parametrize("snapshot_path", ["../outside.md", "/outside.md"])
def test_refutation_implicit_snapshot_containment(refutation_run, snapshot_path):
    p = refutation_run
    edit_artifact_block(p["record"], "refutation", lambda obj: obj.update(snapshot_path=snapshot_path))
    for command, args in (("refutation-evidence", (p["record"],)), ("refutation-write-scope", (p["ledger"], p["record"]))):
        result = native_and_optional_parity(command, *args)
        assert result.returncode == 1
        assert b"refusing to read" in result.stdout


def test_refutation_symlink_snapshot_escape_is_refused(refutation_run, tmp_path):
    p = refutation_run
    outside = tmp_path.parent / (tmp_path.name + "-snapshot.md")
    outside.write_bytes(p["snapshot"].read_bytes())
    p["snapshot"].unlink()
    try:
        p["snapshot"].symlink_to(outside)
    except OSError:
        pytest.skip("Host cannot create symlinks; literal containment checks still run")
    for command, args in (("refutation-evidence", (p["record"],)), ("refutation-write-scope", (p["ledger"], p["record"]))):
        result = native_and_optional_parity(command, *args)
        assert result.returncode == 1
        assert b"containment" in result.stdout


def test_refutation_snapshot_hash_uses_unchanged_raw_bytes(refutation_run):
    p = refutation_run
    p["snapshot"].write_bytes(p["snapshot"].read_bytes().replace(b"\n", b"\r\n"))
    for args in ((p["record"],), (p["record"], p["snapshot"], "--require-snapshot")):
        result = native_and_optional_parity("refutation-evidence", *args)
        assert result.returncode == 1
        assert b"snapshot_sha256 mismatch" in result.stdout


@pytest.mark.parametrize("hostile", ["missing_survived", "fabricated_quote", "severity_write", "fabricated_budget"])
def test_refutation_hostile_records_are_blocking(refutation_run, hostile):
    p = refutation_run
    if hostile == "missing_survived":
        p["record"].write_text(re.sub(
            r"<!-- apodictic:refutation\s+.*?-->", "",
            p["record"].read_text(encoding="utf-8"), flags=re.S,
        ), encoding="utf-8")
        assert native_and_optional_parity("refutation-coverage", p["letter"], p["ledger"], p["record"]).returncode == 1
    elif hostile == "fabricated_quote":
        edit_artifact_block(p["record"], "refutation", lambda obj: obj.update(counter_evidence_quotes=["This quote is absent from the canonical snapshot."]))
        assert native_and_optional_parity("refutation-evidence", p["record"], p["snapshot"]).returncode == 1
    elif hostile == "severity_write":
        edit_artifact_block(p["record"], "refutation", lambda obj: obj.update(severity="Must-Fix"))
        assert native_and_optional_parity("refutation-write-scope", p["ledger"], p["record"]).returncode == 1
    else:
        edit_artifact_block(p["record"], "refutation_budget", lambda obj: obj.update(eligible=16, processed=15, bound=True))
        assert native_and_optional_parity("refutation-coverage", p["letter"], p["ledger"], p["record"]).returncode == 1
        assert native_and_optional_parity("refutation-evidence", p["record"]).returncode == 1


@pytest.mark.parametrize("command,role,label", [
    ("refutation-coverage", "letter", b"editorial letter"),
    ("refutation-coverage", "ledger", b"findings ledger"),
    ("refutation-coverage", "record", b"refutation record"),
    ("refutation-evidence", "record", b"refutation record"),
    ("refutation-write-scope", "ledger", b"findings ledger"),
    ("refutation-write-scope", "record", b"refutation record"),
])
def test_refutation_named_decode_error_is_byte_exact(refutation_run, command, role, label):
    p = refutation_run
    p[role].write_bytes(b"\xff\xfe")
    args = {
        "refutation-coverage": (p["letter"], p["ledger"], p["record"]),
        "refutation-evidence": (p["record"],),
        "refutation-write-scope": (p["ledger"], p["record"]),
    }[command]
    result = native_and_optional_parity(command, *args)
    assert (result.returncode, result.stderr) == (2, b"")
    assert result.stdout.startswith(b"Error: cannot read " + label + b" ")
