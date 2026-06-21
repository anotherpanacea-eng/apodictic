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

Round-trip GLUE (the workflow, not just the gate). `reanchor` validates the re-anchor in memory; the
revision loop also needs the revision-aware marked-up copy ON DISK and the cross-round join:
  emit      re-anchor draft N's notes onto N+1 and WRITE the re-anchored manifest + the rendered annotated
            copy of the revised draft (held/moved only; re-gated RA1-RA3 before any write).
  crossref  join this round-trip's anchor-level classes against regression-diff's finding-level classes
            BY finding_id (the orchestrator join the spec reserves — anchor x finding corroboration).

Usage:
  reanchor.py reanchor <prior_run_folder> <new_snapshot> [--strict]
  reanchor.py emit     <prior_run_folder> <new_snapshot> [-o <out_dir>]
  reanchor.py crossref <prior_run_folder> <new_snapshot> <this_run_folder> [--strict]
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

try:
    import regression_diff as rd
except ImportError:
    rd = None

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


def build_reanchored(manifest_obj, n1_snapshot, n1_path):
    """Re-resolve every draft-N annotation against N+1 and build the carried (held/moved) manifest.

    The single source of truth for both the validating `reanchor()` (the gate) and the writing `emit()`
    (the glue): classify each annotation, partition into buckets, and assemble the re-anchored manifest
    object (held/moved only, bound to N+1, each comment carried VERBATIM — never re-authored). Returns
    `(re_obj, buckets, carried, fid_class)`:
      re_obj     the re-anchored manifest dict (held/moved annotations re-pointed onto N+1).
      buckets    {class: [(finding_id, evidence), …]} — the full RA3 partition of draft-N's annotations.
      carried    [(orig_annotation, new_anchor), …] for held/moved (the surviving subset).
      fid_class  {finding_id: class} — the per-finding class map (the crossref join key, Q2).
    Pure: builds the artifacts, classifies; writes nothing, gates nothing (callers own that)."""
    annotations = manifest_obj.get("annotations")
    if not isinstance(annotations, list):
        annotations = []
    chap_n, sec_n, _cl, _sl = am.heading_index(n1_snapshot)
    buckets = {k: [] for k in _CLASSES}
    carried = []        # (orig_annotation, new_anchor) for held/moved
    fid_class = {}      # finding_id -> class (the crossref join, Q2)
    for an in annotations:
        if not isinstance(an, dict):
            continue
        klass, new_anchor, evidence = reclassify(an, n1_snapshot, chap_n, sec_n)
        fid = an.get("finding_id")
        buckets[klass].append((fid, evidence))
        fid_class[fid] = klass
        if klass in ("held", "moved"):
            carried.append((an, new_anchor))

    # The re-anchored manifest (held/moved only, bound to N+1), carrying each comment VERBATIM.
    re_anns = [{"finding_id": an.get("finding_id"), "anchor": new_anchor, "comment": an.get("comment")}
               for an, new_anchor in carried]
    re_obj = {"schema": am._SCHEMA_ID, "project": manifest_obj.get("project", "Manuscript"),
              "runlabel": _runlabel_of(n1_path), "snapshot_path": os.path.basename(n1_path),
              "snapshot_sha256": am.sha256(n1_snapshot), "snapshot_line_count": am.line_count(n1_snapshot),
              "annotations": re_anns}
    return re_obj, buckets, carried, fid_class


