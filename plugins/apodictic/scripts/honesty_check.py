#!/usr/bin/env python3
"""APODICTIC honesty gate (Phase 4): Deficit Lock + Softness Gate.

Closes the uniform-charity / silent-softening leak — a letter that under-delivers
a finding it already locked at Triage, while still passing severity-floor and
audit-signal-propagation.

  softness-check <editorial_letter> <findings_ledger>
      Compare the delivered letter against the Triage-locked findings
      (apodictic.finding.v1 blocks in the ledger). For each locked
      Must-Fix/Should-Fix, read the severity the letter RECORDS for it in its
      Severity Calibration appendix (Appendix B) — author-facing letters keep
      severity labels there, not inline in the body. ERROR when:
        * the recorded severity is below the lock (silent downgrade), or
        * the locked finding is absent from the author-facing body (buried), or
        * the locked finding is absent from both (dropped),
      unless a body override marker is present. Hedged delivery -> WARN.
      Weak-axis-vs-Must-Fix coherence is owned by `severity-floor`, not here.

  deficit-lock <findings_ledger>
      Verify the lock was actually recorded: the ledger carries structured
      apodictic.finding.v1 locks. ERROR if it states Must-Fix/Should-Fix
      severities in prose but records zero structured locks.

  --self-test     built-in cases (both checks)

Severity tokens are canonical (output-policy.md §Canonical Severity Scale). The
body override marker is `<!-- override: softness-downgrade — <rationale> -->`
(body-only; markers in the appendix are non-canonical). Substring matching is
HTML-tolerant: severity tokens, evidence refs, and mechanism keywords appear in
the text content of both Markdown and rendered-HTML letters.

Exit: 0 pass (no ERROR), 1 ERROR(s), 2 usage error.
"""
import json
import re
import sys

SEV_RANK = {"Could-Fix": 1, "Should-Fix": 2, "Must-Fix": 3}
SEV_TOKENS = ("Must-Fix", "Should-Fix", "Could-Fix")
LOCKED = {"Must-Fix", "Should-Fix"}
HEDGES = ["could perhaps", "might benefit", "somewhat", "arguably",
          "relatively minor", "on the softer side", "not a dealbreaker",
          "could be strengthened", "may want to consider", "if you have time",
          "a minor quibble", "nitpick"]
STOP = {"the", "and", "for", "not", "with", "that", "this", "from", "into",
        "when", "does", "are", "was", "but", "its", "has", "you", "your",
        "than", "then", "doesn", "isn"}
BLOCK_RE = re.compile(r"<!--\s*apodictic:finding\s*(\{.*?\})\s*-->", re.DOTALL)
APPENDIX_A_RE = re.compile(r"Appendix\s+A\b", re.IGNORECASE)
SEVCAL_RE = re.compile(r"Severity\s+Calibration|Appendix\s+B\b", re.IGNORECASE)
NEXT_APPENDIX_RE = re.compile(r"Appendix\s+[C-Z]\b", re.IGNORECASE)
SOFT_MARKER = "<!-- override: softness-downgrade"


def parse_locked_findings(ledger_text):
    out = []
    for payload in BLOCK_RE.findall(ledger_text):
        try:
            obj = json.loads(payload.strip())
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and str(obj.get("schema", "")).startswith("apodictic.finding."):
            out.append(obj)
    return out


def _mech_tokens(mech):
    words = re.findall(r"[A-Za-z][A-Za-z'\-]{2,}", str(mech).lower())
    return {w for w in words if w not in STOP}


def _region_contains(region, finding):
    """True if `finding` is present in `region` — any evidence_ref substring, or
    >= 2 distinctive mechanism tokens."""
    refs = [r for r in (finding.get("evidence_refs") or []) if r]
    if any(ref in region for ref in refs):
        return True
    low = region.lower()
    toks = _mech_tokens(finding.get("mechanism", ""))
    return sum(1 for t in toks if t in low) >= 2


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


def _recorded_severity(sevcal, finding):
    """Highest severity token recorded for `finding` within the Severity
    Calibration region (matched by mechanism tokens / evidence refs). None if the
    finding is not recorded there."""
    best = None
    # Severity Calibration records one finding + its severity per line, so read
    # the severity from the matching line itself (a wider window lets an adjacent
    # entry's severity bleed in and mask a downgrade).
    for line in sevcal.splitlines():
        if _region_contains(line, finding):
            for sev in SEV_TOKENS:
                if sev in line:
                    if best is None or SEV_RANK[sev] > SEV_RANK[best]:
                        best = sev
                    break
    return best


