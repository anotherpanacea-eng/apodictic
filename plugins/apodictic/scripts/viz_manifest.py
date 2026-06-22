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

Manuscript-Visualization Completion (charts 4-7) extends this same manifest<->source contract. The
M1 render-only deliverable is chart 7-nonfiction — the CLAIM LADDER over apodictic.argument_spine.v1
(C0 thesis + C1..Cn subclaims) annotated with support coverage from apodictic.support_plan.v1. The
manifest gains four OPTIONAL, additive arrays (co_presence / scene_functions / reveal_points /
claim_ladder); only claim_ladder is rendered in M1 (the other three are producer-gated — their
producers do not exist yet, so their arrays stay absent and the gates skip them):

  X1 new-array schema    each present co_presence/scene_functions/reveal_points/claim_ladder element
                         is a well-formed object with ONLY its allowlisted keys (a visual-style key
                         is itself a failure; a scene_ids/scene_id/section key on a claim_ladder[]
                         object is itself a failure — the claim-to-scene map has no producer and
                         cannot be smuggled in). claim_ladder[].support[] items admit only
                         {support_type, status} (the support_plan.v1 enums).
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
  X8 producer-present    if a new array is PRESENT, its producer MUST be present and resolvable (for
                         claim_ladder: a resolvable argument_spine.v1 block, plus the support_plan.v1
                         blocks for any non-empty support[]). Absent array -> skipped, not failed.
  W3 chart coverage      a producer artifact is present but its corresponding array is empty/absent
                         (silent under-rendering). Advisory, ERROR under --strict.

(X2/X3/X4 — roster/function/tension provenance — are reserved for the producer-gated charts 4/5/6;
their producers do not exist yet, so those gates are not implemented in M1.)

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
_MANIFEST_GLOB = "*_Structure_Map_*.md"
_TIMELINE_GLOBS = ("*_Timeline_*.md", "Timeline.md")
_LEDGER_GLOB = "*_Findings_Ledger_*.md"
_SPINE_GLOB = "Argument_State*.md"   # chart 7-nonfiction source (the seeded pre-draft Argument_State)

# The manifest is style-free: these are the ONLY keys each object may carry (E1 allowlist).
_SCENE_KEYS = ("scene_id", "chapter", "line_range", "word_count", "pov", "span", "gap")
_FINDING_KEYS = ("id", "severity", "confidence", "chapter")
# Charts 4-7 (Manuscript-Visualization Completion) — four OPTIONAL additive arrays. M1 renders only
# claim_ladder; the other three are producer-gated (their producers do not exist yet). The closed
# allowlists are the X1 firewall: claim_ladder[] admits NO scene_ids/scene_id/section key (the
# claim-to-scene map has no producer and cannot be smuggled in); support[] items admit only the two
# support_plan.v1 fields the manifest copies verbatim.
_CO_PRESENCE_KEYS = ("scene_id", "characters")
_SCENE_FUNCTION_KEYS = ("scene_id", "function", "value_shift")
_REVEAL_POINT_KEYS = ("scene_id", "tension", "reveal_id")
_CLAIM_LADDER_KEYS = ("claim_id", "label", "support")
_SUPPORT_ITEM_KEYS = ("support_type", "status")
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


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
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


