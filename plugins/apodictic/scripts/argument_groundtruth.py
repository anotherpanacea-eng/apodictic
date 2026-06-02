#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mechanical-honesty validator for APODICTIC Argument Benchmark ground-truth files.

Backs `validate.sh argument-groundtruth-check <groundtruth_file>` (docs/argument-benchmark-spec.md
§Mechanical validator). Checks a registered `groundtruth.md` answer key:

  1. GT1-GT7 sections are present and non-empty.
  2. Every referenced code resolves to the Dialectical Clarity namespace
     (AT / CL / SM / WR / BP / OB / DI / NE / AC) or a valid FM-A<x> pattern (x in 1-19).
  3. GT2's failure locus is consistent with its codes: a WARRANT locus carries a WR* code, a
     SUPPORT locus an SM*, a BURDEN locus a BP*, an OBJECTION locus an OB*/DI* (the spec's
     example error — diagnosing a warrant break as a support break). Positive-control GT2s
     marked "N/A — positive control" are exempt. (The locus vocabulary in the corpus is richer
     than a fixed enum — SCOPE / CLAIM-LADDER / FORM / QUALIFIER appear — so the check enforces
     code-consistency for the canonical four loci rather than strict enum membership.)
  4. GT7's Distinguish classification is one of SOUND / UNCONVENTIONAL-BUT-EFFECTIVE / UNSOUND;
     an UNCONVENTIONAL-BUT-EFFECTIVE classification must name >=1 form-dependent code to
     downgrade to advisory.

Output keeps the legacy WARN: / ERROR: / OK: / FAILED: prefixes and exit codes (0 ok, 1 fail,
2 usage) so it slots into --self-test-all alongside the other self-testable validators.

CLI:
    argument_groundtruth.py argument-groundtruth-check <groundtruth_file>
    argument_groundtruth.py --self-test
