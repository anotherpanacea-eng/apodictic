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
  T2b R3 structured-error tiering, driven by the REAL SETEC dispatcher. When
      SETEC is resolvable (SETEC_VOICEPRINT_DIR or a marketplace install, and
      it carries setec_run.py + build_error_output), drive the real dispatcher
      to PRODUCE error envelopes — an unknown surface (bad_input) and a forced
      below-floor case (version_floor) — and assert run_supplement turns each
      REAL envelope into a blocking SupplementResult with the right
      reason_category. No hand-rolled JSON: if build_error_output drifts, the
      real envelope changes and this test sees it. SKIPS cleanly when SETEC is
      absent (offline CI), exactly as the drift gate's CHECK 2 skips.
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
_SKIPS: list[str] = []


def check(cond: bool, msg: str) -> None:
    label = "PASS" if cond else "FAIL"
    print(f"  [{label}] {msg}")
    if not cond:
        _FAILURES.append(msg)


def note_skip(msg: str) -> None:
    """Record a clean skip (offline CI without SETEC), mirroring the drift
    gate's CHECK 2 skip: not a failure, just a notice."""
    print(f"  [SKIP] {msg}")
    _SKIPS.append(msg)


def _resolve_real_setec() -> "setec_discovery.SetecLocation | None":
    """Resolve a real SETEC checkout for the real-dispatcher path, or return
    None to skip cleanly when SETEC is absent (offline CI) — exactly as the
    drift gate's CHECK 2 skips when SETEC is not resolvable.

    Resolution goes through the consumer's own `discover_setec` (which reads
    SETEC_VOICEPRINT_DIR or a marketplace install). A resolved SETEC must
    additionally carry the R2 dispatcher (`setec_run.py`) AND its real
    `build_error_output` builder for the real-envelope test to mean anything;
    if either is missing the SETEC predates this contract and we skip."""
    try:
        loc = setec_discovery.discover_setec()
    except setec_discovery.SetecDiscoveryError:
        return None
    if not (loc.scripts_dir / setec_runner.DISPATCHER_SCRIPT).is_file():
        return None
    output_schema = loc.scripts_dir / "output_schema.py"
    if not output_schema.is_file():
        return None
    if "def build_error_output" not in output_schema.read_text(encoding="utf-8"):
        return None
    return loc


# --------------------------------------------------------------------------
# T1 — floor resolution from the vendored manifest (offline).
# --------------------------------------------------------------------------
def t1_floor_resolution_from_vendored_manifest() -> None:
    print("T1: floor resolution from vendored manifest (offline)")
    payload = json.loads(VENDORED_MANIFEST.read_text(encoding="utf-8"))
    manifest = setec_capabilities.parse_manifest_payload(payload, location=_Loc())

    # Every shim surface resolves to a floor, and the known floors match.
    shim_surfaces = discover_shim_surfaces(SHIM_DIR)
    check(len(shim_surfaces) == 10, f"10 shim surfaces discovered (got {len(shim_surfaces)})")
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
        "argument_decision_audit": "1.116.0",
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
        version=(1, 114, 0),
        version_str="1.114.0",
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
            version=(1, 114, 0), version_str="1.114.0", source="env",
        )
        raised = False
        try:
            setec_runner.run_supplement("variance_audit", ["x.md"], location=loc)
        except setec_discovery.SetecDiscoveryError as exc:
            raised = setec_runner.DISPATCHER_SCRIPT in str(exc)
        check(raised, "pre-R2 SETEC (no setec_run.py) raises a clean upgrade error")


