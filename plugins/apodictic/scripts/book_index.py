#!/usr/bin/env python3
"""book-index — the Manuscript Index Builder's topic map: its validator and its only writer.

`validate.py book-index <run_folder|index_map.md>` delegates here. An Index_Map
(`[Project]_Index_Map_[runlabel].md`) is one `apodictic.index_map.v1` header block plus one
`apodictic.index_heading.v1` block per proposed heading. Every heading is tied to the manuscript by
verbatim quote anchors, and only headings the author accepted, unchanged since, may reach an index.
The tool never changes the manuscript and never invents passages.

  I1 schema            header and heading fields, closed keys, the nested anchor and subheading rules
                       (id patterns, role enum, single-line strings, context shape), accepted_hash
                       present exactly when accepted, the See-only shape and the substantive-anchor
                       minimums. Covers every heading, dropped ones included.
  I2 provenance        every quote (with its context) and every end_quote occurs in the snapshot
                       exactly once (non-overlapping str.count, as A6), and an end_quote comes after
                       its quote. A missing snapshot is an ERROR.
  I3 cross-references  every See / See also target exists, is not dropped and is not a See-only
                       heading; the See graph has no cycle. Reciprocal See also links are allowed.
  I4 acceptance        an accepted heading's accepted_hash equals the hash of its current content.
  W1 coverage          a chapter with no substantive anchor (possible under-indexing).
  W2 locator strings   a heading or subheading with more than six substantive anchors of its own.
  W3 subheadings       a lone subheading, a subheading whose anchor spans equal its parent's or a
                       sibling's, or more than twelve subheadings under one heading.
I2, I3 and W1-W3 skip dropped headings. W checks are advisory and ERROR under --strict; there are no
override markers. I2 proves an anchor is a real passage, not that it is about its heading; the review
list shows every anchor in context so the author judges that.

Writer commands. The map is the only state, and these are the only ways it changes. The /book-index
command runs them from the author's explicit replies; acceptance is per heading id or per kind group.
  init        write the snapshot and the map from model proposals (all forced to `proposed`)
  update      replace or add headings from proposals (a changed heading returns to `proposed`)
  review      print the review list: headings by kind and weight, every anchor in context
  accept      record acceptance (status + accepted_hash) after the heading passes I1-I3
  drop        set headings to `dropped`
  rename      change a heading's printed text (re-opens an accepted heading)
  merge       fold a source heading into a target (spec §Author decisions)
  resnapshot  re-anchor the map on a corrected text and re-open headings whose passages changed

  book_index.py book-index <run_folder|index_map.md> [--strict]
  book_index.py init <source_text> <run_folder> <project> <runlabel> <proposals.json> [--chapter-level N]
  book_index.py update <index_map.md> <proposals.json>
  book_index.py review <index_map.md>
  book_index.py accept <index_map.md> (<IX-id>... | --kind <kind>)
  book_index.py drop <index_map.md> <IX-id>...
  book_index.py rename <index_map.md> <IX-id> <new heading>
  book_index.py merge <index_map.md> <source IX-id> <target IX-id>
  book_index.py resnapshot <index_map.md> <new_source_text> <runlabel>
  book_index.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict, or a refused write), 2 usage.
See docs/manuscript-indexing.md.
"""
import bisect
import copy
import glob
import hashlib
import json
import os
import re
import sys

import annotation_manifest as am
import apodictic_artifacts as art
import reanchor

MAP_SCHEMA = "apodictic.index_map.v1"
HEADING_SCHEMA = "apodictic.index_heading.v1"
_MAP_GLOB = "*_Index_Map_*.md"
_HEADING_ID_RE = re.compile(r"^IX-[0-9]{3,}$")
_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_SNAPSHOT_RE = re.compile(r"^(.+)_Manuscript_Snapshot_[^/]+\.md$")
_KINDS = ("name", "place", "work", "concept", "term")
_ANCHOR_KEYS = {"id", "quote", "role", "end_quote", "context"}
_SUB_KEYS = {"id", "label", "anchors"}
_HASH_EXCLUDED = ("status", "accepted_hash", "weight")
_W2_MAX = 6
_W3_MAX_SUBS = 12


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _write(path, text):
    """Encode first, then replace atomically, so a failed write never truncates the old file."""
    data = text.encode("utf-8")
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.replace(tmp, path)


def _one_line(value):
    return isinstance(value, str) and "\n" not in value and "\r" not in value


def accepted_hash(heading):
    """sha256 of the heading's canonical JSON minus status, accepted_hash and weight."""
    projection = {k: v for k, v in heading.items() if k not in _HASH_EXCLUDED}
    canon = json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- the map carrier

def parse_map(text):
    """-> (header_or_None, headings, errors). Errors are (heading_id_or_None, message) for blocks
    that cannot be read at all; a heading that parses but breaks a rule is left to check()."""
    header, headings, errs = None, [], []
    n_headers = n_blocks = 0
    for btype, obj, jerr in art.parse_blocks(text or ""):
        if btype == "index_map":
            n_headers += 1
            if jerr:
                errs.append((None, "I1 schema: index_map header: invalid JSON — %s" % jerr))
            elif n_headers == 1:
                header = obj
        elif btype == "index_heading":
            n_blocks += 1
            if jerr:
                errs.append((None, "I1 schema: index_heading #%d: invalid JSON — %s" % (n_blocks, jerr)))
            else:
                headings.append(obj)
    if n_headers != 1:
        errs.append((None, "I1 schema: a map needs exactly one index_map header (found %d)" % n_headers))
    return header, headings, errs


def _block(btype, obj):
    # JSON never uses < or > outside strings, so escaping them everywhere keeps a quote holding
    # `-->` from closing the HTML-comment carrier; json.loads decodes them back.
    body = json.dumps(obj, indent=2, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e")
    return "<!-- apodictic:%s\n%s\n-->\n" % (btype, body)


def render_map(header, headings):
    parts = ["# Index Map\n\nWritten by book_index.py. Change it only through /book-index.\n\n",
             _block("index_map", header)]
    for h in headings:
        parts.append("\n" + _block("index_heading", h))
    return "".join(parts)


def _snapshot_path(map_path, header):
    rel = header.get("snapshot_path") if isinstance(header, dict) else None
    if not isinstance(rel, str) or not rel:
        return None
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(map_path)), rel))


# ---------------------------------------------------------------- snapshot structure

