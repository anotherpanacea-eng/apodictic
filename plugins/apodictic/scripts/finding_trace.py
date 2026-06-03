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
  E4 dangling revision    a revision-plan / coaching artifact cites an F-... ID not in the ledger.
  W1 lifecycle coverage   once synthesis has cleared (sidecar phase >= run_synthesis),
                          a Must-Fix/Should-Fix ledger ID with no finding_states entry
                          (advisory; ERROR under --strict).
  W2 revision coverage    a Must-Fix ledger ID not referenced in any revision plan, when one
                          is present (advisory; ERROR under --strict).
  E5 phantom completion   finding_states[id]=="revised" for a ledger ID not marked resolved
                          (`<!-- resolved: F-... -->` in a completed-revision artifact), when one
                          is present.
  W3 completion coverage  a ledger ID marked resolved in a completed-revision artifact whose
                          finding_states entry is not "revised" (advisory; ERROR under --strict).

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
# Explicit resolution marker in a completed-revision artifact: `<!-- resolved: F-XX-NN -->`.
# A bare mention (e.g. a finding listed under "Flags still present") is NOT a resolution claim,
# so completion (E5/W3) keys on this marker, not on any F-... token in the report.
_RESOLVED_RE = re.compile(r"<!--\s*resolved:(.*?)-->", re.DOTALL | re.IGNORECASE)

# Editorial-letter filename globs (output-structure.md naming).
_LETTER_GLOBS = ("*_Core_DE_Synthesis_*.md", "*_Full_DE_*.md", "*_Editorial_Letter_*.md")
_LEDGER_GLOB = "*_Findings_Ledger_*.md"
# Revision-plan / coaching artifact globs (the lifecycle stage after the letter).
_REVISION_GLOBS = ("*_Session_Plan_*.md", "*_Revision_*.md")
# Completed-revision artifacts — a SUBSET of _REVISION_GLOBS: the Revision Report stage where a
# finding's lifecycle advances to `revised` (state-lifecycle.md §Revision Round Output). Session
# plans express intent (plan coverage, W2); completed-revision artifacts express done work (E5/W3).
_COMPLETION_GLOBS = ("*_Revision_*.md",)


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


def revision_cited_ids(text):
    """F-... IDs referenced in a revision-plan / coaching artifact. These are working documents,
    so IDs are matched ANYWHERE in the text (inline prose references count) — not comment-only."""
    return set(_ID_RE.findall(text)) if text else set()


def resolved_cited_ids(text):
    """F-... IDs explicitly marked resolved in a completed-revision artifact via
    `<!-- resolved: F-XX-NN -->` markers. A bare mention (a finding under "Flags still present"
    or "New issues introduced") is NOT a resolution claim and is excluded — only an explicit
    marker counts a finding as a completed revision."""
    ids = set()
    if not text:
        return ids
    for body in _RESOLVED_RE.findall(text):
        ids.update(_ID_RE.findall(body))
    return ids


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


