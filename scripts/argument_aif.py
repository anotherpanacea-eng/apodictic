#!/usr/bin/env python3
"""Deterministic, loss-aware Argument_State -> AIF-Core-subset export (R4B)."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
import apodictic_artifacts as artifacts  # noqa: E402
from override_marker import mask_code_spans  # noqa: E402

SCHEMA = "apodictic.aif-core-export.v1"
STATE_SCHEMA = "0.2.0"
NODE_TYPES = {"I-node", "RA-node", "CA-node"}
LOSS_CODES = {
    "CLAIM-LADDER-TOPOLOGY-UNDECLARED", "UNMAPPED-PA", "UNTYPED-OBJECTION",
    "UNRESOLVED-TARGET", "ALTERNATIVE-NO-CONFLICT-CRITERION",
    "ARGUMENT-WIDE-PROJECTED-TO-C0", "APODICTIC-METADATA",
    "OUT-OF-PROFILE-SECTION", "PREDRAFT-SUPERSEDED-BY-FINAL",
    "MISSING-SUPPORT-TOPOLOGY", "MISSING-WARRANT-TOPOLOGY",
    "FINAL-SECTION-INCOMPLETE", "SOURCE-ID-COLLISION",
}
BLOCKING = {"UNRESOLVED-TARGET", "FINAL-SECTION-INCOMPLETE", "SOURCE-ID-COLLISION"}
LOSS_DETAILS = {
    "CLAIM-LADDER-TOPOLOGY-UNDECLARED": "Argument_State declares no claim-ladder incidence; no RA-node was invented.",
    "UNMAPPED-PA": "No typed preference application is present; no PA-node was invented.",
    "UNTYPED-OBJECTION": "The objection has no complete Target/Relation pair; no CA-node was invented.",
    "UNRESOLVED-TARGET": "The typed objection target does not resolve under its declared relation.",
    "ALTERNATIVE-NO-CONFLICT-CRITERION": "The alternative declares no conflict criterion; no CA-node was invented.",
    "ARGUMENT-WIDE-PROJECTED-TO-C0": "The argument-wide target was projected to the C0 root.",
    "APODICTIC-METADATA": "APODICTIC metadata is not serialized as AIF graph semantics.",
    "OUT-OF-PROFILE-SECTION": "A populated Argument_State section is outside the AIF-Core subset profile.",
    "PREDRAFT-SUPERSEDED-BY-FINAL": "Final prose supersedes the corresponding pre-draft carrier population.",
    "MISSING-SUPPORT-TOPOLOGY": "No support topology is declared for the subclaim.",
    "MISSING-WARRANT-TOPOLOGY": "No warrant topology is declared for the subclaim.",
    "FINAL-SECTION-INCOMPLETE": "The final section began but lacks a complete record for the subclaim.",
    "SOURCE-ID-COLLISION": "Source-derived node IDs collide.",
}
LOSS_KEYS = {"code", "source_ref", "subject_id", "detail", "blocking"}
TOP_KEYS = {"schema", "source", "profile", "nodes", "edges", "losses"}
SOURCE_KEYS = {"artifact", "sha256", "argument_state_schema", "schema_version_basis"}
PROFILE_KEYS = {"name", "aif_reference", "loss_policy"}
CA_SCHEMES = {
    "WARRANT-DEFEATER": "apodictic:warrant-defeater",
    "CLAIM-CHALLENGE": "apodictic:claim-challenge",
    "EVIDENCE-CHALLENGE": "apodictic:evidence-challenge",
    "VALUE-CONFLICT": "apodictic:value-conflict",
}
SUPPORT_TYPES = {"REASON", "EXAMPLE", "DATA", "AUTHORITY", "EXPERIENCE"}
SCHEME_HINTS = {"AUTHORITY", "CONSEQUENCE", "CAUSAL", "ANALOGY", "EXAMPLE", "TESTIMONY", "PRACTICAL REASONING", "SIGN"}
WARRANT_STATUS = {"EXPLICIT", "RECOVERABLE", "MISSING", "CONTESTED"}
BACKING = {"PRESENT", "THIN", "ABSENT"}
QUALIFIER = {"MATCHED", "OVERCONFIDENT", "UNDERCLAIMED"}
_CID = re.compile(r"C\d+")
_ABS = re.compile(r"(?:^|[\s\"'])(?:/Users/|/home/|/private/tmp/|[A-Za-z]:\\)")
# Reserved machine-seeded placeholder vocabulary. The pre-draft seeder (argument_spine.py) and the
# Dialectical Clarity backfill mark a reserved-but-empty section with a fully-italic token whose inner
# text opens with one of these keywords: `_seeded_`, `_seeded by support_plan blocks_`, `_pending_`,
# `_pending — backfilled by Step 9 ..._`. Those are structural stubs, not authored content, so they
# must NOT disclose an out-of-profile loss. Every OTHER line — including arbitrary italic authored
# content such as `_smuggled real out-of-profile content_` — is real content that MUST disclose.
_PLACEHOLDER_KEYWORDS = ("seeded", "pending")
# Canonical key EMISSION order (mirrors build_export / _loss). run_check re-emits the parsed object in
# this order and compares bytes, so a key-reordered artifact fails even without --source (validate_export
# only checks membership via the order-blind *_KEYS sets). Kept beside those shape sets.
_ORDER_TOP = ("schema", "source", "profile", "nodes", "edges", "losses")
_ORDER_SOURCE = ("artifact", "sha256", "argument_state_schema", "schema_version_basis")
_ORDER_PROFILE = ("name", "aif_reference", "loss_policy")
_ORDER_NODE = {"I-node": ("id", "type", "text", "source_ref"),
               "RA-node": ("id", "type", "scheme", "scheme_text", "source_ref"),
               "CA-node": ("id", "type", "scheme", "source_ref")}
_ORDER_EDGE = ("from", "to")
_ORDER_LOSS = ("code", "source_ref", "subject_id", "detail", "blocking")


class ExportError(Exception):
    """A safe, bounded exporter failure class (never embeds source content or paths)."""


def _no_dupes(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate-key")
        out[key] = value
    return out


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def _canon_keys(order, d):
    """Re-key `d` into `order` (known keys first, in canonical order), appending any unknown keys in
    their original order so nothing is dropped — validate_export owns rejecting unknown keys."""
    out = {k: d[k] for k in order if k in d}
    for k in d:
        if k not in out:
            out[k] = d[k]
    return out


def _reorder_keys(obj):
    """Reconstruct a parsed export with keys in build_export's canonical emission order. A shape the
    validator has already rejected passes through untouched (the byte compare fails regardless)."""
    if not isinstance(obj, dict):
        return obj
    out = _canon_keys(_ORDER_TOP, obj)
    if isinstance(out.get("source"), dict):
        out["source"] = _canon_keys(_ORDER_SOURCE, out["source"])
    if isinstance(out.get("profile"), dict):
        out["profile"] = _canon_keys(_ORDER_PROFILE, out["profile"])
    if isinstance(out.get("nodes"), list):
        out["nodes"] = [_canon_keys(_ORDER_NODE.get(n.get("type"), ()), n) if isinstance(n, dict) else n
                        for n in out["nodes"]]
    if isinstance(out.get("edges"), list):
        out["edges"] = [_canon_keys(_ORDER_EDGE, e) if isinstance(e, dict) else e for e in out["edges"]]
    if isinstance(out.get("losses"), list):
        out["losses"] = [_canon_keys(_ORDER_LOSS, x) if isinstance(x, dict) else x for x in out["losses"]]
    return out


def _loss(code, source_ref, subject_id=None):
    return {"code": code, "source_ref": source_ref, "subject_id": subject_id,
            "detail": LOSS_DETAILS[code], "blocking": code in BLOCKING}


def _loss_key(item):
    return (item["code"], item["source_ref"], item["subject_id"] or "", item["detail"])


def _section(text, masked, number):
    pat = re.compile(r"(?m)^##\s+%d\.[^\n]*\n" % number)
    hits = list(pat.finditer(masked))
    if len(hits) > 1:
        raise ExportError("duplicate-section-heading")
    if not hits:
        return None
    start = hits[0].end()
    nxt = re.search(r"(?m)^##\s+(?:\d+\.|Pending\b)", masked[start:])
    end = start + nxt.start() if nxt else len(masked)
    return text[start:end], masked[start:end]


def _structural_mask(text):
    """Coordinate-preserving activity mask backed by the shared code-span state machine.

    The shared stripper decides what is inactive. Equal spans are projected back onto the
    original line coordinates; stripped spans become spaces. Consumers may therefore locate
    active syntax in this mask and slice verbatim values from ``text`` with the same offsets.
    """
    masked = mask_code_spans(text)
    if len(masked) != len(text):
        raise ExportError("structural-mask-invalid")
    return masked


def _load_carriers(text, masked):
    wanted = {"argument_spine", "support_plan", "warrant_plan"}
    out = {kind: [] for kind in wanted}
    active_blocks = []
    for match in artifacts.BLOCK_RE.finditer(masked):
        parsed = artifacts.parse_blocks(text[match.start():match.end()])
        if len(parsed) != 1:
            raise ExportError("carrier-json-invalid")
        active_blocks.append(parsed[0])
    for kind, obj, parse_error in active_blocks:
        if kind not in wanted:
            continue
        if parse_error or not isinstance(obj, dict):
            raise ExportError("carrier-json-invalid")
        schema_id = "apodictic.%s.v1" % kind
        schema = artifacts.load_schema(schema_id)
        errors = artifacts.validate_obj(obj, schema, where=kind)
        if schema is None or set(obj) - set((schema.get("properties") or {})):
            errors.append("closed-shape")
        if errors:
            raise ExportError("carrier-schema-invalid")
        out[kind].append(obj)
    return out


def _spine_data(spines):
    if not spines:
        return None
    if len(spines) != 1:
        raise ExportError("carrier-cardinality-invalid")
    spine = spines[0]
    claims = {"C0": spine["thesis"].strip()}
    if not claims["C0"]:
        raise ExportError("carrier-value-invalid")
    for raw in spine["subclaims"]:
        match = re.fullmatch(r"(C\d+):\s*(\S.*)", raw)
        if not match or match.group(1) in claims:
            raise ExportError("carrier-value-invalid")
        claims[match.group(1)] = match.group(2)
    return claims


def _final_claims(sec):
    if sec is None:
        return None, False
    text, masked = sec
    started = bool(re.search(r"(?m)^C0 \(main claim\):|^Subclaims:\s*$|^\s{2}C\d+:", masked))
    if not started:
        return None, False
    allowed_meta = {"Stakes", "Stakes type", "Key terms", "Fired codes"}
    claims, c0_seen = {}, False
    for line_match in re.finditer(r"(?m)^.*$", masked):
        line = line_match.group(0)
        if not line.strip() or line.strip() == "Subclaims:":
            continue
        m = re.fullmatch(r"C0 \(main claim\):[ \t]*?(.*)", line)
        if m:
            if c0_seen: raise ExportError("final-claim-duplicate")
            line_start = line_match.start()
            value = text[line_start + m.start(1):line_start + m.end(1)].strip()
            if not value: raise ExportError("final-claim-incomplete")
            claims["C0"], c0_seen = value, True; continue
        m = re.fullmatch(r"\s{2}(C\d+):[ \t]*?(.*)", line)
        if m:
            if m.group(1) in claims: raise ExportError("final-claim-duplicate")
            line_start = line_match.start()
            value = text[line_start + m.start(2):line_start + m.end(2)].strip()
            if not value: raise ExportError("final-claim-incomplete")
            claims[m.group(1)] = value; continue
        m = re.match(r"^([A-Za-z][A-Za-z ]+):", line)
        if m and m.group(1) not in allowed_meta:
            raise ExportError("final-claim-field-unknown")
    if "C0" not in claims or not any(cid != "C0" for cid in claims):
        raise ExportError("final-claim-incomplete")
    return claims, True


def _parse_record_fields(body_text, body_masked, allowed, required, enums, kind):
    fields = {}
    offset = 0
    for line in body_masked.splitlines(keepends=True):
        bare = line.rstrip("\r\n")
        if not bare.strip(): offset += len(line); continue
        m = re.fullmatch(r"[ \t]{2}([A-Za-z][A-Za-z ]*):[ \t]*?(.*)", bare)
        if not m:
            if bare.strip().startswith("_"): offset += len(line); continue
            raise ExportError("final-%s-line-invalid" % kind)
        key = m.group(1)
        value = body_text[offset + m.start(2):offset + m.end(2)].strip()
        if not value: raise ExportError("final-%s-record-incomplete" % kind)
        if key not in allowed: raise ExportError("final-%s-field-unknown" % kind)
        if key in fields: raise ExportError("final-%s-field-duplicate" % kind)
        if key in enums and value not in enums[key]: raise ExportError("final-%s-enum-invalid" % kind)
        fields[key] = value
        offset += len(line)
    if not required <= set(fields): raise ExportError("final-%s-record-incomplete" % kind)
    return fields


def _records(sec, kind):
    if sec is None: return None, False
    text, masked = sec
    if kind == "support":
        allowed = {"Support", "Support type", "Scheme hint", "Codes"}
        required = {"Support", "Support type"}
        enums = {"Support type": SUPPORT_TYPES, "Scheme hint": SCHEME_HINTS}
        projection = lambda f: {"support": f["Support"], "support_type": f["Support type"], "scheme_hint": f.get("Scheme hint")}
        token = r"Support(?: type)?|Scheme hint"
    else:
        allowed = {"Warrant", "Warrant status", "Backing", "Qualifier", "Defeater refs", "Codes"}
        required = {"Warrant", "Warrant status", "Backing", "Qualifier"}
        enums = {"Warrant status": WARRANT_STATUS, "Backing": BACKING, "Qualifier": QUALIFIER}
        projection = lambda f: {"warrant": f["Warrant"], "warrant_status": f["Warrant status"], "backing": f["Backing"], "qualifier": f["Qualifier"]}
        token = r"Warrant(?: status)?|Backing|Qualifier"
    started = bool(re.search(r"(?m)^\s{2}(?:%s):" % token, masked))
    if not started: return None, False
    heads = list(re.finditer(r"(?m)^(C\d+):[^\n]*\n", masked))
    if not heads: raise ExportError("final-%s-record-incomplete" % kind)
    out = {}
    for index, head in enumerate(heads):
        cid = head.group(1)
        if cid in out: raise ExportError("final-%s-record-duplicate" % kind)
        end = heads[index + 1].start() if index + 1 < len(heads) else len(masked)
        fields = _parse_record_fields(text[head.end():end], masked[head.end():end], allowed, required, enums, kind)
        out[cid] = projection(fields)
    return out, True


def _plan_map(plans, kind):
    out = {}
    for plan in plans:
        cid = plan["subclaim_id"]
        if cid in out: raise ExportError("carrier-id-duplicate")
        if kind == "support":
            out[cid] = {"support": plan["planned_support"], "support_type": plan["support_type"], "scheme_hint": plan.get("scheme_hint")}
        else:
            out[cid] = {k: plan[k] for k in ("warrant", "warrant_status", "backing", "qualifier")}
    return out


def _objections(sec):
    if sec is None: return []
    text, masked = sec
    heads = list(re.finditer(r"(?m)^Objection\s+(\d+)(?:[^:]*):[ \t]*?(.*)$", masked))
    out, seen = [], set()
    allowed = {"Target", "Relation", "Basis", "Condition", "Derivation anchors", "Engaged", "Quality"}
    for i, head in enumerate(heads):
        oid = "O" + head.group(1)
        if oid in seen: raise ExportError("objection-duplicate")
        seen.add(oid)
        objection_text = text[head.start(2):head.end(2)].strip()
        if not objection_text: raise ExportError("objection-incomplete")
        body_end = heads[i + 1].start() if i + 1 < len(heads) else len(masked)
        body_masked = masked[head.end():body_end]
        body_text = text[head.end():body_end]
        fields = {}
        for field in re.finditer(r"(?m)^[ \t]{2}([A-Za-z][A-Za-z ]*):[ \t]*?(.*)$", body_masked):
            key = field.group(1)
            value = body_text[field.start(2):field.end(2)].strip()
            if not value: raise ExportError("objection-incomplete")
            if key not in allowed: raise ExportError("objection-field-unknown")
            if key in fields: raise ExportError("objection-field-duplicate")
            fields[key] = value
        out.append({"id": oid, "text": objection_text, "fields": fields})
    return out


def _is_reserved_placeholder(line):
    """True for a reserved machine-seeded stub only: a fully-italic `_seeded…_` / `_pending…_` (or an
    empty `__`) marker, or a fully-bracketed `[…]` stub. ONLY these enumerated shapes count as
    unpopulated; every other line — including arbitrary italic authored content — is real content that
    must disclose a loss. Replaces the old `startswith('_')` heuristic that swallowed authored italics
    (`_smuggled real out-of-profile content_`) as if the section were an empty placeholder (R4B fix)."""
    if line.startswith("[") and line.endswith("]"):
        return True
    if len(line) >= 2 and line.startswith("_") and line.endswith("_"):
        inner = line[1:-1].strip().lower()
        return inner == "" or inner.split(" ", 1)[0] in _PLACEHOLDER_KEYWORDS
    return False


def _populated(sec):
    if sec is None: return False
    body = sec[1]
    lines = [x.strip() for x in body.splitlines() if x.strip()]
    return any(not _is_reserved_placeholder(x) for x in lines)


def build_export(source, *, artifact="Argument_State.md", state_schema=STATE_SCHEMA):
    if state_schema != STATE_SCHEMA: raise ExportError("state-schema-unsupported")
    raw = source if isinstance(source, bytes) else source.encode("utf-8")
    try: text = raw.decode("utf-8")
    except UnicodeDecodeError: raise ExportError("source-encoding-invalid")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    masked = _structural_mask(text)
    carriers = _load_carriers(text, masked)
    sections = {n: _section(text, masked, n) for n in range(1, 11)}
    spine_claims = _spine_data(carriers["argument_spine"])
    final_claims, claims_started = _final_claims(sections[2])
    claims_final = claims_started and (spine_claims is None or final_claims != spine_claims)
    claims = final_claims if claims_final else (spine_claims or final_claims)
    if not claims or "C0" not in claims: raise ExportError("claim-population-missing")
    subclaims = sorted((c for c in claims if c != "C0"), key=lambda x: int(x[1:]))
    final_support, support_started = _records(sections[3], "support")
    final_warrant, warrant_started = _records(sections[4], "warrant")
    plan_support = _plan_map(carriers["support_plan"], "support")
    plan_warrant = _plan_map(carriers["warrant_plan"], "warrant")
    declared = set(subclaims)
    populations = {
        "support-plan": set(plan_support), "warrant-plan": set(plan_warrant),
        "final-support": set(final_support or {}), "final-warrant": set(final_warrant or {}),
    }
    if any(ids - declared for ids in populations.values()):
        raise ExportError("subclaim-id-undeclared")
    support_final = support_started and (not plan_support or final_support != plan_support)
    warrant_final = warrant_started and (not plan_warrant or final_warrant != plan_warrant)
    supports = final_support if support_final else plan_support
    warrants = final_warrant if warrant_final else plan_warrant

    losses = [_loss("CLAIM-LADDER-TOPOLOGY-UNDECLARED", "§2")]
    if _populated(sections[5]): losses.append(_loss("UNMAPPED-PA", "§5"))
    for number in (1, 7, 8, 9, 10):
        if _populated(sections[number]): losses.append(_loss("OUT-OF-PROFILE-SECTION", "§%d" % number))
    if claims_started and re.search(r"(?m)^(?:Stakes|Stakes type|Key terms|Fired codes):", sections[2][1]):
        losses.append(_loss("APODICTIC-METADATA", "§2"))
    if spine_claims:
        losses.append(_loss("APODICTIC-METADATA", "predraft:argument_spine.v1", "argument_spine"))
    if claims_final and spine_claims: losses.append(_loss("PREDRAFT-SUPERSEDED-BY-FINAL", "§2", "argument_spine"))
    if support_final and plan_support: losses.append(_loss("PREDRAFT-SUPERSEDED-BY-FINAL", "§3", "support_plan"))
    if warrant_final and plan_warrant: losses.append(_loss("PREDRAFT-SUPERSEDED-BY-FINAL", "§4", "warrant_plan"))

    nodes = [{"id": "i:" + cid, "type": "I-node", "text": claims[cid], "source_ref": "§2 " + cid}
             for cid in sorted(claims, key=lambda x: int(x[1:]))]
    edges = []
    for cid in subclaims:
        support, warrant = supports.get(cid), warrants.get(cid)
        if support_final and not support: losses.append(_loss("FINAL-SECTION-INCOMPLETE", "§3 " + cid, cid))
        elif not support: losses.append(_loss("MISSING-SUPPORT-TOPOLOGY", "predraft:support_plan.v1:" + cid, cid))
        if warrant_final and not warrant: losses.append(_loss("FINAL-SECTION-INCOMPLETE", "§4 " + cid, cid))
        elif not warrant: losses.append(_loss("MISSING-WARRANT-TOPOLOGY", "predraft:warrant_plan.v1:" + cid, cid))
        if support: losses.append(_loss("APODICTIC-METADATA", ("§3 " if support_final else "predraft:support_plan.v1:") + cid, cid))
        if warrant: losses.append(_loss("APODICTIC-METADATA", ("§4 " if warrant_final else "predraft:warrant_plan.v1:") + cid, cid))
        if support and warrant:
            nodes.extend([
                {"id": "i:%s.support" % cid, "type": "I-node", "text": support["support"], "source_ref": ("§3 " if support_final else "predraft:support_plan.v1:") + cid},
                {"id": "s:RA:" + cid, "type": "RA-node", "scheme": "apodictic:warrant-application", "scheme_text": warrant["warrant"], "source_ref": ("§4 " if warrant_final else "predraft:warrant_plan.v1:") + cid},
            ])
            edges.extend([{"from": "i:%s.support" % cid, "to": "s:RA:" + cid}, {"from": "s:RA:" + cid, "to": "i:" + cid}])

    for objection in _objections(sections[6]):
        oid, fields = objection["id"], objection["fields"]
        nodes.append({"id": "i:" + oid, "type": "I-node", "text": objection["text"], "source_ref": "§6 " + oid})
        relation, target = fields.get("Relation"), fields.get("Target")
        if not relation or not target:
            losses.append(_loss("UNTYPED-OBJECTION", "§6 " + oid, oid)); continue
        if relation == "ALTERNATIVE":
            losses.append(_loss("ALTERNATIVE-NO-CONFLICT-CRITERION", "§6 " + oid, oid)); continue
        destination = None
        if target == "argument-wide":
            destination = "i:C0"; losses.append(_loss("ARGUMENT-WIDE-PROJECTED-TO-C0", "§6 " + oid, oid))
        elif re.fullmatch(r"C\d+\.warrant", target): destination = "s:RA:" + target.split(".")[0]
        elif re.fullmatch(r"C\d+\.support", target): destination = "i:" + target
        elif _CID.fullmatch(target): destination = "i:" + target
        ids = {node["id"] for node in nodes}
        if relation not in CA_SCHEMES or destination not in ids or (relation == "WARRANT-DEFEATER") != str(destination).startswith("s:RA:"):
            losses.append(_loss("UNRESOLVED-TARGET", "§6 " + oid, oid)); continue
        nodes.append({"id": "s:CA:" + oid, "type": "CA-node", "scheme": CA_SCHEMES[relation], "source_ref": "§6 " + oid})
        edges.extend([{"from": "i:" + oid, "to": "s:CA:" + oid}, {"from": "s:CA:" + oid, "to": destination}])
        if set(fields) & {"Basis", "Condition", "Derivation anchors", "Engaged", "Quality"}:
            losses.append(_loss("APODICTIC-METADATA", "§6 " + oid, oid))

    ids = [node["id"] for node in nodes]
    if len(ids) != len(set(ids)): losses.append(_loss("SOURCE-ID-COLLISION", "§2–§6"))
    losses = sorted({_loss_key(x): x for x in losses}.values(), key=_loss_key)
    nodes.sort(key=lambda x: x["id"]); edges.sort(key=lambda x: (x["from"], x["to"]))
    obj = {"schema": SCHEMA,
           "source": {"artifact": Path(artifact).name, "sha256": hashlib.sha256(raw).hexdigest(), "argument_state_schema": STATE_SCHEMA, "schema_version_basis": "operator-declared"},
           "profile": {"name": "aif-core-subset", "aif_reference": "AIF Specification, Definition 1.1", "loss_policy": "explicit"},
           "nodes": nodes, "edges": edges, "losses": losses}
    errors = validate_export(obj)
    if errors: raise ExportError("generated-export-invalid")
    if any(x["blocking"] for x in losses): raise ExportError("blocking-loss")
    return obj


def validate_export(obj):
    errors = []
    if not isinstance(obj, dict) or set(obj) != TOP_KEYS: return ["top-level closed shape"]
    if obj.get("schema") != SCHEMA: errors.append("schema literal")
    source, profile = obj.get("source"), obj.get("profile")
    if not isinstance(source, dict) or set(source) != SOURCE_KEYS: errors.append("source closed shape")
    else:
        if not isinstance(source["artifact"], str) or not source["artifact"] or Path(source["artifact"]).name != source["artifact"]: errors.append("source artifact")
        if not isinstance(source["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", source["sha256"]): errors.append("source sha256")
        if source["argument_state_schema"] != STATE_SCHEMA: errors.append("state schema literal")
        if source["schema_version_basis"] != "operator-declared": errors.append("schema basis literal")
    expected_profile = {"name": "aif-core-subset", "aif_reference": "AIF Specification, Definition 1.1", "loss_policy": "explicit"}
    if not isinstance(profile, dict) or set(profile) != PROFILE_KEYS: errors.append("profile closed shape")
    elif profile != expected_profile: errors.append("profile literals")
    nodes, edges, losses = obj.get("nodes"), obj.get("edges"), obj.get("losses")
    if not all(isinstance(x, list) for x in (nodes, edges, losses)): return errors + ["arrays required"]
    ids, types, schemes, node_shapes_ok = [], {}, {}, True
    for node in nodes:
        if not isinstance(node, dict): errors.append("node object"); node_shapes_ok = False; continue
        typ, keys = node.get("type"), set(node)
        wanted = {"id", "type", "text", "source_ref"} if typ == "I-node" else ({"id", "type", "scheme", "scheme_text", "source_ref"} if typ == "RA-node" else {"id", "type", "scheme", "source_ref"})
        if typ not in NODE_TYPES or keys != wanted: errors.append("node closed shape"); node_shapes_ok = False; continue
        nid = node["id"]
        id_ok = (typ == "I-node" and re.fullmatch(r"i:(?:C\d+(?:\.support)?|O\d+)", nid or "")) or (typ == "RA-node" and re.fullmatch(r"s:RA:C\d+", nid or "")) or (typ == "CA-node" and re.fullmatch(r"s:CA:O\d+", nid or ""))
        if not isinstance(nid, str) or not id_ok: errors.append("node id")
        if not isinstance(node["source_ref"], str) or not node["source_ref"]: errors.append("node source_ref")
        if typ == "I-node" and (not isinstance(node["text"], str) or not node["text"]): errors.append("I text")
        if typ == "RA-node" and (node["scheme"] != "apodictic:warrant-application" or not isinstance(node["scheme_text"], str) or not node["scheme_text"]): errors.append("RA schema")
        if typ == "CA-node" and node["scheme"] not in set(CA_SCHEMES.values()): errors.append("CA scheme")
        ids.append(nid); types[nid] = typ; schemes[nid] = node.get("scheme")
    if (node_shapes_ok and nodes != sorted(nodes, key=lambda x: x["id"])) or len(ids) != len(set(ids)): errors.append("node order/unique")
    pairs, edge_shapes_ok = [], True
    for edge in edges:
        if not isinstance(edge, dict) or set(edge) != {"from", "to"} or not all(isinstance(edge.get(k), str) for k in ("from", "to")):
            errors.append("edge closed shape"); edge_shapes_ok = False; continue
        a, b = edge["from"], edge["to"]; pairs.append((a, b))
        if a not in types or b not in types: errors.append("dangling edge"); continue
        if (types[a], types[b]) not in {("I-node", "RA-node"), ("RA-node", "I-node"), ("I-node", "CA-node"), ("CA-node", "I-node"), ("CA-node", "RA-node")}: errors.append("edge direction")
    if (edge_shapes_ok and edges != sorted(edges, key=lambda x: (x["from"], x["to"]))) or len(pairs) != len(set(pairs)): errors.append("edge order/unique")
    for nid, typ in types.items():
        incoming = [a for a, b in pairs if b == nid]; outgoing = [b for a, b in pairs if a == nid]
        if typ == "RA-node" and (not any(types.get(x) == "I-node" for x in incoming) or any(types.get(x) not in {"I-node", "CA-node"} for x in incoming) or len(outgoing) != 1 or types.get(outgoing[0]) != "I-node"): errors.append("RA incidence " + nid)
        if typ == "CA-node":
            dest_type = types.get(outgoing[0]) if len(outgoing) == 1 else None
            expected_dest = "RA-node" if schemes.get(nid) == CA_SCHEMES["WARRANT-DEFEATER"] else "I-node"
            if len(incoming) != 1 or types.get(incoming[0]) != "I-node" or len(outgoing) != 1 or dest_type != expected_dest: errors.append("CA incidence " + nid)
    loss_keys, loss_shapes_ok = [], True
    for item in losses:
        if not isinstance(item, dict) or set(item) != LOSS_KEYS: errors.append("loss closed shape"); loss_shapes_ok = False; continue
        code = item.get("code")
        if code not in LOSS_CODES or item.get("blocking") != (code in BLOCKING): errors.append("loss enum/blocking")
        if code in LOSS_DETAILS and item.get("detail") != LOSS_DETAILS[code]: errors.append("loss detail")
        if not isinstance(item.get("source_ref"), str) or not item["source_ref"] or (item.get("subject_id") is not None and (not isinstance(item["subject_id"], str) or not item["subject_id"])): errors.append("loss fields")
        loss_keys.append(_loss_key(item))
    if (loss_shapes_ok and losses != sorted(losses, key=_loss_key)) or len(loss_keys) != len(set(loss_keys)): errors.append("loss order/unique")
    if any(x.get("blocking") for x in losses if isinstance(x, dict)): errors.append("blocking loss stored")
    meta = copy.deepcopy(obj)
    for node in meta.get("nodes", []):
        if isinstance(node, dict): node.pop("text", None); node.pop("scheme_text", None)
    if _ABS.search(json.dumps(meta, ensure_ascii=False)): errors.append("generated path leakage")
    return errors


def atomic_write(path, data):
    target = Path(path)
    fd, temp = tempfile.mkstemp(prefix="." + target.name + ".", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.replace(temp, target)
    except Exception:
        try: os.unlink(temp)
        except OSError: pass
        raise


def run_check(path, source=None):
    try: raw = Path(path).read_bytes()
    except OSError: print("argument-aif-check: FAIL [artifact-read]"); return 1
    try: text = raw.decode("utf-8"); obj = json.loads(text, object_pairs_hook=_no_dupes)
    except (UnicodeError, ValueError, json.JSONDecodeError): print("argument-aif-check: FAIL [artifact-json]"); return 1
    errors = validate_export(obj)
    # Byte-canonicality: sourceless too. The first compare catches indentation/whitespace/encoding
    # drift; `sort_keys=False` preserves the parsed key order, so a key-reordered-but-otherwise-canonical
    # artifact slips past it — the elif re-emits in the canonical key order and re-compares, so a
    # reordered artifact fails even without --source. (Loss-set completeness still needs the source.)
    if canonical(obj).encode("utf-8") != raw: errors.append("non-canonical JSON bytes")
    elif canonical(_reorder_keys(obj)).encode("utf-8") != raw: errors.append("non-canonical key order")
    if source:
        src_obj = obj.get("source") if isinstance(obj, dict) else None
        recorded = src_obj.get("artifact") if isinstance(src_obj, dict) else None
        # Bind the export's self-attested artifact name to the supplied source. The rebuild adopts
        # `recorded`, so without this an arbitrary/tampered basename would ride through (the sha256 is
        # recomputed, so it is cosmetic provenance — but bind it so a mislabeled export cannot claim a
        # clean source-closure check).
        if not isinstance(recorded, str) or Path(recorded).name != Path(source).name:
            errors.append("source artifact basename mismatch")
        else:
            try: source_raw = Path(source).read_bytes(); rebuilt = build_export(source_raw, artifact=recorded, state_schema=src_obj.get("argument_state_schema"))
            except (OSError, ExportError): errors.append("source rebuild")
            else:
                if canonical(rebuilt).encode("utf-8") != raw: errors.append("source-derived byte closure")
    if errors:
        print("argument-aif-check: FAIL (%d)" % len(errors)); [print("  - " + x) for x in errors]; return 1
    print("argument-aif-check: PASS — %d nodes, %d edges, %d disclosed losses" % (len(obj["nodes"]), len(obj["edges"]), len(obj["losses"]))); return 0


def selftest():
    final = '''## 2. Claim Architecture\nC0 (main claim): root /Users/authored/path\n\nSubclaims:\n  C1: one\n\n## 3. Support Map\nC1: one\n  Support: because evidence\n  Support type: DATA\n  Scheme hint: SIGN\n\n## 4. Warrant and Inference Map\nC1: one\n  Warrant: evidence bears on the claim\n  Warrant status: EXPLICIT\n  Backing: PRESENT\n  Qualifier: MATCHED\n\n## 5. Burden, Scope, and Comparative Assessment\nClaim scope: LOCAL\n\n## 6. Objection and Dialectical Integrity Map\nObjection 1: unless the sample is biased\n  Target: C1.warrant\n  Relation: WARRANT-DEFEATER\n  Basis: IMPORTED\n'''
    failures, arms = [], []
    def check(name, condition):
        arms.append(name)
        if not condition: failures.append(name)
    obj = build_export(final.encode())
    check("support", any(n["id"] == "i:C1.support" for n in obj["nodes"]))
    check("CA attacks RA", {"from": "s:CA:O1", "to": "s:RA:C1"} in obj["edges"])
    check("authored path", "/Users/authored/path" in canonical(obj))
    for name, mutate in [
        ("bad CA scheme", lambda x: next(n for n in x["nodes"] if n["type"] == "CA-node").update({"scheme": "bad"})),
        ("wrong CA destination", lambda x: next(e for e in x["edges"] if e["from"].startswith("s:CA:")).update({"to": "i:C1"})),
        ("bad profile", lambda x: x["profile"].update({"loss_policy": "maybe"})),
        ("altered loss detail", lambda x: x["losses"][0].update({"detail": "changed"})),
    ]:
        bad = copy.deepcopy(obj); mutate(bad); check(name, bool(validate_export(bad)))
    fenced = "```md\n" + final + "\n```\n" + final
    check("fence-aware", build_export(fenced.encode())["source"]["sha256"] == hashlib.sha256(fenced.encode()).hexdigest())
    crlf = final.replace("\n", "\r\n").encode(); lf = final.encode()
    check("raw-byte sha", build_export(crlf)["source"]["sha256"] != build_export(lf)["source"]["sha256"])
    section_ten = build_export((final + "\n## 10. Audit Trail\nResearch disposition: retained\n").encode())
    check("section 10 loss", any(x["code"] == "OUT-OF-PROFILE-SECTION" and x["source_ref"] == "§10" for x in section_ten["losses"]))
    inline = (final.replace("root /Users/authored/path", "root `claim` verbatim")
              .replace("because evidence", "because `support` verbatim")
              .replace("evidence bears on the claim", "`warrant` bears verbatim")
              .replace("unless the sample is biased", "unless `objection` verbatim"))
    inline_obj = build_export(inline.encode())
    rendered = canonical(inline_obj)
    check("inline values verbatim", all(value in rendered for value in
          ("root `claim` verbatim", "because `support` verbatim", "`warrant` bears verbatim", "unless `objection` verbatim")))
    carrier = '''<!-- apodictic:argument_spine\n{"schema":"apodictic.argument_spine.v1","form":"policy `brief`","goal":"persuade","argument_type":"AT1","burden_level":"MEDIUM","audience_expertise":"MIXED","audience_receptivity":"MIXED","thesis":"keep `carrier value` verbatim","subclaims":["C1: one"],"anti_thesis":"no"}\n-->'''
    carrier_obj = build_export(carrier.encode())
    check("inline carrier value verbatim", next(n for n in carrier_obj["nodes"] if n["id"] == "i:C0")["text"] == "keep `carrier value` verbatim")
    multiline_decoy = ("quote `opens here\n## 2. Claim Architecture\n"
                       "C0 (main claim): decoy claim\nSubclaims:\n  C99: decoy subclaim\n"
                       "and closes here` outside\n" + final)
    decoy_obj = build_export(multiline_decoy.encode())
    check("multiline inline heading decoy",
          next(n for n in decoy_obj["nodes"] if n["id"] == "i:C0")["text"] == "root /Users/authored/path"
          and not any(n["id"] == "i:C99" for n in decoy_obj["nodes"]))
    incomplete = final.replace("  Support type: DATA\n", "")
    try: build_export(incomplete.encode()); raised = False
    except ExportError: raised = True
    check("incomplete final", raised)
    # final-support-enum-invalid: a §3 support record with an out-of-enum Support type must fail at build.
    bad_support = final.replace("  Support type: DATA\n", "  Support type: VIBES\n")
    try: build_export(bad_support.encode()); enum_raised = False
    except ExportError as exc: enum_raised = str(exc) == "final-support-enum-invalid"
    check("final-support-enum-invalid", enum_raised)
    # Out-of-profile under-disclosure (R4B): authored italic content in an out-of-profile section is
    # disclosed, while a genuinely-seeded `_seeded…_` stub is NOT (no false OUT-OF-PROFILE loss).
    smuggled = build_export((final + "\n## 7. Out Of Profile\n_smuggled real out-of-profile content_\n").encode())
    check("out-of-profile italic authored content discloses loss",
          any(x["code"] == "OUT-OF-PROFILE-SECTION" and x["source_ref"] == "§7" for x in smuggled["losses"]))
    seeded_stub = build_export((final + "\n## 7. Out Of Profile\n_seeded by argument_spine_\n").encode())
    check("reserved placeholder stays unpopulated",
          not any(x["code"] == "OUT-OF-PROFILE-SECTION" and x["source_ref"] == "§7" for x in seeded_stub["losses"]))
    if failures:
        print("Self-test: FAIL"); [print("  - " + x) for x in failures]; return 1
    print("Self-test: PASS (argument-aif; %d focused arms)" % len(arms)); return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ["--self-test"]: return selftest()
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="cmd", required=True)
    export = sub.add_parser("export"); export.add_argument("source"); export.add_argument("--state-schema", required=True); export.add_argument("--out"); export.add_argument("--strict", action="store_true")
    check = sub.add_parser("check"); check.add_argument("artifact"); check.add_argument("--source")
    args = parser.parse_args(argv)
    if args.cmd == "check": return run_check(args.artifact, args.source)
    try:
        raw = Path(args.source).read_bytes(); obj = build_export(raw, artifact=Path(args.source).name, state_schema=args.state_schema)
        if args.strict and obj["losses"]: raise ExportError("strict-loss")
        data = canonical(obj)
        if args.out: atomic_write(args.out, data)
        else: sys.stdout.write(data)
        return 0
    except OSError:
        print("argument-aif-export: FAIL [source-read]", file=sys.stderr); return 1
    except ExportError as exc:
        print("argument-aif-export: FAIL [%s]" % str(exc), file=sys.stderr); return 1


if __name__ == "__main__":
    sys.exit(main())
