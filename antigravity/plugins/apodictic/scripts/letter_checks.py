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

    return errors, warnings


# Registry of file-driven checks: name -> function(text) -> (errors, warnings).
CHECKS = {
    "severity-floor": severity_floor,
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
    errors, warnings = fn(text)
    for w in warnings:
        print(w)
    for e in errors:
        print(e)
    if errors:
        print("")
        print("FAILED: %d %s rule failure(s). Canonical rules: "
              "core-editor/references/output-policy.md §Severity Floor Rules." % (len(errors), name))
        return 1
    print("OK: %s rules satisfied (or override marker present in body)." % name)
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
        e, w = severity_floor(over_body)
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
