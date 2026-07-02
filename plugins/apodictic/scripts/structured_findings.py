#!/usr/bin/env python3
"""APODICTIC structured-state validator (Phase 3; Harness Contracts v2).

Validates the real-JSON structured blocks embedded in ledger / editorial-letter
markdown and the Diagnostic_State.meta.json sidecar.

Contracts are defined by the JSON Schema files in `plugins/apodictic/schemas/`
(the single source of truth) and applied by the shared `apodictic_artifacts`
module — this file owns only the orchestration (which artifacts to scan, the
ledger block-presence invariant, and the sidecar triage cross-check).

  structured_findings.py <file> [<file> ...]   # .json => sidecar; else embedded blocks
  structured_findings.py --self-test

Exit: 0 pass, 1 validation error(s), 2 usage error.
"""
import glob
import json
import os
import re
import sys

import apodictic_artifacts as art

# A ledger entry is identified by these markers; only ledgers must carry a
# finding block per synthesis-bound (Must-Fix/Should-Fix) Notable Finding.
LEDGER_MARKER_RE = re.compile(r"Notable Findings|Ledger Entry", re.IGNORECASE)
# Prose severity labels marking a synthesis-bound finding (outside any block):
# after **, "Severity:", "held at", "Tier:", or a line-start bullet/number.
PROSE_SEVERITY_RE = re.compile(
    r"(?:\*\*\s*|Severity[:\s]+|held at\s+|Tier[:\s]+|(?:^|\n)[ \t]*(?:[-*]|\d+[.)])[ \t]+)(Must-Fix|Should-Fix)\b")


def _duplicate_id_errors(ids, label):
    """Finding Lifecycle IDs must be unique per run."""
    seen, errs = {}, []
    for fid in ids:
        if fid:
            seen[fid] = seen.get(fid, 0) + 1
    for fid, count in seen.items():
        if count > 1:
            errs.append("%s: finding id %r appears %d times — Lifecycle IDs must be unique per run"
                        % (label, fid, count))
    return errs


def validate_markdown_text(text, label="<md>"):
    """Validate every embedded apodictic:* block against its schema. (errors, count)."""
    errs = []
    blocks = art.parse_blocks(text)
    for i, (btype, obj, jerr) in enumerate(blocks, 1):
        where = "%s block #%d (apodictic:%s)" % (label, i, btype)
        if jerr:
            errs.append("%s: invalid JSON — %s" % (where, jerr))
            continue
        schema_id = obj.get("schema") if isinstance(obj, dict) else None
        if schema_id and not str(schema_id).startswith("apodictic.%s." % btype):
            errs.append("%s: marker type 'apodictic:%s' does not match schema '%s'"
                        % (where, btype, schema_id))
        schema = art.load_schema(schema_id) if schema_id else None
        if schema is None:
            errs.append("%s: missing or unknown schema %r (known: %s)"
                        % (where, schema_id, ", ".join(art.known_schema_ids())))
            continue
        errs.extend(art.validate_obj(obj, schema, where))
    errs.extend(_duplicate_id_errors(
        [obj.get("id") for bt, obj, je in blocks if bt == "finding" and isinstance(obj, dict)], label))
    return errs, len(blocks)


def severity_tally(items):
    """The canonical severity tally: count each item's `severity` over the schema-sourced severity
    set and map to the `triage_summary` keys (`Must-Fix/Should-Fix/Could-Fix` ->
    `must_fix/should_fix/could_fix`). Factored out of validate_sidecar_obj so `disposition-check`'s
    DP2.4 tally guard (docs/finding-dispositions.md) REUSES the exact logic it audits — the guard
    cannot drift from the tally. `items` is any iterable of dicts carrying `severity` (the sidecar
    findings[] array here; the ledger's parsed apodictic.finding.v1 blocks in disposition_check)."""
    tally = {sev: 0 for sev in art.load_severity_values()}
    for el in items:
        if isinstance(el, dict) and el.get("severity") in tally:
            tally[el["severity"]] += 1
    return {"must_fix": tally.get("Must-Fix", 0),
            "should_fix": tally.get("Should-Fix", 0),
            "could_fix": tally.get("Could-Fix", 0)}


