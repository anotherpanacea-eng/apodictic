#!/usr/bin/env python3
"""Shared parsing + schema validation for APODICTIC structured artifacts.

Stdlib-only. The JSON Schema files in `plugins/apodictic/schemas/` are the single
source of truth for the structured-artifact contracts (apodictic.finding.v1,
audit_trigger.v1, readiness.v1, diagnostic-state.v1). This module is a *subset*
JSON-Schema validator — it honors `required`, `const`, `enum`, `type`, array
`minItems`, and `pattern`, plus the `items.$schema_ref` extension for arrays of
typed objects. It is deliberately NOT a full JSON-Schema engine (the plugin
runtime is stdlib-only, no `jsonschema` dependency).

`structured_findings.py` and `honesty_check.py` both build on this module, so the
block grammar and the field contracts live in exactly one place.

  apodictic_artifacts.py --self-test
"""
import json
import os
import re
import sys
from pathlib import Path

try:
    import override_marker as _ovm  # code-span stripping SSoT (meta-linter M6); sibling module
except ImportError:
    _ovm = None

# One grammar for the embedded block carrier, shared by every validator. We match the
# CARRIER (`<!-- apodictic:<type> ... -->`) first and capture the whole payload up to the
# closing `-->`, rather than only comments that already contain a complete `{...}`. A broken
# payload (e.g. a missing closing brace) is then surfaced as a JSON error by parse_blocks
# instead of disappearing before validation.
BLOCK_RE = re.compile(r"<!--\s*apodictic:([A-Za-z_]+)\s*(.*?)\s*-->", re.DOTALL)

# Exact Finding Lifecycle ID token (boundary-guarded, so F-P5-01 != F-P5-011). The same pattern as
# the finding schema's `id` and honesty_check._id_present's per-id boundary match — hosted HERE
# because the disposition-marker grammar below (and its consumers: run_gate.py,
# disposition_check.py, feedback_triage.py W3) needs it and this module must stay dependency-free
# (finding_trace imports THIS module, so it cannot be imported from here). This is the SINGLE
# compiled source: finding_trace._ID_RE and regression_diff._ID_RE are re-pointed to this object
# (each keeps a byte-equal literal only as its art-less degraded fallback), and the
# fid_re_lockstep self-test below pins all three patterns equal so the fallbacks cannot drift.
FID_RE = re.compile(r"(?<![\w-])F-[A-Za-z0-9]+-[0-9]{2,}(?![\w-])")

# Finding-disposition marker grammar — the SINGLE SSoT (docs/finding-dispositions.md §Schema 3),
# sibling of finding_trace's `<!-- resolved: F-… -->` family. Pinned forms:
#   <!-- declined: F-P5-01 — <one-line reason> -->
#   <!-- deferred: F-P5-01 until: <trigger> — <one-line reason> -->
# Hosted HERE (not finding_trace) so run_gate.py can use it without the hard finding_trace
# dependency its lazy-import comment exists to avoid, and imported by BOTH run_gate.py and
# disposition_check.py — neither defines a local copy. Case-insensitive; no collision with the
# resolved:/override:/finding: comment families.
_DISPOSITION_RE = re.compile(r"<!--\s*(declined|deferred):(.*?)-->", re.DOTALL | re.IGNORECASE)
# Body grammar: the id must LEAD the body (a prose comment merely mentioning an id is not a
# disposition marker); `until:` (deferred only) then an em-/en-dash separates the reason.
_DISPOSITION_BODY_RE = re.compile(
    r"^\s*(F-[A-Za-z0-9]+-[0-9]{2,})(?![\w-])\s*(.*)$", re.DOTALL)
_DISPOSITION_DASH_RE = re.compile(r"\s*[—–]\s*")


