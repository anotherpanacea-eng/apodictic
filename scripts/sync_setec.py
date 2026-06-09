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

SETEC resolution (provisional): set SETEC_VOICEPRINT_DIR to a SETEC plugin
root. # FINALIZATION: when SETEC cuts the real R1 release, this script's
resolution should pin to that release tag (download the tagged tarball,
like sync-plugin.mjs does for apodictic) instead of reading a local worktree
via SETEC_VOICEPRINT_DIR. The lock's `tag`/`commit`/`source` fields are
provisional until then (see setec-plugin.lock).

Env:
  SETEC_VOICEPRINT_DIR — path to the SETEC plugin root (the dir with
    .claude-plugin/plugin.json and scripts/). Required (provisional pin
    source). Falls back to the marketplace install if unset.
"""

from __future__ import annotations

import argparse
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

# The surface the consumer filter keys on: an entry is vendored iff this
# string appears in its `consumers` list.
CONSUMER = "apodictic"

# The SETEC scripts directory subpath under the plugin root.
SETEC_SCRIPTS_SUBDIR = "scripts"
CAPABILITIES_SCRIPT = "capabilities.py"
CONTRACT_FIXTURES_SUBDIR = Path("references") / "contract_fixtures"

JUNK = {".DS_Store", "__pycache__"}


class SyncError(RuntimeError):
    """Raised when the SETEC source cannot be resolved or the derived
    contract is malformed."""


def _resolve_setec_root() -> Path:
    """Resolve the SETEC plugin root. Provisional: SETEC_VOICEPRINT_DIR, then
    the marketplace install. # FINALIZATION: replace with release-tag pinning."""
    env = os.environ.get("SETEC_VOICEPRINT_DIR")
    if env:
        root = Path(env).expanduser().resolve()
        if not (root / ".claude-plugin" / "plugin.json").exists() and not (
            root / "plugin.json"
        ).exists():
            raise SyncError(
                f"SETEC_VOICEPRINT_DIR={root} is not a SETEC plugin root "
                f"(no .claude-plugin/plugin.json)."
            )
        return root
    base = Path.home() / ".claude" / "plugins" / "marketplaces"
    candidates = sorted(base.glob("*/plugins/setec-voiceprint")) if base.is_dir() else []
    for c in candidates:
        if (c / ".claude-plugin" / "plugin.json").exists():
            return c.resolve()
    raise SyncError(
        "Could not resolve a SETEC plugin root. Set SETEC_VOICEPRINT_DIR to a "
        "local SETEC checkout (provisional pin source until the R1 release)."
    )


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
    {setec_version, manifest_schema_version, entries: [apodictic surfaces]}.

    Entries are sorted by `id` so the vendored copy is byte-stable across
    runs regardless of producer ordering."""
    entries = full.get("entries")
    if not isinstance(entries, list):
        raise SyncError("emit envelope has no `entries` list.")
    consumer_entries = [
        e
        for e in entries
        if isinstance(e, dict) and CONSUMER in (e.get("consumers") or [])
    ]
    consumer_entries.sort(key=lambda e: e.get("id") or e.get("surface") or "")
    return {
        "setec_version": full.get("setec_version"),
        "manifest_schema_version": full.get("manifest_schema_version"),
        "entries": consumer_entries,
    }


def _serialize(manifest: dict) -> str:
    """Canonical serialization for the vendored manifest: pretty, trailing
    newline. Deterministic so --check is a pure string compare."""
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def _is_junk(rel: str) -> bool:
    parts = Path(rel).parts
    return any(p in JUNK for p in parts) or rel.endswith(".pyc")


def _copy_fixtures(setec_root: Path, dest: Path) -> list[str]:
    """Copy SETEC's references/contract_fixtures/ (goldens + fake_setec.py +
    README) into dest. Returns the sorted list of copied relative paths."""
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
    # The contract requires at least the 9 goldens + fake_setec.py.
    goldens = [c for c in copied if c.endswith(".json")]
    if len(goldens) < 9:
        raise SyncError(
            f"expected >=9 golden envelopes in contract_fixtures, found "
            f"{len(goldens)}: {goldens!r}"
        )
    if "fake_setec.py" not in copied:
        raise SyncError("contract_fixtures is missing fake_setec.py.")
    return copied


def build_lock(setec_root: Path, manifest: dict) -> dict:
    """Construct the provisional pin record (mirrors apodictic-plugin.lock)."""
    commit = _git_commit(setec_root)
    branch = _git_branch(setec_root)
    return {
        "repo": "anotherpanacea-eng/setec-voiceprint",
        "subdir": "plugins/setec-voiceprint",
        # FINALIZATION: `tag` is provisional — there is no R1 release tag yet.
        # The R1+R5 work lives on the branch named below. On the real release,
        # set tag to the release tag (e.g. v1.113.0) and source to the release
        # URL, and switch sync_setec.py's resolution to tarball download.
        "tag": branch or "feat/normalized-entrypoint-r1-r5",
        "commit": commit or "(uncommitted)",
        "plugin_version": _read_plugin_version(setec_root),
        "setec_version": manifest.get("setec_version"),
        "manifest_schema_version": manifest.get("manifest_schema_version"),
        "source": f"local worktree: {setec_root}",
        "provisional": True,
    }


def _serialize_lock(lock: dict) -> str:
    return json.dumps(lock, indent=2, ensure_ascii=False) + "\n"


def derive(setec_root: Path) -> tuple[str, dict]:
    """Re-derive the vendored manifest string + the lock dict from SETEC.
    Pure (no writes); used by both --write and --check."""
    full = emit_manifest(setec_root)
    projected = project_consumer_manifest(full)
    return _serialize(projected), build_lock(setec_root, projected)


def cmd_write() -> int:
    setec_root = _resolve_setec_root()
    manifest_str, lock = derive(setec_root)
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    VENDORED_MANIFEST.write_text(manifest_str, encoding="utf-8")
    copied = _copy_fixtures(setec_root, VENDORED_FIXTURES)
    LOCK_PATH.write_text(_serialize_lock(lock), encoding="utf-8")
    print(
        f"synced SETEC contract from {setec_root}\n"
        f"  setec_version={lock['setec_version']} "
        f"(plugin {lock['plugin_version']}, schema {lock['manifest_schema_version']})\n"
        f"  manifest -> {VENDORED_MANIFEST.relative_to(REPO_ROOT)} "
        f"({len(json.loads(manifest_str)['entries'])} consumer surfaces)\n"
        f"  fixtures -> {VENDORED_FIXTURES.relative_to(REPO_ROOT)} "
        f"({len(copied)} files)\n"
        f"  lock     -> {LOCK_PATH.relative_to(REPO_ROOT)} (provisional pin)"
    )
    return 0


def cmd_check() -> int:
    """Re-derive and compare against the vendored copy. Exit 1 on staleness."""
    setec_root = _resolve_setec_root()
    manifest_str, lock = derive(setec_root)
    stale: list[str] = []

    if not VENDORED_MANIFEST.exists():
        stale.append(f"missing {VENDORED_MANIFEST.relative_to(REPO_ROOT)}")
    elif VENDORED_MANIFEST.read_text(encoding="utf-8") != manifest_str:
        stale.append(
            f"{VENDORED_MANIFEST.relative_to(REPO_ROOT)} diverges from live "
            f"`capabilities emit` (consumer projection)"
        )

    # Fixtures: compare file-for-file against SETEC's contract_fixtures.
    src_fix = setec_root / CONTRACT_FIXTURES_SUBDIR
    if not VENDORED_FIXTURES.is_dir():
        stale.append(f"missing {VENDORED_FIXTURES.relative_to(REPO_ROOT)}")
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

    # Lock: setec_version / plugin_version / commit are the load-bearing pin.
    if LOCK_PATH.exists():
        cur = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        for key in ("setec_version", "plugin_version", "commit", "manifest_schema_version"):
            if cur.get(key) != lock.get(key):
                stale.append(
                    f"lock: {key}={cur.get(key)!r} but source is {lock.get(key)!r}"
                )
    else:
        stale.append(f"missing {LOCK_PATH.relative_to(REPO_ROOT)}")

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
