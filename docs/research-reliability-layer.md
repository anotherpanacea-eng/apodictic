# Research / API Reliability Layer

**Status:** **Built** (`api_reliability.py` + `response_cache.py` TTL + `academic_apis.py` wiring + the two research-mode prose contracts). Run-level/provider-level hardening of `/research`; additive — `APODICTIC_RELIABILITY=off` omits the `reliability` block (the additive per-result/summary keys remain, never altering existing values).
<!-- built-when: plugins/apodictic/skills/specialized-audits/scripts/api_reliability.py -->
<!-- Single-marker by design (docs/qol-status-drift-lint.md § Marker syntax: one repo-relative PATH, no globs, no AND). The CI registration of the module's --self-test is asserted by the ci.yml step, not by a second marker. -->

**ROADMAP home:** `ROADMAP.md` § Research / API Reliability Layer (post-v2.x hardening band; the follow-on to the v2.0.0 Phase 5 plumbing).
**Surface owner:** `/research` (Citation Verifier, Field Reconnaissance) → `plugins/apodictic/skills/specialized-audits/scripts/`.

---

## 1. Framing

apodictic's `/research` modes reach seven keyless/low-friction academic APIs —
CrossRef, Semantic Scholar, OpenAlex, CORE, Unpaywall, PubMed, Wayback — through
one shipped client (`academic_apis.py`) backed by a disk cache
(`response_cache.py`) and a provenance store (`provenance.py`). v2.0.0 Phase 5
hardened the *single call*: bounded exponential backoff honoring `Retry-After`, a
no-sticky-error rule that keeps transient `_error` payloads memory-only, and a
single-call retraction derivation. The gap this layer closes is **run-level and
provider-level**: today a provider that is *up but silently degraded* (empty
result sets, throttling to exhaustion, down for the whole batch) produces the same
shape as a genuine "source not found" — `resolved: false`,
`confidence: unretrievable` — with nothing distinguishing "we looked and it isn't
there" from "the index we needed never answered." For a Citation Verifier whose
contract is *never bluff verification*, that conflation is the central failure
mode. This layer makes degradation **legible and bounded**: per-provider call
budgets, a per-provider circuit breaker, cache TTLs with freshness stamps, and a
per-run **reliability ledger** that lets an `unretrievable` verdict be tagged
honestly as *not-found* vs. *not-checked (provider degraded/exhausted)*.

This is plumbing, not judgment. It never edits a manuscript, never fetches outside
the seven existing providers, and never upgrades a verdict — it sits inside the
existing diagnostic/rewrite firewall.

---

## 2. Unit of work

One new stdlib-only module plus additive changes to two existing scripts and the
two LLM-facing research-mode docs:

- **`plugins/apodictic/skills/specialized-audits/scripts/api_reliability.py`** —
  new module: `ProviderBudget`, `CircuitBreaker`, `ReliabilityLedger`, and a `TTL`
  helper. Carries a `--self-test` arm.
- **`response_cache.py`** — additive TTL + freshness-stamp support. Disk entries
  gain a `{_cached_at, _payload}` envelope; `get(key, ttl_seconds=...)` re-fetches
  when stale; `set(key, value, ttl=...)`. Backward-compatible (no TTL ⇒ today's
  behavior; legacy un-enveloped files never auto-expire). Gains a `--self-test`.
- **`academic_apis.py`** — thread a run-scoped ledger through
  `resolve_batch → resolve_citation → resolvers → _fetch_json`; emit a
  `reliability` block in the batch `output` and a per-result `resolution_status`.
  Gains a `--self-test` (offline, network monkeypatched).
- **`references/craft/research-citation-verifier.md`** and
  **`references/craft/research-field-recon.md`** — the prose contract.
- **`specialized-audits/SKILL.md` § Research Mode Scripts** — register the module.
- **`changelog.d/research-reliability-layer.md`** — one fragment.

This is **not** a new `/research` mode, a new audit, or a new `validate.sh`
validator. It is a hardening of an existing surface's external-IO substrate.

---

## 3. Substrate (re-verified against the live repo — paths corrected from the spec draft)