def validate_sidecar_obj(obj, label="<sidecar>"):
    """Validate the optional structured arrays + the triage_summary cross-check."""
    errs = []
    if not isinstance(obj, dict):
        return ["%s: sidecar is not a JSON object" % label]
    sidecar_schema = art.load_schema("apodictic.diagnostic-state.v1")
    for arr_name, schema_id in art.array_item_schemas(sidecar_schema).items():
        arr = obj.get(arr_name)
        if arr is None:
            continue  # arrays are optional; old sidecars stay valid
        if not isinstance(arr, list):
            errs.append("%s.%s: must be an array" % (label, arr_name))
            continue
        item_schema = art.load_schema(schema_id)
        for i, el in enumerate(arr):
            where = "%s.%s[%d]" % (label, arr_name, i)
            if isinstance(el, dict):
                el_schema = el.get("schema")
                if el_schema is None:
                    el = dict(el, schema=schema_id)  # infer from the array
                elif el_schema != schema_id:
                    errs.append("%s: schema '%s' does not match the '%s' array (expected '%s')"
                                % (where, el_schema, arr_name, schema_id))
                    continue
            errs.extend(art.validate_obj(el, item_schema, where))
    if isinstance(obj.get("findings"), list):
        errs.extend(_duplicate_id_errors(
            [el.get("id") for el in obj["findings"] if isinstance(el, dict)], "%s.findings" % label))
    # Cross-field rule (not expressible in schema): a non-empty findings[] REQUIRES
    # a triage_summary whose counts equal the findings[] severity tally.
    findings = obj.get("findings")
    triage = obj.get("triage_summary")
    if findings and isinstance(findings, list):
        if not isinstance(triage, dict):
            errs.append("%s: findings[] is non-empty but triage_summary is missing or not an "
                        "object — the severity tally cannot be verified" % label)
        else:
            expect = severity_tally(findings)
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
    prose severity labels (outside any block) to the count of finding blocks.
    Enforced only for ledger entries; author-facing letters keep severities in prose
    / the Severity Calibration appendix and are not required to embed blocks."""
    if not LEDGER_MARKER_RE.search(text):
        return []
    outside = art.BLOCK_RE.sub("", text)
    labels = len(PROSE_SEVERITY_RE.findall(outside))
    finding_blocks = sum(1 for btype, _obj, _err in art.parse_blocks(text) if btype == "finding")
    if labels > finding_blocks:
        return ["%s: %d synthesis-bound (Must-Fix/Should-Fix) finding label(s) but only %d "
                "apodictic:finding block(s) — each synthesis-bound Notable Finding requires a "
                "structured block (findings-ledger-format.md)" % (label, labels, finding_blocks)]
    return []


def validate_file(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError) as exc:
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


def _fixture_dir():
    """Locate test_fixtures/ from the plugin or root scripts copy."""
    here = os.path.dirname(os.path.abspath(__file__))
    for c in (os.path.join(here, "test_fixtures"),
              os.path.join(here, "..", "plugins", "apodictic", "scripts", "test_fixtures")):
        if os.path.isdir(c):
            return c
    return None


def run_self_test():
    results = {"rc": 0}

    def check(name, errs, expect_clean):
        if (len(errs) == 0) == expect_clean:
            print("  %s: OK" % name)
        else:
            print("  %s: FAIL (errs=%s)" % (name, errs))
            results["rc"] = 1

    # non-UTF8 artifact: validate_file must degrade to the cannot-read error path,
    # never a traceback (the disposition_check adjacent-exception class, swept repo-wide)
    import tempfile as _tf
    _fd, _nu = _tf.mkstemp(suffix=".md")
    with os.fdopen(_fd, "wb") as _fh:
        _fh.write(b"\xff\xfenot utf-8\xff")
    check("non_utf8_validate_file_degrades", validate_file(_nu), False)
    os.unlink(_nu)

    F = ('<!-- apodictic:finding\n'
         '{"schema":"apodictic.finding.v1","id":"F-P5-01","mechanism":"m","severity":"Must-Fix",'
         '"confidence":"HIGH","evidence_refs":["Ch.1"],"fix_class":"x","risk_if_fixed":"y"}\n-->')
    e, n = validate_markdown_text(F)
    check("finding_valid", e, True)
    check("finding_count", [] if n == 1 else ["count=%d" % n], True)
    check("finding_bad_severity", validate_markdown_text(F.replace("Must-Fix", "Critical"))[0], False)
    check("finding_bad_confidence", validate_markdown_text(F.replace("HIGH", "PRETTY-SURE"))[0], False)
    miss = ('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"F-P5-02","severity":"Must-Fix",'
            '"confidence":"HIGH","evidence_refs":["c"],"fix_class":"x","risk_if_fixed":"y"}\n-->')
    check("finding_missing_mechanism", validate_markdown_text(miss)[0], False)
    check("finding_empty_evidence", validate_markdown_text(F.replace('["Ch.1"]', "[]"))[0], False)
    check("finding_missing_id", validate_markdown_text(F.replace('"id":"F-P5-01",', ""))[0], False)
    check("finding_bad_id_format", validate_markdown_text(F.replace("F-P5-01", "P5-1"))[0], False)
    check("finding_duplicate_ids",
          validate_markdown_text(F + "\n" + F.replace('"mechanism":"m"', '"mechanism":"n"'))[0], False)
    check("finding_bad_json",
          validate_markdown_text('<!-- apodictic:finding\n{"schema":"x", "severity": }\n-->')[0], False)
    check("marker_schema_mismatch",
          validate_markdown_text(F.replace("apodictic:finding", "apodictic:readiness", 1))[0], False)
    AT = ('<!-- apodictic:audit_trigger\n{"schema":"apodictic.audit_trigger.v1","audit":"Reception Risk",'
          '"evidence":"L2956","recommendation":"run"}\n-->')
    check("audit_trigger_valid", validate_markdown_text(AT)[0], True)
    check("audit_trigger_bad_rec", validate_markdown_text(AT.replace('"run"', '"maybe"'))[0], False)
    RD = ('<!-- apodictic:readiness\n{"schema":"apodictic.readiness.v1","dimension":"structure",'
          '"verdict":"not-ready","rationale":"r"}\n-->')
    check("readiness_valid", validate_markdown_text(RD)[0], True)
    fobj = {"schema": "apodictic.finding.v1", "id": "F-P5-03", "mechanism": "m", "severity": "Must-Fix",
            "confidence": "HIGH", "evidence_refs": ["c"], "fix_class": "x", "risk_if_fixed": "y"}
    sc_ok = {"findings": [fobj], "triage_summary": {"must_fix": 1, "should_fix": 0, "could_fix": 0}}
    check("sidecar_tally_match", validate_sidecar_obj(sc_ok), True)
    sc_bad = json.loads(json.dumps(sc_ok)); sc_bad["triage_summary"]["must_fix"] = 2
    check("sidecar_tally_mismatch", validate_sidecar_obj(sc_bad), False)
    check("sidecar_empty_template",
          validate_sidecar_obj({"findings": [], "triage_summary": {"must_fix": 0, "should_fix": 0, "could_fix": 0}}), True)
    check("sidecar_no_arrays_backcompat",
          validate_sidecar_obj({"triage_summary": {"must_fix": 3, "should_fix": 1, "could_fix": 0}}), True)
    check("sidecar_schema_array_mismatch",
          validate_sidecar_obj({"findings": [{"schema": "apodictic.readiness.v1", "dimension": "d",
                                              "verdict": "v", "rationale": "r"}],
                                "triage_summary": {"must_fix": 0, "should_fix": 0, "could_fix": 0}}), False)
    check("sidecar_findings_without_triage", validate_sidecar_obj({"findings": [fobj]}), False)
    led = "## Pass 5 — Ledger Entry\n### Notable Findings\n"
    check("ledger_block_missing", check_block_presence(led + "1. **Agency collapse.** Severity: Must-Fix.\n", "<t>"), False)
    check("ledger_block_missing_bold_label",
          check_block_presence(led + "1. **Severity:** Must-Fix — Agency collapse.\n", "<t>"), False)
    check("ledger_block_missing_bullet", check_block_presence(led + "- Must-Fix: Agency collapse.\n", "<t>"), False)
    check("ledger_block_present",
          check_block_presence(led + "1. **Agency collapse.** Severity: Must-Fix.\n"
                               '<!-- apodictic:finding\n{"schema":"apodictic.finding.v1"}\n-->\n', "<t>"), True)
    check("non_ledger_presence_not_enforced",
          check_block_presence("# Editorial Letter\nThe pacing is a Must-Fix problem.\n", "<t>"), True)
    # Data-driven fixtures: sf.<pass|fail>.<name>.<md|json> in test_fixtures/.
    fdir = _fixture_dir()
    if fdir:
        for path in sorted(glob.glob(os.path.join(fdir, "sf.*"))):
            name = os.path.basename(path)
            check("fixture:%s" % name, validate_file(path), ".pass." in name)
    else:
        print("  fixtures: SKIP (test_fixtures/ not found)")
    print("Self-test: PASS" if results["rc"] == 0 else "Self-test: FAIL")
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
