#!/usr/bin/env python3
"""Native validator dispatcher and ordered self-test/canonical aggregates (Python 3.10+)."""

import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Callable, NamedTuple


AGG_VALIDATORS = (
    'contract-hash',
    'contract-check',
    'ledger-check',
    'artifact-names',
    'synthesis-sections',
    'tone-check',
    'state-lines',
    'severity-floor',
    'audit-signal-propagation',
    'underdiagnosis-triggers',
    'ledger-consolidation',
    'decision-layer-check',
    'author-facing-lint',
    'quality-risk-triggers',
    'cost-floor',
    'timeline-diff',
    'timeline-arithmetic',
    'timeline-anchor-conflict',
    'audit-tier-criterion',
    'pass-header',
    'argument-recon-prerequisite',
    'structured-findings',
    'softness-check',
    'deficit-lock',
    'artifacts-schema',
    'gate',
    'gate-state',
    'finding-trace',
    'escalation-check',
    'feedback-triage',
    'editor-scaffolding',
    'diagnostic-vocabulary',
    'retcon-plan',
    'state-card-diff',
    'revision-arc',
    'regression-diff',
    'legal-risk',
    'promise-contract',
    'continuity-bible',
    'setup-payoff',
    'world-bible',
    'intake-interview',
    'author-fingerprint',
    'content-advisory',
    'coaching-history',
    'style-explanation',
    'persona-divergence',
    'argument-spine',
    'scene-ethics',
    'argument-groundtruth-check',
    'fiction-groundtruth-check',
    'agreement-alpha',
    'argument-crosswalk-check',
    'argument-agd',
    'argument-aif-check',
    'argument-reconstruction',
    'argument-reconstruction-draft',
    'registry-check',
    'schema-coverage',
    'lifecycle-node',
    'reader-instrument',
    'manuscript-viz',
    'annotated-manuscript',
    'crosslink',
    'reanchor',
    'roundtrip-disposition',
    'disposition-check',
    'synthesis-coverage',
    'dispatch-record',
    'specificity-floor',
    'refutation-coverage',
    'refutation-evidence',
    'refutation-write-scope',
    'obsidian-export',
    'html-export',
    'docx-export',
    'pdf-export',
    'results-guide',
    'position-pair-register',
    'reader-contract-outline',
    'calibration-honesty',
    'stance-calibration',
    'validator-conventions',
    'argument-carve-behavior-preservation',
)
COMMANDS = (*AGG_VALIDATORS, "argument-aif-export")
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
_ARTIFACT_PLANNING = {
    "legal-risk": "legal_risk.py",
    "promise-contract": "promise_contract.py",
    "continuity-bible": "continuity_bible.py",
    "setup-payoff": "setup_payoff_checks.py",
    "world-bible": "world_bible.py",
    "argument-spine": "argument_spine.py",
    "scene-ethics": "scene_ethics.py",
}
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
_ARGUMENT_RECONSTRUCTION = {
    "argument-reconstruction-draft": "reconstruction_draft.py",
    "argument-reconstruction": "approval_graph.py",
}
_ANNOTATION_EXPORTS = {
    "obsidian-export": "<run_folder> | (generate) {script} ... via annotation_export.py obsidian <run_folder>",
    "html-export": "<run_folder> | (generate) via annotation_export.py html <run_folder>",
    "docx-export": "<run_folder> | (generate) via annotation_export.py docx <run_folder>",
    "pdf-export": "<run_folder> | (generate) via annotation_export.py pdf <run_folder>",
}
_REPOSITORY_INTEGRITY = {
    "registry-check": ("registry_check.py", 1, "<registry.json | workspace_dir> [--strict] | --self-test"),
    "schema-coverage": ("schema_coverage.py", 0, ""),
    "validator-conventions": ("meta_lint.py", 0, ""),
    "calibration-honesty": ("calibration_honesty.py", 1, "<run_folder|files...> [--strict] | --self-test"),
    "stance-calibration": (
        "stance_calibration.py", 3,
        "<findings_ledger.md> --argument-state <Argument_State.md> | --self-test",
    ),
}
# Preserve the original command-specific navigation-option precedence.
_BASH_COMMANDS_A = frozenset((
    "contract-hash", "contract-check", "ledger-check", "artifact-names", "synthesis-sections",
    "tone-check", "state-lines", *_LETTER_SIGNALS, "quality-risk-triggers", "cost-floor",
    "timeline-diff", "timeline-arithmetic", "timeline-anchor-conflict",
))


def _line(text, *, error=False):
    # Bash emits LF bytes, even when the native Python host uses CRLF text I/O.
    stream = sys.stderr.buffer if error else sys.stdout.buffer
    stream.write((text + "\n").encode("utf-8", errors="surrogateescape"))
    stream.flush()


