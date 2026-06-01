#!/usr/bin/env python3
"""APODICTIC structured-state validator (Phase 3).

Validates the real-JSON structured blocks embedded in ledger / editorial-letter
markdown and the Diagnostic_State.meta.json sidecar.

Embedded block envelope (markdown-first; the prose is primary, the block is an
index):

    <!-- apodictic:finding
    {
      "schema": "apodictic.finding.v1",
      "mechanism": "...",
      "severity": "Must-Fix",
      "confidence": "HIGH",
      "evidence_refs": ["Pass 4 §Scene Turns", "Ch. 12"],
      "fix_class": "...",
      "risk_if_fixed": "..."
    }
    -->

This is the parser half of `scripts/validate.sh structured-findings`: validate.sh
is the command surface; JSON gets a real parser here (not shell regex on
colon-lines). `severity` / `confidence` must be canonical tokens
(`output-policy.md §Canonical Severity Scale` / §Confidence Calibration).

Usage:
  structured_findings.py <file> [<file> ...]   # .json => sidecar; else embedded blocks
  structured_findings.py --self-test

Exit: 0 pass, 1 validation error(s), 2 usage error.
"""
import json
import re
import sys

CANON_SEVERITY = {"Must-Fix", "Should-Fix", "Could-Fix"}
CANON_CONFIDENCE = {"HIGH", "MEDIUM", "LOW", "UNCERTAIN"}
AUDIT_RECOMMENDATION = {"run", "recommend", "defer"}

# Required fields per schema id.
SCHEMA_REQUIRED = {
    "apodictic.finding.v1": ["schema", "mechanism", "severity", "confidence",
                             "evidence_refs", "fix_class", "risk_if_fixed"],
    "apodictic.audit_trigger.v1": ["schema", "audit", "evidence", "recommendation"],
    "apodictic.readiness.v1": ["schema", "dimension", "verdict", "rationale"],
}

# Capture everything between the apodictic:<type> marker and the closing --> .
BLOCK_RE = re.compile(r"<!--\s*apodictic:([A-Za-z_]+)\s*(.*?)-->", re.DOTALL)
# A ledger entry is identified by these structural markers; only ledgers must
# carry a finding block per synthesis-bound (Must-Fix/Should-Fix) Notable Finding.
LEDGER_MARKER_RE = re.compile(r"Notable Findings|Ledger Entry", re.IGNORECASE)
# Prose severity labels marking a synthesis-bound finding (outside any block):
# after ** (with optional space, covering "**Severity:** Must-Fix"), "Severity:",
# "held at", "Tier:", or a line-start bullet/number ("- Must-Fix:", "1. Must-Fix").
PROSE_SEVERITY_RE = re.compile(
    r"(?:\*\*\s*|Severity[:\s]+|held at\s+|Tier[:\s]+|(?:^|\n)[ \t]*(?:[-*]|\d+[.)])[ \t]+)(Must-Fix|Should-Fix)\b")


def validate_object(obj, where):
    """Validate one structured object (from a block or a sidecar array)."""
    errs = []
    if not isinstance(obj, dict):
        return ["%s: not a JSON object" % where]
    schema = obj.get("schema")
    if not schema:
        return ["%s: missing 'schema' field" % where]
    if schema not in SCHEMA_REQUIRED:
        return ["%s: unknown schema '%s' (known: %s)"
                % (where, schema, ", ".join(sorted(SCHEMA_REQUIRED)))]
    for key in SCHEMA_REQUIRED[schema]:
        if key not in obj:
            errs.append("%s: schema '%s' missing required field '%s'" % (where, schema, key))
    if schema == "apodictic.finding.v1":
        sev = obj.get("severity")
        if sev is not None and sev not in CANON_SEVERITY:
            errs.append("%s: severity '%s' is not a canonical token (%s)"
                        % (where, sev, ", ".join(sorted(CANON_SEVERITY))))
        conf = obj.get("confidence")
        if conf is not None and conf not in CANON_CONFIDENCE:
            errs.append("%s: confidence '%s' is not a canonical token (%s)"
                        % (where, conf, ", ".join(sorted(CANON_CONFIDENCE))))
        refs = obj.get("evidence_refs")
        if refs is not None and (not isinstance(refs, list) or len(refs) == 0):
            errs.append("%s: evidence_refs must be a non-empty array" % where)
    elif schema == "apodictic.audit_trigger.v1":
        rec = obj.get("recommendation")
        if rec is not None and rec not in AUDIT_RECOMMENDATION:
            errs.append("%s: recommendation '%s' not in (%s)"
                        % (where, rec, ", ".join(sorted(AUDIT_RECOMMENDATION))))
    return errs