| Asserted substrate | Verified location | Confirmed fact |
|---|---|---|
| External-API client | `plugins/apodictic/skills/specialized-audits/scripts/academic_apis.py` | 531 lines (pre-change); `_fetch_json(url, headers, timeout)`, `resolve_citation(citation, cache, provenance)`, `resolve_batch(citations, output_path)` |
| Phase 5 backoff / Retry-After | same file, ll. 45–105 | `_HTTP_MAX_RETRIES` (`APODICTIC_HTTP_RETRIES`, default 3), `_RETRYABLE_STATUS={429,500,502,503,504}`, `_retry_after_delay()` caps at 60s |
| No-sticky-error cache | `response_cache.py` ll. 50–64 | `set()` keeps `_error` dicts memory-only, never to disk |
| Batch output shape | `resolve_batch` (output dict at ll. 453–458) | `output = {summary, results, provenance, cache_stats}` — the insertion point for a `reliability` block |
| Confidence vocabulary | `references/craft/research-citation-verifier.md` (Confidence levels table; `unretrievable` is the relevant row) | `full-text` / `abstract-only` / `metadata-only verified` / `unretrievable` |
| Artifact names | `references/craft/research-citation-verifier.md` (`Citation_Ledger.md`), `research-field-recon.md` (`Field_Reconnaissance_Report.md`) | both confirmed present (NOT in the dir the spec draft cited — they live under `references/craft/`) |
| Synthesis blind-spot home | `skills/core-editor/references/run-synthesis.md` § "3. Blind Spot / Absence Inventory (required)" | confirmed; already routes a declined high-stakes Citation Verifier to a confidence limiter |
| Self-test convention | root `scripts/` letter-family validators in `validate.sh`'s `AGG_VALIDATORS` | the research-dir scripts carry NO `--self-test` today — this layer **introduces** it to the dir |
| Mirror set | `validate.sh check-mirror` | compares **all `*.py` in root `scripts/` ↔ `plugins/apodictic/scripts/`**; the research dir is a THIRD location outside that pair → single-sourced by directory placement, not by a narrow mirror set |

**Substrate-citation corrections folded from spec review:** the two research docs
live under `references/craft/`, not the scripts dir; the client is 531 lines (not
532) and the output dict sits at ll. 453–458; the research-dir scripts have no
prior `--self-test`; and the mirror exemption is by directory, not by a narrow
mirror set. All corrected above.

---

## 4. The wiring seam (honest about scope — folded from spec review)

`resolve_batch` **constructs** `ResponseCache` and `ProvenanceStore` internally
(there is no caller injection seam); the ledger is constructed the same way. The
real change surface is larger than "composition":

- `_fetch_json` was a module-level free function with **no provider identity**.
  It gains optional `provider` + `ledger` parameters. When both are present it is
  **gated** first (`ledger.allow_call(provider)`): an open circuit or exhausted
  budget short-circuits **before** any network/budget cost and returns a
  `{_skipped}` sentinel. After a call that fires, the outcome is recorded on the
  ledger (error → breaker failure; clean → reset). A bare `_fetch_json(url)` with
  no ledger is byte-for-byte today's behavior.
- The network body was factored into `_fetch_json_network` so the gate/record
  wraps a single body (every prior return path is preserved).
- **Every resolver** (`resolve_crossref_doi`, `search_crossref`,
  `search_semantic_scholar`, `get_s2_citations`, `search_openalex`, `search_core`,
  `check_unpaywall`, `search_pubmed`, `check_wayback`) gains a `ledger=None`
  parameter and passes its provider name through — none knew which provider it was
  hitting before, so this is a signature change rippling through the resolver tier
  (not the light touch the draft implied).
- `resolve_citation` threads the ledger, tracks which tiers were skipped
  (`not_checked`), and sets `resolution_status`. URL liveness (`_check_url`) is
  **not** gated (it is not one of the seven index providers and is never
  disk-cached).

### 4.1 Cache TTL / freshness (`response_cache.py`)