def chapters(snapshot, level):
    """[(label, start, end)] char spans. A chapter starts at each ATX heading of `level` and runs to
    the next heading of that level or higher. Text before the first chapter is front matter."""
    # atx_headings numbers lines by str.splitlines, so the offsets must too.
    line_starts, pos = [], 0
    for line in snapshot.splitlines(keepends=True):
        line_starts.append(pos)
        pos += len(line)
    heads = []
    for lineno, raw, _norm in am.atx_headings(snapshot):
        start = line_starts[lineno - 1]
        depth = re.match(r"#+", snapshot[start:]).end()
        heads.append((depth, raw.strip(), start))
    out = []
    for i, (depth, label, start) in enumerate(heads):
        if depth != level:
            continue
        end = next((s for d, _l, s in heads[i + 1:] if d <= level), len(snapshot))
        out.append((label, start, end))
    return out


def _chapter_at(chaps, pos):
    for label, start, end in chaps:
        if start <= pos < end:
            return label
    return None


def _paragraph_spans(snapshot):
    """Sorted (start, end) spans of blank-line-separated blocks."""
    spans, start = [], 0
    for m in re.finditer(r"\n[ \t]*\n(?:[ \t]*\n)*", snapshot):
        spans.append((start, m.start()))
        start = m.end()
    spans.append((start, len(snapshot)))
    return spans


def _paragraph_text(snapshot, paras, start, end):
    """The text of every paragraph the span [start, end) touches."""
    starts = [s for s, _e in paras]
    i = max(bisect.bisect_right(starts, start) - 1, 0)
    j = max(bisect.bisect_right(starts, max(end - 1, start)) - 1, 0)
    return snapshot[paras[i][0]:paras[j][1]]


def locate(anchor, snapshot):
    """-> ((start, end), None) for the anchor's resolved span, or (None, reason)."""
    ctx = anchor.get("context") or {}
    before, after = ctx.get("before", ""), ctx.get("after", "")
    target = before + anchor["quote"] + after
    n = snapshot.count(target)
    if n != 1:
        return None, ("quote not found in the snapshot" if n == 0
                      else "quote occurs %d times in the snapshot" % n)
    q_start = snapshot.find(target) + len(before)
    q_end = q_start + len(anchor["quote"])
    end_quote = anchor.get("end_quote")
    if end_quote is None:
        return (q_start, q_end), None
    n = snapshot.count(end_quote)
    if n != 1:
        return None, ("end_quote not found in the snapshot" if n == 0
                      else "end_quote occurs %d times in the snapshot" % n)
    e_start = snapshot.find(end_quote)
    if e_start < q_end:
        return None, "end_quote comes before the end of its quote"
    return (q_start, e_start + len(end_quote)), None


def _all_anchors(heading):
    """[(owner_id, anchor)] for the heading's own anchors, then each subheading's."""
    out = [(heading["id"], a) for a in heading.get("anchors") or []]
    for sub in heading.get("subheadings") or []:
        out.extend((sub["id"], a) for a in sub.get("anchors") or [])
    return out


def _is_live(heading):
    return heading.get("status") != "dropped"


# ---------------------------------------------------------------- I1

def _anchor_errs(anchor, owner, where):
    if not isinstance(anchor, dict):
        return ["%s: anchor must be an object" % where]
    errs = ["%s: unknown anchor field %r" % (where, k) for k in sorted(anchor) if k not in _ANCHOR_KEYS]
    for k in ("id", "quote", "role", "end_quote"):
        if k not in anchor:
            errs.append("%s: anchor missing %r" % (where, k))
    aid = anchor.get("id")
    if "id" in anchor and not (isinstance(aid, str) and re.fullmatch(re.escape(owner) + r"\.a[0-9]+", aid)):
        errs.append("%s: anchor id %r must be %s.a<N>" % (where, aid, owner))
    if "quote" in anchor and not (_one_line(anchor["quote"]) and anchor["quote"]):
        errs.append("%s: quote must be a non-empty single-line string" % where)
    if "role" in anchor and anchor["role"] not in ("substantive", "passing"):
        errs.append("%s: role %r not in substantive / passing" % (where, anchor["role"]))
    eq = anchor.get("end_quote")
    if eq is not None and not (_one_line(eq) and eq):
        errs.append("%s: end_quote must be null or a non-empty single-line string" % where)
    if "context" in anchor:
        ctx = anchor["context"]
        if not (isinstance(ctx, dict) and set(ctx) == {"before", "after"}
                and _one_line(ctx["before"]) and _one_line(ctx["after"])):
            errs.append("%s: context must be {\"before\": str, \"after\": str}, single-line" % where)
    return errs


def _substantive(anchors):
    return sum(1 for a in anchors if isinstance(a, dict) and a.get("role") == "substantive")


def heading_errs(h, index):
    """I1 errors for one heading (a dict)."""
    hid = h.get("id") if isinstance(h.get("id"), str) else "index_heading #%d" % index
    errs = art.validate_obj(h, art.load_schema(HEADING_SCHEMA), hid)
    if errs:
        return ["I1 schema: " + e for e in errs]
    try:
        json.dumps(h, ensure_ascii=False).encode("utf-8")
    except UnicodeEncodeError:
        return ["I1 schema: %s: a string is not valid Unicode (a lone surrogate)" % hid]
    w = h["weight"]
    if isinstance(w, bool) or not 0 <= w <= 1:
        errs.append("%s: weight must be a number in [0, 1]" % hid)
    if not h["heading"].strip():
        errs.append("%s: heading must be non-empty" % hid)
    if (h["status"] == "accepted") != ("accepted_hash" in h):
        errs.append("%s: accepted_hash is required when accepted and absent otherwise" % hid)
    for field in ("see", "see_also"):
        for t in h[field]:
            if not _HEADING_ID_RE.match(t):
                errs.append("%s: %s entry %r is not a heading id" % (hid, field, t))
    for i, a in enumerate(h["anchors"]):
        errs.extend(_anchor_errs(a, hid, "%s anchor #%d" % (hid, i + 1)))
    for i, sub in enumerate(h["subheadings"]):
        where = "%s subheading #%d" % (hid, i + 1)
        if not isinstance(sub, dict):
            errs.append("%s: must be an object" % where)
            continue
        errs.extend("%s: unknown subheading field %r" % (where, k) for k in sorted(sub) if k not in _SUB_KEYS)
        sid = sub.get("id")
        if not (isinstance(sid, str) and re.fullmatch(re.escape(hid) + r"\.s[0-9]+", sid)):
            errs.append("%s: id %r must be %s.s<N>" % (where, sid, hid))
            sid = where
        if not (isinstance(sub.get("label"), str) and sub["label"].strip()):
            errs.append("%s: label must be non-empty" % where)
        anchors = sub.get("anchors")
        if not isinstance(anchors, list):
            errs.append("%s: anchors must be an array" % where)
            continue
        for j, a in enumerate(anchors):
            errs.extend(_anchor_errs(a, sid, "%s anchor #%d" % (sid, j + 1)))
        if _is_live(h) and not _substantive(anchors):
            errs.append("%s: a subheading needs at least one substantive anchor" % sid)
    if h["see"] and (h["anchors"] or h["subheadings"] or h["see_also"]):
        errs.append("%s: a See-only heading has no anchors, no subheadings and no See also" % hid)
    if _is_live(h) and not h["see"]:
        subs = [s for s in h["subheadings"] if isinstance(s, dict) and isinstance(s.get("anchors"), list)]
        if not (_substantive(h["anchors"]) or any(_substantive(s["anchors"]) for s in subs)):
            errs.append("%s: needs a substantive anchor of its own or in a subheading" % hid)
    return ["I1 schema: " + e for e in errs]


