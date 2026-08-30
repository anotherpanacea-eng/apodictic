#!/usr/bin/env python3
"""
check_setec_contract.py — APODICTIC↔SETEC contract drift gate.

Python port of the Gemini drift gate (`generate:ui:check` +
`validateRegistry` in scripts/generate-ui.mjs), adapted to the
APODICTIC→SETEC contract boundary. Two independent checks:

  CHECK 1 — self-consistency guard (offline; mirrors validateRegistry).
    Every surface APODICTIC has a SHIM for MUST appear in the VENDORED
    capabilities manifest with a non-null `min_setec_version`. This catches
    the producer dropping/renaming a consumer surface, or shipping a surface
    without a floor — the analog of Gemini's "registry count disagrees with
    the array that drives the UI" freeze. It needs no live SETEC: it reads
    the committed vendored manifest only, so it runs in every CI job.
    ALSO offline (F1): the RUNTIME vendored client
    (plugins/apodictic/skills/specialized-audits/scripts/_vendored_setec_client.py)
    must hash to setec-plugin.lock's `client_sha256` — this is the check that
    makes a mutated vendored client or a corrupted lock entry fail WITHOUT a
    live SETEC checkout. Before this fix, only CHECK 2 (which needs
    SETEC_VOICEPRINT_DIR) compared client bytes, so a PR mutating the
    vendored client — the normal CI case, no sibling checkout — sailed
    through CI green.

  CHECK 2 — live drift (needs SETEC; mirrors `sync-plugin.mjs --check`).
    The vendored manifest + fixtures must match what live SETEC's
    `capabilities emit` / contract_fixtures produce right now. Delegates to
    sync_setec.cmd_check(). When SETEC cannot be resolved (no
    SETEC_VOICEPRINT_DIR, no marketplace install — the normal CI case until
    the R1 release), this check is SKIPPED with a notice, not failed: the
    self-consistency guard is the always-on gate, and the weekly sync
    workflow (which sets SETEC up) is where live drift is enforced.

Usage:
  python3 tools/check_setec_contract.py            # run both checks
  python3 tools/check_setec_contract.py --self-test # run built-in cases (hostile fixtures)

Exit codes: 0 OK / 1 drift or self-consistency failure / 2 usage.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VENDORED_MANIFEST = REPO_ROOT / "tests" / "setec-contract" / "setec-capabilities.json"
SHIM_DIR = (
    REPO_ROOT
    / "plugins"
    / "apodictic"
    / "skills"
    / "specialized-audits"
    / "scripts"
)
VENDORED_CLIENT = SHIM_DIR / "_vendored_setec_client.py"
LOCK_PATH = REPO_ROOT / "setec-plugin.lock"

# Make the consumer parser importable so the gate validates the vendored
# manifest through the SAME parse path the runtime uses.
sys.path.insert(0, str(SHIM_DIR))
from setec_discovery import VersionParseError, meets_floor  # noqa: E402

EXPECTED_OUTPUT_POLICY = {
    "common_required": ["ai_status", "available", "baseline", "claim_license",
        "claim_license_rendered", "results", "schema_version", "target",
        "task_surface", "tool", "version", "warnings"],
    "success_extensions": "surface_specific_allowed",
    "error_required": ["reason", "reason_category"],
    "error_extensions": "surface_specific_allowed",
    "reserved_collision_refused": True,
}
EXPECTED_REASONS = ["bad_input", "internal_error", "missing_dependency",
    "policy_refused", "text_too_short", "version_floor"]
EXPECTED_S5 = {
    "method": "unweighted mean of six family Burrows-Delta values",
    "family_order": ["char_ngrams_3", "char_ngrams_4", "char_ngrams_5",
        "pos_trigrams", "dependency_ngrams", "punctuation"],
    "family_limits": {"char_ngrams_3": 200, "char_ngrams_4": 200,
        "char_ngrams_5": 200, "pos_trigrams": 300,
        "dependency_ngrams": 300, "punctuation": None},
}
CONTRACT_KEYS = {"output_schema_version", "output_key_policy",
    "reason_categories", "contract_block_min_setec_version", "s5_identity",
    "client", "fixtures"}
FIXTURE_FILES = {
    "semver_parser_sha256": "semver_parser_cases.json",
    "warning_classifier_coverage_sha256": "warning_classifier_coverage.json",
    "warning_producer_emissions_sha256": "warning_producer_emissions.json",
}
MANIFEST_SCHEMA_VERSION = "0.4.0"
MANIFEST_KEYS = {"setec_version", "manifest_schema_version", "contract", "entries"}


def check_contract_policy(payload: dict, client_path: Path, lock_path: Path) -> list[str]:
    """Independent consumer pins for the producer-authored contract block."""
    problems: list[str] = []
    raw_version = payload.get("setec_version")
    if not isinstance(raw_version, str):
        contract_required = True
        problems.append("vendored manifest has an invalid setec_version")
    else:
        try:
            contract_required = meets_floor(raw_version, (1, 129, 0))
        except VersionParseError:
            contract_required = True
            problems.append("vendored manifest has an invalid setec_version")
    contract = payload.get("contract")
    if contract_required or isinstance(contract, dict):
        if set(payload) != MANIFEST_KEYS:
            problems.append("manifest root differs from the closed 0.4 consumer pin")
        if payload.get("manifest_schema_version") != MANIFEST_SCHEMA_VERSION:
            problems.append("manifest_schema_version differs from the independent 0.4.0 pin")
    if not isinstance(contract, dict):
        if contract_required:
            problems.append("vendored manifest has no contract mapping")
        return problems
    if set(contract) != CONTRACT_KEYS:
        problems.append("contract top-level keys differ from the closed consumer pin")
    expected = {"output_schema_version": "1.0",
        "output_key_policy": EXPECTED_OUTPUT_POLICY,
        "reason_categories": EXPECTED_REASONS,
        "contract_block_min_setec_version": "1.129.0",
        "s5_identity": EXPECTED_S5}
    for key, value in expected.items():
        if contract.get(key) != value:
            problems.append(f"contract.{key} differs from the independent consumer pin")
    client = contract.get("client")
    actual_client = hashlib.sha256(client_path.read_bytes()).hexdigest()
    if not isinstance(client, dict) or set(client) != {"relative_path", "sha256"}:
        problems.append("contract.client has the wrong closed shape")
    elif client.get("relative_path") != "scripts/setec/consumer_client.py" or client.get("sha256") != actual_client:
        problems.append("contract.client path/hash does not match the vendored runtime client")
    fixtures = contract.get("fixtures")
    fixture_dir = VENDORED_MANIFEST.parent / "fixtures"
    if not isinstance(fixtures, dict) or set(fixtures) != set(FIXTURE_FILES):
        problems.append("contract.fixtures has the wrong closed shape")
    else:
        for key, name in FIXTURE_FILES.items():
            actual = hashlib.sha256((fixture_dir / name).read_bytes()).hexdigest()
            if fixtures.get(key) != actual:
                problems.append(f"contract.fixtures.{key} does not match {name}")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    for key in ("setec_version", "manifest_schema_version"):
        if lock.get(key) != payload.get(key):
            problems.append(f"lock {key} differs from vendored manifest")
    if lock.get("client_sha256") != actual_client:
        problems.append("lock client_sha256 differs from vendored runtime client")
    return problems


def discover_shim_surfaces(shim_dir: Path = SHIM_DIR) -> dict[str, str]:
    """Return {surface_id: shim_filename} for every ai_prose_*.py shim by
    reading each shim's `SURFACE = "..."` constant. The shims are the
    consumer's source of truth for "which SETEC surfaces APODICTIC consumes",
    so the guard re-derives the set from them rather than hardcoding nine
    names (a hardcoded list would itself drift)."""
    import ast

    surfaces: dict[str, str] = {}
    for shim in sorted(shim_dir.glob("ai_prose_*.py")):
        tree = ast.parse(shim.read_text(encoding="utf-8"), filename=str(shim))
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and target.id == "SURFACE"
                        and isinstance(node.value, ast.Constant)
                        and isinstance(node.value.value, str)
                    ):
                        surfaces[node.value.value] = shim.name
    return surfaces


def _vendored_floors(manifest_path: Path) -> dict[str, str | None]:
    """Return {surface_id: min_setec_version-or-None} for every entry in the
    vendored manifest, keyed by `id`/`surface`."""
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    floors: dict[str, str | None] = {}
    for entry in payload.get("entries") or []:
        if not isinstance(entry, dict):
            continue
        sid = entry.get("id") or entry.get("surface")
        if isinstance(sid, str) and sid:
            floors[sid] = entry.get("min_setec_version")
    return floors


def check_client_sha256_offline(
    client_path: Path = VENDORED_CLIENT, lock_path: Path = LOCK_PATH,
) -> list[str]:
    """F1: offline (no live SETEC) proof that the RUNTIME vendored client
    matches the pin in setec-plugin.lock. Hashes the actual file bytes at
    `client_path` and compares to `lock_path`'s `client_sha256` — catches
    EITHER a mutated vendored client OR a corrupted/stale lock entry, since
    either one alone makes the two sides disagree."""
    problems: list[str] = []
    if not client_path.is_file():
        return [f"vendored client missing: {client_path}"]
    if not lock_path.is_file():
        return [f"lock file missing: {lock_path}"]
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"lock file is not valid JSON: {exc}"]
    pinned = lock.get("client_sha256")
    if not isinstance(pinned, str) or not pinned:
        return ["lock file has no client_sha256 pin"]
    actual = hashlib.sha256(client_path.read_bytes()).hexdigest()
    if actual != pinned:
        problems.append(
            f"vendored client {client_path.relative_to(REPO_ROOT)} sha256="
            f"{actual} does not match setec-plugin.lock client_sha256="
            f"{pinned} — the runtime client and/or the lock has drifted "
            f"(offline check; no live SETEC checkout involved)"
        )
    return problems


def check_provisional_lock_warning(lock_path: Path = LOCK_PATH) -> "str | None":
    """F2: `setec-plugin.lock`'s `provisional: true` means this pin is NOT a
    tagged producer release — commonly (as of this writing) a local
    worktree commit with a code-safe provisional label as `source`. That is
    expected and correct WHILE the producer PR is still open, but it must
    be LOUD, not silent: returns a warning string when provisional, else
    None. Downgraded to a WARNING (not a CHECK 1 failure) so CI stays green
    pre-release — a hard failure here would block the consumer PR from even
    being reviewable before the producer PR merges, which is the wrong
    ordering. The actual gate is operational, not automatable from inside
    this repo: EACH CONSUMER PR MUST STAY DRAFT until the producer PR merges
    and the intended release is tagged, at which point
    `python3 scripts/sync_setec.py` is re-run (against the tagged release,
    with SETEC_RELEASE_TAG set — see sync-setec.yml) to produce a
    FINALIZED, non-provisional re-pin before the consumer PR is marked
    ready for review."""
    if not lock_path.is_file():
        return None
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not lock.get("provisional"):
        return None
    return (
        f"setec-plugin.lock is PROVISIONAL (source={lock.get('source')!r}, "
        f"commit={lock.get('commit')!r}) — this pin is NOT a tagged producer "
        f"release. This consumer PR MUST stay DRAFT until the producer PR "
        f"merges and v{lock.get('setec_version', '?')} (or the intended "
        f"release) is tagged, then re-sync with SETEC_RELEASE_TAG set and "
        f"re-pin to a FINALIZED lock before marking it ready for review."
    )


# F13 (spec C2.2 byte-pin, extended to the sync workflow itself): the
# `.github/workflows/sync-setec.yml` bytes are pinned here so an edit that
# e.g. narrows its `add-paths` list to drop the vendored client — silently
# breaking the C2.2 byte-pin's actual PR-delivery path — fails the SAME
# unconditional CI step every PR already runs (`python
# tools/check_setec_contract.py`), instead of landing unreviewed. Update the
# pinned hash here (after reviewing the diff) whenever the workflow file is
# intentionally changed.
PINNED_WORKFLOWS: tuple[tuple[Path, str], ...] = (
    (
        REPO_ROOT / ".github" / "workflows" / "sync-setec.yml",
        "aaa97835b4725134cde9f72881a1e456ce47f8ac6ca887552798b26bd7ab3220",
    ),
)


def check_pinned_workflows(pinned: tuple[tuple[Path, str], ...] = PINNED_WORKFLOWS) -> list[str]:
    """F13: offline (no live SETEC) proof that each pinned CI workflow file
    still hashes to its committed pin. Runs as part of CHECK 1 — the same
    unconditional CI step every PR runs — so a workflow edit (intentional
    or not) is reviewed rather than silently changing CI behavior."""
    problems: list[str] = []
    for path, expected in pinned:
        if not path.is_file():
            problems.append(f"pinned workflow missing: {path}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            problems.append(
                f"pinned workflow {path.relative_to(REPO_ROOT)} sha256={actual} "
                f"does not match the pin {expected!r} in "
                f"tools/check_setec_contract.py's PINNED_WORKFLOWS — review the "
                f"diff and, if intentional, update the pin"
            )
    return problems


def check_self_consistency(
    manifest_path: Path = VENDORED_MANIFEST,
    shim_dir: Path = SHIM_DIR,
    client_path: Path = VENDORED_CLIENT,
    lock_path: Path = LOCK_PATH,
) -> list[str]:
    """CHECK 1. Return a list of problems (empty == OK)."""
    problems: list[str] = list(
        check_client_sha256_offline(client_path=client_path, lock_path=lock_path)
    )
    problems.extend(check_pinned_workflows())
    if not manifest_path.exists():
        return problems + [f"vendored manifest missing: {manifest_path}"]

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    problems.extend(check_contract_policy(payload, client_path, lock_path))

    floors = _vendored_floors(manifest_path)
    shim_surfaces = discover_shim_surfaces(shim_dir)
    if not shim_surfaces:
        problems.append(
            f"no ai_prose_*.py shims with a SURFACE constant found in {shim_dir} "
            f"— cannot verify consumer↔manifest coverage"
        )

    for surface, shim in sorted(shim_surfaces.items()):
        if surface not in floors:
            problems.append(
                f"shim {shim} consumes surface {surface!r}, but it is ABSENT "
                f"from the vendored manifest (producer dropped/renamed a "
                f"consumer surface?)"
            )
        elif not floors[surface]:
            problems.append(
                f"shim {shim} consumes surface {surface!r}, but its vendored "
                f"manifest entry has no min_setec_version (floor undiscoverable)"
            )

    # Also assert the vendored manifest parses through the runtime consumer
    # parser, and that every floored surface APODICTIC shims for is resolvable
    # there — the same code path resolve_floor() uses at runtime.
    try:
        from setec_capabilities import parse_manifest_payload  # noqa: WPS433

        class _FakeLoc:  # parse_manifest_payload only stores .location
            pass

        manifest = parse_manifest_payload(payload, location=_FakeLoc())
        for surface, shim in sorted(shim_surfaces.items()):
            if surface in floors and floors[surface] and surface not in manifest.surfaces:
                problems.append(
                    f"surface {surface!r} (shim {shim}) has a floor in the "
                    f"vendored manifest but does not resolve through the "
                    f"consumer parser — parser/manifest shape mismatch"
                )
    except Exception as exc:  # noqa: BLE001 — surface any parser breakage
        problems.append(f"vendored manifest failed the consumer parser: {exc}")

    return problems


# --------------------------------------------------------------------------
# Drift tri-state (spec C1.3 / setec-consumer-client-contract.md §1.3).
#
# A named local-resolution result, shared vocabulary with voicewright's
# `_cmd_doctor` (which delegates to `discover_setec()` and prints the same
# status names) even though APODICTIC has no doctor command — its direct CI
# invocation of this file's CHECK 2 (live drift vs SETEC `capabilities emit`
# + fixtures + the vendored client) is the stated equivalent (Applicability
# matrix: "C1 doctor: — ; N/A; no doctor exists"). The three states:
#
#   OFFLINE_UNRESOLVED — no SETEC checkout resolvable (no SETEC_VOICEPRINT_DIR,
#     no marketplace install). PASS unless --require-live.
#   RESOLVED_MATCH     — a checkout resolved, and the vendored
#     lock/manifest/fixtures/client all match live SETEC. PASS.
#   RESOLVED_DRIFT      — a checkout resolved, but something diverges (or the
#     sync tooling itself could not be loaded). FAIL.
# --------------------------------------------------------------------------

OFFLINE_UNRESOLVED = "offline_unresolved"
RESOLVED_MATCH = "resolved_match"
RESOLVED_DRIFT = "resolved_drift"


def check_live_drift() -> tuple[str, list[str]]:
    """CHECK 2. Returns (status, problems) where status is one of
    OFFLINE_UNRESOLVED / RESOLVED_MATCH / RESOLVED_DRIFT (spec C1.3's drift
    tri-state). Delegates to sync_setec.cmd_check via its derive() (so the
    gate and the sync script share one definition of "stale"), which also
    covers the vendored client's `client_sha256` (C2.2) once it exists."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        import sync_setec  # noqa: WPS433
    except Exception as exc:  # noqa: BLE001
        return RESOLVED_DRIFT, [f"could not import sync_setec: {exc}"]
    try:
        sync_setec._resolve_setec_root()
    except sync_setec.SyncError:
        return OFFLINE_UNRESOLVED, []
    try:
        rc = sync_setec.cmd_check()
    except sync_setec.SyncError as exc:
        # F8: a resolved-but-malformed source (e.g. a resolvable root whose
        # emit envelope fails project_consumer_manifest's own C2.1/F7
        # contract requirement — missing/non-string/unparseable
        # setec_version, or a required `contract` block silently absent) is
        # a resolved-and-diverges outcome, not a silent skip and never a
        # raw traceback — cmd_check()'s own try/except only wraps a CALL
        # from sync_setec's own __main__, not THIS programmatic call made
        # directly by the drift gate.
        return RESOLVED_DRIFT, [f"live SETEC source is resolvable but malformed: {exc}"]
    if rc == 0:
        return RESOLVED_MATCH, []
    return RESOLVED_DRIFT, ["live SETEC contract drift (see sync_setec --check output above)"]


