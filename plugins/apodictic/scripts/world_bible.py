#!/usr/bin/env python3
"""world-bible — structural integrity + contradiction detection for a standalone Worldbuilding Bible.

`validate.sh world-bible <run_folder|files>` shells out here. A worldbuilding bible is the SFF
author's OWN pre-draft reference document — the rules of the magic/tech, the cost of using it, the
geography, the order of events, the factions. Before a single chapter exists, that bible can already
contradict itself. This tool checks a BIBLE (not a manuscript) for that class of self-contradiction —
closed-set rule consistency, magic-system cost accounting, geography/timeline contradiction — and
SURFACES the contradictions the bible has already committed to. It never invents world content, fills
an unstated gap, or resolves a conflict (the Firewall: extract the stated, never author the unstated).
Each fact is an apodictic.world_fact.v1 block; this validator owns the bible's contract and the three
contradiction arms.

  W1 schema           a world_fact block fails its schema (bad category/polarity enum, malformed
                      WF-NN id, missing required field, unquoted-numeric value, empty loci, broken
                      JSON) OR carries an unknown (closed-key) field — a misspelled key the subset
                      schema engine would otherwise admit silently (so the closed-set guarantee is
                      not hollow).
  WD duplicate id     two facts share a WF-NN id (the W-class id-uniqueness check).
  WB-R1 rule          two `rule` facts on the same subject + same normalized value assert opposite
                      polarity (can vs cannot, or requires vs cannot) — a literal closed-set
                      contradiction. ERROR. Override <!-- override: world-rule WF-NN/WF-MM — … -->.
  WB-C1 cost          two `cost`/cost-bearing-`rule` facts on the same subject assign two different
                      non-null, non-"none" cost values — the bible prices the same power two ways.
                      ERROR. Override <!-- override: world-cost WF-NN/WF-MM — … -->.
  WB-C2 free-vs-costed  the same subject is stated free (cost null/"none") in one fact and carries a
                      real cost in another — the pre-draft form of Cost Amnesia. Advisory WARN;
                      ERROR under --strict. Override <!-- override: world-cost WF-NN/WF-MM — … -->.
  WB-G1 distance      the same unordered {subject, pair_subject} edge is assigned two different parsed
                      distances WITHIN ONE commensurable unit class (spatial: mile/league/km;
                      temporal-travel: day/hour). The two axes never collide-check against each other
                      (a 6-day ride and 120 miles can both be true). ERROR. Override
                      <!-- override: world-geo WF-NN/WF-MM — … -->.
  WB-G2 chronology    the directed `event` edges (subject happens-before pair_subject) contain a CYCLE
                      (X<Y, Y<Z, Z<X), OR the same event is stated at two different absolute day
                      anchors (Day N). An unresolvable timeline contradiction. ERROR. Override
                      <!-- override: world-geo WF-NN/WF-MM — … --> (cycle: name any two ids on it).
  WF (firewall)       a reader-facing prose scan: a resolution/invention verb ("the true rule is",
                      "the canonical cost is", "should be N miles") leaking into the bible's prose —
                      the tool SURFACES, it never resolves. Advisory WARN; ERROR under --strict.
                      Override <!-- override: world-firewall — <rationale> -->.

`value` is ALWAYS a string (numerics quoted) so W1 can type-check + the arms can parse it. The three
arms are deterministic, stdlib-only, and CONSERVATIVE: they fire only on confidently parseable,
literally-colliding facts; ambiguous / unparseable / cross-axis / non-literal (implied) contradictions
are left to the author and never become a hard failure. Reuses apodictic_artifacts (block grammar +
schema engine). Each artifact is optional; an empty/absent one is a no-op. See docs/worldbuilding-bible.md.

  world_bible.py world-bible <run_folder|files...> [--strict]
  world_bible.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import os
import re
import sys

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

_SCHEMA_ID = "apodictic.world_fact.v1"
_BIBLE_GLOB = "*_Worldbuilding_Bible_*.md"

# The closed key set — every key world_bible.py recognizes on a world_fact block. Because the subset
# schema engine in apodictic_artifacts SILENTLY ADMITS unknown keys (a misspelled field passes), the
# closed-set guarantee would be hollow without this bespoke pass. Mirrors the persona-spec pattern
# continuity-bible cites for its own closed enums.
_KNOWN_KEYS = {"schema", "id", "category", "subject", "attribute", "value",
               "polarity", "cost", "pair_subject", "loci"}

# Per-category KEYED requirements — the flat schema marks the arm-specific fields (polarity, cost,
# pair_subject) optional for every category, so a fact whose category NEEDS one of them could omit it,
# pass W1 + --strict, and be SILENTLY SKIPPED by the very arm that gives the category meaning (a `rule`
# with no `polarity` is skipped by WB-R1; a `distance` with no `pair_subject` by WB-G1; a `cost` with
# no `cost` by WB-C1/C2). That makes an arm "look clean" over a malformed bible. These checks close the
# hole so the keyed field is enforced at W1, mirroring the closed-key + cost-type bespoke passes. Each
# arm was read to derive its category->field pair (review finding P1, round 9):
#   rule     -> polarity     (WB-R1 pairs can/cannot/requires; a rule must state its closed-set claim,
#                             which MAY be the explicit opt-out "n/a" — but it must be stated, not absent)
#   cost     -> cost         (WB-C1/C2 read the `cost` field; a cost fact with no cost field is inert)
#   distance -> pair_subject (WB-G1 keys on the unordered {subject, pair_subject} edge)
#   event    -> pair_subject OR a Day/Week anchor (WB-G2 has two arms: the happens-before CYCLE check
#                             needs pair_subject; the anchor-drift check needs a parseable Day/Week in
#                             value/attribute. An event with NEITHER feeds no arm and is skipped, so it
#                             must carry at least one.)
# place / faction / entity have NO contradiction arm (descriptive-only), so they impose no keyed field.

# Override markers naming an unordered pair of ids: "<!-- override: world-rule WF-01/WF-02 — … -->".
# The pair is order-insensitive; both "WF-01/WF-02" and "WF-02/WF-01" silence the same conflict.
_OVERRIDE_RE = re.compile(
    r"<!--\s*override:\s*(world-[a-z]+)\s+(WF-[0-9]+)\s*/\s*(WF-[0-9]+)\b", re.IGNORECASE)
# The firewall override is pair-free (it silences the prose scan, not a fact pair).
_FW_OVERRIDE_RE = re.compile(r"<!--\s*override:\s*world-firewall\b", re.IGNORECASE)

# WF firewall — resolution / invention verbs that would mean the bible's prose RESOLVED a conflict or
# INVENTED canon instead of surfacing it. Kept specific so the advisory rarely misfires; an intended
# phrasing is silenced by the world-firewall override. The tool surfaces; it never adjudicates.
_FIREWALL_RE = re.compile(
    r"\bthe\s+(?:true|correct|real|canonical|actual)\s+(?:rule|cost|price|distance|order|value|answer)\s+is\b"
    r"|\bthe\s+(?:rule|cost|price|distance|order)\s+should\s+(?:be|read)\b"
    r"|\bshould\s+(?:be|read)\s+\d"
    r"|\b(?:resolve[ds]?|reconciled?)\s+(?:to|as)\b"
    r"|\bthe\s+canon(?:ical)?\s+(?:value|version|reading)\s+is\b"
    r"|\bwe\s+(?:pick|choose|adopt|keep)\s+(?:the|WF-)",
    re.IGNORECASE)
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

# WB-G1 distance normalization — TWO disjoint, commensurable unit classes. A stated travel-TIME and a
# stated spatial DISTANCE are SEPARATE axes that never collide-check against each other (a 6-day ride
# and 120 miles can both be true for one edge), per the spec's own "distinct units that cannot be
# normalized to a common base are not compared" conservatism (review finding P3 #4).
#   spatial  -> normalized to MILES (mile, league=3 mi, km≈0.621371 mi, furlong=0.125 mi)
#   temporal -> normalized to HOURS (day=24, hour, week=168) — travel-time, NOT a chronology anchor
_SPATIAL_UNITS = {
    "mile": 1.0, "mi": 1.0,
    "league": 3.0,
    "km": 0.621371, "kilometer": 0.621371, "kilometre": 0.621371,
    "furlong": 0.125,
}
_TEMPORAL_UNITS = {
    "hour": 1.0, "hr": 1.0,
    "day": 24.0,
    "week": 168.0,
}
_NUM_UNIT_RE = re.compile(r"(-?\d+(?:\.\d+)?)\s*([A-Za-z]+)")


def _norm_distance(s):
    """('axis', magnitude) for a stated edge length, or None if not parseable on a known axis.
    axis='spatial' (-> miles) or 'temporal' (-> hours). The two axes are commensurable ONLY within
    themselves; WB-G1 never compares across axes. Reuses the timeline_checks._norm_duration parse
    idiom (number + unit, unit lower-cased + de-pluralized)."""
    if s is None:
        return None
    m = _NUM_UNIT_RE.search(s)
    if not m:
        return None
    value = float(m.group(1))
    unit = m.group(2).lower().rstrip("s")
    if unit in _SPATIAL_UNITS:
        return ("spatial", value * _SPATIAL_UNITS[unit])
    if unit in _TEMPORAL_UNITS:
        return ("temporal", value * _TEMPORAL_UNITS[unit])
    return None


def _norm_anchor_day(*texts):
    """Best-effort absolute day number from any of the given anchor texts. Recognizes 'Day N' and
    'Week M' (-> day (M-1)*7+1). Returns int or None. Mirrors timeline_checks._norm_anchor_day so the
    chronology arm uses the same anchor idiom as the Pass-10 Timeline validator."""
    for t in texts:
        if not t:
            continue
        m = re.search(r"\bDay\s+(\d+)", t, re.IGNORECASE)
        if m:
            return int(m.group(1))
    for t in texts:
        if not t:
            continue
        m = re.search(r"\bWeek\s+(\d+)", t, re.IGNORECASE)
        if m:
            return (int(m.group(1)) - 1) * 7 + 1
    return None


def _required_field_errs(obj, where):
    """Per-category KEYED-requirement check (see _KNOWN_KEYS comment). Returns W1 error strings for a
    fact whose category needs an arm-specific field but omits it — so a malformed fact can never make a
    contradiction arm 'look clean' by being silently skipped. `obj` is a validated dict (called after
    the schema pass, so `category` is a known enum). A present-but-empty string counts as omitted for
    the edge endpoints (an empty subject/pair_subject feeds no arm; the arms already `continue` on it),
    matching the arms' own truthiness guards."""
    if not isinstance(obj, dict):
        return []
    cat = obj.get("category")
    errs = []
    if cat == "rule":
        # WB-R1 pairs on polarity; an absent polarity is silently skipped. "n/a" is the explicit
        # opt-out (a rule that makes no closed-set claim) — allowed, but it must be STATED.
        if "polarity" not in obj:
            errs.append("%s: category=rule requires `polarity` (can | cannot | requires | n/a) — "
                        "WB-R1 silently skips a rule with no polarity" % where)
    elif cat == "cost":
        # WB-C1/C2 read the `cost` field; a cost fact with no `cost` key feeds no cost arm.
        if "cost" not in obj:
            errs.append("%s: category=cost requires the `cost` field (a string price, \"none\", or "
                        "null) — WB-C1/C2 skip a cost fact with no cost" % where)
    elif cat == "distance":
        # WB-G1 keys on the {subject, pair_subject} edge; without pair_subject there is no edge.
        if not (obj.get("pair_subject") or "").strip():
            errs.append("%s: category=distance requires a non-empty `pair_subject` (the other edge "
                        "endpoint) — WB-G1 skips a distance with no pair_subject" % where)
    elif cat == "event":
        # WB-G2 is two arms: cycle (needs pair_subject) OR anchor-drift (needs a parseable Day/Week
        # anchor in value/attribute). An event with NEITHER feeds no arm and is silently skipped.
        has_edge = bool((obj.get("pair_subject") or "").strip())
        has_anchor = _norm_anchor_day(obj.get("value"), obj.get("attribute")) is not None
        if not has_edge and not has_anchor:
            errs.append("%s: category=event requires either a non-empty `pair_subject` (a "
                        "happens-before edge) or a parseable Day/Week anchor in value/attribute (a "
                        "chronology anchor) — WB-G2 skips an event with neither" % where)
    return errs


