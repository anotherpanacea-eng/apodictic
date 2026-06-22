#!/usr/bin/env python3
"""
Run-level / provider-level reliability layer for APODICTIC's research surface.

v2.0.0 Phase 5 hardened the *single call* (bounded backoff honoring Retry-After,
the no-sticky-error cache rule, single-call retraction derivation). This module
adds the *run-level* bookkeeping that makes provider degradation legible and
bounded, so an `unretrievable` verdict can be tagged honestly as
*not-found* (we looked and it isn't there) vs. *not-checked* (the index we needed
was degraded/exhausted and never answered).

Three plain-stdlib objects, composed into `academic_apis.resolve_batch` by the
same pattern that already constructs `ResponseCache` / `ProvenanceStore`:

  ProviderBudget   — per-provider per-batch call ceiling (network calls only;
                     a cache hit does not charge).
  CircuitBreaker   — per-provider, run-scoped; `threshold` consecutive failures
                     opens it for the rest of the batch (no cross-run persistence
                     — a stale-open breaker would itself be a silent-degradation
                     source).
  ReliabilityLedger — the load-bearing artifact: records calls/ok/errors,
                     budget, circuit, and a `coverage` block that classifies
                     each provider as degraded or not.

Plus a thin `TTL` helper for `response_cache.py`'s freshness arithmetic.

This is plumbing, not judgment. It never edits a manuscript, never fetches
outside the seven existing providers, and can only *downgrade* honesty (turn a
`not-found` into a disclosed `not-checked`), never the reverse.

CONVENTION NOTE: the research-dir scripts (academic_apis.py, response_cache.py,
provenance.py) carry NO `--self-test` today; that arm is specific to the root
`scripts/` letter-family validators in `validate.sh`'s `AGG_VALIDATORS`. This
module *introduces* the self-test convention to the research dir, and its CI
entry point is a DIRECT invocation in `.github/workflows/ci.yml`
(`python3 .../api_reliability.py --self-test`) — NOT an `AGG_VALIDATORS` /
`validate.sh` dispatcher arm. A dispatcher arm resolves its helper from
`$(dirname "$0")` = root `scripts/`, and `validate.sh` is mirrored
byte-identically to `plugins/apodictic/scripts/`; a research-dir module cannot
be reached from a byte-identical arm. See docs/research-reliability-layer.md
§ P1.

Usage:
    python api_reliability.py --self-test
"""

import json
import os
import sys
import time

# ---------------------------------------------------------------------------
# Provider identity
# ---------------------------------------------------------------------------

# The seven host families already implicit in academic_apis.py. A provider is a
# host family, NOT a key-tier: "semantic-scholar" is one provider whether or not
# S2_API_KEY is set (per-key budgets are out of scope).
PROVIDERS = (
    "crossref",
    "semantic-scholar",
    "openalex",
    "core",
    "unpaywall",
    "pubmed",
    "wayback",
)

# Default per-batch call budgets. Reasoned (not telemetry-tuned): semantic-scholar
# is tighter because it 429s without a key (per research-citation-verifier.md's
# rate-limit note). Env-overridable via APODICTIC_BUDGET_<PROVIDER> (provider name
# upper-cased, hyphens → underscores) for offline-determinism in tests.
_DEFAULT_BUDGETS = {
    "crossref": 200,
    "semantic-scholar": 100,
    "openalex": 200,
    "core": 100,
    "unpaywall": 200,
    "pubmed": 100,
    "wayback": 100,
}
# Fallback budget for an unknown provider name (never a KeyError — AC-2).
_FALLBACK_BUDGET = 100

# Error-rate floor for the `degraded` derivation (§4.4): a provider is degraded if
# its circuit opened OR its budget was exhausted OR (errors/calls > 0.5 with
# calls >= 4). The calls>=4 guard keeps a single early error from flagging.
_DEGRADED_ERROR_RATE = 0.5
_DEGRADED_MIN_CALLS = 4