def parse_disposition_markers(text):
    """Parse the pinned finding-disposition markers out of `text`.

    Returns [{"kind": "declined"|"deferred", "id": str, "trigger": str|None, "reason": str}, ...]
    in document order. Parsing is LENIENT, validation strict: a marker missing its reason (or a
    deferred marker missing `until: <trigger>`) still parses — with reason ""/trigger None — and is
    then refused by the record-shape gates (disposition-check DP0; run_gate's write-time guard),
    so a malformed marker is surfaced, never silently honored. A comment whose body does not LEAD
    with a Finding Lifecycle ID is not a disposition marker and is skipped (e.g. a docs example
    deferring a work item by slug). Code spans are stripped first through the override_marker SSoT
    (meta-linter M6) so a marker quoted in a fenced/inline documentation example is never live."""
    if not text:
        return []
    region = _ovm.strip_code_spans(text) if _ovm is not None else text
    out = []
    for kind, body in _DISPOSITION_RE.findall(region):
        m = _DISPOSITION_BODY_RE.match(body)
        if not m:
            continue  # no leading F-id -> not a disposition marker
        fid, rest = m.group(1), m.group(2).strip()
        kind = kind.lower()
        trigger = None
        if kind == "deferred":
            um = re.match(r"^until:\s*(.*)$", rest, re.DOTALL)
            if um:
                parts = _DISPOSITION_DASH_RE.split(um.group(1), maxsplit=1)
                trigger = parts[0].strip() or None
                reason = parts[1].strip() if len(parts) > 1 else ""
            else:
                # no `until:` -> no trigger; whole tail (past any dash) is the reason
                parts = _DISPOSITION_DASH_RE.split(rest, maxsplit=1)
                reason = parts[1].strip() if len(parts) > 1 else parts[0].strip()
        else:
            parts = _DISPOSITION_DASH_RE.split(rest, maxsplit=1)
            reason = parts[1].strip() if len(parts) > 1 else parts[0].strip()
        out.append({"kind": kind, "id": fid, "trigger": trigger, "reason": reason})
    return out

# Canonical severity ORDER (semantic; the SET is cross-checked against the
# finding schema's `severity` enum by load_severity_values()).
SEVERITY_RANK = {"Could-Fix": 1, "Should-Fix": 2, "Must-Fix": 3}

_TYPES = {"string": str, "array": list, "object": dict,
          "integer": int, "number": (int, float), "boolean": bool}
_SCHEMA_CACHE = {}


def schema_dir():
    """Locate plugins/apodictic/schemas/ from either the plugin or root scripts copy."""
    env = os.environ.get("APODICTIC_SCHEMA_DIR")
    here = Path(__file__).resolve().parent
    candidates = ([Path(env)] if env else []) + [
        here / "schemas",
        here / ".." / "schemas",
        here / ".." / "plugins" / "apodictic" / "schemas",
        here / ".." / ".." / "plugins" / "apodictic" / "schemas",
    ]
    for c in candidates:
        c = c.resolve()
        if c.is_dir() and any(c.glob("*.schema.json")):
            return c
    return None


def load_schema(schema_id):
    """Load a schema by $id (filename stem). Returns the dict or None. Cached."""
    if schema_id in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[schema_id]
    schema = None
    d = schema_dir()
    if d:
        f = d / (schema_id + ".schema.json")
        if f.exists():
            try:
                schema = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                schema = None
    _SCHEMA_CACHE[schema_id] = schema
    return schema


def known_schema_ids():
    """All schema $ids available on disk (filename stems)."""
    d = schema_dir()
    return sorted(p.name[:-len(".schema.json")] for p in d.glob("*.schema.json")) if d else []


def schema_field_names(schema_id):
    """Declared `properties` keys of a schema, as a frozenset, or None if the schema is absent.

    The single source of truth a docs-no-re-list lint reads to assert no author-facing doc
    enumerates a field name the schema does not declare (Harness Contracts v2)."""
    schema = load_schema(schema_id)
    if schema is None:
        return None
    return frozenset((schema.get("properties") or {}).keys())


def fid_key(value):
    """A finding/ledger id normalized to a hashable, sortable form (a str, or None). The SINGLE source
    of truth for the recurring non-hashable/non-string id crash class: a malformed id (a JSON list/
    object/number kept as-is by parse_*) is str()-coerced — a valid string id is unchanged — so it can
    never crash a dict KEY (uniqueness maps, ledger indexes, comment-provenance joins) or a SORT key
    (`'<' not supported between str and int`). Lives here (the lowest shared lib) so finding_trace,
    annotation_manifest, annotation_export, reanchor, … all route through ONE coercion."""
    return value if value is None or isinstance(value, str) else str(value)


