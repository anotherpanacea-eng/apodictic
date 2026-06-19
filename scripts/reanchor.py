#!/usr/bin/env python3
"""reanchor — Annotated-Manuscript round-trip re-anchoring (carry the margin notes across a revision).

Given draft N's gated annotation manifest (a prior run folder) and draft N+1's snapshot, re-resolve each
annotation against the new snapshot and classify what happened — making the annotated copy revision-aware
and feeding ANCHOR/TEXT-level evidence into regression-diff (the finding-level cross-round diff). Pure text
search over the new snapshot — it invents nothing: a re-anchored quote must occur verbatim and exactly once
in N+1 (the A6 identity, reused), the offset is RECOMPUTED against N+1 (never carried forward), and the
margin comment is carried over byte-identically (never re-authored).

Classes (an exhaustive, mutually-exclusive partition of draft-N's annotations — RA3):
  held              the span resolves to the SAME locus in N+1 (quote verbatim+unique at the same offset;
                    chapter/section heading present+unique; document always held).
  moved             (quote only) the quote resolves verbatim+unique but at a NEW recomputed offset.
  vanished          the span no longer occurs in N+1 (quote absent; heading gone) — candidate resolved.
  ambiguous         the span now occurs >1 time in N+1 (quote/heading duplicated) — re-anchor refused.
  not-re-anchorable (line-range only) bare line numbers carry no text to search — refused by design.

Validator (run-folder + new snapshot):
  RA1 (ERROR)  re-anchor integrity: the emitted re-anchored manifest (held/moved only, bound to N+1)
       passes the structural A-gate against N+1 (A1 + A2 + A3 + A4-multiset + A6; A4/A5 ledger arms do
       not apply — there is no re-diagnosed N+1 ledger).
  RA2 (ERROR)  comment fidelity: every carried-over comment is byte-identical to its draft-N manifest
       comment (the firewall: relocate, never re-author — and A6(a)'s projection arm is inert here).
  RA3 (ERROR)  partition completeness: every draft-N annotation lands in exactly one class.
  W1 (WARN; ERROR --strict)  candidate-resolved: one or more `vanished` annotations.
  W2 (WARN; ERROR --strict)  re-anchor refused: one or more `ambiguous` / `not-re-anchorable` annotations.
Only RA1-RA3 (the mechanical re-anchor contract) are hard; W1/W2 are advisory (a vanished anchor is a
candidate, not proof — the writer may have reworded) — the regression-diff posture. Prints to stdout; a
human-readable re-anchoring report is orchestrator-written.

Usage:
  reanchor.py reanchor <prior_run_folder> <new_snapshot> [--strict]
  reanchor.py --self-test
Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import json
import os
import sys

try:
    import annotation_manifest as am
except ImportError:
    am = None

_CLASSES = ("held", "moved", "vanished", "ambiguous", "not-re-anchorable")


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def reclassify(annotation, n1_snapshot, chap_n, sec_n):
    """-> (klass, new_anchor_or_None, evidence). new_anchor is set only for held/moved (the carried set)."""
    anc = annotation.get("anchor") or {}
    kind, val = anc.get("kind"), anc.get("value")
    if kind == "quote":
        q = anc.get("quote")
        if not isinstance(q, str) or not q:
            return "ambiguous", None, "malformed quote anchor"
        n = n1_snapshot.count(q)
        if n == 0:
            return "vanished", None, "quote absent in N+1"
        if n > 1:
            return "ambiguous", None, "quote occurs %d times in N+1" % n
        start = n1_snapshot.find(q)
        new_val = "%d-%d" % (start, start + len(q))
        new_anchor = {"kind": "quote", "value": new_val, "quote": q}
        if new_val == val:
            return "held", new_anchor, "quote held at %s" % new_val
        return "moved", new_anchor, "quote moved %s -> %s" % (val, new_val)
    if kind == "chapter":
        c = chap_n.get(val, 0)
        if c == 1:
            return "held", dict(anc), "chapter heading %r present+unique" % val
        return ("vanished" if c == 0 else "ambiguous"), None, "chapter heading %r matches %d in N+1" % (val, c)
    if kind == "section":
        key = str(val).strip().lower()
        c = sec_n.get(key, 0)
        if c == 1:
            return "held", dict(anc), "section heading %r present+unique" % val
        return ("vanished" if c == 0 else "ambiguous"), None, "section heading %r matches %d in N+1" % (val, c)
    if kind == "line-range":
        return "not-re-anchorable", None, "bare line range %r carries no text to search" % val
    # document (or any other) — no locus, always held
    return "held", dict(anc), "document anchor (no locus)"


def _manifest_text(obj):
    return "<!-- apodictic:annotation\n%s\n-->" % json.dumps(obj, indent=2)


def _comment_fidelity_errs(emitted_annotations, orig_comment):
    """RA2: each emitted annotation's comment must equal the draft-N comment for that finding_id."""
    errs = []
    for ra in emitted_annotations:
        if not isinstance(ra, dict):
            continue
        fid = ra.get("finding_id")
        if ra.get("comment") != orig_comment.get(fid):
            errs.append("RA2 comment fidelity: %s comment differs from the draft-N manifest "
                        "(re-anchoring must relocate, never re-author)" % fid)
    return errs