# --------------------------------------------------------------------------
# T2b — R3 structured-error tiering, driven by the REAL SETEC dispatcher.
#
# SHOULD-FIX (review follow-up): this test used to HAND-ROLL the R3 error
# envelope, so if SETEC's build_error_output drifted (dropped/renamed a key)
# the test stayed green while production broke. It now drives the REAL
# dispatcher (setec_run.py) to PRODUCE the error envelopes — no hand-rolled
# JSON — and asserts the consumer's run_supplement parse path turns the REAL
# envelope into a blocking SupplementResult with the right reason_category.
# When SETEC is absent (offline CI) it SKIPS cleanly, exactly as the drift
# gate's CHECK 2 skips.
#
# Two REAL error categories are drivable from a real SETEC offline (no heavy
# deps, deterministic):
#   * bad_input    — an unknown surface; the dispatcher fails surface
#                    resolution and emits build_error_output(bad_input) BEFORE
#                    running any script. Driven via the REAL subprocess path
#                    run_supplement uses (run_setec_script -> setec_run.py).
#   * version_floor — a known surface whose manifest floor exceeds the running
#                    SETEC version. The running version is fixed at the
#                    plugin's plugin.json, so we drive the REAL dispatcher
#                    in-process (setec_run.dispatch with an injected low
#                    observed_version) to FORCE the below-floor case, capture
#                    the REAL envelope it emits, and route those REAL bytes
#                    through the consumer's run_supplement parse path. The
#                    envelope (incl. the machine-readable version_floor pair)
#                    is build_error_output's real output, not hand-rolled.
# --------------------------------------------------------------------------
def _import_real_setec(loc: "setec_discovery.SetecLocation"):
    """Import the REAL SETEC dispatcher + capabilities from the resolved
    checkout's scripts dir. Returns (setec_run_module, capabilities_module).
    Heavy deps are not touched (the bad_input / version_floor paths fail
    before any audit script runs)."""
    scripts = str(loc.scripts_dir)
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import importlib

    real_setec_run = importlib.import_module("setec_run")
    real_capabilities = importlib.import_module("capabilities")
    return real_setec_run, real_capabilities


