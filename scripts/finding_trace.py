#!/usr/bin/env python3
"""finding-trace — cross-artifact Finding Lifecycle ID integrity (Harness Engineering).

`validate.sh finding-trace <run_folder> [--strict]` (or explicit files) shells out here.
Every material finding carries a durable Finding Lifecycle ID (`apodictic.finding.v1.id`,
`F-<ORIGIN>-<NN>`). `structured-findings` owns intra-ledger ID hygiene and `softness-check`
owns severity fidelity (locked -> delivered) by ID. This validator owns the *un-owned*
dimension: cross-artifact REFERENTIAL INTEGRITY + sidecar lifecycle COHERENCE.

  E1 dangling reference   a letter HTML-comment / severity_calibration citation to an
                          F-... ID that is not in the ledger (typo / phantom).
  E2 phantom sidecar      execution.finding_states key that is not a ledger ID.
  E3 invalid state        finding_states value not in {locked, delivered, revised}.
  W1 lifecycle coverage   once synthesis has cleared (sidecar phase >= run_synthesis),
                          a Must-Fix/Should-Fix ledger ID with no finding_states entry
                          (advisory; ERROR under --strict).

Each artifact is optional; a missing one skips its dimension (no false failure).
Reuses apodictic_artifacts.parse_blocks (one block grammar). See docs/finding-lifecycle-ids.md.

  finding_trace.py finding-trace <run_folder> [--strict]
  finding_trace.py finding-trace <ledger.md> [<letter.md>] [<sidecar.json>] [--strict]
  finding_trace.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
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

_STATES = ("locked", "delivered", "revised")
_SYNTH_BOUND = ("Must-Fix", "Should-Fix")
# Synthesis has cleared (findings locked) once the gate frontier reaches a gated phase.
_SYNTH_CLEARED_PHASES = ("run_synthesis", "run_spot_check")

# Exact Lifecycle-ID token (so F-P5-01 != F-P5-011); mirrors honesty_check._id_present.
_ID_RE = re.compile(r"(?<![\w-])F-[A-Za-z0-9]+-[0-9]{2,}(?![\w-])")
_COMMENT_RE = re.compile(r"<!--(.*?)-->", re.DOTALL)

# Editorial-letter filename globs (output-structure.md naming).
_LETTER_GLOBS = ("*_Core_DE_Synthesis_*.md", "*_Full_DE_*.md", "*_Editorial_Letter_*.md")
_LEDGER_GLOB = "*_Findings_Ledger_*.md"


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def ledger_inventory(ledger_text):
    """{id: severity} for the ledger's apodictic.finding.v1 blocks. The authoritative ID set."""
    inv = {}
    if not ledger_text or art is None:
        return inv
    for bt, obj, _err in art.parse_blocks(ledger_text):
        if bt == "finding" and isinstance(obj, dict) and obj.get("id"):
            inv[obj["id"]] = obj.get("severity")
    return inv


def letter_cited_ids(letter_text):
    """F-... IDs cited in the letter — tokens inside HTML comments (the canonical citation
    surface: `<!-- finding: F-XX-NN -->` near a finding, and apodictic:severity_calibration
    blocks, which are themselves HTML comments). IDs never appear in author-facing prose."""
    cited = set()
    if not letter_text:
        return cited
    for body in _COMMENT_RE.findall(letter_text):
        cited.update(_ID_RE.findall(body))
    return cited


def sidecar_state(sidecar_text):
    """(finding_states dict, phase, parse_ok) from a Diagnostic_State.meta.json.
    parse_ok is False when a *discovered* sidecar is present but not valid JSON — the
    caller must treat that as an error, not a clean empty lifecycle state."""
    try:
        meta = json.loads(sidecar_text)
    except (ValueError, TypeError):
        return {}, None, False
    ex = meta.get("execution", {}) if isinstance(meta, dict) else {}
    fs = ex.get("finding_states") or {}
    return (fs if isinstance(fs, dict) else {}), ex.get("phase"), True


