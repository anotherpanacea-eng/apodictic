# Cost-Floor Dispatch Override

## Problem

APODICTIC's dispatch is quality-maximizing: `final mode = max(token-fit-floor, quality-risk-escalation)` (run-core.md §Execution Protocol step 3c). The token-fit floor alone sends a standard-context (<1M) user with a >100K-word manuscript to swarm (~5× nominal, ~8.5× measured end-to-end on the 2026-06 pilot) and 60–100K to hybrid — **regardless of the user's usage budget.** The existing override channel (`quality_risk_override` + the `<!-- override: quality-risk-Q[1-5] — … -->` marker family) only *declines an upward escalation*; nothing let a cost-constrained user cap the run *below* the token-fit floor at the cheapest load-viable mode with honest tradeoff disclosure. The demand signal was already instrumented — `dispatch_record.py --report` counts budget-flavored `quality_risk_override` rationales — and run-core itself names "budget constraint" as a legitimate override reason.

## Mechanism

A first-class, **user-declared** cap (never inferred from a plan/tier/usage-window sniff):

- **Marker family** — `<!-- override: cost-floor-<mode> — <rationale> -->`, `<mode> ∈ {single-agent, sequential, hybrid}` (three exact slugs; no `cost-floor-swarm` — swarm is the ceiling; a bare `cost-floor` marker is an error). Read via the shared `override_marker` SSoT (suffix-collision + code-span-decoy hardened).
- **Run-metadata token** — `cost_floor_override: <mode>[; context_tier: standard|large] — <rationale>`, a field-read sibling of `quality_risk_override`. `context_tier` is required only for a single-agent cap and is **declared, not platform-verified** (like `dispatch_log` provenance — bash cannot observe the true host window).
- **Decision rule** — Execution Protocol step 3 gains **(d)**: `final = min( max(token-fit-floor, RAW-quality-risk-target), cost_cap )`. The cap composes over the **RAW** fired-trigger target (the one `quality-risk-triggers` surfaces even when a QRO marker is present), not the post-QRO decline-to-floor value — composing over the post-QRO value would make a cap strictly between floor and Q-target unreachable. While a lower cap is active, QRO's decline-to-floor precedence is **suspended** and the paired `quality-risk-Q[n]` marker (CF4) is the named acknowledgment for demoting past a fired trigger.
- **Per-mode cost estimate** — `preflight.sh` prints a `## Per-Mode Token Cost Estimate` section (single-agent overhead-loaded · sequential ×3 · hybrid ×4 · swarm ×7 of the bare manuscript-token estimate) so the user sees the numbers before choosing. Order-of-magnitude budget signals, **not ratio-comparable**.
- **Intake-router front door** — a §2b below-floor mode pick is recorded as the *same* `cost_floor_override` artifact and routed through this gate, so there is no informal below-floor affordance that escapes the validator.

No new schema: the artifacts are a marker + a metadata token, validated by the `cost-floor` arm directly. No dependency on the unbuilt Runner-Governed orchestrator API.

## The four validator predicates (CF1–CF4)

`scripts/validate.sh cost-floor <contract_or_run_metadata_file> [<preflight_packet>] [<meta_json>] [--strict]`:

- **CF1 — marker integrity (bidirectional).** Scan the three slugs via `override_marker`; scan the token via `_CFO_TOKEN_RE` over `strip_code_spans` output. Zero markers AND zero live tokens → inert PASS. More than one distinct mode slug → ERROR (conflicting caps). Empty rationale → ERROR. A bare/unsuffixed `cost-floor` marker → ERROR. **Reverse orphan-token check** (DP2.5 precedent): a live token with NO matching live marker → WARN by default, ERROR under `--strict`.
- **CF2 — marker↔token sync (forward).** When a live marker exists, the token must be present (code-span stripped) and its mode must equal the marker's. Missing/mismatched → ERROR.
- **CF3 — viability bound (single-agent).** A single-agent cap must declare `context_tier: large` (`standard` or absent → ERROR) AND its **mandatory** preflight packet's `Estimated single-agent load` must be < 600K (packet absent, or load ≥ 600K → ERROR). Sequential/hybrid carry no context/load requirement, but a sequential/hybrid cap below the packet's own token-fit floor → below-floor WARN.
- **CF4 — no silent quality-risk demotion.** Recompute fired Q1–Q5 from artifacts via the shared `_fired_triggers` enumerator (the 7085daa rule — never trust a recorded field). Every fired trigger whose per-trigger target exceeds the cap (order single-agent < sequential < hybrid < swarm) requires the matching `quality-risk-Q[n]` marker; missing → ERROR naming the trigger. When the optional meta sidecar is withheld and the cap is below swarm, Q4's meta branch is unevaluable → WARN (CF4-unevaluable).

