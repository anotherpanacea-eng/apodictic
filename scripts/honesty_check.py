#!/usr/bin/env python3
"""APODICTIC honesty gate (Phase 4): Deficit Lock + Softness Gate.

Closes the uniform-charity / silent-softening leak — a letter that under-delivers
a finding it already locked at Triage, while still passing severity-floor and
audit-signal-propagation.

  softness-check <editorial_letter> <findings_ledger>
      Compare the delivered letter against the Triage-locked findings
      (apodictic.finding.v1 blocks in the ledger). For each locked
      Must-Fix/Should-Fix: when the finding carries a Lifecycle ID, match it to the
      letter by ID (exact) — both the body delivery and the Severity Calibration
      record reference the ID; otherwise fall back to evidence-ref / mechanism
      heuristics. ERROR on a recorded downgrade, a finding buried (absent from the
      author-facing body), or a finding dropped (absent from both), unless a body
      override marker is present. Hedged delivery -> WARN. Weak-axis coherence is
      owned by `severity-floor`, not here.

  deficit-lock <findings_ledger>
      Verify EVERY synthesis-bound (Must-Fix/Should-Fix) finding was locked
      structurally: more prose severity labels than apodictic.finding.v1 blocks
      means a finding was left unlocked -> ERROR.

  --self-test     built-in cases (both checks)

Block grammar + severity ordering come from the shared `apodictic_artifacts`
module (schemas/ are the source of truth). The body override marker is
`<!-- override: softness-downgrade — <rationale> -->` (body-only; appendix
markers are non-canonical). Substring matching is HTML-tolerant.

Exit: 0 pass (no ERROR), 1 ERROR(s), 2 usage error.
"""
import re
import sys

import apodictic_artifacts as art

SEV_RANK = art.SEVERITY_RANK
SEV_TOKENS = tuple(SEV_RANK)
LOCKED = {"Must-Fix", "Should-Fix"}
HEDGES = ["could perhaps", "might benefit", "somewhat", "arguably",
          "relatively minor", "on the softer side", "not a dealbreaker",
          "could be strengthened", "may want to consider", "if you have time",
          "a minor quibble", "nitpick"]
STOP = {"the", "and", "for", "not", "with", "that", "this", "from", "into",
        "when", "does", "are", "was", "but", "its", "has", "you", "your",
        "than", "then", "doesn", "isn"}
# Prose severity labels marking a synthesis-bound finding (outside any block).
PROSE_SEVERITY_RE = re.compile(
    r"(?:\*\*\s*|Severity[:\s]+|held at\s+|Tier[:\s]+|(?:^|\n)[ \t]*(?:[-*]|\d+[.)])[ \t]+)(Must-Fix|Should-Fix)\b")
APPENDIX_A_RE = re.compile(r"Appendix\s+A\b", re.IGNORECASE)
SEVCAL_RE = re.compile(r"Severity\s+Calibration|Appendix\s+B\b", re.IGNORECASE)
NEXT_APPENDIX_RE = re.compile(r"Appendix\s+[C-Z]\b", re.IGNORECASE)
SOFT_MARKER = "<!-- override: softness-downgrade"


def parse_locked_findings(ledger_text):
    """Locked apodictic.finding.v1 objects from the ledger (via the shared parser)."""
    out = []
    for btype, obj, jerr in art.parse_blocks(ledger_text):
        if jerr or btype != "finding" or not isinstance(obj, dict):
            continue
        if str(obj.get("schema", "")).startswith("apodictic.finding."):
            out.append(obj)
    return out


def _mech_tokens(mech):
    words = re.findall(r"[A-Za-z][A-Za-z'\-]{2,}", str(mech).lower())
    return {w for w in words if w not in STOP}


def _ref_present(ref, region):
    """Token-boundary match for an evidence ref (so 'Chapter 3' != 'Chapter 34')."""
    return re.search(r"(?<![\w])%s(?![\w])" % re.escape(ref), region) is not None


def _id_present(region, fid):
    """Exact Lifecycle-ID token match (so F-P5-01 != F-P5-011)."""
    return re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(fid), region) is not None


