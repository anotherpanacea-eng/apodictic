#!/usr/bin/env python3
"""
setec_runner.py — pass-side helper for SETEC subprocess supplementation.

Wraps the common "discover SETEC, invoke the normalized dispatcher, parse
the schema_version 1.0 envelope, classify warnings / structured errors,
return a structured result" plumbing. APODICTIC passes that bolster their
analysis with SETEC measurements (Pass 3 Rhythm/Modulation, Pass 7
POV/Voice, the AI-Prose Calibration audit, idiolect preservation, etc.)
call into this module rather than reimplementing the flow.

R2/R3 adoption (Increment 4). Every surface now routes through SETEC's
normalized dispatcher, ``setec_run.py <surface> [args] --json`` (R2): the
dispatcher resolves the surface from its capabilities manifest, enforces
the per-surface version floor + dependencies, runs the underlying script,
and **guarantees a schema_version 1.0 envelope reaches stdout for EVERY
surface** — including ``pov_voice_profile``, whose file artifact the
dispatcher projects to stdout. The consumer never touches ``--json-out``,
never allocates an ``ai-prose-baselines-private/`` tempdir, and never
scrapes stderr. A failed/blocked run is the SAME envelope with
``available: false`` plus ``reason`` + ``reason_category`` (R3); the runner
branches on ``reason_category`` to assign a tier.

The dispatcher is the SINGLE RUNTIME AUTHORITY for floor/dependency
failures (it returns R3 ``version_floor`` / ``missing_dependency``). The
consumer-side ``setec_capabilities.resolve_floor`` + the vendored manifest
are retained for the offline drift gate and capability introspection
(Increment 2's contract role), NOT as a redundant runtime pre-check that
could drift from the dispatcher.

See docs/pass3-pass7-setec-supplement-spec.md §6.6 for the design and
§6.4 for the three-tier warnings classification; the R3 ``reason_category``
-> tier mapping extends §6.4 to structured errors.

Usage (caller builds the SETEC surface arg list; the runner routes through
the dispatcher and handles the envelope):

    from setec_runner import run_supplement

    result = run_supplement(
        "variance_audit",
        ["draft.md", "--baseline-dir", "/path/to/baseline", "--no-tier3"],
    )

    if not result.available:
        # SETEC ran but couldn't produce a measurement (R3). The reason and
        # reason_category say why; blocking_warnings carries the explanation.
        print("SETEC N/A:", result.reason_category, result.reason)
        return

    print(result.results["tier1"]["sentence_length"]["burstiness_B"])
    for w in result.reliability_warnings:
        # Render these inline near the cited measurement
        ...

--------------------------------------------------------------------------
C3 thin-wrapper note (fleet-coordination/specs/setec-consumer-client-
contract.md): the envelope-tiering MECHANISM (the three-tier warning
classifier + its permanent-fail-upward default, the R3 reason_category ->
tier map, the ``SupplementResult``/``SetecRunnerError`` shapes, and the
dispatcher-invocation plumbing itself) now lives in the runtime vendored
shared client, `_vendored_setec_client.py`, and is imported here rather
than re-implemented — ``run_supplement`` is a thin delegation to the
vendored ``run_dispatcher``. What stays LOCAL is APODICTIC's own policy:
the default-location-via-``discover_setec`` convenience on ``run_supplement``,
and the CLI glue (``run_surface_cli`` / ``_cli_main``). See
tests/setec-contract/setec-client-symbol-inventory.json for the full
shared vs. apodictic_policy classification.
--------------------------------------------------------------------------
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setec_discovery import (  # noqa: E402
    SetecDiscoveryError,
    SetecLocation,
    discover_setec,
)
from _vendored_setec_client import (  # noqa: E402
    DISPATCHER_SCRIPT,
    EXPECTED_SCHEMA_VERSION,
    KNOWN_REASON_CATEGORIES,
    REASON_CATEGORY_BAD_INPUT,
    REASON_CATEGORY_INTERNAL_ERROR,
    REASON_CATEGORY_MISSING_DEPENDENCY,
    REASON_CATEGORY_POLICY_REFUSED,
    REASON_CATEGORY_TEXT_TOO_SHORT,
    REASON_CATEGORY_VERSION_FLOOR,
    RELIABILITY_PATTERNS,
    SetecRunnerError,
    SupplementResult,
    classify_warning,
    run_dispatcher,
)


def run_supplement(
    surface: str,
    args: list[str],
    *,
    location: SetecLocation | None = None,
) -> SupplementResult:
    """Run a SETEC SURFACE through the normalized dispatcher and return a
    SupplementResult.

    Invokes ``setec_run.py <surface> [args] --json`` (R2) via the vendored
    shared client's ``run_dispatcher`` and parses the schema_version 1.0
    envelope from STDOUT — for ALL surfaces, including ``pov_voice_profile``
    (the dispatcher projects its file artifact to stdout, so the consumer
    never touches ``--json-out``). There is ONE delivery path.

    ``surface`` is the normalized surface NAME (e.g. ``"variance_audit"``,
    ``"pov_voice_profile"``), NOT a script filename. The dispatcher resolves
    the surface to its script from SETEC's capabilities manifest.

    Floor / dependency enforcement is the DISPATCHER's job (R3): an
    out-of-floor or missing-dependency run comes back as an envelope with
    ``available: false`` + ``reason_category`` in {``version_floor``,
    ``missing_dependency``, ...}, which ``run_dispatcher`` parses and tiers
    (three-tier classification for SUCCESS warnings; the R3 reason_category
    -> tier map for ERROR envelopes — both in the vendored shared client).
    The consumer does NOT pre-check the floor with ``resolve_floor`` here —
    that would double-enforce and could drift from the dispatcher.
    ``resolve_floor`` + the vendored manifest remain for the offline drift
    gate and capability introspection (Increment 2's contract role).

    THE ONE APODICTIC-SPECIFIC POLICY HERE (why this function still exists
    rather than callers using ``run_dispatcher`` directly): ``location``
    defaults to this repo's own ``discover_setec()`` (env var + marketplace
    resolver order) when not supplied.

    Raises ``SetecDiscoveryError`` if SETEC cannot be located, fails the
    BOOTSTRAP version-floor check, or is too old to carry the dispatcher
    (``setec_run.py`` absent — surfaced as a clean upgrade message, not a
    crash). Callers handle this as the blocking tier per spec §6.4.

    Raises ``SetecRunnerError`` if the dispatcher ran but produced output
    that does not conform to schema_version 1.0 (defense-in-depth; should not
    happen at the supported SETEC version floor).
    """
    if location is None:
        location = discover_setec()
    return run_dispatcher(surface, args, location=location)


def run_surface_cli(surface: str, argv: list[str]) -> int:
    """Thin CLI entry shared by the ``ai_prose_*.py`` surface shims.

    Routes ``surface`` through the dispatcher via ``run_supplement`` and emits
    the schema_version 1.0 envelope (success OR R3 error) to STDOUT, so a CLI
    caller / the LLM reading a shim's output always gets the same envelope the
    pass-side ``run_supplement`` parses. The exit code is the DISPATCHER's own
    (``result.returncode``), preserved rather than re-derived from
    reason_category — only the dispatcher can tell a known-surface contract
    failure (3) from an unknown-surface discovery failure (2), since both carry
    reason_category ``bad_input``. The dispatcher's contract:

      * 0  — available=True success envelope on stdout.
      * 2  — discovery / version-floor failure (unknown surface, too-old SETEC).
      * 3  — contract / usage failure (bad input on a known surface, missing
             dependency, text too short, policy refusal).
      * 1  — internal error.

    The envelope is still printed on the error exits (the dispatcher already
    put it on stdout), so a consumer never has to scrape stderr. Two failures
    happen BEFORE/AROUND the dispatcher and carry no envelope: a
    discovery/bootstrap failure (SETEC absent or too old) prints the upgrade
    message to stderr and exits 2; an unparseable dispatcher envelope
    (``SetecRunnerError``) exits 3.
    """
    try:
        result = run_supplement(surface, argv)
    except SetecDiscoveryError as e:
        print(str(e), file=sys.stderr)
        return 2
    except SetecRunnerError as e:
        print(f"SETEC runner error: {e}", file=sys.stderr)
        return 3
    # Emit the parsed envelope verbatim (success or R3 error) to stdout.
    print(json.dumps(result.envelope, indent=2, default=str))
    if result.available:
        return 0
    # Preserve the dispatcher's own exit code (run_supplement captured the real
    # subprocess returncode) rather than re-deriving it from reason_category:
    # the dispatcher alone distinguishes a known-surface contract failure (3)
    # from an unknown-surface discovery failure (2) — both carry reason_category
    # `bad_input`, so a category->code map gets `bad_input` wrong. Matches
    # _cli_main, which already returns result.returncode.
    return result.returncode


def _cli_main() -> int:
    """`python setec_runner.py SURFACE [SURFACE_ARG ...]` — convenience CLI.

    Useful for debugging the runner from a shell. Routes the named SURFACE
    through the dispatcher, prints the classified warning buckets / R3 reason
    and a compact summary, then exits with the dispatcher's return code.
    """
    if len(sys.argv) < 2:
        print(
            "Usage: setec_runner.py SURFACE [SURFACE_ARG ...]\n"
            "Example: setec_runner.py variance_audit draft.md --no-tier2",
            file=sys.stderr,
        )
        return 2
    surface = sys.argv[1]
    args = sys.argv[2:]
    try:
        result = run_supplement(surface, args)
    except SetecDiscoveryError as e:
        print(str(e), file=sys.stderr)
        return 2
    except SetecRunnerError as e:
        print(f"SETEC runner error: {e}", file=sys.stderr)
        return 3
    summary = {
        "schema_version": result.schema_version,
        "tool": result.tool,
        "version": result.version,
        "task_surface": result.task_surface,
        "available": result.available,
        "reason_category": result.reason_category,
        "reason": result.reason,
        "target": result.target,
        "baseline_present": result.baseline is not None,
        "blocking_warnings": result.blocking_warnings,
        "reliability_warnings": result.reliability_warnings,
        "cosmetic_warnings": result.cosmetic_warnings,
        "results_top_keys": sorted((result.results or {}).keys()),
    }
    print(json.dumps(summary, indent=2, default=str))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(_cli_main())
