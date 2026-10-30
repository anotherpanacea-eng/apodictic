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

Phase B (Increment 2). `locate` and `format` are the only writers of the finished index.
  locate      resolve each substantive anchor of each published (accepted, I1-I4 clean) heading to a
              locator under a scheme, or to the unresolved list with a reason: `paragraph` (chapter.
              paragraph, from the snapshot) or `page` (printed folios from the proof PDF, by folded
              quote match, with the order check). Writes `[Project]_Index_Locators_[runlabel].json`.
  format      write the index (.txt or .docx) under a style (indented or run-in, word- or
              letter-by-letter, Chicago or full ranges, See also at the end or after the heading),
              or with no locators file the locator-free topic map, plus a report of everything left
              out and, with --max-lines, the lowest-weight cut candidates.

  book_index.py book-index <run_folder|index_map.md> [--strict]
  book_index.py init <source_text> <run_folder> <project> <runlabel> <proposals.json> [--chapter-level N]
  book_index.py update <index_map.md> <proposals.json>
  book_index.py review <index_map.md>
  book_index.py accept <index_map.md> (<IX-id>... | --kind <kind>)
  book_index.py drop <index_map.md> <IX-id>...
  book_index.py rename <index_map.md> <IX-id> <new heading>
  book_index.py merge <index_map.md> <source IX-id> <target IX-id>
  book_index.py resnapshot <index_map.md> <new_source_text> <runlabel>
  book_index.py locate <index_map.md> --scheme paragraph|page [--pdf <proof.pdf> --body-end N]
                [--folio-start N] [--include-front] [--include-back]
  book_index.py format <index_map.md> [--locators <file.json>] [--layout indented|run-in]
                [--sort word|letter] [--ranges chicago|full] [--see-also end|after-heading] [--docx]
                [--max-lines N]
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
import unicodedata

import annotation_export as ax
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


def _links(h):
    """The string ids a heading's See and See also lists name (malformed entries are I1's job)."""
    return {t for f in ("see", "see_also") if isinstance(h.get(f), list) for t in h[f] if isinstance(t, str)}


def _save(map_path, header, headings, ids=None):
    """Validate the would-be map in memory and write it only if I1-I3 hold for `ids` and for every
    heading that links to one of them (or for all headings when `ids` is None)."""
    if ids is not None:
        ids = set(ids) | {h.get("id") for h in headings if isinstance(h, dict) and ids & _links(h)}
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
        try:
            unchanged = old is not None and old.get("status") == "accepted" and old["accepted_hash"] == accepted_hash(new)
        except UnicodeEncodeError:
            unchanged = False  # I1 refuses it below
        if unchanged:
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


# ---------------------------------------------------------------- Phase B: locators

_DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−"), "-")
_QUOTES = {ord(c): "'" for c in "‘’‚‛′"}
_QUOTES.update({ord(c): '"' for c in "“”„‟″"})
_MD_DROP_RE = re.compile(r"\[\^[^\]\s]*\]|\]\([^)\s]*\)|[*_`\[]|[\u00b9\u00b2\u00b3\u2070-\u2079]+")


def fold(text):
    """-> (folded, origins): the Phase B match form of `text` and, per folded character, the index of
    the raw character it came from. Inline markdown and footnote markers are dropped; dashes, quote
    styles, ligatures (NFKC), line-break hyphenation and whitespace are folded; case is folded."""
    drop = [False] * len(text)
    for m in _MD_DROP_RE.finditer(text):
        for i in range(m.start(), m.end()):
            drop[i] = True
    out, origins = [], []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if drop[i] or c == "­":
            i += 1
            continue
        if c in "-‐" and out and out[-1].isalpha():
            j = i + 1
            while j < n and text[j] in " \t":
                j += 1
            if j < n and text[j] == "\n":
                k = j + 1
                while k < n and text[k].isspace():
                    k += 1
                if k < n and text[k].isalpha():  # "peo-\nple" joins
                    i = k
                    continue
        if c.isspace():
            if out and out[-1] != " ":
                out.append(" ")
                origins.append(i)
            i += 1
            continue
        for ch in unicodedata.normalize("NFKC", c).translate(_DASHES).translate(_QUOTES).lower():
            if ch == "-" and out and out[-1] == "-":
                continue  # "--" is one dash
            out.append(ch)
            origins.append(i)
        i += 1
    return "".join(out), origins


def _fold_key(text):
    return fold(text)[0].strip()


def order_verdicts(positions):
    """`positions`: proof positions of distinct snapshot spans, in snapshot order. -> one verdict per
    span: "kept" when the span is in every longest non-decreasing subsequence, "ambiguous_order" when
    it is in some, "out_of_order" when it is in none."""
    n = len(positions)
    f, g = [1] * n, [1] * n
    for i in range(n):
        for j in range(i):
            if positions[j] <= positions[i]:
                f[i] = max(f[i], f[j] + 1)
    for i in reversed(range(n)):
        for j in range(i + 1, n):
            if positions[i] <= positions[j]:
                g[i] = max(g[i], g[j] + 1)
    best = max(f, default=0)
    on_some = [f[i] + g[i] - 1 == best for i in range(n)]
    per_level = {}
    for i in range(n):
        if on_some[i]:
            per_level[f[i]] = per_level.get(f[i], 0) + 1
    return ["out_of_order" if not on_some[i] else "kept" if per_level[f[i]] == 1 else "ambiguous_order"
            for i in range(n)]


