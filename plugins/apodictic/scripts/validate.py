#!/usr/bin/env python3
"""Native validator dispatcher, CB-1(a) groups 1–4, 5a and 6–11.

Early utilities, signals, configuration, timelines and structured checks run without Bash.
Other commands and aggregates still belong to validate.sh until their groups land.
"""

import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


COMMANDS = (
    "contract-hash", "contract-check", "ledger-check", "artifact-names",
    "synthesis-sections", "tone-check", "state-lines",
)
_HELPERS = {
    "ledger-check": ("letter_checks.py", 1, "<ledger_file>"),
    "artifact-names": ("config_checks.py", 3, "<output_dir> <project_name> <runlabel>"),
    "synthesis-sections": ("letter_checks.py", 1, "<editorial_letter_file>"),
    "tone-check": ("letter_checks.py", 1, "<editorial_letter_file>"),
}
_LETTER_SIGNALS = {
    "author-facing-lint": "<editorial_letter_file> | --self-test",
    "severity-floor": "<editorial_letter_file> [<ledger_file>] | --self-test",
    "audit-signal-propagation": (
        "<editorial_letter_file> [<ledger_file>] | --self-test | "
        "--check-registry [<registry_file> <pass_deps_file>]"
    ),
    "underdiagnosis-triggers": "<editorial_letter_file> [<ledger_file>] | --self-test",
    "ledger-consolidation": "<consolidated_ledger_file> [<raw_ledger_file>] | --self-test",
    "decision-layer-check": "<editorial_letter_file> | --self-test",
}
COMMANDS += tuple(_LETTER_SIGNALS)
_CONFIG_TIMELINES = {
    "quality-risk-triggers": (
        "config_checks.py", "<contract_file> [<diagnostic_state_meta_file>] | --self-test",
    ),
    "cost-floor": (
        "config_checks.py", "<contract_or_run_metadata_file> [<preflight_packet>] [<meta_json>] [--strict] | --self-test",
    ),
    "audit-tier-criterion": (
        "config_checks.py", "<pass_dependencies_file> [<audits_root_dir>] | --self-test",
    ),
    "pass-header": (
        "config_checks.py", "<pass_artifact_file> [<pass_dependencies_file>] | --self-test",
    ),
    "argument-recon-prerequisite": (
        "config_checks.py", "<run_folder> [<editorial_letter_file>] | --self-test",
    ),
    "timeline-diff": (
        "timeline_checks.py", "<prior_timeline> <current_timeline> | --self-test",
    ),
    "timeline-arithmetic": ("timeline_checks.py", "<timeline_file> | --self-test"),
    "timeline-anchor-conflict": ("timeline_checks.py", "<timeline_file> | --self-test"),
}
COMMANDS += tuple(_CONFIG_TIMELINES)
_STRUCTURED_INTEGRITY = {
    "structured-findings": ("structured_findings.py", 0, ""),
    "softness-check": ("honesty_check.py", 2, "<editorial_letter> <findings_ledger> | --self-test"),
    "deficit-lock": ("honesty_check.py", 1, "<findings_ledger> | --self-test"),
    "artifacts-schema": ("apodictic_artifacts.py", 0, "--self-test"),
    "finding-trace": ("finding_trace.py", 1, "<run_folder|files...> [--strict] | --self-test"),
    "feedback-triage": ("feedback_triage.py", 1, "<run_folder|files...> [--strict] | --self-test"),
    "editor-scaffolding": (
        "editor_scaffolding.py", 1,
        "<editorial_letter|run_folder> [--strict] | editor-scaffolding --dual <editor_letter> <author_letter> "
        "[--strict] | editor-scaffolding --per-pass <pass_artifact> [--strict] | --self-test",
    ),
    "diagnostic-vocabulary": ("diagnostic_vocabulary.py", 1, "<vocab_guide|run_folder> [--strict] | --self-test"),
}
COMMANDS += tuple(_STRUCTURED_INTEGRITY)
_RUN_INTEGRITY = {
    "escalation-check": ("escalation_check.py", 1, "<run_folder|files...> [--strict] | --self-test"),
    "dispatch-record": (
        "dispatch_record.py", 1,
        "<run_folder> [--strict] | dispatch-record --report <project_dir> | --self-test",
    ),
    "disposition-check": (
        "disposition_check.py", 1, "<run_folder|sidecar> [readiness_assessment] [--strict] | --self-test",
    ),
    "synthesis-coverage": ("synthesis_coverage.py", 1, "<run_folder> [--strict] | --self-test"),
    "specificity-floor": ("specificity_floor.py", 2, "<editorial_letter> <findings_ledger> [--strict] | --self-test"),
}
COMMANDS += tuple(_RUN_INTEGRITY)
_PLANNING_REFUTATION = {
    "retcon-plan": ("retcon_plan.py", 1, "<run_folder|files...> [--strict] | --self-test"),
    "state-card-diff": ("state_card_diff.py", 1, "<current> | <prior> <current> [--strict] | --self-test"),
    "revision-arc": ("revision_arc.py", 1, "<run_folder|files...> [--strict] | --self-test"),
    "regression-diff": (
        "regression_diff.py", 1,
        "<prior_run_folder> <this_run_folder> [--strict] | <run_folder> | --self-test",
    ),
    "refutation-coverage": (
        "refutation_check.py", 3, "<editorial_letter> <findings_ledger> <refutation_record> | --self-test",
    ),
    "refutation-evidence": (
        "refutation_check.py", 1, "<refutation_record> [<manuscript_snapshot>] [--require-snapshot] | --self-test",
    ),
    "refutation-write-scope": (
        "refutation_check.py", 2, "<findings_ledger> <refutation_record> | --self-test",
    ),
}
COMMANDS += tuple(_PLANNING_REFUTATION)
_ARTIFACT_PLANNING = {
    "legal-risk": "legal_risk.py",
    "promise-contract": "promise_contract.py",
    "continuity-bible": "continuity_bible.py",
    "setup-payoff": "setup_payoff_checks.py",
    "world-bible": "world_bible.py",
    "argument-spine": "argument_spine.py",
    "scene-ethics": "scene_ethics.py",
}
COMMANDS += tuple(_ARTIFACT_PLANNING)
_INTAKE_VOICE = {
    "intake-interview": ("intake_interview.py", "<run_folder|files...> [--strict] | --self-test"),
    "author-fingerprint": ("author_fingerprint.py", "<author_root|files...> [--strict] | --self-test"),
    "content-advisory": ("content_advisory.py", "<run_folder|files...> [--strict] | --self-test"),
    "coaching-history": (
        "coaching_history.py",
        "<project_root|files...> [--strict] | coaching-history delete <project_root> | --self-test",
    ),
    "style-explanation": ("style_explanation.py", "<author_root|files...> [--strict] | --self-test"),
    "persona-divergence": ("persona_divergence.py", "<run_folder|files...> [--strict] | --self-test"),
}
COMMANDS += tuple(_INTAKE_VOICE)
_READER_MANUSCRIPT = {
    "lifecycle-node": ("lifecycle_node.py", 1, "lifecycle-node", "<sidecar> [run_folder] | --self-test"),
    "reader-instrument": ("reader_instrument.py", 1, "reader-instrument", "<run_folder|files...> [--strict] | --self-test"),
    "manuscript-viz": ("viz_manifest.py", 1, "manuscript-viz", "<run_folder|files...> [--strict] [--require-block] | --self-test"),
    "annotated-manuscript": ("annotation_manifest.py", 1, "annotated-manuscript", "<run_folder|files...> [--strict] | --self-test"),
    "crosslink": ("crosslink.py", 1, "crosslink", "<run_folder|files...> [--strict] | --self-test"),
    "reanchor": ("reanchor.py", 1, "reanchor", "<prior_run_folder> <new_snapshot> [--strict] | --self-test"),
    "roundtrip-disposition": ("reanchor.py", 3, "disposition", "<prior_run_folder> <new_snapshot> <this_run_folder> [--strict] | --self-test"),
    "reader-contract-outline": ("reader_contract_outline.py", 1, "reader-contract-outline", "<run_folder|files...> [--strict] | --self-test"),
    "results-guide": ("results_guide.py", 1, "results-guide", "<run_folder|files...> [--strict] | --self-test"),
    "position-pair-register": ("position_pair_gates.py", 3, "position-pair-register", "<artifact.md> <envelope.json> <manuscript> [--strict] | --self-test"),
}
COMMANDS += tuple(_READER_MANUSCRIPT)
_ARGUMENT_EVALUATORS = {
    "argument-groundtruth-check": (
        "argument_groundtruth.py", 1, "argument-groundtruth-check",
        "<groundtruth_file> | --round-record <record.md> --fixtures-dir <dir> | "
        "--repair-diff <broken/fixture.md> <clean/fixture.md> <clean/groundtruth.md> | --self-test",
    ),
    "fiction-groundtruth-check": (
        "fiction_groundtruth.py", 1, "fiction-groundtruth-check", "<groundtruth_file> | --self-test",
    ),
    "agreement-alpha": (
        "agreement_alpha.py", 1, "agreement-alpha",
        "<ratings.csv> [--metric nominal|ordinal] [--seed <int>] [--resamples <int>=1000] | --self-test",
    ),
    "argument-crosswalk-check": ("argument_crosswalk.py", 0, "argument-crosswalk-check", ""),
    "argument-agd": (
        "argument_agd.py", 1, "argument-agd",
        "<argument_state.md> [--source <source.md>] [--scan <agd_move_scan.json>] [--strict] | --self-test",
    ),
    "argument-aif-export": ("argument_aif.py", 0, "export", ""),
    "argument-aif-check": ("argument_aif.py", 0, "check", ""),
}
COMMANDS += tuple(_ARGUMENT_EVALUATORS)
_ARGUMENT_RECONSTRUCTION = {
    "argument-reconstruction-draft": "reconstruction_draft.py",
    "argument-reconstruction": "approval_graph.py",
}
COMMANDS += tuple(_ARGUMENT_RECONSTRUCTION)


