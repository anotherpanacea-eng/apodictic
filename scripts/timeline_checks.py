#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real parser + verifier for the Pass 10 Timeline artifact (validate.sh timeline-* arms).

Implements the Phase 7 Timeline parser deferred in core-editor/references/pass-10.md
§Phase 7 Work Items:

  * timeline-diff            — structural diff (Section 1 Event Ledger rows + Section 3
                               Temporal Marker bullets) vs Section 8 Diff Notes coverage.
                               Faithful re-implementation of the bash arm.
  * timeline-arithmetic      — marker hygiene (negative gaps, pre-labeled conflicts) PLUS
                               TRUE arithmetic: a scene's computed end must not overrun the
                               next scene's computed start (unless flagged flashback/concurrent).
  * timeline-anchor-conflict — pre-labeled conflict surfacing PLUS TRUE anchor-drift: the same
                               Scene ID resolved to two different absolute day anchors.

The arithmetic / anchor-drift detection is deliberately conservative: it only fires on rows
whose anchors normalize to a (day, time-of-day) / day number with HIGH/MEDIUM confidence and
that are not marked flashback / concurrent / ambiguous. Unparseable, LOW/UNCERTAIN, or
flashback rows are exempt — the model still owns the judgment for those.

CLI (called by validate.sh; degrades to the bash implementation when python3 is absent):
    timeline_checks.py timeline-diff <prior> <current>
    timeline_checks.py timeline-arithmetic <timeline>
    timeline_checks.py timeline-anchor-conflict <timeline>
    timeline_checks.py --self-test [<check-name>]