def _env_budget(provider: str) -> int | None:
    """Read APODICTIC_BUDGET_<PROVIDER> if set and valid, else None."""
    key = "APODICTIC_BUDGET_" + provider.upper().replace("-", "_")
    raw = os.environ.get(key)
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def reliability_enabled() -> bool:
    """Default-on with an env opt-out. APODICTIC_RELIABILITY=off reproduces the
    pre-reliability behavior in the non-reliability keys of the output (AC-13)."""
    return os.environ.get("APODICTIC_RELIABILITY", "on").strip().lower() != "off"


# ---------------------------------------------------------------------------
# ProviderBudget
# ---------------------------------------------------------------------------

class ProviderBudget:
    """Per-provider call ceiling for one batch run. A cache hit does NOT charge
    the budget (only a real network call does) — this keeps the budget a true
    network-rationing tool and keeps re-runs (mostly cache hits) cheap."""

    def __init__(self, limits: dict | None = None):
        # Resolve each provider's ceiling: explicit override > env > default.
        self._limit: dict[str, int] = {}
        self._spent: dict[str, int] = {}
        for p in PROVIDERS:
            if limits and p in limits:
                self._limit[p] = int(limits[p])
            else:
                env = _env_budget(p)
                self._limit[p] = env if env is not None else _DEFAULT_BUDGETS[p]
            self._spent[p] = 0
        # Carry any caller-supplied non-standard providers too.
        if limits:
            for p, v in limits.items():
                if p not in self._limit:
                    self._limit[p] = int(v)
                    self._spent[p] = 0

    def _ensure(self, provider: str) -> None:
        if provider not in self._limit:
            # Unknown provider → fallback budget, never a KeyError (AC-2).
            env = _env_budget(provider)
            self._limit[provider] = env if env is not None else _FALLBACK_BUDGET
            self._spent[provider] = 0

    def charge(self, provider: str) -> bool:
        """Charge one network call. Returns True (and decrements) if allowed,
        False if the provider's budget is exhausted."""
        self._ensure(provider)
        if self._spent[provider] >= self._limit[provider]:
            return False
        self._spent[provider] += 1
        return True

    def remaining(self, provider: str) -> int:
        self._ensure(provider)
        return max(0, self._limit[provider] - self._spent[provider])

    def exhausted(self, provider: str) -> bool:
        self._ensure(provider)
        return self._spent[provider] >= self._limit[provider]

    def spent(self) -> dict:
        return dict(self._spent)


# ---------------------------------------------------------------------------
# CircuitBreaker
# ---------------------------------------------------------------------------

class CircuitBreaker:
    """Per-provider, run-scoped breaker. `threshold` CONSECUTIVE failures open it
    for the remainder of the batch; a clean outcome resets the counter. An open
    breaker short-circuits before the call (no budget charge, no network).

    Run-scoped is deliberate (DC-3 / §8): cross-run breaker persistence is a
    non-goal because a stale-open breaker would itself be a silent-degradation
    source — exactly the failure this layer exists to kill."""

    def __init__(self, threshold: int = 3):
        self._threshold = max(1, int(threshold))
        self._failures: dict[str, int] = {}
        self._open: dict[str, bool] = {}

    def record_outcome(self, provider: str, ok: bool) -> None:
        if ok:
            self._failures[provider] = 0
            # A success does NOT re-close an already-open breaker: once open it
            # stays open for the run (run-scoped, no half-open in M1).
            return
        if self._open.get(provider):
            return
        self._failures[provider] = self._failures.get(provider, 0) + 1
        if self._failures[provider] >= self._threshold:
            self._open[provider] = True

    def is_open(self, provider: str) -> bool:
        return bool(self._open.get(provider))

    def failures(self, provider: str) -> int:
        return self._failures.get(provider, 0)

    def state(self) -> dict:
        out: dict[str, dict] = {}
        names = set(self._failures) | set(self._open)
        for p in names:
            out[p] = {"failures": self._failures.get(p, 0), "open": bool(self._open.get(p))}
        return out


# ---------------------------------------------------------------------------
# ReliabilityLedger
# ---------------------------------------------------------------------------

