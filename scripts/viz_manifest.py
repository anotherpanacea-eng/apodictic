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
  W2 scene order         scenes[] order diverges from the Timeline's document order (the pacing
                         curve's x-axis is scene order — a reordered manifest draws a false shape).
                         Advisory.
  W1 coverage            a Timeline row not represented in scenes[] (silent under-render). Advisory.

The severity->encoding map is HARDCODED in the renderer, never read from the manifest, so a run
cannot recolor a Must-Fix to comfort, and a Must-Fix marker is always drawn at full salience (its
size never shrinks for low confidence). Reuses timeline_checks._parse_event_ledger (the Timeline
column parser) and apodictic_artifacts (block grammar + schema engine). See
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

_SCHEMA_ID = "apodictic.viz_manifest.v1"
_FINDING_SCHEMA_ID = "apodictic.finding.v1"
_MANIFEST_GLOB = "*_Structure_Map_*.md"
_TIMELINE_GLOBS = ("*_Timeline_*.md", "Timeline.md")
_LEDGER_GLOB = "*_Findings_Ledger_*.md"

# The manifest is style-free: these are the ONLY keys each object may carry (E1 allowlist).
_SCENE_KEYS = ("scene_id", "chapter", "line_range", "word_count", "pov", "span", "gap")
_FINDING_KEYS = ("id", "severity", "confidence", "chapter")
_TOP_KEYS = ("schema", "project", "partial", "scenes", "findings")

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
            out[obj["id"]] = obj
    return out


def chapter_of(obj):
    """Conservative chapter bin from a finding's evidence_refs: 'Ch N' or the literal 'unplaced'."""
    for ref in obj.get("evidence_refs") or []:
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


def _check_objects(items, kind, allowed, required):
    """E1 nested-object validation (the subset schema engine can't recurse into array items)."""
    errs = []
    if not isinstance(items, list):
        errs.append("E1 manifest schema: %s must be an array" % kind)
        return errs
    for i, it in enumerate(items):
        where = "%s[%d]" % (kind, i)
        if not isinstance(it, dict):
            errs.append("E1 manifest schema: %s must be an object" % where)
            continue
        for k in required:
            if k not in it:
                errs.append("E1 manifest schema: %s missing required field '%s'" % (where, k))
        for k in it:
            if k not in allowed:
                errs.append("E1 manifest schema: %s has disallowed field '%s' "
                            "(no visual-style fields — style is the renderer's)" % (where, k))
    return errs


def check(manifest_text, timeline_text, ledger_text, strict=False, require_block=False):
    """Run the manifest<->source provenance checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    obj, schema_errs = parse_manifest(manifest_text)
    if obj is None:
        # A present-but-unparseable block is an E1 failure, NOT a no-op — otherwise corrupt JSON
        # passes silently (and the --check-all gate would pass vacuously if the example broke).
        if any("invalid JSON" in e for e in schema_errs):
            return 1, ["manuscript-viz: %s" % schema_errs[0], "manuscript-viz: FAIL (E1 manifest schema)"]
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

    rows = timeline_rows(timeline_text)
    led = ledger_findings(ledger_text)

    # E2 — provenance closure + E4 — byte-equal copy fidelity (scenes)
    for sc in scenes:
        if not isinstance(sc, dict):
            continue
        sid = sc.get("scene_id")
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
        fid = fd.get("id")
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
    manifest_ids = {fd.get("id") for fd in findings if isinstance(fd, dict)}
    for fid, src in sorted(led.items()):
        if src.get("severity") == "Must-Fix" and fid not in manifest_ids:
            errs.append("E3 Must-Fix completeness: ledger Must-Fix %s is absent from findings[] "
                        "(the render cannot drop a locked severity)" % fid)

    # W1 — coverage: a Timeline row not represented in scenes[]
    scene_ids = {sc.get("scene_id") for sc in scenes if isinstance(sc, dict)}
    for sid in sorted(rows):
        if sid not in scene_ids:
            warns.append("W1 coverage: Timeline scene %s is not in scenes[] (silent under-render)" % sid)

    # W2 — scene order: the manifest scenes[] order should follow the Timeline's document order. The
    # pacing curve's x-axis is raw scenes[] order, so a reordered manifest draws a false pacing shape
    # while passing every per-id check (order is a data channel the set-based checks don't close).
    mf_order = [sc.get("scene_id") for sc in scenes
                if isinstance(sc, dict) and sc.get("scene_id") in rows]
    tl_subset = [sid for sid in rows if sid in set(mf_order)]   # rows preserves Timeline document order
    if mf_order != tl_subset:
        warns.append("W2 scene order: scenes[] order diverges from the Timeline document order "
                     "(%s vs %s) — the pacing curve's shape must come from the Timeline, not the manifest"
                     % (" ".join(map(str, mf_order)), " ".join(map(str, tl_subset))))

    # Report
    lines.append("manuscript-viz: %s — %d scene(s), %d finding(s)%s"
                 % (obj.get("project", "?"), len(scenes), len(findings),
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
        lines.append("WARN: manuscript-viz: %d coverage gap(s) — see W1 above" % len(warns))
    else:
        lines.append("manuscript-viz: PASS (manifest<->source provenance: schema + closure + Must-Fix + verbatim copy)")
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


def render_html(manifest_text, timeline_text, ledger_text):
    """Pure function of the manifest (+ verbatim sources): a self-contained HTML+inline-SVG file.

    No network, no deps, no model call — render-only. Charts 1-3: pacing curve, POV time-share,
    finding-severity-by-chapter. Severity encoding is hardcoded here, not read from the manifest."""
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
    return """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1">