def header_errs(header):
    errs = ["I1 schema: " + e for e in art.validate_obj(header, art.load_schema(MAP_SCHEMA), "index_map")]
    if not errs:
        level = header.get("chapter_level", 1)
        if isinstance(level, bool) or not isinstance(level, int) or not 1 <= level <= 6:
            errs.append("I1 schema: index_map: chapter_level must be an integer 1 to 6")
        if not header["snapshot_path"]:
            errs.append("I1 schema: index_map: snapshot_path must be non-empty")
    return errs


# ---------------------------------------------------------------- the validator

def check(header, headings, snapshot):
    """-> (errors, warns, notes, spans). errors/warns are (heading_id_or_None, message); spans maps
    anchor id -> resolved span for every anchor that passed I2. `snapshot` None means it is missing."""
    errors, warns, notes, spans = [], [], [], {}
    if header is not None:
        errors.extend((None, e) for e in header_errs(header))
    ok = []
    seen_ids = set()
    for i, h in enumerate(headings):
        if not isinstance(h, dict):
            errors.append((None, "I1 schema: index_heading #%d: expected a JSON object" % (i + 1)))
            continue
        errs = heading_errs(h, i + 1)
        hid = h.get("id") if isinstance(h.get("id"), str) else None
        if hid in seen_ids:
            errs.append("I1 schema: duplicate heading id %s" % hid)
        seen_ids.add(hid)
        if not errs:
            nested = [s["id"] for s in h["subheadings"]] + [a["id"] for _o, a in _all_anchors(h)]
            errs.extend("I1 schema: duplicate id %s" % x for x in sorted({x for x in nested if nested.count(x) > 1}))
        errors.extend((hid, e) for e in errs)
        if not errs:
            ok.append(h)
    by_id = {h["id"]: h for h in headings if isinstance(h, dict) and isinstance(h.get("id"), str)}
    live = [h for h in ok if _is_live(h)]

    if snapshot is None:
        errors.append((None, "I2 provenance: snapshot not found (snapshot_path in the index_map header)"))
    else:
        for h in live:
            for _owner, a in _all_anchors(h):
                span, why = locate(a, snapshot)
                if span is None:
                    errors.append((h["id"], "I2 provenance: %s: %s" % (a["id"], why)))
                else:
                    spans[a["id"]] = span

    for h in live:
        for field, label in (("see", "See"), ("see_also", "See also")):
            for t in h[field]:
                tgt = by_id.get(t)
                if tgt is None:
                    errors.append((h["id"], "I3 cross-references: %s: %s target %s does not exist"
                                   % (h["id"], label, t)))
                elif not _is_live(tgt):
                    errors.append((h["id"], "I3 cross-references: %s: %s target %s is dropped"
                                   % (h["id"], label, t)))
                elif tgt.get("see"):
                    errors.append((h["id"], "I3 cross-references: %s: %s target %s is a See-only heading"
                                   % (h["id"], label, t)))
    cycle = _see_cycle({h["id"]: [t for t in h["see"] if t in by_id] for h in live})
    if cycle:
        errors.append((cycle[0], "I3 cross-references: See cycle %s" % " -> ".join(cycle)))

    for h in ok:
        if h["status"] == "accepted" and h["accepted_hash"] != accepted_hash(h):
            errors.append((h["id"], "I4 acceptance: %s changed after it was accepted; re-accept it"
                           % h["id"]))

    if snapshot is not None and isinstance(header, dict):
        level = header.get("chapter_level", 1)
        chaps = chapters(snapshot, level) if isinstance(level, int) else []
        if not chaps:
            notes.append("W1 skipped: no chapter headings at level %s" % level)
        for label, start, end in chaps:
            if not any(start <= spans[a["id"]][0] < end
                       for h in live for _o, a in _all_anchors(h)
                       if a["role"] == "substantive" and a["id"] in spans):
                warns.append((None, "W1 coverage: chapter %r has no substantive anchor" % label))
    for h in live:
        owners = [(h["id"], h["anchors"])] + [(s["id"], s["anchors"]) for s in h["subheadings"]]
        for owner, anchors in owners:
            n = _substantive(anchors)
            if n > _W2_MAX:
                warns.append((h["id"], "W2 locator strings: %s has %d substantive anchors; break it down"
                              % (owner, n)))
        subs = h["subheadings"]
        if len(subs) == 1:
            warns.append((h["id"], "W3 subheadings: %s has a lone subheading" % h["id"]))
        if len(subs) > _W3_MAX_SUBS:
            warns.append((h["id"], "W3 subheadings: %s has %d subheadings" % (h["id"], len(subs))))
        span_sets = [frozenset(spans.get(a["id"]) for a in anchors) for _o, anchors in owners]
        for i, sub in enumerate(subs, start=1):
            mine = span_sets[i]
            others = [span_sets[0]] + [s for j, s in enumerate(span_sets[1:], start=1) if j != i]
            if None not in mine and any(mine == other for other in others):
                warns.append((h["id"], "W3 subheadings: %s repeats the anchor spans of its parent or a "
                              "sibling" % sub["id"]))
    return errors, warns, notes, spans


def _see_cycle(graph):
    """The first See cycle found, as [id, ..., id], or None."""
    state = {}

    def visit(node, path):
        state[node] = 1
        for nxt in graph.get(node, []):
            if state.get(nxt) == 1:
                return path[path.index(nxt):] + [nxt]
            if nxt not in state:
                found = visit(nxt, path + [nxt])
                if found:
                    return found
        state[node] = 2
        return None

    for node in sorted(graph):
        if node not in state:
            found = visit(node, [node])
            if found:
                return found
    return None


def load(map_path):
    """-> (text, header, headings, parse_errors, snapshot_text_or_None)."""
    text = _read(map_path)
    if text is None:
        return None, None, [], [(None, "cannot read %s" % map_path)], None
    header, headings, errs = parse_map(text)
    snap_path = _snapshot_path(map_path, header)
    snapshot = _read(snap_path) if snap_path else None
    return text, header, headings, errs, snapshot


