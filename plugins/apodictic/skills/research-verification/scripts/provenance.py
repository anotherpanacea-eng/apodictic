#!/usr/bin/env python3
"""
Provenance tracking for APODICTIC Citation Verifier.

Every API response used during resolution is stored as a provenance entry.
Verdicts and claims about sources must trace back to stored entries.

Learned from PhilLit's anti-hallucination architecture: provenance is
enforced by audit trail, not by prompt instruction.
"""

import json
import time
from pathlib import Path


class ProvenanceStore:
    """Stores API response provenance for citation verification."""

    def __init__(self):
        self.entries: list[dict] = []
        self._counter = 0

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
    if "message" in response and "DOI" in response.get("message", {}):
        msg = response["message"]
        title = msg.get("title", [""])[0] if isinstance(msg.get("title"), list) else msg.get("title", "")
        return f"CrossRef: {title[:80]}"

    # Semantic Scholar
    if "data" in response:
        items = response["data"]
        if items and isinstance(items, list):
            return f"S2: {len(items)} results, first: {items[0].get('title', '')[:60]}"

    # OpenAlex
    if "results" in response and "meta" in response:
        results = response["results"]
        count = response.get("meta", {}).get("count", len(results))
        return f"OpenAlex: {count} results"

    # Wayback
    if "archived_snapshots" in response:
        closest = response.get("archived_snapshots", {}).get("closest", {})
        if closest.get("available"):
            return f"Wayback: available, {closest.get('timestamp', '')}"
        return "Wayback: no snapshot"

    # Unpaywall
    if "best_oa_location" in response:
        oa = response.get("best_oa_location", {})
        if oa:
            return f"Unpaywall: OA at {oa.get('url_for_pdf', 'no PDF')[:60]}"
        return "Unpaywall: no OA"

    # Generic
    keys = list(response.keys())[:5]
    return f"Response keys: {keys}"