def _line(text, *, error=False):
    # Bash emits LF bytes, even when the native Python host uses CRLF text I/O.
    stream = sys.stderr.buffer if error else sys.stdout.buffer
    stream.write((text + "\n").encode("utf-8", errors="surrogateescape"))
    stream.flush()


def _usage(command, arguments):
    # Keep migrated-command diagnostics compatible with the sibling Bash CLI.
    legacy_name = os.path.splitext(sys.argv[0])[0] + ".sh"
    _line(f"Usage: {legacy_name} {command} {arguments}")
    return 2


def _hash(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _run_helper(script, args):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    return subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parent / script), *args],
        env=env,
    ).returncode


def _argument_reconstruction(command, args):
    script = _ARGUMENT_RECONSTRUCTION[command]
    if not (Path(__file__).resolve().parent / script).is_file():
        _line(f"ERROR: {command} requires python3 and {script}", error=True)
        return 1
    return _run_helper(script, ["--self-test"] if args and args[0] == "--self-test" else args)


def _helper(command, args):
    script, count, arguments = _HELPERS[command]
    self_test = bool(args and args[0] == "--self-test")
    if not self_test:
        if len(args) < count:
            return _usage(command, arguments)
        is_directory = command == "artifact-names"
        exists = os.path.isdir(args[0]) if is_directory else os.path.isfile(args[0])
        if not exists:
            kind = "Directory" if is_directory else "File"
            _line(f"Error: {kind} not found: {args[0]}", error=True)
            return 2
    helper_args = ["--self-test", command] if self_test else [command, *args[:count]]
    return _run_helper(script, helper_args)


