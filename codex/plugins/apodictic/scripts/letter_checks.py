#!/usr/bin/env python3
"""Shared parsers + checks for APODICTIC editorial-letter / ledger validators.

Backs validate.sh's prose-validator arms with a real parser and token-boundary
matching, replacing brittle shell regex (the recurring source of severity-label /
prefix evidence-ref / calibration-line edge-case findings). validate.sh stays the
command surface and degrades to its prior bash path when python3 is absent.

Ported arms (Validator Architecture Hardening, incremental):
  - severity-floor   — output-policy.md §Severity Floor Rules
  (decision-layer-check, audit-signal-propagation, ... follow in later increments)

Conventions mirror structured_findings.py / honesty_check.py:
  - body vs appendix split: the synthesis body (above the first "Appendix <X>"
    heading) is canonical for findings; appendices hold evidence and are
    non-canonical for override markers.
  - override markers are HTML comments honored ONLY in the body.
  - each check returns (errors, warnings) lists; callers map a non-empty errors
    list to exit 1, warnings to a WARN line + exit 0.
  - the surfaced lines keep the legacy "ERROR:" / "WARN:" / "FAILED:" / "OK:"
    prefixes that callers (e.g. underdiagnosis-triggers Trigger #5) grep for.
  - data-driven fixtures under test_fixtures/lc.*  (.pass.->exit 0, .fail.->exit 1).

CLI:
  letter_checks.py severity-floor <letter_file> [<ledger_file>]
  letter_checks.py --self-test [<check-name>]
"""

import glob
import os
import re
import sys

# First "Appendix <X>" heading marks the boundary between the canonical synthesis
# body and the (non-canonical, evidence-bearing) appendices.
_APPENDIX_RE = re.compile(r"^#{1,4}.*Appendix\s+[A-Za-z]", re.IGNORECASE | re.MULTILINE)

# Verdict bands that a Systemic Must-Fix (Rule 2) / high flag volume (Rule 3)
# must not coexist with unmarked.
_HIGH_VERDICT_RE = re.compile(
    r"(Strong Fit|publishable as[- ]is|Highest Band|Excellent Fit)", re.IGNORECASE)
_JUSTIFICATION_RE = re.compile(
    r"(flag volume|justification|justified|does not impair)", re.IGNORECASE)
_WEAK_AXIS_RE = re.compile(r"Weak\s+(at\s+)?(High|Medium)", re.IGNORECASE)


def split_body(text):
    """Return the synthesis body (everything before the first Appendix heading).

    The full text is canonical for *findings* (severity tokens, verdicts), but only
    the body is canonical for *override markers* — markers in an appendix do not
    count, matching the legacy bash behavior.
    """
    m = _APPENDIX_RE.search(text)
    return text[: m.start()] if m else text


def has_override(body, slug):
    """True if an override HTML-comment marker for `slug` appears in the body."""
    return ("<!-- override: %s" % slug) in body


def count_token(text, token):
    """Case-insensitive count of literal `token` occurrences (e.g. 'Must-Fix')."""
    return len(re.findall(re.escape(token), text, re.IGNORECASE))


