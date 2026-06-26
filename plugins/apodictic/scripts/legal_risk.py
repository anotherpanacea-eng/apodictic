#!/usr/bin/env python3
"""legal-risk — structural integrity for the Legal Risk Register workflow (Workflows).

`validate.sh legal-risk <run_folder|files>` shells out here. For memoir / autofiction / nonfiction
with identifiable real people, the register FLAGS areas that may warrant legal review — defamation,
privacy/disclosure, rights-clearance — with a legal-escalation severity and an escalation trigger.
It is NOT legal advice and never adjudicates: the module firewall is *flag, don't practice law*.
Each flag is an apodictic.legal_risk.v1 block; this validator owns the register's contract and
mechanizes the firewall.

  L1 invalid item     a legal_risk block fails its schema (bad risk_class/severity enum, malformed
                      LR-NN id, missing required field, broken JSON).
  L2 duplicate id     two items share an LR-NN id.
  L3 missing disclaimer  the register carries legal_risk items but no not-a-lawyer / not-legal-advice
                      disclaimer in READER-FACING prose (HTML comments and the legal_risk blocks are
                      stripped first, so an impl note can't satisfy it). The signature gate — the
                      register must never read as legal advice.
  W1 legal-advice drift  a `concern`/`disposition` states a legal CONCLUSION ("not defamatory",
                      "protected by", "is fair use", "no liability", "can't be sued", "is legal")
                      rather than flagging for review (advisory; ERROR --strict). The module firewall.
                      Override (per id): <!-- override: legal-advice-drift LR-NN — <rationale> -->.
  W2 unrouted high risk  a `review-now` item whose `disposition` does not route to legal review /
                      counsel (advisory; ERROR --strict) — a top-tier flag must point to a lawyer.

`severity` is a legal-escalation tier (monitor / review-recommended / review-now), orthogonal to the
editorial Must/Should/Could scale. Reuses apodictic_artifacts (block grammar + schema engine). Each
artifact is optional; an empty/absent one is a no-op. See docs/legal-risk-register.md.

  legal_risk.py legal-risk <run_folder|files...> [--strict]
  legal_risk.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import os
import re
import sys

from override_marker import override_targets  # SSoT: code-span-stripped, boundary-matched override scan

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

_SCHEMA_ID = "apodictic.legal_risk.v1"
_REGISTER_GLOB = "*_Legal_Risk_Register_*.md"

# L3 — the register must carry a not-a-lawyer / not-legal-advice disclaimer in READER-FACING prose.
_DISCLAIMER_RE = re.compile(r"not\s+a\s+lawyer|not\s+legal\s+advice", re.IGNORECASE)
# HTML comments (incl. the apodictic:legal_risk blocks, which ARE <!-- … --> comments) are stripped
# before the L3 search, so an implementation note or block text cannot satisfy the disclaimer gate.
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# Override markers naming an item id ("<!-- override: legal-advice-drift LR-01 — ... -->") route
# through the shared override_marker SSoT — code spans stripped, slug boundary-matched.
# W1 — legal CONCLUSION language (the module flags; it does not adjudicate). Kept specific so an
# advisory rarely misfires; an intended phrasing is silenced per-id by the override marker.
_ADVICE_RE = re.compile(
    r"\bnot\s+(?:defamatory|libel(?:ous|lous)?|actionable)\b"
    r"|\bno\s+(?:defamation|libel|liability|cause\s+of\s+action|legal\s+(?:risk|exposure|liability))\b"
    r"|\b(?:is|are|constitutes?|qualifies\s+as|counts\s+as|covered\s+by)\s+fair\s+use\b"
    r"|\bprotected\s+by\b"
    r"|\b(?:can(?:not|'t)?|cannot|won'?t|will\s+not)\s+be\s+sued\b"
    r"|\bnot\s+be\s+sued\b"
    r"|\b(?:is|it'?s)\s+(?:legal|illegal|lawful|unlawful|defensible|privileged)\b",
    re.IGNORECASE)
# W2 — a review-now disposition must route to a lawyer / legal review.
_ROUTING_RE = re.compile(r"legal|lawyer|counsel|attorney|review", re.IGNORECASE)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _overrides(text, slug):
    """The set of LR-NN ids overridden for `slug` — via the shared SSoT, so a marker quoted inside a
    code span is not honored as a live directive."""
    return {t[0] for t in override_targets(text, slug, r"(LR-[0-9]+)")}


def parse_items(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:legal_risk block."""
    items = []
    if not text or art is None:
        return items
    schema = art.load_schema(_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "legal_risk":
            continue
        idx += 1
        where = "legal_risk #%d" % idx
        if jerr:
            items.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        items.append((obj, art.validate_obj(obj, schema, where), idx))
    return items


def register(text, strict=False):
    """Run the Legal Risk Register integrity checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    items = parse_items(text)
    if not items:
        return 0, ["legal-risk: no legal_risk blocks found — nothing to check"]

    # L1 — schema / JSON validity (per block)
    for _obj, schema_errs, _idx in items:
        for e in schema_errs:
            errs.append("L1 invalid item: %s" % e)

    valid = [(obj, idx) for obj, schema_errs, idx in items if obj is not None and not schema_errs]

    # L2 — duplicate id
    seen = {}
    for obj, idx in valid:
        seen.setdefault(obj.get("id"), []).append(idx)
    by_id = {}
    for lid, where in sorted(seen.items()):
        if len(where) > 1:
            errs.append("L2 duplicate id: %s appears %d times (ids must be unique)" % (lid, len(where)))
        by_id[lid] = next(o for o, _ in valid if o.get("id") == lid)

    # L3 — the register must carry a not-a-lawyer disclaimer in VISIBLE prose (the signature gate).
    # Strip HTML comments + the legal_risk blocks first, so an impl note / block text can't satisfy it.
    visible = _HTML_COMMENT_RE.sub("", text or "")
    if not _DISCLAIMER_RE.search(visible):
        errs.append("L3 missing disclaimer: the register has legal_risk items but no reader-facing "
                    "not-a-lawyer / not-legal-advice disclaimer (HTML comments don't count) — it must "
                    "never read as legal advice")

    advice_overrides = _overrides(text, "legal-advice-drift")
    for lid, obj in sorted(by_id.items()):
        blob = "%s %s" % (obj.get("concern") or "", obj.get("disposition") or "")
        # W1 — legal-advice drift (a conclusion where a flag belongs)
        if _ADVICE_RE.search(blob) and lid not in advice_overrides:
            warns.append("W1 legal-advice drift: %s reads like a legal conclusion, not a flag for "
                         "review — describe the exposure and route it, don't adjudicate" % lid)
        # W2 — a review-now item must route to legal review / counsel
        if obj.get("severity") == "review-now" and not _ROUTING_RE.search(obj.get("disposition") or ""):
            warns.append("W2 unrouted high risk: %s is review-now but its disposition does not route "
                         "to legal review / counsel" % lid)

    # Report
    lines.append("legal-risk: %d item(s)%s" % (
        len(items), "" if len(valid) == len(items) else " (%d well-formed)" % len(valid)))
    for obj, _idx in valid:
        lines.append("  %-7s class=%-15s severity=%s" % (obj.get("id"), obj.get("risk_class"),
                                                         obj.get("severity")))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("legal-risk: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: legal-risk: %d advisory gap(s) — see W1/W2 above" % len(warns))
    else:
        lines.append("legal-risk: PASS (contract + disclaimer gate + flag-don't-adjudicate firewall)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    if len(paths) == 1 and os.path.isdir(paths[0]):
        return _newest(glob.glob(os.path.join(paths[0], _REGISTER_GLOB)))
    for p in paths:
        if _has_block(_read(p) or "", "legal_risk"):
            return p
    return paths[0] if paths else None


def run(paths, strict=False):
    path = resolve(paths)
    if not path:
        return 2, ["legal-risk: no Legal Risk Register artifact found (need a *_Legal_Risk_Register_*.md "
                   "or a file with apodictic:legal_risk blocks)"]
    text = _read(path)
    if text is None:
        return 2, ["legal-risk: cannot read %s" % path]
    return register(text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    DISCLAIMER = "Note: I am not a lawyer; this flags areas that may need legal review and is not legal advice.\n\n"

    def item(lid, rclass="defamation", sev="review-recommended",
             concern="a factual assertion about a named, identifiable living person",
             trigger="any retained statement of fact alleging misconduct by a named living person",
             disp="flag for legal review before publication"):
        obj = {"schema": _SCHEMA_ID, "id": lid, "risk_class": rclass, "severity": sev,
               "concern": concern, "escalation_trigger": trigger, "disposition": disp}
        return "<!-- apodictic:legal_risk\n%s\n-->" % _j.dumps(obj)

    # clean single item (with disclaimer)
    chk("clean_single", register(DISCLAIMER + item("LR-01"))[0] == 0)

    # L1 bad enum / id / missing field / JSON
    chk("l1_bad_class", register(DISCLAIMER + item("LR-01", rclass="slander"))[0] == 1)
    chk("l1_bad_severity", register(DISCLAIMER + item("LR-01", sev="urgent"))[0] == 1)
    chk("l1_bad_id", register(DISCLAIMER + item("LR-1"))[0] == 1)
    chk("l1_missing_field",
        register(DISCLAIMER + item("LR-01").replace('"escalation_trigger"', '"trigger"'))[0] == 1)
    code, lines = register(DISCLAIMER + '<!-- apodictic:legal_risk\n{"schema":"apodictic.legal_risk.v1"\n-->')
    chk("l1_bad_json", code == 1 and any("L1 invalid item" in ln for ln in lines))

    # L2 duplicate id
    code, lines = register(DISCLAIMER + item("LR-01") + "\n" + item("LR-01", rclass="privacy"))
    chk("l2_duplicate_id", code == 1 and any("L2 duplicate" in ln for ln in lines))

    # L3 — missing disclaimer is an ERROR (the signature gate); present is clean
    code, lines = register(item("LR-01"))  # no disclaimer
    chk("l3_missing_disclaimer", code == 1 and any("L3 missing disclaimer" in ln for ln in lines))
    chk("l3_disclaimer_present_ok", register(DISCLAIMER + item("LR-01"))[0] == 0)
    # the disclaimer is also satisfied by the "not legal advice" phrasing alone
    chk("l3_alt_phrasing_ok",
        register("This register is not legal advice.\n\n" + item("LR-01"))[0] == 0)
    # a disclaimer ONLY inside an HTML comment does NOT satisfy L3 — it must be visible prose (PR #43)
    code, lines = register("<!-- impl note: this register is NOT legal advice -->\n" + item("LR-01"))
    chk("l3_comment_only_fails", code == 1 and any("L3 missing disclaimer" in ln for ln in lines))
    # the legal_risk block text alone (which is an HTML comment) cannot satisfy L3 either
    code, lines = register(item("LR-01", disp="flag for legal review; not legal advice as such"))
    chk("l3_block_text_fails", code == 1 and any("L3 missing disclaimer" in ln for ln in lines))

    # W1 — legal-advice drift (a conclusion) => advisory; ERROR --strict; override silences
    code, lines = register(DISCLAIMER + item("LR-01", disp="this passage is not defamatory; no action needed"))
    chk("w1_advice_drift_advisory", code == 0 and any("W1 legal-advice drift" in ln for ln in lines))
    chk("w1_advice_drift_strict_fails",
        register(DISCLAIMER + item("LR-01", concern="the quote is fair use"), strict=True)[0] == 1)
    chk("w1_protected_by_fires",
        any("W1 legal-advice drift" in ln
            for ln in register(DISCLAIMER + item("LR-01", disp="protected by the First Amendment"))[1]))
    ov = "<!-- override: legal-advice-drift LR-01 — quoting the author's own note -->\n"
    chk("w1_override",
        register(DISCLAIMER + ov + item("LR-01", disp="this is not defamatory"))[0] == 0)
    # a plain flag (no conclusion) does not trip W1
    chk("w1_plain_flag_clean",
        not any("W1" in ln for ln in register(DISCLAIMER + item("LR-01"))[1]))

    # W2 — review-now must route to counsel; advisory, ERROR --strict; routed is clean
    code, lines = register(DISCLAIMER + item("LR-01", sev="review-now", disp="hold this chapter"))
    chk("w2_unrouted_advisory", code == 0 and any("W2 unrouted high risk" in ln for ln in lines))
    chk("w2_unrouted_strict_fails",
        register(DISCLAIMER + item("LR-01", sev="review-now", disp="hold this chapter"), strict=True)[0] == 1)
    chk("w2_routed_clean",
        not any("W2" in ln for ln in register(DISCLAIMER + item(
            "LR-01", sev="review-now", disp="route to legal counsel before publication"))[1]))
    # monitor / review-recommended need no routing
    chk("w2_monitor_no_routing_needed",
        not any("W2" in ln for ln in register(DISCLAIMER + item("LR-01", sev="monitor", disp="watch this"))[1]))

    # no blocks -> no-op (even without a disclaimer; L3 only fires when items exist)
    chk("no_items_noop", register("# Notes\nnothing structured\n")[0] == 0)

    # run-folder + explicit-file resolution
    import tempfile
    import shutil
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "Proj_Legal_Risk_Register_run.md")
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Legal Risk Register\n" + DISCLAIMER + item("LR-01") + "\n")
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
    args = [a for a in argv[1:] if a != "legal-risk"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: legal_risk.py legal-risk <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