def _registry_check(args):
    registry = args[0] if args else ""
    dependencies = args[1] if len(args) > 1 else ""
    if not registry:
        # Preserve script-relative candidate order and lexical ../ components.
        script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
        for relative in (
            "../skills/core-editor/references",
            "../plugins/apodictic/skills/core-editor/references",
        ):
            base = os.path.join(script_dir, relative)
            candidate = os.path.join(base, "audit-routing-table.md")
            if os.path.isfile(candidate):
                registry = candidate
                dependencies = os.path.join(base, "pass-dependencies.md")
                break
    if not os.path.isfile(registry) or not os.path.isfile(dependencies):
        _line("Error: registry or pass-dependencies file not found "
              f"(REG={registry} DEP={dependencies})", error=True)
        return 2
    return _run_helper("letter_checks.py", ["check-registry", registry, dependencies])


def _letter_signal(command, args):
    if not args:
        return _usage(command, _LETTER_SIGNALS[command])
    if args[0] == "--self-test":
        return _run_helper("letter_checks.py", ["--self-test", command])
    if command == "audit-signal-propagation" and args[0] == "--check-registry":
        return _registry_check(args[1:])
    # These Bash arms delegate before probing files and forward every argument.
    # The existing parser owns optional-file handling and ignored extras.
    return _run_helper("letter_checks.py", [command, *args])


