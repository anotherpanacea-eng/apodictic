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
-> tier mapping below extends §6.4 to structured errors.

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
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setec_discovery import (  # noqa: E402
    SetecDiscoveryError,
    SetecLocation,
    discover_setec,
    run_setec_script,
)


EXPECTED_SCHEMA_VERSION = "1.0"

# The normalized dispatcher SETEC exposes (R2). All surfaces route through
# it; it guarantees a stdout envelope and owns floor/dep enforcement (R3).
DISPATCHER_SCRIPT = "setec_run.py"

# R3 reason_category enum (mirrors SETEC's output_schema.REASON_CATEGORIES).
# Pinned here so the consumer's tier mapping is exhaustive and a new producer
# category fails loudly (defaulting to blocking) rather than silently slipping
# into the cosmetic tier.
REASON_CATEGORY_VERSION_FLOOR = "version_floor"
REASON_CATEGORY_MISSING_DEPENDENCY = "missing_dependency"
REASON_CATEGORY_BAD_INPUT = "bad_input"
REASON_CATEGORY_TEXT_TOO_SHORT = "text_too_short"
REASON_CATEGORY_POLICY_REFUSED = "policy_refused"
REASON_CATEGORY_INTERNAL_ERROR = "internal_error"

KNOWN_REASON_CATEGORIES = frozenset({
    REASON_CATEGORY_VERSION_FLOOR,
    REASON_CATEGORY_MISSING_DEPENDENCY,
    REASON_CATEGORY_BAD_INPUT,
    REASON_CATEGORY_TEXT_TOO_SHORT,
    REASON_CATEGORY_POLICY_REFUSED,
    REASON_CATEGORY_INTERNAL_ERROR,
})

# R3 reason_category -> tier (spec §6.4, extended for structured errors).
#
#   * version_floor / missing_dependency -> BLOCKING. The surface cannot run
#     against this SETEC; surface the upgrade/install message (the dispatcher
#     puts BOTH the required floor and observed version into `reason`, and a
#     machine-readable pair into the envelope's `version_floor` /
#     `missing_dependency` extra key). The pass falls back to LLM-only and
#     records the gap — never an LLM estimate of the computation.
#   * text_too_short -> RELIABILITY. The input was below the surface's length
#     floor; this is the same reliability-vs-blocking semantics §6.4 already
#     applies to a too-short SUCCESS envelope, now arriving as a structured
#     error. The measurement is unavailable, but the gap is about THIS input's
#     length (a noisy/absent signal), not a missing capability — so it renders
#     as a reliability caveat, not a hard "SETEC N/A" block.
#   * policy_refused / bad_input / internal_error -> BLOCKING with the reason
#     text. A privacy/policy guard refused, the args were malformed / the
#     surface unknown, or the run failed unexpectedly (incl. an out-of-bounds
#     computed value caught by SETEC's R4 gate). None of these yield a usable
#     measurement; block and carry the human reason.
#
# An UNKNOWN category (a producer added one the consumer hasn't mapped)
# defaults to BLOCKING — fail safe, never silently downgrade an error.
_REASON_CATEGORY_TIER: dict[str, str] = {
    REASON_CATEGORY_VERSION_FLOOR: "blocking",
    REASON_CATEGORY_MISSING_DEPENDENCY: "blocking",
    REASON_CATEGORY_TEXT_TOO_SHORT: "reliability",
    REASON_CATEGORY_POLICY_REFUSED: "blocking",
    REASON_CATEGORY_BAD_INPUT: "blocking",
    REASON_CATEGORY_INTERNAL_ERROR: "blocking",
}


