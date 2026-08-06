#!/usr/bin/env python3
"""
sync_setec.py — vendor a pinned copy of SETEC's CONTRACT into APODICTIC.

Python port of APODICTIC-Gemini's scripts/sync-plugin.mjs, adapted to the
APODICTIC→SETEC boundary. The key difference from the Gemini case:
APODICTIC does NOT serve SETEC's plugin — it invokes SETEC as a subprocess
discovered at runtime (setec_discovery / setec_runner). So this vendors only
the CONTRACT the consumer depends on, not the whole plugin:

  (a) SETEC's R1 capabilities manifest, projected to the surfaces APODICTIC
      consumes (`capabilities.py emit --json`, filtered to entries whose
      `consumers` include "apodictic") ->
      tests/setec-contract/setec-capabilities.json
  (b) the R5 contract fixtures (golden envelopes + the stdlib-only
      fake_setec.py) ->
      tests/setec-contract/fixtures/

plus a pin in setec-plugin.lock (mirrors apodictic-plugin.lock).

Why project the manifest instead of vendoring all 82 entries: the drift
gate (tools/check_setec_contract.py) compares vendored-vs-live. Vendoring
the full producer manifest would make drift fire on any change to any
surface APODICTIC doesn't consume, flooding the weekly bump PR with noise.
The projection is exactly the contract APODICTIC depends on, so drift means
"something APODICTIC consumes changed."

Usage:
  python3 scripts/sync_setec.py            # re-derive from the resolved SETEC, write vendored copy + lock
  python3 scripts/sync_setec.py --check    # re-derive and exit nonzero if the vendored copy is stale

SETEC resolution: set SETEC_VOICEPRINT_DIR to a SETEC plugin root. The weekly
sync-setec.yml `actions/checkout`s the pinned SETEC release tag and points
SETEC_VOICEPRINT_DIR at it; a local run points it at a SETEC checkout. Set
SETEC_RELEASE_TAG to emit a non-provisional release pin (build_lock then records
the tag + release URL); without it the pin falls back to the branch + local
worktree (the pre-release bootstrap posture, retired in normal operation).

Env:
  SETEC_VOICEPRINT_DIR — path to the SETEC plugin root (the dir with
    .claude-plugin/plugin.json and scripts/). Required. Falls back to the
    marketplace install if unset.
  SETEC_RELEASE_TAG — optional; when set, build_lock emits a non-provisional
    pin to that release tag (the weekly workflow passes the resolved release).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VENDOR_DIR = REPO_ROOT / "tests" / "setec-contract"
VENDORED_MANIFEST = VENDOR_DIR / "setec-capabilities.json"
VENDORED_FIXTURES = VENDOR_DIR / "fixtures"
LOCK_PATH = REPO_ROOT / "setec-plugin.lock"

# The shim dir also holds the C3 thin wrappers over the runtime vendored
# client (setec_discovery.py re-exports meets_floor/VersionParseError from
# _vendored_setec_client.py). Reused here (not re-implemented) so the
# contract-block gating below shares ONE SemVer parser with the runtime and
# the drift gate.
_SHIM_DIR = (
    REPO_ROOT / "plugins" / "apodictic" / "skills" / "specialized-audits" / "scripts"
)
if str(_SHIM_DIR) not in sys.path:
    sys.path.insert(0, str(_SHIM_DIR))

from setec_discovery import (  # noqa: E402
    SetecDiscoveryError,
    VersionParseError,
    discover_setec,
    meets_floor,
)

# The surface the consumer filter keys on: an entry is vendored iff this
# string appears in its `consumers` list.
CONSUMER = "apodictic"

# The SETEC scripts directory subpath under the plugin root.
SETEC_SCRIPTS_SUBDIR = "scripts"
CAPABILITIES_SCRIPT = "capabilities.py"
CONTRACT_FIXTURES_SUBDIR = Path("references") / "contract_fixtures"

# C2.1/F5/F10: the PRODUCER's `setec_version` (the plugin release, e.g.
# "1.129.0") at/above which the `emit` envelope's `contract` block is
# REQUIRED (fleet-coordination/specs/setec-consumer-client-contract.md
# C2.1). This is APODICTIC's OWN pin — mirrors voicewright's
# CONTRACT_BLOCK_MIN_SETEC_VERSION (same value, independently held, per the
# "consumer policy stays injected" design: each consumer, not the producer,
# decides when IT starts requiring the block).
#
# F5/F10 fix: this used to be gated on `manifest_schema_version >= 0.4.0`
# (CONTRACT_MANIFEST_SCHEMA_VERSION, now removed) — a review finding showed
# that rule is producer-bypassable, since a producer could hold
# manifest_schema_version below the floor while setec_version climbs
# arbitrarily high, and the REQUIRED gate would never fire. The producer's
# own EMISSION rule stays schema-based (a floor on manifest_schema_version,
# unrelated to this constant) — that is about what the producer PUBLISHES,
# not what this consumer REQUIRES. Requirement is keyed on setec_version via
# `meets_floor`, which understands SemVer prerelease tags (unlike the
# retired plain-integer manifest_schema_version comparison).
CONTRACT_BLOCK_MIN_SETEC_VERSION = (1, 129, 0)

# The runtime destination for the vendored, byte-identical shared client
# (C2.2's per-consumer table; this is APODICTIC's row).
CLIENT_SOURCE_RELATIVE = Path("scripts") / "setec" / "consumer_client.py"
CLIENT_RUNTIME_DESTINATION = (
    REPO_ROOT / "plugins" / "apodictic" / "skills" / "specialized-audits"
    / "scripts" / "_vendored_setec_client.py"
)

JUNK = {".DS_Store", "__pycache__"}


class SyncError(RuntimeError):
    """Raised when the SETEC source cannot be resolved or the derived
    contract is malformed."""


def _resolve_setec_root() -> Path:
    """Use the runtime resolver so live drift and execution trust one root."""
    try:
        return discover_setec().plugin_root
    except SetecDiscoveryError as exc:
        raise SyncError(str(exc)) from exc


def _read_plugin_version(root: Path) -> str:
    for rel in (".claude-plugin/plugin.json", "plugin.json"):
        p = root / rel
        if p.exists():
            return str(json.loads(p.read_text(encoding="utf-8")).get("version", ""))
    raise SyncError(f"No plugin.json under {root}.")


def _git_commit(root: Path) -> str | None:
    """Best-effort: the SETEC source commit, for the provisional pin."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _git_branch(root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def emit_manifest(setec_root: Path) -> dict:
    """Run SETEC's `capabilities.py emit --json` and return the parsed dict."""
    script = setec_root / SETEC_SCRIPTS_SUBDIR / CAPABILITIES_SCRIPT
    if not script.is_file():
        raise SyncError(
            f"SETEC has no {SETEC_SCRIPTS_SUBDIR}/{CAPABILITIES_SCRIPT} at "
            f"{setec_root} — this SETEC predates the R1 capabilities query."
        )
    completed = subprocess.run(
        [sys.executable, str(script), "emit", "--json"],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        raise SyncError(
            f"`capabilities.py emit --json` failed (rc={completed.returncode}). "
            f"Stderr: {completed.stderr[:500]!r}"
        )
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SyncError(f"emit output did not parse: {exc}") from exc


def project_consumer_manifest(full: dict) -> dict:
    """Project the full emit envelope to the APODICTIC-consumer slice:
    {setec_version, manifest_schema_version, [contract,] entries: [apodictic
    surfaces]}. Entries are sorted by `id` so the vendored copy is
    byte-stable across runs regardless of producer ordering.

    F5/F10: the contract block is REQUIRED when the PRODUCER's live
    `setec_version` (the plugin release, e.g. "1.129.0") is at/above
    CONTRACT_BLOCK_MIN_SETEC_VERSION — NOT when manifest_schema_version
    crosses a threshold. Gating on manifest_schema_version was
    producer-bypassable: a producer could hold manifest_schema_version below
    the floor while setec_version climbed arbitrarily high, and this
    consumer would never require the block. The producer's own EMISSION
    rule (when it PUBLISHES `contract` at all) remains schema-based — that
    is a separate, producer-owned decision about what it ships, not what
    this consumer demands.

    F7: a missing, non-string, empty, or unparseable `setec_version` FAILS
    CLOSED (raises SyncError) rather than silently skipping the floor check.
    The old `isinstance(x, str) and meets_floor(...)`-shaped condition
    short-circuited to False the moment `setec_version` was anything but a
    valid version string — silently treating a malformed envelope as
    legacy/no-contract-required, exactly the case this check exists to
    catch. A malformed `setec_version` is not proof the release is below
    the floor; we cannot parse it at all, so we never allow it to take the
    legacy no-contract path."""
    entries = full.get("entries")
    if not isinstance(entries, list):
        raise SyncError("emit envelope has no `entries` list.")
    setec_version = full.get("setec_version")
    contract = full.get("contract")
    if not isinstance(setec_version, str) or not setec_version:
        raise SyncError(
            f"emit envelope's `setec_version` is missing or not a non-empty "
            f"string ({setec_version!r}) — cannot determine whether this "
            f"release requires the C2.1 contract block, so refusing to "
            f"proceed rather than silently allowing a missing `contract` "
            f"through."
        )
    try:
        meets = meets_floor(setec_version, CONTRACT_BLOCK_MIN_SETEC_VERSION)
    except VersionParseError as exc:
        raise SyncError(
            f"emit envelope's `setec_version` {setec_version!r} does not "
            f"parse ({exc}) — cannot determine whether this release "
            f"requires the C2.1 contract block, so refusing to proceed."
        ) from exc
    if meets and contract is None:
        raise SyncError(
            f"SETEC {setec_version} is at/above "
            f"CONTRACT_BLOCK_MIN_SETEC_VERSION "
            f"({'.'.join(str(p) for p in CONTRACT_BLOCK_MIN_SETEC_VERSION)}) "
            f"but its emit envelope has no `contract` block."
        )

    consumer_entries = [
        e
        for e in entries
        if isinstance(e, dict) and CONSUMER in (e.get("consumers") or [])
    ]
    consumer_entries.sort(key=lambda e: e.get("id") or e.get("surface") or "")

    projected: dict = {
        "setec_version": setec_version,
        "manifest_schema_version": full.get("manifest_schema_version"),
    }
    if contract is not None:
        projected["contract"] = contract
    projected["entries"] = consumer_entries
    return projected


def _serialize(manifest: dict) -> str:
    """Canonical serialization for the vendored manifest: pretty, trailing
    newline. Deterministic so --check is a pure string compare."""
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def _is_junk(rel: str) -> bool:
    parts = Path(rel).parts
    return any(p in JUNK for p in parts) or rel.endswith(".pyc")


def _consumed_shim_surfaces() -> set[str]:
    """The SETEC surfaces APODICTIC actually dispatches — its ai_prose_*.py
    shims, the single source of truth for "what we consume". Reused from the
    drift gate (tools/check_setec_contract.discover_shim_surfaces) so the two
    never diverge. Deferred import avoids a module-load cycle."""
    tools_dir = REPO_ROOT / "tools"
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))
    from check_setec_contract import discover_shim_surfaces  # noqa: WPS433

    return set(discover_shim_surfaces())