def _config_timeline(command, args):
    script, usage = _CONFIG_TIMELINES[command]
    if not args:
        return _usage(command, usage)
    if args[0] == "--self-test":
        return _run_helper(script, ["--self-test", command])
    if command == "timeline-diff" and len(args) < 2:
        return _usage(command, "<prior_timeline> <current_timeline>")
    # Helpers own file checks, defaults, flags, optional inputs and ignored extras.
    return _run_helper(script, [command, *args])


def _structured_integrity(command, args):
    script, count, usage = _STRUCTURED_INTEGRITY[command]
    if command == "structured-findings":
        # This arm has no wrapper prefix, arity check, file probe or flag parser.
        return _run_helper(script, args)
    if args and args[0] == "--self-test":
        # Honesty's two surfaces share a suite; schema is self-test-only.
        return _run_helper(script, ["--self-test"])
    if command == "artifacts-schema" or len(args) < count:
        return _usage(command, usage)
    # Late self-tests, flags, discovery and read failures belong to these helpers.
    return _run_helper(script, [command, *args])


def _run_integrity(command, args):
    script, count, usage = _RUN_INTEGRITY[command]
    if args and args[0] == "--self-test":
        return _run_helper(script, ["--self-test"])
    if len(args) < count:
        return _usage(command, usage)
    # Keep report/strict/late-self-test parsing and discovery in the helper.
    return _run_helper(script, [command, *args])


def _planning_refutation(command, args):
    script, count, usage = _PLANNING_REFUTATION[command]
    if args and args[0] == "--self-test":
        return _run_helper(script, ["--self-test"])
    if len(args) < count:
        return _usage(command, usage)
    # Planning flags and positional refutation dispatch remain distinct in helpers.
    return _run_helper(script, [command, *args])


def _artifact_planning(command, args):
    script = _ARTIFACT_PLANNING[command]
    if args and args[0] == "--self-test":
        return _run_helper(script, ["--self-test"])
    if not args:
        return _usage(command, "<run_folder|files...> [--strict] | --self-test")
    return _run_helper(script, [command, *args])


def _intake_voice(command, args):
    script, usage = _INTAKE_VOICE[command]
    if args and args[0] == "--self-test":
        return _run_helper(script, ["--self-test"])
    if not args:
        return _usage(command, usage)
    if command == "coaching-history" and args[0] == "delete":
        if len(args) < 2:
            _line("Error: coaching-history delete requires <project_root>", error=True)
            return 1
        # The Bash branch retains exactly the second raw token, even if a flag.
        return _run_helper(script, ["delete", args[1]])
    return _run_helper(script, [command, *args])


def _reader_manuscript(command, args):
    script, count, prefix, usage = _READER_MANUSCRIPT[command]
    if args and args[0] == "--self-test":
        return _run_helper(script, ["--self-test"])
    if len(args) < count:
        return _usage(command, usage)
    return _run_helper(script, [prefix, *args])


def _argument_evaluator(command, args):
    script, count, prefix, usage = _ARGUMENT_EVALUATORS[command]
    if args and args[0] == "--self-test":
        return _run_helper(script, ["--self-test"])
    if len(args) < count:
        return _usage(command, usage)
    return _run_helper(script, [prefix, *args])


