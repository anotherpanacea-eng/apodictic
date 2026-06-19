#!/usr/bin/env python3
"""annotated-manuscript — the editorial letter's findings, anchored in the margin.

`validate.sh annotated-manuscript <run_folder> [--strict]` shells out here. A human
developmental editor hands back the manuscript itself, marked up — margin comments
anchored where the problem lives — not only a letter that *references* loci. This builds
no new analysis: each margin comment is a VERBATIM projection of an existing
`apodictic.finding.v1` field set, anchored against a frozen snapshot of the manuscript.
The hard parts are *where it attaches* (the anchor ladder) and *proving the prose was
never touched* (the no-mutation reverse transform). Comments only — never tracked changes,
never suggested prose (that is content invention, the Firewall's red line).

Three artifacts (so the manuscript is never mutated in place):
  - the snapshot    `*_Manuscript_Snapshot_*.md`  — LF-normalized, trailing newline; immutable.
  - the manifest    `*_Annotation_Manifest_*.md`   — one apodictic.annotation.v1 block: the snapshot
                    binding (path/sha256/line_count) + annotations[] {finding_id, anchor, comment}.
  - the annotated   `*_Annotated_Manuscript_*.md`   — the snapshot with CriticMarkup `{>> ... <<}`
                    comment spans injected; the reverse transform (delete every span) == the snapshot.

The anchor ladder (per evidence_refs TOKEN; finest rung any MANUSCRIPT-scoped token supports):
  quote       (Increment 2) a finding's optional verbatim `evidence_quote` that occurs in the snapshot
              exactly once — anchors the note to the exact sentence (char offsets). Degrades if absent /
              multi-line / ambiguous; never fabricates. Gated by A6.
  line-range  a token that EXACTLY equals a Timeline Section-1 scene-id with an in-bounds range.
  section     a non-chapter manuscript heading name matched uniquely in the snapshot.
  chapter     a chapter token (Chapter N / Ch. N / Ch.N / Ch N, via the SHARED chapter_token) with a
              unique matching heading. Page suffixes are ignored — never promoted to precision.
  document    no manuscript-scoped token resolved (e.g. a `Pass N §...` artifact ref) — surfaced as a
              general note at the head, honestly NOT positioned in the margin.
`Pass N §...` / bare `§...` tokens are ARTIFACT-scoped: excluded from the finer rungs (they cannot win
a section anchor from a pass-artifact ref); they contribute only `document`.

Validator (`annotated-manuscript`):
  A1 manifest schema     the single apodictic.annotation.v1 block parses; top-level binding fields +
                         per-entry shape; anchor.kind enum; finding_id UNIQUE across annotations[].
  A2 no prose mutation   reverse transform (delete every {>> ... <<} span) == the BOUND snapshot,
     (signature gate)    byte-for-byte. Two-sided precondition, before render: hard-fail if EITHER the
                         snapshot OR any projected comment field carries a CriticMarkup sigil.
  A3 anchor integrity    every anchor resolves against the snapshot — line-range in bounds, a UNIQUE
                         chapter/section heading (ATX, normalized; an ambiguous heading is not precise
                         enough); honest `document` is fine, an unresolved finer anchor is an error.
  A4 Must-Fix reaches    the rendered comment-span multiset == the manifest comment multiset (each
     the marked-up copy  manifest comment renders exactly once AND no un-manifested/authored span is
                         present), then every body Must-Fix is in the manifest. Reuses
                         finding_trace.ledger_inventory.
  A5 verbatim+renderable each comment == the fixed template over the finding's verbatim fields, AND
                         each projected field is inline-CriticMarkup-safe (no \\r \\n {>> <<} |).
  A6 quote integrity     (Increment 2) every `quote` anchor's text occurs in the snapshot VERBATIM and
                         exactly once, the offsets pin that occurrence, and it matches the finding's
                         evidence_quote — the fabricated-quote failure A3 cannot see. Provenance-by-
                         identity; the rendered margin is still the comment (A5), never the quote.
  W1 coverage / drift    a Should/Could finding with a locatable ref left as `document`; or a Timeline
                         line-range that overruns the snapshot at a boundary. Advisory (ERROR --strict);
                         override `<!-- override: annotation-coverage <F-...> -->`.

Reuses apodictic_artifacts (block grammar + schema engine + chapter_token), timeline_checks (the
Timeline Event-Ledger parser), and finding_trace.ledger_inventory (the Must-Fix set). See
docs/annotated-manuscript.md.

  annotation_manifest.py build <run_folder> [-o-]            # resolve anchors + render (writes manifest + annotated copy)
  annotation_manifest.py render <manifest> <snapshot> [-o out.md]
  annotation_manifest.py annotated-manuscript <run_folder|files...> [--strict]
  annotation_manifest.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import hashlib
import json
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
    import finding_trace as ft
except ImportError:
    ft = None

_SCHEMA_ID = "apodictic.annotation.v1"
_FINDING_SCHEMA_ID = "apodictic.finding.v1"

_SNAPSHOT_GLOB = "*_Manuscript_Snapshot_*.md"
_MANIFEST_GLOB = "*_Annotation_Manifest_*.md"
_ANNOTATED_GLOB = "*_Annotated_Manuscript_*.md"
_LEDGER_GLOB = "*_Findings_Ledger_*.md"
_TIMELINE_GLOBS = ("*_Timeline_*.md", "Timeline.md")

_ANCHOR_KINDS = ("line-range", "section", "chapter", "document", "quote")
_RUNG_RANK = {"document": 1, "chapter": 2, "section": 3, "line-range": 4, "quote": 5}
_TOP_KEYS = ("schema", "project", "runlabel", "snapshot_path", "snapshot_sha256",
             "snapshot_line_count", "annotations")
_ANNOT_KEYS = ("finding_id", "anchor", "comment")

# CriticMarkup comment span. The reverse transform deletes exactly these spans; nothing else is
# ever inserted (spans carry no surrounding whitespace), so the transform is the snapshot identity.
_CM_OPEN, _CM_CLOSE = "{>>", "<<}"
_CM_SPAN_RE = re.compile(r"\{>>.*?<<\}", re.DOTALL)
# An inline comment field must not break the span grammar or inject document structure.
_UNSAFE_RE = re.compile(r"[\r\n|]|\{>>|<<\}")
# Artifact-scoped reference tokens (a pass/audit artifact, NOT a manuscript locus): a LEADING `§`
# (a bare section-of-artifact ref like `§Orientation`) or a leading `Pass N`. NB a manuscript
# scene-id is `Ch N §M` — it contains `§` but starts with a chapter token, so it is NOT artifact-
# scoped (and an exact scene-id match is resolved as line-range before this test even applies).
_PASS_REF_RE = re.compile(r"^\s*pass\s+\d+", re.IGNORECASE)
_ATX_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")
_OVERRIDE_RE = re.compile(r"<!--\s*override:\s*annotation-coverage\s+(F-[A-Za-z0-9]+-[0-9]{2,})",
                          re.IGNORECASE)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


# ---------------------------------------------------------------- snapshot + comment primitives

def normalize_snapshot(text):
    """Snapshot normalization: line endings -> LF, a trailing newline ensured, NOTHING else."""
    t = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    if not t.endswith("\n"):
        t += "\n"
    return t


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def line_count(snapshot):
    """Lines in a normalized (trailing-newline) snapshot — the snapshot IS the line index."""
    return snapshot.count("\n")


def comment_for(finding):
    """The fixed margin-comment template over a finding's VERBATIM fields. No free-text slot."""
    return "[%s · %s] %s — fix class: %s. (See letter §%s.)" % (
        finding.get("severity"), finding.get("id"), finding.get("mechanism"),
        finding.get("fix_class"), finding.get("id"))


