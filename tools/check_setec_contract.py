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

import json
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

# Make the consumer parser importable so the gate validates the vendored
# manifest through the SAME parse path the runtime uses.
sys.path.insert(0, str(SHIM_DIR))


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


def check_self_consistency(
    manifest_path: Path = VENDORED_MANIFEST,
    shim_dir: Path = SHIM_DIR,
) -> list[str]:
    """CHECK 1. Return a list of problems (empty == OK)."""
    problems: list[str] = []
    if not manifest_path.exists():
        return [f"vendored manifest missing: {manifest_path}"]

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

        payload = json.loads(manifest_path.read_text(encoding="utf-8"))

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


def check_live_drift() -> tuple[str, list[str]]:
    """CHECK 2. Returns (status, problems) where status is 'ok', 'skipped',
    or 'failed'. Delegates to sync_setec.cmd_check via its derive() (so the
    gate and the sync script share one definition of "stale")."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        import sync_setec  # noqa: WPS433
    except Exception as exc:  # noqa: BLE001
        return "failed", [f"could not import sync_setec: {exc}"]
    try:
        setec_root = sync_setec._resolve_setec_root()
    except sync_setec.SyncError:
        return "skipped", []
    rc = sync_setec.cmd_check()
    if rc == 0:
        return "ok", []
    return "failed", ["live SETEC contract drift (see sync_setec --check output above)"]


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
        print(f"  OK: all {len(shims)} shim surfaces present in vendored manifest with a floor")

    print("== CHECK 2: live drift vs SETEC `capabilities emit` + fixtures ==")
    status, live_problems = check_live_drift()
    if status == "failed":
        failed = True
        for p in live_problems:
            print(f"  FAIL: {p}", file=sys.stderr)
    elif status == "skipped":
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

    if failures:
        print(f"\ncheck_setec_contract --self-test: FAIL ({failures} case(s))", file=sys.stderr)
        return 1
    print("\ncheck_setec_contract --self-test: PASS")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return _self_test()
    require_live = "--require-live" in argv
    return run(require_live=require_live)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
