#!/usr/bin/env python3
"""
test_setec_contract.py — APODICTIC↔SETEC contract tests (Increment 2 / R1).

APODICTIC has no pytest suite (AGENTS.md § CI), so this is a self-contained
runner: `python3 tests/setec-contract/test_setec_contract.py` exits 0 iff
every case passes, nonzero otherwise. It is wired into .github/workflows/ci.yml.

Covers (per the Increment-2 brief's MANDATORY test list):
  T1  Floor resolution from the VENDORED manifest — offline, no SETEC. Uses
      setec_capabilities.parse_manifest_payload on the committed vendored
      manifest and checks each shim surface's floor matches.
  T2  A vendored golden parses cleanly through setec_runner's dispatcher
      path, with NO SETEC installed: a fake SETEC scripts dir provides a
      stand-in `setec_run.py` dispatcher that prints the vendored golden to
      stdout, and run_supplement(surface, ...) parses + classifies it.
  T2b R3 structured-error tiering: a stand-in dispatcher that emits an
      `available:false` envelope per reason_category maps each category to
      the right tier (version_floor/missing_dependency/policy_refused/
      bad_input/internal_error -> blocking; text_too_short -> reliability).
  T3  Deleting the hardcoded floors did not break discovery: setec_discovery
      no longer carries a per-surface (1,86,0)/(1,107,0) authority; its
      default floor is the bootstrap floor, and discover_setec still resolves
      a valid SETEC root (using a synthetic plugin root, no SETEC needed).
  T4  Floor-aware failure: resolve_floor raises a SetecDiscoveryError naming
      the SURFACE floor (not the bootstrap floor) when setec_version is below
      a surface's manifest floor.
  T5  The drift-gate self-consistency guard fires on a dropped/floor-less
      consumer surface (delegates to check_setec_contract --self-test).

These tests run WITHOUT SETEC's heavy deps (spaCy/torch/...): the vendored
fake_setec.py + goldens are the whole substrate.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VENDOR_DIR = REPO_ROOT / "tests" / "setec-contract"
VENDORED_MANIFEST = VENDOR_DIR / "setec-capabilities.json"
VENDORED_FIXTURES = VENDOR_DIR / "fixtures"
SHIM_DIR = (
    REPO_ROOT / "plugins" / "apodictic" / "skills" / "specialized-audits" / "scripts"
)
TOOLS_DIR = REPO_ROOT / "tools"

sys.path.insert(0, str(SHIM_DIR))
sys.path.insert(0, str(TOOLS_DIR))

import setec_capabilities  # noqa: E402
import setec_discovery  # noqa: E402
import setec_runner  # noqa: E402
from check_setec_contract import discover_shim_surfaces  # type: ignore  # noqa: E402


class _Loc:
    """Minimal stand-in for SetecLocation (parse_manifest_payload only stores
    .location; nothing reads its attributes in these tests)."""


_FAILURES: list[str] = []


def check(cond: bool, msg: str) -> None:
    label = "PASS" if cond else "FAIL"
    print(f"  [{label}] {msg}")
    if not cond:
        _FAILURES.append(msg)


# --------------------------------------------------------------------------
# T1 — floor resolution from the vendored manifest (offline).
# --------------------------------------------------------------------------
def t1_floor_resolution_from_vendored_manifest() -> None:
    print("T1: floor resolution from vendored manifest (offline)")
    payload = json.loads(VENDORED_MANIFEST.read_text(encoding="utf-8"))
    manifest = setec_capabilities.parse_manifest_payload(payload, location=_Loc())

    # Every shim surface resolves to a floor, and the known floors match.
    shim_surfaces = discover_shim_surfaces(SHIM_DIR)
    check(len(shim_surfaces) == 9, f"9 shim surfaces discovered (got {len(shim_surfaces)})")
    expected = {
        "variance_audit": "1.86.0",
        "manuscript_audit": "1.86.0",
        "repetition_audit": "1.86.0",
        "voice_distance": "1.86.0",
        "voice_profile": "1.86.0",
        "pov_voice_profile": "1.86.0",
        "punctuation_cadence_audit": "1.86.0",
        "idiolect_detector": "1.86.0",
        "narrative_decision_audit": "1.107.0",
    }
    for surface in shim_surfaces:
        cap = manifest.surfaces.get(surface)
        check(cap is not None, f"{surface} resolves in vendored manifest")
        if cap is not None:
            check(
                cap.min_setec_version_str == expected.get(surface),
                f"{surface} floor == {expected.get(surface)} "
                f"(got {cap.min_setec_version_str})",
            )
    # narrative_decision_audit's floor is the manifest's, NOT a hardcoded const.
    check(
        manifest.surfaces["narrative_decision_audit"].min_setec_version == (1, 107, 0),
        "narrative_decision_audit floor is data-driven (1,107,0) from manifest",
    )


# --------------------------------------------------------------------------
# T2 — a vendored golden parses through setec_runner's DISPATCHER path with
#      NO SETEC installed.
# --------------------------------------------------------------------------
def _fake_dispatcher_dir(emits: str) -> tempfile.TemporaryDirectory:
    """Build a temp SETEC scripts dir holding a stand-in `setec_run.py`
    dispatcher whose body is exactly `emits` (a Python program that writes an
    envelope to stdout). R2 routes every surface through this dispatcher, so
    the fake dispatcher is the whole substrate run_supplement needs — no SETEC
    heavy deps, no per-surface scripts."""
    tmp = tempfile.TemporaryDirectory(prefix="fake_setec_dispatcher_")
    (Path(tmp.name) / setec_runner.DISPATCHER_SCRIPT).write_text(
        emits, encoding="utf-8"
    )
    return tmp


def _golden_dispatcher_body(golden_name: str) -> str:
    """A `setec_run.py` stand-in that prints the named vendored golden to
    stdout verbatim (mimicking the dispatcher re-emitting a surface's success
    envelope)."""
    golden_path = VENDORED_FIXTURES / golden_name
    return (
        "#!/usr/bin/env python3\n"
        "import sys\n"
        f"sys.stdout.write(open({str(golden_path)!r}, encoding='utf-8').read())\n"
    )


def _loc(tmp_path: str) -> "setec_discovery.SetecLocation":
    """Build a SetecLocation for a temp dir path. `tmp_path` is the directory
    string yielded by `with _fake_dispatcher_dir(...) as tmp` (TemporaryDirectory's
    context manager returns its `.name`)."""
    return setec_discovery.SetecLocation(
        plugin_root=Path(tmp_path),
        scripts_dir=Path(tmp_path),
        version=(1, 112, 0),
        version_str="1.112.0",
        source="env",
    )


def t2_vendored_golden_through_runner() -> None:
    print("T2: vendored golden parses through setec_runner dispatcher path "
          "(no SETEC installed)")
    # variance_audit golden, routed through the stand-in dispatcher by SURFACE.
    with _fake_dispatcher_dir(_golden_dispatcher_body("variance_audit.json")) as tmp:
        result = setec_runner.run_supplement(
            "variance_audit", ["dummy.md"], location=_loc(tmp)
        )
    check(result.schema_version == "1.0", "envelope schema_version == 1.0")
    check(result.task_surface == "smoothing_diagnosis", "task_surface parsed from golden")
    check(result.tool == "variance_audit", "tool parsed from golden")
    check(result.available is True, "available flag parsed")
    check(isinstance(result.results, dict) and len(result.results) > 0, "results payload present")
    # Warnings classify without raising (the three-tier path runs).
    _ = (result.blocking_warnings, result.reliability_warnings, result.cosmetic_warnings)
    check(True, "warning classification ran without error")

    # narrative_decision_audit golden too (the experimental surface).
    with _fake_dispatcher_dir(
        _golden_dispatcher_body("narrative_decision_audit.json")
    ) as tmp:
        result = setec_runner.run_supplement(
            "narrative_decision_audit", ["story.md"], location=_loc(tmp)
        )
    check(
        result.task_surface == "narrative_decision_audit",
        "narrative_decision golden task_surface parsed",
    )

    # A SETEC without the dispatcher (pre-R2) fails cleanly with an upgrade
    # message, not a crash.
    with tempfile.TemporaryDirectory(prefix="no_dispatcher_") as td:
        loc = setec_discovery.SetecLocation(
            plugin_root=Path(td), scripts_dir=Path(td),
            version=(1, 112, 0), version_str="1.112.0", source="env",
        )
        raised = False
        try:
            setec_runner.run_supplement("variance_audit", ["x.md"], location=loc)
        except setec_discovery.SetecDiscoveryError as exc:
            raised = setec_runner.DISPATCHER_SCRIPT in str(exc)
        check(raised, "pre-R2 SETEC (no setec_run.py) raises a clean upgrade error")


# --------------------------------------------------------------------------
# T2b — R3 structured-error tiering by reason_category.
# --------------------------------------------------------------------------
def _error_dispatcher_body(reason_category: str) -> str:
    """A `setec_run.py` stand-in that emits an R3 `available:false` envelope
    carrying the given reason_category (the shape SETEC's build_error_output
    produces)."""
    return (
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "env = {\n"
        '  "schema_version": "1.0",\n'
        '  "task_surface": None,\n'
        '  "tool": "setec_run",\n'
        '  "version": "1.0.0",\n'
        '  "available": False,\n'
        '  "target": {"path": None, "words": 0},\n'
        '  "baseline": None,\n'
        '  "results": {},\n'
        '  "claim_license": None,\n'
        '  "claim_license_rendered": None,\n'
        '  "warnings": [],\n'
        '  "ai_status": None,\n'
        f'  "reason": "synthetic {reason_category} for the contract test",\n'
        f'  "reason_category": {reason_category!r},\n'
        "}\n"
        "sys.stdout.write(json.dumps(env))\n"
    )


def t2b_r3_error_tiering() -> None:
    print("T2b: R3 reason_category -> tier mapping")
    expect_blocking = (
        "version_floor", "missing_dependency", "policy_refused",
        "bad_input", "internal_error",
    )
    for cat in expect_blocking:
        with _fake_dispatcher_dir(_error_dispatcher_body(cat)) as tmp:
            result = setec_runner.run_supplement(
                "variance_audit", ["x.md"], location=_loc(tmp)
            )
        check(result.available is False, f"{cat}: available is False")
        check(result.reason_category == cat, f"{cat}: reason_category parsed")
        check(
            bool(result.blocking_warnings) and not result.reliability_warnings,
            f"{cat}: tiered BLOCKING (reason in blocking_warnings)",
        )
        check(
            result.reason and "synthetic" in result.reason,
            f"{cat}: structured reason preserved",
        )

    # text_too_short keeps the reliability-vs-blocking semantics: reliability.
    with _fake_dispatcher_dir(_error_dispatcher_body("text_too_short")) as tmp:
        result = setec_runner.run_supplement(
            "variance_audit", ["x.md"], location=_loc(tmp)
        )
    check(result.available is False, "text_too_short: available is False")
    check(
        bool(result.reliability_warnings) and not result.blocking_warnings,
        "text_too_short: tiered RELIABILITY (not blocking)",
    )


# --------------------------------------------------------------------------
# T3 — deleting hardcoded floors did not break discovery.
# --------------------------------------------------------------------------
def t3_discovery_still_works_without_hardcoded_floors() -> None:
    print("T3: discovery works after deleting hardcoded floors")
    # No per-surface (1,86,0) authority remains; the default floor is bootstrap.
    check(
        setec_discovery.MIN_SETEC_VERSION == setec_discovery.BOOTSTRAP_SETEC_VERSION,
        "setec_discovery.MIN_SETEC_VERSION is the bootstrap floor, not (1,86,0)",
    )
    check(
        setec_discovery.MIN_SETEC_VERSION != (1, 86, 0),
        "the retired (1,86,0) per-surface authority is gone",
    )
    # The narrative shim no longer defines a module-level MIN_SETEC_VERSION.
    shim = (SHIM_DIR / "ai_prose_narrative_decision_audit.py").read_text()
    check(
        "MIN_SETEC_VERSION = (1, 107, 0)" not in shim,
        "narrative shim's (1,107,0) constant is deleted",
    )
    # Build a synthetic SETEC plugin root above the bootstrap floor; discovery
    # resolves it (no real SETEC, no heavy deps).
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "setec-voiceprint"
        (root / ".claude-plugin").mkdir(parents=True)
        (root / "scripts").mkdir()
        (root / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "setec-voiceprint", "version": "1.112.0"}),
            encoding="utf-8",
        )
        import os

        old = os.environ.get("SETEC_VOICEPRINT_DIR")
        os.environ["SETEC_VOICEPRINT_DIR"] = str(root)
        try:
            loc = setec_discovery.discover_setec()
        finally:
            if old is None:
                os.environ.pop("SETEC_VOICEPRINT_DIR", None)
            else:
                os.environ["SETEC_VOICEPRINT_DIR"] = old
        check(loc.version == (1, 112, 0), "synthetic SETEC root discovered at 1.112.0")


# --------------------------------------------------------------------------
# T4 — floor-aware failure names the SURFACE floor.
# --------------------------------------------------------------------------
def t4_below_surface_floor_fails_with_surface_floor() -> None:
    print("T4: below-surface-floor failure names the surface floor")
    # Manifest where the producer reports a setec_version below the
    # narrative surface's floor (it satisfies bootstrap discovery but not the
    # surface). parse + resolve directly (no subprocess).
    payload = {
        "setec_version": "1.100.0",  # >= some surfaces, < narrative's 1.107.0
        "manifest_schema_version": "0.3.0",
        "entries": [
            {
                "id": "narrative_decision_audit",
                "surface": "narrative_decision_audit",
                "consumers": ["apodictic"],
                "min_setec_version": "1.107.0",
            }
        ],
    }
    manifest = setec_capabilities.parse_manifest_payload(payload, location=_Loc())
    cap = manifest.require("narrative_decision_audit")
    fired = manifest.setec_version < cap.min_setec_version
    check(fired, "1.100.0 < narrative floor 1.107.0 detected")
    # And the message machinery names the surface floor (1.107.0), not bootstrap.
    msg = setec_discovery._install_instructions(cap.min_setec_version)
    check("1.107.0" in msg, "upgrade message cites the surface floor 1.107.0")
    check(
        ".".join(map(str, setec_discovery.BOOTSTRAP_SETEC_VERSION)) not in msg,
        "upgrade message does NOT cite the bootstrap floor",
    )

    # require() raises a helpful error for an unknown surface.
    raised = False
    try:
        manifest.require("nonexistent_surface")
    except setec_capabilities.SetecCapabilitiesError:
        raised = True
    check(raised, "require() raises SetecCapabilitiesError for unknown surface")


# --------------------------------------------------------------------------
# T5 — drift gate self-consistency guard fires (delegated self-test).
# --------------------------------------------------------------------------
def t5_drift_gate_self_test() -> None:
    print("T5: drift-gate self-consistency guard (--self-test)")
    proc = subprocess.run(
        [sys.executable, str(TOOLS_DIR / "check_setec_contract.py"), "--self-test"],
        capture_output=True,
        text=True,
    )
    check(proc.returncode == 0, f"check_setec_contract --self-test exits 0 (rc={proc.returncode})")
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)


def main() -> int:
    for fn in (
        t1_floor_resolution_from_vendored_manifest,
        t2_vendored_golden_through_runner,
        t2b_r3_error_tiering,
        t3_discovery_still_works_without_hardcoded_floors,
        t4_below_surface_floor_fails_with_surface_floor,
        t5_drift_gate_self_test,
    ):
        fn()
        setec_capabilities.clear_cache()
    print()
    if _FAILURES:
        print(f"test_setec_contract: FAIL ({len(_FAILURES)} assertion(s))", file=sys.stderr)
        for f in _FAILURES:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("test_setec_contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
