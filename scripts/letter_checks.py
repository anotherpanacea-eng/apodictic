#!/usr/bin/env python3
"""Shared parsers + checks for APODICTIC editorial-letter / ledger validators.

Backs validate.sh's prose-validator arms with a real parser and token-boundary
matching, replacing brittle shell regex (the recurring source of severity-label /
prefix evidence-ref / calibration-line edge-case findings). validate.sh stays the
command surface and degrades to its prior bash path when python3 is absent.

Ported arms (Validator Architecture Hardening, incremental):
  - severity-floor, decision-layer-check, audit-signal-propagation,
    underdiagnosis-triggers, ledger-consolidation, author-facing-lint
  - synthesis-sections, tone-check, ledger-check (Increment 8 — the remaining
    editorial-letter / ledger prose arms, previously bash-regex): heading-anchored
    section matching (kills mid-heading mentions), body-only + code-span-stripped +
    blockquote-skipped tone scanning, and anchored per-pass ledger subsections.
    ledger-check returns (rc, lines) directly (NOTE + no-passes WARNING) via RAW_CHECKS.

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
  letter_checks.py synthesis-sections <letter_file>
  letter_checks.py tone-check <letter_file>
  letter_checks.py ledger-check <ledger_file>
  letter_checks.py --self-test [<check-name>]
"""

import glob
import os
import re
import sys

from override_marker import has_override, override_slugs, strip_code_spans

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


# `has_override` (and `override_slugs`, for the data-driven per-audit slug) come from the shared
# `override_marker` module — boundary-matched + code-spans stripped, so a suffixed slug or a
# backtick'd documentation example is NOT honored (the 2026-06-20 override-substring class, gated by
# meta_lint.py's M5). Imported above; the legacy bare-substring definition is retired.


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


# --------------------------------------------------------------------------
# audit-signal-propagation — Canonical Audit-Signal Propagation Rule.
# Canonical homes: run-synthesis.md §Step 2; per-audit table pass-dependencies.md §4e.
# Faithful port of the bash arm (per-audit appendix-subsection detection; name-match
# OR shared-evidence-line propagation; per-class + per-audit override markers; legacy
# whole-letter fallback when no audit appendix is present).
#
# §4e-SOURCE-OF-TRUTH mapping (2026-07-04). The signal-class → synthesis-severity
# mapping the validator enforces is no longer hardcoded here: it is READ from the
# `#### Default mapping (fallback for un-enumerated audits)` block of
# pass-dependencies.md §4e (the "Column contract" the §4e prose formalizes). A §4e
# per-audit row may additionally reassign the required severity for its own signal
# class via a machine-parseable directive in the Override column
# (`propagate-override: <signal-class> → <synthesis-severity>`); such a directive is
# honored for that audit's slug. On the real committed §4e the Default mapping block
# reproduces the historical hardcode exactly and no row carries an override directive,
# so the port is oracle-identical. A malformed §4e mapping (unrecognized synthesis
# severity, a missing required signal class, or a malformed override directive) is
# surfaced as an ERROR rather than silently defaulting. When pass-dependencies.md is
# not locatable (e.g. a self-test synthetic context passing no dep_text), the parser
# degrades to the canonical fallback map below — the same values, so never a regression.
# --------------------------------------------------------------------------

# Canonical fallback map (used only when pass-dependencies.md cannot be located).
# Byte-equivalent to the §4e Default-mapping block; kept so the validator never
# crashes in a python-context that lacks the reference file. KEEP IN SYNC with the
# §4e `#### Default mapping` block (and the bash degrade-path inline map): a future
# §4e default change must update this constant too, or a degraded (no-reference-file,
# non-CI) host would resolve stale severities. CI always locates the file, so this
# constant is never exercised there — it is purely the degraded-host safety net.
_CANONICAL_SIGNAL_MAP = {
    "must-fix-floor": "must-fix",
    "hard-gate": "must-fix",
    "high": "must-or-should",
}
# The three signal classes this validator drives (the strong audit-internal signals).
_REQUIRED_SIGNAL_CLASSES = ("must-fix-floor", "hard-gate", "high")


class SignalMapError(ValueError):
    """Raised when the §4e Audit-Signal Propagation mapping is malformed."""


# Synthesis-severity recognizers, longest/most-specific first so
# "Must-Fix or Should-Fix" resolves to must-or-should before the bare Must-Fix rule.
_SEVERITY_TIERS = (
    ("must-or-should", re.compile(r"Must-Fix\s+or\s+Should-Fix", re.IGNORECASE)),
    ("must-fix", re.compile(r"Must-Fix", re.IGNORECASE)),
    ("should-fix", re.compile(r"Should-Fix", re.IGNORECASE)),
    ("could-fix", re.compile(r"Could-Fix", re.IGNORECASE)),
)
# Signal-class recognizers for the Default-mapping bullet left-hand side,
# most-specific first ("Must-Fix floor" before the bare "HIGH"/"Alert" rule).
_SIGNAL_CLASS_PATTERNS = (
    ("must-fix-floor", re.compile(r"Must-Fix\s+floor", re.IGNORECASE)),
    ("hard-gate", re.compile(r"hard[\s-]gate", re.IGNORECASE)),
    ("high", re.compile(r"\bHIGH\b|\bAlert\b", re.IGNORECASE)),
)
_MAPPING_ARROW = r"(?:→|->)"  # → or ASCII ->
_DEFAULT_MAPPING_HEADING_RE = re.compile(r"^#{1,6}\s.*Default mapping", re.IGNORECASE)
_OVERRIDE_DIRECTIVE_RE = re.compile(
    r"propagate-override:\s*([A-Za-z][A-Za-z-]*)\s*" + _MAPPING_ARROW + r"\s*([^|]+)",
    re.IGNORECASE)


def _severity_to_tier(text):
    for tier, rx in _SEVERITY_TIERS:
        if rx.search(text):
            return tier
    return None


def _parse_default_mapping(dep_text):
    """Parse the §4e '#### Default mapping' block into {signal-class: synthesis-tier}
    for the three strong signal classes. Raise SignalMapError if the block is missing,
    a required class is absent, or a row's synthesis severity is unrecognized."""
    lines = dep_text.split("\n")
    start = None
    for i, ln in enumerate(lines):
        if _DEFAULT_MAPPING_HEADING_RE.match(ln):
            start = i
            break
    if start is None:
        raise SignalMapError(
            "§4e '#### Default mapping (fallback for un-enumerated audits)' block not found")
    mapping = {}
    for ln in lines[start + 1:]:
        if re.match(r"^#{1,6}\s", ln):  # next heading closes the block
            break
        m = re.match(r"\s*-\s+(.*?)\s*" + _MAPPING_ARROW + r"\s*(.*\S)\s*$", ln)
        if not m:
            continue
        lhs, rhs = m.group(1), m.group(2)
        cls = None
        for c, rx in _SIGNAL_CLASS_PATTERNS:
            if rx.search(lhs):
                cls = c
                break
        if cls is None:
            continue  # MEDIUM/Flag and LOW/Note rows are not driven by this validator
        tier = _severity_to_tier(rhs)
        if tier is None:
            raise SignalMapError(
                "malformed §4e default-mapping row (unrecognized synthesis severity): %r"
                % ln.strip())
        mapping[cls] = tier
    for required in _REQUIRED_SIGNAL_CLASSES:
        if required not in mapping:
            raise SignalMapError(
                "§4e default mapping is missing required signal class %r" % required)
    return mapping


