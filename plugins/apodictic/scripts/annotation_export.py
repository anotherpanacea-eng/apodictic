#!/usr/bin/env python3
"""annotation-export — render the gated annotation manifest into other formats. Increment 1: Obsidian.

`manifest + snapshot → Obsidian-native Markdown`: each finding becomes a native footnote `[^<finding_id>]`
at its anchor locus, whose definition carries the **verbatim** manifest comment. No plugin (Obsidian
renders footnotes natively; CriticMarkup needs one). A pure projection of the gated manifest — it invents
nothing; the reverse transform (delete the manifest-keyed `[^id]` refs + the trailing definition block)
reproduces the snapshot byte-for-byte (the A2 discipline). The Obsidian copy is built from the SNAPSHOT
(clean ATX headings), not the CriticMarkup annotated copy.

Validator (`obsidian-export <run_folder>`):
  O1 (ERROR) round-trip — manifest-keyed, two-sided. Precondition: the snapshot and every comment are free
     of the footnote-ref sigil '[^' and no snapshot line is footnote-definition-shaped. Round-trip: strip
     the exact `[^<finding_id>]` refs (manifest id set, never a wildcard) + the trailing `[^<id>]:` block
     → snapshot byte-for-byte.
  O2 (ERROR) footnote resolution — every `[^id]` ref has exactly one definition and vice versa; the id set
     equals the manifest's annotation finding_ids (the A4 forward+inverse multiset, on footnotes).
  O3 (ERROR) comment fidelity — each definition body equals its manifest comment byte-for-byte (the A5
     analog: relocate, never re-author).

Usage:
  annotation_export.py obsidian <run_folder>          # writes obsidian/<Project>_..._Obsidian_...md
  annotation_export.py obsidian-export <run_folder> [--strict]   # validate (O1-O3), print
  annotation_export.py --self-test
Exit: 0 clean, 1 ERROR, 2 usage.
"""
import glob
import os
import re
import sys

try:
    import annotation_manifest as am
except ImportError:
    am = None

_FN_REF = "[^"                                          # footnote-ref sigil (the two-sided precondition)
_FN_DEF_RE = re.compile(r"^\[\^[^\]]+\]:")             # a footnote-definition-shaped line
# The trailing definition block: a separator newline + one-or-more `[^id]: …` lines to end of text.
_DEF_BLOCK_RE = re.compile(r"\n(?:\[\^[^\]]+\]:[^\n]*\n)+\Z")

# Increment 2 (letter cross-links).
_CROSSLINKED_GLOB = "*_Crosslinked_Letter_*.md"
_FINDING_MARKER_RE = re.compile(r"<!--\s*finding:\s*(F-[A-Za-z0-9]+-[0-9]{2,})\s*-->")
_CM_SPAN_RE = re.compile(r"\{>>.*?<<\}", re.DOTALL)    # a CriticMarkup span (the crosslinked back-link)
_WIKILINK_RE = re.compile(r"\[\[[^\]]*\]\]")           # an Obsidian wikilink (added by Inc 2)
_WIKILINK_SIGIL = "[["                                 # the O5 two-sided precondition sigil


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def _insertion_offset(anchor, snapshot, nl_at, chap_l, sec_l):
    """The character offset a footnote ref is spliced at — mirroring annotation_manifest.render:
    quote → end offset; chapter/section/line-range → end of the anchored line; document → end of line 1."""
    kind = anchor.get("kind")
    if kind == "quote":
        m = re.match(r"(\d+)-(\d+)$", str(anchor.get("value", "")))
        return int(m.group(2)) if m else 0
    if kind == "document":
        return nl_at.get(1, len(snapshot))
    line = am.anchor_line(anchor, snapshot, chap_l, sec_l)
    return nl_at.get(1, len(snapshot)) if line is None else nl_at.get(line, len(snapshot))


def _fwd_wikilink(letter_basename, fid):
    """The exact forward wikilink appended to a copy footnote definition (Increment 2)."""
    return " [[%s#^%s|→ letter §%s]]" % (letter_basename, fid, fid)


def build_obsidian(manifest_obj, snapshot, letter_basename=None):
    """-> (obsidian_text_or_None, errs). Pure projection of the gated manifest; errs is the O1 precondition.
    When letter_basename is set (Increment 2), each footnote definition appends a forward wikilink to the
    letter entry — the verbatim comment is unchanged; only the exact wikilink is added."""
    annotations = manifest_obj.get("annotations") if isinstance(manifest_obj.get("annotations"), list) else []
    errs = []
    # O1 precondition (two-sided, mirroring render/A2): no footnote sigil in the snapshot or any comment,
    # and no snapshot line already shaped like a footnote definition (else the reverse transform is ambiguous).
    if _FN_REF in snapshot:
        errs.append("O1 precondition: the snapshot already contains a footnote-ref sigil '[^' — the reverse "
                    "transform would not be reversible")
    for ln in snapshot.split("\n"):
        if _FN_DEF_RE.match(ln):
            errs.append("O1 precondition: the snapshot contains a footnote-definition-shaped line: %r" % ln[:50])
            break
    for an in annotations:
        if not isinstance(an, dict):
            continue
        c = an.get("comment") or ""
        if _FN_REF in c:
            errs.append("O1 precondition: comment for %s contains '[^'" % an.get("finding_id"))
        if "\n" in c or "\r" in c:
            errs.append("O1 precondition: comment for %s is multi-line — a footnote definition is one "
                        "line (the trailing-block round-trip would break)" % an.get("finding_id"))
    if errs:
        return None, errs
    if not annotations:
        return snapshot, []   # nothing to annotate — the copy IS the snapshot

    chap_n, sec_n, chap_l, sec_l = am.heading_index(snapshot)
    nl_at, ln = {}, 1
    for i, ch in enumerate(snapshot):
        if ch == "\n":
            nl_at[ln] = i
            ln += 1

    # Splice refs in DESCENDING (offset, finding_id) so each insertion sits to the right of every
    # not-yet-inserted one (never perturbing offsets); co-located refs end up adjacent ([^A][^B]),
    # which renders in Reading view and round-trips exactly (no inserted separator to strip).
    inserts = [(_insertion_offset(an.get("anchor") or {}, snapshot, nl_at, chap_l, sec_l), an.get("finding_id"))
               for an in annotations if isinstance(an, dict)]
    out = snapshot
    for off, fid in sorted(inserts, key=lambda t: (t[0], t[1] or ""), reverse=True):
        off = max(0, min(off, len(out)))
        out = out[:off] + ("[^%s]" % fid) + out[off:]

    # Definition block (deterministic: sorted by finding_id), each line the VERBATIM manifest comment,
    # plus (Inc 2) the exact forward wikilink to the letter entry.
    def _def(an):
        fid = an.get("finding_id")
        tail = _fwd_wikilink(letter_basename, fid) if letter_basename else ""
        return "[^%s]: %s%s\n" % (fid, an.get("comment"), tail)
    defs = "".join(_def(an) for an in sorted(annotations, key=lambda a: a.get("finding_id") or "")
                   if isinstance(an, dict))
    return out + "\n" + defs, []