def _usage(command, arguments):
    # Keep migrated-command diagnostics compatible with the pre-cutover Bash CLI.
    legacy_name = os.path.splitext(sys.argv[0])[0] + ".sh"
    _line(f"Usage: {legacy_name} {command} {arguments}")
    return 2


def _hash(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _run_helper(script, args, *, input=None):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    windows = os.name == "nt"
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parent / script), *args],
        env=env, input=input, capture_output=windows,
    )
    if windows:
        # Shipped helpers expose UTF-8 text (including canonical JSON), while
        # Windows text I/O expands LF to CRLF. Keep the dispatcher's LF contract
        # without decoding, changing lone CR bytes, or changing helper failures.
        for stream, output in ((sys.stdout.buffer, result.stdout),
                               (sys.stderr.buffer, result.stderr)):
            stream.write(output.replace(b"\r\n", b"\n"))
            stream.flush()
    return result.returncode


def _script_dir():
    # Bash uses the logical (unresolved) script directory, as `cd "$(dirname "$0")" && pwd`.
    return os.path.abspath(os.path.dirname(sys.argv[0]))


def _navigation_scan(command, args):
    links = args.count("--internal-links")
    malformed = any(arg.startswith("--internal-links") and arg != "--internal-links" for arg in args)
    if not (links or malformed):
        return 0
    if command != "pdf-export" or links != 1 or malformed or len(args) != 2:
        _line("pdf-export: usage: pdf-export <run_folder> --internal-links (once)")
        return 2
    if any(arg.startswith("--") and arg != "--internal-links" for arg in args):
        _line("pdf-export: usage: misplaced navigation option")
        return 2
    return 0


def _repository_integrity(command, args):
    script, count, usage = _REPOSITORY_INTEGRITY[command]
    if args and args[0] == "--self-test":
        if command == "validator-conventions":
            result = _override_companion()
            if result:
                return result
        return _run_helper(script, ["--self-test"])
    if len(args) < count:
        return _usage(command, usage)
    return _run_helper(script, [command, *args])


def _override_companion():
    slug = "severity-floor-weak-axis"
    marker = f"<!-- override: {slug} -->"
    cases = (
        ("genuine_emdash", "found", f"<!-- override: {slug} — reason -->\n"),
        ("genuine_noreason", "found", marker + "\n"),
        ("nospace_dash", "found", f"<!-- override: {slug}—reason -->\n"),
        ("flex_whitespace", "found", f"<!--  override:  {slug}  -->\n"),
        ("suffix_collision", "miss", f"<!-- override: {slug}-but-not-really — decoy -->\n"),
        ("inline_codespan_decoy", "miss", f"Use `{marker}` here.\n"),
        ("fenced_block_decoy", "miss", f"before\n```\n{marker}\n```\nafter\n"),
        ("indented_fenced_decoy", "miss", f"x\n    ```\n{marker}\n    ```\ny\n"),
        ("multi_backtick_decoy", "miss", f"``{marker}``\n"),
        ("tilde_fence_decoy", "miss", f"before\n~~~\n{marker}\n~~~\nafter\n"),
        ("tilde_with_backtick_line_decoy", "miss", f"~~~\n```\n{marker}\n```\n~~~\n"),
        ("multiline_inline_decoy", "miss", f"a `open\n{marker}\nclose` b\n"),
    )
    failed = False
    for label, want, body in cases:
        # Like Bash's `if ... | _has_override`, any nonzero status (including launch failure) is a miss.
        result = _run_helper("override_marker.py", ["--has-override", slug], input=body.encode("utf-8"))
        got = "found" if result == 0 else "miss"
        if got == want:
            _line(f"  ho_{label}: OK ({got})")
        else:
            _line(f"  ho_{label}: FAIL (got {got} want {want})")
            failed = True
    if failed:
        _line("Self-test: FAIL (_has_override bash regression)")
    return int(failed)