def _paragraph_index(snapshot, level):
    """[(start, end, chapter_no, paragraph_no)] for body paragraphs, chapters numbered from 1. ATX
    heading lines and front matter are excluded; body text after a heading counts whether or not a
    blank line separates them."""
    chaps = chapters(snapshot, level)
    segments = []
    for s, e in _paragraph_spans(snapshot):
        run_start, pos = None, s
        for line in snapshot[s:e].splitlines(keepends=True):
            if re.match(r"\s*#{1,6}\s", line):
                if run_start is not None:
                    segments.append((run_start, pos))
                run_start = None
            elif run_start is None and line.strip():
                run_start = pos
            pos += len(line)
        if run_start is not None:
            segments.append((run_start, e))
    out = []
    for ch_no, (_label, cstart, cend) in enumerate(chaps, start=1):
        para = 0
        for s, e in segments:
            if cstart <= s < cend and snapshot[s:e].strip():
                para += 1
                out.append((s, e, ch_no, para))
    return out


def _paragraph_locators(snapshot, level, placements):
    """Paragraph scheme: each placement {anchor, span} -> locator or unresolved reason."""
    index = _paragraph_index(snapshot, level)
    if not index:
        return None, "no chapter headings at level %s: the paragraph scheme needs chapters" % level
    starts = [s for s, _e, _c, _p in index]

    def at(pos):
        i = bisect.bisect_right(starts, pos) - 1
        if i >= 0 and index[i][0] <= pos < index[i][1]:
            return index[i][2], index[i][3]
        return None

    out = []
    for p in placements:
        s, e = p["span"]
        a, b = at(s), at(max(e - 1, s))
        if a is None or b is None:
            out.append(dict(p, reason="outside_body_paragraphs"))
        else:
            out.append(dict(p, start={"label": "%d.%d" % a, "sort": list(a)},
                            end={"label": "%d.%d" % b, "sort": list(b)} if b != a else None))
    return out, None


def _load_pypdf():
    try:
        import pypdf
    except ImportError:
        return None
    return pypdf


def _proof_pages(pdf_path, folio_start, body_end, include_front, include_back):
    """-> (pages, None) with pages [{label, text, body}] or (None, reason)."""
    pypdf = _load_pypdf()
    if pypdf is None:
        return None, "the page scheme needs pypdf (pip install pypdf)"
    try:
        reader = pypdf.PdfReader(pdf_path)
        texts = [page.extract_text() or "" for page in reader.pages]
        has_labels = "/PageLabels" in reader.trailer["/Root"]
        pdf_labels = list(reader.page_labels) if has_labels else None
    except Exception as exc:  # pypdf raises many types on damaged files
        return None, "cannot read the proof PDF: %s" % exc
    if not any(t.strip() for t in texts):
        return None, "the proof has no extractable text (a scanned image?)"
    if folio_start is not None and folio_start < 1:
        return None, "--folio-start is a 1-based PDF page number"
    if pdf_labels is None and folio_start is None:
        return None, ("the proof has no page labels: give --folio-start <PDF page that is folio 1> "
                      "(this tool never guesses folios)")
    if body_end is None:
        return None, ("give --body-end <last PDF page of the body text>: notes and other back matter can "
                      "repeat body sentences, so the body's end is the author's to state")
    if include_front and pdf_labels is None:
        return None, ("--include-front needs the PDF's own page labels: front-matter folios are never "
                      "inferred from --folio-start")
    pages = []
    for i, text in enumerate(texts):
        if pdf_labels is not None:
            label = pdf_labels[i]
            arabic = label.isdigit()
        else:
            arabic = i + 1 >= folio_start
            label = str(i + 2 - folio_start) if arabic else None
        back = i + 1 > body_end
        body = (arabic and not back) or (include_front and not arabic and not back) or (include_back and back)
        pages.append({"label": label, "text": text, "body": body})
    if not any(p["body"] for p in pages):
        return None, "no body pages to search: check --folio-start and --body-end against the proof"
    return pages, None


def _strip_running_heads(pages):
    """Drop a body page's first and last line when, digits masked, it repeats on at least five pages."""
    def mask(line):
        return re.sub(r"\d+", "#", line.strip())

    split = [[ln for ln in p["text"].split("\n") if ln.strip()] for p in pages]
    counts = {}
    for p, lines in zip(pages, split):
        if p["body"] and lines:
            for ln in {mask(lines[0]), mask(lines[-1])}:
                counts[ln] = counts.get(ln, 0) + 1
    out = []
    for p, lines in zip(pages, split):
        if p["body"]:
            if lines and counts.get(mask(lines[0]), 0) >= 5:
                lines = lines[1:]
            if lines and counts.get(mask(lines[-1]), 0) >= 5:
                lines = lines[:-1]
        out.append("\n".join(lines))
    return out


