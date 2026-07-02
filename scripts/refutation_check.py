#!/usr/bin/env python3
"""APODICTIC finding-disconfirmation gates (docs/finding-disconfirmation.md §8).

HIGH means "survived": the Step 6b Finding Disconfirmation Pass (run-synthesis.md
§Processing Protocol) attempts to REFUTE each locked Must-Fix / HIGH Should-Fix finding
against the manuscript text and records every attempt in
`[Project]_Refutation_Record_[runlabel].md` — one `apodictic.refutation.v1` block per
attempt plus exactly one `apodictic.refutation_budget.v1` block. Three arms enforce it:

  refutation-coverage <editorial_letter> <findings_ledger> <refutation_record>
      V1 — no HIGH without survived refutation. Every synthesis-bound ledger finding at
      confidence HIGH needs a record block with attempted:true + outcome "survived", OR a
      cap-bound disclosure marker `<!-- refutation: not-attempted-budget F-<ORIGIN>-<NN> -->`
      in the letter BODY — honored ONLY when the RECOMPUTED budget actually binds (the
      eligible set recomputed from the ledger — Must-Fix ∪ HIGH Should-Fix, minus
      disposition-exempt — exceeds the spec cap 15) AND the block says bound:true AND the id
      is unprocessed (a marker on a processed finding, under an unbound budget, or under a
      bound:true claim the ledger recompute does not corroborate, is an ERROR: the marker is
      a disclosure, not an exemption you can reach for). The budget block is the pass's
      SELF-REPORT: its eligible/bound/cap are recomputed/pinned against the ledger and the
      spec — mismatch is a blocking ERROR (recompute, don't trust — the recorded-field
      rule applied to an exemption gate; Codex P1, PR #161: a fabricated bound:true
      budget must never let an untested HIGH ship as "cap-bound"). Every Must-Fix needs a
      record with attempted:true — the cap can never bind on Must-Fix (their ceiling is 10,
      the cap is 15), so a missing Must-Fix record is a silent skip, forbidden. Every record
      id must resolve to a locked (Must-Fix/Should-Fix) ledger finding (dangling = ERROR). A
      finding whose id carries a live declined/deferred disposition marker
      (docs/finding-dispositions.md; grammar SSoT `apodictic_artifacts.parse_disposition_markers`,
      read from the ledger or the letter) is exempt — the author already ruled (spec §5).

  refutation-evidence <refutation_record> [<manuscript_snapshot>] [--require-snapshot]
      V2 — attempts without quote-anchored counter-evidence don't count. Every record needs
      counter_evidence_quotes / alternative_explanations at minItems 1 (schema; a violation
      voids the attempt and is an ERROR). Each quote must occur VERBATIM in the intake
      manuscript snapshot — checked against the as-is snapshot bytes — and be single-line
      (no \\n / bare \\r). Verbatim-presence only (count >= 1): A6's uniqueness/offset
      requirements are deliberately dropped — a counter-evidence quote is evidence, not an
      anchor (docs/annotated-manuscript.md §A6 divergence, stated in the spec). A fabricated
      quote (count 0) is an ERROR — you cannot claim an attempt without touching real text.
      Quote > 25 words -> WARN (quote-budget hygiene, counter_evidence_quotes only; WARNs are
      advisory, exit 0, per the standing validate.sh convention). Each alternative_explanations
      entry must carry a quote mark, a Ch./p. locator, or a contract-artifact reference ->
      WARN if none (the §6.4 grounding floor; deeper grounding is prompt-side, audited by the
      rubber-stamp eval fixture). Snapshot handling splits by what the flow requires:
        * the snapshot is REQUIRED (missing = ERROR) under --require-snapshot, or when the
          record's folder holds a *_Core_DE_Synthesis_* / *_Full_DE_Synthesis_* letter (the
          same run-shape detection the annotated-manuscript offer uses) — a missing snapshot
          on a core-de/full-de run is a broken intake, not a degrade case;
        * elsewhere a missing snapshot is a WARN and every demotion in the record is VOID:
          outcomes weakened/refuted may NOT be transcribed into the ledger without verified
          quotes (confidence stays unchanged), and the letter must carry the disclosure line
          "counter-evidence quotes unverified — no intake snapshot; demotions withheld".
      When present, each record's snapshot_path/snapshot_sha256 must match the snapshot file
      actually on disk (as-is bytes, hashed) — mismatch = ERROR (the record was written
      against different bytes). snapshot_path is a MODEL-WRITTEN value used for filesystem
      READS only: it is resolved beside the record and contained to that folder (realpath);
      an absolute or escaping path is refused by name, never followed, never written to.
      Budget arithmetic: processed == min(eligible, cap) and bound == (eligible > processed),
      from the block's own fields -> ERROR on mismatch. cap must equal the spec constant 15
      (§5 — not a per-run knob) and processed must equal the count of schema-valid refutation
      blocks in the record -> both ERROR (the block is a self-report; promoted from WARN per
      the Codex P1 — a processed count with no blocks behind it is fabricated work).

  refutation-write-scope <findings_ledger> <refutation_record>
      V3 — the pass may write only refutation.* + confidence; any severity write fails the
      run. Schema-clean records only. A `severity` key at any depth — or any canonical
      severity token (Must-Fix | Should-Fix | Could-Fix) used as a field value — inside a
      refutation/budget block is an ERROR (the schema omits the property; this arm enforces
      it against the subset checker's unknown-key tolerance). For every processed id: ledger
      `confidence` == record `confidence_after`, and confidence_after obeys the outcome caps
      (survived = unchanged, never confidence-raising; weakened capped at MEDIUM; refuted =
      LOW/UNCERTAIN). The equality assertion is SKIPPED for records V2 voided for a missing
      snapshot (re-derived here from the record's snapshot_path resolved beside the record) —
      the expected ledger != record delta IS the withheld demotion. V3 is a pre-delivery
      fail-the-run gate, not a write-prevention mechanism: it cannot stop a bad transcription
      from being written, it stops the run from shipping with one (the deficit-lock /
      softness-check posture). "The letter cannot deliver below the locked severity" remains
      owned by deficit-lock + softness-check, which this pass runs entirely downstream of.

  --self-test    built-in cases (all three arms; disk fixtures in a temp dir)

Block grammar + schema validation come from the shared `apodictic_artifacts` module
(schemas/ are the source of truth: apodictic.refutation.v1 + apodictic.refutation_budget.v1).
Marker scanning strips code spans via the `override_marker` SSoT (meta-linter M5/M6 class)
and boundary-matches the Finding Lifecycle ID (F-P5-01 != F-P5-011). Malformed blocks are
refused with named shape errors — never silently filtered before comparison.

Exit: 0 pass (WARNs/NOTEs are advisory), 1 ERROR(s), 2 usage error.
"""
import glob
import hashlib
import os
import re
import sys

import apodictic_artifacts as art
from override_marker import strip_code_spans  # code-span stripping SSoT (meta-linter M6)

