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
escalation is recommended, for a host that wants the checkpoint to halt.

De-escalation (the symmetric case): when NO trigger fires and EVERY complexity dimension is
measured and in a 'clearly simple' band (set well below the escalation thresholds, with a neutral
zone between), an over-provisioned expensive mode (hybrid/swarm) is recommended down to sequential
to save Tier-2 tokens. It is strictly more conservative than escalation — a missing/malformed signal
blocks it — because wrongly de-escalating a complex manuscript risks cross-pass anchoring (wrong
analysis), worse than the wasted tokens of over-provisioning. Also advisory; --strict exits 1.
See docs/adaptive-mode-escalation.md.

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

# De-escalation "clearly simple" band — set well BELOW the escalation thresholds so a neutral
# zone separates the two (no thrash near a boundary). De-escalation is recommended only when EVERY
# dimension is measured and in this band; a missing/malformed signal blocks it. The asymmetry is
# deliberate: wrongly de-escalating a complex manuscript risks cross-pass anchoring (WRONG analysis),
# worse than the wasted tokens of over-provisioning — so the safe direction is conservative.
_SIMPLE_POV = 2          # escalation fires at pov>3; 3 is the neutral zone
_SIMPLE_BELIEF = 2       # escalation fires at belief_failures>5
_SIMPLE_ORIENT = 1       # escalation fires at orientation_failures>3
_SIMPLE_FINDINGS = 8     # escalation fires at tier1_finding_count>20


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
    """(execution_mode, complexity_signals, parse_ok). Tolerant of model-authored shapes:
    a non-dict last_session / complexity_signals degrades to unknown / empty, never crashes."""
    try:
        meta = json.loads(sidecar_text)
    except (ValueError, TypeError):
        return None, {}, False
    if not isinstance(meta, dict):
        return None, {}, False
    ls = meta.get("last_session")
    mode = ls.get("execution_mode") if isinstance(ls, dict) else None
    cs = meta.get("complexity_signals")
    return (mode or None), (cs if isinstance(cs, dict) else {}), True


def _int_signal(signals, key):
    """(value, status) — status in 'ok' / 'absent' / 'bad'. The sidecar is model-authored, so a
    non-integer (string, float, bool) is 'bad' (reported unevaluable), never compared or coerced."""
    if key not in signals:
        return None, "absent"
    v = signals[key]
    if isinstance(v, bool) or not isinstance(v, int):
        return None, "bad"
    return v, "ok"


def _bool_signal(signals, key):
    """(value, status) — a non-boolean is 'bad' (so a string like \"false\" is not truthy-fired)."""
    if key not in signals:
        return None, "absent"
    v = signals[key]
    if not isinstance(v, bool):
        return None, "bad"
    return v, "ok"


def evaluate(mode, signals, t1count):
    """Return (fired, unevaluable, recommendation) where fired/unevaluable are lists of strings
    and recommendation is (current_mode, recommended_mode) or None."""
    fired, uneval = [], []

    def _note(label, status):  # absent vs malformed, reported distinctly; neither fires
        if status == "absent":
            uneval.append(label)
        elif status == "bad":
            uneval.append(label + " (malformed — wrong type; treated as unevaluable)")

    pov, pst = _int_signal(signals, "pov_count")
    _note("T1 pov_count", pst)
    if pst == "ok" and pov > 3:
        fired.append("T1 pov_count=%d (>3)" % pov)

    nl, nst = _bool_signal(signals, "nonlinear_timeline")
    _note("T2 nonlinear_timeline", nst)
    if nst == "ok" and nl:
        fired.append("T2 nonlinear_timeline")

    bf, bst = _int_signal(signals, "belief_failures")
    of, ost = _int_signal(signals, "orientation_failures")
    if bst == "bad":
        uneval.append("T3 belief_failures (malformed — wrong type; treated as unevaluable)")
    if ost == "bad":
        uneval.append("T3 orientation_failures (malformed — wrong type; treated as unevaluable)")
    if bst == "absent" and ost == "absent":
        uneval.append("T3 belief_failures / orientation_failures")
    elif bst == "ok" or ost == "ok":
        bfv = bf if bst == "ok" else 0
        ofv = of if ost == "ok" else 0
        if bfv > 5 or ofv > 3:
            fired.append("T3 belief_failures=%d (>5) or orientation_failures=%d (>3)" % (bfv, ofv))

    if t1count > 20:
        fired.append("T4 tier1_finding_count=%d (>20)" % t1count)

    rec = None
    if fired:
        if mode == "single-agent":
            rec = ("single-agent", "sequential")
        elif mode == "sequential":
            pov_complex = pst == "ok" and pov > 3
            nl_complex = nst == "ok" and nl
            architectural = pov_complex and (t1count > 20 or nl_complex)
            rec = ("sequential", "swarm" if architectural else "hybrid")
        # hybrid / swarm: already at/above the ceiling -> no recommendation
    return fired, uneval, rec