def run(*, require_live: bool = False) -> int:
    failed = False

    print("== CHECK 1: consumer↔manifest self-consistency (offline) ==")
    problems = check_self_consistency()
    if problems:
        failed = True
        for p in problems:
            print(f"  FAIL: {p}", file=sys.stderr)
    else:
        shims = discover_shim_surfaces()
        print(
            f"  OK: all {len(shims)} shim surfaces present in vendored manifest "
            f"with a floor, and the runtime vendored client matches "
            f"setec-plugin.lock"
        )

    provisional_warning = check_provisional_lock_warning()
    if provisional_warning:
        print(
            f"  WARNING (provisional lock, does not fail CI): {provisional_warning}",
            file=sys.stderr,
        )

    print("== CHECK 2: live drift vs SETEC `capabilities emit` + fixtures ==")
    status, live_problems = check_live_drift()
    print(f"  status: {status}")
    if status == RESOLVED_DRIFT:
        failed = True
        for p in live_problems:
            print(f"  FAIL: {p}", file=sys.stderr)
    elif status == OFFLINE_UNRESOLVED:
        if require_live:
            print("  FAIL: SETEC not resolvable but --require-live was set", file=sys.stderr)
            failed = True
        else:
            print(
                "  SKIPPED: SETEC not resolvable (set SETEC_VOICEPRINT_DIR to "
                "enforce live drift; the weekly sync workflow does this)."
            )
    else:
        print("  OK: vendored contract matches live SETEC.")

    if failed:
        print("\ncheck_setec_contract: FAILED", file=sys.stderr)
        return 1
    print("\ncheck_setec_contract: OK")
    return 0


