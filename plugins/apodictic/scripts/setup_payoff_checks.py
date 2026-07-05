#!/usr/bin/env python3
"""setup-payoff — referential completeness for the Setup–Payoff Ledger.

`validate.sh setup-payoff <run_folder|files>` shells out here. The Setup–Payoff Ledger is the
referential-completeness half of a developmental-edit style sheet: the mechanical home for the one
ConStory-Bench craft row APODICTIC otherwise has no surface for — "Abandoned Plot Elements",
introduced narrative expectations never resolved (setup without payoff). It records the
author-marked Foreshadow → Trigger → Payoff triples (Codified Foreshadowing-Payoff Text Generation,
Yun et al., arXiv:2601.07033 — F establishes a "causal debt", P fulfils the commitment; a debt left
unpaid is `abandoned`, the defect) and CHECKS every foreshadow resolves. Each foreshadow is an
apodictic.setup_payoff.v1 block; each resolving payoff an apodictic.payoff.v1 block; this validator
owns the Ledger's contract and its no-verdict boundary.

The module firewall is *extract the marked triple, never author the verdict*: the model authors the
EXTRACTION (marks F/T/P), the validator DERIVES the state deterministically and checks referential
completeness — it never DECIDES whether a given passage "counts" as a payoff (that semantic call is
the deferred SETEC-consumer job) and the Ledger carries NO editorial severity (X1). The three-state
axis (paid_off / open / abandoned) is a fact-state orthogonal to severity, mirroring the Continuity
Bible's contradiction axis and Content Advisory's descriptive stance.

  SP1 state present    a setup_payoff.v1 foreshadow block whose `state` is absent or not one of
                       {paid_off, open, abandoned} (also covers schema/JSON validity of both block
                       kinds, malformed SP-NN / PO-NN ids, missing required fields, duplicate ids,
                       and anchor locus shape — each `anchor` must be a coarse chapter / §section /
                       ¶ / line / page locus, not a blank or a prose description).
  SP2 referential      a non-empty `payoff_ref` that does not id-match an existing apodictic.payoff.v1
     integrity         block in the same run (a phantom ref). Forward integrity ONLY — N:1 allowed
                       (many foreshadows -> one payoff); a payoff with no foreshadow is NOT flagged
                       here (that inverse is the deferred Stage B). Resolved BEFORE the derivation.
  SP3 open rationale   an `open` state that carries no non-empty `open_rationale` (a deliberately
                       unresolved thread must say WHY it is deferred — else it is an abandoned defect
                       in disguise).
  SP4 derived state    the author-written `state` disagrees with the mechanically-derived state (the
                       §D4 truth table over the resolved refs). SP2 resolves payoff_ref first, so
                       `paid_off` presupposes a resolved payoff. NO model judgment in the gate.
  X1 firewall          the Ledger artifact carries an apodictic:finding block OR a Must/Should/
                       Could-Fix editorial-severity token — the Content-Advisory A3 firewall applied
                       here. The Ledger is a fact register, not a defect list; severity, if any, is
                       owned downstream by promise-contract (Stage B).

Derivation truth table (§D4 — the SINGLE source, `derive_state`):

  | payoff_ref                       | open_rationale | derived state |
  |----------------------------------|----------------|---------------|
  | non-empty AND resolves (SP2 ok)  | any            | paid_off      |
  | non-empty BUT phantom (SP2 FAIL) | any            | (SP2 error; state not derived) |
  | empty                            | non-empty      | open          |
  | empty                            | empty          | abandoned     |

Reuses apodictic_artifacts (block grammar + schema engine). The editorial letter cites the derived
`abandoned` rows by prose (Stage A wiring — the Legal-Risk / Content-Advisory precedent); no other
validator consumes the register. See docs/setup-payoff-ledger.md.

  setup_payoff_checks.py setup-payoff <run_folder|files...> [--strict]
  setup_payoff_checks.py --self-test

Exit: 0 clean, 1 ERROR, 2 usage.
"""
import glob
import os
import re
import sys
import tempfile

