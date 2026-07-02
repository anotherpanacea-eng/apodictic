#!/usr/bin/env python3
"""lifecycle-node — derive a project's lifecycle node from its sidecar (Project Addressability, Increment 3).

`validate.sh lifecycle-node <sidecar> [run_folder]` shells out here. State-driven dispatch needs one
authoritative, *tested* answer to "where is this project?" so `/start`, `/projects`, and the Increment-4
loop dispatcher don't each re-derive it in prose. This computes the node by a single precedence
(FIRST MATCH WINS) over the existing Diagnostic_State.meta.json sidecar — no new stored state:

    cold -> blocked_gate -> execution -> pre_writing -> submission -> revising -> diagnosed -> diagnosing

The set is TOTAL: any readable sidecar resolves to exactly one node, with `diagnosing` the catch-all
default (intake done, passes/synthesis in progress, no editorial letter yet — the case that matched no
node in the first draft). Each node's signal:

  cold          no sidecar / unreadable (no bound project)
  blocked_gate  execution.pending_gate present (resolve the gate first)
  execution     mode == "execution"
  pre_writing   next_action.key == "pre_writing" (pre-writing minimal sidecar)
  submission    readiness[] non-empty (a submission-readiness assessment was recorded)
  revising      revision_progress.steps_complete > 0
  diagnosed     a synthesis/editorial letter exists: {project_root}/SYNTHESIS.md or
                {project_root}/runs/*/*_Synthesis_*.md (project_root = the sidecar's dir; an optional
                run_folder arg is an extra search location)
  diagnosing    default — mode == "diagnostic" and nothing above matched

`diagnosed` is the only node needing a filesystem check; when no synthesis is found anywhere,
derivation falls through to `diagnosing` (the safe pre-letter default). Reads the sidecar directly
(stdlib JSON). See docs/project-addressability.md.

  lifecycle_node.py lifecycle-node <sidecar> [run_folder]
  lifecycle_node.py --self-test

Exit: 0 (prints the node), 2 usage. (Pure derivation — there is no failure verdict; an unreadable
sidecar is reported as `cold`, exit 0.)
"""
import glob
import json
import os
import sys

NODES = ("cold", "blocked_gate", "execution", "pre_writing",
         "submission", "revising", "diagnosed", "diagnosing")


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _letter_exists(project_root, run_folder=None):
    """True if a synthesis/editorial letter exists for the project."""
    candidates = []
    if project_root:
        candidates.append(os.path.join(project_root, "SYNTHESIS.md"))
        candidates += glob.glob(os.path.join(project_root, "runs", "*", "*_Synthesis_*.md"))
    if run_folder:
        candidates += glob.glob(os.path.join(run_folder, "*_Synthesis_*.md"))
    return any(os.path.isfile(c) for c in candidates)


def derive_node(sidecar, project_root=None, run_folder=None):
    """Return (node, reason) by first-match precedence. TOTAL: any input resolves to a known node.

    Defensive against malformed-but-readable sidecars (a non-dict top level, or fields with the
    wrong type — e.g. `next_action` as a bare string, which docs/project-addressability.md notes
    the denormalized copy can be). Anything that isn't a usable JSON object is `cold`."""
    if not isinstance(sidecar, dict):
        return "cold", "no sidecar / not a JSON object (no usable bound state)"
    execution = sidecar.get("execution")
    if isinstance(execution, dict) and execution.get("pending_gate"):
        return "blocked_gate", "execution.pending_gate=%r" % execution.get("pending_gate")
    if sidecar.get("mode") == "execution":
        return "execution", "mode == execution"
    na = sidecar.get("next_action")
    na_key = na.get("key") if isinstance(na, dict) else na  # tolerate the bare-string form
    if na_key == "pre_writing":
        return "pre_writing", "next_action key == pre_writing"
    readiness = sidecar.get("readiness")
    if isinstance(readiness, list) and readiness:
        return "submission", "readiness[] has %d entr(y/ies)" % len(readiness)
    rp = sidecar.get("revision_progress")
    steps = rp.get("steps_complete", 0) if isinstance(rp, dict) else 0
    if isinstance(steps, int) and steps > 0:
        return "revising", "revision_progress.steps_complete == %d" % steps
    if _letter_exists(project_root, run_folder):
        return "diagnosed", "synthesis/editorial letter present"
    return "diagnosing", "no higher-precedence signal; no letter yet (default)"


def run(paths):
    if not paths:
        return 2, ["lifecycle-node: usage: lifecycle-node <sidecar> [run_folder]"]
    sidecar_path = paths[0]
    run_folder = paths[1] if len(paths) > 1 else None
    sidecar = _read_json(sidecar_path)
    project_root = os.path.dirname(os.path.abspath(sidecar_path)) if sidecar is not None else None
    node, reason = derive_node(sidecar, project_root=project_root, run_folder=run_folder)
    return 0, ["lifecycle-node: %s" % node, "  reason: %s" % reason]


# ---------------------------------------------------------------- self-test