def resolve(path):
    if os.path.isdir(path):
        maps = glob.glob(os.path.join(path, _MAP_GLOB))
        return max(maps, key=os.path.getmtime) if maps else None
    return path if os.path.isfile(path) else None


def run(path, strict=False):
    map_path = resolve(path)
    if not map_path:
        return 2, ["book-index: no Index_Map found (need a *_Index_Map_*.md or a map file)"]
    text, header, headings, parse_errs, snapshot = load(map_path)
    if text is None:
        return 2, ["book-index: cannot read %s" % map_path]
    errors, warns, notes, _spans = check(header, headings, snapshot)
    errors = parse_errs + errors
    counts = {}
    for h in headings:
        status = h.get("status") if isinstance(h, dict) else None
        status = status if status in ("proposed", "accepted", "dropped") else "malformed"
        counts[status] = counts.get(status, 0) + 1
    lines = ["book-index: %d heading(s) (%s)" % (
        len(headings), ", ".join("%d %s" % (n, s) for s, n in sorted(counts.items(), key=str)))]
    lines.extend("  ERROR: %s" % msg for _hid, msg in errors)
    lines.extend("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", msg) for _hid, msg in warns)
    lines.extend("  note: %s" % n for n in notes)
    if errors or (strict and warns):
        lines.append("book-index: FAIL (%d error(s)%s)" % (
            len(errors), ", %d strict warn(s)" % len(warns) if strict and warns else ""))
        return 1, lines
    if warns:
        lines.append("WARN: book-index: %d advisory signal(s) — see W1-W3 above" % len(warns))
    else:
        lines.append("book-index: PASS (schema + provenance + cross-references + acceptance + coverage)")
    return 0, lines


# ---------------------------------------------------------------- the review list

def _flat(text):
    return re.sub(r"\s+", " ", text)


def _context(snapshot, span, width=80):
    start, end = span
    return "…%s**%s**%s…" % (_flat(snapshot[max(0, start - width):start]),
                              _flat(snapshot[start:end]), _flat(snapshot[end:end + width]))


def review(map_path):
    header, headings, errs = _loaded(map_path)
    if errs:
        return 1, errs
    snapshot = _read(_snapshot_path(map_path, header))
    if snapshot is None:
        return 1, ["book-index review: snapshot not found; run the validator"]
    errors, _w, _n, spans = check(header, headings, snapshot)
    level = header.get("chapter_level", 1)
    chaps = chapters(snapshot, level) if isinstance(level, int) else []
    by_id = {h["id"]: h for h in headings if isinstance(h, dict) and isinstance(h.get("id"), str)}
    out = ["# Index review list", "",
           "Map: %s. For each heading: accept, rename, merge into another, or drop. "
           "A heading you do not decide stays proposed and is never printed." % os.path.basename(map_path),
           ""]
    if errors:
        out.append("The map has %d validator error(s); headings with errors cannot be accepted." % len(errors))
        out.append("")
    for kind in _KINDS:
        group = sorted((h for h in by_id.values() if h.get("kind") == kind and _is_live(h)),
                       key=lambda h: (-h.get("weight", 0), h["id"]))
        if not group:
            continue
        out += ["## %s (%d)" % (kind.capitalize() + "s", len(group)), ""]
        for h in group:
            out.append("### %s · %s · %s · weight %.2f" % (h["id"], h["heading"], h["status"], h["weight"]))
            if h.get("variants"):
                out.append("Variants: %s" % "; ".join(h["variants"]))
            hit = {_chapter_at(chaps, spans[a["id"]][0]) for _o, a in _all_anchors(h)
                   if a.get("role") == "substantive" and a.get("id") in spans}
            spread = [label for label, _s, _e in chaps if label in hit]
            if spread:
                out.append("Chapters: %s" % "; ".join(spread))
            for field, label in (("see", "See"), ("see_also", "See also")):
                if h.get(field):
                    out.append("%s: %s" % (label, "; ".join(
                        "%s (%s)" % (t, by_id[t]["heading"]) if t in by_id else t for t in h[field])))
            sections = [(None, h.get("anchors") or [])] + [
                (s.get("label"), s.get("anchors") or []) for s in h.get("subheadings") or []]
            for sublabel, anchors in sections:
                if sublabel:
                    out.append("- Subheading: %s" % sublabel)
                for a in anchors:
                    span = spans.get(a.get("id"))
                    shown = _context(snapshot, span) if span else "(not found: %s)" % a.get("quote")
                    out.append("%s- %s [%s] %s" % ("  " if sublabel else "", a.get("id"), a.get("role"), shown))
            out.append("")
    dropped = sorted(hid for hid, h in by_id.items() if not _is_live(h))
    if dropped:
        out.append("Dropped: %s" % ", ".join(dropped))
    return 0, out


# ---------------------------------------------------------------- writer commands

def _refuse(errors, ids=None):
    """Lines for the errors that block a write (global ones, or ones on the named headings)."""
    return ["  ERROR: %s" % msg for hid, msg in errors if hid is None or ids is None or hid in ids]


def _save(map_path, header, headings, ids=None):
    """Validate the would-be map in memory and write it only if I1-I3 hold for `ids` and for every
    heading that links to one of them (or for all headings when `ids` is None)."""
    if ids is not None:
        ids = set(ids) | {h.get("id") for h in headings if isinstance(h, dict)
                          and ids & set(h.get("see", []) + h.get("see_also", []))}
    snapshot = _read(_snapshot_path(map_path, header) or "")
    errors, _w, _n, _s = check(header, headings, snapshot)
    blocking = _refuse([(hid, msg) for hid, msg in errors if not msg.startswith("I4 ")], ids)
    if blocking:
        return 1, ["book-index: refused; the map would not validate:"] + blocking
    try:
        _write(map_path, render_map(header, headings))
    except (OSError, UnicodeEncodeError) as exc:
        return 1, ["book-index: write failed, map unchanged: %s" % exc]
    return 0, []


def _reopen(h):
    h["status"] = "proposed"
    h.pop("accepted_hash", None)