Disk writes are wrapped: `{ "_cached_at": <ts>, "_payload": <value> }`.
`get(key, ttl_seconds=None)`: `None` ⇒ never age-expire (today's behavior); a
stamp older than the TTL ⇒ a **miss** (re-fetch). A legacy un-enveloped file has
unknown freshness and is **never** auto-expired. `_error` payloads stay
memory-only and are never written, so they are never TTL-cached on disk. A
`now` callable is injectable for deterministic tests.

Default TTLs (env-overridable): bibliographic metadata / OA status / searches
30 days (`APODICTIC_CACHE_TTL_METADATA_DAYS`); Wayback availability 7 days
(`APODICTIC_CACHE_TTL_WAYBACK_DAYS`). URL liveness stays run-local.

### 4.2 ProviderBudget / CircuitBreaker / ReliabilityLedger

Defaults per batch (env-overridable via `APODICTIC_BUDGET_<PROVIDER>`): crossref
200, semantic-scholar 100 (tighter — 429s without a key), openalex 200, core 100,
unpaywall 200, pubmed 100, wayback 100; unknown provider → fallback 100 (never a
`KeyError`). A **cache hit does not charge** the budget. The breaker opens after
`threshold` (default 3) **consecutive** failures and stays open for the run
(run-scoped; cross-run persistence is a non-goal — a stale-open breaker would
itself be a silent-degradation source). The ledger records calls/ok/errors,
budget, circuit, and a `coverage` block; a provider is `degraded` iff its circuit
opened OR its budget exhausted OR `errors/calls > 0.5` with `calls >= 4`.

### 4.3 Per-result `resolution_status` and the batch `reliability` block

Each result gains `resolution_status ∈ {resolved, not-found, not-checked}` and
`degraded_providers`. `not-checked` iff a tier that could plausibly have resolved
the citation was cut short by a degraded provider; `not-found` iff every healthy
provider returned no match; `resolved` otherwise. The Firewall is
one-directional: `resolution_status` is never `"resolved"` on an unresolved
result. `resolve_batch`'s `output` gains a top-level `reliability` key
(`ledger.snapshot()`) next to `cache_stats`, and the `summary` gains
`not_checked` / `not_found` counts. With `APODICTIC_RELIABILITY=off` the
top-level `reliability` block is **omitted**; the additive per-result
(`resolution_status`/`degraded_providers`) and summary (`not_checked`/`not_found`)
keys still appear (computed without a ledger — `degraded_providers` is then `[]`),
additive and never altering a pre-existing value, so the legacy result/summary
keys are unchanged.

### 4.4 Prose contract (LLM-facing)

`Citation_Ledger.md` Summary and `Field_Reconnaissance_Report.md` carry a
**Source coverage: CLEAN | DEGRADED — <provider> (reason)** line. When DEGRADED,
any UNRETRIEVABLE verdict on a citation whose only candidate index was a degraded
provider is reported as NOT-CHECKED, not NOT-FOUND. The citation-verifier Hard
Gates and the field-recon guardrails gain one clause: a DEGRADED coverage state on
a high-stakes / Pre-DE-Prerequisite run is itself a disclosable blind spot, routed
to `run-synthesis.md` § 3 Blind Spot / Absence Inventory (the same path the
field-recon decline already uses), rather than being swallowed into the resolution
rate.

---

## 5. M1 scope vs. the model seam

**M1 (stdlib-only, deterministic, CI-gated — the whole reliability mechanism):**
the three objects + TTL (pure stdlib, `--self-test`); the cache envelope (clock
injection, no sleep); the client wiring (testable **offline** —
`_fetch_json_network` monkeypatched, `APODICTIC_HTTP_RETRIES=0`, canned
`_error`/success/skip dicts; never a socket); CI runs each module's `--self-test`
directly.

**Beyond M1 (the model seam):** the *editorial use* of `resolution_status` /
`coverage` — the LLM writing the honest NOT-CHECKED-vs-NOT-FOUND distinction into
the ledger prose — is prompt-contract work verified through the `evals/` track, not
the validator track. M1 ships the doc contract and the machine-readable block; it
does not assert the LLM honors it. Live-API behavior under real degradation is
out of scope (defaults are reasoned, not telemetry-tuned).

---

## 6. P1 RESOLUTION — why there is NO `validate.sh` arm (folded from spec review)

The spec draft (AC-9 / §10.2) called for an `api-reliability` entry in
`AGG_VALIDATORS` and a `validate.sh` dispatcher arm, while DC-1 / AC-10 kept the
module single-sourced in the research dir. **These are self-contradictory.** Every
`validate.sh` dispatcher arm resolves its helper from `$(dirname "$0")/<module>.py`
= root `scripts/`; no arm reaches outside its own dir. Worse, `validate.sh` is
mirrored **byte-identically** to `plugins/apodictic/scripts/validate.sh`, so a
relative path into the research dir would resolve to two different (one
nonexistent) locations from the two copies. A correct dispatcher arm for a
research-dir module is therefore impossible.

**Resolution (option (a) of the review fix):** drop the `AGG_VALIDATORS` /
dispatcher-arm requirement entirely. `validate.sh` is **not touched**. The
module's `--self-test` (and the cache + client self-tests) run via a **direct
invocation in `.github/workflows/ci.yml`**:

```yaml
- name: Research reliability self-tests
  run: |
    python3 plugins/apodictic/skills/specialized-audits/scripts/api_reliability.py --self-test
    python3 plugins/apodictic/skills/specialized-audits/scripts/response_cache.py --self-test
    python3 plugins/apodictic/skills/specialized-audits/scripts/academic_apis.py --self-test
```

`validate.sh check-mirror` stays green because nothing mirrored changed, and the
research dir is outside the mirror pair (so the module is single-sourced by
directory placement — AC-10's outcome holds, with its rationale corrected).

---

## 7. Acceptance criteria

1. **AC-1.** `api_reliability.py` exists in the research scripts dir;
   `python -m compileall -q plugins` is clean. (CI byte-compile.)
2. **AC-2 (budget).** `ProviderBudget(None).charge("crossref")` grants exactly the
   default budget then denies; `remaining()`/`spent()` reconcile; unknown provider
   → fallback budget, never `KeyError`. (`api_reliability --self-test`.)
3. **AC-3 (breaker).** 3 consecutive failures open; a success before the third
   resets; once open the ledger gate refuses the call with no budget charge.
4. **AC-4 (TTL).** Hit at `now=5` / miss at `now=11` for `ttl=10` written at
   `now=0`; legacy un-enveloped file never auto-expires; `_error` never written.
   (`response_cache --self-test`, clock injected.)
5. **AC-5 (no-sticky-error preserved).** `set(k, {"_error":…}, ttl=…)` writes
   nothing to disk; a fresh in-memory cache misses. (`response_cache --self-test`.)
6. **AC-6 (ledger).** Scripted S2 (3 errors → exhaust) + clean CrossRef yields
   `coverage.clean == false`, `degraded_providers == ["semantic-scholar"]`, and a
   `circuit-open` then `budget-exhausted` event in order.
7. **AC-7 (resolution_status honesty — core claim, dedicated negative fixture).**
   Offline `resolve_citation`/`resolve_batch`: resolvable-only-via-degraded →
   `not-checked`; genuine 0-match of every healthy provider → `not-found`; clean
   → `resolved`. (`academic_apis --self-test`.)
8. **AC-8 (batch shape).** `resolve_batch` output has top-level `reliability`
   (providers/events/coverage) plus the unchanged `summary`/`results`/
   `provenance`/`cache_stats`. (`academic_apis --self-test`.)
9. **AC-9 (CI runs the self-tests directly).** `.github/workflows/ci.yml` invokes
   the three `--self-test`s directly — **NOT** via `AGG_VALIDATORS` (see § 6). No
   `validate.sh`/`AGG_COUNT` change.
10. **AC-10 (mirror discipline).** Module not in root `scripts/`, not in the
    mirror pair; `validate.sh check-mirror` stays green; `validate.sh` untouched.
11. **AC-11 (docs contract + freshness).** Both research docs carry the coverage /
    `resolution_status` contract; SKILL.md registers the module; this doc's Status
    is flipped and `check-status-drift.mjs` passes against the `built-when` marker;
    `commands/research.md` mode list is unchanged so `check-inventory-parity`
    reports no signature drift.
12. **AC-12 (firewall).** No path edits a manuscript, fetches outside the seven
    providers, or upgrades a verdict; `resolution_status` is never `"resolved"` on
    an unresolved result (asserted in `academic_apis --self-test`).
13. **AC-13 (backward compat / opt-out).** `APODICTIC_RELIABILITY=off` (or high
    limits) omits the top-level `reliability` block; the additive per-result
    (`resolution_status`/`degraded_providers`) and summary (`not_checked`/`not_found`)
    keys remain (additive, never altering an existing value — `degraded_providers`
    is `[]` with no ledger), so the legacy `results`/`summary` keys are unchanged.
    (`academic_apis --self-test` AC-13 asserts the block is absent and resolution
    still works; the additive keys are the repo's accepted pattern.)

---

## 8. Non-goals

Run-scoped budgets/breakers (no cross-run breaker persistence — deliberate).
Provider identity is host-family, not key-tier. Defaults are reasoned, not
measured. The editor's honesty is a prompt contract, not enforced by this module.
No new network surface. Field Reconnaissance is more LLM-orchestrated than
Citation Verifier: the `reliability` block is fully realized for the Citation
Verifier batch path; field-recon's M1 deliverable is the prose contract plus
availability of the same module if/when it invokes the batch client.

## 9. Open questions (non-blocking)

- **OQ-1.** Should a DEGRADED coverage state on a high-stakes run *halt* (`--strict`)
  or only *disclose*? Defaults to **disclose** (route to the synthesis blind-spot
  inventory), matching the field-recon decline path.
- **OQ-2.** Should per-provider budgets scale with batch size? Deferred to telemetry.
- **OQ-3.** Persist the `reliability` block to a `Citation_Reliability.json`
  sidecar? Not in M1; additive follow-on.