def _argument_carve(_command, args):
    scripts = _script_dir()
    directory = next((candidate for candidate in (
        scripts + "/../../../evals/fixtures/argument-carve/precarve",
        scripts + "/../evals/fixtures/argument-carve/precarve",
    ) if os.path.isdir(candidate)), None)
    self_test = bool(args and args[0] == "--self-test")
    if directory is None:
        if self_test:
            _line("  fixture_present: SKIP (evals/ not present — repo-only gate)")
            _line("Self-test: PASS")
        else:
            _line("argument-carve-behavior-preservation: SKIP (evals/ not present — repo-only gate)")
        return 0
    letter, ledger, propagation, decision = (directory + "/" + name for name in (
        "argument-editorial-letter.md", "argument-findings-ledger.md",
        "propagation-output.txt", "decision-layer-output.txt",
    ))
    missing = False
    for path in (letter, ledger, propagation, decision):
        if not os.path.isfile(path):
            if not self_test:
                _line(f"ERROR: argument-carve-behavior-preservation fixture missing: {path}")
                return 1
            _line(f"  fixture_present: FAIL (missing: {path})")
            missing = True
    if missing:
        _line("Self-test: FAIL")
        return 1
    if self_test:
        _line("  fixture_present: OK (4 fixture files found)")
    failed = False
    for command, child_args, golden, label in (
        ("audit-signal-propagation", [letter, ledger], propagation, "propagation_golden"),
        ("decision-layer-check", [letter], decision, "decision_layer_golden"),
    ):
        child = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), command, *child_args],
            env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
        # Bash's unguarded capture assignment inherits pipefail/errexit.
        if child.returncode:
            return child.returncode
        output = child.stdout[:-1] if child.stdout.endswith(b"\n") else child.stdout
        output = output.rsplit(b"\n", 1)[-1].replace(b"\0", b"").rstrip(b"\n")
        try:
            expected = Path(golden).read_bytes().replace(b"\0", b"").rstrip(b"\n")
        except OSError as exc:
            _line(f"Error: Cannot read file: {golden}: {exc.strerror}", error=True)
            return 1
        if output == expected:
            if self_test:
                _line(f"  {label}: OK")
        else:
            failed = True
            if self_test:
                _line(f"  {label}: FAIL")
            else:
                _line(f"ERROR: argument-carve-behavior-preservation: {command} output drifted from golden")
            indent = "    " if self_test else "  "
            _line(indent + "expected: " + expected.decode("utf-8", errors="surrogateescape"))
            _line(indent + "got:      " + output.decode("utf-8", errors="surrogateescape"))
    if self_test:
        _line("Self-test: FAIL" if failed else "Self-test: PASS")
    elif failed:
        _line("argument-carve-behavior-preservation: FAIL")
    else:
        _line("argument-carve-behavior-preservation: PASS (smoke: resolvers still classify the argument fixture as Argument-DE post-carve; authoritative guarantee = audit-signal-propagation --check-registry + the byte-identical §4e diff)")
    return int(failed)


def _argument_reconstruction(command, args):
    script = _ARGUMENT_RECONSTRUCTION[command]
    if not (Path(__file__).resolve().parent / script).is_file():
        _line(f"ERROR: {command} requires python3 and {script}", error=True)
        return 1
    return _run_helper(script, ["--self-test"] if args and args[0] == "--self-test" else args)


def _annotation_export(command, args):
    if "--internal-links" in args and not (Path(__file__).resolve().parent / "annotation_export.py").is_file():
        _line("pdf-export: N navigation validation unavailable (Python/helper missing)")
        return 2
    if args and args[0] == "--self-test":
        result = _run_helper("annotation_export.py", ["--self-test"])
        if result or command != "pdf-export":
            return result
        root = Path(os.path.normpath(os.path.join(_script_dir(), "../../..")))
        if (root / "AGENTS.md").is_file():
            suite = root / "tests/test_pdf_navigation.py"
            if not suite.is_file():
                _line("pdf-export: N repository navigation acceptance suite unavailable")
                return 2
            return _run_helper(suite, [])
        return 0
    if not args:
        script_name = os.path.splitext(sys.argv[0])[0] + ".sh"
        return _usage(command, _ANNOTATION_EXPORTS[command].format(script=script_name))
    return _run_helper("annotation_export.py", [command, *args])


def _utility_file_exists(path):
    # Windows resolves a terminal directory component on a file; Bash test -f
    # rejects that spelling. Keep this lexical check local to utility preflight.
    if os.name == "nt" and path.endswith(("/.", "\\.")):
        return False
    return os.path.isfile(path)


def _helper(command, args):
    script, count, arguments = _HELPERS[command]
    self_test = bool(args and args[0] == "--self-test")
    if not self_test:
        if len(args) < count:
            return _usage(command, arguments)
        is_directory = command == "artifact-names"
        exists = os.path.isdir(args[0]) if is_directory else _utility_file_exists(args[0])
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
        script_dir = _script_dir()
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


def _gate(command, args):
    if args and args[0] == "--self-test":
        return _run_helper("run_gate.py", ["--self-test"])
    if command == "gate":
        if len(args) < 2:
            return _usage(command, "<phase> <run_folder> [--strict-warnings] | gate --attest <phase> <run_folder> | gate --skip/--defer <phase> <run_folder> --reason ...")
        return _run_helper("run_gate.py", args)
    if not args:
        return _usage(command, "<Diagnostic_State.meta.json> [--strict]")
    return _run_helper("run_gate.py", ["--check-state", *args])