def trace(ledger_text, letter_text, sidecar_text, revision_texts=None, completion_texts=None,
          strict=False):
    """Run the cross-artifact trace. Returns (code, lines).

    revision_texts   = ALL revision-stage artifacts (session plans + completed revisions) — the
                       surface for E4 (dangling) and W2 (plan coverage).
    completion_texts = the completed-revision (*_Revision_*.md) SUBSET — the surface for E5
                       (phantom completion) and W3 (completion follow-through). Callers keep the
                       invariant completion_texts ⊆ revision_texts.
    """
    lines, errs, warns = [], [], []

    inv = ledger_inventory(ledger_text)
    if not inv:
        return 0, ["finding-trace: no ledger findings found — nothing to trace"]

    have_letter = letter_text is not None
    have_sidecar = sidecar_text is not None
    revision_texts = revision_texts or []
    have_revision = bool(revision_texts)
    completion_texts = completion_texts or []
    have_completion = bool(completion_texts)
    cited = letter_cited_ids(letter_text) if have_letter else set()
    rev_cited = set()
    for rt in revision_texts:
        rev_cited |= revision_cited_ids(rt)
    resolved_ids = set()  # explicitly resolved (<!-- resolved: ID -->) in a completion artifact
    for ct in completion_texts:
        resolved_ids |= resolved_cited_ids(ct)
    finding_states, phase, sc_ok = sidecar_state(sidecar_text) if have_sidecar else ({}, None, True)

    # E1 — dangling reference (letter cites an ID not in the ledger)
    if have_letter:
        for cid in sorted(cited):
            if cid not in inv:
                errs.append("E1 dangling reference: letter cites %s — not in the ledger" % cid)
    # E4 — dangling revision reference (revision plan cites an ID not in the ledger)
    if have_revision:
        for cid in sorted(rev_cited):
            if cid not in inv:
                errs.append("E4 dangling reference: revision plan cites %s — not in the ledger" % cid)
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
    # W2 — revision follow-through coverage (a Must-Fix not picked up by any revision plan)
    if have_revision:
        for fid in sorted(inv):
            if inv[fid] == "Must-Fix" and fid not in rev_cited:
                warns.append("W2 follow-through: Must-Fix %s not referenced in any revision plan" % fid)
    # E5 — phantom completion: a `revised` ledger finding with no completed-revision artifact
    # behind it. Keyed on an explicit `<!-- resolved: ID -->` marker (NOT a bare mention — a
    # report's "Flags still present" list names worked-but-unresolved findings). Gated on a
    # completion artifact being present in scope (a revised state with no completion artifact
    # here may have been resolved in an earlier session — left alone).
    if have_sidecar and sc_ok and have_completion:
        for fid in sorted(finding_states):
            if finding_states.get(fid) == "revised" and fid in inv and fid not in resolved_ids:
                errs.append("E5 phantom completion: finding_states[%s]=revised — not marked "
                            "resolved (<!-- resolved: %s -->) in any completed-revision artifact"
                            % (fid, fid))
    # W3 — completion follow-through: a finding explicitly marked resolved in a completed round
    # whose lifecycle was not advanced to `revised`. Keys on the resolved marker (so a
    # still-present mention never triggers it). Needs a parseable sidecar to judge against.
    if have_completion and have_sidecar and sc_ok:
        for fid in sorted(resolved_ids):
            if fid in inv and finding_states.get(fid) != "revised":
                warns.append("W3 completion: %s marked resolved in a completed-revision artifact "
                             "but finding_states[%s]=%r (expected 'revised')"
                             % (fid, fid, finding_states.get(fid)))

    # Per-ID trace report
    if not have_sidecar:
        sc_note = " (no sidecar — lifecycle trace skipped)"
    elif not sc_ok:
        sc_note = " (sidecar UNPARSEABLE — see E0)"
    else:
        sc_note = ""
    lines.append("finding-trace: %d ledger finding(s)%s%s%s"
                 % (len(inv),
                    "" if have_letter else " (no letter — letter trace skipped)",
                    sc_note,
                    "" if have_revision else " (no revision plan — follow-through skipped)"))
    for fid in sorted(inv):
        state = ((finding_states.get(fid, "—") if sc_ok else "?") if have_sidecar else "n/a")
        mark = ("cited" if fid in cited else "UNCITED") if have_letter else "n/a"
        if not have_revision:
            rev_mark = "n/a"
        elif fid in resolved_ids:
            rev_mark = "done"      # explicitly marked resolved in a completed-revision artifact
        elif fid in rev_cited:
            rev_mark = "planned"   # mentioned in a revision plan / report (not marked resolved)
        else:
            rev_mark = "—"
        lines.append("  %-12s sev=%-9s state=%-9s letter=%-7s rev=%s" % (fid, inv[fid], state, mark, rev_mark))

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
    """(ledger, letter, sidecar, [revisions], [completions]) — newest per single artifact;
    revisions = all session-plan + revision matches; completions = the *_Revision_*.md subset."""
    ledger = _newest(glob.glob(os.path.join(folder, _LEDGER_GLOB)))
    letter = None
    for g in _LETTER_GLOBS:
        letter = _newest(glob.glob(os.path.join(folder, g)))
        if letter:
            break
    sidecar = _walk_up_sidecar(folder)
    revisions = []
    for g in _REVISION_GLOBS:
        revisions += glob.glob(os.path.join(folder, g))
    completions = []
    for g in _COMPLETION_GLOBS:
        completions += glob.glob(os.path.join(folder, g))
    return ledger, letter, sidecar, revisions, completions


