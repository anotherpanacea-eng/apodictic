#!/usr/bin/env python3
"""APODICTIC execution-gate engine (Runner-Governed Execution, increment 1).

`validate.sh gate <phase> <run_folder> [--strict-warnings]` shells out here. Reads
the declarative gate manifest (plugins/apodictic/schemas/execution-gates.v1.json),
resolves the phase's required artifacts in <run_folder> by output-structure.md
naming globs, runs the mechanical checks via `validate.sh <validator> <file>...`
(capturing exit code AND stdout, so a WARN-level blocker isn't lost), prints the
attested checklist, and decides whether the phase may begin.

  run_gate.py <phase> <run_folder> [--strict-warnings]
  run_gate.py --self-test

Exit: 0 permitted (maybe PASS-WITH-WARN), 1 blocked, 2 usage/config error.
"""
import glob
import json
import os
import subprocess
import sys

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

HERE = os.path.dirname(os.path.abspath(__file__))

# Finding-ID lifecycle: a passing gate advances each ledger finding's state
# (forward-only). revised is reached at a revision round (no gated phase yet).
_PHASE_FINDING_STATE = {"run_synthesis": "locked", "run_spot_check": "delivered"}
_STATE_RANK = {"locked": 1, "delivered": 2, "revised": 3}


def _manifest_path():
    env = os.environ.get("APODICTIC_GATES_MANIFEST")
    if env and os.path.exists(env):
        return env
    candidates = []
    if art is not None and art.schema_dir():
        candidates.append(os.path.join(str(art.schema_dir()), "execution-gates.v1.json"))
    candidates += [os.path.join(HERE, "..", "schemas", "execution-gates.v1.json"),
                   os.path.join(HERE, "..", "plugins", "apodictic", "schemas", "execution-gates.v1.json")]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def _find_sidecar(run_folder):
    """Walk up from the run folder to the project-root Diagnostic_State.meta.json."""
    d = os.path.abspath(run_folder)
    for _ in range(4):
        sc = os.path.join(d, "Diagnostic_State.meta.json")
        if os.path.exists(sc):
            return sc
        d = os.path.dirname(d)
    return None


def _runlabel(run_folder):
    sc = _find_sidecar(run_folder)
    if not sc:
        return None
    try:
        with open(sc, encoding="utf-8") as fh:
            return (json.load(fh).get("last_session") or {}).get("runlabel")
    except (OSError, ValueError):
        return None


