#!/usr/bin/env python3
"""continuity-bible — structural integrity for the Auto-Derived Continuity Bible.

`validate.sh continuity-bible <run_folder|files>` shells out here. The Continuity Bible is the
narrative half of a developmental-edit style sheet: a single, locus-anchored reference of the
canonical facts the manuscript commits to — identity/physical facts (ages, spellings, aliases),
named objects, place details — plus consolidated chronology, and (as a side effect) a ledger of
the places the text commits to two facts at once. Each fact is an apodictic.canon_fact.v1 block;
this validator owns the Bible's contract and the consume-don't-duplicate boundary.

The module firewall is *extract the stated, never author the unstated*: a Bible records what the
text asserts and SURFACES contradictions (both values), it never infers, fills a gap, or picks a
winner. Locus PRESENCE/SHAPE is gated (C2); locus RESOLUTION into the manuscript is deferred to
the shared snapshot layer, so the firewall here is author/QA-enforced, not yet mechanically proven.

  C1 schema           a canon_fact block fails its schema (bad category enum, malformed CF-NN id,
                      missing required field, unquoted-numeric value, empty loci, broken JSON).
  C2 locus shape      a fact carries a locus that is empty or not a coarse locus (no chapter /
                      §section / ¶ / line / page token). A well-formedness precondition, NOT a
                      firewall proof — it cannot detect a fabricated-but-well-shaped locus.
  C3 contradiction    a `## Contradiction Ledger` row that does not pair >=2 real canon_fact ids
                      sharing entity+attribute but asserting DIFFERENT values (a row that names an
                      unknown id, names facts on different entity/attribute, or names facts that
                      agree, is not a real contradiction). Bespoke markdown-table parse.
  C4 chronology       a `chronology` fact that does not consolidate to a real Timeline scene id —
     consume         i.e. re-derives a temporal fact the Timeline already owns. Scoped to
                      chronology<->Timeline (only the Timeline has addressable ids). Advisory; ERROR
                      under --strict. Override (per id):
                      <!-- override: bible-rederive CF-NN — <rationale, e.g. no Timeline run> -->.
  W1 coverage         a Timeline POV character has no Cast (person) entry, or a Timeline setting has
                      no Places (place) entry — a continuity gap. Advisory; ERROR under --strict.
                      (Increment 1 sources character coverage from the Timeline POV column — the
                      machine-readable name source — not the prose Pass-5 portraits.)

`value` is always a string (numerics are quoted) so C1 can type-check it. Contradictions are
surfaced, never resolved. Reuses apodictic_artifacts (block grammar + schema engine). The Timeline
is an optional second input; without it C4 cannot confirm scene ids and W1 is skipped.
See docs/continuity-bible.md.

  continuity_bible.py continuity-bible <run_folder|files...> [--strict]
  continuity_bible.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import os
import re
import sys

from override_marker import override_targets  # SSoT: code-span-stripped, boundary-matched override scan

try:
    import apodictic_artifacts as art
except ImportError:
    art = None


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (a parsed carrier, not a prose mention).

    Classifying on parsed blocks — not a raw substring — keeps a file that merely *names* the marker
    in prose from being misrouted/skipped (the 2026-06-20 resolver-hardening sweep). Gated by
    validate.sh validator-conventions (M2)."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))

_SCHEMA_ID = "apodictic.canon_fact.v1"
_BIBLE_GLOB = "*_Continuity_Bible_*.md"

# C2 — a coarse locus shape: a chapter / §section / ¶ / line / page / paragraph token. Rejects
# empty strings and obvious non-loci ("the kitchen"). NOT a firewall proof — a fabricated but
# well-shaped locus ("Ch 9 ¶4") passes; locus RESOLUTION is the deferred snapshot increment.
_LOCUS_RE = re.compile(
    r"\bch(?:apter)?\.?\s*\d+"          # Ch 9 / Chapter 9 / Ch. 9
    r"|§"                                # §section
    r"|¶"                                # ¶paragraph
    r"|\blines?\s+\d+"                   # line 42 / lines 42
    r"|\bp(?:g|ag\.?|\.)?\s*\d+"         # p. 40 / pg 40 / p40
    r"|\bpara(?:graph)?\.?\s*\d+",       # paragraph 4 / para. 4
    re.IGNORECASE)
# CF ids referenced inside a Contradiction-Ledger row.
_CF_REF_RE = re.compile(r"\bCF-[0-9]+\b")
# Override markers naming a fact id ("<!-- override: bible-rederive CF-08 — ... -->") route through
# the shared override_marker SSoT — code spans stripped, slug boundary-matched.


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _overrides(text, slug):
    """The set of CF-NN ids overridden for `slug` — via the shared SSoT, so a marker quoted inside a
    code span is not honored as a live directive."""
    return {t[0] for t in override_targets(text, slug, r"(CF-[0-9]+)")}


def parse_facts(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:canon_fact block."""
    facts = []
    if not text or art is None:
        return facts
    schema = art.load_schema(_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "canon_fact":
            continue
        idx += 1
        where = "canon_fact #%d" % idx
        if jerr:
            facts.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        facts.append((obj, art.validate_obj(obj, schema, where), idx))
    return facts


# ------------------------------------------------------- Timeline (optional) parsing

def _event_ledger_rows(text):
    """Parse the Event-Ledger pipe table (header contains 'Scene ID') into row dicts keyed by
    lowercased column name. Mirrors timeline_checks._parse_event_ledger; kept local so the Bible
    validator self-tests in isolation."""
    rows, header = [], None
    for ln in (text or "").split("\n"):
        if not ln.lstrip().startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue  # alignment row
        low = [c.lower() for c in cells]
        if any("scene id" in c for c in low):
            header = low
            continue
        if header is None:
            continue
        rows.append({header[i]: c for i, c in enumerate(cells) if i < len(header)})
    return rows


def _col(row, *needles):
    for key, val in row.items():
        if any(n in key for n in needles):
            return val
    return None


def timeline_facts(text):
    """(scene_ids, povs, settings) from a Timeline Event Ledger, or (None, set, set) if absent."""
    rows = _event_ledger_rows(text)
    if not rows:
        return None, set(), set()
    scene_ids, povs, settings = set(), set(), set()
    for row in rows:
        sid = _col(row, "scene id")
        if sid and sid.lower() not in ("", "n/a"):
            scene_ids.add(sid.strip())
        pov = _col(row, "pov")
        if pov and pov.lower() not in ("", "n/a"):
            povs.add(pov.strip())
        setting = _col(row, "setting")
        if setting and setting.lower() not in ("", "n/a"):
            settings.add(setting.strip())
    return scene_ids, povs, settings


# ------------------------------------------------------- Contradiction Ledger parsing

def contradiction_rows(text):
    """List of [CF-id, ...] (in row order) for each data row under '## Contradiction Ledger'.
    Bespoke markdown-table parse — the ledger is plain markdown, not an apodictic:* block."""
    out, in_section = [], False
    for ln in (text or "").split("\n"):
        if re.match(r"^##\s+.*Contradiction\s+Ledger", ln, re.IGNORECASE):
            in_section = True
            continue
        if in_section and re.match(r"^##\s", ln):
            break  # next section ends the ledger
        if not in_section or not ln.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue  # alignment row
        if any("entity" in c.lower() and "attribute" in " ".join(cells).lower() for c in cells):
            continue  # header row (has Entity + Attribute column labels)
        # Append EVERY data row's refs, even an empty list: skipping zero-ref rows let a real row
        # like `| Mara | age | unresolved |` vanish from validation so the Bible PASSed. Emitting []
        # lets the C3 `len(uniq) < 2` guard reject it (Codex P1).
        out.append(_CF_REF_RE.findall(ln))
    return out


# ------------------------------------------------------- the checks

def bible(text, timeline_text=None, strict=False):
    """Run the Continuity Bible integrity checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    facts = parse_facts(text)
    if not facts:
        return 0, ["continuity-bible: no canon_fact blocks found — nothing to check"]

    # C1 — schema / JSON validity (per block)
    for _obj, schema_errs, _idx in facts:
        for e in schema_errs:
            errs.append("C1 schema: %s" % e)

    valid = [(obj, idx) for obj, schema_errs, idx in facts if obj is not None and not schema_errs]
    by_id = {}
    seen = {}
    for obj, idx in valid:
        seen.setdefault(obj.get("id"), []).append(idx)
        by_id.setdefault(obj.get("id"), obj)
    for cid, where in sorted(seen.items()):
        if len(where) > 1:
            errs.append("C1 schema: %s appears %d times (ids must be unique)" % (cid, len(where)))

    # C2 — locus presence & shape (a precondition, not a firewall proof)
    for obj, _idx in valid:
        loci = obj.get("loci") or []
        for locus in loci:
            if not isinstance(locus, str) or not locus.strip() or not _LOCUS_RE.search(locus):
                errs.append("C2 locus shape: %s has a malformed / non-locus entry %r (need a "
                            "chapter / §section / ¶ / line / page token)" % (obj.get("id"), locus))

    # C3 — contradiction integrity (each ledger row pairs >=2 real facts that conflict)
    for refs in contradiction_rows(text):
        uniq = sorted(set(refs))
        tag = "+".join(uniq) if uniq else "<no ids>"
        if len(uniq) < 2:
            errs.append("C3 contradiction: ledger row [%s] references fewer than 2 canon_fact ids "
                        "(a contradiction pairs at least two)" % tag)
            continue
        missing = [i for i in uniq if i not in by_id]
        if missing:
            errs.append("C3 contradiction: ledger row [%s] references unknown id(s) %s"
                        % (tag, ", ".join(missing)))
            continue
        objs = [by_id[i] for i in uniq]
        entities = {(o.get("entity") or "").strip().lower() for o in objs}
        attributes = {(o.get("attribute") or "").strip().lower() for o in objs}
        if len(entities) > 1 or len(attributes) > 1:
            errs.append("C3 contradiction: ledger row [%s] pairs facts that do not share "
                        "entity+attribute (not the same fact in conflict)" % tag)
            continue
        if len({o.get("value") for o in objs}) < 2:
            errs.append("C3 contradiction: ledger row [%s] pairs facts that assert the SAME value "
                        "(not a contradiction)" % tag)

    # C4 — chronology consume-vs-rederive (chronology<->Timeline only; advisory, ERROR --strict)
    scene_ids, povs, settings = timeline_facts(timeline_text)
    rederive_overrides = _overrides(text, "bible-rederive")
    for obj, _idx in valid:
        if obj.get("category") != "chronology" or obj.get("id") in rederive_overrides:
            continue
        cons = obj.get("consolidates")
        cons = cons.strip() if isinstance(cons, str) else None
        if not cons:
            warns.append("C4 chronology consume: %s is a chronology fact that does not consolidate "
                         "to a Timeline scene id — it re-derives a temporal fact the Timeline owns "
                         "(cite a scene id, or override if no Timeline run)" % obj.get("id"))
        elif scene_ids is not None and cons not in scene_ids:
            warns.append("C4 chronology consume: %s consolidates %r, which is not a scene id in the "
                         "provided Timeline" % (obj.get("id"), cons))

    # W1 — coverage (Timeline POV / setting with no Cast / Places entry; advisory, ERROR --strict)
    if scene_ids is not None:
        cast = {(o.get("entity") or "").strip().lower() for o, _ in valid if o.get("category") == "person"}
        places = {(o.get("entity") or "").strip().lower() for o, _ in valid if o.get("category") == "place"}
        for pov in sorted(povs):
            if pov.strip().lower() not in cast:
                warns.append("W1 coverage: Timeline POV %r has no Cast (person) entry in the Bible" % pov)
        for setting in sorted(settings):
            if setting.strip().lower() not in places:
                warns.append("W1 coverage: Timeline setting %r has no Places (place) entry in the Bible" % setting)

    # Report
    lines.append("continuity-bible: %d fact(s)%s" % (
        len(facts), "" if len(valid) == len(facts) else " (%d well-formed)" % len(valid)))
    for obj, _idx in valid:
        lines.append("  %-7s %-10s %s = %s" % (obj.get("id"), obj.get("category"),
                                               obj.get("entity"), obj.get("value")))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("continuity-bible: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: continuity-bible: %d advisory gap(s) — see C4/W1 above" % len(warns))
    else:
        lines.append("continuity-bible: PASS (schema + locus shape + contradiction integrity + "
                     "chronology consume boundary)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def _is_timeline(text, path):
    return ("Scene ID" in (text or "")) or ("timeline" in os.path.basename(path).lower())


def resolve(paths):
    """Return (bible_path, timeline_path_or_None)."""
    if len(paths) == 1 and os.path.isdir(paths[0]):
        d = paths[0]
        bible = _newest(glob.glob(os.path.join(d, _BIBLE_GLOB)))
        tl = None
        for cand in [os.path.join(d, "Timeline.md"), os.path.join(os.path.dirname(os.path.abspath(d)), "Timeline.md")]:
            if os.path.isfile(cand):
                tl = cand
                break
        return bible, tl
    bible = timeline = None
    for p in paths:
        text = _read(p) or ""
        if _has_block(text, "canon_fact"):
            bible = bible or p
        elif _is_timeline(text, p):
            timeline = timeline or p
    if bible is None and paths:
        bible = paths[0]
    return bible, timeline


def run(paths, strict=False):
    bible_path, timeline_path = resolve(paths)
    if not bible_path:
        return 2, ["continuity-bible: no Continuity Bible artifact found (need a "
                   "*_Continuity_Bible_*.md or a file with apodictic:canon_fact blocks)"]
    text = _read(bible_path)
    if text is None:
        return 2, ["continuity-bible: cannot read %s" % bible_path]
    return bible(text, timeline_text=_read(timeline_path) if timeline_path else None, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    # non-UTF8 artifact: _read must degrade to the unreadable path (None), never
    # a traceback (the disposition_check adjacent-exception class, swept repo-wide)
    import tempfile as _tf
    _fd, _nu = _tf.mkstemp(suffix=".md")
    with os.fdopen(_fd, "wb") as _fh:
        _fh.write(b"\xff\xfenot utf-8\xff")
    chk("non_utf8_read_returns_none", _read(_nu) is None)
    os.unlink(_nu)

    def fact(cid, entity="Mara", category="person", attribute="age", value="32",
             loci=("Ch 9 ¶4",), consolidates=None):
        obj = {"schema": _SCHEMA_ID, "id": cid, "entity": entity, "category": category,
               "attribute": attribute, "value": value, "loci": list(loci)}
        if consolidates is not None:
            obj["consolidates"] = consolidates
        return "<!-- apodictic:canon_fact\n%s\n-->" % _j.dumps(obj)

    TL = ("## Section 1: Event Ledger\n"
          "| Scene ID | Chapter / Section | POV | Setting | Confidence |\n"
          "|---|---|---|---|---|\n"
          "| Ch 1 §1 | Ch 1 | Mara | Kitchen | HIGH |\n"
          "| Ch 1 §2 | Ch 1 | Mara | Office | HIGH |\n"
          "| Ch 2 §1 | Ch 2 | Jon | Train station | HIGH |\n")

    # clean single fact (no timeline => W1 skipped, no chronology => C4 silent)
    chk("clean_single", bible(fact("CF-01"))[0] == 0)

    # C1 — bad enum / id / missing field / unquoted numeric / empty loci / JSON
    chk("c1_bad_category", bible(fact("CF-01", category="thing"))[0] == 1)
    chk("c1_bad_id", bible(fact("CF-1"))[0] == 1)
    chk("c1_missing_field", bible(fact("CF-01").replace('"attribute"', '"attr"'))[0] == 1)
    code, lines = bible('<!-- apodictic:canon_fact\n{"schema":"apodictic.canon_fact.v1","id":"CF-01",'
                        '"entity":"Mara","category":"person","attribute":"age","value":32,'
                        '"loci":["Ch 9"]}\n-->')
    chk("c1_unquoted_numeric", code == 1 and any("C1 schema" in ln for ln in lines))
    chk("c1_empty_loci", bible(fact("CF-01", loci=[]))[0] == 1)
    code, lines = bible('<!-- apodictic:canon_fact\n{"schema":"apodictic.canon_fact.v1"\n-->')
    chk("c1_bad_json", code == 1 and any("C1 schema" in ln for ln in lines))
    code, lines = bible(fact("CF-01") + "\n" + fact("CF-01", value="30"))
    chk("c1_duplicate_id", code == 1 and any("appears 2 times" in ln for ln in lines))

    # C2 — locus shape
    code, lines = bible(fact("CF-01", loci=["the kitchen"]))
    chk("c2_non_locus", code == 1 and any("C2 locus shape" in ln for ln in lines))
    chk("c2_empty_locus", bible(fact("CF-01", loci=[""]))[0] == 1)
    chk("c2_section_locus_ok", bible(fact("CF-01", loci=["Ch 1 §2"]))[0] == 0)
    chk("c2_line_locus_ok", bible(fact("CF-01", loci=["line 42"]))[0] == 0)

    # C3 — contradiction integrity
    LEDGER = "\n## Contradiction Ledger\n\n| Entity | Attribute | Conflicting facts |\n|---|---|---|\n"
    pair = fact("CF-02", attribute="age", value="30", loci=["Ch 2"]) + "\n" + \
        fact("CF-03", attribute="age", value="32", loci=["Ch 9"])
    chk("c3_clean_contradiction",
        bible(pair + LEDGER + "| Mara | age | CF-02, CF-03 |\n")[0] == 0)
    code, lines = bible(pair + LEDGER + "| Mara | age | CF-02 |\n")
    chk("c3_too_few_ids", code == 1 and any("fewer than 2" in ln for ln in lines))
    # a real data row with NO fact refs must be rejected, not silently dropped (Codex P1)
    code, lines = bible(pair + LEDGER + "| Mara | age | unresolved |\n")
    chk("c3_zero_ref_row_rejected", code == 1 and any("fewer than 2" in ln for ln in lines))
    code, lines = bible(pair + LEDGER + "| Mara | age | CF-02, CF-99 |\n")
    chk("c3_unknown_id", code == 1 and any("unknown id" in ln for ln in lines))
    # facts that agree (same value) are not a contradiction
    agree = fact("CF-02", attribute="age", value="32", loci=["Ch 2"]) + "\n" + \
        fact("CF-03", attribute="age", value="32", loci=["Ch 9"])
    code, lines = bible(agree + LEDGER + "| Mara | age | CF-02, CF-03 |\n")
    chk("c3_same_value", code == 1 and any("SAME value" in ln for ln in lines))
    # facts on different entity/attribute are not the same fact in conflict
    cross = fact("CF-02", entity="Mara", attribute="age", value="30", loci=["Ch 2"]) + "\n" + \
        fact("CF-03", entity="Jon", attribute="age", value="32", loci=["Ch 9"])
    code, lines = bible(cross + LEDGER + "| ? | age | CF-02, CF-03 |\n")
    chk("c3_mismatched_facts", code == 1 and any("do not share" in ln for ln in lines))

    # C4 — chronology consume (advisory; ERROR --strict; override; resolves against Timeline)
    chron = fact("CF-10", entity="office scene", category="chronology", attribute="day",
                 value="Day 1", loci=["Ch 1 §2"])
    code, lines = bible(chron, timeline_text=TL)
    chk("c4_no_consolidate_advisory", code == 0 and any("C4 chronology consume" in ln for ln in lines))
    chk("c4_no_consolidate_strict_fails", bible(chron, timeline_text=TL, strict=True)[0] == 1)
    good_chron = fact("CF-10", entity="office scene", category="chronology", attribute="day",
                      value="Day 1", loci=["Ch 1 §2"], consolidates="Ch 1 §2")
    chk("c4_resolves_clean",
        not any("C4 chronology" in ln for ln in bible(good_chron, timeline_text=TL)[1]))
    bad_chron = fact("CF-10", entity="office scene", category="chronology", attribute="day",
                     value="Day 1", loci=["Ch 1 §2"], consolidates="Ch 9 §9")
    chk("c4_unresolved_ref",
        any("not a scene id" in ln for ln in bible(bad_chron, timeline_text=TL)[1]))
    ov = "<!-- override: bible-rederive CF-10 — no Timeline run for this draft -->\n"
    chk("c4_override_silences",
        not any("C4 chronology" in ln for ln in bible(ov + chron, timeline_text=TL)[1]))
    # no Timeline + consolidates set => cannot disprove, stays clean
    chk("c4_no_timeline_set_clean",
        not any("C4 chronology" in ln for ln in bible(good_chron)[1]))

    # W1 — coverage (Timeline POV / setting with no entry; advisory)
    code, lines = bible(fact("CF-01", entity="Mara", category="person"), timeline_text=TL)
    chk("w1_missing_pov_and_place", code == 0 and any("W1 coverage" in ln for ln in lines)
        and any("Jon" in ln for ln in lines) and any("Kitchen" in ln for ln in lines))
    full = "\n".join([
        fact("CF-01", entity="Mara", category="person", attribute="role", value="protagonist", loci=["Ch 1"]),
        fact("CF-02", entity="Jon", category="person", attribute="role", value="brother", loci=["Ch 2"]),
        fact("CF-03", entity="Kitchen", category="place", attribute="description", value="the family kitchen", loci=["Ch 1"]),
        fact("CF-04", entity="Office", category="place", attribute="description", value="Mara's workplace", loci=["Ch 1"]),
        fact("CF-05", entity="Train station", category="place", attribute="description", value="arrival point", loci=["Ch 2"]),
    ])
    chk("w1_full_coverage_clean", not any("W1" in ln for ln in bible(full, timeline_text=TL)[1]))

    # no blocks -> no-op
    chk("no_facts_noop", bible("# Notes\nnothing structured\n")[0] == 0)

    # run-folder + explicit-file resolution
    import tempfile
    import shutil
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "Proj_Continuity_Bible_run.md")
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Continuity Bible\n" + fact("CF-01") + "\n")
        with open(os.path.join(d, "Timeline.md"), "w", encoding="utf-8", newline="") as fh:
            fh.write("# Timeline\n" + TL)
        chk("run_folder_resolution", run([d])[0] == 0)
        chk("explicit_file_resolution", run([p])[0] == 0)
        # explicit bible + timeline classified correctly (chronology resolves)
        tlp = os.path.join(d, "tl.md")
        with open(tlp, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Timeline\n" + TL)
        bp = os.path.join(d, "Proj_Continuity_Bible_chron.md")
        with open(bp, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Continuity Bible\n" + good_chron + "\n")
        chk("explicit_bible_plus_timeline", run([bp, tlp])[0] == 0)
        chk("missing_artifact_usage", run([os.path.join(d, "nope.md")])[0] == 2)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "continuity-bible"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: continuity_bible.py continuity-bible <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
