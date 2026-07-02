#!/usr/bin/env python3
"""disposition-check — engine-level finding-disposition integrity (docs/finding-dispositions.md).

`validate.sh disposition-check <run_folder|sidecar> [readiness_assessment] [--strict]` shells out
here. A finding disposition (`declined`/`deferred`) is an author decision recorded as an OVERLAY on
the finding lifecycle — the sidecar map `execution.finding_dispositions` mirroring the pinned
durable markers (`<!-- declined: F-… — reason -->` / `<!-- deferred: F-… until: trigger — reason
-->`, grammar SSoT: `apodictic_artifacts.parse_disposition_markers`). This validator owns the
artifact-side audit; `run_gate.py --check-state` owns the log-side one for governed projects
(the finding-trace / gate-state ownership split).

  DP0 record shape     every `finding_dispositions` record validates against
                       apodictic.finding_disposition.v1 (closed-key); `trigger` present iff
                       `deferred`; `reason` non-empty; map key == record id.            ERROR
  DP1 caveat teeth     when a readiness assessment (*Submission_Readiness_Assessment_*.md) is
                       present and an ACTIVE (finding_states[id] != 'revised') declined/deferred
                       Must-Fix exists (sidecar map or markers), the assessment must carry the
                       pinned caveat line(s) — `**Declined Must-Fixes:** …` / `**Deferred
                       Must-Fixes:** …` — naming EVERY such id (a mechanical per-family id-set
                       comparison, not a substring check). Missing line or missing id -> a
                       verdict is absorbing a set-aside finding.                        ERROR
  DP2 no laundering    2.1 the same run's completion artifacts carry both `<!-- resolved: F-X -->`
                       and an active declined/deferred marker for F-X (each direction launders
                       the other);                                                      ERROR
                       2.2 a `finding_dispositions` key that is not a ledger finding id (the
                       finding-trace E2 pattern applied to the new map);                ERROR
                       2.3 a dispositioned id whose ledger severity token differs from the
                       letter's Severity Calibration `locked` value (read-only; the
                       softness-check ID-match approach);                               ERROR
                       2.4 `triage_summary.<sev>` LESS THAN the ledger tally at a severity with a
                       dispositioned finding — a disposition write that "improved" the deficit
                       count (equality overall stays structured-findings' job; the tally is
                       structured_findings.severity_tally, the exact logic it audits);  ERROR
                       2.5 bidirectional marker/sidecar sync — every active marker has a record
                       and every active record has a marker in some home (WARN; ERROR under
                       --strict; a governed project's marker awaiting its next revision_round
                       fold is lag, not divergence — exempt).

Marker homes: the project Diagnostic_State.md Coaching Log, `*_Revision_Report_*.md`, and
`*_Feedback_Triage_*.md`. Each artifact is optional; a missing one skips its dimension (no false
failure). What deliberately reads dispositions NOWHERE: softness-check, deficit-lock,
severity-floor, structured-findings, finding-trace, regression-diff — a disposition is not an
override marker and grants no honesty-gate relief (the laundering firewall). The `/ready` workflow
runs `validate.sh disposition-check <sidecar> <assessment>` BEFORE delivering a verdict; a DP1
ERROR blocks the verdict. Degrades to an advisory WARN without python3 (the bash dispatcher).

  disposition_check.py disposition-check <run_folder|sidecar|files...> [--strict]
  disposition_check.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import json
import os
import re
import sys

try:
    import apodictic_artifacts as art
except ImportError:
    art = None
try:
    import finding_trace as ft
except ImportError:
    ft = None
try:
    import structured_findings as sf
except ImportError:
    sf = None

_SCHEMA_ID = "apodictic.finding_disposition.v1"
_LEDGER_GLOB = "*_Findings_Ledger_*.md"
_REPORT_GLOB = "*_Revision_Report_*.md"
_TRIAGE_GLOB = "*_Feedback_Triage_*.md"
_ASSESS_GLOB = "*Submission_Readiness_Assessment_*.md"
_STATE_MD = "Diagnostic_State.md"
# Pinned caveat-line grammar (submission-readiness.md §Output Template): a line-anchored family
# header, then `; `-separated `F-… — …` entries; ids extracted with the boundary-guarded id regex
# (art.FID_RE — the finding_trace._ID_RE pattern) and compared as ID SETS per family.
_CAVEAT_LINE_RE = re.compile(r"^\*\*(Declined|Deferred) Must-Fixes:\*\*(.*)$", re.MULTILINE)
_SEV_KEY = {"Must-Fix": "must_fix", "Should-Fix": "should_fix", "Could-Fix": "could_fix"}


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def _glob_multi(dirs, pattern):
    out = []
    for d in dirs:
        out.extend(glob.glob(os.path.join(d, pattern)))
    return sorted(set(out))


def _resolve(paths):
    """Resolve inputs to (sidecar, state_md, ledger, letter, reports, triages, assessment).

    One dir arg = a run folder (walk up for the sidecar; the Coaching Log home is the sidecar's
    SIBLING Diagnostic_State.md). One .json arg = the sidecar itself (project-root mode: artifacts
    are globbed from the project root and its runs/*/ archives — the /ready invocation shape).
    Explicit .md files classify by the output-structure.md naming convention."""
    sidecar = state_md = ledger = letter = assessment = None
    reports, triages = [], []
    dirs = []
    for p in paths:
        base = os.path.basename(p)
        if os.path.isdir(p):
            dirs.append(p)
        elif p.endswith(".json"):
            sidecar = p
        elif base == _STATE_MD:
            state_md = p
        elif "Submission_Readiness_Assessment_" in base:
            assessment = p
        elif "_Feedback_Triage_" in base:
            triages.append(p)
        elif "_Revision_Report_" in base:
            reports.append(p)
        elif "_Findings_Ledger_" in base or _has_finding_block(p):
            ledger = p
        else:
            letter = p
    if dirs:
        folder = dirs[0]
        sidecar = sidecar or (ft._walk_up_sidecar(folder) if ft else None)
        scan = [folder]
    elif sidecar:
        scan = [os.path.dirname(sidecar) or "."]
        scan += sorted(glob.glob(os.path.join(scan[0], "runs", "*")))
    else:
        scan = []
    if scan:
        ledger = ledger or _newest(_glob_multi(scan, _LEDGER_GLOB))
        if letter is None and ft is not None:
            for g in ft._LETTER_GLOBS:
                letter = _newest(_glob_multi(scan, g))
                if letter:
                    break
        reports = reports or _glob_multi(scan, _REPORT_GLOB)
        triages = triages or _glob_multi(scan, _TRIAGE_GLOB)
        assessment = assessment or _newest(_glob_multi(scan, _ASSESS_GLOB))
    if state_md is None and sidecar:
        cand = os.path.join(os.path.dirname(sidecar) or ".", _STATE_MD)
        if os.path.exists(cand):
            state_md = cand
    return sidecar, state_md, ledger, letter, reports, triages, assessment


def _has_finding_block(path):
    """Classify a candidate ledger on PARSED blocks (the _has_block idiom, meta-linter M2)."""
    if art is None:
        return False
    text = _read(path) or ""
    return any(bt == "finding" for bt, _o, _e in art.parse_blocks(text))


def _validate_record(fid, rec, where, schema):
    """DP0 for one record: schema shape + the trigger-iff-deferred conditional + non-empty reason
    + map-key/id agreement. The artifact-side twin of run_gate check_state's log-side checks."""
    errs = []
    if not isinstance(rec, dict):
        return ["%s: not a disposition record object" % where]
    errs.extend(art.validate_obj(rec, schema, where))
    if rec.get("id") != fid:
        errs.append("%s: record id %r does not match its map key" % (where, rec.get("id")))
    if rec.get("disposition") == "deferred":
        if not (isinstance(rec.get("trigger"), str) and rec["trigger"].strip()):
            errs.append("%s: deferred requires a non-empty 'trigger' — a deferral without a "
                        "recorded trigger is a decline with extra steps" % where)
    elif "trigger" in rec:
        errs.append("%s: 'trigger' only valid on a deferred disposition" % where)
    if not (isinstance(rec.get("reason"), str) and rec["reason"].strip()):
        errs.append("%s: 'reason' must be non-empty" % where)
    return errs


def check(sidecar_obj, ledger_text, letter_text, report_texts, triage_texts, state_text,
          assessment_text, strict=False, sidecar_parse_ok=True):
    """Run the disposition audit over already-read inputs. Returns (code, lines)."""
    lines, errs, warns, notes = [], [], [], []
    if art is None or ft is None:
        return 2, ["disposition-check: apodictic_artifacts/finding_trace unavailable — cannot run"]

    if not sidecar_parse_ok:
        errs.append("DP0 unparseable sidecar: Diagnostic_State.meta.json is present but not valid "
                    "JSON — the disposition map cannot be verified")
        sidecar_obj = None
    ex = (sidecar_obj or {}).get("execution") or {}
    records = ex.get("finding_dispositions") or {}
    if not isinstance(records, dict):
        errs.append("DP0: execution.finding_dispositions must be an object (map F-id -> record)")
        records = {}
    finding_states = ex.get("finding_states") or {}
    if not isinstance(finding_states, dict):
        finding_states = {}
    # Governed = the sidecar carries a non-empty gate_events log (state-lifecycle.md's dual-writer
    # split). Non-empty, so the template's default empty list does not read as governed.
    governed = bool(ex.get("gate_events"))
    triage_summary = (sidecar_obj or {}).get("triage_summary")

    def active(fid):
        # Supersedence (read-time precedence): finding_states is checked FIRST, everywhere.
        return finding_states.get(fid) != "revised"

    # Marker scan — the three homes, via the shared grammar SSoT (never a local regex).
    marker_homes = ([("coaching-log", state_text)]
                    + [("revision-report", t) for t in (report_texts or [])]
                    + [("feedback-triage", t) for t in (triage_texts or [])])
    marker_homes = [(h, t) for h, t in marker_homes if t is not None]
    markers = {}         # fid -> last-seen marker dict (kind/trigger/reason)
    report_marker_ids = set()  # dispositions asserted by the run's completion artifacts (DP2.1)
    for home, text in marker_homes:
        for m in art.parse_disposition_markers(text):
            markers[m["id"]] = dict(m, home=home)
            if home == "revision-report":
                report_marker_ids.add(m["id"])

    resolved_ids = set()
    for t in (report_texts or []):
        resolved_ids |= ft.resolved_cited_ids(t)

    inv = ft.ledger_inventory(ledger_text) if ledger_text else {}
    have_ledger = bool(inv)

    # Severity lookup: ledger blocks first, the sidecar findings[] mirror as fallback.
    severity = dict(inv)
    for el in ((sidecar_obj or {}).get("findings") or []):
        if isinstance(el, dict) and el.get("id") and el["id"] not in severity:
            severity[art.fid_key(el["id"])] = el.get("severity")

    # ---- DP0 — record shape --------------------------------------------------------------
    schema = art.load_schema(_SCHEMA_ID)
    for fid in sorted(records):
        errs.extend("DP0 %s" % e for e in
                    _validate_record(fid, records[fid], "finding_dispositions[%s]" % fid, schema))

    # ---- DP1 — declined/deferred Must-Fix caveat (the /ready teeth) ----------------------
    # Active set = sidecar records ∪ markers (governed lag means a marker can precede its record).
    dispositioned = {}
    for fid, rec in records.items():
        if isinstance(rec, dict) and rec.get("disposition") in ("declined", "deferred"):
            dispositioned[fid] = rec["disposition"]
    for fid, m in markers.items():
        dispositioned.setdefault(fid, m["kind"])
    active_dispo = {fid: kind for fid, kind in dispositioned.items() if active(fid)}

    if assessment_text is None:
        notes.append("no readiness assessment present — DP1 caveat check skipped")
    else:
        captured = {"declined": set(), "deferred": set()}
        for fam, rest in _CAVEAT_LINE_RE.findall(assessment_text):
            captured[fam.lower()].update(art.FID_RE.findall(rest))
        for fid in sorted(active_dispo):
            kind = active_dispo[fid]
            sev = severity.get(fid)
            if sev is None:
                warns.append("DP1 severity unresolvable for dispositioned %s (no ledger block or "
                             "sidecar findings[] entry) — caveat coverage cannot be verified" % fid)
                continue
            if sev != "Must-Fix":
                continue  # lower tiers are informational (Diagnostic Summary), not caveat material
            # Per-family id-set comparison: active set ⊆ captured set. Deliberately ONE-directional
            # (subset-legal): an EXTRA id on a caveat line is over-disclosure, never laundering —
            # only an absorbed (missing) id has teeth.
            if fid not in captured[kind]:
                errs.append("DP1 %s Must-Fix %s absent from the readiness caveat — a verdict is "
                            "absorbing a %s finding (pinned line: '**%s Must-Fixes:** …')"
                            % (kind, fid, kind, kind.capitalize()))

    # ---- DP2 — no severity laundering / no deficit improvement ---------------------------
    # 2.1 contradiction, scoped to the run's COMPLETION artifacts: the same report set both
    # resolves F-X and carries an active disposition marker for it — each direction launders the
    # other. (A Coaching-Log decline later resolved by a NEW round's report is legitimate
    # supersedence and is NOT this class — hence the report-only scope.)
    for fid in sorted(resolved_ids & report_marker_ids):
        if active(fid):
            errs.append("DP2.1 contradiction: the run's completion artifacts carry both "
                        "<!-- resolved: %s --> and an active %s marker for it" % (fid, markers[fid]["kind"]))
    # 2.2 phantom map key (the finding-trace E2 pattern applied to the new map). Sidecar-scoped
    # LEDGER-integrity only: DP2.2 never reads triage artifacts — the triage-artifact side of
    # decline reconciliation belongs to feedback-triage W3 (the ownership boundary; see
    # feedback_triage.py W3 for the matching comment).
    if have_ledger:
        for fid in sorted(records):
            if fid not in inv:
                errs.append("DP2.2 phantom: finding_dispositions[%s] — not in the ledger" % fid)
    elif records:
        notes.append("no findings ledger present — DP2.2 phantom / DP2.3 severity / DP2.4 tally skipped")
    # 2.3 severity immutability: the record schema is closed-key with NO severity field (a
    # disposition structurally cannot carry one); additionally, a dispositioned id's ledger
    # severity must equal the letter's Severity Calibration `locked` value — a post-hoc ledger
    # edit is the remaining channel. Read-only; a legitimate override-marked DELIVERED downgrade
    # stays softness-check's business.
    if have_ledger and letter_text:
        calib = {}
        for bt, obj, _e in art.parse_blocks(letter_text):
            if bt == "severity_calibration" and isinstance(obj, dict) and obj.get("id"):
                calib[art.fid_key(obj["id"])] = obj.get("locked")
        for fid in sorted(dispositioned):
            if fid in inv and fid in calib and inv[fid] != calib[fid]:
                errs.append("DP2.3 severity mismatch: dispositioned %s is %r in the ledger but "
                            "locked %r in the letter's Severity Calibration" % (fid, inv[fid], calib[fid]))
    # 2.4 tally guard: a disposition write that "improved" the deficit count. Recompute the ledger
    # tally with structured_findings.severity_tally — the EXACT logic structured-findings audits
    # triage_summary with, factored shared so this guard cannot drift from it. DP2 owns only the
    # disposition-shaped DECREMENT (<); overall equality stays structured-findings' job.
    if have_ledger and isinstance(triage_summary, dict) and sf is not None and dispositioned:
        ledger_objs = [obj for bt, obj, _e in art.parse_blocks(ledger_text)
                       if bt == "finding" and isinstance(obj, dict)]
        ledger_tally = sf.severity_tally(ledger_objs)
        dispo_sevs = {severity.get(fid) for fid in dispositioned} & set(_SEV_KEY)
        for sev in sorted(dispo_sevs):
            key = _SEV_KEY[sev]
            try:
                got = int(triage_summary.get(key, 0))
            except (TypeError, ValueError):
                continue  # a malformed triage_summary value is structured-findings' E, not DP2.4's
            if got < ledger_tally[key]:
                errs.append("DP2.4 tally decrement: triage_summary.%s=%d but the ledger carries %d "
                            "%s finding(s) — a disposition never decrements a count" % (key, got, ledger_tally[key], sev))
    # 2.5 bidirectional marker/sidecar sync (active only; WARN, ERROR under --strict).
    if not marker_homes:
        notes.append("no marker homes present (Coaching Log / Revision Report / Feedback Triage) "
                     "— DP2.5 sync check skipped")
    else:
        for fid in sorted(markers):
            if active(fid) and fid not in records:
                if governed:
                    notes.append("DP2.5: active %s marker for %s awaits its revision_round fold "
                                 "(governed lag, not divergence)" % (markers[fid]["kind"], fid))
                else:
                    warns.append("DP2.5 marker without record: active %s marker for %s has no "
                                 "finding_dispositions entry" % (markers[fid]["kind"], fid))
        for fid in sorted(records):
            if active(fid) and fid not in markers:
                warns.append("DP2.5 record without marker: active finding_dispositions[%s] has no "
                             "disposition marker in any home — the markers are the canonical source" % fid)

    # ---- report --------------------------------------------------------------------------
    lines.append("disposition-check: %d record(s), %d marker(s)%s"
                 % (len(records), len(markers),
                    "" if sidecar_obj is not None or not sidecar_parse_ok else " (no sidecar)"))
    for fid in sorted(set(list(records) + list(markers))):
        rec = records.get(fid) if isinstance(records.get(fid), dict) else {}
        kind = rec.get("disposition") or markers.get(fid, {}).get("kind", "?")
        lines.append("  %-12s %-9s sev=%-9s state=%-9s %s"
                     % (fid, kind, severity.get(fid, "?"), finding_states.get(fid, "—"),
                        "superseded" if not active(fid) else "active"))
    for n in notes:
        lines.append("  note: %s" % n)
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))
    if errs or (strict and warns):
        lines.append("disposition-check: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: disposition-check: %d advisory sync gap(s) — see DP2.5 above" % len(warns))
    else:
        lines.append("disposition-check: PASS (record shape + caveat coverage + no-laundering)")
    return 0, lines


def run(paths, strict=False):
    if art is None or ft is None:
        return 2, ["disposition-check: apodictic_artifacts/finding_trace unavailable — cannot run"]
    sidecar, state_md, ledger, letter, reports, triages, assessment = _resolve(paths)
    if not sidecar and not (reports or triages or state_md):
        return 2, ["disposition-check: nothing to check — need a run folder, a "
                   "Diagnostic_State.meta.json sidecar, or disposition-marker artifacts"]
    sidecar_obj, sc_ok = None, True
    if sidecar:
        raw = _read(sidecar)
        try:
            sidecar_obj = json.loads(raw) if raw is not None else None
            sc_ok = raw is not None and isinstance(sidecar_obj, dict)
        except ValueError:
            sidecar_obj, sc_ok = None, False
    return check(sidecar_obj,
                 _read(ledger) if ledger else None,
                 _read(letter) if letter else None,
                 [t for t in (_read(r) for r in reports) if t is not None],
                 [t for t in (_read(t_) for t_ in triages) if t is not None],
                 _read(state_md) if state_md else None,
                 _read(assessment) if assessment else None,
                 strict=strict, sidecar_parse_ok=sc_ok)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import tempfile
    import shutil
    rc = {"v": 0}
    made = []

    def check_(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def finding(fid, sev="Must-Fix"):
        return ('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"%s",'
                '"mechanism":"m","severity":"%s","confidence":"HIGH","evidence_refs":["c"],'
                '"fix_class":"x","risk_if_fixed":"y"}\n-->' % (fid, sev))

    ledger = ("## Ledger\n" + finding("F-P5-01") + "\n" + finding("F-DP-02") + "\n"
              + finding("F-P5-03", "Should-Fix") + "\n")

    def rec(fid, kind="declined", **kw):
        r = {"schema": _SCHEMA_ID, "id": fid, "disposition": kind, "reason": "held on purpose",
             "source": "author", "session": 3, "ts": "2026-07-01T00:00:00Z"}
        if kind == "deferred":
            r["trigger"] = "beta reads back"
        r.update(kw)
        return r

    def sidecar(dispositions, states=None, triage=None, governed=False):
        ex = {"finding_states": states or {}, "finding_dispositions": dispositions}
        if governed:
            ex["gate_events"] = [{"gate": "run_synthesis", "result": "mechanical-passed",
                                  "provenance": "mechanical", "ts": "t"}]
        sc = {"project": "P", "execution": ex}
        if triage is not None:
            sc["triage_summary"] = triage
        return sc

    coaching = ("## Coaching Log\n"
                "<!-- declined: F-P5-01 — abstraction is the register -->\n"
                "<!-- deferred: F-DP-02 until: beta reads back — waiting on reader signal -->\n")
    states_delivered = {"F-P5-01": "delivered", "F-DP-02": "delivered", "F-P5-03": "delivered"}
    both = {"F-P5-01": rec("F-P5-01"), "F-DP-02": rec("F-DP-02", "deferred")}
    caveat = ("## Readiness Verdict: CONDITIONALLY VIABLE\n"
              "**Declined Must-Fixes:** F-P5-01 — abstraction is the register (declined, session 3)\n"
              "**Deferred Must-Fixes:** F-DP-02 — until: beta reads back — waiting on reader signal\n")

    def go(dispositions=None, states=None, triage=None, governed=False, ledger_text=ledger,
           letter=None, reports=(), triages=(), state=coaching, assessment=None, strict=False,
           no_sidecar=False):
        sc = None if no_sidecar else sidecar(dispositions if dispositions is not None else both,
                                             states if states is not None else dict(states_delivered),
                                             triage, governed)
        return check(sc, ledger_text, letter, list(reports), list(triages), state, assessment,
                     strict=strict)

    # clean: records + markers in sync, no assessment (DP1 skipped with a note)
    code, lines = go()
    check_("clean_sync_passes", code == 0 and any("DP1 caveat check skipped" in ln for ln in lines))

    # ---- DP0 ----
    bad = dict(both); bad["F-P5-01"] = rec("F-P5-01", source="editor")
    check_("dp0_bad_enum", go(dispositions=bad)[0] == 1)
    bad = dict(both); bad["F-P5-01"] = rec("F-P5-01", reason="  ")
    code, lines = go(dispositions=bad)
    check_("dp0_empty_reason", code == 1 and any("'reason' must be non-empty" in ln for ln in lines))
    bad = dict(both); bad["F-DP-02"] = {k: v for k, v in rec("F-DP-02", "deferred").items() if k != "trigger"}
    code, lines = go(dispositions=bad)
    check_("dp0_deferred_without_trigger_refused",
           code == 1 and any("deferred requires a non-empty 'trigger'" in ln for ln in lines))
    bad = dict(both); bad["F-P5-01"] = rec("F-P5-01", trigger="stray")
    code, lines = go(dispositions=bad)
    check_("dp0_trigger_on_declined_refused",
           code == 1 and any("'trigger' only valid on a deferred" in ln for ln in lines))
    bad = dict(both); bad["F-P5-01"] = rec("F-P5-01", severity="Could-Fix")
    code, lines = go(dispositions=bad)
    check_("dp0_no_severity_field_closed_key",
           code == 1 and any("unknown field 'severity'" in ln for ln in lines))
    bad = dict(both); bad["F-P5-01"] = rec("F-DP-02", "deferred")
    code, lines = go(dispositions=bad)
    check_("dp0_key_id_mismatch", code == 1 and any("does not match its map key" in ln for ln in lines))

    # ---- DP1 ----
    code, lines = go(assessment=caveat)
    check_("dp1_caveat_present_clean", code == 0)
    code, lines = go(assessment="## Readiness Verdict: READY\nNo caveats.\n")
    check_("dp1_caveat_absent_fails",
           code == 1 and any("DP1 declined Must-Fix F-P5-01" in ln for ln in lines)
           and any("DP1 deferred Must-Fix F-DP-02" in ln for ln in lines))
    # one id missing from its family line
    code, lines = go(assessment="**Declined Must-Fixes:** F-P5-01 — held\n")
    check_("dp1_missing_one_id",
           code == 1 and any("F-DP-02" in ln and "DP1" in ln for ln in lines)
           and not any("DP1 declined Must-Fix F-P5-01" in ln for ln in lines))
    # an id on the WRONG family line is still absent from its own family
    code, lines = go(assessment="**Declined Must-Fixes:** F-P5-01; F-DP-02\n")
    check_("dp1_wrong_family_still_fails", code == 1 and any("DP1 deferred Must-Fix F-DP-02" in ln for ln in lines))
    # an EXTRA caveat id is subset-legal over-disclosure — never an error
    code, _ = go(assessment=caveat + "**Declined Must-Fixes:** F-ZZ-77 — over-disclosed\n")
    check_("dp1_extra_id_subset_legal", code == 0)
    # a superseded (revised) id is exempt — no caveat owed
    sup_states = dict(states_delivered, **{"F-P5-01": "revised"})
    code, lines = go(states=sup_states, assessment="**Deferred Must-Fixes:** F-DP-02 — until: beta reads back\n")
    check_("dp1_superseded_exempt", code == 0)
    # a Should-Fix disposition needs no caveat (lower tiers are informational)
    only_should = {"F-P5-03": rec("F-P5-03")}
    code, _ = go(dispositions=only_should, state="<!-- declined: F-P5-03 — style call -->",
                 assessment="## Readiness Verdict: READY\n")
    check_("dp1_should_fix_no_caveat_needed", code == 0)
    # marker-only active disposition (no record yet) still forces the caveat — the laundering
    # attempt "keep it out of the sidecar" has no purchase
    code, lines = go(dispositions={}, governed=True, assessment="## Readiness Verdict: READY\n")
    check_("dp1_marker_only_still_forces_caveat",
           code == 1 and any("DP1 declined Must-Fix F-P5-01" in ln for ln in lines))
    # severity unresolvable -> honest WARN, not silent pass, not false ERROR
    code, lines = go(ledger_text=None, assessment="## Readiness Verdict: READY\n")
    check_("dp1_severity_unresolvable_warns",
           code == 0 and any("severity unresolvable" in ln for ln in lines))

    # ---- DP2 ----
    report_contra = ("# Revision Report\n<!-- resolved: F-P5-01 -->\n"
                     "<!-- declined: F-P5-01 — but also resolved? -->\n")
    code, lines = go(reports=[report_contra])
    check_("dp2_1_contradiction",
           code == 1 and any("DP2.1 contradiction" in ln and "F-P5-01" in ln for ln in lines))
    # legitimate supersedence: an OLD Coaching-Log decline + a new report resolving it (state revised)
    code, lines = go(states=dict(states_delivered, **{"F-P5-01": "revised"}),
                     reports=["# Revision Report\n<!-- resolved: F-P5-01 -->\n"])
    check_("dp2_1_supersedence_not_contradiction",
           code == 0 and not any("DP2.1" in ln for ln in lines))
    phantom = dict(both); phantom["F-ZZ-99"] = rec("F-ZZ-99")
    code, lines = go(dispositions=phantom,
                     state=coaching + "<!-- declined: F-ZZ-99 — phantom -->\n")
    check_("dp2_2_phantom", code == 1 and any("DP2.2 phantom" in ln and "F-ZZ-99" in ln for ln in lines))
    letter_cal = ('# Letter\n<!-- apodictic:severity_calibration\n'
                  '{"schema":"apodictic.severity_calibration.v1","id":"F-P5-01","locked":"Should-Fix",'
                  '"delivered":"Should-Fix","direction":"unchanged","rationale":"r"}\n-->\n')
    code, lines = go(letter=letter_cal)
    check_("dp2_3_severity_mismatch",
           code == 1 and any("DP2.3 severity mismatch" in ln and "F-P5-01" in ln for ln in lines))
    letter_ok = letter_cal.replace('"locked":"Should-Fix"', '"locked":"Must-Fix"')
    check_("dp2_3_matching_clean", go(letter=letter_ok)[0] == 0)
    code, lines = go(triage={"must_fix": 1, "should_fix": 1, "could_fix": 0})
    check_("dp2_4_tally_decrement",
           code == 1 and any("DP2.4 tally decrement" in ln and "must_fix=1" in ln for ln in lines))
    check_("dp2_4_honest_tally_clean", go(triage={"must_fix": 2, "should_fix": 1, "could_fix": 0})[0] == 0)
    # DP2.5 marker without record (non-governed) — WARN by default, ERROR under --strict
    code, lines = go(dispositions={"F-P5-01": rec("F-P5-01")})
    check_("dp2_5_marker_without_record_warns",
           code == 0 and any("DP2.5 marker without record" in ln and "F-DP-02" in ln for ln in lines))
    check_("dp2_5_strict_escalates", go(dispositions={"F-P5-01": rec("F-P5-01")}, strict=True)[0] == 1)
    # governed-lag exemption: same desync on a governed sidecar is a note, not a WARN
    code, lines = go(dispositions={"F-P5-01": rec("F-P5-01")}, governed=True)
    check_("dp2_5_governed_lag_exempt",
           code == 0 and any("governed lag" in ln for ln in lines)
           and not any("DP2.5 marker without record" in ln for ln in lines))
    code, lines = go(state="## Coaching Log\n<!-- declined: F-P5-01 — abstraction is the register -->\n")
    check_("dp2_5_record_without_marker_warns",
           code == 0 and any("DP2.5 record without marker" in ln and "F-DP-02" in ln for ln in lines))
    check_("dp2_5_record_without_marker_strict",
           go(state="## Coaching Log\n<!-- declined: F-P5-01 — abstraction is the register -->\n",
              strict=True)[0] == 1)

    # ---- gardening (state-lifecycle.md §State Gardening) ----
    # active disposition markers survive gardening and must still be FOUND in a gardened state
    # file; a SUPERSEDED disposition compressed to the one-line archive form must NOT parse as an
    # active marker (it is prose, not an HTML comment).
    gardened = ("## Coaching Log\n"
                "<!-- declined: F-P5-01 — abstraction is the register -->\n"
                "<!-- deferred: F-DP-02 until: beta reads back — waiting on reader signal -->\n"
                "## Archived\n"
                "- F-P5-03: declined session 2, later revised session 5. "
                "Full record: Diagnostic_State_Archive_2026-06-01T10-00.md\n")
    code, lines = go(state=gardened)
    check_("gardening_active_markers_still_found", code == 0)
    found = art.parse_disposition_markers(gardened)
    check_("gardening_archive_line_not_a_marker",
           len(found) == 2 and not any(m["id"] == "F-P5-03" for m in found))

    # unparseable sidecar is an ERROR, not a clean empty map
    code, lines = check(None, ledger, None, [], [], coaching, None, sidecar_parse_ok=False)
    check_("unparseable_sidecar_errors", code == 1 and any("DP0 unparseable sidecar" in ln for ln in lines))

    # ---- file/run-folder resolution (end-to-end) ----
    d = tempfile.mkdtemp()
    made.append(d)
    with open(os.path.join(d, "P_Findings_Ledger_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(ledger)
    with open(os.path.join(d, "Diagnostic_State.meta.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(sidecar(both, dict(states_delivered)), fh)
    with open(os.path.join(d, _STATE_MD), "w", encoding="utf-8", newline="") as fh:
        fh.write(coaching)
    with open(os.path.join(d, "Submission_Readiness_Assessment_2026-07-01.md"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write(caveat)
    check_("run_folder_resolution", run([d])[0] == 0)
    check_("sidecar_plus_assessment_resolution",
           run([os.path.join(d, "Diagnostic_State.meta.json"),
                os.path.join(d, "Submission_Readiness_Assessment_2026-07-01.md")])[0] == 0)
    # the /ready laundering arm end-to-end: strip the caveat -> DP1 blocks
    with open(os.path.join(d, "Submission_Readiness_Assessment_2026-07-01.md"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("## Readiness Verdict: READY\nLooks great.\n")
    check_("run_folder_dp1_blocks", run([d])[0] == 1)
    check_("usage_error_on_nothing", run([os.path.join(d, "nope", "nothing.xyz")])[0] == 2)

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "disposition-check"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: disposition_check.py disposition-check <run_folder|sidecar|files...> "
              "[--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