def _id_delivered_in_body(body, fid, finding, radius=400):
    """The ID LOCATES the delivery, but real author-facing prose must show the
    finding near it — a bare `<!-- finding: ID -->` comment is not a delivery.
    Look in a window around each ID occurrence (HTML comments stripped) for the
    finding via the mechanism/evidence heuristic."""
    for m in re.finditer(r"(?<![\w-])%s(?![\w-])" % re.escape(fid), body):
        window = re.sub(r"<!--.*?-->", " ", body[max(0, m.start() - radius):m.end() + radius], flags=re.DOTALL)
        if _region_contains(window, finding):
            return True
    return False


def _region_contains(region, finding):
    """Heuristic presence: any evidence_ref (token-boundary) or >= 2 mechanism tokens."""
    refs = [r for r in (finding.get("evidence_refs") or []) if isinstance(r, str) and r]
    if any(_ref_present(r, region) for r in refs):
        return True
    low = region.lower()
    toks = _mech_tokens(finding.get("mechanism", ""))
    return sum(1 for t in toks if re.search(r"\b%s\b" % re.escape(t), low)) >= 2


def _body(text):
    m = APPENDIX_A_RE.search(text) or SEVCAL_RE.search(text)
    return text[:m.start()] if m else text


def _sevcal(text):
    m = SEVCAL_RE.search(text)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = NEXT_APPENDIX_RE.search(rest)
    return rest[:nxt.start()] if nxt else rest


def _last_severity_on(line):
    """The DELIVERED severity = last severity token on the line ('softened to X')."""
    delivered, pos = None, -1
    for sev in SEV_TOKENS:
        p = line.rfind(sev)
        if p > pos:
            pos, delivered = p, sev
    return delivered


def _recorded_severity(sevcal, finding):
    """Heuristic: delivered severity on the calibration line matching the finding
    (mechanism / refs). Lowest across matching lines (any downgrade counts)."""
    best = None
    for line in sevcal.splitlines():
        if not _region_contains(line, finding):
            continue
        d = _last_severity_on(line)
        if d is not None and (best is None or SEV_RANK[d] < SEV_RANK[best]):
            best = d
    return best


def _recorded_severity_by_id(sevcal, fid):
    """Exact: delivered severity across ALL calibration lines citing the finding's
    ID; lowest wins, so a later 'softened to Should-Fix' line is authoritative
    (mirrors the heuristic path)."""
    best = None
    for line in sevcal.splitlines():
        if _id_present(line, fid):
            d = _last_severity_on(line)
            if d is not None and (best is None or SEV_RANK[d] < SEV_RANK[best]):
                best = d
    return best


def _structured_calibration(letter_text):
    """(id -> delivered severity, block_errors). Embedded apodictic:severity_calibration blocks
    are read in preference to the prose heuristic (lowest delivered wins on repeats). Each block
    is schema-validated: a malformed or schema-invalid block is an ERROR rather than being
    silently skipped — the structured Severity Calibration is a delivery contract, so an invalid
    block must not quietly fall back to prose delivery."""
    out, errs = {}, []
    schema = art.load_schema("apodictic.severity_calibration.v1")
    n = 0
    for btype, obj, jerr in art.parse_blocks(letter_text):
        if btype != "severity_calibration":
            continue
        n += 1
        where = "Severity Calibration block #%d" % n
        if jerr:
            errs.append("%s: invalid JSON — %s" % (where, jerr))
            continue
        if not isinstance(obj, dict):
            errs.append("%s: not a JSON object" % where)
            continue
        block_errs = art.validate_obj(obj, schema, where) if schema is not None else []
        if block_errs:
            errs.extend(block_errs)
            continue
        fid, delivered = obj.get("id"), obj.get("delivered")
        if fid and delivered in SEV_RANK:
            if fid not in out or SEV_RANK[delivered] < SEV_RANK[out[fid]]:
                out[fid] = delivered
    return out, errs


def _has_hedge(body, finding):
    for line in body.splitlines():
        if _region_contains(line, finding) and any(h in line.lower() for h in HEDGES):
            return True
    return False


def _short(s, n=60):
    s = str(s)
    return s if len(s) <= n else s[:n] + "…"