def _parse_per_audit_overrides(dep_text):
    """Scan §4e table rows for an Override-column directive
    `propagate-override: <signal-class> → <synthesis-severity>` and build
    {audit-slug: {signal-class: synthesis-tier}}. A directive naming an unknown signal
    class or an unrecognized synthesis severity is a SignalMapError (malformed row)."""
    overrides = {}
    for ln in dep_text.split("\n"):
        if "propagate-override:" not in ln:
            continue
        if not ln.lstrip().startswith("|"):
            continue  # directives are only honored inside a §4e table row
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if not cells or not cells[0]:
            continue
        slug = _audit_slug(_strip_leading_determiner(cells[0]))
        for m in _OVERRIDE_DIRECTIVE_RE.finditer(ln):
            cls_raw = m.group(1).strip().lower()
            sev_raw = m.group(2).strip()
            if cls_raw not in _REQUIRED_SIGNAL_CLASSES:
                raise SignalMapError(
                    "malformed §4e override directive for %r: unknown signal class %r"
                    % (cells[0], cls_raw))
            tier = _severity_to_tier(sev_raw)
            if tier is None:
                raise SignalMapError(
                    "malformed §4e override directive for %r: unrecognized synthesis "
                    "severity %r" % (cells[0], sev_raw))
            overrides.setdefault(slug, {})[cls_raw] = tier
    return overrides


def _locate_pass_dependencies():
    """Best-effort locate pass-dependencies.md relative to this script, mirroring the
    two committed script-mirror layouts (plugin copy and repo-root copy). Returns a
    path or None."""
    here = os.path.dirname(os.path.abspath(__file__))
    for base in (os.path.join(here, "..", "skills", "core-editor", "references"),
                 os.path.join(here, "..", "plugins", "apodictic", "skills",
                              "core-editor", "references")):
        cand = os.path.join(base, "pass-dependencies.md")
        if os.path.isfile(cand):
            return cand
    return None


def _load_signal_map(dep_text=None):
    """Build the §4e-driven signal map {'default': {...}, 'per_audit': {...}}.

    dep_text (raw §4e / pass-dependencies markdown) drives the parse when supplied
    (used by the hostile self-test fixtures). Otherwise the real pass-dependencies.md
    is located and read. If the file cannot be located, degrade to the canonical
    fallback map (same values — never a regression). A located-but-malformed §4e
    raises SignalMapError so the caller can surface it."""
    if dep_text is None:
        path = _locate_pass_dependencies()
        if path is None:
            return {"default": dict(_CANONICAL_SIGNAL_MAP), "per_audit": {}}
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            dep_text = fh.read()
    return {"default": _parse_default_mapping(dep_text),
            "per_audit": _parse_per_audit_overrides(dep_text)}


def _tier_satisfied(tier, synth_mf, synth_sf):
    """Whether the presence of body Must-Fix / Should-Fix satisfies `tier`."""
    return {"must-fix": synth_mf,
            "must-or-should": synth_mf or synth_sf,
            "should-fix": synth_sf,
            "could-fix": True}.get(tier, False)


_HIGH_SIGNAL_RE = re.compile(
    r"(HIGH[- ]severity|Alert finding|Alert concentration|HIGH signal|HIGH rating|"
    r"HIGH-severity|HIGH-confidence)", re.IGNORECASE)
# Audit-name recognizer. Title-case words (no IGNORECASE, so lowercase connector words
# like "and"/"the" cannot be consumed — prevents over-capturing across two audits on one
# line) plus standalone "&" / "/" connectors and an optional trailing parenthetical, so
# registry names like "Series & Composite Novel", "Memoir / Creative NF", and
# "Banister (Epistemic Humility)" are captured whole rather than truncated to a suffix.
_AUDIT_NAME_RE = re.compile(
    r"([A-Z][A-Za-z/&-]*(?: (?:[&/]|[A-Z][A-Za-z/&-]*)){0,6}(?: \([^)]+\))?) [Aa]udit")
# Sentence-initial determiners that prose puts in front of an audit name
# ("The Reception Risk Audit triggered ...") are not part of the name. Strip a leading
# determiner WORD (the trailing \s+ guards real first words like "Theme"/"Anchor") so the
# prose mention collapses onto the heading-derived name instead of inventing a phantom.
_LEADING_DETERMINER_RE = re.compile(r"^(?:the|an?|this|that|these|those)\s+", re.IGNORECASE)
_EVIDENCE_RE = re.compile(r"(?:L|line )[0-9]+", re.IGNORECASE)


def _strip_leading_determiner(name):
    return _LEADING_DETERMINER_RE.sub("", name)