def _self_test_all():
    total = len(AGG_VALIDATORS)
    passed = 0
    failed = 0
    gate_ok = False
    _line(f"Aggregate self-test dispatcher (v1.8.4) — running --self-test on all {total} validators:")
    for command in AGG_VALIDATORS:
        if command == "gate-state":
            ok = gate_ok
            detail = " (covered by gate shared suite)" if ok else " (gate shared suite failed)"
        else:
            child = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), command, "--self-test"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
            )
            ok = child.returncode == 0
            detail = ""
            if command == "gate":
                gate_ok = ok
        _line(f"  {command}: {'PASS' if ok else 'FAIL'}{detail}")
        if ok:
            passed += 1
        else:
            failed += 1
    _line("")
    if failed:
        _line(f"Aggregate self-test: FAIL ({failed}/{total} validators failed; rerun individually with --self-test for details)")
    else:
        _line(f"Aggregate self-test: PASS ({passed}/{total} validators)")
    return int(bool(failed))


def _utility(command, args):
    if args and args[0] == "--self-test":
        return _self_test(command)
    count = 2 if command == "contract-check" else 1
    if len(args) < count:
        arguments = "<diagnostic_state_file>" if command == "state-lines" else "<contract_file>"
        if command == "contract-check":
            arguments += " <expected_hash>"
        return _usage(command, arguments)
    if not _utility_file_exists(args[0]):
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


class Route(NamedTuple):
    handler: Callable[[str, list], int]
    helper: str | None  # Primary sibling helper script; None for in-process work.


# The one command table: main() dispatches through it, and the repository checks
# (validator_runner inventory, schema-coverage C4) read it by importing this module.
ROUTES = {
    "contract-hash": Route(_utility, None),
    "contract-check": Route(_utility, None),
    "state-lines": Route(_utility, None),
    "gate": Route(_gate, "run_gate.py"),
    "gate-state": Route(_gate, "run_gate.py"),
    "argument-carve-behavior-preservation": Route(_argument_carve, None),
    **{c: Route(_helper, row[0]) for c, row in _HELPERS.items()},
    **{c: Route(_letter_signal, "letter_checks.py") for c in _LETTER_SIGNALS},
    **{c: Route(_config_timeline, row[0]) for c, row in _CONFIG_TIMELINES.items()},
    **{c: Route(_structured_integrity, row[0]) for c, row in _STRUCTURED_INTEGRITY.items()},
    **{c: Route(_run_integrity, row[0]) for c, row in _RUN_INTEGRITY.items()},
    **{c: Route(_planning_refutation, row[0]) for c, row in _PLANNING_REFUTATION.items()},
    **{c: Route(_artifact_planning, script) for c, script in _ARTIFACT_PLANNING.items()},
    **{c: Route(_intake_voice, row[0]) for c, row in _INTAKE_VOICE.items()},
    **{c: Route(_reader_manuscript, row[0]) for c, row in _READER_MANUSCRIPT.items()},
    **{c: Route(_argument_evaluator, row[0]) for c, row in _ARGUMENT_EVALUATORS.items()},
    **{c: Route(_argument_reconstruction, script) for c, script in _ARGUMENT_RECONSTRUCTION.items()},
    **{c: Route(_annotation_export, "annotation_export.py") for c in _ANNOTATION_EXPORTS},
    **{c: Route(_repository_integrity, row[0]) for c, row in _REPOSITORY_INTEGRITY.items()},
}


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] in ("--check-canonical", "--check-all"):
        from validate_canonical import run_canonical
    if args and args[0] == "--self-test-all":
        return _self_test_all()
    if args and args[0] == "--check-canonical":
        result = run_canonical()
        _line("check-all canonical shard: FAIL (one or more real-file checks failed)" if result else
              "check-all canonical shard: PASS (real-file invariants)")
        return result
    if args and args[0] == "--check-all":
        _line("== --self-test-all ==")
        self_tests = _self_test_all()
        _line("")
        canonical = run_canonical()
        result = int(bool(self_tests or canonical))
        _line("check-all: FAIL (one or more checks failed; rerun individually for details)" if result else
              "check-all: PASS (self-tests + real-file invariants)")
        return result
    if not args or args[0] not in ROUTES:
        if args:
            _line(f"Unknown command: {args[0]}")
        _line("Usage: validate.py <command> [args...]")
        _line("Commands: " + ", ".join(COMMANDS))
        _line(f"Aggregate: --self-test-all (runs --self-test on all {len(AGG_VALIDATORS)} self-testable validators)")
        _line("Aggregate: --check-canonical (real-file invariants)")
        _line("Aggregate: --check-all (self-tests + real-file invariants)")
        return 2
    command, args = args[0], args[1:]
    if command not in _BASH_COMMANDS_A:
        result = _navigation_scan(command, args)
        if result:
            return result
    return ROUTES[command].handler(command, args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except OSError as exc:
        _line(f"ERROR: {exc}", error=True)
        sys.exit(1)
