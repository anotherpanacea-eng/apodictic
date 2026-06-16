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

# One grammar for the embedded block carrier, shared by every validator. We match the
# CARRIER (`<!-- apodictic:<type> ... -->`) first and capture the whole payload up to the
# closing `-->`, rather than only comments that already contain a complete `{...}`. A broken
# payload (e.g. a missing closing brace) is then surfaced as a JSON error by parse_blocks
# instead of disappearing before validation.
BLOCK_RE = re.compile(r"<!--\s*apodictic:([A-Za-z_]+)\s*(.*?)\s*-->", re.DOTALL)

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
    print("Self-test: %s" % ("PASS" if rc["v"] == 0 else "FAIL"))
    return rc["v"]


if __name__ == "__main__":
    sys.exit(run_self_test() if "--self-test" in sys.argv else 0)