def load_severity_values():
    """Severity tokens, sourced from the finding schema's enum (fallback to RANK)."""
    s = load_schema("apodictic.finding.v1")
    enum = (s or {}).get("properties", {}).get("severity", {}).get("enum")
    return list(enum) if enum else list(SEVERITY_RANK.keys())


# Chapter-reference normalizer — SHARED so viz_manifest (chapter binning) and
# annotation_manifest (the anchor ladder's chapter rung) cannot drift. Recognizes the
# four canonical evidence-ref forms — "Chapter N" / "Ch. N" / "Ch.N" / "Ch N"
# (case-insensitive) — and returns the canonical token "Ch N", else None. A trailing
# page suffix (the "p.40" in "Ch.3 p.40") is ignored, never promoted to precision.
_CHAPTER_TOKEN_RE = re.compile(r"\bch(?:apter)?\.?\s*(\d+)\b", re.IGNORECASE)


def chapter_token(ref):
    """Canonical chapter token ('Ch N') from a reference string, or None if it names no chapter."""
    if ref is None:
        return None
    m = _CHAPTER_TOKEN_RE.search(str(ref))
    return ("Ch %s" % m.group(1)) if m else None


def array_item_schemas(container_schema):
    """field -> referenced schema id, from each array property's items.$schema_ref."""
    out = {}
    for key, spec in (container_schema or {}).get("properties", {}).items():
        if isinstance(spec, dict) and spec.get("type") == "array":
            ref = (spec.get("items") or {}).get("$schema_ref")
            if ref:
                out[key] = ref
    return out


def parse_blocks(text):
    """Return [(btype, obj, json_error_or_None), ...] for each apodictic:<type> block."""
    out = []
    for btype, payload in BLOCK_RE.findall(text):
        try:
            out.append((btype, json.loads(payload.strip()), None))
        except json.JSONDecodeError as exc:
            out.append((btype, None, str(exc)))
    return out


def _type_ok(val, t):
    py = _TYPES.get(t)
    if py is None:
        return True
    if t == "integer" and isinstance(val, bool):
        return False  # bool subclasses int; reject for integer fields
    return isinstance(val, py)


def validate_obj(obj, schema, where="<obj>"):
    """Subset JSON-Schema validation of a single object. Returns a list of errors."""
    if schema is None:
        return ["%s: no schema available to validate against" % where]
    if not isinstance(obj, dict):
        return ["%s: expected a JSON object" % where]
    errs = []
    for key in schema.get("required", []):
        if key not in obj:
            errs.append("%s: missing required field '%s'" % (where, key))
    for key, spec in schema.get("properties", {}).items():
        if key not in obj or not isinstance(spec, dict):
            continue
        val = obj[key]
        if "const" in spec and val != spec["const"]:
            errs.append("%s: '%s' must be '%s' (got %r)" % (where, key, spec["const"], val))
        if "enum" in spec and val not in spec["enum"]:
            errs.append("%s: '%s'=%r not in %s" % (where, key, val, spec["enum"]))
        if "type" in spec and not _type_ok(val, spec["type"]):
            errs.append("%s: '%s' must be type %s" % (where, key, spec["type"]))
        if spec.get("type") == "array" and isinstance(val, list):
            if len(val) < spec.get("minItems", 0):
                errs.append("%s: '%s' requires >= %d item(s)" % (where, key, spec["minItems"]))
            item_type = (spec.get("items") or {}).get("type")
            if item_type:
                for j, el in enumerate(val):
                    if not _type_ok(el, item_type):
                        errs.append("%s: '%s'[%d]=%r must be type %s" % (where, key, j, el, item_type))
        if "pattern" in spec and isinstance(val, str) and not re.search(spec["pattern"], val):
            errs.append("%s: '%s'=%r does not match pattern /%s/" % (where, key, val, spec["pattern"]))
    # Closed-key enforcement (Harness Contracts v2): opt-in per schema. When a schema declares
    # `additionalProperties: false`, every key not in `properties` is an error — this is what kills
    # a misspelled field (a `severty` typo) that today validates clean. Backward-compatible: schemas
    # default to `additionalProperties` absent/true, which keeps the permissive behavior the open
    # schemas (the sidecar, gate_event) intentionally rely on.
    if schema.get("additionalProperties") is False:
        declared = set(schema.get("properties", {}).keys())
        for key in obj:
            if key not in declared:
                errs.append("%s: unknown field '%s' (schema is closed; additionalProperties:false)" % (where, key))
    return errs