# --------------------------------------------------------------------------
# Self-test: hostile fixtures for the self-consistency guard (CHECK 1). These
# build a temp vendored manifest + temp shim dir and assert the guard fires
# on (a) a dropped consumer surface and (b) a floor-less consumer surface,
# and stays green on a faithful manifest.
# --------------------------------------------------------------------------

_SHIM_TEMPLATE = '''#!/usr/bin/env python3
"""fixture shim."""
SURFACE = "{surface}"
'''


def _write_fixture(tmp: Path, surfaces_in_manifest: list[tuple[str, str | None]], shim_surfaces: list[str]) -> tuple[Path, Path]:
    manifest = {
        "setec_version": "1.112.0",
        "manifest_schema_version": "0.3.0",
        "entries": [
            {"id": s, "surface": s, "consumers": ["apodictic"], "min_setec_version": floor}
            for s, floor in surfaces_in_manifest
        ],
    }
    mpath = tmp / "manifest.json"
    mpath.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    sdir = tmp / "shims"
    sdir.mkdir()
    for s in shim_surfaces:
        (sdir / f"ai_prose_{s}.py").write_text(_SHIM_TEMPLATE.format(surface=s), encoding="utf-8")
    return mpath, sdir


def _self_test() -> int:
    failures = 0

    def case(name: str, manifest_surfaces, shim_surfaces, expect_problem: bool):
        nonlocal failures
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            mpath, sdir = _write_fixture(tmp, manifest_surfaces, shim_surfaces)
            problems = check_self_consistency(manifest_path=mpath, shim_dir=sdir)
            got = bool(problems)
            ok = got == expect_problem
            print(f"  [{'PASS' if ok else 'FAIL'}] {name}: problems={problems!r}")
            if not ok:
                failures += 1

    # Faithful: shim surface present + floored -> green.
    case(
        "faithful manifest is green",
        [("variance_audit", "1.86.0"), ("narrative_decision_audit", "1.107.0")],
        ["variance_audit", "narrative_decision_audit"],
        expect_problem=False,
    )
    # Producer dropped a consumer surface the shim still references -> fire.
    case(
        "dropped consumer surface fires",
        [("variance_audit", "1.86.0")],
        ["variance_audit", "narrative_decision_audit"],
        expect_problem=True,
    )
    # Surface present but floor-less -> fire.
    case(
        "floor-less consumer surface fires",
        [("variance_audit", None)],
        ["variance_audit"],
        expect_problem=True,
    )

    payload = json.loads(VENDORED_MANIFEST.read_text(encoding="utf-8"))
    hostile = dict(payload)
    hostile["owner_signed_exception"] = True
    problems = check_contract_policy(hostile, VENDORED_CLIENT, LOCK_PATH)
    ok = any("manifest root" in problem for problem in problems)
    print(f"  [{'PASS' if ok else 'FAIL'}] extra manifest root key fires")
    failures += int(not ok)

    hostile = dict(payload)
    hostile["manifest_schema_version"] = "9.9.9"
    problems = check_contract_policy(hostile, VENDORED_CLIENT, LOCK_PATH)
    ok = any("independent 0.4.0 pin" in problem for problem in problems)
    print(f"  [{'PASS' if ok else 'FAIL'}] co-drifted manifest schema fires")
    failures += int(not ok)

    hostile = dict(payload)
    hostile["setec_version"] = "1.129"
    hostile.pop("contract")
    problems = check_contract_policy(hostile, VENDORED_CLIENT, LOCK_PATH)
    ok = any("no contract mapping" in problem for problem in problems)
    print(f"  [{'PASS' if ok else 'FAIL'}] short-form floor still requires contract")
    failures += int(not ok)

    hostile = dict(payload)
    hostile["setec_version"] = "1.129.0-rc.1"
    hostile.pop("contract")
    problems = check_contract_policy(hostile, VENDORED_CLIENT, LOCK_PATH)
    ok = not any("no contract mapping" in problem for problem in problems)
    print(f"  [{'PASS' if ok else 'FAIL'}] prerelease below floor may omit contract")
    failures += int(not ok)

    if failures:
        print(f"\ncheck_setec_contract --self-test: FAIL ({failures} case(s))", file=sys.stderr)
        return 1
    print("\ncheck_setec_contract --self-test: PASS")
    return 0