def reverse_obsidian(obsidian_text, finding_ids):
    """The A2-analog inverse: strip the trailing definition block, then the exact manifest-keyed refs."""
    body = _DEF_BLOCK_RE.sub("", obsidian_text)
    for fid in finding_ids:
        body = body.replace("[^%s]" % fid, "")
    return body


def check_obsidian(manifest_obj, snapshot, obsidian_text, letter_basename=None):
    """O1-O3 over an emitted Obsidian copy. Returns (errs, warns). When letter_basename is set (Inc 2),
    O3 expects each definition to equal `comment` + the exact forward wikilink."""
    errs = []
    annotations = manifest_obj.get("annotations") if isinstance(manifest_obj.get("annotations"), list) else []
    ids = [an.get("finding_id") for an in annotations if isinstance(an, dict)]

    # O1 (authoritative) — exact-build equality: the on-disk copy must equal a fresh deterministic build
    # from the gated manifest + snapshot, byte-for-byte. The copy is fully determined by them, so this pins
    # prose, every footnote ref POSITION, the verbatim definitions (+ Inc-2 wikilinks), and forbids any
    # authored content — including an injected orphan trailing `[^X]: …` definition that the round-trip
    # strips and O2 (a def with no ref is not a manifest id) would both miss (the H1/D1 discipline).
    built, _perrs = build_obsidian(manifest_obj, snapshot, letter_basename=letter_basename)
    if built is not None and obsidian_text != built:
        errs.append("O1 copy integrity: the on-disk Obsidian copy is not byte-identical to a fresh build "
                    "from the gated manifest + snapshot (mutated prose, a moved/altered footnote, or "
                    "authored content such as a smuggled orphan definition)")

    # O1 — round-trip to source (manifest-keyed strip == snapshot).
    if reverse_obsidian(obsidian_text, ids) != snapshot:
        errs.append("O1 round-trip: stripping the [^id] refs + the trailing definition block does NOT "
                    "reproduce the snapshot byte-for-byte (prose was altered, or a ref/def is malformed)")

    # O2 — footnote resolution: refs in the body ↔ definitions ↔ manifest id set (bijection, multiset).
    body = _DEF_BLOCK_RE.sub("", obsidian_text)
    ref_counts = {}
    for m in re.finditer(r"\[\^([^\]]+)\]", body):
        ref_counts[m.group(1)] = ref_counts.get(m.group(1), 0) + 1
    def_ids = _DEF_BLOCK_RE.search(obsidian_text)
    def_lines = []
    if def_ids:
        for dl in def_ids.group(0).strip("\n").split("\n"):
            dm = re.match(r"\[\^([^\]]+)\]:\s?(.*)$", dl)
            if dm:
                def_lines.append((dm.group(1), dm.group(2)))
    def_counts = {}
    for fid, _b in def_lines:
        def_counts[fid] = def_counts.get(fid, 0) + 1
    manifest_set = {}
    for fid in ids:
        manifest_set[fid] = manifest_set.get(fid, 0) + 1
    for fid, n in sorted(ref_counts.items()):
        if n != 1:
            errs.append("O2 footnote resolution: ref [^%s] appears %d times (need exactly 1)" % (fid, n))
        if fid not in manifest_set:
            errs.append("O2 footnote resolution: ref [^%s] is not a manifest finding_id (un-manifested footnote)" % fid)
    for fid, n in sorted(def_counts.items()):
        if n != 1:
            errs.append("O2 footnote resolution: definition [^%s]: appears %d times (need exactly 1)" % (fid, n))
    for fid in sorted(manifest_set):
        if ref_counts.get(fid, 0) != 1:
            errs.append("O2 footnote resolution: manifest finding %s has %d refs (need exactly 1)"
                        % (fid, ref_counts.get(fid, 0)))
        if def_counts.get(fid, 0) != 1:
            errs.append("O2 footnote resolution: manifest finding %s has %d definitions (need exactly 1)"
                        % (fid, def_counts.get(fid, 0)))

    # O3 — comment fidelity: each definition body equals the manifest comment (Inc 1) or the comment +
    # the EXACT forward wikilink (Inc 2). No room for authored text around the verbatim comment.
    comment_of = {an.get("finding_id"): an.get("comment") for an in annotations if isinstance(an, dict)}
    for fid, body_text in def_lines:
        if fid not in comment_of:
            continue
        expected = comment_of[fid] + (_fwd_wikilink(letter_basename, fid) if letter_basename else "")
        if body_text != expected:
            errs.append("O3 comment fidelity: definition for %s is not the verbatim manifest comment%s "
                        "(relocate, never re-author)" % (fid, " + exact forward wikilink" if letter_basename else ""))
    return errs, []


# ---------------------------------------------------------------- Increment 2: the letter

def _heading_slug(raw):
    """A copy heading's match text with any appended footnote ref stripped (Obsidian strips it from the
    anchor slug — web-verified): `Chapter 9[^F-RR-01]` -> `Chapter 9`."""
    return re.sub(r"\[\^[^\]]+\]", "", raw).strip()


def _heading_text_of(anchor, snapshot):
    """For a chapter/section anchor, the snapshot heading's text (e.g. 'Chapter 9'); else None."""
    kind, val = anchor.get("kind"), anchor.get("value")
    _cn, _sn, chap_l, sec_l = am.heading_index(snapshot)
    if kind == "chapter":
        lineno = chap_l.get(val)
    elif kind == "section":
        lineno = sec_l.get(str(val).strip().lower())
    else:
        return None
    if not lineno:
        return None
    for (l, raw, _norm) in am.atx_headings(snapshot):
        if l == lineno:
            return raw
    return None


def _reverse_wikilink(anchor, snapshot, copy_basename):
    """The letter→copy back-link for an anchor -> (wikilink, is_file_level). A heading link when the
    anchor resolves to a heading whose text is safe in an Obsidian `#fragment` (no `] [ | #`, which would
    break the wikilink syntax / the O5 strip); otherwise a file-level link (W1)."""
    heading = _heading_text_of(anchor, snapshot)
    if heading is not None and not any(c in heading for c in "][|#"):
        return "[[%s#%s]]" % (copy_basename, heading), False
    return "[[%s]]" % copy_basename, True


def build_obsidian_letter(crosslinked_text, manifest_obj, snapshot, copy_basename):
    """-> (letter_text_or_None, errs, warns). Project the gated crosslinked letter: append ` ^F-id` block
    ids to finding lines + convert each CriticMarkup back-link span to a `[[copy#heading]]` wikilink
    (file-level for line-range/quote/document — W1). Pure projection; the editorial prose is untouched (O5)."""
    errs, warns = [], []
    # O5 two-sided precondition: the editorial prose (letter minus CriticMarkup spans) must carry no
    # wikilink sigil and no line-terminal block id, so the strip is unambiguous (mirrors render/A2).
    prose = am.reverse_transform(crosslinked_text)
    if _WIKILINK_SIGIL in prose:
        errs.append("O5 precondition: the editorial letter already contains '[[' — the reverse transform "
                    "would be ambiguous")
    for ln in prose.split("\n"):
        if re.search(r" \^\S+$", ln):
            errs.append("O5 precondition: the editorial letter has a line-terminal ' ^token' block id")
            break
    if errs:
        return None, errs, warns
    anchor_of = {an.get("finding_id"): (an.get("anchor") or {})
                 for an in (manifest_obj.get("annotations") or []) if isinstance(an, dict)}

    out_lines = []
    for line in crosslinked_text.split("\n"):
        m = _FINDING_MARKER_RE.search(line)
        if not m:
            out_lines.append(line)
            continue
        fid = m.group(1)
        anchor = anchor_of.get(fid, {})
        wl, file_level = _reverse_wikilink(anchor, snapshot, copy_basename)
        if file_level:
            warns.append("W1 file-level back-link: %s anchor (%s) has no Obsidian-linkable heading"
                         % (fid, anchor.get("kind")))
        new_line, n = _CM_SPAN_RE.subn(wl, line, count=1)   # replace the back-link span in place
        if n == 0:
            new_line = line + wl                            # no span (uncited) — append
        out_lines.append(new_line + " ^%s" % fid)           # block id at end of the single-line block
    return "\n".join(out_lines), errs, warns


