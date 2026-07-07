# Model-Capacity Exploitation — M1: Dispatch Observability

**Status:** M1 (`dispatch_log` sidecar object + `dispatch-record` validator + `--report`) — **built**. M2 (pre-registered tier experiment) and M3 (contract-time advisory allocation) are **gated / not built** — see §M-split. Roadmap: `ROADMAP.md` → Harness Engineering → Model-Capacity Exploitation. Implementation: `scripts/dispatch_record.py`, `validate.sh dispatch-record`, `run-core.md §Execution Protocol` (steps 7, 10), the `dispatch_log` property on `apodictic.diagnostic-state.v1`.

## The scoping verdict (observability-first)

The roadmap sentence is "plan model and compute allocation up front from the contract and uncertainty profile." Half of it already shipped — the **compute** half (the preflight token-fit floor, the Quality-Risk Q1–Q5 overlay, the escalation/de-escalation checkpoint, and long-context re-grounding). What is genuinely unbuilt is the **model-tier** half — and the repo's own scorecards show **no measured tier differential** (synthetic-controls, cross-vendor, and swarm-vs-single evals all trend flat-or-mildly-against more capacity buying more findings). An allocator without differential-value evidence is speculation, and the repo default is build-nothing-without-a-forcing-function.

So v1 builds the one thing that makes a *later* allocation decision **measurable**, and nothing that pretends to make it now: a record of **which model each dispatched step was issued to**. Every other outcome signal a future allocator needs — per-pass finding counts, confidence/severity distributions, counterevidence presence, refutation survival, coverage degrades, escalation state — is already on disk per run. The one field missing is the join key: model identity per dispatch. M1 closes exactly that gap. No allocator ships in v1.

## What is controllable (the narrow lever)