def unsafe_fields(finding):
    """Projected fields that are NOT inline-CriticMarkup-safe (A5 sub-rule). Empty == safe."""
    bad = []
    for f in ("severity", "id", "mechanism", "fix_class"):
        v = finding.get(f)
        if v is None or _UNSAFE_RE.search(str(v)):
            bad.append(f)
    return bad


# ---------------------------------------------------------------- snapshot structure

def atx_headings(snapshot):
    """[(lineno, raw_text, norm_text)] for ATX (`#..`) headings only (1-based linenos)."""
    out = []
    for i, line in enumerate(snapshot.splitlines()):
        m = _ATX_RE.match(line)
        if m:
            raw = m.group(1)
            out.append((i + 1, raw, raw.strip().lower()))
    return out


def heading_index(snapshot):
    """(chapter_counts, section_counts, chapter_lines, section_lines) from the snapshot headings.

    chapter_counts/section_counts map a key -> how many headings carry it (for the uniqueness gate);
    *_lines map a key -> the FIRST matching lineno (used only when the key is unique)."""
    chap_n, sec_n, chap_l, sec_l = {}, {}, {}, {}
    for lineno, _raw, norm in atx_headings(snapshot):
        ct = art.chapter_token(norm) if art is not None else None
        if ct:
            chap_n[ct] = chap_n.get(ct, 0) + 1
            chap_l.setdefault(ct, lineno)
        else:
            sec_n[norm] = sec_n.get(norm, 0) + 1
            sec_l.setdefault(norm, lineno)
    return chap_n, sec_n, chap_l, sec_l


def timeline_scene_ranges(timeline_text):
    """{scene_id: (start,end)} from the Timeline Section-1 Event-Ledger 'Line range' column."""
    out = {}
    if not timeline_text or tl is None:
        return out
    for row in tl._parse_event_ledger(timeline_text):
        sid = tl._row_get(row, "scene id")
        lr = tl._row_get(row, "line range")
        if not sid or not lr:
            continue
        m = re.match(r"\s*(\d+)\s*[-–]\s*(\d+)\s*$", str(lr))
        if m:
            out[sid] = (int(m.group(1)), int(m.group(2)))
    return out


def _artifact_scoped(token):
    t = str(token).strip()
    return bool(_PASS_REF_RE.search(t)) or t.startswith("§")


# ---------------------------------------------------------------- the anchor ladder

def resolve_anchor(refs, lc, chap_n, sec_n, scene_ranges):
    """Resolve a finding's evidence_refs to {kind, value} — finest rung any manuscript-scoped token
    supports, never fabricating precision. chap_n/sec_n are the heading-uniqueness counts."""
    best = {"kind": "document", "value": ""}
    best_rank = 1
    for ref in refs or []:
        t = str(ref).strip()
        cand = None
        if t in scene_ranges:                                    # line-range — exact scene-id (manuscript-scoped by definition)
            s, e = scene_ranges[t]
            if 1 <= s <= e <= lc:
                cand = ("line-range", "%d-%d" % (s, e), 4)
        elif _artifact_scoped(t):                                # a Pass/audit artifact ref — excluded from the finer rungs
            continue
        else:
            ct = art.chapter_token(t) if art is not None else None
            if ct is not None:                                   # chapter-shaped token
                if chap_n.get(ct, 0) == 1:                       # unique heading (ambiguous -> degrade)
                    cand = ("chapter", ct, 2)
            elif sec_n.get(t.lower(), 0) == 1:                   # non-chapter heading name -> section
                cand = ("section", t, 3)
        if cand and cand[2] > best_rank:
            best, best_rank = {"kind": cand[0], "value": cand[1]}, cand[2]
    return best


def anchor_line(anchor, snapshot, chap_l, sec_l):
    """The 1-based snapshot line an anchor attaches to (None for `document`, which prepends line 1)."""
    kind, val = anchor.get("kind"), anchor.get("value")
    if kind == "line-range":
        m = re.match(r"(\d+)-(\d+)$", str(val))
        return int(m.group(1)) if m else None
    if kind == "chapter":
        return chap_l.get(val)
    if kind == "section":
        return sec_l.get(str(val).strip().lower())
    return None


def quote_anchor(finding, snapshot):
    """A `quote` anchor (Increment 2) for a finding's optional verbatim `evidence_quote`, or None.

    Emitted ONLY when the quote is a single-line, inline-safe string that occurs in the snapshot
    verbatim and EXACTLY ONCE (non-overlapping `str.count`, the same definition A6 uses). Empty /
    whitespace-only, multi-line, sigil-bearing, absent, or ambiguous (>1) quotes return None and fall
    through to the `evidence_refs` ladder — the resolver never fabricates a sentence-level span."""
    q = finding.get("evidence_quote")
    if not isinstance(q, str) or not q.strip():
        return None
    if "\n" in q or "\r" in q or _CM_OPEN in q or _CM_CLOSE in q:   # any line break -> not single-line
        return None
    if snapshot.count(q) != 1:
        return None
    start = snapshot.find(q)
    return {"kind": "quote", "value": "%d-%d" % (start, start + len(q)), "quote": q}


# ---------------------------------------------------------------- manifest + render

def parse_manifest(text):
    """(obj_or_None, schema_errs) for the single apodictic:annotation block."""
    if not text or art is None:
        return None, ["no annotation block found"]
    schema = art.load_schema(_SCHEMA_ID)
    for bt, obj, jerr in art.parse_blocks(text):
        if bt != "annotation":
            continue
        if jerr:
            return None, ["annotation: invalid JSON — %s" % jerr]
        return obj, art.validate_obj(obj, schema, "annotation")
    return None, ["no annotation block found"]


def build_manifest(snapshot, ledger_text, timeline_text, project="Manuscript",
                   runlabel="run", snapshot_path="snapshot.md"):
    """Resolve every ledger finding to an anchor + projected comment. Returns (obj, errors).

    A finding whose projected fields are NOT inline-safe is a hard error here (build refuses to
    emit an unrenderable comment), surfacing it for a finding-hygiene fix rather than guessing."""
    errs = []
    lc = line_count(snapshot)
    chap_n, sec_n, _cl, _sl = heading_index(snapshot)
    scene_ranges = timeline_scene_ranges(timeline_text)
    annotations = []
    findings = []
    if ledger_text and art is not None:
        for bt, obj, _e in art.parse_blocks(ledger_text):
            if bt == "finding" and isinstance(obj, dict) and obj.get("id"):
                findings.append(obj)
    for fd in findings:
        bad = unsafe_fields(fd)
        if bad:
            errs.append("finding %s has non-inline-safe field(s) %s — cannot project a CriticMarkup "
                        "comment (fix the finding text)" % (fd.get("id"), bad))
            continue
        anchor = (quote_anchor(fd, snapshot)
                  or resolve_anchor(fd.get("evidence_refs"), lc, chap_n, sec_n, scene_ranges))
        annotations.append({"finding_id": fd["id"], "anchor": anchor, "comment": comment_for(fd)})
    obj = {"schema": _SCHEMA_ID, "project": project, "runlabel": runlabel,
           "snapshot_path": snapshot_path, "snapshot_sha256": sha256(snapshot),
           "snapshot_line_count": lc, "annotations": annotations}
    return obj, errs