def strip_obsidian_letter(text, finding_ids, copy_basename=None):
    """Strip Inc-2 additions (the [[…]] wikilinks + line-terminal ` ^<fid>`) — the O5 inverse. When
    copy_basename is given the wikilink strip is **manifest-keyed** to that copy target (`[[copy]]` /
    `[[copy#heading]]`) — never a `[[…]]` wildcard — so an injected wikilink to ANOTHER target survives
    the strip and is caught by the O5 prose compare (the firewall's manifest-keyed-strip discipline)."""
    if copy_basename is not None:
        t = re.sub(r"\[\[%s(?:#[^\]]*)?\]\]" % re.escape(copy_basename), "", text)
    else:
        t = _WIKILINK_RE.sub("", text)
    for fid in finding_ids:
        t = t.replace(" ^%s" % fid, "")
    return t


def check_obsidian_letter(crosslinked_text, obsidian_letter, copy_text, copy_basename, letter_basename,
                          manifest_obj, snapshot):
    """O4 (link resolution) + O5 (letter prose fidelity) over the emitted Obsidian letter + copy."""
    errs, warns = [], []
    ids = [an.get("finding_id") for an in (manifest_obj.get("annotations") or []) if isinstance(an, dict)]

    # O5 (authoritative) — exact-build equality: the on-disk letter must equal a fresh build from the gated
    # crosslinked letter + manifest + snapshot + copy basename, byte-for-byte. The letter is fully determined
    # by those inputs, so this pins the editorial prose, every block id, and every back-link wikilink, and
    # forbids any authored content. This is the firewall guarantee: it closes the wildcard-strip hole where
    # `_WIKILINK_RE.sub("")` deleted an INJECTED `[[Injected_Note]]` before the prose compare, so a tampered
    # on-disk letter passed (the H1/D1 discipline). The strip-based check below remains a granular diagnostic.
    built, _berrs, _bw = build_obsidian_letter(crosslinked_text, manifest_obj, snapshot, copy_basename)
    if built is not None and obsidian_letter != built:
        errs.append("O5 letter integrity: the on-disk Obsidian letter is not byte-identical to a fresh build "
                    "from the gated crosslinked letter + manifest + snapshot (an injected/altered wikilink or "
                    "block id, or mutated editorial prose)")

    # O5 — letter prose fidelity (diagnostic): strip the Obsidian additions == strip the crosslinked
    # CriticMarkup. Manifest-keyed to the copy target (not a `[[…]]` wildcard), so an injected wikilink to a
    # foreign target survives the strip and trips this compare too.
    if strip_obsidian_letter(obsidian_letter, ids, copy_basename) != am.reverse_transform(crosslinked_text):
        errs.append("O5 letter prose fidelity: stripping the Obsidian letter's additions does not "
                    "reproduce the crosslinked letter's editorial prose (the projection mutated prose)")

    # O4 forward — every copy `[[letter#^id]]` resolves to a `^id` block id in the letter.
    letter_block_ids = set(re.findall(r" \^(F-[A-Za-z0-9]+-[0-9]{2,})$", obsidian_letter, re.MULTILINE))
    fwd = re.compile(r"\[\[%s#\^(F-[A-Za-z0-9]+-[0-9]{2,})(?:\|[^\]]*)?\]\]" % re.escape(letter_basename))
    for m in fwd.finditer(copy_text):
        if m.group(1) not in letter_block_ids:
            errs.append("O4 link resolution: copy forward link [[%s#^%s]] has no matching ^%s block id "
                        "in the letter" % (letter_basename, m.group(1), m.group(1)))

    # O4 reverse — PER-FINDING correctness (not mere set-membership): each finding line's back-link must
    # be EXACTLY the expected `[[copy#<that finding's heading>]]` (or file-level), so a real-but-wrong
    # heading — or a smuggled `|display` label — fails. Defense-in-depth: any heading fragment must also
    # resolve to a real copy heading (footnote refs stripped).
    copy_headings = set(_heading_slug(raw) for (_l, raw, _n) in am.atx_headings(copy_text))
    anchor_of = {an.get("finding_id"): (an.get("anchor") or {})
                 for an in (manifest_obj.get("annotations") or []) if isinstance(an, dict)}
    for line in obsidian_letter.split("\n"):
        fm = _FINDING_MARKER_RE.search(line)
        if not fm:
            continue
        fid = fm.group(1)
        expected, _fl = _reverse_wikilink(anchor_of.get(fid, {}), snapshot, copy_basename)
        if expected not in line:
            errs.append("O4 link resolution: %s back-link is not the expected %s "
                        "(wrong heading, or a smuggled display label)" % (fid, expected))
        rm = re.search(r"\[\[%s#([^\]|]+)\]\]" % re.escape(copy_basename), line)
        if rm and rm.group(1).strip() not in copy_headings:
            errs.append("O4 link resolution: letter reverse link [[%s#%s]] matches no copy heading"
                        % (copy_basename, rm.group(1).strip()))
    return errs, warns


# ---------------------------------------------------------------- Increment 3: read-only HTML

_HTML_STYLE = (
    "body{max-width:46em;margin:2rem auto;padding:0 1rem;"
    "font-family:Georgia,'Times New Roman',serif;line-height:1.5;color:#222}\n"
    "pre.manuscript{white-space:pre-wrap;font-family:inherit;font-size:1rem;margin:0}\n"
    ".fnref{font-size:.75em;color:#a00;vertical-align:super}\n"
    ".fnref a,.backref{text-decoration:none;color:#a00}\n"
    "section.findings{margin-top:2rem;border-top:1px solid #ccc;padding-top:1rem;font-size:.95em}\n"
    "section.findings h2{font-size:1.1rem}\n"
    "section.findings li{margin:.4rem 0}\n"
)


def _html_escape(s):
    """Element-content escaping: `&` FIRST, then `<`, `>` (the order is load-bearing for the exact inverse)."""
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _html_unescape_exact(s):
    """The EXACT inverse of _html_escape (mirror order: `<`, `>`, then `&` LAST). NOT a general decoder."""
    return (s or "").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


def _html_marker(fid):
    return '<sup class="fnref" id="ref-%s"><a href="#fn-%s">[%s]</a></sup>' % (fid, fid, fid)


def _html_backref(fid):
    return '<a class="backref" href="#ref-%s">↩</a>' % fid


_PRE_RE = re.compile(r'<pre class="manuscript">(.*)</pre>', re.DOTALL)