def validate_markdown_text(text, label="<md>"):
    """Validate every embedded apodictic:* block. Returns (errors, block_count)."""
    errs = []
    blocks = BLOCK_RE.findall(text)
    for i, (btype, payload) in enumerate(blocks, 1):
        where = "%s block #%d (apodictic:%s)" % (label, i, btype)
        try:
            obj = json.loads(payload.strip())
        except json.JSONDecodeError as exc:
            errs.append("%s: invalid JSON — %s" % (where, exc))
            continue
        schema = obj.get("schema", "") if isinstance(obj, dict) else ""
        if schema and not schema.startswith("apodictic.%s." % btype):
            errs.append("%s: marker type 'apodictic:%s' does not match schema '%s'"
                        % (where, btype, schema))
        errs.extend(validate_object(obj, where))
    return errs, len(blocks)


def validate_sidecar_obj(obj, label="<sidecar>"):
    """Validate the optional structured arrays + the triage_summary cross-check."""
    errs = []
    if not isinstance(obj, dict):
        return ["%s: sidecar is not a JSON object" % label]
    array_schema = {
        "findings": "apodictic.finding.v1",
        "audit_triggers": "apodictic.audit_trigger.v1",
        "readiness": "apodictic.readiness.v1",
    }
    for arr_name, default_schema in array_schema.items():
        arr = obj.get(arr_name)
        if arr is None:
            continue  # arrays are optional; old sidecars stay valid
        if not isinstance(arr, list):
            errs.append("%s.%s: must be an array" % (label, arr_name))
            continue
        for i, el in enumerate(arr):
            where = "%s.%s[%d]" % (label, arr_name, i)
            if isinstance(el, dict):
                el_schema = el.get("schema")
                if el_schema is None:
                    el = dict(el, schema=default_schema)  # inferred from the array
                elif el_schema != default_schema:
                    errs.append("%s: schema '%s' does not match the '%s' array (expected '%s')"
                                % (where, el_schema, arr_name, default_schema))
                    continue
            errs.extend(validate_object(el, where))
    # Cross-check triage_summary against the findings[] tally. A non-empty
    # findings[] REQUIRES a triage_summary object — otherwise the tally invariant
    # the sidecar advertises would silently go unenforced.
    findings = obj.get("findings")
    triage = obj.get("triage_summary")
    if findings and isinstance(findings, list):
        if not isinstance(triage, dict):
            errs.append("%s: findings[] is non-empty but triage_summary is missing or not an "
                        "object — the severity tally cannot be verified" % label)
        else:
            tally = {"Must-Fix": 0, "Should-Fix": 0, "Could-Fix": 0}
            for el in findings:
                if isinstance(el, dict) and el.get("severity") in tally:
                    tally[el["severity"]] += 1
            expect = {"must_fix": tally["Must-Fix"],
                      "should_fix": tally["Should-Fix"],
                      "could_fix": tally["Could-Fix"]}
            for key, want in expect.items():
                try:
                    got = int(triage.get(key, 0))
                except (TypeError, ValueError):
                    got = None
                if got != want:
                    errs.append("%s: triage_summary.%s=%s but findings[] tally for that "
                                "severity is %d" % (label, key, triage.get(key), want))
    return errs