def severity_floor(text):
    """Mechanical check of the three Severity Floor Rules.

    Canonical home: core-editor/references/output-policy.md §Severity Floor Rules.
    Severity tokens / verdicts are read from the whole letter; override markers
    only from the body. Returns (errors, warnings).
    """
    errors, warnings = [], []
    body = split_body(text)
    must = count_token(text, "Must-Fix")
    should = count_token(text, "Should-Fix")

    # Rule 1: Weak core-promise axis at High/Medium intensity -> >=1 Must-Fix.
    if _WEAK_AXIS_RE.search(text) and must < 1:
        if has_override(body, "severity-floor-weak-axis"):
            warnings.append("WARN: Rule 1 — Weak axis present at High/Medium intensity "
                            "with no Must-Fix flag (override marker detected in letter body).")
        else:
            errors.append("ERROR: Rule 1 — Weak core-promise axis at High/Medium intensity "
                          "but no Must-Fix flag (no override marker in body).")

    # Rule 2: Systemic Must-Fix -> verdict <= Partial Fit.
    if re.search(r"Systemic", text, re.IGNORECASE) and must >= 1 and _HIGH_VERDICT_RE.search(text):
        if has_override(body, "severity-floor-systemic"):
            warnings.append("WARN: Rule 2 — Systemic Must-Fix paired with high verdict band "
                            "(override marker detected in letter body).")
        else:
            errors.append("ERROR: Rule 2 — Systemic Must-Fix flag present but verdict exceeds "
                          "Partial Fit ceiling (no override marker in body).")

    # Rule 3: >=3 Should-Fix-or-above -> highest positive band needs justification.
    sf_total = should + must
    if sf_total >= 3 and _HIGH_VERDICT_RE.search(text):
        if _JUSTIFICATION_RE.search(text):
            pass  # justification present
        elif has_override(body, "severity-floor-band-cap"):
            warnings.append("WARN: Rule 3 — ≥3 Should-Fix-or-above flags with highest verdict "
                            "band (override marker detected in letter body).")
        else:
            errors.append("ERROR: Rule 3 — %d Should-Fix-or-above flags with highest verdict "
                          "band and no explicit justification (no override marker in body)."
                          % sf_total)

    return errors, warnings, \
        "OK: Severity-floor rules satisfied (or override marker present in body).", \
        ("FAILED: %d severity-floor rule failure(s). Canonical rules: "
         "core-editor/references/output-policy.md §Severity Floor Rules." % len(errors))


# --------------------------------------------------------------------------
# decision-layer-check — Decision-Layer Consolidation contract.
# Canonical homes: core-editor/references/run-synthesis.md §Step 7 +
# output-policy.md §Mandatory Appendices / §Evidence Density Self-Check.
# Faithful port of the bash arm (subhead-cluster / list / bold-paragraph /
# verb-paragraph counting; argument-DE class detection; body-only Must-Fix
# evidence-density windows).
# --------------------------------------------------------------------------

_LEVEL2_RE = re.compile(r"^##[^#]")
_ARGUMENT_DE_RE = re.compile(
    r"(Coalition-Partner Ground-Truth|Editorial-Dispute Territory|Argument_State|"
    r"Claim Ladder|Argument Engine)", re.IGNORECASE)
_REF_RE = re.compile(
    r"(Chapter\s+[0-9]+|Ch\.\s*[0-9]+|Scene\s+[0-9]+|lines?\s+[0-9]+|L[0-9]+|"
    r"page\s+[0-9]+|p\.\s*[0-9]+|§\s*[A-Za-z0-9.\-]+|[A-Z]{2,5}-[0-9]+)", re.IGNORECASE)


def _content_lines(text):
    """1-based-friendly line list: drop one trailing '' so len() mirrors awk NR / wc -l
    for newline-terminated files (all generated letters and fixtures end in \\n)."""
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return lines


def _extract_section(lines, patterns):
    """Return the section line list under the first heading matching any pattern
    (each pattern tried in order, across the whole doc), bounded by the next
    level-2 heading; None if no heading matches."""
    start = None
    for pat in patterns:
        rx = re.compile(r"^#{1,4}\s+.*" + pat, re.IGNORECASE)
        for i, ln in enumerate(lines):
            if rx.search(ln):
                start = i
                break
        if start is not None:
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if _LEVEL2_RE.match(lines[j]):
            end = j
            break
    return lines[start + 1:end]