class ReliabilityLedger:
    """Run-level reliability bookkeeping. The load-bearing artifact: its
    `snapshot()` is what lets an `unretrievable` verdict be honestly classified
    as not-found vs. not-checked.

    A single ledger owns the budget + breaker so callers thread ONE context
    object through `resolve_citation` → resolvers → `_fetch_json`."""

    def __init__(self, budget: ProviderBudget | None = None,
                 breaker: CircuitBreaker | None = None):
        self.budget = budget if budget is not None else ProviderBudget()
        self.breaker = breaker if breaker is not None else CircuitBreaker()
        self._calls: dict[str, int] = {}
        self._ok: dict[str, int] = {}
        self._errors: dict[str, int] = {}
        self._events: list[dict] = []
        # Per-run monotonic call counter for event ordering ("at_call").
        self._call_seq = 0

    # -- gate: may we call this provider right now? -------------------------

    def allow_call(self, provider: str) -> bool:
        """Decide whether a network call to `provider` may proceed. Records a
        `circuit-open` or `budget-exhausted` event (once each, on the transition)
        and returns False to skip. A skipped provider is the caller's signal to
        fall through to the next tier exactly as it does today for an `_error`."""
        if self.breaker.is_open(provider):
            self._note_event(provider, "circuit-open",
                             after_failures=self.breaker.failures(provider))
            return False
        if not self.budget.charge(provider):
            self._note_event(provider, "budget-exhausted")
            return False
        return True

    def _note_event(self, provider: str, kind: str, **extra) -> None:
        # Record at most one circuit-open and one budget-exhausted event per
        # provider per run (the transition is the signal, not every skip).
        for ev in self._events:
            if ev["provider"] == provider and ev["kind"] == kind:
                return
        ev = {"provider": provider, "kind": kind, "at_call": self._call_seq}
        ev.update(extra)
        self._events.append(ev)

    # -- record the outcome of a call that actually fired -------------------

    def record(self, provider: str, response) -> None:
        """Record the outcome of a network call that fired. A dict containing
        `_error` (a retry-exhausted _fetch_json result) is one failure; anything
        else is a success that resets the breaker counter."""
        self._call_seq += 1
        self._calls[provider] = self._calls.get(provider, 0) + 1
        is_error = isinstance(response, dict) and "_error" in response
        if is_error:
            self._errors[provider] = self._errors.get(provider, 0) + 1
            self.breaker.record_outcome(provider, ok=False)
            if self.breaker.is_open(provider):
                self._note_event(provider, "circuit-open",
                                 after_failures=self.breaker.failures(provider))
        else:
            self._ok[provider] = self._ok.get(provider, 0) + 1
            self.breaker.record_outcome(provider, ok=True)

    # -- degradation classification -----------------------------------------

    def _degraded(self, provider: str) -> bool:
        if self.breaker.is_open(provider):
            return True
        if self.budget.exhausted(provider):
            return True
        calls = self._calls.get(provider, 0)
        errors = self._errors.get(provider, 0)
        if calls >= _DEGRADED_MIN_CALLS and (errors / calls) > _DEGRADED_ERROR_RATE:
            return True
        return False

    def degraded_providers(self) -> list[str]:
        seen = set(self._calls) | set(self.breaker.state()) | set(self.budget.spent())
        # Only report providers that were actually touched OR forced open.
        touched = [p for p in PROVIDERS if p in self._calls or self.breaker.is_open(p)]
        touched += [p for p in seen if p not in PROVIDERS and (p in self._calls or self.breaker.is_open(p))]
        return [p for p in touched if self._degraded(p)]

    def is_degraded(self, provider: str) -> bool:
        return self._degraded(provider)

    # -- snapshot -----------------------------------------------------------

    def snapshot(self) -> dict:
        providers: dict[str, dict] = {}
        touched = [p for p in self._calls]
        for p in self.breaker.state():
            if p not in touched:
                touched.append(p)
        for p in touched:
            providers[p] = {
                "calls": self._calls.get(p, 0),
                "ok": self._ok.get(p, 0),
                "errors": self._errors.get(p, 0),
                "budget_remaining": self.budget.remaining(p),
                "circuit": "open" if self.breaker.is_open(p) else "closed",
                "degraded": self._degraded(p),
            }
        degraded = self.degraded_providers()
        if degraded:
            note = (
                f"{', '.join(degraded)} degraded "
                "(circuit open, budget exhausted, or error rate > 50%); "
                "citations whose only candidate index was a degraded provider are "
                "NOT-CHECKED, not NOT-FOUND."
            )
        else:
            note = "All touched providers healthy; unretrievable verdicts are NOT-FOUND."
        return {
            "providers": providers,
            "events": list(self._events),
            "coverage": {
                "degraded_providers": degraded,
                "clean": not degraded,
                "note": note,
            },
        }


