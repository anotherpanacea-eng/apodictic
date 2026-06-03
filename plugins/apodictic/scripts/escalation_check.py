#!/usr/bin/env python3
"""escalation-check — Adaptive Mid-Run Mode Escalation detector (Infrastructure).

`validate.sh escalation-check <run_folder> [--strict]` shells out here. After Tier 1
(Pass 0 + Pass 1), the system knows the manuscript's actual complexity, which may exceed
the preflight estimate the execution mode was chosen from. This is a CONDITION-TRIGGERED
gate (not "the model should notice"): every trigger is a count or a boolean read from a
named field, so it fires identically across models.

Triggers (per ROADMAP Adaptive Mid-Run Mode Escalation):
  T1  pov_count > 3                                  (sidecar complexity_signals)
  T2  nonlinear_timeline                             (sidecar complexity_signals)
  T3  belief_failures > 5 OR orientation_failures > 3 (sidecar complexity_signals)
  T4  tier1_finding_count > 20                       (computed from the ledger: F-P0-/F-P1- blocks)

A signal absent from the sidecar is reported UNEVALUABLE (not fired) — conservative:
under-trigger, never over-trigger. T4 is always computed. The recommendation follows the
escalation paths (single-agent->sequential; sequential->hybrid/swarm). Advisory by default
(exit 0 — escalation is a recommendation, never automatic); --strict exits 1 when an
escalation is recommended, for a host that wants the checkpoint to halt. See
docs/adaptive-mode-escalation.md.

  escalation_check.py escalation-check <run_folder|files...> [--strict]
  escalation_check.py --self-test

Exit: 0 advisory (or no escalation), 1 escalation recommended under --strict, 2 usage.
"""
import glob
import json
import os
import re
import sys

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

_MODES = ("single-agent", "sequential", "hybrid", "swarm")
# Finding-ID origin for the Tier-1 passes (Pass 0 Structure Map, Pass 1 Reader Orientation).
_TIER1_ID_RE = re.compile(r"^F-P[01]-")
_LEDGER_GLOB = "*_Findings_Ledger_*.md"


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def tier1_finding_count(ledger_text):
    """Count apodictic.finding blocks whose id origin is a Tier-1 pass (F-P0-/F-P1-).
    Computed from the ledger so it can never drift from a model-recorded number."""
    n = 0
    if not ledger_text or art is None:
        return 0
    for bt, obj, _e in art.parse_blocks(ledger_text):
        if bt == "finding" and isinstance(obj, dict) and _TIER1_ID_RE.match(obj.get("id") or ""):
            n += 1
    return n


def load_sidecar(sidecar_text):
    """(execution_mode, complexity_signals, parse_ok)."""
    try:
        meta = json.loads(sidecar_text)
    except (ValueError, TypeError):
        return None, {}, False
    if not isinstance(meta, dict):
        return None, {}, False
    mode = (meta.get("last_session") or {}).get("execution_mode") or None
    cs = meta.get("complexity_signals")
    return mode, (cs if isinstance(cs, dict) else {}), True


def evaluate(mode, signals, t1count):
    """Return (fired, unevaluable, recommendation) where fired/unevaluable are lists of strings
    and recommendation is (current_mode, recommended_mode) or None."""
    fired, uneval = [], []

    pov = signals.get("pov_count")
    if pov is None:
        uneval.append("T1 pov_count")
    elif pov > 3:
        fired.append("T1 pov_count=%d (>3)" % pov)

    nl = signals.get("nonlinear_timeline")
    if nl is None:
        uneval.append("T2 nonlinear_timeline")
    elif nl:
        fired.append("T2 nonlinear_timeline")

    bf, of = signals.get("belief_failures"), signals.get("orientation_failures")
    if bf is None and of is None:
        uneval.append("T3 belief_failures / orientation_failures")
    else:
        bf, of = bf or 0, of or 0
        if bf > 5 or of > 3:
            fired.append("T3 belief_failures=%d (>5) or orientation_failures=%d (>3)" % (bf, of))

    if t1count > 20:
        fired.append("T4 tier1_finding_count=%d (>20)" % t1count)

    rec = None
    if fired:
        if mode == "single-agent":
            rec = ("single-agent", "sequential")
        elif mode == "sequential":
            architectural = (pov is not None and pov > 3) and (t1count > 20 or bool(nl))
            rec = ("sequential", "swarm" if architectural else "hybrid")
        # hybrid / swarm: already at/above the ceiling -> no recommendation
    return fired, uneval, rec


def check(ledger_text, sidecar_text, strict=False):
    """Run the escalation check. Returns (code, lines)."""
    lines = []
    mode, signals, sc_ok = (None, {}, True)
    if sidecar_text is not None:
        mode, signals, sc_ok = load_sidecar(sidecar_text)
        if not sc_ok:
            return 1, ["escalation-check: sidecar present but not valid JSON — cannot read execution_mode / signals"]
    t1count = tier1_finding_count(ledger_text)

    fired, uneval, rec = evaluate(mode, signals, t1count)
    lines.append("escalation-check: current mode=%s, tier1_finding_count=%d"
                 % (mode or "unknown", t1count))
    for f in fired:
        lines.append("  TRIGGER %s" % f)
    for u in uneval:
        lines.append("  unevaluable: %s (signal not recorded in sidecar — assess this dimension manually)" % u)

    if rec:
        lines.append("escalation-check: RECOMMEND escalate %s -> %s (%d trigger(s) fired); "
                     "present to the author, switch only on confirmation" % (rec[0], rec[1], len(fired)))
        return (1 if strict else 0), lines
    if fired and mode in ("hybrid", "swarm"):
        lines.append("escalation-check: %d trigger(s) fired, but mode '%s' is at/above the escalation "
                     "ceiling — no change" % (len(fired), mode))
        return 0, lines
    if fired:
        lines.append("escalation-check: %d trigger(s) fired but current mode is unknown — set "
                     "last_session.execution_mode in the sidecar for a recommendation" % len(fired))
        return 0, lines
    lines.append("escalation-check: no escalation — revealed complexity is within the preflight estimate")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _walk_up_sidecar(start):
    d = os.path.abspath(start if os.path.isdir(start) else os.path.dirname(start))
    for _ in range(4):
        sc = os.path.join(d, "Diagnostic_State.meta.json")
        if os.path.exists(sc):
            return sc
        d = os.path.dirname(d)
    return None