def _page_locators(pdf_path, placements, folio_start=None, body_end=None, include_front=False,
                   include_back=False):
    """Page scheme: find each anchor's folded quote in the folded body text of the proof, assign folios,
    then run the order check over distinct snapshot spans."""
    pages, why = _proof_pages(pdf_path, folio_start, body_end, include_front, include_back)
    if pages is None:
        return None, why
    texts = _strip_running_heads(pages)
    raw, page_at = [], []
    for p, text in zip(pages, texts):
        if p["body"]:
            raw.append(text)
            page_at.extend([p["label"]] * (len(text) + 1))
    raw_text = "\n".join(raw)
    proof, origins = fold(raw_text)

    def label_at(folded_index):
        return page_at[origins[folded_index]]

    found = []
    for p in placements:
        a = p["anchor"]
        ctx = a.get("context") or {}
        key = _fold_key(ctx.get("before", "") + a["quote"] + ctx.get("after", ""))
        n = proof.count(key)
        if n != 1:
            found.append(dict(p, reason="not_found" if n == 0 else "ambiguous_match", positions=[]))
            continue
        q0 = proof.find(key) + len(fold(ctx.get("before", ""))[0].lstrip())
        q_end = q0 + len(_fold_key(a["quote"]))
        end_pos = None
        if a.get("end_quote") is not None:
            ekey = _fold_key(a["end_quote"])
            after = proof.count(ekey, q_end)
            if after == 1:
                end_pos = proof.find(ekey, q_end) + len(ekey) - 1
            else:
                before = 0 <= proof.find(ekey) < q0
                reason = ("end_quote_ambiguous" if after > 1 else
                          "end_quote_before_start" if before else "end_quote_not_found")
                found.append(dict(p, reason=reason, positions=[q0]))
                continue
        found.append(dict(p, proof_pos=q0, proof_end=end_pos))

    placed = [p for p in found if "proof_pos" in p]
    spans = sorted({tuple(p["span"]) for p in placed})
    pos_of = {}
    for p in placed:
        pos_of.setdefault(tuple(p["span"]), p["proof_pos"])
    verdict = dict(zip(spans, order_verdicts([pos_of[s] for s in spans])))
    out = []
    for p in found:
        if "proof_pos" not in p:
            out.append(p)
            continue
        v = verdict[tuple(p["span"])]
        if v != "kept":
            out.append(dict(p, reason=v, positions=[p["proof_pos"]]))
            continue
        start = label_at(p["proof_pos"])
        end = label_at(p["proof_end"]) if p["proof_end"] is not None else None
        sort = [p["proof_pos"]]
        out.append(dict(p, start={"label": start, "sort": sort},
                        end={"label": end, "sort": [p["proof_end"]]} if end not in (None, start) else None))
    return out, None


def _published(header, headings, snapshot):
    """Headings that may reach an index: accepted, with no validator error of their own (so I1-I4 hold)."""
    errors, _w, _n, spans = check(header, headings, snapshot)
    if any(hid is None for hid, _m in errors):
        return None, spans, [m for hid, m in errors if hid is None]
    bad = {hid for hid, _m in errors}
    return [h for h in headings if isinstance(h, dict) and h.get("status") == "accepted"
            and h.get("id") not in bad], spans, []


def _side_path(map_path, kind, ext):
    m = re.match(r"^(.+)_Index_Map_(.+)\.md$", os.path.basename(map_path))
    stem = "%s_%s_%s" % (m.group(1), kind, m.group(2)) if m else "Index_" + kind
    return os.path.join(os.path.dirname(os.path.abspath(map_path)), stem + ext)


def locate_index(map_path, scheme, pdf=None, folio_start=None, body_end=None, include_front=False,
                 include_back=False):
    """Resolve every substantive anchor of every published heading to a locator under `scheme`, or to
    the unresolved list with a reason. Writes `[Project]_Index_Locators_[runlabel].json`."""
    text, header, headings, parse_errs, snapshot = load(map_path)
    if text is None or header is None or parse_errs or snapshot is None:
        return 1, ["book-index locate: the map or its snapshot cannot be read; run the validator"]
    published, spans, errs = _published(header, headings, snapshot)
    if published is None:
        return 1, ["book-index locate: refused; the map has errors:"] + ["  ERROR: %s" % e for e in errs]
    placements = []
    for h in published:
        for owner, a in _all_anchors(h):
            if a["role"] == "substantive":
                placements.append({"heading": h["id"], "owner": owner, "anchor": a, "span": spans[a["id"]]})
    if scheme == "paragraph":
        results, why = _paragraph_locators(snapshot, header.get("chapter_level", 1), placements)
    elif scheme == "page":
        if not pdf:
            return 2, ["book-index locate: the page scheme needs --pdf <proof.pdf>"]
        results, why = _page_locators(pdf, placements, folio_start, body_end, include_front, include_back)
    else:
        return 2, ["book-index locate: scheme must be paragraph or page (line, ebook and embedded are "
                   "Increment 3)"]
    if results is None:
        return 1, ["book-index locate: refused: %s" % why]
    record = {
        "schema": "book-index locators (Increment 2)", "scheme": scheme,
        "map": os.path.basename(map_path), "snapshot_sha256": hashlib.sha256(snapshot.encode("utf-8")).hexdigest(),
        "chapter_level": header.get("chapter_level", 1),
        "pdf_sha256": hashlib.sha256(open(pdf, "rb").read()).hexdigest() if pdf else None,
        "accepted": {h["id"]: h["accepted_hash"] for h in published},
        "placed": [{"anchor": r["anchor"]["id"], "heading": r["heading"], "owner": r["owner"],
                    "start": r["start"], "end": r["end"]} for r in results if "start" in r],
        "unresolved": [{"anchor": r["anchor"]["id"], "heading": r["heading"], "reason": r["reason"],
                        "positions": r.get("positions", [])} for r in results if "reason" in r],
    }
    out = _side_path(map_path, "Index_Locators", ".json")
    _write(out, json.dumps(record, indent=1, ensure_ascii=False) + "\n")
    return 0, ["book-index locate (%s): %d placed, %d unresolved -> %s"
               % (scheme, len(record["placed"]), len(record["unresolved"]), os.path.basename(out))]


