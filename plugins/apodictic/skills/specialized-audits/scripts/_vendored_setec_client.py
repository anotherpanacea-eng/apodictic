"""consumer_client.py — the ONE shared SETEC consumer client.

Producer-owned, stdlib-only. This module is the single source for the logic
that used to be duplicated across voicewright's four client modules
(``discovery.py`` / ``runner.py`` / ``surfaces.py`` / ``capabilities.py``)
and APODICTIC's three (``setec_discovery.py`` / ``setec_runner.py`` /
``setec_capabilities.py``): version parsing + precedence, the schema-1.0
envelope shape, the three-tier warning classifier, and the
discovery/subprocess-invocation plumbing.

Per `fleet-coordination/specs/setec-consumer-client-contract.md` C2.2, this
file is synced into each consumer repo as a vendored, byte-identical copy
(``sync_setec.py``'s ``_copy_client``) and pinned by SHA-256 in both the
manifest ``contract.client`` block and each consumer's lock file. Consumers
wrap it (C3): a thin per-repo module supplies the injected POLICY —
resolver order (env vars, marketplace search, sibling checkout), the
BOOTSTRAP version floor, and (voicewright only) the ``surfaces.py``
consumed-surface partition — none of which live here. This module never
reads an environment variable and never hardcodes a version floor.

Out of scope (per the build contract's hard law): no envelope/root-key
change, no warning-tier transfer, no claim-license edit, no sealed-evidence
hash migration. This module does not import ``output_schema`` or
``claim_license`` — it independently re-implements the SAME schema-1.0
common-key contract as a plain dict shape, exactly as both prior consumer
clients already did, so a consumer never needs the producer's Python
package importable at parse time.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

# ============================================================================
# 1. Version parsing + SemVer precedence (spec C1.1)
# ============================================================================
#
# A SemVer SUBSET grammar: 1-3 numeric release components (zero-padded to
# three), an optional dot-separated prerelease, an optional dot-separated
# build-metadata tag (ignored for precedence, per SemVer 10). A FOURTH release
# component, an empty string, a non-numeric release component, a leading-zero
# numeric component (release or prerelease), or a malformed prerelease/build
# identifier all raise VersionParseError — there is no silent partial parse.
# `references/contract_fixtures/semver_parser_cases.json` is the producer-
# owned closed fixture both consumers pin their parser tests against.

class VersionParseError(ValueError):
    """Raised when a version string does not fit the shared parser grammar.

    Replaces the old per-consumer ``_parse_version() -> tuple[int, ...]``
    silent-partial-parse behavior (``"garbage" -> ()``,
    ``"1.129.0-rc.1" -> (1, 129, 0, 1)`` dropping the prerelease tag and
    letting it satisfy a numerically-equal stable floor). There is no
    silent-floor-drop path left: an unparseable version is always an error.
    """


# F9: `\d` matches Unicode digits (`int("١٢٣") == 123`), not just ASCII —
# `re.ASCII` closes that. And a `$`-anchored `.match()` treats a string
# ending in "\n" as matching (Python's `$` matches immediately before a
# trailing newline, not only at the true end), so a version string with
# trailing-newline noise could pass validation invisibly — a "precedence
# inversion" risk (two strings that render identically but differ only in
# trailing whitespace would both validate and could compare equal/adjacent
# in ways the SemVer grammar never intended). `re.fullmatch` on an
# UNANCHORED pattern requires the ENTIRE string, trailing newline included,
# so neither gap exists.
_NUMERIC_RE = re.compile(r"[0-9]+", re.ASCII)
_IDENTIFIER_RE = re.compile(r"[0-9A-Za-z-]+", re.ASCII)


def _validate_release_component(component: str, version_str: str) -> int:
    if not _NUMERIC_RE.fullmatch(component):
        raise VersionParseError(
            f"non-numeric release component {component!r} in {version_str!r}"
        )
    if len(component) > 1 and component[0] == "0":
        raise VersionParseError(
            f"release component {component!r} has a leading zero in "
            f"{version_str!r}"
        )
    return int(component)


def _validate_prerelease_identifier(ident: str, version_str: str) -> "str | int":
    if ident == "" or not _IDENTIFIER_RE.fullmatch(ident):
        raise VersionParseError(
            f"malformed prerelease identifier {ident!r} in {version_str!r}"
        )
    if ident.isdigit():
        if len(ident) > 1 and ident[0] == "0":
            raise VersionParseError(
                f"prerelease numeric identifier {ident!r} has a leading zero "
                f"in {version_str!r}"
            )
        return int(ident)
    return ident


def _validate_build_identifier(ident: str, version_str: str) -> None:
    if ident == "" or not _IDENTIFIER_RE.fullmatch(ident):
        raise VersionParseError(
            f"malformed build-metadata identifier {ident!r} in {version_str!r}"
        )


def parse_version(version_str: str) -> dict[str, Any]:
    """Parse a version string into ``{"release": [major, minor, patch],
    "prerelease": [str|int, ...] | None}``.

    Short releases zero-pad: ``"1"`` -> ``[1, 0, 0]``, ``"1.2"`` ->
    ``[1, 2, 0]``. A fourth release component is malformed and raises, as
    does an empty string, a non-numeric or leading-zero release component, or
    a malformed prerelease/build identifier. Build metadata (``+...``) is
    validated for shape but dropped from the result — it plays no role in
    precedence (SemVer 10).
    """
    if not isinstance(version_str, str) or version_str == "":
        raise VersionParseError("empty version string")

    build_parts = version_str.split("+", 1)
    core = build_parts[0]
    if len(build_parts) == 2:
        build = build_parts[1]
        if build == "":
            raise VersionParseError(
                f"empty build metadata in {version_str!r}"
            )
        for ident in build.split("."):
            _validate_build_identifier(ident, version_str)

    pre_parts = core.split("-", 1)
    release_part = pre_parts[0]
    if release_part == "":
        raise VersionParseError(f"empty release in {version_str!r}")

    release_components = release_part.split(".")
    if len(release_components) > 3:
        raise VersionParseError(
            f"more than 3 release components in {version_str!r}"
        )
    if any(c == "" for c in release_components):
        raise VersionParseError(f"malformed release in {version_str!r}")

    nums = [_validate_release_component(c, version_str) for c in release_components]
    while len(nums) < 3:
        nums.append(0)

    prerelease: list[Any] | None = None
    if len(pre_parts) == 2:
        prerelease_part = pre_parts[1]
        if prerelease_part == "":
            raise VersionParseError(f"empty prerelease in {version_str!r}")
        prerelease = [
            _validate_prerelease_identifier(ident, version_str)
            for ident in prerelease_part.split(".")
        ]

    return {"release": nums, "prerelease": prerelease}


def version_precedence_key(parsed: dict[str, Any]) -> tuple:
    """SemVer precedence sort key (SemVer 11) for a `parse_version()` result.

    A release WITHOUT a prerelease outranks the same release WITH one
    (``1.129.0-rc.1 < 1.129.0``). Two prereleases compare identifier by
    identifier: numeric identifiers compare numerically and always outrank
    lower than alphanumeric ones (SemVer 11.4.3); a prefix-equal shorter set
    has lower precedence (11.4.4) — both fall out of ordinary tuple
    comparison over ``(kind, value)`` pairs, since Python never compares the
    second element once the first (kind) elements differ, and a shorter
    tuple that is a strict prefix of a longer one sorts lower.
    """
    release = tuple(parsed["release"])
    prerelease = parsed["prerelease"]
    if prerelease is None:
        return (release, 1, ())
    ident_keys = tuple(
        (0, ident) if isinstance(ident, int) else (1, ident)
        for ident in prerelease
    )
    return (release, 0, ident_keys)


def meets_floor(version_str: str, floor: Sequence[int]) -> bool:
    """True if `version_str` meets-or-exceeds the stable release `floor`.

    `floor` is a plain release tuple/list (no prerelease component — a floor
    is always a stable release). A prerelease build of the SAME release as
    the floor does NOT meet it (SemVer precedence: prerelease < release).
    Raises VersionParseError if `version_str` does not parse.
    """
    parsed = parse_version(version_str)
    floor_key = (tuple(floor) + (0, 0, 0))[:3]
    stable_floor_key = (floor_key, 1, ())
    return version_precedence_key(parsed) >= stable_floor_key


# ============================================================================
# 2. Three-tier warning classifier (spec C1.2)
# ============================================================================
#
# Permanent consumer-side authority: unmatched warning prose on a SUCCESS
# envelope defaults to "reliability", never "cosmetic" (the pre-C1 default).
# `references/contract_fixtures/warning_classifier_coverage.json` pins one
# row per branch below plus one unmatched case;
# `warning_producer_emissions.json` binds a bounded subset of these strings
# to real producer pytest nodes. Editing a bound live string without
# updating its fixture is a red producer test (the firewall).

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


def classify_warning(warning: str) -> str:
    """Return the consumer tier for a SUCCESS-envelope warning.

    Known patterns are reliability warnings. Unmatched prose fails upward to
    that same tier; it is never presumed cosmetic.
    """
    for pattern in RELIABILITY_PATTERNS:
        if pattern.search(warning):
            return "reliability"
    return "reliability"


# ============================================================================
# 3. Schema-1.0 envelope tiering (R2/R3 dispatcher contract)
# ============================================================================

EXPECTED_SCHEMA_VERSION = "1.0"
DISPATCHER_SCRIPT = "setec_run.py"

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

# reason_category -> tier. Absent/unknown category fails safe to "blocking".
_REASON_CATEGORY_TIER: dict[str, str] = {
    REASON_CATEGORY_VERSION_FLOOR: "blocking",
    REASON_CATEGORY_MISSING_DEPENDENCY: "blocking",
    REASON_CATEGORY_TEXT_TOO_SHORT: "reliability",
    REASON_CATEGORY_POLICY_REFUSED: "blocking",
    REASON_CATEGORY_BAD_INPUT: "blocking",
    REASON_CATEGORY_INTERNAL_ERROR: "blocking",
}

_REQUIRED_ENVELOPE_KEYS = (
    "task_surface", "tool", "version", "available", "target",
    "baseline", "results", "claim_license", "claim_license_rendered",
    "warnings", "ai_status",
)
_ERROR_ENVELOPE_KEYS = ("reason", "reason_category")


class SetecRunnerError(RuntimeError):
    """Raised when SETEC ran but the envelope is unparseable or invalid.
    Discovery / bootstrap-floor errors propagate as SetecDiscoveryError."""


@dataclass
class SupplementResult:
    """Structured result of one SETEC surface invocation."""

    schema_version: str
    task_surface: "str | None"
    tool: str
    version: str
    available: bool
    target: dict[str, Any]
    baseline: "dict[str, Any] | None"
    results: dict[str, Any]
    claim_license: "dict[str, Any] | None"
    claim_license_rendered: "str | None"
    blocking_warnings: list[str] = field(default_factory=list)
    reliability_warnings: list[str] = field(default_factory=list)
    cosmetic_warnings: list[str] = field(default_factory=list)
    ai_status: "str | None" = None
    reason: "str | None" = None
    reason_category: "str | None" = None
    envelope: dict[str, Any] = field(default_factory=dict)
    returncode: int = 0


def _tier_for_reason_category(reason_category: "str | None") -> str:
    if not reason_category:
        return "blocking"
    return _REASON_CATEGORY_TIER.get(reason_category, "blocking")


def _classify_warnings(warnings: list[str]) -> tuple[list[str], list[str]]:
    """Return (reliability, cosmetic) for a SUCCESS envelope's warnings."""
    reliability: list[str] = []
    cosmetic: list[str] = []
    for w in warnings:
        if classify_warning(w) == "reliability":
            reliability.append(w)
        else:
            cosmetic.append(w)
    return reliability, cosmetic


