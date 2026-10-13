"""CB-1(a) utility behavior and exact-byte Bash/Python differential harness.

Bash stays an independent oracle during the migration. Native byte-contract tests
also run on hosts with no Bash or external hash/count tools.
"""

import hashlib
from datetime import datetime, timezone
import json
import math
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
ARTIFACT_PLANNING = (
    "legal-risk", "promise-contract", "continuity-bible", "setup-payoff",
    "world-bible", "argument-spine", "scene-ethics",
)
INTAKE_VOICE = (
    "intake-interview", "author-fingerprint", "content-advisory", "coaching-history",
    "style-explanation", "persona-divergence",
)
READER_MANUSCRIPT = (
    "lifecycle-node", "reader-instrument", "manuscript-viz", "annotated-manuscript",
    "crosslink", "reanchor", "roundtrip-disposition", "reader-contract-outline",
    "results-guide", "position-pair-register",
)
ARGUMENT_EVALUATORS = (
    "argument-groundtruth-check", "fiction-groundtruth-check", "agreement-alpha",
    "argument-crosswalk-check", "argument-agd", "argument-aif-export", "argument-aif-check",
)
ANNOTATION_EXPORTS = ("obsidian-export", "html-export", "docx-export", "pdf-export")
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


@pytest.mark.parametrize("command", UTILITIES + LETTER_SIGNALS + CONFIG_TIMELINES + STRUCTURED_INTEGRITY + RUN_INTEGRITY + PLANNING_DIFFS + REFUTATION + ARTIFACT_PLANNING + INTAKE_VOICE + READER_MANUSCRIPT)
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


@pytest.mark.parametrize("command", ["--self-test-all", "--check-canonical", "--check-all", "gate", "bogus"])
def test_unported_entrypoints_do_not_claim_success(command):
    result = run_python(command)
    assert result.returncode == 2
    assert b"Partial migration:" in result.stdout
    assert result.stderr == b""


@pytest.mark.parametrize("command", ["argument-reconstruction", "argument-reconstruction-draft"])
def test_argument_reconstruction_delegate_preserves_distinct_parsers(command, tmp_path):
    env = {**os.environ, "TMPDIR": str(tmp_path.resolve())}
    for args in ((), ("--bogus",), ("project", "--self-test"), ("--self-test", "ignored")):
        parity(command, *args, env=env)
    self_test = run_python(command, "--self-test", "ignored", env={**env, "PATH": ""})
    assert self_test.returncode == 0
    assert self_test.stderr == b""
    assert b"self-test: PASS\n" in self_test.stdout


@pytest.mark.parametrize("command, helper", [
    ("argument-reconstruction", "approval_graph.py"),
    ("argument-reconstruction-draft", "reconstruction_draft.py"),
])
def test_argument_reconstruction_shipped_helper_availability(tmp_path, command, helper):
    copied = tmp_path / "validate.py"
    shutil.copyfile(PYTHON_CLI, copied)
    env = {**os.environ, "TMPDIR": str(tmp_path.resolve()), "PATH": ""}

    def invoke(*args):
        return subprocess.run([sys.executable, str(copied), command, *args],
                              capture_output=True, env=env, timeout=30)

    expected = f"ERROR: {command} requires python3 and {helper}\n".encode()
    for args in ((), ("project",), ("--self-test", "ignored")):
        result = invoke(*args)
        assert (result.returncode, result.stdout, result.stderr) == (1, b"", expected)

    target = tmp_path / helper
    target.mkdir()
    result = invoke("--self-test")
    assert (result.returncode, result.stdout, result.stderr) == (1, b"", expected)
    target.rmdir()
    target.symlink_to(tmp_path / "absent-helper.py")
    result = invoke("project")
    assert (result.returncode, result.stdout, result.stderr) == (1, b"", expected)
    target.unlink()
    regular = tmp_path / "synthetic_helper.py"
    regular.write_text("import sys; print(repr(sys.argv[1:]))\n", encoding="utf-8")
    target.symlink_to(regular)
    result = invoke("--self-test", "ignored")
    assert (result.returncode, result.stdout, result.stderr) == (0, b"['--self-test']\n", b"")
    result = invoke("project", "--bogus")
    assert (result.returncode, result.stdout, result.stderr) == (0, b"['project', '--bogus']\n", b"")


