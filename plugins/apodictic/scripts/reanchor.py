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

Disposition record (round-close). The `/start` round-trip resume ends in a per-finding disposition table
the OPERATOR confirms — the model proposes; the operator disposes. The orchestrator-written record
(`[Project]_Roundtrip_Disposition_[runlabel].md`, marker-based) is gated by `disposition`:
  RT1 (ERROR)  recompute alignment: every row's finding_id is in the prior manifest's RA3 partition
       (recomputed live, never trusted from the record), its anchor= class equals the recomputed class,
       its regression= class (when not `none`) equals the recomputed crossref class, and the `compares:`
       header names the actual prior/this runlabels. No stale or fabricated evidence classes.
  RT2 (ERROR)  confirmation record present: any row decided (decision != pending) requires the file-level
       `<!-- disposition-confirmed: operator <ts> -->` token. This proves the RECORD of confirmation
       exists and is consistent — a bash/py validator cannot prove a human confirmed (the honesty
       ceiling); rev-a4 (`gate --attest`) is the human-attestation layer.
  RT3 (ERROR)  confirmed-writes-only: when a disposition record exists, every `<!-- resolved: F-… -->`
       marker in the run folder's Revision Report(s) whose id is in the RA3 partition corresponds to a
       decision=confirm-resolved row — an unconfirmed close (vanished-anchor auto-close) is the error
       this gate exists to prevent. Marker parse reuses finding_trace.resolved_cited_ids (never
       reimplemented).
  RT4 (WARN; ERROR --strict)  partition coverage: every finding id in the recomputed RA3 partition has
       a disposition row — a record that exists is a round-close record (carry-only writes none), so a
       missing row is a finding silently omitted from round-close review; reported by id.
  W1 (WARN; ERROR --strict)  unadjudicated / staged: rows still pending, or confirm-resolved rows not
       yet reflected as resolved markers (work legitimately stages across sessions).

Usage:
  reanchor.py reanchor    <prior_run_folder> <new_snapshot> [--strict]
  reanchor.py emit        <prior_run_folder> <new_snapshot> [-o <out_dir>]
  reanchor.py crossref    <prior_run_folder> <new_snapshot> <this_run_folder> [--strict]
  reanchor.py disposition <prior_run_folder> <new_snapshot> <this_run_folder> [--strict]
  reanchor.py --self-test
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
    import regression_diff as rd
except ImportError:
    rd = None

try:
    import finding_trace as ft
except ImportError:
    ft = None

_CLASSES = ("held", "moved", "vanished", "ambiguous", "not-re-anchorable")

# ---- Roundtrip Disposition record (the round-close operator record; marker-based, no schema file) ----
_DISPOSITION_GLOB = "*_Roundtrip_Disposition_*.md"
_REVISION_REPORT_GLOB = "*_Revision_Report_*.md"
# regression= values a row may record: the prior-keyed crossref classes (regression_diff.
# _PRIOR_KEYED_CLASSES — incl. `unexplained-drop`, which the recompute really yields for a prior
# finding with no current match and no resolution claim), the current-keyed classes the record
# grammar names for completeness (`new` / `new-in-quiet-chapter` — never joinable to a prior id, so
# RT1 fails them against the recompute), and `none` (no crossref join — e.g. a carry-only round).
_DISPO_REGRESSION = ("persisted", "resolved-and-held", "recurrence-candidate", "unexplained-drop",
                     "new", "new-in-quiet-chapter", "none")
_DISPO_DECISIONS = ("confirm-resolved", "keep-open", "needs-placement", "declined", "pending")
# `disposition:` requires the colon immediately after the word, so the `disposition-confirmed:`
# token can never be swallowed as a row.
_DISPO_ANY_RE = re.compile(r"<!--\s*disposition:(.*?)-->", re.DOTALL)
_DISPO_ROW_RE = re.compile(
    r"\A(?P<fid>\S+)\s+anchor=(?P<anchor>\S+)\s+regression=(?P<reg>\S+)\s+decision=(?P<dec>\S+)\Z")
# The confirmation token: `operator <ISO-8601, minutes, hyphenated>` (e.g. 2026-07-01T14-30). The
# validator checks the RECORD's shape only — its output must never claim a human confirmed (RT2's
# honesty ceiling; the human layer is rev-a4 at `gate --attest`).
_DISPO_TOKEN_RE = re.compile(
    r"<!--\s*disposition-confirmed:\s*operator\s+\d{4}-\d{2}-\d{2}T\d{2}-\d{2}\s*-->")