def init(source, run_folder, project, runlabel, proposals_path, chapter_level=1):
    if not (_NAME_RE.match(project) and _NAME_RE.match(runlabel)):
        return 2, ["book-index init: project and runlabel must be plain names (letters, digits, . _ -)"]
    text = _read(source)
    if text is None:
        return 2, ["book-index init: cannot read %s" % source]
    proposals, why = _read_proposals(proposals_path)
    if why:
        return 2, ["book-index init: " + why]
    snap_name = "%s_Manuscript_Snapshot_%s.md" % (project, runlabel)
    map_path = os.path.join(run_folder, "%s_Index_Map_%s.md" % (project, runlabel))
    snap_path = os.path.join(run_folder, snap_name)
    for p in (snap_path, map_path):
        if os.path.exists(p):
            return 1, ["book-index init: %s exists; a run never overwrites a snapshot or map" % p]
    snapshot = am.normalize_snapshot(text)
    for h in proposals:
        _reopen(h)
    header = {"schema": MAP_SCHEMA, "snapshot_path": snap_name, "chapter_level": chapter_level}
    errors, warns, notes, _s = check(header, proposals, snapshot)
    if errors:
        return 1, ["book-index init: refused; fix the proposals:"] + _refuse(errors)
    os.makedirs(run_folder, exist_ok=True)
    _write(snap_path, snapshot)
    _write(map_path, render_map(header, proposals))
    lines = ["book-index init: wrote %s and %s (%d proposed heading(s))"
             % (snap_name, os.path.basename(map_path), len(proposals))]
    lines.extend("  WARN: %s" % msg for _h, msg in warns)
    lines.extend("  note: %s" % n for n in notes)
    return 0, lines


def _read_proposals(path):
    try:
        with open(path, encoding="utf-8") as fh:
            proposals = json.load(fh)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, "cannot read proposals: %s" % exc
    if not isinstance(proposals, list) or not all(isinstance(h, dict) for h in proposals):
        return None, "proposals must be a JSON array of index_heading objects"
    return proposals, None


def _loaded(map_path):
    """-> (header, headings, refusal_lines). Writers refuse a map with any I1 error, so they only
    ever handle well-formed headings."""
    text, header, headings, parse_errs, _snapshot = load(map_path)
    if text is None or header is None or parse_errs:
        return None, None, ["book-index: the map cannot be parsed; run the validator"]
    errors, _w, _n, _s = check(header, headings, None)
    i1 = [(hid, msg) for hid, msg in errors if msg.startswith("I1 ")]
    if i1:
        return None, None, ["book-index: refused; the map has schema errors:"] + _refuse(i1)
    return header, headings, []


def update(map_path, proposals_path):
    """Replace headings by id, or append new ones, from a proposals file. A replaced heading keeps
    its acceptance only when its content is unchanged; anything else is `proposed`."""
    header, headings, errs = _loaded(map_path)
    if errs:
        return 1, errs
    proposals, why = _read_proposals(proposals_path)
    if why:
        return 2, ["book-index update: " + why]
    if not all(isinstance(h.get("id"), str) and _HEADING_ID_RE.match(h["id"]) for h in proposals):
        return 1, ["book-index update: every proposal needs an id like IX-001"]
    index = {h.get("id"): i for i, h in enumerate(headings)}
    for new in proposals:
        old = headings[index[new.get("id")]] if new.get("id") in index else None
        new.pop("accepted_hash", None)
        if old is not None and old.get("status") == "accepted" and old["accepted_hash"] == accepted_hash(new):
            new.update(status="accepted", accepted_hash=old["accepted_hash"])
        else:
            new["status"] = "proposed"
        if old is not None:
            headings[index[new["id"]]] = new
        else:
            index[new.get("id")] = len(headings)
            headings.append(new)
    ids = {h.get("id") for h in proposals}
    code, lines = _save(map_path, header, headings, ids)
    return code, lines or ["book-index update: %d heading(s) written; changed ones are proposed" % len(proposals)]


def accept(map_path, ids=None, kind=None):
    header, headings, errs = _loaded(map_path)
    if errs:
        return 1, errs
    by_id = {h.get("id"): h for h in headings if isinstance(h, dict)}
    if kind is not None:
        ids = [h["id"] for h in headings if isinstance(h, dict) and h.get("kind") == kind
               and h.get("status") == "proposed"]
    missing = [i for i in ids if i not in by_id or not _is_live(by_id[i])]
    if missing or not ids:
        return 1, ["book-index accept: no live heading %s" % ", ".join(missing or ["selected"])]
    for i in ids:
        by_id[i]["status"] = "accepted"
        by_id[i]["accepted_hash"] = accepted_hash(by_id[i])
    code, lines = _save(map_path, header, headings, set(ids))
    return code, lines or ["book-index accept: accepted %s" % ", ".join(ids)]


def drop(map_path, ids):
    header, headings, errs = _loaded(map_path)
    if errs:
        return 1, errs
    by_id = {h.get("id"): h for h in headings if isinstance(h, dict)}
    missing = [i for i in ids if i not in by_id]
    if missing:
        return 1, ["book-index drop: no heading %s" % ", ".join(missing)]
    for i in ids:
        by_id[i]["status"] = "dropped"
        by_id[i].pop("accepted_hash", None)
    code, lines = _save(map_path, header, headings, set(ids))
    return code, lines or ["book-index drop: dropped %s" % ", ".join(ids)]


def rename(map_path, hid, new_heading):
    header, headings, errs = _loaded(map_path)
    if errs:
        return 1, errs
    h = next((h for h in headings if isinstance(h, dict) and h.get("id") == hid), None)
    if h is None or not new_heading.strip():
        return 1, ["book-index rename: no heading %s, or an empty new heading" % hid]
    h["heading"] = new_heading
    _reopen(h)
    code, lines = _save(map_path, header, headings, {hid})
    return code, lines or ["book-index rename: %s is now %r and back to proposed" % (hid, new_heading)]


def _max_index(items, prefix, letter):
    pat = re.compile(re.escape(prefix) + r"\." + letter + r"([0-9]+)$")
    return max([int(m.group(1)) for m in (pat.match(x.get("id", "")) for x in items) if m] or [0])


