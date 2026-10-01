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
        # A provider is ENGAGED if a call fired, its breaker forced open, OR a budget-exhausted
        # event fired — allow_call() records `budget-exhausted` when the provider's budget was
        # spent BEFORE any call could fire, which cuts an unresolved citation to NOT-CHECKED. The
        # bare _calls/breaker touched-set missed that path, so a budget-exhausted-only provider was
        # classified _degraded() yet dropped from coverage (and thus from the OQ-1 strict halt).
        exhausted_evt = {ev["provider"] for ev in self._events if ev["kind"] == "budget-exhausted"}

        def _engaged(p):
            return p in self._calls or self.breaker.is_open(p) or p in exhausted_evt

        seen = set(self._calls) | set(self.breaker.state()) | set(self.budget.spent()) | exhausted_evt
        touched = [p for p in PROVIDERS if _engaged(p)]
        touched += [p for p in seen if p not in PROVIDERS and _engaged(p)]
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
# OQ-1 — strict-mode halt on a degraded high-stakes run
# ---------------------------------------------------------------------------

# Exit code the CLI uses to signal a strict high-stakes HALT. Distinct from
# argparse's usage exit (2) and a generic error (1) so a wrapper can tell a
# degraded-coverage halt from a parse/other error. Additive: only ever returned
# when the caller opted into --strict AND coverage was genuinely degraded.
STRICT_HALT_EXIT_CODE = 3


def strict_halt_decision(snapshot, not_checked_count, *, strict: bool) -> dict:
    """Decide whether a strict high-stakes run must HALT on degraded coverage (OQ-1).

    A high-stakes run (Citation Verifier / Field Reconnaissance) opts in by
    setting `strict=True`; that flag IS the caller's high-stakes declaration.
    The halt fires iff ALL THREE hold:

      1. strict is enabled,
      2. coverage is DEGRADED — the ledger snapshot lists >= 1 degraded provider
         (`snapshot["coverage"]["degraded_providers"]` is non-empty), and
      3. >= 1 result was NOT-CHECKED — `not_checked_count > 0` — meaning a
         degraded provider was actually on some unresolved citation's path and
         cut it short (the batch summary's `not_checked` count).

    Condition (3) is what makes the halt ONE-DIRECTIONAL and honest, matching the
    per-result rule in research-citation-verifier.md (NOT-CHECKED is set only when
    a degraded provider was on *that* citation's path):

      * a CLEAN run (no degraded providers) never halts;
      * a genuine all-healthy NOT-FOUND never halts — with no degraded provider,
        or with `not_checked_count == 0`, an unresolved citation is NOT-FOUND, not
        NOT-CHECKED, so degradation that never blocked a lookup cannot manufacture
        a halt.

    Returns a JSON-serializable dict (embedded under the reliability block's
    `strict` key when strict is on; never mutates the ledger):
      {"enabled", "halt", "reason", "degraded_providers", "not_checked"}.
    """
    coverage = {}
    if isinstance(snapshot, dict):
        cov = snapshot.get("coverage")
        if isinstance(cov, dict):
            coverage = cov
    degraded = list(coverage.get("degraded_providers", []) or [])
    nc = int(not_checked_count or 0)
    halt = bool(strict) and bool(degraded) and nc > 0
    if halt:
        reason = (
            "STRICT HALT: degraded provider coverage on a high-stakes run — "
            f"{', '.join(degraded)} degraded and {nc} citation(s) NOT-CHECKED "
            "(could not be looked up); refusing to emit a degraded verdict as a "
            "clean not-found. Route to run-synthesis Blind Spot / Absence Inventory."
        )
    else:
        reason = None
    return {
        "enabled": bool(strict),
        "halt": halt,
        "reason": reason,
        "degraded_providers": degraded,
        "not_checked": nc,
    }


# ---------------------------------------------------------------------------
# OQ-3 — Citation_Reliability.json sidecar
# ---------------------------------------------------------------------------

CITATION_RELIABILITY_FILENAME = "Citation_Reliability.json"
CITATION_RELIABILITY_SCHEMA = "apodictic.citation_reliability.v1"


