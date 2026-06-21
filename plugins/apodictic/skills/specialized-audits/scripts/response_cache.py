#!/usr/bin/env python3
"""
Response cache for APODICTIC research mode API calls.

Simple in-memory + optional disk cache. Prevents re-fetching the same
DOI/title/URL within a single verification run, and (with a TTL) across runs
without ever letting a stale payload pass as fresh.

TTL / freshness (research-reliability-layer): disk entries are wrapped in a
freshness envelope `{ "_cached_at": <ts>, "_payload": <value> }` so staleness is
computable. `get(key, ttl_seconds=...)` re-fetches (returns a MISS) when an
entry is older than the TTL. The envelope is backward-compatible: a legacy
un-enveloped file is treated as freshness-unknown and NEVER auto-expired, and a
caller that passes no TTL gets today's never-expire-on-age behavior.

The no-sticky-error rule is unchanged and load-bearing: dicts containing
`_error` are kept MEMORY-ONLY and never written to disk, so a transient outage
cannot stick across runs and masquerade as a ghost citation — and is therefore
never TTL-cached on disk in the first place.
"""

import json
import hashlib
import time
from pathlib import Path


class ResponseCache:
    """In-memory cache with optional disk persistence and optional TTL freshness."""

    def __init__(self, cache_dir: str | None = None, now=None):
        self._memory: dict[str, dict] = {}
        # Parallel freshness stamps for in-memory entries (seconds, or None when
        # freshness is unknown — e.g. a legacy disk file lacking a stamp).
        self._stamp: dict[str, float | None] = {}
        self._hits = 0
        self._misses = 0
        self._cache_dir = Path(cache_dir) if cache_dir else None
        # Injectable clock for deterministic TTL tests (no sleep).
        self._now = now if now is not None else time.time
        if self._cache_dir:
            self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _disk_path(self, key: str) -> Path | None:
        if not self._cache_dir:
            return None
        h = hashlib.sha256(key.encode()).hexdigest()[:16]
        return self._cache_dir / f"{h}.json"

    @staticmethod
    def _unwrap(data):
        """Return (payload, cached_at). Accepts both the freshness envelope and a
        legacy un-enveloped payload. A legacy payload has cached_at=None
        (freshness unknown → never auto-expired)."""
        if isinstance(data, dict) and "_cached_at" in data and "_payload" in data:
            return data["_payload"], data["_cached_at"]
        return data, None

    def get(self, key: str, ttl_seconds: float | None = None) -> dict | None:
        """Get a cached response. Returns None on miss.

        ttl_seconds is None ⇒ never expires on age (today's behavior). When a TTL
        is given and the entry's freshness stamp is older than it, the entry is a
        MISS (re-fetch) and the stale in-memory copy is dropped. An entry with an
        unknown stamp (legacy file) is never aged out."""
        if key in self._memory:
            stamp = self._stamp.get(key)
            if self._expired(stamp, ttl_seconds):
                # Drop the stale in-memory copy and fall through to disk/miss.
                del self._memory[key]
                self._stamp.pop(key, None)
            else:
                self._hits += 1
                return self._memory[key]

        disk = self._disk_path(key)
        if disk and disk.exists():
            try:
                raw = json.loads(disk.read_text())
                payload, cached_at = self._unwrap(raw)
                if self._expired(cached_at, ttl_seconds):
                    # Stale on disk → treat as a miss; the caller re-fetches and
                    # set() overwrites with a fresh stamp.
                    self._misses += 1
                    return None
                self._memory[key] = payload
                self._stamp[key] = cached_at
                self._hits += 1
                return payload
            except (json.JSONDecodeError, OSError):
                pass

        self._misses += 1
        return None

    def _expired(self, cached_at: float | None, ttl_seconds: float | None) -> bool:
        if ttl_seconds is None or cached_at is None:
            return False
        return (self._now() - cached_at) > ttl_seconds

    def set(self, key: str, value: dict, ttl: float | None = None) -> None:
        """Store a response in cache. Transient error payloads (dicts containing
        `_error`, e.g. a retry-exhausted 429/5xx) are kept MEMORY-ONLY and never
        written to disk — otherwise a temporary outage would stick across runs and
        keep masquerading as an unretrievable/ghost citation until the cache is
        cleared by hand.

        Successful payloads are written inside a freshness envelope so a later
        get(key, ttl_seconds=...) can age them out. The `ttl` parameter is
        accepted for symmetry / caller intent; expiry is enforced at read time
        (get) against whichever ttl_seconds the caller passes, so the same disk
        entry can be read under different TTLs. An `_error` payload is never
        written regardless of any ttl — preserving the no-sticky-error rule."""
        now = self._now()
        self._memory[key] = value
        if isinstance(value, dict) and "_error" in value:
            # No-sticky-error: memory-only, no stamp, never to disk — even with a
            # TTL. This is the load-bearing Phase 5 invariant; the envelope must
            # not regress it.
            self._stamp[key] = None
            return
        self._stamp[key] = now
        disk = self._disk_path(key)
        if disk:
            envelope = {"_cached_at": now, "_payload": value}
            try:
                disk.write_text(json.dumps(envelope, default=str))
            except OSError:
                pass

    def stats(self) -> dict:
        """Return cache statistics."""
        return {
            "entries": len(self._memory),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / max(1, self._hits + self._misses), 2)
        }