def build_html(manifest_obj, snapshot):
    """-> (html_text_or_None, errs). Pure projection: a self-contained read-only HTML — the snapshot in a
    faithful <pre> (escaped, markers spliced between escaped segments) + a findings list with bidirectional
    anchors. errs is the two-sided precondition."""
    annotations = [a for a in (manifest_obj.get("annotations") or []) if isinstance(a, dict)]
    errs = []
    # Two-sided precondition (by construction, since escaping removes every `<`): neither the escaped
    # snapshot nor any escaped comment can contain the literal marker prefix `<sup`.
    if "<sup" in _html_escape(snapshot):
        errs.append("H1 precondition: the escaped snapshot contains '<sup' (impossible after escaping)")
    for a in annotations:
        if "<sup" in _html_escape(a.get("comment") or ""):
            errs.append("H1 precondition: escaped comment for %s contains '<sup'" % a.get("finding_id"))
    if errs:
        return None, errs

    project = manifest_obj.get("project", "Manuscript")
    chap_n, sec_n, chap_l, sec_l = am.heading_index(snapshot)
    nl_at, ln = {}, 1
    for i, ch in enumerate(snapshot):
        if ch == "\n":
            nl_at[ln] = i
            ln += 1
    # group markers by raw-snapshot offset (co-located markers render adjacent, deterministic by id)
    by_off = {}
    for a in annotations:
        off = _insertion_offset(a.get("anchor") or {}, snapshot, nl_at, chap_l, sec_l)
        by_off.setdefault(max(0, min(off, len(snapshot))), []).append(a.get("finding_id"))
    # escape each prose segment between offsets; splice literal markers between (never escaped, no drift)
    parts, prev = [], 0
    for off in sorted(by_off):
        parts.append(_html_escape(snapshot[prev:off]))
        for fid in sorted(by_off[off]):
            parts.append(_html_marker(fid))
        prev = off
    parts.append(_html_escape(snapshot[prev:]))
    pre_content = "".join(parts)

    lis = "".join('<li id="fn-%s">%s %s</li>\n'
                  % (a.get("finding_id"), _html_escape(a.get("comment")), _html_backref(a.get("finding_id")))
                  for a in sorted(annotations, key=lambda x: x.get("finding_id") or ""))
    html = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<title>%s — Annotated Manuscript</title>\n<style>\n%s</style>\n</head>\n<body>\n'
            '<main><pre class="manuscript">%s</pre></main>\n'
            '<section class="findings">\n<h2>Findings</h2>\n<ol>\n%s</ol>\n</section>\n</body>\n</html>\n'
            % (_html_escape(project), _HTML_STYLE, pre_content, lis))
    return html, []


def reverse_html(pre_content, finding_ids):
    """The A2-analog inverse: delete the exact manifest-keyed markers, then the exact 3-entity unescape."""
    t = pre_content
    for fid in finding_ids:
        t = t.replace(_html_marker(fid), "")
    return _html_unescape_exact(t)


def check_html(manifest_obj, snapshot, html_text):
    """H1-H3 over an emitted HTML export. Returns (errs, warns)."""
    errs = []
    annotations = [a for a in (manifest_obj.get("annotations") or []) if isinstance(a, dict)]
    ids = [a.get("finding_id") for a in annotations]

    pres = _PRE_RE.findall(html_text)
    if len(pres) != 1:
        return ["H1 round-trip: expected exactly one <pre class=\"manuscript\"> (found %d)" % len(pres)], []
    pre_content = pres[0]

    # H1 — round-trip: strip manifest-keyed markers + exact unescape == snapshot.
    if reverse_html(pre_content, ids) != snapshot:
        errs.append("H1 round-trip: stripping the markers + exact HTML-unescape does NOT reproduce the "
                    "snapshot byte-for-byte (prose altered, or a marker/escape is malformed)")

    # H2 — anchor resolution: <sup id="ref-fid"> ↔ <li id="fn-fid"> bijection == manifest id set.
    ref_ids = re.findall(r'<sup class="fnref" id="ref-(F-[A-Za-z0-9]+-[0-9]{2,})">', pre_content)
    fn_ids = re.findall(r'<li id="fn-(F-[A-Za-z0-9]+-[0-9]{2,})">', html_text)
    manifest_set = {}
    for fid in ids:
        manifest_set[fid] = manifest_set.get(fid, 0) + 1
    for label, found in (("marker", ref_ids), ("finding", fn_ids)):
        counts = {}
        for fid in found:
            counts[fid] = counts.get(fid, 0) + 1
        for fid, n in sorted(counts.items()):
            if n != 1:
                errs.append("H2 anchor resolution: %s id %s appears %d times (need exactly 1)" % (label, fid, n))
            if fid not in manifest_set:
                errs.append("H2 anchor resolution: %s id %s is not a manifest finding_id (un-manifested)" % (label, fid))
        for fid in sorted(manifest_set):
            if counts.get(fid, 0) != 1:
                errs.append("H2 anchor resolution: manifest finding %s has %d %s id(s) (need exactly 1)"
                            % (fid, counts.get(fid, 0), label))

    # H3 — comment fidelity: each <li> content == escape(comment) + " " + exact back-ref.
    comment_of = {a.get("finding_id"): a.get("comment") for a in annotations}
    for m in re.finditer(r'<li id="fn-(F-[A-Za-z0-9]+-[0-9]{2,})">(.*?)</li>', html_text, re.DOTALL):
        fid, content = m.group(1), m.group(2)
        if fid in comment_of:
            expected = "%s %s" % (_html_escape(comment_of[fid]), _html_backref(fid))
            if content != expected:
                errs.append("H3 comment fidelity: <li> for %s is not the verbatim manifest comment + the "
                            "exact back-ref (relocate, never re-author)" % fid)
    return errs, []


def _runlabel_of(path):
    base = os.path.basename(path or "")
    for infix in ("_Manuscript_Snapshot_", "_Annotation_Manifest_"):
        if infix in base:
            return os.path.splitext(base.split(infix)[-1])[0] or "run"
    return os.path.splitext(base)[0] or "run"


def _resolve(folder):
    """-> (manifest_obj_or_None, snapshot_or_None, project, runlabel, crosslinked_text_or_None, err)."""
    man = _newest(glob.glob(os.path.join(folder, am._MANIFEST_GLOB)))
    snap = _newest(glob.glob(os.path.join(folder, am._SNAPSHOT_GLOB)))
    if not man:
        return None, None, None, None, None, "no %s in %s" % (am._MANIFEST_GLOB, folder)
    if not snap:
        return None, None, None, None, None, "no %s in %s" % (am._SNAPSHOT_GLOB, folder)
    obj, merrs = am.parse_manifest(_read(man))
    if obj is None:
        return None, None, None, None, None, "manifest invalid — %s" % (merrs[0] if merrs else "no annotation block")
    snapshot = am.normalize_snapshot(_read(snap) or "")
    project = os.path.basename(snap).split("_Manuscript_Snapshot_")[0] or obj.get("project", "Manuscript")
    # The crosslinked letter (Increment 2 input) — optional; its presence enables the letter projection.
    cl_path = _newest(glob.glob(os.path.join(folder, _CROSSLINKED_GLOB)))
    crosslinked = _read(cl_path) if cl_path else None
    return obj, snapshot, project, _runlabel_of(snap), crosslinked, None