def _coerce_envelope(envelope: dict[str, Any]) -> None:
    sv = envelope.get("schema_version")
    if sv != EXPECTED_SCHEMA_VERSION:
        raise SetecRunnerError(
            f"SETEC envelope schema_version={sv!r}, expected "
            f"{EXPECTED_SCHEMA_VERSION!r}. The bootstrap floor should prevent "
            f"this; check that the discovered SETEC is recent enough."
        )
    missing = [k for k in _REQUIRED_ENVELOPE_KEYS if k not in envelope]
    if envelope.get("available") is False:
        missing.extend(k for k in _ERROR_ENVELOPE_KEYS if k not in envelope)
    if missing:
        raise SetecRunnerError(
            f"SETEC envelope missing required keys: {missing!r}. Envelope "
            f"keys present: {sorted(envelope.keys())!r}"
        )


def tier_envelope(envelope: dict[str, Any], *, returncode: int = 0) -> SupplementResult:
    """Parse + tier an already-decoded schema-1.0 envelope into a
    SupplementResult. Raises SetecRunnerError if it does not conform."""
    _coerce_envelope(envelope)
    available = bool(envelope["available"])
    warnings = list(envelope.get("warnings") or [])
    reason = envelope.get("reason")
    reason_category = envelope.get("reason_category")

    if available:
        reliability, cosmetic = _classify_warnings(warnings)
        blocking: list[str] = []
    else:
        tier = _tier_for_reason_category(reason_category)
        reason_msgs = [reason] if reason else []
        reliability, cosmetic = _classify_warnings(warnings)
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
        returncode=returncode,
    )