<title>Structure Map — {project}</title>
<style>
 body{{font-family:system-ui,sans-serif;background:#EDE5D0;color:#33311E;max-width:760px;margin:0 auto;padding:2rem 1.5rem;line-height:1.6}}
 h1{{font-size:1.4rem;margin:0 0 .25rem}} h2{{font-size:1.05rem;margin:2rem 0 .5rem;border-bottom:1px solid #D1C8AC;padding-bottom:.3rem}}
 .meta{{color:#7A7560;font-size:.85rem;margin-bottom:1rem}} .partial{{color:#8C2A3D;font-size:.9rem}}
 .record{{background:#F4EDDA;border-left:3px solid #8B5E3C;padding:.6rem .9rem;font-size:.85rem;border-radius:0 4px 4px 0}}
 .legend{{font-size:.8rem;color:#7A7560;margin:.4rem 0}} svg{{max-width:100%}}
</style></head><body>
<h1>Structure Map — {project}</h1>
<div class=meta>Render-only companion · APODICTIC manuscript-structure visualization (charts 1–3)</div>
<div class=record><strong>The editorial letter is the artifact of record.</strong> This is a render of data the
passes already produced — it adds no analysis and no verdict lives only here. Severity encoding is fixed:
a Must-Fix is always rendered at full salience (size never shrinks for low confidence).</div>
{partial_note}
<h2>Pacing — word count by scene</h2>{c1}
<h2>POV time-share</h2>{c2}
<h2>Findings by chapter</h2><div class=legend>{legend}</div>{c3}
</body></html>""".format(project=project, partial_note=partial_note,
                         c1=_bars_svg(pacing), c2=_bars_svg(pov), c3=_bars_svg(sev_bars), legend=legend)


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    """Return (manifest_path, timeline_path, ledger_path) from a run folder or explicit files."""
    if len(paths) == 1 and os.path.isdir(paths[0]):
        d = paths[0]
        man = _newest(glob.glob(os.path.join(d, _MANIFEST_GLOB)))
        tlp = None
        for g in _TIMELINE_GLOBS:
            tlp = _newest(glob.glob(os.path.join(d, g)))
            if tlp:
                break
        led = _newest(glob.glob(os.path.join(d, _LEDGER_GLOB)))
        return man, tlp, led
    man = tlp = led = None
    for p in paths:
        body = _read(p) or ""
        if "apodictic:viz_manifest" in body and man is None:
            man = p
        elif "scene id" in body.lower() and "|" in body and tlp is None:
            tlp = p
        elif "apodictic:finding" in body and led is None:
            led = p
    if man is None and paths:
        man = paths[0]
    return man, tlp, led


def run(paths, strict=False, require_block=False):
    man, tlp, led = resolve(paths)
    if not man:
        return 2, ["manuscript-viz: no Structure Map manifest found (need a *_Structure_Map_*.md "
                   "or a file with an apodictic:viz_manifest block)"]
    mtext = _read(man)
    if mtext is None:
        return 2, ["manuscript-viz: cannot read %s" % man]
    return check(mtext, _read(tlp) if tlp else None, _read(led) if led else None,
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
    with open(os.path.join(d, "Proj_Timeline_run.md"), "w") as fh:
        fh.write(timeline)
    with open(os.path.join(d, "Proj_Findings_Ledger_run.md"), "w") as fh:
        fh.write(ledger)
    with open(os.path.join(d, "Proj_Structure_Map_run.md"), "w") as fh:
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
    with open(tlp, "w") as fh: fh.write(timeline)
    with open(ldp, "w") as fh: fh.write(ledger)
    with open(rev_man, "w") as fh: fh.write(manifest(scenes=rev_scenes))
    with open(ok_man, "w") as fh: fh.write(manifest())
    chk("render_refuses_reordered", main(["x", "render", rev_man, tlp, ldp, "-o", out]) == 1)
    chk("render_force_reordered", main(["x", "render", rev_man, tlp, ldp, "-o", out, "--force"]) == 0)
    chk("render_in_order_ok", main(["x", "render", ok_man, tlp, ldp, "-o", out]) == 0)

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
            print("Usage: viz_manifest.py render <manifest> [timeline] [ledger] [-o out.html] [--force]")
            return 2
        man, tlp, led = resolve(rest) if len(rest) == 1 and os.path.isdir(rest[0]) else (
            rest[0], rest[1] if len(rest) > 1 else None, rest[2] if len(rest) > 2 else None)
        mtext = _read(man)
        tltext = _read(tlp) if tlp else None
        ledtext = _read(led) if led else None
        # Gate before rendering: rendering un-provenanced data is exactly the firewall hole the
        # validator exists to prevent. Refuse on an ERROR-level gate failure, OR on a scene-order
        # divergence — W2 is advisory in general, but a reordered manifest draws a FALSE pacing curve
        # (the one warning that corrupts the render's core output), so it blocks the render too.
        # W1 coverage stays advisory: a legitimate partial map still renders.
        gcode, glines = check(mtext, tltext, ledtext, require_block=True)
        scene_order_broken = any("W2 scene order" in ln for ln in glines)
        if (gcode != 0 or scene_order_broken) and not force:
            for ln in glines:
                print(ln, file=sys.stderr)
            print("manuscript-viz: refusing to render — the manifest fails the provenance gate or "
                  "reorders scenes vs the Timeline (a false pacing curve). Pass --force to override. "
                  "See above.", file=sys.stderr)
            return 1
        h = render_html(mtext, tltext, ledtext)
        if out:
            with open(out, "w", encoding="utf-8") as fh:
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