# ---------------------------------------------------------------- Phase B: the formatted index

def _sort_key(text, letter_by_letter):
    t = unicodedata.normalize("NFKD", text).casefold()
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^\w\s]", "", t).strip()
    return re.sub(r"\s+", "" if letter_by_letter else " ", t)


def _chicago_range(a, b):
    """Chicago inclusive-number style for arabic folios (45-52, 101-8, 321-28, 1496-1500)."""
    if not (a.isdigit() and b.isdigit()) or int(a) < 100 or int(a) % 100 == 0 or len(a) != len(b):
        return "%s–%s" % (a, b)
    keep = 1 if int(a) % 100 < 10 else 2
    i = 0
    while i < len(a) - keep and a[i] == b[i]:
        i += 1
    if len(a) == 4 and len(a) - i == 3:
        i = 0  # three of four digits change: give them all (1496-1500)
    return "%s–%s" % (a, b[i:])


def _locator_text(loc, ranges):
    start, end = loc["start"]["label"], (loc["end"] or {}).get("label")
    if not end:
        return start
    if ranges == "chicago":
        if "." in start and start.split(".")[0] == end.split(".")[0]:
            return "%s–%s" % (start, end.split(".", 1)[1])
        return _chicago_range(start, end)
    return "%s–%s" % (start, end)


def _merged(locs, ranges):
    seen, out = set(), []
    for loc in sorted(locs, key=lambda x: x["start"]["sort"]):
        t = _locator_text(loc, ranges)
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _locator_record_errors(rec, published):
    """Why a locators file can't be used with these published headings, or None."""
    if not isinstance(rec, dict):
        return "the locators file is not a JSON object"
    if not isinstance(rec.get("snapshot_sha256"), str) or not isinstance(rec.get("chapter_level"), int):
        return "the locators file lacks its snapshot hash or chapter level"
    if not isinstance(rec.get("accepted"), dict) or not all(isinstance(v, str) for v in rec["accepted"].values()):
        return "the locators file has no valid accepted-hash table"
    owners = {h["id"]: h["id"] for h in published}
    owners.update({s["id"]: h["id"] for h in published for s in h["subheadings"]})

    def loc_ok(x):
        return (isinstance(x, dict) and isinstance(x.get("label"), str) and isinstance(x.get("sort"), list)
                and all(type(v) is int for v in x["sort"]))

    for p in rec.get("placed") if isinstance(rec.get("placed"), list) else [None]:
        if not (isinstance(p, dict) and isinstance(p.get("owner"), str) and p["owner"] in owners
                and owners[p["owner"]] == p.get("heading") and loc_ok(p.get("start"))
                and "end" in p and (p["end"] is None or loc_ok(p["end"]))):
            return "a placed locator is malformed or names a heading that is not published: %r" % (p,)
    for u in rec.get("unresolved") if isinstance(rec.get("unresolved"), list) else [None]:
        if not (isinstance(u, dict) and all(isinstance(u.get(k), str) for k in ("anchor", "heading", "reason"))
                and isinstance(u.get("positions"), list)):
            return "an unresolved entry is malformed: %r" % (u,)
    return None