Degraded path (no `python3`): WARN-skip with an inline checklist — the arm composes marker scanning + token grammar + trigger recomputation, and a second bash implementation is a drift surface, so no bash port is shipped.

## Disclosure contract (three mandatory parts)

Before dispatch under a cap, run-core scripts the disclosure: (1) **the numbers** — the per-mode preflight estimates for at least the capped and displaced modes plus the ~8.5×-measured gap; (2) **the named trade, typed correctly** — *safety* (compaction / late-pass salience) when below the token-fit floor, *quality* (the named Q-trigger's isolation forgone, requiring the paired Q[n] override) when it demotes a fired quality-risk target; (3) **honest framing of what swarm buys** — verification isolation + tighter severity banding, NOT "2× deeper analysis," carrying the eval doc's hedges verbatim in spirit: **directional, single-fixture N=1, not a verdict**.

## CR-6 detectability (the report line)

`dispatch_record.py --report` counts `cost_floor_override` records (marker form via `override_payloads` over the three slugs; token form via `_CFO_TOKEN_RE`, code-span stripped) and prints a `cost_floor_override records:` line. Nothing else reads these records across runs; without the line a recorded cap would be recorded-but-invisible. Report only — gates nothing.

## Relation to adaptive-mode-escalation's mid-run seam

The two mode-change mechanisms sit on **different axes and never collide**:

- **This feature** is a **dispatch-time, user-DECLARED** cap, set once at dispatch.
- **adaptive-mode-escalation**'s Mid-Run Escalation Check is an **automatic, complexity-gated** de-escalation that floors at `sequential` and runs once after Tier 1.

A recorded cost cap does not suppress the mid-run checkpoint's recommendation — it is surfaced with the cap noted, and switching above the cap requires the author to explicitly lift it (supersede the marker + token). Every path stays author-confirmed; no path is silent.

## What a passing `cost-floor` arm certifies — and what it does NOT

**Certifies:**
- Marker/record integrity — a well-formed cap carries both the mode-suffixed marker and the matching token, with a non-empty rationale and no conflicting dual-mode caps.
- **Bidirectional sync** — neither half is orphaned (marker without token → CF2 ERROR; token without marker → CF1 WARN/`--strict`-ERROR).
- **CF4 marker coverage** — every fired quality-risk trigger whose target exceeds the cap carries its own `quality-risk-Q[n]` override marker (a cost cap cannot silently demote a fired quality-risk decision).
- **Single-agent context-tier + load bound** — a single-agent cap declares `context_tier: large` and its mandatory preflight packet reports an estimated single-agent load < 600K.

**Does NOT certify:**
- That the three-part **disclosure actually occurred** — the disclosure is a run-core *instruction*, not a mechanical gate; a run with the records present but the disclosure skipped is not caught (the validator cannot observe whether the disclosure was shown). This split is deliberate and stated honestly rather than overclaimed.
- That the host is **truly ≥1M-context** — `context_tier` is a *declared* token (like `dispatch_log` provenance), gated for presence + consistency, never platform-verified.
- That a below-floor **sequential/hybrid cap is safe** — the below-floor WARN surfaces the compaction/salience trade; it does not bless it. The point of the feature is user agency over budget, with the honest cost stated, not forbidden.

## Out of scope

The powered swarm-vs-single eval harness (`docs/swarm-vs-single-eval.md` — this feature *consumes* its cost-evidence framing, builds none of it); any runner-governed orchestrator API; automatic budget detection; re-tuning the token-fit tiers or quality-risk triggers (the `_fired_triggers` extraction is behavior-preserving); mid-run cost-based de-escalation; real-dollar cost estimates (token figures only).

**Status:** built at merge.