def merge(map_path, source_id, target_id):
    """Fold source into target (spec §Author decisions): anchors and subheadings move and are
    renumbered, the source's heading and variants join the target's variants, See lists union,
    references to the source repoint to the target, the source is emptied and dropped, and the
    target and every rewritten heading return to proposed."""
    header, headings, errs = _loaded(map_path)
    if errs:
        return 1, errs
    by_id = {h.get("id"): h for h in headings if isinstance(h, dict)}
    src, tgt = by_id.get(source_id), by_id.get(target_id)
    if src is None or tgt is None or src is tgt or not (_is_live(src) and _is_live(tgt)):
        return 1, ["book-index merge: need two different live headings"]
    n = _max_index(tgt["anchors"], target_id, "a")
    for a in src["anchors"]:
        n += 1
        tgt["anchors"].append(dict(a, id="%s.a%d" % (target_id, n)))
    n = _max_index(tgt["subheadings"], target_id, "s")
    for sub in src["subheadings"]:
        n += 1
        sid = "%s.s%d" % (target_id, n)
        moved = [dict(a, id=sid + a["id"][len(sub["id"]):]) for a in sub["anchors"]]
        tgt["subheadings"].append(dict(sub, id=sid, anchors=moved))
    for v in [src["heading"]] + list(src["variants"]):
        if v != tgt["heading"] and v not in tgt["variants"]:
            tgt["variants"].append(v)
    for field in ("see", "see_also"):
        merged = []
        for t in tgt[field] + src[field]:
            if t not in (source_id, target_id) and t not in merged:
                merged.append(t)
        tgt[field] = merged
    reopened = [target_id]
    for h in headings:
        if not isinstance(h, dict) or h is src or h is tgt:
            continue
        for field in ("see", "see_also"):
            if source_id in h.get(field, []):
                new = []
                for t in h[field]:
                    t = target_id if t == source_id else t
                    if t != h.get("id") and t not in new:
                        new.append(t)
                h[field] = new
                if h["id"] not in reopened:
                    reopened.append(h["id"])
    for hid in reopened:
        _reopen(by_id[hid])
    src.update(status="dropped", anchors=[], subheadings=[], see=[], see_also=[])
    src.pop("accepted_hash", None)
    code, lines = _save(map_path, header, headings, set(reopened) | {source_id})
    return code, lines or ["book-index merge: %s merged into %s; back to proposed for review: %s"
                           % (source_id, target_id, ", ".join(reopened))]


def resnapshot(map_path, new_source, runlabel):
    """Re-anchor the map on a corrected text. An anchor that vanished or became ambiguous, or whose
    paragraph text (across its whole span) or chapter changed, re-opens its heading."""
    header, headings, errs = _loaded(map_path)
    if errs:
        return 1, errs
    old_path = _snapshot_path(map_path, header)
    old = _read(old_path or "")
    new_text = _read(new_source)
    m = _SNAPSHOT_RE.match(os.path.basename(old_path or ""))
    if old is None or new_text is None or not m or not _NAME_RE.match(runlabel):
        return 2, ["book-index resnapshot: need the current snapshot, a readable new text and a plain runlabel"]
    new_name = "%s_Manuscript_Snapshot_%s.md" % (m.group(1), runlabel)
    new_path = os.path.join(os.path.dirname(old_path), new_name)
    if os.path.exists(new_path):
        return 1, ["book-index resnapshot: %s exists; choose a new runlabel" % new_name]
    new = am.normalize_snapshot(new_text)
    level = header.get("chapter_level", 1)
    old_ch, new_ch = chapters(old, level), chapters(new, level)
    old_par, new_par = _paragraph_spans(old), _paragraph_spans(new)
    broken, changed = [], []
    for h in headings:
        if not isinstance(h, dict) or not _is_live(h):
            continue
        reasons = []
        for _o, a in _all_anchors(h):
            ctx = a.get("context") or {}
            span, _why = locate(a, old)
            if span is None:
                broken.append("%s %s: not found in the old snapshot" % (h["id"], a["id"]))
                reasons.append("broken quote")
                continue
            pieces = [ctx.get("before", "") + a["quote"] + ctx.get("after", "")]
            if a.get("end_quote") is not None:
                pieces.append(a["end_quote"])
            klasses = []
            for piece in pieces:
                start = old.find(piece)
                klass, _nv, _ev = reanchor.classify_quote(piece, "%d-%d" % (start, start + len(piece)), new)
                klasses.append(klass)
            bad = [k for k in klasses if k not in ("held", "moved")]
            if bad:
                broken.append("%s %s: %s" % (h["id"], a["id"], "/".join(bad)))
                reasons.append("broken quote")
                continue
            new_span, why = locate(a, new)
            if new_span is None:
                broken.append("%s %s: %s" % (h["id"], a["id"], why))
                reasons.append("broken quote")
            elif (_paragraph_text(old, old_par, *span) != _paragraph_text(new, new_par, *new_span)
                  or _chapter_at(old_ch, span[0]) != _chapter_at(new_ch, new_span[0])):
                changed.append("%s %s: its passage or chapter changed" % (h["id"], a["id"]))
                reasons.append("changed passage")
        if reasons and h["status"] == "accepted":
            _reopen(h)
    header = dict(header, snapshot_path=os.path.relpath(new_path, os.path.dirname(os.path.abspath(map_path))))
    _write(new_path, new)
    _write(map_path, render_map(header, headings))
    lines = ["book-index resnapshot: map now points at %s (the old snapshot stays)" % new_name]
    lines += ["  broken quote (update it, then re-accept): %s" % b for b in broken]
    lines += ["  re-review (passage changed): %s" % c for c in changed]
    if not (broken or changed):
        lines.append("  every anchor held; no heading re-opened")
    return 0, lines


# ---------------------------------------------------------------- self-test