def format_index(map_path, locators=None, layout="indented", sort="word", ranges="chicago",
                 see_also="end", output="txt", max_lines=None):
    """Write the formatted index (or, with no locators file, the locator-free topic map) and a report of
    everything left out. Only published headings are printed."""
    text, header, headings, parse_errs, snapshot = load(map_path)
    if text is None or header is None or parse_errs or snapshot is None:
        return 1, ["book-index format: the map or its snapshot cannot be read; run the validator"]
    published, _spans, errs = _published(header, headings, snapshot)
    if published is None:
        return 1, ["book-index format: refused; the map has errors:"] + ["  ERROR: %s" % e for e in errs]
    by_id = {h["id"]: h for h in published}
    placed, unresolved = {}, []
    if locators:
        try:
            rec = json.loads(_read(locators) or "")
        except json.JSONDecodeError:
            rec = None
        why = _locator_record_errors(rec, published)
        if why:
            return 1, ["book-index format: refused: %s" % why]
        if (rec["snapshot_sha256"] != hashlib.sha256(snapshot.encode("utf-8")).hexdigest()
                or rec["chapter_level"] != header.get("chapter_level", 1)):
            return 1, ["book-index format: the locators were made against another snapshot or chapter level; "
                       "run locate again"]
        stale = sorted(hid for hid, hsh in rec["accepted"].items()
                       if hid not in by_id or by_id[hid]["accepted_hash"] != hsh)
        stale += sorted(hid for hid in by_id if hid not in rec["accepted"])
        if stale:
            return 1, ["book-index format: the locators are stale for %s; run locate again" % ", ".join(stale)]
        for p in rec["placed"]:
            placed.setdefault(p["owner"], []).append(p)
        unresolved = rec["unresolved"]
    # Which headings print: See-only headings point only at printable non-See-only headings (I3), so
    # one pass settles the others and a second settles the See-only ones.
    printable = {h["id"] for h in published if not h["see"] and (
        not locators or placed.get(h["id"]) or any(placed.get(s["id"]) for s in h["subheadings"]))}
    printable |= {h["id"] for h in published if h["see"] and any(t in printable for t in h["see"])}
    report, entries = [], []
    for h in published:
        own = _merged(placed.get(h["id"], []), ranges) if locators else []
        subs = []
        for s in h["subheadings"]:
            locs = _merged(placed.get(s["id"], []), ranges) if locators else []
            if locators and not locs:
                report.append("subheading %s (%s) left out: no placed locators" % (s["id"], s["label"]))
                continue
            subs.append((s["label"], locs))
        refs = {}
        for field in ("see", "see_also"):
            keep = []
            for t in h[field]:
                if t in printable:
                    keep.append(by_id[t]["heading"])
                else:
                    report.append("%s: %s %s dropped (target not printed)" % (h["id"], field, t))
            refs[field] = sorted(keep, key=lambda x: _sort_key(x, sort == "letter"))
        if h["see"] and not refs["see"]:
            report.append("heading %s (%s) left out: none of its See targets is printed" % (h["id"], h["heading"]))
            continue
        if locators and not h["see"] and not own and not subs:
            report.append("heading %s (%s) left out: no placed locators" % (h["id"], h["heading"]))
            continue
        subs.sort(key=lambda x: _sort_key(x[0], sort == "letter"))
        entries.append({"id": h["id"], "heading": h["heading"], "weight": h["weight"], "own": own,
                        "subs": subs, "see": refs["see"], "see_also": refs["see_also"]})
    entries.sort(key=lambda e: (_sort_key(e["heading"], sort == "letter"), e["heading"], e["id"]))

    def render(entry):
        """-> [(indent_level, text)] for one entry."""
        head = entry["heading"] + ("".join(", " + loc for loc in entry["own"]))
        if entry["see"]:
            return [(0, "%s. See %s" % (entry["heading"], "; ".join(entry["see"])))]
        also = "See also " + "; ".join(entry["see_also"]) if entry["see_also"] else None
        if layout == "run-in":
            parts = [head] + ["%s%s" % (lbl, "".join(", " + x for x in locs)) for lbl, locs in entry["subs"]]
            lead = ": " if not entry["own"] else "; "  # Chicago run-in: "heading: sub, 3" when no own locators
            line = head + lead + "; ".join(parts[1:]) if entry["subs"] else head
            if also and see_also == "after-heading" and entry["subs"]:
                line = "%s. %s; %s" % (head, also, "; ".join(parts[1:]))
            elif also:
                line += ". " + also
            return [(0, line)]
        lines = [(0, head + (". " + also if also and (see_also == "after-heading" or not entry["subs"]) else ""))]
        lines += [(1, "%s%s" % (lbl, "".join(", " + x for x in locs))) for lbl, locs in entry["subs"]]
        if also and see_also == "end" and entry["subs"]:
            lines.append((1, also))
        return lines

    blocks, letter = [], None
    for e in entries:
        first = (_sort_key(e["heading"], False)[:1] or "#").upper()
        if letter is not None and first != letter:
            blocks.append([(0, "")])
        letter = first
        blocks.append(render(e))
    lines = [ln for block in blocks for ln in block]
    cut = []
    if max_lines is not None and len(lines) > max_lines:
        over = len(lines) - max_lines
        for e in sorted(entries, key=lambda e: (e["weight"], e["id"])):
            if over <= 0:
                break
            cut.append("%s (%s, weight %.2f, %d line(s))" % (e["id"], e["heading"], e["weight"], len(render(e))))
            over -= len(render(e))
    kind = "Index" if locators else "Index_Topics"
    out = _side_path(map_path, kind, "." + output)
    if output == "docx":
        _write_bytes(out, _index_docx(lines))
    else:
        _write(out, "".join("    " * lvl + t + "\n" for lvl, t in lines))
    rep = ["# Index report", "", "Output: %s (%d lines, layout %s, sort %s-by-%s, ranges %s)"
           % (os.path.basename(out), len(lines), layout, sort, sort == "letter" and "letter" or "word", ranges), ""]
    if unresolved:
        rep += ["## Unresolved anchors (%d)" % len(unresolved), ""]
        rep += ["- %s (%s): %s%s" % (u["anchor"], u["heading"], u["reason"],
                                     " at proof position %s" % u["positions"] if u["positions"] else "")
                for u in unresolved]
        rep.append("")
    if report:
        rep += ["## Left out", ""] + ["- " + r for r in report] + [""]
    if max_lines is not None:
        rep += ["## Length allowance (%d lines)" % max_lines, ""]
        rep += (["Cut candidates, lowest weight first (none applied):", ""] + ["- " + c for c in cut]
                if cut else ["Within the allowance."]) + [""]
    _write(_side_path(map_path, kind + "_Report", ".md"), "\n".join(rep))
    return 0, ["book-index format: wrote %s and its report (%d entries, %d unresolved, %d left out%s)"
               % (os.path.basename(out), len(entries), len(unresolved), len(report),
                  ", %d cut candidate(s)" % len(cut) if cut else "")]


def _write_bytes(path, data):
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.replace(tmp, path)


_INDEX_DOCX_CT = (
    ax._XMLDECL +
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
    '</Types>')
_INDEX_DOCX_RELS = (
    ax._XMLDECL +
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
    '</Relationships>')


