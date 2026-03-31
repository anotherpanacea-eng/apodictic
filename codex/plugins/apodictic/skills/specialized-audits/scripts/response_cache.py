#!/usr/bin/env python3
"""
Response cache for APODICTIC research mode API calls.

Simple in-memory + optional disk cache. Prevents re-fetching the same
DOI/title/URL within a single verification run.
"""

import json
import hashlib
from pathlib import Path


class ResponseCache:
    """In-memory cache with optional disk persistence."""

    def __init__(self, cache_dir: str | None = None):
        self._memory: dict[str, dict] = {}
        self._hits = 0
        self._misses = 0
        self._cache_dir = Path(cache_dir) if cache_dir else None
        if self._cache_dir:
            self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _disk_path(self, key: str) -> Path | None:
        if not self._cache_dir:
            return None
        h = hashlib.sha256(key.encode()).hexdigest()[:16]
        return self._cache_dir / f"{h}.json"

    def get(self, key: str) -> dict | None:
        """Get a cached response. Returns None on miss."""
        if key in self._memory:
            self._hits += 1
            return self._memory[key]

        disk = self._disk_path(key)
        if disk and disk.exists():
            try:
                data = json.loads(disk.read_text())
                self._memory[key] = data
                self._hits += 1
                return data
            except (json.JSONDecodeError, OSError):
                pass

        self._misses += 1
        return None

    def set(self, key: str, value: dict) -> None:
        """Store a response in cache."""
        self._memory[key] = value
        disk = self._disk_path(key)
        if disk:
            try:
                disk.write_text(json.dumps(value, default=str))
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
