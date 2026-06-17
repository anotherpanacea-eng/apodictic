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


def build_obsidian(manifest_obj, snapshot):
    """-> (obsidian_text_or_None, errs). Pure projection of the gated manifest; errs is the O1 precondition."""
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

    # Definition block (deterministic: sorted by finding_id), each line the VERBATIM manifest comment.
    defs = "".join("[^%s]: %s\n" % (an.get("finding_id"), an.get("comment"))
                   for an in sorted(annotations, key=lambda a: a.get("finding_id") or "")
                   if isinstance(an, dict))
    return out + "\n" + defs, []


def reverse_obsidian(obsidian_text, finding_ids):
    """The A2-analog inverse: strip the trailing definition block, then the exact manifest-keyed refs."""
    body = _DEF_BLOCK_RE.sub("", obsidian_text)
    for fid in finding_ids:
        body = body.replace("[^%s]" % fid, "")
    return body


def check_obsidian(manifest_obj, snapshot, obsidian_text):
    """O1-O3 over an emitted Obsidian copy. Returns (errs, warns)."""
    errs = []
    annotations = manifest_obj.get("annotations") if isinstance(manifest_obj.get("annotations"), list) else []
    ids = [an.get("finding_id") for an in annotations if isinstance(an, dict)]

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

    # O3 — comment fidelity: each definition body == the manifest comment byte-for-byte.
    comment_of = {an.get("finding_id"): an.get("comment") for an in annotations if isinstance(an, dict)}
    for fid, body_text in def_lines:
        if fid in comment_of and body_text != comment_of[fid]:
            errs.append("O3 comment fidelity: definition for %s is not the verbatim manifest comment "
                        "(relocate, never re-author)" % fid)
    return errs, []


def _runlabel_of(path):
    base = os.path.basename(path or "")
    for infix in ("_Manuscript_Snapshot_", "_Annotation_Manifest_"):
        if infix in base:
            return os.path.splitext(base.split(infix)[-1])[0] or "run"
    return os.path.splitext(base)[0] or "run"


def _resolve(folder):
    """-> (manifest_obj_or_None, snapshot_or_None, project, runlabel, err)."""
    man = _newest(glob.glob(os.path.join(folder, am._MANIFEST_GLOB)))
    snap = _newest(glob.glob(os.path.join(folder, am._SNAPSHOT_GLOB)))
    if not man:
        return None, None, None, None, "no %s in %s" % (am._MANIFEST_GLOB, folder)
    if not snap:
        return None, None, None, None, "no %s in %s" % (am._SNAPSHOT_GLOB, folder)
    obj, merrs = am.parse_manifest(_read(man))
    if obj is None:
        return None, None, None, None, "manifest invalid — %s" % (merrs[0] if merrs else "no annotation block")
    snapshot = am.normalize_snapshot(_read(snap) or "")
    project = os.path.basename(snap).split("_Manuscript_Snapshot_")[0] or obj.get("project", "Manuscript")
    return obj, snapshot, project, _runlabel_of(snap), None


def generate(folder):
    """Write obsidian/<Project>_Annotated_Manuscript_<runlabel>.md. Returns (code, lines)."""
    obj, snapshot, project, runlabel, err = _resolve(folder)
    if err:
        return 2, ["obsidian-export: %s" % err]
    text, errs = build_obsidian(obj, snapshot)
    if errs:
        return 1, ["obsidian-export: " + e for e in errs] + ["obsidian-export: FAIL (O1 precondition)"]
    outdir = os.path.join(folder, "obsidian")
    os.makedirs(outdir, exist_ok=True)
    out_path = os.path.join(outdir, "%s_Annotated_Manuscript_%s.md" % (project, runlabel))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return 0, ["obsidian-export: wrote obsidian/%s" % os.path.basename(out_path)]


def run(paths, strict=False):
    if len(paths) < 1 or not os.path.isdir(paths[0]):
        return 2, ["obsidian-export: usage: obsidian-export <run_folder>"]
    obj, snapshot, _p, _r, err = _resolve(paths[0])
    if err:
        return 2, ["obsidian-export: %s" % err]
    # Validate the ON-DISK export artifact, never a regenerate — so a hand-edited copy (mutated prose,
    # re-authored comment, smuggled un-manifested footnote) is actually caught. This mirrors how
    # `annotated-manuscript` globs and gates the committed annotated copy's bytes (the A2 discipline).
    copy_path = _newest(glob.glob(os.path.join(paths[0], "obsidian", "*_Annotated_Manuscript_*.md")))
    if not copy_path:
        return 2, ["obsidian-export: no obsidian/*_Annotated_Manuscript_*.md found "
                   "(run `annotation_export.py obsidian <run_folder>` first)"]
    text = _read(copy_path)
    if text is None:
        return 2, ["obsidian-export: cannot read %s" % copy_path]
    # The two-sided build precondition the artifact must have satisfied (snapshot/comments free of '[^').
    _expected, perrs = build_obsidian(obj, snapshot)
    if perrs:
        return 1, ["obsidian-export: " + e for e in perrs] + ["obsidian-export: FAIL (O1 precondition)"]
    errs, warns = check_obsidian(obj, snapshot, text)
    lines = ["obsidian-export: %d finding(s); validating obsidian/%s"
             % (len(obj.get("annotations") or []), os.path.basename(copy_path))]
    for e in errs:
        lines.append("  ERROR: %s" % e)
    if errs:
        lines.append("obsidian-export: FAIL (%d error(s))" % len(errs))
        return 1, lines
    lines.append("obsidian-export: PASS (O1 round-trip + O2 footnote resolution + O3 comment fidelity)")
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

    print("Self-test: %s" % ("PASS" if rc["v"] == 0 else "FAIL"))
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    if am is None:
        print("obsidian-export: annotation_manifest unavailable (same-dir import failed)")
        return 2
    args = [a for a in argv[1:] if not a.startswith("--")]
    if args and args[0] == "obsidian":
        rest = [a for a in args[1:]]
        if len(rest) != 1 or not os.path.isdir(rest[0]):
            print("Usage: annotation_export.py obsidian <run_folder>")
            return 2
        code, lines = generate(rest[0])
        for ln in lines:
            print(ln)
        return code
    paths = [a for a in args if a != "obsidian-export"]
    if not paths:
        print("Usage: annotation_export.py obsidian <run_folder> | obsidian-export <run_folder> | --self-test")
        return 2
    code, lines = run(paths, strict="--strict" in argv)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