def softness_check(letter_text, ledger_text):
    """Return (errors, warnings)."""
    errs, warns = [], []
    body = _body(letter_text)
    sevcal = _sevcal(letter_text)
    struct_cal, cal_block_errs = _structured_calibration(letter_text)
    # A malformed/schema-invalid Severity Calibration block is a broken delivery contract —
    # hard ERROR (the softness-downgrade override cannot mask it).
    errs.extend("invalid Severity Calibration block — %s" % e for e in cal_block_errs)
    marker = SOFT_MARKER in body
    for f in parse_locked_findings(ledger_text):
        lock = f.get("severity")
        if lock not in LOCKED:
            continue
        mech = _short(f.get("mechanism", "?"))
        fid = f.get("id")
        if fid:
            in_body = _id_delivered_in_body(body, fid, f)
            # Prefer the structured Severity Calibration block; fall back to prose.
            rec = struct_cal.get(fid)
            if rec is None:
                rec = _recorded_severity_by_id(sevcal, fid)
            label = "%s — %s" % (fid, mech)
        else:
            in_body = _region_contains(body, f)
            rec = _recorded_severity(sevcal, f)
            label = mech
        problem = None
        if rec is not None and SEV_RANK[rec] < SEV_RANK[lock]:
            problem = "Severity Calibration records %s, below the locked %s" % (rec, lock)
        elif not in_body and rec is None:
            problem = "locked %s finding absent from both the body and Severity Calibration (dropped)" % lock
        elif not in_body:
            problem = "locked %s finding recorded in Severity Calibration but absent from the author-facing body (buried)" % lock
        if problem:
            msg = "%s (%s)" % (problem, label)
            if marker:
                warns.append(msg + " — softness-downgrade marker present (acknowledged)")
            else:
                errs.append(msg + " — no softness-downgrade override marker in body")
        elif _has_hedge(body, f):
            warns.append("locked %s finding (%s) delivered but hedged in the body" % (lock, label))
    return errs, warns


def deficit_lock(ledger_text):
    """Return (errors, warnings). Verifies EVERY synthesis-bound finding was locked."""
    errs, warns = [], []
    locks = parse_locked_findings(ledger_text)
    finding_schema = art.load_schema("apodictic.finding.v1")
    # Only SCHEMA-VALID locks count — a block missing required fields is not a lock.
    n_struct = sum(1 for f in locks if f.get("severity") in LOCKED
                   and (finding_schema is None or not art.validate_obj(f, finding_schema)))
    prose_labels = len(PROSE_SEVERITY_RE.findall(art.BLOCK_RE.sub("", ledger_text)))
    if prose_labels > n_struct:
        errs.append("ledger has %d synthesis-bound (Must-Fix/Should-Fix) finding label(s) but only "
                    "%d structured apodictic.finding.v1 lock(s) — every synthesis-bound finding must "
                    "be locked (Deficit Lock)" % (prose_labels, n_struct))
    return errs, warns


def report(errs, warns, label):
    for w in warns:
        print("WARN: %s" % w)
    for e in errs:
        print("ERROR: %s" % e)
    if errs:
        print("%s: FAIL (%d error(s), %d warning(s))" % (label, len(errs), len(warns)))
        return 1
    print("%s: PASS%s" % (label, (" (%d warning(s))" % len(warns)) if warns else ""))
    return 0