_COMPARES_RE = re.compile(r"^compares:\s*(\S+)\s*(?:→|->)\s*(\S+)\s*$", re.MULTILINE)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _safe_component(value, fallback):
    """Reduce an untrusted string to a SINGLE safe filename component (no path traversal, no separators).

    `project` is copied verbatim from the prior manifest (schema permits any string) and `runlabel` is
    derived from a filename, so either could carry path separators, `..`, drive/UNC prefixes, or NUL —
    each of which, interpolated into `os.path.join(out, ...)`, can write outside `out` (or, if absolute,
    discard `out` entirely). Strip every directory part, reject the traversal/special names, and keep only
    a conservative whitelist; fall back to a constant when nothing safe survives. This is the FIRST line of
    defence — `emit` ALSO verifies the resolved parent stays under `out` (defence in depth)."""
    s = "" if value is None else str(value)
    # Drop anything up to the last path separator (handles both / and \, abs paths, drive letters, UNC).
    s = s.replace("\\", "/").rsplit("/", 1)[-1]
    # NUL and control bytes are never valid in a filename.
    s = "".join(ch for ch in s if ch >= " " and ch != "\x7f")
    # Conservative whitelist: alnum, space, dot, dash, underscore. Everything else (incl. ':') -> '_'.
    s = "".join(ch if (ch.isalnum() or ch in " ._-") else "_" for ch in s).strip()
    # Reject pure-dot names (".", "..") and empty -> fallback.
    if not s or set(s) <= {"."}:
        return fallback
    return s


def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def _fid(value):
    """A finding_id normalized to a hashable, sortable form (a str, or None). A malformed non-string id
    (a JSON list/object/number that survives parse_manifest as-is) is str()-coerced, so it cannot crash
    the `fid_class` dict key, the `orig_comment` join key, or the report `sorted()` (unhashable `list`,
    or `'<' not supported between str and int`). This is the finding_id SIBLING of the reclassify-anchor
    crash guard — finding_id is read for keying/sorting/display in several places, not just reclassify."""
    return value if value is None or isinstance(value, str) else str(value)