REFUTATION_SCHEMA = "apodictic.refutation.v1"
BUDGET_SCHEMA = "apodictic.refutation_budget.v1"
LOCKED = {"Must-Fix", "Should-Fix"}
# §5 cap: 15 findings per run — a SPEC CONSTANT (the Must-Fix ceiling is 10, so the cap can
# only ever bind on HIGH Should-Fix). Pinned here because the budget block's `cap` field is
# model-written: a lowered cap manufactures a "binding" budget, the same fabrication class
# as a lied bound:true (Codex P1, PR #161) — recompute/pin, don't trust.
SPEC_CAP = 15
# §7 caps table: outcome -> permitted confidence_after values. survived is absent on
# purpose — its rule is equality with the ledger (unchanged; never confidence-raising),
# asserted separately.
OUTCOME_CAPS = {"weakened": ("MEDIUM", "LOW", "UNCERTAIN"),
                "refuted": ("LOW", "UNCERTAIN")}
QUOTE_WORD_BUDGET = 25  # output-policy.md §Output Constraints quote budget
PINNED_DISCLOSURE = "counter-evidence quotes unverified — no intake snapshot; demotions withheld"

# Cap-bound disclosure marker (spec §5), pinned form:
#   <!-- refutation: not-attempted-budget F-<ORIGIN>-<NN> -->
# Scanned on the code-span-stripped letter BODY only; the id is boundary-matched so
# F-P5-01 never matches inside F-P5-011 (the override_marker discipline, new `refutation:`
# comment family — no collision with override:/finding:/declined:/deferred:/resolved:).
_BUDGET_MARKER_RE = re.compile(
    r"<!--\s*refutation:\s*not-attempted-budget\s+(F-[A-Za-z0-9]+-[0-9]{2,})(?![\w-])\s*-->")
# Letter body = everything before the first appendix heading (markers in appendix bodies
# are non-canonical, the standing body-vs-appendix override discipline).
_APPENDIX_SPLIT_RE = re.compile(r"Appendix\s+[A-Z]\b|Severity\s+Calibration", re.IGNORECASE)
# §6.4 grounding floor for alternative_explanations: a quote mark, a Ch./p. locator, or a
# contract-artifact reference. Quote marks are the double-quote family only (an apostrophe
# in a contraction must not count as grounding).
_QUOTE_MARK_RE = re.compile(r'["“”]')
_PAGE_LOCATOR_RE = re.compile(r"\bpp?\.\s*\d+")
_CONTRACT_REF_RE = re.compile(r"\bcontract\b|_Contract_", re.IGNORECASE)
# Run-shape detection (the annotated-manuscript offer's rule): the run wrote a full letter.
_RUN_SHAPE_GLOBS = ("*_Core_DE_Synthesis_*.md", "*_Full_DE_Synthesis_*.md")


def _body(letter_text):
    m = _APPENDIX_SPLIT_RE.search(letter_text or "")
    return letter_text[:m.start()] if m else (letter_text or "")


def parse_record(record_text):
    """((refutations, budgets), shape_errors) — the record's schema-validated refutation /
    refutation_budget blocks (parsed via art.parse_blocks, never a raw marker scan). Malformed blocks (bad
    JSON, non-dict payload, schema-invalid) are refused with NAMED shape errors and excluded
    from the returned lists — never silently filtered into a comparison."""
    refs, budgets, errs = [], [], []
    r_schema = art.load_schema(REFUTATION_SCHEMA)
    b_schema = art.load_schema(BUDGET_SCHEMA)
    n_r = n_b = 0
    for btype, obj, jerr in art.parse_blocks(record_text or ""):
        if btype == "refutation":
            n_r += 1
            where = "refutation block #%d" % n_r
            schema = r_schema
            dest = refs
        elif btype == "refutation_budget":
            n_b += 1
            where = "refutation_budget block #%d" % n_b
            schema = b_schema
            dest = budgets
        else:
            continue
        if jerr:
            errs.append("%s: invalid JSON — %s" % (where, jerr))
            continue
        if not isinstance(obj, dict):
            errs.append("%s: payload is not a JSON object" % where)
            continue
        block_errs = art.validate_obj(obj, schema, where)
        if block_errs:
            errs.extend(block_errs)
            continue
        dest.append(obj)
    return (refs, budgets), errs


def _locked_findings(ledger_text):
    """Locked apodictic.finding.v1 dicts from the ledger (tolerant parse — ledger block
    validity is structured-findings/deficit-lock's job, not this gate's)."""
    out = []
    for btype, obj, jerr in art.parse_blocks(ledger_text or ""):
        if jerr or btype != "finding" or not isinstance(obj, dict):
            continue
        if str(obj.get("schema", "")).startswith("apodictic.finding."):
            out.append(obj)
    return out


def _records_by_id(refs):
    """(id -> record, duplicate_errors). Ids are fid_key-coerced so a malformed id can
    never crash a dict key (the non-hashable/non-string id class)."""
    out, errs = {}, []
    for r in refs:
        fid = art.fid_key(r.get("id"))
        if fid in out:
            errs.append("duplicate refutation block for id %s — one attempt record per finding" % fid)
        out[fid] = r
    return out, errs


def _the_budget(budgets, errs):
    """Exactly one budget block per record (spec §4). Appends named errors; returns the
    block or None."""
    if len(budgets) == 0:
        errs.append("record carries no %s block — the budget block is the mechanical basis "
                    "for cap-bound disclosure; a zero-eligible run still writes one with "
                    "eligible: 0" % BUDGET_SCHEMA)
        return None
    if len(budgets) > 1:
        errs.append("record carries %d %s blocks — exactly one budget block per record"
                    % (len(budgets), BUDGET_SCHEMA))
        return None
    return budgets[0]


def _disposition_ids(*texts):
    """Ids carried by live declined/deferred disposition markers in any of `texts`
    (grammar SSoT: apodictic_artifacts.parse_disposition_markers — code-span-stripped,
    boundary-matched)."""
    out = set()
    for t in texts:
        for m in art.parse_disposition_markers(t or ""):
            out.add(m["id"])
    return out


def _resolve_snapshot(record_dir, snapshot_path):
    """(resolved_path_or_None, refusal_or_None). Containment: snapshot_path is a
    MODEL-WRITTEN value used only for filesystem READS — resolved beside the record and
    confined to that folder via realpath. Absolute paths and traversal (including symlink
    escape) are refused by name, never followed. Never used as a write target."""
    if not isinstance(snapshot_path, str) or not snapshot_path.strip():
        return None, "snapshot_path is not a non-empty string"
    if os.path.isabs(snapshot_path):
        return None, ("snapshot_path %r is absolute — it must be the intake-snapshot "
                      "filename beside the record; refusing to read it" % snapshot_path)
    base = os.path.realpath(record_dir or ".")
    target = os.path.realpath(os.path.join(base, snapshot_path))
    if target != base and not target.startswith(base + os.sep):
        return None, ("snapshot_path %r escapes the run folder (containment) — refusing "
                      "to read it" % snapshot_path)
    return target, None


