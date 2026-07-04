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
  W3 unreconciled decline an item triaged `decline` whose evidence_refs cite a ledger F-… id, with
                          no disposition marker for that id in this artifact — the decline lives
                          only here, invisible to the engine (docs/finding-dispositions.md;
                          advisory; ERROR under --strict).
  E5 dangling maps_to  an item's `maps_to` finding-id (Increment 2) does not resolve to a real
                          apodictic.finding.v1 in the supplied Findings Ledger — a phantom / typo'd
                          finding reference. Cross-artifact referential integrity, mirroring
                          finding-trace E1. Requires the ledger (2nd file); skipped without it.
  W4 unmapped validated   a `validated` item that carries no `maps_to` — the spec's "a validated
                          feedback item must point at a real F-…", made checkable. Advisory (ERROR
                          under --strict) so an item validated ahead of its ledger entry, and every
                          pre-Increment-2 artifact, stays valid; --strict is the finalize/CI gate.
                          Also requires the ledger (only engaged in the two-file cross-check mode).

Conflicts are treated as an UNDIRECTED graph: A.conflicts_with B pairs {A,B} even if B omits A.
The Findings Ledger is an OPTIONAL second file (a run folder globs *_Findings_Ledger_*.md; explicit
args classify by block type) — like finding-trace / ledger-consolidation. When absent (or carrying
no finding blocks), the maps_to cross-check (E5/W4) is skipped and only the self-contained schema +
conflict checks run. Each artifact is optional; an empty/absent one is a no-op (no false failure).
Reuses apodictic_artifacts (one block grammar + the schema engine). See docs/feedback-triage.md.

  feedback_triage.py feedback-triage <run_folder|files...> [--strict]
  feedback_triage.py feedback-triage <triage.md> [<ledger.md>] [--strict]
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


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (a parsed carrier, not a prose mention).

    Classifying on parsed blocks — not a raw substring — keeps a file that merely *names* the marker
    in prose from being misrouted/skipped (the 2026-06-20 resolver-hardening sweep). Gated by
    validate.sh validator-conventions (M2)."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))

_SCHEMA_ID = "apodictic.feedback_item.v1"
_ACTIONABLE = ("act-now", "act-later")
_VALIDATED = ("validated", "partly-validated")
# W4 targets the spec's exact term — "a *validated* feedback item must point at a real F-…" — so it
# keys on assessment == "validated" only, NOT the broader (partly-validated) actionable set above.
_MAPS_REQUIRED = "validated"
_TRIAGE_GLOB = "*_Feedback_Triage_*.md"
_LEDGER_GLOB = "*_Findings_Ledger_*.md"


def ledger_ids(ledger_text):
    """The authoritative set of Finding Lifecycle IDs in a Findings Ledger — {fid_key(id)} over its
    apodictic.finding.v1 blocks. Mirrors finding_trace.ledger_inventory (keyed the same way, via
    art.fid_key so a malformed non-hashable finding id can't crash the index). Empty when no ledger
    is supplied or it carries no finding blocks — the caller treats that as 'no cross-check'."""
    ids = set()
    if not ledger_text or art is None:
        return ids
    for bt, obj, _err in art.parse_blocks(ledger_text):
        if bt == "finding" and isinstance(obj, dict) and obj.get("id"):
            ids.add(art.fid_key(obj["id"]))
    return ids


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
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