# ============================================================================
# 4. Discovery + subprocess invocation (POLICY injected by the wrapper)
# ============================================================================
#
# This module supplies the MECHANISM only. A consumer wrapper supplies:
#   - its ordered list of (path, source-label) candidates (env vars,
#     marketplace search, sibling checkout — repo-specific and NEVER
#     hardcoded here);
#   - its own BOOTSTRAP_SETEC_VERSION floor.
# `_resolve_setec_root` in each consumer's `sync_setec.py` (a SEPARATE,
# offline-checkout resolver used only by the sync/CI tooling) also uses this
# module's `_looks_like_plugin_root` / `_normalize_to_plugin_root` mechanism
# with its own repo-specific resolver order injected (C3).

_PLUGIN_SUBPATH = Path("plugins") / "setec-voiceprint"


@dataclass
class SetecLocation:
    plugin_root: Path
    scripts_dir: Path
    version: tuple[int, ...]
    version_str: str
    source: str


class SetecDiscoveryError(RuntimeError):
    """Raised when SETEC cannot be located or fails the version check."""


def read_plugin_manifest(plugin_root: Path) -> "dict | None":
    for path in (plugin_root / ".claude-plugin" / "plugin.json", plugin_root / "plugin.json"):
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return None
    return None


def looks_like_plugin_root(path: Path) -> bool:
    if not path.is_dir() or not (path / "scripts").is_dir():
        return False
    manifest = read_plugin_manifest(path)
    return bool(manifest) and manifest.get("name") == "setec-voiceprint"