def t2b_r3_error_tiering() -> None:
    print("T2b: R3 reason_category -> tier mapping (REAL dispatcher envelopes)")
    loc = _resolve_real_setec()
    if loc is None:
        note_skip(
            "SETEC not resolvable (set SETEC_VOICEPRINT_DIR to a SETEC "
            "checkout carrying setec_run.py + build_error_output to drive the "
            "real-dispatcher error path); mirrors the drift gate CHECK 2 skip."
        )
        return

    # --- bad_input: the REAL dispatcher subprocess, end to end -------------
    # An unknown surface drives the real dispatcher's surface-resolution
    # failure -> build_error_output(bad_input). This is the exact subprocess
    # path run_supplement uses in production (run_setec_script -> setec_run.py).
    result = setec_runner.run_supplement(
        "no_such_surface_contract_test", [], location=loc
    )
    check(result.available is False, "bad_input (real): available is False")
    check(
        result.reason_category == "bad_input",
        f"bad_input (real): reason_category parsed (got {result.reason_category!r})",
    )
    check(
        bool(result.blocking_warnings) and not result.reliability_warnings,
        "bad_input (real): tiered BLOCKING (reason in blocking_warnings)",
    )
    check(
        bool(result.reason) and "unknown surface" in (result.reason or ""),
        "bad_input (real): structured reason from build_error_output preserved",
    )
    # The REAL envelope conforms to the schema_version 1.0 error shape the
    # consumer pins (build_error_output's output, not hand-rolled). If
    # build_error_output drops/renames a required key, _coerce_envelope in
    # run_supplement would have raised before we got here.
    check(
        result.envelope.get("schema_version") == "1.0",
        "bad_input (real): envelope is schema_version 1.0",
    )

    # --- version_floor: the REAL dispatcher, forced below floor ------------
    real_setec_run, real_capabilities = _import_real_setec(loc)
    manifest = real_capabilities.load_manifest()
    # narrative_decision_audit floors at 1.107.0 in SETEC's manifest; force the
    # running version below it. dispatch() emits the REAL version_floor
    # envelope (build_error_output) to stdout; capture it.
    import io
    import contextlib

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = real_setec_run.dispatch(
            "narrative_decision_audit",
            ["x.md"],
            manifest=manifest,
            observed_version="1.0.0",
        )
    real_envelope_bytes = buf.getvalue()
    check(
        rc == real_setec_run.EXIT_DISCOVERY,
        f"version_floor (real): dispatch exits discovery code (got {rc})",
    )
    parsed = json.loads(real_envelope_bytes)
    check(
        parsed.get("reason_category") == "version_floor",
        "version_floor (real): real dispatcher emitted reason_category "
        "version_floor",
    )
    # Route the REAL envelope bytes through the consumer's run_supplement parse
    # path via a stand-in dispatcher that re-emits them verbatim (the dispatcher
    # already produced the real envelope; this exercises the consumer parse +
    # tiering on real bytes).
    body = (
        "#!/usr/bin/env python3\n"
        "import sys\n"
        f"sys.stdout.write({real_envelope_bytes!r})\n"
    )
    with _fake_dispatcher_dir(body) as tmp:
        result = setec_runner.run_supplement(
            "narrative_decision_audit", ["x.md"], location=_loc(tmp)
        )
    check(result.available is False, "version_floor (real): available is False")
    check(
        result.reason_category == "version_floor",
        "version_floor (real): consumer parsed reason_category",
    )
    check(
        bool(result.blocking_warnings) and not result.reliability_warnings,
        "version_floor (real): tiered BLOCKING",
    )
    # The machine-readable floor/observed pair from build_error_output's extra
    # survives the round trip (the consumer never re-derives it from prose).
    check(
        result.envelope.get("version_floor")
        == {"required": "1.107.0", "observed": "1.0.0"},
        "version_floor (real): machine-readable {required, observed} pair "
        "preserved",
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
            json.dumps({"name": "setec-voiceprint", "version": "1.114.0"}),
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
        check(loc.version == (1, 114, 0), "synthetic SETEC root discovered at 1.114.0")


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


# --------------------------------------------------------------------------
# T8 — run_surface_cli preserves the dispatcher's exit code (no re-derivation).
# --------------------------------------------------------------------------
def t8_run_surface_cli_preserves_dispatcher_exit_code() -> None:
    print("T8: run_surface_cli preserves the dispatcher's exit code")
    import contextlib
    import io

    def _err_result(returncode: int):
        env = {
            "schema_version": "1.0", "available": False,
            "reason_category": "bad_input", "reason": "unrecognized --bogus",
        }
        return setec_runner.SupplementResult(
            schema_version="1.0", task_surface=None, tool="idiolect_detector",
            version="1.114.0", available=False, target={}, baseline=None,
            results={}, claim_license=None, claim_license_rendered=None,
            reason="unrecognized --bogus", reason_category="bad_input",
            envelope=env, returncode=returncode,
        )

    orig = setec_runner.run_supplement
    try:
        # SAME reason_category (bad_input), DIFFERENT dispatcher exit codes: a
        # known-surface contract failure is 3, an unknown-surface discovery
        # failure is 2. run_surface_cli must preserve each — a category->code
        # map cannot, since both are `bad_input`.
        setec_runner.run_supplement = lambda surface, argv: _err_result(3)
        with contextlib.redirect_stdout(io.StringIO()):
            rc3 = setec_runner.run_surface_cli("idiolect_detector", ["--bogus"])
        check(rc3 == 3, f"known-surface bad_input preserves dispatcher exit 3 (got {rc3})")

        setec_runner.run_supplement = lambda surface, argv: _err_result(2)
        with contextlib.redirect_stdout(io.StringIO()):
            rc2 = setec_runner.run_surface_cli("nope", [])
        check(rc2 == 2, f"unknown-surface bad_input preserves dispatcher exit 2 (got {rc2})")
    finally:
        setec_runner.run_supplement = orig


# --------------------------------------------------------------------------
# T9 — voice_profile CONSUME-side contract: families.<fam>.top_features (and
#      most_stable_features) carry the {feature, mean, sd, cv} shape that
#      in-flight apodictic capabilities are specced to glob.
#
# Scope note (a consumer has landed): as of this commit the Interpretable
# Stylometric Explanation capability (scripts/style_explanation.py +
# apodictic.style_label.v1) is the first shipped consume-side reference to the
# top_features / most_stable_features shape — its `feature_ref` provenance binds
# a descriptive style label to families.<fam>.top_features[].{feature, mean, sd,
# cv}. (The M1 validator checks `feature_ref` presence/non-emptiness, not its
# resolvability — it does not re-read the SETEC envelope at runtime — but the
# capability's schema/docs/fixture cite this shape as their consume contract, so
# it is no longer a purely forward-looking reference.) The older voice_profile
# consumer (skills/specialized-audits/scripts/ai_prose_voice_profile.py) remains
# a pure pass-through that forwards argv to the SETEC dispatcher and never parses
# the envelope. This gate pins the field shape so that a SETEC drop of these
# arrays fails HERE, in per-PR CI, rather than reaching the capability's specced
# consume contract silently.
#
# Why this is its own OFFLINE gate (reads only the vendored fixture, no SETEC):
# the drift gate's CHECK 2 (sync_setec.cmd_check) is a whole-file byte compare
# of the vendored fixture against SETEC's own contract_fixtures/ copy — it
# (a) SKIPS entirely offline (per-PR CI never runs it; only the weekly sync
# workflow does) and (b) only asserts "vendored == SETEC's copy", never that
# top_features EXISTS. So if SETEC ever drops/renames top_features, sync_setec
# re-vendors the smaller fixture, cmd_check passes (they match again), and the
# breakage would reach the specced consumers SILENTLY once they ship. Pinning
# the field here surfaces such a drop HERE, in per-PR CI, instead of at runtime
# in a future capability. most_stable_features is the other specced consume
# field — pin BOTH so neither can vanish unnoticed.
# --------------------------------------------------------------------------
def t9_voice_profile_consume_contract() -> None:
    print("T9: voice_profile families.<fam>.{top_features,most_stable_features} "
          "consume-side shape (offline)")
    fixture = VENDORED_FIXTURES / "voice_profile.json"
    check(fixture.is_file(), "voice_profile.json fixture present")
    if not fixture.is_file():
        return
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    families = payload.get("results", {}).get("families")
    check(
        isinstance(families, dict) and len(families) > 0,
        "voice_profile results.families is a non-empty object",
    )
    if not (isinstance(families, dict) and families):
        return

    required_keys = {"feature", "mean", "sd", "cv"}
    for fam, body in sorted(families.items()):
        for array_name in ("top_features", "most_stable_features"):
            arr = body.get(array_name) if isinstance(body, dict) else None
            check(
                isinstance(arr, list) and len(arr) > 0,
                f"families.{fam}.{array_name} is a non-empty array "
                f"(the specced consume-side contract; a SETEC drop must fail "
                f"here, not silently break the in-flight consumers once they "
                f"ship)",
            )
            if not (isinstance(arr, list) and arr):
                continue
            item = arr[0]
            has_keys = isinstance(item, dict) and required_keys <= set(item)
            check(
                has_keys,
                f"families.{fam}.{array_name}[] carries {{feature, mean, sd, cv}} "
                f"(got {sorted(item) if isinstance(item, dict) else type(item).__name__})",
            )
            if has_keys:
                typed = (
                    isinstance(item["feature"], str)
                    and all(
                        isinstance(item[k], (int, float))
                        and not isinstance(item[k], bool)
                        for k in ("mean", "sd", "cv")
                    )
                )
                check(
                    typed,
                    f"families.{fam}.{array_name}[] typed "
                    f"(feature:str, mean/sd/cv:number)",
                )


# --------------------------------------------------------------------------
# T9b — doc-truth guard for T9's rationale. T9 now pins a PRESENT-TENSE contract:
# the Interpretable Stylometric Explanation capability (style_explanation.py +
# apodictic.style_label.v1) is the first shipped consume-side reference to
# top_features / most_stable_features (its `feature_ref` provenance cites the
# families.<fam>.top_features shape). A prior draft of T9 over-claimed in the
# OTHER direction — asserting as fact that capabilities "actually consume" /
# "glob" these arrays and that a SETEC drop would "silently break consumers" when
# no consumer yet existed. This guard fails if (a) that retired overclaim phrasing
# reappears in the T9 block, or (b) a consumer of these arrays appears that is NOT
# the documented Interpretable-Stylometric-Explanation capability — i.e. an
# UNEXPECTED consumer lands WITHOUT the T9 wording being updated to name it. Either
# way the rationale must stay congruent with the repo.
# --------------------------------------------------------------------------
def t9b_consume_claim_matches_repo() -> None:
    print("T9b: T9 rationale matches the repo (no overclaimed current consumer)")
    src = Path(__file__).resolve().read_text(encoding="utf-8")

    # (a) The retired present-tense overclaim phrasing must not reappear in the
    #     T9 block. Scan ONLY the T9 region (from its header up to T9b's header)
    #     so this guard does not match the example phrases quoted in its own
    #     docstring/assertions below. Phrases are split so the literal full
    #     string never appears in this function's source either.
    start = src.find("# T9 —")
    end = src.find("# T9b —")
    t9_block = src[start:end] if (start != -1 and end != -1 and end > start) else src
    # Normalize whitespace (incl. comment-continuation '# ' / f-string wraps) so
    # an overclaim split across lines is still caught.
    t9_norm = " ".join(t9_block.replace("#", " ").split())
    overclaims = (
        "apodictic " + "actually consumes",
        "every consumer " + "that globs",
        "capabilities " + "glob.",
        "silently " + "break consumers)",
    )
    for phrase in overclaims:
        check(
            phrase not in t9_norm,
            f"T9 must not reassert the refuted present-tense consumer claim "
            f"({phrase!r})",
        )

    # (b) Ground truth: is there a non-test consumer of these arrays OTHER than the
    #     documented Interpretable-Stylometric-Explanation capability? That
    #     capability is the expected, named consumer (T9's present-tense rationale
    #     above); any OTHER consumer landing without the wording being updated to
    #     name it is what this guard forces an update for.
    try:
        out = subprocess.run(
            ["git", "grep", "-nE", "top_features|most_stable_features"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        _SKIPS.append("T9b: git grep unavailable for consumer cross-check")
        return
    if out.returncode not in (0, 1):
        _SKIPS.append("T9b: git grep returned a non-match error; consumer "
                      "cross-check skipped")
        return
    # Files belonging to the documented Interpretable-Stylometric-Explanation
    # capability — its `feature_ref` provenance is the EXPECTED consume-side
    # reference T9's present-tense rationale now names. Matched by path so a stray
    # new consumer elsewhere still trips the guard.
    expected_paths = (
        "style_explanation.py",
        "apodictic.style_label.v1.schema.json",
        "interpretable-stylometric-explanation.md",
        "example-author-style-explanation.md",
        # The changelog's assembled entry for that capability quotes the
        # families.<fam>.top_features shape it consumes. A release note is
        # documentation of the EXPECTED capability, not a new code consumer —
        # exclude it like the reference module above (else every release that
        # carries this entry trips the guard).
        "changelog.md",
    )
    consumers = [
        line for line in out.stdout.splitlines()
        if line
        and "tests/setec-contract/" not in line.split(":", 1)[0]
        and not any(p in line.split(":", 1)[0] for p in expected_paths)
    ]
    check(
        not consumers,
        "the only shipped consume-side references to "
        "top_features/most_stable_features are the documented "
        "Interpretable-Stylometric-Explanation capability, so T9's present-tense "
        "wording is accurate; an UNEXPECTED consumer landed "
        f"({consumers!r}) — name it in the T9 rationale",
    )


def main() -> int:
    for fn in (
        t1_floor_resolution_from_vendored_manifest,
        t2_vendored_golden_through_runner,
        t2b_r3_error_tiering,
        t3_discovery_still_works_without_hardcoded_floors,
        t4_below_surface_floor_fails_with_surface_floor,
        t5_drift_gate_self_test,
        t6_required_groups_validation,
        t7_idiolect_help_bypasses_required_groups,
        t8_run_surface_cli_preserves_dispatcher_exit_code,
        t9_voice_profile_consume_contract,
        t9b_consume_claim_matches_repo,
    ):
        fn()
        setec_capabilities.clear_cache()
    print()
    if _FAILURES:
        print(f"test_setec_contract: FAIL ({len(_FAILURES)} assertion(s))", file=sys.stderr)
        for f in _FAILURES:
            print(f"  - {f}", file=sys.stderr)
        return 1
    if _SKIPS:
        print(f"test_setec_contract: PASS ({len(_SKIPS)} skip(s))")
        for s in _SKIPS:
            print(f"  - SKIPPED: {s}")
    else:
        print("test_setec_contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