def trace(ledger_text, letter_text, sidecar_text, strict=False):
    """Run the cross-artifact trace. Returns (code, lines)."""
    lines, errs, warns = [], [], []

    inv = ledger_inventory(ledger_text)
    if not inv:
        return 0, ["finding-trace: no ledger findings found — nothing to trace"]

    have_letter = letter_text is not None
    have_sidecar = sidecar_text is not None
    cited = letter_cited_ids(letter_text) if have_letter else set()
    finding_states, phase, sc_ok = sidecar_state(sidecar_text) if have_sidecar else ({}, None, True)

    # E1 — dangling reference (letter cites an ID not in the ledger)
    if have_letter:
        for cid in sorted(cited):
            if cid not in inv:
                errs.append("E1 dangling reference: letter cites %s — not in the ledger" % cid)
    # E0 — a discovered sidecar that cannot be parsed is an ERROR, not a clean empty lifecycle:
    # otherwise E2/E3/W1 are silently bypassed on the artifact that is supposed to carry the state.
    if have_sidecar and not sc_ok:
        errs.append("E0 unparseable sidecar: Diagnostic_State.meta.json is present but not valid "
                    "JSON — lifecycle coherence cannot be verified")
    # E2 / E3 — sidecar coherence (only when the sidecar parsed)
    if have_sidecar and sc_ok:
        for fid in sorted(finding_states):
            if fid not in inv:
                errs.append("E2 phantom sidecar state: finding_states[%s] — not in the ledger" % fid)
            if finding_states[fid] not in _STATES:
                errs.append("E3 invalid state: finding_states[%s]=%r (expected %s)"
                            % (fid, finding_states[fid], "/".join(_STATES)))
    # W1 — lifecycle coverage (only once synthesis has cleared, and the sidecar parsed)
    synth_cleared = sc_ok and phase in _SYNTH_CLEARED_PHASES
    if have_sidecar and sc_ok and synth_cleared:
        for fid in sorted(inv):
            if inv[fid] in _SYNTH_BOUND and fid not in finding_states:
                warns.append("W1 coverage: %s (%s) locked but has no finding_states entry"
                             % (fid, inv[fid]))

    # Per-ID trace report
    if not have_sidecar:
        sc_note = " (no sidecar — lifecycle trace skipped)"
    elif not sc_ok:
        sc_note = " (sidecar UNPARSEABLE — see E0)"
    else:
        sc_note = ""
    lines.append("finding-trace: %d ledger finding(s)%s%s"
                 % (len(inv),
                    "" if have_letter else " (no letter — letter trace skipped)",
                    sc_note))
    for fid in sorted(inv):
        state = ((finding_states.get(fid, "—") if sc_ok else "?") if have_sidecar else "n/a")
        mark = ("cited" if fid in cited else "UNCITED") if have_letter else "n/a"
        lines.append("  %-12s sev=%-10s state=%-10s letter=%s" % (fid, inv[fid], state, mark))

    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("finding-trace: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: finding-trace: %d advisory coverage gap(s) — see W1 above" % len(warns))
    else:
        lines.append("finding-trace: PASS (referential integrity + sidecar coherence)")
    return 0, lines


# ---------------------------------------------------------------- artifact resolution

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


def resolve_run_folder(folder):
    """(ledger_path, letter_path, sidecar_path) — newest match per artifact, any may be None."""
    ledger = _newest(glob.glob(os.path.join(folder, _LEDGER_GLOB)))
    letter = None
    for g in _LETTER_GLOBS:
        letter = _newest(glob.glob(os.path.join(folder, g)))
        if letter:
            break
    sidecar = _walk_up_sidecar(folder)
    return ledger, letter, sidecar


def classify_files(paths):
    """Classify explicit file args into (ledger, letter, sidecar) by content/extension."""
    ledger = letter = sidecar = None
    for p in paths:
        if p.endswith(".json"):
            sidecar = p
            continue
        text = _read(p) or ""
        if "apodictic:finding" in text:
            ledger = p
        else:
            letter = p
    return ledger, letter, sidecar