def _audit_slug(name):
    s = name.lower().replace("&", "")
    s = re.sub(r"[()]", "", s)  # drop parens so e.g. "Banister (Epistemic Humility)" slugs cleanly
    s = re.sub(r"[\s/]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def _evidence_lines(text):
    return {re.sub(r"^(?:L|line )", "", m, flags=re.IGNORECASE)
            for m in _EVIDENCE_RE.findall(text)}


def _grep_after(text, pattern, n):
    seg = text.split("\n")
    rx = re.compile(pattern, re.IGNORECASE)
    keep = set()
    for i, ln in enumerate(seg):
        if rx.search(ln):
            keep.update(range(i, min(len(seg), i + n + 1)))
    return "\n".join(seg[i] for i in sorted(keep))


def _audit_subsection(appx_body, name, fallback_after):
    """Lines from the heading containing '<name> audit' through the next heading;
    fall back to grep '<name> audit' -A <fallback_after> when no heading matches."""
    pat = re.compile(re.escape(name) + r" audit", re.IGNORECASE)
    out, in_section = [], False
    for ln in appx_body.split("\n"):
        is_heading = ln.startswith("#")
        if is_heading and pat.search(ln):
            in_section = True
            out.append(ln)
            continue
        if in_section and is_heading:
            break
        if in_section:
            out.append(ln)
    if not out:
        return _grep_after(appx_body, re.escape(name) + r" audit", fallback_after)
    return "\n".join(out)


def audit_signal_propagation(text, dep_text=None):
    errors, warnings = [], []
    ok_line = ("OK: Audit-internal severity signals propagated to synthesis layer "
               "(per-audit; or override marker present in body).")
    failed_line = ("FAILED: %d audit-signal propagation failure(s). Canonical rule: "
                   "core-editor/references/run-synthesis.md §Step 2; per-audit table: "
                   "pass-dependencies.md §4e.")
    # §4e is the source of truth for the signal-class → synthesis-severity mapping.
    try:
        signal_map = _load_signal_map(dep_text)
    except SignalMapError as exc:
        errors.append("ERROR: §4e Audit-Signal Propagation mapping is malformed — %s "
                      "(pass-dependencies.md §4e is the source of truth for the "
                      "signal→severity mapping)." % exc)
        return errors, warnings, ok_line, failed_line % len(errors)
    default_map = signal_map["default"]
    per_audit_map = signal_map["per_audit"]
    lines = _content_lines(text)
    total = len(lines)
    appendix_idx = None  # 1-based
    appx_rx = re.compile(r"^#{1,4}.*Appendix [A-C]", re.IGNORECASE)
    for i, ln in enumerate(lines):
        if appx_rx.search(ln):
            appendix_idx = i + 1
            break
    if appendix_idx:
        synth_body = "\n".join(lines[: appendix_idx - 1])
        appx_body = "\n".join(lines[appendix_idx - 1:])
    else:
        synth_body, appx_body = "\n".join(lines), ""

    ov_must_fix = has_override(synth_body, "audit-propagation-must-fix")
    ov_hard_gate = has_override(synth_body, "audit-propagation-hard-gate")
    ov_high = has_override(synth_body, "audit-propagation-high")
    per_audit_overrides = override_slugs(synth_body, "audit-propagation-")

    def tier_items(tier):
        rx = {"must-fix": r"Must-Fix",
              "must-or-should": r"Must-Fix|Should-Fix",
              "should-fix": r"Should-Fix",
              "could-fix": r"Could-Fix"}[tier]
        pat = re.compile(rx, re.IGNORECASE)
        return "\n".join(ln for ln in synth_body.split("\n") if pat.search(ln))

    def check_audit_signal(audit_name, signal_class):
        slug = _audit_slug(audit_name)
        # Required synthesis tier is §4e-driven: a per-audit Override-column directive
        # for this slug/signal-class wins; otherwise the §4e Default mapping applies.
        required_tier = per_audit_map.get(slug, {}).get(signal_class) \
            or default_map[signal_class]
        subsection = _audit_subsection(appx_body, audit_name, 5)
        audit_lines = _evidence_lines(subsection)
        body_items = tier_items(required_tier)
        name_match = bool(body_items) and re.search(
            re.escape(audit_name), body_items, re.IGNORECASE) is not None
        line_match = bool(audit_lines) and bool(body_items) and \
            bool(audit_lines & _evidence_lines(body_items))
        if name_match or line_match:
            return 0
        class_override = {"must-fix-floor": ov_must_fix, "hard-gate": ov_hard_gate,
                          "high": ov_high}.get(signal_class, False)
        per_audit_override = slug in per_audit_overrides
        if class_override or per_audit_override:
            kind = ("per-audit (audit-propagation-%s)" % slug) if per_audit_override else "class"
            warnings.append("WARN: %s %s signal not propagated to synthesis body "
                            "(override marker present in body — %s)."
                            % (audit_name, signal_class, kind))
            return 0
        errors.append("ERROR: %s %s signal in appendix did not propagate to synthesis-body "
                      "%s item (no audit-name reference and no shared evidence-line; no "
                      "override marker in body)." % (audit_name, signal_class, required_tier))
        return 1

    audit_names = sorted({_strip_leading_determiner(n) for n in _AUDIT_NAME_RE.findall(appx_body)})

    if not audit_names:
        # Legacy whole-letter fallback (no named audit appendix). The required tier
        # for each strong signal class is §4e-driven (default_map), not hardcoded.
        synth_mf = re.search(r"Must-Fix", synth_body, re.IGNORECASE) is not None
        synth_sf = re.search(r"Should-Fix", synth_body, re.IGNORECASE) is not None
        if re.search(r"hard gate", text, re.IGNORECASE) and \
                not _tier_satisfied(default_map["hard-gate"], synth_mf, synth_sf):
            if ov_hard_gate:
                warnings.append("WARN: Audit hard gate present without synthesis-layer "
                                "Must-Fix (override marker detected in body).")
            else:
                errors.append("ERROR: Audit hard gate present but no synthesis-layer "
                              "Must-Fix flag (no override marker in body).")
        if re.search(r"Must-Fix floor", text, re.IGNORECASE) and \
                not _tier_satisfied(default_map["must-fix-floor"], synth_mf, synth_sf):
            if ov_must_fix:
                warnings.append("WARN: Audit Must-Fix floor present without synthesis-layer "
                                "Must-Fix (override marker detected in body).")
            else:
                errors.append("ERROR: Audit Must-Fix floor present but no synthesis-layer "
                              "Must-Fix flag (no override marker in body).")
        if re.search(r"(HIGH[- ]severity|Alert finding|Alert concentration|HIGH signal|"
                     r"HIGH rating)", text, re.IGNORECASE) and \
                not _tier_satisfied(default_map["high"], synth_mf, synth_sf):
            if ov_high:
                warnings.append("WARN: Audit HIGH/Alert signal present without synthesis "
                                "Must-Fix or Should-Fix (override marker detected in body).")
            else:
                errors.append("ERROR: Audit HIGH/Alert signal present but no synthesis "
                              "Must-Fix or Should-Fix (no override marker in body).")
    else:
        for audit_name in audit_names:
            sub = _audit_subsection(appx_body, audit_name, 8)
            saw_strong = False
            if re.search(r"(hard gate|hard-gate)", sub, re.IGNORECASE):
                check_audit_signal(audit_name, "hard-gate")
                saw_strong = True
            if re.search(r"Must-Fix floor", sub, re.IGNORECASE):
                check_audit_signal(audit_name, "must-fix-floor")
                saw_strong = True
            if not saw_strong and _HIGH_SIGNAL_RE.search(sub):
                check_audit_signal(audit_name, "high")

    return errors, warnings, ok_line, failed_line % len(errors)


def check_registry(reg_path, dep_path):
    """Every registry-listed signal-emitting audit must have a §4e row ('| <audit> |')
    in pass-dependencies.md or in the argument-audits-propagation.md fragment (Phase A
    carve moved argument-cluster rows to the fragment; both files are authoritative).
    Prints the legacy Registry-check summary; returns rc."""
    if not os.path.isfile(reg_path) or not os.path.isfile(dep_path):
        sys.stderr.write("Error: registry or pass-dependencies file not found "
                         "(REG=%s DEP=%s)\n" % (reg_path, dep_path))
        return 2
    with open(reg_path, "r", encoding="utf-8", errors="replace") as fh:
        reg_lines = fh.read().split("\n")
    with open(dep_path, "r", encoding="utf-8", errors="replace") as fh:
        dep_text = fh.read()
    # Also load the argument-audits-propagation fragment (Phase A carve): argument-cluster
    # §4e rows live there after extraction. Locate it relative to pass-dependencies.md.
    frag_path = os.path.join(os.path.dirname(dep_path), "argument-audits-propagation.md")
    if os.path.isfile(frag_path):
        with open(frag_path, "r", encoding="utf-8", errors="replace") as fh:
            dep_text += "\n" + fh.read()
    entries, capture = [], False
    for ln in reg_lines:
        if "registry:signal-emitting-audits:begin" in ln:
            capture = True
            continue
        if "registry:signal-emitting-audits:end" in ln:
            break
        if capture and ln.startswith("- "):
            entries.append(ln[2:])
    if not entries:
        sys.stderr.write("Error: no registry entries found in %s\n" % reg_path)
        return 2
    missing = [a for a in entries if ("| %s |" % a) not in dep_text]
    for a in missing:
        print("ERROR: signal-emitting audit '%s' has no §4e propagation row in %s"
              % (a, os.path.basename(dep_path)))
    if not missing:
        print("Registry check: PASS (%d signal-emitting audits all have §4e rows)"
              % len(entries))
        return 0
    print("Registry check: FAIL (%d of %d registry audits missing a §4e row)"
          % (len(missing), len(entries)))
    return 1


# --------------------------------------------------------------------------
# underdiagnosis-triggers — Conditional Underdiagnosis Retry Loop.
# Canonical home: run-synthesis.md §Step 9. Faithful port: triggers #1-4 scan the
# whole letter (mechanism convergence, hard-gate, final-third, multi-axis) against the
# body Must-Fix; triggers #5-6 reuse the ported severity_floor / audit_signal_propagation.
# --------------------------------------------------------------------------

_CONV_KEYWORDS = ["aftermath", "compression", "status", "thread", "final-third",
                  "coercion", "agency", "opacity"]


def underdiagnosis_triggers(text):
    errors, warnings, fired = [], [], []
    lines = _content_lines(text)
    appendix_idx = None
    appx_rx = re.compile(r"^#{1,4}.*Appendix [A-C]", re.IGNORECASE)
    for i, ln in enumerate(lines):
        if appx_rx.search(ln):
            appendix_idx = i + 1
            break
    body = "\n".join(lines[: appendix_idx - 1]) if appendix_idx else "\n".join(lines)
    body_mustfix = re.search(r"Must-Fix", body, re.IGNORECASE) is not None

    ov = {k: has_override(body, "underdiagnosis-trigger-%s" % k)
          for k in ("convergence", "hard-gate", "final-third", "multi-axis",
                    "severity-floor", "propagation")}

    def fire(key, ovkey, warn_msg, err_msg):
        if ov[ovkey]:
            warnings.append(warn_msg)
        else:
            errors.append(err_msg)
        fired.append(key)

    # Trigger 1: convergence — same mechanism keyword in 3+ artifacts, no body Must-Fix.
    if not body_mustfix:
        for kw in _CONV_KEYWORDS:
            if len(re.findall(kw, text, re.IGNORECASE)) >= 3:
                fire("convergence", "convergence",
                     "WARN: Trigger #1 (convergence) — '%s' appears in 3+ artifacts with no "
                     "synthesis Must-Fix (override marker detected in body)." % kw,
                     "ERROR: Trigger #1 (convergence) — '%s' appears in 3+ artifacts with no "
                     "synthesis Must-Fix and no override marker in body." % kw)
                break

    # Trigger 2: hard-gate — audit Alert/hard gate present, no body Must-Fix.
    if re.search(r"(hard gate|Alert (concentration|finding))", text, re.IGNORECASE) and not body_mustfix:
        fire("hard-gate", "hard-gate",
             "WARN: Trigger #2 (hard-gate) — high-risk audit Alert/hard gate present without "
             "synthesis Must-Fix (override marker detected in body).",
             "ERROR: Trigger #2 (hard-gate) — high-risk audit Alert/hard gate present without "
             "synthesis Must-Fix and no override marker in body.")

    # Trigger 3: final-third — character pass + structure pass both flag the final third.
    ft = r"(final[- ]third|act[- ]?(III|3)|close|climax)"
    if (re.search(r"(character pass|character audit).*" + ft, text, re.IGNORECASE)
            and re.search(r"(structure pass|structural pass|structure audit).*" + ft, text, re.IGNORECASE)
            and not body_mustfix):
        fire("final-third", "final-third",
             "WARN: Trigger #3 (final-third) — final-third concern flagged by both character + "
             "structure passes without synthesis Must-Fix (override marker in body).",
             "ERROR: Trigger #3 (final-third) — final-third concern flagged by both character + "
             "structure passes without synthesis Must-Fix and no override marker in body.")

    # Trigger 4: multi-axis — 2+ of {series, representation, reader-trust}, no body Must-Fix.
    axis = (bool(re.search(r"series", text, re.IGNORECASE))
            + bool(re.search(r"representation", text, re.IGNORECASE))
            + bool(re.search(r"reader[- ]trust", text, re.IGNORECASE)))
    if axis >= 2 and not body_mustfix:
        fire("multi-axis", "multi-axis",
             "WARN: Trigger #4 (multi-axis) — concern spans %d+ severity classes without "
             "synthesis Must-Fix (override marker in body)." % axis,
             "ERROR: Trigger #4 (multi-axis) — concern spans %d+ severity classes "
             "(series/representation/reader-trust) without synthesis Must-Fix and no override "
             "marker in body." % axis)

    # Trigger 5: severity-floor — reuse the ported check (fires on its WARN/ERROR).
    sf_e, sf_w, _, _ = severity_floor(text)
    if sf_e or sf_w:
        fire("severity-floor", "severity-floor",
             "WARN: Trigger #5 (severity-floor) — severity-floor validator surfaced WARN/ERROR "
             "(override marker in body).",
             "ERROR: Trigger #5 (severity-floor) — severity-floor validator surfaced WARN/ERROR "
             "with no override marker in body.")

    # Trigger 6: propagation — reuse the ported check.
    ap_e, ap_w, _, _ = audit_signal_propagation(text)
    if ap_e or ap_w:
        fire("propagation", "propagation",
             "WARN: Trigger #6 (propagation) — audit-signal-propagation validator surfaced "
             "un-propagated signal (override marker in body).",
             "ERROR: Trigger #6 (propagation) — audit-signal-propagation validator surfaced "
             "un-propagated signal with no override marker in body.")

    fired_str = "".join(f + " " for f in fired)
    if fired:
        ok = "OK: Triggers fired (%s); all addressed via override markers in body." % fired_str
    else:
        ok = "OK: No underdiagnosis triggers fired."
    failed = ("FAILED: %d underdiagnosis trigger(s) fired. Triggers: %s\n"
              "Synthesis must either upgrade the affected finding's severity OR insert an "
              "override marker in the letter body. Canonical home: "
              "core-editor/references/run-synthesis.md §Step 9." % (len(errors), fired_str))
    return errors, warnings, ok, failed


# --------------------------------------------------------------------------
# ledger-consolidation — Findings Ledger Consolidation Contract.
# Canonical home: run-synthesis.md §Step 2. Faithful port: raw-aggregate detection,
# convergence annotation, severity collation, and (when a raw ledger is supplied) the
# reduction-ratio check. Override markers may appear anywhere (no body/appendix split).
# --------------------------------------------------------------------------


def _count_lines_matching(text, pattern, flags=0):
    rx = re.compile(pattern, flags)
    return sum(1 for ln in text.split("\n") if rx.match(ln))


def ledger_consolidation(text, raw_text=None):
    errors, warnings = [], []

    def gate(ov_present, warn_msg, err_msg):
        if ov_present:
            warnings.append(warn_msg)
        else:
            errors.append(err_msg)

    ov_raw = has_override(text, "ledger-consolidation-raw-aggregate")
    ov_conv = has_override(text, "ledger-consolidation-no-convergence")
    ov_collate = has_override(text, "ledger-consolidation-no-collation")
    ov_reduction = has_override(text, "ledger-consolidation-no-reduction")

    # Check 1: raw concatenation.
    raw_count = _count_lines_matching(text, r"^##+ Pass [0-9]+ Findings")
    if raw_count >= 3:
        gate(ov_raw,
             "WARN: Check 1 (raw-aggregate) — %d 'Pass N Findings' headers detected "
             "(override marker present)." % raw_count,
             "ERROR: Check 1 (raw-aggregate) — %d 'Pass N Findings' headers detected; raw "
             "concatenation pattern (no override marker)." % raw_count)

    # Check 2: convergence annotation.
    consol_headers = _count_lines_matching(text, r"^##+ (Mechanism|Finding|Cluster|Concern):")
    if consol_headers > 0:
        if not re.search(r"(confirmed by|also flagged|cross[- ]pass|Pass [0-9].*Pass [0-9]|"
                         r"appears in [0-9]+ pass)", text, re.IGNORECASE):
            gate(ov_conv,
                 "WARN: Check 2 (convergence) — consolidated entries present but no convergence "
                 "annotation found (override marker present).",
                 "ERROR: Check 2 (convergence) — consolidated entries present but no convergence "
                 "annotation found (no override marker). Add '(confirmed by Pass N, ...)' to "
                 "multi-source entries.")

    # Check 3: severity collation.
    sev_tiers = sum(bool(re.search(t, text, re.IGNORECASE))
                    for t in ("Must-Fix", "Should-Fix", "Could-Fix"))
    if sev_tiers >= 2 and consol_headers > 0:
        if not re.search(r"(collated|highest severity|downgrad|upgrad|resolved)", text, re.IGNORECASE):
            gate(ov_collate,
                 "WARN: Check 3 (severity-collation) — multiple severity tiers present without "
                 "collation annotation (override marker present).",
                 "ERROR: Check 3 (severity-collation) — multiple severity tiers present in "
                 "consolidated entries but no collation annotation "
                 "(collated/downgrade/upgrade/resolved). No override marker.")

    # Check 4: reduction ratio (only when a raw ledger is supplied).
    if raw_text is not None:
        raw_items = _count_lines_matching(raw_text, r"^- ")
        cons_items = _count_lines_matching(text, r"^- ")
        if raw_items > 0:
            threshold = raw_items * 70 // 100
            if cons_items > threshold:
                gate(ov_reduction,
                     "WARN: Check 4 (reduction) — consolidated items (%d) exceed 70%% of raw items "
                     "(%d; threshold %d); insufficient reduction (override marker present)."
                     % (cons_items, raw_items, threshold),
                     "ERROR: Check 4 (reduction) — consolidated items (%d) exceed 70%% of raw items "
                     "(%d; threshold %d); insufficient reduction. No override marker."
                     % (cons_items, raw_items, threshold))

    return errors, warnings, \
        "OK: Findings Ledger consolidation contract satisfied (or override markers present).", \
        ("FAILED: %d ledger-consolidation contract failure(s). Canonical contract: "
         "core-editor/references/run-synthesis.md §Step 2 — Findings Ledger Consolidation "
         "Contract." % len(errors))


# ----------------------------------------------------------------------
# author-facing-lint (#16) — advisory, warn-only.
# Enforces output-policy.md §Author-Facing Language: framework shorthand must be
# translated on first use and "never as the primary label." Surfaces framework
# codes used as an un-glossed primary label in the author-facing synthesis BODY
# (appendices are exempt — the policy explicitly allows codes there). A code is
# exempt when glossed inline on first use, in either legitimate form:
#   "plain language (CODE)"   (code in parens after the words), or
#   "CODE (plain-language gloss)"   (code defined by a following parenthetical).
# Only the FIRST use of each distinct code is judged (the policy's "on first
# use"). This check NEVER errors — every hit is a warning, so it cannot fail the
# build; promote to blocking once it is proven quiet. Body override marker:
# <!-- override: author-facing-lint -->.
#
# Patterns are the framework's real code families (not hand-rolled guesses):
#   pass numbers (Pass 11F), confidence tags ([HIGH CONFIDENCE], [UNCERTAIN]),
#   finding / quality codes (QF-7, CR-8, CR-01, FM-A10), prose tier labels (P0-P5).
_AFL_CODE_RE = re.compile(
    r"\bPass\s+\d+[A-Z]?\b"
    r"|\[(?:HIGH|MEDIUM|MODERATE|LOW)\s+CONFIDENCE\]"
    r"|\[UNCERTAIN\]"
    r"|\b(?:QF|CR|FM)-[A-Z]?\d+\b"
    r"|\bP[0-5]\b"
)


def _afl_has_plain_language(s):
    """True if `s` carries descriptive words beyond framework codes — tells a real
    inline gloss ('weak motivation') from codes glossing codes ('QF-7')."""
    return bool(re.search(r"[A-Za-z]{2,}", _AFL_CODE_RE.sub(" ", s)))


def _afl_phrase_before_paren(before):
    """True when `before` (rstripped, ending in '(') is a real plain-language phrase
    right up to the paren — i.e. descriptive words follow any trailing framework code,
    so 'weak motivation (' qualifies but a code-only 'Pass 11F (' does not."""
    if not before.endswith("("):
        return False
    pre = before[:-1]
    tail = pre
    for cm in _AFL_CODE_RE.finditer(pre):
        tail = pre[cm.end():]
    return bool(re.search(r"[A-Za-z]{2,}", tail))


def author_facing_lint(text):
    """Advisory lint (warn-only): framework codes used as un-glossed primary
    labels in the author-facing letter body. Returns (errors, warnings, ok,
    failed); `errors` is ALWAYS empty so the build is never gated."""
    body = split_body(text)
    ok = ("OK: author-facing-lint — no un-translated framework codes used as "
          "primary labels in the synthesis body (advisory).")
    failed = ""  # unused: this check never errors
    if has_override(body, "author-facing-lint"):
        return [], [], ok, failed
    warnings = []
    seen = set()
    for i, line in enumerate(body.split("\n"), start=1):
        if line.lstrip().startswith("<!--"):
            continue  # HTML-comment / marker lines are not author-facing prose
        for m in _AFL_CODE_RE.finditer(line):
            code = m.group(0)
            key = code.upper()
            if key in seen:
                continue  # judge only the first use of each distinct code
            seen.add(key)
            before = line[:m.start()].rstrip()
            after = line[m.end():].lstrip()
            # Exempt a code only when it carries an ACTUAL inline definition whose text
            # is real descriptive words, not just more codes ("Pass 11F (QF-7)" defines
            # nothing). Accepted output-policy.md forms:
            #   "CODE (plain-language gloss)"   — a following parenthetical with real text
            #   "CODE — plain-language gloss"   — a dash-led inline phrase with real text
            #   "plain-language version (CODE)" — real words right before the opening paren
            paren_after = re.match(r"\(([^)]*)\)", after)         # CODE (...)
            dash_after = re.match(r"(?:[—–]|-\s)\s*(.+)", after)  # CODE — ... / CODE - ...
            if ((paren_after and _afl_has_plain_language(paren_after.group(1)))
                    or (dash_after and _afl_has_plain_language(dash_after.group(1)))
                    or _afl_phrase_before_paren(before)):
                continue  # glossed inline on first use with real text → legitimate
            warnings.append(
                "WARN: author-facing-lint — framework code %r used without inline "
                "translation at line %d (first use). Define it in plain language "
                "on first use, gloss it as 'plain language (%s)', or move it to an "
                "appendix (output-policy.md §Author-Facing Language)."
                % (code, i, code))
    return [], warnings, ok, failed


# --------------------------------------------------------------------------
# synthesis-sections — run-synthesis.md §Post-Write Section Validation.
#
# The 14 required editorial-letter sections must each appear as a markdown
# HEADING (a line opening with 1-4 `#`), not merely as a phrase in prose.
#
# Hardening over the legacy `grep -iE "^#{1,4}\s.*NAME"`: the section name
# must open the heading *title* (after the `#` run, whitespace, and optional
# emphasis markers), matched at a trailing word boundary. This kills the
# mid-heading false-positive the raw `.*NAME` substring allowed — a heading
# like `## Notes on the Stress Test approach` no longer satisfies the
# `Stress Test` requirement — while still accepting the canonical
# subtitled/emphasized forms (`## Appendix A — Diagnostic Detail`,
# `# Development Edit — Worked Example`, `## **Stress Test**`).
# --------------------------------------------------------------------------

# Required section headings, in the run-synthesis.md validation order.
_SYNTHESIS_SECTIONS = (
    "Development Edit", "The Short Version", "What the Book Does Best",
    "What Needs Work", "Additional Observations", "Revision Checklist",
    "Protected Elements", "Author Decisions", "Control Questions",
    "The Strongest Case Against", "Stress Test", "Appendix A",
    "Appendix B", "Appendix C",
)

# A markdown heading line: 1-4 `#`, whitespace, then the title (group 1).
_HEADING_RE = re.compile(r"^#{1,4}\s+(.*\S)\s*$", re.MULTILINE)
# Leading emphasis / list decoration to peel off a heading title before the
# section-name prefix test (`**Stress Test**`, `_Stress Test_`).
_HEADING_LEAD_RE = re.compile(r"^[*_\s]+")


def _heading_titles(text):
    """Every markdown heading title in `text`, decoration-stripped."""
    out = []
    for m in _HEADING_RE.finditer(text):
        title = _HEADING_LEAD_RE.sub("", m.group(1)).lstrip()
        out.append(title)
    return out


def _title_opens_with(title, name):
    """True iff `title` opens with section `name` at a trailing word boundary.

    Case-insensitive. `Appendix A — Diagnostic Detail` opens with `Appendix A`
    (next char is whitespace); `Appendix Alpha` does NOT open with `Appendix A`
    (next char `l` is a word char); `Notes on X` does not open with `X`.
    """
    tl, nl = title.lower(), name.lower()
    if not tl.startswith(nl):
        return False
    rest = tl[len(nl):]
    # trailing boundary: end-of-title, or the next char is not alphanumeric.
    return rest == "" or not (rest[0].isalnum() or rest[0] == "_")


def synthesis_sections(text):
    """Check the 14 required editorial-letter section headings are present.

    Returns (errors, warnings, ok_line, failed_line). One ERROR per missing
    heading; the letter fails (exit 1) if any are missing.
    """
    titles = _heading_titles(text)
    errors = []
    for name in _SYNTHESIS_SECTIONS:
        if not any(_title_opens_with(t, name) for t in titles):
            errors.append("ERROR: Missing required heading: '%s'" % name)
    ok = "OK: All 14 required section headings present in editorial letter."
    failed = ("FAILED: %d missing required heading(s) in editorial letter.\n"
              "NOTE: Sections must appear as markdown headings (lines starting with #),\n"
              "not just as phrases in prose." % len(errors))
    return errors, [], ok, failed


# --------------------------------------------------------------------------
# tone-check — output-policy.md §Severity Tone (no sycophantic superlatives).
#
# Hardening over the legacy whole-file `grep -iq "\bWORD\b"`: scan only the
# synthesis BODY (superlatives quoted as evidence in an appendix are not the
# letter's own tone), with code spans/fences stripped via the shared
# override_marker.strip_code_spans SSoT (a superlative in a fenced example or
# inline `code` is documentation, not praise) and markdown blockquote lines
# dropped (a `>`-quoted author blurb — "> a masterpiece" — is quoted external
# text, not the letter's assessment voice). The letter's own prose is judged.
# --------------------------------------------------------------------------

_BLOCKED_SUPERLATIVES = (
    "masterpiece", "stunning", "flawless", "clean bill",
    "tour de force", "triumph", "perfection",
)


def tone_check(text):
    """Flag blocked sycophantic superlatives in the editorial-letter body.

    Returns (errors, warnings, ok_line, failed_line). One ERROR per distinct
    blocked superlative found; the letter fails (exit 1) if any are found.
    """
    body = split_body(text)
    scan = strip_code_spans(body)
    scan = "\n".join(ln for ln in scan.split("\n") if not ln.lstrip().startswith(">"))
    errors = []
    for word in _BLOCKED_SUPERLATIVES:
        if re.search(r"\b%s\b" % re.escape(word), scan, re.IGNORECASE):
            errors.append("ERROR: Blocked superlative found: '%s'" % word)
    ok = "OK: No blocked superlatives found. Severity tone is compliant."
    failed = ("FAILED: %d blocked superlative(s) found in editorial letter.\n"
              "NOTE: The framework enforces rigorous diagnosis; sycophantic praise "
              "is not permitted." % len(errors))
    return errors, [], ok, failed


# --------------------------------------------------------------------------
# ledger-check — the Findings Ledger's per-pass required-subsection contract.
#
# Each `## Pass N` entry must carry five `### ` subsections; Pass 0 and Pass 10
# are data-building passes (a missing subsection is a NOTE, not an ERROR). This
# check emits NOTE lines and a no-passes WARNING that fails — output the 4-tuple
# CHECKS wrapper can't express — so it returns (rc, lines) directly and is
# dispatched via RAW_CHECKS.
#
# Hardening over the legacy `sed`-sliced `grep -q "### NAME"`: the pass slices
# are bounded exactly between consecutive `## Pass N` headings, and required
# subsections are matched as real `### ` heading lines (anchored, word-boundary)
# rather than a substring that a mid-line prose `### NAME` could satisfy.
# --------------------------------------------------------------------------

_LEDGER_REQUIRED = (
    "Notable Findings", "Data Artifacts for Letter Reference",
    "Cross-Pass Connections", "Unresolved Questions", "Audit Triggers",
)
_PASS_HEADER_RE = re.compile(r"^## Pass (\d+)", re.MULTILINE)
_SUBSECTION_RE = re.compile(r"^#{3,}\s+(.*\S)\s*$", re.MULTILINE)


def _pass_has_subsection(section_text, name):
    """True iff `section_text` contains a `### `/`#### ` heading opening with `name`."""
    for m in _SUBSECTION_RE.finditer(section_text):
        title = _HEADING_LEAD_RE.sub("", m.group(1)).lstrip()
        if _title_opens_with(title, name):
            return True
    return False


def ledger_check(text):
    """Validate the Findings Ledger's per-pass required subsections.

    Returns (rc, lines). rc 0 = all required subsections present (Pass 0/10
    misses are NOTE-only), rc 1 = a missing subsection in a non-data-building
    pass, or no pass entries at all.
    """
    headers = list(_PASS_HEADER_RE.finditer(text))
    if not headers:
        return 1, ["WARNING: No pass entries found in ledger."]

    lines, errors = [], 0
    for idx, m in enumerate(headers):
        # Verbatim digit token (string), matching the legacy bash `grep -o '[0-9]\+'`:
        # the Pass 0/10 leniency is a string compare, and the surfaced line echoes the
        # token verbatim (so a non-canonical `## Pass 00` stays strict + prints "Pass 00").
        pass_tok = m.group(1)
        start = m.start()
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(text)
        section = text[start:end]
        lenient = pass_tok in ("0", "10")
        for req in _LEDGER_REQUIRED:
            if _pass_has_subsection(section, req):
                continue
            if lenient:
                lines.append("NOTE: Pass %s missing '### %s' (acceptable for "
                             "data-building pass)" % (pass_tok, req))
            else:
                lines.append("ERROR: Pass %s missing required section '### %s'"
                             % (pass_tok, req))
                errors += 1

    if errors > 0:
        lines.append("")
        lines.append("FAILED: %d missing required section(s) in ledger." % errors)
        return 1, lines
    lines.append("OK: All pass entries contain required sections.")
    return 0, lines


# Registry of file-driven checks: name -> function(text) -> (errors, warnings, ok, failed).
CHECKS = {
    "severity-floor": severity_floor,
    "decision-layer-check": decision_layer_check,
    "audit-signal-propagation": audit_signal_propagation,
    "underdiagnosis-triggers": underdiagnosis_triggers,
    "ledger-consolidation": ledger_consolidation,
    "author-facing-lint": author_facing_lint,
    "synthesis-sections": synthesis_sections,
    "tone-check": tone_check,
}

# Checks that return (rc, lines) directly (NOTE lines / no-passes WARNING that
# the (errors, warnings, ok, failed) wrapper can't express). Dispatched apart.
RAW_CHECKS = {
    "ledger-check": ledger_check,
}

# Checks that accept an optional second file (raw ledger for ledger-consolidation).
_TWO_FILE_CHECKS = {"ledger-consolidation"}


def run_check(name, path, extra_path=None):
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
    if name in _TWO_FILE_CHECKS:
        raw_text = None
        if extra_path and os.path.isfile(extra_path):
            with open(extra_path, "r", encoding="utf-8", errors="replace") as fh:
                raw_text = fh.read()
        errors, warnings, ok_line, failed_line = fn(text, raw_text)
    else:
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


def run_raw_check(name, path):
    """Run a (rc, lines)-returning check against a file; print its lines; return rc."""
    fn = RAW_CHECKS.get(name)
    if fn is None:
        sys.stderr.write("Error: unknown check: %s\n" % name)
        return 2
    if not os.path.isfile(path):
        sys.stderr.write("Error: File not found: %s\n" % path)
        return 2
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    rc, lines = fn(text)
    for ln in lines:
        print(ln)
    return rc


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

    def check_rc(name, got_rc, expect_clean):
        if (got_rc == 0) == expect_clean:
            print("  %s: OK" % name)
        else:
            print("  %s: FAIL (rc=%s)" % (name, got_rc))
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
        # 2026-06-20 override-substring hardening (shared override_marker.has_override): a marker quoted
        # inside a backtick CODE SPAN is a documentation example, not a live override -> still ERROR.
        over_codespan = ("# Development Edit\n## Best\nVoice axis rated Weak at High intensity.\n"
                         "Use `<!-- override: severity-floor-weak-axis -->` to suppress.\n"
                         "## What Needs Work\nPacing Should-Fix flag.\n## Appendix B\nx\n")
        check("sf_override_codespan_decoy_errors", severity_floor(over_codespan)[0], False)
        # a SUFFIX-COLLISION slug (`...-weak-axis-but-not-really`) must NOT satisfy `-weak-axis` -> ERROR.
        over_suffix = ("# Development Edit\n## Best\nVoice axis rated Weak at High intensity.\n"
                       "<!-- override: severity-floor-weak-axis-but-not-really — decoy. -->\n"
                       "## What Needs Work\nPacing Should-Fix flag.\n## Appendix B\nx\n")
        check("sf_override_suffix_collision_errors", severity_floor(over_suffix)[0], False)
        # a genuine marker WITH an em-dash reason IS honored -> WARN (already covered above); a genuine
        # marker with NO reason (bare `-->`) is also honored -> no ERROR.
        over_noreason = ("# Development Edit\n## Best\nVoice axis rated Weak at High intensity.\n"
                         "<!-- override: severity-floor-weak-axis -->\n"
                         "## What Needs Work\nPacing Should-Fix flag.\n## Appendix B\nx\n")
        check("sf_override_no_reason_honored", severity_floor(over_noreason)[0], True)
        # Justification text defuses Rule 3 even at the highest band.
        justified = ("# Development Edit\nVerdict: Strong Fit. The flag volume does not impair.\n"
                     "Should-Fix one. Should-Fix two. Should-Fix three.\n")
        check("sf_justified_band", severity_floor(justified)[0], True)

    if which in (None, "audit-signal-propagation"):
        # Registry completeness sub-tests: synthetic registry + §4e fixtures (2-file).
        import tempfile
        dep = ("### §4e. Audit-Signal Propagation Table\n"
               "| Foo Audit | hard gate | Must-Fix | — | src | — |\n"
               "| Bar Audit | flag | Should-Fix | — | src | — |\n")
        reg_ok = ("## Signal-Emitting Audit Registry\n"
                  "<!-- registry:signal-emitting-audits:begin -->\n"
                  "- Foo Audit\n- Bar Audit\n"
                  "<!-- registry:signal-emitting-audits:end -->\n")
        reg_missing = reg_ok.replace("- Bar Audit\n", "- Bar Audit\n- Ghost Audit\n")
        def expect_rc(name, got, want):
            if got == want:
                print("  %s: OK" % name)
            else:
                print("  %s: FAIL (rc=%s, expected %s)" % (name, got, want))
                rc["v"] = 1
        with tempfile.TemporaryDirectory() as td:
            dp = os.path.join(td, "dep.md"); open(dp, "w", encoding="utf-8", newline="").write(dep)
            rp_ok = os.path.join(td, "reg_ok.md"); open(rp_ok, "w", encoding="utf-8", newline="").write(reg_ok)
            rp_bad = os.path.join(td, "reg_bad.md"); open(rp_bad, "w", encoding="utf-8", newline="").write(reg_missing)
            expect_rc("registry_ok", check_registry(rp_ok, dp), 0)
            expect_rc("registry_missing", check_registry(rp_bad, dp), 1)

        # In-code propagation cases: POV Voice Profile appendix subsection as a
        # multi-POV fixture (Mara/Jon + Mara/Elen pairs). Exercises the §4e Must-Fix
        # row's signal class — a voice-collapse verdict on 2+ POV pairs + Blind-Swap
        # fail expressed as a Must-Fix floor. The "### POV Voice Profile Audit"
        # heading is what _AUDIT_NAME_RE parses as audit name "POV Voice Profile"
        # (slug pov-voice-profile); "Must-Fix floor" is the strong signal _audit_subsection
        # detects. See pass-dependencies.md §4e (POV Voice Profile rows).
        pov_positive = (
            "# Development Edit — Multi-POV Manuscript\n\n"
            "## What Needs Work\n\n"
            "- **Must-Fix:** Voice collapse between the Mara and Jon POV strands. "
            "The POV Voice Profile audit Must-Fix floor at L1840 surfaces here; the "
            "same flattening recurs across the Mara/Elen pair (lines 2100-2180). "
            "<!-- finding: F-PVP-01 -->\n\n"
            "## Appendix A — Diagnostic Detail\n\n"
            "### POV Voice Profile Audit\n\n"
            "Must-Fix floor triggered: voice-collapse verdict on 2 POV pairs "
            "(Mara/Jon, Mara/Elen) AND Pass 7 Blind Swap fails on the same pairs at L1840.\n")
        # positive: Must-Fix floor propagates via audit-name reference + shared evidence
        # line (L1840) to a body Must-Fix -> clean.
        check("pov_propagated_clean", audit_signal_propagation(pov_positive)[0], True)

        pov_negative = (
            "# Development Edit — Multi-POV Manuscript\n\n"
            "## What Needs Work\n\n"
            "- **Should-Fix:** The prologue competes with Chapter 1 for the reader's "
            "first orientation (Chapter 1, lines 1-40).\n\n"
            "## Appendix A — Diagnostic Detail\n\n"
            "### POV Voice Profile Audit\n\n"
            "Must-Fix floor triggered: voice-collapse verdict on 2 POV pairs "
            "(Mara/Jon, Mara/Elen) AND Pass 7 Blind Swap fails on the same pairs at L1840.\n")
        # negative: same Must-Fix floor but no body Must-Fix references the audit and
        # no shared evidence line -> ERROR.
        check("pov_unpropagated_errors", audit_signal_propagation(pov_negative)[0], False)

        pov_override = (
            "# Development Edit — Multi-POV Manuscript\n\n"
            "<!-- override: audit-propagation-must-fix — POV pair count is borderline "
            "this round; deferring to the qualitative Blind-Swap read. -->\n\n"
            "## What Needs Work\n\n"
            "- **Should-Fix:** The prologue competes with Chapter 1 for the reader's "
            "first orientation (Chapter 1, lines 1-40).\n\n"
            "## Appendix A — Diagnostic Detail\n\n"
            "### POV Voice Profile Audit\n\n"
            "Must-Fix floor triggered: voice-collapse verdict on 2 POV pairs "
            "(Mara/Jon, Mara/Elen) AND Pass 7 Blind Swap fails on the same pairs at L1840.\n")
        # override: the negative case + a body class-override marker -> no ERROR, one WARN.
        pov_e, pov_w = audit_signal_propagation(pov_override)[:2]
        check("pov_override_body_no_error", pov_e, True)
        warns("pov_override_body_warns", pov_w, True)

        # §4e-table-driven mapping hostile fixtures (2026-07-04). The signal→severity
        # mapping is now READ from §4e (dep_text). These inject a synthetic §4e to
        # prove (a) a per-audit Override-column modifier that reassigns the required
        # severity is honored, and (b) a malformed §4e mapping is caught.
        _dep_default = (
            "#### Default mapping (fallback for un-enumerated audits)\n\n"
            "- Audit-internal Must-Fix floor → Synthesis Must-Fix\n"
            "- Audit-internal hard gate → Synthesis Must-Fix\n"
            "- Audit-internal HIGH / Alert → Synthesis Must-Fix or Should-Fix per audit context\n")
        # A Reception Risk hard gate that reaches only a synthesis Should-Fix. Under the
        # §4e Default mapping (hard gate → Must-Fix) this FAILS; a per-audit
        # Override-column modifier reassigning hard-gate → Should-Fix makes it PASS.
        _mod_letter = (
            "# Development Edit\n## What Needs Work\n"
            "- **Should-Fix:** Reception Risk hard gate at L2956 — softened this round "
            "per calibration.\n"
            "## Appendix A: Reception Risk Audit\nHard Gate triggered at L2956.\n")
        _dep_modifier = _dep_default + (
            "\n| Reception Risk | Alert | Should-Fix | ctx | src | "
            "propagate-override: hard-gate → Should-Fix |\n")
        # honored: modifier reassigns the required tier to Should-Fix -> clean.
        check("asp_4e_modifier_honored",
              audit_signal_propagation(_mod_letter, dep_text=_dep_modifier)[0], True)
        # control: SAME letter under the default §4e mapping (no modifier row) -> ERROR
        # (hard gate requires Must-Fix; only Should-Fix present). Proves the modifier —
        # not the letter — changed the required severity.
        check("asp_4e_modifier_control_default_errors",
              audit_signal_propagation(_mod_letter, dep_text=_dep_default)[0], False)
        # malformed: a §4e override directive with an unrecognized synthesis severity
        # is caught (surfaced as an ERROR), not silently defaulted.
        _dep_malformed = _dep_default + (
            "\n| Reception Risk | Alert | ? | ctx | src | "
            "propagate-override: hard-gate → Teleport-Fix |\n")
        check("asp_4e_malformed_row_caught",
              audit_signal_propagation(_mod_letter, dep_text=_dep_malformed)[0], False)
        # malformed default block: a Default-mapping row with an unrecognized severity
        # is likewise caught.
        _dep_bad_default = (
            "#### Default mapping (fallback for un-enumerated audits)\n\n"
            "- Audit-internal Must-Fix floor → Synthesis Must-Fix\n"
            "- Audit-internal hard gate → Synthesis Banana-Fix\n"
            "- Audit-internal HIGH / Alert → Synthesis Must-Fix or Should-Fix\n")
        check("asp_4e_malformed_default_caught",
              audit_signal_propagation(_mod_letter, dep_text=_dep_bad_default)[0], False)

    if which in (None, "author-facing-lint"):
        # Advisory / warn-only: errors must ALWAYS be empty (never gates); warnings
        # flag un-glossed first use of a framework code in the author-facing body.
        bare = ("# Development Edit\n## What Needs Work\n"
                "This is a Pass 11F problem and a QF-7 issue.\n")
        e, w = author_facing_lint(bare)[:2]
        check("afl_never_errors", e, True)             # errors empty -> cannot fail the build
        warns("afl_bare_codes_warn", w, True)          # bare primary-label codes -> warnings
        glossed = ("# Development Edit\n## What Needs Work\n"
                   "The consent-and-reception pass (Pass 11F) flagged weak "
                   "motivation (QF-7).\n")
        warns("afl_glossed_quiet", author_facing_lint(glossed)[1], False)   # glossed first use -> quiet
        appendix_only = ("# Development Edit\n## What Needs Work\nClean prose.\n"
                         "## Appendix B\nMust-Fix QF-7 / Pass 11F tracking.\n")
        warns("afl_appendix_exempt", author_facing_lint(appendix_only)[1], False)  # appendix exempt
        override = ("# Development Edit\n"
                    "<!-- override: author-facing-lint -->\n"
                    "## What Needs Work\nA Pass 11F / QF-7 note.\n")
        warns("afl_override_quiets", author_facing_lint(override)[1], False)  # body override suppresses
        # Codex PR #97 hardening: recognize real inline-definition forms + the [UNCERTAIN] tag.
        emdash = ("# Development Edit\n## What Needs Work\n"
                  "Prose Tier: P1 — strong foundation, weak spine.\n")
        warns("afl_emdash_gloss_quiet", author_facing_lint(emdash)[1], False)  # dash-led gloss -> quiet
        bare_paren = ("# Development Edit\n## What Needs Work\n(Pass 11F) is unresolved.\n")
        warns("afl_bare_paren_warns", author_facing_lint(bare_paren)[1], True)  # bare "(CODE)" not a gloss -> warns
        uncertain = ("# Development Edit\n## What Needs Work\nThe genre signal is [UNCERTAIN].\n")
        warns("afl_uncertain_tag_warns", author_facing_lint(uncertain)[1], True)  # [UNCERTAIN] -> warns
        codes_gloss = ("# Development Edit\n## What Needs Work\nPass 11F (QF-7) is unresolved.\n")
        warns("afl_codes_gloss_codes_warn", author_facing_lint(codes_gloss)[1], True)  # codes glossing codes -> warns

    if which in (None, "synthesis-sections"):
        _ss_full = "".join("## %s\n\nbody\n\n" % h for h in _SYNTHESIS_SECTIONS)
        check("ss_all_headings", synthesis_sections(_ss_full)[0], True)
        _ss_missing = _ss_full.replace("## Stress Test\n\nbody\n\n", "")
        check("ss_missing_heading", synthesis_sections(_ss_missing)[0], False)
        # Subtitled / emphasized canonical forms still satisfy the requirement.
        _ss_subtitled = (_ss_full
                         .replace("## Development Edit\n", "# Development Edit — Worked Example\n")
                         .replace("## Stress Test\n", "## **Stress Test**\n")
                         .replace("## Appendix A\n", "## Appendix A — Diagnostic Detail\n"))
        check("ss_subtitled_headings_ok", synthesis_sections(_ss_subtitled)[0], True)
        # Hardening: the section named only mid-heading (not opening the title) does NOT count.
        _ss_midheading = _ss_full.replace("## Stress Test\n\nbody\n\n",
                                          "## Notes on the Stress Test approach\n\nbody\n\n")
        check("ss_midheading_mention_fails", synthesis_sections(_ss_midheading)[0], False)
        # Hardening: a lookalike prefix (`Appendix Alpha`) does not satisfy `Appendix A`.
        _ss_lookalike = _ss_full.replace("## Appendix A\n\nbody\n\n",
                                         "## Appendix Alpha\n\nbody\n\n")
        check("ss_lookalike_prefix_fails", synthesis_sections(_ss_lookalike)[0], False)

    if which in (None, "tone-check"):
        clean = "# Development Edit\nThe pacing needs work; the voice is distinctive.\n"
        check("tc_clean", tone_check(clean)[0], True)
        superlative = "# Development Edit\nThis is a flawless masterpiece.\n"
        check("tc_body_superlative", tone_check(superlative)[0], False)
        # Hardening: a superlative quoted as evidence in an appendix is not the letter's tone.
        appendix_only = ("# Development Edit\n## What Needs Work\nPacing needs work.\n"
                         "## Appendix A\nThe jacket copy calls it a masterpiece.\n")
        check("tc_appendix_exempt", tone_check(appendix_only)[0], True)
        # Hardening: a superlative inside a code span / fence is documentation, not praise.
        codespan_only = ("# Development Edit\n## What Needs Work\nAvoid words like "
                         "`masterpiece` in the letter.\n")
        check("tc_codespan_exempt", tone_check(codespan_only)[0], True)
        fence_only = ("# Development Edit\n## What Needs Work\nBlocked list:\n"
                      "```\nmasterpiece\nflawless\n```\nProse stays clean.\n")
        check("tc_fence_exempt", tone_check(fence_only)[0], True)
        # Hardening: a `>`-quoted author blurb is quoted external text, not the letter's voice.
        blockquote_only = ("# Development Edit\n## What Needs Work\nPacing needs work.\n"
                           "> The author's blurb calls it a triumph.\n")
        check("tc_blockquote_exempt", tone_check(blockquote_only)[0], True)

    if which in (None, "ledger-check"):
        _sect = ("### Notable Findings\nx\n### Data Artifacts for Letter Reference\nx\n"
                 "### Cross-Pass Connections\nx\n### Unresolved Questions\nx\n"
                 "### Audit Triggers\nx\n")
        check_rc("lc_complete_pass", ledger_check("## Pass 5 — Character\n" + _sect)[0], True)
        check_rc("lc_missing_section",
                 ledger_check("## Pass 5 — Character\n### Notable Findings\nx\n"
                              "### Cross-Pass Connections\nx\n### Unresolved Questions\nx\n"
                              "### Audit Triggers\nx\n")[0], False)
        check_rc("lc_pass0_lenient",
                 ledger_check("## Pass 0 — Structure\n### Notable Findings\nx\n")[0], True)
        check_rc("lc_pass10_lenient",
                 ledger_check("## Pass 10 — Timeline\n### Notable Findings\nx\n")[0], True)
        check_rc("lc_no_passes", ledger_check("# Ledger\nno passes here\n")[0], False)
        # Hardening: a required subsection named only in mid-line prose (not a `### ` heading)
        # does NOT satisfy the requirement; the anchored heading match catches the miss.
        _prose = ("## Pass 5 — Character\n### Notable Findings\nx\n"
                  "### Data Artifacts for Letter Reference\nx\n### Cross-Pass Connections\nx\n"
                  "### Unresolved Questions\nx\nSee the ### Audit Triggers list below.\n")
        check_rc("lc_prose_pseudo_heading_fails", ledger_check(_prose)[0], False)

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
            if chk in RAW_CHECKS:
                check_rc("fixture:%s" % name, RAW_CHECKS[chk](txt)[0], ".pass." in name)
            else:
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
    if argv[1] == "check-registry":
        if len(argv) < 4:
            sys.stderr.write("Usage: letter_checks.py check-registry <registry_file> <pass_deps_file>\n")
            return 2
        return check_registry(argv[2], argv[3])
    if argv[1] in CHECKS:
        if len(argv) < 3:
            sys.stderr.write("Usage: letter_checks.py %s <file> [<ledger_file>]\n" % argv[1])
            return 2
        return run_check(argv[1], argv[2], argv[3] if len(argv) > 3 else None)
    if argv[1] in RAW_CHECKS:
        if len(argv) < 3:
            sys.stderr.write("Usage: letter_checks.py %s <file>\n" % argv[1])
            return 2
        return run_raw_check(argv[1], argv[2])
    sys.stderr.write("Error: unknown command: %s\n" % argv[1])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