def _core_full_run_shape(record_dir):
    """True iff the record's folder holds a *_Core_DE_Synthesis_* / *_Full_DE_Synthesis_*
    letter — the run-shape detection the annotated-manuscript offer uses. On these runs the
    intake snapshot is mandatory (run-core.md §Intake Protocol), so refutation-evidence
    requires it even without the explicit --require-snapshot flag."""
    for g in _RUN_SHAPE_GLOBS:
        if glob.glob(os.path.join(record_dir or ".", g)):
            return True
    return False


def _read_bytes(path):
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except OSError:
        return None


def _short(s, n=60):
    s = str(s)
    return s if len(s) <= n else s[:n] + "…"


# ------------------------------------------------------------------ V1 coverage

def refutation_coverage(letter_text, ledger_text, record_text):
    """V1 — no HIGH without survived refutation. Returns (errs, warns, notes)."""
    errs, warns, notes = [], [], []
    (refs, budgets), shape_errs = parse_record(record_text)
    errs.extend(shape_errs)
    budget = _the_budget(budgets, errs)
    bound = budget.get("bound") if budget else None
    by_id, dup_errs = _records_by_id(refs)
    errs.extend(dup_errs)

    findings = _locked_findings(ledger_text)
    locked = [f for f in findings if f.get("severity") in LOCKED]
    ledger_ids = {art.fid_key(f.get("id")) for f in locked if f.get("id") is not None}
    dispo = _disposition_ids(ledger_text, letter_text)

    # Budget recompute (BLOCKING — the recorded-field rule applied to an exemption gate:
    # recompute a recorded value, never trust it; Codex P1, PR #161): the budget block is
    # the pass's SELF-REPORT, and the
    # cap-bound exemption used to trust it — a fabricated bound:true with eligible/processed
    # lies let an untested HIGH ship as "cap-bound" with zero real refutation work, with the
    # mismatches surfacing only as advisory WARNs. eligible is DERIVED from the lock
    # (Must-Fix ∪ HIGH Should-Fix, dispositions excluded), bound is DERIVED from that
    # recompute vs the spec cap, and cap is the §5 spec constant — every one of the block's
    # fields is a claim to verify, never an input.
    recomputed_eligible = sum(
        1 for f in locked
        if art.fid_key(f.get("id")) not in dispo
        and (f.get("severity") == "Must-Fix"
             or (f.get("severity") == "Should-Fix" and f.get("confidence") == "HIGH")))
    recomputed_bound = recomputed_eligible > SPEC_CAP
    if budget is not None:
        if budget.get("cap") != SPEC_CAP:
            errs.append("budget block records cap: %r but the refutation cap is the spec "
                        "constant %d (docs/finding-disconfirmation.md §5) — the cap is not "
                        "a per-run knob; a lowered cap manufactures a binding budget"
                        % (budget.get("cap"), SPEC_CAP))
        if budget.get("eligible") != recomputed_eligible:
            errs.append("budget block records eligible: %r but the ledger's eligible set "
                        "(Must-Fix ∪ HIGH Should-Fix, dispositions excluded) recomputes to "
                        "%d — eligible is derived from the lock, not asserted; reconcile "
                        "the budget with the ledger"
                        % (budget.get("eligible"), recomputed_eligible))
        if bound != recomputed_bound:
            errs.append("budget block records bound: %r but the ledger recompute derives "
                        "bound: %r (eligible recomputes to %d vs cap %d) — bound is a "
                        "claim the ledger must corroborate, never an input to the "
                        "cap-bound exemption"
                        % (bound, recomputed_bound, recomputed_eligible, SPEC_CAP))

    # Cap-bound disclosure markers — letter BODY only, code spans stripped (SSoT). The
    # exemption is honored only when the RECOMPUTED budget actually binds: the block's
    # bound:true is necessary (the pass must have disclosed) but never sufficient.
    markers = set(_BUDGET_MARKER_RE.findall(strip_code_spans(_body(letter_text))))
    for fid in sorted(markers):
        if fid in by_id:
            errs.append("cap-bound disclosure marker names %s, which HAS a refutation record "
                        "— the marker is a disclosure of an unprocessed finding, not an "
                        "exemption; remove the marker or the record" % fid)
        elif bound is not True:
            errs.append("cap-bound disclosure marker for %s under an unbound budget "
                        "(bound: %r) — the marker is honored only when the budget block "
                        "records bound: true" % (fid, bound))
        elif not recomputed_bound:
            errs.append("cap-bound disclosure marker for %s but the recomputed budget does "
                        "NOT bind (eligible recomputes to %d from the ledger, cap %d) — "
                        "bound: true in the budget block is a claim to verify, never an "
                        "input; run the Step 6b pass for %s or demote its confidence per "
                        "the §7 caps table" % (fid, recomputed_eligible, SPEC_CAP, fid))
        elif fid not in ledger_ids:
            errs.append("cap-bound disclosure marker names %s, which resolves to no locked "
                        "ledger finding — a disclosure for a phantom finding" % fid)

    # Per-finding coverage.
    for f in locked:
        sev = f.get("severity")
        conf = f.get("confidence")
        fid = art.fid_key(f.get("id"))
        label = "%s — %s" % (fid, _short(f.get("mechanism", "?")))
        if fid is None:
            if sev == "Must-Fix" or conf == "HIGH":
                errs.append("locked %s finding without a Finding Lifecycle ID cannot be "
                            "matched to a refutation record (%s) — assign an id "
                            "(apodictic.finding.v1 requires one)" % (sev, label))
            continue
        if fid in dispo:
            if fid in by_id:
                notes.append("%s carries a declined/deferred disposition AND a refutation "
                             "record — the record stands, the disposition exempts nothing "
                             "extra" % fid)
            else:
                notes.append("%s carries a declined/deferred disposition — exempt from the "
                             "refutation requirement (the author already ruled; spec §5)" % fid)
                continue
        rec = by_id.get(fid)
        if rec is None:
            if sev == "Must-Fix":
                errs.append("Must-Fix finding %s has no refutation record — every Must-Fix "
                            "is always processed (the cap cannot bind on Must-Fix); run the "
                            "Step 6b pass for it or record the author's disposition" % label)
            elif conf == "HIGH":
                if fid in markers and bound is True and recomputed_bound:
                    notes.append("HIGH finding %s not attempted — cap-bound and disclosed "
                                 "(marker honored: bound: true corroborated by the ledger "
                                 "recompute); its letter language must say convergence-only, "
                                 "not stress-tested" % fid)
                elif fid not in markers:
                    errs.append("HIGH finding %s has no survived refutation record and no "
                                "cap-bound disclosure marker — HIGH means survived; demote "
                                "the confidence per the §7 caps table, run the pass, or "
                                "disclose the cap with "
                                "<!-- refutation: not-attempted-budget %s --> (honored only "
                                "when the recomputed budget binds)" % (label, fid))
                # fid in markers under an unbound budget, or under a bound:true the
                # recompute does not corroborate, already errored in the marker scan.
            continue
        if rec.get("attempted") is not True:
            errs.append("%s finding %s has a refutation record with attempted: false — a "
                        "recorded skip is not an attempt; %s" %
                        (sev, label,
                         "Must-Fix is never skippable" if sev == "Must-Fix"
                         else "a HIGH needs a real survived attempt"))
            continue
        if conf == "HIGH" and rec.get("outcome") != "survived":
            errs.append("HIGH finding %s: record outcome is %r — HIGH requires a survived "
                        "attempt; transcribe confidence_after per the §7 caps table "
                        "(refutation-write-scope checks the exact transcription)"
                        % (label, rec.get("outcome")))

    # Dangling records: every record id resolves to a LOCKED ledger finding.
    all_ids = {art.fid_key(f.get("id")) for f in findings if f.get("id") is not None}
    for fid in sorted(k for k in by_id if k is not None):
        if fid not in ledger_ids:
            if fid in all_ids:
                errs.append("refutation record id %s resolves to a ledger finding that is "
                            "not synthesis-bound (not Must-Fix/Should-Fix) — the pass's "
                            "eligible set is locked findings only" % fid)
            else:
                errs.append("dangling refutation record id %s — it resolves to no ledger "
                            "finding" % fid)
    for fid in (k for k in by_id if k is None):
        errs.append("refutation record with a null id — cannot resolve to a ledger finding")
    return errs, warns, notes