def _copy_fixtures(
    setec_root: Path, dest: Path, expected_surfaces: set[str] | None = None
) -> list[str]:
    """Copy SETEC's references/contract_fixtures/ (goldens + fake_setec.py +
    README) into dest. Returns the sorted list of copied relative paths.

    Guard: every surface APODICTIC consumes (``expected_surfaces``; defaults to
    the ai_prose_*.py shim set) must have a ``<surface>.json`` golden in the
    copied set. This self-updating subset check replaces a hardcoded count — a
    newly-consumed surface (e.g. ``argument_decision_audit``) whose golden is
    missing fails the sync loudly instead of slipping under a fixed ``>=N``
    threshold."""
    src = setec_root / CONTRACT_FIXTURES_SUBDIR
    if not src.is_dir():
        raise SyncError(f"SETEC has no {CONTRACT_FIXTURES_SUBDIR} at {setec_root}.")
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    copied: list[str] = []
    for item in sorted(src.iterdir()):
        rel = item.name
        if _is_junk(rel):
            continue
        if item.is_file():
            shutil.copy2(item, dest / rel)
            copied.append(rel)
    # Self-updating guard: every consumed surface must have a golden.
    golden_stems = {c[: -len(".json")] for c in copied if c.endswith(".json")}
    expected = (
        expected_surfaces
        if expected_surfaces is not None
        else _consumed_shim_surfaces()
    )
    missing = sorted(expected - golden_stems)
    if missing:
        raise SyncError(
            f"contract_fixtures is missing a golden for consumed surface(s) "
            f"{missing!r} (goldens present: {sorted(golden_stems)!r})."
        )
    if not golden_stems:
        raise SyncError(
            f"no golden envelopes found in {CONTRACT_FIXTURES_SUBDIR} at {setec_root}."
        )
    if "fake_setec.py" not in copied:
        raise SyncError("contract_fixtures is missing fake_setec.py.")
    return copied


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _display_path(path: Path) -> str:
    """Render `path` relative to REPO_ROOT for messages when possible,
    falling back to the absolute path. The module-level VENDOR_DIR /
    LOCK_PATH / CLIENT_RUNTIME_DESTINATION constants are monkeypatchable (the
    hermetic drift-tri-state self-test in tools/check_setec_contract.py
    redirects them into a tempdir outside REPO_ROOT), so a bare
    `.relative_to(REPO_ROOT)` would raise ValueError there."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _read_client_source(setec_root: Path) -> bytes:
    """Read the PRODUCER's shared client source bytes (spec C2.2). Raises
    SyncError if this SETEC predates the shared client (no
    scripts/setec/consumer_client.py) — a clean failure rather than a
    confusing downstream hash mismatch."""
    path = setec_root / CLIENT_SOURCE_RELATIVE
    if not path.is_file():
        raise SyncError(
            f"SETEC has no {CLIENT_SOURCE_RELATIVE} at {setec_root} — this "
            f"SETEC predates the C2 shared consumer client."
        )
    return path.read_bytes()


def _copy_client(source_bytes: bytes, runtime_destination: Path) -> None:
    """Write `source_bytes` VERBATIM to `runtime_destination` — byte-identical
    vendoring, not a re-export shim (spec C2.2)."""
    runtime_destination.parent.mkdir(parents=True, exist_ok=True)
    runtime_destination.write_bytes(source_bytes)


def build_lock(setec_root: Path, manifest: dict, client_source_bytes: bytes) -> dict:
    """Construct the pin record (mirrors apodictic-plugin.lock).

    FINALIZED path: when ``SETEC_RELEASE_TAG`` is set to a real release tag
    (e.g. ``v1.113.0``), emit a non-provisional pin to that release — ``tag``
    is the release tag and ``source`` the release URL. The weekly
    ``sync-setec.yml`` resolves the release ref and passes it through this env
    var; a local finalization run sets it explicitly.

    Provisional fallback (no release tag): pin to the branch + a code-safe
    local-worktree label; machine-local checkout paths are operational context,
    not contract identity, and must not enter the committed lock.
    ``provisional: true`` — the pre-release bootstrap posture.

    ``client_sha256`` (spec C2.2) is hashed from the PRODUCER SOURCE bytes —
    NEVER from the just-written runtime vendored copy. This is a deliberate
    anti-drift design point: the lock's pin must reflect what the producer
    actually shipped, so a byte-mutated runtime copy is caught by comparing
    against this SOURCE-derived hash (`cmd_check`'s runtime-destination
    re-hash), not by re-deriving from the (possibly mutated) copy itself,
    which would make the check self-referential and unable to detect
    corruption of the vendored file."""
    client_sha256 = _sha256_bytes(client_source_bytes)
    commit = _git_commit(setec_root)
    release_tag = os.environ.get("SETEC_RELEASE_TAG")
    if release_tag:
        return {
            "repo": "anotherpanacea-eng/setec-voiceprint",
            "subdir": "plugins/setec-voiceprint",
            "tag": release_tag,
            "commit": commit or "(uncommitted)",
            "plugin_version": _read_plugin_version(setec_root),
            "setec_version": manifest.get("setec_version"),
            "manifest_schema_version": manifest.get("manifest_schema_version"),
            "client_sha256": client_sha256,
            "source": (
                "https://github.com/anotherpanacea-eng/setec-voiceprint/"
                f"releases/tag/{release_tag}"
            ),
            "provisional": False,
        }
    branch = _git_branch(setec_root)
    return {
        "repo": "anotherpanacea-eng/setec-voiceprint",
        "subdir": "plugins/setec-voiceprint",
        # Provisional: no SETEC_RELEASE_TAG given. The R1+R5 work also lives on
        # the branch named below; set SETEC_RELEASE_TAG on the real release.
        "tag": branch or "feat/normalized-entrypoint-r1-r5",
        "commit": commit or "(uncommitted)",
        "plugin_version": _read_plugin_version(setec_root),
        "setec_version": manifest.get("setec_version"),
        "manifest_schema_version": manifest.get("manifest_schema_version"),
        "client_sha256": client_sha256,
        "source": "local worktree (provisional)",
        "provisional": True,
    }


def _serialize_lock(lock: dict) -> str:
    return json.dumps(lock, indent=2, ensure_ascii=False) + "\n"


def derive(setec_root: Path) -> tuple[str, dict, bytes]:
    """Re-derive the vendored manifest string + the lock dict + the producer
    client SOURCE bytes from SETEC. Pure (no writes); used by both --write
    and --check."""
    full = emit_manifest(setec_root)
    projected = project_consumer_manifest(full)
    client_source_bytes = _read_client_source(setec_root)
    return (
        _serialize(projected),
        build_lock(setec_root, projected, client_source_bytes),
        client_source_bytes,
    )


def cmd_write() -> int:
    setec_root = _resolve_setec_root()
    manifest_str, lock, client_source_bytes = derive(setec_root)
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    VENDORED_MANIFEST.write_text(manifest_str, encoding="utf-8")
    copied = _copy_fixtures(setec_root, VENDORED_FIXTURES)
    _copy_client(client_source_bytes, CLIENT_RUNTIME_DESTINATION)
    LOCK_PATH.write_text(_serialize_lock(lock), encoding="utf-8")
    print(
        f"synced SETEC contract from {setec_root}\n"
        f"  setec_version={lock['setec_version']} "
        f"(plugin {lock['plugin_version']}, schema {lock['manifest_schema_version']})\n"
        f"  manifest -> {_display_path(VENDORED_MANIFEST)} "
        f"({len(json.loads(manifest_str)['entries'])} consumer surfaces)\n"
        f"  fixtures -> {_display_path(VENDORED_FIXTURES)} "
        f"({len(copied)} files)\n"
        f"  client   -> {_display_path(CLIENT_RUNTIME_DESTINATION)} "
        f"(sha256 {lock['client_sha256'][:12]}...)\n"
        f"  lock     -> {_display_path(LOCK_PATH)} "
        f"({'provisional' if lock['provisional'] else 'release'} pin: "
        f"{lock['tag']})"
    )
    return 0


def cmd_check() -> int:
    """Re-derive and compare against the vendored copy. Exit 1 on staleness."""
    setec_root = _resolve_setec_root()
    manifest_str, lock, client_source_bytes = derive(setec_root)
    stale: list[str] = []

    if not VENDORED_MANIFEST.exists():
        stale.append(f"missing {_display_path(VENDORED_MANIFEST)}")
    elif VENDORED_MANIFEST.read_text(encoding="utf-8") != manifest_str:
        stale.append(
            f"{_display_path(VENDORED_MANIFEST)} diverges from live "
            f"`capabilities emit` (consumer projection)"
        )

    # Fixtures: compare file-for-file against SETEC's contract_fixtures.
    src_fix = setec_root / CONTRACT_FIXTURES_SUBDIR
    if not VENDORED_FIXTURES.is_dir():
        stale.append(f"missing {_display_path(VENDORED_FIXTURES)}")
    else:
        src_files = {
            p.name: p
            for p in src_fix.iterdir()
            if p.is_file() and not _is_junk(p.name)
        }
        dst_files = {
            p.name: p
            for p in VENDORED_FIXTURES.iterdir()
            if p.is_file() and not _is_junk(p.name)
        }
        for name in sorted(set(src_files) | set(dst_files)):
            if name not in dst_files:
                stale.append(f"fixtures: missing vendored {name}")
            elif name not in src_files:
                stale.append(f"fixtures: vendored {name} no longer in SETEC source")
            elif src_files[name].read_bytes() != dst_files[name].read_bytes():
                stale.append(f"fixtures: {name} diverges from SETEC source")

    # Lock: setec_version / plugin_version / commit / client_sha256 are the
    # load-bearing pin. client_sha256 (spec C2.2) is hashed from the
    # PRODUCER SOURCE bytes (never the runtime copy) — see build_lock.
    if LOCK_PATH.exists():
        cur = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        for key in (
            "setec_version", "plugin_version", "commit",
            "manifest_schema_version", "client_sha256",
        ):
            if cur.get(key) != lock.get(key):
                stale.append(
                    f"lock: {key}={cur.get(key)!r} but source is {lock.get(key)!r}"
                )
    else:
        stale.append(f"missing {_display_path(LOCK_PATH)}")

    # Runtime vendored client: re-hash the ACTUAL runtime destination file and
    # compare against the producer-source hash. This is the check that fires
    # on a byte-mutated (or deleted) vendored client even if the lock itself
    # was left untouched — the lock-key compare above alone cannot catch a
    # divergence confined to the runtime copy.
    expected_client_sha256 = lock.get("client_sha256")
    if not CLIENT_RUNTIME_DESTINATION.is_file():
        stale.append(
            f"missing runtime vendored client "
            f"{_display_path(CLIENT_RUNTIME_DESTINATION)}"
        )
    else:
        runtime_sha256 = _sha256_bytes(CLIENT_RUNTIME_DESTINATION.read_bytes())
        if runtime_sha256 != expected_client_sha256:
            stale.append(
                f"runtime vendored client "
                f"{_display_path(CLIENT_RUNTIME_DESTINATION)} diverges "
                f"from the producer source (sha256 {runtime_sha256} != "
                f"{expected_client_sha256})"
            )

    if stale:
        print("sync_setec --check FAILED — vendored SETEC contract is stale:", file=sys.stderr)
        for s in stale:
            print(f"  - {s}", file=sys.stderr)
        print("\nRun: python3 scripts/sync_setec.py", file=sys.stderr)
        return 1
    print(
        f"sync_setec --check OK: vendored contract current with SETEC "
        f"{lock['setec_version']} (plugin {lock['plugin_version']})."
    )
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="re-derive and exit nonzero if the vendored copy is stale",
    )
    args = parser.parse_args(argv)
    try:
        return cmd_check() if args.check else cmd_write()
    except SyncError as exc:
        print(f"sync_setec failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
