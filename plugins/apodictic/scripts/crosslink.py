#!/usr/bin/env python3
"""crosslink — letter <-> margin bidirectional cross-links (Annotated-Manuscript Increment 3).

`validate.sh crosslink <run_folder> [--strict]` shells out here. Increments 1-2 made the margin->letter
direction real (each margin comment ends "(See letter §F-...)"). This adds letter->margin: a crosslink
render injects a CriticMarkup back-link span immediately after each editorial-letter `<!-- finding: F-... -->`
marker whose finding has a manifest annotation, pointing at that finding's manuscript anchor:

    {>>→ marked-up copy: <finding_id> @ <anchor.kind>:<anchor.value><<}

The anchor (kind:value) and the id are copied VERBATIM from the gated annotation manifest; the render
authors nothing. The letter is treated as a "second snapshot": the SAME reverse transform (delete every
{>> ... <<} span) proves no letter mutation, behind the SAME two-sided sigil precondition (the letter
must not already contain a CriticMarkup sigil). The crosslinked letter is a derived companion; the letter
of record is never touched.

Validator (`crosslink`):
  X1 forward link    each manifest annotation's comment carries "(See letter §<id>)" (margin->letter).
  X2 reverse consist for each `finding:` marker of an annotated finding, a back-link carries that id and
                     an anchor string == "<kind>:<value>" from the manifest (no drift).
  X3 no dangling     every back-link id resolves to a manifest annotation (no phantom), and every
                     marker-of-an-annotated-finding has its back-link (no missing reverse link), by count.
  W1 uncited         a finding annotated but not cited by any letter `finding:` marker (advisory; ERROR
                     under --strict; override `<!-- override: crosslink-uncited F-... -->`).
  X4 no mutation     letter has no {>>/<<} sigil (precondition) AND reverse_transform(crosslinked)==letter.

Reuses annotation_manifest (reverse_transform + sigil constants + parse_manifest + comment_for) and
finding_trace (editorial-letter globs). The `<!-- finding: F-... -->` marker parser and the back-link
parser are NEW. See docs/annotated-manuscript.md (§Increment 3).

  crosslink.py crosslink <run_folder|files...> [--strict]
  crosslink.py render <run_folder>   |   render <letter> <manifest> [-o out.md]
  crosslink.py build <run_folder>    # alias for render that writes the crosslinked letter
  crosslink.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import json
import os
import re
import sys

try:
    import annotation_manifest as am
except ImportError:
    am = None
try:
    import finding_trace as ft
except ImportError:
    ft = None

_MANIFEST_GLOB = "*_Annotation_Manifest_*.md"
_CROSSLINKED_GLOB = "*_Crosslinked_Letter_*.md"
# Editorial-letter globs (mirror finding_trace's letter set; redeclared so a missing ft still resolves).
_LETTER_GLOBS = ("*_Core_DE_Synthesis_*.md", "*_Full_DE_*.md", "*_Editorial_Letter_*.md")

# The letter's per-finding citation marker (the injection target). NB this is the `finding:` marker
# specifically — NOT every F-id in an HTML comment (finding_trace.letter_cited_ids also returns
# severity_calibration ids); crosslink keys on the finding: marker set.
_FINDING_MARKER_RE = re.compile(r"<!--\s*finding:\s*(F-[A-Za-z0-9]+-[0-9]{2,})\s*-->")
# The back-link span: {>>→ marked-up copy: <fid> @ <kind>:<value><<}. The id makes it self-describing
# (matched by id, not position); `@` separates it from the verbatim kind:value (which may hold ':' '-'
# spaces '§' or be empty for `document`). Non-greedy stops at the first <<} (anchor values are sigil-safe).
_BACKLINK_RE = re.compile(r"\{>>→ marked-up copy: (F-[A-Za-z0-9]+-[0-9]{2,}) @ (.*?)<<\}", re.DOTALL)
_OVERRIDE_RE = re.compile(r"<!--\s*override:\s*crosslink-uncited\s+(F-[A-Za-z0-9]+-[0-9]{2,})", re.IGNORECASE)
# Any CriticMarkup span (the shared grammar; mirrors annotation_manifest._CM_SPAN_RE). Used to enumerate
# EVERY span so an authored/non-back-link span can't ride through X4's reverse transform. Fallback only
# when annotation_manifest isn't importable; otherwise am._CM_SPAN_RE is used.
_CM_SPAN_RE_FALLBACK = re.compile(r"\{>>.*?<<\}", re.DOTALL)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _sigils():
    return (am._CM_OPEN, am._CM_CLOSE) if am is not None else ("{>>", "<<}")


def _anchor_str(anchor):
    """The verbatim '<kind>:<value>' embedded in a back-link (value may be empty for `document`)."""
    a = anchor or {}
    return "%s:%s" % (a.get("kind", ""), a.get("value", ""))


def backlink_span(fid, anchor):
    o, c = _sigils()
    return "%s→ marked-up copy: %s @ %s%s" % (o, fid, _anchor_str(anchor), c)


def manifest_anchors(manifest_text):
    """{finding_id: annotation-dict} from the annotation manifest (Increment 1-2)."""
    out = {}
    if am is None or not manifest_text:
        return out
    obj, _errs = am.parse_manifest(manifest_text)
    if not isinstance(obj, dict):
        return out
    for an in obj.get("annotations") or []:
        if isinstance(an, dict) and an.get("finding_id"):
            out[an["finding_id"]] = an
    return out


# ---------------------------------------------------------------- render

def render(letter, anchors):
    """Inject a back-link span after each `<!-- finding: F-id -->` marker whose finding is annotated.

    `anchors`: {finding_id: annotation-dict}. Raises ValueError on the two-sided sigil precondition
    (the letter must not already contain a CriticMarkup sigil — else the reverse transform would not be
    reversible and would silently delete the author's own span). Spans are spliced in DESCENDING offset
    order (the Increment-2 renderer's rule) so insertions never perturb later offsets, and always land
    AFTER the marker's `-->`, never inside the comment."""
    o, c = _sigils()
    if o in letter or c in letter:
        raise ValueError("letter already contains a CriticMarkup sigil ({>> or <<}) — the reverse "
                         "transform would not be reversible; escape the letter first")
    inserts = []   # (end_offset, marker_index, span)
    for i, m in enumerate(_FINDING_MARKER_RE.finditer(letter)):
        an = anchors.get(m.group(1))
        if an is None:
            continue
        inserts.append((m.end(), i, backlink_span(m.group(1), an.get("anchor") or {})))
    out = letter
    for off, _i, span in sorted(inserts, key=lambda t: (t[0], t[1]), reverse=True):
        out = out[:off] + span + out[off:]
    return out


# ---------------------------------------------------------------- validator

def check(letter_text, crosslinked_text, manifest_text, strict=False):
    """Run X1-X4 + W1. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    anchors = manifest_anchors(manifest_text)
    if not anchors:
        return 0, ["crosslink: no annotation manifest / annotations resolved — nothing to cross-link"]
    if letter_text is None or crosslinked_text is None:
        miss = " + ".join(n for n, t in (("editorial letter", letter_text),
                                          ("crosslinked letter", crosslinked_text)) if t is None)
        return 2, ["crosslink: need an editorial letter AND a crosslinked letter (missing %s)" % miss]
    o, c = _sigils()

    # X1 — forward link: each annotation's comment carries the (See letter §<id>) margin->letter link
    for fid, an in sorted(anchors.items()):
        tail = "(See letter §%s.)" % fid
        if tail not in str(an.get("comment", "")):
            errs.append("X1 forward link: annotation %s comment lacks the margin->letter link '%s'"
                        % (fid, tail))

    marker_fids = _FINDING_MARKER_RE.findall(letter_text)
    marker_count = {}
    for f in marker_fids:
        marker_count[f] = marker_count.get(f, 0) + 1

    # X3 marker integrity — the injected spans must not have CORRUPTED any finding marker (e.g. a span
    # buried inside `<!-- finding: F-… {>>…<<}-->` reverses cleanly under X4 but breaks navigation). The
    # crosslinked letter's `finding:` markers, in order, must equal the letter's.
    crl_markers = [(m.group(1), m.end()) for m in _FINDING_MARKER_RE.finditer(crosslinked_text)]
    if [f for f, _e in crl_markers] != marker_fids:
        errs.append("X3 marker integrity: the crosslinked letter's `finding:` markers differ from the "
                    "letter's — a back-link span was injected inside (not after) a <!-- finding: --> marker")

    # X2/X3 POSITIONAL pairing — enumerate EVERY CriticMarkup span (not just back-link-shaped ones):
    # each must be a well-formed back-link sitting in the bytes IMMEDIATELY AFTER a marker's `-->`
    # (start == that marker's end), carrying that marker's id, resolving to a manifest annotation, and
    # matching its anchor. Iterating the SHARED span regex (not `_BACKLINK_RE`) is the firewall fix: an
    # authored / malformed `{>> ... <<}` span would otherwise ride through X4 (which deletes ALL spans
    # before the reverse-transform compare) un-noticed (Codex #103 review). This also catches swapped /
    # mis-attributed back-links, orphan/in-prose/doubled spans, phantoms, and drift.
    cm_span = am._CM_SPAN_RE if am is not None else _CM_SPAN_RE_FALLBACK
    marker_end_fid = {e: f for f, e in crl_markers}
    paired = {}   # fid -> count of correctly-placed back-links
    for sm in cm_span.finditer(crosslinked_text):
        bm = _BACKLINK_RE.fullmatch(sm.group())
        bstart = sm.start()
        if bm is None:
            errs.append("X3 un-manifested span: a CriticMarkup span in the crosslinked letter is not a "
                        "valid manifest back-link (authored or malformed) — %r" % (sm.group()[:60]))
            continue
        bl_fid, bl_anchor = bm.group(1), bm.group(2)
        if bstart not in marker_end_fid:
            errs.append("X3 misplaced back-link: a %s back-link is not immediately after a `finding:` "
                        "marker (orphan / in-prose / doubled)" % bl_fid)
            continue
        mk_fid = marker_end_fid[bstart]
        if bl_fid != mk_fid:
            errs.append("X2 mis-attributed back-link: the back-link after the %s marker carries %s "
                        "(swapped / wrong finding)" % (mk_fid, bl_fid))
            continue
        if bl_fid not in anchors:
            errs.append("X3 phantom back-link: %s has a back-link but no manifest annotation" % bl_fid)
            continue
        want = _anchor_str(anchors[bl_fid].get("anchor"))
        if bl_anchor != want:
            errs.append("X2 anchor drift: back-link %s points at %r but the manifest anchor is %r"
                        % (bl_fid, bl_anchor, want))
            continue
        paired[bl_fid] = paired.get(bl_fid, 0) + 1
    # X3 missing — each annotated finding cited by N markers needs N correctly-paired back-links
    for fid in sorted(anchors):
        if marker_count.get(fid, 0) > paired.get(fid, 0):
            errs.append("X3 missing reverse link: %s is cited by %d letter marker(s) but has %d correctly-"
                        "placed back-link(s)" % (fid, marker_count[fid], paired.get(fid, 0)))

    # W1 — annotated but not cited by any letter finding: marker (advisory; override-able)
    overrides = set(_OVERRIDE_RE.findall(crosslinked_text)) | set(_OVERRIDE_RE.findall(letter_text))
    for fid in sorted(anchors):
        if marker_count.get(fid, 0) == 0 and fid not in overrides:
            warns.append("W1 uncited: %s is annotated but not cited by any letter `finding:` marker" % fid)

    # X4 — no letter mutation: two-sided sigil precondition on the LETTER + reverse-transform identity
    if o in letter_text or c in letter_text:
        errs.append("X4 no letter mutation: the LETTER already contains a CriticMarkup sigil ({>> or <<}) "
                    "— the reverse transform is not reversible; escape the letter first")
    elif am is not None and am.reverse_transform(crosslinked_text) != letter_text:
        errs.append("X4 no letter mutation: deleting every {>> ... <<} span from the crosslinked letter "
                    "does NOT reproduce the letter byte-for-byte (prose altered, or a span is malformed)")

    lines.append("crosslink: %d annotation(s), %d letter `finding:` marker(s), %d back-link(s)"
                 % (len(anchors), len(marker_fids), len(_BACKLINK_RE.findall(crosslinked_text))))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))
    if errs or (strict and warns):
        lines.append("crosslink: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: crosslink: %d advisory flag(s) — see W1 above" % len(warns))
    else:
        lines.append("crosslink: PASS (bidirectional integrity + no letter mutation)")
    return 0, lines


# ---------------------------------------------------------------- resolution + CLIs

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve_run_folder(folder):
    man = _newest(glob.glob(os.path.join(folder, _MANIFEST_GLOB)))
    crl = _newest(glob.glob(os.path.join(folder, _CROSSLINKED_GLOB)))
    letter = None
    for g in _LETTER_GLOBS:
        letter = _newest(glob.glob(os.path.join(folder, g)))
        if letter:
            break
    return letter, crl, man


def classify_files(paths):
    letter = crl = man = None
    for p in paths:
        base = os.path.basename(p)
        body = _read(p) or ""
        if "_Annotation_Manifest_" in base or "apodictic:annotation" in body:
            man = p
        elif "_Crosslinked_Letter_" in base or "→ marked-up copy:" in body:
            crl = p
        else:
            letter = p
    return letter, crl, man


def run(paths, strict=False):
    if len(paths) == 1 and os.path.isdir(paths[0]):
        letter, crl, man = resolve_run_folder(paths[0])
    else:
        letter, crl, man = classify_files(paths)
    if not man:
        return 2, ["crosslink: no annotation manifest found (need a *_Annotation_Manifest_*.md or a "
                   "file with an apodictic:annotation block)"]
    return check(_read(letter) if letter else None, _read(crl) if crl else None, _read(man), strict=strict)


def _crosslinked_name(letter_path):
    """`<Project>_Crosslinked_Letter_<runlabel>.md` derived from the letter filename."""
    base = os.path.basename(letter_path)
    stem = os.path.splitext(base)[0]
    parts = stem.split("_")
    project = parts[0] if parts else "Letter"
    runlabel = parts[-1] if len(parts) > 1 else "run"
    return "%s_Crosslinked_Letter_%s.md" % (project, runlabel)


def build(folder):
    """Render the crosslinked letter from the run folder's editorial letter + annotation manifest."""
    letter, _crl, man = resolve_run_folder(folder)
    if not letter or not man:
        print("crosslink: need both an editorial letter and an annotation manifest in %s" % folder,
              file=sys.stderr)
        return 2
    anchors = manifest_anchors(_read(man))
    try:
        crosslinked = render(_read(letter), anchors)
    except ValueError as exc:
        print("crosslink: %s" % exc, file=sys.stderr)
        return 1
    out = os.path.join(folder, _crosslinked_name(letter))
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(crosslinked)
    print("crosslink: wrote %s" % os.path.basename(out))
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

    def comment(fid):
        return "[Must-Fix · %s] m — fix class: f. (See letter §%s.)" % (fid, fid)

    def manifest_md(annos):
        obj = {"schema": "apodictic.annotation.v1", "project": "T", "runlabel": "r",
               "snapshot_path": "s.md", "snapshot_sha256": "0" * 64, "snapshot_line_count": 1,
               "annotations": annos}
        return "# Manifest\n<!-- apodictic:annotation\n%s\n-->\n" % json.dumps(obj)

    annos = [
        {"finding_id": "F-A-01", "anchor": {"kind": "chapter", "value": "Ch 9"}, "comment": comment("F-A-01")},
        {"finding_id": "F-B-01", "anchor": {"kind": "quote", "value": "10-20"}, "comment": comment("F-B-01")},
        {"finding_id": "F-D-01", "anchor": {"kind": "document", "value": ""}, "comment": comment("F-D-01")},
    ]
    manifest = manifest_md(annos)
    anchors = manifest_anchors(manifest)
    chk("manifest_parsed", set(anchors) == {"F-A-01", "F-B-01", "F-D-01"})

    # A letter citing F-A-01 (twice), F-B-01, F-D-01 via finding: markers
    letter = ("# Editorial Letter\n## What Needs Work\n"
              "Pacing collapses at Chapter 9. <!-- finding: F-A-01 -->\n"
              "The dialogue goes flat. <!-- finding: F-B-01 -->\n"
              "(Again, the pacing.) <!-- finding: F-A-01 -->\n"
              "A soft genre signal. <!-- finding: F-D-01 -->\n")

    crosslinked = render(letter, anchors)
    chk("render_reverses", am.reverse_transform(crosslinked) == letter)
    chk("render_backlink_count", len(_BACKLINK_RE.findall(crosslinked)) == 4)   # F-A-01 x2, F-B-01, F-D-01
    chk("render_doc_empty_value", "@ document:<<}".replace("<<}", am._CM_CLOSE) in crosslinked)
    chk("render_after_marker", "<!-- finding: F-A-01 -->{>>→ marked-up copy: F-A-01 @ chapter:Ch 9<<}"
        .replace("{>>", am._CM_OPEN).replace("<<}", am._CM_CLOSE) in crosslinked)

    # clean validate
    code, ls = check(letter, crosslinked, manifest)
    chk("clean_validate", code == 0)

    # X4 — mutate one prose char in the crosslinked letter
    code, ls = check(letter, crosslinked.replace("flat.", "flat!!"), manifest)
    chk("x4_mutation", code == 1 and any("X4 no letter mutation" in x for x in ls))

    # X4 / precondition — a letter that already contains a sigil
    sigil_letter = "# L\nAn aside {>>not ours<<} here. <!-- finding: F-A-01 -->\n".replace("{>>", am._CM_OPEN).replace("<<}", am._CM_CLOSE)
    chk("render_refuses_sigil_letter", _render_raises(sigil_letter, anchors))
    code, ls = check(sigil_letter, sigil_letter, manifest)
    chk("x4_letter_sigil_precondition", code == 1 and any("already contains a CriticMarkup sigil" in x for x in ls))

    # X2 — anchor drift: a back-link whose anchor != manifest
    drift = crosslinked.replace("F-A-01 @ chapter:Ch 9", "F-A-01 @ chapter:Ch 3", 1)
    code, ls = check(letter, drift, manifest)
    chk("x2_anchor_drift", code == 1 and any("X2 anchor drift" in x and "F-A-01" in x for x in ls))

    # X3 — missing reverse link (a cited annotated finding with no back-link)
    missing = _BACKLINK_RE.sub("", crosslinked, count=1)   # drop the first back-link (an F-A-01 one)
    code, ls = check(letter, missing, manifest)
    chk("x3_missing", code == 1 and any("X3 missing reverse link" in x for x in ls))

    bl_b = "%s→ marked-up copy: F-B-01 @ quote:10-20%s" % (am._CM_OPEN, am._CM_CLOSE)
    bl_d = "%s→ marked-up copy: F-D-01 @ document:%s" % (am._CM_OPEN, am._CM_CLOSE)
    # X2 — SWAPPED back-links: the F-B-01 marker followed by F-D-01's back-link and vice-versa. Each
    # back-link is globally self-consistent (right id+anchor), so only the POSITIONAL pairing catches it.
    swapped = crosslinked.replace("F-B-01 -->" + bl_b, "F-B-01 -->" + bl_d).replace("F-D-01 -->" + bl_d, "F-D-01 -->" + bl_b)
    code, ls = check(letter, swapped, manifest)
    chk("x2_swapped", code == 1 and any("X2 mis-attributed" in x for x in ls))
    # X3 — a back-link injected INSIDE the marker reverses cleanly under X4 but breaks the marker
    in_comment = crosslinked.replace("<!-- finding: F-B-01 -->" + bl_b, "<!-- finding: F-B-01 " + bl_b + "-->")
    code, ls = check(letter, in_comment, manifest)
    chk("x3_in_comment", code == 1 and any("marker integrity" in x or "misplaced" in x for x in ls))
    chk("x3_in_comment_x4_blind", am.reverse_transform(in_comment) == letter)   # X4 alone would not catch it
    # X3 — misplaced back-link (appended in prose, not after a marker)
    misplaced = crosslinked + bl_b
    code, ls = check(letter, misplaced, manifest)
    chk("x3_misplaced", code == 1 and any("X3 misplaced" in x for x in ls))
    # X3 — an AUTHORED (non-back-link) CriticMarkup span rides through X4 (deletes all spans) unless we
    # enumerate EVERY span and reject non-back-links (Codex #103 firewall finding).
    authored = crosslinked + ("%sAUTHORED EXTRA NOTE%s" % (am._CM_OPEN, am._CM_CLOSE))
    code, ls = check(letter, authored, manifest)
    chk("x3_authored_span", code == 1 and any("X3 un-manifested span" in x for x in ls))
    chk("x3_authored_span_x4_blind", am.reverse_transform(authored) == letter)   # X4 alone misses it
    # X3 — a PHANTOM back-link: after a marker for a finding with no manifest annotation
    letter_ph = letter + "An unannotated finding. <!-- finding: F-Z-99 -->\n"
    crl_ph = letter_ph.replace("<!-- finding: F-Z-99 -->",
                               "<!-- finding: F-Z-99 -->%s→ marked-up copy: F-Z-99 @ chapter:Ch 1%s"
                               % (am._CM_OPEN, am._CM_CLOSE))
    code, ls = check(letter_ph, crl_ph, manifest)
    chk("x3_phantom", code == 1 and any("X3 phantom" in x and "F-Z-99" in x for x in ls))

    # W1 — annotated but uncited (F-D-01 not cited)
    letter_no_d = letter.replace("A soft genre signal. <!-- finding: F-D-01 -->\n", "")
    crl_no_d = render(letter_no_d, anchors)
    code, ls = check(letter_no_d, crl_no_d, manifest)
    chk("w1_uncited_advisory", code == 0 and any("W1 uncited" in x and "F-D-01" in x for x in ls))
    chk("w1_uncited_strict_fails", check(letter_no_d, crl_no_d, manifest, strict=True)[0] == 1)
    # ...silenced by an override marker carried in the letter (and so in the crosslinked letter)
    letter_ovr = letter_no_d + "<!-- override: crosslink-uncited F-D-01 -->\n"
    crl_ovr = render(letter_ovr, anchors)
    code, ls = check(letter_ovr, crl_ovr, manifest)
    chk("w1_override", code == 0 and not any("W1 uncited" in x for x in ls))

    # X1 — a manifest comment missing the (See letter §id) link
    annos_bad = json.loads(json.dumps(annos))
    annos_bad[0]["comment"] = "[Must-Fix · F-A-01] m — fix class: f."   # dropped the link tail
    code, ls = check(letter, crosslinked, manifest_md(annos_bad))
    chk("x1_missing_forward_link", code == 1 and any("X1 forward link" in x and "F-A-01" in x for x in ls))

    # resolution — a run folder
    d = tempfile.mkdtemp()
    made.append(d)
    with open(os.path.join(d, "Example_Annotation_Manifest_r.md"), "w") as fh:
        fh.write(manifest)
    with open(os.path.join(d, "Example_Editorial_Letter_r.md"), "w") as fh:
        fh.write(letter)
    chk("build_writes_crosslinked", build(d) == 0)
    chk("run_folder_validates", run([d])[0] == 0)
    chk("missing_manifest_usage", run([d + "/nope"])[0] == 2)

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def _render_raises(letter, anchors):
    try:
        render(letter, anchors)
        return False
    except ValueError:
        return True


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    if len(argv) > 1 and argv[1] in ("render", "build"):
        rest = argv[2:]
        out = None
        if "-o" in rest:
            i = rest.index("-o")
            out = rest[i + 1] if i + 1 < len(rest) else None
            rest = rest[:i] + rest[i + 2:]
        rest = [a for a in rest if not a.startswith("-")]
        if len(rest) == 1 and os.path.isdir(rest[0]):
            return build(rest[0])
        if len(rest) < 2:
            print("Usage: crosslink.py render <run_folder> | render <letter> <manifest> [-o out.md]")
            return 2
        anchors = manifest_anchors(_read(rest[1]))
        try:
            h = render(_read(rest[0]), anchors)
        except ValueError as exc:
            print("crosslink: %s" % exc, file=sys.stderr)
            return 1
        if out:
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(h)
            print("crosslink: rendered %s" % out)
        else:
            sys.stdout.write(h)
        return 0
    args = [a for a in argv[1:] if a != "crosslink"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: crosslink.py crosslink <run_folder|files...> [--strict] | render ... | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