def _count_decision_entries(section):
    """Three-tier count: (a) Keep/Cut/Unsure subhead clusters (l3 or bold-paragraph),
    (b) list items, (c) bold-paragraph leaders, (d) verb-leading paragraphs.
    -1 if the section is absent. Case sensitivity mirrors the bash grep flags."""
    if section is None:
        return -1
    sub = sum(1 for ln in section
              if re.match(r"^###\s+(Keep|Cut|Unsure|Defer|Decide)[\s:]*", ln)
              or re.match(r"^\*\*(Keep|Cut|Unsure|Defer|Decide)([\s/—–-]|\*\*$)", ln))
    if sub >= 1:
        return sub
    li = sum(1 for ln in section if re.match(r"^([-*]|[0-9]+\.) ", ln))
    if li > 0:
        return li
    bp = sum(1 for ln in section if re.match(r"^\*\*[^*]", ln))
    if bp > 0:
        return bp
    # (d) verb-leading paragraphs.
    count, prev_blank = 0, True
    for ln in section:
        if ln.strip() == "":
            prev_blank = True
            continue
        if prev_blank and (
                re.match(r"^\s*(Protect|Keep|Cut|Defer|Decide|Unsure)[\s:.,]", ln)
                or re.match(r"^\s*\*\*(Decision|Question|Element|Protect|Keep|Cut|"
                            r"Defer|Decide|Unsure)", ln)):
            count += 1
        prev_blank = False
    return count


def _mf_labeled_lines(lines, body_end):
    """1-based line numbers (<= body_end) of *labeled* Must-Fix entries — heading,
    list/numbered leader (label in first 80 chars), Severity label, MF-N anchor, or
    table severity cell. Prose mentions are excluded."""
    out = []
    for nr in range(1, body_end + 1):
        line = lines[nr - 1]
        ll = line.lower()
        if "must-fix" not in ll:
            continue
        head80_l = line[:80].lower()
        if re.match(r"^#+\s", line):
            out.append(nr)
        elif re.match(r"^\s*[-*]\s", line) and "must-fix" in head80_l:
            out.append(nr)
        elif re.match(r"^\s*[0-9]+\.\s", line) and "must-fix" in head80_l:
            out.append(nr)
        elif re.search(r"\*\*[Ss]everity:?\*\*", line):
            out.append(nr)
        elif re.match(r"^\s*[Ss]everity:\s", line):
            out.append(nr)
        elif re.search(r"MF-[0-9]+", line):
            out.append(nr)
        elif re.match(r"^\s*\|", line) and re.search(r"\|\s*[Mm]ust-[Ff]ix\s*\|", line):
            out.append(nr)
    return out