def build_reliability_sidecar(ledger, resolution_summary=None,
                              strict_decision=None) -> dict:
    """Pure serializer for the Citation_Reliability.json sidecar (OQ-3).

    Assembles a deterministic, stdlib-JSON-serializable payload from a
    `ReliabilityLedger` plus the batch's resolution summary and (optionally) the
    strict-halt decision. It records: per-provider **budget spent**, **circuit
    states** (raw failure counts + open flags), the **coverage /
    degraded_providers** block, the per-provider snapshot, the event log, and the
    **resolved / not_found / not_checked** resolution summary.

    ADDITIVE and side-effect-free: it READS the ledger (snapshot/budget/breaker),
    never mutates it, and does NOT alter the in-`output` `reliability` block
    (which stays `ledger.snapshot()`). Callable with no disk access, so the
    self-test can assert the JSON shape directly."""
    if ledger is not None:
        snap = ledger.snapshot()
        budget_spent = dict(ledger.budget.spent())
        circuits = dict(ledger.breaker.state())
    else:
        snap = {"providers": {}, "events": [],
                "coverage": {"degraded_providers": [], "clean": True, "note": ""}}
        budget_spent = {}
        circuits = {}
    summary = dict(resolution_summary or {})
    resolution = {
        "total": int(summary.get("total", 0)),
        "resolved": int(summary.get("resolved", 0)),
        "not_found": int(summary.get("not_found", 0)),
        "not_checked": int(summary.get("not_checked", 0)),
        "unretrievable": int(summary.get("unretrievable", 0)),
    }
    payload = {
        "schema": CITATION_RELIABILITY_SCHEMA,
        "coverage": dict(snap.get("coverage", {})),
        "providers": dict(snap.get("providers", {})),
        "budget_spent": budget_spent,
        "circuits": circuits,
        "events": list(snap.get("events", [])),
        "resolution_summary": resolution,
    }
    if strict_decision is not None:
        payload["strict"] = dict(strict_decision)
    return payload


def sidecar_json(payload: dict) -> str:
    """Canonical deterministic serialization of a sidecar payload (sorted keys,
    stdlib json). The single source of the on-disk bytes so the self-test can
    assert byte-determinism without touching disk."""
    return json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n"


