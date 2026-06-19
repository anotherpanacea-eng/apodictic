#!/usr/bin/env python3
"""feedback-triage — structural integrity for the Feedback Triage workflow (Workflows track).

`validate.sh feedback-triage <run_folder> [--strict]` (or explicit files) shells out here.
A writer returning with beta-reader / critique-group / editor feedback records each item as a
structured `apodictic.feedback_item.v1` block in a Feedback Triage artifact: the external claim,
APODICTIC's own `assessment` of it (did our analysis confirm it?), the `triage` disposition, the
items it `conflicts_with`, and the chosen `disposition`. This validator owns the workflow's
machine-checkable invariants — contract hygiene + conflict referential integrity + the
"contradiction kept live on both sides" coherence gap that prose triage can hide.

  E1 invalid item     a feedback_item block fails its schema (bad enum / id / missing field / JSON).
  E2 duplicate id     two items share an FB-NN id (ids must be unique per triage).
  E3 dangling conflict an id in conflicts_with does not resolve to a real item in the artifact.
  E4 self conflict    an item lists its own id in conflicts_with.
  W1 unresolved conflict  two items conflict but BOTH stay actionable (act-now/act-later) — the
                          contradiction was never resolved (advisory; ERROR under --strict).
  W2 act-on-unvalidated   an item triaged act-now whose claim is not (partly-)validated — acting
                          now on an unconfirmed external claim (advisory; ERROR under --strict).

Conflicts are treated as an UNDIRECTED graph: A.conflicts_with B pairs {A,B} even if B omits A.
Each artifact is optional; an empty/absent one is a no-op (no false failure). Reuses
apodictic_artifacts (one block grammar + the schema engine). See docs/feedback-triage.md.

  feedback_triage.py feedback-triage <run_folder|files...> [--strict]
  feedback_triage.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import os
import sys

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

_SCHEMA_ID = "apodictic.feedback_item.v1"
_ACTIONABLE = ("act-now", "act-later")
_VALIDATED = ("validated", "partly-validated")
_TRIAGE_GLOB = "*_Feedback_Triage_*.md"


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def parse_items(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:feedback_item block.

    Each entry's schema_errs is a list (JSON/schema failures); obj is the parsed dict (or None
    when the JSON itself is broken). Index is 1-based block position for messages."""
    items = []
    if not text or art is None:
        return items
    schema = art.load_schema(_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "feedback_item":
            continue
        idx += 1
        where = "feedback_item #%d" % idx
        if jerr:
            items.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        errs = art.validate_obj(obj, schema, where)
        items.append((obj, errs, idx))
    return items


def triage(text, strict=False):
    """Run the Feedback Triage integrity checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    items = parse_items(text)
    if not items:
        return 0, ["feedback-triage: no feedback_item blocks found — nothing to triage"]

    # E1 — schema/JSON validity (per block)
    for _obj, schema_errs, _idx in items:
        for e in schema_errs:
            errs.append("E1 invalid item: %s" % e)

    # Index well-formed items by id (only items that passed schema have a trustworthy id)
    by_id = {}
    valid = [(obj, idx) for obj, schema_errs, idx in items if obj is not None and not schema_errs]
    # E2 — duplicate id
    seen = {}
    for obj, idx in valid:
        fid = obj.get("id")
        seen.setdefault(fid, []).append(idx)
    for fid, where in sorted(seen.items()):
        if len(where) > 1:
            errs.append("E2 duplicate id: %s appears %d times (ids must be unique per triage)"
                        % (fid, len(where)))
        by_id[fid] = next(o for o, _ in valid if o.get("id") == fid)

    known = set(by_id)
    # E3 dangling conflict / E4 self conflict + build the undirected conflict graph
    conflicts = set()  # frozenset({a, b})
    for fid, obj in sorted(by_id.items()):
        for other in obj.get("conflicts_with") or []:
            if other == fid:
                errs.append("E4 self conflict: %s lists itself in conflicts_with" % fid)
                continue
            if other not in known:
                errs.append("E3 dangling conflict: %s.conflicts_with cites %s — no such item" % (fid, other))
                continue
            conflicts.add(frozenset((fid, other)))

    # W1 — unresolved conflict: both sides still actionable
    for pair in sorted(conflicts, key=lambda p: sorted(p)):
        a, b = sorted(pair)
        if by_id[a].get("triage") in _ACTIONABLE and by_id[b].get("triage") in _ACTIONABLE:
            warns.append("W1 unresolved conflict: %s and %s contradict but both stay actionable "
                         "(%s / %s) — resolve one before revising"
                         % (a, b, by_id[a].get("triage"), by_id[b].get("triage")))
    # W2 — acting now on an unvalidated claim
    for fid, obj in sorted(by_id.items()):
        if obj.get("triage") == "act-now" and obj.get("assessment") not in _VALIDATED:
            warns.append("W2 act-on-unvalidated: %s is act-now but assessment=%r (not validated)"
                         % (fid, obj.get("assessment")))

    # Report
    lines.append("feedback-triage: %d item(s)%s" % (len(items),
                 "" if len(valid) == len(items) else " (%d well-formed)" % len(valid)))
    for obj, idx in valid:
        cw = ",".join(obj.get("conflicts_with") or []) or "—"
        lines.append("  %-7s src=%-16s assess=%-15s triage=%-9s conflicts=%s"
                     % (obj.get("id"), (obj.get("source") or "?")[:16],
                        obj.get("assessment"), obj.get("triage"), cw))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("feedback-triage: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: feedback-triage: %d advisory coherence gap(s) — see W1/W2 above" % len(warns))
    else:
        lines.append("feedback-triage: PASS (contract + conflict integrity)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    """Return the triage artifact path from a run folder or explicit files."""
    if len(paths) == 1 and os.path.isdir(paths[0]):
        return _newest(glob.glob(os.path.join(paths[0], _TRIAGE_GLOB)))
    for p in paths:
        if "apodictic:feedback_item" in (_read(p) or ""):
            return p
    # fall back to the first file arg if none carried a block (so a clean empty file reports no-op)
    return paths[0] if paths else None


def run(paths, strict=False):
    path = resolve(paths)
    if not path:
        return 2, ["feedback-triage: no Feedback Triage artifact found (need a *_Feedback_Triage_*.md "
                   "or a file with apodictic:feedback_item blocks)"]
    text = _read(path)
    if text is None:
        return 2, ["feedback-triage: cannot read %s" % path]
    return triage(text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import tempfile
    import shutil
    rc = {"v": 0}
    made = []

    def check(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def item(fid, assessment="validated", triage_="act-now", conflicts=None, source="Beta reader",
             claim="c", disp="d"):
        obj = {"schema": _SCHEMA_ID, "id": fid, "source": source, "claim": claim,
               "assessment": assessment, "triage": triage_, "disposition": disp}
        if conflicts is not None:
            obj["conflicts_with"] = conflicts
        import json as _j
        return "<!-- apodictic:feedback_item\n%s\n-->" % _j.dumps(obj)

    # clean single item
    code, _ = triage(item("FB-01"))
    check("clean_single", code == 0)

    # bad enums / id / missing field -> E1
    check("bad_assessment", triage(item("FB-01").replace("validated", "true"))[0] == 1)
    check("bad_triage", triage(item("FB-01", triage_="act-now").replace('"act-now"', '"asap"'))[0] == 1)
    check("bad_id_format", triage(item("FB-1"))[0] == 1)
    check("missing_field", triage(item("FB-01").replace('"disposition": "d"', '"disposition2": "d"'))[0] == 1)
    # malformed JSON block (no closing brace before -->) -> E1 invalid item
    code, lines = triage('<!-- apodictic:feedback_item\n{"schema":"apodictic.feedback_item.v1"\n-->')
    check("bad_json", code == 1 and any("E1 invalid item" in ln for ln in lines))

    # E2 duplicate id
    code, lines = triage(item("FB-01") + "\n" + item("FB-01", claim="other"))
    check("e2_duplicate_id", code == 1 and any("E2 duplicate" in ln for ln in lines))

    # E3 dangling conflict
    code, lines = triage(item("FB-01", conflicts=["FB-99"]))
    check("e3_dangling_conflict", code == 1 and any("E3 dangling" in ln and "FB-99" in ln for ln in lines))

    # E4 self conflict
    code, lines = triage(item("FB-01", conflicts=["FB-01"]))
    check("e4_self_conflict", code == 1 and any("E4 self conflict" in ln for ln in lines))

    # W1 unresolved conflict (both actionable) — advisory, ERROR --strict
    two_live = item("FB-01", triage_="act-now", conflicts=["FB-02"]) + "\n" + item("FB-02", triage_="act-later")
    code_w, lines_w = triage(two_live)
    check("w1_unresolved_advisory",
          code_w == 0 and any("W1 unresolved conflict" in ln for ln in lines_w))
    check("w1_unresolved_strict_fails", triage(two_live, strict=True)[0] == 1)

    # one-directional declaration still detected (FB-02 omits the back-reference)
    code_w, lines_w = triage(item("FB-01", conflicts=["FB-02"]) + "\n" + item("FB-02"))
    check("w1_undirected", code_w == 0 and any("W1 unresolved conflict" in ln for ln in lines_w))

    # resolved conflict: one side declined -> clean
    resolved = item("FB-01", triage_="act-now", conflicts=["FB-02"]) + "\n" + \
        item("FB-02", assessment="refuted", triage_="decline")
    check("conflict_resolved_clean", triage(resolved)[0] == 0)

    # W2 act-on-unvalidated — advisory, ERROR --strict
    code_w, lines_w = triage(item("FB-01", assessment="pending", triage_="act-now"))
    check("w2_act_unvalidated_advisory",
          code_w == 0 and any("W2 act-on-unvalidated" in ln for ln in lines_w))
    check("w2_act_unvalidated_strict_fails",
          triage(item("FB-01", assessment="pending", triage_="act-now"), strict=True)[0] == 1)

    # monitor on a pending item is fine (no W2)
    check("pending_monitor_clean", triage(item("FB-01", assessment="pending", triage_="monitor"))[0] == 0)

    # no blocks -> no-op
    check("no_items_noop", triage("# Feedback\nNo structured items yet.\n")[0] == 0)

    # file + run-folder resolution
    d = tempfile.mkdtemp()
    made.append(d)
    with open(os.path.join(d, "Proj_Feedback_Triage_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Feedback Triage\n" + resolved + "\n")
    check("run_folder_resolution", run([d])[0] == 0)
    check("explicit_file_resolution", run([os.path.join(d, "Proj_Feedback_Triage_run.md")])[0] == 0)
    check("missing_artifact_usage", run([d + "/nope.md"])[0] in (2,))

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "feedback-triage"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: feedback_triage.py feedback-triage <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
