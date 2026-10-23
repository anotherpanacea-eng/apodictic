#!/usr/bin/env python3
"""
Provenance tracking for APODICTIC Citation Verifier.

Every API response used during resolution is stored as a provenance entry.
Verdicts and claims about sources must trace back to stored entries.

Learned from PhilLit's anti-hallucination architecture: provenance is
enforced by audit trail, not by prompt instruction.
"""

import json
import copy
import hashlib
import math
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def is_admitted_json(value) -> bool:
    """Accept exactly finite, acyclic parsed JSON values, without coercion."""
    active = set()

    def valid(node):
        if node is None or type(node) in (bool, int):
            return True
        if type(node) is float:
            return math.isfinite(node)
        if type(node) is str:
            return not any(0xD800 <= ord(char) <= 0xDFFF for char in node)
        if type(node) not in (list, dict):
            return False
        identity = id(node)
        if identity in active:
            return False
        active.add(identity)
        try:
            if type(node) is list:
                return all(valid(item) for item in node)
            return all(type(key) is str and valid(key) and valid(item)
                       for key, item in node.items())
        finally:
            active.remove(identity)

    try:
        return valid(value)
    except RecursionError:
        return False


def json_value_sha256(value) -> str:
    """Digest a previously admitted parsed JSON value, never HTTP wire bytes."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class ProvenanceStore:
    """Stores API response provenance for citation verification."""

    def __init__(self, record_responses: bool = False):
        self.entries: list[dict] = []
        self._counter = 0
        self.record_responses = record_responses
        self._events: list[dict] = []
        self._evidence_incomplete = False
        self._citation_index: int | None = None

    def _record_response(self, ref_id, source, *, kind, outcome, origin,
                         payload=None, observed_at=None, category=None, status=None,
                         details=None):
        if not self.record_responses:
            return None
        if self._evidence_incomplete:
            raise RuntimeError("response evidence collection is incomplete")
        event = {
            "event_id": f"response-{len(self._events) + 1}",
            "citation_index": self._citation_index,
            "ref_id": ref_id,
            "source": source,
            "kind": kind,
            "outcome": outcome,
            "origin": origin,
            "observed_at": observed_at,
            "recorded_at": _utc_now(),
            "prov_ref": None,
        }
        if kind == "json_value":
            if not is_admitted_json(payload):
                raise ValueError("invalid parsed JSON evidence value")
            try:
                snapshot = copy.deepcopy(payload)
                digest = json_value_sha256(snapshot)
            except Exception:
                self._evidence_incomplete = True
                raise
            event.update(representation="parsed-json-value-v1", payload=snapshot,
                         payload_sha256=digest)
        if category is not None:
            event["category"] = category
        if status is not None:
            event["status"] = status
        if details:
            event.update(details)
        self._events.append(event)
        return len(self._events) - 1

    def _observe_parsed(self, ref_id, source, value, *, origin, observed_at):
        if is_admitted_json(value):
            return self._record_response(ref_id, source, kind="json_value",
                                         outcome="invalid", origin=origin,
                                         payload=value, observed_at=observed_at)
        return self._record_response(ref_id, source,
                                     kind="request_failure" if origin == "fresh" else "cache_invalid",
                                     outcome="invalid",
                                     origin="local" if origin == "fresh" else origin,
                                     category="invalid-json-value")

    def _finish_response(self, event_index, outcome, prov_ref=None):
        if event_index is None:
            return
        event = self._events[event_index]
        if event["kind"] == "json_value":
            event["outcome"] = outcome
        if prov_ref is not None:
            event["prov_ref"] = prov_ref

    def _cache_metadata(self, event_index):
        if event_index is None:
            return None
        event = self._events[event_index]
        if event["kind"] != "json_value" or event["origin"] != "fresh":
            return None
        return {"kind": "provider_json", "observed_at": event["observed_at"],
                "payload_sha256": event["payload_sha256"]}

    def response_evidence(self) -> dict:
        if not self.record_responses:
            raise RuntimeError("response evidence was not enabled")
        if self._evidence_incomplete:
            raise RuntimeError("response evidence collection is incomplete")
        try:
            return copy.deepcopy({"schema": "apodictic.response-evidence.v1",
                                  "events": self._events})
        except Exception:
            self._evidence_incomplete = True
            raise

    def save_response_evidence(self, path: str) -> str:
        document = self.response_evidence()
        # Verify and serialize before creating a temporary destination.
        try:
            for event in document["events"]:
                if event["kind"] == "json_value":
                    if (not is_admitted_json(event["payload"]) or
                            json_value_sha256(event["payload"]) != event["payload_sha256"]):
                        raise RuntimeError("response evidence digest mismatch")
            encoded = json.dumps(document, indent=2, ensure_ascii=False,
                                 allow_nan=False).encode("utf-8")
        except Exception:
            self._evidence_incomplete = True
            raise
        target = Path(path)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="wb", dir=target.parent,
                                             prefix=f".{target.name}.", suffix=".tmp",
                                             delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(encoded)
            os.replace(temporary, target)
            temporary = None  # replacement is the success commit point
        finally:
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass
        return str(path)

    def store(self, ref_id: str, source: str, response: dict) -> str:
        """
        Store an API response and return a provenance reference ID.

        Args:
            ref_id: The citation reference ID this response relates to
            source: The API source (e.g., "crossref", "semantic-scholar", "unpaywall")
            response: The raw API response

        Returns:
            A provenance reference string (e.g., "prov-3-crossref")
        """
        self._counter += 1
        prov_ref = f"prov-{self._counter}-{source}"

        self.entries.append({
            "prov_ref": prov_ref,
            "ref_id": ref_id,
            "source": source,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "response_keys": list(response.keys()) if isinstance(response, dict) else [],
            "has_error": "_error" in response if isinstance(response, dict) else False,
            # Store a summary, not the full response (which may be large)
            "response_summary": _summarize(response),
        })

        return prov_ref

    def verify(self, ref_id: str) -> list[dict]:
        """Return all provenance entries for a given citation ref_id."""
        return [e for e in self.entries if e["ref_id"] == ref_id]

    def has_provenance(self, ref_id: str) -> bool:
        """Check whether any provenance exists for a ref_id."""
        return any(e["ref_id"] == ref_id for e in self.entries)

    def save(self, path: str) -> None:
        """Save provenance store to disk."""
        Path(path).write_text(json.dumps(self.entries, indent=2, default=str))

    def summary(self) -> dict:
        """Return a summary of the provenance store."""
        sources = {}
        for e in self.entries:
            sources[e["source"]] = sources.get(e["source"], 0) + 1
        return {
            "total_entries": len(self.entries),
            "by_source": sources,
            "ref_ids_covered": len(set(e["ref_id"] for e in self.entries)),
            "errors": sum(1 for e in self.entries if e["has_error"])
        }


def _summarize(response: dict) -> str:
    """Create a brief summary of an API response for the provenance log."""
    if not isinstance(response, dict):
        return str(response)[:200]

    if "_error" in response:
        return f"ERROR: {response['_error']}"

    # CrossRef
    if isinstance(response.get("message"), dict) and "DOI" in response["message"]:
        msg = response["message"]
        title = msg.get("title")
        if isinstance(title, list):
            title = title[0] if title and isinstance(title[0], str) else ""
        if isinstance(title, str) and title:
            return f"CrossRef: {title[:80]}"
        return "CrossRef: title unavailable"

    # Semantic Scholar
    if "data" in response:
        items = response["data"]
        if isinstance(items, list):
            if items and isinstance(items[0], dict) and isinstance(items[0].get("title"), str):
                return f"S2: {len(items)} results, first: {items[0]['title'][:60]}"
            return f"S2: {len(items)} results"

    # OpenAlex
    if isinstance(response.get("results"), list) and "meta" in response:
        results = response["results"]
        meta = response.get("meta")
        count = meta.get("count", len(results)) if isinstance(meta, dict) else len(results)
        if type(count) is not int or count < 0:
            count = len(results)
        return f"OpenAlex: {count} results"

    # Wayback
    if "archived_snapshots" in response:
        snapshots = response.get("archived_snapshots")
        closest = snapshots.get("closest", {}) if isinstance(snapshots, dict) else {}
        if isinstance(closest, dict) and closest.get("available"):
            return f"Wayback: available, {closest.get('timestamp', '')}"
        return "Wayback: no snapshot"

    # Unpaywall
    if "best_oa_location" in response:
        oa = response.get("best_oa_location", {})
        if isinstance(oa, dict) and oa:
            pdf = oa.get("url_for_pdf")
            return f"Unpaywall: OA at {pdf[:60]}" if isinstance(pdf, str) and pdf else "Unpaywall: no PDF"
        return "Unpaywall: no OA"

    # Generic
    keys = list(response.keys())[:5]
    return f"Response keys: {keys}"