# --------------------------------------------------------------------------
# Self-test: hermetic drift tri-state (spec C1.3). Builds a synthetic SETEC
# plugin root on disk (a stand-in `capabilities.py` + a tiny contract_fixtures
# dir) and a synthetic "vendored" copy this test fully controls (via
# monkeypatched `sync_setec` path constants — NOT the repo's real committed
# vendored files), so the tri-state fires without assuming CI has a sibling
# SETEC checkout (mirrors the hostile-fixture pattern above). Exercises the
# REAL `sync_setec` derive/compare machinery end to end (subprocess `emit`,
# `cmd_check`'s manifest/fixtures/lock compare), only the storage locations
# are redirected to a tempdir.
# --------------------------------------------------------------------------

_FAKE_CAPABILITIES_TEMPLATE = '''#!/usr/bin/env python3
import json
import sys

MANIFEST = {manifest_json}

if __name__ == "__main__":
    print(json.dumps(MANIFEST))
'''


def _build_synthetic_setec_root(tmp: Path) -> Path:
    """A minimal synthetic SETEC plugin root well BELOW
    CONTRACT_BLOCK_MIN_SETEC_VERSION (so no `contract` block is required —
    this test exercises drift mechanics, not contract-presence, which has
    its own dedicated tests): a plugin.json, a stand-in
    `scripts/capabilities.py` that prints a fixed manifest for any args, and
    a one-file `references/contract_fixtures/` dir. Enough for
    `sync_setec.emit_manifest` + `cmd_check`'s fixtures compare; deliberately
    NOT enough for `cmd_write`'s stricter per-shim-surface golden guard (this
    self-test never calls `cmd_write`).

    F5/F10: `setec_version` (not `manifest_schema_version`) now GATES
    whether `project_consumer_manifest` requires a `contract` block. The
    prior fixture used "9.9.9", which trivially exceeds ANY real floor
    (including CONTRACT_BLOCK_MIN_SETEC_VERSION) — once the gating rule
    keyed on setec_version, that would make this fixture (which has no
    `contract` key) raise SyncError the moment `derive()` runs. Pinned
    below the floor here so "resolved_match" still means what it says."""
    root = tmp / "synthetic-setec-voiceprint"
    (root / ".claude-plugin").mkdir(parents=True)
    (root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "setec-voiceprint", "version": "1.128.0"}),
        encoding="utf-8",
    )
    (root / "scripts").mkdir()
    manifest = {
        "setec_version": "1.128.0",
        "manifest_schema_version": "0.3.0",
        "entries": [],
    }
    (root / "scripts" / "capabilities.py").write_text(
        _FAKE_CAPABILITIES_TEMPLATE.format(manifest_json=json.dumps(manifest)),
        encoding="utf-8",
    )
    fixtures = root / "references" / "contract_fixtures"
    fixtures.mkdir(parents=True)
    (fixtures / "onefile.txt").write_text("hello\n", encoding="utf-8")
    client_dir = root / "scripts" / "setec"
    client_dir.mkdir(parents=True)
    (client_dir / "__init__.py").write_text("", encoding="utf-8")
    (client_dir / "consumer_client.py").write_text(
        '"""synthetic stand-in for the shared consumer client."""\n'
        "VALUE = 1\n",
        encoding="utf-8",
    )
    return root