# ------------------------------------------------------------------ V2 evidence

def refutation_evidence(record_text, record_dir, snapshot_arg=None, require_snapshot=False):
    """V2 — attempts without quote-anchored counter-evidence don't count.
    Returns (errs, warns, notes). `snapshot_arg` is the explicit CLI snapshot path (or
    None: resolve each record's snapshot_path beside the record, contained)."""
    errs, warns, notes = [], [], []
    (refs, budgets), shape_errs = parse_record(record_text)
    errs.extend(shape_errs)
    budget = _the_budget(budgets, errs)

    # Budget arithmetic (spec §V2): internal consistency of the block's own fields, plus
    # the two grounded checks — cap pinned to the spec constant, processed pinned to the
    # actual schema-valid block count (BLOCKING, promoted from WARN per the Codex P1 on
    # PR #161: the block is a self-report; a processed count with no blocks behind it is
    # fabricated work).
    if budget is not None:
        cap, eligible, processed, bound = (budget.get("cap"), budget.get("eligible"),
                                           budget.get("processed"), budget.get("bound"))
        if cap != SPEC_CAP:
            errs.append("budget block records cap: %r but the refutation cap is the spec "
                        "constant %d (docs/finding-disconfirmation.md §5) — the cap is not "
                        "a per-run knob; a lowered cap manufactures a binding budget"
                        % (cap, SPEC_CAP))
        if processed != min(eligible, cap):
            errs.append("budget arithmetic: processed (%r) != min(eligible, cap) = %r — the "
                        "pass processes Must-Fix first, then HIGH Should-Fix, up to the cap"
                        % (processed, min(eligible, cap)))
        if bound != (eligible > processed):
            errs.append("budget arithmetic: bound (%r) != (eligible > processed) (%r) — the "
                        "bound flag is derived, not asserted" % (bound, eligible > processed))
        if processed != len(refs):
            errs.append("budget block records processed: %r but the record carries %d "
                        "schema-valid refutation block(s) — processed is a recorded count "
                        "the record itself must corroborate (malformed blocks are refused "
                        "above and do not count); reconcile the budget with the record"
                        % (processed, len(refs)))

    required = bool(require_snapshot) or _core_full_run_shape(record_dir)
    explicit = None
    if snapshot_arg is not None:
        if os.path.isfile(snapshot_arg):
            explicit = snapshot_arg
        else:
            errs.append("named manuscript snapshot not found: %s — a snapshot the caller "
                        "names must exist (for the resolve-beside-the-record path, omit the "
                        "argument)" % snapshot_arg)
            return errs, warns, notes

    byte_cache = {}
    for i, rec in enumerate(refs, 1):
        fid = art.fid_key(rec.get("id")) or "refutation block #%d" % i
        # --- resolve the snapshot this record binds ---
        if explicit is not None:
            target = explicit
            sp = rec.get("snapshot_path")
            if isinstance(sp, str) and os.path.basename(sp) != os.path.basename(explicit):
                errs.append("%s: record snapshot_path names %r but the run's snapshot is %r "
                            "— the record was written against a different draft" %
                            (fid, sp, os.path.basename(explicit)))
                continue
        else:
            target, refusal = _resolve_snapshot(record_dir, rec.get("snapshot_path"))
            if refusal:
                errs.append("%s: %s" % (fid, refusal))
                continue
        if not os.path.isfile(target):
            if required:
                errs.append("%s: manuscript snapshot missing (%s) — core-de/full-de runs "
                            "persist the intake snapshot (run-core.md §Intake Protocol); a "
                            "missing snapshot here is a broken intake, not a degrade case" %
                            (fid, os.path.basename(str(target))))
            else:
                warns.append("%s: manuscript snapshot missing (%s) — counter-evidence quotes "
                             "are unverifiable, so every demotion in this record is VOID: "
                             "outcomes weakened/refuted may NOT be transcribed into the "
                             "ledger (confidence stays unchanged), and the letter must carry "
                             "the disclosure line \"%s\"" %
                             (fid, os.path.basename(str(target)), PINNED_DISCLOSURE))
                if rec.get("outcome") in OUTCOME_CAPS:
                    notes.append("%s: demotion (%s) withheld — unverified without the "
                                 "snapshot" % (fid, rec.get("outcome")))
            continue
        if target not in byte_cache:
            byte_cache[target] = _read_bytes(target)
        raw = byte_cache[target]
        if raw is None:
            errs.append("%s: snapshot %s exists but cannot be read" % (fid, os.path.basename(target)))
            continue
        # --- record-vs-snapshot identity: as-is bytes, hashed ---
        digest = hashlib.sha256(raw).hexdigest()
        if digest != rec.get("snapshot_sha256"):
            errs.append("%s: snapshot_sha256 mismatch — record %s… vs on-disk %s… — the "
                        "record was written against different bytes; re-run the Step 6b "
                        "pass against the current snapshot" %
                        (fid, str(rec.get("snapshot_sha256"))[:12], digest[:12]))
            continue
        text = raw.decode("utf-8", errors="replace")
        # --- verbatim, single-line quotes (count >= 1; uniqueness deliberately dropped) ---
        for j, q in enumerate(rec.get("counter_evidence_quotes") or [], 1):
            where = "%s quote #%d" % (fid, j)
            if not isinstance(q, str) or not q.strip():
                errs.append("%s: empty or non-string — a counter-evidence quote is verbatim "
                            "manuscript bytes" % where)
                continue
            if "\n" in q or "\r" in q:
                errs.append("%s: multi-line — quotes are single-line snapshot substrings "
                            "(the A6 locator semantics; quote the single most diagnostic "
                            "line)" % where)
                continue
            if text.count(q) < 1:
                errs.append("%s: not found verbatim in the snapshot — a fabricated quote "
                            "voids the attempt (you cannot claim an attempt without "
                            "touching real text): %r" % (where, _short(q, 80)))
                continue
            if len(q.split()) > QUOTE_WORD_BUDGET:
                warns.append("%s: %d words exceeds the %d-word quote budget "
                             "(output-policy.md §Output Constraints) — trim to the "
                             "diagnostic core" % (where, len(q.split()), QUOTE_WORD_BUDGET))
        # --- §6.4 grounding floor for alternatives ---
        for j, a in enumerate(rec.get("alternative_explanations") or [], 1):
            if not isinstance(a, str):
                errs.append("%s alternative #%d: not a string" % (fid, j))
                continue
            if not (_QUOTE_MARK_RE.search(a) or _PAGE_LOCATOR_RE.search(a)
                    or art.chapter_token(a) or _CONTRACT_REF_RE.search(a)):
                warns.append("%s alternative #%d carries no quote mark, Ch./p. locator, or "
                             "contract reference — each rival reading must point at text or "
                             "a contract/intent statement (§6.4 grounding floor): %r"
                             % (fid, j, _short(a, 80)))
    return errs, warns, notes


