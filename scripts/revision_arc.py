#!/usr/bin/env python3
"""revision-arc — structural integrity for Multi-Session Revision Arc Planning (Coaching Deepening).

`validate.sh revision-arc <run_folder> [--strict]` (or explicit files) shells out here. The
revision-coach reads the diagnostic state and SEQUENCES the Findings Ledger into a phased
multi-week strategy — Phase 1 structural root causes -> Phase 2 downstream consequences ->
Phase 3 polish — recorded as a single `apodictic.revision_arc.v1` block (one arc per manuscript).
It is the layer ABOVE the per-session Loop Dispatch: the arc is the calendar that sequences
findings into per-session planning; it does not re-run dispatch, and it generalizes Retcon
Planning's single-decision arc to the full Ledger.

THE HONEST POSTURE (load-bearing — the Retcon pattern: the coach infers, the validator gates the
PLAN). The Root-Cause mapping is NOT machine-readable (finding.v1 carries only structured
`severity`; the diagnostic-state Root-Cause map is markdown prose). So this validator gates the
arc's **provenance + self-consistency + firewall ONLY** — it does NOT verify the arc against a
true causal graph, and it never re-judges severity, re-validates root causes, or rates leverage-
optimality. The coach's dependency reasoning (which finding is upstream of which) is TRUSTED, not
gated. A3 is a SELF-CONSISTENCY check over the arc's OWN structure (the co-presence present-vs-
mentioned precedent), never a correctness check against the Ledger's real dependency structure.

  A1 invalid arc      the revision_arc block / a phase object fails its shape: bad/missing schema,
                      no phases, an empty phase (`findings` must have >=1 ref), a finding_ref that
                      isn't a finding.v1 id (^F-[A-Za-z0-9]+-[0-9]{2,}$), a non-string phase_label
                      / rationale / adaptation_note, a root_cause_findings member not in that
                      phase's findings, or invalid JSON.
  A2 provenance       every finding_ref in the arc resolves to a real finding.v1 id in the Findings
                      Ledger (a dangling ref is an error, mirroring finding-trace E1/E4). The arc
                      invents no findings. (Skipped only when NO ledger is in scope — then A2 is a
                      no-op and the absence is reported, never a silent pass.)
  A3 self-consistency (NOT a causal-graph check.) Each finding_ref appears in EXACTLY one phase
                      across the arc (no finding in two phases); and a finding the arc itself
                      labels a structural root cause (a `root_cause_findings` member) whose Ledger
                      severity is Must-Fix is NOT parked in the LAST (polish) phase — the leverage
                      check over the STRUCTURED severity enum + the arc's OWN phase ordering. This
                      verifies the arc's internal consistency, never that its phasing matches the
                      Ledger's true causal structure (that is the coach's trusted reasoning).
  A4 rationale        every phase carries a non-empty `rationale` (the sequencing 'why').
  W1 firewall drift   a phase rationale that prescribes EXECUTION (invents the prose/scene that
                      resolves a finding) rather than sequencing it — reuses the retcon-plan
                      firewall-drift heuristics. ADVISORY / best-effort (pattern-based: known
                      false-negatives — a rationale can prescribe execution in language the
                      heuristics don't catch); ERROR under --strict. The Firewall line: the arc
                      sequences findings; the author writes the tissue.
  W2 orphan finding   a Must-Fix Ledger finding absent from the arc — a high-leverage fix the
                      multi-week strategy doesn't sequence (advisory; ERROR under --strict).

Reuses apodictic_artifacts (block grammar + schema engine), finding_trace.ledger_inventory (the
authoritative Ledger ID set, shared so provenance can't drift), and the retcon_plan firewall-drift
regexes (shared so the Firewall heuristic is single-sourced across the two coaching tracks). Each
artifact is optional; an empty/absent one is a no-op. See docs/multi-session-arc-planning.md.

  revision_arc.py revision-arc <run_folder|files...> [--strict]
  revision_arc.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import os
import re
import sys

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

try:
    # Shared so the Ledger's authoritative ID set is single-sourced with finding-trace.
    from finding_trace import ledger_inventory
except ImportError:
    ledger_inventory = None

# Reuse the retcon-plan firewall-drift DIRECTIVE heuristics (single-sourced across the two coaching
# tracks): a ghostwrite directive ("write the line …") or a content-adding "scene where …" clause.
# If the import is unavailable the W1 firewall scan degrades to those-two-skipped (advisory anyway).
try:
    from retcon_plan import (_GHOSTWRITE_RE, _INVENTED_SCENE_RE)
except ImportError:
    _GHOSTWRITE_RE = _INVENTED_SCENE_RE = None

# Invented-prose (quoted-dialogue) heuristic — a LOCAL, tightened variant of retcon-plan's
# _INVENTED_QUOTE_RE. Retcon `intervention_class` strings are short, so its single-straight-quote
# alternative ('…' over 25 chars) rarely false-fires there; an ARC `rationale` is long prose where a
# straight apostrophe is a contraction/possessive ("the book's subject … the findings can't"), so the
# straight-single-quote alternative would constantly false-positive on legitimate sequencing prose.
# We therefore match only a PAIRED quoted span — double quotes ("…"/"…") or TYPOGRAPHIC singles
# ('…'), which actually delimit invented dialogue — never two lone straight apostrophes. The directive
# regexes above still catch "write the line where …" / "add a scene where …". (Pattern-based +
# advisory: this is best-effort, with the documented limit that quoted dialogue is the only quoted
# tell it catches.)
_W1_QUOTE_RE = re.compile(r"[\"“][^\"”]{25,}[\"”]|[‘][^’]{25,}[’]")


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (a parsed carrier, not a prose mention).

    Classifying on parsed blocks — not a raw substring — keeps a file that merely *names* the marker
    in prose from being misrouted/skipped. Gated by validate.sh validator-conventions (M2)."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))


_SCHEMA_ID = "apodictic.revision_arc.v1"
_ARC_GLOB = "*_Revision_Arc_*.md"
_LEDGER_GLOB = "*_Findings_Ledger_*.md"
# finding.v1 id pattern (the finding_ref shape) — kept in sync with the finding schema.
_FINDING_REF_RE = re.compile(r"^F-[A-Za-z0-9]+-[0-9]{2,}$")
_MUST_FIX = "Must-Fix"


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def parse_arcs(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:revision_arc block."""
    arcs = []
    if not text or art is None:
        return arcs
    schema = art.load_schema(_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "revision_arc":
            continue
        idx += 1
        where = "revision_arc #%d" % idx
        if jerr:
            arcs.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        errs = art.validate_obj(obj, schema, where)
        arcs.append((obj, errs, idx))
    return arcs


def _phase_shape_errors(obj, where):
    """The nested phase-object + finding_ref checks the subset schema checker cannot express
    (array-of-object shape, nested required keys, the finding_ref pattern, the non-empty rationale,
    the root_cause_findings <= findings subset). Part of A1. Returns a list of error strings.

    Self-consistency over the FORM only — never a causal-correctness claim."""
    errs = []
    if not isinstance(obj, dict):
        return errs  # a non-dict block is already reported by validate_obj
    # adaptation_note (already type-checked by validate_obj when present); required-ness is the schema's.
    phases = obj.get("phases")
    if not isinstance(phases, list):
        return errs  # a non-list `phases` is already reported by the schema's type:array check
    for pi, phase in enumerate(phases):
        pwhere = "%s phase #%d" % (where, pi + 1)
        if not isinstance(phase, dict):
            errs.append("%s: each phase must be a JSON object" % pwhere)
            continue
        label = phase.get("phase_label")
        if not isinstance(label, str) or not label.strip():
            errs.append("%s: 'phase_label' must be a non-empty string" % pwhere)
        rationale = phase.get("rationale")
        # rationale presence is checked here as a shape error (non-string/missing); EMPTINESS is A4.
        if "rationale" in phase and not isinstance(rationale, str):
            errs.append("%s: 'rationale' must be a string" % pwhere)
        findings = phase.get("findings")
        if not isinstance(findings, list) or not findings:
            errs.append("%s: 'findings' must be a non-empty list of finding refs (no empty phases)" % pwhere)
            findings = findings if isinstance(findings, list) else []
        find_set = set()
        for fr in findings:
            if not isinstance(fr, str) or not _FINDING_REF_RE.match(fr):
                errs.append("%s: finding ref %r is not a finding.v1 id (^F-<ORIGIN>-<NN>$)" % (pwhere, fr))
            else:
                find_set.add(fr)
        rcf = phase.get("root_cause_findings")
        if rcf is not None:
            if not isinstance(rcf, list):
                errs.append("%s: 'root_cause_findings' must be a list of finding refs" % pwhere)
            else:
                for fr in rcf:
                    if not isinstance(fr, str) or not _FINDING_REF_RE.match(fr):
                        errs.append("%s: root_cause_findings ref %r is not a finding.v1 id" % (pwhere, fr))
                    elif fr not in find_set:
                        errs.append("%s: root_cause_findings %s is not in this phase's findings "
                                    "(a root cause must be placed in the phase that labels it)" % (pwhere, fr))
    return errs


def _arc_findings(obj):
    """[(finding_ref, phase_index_0based), ...] over all phases — order preserved."""
    out = []
    for pi, phase in enumerate(obj.get("phases") or []):
        if not isinstance(phase, dict):
            continue
        for fr in (phase.get("findings") or []):
            if isinstance(fr, str):
                out.append((fr, pi))
    return out


def _firewall_drift(rationale):
    """True if a phase rationale reads like EXECUTION prescription, not sequencing — the W1 heuristic
    (local tightened quote heuristic + the shared retcon-plan directive regexes). Best-effort/advisory:
    pattern-based, known false-negatives (a rationale can prescribe execution in language not caught)."""
    if not rationale:
        return False
    if _W1_QUOTE_RE.search(rationale):
        return True
    if _GHOSTWRITE_RE is not None and (_GHOSTWRITE_RE.search(rationale) or _INVENTED_SCENE_RE.search(rationale)):
        return True
    return False


def plan(text, ledger_text=None, strict=False):
    """Run the revision-arc integrity checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    arcs = parse_arcs(text)
    if not arcs:
        return 0, ["revision-arc: no revision_arc block found — nothing to check"]

    # A1 — schema/JSON validity + nested phase shape (per arc block)
    for obj, schema_errs, _idx in arcs:
        deep = _phase_shape_errors(obj, "revision_arc") if (obj is not None and not schema_errs) else []
        for e in schema_errs + deep:
            errs.append("A1 invalid arc: %s" % e)

    valid = [obj for obj, schema_errs, _idx in arcs
             if obj is not None and not schema_errs and not _phase_shape_errors(obj, "revision_arc")]

    # The authoritative Ledger ID set (id -> severity). Empty/absent ledger => A2 is a no-op.
    inv = ledger_inventory(ledger_text) if (ledger_text and ledger_inventory) else {}
    have_ledger = bool(inv)

    for ai, obj in enumerate(valid):
        where = "arc #%d" % (ai + 1) if len(valid) > 1 else "arc"
        placements = _arc_findings(obj)

        # A3a — each finding_ref appears in EXACTLY one phase (no finding in two phases). SELF-
        # CONSISTENCY only; this is NOT a claim about the Ledger's true causal structure.
        phases_of = {}
        for fr, pi in placements:
            phases_of.setdefault(fr, []).append(pi)
        for fr, where_phases in sorted(phases_of.items()):
            if len(where_phases) > 1:
                errs.append("A3 self-consistency: %s placed in %d phases (%s) — each finding belongs "
                            "to exactly one phase" % (fr, len(where_phases),
                                                      ", ".join("phase %d" % (p + 1) for p in where_phases)))

        # A3b — leverage: a Must-Fix finding the arc itself labels a structural root cause is not
        # parked in the LAST/polish phase. Over the STRUCTURED severity + the arc's OWN phase order.
        nphases = len(obj.get("phases") or [])
        last_idx = nphases - 1
        if have_ledger and nphases > 1:
            for pi, phase in enumerate(obj.get("phases") or []):
                if not isinstance(phase, dict):
                    continue
                for fr in (phase.get("root_cause_findings") or []):
                    if not isinstance(fr, str):
                        continue
                    if pi == last_idx and inv.get(art.fid_key(fr) if art else fr) == _MUST_FIX:
                        errs.append("A3 leverage: %s is a Must-Fix the arc labels a structural root "
                                    "cause but is parked in the last (polish) phase — a root cause "
                                    "must be sequenced before its downstream phases" % fr)

        # A2 — provenance closure (every finding_ref resolves to a real Ledger finding)
        if have_ledger:
            for fr in sorted(phases_of):
                if (art.fid_key(fr) if art else fr) not in inv:
                    errs.append("A2 provenance: %s references %s — not in the Findings Ledger "
                                "(the arc invents no findings)" % (where, fr))

        # A4 — every phase has a non-empty rationale
        for pi, phase in enumerate(obj.get("phases") or []):
            if not isinstance(phase, dict):
                continue
            if not (phase.get("rationale") or "").strip():
                errs.append("A4 rationale: %s phase #%d (%r) has an empty rationale — name the "
                            "sequencing 'why'" % (where, pi + 1, phase.get("phase_label")))

        # W1 — firewall drift (a rationale that prescribes execution). ADVISORY / best-effort.
        for pi, phase in enumerate(obj.get("phases") or []):
            if not isinstance(phase, dict):
                continue
            if _firewall_drift(phase.get("rationale")):
                warns.append("W1 firewall drift: %s phase #%d rationale reads like execution "
                             "prescription, not sequencing — the arc sequences findings; the author "
                             "writes the tissue" % (where, pi + 1))

    # W2 — orphan finding (a Must-Fix Ledger finding absent from the arc)
    if have_ledger:
        in_arc = set()
        for obj in valid:
            for fr, _pi in _arc_findings(obj):
                in_arc.add(art.fid_key(fr) if art else fr)
        for fid, sev in sorted(inv.items()):
            if sev == _MUST_FIX and fid not in in_arc:
                warns.append("W2 orphan finding: Must-Fix %s is in the Ledger but absent from the arc "
                             "— the multi-week strategy doesn't sequence it" % fid)

    # Report
    nphases_total = sum(len(o.get("phases") or []) for o in valid)
    head = "revision-arc: %d arc(s)%s; %d phase(s)%s" % (
        len(arcs), "" if len(valid) == len(arcs) else " (%d well-formed)" % len(valid), nphases_total,
        "; %d ledger finding(s)" % len(inv) if have_ledger else "; no ledger in scope (A2/W2 skipped)")
    lines.append(head)
    for ai, obj in enumerate(valid):
        for pi, phase in enumerate(obj.get("phases") or []):
            if not isinstance(phase, dict):
                continue
            fr = phase.get("findings") or []
            rcf = phase.get("root_cause_findings") or []
            lines.append("  phase %d  %-26s findings=%s%s"
                         % (pi + 1, (phase.get("phase_label") or "")[:26], ",".join(str(x) for x in fr),
                            "  root_causes=%s" % ",".join(str(x) for x in rcf) if rcf else ""))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("revision-arc: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: revision-arc: %d advisory gap(s) — see W1/W2 above" % len(warns))
    else:
        lines.append("revision-arc: PASS (self-consistency + provenance + firewall%s)"
                     % ("" if have_ledger else "; no ledger — provenance/orphan unchecked"))
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve_arc(paths):
    """The Revision Arc artifact: a *_Revision_Arc_*.md in a run folder, or the first file carrying a
    revision_arc block, else the first path."""
    if len(paths) == 1 and os.path.isdir(paths[0]):
        return _newest(glob.glob(os.path.join(paths[0], _ARC_GLOB)))
    for p in paths:
        if _has_block(_read(p) or "", "revision_arc"):
            return p
    return paths[0] if paths else None


def resolve_ledger(paths, arc_path):
    """The Findings Ledger in scope: a *_Findings_Ledger_*.md in the run folder (or the arc's folder),
    else the first explicit file carrying a finding block that isn't the arc. None if none found."""
    folders = []
    if len(paths) == 1 and os.path.isdir(paths[0]):
        folders.append(paths[0])
    if arc_path:
        folders.append(os.path.dirname(arc_path))
    for d in folders:
        if d:
            hit = _newest(glob.glob(os.path.join(d, _LEDGER_GLOB)))
            if hit:
                return hit
    for p in paths:
        if p == arc_path or os.path.isdir(p):
            continue
        if _has_block(_read(p) or "", "finding"):
            return p
    # Fall back to the arc file itself when it embeds its own example Findings Ledger (the
    # self-contained canonical-fixture form — arc block + finding blocks in one .md).
    if arc_path and _has_block(_read(arc_path) or "", "finding"):
        return arc_path
    return None


def run(paths, strict=False):
    arc_path = resolve_arc(paths)
    if not arc_path:
        return 2, ["revision-arc: no Revision Arc artifact found (need a *_Revision_Arc_*.md or a file "
                   "with an apodictic:revision_arc block)"]
    text = _read(arc_path)
    if text is None:
        return 2, ["revision-arc: cannot read %s" % arc_path]
    ledger_path = resolve_ledger(paths, arc_path)
    ledger_text = _read(ledger_path) if ledger_path else None
    return plan(text, ledger_text=ledger_text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    import tempfile
    import shutil
    rc = {"v": 0}
    made = []

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def phase(label, findings, rationale="Phase 1 closes the Must-Fix root cause before downstream "
              "work begins.", root_causes=None):
        p = {"phase_label": label, "findings": list(findings), "rationale": rationale}
        if root_causes is not None:
            p["root_cause_findings"] = list(root_causes)
        return p

    def arc(phases, note="Stateless re-plan: regenerated each run from the current finding_states.",
            schema=_SCHEMA_ID):
        obj = {"schema": schema, "phases": phases, "adaptation_note": note}
        return "<!-- apodictic:revision_arc\n%s\n-->" % _j.dumps(obj)

    def finding(fid, severity="Must-Fix"):
        obj = {"schema": "apodictic.finding.v1", "id": fid,
               "mechanism": "x", "severity": severity, "confidence": "HIGH",
               "evidence_refs": ["Chapter 1"], "fix_class": "y", "risk_if_fixed": "z"}
        return "<!-- apodictic:finding\n%s\n-->" % _j.dumps(obj)

    # A canonical-shaped 3-phase arc + a matching Ledger.
    LEDGER = (finding("F-RC-01", "Must-Fix") + finding("F-CN-02", "Should-Fix")
              + finding("F-PL-03", "Could-Fix"))
    CLEAN = arc([
        phase("Structural root causes", ["F-RC-01"],
              rationale="Phase 1 must close the Must-Fix structural root cause before Phase 2 begins.",
              root_causes=["F-RC-01"]),
        phase("Consequences", ["F-CN-02"],
              rationale="Sequenced after Phase 1: this Should-Fix consequence depends on the root fix."),
        phase("Polish", ["F-PL-03"],
              rationale="Could-Fix line-level work, sequenced last; no upstream dependency."),
    ])

    # clean arc with a matching ledger => PASS (A1-A4 clean, no W flags)
    chk("clean_arc", plan(CLEAN, ledger_text=LEDGER)[0] == 0)
    # clean arc with NO ledger => PASS (A2/W2 skipped, reported not silent)
    code, ll = plan(CLEAN, ledger_text=None)
    chk("clean_no_ledger", code == 0 and any("no ledger in scope" in x for x in ll))

    # A1 — bad schema const / no phases / empty phase / bad finding_ref / non-string rationale / JSON
    chk("a1_bad_schema", plan(arc([phase("P1", ["F-RC-01"])], schema="apodictic.bogus.v1"),
                              ledger_text=LEDGER)[0] == 1)
    chk("a1_no_phases", plan(arc([]), ledger_text=LEDGER)[0] == 1)
    code, ll = plan(arc([{"phase_label": "P1", "findings": [], "rationale": "r"}]), ledger_text=LEDGER)
    chk("a1_empty_phase", code == 1 and any("non-empty list" in x for x in ll))
    code, ll = plan(arc([{"phase_label": "P1", "findings": ["nope"], "rationale": "r"}]), ledger_text=LEDGER)
    chk("a1_bad_finding_ref", code == 1 and any("not a finding.v1 id" in x for x in ll))
    code, ll = plan(arc([{"phase_label": "P1", "findings": ["F-RC-01"], "rationale": 5}]),
                    ledger_text=LEDGER)
    chk("a1_nonstring_rationale", code == 1 and any("must be a string" in x for x in ll))
    code, ll = plan("<!-- apodictic:revision_arc\n{\"schema\":\"apodictic.revision_arc.v1\"\n-->",
                    ledger_text=LEDGER)
    chk("a1_bad_json", code == 1 and any("A1 invalid arc" in x for x in ll))
    # a root_cause_findings member not in the phase's findings => A1 shape error
    code, ll = plan(arc([phase("P1", ["F-RC-01"], root_causes=["F-CN-02"])]), ledger_text=LEDGER)
    chk("a1_rcf_not_in_findings", code == 1 and any("not in this phase's findings" in x for x in ll))

    # A2 — provenance: a finding_ref not in the ledger => ERROR
    code, ll = plan(arc([phase("P1", ["F-XX-99"], root_causes=["F-XX-99"])]), ledger_text=LEDGER)
    chk("a2_dangling", code == 1 and any("A2 provenance" in x and "F-XX-99" in x for x in ll))

    # A3 — self-consistency: a finding in two phases => ERROR
    code, ll = plan(arc([phase("P1", ["F-RC-01"]), phase("P2", ["F-RC-01"])]), ledger_text=LEDGER)
    chk("a3_two_phases", code == 1 and any("A3 self-consistency" in x and "2 phases" in x for x in ll))
    # A3 — leverage: a Must-Fix root cause parked in the LAST phase => ERROR
    code, ll = plan(arc([
        phase("P1", ["F-CN-02"]),
        phase("Polish", ["F-RC-01"], root_causes=["F-RC-01"]),
    ]), ledger_text=LEDGER)
    chk("a3_rootcause_in_last", code == 1 and any("A3 leverage" in x and "F-RC-01" in x for x in ll))
    # a NON-Must-Fix root cause in the last phase is fine (leverage gate keys on Must-Fix)
    code, ll = plan(arc([
        phase("P1", ["F-RC-01"], root_causes=["F-RC-01"]),
        phase("Polish", ["F-CN-02"], root_causes=["F-CN-02"]),
    ]), ledger_text=LEDGER)
    chk("a3_nonmustfix_rootcause_last_ok", code == 0)
    # a Must-Fix root cause in an EARLIER phase is fine
    chk("a3_rootcause_first_ok", plan(CLEAN, ledger_text=LEDGER)[0] == 0)
    # single-phase arc: the leverage gate does not fire (no "last vs earlier" distinction)
    code, ll = plan(arc([phase("Only", ["F-RC-01"], root_causes=["F-RC-01"])]), ledger_text=LEDGER)
    chk("a3_single_phase_ok", code == 0)

    # A4 — empty rationale => ERROR
    code, ll = plan(arc([phase("P1", ["F-RC-01"], rationale="   ")]), ledger_text=LEDGER)
    chk("a4_empty_rationale", code == 1 and any("A4 rationale" in x for x in ll))

    # W1 — firewall drift (a rationale prescribing execution) => advisory, ERROR --strict;
    # a sequencing-only rationale passes (the pass/fail pair).
    DRIFT = arc([phase("P1", ["F-RC-01"],
                       rationale='rewrite the climax to foreshadow the betrayal: add a scene where '
                                 'she finds the letter')])
    code_w, ll_w = plan(DRIFT, ledger_text=LEDGER)
    chk("w1_drift_advisory", code_w == 0 and any("W1 firewall drift" in x for x in ll_w))
    chk("w1_drift_strict_fails", plan(DRIFT, ledger_text=LEDGER, strict=True)[0] == 1)
    # the sequencing-only counterpart of the SAME finding passes clean (no W1)
    SEQ = arc([phase("P1", ["F-RC-01"],
                     rationale="Phase 1 must close the Must-Fix root cause before Phase 2 work begins.")])
    code_w, ll_w = plan(SEQ, ledger_text=LEDGER)
    chk("w1_sequencing_passes", code_w == 0 and not any("W1 firewall drift" in x for x in ll_w))

    # W2 — orphan: a Must-Fix ledger finding absent from the arc => advisory, ERROR --strict
    LEDGER2 = LEDGER + finding("F-RC-04", "Must-Fix")  # F-RC-04 never placed in CLEAN
    code_w, ll_w = plan(CLEAN, ledger_text=LEDGER2)
    chk("w2_orphan_advisory", code_w == 0 and any("W2 orphan finding" in x and "F-RC-04" in x for x in ll_w))
    chk("w2_orphan_strict_fails", plan(CLEAN, ledger_text=LEDGER2, strict=True)[0] == 1)
    # a Could-Fix orphan does NOT trip W2 (only Must-Fix)
    LEDGER3 = LEDGER + finding("F-PL-05", "Could-Fix")
    code_w, ll_w = plan(CLEAN, ledger_text=LEDGER3)
    chk("w2_couldfix_orphan_clean", code_w == 0 and not any("W2 orphan" in x for x in ll_w))

    # no blocks -> no-op
    chk("no_arc_noop", plan("# Revision Arc\nNothing structured yet.\n", ledger_text=LEDGER)[0] == 0)

    # 2- and 4-phase arcs are absorbed (no fixed 3-enum)
    chk("two_phase_ok", plan(arc([phase("Structural", ["F-RC-01"], root_causes=["F-RC-01"]),
                                  phase("Polish", ["F-PL-03"])]), ledger_text=LEDGER)[0] == 0)
    FOUR = arc([phase("Structural", ["F-RC-01"], root_causes=["F-RC-01"]),
                phase("Consequence A", ["F-CN-02"]),
                phase("Consequence B", ["F-PL-03"]),
                phase("Polish", ["F-PL-06"])])
    chk("four_phase_ok", plan(FOUR, ledger_text=LEDGER + finding("F-PL-06", "Could-Fix"))[0] == 0)

    # run-folder + explicit-file resolution (arc + ledger discovered together)
    d = tempfile.mkdtemp()
    made.append(d)
    with open(os.path.join(d, "Proj_Findings_Ledger_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Ledger\n" + LEDGER + "\n")
    with open(os.path.join(d, "Proj_Revision_Arc_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Revision Arc\n" + CLEAN + "\n")
    chk("run_folder_resolution", run([d])[0] == 0)
    # run folder where a Must-Fix orphan exists in the ledger -> --strict fails (provenance wiring)
    with open(os.path.join(d, "Proj_Findings_Ledger_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Ledger\n" + LEDGER2 + "\n")
    chk("run_folder_orphan_strict", run([d], strict=True)[0] == 1)
    # explicit two-file resolution: ledger2 has only an orphan (advisory W2) -> exit 0 without --strict,
    # exit 1 under --strict (confirms both files are wired and the ledger is in scope).
    arc_f = os.path.join(d, "Proj_Revision_Arc_run.md")
    led_f = os.path.join(d, "Proj_Findings_Ledger_run.md")
    chk("explicit_two_file_resolution", run([arc_f, led_f])[0] == 0)
    chk("explicit_two_file_strict", run([arc_f, led_f], strict=True)[0] == 1)
    chk("missing_artifact_usage", run([d + "/nope.md"])[0] == 2)

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    # regression: a non-dict revision_arc payload must not crash (the 2026-06-20 sweep class)
    chk("crash_nondict_arc", plan('<!-- apodictic:revision_arc\n"juststring"\n-->', ledger_text=LEDGER)[0] == 1)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "revision-arc"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: revision_arc.py revision-arc <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