def check_block_presence(text, label):
    """In a ledger, every synthesis-bound (Must-Fix/Should-Fix) Notable Finding must
    carry an apodictic:finding block (findings-ledger-format.md). Heuristic: compare
    the count of prose severity labels (outside any block) to the count of finding
    blocks. Enforced only for ledger entries; author-facing letters keep severities
    in prose / the Severity Calibration appendix and are not required to embed blocks."""
    if not LEDGER_MARKER_RE.search(text):
        return []
    outside = BLOCK_RE.sub("", text)
    labels = len(PROSE_SEVERITY_RE.findall(outside))
    finding_blocks = sum(1 for btype, _ in BLOCK_RE.findall(text) if btype == "finding")
    if labels > finding_blocks:
        return ["%s: %d synthesis-bound (Must-Fix/Should-Fix) finding label(s) but only %d "
                "apodictic:finding block(s) — each synthesis-bound Notable Finding requires a "
                "structured block (findings-ledger-format.md)" % (label, labels, finding_blocks)]
    return []


def validate_file(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        return ["%s: cannot read — %s" % (path, exc)]
    if path.endswith(".json"):
        try:
            obj = json.loads(text)
        except json.JSONDecodeError as exc:
            return ["%s: invalid JSON — %s" % (path, exc)]
        return validate_sidecar_obj(obj, label=path)
    errs, _ = validate_markdown_text(text, label=path)
    errs.extend(check_block_presence(text, path))
    return errs


def run_self_test():
    results = {"rc": 0}

    def check(name, errs, expect_clean):
        clean = (len(errs) == 0)
        if clean == expect_clean:
            print("  %s: OK" % name)
        else:
            print("  %s: FAIL (errs=%s)" % (name, errs))
            results["rc"] = 1

    md_ok = ('<!-- apodictic:finding\n'
             '{"schema":"apodictic.finding.v1","mechanism":"m","severity":"Must-Fix",'
             '"confidence":"HIGH","evidence_refs":["Ch.1"],"fix_class":"x","risk_if_fixed":"y"}\n-->')
    e, n = validate_markdown_text(md_ok)
    check("finding_valid", e, True)
    check("finding_count", [] if n == 1 else ["count=%d" % n], True)
    check("finding_bad_severity", validate_markdown_text(md_ok.replace("Must-Fix", "Critical"))[0], False)
    check("finding_bad_confidence", validate_markdown_text(md_ok.replace("HIGH", "PRETTY-SURE"))[0], False)
    md_missing = ('<!-- apodictic:finding\n'
                  '{"schema":"apodictic.finding.v1","severity":"Must-Fix","confidence":"HIGH",'
                  '"evidence_refs":["c"],"fix_class":"x","risk_if_fixed":"y"}\n-->')
    check("finding_missing_mechanism", validate_markdown_text(md_missing)[0], False)
    md_emptyrefs = md_ok.replace('["Ch.1"]', '[]')
    check("finding_empty_evidence", validate_markdown_text(md_emptyrefs)[0], False)
    md_badjson = '<!-- apodictic:finding\n{"schema":"apodictic.finding.v1", "severity": }\n-->'
    check("finding_bad_json", validate_markdown_text(md_badjson)[0], False)
    md_mismatch = md_ok.replace("apodictic:finding", "apodictic:readiness", 1)
    check("marker_schema_mismatch", validate_markdown_text(md_mismatch)[0], False)
    md_at = ('<!-- apodictic:audit_trigger\n'
             '{"schema":"apodictic.audit_trigger.v1","audit":"Reception Risk",'
             '"evidence":"L2956","recommendation":"run"}\n-->')
    check("audit_trigger_valid", validate_markdown_text(md_at)[0], True)
    check("audit_trigger_bad_rec", validate_markdown_text(md_at.replace('"run"', '"maybe"'))[0], False)
    md_rd = ('<!-- apodictic:readiness\n'
             '{"schema":"apodictic.readiness.v1","dimension":"structure",'
             '"verdict":"not-ready","rationale":"r"}\n-->')
    check("readiness_valid", validate_markdown_text(md_rd)[0], True)
    sc_ok = {"findings": [{"schema": "apodictic.finding.v1", "mechanism": "m",
                           "severity": "Must-Fix", "confidence": "HIGH",
                           "evidence_refs": ["c"], "fix_class": "x", "risk_if_fixed": "y"}],
             "triage_summary": {"must_fix": 1, "should_fix": 0, "could_fix": 0}}
    check("sidecar_tally_match", validate_sidecar_obj(sc_ok), True)
    sc_bad = json.loads(json.dumps(sc_ok))
    sc_bad["triage_summary"]["must_fix"] = 2
    check("sidecar_tally_mismatch", validate_sidecar_obj(sc_bad), False)
    check("sidecar_empty_template",
          validate_sidecar_obj({"findings": [], "triage_summary": {"must_fix": 0, "should_fix": 0, "could_fix": 0}}),
          True)
    check("sidecar_no_arrays_backcompat",
          validate_sidecar_obj({"triage_summary": {"must_fix": 3, "should_fix": 1, "could_fix": 0}}),
          True)
    # schema/array mismatch: a readiness object placed in findings[] must be rejected
    check("sidecar_schema_array_mismatch",
          validate_sidecar_obj({"findings": [{"schema": "apodictic.readiness.v1", "dimension": "d",
                                              "verdict": "v", "rationale": "r"}],
                                "triage_summary": {"must_fix": 0, "should_fix": 0, "could_fix": 0}}),
          False)
    # findings[] non-empty but triage_summary missing -> must error
    check("sidecar_findings_without_triage",
          validate_sidecar_obj({"findings": [{"schema": "apodictic.finding.v1", "mechanism": "m",
                                              "severity": "Must-Fix", "confidence": "HIGH",
                                              "evidence_refs": ["c"], "fix_class": "x", "risk_if_fixed": "y"}]}),
          False)
    # ledger block-presence: severity-labeled finding with no block -> error
    check("ledger_block_missing",
          check_block_presence("## Pass 5 — Ledger Entry\n### Notable Findings\n"
                               "1. **Agency collapse.** Severity: Must-Fix.\n", "<t>"),
          False)
    # bold-label and bullet/number severity forms must also be caught
    check("ledger_block_missing_bold_label",
          check_block_presence("## Pass 5 — Ledger Entry\n### Notable Findings\n"
                               "1. **Severity:** Must-Fix — Agency collapse.\n", "<t>"),
          False)
    check("ledger_block_missing_bullet",
          check_block_presence("## Pass 5 — Ledger Entry\n### Notable Findings\n"
                               "- Must-Fix: Agency collapse.\n", "<t>"),
          False)
    # ledger block-presence: finding + block -> clean
    check("ledger_block_present",
          check_block_presence("## Pass 5 — Ledger Entry\n### Notable Findings\n"
                               "1. **Agency collapse.** Severity: Must-Fix.\n"
                               '<!-- apodictic:finding\n{"schema":"apodictic.finding.v1"}\n-->\n', "<t>"),
          True)
    # non-ledger (letter) with prose Must-Fix and no block -> not enforced (clean)
    check("non_ledger_presence_not_enforced",
          check_block_presence("# Editorial Letter\nThe pacing is a Must-Fix problem.\n", "<t>"),
          True)
    if results["rc"] == 0:
        print("Self-test: PASS")
    else:
        print("Self-test: FAIL")
    return results["rc"]


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    if argv[1] == "--self-test":
        return run_self_test()
    all_errs = []
    for path in argv[1:]:
        all_errs.extend(validate_file(path))
    if all_errs:
        for err in all_errs:
            print("ERROR: %s" % err)
        print("structured-findings: FAIL (%d error(s))" % len(all_errs))
        return 1
    print("structured-findings: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