def reclassify(annotation, n1_snapshot, chap_n, sec_n):
    """-> (klass, new_anchor_or_None, evidence). new_anchor is set only for held/moved (the carried set)."""
    if not isinstance(annotation, dict):
        return "ambiguous", None, "malformed annotation (not an object)"
    anc = annotation.get("anchor")
    anc = anc if isinstance(anc, dict) else {}
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
        # chap_n is a real dict; a non-string value (JSON list/dict survives parse_manifest as-is)
        # is unhashable and would crash `chap_n.get(val, 0)`. The section branch is already safe
        # (it str()-coerces val); this hashing-lookup branch was the one-branch-not-all gap.
        if not isinstance(val, str):
            return "ambiguous", None, "malformed chapter anchor value (not a string): %r" % (val,)
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
        fid = _fid(ra.get("finding_id"))
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
        fid = _fid(an.get("finding_id"))
        buckets[klass].append((fid, evidence))
        fid_class[fid] = klass
        if klass in ("held", "moved"):
            carried.append((an, new_anchor))

    # The re-anchored manifest (held/moved only, bound to N+1), carrying each comment VERBATIM.
    re_anns = [{"finding_id": _fid(an.get("finding_id")), "anchor": new_anchor, "comment": an.get("comment")}
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
    orig_comment = {_fid(an.get("finding_id")): an.get("comment") for an in annotations if isinstance(an, dict)}
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


def _finish(lines, errs, warns, strict, ok_msg, label="reanchor"):
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))
    if errs or (strict and warns):
        lines.append("%s: FAIL (%d error(s)%s)"
                     % (label, len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        if label == "reanchor":
            lines.append("WARN: reanchor: %d re-anchor advisory(ies) — see W1-W2 above" % len(warns))
        else:
            lines.append("WARN: %s: %d advisory(ies) — see the RT4/W1 lines above" % (label, len(warns)))
    else:
        lines.append("%s: PASS (%s)" % (label, ok_msg))
    return 0, lines


def _runlabel_of(snapshot_path):
    base = os.path.basename(snapshot_path)
    if "_Manuscript_Snapshot_" in base:
        return os.path.splitext(base.split("_Manuscript_Snapshot_")[-1])[0] or "run"
    return os.path.splitext(base)[0] or "run"


def _runlabel_of_manifest(man_path):
    """The prior round's runlabel, derived from the RESOLVED manifest path (the actual input the
    disposition recompute runs against) — the manifest-filename sibling of `_runlabel_of` (which
    splits on the snapshot infix). Derived, never hand-typed: the `compares:` header is validated
    against this, so it always names the real inputs, not what the record claims."""
    base = os.path.basename(man_path or "")
    if "_Annotation_Manifest_" in base:
        return os.path.splitext(base.split("_Annotation_Manifest_")[-1])[0] or "run"
    return _runlabel_of(man_path or "")


def _prior_manifest_path(prior):
    """The draft-N manifest path the round-trip resolves: a dir -> its newest manifest; a file ->
    itself. The single resolution rule shared by `_resolve_inputs` and `disposition` (which also
    needs the PATH, for the derived `compares:` prior runlabel)."""
    if os.path.isdir(prior):
        return _newest(glob.glob(os.path.join(prior, am._MANIFEST_GLOB)))
    return prior


def _resolve_inputs(prior, new_snap):
    """Resolve the (draft-N manifest object, normalized N+1 snapshot) pair the round-trip operates on.

    Shared by `run` (the gate), `emit` (the glue write), `crossref` (the join), and `disposition`
    (the round-close record gate), so all four resolve the prior manifest + new snapshot the SAME way:
    a dir -> its newest manifest; a file -> itself.
    Returns `(obj, n1, err)` — on any failure `obj`/`n1` are None and `err` is a (code, [line]) the caller
    returns verbatim."""
    man_path = _prior_manifest_path(prior)
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
    # `project`/`runlabel` are untrusted (copied from the prior manifest / derived from a filename) and
    # are interpolated into the output paths. Sanitize each to a single safe filename component so neither
    # `../escape` (traversal) nor an absolute value (which would make os.path.join discard `out`) can steer
    # a write outside the requested directory.
    project = _safe_component(re_obj.get("project", "Manuscript"), "Manuscript")
    runlabel = _safe_component(re_obj.get("runlabel", "run"), "run")
    man_path = os.path.join(out, "%s_Reanchored_Manifest_%s.md" % (project, runlabel))
    ann_path = os.path.join(out, "%s_Reanchored_Annotated_Manuscript_%s.md" % (project, runlabel))
    # Defence in depth: regardless of sanitization, REFUSE to write unless the resolved parent of EACH
    # output file is `out` itself (realpath-compared, so symlinks and `..` are resolved before the check).
    out_real = os.path.realpath(out)
    for p in (man_path, ann_path):
        if os.path.realpath(os.path.dirname(p)) != out_real:
            return 2, ["reanchor: emit refused — resolved output path escapes the output dir: %s "
                       "(nothing written)" % p]
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


def disposition(paths, strict=False):
    """Gate the Roundtrip Disposition record (`[Project]_Roundtrip_Disposition_[runlabel].md`) in
    <this_run_folder> against the LIVE recompute — the model proposes; the operator disposes; this
    validator proves the record never asserts evidence the recompute doesn't support (RT1), never
    carries a decision without the recorded confirmation token (RT2), that no resolved marker
    was written without a confirmed disposition (RT3 — the no-auto-close rule), and that no
    recomputed prior finding is silently omitted from the record (RT4 — partition coverage; WARN,
    ERROR --strict). Absent record ->
    PASS no-op (the check_state early-return precedent), so it is safe anywhere, including hosts
    where no disposition record can have been produced. Args mirror `crossref`:
    <prior_run_folder> <new_snapshot> <this_run_folder> [--strict]. Returns (code, lines)."""
    if len(paths) < 3:
        return 2, ["reanchor: usage: disposition <prior_run_folder> <new_snapshot> <this_run_folder> "
                   "[--strict]"]
    prior, new_snap, this_run = paths[0], paths[1], paths[2]
    if not os.path.isdir(this_run):
        return 2, ["reanchor: disposition run folder not found: %s" % this_run]
    rec_path = _newest(glob.glob(os.path.join(this_run, _DISPOSITION_GLOB)))
    if rec_path is None:
        return 0, ["disposition: no %s in %s — nothing to check" % (_DISPOSITION_GLOB, this_run),
                   "disposition: PASS (no disposition record — nothing to check)"]
    rec_text = _read(rec_path)
    if rec_text is None:
        return 2, ["reanchor: cannot read disposition record %s" % rec_path]
    if ft is None:
        return 2, ["reanchor: finding_trace is unavailable (same-dir import failed) — RT3 cannot "
                   "verify the resolved markers; refusing to gate %s" % os.path.basename(rec_path)]
    obj, n1, err = _resolve_inputs(prior, new_snap)
    if err is not None:
        return err
    _re_obj, _buckets, _carried, fid_class = build_reanchored(obj, n1, new_snap)
    # Best-effort like `crossref` ({} when a ledger is missing): a recorded non-`none` class with no
    # recomputed join then FAILS RT1 — the record is never taken at its word.
    reg_class = rd.crossref_classes(prior, this_run) if rd is not None else {}

    lines, errs, warns = [], [], []
    lines.append("disposition: %s — %d prior annotation class(es) recomputed"
                 % (os.path.basename(rec_path), len(fid_class)))

    # RT1 — the `compares:` header must name the ACTUAL inputs (both runlabels derived live).
    prior_label = _runlabel_of_manifest(_prior_manifest_path(prior))
    this_label = _runlabel_of(new_snap)
    cm = _COMPARES_RE.search(rec_text)
    if cm is None:
        errs.append("RT1 recompute alignment: no `compares: <prior> → <this>` header in the record")
    elif (cm.group(1), cm.group(2)) != (prior_label, this_label):
        errs.append("RT1 recompute alignment: `compares:` header names %s → %s but the actual inputs "
                    "are %s → %s" % (cm.group(1), cm.group(2), prior_label, this_label))

    # Parse the disposition rows (the machine record; the human table is presentation only).
    rows, seen = [], set()
    for raw in _DISPO_ANY_RE.findall(rec_text):
        rm = _DISPO_ROW_RE.match(raw.strip())
        if (rm is None or rm.group("anchor") not in _CLASSES
                or rm.group("reg") not in _DISPO_REGRESSION
                or rm.group("dec") not in _DISPO_DECISIONS):
            errs.append("RT1 recompute alignment: malformed disposition row `%s`"
                        % " ".join(raw.split()))
            continue
        fid = rm.group("fid")
        if fid in seen:
            errs.append("RT1 recompute alignment: duplicate disposition row for %s" % fid)
            continue
        seen.add(fid)
        rows.append((fid, rm.group("anchor"), rm.group("reg"), rm.group("dec")))

    # RT1 — recompute alignment, row by row (never trust the record's classes).
    for fid, anc, reg, dec in rows:
        lines.append("  disposition:%s %s anchor=%s regression=%s" % (dec, fid, anc, reg))
        if fid not in fid_class:
            errs.append("RT1 recompute alignment: %s is not in the prior manifest's RA3 partition" % fid)
            continue
        if anc != fid_class[fid]:
            errs.append("RT1 recompute alignment: %s records anchor=%s but the recompute classifies it "
                        "%s" % (fid, anc, fid_class[fid]))
        if reg != "none":
            actual = reg_class.get(fid)
            if reg != actual:
                errs.append("RT1 recompute alignment: %s records regression=%s but the recomputed "
                            "crossref class is %s" % (fid, reg, actual if actual else "none (no join)"))

    # RT2 — confirmation record present: no decision stands on the record without the token. The
    # validator proves the RECORD of confirmation is present and consistent — never that a human
    # confirmed (that layer is the state-lifecycle sequencing rule + rev-a4 at `gate --attest`).
    token = _DISPO_TOKEN_RE.search(rec_text) is not None
    decided = [fid for fid, _a, _r, dec in rows if dec != "pending"]
    if decided and not token:
        errs.append("RT2 confirmation record: %d decided row(s) but no `<!-- disposition-confirmed: "
                    "operator <ISO-8601> -->` token — the record of confirmation is absent"
                    % len(decided))

    # RT3 — confirmed-writes-only: a resolved marker in this folder's Revision Report(s) whose id the
    # prior manifest annotates (the RA3 partition — the ids a disposition row CAN govern; RT1 bars
    # rows for anything else) must have a confirm-resolved row. Marker parse: finding_trace.
    # resolved_cited_ids — the SSoT (never a local reimplementation). Markers for un-annotated ledger
    # findings carry no anchor evidence either way and stay governed by rev-a2 / finding-trace.
    confirm_ok = {fid for fid, _a, _r, dec in rows if dec == "confirm-resolved"}
    resolved_ids = set()
    for rp in sorted(glob.glob(os.path.join(this_run, _REVISION_REPORT_GLOB))):
        resolved_ids |= ft.resolved_cited_ids(_read(rp) or "")
    for rid in sorted(resolved_ids):
        if rid in fid_class and rid not in confirm_ok:
            errs.append("RT3 confirmed-writes-only: `<!-- resolved: %s -->` in a Revision Report has no "
                        "decision=confirm-resolved disposition row — an unconfirmed close is the "
                        "auto-close this gate exists to prevent" % rid)

    # RT4 — partition coverage: every finding id the recompute puts in the RA3 partition must have a
    # disposition row. A record that EXISTS is a round-close record (carry-only exit (a) writes no
    # record at all), so a missing row is a finding silently dropped from round-close review — it must
    # never read as adjudicated. Reported by id; WARN by default (a record may be drafted incrementally
    # within a session, the W1 staging posture), ERROR under --strict (round close). The falsy-key
    # filter mirrors crossref's: an annotation _fid could not normalize (None) has no id a row could
    # name — it is outside the record's governable domain and gated upstream by the A-gate/RA3.
    for fid in sorted(k for k in fid_class if k and k not in seen):
        warns.append("RT4 partition coverage: %s is in the recomputed RA3 partition but has no "
                     "disposition row — adjudicate it (or record it decision=pending) before "
                     "round close" % fid)

    # W1 — unadjudicated / staged (advisory; work stages across sessions — `--strict` gates round close).
    for fid, _a, _r, dec in rows:
        if dec == "pending":
            warns.append("W1 unadjudicated: %s is still pending — adjudicate before round close" % fid)
    for fid in sorted(confirm_ok - resolved_ids):
        warns.append("W1 staged: %s is confirm-resolved but not yet reflected as a `<!-- resolved: %s "
                     "-->` marker in a Revision Report" % (fid, fid))

    ok_msg = ("%d disposition row(s) aligned; record of confirmation %s"
              % (len(rows), "present and consistent" if token else "not required (no decided rows)"))
    return _finish(lines, errs, warns, strict, ok_msg, label="disposition")


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

        # CONTAINMENT (Codex P1): `project`/`runlabel` are untrusted, so a hostile manifest must NEVER
        # steer emit's writes outside the requested `out`. Two attack vectors, each verified against an
        # isolated parent + a canary sibling dir that MUST stay empty:
        #   (a) traversal  project="../escape"  -> would write into out's parent (os.path.join keeps `out`).
        #   (b) absolute   project="<canary>/x" -> os.path.join DISCARDS `out`, writing under the canary.
        # Pre-fix this block FAILS (a stray *_Reanchored_*.md lands in the parent / the canary). The held-
        # quote prior below re-anchors clean (RA1-RA3 pass), so any escape is a path-construction escape,
        # not an RA refusal masking it.
        def _attack_prior(project_value):
            asnap = am.normalize_snapshot("# Chapter 1\nThe unique sentence here.\n")
            aq = "The unique sentence here."
            aqs = asnap.find(aq)
            return asnap, {"schema": am._SCHEMA_ID, "project": project_value, "runlabel": "rN",
                           "snapshot_path": "T_Manuscript_Snapshot_rN.md",
                           "snapshot_sha256": am.sha256(asnap),
                           "snapshot_line_count": am.line_count(asnap),
                           "annotations": [{"finding_id": "F-Q-01",
                                            "anchor": {"kind": "quote",
                                                       "value": "%d-%d" % (aqs, aqs + len(aq)), "quote": aq},
                                            "comment": "a benign carried comment"}]}

        def _no_escape(project_value, label):
            # Isolated parent: out is a SUBDIR, and there is a canary sibling. After emit, neither the
            # parent (minus out) nor the canary may contain any emitted artifact.
            root = tempfile.mkdtemp()
            try:
                esc_out = os.path.join(root, "out")
                canary = os.path.join(root, "canary")
                os.makedirs(esc_out)
                os.makedirs(canary)
                # For the absolute vector, aim the absolute prefix straight at the canary dir.
                pv = project_value.replace("__CANARY__", canary) if "__CANARY__" in project_value \
                    else project_value
                asnap, aman = _attack_prior(pv)
                ad = os.path.join(root, "prior")
                os.makedirs(ad)
                with open(os.path.join(ad, "T_Annotation_Manifest_rN.md"), "w",
                          encoding="utf-8", newline="") as fh:
                    fh.write(_manifest_text(aman))
                asp = os.path.join(ad, "T_Manuscript_Snapshot_rN1.md")
                with open(asp, "w", encoding="utf-8", newline="") as fh:
                    fh.write(asnap)
                emit([ad, asp], out_dir=esc_out)
                stray = []
                for base in (root, canary):
                    for name in os.listdir(base):
                        full = os.path.join(base, name)
                        # the only legitimate entries under root are the out/canary/prior dirs themselves.
                        if base == root and full in (esc_out, canary, ad):
                            continue
                        stray.append(full)
                chk("emit_contains_%s" % label, not stray)
            finally:
                shutil.rmtree(root, ignore_errors=True)

        _no_escape("../escape", "traversal_project")
        _no_escape("__CANARY__/pwned", "absolute_project")
        # runlabel is the sibling vector — guard it too (single component, no separators survive).
        chk("safe_component_traversal", _safe_component("../escape", "fb") == "escape")
        chk("safe_component_absolute", "/" not in _safe_component("/etc/passwd", "fb")
            and "\\" not in _safe_component("\\\\srv\\share\\x", "fb"))
        chk("safe_component_dotdot_fallback", _safe_component("..", "fb") == "fb"
            and _safe_component(".", "fb") == "fb" and _safe_component("", "fb") == "fb")
        chk("safe_component_nul_stripped", "\x00" not in _safe_component("a\x00b", "fb"))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # regression: a non-dict anchor / annotation must not crash reclassify (2026-06-20 sweep) — the
    # fix is no-crash; a non-dict anchor yields an empty-anchor classification, a non-dict annotation -> ambiguous
    chk("crash_nondict_anchor", isinstance(reclassify({"finding_id": "F-X-01", "anchor": [1, 2]}, "snap", 1, 1), tuple))
    chk("crash_nondict_annotation", reclassify([1, 2, 3], "snap", 1, 1)[0] == "ambiguous")
    # regression: a non-hashable chapter anchor value (a JSON list/dict, kept as-is by parse_manifest)
    # must not crash the chapter branch's `chap_n.get(val, 0)` lookup. chap_n MUST be a real dict here
    # (the prior non-dict-anchor test passed ints, which never reaches this hashing site). Pre-fix this
    # raised TypeError: unhashable type. The section branch already str()-coerces; this was the gap.
    _chap_n, _sec_n, _c, _s = am.heading_index(snap_n)
    for _bad in ([1, 2], {"k": "v"}):
        kl, _na, _ev = reclassify({"finding_id": "F-CH-X", "anchor": {"kind": "chapter", "value": _bad}},
                                  snap_n, _chap_n, _sec_n)
        chk("crash_nonstring_chapter_value_%s" % type(_bad).__name__, kl == "ambiguous")
    # end-to-end through reanchor(): a manifest whose chapter anchor value is a list must classify
    # (not traceback) — the validator-entry path parse_manifest -> reanchor -> reclassify.
    _man_bad = dict(man_n, annotations=[ann("F-CH-99", {"kind": "chapter", "value": [1, 2]})])
    try:
        _cb, _lb = run_via(_man_bad, snap_moved)
        chk("reanchor_nonstring_chapter_value_no_crash",
            any("reanchor:ambiguous F-CH-99" in x for x in _lb))
    except TypeError:
        chk("reanchor_nonstring_chapter_value_no_crash", False)
    # regression — the finding_id SIBLING of the reclassify-anchor guard: finding_id is read as a dict
    # KEY (fid_class / orig_comment) and a SORT key (the report), not just inside reclassify. A
    # non-hashable id (JSON list/object) crashed `fid_class[fid]` (unhashable type), and a mixed int/str
    # id set crashed the report `sorted()` (`'<' not supported between str and int`). _fid() normalizes.
    _secref = {"kind": "section", "value": "Beta"}
    for _bad, _lbl in (([1, 2], "list"), ({"k": "v"}, "dict")):
        _mb = dict(man_n, annotations=[{"finding_id": _bad, "anchor": _secref, "comment": "c"}])
        try:
            chk("reanchor_nonhashable_finding_id_no_crash_%s" % _lbl, isinstance(run_via(_mb, snap_moved)[1], list))
        except TypeError:
            chk("reanchor_nonhashable_finding_id_no_crash_%s" % _lbl, False)
    _mm = dict(man_n, annotations=[{"finding_id": 7, "anchor": _secref, "comment": "c"},
                                   {"finding_id": "F-S-01", "anchor": _secref, "comment": "c"}])
    try:
        chk("reanchor_mixed_type_finding_id_no_crash", isinstance(run_via(_mm, snap_moved)[1], list))
    except TypeError:
        chk("reanchor_mixed_type_finding_id_no_crash", False)

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

    # disposition: the round-close record gate (RT1-RT4 + W1) — needs the crossref join (rd) and the
    # finding_trace marker SSoT (ft), both same-dir siblings.
    if rd is not None and ft is not None:
        dd = tempfile.mkdtemp()
        try:
            _disposition_self_test(chk, dd)
        finally:
            shutil.rmtree(dd, ignore_errors=True)

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


def _disposition_self_test(chk, dd):
    """disposition (RT1-RT4 + W1): the round-close record gate against a live recompute. The staged
    rounds mirror _crossref_self_test's: F-HOLD-01 (quote persists -> held; recurs -> recurrence-
    candidate) and F-GONE-01 (quote cut -> vanished; resolved, no match -> resolved-and-held)."""
    import json as _j

    prior_snap = am.normalize_snapshot("# Chapter 7\nThe want never forces a sacrifice here.\n"
                                       "A sentence slated for the cut sits in chapter nine.\n# Chapter 9\nx\n")
    q_hold = "The want never forces a sacrifice here."
    q_gone = "A sentence slated for the cut sits in chapter nine."
    hs, gs = prior_snap.find(q_hold), prior_snap.find(q_gone)
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

    def w(path, text):
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)

    pri = os.path.join(dd, "r1")
    os.makedirs(pri)
    w(os.path.join(pri, "X_Annotation_Manifest_r1.md"), _manifest_text(prior_man))
    w(os.path.join(pri, "X_Findings_Ledger_r1.md"),
      "# Ledger\n"
      + finding("F-HOLD-01", "the want never forces a sacrifice so stakes stay abstract", ["Ch 7"]) + "\n"
      + finding("F-GONE-01", "a sentence slated for the cut creates a continuity seam", ["Ch 9"]) + "\n")
    # round 1 claimed both resolved -> the recompute yields recurrence-candidate (F-HOLD recurs) and
    # resolved-and-held (F-GONE, no match).
    w(os.path.join(pri, "X_Revision_Report_r1.md"),
      "# Revision Report\n<!-- resolved: F-HOLD-01 -->\n<!-- resolved: F-GONE-01 -->\n")
    new_snap = os.path.join(dd, "X_Manuscript_Snapshot_r2.md")
    w(new_snap, am.normalize_snapshot("# Chapter 7\nThe want never forces a sacrifice here.\n# Chapter 9\nx\n"))

    aligned_record = ("# Roundtrip Disposition — X r2\ncompares: r1 → r2\n\n"
                      "| finding | anchor class | regression class | proposed | decision |\n"
                      "|---|---|---|---|---|\n"
                      "| F-GONE-01 | vanished | resolved-and-held | confirm-resolved | confirm-resolved |\n"
                      "| F-HOLD-01 | held | recurrence-candidate | keep-open | keep-open |\n\n"
                      "<!-- disposition: F-GONE-01 anchor=vanished regression=resolved-and-held "
                      "decision=confirm-resolved -->\n"
                      "<!-- disposition: F-HOLD-01 anchor=held regression=recurrence-candidate "
                      "decision=keep-open -->\n")
    token = "<!-- disposition-confirmed: operator 2026-07-01T14-30 -->\n"
    report = "# Revision Report\n- Flags resolved: F-GONE-01\n<!-- resolved: F-GONE-01 -->\n"

    seq = {"n": 0}

    def cur_folder(record, rep=report, ledger=True):
        seq["n"] += 1
        cur = os.path.join(dd, "r2-%d" % seq["n"])
        os.makedirs(cur)
        if ledger:
            w(os.path.join(cur, "X_Findings_Ledger_r2.md"),
              "# Ledger\n" + finding("F-HOLD-01", "the want still never forces a sacrifice; "
                                     "stakes remain abstract", ["Ch 7"]) + "\n")
        if record is not None:
            w(os.path.join(cur, "X_Roundtrip_Disposition_r2.md"), record)
        if rep is not None:
            w(os.path.join(cur, "X_Revision_Report_r2.md"), rep)
        return cur

    # absent record -> PASS no-op (safe anywhere).
    code, lines = disposition([pri, new_snap, cur_folder(None, rep=None)])
    chk("dispo_absent_record_noop", code == 0 and any("nothing to check" in x for x in lines))

    # aligned record + token + confirmed-only marker -> PASS, no warns; wording stays inside the
    # honesty ceiling (never "operator confirmed").
    code, lines = disposition([pri, new_snap, cur_folder(aligned_record + token)])
    txt = "\n".join(lines)
    chk("dispo_aligned_pass", code == 0 and "disposition:confirm-resolved F-GONE-01" in txt
        and "disposition:keep-open F-HOLD-01" in txt and "PASS" in txt)
    chk("dispo_no_warns_when_clean", "W1" not in txt)
    chk("dispo_honesty_wording", "record of confirmation present and consistent" in txt
        and "operator confirmed" not in txt)
    chk("dispo_deterministic", disposition([pri, new_snap, cur_folder(aligned_record + token)])[1][1:]
        == lines[1:])   # line 0 names the (per-case) record folder's basename-invariant record name

    # RT1 wrong class: the record claims F-GONE-01 held (it vanished) -> FAIL.
    bad = aligned_record.replace("F-GONE-01 anchor=vanished", "F-GONE-01 anchor=held") + token
    code, lines = disposition([pri, new_snap, cur_folder(bad)])
    chk("dispo_rt1_wrong_anchor_class", code == 1 and any("RT1" in x and "anchor=held" in x for x in lines))

    # RT1 wrong regression class (stale/fabricated evidence) -> FAIL.
    bad = aligned_record.replace("regression=recurrence-candidate decision=keep-open",
                                 "regression=resolved-and-held decision=keep-open") + token
    code, lines = disposition([pri, new_snap, cur_folder(bad)])
    chk("dispo_rt1_wrong_regression_class", code == 1 and any("RT1" in x for x in lines))

    # RT1 unknown id: a row for a finding the RA3 partition never had -> FAIL.
    bad = aligned_record + "<!-- disposition: F-NOPE-01 anchor=held regression=none decision=keep-open -->\n" + token
    code, lines = disposition([pri, new_snap, cur_folder(bad)])
    chk("dispo_rt1_unknown_id", code == 1 and any("RT1" in x and "F-NOPE-01" in x for x in lines))

    # RT1 compares-header drift: names a prior round that is not the actual input -> FAIL.
    bad = (aligned_record + token).replace("compares: r1 → r2", "compares: r0 → r2")
    code, lines = disposition([pri, new_snap, cur_folder(bad)])
    chk("dispo_rt1_compares_header", code == 1 and any("RT1" in x and "compares" in x for x in lines))
    bad = (aligned_record + token).replace("compares: r1 → r2\n", "")
    chk("dispo_rt1_compares_missing",
        disposition([pri, new_snap, cur_folder(bad)])[0] == 1)

    # RT1 malformed row / duplicate row -> FAIL (the record grammar is closed).
    bad = aligned_record + "<!-- disposition: F-HOLD-01 anchor=held regression=none decision=maybe -->\n" + token
    code, lines = disposition([pri, new_snap, cur_folder(bad)])
    chk("dispo_rt1_malformed_decision", code == 1 and any("malformed" in x for x in lines))
    bad = (aligned_record
           + "<!-- disposition: F-HOLD-01 anchor=held regression=recurrence-candidate decision=declined -->\n"
           + token)
    code, lines = disposition([pri, new_snap, cur_folder(bad)])
    chk("dispo_rt1_duplicate_row", code == 1 and any("duplicate" in x for x in lines))

    # RT2 decided rows without the confirmation token -> FAIL (no decision stands on the record alone).
    code, lines = disposition([pri, new_snap, cur_folder(aligned_record)])
    chk("dispo_rt2_no_token", code == 1 and any("RT2" in x for x in lines))

    # RT3 resolved marker without a confirm-resolved row (the auto-close) -> FAIL.
    rep = report + "<!-- resolved: F-HOLD-01 -->\n"
    code, lines = disposition([pri, new_snap, cur_folder(aligned_record + token, rep=rep)])
    chk("dispo_rt3_unconfirmed_marker", code == 1 and any("RT3" in x and "F-HOLD-01" in x for x in lines))

    # W1 pending rows: advisory by default, ERROR under --strict.
    pend = aligned_record.replace(
        "regression=recurrence-candidate decision=keep-open",
        "regression=recurrence-candidate decision=pending") + token
    code, lines = disposition([pri, new_snap, cur_folder(pend)])
    chk("dispo_w1_pending_warn", code == 0 and any("W1 unadjudicated" in x for x in lines))
    chk("dispo_w1_pending_strict_fails",
        disposition([pri, new_snap, cur_folder(pend)], strict=True)[0] == 1)

    # W1 staged: confirm-resolved not yet reflected as a resolved marker (no report at all).
    code, lines = disposition([pri, new_snap, cur_folder(aligned_record + token, rep=None)])
    chk("dispo_w1_staged_warn", code == 0 and any("W1 staged" in x and "F-GONE-01" in x for x in lines))

    # RT4 omitted row: the record simply DROPS F-HOLD-01 (no row at all) -> WARN by default naming
    # the missing id, ERROR under --strict — a partial record must never read as round-close clean
    # (the silently-omitted-finding hole; a record that exists is a round-close record, so coverage
    # of the recomputed RA3 partition is expected — carry-only exit (a) writes no record at all).
    omit = ("# Roundtrip Disposition — X r2\ncompares: r1 → r2\n\n"
            "<!-- disposition: F-GONE-01 anchor=vanished regression=resolved-and-held "
            "decision=confirm-resolved -->\n" + token)
    code, lines = disposition([pri, new_snap, cur_folder(omit)])
    chk("dispo_rt4_omitted_row_warn", code == 0
        and any("RT4" in x and "F-HOLD-01" in x for x in lines))
    chk("dispo_rt4_omitted_row_strict_fails",
        disposition([pri, new_snap, cur_folder(omit)], strict=True)[0] == 1)

    # carry-only round: no ledger in this_run (no crossref join yet) -> regression=none rows align.
    carry = ("# Roundtrip Disposition — X r2\ncompares: r1 → r2\n\n"
             "<!-- disposition: F-GONE-01 anchor=vanished regression=none decision=needs-placement -->\n"
             "<!-- disposition: F-HOLD-01 anchor=held regression=none decision=pending -->\n" + token)
    code, lines = disposition([pri, new_snap, cur_folder(carry, rep=None, ledger=False)])
    chk("dispo_carry_only_none_rows", code == 0 and any("W1 unadjudicated: F-HOLD-01" in x for x in lines))

    # usage: two args -> 2.
    chk("dispo_usage_two_args", disposition([pri, new_snap])[0] == 2)
    chk("dispo_missing_folder", disposition([pri, new_snap, os.path.join(dd, "nope")])[0] == 2)


def run_via(manifest_obj, n1_snapshot, strict=False):
    return reanchor(manifest_obj, n1_snapshot, "X_Manuscript_Snapshot_rN1.md", strict=strict)


_USAGE = ("Usage: reanchor.py reanchor    <prior_run_folder> <new_snapshot> [--strict]\n"
          "       reanchor.py emit        <prior_run_folder> <new_snapshot> [-o <out_dir>]\n"
          "       reanchor.py crossref    <prior_run_folder> <new_snapshot> <this_run_folder> [--strict]\n"
          "       reanchor.py disposition <prior_run_folder> <new_snapshot> <this_run_folder> [--strict]\n"
          "       reanchor.py --self-test")


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    if am is None:
        print("reanchor: annotation_manifest is unavailable (same-dir import failed)")
        return 2
    sub = argv[1] if len(argv) > 1 else None
    rest = argv[2:] if sub in ("reanchor", "emit", "crossref", "disposition") else argv[1:]
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
    elif sub == "disposition":
        code, lines = disposition(paths, strict=strict)
    else:   # default + explicit `reanchor`
        code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