The framework never calls model APIs; the host does. Per-pass model assignment is real only where the delegated-agent facility takes a model parameter (the Claude Code Task tool's `model:` parameter). Everywhere else "allocation" can only be advisory prose, and mid-conversation parent model switching does not exist on any host. The **recording layer (M1) is host-neutral** — the model-tag table already covers every host's tags. The **control lever (M3, if ever) is Claude-Code-class only**.

## The record: `dispatch_log`

An additive array on `apodictic.diagnostic-state.v1`, following the `complexity_signals` / `synthesis_coverage` precedent (no new schema file, no version bump). The parent appends one entry at the moment it issues each delegated-agent dispatch (Execution Protocol steps 7 and 10):

```jsonc
"dispatch_log": [
  { "seq": 1, "step": "pass0+1",  "model_tag": "opus46",   "execution_mode": "hybrid", "max_turns": 32,   "provenance": "dispatch-derived" },
  { "seq": 2, "step": "pass5",    "model_tag": "sonnet46", "execution_mode": "hybrid", "max_turns": null, "provenance": "dispatch-derived" },
  { "seq": 3, "step": "synthesis","model_tag": "opus46",   "execution_mode": "hybrid", "max_turns": null, "provenance": "dispatch-derived" }
]
```

### Step vocabulary — v1 grammar

`pass<N>`, `pass0+1` (the combined triage subagent, `run-core.md` §Pass grouping), `synthesis`, and `all-passes` (single-agent's one subagent). These are exactly the step kinds M1's two recording sentences create (steps 7 and 10). **Deferred extension (stated, not wired):** `audit:<audit-id>`, `prerequisite:<audit-id>`, and `refutation` need recording sentences at seams M1 does not touch; they extend the grammar when those sites are wired. A host that opportunistically records a deferred-extension id is **recorded-but-not-reconciled** (R2 ignores it, R4 shape-checks its fields). Any step id outside both sets is an unknown step kind (R4 WARN).

### Provenance honesty — the pinned rule

`dispatch-derived` = the parent appended this entry at the moment it issued a delegated-agent dispatch — legitimate in **any** mode on a dispatch-capable host, including single-agent's one subagent. **It attests the dispatch *instruction* — the model parameter the parent requested — and is `parent-requested, not platform-verified`: no host API attests which model actually served the subagent.** This is deliberately *weaker* than `synthesis_coverage`'s dispatch-derived manifest (whose rows are checkable file paths, reconciled by its V2–V4); `dispatch_log` has no equivalent reconciliation substrate, and neither this doc nor the validator claims one.

`declared` = a step that ran inline in the recording context with no dispatch event (no-shell hosts, or a genuinely inline step). Provenance tracks the **host's per-entry dispatch capability, not the run's mode** — a no-shell host legitimately records all-`declared` entries under `execution_mode: sequential`.

**Facts, not classifications.** The log records the model **tag**, never a "tier" label — the tier↔model mapping is a judgment that changes as models improve and belongs in the future M3 spec, not the durable record. Every consumer of `dispatch_log` (prose, `--report`, future M2/M3) must carry the "parent-requested, not platform-verified" qualifier when relying on `dispatch-derived` entries.

## The validator: `validate.sh dispatch-record <run_folder> [--strict]`

`scripts/dispatch_record.py` behind a thin dispatcher arm (no new bash-regex validators; the bash degrade path is an advisory WARN without `python3`). Mirrored byte-identical in `plugins/apodictic/scripts/`.

- **R1 (presence — advisory-first):** a run folder with pass artifacts should carry a `dispatch_log` with ≥1 entry. **Grandfather:** the key being **absent** is the pre-adoption marker (silent PASS — the field's absence is the grandfather marker); a present-but-**empty** `[]` is a post-adoption recording failure that fires (WARN default / FAIL `--strict`).
- **R2 (coverage — bidirectional with asymmetry):** the denominator is the pass-artifact glob family (`_Pass[N]_`) plus the synthesis-letter globs (`*_Core_DE_Synthesis_*` / `*_Full_DE_Synthesis_*` — the detection the annotated-manuscript offer uses). **Satisfaction map:** `pass<N>` → Pass N; `pass0+1` → **both** Pass 0 and Pass 1; `all-passes` → every pass artifact (and is **exclusive** — may not coexist with `pass<N>` / `pass0+1`); `synthesis` → the letter. Deferred-extension ids are recorded-but-not-reconciled. **Direction asymmetry:** an enumerated artifact with no satisfying entry = FAIL under `--strict`, WARN otherwise (the record can't shrink); an entry with no matching artifact = WARN, never FAIL (a dispatched-then-failed subagent is a legitimate, informative record). dispatch-record **consumes** `artifact-names`' enumeration; filename grammar stays `artifact-names`' concern.
- **R3 (tag vocabulary):** `model_tag` must appear in the model-tag table parsed from `output-structure.md` (SSoT-by-reference — never a hardcoded constant), **or be the literal `unknown`, a sanctioned PASS** (the documented derivation fallback — punishing it would teach hosts to invent tags). Any other unknown tag = WARN naming the table as the fix. **Fail-loud floor:** a zero-row table parse exits 2 (`model-tag-table-unparseable`) — never a vacuous accept-everything.
- **R4 (shape — per entry):** `execution_mode` ∈ {single-agent, sequential, hybrid, swarm}; `provenance` ∈ {dispatch-derived, declared}; `seq` strictly increasing; malformed / missing-field / bad-enum / duplicate-seq = FAIL; unknown step kind = WARN. **No mode-based provenance FAIL** — provenance is per-entry host-capability, not run mode.
- **R5 (escalation reconciliation — WARN-first):** using only the log + `last_session.execution_mode` (updated on a confirmed switch): (a) the `execution_mode` values in `seq` order may change **at most once** (the Mid-Run Escalation Check runs once, at the Tier-1→Tier-2 seam — a thrashing log is flagged); (b) when `last_session.execution_mode` is present, the **final** entry's mode must equal it (a stale post-escalation entry is flagged). `--strict` promotes.

### `--report <project_dir>` (read-only, cross-run)

Scans the project's run folders and sidecars and prints, without gating anything: runs scanned; per-model-tag dispatch tallies; and the **M2 demand-signal line** — the count of `quality_risk_override` records (`run-core.md` §Override path; the override-marker form matched via the shared `override_marker` helper, the token form read from run metadata) and how many carry a budget-flavored rationale. Nothing else reads `quality_risk_override` across runs; without `--report` the M2 trigger would be recorded-but-invisible (the condition-triggered-detectability discipline — a trigger no one can mechanically see fires for no one).

## Posture (allocation is never a verdict)

- **Allocation rationale may reference only pipeline mechanics** (word/token counts, POV count, mode, stakes tier, context fit). Banned frame: any wording where the model choice grades the manuscript. Required frame for any future advisory surface: *"Model allocation is a cost/robustness decision about the pipeline, not an assessment of the manuscript."*
- **The editorial letter never discusses model allocation.** Provenance lives in the sidecar, the runlabel, and the Run Archive table — model identity per pass is provenance, not epistemics, and a per-pass model table in the letter would invite re-weighing findings by model prestige.
- **Frontier floor:** triage (Pass 0+1), synthesis, and the adversarial stress test are never candidates for downtiering in any future allocation work — wasted tokens are recoverable, wrong analysis is not.
- **No-telemetry:** `dispatch_log` is per-project, local, inside the sidecar that already exists. No aggregation service, no upload, no cross-project harvesting (`--report` reads one operator-named project directory, locally). A *learned* allocator would have nothing to train on beyond the operator's own machine — so M3, if it ever ships, ships documented heuristics with cited local evidence, never learned weights.

## M-split

| M | What | Gate |
|---|---|---|
| **M1** | `dispatch_log` + `dispatch-record` + `--report` + prose (this build) | built |
| **M2** | Pre-registered tier experiment (§Tiered Model Assignment Testing Protocol, run under swarm-pilot discipline): analytical passes at sonnet-tier vs the all-frontier baseline; metrics incl. counterevidence rate (≥75% vs 92% baseline). | **Trigger:** a real cost forcing function — operator budget pressure, or the `dispatch-record --report` demand-signal line showing repeated budget-rationale `quality_risk_override` records. Eval-shaped, not a framework PR. |
| **M3** | Contract-time advisory allocation plan (per-pass tier recommendation; frontier floor; author-confirmed; Claude-Code-class hosts only, prose elsewhere). | **Gated on M2 showing differential value.** Own spec, own /spec-review. |

## What M1 does not touch

§Pre-Pass Re-Grounding, §Mid-Run Escalation Check, `escalation_check.py`, `synthesis_coverage.py`, `specificity_floor.py`, the editorial letter surface, and the pass-filename / runlabel grammar. `run-core.md` gains recording sentences only — zero behavioral change to mode selection, dispatch order, escalation, re-grounding, or synthesis.
