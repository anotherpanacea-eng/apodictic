#!/usr/bin/env python3
"""manuscript-viz — manifest<->source provenance for Manuscript-Structure Visualizations.

`validate.sh manuscript-viz <run_folder|files...> [--strict]` shells out here. A finished
development edit already CONTAINS most of the numbers a structural picture needs — locked inside
prose and tables. This builds no new analysis: a `apodictic.viz_manifest.v1` block holds only
TRACEABLE data copied verbatim from two already-machine-readable sources — the Timeline Event-Ledger
pipe-table (scenes) and the `apodictic.finding.v1` blocks (findings) — and a render-only SVG layer
draws it. The validator owns manifest<->source provenance:

  E1 manifest schema     the block parses + satisfies the wrapper schema, every scenes[]/findings[]
                         element is a well-formed object with ONLY allowlisted keys (a visual-style
                         field is itself a failure — style is the renderer's, not the run's).
  E2 provenance closure  every findings[].id resolves to a real finding in the Ledger; every
                         scenes[].scene_id resolves to a Timeline Event-Ledger row; every
                         findings[].chapter equals the conservative `evidence_refs` parse (Chapter N /
                         Ch N -> "Ch N", else the literal "unplaced"). No guessed placement.
  E3 Must-Fix complete   every body Must-Fix finding in the Ledger appears in findings[].
  E4 no orphan data      every scenes[] cell is byte-equal to the Timeline cell; every findings[]
                         severity/confidence is byte-equal to its source block. The manifest copied,
                         it did not compute or embellish.
  E5 no duplicate entry  a scene_id or finding id appears at most once — a repeat double-draws a bar
                         (a value the sources did not contain); the per-id E2/E4 checks pass on dups.
  W2 scene order         scenes[] order diverges from the Timeline's document order (the pacing
                         curve's x-axis is scene order — a reordered manifest draws a false shape).
                         Advisory.
  W1 coverage            a Timeline row not represented in scenes[] (silent under-render). Advisory.

Manuscript-Visualization Completion (charts 4-7) extends this same manifest<->source contract. Three
render deliverables exist today: chart 7-nonfiction — the CLAIM LADDER over apodictic.argument_spine.v1
(C0 thesis + C1..Cn subclaims) annotated with support coverage from apodictic.support_plan.v1; chart 5 —
the CHARACTER CO-PRESENCE NETWORK over the apodictic.scene_roster.v1 producer (per-scene cast; the
Timeline carries POV only, not a full roster); and chart 6 — the SCENE-FUNCTION HEATMAP over the
apodictic.scene_function.v1 producer (per-scene structural function from the scene-turn audit's Step-1
Unit Classification: scene | sequel | hybrid | non-unit). The manifest gains four OPTIONAL, additive
arrays (co_presence / scene_functions / reveal_points / claim_ladder); claim_ladder + co_presence +
scene_functions are rendered (reveal_points is still producer-gated — apodictic.tension_point.v1 does
not exist yet, so its array stays absent and the gate skips it):

  X1 new-array schema    each present co_presence/scene_functions/reveal_points/claim_ladder element
                         is a well-formed object with ONLY its allowlisted keys (a visual-style key
                         is itself a failure; a scene_ids/scene_id/section key on a claim_ladder[]
                         object is itself a failure — the claim-to-scene map has no producer and
                         cannot be smuggled in). claim_ladder[].support[] items admit only
                         {support_type, status} (the support_plan.v1 enums); co_presence[].characters
                         items are bare canonical NAME STRINGS (the auditable {name, anchor} richness
                         lives in the scene_roster.v1 PRODUCER, not the manifest).
  X5 claim-ladder prov   every claim_ladder[].claim_id is a member of
                         argument_spine.spine_subclaim_ids(spine) (REUSE that parser — no second
                         one); label is byte-equal to the matching subclaim string with its leading
                         "Cn:"/"Cn " token stripped; each support[] item is byte-equal to a real
                         support_plan.v1 block whose subclaim_id == claim_id; an empty support[] is
                         permitted ONLY when no support_plan declares that claim_id (bare assertion,
                         the W2 condition argument_spine.py already computes). No scene resolution.
  X6 no orphan datum     generalizes E4 to the new arrays — every value byte-equals its producer
                         source (a claim_ladder[] label not byte-equal to its stripped subclaim, or a
                         support pairing absent from support_plan.v1, fails here).
  X7 no duplicate        generalizes E5 — a scene_id at most once per new array; a claim_id at most
                         once in claim_ladder[].
  X3 scene-function prov every scene_functions[].scene_id matches a scene_function.v1 producer entry
                         AND resolves to a Timeline Event-Ledger row; the manifest function is
                         byte-equal to the producer's classification; in the producer, every function
                         is in the closed scene-turn Unit-Classification enum and every anchor is
                         non-empty (a line-range anchor must overlap the scene's Timeline line-range).
                         The function READING is producer/author-enforced — the gate enforces
                         enum + anchor + provenance closure, NOT the semantic reading.
  X2 co-presence prov    every co_presence[].scene_id matches a scene_roster.v1 roster entry AND
                         resolves to a Timeline Event-Ledger row; every name in
                         co_presence[].characters is in that scene's roster (canonical) names; the
                         scene's Timeline POV character is present in its roster (cross-check); and in
                         the producer, every roster character's `anchor` is non-empty. The
                         present-vs-mentioned READING is producer/author-enforced (a validator cannot
                         read prose) — the gate enforces anchor-non-empty + provenance closure, NOT
                         the semantic reading (the Continuity Bible C2 author-enforced precedent).
  X8 producer-present    if a new array is PRESENT, its producer MUST be present and resolvable (for
                         claim_ladder: a resolvable argument_spine.v1 block, plus the support_plan.v1
                         blocks for any non-empty support[]; for co_presence: a resolvable
                         scene_roster.v1 block; for scene_functions: a resolvable scene_function.v1
                         block). Absent array -> skipped, not failed.
  W3 chart coverage      a producer artifact is present but its corresponding array is empty/absent
                         (silent under-rendering). Advisory, ERROR under --strict.

(X4 — reveal/tension provenance — is reserved for the still-producer-gated chart 4; its
apodictic.tension_point.v1 producer does not exist yet, so that gate is not implemented. X2 backs chart
5 and X3 backs chart 6 — their scene_roster.v1 / scene_function.v1 producers DO exist.)

The severity->encoding map is HARDCODED in the renderer, never read from the manifest, so a run
cannot recolor a Must-Fix to comfort, and a Must-Fix marker is always drawn at full salience (its
size never shrinks for low confidence). Reuses timeline_checks._parse_event_ledger (the Timeline
column parser), apodictic_artifacts (block grammar + schema engine), and — for the claim ladder —
argument_spine.parse_spine / parse_support_plans / spine_subclaim_ids (no second parser). See
docs/manuscript-visualizations.md.

  viz_manifest.py manuscript-viz <run_folder|files...> [--strict] [--require-block]
  viz_manifest.py render <manifest> <timeline> <ledger> [-o out.html]
  viz_manifest.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import html
import os
import re
import sys

try:
    import apodictic_artifacts as art
except ImportError:
    art = None
try:
    import timeline_checks as tl
except ImportError:
    tl = None
try:
    # Chart 7-nonfiction (claim ladder) reuses the spine/support parsers + the Cn-token resolver —
    # never a second parser. argument_spine.py lives in the same (mirrored) script dir, so this
    # import resolves from either copy; it degrades to None like the others.
    import argument_spine as aspine
except ImportError:
    aspine = None


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (a parsed carrier, not a prose mention).

    Classifying on parsed blocks — not a raw substring — keeps a file that merely *names* the marker
    in prose from being misrouted/skipped (the 2026-06-20 resolver-hardening sweep). Gated by
    validate.sh validator-conventions (M2)."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))


_SCHEMA_ID = "apodictic.viz_manifest.v1"
_FINDING_SCHEMA_ID = "apodictic.finding.v1"
_ROSTER_SCHEMA_ID = "apodictic.scene_roster.v1"   # chart 5 producer (per-scene cast)
_SFUNC_SCHEMA_ID = "apodictic.scene_function.v1"  # chart 6 producer (per-scene structural function)
_MANIFEST_GLOB = "*_Structure_Map_*.md"
_TIMELINE_GLOBS = ("*_Timeline_*.md", "Timeline.md")
_LEDGER_GLOB = "*_Findings_Ledger_*.md"
_SPINE_GLOB = "Argument_State*.md"   # chart 7-nonfiction source (the seeded pre-draft Argument_State)
_ROSTER_GLOB = "*Scene_Roster*.md"   # chart 5 producer source (the per-scene cast roster)
_SFUNC_GLOB = "*Scene_Function*.md"  # chart 6 producer source (the per-scene function classification)

# The manifest is style-free: these are the ONLY keys each object may carry (E1 allowlist).
_SCENE_KEYS = ("scene_id", "chapter", "line_range", "word_count", "pov", "span", "gap")
_FINDING_KEYS = ("id", "severity", "confidence", "chapter")
# Charts 4-7 (Manuscript-Visualization Completion) — four OPTIONAL additive arrays. M1 renders only
# claim_ladder; the other three are producer-gated (their producers do not exist yet). The closed
# allowlists are the X1 firewall: claim_ladder[] admits NO scene_ids/scene_id/section key (the
# claim-to-scene map has no producer and cannot be smuggled in); support[] items admit only the two
# support_plan.v1 fields the manifest copies verbatim.
_CO_PRESENCE_KEYS = ("scene_id", "characters")
# chart 6 — the manifest scene_functions[] carries a bare {scene_id, function}; the auditable `anchor`
# richness lives in the scene_function.v1 PRODUCER (the same manifest/producer split as co_presence).
_SCENE_FUNCTION_KEYS = ("scene_id", "function")
_REVEAL_POINT_KEYS = ("scene_id", "tension", "reveal_id")
_CLAIM_LADDER_KEYS = ("claim_id", "label", "support")
_SUPPORT_ITEM_KEYS = ("support_type", "status")
# scene_roster.v1 producer — the nested objects the subset engine cannot recurse into (validated in
# scene_roster() below). A roster character carries a REQUIRED non-empty `anchor` (the accountability
# mechanism for the producer-enforced present-vs-mentioned reading); an alias maps a surface form to a
# canonical name.
_ROSTER_ENTRY_KEYS = ("scene_id", "characters")
_ROSTER_CHARACTER_KEYS = ("name", "anchor")
_ALIAS_KEYS = ("surface", "canonical")
# scene_function.v1 producer — the nested functions[] objects (validated in scene_functions_producer()
# below). Each carries a REQUIRED non-empty `anchor` (the accountability mechanism for the
# author-enforced function classification) and a `function` from the CLOSED scene-turn Unit-Classification
# enum (craft/scene-turn.md §Step 1): scene | sequel | hybrid | non-unit.
_FUNCTION_ENTRY_KEYS = ("scene_id", "function", "anchor")
_SCENE_FUNCTION_ENUM = ("scene", "sequel", "hybrid", "non-unit")
# The support_plan.v1 enums the manifest copies verbatim (X1 value-allowlist on support[] items).
_SUPPORT_TYPE_ENUM = ("REASON", "EXAMPLE", "DATA", "AUTHORITY", "EXPERIENCE")
_SUPPORT_STATUS_ENUM = ("in-hand", "to-acquire")
_TOP_KEYS = ("schema", "project", "partial", "scenes", "findings",
             "co_presence", "scene_functions", "reveal_points", "claim_ladder")

# Hardcoded severity -> encoding (renderer-owned; the manifest cannot override it).
_SEV_ENCODING = {
    "Must-Fix":   {"color": "#A8344A", "rank": 3},
    "Should-Fix": {"color": "#8B5E3C", "rank": 2},
    "Could-Fix":  {"color": "#5E8C6A", "rank": 1},
}
_CHAPTER_RE = re.compile(r"\b(?:Chapter|Ch)\s*(\d+)\b", re.IGNORECASE)
# A LINE-RANGE-shaped anchor: a leading "lines N-M" (case-insensitive; en-dash or hyphen). The
# producer's anchor MAY instead be a quote (no leading line range) — that form is not bounded.
# A bare Timeline line_range cell ("N-M") is parsed by the SAME helper (its optional leading "lines"
# prefix makes both forms parse), so the X2(e) bounding compares like with like.
_LINE_RANGE_RE = re.compile(r"^\s*(?:lines?\s+)?(\d+)\s*[-–]\s*(\d+)\b", re.IGNORECASE)


def _parse_line_range(text):
    """(start, end) ints from a leading 'lines N-M' / 'N-M' span, or None if `text` isn't line-range
    shaped (e.g. a quote-form anchor). Normalizes a reversed span so start <= end."""
    if not isinstance(text, str):
        return None
    m = _LINE_RANGE_RE.match(text)
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    return (a, b) if a <= b else (b, a)


def _ranges_overlap(r1, r2):
    """True iff the inclusive integer ranges r1=(a,b), r2=(c,d) overlap at all."""
    return r1[0] <= r2[1] and r2[0] <= r1[1]


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


# ---------------------------------------------------------------- source parsing

def timeline_rows(timeline_text):
    """Timeline Event-Ledger rows as {scene_id: {chapter,line_range,word_count,pov,span,gap}} (verbatim)."""
    out = {}
    if not timeline_text or tl is None:
        return out
    for row in tl._parse_event_ledger(timeline_text):
        sid = tl._row_get(row, "scene id")
        if not sid:
            continue
        out[sid] = {
            "scene_id": sid,
            "chapter": tl._row_get(row, "chapter") or "",
            "line_range": tl._row_get(row, "line range") or "",
            "word_count": tl._row_get(row, "word count") or "",
            "pov": tl._row_get(row, "pov") or "",
            "span": tl._row_get(row, "span") or "",
            "gap": tl._row_get(row, "gap") or "",
        }
    return out


def ledger_findings(ledger_text):
    """{finding_id: obj} for the ledger's apodictic.finding.v1 blocks (the authoritative ID set)."""
    out = {}
    if not ledger_text or art is None:
        return out
    for bt, obj, _err in art.parse_blocks(ledger_text):
        if bt == "finding" and isinstance(obj, dict) and obj.get("id"):
            out[art.fid_key(obj["id"])] = obj   # a non-hashable ledger id must not crash this index key
    return out


def _strip_claim_id(subclaim_str):
    """The subclaim string with its leading 'Cn'/'Cn:'/'Cn ' token stripped — the SAME token
    argument_spine.spine_subclaim_ids() consumed (it matches `_SUBCLAIM_ID_RE = ^\\s*(C[0-9]+)\\b`).
    The remainder is the rung label X5/X6 byte-check against. Strips the regex-matched span, then a
    single trailing separator run of ':' / whitespace (the canonical 'C1: …' / 'C1 …' conventions)."""
    if aspine is None or not isinstance(subclaim_str, str):
        return None
    m = aspine._SUBCLAIM_ID_RE.match(subclaim_str)
    if not m:
        return None
    rest = subclaim_str[m.end():]
    return re.sub(r"^[:\s]+", "", rest)


def spine_ladder(spine_text):
    """The claim-ladder SOURCE for chart 7-nonfiction, drawn from apodictic.argument_spine.v1 +
    apodictic.support_plan.v1 — the same parsed-block path argument_spine.py uses (no second parser).

    Returns a dict the X5/X6/X8/W3 gates and the renderer read:
      {
        "present":  bool,                       # a valid argument_spine.v1 block resolved
        "thesis":   str|None,                   # C0 (rendered from the spine, not stored in manifest)
        "ids":      set[str],                   # declared Cn ids (spine_subclaim_ids — REUSED)
        "labels":   {Cn: stripped_label},       # subclaim string minus its leading Cn token
        "support":  {Cn: [{support_type,status}, ...]},  # support_plan.v1 blocks keyed on subclaim_id
        "planned":  set[str],                   # Cn ids that have >=1 support_plan block
      }
    `support` carries ONLY the two fields the manifest copies (support_type, status) — verbatim from
    the producer block — so X6 can byte-compare the manifest's support[] against this source."""
    out = {"present": False, "thesis": None, "ids": set(), "labels": {},
           "support": {}, "planned": set()}
    if not spine_text or aspine is None:
        return out
    obj, schema_errs = aspine.parse_spine(spine_text)
    if obj is None or schema_errs:
        return out
    out["present"] = True
    out["thesis"] = obj.get("thesis")
    out["ids"] = aspine.spine_subclaim_ids(obj)   # REUSE — the leading-Cn-token parse, not re-derived
    for s in (obj.get("subclaims") or []):
        if not isinstance(s, str):
            continue
        m = aspine._SUBCLAIM_ID_RE.match(s)
        if m:
            out["labels"][m.group(1)] = _strip_claim_id(s)
    # support_plan.v1 blocks, grouped by subclaim_id, copying ONLY {support_type, status} verbatim.
    for o, serrs, _i in aspine.parse_support_plans(spine_text):
        if o is None or serrs:
            continue
        sid = o.get("subclaim_id")
        if not sid:
            continue
        out["planned"].add(sid)
        out["support"].setdefault(sid, []).append(
            {"support_type": o.get("support_type"), "status": o.get("status")})
    return out