def generate(folder):
    """Write obsidian/<copy> (and, when a crosslinked letter is present, obsidian/<letter> + forward
    wikilinks in the copy — Increment 2). Returns (code, lines)."""
    obj, snapshot, project, runlabel, crosslinked, err = _resolve(folder)
    if err:
        return 2, ["obsidian-export: %s" % err]
    copy_basename = "%s_Annotated_Manuscript_%s" % (project, runlabel)
    letter_basename = "%s_Crosslinked_Letter_%s" % (project, runlabel)
    letter_bn = letter_basename if crosslinked else None
    copy_text, errs = build_obsidian(obj, snapshot, letter_basename=letter_bn)
    if errs:
        return 1, ["obsidian-export: " + e for e in errs] + ["obsidian-export: FAIL (O1 precondition)"]
    outdir = os.path.join(folder, "obsidian")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, copy_basename + ".md"), "w", encoding="utf-8") as fh:
        fh.write(copy_text)
    wrote = [copy_basename + ".md"]
    if crosslinked:
        letter_text, lerrs, _lwarns = build_obsidian_letter(crosslinked, obj, snapshot, copy_basename)
        if lerrs:
            return 1, ["obsidian-export: " + e for e in lerrs] + ["obsidian-export: FAIL (O5 precondition)"]
        with open(os.path.join(outdir, letter_basename + ".md"), "w", encoding="utf-8") as fh:
            fh.write(letter_text)
        wrote.append(letter_basename + ".md")
    return 0, ["obsidian-export: wrote " + ", ".join("obsidian/" + w for w in wrote)]


def run(paths, strict=False):
    if len(paths) < 1 or not os.path.isdir(paths[0]):
        return 2, ["obsidian-export: usage: obsidian-export <run_folder>"]
    obj, snapshot, _p, _r, crosslinked, err = _resolve(paths[0])
    if err:
        return 2, ["obsidian-export: %s" % err]
    # Validate the ON-DISK export artifacts, never a regenerate — so a hand-edited copy/letter is caught
    # (mirrors how annotated-manuscript gates the committed copy's bytes — the A2 discipline).
    copy_path = _newest(glob.glob(os.path.join(paths[0], "obsidian", "*_Annotated_Manuscript_*.md")))
    if not copy_path:
        return 2, ["obsidian-export: no obsidian/*_Annotated_Manuscript_*.md found "
                   "(run `annotation_export.py obsidian <run_folder>` first)"]
    copy_text = _read(copy_path)
    if copy_text is None:
        return 2, ["obsidian-export: cannot read %s" % copy_path]
    copy_basename = os.path.splitext(os.path.basename(copy_path))[0]
    letter_path = _newest(glob.glob(os.path.join(paths[0], "obsidian", _CROSSLINKED_GLOB)))
    letter_basename = os.path.splitext(os.path.basename(letter_path))[0] if letter_path else None
    # The two-sided build precondition the artifacts must have satisfied.
    _expected, perrs = build_obsidian(obj, snapshot, letter_basename=letter_basename)
    if perrs:
        return 1, ["obsidian-export: " + e for e in perrs] + ["obsidian-export: FAIL (O1 precondition)"]
    errs, _w = check_obsidian(obj, snapshot, copy_text, letter_basename=letter_basename)
    gates = "O1 round-trip + O2 footnote resolution + O3 comment fidelity"
    if letter_path and not crosslinked:
        # An on-disk Obsidian letter exists but its gated crosslinked source is absent, so O4/O5 cannot run.
        # Refuse to PASS rather than silently skip — else deleting the gated source and leaving a tampered
        # obsidian/ letter in place would ride through unvalidated (a firewall bypass).
        errs.append("an exported Obsidian letter (obsidian/%s) is present but its gated crosslinked source "
                    "(%s) is absent — refusing to PASS an unvalidatable letter"
                    % (os.path.basename(letter_path), _CROSSLINKED_GLOB))
    elif letter_path and crosslinked:
        letter_text = _read(letter_path) or ""
        e_l, _wl = check_obsidian_letter(crosslinked, letter_text, copy_text, copy_basename,
                                         letter_basename, obj, snapshot)
        errs = errs + e_l
        gates += " + O4 link resolution + O5 letter prose fidelity"
    lines = ["obsidian-export: %d finding(s); validating obsidian/%s%s"
             % (len(obj.get("annotations") or []), os.path.basename(copy_path),
                " + " + os.path.basename(letter_path) if letter_path else "")]
    for e in errs:
        lines.append("  ERROR: %s" % e)
    if errs:
        lines.append("obsidian-export: FAIL (%d error(s))" % len(errs))
        return 1, lines
    lines.append("obsidian-export: PASS (%s)" % gates)
    return 0, lines


def generate_html(folder):
    """Write html/<Project>_Annotated_Manuscript_<runlabel>.html. Returns (code, lines)."""
    obj, snapshot, project, runlabel, _cl, err = _resolve(folder)
    if err:
        return 2, ["html-export: %s" % err]
    html, errs = build_html(obj, snapshot)
    if errs:
        return 1, ["html-export: " + e for e in errs] + ["html-export: FAIL (H1 precondition)"]
    outdir = os.path.join(folder, "html")
    os.makedirs(outdir, exist_ok=True)
    out_path = os.path.join(outdir, "%s_Annotated_Manuscript_%s.html" % (project, runlabel))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return 0, ["html-export: wrote html/%s" % os.path.basename(out_path)]