# ------------------------------------------------------------------ V3 write-scope

def _severity_channel_errors(obj, where, severity_tokens):
    """Recursive banned-key/banned-value walk: a `severity` key at any depth, or any string
    value exactly equal to a canonical severity token, is a severity channel in a record
    that must not have one."""
    errs = []

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                kpath = "%s.%s" % (path, k)
                if isinstance(k, str) and k.lower() == "severity":
                    errs.append("%s: severity key at %s — the refutation record has no "
                                "severity channel by design; severity stays with the "
                                "Deficit Lock" % (where, kpath))
                walk(v, kpath)
        elif isinstance(node, list):
            for idx, v in enumerate(node):
                walk(v, "%s[%d]" % (path, idx))
        elif isinstance(node, str) and node in severity_tokens:
            errs.append("%s: canonical severity token %r used as a field value at %s — the "
                        "record may not carry severity in any channel" % (where, node, path))

    walk(obj, "$")
    return errs


def refutation_write_scope(ledger_text, record_text, record_dir):
    """V3 — no severity channel in the record; exact confidence transcription.
    Returns (errs, warns, notes)."""
    errs, warns, notes = [], [], []
    (refs, budgets), shape_errs = parse_record(record_text)
    errs.extend(shape_errs)
    severity_tokens = set(art.load_severity_values())

    # Severity-channel scan runs on EVERY parsed refutation/budget dict — including
    # schema-invalid ones (an invalid block must not dodge the severity kill), so re-parse
    # the raw blocks rather than only the schema-clean lists.
    n = 0
    for btype, obj, jerr in art.parse_blocks(record_text or ""):
        if btype not in ("refutation", "refutation_budget") or jerr or not isinstance(obj, dict):
            continue
        n += 1
        errs.extend(_severity_channel_errors(obj, "%s block #%d" % (btype, n), severity_tokens))

    # Confidence transcription: ledger confidence == record confidence_after, per the
    # outcome caps table. Voided records (snapshot missing beside the record — the V2
    # no-flag degrade) skip the equality assertion: the withheld demotion IS the correct
    # ledger state. Caps on confidence_after itself always apply.
    ledger_conf = {}
    for f in _locked_findings(ledger_text):
        fid = art.fid_key(f.get("id"))
        if fid is not None:
            ledger_conf[fid] = f.get("confidence")
    for rec in refs:
        fid = art.fid_key(rec.get("id"))
        outcome = rec.get("outcome")
        ca = rec.get("confidence_after")
        if outcome in OUTCOME_CAPS and ca not in OUTCOME_CAPS[outcome]:
            errs.append("%s: outcome %r caps confidence_after at %s — record says %r "
                        "(§7 caps table)" % (fid, outcome,
                                             "/".join(OUTCOME_CAPS[outcome]), ca))
        if fid not in ledger_conf:
            continue  # dangling — refutation-coverage owns that ERROR
        target, refusal = _resolve_snapshot(record_dir, rec.get("snapshot_path"))
        if refusal:
            errs.append("%s: %s" % (fid, refusal))
            continue
        void = not os.path.isfile(target)
        if void:
            notes.append("%s: snapshot missing beside the record — V2-voided; the "
                         "confidence_after-equality assertion is skipped (the withheld "
                         "demotion is the correct ledger state)" % fid)
            continue
        if ledger_conf[fid] != ca:
            errs.append("%s: transcription mismatch — ledger confidence %r != record "
                        "confidence_after %r; the synthesis agent transcribes "
                        "confidence_after into the locked ledger block per the §7 caps "
                        "table before Step 7 (run-synthesis.md §6b), and %s" %
                        (fid, ledger_conf[fid], ca,
                         "survival never raises confidence" if outcome == "survived"
                         else "a demotion must actually land in the ledger"))
    return errs, warns, notes


# ------------------------------------------------------------------ report / CLI

def report(errs, warns, notes, label):
    for nline in notes:
        print("NOTE: %s" % nline)
    for w in warns:
        print("WARN: %s" % w)
    for e in errs:
        print("ERROR: %s" % e)
    if errs:
        print("%s: FAIL (%d error(s), %d warning(s))" % (label, len(errs), len(warns)))
        return 1
    print("%s: PASS%s" % (label, (" (%d warning(s))" % len(warns)) if warns else ""))
    return 0


def _read_file(path, what):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read(), None
    except (OSError, UnicodeDecodeError) as exc:
        return None, "cannot read %s %s: %s" % (what, path, exc)


# ------------------------------------------------------------------ self-test

