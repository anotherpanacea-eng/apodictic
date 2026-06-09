### SETEC integration — R1 capabilities query + vendor/pin/drift-gate

APODICTIC now data-drives each SETEC surface's version floor from SETEC's
capabilities manifest (`capabilities.py emit --json`) instead of hardcoding it.
New `setec_capabilities.resolve_floor()` discovers SETEC at a single bootstrap
floor, queries the manifest, and asserts the discovered `setec_version` against
each surface's `min_setec_version`. The retired `MIN_SETEC_VERSION = (1, 86, 0)`
per-surface authority and the narrative-decision shim's `(1, 107, 0)` constant
are deleted; all nine `ai_prose_*` shims resolve their floor through the manifest.

Added a vendor/pin/drift-gate apparatus (ported from APODICTIC-Gemini's pull
pattern, in Python): a pinned copy of SETEC's consumer-projected manifest +
R5 contract fixtures under `tests/setec-contract/`, a `setec-plugin.lock` pin,
`scripts/sync_setec.py` (`--check`-able re-derivation), and a drift gate
(`tools/check_setec_contract.py`) whose self-consistency guard fails if any
shim surface is missing from the vendored manifest or lacks a floor. Wired into
CI plus a weekly `sync-setec` workflow. (Provisional pin against the unreleased
SETEC R1+R5 branch; finalization re-pins to the release tag.)