def scene_roster(roster_text):
    """The chart-5 PRODUCER source — the apodictic.scene_roster.v1 per-scene cast (parsed-block path,
    no second parser). ONE block per manuscript. Returns a dict the X2 gate + the renderer read:

      {
        "present":    bool,                            # a valid scene_roster.v1 block resolved
        "project":    str|None,
        "aliases":    {surface_lower: canonical},      # declared surface-form -> canonical-name table
        "names":      {scene_id: [canonical_name, ...]},  # CANONICALIZED, de-duped, in declared order
        "anchors":    {scene_id: {canonical_name: anchor, ...}},  # the audit locus per character
        "obj_errs":   [str, ...],                      # nested-object schema errors (anchor non-empty,
                                                       #   closed allowlist, alias/roster shape)
      }

    The alias table collapses surface forms to one canonical node (the longest declared surface form
    is NOT auto-chosen as canonical — canonical is whatever the table's `canonical` field names; the
    renderer + co-occurrence key on it). A name with no alias row IS its own canonical (identity).
    Producer-/author-enforced present-vs-mentioned: this records who is PRESENT (anchored); a
    mentioned-only character is simply absent from `characters` (no entry, no edge). The X2 gate
    enforces anchor-non-empty + provenance closure here, NOT the semantic reading."""
    out = {"present": False, "project": None, "aliases": {}, "names": {}, "anchors": {}, "obj_errs": []}
    if not roster_text or art is None:
        return out
    schema = art.load_schema(_ROSTER_SCHEMA_ID)
    obj = None
    for bt, o, jerr in art.parse_blocks(roster_text):
        if bt != "scene_roster":
            continue
        if jerr:
            out["obj_errs"].append("X2 co-presence provenance: scene_roster block — invalid JSON — %s" % jerr)
            return out
        obj = o
        break
    if not isinstance(obj, dict):
        return out
    for e in art.validate_obj(obj, schema, "scene_roster"):
        out["obj_errs"].append("X2 co-presence provenance: scene_roster — %s" % e)
    # If the wrapper schema rejected the block (e.g. wrong const / missing rosters / stray top key),
    # it is not a usable producer — surface the errors but do not pretend it is present.
    if out["obj_errs"]:
        return out
    out["present"] = True
    out["project"] = obj.get("project")

    # character_aliases[] — {surface, canonical}. Closed allowlist + non-empty strings. Keyed
    # case-folded on the surface form so 'Mara'/'mara' collapse identically; canonical kept verbatim.
    aliases = obj.get("character_aliases") or []
    if not isinstance(aliases, list):
        out["obj_errs"].append("X2 co-presence provenance: scene_roster.character_aliases must be an array")
        aliases = []
    for i, al in enumerate(aliases):
        where = "scene_roster.character_aliases[%d]" % i
        if not isinstance(al, dict):
            out["obj_errs"].append("X2 co-presence provenance: %s must be an object" % where)
            continue
        for k in _ALIAS_KEYS:
            if k not in al:
                out["obj_errs"].append("X2 co-presence provenance: %s missing required field '%s'" % (where, k))
        for k in al:
            if k not in _ALIAS_KEYS:
                out["obj_errs"].append("X2 co-presence provenance: %s has disallowed field '%s' "
                                       "(an alias row is only {surface, canonical})" % (where, k))
        surf, canon = al.get("surface"), al.get("canonical")
        if not isinstance(surf, str) or not surf.strip() or not isinstance(canon, str) or not canon.strip():
            out["obj_errs"].append("X2 co-presence provenance: %s surface/canonical must be non-empty strings"
                                   % where)
            continue
        out["aliases"][surf.strip().casefold()] = canon.strip()

    def _canonical(name):
        # A declared surface form resolves to its canonical; an undeclared name is its own canonical.
        return out["aliases"].get(name.strip().casefold(), name.strip())

    # rosters[] — {scene_id, characters: [{name, anchor}]}. Closed allowlist; anchor REQUIRED non-empty.
    rosters = obj.get("rosters") or []
    if not isinstance(rosters, list):
        out["obj_errs"].append("X2 co-presence provenance: scene_roster.rosters must be an array")
        rosters = []
    for i, r in enumerate(rosters):
        where = "scene_roster.rosters[%d]" % i
        if not isinstance(r, dict):
            out["obj_errs"].append("X2 co-presence provenance: %s must be an object" % where)
            continue
        for k in _ROSTER_ENTRY_KEYS:
            if k not in r:
                out["obj_errs"].append("X2 co-presence provenance: %s missing required field '%s'" % (where, k))
        for k in r:
            if k not in _ROSTER_ENTRY_KEYS:
                out["obj_errs"].append("X2 co-presence provenance: %s has disallowed field '%s' "
                                       "(a roster entry is only {scene_id, characters})" % (where, k))
        sid = r.get("scene_id")
        chars = r.get("characters")
        if not isinstance(sid, str) or not sid.strip():
            out["obj_errs"].append("X2 co-presence provenance: %s.scene_id must be a non-empty string" % where)
            continue
        sid = sid.strip()
        if not isinstance(chars, list):
            out["obj_errs"].append("X2 co-presence provenance: %s.characters must be an array" % where)
            continue
        names, anchors = [], {}
        for j, c in enumerate(chars):
            cwhere = "%s.characters[%d]" % (where, j)
            if not isinstance(c, dict):
                out["obj_errs"].append("X2 co-presence provenance: %s must be an object" % cwhere)
                continue
            for k in _ROSTER_CHARACTER_KEYS:
                if k not in c:
                    out["obj_errs"].append("X2 co-presence provenance: %s missing required field '%s'" % (cwhere, k))
            for k in c:
                if k not in _ROSTER_CHARACTER_KEYS:
                    out["obj_errs"].append("X2 co-presence provenance: %s has disallowed field '%s' "
                                           "(a roster character is only {name, anchor})" % (cwhere, k))
            nm, anc = c.get("name"), c.get("anchor")
            if not isinstance(nm, str) or not nm.strip():
                out["obj_errs"].append("X2 co-presence provenance: %s.name must be a non-empty string" % cwhere)
                continue
            # X2(d) — the anchor is the accountability mechanism for the author-enforced presence
            # reading: it MUST be present and non-empty (a Timeline-relative line-range or on-page
            # quote). An empty anchor is a free presence assertion — the firewall's whole point.
            if not isinstance(anc, str) or not anc.strip():
                out["obj_errs"].append("X2 co-presence provenance: %s.anchor must be a non-empty string "
                                       "(presence is author-enforced and made auditable by the anchor — "
                                       "a line-range or on-page quote; an empty anchor is a free assertion)"
                                       % cwhere)
            cn = _canonical(nm)
            if cn not in names:   # collapse surface forms / dup entries to one canonical node
                names.append(cn)
            # First anchor for a canonical name wins (deterministic; later dup-name rows keep the first).
            anchors.setdefault(cn, anc if isinstance(anc, str) else "")
        # A repeated scene_id in the producer would silently merge two cast lists — flag it (X7-style).
        if sid in out["names"]:
            out["obj_errs"].append("X2 co-presence provenance: %s.scene_id %r appears more than once in "
                                   "the producer (each scene has exactly one roster)" % (where, sid))
            continue
        out["names"][sid] = names
        out["anchors"][sid] = anchors
    return out


def scene_functions_producer(sfunc_text):
    """The chart-6 PRODUCER source — the apodictic.scene_function.v1 per-scene structural function
    (parsed-block path, no second parser). ONE block per manuscript. Returns a dict the X3 gate + the
    renderer read:

      {
        "present":   bool,                      # a valid scene_function.v1 block resolved
        "project":   str|None,
        "functions": {scene_id: function},      # scene_id -> the closed scene-turn function token
        "anchors":   {scene_id: anchor},        # the audit locus per scene
        "obj_errs":  [str, ...],                # nested-object schema errors (function-in-enum,
                                                #   anchor non-empty, closed allowlist, dup scene_id)
      }

    The `function` token is the scene-turn audit's Step 1 Unit Classification (scene | sequel | hybrid |
    non-unit — craft/scene-turn.md §Step 1), copied verbatim. Producer-/author-enforced: this records
    the author's function reading, made auditable by the required non-empty `anchor`. The X3 gate
    enforces function-in-enum + anchor-non-empty + provenance closure (scene_id -> Timeline row), NOT
    the semantic reading (the scene_roster.v1 author-enforced precedent)."""
    out = {"present": False, "project": None, "functions": {}, "anchors": {}, "obj_errs": []}
    if not sfunc_text or art is None:
        return out
    schema = art.load_schema(_SFUNC_SCHEMA_ID)
    obj = None
    for bt, o, jerr in art.parse_blocks(sfunc_text):
        if bt != "scene_function":
            continue
        if jerr:
            out["obj_errs"].append("X3 scene-function provenance: scene_function block — invalid JSON — %s" % jerr)
            return out
        obj = o
        break
    if not isinstance(obj, dict):
        return out
    for e in art.validate_obj(obj, schema, "scene_function"):
        out["obj_errs"].append("X3 scene-function provenance: scene_function — %s" % e)
    # If the wrapper schema rejected the block (wrong const / missing functions / stray top key), it is
    # not a usable producer — surface the errors but do not pretend it is present.
    if out["obj_errs"]:
        return out
    out["present"] = True
    out["project"] = obj.get("project")

    # functions[] — {scene_id, function, anchor}. Closed allowlist; function in the closed enum; anchor
    # REQUIRED non-empty.
    functions = obj.get("functions") or []
    if not isinstance(functions, list):
        out["obj_errs"].append("X3 scene-function provenance: scene_function.functions must be an array")
        functions = []
    for i, f in enumerate(functions):
        where = "scene_function.functions[%d]" % i
        if not isinstance(f, dict):
            out["obj_errs"].append("X3 scene-function provenance: %s must be an object" % where)
            continue
        for k in _FUNCTION_ENTRY_KEYS:
            if k not in f:
                out["obj_errs"].append("X3 scene-function provenance: %s missing required field '%s'" % (where, k))
        for k in f:
            if k not in _FUNCTION_ENTRY_KEYS:
                out["obj_errs"].append("X3 scene-function provenance: %s has disallowed field '%s' "
                                       "(a function entry is only {scene_id, function, anchor})" % (where, k))
        sid = f.get("scene_id")
        fn = f.get("function")
        anc = f.get("anchor")
        if not isinstance(sid, str) or not sid.strip():
            out["obj_errs"].append("X3 scene-function provenance: %s.scene_id must be a non-empty string" % where)
            continue
        sid = sid.strip()
        # X3(b) — function must be a member of the closed scene-turn Unit-Classification enum. A value
        # outside it is an invented category (the firewall's whole point — the render draws only the
        # author's declared function).
        if fn not in _SCENE_FUNCTION_ENUM:
            out["obj_errs"].append("X3 scene-function provenance: %s.function=%r is not in the scene-turn "
                                   "Unit-Classification set %s" % (where, fn, list(_SCENE_FUNCTION_ENUM)))
        # X3(d) — the anchor is the accountability mechanism for the author-enforced function reading: it
        # MUST be present and non-empty (a Timeline-relative line-range or on-page quote). An empty anchor
        # is a free classification — the firewall's whole point.
        if not isinstance(anc, str) or not anc.strip():
            out["obj_errs"].append("X3 scene-function provenance: %s.anchor must be a non-empty string "
                                   "(the function reading is author-enforced and made auditable by the "
                                   "anchor — a line-range or on-page quote; an empty anchor is a free "
                                   "assertion)" % where)
        # A repeated scene_id in the producer would silently overwrite a classification — flag it (X7-style).
        if sid in out["functions"]:
            out["obj_errs"].append("X3 scene-function provenance: %s.scene_id %r appears more than once in "
                                   "the producer (each scene has exactly one function)" % (where, sid))
            continue
        out["functions"][sid] = fn if isinstance(fn, str) else ""
        out["anchors"][sid] = anc if isinstance(anc, str) else ""
    return out


def chapter_of(obj):
    """Conservative chapter bin from a finding's evidence_refs: 'Ch N' or the literal 'unplaced'.

    Delegates to the SHARED apodictic_artifacts.chapter_token so viz and annotation_manifest
    normalize chapter refs identically (it recognizes 'Ch. N' / 'Ch.N' too, which the local
    _CHAPTER_RE below — kept only for the render-time numeric sort of already-binned 'Ch N'
    strings — does not). Falls back to the local regex if the shared module is unavailable."""
    for ref in obj.get("evidence_refs") or []:
        tok = art.chapter_token(ref) if art is not None else None
        if tok:
            return tok
        if art is None:
            m = _CHAPTER_RE.search(str(ref))
            if m:
                return "Ch %s" % m.group(1)
    return "unplaced"


# ---------------------------------------------------------------- manifest parsing

def parse_manifest(text):
    """(obj_or_None, schema_errs). The single apodictic:viz_manifest block in the file."""
    if not text or art is None:
        return None, ["no viz_manifest block found"]
    schema = art.load_schema(_SCHEMA_ID)
    for bt, obj, jerr in art.parse_blocks(text):
        if bt != "viz_manifest":
            continue
        if jerr:
            return None, ["viz_manifest: invalid JSON — %s" % jerr]
        return obj, art.validate_obj(obj, schema, "viz_manifest")
    return None, ["no viz_manifest block found"]


def _check_objects(items, kind, allowed, required, gate="E1 manifest schema"):
    """Nested-object validation (the subset schema engine can't recurse into array items). `gate` is
    the rule prefix — "E1 manifest schema" for the original scenes[]/findings[] arrays, "X1 new-array
    schema" for the charts-4-7 arrays (whose closed allowlist is the no-scene-axis firewall)."""
    errs = []
    if not isinstance(items, list):
        errs.append("%s: %s must be an array" % (gate, kind))
        return errs
    for i, it in enumerate(items):
        where = "%s[%d]" % (kind, i)
        if not isinstance(it, dict):
            errs.append("%s: %s must be an object" % (gate, where))
            continue
        for k in required:
            if k not in it:
                errs.append("%s: %s missing required field '%s'" % (gate, where, k))
        for k in it:
            if k not in allowed:
                errs.append("%s: %s has disallowed field '%s' "
                            "(no visual-style fields — style is the renderer's)" % (gate, where, k))
    return errs


def _dup_errs(items, key, label, gate="E5 duplicate entry"):
    """Flag a key value that appears more than once across `items` (each maps to one chart element).
    `gate` is the rule prefix — "E5 duplicate entry" for scenes[]/findings[], "X7 duplicate entry"
    for the charts-4-7 arrays (a repeated claim_id double-draws a rung)."""
    counts = {}
    for it in items:
        if isinstance(it, dict) and it.get(key) is not None:
            kv = art.fid_key(it[key])   # a non-hashable id can't be a count-map key — coerce, never crash
            counts[kv] = counts.get(kv, 0) + 1
    errs = []
    for val, n in sorted(((v, c) for v, c in counts.items() if c > 1), key=lambda vc: str(vc[0])):
        errs.append("%s: %s %r appears %d times in the manifest "
                    "(each maps to exactly one chart element)" % (gate, label, val, n))
    return errs


def _check_claim_ladder(items, ladder):
    """X1/X5/X6/X7/X8 for the claim_ladder[] array (chart 7-nonfiction). `items` is the manifest's
    claim_ladder list; `ladder` is the spine_ladder() source. Returns (errs, warns_unused=[]). The
    no-scene-axis guard is folded into X1 below via the allowlist (a scene_ids/scene_id/section key
    has no allowlist slot, so it fails as a disallowed field)."""
    errs = []
    if not isinstance(items, list):
        errs.append("X1 new-array schema: claim_ladder must be an array")
        return errs
    if not items:
        return errs
    # X8 — producer-present: a claim_ladder array can exist ONLY if its argument_spine.v1 producer
    # resolves (the firewall's teeth — no producer, no chart to byte-check against).
    if not ladder.get("present"):
        errs.append("X8 producer-present: claim_ladder[] is present but no resolvable "
                    "apodictic.argument_spine.v1 block was found to byte-check it against "
                    "(render-what-you-produce: the producer must exist)")
        return errs
    # X1 — per-object allowlist (a visual-style key, or a scene_ids/scene_id/section key, is itself a
    # failure: the claim-to-scene map has no producer and cannot be smuggled in).
    errs += _check_objects(items, "claim_ladder", _CLAIM_LADDER_KEYS, ("claim_id", "label", "support"),
                           gate="X1 new-array schema")
    # X7 — a claim_id appears at most once (a repeat double-draws a rung).
    errs += _dup_errs([it for it in items if isinstance(it, dict)], "claim_id", "claim_id",
                      gate="X7 duplicate entry")
    ids = ladder.get("ids") or set()
    labels = ladder.get("labels") or {}
    support_src = ladder.get("support") or {}
    planned = ladder.get("planned") or set()
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            continue
        where = "claim_ladder[%d]" % i
        cid = it.get("claim_id")
        # X5 — claim_id must be a declared spine subclaim (spine_subclaim_ids — REUSED, not re-derived).
        # A non-string / unhashable cid (a malformed shape) can't be a declared id — treat it as a
        # non-member rather than letting set membership crash on a hostile shape.
        cid_ok = isinstance(cid, str) and cid in ids
        if not cid_ok:
            errs.append("X5 claim-ladder provenance: %s.claim_id=%r is not a declared spine subclaim "
                        "(declared: %s)" % (where, cid, ", ".join(sorted(ids)) or "none"))
            continue
        # X6 — label byte-equal to the subclaim string minus its leading Cn token (the same token
        # spine_subclaim_ids consumed). A non-matching label is an "invented data point". The label
        # must BE a string (X1/X6 require a byte-for-byte copy of a string) — a non-string label is
        # refused outright, not str()-coerced (str(123) == str("123") would smuggle a numeric label
        # past the provenance check; the closed allowlist only validates keys, never value types).
        mlabel = it.get("label")
        want_label = labels.get(cid)
        if not isinstance(mlabel, str) or mlabel != want_label:
            errs.append("X6 no orphan datum: %s.label=%r != the subclaim string minus its leading "
                        "%s token %r (manifest must copy verbatim as a string)"
                        % (where, mlabel, cid, want_label))
        # X1/X6 — support[] items: closed allowlist + enum, byte-equal to a real support_plan.v1 block.
        sup = it.get("support")
        if not isinstance(sup, list):
            errs.append("X1 new-array schema: %s.support must be an array" % where)
            continue
        # X6 multiplicity: the manifest's support multiset for this claim must be a SUB-multiset of the
        # producer's. Consume a working copy as each pairing matches — so listing a pairing MORE times
        # than support_plan.v1 contains (over-drawing a chip the source never had a second of) fails the
        # same way a fabricated pairing does (a value the source did not contain — the E5/X7 concern).
        unconsumed = [(p["support_type"], p["status"]) for p in support_src.get(cid, [])]
        for j, su in enumerate(sup):
            swhere = "%s.support[%d]" % (where, j)
            if not isinstance(su, dict):
                errs.append("X1 new-array schema: %s must be an object" % swhere)
                continue
            for k in ("support_type", "status"):
                if k not in su:
                    errs.append("X1 new-array schema: %s missing required field '%s'" % (swhere, k))
            for k in su:
                if k not in _SUPPORT_ITEM_KEYS:
                    errs.append("X1 new-array schema: %s has disallowed field '%s' "
                                "(support[] copies only support_type + status from support_plan.v1)"
                                % (swhere, k))
            if su.get("support_type") not in _SUPPORT_TYPE_ENUM and "support_type" in su:
                errs.append("X1 new-array schema: %s.support_type=%r not in the support_plan.v1 set %s"
                            % (swhere, su.get("support_type"), list(_SUPPORT_TYPE_ENUM)))
            if su.get("status") not in _SUPPORT_STATUS_ENUM and "status" in su:
                errs.append("X1 new-array schema: %s.status=%r not in {in-hand, to-acquire}"
                            % (swhere, su.get("status")))
            # X6 — this pairing must exist (and not already be consumed) in the support_plan.v1 blocks.
            key = (su.get("support_type"), su.get("status"))
            if key in unconsumed:
                unconsumed.remove(key)   # one manifest chip per one producer block
            else:
                errs.append("X6 no orphan datum: %s pairing %r has no (remaining) matching "
                            "apodictic.support_plan.v1 block with subclaim_id=%s (the manifest copies one "
                            "chip per support block — it may not invent or over-draw a pairing)"
                            % (swhere, {"support_type": key[0], "status": key[1]}, cid))
        # X6 completeness: the manifest's support[] must be an EXACT multiset of the producer's, not merely
        # a sub-multiset — every support_plan.v1 block must be copied (one chip per block). A pairing left
        # in `unconsumed` was SILENTLY OMITTED; dropping a "to-acquire" chip renders the claim as better
        # supported than the plan declares (the omission-direction mirror of the over-draw check above). An
        # all-empty support[] is reported by the more specific X5 bare-assertion check below, not here.
        if sup and unconsumed:
            errs.append("X6 no orphan datum: %s.support omits %d apodictic.support_plan.v1 pairing(s) for "
                        "%s (%s) — the manifest must copy every support block, not a subset (a dropped "
                        "'to-acquire' chip over-states the claim's support coverage)"
                        % (where, len(unconsumed), cid,
                           ", ".join("%s/%s" % p for p in sorted(unconsumed))))
        # X5 — an EMPTY support[] is permitted ONLY for a bare assertion (no support_plan declares cid).
        if not sup and cid in planned:
            errs.append("X5 claim-ladder provenance: %s.support is empty but apodictic.support_plan.v1 "
                        "blocks DO declare %s — an empty support[] is permitted only for a bare assertion "
                        "(a subclaim the support plan never covers)" % (where, cid))
    return errs