def decision_layer_check(text):
    errors, warnings = [], []
    lines = _content_lines(text)
    total = len(lines)

    appendix_idx = None  # 1-based
    appx_rx = re.compile(r"^#{1,4}.*Appendix [A-C]", re.IGNORECASE)
    for i, ln in enumerate(lines):
        if appx_rx.search(ln):
            appendix_idx = i + 1
            break
    body = "\n".join(lines[: appendix_idx - 1]) if appendix_idx else "\n".join(lines)
    body_end = (appendix_idx - 1) if appendix_idx else total

    argument_de = bool(_ARGUMENT_DE_RE.search(text))

    def range_check(count, lo, hi, slug, label):
        if count == -1:
            warnings.append("WARN: %s — heading not found." % label)
            return
        if count < lo or count > hi:
            if has_override(body, slug):
                warnings.append("WARN: %s — count %d outside %d-%d range "
                                "(override marker present)." % (label, count, lo, hi))
            else:
                errors.append("ERROR: %s — count %d outside %d-%d range "
                              "(no override marker in body)." % (label, count, lo, hi))

    # Check 1: Protected Elements — 3-6.
    if argument_de:
        pe = _count_decision_entries(_extract_section(
            lines, ["Coalition-Partner Ground-Truth", "Strengths.*Protected Elements",
                    "Protected Elements"]))
    else:
        pe = _count_decision_entries(_extract_section(lines, ["Protected Elements"]))
    range_check(pe, 3, 6, "decision-layer-protected-elements",
                "Check 1 (protected-elements)")

    # Check 2: Author Decisions — 3-7.
    if argument_de:
        ad = _count_decision_entries(_extract_section(
            lines, ["Editorial-Dispute Territory", "Author Decisions"]))
    else:
        ad = _count_decision_entries(_extract_section(lines, ["Author Decisions"]))
    range_check(ad, 3, 7, "decision-layer-author-decisions",
                "Check 2 (author-decisions)")

    # Check 3: Control Questions — exactly 7. Skipped for argument-DE.
    if not argument_de:
        cq = _count_decision_entries(_extract_section(lines, ["Control Questions"]))
        if cq == -1:
            warnings.append("WARN: Check 3 (control-questions) — heading not found.")
        elif cq != 7:
            if has_override(body, "decision-layer-control-questions"):
                warnings.append("WARN: Check 3 (control-questions) — count %d "
                                "(expected exactly 7; override marker present)." % cq)
            else:
                errors.append("ERROR: Check 3 (control-questions) — count %d "
                              "(expected exactly 7; no override marker in body)." % cq)

    # Check 4: Appendices A, B, C present. Skipped for argument-DE.
    if not argument_de:
        missing = [app for app in ("Appendix A", "Appendix B", "Appendix C")
                   if not any(re.search(r"^#{1,4}\s+.*" + app, ln, re.IGNORECASE) for ln in lines)]
        if missing:
            joined = ", ".join(missing)
            if has_override(body, "decision-layer-appendices"):
                warnings.append("WARN: Check 4 (appendices) — missing: %s "
                                "(override marker present)." % joined)
            else:
                errors.append("ERROR: Check 4 (appendices) — missing: %s "
                              "(no override marker in body)." % joined)

    # Check 5: Must-Fix evidence density (body-only labeled MF, paragraph-block window).
    mf_lines = _mf_labeled_lines(lines, body_end)
    section_lines = [nr for nr in range(1, total + 1) if _LEVEL2_RE.match(lines[nr - 1])]
    mf_thin = 0
    for ln in mf_lines:
        next_mf = next((x for x in mf_lines if x > ln), None)
        next_sec = next((s for s in section_lines if s > ln), None)
        end = total
        if next_mf is not None and next_mf < end:
            end = next_mf
        if next_sec is not None and next_sec < end:
            end = next_sec
        if end > ln:
            end -= 1
        block = "\n".join(lines[ln - 1:end])
        if len(_REF_RE.findall(block)) < 2:
            mf_thin += 1
    if mf_thin > 0:
        if has_override(body, "decision-layer-evidence-density"):
            warnings.append("WARN: Check 5 (evidence-density) — %d Must-Fix mention(s) "
                            "with <2 references in paragraph-block window "
                            "(override marker present)." % mf_thin)
        else:
            errors.append("ERROR: Check 5 (evidence-density) — %d Must-Fix mention(s) "
                          "with <2 references in paragraph-block window "
                          "(no override marker in body)." % mf_thin)

    home = ("core-editor/references/run-synthesis.md §Step 7 + "
            "core-editor/references/output-policy.md §Mandatory Appendices / "
            "§Evidence Density Self-Check")
    if argument_de:
        ok = ("OK: Decision-Layer Consolidation contract satisfied (argument-DE class — "
              "Checks 3-4 skipped per C3 calibration; or override markers present).")
        failed = ("FAILED: %d decision-layer-check failure(s) (argument-DE class — "
                  "Checks 3-4 skipped). Canonical homes: %s." % (len(errors), home))
    else:
        ok = "OK: Decision-Layer Consolidation contract satisfied (or override markers present)."
        failed = ("FAILED: %d decision-layer-check failure(s). Canonical homes: %s."
                  % (len(errors), home))
    return errors, warnings, ok, failed


# Registry of file-driven checks: name -> function(text) -> (errors, warnings, ok, failed).
CHECKS = {
    "severity-floor": severity_floor,
    "decision-layer-check": decision_layer_check,
}


def run_check(name, path):
    """Run a registered check against a file; print legacy-format lines; return rc."""
    fn = CHECKS.get(name)
    if fn is None:
        sys.stderr.write("Error: unknown check: %s\n" % name)
        return 2
    if not os.path.isfile(path):
        sys.stderr.write("Error: File not found: %s\n" % path)
        return 2
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    errors, warnings, ok_line, failed_line = fn(text)
    for w in warnings:
        print(w)
    for e in errors:
        print(e)
    if errors:
        print("")
        print(failed_line)
        return 1
    print(ok_line)
    return 0


def _fixture_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    for c in (os.path.join(here, "test_fixtures"),
              os.path.join(here, "..", "plugins", "apodictic", "scripts", "test_fixtures")):
        if os.path.isdir(c):
            return c
    return None