# Three-tier warnings classification per spec §6.4 (for SUCCESS envelopes).
# Patterns are matched case-insensitively against each warning string. The
# list is expected to grow as new SETEC scripts surface new warning shapes;
# unmatched warnings on an available=True envelope default to "cosmetic" tier
# (silent in pass output, available on drill-in).
RELIABILITY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"text too short", re.IGNORECASE),
    re.compile(r"text length .* below", re.IGNORECASE),
    re.compile(r"below (?:the )?recommended (?:length |word )?threshold", re.IGNORECASE),
    re.compile(r"signal .* noisy", re.IGNORECASE),
    re.compile(r"signals? skipped", re.IGNORECASE),
    re.compile(r"tier \d+ (?:skipped|fell back|unavailable)", re.IGNORECASE),
    re.compile(r"(?:spacy|sentence-transformers|sklearn|transformers|torch) (?:not |un)available", re.IGNORECASE),
    re.compile(r"fell back to (?:tf-?idf|heuristic)", re.IGNORECASE),
    re.compile(r"insufficient (?:sentences|tokens|words)", re.IGNORECASE),
    re.compile(r"baseline (?:too small|insufficient)", re.IGNORECASE),
    re.compile(r"(?:dependency|dep) missing", re.IGNORECASE),
)


class SetecRunnerError(RuntimeError):
    """Raised when SETEC runs but the envelope is unparseable or invalid.

    Discovery and bootstrap-floor errors propagate as SetecDiscoveryError
    from the underlying setec_discovery module (e.g. SETEC absent, or too
    old to carry the R2 dispatcher) — callers should catch both. PER-SURFACE
    floor/dependency failures are NOT raised here: the dispatcher returns
    them as R3 error envelopes (available=False + reason_category), which the
    runner parses and tiers. See spec §6.4 (blocking tier) for the
    recommended pass-side handling when SETEC cannot supply measurements.
    """


@dataclass
class SupplementResult:
    """Structured result of one SETEC surface invocation.

    The pass reads the fields it needs, renders reliability warnings
    inline next to measurements, and respects claim_license bounds
    when stating findings. On an R3 error envelope (available=False),
    `reason` / `reason_category` carry the structured explanation and the
    relevant warning bucket carries the human text.
    """

    schema_version: str
    task_surface: str | None
    tool: str
    version: str
    available: bool
    target: dict[str, Any]
    baseline: dict[str, Any] | None
    results: dict[str, Any]
    claim_license: dict[str, Any] | None
    claim_license_rendered: str | None
    blocking_warnings: list[str] = field(default_factory=list)
    reliability_warnings: list[str] = field(default_factory=list)
    cosmetic_warnings: list[str] = field(default_factory=list)
    ai_status: str | None = None
    # R3 structured-error fields (present only on available=False envelopes).
    reason: str | None = None
    reason_category: str | None = None
    envelope: dict[str, Any] = field(default_factory=dict)
    returncode: int = 0


def classify_warning(warning: str) -> str:
    """Return 'reliability' if the warning matches a known reliability
    pattern, else 'cosmetic'. Blocking classification is decided by
    the envelope's `available` flag / `reason_category`, not by warning
    text on a SUCCESS envelope."""
    for pattern in RELIABILITY_PATTERNS:
        if pattern.search(warning):
            return "reliability"
    return "cosmetic"


def _tier_for_reason_category(reason_category: str | None) -> str:
    """Map an R3 `reason_category` to a tier ('blocking' / 'reliability').
    An absent or UNKNOWN category fails safe to 'blocking' — an error is never
    silently downgraded to a softer tier."""
    if not reason_category:
        return "blocking"
    return _REASON_CATEGORY_TIER.get(reason_category, "blocking")


def _classify_warnings(
    warnings: list[str], available: bool
) -> tuple[list[str], list[str], list[str]]:
    """Return (blocking, reliability, cosmetic) for a SUCCESS (available=True)
    envelope's warnings. For an error envelope the tiering is driven by
    `reason_category` in `run_supplement`, not by this helper, so callers pass
    only success-envelope warnings here."""
    reliability: list[str] = []
    cosmetic: list[str] = []
    for w in warnings:
        if classify_warning(w) == "reliability":
            reliability.append(w)
        else:
            cosmetic.append(w)
    return [], reliability, cosmetic