def _check_co_presence(items, roster, rows):
    """X1/X2/X7/X8 for the co_presence[] array (chart 5). `items` is the manifest's co_presence list
    (each {scene_id, characters:[bare canonical name strings]}); `roster` is scene_roster()'s producer
    source; `rows` is the Timeline rows index (scene_id -> {pov, ...}). Returns errs.

    The manifest carries BARE NAMES; the auditable {name, anchor} richness lives in the producer. X2
    byte-checks the manifest names are a subset of the producer roster's CANONICAL names for that
    scene_id, that every scene_id resolves to a producer roster AND a Timeline row, and that the
    Timeline POV character is present in the roster. The anchor-non-empty check (X2(d)) runs in
    scene_roster() and surfaces via roster['obj_errs']. The present-vs-mentioned READING itself is
    producer-/author-enforced; the gate polices provenance + anchor, never the prose."""
    errs = []
    if not isinstance(items, list):
        errs.append("X1 new-array schema: co_presence must be an array")
        return errs
    if not items:
        return errs
    # X8 — producer-present: a co_presence array can exist ONLY if its scene_roster.v1 producer
    # resolves (the firewall's teeth — no producer, no roster to byte-check against).
    if not roster.get("present"):
        errs.append("X8 producer-present: co_presence[] is present but no resolvable "
                    "apodictic.scene_roster.v1 producer was found to byte-check it against "
                    "(render-what-you-produce: the producer must exist)")
        # Still surface any nested-object errors from a malformed producer (more actionable than X8 alone).
        errs += roster.get("obj_errs") or []
        return errs
    # X2(d) + nested-object schema — anchor-non-empty / closed allowlists / alias shape, from the producer.
    errs += roster.get("obj_errs") or []
    # X1 — per-object allowlist on the manifest array (a visual-style / scene-axis-extra key fails).
    errs += _check_objects(items, "co_presence", _CO_PRESENCE_KEYS, ("scene_id", "characters"),
                           gate="X1 new-array schema")
    # X7 — a scene_id appears at most once in co_presence (a repeat double-draws its edges).
    errs += _dup_errs([it for it in items if isinstance(it, dict)], "scene_id", "scene_id",
                      gate="X7 duplicate entry")
    roster_names = roster.get("names") or {}     # scene_id -> [canonical names] (producer)
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            continue
        where = "co_presence[%d]" % i
        sid = it.get("scene_id")
        # X2(a) — scene_id must match a producer roster AND resolve to a Timeline Event-Ledger row.
        sid_key = art.fid_key(sid)
        in_roster = isinstance(sid, str) and sid in roster_names
        in_timeline = sid_key in rows
        if not in_roster:
            errs.append("X2 co-presence provenance: %s.scene_id=%r matches no apodictic.scene_roster.v1 "
                        "roster entry (the manifest must copy a scene the producer rostered)" % (where, sid))
        if not in_timeline:
            errs.append("X2 co-presence provenance: %s.scene_id=%r resolves to no Timeline Event-Ledger "
                        "row (a co-presence scene must be a real Timeline scene)" % (where, sid))
        if not in_roster:
            continue
        prod_names = roster_names.get(sid, [])
        prod_set = set(prod_names)
        scene_anchors = (roster.get("anchors") or {}).get(sid, {})
        # The scene's Timeline line-range (e.g. "1-118"), parsed once for the anchor-bounding check.
        scene_lr = _parse_line_range((rows.get(sid_key) or {}).get("line_range", "")) if in_timeline else None
        chars = it.get("characters")
        if not isinstance(chars, list):
            errs.append("X1 new-array schema: %s.characters must be an array" % where)
            continue
        for c in chars:
            # X1 — a co_presence character is a BARE NAME STRING (the {name, anchor} richness is the
            # producer's, not the manifest's). A non-string is itself a failure.
            if not isinstance(c, str):
                errs.append("X1 new-array schema: %s.characters item %r must be a bare name string "
                            "(the auditable {name, anchor} lives in the scene_roster.v1 producer)"
                            % (where, c))
                continue
            # X2(b) — every co_presence name must be in that scene's producer roster (canonical) names.
            if c not in prod_set:
                errs.append("X2 co-presence provenance: %s character %r is not in scene %r's "
                            "apodictic.scene_roster.v1 roster names [%s] (a co-presence name must be a "
                            "rostered, present character — not a mentioned/invented one)"
                            % (where, c, sid, ", ".join(sorted(prod_set)) or "none"))
                continue
            # X2(e) — line-range anchor bounding (a PARTIAL tightening of anchor-truthfulness, NOT a
            # claim that prose is gated). When the producer anchor is line-range-shaped ("lines N-M …"),
            # assert N-M overlaps the scene's Timeline line-range — an anchor that points OUTSIDE the
            # scene cannot witness on-page presence within it. A QUOTE-form anchor (no leading line
            # range) is SKIPPED silently — the schema permits it and it can't be mechanically bounded.
            # The prose present-vs-mentioned reading stays trusted/author-accountable exactly as before.
            anc_lr = _parse_line_range(scene_anchors.get(c, ""))
            if anc_lr is not None and scene_lr is not None and not _ranges_overlap(anc_lr, scene_lr):
                errs.append("X2 co-presence provenance: character %r anchor lines %d-%d fall outside "
                            "scene %r Timeline line-range %d-%d (a line-range anchor must witness "
                            "on-page presence WITHIN the scene — quote-form anchors are not bounded)"
                            % (c, anc_lr[0], anc_lr[1], sid, scene_lr[0], scene_lr[1]))
        # X2(c) — the scene's Timeline POV character must be present in its producer roster (cross-check:
        # the POV is by definition on-page, so a roster missing its own POV is an extraction error).
        if in_timeline:
            pov = (rows.get(sid_key) or {}).get("pov", "")
            if pov and pov not in prod_set:
                errs.append("X2 co-presence provenance: scene %r's Timeline POV character %r is absent "
                            "from its apodictic.scene_roster.v1 roster [%s] (the POV is on-page by "
                            "definition — a roster missing its own POV is an extraction error)"
                            % (sid, pov, ", ".join(sorted(prod_set)) or "none"))
    return errs


def _check_scene_functions(items, sfunc, rows):
    """X1/X3/X7/X8 for the scene_functions[] array (chart 6). `items` is the manifest's scene_functions
    list (each {scene_id, function}); `sfunc` is scene_functions_producer()'s source; `rows` is the
    Timeline rows index (scene_id -> {line_range, ...}). Returns errs.

    The manifest carries a BARE {scene_id, function}; the auditable `anchor` richness lives in the
    producer (the same split as co_presence). X3 byte-checks the manifest function is EQUAL to the
    producer's classification for that scene_id, that every scene_id resolves to a producer entry AND a
    Timeline row, and (via the producer's obj_errs) that every function is in the closed scene-turn enum
    and every anchor is non-empty. The author-enforced function READING itself is producer-/author-
    enforced; the gate polices provenance + anchor + enum, never the prose."""
    errs = []
    if not isinstance(items, list):
        errs.append("X1 new-array schema: scene_functions must be an array")
        return errs
    if not items:
        return errs
    # X8 — producer-present: a scene_functions array can exist ONLY if its scene_function.v1 producer
    # resolves (the firewall's teeth — no producer, nothing to byte-check against).
    if not sfunc.get("present"):
        errs.append("X8 producer-present: scene_functions[] is present but no resolvable "
                    "apodictic.scene_function.v1 producer was found to byte-check it against "
                    "(render-what-you-produce: the producer must exist)")
        # Still surface any nested-object errors from a malformed producer (more actionable than X8 alone).
        errs += sfunc.get("obj_errs") or []
        return errs
    # X3(b/d) + nested-object schema — function-in-enum / anchor-non-empty / closed allowlist / dup, from
    # the producer.
    errs += sfunc.get("obj_errs") or []
    # X1 — per-object allowlist on the manifest array (a visual-style / extra key fails).
    errs += _check_objects(items, "scene_functions", _SCENE_FUNCTION_KEYS, ("scene_id", "function"),
                           gate="X1 new-array schema")
    # X7 — a scene_id appears at most once in scene_functions (a repeat double-draws its heatmap row).
    errs += _dup_errs([it for it in items if isinstance(it, dict)], "scene_id", "scene_id",
                      gate="X7 duplicate entry")
    prod_functions = sfunc.get("functions") or {}   # scene_id -> function token (producer)
    prod_anchors = sfunc.get("anchors") or {}
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            continue
        where = "scene_functions[%d]" % i
        sid = it.get("scene_id")
        sid_key = art.fid_key(sid)
        in_prod = isinstance(sid, str) and sid in prod_functions
        in_timeline = sid_key in rows
        # X3(a) — scene_id must match a producer classification AND resolve to a Timeline Event-Ledger row.
        if not in_prod:
            errs.append("X3 scene-function provenance: %s.scene_id=%r matches no apodictic.scene_function.v1 "
                        "classification (the manifest must copy a scene the producer classified)" % (where, sid))
        if not in_timeline:
            errs.append("X3 scene-function provenance: %s.scene_id=%r resolves to no Timeline Event-Ledger "
                        "row (a scene-function scene must be a real Timeline scene)" % (where, sid))
        if not in_prod:
            continue
        # X3(c) — the manifest function must be byte-equal to the producer's classification (verbatim copy;
        # not a computed or relabelled category — the same E4/X6 no-orphan-datum discipline).
        mfn = it.get("function")
        pfn = prod_functions.get(sid)
        if mfn != pfn:
            errs.append("X3 scene-function provenance: %s.function=%r != the apodictic.scene_function.v1 "
                        "classification %r for scene %r (the manifest must copy the producer verbatim)"
                        % (where, mfn, pfn, sid))
        # X3(e) — line-range anchor bounding (a PARTIAL tightening of anchor-truthfulness, mirroring the
        # co-presence X2(e)). When the producer anchor is line-range-shaped ("lines N-M …"), assert N-M
        # overlaps the scene's Timeline line-range — an anchor pointing OUTSIDE the scene cannot witness
        # its function. A QUOTE-form anchor (no leading line range) is SKIPPED silently.
        if in_timeline:
            scene_lr = _parse_line_range((rows.get(sid_key) or {}).get("line_range", ""))
            anc_lr = _parse_line_range(prod_anchors.get(sid, ""))
            if anc_lr is not None and scene_lr is not None and not _ranges_overlap(anc_lr, scene_lr):
                errs.append("X3 scene-function provenance: scene %r anchor lines %d-%d fall outside its "
                            "Timeline line-range %d-%d (a line-range anchor must witness the function "
                            "WITHIN the scene — quote-form anchors are not bounded)"
                            % (sid, anc_lr[0], anc_lr[1], scene_lr[0], scene_lr[1]))
    return errs