def render(snapshot, manifest_obj):
    """Inject CriticMarkup comment spans into the snapshot. Pure function of (snapshot, manifest).

    A single character-offset splice that subsumes Increment-1's line placement (Increment 2): every
    span is reduced to ONE insertion offset — `document` -> 0; a line-anchored span -> the offset of its
    line's terminating newline (i.e. end-of-line, exactly as Increment 1); a `quote` span -> its anchor
    `end` offset — then all spans are spliced in DESCENDING offset order (tie-broken by descending
    manifest index) so each insertion sits to the right of every not-yet-inserted span and never
    perturbs another's offset. Spans carry no surrounding whitespace, so deleting them yields the
    snapshot byte-for-byte; the right-to-left order is what keeps a span from landing INSIDE another's
    `{>> ... <<}` (which would dangle a sigil — an A2 break). Byte-identical to Increment 1 for
    non-quote anchors. Raises ValueError on the A2 sigil precondition."""
    if _CM_OPEN in snapshot or _CM_CLOSE in snapshot:
        raise ValueError("snapshot already contains a CriticMarkup sigil — the reverse transform "
                         "would not be reversible; escape the snapshot first")
    chap_n, sec_n, chap_l, sec_l = heading_index(snapshot)
    # offset of the newline terminating each 1-based line (end-of-line spans insert just before it)
    nl_at, ln = {}, 1
    for i, ch in enumerate(snapshot):
        if ch == "\n":
            nl_at[ln] = i
            ln += 1
    inserts = []   # (offset, manifest_index, span)
    for idx, an in enumerate(manifest_obj.get("annotations") or []):
        anc = an.get("anchor") or {}
        span = "%s%s%s" % (_CM_OPEN, an.get("comment", ""), _CM_CLOSE)
        if anc.get("kind") == "quote":
            m = re.match(r"(\d+)-(\d+)$", str(anc.get("value", "")))
            off = int(m.group(2)) if m else 0
        else:
            line = anchor_line(anc, snapshot, chap_l, sec_l)
            off = 0 if line is None else nl_at.get(line, len(snapshot))
        inserts.append((off, idx, span))
    out = snapshot
    # descending (offset, manifest index): insert right-to-left so earlier inserts never shift later ones
    for off, _idx, span in sorted(inserts, key=lambda t: (t[0], t[1]), reverse=True):
        off = max(0, min(off, len(out)))
        out = out[:off] + span + out[off:]
    return out


def reverse_transform(annotated):
    """Delete every CriticMarkup comment span — the specified A2 inverse of render()."""
    return _CM_SPAN_RE.sub("", annotated)


# ---------------------------------------------------------------- the validator