def _has_hedge(body, finding):
    for line in body.splitlines():
        if _region_contains(line, finding):
            low = line.lower()
            if any(h in low for h in HEDGES):
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
    marker = SOFT_MARKER in body
    for f in parse_locked_findings(ledger_text):
        lock = f.get("severity")
        if lock not in LOCKED:
            continue
        mech = _short(f.get("mechanism", "?"))
        rec = _recorded_severity(sevcal, f)
        in_body = _region_contains(body, f)
        problem = None
        if rec is not None and SEV_RANK[rec] < SEV_RANK[lock]:
            problem = "Severity Calibration records %s, below the locked %s" % (rec, lock)
        elif not in_body and rec is None:
            problem = "locked %s finding absent from both the body and Severity Calibration (dropped)" % lock
        elif not in_body:
            problem = "locked %s finding recorded in Severity Calibration but absent from the author-facing body (buried)" % lock
        if problem:
            msg = "%s (%s)" % (problem, mech)
            if marker:
                warns.append(msg + " — softness-downgrade marker present (acknowledged)")
            else:
                errs.append(msg + " — no softness-downgrade override marker in body")
        elif _has_hedge(body, f):
            warns.append("locked %s finding (%s) delivered but hedged in the body" % (lock, mech))
    return errs, warns


def deficit_lock(ledger_text):
    """Return (errors, warnings). Verifies the lock was recorded structurally."""
    errs, warns = [], []
    locks = parse_locked_findings(ledger_text)
    n_struct = len([f for f in locks if f.get("severity") in LOCKED])
    stripped = BLOCK_RE.sub("", ledger_text)
    prose_hits = len(re.findall(r"Must-Fix", stripped)) + len(re.findall(r"Should-Fix", stripped))
    if n_struct == 0 and prose_hits > 0:
        errs.append("ledger states Must-Fix/Should-Fix severities in prose (%d mention(s)) but "
                    "records zero structured apodictic.finding.v1 locks — Deficit Lock not applied" % prose_hits)
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
    rc = {"v": 0}

    def check(name, errs, expect_clean):
        clean = (len(errs) == 0)
        if clean == expect_clean:
            print("  %s: OK" % name)
        else:
            print("  %s: FAIL (errs=%s)" % (name, errs))
            rc["v"] = 1

    lock = ('<!-- apodictic:finding\n'
            '{"schema":"apodictic.finding.v1","mechanism":"Theo has no arc; protagonist does not change",'
            '"severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Chapter 34"],'
            '"fix_class":"x","risk_if_fixed":"y"}\n-->')

    def letter(body_line, sevcal_sev, extra_body=""):
        return ("# Edit\n## What Needs Work\n" + body_line + "\n" + extra_body +
                "\n## Appendix A: Diagnostic Detail\npass pointers\n"
                "## Appendix B: Severity Calibration\n"
                "Theo's zero arc: Pass 5 confirms. Severity held at " + sevcal_sev + ".\n")

    # known-good: body delivers it, calibration records Must-Fix
    check("good_delivered_and_recorded",
          softness_check(letter("Theo has no arc, and the catalyst defense fails (Chapter 34).", "Must-Fix"), lock)[0], True)
    # silent downgrade in calibration: recorded Should-Fix below locked Must-Fix
    check("downgrade_in_calibration",
          softness_check(letter("Theo has no arc (Chapter 34).", "Should-Fix"), lock)[0], False)
    # buried: recorded Must-Fix but absent from author-facing body
    check("buried_absent_from_body",
          softness_check(letter("The pacing wanders a little in the middle.", "Must-Fix"), lock)[0], False)
    # dropped: absent from both
    check("dropped_from_both",
          softness_check("# Edit\n## What Needs Work\nPacing only.\n## Appendix B: Severity Calibration\nNothing relevant.\n", lock)[0], False)
    # downgrade WITH body marker -> WARN not ERROR
    body_mk = ("# Edit\n## What Needs Work\nTheo has no arc (Chapter 34).\n"
               "<!-- override: softness-downgrade — over-diagnosed; see Appendix B -->\n"
               "## Appendix B: Severity Calibration\nTheo's zero arc: Severity Should-Fix.\n")
    check("downgrade_with_body_marker_warns", softness_check(body_mk, lock)[0], True)
    # marker only in appendix -> still ERROR
    body_appx = ("# Edit\n## What Needs Work\nTheo has no arc (Chapter 34).\n"
                 "## Appendix B: Severity Calibration\nTheo's zero arc: Severity Should-Fix.\n"
                 "<!-- override: softness-downgrade — appendix only -->\n")
    check("appendix_only_marker_still_errors", softness_check(body_appx, lock)[0], False)
    # delivered + recorded but hedged in body -> WARN (no error)
    e_h, w_h = softness_check(letter("Theo's arc could perhaps be strengthened (Chapter 34).", "Must-Fix"), lock)
    check("hedged_warns_no_error", e_h, True)
    check("hedged_has_warning", [] if w_h else ["no warning"], True)
    # deficit-lock: structured lock present
    check("lock_structured_present", deficit_lock(lock)[0], True)
    # deficit-lock: prose severity, no structured lock -> ERROR
    check("lock_prose_without_struct_errors",
          deficit_lock("## Ledger\n- Must-Fix: agency collapse (prose only)\n")[0], False)
    # deficit-lock: empty ledger -> OK
    check("lock_empty_ledger_ok", deficit_lock("## Ledger\n- data-building pass\n")[0], True)

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