def deescalation_rec(mode, signals, t1count):
    """Conservative reverse of evaluate(): recommend a CHEAPER mode only when no escalation trigger
    fired AND every complexity dimension is measured, well-typed, and in the 'clearly simple' band.
    A missing/malformed signal blocks the recommendation (we will not de-escalate on the strength of
    an absent signal). Only the expensive modes de-escalate, and only to sequential — the roadmap's
    named `swarm -> sequential` case generalized to hybrid; single-agent/sequential are left alone
    (that is where salience-decay risk lives). Returns (current_mode, cheaper_mode) or None."""
    if mode not in ("hybrid", "swarm"):
        return None
    pov, pst = _int_signal(signals, "pov_count")
    nl, nst = _bool_signal(signals, "nonlinear_timeline")
    bf, bst = _int_signal(signals, "belief_failures")
    of, ost = _int_signal(signals, "orientation_failures")
    if not (pst == nst == bst == ost == "ok"):   # every dimension must be present and well-typed
        return None
    simple = (pov <= _SIMPLE_POV and nl is False and bf <= _SIMPLE_BELIEF
              and of <= _SIMPLE_ORIENT and t1count <= _SIMPLE_FINDINGS)
    return (mode, "sequential") if simple else None


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
    # No escalation triggers — consider DE-escalation (only on affirmatively-confirmed simplicity).
    derec = deescalation_rec(mode, signals, t1count)
    if derec:
        lines.append("escalation-check: RECOMMEND de-escalate %s -> %s (no triggers fired and every "
                     "complexity signal is in the simple band — the preflight mode is over-provisioned); "
                     "present to the author, switch only on confirmation" % (derec[0], derec[1]))
        return (1 if strict else 0), lines
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

    # model-authored type hardening (Codex #31 P2): wrong-typed signals are unevaluable,
    # never a traceback or a truthiness over-trigger
    code, lines = check(ledger(3), sidecar("single-agent", pov_count="4"))  # string int
    chk("string_pov_unevaluable",
        code == 0 and any("T1 pov_count (malformed" in ln for ln in lines)
        and not any("TRIGGER T1" in ln for ln in lines))
    code, lines = check(ledger(3), sidecar("single-agent", nonlinear_timeline="false"))  # string bool
    chk("string_timeline_not_fired",
        code == 0 and not any("TRIGGER T2" in ln for ln in lines)
        and any("T2 nonlinear_timeline (malformed" in ln for ln in lines))
    code, lines = check(ledger(3), sidecar("single-agent", belief_failures="6"))
    chk("string_belief_unevaluable",
        code == 0 and not any("TRIGGER T3" in ln for ln in lines)
        and any("T3 belief_failures (malformed" in ln for ln in lines))
    # non-dict last_session must not crash .get()
    code, lines = check(ledger(25), '{"last_session": "single-agent"}')
    chk("nondict_last_session_no_crash",
        any("current mode=unknown" in ln for ln in lines) and any("TRIGGER T4" in ln for ln in lines))

    # ---- de-escalation (the symmetric case) ----
    SIMPLE = dict(pov_count=1, nonlinear_timeline=False, belief_failures=0, orientation_failures=0)
    # swarm + every signal clearly simple + few findings -> de-escalate to sequential
    code, lines = check(ledger(3), sidecar("swarm", **SIMPLE))
    chk("deescalate_swarm_to_sequential",
        code == 0 and any("de-escalate swarm -> sequential" in ln for ln in lines))
    # hybrid + clearly simple -> de-escalate to sequential
    code, lines = check(ledger(3), sidecar("hybrid", **SIMPLE))
    chk("deescalate_hybrid_to_sequential",
        any("de-escalate hybrid -> sequential" in ln for ln in lines))
    # --strict: a de-escalation recommendation exits 1 (symmetric with escalation)
    chk("deescalate_strict_exit_1", check(ledger(3), sidecar("swarm", **SIMPLE), strict=True)[0] == 1)
    # already cheap: sequential/single-agent never de-escalate (nothing cheaper that is safe)
    chk("sequential_no_deescalation",
        not any("de-escalate" in ln for ln in check(ledger(3), sidecar("sequential", **SIMPLE))[1]))
    chk("single_agent_no_deescalation",
        not any("de-escalate" in ln for ln in check(ledger(3), sidecar("single-agent", **SIMPLE))[1]))
    # a MISSING signal blocks de-escalation (cannot confirm simplicity) — conservative
    code, lines = check(ledger(3), sidecar("swarm", pov_count=1, nonlinear_timeline=False,
                                           belief_failures=0))  # orientation_failures absent
    chk("missing_signal_blocks_deescalation",
        code == 0 and not any("de-escalate" in ln for ln in lines)
        and any("no escalation" in ln for ln in lines))
    # a malformed signal blocks de-escalation
    code, lines = check(ledger(3), sidecar("swarm", pov_count="1", nonlinear_timeline=False,
                                           belief_failures=0, orientation_failures=0))
    chk("malformed_signal_blocks_deescalation", not any("de-escalate" in ln for ln in lines))
    # the NEUTRAL zone (pov=3: neither >3 nor <=2) -> no escalation AND no de-escalation
    code, lines = check(ledger(3), sidecar("swarm", pov_count=3, nonlinear_timeline=False,
                                           belief_failures=0, orientation_failures=0))
    chk("neutral_zone_no_action",
        code == 0 and not any("de-escalate" in ln for ln in lines)
        and not any("RECOMMEND escalate" in ln for ln in lines))
    # too many Tier-1 findings (above the simple band) blocks de-escalation even if other signals simple
    chk("findings_above_simple_block_deescalation",
        not any("de-escalate" in ln for ln in check(ledger(12), sidecar("swarm", **SIMPLE))[1]))
    # a fired trigger takes precedence over de-escalation (swarm at ceiling, not de-escalated)
    code, lines = check(ledger(3), sidecar("swarm", pov_count=5, nonlinear_timeline=False,
                                           belief_failures=0, orientation_failures=0))
    chk("trigger_precedence_over_deescalation",
        not any("de-escalate" in ln for ln in lines) and any("ceiling" in ln for ln in lines))

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