def normalize_to_plugin_root(path: Path) -> "Path | None":
    """Accept either a SETEC plugin root or a repo root that contains one
    (``<root>/plugins/setec-voiceprint``). Returns the plugin root, or None
    if neither shape matches."""
    path = path.expanduser().resolve()
    if looks_like_plugin_root(path):
        return path
    nested = path / _PLUGIN_SUBPATH
    if looks_like_plugin_root(nested):
        return nested
    return None


def build_location(
    plugin_root: Path, source: str, min_version: Sequence[int],
    *, install_instructions: Callable[[], str] = lambda: "",
) -> SetecLocation:
    """Validate `plugin_root` against `min_version` (a bootstrap floor
    supplied by the caller) and build a SetecLocation. Raises
    SetecDiscoveryError on a missing/unreadable manifest, an unparseable
    version, or a version below the floor."""
    manifest = read_plugin_manifest(plugin_root)
    if not manifest:
        raise SetecDiscoveryError(
            f"Found a SETEC plugin root at {plugin_root}, but plugin.json is "
            f"unreadable.\n\n{install_instructions()}"
        )
    version_str = manifest.get("version")
    if not isinstance(version_str, str):
        raise SetecDiscoveryError(
            f"SETEC plugin.json at {plugin_root} has a non-string version: "
            f"{version_str!r}.\n\n{install_instructions()}"
        )
    try:
        parsed = parse_version(version_str)
    except VersionParseError as exc:
        raise SetecDiscoveryError(
            f"SETEC plugin.json at {plugin_root} has a missing/unparseable "
            f"version: {version_str!r} ({exc}).\n\n{install_instructions()}"
        ) from exc
    if not meets_floor(version_str, tuple(min_version)):
        min_str = ".".join(str(p) for p in min_version)
        raise SetecDiscoveryError(
            f"SETEC version {version_str} found at {plugin_root}, but the "
            f"consumer requires {min_str} or newer.\n\n{install_instructions()}"
        )
    return SetecLocation(
        plugin_root=plugin_root,
        scripts_dir=plugin_root / "scripts",
        version=tuple(parsed["release"]),
        version_str=version_str,
        source=source,
    )