def run_self_test():
    import tempfile
    import shutil
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    # non-UTF8 sidecar: _read_json must degrade to the unreadable path (None), never
    # a traceback (the disposition_check adjacent-exception class, swept repo-wide)
    _fd, _nu = tempfile.mkstemp(suffix=".json")
    with os.fdopen(_fd, "wb") as _fh:
        _fh.write(b"\xff\xfenot utf-8\xff")
    chk("non_utf8_read_json_returns_none", _read_json(_nu) is None)
    os.unlink(_nu)

    def node(sidecar, project_root=None, run_folder=None):
        return derive_node(sidecar, project_root=project_root, run_folder=run_folder)[0]

    base = {"schema": "apodictic.diagnostic-state.v1", "mode": "diagnostic",
            "next_action": {"key": "run_passes", "description": ""},
            "revision_progress": {"steps_complete": 0}, "readiness": []}

    # cold — no sidecar
    chk("cold_no_sidecar", node(None) == "cold")

    # B1 — fresh / mid-pass Core-DE project must be diagnosing, NOT undefined
    chk("b1_fresh_project_diagnosing", node(dict(base)) == "diagnosing")

    # blocked_gate beats everything else
    sc = dict(base, mode="execution", execution={"pending_gate": "run_synthesis"})
    chk("blocked_gate_precedence", node(sc) == "blocked_gate")

    # execution
    chk("execution", node(dict(base, mode="execution", active_scene_scope="ch3"))== "execution")

    # pre_writing (minimal sidecar)
    chk("pre_writing", node({"mode": "diagnostic", "next_action": {"key": "pre_writing"}}) == "pre_writing")

    # submission — readiness[] non-empty
    sc = dict(base, readiness=[{"schema": "apodictic.readiness.v1", "dimension": "query",
                                "verdict": "weak", "rationale": "x"}])
    chk("submission_readiness", node(sc) == "submission")

    # revising — steps_complete > 0
    chk("revising", node(dict(base, revision_progress={"steps_complete": 2})) == "revising")

    # precedence: submission before revising (both true -> submission)
    sc = dict(base, readiness=[{"schema": "apodictic.readiness.v1", "dimension": "d",
                                "verdict": "v", "rationale": "r"}],
              revision_progress={"steps_complete": 3})
    chk("submission_beats_revising", node(sc) == "submission")

    # diagnosed — synthesis present at project root
    d = tempfile.mkdtemp()
    try:
        open(os.path.join(d, "SYNTHESIS.md"), "w", encoding="utf-8", newline="").close()
        chk("diagnosed_root_synthesis", node(dict(base), project_root=d) == "diagnosed")
        # via runs/*/*_Synthesis_*.md
        d2 = tempfile.mkdtemp()
        os.makedirs(os.path.join(d2, "runs", "2026-06-08_opus_core-de"))
        open(os.path.join(d2, "runs", "2026-06-08_opus_core-de", "Proj_Core_DE_Synthesis_run.md"), "w", encoding="utf-8", newline="").close()
        chk("diagnosed_runs_glob", node(dict(base), project_root=d2) == "diagnosed")
        shutil.rmtree(d2, ignore_errors=True)
        # S4 — no letter anywhere -> diagnosing (safe default), even though project_root given
        d3 = tempfile.mkdtemp()
        chk("s4_no_letter_diagnosing", node(dict(base), project_root=d3) == "diagnosing")
        shutil.rmtree(d3, ignore_errors=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # B1 (build review) — malformed-but-readable inputs must NOT crash and must resolve to a node
    chk("malformed_next_action_string", node({"next_action": "pre_writing"}) == "pre_writing")
    chk("malformed_toplevel_list", node([]) == "cold")
    chk("malformed_toplevel_scalar", node(42) == "cold")
    chk("malformed_empty_dict", node({}) == "diagnosing")
    chk("malformed_execution_nondict", node({"execution": "oops", "mode": "diagnostic"}) == "diagnosing")
    chk("malformed_revprog_nondict", node({"revision_progress": "oops"}) == "diagnosing")
    chk("malformed_steps_string", node({"revision_progress": {"steps_complete": "3"}}) == "diagnosing")

    # totality — a wide range of sidecars all resolve to a known node
    import itertools
    for mode, na, steps, rdy in itertools.product(
            ["diagnostic", "execution"], ["run_passes", "pre_writing", "run_synthesis", "coaching"],
            [0, 1], [[], [{"schema": "apodictic.readiness.v1", "dimension": "d", "verdict": "v", "rationale": "r"}]]):
        n = node({"mode": mode, "next_action": {"key": na},
                  "revision_progress": {"steps_complete": steps}, "readiness": rdy})
        if n not in NODES:
            chk("totality_%s_%s_%d" % (mode, na, steps), False)
    chk("totality_all_known", True)

    # CLI resolution (real sidecar file)
    df = tempfile.mkdtemp()
    try:
        p = os.path.join(df, "Diagnostic_State.meta.json")
        with open(p, "w", encoding="utf-8", newline="") as fh:
            json.dump(dict(base), fh)
        chk("cli_file_resolution", run([p])[0] == 0 and "diagnosing" in run([p])[1][0])
        chk("cli_usage", run([])[0] == 2)
        # unreadable / missing path -> cold, exit 0
        chk("cli_missing_cold", "cold" in run([os.path.join(df, "nope.json")])[1][0])
    finally:
        shutil.rmtree(df, ignore_errors=True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "lifecycle-node"]
    paths = [a for a in args if not a.startswith("--")]
    code, lines = run(paths)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