"""

import os
import re
import sys

# Dialectical Clarity code namespace (docs/argument-benchmark-spec.md §Mechanical validator).
_NAMESPACE = {"AT", "CL", "SM", "WR", "BP", "OB", "DI", "NE", "AC"}
# 2-letter prefixes that are NOT codes (ground-truth section labels GT1..GT7).
_NON_CODE_PREFIXES = {"GT"}
_FM_A_MAX = 19

# Canonical failure loci -> the code family GT2 must carry for that locus.
_LOCUS_FAMILY = {"SUPPORT": ("SM",), "WARRANT": ("WR",), "BURDEN": ("BP",),
                 "OBJECTION": ("OB", "DI")}
_GT7_CLASSES = ["UNCONVENTIONAL-BUT-EFFECTIVE", "UNSOUND", "SOUND"]  # longest-first

_CODE_RE = re.compile(r"\b([A-Z]{2})([0-9]+)\b")
_FM_A_RE = re.compile(r"\bFM-A([0-9]+)\b")
_HEADING_RE = re.compile(r"^#{1,4}\s")
_BARE_PREFIX_RE = re.compile(r"\b(?:AT|CL|SM|WR|BP|OB|DI|NE|AC)\b")
# Leading verdict token of a GT7 "Expected classification" value, skipping markdown emphasis.
_GT7_VERDICT_RE = re.compile(r"[\s*`]*([A-Z][A-Z-]*)")
# Decoy code mentions that do NOT name the diagnosed family: explicitly negated ("not WR0",
# "not WR0/WR2") or marked passing ("WR0 = PASS", "WR0 (PASS)"). Masked before the GT2
# locus<->code-family check so a correct family named only to deny it can't satisfy the check.
_NEGATED_CODES_RE = re.compile(r"\b[Nn][Oo][Tt]\s+((?:[A-Z]{2}[0-9]+(?:\s*[/,]\s*)?)+)")
_PASS_CODE_RE = re.compile(r"\b[A-Z]{2}[0-9]+\s*(?:=\s*PASS\b|\(\s*PASS\s*\))")


def _positive_code_text(text):
    """`text` with decoy (negated / PASS-marked) code mentions removed, so only codes asserted
    as the actual diagnosis remain for the GT2 locus<->code-family consistency check."""
    return _PASS_CODE_RE.sub(" ", _NEGATED_CODES_RE.sub(" ", text))


def _gt_numbers_in_heading(line):
    """All GT section numbers a heading covers — corpus fixtures combine sections under one
    heading, e.g. `## GT4–GT7 — *(PROVISIONAL)*` (a range) or `## GT5 / GT6 — …` (a list)."""
    nums = set()
    for a, b in re.findall(r"GT([1-7])\s*[-–—]\s*(?:GT\s*)?([1-7])", line):
        if int(a) <= int(b):
            nums.update(range(int(a), int(b) + 1))
    nums.update(int(n) for n in re.findall(r"GT([1-7])", line))
    return sorted(nums)


def _parse_gt_sections(text):
    """Return {n: {"body": str, "provisional": bool}} for each GT<n> section. A combined heading
    maps its body to every number it covers; `provisional` is true when the heading is marked
    PROVISIONAL (derive-on-run fixtures that legitimately omit some fields)."""
    sections = {}
    cur, prov, buf = [], False, []

    def flush():
        if cur:
            body = "\n".join(buf).strip()
            for n in cur:
                sections[n] = {"body": body, "provisional": prov}

    for ln in text.split("\n"):
        if _HEADING_RE.match(ln):
            nums = _gt_numbers_in_heading(ln)
            flush()
            cur, prov, buf = nums, ("PROVISIONAL" in ln.upper()), []
            continue
        if cur:
            buf.append(ln)
    flush()
    return sections


def _codes_in(text):
    """Set of namespace codes (e.g. 'WR0') present in text, excluding non-code prefixes."""
    return {p + d for p, d in _CODE_RE.findall(text) if p not in _NON_CODE_PREFIXES}


def _has_family(text, prefixes):
    codes = _codes_in(text)
    return any(c[:2] in prefixes for c in codes)


def argument_groundtruth_check(text):
    errors, warnings = [], []
    sections = _parse_gt_sections(text)

    # Check 1: GT1-GT7 each covered by a heading (combined headings OK) + non-empty.
    for n in range(1, 8):
        sec = sections.get(n)
        if sec is None:
            errors.append("Check 1 (sections) — GT%d not covered by any heading." % n)
        elif not sec["body"].strip():
            errors.append("Check 1 (sections) — GT%d section is empty." % n)

    # Check 2: every code resolves to the namespace or FM-A<1..19>.
    for prefix, digits in _CODE_RE.findall(text):
        if prefix in _NON_CODE_PREFIXES:
            continue
        if prefix not in _NAMESPACE:
            errors.append("Check 2 (codes) — '%s%s' has an unrecognized prefix (not in DC "
                          "namespace AT/CL/SM/WR/BP/OB/DI/NE/AC)." % (prefix, digits))
    for digits in _FM_A_RE.findall(text):
        if not (1 <= int(digits) <= _FM_A_MAX):
            errors.append("Check 2 (codes) — 'FM-A%s' is out of range (x must be 1-%d)."
                          % (digits, _FM_A_MAX))

    # Check 3: GT2 locus <-> code-family consistency (positive controls exempt). The locus
    # vocabulary is richer than a fixed enum and is often compound (e.g. "WARRANT / OBJECTION"),
    # so the rule is: when the locus names any of the canonical four loci, at least one of those
    # named loci's code families must be present in GT2. A single canonical locus whose only
    # codes are from another family (the spec's "WARRANT diagnosed as SUPPORT" error) still fails.
    gt2 = sections.get(2, {}).get("body", "")
    if gt2 and not re.search(r"N/A", gt2) and "positive control" not in gt2.lower():
        m = re.search(r"Primary failure layer:\*\*\s*(.+)", gt2)
        locus = m.group(1) if m else ""
        if not locus.strip():
            errors.append("Check 3 (GT2 locus) — 'Primary failure layer' field is missing or empty.")
        else:
            # Only codes asserted as the diagnosis count — a family named solely to negate it
            # ("not WR0") or mark it passing ("WR0 = PASS") must not satisfy the locus.
            gt2_pos = _positive_code_text(gt2)
            named = {layer: fam for layer, fam in _LOCUS_FAMILY.items()
                     if re.search(r"\b%s\b" % layer, locus)}
            if named and not any(_has_family(gt2_pos, fam) for fam in named.values()):
                want = ", ".join("%s->%s*" % (l, "/".join(f)) for l, f in named.items())
                errors.append("Check 3 (GT2 locus) — locus names %s but GT2 carries no matching "
                              "code (expected one of: %s)." % ("/".join(named), want))

    # Check 4: GT7 Distinguish classification — validated when the field is present (provisional /
    # derive-on-run fixtures legitimately omit it).
    gt7 = sections.get(7, {}).get("body", "")
    m = re.search(r"Expected classification:\*\*\s*(.+)", gt7)
    if m:
        cls_line = m.group(1)
        # The verdict is the field value at the *start* of the line; a trailing parenthetical,
        # dash-set-off rationale, or "..., not UNSOUND" gloss is commentary, not the
        # classification. Parse the leading token so "SOUND — ... not UNSOUND" reads as SOUND
        # (not UNSOUND) and "BROKEN, not UNSOUND" is correctly rejected.
        vm = _GT7_VERDICT_RE.match(cls_line)
        verdict = vm.group(1) if vm else ""
        cls = verdict if verdict in _GT7_CLASSES else None
        if cls is None:
            errors.append("Check 4 (GT7) — classification is not one of SOUND / "
                          "UNCONVENTIONAL-BUT-EFFECTIVE / UNSOUND (got %r)." % cls_line.strip())
        elif cls == "UNCONVENTIONAL-BUT-EFFECTIVE":
            # Must identify the form-dependent codes to downgrade — specific (SM0 / FM-A1) or
            # family-level ("DI codes", "SM/WR on the cost accounting") references both count.
            if not (_codes_in(gt7) or _FM_A_RE.search(gt7) or _BARE_PREFIX_RE.search(gt7)):
                errors.append("Check 4 (GT7) — UNCONVENTIONAL-BUT-EFFECTIVE must name >=1 "
                              "form-dependent code to downgrade to advisory, but GT7 names none.")

    ok = "OK: Argument ground-truth contract satisfied (GT1-GT7 present; codes resolve; locus consistent)."
    failed = ("FAILED: %d argument-groundtruth-check failure(s). Canonical home: "
              "docs/argument-benchmark-spec.md §Mechanical validator + evals/argument-groundtruth-template.md."
              % len(errors))
    return errors, warnings, ok, failed


def _emit(errors, warnings, ok_line, failed_line):
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


# --------------------------------------------------------------------------
# Self-test (hermetic — built-in valid + invalid ground-truth fixtures).
# --------------------------------------------------------------------------

_VALID_GT = """# Ground Truth: self-test