def _self_test_drift_tristate() -> int:
    import shutil

    failures = 0
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import sync_setec  # noqa: WPS433

    def report(name: str, ok: bool) -> None:
        nonlocal failures
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            failures += 1

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        synthetic_root = _build_synthetic_setec_root(tmp)
        vendor_dir = tmp / "vendored"
        vendor_dir.mkdir()
        vendored_manifest = vendor_dir / "setec-capabilities.json"
        vendored_fixtures = vendor_dir / "fixtures"
        lock_path = tmp / "setec-plugin.lock"
        client_runtime_destination = tmp / "_vendored_setec_client.py"

        # Redirect sync_setec's storage constants at this test's tempdir so
        # the comparison never touches the repo's real committed vendored
        # copy — a fully hermetic tri-state, not one keyed to today's pin.
        orig = (
            sync_setec.VENDOR_DIR, sync_setec.VENDORED_MANIFEST,
            sync_setec.VENDORED_FIXTURES, sync_setec.LOCK_PATH,
            sync_setec.CLIENT_RUNTIME_DESTINATION,
        )
        orig_env = os.environ.get("SETEC_VOICEPRINT_DIR")
        orig_release_tag = os.environ.get("SETEC_RELEASE_TAG")
        try:
            sync_setec.VENDOR_DIR = vendor_dir
            sync_setec.VENDORED_MANIFEST = vendored_manifest
            sync_setec.VENDORED_FIXTURES = vendored_fixtures
            sync_setec.LOCK_PATH = lock_path
            sync_setec.CLIENT_RUNTIME_DESTINATION = client_runtime_destination

            # The weekly sync exports SETEC_RELEASE_TAG so its real re-pin is
            # finalized. This synthetic arm deliberately exercises the
            # provisional fallback, so inherited workflow state must not
            # change the fixture's semantics.
            os.environ.pop("SETEC_RELEASE_TAG", None)

            # --- offline_unresolved: SETEC_VOICEPRINT_DIR points at a path
            # with no plugin.json, so _resolve_setec_root raises immediately
            # (never falls through to a real marketplace install on this
            # machine — hermetic regardless of dev-box state).
            os.environ["SETEC_VOICEPRINT_DIR"] = str(tmp / "not-a-setec-root")
            (tmp / "not-a-setec-root").mkdir()
            status, _ = check_live_drift()
            report(f"offline_unresolved fires with no plugin.json (got {status})", status == OFFLINE_UNRESOLVED)

            # --- resolved_match: seed the vendored copy (manifest, fixtures,
            # lock, AND the runtime vendored client) by deriving+writing from
            # the synthetic root directly (NOT via cmd_write, which
            # additionally requires a golden per real shim surface).
            os.environ["SETEC_VOICEPRINT_DIR"] = str(synthetic_root)
            manifest_str, lock, client_source_bytes = sync_setec.derive(synthetic_root)
            report(
                "provisional lock source omits machine-local checkout path",
                lock.get("source") == "local worktree (provisional)"
                and str(synthetic_root) not in json.dumps(lock),
            )
            vendored_manifest.write_text(manifest_str, encoding="utf-8")
            shutil.copytree(
                synthetic_root / sync_setec.CONTRACT_FIXTURES_SUBDIR, vendored_fixtures
            )
            sync_setec._copy_client(client_source_bytes, client_runtime_destination)
            lock_path.write_text(sync_setec._serialize_lock(lock), encoding="utf-8")
            status, _ = check_live_drift()
            report(f"resolved_match fires on a faithfully-seeded vendored copy (got {status})", status == RESOLVED_MATCH)

            # --- resolved_drift: byte-mutate the vendored fixtures copy
            # (simulates a stale runtime client / fixture) and re-check.
            (vendored_fixtures / "onefile.txt").write_text("mutated\n", encoding="utf-8")
            status, _ = check_live_drift()
            report(f"resolved_drift fires on a byte-mutated vendored fixture (got {status})", status == RESOLVED_DRIFT)
            (vendored_fixtures / "onefile.txt").write_text("hello\n", encoding="utf-8")  # revert

            # --- resolved_drift: byte-mutate the RUNTIME VENDORED CLIENT
            # itself (acceptance gate 3's first mutation-negative proof —
            # "delete or mutate one byte in each runtime client and observe
            # offline CHECK 1 fail") — the lock is untouched here, so this
            # exercises cmd_check's separate runtime-destination re-hash, not
            # the lock-key compare.
            client_runtime_destination.write_bytes(
                client_runtime_destination.read_bytes() + b"\n# mutated\n"
            )
            status, _ = check_live_drift()
            report(
                f"resolved_drift fires on a byte-mutated RUNTIME vendored client (got {status})",
                status == RESOLVED_DRIFT,
            )
            sync_setec._copy_client(client_source_bytes, client_runtime_destination)  # revert

            # --- resolved_drift: alter ONLY the lock's client_sha256 (the
            # runtime client file itself is untouched) — acceptance gate 3's
            # second mutation-negative proof ("alter only lock client_sha256
            # and observe fail").
            lock_bad_hash = dict(lock)
            lock_bad_hash["client_sha256"] = "0" * 64
            lock_path.write_text(sync_setec._serialize_lock(lock_bad_hash), encoding="utf-8")
            status, _ = check_live_drift()
            report(
                f"resolved_drift fires on a lock-only client_sha256 corruption (got {status})",
                status == RESOLVED_DRIFT,
            )

            # --- resolved_drift via a different lock field corrupted alone
            # (fixtures/manifest/client untouched) — proves the general
            # lock-key compare, not just client_sha256.
            lock_bad = dict(lock)
            lock_bad["plugin_version"] = "0.0.0-corrupted"
            lock_path.write_text(sync_setec._serialize_lock(lock_bad), encoding="utf-8")
            status, _ = check_live_drift()
            report(f"resolved_drift fires on a lock-only divergence (got {status})", status == RESOLVED_DRIFT)
        finally:
            (
                sync_setec.VENDOR_DIR, sync_setec.VENDORED_MANIFEST,
                sync_setec.VENDORED_FIXTURES, sync_setec.LOCK_PATH,
                sync_setec.CLIENT_RUNTIME_DESTINATION,
            ) = orig
            if orig_env is None:
                os.environ.pop("SETEC_VOICEPRINT_DIR", None)
            else:
                os.environ["SETEC_VOICEPRINT_DIR"] = orig_env
            if orig_release_tag is None:
                os.environ.pop("SETEC_RELEASE_TAG", None)
            else:
                os.environ["SETEC_RELEASE_TAG"] = orig_release_tag

    if failures:
        print(
            f"\ncheck_setec_contract --self-test (drift tri-state): FAIL "
            f"({failures} case(s))",
            file=sys.stderr,
        )
        return 1
    print("\ncheck_setec_contract --self-test (drift tri-state): PASS")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        rc1 = _self_test()
        rc2 = _self_test_drift_tristate()
        return 1 if (rc1 or rc2) else 0
    require_live = "--require-live" in argv
    return run(require_live=require_live)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