def run_self_test():
    import shutil
    import tempfile

    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    snap = am.normalize_snapshot(
        "Front matter line.\n\n"
        "# Chapter One: Judgment\n\n"
        "Reflective judgment must find the universal for a given particular. "
        "It returns to reflective judgment as the faculty of the spectator.\n\n"
        "Kant never wrote the political philosophy he promised.\n\n"
        "# Chapter Two: The Spectator\n\n"
        "The spectator sees the whole, which is why the spectator, not the actor, judges.\n\n"
        "Arendt read Kant this way. A quote with --> inside it.\n")

    def anc(aid, quote, role="substantive", end_quote=None, **extra):
        return dict({"id": aid, "quote": quote, "role": role, "end_quote": end_quote}, **extra)

    def head(hid, anchors=(), subs=(), see=(), see_also=(), status="proposed", **extra):
        h = {"schema": HEADING_SCHEMA, "id": hid, "heading": "heading " + hid, "kind": "concept",
             "variants": [], "status": status, "weight": 0.5, "anchors": list(anchors),
             "subheadings": list(subs), "see": list(see), "see_also": list(see_also)}
        h.update(extra)
        if status == "accepted":
            h["accepted_hash"] = accepted_hash(h)
        return h

    header = {"schema": MAP_SCHEMA, "snapshot_path": "S_Manuscript_Snapshot_r1.md", "chapter_level": 1}
    judgment = head("IX-001", [anc("IX-001.a1", "must find the universal for a given particular")],
                    see_also=["IX-002"])
    spectator = head("IX-002", [anc("IX-002.a1", "The spectator sees the whole")], see_also=["IX-001"])

    def codes(headings, snapshot=snap, hdr=header):
        errors, warns, _n, _s = check(hdr, headings, snapshot)
        return [m.split(":")[0] for _h, m in errors], [m.split(":")[0] for _h, m in warns]

    e, w = codes([judgment, spectator])
    chk("fresh_proposed_map_with_see_also_clean", e == [] and w == [])

    twice = head("IX-003", [anc("IX-003.a1", "the spectator")])
    chk("i2_quote_twice", "I2 provenance" in codes([judgment, spectator, twice])[0])
    gone = head("IX-003", [anc("IX-003.a1", "not in the book at all")])
    chk("i2_quote_missing", "I2 provenance" in codes([judgment, spectator, gone])[0])
    chk("i2_missing_snapshot", "I2 provenance" in codes([judgment, spectator], snapshot=None)[0])
    backwards = head("IX-003", [anc("IX-003.a1", "Kant never wrote", end_quote="Reflective judgment must")])
    chk("i2_end_quote_before_quote", "I2 provenance" in codes([judgment, spectator, backwards])[0])
    ranged = head("IX-003", [anc("IX-003.a1", "Kant never wrote", end_quote="which is why the spectator")])
    chk("i2_range_ok", codes([judgment, spectator, ranged])[0] == [])
    ctx = head("IX-003", [anc("IX-003.a1", "the spectator",
                              context={"before": "which is why ", "after": ", not the actor"})])
    chk("i2_context_disambiguates", codes([judgment, spectator, ctx])[0] == [])

    a = head("IX-010", see=["IX-011"])
    b = head("IX-011", see=["IX-010"])
    chk("i3_circular_see", "I3 cross-references" in codes([judgment, spectator, a, b])[0])
    dropped = head("IX-012", status="dropped")
    to_dropped = head("IX-003", [anc("IX-003.a1", "Kant never wrote")], see_also=["IX-012"])
    chk("i3_see_also_to_dropped", "I3 cross-references" in codes([judgment, spectator, dropped, to_dropped])[0])
    see_only = head("IX-013", see=["IX-001"])
    to_see_only = head("IX-003", [anc("IX-003.a1", "Kant never wrote")], see_also=["IX-013"])
    chk("i3_see_also_to_see_only", "I3 cross-references" in codes([judgment, spectator, see_only, to_see_only])[0])
    chk("see_only_heading_valid", codes([judgment, spectator, see_only])[0] == [])
    bad_see_only = head("IX-013", see=["IX-001"], see_also=["IX-002"])
    chk("i1_see_only_with_see_also", "I1 schema" in codes([judgment, spectator, bad_see_only])[0])

    subbed = head("IX-004", subs=[
        {"id": "IX-004.s1", "label": "and the spectator",
         "anchors": [anc("IX-004.s1.a1", "the faculty of the spectator")]},
        {"id": "IX-004.s2", "label": "Kant on",
         "anchors": [anc("IX-004.s2.a1", "Kant never wrote"),
                     anc("IX-004.s2.a2", "he promised", role="passing")]}], status="accepted")
    chk("only_subheading_anchors_valid", codes([judgment, spectator, subbed])[0] == [])
    flipped = copy.deepcopy(subbed)
    flipped["subheadings"][1]["anchors"][1]["role"] = "substantive"
    chk("i4_role_flip_after_accept", "I4 acceptance" in codes([judgment, spectator, flipped])[0])
    bad_id = copy.deepcopy(subbed)
    bad_id["subheadings"][0]["anchors"][0]["id"] = "IX-004.s2.a1"
    bad_id["accepted_hash"] = accepted_hash(bad_id)
    chk("i1_malformed_nested_anchor_id", "I1 schema" in codes([judgment, spectator, bad_id])[0])
    lone = head("IX-005", subs=[{"id": "IX-005.s1", "label": "alone",
                                 "anchors": [anc("IX-005.s1.a1", "Arendt read Kant")]}])
    chk("w3_lone_subheading", "W3 subheadings" in codes([judgment, spectator, lone])[1])
    unknown = head("IX-006", [anc("IX-006.a1", "Kant never wrote", note="x")])
    chk("i1_unknown_nested_key", "I1 schema" in codes([judgment, spectator, unknown])[0])
    chk("i1_unknown_top_key", "I1 schema" in codes([judgment, spectator, dict(spectator, colour="x")])[0])
    accepted_no_hash = dict(judgment, status="accepted")
    chk("i1_accepted_needs_hash", "I1 schema" in codes([accepted_no_hash, spectator])[0])
    chk("w1_uncovered_chapter", "W1 coverage" in codes([judgment])[1])

    d = tempfile.mkdtemp()
    try:
        src = os.path.join(d, "book.md")
        _write(src, snap.replace("\n", "\r\n"))
        arrow = head("IX-007", [anc("IX-007.a1", "A quote with --> inside it.")])
        props = os.path.join(d, "proposals.json")
        _write(props, json.dumps([judgment, spectator, arrow, subbed]))
        run_dir = os.path.join(d, "run")
        code, _l = init(src, run_dir, "S", "r1", props)
        map_path = os.path.join(run_dir, "S_Index_Map_r1.md")
        chk("init_writes_map_and_snapshot", code == 0 and os.path.isfile(map_path))
        chk("init_forces_proposed", "accepted" not in [h["status"] for h in parse_map(_read(map_path))[1]])
        quotes = [a["quote"] for h in parse_map(_read(map_path))[1] for a in h["anchors"]]
        chk("quote_with_arrow_round_trips", "with -->" not in _read(map_path)
            and "A quote with --> inside it." in quotes and run(run_dir)[0] == 0)
        chk("init_never_overwrites", init(src, run_dir, "S", "r1", props)[0] == 1)
        chk("run_folder_resolution", run(run_dir)[0] == 0 and run(map_path)[0] == 0)
        chk("missing_map_usage", run(os.path.join(d, "nope"))[0] == 2)

        chk("accept_records_hash", accept(map_path, ["IX-001", "IX-004"])[0] == 0
            and run(map_path, strict=True)[0] == 0)
        chk("review_lists_anchor_in_context", "**must find the universal for a given particular**"
            in "\n".join(review(map_path)[1]))

        code, lines = merge(map_path, "IX-002", "IX-001")
        _h, merged, _e = parse_map(_read(map_path))
        by = {h["id"]: h for h in merged}
        chk("merge_result_passes_i1_to_i3", code == 0 and run(map_path)[0] == 0)
        chk("merge_empties_and_drops_source",
            by["IX-002"]["status"] == "dropped" and by["IX-002"]["anchors"] == []
            and by["IX-002"]["see_also"] == [] and "accepted_hash" not in by["IX-002"])
        chk("merge_moves_anchors_and_variants",
            [a["id"] for a in by["IX-001"]["anchors"]] == ["IX-001.a1", "IX-001.a2"]
            and "heading IX-002" in by["IX-001"]["variants"] and by["IX-001"]["see_also"] == []
            and by["IX-001"]["status"] == "proposed")

        _h, cur, _e = parse_map(_read(map_path))
        same = [h for h in cur if h["id"] == "IX-004"]
        promoted = copy.deepcopy(same)
        promoted[0]["subheadings"][1]["anchors"][1]["role"] = "substantive"
        _write(props, json.dumps(same))
        kept = update(map_path, props)[0] == 0 and parse_map(_read(map_path))[1][3]["status"] == "accepted"
        _write(props, json.dumps(promoted))
        update(map_path, props)
        chk("update_keeps_unchanged_reopens_changed",
            kept and parse_map(_read(map_path))[1][3]["status"] == "proposed")
        accept(map_path, ["IX-001", "IX-004", "IX-007"])
        edited = os.path.join(d, "book2.md")
        _write(edited, snap.replace("Front matter line.", "Front matter, revised.")
               .replace("Arendt read Kant this way.", "Arendt read Kant differently."))
        code, lines = resnapshot(map_path, edited, "r2")
        _h, after, _e = parse_map(_read(map_path))
        by = {h["id"]: h for h in after}
        chk("resnapshot_offset_shift_keeps_acceptance", code == 0 and by["IX-001"]["status"] == "accepted")
        chk("resnapshot_changed_paragraph_reopens", by["IX-007"]["status"] == "proposed")
        chk("resnapshot_points_at_new_snapshot", _h["snapshot_path"] == "S_Manuscript_Snapshot_r2.md"
            and os.path.isfile(os.path.join(run_dir, "S_Manuscript_Snapshot_r1.md")))

        range_map = os.path.join(run_dir, "S_Index_Map_r3.md")
        _write(range_map, render_map(dict(header, snapshot_path="S_Manuscript_Snapshot_r2.md"),
                                     [head("IX-001", [anc("IX-001.a1", "Kant never wrote",
                                                          end_quote="which is why the spectator")],
                                           status="accepted")]))
        interior = os.path.join(d, "book3.md")
        _write(interior, _read(os.path.join(run_dir, "S_Manuscript_Snapshot_r2.md"))
               .replace("# Chapter Two: The Spectator\n\n", "# Chapter Two: The Spectator\n\nA new paragraph.\n\n"))
        resnapshot(range_map, interior, "r4")
        chk("resnapshot_range_interior_change_reopens",
            parse_map(_read(range_map))[1][0]["status"] == "proposed")

        # Writer safety (Codex review 1): a heading the hash or the writer cannot encode is refused
        # and the map is untouched; a change that breaks a live link from another heading is refused.
        before = _read(map_path)
        _write(props, json.dumps([head("IX-020", [anc("IX-020.a1", "Kant never wrote")], heading="\ud800")]))
        chk("unencodable_update_refused_map_unchanged", update(map_path, props)[0] == 1 and _read(map_path) == before)
        _h, cur, _e = parse_map(before)
        target = next(h for h in cur if h["id"] == "IX-004")
        referrer = next(h for h in cur if h["id"] == "IX-001")
        referrer["see_also"] = ["IX-004"]
        _write(props, json.dumps([referrer]))
        update(map_path, props)
        accept(map_path, ["IX-001"])
        before = _read(map_path)
        _write(props, json.dumps([dict(target, anchors=[], subheadings=[], see=["IX-007"], see_also=[])]))
        chk("update_breaking_a_referrer_refused", update(map_path, props)[0] == 1 and _read(map_path) == before)
        chk("drop_breaking_a_referrer_refused", drop(map_path, ["IX-004"])[0] == 1 and _read(map_path) == before)

        dup = head("IX-030", [anc("IX-030.a1", "Kant never wrote"), anc("IX-030.a1", "Arendt read Kant")])
        chk("i1_duplicate_anchor_id", "I1 schema" in codes([judgment, spectator, dup])[0])
        _write(map_path, before + "\n<!-- apodictic:index_heading\nnull\n-->\n")
        chk("i1_null_heading_block", run(map_path)[0] == 1)
        _write(map_path, before.replace('"status": "accepted"', '"status": []', 1))
        chk("i1_malformed_status_no_crash", run(map_path)[0] == 1)
        _write(map_path, before)
        _write(props, json.dumps([{"id": []}]))
        chk("update_malformed_id_refused", update(map_path, props)[0] == 1)

        sub_dir = os.path.join(d, "nested")
        os.makedirs(os.path.join(sub_dir, "snaps"))
        _write(os.path.join(sub_dir, "snaps", "S_Manuscript_Snapshot_r1.md"), snap)
        nested_map = os.path.join(sub_dir, "S_Index_Map_r1.md")
        _write(nested_map, render_map(dict(header, snapshot_path="snaps/S_Manuscript_Snapshot_r1.md"),
                                      [judgment, spectator]))
        resnapshot(nested_map, src, "r2")
        chk("resnapshot_keeps_snapshot_directory", run(nested_map)[0] == 0)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