def _self_test(command):
    """Keep the existing pure-utility self-test output and observable assertions."""
    failed = False

    def check(name, condition):
        nonlocal failed
        _line(f"  {name}: {'OK' if condition else 'FAIL'}")
        failed = failed or not condition

    def run(*args):
        return subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), *args], capture_output=True,
        )

    def rc(name, expected, *args):
        result = run(*args)
        if result.returncode == expected:
            check(name, True)
        else:
            nonlocal failed
            failed = True
            _line(f"  {name}: FAIL (rc={result.returncode} want {expected})")

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "c.md"
        missing = str(Path(directory) / "nope.md")
        if command == "contract-hash":
            path.write_bytes(b"controlling idea\n")
            digest = run(command, str(path)).stdout.rstrip(b"\n")
            check("hash_is_64hex", re.fullmatch(rb"[0-9a-f]{64}", digest) is not None)
            check("deterministic", digest == run(command, str(path)).stdout.rstrip(b"\n"))
            rc("missing_file_exit2", 2, command, missing)
            rc("no_arg_exit2", 2, command)
        elif command == "contract-check":
            path.write_bytes(b"contract body\n")
            digest = run("contract-hash", str(path)).stdout.decode("ascii").strip()
            rc("match_exit0", 0, command, str(path), digest)
            rc("mismatch_exit1", 1, command, str(path), "0" * 64)
            rc("missing_file_exit2", 2, command, missing, digest)
            rc("missing_arg_exit2", 2, command, str(path))
        else:
            for count, label in ((5, "counts_five"), (300, "counts_300_warn_threshold"),
                                 (500, "counts_500_forced_threshold")):
                path.write_bytes("".join(f"{n}\n" for n in range(1, count + 1)).encode("ascii"))
                check(label, run(command, str(path)).stdout == f"{count}\n".encode("ascii"))
            rc("missing_file_exit2", 2, command, missing)
            rc("no_arg_exit2", 2, command)
    _line("Self-test: FAIL" if failed else "Self-test: PASS")
    return int(failed)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] not in COMMANDS:
        if args:
            _line(f"Unknown or unported command: {args[0]}")
        _line("Usage: validate.py <command> [args...]")
        _line("Native commands: " + ", ".join(COMMANDS))
        _line("Partial migration: remaining commands and aggregates require validate.sh.")
        return 2
    command, args = args[0], args[1:]
    if command in _ARGUMENT_RECONSTRUCTION:
        return _argument_reconstruction(command, args)
    if command in _ARGUMENT_EVALUATORS:
        return _argument_evaluator(command, args)
    if command in _READER_MANUSCRIPT:
        return _reader_manuscript(command, args)
    if command in _INTAKE_VOICE:
        return _intake_voice(command, args)
    if command in _ARTIFACT_PLANNING:
        return _artifact_planning(command, args)
    if command in _PLANNING_REFUTATION:
        return _planning_refutation(command, args)
    if command in _RUN_INTEGRITY:
        return _run_integrity(command, args)
    if command in _STRUCTURED_INTEGRITY:
        return _structured_integrity(command, args)
    if command in _CONFIG_TIMELINES:
        return _config_timeline(command, args)
    if command in _LETTER_SIGNALS:
        return _letter_signal(command, args)
    if command in _HELPERS:
        return _helper(command, args)
    if args and args[0] == "--self-test":
        return _self_test(command)
    count = 2 if command == "contract-check" else 1
    if len(args) < count:
        arguments = "<diagnostic_state_file>" if command == "state-lines" else "<contract_file>"
        if command == "contract-check":
            arguments += " <expected_hash>"
        return _usage(command, arguments)
    if not os.path.isfile(args[0]):
        _line(f"Error: File not found: {args[0]}", error=True)
        return 2
    try:
        if command == "state-lines":
            with open(args[0], "rb") as source:
                count = sum(block.count(b"\n") for block in iter(lambda: source.read(1024 * 1024), b""))
            _line(str(count))
            return 0
        actual = _hash(args[0])
    except OSError as exc:
        _line(f"Error: Cannot read file: {args[0]}: {exc.strerror}", error=True)
        return 1
    if command == "contract-hash":
        _line(actual)
        return 0
    if actual == args[1]:
        _line("OK: Contract unchanged.")
        return 0
    for line in (
        "WARNING: Contract has been modified since intake.",
        f"  Expected: {args[1]}", f"  Actual:   {actual}",
        "  If this was intentional (author-requested contract revision), update the",
        "  contract_hash in Diagnostic_State.meta.json. If unintentional, investigate.",
    ):
        _line(line)
    return 1


if __name__ == "__main__":
    sys.exit(main())