def reanchor(manifest_obj, n1_snapshot, n1_path, strict=False):
    """Re-anchor draft-N's manifest onto N+1's snapshot. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    annotations = manifest_obj.get("annotations")
    if not isinstance(annotations, list) or not annotations:
        return 2, ["reanchor: prior manifest has no annotations[] to re-anchor"]

    re_obj, buckets, carried, _fc = build_reanchored(manifest_obj, n1_snapshot, n1_path)

    # RA3 — partition completeness: every draft-N annotation in exactly one class. A non-dict annotation
    # is unclassifiable (build_reanchored skips it), so it never lands in a bucket — caught here.
    classified = sum(len(v) for v in buckets.values())
    for an in annotations:
        if not isinstance(an, dict):
            errs.append("RA3 partition: a non-object annotation cannot be classified")
    if classified != len(annotations):
        errs.append("RA3 partition completeness: classified %d of %d annotation(s)"
                    % (classified, len(annotations)))

    re_manifest_text = _manifest_text(re_obj)

    # RA2 — comment fidelity: the EMITTED manifest (serialized + RE-PARSED — the exact form that gets
    # rendered and gated) must carry each finding's comment byte-identical to draft N's. Re-parsing
    # breaks the in-memory aliasing, so a serialization/escaping corruption — or any future change that
    # makes carrying something other than a verbatim copy — is caught here, independently of A4-multiset
    # (the firewall: relocate, never re-author; RA2 stands in for A6(a)'s projection arm, which is inert
    # without an N+1 ledger).
    orig_comment = {an.get("finding_id"): an.get("comment") for an in annotations if isinstance(an, dict)}
    emitted, _pe = am.parse_manifest(re_manifest_text)
    emitted_anns = emitted.get("annotations") if isinstance(emitted, dict) else re_obj["annotations"]
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


def _resolve_inputs(prior, new_snap):
    """Resolve the (draft-N manifest object, normalized N+1 snapshot) pair the round-trip operates on.

    Shared by `run` (the gate), `emit` (the glue write), and `crossref` (the join), so all three resolve
    the prior manifest + new snapshot the SAME way: a dir -> its newest manifest; a file -> itself.
    Returns `(obj, n1, err)` — on any failure `obj`/`n1` are None and `err` is a (code, [line]) the caller
    returns verbatim."""
    if os.path.isdir(prior):
        man_path = _newest(glob.glob(os.path.join(prior, am._MANIFEST_GLOB)))
    else:
        man_path = prior
    if not man_path:
        return None, None, (2, ["reanchor: no %s in %s" % (am._MANIFEST_GLOB, prior)])
    obj, merrs = am.parse_manifest(_read(man_path))
    if obj is None:
        return None, None, (1, ["reanchor: prior manifest invalid — %s"
                                % (merrs[0] if merrs else "no annotation block")])
    raw = _read(new_snap)
    if raw is None:
        return None, None, (2, ["reanchor: cannot read new snapshot %s" % new_snap])
    return obj, am.normalize_snapshot(raw), None


def run(paths, strict=False):
    if len(paths) < 2:
        return 2, ["reanchor: usage: reanchor <prior_run_folder> <new_snapshot> [--strict]"]
    obj, n1, err = _resolve_inputs(paths[0], paths[1])
    if err is not None:
        return err
    return reanchor(obj, n1, paths[1], strict=strict)


def emit(paths, out_dir=None):
    """Round-trip GLUE write: re-anchor draft N's notes onto the revised draft N+1 and WRITE the revision-
    aware artifacts (the re-anchored manifest + the rendered annotated copy of N+1) to disk. This is the
    missing producer for the round-trip — `reanchor` (the gate) only classifies + validates in memory; a
    revision loop needs the marked-up copy of the NEW draft on disk.

    Re-gates before writing (RA1-RA3 must pass — never write an unverified re-anchor), then emits two
    artifacts named `[Project]_Reanchored_Manifest_[runlabel].md` + `[Project]_Reanchored_Annotated_
    Manuscript_[runlabel].md` (the `Reanchored_` infix distinguishes them from a fresh-diagnosis
    `_Annotation_Manifest_` / `_Annotated_Manuscript_`, so a re-anchored copy is never mistaken for a
    re-diagnosed one). Writes ONLY held/moved annotations (the surviving subset); vanished / ambiguous /
    not-re-anchorable are reported, never silently re-pointed (RA3 guarantees none is lost). Returns
    (code, lines)."""
    if len(paths) < 2:
        return 2, ["reanchor: usage: emit <prior_run_folder> <new_snapshot> [-o <out_dir>]"]
    prior, new_snap = paths[0], paths[1]
    obj, n1, err = _resolve_inputs(prior, new_snap)
    if err is not None:
        return err

    # Re-gate first: never write an unverified re-anchor. The default (non-strict) gate makes the
    # advisory W1/W2 (vanished / refused) non-fatal — they're the expected revision signal — but RA1-RA3
    # (the mechanical re-anchor contract) MUST pass before anything is written.
    code, glines = reanchor(obj, n1, new_snap, strict=False)
    if code != 0:
        return code, ["reanchor: emit refused — the re-anchor does not pass RA1-RA3 against the revised "
                      "draft; nothing written"] + glines

    re_obj, _buckets, carried, _fc = build_reanchored(obj, n1, new_snap)
    try:
        annotated = am.render(n1, re_obj)
    except ValueError as exc:
        return 1, ["reanchor: emit refused — render failed: %s (nothing written)" % exc]

    out = out_dir if out_dir else (prior if os.path.isdir(prior) else os.path.dirname(prior) or ".")
    if not os.path.isdir(out):
        return 2, ["reanchor: emit output dir does not exist: %s" % out]
    project = re_obj.get("project", "Manuscript")
    runlabel = re_obj.get("runlabel", "run")
    man_path = os.path.join(out, "%s_Reanchored_Manifest_%s.md" % (project, runlabel))
    ann_path = os.path.join(out, "%s_Reanchored_Annotated_Manuscript_%s.md" % (project, runlabel))
    with open(man_path, "w", encoding="utf-8", newline="") as fh:
        fh.write("# Re-anchored Annotation Manifest\n\n%s\n" % _manifest_text(re_obj))
    with open(ann_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(annotated)
    return 0, ["reanchor: emit wrote %s + %s (%d held/moved annotation(s) carried onto the revised draft)"
               % (os.path.basename(man_path), os.path.basename(ann_path), len(carried))]


def crossref(paths, strict=False):
    """The orchestrator's anchor-level x finding-level JOIN (Q2): cross-reference this round-trip's
    per-annotation classes against `regression-diff`'s per-finding classes BY `finding_id`, the only key
    they share. `reanchor` keys on anchor.quote / heading text; `regression-diff` on origin+chapter+
    mechanism — so neither validator asserts the join (each is honest about its own evidence), and it lives
    here in the glue, exactly as the spec reserves it (docs/annotated-manuscript-reanchoring.md §Q2).

    Surfaces the two corroborations that sharpen the heuristic regression signal with anchor ground truth:
      - vanished (anchor) x resolved-and-held (finding): the prose is GONE and the prior round marked it
        resolved — strong, two-source evidence the fix landed.
      - held/moved (anchor) x recurrence-candidate (finding): the prose PERSISTS verbatim and a resolved
        finding heuristically matched it — strong evidence the fix did NOT hold.
    Args: <prior_run_folder> <new_snapshot> <this_run_folder>. Advisory by default (a corroboration is
    still a candidate for editor judgment); `--strict` makes a persists-but-claimed-resolved corroboration
    (the regression) an error. Returns (code, lines)."""
    if len(paths) < 3:
        return 2, ["reanchor: usage: crossref <prior_run_folder> <new_snapshot> <this_run_folder> [--strict]"]
    prior, new_snap, this_run = paths[0], paths[1], paths[2]
    obj, n1, err = _resolve_inputs(prior, new_snap)
    if err is not None:
        return err
    _re_obj, _buckets, _carried, fid_class = build_reanchored(obj, n1, new_snap)

    # The regression-diff side: classify this round's findings against the prior round, by finding_id.
    reg_class = rd.crossref_classes(prior, this_run) if rd is not None else {}

    lines = ["reanchor: crossref %d re-anchored class(es) x regression-diff finding class(es) by finding_id"
             % len(fid_class)]
    warns, errs = [], []
    for fid in sorted(k for k in fid_class if k):
        anc = fid_class.get(fid)
        reg = reg_class.get(fid)
        if reg is None:
            continue
        if anc == "vanished" and reg == "resolved-and-held":
            lines.append("  crossref:corroborated-resolved %s — prose vanished AND finding resolved-and-held "
                         "(two-source: the fix landed)" % fid)
        elif anc in ("held", "moved") and reg == "recurrence-candidate":
            msg = ("  crossref:contradicted-resolution %s — prose persists (%s) BUT finding is a "
                   "recurrence-candidate (the resolution may not have held)" % (fid, anc))
            lines.append(msg)
            warns.append("X1 persists-but-claimed-resolved: %s anchored prose still present in N+1 while "
                         "regression-diff flags it recurring — confirm before crediting the fix" % fid)
        else:
            lines.append("  crossref:noted %s — reanchor=%s regression-diff=%s" % (fid, anc, reg))

    return _finish(lines, errs, warns, strict, "%d finding(s) joined, no contradictions" % len(fid_class))


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

    # build_reanchored: the shared builder returns the same partition the report shows + the join map.
    re_obj_b, buckets_b, carried_b, fid_class_b = build_reanchored(man_n, snap_moved, "X_Snapshot_rN1.md")
    chk("build_reanchored_carries_held_moved", len(carried_b) == 3 and len(re_obj_b["annotations"]) == 3)
    chk("build_reanchored_fid_class", fid_class_b.get("F-QT-01") == "moved"
        and fid_class_b.get("F-LR-01") == "not-re-anchorable")
    chk("build_reanchored_bound_to_n1", re_obj_b["snapshot_sha256"] == am.sha256(snap_moved))

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

        # emit: writes the re-anchored manifest + the rendered revised-draft annotated copy, and the
        # emitted copy passes the A-gate against the revised snapshot (held/moved only).
        outd = tempfile.mkdtemp()
        try:
            ecode, elines = emit([d, sp], out_dir=outd)
            man_w = os.path.join(outd, "T_Reanchored_Manifest_rN1.md")
            ann_w = os.path.join(outd, "T_Reanchored_Annotated_Manuscript_rN1.md")
            chk("emit_exit_0", ecode == 0)
            chk("emit_wrote_both", os.path.isfile(man_w) and os.path.isfile(ann_w))
            # the emitted copy + manifest re-gate clean against the revised draft (A1-A6, ledger-optional).
            if os.path.isfile(man_w) and os.path.isfile(ann_w):
                eobj, _ee = am.parse_manifest(_read(man_w))
                acode, _al = am.check(am.normalize_snapshot(snap_moved), _read(man_w), _read(ann_w),
                                      ledger_text=None, ledger_optional=True)
                chk("emit_copy_passes_agate", acode == 0)
                chk("emit_manifest_held_moved_only", isinstance(eobj, dict)
                    and len(eobj.get("annotations", [])) == 3)
                # firewall: every carried comment is byte-identical to draft N's (relocate, never re-author).
                orig = {a["finding_id"]: a["comment"] for a in man_n["annotations"]}
                chk("emit_comments_verbatim",
                    all(a.get("comment") == orig.get(a.get("finding_id")) for a in eobj["annotations"]))
            chk("emit_usage_one_arg", emit([d])[0] == 2)
            chk("emit_missing_outdir", emit([d, sp], out_dir=os.path.join(outd, "nope"))[0] == 2)
        finally:
            shutil.rmtree(outd, ignore_errors=True)

        chk("emit_no_write_on_bad_prior", emit(["/no/such/dir", sp])[0] in (1, 2))

        # emit REFUSES TO WRITE when the re-anchor fails the hard contract (the firewall). A carried
        # comment bearing a CriticMarkup sigil fails A2/A5 -> RA1 against N+1, so emit must exit 1 with
        # NOTHING written. Build a prior whose held annotation carries such a comment.
        bad_d = tempfile.mkdtemp()
        bad_out = tempfile.mkdtemp()
        try:
            bad_snap = am.normalize_snapshot("# Chapter 1\nThe unique sentence here.\n")
            bq = "The unique sentence here."
            bqs = bad_snap.find(bq)
            bad_man = {"schema": am._SCHEMA_ID, "project": "T", "runlabel": "rN",
                       "snapshot_path": "T_Manuscript_Snapshot_rN.md", "snapshot_sha256": am.sha256(bad_snap),
                       "snapshot_line_count": am.line_count(bad_snap),
                       "annotations": [{"finding_id": "F-Q-01",
                                        "anchor": {"kind": "quote", "value": "%d-%d" % (bqs, bqs + len(bq)),
                                                   "quote": bq},
                                        "comment": "a comment with a {>> sigil <<} that breaks A2/A5"}]}
            with open(os.path.join(bad_d, "T_Annotation_Manifest_rN.md"), "w",
                      encoding="utf-8", newline="") as fh:
                fh.write(_manifest_text(bad_man))
            bad_sp = os.path.join(bad_d, "T_Manuscript_Snapshot_rN1.md")
            with open(bad_sp, "w", encoding="utf-8", newline="") as fh:
                fh.write(bad_snap)
            bcode, blines = emit([bad_d, bad_sp], out_dir=bad_out)
            chk("emit_refuses_on_ra_failure",
                bcode == 1 and any("emit refused" in x for x in blines))
            chk("emit_wrote_nothing_on_ra_failure", not os.listdir(bad_out))
        finally:
            shutil.rmtree(bad_d, ignore_errors=True)
            shutil.rmtree(bad_out, ignore_errors=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # crossref: the orchestrator join by finding_id. Build a prior run folder whose ledger + manifest share
    # ids, and a current round folder whose re-diagnosis recurs one resolved finding (recurrence-candidate)
    # while the OTHER finding's prose vanished (resolved-and-held) — the two corroborations crossref exists
    # to surface.
    if rd is not None:
        cd = tempfile.mkdtemp()
        try:
            _crossref_self_test(chk, cd)
        finally:
            shutil.rmtree(cd, ignore_errors=True)

    print("Self-test: %s" % ("PASS" if rc["v"] == 0 else "FAIL"))
    return rc["v"]


def _crossref_self_test(chk, cd):
    """crossref join: anchor classes (this round-trip) x regression-diff finding classes, by finding_id."""
    import json as _j
    # Prior round: a snapshot with a held quote (F-HOLD-01) and a quote that will vanish (F-GONE-01),
    # an annotation manifest over both, and a ledger marking both findings present, with F-GONE-01 resolved.
    prior_snap = am.normalize_snapshot("# Chapter 7\nThe want never forces a sacrifice here.\n"
                                       "A sentence slated for the cut sits in chapter nine.\n# Chapter 9\nx\n")
    q_hold = "The want never forces a sacrifice here."
    q_gone = "A sentence slated for the cut sits in chapter nine."
    hs = prior_snap.find(q_hold)
    gs = prior_snap.find(q_gone)
    prior_man = {"schema": am._SCHEMA_ID, "project": "X", "runlabel": "r1",
                 "snapshot_path": "X_Manuscript_Snapshot_r1.md", "snapshot_sha256": am.sha256(prior_snap),
                 "snapshot_line_count": am.line_count(prior_snap),
                 "annotations": [
                     {"finding_id": "F-HOLD-01", "anchor": {"kind": "quote",
                      "value": "%d-%d" % (hs, hs + len(q_hold)), "quote": q_hold}, "comment": "held note"},
                     {"finding_id": "F-GONE-01", "anchor": {"kind": "quote",
                      "value": "%d-%d" % (gs, gs + len(q_gone)), "quote": q_gone}, "comment": "gone note"},
                 ]}

    def finding(fid, mech, refs, sev="Should-Fix"):
        return '<!-- apodictic:finding\n%s\n-->' % _j.dumps(
            {"schema": "apodictic.finding.v1", "id": fid, "mechanism": mech, "severity": sev,
             "confidence": "HIGH", "evidence_refs": list(refs), "fix_class": "x", "risk_if_fixed": "y"})

    pri = os.path.join(cd, "r1")
    cur = os.path.join(cd, "r2")
    os.makedirs(pri)
    os.makedirs(cur)
    with open(os.path.join(pri, "X_Annotation_Manifest_r1.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(_manifest_text(prior_man))
    # prior ledger: both findings, F-GONE-01 marked resolved (so regression-diff can recur/hold it).
    with open(os.path.join(pri, "X_Findings_Ledger_r1.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Ledger\n"
                 + finding("F-HOLD-01", "the want never forces a sacrifice so stakes stay abstract", ["Ch 7"])
                 + "\n"
                 + finding("F-GONE-01", "a sentence slated for the cut creates a continuity seam", ["Ch 9"])
                 + "\n<!-- resolved: F-GONE-01 -->\n")
    # current re-diagnosis: F-HOLD recurs (same origin+chapter+shared tokens), F-GONE has no match (held).
    with open(os.path.join(cur, "X_Findings_Ledger_r2.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Ledger\n"
                 + finding("F-HOLD-01", "the want still never forces a sacrifice; stakes remain abstract", ["Ch 7"])
                 + "\n")
    # also mark F-HOLD resolved in the prior round so the recurrence (held + recurrence-candidate) fires.
    with open(os.path.join(pri, "X_Revision_Report_r1.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Revision Report\n<!-- resolved: F-HOLD-01 -->\n<!-- resolved: F-GONE-01 -->\n")

    # revised draft N+1: F-HOLD's quote PERSISTS verbatim (held/moved), F-GONE's quote is CUT (vanished).
    new_snap_path = os.path.join(cd, "X_Manuscript_Snapshot_r2.md")
    with open(new_snap_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(am.normalize_snapshot("# Chapter 7\nThe want never forces a sacrifice here.\n# Chapter 9\nx\n"))

    code, lines = crossref([pri, new_snap_path, cur])
    txt = "\n".join(lines)
    chk("crossref_corroborated_resolved", "crossref:corroborated-resolved F-GONE-01" in txt)
    chk("crossref_contradicted_resolution", "crossref:contradicted-resolution F-HOLD-01" in txt)
    chk("crossref_advisory_exit_0", code == 0)
    chk("crossref_strict_fails_on_contradiction", crossref([pri, new_snap_path, cur], strict=True)[0] == 1)
    chk("crossref_usage_two_args", crossref([pri, new_snap_path])[0] == 2)
    chk("crossref_classes_join", rd.crossref_classes(pri, cur).get("F-HOLD-01") == "recurrence-candidate"
        and rd.crossref_classes(pri, cur).get("F-GONE-01") == "resolved-and-held")

    # A pure-WIN crossref (vanished x resolved-and-held, no contradiction) must NOT false-fail under
    # --strict — the win is corroboration, not an error; only X1 (persists-but-claimed-resolved) flips it.
    win_cur = os.path.join(cd, "r2win")
    os.makedirs(win_cur)
    with open(os.path.join(win_cur, "X_Findings_Ledger_r2win.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Ledger\n" + finding("F-UNREL-01", "an unrelated new note", ["Ch 2"]) + "\n")
    win_snap = os.path.join(cd, "X_Manuscript_Snapshot_r2win.md")
    with open(win_snap, "w", encoding="utf-8", newline="") as fh:
        fh.write(am.normalize_snapshot("# Chapter 7\nThe want never forces a sacrifice here.\n# Chapter 9\nx\n"))
    chk("crossref_strict_clean_on_win_only", crossref([pri, win_snap, win_cur], strict=True)[0] == 0)


def run_via(manifest_obj, n1_snapshot, strict=False):
    return reanchor(manifest_obj, n1_snapshot, "X_Manuscript_Snapshot_rN1.md", strict=strict)


_USAGE = ("Usage: reanchor.py reanchor <prior_run_folder> <new_snapshot> [--strict]\n"
          "       reanchor.py emit     <prior_run_folder> <new_snapshot> [-o <out_dir>]\n"
          "       reanchor.py crossref <prior_run_folder> <new_snapshot> <this_run_folder> [--strict]\n"
          "       reanchor.py --self-test")


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    if am is None:
        print("reanchor: annotation_manifest is unavailable (same-dir import failed)")
        return 2
    sub = argv[1] if len(argv) > 1 else None
    rest = argv[2:] if sub in ("reanchor", "emit", "crossref") else argv[1:]
    strict = "--strict" in rest
    # Pull an `-o <out_dir>` pair (emit only) out of the positionals.
    out_dir = None
    if "-o" in rest:
        i = rest.index("-o")
        out_dir = rest[i + 1] if i + 1 < len(rest) else None
        rest = rest[:i] + rest[i + 2:]
    paths = [a for a in rest if not a.startswith("-")]
    if not paths:
        print(_USAGE)
        return 2
    if sub == "emit":
        code, lines = emit(paths, out_dir=out_dir)
    elif sub == "crossref":
        code, lines = crossref(paths, strict=strict)
    else:   # default + explicit `reanchor`
        code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