def _ledger_finding_ids(ledger_path):
    """Lifecycle IDs of the apodictic.finding blocks in the ledger."""
    if not ledger_path or art is None:
        return []
    try:
        with open(ledger_path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return []
    return [obj["id"] for bt, obj, _e in art.parse_blocks(text)
            if bt == "finding" and isinstance(obj, dict) and obj.get("id")]


def _write_execution(sidecar, phase, result, allowed_next, run_folder, finding_states=None):
    """Record the gate result into the sidecar's execution block. Returns True if written."""
    try:
        with open(sidecar, encoding="utf-8") as fh:
            meta = json.load(fh)
    except (OSError, ValueError):
        return False
    ex = meta.setdefault("execution", {})
    ex.setdefault("gates", {})[phase] = result
    try:
        ex["run_folder"] = os.path.relpath(run_folder, os.path.dirname(sidecar))
    except ValueError:
        ex["run_folder"] = run_folder
    if result in ("passed", "pass-with-warn"):
        ex["phase"] = phase
        ex["allowed_next"] = list(allowed_next or [])
    if finding_states:
        fs = ex.setdefault("finding_states", {})
        for fid, st in finding_states.items():
            if _STATE_RANK.get(st, 0) >= _STATE_RANK.get(fs.get(fid), 0):
                fs[fid] = st  # forward-only
    try:
        with open(sidecar, "w", encoding="utf-8") as fh:
            json.dump(meta, fh, indent=2)
            fh.write("\n")
        return True
    except OSError:
        return False


def _resolve(run_folder, patterns, runlabel):
    pats = [patterns] if isinstance(patterns, str) else list(patterns or [])
    matches = []
    for p in pats:
        matches.extend(glob.glob(os.path.join(run_folder, p)))
    if not matches:
        return None
    if runlabel:
        for m in matches:
            if runlabel in os.path.basename(m):
                return m
    return max(matches, key=os.path.getmtime)


def _project_and_runlabel(run_folder, keys, runlabel):
    """Derive <project> and <runlabel> from the findings-ledger filename
    (`<Project>_Findings_Ledger_<runlabel>.md`) for checks like artifact-names."""
    project, rl = None, runlabel
    led = _resolve(run_folder, keys.get("findings_ledger", ""), runlabel)
    if led and "_Findings_Ledger_" in os.path.basename(led):
        pre, _, post = os.path.basename(led).partition("_Findings_Ledger_")
        project = pre
        rl = rl or (post[:-3] if post.endswith(".md") else post)
    return project or "Project", rl or "run"


def run_gate(phase, run_folder, strict_warnings=False, validate_sh=None, write=False):
    """Return (exit_code, lines)."""
    manifest_path = _manifest_path()
    if not manifest_path:
        return 2, ["gate: could not locate execution-gates.v1.json"]
    with open(manifest_path, encoding="utf-8") as fh:
        manifest = json.load(fh)
    phase_spec = manifest.get("phases", {}).get(phase)
    if not phase_spec:
        return 2, ["gate: unknown phase %r (known: %s)"
                   % (phase, ", ".join(sorted(manifest.get("phases", {}))))]
    if not os.path.isdir(run_folder):
        return 2, ["gate: run_folder not found: %s" % run_folder]

    keys = manifest.get("artifact_keys", {})
    runlabel = _runlabel(run_folder)
    project, runlabel_val = _project_and_runlabel(run_folder, keys, runlabel)
    validate_sh = validate_sh or os.path.join(HERE, "validate.sh")
    er = phase_spec.get("entry_requires", {})
    lines, fail, warn = [], 0, 0

    resolved = {}
    for key in er.get("artifacts", []):
        path = _resolve(run_folder, keys.get(key, ""), runlabel)
        if path:
            resolved[key] = path
            lines.append("  artifact %-22s ok (%s)" % (key, os.path.basename(path)))
        else:
            lines.append("  artifact %-22s MISSING" % key)
            fail = 1

    for chk in er.get("checks", []):
        v = chk["validator"]
        files, ok = [], True
        for t in chk.get("targets", []):
            if t == "run_folder":
                files.append(run_folder)
            elif t == "$project":
                files.append(project)
            elif t == "$runlabel":
                files.append(runlabel_val)
            else:
                p = resolved.get(t) or _resolve(run_folder, keys.get(t, ""), runlabel)
                if not p:
                    lines.append("  check    %-22s MISSING target (%s)" % (v, t))
                    ok = False
                    break
                files.append(p)
        if not ok:
            fail = 1
            continue
        proc = subprocess.run(["bash", validate_sh, v] + files, capture_output=True, text=True)
        out = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0:
            lines.append("  check    %-22s ERROR (exit %d)" % (v, proc.returncode))
            fail = 1
        elif "WARN" in out:
            lines.append("  check    %-22s WARN" % v)
            warn = 1
        else:
            lines.append("  check    %-22s ok" % v)

    for a in er.get("attested", []):
        lines.append("  ATTEST   %s" % a)

    if fail or (warn and strict_warnings):
        result, code = "blocked", 1
    elif warn:
        result, code = "pass-with-warn", 0
    else:
        result, code = "passed", 0

    if write:
        sidecar = _find_sidecar(run_folder)
        finding_states = {}
        if code == 0 and phase in _PHASE_FINDING_STATE:
            led = resolved.get("findings_ledger") or _resolve(run_folder, keys.get("findings_ledger", ""), runlabel)
            for fid in _ledger_finding_ids(led):
                finding_states[fid] = _PHASE_FINDING_STATE[phase]
        if sidecar and _write_execution(sidecar, phase, result, phase_spec.get("allowed_next", []),
                                        run_folder, finding_states):
            extra = " + %d finding state(s)→%s" % (len(finding_states), _PHASE_FINDING_STATE.get(phase, "")) if finding_states else ""
            lines.append("  (recorded execution.gates[%s]=%s%s in %s)" % (phase, result, extra, os.path.basename(sidecar)))

    if code == 1:
        lines.append("gate %s: BLOCKED%s" % (phase, " (--strict-warnings: unresolved WARN)" if (warn and strict_warnings) else ""))
        return 1, lines
    lines.append("gate %s: %s" % (phase, "PASS-WITH-WARN — resolve or acknowledge each WARN before transitioning"
                                   if warn else "PASS"))
    if er.get("attested"):
        lines.append("gate %s: also confirm the %d ATTEST item(s) above before transitioning"
                     % (phase, len(er["attested"])))
    return 0, lines


def run_self_test():
    import tempfile
    import shutil
    rc = {"v": 0}

    def check(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    valid_block = ('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"F-P5-01",'
                   '"mechanism":"protagonist never chooses","severity":"Must-Fix","confidence":"HIGH",'
                   '"evidence_refs":["Ch. 12"],"fix_class":"x","risk_if_fixed":"y"}\n-->')
    ledger_ok = ("## Pass 5 — Ledger Entry\n### Notable Findings\n1. **Agency collapse.** Severity: Must-Fix.\n"
                 + valid_block + "\n\n### Data Artifacts for Letter Reference\n- none\n\n"
                 "### Cross-Pass Connections\n- none\n\n### Unresolved Questions\n- none\n\n"
                 "### Audit Triggers\n| Trigger | Evidence | Recommendation |\n|---|---|---|\n")
    ledger_bad = "## Pass 5 — Ledger Entry\n### Notable Findings\n1. **Agency collapse.** Severity: Must-Fix.\n"

    vs = os.path.join(HERE, "validate.sh")
    made = []

    def folder(ledger_text, with_log=True):
        d = tempfile.mkdtemp()
        made.append(d)
        with open(os.path.join(d, "Proj_Findings_Ledger_run.md"), "w") as fh:
            fh.write(ledger_text)
        if with_log:
            with open(os.path.join(d, "Proj_Audit_Invocation_Log_run.md"), "w") as fh:
                fh.write("## Audit Invocation Log\n")
        return d

    check("run_synthesis_pass", run_gate("run_synthesis", folder(ledger_ok), validate_sh=vs)[0] == 0)
    check("missing_artifact_blocks", run_gate("run_synthesis", folder(ledger_ok, with_log=False), validate_sh=vs)[0] == 1)
    check("failing_check_blocks", run_gate("run_synthesis", folder(ledger_bad), validate_sh=vs)[0] == 1)
    check("unknown_phase_usage", run_gate("nope", folder(ledger_ok), validate_sh=vs)[0] == 2)

    # WARN policy: a softness-check WARN (exit 0 + WARN, hedged delivery) is a soft
    # block (exit 0) by default and a hard block under --strict-warnings.
    wd = tempfile.mkdtemp()
    made.append(wd)
    with open(os.path.join(wd, "Proj_Core_DE_Synthesis_run.md"), "w") as fh:
        fh.write("# Edit\n## What Needs Work\nTheo's arc could perhaps be strengthened (Chapter 34).\n"
                 "## Appendix B: Severity Calibration\nTheo arc: Severity held at Must-Fix.\n")
    with open(os.path.join(wd, "Proj_Findings_Ledger_run.md"), "w") as fh:
        fh.write('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","mechanism":"Theo arc",'
                 '"severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Chapter 34"],'
                 '"fix_class":"x","risk_if_fixed":"y"}\n-->\n')
    tm = os.path.join(wd, "gates.json")
    with open(tm, "w") as fh:
        json.dump({"$id": "test",
                   "artifact_keys": {"editorial_letter": "*_Core_DE_Synthesis_*.md",
                                     "findings_ledger": "*_Findings_Ledger_*.md"},
                   "phases": {"warn_test": {"entry_requires": {
                       "artifacts": ["editorial_letter", "findings_ledger"],
                       "checks": [{"validator": "softness-check",
                                   "targets": ["editorial_letter", "findings_ledger"]}]}}}}, fh)
    os.environ["APODICTIC_GATES_MANIFEST"] = tm
    check("warn_soft_block_passes", run_gate("warn_test", wd, validate_sh=vs)[0] == 0)
    check("warn_strict_blocks", run_gate("warn_test", wd, validate_sh=vs, strict_warnings=True)[0] == 1)
    os.environ.pop("APODICTIC_GATES_MANIFEST", None)

    # increment 2: a passing gate records its result into the sidecar's execution block
    sd = folder(ledger_ok)
    with open(os.path.join(sd, "Diagnostic_State.meta.json"), "w") as fh:
        json.dump({"project": "Proj", "execution": {}}, fh)
    run_gate("run_synthesis", sd, validate_sh=vs, write=True)
    with open(os.path.join(sd, "Diagnostic_State.meta.json")) as fh:
        ex = json.load(fh).get("execution", {})
    check("writes_execution_state",
          ex.get("gates", {}).get("run_synthesis") == "passed"
          and ex.get("phase") == "run_synthesis"
          and "run_spot_check" in ex.get("allowed_next", []))
    # increment 3: a passing gate advances each ledger finding's lifecycle state
    check("records_finding_lifecycle", ex.get("finding_states", {}).get("F-P5-01") == "locked")

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print("Usage: run_gate.py <phase> <run_folder> [--strict-warnings] | --self-test")
        return 2
    code, lines = run_gate(args[0], args[1], strict_warnings="--strict-warnings" in argv,
                           write="--no-write" not in argv)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