def write_reliability_sidecar(target, ledger, resolution_summary=None,
                              strict_decision=None) -> str:
    """Write the Citation_Reliability.json sidecar (OQ-3) and return its path.

    `target` may be a directory (the file is written as Citation_Reliability.json
    inside it) or an explicit `*.json` path. Deterministic key order, stdlib json.
    Purely additive: writing the sidecar does not touch the batch `output` or the
    in-`output` reliability block; it is opt-in at the call site."""
    p = str(target)
    path = p if p.endswith(".json") else os.path.join(p, CITATION_RELIABILITY_FILENAME)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    payload = build_reliability_sidecar(ledger, resolution_summary, strict_decision)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(sidecar_json(payload))
    return path


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

    # -- OQ-1: strict-mode halt on a degraded high-stakes run -----------------
    # `snap` (AC-6) is a DEGRADED snapshot: coverage.degraded_providers ==
    # ["semantic-scholar"]. `snap3` (AC-13) is a CLEAN snapshot: [].
    deg_snap, clean_snap = snap, snap3
    # (a) degraded high-stakes run under strict + a not-checked citation → HALTS.
    d_a = strict_halt_decision(deg_snap, not_checked_count=2, strict=True)
    t.expect_true("oq1_a_strict_degraded_halts", d_a["halt"] is True)
    t.expect_true("oq1_a_halt_has_reason", bool(d_a["reason"]))
    t.expect("oq1_a_degraded_named", d_a["degraded_providers"], ["semantic-scholar"])
    t.expect("oq1_a_not_checked_echoed", d_a["not_checked"], 2)
    # (b) the SAME degraded run NON-strict → does NOT halt (default preserved).
    d_b = strict_halt_decision(deg_snap, not_checked_count=2, strict=False)
    t.expect_true("oq1_b_nonstrict_no_halt", d_b["halt"] is False)
    t.expect_true("oq1_b_reason_none", d_b["reason"] is None)
    t.expect_true("oq1_b_enabled_false", d_b["enabled"] is False)
    # (c) a CLEAN / all-healthy run under strict → does NOT halt.
    d_c = strict_halt_decision(clean_snap, not_checked_count=0, strict=True)
    t.expect_true("oq1_c_clean_strict_no_halt", d_c["halt"] is False)
    t.expect_true("oq1_c_enabled_true", d_c["enabled"] is True)
    # (d) a genuine all-healthy NOT-FOUND under strict → does NOT halt
    #     (no degraded provider, not_checked == 0: NOT-FOUND is not NOT-CHECKED).
    d_d = strict_halt_decision(clean_snap, not_checked_count=0, strict=True)
    t.expect_true("oq1_d_healthy_notfound_no_halt", d_d["halt"] is False)
    # one-directional guard: degraded providers present but not_checked == 0
    # (degradation never blocked a lookup) → still NO halt.
    d_guard = strict_halt_decision(deg_snap, not_checked_count=0, strict=True)
    t.expect_true("oq1_guard_degraded_no_notchecked_no_halt", d_guard["halt"] is False)
    # a None/empty snapshot never fabricates a halt.
    t.expect_true("oq1_none_snapshot_no_halt",
                  strict_halt_decision(None, 5, strict=True)["halt"] is False)
    # regression (PR #168 review): a provider budget-EXHAUSTED BEFORE any call fires records a
    # budget-exhausted event and cuts a citation to NOT-CHECKED, but the bare _calls/breaker
    # touched-set dropped it from coverage — so --strict silently did NOT halt. Coverage must now
    # list it degraded and the strict halt must fire.
    be_led = ReliabilityLedger(budget=ProviderBudget(limits={"semantic-scholar": 0}))
    be_led.allow_call("semantic-scholar")   # False: exhausted before any call; event recorded
    be_snap = be_led.snapshot()
    t.expect("oq1_budget_exhausted_coverage_degraded",
             be_snap["coverage"]["degraded_providers"], ["semantic-scholar"])
    t.expect_true("oq1_budget_exhausted_not_clean", be_snap["coverage"]["clean"] is False)
    t.expect_true("oq1_budget_exhausted_strict_halts",
                  strict_halt_decision(be_snap, not_checked_count=1, strict=True)["halt"] is True)
    # but a truly UNUSED zero-budget provider (never engaged, no event) stays clean — no over-report.
    unused_led = ReliabilityLedger(budget=ProviderBudget(limits={"semantic-scholar": 0}))
    t.expect("oq1_unused_zero_budget_clean",
             unused_led.snapshot()["coverage"]["degraded_providers"], [])

    # -- OQ-3: Citation_Reliability.json sidecar serializer -------------------
    import tempfile
    sc_summary = {"total": 5, "resolved": 2, "not_found": 1, "not_checked": 2,
                  "unretrievable": 3}
    payload = build_reliability_sidecar(led2, sc_summary, d_a)
    # (e) expected keys + values.
    t.expect("oq3_sidecar_schema", payload.get("schema"), CITATION_RELIABILITY_SCHEMA)
    for k in ("schema", "coverage", "providers", "budget_spent", "circuits",
              "events", "resolution_summary", "strict"):
        t.expect_true(f"oq3_sidecar_has_{k}", k in payload)
    t.expect("oq3_sidecar_resolution_not_checked",
             payload["resolution_summary"]["not_checked"], 2)
    t.expect("oq3_sidecar_resolution_not_found",
             payload["resolution_summary"]["not_found"], 1)
    t.expect("oq3_sidecar_coverage_degraded",
             payload["coverage"]["degraded_providers"], ["semantic-scholar"])
    t.expect_true("oq3_sidecar_budget_spent_s2",
                  payload["budget_spent"].get("semantic-scholar", 0) >= 3)
    t.expect("oq3_sidecar_circuit_open_recorded",
             payload["circuits"].get("semantic-scholar", {}).get("open"), True)
    t.expect_true("oq3_sidecar_strict_halt", payload["strict"]["halt"] is True)
    # a sidecar built WITHOUT a strict decision omits the strict key (additive).
    payload_ns = build_reliability_sidecar(led2, sc_summary, None)
    t.expect_true("oq3_sidecar_no_strict_key_when_none", "strict" not in payload_ns)
    # (f) deterministic serialization + JSON round-trip / schema.
    s1 = sidecar_json(payload)
    s2 = sidecar_json(build_reliability_sidecar(led2, sc_summary, d_a))
    t.expect_true("oq3_sidecar_deterministic", s1 == s2)
    rt = json.loads(s1)
    t.expect("oq3_sidecar_roundtrip_schema", rt.get("schema"), CITATION_RELIABILITY_SCHEMA)
    t.expect("oq3_sidecar_roundtrip_not_checked",
             rt["resolution_summary"]["not_checked"], 2)
    # writer round-trips to disk identically to the pure serializer.
    with tempfile.TemporaryDirectory() as _d:
        wpath = write_reliability_sidecar(_d, led2, sc_summary, d_a)
        t.expect_true("oq3_sidecar_writes_named_file",
                      wpath.endswith(CITATION_RELIABILITY_FILENAME))
        with open(wpath, encoding="utf-8") as _fh:
            disk = json.loads(_fh.read())
        t.expect("oq3_sidecar_disk_matches_pure", disk, rt)

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