def run_html(paths):
    """Validate the ON-DISK html/<copy>.html (H1-H3), never a regenerate."""
    if len(paths) < 1 or not os.path.isdir(paths[0]):
        return 2, ["html-export: usage: html-export <run_folder>"]
    obj, snapshot, _p, _r, _cl, err = _resolve(paths[0])
    if err:
        return 2, ["html-export: %s" % err]
    html_path = _newest(glob.glob(os.path.join(paths[0], "html", "*_Annotated_Manuscript_*.html")))
    if not html_path:
        return 2, ["html-export: no html/*_Annotated_Manuscript_*.html found "
                   "(run `annotation_export.py html <run_folder>` first)"]
    html_text = _read(html_path)
    if html_text is None:
        return 2, ["html-export: cannot read %s" % html_path]
    _exp, perrs = build_html(obj, snapshot)
    if perrs:
        return 1, ["html-export: " + e for e in perrs] + ["html-export: FAIL (H1 precondition)"]
    errs, _w = check_html(obj, snapshot, html_text)
    lines = ["html-export: %d finding(s); validating html/%s"
             % (len(obj.get("annotations") or []), os.path.basename(html_path))]
    for e in errs:
        lines.append("  ERROR: %s" % e)
    if errs:
        lines.append("html-export: FAIL (%d error(s))" % len(errs))
        return 1, lines
    lines.append("html-export: PASS (H1 round-trip + H2 anchor resolution + H3 comment fidelity)")
    return 0, lines


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    import tempfile
    import shutil
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    snap = am.normalize_snapshot(
        "# Chapter 1\n"
        "The lighthouse stood unlit for forty years.\n"
        "She counted the hours.\n"
        "# Chapter 9\n"
        "Three days collapsed here.\n")
    quote = "The lighthouse stood unlit for forty years."
    qs = snap.find(quote)

    def ann(fid, anchor, comment):
        return {"finding_id": fid, "anchor": anchor, "comment": comment}

    obj = {"schema": am._SCHEMA_ID, "project": "T", "runlabel": "r",
           "snapshot_path": "T_Manuscript_Snapshot_r.md", "snapshot_sha256": am.sha256(snap),
           "snapshot_line_count": am.line_count(snap),
           "annotations": [
               ann("F-QT-01", {"kind": "quote", "value": "%d-%d" % (qs, qs + len(quote)), "quote": quote},
                   "[Must-Fix · F-QT-01] flat reveal — fix class: stage it. (See letter §F-QT-01.)"),
               ann("F-CH-01", {"kind": "chapter", "value": "Ch 9"},
                   "[Should-Fix · F-CH-01] pacing seam — fix class: add a beat. (See letter §F-CH-01.)"),
               ann("F-DOC-01", {"kind": "document", "value": ""},
                   "[Could-Fix · F-DOC-01] soft opening — fix class: sharpen. (See letter §F-DOC-01.)"),
               ann("F-NEG-01", {"kind": "chapter", "value": "Ch 1"},
                   "[Should-Fix · F-NEG-01] POV wobble — fix class: hold POV. (See letter §F-NEG-01.)"),
           ]}

    text, errs = build_obsidian(obj, snap)
    chk("build_no_precondition_errs", not errs and text is not None)
    chk("ref_at_quote_end", (quote + "[^F-QT-01]") in text)
    chk("ref_on_chapter_line", "# Chapter 9[^F-CH-01]" in text)
    # F-DOC-01 (document, end of line 1) + F-NEG-01 (Ch 1, end of line 1) are CO-LOCATED -> adjacent refs.
    chk("co_located_adjacent", "# Chapter 1[^F-DOC-01][^F-NEG-01]" in text)
    chk("definition_block_verbatim",
        "[^F-QT-01]: [Must-Fix · F-QT-01] flat reveal — fix class: stage it. (See letter §F-QT-01.)" in text)

    # O1 round-trip: strip refs + def block -> snapshot.
    chk("round_trip_to_snapshot", reverse_obsidian(text, [a["finding_id"] for a in obj["annotations"]]) == snap)

    # the validator passes on a clean export.
    e, _w = check_obsidian(obj, snap, text)
    chk("check_clean", e == [])

    # O1 fires on prose mutation (tamper a body char).
    tampered = text.replace("Three days collapsed here.", "Three days collapsed HERE.")
    e, _w = check_obsidian(obj, snap, tampered)
    chk("o1_fires_on_mutation", any("O1 round-trip" in x for x in e))

    # O3 fires on a re-authored comment.
    reauth = text.replace("flat reveal", "REWRITTEN")
    e, _w = check_obsidian(obj, snap, reauth)
    chk("o3_fires_on_reauthor", any("O3 comment fidelity" in x for x in e))

    # O2 fires on an un-manifested (authored) footnote ref+def smuggled in.
    smuggled = text.replace("Three days collapsed here.", "Three days collapsed here.[^F-EVIL-01]")
    smuggled = smuggled.rstrip("\n") + "\n[^F-EVIL-01]: authored note\n"
    e, _w = check_obsidian(obj, snap, smuggled)
    chk("o2_fires_on_unmanifested", any("O2 footnote resolution" in x and "F-EVIL-01" in x for x in e))

    # O1 precondition: a snapshot already carrying '[^' is refused.
    bad_snap = am.normalize_snapshot("# Ch 1\nan array[^index] reference\n")
    _t, perrs = build_obsidian({"annotations": [ann("F-X-01", {"kind": "document", "value": ""}, "c")]}, bad_snap)
    chk("precondition_snapshot_sigil", any("snapshot already contains" in x for x in perrs))

    # O1 precondition: a comment carrying '[^' is refused.
    _t, perrs = build_obsidian({"annotations": [ann("F-X-01", {"kind": "document", "value": ""}, "see [^1]")]}, snap)
    chk("precondition_comment_sigil", any("comment for F-X-01 contains" in x for x in perrs))

    # O1 precondition: a multi-line comment is refused (a footnote definition is one line).
    _t, perrs = build_obsidian({"annotations": [ann("F-X-01", {"kind": "document", "value": ""}, "line one\nline two")]}, snap)
    chk("precondition_comment_multiline", any("is multi-line" in x for x in perrs))

    # determinism.
    chk("deterministic", build_obsidian(obj, snap)[0] == build_obsidian(obj, snap)[0])

    # empty manifest -> copy is the snapshot, round-trips trivially.
    t0, _e = build_obsidian({"annotations": []}, snap)
    chk("empty_is_snapshot", t0 == snap)

    # --- Increment 2: the letter cross-links ---
    copy_bn, letter_bn = "T_Annotated_Manuscript_r", "T_Crosslinked_Letter_r"
    copy2, _e = build_obsidian(obj, snap, letter_basename=letter_bn)
    chk("inc2_copy_forward_wikilink",
        "(See letter §F-CH-01.) [[T_Crosslinked_Letter_r#^F-CH-01|→ letter §F-CH-01]]" in copy2)
    chk("inc2_copy_round_trips",
        reverse_obsidian(copy2, [a["finding_id"] for a in obj["annotations"]]) == snap)
    chk("inc2_copy_o3_clean", check_obsidian(obj, snap, copy2, letter_basename=letter_bn)[0] == [])
    # O3 fires if the forward wikilink is tampered (authored text in the definition).
    chk("inc2_o3_fires_on_bad_wikilink",
        any("O3" in x for x in check_obsidian(obj, snap, copy2.replace("→ letter §F-CH-01", "→ EVIL"), letter_basename=letter_bn)[0]))

    crosslinked = ("# T — Editorial Letter\n\n## What Needs Work\n\n"
                   "The reveal lands flat. <!-- finding: F-QT-01 -->{>>→ marked-up copy: F-QT-01 @ quote:%d-%d<<}\n\n"
                   "The pacing collapses in chapter nine. <!-- finding: F-CH-01 -->{>>→ marked-up copy: F-CH-01 @ chapter:Ch 9<<}\n\n"
                   "The opening is soft. <!-- finding: F-DOC-01 -->{>>→ marked-up copy: F-DOC-01 @ document:<<}\n\n"
                   "The POV wobbles. <!-- finding: F-NEG-01 -->{>>→ marked-up copy: F-NEG-01 @ chapter:Ch 1<<}\n"
                   % (qs, qs + len(quote)))
    letter2, lerrs, lwarns = build_obsidian_letter(crosslinked, obj, snap, copy_bn)
    chk("inc2_letter_no_precond_errs", not lerrs)
    chk("inc2_letter_block_id", "<!-- finding: F-CH-01 -->[[T_Annotated_Manuscript_r#Chapter 9]] ^F-CH-01" in letter2)
    chk("inc2_letter_heading_text_not_token", "#Chapter 9]]" in letter2 and "#Ch 9]]" not in letter2)
    chk("inc2_letter_file_level_doc", "[[T_Annotated_Manuscript_r]] ^F-DOC-01" in letter2 and len(lwarns) >= 1)
    ids = [a["finding_id"] for a in obj["annotations"]]
    chk("inc2_o5_prose_fidelity", strip_obsidian_letter(letter2, ids, copy_bn) == am.reverse_transform(crosslinked))
    chk("inc2_o4_o5_clean",
        check_obsidian_letter(crosslinked, letter2, copy2, copy_bn, letter_bn, obj, snap)[0] == [])
    # Codex #109 (THE reproduced firewall hole): an INJECTED `[[Injected_Note]]` in the on-disk letter — with
    # no whitespace delta — used to PASS because the wildcard `_WIKILINK_RE.sub("")` stripped it before the
    # prose compare. The authoritative O5 exact-build equality (and the now manifest-keyed strip) must catch it.
    # NO leading space — the exact zero-whitespace-delta injection from the bug report, so the OLD wildcard
    # strip would have removed it cleanly (reproducing the prose, a false PASS); only the authoritative lock
    # + the manifest-keyed strip catch it. (A leading space would let the old strip leave a residual and pass
    # for the wrong reason — a vacuous test.)
    _injected = letter2.replace("# T — Editorial Letter", "# T — Editorial Letter[[Injected_Note]]", 1)
    chk("inc2_o5_catches_injected_wikilink",
        any("O5" in x for x in check_obsidian_letter(crosslinked, _injected, copy2, copy_bn, letter_bn, obj, snap)[0]))
    chk("inc2_o5_keyed_strip_keeps_foreign_wikilink",   # the keyed strip leaves a foreign wikilink in place
        strip_obsidian_letter(_injected, ids, copy_bn) != am.reverse_transform(crosslinked))
    # Codex #109 analog on the COPY: an injected orphan trailing `[^X]: …` definition (no in-body ref) used
    # to slip past O1's trailing-block strip + O2 (a def with no ref is not a manifest id). Authoritative O1
    # exact-build equality catches it.
    _orphan = copy2.rstrip("\n") + "\n[^F-EVIL-02]: an authored orphan definition\n"
    chk("inc2_copy_catches_orphan_definition",
        any("O1 copy integrity" in x for x in check_obsidian(obj, snap, _orphan, letter_basename=letter_bn)[0]))
    # O4 forward fires when a letter block id is missing (copy forward link dangles).
    chk("inc2_o4_forward_fires",
        any("O4" in x for x in check_obsidian_letter(crosslinked, letter2.replace(" ^F-CH-01", ""),
                                                     copy2, copy_bn, letter_bn, obj, snap)[0]))
    # O5 fires on letter prose mutation.
    chk("inc2_o5_fires_on_mutation",
        any("O5" in x for x in check_obsidian_letter(crosslinked, letter2.replace("pacing collapses", "pacing COLLAPSES"),
                                                     copy2, copy_bn, letter_bn, obj, snap)[0]))
    # O5 precondition: an editorial letter already containing '[[' is refused.
    _t, lerrs2, _w = build_obsidian_letter(crosslinked.replace("The reveal lands flat.", "See [[elsewhere]]."),
                                           obj, snap, copy_bn)
    chk("inc2_o5_precondition_wikilink", any("already contains '[['" in x for x in lerrs2))

    # P2-2: O4-reverse is PER-FINDING — a real-but-wrong heading fails (set-membership would pass).
    chk("inc2_o4_reverse_wrong_heading_fires",
        any("O4" in x for x in check_obsidian_letter(
            crosslinked, letter2.replace("#Chapter 9]]", "#Chapter 1]]"), copy2, copy_bn, letter_bn, obj, snap)[0]))
    # P3: a smuggled `|display` label on a reverse link fails (the expected link has no `|`).
    chk("inc2_o4_reverse_display_label_fires",
        any("O4" in x for x in check_obsidian_letter(
            crosslinked, letter2.replace("#Chapter 9]]", "#Chapter 9|SMUGGLED]]"), copy2, copy_bn, letter_bn, obj, snap)[0]))
    # P2-1: a section heading with an unsafe char (`]`) degrades to a file-level link (not a malformed one).
    snap_br = am.normalize_snapshot("# Orientation [draft]\nProse here.\n")
    obj_br = {"annotations": [ann("F-SEC-01", {"kind": "section", "value": "Orientation [draft]"},
                                  "[Should-Fix · F-SEC-01] x — fix class: y. (See letter §F-SEC-01.)")]}
    cl_br = "# L\n\nThing. <!-- finding: F-SEC-01 -->{>>→ marked-up copy: F-SEC-01 @ section:Orientation [draft]<<}\n"
    lt_br, _e, w_br = build_obsidian_letter(cl_br, obj_br, snap_br, "C")
    chk("inc2_unsafe_heading_file_level", "[[C]] ^F-SEC-01" in lt_br and "[[C#" not in lt_br and len(w_br) >= 1)

    # generate() end-to-end from a run folder.
    d = tempfile.mkdtemp()
    try:
        with open(os.path.join(d, "T_Manuscript_Snapshot_r.md"), "w") as fh:
            fh.write(snap)
        with open(os.path.join(d, "T_Annotation_Manifest_r.md"), "w") as fh:
            fh.write("<!-- apodictic:annotation\n%s\n-->" % _j.dumps(obj))
        chk("generate_writes", generate(d)[0] == 0 and os.path.isfile(
            os.path.join(d, "obsidian", "T_Annotated_Manuscript_r.md")))
        chk("run_validates", run([d])[0] == 0)
        # run() must validate the ON-DISK copy: tampering the emitted file is caught (not a regenerate).
        copy_p = os.path.join(d, "obsidian", "T_Annotated_Manuscript_r.md")
        good = open(copy_p, encoding="utf-8").read()
        open(copy_p, "w", encoding="utf-8").write(good.replace("Three days collapsed here.", "Three days collapsed THERE."))
        chk("run_catches_disk_prose_mutation", run([d])[0] == 1)
        open(copy_p, "w", encoding="utf-8").write(good.replace("pacing seam", "AN INVENTED CLAIM"))
        chk("run_catches_disk_comment_reauthor", run([d])[0] == 1)
        open(copy_p, "w", encoding="utf-8").write(
            good.replace("Three days collapsed here.", "Three days collapsed here.[^F-EVIL-01]").rstrip("\n")
            + "\n[^F-EVIL-01]: authored note\n")
        chk("run_catches_disk_unmanifested_footnote", run([d])[0] == 1)
        open(copy_p, "w", encoding="utf-8").write(good)
        chk("run_passes_after_restore", run([d])[0] == 0)
        # a missing on-disk export is a usage error, not a false PASS.
        os.remove(copy_p)
        chk("run_no_copy_is_usage", run([d])[0] == 2)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # Increment 2 end-to-end: a run folder WITH a crosslinked letter -> generate writes copy + letter,
    # run validates both (O1-O5), and tampering the on-disk letter is caught.
    d2 = tempfile.mkdtemp()
    try:
        with open(os.path.join(d2, "T_Manuscript_Snapshot_r.md"), "w") as fh:
            fh.write(snap)
        with open(os.path.join(d2, "T_Annotation_Manifest_r.md"), "w") as fh:
            fh.write("<!-- apodictic:annotation\n%s\n-->" % _j.dumps(obj))
        with open(os.path.join(d2, "T_Crosslinked_Letter_r.md"), "w") as fh:
            fh.write(crosslinked)
        code, _l = generate(d2)
        chk("inc2_generate_both", code == 0
            and os.path.isfile(os.path.join(d2, "obsidian", "T_Annotated_Manuscript_r.md"))
            and os.path.isfile(os.path.join(d2, "obsidian", "T_Crosslinked_Letter_r.md")))
        chk("inc2_run_validates_both", run([d2])[0] == 0)
        letter_p = os.path.join(d2, "obsidian", "T_Crosslinked_Letter_r.md")
        good_l = open(letter_p, encoding="utf-8").read()
        open(letter_p, "w", encoding="utf-8").write(good_l.replace("pacing collapses", "pacing COLLAPSES"))
        chk("inc2_run_catches_letter_mutation", run([d2])[0] == 1)
        # Codex #109 end-to-end: inject a `[[Injected_Note]]` (zero whitespace delta) into the EXPORTED
        # letter file and run the validator — it must FAIL (it returned PASS before the authoritative O5 lock).
        open(letter_p, "w", encoding="utf-8").write(
            good_l.replace("# T — Editorial Letter", "# T — Editorial Letter[[Injected_Note]]", 1))
        chk("inc2_run_catches_disk_injected_wikilink", run([d2])[0] == 1)
        # Codex #109 P2: deleting the gated crosslinked SOURCE while leaving the tampered obsidian/ letter
        # must NOT silently skip O4/O5 — it must FAIL (a present-but-unvalidatable letter is refused).
        src_p = os.path.join(d2, "T_Crosslinked_Letter_r.md")
        os.remove(src_p)
        chk("inc2_run_refuses_letter_without_gated_source", run([d2])[0] == 1)
        open(src_p, "w", encoding="utf-8").write(crosslinked)   # restore the gated source
        open(letter_p, "w", encoding="utf-8").write(good_l)
        chk("inc2_run_passes_after_restore", run([d2])[0] == 0)
    finally:
        shutil.rmtree(d2, ignore_errors=True)

    # --- Increment 3: read-only HTML ---
    html, herrs = build_html(obj, snap)
    chk("html_no_precond_errs", not herrs and html is not None)
    chk("html_one_pre", len(_PRE_RE.findall(html)) == 1)
    chk("html_marker_at_anchor",
        '<sup class="fnref" id="ref-F-QT-01"><a href="#fn-F-QT-01">[F-QT-01]</a></sup>' in html)
    chk("html_finding_li",
        '<li id="fn-F-CH-01">[Should-Fix · F-CH-01] pacing seam — fix class: add a beat. (See letter §F-CH-01.) '
        '<a class="backref" href="#ref-F-CH-01">↩</a></li>' in html)
    chk("html_check_clean", check_html(obj, snap, html)[0] == [])
    chk("html_round_trip", reverse_html(_PRE_RE.findall(html)[0], [a["finding_id"] for a in obj["annotations"]]) == snap)
    chk("html_h1_fires_on_mutation",
        any("H1" in x for x in check_html(obj, snap, html.replace("Three days collapsed here.", "Three days THERE."))[0]))
    chk("html_h3_fires_on_reauthor",
        any("H3" in x for x in check_html(obj, snap, html.replace("pacing seam", "INVENTED"))[0]))
    chk("html_h2_fires_on_unmanifested",
        any("H2" in x for x in check_html(obj, snap, html.replace(
            "</ol>", '<li id="fn-F-EVIL-01">x <a class="backref" href="#ref-F-EVIL-01">↩</a></li>\n</ol>'))[0]))

    # HOSTILE (mandated): HTML metachars `& < >` UPSTREAM of an anchor (catches offset drift) + literal
    # `& <` in a comment (catches double-escape + the exact inverse) — the canonical fixture has none.
    q = "The lighthouse stood unlit for forty years."
    snap_h = am.normalize_snapshot("# A & B <tag> here\n" + q + "\n")
    qh = snap_h.find(q)
    obj_h = {"project": "H & <co>", "annotations": [ann(
        "F-QT-01", {"kind": "quote", "value": "%d-%d" % (qh, qh + len(q)), "quote": q},
        "[Must-Fix · F-QT-01] the line uses & and <x> markup — fix class: stage it. (See letter §F-QT-01.)")]}
    html_h, _e = build_html(obj_h, snap_h)
    chk("html_hostile_round_trips", reverse_html(_PRE_RE.findall(html_h)[0], ["F-QT-01"]) == snap_h)
    chk("html_hostile_check_clean", check_html(obj_h, snap_h, html_h)[0] == [])
    chk("html_hostile_escapes_prose", "# A &amp; B &lt;tag&gt; here" in html_h)
    chk("html_hostile_escapes_comment", "uses &amp; and &lt;x&gt; markup" in html_h)
    chk("html_hostile_no_offset_drift", (q + '<sup class="fnref" id="ref-F-QT-01">') in html_h)

    # generate_html + run_html end-to-end; on-disk tampering caught.
    d3 = tempfile.mkdtemp()
    try:
        with open(os.path.join(d3, "T_Manuscript_Snapshot_r.md"), "w") as fh:
            fh.write(snap)
        with open(os.path.join(d3, "T_Annotation_Manifest_r.md"), "w") as fh:
            fh.write("<!-- apodictic:annotation\n%s\n-->" % _j.dumps(obj))
        chk("html_generate_writes", generate_html(d3)[0] == 0
            and os.path.isfile(os.path.join(d3, "html", "T_Annotated_Manuscript_r.html")))
        chk("html_run_validates", run_html([d3])[0] == 0)
        hp = os.path.join(d3, "html", "T_Annotated_Manuscript_r.html")
        gh = open(hp, encoding="utf-8").read()
        open(hp, "w", encoding="utf-8").write(gh.replace("Three days collapsed here.", "Three days THERE."))
        chk("html_run_catches_disk_mutation", run_html([d3])[0] == 1)
        open(hp, "w", encoding="utf-8").write(gh)
        chk("html_run_passes_after_restore", run_html([d3])[0] == 0)
    finally:
        shutil.rmtree(d3, ignore_errors=True)

    print("Self-test: %s" % ("PASS" if rc["v"] == 0 else "FAIL"))
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    if am is None:
        print("obsidian-export: annotation_manifest unavailable (same-dir import failed)")
        return 2
    args = [a for a in argv[1:] if not a.startswith("--")]
    # generate modes
    for verb, gen in (("obsidian", generate), ("html", generate_html)):
        if args and args[0] == verb:
            rest = [a for a in args[1:]]
            if len(rest) != 1 or not os.path.isdir(rest[0]):
                print("Usage: annotation_export.py %s <run_folder>" % verb)
                return 2
            code, lines = gen(rest[0])
            for ln in lines:
                print(ln)
            return code
    # validate modes
    if args and args[0] == "html-export":
        code, lines = run_html(args[1:])
        for ln in lines:
            print(ln)
        return code
    paths = [a for a in args if a != "obsidian-export"]
    if not paths:
        print("Usage: annotation_export.py obsidian|html <run_folder> | obsidian-export|html-export "
              "<run_folder> | --self-test")
        return 2
    code, lines = run(paths, strict="--strict" in argv)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