def discover_from_candidates(
    candidates: Sequence[tuple[Path, str]],
    min_version: Sequence[int],
    *, install_instructions: Callable[[], str] = lambda: "",
) -> SetecLocation:
    """Resolve the first candidate (in caller-supplied ORDER) that normalizes
    to a valid SETEC plugin root meeting `min_version`. Raises
    SetecDiscoveryError with a summary of every candidate tried."""
    tried: list[str] = []
    for raw, source in candidates:
        plugin_root = normalize_to_plugin_root(raw)
        if plugin_root is None:
            tried.append(f"{source}={raw} (not a setec-voiceprint plugin/repo root)")
            continue
        return build_location(
            plugin_root, source, min_version,
            install_instructions=install_instructions,
        )
    raise SetecDiscoveryError(
        "SETEC Voiceprint not found. Tried: "
        + ("; ".join(tried) if tried else "(no candidates)")
        + f"\n\n{install_instructions()}"
    )


def run_setec_script(
    script_name: str,
    args: list[str],
    *,
    location: SetecLocation,
    check: bool = False,
    capture_output: bool = False,
) -> "subprocess.CompletedProcess":
    """Run a SETEC script (bare filename inside `location.scripts_dir`) as a
    subprocess. cwd is inherited from the caller so caller-relative paths
    (target files, --baseline-dir, --manifest) resolve where expected."""
    script_path = location.scripts_dir / script_name
    if not script_path.is_file():
        raise SetecDiscoveryError(
            f"SETEC script {script_name} not found at {script_path}. SETEC "
            f"{location.version_str} may be missing this entry point; verify "
            f"the name or upgrade SETEC."
        )
    cmd = [sys.executable, str(script_path), *args]
    return subprocess.run(cmd, check=check, capture_output=capture_output, text=True)


def run_dispatcher(
    surface: str, args: list[str], *, location: SetecLocation,
) -> SupplementResult:
    """Run `surface` through SETEC's normalized dispatcher (`setec_run.py`)
    and return a tiered SupplementResult. Raises SetecDiscoveryError if the
    dispatcher is absent (a pre-R2 SETEC); SetecRunnerError if the dispatcher
    ran but produced a non-conforming envelope."""
    if not (location.scripts_dir / DISPATCHER_SCRIPT).is_file():
        raise SetecDiscoveryError(
            f"SETEC at {location.plugin_root} (version {location.version_str}) "
            f"does not provide the normalized dispatcher {DISPATCHER_SCRIPT!r}; "
            f"it predates the R2 normalized entrypoint. Upgrade SETEC to a "
            f"release that ships {DISPATCHER_SCRIPT}."
        )
    dispatcher_args = [surface, *args, "--json"]
    completed = run_setec_script(
        DISPATCHER_SCRIPT, dispatcher_args, location=location, capture_output=True
    )
    if not completed.stdout.strip():
        raise SetecRunnerError(
            f"SETEC dispatcher produced no stdout for surface {surface!r} "
            f"(returncode={completed.returncode}). Stderr (truncated): "
            f"{completed.stderr[:500]!r}"
        )
    try:
        envelope = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SetecRunnerError(
            f"SETEC dispatcher output for surface {surface!r} did not parse: "
            f"{exc}. First 500 chars: {completed.stdout[:500]!r}"
        ) from exc
    return tier_envelope(envelope, returncode=completed.returncode)