def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def run(paths, strict=False):
    ledger = sidecar = None
    if len(paths) == 1 and os.path.isdir(paths[0]):
        ledger = _newest(glob.glob(os.path.join(paths[0], _LEDGER_GLOB)))
        sidecar = _walk_up_sidecar(paths[0])
    else:
        for p in paths:
            if p.endswith(".json"):
                sidecar = p
            else:
                ledger = p
    if ledger is None and sidecar is None:
        return 2, ["escalation-check: need a run folder (with a *_Findings_Ledger_*.md and/or a "
                   "Diagnostic_State.meta.json) or explicit files"]
    return check(_read(ledger) if ledger else None,
                 _read(sidecar) if sidecar else None, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import tempfile
    import shutil
    rc = {"v": 0}
    made = []

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def finding(fid):
        return ('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"%s","mechanism":"m",'
                '"severity":"Should-Fix","confidence":"HIGH","evidence_refs":["c"],"fix_class":"x",'
                '"risk_if_fixed":"y"}\n-->' % fid)

    def ledger(n):  # n Tier-1 findings (F-P0-/F-P1-) + a couple non-tier-1 (must not count)
        blocks = [finding("F-P0-%02d" % i) for i in range(1, n + 1)]
        blocks += [finding("F-P5-01"), finding("F-P10-02")]  # not Tier 1
        return "## Ledger\n" + "\n".join(blocks) + "\n"

    def sidecar(mode, **signals):
        d = {"last_session": {"execution_mode": mode}}
        if signals:
            d["complexity_signals"] = signals
        return json.dumps(d)

    # T4 finding-count is computed from the ledger (Tier-1 ids only)
    chk("tier1_count_counts_p0_p1_only", tier1_finding_count(ledger(5)) == 5)

    # single-agent + pov>3 -> recommend sequential
    code, lines = check(ledger(3), sidecar("single-agent", pov_count=5))
    chk("single_to_sequential",
        code == 0 and any("escalate single-agent -> sequential" in ln for ln in lines))

    # sequential + pov>3 + many findings -> swarm (architectural)
    code, lines = check(ledger(25), sidecar("sequential", pov_count=5, nonlinear_timeline=False))
    chk("sequential_to_swarm_architectural",
        any("escalate sequential -> swarm" in ln for ln in lines))

    # sequential + only T4 (findings>20), pov not >3 -> hybrid (focus map)
    code, lines = check(ledger(25), sidecar("sequential", pov_count=2))
    chk("sequential_to_hybrid_density",
        any("escalate sequential -> hybrid" in ln for ln in lines))

    # T3: belief/orientation density fires
    code, lines = check(ledger(3), sidecar("single-agent", belief_failures=6))
    chk("t3_belief_fires", any("escalate single-agent -> sequential" in ln for ln in lines)
        and any("TRIGGER T3" in ln for ln in lines))

    # already hybrid -> no escalation even with triggers (ceiling)
    code, lines = check(ledger(25), sidecar("hybrid", pov_count=5))
    chk("ceiling_no_escalation",
        code == 0 and any("escalation ceiling" in ln for ln in lines)
        and not any("RECOMMEND escalate" in ln for ln in lines))

    # no triggers -> no escalation
    code, lines = check(ledger(3), sidecar("single-agent", pov_count=2, nonlinear_timeline=False,
                                           belief_failures=1, orientation_failures=1))
    chk("no_escalation", code == 0 and any("no escalation" in ln for ln in lines))

    # unevaluable signals reported (sidecar has mode but no complexity_signals)
    code, lines = check(ledger(3), sidecar("single-agent"))
    chk("unevaluable_reported", any("unevaluable: T1" in ln for ln in lines)
        and any("unevaluable: T2" in ln for ln in lines))

    # --strict: a recommendation exits 1
    code_s, _ = check(ledger(3), sidecar("single-agent", pov_count=5), strict=True)
    chk("strict_exit_1_on_recommend", code_s == 1)
    code_d, _ = check(ledger(3), sidecar("single-agent", pov_count=5), strict=False)
    chk("default_exit_0_advisory", code_d == 0)

    # malformed sidecar -> error
    code, lines = check(ledger(3), "{ not json")
    chk("malformed_sidecar_errors", code == 1 and any("not valid JSON" in ln for ln in lines))

    # run-folder resolution
    d = tempfile.mkdtemp()
    made.append(d)
    with open(os.path.join(d, "Proj_Findings_Ledger_run.md"), "w") as fh:
        fh.write(ledger(25))
    with open(os.path.join(d, "Diagnostic_State.meta.json"), "w") as fh:
        fh.write(sidecar("sequential", pov_count=5, nonlinear_timeline=True))
    code, lines = run([d])
    chk("run_folder_resolution", code == 0 and any("escalate sequential -> swarm" in ln for ln in lines))

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "escalation-check"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: escalation_check.py escalation-check <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