def check(manifest_text, timeline_text, ledger_text, spine_text=None,
          strict=False, require_block=False):
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

    # ---- Manuscript-Visualization Completion (charts 4-7): X1/X5/X6/X7/X8 + W3 ----
    # The four arrays are OPTIONAL and additive. M1 implements chart 7-nonfiction (claim_ladder);
    # the other three are producer-gated — their producers (scene_roster / scene_function /
    # tension_point) do not exist yet, so a PRESENT array for them fails X8 (you cannot ship a chart
    # array without the producer to byte-check it against). Absent arrays are skipped (a partial map
    # is legitimate — the same posture as W1 coverage).
    ladder = spine_ladder(spine_text)
    claim_ladder = obj.get("claim_ladder")
    if claim_ladder is not None:
        errs += _check_claim_ladder(claim_ladder, ladder)
    # X8 — the three producer-gated arrays have NO producer in M1, so a present array is a hard fail.
    for arr_key, prod in (("co_presence", "apodictic.scene_roster.v1"),
                          ("scene_functions", "apodictic.scene_function.v1"),
                          ("reveal_points", "apodictic.tension_point.v1")):
        arr = obj.get(arr_key)
        if arr:   # present and non-empty
            errs.append("X8 producer-present: %s[] is present but its producer (%s) does not exist "
                        "yet — this chart is producer-gated and cannot be rendered render-first "
                        "(doing so would fabricate data)" % (arr_key, prod))
    # W3 — chart coverage: the argument_spine.v1 producer is present (with declared subclaims) but
    # claim_ladder[] is empty/absent — the data exists but the chart was silently dropped. Advisory.
    if ladder.get("present") and ladder.get("ids") and not claim_ladder:
        warns.append("W3 chart coverage: an apodictic.argument_spine.v1 with %d declared subclaim(s) "
                     "is present but claim_ladder[] is empty/absent — the claim ladder is renderable "
                     "but was dropped (silent under-rendering)" % len(ladder.get("ids")))

    # Report
    lines.append("manuscript-viz: %s — %d scene(s), %d finding(s)%s%s"
                 % (obj.get("project", "?"), len(scenes), len(findings),
                    ", %d claim rung(s)" % len(claim_ladder) if claim_ladder else "",
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
        lines.append("manuscript-viz: PASS (manifest<->source provenance: schema + closure + Must-Fix + verbatim copy + uniqueness + claim-ladder)")
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


def render_html(manifest_text, timeline_text, ledger_text, spine_text=None):
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
<div class=meta>Render-only companion · APODICTIC manuscript-structure visualization (charts 1–3{cl_label})</div>
<div class=record><strong>The editorial letter is the artifact of record.</strong> This is a render of data the
passes already produced — it adds no analysis and no verdict lives only here. Severity encoding is fixed:
a Must-Fix is always rendered at full salience (size never shrinks for low confidence).</div>
{partial_note}
<h2>Pacing — word count by scene</h2>{c1}
<h2>POV time-share</h2>{c2}
<h2>Findings by chapter</h2><div class=legend>{legend}</div>{c3}
{claim_section}
</body></html>""".format(project=project, partial_note=partial_note,
                         c1=_bars_svg(pacing), c2=_bars_svg(pov), c3=_bars_svg(sev_bars), legend=legend,
                         claim_section=claim_section,
                         cl_label=" + claim ladder" if claim_section else "")


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    """Return (manifest_path, timeline_path, ledger_path, spine_path) from a run folder or files.

    spine_path is the pre-draft Argument_State (the chart 7-nonfiction claim-ladder source); it may
    be None (a fiction run carries no spine — the claim ladder simply isn't rendered)."""
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
        return man, tlp, led, spinep
    man = tlp = led = spinep = None
    for p in paths:
        body = _read(p) or ""
        if _has_block(body, "viz_manifest") and man is None:
            man = p
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
    return man, tlp, led, spinep


def run(paths, strict=False, require_block=False):
    man, tlp, led, spinep = resolve(paths)
    if not man:
        return 2, ["manuscript-viz: no Structure Map manifest found (need a *_Structure_Map_*.md "
                   "or a file with an apodictic:viz_manifest block)"]
    mtext = _read(man)
    if mtext is None:
        return 2, ["manuscript-viz: cannot read %s" % man]
    return check(mtext, _read(tlp) if tlp else None, _read(led) if led else None,
                 spine_text=_read(spinep) if spinep else None,
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

    # X8 — a present co_presence / scene_functions / reveal_points array fails (no producer in M1)
    for arr_key in ("co_presence", "scene_functions", "reveal_points"):
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
            # is the manifest-only escape hatch (an un-provenanced preview). A 4th positional file (or
            # a run folder) supplies the Argument_State spine for the claim ladder (optional).
            print("Usage: viz_manifest.py render <manifest> <timeline> <ledger> [<argument_state>] [-o out.html]\n"
                  "       viz_manifest.py render <run_folder> [-o out.html]\n"
                  "       viz_manifest.py render <manifest> --force        # manifest-only, skips the provenance gate")
            return 2
        if len(rest) == 1 and os.path.isdir(rest[0]):
            man, tlp, led, spinep = resolve(rest)
        else:
            man = rest[0]
            tlp = rest[1] if len(rest) > 1 else None
            led = rest[2] if len(rest) > 2 else None
            spinep = rest[3] if len(rest) > 3 else None
        mtext = _read(man)
        tltext = _read(tlp) if tlp else None
        ledtext = _read(led) if led else None
        spinetext = _read(spinep) if spinep else None
        # Gate before rendering: rendering un-provenanced data is exactly the firewall hole the
        # validator exists to prevent. Refuse on an ERROR-level gate failure, OR on a scene-order
        # divergence — W2 is advisory in general, but a reordered manifest draws a FALSE pacing curve
        # (the one warning that corrupts the render's core output), so it blocks the render too.
        # W1 coverage stays advisory: a legitimate partial map still renders.
        gcode, glines = check(mtext, tltext, ledtext, spine_text=spinetext, require_block=True)
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
        h = render_html(mtext, tltext, ledtext, spine_text=spinetext)
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