def triage(text, ledger_text=None, strict=False):
    """Run the Feedback Triage integrity checks. Returns (code, lines).

    ledger_text = the paired Findings Ledger (Increment 2). When it carries finding blocks the
    maps_to cross-check engages (E5 dangling reference / W4 unmapped validated); when absent or
    empty of findings the check is skipped — self-contained schema + conflict checks only."""
    lines, errs, warns = [], [], []
    items = parse_items(text)
    if not items:
        return 0, ["feedback-triage: no feedback_item blocks found — nothing to triage"]
    led = ledger_ids(ledger_text)
    have_ledger = bool(led)  # a ledger with real findings to cross-check against

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
    # W3 — unreconciled decline (docs/finding-dispositions.md): a declined item that CITES a ledger
    # finding (an F-… token in evidence_refs) should carry an engine disposition marker in this same
    # artifact — otherwise the decline is invisible to the coach ladder and the /ready caveat.
    # OWNERSHIP BOUNDARY (W3 vs disposition-check DP2.2): W3 is feedback-triage-ARTIFACT-scoped
    # advisory — it never reads the sidecar; DP2.2 is sidecar-scoped ledger-integrity — it never
    # reads triage artifacts. The matching comment lives at DP2.2 in disposition_check.py.
    marker_ids = ({m["id"] for m in art.parse_disposition_markers(text)}
                  if art is not None and hasattr(art, "parse_disposition_markers") else set())
    for fid, obj in sorted(by_id.items()):
        if obj.get("triage") != "decline":
            continue
        cited = set()
        for ref in obj.get("evidence_refs") or []:
            if isinstance(ref, str) and art is not None:
                cited.update(art.FID_RE.findall(ref))
        for led_id in sorted(cited - marker_ids):
            warns.append("W3 unreconciled decline: declined feedback %s maps to engine finding %s "
                         "but no disposition was recorded — the decline lives only in this artifact"
                         % (fid, led_id))

    # E5 dangling maps_to / W4 unmapped validated (Increment 2) — the structured finding-id link,
    # cross-checked against the Findings Ledger. Only engaged when a ledger with findings is supplied
    # (the two-file cross-check mode, like finding-trace); without it the referential dimension is
    # skipped, not failed. E5 is a hard referential-integrity error (a maps_to must resolve to a real
    # ledger finding — assessment-independent, mirroring finding-trace E1); W4 is the advisory
    # presence gate for the spec's "a validated feedback item must point at a real F-…".
    if have_ledger:
        for fid, obj in sorted(by_id.items()):
            mapped = obj.get("maps_to")
            if mapped and art is not None and art.fid_key(mapped) not in led:
                errs.append("E5 dangling maps_to: %s.maps_to cites %s — not in the Findings Ledger"
                            % (fid, mapped))
            if obj.get("assessment") == _MAPS_REQUIRED and not mapped:
                warns.append("W4 unmapped validated: %s is assessment=validated but carries no "
                             "maps_to — a validated item must point at a real ledger finding" % fid)

    # Report
    lines.append("feedback-triage: %d item(s)%s%s" % (len(items),
                 "" if len(valid) == len(items) else " (%d well-formed)" % len(valid),
                 "" if have_ledger else " (no ledger — maps_to cross-check skipped)"))
    for obj, idx in valid:
        cw = ",".join(obj.get("conflicts_with") or []) or "—"
        lines.append("  %-7s src=%-16s assess=%-15s triage=%-9s conflicts=%-11s maps=%s"
                     % (obj.get("id"), (obj.get("source") or "?")[:16],
                        obj.get("assessment"), obj.get("triage"), cw, obj.get("maps_to") or "—"))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("feedback-triage: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: feedback-triage: %d advisory coherence gap(s) — see W1/W2/W3/W4 above" % len(warns))
    else:
        lines.append("feedback-triage: PASS (contract + conflict integrity)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    """Return (triage_path, ledger_path) from a run folder or explicit files. The ledger is the
    optional Increment-2 second artifact — a run folder globs *_Findings_Ledger_*.md; explicit args
    classify by block type (feedback_item -> triage, finding -> ledger). ledger_path is None when
    none is supplied, in which case the maps_to cross-check degrades (self-contained checks only)."""
    if len(paths) == 1 and os.path.isdir(paths[0]):
        return (_newest(glob.glob(os.path.join(paths[0], _TRIAGE_GLOB))),
                _newest(glob.glob(os.path.join(paths[0], _LEDGER_GLOB))))
    triage_path = ledger_path = None
    for p in paths:
        text = _read(p) or ""
        if triage_path is None and _has_block(text, "feedback_item"):
            triage_path = p
        elif ledger_path is None and _has_block(text, "finding"):
            ledger_path = p
    # fall back to the first non-ledger file arg if none carried a feedback block (so a clean empty
    # file reports no-op, matching Increment-1 behaviour)
    if triage_path is None:
        for p in paths:
            if p != ledger_path:
                triage_path = p
                break
    return triage_path, ledger_path


def run(paths, strict=False):
    path, ledger_path = resolve(paths)
    if not path:
        return 2, ["feedback-triage: no Feedback Triage artifact found (need a *_Feedback_Triage_*.md "
                   "or a file with apodictic:feedback_item blocks)"]
    text = _read(path)
    if text is None:
        return 2, ["feedback-triage: cannot read %s" % path]
    ledger_text = _read(ledger_path) if ledger_path else None
    return triage(text, ledger_text=ledger_text, strict=strict)


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

    # non-UTF8 artifact: _read must degrade to the unreadable path (None), never
    # a traceback (the disposition_check adjacent-exception class, swept repo-wide)
    import tempfile as _tf
    _fd, _nu = _tf.mkstemp(suffix=".md")
    with os.fdopen(_fd, "wb") as _fh:
        _fh.write(b"\xff\xfenot utf-8\xff")
    check("non_utf8_read_returns_none", _read(_nu) is None)
    os.unlink(_nu)

    def item(fid, assessment="validated", triage_="act-now", conflicts=None, source="Beta reader",
             claim="c", disp="d", maps_to=None):
        obj = {"schema": _SCHEMA_ID, "id": fid, "source": source, "claim": claim,
               "assessment": assessment, "triage": triage_, "disposition": disp}
        if conflicts is not None:
            obj["conflicts_with"] = conflicts
        if maps_to is not None:
            obj["maps_to"] = maps_to
        import json as _j
        return "<!-- apodictic:feedback_item\n%s\n-->" % _j.dumps(obj)

    def ledger(*fids):
        import json as _j
        blocks = []
        for f in fids:
            blocks.append("<!-- apodictic:finding\n%s\n-->" % _j.dumps(
                {"schema": "apodictic.finding.v1", "id": f, "mechanism": "m", "severity": "Must-Fix",
                 "confidence": "HIGH", "evidence_refs": ["c"], "fix_class": "x", "risk_if_fixed": "y"}))
        return "# Findings Ledger\n" + "\n".join(blocks) + "\n"

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

    # W3 unreconciled decline — a declined item citing a ledger F-… id with no disposition marker
    # in the same artifact fires; recording the marker (or citing no F-… id) clears it.
    declined_ref = item("FB-01", assessment="refuted", triage_="decline")\
        .replace('"disposition": "d"', '"disposition": "d", "evidence_refs": ["Pass 5", "F-P5-01"]')
    code_w, lines_w = triage(declined_ref)
    check("w3_unreconciled_decline_fires",
          code_w == 0 and any("W3 unreconciled decline" in ln and "F-P5-01" in ln for ln in lines_w))
    check("w3_strict_fails", triage(declined_ref, strict=True)[0] == 1)
    reconciled = declined_ref + "\n<!-- declined: F-P5-01 — reader claim refuted by the diagnosis -->\n"
    code_w, lines_w = triage(reconciled)
    check("w3_marker_reconciles", code_w == 0 and not any("W3" in ln for ln in lines_w))
    check("w3_no_fid_ref_clean",
          not any("W3" in ln for ln in triage(item("FB-02", assessment="refuted", triage_="decline"))[1]))
    # a NON-declined item citing an F-… id never fires W3
    acted = item("FB-03", assessment="validated", triage_="act-now")\
        .replace('"disposition": "d"', '"disposition": "d", "evidence_refs": ["F-P5-01"]')
    check("w3_only_on_decline", not any("W3" in ln for ln in triage(acted)[1]))

    # --- Increment 2: structured maps_to cross-checked against the Findings Ledger ---
    led = ledger("F-RR-01", "F-P1-02")
    # a validated item whose maps_to resolves -> clean (no E5, no W4)
    code, lines = triage(item("FB-01", maps_to="F-RR-01"), ledger_text=led)
    check("maps_to_resolves_clean",
          code == 0 and not any("E5" in ln or "W4" in ln for ln in lines))
    check("maps_to_report_column", any("maps=F-RR-01" in ln for ln in lines))
    # a dangling maps_to (no such ledger finding) -> E5 ERROR (assessment-independent)
    code, lines = triage(item("FB-01", maps_to="F-XX-99"), ledger_text=led)
    check("e5_dangling_maps_to",
          code == 1 and any("E5 dangling maps_to" in ln and "F-XX-99" in ln for ln in lines))
    # E5 fires even for a NON-validated item — a recorded maps_to must always resolve
    code, lines = triage(item("FB-02", assessment="refuted", triage_="decline", maps_to="F-XX-99"),
                         ledger_text=led)
    check("e5_dangling_any_assessment",
          code == 1 and any("E5 dangling maps_to" in ln for ln in lines))
    # a validated item WITHOUT maps_to, ledger present -> W4 advisory (ERROR under --strict)
    code_w, lines_w = triage(item("FB-01"), ledger_text=led)
    check("w4_unmapped_validated_advisory",
          code_w == 0 and any("W4 unmapped validated" in ln and "FB-01" in ln for ln in lines_w))
    check("w4_unmapped_validated_strict_fails", triage(item("FB-01"), ledger_text=led, strict=True)[0] == 1)
    # a NON-validated item without maps_to -> no W4 (only `validated` must map)
    check("w4_only_on_validated",
          not any("W4" in ln for ln in triage(item("FB-03", assessment="pending", triage_="monitor"),
                                              ledger_text=led)[1]))
    # partly-validated is NOT subject to W4 (spec: "a *validated* feedback item must point at ...")
    check("w4_skips_partly_validated",
          not any("W4" in ln for ln in triage(item("FB-04", assessment="partly-validated",
                                                    triage_="act-later"), ledger_text=led)[1]))
    # NO ledger supplied -> maps_to cross-check skipped entirely (self-contained schema/conflict only);
    # a validated item without maps_to, and even a dangling maps_to, do not fire without a ledger
    code, lines = triage(item("FB-01", maps_to="F-XX-99"))
    check("no_ledger_skips_maps_check",
          code == 0 and not any("E5" in ln or "W4" in ln for ln in lines)
          and any("maps_to cross-check skipped" in ln for ln in lines))
    # a ledger file with NO finding blocks is treated as no cross-check (degrade, not false E5/W4)
    check("empty_ledger_degrades",
          triage(item("FB-01", maps_to="F-XX-99"), ledger_text="# not a ledger\n")[0] == 0)
    # a malformed maps_to value (bad F-pattern) is caught by the schema (E1), not E5
    code, lines = triage(item("FB-01", maps_to="F-1"), ledger_text=led)
    check("bad_maps_to_pattern_is_e1", code == 1 and any("E1 invalid item" in ln for ln in lines))

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

    # Increment 2: a run folder with BOTH a triage artifact and a Findings Ledger cross-checks maps_to.
    d2 = tempfile.mkdtemp()
    made.append(d2)
    with open(os.path.join(d2, "Proj_Feedback_Triage_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Feedback Triage\n" + item("FB-01", maps_to="F-RR-01") + "\n")
    with open(os.path.join(d2, "Proj_Findings_Ledger_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(ledger("F-RR-01"))
    check("run_folder_ledger_crosscheck", run([d2])[0] == 0)
    # a dangling maps_to in the run folder is caught as E5
    with open(os.path.join(d2, "Proj_Feedback_Triage_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Feedback Triage\n" + item("FB-01", maps_to="F-XX-99") + "\n")
    rc2, ln2 = run([d2])
    check("run_folder_ledger_dangling", rc2 == 1 and any("E5 dangling maps_to" in ln for ln in ln2))
    # explicit two-file classification (triage + ledger, order-independent)
    with open(os.path.join(d2, "Proj_Feedback_Triage_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Feedback Triage\n" + item("FB-01", maps_to="F-RR-01") + "\n")
    check("explicit_two_file_crosscheck",
          run([os.path.join(d2, "Proj_Findings_Ledger_run.md"),
               os.path.join(d2, "Proj_Feedback_Triage_run.md")])[0] == 0)

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