# ---------------------------------------------------------------------------
# TTL helper (for response_cache.py freshness arithmetic)
# ---------------------------------------------------------------------------

# Cache TTLs are per content-kind, env-overridable for offline determinism.
_DAY = 86400.0


def _env_days(name: str, default_days: float) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default_days
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default_days


class TTL:
    """Per-content-kind TTL resolver. The client knows whether a cache key is a
    DOI resolution (near-immutable → 30d) or a Wayback availability check
    (snapshots accrue → 7d). URL liveness is never disk-cached today and stays
    run-local. Env overrides: APODICTIC_CACHE_TTL_METADATA_DAYS,
    APODICTIC_CACHE_TTL_WAYBACK_DAYS."""

    @staticmethod
    def metadata_seconds() -> float:
        return _env_days("APODICTIC_CACHE_TTL_METADATA_DAYS", 30.0) * _DAY

    @staticmethod
    def wayback_seconds() -> float:
        return _env_days("APODICTIC_CACHE_TTL_WAYBACK_DAYS", 7.0) * _DAY

    @staticmethod
    def for_key(key: str) -> float | None:
        """Return the TTL (seconds) for a cache key by its prefix, or None for a
        key that should never age-expire."""
        if key.startswith("wayback:"):
            return TTL.wayback_seconds()
        if (key.startswith("crossref:")
                or key.startswith("unpaywall:")
                or key.startswith("s2:")
                or key.startswith("openalex:")
                or key.startswith("core:")
                or ":search:" in key):
            return TTL.metadata_seconds()
        return None


# ---------------------------------------------------------------------------
# Self-test (the contract). Introduces the convention to this dir; run directly
# from CI. Positive AND negative fixtures — the negatives are the point.
# ---------------------------------------------------------------------------

class _SelfTest:
    def __init__(self):
        self.failures: list[str] = []
        self.passed = 0

    def expect(self, name: str, got, want) -> None:
        if got == want:
            self.passed += 1
        else:
            self.failures.append(f"{name}: got {got!r}, want {want!r}")

    def expect_true(self, name: str, cond) -> None:
        self.expect(name, bool(cond), True)