def check(manifest_text, timeline_text, ledger_text, spine_text=None, roster_text=None,
          scene_function_text=None, strict=False, require_block=False):
    """Run the manifest<->source provenance checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    obj, schema_errs = parse_manifest(manifest_text)
    if not isinstance(obj, dict):
        # A present-but-unparseable/non-object block is an E1 failure, NOT a no-op — otherwise corrupt
        # JSON or a non-object payload (e.g. [1,2,3]) passes silently / reaches obj.get() and crashes.
        # RETAINS #141's non-object guard (do NOT revert to `obj is None` when reconciling the branches).
        if obj is not None or any("invalid JSON" in e for e in schema_errs):
            return 1, ["manuscript-viz: %s" % (schema_errs[0] if schema_errs else "manifest block is not a JSON object"),
                       "manuscript-viz: FAIL (E1 manifest schema)"]
        # A genuinely-absent block is a no-op for a run folder, but --require-block (the canonical-
        # example gate) makes it a hard failure so the gate cannot pass with no manifest to validate.
        if require_block:
            return 1, ["manuscript-viz: no viz_manifest block found, but --require-block is set "
                       "(a gated manifest must be present and valid)",
                       "manuscript-viz: FAIL (E1 — required manifest block missing)"]
        return 0, ["manuscript-viz: no viz_manifest block found — nothing to validate"]

    # E1 — wrapper schema + nested-object allowlist
    for e in schema_errs:
        errs.append("E1 manifest schema: %s" % e)
    for k in obj:
        if k not in _TOP_KEYS:
            errs.append("E1 manifest schema: top-level has disallowed field '%s'" % k)
    scenes = obj.get("scenes") if isinstance(obj.get("scenes"), list) else []
    findings = obj.get("findings") if isinstance(obj.get("findings"), list) else []
    errs += _check_objects(obj.get("scenes"), "scenes", _SCENE_KEYS, _SCENE_KEYS)
    errs += _check_objects(obj.get("findings"), "findings", _FINDING_KEYS, _FINDING_KEYS)

    # E5 — no duplicate manifest entries. A repeated scene_id double-draws the pacing bar and inflates
    # the POV time-share; a repeated finding id double-counts a chapter's severity bar — a chart showing
    # a value the sources did NOT contain. The per-id E2/E4 checks pass on duplicates (each copy resolves
    # and byte-matches), so uniqueness needs its own gate.
    errs += _dup_errs(scenes, "scene_id", "scene_id")
    errs += _dup_errs(findings, "id", "finding id")

    rows = timeline_rows(timeline_text)
    led = ledger_findings(ledger_text)

    # E2 — provenance closure + E4 — byte-equal copy fidelity (scenes)
    for sc in scenes:
        if not isinstance(sc, dict):
            continue
        # art.fid_key: a non-hashable scene_id must not crash rows.get() (rows is keyed by string
        # scene-ids, so a coerced id still ties; a malformed one fails E2 below as a non-match).
        sid = art.fid_key(sc.get("scene_id"))
        src = rows.get(sid)
        if src is None:
            errs.append("E2 provenance closure: scene %r resolves to no Timeline Event-Ledger row" % sid)
            continue
        for f in ("chapter", "line_range", "word_count", "pov", "span", "gap"):
            if str(sc.get(f, "")) != src[f]:
                errs.append("E4 no orphan data: scene %s.%s=%r != Timeline cell %r (manifest must copy verbatim)"
                            % (sid, f, sc.get(f), src[f]))

    # E2 — provenance closure + chapter honesty + E4 — copy fidelity (findings)
    for fd in findings:
        if not isinstance(fd, dict):
            continue
        fid = art.fid_key(fd.get("id"))   # non-hashable finding id must not crash led.get() (E2 lookup)
        src = led.get(fid)
        if src is None:
            errs.append("E2 provenance closure: finding %r resolves to no apodictic.finding.v1 in the Ledger" % fid)
            continue
        want_chapter = chapter_of(src)
        if str(fd.get("chapter", "")) != want_chapter:
            errs.append("E2 provenance closure: finding %s.chapter=%r != the conservative evidence_refs parse %r "
                        "(no guessed placement)" % (fid, fd.get("chapter"), want_chapter))
        for f in ("severity", "confidence"):
            if str(fd.get(f, "")) != str(src.get(f, "")):
                errs.append("E4 no orphan data: finding %s.%s=%r != source block %r"
                            % (fid, f, fd.get(f), src.get(f)))

    # E3 — every body Must-Fix in the ledger appears in findings[]
    # art.fid_key: coerce before the set build — a non-hashable id would crash the set comprehension.
    manifest_ids = {art.fid_key(fd.get("id")) for fd in findings if isinstance(fd, dict)}
    for fid, src in sorted(led.items()):
        if src.get("severity") == "Must-Fix" and fid not in manifest_ids:
            errs.append("E3 Must-Fix completeness: ledger Must-Fix %s is absent from findings[] "
                        "(the render cannot drop a locked severity)" % fid)

    # W1 — coverage: a Timeline row not represented in scenes[]
    scene_ids = {art.fid_key(sc.get("scene_id")) for sc in scenes if isinstance(sc, dict)}
    for sid in sorted(rows):
        if sid not in scene_ids:
            warns.append("W1 coverage: Timeline scene %s is not in scenes[] (silent under-render)" % sid)

    # W2 — scene order: the manifest scenes[] order should follow the Timeline's document order. The
    # pacing curve's x-axis is raw scenes[] order, so a reordered manifest draws a false pacing shape
    # while passing every per-id check (order is a data channel the set-based checks don't close).
    mf_order = [art.fid_key(sc.get("scene_id")) for sc in scenes
                if isinstance(sc, dict) and art.fid_key(sc.get("scene_id")) in rows]
    tl_subset = [sid for sid in rows if sid in set(mf_order)]   # rows preserves Timeline document order
    if mf_order != tl_subset:
        _fmt = lambda seq: ", ".join("'%s'" % s for s in seq)   # scene ids contain spaces — quote them
        warns.append("W2 scene order: scenes[] order [%s] diverges from the Timeline document order "
                     "[%s] — the pacing curve's shape must come from the Timeline, not the manifest"
                     % (_fmt(mf_order), _fmt(tl_subset)))

    # ---- Manuscript-Visualization Completion (charts 4-7): X1/X2/X5/X6/X7/X8 + W3 ----
    # The four arrays are OPTIONAL and additive. Two are rendered: chart 7-nonfiction (claim_ladder,
    # producer apodictic.argument_spine.v1 + support_plan.v1) and chart 5 (co_presence, producer
    # apodictic.scene_roster.v1). The other two stay producer-gated — their producers (scene_function /
    # tension_point) do not exist yet, so a PRESENT array for them fails X8 (you cannot ship a chart
    # array without the producer to byte-check it against). Absent arrays are skipped (a partial map
    # is legitimate — the same posture as W1 coverage).
    ladder = spine_ladder(spine_text)
    claim_ladder = obj.get("claim_ladder")
    if claim_ladder is not None:
        errs += _check_claim_ladder(claim_ladder, ladder)
    # Chart 5 — co_presence byte-checked against the scene_roster.v1 producer + the Timeline (X1/X2/X7/X8).
    roster = scene_roster(roster_text)
    co_presence = obj.get("co_presence")
    if co_presence is not None:
        errs += _check_co_presence(co_presence, roster, rows)
    # Chart 6 — scene_functions byte-checked against the scene_function.v1 producer + the Timeline
    # (X1/X3/X7/X8). The producer classifies each Timeline scene into the closed scene-turn function set.
    sfunc = scene_functions_producer(scene_function_text)
    scene_functions = obj.get("scene_functions")
    if scene_functions is not None:
        errs += _check_scene_functions(scene_functions, sfunc, rows)
    # X8 — the ONE still-producer-gated array (reveal_points) has no producer yet, so a present array is a
    # hard fail. (scene_functions now has apodictic.scene_function.v1 — wired above; co_presence has
    # scene_roster.v1; claim_ladder has argument_spine.v1.)
    for arr_key, prod in (("reveal_points", "apodictic.tension_point.v1"),):
        arr = obj.get(arr_key)
        if arr:   # present and non-empty
            errs.append("X8 producer-present: %s[] is present but its producer (%s) does not exist "
                        "yet — this chart is producer-gated and cannot be rendered render-first "
                        "(doing so would fabricate data)" % (arr_key, prod))
    # W3 — chart coverage: a producer is present but its array is empty/absent — the data exists but
    # the chart was silently dropped. Advisory. (claim ladder: argument_spine.v1 with subclaims;
    # co-presence: scene_roster.v1 with rostered scenes; scene-function: scene_function.v1 with classes.)
    if ladder.get("present") and ladder.get("ids") and not claim_ladder:
        warns.append("W3 chart coverage: an apodictic.argument_spine.v1 with %d declared subclaim(s) "
                     "is present but claim_ladder[] is empty/absent — the claim ladder is renderable "
                     "but was dropped (silent under-rendering)" % len(ladder.get("ids")))
    if roster.get("present") and roster.get("names") and not co_presence:
        warns.append("W3 chart coverage: an apodictic.scene_roster.v1 with %d rostered scene(s) is "
                     "present but co_presence[] is empty/absent — the co-presence network is renderable "
                     "but was dropped (silent under-rendering)" % len(roster.get("names")))
    if sfunc.get("present") and sfunc.get("functions") and not scene_functions:
        warns.append("W3 chart coverage: an apodictic.scene_function.v1 with %d classified scene(s) is "
                     "present but scene_functions[] is empty/absent — the scene-function heatmap is "
                     "renderable but was dropped (silent under-rendering)" % len(sfunc.get("functions")))

    # Report
    lines.append("manuscript-viz: %s — %d scene(s), %d finding(s)%s%s%s%s"
                 % (obj.get("project", "?"), len(scenes), len(findings),
                    ", %d claim rung(s)" % len(claim_ladder) if claim_ladder else "",
                    ", %d co-presence scene(s)" % len(co_presence) if co_presence else "",
                    ", %d scene-function scene(s)" % len(scene_functions) if scene_functions else "",
                    " [partial]" if obj.get("partial") else ""))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("manuscript-viz: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: manuscript-viz: %d advisory flag(s) — see W1/W2/W3 above" % len(warns))
    else:
        lines.append("manuscript-viz: PASS (manifest<->source provenance: schema + closure + Must-Fix + verbatim copy + uniqueness + claim-ladder + co-presence + scene-function)")
    return 0, lines


# ---------------------------------------------------------------- render (charts 1-3)

def _bars_svg(pairs, width=680, height=160, pad=28):
    """A labelled bar chart from [(label, value, color)]; deterministic inline SVG."""
    if not pairs:
        return '<svg width="%d" height="40"><text x="0" y="20" fill="#7A7560">no data</text></svg>' % width
    vmax = max(v for _, v, _ in pairs) or 1
    n = len(pairs)
    bw = (width - 2 * pad) / n
    bars = []
    for i, (label, val, color) in enumerate(pairs):
        bh = (height - 2 * pad) * (val / vmax)
        x = pad + i * bw + bw * 0.12
        y = height - pad - bh
        w = bw * 0.76
        bars.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" rx="2"/>'
                    % (x, y, w, bh, color))
        bars.append('<text x="%.1f" y="%.1f" font-size="10" fill="#7A7560" text-anchor="middle">%s</text>'
                    % (x + w / 2, height - pad + 12, html.escape(str(label))))
        bars.append('<text x="%.1f" y="%.1f" font-size="9" fill="#9E9680" text-anchor="middle">%s</text>'
                    % (x + w / 2, y - 4, html.escape(str(val))))
    return ('<svg width="%d" height="%d" role="img">%s'
            '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#D1C8AC"/></svg>'
            % (width, height, "".join(bars), pad, height - pad, width - pad, height - pad))


# Hardcoded support-status -> chip encoding (renderer-owned; the manifest never carries style — same
# discipline as _SEV_ENCODING). in-hand reads "settled," to-acquire reads "still open."
_SUPPORT_STATUS_STYLE = {
    "in-hand":    {"bg": "#D6E4D2", "fg": "#2F5233"},
    "to-acquire": {"bg": "#EFE1C6", "fg": "#7A5A1E"},
}


def _claim_ladder_svg(thesis, rungs, width=680):
    """Chart 7-nonfiction — the claim ladder. `thesis` is C0 (from argument_spine.v1.thesis); `rungs`
    is [(claim_id, label, [(support_type, status), ...]), ...] (a bare assertion has an empty list).
    Deterministic inline SVG; no network, no model. Each support unit is one chip (type +
    in-hand/to-acquire); a rung with no support shows a 'bare assertion' pill (the W2 analogue)."""
    row_h, top = 64, 88
    height = top + max(1, len(rungs)) * row_h + 16
    x_id, x_label, rail = 24, 92, 60
    out = []
    # The spine rail + the C0 (thesis) root node.
    out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#C8BE9E" stroke-width="2"/>'
               % (rail, 40, rail, height - 24))
    out.append('<circle cx="%d" cy="40" r="6" fill="#3B4A3E"/>' % rail)
    out.append('<text x="%d" y="34" font-size="11" font-weight="600" fill="#3B4A3E">C0 (thesis)</text>' % (rail + 14))
    out.append('<text x="%d" y="50" font-size="12" fill="#33311E">%s</text>'
               % (rail + 14, html.escape(str(thesis or "(no thesis)"))))
    for i, (cid, label, support) in enumerate(rungs):
        cy = top + i * row_h + 18
        out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#C8BE9E"/>' % (rail, cy, x_label - 8, cy))
        out.append('<circle cx="%d" cy="%d" r="5" fill="#5E8C6A"/>' % (rail, cy))
        out.append('<text x="%d" y="%d" font-size="11" font-weight="600" fill="#3B4A3E">%s</text>'
                   % (x_id, cy + 4, html.escape(str(cid))))
        out.append('<text x="%d" y="%d" font-size="12" fill="#33311E">%s</text>'
                   % (x_label, cy + 4, html.escape(str(label or ""))))
        # Support chips (one per support unit), or a "bare assertion" pill when none.
        cx = x_label
        chip_y = cy + 12
        if support:
            for stype, status in support:
                style = _SUPPORT_STATUS_STYLE.get(status, {"bg": "#E3DDC9", "fg": "#5A5436"})
                txt = "%s · %s" % (stype, status)
                cw = 9 + len(txt) * 6.4
                out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="18" rx="9" fill="%s"/>'
                           % (cx, chip_y, cw, style["bg"]))
                out.append('<text x="%.1f" y="%.1f" font-size="10" fill="%s">%s</text>'
                           % (cx + 6, chip_y + 13, style["fg"], html.escape(txt)))
                cx += cw + 8
        else:
            txt = "bare assertion"
            cw = 9 + len(txt) * 6.4
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="18" rx="9" fill="#F0D7DC" '
                       'stroke="#A8344A" stroke-dasharray="2 2"/>' % (cx, chip_y, cw))
            out.append('<text x="%.1f" y="%.1f" font-size="10" fill="#8C2A3D">%s</text>'
                       % (cx + 6, chip_y + 13, html.escape(txt)))
    return '<svg width="%d" height="%d" role="img">%s</svg>' % (width, height, "".join(out))


# Hardcoded co-presence weight -> chord stroke-width band (renderer-owned; the manifest never carries
# style — the same discipline as _SEV_ENCODING / _SUPPORT_STATUS_STYLE). The weight is the count of
# shared scenes, computed MECHANICALLY from the rosters; this map turns that count into a thickness
# band, it is never read from the manifest. Bands keep a 7-shared-scene chord from drowning the chart.
def _co_presence_weight_width(weight):
    """A shared-scene count -> chord stroke width (px), from a fixed band map. Monotone in weight."""
    if weight <= 1:
        return 1.4
    if weight == 2:
        return 2.6
    if weight <= 4:
        return 3.8
    return 5.0


def co_presence_graph(co_presence):
    """Mechanically derive (nodes, edges) from the manifest's co_presence[] (already X2-byte-checked).

    nodes: sorted list of every distinct character name appearing in ANY scene's characters[] (a solo
    character keeps its node — never dropped). edges: {(a, b): weight} for a<b, weight = the count of
    scenes whose roster contains BOTH a and b. No judgement: an edge iff co-occurrence >=1; weight =
    count. Deterministic (sorted nodes; canonical-ordered pair keys)."""
    nodes, edges = set(), {}
    for entry in co_presence or []:
        if not isinstance(entry, dict):
            continue
        names = sorted({c for c in (entry.get("characters") or []) if isinstance(c, str) and c})
        for n in names:
            nodes.add(n)
        for a in range(len(names)):
            for b in range(a + 1, len(names)):
                key = (names[a], names[b])   # names is sorted, so a < b lexically — canonical pair key
                edges[key] = edges.get(key, 0) + 1
    return sorted(nodes), edges


def _co_presence_svg(nodes, edges, width=680):
    """Chart 5 — the character co-presence network. DETERMINISTIC circular layout: nodes equally
    spaced on a circle (alphabetical order — no force sim, no randomness); a chord for each shared-
    scene edge, chord thickness from the hardcoded weight band; a solo character renders as an isolated
    node (drawn, never dropped). Single-file inline SVG; no network, no model. `nodes`/`edges` come
    from co_presence_graph (computed mechanically from the byte-checked rosters)."""
    import math
    n = len(nodes)
    height = 420 if n else 60
    if not nodes:
        return ('<svg width="%d" height="60" role="img"><text x="0" y="30" fill="#7A7560">'
                'no co-presence data</text></svg>' % width)
    cx, cy = width / 2.0, height / 2.0
    r = min(width, height) / 2.0 - 70   # leave a margin for labels
    pos = {}
    for i, name in enumerate(nodes):
        # Start at the top (-90deg) and go clockwise — a fixed, reproducible placement.
        ang = -math.pi / 2 + (2 * math.pi * i / n)
        pos[name] = (cx + r * math.cos(ang), cy + r * math.sin(ang), ang)
    out = []
    # Edges first (so nodes draw on top). A straight chord between the two endpoints; thickness banded.
    for (a, b), w in sorted(edges.items()):
        if a not in pos or b not in pos:
            continue
        x1, y1, _ = pos[a]
        x2, y2, _ = pos[b]
        sw = _co_presence_weight_width(w)
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#8B7E5A" '
                   'stroke-width="%.1f" stroke-opacity="0.55"/>' % (x1, y1, x2, y2, sw))
        # weight label at the chord midpoint (the shared-scene count — a copied fact, not a judgement)
        mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        out.append('<text x="%.1f" y="%.1f" font-size="9" fill="#9E9680" text-anchor="middle">%d</text>'
                   % (mx, my, w))
    # Nodes + labels.
    for name in nodes:
        x, y, ang = pos[name]
        out.append('<circle cx="%.1f" cy="%.1f" r="6" fill="#3B4A3E"/>' % (x, y))
        # Label pushed radially outward; anchor by hemisphere so text doesn't overrun the circle.
        lx = x + 12 * math.cos(ang)
        ly = y + 12 * math.sin(ang) + 4
        anchor = "start" if math.cos(ang) >= 0 else "end"
        out.append('<text x="%.1f" y="%.1f" font-size="11" fill="#33311E" text-anchor="%s">%s</text>'
                   % (lx, ly, anchor, html.escape(str(name))))
    return '<svg width="%d" height="%d" role="img">%s</svg>' % (width, height, "".join(out))


# Hardcoded scene-function -> cell encoding (renderer-owned; the manifest never carries style — the same
# discipline as _SEV_ENCODING / _SUPPORT_STATUS_STYLE / the co-presence band). The function token is the
# author's classification, copied verbatim; this map turns it into a cell color + a fixed column, never
# read from the manifest. The column ORDER is the scene-turn Step-1 Unit-Classification taxonomy order.
_SCENE_FUNCTION_ORDER = ("scene", "sequel", "hybrid", "non-unit")
_SCENE_FUNCTION_ENCODING = {
    "scene":    {"color": "#3B4A3E", "label": "Scene"},
    "sequel":   {"color": "#5E8C6A", "label": "Sequel"},
    "hybrid":   {"color": "#8B5E3C", "label": "Hybrid"},
    "non-unit": {"color": "#A8344A", "label": "Non-unit"},
}


def scene_function_grid(scene_functions):
    """Mechanically derive [(scene_id, function), ...] from the manifest's scene_functions[] (already
    X3-byte-checked), preserving manifest order (= Timeline order after the gate). No judgement: one row
    per scene, its single declared function. A function outside the known set is dropped from the grid
    (the gate already failed it — the render never invents a column)."""
    grid = []
    for entry in scene_functions or []:
        if not isinstance(entry, dict):
            continue
        sid = entry.get("scene_id")
        fn = entry.get("function")
        if isinstance(sid, str) and sid and fn in _SCENE_FUNCTION_ENCODING:
            grid.append((sid, fn))
    return grid


def _scene_function_svg(grid, width=680):
    """Chart 6 — the scene-function heatmap. DETERMINISTIC scenes x functions grid: one row per scene (in
    manifest/Timeline order), one column per scene-turn function (fixed Step-1 order); the single cell at
    (scene, its function) is shaded from the hardcoded function->color band, the rest read as page-empty.
    Single-file inline SVG; no network, no model. `grid` comes from scene_function_grid (computed
    mechanically from the byte-checked classifications)."""
    cols = _SCENE_FUNCTION_ORDER
    label_w, top, row_h = 150, 44, 26
    if not grid:
        return ('<svg width="%d" height="60" role="img"><text x="0" y="30" fill="#7A7560">'
                'no scene-function data</text></svg>' % width)
    cell_w = (width - label_w - 16) / len(cols)
    height = top + len(grid) * row_h + 16
    out = []
    # Column headers (the function names — the closed scene-turn Step-1 taxonomy).
    for j, fn in enumerate(cols):
        cxx = label_w + j * cell_w + cell_w / 2.0
        enc = _SCENE_FUNCTION_ENCODING[fn]
        out.append('<text x="%.1f" y="%d" font-size="10" fill="#7A7560" text-anchor="middle">%s</text>'
                   % (cxx, top - 14, html.escape(enc["label"])))
    # One row per scene: the scene_id label + a shaded cell under its declared function.
    for i, (sid, fn) in enumerate(grid):
        ry = top + i * row_h
        out.append('<text x="0" y="%.1f" font-size="10" fill="#33311E">%s</text>'
                   % (ry + row_h * 0.66, html.escape(str(sid))))
        for j, col in enumerate(cols):
            cxx = label_w + j * cell_w
            filled = (col == fn)
            color = _SCENE_FUNCTION_ENCODING[col]["color"] if filled else "#EDE5D0"
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
                       'stroke="#D1C8AC" stroke-width="0.5"/>'
                       % (cxx, ry + 2, cell_w - 2, row_h - 4, color))
    return '<svg width="%d" height="%d" role="img">%s</svg>' % (width, height, "".join(out))


def render_html(manifest_text, timeline_text, ledger_text, spine_text=None, roster_text=None,
                scene_function_text=None):
    """Pure function of the manifest (+ verbatim sources): a self-contained HTML+inline-SVG file.

    No network, no deps, no model call — render-only. Charts 1-3: pacing curve, POV time-share,
    finding-severity-by-chapter. Chart 7-nonfiction (claim ladder) is drawn when the manifest carries
    a claim_ladder[] array and an apodictic.argument_spine.v1 source resolves (C0 from the spine's
    thesis; rungs + support coverage from the byte-checked manifest array — no scene axis). Severity /
    support-status encodings are hardcoded here, not read from the manifest."""
    obj, _ = parse_manifest(manifest_text)
    if obj is None:
        return "<!doctype html><meta charset=utf-8><title>Structure Map</title><p>No manifest.</p>"
    project = html.escape(str(obj.get("project", "Manuscript")))
    partial = bool(obj.get("partial"))
    scenes = [s for s in (obj.get("scenes") or []) if isinstance(s, dict)]

    def _int(v):
        try:
            return int(re.sub(r"[^0-9]", "", str(v)) or 0)
        except ValueError:
            return 0

    # Chart 1 — pacing / word-count curve (scene order)
    pacing = [(s.get("scene_id", "?"), _int(s.get("word_count")), "#3B4A3E") for s in scenes]
    # Chart 2 — POV time-share (sum word_count by pov)
    pov_tot = {}
    for s in scenes:
        pov_tot[s.get("pov", "?")] = pov_tot.get(s.get("pov", "?"), 0) + _int(s.get("word_count"))
    pov = [(p, v, "#5E8C6A") for p, v in sorted(pov_tot.items(), key=lambda kv: -kv[1])]
    # Chart 3 — finding severity by chapter (count, colored by dominant severity)
    findings = [f for f in (obj.get("findings") or []) if isinstance(f, dict)]
    by_ch = {}
    for f in findings:
        ch = f.get("chapter", "unplaced")
        by_ch.setdefault(ch, []).append(f.get("severity", "Could-Fix"))
    # Numeric-aware chapter order: "Ch 2" before "Ch 10" (lexicographic would put 10 first), with
    # any non-numeric bin (e.g. the literal "unplaced") sorted last.
    def _ch_key(item):
        ch = item[0]
        m = _CHAPTER_RE.search(str(ch))
        return (0, int(m.group(1))) if m else (1, str(ch))
    sev_bars = []
    for ch, sevs in sorted(by_ch.items(), key=_ch_key):
        dom = max(sevs, key=lambda s: _SEV_ENCODING.get(s, {"rank": 0})["rank"])
        color = _SEV_ENCODING.get(dom, {"color": "#7A7560"})["color"]
        sev_bars.append((ch, len(sevs), color))

    legend = " · ".join('<span style="color:%s">&#9632;</span> %s' % (e["color"], html.escape(s))
                        for s, e in sorted(_SEV_ENCODING.items(), key=lambda kv: -kv[1]["rank"]))
    partial_note = ('<p class="partial">⚠ Partial manuscript — the pacing curve is honest but '
                    'incomplete; do not read it as a finished arc.</p>') if partial else ""

    # Chart 7-nonfiction — the claim ladder. Drawn only when the manifest carries a claim_ladder[]
    # array AND an argument_spine.v1 source resolves (C0 = the spine's thesis). The rungs + support
    # coverage come from the byte-checked manifest array (X5/X6 already validated them upstream); the
    # renderer just lays them out. No scene axis.
    claim_section = ""
    ladder_src = spine_ladder(spine_text)
    cl = [c for c in (obj.get("claim_ladder") or []) if isinstance(c, dict)]
    if cl and ladder_src.get("present"):
        rungs = []
        for c in cl:
            support = [(su.get("support_type"), su.get("status"))
                       for su in (c.get("support") or []) if isinstance(su, dict)]
            rungs.append((c.get("claim_id", "?"), c.get("label", ""), support))
        ladder_legend = ('<span class="chip" style="background:#D6E4D2;color:#2F5233">support · in-hand</span> '
                         '<span class="chip" style="background:#EFE1C6;color:#7A5A1E">support · to-acquire</span> '
                         '<span class="chip bare">bare assertion</span>')
        claim_section = ("<h2>Claim ladder (nonfiction)</h2>"
                         "<div class=legend>%s</div>"
                         "<p class=meta>C0 + subclaims with planned-support coverage, copied from the "
                         "argument spine and support plan. This is the <em>declared</em> ladder, not a "
                         "claim-to-scene map.</p>%s"
                         % (ladder_legend, _claim_ladder_svg(ladder_src.get("thesis"), rungs)))

    # Chart 5 — the character co-presence network. Drawn only when the manifest carries a co_presence[]
    # array AND an apodictic.scene_roster.v1 producer resolves (the X2-byte-checked rosters). Nodes +
    # edges are computed MECHANICALLY from the byte-checked array (an edge iff two characters co-occur
    # in >=1 scene; weight = the count of shared scenes); a solo character keeps an isolated node.
    co_presence_section = ""
    roster_src = scene_roster(roster_text)
    cp = [c for c in (obj.get("co_presence") or []) if isinstance(c, dict)]
    if cp and roster_src.get("present"):
        nodes, edges = co_presence_graph(cp)
        co_presence_section = (
            "<h2>Character co-presence network</h2>"
            "<p class=meta>Nodes are characters; an edge means they share a scene; chord thickness is "
            "the count of shared scenes. Computed mechanically from the scene rosters (who is "
            "<em>present and acting</em> on-page, not merely mentioned). A solo character renders as an "
            "isolated node. This is structure, not a judgement about any relationship.</p>%s"
            % _co_presence_svg(nodes, edges))

    # Chart 6 — the scene-function heatmap. Drawn only when the manifest carries a scene_functions[]
    # array AND an apodictic.scene_function.v1 producer resolves (the X3-byte-checked classifications).
    # The grid is computed MECHANICALLY from the byte-checked array (one row per scene, one shaded cell
    # at its declared function); the function->color band is hardcoded here, never read from the manifest.
    scene_function_section = ""
    sfunc_src = scene_functions_producer(scene_function_text)
    sf = [c for c in (obj.get("scene_functions") or []) if isinstance(c, dict)]
    if sf and sfunc_src.get("present"):
        grid = scene_function_grid(sf)
        sf_legend = " · ".join(
            '<span style="color:%s">&#9632;</span> %s' % (_SCENE_FUNCTION_ENCODING[fn]["color"],
                                                          html.escape(_SCENE_FUNCTION_ENCODING[fn]["label"]))
            for fn in _SCENE_FUNCTION_ORDER)
        scene_function_section = (
            "<h2>Scene-function heatmap</h2>"
            "<div class=legend>%s</div>"
            "<p class=meta>One row per scene, one column per scene-turn function "
            "(scene / sequel / hybrid / non-unit); the shaded cell is the scene's declared function, "
            "copied from the scene-function classification. This is the <em>author's</em> classification "
            "made auditable by its anchor, not a judgement the render reached.</p>%s"
            % (sf_legend, _scene_function_svg(grid)))

    return """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1">
