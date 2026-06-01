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
            if isinstance(el, dict) and "schema" not in el:
                el = dict(el, schema=default_schema)  # schema inferred from the array
            errs.extend(validate_object(el, where))
    # Cross-check triage_summary against the findings[] tally — only when findings
    # are present (counts may legitimately come from prose on older sidecars).
    findings = obj.get("findings")
    triage = obj.get("triage_summary")
    if findings and isinstance(findings, list) and isinstance(triage, dict):
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