Output contract: WARN: / ERROR: / OK: line prefixes + exit code (0 ok, 1 fail, 2 usage),
matching the bash arms so callers and the release gate are unaffected.
"""

import os
import re
import sys

# Time-of-day word -> hour-of-day. Order matters for substring precedence
# (check "late night" / "midnight" before "night", "midday" before "day").
_TOD_WORDS = [
    ("midnight", 0.0), ("dawn", 6.0), ("early morning", 6.0), ("morning", 8.0),
    ("midday", 12.0), ("noon", 12.0), ("midafternoon", 15.0), ("afternoon", 14.0),
    ("evening", 19.0), ("dusk", 20.0), ("late night", 23.0), ("night", 22.0),
]

# Duration unit -> hours.
_UNIT_HOURS = {
    "minute": 1.0 / 60.0, "min": 1.0 / 60.0, "hour": 1.0, "hr": 1.0,
    "day": 24.0, "week": 168.0, "month": 720.0, "year": 8760.0,
}

# Anchors carrying these tokens are exempt from arithmetic-overrun checks
# (legitimate non-linear structure the model owns).
_NONLINEAR_RE = re.compile(
    r"(flashback|flash-forward|flashforward|concurrent|simultaneous|meanwhile|"
    r"dream|POV[- ]split|out of order|nonlinear|non-linear)", re.IGNORECASE)

_LEVEL2_RE = re.compile(r"^##[^#]")

# Code spans (fenced ``` ``` and inline ` `) are stripped before an override scan so a documentation
# EXAMPLE of a marker (in backticks) is not mistaken for a live override.
_CODE_SPAN_RE = re.compile(r"```.*?```|`[^`\n]*`", re.DOTALL)


def _has_override(body, slug):
    """A genuine body override comment for `slug` — NOT a suffixed slug, NOT inside a code span.

    The earlier `"<!-- override: <slug>" in body` substring test matched a suffixed slug (e.g.
    `<slug>-but-not-really`) and matched a backtick'd documentation example. This requires the EXACT
    slug followed by a delimiter (whitespace / em- or en-dash / the comment close), in stripped prose.
    """
    region = _CODE_SPAN_RE.sub(" ", body or "")
    return re.search(r"<!--\s*override:\s*" + re.escape(slug) + r"(?=\s|—|–|-->|$)", region) is not None


# --------------------------------------------------------------------------
# Shared parsing helpers.
# --------------------------------------------------------------------------

def _content_lines(text):
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return lines


def _split_section8(text):
    """Return (body, section8) split at the first 'Section 8' heading (1-based,
    Section 8 inclusive). Section 8 is the appendix-equivalent — markers there are
    non-canonical, mirroring the bash arms."""
    lines = _content_lines(text)
    s8 = None
    rx = re.compile(r"^#{1,4}.*Section 8", re.IGNORECASE)
    for i, ln in enumerate(lines):
        if rx.search(ln):
            s8 = i
            break
    if s8 is None:
        return "\n".join(lines), ""
    return "\n".join(lines[:s8]), "\n".join(lines[s8:])


# Number parsing tolerant of comma thousands-separators. The bare `\d+`/`\d` digit runs below used to
# drop the leading groups under `.search()` — "1,000 days" -> 0.0, "Day 1,000" -> 1 — a false POSITIVE
# on a self-consistent timeline and a false NEGATIVE on a real conflict (the same blind spot fixed in
# world_bible.py, PR #135). The grouped alternative requires AT LEAST ONE ",ddd" group (`+`, not `*`)
# so an ungrouped multi-digit number can't be prefix-matched ("1000" stays "1000", never "100").
# Commas are stripped via _strip_grouping before float()/int().
_NUM_UNIT_RE = re.compile(r"(-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+(?:\.\d+)?)\s*([A-Za-z]+)")
_ANCHOR_NUM = r"(\d{1,3}(?:,\d{3})+|\d+)"
_ANCHOR_DAY_RE = re.compile(r"\bDay\s+" + _ANCHOR_NUM, re.IGNORECASE)
_ANCHOR_WEEK_RE = re.compile(r"\bWeek\s+" + _ANCHOR_NUM, re.IGNORECASE)


def _strip_grouping(num):
    """Drop comma thousands-separators from a captured numeral so float()/int() see the real
    magnitude ('1,000' -> '1000'). Comma is the only grouping char authors use here; '.' is the
    decimal point and is preserved."""
    return num.replace(",", "")


def _norm_duration(s):
    """'3 hours' -> 3.0, '2 days' -> 48.0, '30 minutes' -> 0.5, '-2 days' -> -48.0;
    None for 'n/a' / empty / unparseable. Comma-grouped counts ('1,000 days') parse correctly."""
    if s is None:
        return None
    m = _NUM_UNIT_RE.search(s)
    if not m:
        return None
    value = float(_strip_grouping(m.group(1)))
    unit = m.group(2).lower().rstrip("s")
    if unit not in _UNIT_HOURS:
        return None
    return value * _UNIT_HOURS[unit]


def _norm_anchor_day(*texts):
    """Best-effort absolute day number from any of the given anchor texts.
    Recognizes 'Day N' and 'Week M' (-> day (M-1)*7+1). Returns int or None."""
    for t in texts:
        if not t:
            continue
        m = _ANCHOR_DAY_RE.search(t)
        if m:
            return int(_strip_grouping(m.group(1)))
    for t in texts:
        if not t:
            continue
        m = _ANCHOR_WEEK_RE.search(t)
        if m:
            return (int(_strip_grouping(m.group(1))) - 1) * 7 + 1
    return None


def _norm_anchor_tod(*texts):
    """Best-effort hour-of-day from anchor texts: a time-of-day word or explicit
    clock time ('14:30', '2pm', '9 am'). Returns float hours or None."""
    for t in texts:
        if not t:
            continue
        m = re.search(r"\b(\d{1,2}):(\d{2})\b", t)
        if m:
            return int(m.group(1)) + int(m.group(2)) / 60.0
        m = re.search(r"\b(\d{1,2})\s*([ap])\.?m\.?\b", t, re.IGNORECASE)
        if m:
            h = int(m.group(1)) % 12
            if m.group(2).lower() == "p":
                h += 12
            return float(h)
        low = t.lower()
        # Word-boundary match, not substring: "noon" must not match inside "afternoon"
        # (and "morning" not inside a longer token). Order still resolves "early morning"
        # before "morning" and "late night" before "night".
        for word, hour in _TOD_WORDS:
            if re.search(r"\b" + re.escape(word) + r"\b", low):
                return hour
    return None


def _confidence_ok(conf):
    """Arithmetic fires only on HIGH/MEDIUM (or unstated) confidence rows; LOW/UNCERTAIN
    rows are exempt (the model flagged them as not firm)."""
    if not conf:
        return True
    c = conf.strip().upper()
    return c not in ("LOW", "UNCERTAIN")


def _parse_event_ledger(text):
    """Parse pipe-table rows whose header contains 'Scene ID' into dicts keyed by
    normalized column name. Returns a list of row dicts (in document order)."""
    rows = []
    header = None
    for ln in text.split("\n"):
        if not ln.lstrip().startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if re.match(r"^\|?\s*:?-{3,}", ln.strip()) or all(set(c) <= set("-: ") for c in cells):
            continue  # alignment row
        low = [c.lower() for c in cells]
        if any("scene id" in c for c in low):
            header = low
            continue
        if header is None:
            continue
        row = {}
        for i, c in enumerate(cells):
            if i < len(header):
                row[header[i]] = c
        rows.append(row)
    return rows


def _row_get(row, *needles):
    for key, val in row.items():
        for n in needles:
            if n in key:
                return val
    return None


def _parse_section3_anchors(text):
    """Map Scene ID -> set of distinct day numbers from Section 3 bullets like
    '- Ch 1 §1: "Monday morning" -> Day 1' and from the Event Ledger."""
    by_scene = {}

    def add(scene, day):
        if scene and day is not None:
            by_scene.setdefault(scene.strip(), set()).add(day)

    in_s3 = False
    for ln in text.split("\n"):
        if re.match(r"^##\s+.*Section 3", ln, re.IGNORECASE):
            in_s3 = True
            continue
        if _LEVEL2_RE.match(ln):
            in_s3 = False
        if in_s3 and ln.lstrip().startswith("- "):
            m = re.match(r"^\s*-\s*([^:]+):", ln)
            if m:
                add(m.group(1), _norm_anchor_day(ln))
    for row in _parse_event_ledger(text):
        # Honor the contract: LOW/UNCERTAIN Event Ledger rows are exempt from drift,
        # parallel to the arithmetic check (an explicitly uncertain guess must not become
        # a hard validator failure). Section 3 markers carry no confidence field, so they
        # are always counted.
        if not _confidence_ok(_row_get(row, "confidence")):
            continue
        scene = _row_get(row, "scene id")
        add(scene, _norm_anchor_day(_row_get(row, "calculated date"),
                                    _row_get(row, "anchor")))
    return by_scene


# --------------------------------------------------------------------------
# Checks. Each returns (errors, warnings, ok_line, failed_line).
# --------------------------------------------------------------------------

_PASS10 = "core-editor/references/pass-10.md"


def timeline_arithmetic(text):
    errors, warnings = [], []
    body, _ = _split_section8(text)
    ov = _has_override(body, "timeline-arithmetic-conflict")

    # Marker hygiene (faithful to the bash arm) — body only.
    neg_gaps = sum(1 for ln in body.split("\n")
                   if re.search(r"\|\s*-[0-9]+\s*(hours?|days?|minutes?|weeks?|months?|years?)",
                                ln, re.IGNORECASE))
    conflict_markers = sum(1 for ln in body.split("\n")
                           if re.search(r"\|.*\((conflicts|contradicts)", ln, re.IGNORECASE))

    # True arithmetic: a scene's computed end must not overrun the next scene's
    # computed start, unless the next scene is flagged non-linear.
    overruns = 0
    rows = _parse_event_ledger(body)
    parsed = []
    for row in rows:
        day = _norm_anchor_day(_row_get(row, "calculated date"), _row_get(row, "anchor"))
        tod = _norm_anchor_tod(_row_get(row, "calculated time"), _row_get(row, "anchor"))
        span = _norm_duration(_row_get(row, "span"))
        conf_ok = _confidence_ok(_row_get(row, "confidence"))
        anchor_txt = " ".join(filter(None, [_row_get(row, "anchor"),
                                            _row_get(row, "calculated date")]))
        nonlinear = bool(_NONLINEAR_RE.search(anchor_txt))
        start = day * 24.0 + tod if (day is not None and tod is not None) else None
        parsed.append({"start": start, "span": span, "conf_ok": conf_ok, "nonlinear": nonlinear})
    for i in range(1, len(parsed)):
        prev, cur = parsed[i - 1], parsed[i]
        # Exempt the pair if EITHER side is non-linear (a flashback/concurrent row is
        # exempt whether it is the current row or the predecessor used for overrun math)
        # or either side is LOW/UNCERTAIN confidence.
        if (cur["nonlinear"] or prev["nonlinear"]
                or not cur["conf_ok"] or not prev["conf_ok"]):
            continue
        if prev["start"] is None or cur["start"] is None or prev["span"] is None:
            continue
        if cur["start"] < prev["start"] + prev["span"] - 1e-9:
            overruns += 1

    total = neg_gaps + conflict_markers + overruns
    if total == 0:
        return [], [], ("OK: Timeline arithmetic consistent (no negative gaps, no pre-labeled "
                        "conflicts, no span overruns)."), ""
    detail = ("%d negative gap(s); %d pre-labeled conflict(s); %d computed span overrun(s)"
              % (neg_gaps, conflict_markers, overruns))
    if ov:
        warnings.append("WARN: %d timeline-arithmetic candidate(s) detected (%s); body override "
                        "marker present." % (total, detail))
    else:
        errors.append("ERROR: %d timeline-arithmetic candidate(s) surfaced (%s). Surface each in "
                      "Section 4 (Inconsistency Ledger), correct the spans/anchors, or place a body "
                      "override marker <!-- override: timeline-arithmetic-conflict — <reason> --> "
                      "above Section 8. Canonical home: %s §Section 4." % (total, detail, _PASS10))
    return errors, warnings, "", ("FAILED: timeline-arithmetic — %s." % detail)


def timeline_anchor_conflict(text):
    errors, warnings = [], []
    body, _ = _split_section8(text)
    ov = _has_override(body, "timeline-anchor-conflict")

    candidates = sum(1 for ln in body.split("\n")
                     if re.search(r"\((contradicts|paradox with|conflicts with)", ln, re.IGNORECASE))

    drift = 0
    drift_scenes = []
    for scene, days in _parse_section3_anchors(body).items():
        if len(days) >= 2:
            drift += 1
            drift_scenes.append("%s -> Day %s" % (scene, "/".join(str(d) for d in sorted(days))))

    total = candidates + drift
    if total == 0:
        return [], [], "OK: No anchor conflicts (no pre-labeled candidates, no same-scene anchor drift).", ""
    detail = "%d pre-labeled candidate(s); %d same-scene anchor drift(s)" % (candidates, drift)
    if drift_scenes:
        detail += " [" + "; ".join(drift_scenes) + "]"
    if ov:
        warnings.append("WARN: %d anchor-conflict candidate(s) surfaced (%s); body override "
                        "marker present." % (total, detail))
    else:
        errors.append("ERROR: %d anchor-conflict candidate(s) surfaced (%s). Classify each in "
                      "Section 4 (Inconsistency Ledger), reconcile the anchors, or place a body "
                      "override marker <!-- override: timeline-anchor-conflict — <reason> --> above "
                      "Section 8. Canonical home: %s §Section 4." % (total, detail, _PASS10))
    return errors, warnings, "", ("FAILED: timeline-anchor-conflict — %s." % detail)


def _diff_event_rows(text):
    out = set()
    for ln in text.split("\n"):
        if not ln.startswith("|"):
            continue
        if re.match(r"^\|\s*---", ln) or re.match(r"^\|\s*Scene ID", ln):
            continue
        out.add(ln)
    return out


def _diff_section3_markers(text):
    out, in_s3 = set(), False
    for ln in text.split("\n"):
        if re.match(r"^##\s+.*Section 3", ln):
            in_s3 = True
            continue
        if re.match(r"^##\s", ln):
            in_s3 = False
        if in_s3 and ln.startswith("- "):
            out.add(ln)
    return out


def timeline_diff(prior_text, current_text):
    errors, warnings = [], []
    body, section8 = _split_section8(current_text)
    ov = _has_override(body, "timeline-diff-undocumented")

    prior_rows, cur_rows = _diff_event_rows(prior_text), _diff_event_rows(current_text)
    prior_s3, cur_s3 = _diff_section3_markers(prior_text), _diff_section3_markers(current_text)
    added = len(cur_rows - prior_rows)
    removed = len(prior_rows - cur_rows)
    s3_added = len(cur_s3 - prior_s3)
    s3_removed = len(prior_s3 - cur_s3)
    diff_total = added + removed + s3_added + s3_removed
    exp_added, exp_removed = added + s3_added, removed + s3_removed

    ok_summary = ("OK: No structural diff between prior and current Timeline (Section 1 + "
                  "Section 3 checked).")
    if diff_total == 0:
        return [], [], ok_summary, ""

    counts = ("%d change(s); §1: %d added, %d removed; §3: %d added, %d removed"
              % (diff_total, added, removed, s3_added, s3_removed))
    # Coverage gate (per diff class). Section 8 must actually cover the structural diff:
    # added rows need 'Added'/'Anchors added' bullets, removed rows need 'Removed'/'Anchors
    # removed'. A row *edit* shows up in the line-level structural diff as one added + one
    # removed line, so a 'Changed'/'Anchors changed'/'Calculations changed' bullet documents
    # one add+remove pair. Generic 'Changed' text can no longer mask a pure addition or
    # removal (a 'Changed' bullet only offsets a matched add/remove pair).
    s8 = section8.split("\n")
    doc_added = sum(1 for ln in s8
                    if re.match(r"^[-*]\s+(Added|Events? added|Anchors? added)", ln, re.IGNORECASE))
    doc_removed = sum(1 for ln in s8
                      if re.match(r"^[-*]\s+(Removed|Events? removed|Anchors? removed)", ln, re.IGNORECASE))
    doc_changed = sum(1 for ln in s8
                      if re.match(r"^[-*]\s+(Changed|Events? changed|Anchors? changed|"
                                  r"Calculations? changed)", ln, re.IGNORECASE))
    changed_applied = min(doc_changed, min(exp_added, exp_removed))  # edit pairs
    need_added = exp_added - changed_applied
    need_removed = exp_removed - changed_applied
    if doc_added >= need_added and doc_removed >= need_removed:
        return [], [], "OK: Diff detected (%s) and documented in Section 8." % counts, ""

    msg = ("Section 8 documentation does not cover the structural diff: need %d added / %d "
           "removed bullet(s) (have %d added, %d removed, %d changed) for §1+§3 totals "
           "%d added / %d removed"
           % (need_added, need_removed, doc_added, doc_removed, doc_changed, exp_added, exp_removed))
    if ov:
        warnings.append("WARN: %s; body override marker present." % msg)
        return errors, warnings, "OK: override (under-documented diff).", ""
    errors.append("ERROR: %s. Document each class in Section 8 (added rows need 'Added', removed "
                  "rows need 'Removed', a row edit may be one 'Changed'), or place a body override "
                  "marker <!-- override: timeline-diff-undocumented — <reason> --> above Section 8. "
                  "Canonical home: %s §Section 8." % (msg, _PASS10))
    return errors, warnings, "", ("FAILED: timeline-diff — %s." % msg)


SINGLE_FILE_CHECKS = {
    "timeline-arithmetic": timeline_arithmetic,
    "timeline-anchor-conflict": timeline_anchor_conflict,
}


def _emit(errors, warnings, ok_line, failed_line):
    for w in warnings:
        print(w)
    for e in errors:
        print(e)
    if errors:
        if failed_line:
            print("")
            print(failed_line)
        return 1
    if ok_line:
        print(ok_line)
    return 0


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


# --------------------------------------------------------------------------
# Self-test.
# --------------------------------------------------------------------------

def _fixture_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (os.path.join(here, "test_fixtures"),
                 os.path.join(here, "..", "..", "..", "plugins", "apodictic",
                              "scripts", "test_fixtures")):
        if os.path.isdir(cand):
            return cand
    return os.path.join(here, "test_fixtures")


def run_self_test(which=None):
    rc = {"v": 0}

    def expect(name, got, want):
        if got == want:
            print("  %s: OK" % name)
        else:
            print("  %s: FAIL (got %s, expected %s)" % (name, got, want))
            rc["v"] = 1

    # Single-file fixtures: tl.<pass|fail>.<check>.<name>.md
    fdir = _fixture_dir()
    if os.path.isdir(fdir):
        for fn in sorted(os.listdir(fdir)):
            if not fn.startswith("tl.") or not fn.endswith(".md"):
                continue
            parts = fn.split(".")
            chk = parts[2] if len(parts) > 3 else ""
            if chk not in SINGLE_FILE_CHECKS:
                continue
            if which not in (None, chk):
                continue
            errs = SINGLE_FILE_CHECKS[chk](_read(os.path.join(fdir, fn)))[0]
            want_clean = parts[1] == "pass"
            expect("fixture:%s" % fn, len(errs) == 0, want_clean)

    # timeline-diff: in-code prior/current pairs (two-file check).
    if which in (None, "timeline-diff"):
        import tempfile
        prior = ("# Timeline\n## Section 1: Event Ledger\n| Scene ID | Anchor text | Span |\n"
                 "|---|---|---|\n| Ch 1 §1 | Monday morning | 3 hours |\n"
                 "| Ch 1 §2 | Tuesday afternoon | 2 hours |\n## Section 8: Diff Notes\nn/a.\n")
        cur_same = prior.replace("n/a.", "n/a — no changes.")
        added_row = "| Ch 2 §1 | Wednesday morning | 1 hour |\n## Section 8: Diff Notes\n"
        cur_undoc = prior.replace("## Section 8: Diff Notes\n", added_row).replace("n/a.", "n/a — no changes.")
        cur_doc = prior.replace("## Section 8: Diff Notes\n", added_row).replace(
            "n/a.", "- Added: Ch 2 §1 (Wednesday morning) — new scene.")
        cur_over = ("# Timeline\n<!-- override: timeline-diff-undocumented — deferred. -->\n"
                    + prior.split("\n", 1)[1].replace("## Section 8: Diff Notes\n", added_row).replace(
                        "n/a.", "n/a — no changes."))

        def diff_rc(p, c):
            with tempfile.TemporaryDirectory() as td:
                pp = os.path.join(td, "p.md"); open(pp, "w", encoding="utf-8", newline="").write(p)
                cc = os.path.join(td, "c.md"); open(cc, "w", encoding="utf-8", newline="").write(c)
                return _emit(*timeline_diff(_read(pp), _read(cc)))
        # Generic 'Changed' text must NOT cover a pure addition (review fix).
        cur_changed_masks = prior.replace("## Section 8: Diff Notes\n", added_row).replace(
            "n/a.", "- Changed: refreshed timeline wording only.")
        # A genuine row edit (span 2h->3h = one added + one removed line) IS covered by
        # a single 'Changed' bullet.
        cur_edit = prior.replace("| Ch 1 §2 | Tuesday afternoon | 2 hours |",
                                 "| Ch 1 §2 | Tuesday afternoon | 3 hours |").replace(
            "n/a.", "- Changed: Ch 1 §2 span 2h->3h.")
        expect("diff_no_change", diff_rc(prior, cur_same), 0)
        expect("diff_undocumented", diff_rc(prior, cur_undoc), 1)
        expect("diff_documented", diff_rc(prior, cur_doc), 0)
        expect("diff_override_body", diff_rc(prior, cur_over), 0)
        # 2026-06-20 override-parse hardening: a SUFFIXED slug must NOT be accepted as the override
        cur_over_suffixed = cur_over.replace("timeline-diff-undocumented —", "timeline-diff-undocumented-later —")
        expect("diff_override_suffixed_slug_rejected", diff_rc(prior, cur_over_suffixed), 1)
        # a marker inside a backtick code span (a documentation example) must NOT count as a live override
        cur_over_backtick = cur_over.replace(
            "<!-- override: timeline-diff-undocumented — deferred. -->",
            "Use `<!-- override: timeline-diff-undocumented -->` to defer.")
        expect("diff_override_in_backticks_rejected", diff_rc(prior, cur_over_backtick), 1)
        expect("diff_changed_masks_add", diff_rc(prior, cur_changed_masks), 1)
        expect("diff_edit_changed_covers", diff_rc(prior, cur_edit), 0)

    # Comma thousands-separator parsing — the same blind spot fixed in world_bible.py (#135) lived
    # in this validator too. Each assertion below FAILS against pre-fix code.
    if which in (None, "timeline-arithmetic", "timeline-anchor-conflict"):
        # Unit: grouped numerals parse to full magnitude; ungrouped multi-digit numbers are UNCHANGED
        # (the grouped alternative requires a comma, so "1000" never prefix-matches down to 100).
        expect("comma_duration_thousands", _norm_duration("1,000 days"), 1000 * 24.0)   # pre-fix: 0.0
        expect("comma_duration_ungrouped_unchanged", _norm_duration("1000 days"), 1000 * 24.0)
        expect("comma_anchor_day", _norm_anchor_day("Day 1,000"), 1000)                 # pre-fix: 1
        expect("comma_anchor_week", _norm_anchor_day("Week 1,000"), (1000 - 1) * 7 + 1) # pre-fix: 1
        expect("comma_anchor_ungrouped_unchanged", _norm_anchor_day("Day 1000"), 1000)
        # Arm-level: an agree-clean timeline must NOT flag (pre-fix: false POSITIVE) and a genuine
        # conflict MUST flag (pre-fix: false NEGATIVE).
        anchor_clean = ('# Timeline\n## Section 3: Scene Anchors\n'
                        '- Ch 2 §1: "the thousandth dawn" -> Day 1,000\n'
                        '- Ch 2 §1: "a thousand days in" -> Day 1000\n')          # same day, comma vs not
        anchor_conflict = ('# Timeline\n## Section 3: Scene Anchors\n'
                           '- Ch 3 §2: "the thousandth dawn" -> Day 1,000\n'
                           '- Ch 3 §2: "five days later, same scene" -> Day 1,005\n')  # genuinely different days
        expect("anchor_comma_consistent_clean", _emit(*timeline_anchor_conflict(anchor_clean)), 0)
        expect("anchor_comma_conflict_flagged", _emit(*timeline_anchor_conflict(anchor_conflict)), 1)
        _tbl = ("# Timeline\n## Section 1: Event Ledger\n"
                "| Scene ID | Anchor text | Span |\n|---|---|---|\n")
        arith_clean = _tbl + ("| Ch 1 §1 | Day 1,000 0:00 | 10 hours |\n"
                              "| Ch 1 §2 | Day 1,001 0:00 | 1 hour |\n")   # sequential days, no overrun
        arith_conflict = _tbl + ("| Ch 1 §1 | Day 1 0:00 | 1,000 hours |\n"
                                 "| Ch 1 §2 | Day 2 0:00 | 1 hour |\n")    # 1,000h span overruns Day 2
        expect("arith_comma_anchor_sequential_clean", _emit(*timeline_arithmetic(arith_clean)), 0)
        expect("arith_comma_span_overrun_flagged", _emit(*timeline_arithmetic(arith_conflict)), 1)

    if rc["v"] == 0:
        print("Self-test: PASS")
    else:
        print("Self-test: FAIL")
    return rc["v"]


def main(argv):
    if len(argv) < 2:
        sys.stderr.write("Usage: timeline_checks.py <timeline-diff|timeline-arithmetic|"
                         "timeline-anchor-conflict|--self-test> ...\n")
        return 2
    if argv[1] == "--self-test":
        return run_self_test(argv[2] if len(argv) > 2 else None)
    if argv[1] == "timeline-diff":
        if len(argv) < 4:
            sys.stderr.write("Usage: timeline_checks.py timeline-diff <prior> <current>\n")
            return 2
        for p in (argv[2], argv[3]):
            if not os.path.isfile(p):
                sys.stderr.write("Error: File not found: %s\n" % p)
                return 2
        return _emit(*timeline_diff(_read(argv[2]), _read(argv[3])))
    if argv[1] in SINGLE_FILE_CHECKS:
        if len(argv) < 3:
            sys.stderr.write("Usage: timeline_checks.py %s <timeline>\n" % argv[1])
            return 2
        if not os.path.isfile(argv[2]):
            sys.stderr.write("Error: File not found: %s\n" % argv[2])
            return 2
        return _emit(*SINGLE_FILE_CHECKS[argv[1]](_read(argv[2])))
    sys.stderr.write("Error: unknown command: %s\n" % argv[1])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