<title>Structure Map — {project}</title>
<style>
 body{{font-family:system-ui,sans-serif;background:#EDE5D0;color:#33311E;max-width:760px;margin:0 auto;padding:2rem 1.5rem;line-height:1.6}}
 h1{{font-size:1.4rem;margin:0 0 .25rem}} h2{{font-size:1.05rem;margin:2rem 0 .5rem;border-bottom:1px solid #D1C8AC;padding-bottom:.3rem}}
 .meta{{color:#7A7560;font-size:.85rem;margin-bottom:1rem}} .partial{{color:#8C2A3D;font-size:.9rem}}
 .record{{background:#F4EDDA;border-left:3px solid #8B5E3C;padding:.6rem .9rem;font-size:.85rem;border-radius:0 4px 4px 0}}
 .legend{{font-size:.8rem;color:#7A7560;margin:.4rem 0}} svg{{max-width:100%}}
 .chip{{display:inline-block;padding:.05rem .45rem;border-radius:9px;font-size:.75rem;margin-right:.2rem}}
 .chip.bare{{background:#F0D7DC;color:#8C2A3D;border:1px dashed #A8344A}}
</style></head><body>
<h1>Structure Map — {project}</h1>
<div class=meta>Render-only companion · APODICTIC manuscript-structure visualization (charts 1–3{cp_label}{sf_label}{cl_label})</div>
<div class=record><strong>The editorial letter is the artifact of record.</strong> This is a render of data the
passes already produced — it adds no analysis and no verdict lives only here. Severity encoding is fixed:
a Must-Fix is always rendered at full salience (size never shrinks for low confidence).</div>
{partial_note}
<h2>Pacing — word count by scene</h2>{c1}
<h2>POV time-share</h2>{c2}
<h2>Findings by chapter</h2><div class=legend>{legend}</div>{c3}
{co_presence_section}
{scene_function_section}
{claim_section}
</body></html>""".format(project=project, partial_note=partial_note,
                         c1=_bars_svg(pacing), c2=_bars_svg(pov), c3=_bars_svg(sev_bars), legend=legend,
                         claim_section=claim_section, co_presence_section=co_presence_section,
                         scene_function_section=scene_function_section,
                         cl_label=" + claim ladder" if claim_section else "",
                         cp_label=" + co-presence network" if co_presence_section else "",
                         sf_label=" + scene-function heatmap" if scene_function_section else "")


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    """Return (manifest_path, timeline_path, ledger_path, spine_path, roster_path, scene_function_path)
    from a run folder or files.

    spine_path is the pre-draft Argument_State (the chart 7-nonfiction claim-ladder source), roster_path
    is the per-scene cast (the chart-5 co-presence producer), and scene_function_path is the per-scene
    function classification (the chart-6 heatmap producer); any may be None (a run carrying no producer
    simply doesn't render that chart)."""
    if len(paths) == 1 and os.path.isdir(paths[0]):
        d = paths[0]
        man = _newest(glob.glob(os.path.join(d, _MANIFEST_GLOB)))
        tlp = None
        for g in _TIMELINE_GLOBS:
            tlp = _newest(glob.glob(os.path.join(d, g)))
            if tlp:
                break
        led = _newest(glob.glob(os.path.join(d, _LEDGER_GLOB)))
        spinep = _newest(glob.glob(os.path.join(d, _SPINE_GLOB)))
        rosterp = _newest(glob.glob(os.path.join(d, _ROSTER_GLOB)))
        sfuncp = _newest(glob.glob(os.path.join(d, _SFUNC_GLOB)))
        return man, tlp, led, spinep, rosterp, sfuncp
    man = tlp = led = spinep = rosterp = sfuncp = None
    for p in paths:
        body = _read(p) or ""
        if _has_block(body, "viz_manifest") and man is None:
            man = p
        elif _has_block(body, "scene_roster") and rosterp is None:
            # Check the roster BEFORE the Timeline/finding heuristics — the scene-roster producer
            # carries no pipe-table and no finding block (it would otherwise be mis-detected).
            rosterp = p
        elif _has_block(body, "scene_function") and sfuncp is None:
            # Check the scene-function producer BEFORE the Timeline/finding heuristics — it carries no
            # pipe-table and no finding block, so it would otherwise be mis-detected.
            sfuncp = p
        elif _has_block(body, "argument_spine") and spinep is None:
            # Check the spine BEFORE the Timeline/finding heuristics — the canonical pre-draft
            # Argument_State carries no pipe-table and no finding block, so it falls through to here.
            spinep = p
        elif "scene id" in body.lower() and "|" in body and tlp is None:
            tlp = p
        elif _has_block(body, "finding") and led is None:
            led = p
    if man is None and paths:
        man = paths[0]
    return man, tlp, led, spinep, rosterp, sfuncp


def run(paths, strict=False, require_block=False):
    man, tlp, led, spinep, rosterp, sfuncp = resolve(paths)
    if not man:
        return 2, ["manuscript-viz: no Structure Map manifest found (need a *_Structure_Map_*.md "
                   "or a file with an apodictic:viz_manifest block)"]
    mtext = _read(man)
    if mtext is None:
        return 2, ["manuscript-viz: cannot read %s" % man]
    return check(mtext, _read(tlp) if tlp else None, _read(led) if led else None,
                 spine_text=_read(spinep) if spinep else None,
                 roster_text=_read(rosterp) if rosterp else None,
                 scene_function_text=_read(sfuncp) if sfuncp else None,
                 strict=strict, require_block=require_block)


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

    # non-UTF8 artifact: _read must degrade to the unreadable path (None), never
    # a traceback (the disposition_check adjacent-exception class, swept repo-wide)
    import tempfile as _tf
    _fd, _nu = _tf.mkstemp(suffix=".md")
    with os.fdopen(_fd, "wb") as _fh:
        _fh.write(b"\xff\xfenot utf-8\xff")
    chk("non_utf8_read_returns_none", _read(_nu) is None)
    os.unlink(_nu)

    timeline = ("## Section 1: Event Ledger\n\n"
                "| Scene ID | Chapter / Section | Line range | Word count | POV | Setting | Span | Gap from previous scene |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| Ch 1 §1 | Ch 1 | 1-118 | 1480 | Mara | Kitchen | 3 hours | n/a |\n"
                "| Ch 1 §2 | Ch 1 | 119-240 | 1390 | Mara | Office | 2 hours | 3 hours |\n"
                "| Ch 2 §1 | Ch 2 | 241-372 | 1610 | Jon | Station | 1 hour | 16 hours |\n")

    def finding(fid="F-RR-01", severity="Must-Fix", confidence="HIGH", refs=("Chapter 9",)):
        obj = {"schema": _FINDING_SCHEMA_ID, "id": fid, "mechanism": "m", "severity": severity,
               "confidence": confidence, "evidence_refs": list(refs), "fix_class": "f", "risk_if_fixed": "r"}
        return "<!-- apodictic:finding\n%s\n-->" % _j.dumps(obj)

    ledger = "# Findings Ledger\n" + finding() + "\n"

    def scene(sid, ch, lr, wc, pov, span, gap, extra=None):
        o = {"scene_id": sid, "chapter": ch, "line_range": lr, "word_count": wc, "pov": pov,
             "span": span, "gap": gap}
        if extra:
            o.update(extra)
        return o

    def manifest(scenes=None, findings=None, extra=None):
        if scenes is None:
            scenes = [scene("Ch 1 §1", "Ch 1", "1-118", "1480", "Mara", "3 hours", "n/a"),
                      scene("Ch 1 §2", "Ch 1", "119-240", "1390", "Mara", "2 hours", "3 hours"),
                      scene("Ch 2 §1", "Ch 2", "241-372", "1610", "Jon", "1 hour", "16 hours")]
        if findings is None:
            findings = [{"id": "F-RR-01", "severity": "Must-Fix", "confidence": "HIGH", "chapter": "Ch 9"}]
        o = {"schema": _SCHEMA_ID, "project": "Test", "scenes": scenes, "findings": findings}
        if extra:
            o.update(extra)
        return "<!-- apodictic:viz_manifest\n%s\n-->" % _j.dumps(o)

    # clean
    chk("clean", check(manifest(), timeline, ledger)[0] == 0)
    # regression (Codex #139 round-2): a present-but-non-object manifest block (a JSON array) is an E1
    # failure, not a vacuous pass / crash — retains #141's non-object guard so the branches converge.
    chk("crash_nondict_manifest", check("<!-- apodictic:viz_manifest\n[1,2,3]\n-->", timeline, ledger)[0] == 1)
    # regression (Codex #139 round-3 pre-screen): a NESTED non-hashable scene_id / finding id must not
    # crash check()'s E2 rows.get(sid)/led.get(fid), the E3/W1 set builds, or the W2 `in rows` test —
    # not just _dup_errs. Coerced via art.fid_key, it fails E2 as a non-match (code 1), never a TypeError.
    chk("check_nested_nonhashable_id_no_crash",
        check(manifest(scenes=[scene([1, 2], "Ch 1", "1-118", "1480", "Mara", "3 hours", "n/a")],
                       findings=[{"id": {"x": 1}, "severity": "Must-Fix", "confidence": "HIGH",
                                  "chapter": "Ch 9"}]),
              timeline, ledger)[0] == 1)

    # E1 — disallowed (visual-style) field in a scene, and at top level
    bad_scene = [scene("Ch 1 §1", "Ch 1", "1-118", "1480", "Mara", "3 hours", "n/a", extra={"color": "red"})]
    code, ls = check(manifest(scenes=bad_scene
                              + [scene("Ch 1 §2", "Ch 1", "119-240", "1390", "Mara", "2 hours", "3 hours"),
                                 scene("Ch 2 §1", "Ch 2", "241-372", "1610", "Jon", "1 hour", "16 hours")]),
                     timeline, ledger)
    chk("e1_style_field_scene", code == 1 and any("disallowed field 'color'" in x for x in ls))
    chk("e1_style_field_top",
        check(manifest(extra={"theme": "noir"}), timeline, ledger)[0] == 1)
    chk("e1_missing_scene_field",
        check(manifest(scenes=[{"scene_id": "Ch 1 §1"}]), timeline, ledger)[0] == 1)

    # E2 — scene not in Timeline / finding not in Ledger / wrong chapter parse
    code, ls = check(manifest(scenes=[scene("Ch 9 §9", "Ch 9", "1-2", "10", "X", "1", "n/a")]), timeline, ledger)
    chk("e2_scene_dangling", code == 1 and any("E2" in x and "no Timeline" in x for x in ls))
    code, ls = check(manifest(findings=[{"id": "F-XX-99", "severity": "Must-Fix", "confidence": "HIGH", "chapter": "Ch 9"}]),
                     timeline, ledger)
    chk("e2_finding_dangling", code == 1 and any("E2" in x and "no apodictic.finding" in x for x in ls))
    code, ls = check(manifest(findings=[{"id": "F-RR-01", "severity": "Must-Fix", "confidence": "HIGH", "chapter": "Ch 3"}]),
                     timeline, ledger)
    chk("e2_wrong_chapter", code == 1 and any("E2" in x and "conservative evidence_refs parse" in x for x in ls))

    # E4 — byte mismatch on a copied cell / a copied severity
    code, ls = check(manifest(scenes=[scene("Ch 1 §1", "Ch 1", "1-118", "9999", "Mara", "3 hours", "n/a"),
                                       scene("Ch 1 §2", "Ch 1", "119-240", "1390", "Mara", "2 hours", "3 hours"),
                                       scene("Ch 2 §1", "Ch 2", "241-372", "1610", "Jon", "1 hour", "16 hours")]),
                     timeline, ledger)
    chk("e4_scene_cell", code == 1 and any("E4" in x and "word_count" in x for x in ls))
    code, ls = check(manifest(findings=[{"id": "F-RR-01", "severity": "Should-Fix", "confidence": "HIGH", "chapter": "Ch 9"}]),
                     timeline, ledger)
    chk("e4_finding_sev", code == 1 and any("E4" in x and "severity" in x for x in ls))

    # E3 — a body Must-Fix dropped from findings[]
    chk("e3_mustfix_dropped", check(manifest(findings=[]), timeline, ledger)[0] == 1)
    # a Could-Fix ledger does NOT force inclusion (E3 is Must-Fix only)
    led_could = "# Ledger\n" + finding(fid="F-A-01", severity="Could-Fix", confidence="LOW") + "\n"
    chk("e3_couldfix_optional", check(manifest(findings=[]), timeline, led_could)[0] == 0)

    # E5 — a duplicated scene_id (double-draws the pacing bar) / a duplicated finding id (double-counts)
    dup_scenes = [scene("Ch 1 §1", "Ch 1", "1-118", "1480", "Mara", "3 hours", "n/a"),
                  scene("Ch 1 §1", "Ch 1", "1-118", "1480", "Mara", "3 hours", "n/a"),
                  scene("Ch 2 §1", "Ch 2", "241-372", "1610", "Jon", "1 hour", "16 hours")]
    code, ls = check(manifest(scenes=dup_scenes), timeline, ledger)
    chk("e5_dup_scene", code == 1 and any("E5 duplicate entry" in x and "scene_id" in x for x in ls))
    code, ls = check(manifest(findings=[{"id": "F-RR-01", "severity": "Must-Fix", "confidence": "HIGH", "chapter": "Ch 9"},
                                        {"id": "F-RR-01", "severity": "Must-Fix", "confidence": "HIGH", "chapter": "Ch 9"}]),
                     timeline, ledger)
    chk("e5_dup_finding", code == 1 and any("E5 duplicate entry" in x and "finding id" in x for x in ls))

    # W1 — a Timeline row omitted from scenes[] (advisory, ERROR --strict)
    one_scene = [scene("Ch 1 §1", "Ch 1", "1-118", "1480", "Mara", "3 hours", "n/a")]
    code, ls = check(manifest(scenes=one_scene), timeline, ledger)
    chk("w1_coverage_advisory", code == 0 and any("W1 coverage" in x for x in ls))
    chk("w1_coverage_strict_fails", check(manifest(scenes=one_scene), timeline, ledger, strict=True)[0] == 1)

    # E1 — a present-but-broken manifest block is a FAIL, not a vacuous no-op
    broken = "# Map\n<!-- apodictic:viz_manifest\n{ \"schema\": \"apodictic.viz_manifest.v1\",, }\n-->"
    code, ls = check(broken, timeline, ledger)
    chk("e1_invalid_json_fails", code == 1 and any("invalid JSON" in x for x in ls))
    # a genuinely-absent block is a no-op (code 0) for a run folder, BUT --require-block makes it a FAIL
    chk("noop_missing_block", check("# Map\n(no manifest here)\n", timeline, ledger)[0] == 0)
    chk("require_block_missing_fails",
        check("# Map\n(no manifest here)\n", timeline, ledger, require_block=True)[0] == 1)

    # W2 — scenes[] in non-Timeline order (still per-id valid) → advisory, ERROR under --strict
    rev_scenes = [scene("Ch 2 §1", "Ch 2", "241-372", "1610", "Jon", "1 hour", "16 hours"),
                  scene("Ch 1 §1", "Ch 1", "1-118", "1480", "Mara", "3 hours", "n/a"),
                  scene("Ch 1 §2", "Ch 1", "119-240", "1390", "Mara", "2 hours", "3 hours")]
    code, ls = check(manifest(scenes=rev_scenes), timeline, ledger)
    chk("w2_scene_order_advisory", code == 0 and any("W2 scene order" in x for x in ls))
    chk("w2_scene_order_strict_fails", check(manifest(scenes=rev_scenes), timeline, ledger, strict=True)[0] == 1)

    # render — pure function, self-contained, draws the three charts
    h = render_html(manifest(), timeline, ledger)
    chk("render_selfcontained", "<svg" in h and "http://" not in h and "https://" not in h)
    chk("render_has_charts", h.count("<svg") >= 3 and "Mara" in h and "Ch 9" in h)
    chk("render_record_note", "artifact of record" in h)
    # Chart 3 — chapters sort numerically (Ch 2 before Ch 10), not lexicographically
    h_ord = render_html(manifest(scenes=[], findings=[
        {"id": "F-A", "severity": "Must-Fix", "confidence": "HIGH", "chapter": "Ch 2"},
        {"id": "F-B", "severity": "Must-Fix", "confidence": "HIGH", "chapter": "Ch 10"}]), timeline, ledger)
    chk("chart3_numeric_order", h_ord.index("Ch 2") < h_ord.index("Ch 10"))

    # resolution
    d = tempfile.mkdtemp()
    made.append(d)
    with open(os.path.join(d, "Proj_Timeline_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(timeline)
    with open(os.path.join(d, "Proj_Findings_Ledger_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(ledger)
    with open(os.path.join(d, "Proj_Structure_Map_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Structure Map\n" + manifest() + "\n")
    chk("run_folder_resolution", run([d])[0] == 0)
    chk("explicit_files_resolution",
        run([os.path.join(d, "Proj_Structure_Map_run.md"),
             os.path.join(d, "Proj_Timeline_run.md"),
             os.path.join(d, "Proj_Findings_Ledger_run.md")])[0] == 0)
    chk("missing_artifact_usage", run([d + "/nope.md"])[0] in (2,))

    # render gate: a reordered manifest draws a false pacing curve, so `render` refuses without --force
    rd = tempfile.mkdtemp()
    made.append(rd)
    tlp = os.path.join(rd, "tl.md"); ldp = os.path.join(rd, "ld.md")
    rev_man = os.path.join(rd, "rev_Structure_Map.md"); ok_man = os.path.join(rd, "ok_Structure_Map.md")
    out = os.path.join(rd, "out.html")
    with open(tlp, "w", encoding="utf-8", newline="") as fh: fh.write(timeline)
    with open(ldp, "w", encoding="utf-8", newline="") as fh: fh.write(ledger)
    with open(rev_man, "w", encoding="utf-8", newline="") as fh: fh.write(manifest(scenes=rev_scenes))
    with open(ok_man, "w", encoding="utf-8", newline="") as fh: fh.write(manifest())
    chk("render_refuses_reordered", main(["x", "render", rev_man, tlp, ldp, "-o", out]) == 1)
    chk("render_force_reordered", main(["x", "render", rev_man, tlp, ldp, "-o", out, "--force"]) == 0)
    chk("render_in_order_ok", main(["x", "render", ok_man, tlp, ldp, "-o", out]) == 0)

    # ============================================================================================
    # Chart 7-nonfiction — the claim ladder (X1/X5/X6/X7/X8 + W3). Exercised on a canonical
    # argument_spine.v1 + support_plan.v1 fixture mirroring example-argument-state-predraft.md: a
    # HOSTILE op-ed with C1 (DATA, to-acquire), C2 (AUTHORITY, in-hand), C3 (DATA, to-acquire). The
    # Cn-token resolver path goes through argument_spine.spine_subclaim_ids() — no second parser.
    # ============================================================================================
    def spine_block(subclaims, supports):
        sp = {"schema": "apodictic.argument_spine.v1", "form": "op-ed", "goal": "g",
              "argument_type": "AT3", "burden_level": "HIGH", "audience_expertise": "MIXED",
              "audience_receptivity": "HOSTILE",
              "thesis": "fund curb-cut ramps citywide within two budget cycles",
              "subclaims": subclaims, "anti_thesis": "spend the dollars on road resurfacing instead"}
        out = ["## 1. Context and Classification\n## 2. Claim Architecture\n## 3. Support Map\n",
               "<!-- apodictic:argument_spine\n%s\n-->" % _j.dumps(sp)]
        for sup in supports:
            out.append("<!-- apodictic:support_plan\n%s\n-->" % _j.dumps(sup))
        return "\n".join(out) + "\n"

    L1 = "missing curb cuts are a documented, daily mobility barrier"
    L2 = "the phased cost fits the existing capital-improvement budget without new taxes"
    L3 = "piecemeal complaint-driven installation has failed for a decade"
    canon_subclaims = ["C1: " + L1, "C2: " + L2, "C3: " + L3]
    canon_supports = [
        {"schema": "apodictic.support_plan.v1", "subclaim_id": "C1", "support_type": "DATA",
         "planned_support": "the accessibility audit's count of non-compliant corners", "status": "to-acquire"},
        {"schema": "apodictic.support_plan.v1", "subclaim_id": "C2", "support_type": "AUTHORITY",
         "planned_support": "the published capital-improvement budget", "status": "in-hand"},
        {"schema": "apodictic.support_plan.v1", "subclaim_id": "C3", "support_type": "DATA",
         "planned_support": "a decade of complaint-log resolution times", "status": "to-acquire"},
    ]
    canon_spine = spine_block(canon_subclaims, canon_supports)

    def cl_manifest(ladder, scenes=None):
        # A claim-ladder manifest with NO scenes/findings by default (the ladder is independent of the
        # Timeline/Ledger sources; an empty scenes/findings is legitimate for a pre-draft run).
        o = {"schema": _SCHEMA_ID, "project": "Curb Cuts",
             "scenes": scenes if scenes is not None else [], "findings": [],
             "claim_ladder": ladder}
        return "<!-- apodictic:viz_manifest\n%s\n-->" % _j.dumps(o)

    canon_ladder = [
        {"claim_id": "C1", "label": L1, "support": [{"support_type": "DATA", "status": "to-acquire"}]},
        {"claim_id": "C2", "label": L2, "support": [{"support_type": "AUTHORITY", "status": "in-hand"}]},
        {"claim_id": "C3", "label": L3, "support": [{"support_type": "DATA", "status": "to-acquire"}]},
    ]

    # clean — the canonical ladder validates against the canonical spine
    code, ls = check(cl_manifest(canon_ladder), None, None, spine_text=canon_spine)
    chk("x5_claim_ladder_clean", code == 0 and any("claim rung" in x for x in ls))

    # X8 — a claim_ladder[] with NO resolvable argument_spine producer FAILS (the firewall's teeth)
    code, ls = check(cl_manifest(canon_ladder), None, None, spine_text=None)
    chk("x8_no_producer_fails", code == 1 and any("X8 producer-present" in x and "argument_spine" in x for x in ls))

    # X1 — a scene_ids / scene_id / section key on a ladder object is itself a failure (no scene axis)
    for badkey in ("scene_ids", "scene_id", "section"):
        bad = [dict(canon_ladder[0], **{badkey: ["Ch 1 §2"]})] + canon_ladder[1:]
        code, ls = check(cl_manifest(bad), None, None, spine_text=canon_spine)
        chk("x1_scene_axis_%s_fails" % badkey,
            code == 1 and any("X1" in x and "disallowed field '%s'" % badkey in x for x in ls))

    # X1 — a visual-style key on a ladder object fails too
    bad = [dict(canon_ladder[0], color="red")] + canon_ladder[1:]
    chk("x1_style_field_fails",
        check(cl_manifest(bad), None, None, spine_text=canon_spine)[0] == 1)

    # X1 — a disallowed key on a support[] item fails; an out-of-enum support_type/status fails
    bad = [{"claim_id": "C1", "label": L1,
            "support": [{"support_type": "DATA", "status": "to-acquire", "weight": 5}]}] + canon_ladder[1:]
    chk("x1_support_extra_key_fails",
        check(cl_manifest(bad), None, None, spine_text=canon_spine)[0] == 1)
    bad = [{"claim_id": "C1", "label": L1,
            "support": [{"support_type": "VIBES", "status": "to-acquire"}]}] + canon_ladder[1:]
    chk("x1_support_bad_enum_fails",
        check(cl_manifest(bad), None, None, spine_text=canon_spine)[0] == 1)

    # X5 — a claim_id the spine did not declare fails
    bad = canon_ladder + [{"claim_id": "C9", "label": "invented", "support": []}]
    code, ls = check(cl_manifest(bad), None, None, spine_text=canon_spine)
    chk("x5_undeclared_claim_fails", code == 1 and any("X5" in x and "C9" in x for x in ls))

    # X6 — a label NOT byte-equal to the stripped subclaim string fails (the "invented data point")
    bad = [dict(canon_ladder[0], label="curb cuts matter, basically")] + canon_ladder[1:]
    code, ls = check(cl_manifest(bad), None, None, spine_text=canon_spine)
    chk("x6_label_mismatch_fails", code == 1 and any("X6" in x and "label" in x for x in ls))

    # X6 — a NON-STRING label is refused, not str()-coerced. X1/X6 require a byte-for-byte STRING copy
    # of the stripped subclaim; the closed allowlist only checks keys, never value types, so a numeric
    # label 123 reached the provenance check. The pre-fix `str(label) != str(want_label)` made
    # str(123) == str("123") pass — a numeric "123" smuggled past a check that demands a string. Build
    # a spine whose C1 subclaim strips to the digit string "123" and a manifest carrying the int 123.
    num_subclaims = ["C1: 123", "C2: " + L2, "C3: " + L3]
    num_spine = spine_block(num_subclaims, canon_supports)
    num_ladder = [{"claim_id": "C1", "label": 123,
                   "support": [{"support_type": "DATA", "status": "to-acquire"}]}] + canon_ladder[1:]
    code, ls = check(cl_manifest(num_ladder), None, None, spine_text=num_spine)
    chk("x6_nonstring_label_refused", code == 1 and any("X6" in x and "label" in x for x in ls))
    # control: the SAME ladder with the label as the string "123" validates clean (proves the failure
    # above is the type guard, not the value — a verbatim string copy still passes)
    str_ladder = [dict(num_ladder[0], label="123")] + canon_ladder[1:]
    chk("x6_string_label_ok",
        check(cl_manifest(str_ladder), None, None, spine_text=num_spine)[0] == 0)

    # X6 — a support pairing absent from support_plan.v1 fails (C2 is AUTHORITY/in-hand, not DATA)
    bad = [canon_ladder[0],
           {"claim_id": "C2", "label": L2, "support": [{"support_type": "DATA", "status": "to-acquire"}]},
           canon_ladder[2]]
    code, ls = check(cl_manifest(bad), None, None, spine_text=canon_spine)
    chk("x6_support_pairing_fabricated_fails", code == 1 and any("X6" in x and "pairing" in x for x in ls))

    # X6 multiplicity — over-drawing a chip (listing a pairing MORE times than support_plan.v1 has it)
    # fails, even though each copy "exists" in the source (the shallow membership-only check would miss it)
    bad = [{"claim_id": "C1", "label": L1,
            "support": [{"support_type": "DATA", "status": "to-acquire"},
                        {"support_type": "DATA", "status": "to-acquire"}]}] + canon_ladder[1:]
    code, ls = check(cl_manifest(bad), None, None, spine_text=canon_spine)
    chk("x6_support_overdraw_fails", code == 1 and any("X6" in x and "remaining" in x for x in ls))

    # multi-support — a subclaim with TWO support_plan blocks renders both chips (P3 #4, no support score)
    multi_supports = canon_supports + [
        {"schema": "apodictic.support_plan.v1", "subclaim_id": "C1", "support_type": "EXAMPLE",
         "planned_support": "a named intersection where a wheelchair user was stranded", "status": "in-hand"}]
    multi_spine = spine_block(canon_subclaims, multi_supports)
    multi_ladder = [{"claim_id": "C1", "label": L1,
                     "support": [{"support_type": "DATA", "status": "to-acquire"},
                                 {"support_type": "EXAMPLE", "status": "in-hand"}]}] + canon_ladder[1:]
    chk("x6_multi_support_ok",
        check(cl_manifest(multi_ladder), None, None, spine_text=multi_spine)[0] == 0)
    h_multi = render_html(cl_manifest(multi_ladder), None, None, spine_text=multi_spine)
    chk("render_multi_support_two_chips", h_multi.count("EXAMPLE") >= 1 and h_multi.count("DATA") >= 1)
    # X6 completeness (Codex #139 P1): omitting a producer support block — here keeping only C1's in-hand
    # EXAMPLE and dropping its DATA/to-acquire chip — must FAIL. A sub-multiset is not enough: under-
    # rendering "to-acquire" support over-states the claim. Pre-fix this passed silently.
    omit_ladder = [{"claim_id": "C1", "label": L1,
                    "support": [{"support_type": "EXAMPLE", "status": "in-hand"}]}] + canon_ladder[1:]
    code, ls = check(cl_manifest(omit_ladder), None, None, spine_text=multi_spine)
    chk("x6_support_omission_fails",
        code == 1 and any("X6" in x and "omits" in x and "to-acquire" in x for x in ls))

    # X5 — an EMPTY support[] is permitted ONLY for a bare assertion (a subclaim with no support_plan).
    bare_spine = spine_block(canon_subclaims, canon_supports[:2])   # drop C3's support plan
    bare_ladder = [canon_ladder[0], canon_ladder[1],
                   {"claim_id": "C3", "label": L3, "support": []}]
    chk("x5_bare_assertion_ok",
        check(cl_manifest(bare_ladder), None, None, spine_text=bare_spine)[0] == 0)
    # but an empty support[] on a subclaim that DOES have a support_plan block fails
    bad = [canon_ladder[0], canon_ladder[1], {"claim_id": "C3", "label": L3, "support": []}]
    code, ls = check(cl_manifest(bad), None, None, spine_text=canon_spine)
    chk("x5_empty_support_with_plan_fails", code == 1 and any("X5" in x and "bare assertion" in x for x in ls))

    # X7 — a claim_id appears at most once (a repeat double-draws a rung)
    bad = canon_ladder + [canon_ladder[0]]
    code, ls = check(cl_manifest(bad), None, None, spine_text=canon_spine)
    chk("x7_dup_claim_fails", code == 1 and any("X7 duplicate entry" in x and "claim_id" in x for x in ls))

    # hostile shape — an unhashable claim_id (a list) must FAIL cleanly (X5), never traceback
    bad = [{"claim_id": ["C1"], "label": L1, "support": []}]
    code, ls = check(cl_manifest(bad), None, None, spine_text=canon_spine)
    chk("x5_unhashable_claim_id_no_crash", code == 1 and any("X5" in x for x in ls))
    # hostile shape — a non-dict ladder element must FAIL cleanly (X1), never traceback
    code, ls = check(cl_manifest(["not-an-object"]), None, None, spine_text=canon_spine)
    chk("x1_non_object_rung_no_crash", code == 1 and any("X1" in x and "must be an object" in x for x in ls))

    # X8 — a present reveal_points array fails (no producer yet). co_presence + scene_functions now HAVE
    # producers (apodictic.scene_roster.v1 / apodictic.scene_function.v1), so they are exercised in the
    # chart-5 / chart-6 blocks below, not here.
    for arr_key in ("reveal_points",):
        o = {"schema": _SCHEMA_ID, "project": "P", "scenes": [], "findings": [],
             arr_key: [{"scene_id": "Ch 1 §1", "characters": ["Mara"]}]}
        m = "<!-- apodictic:viz_manifest\n%s\n-->" % _j.dumps(o)
        code, ls = check(m, timeline, ledger, spine_text=None)
        chk("x8_producer_gated_%s_fails" % arr_key,
            code == 1 and any("X8 producer-present" in x and arr_key in x for x in ls))

    # W3 — spine present (with subclaims) but claim_ladder absent → advisory (ERROR under --strict)
    no_ladder = "<!-- apodictic:viz_manifest\n%s\n-->" % _j.dumps(
        {"schema": _SCHEMA_ID, "project": "P", "scenes": [], "findings": []})
    code, ls = check(no_ladder, None, None, spine_text=canon_spine)
    chk("w3_coverage_advisory", code == 0 and any("W3 chart coverage" in x for x in ls))
    chk("w3_coverage_strict_fails",
        check(no_ladder, None, None, spine_text=canon_spine, strict=True)[0] == 1)

    # render — the claim ladder draws when the manifest carries it AND a spine resolves; no scene axis
    h = render_html(cl_manifest(canon_ladder), None, None, spine_text=canon_spine)
    chk("render_claim_ladder",
        "Claim ladder" in h and "C0 (thesis)" in h and L1 in h and "AUTHORITY" in h)
    chk("render_claim_ladder_selfcontained",
        "<svg" in h and "http://" not in h and "https://" not in h)
    # the bare-assertion pill renders for a subclaim with empty support[]
    h_bare = render_html(cl_manifest(bare_ladder), None, None, spine_text=bare_spine)
    chk("render_bare_assertion_pill", "bare assertion" in h_bare)
    # without a spine source the ladder section is simply omitted (no crash, no fabricated C0)
    h_nospine = render_html(cl_manifest(canon_ladder), None, None, spine_text=None)
    chk("render_no_spine_omits_ladder", "Claim ladder" not in h_nospine)

    # claim-ladder resolution from a run folder (Argument_State*.md globbed as the spine source)
    cd = tempfile.mkdtemp()
    made.append(cd)
    with open(os.path.join(cd, "Proj_Structure_Map_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Map\n" + cl_manifest(canon_ladder) + "\n")
    with open(os.path.join(cd, "Argument_State.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(canon_spine)
    chk("claim_ladder_run_folder_resolution", run([cd])[0] == 0)

    # ============================================================================================
    # Chart 5 — the character co-presence network (X1/X2/X7/X8). The PRODUCER is apodictic.scene_roster.v1
    # (per-scene cast; the Timeline carries POV only). The Timeline above is solo-POV (Mara/Mara/Jon →
    # zero edges), so the worked roster ADDS co-characters: Mara + Adrian share Ch 1 §1 + Ch 1 §2 (one
    # edge, weight 2); Eleanor is mentioned-not-present (no roster entry → no edge); Jon is solo in Ch 2
    # §1 (isolated node); and the "Mara Voss" surface form collapses to "Mara" via the alias table.
    # ============================================================================================
    def roster_block(rosters, aliases=None):
        o = {"schema": _ROSTER_SCHEMA_ID, "project": "Test"}
        if aliases is not None:
            o["character_aliases"] = aliases
        o["rosters"] = rosters
        return "<!-- apodictic:scene_roster\n%s\n-->" % _j.dumps(o)

    def char(name, anchor="\"she acted on-page\""):
        # Default to a QUOTE-form anchor (no leading line range) so the X2(e) line-range bounding is
        # skipped for it — the generic helper isn't coupled to each scene's Timeline line_range. Tests
        # that exercise the bounding pass an explicit "lines N-M …" anchor.
        return {"name": name, "anchor": anchor}

    # The canonical worked roster (mirrors example-scene-roster.md). All three scene_ids resolve to the
    # `timeline` fixture above; each scene's POV (Mara/Mara/Jon) is present in its roster.
    canon_rosters = [
        {"scene_id": "Ch 1 §1", "characters": [char("Mara"), char("Adrian")]},
        {"scene_id": "Ch 1 §2", "characters": [char("Mara Voss"), char("Adrian")]},
        {"scene_id": "Ch 2 §1", "characters": [char("Jon")]},
    ]
    canon_aliases = [{"surface": "Mara Voss", "canonical": "Mara"}]
    canon_roster = roster_block(canon_rosters, canon_aliases)

    def cp_manifest(co_presence):
        # Scenes mirror the Timeline so the POV cross-check has rows to read (and E2/E4 stay clean); the
        # findings include the ledger's F-RR-01 Must-Fix so E3 completeness is satisfied (these tests
        # isolate co_presence, not finding placement).
        scns = [scene("Ch 1 §1", "Ch 1", "1-118", "1480", "Mara", "3 hours", "n/a"),
                scene("Ch 1 §2", "Ch 1", "119-240", "1390", "Mara", "2 hours", "3 hours"),
                scene("Ch 2 §1", "Ch 2", "241-372", "1610", "Jon", "1 hour", "16 hours")]
        o = {"schema": _SCHEMA_ID, "project": "Test", "scenes": scns,
             "findings": [{"id": "F-RR-01", "severity": "Must-Fix", "confidence": "HIGH", "chapter": "Ch 9"}],
             "co_presence": co_presence}
        return "<!-- apodictic:viz_manifest\n%s\n-->" % _j.dumps(o)

    canon_cp = [
        {"scene_id": "Ch 1 §1", "characters": ["Mara", "Adrian"]},
        {"scene_id": "Ch 1 §2", "characters": ["Mara", "Adrian"]},
        {"scene_id": "Ch 2 §1", "characters": ["Jon"]},
    ]

    # clean — the canonical co-presence validates against the canonical roster + Timeline
    code, ls = check(cp_manifest(canon_cp), timeline, ledger, roster_text=canon_roster)
    chk("x2_co_presence_clean", code == 0 and any("co-presence scene" in x for x in ls))

    # X8 — a co_presence[] with NO resolvable scene_roster producer FAILS (the firewall's teeth)
    code, ls = check(cp_manifest(canon_cp), timeline, ledger, roster_text=None)
    chk("x2_no_producer_fails",
        code == 1 and any("X8 producer-present" in x and "scene_roster" in x for x in ls))

    # X2(a) — a dangling co_presence scene_id (no roster entry AND no Timeline row) fails
    bad_cp = canon_cp + [{"scene_id": "Ch 9 §9", "characters": ["Mara"]}]
    code, ls = check(cp_manifest(bad_cp), timeline, ledger, roster_text=canon_roster)
    chk("x2_dangling_scene_id_fails",
        code == 1 and any("X2 co-presence provenance" in x and "Ch 9 §9" in x for x in ls))

    # X2(b) — a co_presence name absent from that scene's roster fails (mentioned/invented, not present).
    # Eleanor is the firewall fixture: she is mentioned-not-present, so she has NO roster entry → naming
    # her in co_presence is a provenance breach (and, via the render below, draws no edge).
    bad_cp = [{"scene_id": "Ch 1 §1", "characters": ["Mara", "Adrian", "Eleanor"]}] + canon_cp[1:]
    code, ls = check(cp_manifest(bad_cp), timeline, ledger, roster_text=canon_roster)
    chk("x2_name_not_in_roster_fails",
        code == 1 and any("X2 co-presence provenance" in x and "Eleanor" in x for x in ls))

    # X2(c) — the Timeline POV character must be present in its roster (cross-check). Drop Jon (the POV)
    # from Ch 2 §1's roster → the producer rosters someone else instead → POV-missing error.
    pov_missing_rosters = [canon_rosters[0], canon_rosters[1],
                           {"scene_id": "Ch 2 §1", "characters": [char("Adrian")]}]
    # the manifest co_presence for Ch 2 §1 names Adrian (in-roster) so X2(b) passes; only X2(c) fires
    pov_missing_cp = canon_cp[:2] + [{"scene_id": "Ch 2 §1", "characters": ["Adrian"]}]
    code, ls = check(cp_manifest(pov_missing_cp), timeline, ledger,
                     roster_text=roster_block(pov_missing_rosters, canon_aliases))
    chk("x2_pov_missing_from_roster_fails",
        code == 1 and any("X2 co-presence provenance" in x and "POV" in x and "Jon" in x for x in ls))

    # X2(d) — a producer roster character with an EMPTY anchor fails (presence must be auditable).
    empty_anchor_rosters = [{"scene_id": "Ch 1 §1", "characters": [char("Mara"), char("Adrian", anchor="")]},
                            canon_rosters[1], canon_rosters[2]]
    code, ls = check(cp_manifest(canon_cp), timeline, ledger,
                     roster_text=roster_block(empty_anchor_rosters, canon_aliases))
    chk("x2_empty_anchor_fails",
        code == 1 and any("X2 co-presence provenance" in x and "anchor must be a non-empty" in x for x in ls))

    # X2(e) — a LINE-RANGE-shaped anchor that falls OUTSIDE its scene's Timeline line-range fails
    # (a partial tightening of anchor-truthfulness — an anchor cannot witness presence in a scene it
    # points outside of). Ch 1 §1's Timeline line_range is 1-118; an anchor "lines 900-950" is outside.
    outside_rosters = [{"scene_id": "Ch 1 §1",
                        "characters": [char("Mara", anchor="lines 1-50: \"here\""),
                                       char("Adrian", anchor="lines 900-950: \"elsewhere\"")]},
                       canon_rosters[1], canon_rosters[2]]
    code, ls = check(cp_manifest(canon_cp), timeline, ledger,
                     roster_text=roster_block(outside_rosters, canon_aliases))
    chk("x2_anchor_outside_scene_line_range_fails",
        code == 1 and any("anchor lines 900-950 fall outside" in x and "Ch 1 §1" in x for x in ls))
    # X2(e) positive — an in-range line-range anchor (overlapping the Timeline 1-118) passes; and a
    # QUOTE-form anchor (no leading line range) is SKIPPED, not falsely rejected. Ch 1 §1 gets an
    # in-range line anchor for Mara + a quote anchor for Adrian; the other scenes keep quote anchors.
    inrange_rosters = [{"scene_id": "Ch 1 §1",
                        "characters": [char("Mara", anchor="lines 10-40: \"within scene\""),
                                       char("Adrian", anchor="\"a quote-only anchor, unbounded\"")]},
                       canon_rosters[1], canon_rosters[2]]
    chk("x2_anchor_in_range_and_quote_form_pass",
        check(cp_manifest(canon_cp), timeline, ledger,
              roster_text=roster_block(inrange_rosters, canon_aliases))[0] == 0)
    # X2(e) unit — the helpers: line-range parse (both "lines N-M" and bare "N-M"), quote -> None,
    # reversed span normalized, overlap math (touching endpoints overlap; disjoint do not).
    chk("line_range_parse",
        _parse_line_range("lines 1-118: \"x\"") == (1, 118) and _parse_line_range("119-240") == (119, 240)
        and _parse_line_range("\"a quote\"") is None and _parse_line_range("lines 40-10") == (10, 40))
    chk("ranges_overlap",
        _ranges_overlap((1, 118), (100, 200)) and _ranges_overlap((118, 118), (118, 250))
        and not _ranges_overlap((1, 50), (51, 99)))

    # X8/X2 — a co_presence that DIVERGES from the producer roster (a name the roster doesn't carry)
    # is the provenance-breach case (X2(b) above is exactly this — proven by the Eleanor test).

    # X1 — a visual-style / scene-axis-extra key on a co_presence object fails (no smuggled style)
    bad_cp = [dict(canon_cp[0], color="red")] + canon_cp[1:]
    code, ls = check(cp_manifest(bad_cp), timeline, ledger, roster_text=canon_roster)
    chk("x1_co_presence_style_field_fails",
        code == 1 and any("X1 new-array schema" in x and "disallowed field 'color'" in x for x in ls))

    # X1 — a non-string character item fails (the manifest carries BARE NAME STRINGS only)
    bad_cp = [{"scene_id": "Ch 1 §1", "characters": [{"name": "Mara", "anchor": "x"}, "Adrian"]}] + canon_cp[1:]
    code, ls = check(cp_manifest(bad_cp), timeline, ledger, roster_text=canon_roster)
    chk("x1_co_presence_nonstring_name_fails",
        code == 1 and any("X1 new-array schema" in x and "bare name string" in x for x in ls))

    # X7 — a duplicate scene_id in co_presence fails (double-draws its edges)
    bad_cp = canon_cp + [canon_cp[0]]
    code, ls = check(cp_manifest(bad_cp), timeline, ledger, roster_text=canon_roster)
    chk("x7_co_presence_dup_scene_fails",
        code == 1 and any("X7 duplicate entry" in x and "scene_id" in x for x in ls))

    # producer hostile shapes — an empty/missing anchor, a disallowed roster key, a non-string name, a
    # duplicate producer scene_id, a malformed alias row must FAIL cleanly via the producer's obj_errs.
    dup_prod = [canon_rosters[0], canon_rosters[0], canon_rosters[2]]   # Ch 1 §1 twice in the producer
    code, ls = check(cp_manifest(canon_cp), timeline, ledger,
                     roster_text=roster_block(dup_prod, canon_aliases))
    chk("x2_producer_dup_scene_fails",
        code == 1 and any("appears more than once in the producer" in x for x in ls))
    bad_alias = [{"surface": "Mara Voss", "canonical": "Mara", "weight": 1}]
    code, ls = check(cp_manifest(canon_cp), timeline, ledger,
                     roster_text=roster_block(canon_rosters, bad_alias))
    chk("x2_producer_bad_alias_key_fails",
        code == 1 and any("character_aliases" in x and "disallowed field 'weight'" in x for x in ls))
    # a hostile non-dict roster element / non-dict character must not traceback
    code, ls = check(cp_manifest(canon_cp), timeline, ledger,
                     roster_text=roster_block(["not-an-object"], canon_aliases))
    chk("x2_producer_non_object_roster_no_crash",
        code == 1 and any("X2 co-presence provenance" in x and "must be an object" in x for x in ls))
    # a producer block whose const is wrong (not a scene_roster) → present:False → X8 fires
    bad_const = "<!-- apodictic:scene_roster\n%s\n-->" % _j.dumps(
        {"schema": "apodictic.viz_manifest.v1", "rosters": canon_rosters})
    code, ls = check(cp_manifest(canon_cp), timeline, ledger, roster_text=bad_const)
    chk("x2_producer_wrong_const_fails", code == 1)

    # the mechanical edge derivation (co_presence_graph) — the firewall's "invents nothing" core.
    nodes, edges = co_presence_graph(canon_cp)
    # Mara/Adrian/Jon are nodes; Eleanor (never in co_presence) is NOT
    chk("graph_nodes", nodes == ["Adrian", "Jon", "Mara"])
    # one edge Adrian-Mara with weight 2 (they share Ch 1 §1 + Ch 1 §2); Jon has NO edge (solo)
    chk("graph_edge_and_weight", edges == {("Adrian", "Mara"): 2})
    chk("graph_solo_no_edge", not any("Jon" in pair for pair in edges))

    # render — the co-presence network draws when the manifest carries co_presence[] AND a roster
    # resolves. The firewall fixtures: Eleanor (mentioned-not-present) draws NO node/edge; Jon renders
    # as an isolated node; the two Mara surface forms are one node.
    h_cp = render_html(cp_manifest(canon_cp), timeline, ledger, roster_text=canon_roster)
    chk("render_co_presence", "Character co-presence network" in h_cp and "Adrian" in h_cp and "Jon" in h_cp)
    chk("render_co_presence_selfcontained",
        "<svg" in h_cp and "http://" not in h_cp and "https://" not in h_cp)
    # firewall fixture: a mentioned-not-present character (Eleanor) appears NOWHERE in the render
    chk("render_mentioned_not_present_no_edge", "Eleanor" not in h_cp)
    # alias collapse: "Mara Voss" the surface form is collapsed → the node label is the canonical "Mara",
    # and the surface form does not appear as its own node
    chk("render_alias_collapse", "Mara" in h_cp and "Mara Voss" not in h_cp)
    # isolated node: Jon renders even though he shares no scene (a node, never dropped)
    chk("render_solo_node_present", "Jon" in h_cp)
    # without a roster source the co-presence section is simply omitted (no crash, no fabricated graph)
    h_noroster = render_html(cp_manifest(canon_cp), timeline, ledger, roster_text=None)
    chk("render_no_roster_omits_co_presence", "Character co-presence network" not in h_noroster)

    # co-presence resolution from a run folder (a *Scene_Roster*.md globbed as the producer source)
    pd = tempfile.mkdtemp()
    made.append(pd)
    with open(os.path.join(pd, "Proj_Structure_Map_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Map\n" + cp_manifest(canon_cp) + "\n")
    with open(os.path.join(pd, "Proj_Timeline_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(timeline)
    with open(os.path.join(pd, "Proj_Findings_Ledger_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(ledger)
    with open(os.path.join(pd, "Proj_Scene_Roster_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Roster\n" + canon_roster + "\n")
    chk("co_presence_run_folder_resolution", run([pd])[0] == 0)

    # W3 — a roster producer is present (with rostered scenes) but co_presence absent → advisory.
    # Use a Could-Fix-only ledger (no Must-Fix) so E3 doesn't fire on the empty findings[].
    led_cp_could = "# Ledger\n" + finding(fid="F-A-01", severity="Could-Fix", confidence="LOW") + "\n"
    no_cp = "<!-- apodictic:viz_manifest\n%s\n-->" % _j.dumps(
        {"schema": _SCHEMA_ID, "project": "P", "scenes": [], "findings": []})
    code, ls = check(no_cp, timeline, led_cp_could, roster_text=canon_roster)
    chk("w3_co_presence_coverage_advisory", code == 0 and any("W3 chart coverage" in x and "co-presence" in x for x in ls))
    chk("w3_co_presence_coverage_strict_fails",
        check(no_cp, timeline, led_cp_could, roster_text=canon_roster, strict=True)[0] == 1)

    # ============================================================================================
    # Chart 6 — the scene-function heatmap (X1/X3/X7/X8). The PRODUCER is apodictic.scene_function.v1
    # (per-scene structural function; the scene-turn audit's Step-1 Unit Classification). All three
    # scene_ids resolve to the `timeline` fixture; each function is in the closed enum scene | sequel |
    # hybrid | non-unit; each carries a required non-empty anchor. Negatives: a scene_id not in Timeline,
    # an empty anchor, a duplicate scene_id, a function outside the enum, and a manifest/producer mismatch.
    # ============================================================================================
    def sfunc_block(functions, project="Test"):
        o = {"schema": _SFUNC_SCHEMA_ID, "project": project, "functions": functions}
        return "<!-- apodictic:scene_function\n%s\n-->" % _j.dumps(o)

    def sfn(sid, function, anchor="\"the scene turns on-page\""):
        # Default to a QUOTE-form anchor (no leading line range) so the X3(e) line-range bounding is
        # skipped; tests that exercise the bounding pass an explicit "lines N-M …" anchor.
        return {"scene_id": sid, "function": function, "anchor": anchor}

    # The canonical worked producer (mirrors example-scene-function.md): Ch 1 §1 = scene, Ch 1 §2 =
    # sequel, Ch 2 §1 = hybrid. All resolve to `timeline`.
    canon_functions = [sfn("Ch 1 §1", "scene"), sfn("Ch 1 §2", "sequel"), sfn("Ch 2 §1", "hybrid")]
    canon_sfunc = sfunc_block(canon_functions)

    def sf_manifest(scene_functions):
        scns = [scene("Ch 1 §1", "Ch 1", "1-118", "1480", "Mara", "3 hours", "n/a"),
                scene("Ch 1 §2", "Ch 1", "119-240", "1390", "Mara", "2 hours", "3 hours"),
                scene("Ch 2 §1", "Ch 2", "241-372", "1610", "Jon", "1 hour", "16 hours")]
        o = {"schema": _SCHEMA_ID, "project": "Test", "scenes": scns,
             "findings": [{"id": "F-RR-01", "severity": "Must-Fix", "confidence": "HIGH", "chapter": "Ch 9"}],
             "scene_functions": scene_functions}
        return "<!-- apodictic:viz_manifest\n%s\n-->" % _j.dumps(o)

    canon_sf = [{"scene_id": "Ch 1 §1", "function": "scene"},
                {"scene_id": "Ch 1 §2", "function": "sequel"},
                {"scene_id": "Ch 2 §1", "function": "hybrid"}]

    # clean — the canonical scene_functions validate against the canonical producer + Timeline
    code, ls = check(sf_manifest(canon_sf), timeline, ledger, scene_function_text=canon_sfunc)
    chk("x3_scene_function_clean", code == 0 and any("scene-function scene" in x for x in ls))

    # X8 — a scene_functions[] with NO resolvable scene_function producer FAILS (the firewall's teeth)
    code, ls = check(sf_manifest(canon_sf), timeline, ledger, scene_function_text=None)
    chk("x3_no_producer_fails",
        code == 1 and any("X8 producer-present" in x and "scene_function" in x for x in ls))

    # X3(a) — a dangling scene_functions scene_id (no producer entry AND no Timeline row) fails
    bad_sf = canon_sf + [{"scene_id": "Ch 9 §9", "function": "scene"}]
    code, ls = check(sf_manifest(bad_sf), timeline, ledger, scene_function_text=canon_sfunc)
    chk("x3_dangling_scene_id_fails",
        code == 1 and any("X3 scene-function provenance" in x and "Ch 9 §9" in x for x in ls))

    # X3(c) — a manifest function that DIVERGES from the producer classification fails (verbatim copy)
    bad_sf = [{"scene_id": "Ch 1 §1", "function": "non-unit"}] + canon_sf[1:]
    code, ls = check(sf_manifest(bad_sf), timeline, ledger, scene_function_text=canon_sfunc)
    chk("x3_function_mismatch_fails",
        code == 1 and any("X3 scene-function provenance" in x and "!=" in x for x in ls))

    # X3(b) — a producer function OUTSIDE the closed scene-turn enum fails
    bad_prod = sfunc_block([sfn("Ch 1 §1", "climax"), canon_functions[1], canon_functions[2]])
    code, ls = check(sf_manifest(canon_sf), timeline, ledger, scene_function_text=bad_prod)
    chk("x3_function_not_in_enum_fails",
        code == 1 and any("Unit-Classification set" in x and "climax" in x for x in ls))

    # X3(d) — a producer entry with an EMPTY anchor fails (the classification must be auditable)
    empty_anchor_prod = sfunc_block([sfn("Ch 1 §1", "scene", anchor=""), canon_functions[1], canon_functions[2]])
    code, ls = check(sf_manifest(canon_sf), timeline, ledger, scene_function_text=empty_anchor_prod)
    chk("x3_empty_anchor_fails",
        code == 1 and any("X3 scene-function provenance" in x and "anchor must be a non-empty" in x for x in ls))

    # X3(e) — a LINE-RANGE anchor outside the scene's Timeline line-range fails; an in-range one passes.
    # Ch 1 §1's Timeline line_range is 1-118; an anchor "lines 900-950" is outside.
    outside_prod = sfunc_block([sfn("Ch 1 §1", "scene", anchor="lines 900-950: \"elsewhere\""),
                                canon_functions[1], canon_functions[2]])
    code, ls = check(sf_manifest(canon_sf), timeline, ledger, scene_function_text=outside_prod)
    chk("x3_anchor_outside_scene_line_range_fails",
        code == 1 and any("anchor lines 900-950 fall outside" in x for x in ls))
    inrange_prod = sfunc_block([sfn("Ch 1 §1", "scene", anchor="lines 10-40: \"within\""),
                                canon_functions[1], canon_functions[2]])
    chk("x3_anchor_in_range_passes",
        check(sf_manifest(canon_sf), timeline, ledger, scene_function_text=inrange_prod)[0] == 0)

    # X1 — a visual-style / extra key on a scene_functions object fails (no smuggled style)
    bad_sf = [dict(canon_sf[0], color="red")] + canon_sf[1:]
    code, ls = check(sf_manifest(bad_sf), timeline, ledger, scene_function_text=canon_sfunc)
    chk("x1_scene_function_style_field_fails",
        code == 1 and any("X1 new-array schema" in x and "disallowed field 'color'" in x for x in ls))

    # X7 — a duplicate scene_id in the manifest scene_functions fails (double-draws its heatmap row)
    bad_sf = canon_sf + [canon_sf[0]]
    code, ls = check(sf_manifest(bad_sf), timeline, ledger, scene_function_text=canon_sfunc)
    chk("x7_scene_function_dup_scene_fails",
        code == 1 and any("X7 duplicate entry" in x and "scene_id" in x for x in ls))

    # producer hostile shapes — a duplicate producer scene_id, a disallowed function-entry key, a
    # non-dict entry, a wrong const must FAIL cleanly via the producer's obj_errs.
    dup_prod = sfunc_block([canon_functions[0], canon_functions[0], canon_functions[2]])
    code, ls = check(sf_manifest(canon_sf), timeline, ledger, scene_function_text=dup_prod)
    chk("x3_producer_dup_scene_fails",
        code == 1 and any("appears more than once in the producer" in x for x in ls))
    bad_key_prod = sfunc_block([{"scene_id": "Ch 1 §1", "function": "scene", "anchor": "x", "weight": 1},
                                canon_functions[1], canon_functions[2]])
    code, ls = check(sf_manifest(canon_sf), timeline, ledger, scene_function_text=bad_key_prod)
    chk("x3_producer_bad_entry_key_fails",
        code == 1 and any("disallowed field 'weight'" in x for x in ls))
    non_obj_prod = sfunc_block(["not-an-object"])
    code, ls = check(sf_manifest(canon_sf), timeline, ledger, scene_function_text=non_obj_prod)
    chk("x3_producer_non_object_entry_no_crash",
        code == 1 and any("X3 scene-function provenance" in x and "must be an object" in x for x in ls))
    bad_const = "<!-- apodictic:scene_function\n%s\n-->" % _j.dumps(
        {"schema": "apodictic.viz_manifest.v1", "functions": canon_functions})
    code, ls = check(sf_manifest(canon_sf), timeline, ledger, scene_function_text=bad_const)
    chk("x3_producer_wrong_const_fails", code == 1)

    # the mechanical grid derivation (scene_function_grid) — the firewall's "invents nothing" core.
    grid = scene_function_grid(canon_sf)
    chk("grid_rows", grid == [("Ch 1 §1", "scene"), ("Ch 1 §2", "sequel"), ("Ch 2 §1", "hybrid")])

    # render — the scene-function heatmap draws when the manifest carries scene_functions[] AND a
    # producer resolves. Deterministic grid; self-contained; drops nothing.
    h_sf = render_html(sf_manifest(canon_sf), timeline, ledger, scene_function_text=canon_sfunc)
    chk("render_scene_function",
        "Scene-function heatmap" in h_sf and "Ch 1 §1" in h_sf and "Sequel" in h_sf)
    chk("render_scene_function_selfcontained",
        "<svg" in h_sf and "http://" not in h_sf and "https://" not in h_sf)
    # without a producer source the heatmap section is simply omitted (no crash, no fabricated grid)
    h_no_sf = render_html(sf_manifest(canon_sf), timeline, ledger, scene_function_text=None)
    chk("render_no_producer_omits_scene_function", "Scene-function heatmap" not in h_no_sf)

    # scene-function resolution from a run folder (a *Scene_Function*.md globbed as the producer source)
    sfd = tempfile.mkdtemp()
    made.append(sfd)
    with open(os.path.join(sfd, "Proj_Structure_Map_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Map\n" + sf_manifest(canon_sf) + "\n")
    with open(os.path.join(sfd, "Proj_Timeline_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(timeline)
    with open(os.path.join(sfd, "Proj_Findings_Ledger_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(ledger)
    with open(os.path.join(sfd, "Proj_Scene_Function_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Functions\n" + canon_sfunc + "\n")
    chk("scene_function_run_folder_resolution", run([sfd])[0] == 0)

    # W3 — a producer is present (with classified scenes) but scene_functions absent → advisory.
    led_sf_could = "# Ledger\n" + finding(fid="F-A-01", severity="Could-Fix", confidence="LOW") + "\n"
    no_sf = "<!-- apodictic:viz_manifest\n%s\n-->" % _j.dumps(
        {"schema": _SCHEMA_ID, "project": "P", "scenes": [], "findings": []})
    code, ls = check(no_sf, timeline, led_sf_could, scene_function_text=canon_sfunc)
    chk("w3_scene_function_coverage_advisory",
        code == 0 and any("W3 chart coverage" in x and "scene-function" in x for x in ls))
    chk("w3_scene_function_coverage_strict_fails",
        check(no_sf, timeline, led_sf_could, scene_function_text=canon_sfunc, strict=True)[0] == 1)

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    if len(argv) > 1 and argv[1] == "render":
        rest = argv[2:]
        out = None
        force = "--force" in rest
        rest = [a for a in rest if a != "--force"]
        if "-o" in rest:
            i = rest.index("-o")
            out = rest[i + 1] if i + 1 < len(rest) else None
            rest = rest[:i] + rest[i + 2:]
        if len(rest) < 1:
            # The Timeline + Ledger are required for a normal (gated) render: provenance can't be
            # checked without the sources, so a manifest with scenes/findings would refuse. `--force`
            # is the manifest-only escape hatch (an un-provenanced preview). Trailing positional files
            # (or a run folder) supply the Argument_State spine (claim ladder) + the Scene_Roster
            # producer (co-presence) — content-sniffed by block type, so their order doesn't matter.
            print("Usage: viz_manifest.py render <manifest> <timeline> <ledger> [<argument_state>] [<scene_roster>] [<scene_function>] [-o out.html]\n"
                  "       viz_manifest.py render <run_folder> [-o out.html]\n"
                  "       viz_manifest.py render <manifest> --force        # manifest-only, skips the provenance gate")
            return 2
        rosterp = sfuncp = None
        if len(rest) == 1 and os.path.isdir(rest[0]):
            man, tlp, led, spinep, rosterp, sfuncp = resolve(rest)
        else:
            man = rest[0]
            tlp = rest[1] if len(rest) > 1 else None
            led = rest[2] if len(rest) > 2 else None
            # The spine + roster + scene-function producers are interchangeable in position beyond index
            # 2 — sniff every trailing positional by block type so `<manifest> <timeline> <ledger>
            # <roster>` works even without a spine, and the producer order is free.
            spinep = rosterp = sfuncp = None
            for p in rest[3:]:
                body = _read(p) or ""
                if _has_block(body, "scene_roster") and rosterp is None:
                    rosterp = p
                elif _has_block(body, "scene_function") and sfuncp is None:
                    sfuncp = p
                elif _has_block(body, "argument_spine") and spinep is None:
                    spinep = p
        mtext = _read(man)
        tltext = _read(tlp) if tlp else None
        ledtext = _read(led) if led else None
        spinetext = _read(spinep) if spinep else None
        rostertext = _read(rosterp) if rosterp else None
        sfunctext = _read(sfuncp) if sfuncp else None
        # Gate before rendering: rendering un-provenanced data is exactly the firewall hole the
        # validator exists to prevent. Refuse on an ERROR-level gate failure, OR on a scene-order
        # divergence — W2 is advisory in general, but a reordered manifest draws a FALSE pacing curve
        # (the one warning that corrupts the render's core output), so it blocks the render too.
        # W1 coverage stays advisory: a legitimate partial map still renders.
        gcode, glines = check(mtext, tltext, ledtext, spine_text=spinetext, roster_text=rostertext,
                              scene_function_text=sfunctext, require_block=True)
        scene_order_broken = any("W2 scene order" in ln for ln in glines)
        if (gcode != 0 or scene_order_broken) and not force:
            for ln in glines:
                print(ln, file=sys.stderr)
            missing = [n for n, t in (("timeline", tltext), ("ledger", ledtext)) if t is None]
            if missing:
                print("manuscript-viz: no %s supplied — provenance (E2/E4) cannot be checked without the "
                      "source(s); pass them, or --force for an un-provenanced manifest-only preview."
                      % " or ".join(missing), file=sys.stderr)
            print("manuscript-viz: refusing to render — the manifest fails the provenance gate or reorders "
                  "scenes vs the Timeline (a false pacing curve). Pass --force to override. See above.",
                  file=sys.stderr)
            return 1
        h = render_html(mtext, tltext, ledtext, spine_text=spinetext, roster_text=rostertext,
                        scene_function_text=sfunctext)
        if out:
            with open(out, "w", encoding="utf-8", newline="") as fh:
                fh.write(h)
            print("manuscript-viz: rendered %s" % out)
        else:
            sys.stdout.write(h)
        return 0
    args = [a for a in argv[1:] if a != "manuscript-viz"]
    strict = "--strict" in args
    require_block = "--require-block" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: viz_manifest.py manuscript-viz <run_folder|files...> [--strict] [--require-block] "
              "| render ... | --self-test")
        return 2
    code, lines = run(paths, strict=strict, require_block=require_block)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