# ---------------------------------------------------------------------------
# Self-test (introduced with the reliability layer). Deterministic via an
# injected clock — no sleep. Run directly from CI.
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    import tempfile

    failures: list[str] = []
    passed = [0]

    def expect(name, got, want):
        if got == want:
            passed[0] += 1
        else:
            failures.append(f"{name}: got {got!r}, want {want!r}")

    with tempfile.TemporaryDirectory() as d:
        clock = {"t": 0.0}
        cache = ResponseCache(d, now=lambda: clock["t"])

        # -- AC-4: TTL expiry is deterministic -------------------------------
        cache.set("crossref:doi:10.x", {"message": {"DOI": "10.x"}})  # stamped at t=0
        clock["t"] = 5.0
        hit = cache.get("crossref:doi:10.x", ttl_seconds=10)
        expect("ac4_hit_within_ttl", hit, {"message": {"DOI": "10.x"}})
        clock["t"] = 11.0
        miss = cache.get("crossref:doi:10.x", ttl_seconds=10)
        expect("ac4_miss_after_ttl", miss, None)
        # No-TTL read always hits a present (even old) entry. Re-seed on disk
        # because the prior expiring read dropped the in-memory copy.
        clock["t"] = 0.0
        cache.set("crossref:doi:10.x", {"message": {"DOI": "10.x"}})
        clock["t"] = 10_000.0
        expect("ac4_no_ttl_never_expires",
               cache.get("crossref:doi:10.x"), {"message": {"DOI": "10.x"}})

        # Legacy un-enveloped file is never auto-expired.
        import hashlib
        legacy_key = "openalex:search:old:thing"
        h = hashlib.sha256(legacy_key.encode()).hexdigest()[:16]
        (Path(d) / f"{h}.json").write_text(json.dumps({"results": [1]}))  # no envelope
        legacy_cache = ResponseCache(d, now=lambda: 10_000_000.0)
        expect("ac4_legacy_never_expires",
               legacy_cache.get(legacy_key, ttl_seconds=1), {"results": [1]})

    # -- AC-5: no-sticky-error preserved under the envelope ------------------
    with tempfile.TemporaryDirectory() as d2:
        c = ResponseCache(d2, now=lambda: 0.0)
        c.set("crossref:doi:bad", {"_error": "429", "_url": "x"}, ttl=999)
        # Nothing on disk for an _error payload, even with a ttl.
        import hashlib
        h = hashlib.sha256("crossref:doi:bad".encode()).hexdigest()[:16]
        on_disk = (Path(d2) / f"{h}.json").exists()
        expect("ac5_error_not_on_disk", on_disk, False)
        # A FRESH in-memory cache (no memory carry-over) is a miss.
        c2 = ResponseCache(d2, now=lambda: 0.0)
        expect("ac5_fresh_cache_miss_on_error", c2.get("crossref:doi:bad"), None)
        # Same cache still serves it from memory (the Phase-5 in-run behavior).
        expect("ac5_same_cache_memory_hit", c.get("crossref:doi:bad"),
               {"_error": "429", "_url": "x"})

        # A successful payload IS written (and wrapped in an envelope on disk).
        c.set("crossref:doi:good", {"message": {"DOI": "10.x"}})
        h2 = hashlib.sha256("crossref:doi:good".encode()).hexdigest()[:16]
        raw = json.loads((Path(d2) / f"{h2}.json").read_text())
        expect("ac5_good_enveloped", "_cached_at" in raw and "_payload" in raw, True)
        expect("ac5_good_payload_intact", raw["_payload"], {"message": {"DOI": "10.x"}})

    total = passed[0] + len(failures)
    if failures:
        print(f"response_cache self-test: FAIL ({len(failures)}/{total} checks failed)")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"response_cache self-test: PASS ({passed[0]}/{total} checks)")
    return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2 and sys.argv[1] == "--self-test":
        sys.exit(run_self_test())
    print(__doc__)
    print("Usage: python response_cache.py --self-test")
