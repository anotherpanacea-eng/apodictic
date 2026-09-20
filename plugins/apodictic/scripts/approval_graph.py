#!/usr/bin/env python3
"""Approval-gated reconstruction ledger and deterministic projections.

This module intentionally has no third-party dependencies.  The ledger is the
authority; the Markdown graph and session file are rebuilt views.  The public
functions in this file are the Increment 1 API.  The implementation is kept in
one file because the same bytes are installed in the repository mirror.
"""

from __future__ import annotations

import argparse
import copy
import errno
import hashlib
from functools import wraps
import json
import math
import os
import re
import sys
import tempfile
import threading
import unicodedata
from pathlib import Path
from typing import Any, Iterable

try:
    import fcntl  # type: ignore
except ImportError:  # pragma: no cover - Windows
    fcntl = None
try:
    import msvcrt  # type: ignore
except ImportError:  # pragma: no cover - POSIX
    msvcrt = None


HEX64 = re.compile(r"^[0-9a-f]{64}$")
RID = re.compile(r"^[ne]-[0-9a-f]{12}$")
NID = re.compile(r"^n-[0-9a-f]{12}$")
EID = re.compile(r"^e-[0-9a-f]{12}$")
TS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
STATE_ID = re.compile(r"^Argument_State_v[1-9][0-9]*$")
LOCAL_REF = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*$")
SPLIT_REF = re.compile(r"^SPLIT ([1-9][0-9]*)/([1-9][0-9]*)$")
VIOLATION = re.compile(r"^x-[0-9]{2,}$")
VERSION = re.compile(r"^v[1-9][0-9]*$")

NODE_TYPES = {"CLAIM", "SUPPORT", "WARRANT", "QUALIFIER", "DEFINITION", "STAKES", "OBJECTION", "VIGNETTE"}
EDGE_TYPES = {"SUPPORTS", "WARRANTS", "QUALIFIES", "DEPENDS-ON", "DEFINES", "TARGETS", "ATTACHED-TO"}
SHAPES = {"MINT", "DECISION", "REVISE", "RECONCILE", "QUARANTINE"}
APPROVALS = {"PENDING", "APPROVED", "REJECTED", "SUPERSEDED"}
PRESENCE = {"CURRENT", "ORPHANED"}
INCLUSIONS = {"REQUIRED", "OPTIONAL"}
ACTORS = {"normalizer", "author", "system", "reconciliation"}
EVENTS = {"MINTED", "DECISION", "UNREJECT", "WITHDRAWAL", "INCLUSION", "REVISE", "CASCADE", "RECONCILE"}

TOP_KEYS = ("shape", "prev_hash", "timestamp", "context", "events", "bundle_hash")
EVENT_KEYS = ("event", "actor", "record_id", "related_record_id", "content", "approval_from", "approval_to",
              "presence_from", "presence_to", "inclusion_from", "inclusion_to", "reason", "note")
CONTEXT_KEYS = {
    "source": ("source_filename", "source_sha256", "argument_state"),
    "draft": ("draft_version", "draft_sha256"),
}


