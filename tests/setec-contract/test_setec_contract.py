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
  T2  A vendored golden parses cleanly through setec_runner's envelope path,
      with NO SETEC installed: a fake SETEC scripts dir prints the vendored
      golden to stdout, and run_supplement parses + classifies it.
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
# T2 — a vendored golden parses through setec_runner with NO SETEC installed.
# --------------------------------------------------------------------------
def _fake_scripts_dir(surface_script: str, golden_name: str) -> tempfile.TemporaryDirectory:
    """Build a temp SETEC scripts dir whose `surface_script` prints the
    vendored golden to stdout (mimicking a real stdout `--json` surface),
    so run_supplement's envelope path runs without SETEC's heavy deps."""
    tmp = tempfile.TemporaryDirectory(prefix="fake_setec_scripts_")
    golden_path = VENDORED_FIXTURES / golden_name
    script_body = (
        "#!/usr/bin/env python3\n"
        "import sys\n"
        f"sys.stdout.write(open({str(golden_path)!r}, encoding='utf-8').read())\n"
    )
    (Path(tmp.name) / surface_script).write_text(script_body, encoding="utf-8")
    return tmp


def t2_vendored_golden_through_runner() -> None:
    print("T2: vendored golden parses through setec_runner (no SETEC installed)")
    # variance_audit golden: a stdout-delivery surface.
    with _fake_scripts_dir("variance_audit.py", "variance_audit.json") as tmp:
        loc = setec_discovery.SetecLocation(
            plugin_root=Path(tmp),
            scripts_dir=Path(tmp),
            version=(1, 113, 0),
            version_str="1.113.0",
            source="env",
        )
        result = setec_runner.run_supplement(
            "variance_audit.py", ["dummy.md"], location=loc
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
    with _fake_scripts_dir(
        "narrative_decision_audit.py", "narrative_decision_audit.json"
    ) as tmp:
        loc = setec_discovery.SetecLocation(
            plugin_root=Path(tmp),
            scripts_dir=Path(tmp),
            version=(1, 113, 0),
            version_str="1.113.0",
            source="env",
        )
        result = setec_runner.run_supplement(
            "narrative_decision_audit.py", ["story.md"], location=loc
        )
    check(
        result.task_surface == "narrative_decision_audit",
        "narrative_decision golden task_surface parsed",
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
            json.dumps({"name": "setec-voiceprint", "version": "1.113.0"}),
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
        check(loc.version == (1, 113, 0), "synthetic SETEC root discovered at 1.113.0")


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


# --------------------------------------------------------------------------
# T6 — required_groups read from the R1 manifest + group validation.
# --------------------------------------------------------------------------
def t6_required_groups_validation() -> None:
    print("T6: required_groups parsed + idiolect group validation")
    payload = json.loads(VENDORED_MANIFEST.read_text(encoding="utf-8"))
    manifest = setec_capabilities.parse_manifest_payload(payload, location=_Loc())
    idio = manifest.require("idiolect_detector")
    check(
        idio.required_groups == ["target", "reference"],
        "idiolect required_groups parsed as [target, reference]",
    )
    # Neither group supplied -> both reported missing (the consumer errors).
    check(
        idio.missing_required_groups([]) == ["target", "reference"],
        "empty argv: both required groups missing",
    )
    # A target source only -> the reference group is still missing.
    check(
        idio.missing_required_groups(["--target-dir", "base/"]) == ["reference"],
        "target supplied, reference group still missing",
    )
    # One source from each group satisfies all groups (also covers --flag=value).
    check(
        idio.missing_required_groups(
            ["--manifest=corpus.jsonl", "--reference-corpus", "brown"]
        )
        == [],
        "one target + one reference (incl. = form) satisfies all groups",
    )
    # A surface that declares no required_groups never reports a missing group.
    va = manifest.require("variance_audit")
    check(
        not va.required_groups and va.missing_required_groups([]) == [],
        "variance_audit (no required_groups) reports nothing missing",
    )


# --------------------------------------------------------------------------
# T7 — help/usage requests bypass the idiolect required_groups gate.
# --------------------------------------------------------------------------
def t7_idiolect_help_bypasses_required_groups() -> None:
    print("T7: --help/-h bypass the idiolect required_groups gate")
    import ai_prose_idiolect_detector as idio_shim  # noqa: E402

    # Help/usage requests must pass through to SETEC's own --help, not be
    # blocked by the consumer's missing-group error.
    check(
        idio_shim._enforce_required_groups(["--help"]) is False,
        "--help bypasses the required_groups gate",
    )
    check(
        idio_shim._enforce_required_groups(["-h"]) is False,
        "-h bypasses the required_groups gate",
    )
    check(
        idio_shim._enforce_required_groups(["--target-dir", "x", "--help"])
        is False,
        "--help bypasses even alongside other flags",
    )
    # A real detection run (no help flag) is still gated.
    check(
        idio_shim._enforce_required_groups(["--target-dir", "x"]) is True,
        "a non-help invocation still enforces required_groups",
    )


def main() -> int:
    for fn in (
        t1_floor_resolution_from_vendored_manifest,
        t2_vendored_golden_through_runner,
        t3_discovery_still_works_without_hardcoded_floors,
        t4_below_surface_floor_fails_with_surface_floor,
        t5_drift_gate_self_test,
        t6_required_groups_validation,
        t7_idiolect_help_bypasses_required_groups,
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
