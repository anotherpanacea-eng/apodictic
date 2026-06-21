### Research — API Reliability Layer

The `/research` Citation Verifier and Field Reconnaissance modes now distinguish a
source that is genuinely *not found* from one that was *not checked* because the
index it needed was degraded or exhausted — closing the failure where a silently
degraded API masqueraded as a clean (or missing) result.

A new stdlib-only `api_reliability.py` (in the research scripts dir) adds, per
batch run: per-provider call **budgets**, a per-provider **circuit breaker**
(run-scoped — it never persists open across runs), and a **reliability ledger**.
`response_cache.py` gains **TTL freshness** (bibliographic metadata 30 days,
Wayback 7 days; env-overridable) wrapped in a backward-compatible envelope; the
no-sticky-error rule is preserved — transient `_error` payloads are still never
written to disk, even with a TTL.

`academic_apis.py`'s batch `output` now carries a `reliability` block (per-provider
calls/ok/errors, budget, circuit state, and a `coverage` summary naming any
degraded provider), and each result gains `resolution_status ∈ {resolved,
not-found, not-checked}`. Citation Verifier and Field Reconnaissance report a
**Source coverage** line: when coverage is DEGRADED, any `unretrievable` verdict on
a citation whose only candidate index was a degraded provider is reported as
NOT-CHECKED, not NOT-FOUND, and a DEGRADED state on a high-stakes / Pre-DE run is
disclosed as a blind spot in the synthesis Absence Inventory.

Reliability bookkeeping is default-on; `APODICTIC_RELIABILITY=off` omits the
top-level `reliability` block. The additive per-result
(`resolution_status`/`degraded_providers`) and summary (`not_checked`/`not_found`)
keys remain, additive and never altering an existing value, so the legacy
result/summary keys are unchanged. Per-provider budgets and TTLs are
env-overridable (`APODICTIC_BUDGET_<PROVIDER>`,
`APODICTIC_CACHE_TTL_METADATA_DAYS`, `APODICTIC_CACHE_TTL_WAYBACK_DAYS`).