try:
    import apodictic_artifacts as art
except ImportError:
    art = None


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (a parsed carrier, not a prose mention).

    Classifying on parsed blocks — not a raw substring — keeps a file that merely *names* the marker
    in prose from being misrouted (the resolver-hardening convention; gated by M2)."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))


_SP_SCHEMA_ID = "apodictic.setup_payoff.v1"
_PO_SCHEMA_ID = "apodictic.payoff.v1"
_LEDGER_GLOB = "*_Setup_Payoff_Ledger_*.md"

# X1 firewall — the ledger is a fact register, not a defect list. Mirrors content_advisory._SEVERITY_RE
# (the A3 firewall applied here); an apodictic:finding block is caught by the parsed-block check, so a
# file that merely NAMES the token in prose still FAILs (severity must never leak into the register).
_SEVERITY_RE = re.compile(r"\b(?:Must|Should|Could)-Fix\b")

_VALID_STATES = ("paid_off", "open", "abandoned")

# SP1 anchor locus shape — each `anchor` entry must be a COARSE manuscript locus (a chapter /
# §section / ¶ / line / page / paragraph token), not a blank or a prose description. The schema only
# enforces minItems>=1 + string, so `[""]` / `["the kitchen"]` pass JSON validation; this precondition
# rejects them (the abandoned-row report cites anchor[0] as the prose locus, so a blank/non-locus
# anchor would emit an empty or meaningless citation). Mirrors continuity_bible._LOCUS_RE (C2). NOT a
# firewall proof — a well-shaped-but-fabricated locus ("Ch 9 ¶4") passes; resolution is deferred.
_LOCUS_RE = re.compile(
    r"\bch(?:apter)?\.?\s*\d+"          # Ch 9 / Chapter 9 / Ch. 9
    r"|§"                                # §section
    r"|¶"                                # ¶paragraph
    r"|\blines?\s+\d+"                   # line 42 / lines 42
    r"|\bp(?:g|ag\.?|\.)?\s*\d+"         # p. 40 / pg 40 / p40
    r"|\bpara(?:graph)?\.?\s*\d+",       # paragraph 4 / para. 4
    re.IGNORECASE)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _parse(text, schema_id, label):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic block of `schema_id`'s type."""
    out = []
    if not text or art is None:
        return out
    btype_wanted = schema_id.split(".")[1]  # "apodictic.setup_payoff.v1" -> "setup_payoff"
    schema = art.load_schema(schema_id)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != btype_wanted:
            continue
        idx += 1
        where = "%s #%d" % (label, idx)
        if jerr:
            out.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        out.append((obj, art.validate_obj(obj, schema, where), idx))
    return out


def parse_foreshadows(text):
    return _parse(text, _SP_SCHEMA_ID, "setup_payoff")


def parse_payoffs(text):
    return _parse(text, _PO_SCHEMA_ID, "payoff")


def derive_state(payoff_ref, open_rationale, payoff_ids):
    """The §D4 truth table — the SINGLE source of the derived state. Presupposes SP2 has already
    rejected a phantom ref (a non-empty ref that is NOT in `payoff_ids` returns None: derivation is
    not defined for an unresolved ref — SP2 owns that error, not D4)."""
    ref = (payoff_ref or "").strip()
    rationale = (open_rationale or "").strip()
    if ref:
        return "paid_off" if ref in payoff_ids else None  # None => phantom (SP2 error, not derivable)
    return "open" if rationale else "abandoned"