def run_self_test():
    rc = {"v": 0}

    def check(name, errs, expect_clean):
        ok = (len(errs) == 0) == expect_clean
        print("  %s: %s" % (name, "OK" if ok else "FAIL (errs=%s)" % errs))
        if not ok:
            rc["v"] = 1

    finding = load_schema("apodictic.finding.v1")
    if finding is None:
        print("  schema_load: FAIL (apodictic.finding.v1 not found via schema_dir=%s)" % schema_dir())
        print("Self-test: FAIL")
        return 1
    print("  schema_load: OK (%s)" % schema_dir())
    good = {"schema": "apodictic.finding.v1", "id": "F-P5-01", "mechanism": "m", "severity": "Must-Fix",
            "confidence": "HIGH", "evidence_refs": ["c"], "fix_class": "x", "risk_if_fixed": "y"}
    check("finding_valid", validate_obj(good, finding), True)
    check("bad_severity", validate_obj(dict(good, severity="Critical"), finding), False)
    check("bad_confidence", validate_obj(dict(good, confidence="SURE"), finding), False)
    check("missing_field", validate_obj({k: v for k, v in good.items() if k != "mechanism"}, finding), False)
    check("missing_id", validate_obj({k: v for k, v in good.items() if k != "id"}, finding), False)
    check("bad_id_pattern", validate_obj(dict(good, id="P5-1"), finding), False)
    check("empty_evidence", validate_obj(dict(good, evidence_refs=[]), finding), False)
    check("non_string_evidence_item", validate_obj(dict(good, evidence_refs=[123]), finding), False)
    check("wrong_const", validate_obj(dict(good, schema="apodictic.readiness.v1"), finding), False)
    check("severity_enum_matches_rank",
          [] if set(load_severity_values()) == set(SEVERITY_RANK) else ["mismatch"], True)
    blocks = parse_blocks('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1"}\n-->')
    check("parse_blocks", [] if (len(blocks) == 1 and blocks[0][0] == "finding" and blocks[0][1]) else ["bad"], True)
    # A broken carrier (no closing brace before -->) must be detected as a malformed block
    # (json error), not silently disappear before validation.
    broken = parse_blocks('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1"\n-->')
    check("parse_blocks_broken_carrier",
          [] if (len(broken) == 1 and broken[0][0] == "finding" and broken[0][1] is None
                 and broken[0][2]) else ["bad"], True)
    # chapter_token — the shared chapter-ref normalizer (all four canonical forms; page suffix ignored)
    ct_ok = (chapter_token("Chapter 9") == "Ch 9" and chapter_token("Ch. 12") == "Ch 12"
             and chapter_token("Ch.3 p.40") == "Ch 3" and chapter_token("Ch 7") == "Ch 7"
             and chapter_token("Pass 1 §Orientation") is None and chapter_token("§Scene Turns") is None
             and chapter_token(None) is None)
    check("chapter_token", [] if ct_ok else ["chapter_token mismatch"], True)
    # Closed-key enforcement (Harness Contracts v2): a schema with additionalProperties:false rejects
    # an unknown key; the same schema without the flag (absent/true) still permits it — no regression
    # to the open schemas (the sidecar, gate_event).
    closed = {"type": "object", "required": ["schema"],
              "properties": {"schema": {"const": "x"}, "a": {"type": "string"}},
              "additionalProperties": False}
    open_ = {k: v for k, v in closed.items() if k != "additionalProperties"}
    check("closed_key_rejects_unknown", validate_obj({"schema": "x", "a": "y", "stray": 1}, closed), False)
    check("closed_key_allows_declared", validate_obj({"schema": "x", "a": "y"}, closed), True)
    check("open_key_permits_unknown", validate_obj({"schema": "x", "a": "y", "stray": 1}, open_), True)
    check("closed_key_true_permits_unknown",
          validate_obj({"schema": "x", "a": "y", "stray": 1}, dict(open_, additionalProperties=True)), True)
    # schema_field_names — single source the docs-no-re-list lint reads; absent schema -> None.
    fn = schema_field_names("apodictic.finding.v1")
    sfn_ok = (fn is not None and "severity" in fn and "evidence_refs" in fn
              and schema_field_names("apodictic.does_not_exist.v1") is None)
    check("schema_field_names", [] if sfn_ok else ["schema_field_names mismatch"], True)
    # parse_disposition_markers — the shared finding-disposition marker grammar (the SSoT both
    # run_gate.py and disposition_check.py import; docs/finding-dispositions.md §Schema 3).
    dm = parse_disposition_markers(
        "<!-- declined: F-P5-01 — reader intent is deliberate -->\n"
        "<!-- deferred: F-DP-02 until: beta reads back — waiting on reader signal -->")
    dm_ok = (len(dm) == 2
             and dm[0] == {"kind": "declined", "id": "F-P5-01", "trigger": None,
                           "reason": "reader intent is deliberate"}
             and dm[1] == {"kind": "deferred", "id": "F-DP-02", "trigger": "beta reads back",
                           "reason": "waiting on reader signal"})
    check("disposition_markers_pinned_forms", [] if dm_ok else ["parse mismatch: %r" % dm], True)
    # case-insensitive kind; en-dash reason separator accepted
    dm2 = parse_disposition_markers("<!-- DECLINED: F-P5-03 – held for voice -->")
    check("disposition_markers_case_insensitive",
          [] if (len(dm2) == 1 and dm2[0]["kind"] == "declined" and dm2[0]["id"] == "F-P5-03"
                 and dm2[0]["reason"] == "held for voice") else ["mismatch: %r" % dm2], True)
    # a comment that does not LEAD with an F-id is not a disposition marker (e.g. a docs example
    # deferring a work item by slug) — skipped, never honored
    check("disposition_markers_no_leading_id_skipped",
          [] if parse_disposition_markers(
              "<!-- deferred: orchestrator-pull-interface until later -->") == [] else ["not skipped"], True)
    # boundary-guarded id: F-P5-011 does not parse as F-P5-01 (the id is captured whole)
    dm3 = parse_disposition_markers("<!-- declined: F-P5-011 — x -->")
    check("disposition_markers_exact_boundary_id",
          [] if (len(dm3) == 1 and dm3[0]["id"] == "F-P5-011") else ["mismatch: %r" % dm3], True)
    # lenient parse, strict validation: a reason-less declined / trigger-less deferred still PARSES
    # (reason "" / trigger None) so DP0 / the write-time guard can refuse it by name
    dm4 = parse_disposition_markers("<!-- declined: F-P5-04 -->\n<!-- deferred: F-P5-05 — no trigger -->")
    check("disposition_markers_malformed_parse_for_refusal",
          [] if (len(dm4) == 2 and dm4[0]["reason"] == "" and dm4[1]["trigger"] is None) else
          ["mismatch: %r" % dm4], True)
    # code-span decoy: a marker quoted in a fenced documentation example is NOT live (stripping
    # goes through the override_marker SSoT — meta-linter M6)
    check("disposition_markers_codespan_decoy_rejected",
          [] if parse_disposition_markers(
              "```\n<!-- declined: F-P5-01 — decoy -->\n```\nprose") == [] else ["decoy honored"], True)
    # fid_re_lockstep — FID_RE is the single compiled id-token source; finding_trace._ID_RE and
    # regression_diff._ID_RE re-point to it, keeping byte-equal literals only as their art-less
    # degraded fallback. Pin all three patterns equal so the fallbacks cannot drift. Imported
    # locally (this module must stay dependency-free of both siblings — no top-level cycle).
    try:
        import finding_trace as _ft
        import regression_diff as _rd
        check("fid_re_lockstep",
              [] if FID_RE.pattern == _ft._ID_RE.pattern == _rd._ID_RE.pattern else
              ["pattern drift: art=%r ft=%r rd=%r"
               % (FID_RE.pattern, _ft._ID_RE.pattern, _rd._ID_RE.pattern)], True)
    except ImportError as e:  # a missing sibling would mask drift — fail loud, never skip
        check("fid_re_lockstep", ["sibling import failed: %s" % e], True)
    print("Self-test: %s" % ("PASS" if rc["v"] == 0 else "FAIL"))
    return rc["v"]


if __name__ == "__main__":
    sys.exit(run_self_test() if "--self-test" in sys.argv else 0)