def _index_docx(lines):
    """The formatted index as a byte-stable .docx, through annotation_export's deterministic zip and
    OOXML parts: one paragraph per line, subentries indented, a hanging indent for turnover lines."""
    paras = "".join(
        '<w:p><w:pPr><w:ind w:left="%d" w:hanging="360"/></w:pPr>%s</w:p>'
        % (360 * (lvl + 1), '<w:r><w:t xml:space="preserve">%s</w:t></w:r>' % ax._html_escape(t) if t else "")
        for lvl, t in lines)
    document = '%s<w:document xmlns:w="%s"><w:body>%s</w:body></w:document>' % (ax._XMLDECL, ax._W_NS, paras)
    return ax._deterministic_zip([("[Content_Types].xml", _INDEX_DOCX_CT), ("_rels/.rels", ax._DOCX_ROOT_RELS),
                                  ("word/document.xml", document), ("word/styles.xml", ax._DOCX_STYLES),
                                  ("word/settings.xml", ax._DOCX_SETTINGS),
                                  ("word/_rels/document.xml.rels", _INDEX_DOCX_RELS)])


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

        accepted_one = next(h for h in parse_map(before)[1] if h["status"] == "accepted")
        for name, bad in (("see_null", dict(accepted_one, see=None)),
                          ("see_also_object", dict(accepted_one, see_also=[{}])),
                          ("accepted_unencodable", dict(accepted_one, heading="\ud800"))):
            _write(props, json.dumps([bad]))
            chk("update_refuses_" + name, update(map_path, props)[0] == 1 and _read(map_path) == before)

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

    _phase_b_self_test(chk, head, anc, header)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def _tiny_pdf(pages, labels=None):
    """A minimal text PDF for the page-scheme tests: each page is a list of lines (Helvetica, WinAnsi).
    `labels` is the body of a /PageLabels /Nums array, or None for a PDF without labels."""
    win = {"\u2018": "\\221", "\u2019": "\\222", "\u201c": "\\223", "\u201d": "\\224",
           "\u2013": "\\226", "\u2014": "\\227"}

    def esc(t):
        return "".join(win.get(c, c) for c in t.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)"))

    n = len(pages)
    objs = ["<< /Type /Catalog /Pages 2 0 R%s >>" % (" /PageLabels << /Nums [%s] >>" % labels if labels else ""),
            "<< /Type /Pages /Kids [%s] /Count %d >>" % (" ".join("%d 0 R" % (3 + 2 * i) for i in range(n)), n)]
    for i, lines in enumerate(pages):
        body = "BT /F1 11 Tf 72 720 Td 14 TL " + " ".join("(%s) Tj T*" % esc(ln) for ln in lines) + " ET"
        objs.append("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 %d 0 R >> >> "
                    "/Contents %d 0 R >>" % (3 + 2 * n, 4 + 2 * i))
        objs.append("<< /Length %d >>\nstream\n%s\nendstream" % (len(body.encode("latin-1")), body))
    objs.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    out, offs = b"%PDF-1.4\n", []
    for i, o in enumerate(objs):
        offs.append(len(out))
        out += ("%d 0 obj\n%s\nendobj\n" % (i + 1, o)).encode("latin-1")
    xref = len(out)
    out += ("xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)).encode()
    out += "".join("%010d 00000 n \n" % o for o in offs).encode()
    out += ("trailer << /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)).encode()
    return out


def _phase_b_self_test(chk, head, anc, header):
    import shutil
    import tempfile
    import zipfile

    # Folding and ordering, as pure functions.
    chk("fold_normalizes", _fold_key("*Its* \ufb01ne\u2014\u201cso\u201d[^12] it-\n  self") == 'its fine-"so" itself'
        and _fold_key("The policy[^12] held.") == _fold_key("The policy\u00b9\u00b2 held."))
    chk("order_abc_case", order_verdicts([20, 10, 30]) == ["ambiguous_order", "ambiguous_order", "kept"])
    chk("order_early_wrong_match", order_verdicts([10, 20, 5, 40]) == ["kept", "kept", "out_of_order", "kept"])
    chk("chicago_ranges", [_chicago_range(a, b) for a, b in (("45", "52"), ("101", "108"), ("321", "328"),
                                                               ("1496", "1500"), ("100", "104"), ("ix", "xi"))]
        == ["45\u201352", "101\u20138", "321\u201328", "1496\u20131500", "100\u2013104", "ix\u2013xi"])
    chk("word_vs_letter_sort", sorted(["Newark", "New York"], key=lambda t: _sort_key(t, False)) == ["New York", "Newark"]
        and sorted(["New York", "Newark"], key=lambda t: _sort_key(t, True)) == ["Newark", "New York"])

    para = ["Alpha passage opens the chapter here.", "Bravo passage follows it closely.",
            "Charlie passage comes third in the book.", "Delta passage runs long across a sentence break.",
            "Xray passage starts a range. Yankee passage ends the range.", "Golf start quote tail."]
    snap = am.normalize_snapshot("Front matter.\n\n# Chapter One\n\n" + "\n\n".join(para) + "\n")
    d = tempfile.mkdtemp()
    try:
        src = os.path.join(d, "book.md")
        _write(src, snap)
        heads = [head("IX-001", [anc("IX-001.a1", "Alpha passage opens")]),
                 head("IX-002", [anc("IX-002.a1", "Bravo passage follows")]),
                 head("IX-003", [anc("IX-003.a1", "Charlie passage comes"), anc("IX-003.a2", "third in the book")]),
                 head("IX-004", [anc("IX-004.a1", "across a sentence break")]),
                 head("IX-005", [anc("IX-005.a1", "Alpha passage opens")]),
                 head("IX-006", [anc("IX-006.a1", "Xray passage starts", end_quote="Yankee passage ends")]),
                 head("IX-007", [anc("IX-007.a1", "Delta passage runs")]),
                 head("IX-008", [anc("IX-008.a1", "Golf start", end_quote="tail",
                                     context={"before": "", "after": " quote tail"})])]
        props = os.path.join(d, "p.json")
        _write(props, json.dumps(heads))
        run_dir = os.path.join(d, "run")
        init(src, run_dir, "T", "r1", props)
        m = os.path.join(run_dir, "T_Index_Map_r1.md")
        accept(m, ["IX-001", "IX-002", "IX-003", "IX-004", "IX-005", "IX-006", "IX-008"])
        loc = os.path.join(run_dir, "T_Index_Locators_r1.json")

        code, _l = locate_index(m, "paragraph")
        rec = json.loads(_read(loc))
        chk("only_published_headings_located", code == 0 and {p["heading"] for p in rec["placed"]} == {
            "IX-001", "IX-002", "IX-003", "IX-004", "IX-005", "IX-006", "IX-008"})
        chk("every_anchor_placed_or_unresolved", len(rec["placed"]) + len(rec["unresolved"]) == 8)
        format_index(m, loc)
        out = _read(os.path.join(run_dir, "T_Index_r1.txt"))
        chk("duplicate_locators_merged", "heading IX-003, 1.3\n" in out)
        tampered = os.path.join(d, "tampered")
        shutil.copytree(run_dir, tampered)
        tm = os.path.join(tampered, "T_Index_Map_r1.md")
        _write(tm, _read(tm).replace('"heading IX-002"', '"heading IX-002, edited"'))
        locate_index(tm, "paragraph")
        chk("i4_failing_heading_not_located", "IX-002" not in {p["heading"] for p in json.loads(
            _read(os.path.join(tampered, "T_Index_Locators_r1.json")))["placed"]})
        chk("proposed_heading_not_printed", "IX-007" not in out)
        chk("paragraph_range", "heading IX-006, 1.5\n" in out)

        flat = os.path.join(d, "flat")
        os.makedirs(flat)
        _write(os.path.join(flat, "F_Manuscript_Snapshot_r1.md"), "No chapters. Alpha passage opens here.\n")
        fh = head("IX-001", [anc("IX-001.a1", "Alpha passage opens")], status="accepted")
        _write(os.path.join(flat, "F_Index_Map_r1.md"), render_map(dict(header, snapshot_path="F_Manuscript_Snapshot_r1.md"), [fh]))
        tight = os.path.join(d, "tight")
        os.makedirs(tight)
        _write(os.path.join(tight, "G_Manuscript_Snapshot_r1.md"), "# Chapter One\nAlpha passage.\n\nBravo passage.\n")
        gh = [head("IX-001", [anc("IX-001.a1", "Alpha passage.")], status="accepted"),
              head("IX-002", [anc("IX-002.a1", "Bravo passage.")], status="accepted")]
        _write(os.path.join(tight, "G_Index_Map_r1.md"), render_map(dict(header, snapshot_path="G_Manuscript_Snapshot_r1.md"), gh))
        locate_index(os.path.join(tight, "G_Index_Map_r1.md"), "paragraph")
        chk("paragraph_after_heading_without_blank_line", {p["anchor"]: p["start"]["label"] for p in json.loads(
            _read(os.path.join(tight, "G_Index_Locators_r1.json")))["placed"]} == {"IX-001.a1": "1.1", "IX-002.a1": "1.2"})
        chk("paragraph_refuses_without_chapters", locate_index(os.path.join(flat, "F_Index_Map_r1.md"), "paragraph")[0] == 1)

        if _load_pypdf() is None:
            print("  page_scheme_tests: SKIPPED (pypdf not installed)")
        else:
            rh, body = "THE TEST BOOK", [
                ["Bravo passage follows it closely."], ["Alpha passage opens the chapter here."],
                ["Charlie passage comes third in the book."], ["Delta passage runs long across a sen-"],
                ["tence break.", "Yankee passage ends the range."], ["Xray passage starts a range.", "Golf start quote tail."]]
            pages = [["Front matter."]] + [[rh] + lines + [str(i + 1)] for i, lines in enumerate(body)]
            pdf = os.path.join(d, "proof.pdf")
            with open(pdf, "wb") as fh_:
                fh_.write(_tiny_pdf(pages, labels="0 << /S /r >> 1 << /S /D >>"))
            chk("page_requires_body_end", locate_index(m, "page", pdf=pdf)[0] == 1)
            code, _l = locate_index(m, "page", pdf=pdf, body_end=7)
            rec = json.loads(_read(loc))
            why = {u["anchor"]: u["reason"] for u in rec["unresolved"]}
            got = {p["anchor"]: p["start"]["label"] for p in rec["placed"]}
            chk("page_abc_order_check", code == 0 and why.get("IX-001.a1") == why.get("IX-002.a1") == "ambiguous_order"
                and got.get("IX-003.a1") == "3")
            chk("page_abc_with_second_heading", why.get("IX-005.a1") == "ambiguous_order")
            chk("page_break_with_running_head", got.get("IX-004.a1") == "4")
            chk("page_end_quote_before_start", why.get("IX-006.a1") == "end_quote_before_start")
            chk("page_end_quote_searched_from_quote_end", got.get("IX-008.a1") == "6" and "IX-008.a1" not in why)
            unlabeled = os.path.join(d, "nolabels.pdf")
            with open(unlabeled, "wb") as fh_:
                fh_.write(_tiny_pdf(pages))
            chk("page_refuses_without_folios", locate_index(m, "page", pdf=unlabeled, body_end=7)[0] == 1)
            chk("page_front_matter_needs_pdf_labels",
                locate_index(m, "page", pdf=unlabeled, folio_start=2, body_end=7, include_front=True)[0] == 1)
            chk("page_folio_start_map", locate_index(m, "page", pdf=unlabeled, folio_start=2, body_end=7)[0] == 0
                and {p["anchor"]: p["start"]["label"] for p in json.loads(_read(loc))["placed"]}.get("IX-004.a1") == "4")

        locate_index(m, "paragraph")
        format_index(m, loc, output="docx")
        docx = os.path.join(run_dir, "T_Index_r1.docx")
        first = open(docx, "rb").read()
        format_index(m, loc, output="docx")
        with zipfile.ZipFile(docx) as z:
            xml = z.read("word/document.xml").decode("utf-8")
        chk("docx_deterministic_and_complete", first == open(docx, "rb").read() and "heading IX-003, 1.3" in xml)
        moved = os.path.join(d, "moved")
        shutil.copytree(run_dir, moved)
        mm = os.path.join(moved, "T_Index_Map_r1.md")
        edited = os.path.join(d, "edited.md")
        _write(edited, snap.replace("# Chapter One\n\n", "# Chapter One\n\nA new first paragraph.\n\n"))
        resnapshot(mm, edited, "r2")
        chk("format_refuses_locators_from_older_snapshot",
            format_index(mm, os.path.join(moved, "T_Index_Locators_r1.json"))[0] == 1)
        good = json.loads(_read(loc))
        one = good["placed"][0]
        no_end = {k: v for k, v in one.items() if k != "end"}
        for bad in ("[]", "null", '{"accepted": []}', json.dumps(dict(good, placed=[{"owner": "IX-001"}])),
                    json.dumps(dict(good, placed=[dict(one, owner=[])])), json.dumps(dict(good, placed=[no_end])),
                    json.dumps(dict(good, placed=[dict(one, start={"label": "1", "sort": ["x"]})]))):
            _write(os.path.join(d, "bad.json"), bad)
            chk("format_refuses_malformed_locators %s" % bad[:16], format_index(m, os.path.join(d, "bad.json"))[0] == 1)
        rename(m, "IX-003", "renamed heading")
        accept(m, ["IX-003"])
        chk("format_refuses_stale_locators", format_index(m, loc)[0] == 1)

        # References are checked against what prints: a heading whose only anchor is unresolved drops
        # out, and so do the See and See also references to it.
        refs_dir = os.path.join(d, "refs")
        os.makedirs(refs_dir)
        _write(os.path.join(refs_dir, "R_Manuscript_Snapshot_r1.md"), snap)
        rh_ = [head("IX-001", [anc("IX-001.a1", "Front matter.")], status="accepted"),
               head("IX-002", see=["IX-001"], status="accepted"),
               head("IX-003", [anc("IX-003.a1", "Bravo passage follows")], see_also=["IX-001"], status="accepted")]
        rmap = os.path.join(refs_dir, "R_Index_Map_r1.md")
        _write(rmap, render_map(dict(header, snapshot_path="R_Manuscript_Snapshot_r1.md"), rh_))
        locate_index(rmap, "paragraph")
        format_index(rmap, os.path.join(refs_dir, "R_Index_Locators_r1.json"))
        printed = _read(os.path.join(refs_dir, "R_Index_r1.txt"))
        chk("references_to_unprinted_headings_dropped", printed == "heading IX-003, 1.2\n"
            and "IX-001 dropped" in _read(os.path.join(refs_dir, "R_Index_Report_r1.md")))
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------- CLI

def _usage():
    print("Usage:")
    for line in __doc__.splitlines():
        if line.startswith("  book_index.py "):
            print(line)
    return 2


def _phase_b_cli(cmd, rest):
    import argparse
    ap = argparse.ArgumentParser(prog="book_index.py " + cmd)
    ap.add_argument("map")
    if cmd == "locate":
        ap.add_argument("--scheme", required=True, choices=("paragraph", "page"))
        ap.add_argument("--pdf")
        ap.add_argument("--folio-start", type=int)
        ap.add_argument("--body-end", type=int)
        ap.add_argument("--include-front", action="store_true")
        ap.add_argument("--include-back", action="store_true")
    else:
        ap.add_argument("--locators")
        ap.add_argument("--layout", default="indented", choices=("indented", "run-in"))
        ap.add_argument("--sort", default="word", choices=("word", "letter"))
        ap.add_argument("--ranges", default="chicago", choices=("chicago", "full"))
        ap.add_argument("--see-also", default="end", choices=("end", "after-heading"))
        ap.add_argument("--docx", action="store_true")
        ap.add_argument("--max-lines", type=int)
    try:
        a = ap.parse_args(rest)
    except SystemExit:
        return 2
    if cmd == "locate":
        code, lines = locate_index(a.map, a.scheme, a.pdf, a.folio_start, a.body_end, a.include_front,
                                   a.include_back)
    else:
        code, lines = format_index(a.map, a.locators, a.layout, a.sort, a.ranges, a.see_also,
                                   "docx" if a.docx else "txt", a.max_lines)
    for ln in lines:
        print(ln)
    return code


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = argv[1:]
    if not args:
        return _usage()
    cmd, rest = args[0], args[1:]
    if cmd in ("locate", "format"):
        return _phase_b_cli(cmd, rest)
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