class ApprovalGraphError(Exception):
    """Stable public error carrying whether a proposed append committed."""

    def __init__(self, code: str, message: str, committed: bool | None = False, record_id: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.committed = committed
        self.record_id = record_id


def _err(code: str, message: str, record_id: str | None = None) -> ApprovalGraphError:
    return ApprovalGraphError(code, message, False, record_id)


def _nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def _validate_json_value(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise _err("NONFINITE-NUMBER", f"non-finite number at {path}")
        return
    if isinstance(value, list):
        for i, item in enumerate(value):
            _validate_json_value(item, f"{path}[{i}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise _err("UNSUPPORTED-VALUE", f"non-string key at {path}")
            if not key.isascii() or not key:
                raise _err("UNSUPPORTED-VALUE", f"invalid object key at {path}")
            _validate_json_value(item, f"{path}.{key}")
        return
    raise _err("UNSUPPORTED-VALUE", f"unsupported value at {path}")


def _nfc_copy(value: Any) -> Any:
    if isinstance(value, str):
        return _nfc(value)
    if isinstance(value, list):
        return [_nfc_copy(v) for v in value]
    if isinstance(value, dict):
        return {k: _nfc_copy(v) for k, v in value.items()}
    return value


def canonical_json(value: Any) -> str:
    """Return compact UTF-8-compatible canonical JSON without a trailing LF.

    Dict insertion order is preserved: schema builders supply the grammar-fixed
    order.  Strings are NFC-normalized recursively and non-finite/unsupported
    values are rejected.
    """
    _validate_json_value(value)
    try:
        return json.dumps(_nfc_copy(value), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise _err("UNSUPPORTED-VALUE", str(exc)) from exc


def _collapse(text: str) -> str:
    return " ".join(_nfc(text).split())


def _rid(value: Any, kind: str | None = None) -> str:
    if not isinstance(value, str) or not RID.fullmatch(value):
        raise _err("INVALID-RECORD-ID", f"invalid record id {value!r}")
    if kind == "node" and not NID.fullmatch(value):
        raise _err("INVALID-RECORD-ID", f"expected node id: {value}")
    if kind == "edge" and not EID.fullmatch(value):
        raise _err("INVALID-RECORD-ID", f"expected edge id: {value}")
    return value


def node_id(node_type: str, text: str) -> str:
    if not isinstance(node_type, str) or not isinstance(text, str):
        raise _err("INVALID-NODE-CONTENT", "node type and text must be strings")
    if node_type not in NODE_TYPES:
        raise _err("INVALID-NODE-TYPE", f"unknown node type {node_type!r}")
    material = _nfc(node_type) + "\n" + _collapse(text)
    return "n-" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:12]


def _typing_value(carried_typing: Any) -> str:
    if isinstance(carried_typing, dict):
        if set(carried_typing) != {"relation", "basis", "condition"}:
            raise _err("INVALID-CARRIED-TYPING", "typed TARGETS requires relation, basis, condition")
        if not all(isinstance(carried_typing[key], str) for key in ("relation", "basis", "condition")):
            raise _err("INVALID-CARRIED-TYPING", "typed TARGETS values must be strings")
        relation = _collapse(carried_typing["relation"]).upper()
        basis = _collapse(carried_typing["basis"])
        condition = _collapse(carried_typing["condition"])
        if not relation or not basis:
            raise _err("INVALID-CARRIED-TYPING", "relation and basis are required")
        if not condition:
            condition = "NONE"
        return canonical_json({"relation": relation, "basis": basis, "condition": condition})
    if not isinstance(carried_typing, str):
        raise _err("INVALID-CARRIED-TYPING", "carried typing must be a string or typed object")
    return _nfc(carried_typing)


def edge_id(edge_type: str, source: str, target: str, carried_typing: str) -> str:
    if edge_type not in EDGE_TYPES:
        raise _err("INVALID-EDGE-TYPE", f"unknown edge type {edge_type!r}")
    _rid(source, "node")
    _rid(target, "node")
    if edge_type != "TARGETS" and carried_typing != "—":
        raise _err("INVALID-CARRIED-TYPING", "non-TARGETS edges use literal —")
    if edge_type == "TARGETS" and carried_typing not in {"NONE (legacy-untyped)"}:
        try:
            parsed = json.loads(carried_typing) if isinstance(carried_typing, str) else carried_typing
            carried_typing = _typing_value(parsed)
        except json.JSONDecodeError as exc:
            raise _err("INVALID-CARRIED-TYPING", "typed TARGETS carried typing is not canonical JSON") from exc
    material = _nfc(edge_type) + "\n" + source + "\n" + target + "\n" + _nfc(carried_typing)
    return "e-" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:12]


def _timestamp(value: Any) -> str:
    if not isinstance(value, str) or not TS.fullmatch(value):
        raise _err("INVALID-TIMESTAMP", f"invalid UTC timestamp {value!r}")
    # datetime is deliberately avoided to keep parsing deterministic without timezone assumptions.
    import datetime
    try:
        datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise _err("INVALID-TIMESTAMP", f"invalid UTC timestamp {value!r}") from exc
    return value


def _hex(value: Any, name: str) -> str:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise _err("INVALID-HASH", f"{name} must be 64 lowercase hex characters")
    return value


def _context(context: Any, kind: str) -> dict[str, str] | None:
    if kind in {"DECISION", "REVISE"}:
        if context is not None:
            raise _err("INVALID-CONTEXT", f"{kind} context must be null")
        return None
    if not isinstance(context, dict):
        raise _err("INVALID-CONTEXT", f"{kind} context must be an object")
    expected = CONTEXT_KEYS["draft" if kind == "QUARANTINE" else "source"]
    if tuple(context.keys()) != expected:
        raise _err("UNKNOWN-KEY", f"context keys must be {expected}")
    if kind == "QUARANTINE":
        version = context["draft_version"]
        if not isinstance(version, str) or not VERSION.fullmatch(version):
            raise _err("INVALID-DRAFT-VERSION", "invalid draft version")
        return {"draft_version": version, "draft_sha256": _hex(context["draft_sha256"], "draft_sha256")}
    filename = context["source_filename"]
    if not isinstance(filename, str) or not filename or "\x00" in filename:
        raise _err("INVALID-SOURCE-PATH", "invalid source filename")
    if os.path.isabs(filename) or Path(filename).drive or any(part == ".." for part in Path(filename).parts):
        raise _err("INVALID-SOURCE-PATH", "source filename must be project-relative")
    state = context["argument_state"]
    if not isinstance(state, str) or not STATE_ID.fullmatch(state):
        raise _err("INVALID-ARGUMENT-STATE", "invalid Argument State identity")
    return {"source_filename": _nfc(filename), "source_sha256": _hex(context["source_sha256"], "source_sha256"), "argument_state": state}


def _anchor(anchor: Any) -> dict[str, str]:
    if not isinstance(anchor, dict) or tuple(anchor.keys()) != ("quote", "location"):
        raise _err("INVALID-ANCHOR", "anchor keys must be quote, location")
    if not isinstance(anchor["quote"], str) or not isinstance(anchor["location"], str):
        raise _err("INVALID-ANCHOR", "anchor quote/location must be strings")
    if not _collapse(anchor["quote"]):
        raise _err("INVALID-ANCHOR", "anchor quote must contain non-whitespace text")
    return {"quote": _nfc(anchor["quote"]), "location": _nfc(anchor["location"])}


def _provenance_entry(value: Any) -> str:
    if not isinstance(value, str):
        raise _err("INVALID-PROVENANCE", "provenance entries must be strings")
    if value.startswith("STATE:"):
        rest = value[6:]
        parts = rest.split(":")
        if len(parts) not in (2, 3) or not STATE_ID.fullmatch(parts[0]) or not LOCAL_REF.fullmatch(parts[1]):
            raise _err("INVALID-PROVENANCE", f"invalid STATE provenance {value!r}")
        if len(parts) == 3:
            match = re.fullmatch(r"SPLIT ([1-9][0-9]*)/([1-9][0-9]*)", parts[2])
            if match is None or int(match.group(1)) > int(match.group(2)):
                raise _err("INVALID-PROVENANCE", f"invalid SPLIT provenance {value!r}")
        return value
    if value.startswith("AUTHOR-REVISION:"):
        _rid(value.split(":", 1)[1], "node")
        return value
    if value.startswith("QUARANTINE:"):
        parts = value.split(":")
        if len(parts) != 3 or not VERSION.fullmatch(parts[1]) or not VIOLATION.fullmatch(parts[2]):
            raise _err("INVALID-PROVENANCE", f"invalid QUARANTINE provenance {value!r}")
        return value
    raise _err("INVALID-PROVENANCE", f"invalid provenance {value!r}")


def _flags(value: Any) -> list[str]:
    if not isinstance(value, list) or not value or any(not isinstance(v, str) for v in value):
        raise _err("INVALID-FLAGS", "flags must be a nonempty string array")
    vals = sorted({_nfc(v) for v in value})
    if "NONE" in vals and vals != ["NONE"]:
        raise _err("INVALID-FLAGS", "NONE is only legal as the sole flag")
    return vals


def _node_content(content: Any, origin_kind: str | None = None) -> dict[str, Any]:
    if not isinstance(content, dict) or tuple(content.keys()) != ("type", "text", "anchors", "origin", "provenance", "flags"):
        raise _err("INVALID-MINT-CONTENT", "node content keys are not canonical")
    typ, text, anchors, origin, provenance, flags = (content[k] for k in content)
    if typ not in NODE_TYPES or not isinstance(text, str):
        raise _err("INVALID-NODE-CONTENT", "invalid node type or text")
    if not isinstance(anchors, list) or any(not isinstance(a, dict) for a in anchors):
        raise _err("INVALID-ANCHOR", "anchors must be an array")
    anchors = [_anchor(a) for a in anchors]
    if not isinstance(origin, str) or not isinstance(provenance, list):
        raise _err("INVALID-NODE-CONTENT", "invalid origin/provenance")
    provenance = [_provenance_entry(p) for p in provenance]
    flags = _flags(flags)
    if origin == "MANUSCRIPT":
        if not anchors or not provenance or not all(p.startswith("STATE:") for p in provenance):
            raise _err("INVALID-MINT-CONTENT", "MANUSCRIPT requires anchors and STATE provenance")
    elif origin.startswith("AUTHOR-REVISION (of ") and origin.endswith(")"):
        original = origin[20:-1]
        _rid(original, "node")
        if anchors or provenance != [f"AUTHOR-REVISION:{original}"] or flags != ["NONE"]:
            raise _err("INVALID-MINT-CONTENT", "invalid AUTHOR-REVISION origin closure")
    elif origin.startswith("QUARANTINE (draft ") and origin.endswith(")"):
        version = origin[len("QUARANTINE (draft "):-1]
        if not VERSION.fullmatch(version) or anchors or flags != ["NONE"]:
            raise _err("INVALID-MINT-CONTENT", "invalid QUARANTINE origin closure")
        if len(provenance) != 1 or not provenance[0].startswith(f"QUARANTINE:{version}:"):
            raise _err("INVALID-MINT-CONTENT", "invalid QUARANTINE provenance closure")
    else:
        raise _err("INVALID-MINT-CONTENT", "unknown node origin")
    if origin_kind and origin_kind != origin:
        raise _err("INVALID-MINT-CONTENT", "origin does not match bundle shape")
    return {"type": typ, "text": _nfc(text), "anchors": anchors, "origin": origin, "provenance": provenance, "flags": flags}


def _edge_content(content: Any) -> dict[str, Any]:
    if not isinstance(content, dict) or tuple(content.keys()) != ("type", "source", "target", "carried_typing"):
        raise _err("INVALID-MINT-CONTENT", "edge content keys are not canonical")
    typ, source, target, typing = (content[k] for k in content)
    if typ not in EDGE_TYPES:
        raise _err("INVALID-EDGE-CONTENT", "invalid edge type")
    _rid(source, "node"); _rid(target, "node")
    if not isinstance(typing, str):
        raise _err("INVALID-CARRIED-TYPING", "carried typing must be a string")
    typing = _typing_value(typing) if typ == "TARGETS" and typing != "NONE (legacy-untyped)" else typing
    if typ != "TARGETS" and typing != "—":
        raise _err("INVALID-CARRIED-TYPING", "non-TARGETS edge typing must be —")
    if typ == "TARGETS" and typing != "NONE (legacy-untyped)" and not typing.startswith("{"):
        raise _err("INVALID-CARRIED-TYPING", "TARGETS typing must be typed JSON or legacy marker")
    return {"type": typ, "source": source, "target": target, "carried_typing": typing}


def _refresh_content(content: Any) -> dict[str, Any]:
    if not isinstance(content, dict) or tuple(content.keys()) != ("anchors", "flags"):
        raise _err("INVALID-RECONCILE-CONTENT", "refresh content must contain anchors and flags")
    if not isinstance(content["anchors"], list):
        raise _err("INVALID-RECONCILE-CONTENT", "refresh anchors must be an array")
    return {"anchors": [_anchor(a) for a in content["anchors"]], "flags": _flags(content["flags"])}


def _event(event: Any) -> dict[str, Any]:
    if not isinstance(event, dict) or tuple(event.keys()) != EVENT_KEYS:
        raise _err("UNKNOWN-KEY", "event keys are not canonical")
    for key in ("event", "actor"):
        if not isinstance(event[key], str):
            raise _err("INVALID-EVENT", f"event {key} must be string")
    if event["event"] not in EVENTS or event["actor"] not in ACTORS:
        raise _err("INVALID-EVENT", "unknown event or actor")
    _rid(event["record_id"])
    if event["related_record_id"] is not None:
        _rid(event["related_record_id"], "node")
    for key in ("approval_from", "approval_to"):
        if event[key] is not None and (not isinstance(event[key], str) or event[key] not in APPROVALS):
            raise _err("INVALID-STATE", f"invalid {key}")
    for key in ("presence_from", "presence_to"):
        if event[key] is not None and (not isinstance(event[key], str) or event[key] not in PRESENCE):
            raise _err("INVALID-STATE", f"invalid {key}")
    for key in ("inclusion_from", "inclusion_to"):
        if event[key] is not None and (not isinstance(event[key], str) or event[key] not in INCLUSIONS):
            raise _err("INVALID-STATE", f"invalid {key}")
    if event["reason"] is not None and (not isinstance(event["reason"], str) or not event["reason"]):
        raise _err("INVALID-REASON", "reason must be null or nonempty string")
    if event["note"] is not None and not isinstance(event["note"], str):
        raise _err("INVALID-NOTE", "note must be null or string")
    return copy.deepcopy(event)


def _bundle_without_hash(bundle: Any) -> dict[str, Any]:
    if not isinstance(bundle, dict) or tuple(bundle.keys()) not in (TOP_KEYS[:-1], TOP_KEYS):
        raise _err("INVALID-BUNDLE", "bundle keys are not canonical")
    shape = bundle["shape"]
    if not isinstance(shape, str) or shape not in SHAPES:
        raise _err("INVALID-BUNDLE", f"unknown bundle shape {shape!r}")
    prev = bundle["prev_hash"]
    if prev != "GENESIS":
        _hex(prev, "prev_hash")
    timestamp = _timestamp(bundle["timestamp"])
    context = _context(bundle["context"], shape)
    events = bundle["events"]
    if not isinstance(events, list) or not events:
        raise _err("INVALID-BUNDLE", "events must be a nonempty array")
    events = [_event(e) for e in events]
    result = {"shape": shape, "prev_hash": prev, "timestamp": timestamp, "context": context, "events": events}
    if tuple(bundle.keys()) == TOP_KEYS:
        stored = bundle["bundle_hash"]
        _hex(stored, "bundle_hash")
        expected = hashlib.sha256(canonical_json(result).encode("utf-8")).hexdigest()
        if stored != expected:
            raise _err("BUNDLE-HASH-MISMATCH", "stored bundle_hash does not match canonical bundle")
        result["bundle_hash"] = stored
    return result


def seal_bundle(bundle_without_hash: dict) -> dict:
    """Return a fresh canonical bundle with its final SHA-256 hash."""
    base = _bundle_without_hash(bundle_without_hash)
    if "bundle_hash" in base:
        base.pop("bundle_hash")
    result = {k: base[k] for k in TOP_KEYS[:-1]}
    result["bundle_hash"] = hashlib.sha256(canonical_json(result).encode("utf-8")).hexdigest()
    # A standalone initial bundle is also a complete replay prefix; validate its
    # closed mint payload rather than allowing malformed content to be sealed.
    if result["shape"] == "MINT":
        replay([result])
    return result


def _canonical_bundle(bundle: Any) -> dict[str, Any]:
    if not isinstance(bundle, dict) or tuple(bundle.keys()) != TOP_KEYS:
        raise _err("INVALID-BUNDLE", "bundle must include exactly six canonical keys")
    checked = _bundle_without_hash(bundle)
    ordered = {k: checked[k] for k in TOP_KEYS}
    if canonical_json(ordered) != canonical_json(bundle):
        raise _err("NONCANONICAL-BUNDLE", "bundle values are not canonical")
    return ordered


def _mint_id(content: dict[str, Any]) -> str:
    if "text" in content:
        return node_id(content["type"], content["text"])
    return edge_id(content["type"], content["source"], content["target"], content["carried_typing"])


def _canonical_identity_preimage(content: dict[str, Any]) -> str:
    """Return the complete identity material, independent of the truncated ID."""
    if "text" in content:
        return canonical_json({"kind": "node", "type": _nfc(content["type"]), "text": _collapse(content["text"])})
    return canonical_json({"kind": "edge", "type": _nfc(content["type"]), "source": content["source"],
                           "target": content["target"], "carried_typing": _nfc(content["carried_typing"])})


def _same_existing_identity(existing: dict[str, Any], record_id: str, content: dict[str, Any]) -> None:
    """Reject a distinct full identity that happens to share a truncated ID."""
    if _canonical_identity_preimage(existing["content"]) != _canonical_identity_preimage(content):
        raise _err("ID-COLLISION", f"record {record_id} collides with a distinct canonical identity", record_id)


def _guard_existing_identity(records: dict[str, Any], record_id: str, content: dict[str, Any]) -> None:
    existing = records[record_id]
    _same_existing_identity(existing, record_id, content)
    raise _err("EXISTING-IDENTITY", f"record {record_id} was already minted", record_id)


def _record_kind(record_id: str) -> str:
    return "node" if record_id.startswith("n-") else "edge"


def _history_entry(bundle: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
    def axis(a: str, b: str) -> tuple[Any, Any] | None:
        f, t = event[a], event[b]
        return None if f is None and t is None else (f, t)
    return {"timestamp": bundle["timestamp"], "event": event["event"], "actor": event["actor"],
            "approval": axis("approval_from", "approval_to"), "presence": axis("presence_from", "presence_to"),
            "inclusion": axis("inclusion_from", "inclusion_to"), "bundle": bundle["bundle_hash"]}


def _apply_axis(record: dict[str, Any], axis: str, frm: Any, to: Any, event: dict[str, Any]) -> None:
    current = record[axis]
    if frm is None and to is None:
        return
    if frm != current:
        raise _err("ILLEGAL-TRANSITION", f"{axis} transition starts at {current!r}, not {frm!r}", record["id"])
    record[axis] = to


def _state_copy_record(record: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(record)


def _apply_bundle(state: dict[str, Any], bundle: dict[str, Any], index: int) -> None:
    shape = bundle["shape"]
    records = state["records"]
    events = bundle["events"]
    if index == 0 and (shape != "MINT" or bundle["prev_hash"] != "GENESIS"):
        raise _err("INVALID-FIRST-BUNDLE", "first ledger bundle must be MINT with GENESIS")
    if index > 0 and shape == "MINT":
        raise _err("LATE-MINT", "MINT is legal only as the first bundle")
    if shape == "MINT" and any(e["event"] != "MINTED" or e["actor"] != "normalizer" for e in events):
        raise _err("BUNDLE-SHAPE-MISMATCH", "MINT contains non-normalizer MINTED event")
    if shape == "QUARANTINE" and any(e["event"] != "MINTED" or e["actor"] != "system" for e in events):
        raise _err("BUNDLE-SHAPE-MISMATCH", "QUARANTINE contains non-system event")
    if shape == "RECONCILE" and any(e["event"] not in {"RECONCILE", "MINTED"} for e in events):
        raise _err("BUNDLE-SHAPE-MISMATCH", "RECONCILE contains an illegal event")
    if shape == "DECISION" and (events[0]["event"] not in {"DECISION", "UNREJECT", "WITHDRAWAL", "INCLUSION"} or
                                 any(e["event"] != "CASCADE" for e in events[1:])):
        raise _err("ILLEGAL-TRANSITION", "DECISION event order is invalid")
    if shape == "REVISE" and (len(events) < 2 or events[0]["event"] != "MINTED" or events[1]["event"] != "REVISE" or
                               any(e["event"] != "CASCADE" for e in events[2:])):
        raise _err("BUNDLE-SHAPE-MISMATCH", "REVISE event order is invalid")
    mint_actor = {"MINT": "normalizer", "RECONCILE": "reconciliation", "REVISE": "author", "QUARANTINE": "system"}.get(shape)
    if mint_actor is not None and any(event["event"] == "MINTED" and event["actor"] != mint_actor for event in events):
        raise _err("BUNDLE-SHAPE-MISMATCH", "MINTED actor does not match bundle shape")
    minted = [event["record_id"] for event in events if event["event"] == "MINTED"]
    if shape in {"MINT", "RECONCILE", "QUARANTINE"}:
        expected_mints = sorted((rid for rid in minted if rid.startswith("n-"))) + sorted((rid for rid in minted if rid.startswith("e-")))
        if minted != expected_mints:
            raise _err("BUNDLE-SHAPE-MISMATCH", "MINTED events must be node-first lexical order")
    if shape == "RECONCILE" and any(event["event"] == "MINTED" for event in events[:len(events) - len(minted)]):
        raise _err("BUNDLE-SHAPE-MISMATCH", "RECONCILE events must precede MINTED events")

    # Apply on a private state so a failed multi-event bundle never mutates the caller.
    work = {"records": {rid: _state_copy_record(r) for rid, r in records.items()}, "context": copy.deepcopy(state.get("context")),
            "head": copy.deepcopy(state.get("head"))}
    if (index == 0 and shape == "MINT") or shape == "RECONCILE":
        work["context"] = copy.deepcopy(bundle["context"])
    for pos, event in enumerate(events):
        rid = event["record_id"]
        if event["related_record_id"] is not None and shape != "REVISE":
            raise _err("ILLEGAL-TRANSITION", "related_record_id is legal only in a REVISE bundle", rid)
        if event["event"] not in {"RECONCILE", "MINTED"} and any(event[k] is not None for k in ("presence_from", "presence_to")):
            raise _err("ILLEGAL-TRANSITION", "only RECONCILE may mutate presence", rid)
        if event["event"] == "MINTED":
            content = event["content"]
            if content is None:
                raise _err("INVALID-MINT-CONTENT", "MINTED content is required", rid)
            if rid.startswith("n-"):
                content = _node_content(content)
                expected = node_id(content["type"], content["text"])
                origin_expected = "MANUSCRIPT" if shape in {"MINT", "RECONCILE"} else ("AUTHOR-REVISION" if shape == "REVISE" else "QUARANTINE")
                if shape == "REVISE":
                    origin_expected = None
                if expected != rid:
                    raise _err("IDENTITY-MISMATCH", f"minted node id {rid} does not match content", rid)
                _guard_existing_identity(work["records"], rid, content) if rid in work["records"] else None
                if shape in {"MINT", "RECONCILE"} and content["origin"] != "MANUSCRIPT":
                    raise _err("INVALID-MINT-CONTENT", "source mints must be MANUSCRIPT", rid)
                if shape in {"MINT", "RECONCILE"} and any(provenance.split(":", 2)[1] != bundle["context"]["argument_state"] for provenance in content["provenance"]):
                    raise _err("SOURCE-CONTEXT-MISMATCH", "MANUSCRIPT mint provenance must match bundle Argument State", rid)
                if shape == "REVISE" and not content["origin"].startswith("AUTHOR-REVISION"):
                    raise _err("INVALID-MINT-CONTENT", "REVISE mint must be AUTHOR-REVISION", rid)
                if shape == "QUARANTINE":
                    version = bundle["context"]["draft_version"]
                    if content["origin"] != f"QUARANTINE (draft {version})" or not content["provenance"][0].startswith(f"QUARANTINE:{version}:"):
                        raise _err("QUARANTINE-PROVENANCE-MISMATCH", "QUARANTINE origin does not match bundle draft version", rid)
                record = {"id": rid, "kind": "node", "content": content, "approval": "PENDING", "presence": "CURRENT",
                          "inclusion": None, "origin": content["origin"], "mint_shape": shape,
                          "anchor_context": copy.deepcopy(bundle["context"] if content["origin"] == "MANUSCRIPT" else None),
                          "history": [], "notes": []}
            else:
                content = _edge_content(content)
                expected = edge_id(content["type"], content["source"], content["target"], content["carried_typing"])
                if expected != rid:
                    raise _err("IDENTITY-MISMATCH", f"minted edge id {rid} does not match content", rid)
                _guard_existing_identity(work["records"], rid, content) if rid in work["records"] else None
                if content["source"] not in work["records"] or content["target"] not in work["records"]:
                    raise _err("UNKNOWN-ENDPOINT", f"edge {rid} has an unknown endpoint", rid)
                record = {"id": rid, "kind": "edge", "content": content, "approval": "PENDING", "presence": "CURRENT",
                          "inclusion": None, "origin": "MANUSCRIPT" if shape in {"MINT", "RECONCILE"} else "QUARANTINE",
                          "mint_shape": shape, "anchor_context": None, "history": [], "notes": []}
            if event["approval_from"] is not None or event["approval_to"] != "PENDING" or event["presence_from"] is not None or event["presence_to"] != "CURRENT" or event["inclusion_from"] is not None or event["inclusion_to"] is not None:
                raise _err("ILLEGAL-TRANSITION", "MINTED axes must be null→PENDING, null→CURRENT, null→null", rid)
            record["history"].append(_history_entry(bundle, event))
            if event["note"] is not None:
                record["notes"].append({"timestamp": bundle["timestamp"], "event": event["event"], "text": event["note"]})
            work["records"][rid] = record
            continue

        if rid not in work["records"]:
            raise _err("UNKNOWN-RECORD", f"event references unknown record {rid}", rid)
        record = work["records"][rid]
        kind = record["kind"]
        ev = event["event"]
        actor = event["actor"]
        if event["content"] is not None and not (ev == "RECONCILE" and kind == "node"):
            raise _err("INVALID-EVENT-CONTENT", "content is only legal on MINTED or node RECONCILE", rid)
        if ev == "DECISION":
            if actor != "author" or event["reason"] is not None:
                raise _err("ILLEGAL-TRANSITION", "DECISION actor/reason invalid", rid)
            if event["approval_from"] == "PENDING" and event["approval_to"] == "APPROVED":
                if kind == "node":
                    if event["inclusion_from"] is not None or event["inclusion_to"] not in INCLUSIONS:
                        raise _err("ILLEGAL-TRANSITION", "node approval requires inclusion", rid)
                elif event["inclusion_from"] is not None or event["inclusion_to"] is not None:
                    raise _err("ILLEGAL-TRANSITION", "edge approval has no inclusion", rid)
            elif event["approval_from"] == "PENDING" and event["approval_to"] == "REJECTED":
                if event["inclusion_from"] is not None or event["inclusion_to"] is not None:
                    raise _err("ILLEGAL-TRANSITION", "rejection clears no pending inclusion", rid)
            elif event["approval_from"] == "APPROVED" and event["approval_to"] == "REJECTED":
                if kind == "node" and (event["inclusion_from"] not in INCLUSIONS or event["inclusion_to"] is not None):
                    raise _err("ILLEGAL-TRANSITION", "approved node rejection must clear inclusion", rid)
                if kind == "edge" and (event["inclusion_from"] is not None or event["inclusion_to"] is not None):
                    raise _err("ILLEGAL-TRANSITION", "approved edge rejection has no inclusion", rid)
            else:
                raise _err("ILLEGAL-TRANSITION", "invalid DECISION transition", rid)
        elif ev == "UNREJECT":
            if actor != "author" or event["approval_from"] != "REJECTED" or event["approval_to"] != "PENDING" or not event["reason"] or any(event[key] is not None for key in ("presence_from", "presence_to", "inclusion_from", "inclusion_to", "content", "related_record_id")):
                raise _err("ILLEGAL-TRANSITION", "invalid UNREJECT", rid)
        elif ev == "WITHDRAWAL":
            if actor != "author" or event["approval_from"] != "APPROVED" or event["approval_to"] != "PENDING":
                raise _err("ILLEGAL-TRANSITION", "invalid WITHDRAWAL", rid)
            if kind == "node" and (event["inclusion_from"] not in INCLUSIONS or event["inclusion_to"] is not None):
                raise _err("ILLEGAL-TRANSITION", "node withdrawal must clear inclusion", rid)
            if kind == "edge" and (event["inclusion_from"] is not None or event["inclusion_to"] is not None):
                raise _err("ILLEGAL-TRANSITION", "edge withdrawal has no inclusion", rid)
        elif ev == "INCLUSION":
            if actor != "author" or kind != "node" or event["approval_from"] is not None or event["approval_to"] is not None or event["presence_from"] is not None or event["presence_to"] is not None or event["inclusion_from"] not in INCLUSIONS or event["inclusion_to"] not in INCLUSIONS or event["inclusion_from"] == event["inclusion_to"] or not event["reason"]:
                raise _err("ILLEGAL-TRANSITION", "invalid INCLUSION", rid)
        elif ev == "CASCADE":
            if actor != "system" or kind != "edge" or event["approval_from"] != "APPROVED" or event["approval_to"] != "PENDING" or event["inclusion_from"] is not None or event["inclusion_to"] is not None or event["presence_from"] is not None or event["presence_to"] is not None or event["content"] is not None or event["related_record_id"] is not None or event["reason"] is not None:
                raise _err("ILLEGAL-TRANSITION", "invalid CASCADE", rid)
        elif ev == "REVISE":
            if actor != "author" or kind != "node" or record["approval"] not in {"PENDING", "APPROVED"} or event["approval_from"] not in {"PENDING", "APPROVED"} or event["approval_to"] != "SUPERSEDED" or event["related_record_id"] is None:
                raise _err("ILLEGAL-TRANSITION", "invalid REVISE", rid)
            if record["approval"] == "APPROVED" and event["inclusion_from"] not in INCLUSIONS:
                raise _err("ILLEGAL-TRANSITION", "approved revision must clear inclusion", rid)
            if record["approval"] == "PENDING" and event["inclusion_from"] is not None:
                raise _err("ILLEGAL-TRANSITION", "pending revision has no inclusion", rid)
            if event["inclusion_to"] is not None or event["presence_from"] is not None or event["presence_to"] is not None or event["content"] is not None:
                raise _err("ILLEGAL-TRANSITION", "REVISE has a non-closed axis or content field", rid)
        elif ev == "RECONCILE":
            if actor != "reconciliation" or record["origin"] != "MANUSCRIPT":
                raise _err("ILLEGAL-TRANSITION", "invalid RECONCILE actor/origin", rid)
            if kind == "node" and record["origin"] != "MANUSCRIPT":
                raise _err("ILLEGAL-TRANSITION", "only manuscript nodes reconcile", rid)
            all_null = all(event[k] is None for k in ("approval_from", "approval_to", "presence_from", "presence_to", "inclusion_from", "inclusion_to"))
            presence_change = event["presence_from"] is not None or event["presence_to"] is not None
            if all_null and kind != "node":
                raise _err("ILLEGAL-TRANSITION", "only manuscript nodes accept provenance reconciliation", rid)
            if event["approval_from"] is not None or event["approval_to"] is not None or event["inclusion_from"] is not None or event["inclusion_to"] is not None:
                raise _err("ILLEGAL-TRANSITION", "RECONCILE cannot mutate approval or inclusion", rid)
            if not all_null and not presence_change:
                raise _err("ILLEGAL-TRANSITION", "RECONCILE changes presence or appends provenance", rid)
            if presence_change and (event["presence_from"], event["presence_to"]) not in {("CURRENT", "ORPHANED"), ("ORPHANED", "CURRENT")}:
                raise _err("ILLEGAL-TRANSITION", "RECONCILE presence must be CURRENT<->ORPHANED", rid)
            if all_null:
                reason = event["reason"]
                repeated = reason in record["content"]["provenance"] if isinstance(reason, str) else False
                if not reason or not reason.startswith("STATE:"):
                    raise _err("ILLEGAL-TRANSITION", "RECONCILE provenance reason must be a STATE entry", rid)
                _provenance_entry(reason)
                if reason.split(":", 2)[1] != bundle["context"]["argument_state"]:
                    raise _err("SOURCE-CONTEXT-MISMATCH", "RECONCILE provenance must match bundle Argument State", rid)
                if repeated and event["content"] is None:
                    raise _err("ILLEGAL-TRANSITION", "RECONCILE provenance is duplicate without an anchor refresh", rid)
                if event["content"] is not None:
                    refresh = _refresh_content(event["content"])
                    record["content"]["anchors"] = refresh["anchors"]
                    record["content"]["flags"] = refresh["flags"]
                record["content"]["provenance"].append(reason)
            elif event["content"] is not None or event["reason"] is not None:
                raise _err("INVALID-RECONCILE-CONTENT", "presence change cannot refresh content or provenance", rid)
        else:
            raise _err("ILLEGAL-TRANSITION", f"unsupported event {ev}", rid)
        _apply_axis(record, "approval", event["approval_from"], event["approval_to"], event)
        _apply_axis(record, "presence", event["presence_from"], event["presence_to"], event)
        _apply_axis(record, "inclusion", event["inclusion_from"], event["inclusion_to"], event)
        if ev == "RECONCILE" and record["kind"] == "node" and event["content"] is not None:
            record["anchor_context"] = copy.deepcopy(bundle["context"])
        record["history"].append(_history_entry(bundle, event))
        if event["note"] is not None:
            record["notes"].append({"timestamp": bundle["timestamp"], "event": event["event"], "text": event["note"]})

    # REVISION and cascade structural checks happen after all event axes apply.
    if shape == "REVISE":
        mint, rev = events[0], events[1]
        if mint["related_record_id"] != rev["record_id"] or rev["related_record_id"] != mint["record_id"]:
            raise _err("INVALID-REVISION-PAIR", "REVISE pair is not reciprocal")
        if mint["record_id"] not in work["records"] or work["records"][mint["record_id"]]["origin"].startswith("AUTHOR-REVISION") is False:
            raise _err("INVALID-REVISION-PAIR", "replacement origin does not bind to original")
        original = work["records"][rev["record_id"]]
        expected_origin = f"AUTHOR-REVISION (of {original['id']})"
        if work["records"][mint["record_id"]]["origin"] != expected_origin:
            raise _err("INVALID-REVISION-PAIR", "replacement origin is not reciprocal")
    if shape in {"DECISION", "REVISE"}:
        trigger_index = 0 if shape == "DECISION" else 1
        cascade_start = 1 if shape == "DECISION" else 2
        cascades = [e["record_id"] for e in events[cascade_start:]]
        if cascades != sorted(cascades) or len(set(cascades)) != len(cascades):
            raise _err("BUNDLE-SHAPE-MISMATCH", "cascades must be unique lexical edge order")
        trigger = events[trigger_index]
        expected_cascades = []
        if trigger["record_id"] in records and records[trigger["record_id"]]["kind"] == "node" and trigger["approval_from"] == "APPROVED" and trigger["approval_to"] != "APPROVED":
            expected_cascades = sorted(rid for rid, rec in records.items() if rec["kind"] == "edge" and rec["approval"] == "APPROVED" and (rec["content"]["source"] == trigger["record_id"] or rec["content"]["target"] == trigger["record_id"]))
        if cascades != expected_cascades:
            raise _err("CASCADE-MISMATCH", "decision cascades do not equal the required incident approved edges")
    for rid, rec in work["records"].items():
        if rec["kind"] == "edge" and rec["approval"] == "APPROVED":
            c = rec["content"]
            if c["source"] not in work["records"] or c["target"] not in work["records"] or work["records"][c["source"]]["approval"] != "APPROVED" or work["records"][c["target"]]["approval"] != "APPROVED":
                raise _err("EDGE-ENDPOINT-COUPLING", f"approved edge {rid} lacks approved endpoints", rid)
    state["records"] = work["records"]
    state["context"] = work["context"]


def replay(bundles: list[dict]) -> dict:
    """Validate and replay canonical bundles into deterministic state."""
    if not isinstance(bundles, list):
        raise _err("INVALID-BUNDLES", "bundles must be a list")
    state: dict[str, Any] = {"records": {}, "context": None, "head": {"bundle_count": 0, "terminal_hash": "GENESIS"}, "bundles": []}
    previous = "GENESIS"
    for index, raw in enumerate(bundles):
        bundle = _canonical_bundle(raw)
        if bundle["prev_hash"] != previous:
            raise _err("CHAIN-BROKEN", f"bundle {index + 1} prev_hash does not match prior hash")
        _apply_bundle(state, bundle, index)
        state["bundles"].append(copy.deepcopy(bundle))
        previous = bundle["bundle_hash"]
        state["head"] = {"bundle_count": index + 1, "terminal_hash": previous}
    return state


def eligible_ids(state: dict) -> set[str]:
    records = state.get("records", {})
    nodes = {rid for rid, r in records.items() if r.get("kind") == "node" and r.get("approval") == "APPROVED" and r.get("presence") == "CURRENT"}
    result = set(nodes)
    for rid, rec in records.items():
        if rec.get("kind") == "edge" and rec.get("approval") == "APPROVED" and rec.get("presence") == "CURRENT":
            c = rec.get("content", {})
            if c.get("source") in nodes and c.get("target") in nodes:
                result.add(rid)
    return result


def _projection_json(value: Any) -> str:
    return canonical_json(value)


def _axis_text(pair: tuple[Any, Any] | None) -> str:
    if pair is None:
        return "—"
    left, right = pair
    return f"{left if left is not None else '—'}→{right if right is not None else '—'}"


def _history_line(entry: dict[str, Any]) -> str:
    return (f"  {entry['timestamp']} | {entry['event']} | {entry['actor']} | approval:{_axis_text(entry['approval'])} | "
            f"presence:{_axis_text(entry['presence'])} | inclusion:{_axis_text(entry['inclusion'])} | bundle:{entry['bundle']}")


def project_graph(state: dict) -> bytes:
    """Render the authoritative replay state as strict UTF-8 Markdown bytes."""
    records = state.get("records")
    if not isinstance(records, dict):
        raise _err("INVALID-STATE", "state records must be a mapping")
    ctx = state.get("context")
    out: list[str] = ["# Approval Graph", "Schema: approval-graph/1"]
    if ctx is None:
        out.append("Source manuscript: null — sha256 NONE")
        out.append("Reconciled against: NONE")
    else:
        out.append(f"Source manuscript: {_projection_json(ctx['source_filename'])} — sha256 {ctx['source_sha256']}")
        out.append(f"Reconciled against: {ctx['argument_state']}")
    out.extend(["ID length: 12", "", "## Nodes", ""])
    nodes = sorted((r for r in records.values() if r.get("kind") == "node"), key=lambda r: r["id"])
    for idx, rec in enumerate(nodes):
        c = rec["content"]
        anchors = c["anchors"] if c["anchors"] else "NONE (novel)"
        inclusion = rec["inclusion"] if rec["inclusion"] is not None else "—"
        out.extend([f"### Node {rec['id']}", f"Type: {c['type']}", f"Text: {_projection_json(c['text'])}",
                    f"Anchors: {_projection_json(anchors) if anchors != 'NONE (novel)' else anchors}",
                    f"Provenance: {_projection_json(c['provenance'])}", f"Origin: {c['origin']}", f"Approval: {rec['approval']}",
                    f"Presence: {rec['presence']}", f"Inclusion: {inclusion}", f"Flags: {_projection_json(c['flags'])}"])
        if rec.get("notes"):
            out.append(f"Notes: {_projection_json(rec['notes'])}")
        out.append("History:")
        out.extend(_history_line(h) for h in rec.get("history", []))
        if idx != len(nodes) - 1:
            out.append("")
    out.extend(["", "## Edges", ""])
    edges = sorted((r for r in records.values() if r.get("kind") == "edge"), key=lambda r: r["id"])
    for idx, rec in enumerate(edges):
        c = rec["content"]
        out.extend([f"### Edge {rec['id']}", f"Type: {c['type']}", f"Source: {c['source']}", f"Target: {c['target']}",
                    f"Carried typing: {c['carried_typing']}", f"Approval: {rec['approval']}", f"Presence: {rec['presence']}"])
        if rec.get("notes"):
            out.append(f"Notes: {_projection_json(rec['notes'])}")
        out.append("History:")
        out.extend(_history_line(h) for h in rec.get("history", []))
        if idx != len(edges) - 1:
            out.append("")
    return ("\n".join(out) + "\n").encode("utf-8")


def project_session(state: dict) -> bytes:
    records = state.get("records", {})
    pending_nodes = sorted((r["id"] for r in records.values() if r.get("kind") == "node" and r.get("approval") == "PENDING"))
    pending_edges = []
    for r in records.values():
        if r.get("kind") == "edge" and r.get("approval") == "PENDING":
            c = r.get("content", {})
            if records.get(c.get("source"), {}).get("approval") != "PENDING" and records.get(c.get("target"), {}).get("approval") != "PENDING":
                pending_edges.append(r["id"])
    next_record = sorted(pending_nodes + pending_edges)[0] if pending_nodes or pending_edges else None
    status = "SUSPENDED" if not records or any(r.get("approval") == "PENDING" for r in records.values()) else "CLOSED"
    return (canonical_json({"schema": "approval-session/1", "status": status, "next_record": next_record}) + "\n").encode("utf-8")


def _parse_json_field(text: str, name: str) -> Any:
    try:
        value = json.loads(text, object_pairs_hook=_json_pairs)
        _validate_json_value(value)
        return value
    except ApprovalGraphError:
        raise
    except Exception as exc:
        raise _err("PROJECTION-GRAMMAR", f"invalid JSON in {name}") from exc


def parse_graph(data: bytes) -> dict:
    """Strictly parse a graph projection, preserving decoded field values."""
    if not isinstance(data, (bytes, bytearray)) or not data.endswith(b"\n") or b"\r" in data:
        raise _err("PROJECTION-GRAMMAR", "graph must be UTF-8 LF-terminated bytes")
    try:
        lines = data.decode("utf-8")[:-1].split("\n")
    except UnicodeDecodeError as exc:
        raise _err("PROJECTION-GRAMMAR", "graph is not strict UTF-8") from exc
    if lines[:2] != ["# Approval Graph", "Schema: approval-graph/1"]:
        raise _err("PROJECTION-GRAMMAR", "invalid graph heading")
    if len(lines) < 7 or lines[6] != "## Nodes":
        raise _err("PROJECTION-GRAMMAR", "invalid graph header")
    m = re.fullmatch(r"Source manuscript: (null|.+) — sha256 (NONE|[0-9a-f]{64})", lines[2])
    if not m:
        raise _err("PROJECTION-GRAMMAR", "invalid source header")
    source = None if m.group(1) == "null" else _parse_json_field(m.group(1), "source filename")
    if source is not None and not isinstance(source, str):
        raise _err("PROJECTION-GRAMMAR", "source filename must be string")
    if not lines[4].startswith("ID length: 12"):
        raise _err("PROJECTION-GRAMMAR", "invalid ID length")
    result: dict[str, Any] = {"header": {"source_filename": source, "source_sha256": m.group(2), "argument_state": None}, "nodes": [], "edges": []}
    if lines[3].startswith("Reconciled against: "):
        result["header"]["argument_state"] = lines[3].split(": ", 1)[1]
    i = 7
    current: dict[str, Any] | None = None
    section = "nodes"
    field_order_node = ["Type", "Text", "Anchors", "Provenance", "Origin", "Approval", "Presence", "Inclusion", "Flags"]
    field_order_edge = ["Type", "Source", "Target", "Carried typing", "Approval", "Presence"]
    while i < len(lines):
        line = lines[i]
        if line == "## Edges":
            if current is not None:
                result[section].append(current); current = None
            section = "edges"; i += 1
            continue
        if not line:
            i += 1; continue
        hm = re.fullmatch(r"### (Node|Edge) ([ne]-[0-9a-f]{12})", line)
        if hm:
            if current is not None:
                result[section].append(current)
            if (hm.group(1) == "Node") != (section == "nodes"):
                raise _err("PROJECTION-GRAMMAR", "record section mismatch")
            current = {"id": hm.group(2), "kind": section[:-1]}
            fields = field_order_node if section == "nodes" else field_order_edge
            for field in fields:
                i += 1
                if i >= len(lines) or not lines[i].startswith(field + ": "):
                    raise _err("PROJECTION-GRAMMAR", f"missing {field}")
                raw = lines[i][len(field) + 2:]
                key = field.lower().replace(" ", "_")
                if field in {"Text", "Anchors", "Provenance", "Flags"}:
                    value = "NONE (novel)" if field == "Anchors" and raw == "NONE (novel)" else _parse_json_field(raw, field)
                else:
                    value = raw
                current[key] = value
            i += 1
            if i < len(lines) and lines[i].startswith("Notes: "):
                notes = _parse_json_field(lines[i][7:], "Notes")
                if not isinstance(notes, list):
                    raise _err("PROJECTION-GRAMMAR", "Notes must be an array")
                current["notes"] = notes
                i += 1
            if i >= len(lines) or lines[i] != "History:":
                raise _err("PROJECTION-GRAMMAR", "missing History")
            history = []
            i += 1
            while i < len(lines) and lines[i].startswith("  "):
                history.append(lines[i]); i += 1
            current["history"] = history
            continue
        raise _err("PROJECTION-GRAMMAR", f"unknown graph line {line!r}")
    if current is not None:
        result[section].append(current)
    return result


def classify_existing_novelty(state: dict, candidates: list[dict]) -> dict:
    records = state.get("records", {})
    new: list[dict] = []
    existing: list[dict] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise _err("INVALID-CANDIDATE", "candidate must be an object")
        payload = _node_content(candidate) if "text" in candidate else _edge_content(candidate)
        rid = _mint_id(payload)
        if rid not in records:
            new.append(copy.deepcopy(payload))
            continue
        rec = records[rid]
        _same_existing_identity(rec, rid, payload)
        if rec.get("approval") == "REJECTED":
            disposition = "REJECTED"
        elif rec.get("approval") == "PENDING":
            disposition = "PENDING"
        elif rec.get("approval") == "APPROVED" and rid in eligible_ids(state):
            disposition = "AUTHORIZED"
        else:
            disposition = "WITHHELD"
        existing.append({"record_id": rid, "disposition": disposition})
    return {"new": new, "existing": existing}


def _is_reparse(path: Path) -> bool:
    try:
        import stat
        attrs = getattr(path.stat(follow_symlinks=False), "st_file_attributes", 0)
        return bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
    except OSError:
        return False


def _lexists(path: Path) -> bool:
    return os.path.lexists(str(path))


def _reject_linked_components(path: Path, label: str) -> None:
    """Reject lexical links before resolve() can erase their custody boundary."""
    absolute = path if path.is_absolute() else Path.cwd() / path
    cursor = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        cursor = cursor / part
        if _lexists(cursor) and (cursor.is_symlink() or _is_reparse(cursor)):
            raise _err("LINK-ARTIFACT", f"linked project artifact is forbidden: {label}")


def _project_root(project: str | Path) -> Path:
    candidate = Path(project).expanduser()
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    _reject_linked_components(candidate, str(project))
    root = candidate.resolve(strict=False)
    if not root.exists():
        raise _err("PROJECT-MISSING", "project directory does not exist")
    if not root.is_dir():
        raise _err("INVALID-PROJECT-PATH", "project is not a directory")
    return root


def _inside(root: Path, name: str, allow_missing: bool = True) -> Path:
    relative = Path(name)
    if relative.is_absolute() or relative.drive or any(part in {"", ".", ".."} for part in relative.parts):
        raise _err("PATH-OUTSIDE-PROJECT", f"path escapes project: {name}")
    path = root / relative
    _reject_linked_components(path, name)
    try:
        resolved = path.resolve(strict=False)
    except OSError as exc:
        raise _err("INVALID-PATH", str(exc)) from exc
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise _err("PATH-OUTSIDE-PROJECT", f"path escapes project: {name}") from exc
    if not allow_missing and not _lexists(path):
        raise _err("ARTIFACT-MISSING", f"missing artifact {name}")
    return path


class _ProjectLock:
    """One nonblocking OS project lock, serialized across local threads too."""

    _held: dict[str, tuple[Any, int, int]] = {}
    _guard = threading.Lock()
    _thread_locks: dict[str, threading.RLock] = {}

    def __init__(self, root: Path):
        self.root = root
        self.path = _inside(root, ".Approval_Events.lock")
        self.key = str(self.path)
        self.reused = False
        self.file = None
        self.thread_lock = None

    def __enter__(self):
        owner = threading.get_ident()
        with self._guard:
            self.thread_lock = self._thread_locks.setdefault(self.key, threading.RLock())
        if not self.thread_lock.acquire(blocking=False):
            raise _err("PROJECT-BUSY", "project lock is held by another thread")
        if self.key in self._held and self._held[self.key][2] == owner:
            file_obj, depth, _ = self._held[self.key]
            self._held[self.key] = (file_obj, depth + 1, owner)
            self.reused = True
            return self
        try:
            self.file = open(self.path, "a+b")
            self.file.seek(0)
            if os.fstat(self.file.fileno()).st_size == 0:
                self.file.write(b"\0")
                self.file.flush()
                os.fsync(self.file.fileno())
            self.file.seek(0)
            if msvcrt is not None:
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            elif fcntl is not None:
                fcntl.flock(self.file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            else:
                raise _err("LOCK-UNSUPPORTED", "platform does not provide an OS file lock")
        except (OSError, IOError) as exc:
            if self.file is not None:
                self.file.close()
                self.file = None
            self.thread_lock.release()
            if getattr(exc, "errno", None) in {errno.EACCES, errno.EAGAIN, errno.EDEADLK, 13, 33}:
                raise _err("PROJECT-BUSY", "project lock is held by another process") from exc
            raise _err("LOCK-FAILED", str(exc)) from exc
        self._held[self.key] = (self.file, 1, owner)
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if self.reused:
                file_obj, depth, owner = self._held[self.key]
                self._held[self.key] = (file_obj, depth - 1, owner)
                return False
            if self.file is not None:
                try:
                    self.file.seek(0)
                    if msvcrt is not None:
                        msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
                    elif fcntl is not None:
                        fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)
                finally:
                    self.file.close()
                    self._held.pop(self.key, None)
            return False
        finally:
            if self.thread_lock is not None:
                self.thread_lock.release()


def _write_all(file_obj, data: bytes) -> None:
    view = memoryview(data)
    done = 0
    while done < len(view):
        n = file_obj.write(view[done:])
        if not n:
            raise OSError("short write")
        done += n


def _fsync_dir(root: Path) -> None:
    if os.name != "nt":
        try:
            fd = os.open(root, os.O_RDONLY)
            try: os.fsync(fd)
            finally: os.close(fd)
        except OSError:
            pass


def _atomic_write(path: Path, data: bytes) -> None:
    if path.parent != path.parent.resolve(strict=False):
        raise _err("PATH-OUTSIDE-PROJECT", "invalid projection parent")
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as fh:
            _write_all(fh, data); fh.flush(); os.fsync(fh.fileno())
        os.replace(temp, path)
        _fsync_dir(path.parent)
    except Exception:
        try: temp.unlink(missing_ok=True)
        except OSError: pass
        raise


def _ledger_path(root: Path) -> Path:
    return _inside(root, "Approval_Events.jsonl")


def _projection_paths(root: Path) -> tuple[Path, Path]:
    return _inside(root, "Approval_Graph.md"), _inside(root, "Adjudication_Session.json")


def _source_path(root: Path, digest: str) -> Path:
    if not HEX64.fullmatch(digest):
        raise _err("INVALID-HASH", "invalid source snapshot hash")
    directory = _inside(root, "Approval_Sources")
    if directory.exists() and (directory.is_symlink() or _is_reparse(directory)):
        raise _err("LINK-ARTIFACT", "Approval_Sources may not be a link")
    return _inside(root, f"Approval_Sources/{digest}.utf8")


def _receipt_files(root: Path) -> list[Path]:
    files = []
    current = _inside(root, "Reconstruction_Receipt.md")
    if current.exists(): files.append(current)
    for path in root.glob("Reconstruction_Receipt_v*.md"):
        if path.is_symlink() or _is_reparse(path) or path.is_dir():
            raise _err("LINK-ARTIFACT", f"invalid receipt archive artifact {path.name}")
        if path.is_file():
            if re.fullmatch(r"Reconstruction_Receipt_v[1-9][0-9]*\.md", path.name): files.append(path)
            else: raise _err("RECEIPT-GRAMMAR", f"invalid receipt archive name {path.name}")
    return sorted(files, key=lambda p: (p.name != "Reconstruction_Receipt.md", p.name))


def _receipt_identity(path: Path) -> dict[str, Any]:
    try: text = path.read_text(encoding="utf-8")
    except Exception as exc: raise _err("RECEIPT-GRAMMAR", f"cannot read {path.name}: {exc}") from exc
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if len(lines) < 3 or lines[0] != "# Reconstruction Receipt" or not lines[1].startswith("Identity: ") or not lines[2].startswith("Verdict: "):
        raise _err("RECEIPT-GRAMMAR", f"invalid receipt envelope in {path.name}")
    if sum(1 for line in lines if line.startswith("Identity: ")) != 1:
        raise _err("RECEIPT-GRAMMAR", f"duplicate receipt envelope field in {path.name}")
        raise _err("RECEIPT-GRAMMAR", f"duplicate receipt envelope field in {path.name}")
    identity_text = lines[1][10:]
    identity = _parse_json_field(identity_text, "Identity")
    if not isinstance(identity, dict) or canonical_json(identity) != identity_text or tuple(identity.keys()) != ("draft_filename", "draft_sha256", "graph_sha256", "bundle_count", "terminal_hash", "record_ids", "rejected_ids"):
        raise _err("RECEIPT-GRAMMAR", f"invalid identity keys in {path.name}")
    if not isinstance(identity["draft_filename"], str) or not isinstance(identity["graph_sha256"], str) or not isinstance(identity["draft_sha256"], str):
        raise _err("RECEIPT-GRAMMAR", "receipt identity filenames/hashes invalid")
    _hex(identity["draft_sha256"], "draft_sha256"); _hex(identity["graph_sha256"], "graph_sha256")
    if isinstance(identity["bundle_count"], bool) or not isinstance(identity["bundle_count"], int) or identity["bundle_count"] < 0:
        raise _err("RECEIPT-GRAMMAR", "bundle_count must be nonnegative integer")
    if identity["terminal_hash"] != "GENESIS": _hex(identity["terminal_hash"], "terminal_hash")
    if identity["bundle_count"] == 0 and identity["terminal_hash"] != "GENESIS": raise _err("RECEIPT-GRAMMAR", "zero receipt count requires GENESIS")
    for key in ("record_ids", "rejected_ids"):
        arr = identity[key]
        if not isinstance(arr, list) or any(not isinstance(v, str) or not RID.fullmatch(v) for v in arr) or arr != sorted(set(arr)):
            raise _err("RECEIPT-GRAMMAR", f"{key} must be sorted unique record IDs")
    if not set(identity["rejected_ids"]).issubset(identity["record_ids"]): raise _err("RECEIPT-GRAMMAR", "rejected IDs must be subset")
    verdict = lines[2][9:]
    if verdict not in {"PASS", "ACTION-REQUIRED"}: raise _err("RECEIPT-GRAMMAR", "invalid receipt verdict")
    return identity


def _receipt_prefix_check(root: Path, bundles: list[dict]) -> None:
    for path in _receipt_files(root):
        identity = _receipt_identity(path)
        count = identity["bundle_count"]
        if len(bundles) < count:
            raise _err("RECEIPT-PREFIX-CROSSING", f"ledger is shorter than retained receipt {path.name}")
        if count == 0:
            prefix = replay([])
        else:
            prefix = replay(bundles[:count])
            if bundles[count - 1]["bundle_hash"] != identity["terminal_hash"]:
                raise _err("RECEIPT-PREFIX-CROSSING", f"receipt prefix hash mismatch: {path.name}")
        ids = sorted(prefix["records"])
        rejected = sorted(rid for rid, rec in prefix["records"].items() if rec["approval"] == "REJECTED")
        if ids != identity["record_ids"] or rejected != identity["rejected_ids"]:
            raise _err("RECEIPT-PREFIX-CROSSING", f"receipt record identity mismatch: {path.name}")


def _read_ledger(root: Path, allow_missing: bool = False) -> tuple[list[dict], int]:
    path = _ledger_path(root)
    if not _lexists(path):
        _receipt_prefix_check(root, [])
        if allow_missing:
            return [], 0
        raise _err("LEDGER-MISSING", "Approval_Events.jsonl is missing")
    if path.is_symlink() or _is_reparse(path) or not path.is_file(): raise _err("LINK-ARTIFACT", "ledger must be a regular file")
    raw = path.read_bytes()
    recovered = 0
    if raw and not raw.endswith(b"\n"):
        cut = raw.rfind(b"\n") + 1
        prefix_raw, suffix = raw[:cut], raw[cut:]
        bundles = _parse_ledger_bytes(prefix_raw)
        replay(bundles)
        _receipt_prefix_check(root, bundles)
        with open(path, "r+b") as fh:
            fh.truncate(cut); fh.flush(); os.fsync(fh.fileno())
        _fsync_dir(root)
        recovered = len(suffix)
        return bundles, recovered
    bundles = _parse_ledger_bytes(raw)
    _receipt_prefix_check(root, bundles)
    return bundles, recovered


def _parse_ledger_bytes(raw: bytes) -> list[dict]:
    if not raw:
        return []
    if not raw.endswith(b"\n"):
        raise _err("LEDGER-TORN-UNCLASSIFIED", "unterminated ledger suffix")
    bundles = []
    for index, payload in enumerate(raw[:-1].split(b"\n"), 1):
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise _err("LEDGER-INVALID-UTF8", f"ledger line {index} is not UTF-8") from exc
        try:
            obj = json.loads(text, object_pairs_hook=_json_pairs)
        except ApprovalGraphError:
            raise
        except Exception as exc:
            raise _err("LEDGER-MALFORMED-RECORD", f"invalid ledger JSON line {index}") from exc
        if not isinstance(obj, dict):
            raise _err("LEDGER-MALFORMED-RECORD", f"ledger line {index} is not an object")
        bundle = _canonical_bundle(obj)
        if canonical_json(bundle).encode("utf-8") != payload:
            raise _err("NONCANONICAL-BUNDLE", f"ledger line {index} is not canonical")
        bundles.append(bundle)
    return bundles


def _json_pairs(pairs: list[tuple[str, Any]]) -> dict:
    obj = {}
    for key, value in pairs:
        if key in obj: raise _err("DUPLICATE-JSON-KEY", f"duplicate JSON key {key!r}")
        obj[key] = value
    return obj


def _draft_artifact(root: Path, version: str) -> Path:
    """Resolve the logical draft file named by a quarantine context."""
    if not VERSION.fullmatch(version):
        raise _err("INVALID-DRAFT-VERSION", "invalid draft version")
    archives = []
    for path in root.glob("Reconstruction_Draft_v*.md"):
        if path.is_symlink() or _is_reparse(path) or path.is_dir():
            raise _err("LINK-ARTIFACT", f"invalid draft archive artifact {path.name}")
        if not re.fullmatch(r"Reconstruction_Draft_v[1-9][0-9]*\.md", path.name):
            raise _err("DRAFT-GRAMMAR", f"invalid draft archive name {path.name}")
        archives.append(path)
    current_n = 1 + max([int(p.stem.rsplit("_v", 1)[1]) for p in archives] or [0])
    n = int(version[1:])
    if n == current_n:
        return _inside(root, "Reconstruction_Draft.md")
    return _inside(root, f"Reconstruction_Draft_v{n}.md")


def _check_quarantine_artifact(root: Path, bundle: dict) -> None:
    if bundle.get("shape") != "QUARANTINE":
        return
    ctx = bundle.get("context") or {}
    path = _draft_artifact(root, ctx.get("draft_version", ""))
    if not path.exists() or path.is_symlink() or _is_reparse(path) or not path.is_file():
        raise _err("DRAFT-EVIDENCE-UNAVAILABLE", "quarantine draft artifact is unavailable")
    if hashlib.sha256(path.read_bytes()).hexdigest() != ctx["draft_sha256"]:
        raise _err("DRAFT-HASH-MISMATCH", "quarantine draft hash does not match context")
    version = ctx["draft_version"]
    for event in bundle.get("events", []):
        if event.get("event") != "MINTED" or not event.get("record_id", "").startswith("n-"):
            continue
        content = event.get("content") or {}
        expected_origin = f"QUARANTINE (draft {version})"
        expected_prefix = f"QUARANTINE:{version}:"
        if content.get("origin") != expected_origin or content.get("provenance", [None])[0] is None or not content["provenance"][0].startswith(expected_prefix):
            raise _err("QUARANTINE-PROVENANCE-MISMATCH", "quarantine mint does not bind its draft context", event.get("record_id"))


def _check_bundle_sources(root: Path, bundle: dict) -> None:
    if bundle.get("shape") not in {"MINT", "RECONCILE"}:
        return
    context = bundle.get("context")
    if not context:
        return
    snap = _source_path(root, context["source_sha256"])
    if not snap.exists():
        raise _err("SOURCE-EVIDENCE-UNAVAILABLE", "source snapshot was not staged")
    raw = snap.read_bytes()
    if hashlib.sha256(raw).hexdigest() != context["source_sha256"]:
        raise _err("SOURCE-SNAPSHOT-MISMATCH", "source snapshot hash mismatch")
    text = _collapse(raw.decode("utf-8"))
    for event in bundle.get("events", []):
        is_mint = event.get("event") == "MINTED" and event.get("record_id", "").startswith("n-")
        is_refresh = event.get("event") == "RECONCILE" and event.get("record_id", "").startswith("n-") and event.get("content") is not None
        if not (is_mint or is_refresh):
            continue
        content = event.get("content") or {}
        if is_mint and content.get("origin") != "MANUSCRIPT":
            continue
        last_anchor_start = 0
        for anchor in content.get("anchors", []):
            quote = _collapse(anchor.get("quote", ""))
            found = text.find(quote, last_anchor_start)
            if found < 0:
                raise _err("SOURCE-ANCHOR-MISMATCH", "anchor does not resolve in ordered source evidence", event.get("record_id"))
            last_anchor_start = found

def _stage_source(root: Path, context: dict | None) -> None:
    if not context or "source_filename" not in context: return
    digest = context["source_sha256"]
    dest = _source_path(root, digest)
    source = _inside(root, context["source_filename"], allow_missing=True)
    if dest.exists():
        if dest.is_symlink() or _is_reparse(dest) or not dest.is_file(): raise _err("LINK-ARTIFACT", "source snapshot must be regular file")
        data = dest.read_bytes()
        if hashlib.sha256(data).hexdigest() != digest: raise _err("SOURCE-SNAPSHOT-MISMATCH", "retained source snapshot hash mismatch")
        data.decode("utf-8")
        return
    if not source.exists() or source.is_symlink() or _is_reparse(source) or not source.is_file():
        raise _err("SOURCE-EVIDENCE-UNAVAILABLE", f"source evidence unavailable: {context['source_filename']}")
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != digest: raise _err("SOURCE-HASH-MISMATCH", "live source does not match context hash")
    data.decode("utf-8")
    directory = dest.parent
    directory.mkdir(parents=False, exist_ok=True)
    _inside(root, "Approval_Sources", allow_missing=True)
    _atomic_write(dest, data)


def _check_sources(root: Path, state: dict) -> list[dict]:
    findings = []
    for rid, rec in state["records"].items():
        if rec["kind"] != "node" or rec["origin"] != "MANUSCRIPT": continue
        ctx = rec.get("anchor_context")
        if not ctx:
            findings.append({"code": "SOURCE-EVIDENCE-UNAVAILABLE", "message": "record has no retained source binding", "record_id": rid}); continue
        try:
            snap = _source_path(root, ctx["source_sha256"])
            if not snap.exists():
                findings.append({"code": "SOURCE-EVIDENCE-UNAVAILABLE", "message": f"missing source snapshot {ctx['source_sha256']}", "record_id": rid}); continue
            raw = snap.read_bytes()
            if hashlib.sha256(raw).hexdigest() != ctx["source_sha256"]:
                findings.append({"code": "SOURCE-SNAPSHOT-MISMATCH", "message": "source snapshot hash mismatch", "record_id": rid}); continue
            text = raw.decode("utf-8")
            norm = _collapse(text)
            last_anchor_start = 0
            for anchor in rec["content"]["anchors"]:
                found = norm.find(_collapse(anchor["quote"]), last_anchor_start)
                if found < 0:
                    findings.append({"code": "SOURCE-ANCHOR-MISMATCH", "message": "anchor does not resolve in retained source order", "record_id": rid})
                    break
                last_anchor_start = found
        except (OSError, UnicodeError):
            findings.append({"code": "SOURCE-EVIDENCE-UNAVAILABLE", "message": "source evidence unavailable", "record_id": rid})
    return findings


def _publish(root: Path, state: dict) -> list[str]:
    graph_path, session_path = _projection_paths(root)
    rebuilt = []
    graph = project_graph(state); session = project_session(state)
    if not graph_path.exists() or graph_path.read_bytes() != graph:
        _atomic_write(graph_path, graph); rebuilt.append(graph_path.name)
    if not session_path.exists() or session_path.read_bytes() != session:
        _atomic_write(session_path, session); rebuilt.append(session_path.name)
    return rebuilt


def _preappend_custody(root: Path, bundles: list[dict], state: dict) -> None:
    """Refuse every mutation if any retained evidence or bound anchor is broken."""
    try:
        for bundle in bundles:
            _check_bundle_sources(root, bundle)
            _check_quarantine_artifact(root, bundle)
        findings = _check_sources(root, state)
    except ApprovalGraphError:
        raise
    except (OSError, UnicodeError, TypeError, ValueError) as exc:
        raise _err("SOURCE-EVIDENCE-UNAVAILABLE", str(exc)) from exc
    if findings:
        first = findings[0]
        raise _err(first["code"], first["message"], first["record_id"])


_operation_outcome = threading.local()
_NO_OUTER_OPERATION = object()


def _mark_append_uncertain() -> None:
    if hasattr(_operation_outcome, "committed"):
        _operation_outcome.committed = None


def _mark_durable_append() -> None:
    if hasattr(_operation_outcome, "committed"):
        _operation_outcome.committed = True


def _public_mutation(func):
    """Translate native failures, retaining a known durable outcome through lock release."""
    @wraps(func)
    def wrapped(*args, **kwargs):
        prior = getattr(_operation_outcome, "committed", _NO_OUTER_OPERATION)
        _operation_outcome.committed = False
        try:
            return func(*args, **kwargs)
        except ApprovalGraphError:
            raise
        except Exception as exc:
            raise ApprovalGraphError("OPERATION-FAILED", str(exc), _operation_outcome.committed) from exc
        finally:
            if prior is _NO_OUTER_OPERATION:
                delattr(_operation_outcome, "committed")
            else:
                _operation_outcome.committed = prior
    return wrapped


def _head_equal(expected: Any, actual: dict) -> None:
    if not isinstance(expected, dict) or tuple(expected.keys()) != ("bundle_count", "terminal_hash") or isinstance(expected["bundle_count"], bool) or not isinstance(expected["bundle_count"], int) or expected["bundle_count"] < 0:
        raise _err("INVALID-EXPECTED-HEAD", "expected_head must be bundle_count and terminal_hash")
    if expected["bundle_count"] == 0:
        if expected["terminal_hash"] != "GENESIS": raise _err("INVALID-EXPECTED-HEAD", "zero bundle head requires GENESIS")
    elif not isinstance(expected["terminal_hash"], str) or not HEX64.fullmatch(expected["terminal_hash"]):
        raise _err("INVALID-EXPECTED-HEAD", "nonzero head requires a lowercase SHA-256 hash")
    if expected != actual:
        raise _err("STALE-HEAD", f"expected head {expected!r}, actual {actual!r}")


def _append_locked(root: Path, bundle: dict, expected_head: dict, recovered: int = 0) -> dict:
    bundles, more_recovered = _read_ledger(root, allow_missing=True)
    recovered += more_recovered
    state = replay(bundles)
    _preappend_custody(root, bundles, state)
    _head_equal(expected_head, state["head"])
    bundle = seal_bundle(bundle) if "bundle_hash" not in bundle else _canonical_bundle(bundle)
    if bundle["prev_hash"] != state["head"]["terminal_hash"]:
        raise _err("STALE-HEAD", "proposed bundle prev_hash does not match expected head")
    if bundle["shape"] == "MINT" and state["head"]["bundle_count"] != 0:
        raise _err("LATE-MINT", "MINT is only legal for an empty ledger")
    new_state = replay(bundles + [bundle])
    _stage_source(root, bundle["context"])
    _check_bundle_sources(root, bundle)
    _check_quarantine_artifact(root, bundle)
    ledger = _ledger_path(root)
    try:
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with open(ledger, "ab") as fh:
            _mark_append_uncertain()
            _write_all(fh, canonical_json(bundle).encode("utf-8") + b"\n")
            fh.flush(); os.fsync(fh.fileno())
            _mark_durable_append()
    except Exception as exc:
        outcome = getattr(_operation_outcome, "committed", None)
        raise ApprovalGraphError("APPEND-OUTCOME-UNKNOWN", str(exc), outcome) from exc
    try:
        rebuilt = _publish(root, new_state)
    except Exception as exc:
        raise ApprovalGraphError("PROJECTION-PUBLISH-FAILED", str(exc), True) from exc
    return {"status": "COMMITTED", "head": new_state["head"], "findings": [], "projection_rebuilt": rebuilt, "recovered_bytes": recovered}


@_public_mutation
def append_bundle(project: str | Path, bundle: dict, expected_head: dict) -> dict:
    """Validate one complete bundle and append it under the project OS lock."""
    root = _project_root(project)
    with _ProjectLock(root):
        return _append_locked(root, bundle, expected_head)


def _validate_node_inventory(items: Any) -> list[dict]:
    if not isinstance(items, list): raise _err("INVALID-NORMALIZED-RECORDS", "nodes must be a list")
    merged: dict[str, dict] = {}
    for raw in items:
        content = _node_content(raw)
        if content["origin"] != "MANUSCRIPT": raise _err("INVALID-NORMALIZED-RECORDS", "normalized nodes must be MANUSCRIPT")
        rid = node_id(content["type"], content["text"])
        prior = merged.get(rid)
        if prior is None:
            merged[rid] = content
        else:
            if _canonical_identity_preimage(prior) != _canonical_identity_preimage(content):
                raise _err("ID-COLLISION", f"normalized nodes collide at {rid}", rid)
            prior["anchors"] = prior["anchors"] + [a for a in content["anchors"] if a not in prior["anchors"]]
            prior["provenance"] = prior["provenance"] + [p for p in content["provenance"] if p not in prior["provenance"]]
            prior["flags"] = _flags(prior["flags"] + content["flags"])
    return list(merged.values())


@_public_mutation
def reconcile(project: str | Path, normalized_records: dict, context: dict, expected_head: dict, timestamp: str) -> dict:
    """Create one deterministic RECONCILE bundle for a full normalized inventory."""
    root = _project_root(project); _timestamp(timestamp)
    with _ProjectLock(root):
        bundles, recovered = _read_ledger(root, allow_missing=False)
        state = replay(bundles)
        _preappend_custody(root, bundles, state)
        if not bundles or not any(b["shape"] == "MINT" for b in bundles): raise _err("RECONCILE-UNSTARTED", "reconciliation requires a nonempty MINT-derived state")
        _head_equal(expected_head, state["head"])
        ctx = _context(context, "RECONCILE")
        normalized_nodes = _validate_node_inventory(normalized_records.get("nodes") if isinstance(normalized_records, dict) else None)
        normalized_edges_raw = normalized_records.get("edges") if isinstance(normalized_records, dict) else None
        if not isinstance(normalized_edges_raw, list): raise _err("INVALID-NORMALIZED-RECORDS", "edges must be a list")
        normalized_edges = [_edge_content(e) for e in normalized_edges_raw]
        node_map = {}
        for node in normalized_nodes:
            rid = node_id(node["type"], node["text"])
            if rid in node_map and _canonical_identity_preimage(node_map[rid]) != _canonical_identity_preimage(node):
                raise _err("ID-COLLISION", f"normalized node collision at {rid}", rid)
            if rid in state["records"]:
                _same_existing_identity(state["records"][rid], rid, node)
            node_map[rid] = node
        edge_map = {}
        for edge in normalized_edges:
            rid = edge_id(edge["type"], edge["source"], edge["target"], edge["carried_typing"])
            if edge["source"] not in node_map or edge["target"] not in node_map:
                raise _err("UNKNOWN-ENDPOINT", f"normalized edge {rid} endpoint absent")
            if rid in edge_map and edge_map[rid] != edge: raise _err("ID-COLLISION", f"conflicting edge {rid}")
            if rid in state["records"] and _canonical_identity_preimage(state["records"][rid]["content"]) != _canonical_identity_preimage(edge):
                raise _err("ID-COLLISION", f"normalized edge collides with existing {rid}", rid)
            edge_map[rid] = edge
        events: list[dict] = []
        existing_ids = set(state["records"])
        for rid in sorted(existing_ids):
            rec = state["records"][rid]
            if rec["origin"] != "MANUSCRIPT": continue
            present = rid in node_map or rid in edge_map
            if rec["kind"] == "node":
                if not present and rec["presence"] == "CURRENT":
                    events.append({"event": "RECONCILE", "actor": "reconciliation", "record_id": rid, "related_record_id": None, "content": None, "approval_from": None, "approval_to": None, "presence_from": "CURRENT", "presence_to": "ORPHANED", "inclusion_from": None, "inclusion_to": None, "reason": None, "note": None})
                elif present:
                    incoming = node_map[rid]
                    _same_existing_identity(rec, rid, incoming)
                    if rec["presence"] == "ORPHANED":
                        events.append({"event": "RECONCILE", "actor": "reconciliation", "record_id": rid, "related_record_id": None, "content": None, "approval_from": None, "approval_to": None, "presence_from": "ORPHANED", "presence_to": "CURRENT", "inclusion_from": None, "inclusion_to": None, "reason": None, "note": None})
                    source_changed = ctx != state.get("context")
                    new_prov = [p for p in incoming["provenance"] if p not in rec["content"]["provenance"]]
                    refresh = source_changed or incoming["anchors"] != rec["content"]["anchors"] or incoming["flags"] != rec["content"]["flags"]
                    refresh_prov = incoming["provenance"][-1] if incoming["provenance"] else None
                    for prov in new_prov or ([refresh_prov] if refresh and refresh_prov else []):
                        _provenance_entry(prov)
                        content_refresh = {"anchors": incoming["anchors"], "flags": incoming["flags"]} if refresh else None
                        events.append({"event": "RECONCILE", "actor": "reconciliation", "record_id": rid, "related_record_id": None, "content": content_refresh, "approval_from": None, "approval_to": None, "presence_from": None, "presence_to": None, "inclusion_from": None, "inclusion_to": None, "reason": prov, "note": None})
            elif not present and rec["presence"] == "CURRENT":
                events.append({"event": "RECONCILE", "actor": "reconciliation", "record_id": rid, "related_record_id": None, "content": None, "approval_from": None, "approval_to": None, "presence_from": "CURRENT", "presence_to": "ORPHANED", "inclusion_from": None, "inclusion_to": None, "reason": None, "note": None})
            elif present and rec["presence"] == "ORPHANED":
                events.append({"event": "RECONCILE", "actor": "reconciliation", "record_id": rid, "related_record_id": None, "content": None, "approval_from": None, "approval_to": None, "presence_from": "ORPHANED", "presence_to": "CURRENT", "inclusion_from": None, "inclusion_to": None, "reason": None, "note": None})
        minted_nodes = [(node_id(n["type"], n["text"]), n) for n in normalized_nodes if node_id(n["type"], n["text"]) not in existing_ids]
        minted_edges = [(edge_id(e["type"], e["source"], e["target"], e["carried_typing"]), e) for e in normalized_edges if edge_id(e["type"], e["source"], e["target"], e["carried_typing"]) not in existing_ids]
        for rid, content in sorted(minted_nodes):
            events.append({"event": "MINTED", "actor": "reconciliation", "record_id": rid, "related_record_id": None, "content": content, "approval_from": None, "approval_to": "PENDING", "presence_from": None, "presence_to": "CURRENT", "inclusion_from": None, "inclusion_to": None, "reason": None, "note": None})
        for rid, content in sorted(minted_edges):
            events.append({"event": "MINTED", "actor": "reconciliation", "record_id": rid, "related_record_id": None, "content": content, "approval_from": None, "approval_to": "PENDING", "presence_from": None, "presence_to": "CURRENT", "inclusion_from": None, "inclusion_to": None, "reason": None, "note": None})
        if not events:
            findings = []
            if ctx != state.get("context"): findings.append({"code": "CONTEXT-NOT-ADVANCED", "message": "no legal reconciliation event; source context unchanged", "record_id": None})
            return {"status": "NO-CHANGE", "head": state["head"], "findings": findings, "projection_rebuilt": [], "recovered_bytes": recovered}
        bundle = {"shape": "RECONCILE", "prev_hash": state["head"]["terminal_hash"], "timestamp": timestamp, "context": ctx, "events": events}
        _stage_source(root, ctx)
        return _append_locked(root, bundle, expected_head, recovered)


@_public_mutation
def revise(project: str | Path, original_id: str, replacement: dict, expected_head: dict, timestamp: str, note=None) -> dict:
    """Atomically mint an AUTHOR-REVISION node and supersede its original."""
    root = _project_root(project); _timestamp(timestamp); _rid(original_id, "node")
    if not isinstance(replacement, dict) or tuple(replacement.keys()) != ("type", "text") or replacement["type"] not in NODE_TYPES or not isinstance(replacement["text"], str):
        raise _err("INVALID-REPLACEMENT", "replacement must be exactly type and text")
    rid = node_id(replacement["type"], replacement["text"])
    with _ProjectLock(root):
        bundles, recovered = _read_ledger(root, allow_missing=False); state = replay(bundles); _preappend_custody(root, bundles, state); _head_equal(expected_head, state["head"])
        original = state["records"].get(original_id)
        if not original: raise _err("UNKNOWN-RECORD", f"unknown original {original_id}", original_id)
        if original["kind"] != "node" or original["approval"] == "REJECTED": raise _err("INVALID-REVISION", "only non-rejected nodes may be revised", original_id)
        content = {"type": replacement["type"], "text": replacement["text"], "anchors": [], "origin": f"AUTHOR-REVISION (of {original_id})", "provenance": [f"AUTHOR-REVISION:{original_id}"], "flags": ["NONE"]}
        if rid in state["records"]:
            _guard_existing_identity(state["records"], rid, content)
        events = [{"event": "MINTED", "actor": "author", "record_id": rid, "related_record_id": original_id, "content": content, "approval_from": None, "approval_to": "PENDING", "presence_from": None, "presence_to": "CURRENT", "inclusion_from": None, "inclusion_to": None, "reason": None, "note": None},
                  {"event": "REVISE", "actor": "author", "record_id": original_id, "related_record_id": rid, "content": None, "approval_from": original["approval"], "approval_to": "SUPERSEDED", "presence_from": None, "presence_to": None, "inclusion_from": original["inclusion"] if original["approval"] == "APPROVED" else None, "inclusion_to": None, "reason": None, "note": note}]
        for edge in sorted(state["records"].values(), key=lambda r: r["id"]):
            if edge["kind"] == "edge" and edge["approval"] == "APPROVED" and (edge["content"]["source"] == original_id or edge["content"]["target"] == original_id):
                events.append({"event": "CASCADE", "actor": "system", "record_id": edge["id"], "related_record_id": None, "content": None, "approval_from": "APPROVED", "approval_to": "PENDING", "presence_from": None, "presence_to": None, "inclusion_from": None, "inclusion_to": None, "reason": None, "note": None})
        return _append_locked(root, {"shape": "REVISE", "prev_hash": state["head"]["terminal_hash"], "timestamp": timestamp, "context": None, "events": events}, expected_head, recovered)


def _finding(code: str, message: str, record_id: str | None = None) -> dict:
    return {"code": code, "message": message, "record_id": record_id}


_STAGE_C_PASSAGE = re.compile(r"^### Passage (p-[1-9][0-9]*)$")
_STAGE_C_GATE = re.compile(r"^### Gate Run ([1-9][0-9]*)$")
_STAGE_C_VIOLATION = re.compile(r"^### Violation (x-[0-9]{2,})$")
_STAGE_C_SPAN = re.compile(r"^paragraphs ([1-9][0-9]*)\u2013([1-9][0-9]*)$")
_STAGE_C_RESOLVED = re.compile(r"^RESOLVED \((\S(?:.*\S)?)\)$")
_STAGE_C_CHECKS = {
    "S1-span", "S1-composition", "S2-sentence", "S2-structural",
    "S3-coverage", "S3-overclaim", "S4-novelty", "S4-de-minimis",
}
_STAGE_C_RUN_FIELDS = (
    "Timestamp", "Judge", "Config schema", "Config", "Prior config refs",
    "Author relaxation", "Verdict",
)
_STAGE_C_VIOLATION_FIELDS = (
    "Check", "Draft span(s)", "Graph record", "Judgment", "Disposition",
)


def _stage_c_add(findings: list[dict], code: str, message: str, record_id: str | None = None) -> None:
    """Append one stable finding; Stage C validation must never raise on bad receipts."""
    findings.append(_finding(code, message, record_id))


def _stage_c_lines(path: Path) -> list[str] | None:
    """Strict UTF-8 reader retaining U+2028/U+2029 as ordinary value characters."""
    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        return None
    # Receipt line endings are presentation, unlike identity JSON values.  Do not use
    # splitlines(): it treats JSON-legal U+2028/U+2029 as record separators.
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def _stage_c_field(line: str) -> tuple[str, str] | None:
    """Parse a single exact ``Name: value`` line without accepting a bare colon."""
    if ": " not in line:
        return None
    name, value = line.split(": ", 1)
    return (name, value)


def _stage_c_paragraphs(raw: bytes, findings: list[dict]) -> int | None:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        _stage_c_add(findings, "DRAFT-INVALID-UTF8", "draft must decode as strict UTF-8 for paragraph mapping")
        return None
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return len([block for block in re.split(r"\n[ \t\f\v]*\n(?:[ \t\f\v]*\n)*", text) if block and not all(line.strip() == "" for line in block.split("\n"))])


def _stage_c_parse_block_fields(
    lines: list[str], start: int, stop: int, allowed: tuple[str, ...], findings: list[dict],
    code_prefix: str, subject: str, required: tuple[str, ...] | None = None,
) -> dict[str, list[str]]:
    """Collect fields, retaining duplicates so callers can itemize them."""
    fields: dict[str, list[str]] = {}
    for line in lines[start:stop]:
        if not line.strip():
            continue
        parsed = _stage_c_field(line)
        if parsed is None:
            _stage_c_add(findings, f"{code_prefix}-MALFORMED-FIELD", f"{subject} has malformed field line {line!r}")
            continue
        name, value = parsed
        if name not in allowed:
            _stage_c_add(findings, f"{code_prefix}-UNKNOWN-FIELD", f"{subject} has unknown field {name!r}")
            continue
        fields.setdefault(name, []).append(value)
    for name in (allowed if required is None else required):
        count = len(fields.get(name, []))
        if count == 0:
            _stage_c_add(findings, f"{code_prefix}-MISSING-FIELD", f"{subject} is missing {name}")
        elif count > 1:
            _stage_c_add(findings, f"{code_prefix}-DUPLICATE-FIELD", f"{subject} repeats {name}")
    return fields


def _stage_c_parse_passage(
    passage_id: str, fields: dict[str, list[str]], eligible: set[str], mapped: set[str],
    spans: list[tuple[int, int, str]], findings: list[dict],
) -> None:
    span = fields.get("Span", [None])[0]
    if span is not None:
        match = _STAGE_C_SPAN.fullmatch(span)
        if not match:
            _stage_c_add(findings, "PASSAGE-SPAN-GRAMMAR", f"passage {passage_id} has invalid Span")
        else:
            first, last = int(match.group(1)), int(match.group(2))
            if first > last:  # defensive; regex values are parsed deterministically.
                _stage_c_add(findings, "PASSAGE-SPAN-GRAMMAR", f"passage {passage_id} reverses its span")
            else:
                spans.append((first, last, passage_id))
    kind = fields.get("Kind", [None])[0]
    realizes = fields.get("Realizes", [])
    if kind is not None and kind not in {"MAPPED", "DE-MINIMIS"}:
        _stage_c_add(findings, "PASSAGE-KIND-GRAMMAR", f"passage {passage_id} has invalid Kind")
    if kind == "MAPPED":
        if len(realizes) == 0:
            _stage_c_add(findings, "PASSAGE-REALIZES-MISSING", f"mapped passage {passage_id} needs Realizes")
        elif realizes[0] == "":
            _stage_c_add(findings, "PASSAGE-REALIZES-EMPTY", f"mapped passage {passage_id} has empty Realizes")
        else:
            value = realizes[0]
            ids = value.split(", ")
            if ", ".join(ids) != value or any(not RID.fullmatch(rid) for rid in ids):
                _stage_c_add(findings, "PASSAGE-REALIZES-GRAMMAR", f"mapped passage {passage_id} has malformed Realizes")
            else:
                seen: set[str] = set()
                for rid in ids:
                    if rid in seen:
                        _stage_c_add(findings, "PASSAGE-REALIZES-DUPLICATE", f"mapped passage {passage_id} repeats {rid}", rid)
                    seen.add(rid)
                    if rid not in eligible:
                        _stage_c_add(findings, "PASSAGE-REALIZES-INELIGIBLE", f"mapped passage {passage_id} realizes an ineligible record", rid)
                    else:
                        mapped.add(rid)
    elif kind == "DE-MINIMIS" and realizes:
        _stage_c_add(findings, "PASSAGE-DE-MINIMIS-REALIZES", f"DE-MINIMIS passage {passage_id} forbids Realizes")


def _stage_c_parse_run(
    fields: dict[str, list[str]], header_verdict: str | None, records: dict, findings: list[dict],
) -> str | None:
    """Validate the one gate-run field set and return its legal verdict when available."""
    value = lambda name: fields.get(name, [None])[0]
    timestamp = value("Timestamp")
    if timestamp is not None:
        try:
            _timestamp(timestamp)
        except ApprovalGraphError:
            _stage_c_add(findings, "GATE-RUN-TIMESTAMP", "gate run Timestamp is not ledger UTC grammar")
    for name in ("Judge", "Prior config refs", "Author relaxation"):
        if value(name) is not None and ("\n" in value(name) or not value(name).strip()):
            _stage_c_add(findings, "GATE-RUN-EMPTY-FIELD", f"gate run {name} must be a nonempty single-line string")
    schema, config = value("Config schema"), value("Config")
    if schema is not None and config is not None and (schema != "UNAVAILABLE" or config != "I5-COMPARATOR-UNAVAILABLE"):
        _stage_c_add(findings, "GATE-RUN-CONFIG-PLACEHOLDER", "pre-Increment-4 run requires UNAVAILABLE and I5-COMPARATOR-UNAVAILABLE together")
    verdict = value("Verdict")
    if verdict is not None and verdict not in {"PASS", "ACTION-REQUIRED"}:
        _stage_c_add(findings, "GATE-RUN-VERDICT", "gate run Verdict must be PASS or ACTION-REQUIRED")
        verdict = None
    if verdict is not None and header_verdict is not None and verdict != header_verdict:
        _stage_c_add(findings, "RECEIPT-VERDICT-MISMATCH", "receipt envelope Verdict differs from sole gate run")
    return verdict


def _stage_c_parse_violation(
    violation_id: str, fields: dict[str, list[str]], records: dict, findings: list[dict],
) -> tuple[bool, str | None]:
    """Return whether the violation is OPEN and its valid check, if any."""
    value = lambda name: fields.get(name, [None])[0]
    check = value("Check")
    if check is not None and check not in _STAGE_C_CHECKS:
        _stage_c_add(findings, "VIOLATION-CHECK", f"violation {violation_id} has invalid Check")
        check = None
    for name in ("Draft span(s)", "Judgment"):
        item = value(name)
        if item is not None and (not item.strip() or "\n" in item):
            _stage_c_add(findings, "VIOLATION-EMPTY-FIELD", f"violation {violation_id} {name} must be nonempty single-line")
    graph_record = value("Graph record")
    if graph_record is not None:
        if graph_record == "NONE":
            if check != "S4-novelty":
                _stage_c_add(findings, "VIOLATION-GRAPH-RECORD", f"violation {violation_id} may use NONE only for S4-novelty")
        elif not RID.fullmatch(graph_record) or graph_record not in records:
            _stage_c_add(findings, "VIOLATION-GRAPH-RECORD", f"violation {violation_id} names no existing graph record")
    disposition = value("Disposition")
    opened = disposition == "OPEN"
    if disposition is not None and not opened and not _STAGE_C_RESOLVED.fullmatch(disposition):
        _stage_c_add(findings, "VIOLATION-DISPOSITION", f"violation {violation_id} has invalid Disposition")
    if opened:
        _stage_c_add(findings, "OPEN-VIOLATION", f"violation {violation_id} remains OPEN")
    return opened, check


def _stage_c(root: Path, state: dict, findings: list[dict]) -> None:
    """Perform deterministic Stage C validation only; it never gives semantic approval."""
    receipt = _inside(root, "Reconstruction_Receipt.md")
    draft = _inside(root, "Reconstruction_Draft.md")
    graph = _inside(root, "Approval_Graph.md")
    try:
        draft_raw = draft.read_bytes() if draft.exists() else None
    except Exception as exc:
        draft_raw = None
        _stage_c_add(findings, "DRAFT-READ-FAILED", f"cannot read current draft: {exc}")
    if draft_raw is None:
        _stage_c_add(findings, "DRAFT-MISSING", "current draft is required for acceptance")
    try:
        graph_raw = graph.read_bytes() if graph.exists() else None
    except Exception as exc:
        graph_raw = None
        _stage_c_add(findings, "GRAPH-READ-FAILED", f"cannot read current graph: {exc}")
    if graph_raw is None:
        _stage_c_add(findings, "GRAPH-MISSING", "current Approval_Graph.md is required for acceptance")
    if not receipt.exists():
        _stage_c_add(findings, "RECEIPT-MISSING", "current Reconstruction_Receipt.md is required for acceptance")
        _stage_c_add(findings, "I5-COMPARATOR-UNAVAILABLE", "structured gate configuration comparator is unavailable before Increment 4")
        return

    identity = None
    try:
        identity = _receipt_identity(receipt)
    except ApprovalGraphError as exc:
        _stage_c_add(findings, exc.code, exc.message, exc.record_id)
    lines = _stage_c_lines(receipt)
    if lines is None:
        _stage_c_add(findings, "RECEIPT-INVALID-UTF8", "receipt must decode as strict UTF-8")
    header_verdict = None
    if lines is not None and len(lines) >= 3 and lines[2].startswith("Verdict: "):
        candidate = lines[2][9:]
        if candidate in {"PASS", "ACTION-REQUIRED"}:
            header_verdict = candidate

    if identity is not None:
        if identity.get("draft_filename") != "Reconstruction_Draft.md":
            _stage_c_add(findings, "DRAFT-IDENTITY-MISMATCH", "receipt must identify Reconstruction_Draft.md")
        if draft_raw is not None and hashlib.sha256(draft_raw).hexdigest() != identity["draft_sha256"]:
            _stage_c_add(findings, "DRAFT-HASH-MISMATCH", "receipt draft hash does not match current draft")
        if graph_raw is not None and hashlib.sha256(graph_raw).hexdigest() != identity["graph_sha256"]:
            _stage_c_add(findings, "GRAPH-HASH-MISMATCH", "receipt graph hash does not match current projection")
        try:
            canonical_graph = project_graph(state)
            if hashlib.sha256(canonical_graph).hexdigest() != identity["graph_sha256"]:
                _stage_c_add(findings, "GRAPH-IDENTITY-MISMATCH", "receipt graph hash does not bind canonical replay projection")
        except Exception as exc:
            _stage_c_add(findings, "GRAPH-CANONICALIZATION-FAILED", f"cannot render canonical graph: {exc}")
        head = state.get("head", {}) if isinstance(state, dict) else {}
        if identity.get("bundle_count") != head.get("bundle_count") or identity.get("terminal_hash") != head.get("terminal_hash"):
            _stage_c_add(findings, "RECEIPT-STALE", "current receipt does not bind current ledger head")

    if lines is not None:
        # The exact envelope occupies the first three lines.  Its parser owns the
        # canonical identity JSON; this parser owns all receipt body grammar.
        body = lines[3:]
        records = state.get("records", {}) if isinstance(state, dict) and isinstance(state.get("records"), dict) else {}
        try:
            eligible = eligible_ids(state)
        except Exception:
            eligible = set()
            _stage_c_add(findings, "STAGE-C-STATE-INVALID", "cannot derive eligible record IDs from replay state")
        mapped: set[str] = set()
        spans: list[tuple[int, int, str]] = []
        passage_ids: set[str] = set()
        violation_ids: set[str] = set()
        gate_headers: list[tuple[int, str]] = []
        violation_markers = [i for i, line in enumerate(body) if line == "#### Violations"]
        owned = set(violation_markers)
        headers = [(i, line) for i, line in enumerate(body) if line.startswith("### ")]

        for idx, line in headers:
            match = _STAGE_C_PASSAGE.fullmatch(line)
            if match:
                passage_id = match.group(1)
                if passage_id in passage_ids:
                    _stage_c_add(findings, "PASSAGE-ID-DUPLICATE", f"duplicate passage ID {passage_id}")
                passage_ids.add(passage_id)
                next_header = next((j for j, _ in headers if j > idx), len(body))
                marker = next((j for j in violation_markers if idx < j < next_header), next_header)
                owned.update(range(idx, marker))
                fields = _stage_c_parse_block_fields(body, idx + 1, marker, ("Span", "Kind", "Realizes"), findings, "PASSAGE", f"passage {passage_id}", ("Span", "Kind"))
                _stage_c_parse_passage(passage_id, fields, eligible, mapped, spans, findings)
                continue
            match = _STAGE_C_GATE.fullmatch(line)
            if match:
                gate_headers.append((idx, match.group(1)))
                continue
            match = _STAGE_C_VIOLATION.fullmatch(line)
            if match:
                violation_id = match.group(1)
                if violation_id in violation_ids:
                    _stage_c_add(findings, "VIOLATION-ID-DUPLICATE", f"duplicate violation ID {violation_id}")
                violation_ids.add(violation_id)
                next_header = next((j for j, _ in headers if j > idx), len(body))
                owned.update(range(idx, next_header))
                fields = _stage_c_parse_block_fields(body, idx + 1, next_header, _STAGE_C_VIOLATION_FIELDS, findings, "VIOLATION", f"violation {violation_id}")
                _stage_c_parse_violation(violation_id, fields, records, findings)
                continue
            _stage_c_add(findings, "RECEIPT-UNKNOWN-BLOCK", f"unknown receipt block {line!r}")

        if len(gate_headers) != 1:
            _stage_c_add(findings, "GATE-RUN-COUNT", "receipt requires exactly one valid Gate Run block")
        else:
            gate_index, gate_number = gate_headers[0]
            if any(index > gate_index for index, line in headers if _STAGE_C_PASSAGE.fullmatch(line)):
                _stage_c_add(findings, "PASSAGE-ORDER", "passage blocks must precede the Gate Run")
            marker_after = [i for i in violation_markers if i > gate_index]
            stop = marker_after[0] if marker_after else len(body)
            owned.update(range(gate_index, stop))
            fields = _stage_c_parse_block_fields(body, gate_index + 1, stop, _STAGE_C_RUN_FIELDS, findings, "GATE-RUN", f"Gate Run {gate_number}")
            run_verdict = _stage_c_parse_run(fields, header_verdict, records, findings)
            if run_verdict == "PASS" and any(f.get("code") == "OPEN-VIOLATION" for f in findings):
                _stage_c_add(findings, "PASS-OPEN-INCONSISTENT", "PASS gate run cannot contain an OPEN violation")
        if len(violation_markers) != 1:
            _stage_c_add(findings, "VIOLATIONS-MARKER-COUNT", "receipt requires exactly one #### Violations marker")

        for index, line in enumerate(body):
            if line.strip() and index not in owned:
                _stage_c_add(findings, "RECEIPT-ORPHAN-CONTENT", f"receipt body has unexpected content {line!r}")

        paragraph_count = _stage_c_paragraphs(draft_raw, findings) if draft_raw is not None else None
        if paragraph_count == 0:
            _stage_c_add(findings, "DRAFT-EMPTY", "draft has zero paragraph blocks")
        if paragraph_count is not None:
            coverage = [0] * paragraph_count
            for first, last, passage_id in spans:
                if first > paragraph_count or last > paragraph_count:
                    _stage_c_add(findings, "PASSAGE-SPAN-OUT-OF-RANGE", f"passage {passage_id} exceeds draft paragraph count")
                    continue
                for paragraph in range(first, last + 1):
                    coverage[paragraph - 1] += 1
            for number, count in enumerate(coverage, 1):
                if count == 0:
                    _stage_c_add(findings, "PASSAGE-COVERAGE-GAP", f"draft paragraph {number} has no passage record")
                elif count > 1:
                    _stage_c_add(findings, "PASSAGE-COVERAGE-OVERLAP", f"draft paragraph {number} belongs to multiple passage records")
        for rid, rec in records.items():
            if rec.get("kind") == "node" and rec.get("inclusion") == "REQUIRED" and rid not in mapped:
                _stage_c_add(findings, "REQUIRED-NODE-UNCOVERED", "required node appears in no mapped passage", rid)

    # This is intentionally unconditional and last: Increment 1 has no config
    # comparator, so a well-shaped recorded run can never cause a semantic PASS.
    _stage_c_add(findings, "I5-COMPARATOR-UNAVAILABLE", "structured gate configuration comparator is unavailable before Increment 4")


def validate_project(project: str | Path, stage: str) -> dict:
    """Validate/recover a project and return the stable validation result shape."""
    if stage not in {"graph", "draft-ready", "acceptance"}: raise _err("INVALID-STAGE", "stage must be graph, draft-ready, or acceptance")
    findings: list[dict] = []; rebuilt: list[str] = []; recovered = 0; state = None
    try:
        root = _project_root(project)
    except ApprovalGraphError as exc:
        findings.append(_finding(exc.code, exc.message, exc.record_id))
        if stage == "acceptance": findings.append(_finding("I5-COMPARATOR-UNAVAILABLE", "structured gate configuration comparator is unavailable before Increment 4"))
        return {"verdict": "ACTION-REQUIRED", "stage": stage, "head": None, "findings": findings, "projection_rebuilt": [], "recovered_bytes": 0}
    except Exception as exc:
        findings.append(_finding("OPERATION-FAILED", str(exc)))
        if stage == "acceptance": findings.append(_finding("I5-COMPARATOR-UNAVAILABLE", "structured gate configuration comparator is unavailable before Increment 4"))
        return {"verdict": "ACTION-REQUIRED", "stage": stage, "head": None, "findings": findings, "projection_rebuilt": [], "recovered_bytes": 0}
    try:
        with _ProjectLock(root):
            try:
                bundles, recovered = _read_ledger(root, allow_missing=False)
            except ApprovalGraphError as exc:
                findings.append(_finding(exc.code, exc.message, exc.record_id))
                if stage == "acceptance": findings.append(_finding("I5-COMPARATOR-UNAVAILABLE", "structured gate configuration comparator is unavailable before Increment 4"))
                return {"verdict": "ACTION-REQUIRED", "stage": stage, "head": None, "findings": findings, "projection_rebuilt": [], "recovered_bytes": recovered}
            try:
                state = replay(bundles)
                _receipt_prefix_check(root, bundles)
            except ApprovalGraphError as exc:
                findings.append(_finding(exc.code, exc.message, exc.record_id))
                if stage == "acceptance": findings.append(_finding("I5-COMPARATOR-UNAVAILABLE", "structured gate configuration comparator is unavailable before Increment 4"))
                return {"verdict": "ACTION-REQUIRED", "stage": stage, "head": None, "findings": findings, "projection_rebuilt": [], "recovered_bytes": recovered}
            for bundle in state["bundles"]:
                try:
                    _check_bundle_sources(root, bundle)
                    _check_quarantine_artifact(root, bundle)
                except ApprovalGraphError as exc:
                    findings.append(_finding(exc.code, exc.message, exc.record_id))
            findings.extend(_check_sources(root, state))
            try: rebuilt = _publish(root, state)
            except Exception as exc: findings.append(_finding("PROJECTION-PUBLISH-FAILED", str(exc)))
            if stage in {"draft-ready", "acceptance"}:
                if not bundles or not any(b["shape"] == "MINT" for b in bundles): findings.append(_finding("UNSTARTED-GRAPH", "draft-readiness requires a nonempty MINT-derived graph"))
                if any(r["approval"] == "PENDING" for r in state["records"].values()): findings.append(_finding("PENDING-RECORDS", "all records must leave PENDING before drafting"))
                for rid, rec in state["records"].items():
                    if rec["kind"] == "node" and rec["approval"] == "APPROVED" and rec["inclusion"] is None: findings.append(_finding("MISSING-INCLUSION", "approved node has no Inclusion", rid))
                    if rec["kind"] == "node" and rec["inclusion"] == "REQUIRED" and rid not in eligible_ids(state): findings.append(_finding("REQUIRED-BUT-WITHHELD", "required node is not eligible/current", rid))
            if stage == "acceptance": _stage_c(root, state, findings)
    except ApprovalGraphError as exc:
        findings.append(_finding(exc.code, exc.message, exc.record_id))
        if stage == "acceptance": findings.append(_finding("I5-COMPARATOR-UNAVAILABLE", "structured gate configuration comparator is unavailable before Increment 4"))
        return {"verdict": "ACTION-REQUIRED", "stage": stage, "head": state["head"] if state else None, "findings": findings, "projection_rebuilt": rebuilt, "recovered_bytes": recovered}
    except Exception as exc:
        findings.append(_finding("OPERATION-FAILED", str(exc)))
        if stage == "acceptance": findings.append(_finding("I5-COMPARATOR-UNAVAILABLE", "structured gate configuration comparator is unavailable before Increment 4"))
        return {"verdict": "ACTION-REQUIRED", "stage": stage, "head": state["head"] if state else None, "findings": findings, "projection_rebuilt": rebuilt, "recovered_bytes": recovered}
    return {"verdict": "PASS" if not findings else "ACTION-REQUIRED", "stage": stage, "head": state["head"] if state else {"bundle_count": 0, "terminal_hash": "GENESIS"}, "findings": findings, "projection_rebuilt": rebuilt, "recovered_bytes": recovered}


def _self_test() -> int:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root = Path(td); source = root / "manuscript.md"; source.write_text("A source quote.", encoding="utf-8")
        ctx = {"source_filename": "manuscript.md", "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "argument_state": "Argument_State_v1"}
        content = {"type": "CLAIM", "text": "A source quote.", "anchors": [{"quote": "A source quote.", "location": "p1"}], "origin": "MANUSCRIPT", "provenance": ["STATE:Argument_State_v1:C1"], "flags": ["NONE"]}
        rid = node_id(content["type"], content["text"])
        e = {"event": "MINTED", "actor": "normalizer", "record_id": rid, "related_record_id": None, "content": content, "approval_from": None, "approval_to": "PENDING", "presence_from": None, "presence_to": "CURRENT", "inclusion_from": None, "inclusion_to": None, "reason": None, "note": None}
        bundle = seal_bundle({"shape": "MINT", "prev_hash": "GENESIS", "timestamp": "2026-01-01T00:00:00Z", "context": ctx, "events": [e]})
        result = append_bundle(root, bundle, {"bundle_count": 0, "terminal_hash": "GENESIS"})
        assert result["status"] == "COMMITTED" and replay([bundle])["records"][rid]["approval"] == "PENDING"
        check = validate_project(root, "graph"); assert check["verdict"] == "PASS", check
        assert parse_graph(project_graph(replay([bundle])))['nodes'][0]['id'] == rid
    print("approval_graph self-test: PASS")
    return 0


def _usage_error(message: str) -> int:
    print(canonical_json({"error": "USAGE", "message": message, "committed": False, "record_id": None}), file=sys.stdout)
    return 2


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["--self-test"]: return _self_test()
    if not args: return _usage_error("a project and explicit operation are required")
    project = args[0]
    if "--stage" in args:
        if "--append-bundle" in args: return _usage_error("append and stage cannot be combined")
        if len(args) != 3 or args[1] != "--stage" or args[2] not in {"graph", "draft-ready", "acceptance"}: return _usage_error("validation requires PROJECT --stage graph|draft-ready|acceptance")
        try:
            result = validate_project(project, args[2]); print(canonical_json(result)); return 0 if result["verdict"] == "PASS" else 1
        except ApprovalGraphError as exc:
            print(canonical_json({"error": exc.code, "message": exc.message, "committed": exc.committed, "record_id": exc.record_id})); return 1
    if "--append-bundle" in args:
        if len(args) != 7 or args[1] != "--append-bundle" or args[3] != "--expected-count" or args[5] != "--expected-hash": return _usage_error("append requires PROJECT --append-bundle FILE --expected-count N --expected-hash H")
        result = None
        try:
            count = int(args[4]); digest = args[6]
            if count < 0 or (count == 0 and digest != "GENESIS") or (count > 0 and not HEX64.fullmatch(digest)):
                raise _err("INVALID-EXPECTED-HEAD", "expected count/hash pair is invalid")
            p = Path(args[2]); raw = p.read_bytes()
            if not raw.endswith(b"\n") or raw.count(b"\n") != 1: return _usage_error("append file must contain exactly one LF-terminated bundle")
            obj = _parse_ledger_bytes(raw)[0]
            result = append_bundle(project, obj, {"bundle_count": count, "terminal_hash": digest}); print(canonical_json(result)); return 0
        except ApprovalGraphError as exc:
            print(canonical_json({"error": exc.code, "message": exc.message, "committed": exc.committed, "record_id": exc.record_id})); return 1
        except Exception as exc:
            committed = True if isinstance(result, dict) and result.get("status") == "COMMITTED" else False
            print(canonical_json({"error": "OPERATION-FAILED", "message": str(exc), "committed": committed, "record_id": None})); return 1
    return _usage_error("unknown operation")


if __name__ == "__main__":
    raise SystemExit(main())