## Provenance
- **Fixture slug:** self-test

## GT1 — Main claim *(Q1; §2 C0)*
- **Expected C0:** "X should do Y."

## GT2 — Failure locus *(Q2; §3 Support vs §4 Warrant)*
- **Primary failure layer:** WARRANT
- **Expected codes:** WR0 (warrant gap) + WR2 (scheme fragility). SM = PASS.

## GT3 — Strongest real objection *(Q3; §6)*
- **Expected OB / DI codes:** OB3.

## GT4 — Audience calibration *(Q4; §1 Audience + AC codes)*
- **Audience profile:** Expertise GENERAL · Receptivity MIXED · Consequence MEDIUM (AC1).

## GT5 — Dangerous weakness for red-team *(Q5; §10.4)*
- **Pre-registered vulnerabilities:** no denominator.

## GT6 — Repair order *(Q6; §10.5)*
- **Correct first repair target:** warrant.

## GT7 — Distinguish classification *(Q7; §1 Distinguish / Step 9)*
- **Expected classification:** UNSOUND
- **False-positive trap:** calling it SOUND because it cites evidence.

## Notes
free-form.
"""


def run_self_test(which=None):
    rc = {"v": 0}

    def check(name, errs, expect_clean):
        ok = (len(errs) == 0) == expect_clean
        print("  %s: %s" % (name, "OK" if ok else "FAIL (errs=%s)" % errs))
        if not ok:
            rc["v"] = 1

    def errs_of(text):
        return argument_groundtruth_check(text)[0]

    check("valid", errs_of(_VALID_GT), True)
    # Check 1: a missing GT section.
    check("missing_section", errs_of(_VALID_GT.replace(
        "## GT5 — Dangerous weakness for red-team *(Q5; §10.4)*\n- **Pre-registered vulnerabilities:** no denominator.\n", "")), False)
    # Check 1: an empty GT section.
    check("empty_section", errs_of(_VALID_GT.replace(
        "- **Expected OB / DI codes:** OB3.", "")), False)
    # Check 2: an unrecognized code prefix.
    check("bad_code_prefix", errs_of(_VALID_GT.replace("WR0", "XR0")), False)
    # Check 2: FM-A out of range.
    check("fm_a_out_of_range", errs_of(_VALID_GT.replace("OB3.", "OB3 (FM-A42).")), False)
    # Check 3: WARRANT locus with no WR code (only SM) — the spec's example error.
    check("warrant_without_wr", errs_of(_VALID_GT.replace(
        "WR0 (warrant gap) + WR2 (scheme fragility). SM = PASS.", "SM0 (assertion gap).")), False)
    # Check 4: GT7 classification not one of the three.
    check("bad_gt7_class", errs_of(_VALID_GT.replace("Expected classification:** UNSOUND",
                                                     "Expected classification:** BROKEN")), False)
    # Check 4: UNCONVENTIONAL with no downgraded code named.
    check("unconventional_no_code", errs_of(_VALID_GT.replace(
        "## GT7 — Distinguish classification *(Q7; §1 Distinguish / Step 9)*\n"
        "- **Expected classification:** UNSOUND\n"
        "- **False-positive trap:** calling it SOUND because it cites evidence.",
        "## GT7 — Distinguish classification *(Q7; §1 Distinguish / Step 9)*\n"
        "- **Expected classification:** UNCONVENTIONAL-BUT-EFFECTIVE\n"
        "- **False-positive trap:** none.")), False)
    # Positive-control GT2 (N/A) is exempt from Check 3.
    check("positive_control_gt2_na", errs_of(_VALID_GT.replace(
        "- **Primary failure layer:** WARRANT\n- **Expected codes:** WR0 (warrant gap) + WR2 (scheme fragility). SM = PASS.",
        "- **N/A — positive control.** No planted failure.")), True)
    # Check 4: the verdict is the leading token — a SOUND key glossed "..., not UNSOUND" must
    # parse as SOUND (clean), and must NOT be misread as UNSOUND off the explanatory token.
    check("gt7_sound_not_unsound", errs_of(_VALID_GT.replace(
        "Expected classification:** UNSOUND",
        "Expected classification:** SOUND — a competent essay, not UNSOUND")), True)
    # Check 4: an out-of-enum verdict followed by a valid token in the gloss is still rejected.
    check("gt7_broken_not_unsound", errs_of(_VALID_GT.replace(
        "Expected classification:** UNSOUND",
        "Expected classification:** BROKEN, not UNSOUND")), False)
    # Check 3: the correct family named only as a negation ("not WR0") must not satisfy a
    # WARRANT locus — the "warrant break mis-coded as support" error must still fire.
    check("gt2_negated_family", errs_of(_VALID_GT.replace(
        "- **Expected codes:** WR0 (warrant gap) + WR2 (scheme fragility). SM = PASS.",
        "- **Expected codes:** SM0 (assertion gap); not WR0.")), False)
    # Check 3: the correct family named only as PASS ("WR0 = PASS") must not satisfy the locus.
    check("gt2_pass_decoy_family", errs_of(_VALID_GT.replace(
        "- **Expected codes:** WR0 (warrant gap) + WR2 (scheme fragility). SM = PASS.",
        "- **Expected codes:** SM0 (assertion gap); WR0 = PASS.")), False)

    print("Self-test: %s" % ("PASS" if rc["v"] == 0 else "FAIL"))
    return rc["v"]


def main(argv):
    if len(argv) < 2:
        sys.stderr.write("Usage: argument_groundtruth.py argument-groundtruth-check <file> | --self-test\n")
        return 2
    if argv[1] == "--self-test":
        return run_self_test()
    if argv[1] == "argument-groundtruth-check":
        if len(argv) < 3:
            sys.stderr.write("Usage: argument_groundtruth.py argument-groundtruth-check <groundtruth_file>\n")
            return 2
        if not os.path.isfile(argv[2]):
            sys.stderr.write("Error: File not found: %s\n" % argv[2])
            return 2
        with open(argv[2], "r", encoding="utf-8", errors="replace") as fh:
            return _emit(*argument_groundtruth_check(fh.read()))
    sys.stderr.write("Error: unknown command: %s\n" % argv[1])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
