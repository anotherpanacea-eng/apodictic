#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mechanical-honesty validator for APODICTIC Argument Benchmark ground-truth files.

Backs `validate.sh argument-groundtruth-check <groundtruth_file>` (docs/argument-benchmark-spec.md
§Mechanical validator). Checks a registered `groundtruth.md` answer key against Argument Benchmark
GT schema v0.3.0:

  1. GT1-GT8 sections are present and non-empty.
  2. Every referenced code resolves to the Dialectical Clarity namespace
     (AT / CL / SM / WR / BP / OB / DI / NE / AC) or a valid FM-A<x> pattern (x in 1-20).
  3. GT2's failure locus is consistent with its codes: a WARRANT locus carries a WR* code, a
     SUPPORT locus an SM*, a BURDEN locus a BP*, an OBJECTION locus an OB*/DI* (the spec's
     example error — diagnosing a warrant break as a support break). Positive-control GT2s
     marked "N/A — positive control" are exempt. (The locus vocabulary in the corpus is richer
     than a fixed enum — SCOPE / CLAIM-LADDER / FORM / QUALIFIER appear — so the check enforces
     code-consistency for the canonical four loci rather than strict enum membership.)
  4. GT7's Warrant verdict is one of WARRANTED / UNCONVENTIONAL-BUT-WARRANTED / UNWARRANTED;
     an UNCONVENTIONAL-BUT-WARRANTED verdict must name >=1 form-dependent code to downgrade to
     advisory. The retired field label (`Expected classification`) and the retired v0.1 tokens
     (SOUND / UNCONVENTIONAL-BUT-EFFECTIVE / UNSOUND) are actively rejected, and a GT7 section
     with no parseable verdict field is an ERROR (not a silent skip).
  5. GT8's Premise-plausibility flags: the `Expected premise flags` value is leading-token parsed
     (NONE_REGISTERED or a P<n> id list; a trailing parenthetical such as
     `(provisional migration default)` is commentary; NONE_REGISTERED can never combine with
     anything else). The expected id list and the flag-detail rows must AGREE both ways
     (NONE_REGISTERED forbids rows; a P-list requires exactly-matching rows). Every detail row is
     strict: exactly 5 `|`-cells (premise | role | flag-type(s) | why flagged | Firewall
     boundary), and each ` + `-joined part of the flag cell must be EXACTLY one of CONTESTABLE /
     UNEARNED / OVERLOADED / EXTERNAL-VERIFY / DEFINITIONAL (full-match; NONE_REGISTERED is
     field-level only). The flag-type cell must not smuggle a truth verdict (a standalone
     uppercase TRUE / FALSE / PROVEN / DISPROVEN / CORRECT / INCORRECT) — the engine flags
     premise acceptability, it never adjudicates premise truth. The `Why flagged` /
     `Firewall boundary` prose cells are exempt (their natural sentence "does not rule the
     premise true or false" is lowercase prose, not a verdict).
  6. GT schema v0.3.0 Reliability ledger: one machine-parsed `- **Reliability:**` line in the
     Provenance block assigning every GT anchor a STATUS
     (authoritative / provisional / panel-licensed / low-agreement) and a DECISION-USE
     (gate / confirm / report). Enforces ledger-internal consistency — the group grammar
     (`GT<a>(–GT<b>)?: <status>, <use>`, `(?![0-9])` boundary-guarded, `|`/`/` copied-guidance
     trap rejected), exactly-GT1-GT8 coverage (no gaps/overlaps), and the enforcement matrix
     (`gate` requires a licensed status — authoritative/panel-licensed; `provisional` may only
     confirm/report; `low-agreement` may only report). A heading marked PROVISIONAL whose ledger
     claims a licensed status is a stale-marker ERROR (the M2-promotion tripwire — this consumes
     the formerly-dead heading `provisional` bool). Inter-rater agreement LICENSES a label; it
     never scores the engine (the psychometric frame).

Output keeps the legacy WARN: / ERROR: / OK: / FAILED: prefixes and exit codes (0 ok, 1 fail,
2 usage) so it slots into --self-test-all alongside the other self-testable validators.

The round-record conformance mode is the one mechanical guard at the run-side attribution seam:
it asserts every booked ENGINE-fault in a calibration-round record cites an anchor whose ledger
licenses that booking (a `gate` anchor licenses any booking; a `confirm` anchor licenses a booking
only with an explicit `OVER-FIRE` tag — the asymmetric ruling; a `report` anchor licenses none).

CLI:
    argument_groundtruth.py argument-groundtruth-check <groundtruth_file>
    argument_groundtruth.py argument-groundtruth-check --round-record <record.md> --fixtures-dir <dir>
    argument_groundtruth.py --self-test
"""

import os
import re
import sys

# Dialectical Clarity code namespace (docs/argument-benchmark-spec.md §Mechanical validator).
_NAMESPACE = {"AT", "CL", "SM", "WR", "BP", "OB", "DI", "NE", "AC"}
# 2-letter prefixes that are NOT codes (ground-truth section labels GT1..GT8).
_NON_CODE_PREFIXES = {"GT"}
_FM_A_MAX = 20  # FM-A20 = Self-Undermining Remedy (Step-6 decoy-resistance pattern)

# Canonical failure loci -> the code family GT2 must carry for that locus.
_LOCUS_FAMILY = {"SUPPORT": ("SM",), "WARRANT": ("WR",), "BURDEN": ("BP",),
                 "OBJECTION": ("OB", "DI")}
# GT7 warrant-verdict enum (GT schema v0.2.0). Membership is exact; the inference axis of
# Wachsmuth cogency (Local Relevance + Local Sufficiency), premise acceptability bracketed.
_GT7_CLASSES = ["UNCONVENTIONAL-BUT-WARRANTED", "UNWARRANTED", "WARRANTED"]
# Retired v0.1 tokens — actively rejected so an unmigrated fixture cannot pass vacuously.
_GT7_LEGACY_CLASSES = {"SOUND", "UNCONVENTIONAL-BUT-EFFECTIVE", "UNSOUND"}
# GT8 premise-plausibility flag types valid in a DETAIL ROW (GT schema v0.2.0). NONE_REGISTERED
# is a FIELD-level sentinel only — it can never combine with another flag and never appears in a
# detail row (a row exists precisely because a flag IS registered).
_GT8_ROW_FLAG_TYPES = {"CONTESTABLE", "UNEARNED", "OVERLOADED", "EXTERNAL-VERIFY", "DEFINITIONAL"}

# Reliability ledger (GT schema v0.3.0). Each GT anchor carries a per-section reliability
# STATUS and a DECISION-USE, encoded as one machine-parsed Reliability line in Provenance.
# Inter-rater agreement LICENSES a label; it never scores the engine (the psychometric frame —
# fiction_groundtruth.py's _RELIABILITY, with a deliberately different, domain-honest token set).
_RELIABILITY_STATUSES = {"authoritative", "provisional", "panel-licensed", "low-agreement"}
# Statuses that MAY back a `gate` decision-use (label-adjudicating; a miss may be booked an
# engine failure). `authoritative` = licensed by construction or by the objective-core
# convention (pre-registered GT1-GT3-grade diagnosis); `panel-licensed` = promoted by measured
# >=3-editor agreement (alpha over threshold). `provisional`/`low-agreement` may never gate.
_LICENSED_STATUSES = {"authoritative", "panel-licensed"}
_DECISION_USES = {"gate", "confirm", "report"}

_CODE_RE = re.compile(r"\b([A-Z]{2})([0-9]+)\b")
_FM_A_RE = re.compile(r"\bFM-A([0-9]+)\b")
_HEADING_RE = re.compile(r"^#{1,4}\s")
_BARE_PREFIX_RE = re.compile(r"\b(?:AT|CL|SM|WR|BP|OB|DI|NE|AC)\b")
# Leading verdict token of a GT7 "Expected warrant verdict" value, skipping markdown emphasis.
# The warrant tokens are all-uppercase with hyphens (no underscores). The trailing lookahead
# requires a token boundary so a near-miss like `WARRANTEDx` cannot truncate-parse as WARRANTED.
_GT7_VERDICT_RE = re.compile(r"[\s*`]*([A-Z][A-Z-]*)(?![A-Za-z0-9])")
# Leading token of a GT8 "Expected premise flags" value — NONE_REGISTERED (underscore) or P<n>;
# a trailing `(provisional migration default)` parenthetical is commentary, not part of the token.
# Boundary lookahead: `P1a` must not truncate-parse as P1.
_GT8_FLAGS_RE = re.compile(r"[\s*`]*([A-Z][A-Z0-9_-]*)(?![A-Za-z0-9])")
# A GT8 premise-flag detail row: `- P1: premise | role | flag-type(s) | why | firewall`.
# Accepts the corpus's bolded-field variants (`- **P1:** …`, `- **P1**: …`) — a bolded id must
# not silently escape row validation. Captures (id, rest).
_GT8_ROW_RE = re.compile(r"^\s*-\s*\**(P[0-9]+)[:*]+\s*(.+)$", re.MULTILINE)
# A truth verdict smuggled into a flag cell: a standalone UPPERCASE token. Case-sensitive on
# purpose — the exempt prose fields say lowercase "true or false", which must NOT trip this.
_TRUTH_TOKEN_RE = re.compile(r"\b(TRUE|FALSE|PROVEN|DISPROVEN|CORRECT|INCORRECT)\b")
# Decoy code mentions that do NOT name the diagnosed family: explicitly negated ("not WR0",
# "not WR0/WR2") or marked passing ("WR0 = PASS", "WR0/WR2 (PASS)"). Masked before the GT2
# locus<->code-family check so a correct family named only to deny it can't satisfy the check.
# Both forms consume a whole grouped code list (slash/comma-separated) so no leading positive
# token survives the mask.
_NEGATED_CODES_RE = re.compile(r"\b[Nn][Oo][Tt]\s+((?:[A-Z]{2}[0-9]+(?:\s*[/,]\s*)?)+)")
_PASS_CODE_RE = re.compile(
    r"\b(?:[A-Z]{2}[0-9]+\s*[/,]\s*)*[A-Z]{2}[0-9]+\s*(?:=\s*PASS\b|\(\s*PASS\s*\))")
# The Reliability ledger field line (in Provenance). Value runs to end of line.
_RELIABILITY_FIELD_RE = re.compile(r"Reliability:\*\*\s*(.+)")
# One ledger group: `GT<a>(–GT<b>)?: <status>, <use>` — full-match per group. Hyphen/en-dash/
# em-dash tolerated in the range (mirrors _gt_numbers_in_heading's `[-–—]` class). `(?![0-9])`
# boundary guards so `GT10` cannot truncate-parse as GT1. Status/use tokens are captured lowercase
# and enum-checked by the caller (so `authoritativex` is captured whole, then rejected).
_RELIABILITY_GROUP_RE = re.compile(
    r"^GT([1-8])(?![0-9])(?:\s*[-–—]\s*GT([1-8])(?![0-9]))?:\s*([a-z][a-z-]*),\s*([a-z]+)$")
# A booked engine-fault line in a calibration-round record (round-record conformance mode). Any
# `- BOOKED:` line is claimed for validation (so a malformed/out-of-range booking is a loud ERROR,
# not a silent skip); lines WITHOUT the prefix stay prose-tolerant and are ignored.
_BOOKED_LINE_RE = re.compile(r"^\s*-\s*BOOKED:\s*(.*?)\s*$", re.MULTILINE)
_BOOKED_BODY_RE = re.compile(r"^ENGINE-FAULT\s+(\S+)\s+GT([0-9]+)(\s+OVER-FIRE)?$")


def _positive_code_text(text):
    """`text` with decoy (negated / PASS-marked) code mentions removed, so only codes asserted
    as the actual diagnosis remain for the GT2 locus<->code-family consistency check."""
    return _PASS_CODE_RE.sub(" ", _NEGATED_CODES_RE.sub(" ", text))


def _gt_numbers_in_heading(line):
    """All GT section numbers a heading covers — corpus fixtures combine sections under one
    heading, e.g. `## GT4–GT8 — *(PROVISIONAL)*` (a range), `## GT7–GT8 — …`, or `## GT5 / GT6`
    (a list)."""
    nums = set()
    # (?![0-9]) — `GT10`/`GT78` in an appendix heading must not read as GT1/GT7 and silently
    # capture (or overwrite) a real section's body.
    for a, b in re.findall(r"GT([1-8])(?![0-9])\s*[-–—]\s*(?:GT\s*)?([1-8])(?![0-9])", line):
        if int(a) <= int(b):
            nums.update(range(int(a), int(b) + 1))
    nums.update(int(n) for n in re.findall(r"GT([1-8])(?![0-9])", line))
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


def _reliability_values(text):
    """All Reliability ledger field values in `text` (one per matching line). Exactly one is
    required; zero or two+ are ERRORs surfaced by the caller."""
    return [m.strip() for m in _RELIABILITY_FIELD_RE.findall(text)]


def _parse_reliability_groups(value):
    """Parse one Reliability ledger value into ({n: (status, use)}, errors). Enforces the group
    grammar, the status/use enums, the `|`/`/` copied-guidance trap, overlap, and the
    gate/confirm/report enforcement matrix — but NOT coverage-completeness or the stale-heading
    cross-check (those need the caller's section context). Shared by Check 6 and the round-record
    conformance mode."""
    mapping, errors = {}, []
    if "|" in value or "/" in value:
        errors.append("Check 6 (reliability) — ledger value contains a '|' or '/' alternation "
                      "(a template guidance line copied verbatim is not a legal value): %r" % value)
        return mapping, errors
    for raw_group in value.split(";"):
        group = raw_group.strip()
        if not group:
            errors.append("Check 6 (reliability) — empty ledger group (stray ';').")
            continue
        gm = _RELIABILITY_GROUP_RE.match(group)
        if not gm:
            errors.append("Check 6 (reliability) — ledger group %r does not match the grammar "
                          "`GT<a>(–GT<b>)?: <status>, <use>`." % group)
            continue
        a, b, status, use = gm.group(1), gm.group(2), gm.group(3), gm.group(4)
        if status not in _RELIABILITY_STATUSES:
            errors.append("Check 6 (reliability) — unknown status %r in group %r (expected one of "
                          "authoritative / provisional / panel-licensed / low-agreement)."
                          % (status, group))
            continue
        if use not in _DECISION_USES:
            errors.append("Check 6 (reliability) — unknown decision-use %r in group %r (expected "
                          "one of gate / confirm / report)." % (use, group))
            continue
        # Enforcement matrix: gate requires a licensed status; provisional may only confirm/report;
        # low-agreement may only report. (Licensed statuses may take any use — a licensed anchor
        # can still be report-only by design, e.g. GT8.)
        if use == "gate" and status not in _LICENSED_STATUSES:
            errors.append("Check 6 (reliability) — group %r uses `gate` but status %r is not "
                          "licensed (gate requires authoritative or panel-licensed)."
                          % (group, status))
        if status == "provisional" and use not in ("confirm", "report"):
            errors.append("Check 6 (reliability) — group %r is `provisional` but its use is %r "
                          "(provisional anchors may only confirm or report)." % (group, use))
        if status == "low-agreement" and use != "report":
            errors.append("Check 6 (reliability) — group %r is `low-agreement` but its use is %r "
                          "(a low-agreement anchor is report-only)." % (group, use))
        lo = int(a)
        hi = int(b) if b else lo
        if hi < lo:
            errors.append("Check 6 (reliability) — group %r has a descending range." % group)
            continue
        for n in range(lo, hi + 1):
            if n in mapping:
                errors.append("Check 6 (reliability) — GT%d is covered by more than one ledger "
                              "group (overlap)." % n)
            mapping[n] = (status, use)
    return mapping, errors


def round_record_check(record_text, resolve_fixture):
    """Round-record conformance: assert every booked ENGINE-fault line cites an anchor whose
    Reliability ledger LICENSES that booking. `resolve_fixture(slug)` returns the fixture's
    groundtruth text, or None if the slug is unknown. A `gate` anchor licenses any ENGINE-fault
    booking; a `confirm` anchor licenses a booking ONLY when it carries the explicit `OVER-FIRE`
    tag (the asymmetric ruling — false negatives on a one-editor label go to KEY-REVIEW, not the
    engine); a `report` anchor licenses none. This is the one mechanical guard at the run-side
    seam; the rest of run adjudication is RUN-PROTOCOL prose."""
    errors = []
    for m in _BOOKED_LINE_RE.finditer(record_text):
        body = m.group(1).strip()
        bm = _BOOKED_BODY_RE.match(body)
        if not bm:
            errors.append("round-record — malformed BOOKED line %r (expected "
                          "`ENGINE-FAULT <fixture-slug> GT<n>[ OVER-FIRE]`)." % body)
            continue
        slug, n_str, overfire = bm.group(1), bm.group(2), bool(bm.group(3))
        n = int(n_str)
        if not (1 <= n <= 8):
            errors.append("round-record — booking on %s cites GT%d, out of range (GT1-GT8)."
                          % (slug, n))
            continue
        gt_text = resolve_fixture(slug)
        if gt_text is None:
            errors.append("round-record — booked fixture %r not found in the fixtures dir." % slug)
            continue
        values = _reliability_values(gt_text)
        if len(values) != 1:
            errors.append("round-record — fixture %r carries %d Reliability ledgers (need exactly "
                          "one) — cannot adjudicate its bookings." % (slug, len(values)))
            continue
        mapping, gerrs = _parse_reliability_groups(values[0])
        if gerrs:
            errors.append("round-record — fixture %r has an unparseable Reliability ledger; run "
                          "argument-groundtruth-check on it first." % slug)
            continue
        if n not in mapping:
            errors.append("round-record — booking on %s cites GT%d, which its Reliability ledger "
                          "does not cover." % (slug, n))
            continue
        status, use = mapping[n]
        if use == "gate":
            continue  # licensed for any ENGINE-fault booking
        if use == "confirm":
            if overfire:
                continue  # asymmetric ruling: an over-fire licenses a confirm-anchor booking
            errors.append("round-record — %s GT%d is `confirm`; an ENGINE-FAULT booking WITHOUT "
                          "the OVER-FIRE tag is unlicensed (a false-negative miss on a one-editor "
                          "label routes to KEY-REVIEW, not an engine regression)." % (slug, n))
            continue
        errors.append("round-record — %s GT%d is `%s`; it licenses no ENGINE-FAULT booking."
                      % (slug, n, use))
    return errors


def argument_groundtruth_check(text):
    errors, warnings = [], []
    sections = _parse_gt_sections(text)

    # Check 1: GT1-GT8 each covered by a heading (combined headings OK) + non-empty.
    for n in range(1, 9):
        sec = sections.get(n)
        if sec is None:
            errors.append("Check 1 (sections) — GT%d not covered by any heading." % n)
        elif not sec["body"].strip():
            errors.append("Check 1 (sections) — GT%d section is empty." % n)

    # Check 2: every code resolves to the namespace or FM-A<1..20>.
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

    # Check 4: GT7 Warrant verdict. A GT7 section present but with no parseable verdict field is
    # an ERROR (not a silent skip); the retired field label + retired v0.1 tokens are rejected.
    gt7 = sections.get(7, {}).get("body", "")
    if gt7:
        if re.search(r"Expected classification:\*\*", gt7):
            errors.append("Check 4 (GT7) — uses the retired field label 'Expected classification' "
                          "(GT schema <v0.2.0); rename to 'Expected warrant verdict'.")
        # Reject residue of ALL THREE retired v0.1 GT7 encodings, not just the standalone field
        # label: the combined-block sub-line (`- **GT7 Distinguish:** …`) and the inline variant
        # (`… — expected classification: …`) must not survive beside a migrated field, or an
        # unmigrated encoding can pass clean next to a pasted-in new field.
        if re.search(r"GT7 Distinguish", gt7) or re.search(r"[Ee]xpected classification", gt7):
            errors.append("Check 4 (GT7) — retired v0.1 GT7 encoding residue ('GT7 Distinguish' "
                          "or 'expected classification') survives in the GT7 body; migrate the "
                          "whole section to the 'Expected warrant verdict' field.")
        m = re.search(r"Expected warrant verdict:\*\*\s*(.+)", gt7)
        if not m:
            errors.append("Check 4 (GT7) — GT7 section present but no parseable "
                          "'Expected warrant verdict:' field.")
        else:
            cls_line = m.group(1)
            # The verdict is the field value at the *start* of the line; a trailing parenthetical,
            # dash-set-off rationale, or "..., not UNWARRANTED" gloss is commentary. The leading
            # token is enum-gated, which is strictly stronger than the standalone-truth-token guard
            # (a TRUE/FALSE verdict here is already out-of-enum), so no separate truth check is
            # needed on GT7; the explicit truth-token scan guards the GT8 free-text flag cell.
            vm = _GT7_VERDICT_RE.match(cls_line)
            verdict = vm.group(1) if vm else ""
            if verdict in _GT7_LEGACY_CLASSES:
                errors.append("Check 4 (GT7) — retired v0.1 verdict token %r (SOUND / "
                              "UNCONVENTIONAL-BUT-EFFECTIVE / UNSOUND); migrate to WARRANTED / "
                              "UNCONVENTIONAL-BUT-WARRANTED / UNWARRANTED." % verdict)
            elif verdict not in _GT7_CLASSES:
                errors.append("Check 4 (GT7) — warrant verdict is not one of WARRANTED / "
                              "UNCONVENTIONAL-BUT-WARRANTED / UNWARRANTED (got %r)." % cls_line.strip())
            elif verdict == "UNCONVENTIONAL-BUT-WARRANTED":
                # Must identify the form-dependent codes to downgrade — specific (SM0 / FM-A1) or
                # family-level ("DI codes", "SM/WR on the cost accounting") references both count.
                if not (_codes_in(gt7) or _FM_A_RE.search(gt7) or _BARE_PREFIX_RE.search(gt7)):
                    errors.append("Check 4 (GT7) — UNCONVENTIONAL-BUT-WARRANTED must name >=1 "
                                  "form-dependent code to downgrade to advisory, but GT7 names none.")

    # Check 5: GT8 Premise-plausibility flags (GT schema v0.2.0). Leading-token parse of the
    # `Expected premise flags` value (NONE_REGISTERED or a P<n> id list; a trailing parenthetical
    # such as `(provisional migration default)` is commentary). The expected id list and the
    # flag-detail rows must AGREE — a registered path nothing cross-checks is a vacuous firewall.
    # Every detail row is strict: exactly 5 `|`-cells, each ` + `-part of the flag cell EXACTLY an
    # enum token (full-match — no parentheticals, no prose, no no-space joiner), and no truth
    # verdict smuggled into the flag column.
    gt8 = sections.get(8, {}).get("body", "")
    if gt8:
        expected_ids, none_registered = [], False
        fm = re.search(r"Expected premise flags:\*\*\s*(.+)", gt8)
        if not fm:
            errors.append("Check 5 (GT8) — GT8 section present but no parseable "
                          "'Expected premise flags:' field.")
        else:
            raw = fm.group(1).strip()
            if "|" in raw:
                errors.append("Check 5 (GT8) — 'Expected premise flags' value contains a '|' "
                              "alternation (a template guidance line copied verbatim is not a "
                              "legal value).")
            else:
                lead_m = _GT8_FLAGS_RE.match(raw)
                lead = lead_m.group(1) if lead_m else ""
                # Commentary is a trailing parenthetical; the value proper precedes it.
                value = raw.split("(", 1)[0].strip().rstrip("*` ")
                if lead == "NONE_REGISTERED":
                    none_registered = True
                    if value.strip("*` ") != "NONE_REGISTERED":
                        errors.append("Check 5 (GT8) — NONE_REGISTERED cannot combine with any "
                                      "other flag or id (got %r)." % raw)
                elif re.match(r"P[0-9]+$", lead):
                    expected_ids = re.findall(r"\bP[0-9]+\b", value)
                    leftover = re.sub(r"\bP[0-9]+\b", "", value).strip("*` ,;…")
                    if leftover:
                        errors.append("Check 5 (GT8) — 'Expected premise flags' P-id list carries "
                                      "unexpected content %r." % leftover)
                else:
                    errors.append("Check 5 (GT8) — 'Expected premise flags' leading token must be "
                                  "NONE_REGISTERED or P<n> (got %r)." % raw)
        rows = _GT8_ROW_RE.findall(gt8)
        row_ids = [rid for rid, _ in rows]
        # Field <-> detail-row agreement (both directions).
        if none_registered and rows:
            errors.append("Check 5 (GT8) — expected NONE_REGISTERED but %d flag-detail row(s) "
                          "are registered (%s)." % (len(rows), ", ".join(row_ids)))
        if expected_ids and sorted(set(row_ids)) != sorted(set(expected_ids)):
            errors.append("Check 5 (GT8) — expected flag ids %s do not match detail-row ids %s."
                          % (", ".join(expected_ids), ", ".join(row_ids) if row_ids else "(none)"))
        for rid, row in rows:
            cells = [c.strip() for c in row.split("|")]
            if len(cells) != 5:
                errors.append("Check 5 (GT8) — %s detail row must have exactly 5 '|'-cells "
                              "(premise | role | flag-type(s) | why flagged | Firewall boundary); "
                              "got %d. A '|' inside the premise text must be reworded — cell "
                              "shifting would let a flag escape validation." % (rid, len(cells)))
                continue
            flag_cell = cells[2]
            tt = _TRUTH_TOKEN_RE.search(flag_cell)
            if tt:
                errors.append("Check 5 (GT8) — flag-type cell smuggles a truth verdict %r; the "
                              "engine flags acceptability, it does not adjudicate premise truth."
                              % tt.group(1))
                continue
            for part in flag_cell.split(" + "):
                tok = part.strip().strip("*`")
                if tok not in _GT8_ROW_FLAG_TYPES:
                    errors.append("Check 5 (GT8) — flag-type cell part %r is not exactly one of "
                                  "CONTESTABLE / UNEARNED / OVERLOADED / EXTERNAL-VERIFY / "
                                  "DEFINITIONAL (join multiple flags with ' + '; NONE_REGISTERED "
                                  "is field-level only and never appears in a detail row)."
                                  % part.strip())

    # Check 6: Reliability ledger (GT schema v0.3.0). One machine-parsed ledger line in Provenance
    # (full-text posture — the ledger lives outside the GT sections _parse_gt_sections captures,
    # same as Check 2 at the code scan). Enforces ledger-internal consistency: the group grammar,
    # the status/use enums, the gate/confirm/report enforcement matrix, exact GT1-GT8 coverage
    # (no gaps, no overlaps), and the stale-heading cross-check that consumes the (formerly dead)
    # `sections[n]["provisional"]` bool. Run-side adjudication is RUN-PROTOCOL prose, with the
    # round-record conformance mode as its one mechanical guard (see round_record_check).
    values = _reliability_values(text)
    if not values:
        errors.append("Check 6 (reliability) — no Reliability ledger line "
                      "(`- **Reliability:** GT1–GT3: authoritative, gate; …`); GT schema v0.3.0 "
                      "requires one in the Provenance block.")
    elif len(values) > 1:
        errors.append("Check 6 (reliability) — %d Reliability ledger lines found; exactly one is "
                      "allowed." % len(values))
    else:
        mapping, rel_errors = _parse_reliability_groups(values[0])
        errors.extend(rel_errors)
        covered = set(mapping)
        missing = [n for n in range(1, 9) if n not in covered]
        if missing:
            errors.append("Check 6 (reliability) — ledger coverage is incomplete; GT%s "
                          "not covered (coverage must be exactly GT1-GT8)."
                          % ", GT".join(str(n) for n in missing))
        # Stale-heading cross-check (makes the dead `provisional` bool live): a heading marked
        # PROVISIONAL whose ledger claims a licensed status is a stale marker — promotion must
        # clean the heading or the ledger is wrong. One-way by design: a `provisional` ledger
        # status does NOT require a heading marker (the marker is optional human emphasis).
        for n, (status, _use) in mapping.items():
            sec = sections.get(n)
            if sec and sec.get("provisional") and status not in ("provisional", "low-agreement"):
                errors.append("Check 6 (reliability) — GT%d's heading is marked PROVISIONAL but "
                              "its ledger status is %r (a licensed status under a PROVISIONAL "
                              "heading is a stale marker — promotion must clean the heading, or "
                              "the ledger is wrong)." % (n, status))

    ok = "OK: Argument ground-truth contract satisfied (GT1-GT8 present; codes resolve; locus consistent; warrant verdict + premise flags well-formed; reliability ledger licensed)."
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
- **Reliability:** GT1–GT7: authoritative, gate; GT8: authoritative, report

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

## GT7 — Warrant verdict *(Q7; §1 Distinguish / Step 9)*
- **Expected warrant verdict:** UNWARRANTED
- **False-positive trap:** calling it WARRANTED because it cites evidence.

## GT8 — Premise-plausibility flags
- **Expected premise flags:** NONE_REGISTERED
- **Must not adjudicate:** whether the underlying empirical claim is true.

## Notes
free-form.
"""

# GT7 = WARRANTED coexisting with a registered, two-flag GT8 premise flag — the classic
# valid-inference / contestable-premise boundary case. The Firewall-boundary cell deliberately
# says lowercase "true or false" (legitimate prose) and MUST still pass the truth-token check.
_MOON_CHEESE_GT = _VALID_GT.replace(
    "- **Expected warrant verdict:** UNWARRANTED\n"
    "- **False-positive trap:** calling it WARRANTED because it cites evidence.",
    "- **Expected warrant verdict:** WARRANTED\n"
    "- **False-positive trap:** calling it UNWARRANTED merely because a premise is flagged."
).replace(
    "- **Expected premise flags:** NONE_REGISTERED\n"
    "- **Must not adjudicate:** whether the underlying empirical claim is true.",
    "- **Expected premise flags:** P1\n"
    "- **Flag details:**\n"
    "  - P1: \"the moon is made of cheese\" | ground | CONTESTABLE + EXTERNAL-VERIFY "
    "| a careful reviewer would not let the composition claim pass silently "
    "| The engine flags the premise as contestable and load-bearing; it does not rule the premise true or false.\n"
    "- **Must not adjudicate:** lunar composition."
)

# A combined GT4–GT8 provisional block using the canonical `Expected warrant verdict` /
# `Expected premise flags` field labels the renamed parser matcher reads.
_COMBINED_GT = """# Ground Truth: self-test combined

## Provenance
- **Fixture slug:** self-test-combined
- **Reliability:** GT1–GT3: authoritative, gate; GT4–GT7: provisional, confirm; GT8: provisional, report

## GT1 — Main claim *(Q1; §2 C0)*
- **Expected C0:** "X should do Y."

## GT2 — Failure locus *(Q2; §3 Support vs §4 Warrant)*
- **N/A — positive control.** No planted failure.

## GT3 — Strongest real objection *(Q3; §6)*
- **Expected OB / DI codes:** OB3.

## GT4–GT8 — *(PROVISIONAL)*
- **GT4 Audience profile:** Expertise GENERAL · Receptivity MIXED · Consequence MEDIUM (AC1).
- **GT5 Pre-registered vulnerabilities:** no denominator.
- **GT6 Correct first repair target:** warrant.
- **Expected warrant verdict:** WARRANTED — a competent piece; the soft spot is Should-Fix.
- **False-positive trap:** over-pathologizing a competent piece.
- **Expected premise flags:** NONE_REGISTERED (provisional migration default)
- **Must not adjudicate:** whether the framing assumption holds.

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
    # Check 4: GT7 warrant verdict not one of the three.
    check("bad_gt7_class", errs_of(_VALID_GT.replace("Expected warrant verdict:** UNWARRANTED",
                                                     "Expected warrant verdict:** BROKEN")), False)
    # Check 4: UNCONVENTIONAL-BUT-WARRANTED with no downgraded code named.
    check("unconventional_no_code", errs_of(_VALID_GT.replace(
        "## GT7 — Warrant verdict *(Q7; §1 Distinguish / Step 9)*\n"
        "- **Expected warrant verdict:** UNWARRANTED\n"
        "- **False-positive trap:** calling it WARRANTED because it cites evidence.",
        "## GT7 — Warrant verdict *(Q7; §1 Distinguish / Step 9)*\n"
        "- **Expected warrant verdict:** UNCONVENTIONAL-BUT-WARRANTED\n"
        "- **False-positive trap:** none.")), False)
    # Positive-control GT2 (N/A) is exempt from Check 3.
    check("positive_control_gt2_na", errs_of(_VALID_GT.replace(
        "- **Primary failure layer:** WARRANT\n- **Expected codes:** WR0 (warrant gap) + WR2 (scheme fragility). SM = PASS.",
        "- **N/A — positive control.** No planted failure.")), True)
    # Check 4: the verdict is the leading token — a WARRANTED key glossed "..., not UNWARRANTED"
    # must parse as WARRANTED (clean), and must NOT be misread as UNWARRANTED off the gloss.
    check("gt7_warranted_not_unwarranted", errs_of(_VALID_GT.replace(
        "Expected warrant verdict:** UNWARRANTED\n"
        "- **False-positive trap:** calling it WARRANTED because it cites evidence.",
        "Expected warrant verdict:** WARRANTED — a competent essay, not UNWARRANTED\n"
        "- **False-positive trap:** none.")), True)
    # Check 4: an out-of-enum verdict followed by a valid token in the gloss is still rejected.
    check("gt7_broken_not_unwarranted", errs_of(_VALID_GT.replace(
        "Expected warrant verdict:** UNWARRANTED",
        "Expected warrant verdict:** BROKEN, not UNWARRANTED")), False)
    # Check 4: the retired FIELD LABEL is rejected even when the token is a valid new one.
    check("gt7_old_field_label", errs_of(_VALID_GT.replace(
        "- **Expected warrant verdict:** UNWARRANTED",
        "- **Expected classification:** UNWARRANTED")), False)
    # Check 4: a retired v0.1 TOKEN is rejected even under the new field label.
    check("gt7_old_token", errs_of(_VALID_GT.replace(
        "Expected warrant verdict:** UNWARRANTED", "Expected warrant verdict:** UNSOUND")), False)
    # Check 4: a GT7 section present but stripped of its verdict field is an ERROR, not a skip.
    check("gt7_missing_field", errs_of(_VALID_GT.replace(
        "- **Expected warrant verdict:** UNWARRANTED\n", "")), False)
    # Check 5: GT8 with NONE_REGISTERED (provisional migration default) is accepted.
    check("gt8_provisional_default", errs_of(_VALID_GT.replace(
        "- **Expected premise flags:** NONE_REGISTERED",
        "- **Expected premise flags:** NONE_REGISTERED (provisional migration default)")), True)
    # Check 5: a missing GT8 section is rejected.
    check("gt8_missing_section", errs_of(_VALID_GT.replace(
        "## GT8 — Premise-plausibility flags\n"
        "- **Expected premise flags:** NONE_REGISTERED\n"
        "- **Must not adjudicate:** whether the underlying empirical claim is true.\n", "")), False)
    # Check 5: a GT8 section present but with no premise-flags field is rejected.
    check("gt8_missing_field", errs_of(_VALID_GT.replace(
        "- **Expected premise flags:** NONE_REGISTERED\n", "")), False)
    # Check 5: a malformed premise flag type is rejected.
    check("gt8_bad_flag_type", errs_of(_MOON_CHEESE_GT.replace(
        "CONTESTABLE + EXTERNAL-VERIFY", "CONTESTABLE + NONSENSE-FLAG")), False)
    # Check 5: a truth verdict smuggled into the flag cell is rejected (field-scoped,
    # case-sensitive) — even as a parenthetical the enum check alone would miss.
    check("gt8_truth_token_in_flag", errs_of(_MOON_CHEESE_GT.replace(
        "CONTESTABLE + EXTERNAL-VERIFY", "CONTESTABLE (FALSE)")), False)
    # Check 5 + Check 4: the moon-cheese WARRANTED + P1 two-flag row is accepted, AND its
    # Firewall-boundary sentence contains lowercase "true or false" without tripping the check.
    check("moon_cheese_warranted_p1", errs_of(_MOON_CHEESE_GT), True)
    # Check 1/4/5: a combined GT4–GT8 provisional heading covers GT4-GT8 and is accepted.
    check("combined_gt4_gt8_heading", errs_of(_COMBINED_GT), True)
    # Check 4: a near-miss verdict token must not truncate-parse as a valid one.
    check("gt7_token_boundary", errs_of(_VALID_GT.replace(
        "Expected warrant verdict:** UNWARRANTED", "Expected warrant verdict:** UNWARRANTEDx")), False)
    # Check 4: combined-block legacy residue (`GT7 Distinguish:`) beside a migrated field.
    check("gt7_legacy_distinguish_residue", errs_of(_VALID_GT.replace(
        "- **False-positive trap:** calling it WARRANTED because it cites evidence.",
        "- **False-positive trap:** calling it WARRANTED because it cites evidence.\n"
        "- **GT7 Distinguish:** UNWARRANTED — leftover of the old combined encoding.")), False)
    # Check 4: inline legacy residue (lowercase `expected classification`) beside a migrated field.
    check("gt7_legacy_inline_residue", errs_of(_VALID_GT.replace(
        "- **False-positive trap:** calling it WARRANTED because it cites evidence.",
        "- **False-positive trap:** calling it WARRANTED because it cites evidence.\n"
        "- **GT7 Distinguish — expected classification: UNWARRANTED**")), False)
    # Check 5: a near-miss premise id must not truncate-parse (`P1a` is not P1).
    check("gt8_lead_boundary", errs_of(_VALID_GT.replace(
        "Expected premise flags:** NONE_REGISTERED", "Expected premise flags:** P1a")), False)
    # Check 5: NONE_REGISTERED can never combine with another flag.
    check("gt8_none_registered_combined", errs_of(_VALID_GT.replace(
        "Expected premise flags:** NONE_REGISTERED",
        "Expected premise flags:** NONE_REGISTERED + CONTESTABLE")), False)
    # Check 5: the template's guidance line copied verbatim (contains `|`) is not a legal value.
    check("gt8_template_guidance_copied", errs_of(_VALID_GT.replace(
        "Expected premise flags:** NONE_REGISTERED",
        "Expected premise flags:** NONE_REGISTERED | P1, P2, ...")), False)
    # Check 5: an expected P-id with ZERO detail rows is a vacuous registration — rejected.
    check("gt8_expected_p1_no_rows", errs_of(_VALID_GT.replace(
        "Expected premise flags:** NONE_REGISTERED", "Expected premise flags:** P1")), False)
    # Check 5: NONE_REGISTERED with a registered detail row — field/rows disagreement.
    check("gt8_row_under_none_registered", errs_of(_VALID_GT.replace(
        "- **Must not adjudicate:** whether the underlying empirical claim is true.",
        "- **Flag details:**\n"
        "  - P1: \"a premise\" | ground | CONTESTABLE | why | The engine does not adjudicate.\n"
        "- **Must not adjudicate:** whether the underlying empirical claim is true.")), False)
    # Check 5: expected ids and row ids must match exactly (P1 expected, P2 registered).
    check("gt8_row_id_mismatch", errs_of(_MOON_CHEESE_GT.replace(
        "  - P1: \"the moon is made of cheese\"", "  - P2: \"the moon is made of cheese\"")), False)
    # Check 5: a BOLDED row id (`- **P1:** …`) is validated, not silently skipped — the same
    # moon-cheese row bolded must still be accepted (and thus enum/truth-checked).
    check("gt8_bold_row_id", errs_of(_MOON_CHEESE_GT.replace(
        "  - P1: \"the moon is made of cheese\"",
        "  - **P1:** \"the moon is made of cheese\"")), True)
    # Check 5: a `|` inside the premise text shifts cells — must fail the 5-cell contract, not
    # let the shifted flag cell escape validation.
    check("gt8_pipe_in_premise", errs_of(_MOON_CHEESE_GT.replace(
        "\"the moon is made of cheese\"", "\"the moon | is made of cheese\"")), False)
    # Check 5: a 3-cell row (missing why-flagged + Firewall boundary) is rejected.
    check("gt8_three_cell_row", errs_of(_MOON_CHEESE_GT.replace(
        "  - P1: \"the moon is made of cheese\" | ground | CONTESTABLE + EXTERNAL-VERIFY "
        "| a careful reviewer would not let the composition claim pass silently "
        "| The engine flags the premise as contestable and load-bearing; it does not rule the premise true or false.",
        "  - P1: \"the moon is made of cheese\" | ground | CONTESTABLE + EXTERNAL-VERIFY")), False)
    # Check 5: the no-space joiner must not smuggle a bogus flag past the full-match.
    check("gt8_nospace_plus", errs_of(_MOON_CHEESE_GT.replace(
        "CONTESTABLE + EXTERNAL-VERIFY", "CONTESTABLE+NONSENSE-FLAG")), False)
    # Check 5: a mixed-case truth verdict in a parenthetical is caught by the full-match (the
    # uppercase-only truth-token scan is deliberately narrow; the enum full-match backstops it).
    check("gt8_mixedcase_truth_parenthetical", errs_of(_MOON_CHEESE_GT.replace(
        "CONTESTABLE + EXTERNAL-VERIFY", "CONTESTABLE (False)")), False)
    # Check 5: prose adjudication inside the flag cell is rejected by the full-match.
    check("gt8_prose_in_flag_cell", errs_of(_MOON_CHEESE_GT.replace(
        "CONTESTABLE + EXTERNAL-VERIFY",
        "CONTESTABLE and frankly the premise is false")), False)
    # Check 1: a large-numbered appendix heading (`GT78`) must not read as GT7/GT8 and must not
    # capture or overwrite a real section's body — the file stays clean.
    check("gt_heading_large_number", errs_of(_VALID_GT.replace(
        "## Notes", "## GT78 appendix\nfree-form appendix prose.\n\n## Notes")), True)

    # ---- Check 6: Reliability ledger (GT schema v0.3.0). The `valid`/`combined_gt4_gt8_heading`
    # arms already exercise the clean paths (_VALID_GT + _COMBINED_GT now carry ledgers); below,
    # each failing branch gets an arm, plus the two clean-but-suspicious paths.
    _VG_LEDGER = "- **Reliability:** GT1–GT7: authoritative, gate; GT8: authoritative, report"
    # No ledger at all → ERROR (v0.3.0 requires one).
    check("reliability_missing", errs_of(_VALID_GT.replace(_VG_LEDGER + "\n", "")), False)
    # Two ledgers → ERROR (exactly one allowed).
    check("reliability_duplicate", errs_of(_VALID_GT.replace(
        _VG_LEDGER + "\n",
        _VG_LEDGER + "\n- **Reliability:** GT1–GT8: authoritative, report\n")), False)
    # Coverage gap: GT4 absent.
    check("reliability_coverage_gap", errs_of(_VALID_GT.replace(
        "GT1–GT7: authoritative, gate",
        "GT1–GT3: authoritative, gate; GT5–GT7: authoritative, gate")), False)
    # Overlap: GT3 covered by two groups.
    check("reliability_overlap", errs_of(_VALID_GT.replace(
        "GT1–GT7: authoritative, gate",
        "GT1–GT3: authoritative, gate; GT3–GT7: authoritative, gate")), False)
    # Unknown status token.
    check("reliability_bad_status", errs_of(_VALID_GT.replace(
        "GT1–GT7: authoritative, gate", "GT1–GT7: wobbly, gate")), False)
    # Unknown decision-use token.
    check("reliability_bad_use", errs_of(_VALID_GT.replace(
        "GT8: authoritative, report", "GT8: authoritative, broadcast")), False)
    # The core licensing refusal: `gate` on a `provisional` status.
    check("reliability_gate_on_provisional", errs_of(_COMBINED_GT.replace(
        "GT4–GT7: provisional, confirm", "GT4–GT7: provisional, gate")), False)
    # `confirm` on a `low-agreement` status (low-agreement is report-only).
    check("reliability_confirm_on_low_agreement", errs_of(_COMBINED_GT.replace(
        "GT8: provisional, report", "GT8: low-agreement, confirm")), False)
    # Clean: `low-agreement, report` is the allowed report-only path.
    check("reliability_low_agreement_report", errs_of(_COMBINED_GT.replace(
        "GT8: provisional, report", "GT8: low-agreement, report")), True)
    # Clean: the promotion path — `panel-licensed` may gate (under non-provisional headings).
    check("reliability_panel_licensed_gate", errs_of(_VALID_GT.replace(
        "GT1–GT7: authoritative, gate", "GT1–GT7: panel-licensed, gate")), True)
    # Stale heading marker: a licensed status under a PROVISIONAL-marked heading (the promotion
    # tripwire) — _COMBINED_GT's GT4–GT7 sits under `## GT4–GT8 — *(PROVISIONAL)*`.
    check("reliability_stale_heading_marker", errs_of(_COMBINED_GT.replace(
        "GT4–GT7: provisional, confirm", "GT4–GT7: authoritative, gate")), False)
    # Copied template guidance: a `|` alternation in the value is not a legal ledger.
    check("reliability_template_guidance_copied", errs_of(_VALID_GT.replace(
        "GT1–GT7: authoritative, gate", "GT1–GT7: authoritative | provisional, gate")), False)
    # Token boundary: `GT1–GT10` must not truncate-parse as GT1.
    check("reliability_token_boundary", errs_of(_VALID_GT.replace(
        "GT1–GT7: authoritative, gate", "GT1–GT10: authoritative, gate")), False)

    # ---- Round-record conformance mode (the one mechanical guard on run-side attribution).
    # Hermetic in-memory fixtures — round_record_check only reads each fixture's Reliability ledger.
    _RR_FIXTURES = {
        "gate-fix": "## Provenance\n- **Reliability:** GT1–GT7: authoritative, gate; "
                    "GT8: authoritative, report\n",
        "confirm-fix": "## Provenance\n- **Reliability:** GT1–GT3: authoritative, gate; "
                       "GT4–GT7: provisional, confirm; GT8: provisional, report\n",
    }
    _rr = lambda slug: _RR_FIXTURES.get(slug)
    # An ENGINE-FAULT booked on a `gate` anchor is licensed → clean.
    check("roundrec_gate_booking",
          round_record_check("- BOOKED: ENGINE-FAULT gate-fix GT2\n", _rr), True)
    # Booked on a `confirm` anchor WITHOUT the OVER-FIRE tag → FAIL (the guard's core refusal).
    check("roundrec_confirm_unmarked",
          round_record_check("- BOOKED: ENGINE-FAULT confirm-fix GT7\n", _rr), False)
    # Booked on a `confirm` anchor WITH OVER-FIRE → clean (the asymmetric ruling).
    check("roundrec_confirm_overfire",
          round_record_check("- BOOKED: ENGINE-FAULT confirm-fix GT7 OVER-FIRE\n", _rr), True)
    # Booked on a `report` anchor → FAIL (a report anchor licenses no booking).
    check("roundrec_report_anchor",
          round_record_check("- BOOKED: ENGINE-FAULT confirm-fix GT8\n", _rr), False)
    # An unknown fixture slug → FAIL.
    check("roundrec_unknown_fixture",
          round_record_check("- BOOKED: ENGINE-FAULT nonexistent-fix GT2\n", _rr), False)
    # Prose-tolerance: a record with no BOOKED lines is vacuously clean (today's calibration doc).
    check("roundrec_prose_ignored",
          round_record_check("The engine over-fired on some fixture; see notes.\n- a bullet\n", _rr),
          True)
    # A BOOKED line that is out of GT range is a loud ERROR, not a silent skip.
    check("roundrec_out_of_range",
          round_record_check("- BOOKED: ENGINE-FAULT gate-fix GT9\n", _rr), False)

    print("Self-test: %s" % ("PASS" if rc["v"] == 0 else "FAIL"))
    return rc["v"]


def main(argv):
    if len(argv) < 2:
        sys.stderr.write("Usage: argument_groundtruth.py argument-groundtruth-check <file> | --self-test\n")
        return 2
    if argv[1] == "--self-test":
        return run_self_test()
    if argv[1] == "argument-groundtruth-check":
        # Round-record conformance mode: --round-record <record.md> --fixtures-dir <dir>.
        if len(argv) >= 3 and argv[2] == "--round-record":
            return _run_round_record(argv[2:])
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


def _run_round_record(args):
    """CLI wrapper for the round-record conformance mode. `args` starts at `--round-record`."""
    record_path, fixtures_dir = None, None
    i = 0
    while i < len(args):
        if args[i] == "--round-record" and i + 1 < len(args):
            record_path = args[i + 1]; i += 2; continue
        if args[i] == "--fixtures-dir" and i + 1 < len(args):
            fixtures_dir = args[i + 1]; i += 2; continue
        sys.stderr.write("Usage: argument_groundtruth.py argument-groundtruth-check "
                         "--round-record <record.md> --fixtures-dir <dir>\n")
        return 2
    if not record_path or not fixtures_dir:
        sys.stderr.write("Usage: argument_groundtruth.py argument-groundtruth-check "
                         "--round-record <record.md> --fixtures-dir <dir>\n")
        return 2
    if not os.path.isfile(record_path):
        sys.stderr.write("Error: round record not found: %s\n" % record_path)
        return 2
    if not os.path.isdir(fixtures_dir):
        sys.stderr.write("Error: fixtures dir not found: %s\n" % fixtures_dir)
        return 2

    def resolve(slug):
        path = os.path.join(fixtures_dir, slug, "groundtruth.md")
        if not os.path.isfile(path):
            return None
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()

    with open(record_path, "r", encoding="utf-8", errors="replace") as fh:
        errors = round_record_check(fh.read(), resolve)
    for e in errors:
        print(e)
    if errors:
        print("")
        print("FAILED: %d round-record conformance failure(s). A booked ENGINE-fault must cite an "
              "anchor whose Reliability ledger licenses it (gate: any; confirm: OVER-FIRE only; "
              "report: none)." % len(errors))
        return 1
    print("OK: round-record conformance satisfied (every booked ENGINE-fault is ledger-licensed).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
