### Research — Reliability Layer strict halt + sidecar (OQ-1, OQ-3)

Two additive, stdlib-only follow-ons to the Research / API Reliability Layer, both
off by default so existing (non-strict) behavior and the AC-1..AC-13 contract are
unchanged. **OQ-1 (`--strict` halt):** `academic_apis.py batch --strict` (and
`resolve_batch(..., strict=True)`) now HALTS a high-stakes run — non-zero exit
(`STRICT_HALT_EXIT_CODE` = 3) plus a `reliability.strict` sub-block
(`{enabled, halt, reason, degraded_providers, not_checked}`) — iff coverage ended
DEGRADED (≥1 degraded provider) **and** ≥1 citation was NOT-CHECKED, so a degraded
verdict can no longer be emitted as a clean not-found. The halt is one-directional:
a clean run, a non-strict run, or a genuine all-healthy NOT-FOUND (NOT-FOUND ≠
NOT-CHECKED) never fires it, and with `APODICTIC_RELIABILITY=off` there is no
degradation signal to trip it. **OQ-3 (`Citation_Reliability.json` sidecar):** a
pure serializer `build_reliability_sidecar` + writer `write_reliability_sidecar`
(schema `apodictic.citation_reliability.v1`, deterministic `sort_keys` order)
persist budget-spent, circuit states, coverage/degraded_providers, per-provider
snapshot, events, and the resolved/not_found/not_checked summary; opt-in via
`batch --sidecar-dir DIR`, and it never mutates the in-`output` `reliability` block.
Both modules' `--self-test` gained coverage (halt fires only on genuine degradation;
sidecar shape, determinism, and disk round-trip); OQ-2 (telemetry-tuned budgets)
stays open.