def run_self_test():
    import shutil
    import tempfile
    rc = {"v": 0}

    def check(name, cond, detail=""):
        print("  %s: %s" % (name, "OK" if cond else "FAIL%s" % ((" (%s)" % detail) if detail else "")))
        if not cond:
            rc["v"] = 1

    # non-UTF8 artifact on the refutation-coverage CLI read path must degrade to the
    # named cannot-read usage-error exit (2), never a raw UnicodeDecodeError traceback
    # (the disposition_check adjacent-exception class, swept repo-wide)
    _nud = tempfile.mkdtemp()
    try:
        _nu = os.path.join(_nud, "letter.md")
        _ok = os.path.join(_nud, "ok.md")
        with open(_nu, "wb") as _fh:
            _fh.write(b"\xff\xfenot utf-8\xff")
        with open(_ok, "w", encoding="utf-8") as _fh:
            _fh.write("# ok\n")
        check("non_utf8_read_file_named_error",
              _read_file(_nu, "editorial letter")[0] is None
              and "cannot read editorial letter" in (_read_file(_nu, "editorial letter")[1] or ""))
        check("non_utf8_coverage_cli_degrades",
              main(["refutation_check.py", "refutation-coverage", _nu, _ok, _ok]) == 2)
    finally:
        shutil.rmtree(_nud)

    def finding(fid, sev="Must-Fix", conf="HIGH", mech="the want never costs her anything"):
        return ('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"%s",'
                '"mechanism":"%s","severity":"%s","confidence":"%s",'
                '"evidence_refs":["Ch. 3"],"fix_class":"x","risk_if_fixed":"y"}\n-->' %
                (fid, mech, sev, conf))

    SNAP = ("# Snapshot\n\nChapter 3\n\n"
            "For a moment she almost chooses the orchard over the debt.\n"
            "Then she folded the thought away and said nothing.\n")
    snap_sha = hashlib.sha256(SNAP.encode("utf-8")).hexdigest()
    QUOTE = "For a moment she almost chooses the orchard over the debt."
    ALT = "Restraint could be the design — Ch. 3 frames her caution as inheritance."

    def ref_block(fid="F-P5-01", outcome="survived", conf_after="HIGH", quotes=None,
                  alts=None, sha=None, snap_path="Snap_Manuscript_Snapshot_r1.md", extra=""):
        quotes = [QUOTE] if quotes is None else quotes
        alts = [ALT] if alts is None else alts
        import json as _json
        obj = ('{"schema":"apodictic.refutation.v1","id":"%s","attempted":true,'
               '"outcome":"%s",%s"counter_evidence_quotes":%s,"alternative_explanations":%s,'
               '"rationale":"A paid cost would have refuted this; none found.",'
               '"confidence_after":"%s","snapshot_path":"%s","snapshot_sha256":"%s"}' %
               (fid, outcome, extra, _json.dumps(quotes), _json.dumps(alts), conf_after,
                snap_path, sha or snap_sha))
        return "<!-- apodictic:refutation\n%s\n-->" % obj

    def budget_block(cap=15, eligible=1, processed=1, bound=False):
        return ('<!-- apodictic:refutation_budget\n{"schema":"apodictic.refutation_budget.v1",'
                '"cap":%d,"eligible":%d,"processed":%d,"bound":%s}\n-->' %
                (cap, eligible, processed, "true" if bound else "false"))

    LEDGER = "## Pass 5 — Ledger Entry\n### Notable Findings\n" + finding("F-P5-01") + "\n"
    LETTER = ("# Development Edit: Snap\n## What Needs Work\n"
              "The want never costs her anything (Ch. 3). <!-- finding: F-P5-01 -->\n"
              "## Appendix B: Severity Calibration\nF-P5-01 held.\n")
    RECORD = "# Refutation Record\n" + ref_block() + "\n" + budget_block() + "\n"

    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "Snap_Manuscript_Snapshot_r1.md"), "w",
                  encoding="utf-8", newline="") as fh:
            fh.write(SNAP)
        snap_file = os.path.join(tmp, "Snap_Manuscript_Snapshot_r1.md")

        # 1. valid record, survived HIGH Must-Fix -> all three arms PASS
        e1, w1, _ = refutation_coverage(LETTER, LEDGER, RECORD)
        check("v1_valid_survived_pass", not e1 and not w1, str(e1 + w1))
        e2, w2, _ = refutation_evidence(RECORD, tmp, snap_file, require_snapshot=True)
        check("v2_valid_survived_pass", not e2 and not w2, str(e2 + w2))
        e3, w3, _ = refutation_write_scope(LEDGER, RECORD, tmp)
        check("v3_valid_survived_pass", not e3 and not w3, str(e3 + w3))

        # 2. HIGH finding, no record, budget unbound -> V1 ERROR (the headline gate)
        led2 = LEDGER + finding("F-P5-02", sev="Should-Fix", mech="subplot stalls without payoff") + "\n"
        rec2 = "# Refutation Record\n" + ref_block() + "\n" + budget_block(eligible=2, processed=1) + "\n"
        e, _, _ = refutation_coverage(LETTER, led2, rec2)
        check("v1_high_no_record_unbound_errors",
              any("F-P5-02" in x and "no survived refutation record" in x for x in e), str(e))

        # 3. Cap-bound disclosure — recompute-not-trust (Codex P1, PR #161). A GENUINELY
        #    binding budget: 16 eligible (1 Must-Fix + 15 HIGH Should-Fix) > cap 15, 15
        #    processed in ledger order, marker on the one unprocessed HIGH -> PASS with
        #    note. Then the attacks, each a blocking ERROR: bound:true whose ledger
        #    recompute does NOT bind (naming the marker's finding); bound:false marker;
        #    fabricated eligible (the Codex repro shape — promoted from WARN); lowered
        #    cap; marker on a processed id.
        sf_ids = ["F-P8-%02d" % i for i in range(1, 16)]
        led_bound = LEDGER + "".join(
            finding(fid, sev="Should-Fix", mech="subplot %s stalls" % fid) + "\n" for fid in sf_ids)
        rec_bound = ("# Refutation Record\n" + ref_block() + "\n"
                     + "".join(ref_block(fid=fid) + "\n" for fid in sf_ids[:-1])
                     + budget_block(eligible=16, processed=15, bound=True) + "\n")
        let_bound = LETTER.replace("## Appendix B",
                                   "<!-- refutation: not-attempted-budget F-P8-15 -->\n## Appendix B")
        e, w, notes = refutation_coverage(let_bound, led_bound, rec_bound)
        check("v1_bound_marker_honored", not e and any("F-P8-15" in x for x in notes), str(e + w))
        # bound:true the ledger recompute does not corroborate (2 eligible <= cap 15) —
        # the fabricated-exemption keystone: the marker must ERROR naming the finding.
        rec3 = "# Refutation Record\n" + ref_block() + "\n" + budget_block(eligible=2, processed=1, bound=True) + "\n"
        let3 = LETTER.replace("## Appendix B",
                              "<!-- refutation: not-attempted-budget F-P5-02 -->\n## Appendix B")
        e, _, _ = refutation_coverage(let3, led2, rec3)
        check("v1_marker_fake_bound_errors",
              any("F-P5-02" in x and "does NOT bind" in x for x in e)
              and any("claim the ledger must corroborate" in x for x in e), str(e))
        e, _, _ = refutation_coverage(let3, led2, rec2)  # same marker, bound:false
        check("v1_marker_unbound_budget_errors", any("unbound budget" in x for x in e), str(e))
        # fabricated eligible (the Codex repro shape): 16/15/bound:true claimed on a
        # 2-finding ledger -> blocking ERROR, not the old advisory WARN.
        rec3f = ("# Refutation Record\n" + ref_block() + "\n"
                 + budget_block(eligible=16, processed=15, bound=True) + "\n")
        e, w, _ = refutation_coverage(let3, led2, rec3f)
        check("v1_fabricated_eligible_errors",
              any("eligible is derived from the lock" in x for x in e) and not w, str(e + w))
        # lowered cap: cap is the §5 spec constant, not a knob a record can turn.
        rec3c = ("# Refutation Record\n" + ref_block() + "\n"
                 + budget_block(cap=1, eligible=2, processed=1, bound=True) + "\n")
        e, _, _ = refutation_coverage(let3, led2, rec3c)
        check("v1_lowered_cap_errors", any("not a per-run knob" in x for x in e), str(e))
        let3p = LETTER.replace("## Appendix B",
                               "<!-- refutation: not-attempted-budget F-P5-01 -->\n## Appendix B")
        e, _, _ = refutation_coverage(let3p, LEDGER, RECORD)
        check("v1_marker_on_processed_errors", any("HAS a refutation record" in x for x in e), str(e))
        # marker quoted in a code span is a documentation example, not a live disclosure
        let3c = LETTER.replace("## Appendix B",
                               "`<!-- refutation: not-attempted-budget F-P8-15 -->`\n## Appendix B")
        e, _, _ = refutation_coverage(let3c, led_bound, rec_bound)
        check("v1_marker_codespan_decoy_rejected",
              any("F-P8-15" in x and "no survived refutation record" in x for x in e), str(e))
        # boundary: a marker for F-P8-151 must not disclose F-P8-15 — and under a genuinely
        # bound budget an unknown marked id is a phantom disclosure
        let3b = LETTER.replace("## Appendix B",
                               "<!-- refutation: not-attempted-budget F-P8-151 -->\n## Appendix B")
        e, _, _ = refutation_coverage(let3b, led_bound, rec_bound)
        check("v1_marker_id_boundary",
              any("F-P8-15" in x and "no survived" in x for x in e)
              and any("phantom" in x for x in e), str(e))

        # 4. empty quotes / empty alternatives -> V2 ERROR (attempt void; schema minItems)
        rec4a = "# R\n" + ref_block(quotes=[]) + "\n" + budget_block() + "\n"
        e, _, _ = refutation_evidence(rec4a, tmp, snap_file)
        check("v2_empty_quotes_errors", any("counter_evidence_quotes" in x for x in e), str(e))
        rec4b = "# R\n" + ref_block(alts=[]) + "\n" + budget_block() + "\n"
        e, _, _ = refutation_evidence(rec4b, tmp, snap_file)
        check("v2_empty_alternatives_errors", any("alternative_explanations" in x for x in e), str(e))

        # 5. fabricated / multi-line / over-budget / sha-mismatch / snapshot handling
        e, _, _ = refutation_evidence("# R\n" + ref_block(quotes=["This sentence is not in the snapshot."])
                                      + "\n" + budget_block() + "\n", tmp, snap_file)
        check("v2_fabricated_quote_errors", any("not found verbatim" in x for x in e), str(e))
        e, _, _ = refutation_evidence("# R\n" + ref_block(quotes=["line one\nline two"])
                                      + "\n" + budget_block() + "\n", tmp, snap_file)
        check("v2_multiline_quote_errors", any("multi-line" in x for x in e), str(e))
        long_line = "word " * 29 + "end of the long snapshot line"
        snap_long = SNAP + long_line + "\n"
        with open(os.path.join(tmp, "Long_Manuscript_Snapshot_r1.md"), "w",
                  encoding="utf-8", newline="") as fh:
            fh.write(snap_long)
        sha_long = hashlib.sha256(snap_long.encode("utf-8")).hexdigest()
        rec5 = ("# R\n" + ref_block(quotes=[long_line], sha=sha_long,
                                    snap_path="Long_Manuscript_Snapshot_r1.md")
                + "\n" + budget_block() + "\n")
        e, w, _ = refutation_evidence(rec5, tmp, os.path.join(tmp, "Long_Manuscript_Snapshot_r1.md"))
        check("v2_long_quote_warns_not_errors", not e and any("word quote budget" in x or "quote budget" in x for x in w),
              str(e + w))
        e, _, _ = refutation_evidence("# R\n" + ref_block(sha="0" * 64) + "\n" + budget_block() + "\n",
                                      tmp, snap_file)
        check("v2_sha_mismatch_errors", any("snapshot_sha256 mismatch" in x for x in e), str(e))
        # missing snapshot: ERROR under --require-snapshot; WARN + void without it
        tmp2 = tempfile.mkdtemp()
        try:
            rec_void = ("# R\n" + ref_block(outcome="weakened", conf_after="MEDIUM")
                        + "\n" + budget_block() + "\n")
            e, _, _ = refutation_evidence(rec_void, tmp2, None, require_snapshot=True)
            check("v2_missing_snapshot_required_errors", any("broken intake" in x for x in e), str(e))
            e, w, notes = refutation_evidence(rec_void, tmp2, None)
            check("v2_missing_snapshot_warns_voids",
                  not e and any("VOID" in x and PINNED_DISCLOSURE in x for x in w)
                  and any("withheld" in x for x in notes), str(e + w))
            # ...and V3 skips the equality assertion for the voided record (ledger still HIGH)
            e, _, notes = refutation_write_scope(LEDGER, rec_void, tmp2)
            check("v3_void_skips_equality", not e and any("V2-voided" in x for x in notes), str(e))
            # run-shape detection: a Core_DE_Synthesis letter beside the record implies the flag
            with open(os.path.join(tmp2, "Proj_Core_DE_Synthesis_r1.md"), "w",
                      encoding="utf-8", newline="") as fh:
                fh.write("# letter\n")
            e, _, _ = refutation_evidence(rec_void, tmp2, None)
            check("v2_run_shape_implies_required", any("broken intake" in x for x in e), str(e))
        finally:
            shutil.rmtree(tmp2)
        # ungrounded alternative -> WARN
        e, w, _ = refutation_evidence("# R\n" + ref_block(alts=["could be intentional"])
                                      + "\n" + budget_block() + "\n", tmp, snap_file)
        check("v2_ungrounded_alternative_warns", not e and any("grounding floor" in x for x in w),
              str(e + w))
        # containment: absolute + escaping snapshot_path refused by name
        e, _, _ = refutation_evidence("# R\n" + ref_block(snap_path="/etc/hosts") + "\n"
                                      + budget_block() + "\n", tmp, None)
        check("v2_absolute_snapshot_path_refused", any("absolute" in x for x in e), str(e))
        e, _, _ = refutation_evidence("# R\n" + ref_block(snap_path="../outside.md") + "\n"
                                      + budget_block() + "\n", tmp, None)
        check("v2_escaping_snapshot_path_refused", any("containment" in x for x in e), str(e))
        # budget arithmetic
        e, _, _ = refutation_evidence("# R\n" + ref_block() + "\n"
                                      + budget_block(eligible=3, processed=1) + "\n", tmp, snap_file)
        check("v2_budget_processed_arithmetic_errors",
              any("processed" in x and "min(eligible, cap)" in x for x in e), str(e))
        e, _, _ = refutation_evidence("# R\n" + ref_block() + "\n"
                                      + budget_block(bound=True) + "\n", tmp, snap_file)
        check("v2_budget_bound_arithmetic_errors", any("bound" in x and "derived" in x for x in e), str(e))
        # processed must equal the actual schema-valid block count — a blocking ERROR
        # (promoted from WARN per the Codex P1: processed with no blocks behind it is
        # fabricated work), and the cap is the §5 spec constant, not a knob.
        e, w, _ = refutation_evidence("# R\n" + ref_block() + "\n"
                                      + budget_block(eligible=2, processed=2) + "\n", tmp, snap_file)
        check("v2_processed_count_mismatch_errors",
              any("schema-valid refutation block" in x for x in e) and not w, str(e + w))
        e, _, _ = refutation_evidence("# R\n" + ref_block() + "\n"
                                      + budget_block(cap=1, eligible=1, processed=1) + "\n", tmp, snap_file)
        check("v2_lowered_cap_errors", any("not a per-run knob" in x for x in e), str(e))
        # budget block missing / duplicated
        e, _, _ = refutation_evidence("# R\n" + ref_block() + "\n", tmp, snap_file)
        check("v2_missing_budget_block_errors", any("no apodictic.refutation_budget.v1" in x for x in e), str(e))
        e, _, _ = refutation_evidence("# R\n" + ref_block() + "\n" + budget_block() + "\n"
                                      + budget_block() + "\n", tmp, snap_file)
        check("v2_duplicate_budget_block_errors", any("exactly one budget block" in x for x in e), str(e))

        # 6. severity channel in a refutation block -> V3 ERROR
        rec6 = ("# R\n" + ref_block(extra='"severity":"Should-Fix",') + "\n" + budget_block() + "\n")
        e, _, _ = refutation_write_scope(LEDGER, rec6, tmp)
        check("v3_severity_key_errors", any("severity key" in x for x in e), str(e))
        rec6b = ("# R\n" + ref_block(extra='"note":"Must-Fix",') + "\n" + budget_block() + "\n")
        e, _, _ = refutation_write_scope(LEDGER, rec6b, tmp)
        check("v3_severity_token_value_errors",
              any("used as a field value" in x for x in e), str(e))

        # 7. transcription miss / cap violation -> V3 ERROR
        rec7 = ("# R\n" + ref_block(outcome="weakened", conf_after="MEDIUM") + "\n"
                + budget_block() + "\n")
        e, _, _ = refutation_write_scope(LEDGER, rec7, tmp)  # ledger still HIGH
        check("v3_transcription_miss_errors", any("transcription mismatch" in x for x in e), str(e))
        rec7b = ("# R\n" + ref_block(outcome="refuted", conf_after="HIGH") + "\n"
                 + budget_block() + "\n")
        e, _, _ = refutation_write_scope(LEDGER, rec7b, tmp)
        check("v3_cap_violation_errors", any("caps confidence_after" in x for x in e), str(e))
        # survived must EQUAL the ledger (never confidence-raising): ledger MEDIUM, record HIGH
        led7 = "## Ledger\n" + finding("F-P5-01", conf="MEDIUM") + "\n"
        e, _, _ = refutation_write_scope(led7, RECORD, tmp)
        check("v3_survived_never_raises", any("transcription mismatch" in x for x in e), str(e))
        # V1 also refuses the untranscribed HIGH (outcome != survived at HIGH)
        e, _, _ = refutation_coverage(LETTER, LEDGER, rec7)
        check("v1_high_with_nonsurvived_record_errors",
              any("HIGH requires a survived attempt" in x for x in e), str(e))

        # 8. dangling record id -> V1 ERROR; non-dict payload -> clean named error, no crash
        rec8 = RECORD + ref_block(fid="F-ZZ-09") + "\n"
        e, _, _ = refutation_coverage(LETTER, LEDGER, rec8.replace(budget_block(), budget_block(eligible=1, processed=1)))
        check("v1_dangling_record_errors", any("dangling refutation record id F-ZZ-09" in x for x in e), str(e))
        # a record on a non-locked (Could-Fix) finding is out of scope
        led8 = LEDGER + finding("F-P5-03", sev="Could-Fix", conf="LOW", mech="a polish nit") + "\n"
        e, _, _ = refutation_coverage(LETTER, led8, RECORD + ref_block(fid="F-P5-03") + "\n")
        check("v1_could_fix_record_errors", any("not synthesis-bound" in x for x in e), str(e))
        (r_ok, b_ok), errs8 = parse_record("<!-- apodictic:refutation\n42\n-->")
        check("nondict_payload_named_error",
              not r_ok and any("not a JSON object" in x for x in errs8), str(errs8))
        (r_ok, b_ok), errs8b = parse_record('<!-- apodictic:refutation\n{"schema":"apodictic.refutation.v1"\n-->')
        check("broken_carrier_named_error", not r_ok and any("invalid JSON" in x for x in errs8b), str(errs8b))
        # attempted:false is a recorded skip, not an attempt
        rec8c = RECORD.replace('"attempted":true', '"attempted":false')
        e, _, _ = refutation_coverage(LETTER, LEDGER, rec8c)
        check("v1_attempted_false_errors", any("attempted: false" in x for x in e), str(e))
        # duplicate refutation blocks for one id
        e, _, _ = refutation_coverage(LETTER, LEDGER, RECORD + ref_block() + "\n")
        check("v1_duplicate_record_errors", any("duplicate refutation block" in x for x in e), str(e))
        # disposition-exempt finding: declined Must-Fix without a record passes with a note
        led9 = LEDGER + "\n<!-- declined: F-P5-01 — the author already ruled -->\n"
        e, _, notes = refutation_coverage(LETTER, led9, "# R\n" + budget_block(eligible=0, processed=0) + "\n")
        check("v1_disposition_exempts", not e and any("exempt" in x for x in notes), str(e))
    finally:
        shutil.rmtree(tmp)

    print("Self-test: %s" % ("PASS" if rc["v"] == 0 else "FAIL"))
    return rc["v"]


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "--self-test":
        return run_self_test()
    if cmd == "refutation-coverage":
        if len(argv) < 5:
            print("Usage: refutation_check.py refutation-coverage <editorial_letter> "
                  "<findings_ledger> <refutation_record>")
            return 2
        texts = []
        for path, what in ((argv[2], "editorial letter"), (argv[3], "findings ledger"),
                           (argv[4], "refutation record")):
            text, err = _read_file(path, what)
            if err:
                print("Error: %s" % err)
                return 2
            texts.append(text)
        return report(*refutation_coverage(*texts), label="refutation-coverage")
    if cmd == "refutation-evidence":
        args = [a for a in argv[2:] if a != "--require-snapshot"]
        require = "--require-snapshot" in argv[2:]
        if len(args) < 1:
            print("Usage: refutation_check.py refutation-evidence <refutation_record> "
                  "[<manuscript_snapshot>] [--require-snapshot]")
            return 2
        record_text, err = _read_file(args[0], "refutation record")
        if err:
            print("Error: %s" % err)
            return 2
        snapshot_arg = args[1] if len(args) > 1 else None
        record_dir = os.path.dirname(os.path.abspath(args[0]))
        return report(*refutation_evidence(record_text, record_dir, snapshot_arg, require),
                      label="refutation-evidence")
    if cmd == "refutation-write-scope":
        if len(argv) < 4:
            print("Usage: refutation_check.py refutation-write-scope <findings_ledger> "
                  "<refutation_record>")
            return 2
        ledger_text, err = _read_file(argv[2], "findings ledger")
        if err:
            print("Error: %s" % err)
            return 2
        record_text, err = _read_file(argv[3], "refutation record")
        if err:
            print("Error: %s" % err)
            return 2
        record_dir = os.path.dirname(os.path.abspath(argv[3]))
        return report(*refutation_write_scope(ledger_text, record_text, record_dir),
                      label="refutation-write-scope")
    print("Unknown command: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