def run_self_test():
    import json
    rc = {"v": 0}

    def check(name, errs, expect_clean):
        if (len(errs) == 0) == expect_clean:
            print("  %s: OK" % name)
        else:
            print("  %s: FAIL (errs=%s)" % (name, errs))
            rc["v"] = 1

    # ---- heuristic path (id-less findings; backward-compat) ----
    lock = ('<!-- apodictic:finding\n'
            '{"schema":"apodictic.finding.v1","mechanism":"Theo has no arc; protagonist does not change",'
            '"severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Chapter 34"],'
            '"fix_class":"x","risk_if_fixed":"y"}\n-->')

    def letter(body_line, sevcal_sev):
        return ("# Edit\n## What Needs Work\n" + body_line + "\n"
                "## Appendix A: Diagnostic Detail\np\n"
                "## Appendix B: Severity Calibration\n"
                "Theo's zero arc: Pass 5 confirms. Severity held at " + sevcal_sev + ".\n")

    check("good_delivered_and_recorded",
          softness_check(letter("Theo has no arc, and the catalyst defense fails (Chapter 34).", "Must-Fix"), lock)[0], True)
    check("downgrade_in_calibration",
          softness_check(letter("Theo has no arc (Chapter 34).", "Should-Fix"), lock)[0], False)
    check("buried_absent_from_body",
          softness_check(letter("The pacing wanders a little in the middle.", "Must-Fix"), lock)[0], False)
    check("dropped_from_both",
          softness_check("# Edit\n## What Needs Work\nPacing only.\n## Appendix B: Severity Calibration\nNothing relevant.\n", lock)[0], False)
    lock_ch3 = ('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","mechanism":"subplot stall qrstuv",'
                '"severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Chapter 3"],"fix_class":"x","risk_if_fixed":"y"}\n-->')
    check("prefix_ref_not_matched",
          softness_check("# Edit\n## What Needs Work\nMust-Fix: pacing wanders in Chapter 34.\n"
                         "## Appendix B: Severity Calibration\nChapter 34 pacing: Severity held at Must-Fix.\n", lock_ch3)[0], False)
    body_mk = ("# Edit\n## What Needs Work\nTheo has no arc (Chapter 34).\n"
               "<!-- override: softness-downgrade — over-diagnosed; see Appendix B -->\n"
               "## Appendix B: Severity Calibration\nTheo's zero arc: Severity Should-Fix.\n")
    check("downgrade_with_body_marker_warns", softness_check(body_mk, lock)[0], True)
    e_h, w_h = softness_check(letter("Theo's arc could perhaps be strengthened (Chapter 34).", "Must-Fix"), lock)
    check("hedged_warns_no_error", e_h, True)
    check("hedged_has_warning", [] if w_h else ["no warning"], True)

    # ---- ID path (exact matching) ----
    lock_id = ('<!-- apodictic:finding\n'
               '{"schema":"apodictic.finding.v1","id":"F-P5-02","mechanism":"protagonist never changes; no arc",'
               '"severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Chapter 34"],'
               '"fix_class":"x","risk_if_fixed":"y"}\n-->')

    def letter_id(fid, sevcal_sev, body_has=True, prose=True):
        body = "# Edit\n## What Needs Work\n"
        if prose:
            body += "The protagonist never changes across the novel (Chapter 34).\n"
        if body_has:
            body += "<!-- finding: %s -->\n" % fid
        return (body + "## Appendix A\np\n## Appendix B: Severity Calibration\n"
                + "%s Theo's zero arc: Severity held at %s.\n" % (fid, sevcal_sev))
    check("id_exact_match_pass", softness_check(letter_id("F-P5-02", "Must-Fix"), lock_id)[0], True)
    check("id_downgrade_errors", softness_check(letter_id("F-P5-02", "Should-Fix"), lock_id)[0], False)
    check("id_buried_errors", softness_check(letter_id("F-P5-02", "Must-Fix", body_has=False, prose=False), lock_id)[0], False)
    # [P1] a bare `<!-- finding: ID -->` comment with no author-facing prose is NOT a delivery
    check("id_comment_only_not_delivered", softness_check(letter_id("F-P5-02", "Must-Fix", prose=False), lock_id)[0], False)
    # near-miss ID must NOT match (boundary): letter cites F-P5-021, lock is F-P5-02
    check("id_near_miss_not_matched", softness_check(letter_id("F-P5-021", "Must-Fix"), lock_id)[0], False)
    # a LATER calibration line that downgrades the same ID is authoritative (lowest wins)
    check("id_later_downgrade_caught",
          softness_check("# Edit\n## What Needs Work\nThe protagonist never changes across the novel (Chapter 34).\n"
                         "<!-- finding: F-P5-02 -->\n## Appendix B: Severity Calibration\n"
                         "F-P5-02 Theo's zero arc: Severity held at Must-Fix.\n"
                         "F-P5-02 on reflection: softened to Should-Fix.\n", lock_id)[0], False)

    # ---- structured Severity Calibration (apodictic.severity_calibration.v1) ----
    def letter_struct(delivered, prose_sev="Must-Fix"):
        direction = "unchanged" if delivered == "Must-Fix" else "softened"
        return ("# Edit\n## What Needs Work\n"
                "The protagonist never changes across the novel (Chapter 34).\n"
                "<!-- finding: F-P5-02 -->\n"
                "## Appendix A\np\n## Appendix B: Severity Calibration\n"
                "F-P5-02 Theo's zero arc: Severity held at %s.\n" % prose_sev
                + '<!-- apodictic:severity_calibration\n'
                  '{"schema":"apodictic.severity_calibration.v1","id":"F-P5-02","locked":"Must-Fix",'
                  '"delivered":"%s","direction":"%s"}\n-->\n' % (delivered, direction))
    check("struct_cal_match_pass", softness_check(letter_struct("Must-Fix"), lock_id)[0], True)
    check("struct_cal_downgrade_errors", softness_check(letter_struct("Should-Fix"), lock_id)[0], False)
    # structured block is authoritative over the prose line (prose says Must-Fix, block says Should-Fix)
    check("struct_cal_overrides_prose", softness_check(letter_struct("Should-Fix", prose_sev="Must-Fix"), lock_id)[0], False)

    # A malformed / schema-invalid calibration block is a hard ERROR (delivery contract),
    # even when the body delivers the locked finding at the right tier (no silent prose fallback).
    def letter_bad_block(block_json):
        return ("# Edit\n## What Needs Work\n"
                "The protagonist never changes across the novel (Chapter 34).\n"
                "<!-- finding: F-P5-02 -->\n"
                "## Appendix B: Severity Calibration\n"
                "<!-- apodictic:severity_calibration\n%s\n-->\n" % block_json)
    bad_delivered = ('{"schema":"apodictic.severity_calibration.v1","id":"F-P5-02",'
                     '"locked":"Must-Fix","delivered":"Critical","direction":"unchanged"}')
    missing_direction = ('{"schema":"apodictic.severity_calibration.v1","id":"F-P5-02",'
                         '"locked":"Must-Fix","delivered":"Must-Fix"}')
    bad_json = ('{"schema":"apodictic.severity_calibration.v1","id":"F-P5-02" '
                '"delivered":"Must-Fix","direction":"unchanged"}')  # missing comma -> invalid JSON
    check("struct_cal_bad_delivered_errors", softness_check(letter_bad_block(bad_delivered), lock_id)[0], False)
    check("struct_cal_missing_direction_errors", softness_check(letter_bad_block(missing_direction), lock_id)[0], False)
    check("struct_cal_malformed_json_errors", softness_check(letter_bad_block(bad_json), lock_id)[0], False)

    # ---- deficit-lock ----
    valid_block = ('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"F-P5-01","mechanism":"m",'
                   '"severity":"Must-Fix","confidence":"HIGH","evidence_refs":["c"],"fix_class":"x","risk_if_fixed":"y"}\n-->')
    check("lock_structured_present", deficit_lock(valid_block)[0], True)
    check("lock_prose_without_struct_errors", deficit_lock("## Ledger\n- Must-Fix: agency collapse (prose only)\n")[0], False)
    check("lock_empty_ledger_ok", deficit_lock("## Ledger\n- data-building pass\n")[0], True)
    realistic = "## Pass 5 — Ledger Entry\n### Notable Findings\n1. **Theo's zero arc.** Severity: Must-Fix.\n" + valid_block + "\n"
    check("lock_all_present_ok", deficit_lock(realistic)[0], True)
    check("lock_partial_missing_errors", deficit_lock(realistic + "2. **Reveal fairness.** Severity: Should-Fix.\n")[0], False)
    # [P2] an INVALID finding block (missing required fields) must not count as a lock
    check("lock_invalid_block_not_counted",
          deficit_lock("## Pass 8 — Ledger Entry\n### Notable Findings\n1. **Reveal.** Severity: Must-Fix.\n"
                       '<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","severity":"Must-Fix"}\n-->\n')[0], False)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "--self-test":
        return run_self_test()
    if cmd == "softness-check":
        if len(argv) < 4:
            print("Usage: honesty_check.py softness-check <editorial_letter> <findings_ledger>")
            return 2
        try:
            letter_text = open(argv[2], encoding="utf-8").read()
            ledger_text = open(argv[3], encoding="utf-8").read()
        except OSError as exc:
            print("Error: %s" % exc)
            return 2
        return report(*softness_check(letter_text, ledger_text), label="softness-check")
    if cmd == "deficit-lock":
        if len(argv) < 3:
            print("Usage: honesty_check.py deficit-lock <findings_ledger>")
            return 2
        try:
            ledger_text = open(argv[2], encoding="utf-8").read()
        except OSError as exc:
            print("Error: %s" % exc)
            return 2
        return report(*deficit_lock(ledger_text), label="deficit-lock")
    print("Unknown command: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