# ---------------------------------------------------------------- CLI

def _usage():
    print("Usage:")
    for line in __doc__.splitlines():
        if line.startswith("  book_index.py "):
            print(line)
    return 2


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = argv[1:]
    if not args:
        return _usage()
    cmd, rest = args[0], args[1:]
    flags = [a for a in rest if a.startswith("--")]
    pos = [a for a in rest if not a.startswith("--")]
    if cmd == "book-index" and len(pos) == 1 and set(flags) <= {"--strict"}:
        code, lines = run(pos[0], strict="--strict" in flags)
    elif cmd == "init" and len(rest) in (5, 7):
        level = 1
        if len(rest) == 7:
            if rest[5] != "--chapter-level" or not rest[6].isdigit():
                return _usage()
            level = int(rest[6])
        code, lines = init(*rest[:5], chapter_level=level)
    elif cmd == "update" and len(rest) == 2:
        code, lines = update(*rest)
    elif cmd == "review" and len(rest) == 1:
        code, lines = review(rest[0])
    elif cmd == "accept" and len(rest) == 3 and rest[1] == "--kind" and rest[2] in _KINDS:
        code, lines = accept(rest[0], kind=rest[2])
    elif cmd == "accept" and len(pos) >= 2 and not flags:
        code, lines = accept(pos[0], pos[1:])
    elif cmd == "drop" and len(pos) >= 2 and not flags:
        code, lines = drop(pos[0], pos[1:])
    elif cmd == "rename" and len(rest) == 3:
        code, lines = rename(*rest)
    elif cmd == "merge" and len(rest) == 3:
        code, lines = merge(*rest)
    elif cmd == "resnapshot" and len(rest) == 3:
        code, lines = resnapshot(*rest)
    else:
        return _usage()
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