def run_self_test(which=None):
    rc = {"v": 0}

    def check(name, errs, expect_clean):
        if (len(errs) == 0) == expect_clean:
            print("  %s: OK" % name)
        else:
            print("  %s: FAIL (errs=%s)" % (name, errs))
            rc["v"] = 1

    def warns(name, ws, expect_warn):
        if (len(ws) > 0) == expect_warn:
            print("  %s: OK" % name)
        else:
            print("  %s: FAIL (warns=%s)" % (name, ws))
            rc["v"] = 1

    if which in (None, "severity-floor"):
        # In-code unit cases (mirror the legacy bash self-test, plus warn-class assertions).
        clean = ("# Development Edit\n## What Needs Work\nPacing Should-Fix flag.\n"
                 "## Appendix B\nSeverity Calibration: tested.\n")
        check("sf_clean", severity_floor(clean)[0], True)
        weak_no_mf = ("# Development Edit\n## Best\nVoice axis rated Weak at High intensity.\n"
                      "## What Needs Work\nPacing Should-Fix flag.\n## Appendix B\nx\n")
        check("sf_weak_no_mustfix", severity_floor(weak_no_mf)[0], False)
        systemic = ("# Development Edit\nVerdict: Strong Fit.\n"
                    "Must-Fix: structural pattern with Systemic blast radius.\n")
        check("sf_systemic_high_verdict", severity_floor(systemic)[0], False)
        band = ("# Development Edit\nVerdict: publishable as-is.\n"
                "Should-Fix one. Should-Fix two. Should-Fix three. Should-Fix four.\n")
        check("sf_band_cap", severity_floor(band)[0], False)
        # Override in body -> WARN (exit 0), not ERROR.
        over_body = ("# Development Edit\n## Best\nVoice axis rated Weak at High intensity.\n"
                     "<!-- override: severity-floor-weak-axis — editorial stance, see Appendix B. -->\n"
                     "## What Needs Work\nPacing Should-Fix flag.\n## Appendix B\nx\n")
        e, w = severity_floor(over_body)[:2]
        check("sf_override_body_no_error", e, True)
        warns("sf_override_body_warns", w, True)
        # Marker in appendix only -> still ERROR (body is canonical for markers).
        over_appx = ("# Development Edit\n## Best\nVoice axis rated Weak at High intensity.\n"
                     "## What Needs Work\nPacing Should-Fix flag.\n## Appendix B\n"
                     "<!-- override: severity-floor-weak-axis — marker in appendix only. -->\n")
        check("sf_override_appendix_still_errors", severity_floor(over_appx)[0], False)
        # Justification text defuses Rule 3 even at the highest band.
        justified = ("# Development Edit\nVerdict: Strong Fit. The flag volume does not impair.\n"
                     "Should-Fix one. Should-Fix two. Should-Fix three.\n")
        check("sf_justified_band", severity_floor(justified)[0], True)

    # Data-driven fixtures: lc.<pass|fail>.<check>.<name>.md in test_fixtures/.
    fdir = _fixture_dir()
    if fdir:
        for path in sorted(glob.glob(os.path.join(fdir, "lc.*"))):
            name = os.path.basename(path)
            parts = name.split(".")
            chk = parts[2] if len(parts) > 3 else "severity-floor"
            if which not in (None, chk):
                continue
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                txt = fh.read()
            fn = CHECKS.get(chk, severity_floor)
            check("fixture:%s" % name, fn(txt)[0], ".pass." in name)
    else:
        print("  fixtures: SKIP (test_fixtures/ not found)")

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if len(argv) < 2:
        sys.stdout.write(__doc__)
        return 2
    if argv[1] == "--self-test":
        which = argv[2] if len(argv) > 2 else None
        return run_self_test(which)
    if argv[1] in CHECKS:
        if len(argv) < 3:
            sys.stderr.write("Usage: letter_checks.py %s <file> [<ledger_file>]\n" % argv[1])
            return 2
        return run_check(argv[1], argv[2])
    sys.stderr.write("Error: unknown command: %s\n" % argv[1])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