def _coerce_envelope(envelope: dict[str, Any]) -> None:
    """Validate the minimum required keys of schema_version 1.0. Raises
    SetecRunnerError on malformed envelopes (defense-in-depth; the dispatcher
    + bootstrap floor should prevent this in practice).

    The R3 additive keys (`reason` / `reason_category`) are present only on
    error envelopes, so they are NOT required here — the 12-key success
    contract is the floor for both shapes."""
    sv = envelope.get("schema_version")
    if sv != EXPECTED_SCHEMA_VERSION:
        raise SetecRunnerError(
            f"SETEC envelope schema_version={sv!r}, expected "
            f"{EXPECTED_SCHEMA_VERSION!r}. The dispatcher's bootstrap floor "
            f"should prevent this; check that the discovered SETEC is recent "
            f"enough."
        )
    required = ("task_surface", "tool", "version", "available", "target",
                "baseline", "results", "claim_license",
                "claim_license_rendered", "warnings")
    missing = [k for k in required if k not in envelope]
    if missing:
        raise SetecRunnerError(
            f"SETEC envelope missing required keys: {missing!r}. "
            f"Envelope keys present: {sorted(envelope.keys())!r}"
        )


def run_supplement(
    surface: str,
    args: list[str],
    *,
    location: SetecLocation | None = None,
) -> SupplementResult:
    """Run a SETEC SURFACE through the normalized dispatcher and return a
    SupplementResult.

    Invokes ``setec_run.py <surface> [args] --json`` (R2) via
    ``run_setec_script`` and parses the schema_version 1.0 envelope from
    STDOUT — for ALL surfaces, including ``pov_voice_profile`` (the
    dispatcher projects its file artifact to stdout, so the consumer never
    touches ``--json-out``). There is ONE delivery path.

    ``surface`` is the normalized surface NAME (e.g. ``"variance_audit"``,
    ``"pov_voice_profile"``), NOT a script filename. The dispatcher resolves
    the surface to its script from SETEC's capabilities manifest.

    Floor / dependency enforcement is the DISPATCHER's job (R3): an
    out-of-floor or missing-dependency run comes back as an envelope with
    ``available: false`` + ``reason_category`` ∈ {``version_floor``,
    ``missing_dependency``, ...}, which this function parses and tiers (see
    the module-level mapping). The consumer does NOT pre-check the floor with
    ``resolve_floor`` here — that would double-enforce and could drift from
    the dispatcher. ``resolve_floor`` + the vendored manifest remain for the
    offline drift gate and capability introspection (Increment 2's contract
    role).

    On a SUCCESS envelope (available=True), the ``warnings`` array is
    classified per spec §6.4 into reliability / cosmetic (blocking is empty —
    a success has no blocking warning). On an ERROR envelope (available=False),
    the structured ``reason`` / ``reason_category`` drive the tier: a
    ``text_too_short`` error renders as reliability (the §6.4
    reliability-vs-blocking semantics, arriving as a structured error);
    everything else (version_floor / missing_dependency / policy_refused /
    bad_input / internal_error, and any unknown category) is blocking, with
    the reason text in ``blocking_warnings``.

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

    # Bootstrap/dispatcher floor: routing through the normalized entrypoint
    # requires a SETEC carrying setec_run.py (the R2 dispatcher). If it is
    # absent (a pre-R2 SETEC that still satisfies the discovery bootstrap
    # floor), fail cleanly with an upgrade message rather than letting
    # run_setec_script raise a bare "script not found".
    # FINALIZATION: when SETEC cuts the real R2 release (target ~1.114), raise
    # setec_discovery.BOOTSTRAP_SETEC_VERSION to that release so this absence
    # check becomes belt-and-suspenders rather than the primary R2 gate.
    if not (location.scripts_dir / DISPATCHER_SCRIPT).is_file():
        raise SetecDiscoveryError(
            f"SETEC at {location.plugin_root} (version {location.version_str}) "
            f"does not provide the normalized dispatcher "
            f"{DISPATCHER_SCRIPT!r}; it predates the R2 normalized entrypoint. "
            f"APODICTIC routes every SETEC surface through the dispatcher. "
            f"Upgrade SETEC to a release that ships {DISPATCHER_SCRIPT}."
        )

    # The dispatcher owns the single consumer flag (--json) and the surface
    # name leads the arg list: `setec_run.py <surface> [surface args] --json`.
    dispatcher_args = [surface, *args, "--json"]
    completed: subprocess.CompletedProcess = run_setec_script(
        DISPATCHER_SCRIPT,
        dispatcher_args,
        location=location,
        capture_output=True,
    )

    # The dispatcher ALWAYS emits exactly one envelope to stdout — success
    # (exit 0) OR an R3 error (exit 2/3/1). Empty stdout means the dispatcher
    # itself failed to run (not a contract failure it could envelope).
    if not completed.stdout.strip():
        raise SetecRunnerError(
            f"SETEC dispatcher produced no stdout for surface {surface!r} "
            f"(returncode={completed.returncode}). The dispatcher should emit "
            f"an envelope even on failure. Stderr (truncated): "
            f"{completed.stderr[:500]!r}"
        )
    try:
        envelope = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SetecRunnerError(
            f"SETEC dispatcher output for surface {surface!r} did not parse: "
            f"{exc}. First 500 chars: {completed.stdout[:500]!r}"
        ) from exc

    _coerce_envelope(envelope)
    available = bool(envelope["available"])
    warnings = list(envelope.get("warnings") or [])
    reason = envelope.get("reason")
    reason_category = envelope.get("reason_category")

    if available:
        # SUCCESS: classify warnings into reliability / cosmetic (§6.4).
        blocking, reliability, cosmetic = _classify_warnings(warnings, available)
    else:
        # R3 ERROR: tier by reason_category (NOT by stderr scraping). The
        # reason text becomes the user-facing warning in its tier; any
        # warnings the error envelope also carries are classified normally and
        # folded into the same buckets.
        tier = _tier_for_reason_category(reason_category)
        reason_msgs = [reason] if reason else []
        _b, reliability, cosmetic = _classify_warnings(warnings, available)
        if tier == "reliability":
            reliability = reason_msgs + reliability
            blocking = []
        else:
            blocking = reason_msgs

    return SupplementResult(
        schema_version=envelope["schema_version"],
        task_surface=envelope["task_surface"],
        tool=envelope["tool"],
        version=envelope["version"],
        available=available,
        target=envelope["target"],
        baseline=envelope.get("baseline"),
        results=envelope.get("results") or {},
        claim_license=envelope.get("claim_license"),
        claim_license_rendered=envelope.get("claim_license_rendered"),
        blocking_warnings=blocking,
        reliability_warnings=reliability,
        cosmetic_warnings=cosmetic,
        ai_status=envelope.get("ai_status"),
        reason=reason,
        reason_category=reason_category,
        envelope=envelope,
        returncode=completed.returncode,
    )


def run_surface_cli(surface: str, argv: list[str]) -> int:
    """Thin CLI entry shared by the ``ai_prose_*.py`` surface shims.

    Routes ``surface`` through the dispatcher via ``run_supplement`` and emits
    the schema_version 1.0 envelope (success OR R3 error) to STDOUT, so a CLI
    caller / the LLM reading a shim's output always gets the same envelope the
    pass-side ``run_supplement`` parses. Exit codes mirror the dispatcher's
    contract:

      * 0  — available=True success envelope on stdout.
      * 2  — discovery / bootstrap failure (SETEC absent, too old, or no
             dispatcher) printed to stderr; OR an R3 error envelope whose
             reason_category is a discovery/version failure
             (``version_floor`` / ``bad_input``).
      * 3  — runner/contract error (unparseable envelope), or an R3 error
             envelope whose reason_category is a contract/usage failure
             (``missing_dependency`` / ``text_too_short`` / ``policy_refused``).
      * 1  — an R3 ``internal_error`` envelope.

    The envelope is still printed on the error exits (the dispatcher already
    put it on stdout), so a consumer never has to scrape stderr. Discovery /
    bootstrap failures that never reach the dispatcher (no envelope) print the
    upgrade message to stderr and exit 2.
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
    # Map the R3 reason_category to the dispatcher's exit-code contract so a
    # shim's exit code matches what the dispatcher itself would have returned.
    return {
        REASON_CATEGORY_VERSION_FLOOR: 2,
        REASON_CATEGORY_BAD_INPUT: 2,
        REASON_CATEGORY_MISSING_DEPENDENCY: 3,
        REASON_CATEGORY_TEXT_TOO_SHORT: 3,
        REASON_CATEGORY_POLICY_REFUSED: 3,
        REASON_CATEGORY_INTERNAL_ERROR: 1,
    }.get(result.reason_category or "", 1)


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