def classify_files(paths):
    """Classify explicit file args into (ledger, letter, sidecar, [revisions], [completions])."""
    ledger = letter = sidecar = None
    revisions, completions = [], []
    for p in paths:
        base = os.path.basename(p)
        if p.endswith(".json"):
            sidecar = p
        elif "apodictic:finding" in (_read(p) or ""):
            ledger = p
        elif "_Session_Plan_" in base or "_Revision_" in base:
            revisions.append(p)
            if "_Revision_" in base:
                completions.append(p)
        else:
            letter = p
    return ledger, letter, sidecar, revisions, completions


def run(paths, strict=False):
    if len(paths) == 1 and os.path.isdir(paths[0]):
        ledger, letter, sidecar, revisions, completions = resolve_run_folder(paths[0])
    else:
        ledger, letter, sidecar, revisions, completions = classify_files(paths)
    if not ledger:
        return 2, ["finding-trace: no Findings Ledger found (need a *_Findings_Ledger_*.md or a "
                   "file with apodictic:finding blocks)"]
    sidecar_text = None
    if sidecar:  # a sidecar was discovered — read it; unreadable counts as present-but-bad (E0)
        sidecar_text = _read(sidecar)
        if sidecar_text is None:
            sidecar_text = ""
    revision_texts = [t for t in (_read(r) for r in revisions) if t is not None]
    completion_texts = [t for t in (_read(c) for c in completions) if t is not None]
    return trace(_read(ledger), _read(letter) if letter else None, sidecar_text,
                 revision_texts=revision_texts, completion_texts=completion_texts, strict=strict)


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

    # E4 — dangling revision reference (revision plan cites an ID not in the ledger)
    code, lines = trace(ledger, letter_clean, sc_ok, revision_texts=["Plan: address F-P5-99 next."])
    check("e4_dangling_revision", code == 1 and any("E4 dangling" in ln and "F-P5-99" in ln for ln in lines))

    # revision plan references the Must-Fix -> clean (no W2)
    code, _ = trace(ledger, letter_clean, sc_ok, revision_texts=["Session 1: fix F-P5-01 (the pacing)."])
    check("revision_covers_mustfix", code == 0)

    # W2 follow-through: revision plan present but the Must-Fix not referenced -> advisory, strict ERROR
    code_w, lines_w = trace(ledger, letter_clean, sc_ok, revision_texts=["Session 1: polish only."])
    check("w2_followthrough_advisory",
          code_w == 0 and any("W2 follow-through" in ln and "F-P5-01" in ln for ln in lines_w))
    code_s, _ = trace(ledger, letter_clean, sc_ok, revision_texts=["Session 1: polish only."], strict=True)
    check("w2_followthrough_strict_fails", code_s == 1)

    # --- Increment 3: revision-completion (`revised`) lifecycle ---
    sc_revised = sidecar({"F-P5-01": "revised", "F-P5-02": "locked"})
    sc_delivered = sidecar({"F-P5-01": "delivered", "F-P5-02": "delivered"})
    # Completion = an explicit `<!-- resolved: ID -->` marker (NOT a bare mention).
    rev_done_01 = "# Revision Report\n## Flags resolved\nPacing now lands. <!-- resolved: F-P5-01 -->"
    rev_done_02 = "# Revision Report\n## Flags resolved\nStakes reworked. <!-- resolved: F-P5-02 -->"
    # A legitimate report naming a worked-but-unresolved finding (no resolved marker).
    rev_still_present = ("# Revision Report\n## Flags still present\nF-P5-01 remains present; the "
                         "attempted fix did not land.\n")

    # E5 phantom completion: F-P5-01 marked revised, but only F-P5-02 carries a resolved marker
    # -> the `revised` claim has no completed-revision artifact behind it.
    code, lines = trace(ledger, letter_clean, sc_revised,
                        revision_texts=[rev_done_02], completion_texts=[rev_done_02])
    check("e5_phantom_completion",
          code == 1 and any("E5 phantom" in ln and "F-P5-01" in ln for ln in lines))

    # E5 gated on completion-artifact presence: revised state, no completion artifact -> no E5
    code, _ = trace(ledger, letter_clean, sc_revised)
    check("e5_skipped_without_completion", code == 0)

    # revised + explicitly marked resolved -> clean (no E5, no W3)
    code, _ = trace(ledger, letter_clean, sc_revised,
                    revision_texts=[rev_done_01], completion_texts=[rev_done_01])
    check("revised_with_completion_clean", code == 0)

    # W3 completion follow-through: marked resolved but state still `delivered`
    code_w, lines_w = trace(ledger, letter_clean, sc_delivered,
                            revision_texts=[rev_done_01], completion_texts=[rev_done_01])
    check("w3_completion_advisory",
          code_w == 0 and any("W3 completion" in ln and "F-P5-01" in ln for ln in lines_w))
    code_s, _ = trace(ledger, letter_clean, sc_delivered,
                      revision_texts=[rev_done_01], completion_texts=[rev_done_01], strict=True)
    check("w3_completion_strict_fails", code_s == 1)

    # REGRESSION (PR #32 review P1): a worked-but-unresolved finding ("Flags still present", no
    # resolved marker) must NOT count as completed -> no W3, and must pass even under --strict.
    code, lines = trace(ledger, letter_clean, sc_delivered,
                        revision_texts=[rev_still_present], completion_texts=[rev_still_present])
    check("w3_skips_unresolved_mention", code == 0 and not any("W3 completion" in ln for ln in lines))
    check("w3_strict_ok_on_still_present",
          trace(ledger, letter_clean, sc_delivered, revision_texts=[rev_still_present],
                completion_texts=[rev_still_present], strict=True)[0] == 0)
    # ...and a still-present finding shows rev=planned (mentioned), not rev=done (resolved)
    check("still_present_not_done",
          any("F-P5-01" in ln and "rev=planned" in ln for ln in lines))

    # W3 needs a parseable sidecar to judge advancement: completion present, no sidecar -> skipped
    code, _ = trace(ledger, letter_clean, None,
                    revision_texts=[rev_done_01], completion_texts=[rev_done_01])
    check("w3_skipped_without_sidecar", code == 0)

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
    with open(os.path.join(d, "Proj_Session_Plan_run.md"), "w") as fh:
        fh.write("# Session 1\nAddress F-P5-01 (pacing) and F-P5-02 (stakes).\n")
    with open(os.path.join(d, "Proj_Revision_run.md"), "w") as fh:
        fh.write("# Revision Report\n## Flags resolved\nPacing now lands. <!-- resolved: F-P5-01 -->\n")
    rc_code, rc_lines = run([d])
    check("run_folder_resolution", rc_code == 0)
    check("run_folder_rev_done", any("rev=done" in ln for ln in rc_lines))       # F-P5-01 resolved marker
    check("run_folder_rev_planned", any("rev=planned" in ln for ln in rc_lines))  # F-P5-02 in plan only
    check("explicit_files_classify",
          run([os.path.join(d, "Proj_Findings_Ledger_run.md"),
               os.path.join(d, "Proj_Core_DE_Synthesis_run.md"),
               os.path.join(d, "Diagnostic_State.meta.json")])[0] == 0)
    check("explicit_files_completion",
          any("rev=done" in ln for ln in run([os.path.join(d, "Proj_Findings_Ledger_run.md"),
                                              os.path.join(d, "Proj_Revision_run.md")])[1]))
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