def test_argument_reconstruction_real_append_stage_packet_and_emit(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    monkeypatch.syspath_prepend(str(ROOT / "evals/fixtures/argument-reconstruction"))
    import approval_graph as engine
    import run_cases as fixture

    project = tmp_path / "project"
    project.mkdir()
    context = fixture.source(project, "The invented lantern glows.\n")
    node = fixture.node(engine, "The invented lantern glows.")
    record_id = engine.node_id(node["type"], node["text"])
    bundle = fixture.bundle(engine, "MINT", "GENESIS", context, [
        fixture.event("MINTED", "normalizer", record_id, content=node, at="PENDING", pt="CURRENT")
    ])
    bundle_file = tmp_path / "mint.jsonl"
    bundle_file.write_bytes((engine.canonical_json(bundle) + "\n").encode())
    env = {**os.environ, "TMPDIR": str(tmp_path.resolve()), "PATH": ""}
    appended = run_python("argument-reconstruction", project, "--append-bundle", bundle_file,
                          "--expected-count", "0", "--expected-hash", "GENESIS", env=env)
    assert appended.returncode == 0 and json.loads(appended.stdout)["status"] == "COMMITTED"
    assert (project / "Approval_Events.jsonl").read_bytes() == bundle_file.read_bytes()
    assert (project / "Approval_Graph.md").is_file()

    stage = run_python("argument-reconstruction", project, "--stage", "graph", env=env)
    assert stage.returncode == 0
    assert (json.loads(stage.stdout)["stage"], json.loads(stage.stdout)["verdict"]) == ("graph", "PASS")
    assert (project / ".Approval_Events.lock").read_bytes() == b"\0"

    decision = fixture.bundle(engine, "DECISION", json.loads(appended.stdout)["head"]["terminal_hash"],
                              None, [fixture.event("DECISION", "author", record_id,
                                                   af="PENDING", at="APPROVED", inct="REQUIRED")])
    bundle_file.write_bytes((engine.canonical_json(decision) + "\n").encode())
    head = json.loads(appended.stdout)["head"]
    accepted = run_python("argument-reconstruction", project, "--append-bundle", bundle_file,
                          "--expected-count", head["bundle_count"],
                          "--expected-hash", head["terminal_hash"], env=env)
    assert accepted.returncode == 0 and json.loads(accepted.stdout)["status"] == "COMMITTED"
    stale = run_python("argument-reconstruction", project, "--append-bundle", bundle_file,
                       "--expected-count", "0", "--expected-hash", "GENESIS", env=env)
    assert stale.returncode == 1 and json.loads(stale.stdout)["error"] == "STALE-HEAD"
    assert (project / "Approval_Events.jsonl").read_bytes().count(b"\n") == 2

    (project / "Argument_State.md").write_text(
        "# Argument State\n\n## 1. Context and Classification\nForm: essay\n"
        "Goal: Describe invented lanterns.\nAudience:\n  Expertise: GENERAL\n"
        "  Receptivity: MIXED\n  Consequence context: LOW\n\n## 2. Propositions\n"
        "Synthetic context remainder.\n", encoding="utf-8")
    packet = run_python("argument-reconstruction-draft", project, "--packet", env=env)
    assert packet.returncode == 0 and tuple(json.loads(packet.stdout)) == (
        "context", "nodes", "edges", "style_brief")
    draft = tmp_path / "returned-draft.md"
    draft.write_bytes(b"Invented fresh prose.\n")
    mapping = tmp_path / "returned-map.md"
    mapping.write_text("### Passage p-1\nSpan: paragraphs 1–1\nKind: MAPPED\n"
                       f"Realizes: {record_id}\n", encoding="utf-8")
    final_head = json.loads(accepted.stdout)["head"]
    args = (project, "--emit", "--draft-file", draft, "--map-file", mapping,
            "--expected-count", final_head["bundle_count"], "--expected-hash", final_head["terminal_hash"],
            "--expected-packet-sha256", hashlib.sha256(packet.stdout).hexdigest())
    start = datetime.now(timezone.utc).replace(microsecond=0)
    emitted = run_python("argument-reconstruction-draft", *args, env=env)
    end = datetime.now(timezone.utc).replace(microsecond=0)
    assert emitted.returncode == 0
    assert json.loads(emitted.stdout)["verdict"] == "ACTION-REQUIRED"
    assert {f["code"] for f in json.loads(emitted.stdout)["findings"]} == {
        "I5-COMPARATOR-UNAVAILABLE", "SEMANTIC-NOT-RUN"}
    assert (project / "Reconstruction_Draft.md").read_bytes() == draft.read_bytes()
    receipt = (project / "Reconstruction_Receipt.md").read_text(encoding="utf-8")
    timestamp = re.search(r"^Timestamp: (.+)$", receipt, re.MULTILINE)
    assert timestamp is not None
    assert start <= datetime.strptime(timestamp.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) <= end
    assert "Judge: UNAVAILABLE" in receipt and "Config: I5-COMPARATOR-UNAVAILABLE" in receipt
    stale_args = list(args)
    stale_args[7:10] = ["0", "--expected-hash", "GENESIS"]
    refused = run_python("argument-reconstruction-draft", *stale_args, env=env)
    assert refused.returncode == 1
    assert b"STALE-HEAD" in refused.stderr
    assert (project / "Reconstruction_Draft.md").read_bytes() == draft.read_bytes()
    assert (project / "Reconstruction_Receipt.md").read_text(encoding="utf-8") == receipt


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
def test_gate_pair_is_deferred_until_complete_dispatch_and_aggregate_cutover(command, args):
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


@pytest.mark.parametrize("command", ARTIFACT_PLANNING)
def test_artifact_planning_original_argv_and_late_self_test(command):
    for args in ((), ("",), ("--strict",), (command,), (command, command), ("--unknown",)):
        assert native_and_optional_parity(command, *args).returncode == 2
    late = native_and_optional_parity(command, "--strict", "--self-test", "ignored")
    assert (late.returncode, late.stderr) == (0, b"")
    assert late.stdout.endswith(b"Self-test: PASS\n")


@pytest.mark.parametrize("command,inputs", [
    ("legal-risk", ("example-legal-risk-register.md",)),
    ("promise-contract", ("example-promise-contract.md",)),
    ("continuity-bible", ("example-continuity-bible.md", "example-timeline.md")),
    ("setup-payoff", ("example-setup-payoff-ledger.md",)),
    ("world-bible", ("example-worldbuilding-bible.md",)),
    ("argument-spine", ("example-argument-state-predraft.md",)),
    ("argument-spine", ("example-argument-state-genre-grant.md",)),
    ("argument-spine", ("example-argument-state-genre-academic.md",)),
    ("argument-spine", ("example-argument-state-genre-pitch.md",)),
    ("scene-ethics", ("example-scene-ethics-plan.md",)),
])
def test_artifact_planning_canonical_strict_inputs(command, inputs):
    result = native_and_optional_parity(command, *(REFERENCES / path for path in inputs), "--strict")
    assert (result.returncode, result.stderr) == (0, b"")


@pytest.mark.parametrize("command", ARTIFACT_PLANNING)
def test_artifact_planning_missing_and_non_utf8_read_refusal(tmp_path, command):
    for path in (tmp_path / "missing café.md", tmp_path / "bad café.md"):
        if path.name.startswith("bad"):
            path.write_bytes(b"\xff\xfe")
        result = native_and_optional_parity(command, path)
        assert (result.returncode, result.stderr) == (2, b"")
        if command == "promise-contract":
            assert b"no readable artifact found" in result.stdout
        else:
            assert b"cannot read " in result.stdout


@pytest.mark.parametrize("command,filename,canonical,block", [
    ("legal-risk", "Project_Legal_Risk_Register_r1.md", "example-legal-risk-register.md", "legal_risk"),
    ("setup-payoff", "Project_Setup_Payoff_Ledger_r1.md", "example-setup-payoff-ledger.md", "setup_payoff"),
    ("world-bible", "Project_Worldbuilding_Bible_r1.md", "example-worldbuilding-bible.md", "world_fact"),
    ("argument-spine", "Argument_State_r1.md", "example-argument-state-predraft.md", "argument_spine"),
    ("scene-ethics", "Project_Scene_Ethics_Plan_r1.md", "example-scene-ethics-plan.md", "scene_ethics"),
])
def test_artifact_planning_parsed_first_carrier_and_newest_file(tmp_path, command, filename, canonical, block):
    folder = tmp_path / "run café"
    folder.mkdir()
    bad = folder / filename
    bad.write_text(f"<!-- apodictic:{block}\n{{\n-->\n", encoding="utf-8")
    good = folder / filename.replace("r1", "r2")
    good.write_bytes((REFERENCES / canonical).read_bytes())
    decoy = tmp_path / "prose.md"
    decoy.write_text(f"Prose mentions apodictic:{block}, without carrying a block.\n", encoding="utf-8")
    assert native_and_optional_parity(command, decoy, good, "--strict").returncode == 0
    assert native_and_optional_parity(command, good, bad, "--strict").returncode == 0
    assert native_and_optional_parity(command, bad, good).returncode == 1
    os.utime(bad, (100, 100))
    os.utime(good, (200, 200))
    assert native_and_optional_parity(command, folder, "--strict").returncode == 0
    os.utime(bad, (300, 300))
    assert native_and_optional_parity(command, folder).returncode == 1


def test_literal_command_filename_remains_helper_owned(tmp_path):
    (tmp_path / "legal-risk").write_bytes((REFERENCES / "example-legal-risk-register.md").read_bytes())
    assert native_and_optional_parity("legal-risk", "legal-risk", cwd=tmp_path).returncode == 2
    assert native_and_optional_parity("legal-risk", "./legal-risk", cwd=tmp_path).returncode == 0


def test_promise_separate_inputs_partial_reads_and_all_folder_reports(tmp_path):
    def block(kind, obj):
        return f"<!-- apodictic:{kind}\n{json.dumps(obj, ensure_ascii=False)}\n-->\n"
    pitch = {"schema": "apodictic.pitch_copy.v1", "id": "PC-01", "copy_type": "query",
             "text": "A cartographer maps a changing city."}
    finding = {"schema": "apodictic.finding.v1", "id": "F-PCF-01", "severity": "Should-Fix",
               "confidence": "HIGH", "mechanism": "PCF1 emphasis distortion: the query leads with a minor subplot",
               "evidence_refs": ["copy:query¶1", "contract:CONTROLLING IDEA"],
               "fix_class": "bring the copy back to the kept promise", "risk_if_fixed": "the lead reframes the book"}
    new = tmp_path / "Project_Pitch_Copy_r2.md"
    report = tmp_path / "Report café.md"
    new.write_text(block("pitch_copy", pitch), encoding="utf-8")
    report.write_text(block("finding", finding), encoding="utf-8")
    unreadable = tmp_path / "unreadable.md"
    unreadable.write_bytes(b"\xff\xfe")
    assert native_and_optional_parity("promise-contract", report, new, unreadable, "--strict").returncode == 0
    old = tmp_path / "Project_Pitch_Copy_r1.md"
    old_pitch = dict(pitch, copy_type="invalid")
    old_finding = dict(finding, id="F-PCF-02", evidence_refs=["copy:query¶1"])
    old.write_text(block("pitch_copy", old_pitch) + block("finding", old_finding), encoding="utf-8")
    os.utime(old, (100, 100))
    os.utime(new, (200, 200))
    selected = native_and_optional_parity("promise-contract", tmp_path, "--strict")
    assert selected.returncode == 1
    assert b"P1 one-sided gap" in selected.stdout
    assert b"P2" not in selected.stdout  # Old copy is excluded from pitch, but included in report.
    old_finding["evidence_refs"] = finding["evidence_refs"]
    old.write_text(block("pitch_copy", old_pitch) + block("finding", old_finding), encoding="utf-8")
    os.utime(old, (100, 100))
    assert native_and_optional_parity("promise-contract", tmp_path, "--strict").returncode == 0


def test_continuity_timeline_local_parent_and_first_explicit_order(tmp_path):
    folder = tmp_path / "run"
    folder.mkdir()
    bible = folder / "Project_Continuity_Bible_r1.md"
    bible.write_bytes((REFERENCES / "example-continuity-bible.md").read_bytes())
    parent = tmp_path / "Timeline.md"
    parent.write_bytes((REFERENCES / "example-timeline.md").read_bytes())
    assert native_and_optional_parity("continuity-bible", folder, "--strict").returncode == 0
    local = folder / "Timeline.md"
    local.write_text(parent.read_text(encoding="utf-8").replace("Ch 1 §2", "Ch 99 §2"), encoding="utf-8")
    assert native_and_optional_parity("continuity-bible", folder, "--strict").returncode == 1
    assert native_and_optional_parity("continuity-bible", parent, bible, local, "--strict").returncode == 0
    assert native_and_optional_parity("continuity-bible", local, bible, parent, "--strict").returncode == 1
    local.unlink()
    assert native_and_optional_parity("continuity-bible", folder, "--strict").returncode == 0
    parent.write_bytes(b"\xff\xfe")
    # An unreadable optional timeline retains the same coverage limitation as omission.
    assert native_and_optional_parity("continuity-bible", bible, parent, "--strict").returncode == 0
    assert native_and_optional_parity("continuity-bible", bible, "--strict").returncode == 0


def test_scene_ethics_advisory_strict_and_scoped_override(tmp_path):
    path = tmp_path / "ethics café.md"
    item = {"schema": "apodictic.scene_ethics.v1", "id": "EP-01", "subject": "a named manager",
            "depiction": "a workplace remark", "consent_status": "not-sought", "handling": "as-is",
            "legal_ref": "LR-01"}
    text = "<!-- apodictic:scene_ethics\n" + json.dumps(item) + "\n-->\n"
    path.write_text(text, encoding="utf-8")
    advisory = native_and_optional_parity("scene-ethics", path)
    assert advisory.returncode == 0 and b"W1 unresolved depiction" in advisory.stdout
    assert native_and_optional_parity("scene-ethics", path, "--strict").returncode == 1
    path.write_text("<!-- override: scene-ethics-unresolved EP-99 — unrelated -->\n" + text, encoding="utf-8")
    assert native_and_optional_parity("scene-ethics", path, "--strict").returncode == 1
    path.write_text("<!-- override: scene-ethics-unresolved EP-01 — public record -->\n" + text, encoding="utf-8")
    assert native_and_optional_parity("scene-ethics", path, "--strict").returncode == 0


@pytest.mark.parametrize("command", INTAKE_VOICE)
def test_intake_voice_raw_arguments_and_self_test_precedence(tmp_path, command):
    for args in ((), ("",), ("--strict",), (command,), (command, command),
                 ("--unknown",), ("--unknown", "missing"), ("--", "missing"), ("-",)):
        assert native_and_optional_parity(command, *args, cwd=tmp_path).returncode == 2
    for args in (("--self-test", "ignored"), ("--strict", "--self-test", "ignored")):
        result = native_and_optional_parity(command, *args)
        assert (result.returncode, result.stderr) == (0, b"")
        assert result.stdout.endswith(b"Self-test: PASS\n")


@pytest.mark.parametrize("command,inputs", [
    ("intake-interview", ("example-intake-interview.md", "example-intake-interview-ledger.md")),
    ("author-fingerprint", ("example-author-voice-profile.md",)),
    ("content-advisory", ("example-content-advisory.md",)),
    ("coaching-history", ("example-coaching-history",)),
    ("style-explanation", ("example-author-style-explanation.md",)),
    ("persona-divergence", ("example-persona-divergence-map.md", "example-persona-divergence-ledger.md")),
])
def test_intake_voice_canonical_strict_inputs(command, inputs):
    result = native_and_optional_parity(command, *(REFERENCES / name for name in inputs), "--strict")
    assert (result.returncode, result.stderr) == (0, b"")


@pytest.mark.parametrize("command", INTAKE_VOICE)
def test_intake_voice_read_and_no_artifact_distinctions(tmp_path, command):
    for path in (tmp_path / "missing café.md", tmp_path / "bad café.md"):
        if path.name.startswith("bad"):
            path.write_bytes(b"\xff\xfe")
        result = native_and_optional_parity(command, path)
        assert (result.returncode, result.stderr) == (2, b"")
        if command == "content-advisory":
            assert b"no advisory artifact found" in result.stdout
        elif command == "coaching-history":
            assert b"no opt-in marker" in result.stdout
        else:
            assert b"cannot read " in result.stdout
    assert native_and_optional_parity(command, tmp_path).returncode == 2


@pytest.mark.parametrize("command,filename,canonical,kind,extra", [
    ("intake-interview", "Project_Intake_Interview_r1.md", "example-intake-interview.md", "intake_query", ("example-intake-interview-ledger.md",)),
    ("author-fingerprint", "Author_Voice_Profile_r1.md", "example-author-voice-profile.md", "voice_fingerprint", ()),
    ("content-advisory", "Project_Content_Advisory_r1.md", "example-content-advisory.md", "content_note", ()),
    ("persona-divergence", "Project_Persona_Divergence_Map_r1.md", "example-persona-divergence-map.md", "persona", ("example-persona-divergence-ledger.md",)),
])
def test_intake_voice_parsed_carrier_and_newest_discovery(tmp_path, command, filename, canonical, kind, extra):
    folder = tmp_path / "run café"
    folder.mkdir()
    bad = folder / filename
    bad.write_text(f"<!-- apodictic:{kind}\n{{\n-->\n", encoding="utf-8")
    good = folder / filename.replace("r1", "r2")
    good.write_bytes((REFERENCES / canonical).read_bytes())
    optional = []
    for name in extra:
        ledger = folder / "Project_Findings_Ledger_r1.md"
        ledger.write_bytes((REFERENCES / name).read_bytes())
        optional.append(ledger)
    prose = tmp_path / "decoy.md"
    prose.write_text(f"Mention apodictic:{kind} without a parsed block.\n", encoding="utf-8")
    assert native_and_optional_parity(command, prose, good, *optional, "--strict").returncode == 0
    assert native_and_optional_parity(command, good, bad, *optional, "--strict").returncode == 0
    assert native_and_optional_parity(command, bad, good, *optional).returncode == 1
    os.utime(bad, (100, 100))
    os.utime(good, (200, 200))
    assert native_and_optional_parity(command, folder, "--strict").returncode == 0
    os.utime(bad, (300, 300))
    assert native_and_optional_parity(command, folder).returncode == 1


def test_style_prefers_parsed_labels_over_newer_fingerprint_and_first_fallback(tmp_path):
    labels = tmp_path / "Author_Style_Explanation_r1.md"
    labels.write_bytes((REFERENCES / "example-author-style-explanation.md").read_bytes())
    profile = tmp_path / "Author_Voice_Profile_r2.md"
    profile.write_bytes((REFERENCES / "example-author-voice-profile.md").read_bytes())
    os.utime(labels, (100, 100))
    os.utime(profile, (200, 200))
    result = native_and_optional_parity("style-explanation", tmp_path, "--strict")
    assert result.returncode == 0 and b"4 label(s)" in result.stdout
    assert native_and_optional_parity("style-explanation", profile, labels, "--strict").stdout == result.stdout
    labels.unlink()
    result = native_and_optional_parity("style-explanation", tmp_path, "--strict")
    assert result.returncode == 0 and b"no style_label blocks" in result.stdout
    prose = tmp_path / "plain.md"
    prose.write_text("Plain prose.\n", encoding="utf-8")
    for command, marker in (("style-explanation", b"no style_label"), ("author-fingerprint", b"no voice_fingerprint")):
        result = native_and_optional_parity(command, prose, "--strict")
        assert result.returncode == 0 and marker in result.stdout
    assert native_and_optional_parity("content-advisory", prose).returncode == 2


def test_advisory_folder_prose_decode_and_scoped_override(tmp_path):
    path = tmp_path / "Project_Content_Advisory_r1.md"
    path.write_text("<!-- content-advisory: opted-in -->\nYou should cut this scene.\n", encoding="utf-8")
    assert native_and_optional_parity("content-advisory", path).returncode == 2
    result = native_and_optional_parity("content-advisory", tmp_path)
    assert result.returncode == 0 and b"W1 prescriptive drift" in result.stdout
    assert native_and_optional_parity("content-advisory", tmp_path, "--strict").returncode == 1
    text = path.read_text(encoding="utf-8")
    path.write_text("<!-- override: advisory-eval CN-01 — scoped elsewhere -->\n" + text, encoding="utf-8")
    assert native_and_optional_parity("content-advisory", tmp_path, "--strict").returncode == 1
    path.write_text("<!-- override: advisory-eval-prose — requested wording -->\n" + text, encoding="utf-8")
    assert native_and_optional_parity("content-advisory", tmp_path, "--strict").returncode == 0
    path.write_bytes(b"\xff\xfe")
    result = native_and_optional_parity("content-advisory", tmp_path)
    assert result.returncode == 2 and b"cannot read " in result.stdout


def test_intake_optional_ledger_order_degradation_and_duplicate_override(tmp_path):
    query = tmp_path / "query.md"
    query.write_bytes((REFERENCES / "example-intake-interview.md").read_bytes())
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes((REFERENCES / "example-intake-interview-ledger.md").read_bytes())
    good = native_and_optional_parity("intake-interview", query, ledger, "--strict")
    assert native_and_optional_parity("intake-interview", ledger, query, "--strict").stdout == good.stdout
    bad = tmp_path / "bad.md"
    bad.write_bytes(b"\xff\xfe")
    for args in ((query,), (query, bad)):
        result = native_and_optional_parity("intake-interview", *args, "--strict")
        assert result.returncode == 1 and b"I3 grounded" in result.stdout
    assert native_and_optional_parity("intake-interview", query, bad, ledger, "--strict").returncode == 0
    edit_artifact_block(query, "intake_query", lambda obj: obj.update(question="What is the genre?"))
    assert native_and_optional_parity("intake-interview", query, ledger).returncode == 0
    assert native_and_optional_parity("intake-interview", query, ledger, "--strict").returncode == 1
    query.write_text("<!-- override: intake-dup IQ-01 — author requested -->\n" + query.read_text(encoding="utf-8"), encoding="utf-8")
    assert native_and_optional_parity("intake-interview", query, ledger, "--strict").returncode == 0


def test_persona_local_only_timeline_optional_inputs_and_severity_lock(tmp_path):
    folder = tmp_path / "run"
    folder.mkdir()
    path = folder / "Project_Persona_Divergence_Map_r1.md"
    path.write_bytes((REFERENCES / "example-persona-divergence-map.md").read_bytes())
    edit_artifact_block(path, "divergence", lambda obj: (obj.update(anchor="Ch 1 §2"), obj.pop("asserted_severity", None)))
    parent = tmp_path / "Timeline.md"
    parent.write_bytes((REFERENCES / "example-timeline.md").read_bytes())
    result = native_and_optional_parity("persona-divergence", folder, "--strict")
    assert result.returncode == 1 and b"D2 grounded" in result.stdout
    assert native_and_optional_parity("persona-divergence", parent, path, "--strict").returncode == 0
    local = folder / "Timeline.md"
    local.write_bytes(parent.read_bytes())
    assert native_and_optional_parity("persona-divergence", folder, "--strict").returncode == 0
    edit_artifact_block(path, "divergence", lambda obj: obj.update(asserted_severity="Must-Fix"))
    result = native_and_optional_parity("persona-divergence", folder, "--strict")
    assert result.returncode == 1 and b"no locked Ledger severity" in result.stdout
    path.write_bytes((REFERENCES / "example-persona-divergence-map.md").read_bytes())
    bad_ledger = folder / "Project_Findings_Ledger_r1.md"
    bad_ledger.write_bytes(b"\xff\xfe")
    assert native_and_optional_parity("persona-divergence", folder).returncode == 1
    bad_ledger.write_bytes((REFERENCES / "example-persona-divergence-ledger.md").read_bytes())
    assert native_and_optional_parity("persona-divergence", folder, "--strict").returncode == 0


@pytest.mark.parametrize("command,canonical,marker,warning", [
    ("author-fingerprint", "example-author-voice-profile.md", "<!-- author-voice-profile: local-only -->", b"W2 local-only"),
    ("style-explanation", "example-author-style-explanation.md", "<!-- author-style-explanation: local-only -->", b"X6 local-only"),
])
def test_voice_local_only_warnings_remain_nonblocking_strict(tmp_path, command, canonical, marker, warning):
    path = tmp_path / "voice café.md"
    path.write_text((REFERENCES / canonical).read_text(encoding="utf-8").replace(marker, "") + "\nhttps://example.invalid/profile\n", encoding="utf-8")
    result = native_and_optional_parity(command, path, "--strict")
    assert result.returncode == 0 and warning in result.stdout


def test_coaching_delete_missing_target_preserves_exit_stdout_with_named_stderr():
    native = run_python("coaching-history", "delete")
    assert (native.returncode, native.stdout, native.stderr) == (
        1, b"", b"Error: coaching-history delete requires <project_root>\n",
    )
    if BASH is not None:
        legacy = subprocess.run([BASH, str(BASH_CLI), "coaching-history", "delete"], capture_output=True, timeout=60)
        assert (legacy.returncode, legacy.stdout) == (1, b"")
        assert legacy.stderr  # Shell source-path/line diagnostics are deliberately not emulated.


@pytest.mark.parametrize("raw,expected", [
    (("delete", "--self-test", "absent"), 0),
    (("delete", "absent", "--self-test"), 2),
    (("delete", "--strict", "absent"), 2),
    (("delete", "absent", "extra"), 2),
    (("coaching-history", "delete", "absent"), 2),
    (("--strict", "delete", "absent"), 2),
    (("delete", "coaching-history", "absent"), 2),
    (("delete", "", "absent"), 2),
])
def test_coaching_first_delete_truncation_and_helper_filtering(tmp_path, raw, expected):
    result = native_and_optional_parity("coaching-history", *raw, cwd=tmp_path)
    assert result.returncode == expected and result.stderr == b""


def tree_contents(root):
    return {
        str(p.relative_to(root)): (p.stat().st_mode & 0o777, p.read_bytes() if p.is_file() else None)
        for p in sorted(root.rglob("*"))
    }


@pytest.mark.parametrize("malformed", [False, True])
def test_coaching_delete_effects_residue_idempotence_and_partial_failure(tmp_path, malformed):
    project = tmp_path / "project café"
    def restore():
        if project.exists():
            shutil.rmtree(project)
        (project / "nested/deep").mkdir(parents=True)
        (project / "Diagnostic_State.md").write_text("<!-- coaching-history: opted-in -->\n", encoding="utf-8")
        for name in ("First_Coaching_History_r1.md", "nested/deep/Second_Coaching_History_r2.md"):
            (project / name).write_text("# History\n", encoding="utf-8")
        (project / "projection.md").write_text("<!-- apodictic:coaching_observation\n{}\n-->\n", encoding="utf-8")
        sidecar = {"coaching_history_seq": 1, "nested": [{"coaching_history_seq": 2, "keep": "yes"}], "keep": "value"}
        (project / "Diagnostic_State.meta.json").write_text("{broken" if malformed else json.dumps(sidecar), encoding="utf-8")
        for p in project.rglob("*"):
            p.chmod(0o750 if p.is_dir() else 0o640)
    restore()
    before = tree_contents(project)
    native = run_python("coaching-history", "delete", project, "--self-test", "ignored")
    after = tree_contents(project)
    assert native.returncode == (1 if malformed else 0) and native.stderr == b""
    assert not list(project.rglob("*_Coaching_History_*.md"))
    assert after["projection.md"] == before["projection.md"]
    if malformed:
        assert after["Diagnostic_State.md"] == before["Diagnostic_State.md"]
        assert after["Diagnostic_State.meta.json"] == before["Diagnostic_State.meta.json"]
    else:
        assert json.loads((project / "Diagnostic_State.meta.json").read_text()) == {"nested": [{"keep": "yes"}], "keep": "value"}
        assert b"coaching-history: deleted" in after["Diagnostic_State.md"][1]
        recompute = run_python("coaching-history", project, "--strict")
        assert recompute.returncode == 1 and b"H6" in recompute.stdout
        repeated = run_python("coaching-history", "delete", project)
        assert repeated.returncode == 0 and tree_contents(project) == after
        (project / "projection.md").unlink()
        clean = run_python("coaching-history", project, "--strict")
        assert clean.returncode == 0 and b"PASS" in clean.stdout
    if BASH is not None:
        restore()
        assert tree_contents(project) == before
        legacy = subprocess.run([BASH, str(BASH_CLI), "coaching-history", "delete", str(project), "--self-test", "ignored"], capture_output=True, timeout=60)
        assert (legacy.returncode, legacy.stdout, legacy.stderr) == (native.returncode, native.stdout, native.stderr)
        assert tree_contents(project) == after
        if not malformed:
            check = subprocess.run([BASH, str(BASH_CLI), "coaching-history", str(project), "--strict"], capture_output=True, timeout=60)
            assert (check.returncode, check.stdout, check.stderr) == (recompute.returncode, recompute.stdout, recompute.stderr)
            repeat = subprocess.run([BASH, str(BASH_CLI), "coaching-history", "delete", str(project)], capture_output=True, timeout=60)
            assert (repeat.returncode, repeat.stdout, repeat.stderr) == (repeated.returncode, repeated.stdout, repeated.stderr)
            assert tree_contents(project) == after


def test_coaching_warning_order_same_seed_strict_url_and_residue_override(tmp_path):
    history = tmp_path / "Project_Coaching_History_r1.md"
    history.write_text("# History\n", encoding="utf-8")
    (tmp_path / "Diagnostic_State.md").write_text("<!-- coaching-history: opted-in -->\n", encoding="utf-8")
    notes = tmp_path / "notes.md"
    notes.write_text("CH-01 CH-02 CH-03 CH-04 CH-05\n", encoding="utf-8")
    for seed in ("1", "2", "3"):
        env = dict(os.environ, PYTHONHASHSEED=seed)
        result = native_and_optional_parity("coaching-history", tmp_path, env=env)
        assert result.returncode == 0 and b"bare" in result.stdout
        assert native_and_optional_parity("coaching-history", tmp_path, "--strict", env=env).returncode == 1
    notes.write_text("<!-- override: coaching-residue CH-99 — unrelated -->\nCH-01\n", encoding="utf-8")
    assert native_and_optional_parity("coaching-history", tmp_path, "--strict").returncode == 1

    notes.write_text("<!-- override: coaching-residue CH-01 — discussion only -->\nCH-01\n", encoding="utf-8")
    assert native_and_optional_parity("coaching-history", tmp_path, "--strict").returncode == 0
    notes.unlink()
    history.write_text("# History\nhttps://example.invalid/profile\n", encoding="utf-8")
    result = native_and_optional_parity("coaching-history", tmp_path)
    assert result.returncode == 0 and b"W1 local-only" in result.stdout
    assert native_and_optional_parity("coaching-history", tmp_path, "--strict").returncode == 1


def test_coaching_root_sidecar_consent_order_and_recursive_newest_selection(tmp_path):
    project = tmp_path / "project"
    shutil.copytree(REFERENCES / "example-coaching-history", project)
    history = next(project.glob("*_Coaching_History_*.md"))
    state = project / "Diagnostic_State.md"
    sidecar = project / "Diagnostic_State.meta.json"
    assert native_and_optional_parity("coaching-history", project, "--strict").returncode == 0
    outside = tmp_path / "outside.json"
    outside.write_text("{broken", encoding="utf-8")
    assert native_and_optional_parity("coaching-history", history, outside, "--strict").returncode == 0
    original_state, original_sidecar = state.read_bytes(), sidecar.read_bytes()
    # A present malformed local sidecar fails before absent consent; extra paths do not replace it.
    state.write_text("# State\n", encoding="utf-8")
    history_text = history.read_text(encoding="utf-8")
    history.write_text(history_text.replace("<!-- coaching-history: opted-in -->", ""), encoding="utf-8")
    sidecar.write_text("{broken", encoding="utf-8")
    result = native_and_optional_parity("coaching-history", history, outside)
    assert result.returncode == 1 and b"H0 unparseable sidecar" in result.stdout
    sidecar.write_bytes(original_sidecar)
    assert native_and_optional_parity("coaching-history", history).returncode == 2
    state.write_bytes(original_state + b"\n<!-- coaching-history: deleted -->\n")
    result = native_and_optional_parity("coaching-history", project)
    assert result.returncode == 1 and b"consent contradiction" in result.stdout
    state.write_bytes(original_state)
    history.write_text(history_text, encoding="utf-8")
    nested = project / "nested/deep"
    nested.mkdir(parents=True)
    bad = nested / "Second_Coaching_History_r2.md"
    bad.write_text("<!-- apodictic:coaching_observation\n{\n-->\n", encoding="utf-8")
    os.utime(history, (100, 100))
    os.utime(bad, (200, 200))
    selected = native_and_optional_parity("coaching-history", project)
    assert selected.returncode == 1 and b"H1 schema" in selected.stdout
    explicit = native_and_optional_parity("coaching-history", history, bad)
    assert explicit.returncode == 1 and b"H1 schema" not in explicit.stdout
    # Explicit first carrier moves the consent/sidecar root to its own directory.
    reverse = native_and_optional_parity("coaching-history", bad, history)
    assert reverse.returncode == 2 and b"no opt-in marker" in reverse.stdout


@pytest.mark.parametrize('command', READER_MANUSCRIPT)
def test_reader_manuscript_wrapper_arity_and_helper_owned_tokens(tmp_path, command):
    minimum = 3 if command in ('roundtrip-disposition', 'position-pair-register') else 1
    for raw in [()] + [('missing',) * count for count in range(1, minimum)]:
        result = native_and_optional_parity(command, *raw)
        assert result.returncode == 2 and result.stderr == b''
        assert b'validate.sh ' + command.encode() in result.stdout
    for raw in [('',) * minimum, ('--strict',) * minimum, (command,) * minimum,
                ('--unknown', 'missing', '--', '-', 'extra')]:
        result = native_and_optional_parity(command, *raw, cwd=tmp_path)
        assert result.returncode in (0, 1, 2)  # Helper-owned no-op/read/usage decisions vary.
    result = native_and_optional_parity(command, 'missing', '--self-test')
    assert result.returncode == (2 if minimum == 3 else 0)
    result = native_and_optional_parity(command, 'missing', 'missing', '--self-test')
    assert result.returncode == 0 and result.stdout.endswith(b'Self-test: PASS\n')


VIZ_INPUTS = ('example-structure-map-manifest.md', 'example-timeline.md', 'example-findings-ledger.md',
              'example-argument-state-predraft.md', 'example-scene-roster.md', 'example-scene-function.md',
              'example-tension-points.md', 'example-story-spine.md')
POSITION_REFERENCES = SCRIPTS.parent / 'skills/prose-measurements/references/example-position-pair-register'


@pytest.mark.parametrize('strict', [False, True])
@pytest.mark.parametrize('command,names', [
    ('lifecycle-node', ('example-run-folder/Diagnostic_State.meta.json', 'example-run-folder')),
    ('reader-instrument', ('example-beta-reader-instrument.md', 'example-uncertainty-ledger.md')),
    ('manuscript-viz', VIZ_INPUTS),
    ('annotated-manuscript', ('example-annotated-manuscript',)),
    ('crosslink', ('example-annotated-manuscript',)),
    ('reanchor', ('example-annotated-manuscript', 'example-reanchor-revised.md')),
    ('reader-contract-outline', ('example-reader-contract-outline',)),
    ('results-guide', ('example-results-guide',)),
    ('position-pair-register', ('Example_Position_Pair_Register_run.md', 'envelope.json', 'manuscript.txt')),
])
def test_reader_manuscript_canonical_default_and_strict(command, names, strict):
    base = POSITION_REFERENCES if command == 'position-pair-register' else REFERENCES
    args = [base / name for name in names]
    if command == 'manuscript-viz':
        args.append('--require-block')
    if strict:
        args.append('--strict')
    result = native_and_optional_parity(command, *args)
    assert result.returncode == (1 if command == 'reanchor' and strict else 0)
    assert result.stderr == b''


@pytest.fixture
def disposition_round(tmp_path):
    prior, current = tmp_path / 'prior', tmp_path / 'current'
    prior.mkdir(); current.mkdir()
    for pattern in ('*_Annotation_Manifest_*.md', '*_Findings_Ledger_*.md'):
        for source in (REFERENCES / 'example-annotated-manuscript').glob(pattern):
            shutil.copy2(source, prior / source.name)
    for source in (REFERENCES / 'example-run-folder-r2').glob('*_Findings_Ledger_*.md'):
        shutil.copy2(source, current / source.name)
    for name, dest in [('example-roundtrip-disposition.md', 'Example_Roundtrip_Disposition_reanchor-r2.md'),
                       ('example-roundtrip-revision-report.md', 'Example_Revision_Report_reanchor-r2.md')]:
        shutil.copy2(REFERENCES / name, current / dest)
    snapshot = tmp_path / 'Example_Manuscript_Snapshot_reanchor-r2.md'
    shutil.copy2(REFERENCES / 'example-reanchor-revised.md', snapshot)
    return prior, snapshot, current


def test_disposition_canonical_record_and_absent_record_before_reads(disposition_round, tmp_path):
    for flags in ((), ('--strict',)):
        assert native_and_optional_parity('roundtrip-disposition', *disposition_round, *flags).returncode == 0
    empty = tmp_path / 'absent'
    empty.mkdir()
    assert native_and_optional_parity('roundtrip-disposition', 'missing-prior', 'missing-snapshot', empty, '--strict').returncode == 0
    record = empty / 'Project_Roundtrip_Disposition_r1.md'
    record.write_bytes(b'\xff\xfe')
    assert native_and_optional_parity('roundtrip-disposition', 'missing-prior', 'missing-snapshot', empty, '--strict').returncode == 2
    record = next(disposition_round[2].glob('*_Roundtrip_Disposition_*.md'))
    text = record.read_text(encoding='utf-8')
    record.write_text(re.sub(r'<!--\s*disposition-confirmed:.*?-->', '', text, flags=re.S), encoding='utf-8')
    result = native_and_optional_parity('roundtrip-disposition', *disposition_round)
    assert result.returncode == 1 and b'RT2' in result.stdout


@pytest.mark.parametrize('project', ['Example', 'ExampleNF'])
def test_outline_explicit_coherent_projects(project):
    folder = REFERENCES / 'example-reader-contract-outline'
    args = [folder / f'{project}_{kind}_2026-01-01.md' for kind in
            ('Pass0_Reverse_Outline', 'Contract', 'Findings_Ledger', 'Contract_Map', 'Reader_Contract_Outline')]
    assert native_and_optional_parity('reader-contract-outline', *args, '--strict').returncode == 0


def test_lifecycle_total_sidecar_and_optional_folder_precedence(tmp_path):
    state = tmp_path / 'state.json'
    state.write_text('{}', encoding='utf-8')
    folder = tmp_path / 'optional'
    folder.mkdir()
    def node(expected):
        result = native_and_optional_parity('lifecycle-node', state, folder, '--strict', 'ignored')
        assert result.returncode == 0 and result.stdout.startswith(f'lifecycle-node: {expected}\n'.encode())
    node('diagnosing')
    (folder / 'Project_Synthesis_r1.md').write_text('# Letter\n', encoding='utf-8')
    node('diagnosed')
    state.write_text('{"mode":"execution","execution":{"pending_gate":"next"}}', encoding='utf-8')
    node('blocked_gate')
    for body in (b'\xff', b'{invalid', b'[]'):
        state.write_bytes(body)
        node('cold')


def test_reader_first_parsed_carrier_optional_ledger_and_scoped_override(tmp_path):
    good = tmp_path / 'reader café.md'
    good.write_bytes((REFERENCES / 'example-beta-reader-instrument.md').read_bytes())
    ledger = REFERENCES / 'example-uncertainty-ledger.md'
    bad = tmp_path / 'bad.md'
    bad.write_text('<!-- apodictic:reader_question\n{}\n-->\n', encoding='utf-8')
    prose = tmp_path / 'decoy.md'
    prose.write_text('A mention of apodictic:reader_question.\n', encoding='utf-8')
    assert native_and_optional_parity('reader-instrument', prose, good, ledger, '--strict').returncode == 0
    assert native_and_optional_parity('reader-instrument', good, bad, ledger, '--strict').returncode == 0
    assert native_and_optional_parity('reader-instrument', bad, good, ledger).returncode == 1
    bad.write_bytes(b'\xff')
    assert native_and_optional_parity('reader-instrument', bad).returncode == 2
    assert native_and_optional_parity('reader-instrument', good, bad).returncode == 1
    edit_artifact_block(good, 'reader_question', lambda obj: obj.update(question="Don't you think this scene is boring?"))
    assert native_and_optional_parity('reader-instrument', good, ledger).returncode == 0
    assert native_and_optional_parity('reader-instrument', good, ledger, '--strict').returncode == 1
    good.write_text('<!-- override: leading-question RQ-01 — author wording -->\n' + good.read_text(encoding='utf-8'), encoding='utf-8')
    assert native_and_optional_parity('reader-instrument', good, ledger, '--strict').returncode == 0


def test_viz_timeline_glob_optional_roles_and_require_block(tmp_path):
    names = ('Project_Structure_Map_r1.md', 'Project_Timeline_r1.md', 'Project_Findings_Ledger_r1.md',
             'Argument_State_r1.md', 'Project_Scene_Roster_r1.md', 'Project_Scene_Function_r1.md',
             'Project_Tension_Points_r1.md', 'Project_Story_Spine_r1.md')
    files = []
    for name, canonical in zip(names, VIZ_INPUTS):
        path = tmp_path / name
        path.write_bytes((REFERENCES / canonical).read_bytes())
        files.append(path)
    os.utime(files[1], (100, 100))
    fallback = tmp_path / 'Timeline.md'
    fallback.write_bytes(b'\xff')
    os.utime(fallback, (200, 200))
    assert native_and_optional_parity('manuscript-viz', tmp_path, '--strict', '--require-block').returncode == 0
    assert native_and_optional_parity('manuscript-viz', *reversed(files), '--strict', '--require-block').returncode == 0
    files[1].unlink()
    assert native_and_optional_parity('manuscript-viz', tmp_path, '--strict', '--require-block').returncode == 1
    plain = tmp_path / 'plain.md'
    plain.write_text('# No block\n', encoding='utf-8')
    assert native_and_optional_parity('manuscript-viz', plain).returncode == 0
    assert native_and_optional_parity('manuscript-viz', plain, '--require-block').returncode == 1


def test_annotation_last_role_bound_snapshot_and_crosslink_priority_noop(tmp_path):
    folder = tmp_path / 'annotations'
    shutil.copytree(REFERENCES / 'example-annotated-manuscript', folder)
    files = sorted(folder.glob('*.md'))
    original = next(folder.glob('*_Manuscript_Snapshot_*.md'))
    newer = folder / 'Other_Manuscript_Snapshot_r2.md'
    newer.write_text('Unrelated snapshot\n', encoding='utf-8')
    os.utime(newer, (2000000000, 2000000000))
    assert native_and_optional_parity('annotated-manuscript', folder, '--strict').returncode == 0
    good = native_and_optional_parity('annotated-manuscript', newer, *files, '--strict')
    assert good.returncode == 0
    assert native_and_optional_parity('annotated-manuscript', *files, newer, '--strict').returncode == 1
    # Letter glob class outranks a newer lower-priority canonical editorial letter.
    priority = folder / 'Project_Core_DE_Synthesis_old.md'
    priority.write_text('Different priority letter\n', encoding='utf-8')
    os.utime(priority, (100, 100))
    assert native_and_optional_parity('crosslink', folder, '--strict').returncode == 1
    priority.unlink()
    assert native_and_optional_parity('crosslink', folder, '--strict').returncode == 0
    empty_manifest = tmp_path / 'Project_Annotation_Manifest_empty.md'
    empty_manifest.write_text('# No anchors\n', encoding='utf-8')
    assert native_and_optional_parity('crosslink', empty_manifest, '--strict').returncode == 0
    original.write_bytes(b'\xff')
    assert native_and_optional_parity('annotated-manuscript', folder).returncode == 2


def test_outline_project_score_contract_collisions_and_same_seed_extra_keys(tmp_path):
    folder = tmp_path / 'outline'
    shutil.copytree(REFERENCES / 'example-reader-contract-outline', folder)
    chosen = native_and_optional_parity('reader-contract-outline', folder, '--strict')
    assert chosen.returncode == 0
    contract = folder / 'Example_Contract_2026-01-01.md'
    original = contract.read_bytes()
    contract.unlink()
    other = native_and_optional_parity('reader-contract-outline', folder, '--strict')
    assert other.returncode == 0 and other.stdout != chosen.stdout
    contract.write_bytes(original)
    map_path = folder / 'Example_Contract_Map_2026-01-01.md'
    original_map = map_path.read_bytes()
    for site in ('inputs', 'clauses'):
        map_path.write_bytes(original_map)
        def add(obj):
            target = obj['inputs'] if site == 'inputs' else obj['clauses'][0]
            target.update({key: 'synthetic' for key in ('extra_a', 'extra_b', 'extra_c', 'extra_d', 'extra_e')})
        edit_artifact_block(map_path, 'contract_map', add)
        for seed in ('1', '2', '3'):
            result = native_and_optional_parity('reader-contract-outline', folder, '--strict', env=dict(os.environ, PYTHONHASHSEED=seed))
            assert result.returncode == 1 and b'unknown key' in result.stdout


def test_guide_source_precedence_and_citation_containment(tmp_path):
    folder = tmp_path / 'nested/run'
    folder.mkdir(parents=True)
    guide = folder / 'Project_Results_Guide_r1.md'
    guide.write_text('# Guide\n\n### Is the structure working?\n\nSee `inside.md`.\n', encoding='utf-8')
    (folder / 'inside.md').write_text('Synthetic\n', encoding='utf-8')
    source = tmp_path / 'pass-dependencies.md'
    pd = (REFERENCES / 'pass-dependencies.md').read_text(encoding='utf-8')
    source.write_text(pd, encoding='utf-8')
    first = native_and_optional_parity('results-guide', folder)
    assert first.returncode == 0 and b'R1 skipped' not in first.stdout
    local = folder / 'pass-dependencies.md'
    local.write_text(pd.replace('Is the structure working?', 'A different question?'), encoding='utf-8')
    assert native_and_optional_parity('results-guide', folder).returncode == 1
    local.unlink()
    guide.write_text('# Guide\n\n### Is the structure working?\n\nSee `../../outside.md`.\n', encoding='utf-8')
    (tmp_path / 'outside.md').write_text('Exists outside\n', encoding='utf-8')
    assert native_and_optional_parity('results-guide', folder).returncode == 1
    guide.write_bytes(b'\xff')
    assert native_and_optional_parity('results-guide', folder).returncode == 1


def test_position_pair_quote_drop_strict_and_role_read_errors(tmp_path):
    folder = tmp_path / 'position'
    shutil.copytree(POSITION_REFERENCES, folder)
    artifact, envelope, manuscript = (folder / name for name in ('Example_Position_Pair_Register_run.md', 'envelope.json', 'manuscript.txt'))
    obj = json.loads(envelope.read_text(encoding='utf-8'))
    obj['results']['pairs'][0]['a']['quote'] = 'A quote absent from the source.'
    envelope.write_text(json.dumps(obj), encoding='utf-8')
    result = native_and_optional_parity('position-pair-register', artifact, envelope, manuscript, 'ignored')
    assert result.returncode == 0 and b'pairs_dropped_quote_mismatch=' in result.stdout
    assert native_and_optional_parity('position-pair-register', artifact, envelope, manuscript, '--strict').returncode == 1
    envelope.write_text('{invalid', encoding='utf-8')
    assert native_and_optional_parity('position-pair-register', artifact, envelope, manuscript).returncode == 1
    artifact.write_bytes(b'\xff')
    assert native_and_optional_parity('position-pair-register', artifact, envelope, manuscript).returncode == 1


@pytest.mark.parametrize('command,mode', [('manuscript-viz', 'render'), ('annotated-manuscript', 'build'),
                                        ('crosslink', 'render'), ('reader-contract-outline', 'build'), ('reanchor', 'emit')])
def test_wrapper_mode_words_never_enable_producer_writes(tmp_path, command, mode):
    folder = tmp_path / 'inputs'
    source = 'example-reader-contract-outline' if command == 'reader-contract-outline' else 'example-annotated-manuscript'
    shutil.copytree(REFERENCES / source, folder)
    before = tree_contents(tmp_path)
    native_and_optional_parity(command, mode, folder, '-o', tmp_path / 'unexpected.html')
    assert tree_contents(tmp_path) == before


@pytest.mark.parametrize('root_name', ['ordinary', 'colon: PASS', 'prój\nPASS'])
def test_viz_self_test_exact_output_with_real_temp_roots(tmp_path, root_name):
    root = tmp_path / root_name
    try:
        root.mkdir()
    except OSError:
        pytest.skip('Host forbids this temporary directory spelling')
    env = dict(os.environ, TMPDIR=str(root), TEMP=str(root), TMP=str(root))
    result = native_and_optional_parity('manuscript-viz', '--self-test', env=env)
    assert result.returncode == 0 and result.stdout.endswith(b'Self-test: PASS\n')
    assert b'  render_force_reordered: OK\n' in result.stdout
    assert b'  render_in_order_ok: OK\n' in result.stdout
    assert b'manuscript-viz: rendered ' not in result.stdout
    assert result.stderr  # Stable intentional render refusal remains public.
    assert not list(root.iterdir())


@pytest.fixture
def viz_helper_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location('cb1_viz_capture_test', SCRIPTS / 'viz_manifest.py')
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


@pytest.mark.parametrize('positive_site', [0, 1], ids=['forced-render', 'ordered-render'])
@pytest.mark.parametrize('fault', ['silent', 'extra-output', 'nonzero', 'exception'])
def test_viz_positive_render_capture_refuses_fault_and_restores_stdout(viz_helper_module, monkeypatch, tmp_path, positive_site, fault):
    from contextlib import redirect_stdout, redirect_stderr
    from io import StringIO
    import tempfile
    module = viz_helper_module
    original = module.main
    real_mkdtemp = tempfile.mkdtemp
    made = []
    def create(*args, **kwargs):
        kwargs['dir'] = str(tmp_path)
        path = real_mkdtemp(*args, **kwargs)
        made.append(Path(path))
        return path
    monkeypatch.setattr(tempfile, 'mkdtemp', create)
    positive = 0
    injected = RuntimeError('render exception control')
    def render(argv):
        nonlocal positive
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = original(argv)
        sys.stderr.write(err.getvalue())
        if rc != 0:
            sys.stdout.write(out.getvalue())
            return rc
        site = positive
        positive += 1
        if site != positive_site:
            sys.stdout.write(out.getvalue())
            return rc
        if fault == 'exception':
            raise injected
        if fault != 'silent':
            sys.stdout.write(out.getvalue())
        if fault == 'extra-output':
            print('unexpected diagnostic')
        return 7 if fault == 'nonzero' else 0
    monkeypatch.setattr(module, 'main', render)
    public, errors = StringIO(), StringIO()
    with redirect_stdout(public), redirect_stderr(errors):
        if fault == 'exception':
            with pytest.raises(RuntimeError) as caught:
                module.run_self_test()
            assert caught.value is injected
        else:
            assert module.run_self_test() == 1
        assert sys.stdout is public
    name = 'render_force_reordered' if positive_site == 0 else 'render_in_order_ok'
    if fault != 'exception':
        assert f'  {name}: FAIL\n' in public.getvalue()
        assert public.getvalue().endswith('Self-test: FAIL\n')
        assert '  w3_beat_map_coverage_strict_fails: OK\n' in public.getvalue()
        assert not any(path.exists() for path in made)
    else:
        assert f'  {name}: OK\n' not in public.getvalue()
        # Preserve inherited exceptional cleanup limits; remove probe leftovers ourselves.
        for path in made:
            shutil.rmtree(path, ignore_errors=True)
    assert errors.getvalue()  # Negative render refusal stderr was not swallowed.


@pytest.mark.parametrize("command", ARGUMENT_EVALUATORS)
def test_argument_evaluator_first_self_test_is_exact(command):
    result = parity(command, "--self-test", "ignored")
    assert result.returncode == 0


@pytest.mark.parametrize("command", ARGUMENT_EVALUATORS)
def test_argument_evaluator_raw_wrapper_minimum_and_late_tokens(command, tmp_path):
    parity(command)
    parity(command, "--not-a-real-option", "--self-test", tmp_path / "missing")


def test_argument_evaluator_public_canonical_inputs():
    argument = ROOT / "evals/fixtures/argument-benchmark"
    fiction = ROOT / "evals/fixtures/fiction-benchmark"
    for path in (*argument.glob("*/groundtruth.md"), *argument.glob("*/*/groundtruth.md")):
        assert parity("argument-groundtruth-check", path).returncode == 0
    for path in (*fiction.glob("*/groundtruth.md"), *fiction.glob("*/*/groundtruth.md")):
        assert parity("fiction-groundtruth-check", path).returncode == 0
    for clean in argument.glob("*/clean/groundtruth.md"):
        pair = clean.parent.parent
        assert parity("argument-groundtruth-check", "--repair-diff", pair / "broken/fixture.md",
                      pair / "clean/fixture.md", clean).returncode == 0
    assert parity("argument-groundtruth-check", "--round-record",
                  ROOT / "docs/argument-benchmark-calibration-round.md", "--fixtures-dir", argument).returncode == 0
    crosswalk = ROOT / "evals/argument-crosswalk/crosswalk.json"
    for args in ((), (crosswalk,), ("--check", crosswalk)):
        assert parity("argument-crosswalk-check", *args).returncode == 0
    for state in (ROOT / "evals/fixtures/argument-agd").glob("*/argument-state.md"):
        args = [state, "--source", state.with_name("source.md")]
        scan = state.with_name("agd_move_scan.json")
        if scan.exists():
            args.extend(("--scan", scan))
        assert parity("argument-agd", *args, "--strict").returncode == 0
    for artifact, source in (
        (ROOT / "evals/fixtures/argument-aif/final-audit/export.json",
         ROOT / "evals/fixtures/argument-aif/final-audit/argument-state.md"),
        (REFERENCES / "example-argument-aif-export.json", REFERENCES / "example-argument-aif-state.md"),
    ):
        assert parity("argument-aif-check", artifact, "--source", source).returncode == 0


def test_argument_alpha_synthetic_seed_floor_and_panel(tmp_path):
    ratings = tmp_path / "ratings.csv"
    ratings.write_text("rater,unit,value\na,1,1\nb,1,1\nc,1,1\na,2,2\nb,2,2\nc,2,2\n"
                       "a,3,1\nb,3,2\nc,3,1\na,4,2\nb,4,2\nc,4,1\n", encoding="utf-8")
    args = ("agreement-alpha", ratings, "--seed", "17", "--resamples", "1000")
    first = parity(*args)
    assert first.returncode == 0
    assert first.stdout == parity(*args).stdout
    assert parity("agreement-alpha", ratings, "--resamples", "999").returncode != 0
    assert parity("agreement-alpha", ratings, "--metric", "ordinal", "--seed", "17").returncode == 0
    ratings.write_text("rater,unit,value\na,1,1\nb,1,1\na,2,2\nb,2,2\n", encoding="utf-8")
    assert parity("agreement-alpha", ratings).returncode == 2


@pytest.mark.parametrize("variant", [
    "file", "stdout", "empty-out", "dash", "strict", "unsupported", "missing-parent",
    "symlink", "same-source", "invalid-utf8", "blocking-loss", "schema-03", "schema-04",
])
def test_argument_aif_export_effects_match_from_identical_temporary_state(tmp_path, variant):
    if BASH is None:
        pytest.skip("Bash differential oracle unavailable")
    tree = tmp_path / "aif"
    canonical = ROOT / "evals/fixtures/argument-aif/final-audit/argument-state.md"

    def setup():
        if tree.exists():
            shutil.rmtree(tree)
        tree.mkdir()
        source = tree / "argument-state.md"
        source.write_bytes(canonical.read_bytes())
        if variant == "invalid-utf8":
            source.write_bytes(b"\xff")
        if variant == "blocking-loss":
            source.write_bytes((ROOT / "evals/fixtures/argument-aif/mixed-support/argument-state.md").read_bytes())
        destination = tree / "export.json"
        destination.write_bytes(b"sentinel")
        destination.chmod(0o640)
        referent = tree / "referent.json"
        if variant == "symlink":
            referent.write_bytes(b"referent")
            referent.chmod(0o640)
            destination.unlink()
            destination.symlink_to(referent)
        schema = {"unsupported": "9.9.9", "schema-03": "0.3.0", "schema-04": "0.4.0"}.get(variant, "0.2.0")
        args = [str(source), "--state-schema", schema]
        if variant == "strict":
            args.append("--strict")
        if variant == "file" or variant in ("unsupported", "invalid-utf8", "blocking-loss", "strict", "symlink", "schema-03", "schema-04"):
            args.extend(("--out", str(destination)))
        elif variant == "empty-out":
            args.extend(("--out", ""))
        elif variant == "dash":
            args.extend(("--out", str(tree / "-")))
        elif variant == "missing-parent":
            args.extend(("--out", str(tree / "missing/export.json")))
        elif variant == "same-source":
            args.extend(("--out", str(source)))
        return args

    def snapshot():
        result = {}
        for path in tree.rglob("*"):
            relative = str(path.relative_to(tree))
            if path.is_symlink():
                result[relative] = ("symlink", os.readlink(path))
            elif path.is_file():
                result[relative] = ("file", path.read_bytes(), path.stat().st_mode & 0o777)
            else:
                result[relative] = ("dir", path.stat().st_mode & 0o777)
        return result

    arguments = setup()
    legacy = subprocess.run([BASH, str(BASH_CLI), "argument-aif-export", *arguments],
                            cwd=ROOT, capture_output=True, timeout=60)
    legacy_effects = snapshot()
    assert setup() == arguments
    native = run_python("argument-aif-export", *arguments)
    assert (native.returncode, native.stdout, native.stderr, snapshot()) == (
        legacy.returncode, legacy.stdout, legacy.stderr, legacy_effects)
    if variant in ("file", "symlink", "schema-03", "schema-04"):
        artifact = tree / "export.json"
        assert artifact.stat().st_mode & 0o777 == 0o600
        assert parity("argument-aif-check", artifact, "--source", tree / "argument-state.md").returncode == 0
    if variant == "file":
        assert (tree / "export.json").read_bytes() == (
            ROOT / "evals/fixtures/argument-aif/final-audit/export.json").read_bytes()
    if variant in ("strict", "unsupported", "invalid-utf8", "blocking-loss", "missing-parent"):
        assert native.returncode != 0


def test_argument_aif_checker_source_closure_and_canonical_bytes(tmp_path):
    source = tmp_path / "argument-state.md"
    source.write_bytes((ROOT / "evals/fixtures/argument-aif/final-audit/argument-state.md").read_bytes())
    artifact = tmp_path / "export.json"
    assert run_python("argument-aif-export", source, "--state-schema", "0.2.0", "--out", artifact).returncode == 0
    original = artifact.read_bytes()
    assert parity("argument-aif-check", artifact).returncode == 0
    assert parity("argument-aif-check", artifact, "--source", source).returncode == 0
    assert parity("argument-aif-check", artifact, "--source", "").returncode != 0
    artifact.write_bytes(original.replace(b"\n", b"\r\n", 1))
    assert parity("argument-aif-check", artifact).returncode != 0
    artifact.write_bytes(original)
    source.write_bytes(source.read_bytes().replace(b"\n", b"\r\n", 1))
    assert parity("argument-aif-check", artifact, "--source", source).returncode != 0
    assert artifact.read_bytes() == original


def test_argument_evaluators_run_without_path_or_bash(tmp_path):
    env = dict(os.environ, PATH="", PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    for command in ARGUMENT_EVALUATORS:
        result = run_python(command, "--self-test", env=env)
        assert result.returncode == 0
        assert b"Self-test: PASS" in result.stdout
    source = tmp_path / "argument-state.md"
    source.write_bytes((ROOT / "evals/fixtures/argument-aif/final-audit/argument-state.md").read_bytes())
    artifact = tmp_path / "export.json"
    assert run_python("argument-aif-export", source, "--state-schema", "0.2.0", "--out", artifact,
                      env=env).returncode == 0
    assert run_python("argument-aif-check", artifact, "--source", source, env=env).returncode == 0
    assert artifact.read_bytes() == (ROOT / "evals/fixtures/argument-aif/final-audit/export.json").read_bytes()


def test_argument_evaluator_hostile_helper_owned_modes(tmp_path):
    bad = tmp_path / "bad.md"
    bad.write_bytes(b"\xff")
    assert parity("argument-groundtruth-check", bad).returncode != 0
    assert parity("fiction-groundtruth-check", bad).returncode != 0
    assert parity("argument-groundtruth-check", "--repair-diff", bad).returncode != 0
    # An unbooked round is the helper's existing vacuous success.
    assert parity("argument-groundtruth-check", "--round-record", bad, "--fixtures-dir", tmp_path).returncode == 0
    assert parity("argument-crosswalk-check", tmp_path / "missing.json").returncode != 0
    assert parity("argument-agd", bad, "--source", bad, "--strict").returncode != 0


def test_argument_groundtruth_pair_path_and_round_booking(tmp_path):
    original = ROOT / "evals/fixtures/argument-benchmark/policy-brief-uncompared/clean/groundtruth.md"
    flat = tmp_path / "groundtruth.md"
    flat.write_bytes(original.read_bytes())
    assert parity("argument-groundtruth-check", flat).returncode != 0
    wrong = tmp_path / "wrong-pair/clean"
    wrong.mkdir(parents=True)
    (wrong / "groundtruth.md").write_bytes(original.read_bytes())
    assert parity("argument-groundtruth-check", wrong / "groundtruth.md").returncode != 0
    record = tmp_path / "round.md"
    record.write_text("- BOOKED: ENGINE-FAULT absent-fixture GT2\n", encoding="utf-8")
    assert parity("argument-groundtruth-check", "--round-record", record,
                  "--fixtures-dir", ROOT / "evals/fixtures/argument-benchmark").returncode != 0


def test_argument_agd_source_and_scan_edges(tmp_path):
    base = ROOT / "evals/fixtures/argument-agd/cue-free-structural-discounting"
    state = base / "argument-state.md"
    source = base / "source.md"
    scan = base / "agd_move_scan.json"
    assert parity("argument-agd", state, "--source", source, "--scan", scan, "--strict").returncode == 0
    assert parity("argument-agd", state, "--source", tmp_path / "missing.md", "--strict").returncode != 0
    assert parity("argument-agd", state, "--scan", tmp_path / "missing.json", "--strict").returncode != 0
    corrupt = tmp_path / "scan.json"
    corrupt.write_text("{", encoding="utf-8")
    assert parity("argument-agd", state, "--scan", corrupt, "--strict").returncode != 0


@pytest.mark.parametrize("fixture", [
    "mixed-support", "mixed-warrant", "carrier-disagreement", "bad-carrier-missing",
    "bad-carrier-enum", "bad-carrier-extra", "fallback-c99", "extra-final-record",
])
def test_argument_aif_public_hostile_export_preserves_destination(tmp_path, fixture):
    if BASH is None:
        pytest.skip("Bash differential oracle unavailable")
    source = ROOT / "evals/fixtures/argument-aif" / fixture / "argument-state.md"
    out = tmp_path / "export.json"
    def reset():
        out.write_bytes(b"sentinel")
        out.chmod(0o640)

    def effects():
        return (out.read_bytes(), out.stat().st_mode & 0o777,
                sorted(p.name for p in tmp_path.iterdir()))

    expected = (b"sentinel", 0o640, ["export.json"])
    reset()
    assert effects() == expected
    args = ("argument-aif-export", source, "--state-schema", "0.2.0", "--out", out)
    legacy = subprocess.run([BASH, str(BASH_CLI), *map(str, args)], cwd=ROOT,
                            capture_output=True, timeout=60)
    legacy_effects = effects()
    assert legacy.returncode != 0
    assert legacy_effects == expected
    reset()
    assert effects() == expected
    native = run_python(*args)
    native_effects = effects()
    assert (native.returncode, native.stdout, native.stderr) == (
        legacy.returncode, legacy.stdout, legacy.stderr)
    assert native_effects == legacy_effects == expected


@pytest.mark.parametrize("fixture", [
    "final-audit", "final-over-predraft", "predraft-complete", "predraft-partial",
])
def test_argument_aif_public_positive_generations_have_same_artifact(tmp_path, fixture):
    if BASH is None:
        pytest.skip("Bash differential oracle unavailable")
    source = tmp_path / "argument-state.md"
    source.write_bytes((ROOT / "evals/fixtures/argument-aif" / fixture / "argument-state.md").read_bytes())
    out = tmp_path / "export.json"
    args = ("argument-aif-export", source, "--state-schema", "0.2.0", "--out", out)
    bash = subprocess.run([BASH, str(BASH_CLI), *map(str, args)], cwd=ROOT,
                          capture_output=True, timeout=60)
    assert bash.returncode == 0
    original = out.read_bytes()
    mode = out.stat().st_mode & 0o777
    out.unlink()
    native = run_python(*args)
    assert (native.returncode, native.stdout, native.stderr) == (bash.returncode, bash.stdout, bash.stderr)
    assert out.read_bytes() == original
    assert out.stat().st_mode & 0o777 == mode
    assert sorted(p.name for p in tmp_path.iterdir()) == ["argument-state.md", "export.json"]
    assert parity("argument-aif-check", out, "--source", source).returncode == 0


@pytest.mark.parametrize("command", ANNOTATION_EXPORTS)
def test_annotation_export_wrapper_and_helper_boundaries(command):
    assert parity(command).returncode == 2
    assert parity(command, "missing-folder", "--self-test").returncode == 0
    if command != "pdf-export":
        assert parity(command, "--self-test", "ignored").returncode == 0
    empty_path = {**os.environ, "PATH": "", "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    late = run_python(command, "missing-folder", "--self-test", env=empty_path)
    assert (late.returncode, late.stderr) == (0, b"")
    assert late.stdout.endswith(b"Self-test: PASS\n")


@pytest.mark.parametrize("command,args,expected", [
    ("obsidian-export", ("x", "--internal-links"), b"pdf-export: usage: pdf-export <run_folder> --internal-links (once)\n"),
    ("html-export", ("--self-test", "--internal-links"), b"pdf-export: usage: pdf-export <run_folder> --internal-links (once)\n"),
    ("docx-export", ("x", "--internal-links=true"), b"pdf-export: usage: pdf-export <run_folder> --internal-links (once)\n"),
    ("pdf-export", ("x", "--internal-links", "extra"), b"pdf-export: usage: pdf-export <run_folder> --internal-links (once)\n"),
    ("pdf-export", ("x", "--internal-links", "--internal-links"), b"pdf-export: usage: pdf-export <run_folder> --internal-links (once)\n"),
    ("pdf-export", ("--self-test", "--internal-links"), b"pdf-export: usage: misplaced navigation option\n"),
    ("pdf-export", ("--", "--internal-links"), b"pdf-export: usage: misplaced navigation option\n"),
    ("pdf-export", ("--internal-links", ""), b"pdf-export: N run folder unavailable\n"),
])
def test_annotation_export_navigation_scanner_precedes_helper(command, args, expected):
    result = parity(command, *args)
    assert (result.returncode, result.stdout, result.stderr) == (2, expected, b"")


def _navigation_success(stderr):
    match = re.fullmatch(
        rb"([.s]+\n-{70}\nRan (\d+) tests in )([0-9]+(?:\.[0-9]+)?)(s\n\nOK(?: \(skipped=\d+\))?\n)",
        stderr,
    )
    assert match is not None, stderr
    count = int(match.group(2))
    elapsed = float(match.group(3))
    assert count > 0 and math.isfinite(elapsed) and elapsed > 0
    assert len(match.group(1).split(b"\n", 1)[0]) == count
    return count, match.group(1), match.group(4)


def test_pdf_first_selftest_runs_actual_repository_navigation_suite():
    env = {**os.environ, "TMPDIR": os.environ.get("TMPDIR", "/private/tmp"),
           "PYTHONWARNINGS": "ignore", "PYTHONDONTWRITEBYTECODE": "1"}
    shared = subprocess.run([sys.executable, str(SCRIPTS / "annotation_export.py"), "--self-test"],
                            env=env, capture_output=True, timeout=60)
    bash = subprocess.run([BASH, str(BASH_CLI), "pdf-export", "--self-test"],
                          env=env, capture_output=True, timeout=60) if BASH else None
    native = run_python("pdf-export", "--self-test", "ignored", env=env)
    assert (shared.returncode, shared.stderr) == (0, b"")
    assert (native.returncode, native.stdout) == (0, shared.stdout)
    count, before, after = _navigation_success(native.stderr)
    assert after.startswith(b"s\n\nOK")
    if bash is not None:
        assert (bash.returncode, bash.stdout) == (native.returncode, native.stdout)
        bash_count, bash_before, bash_after = _navigation_success(bash.stderr)
        assert (bash_count, bash_before, bash_after) == (count, before, after)
    pathless = run_python("pdf-export", "--self-test", env={**env, "PATH": ""})
    assert (pathless.returncode, pathless.stdout) == (0, shared.stdout)
    pathless_count, _, pathless_result = _navigation_success(pathless.stderr)
    assert pathless_count == count and pathless_result.startswith(b"s\n\nOK")
    skipped = re.search(rb"skipped=(\d+)", pathless_result)
    assert skipped is None or int(skipped.group(1)) < pathless_count


def test_pdf_repository_continuation_marker_and_failure(tmp_path):
    scripts = tmp_path / "plugins/apodictic/scripts"
    scripts.mkdir(parents=True)
    shutil.copyfile(PYTHON_CLI, scripts / "validate.py")
    helper = scripts / "annotation_export.py"
    helper.write_text("import os, sys\nprint('shared:' + repr(sys.argv[1:]))\nsys.exit(int(os.environ.get('G12_HELPER_RC', '0')))\n", encoding="utf-8")
    def invoke(env=None):
        return subprocess.run([sys.executable, str(scripts / "validate.py"), "pdf-export", "--self-test"],
                              capture_output=True, env={**os.environ, **(env or {})}, timeout=30)
    alone = invoke()
    assert (alone.returncode, alone.stdout, alone.stderr) == (0, b"shared:['--self-test']\n", b"")
    (tmp_path / "AGENTS.md").write_text("repository marker\n", encoding="utf-8")
    missing = invoke()
    assert (missing.returncode, missing.stdout, missing.stderr) == (
        2, b"shared:['--self-test']\npdf-export: N repository navigation acceptance suite unavailable\n", b"")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_pdf_navigation.py").write_text("print('navigation suite ran')\nraise SystemExit(7)\n", encoding="utf-8")
    failing = invoke()
    assert (failing.returncode, failing.stdout, failing.stderr) == (
        7, b"shared:['--self-test']\nnavigation suite ran\n", b"")
    blocked = invoke({"G12_HELPER_RC": "5"})
    assert (blocked.returncode, blocked.stdout, blocked.stderr) == (5, b"shared:['--self-test']\n", b"")
    helper.unlink()
    unavailable = subprocess.run([sys.executable, str(scripts / "validate.py"), "pdf-export",
                                  "run", "--internal-links"], capture_output=True, timeout=30)
    assert (unavailable.returncode, unavailable.stdout, unavailable.stderr) == (
        2, b"pdf-export: N navigation validation unavailable (Python/helper missing)\n", b"")


@pytest.mark.parametrize("verb", ("obsidian", "html", "docx", "pdf"))
def test_annotation_exports_validate_authentic_goldens_without_writes(tmp_path, verb):
    source = REFERENCES / "example-annotated-manuscript"
    for path in source.iterdir():
        if path.is_file() and ("_Manuscript_Snapshot_" in path.name or "_Annotation_Manifest_" in path.name
                               or (verb == "obsidian" and "_Crosslinked_Letter_" in path.name)):
            shutil.copy2(path, tmp_path / path.name)
    command = verb + "-export"
    before_producer = sorted(path.name for path in tmp_path.iterdir())
    attempted_alias = run_python(command, verb, tmp_path, cwd=tmp_path)
    assert attempted_alias.returncode == 2
    assert sorted(path.name for path in tmp_path.iterdir()) == before_producer
    missing = run_python(command, tmp_path)
    assert missing.returncode == 2 and b"run `annotation_export.py" in missing.stdout
    producer = subprocess.run([sys.executable, str(SCRIPTS / "annotation_export.py"), verb, str(tmp_path)],
                              capture_output=True, timeout=60)
    assert (producer.returncode, producer.stderr) == (0, b"")
    exported = sorted(path for path in (tmp_path / verb).iterdir() if path.is_file())
    assert len(exported) == (2 if verb == "obsidian" else 1)
    for path in exported:
        golden = (source if verb in ("obsidian", "html") else ROOT / "evals/fixtures/annotation-export") / verb / path.name
        assert golden.is_file() and path.read_bytes() == golden.read_bytes()
    def tree():
        return {str(path.relative_to(tmp_path)): (hashlib.sha256(path.read_bytes()).digest(),
                                                   path.stat().st_mode & 0o777)
                for path in tmp_path.rglob("*") if path.is_file()}
    before = tree()
    if BASH:
        legacy = subprocess.run([BASH, str(BASH_CLI), command, str(tmp_path)], capture_output=True, timeout=60)
        assert tree() == before
    native = run_python(command, tmp_path, env={**os.environ, "PATH": ""})
    assert native.returncode == 0 and native.stderr == b"" and b"PASS" in native.stdout
    assert tree() == before
    if BASH:
        assert (native.returncode, native.stdout, native.stderr) == (
            legacy.returncode, legacy.stdout, legacy.stderr)
        assert parity(command, tmp_path, "--", "ignored").returncode == 0
        assert parity(command, tmp_path, "--strict").returncode == 0
        repeated = parity(command, command, tmp_path, cwd=tmp_path)
        assert repeated.returncode == (0 if verb == "obsidian" else 2)
        assert tree() == before


def test_pdf_linked_mode_authenticates_and_checks_existing_artifact(tmp_path):
    from test_pdf_navigation import normal_run

    normal_run(tmp_path)
    absent = run_python("pdf-export", tmp_path, "--internal-links", env={**os.environ, "PATH": ""})
    assert absent.returncode == 2 and b"linked PDF selection is missing" in absent.stdout
    produced = subprocess.run([sys.executable, str(SCRIPTS / "annotation_export.py"), "pdf",
                               str(tmp_path), "--internal-links"], capture_output=True, timeout=60)
    assert (produced.returncode, produced.stderr) == (0, b"")
    artifact = next((tmp_path / "pdf-linked").glob("*.pdf"))
    before = artifact.read_bytes()
    for args in ((tmp_path, "--internal-links"), ("--internal-links", tmp_path)):
        result = parity("pdf-export", *args)
        assert result.returncode == 0 and b"reader unqualified" in result.stdout
        assert artifact.read_bytes() == before
        pathless = run_python("pdf-export", *args, env={**os.environ, "PATH": ""})
        assert (pathless.returncode, pathless.stdout, pathless.stderr) == (
            result.returncode, result.stdout, result.stderr)
    artifact.write_bytes(before[:-1] + b"X")
    tampered = parity("pdf-export", tmp_path, "--internal-links")
    assert tampered.returncode == 1 and b"P1 artifact integrity" in tampered.stdout


REPOSITORY_INTEGRITY = (
    'registry-check', 'schema-coverage', 'validator-conventions',
    'calibration-honesty', 'stance-calibration', 'argument-carve-behavior-preservation',
)


@pytest.mark.parametrize('command', REPOSITORY_INTEGRITY)
def test_repository_integrity_real_selftests_and_empty_path(command):
    result = native_and_optional_parity(command, '--self-test', 'discarded')
    assert result.returncode == 0
    env = {**os.environ, 'PATH': '', 'PYTHONUTF8': '1', 'PYTHONIOENCODING': 'utf-8'}
    native = run_python(command, '--self-test', 'discarded', env=env)
    assert (native.returncode, native.stdout, native.stderr) == (result.returncode, result.stdout, result.stderr)
    if command == 'validator-conventions':
        assert native.stdout.startswith(b'  ho_genuine_emdash: OK (found)\n')
        assert b'  ho_multiline_inline_decoy: OK (miss)\n' in native.stdout
        late = parity(command, 'ignored', '--self-test')
        assert late.returncode == 0 and b'  ho_' not in late.stdout


@pytest.mark.parametrize('command', REPOSITORY_INTEGRITY)
@pytest.mark.parametrize('args', [('--internal-links',), ('--internal-links=true',),
                                  ('--self-test', '--internal-links'),
                                  ('--', '--internal-links'), ('--internal-links', '--internal-links')])
def test_repository_integrity_scanner_before_every_route(command, args):
    result = parity(command, *args)
    assert (result.returncode, result.stdout, result.stderr) == (
        2, b'pdf-export: usage: pdf-export <run_folder> --internal-links (once)\n', b'')


@pytest.mark.parametrize('command,args,rc', [
    ('registry-check', (), 2), ('registry-check', ('--strict',), 2),
    ('registry-check', ('missing',), 2), ('registry-check', ('missing', '--self-test'), 0),
    ('schema-coverage', (), 0), ('schema-coverage', ('--strict',), 0),
    ('schema-coverage', ('--check-docs',), 0), ('schema-coverage', ('--check-docs', '--unknown'), 0),
    ('schema-coverage', ('missing',), 2), ('schema-coverage', ('missing', '--self-test'), 0),
    ('validator-conventions', (), 0), ('validator-conventions', ('ignored', '--strict'), 0),
    ('calibration-honesty', (), 2), ('calibration-honesty', ('--strict',), 2),
    ('calibration-honesty', ('missing',), 2), ('calibration-honesty', ('missing', '--self-test'), 0),
    ('stance-calibration', (), 2), ('stance-calibration', ('missing', '--self-test'), 2),
    ('stance-calibration', ('missing', '--self-test', 'extra'), 0),
    ('stance-calibration', ('missing', 'extra', '--argument-state'), 2),
])
def test_repository_integrity_raw_wrapper_boundaries(command, args, rc):
    assert parity(command, *args).returncode == rc


@pytest.mark.parametrize('payload,rc', [(b'{', 1), (b'[]', 1), (b'\xff', 2),
    (b'{"schema":"apodictic.project_registry.v1","projects":[]}', 0)])
def test_registry_public_shape_reads_and_first_path(tmp_path, payload, rc):
    workspace = tmp_path / 'workspace café'
    registry = workspace / '.apodictic/registry.json'
    registry.parent.mkdir(parents=True)
    registry.write_bytes(payload)
    for args in ((workspace,), (registry,), ('registry-check', registry, 'ignored'),
                 ('--unknown', registry, '--strict', 'ignored')):
        assert parity('registry-check', *args).returncode == rc
    assert parity('registry-check', 'missing', registry).returncode == 2


def test_schema_public_directory_and_docs_modes(tmp_path):
    schemas = tmp_path / 'schemas'
    schemas.mkdir()
    assert parity('schema-coverage', schemas).returncode == 1
    (schemas / '_coverage.json').write_bytes(b'{')
    assert parity('schema-coverage', schemas, 'ignored').returncode == 1
    (schemas / '_coverage.json').write_bytes(b'[]')
    assert parity('schema-coverage', schemas, '--check-docs', '--strict').returncode == 1
    assert parity('schema-coverage', 'schema-coverage', '--check-docs').returncode == 0
    assert parity('schema-coverage', '--check-docs', 'missing').returncode == 2


def test_calibration_public_resolution_qualifiers_and_overrides(tmp_path):
    clean = tmp_path / 'Old_Core_DE_Synthesis_r1.md'
    bad = tmp_path / 'New_Core_DE_Synthesis_r2.md'
    clean.write_text('# Letter\n\nThe op-ed scores in the AI-elevated band, uncalibrated.\n', encoding='utf-8')
    bad.write_text('# Letter\n\nThe op-ed scores in the AI-elevated band.\n', encoding='utf-8')
    os.utime(clean, (100, 100)); os.utime(bad, (200, 200))
    assert parity('calibration-honesty', tmp_path, '--strict').returncode == 1
    assert parity('calibration-honesty', clean, bad, '--strict').returncode == 0
    assert parity('calibration-honesty', bad, '--unknown').returncode == 0
    binary = tmp_path / 'binary.md'; binary.write_bytes(b'\xff')
    assert parity('calibration-honesty', binary).returncode == 2
    assert parity('calibration-honesty', binary, clean, '--strict').returncode == 0
    assert parity('calibration-honesty', 'calibration-honesty', clean, '--strict').returncode == 0
    bad.write_text('# Letter\n\nThe op-ed scores in the AI-elevated band. '
                   '<!-- override: calibration-honesty — synthetic reason -->\n', encoding='utf-8')
    assert parity('calibration-honesty', tmp_path, '--strict').returncode == 0
    assert parity('calibration-honesty', '', '--strict').returncode == 2


def test_stance_public_join_and_raw_parser_errors(tmp_path):
    source = ROOT / 'evals/fixtures/stance-calibration/clean'
    ledger = tmp_path / 'Findings_Ledger.md'; state = tmp_path / 'Argument_State.md'
    shutil.copy2(source / ledger.name, ledger); shutil.copy2(source / state.name, state)
    assert parity('stance-calibration', ledger, '--argument-state', state).returncode == 0
    for args in ((ledger, '--argument-state', state, 'extra'),
                 (ledger, '--argument-state', state, '--strict'),
                 ('--argument-state', state, ledger),
                 (ledger, '--argument-state', state, '--argument-state', state),
                 ('stance-calibration', ledger, '--argument-state', state)):
        assert parity('stance-calibration', *args).returncode == 2
    state.write_text(state.read_text().replace('CO1', 'CO9'), encoding='utf-8')
    assert parity('stance-calibration', ledger, '--argument-state', state).returncode == 1
    for target in (ledger, state):
        old = target.read_bytes(); target.write_bytes(b'\xff')
        assert parity('stance-calibration', ledger, '--argument-state', state).returncode == 2
        target.write_bytes(old)


@pytest.fixture
def repository_bundle(tmp_path):
    scripts = tmp_path / 'plugins/apodictic/scripts'
    shutil.copytree(SCRIPTS, scripts)
    shutil.copytree(SCRIPTS.parent / 'schemas', scripts.parent / 'schemas')
    fixtures = tmp_path / 'evals/fixtures/argument-carve/precarve'
    shutil.copytree(ROOT / 'evals/fixtures/argument-carve/precarve', fixtures)
    return scripts, fixtures


def _repository_copy_run(scripts, native, *args, env=None):
    if not native and BASH is None:
        pytest.skip('Bash differential oracle unavailable')
    entry = [sys.executable, str(scripts / 'validate.py')] if native else [BASH, str(scripts / 'validate.sh')]
    return subprocess.run([*entry, *map(str, args)], capture_output=True, timeout=60, env=env)


def _repository_copy_parity(scripts, *args):
    legacy = _repository_copy_run(scripts, False, *args)
    native = _repository_copy_run(scripts, True, *args)
    assert (native.returncode, native.stdout, native.stderr) == (legacy.returncode, legacy.stdout, legacy.stderr)
    return native


def _repository_effects(root):
    contents = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            value = ('symlink', os.readlink(path))
        elif path.is_file():
            try:
                value = path.read_bytes()
            except PermissionError:
                value = 'unreadable'
        else:
            value = None
        contents[str(path.relative_to(root))] = (path.lstat().st_mode & 0o777, value)
    return contents


@pytest.mark.parametrize('args', [(), ('--self-test', 'ignored'), ('ignored', '--self-test')])
def test_carve_actual_fixture_read_only_and_standalone_candidates(repository_bundle, tmp_path, args):
    scripts, fixtures = repository_bundle
    before = _repository_effects(tmp_path)
    assert _repository_copy_parity(scripts, 'argument-carve-behavior-preservation', *args).returncode == 0
    assert _repository_effects(tmp_path) == before
    second = scripts.parent / 'evals/fixtures/argument-carve/precarve'
    second.parent.mkdir(parents=True)
    shutil.copytree(fixtures, second)
    (second / 'propagation-output.txt').write_bytes(b'wrong\n')
    assert _repository_copy_parity(scripts, 'argument-carve-behavior-preservation', *args).returncode == 0
    shutil.rmtree(fixtures)
    assert _repository_copy_parity(scripts, 'argument-carve-behavior-preservation', *args).returncode == 1
    shutil.rmtree(second)
    skipped = _repository_copy_parity(scripts, 'argument-carve-behavior-preservation', *args)
    assert skipped.returncode == 0 and b'SKIP (evals/ not present' in skipped.stdout
    assert (b'Self-test: PASS\n' in skipped.stdout) == bool(args and args[0] == '--self-test')
    assert _repository_copy_parity(scripts, 'argument-carve-behavior-preservation', '--self-test', '--internal-links').returncode == 2


@pytest.mark.parametrize('selftest', [False, True])
@pytest.mark.parametrize('mutation', ['missing', 'multiple-missing', 'directory', 'symlink'])
def test_carve_actual_fixture_preflight_order(repository_bundle, selftest, mutation):
    scripts, fixtures = repository_bundle
    letter = fixtures / 'argument-editorial-letter.md'; letter.unlink()
    if mutation == 'multiple-missing': (fixtures / 'argument-findings-ledger.md').unlink()
    if mutation == 'directory': letter.mkdir()
    if mutation == 'symlink': letter.symlink_to(fixtures / 'absent')
    result = _repository_copy_parity(scripts, 'argument-carve-behavior-preservation', *(['--self-test'] if selftest else []))
    assert result.returncode == 1
    if selftest:
        assert result.stdout.count(b'missing:') == (2 if mutation == 'multiple-missing' else 1)
    else:
        assert b'fixture missing:' in result.stdout
    assert (b'Self-test: FAIL\n' in result.stdout) == selftest
    assert b'../../../evals/fixtures/argument-carve/precarve/argument-editorial-letter.md' in result.stdout


@pytest.mark.parametrize('selftest', [False, True])
@pytest.mark.parametrize('mutation', ['trailing-lf', 'no-final-lf', 'nul', 'crlf', 'multiline-binary', 'both-drift'])
def test_carve_raw_golden_bytes_and_no_writes(repository_bundle, tmp_path, selftest, mutation):
    scripts, fixtures = repository_bundle
    golden = fixtures / 'propagation-output.txt'; payload = golden.read_bytes()
    if mutation == 'trailing-lf': payload += b'\n\n'
    if mutation == 'no-final-lf': payload = payload.rstrip(b'\n')
    if mutation == 'nul': payload = payload[:2] + b'\0' + payload[2:]
    if mutation == 'crlf': payload = payload.replace(b'\n', b'\r\n')
    if mutation == 'multiline-binary': payload = b'wrong\n  spaced\xff\r\n'
    if mutation == 'both-drift':
        payload = b'wrong\n'; (fixtures / 'decision-layer-output.txt').write_bytes(b'also wrong\n')
    golden.write_bytes(payload)
    before = _repository_effects(tmp_path)
    result = _repository_copy_parity(scripts, 'argument-carve-behavior-preservation', *(['--self-test'] if selftest else []))
    assert result.returncode == (0 if mutation in ('trailing-lf', 'no-final-lf', 'nul') else 1)
    assert _repository_effects(tmp_path) == before


@pytest.mark.parametrize('selftest', [False, True])
@pytest.mark.parametrize('phase', ['first-child', 'matched-failure-goldens', 'second-child',
                                    'first-read', 'second-read', 'drift-second-child', 'drift-second-read',
                                    'first-child-before-read', 'second-child-before-read'])
def test_carve_real_failure_phases_no_false_pass(repository_bundle, tmp_path, selftest, phase):
    scripts, fixtures = repository_bundle
    lexical = str(scripts) + '/../../../evals/fixtures/argument-carve/precarve/'
    letter = fixtures / 'argument-editorial-letter.md'
    propagation = fixtures / 'propagation-output.txt'; decision = fixtures / 'decision-layer-output.txt'
    original_summary = propagation.read_bytes().rstrip(b'\n')
    if phase in ('first-child', 'matched-failure-goldens', 'first-child-before-read'):
        letter.write_text('# Invented public hostile letter\n\nhard gate\n', encoding='utf-8')
        if phase == 'matched-failure-goldens':
            for command, args, golden in (
                ('audit-signal-propagation', [lexical + letter.name, lexical + 'argument-findings-ledger.md'], propagation),
                ('decision-layer-check', [lexical + letter.name], decision),
            ):
                child = _repository_copy_parity(scripts, command, *args)
                assert child.returncode == 1
                golden.write_bytes(child.stdout.rstrip(b'\n').rsplit(b'\n', 1)[-1] + b'\n')
    if phase in ('second-child', 'drift-second-child', 'second-child-before-read'): letter.write_bytes(b'\xff\xfe')
    if phase.startswith('drift'): propagation.write_bytes(b'wrong\n')
    unreadable = (propagation if phase in ('first-read', 'first-child-before-read') else
                  decision if phase in ('second-read', 'drift-second-read', 'second-child-before-read') else None)
    if unreadable is not None:
        unreadable.chmod(0)
        if os.access(unreadable, os.R_OK):
            pytest.skip('Host bypasses mode restrictions; unreadable golden not exercised')
        with pytest.raises(PermissionError): unreadable.read_bytes()
    before = _repository_effects(tmp_path)
    args = ['argument-carve-behavior-preservation', *(['--self-test'] if selftest else [])]
    legacy = _repository_copy_run(scripts, False, *args)
    assert _repository_effects(tmp_path) == before
    native = _repository_copy_run(scripts, True, *args)
    assert _repository_effects(tmp_path) == before
    assert native.returncode == legacy.returncode == 1
    prefix = b'  fixture_present: OK (4 fixture files found)\n' if selftest else b''
    if phase in ('second-child', 'second-read', 'second-child-before-read') and selftest: prefix += b'  propagation_golden: OK\n'
    if phase.startswith('drift'):
        prefix += ((b'  propagation_golden: FAIL\n    expected: wrong\n    got:      ' if selftest else
                    b'ERROR: argument-carve-behavior-preservation: audit-signal-propagation output drifted from golden\n  expected: wrong\n  got:      ')
                   + original_summary + b'\n')
    assert native.stdout == legacy.stdout == prefix
    if unreadable is None or phase.endswith('before-read'):
        assert native.stderr == legacy.stderr == b''
    else:
        assert legacy.stderr == ('cat: ' + lexical + unreadable.name + ': Permission denied\n').encode()
        assert native.stderr == ('Error: Cannot read file: ' + lexical + unreadable.name + ': Permission denied\n').encode()


@pytest.mark.parametrize('helper', ['registry_check.py', 'schema_coverage.py', 'meta_lint.py',
                                   'calibration_honesty.py', 'stance_calibration.py', 'override_marker.py', 'letter_checks.py'])
def test_repository_missing_installation_never_fake_pass(repository_bundle, helper):
    scripts, _ = repository_bundle
    command = {'registry_check.py':'registry-check', 'schema_coverage.py':'schema-coverage',
               'meta_lint.py':'validator-conventions', 'calibration_honesty.py':'calibration-honesty',
               'stance_calibration.py':'stance-calibration', 'override_marker.py':'validator-conventions',
               'letter_checks.py':'argument-carve-behavior-preservation'}[helper]
    (scripts / helper).unlink()
    result = _repository_copy_run(scripts, True, command, '--self-test')
    assert result.returncode == 2 and b'Self-test: PASS' not in result.stdout
    if helper == 'letter_checks.py':
        assert result.stdout == b'  fixture_present: OK (4 fixture files found)\n' and result.stderr == b''
    else:
        assert helper.encode() in result.stderr


def test_carve_native_empty_path_executes_real_children_without_writes(repository_bundle, tmp_path):
    scripts, _ = repository_bundle
    env = {**os.environ, 'PATH': '', 'PYTHONUTF8': '1', 'PYTHONIOENCODING': 'utf-8'}
    before = _repository_effects(tmp_path)
    for args in ((), ('--self-test',)):
        result = _repository_copy_run(scripts, True, 'argument-carve-behavior-preservation', *args, env=env)
        assert result.returncode == 0 and result.stderr == b''
        assert result.stdout.endswith(b'Self-test: PASS\n' if args else
            b'argument-carve-behavior-preservation: PASS (smoke: resolvers still classify the argument fixture as Argument-DE post-carve; authoritative guarantee = audit-signal-propagation --check-registry + the byte-identical \xc2\xa74e diff)\n')
        assert _repository_effects(tmp_path) == before


@pytest.mark.parametrize('helper,command', [
    ('registry_check.py', 'registry-check'), ('schema_coverage.py', 'schema-coverage'),
    ('meta_lint.py', 'validator-conventions'), ('calibration_honesty.py', 'calibration-honesty'),
    ('stance_calibration.py', 'stance-calibration'),
])
def test_repository_regular_helper_symlink_stays_available(repository_bundle, helper, command):
    scripts, _ = repository_bundle
    target = scripts / ('target-' + helper)
    (scripts / helper).rename(target)
    (scripts / helper).symlink_to(target.name)
    assert _repository_copy_parity(scripts, command, '--self-test').returncode == 0