def check(snapshot_text, manifest_text, annotated_text, ledger_text, timeline_text=None,
          strict=False, ledger_optional=False):
    """Run A1-A6 + W1. Returns (code, lines). Each input may be None (resolution reports the gap).

    `ledger_optional=True` is the re-anchoring context (`reanchor.py`): a manifest re-anchored onto a
    *revised* draft has no re-diagnosed Findings Ledger, so the ledger-dependent arms (A5 projection,
    A4 Must-Fix completeness) are legitimately absent and the "no Findings Ledger" error is suppressed
    — leaving A1 + A2 + A3 + A4-multiset + A6 (the structural / no-mutation / quote-integrity subset a
    re-anchored copy inherits). Comment fidelity in that context is RA2's job (verbatim carry-over),
    not A5's. Default False preserves the strict ledger requirement for the normal build path."""
    lines, errs, warns = [], [], []
    obj, schema_errs = parse_manifest(manifest_text)
    if obj is None:
        if any("invalid JSON" in e for e in schema_errs):
            return 1, ["annotated-manuscript: %s" % schema_errs[0],
                       "annotated-manuscript: FAIL (A1 manifest schema)"]
        return 1, ["annotated-manuscript: no apodictic.annotation block found in the manifest",
                   "annotated-manuscript: FAIL (A1 — manifest block missing)"]
    if snapshot_text is None or annotated_text is None:
        return 2, ["annotated-manuscript: need a snapshot AND an annotated copy to validate "
                   "(missing %s)" % (" + ".join(n for n, t in (("snapshot", snapshot_text),
                    ("annotated copy", annotated_text)) if t is None))]

    snapshot = snapshot_text   # the committed snapshot is already normalized; compared as-is

    # A1 — wrapper schema + nested annotations[] + uniqueness
    for e in schema_errs:
        errs.append("A1 manifest schema: %s" % e)
    for k in obj:
        if k not in _TOP_KEYS:
            errs.append("A1 manifest schema: top-level has disallowed field '%s'" % k)
    annotations = obj.get("annotations") if isinstance(obj.get("annotations"), list) else []
    if not isinstance(obj.get("annotations"), list):
        errs.append("A1 manifest schema: annotations must be an array")
    seen = {}
    for i, an in enumerate(annotations):
        where = "annotations[%d]" % i
        if not isinstance(an, dict):
            errs.append("A1 manifest schema: %s must be an object" % where)
            continue
        for k in _ANNOT_KEYS:
            if k not in an:
                errs.append("A1 manifest schema: %s missing required field '%s'" % (where, k))
        anc = an.get("anchor")
        if not isinstance(anc, dict) or anc.get("kind") not in _ANCHOR_KINDS:
            errs.append("A1 manifest schema: %s.anchor.kind must be one of %s"
                        % (where, "/".join(_ANCHOR_KINDS)))
        elif anc.get("kind") == "quote":
            # Structural shape of a quote anchor (content/snapshot matching is A6's job). A malformed
            # quote anchor is an A1 error, not a silent A3 skip (A3 deliberately skips kind=="quote").
            qv = anc.get("quote")
            if not isinstance(qv, str) or not qv:
                errs.append("A1 manifest schema: %s quote anchor requires a non-empty 'quote' string" % where)
            vm = re.match(r"^(\d+)-(\d+)$", str(anc.get("value", "")))
            if not vm or int(vm.group(1)) > int(vm.group(2)):
                errs.append("A1 manifest schema: %s quote anchor value must be '<start>-<end>' with "
                            "start <= end" % where)
        fid = an.get("finding_id")
        if fid is not None:
            seen[fid] = seen.get(fid, 0) + 1
    for fid, n in sorted((kv for kv in seen.items() if kv[1] > 1)):
        errs.append("A1 manifest schema: finding_id %r appears %d times in annotations[] "
                    "(each finding gets exactly one entry; a duplicate double-comments it)" % (fid, n))

    # Binding — the manifest must bind THIS snapshot (so the validator can't be pointed at the wrong one)
    lc = line_count(snapshot)
    if obj.get("snapshot_sha256") != sha256(snapshot):
        errs.append("A2 no prose mutation: manifest snapshot_sha256 does not match the resolved "
                    "snapshot (the manifest is bound to a different snapshot)")
    if obj.get("snapshot_line_count") != lc:
        errs.append("A1 manifest schema: snapshot_line_count=%r != the snapshot's %d lines"
                    % (obj.get("snapshot_line_count"), lc))

    # A2 — no prose mutation (the signature gate) + two-sided sigil precondition
    if _CM_OPEN in snapshot or _CM_CLOSE in snapshot:
        errs.append("A2 no prose mutation: the SNAPSHOT already contains a CriticMarkup sigil "
                    "({>> or <<}) — the reverse transform is not reversible; escape the snapshot first")
    elif reverse_transform(annotated_text) != snapshot:
        errs.append("A2 no prose mutation: deleting every {>> ... <<} span from the annotated copy "
                    "does NOT reproduce the snapshot byte-for-byte (prose was altered, or a span is "
                    "malformed)")

    # Heading / Timeline structure for A3 + render-equality
    chap_n, sec_n, chap_l, sec_l = heading_index(snapshot)
    scene_ranges = timeline_scene_ranges(timeline_text)

    # A3 — anchor integrity (honest `document` is fine; an unresolved finer anchor is an error)
    for an in annotations:
        if not isinstance(an, dict):
            continue
        anc = an.get("anchor") or {}
        kind, val = anc.get("kind"), anc.get("value")
        if kind == "line-range":
            m = re.match(r"(\d+)-(\d+)$", str(val))
            if not m or not (1 <= int(m.group(1)) <= int(m.group(2)) <= lc):
                errs.append("A3 anchor integrity: %s line-range %r is not an in-bounds 1..%d range"
                            % (an.get("finding_id"), val, lc))
        elif kind == "chapter":
            if chap_n.get(val, 0) != 1:
                errs.append("A3 anchor integrity: %s chapter anchor %r matches %d snapshot heading(s) "
                            "(need exactly 1; ambiguous -> document)"
                            % (an.get("finding_id"), val, chap_n.get(val, 0)))
        elif kind == "section":
            if sec_n.get(str(val).strip().lower(), 0) != 1:
                errs.append("A3 anchor integrity: %s section anchor %r matches %d snapshot heading(s) "
                            "(need exactly 1)" % (an.get("finding_id"), val, sec_n.get(str(val).strip().lower(), 0)))

    # A4/A5 need the ledger. A wholly-absent ledger is reported ONCE (not once per annotation): the
    # run-folder resolver supplies it when present, so a None ledger means it is genuinely missing and
    # comment provenance is unverifiable. A per-annotation `src is None` below then means a manifest
    # entry referencing a finding ABSENT from a ledger that IS present (a dangling reference — a
    # different, real bug worth surfacing per id).
    have_ledger = ledger_text is not None
    inv = ft.ledger_inventory(ledger_text) if (ft and have_ledger) else {}
    led_obj = {}
    if have_ledger and art is not None:
        for bt, o, _e in art.parse_blocks(ledger_text):
            if bt == "finding" and isinstance(o, dict) and o.get("id"):
                led_obj[o["id"]] = o
    if not have_ledger and annotations and not ledger_optional:
        errs.append("A4/A5: no Findings Ledger resolved — comment provenance (verbatim projection + "
                    "Must-Fix completeness) is unverifiable for %d annotation(s); supply the ledger"
                    % len(annotations))
    # A5 — verbatim + renderable projection (only when the ledger is present to compare against)
    if have_ledger:
        for an in annotations:
            if not isinstance(an, dict):
                continue
            fid = an.get("finding_id")
            src = led_obj.get(fid)
            if src is None:
                errs.append("A5 projection: %s is not an apodictic.finding.v1 in the ledger "
                            "(dangling manifest reference; cannot verify the comment)" % fid)
                continue
            bad = unsafe_fields(src)
            if bad:
                errs.append("A5 projection: %s projects non-inline-safe field(s) %s into the margin "
                            "(no \\r \\n {>> <<} | allowed)" % (fid, bad))
            elif an.get("comment") != comment_for(src):
                errs.append("A5 projection: %s comment is not the verbatim field projection "
                            "(the renderer must project, not author)" % fid)

    # A4 — the rendered comment-span multiset must EQUAL the manifest comment multiset (both
    # directions), then every body Must-Fix must be present. FORWARD: each manifest comment renders
    # exactly once (a manifest entry that never renders is the gap a manifest-only check misses).
    # INVERSE: no rendered span may be absent from the manifest — an extra *authored* CriticMarkup note
    # passes A2 (the reverse transform deletes it) and the per-manifest checks, smuggling un-projected
    # content into the deliverable; that is a Firewall violation, caught here. (PR #99 review.)
    span_contents = [s[len(_CM_OPEN):-len(_CM_CLOSE)] for s in _CM_SPAN_RE.findall(annotated_text)]
    span_counts = {}
    for c in span_contents:
        span_counts[c] = span_counts.get(c, 0) + 1
    manifest_comments = set()
    for an in annotations:
        if isinstance(an, dict):
            manifest_comments.add(an.get("comment"))
    manifest_ids = {an.get("finding_id") for an in annotations if isinstance(an, dict)}
    for an in annotations:
        if not isinstance(an, dict):
            continue
        c = an.get("comment")
        n = span_counts.get(c, 0)
        if n != 1:
            errs.append("A4 rendered span: %s appears as %d rendered comment span(s) in the annotated "
                        "copy (need exactly 1 — a manifest entry that never renders is the gap a "
                        "manifest-only check misses)" % (an.get("finding_id"), n))
    for content, n in sorted(span_counts.items()):
        if content not in manifest_comments:
            shown = (content[:77] + "…") if len(content) > 80 else content
            errs.append("A4 un-manifested span: the annotated copy carries a CriticMarkup note absent "
                        "from annotations[] (%d occurrence(s)): %r — every margin span must be a "
                        "verbatim projection of a manifest annotation; an authored note is a Firewall "
                        "violation (it passes A2 because the reverse transform deletes it)" % (n, shown))
    for fid, sev in sorted(inv.items()):
        if sev == "Must-Fix" and fid not in manifest_ids:
            errs.append("A4 Must-Fix completeness: ledger Must-Fix %s has no annotation "
                        "(a locked Must-Fix cannot fail to reach the marked-up copy)" % fid)

    # A6 — quote integrity (Increment 2): the content gate A3 does not cover. For every `quote` anchor,
    # the quoted text must be a verbatim, UNIQUE manuscript span that the recorded offsets pin and that
    # matches the finding's evidence_quote. Provenance-by-identity: anything A6 admits is, by
    # construction, manuscript bytes — the rendered margin is still the comment (A5), never the quote.
    for an in annotations:
        if not isinstance(an, dict):
            continue
        anc = an.get("anchor") or {}
        if anc.get("kind") != "quote":
            continue
        fid = an.get("finding_id")
        qv = anc.get("quote")
        # (d) present + single-line + inline-safe (extends A2's two-sided sigil precondition to
        # anchor.quote). Any line break — \n OR \r (a bare CR, the one the snapshot's LF normalization
        # would have collapsed) — violates the single-line contract, so both are rejected.
        if (not isinstance(qv, str) or not qv or "\n" in qv or "\r" in qv
                or _CM_OPEN in qv or _CM_CLOSE in qv):
            errs.append("A6 quote integrity: %s anchor.quote is missing, empty, multi-line (\\n/\\r), "
                        "or not inline-CriticMarkup-safe (no {>> <<})" % fid)
            continue
        # (a) faithful projection of the finding's evidence_quote (no substitution)
        src = led_obj.get(fid)
        if src is not None and qv != src.get("evidence_quote"):
            errs.append("A6 quote integrity: %s anchor.quote is not the finding's verbatim "
                        "evidence_quote (the manifest substituted a different quote)" % fid)
        # (b) verbatim + unique (non-overlapping count)
        n = snapshot.count(qv)
        if n != 1:
            errs.append("A6 quote integrity: %s anchor.quote occurs %d time(s) in the snapshot "
                        "(need exactly 1 — 0 = fabricated, >1 = ambiguous, must degrade not anchor)"
                        % (fid, n))
            continue
        # (c) offsets pin the unique occurrence (catches an off-by-one / relocated span, distinct from absence)
        m = re.match(r"^(\d+)-(\d+)$", str(anc.get("value", "")))
        if not m:
            errs.append("A6 quote integrity: %s quote anchor value is not '<start>-<end>'" % fid)
            continue
        start, end = int(m.group(1)), int(m.group(2))
        if snapshot[start:end] != qv or start != snapshot.find(qv):
            errs.append("A6 quote integrity: %s offsets %d-%d do not delimit the unique occurrence "
                        "(snapshot[start:end] != quote, or not the str.find index)" % (fid, start, end))

    # W1 — snapshot normalization (the harness owns it; the validator never rewrites the snapshot, so
    # this is advisory). A non-LF / no-trailing-newline snapshot is still A2-self-consistent, but it
    # violates §Prerequisite's normalization contract.
    if snapshot != normalize_snapshot(snapshot):
        warns.append("W1 normalization: the snapshot is not LF-normalized with a trailing newline "
                     "(the run harness should normalize on snapshot creation, per §Prerequisite)")

    # W1 — coverage (a locatable Should/Could left as `document`) + Timeline boundary drift
    overrides = set(_OVERRIDE_RE.findall(manifest_text or ""))
    for an in annotations:
        if not isinstance(an, dict):
            continue
        fid = an.get("finding_id")
        anc = an.get("anchor") or {}
        if anc.get("kind") == "document" and fid not in overrides:
            src = led_obj.get(fid)
            if src and inv.get(fid) in ("Should-Fix", "Could-Fix"):
                would = resolve_anchor(src.get("evidence_refs"), lc, chap_n, sec_n, scene_ranges)
                if would.get("kind") != "document":
                    warns.append("W1 coverage: %s (%s) is a `document` note but its ref resolves to "
                                 "%s — anchor it, or override" % (fid, inv.get(fid), would.get("kind")))
    for sid, (s, e) in sorted(scene_ranges.items()):
        if e > lc:
            warns.append("W1 boundary drift: Timeline scene %s line-range ends at %d, past the "
                         "snapshot's %d lines" % (sid, e, lc))

    # Report
    by_kind = {}
    for an in annotations:
        if isinstance(an, dict):
            k = (an.get("anchor") or {}).get("kind", "?")
            by_kind[k] = by_kind.get(k, 0) + 1
    lines.append("annotated-manuscript: %s [%s] — %d annotation(s) (%s)"
                 % (obj.get("project", "?"), obj.get("runlabel", "?"), len(annotations),
                    ", ".join("%s:%d" % (k, by_kind[k]) for k in sorted(by_kind)) or "none"))
    for an in annotations:
        if isinstance(an, dict):
            anc = an.get("anchor") or {}
            lines.append("  %-12s %s:%s" % (an.get("finding_id"), anc.get("kind"), anc.get("value")))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("annotated-manuscript: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: annotated-manuscript: %d advisory flag(s) — see W1 above" % len(warns))
    else:
        lines.append("annotated-manuscript: PASS (no-mutation + anchor integrity + Must-Fix rendered "
                     "+ verbatim projection)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve_run_folder(folder):
    snap = _newest(glob.glob(os.path.join(folder, _SNAPSHOT_GLOB)))
    man = _newest(glob.glob(os.path.join(folder, _MANIFEST_GLOB)))
    ann = _newest(glob.glob(os.path.join(folder, _ANNOTATED_GLOB)))
    led = _newest(glob.glob(os.path.join(folder, _LEDGER_GLOB)))
    tlp = None
    for g in _TIMELINE_GLOBS:
        tlp = _newest(glob.glob(os.path.join(folder, g)))
        if tlp:
            break
    return snap, man, ann, led, tlp


def classify_files(paths):
    snap = man = ann = led = tlp = None
    for p in paths:
        base = os.path.basename(p)
        body = _read(p) or ""
        if "_Manuscript_Snapshot_" in base:
            snap = p
        elif "_Annotation_Manifest_" in base or "apodictic:annotation" in body:
            man = p
        elif "_Annotated_Manuscript_" in base:
            ann = p
        elif "apodictic:finding" in body:
            led = p
        elif "scene id" in body.lower() and "|" in body:
            tlp = p
    return snap, man, ann, led, tlp


def run(paths, strict=False):
    if len(paths) == 1 and os.path.isdir(paths[0]):
        snap, man, ann, led, tlp = resolve_run_folder(paths[0])
        # Honor the manifest's snapshot BINDING: resolve the snapshot the manifest was rendered against
        # by its `snapshot_path`, NOT by a "newest" glob — so an r1 manifest sitting beside a newer r2
        # snapshot is still checked against its own (r1) pair, never mis-paired with r2 (the rerun-in-
        # progress case the spec calls out). basename() keeps the binding inside the run folder (no
        # traversal); falls back to the glob only if the bound file is absent (then A2's sha check fails
        # loudly rather than degrading).
        if man:
            mobj, _merr = parse_manifest(_read(man))
            bound = mobj.get("snapshot_path") if isinstance(mobj, dict) else None
            if bound:
                cand = os.path.join(paths[0], os.path.basename(str(bound)))
                if os.path.isfile(cand):
                    snap = cand
    else:
        snap, man, ann, led, tlp = classify_files(paths)
    if not man:
        return 2, ["annotated-manuscript: no annotation manifest found (need a *_Annotation_Manifest_*.md "
                   "or a file with an apodictic:annotation block)"]
    return check(_read(snap) if snap else None, _read(man), _read(ann) if ann else None,
                 _read(led) if led else None, _read(tlp) if tlp else None, strict=strict)


# ---------------------------------------------------------------- build / render CLIs

def build(folder):
    """Resolve anchors + render from a run folder. Writes the manifest + annotated copy. Returns code."""
    snap, _man, _ann, led, tlp = resolve_run_folder(folder)
    if not snap:
        print("annotated-manuscript: no *_Manuscript_Snapshot_*.md in %s" % folder, file=sys.stderr)
        return 2
    snapshot = _read(snap)
    if snapshot is None:
        print("annotated-manuscript: cannot read %s" % snap, file=sys.stderr)
        return 2
    project = os.path.basename(snap).split("_Manuscript_Snapshot_")[0] or "Manuscript"
    runlabel = os.path.splitext(os.path.basename(snap).split("_Manuscript_Snapshot_")[-1])[0] or "run"
    obj, berrs = build_manifest(snapshot, _read(led) if led else None, _read(tlp) if tlp else None,
                                project=project, runlabel=runlabel, snapshot_path=os.path.basename(snap))
    if berrs:
        for e in berrs:
            print("annotated-manuscript: %s" % e, file=sys.stderr)
        return 1
    annotated = render(snapshot, obj)
    man_path = os.path.join(folder, "%s_Annotation_Manifest_%s.md" % (project, runlabel))
    ann_path = os.path.join(folder, "%s_Annotated_Manuscript_%s.md" % (project, runlabel))
    with open(man_path, "w", encoding="utf-8", newline="") as fh:
        fh.write("# Annotation Manifest\n\n<!-- apodictic:annotation\n%s\n-->\n"
                 % json.dumps(obj, indent=2))
    with open(ann_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(annotated)
    print("annotated-manuscript: wrote %s + %s" % (os.path.basename(man_path), os.path.basename(ann_path)))
    return 0


# ---------------------------------------------------------------- self-test

def run_self_test():
    import tempfile
    import shutil
    rc = {"v": 0}
    made = []

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    # A snapshot with two chapter headings, a section heading, and body lines that a Timeline
    # scene-range can point at.
    snapshot = normalize_snapshot(
        "# Chapter 1\n"            # line 1
        "She opened the door.\n"   # line 2
        "## Scene Turns\n"         # line 3 (a manuscript section)
        "The turn lands late.\n"   # line 4
        "# Chapter 9\n"            # line 5
        "Three days passed.\n"     # line 6
        "# Chapter 12\n"           # line 7
        "The lighthouse stood unlit for forty years.\n"   # line 8 — a unique sentence (quote rung)
        "tick tock tick tock\n")   # line 9 — 'tick tock' appears twice (ambiguous -> degrade)

    timeline = ("## Section 1: Event Ledger\n\n"
                "| Scene ID | Chapter / Section | Line range | Word count | POV | Setting | Span | Gap |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| Ch 1 §1 | Ch 1 | 2-2 | 5 | Mara | Door | 1h | n/a |\n")

    def finding(fid, sev, refs, mech="m", fix="f", quote=None):
        o = {"schema": _FINDING_SCHEMA_ID, "id": fid, "mechanism": mech, "severity": sev,
             "confidence": "HIGH", "evidence_refs": list(refs), "fix_class": fix, "risk_if_fixed": "r"}
        if quote is not None:
            o["evidence_quote"] = quote
        return '<!-- apodictic:finding\n%s\n-->' % json.dumps(o)

    # F-LR line-range (exact scene-id), F-CH chapter, F-DOC pass-artifact -> document,
    # F-SEC section, F-MIX mixed (pass-ref + chapter -> chapter); F-QT quote (Inc 2; outranks its Ch 12
    # ref), F-QAMB ambiguous quote -> degrades to its chapter ref.
    quote_pos = "The lighthouse stood unlit for forty years."
    ledger = "# Ledger\n" + "\n".join([
        finding("F-LR-01", "Must-Fix", ["Ch 1 §1"]),
        finding("F-CH-01", "Must-Fix", ["Chapter 9"]),
        finding("F-DOC-01", "Should-Fix", ["Pass 1 §Orientation"]),
        finding("F-SEC-01", "Could-Fix", ["Scene Turns"]),
        finding("F-MIX-01", "Should-Fix", ["Pass 4 §Scene Turns", "Ch. 9"]),
        finding("F-QT-01", "Must-Fix", ["Chapter 12"], quote=quote_pos),
        finding("F-QAMB-01", "Should-Fix", ["Chapter 12"], quote="tick tock"),
    ]) + "\n"

    obj, berrs = build_manifest(snapshot, ledger, timeline, project="T", runlabel="r")
    chk("build_no_errors", not berrs)
    amap = {a["finding_id"]: a["anchor"] for a in obj["annotations"]}
    chk("ladder_line_range", amap["F-LR-01"] == {"kind": "line-range", "value": "2-2"})
    chk("ladder_chapter", amap["F-CH-01"] == {"kind": "chapter", "value": "Ch 9"})
    chk("ladder_doc_passref", amap["F-DOC-01"]["kind"] == "document")
    chk("ladder_section", amap["F-SEC-01"] == {"kind": "section", "value": "Scene Turns"})
    # mixed: the `§` pass-ref is artifact-scoped (cannot win section); the chapter token wins
    chk("ladder_mixed_chapter_wins", amap["F-MIX-01"] == {"kind": "chapter", "value": "Ch 9"})
    # quote (Inc 2): a unique verbatim evidence_quote outranks the finding's chapter ref
    _qs = snapshot.find(quote_pos)
    chk("ladder_quote", amap["F-QT-01"] == {"kind": "quote",
        "value": "%d-%d" % (_qs, _qs + len(quote_pos)), "quote": quote_pos})
    # an AMBIGUOUS quote ('tick tock' twice) does NOT anchor; it degrades to the chapter ref
    chk("ladder_quote_ambiguous_degrades", amap["F-QAMB-01"] == {"kind": "chapter", "value": "Ch 12"})

    annotated = render(snapshot, obj)
    chk("render_reverses_to_snapshot", reverse_transform(annotated) == snapshot)
    chk("render_no_new_lines", annotated.count("\n") == snapshot.count("\n"))
    chk("render_doc_at_head", annotated.startswith(_CM_OPEN))   # F-DOC prepends line 1

    def manifest_md(o):
        return "# Manifest\n<!-- apodictic:annotation\n%s\n-->\n" % json.dumps(o)

    # clean validate
    code, ls = check(snapshot, manifest_md(obj), annotated, ledger, timeline)
    chk("clean_validate", code == 0)

    # --- Increment 2: A6 quote integrity + A1 quote shape (hostile manifests) ---
    # A6(b) fabricated: a quote anchor whose text is absent from the snapshot (A2/A4 still pass)
    obj_fab = json.loads(json.dumps(obj))
    for a in obj_fab["annotations"]:
        if a["finding_id"] == "F-QT-01":
            a["anchor"] = {"kind": "quote", "value": "0-9", "quote": "ABSENTXYZ"}
    code, ls = check(snapshot, manifest_md(obj_fab), render(snapshot, obj_fab), ledger, timeline)
    chk("a6_fabricated_quote", code == 1 and any("A6 quote integrity" in x and "occurs 0" in x for x in ls))
    # A6(c) wrong offsets: correct UNIQUE quote, offsets shifted +1 (distinct from absence)
    obj_wo = json.loads(json.dumps(obj))
    for a in obj_wo["annotations"]:
        if a["finding_id"] == "F-QT-01":
            a["anchor"] = {"kind": "quote", "value": "%d-%d" % (_qs + 1, _qs + 1 + len(quote_pos)), "quote": quote_pos}
    code, ls = check(snapshot, manifest_md(obj_wo), render(snapshot, obj_wo), ledger, timeline)
    chk("a6_wrong_offsets", code == 1 and any("A6 quote integrity" in x and "do not delimit" in x for x in ls))
    # A6(a) projection mismatch: anchor.quote is a DIFFERENT unique snapshot string than the finding's
    obj_pm = json.loads(json.dumps(obj))
    _other = "The turn lands late."
    _os = snapshot.find(_other)
    for a in obj_pm["annotations"]:
        if a["finding_id"] == "F-QT-01":
            a["anchor"] = {"kind": "quote", "value": "%d-%d" % (_os, _os + len(_other)), "quote": _other}
    code, ls = check(snapshot, manifest_md(obj_pm), render(snapshot, obj_pm), ledger, timeline)
    chk("a6_projection_mismatch", code == 1 and any("A6 quote integrity" in x and "evidence_quote" in x for x in ls))
    # A1: a structurally malformed quote anchor (missing quote, bad value) is an A1 error, not a silent skip
    obj_a1 = json.loads(json.dumps(obj))
    for a in obj_a1["annotations"]:
        if a["finding_id"] == "F-QT-01":
            a["anchor"] = {"kind": "quote", "value": "nope"}
    code, ls = check(snapshot, manifest_md(obj_a1), render(snapshot, obj_a1), ledger, timeline)
    chk("a1_malformed_quote", code == 1 and any("A1 manifest schema" in x and "quote anchor" in x for x in ls))
    # A1: a reversed quote-anchor range (start > end) is an A1 error (matches the documented gate)
    obj_rev = json.loads(json.dumps(obj))
    for a in obj_rev["annotations"]:
        if a["finding_id"] == "F-QT-01":
            a["anchor"] = {"kind": "quote", "value": "10-3", "quote": quote_pos}
    code, ls = check(snapshot, manifest_md(obj_rev), render(snapshot, obj_rev), ledger, timeline)
    chk("a1_reversed_offsets", code == 1 and any("A1 manifest schema" in x and "start <= end" in x for x in ls))
    # build degrades a multi-line / empty evidence_quote (never a quote rung)
    obj_ml, _ = build_manifest(snapshot, "# L\n" + finding("F-ML-01", "Must-Fix", ["Chapter 9"], quote="a\nb") + "\n", timeline)
    chk("quote_multiline_degrades", obj_ml["annotations"][0]["anchor"]["kind"] != "quote")
    obj_em, _ = build_manifest(snapshot, "# L\n" + finding("F-EM-01", "Must-Fix", ["Chapter 9"], quote="   ") + "\n", timeline)
    chk("quote_empty_degrades", obj_em["annotations"][0]["anchor"]["kind"] != "quote")
    # A bare CR (\r) is a line break too: the locator degrades it AND a forged CR quote anchor is an
    # A6 error — the single-line contract holds against \r, not just \n (Codex PR #101 review P2).
    snap_cr = "AAAA\nq a\rb z\nBBBB\n"
    fd_cr = {"schema": _FINDING_SCHEMA_ID, "id": "F-CR-01", "mechanism": "m", "severity": "Must-Fix",
             "confidence": "HIGH", "evidence_refs": ["x"], "fix_class": "f", "risk_if_fixed": "r",
             "evidence_quote": "a\rb"}
    chk("quote_cr_locator_degrades", quote_anchor(fd_cr, snap_cr) is None)
    _cr = snap_cr.find("a\rb")
    obj_cr = {"schema": _SCHEMA_ID, "project": "T", "runlabel": "r", "snapshot_path": "s",
              "snapshot_sha256": sha256(snap_cr), "snapshot_line_count": line_count(snap_cr),
              "annotations": [{"finding_id": "F-CR-01",
                               "anchor": {"kind": "quote", "value": "%d-%d" % (_cr, _cr + 3), "quote": "a\rb"},
                               "comment": comment_for(fd_cr)}]}
    led_cr = "# L\n<!-- apodictic:finding\n" + json.dumps(fd_cr) + "\n-->\n"
    code, ls = check(snap_cr, manifest_md(obj_cr), render(snap_cr, obj_cr), led_cr, None)
    chk("a6_cr_quote_rejected", code == 1 and any("A6 quote integrity" in x for x in ls))

    # a wholly-absent ledger -> ONE clear A4/A5 message, not per-annotation "not in the ledger" noise
    code, ls = check(snapshot, manifest_md(obj), annotated, None, timeline)
    chk("no_ledger_single_message",
        code == 1 and sum("A4/A5: no Findings Ledger" in x for x in ls) == 1
        and not any("A5 projection" in x for x in ls))

    # A2 — mutate one prose char in the annotated copy -> reverse transform diverges
    mutated = annotated.replace("Three days passed.", "Three days passed!!")
    code, ls = check(snapshot, manifest_md(obj), mutated, ledger, timeline)
    chk("a2_prose_mutation", code == 1 and any("A2 no prose mutation" in x for x in ls))

    # A2 — snapshot carrying a sigil is a loud failure (two-sided precondition)
    snap_sigil = normalize_snapshot("# Chapter 1\nText {>>oops<<} here.\n")
    obj_s, _ = build_manifest(snap_sigil, "# Ledger\n", None, project="T", runlabel="r")
    code, ls = check(snap_sigil, manifest_md(obj_s), snap_sigil, "# Ledger\n", None)
    chk("a2_snapshot_sigil", code == 1 and any("SNAPSHOT already contains" in x for x in ls))

    # A4 — a Must-Fix present in the manifest but NOT rendered (annotated == snapshot, zero spans)
    code, ls = check(snapshot, manifest_md(obj), snapshot, ledger, timeline)
    chk("a4_unrendered_mustfix",
        code == 1 and any("A4 rendered span" in x for x in ls))
    # A4 — a Must-Fix dropped from the manifest entirely
    obj_drop = dict(obj, annotations=[a for a in obj["annotations"] if a["finding_id"] != "F-CH-01"])
    ann_drop = render(snapshot, obj_drop)
    code, ls = check(snapshot, manifest_md(obj_drop), ann_drop, ledger, timeline)
    chk("a4_dropped_mustfix",
        code == 1 and any("A4 Must-Fix completeness" in x and "F-CH-01" in x for x in ls))
    # A4 inverse (PR #99 review): an EXTRA authored CriticMarkup note appended to the annotated copy
    # must be rejected — it passes A2 (reverse_transform deletes it) and every per-manifest check, but
    # it smuggles un-projected content into the deliverable (a Firewall hole).
    ann_extra = annotated + "{>>AUTHORIZED? no: extra authored note<<}"
    code, ls = check(snapshot, manifest_md(obj), ann_extra, ledger, timeline)
    chk("a4_rejects_unmanifested_span",
        code == 1 and any("A4 un-manifested span" in x for x in ls))

    # A5 — an authored (non-projection) comment
    obj_bad = json.loads(json.dumps(obj))
    for a in obj_bad["annotations"]:
        if a["finding_id"] == "F-CH-01":
            a["comment"] = "[Must-Fix · F-CH-01] I rewrote this — fix class: f. (See letter §F-CH-01.)"
    ann_bad = render(snapshot, obj_bad)
    code, ls = check(snapshot, manifest_md(obj_bad), ann_bad, ledger, timeline)
    chk("a5_authored_comment", code == 1 and any("A5 projection" in x for x in ls))

    # A5 / build — a finding field carrying a sigil/newline is refused by build, flagged by A5
    led_unsafe = "# Ledger\n" + finding("F-X-01", "Must-Fix", ["Chapter 9"], mech="bad <<} inject") + "\n"
    _o, ue = build_manifest(snapshot, led_unsafe, None)
    chk("a5_build_refuses_unsafe", any("non-inline-safe" in e for e in ue))

    # A1 — duplicate finding_id
    obj_dup = dict(obj, annotations=obj["annotations"] + [obj["annotations"][1]])
    ann_dup = render(snapshot, obj_dup)
    code, ls = check(snapshot, manifest_md(obj_dup), ann_dup, ledger, timeline)
    chk("a1_duplicate_id", code == 1 and any("appears 2 times in annotations" in x for x in ls))

    # A1 — bad anchor.kind
    obj_kind = json.loads(json.dumps(obj))
    obj_kind["annotations"][0]["anchor"]["kind"] = "sentence"
    code, ls = check(snapshot, manifest_md(obj_kind), render(snapshot, obj), ledger, timeline)
    chk("a1_bad_anchor_kind", code == 1 and any("anchor.kind must be one of" in x for x in ls))

    # A3 — an out-of-bounds line-range
    obj_oob = json.loads(json.dumps(obj))
    for a in obj_oob["annotations"]:
        if a["finding_id"] == "F-LR-01":
            a["anchor"] = {"kind": "line-range", "value": "99-120"}
    code, ls = check(snapshot, manifest_md(obj_oob), annotated, ledger, timeline)
    chk("a3_oob_line_range", code == 1 and any("A3 anchor integrity" in x for x in ls))

    # A3 — ambiguous chapter heading degrades to document at build (no fabricated precision)
    snap_ambig = normalize_snapshot("# Chapter 9\nA\n# Chapter 9\nB\n")
    obj_a, _ = build_manifest(snap_ambig, "# Ledger\n" + finding("F-CH-02", "Must-Fix", ["Chapter 9"]) + "\n",
                              None)
    chk("a3_ambiguous_chapter_degrades", obj_a["annotations"][0]["anchor"]["kind"] == "document")

    # W1 — a locatable Should/Could parked at document is advisory (ERROR --strict)
    obj_w = json.loads(json.dumps(obj))
    for a in obj_w["annotations"]:
        if a["finding_id"] == "F-SEC-01":
            a["anchor"] = {"kind": "document", "value": ""}
    ann_w = render(snapshot, obj_w)
    code, ls = check(snapshot, manifest_md(obj_w), ann_w, ledger, timeline)
    chk("w1_advisory", code == 0 and any("W1 coverage" in x and "F-SEC-01" in x for x in ls))
    chk("w1_strict_fails", check(snapshot, manifest_md(obj_w), ann_w, ledger, timeline, strict=True)[0] == 1)
    # ...silenced by an override marker
    man_ovr = ("# Manifest\n<!-- override: annotation-coverage F-SEC-01 -->\n"
               "<!-- apodictic:annotation\n%s\n-->\n" % json.dumps(obj_w))
    chk("w1_override_silences", check(snapshot, man_ovr, ann_w, ledger, timeline, strict=True)[0] == 0)

    # resolution — a real run folder
    d = tempfile.mkdtemp()
    made.append(d)
    with open(os.path.join(d, "T_Manuscript_Snapshot_r.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(snapshot)
    with open(os.path.join(d, "T_Findings_Ledger_r.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(ledger)
    with open(os.path.join(d, "T_Timeline_r.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(timeline)
    chk("build_writes_artifacts", build(d) == 0)
    chk("run_folder_validates", run([d])[0] == 0)
    chk("missing_manifest_usage", run([d + "/nope"])[0] == 2)

    # binding resolution: an r1 deliverable must keep validating when a NEWER, DIFFERENT r2 snapshot
    # lands in the same folder (rerun in progress) — resolution honors the manifest's snapshot_path,
    # never the newest file by mtime. (Without the binding, A2 would falsely fail on the wrong pair.)
    d2 = tempfile.mkdtemp()
    made.append(d2)
    for nm, body in (("P_Manuscript_Snapshot_r1.md", snapshot), ("P_Findings_Ledger_r1.md", ledger),
                     ("P_Timeline_r1.md", timeline)):
        with open(os.path.join(d2, nm), "w", encoding="utf-8", newline="") as fh:
            fh.write(body)
    build(d2)   # binds r1 (the only snapshot present at build time)
    r2 = os.path.join(d2, "P_Manuscript_Snapshot_r2.md")
    with open(r2, "w", encoding="utf-8", newline="") as fh:
        fh.write(snapshot + "# Chapter 10\nNew material.\n")
    future = os.path.getmtime(os.path.join(d2, "P_Manuscript_Snapshot_r1.md")) + 1000
    os.utime(r2, (future, future))   # force r2 strictly newest, so a newest-glob would mis-pick it
    chk("binding_resolves_bound_not_newest", run([d2])[0] == 0)
    # ...and the sha backstop still catches a genuinely tampered bound snapshot (no silent wrong pass)
    with open(os.path.join(d2, "P_Manuscript_Snapshot_r1.md"), "a", encoding="utf-8", newline="") as fh:
        fh.write("tampered\n")
    chk("binding_sha_mismatch_fails", run([d2])[0] == 1)

    # W1 normalization: a CRLF (non-LF) snapshot is A2-self-consistent but trips the advisory
    snap_crlf = "# Chapter 1\r\nText.\r\n"
    obj_crlf, _ = build_manifest(snap_crlf, "# Ledger\n", None)
    ann_crlf = render(snap_crlf, obj_crlf)
    code, ls = check(snap_crlf, manifest_md(obj_crlf), ann_crlf, "# Ledger\n", None)
    chk("w1_crlf_normalization", code == 0 and any("W1 normalization" in x for x in ls))

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    if len(argv) > 1 and argv[1] == "build":
        rest = [a for a in argv[2:] if not a.startswith("-")]
        if len(rest) != 1 or not os.path.isdir(rest[0]):
            print("Usage: annotation_manifest.py build <run_folder>")
            return 2
        return build(rest[0])
    if len(argv) > 1 and argv[1] == "render":
        rest = argv[2:]
        out = None
        if "-o" in rest:
            i = rest.index("-o")
            out = rest[i + 1] if i + 1 < len(rest) else None
            rest = rest[:i] + rest[i + 2:]
        rest = [a for a in rest if not a.startswith("-")]
        if len(rest) < 2:
            print("Usage: annotation_manifest.py render <manifest> <snapshot> [-o out.md]")
            return 2
        obj, errs = parse_manifest(_read(rest[0]))
        if obj is None:
            print("annotated-manuscript: %s" % (errs[0] if errs else "no manifest"), file=sys.stderr)
            return 1
        try:
            h = render(_read(rest[1]), obj)
        except ValueError as exc:
            print("annotated-manuscript: %s" % exc, file=sys.stderr)
            return 1
        if out:
            with open(out, "w", encoding="utf-8", newline="") as fh:
                fh.write(h)
            print("annotated-manuscript: rendered %s" % out)
        else:
            sys.stdout.write(h)
        return 0
    args = [a for a in argv[1:] if a != "annotated-manuscript"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: annotation_manifest.py annotated-manuscript <run_folder|files...> [--strict] "
              "| build <run_folder> | render <manifest> <snapshot> | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