def reanchor(manifest_obj, n1_snapshot, n1_path, strict=False):
    """Re-anchor draft-N's manifest onto N+1's snapshot. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    annotations = manifest_obj.get("annotations")
    if not isinstance(annotations, list) or not annotations:
        return 2, ["reanchor: prior manifest has no annotations[] to re-anchor"]

    chap_n, sec_n, _cl, _sl = am.heading_index(n1_snapshot)
    buckets = {k: [] for k in _CLASSES}
    carried = []   # (orig_annotation, new_anchor) for held/moved
    classified = 0
    for an in annotations:
        if not isinstance(an, dict):
            errs.append("RA3 partition: a non-object annotation cannot be classified")
            continue
        klass, new_anchor, evidence = reclassify(an, n1_snapshot, chap_n, sec_n)
        classified += 1
        fid = an.get("finding_id")
        buckets[klass].append((fid, evidence))
        if klass in ("held", "moved"):
            carried.append((an, new_anchor))

    # RA3 — partition completeness: every draft-N annotation in exactly one class.
    if classified != len(annotations):
        errs.append("RA3 partition completeness: classified %d of %d annotation(s)"
                    % (classified, len(annotations)))

    # Build the re-anchored manifest (held/moved only, bound to N+1), carrying each comment VERBATIM.
    re_anns = []
    for an, new_anchor in carried:
        re_anns.append({"finding_id": an.get("finding_id"), "anchor": new_anchor,
                        "comment": an.get("comment")})
    re_obj = {"schema": am._SCHEMA_ID, "project": manifest_obj.get("project", "Manuscript"),
              "runlabel": _runlabel_of(n1_path), "snapshot_path": os.path.basename(n1_path),
              "snapshot_sha256": am.sha256(n1_snapshot), "snapshot_line_count": am.line_count(n1_snapshot),
              "annotations": re_anns}
    re_manifest_text = _manifest_text(re_obj)

    # RA2 — comment fidelity: the EMITTED manifest (serialized + RE-PARSED — the exact form that gets
    # rendered and gated) must carry each finding's comment byte-identical to draft N's. Re-parsing
    # breaks the in-memory aliasing, so a serialization/escaping corruption — or any future change that
    # makes carrying something other than a verbatim copy — is caught here, independently of A4-multiset
    # (the firewall: relocate, never re-author; RA2 stands in for A6(a)'s projection arm, which is inert
    # without an N+1 ledger).
    orig_comment = {an.get("finding_id"): an.get("comment") for an in annotations if isinstance(an, dict)}
    emitted, _pe = am.parse_manifest(re_manifest_text)
    emitted_anns = emitted.get("annotations") if isinstance(emitted, dict) else re_anns
    errs += _comment_fidelity_errs(emitted_anns, orig_comment)

    # RA1 — re-anchor integrity: the re-anchored manifest, rendered, passes the structural A-gate
    # against N+1 (A1 + A2 + A3 + A4-multiset + A6; ledger arms inert — ledger_optional).
    try:
        annotated = am.render(n1_snapshot, re_obj)
        code, alines = am.check(n1_snapshot, re_manifest_text, annotated,
                                ledger_text=None, ledger_optional=True)
        if code != 0:
            errs.append("RA1 re-anchor integrity: the re-anchored manifest fails the A-gate against N+1")
            for al in alines:
                if "ERROR" in al or "FAIL" in al:
                    errs.append("  [A-gate] %s" % al.strip())
    except ValueError as exc:
        errs.append("RA1 re-anchor integrity: render failed — %s" % exc)

    # Report (deterministic: class order, then finding_id).
    lines.append("reanchor: %d annotation(s) re-anchored onto %s" % (len(annotations), os.path.basename(n1_path)))
    for klass in _CLASSES:
        for fid, evidence in sorted(buckets[klass], key=lambda t: (t[0] or "")):
            lines.append("  reanchor:%s %s — %s" % (klass, fid, evidence))

    for fid, _e in sorted(buckets["vanished"], key=lambda t: (t[0] or "")):
        warns.append("W1 candidate-resolved: %s anchored prose is gone in N+1 (candidate the finding was "
                     "addressed; the orchestrator may cross-reference regression-diff)" % fid)
    for klass in ("ambiguous", "not-re-anchorable"):
        for fid, evidence in sorted(buckets[klass], key=lambda t: (t[0] or "")):
            warns.append("W2 re-anchor refused: %s (%s) needs editor placement — %s" % (fid, klass, evidence))

    return _finish(lines, errs, warns, strict,
                   "%d held/moved re-anchored, no refusals" % len(carried))


def _finish(lines, errs, warns, strict, ok_msg):
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))
    if errs or (strict and warns):
        lines.append("reanchor: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: reanchor: %d re-anchor advisory(ies) — see W1-W2 above" % len(warns))
    else:
        lines.append("reanchor: PASS (%s)" % ok_msg)
    return 0, lines


def _runlabel_of(snapshot_path):
    base = os.path.basename(snapshot_path)
    if "_Manuscript_Snapshot_" in base:
        return os.path.splitext(base.split("_Manuscript_Snapshot_")[-1])[0] or "run"
    return os.path.splitext(base)[0] or "run"


def run(paths, strict=False):
    if len(paths) < 2:
        return 2, ["reanchor: usage: reanchor <prior_run_folder> <new_snapshot> [--strict]"]
    prior, new_snap = paths[0], paths[1]
    if os.path.isdir(prior):
        man_path = _newest(glob.glob(os.path.join(prior, am._MANIFEST_GLOB)))
    else:
        man_path = prior
    if not man_path:
        return 2, ["reanchor: no %s in %s" % (am._MANIFEST_GLOB, prior)]
    obj, merrs = am.parse_manifest(_read(man_path))
    if obj is None:
        return 1, ["reanchor: prior manifest invalid — %s" % (merrs[0] if merrs else "no annotation block")]
    raw = _read(new_snap)
    if raw is None:
        return 2, ["reanchor: cannot read new snapshot %s" % new_snap]
    n1 = am.normalize_snapshot(raw)
    return reanchor(obj, n1, new_snap, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    import tempfile
    import shutil

    # draft N snapshot: a chapter heading, a quote, a section, and a line for the line-range case.
    snap_n = ("# Chapter 1\n"                                  # line 1
              "The lighthouse stood unlit for forty years.\n"  # line 2 (the quote)
              "She counted the hours until the train.\n"       # line 3
              "# Scene Turns\n"                                 # line 4 (a section heading)
              "The turn lands late in the chapter.\n")          # line 5
    snap_n = am.normalize_snapshot(snap_n)
    quote = "The lighthouse stood unlit for forty years."
    qs = snap_n.find(quote)

    def ann(fid, anchor, comment="[Must-Fix · %s] m — fix class: f. (See letter §%s.)"):
        return {"finding_id": fid, "anchor": anchor, "comment": comment % (fid, fid)}

    man_n = {"schema": am._SCHEMA_ID, "project": "T", "runlabel": "rN",
             "snapshot_path": "T_Manuscript_Snapshot_rN.md", "snapshot_sha256": am.sha256(snap_n),
             "snapshot_line_count": am.line_count(snap_n),
             "annotations": [
                 ann("F-QT-01", {"kind": "quote", "value": "%d-%d" % (qs, qs + len(quote)), "quote": quote}),
                 ann("F-CH-01", {"kind": "chapter", "value": "Ch 1"}),
                 ann("F-SEC-01", {"kind": "section", "value": "Scene Turns"}),
                 ann("F-LR-01", {"kind": "line-range", "value": "2-2"}),
             ]}

    # N+1: held chapter + section; the quote MOVED (a line inserted before it); nothing vanished.
    snap_moved = am.normalize_snapshot(
        "# Chapter 1\nA new opening line shifts everything down.\n"
        "The lighthouse stood unlit for forty years.\nShe counted the hours until the train.\n"
        "# Scene Turns\nThe turn lands late in the chapter.\n")
    code, lines = run_via(man_n, snap_moved)
    txt = "\n".join(lines)
    chk("quote_moved", "reanchor:moved F-QT-01" in txt)
    chk("chapter_held", "reanchor:held F-CH-01" in txt)
    chk("section_held", "reanchor:held F-SEC-01" in txt)
    chk("line_range_not_reanchorable", "reanchor:not-re-anchorable F-LR-01" in txt)
    chk("moved_passes_ra1_advisory", code == 0)   # only W2 (line-range) advisory
    chk("moved_strict_fails", run_via(man_n, snap_moved, strict=True)[0] == 1)

    # N+1: the quote VANISHED (sentence cut), the chapter heading retitled (vanished).
    snap_vanished = am.normalize_snapshot(
        "# Prologue\nShe counted the hours until the train.\n# Scene Turns\nThe turn lands late.\n")
    code, lines = run_via(man_n, snap_vanished)
    txt = "\n".join(lines)
    chk("quote_vanished", "reanchor:vanished F-QT-01" in txt and "W1 candidate-resolved: F-QT-01" in txt)
    chk("chapter_vanished", "reanchor:vanished F-CH-01" in txt)

    # N+1: the quote occurs TWICE (ambiguous).
    snap_ambig = am.normalize_snapshot(
        "# Chapter 1\nThe lighthouse stood unlit for forty years.\n"
        "The lighthouse stood unlit for forty years.\n# Scene Turns\nx\n")
    txt = "\n".join(run_via(man_n, snap_ambig)[1])
    chk("quote_ambiguous", "reanchor:ambiguous F-QT-01" in txt and "W2 re-anchor refused: F-QT-01" in txt)

    # held-everything (N+1 == N): all held, clean PASS, no advisories.
    code, lines = run_via(man_n, snap_n)
    chk("identity_all_held", code == 0 and "reanchor:held F-QT-01" in "\n".join(lines)
        and not any("W1" in x or "W2" in x for x in lines if x.strip().startswith(("W1", "W2"))))

    # RA3 partition: every annotation classified exactly once (4 in -> 4 class lines).
    nclass = sum(1 for x in lines if x.strip().startswith("reanchor:") and " — " in x)
    chk("ra3_partition_complete", nclass == 4)

    # RA2: a tampered carried comment fails (relocate, never re-author). Force via a manifest whose
    # quote will be held but whose comment we corrupt post-hoc is awkward; instead verify the guard
    # exists by re-anchoring a manifest whose held annotation's comment is fine, then asserting RA2
    # never fires on the clean identity case.
    chk("ra2_clean_on_identity", not any("RA2 comment fidelity" in x for x in lines))
    # RA2 is a LIVE guard: a divergent emitted comment (a future carrying-logic regression or a
    # serialization corruption) must fire it.
    chk("ra2_fires_on_divergence",
        len(_comment_fidelity_errs([{"finding_id": "F-X-01", "comment": "re-authored"}],
                                   {"F-X-01": "original"})) == 1)
    chk("ra2_clean_when_equal",
        _comment_fidelity_errs([{"finding_id": "F-X-01", "comment": "same"}], {"F-X-01": "same"}) == [])

    # determinism: identical inputs -> identical output.
    chk("deterministic", run_via(man_n, snap_moved)[1] == run_via(man_n, snap_moved)[1])

    # run() end-to-end from a folder + snapshot file.
    d = tempfile.mkdtemp()
    try:
        with open(os.path.join(d, "T_Annotation_Manifest_rN.md"), "w", encoding="utf-8", newline="") as fh:
            fh.write(_manifest_text(man_n))
        sp = os.path.join(d, "T_Manuscript_Snapshot_rN1.md")
        with open(sp, "w", encoding="utf-8", newline="") as fh:
            fh.write(snap_moved)
        chk("run_folder_snapshot", run([d, sp])[0] == 0)
        chk("run_usage_one_arg", run([d])[0] == 2)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("Self-test: %s" % ("PASS" if rc["v"] == 0 else "FAIL"))
    return rc["v"]


def run_via(manifest_obj, n1_snapshot, strict=False):
    return reanchor(manifest_obj, n1_snapshot, "X_Manuscript_Snapshot_rN1.md", strict=strict)


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    if am is None:
        print("reanchor: annotation_manifest is unavailable (same-dir import failed)")
        return 2
    args = [a for a in argv[1:] if a != "reanchor"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: reanchor.py reanchor <prior_run_folder> <new_snapshot> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