def _norm_value(s):
    """Normalize a rule value for closed-set collision: case-folded, leading-article-stripped,
    whitespace-collapsed. So 'raise the dead' and 'Raise  the Dead' collide; 'fly' and 'flying' do
    NOT (literal, not semantic — the conservative-firing discipline)."""
    s = (s or "").strip().lower()
    s = re.sub(r"^(?:the|a|an)\s+", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _overrides(text, slug):
    """Set of frozenset({id, id}) unordered pairs overridden for the given slug (world-rule /
    world-cost / world-geo)."""
    out = set()
    for m in _OVERRIDE_RE.finditer(text or ""):
        if m.group(1).lower() == slug:
            out.add(frozenset((m.group(2), m.group(3))))
    return out


def parse_facts(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:world_fact block. Schema errors
    include the bespoke closed-key check (an unknown key fails W1), since the subset engine admits
    unknown keys silently."""
    facts = []
    if not text or art is None:
        return facts
    schema = art.load_schema(_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "world_fact":
            continue
        idx += 1
        where = "world_fact #%d" % idx
        if jerr:
            facts.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        errs = art.validate_obj(obj, schema, where)
        # Closed-key pass — the subset engine admits unknown keys, so a misspelled field
        # ("polairty", "subjct") would pass schema validation. Catch it here or the closed-set
        # guarantee is hollow (spec §Closed-key checking is bespoke).
        if isinstance(obj, dict):
            for k in sorted(obj):
                if k not in _KNOWN_KEYS:
                    errs.append("%s: unknown field %r (closed key set: %s)"
                                % (where, k, ", ".join(sorted(_KNOWN_KEYS))))
            # Bespoke `cost` value-type guard — same philosophy as the closed-key pass. The schema
            # leaves `cost` un-typed (the subset engine cannot express string|null, per its own
            # $comment), so a numeric/list/bool `cost` would pass W1 + closed-key and crash the
            # cost arm's _norm_value(c) -> (c or "").strip(). Catch it here so the malformed bible
            # gets a clean W1 ERROR, matching the spec's "string fields are type-checked so the
            # arms can safely parse them" guarantee (the one un-schema'd field that needed it).
            if "cost" in obj and obj["cost"] is not None and not isinstance(obj["cost"], str):
                errs.append("%s: `cost` must be a string or null, got %s"
                            % (where, type(obj["cost"]).__name__))
            # Per-category KEYED requirement — a fact whose category needs an arm-specific field but
            # omits it must FAIL W1, not pass --strict and get silently skipped by its arm (P1, round 9).
            errs.extend(_required_field_errs(obj, where))
        facts.append((obj, errs, idx))
    return facts


# ------------------------------------------------------- the contradiction arms

def _rule_contradictions(valid, overrides):
    """WB-R1: same subject + same normalized value, opposite polarity (can vs cannot, or requires vs
    cannot). Returns a list of error strings."""
    errs = []
    # group rule facts by (subject, normalized value) -> {polarity: [ids]}
    groups = {}
    for obj in valid:
        if obj.get("category") != "rule":
            continue
        pol = (obj.get("polarity") or "").strip().lower()
        if pol not in ("can", "cannot", "requires"):
            continue  # n/a or unset: not a closed-set assertion to pair
        key = (_norm_value(obj.get("subject")), _norm_value(obj.get("value")))
        groups.setdefault(key, {}).setdefault(pol, []).append(obj.get("id"))
    for (subj, val), bypol in sorted(groups.items()):
        # contradiction: a `cannot` paired with a `can` OR a `requires` on the same value
        if "cannot" not in bypol:
            continue
        opposed = bypol.get("can", []) + bypol.get("requires", [])
        for neg_id in sorted(bypol["cannot"]):
            for pos_id in sorted(opposed):
                if frozenset((neg_id, pos_id)) in overrides:
                    continue
                errs.append("WB-R1 rule: %s and %s assert opposite polarity for the same rule "
                            "(subject=%r, value=%r) — cannot both hold; surface or override"
                            % (neg_id, pos_id, subj, val))
    return errs


def _cost_contradictions(valid, overrides, strict):
    """WB-C1 (ERROR: two different real costs for one subject) + WB-C2 (advisory: free-then-costed).
    Returns (errors, warns)."""
    errs, warns = [], []
    # group cost-bearing facts (category cost, or rule carrying a cost) by subject
    by_subject = {}
    for obj in valid:
        if obj.get("category") not in ("cost", "rule"):
            continue
        if "cost" not in obj:
            continue  # no cost field => nothing for the cost arm to read
        by_subject.setdefault(_norm_value(obj.get("subject")), []).append(obj)
    for subj, objs in sorted(by_subject.items()):
        real, free = [], []  # (id, normalized-cost)
        for o in objs:
            c = o.get("cost")
            if c is None or _norm_value(c) in ("none", "no cost", "free", "nothing"):
                free.append(o.get("id"))
            else:
                real.append((o.get("id"), _norm_value(c)))
        # WB-C1 — two DIFFERENT real cost values for the same subject. Group ids by normalized cost
        # value, then pair ACROSS distinct value-groups (same-value pairs agree and are skipped). One
        # error per colliding pair so each pair is overridable independently.
        by_cost = {}
        for cid, cval in real:
            by_cost.setdefault(cval, []).append(cid)
        groups = sorted(by_cost.items())
        for gi in range(len(groups)):
            for gj in range(gi + 1, len(groups)):
                for a in sorted(groups[gi][1]):
                    for b in sorted(groups[gj][1]):
                        if frozenset((a, b)) in overrides:
                            continue
                        lo, hi = sorted((a, b))
                        errs.append("WB-C1 cost: %s and %s assign different stated costs to subject=%r "
                                    "(the bible prices the same power two ways) — reconcile, stage the "
                                    "escalation, or override" % (lo, hi, subj))
        # WB-C2 — same subject free in one fact, costed in another (advisory)
        if free and real:
            for fid in sorted(free):
                for cid, _cval in real:
                    if frozenset((fid, cid)) in overrides:
                        continue
                    warns.append("WB-C2 free-vs-costed: subject=%r is stated free in %s but costed "
                                 "in %s — a power the bible sometimes prices and sometimes gives away"
                                 % (subj, fid, cid))
    return errs, warns


# WB-G1 distances within 1% of each other are treated as AGREEING — a unit conversion (km->miles,
# leagues->miles) rarely lands on exact equality, and no author means a sub-1% difference as a
# contradiction. The conservative-firing discipline: float noise must never become a false ERROR.
_DIST_REL_TOL = 0.01


def _dist_close(x, y):
    if x == y:
        return True
    return abs(x - y) <= _DIST_REL_TOL * max(abs(x), abs(y))


def _distance_contradictions(valid, overrides):
    """WB-G1: same unordered {subject, pair_subject} edge, two different parsed distances WITHIN one
    commensurable unit class (spatial OR temporal — never across axes). Distances within 1% are
    treated as agreeing (unit-conversion noise is not a contradiction). Returns error strings."""
    errs = []
    # edge -> axis -> [(id, magnitude), ...]
    edges = {}
    for obj in valid:
        if obj.get("category") != "distance":
            continue
        a = _norm_value(obj.get("subject"))
        b = _norm_value(obj.get("pair_subject"))
        if not a or not b:
            continue  # an edge needs both endpoints
        parsed = _norm_distance(obj.get("value"))
        if parsed is None:
            continue  # unparseable / unknown unit -> exempt (left to author)
        axis, mag = parsed
        edge = frozenset((a, b))
        edges.setdefault(edge, {}).setdefault(axis, []).append((obj.get("id"), mag))
    for edge, by_axis in sorted(edges.items(), key=lambda kv: sorted(kv[0])):
        for axis, items in sorted(by_axis.items()):
            items = sorted(items)  # by id
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    (a_id, a_mag), (b_id, b_mag) = items[i], items[j]
                    if _dist_close(a_mag, b_mag):
                        continue  # agree (within tolerance) — not a collision
                    if frozenset((a_id, b_id)) in overrides:
                        continue
                    pair = "/".join(sorted(edge))
                    errs.append("WB-G1 distance: %s and %s assign different %s distances to the same "
                                "edge {%s} — one edge, two lengths; reconcile or override"
                                % (a_id, b_id, axis, pair))
    return errs


def _mag_of(fid, by_mag):
    """For WB-G2 anchor-drift: the day-anchor a fact id was bucketed under (by_day maps day -> [ids])."""
    for mag, ids in by_mag.items():
        if fid in ids:
            return mag
    return None


def _chronology_contradictions(valid, overrides):
    """WB-G2: (a) a CYCLE in the directed happens-before graph (subject -> pair_subject), or (b) the
    same event stated at two different absolute Day anchors. Returns error strings."""
    errs = []
    # (b) anchor drift: event subject -> set of distinct day anchors
    by_event = {}
    for obj in valid:
        if obj.get("category") != "event":
            continue
        day = _norm_anchor_day(obj.get("value"), obj.get("attribute"))
        if day is None:
            continue
        subj = _norm_value(obj.get("subject"))
        by_event.setdefault(subj, {}).setdefault(day, []).append(obj.get("id"))
    for subj, by_day in sorted(by_event.items()):
        if len(by_day) < 2:
            continue
        ids = sorted(i for dids in by_day.values() for i in dids)
        # a single override on any pair on this event silences the anchor drift for that pair
        reported = False
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                if frozenset((ids[i], ids[j])) in overrides:
                    continue
                if _mag_of(ids[i], by_day) == _mag_of(ids[j], by_day):
                    continue
                if not reported:
                    days = "/".join("Day %s" % d for d in sorted(by_day))
                    errs.append("WB-G2 chronology: event subject=%r is anchored to two different days "
                                "(%s) — %s; surface or override" % (subj, days, ", ".join(ids)))
                    reported = True

    # (a) cycle in the happens-before edges. Build subject -> {pair_subject} and DFS for a back-edge.
    graph = {}
    edge_ids = {}  # (u, v) -> id, for naming a pair on the cycle in the override hint
    for obj in valid:
        if obj.get("category") != "event":
            continue
        u = _norm_value(obj.get("subject"))
        v = _norm_value(obj.get("pair_subject"))
        if not u or not v:
            continue  # an ordering edge needs both endpoints
        graph.setdefault(u, set()).add(v)
        graph.setdefault(v, set())
        edge_ids[(u, v)] = obj.get("id")
    cycle = _find_cycle(graph)
    if cycle:
        # name the participating fact ids (the edges that make up the cycle). Honor an override if ANY
        # override pair names two ids that both lie on the cycle — the author marks the loop as
        # intentional by citing any two of its edges (order-insensitive), not a specific adjacency.
        cyc_ids = []
        for k in range(len(cycle) - 1):
            fid = edge_ids.get((cycle[k], cycle[k + 1]))
            if fid and fid not in cyc_ids:
                cyc_ids.append(fid)
        cyc_set = set(cyc_ids)
        ov = any(pair <= cyc_set for pair in overrides)
        if not ov:
            errs.append("WB-G2 chronology: the happens-before edges form a cycle (%s) — an "
                        "unresolvable ordering; %s; break the cycle or override"
                        % (" -> ".join(cycle), ", ".join(cyc_ids) or "no addressable ids"))
    return errs


def _find_cycle(graph):
    """Return one cycle as a node list [a, b, ..., a] via stdlib DFS, or None. Deterministic (sorted
    node + neighbor order) so the reported cycle is stable across runs."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}
    parent = {}

    def visit(u):
        color[u] = GRAY
        for w in sorted(graph.get(u, ())):
            if color.get(w, WHITE) == WHITE:
                parent[w] = u
                got = visit(w)
                if got:
                    return got
            elif color.get(w) == GRAY:
                # back-edge u->w: reconstruct w ... u, then close with w
                path = [u]
                x = u
                while x != w and x in parent:
                    x = parent[x]
                    path.append(x)
                path.reverse()
                path.append(w)
                return path
        color[u] = BLACK
        return None

    for n in sorted(graph):
        if color[n] == WHITE:
            got = visit(n)
            if got:
                return got
    return None


def _firewall_scan(text, strict):
    """WF: the bible's reader-facing prose must SURFACE, never resolve/invent. Scan the visible prose
    (HTML comments — incl. the world_fact blocks, which ARE comments — stripped first) for a
    resolution/invention verb. Advisory; ERROR under --strict; world-firewall override silences."""
    if _FW_OVERRIDE_RE.search(text or ""):
        return []
    visible = _HTML_COMMENT_RE.sub("", text or "")
    hits = []
    for ln in visible.split("\n"):
        if _FIREWALL_RE.search(ln):
            hits.append(ln.strip())
    if not hits:
        return []
    return ["WF firewall: the bible prose reads as RESOLVING a conflict or INVENTING canon "
            "(%r) — the tool surfaces both values and leaves the choice to the author; describe "
            "the conflict, do not pick a winner (or override world-firewall)" % hits[0][:80]]


# ------------------------------------------------------- the runner

def bible(text, strict=False):
    """Run the Worldbuilding Bible integrity + contradiction checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    facts = parse_facts(text)
    if not facts:
        return 0, ["world-bible: no world_fact blocks found — nothing to check"]

    # W1 — schema / JSON validity / closed-key (per block)
    for _obj, schema_errs, _idx in facts:
        for e in schema_errs:
            errs.append("W1 schema: %s" % e)

    valid_pairs = [(obj, idx) for obj, schema_errs, idx in facts
                   if obj is not None and not schema_errs]
    valid = [obj for obj, _idx in valid_pairs]

    # WD — duplicate id (W-class id-uniqueness)
    seen = {}
    for obj in valid:
        seen.setdefault(obj.get("id"), 0)
        seen[obj.get("id")] += 1
    for wid, n in sorted(seen.items()):
        if n > 1:
            errs.append("WD duplicate id: %s appears %d times (ids must be unique)" % (wid, n))

    rule_ov = _overrides(text, "world-rule")
    cost_ov = _overrides(text, "world-cost")
    geo_ov = _overrides(text, "world-geo")

    # The three contradiction arms (conservative, literal-collision only)
    errs.extend(_rule_contradictions(valid, rule_ov))
    c_errs, c_warns = _cost_contradictions(valid, cost_ov, strict)
    errs.extend(c_errs)
    warns.extend(c_warns)
    errs.extend(_distance_contradictions(valid, geo_ov))
    errs.extend(_chronology_contradictions(valid, geo_ov))

    # WF — firewall prose scan (advisory; ERROR under --strict)
    warns.extend(_firewall_scan(text, strict))

    # Report
    lines.append("world-bible: %d fact(s)%s" % (
        len(facts), "" if len(valid) == len(facts) else " (%d well-formed)" % len(valid)))
    for obj in valid:
        lines.append("  %-7s %-9s %s" % (obj.get("id"), obj.get("category"), obj.get("subject")))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("world-bible: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: world-bible: %d advisory signal(s) — see WB-C2/WF above" % len(warns))
    else:
        lines.append("world-bible: PASS (schema + closed-key + rule/cost/geo contradiction arms + "
                     "surface-don't-resolve firewall)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    if len(paths) == 1 and os.path.isdir(paths[0]):
        return _newest(glob.glob(os.path.join(paths[0], _BIBLE_GLOB)))
    for p in paths:
        if "apodictic:world_fact" in (_read(p) or ""):
            return p
    return paths[0] if paths else None


def run(paths, strict=False):
    path = resolve(paths)
    if not path:
        return 2, ["world-bible: no Worldbuilding Bible artifact found (need a "
                   "*_Worldbuilding_Bible_*.md or a file with apodictic:world_fact blocks)"]
    text = _read(path)
    if text is None:
        return 2, ["world-bible: cannot read %s" % path]
    return bible(text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def fact(wid, category="rule", subject="blood-magic", attribute="limit",
             value="cannot raise the dead", loci=("Bible §Magic ¶3",), **extra):
        obj = {"schema": _SCHEMA_ID, "id": wid, "category": category, "subject": subject,
               "attribute": attribute, "value": value, "loci": list(loci)}
        for k, v in extra.items():
            obj[k] = v
        return "<!-- apodictic:world_fact\n%s\n-->" % _j.dumps(obj)

    # clean single rule fact (no pairing) — PASS
    chk("clean_single", bible(fact("WF-01", polarity="cannot"))[0] == 0)

    # W1 — bad enum / id / missing field / unquoted numeric / empty loci / JSON / closed-key
    chk("w1_bad_category", bible(fact("WF-01", category="thing"))[0] == 1)
    chk("w1_bad_polarity", bible(fact("WF-01", polarity="maybe"))[0] == 1)
    chk("w1_bad_id", bible(fact("WF-1"))[0] == 1)
    chk("w1_missing_field", bible(fact("WF-01").replace('"attribute"', '"attr"'))[0] == 1)
    code, lines = bible('<!-- apodictic:world_fact\n{"schema":"apodictic.world_fact.v1","id":"WF-01",'
                        '"category":"distance","subject":"Karth","attribute":"distance-to",'
                        '"value":120,"pair_subject":"the capital","loci":["Map note 2"]}\n-->')
    chk("w1_unquoted_numeric", code == 1 and any("W1 schema" in ln for ln in lines))
    chk("w1_empty_loci", bible(fact("WF-01", loci=[]))[0] == 1)
    code, lines = bible('<!-- apodictic:world_fact\n{"schema":"apodictic.world_fact.v1"\n-->')
    chk("w1_bad_json", code == 1 and any("W1 schema" in ln for ln in lines))
    # closed-key: a misspelled field the subset engine would ADMIT must be caught (the bespoke pass)
    code, lines = bible(fact("WF-01", polairty="cannot"))
    chk("w1_closed_key_misspell", code == 1 and any("unknown field" in ln for ln in lines))
    chk("w1_known_optional_ok", bible(fact("WF-01", polarity="cannot", cost=None))[0] == 0)
    # closed-key admits `cost` but the schema leaves it un-typed; a non-string/non-null `cost`
    # (numeric, list, bool) must be a clean W1 ERROR, not an uncaught AttributeError in the cost arm.
    code, lines = bible(fact("WF-01", category="cost", subject="bm", attribute="cost",
                             value="p", cost=5))
    chk("w1_cost_not_string_numeric",
        code == 1 and any("W1 schema" in ln and "`cost` must be a string or null" in ln for ln in lines))
    chk("w1_cost_not_string_list",
        bible(fact("WF-01", category="cost", subject="bm", attribute="cost",
                   value="p", cost=["a", "b"]))[0] == 1)
    chk("w1_cost_not_string_bool",
        bible(fact("WF-01", category="cost", subject="bm", attribute="cost",
                   value="p", cost=True))[0] == 1)

    # W1 per-category KEYED requirements (P1, round 9) — a fact whose category needs an arm-specific
    # field but omits it must FAIL W1 (and therefore --strict), not pass and get silently skipped by
    # its arm. Build the malformed facts WITHOUT going through fact() (whose helpers add nothing the
    # check forbids), spelling each category out so the smallest-input-that-breaks is explicit.
    def raw(d):
        return "<!-- apodictic:world_fact\n%s\n-->" % _j.dumps(
            dict({"schema": _SCHEMA_ID, "loci": ["Bible §1"]}, **d))
    # rule with NO polarity -> W1 ERROR (was: PASS, silently skipped by WB-R1)
    code, lines = bible(raw({"id": "WF-01", "category": "rule", "subject": "blood-magic",
                             "attribute": "limit", "value": "raise the dead"}), strict=True)
    chk("w1_rule_requires_polarity",
        code == 1 and any("category=rule requires `polarity`" in ln for ln in lines))
    # explicit polarity="n/a" is the stated opt-out -> allowed (present, just makes no claim)
    chk("w1_rule_polarity_na_ok",
        bible(raw({"id": "WF-01", "category": "rule", "subject": "blood-magic",
                   "attribute": "limit", "value": "x", "polarity": "n/a"}), strict=True)[0] == 0)
    # cost with NO cost field -> W1 ERROR (was: PASS, skipped by WB-C1/C2)
    code, lines = bible(raw({"id": "WF-01", "category": "cost", "subject": "blood-magic",
                             "attribute": "cost", "value": "the price"}), strict=True)
    chk("w1_cost_requires_cost",
        code == 1 and any("category=cost requires the `cost` field" in ln for ln in lines))
    # cost=null IS a stated (free) cost -> allowed (the WB-C2 free form)
    chk("w1_cost_null_ok",
        bible(raw({"id": "WF-01", "category": "cost", "subject": "bm", "attribute": "cost",
                   "value": "v", "cost": None}), strict=True)[0] == 0)
    # distance with NO pair_subject -> W1 ERROR (was: PASS, skipped by WB-G1)
    code, lines = bible(raw({"id": "WF-01", "category": "distance", "subject": "Karth",
                             "attribute": "distance-to", "value": "120 miles"}), strict=True)
    chk("w1_distance_requires_pair_subject",
        code == 1 and any("category=distance requires a non-empty `pair_subject`" in ln for ln in lines))
    # distance with EMPTY pair_subject -> still W1 ERROR (empty feeds no arm)
    chk("w1_distance_empty_pair_subject",
        bible(raw({"id": "WF-01", "category": "distance", "subject": "Karth",
                   "attribute": "distance-to", "value": "120 miles", "pair_subject": "  "}),
              strict=True)[0] == 1)
    # event with NEITHER pair_subject NOR a Day/Week anchor -> W1 ERROR (was: PASS, skipped by WB-G2)
    code, lines = bible(raw({"id": "WF-01", "category": "event", "subject": "the Sundering",
                             "attribute": "when", "value": "long ago"}), strict=True)
    chk("w1_event_requires_edge_or_anchor",
        code == 1 and any("category=event requires either" in ln for ln in lines))
    # event WITH a pair_subject (ordering edge) -> allowed
    chk("w1_event_edge_ok",
        bible(raw({"id": "WF-01", "category": "event", "subject": "X", "attribute": "happens-before",
                   "value": "before", "pair_subject": "Y"}), strict=True)[0] == 0)
    # event WITH a Day anchor (chronology anchor, no edge) -> allowed
    chk("w1_event_anchor_ok",
        bible(raw({"id": "WF-01", "category": "event", "subject": "X", "attribute": "Day 100",
                   "value": "Day 100"}), strict=True)[0] == 0)
    # categories with NO arm impose no keyed field (descriptive-only) -> allowed
    chk("w1_place_no_keyed_field",
        bible(raw({"id": "WF-01", "category": "place", "subject": "Karth",
                   "attribute": "desc", "value": "a port city"}), strict=True)[0] == 0)
    chk("w1_faction_no_keyed_field",
        bible(raw({"id": "WF-01", "category": "faction", "subject": "the Guild",
                   "attribute": "desc", "value": "merchants"}), strict=True)[0] == 0)
    chk("w1_entity_no_keyed_field",
        bible(raw({"id": "WF-01", "category": "entity", "subject": "the Sword",
                   "attribute": "desc", "value": "a relic"}), strict=True)[0] == 0)

    # WD — duplicate id
    code, lines = bible(fact("WF-01", polarity="can", value="fly")
                        + "\n" + fact("WF-01", polarity="cannot", value="swim"))
    chk("wd_duplicate_id", code == 1 and any("WD duplicate id" in ln for ln in lines))

    # WB-R1 — rule contradiction (can vs cannot on the same normalized value); override silences
    can = fact("WF-01", subject="blood-magic", value="raise the dead", polarity="can")
    cannot = fact("WF-02", subject="blood-magic", value="Raise  the  Dead", polarity="cannot")
    code, lines = bible(can + "\n" + cannot)
    chk("wb_r1_fires", code == 1 and any("WB-R1 rule" in ln for ln in lines))
    # requires vs cannot also contradicts
    req = fact("WF-01", subject="blood-magic", value="a blood sacrifice", polarity="requires")
    forb = fact("WF-02", subject="blood-magic", value="a blood sacrifice", polarity="cannot")
    chk("wb_r1_requires_cannot", bible(req + "\n" + forb)[0] == 1)
    # different values do NOT collide (literal, not semantic): "can fly" vs "cannot swim"
    chk("wb_r1_different_value_clean",
        bible(fact("WF-01", value="fly", polarity="can")
              + "\n" + fact("WF-02", value="swim", polarity="cannot"))[0] == 0)
    # same polarity twice is not a contradiction
    chk("wb_r1_same_polarity_clean",
        bible(fact("WF-01", value="fly", polarity="can")
              + "\n" + fact("WF-02", value="fly", polarity="can"))[0] == 0)
    ov = "<!-- override: world-rule WF-01/WF-02 — staged reveal: the limit changes after the Sundering -->\n"
    chk("wb_r1_override", bible(ov + can + "\n" + cannot)[0] == 0)
    chk("wb_r1_override_order_insensitive",
        bible("<!-- override: world-rule WF-02/WF-01 — reversed -->\n" + can + "\n" + cannot)[0] == 0)

    # WB-C1 — two different real costs for one subject; override silences
    c_a = fact("WF-01", category="cost", subject="blood-magic", attribute="cost",
               value="the price of a casting", cost="one year of life")
    c_b = fact("WF-02", category="cost", subject="blood-magic", attribute="cost",
               value="the price of a casting", cost="a drop of blood")
    code, lines = bible(c_a + "\n" + c_b)
    chk("wb_c1_fires", code == 1 and any("WB-C1 cost" in ln for ln in lines))
    # same cost twice — agree, not a collision
    chk("wb_c1_same_cost_clean",
        bible(fact("WF-01", category="cost", subject="x", attribute="cost", value="p", cost="one year of life")
              + "\n" + fact("WF-02", category="cost", subject="x", attribute="cost", value="p", cost="One Year of Life"))[0] == 0)
    ov_c = "<!-- override: world-cost WF-01/WF-02 — documented escalation: novices pay more -->\n"
    chk("wb_c1_override", bible(ov_c + c_a + "\n" + c_b)[0] == 0)

    # WB-C2 — free-then-costed (advisory; ERROR under --strict; override)
    free = fact("WF-01", category="cost", subject="blood-magic", attribute="cost", value="free use", cost="none")
    costed = fact("WF-02", category="cost", subject="blood-magic", attribute="cost",
                  value="the price", cost="one year of life")
    code, lines = bible(free + "\n" + costed)
    chk("wb_c2_advisory", code == 0 and any("WB-C2 free-vs-costed" in ln for ln in lines))
    chk("wb_c2_strict_fails", bible(free + "\n" + costed, strict=True)[0] == 1)
    chk("wb_c2_null_cost_is_free",
        any("WB-C2" in ln for ln in bible(
            fact("WF-01", category="cost", subject="bm", attribute="cost", value="v", cost=None)
            + "\n" + fact("WF-02", category="cost", subject="bm", attribute="cost", value="v2", cost="a life"))[1]))
    ov_c2 = "<!-- override: world-cost WF-01/WF-02 — the free tier is the staged hook -->\n"
    chk("wb_c2_override", not any("WB-C2" in ln for ln in bible(ov_c2 + free + "\n" + costed)[1]))

    # WB-G1 — distance contradiction WITHIN an axis; cross-axis is EXEMPT (P3 #4)
    d6 = fact("WF-01", category="distance", subject="Karth", attribute="distance-to",
              value="6 days", pair_subject="the capital")
    d2 = fact("WF-02", category="distance", subject="Karth", attribute="distance-to",
              value="2 days", pair_subject="the capital")
    code, lines = bible(d6 + "\n" + d2)
    chk("wb_g1_temporal_fires", code == 1 and any("WB-G1 distance" in ln for ln in lines))
    # spatial collision: 120 miles vs 40 leagues(=120mi) AGREE; 120 miles vs 200 miles collide
    sp_a = fact("WF-01", category="distance", subject="Karth", attribute="distance-to",
                value="120 miles", pair_subject="the capital")
    sp_b = fact("WF-02", category="distance", subject="Karth", attribute="distance-to",
                value="40 leagues", pair_subject="the capital")
    chk("wb_g1_spatial_agree_clean", bible(sp_a + "\n" + sp_b)[0] == 0)
    sp_c = fact("WF-02", category="distance", subject="Karth", attribute="distance-to",
                value="200 miles", pair_subject="the capital")
    chk("wb_g1_spatial_collide", bible(sp_a + "\n" + sp_c)[0] == 1)
    # unit-conversion noise within 1% AGREES (160.934 km ≈ 100 miles); float drift is not an ERROR
    sp_km = fact("WF-02", category="distance", subject="Karth", attribute="distance-to",
                 value="160.934 km", pair_subject="the capital")
    sp_100 = fact("WF-01", category="distance", subject="Karth", attribute="distance-to",
                  value="100 miles", pair_subject="the capital")
    chk("wb_g1_conversion_tolerance_clean", bible(sp_100 + "\n" + sp_km)[0] == 0)
    # CROSS-AXIS exemption: "6 days" (temporal, WF-01) vs "120 miles" (spatial, WF-03) for one edge
    # => NOT compared (a travel-time and a mileage can both be true).
    sp_a3 = fact("WF-03", category="distance", subject="Karth", attribute="distance-to",
                 value="120 miles", pair_subject="the capital")
    chk("wb_g1_cross_axis_exempt", bible(d6 + "\n" + sp_a3)[0] == 0)
    # edge is unordered: A->B and B->A are the same edge
    d2_rev = fact("WF-02", category="distance", subject="the capital", attribute="distance-to",
                  value="2 days", pair_subject="Karth")
    chk("wb_g1_edge_unordered", bible(d6 + "\n" + d2_rev)[0] == 1)
    ov_g = "<!-- override: world-geo WF-01/WF-02 — the fast road halves the ride -->\n"
    chk("wb_g1_override", bible(ov_g + d6 + "\n" + d2)[0] == 0)
    # unparseable unit -> exempt, never a false ERROR
    chk("wb_g1_unparseable_exempt",
        bible(fact("WF-01", category="distance", subject="A", attribute="distance-to",
                   value="a fortnight's walk", pair_subject="B")
              + "\n" + fact("WF-02", category="distance", subject="A", attribute="distance-to",
                            value="some way off", pair_subject="B"))[0] == 0)

    # WB-G2 — chronology cycle + anchor drift; override silences each
    e1 = fact("WF-01", category="event", subject="the Sundering", attribute="happens-before",
              value="before", pair_subject="the Founding")
    e2 = fact("WF-02", category="event", subject="the Founding", attribute="happens-before",
              value="before", pair_subject="the War")
    e3 = fact("WF-03", category="event", subject="the War", attribute="happens-before",
              value="before", pair_subject="the Sundering")
    code, lines = bible(e1 + "\n" + e2 + "\n" + e3)
    chk("wb_g2_cycle_fires", code == 1 and any("WB-G2 chronology" in ln and "cycle" in ln for ln in lines))
    # acyclic chain is clean
    chk("wb_g2_chain_clean", bible(e1 + "\n" + e2)[0] == 0)
    ov_cyc = "<!-- override: world-geo WF-01/WF-02 — intentional time-loop myth -->\n"
    chk("wb_g2_cycle_override", bible(ov_cyc + e1 + "\n" + e2 + "\n" + e3)[0] == 0)
    # anchor drift: same event at two Day anchors
    a1 = fact("WF-01", category="event", subject="the Sundering", attribute="Day 100", value="Day 100")
    a2 = fact("WF-02", category="event", subject="the Sundering", attribute="Day 200", value="Day 200")
    code, lines = bible(a1 + "\n" + a2)
    chk("wb_g2_anchor_drift_fires", code == 1 and any("WB-G2 chronology" in ln and "different days" in ln for ln in lines))
    ov_a = "<!-- override: world-geo WF-01/WF-02 — two calendars (old/new reckoning) -->\n"
    chk("wb_g2_anchor_override", bible(ov_a + a1 + "\n" + a2)[0] == 0)

    # WF — firewall prose scan (advisory; ERROR --strict; override)
    resolve_prose = "## Notes\n\nThe true order is Day 100 for the Sundering; WF-02 is wrong.\n"
    code, lines = bible(a1 + "\n" + a2 + "\n" + ov_a + resolve_prose)
    chk("wf_firewall_advisory", any("WF firewall" in ln for ln in lines))
    chk("wf_firewall_strict_fails",
        bible(a1 + "\n" + a2 + "\n" + ov_a + resolve_prose, strict=True)[0] == 1)
    fw_ov = "<!-- override: world-firewall — quoting the author's own reconciliation note -->\n"
    chk("wf_firewall_override",
        not any("WF firewall" in ln for ln in bible(a1 + "\n" + a2 + "\n" + ov_a + fw_ov + resolve_prose)[1]))
    # clean descriptive prose does not trip WF
    chk("wf_clean_prose_ok",
        not any("WF firewall" in ln for ln in bible(
            fact("WF-01", polarity="cannot") + "\n## Notes\n\nThe bible states one rule, cited.\n")[1]))

    # no blocks -> no-op
    chk("no_facts_noop", bible("# Notes\nnothing structured\n")[0] == 0)

    # run-folder + explicit-file resolution
    import tempfile
    import shutil
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "Proj_Worldbuilding_Bible_run.md")
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Worldbuilding Bible\n" + fact("WF-01", polarity="cannot") + "\n")
        chk("run_folder_resolution", run([d])[0] == 0)
        chk("explicit_file_resolution", run([p])[0] == 0)
        chk("missing_artifact_usage", run([os.path.join(d, "nope.md")])[0] == 2)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "world-bible"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: world_bible.py world-bible <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
