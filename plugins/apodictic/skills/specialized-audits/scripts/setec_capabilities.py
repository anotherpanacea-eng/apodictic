#!/usr/bin/env python3
"""
setec_capabilities.py — query SETEC's R1 capabilities manifest.

Implements the consumer half of R1 (the machine-readable capabilities
query) from docs/setec-normalized-entrypoint-requirements.md. APODICTIC
data-drives each surface's version floor from this manifest instead of
hardcoding per-shim constants (docs/setec-dependency-posture.md Decision 2:
"version floors are a property of the surface, discovered, not hardcoded").

Flow (per the requirements doc's acceptance criterion):
  1. Discover SETEC at a MINIMAL bootstrap floor that guarantees the
     `capabilities.py emit --json` command + the R1 field bundle
     (`min_setec_version`/`json_delivery`/`inputs`) exist.
  2. Run `capabilities.py emit --json` via the existing run_setec_script
     plumbing and parse {setec_version, manifest_schema_version, entries[]}.
  3. Resolve a surface's floor from the entry's `min_setec_version`, and
     assert the discovered `setec_version` >= that floor.

No per-surface floor is hardcoded anywhere in APODICTIC after this module
lands — the manifest is the single authority. The only constant kept is
the bootstrap floor (setec_discovery.BOOTSTRAP_SETEC_VERSION, re-exported
here): the version at which `capabilities emit` plus the R1 field bundle
exist. # FINALIZATION on that constant lives in setec_discovery.py.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setec_discovery import (  # noqa: E402
    BOOTSTRAP_SETEC_VERSION,
    SetecDiscoveryError,
    SetecLocation,
    _parse_version,
    discover_setec,
    run_setec_script,
)

# Re-exported from setec_discovery (single source of truth for the
# provisional bootstrap floor; # FINALIZATION marker lives there). Kept as a
# module attribute here so callers that `from setec_capabilities import
# BOOTSTRAP_SETEC_VERSION` continue to work.
__all__ = ["BOOTSTRAP_SETEC_VERSION"]

# The R1 query command. SETEC exposes the manifest as
# `capabilities.py emit --json` (see the SETEC-side spec, OQ1).
_CAPABILITIES_SCRIPT = "capabilities.py"
_EMIT_ARGS = ["emit", "--json"]


class SetecCapabilitiesError(RuntimeError):
    """Raised when the capabilities query cannot be run or parsed, or when
    a requested surface is missing / lacks a floor in the manifest.

    Distinct from SetecDiscoveryError (SETEC absent / version-floor) so
    callers can tell "SETEC too old to even emit a manifest" from
    "manifest emitted but this surface isn't in it / has no floor".
    """


@dataclass(frozen=True)
class SurfaceCapability:
    """The consumer-relevant facts for one SETEC surface, read from the
    R1 manifest. The floor is `min_setec_version` — asserted against the
    discovered setec_version, never hardcoded."""

    surface: str
    min_setec_version: tuple[int, ...]
    min_setec_version_str: str
    json_delivery: str | None
    handoff: str | None
    inputs: list[dict[str, Any]]
    required_groups: list[str]
    raw: dict[str, Any]

    def missing_required_groups(self, argv: list[str]) -> list[str]:
        """Required input groups (R1 ``required_groups``) for which NONE of the
        group's member flags appear in ``argv``. Each named group requires
        exactly one of its members (e.g. ``idiolect_detector`` needs one
        ``target`` source and one ``reference`` source). Fully manifest-driven:
        the flag->group map comes from this surface's structured ``inputs[]``,
        so the consumer hardcodes no surface's flags. Returns [] when every
        required group is satisfied (also [] when the surface declares none)."""
        if not self.required_groups:
            return []
        flag_to_group: dict[str, str] = {
            item["flag"]: item["group"]
            for item in self.inputs
            if isinstance(item, dict) and item.get("flag") and item.get("group")
        }
        present: set[str] = set()
        for tok in argv:
            group = flag_to_group.get(tok.split("=", 1)[0])
            if group:
                present.add(group)
        return [g for g in self.required_groups if g not in present]


@dataclass(frozen=True)
class SetecManifest:
    """Parsed R1 capabilities query: the producer's version + the per-surface
    table. Cached per-process by `query_capabilities`."""

    setec_version: tuple[int, ...]
    setec_version_str: str
    manifest_schema_version: str | None
    surfaces: dict[str, SurfaceCapability]
    location: SetecLocation

    def require(self, surface: str) -> SurfaceCapability:
        """Return the SurfaceCapability for `surface`, or raise
        SetecCapabilitiesError naming the available surfaces."""
        cap = self.surfaces.get(surface)
        if cap is None:
            available = ", ".join(sorted(self.surfaces)) or "(none)"
            raise SetecCapabilitiesError(
                f"SETEC capabilities manifest has no entry for surface "
                f"{surface!r}. Surfaces present: {available}. The producer "
                f"may have renamed or dropped this surface; check the "
                f"vendored manifest and the SETEC version."
            )
        return cap


# Per-process cache keyed by the resolved plugin_root, so a test or a
# single pass that queries twice does not shell out twice.
_MANIFEST_CACHE: dict[str, SetecManifest] = {}


def _entry_surface_id(entry: dict[str, Any]) -> str | None:
    """Return the surface id for a manifest entry. The R1 emit envelope
    keys each entry by `id` (and duplicates it as `surface`)."""
    for key in ("id", "surface"):
        value = entry.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def parse_manifest_payload(
    payload: dict[str, Any], *, location: SetecLocation
) -> SetecManifest:
    """Parse a {setec_version, manifest_schema_version, entries[]} dict into
    a SetecManifest. Shared by the live query and the vendored-manifest path
    (the drift gate / offline tests parse the vendored JSON through here).

    Surfaces without a `min_setec_version` are kept out of the floor table
    (their floor is undiscoverable) but do not abort the parse — only a
    surface APODICTIC actually asks for must carry a floor, enforced at
    `require()` / `resolve_floor` time."""
    version_str = str(payload.get("setec_version", "")).strip()
    version = _parse_version(version_str)
    if not version:
        raise SetecCapabilitiesError(
            f"SETEC capabilities manifest has missing or unparseable "
            f"setec_version: {version_str!r}."
        )
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise SetecCapabilitiesError(
            "SETEC capabilities manifest has no `entries` list "
            f"(top-level keys: {sorted(payload.keys())!r})."
        )
    surfaces: dict[str, SurfaceCapability] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        surface = _entry_surface_id(entry)
        if surface is None:
            continue
        floor_str = entry.get("min_setec_version")
        if not isinstance(floor_str, str) or not floor_str.strip():
            # Surface carries no floor (e.g. a discoverability-only entry).
            # Skip it from the floor table; require() raises if a consumer
            # asks for it.
            continue
        floor = _parse_version(floor_str)
        if not floor:
            continue
        inputs = entry.get("inputs")
        required_groups = entry.get("required_groups")
        surfaces[surface] = SurfaceCapability(
            surface=surface,
            min_setec_version=floor,
            min_setec_version_str=floor_str,
            json_delivery=entry.get("json_delivery"),
            handoff=entry.get("handoff"),
            inputs=list(inputs) if isinstance(inputs, list) else [],
            required_groups=(
                list(required_groups)
                if isinstance(required_groups, list)
                else []
            ),
            raw=entry,
        )
    return SetecManifest(
        setec_version=version,
        setec_version_str=version_str,
        manifest_schema_version=(
            str(payload["manifest_schema_version"])
            if payload.get("manifest_schema_version") is not None
            else None
        ),
        surfaces=surfaces,
        location=location,
    )


def query_capabilities(
    *,
    location: SetecLocation | None = None,
    force: bool = False,
) -> SetecManifest:
    """Run SETEC's `capabilities.py emit --json` and return a parsed,
    per-process-cached SetecManifest.

    Discovers SETEC at the BOOTSTRAP floor (the version where `emit` + the
    R1 field bundle exist) when `location` is not supplied. If the
    discovered SETEC predates `emit` (no R1), discovery fails with the
    standard upgrade message (computational surfaces hard-require SETEC per
    docs/setec-dependency-posture.md — never a silent fallback).

    Raises:
      SetecDiscoveryError — SETEC absent or below the bootstrap floor.
      SetecCapabilitiesError — SETEC found but `emit` failed / produced
        unparseable output (e.g. an even-older SETEC without the subcommand).
    """
    if location is None:
        location = discover_setec(min_version=BOOTSTRAP_SETEC_VERSION)
    cache_key = str(location.plugin_root)
    if not force and cache_key in _MANIFEST_CACHE:
        return _MANIFEST_CACHE[cache_key]

    completed = run_setec_script(
        _CAPABILITIES_SCRIPT,
        _EMIT_ARGS,
        location=location,
        capture_output=True,
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        raise SetecCapabilitiesError(
            f"SETEC `capabilities.py emit --json` failed "
            f"(returncode={completed.returncode}) at {location.plugin_root}. "
            f"This SETEC may predate the R1 capabilities query. "
            f"Stderr (truncated): {completed.stderr[:500]!r}"
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SetecCapabilitiesError(
            f"SETEC `capabilities.py emit --json` output did not parse: "
            f"{exc}. First 500 chars: {completed.stdout[:500]!r}"
        ) from exc
    manifest = parse_manifest_payload(payload, location=location)
    _MANIFEST_CACHE[cache_key] = manifest
    return manifest


def resolve_floor(
    surface: str,
    *,
    location: SetecLocation | None = None,
) -> tuple[SurfaceCapability, SetecManifest]:
    """Resolve `surface`'s floor from the live manifest and assert the
    discovered setec_version satisfies it.

    Returns (capability, manifest). Raises:
      SetecDiscoveryError — SETEC absent / below the bootstrap floor, OR
        the discovered setec_version is below the surface's manifest floor
        (raised with the floor-aware install/upgrade message so the user
        sees the *surface's* required minimum, not the bootstrap floor).
      SetecCapabilitiesError — the surface is absent from the manifest or
        carries no floor.
    """
    manifest = query_capabilities(location=location)
    cap = manifest.require(surface)
    if manifest.setec_version < cap.min_setec_version:
        # Reuse setec_discovery's floor-aware upgrade message so the user
        # sees the surface's required minimum.
        from setec_discovery import _install_instructions  # local import

        raise SetecDiscoveryError(
            f"SETEC version {manifest.setec_version_str} at "
            f"{manifest.location.plugin_root} satisfies the bootstrap floor "
            f"but is below surface {surface!r}'s manifest floor "
            f"{cap.min_setec_version_str}.\n\n"
            f"{_install_instructions(cap.min_setec_version)}"
        )
    return cap, manifest


def clear_cache() -> None:
    """Drop the per-process manifest cache. Tests that point
    SETEC_VOICEPRINT_DIR at different roots call this between cases."""
    _MANIFEST_CACHE.clear()


def _cli_main(argv: list[str]) -> int:
    """`python setec_capabilities.py [surface]` — debug the R1 query.

    With no arg: print {setec_version, manifest_schema_version, surfaces}.
    With a surface: print that surface's resolved floor + posture, and the
    floor-satisfaction check result.
    """
    try:
        if argv:
            cap, manifest = resolve_floor(argv[0])
            payload = {
                "setec_version": manifest.setec_version_str,
                "surface": cap.surface,
                "min_setec_version": cap.min_setec_version_str,
                "json_delivery": cap.json_delivery,
                "handoff": cap.handoff,
                "required_groups": cap.required_groups,
                "floor_satisfied": True,
            }
        else:
            manifest = query_capabilities()
            payload = {
                "setec_version": manifest.setec_version_str,
                "manifest_schema_version": manifest.manifest_schema_version,
                "surfaces": {
                    name: cap.min_setec_version_str
                    for name, cap in sorted(manifest.surfaces.items())
                },
            }
    except (SetecDiscoveryError, SetecCapabilitiesError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli_main(sys.argv[1:]))