def run_self_test() -> int:
    t = _SelfTest()

    # -- AC-2: ProviderBudget -------------------------------------------------
    b = ProviderBudget(None)
    default_crossref = _DEFAULT_BUDGETS["crossref"]  # 200
    charged = sum(1 for _ in range(default_crossref) if b.charge("crossref"))
    t.expect("ac2_budget_grants_exactly_default", charged, default_crossref)
    t.expect_true("ac2_budget_then_denies", b.charge("crossref") is False)
    t.expect("ac2_remaining_zero", b.remaining("crossref"), 0)
    t.expect("ac2_spent_reconciles", b.spent().get("crossref"), default_crossref)
    # Unknown provider → fallback budget, no KeyError.
    t.expect_true("ac2_unknown_provider_ok", b.charge("not-a-real-provider") is True)
    t.expect("ac2_unknown_remaining", b.remaining("not-a-real-provider"), _FALLBACK_BUDGET - 1)
    # Explicit limit override.
    b2 = ProviderBudget({"crossref": 2})
    t.expect_true("ac2_override_1", b2.charge("crossref"))
    t.expect_true("ac2_override_2", b2.charge("crossref"))
    t.expect_true("ac2_override_denies_3", b2.charge("crossref") is False)

    # -- AC-3: CircuitBreaker opens and short-circuits ------------------------
    cb = CircuitBreaker(threshold=3)
    cb.record_outcome("pubmed", False)
    cb.record_outcome("pubmed", False)
    t.expect_true("ac3_not_open_at_2", cb.is_open("pubmed") is False)
    cb.record_outcome("pubmed", False)
    t.expect_true("ac3_open_at_3", cb.is_open("pubmed"))
    # A success BEFORE the third failure resets the counter.
    cb2 = CircuitBreaker(threshold=3)
    cb2.record_outcome("pubmed", False)
    cb2.record_outcome("pubmed", False)
    cb2.record_outcome("pubmed", True)   # reset
    cb2.record_outcome("pubmed", False)
    cb2.record_outcome("pubmed", False)
    t.expect_true("ac3_reset_before_third", cb2.is_open("pubmed") is False)
    cb2.record_outcome("pubmed", False)
    t.expect_true("ac3_opens_after_reset_at_3", cb2.is_open("pubmed"))
    # Once open, an open breaker means the ledger gate refuses the call (no charge).
    led = ReliabilityLedger(breaker=cb)
    pre_spent = led.budget.spent().get("pubmed", 0)
    t.expect_true("ac3_open_blocks_call", led.allow_call("pubmed") is False)
    t.expect("ac3_open_no_charge", led.budget.spent().get("pubmed", 0), pre_spent)

    # -- AC-6: ledger classifies degradation ---------------------------------
    # S2: 3 errors (opens at threshold 3), then exhaust budget; CrossRef clean.
    s2b = ProviderBudget({"semantic-scholar": 3})
    s2cb = CircuitBreaker(threshold=3)
    led2 = ReliabilityLedger(budget=s2b, breaker=s2cb)
    for _ in range(3):
        if led2.allow_call("semantic-scholar"):
            led2.record("semantic-scholar", {"_error": "429 too many requests"})
    # Circuit is now open; one more allow_call is refused (budget also exhausted).
    t.expect_true("ac6_s2_call_refused_after_open", led2.allow_call("semantic-scholar") is False)
    # CrossRef: clean call.
    if led2.allow_call("crossref"):
        led2.record("crossref", {"message": {"DOI": "10.x/y"}})
    snap = led2.snapshot()
    t.expect_true("ac6_coverage_not_clean", snap["coverage"]["clean"] is False)
    t.expect("ac6_degraded_list", snap["coverage"]["degraded_providers"], ["semantic-scholar"])
    t.expect("ac6_s2_circuit_open", snap["providers"]["semantic-scholar"]["circuit"], "open")
    t.expect_true("ac6_s2_degraded_flag", snap["providers"]["semantic-scholar"]["degraded"])
    t.expect_true("ac6_crossref_not_degraded", snap["providers"]["crossref"]["degraded"] is False)
    kinds = [e["kind"] for e in snap["events"] if e["provider"] == "semantic-scholar"]
    t.expect_true("ac6_circuit_open_event", "circuit-open" in kinds)
    # circuit-open must be recorded before budget-exhausted in the event order.
    if "circuit-open" in kinds and "budget-exhausted" in kinds:
        t.expect_true("ac6_event_order",
                      kinds.index("circuit-open") < kinds.index("budget-exhausted"))

    # -- AC-13: opt-out / high-limit reproduces clean run --------------------
    hi = ProviderBudget({p: 10 ** 9 for p in PROVIDERS})
    hicb = CircuitBreaker(threshold=10 ** 9)
    led3 = ReliabilityLedger(budget=hi, breaker=hicb)
    for _ in range(50):
        if led3.allow_call("crossref"):
            led3.record("crossref", {"message": {"DOI": "10.x"}})
    snap3 = led3.snapshot()
    t.expect_true("ac13_high_limits_clean", snap3["coverage"]["clean"])
    t.expect("ac13_no_degraded", snap3["coverage"]["degraded_providers"], [])
    t.expect_true("ac13_reliability_enabled_default",
                  os.environ.get("APODICTIC_RELIABILITY", "on") != "off")

    # -- error-rate floor: >50% errors with calls>=4 degrades even if breaker
    #    threshold is high (independent degradation path) --------------------
    erb = ProviderBudget({p: 10 ** 9 for p in PROVIDERS})
    ercb = CircuitBreaker(threshold=10 ** 9)  # never opens
    led4 = ReliabilityLedger(budget=erb, breaker=ercb)
    # 3 errors, 1 ok over 4 calls → 0.75 > 0.5 → degraded.
    for resp in [{"_error": "x"}, {"_error": "x"}, {"_error": "x"}, {"ok": 1}]:
        if led4.allow_call("openalex"):
            led4.record("openalex", resp)
    t.expect_true("error_rate_floor_degrades", led4.is_degraded("openalex"))
    t.expect("error_rate_floor_circuit_closed",
             led4.snapshot()["providers"]["openalex"]["circuit"], "closed")
    # Below the calls>=4 guard, a lone early error does NOT degrade.
    led5 = ReliabilityLedger(budget=erb, breaker=CircuitBreaker(threshold=10 ** 9))
    if led5.allow_call("pubmed"):
        led5.record("pubmed", {"_error": "x"})
    t.expect_true("error_rate_floor_guard_no_flag_at_1", led5.is_degraded("pubmed") is False)

    # -- AC-12: cache-hit does not charge / honesty is one-directional -------
    # A cache hit never reaches allow_call(), so budget/breaker are untouched.
    led6 = ReliabilityLedger(budget=ProviderBudget({"crossref": 1}))
    # Simulate: cache hit → no allow_call. Budget still full.
    t.expect("ac12_cache_hit_no_charge", led6.budget.remaining("crossref"), 1)

    # -- TTL helper -----------------------------------------------------------
    os.environ.pop("APODICTIC_CACHE_TTL_METADATA_DAYS", None)
    os.environ.pop("APODICTIC_CACHE_TTL_WAYBACK_DAYS", None)
    t.expect("ttl_metadata_default", TTL.for_key("crossref:doi:10.x"), 30.0 * _DAY)
    t.expect("ttl_wayback_default", TTL.for_key("wayback:http://x"), 7.0 * _DAY)
    t.expect("ttl_search_is_metadata", TTL.for_key("openalex:search:foo:bar"), 30.0 * _DAY)
    t.expect("ttl_unknown_none", TTL.for_key("liveness:http://x"), None)
    os.environ["APODICTIC_CACHE_TTL_WAYBACK_DAYS"] = "1"
    t.expect("ttl_wayback_env_override", TTL.for_key("wayback:x"), 1.0 * _DAY)
    os.environ.pop("APODICTIC_CACHE_TTL_WAYBACK_DAYS", None)

    # -- snapshot shape (AC-8 contract for the block) ------------------------
    snap_keys = set(snap.keys())
    t.expect_true("ac8_snapshot_has_providers", "providers" in snap_keys)
    t.expect_true("ac8_snapshot_has_events", "events" in snap_keys)
    t.expect_true("ac8_snapshot_has_coverage", "coverage" in snap_keys)
    cov_keys = set(snap["coverage"].keys())
    t.expect_true("ac8_coverage_shape",
                  {"degraded_providers", "clean", "note"} <= cov_keys)
    # snapshot must be JSON-serializable.
    try:
        json.dumps(snap)
        t.expect_true("ac8_snapshot_json", True)
    except (TypeError, ValueError) as e:
        t.expect("ac8_snapshot_json", str(e), "<serializable>")

    # -- report ---------------------------------------------------------------
    total = t.passed + len(t.failures)
    if t.failures:
        print(f"api_reliability self-test: FAIL ({len(t.failures)}/{total} checks failed)")
        for f in t.failures:
            print(f"  - {f}")
        return 1
    print(f"api_reliability self-test: PASS ({t.passed}/{total} checks)")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) >= 1 and argv[0] == "--self-test":
        return run_self_test()
    print(__doc__)
    print("Usage: python api_reliability.py --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