def run(paths, strict=False):
    if len(paths) == 1 and os.path.isdir(paths[0]):
        ledger, letter, sidecar = resolve_run_folder(paths[0])
    else:
        ledger, letter, sidecar = classify_files(paths)
    if not ledger:
        return 2, ["finding-trace: no Findings Ledger found (need a *_Findings_Ledger_*.md or a "
                   "file with apodictic:finding blocks)"]
    sidecar_text = None
    if sidecar:  # a sidecar was discovered — read it; unreadable counts as present-but-bad (E0)
        sidecar_text = _read(sidecar)
        if sidecar_text is None:
            sidecar_text = ""
    return trace(_read(ledger), _read(letter) if letter else None, sidecar_text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import tempfile
    import shutil
    rc = {"v": 0}
    made = []

    def check(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def finding(fid, sev="Must-Fix"):
        return ('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"%s",'
                '"mechanism":"m","severity":"%s","confidence":"HIGH","evidence_refs":["c"],'
                '"fix_class":"x","risk_if_fixed":"y"}\n-->' % (fid, sev))

    ledger = "## Pass 5 — Ledger Entry\n" + finding("F-P5-01") + "\n" + finding("F-P5-02", "Should-Fix") + "\n"
    letter_clean = ("# Edit\n## What Needs Work\nThe pacing collapses in Chapter 9. "
                    "<!-- finding: F-P5-01 -->\nThe stakes stay abstract. <!-- finding: F-P5-02 -->\n"
                    '<!-- apodictic:severity_calibration\n{"schema":"apodictic.severity_calibration.v1",'
                    '"id":"F-P5-01","locked":"Must-Fix","delivered":"Must-Fix","direction":"unchanged",'
                    '"rationale":"held"}\n-->\n')
    letter_dangling = letter_clean + "Also a typo'd ref. <!-- finding: F-P5-99 -->\n"

    def sidecar(states, phase="run_synthesis"):
        return json.dumps({"execution": {"phase": phase, "finding_states": states}})

    sc_ok = sidecar({"F-P5-01": "locked", "F-P5-02": "locked"})
    sc_phantom = sidecar({"F-P5-01": "locked", "F-XX-09": "locked"})
    sc_invalid = sidecar({"F-P5-01": "frozen"})
    sc_partial = sidecar({"F-P5-01": "locked"})           # F-P5-02 missing -> W1
    sc_presynth = sidecar({}, phase="")                    # pre-synthesis -> W1 skipped

    # clean trace
    code, _ = trace(ledger, letter_clean, sc_ok)
    check("clean_trace_passes", code == 0)

    # E1 dangling letter reference
    code, lines = trace(ledger, letter_dangling, sc_ok)
    check("e1_dangling_ref", code == 1 and any("E1 dangling" in ln and "F-P5-99" in ln for ln in lines))

    # E2 phantom sidecar state
    code, lines = trace(ledger, letter_clean, sc_phantom)
    check("e2_phantom_sidecar", code == 1 and any("E2 phantom" in ln and "F-XX-09" in ln for ln in lines))

    # E3 invalid state
    code, lines = trace(ledger, letter_clean, sc_invalid)
    check("e3_invalid_state", code == 1 and any("E3 invalid" in ln for ln in lines))

    # W1 coverage: advisory (exit 0) by default, ERROR under --strict
    code_w, lines_w = trace(ledger, letter_clean, sc_partial)
    check("w1_coverage_advisory", code_w == 0 and any("W1 coverage" in ln and "F-P5-02" in ln for ln in lines_w))
    code_s, _ = trace(ledger, letter_clean, sc_partial, strict=True)
    check("w1_coverage_strict_fails", code_s == 1)

    # W1 skipped pre-synthesis (no false positive before findings are locked)
    code, _ = trace(ledger, letter_clean, sc_presynth)
    check("w1_skipped_presynthesis", code == 0)

    # present-but-malformed sidecar is an ERROR (not a clean empty lifecycle state)
    code, lines = trace(ledger, letter_clean, "{ not valid json")
    check("malformed_sidecar_errors", code == 1 and any("E0 unparseable" in ln for ln in lines))

    # graceful: ledger-only run skips letter + sidecar dimensions
    code, lines = trace(ledger, None, None)
    check("ledger_only_graceful", code == 0 and any("letter trace skipped" in ln for ln in lines))

    # no ledger findings -> nothing to trace (exit 0)
    code, _ = trace("# empty\n", letter_clean, sc_ok)
    check("no_findings_noop", code == 0)

    # exact-boundary ID match: F-P5-011 must NOT satisfy a citation of F-P5-01
    led1 = "## L\n" + finding("F-P5-011") + "\n"
    let1 = "x <!-- finding: F-P5-01 -->\n"   # cites F-P5-01, ledger has only F-P5-011
    code, lines = trace(led1, let1, None)
    check("exact_boundary_ids", code == 1 and any("F-P5-01" in ln and "E1" in ln for ln in lines))

    # run-folder resolution + explicit-file classification
    d = tempfile.mkdtemp()
    made.append(d)
    with open(os.path.join(d, "Proj_Findings_Ledger_run.md"), "w") as fh:
        fh.write(ledger)
    with open(os.path.join(d, "Proj_Core_DE_Synthesis_run.md"), "w") as fh:
        fh.write(letter_clean)
    with open(os.path.join(d, "Diagnostic_State.meta.json"), "w") as fh:
        fh.write(sc_ok)
    check("run_folder_resolution", run([d])[0] == 0)
    check("explicit_files_classify",
          run([os.path.join(d, "Proj_Findings_Ledger_run.md"),
               os.path.join(d, "Proj_Core_DE_Synthesis_run.md"),
               os.path.join(d, "Diagnostic_State.meta.json")])[0] == 0)
    check("missing_ledger_usage_error", run([os.path.join(d, "Diagnostic_State.meta.json")])[0] == 2)

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a not in ("finding-trace",)]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: finding_trace.py finding-trace <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