def ledger(text, strict=False):
    """Run the Setup–Payoff Ledger referential-completeness checks. Returns (code, lines)."""
    lines, errs = [], []
    foreshadows = parse_foreshadows(text)
    payoffs = parse_payoffs(text)
    if not foreshadows and not payoffs:
        return 0, ["setup-payoff: no setup_payoff or payoff blocks found — nothing to check"]

    # SP1 — schema / JSON validity + state presence (per block), for BOTH block kinds
    for _obj, schema_errs, _idx in foreshadows:
        for e in schema_errs:
            errs.append("SP1 schema: %s" % e)
    for _obj, schema_errs, _idx in payoffs:
        for e in schema_errs:
            errs.append("SP1 schema: %s" % e)

    valid_f = [(o, i) for o, se, i in foreshadows if o is not None and not se]
    valid_p = [(o, i) for o, se, i in payoffs if o is not None and not se]

    # Duplicate-id guards (ids must be unique within their kind)
    for kind, valid in (("SP", valid_f), ("PO", valid_p)):
        seen = {}
        for obj, idx in valid:
            seen.setdefault(obj.get("id"), []).append(idx)
        for cid, where in sorted(seen.items()):
            if len(where) > 1:
                errs.append("SP1 schema: %s appears %d times (ids must be unique)"
                            % (cid, len(where)))

    payoff_ids = {o.get("id") for o, _ in valid_p}

    # SP1 — anchor locus shape: each anchor entry is a coarse manuscript locus, not a blank or a
    # prose description (the schema allows `[""]` / `["the kitchen"]`; the abandoned-row report cites
    # anchor[0] as the prose locus). Applies to BOTH block kinds. Mirrors continuity_bible's C2.
    for _kind, valid in (("SP", valid_f), ("PO", valid_p)):
        for obj, _idx in valid:
            for locus in (obj.get("anchor") or []):
                if not isinstance(locus, str) or not locus.strip() or not _LOCUS_RE.search(locus):
                    errs.append("SP1 anchor locus: %s has a malformed / non-locus anchor entry %r "
                                "(need a chapter / §section / ¶ / line / page token)"
                                % (obj.get("id"), locus))

    # SP1 (state token) is enforced by the schema enum; a foreshadow that reached valid_f has a
    # state in the enum. (An absent/out-of-enum state is an SP1 schema error above.)

    for obj, _idx in valid_f:
        fid = obj.get("id")
        ref = (obj.get("payoff_ref") or "").strip()
        rationale = (obj.get("open_rationale") or "").strip()
        declared = obj.get("state")

        # SP2 — forward referential integrity (a non-empty ref must resolve; N:1 allowed)
        ref_ok = True
        if ref and ref not in payoff_ids:
            ref_ok = False
            errs.append("SP2 referential integrity: %s has payoff_ref %r that resolves to no "
                        "apodictic.payoff.v1 block (a phantom ref)" % (fid, ref))

        # SP3 — an `open` state must carry a non-empty rationale
        if declared == "open" and not rationale:
            errs.append("SP3 open rationale: %s is `open` but carries no non-empty open_rationale "
                        "(a deliberately unresolved thread must say why it is deferred)" % fid)

        # SP4 — the declared state must match the mechanically-derived state (§D4). Skip when SP2
        # already failed for this block (the ref is unresolved, so the state is not derivable — SP2
        # owns the error; deriving here would double-report a phantom ref as an SP4 mismatch).
        if ref_ok:
            derived = derive_state(ref, rationale, payoff_ids)
            if derived is not None and declared != derived:
                errs.append("SP4 derived state: %s declares state %r but the refs derive %r "
                            "(payoff_ref=%r, open_rationale=%s) — the register never overrides the "
                            "derivation" % (fid, declared, derived, ref,
                                            "set" if rationale else "empty"))

    # X1 — firewall: the ledger carries no editorial severity token / no finding block
    if _SEVERITY_RE.search(text or ""):
        errs.append("X1 firewall: the Setup–Payoff Ledger carries an editorial Must/Should/Could-Fix "
                    "token — the register is a fact list, not a defect list (severity is owned "
                    "downstream by promise-contract)")
    if _has_block(text, "finding"):
        errs.append("X1 firewall: the Setup–Payoff Ledger contains an apodictic:finding block — "
                    "the register must not carry findings")

    # Report
    lines.append("setup-payoff: %d foreshadow(s), %d payoff(s)%s" % (
        len(foreshadows), len(payoffs),
        "" if (len(valid_f) == len(foreshadows) and len(valid_p) == len(payoffs))
        else " (%d/%d well-formed)" % (len(valid_f) + len(valid_p),
                                       len(foreshadows) + len(payoffs))))
    abandoned = [(o.get("id"), o.get("foreshadow"), o.get("anchor"))
                 for o, _ in valid_f if o.get("state") == "abandoned"]
    for obj, _idx in valid_f:
        lines.append("  %-7s %-10s foreshadow=%s%s" % (
            obj.get("id"), obj.get("state"),
            (obj.get("foreshadow") or "")[:48],
            " -> %s" % obj.get("payoff_ref") if (obj.get("payoff_ref") or "").strip() else ""))
    for e in errs:
        lines.append("  ERROR: %s" % e)

    if errs:
        lines.append("setup-payoff: FAIL (%d error(s))" % len(errs))
        return 1, lines

    # Abandoned rollup — the derived-state pass emits the abandoned rows (id + short foreshadow) for
    # the editorial letter to cite in prose (Stage A wiring; formatted like continuity_bible's WARN
    # rollup). These are NOT errors — an abandoned setup is a surfaced fact, not a validation failure.
    if abandoned:
        lines.append("setup-payoff: %d abandoned setup(s) — cite in the editorial letter (prose):"
                     % len(abandoned))
        for aid, fore, anchor in abandoned:
            loc = anchor[0] if isinstance(anchor, list) and anchor else "?"
            lines.append("  ABANDONED %s (%s): %s" % (aid, loc, (fore or "")[:72]))
    else:
        lines.append("setup-payoff: PASS (SP1 schema + SP2 referential integrity + SP3 open "
                     "rationale + SP4 derived-state agreement + X1 firewall)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    """Return the Setup–Payoff Ledger path (a *_Setup_Payoff_Ledger_*.md in a run folder, or a file
    carrying setup_payoff/payoff blocks, or the first path)."""
    if len(paths) == 1 and os.path.isdir(paths[0]):
        return _newest(glob.glob(os.path.join(paths[0], _LEDGER_GLOB)))
    for p in paths:
        text = _read(p) or ""
        if _has_block(text, "setup_payoff") or _has_block(text, "payoff"):
            return p
    return paths[0] if paths else None


def run(paths, strict=False):
    ledger_path = resolve(paths)
    if not ledger_path:
        return 2, ["setup-payoff: no Setup–Payoff Ledger artifact found (need a "
                   "*_Setup_Payoff_Ledger_*.md or a file with apodictic:setup_payoff/payoff blocks)"]
    text = _read(ledger_path)
    if text is None:
        return 2, ["setup-payoff: cannot read %s" % ledger_path]
    return ledger(text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    # non-UTF8 artifact: _read must degrade to None, never a traceback (the repo-wide read class)
    import tempfile as _tf
    _fd, _nu = _tf.mkstemp(suffix=".md")
    with os.fdopen(_fd, "wb") as _fh:
        _fh.write(b"\xff\xfenot utf-8\xff")
    chk("non_utf8_read_returns_none", _read(_nu) is None)
    os.unlink(_nu)

    def fore(sid, foreshadow="A gun is planted on the mantel", anchor=("Ch 1 §2",),
             trigger=None, payoff_ref="", state="abandoned", open_rationale=None):
        obj = {"schema": _SP_SCHEMA_ID, "id": sid, "foreshadow": foreshadow,
               "anchor": list(anchor), "payoff_ref": payoff_ref, "state": state}
        if trigger is not None:
            obj["trigger"] = trigger
        if open_rationale is not None:
            obj["open_rationale"] = open_rationale
        return "<!-- apodictic:setup_payoff\n%s\n-->" % _j.dumps(obj)

    def payoff(pid, text="The gun is fired in the climax", anchor=("Ch 9 ¶4",)):
        obj = {"schema": _PO_SCHEMA_ID, "id": pid, "payoff": text, "anchor": list(anchor)}
        return "<!-- apodictic:payoff\n%s\n-->" % _j.dumps(obj)

    # derive_state — the §D4 truth table (the single derivation source)
    chk("d4_paid_off", derive_state("PO-01", None, {"PO-01"}) == "paid_off")
    chk("d4_phantom_none", derive_state("PO-09", None, {"PO-01"}) is None)
    chk("d4_open", derive_state("", "series thread", set()) == "open")
    chk("d4_abandoned", derive_state("", "", set()) == "abandoned")

    # clean: one paid_off (resolves), one open (rationaled), one abandoned
    clean = "\n".join([
        payoff("PO-03"),
        fore("SP-01", state="paid_off", payoff_ref="PO-03"),
        fore("SP-02", state="open", payoff_ref="",
             open_rationale="a sequel hook — the prophecy resolves in Book 2"),
        fore("SP-03", state="abandoned", payoff_ref="",
             foreshadow="a locket is described in loving detail, then never mentioned again"),
    ])
    code, lines = ledger(clean)
    chk("clean_passes", code == 0)
    chk("clean_reports_abandoned",
        any("ABANDONED SP-03" in ln for ln in lines))

    # N:1 — two foreshadows resolving to one payoff is allowed
    n1 = "\n".join([payoff("PO-05"),
                    fore("SP-01", state="paid_off", payoff_ref="PO-05"),
                    fore("SP-02", state="paid_off", payoff_ref="PO-05")])
    chk("n_to_1_allowed", ledger(n1)[0] == 0)

    # SP1 — schema: bad SP id, bad PO id, missing field, bad state enum, duplicate id, bad JSON
    chk("sp1_bad_sp_id", ledger(fore("SP-1", state="abandoned"))[0] == 1)
    chk("sp1_bad_po_id", ledger(payoff("PO-1"))[0] == 1)
    chk("sp1_missing_field",
        ledger(fore("SP-01").replace('"foreshadow"', '"fore"'))[0] == 1)
    code, lines = ledger(fore("SP-01", state="resolved"))  # not in enum
    chk("sp1_bad_state_enum", code == 1 and any("SP1 schema" in ln for ln in lines))
    code, lines = ledger(fore("SP-01", state="abandoned") + "\n" +
                         fore("SP-01", state="abandoned", foreshadow="another"))
    chk("sp1_duplicate_id", code == 1 and any("appears 2 times" in ln for ln in lines))
    code, lines = ledger('<!-- apodictic:setup_payoff\n{"schema":"apodictic.setup_payoff.v1"\n-->')
    chk("sp1_bad_json", code == 1 and any("SP1 schema" in ln for ln in lines))
    # closed-key: an unknown field is rejected (additionalProperties:false)
    code, lines = ledger(fore("SP-01", state="abandoned").replace(
        '"state": "abandoned"', '"state": "abandoned", "severty": "Must-Fix"'))
    chk("sp1_closed_key_rejects_unknown", code == 1 and any("SP1 schema" in ln for ln in lines))
    # payoff closed-key
    code, lines = ledger(payoff("PO-01").replace('"payoff":', '"stray": "x", "payoff":'))
    chk("po_closed_key_rejects_unknown", code == 1 and any("SP1 schema" in ln for ln in lines))
    # empty anchor -> minItems fail
    chk("sp1_empty_anchor", ledger(fore("SP-01", state="abandoned", anchor=[]))[0] == 1)
    # anchor locus shape: a BLANK or a PROSE (non-locus) anchor FAILs even though the schema
    # (minItems>=1 + string) accepts them — the abandoned-row citation uses anchor[0] as the locus
    code, lines = ledger(fore("SP-01", state="abandoned", anchor=[""]))
    chk("sp1_blank_anchor_locus", code == 1 and any("SP1 anchor locus" in ln for ln in lines))
    code, lines = ledger(fore("SP-01", state="abandoned", anchor=["the kitchen"]))
    chk("sp1_nonlocus_anchor", code == 1 and any("SP1 anchor locus" in ln for ln in lines))
    # a payoff block's anchor is validated too (both kinds carry a locus)
    code, lines = ledger(payoff("PO-01", anchor=["nowhere in particular"]))
    chk("po_nonlocus_anchor", code == 1 and any("SP1 anchor locus" in ln for ln in lines))
    # a well-shaped locus passes (the report cites it cleanly)
    chk("sp1_valid_locus_passes",
        ledger(fore("SP-01", state="abandoned", anchor=["Ch 3 ¶2"]))[0] == 0)

    # SP2 — HOSTILE: a paid_off with a phantom payoff_ref FAILs
    code, lines = ledger(fore("SP-02", state="paid_off", payoff_ref="PO-09"))
    chk("sp2_phantom_ref_fails",
        code == 1 and any("SP2 referential integrity" in ln for ln in lines))

    # SP3 — HOSTILE: an open state with no rationale FAILs
    code, lines = ledger(fore("SP-04", state="open", payoff_ref="", open_rationale=""))
    chk("sp3_open_no_rationale_fails",
        code == 1 and any("SP3 open rationale" in ln for ln in lines))
    # open with a whitespace-only rationale also FAILs (stripped)
    chk("sp3_open_whitespace_rationale_fails",
        ledger(fore("SP-05", state="open", open_rationale="   "))[0] == 1)

    # SP4 — HOSTILE: a declared paid_off with no ref FAILs (derives abandoned, not paid_off)
    code, lines = ledger(fore("SP-06", state="paid_off", payoff_ref=""))
    chk("sp4_paid_off_no_ref_fails",
        code == 1 and any("SP4 derived state" in ln for ln in lines))
    # SP4 — a declared abandoned that actually resolves (has a real ref) FAILs (derives paid_off)
    code, lines = ledger(payoff("PO-07") + "\n" +
                         fore("SP-07", state="abandoned", payoff_ref="PO-07"))
    chk("sp4_abandoned_but_resolves_fails",
        code == 1 and any("SP4 derived state" in ln for ln in lines))
    # SP4 — a declared open with a resolving ref FAILs (derives paid_off)
    code, lines = ledger(payoff("PO-08") + "\n" +
                         fore("SP-08", state="open", payoff_ref="PO-08",
                              open_rationale="claims deferred but a payoff resolves it"))
    chk("sp4_open_but_resolves_fails",
        code == 1 and any("SP4 derived state" in ln for ln in lines))
    # SP2 owns a phantom ref: a paid_off with a phantom ref reports SP2, NOT a double SP4 mismatch
    code, lines = ledger(fore("SP-09", state="paid_off", payoff_ref="PO-99"))
    chk("sp2_owns_phantom_no_double_sp4",
        code == 1 and any("SP2" in ln for ln in lines)
        and not any("SP4" in ln for ln in lines))

    # X1 — HOSTILE: a planted Must-Fix token FAILs (severity leak)
    code, lines = ledger(clean + "\n\n## Notes\n\n- SP-03 is a Must-Fix.\n")
    chk("x1_severity_token_fails",
        code == 1 and any("X1 firewall" in ln for ln in lines))
    # X1 — a planted apodictic:finding block FAILs
    finding = ('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"F-P5-01",'
               '"mechanism":"m","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["c"],'
               '"fix_class":"x","risk_if_fixed":"y"}\n-->')
    code, lines = ledger(clean + "\n" + finding)
    chk("x1_finding_block_fails",
        code == 1 and any("apodictic:finding block" in ln for ln in lines))

    # trigger is recorded, not gated: a foreshadow with a trigger is no different for completeness
    chk("trigger_recorded_not_gated",
        ledger(fore("SP-01", state="abandoned", trigger="when the heir returns"))[0] == 0)

    # no blocks -> no-op
    chk("no_blocks_noop", ledger("# Notes\nnothing structured\n")[0] == 0)

    # run-folder + explicit-file resolution
    import shutil
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "Proj_Setup_Payoff_Ledger_run.md")
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Setup-Payoff Ledger\n" + clean + "\n")
        chk("run_folder_resolution", run([d])[0] == 0)
        chk("explicit_file_resolution", run([p])[0] == 0)
        chk("missing_artifact_usage", run([os.path.join(d, "nope.md")])[0] == 2)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "setup-payoff"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: setup_payoff_checks.py setup-payoff <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
