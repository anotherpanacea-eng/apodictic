# Uncertainty-Resolution Intake Interview — disambiguate what the text leaves open

**Status:** **Built (Increment 1), 2026-06-20.** Shipped: the `apodictic.intake_query.v1` schema, the after-Tier-1 interview step in `run-core.md` (interactive-host-gated) + the `core-editor/references/intake-interview.md` module, `scripts/intake_interview.py` + `validate.sh intake-interview` (I1–I4 + W1), and the canonical `example-intake-interview.md` + `example-intake-interview-ledger.md` (one ref-grounded query, one source_note-grounded query) wired into `--check-all` under `--strict`. Self-testable validators 50 → 51. **Build notes:** the validator count is **derived** from `validate.sh`'s `AGG_VALIDATORS` list (not a hand-maintained number); **I3** is implemented as "at least one grounding (a resolving `ambiguity_ref` or a non-empty `source_note`), and a stated-but-dangling `ambiguity_ref` is its own error" — the load-bearing rule is that a query grounded in neither is manufactured; **I4** carries a negation guard so a *negated* mention of suppression (the spec's own recommended "it does not pre-suppress any finding") does not false-fire. Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) "Reconsidered from the boundary," item 18.
<!-- built-when: scripts/intake_interview.py -->

APODICTIC already opens with a substantial intake. It is **not** a blank questionnaire: `run-core.md §Intake Protocol` runs a **draft-then-validate** loop — the framework presents its *inferred* contract ("this is what I infer from the text; please correct any misalignments") and the author confirms or corrects the genre, controlling-idea hypothesis, anti-idea, reader promise, comps, and constraints. The Shelf & Positioning audit separately captures the author's *Intended Shelf* and lane/format gates. So the inferred-vs-intended **contract** is already captured, with the inference shown first.

What no existing surface does systematically is resolve a **specific structural ambiguity the framework detected but cannot settle from the text** — "is the non-linear ordering in Chapters 4–6 a deliberate braid, or drift?" Today the Distinguish framework *guesses* intentionality (lock-then-classify, "no intentionality exemption"). This capability replaces the guess, for detected ambiguities, with a question to the only person who knows: the author. That — and only that — is its job.

## What it is **not** (the scope correction that makes it safe)

The first draft of this spec claimed the interview's safety came from the framework "never asking" for the contract. That is false — the draft-then-validate intake openly asks for controlling idea, reader promise, and genre (showing its inference first). So the discipline is **not** "never ask the contract"; it is **don't duplicate what's already owned, and confine this loop to detected ambiguities only.**

| Already owned by | What it captures | This interview |
|---|---|---|
| `run-core.md §Intake Protocol` (draft-then-validate) | genre, controlling-idea, anti-idea, reader promise, comps | **defers** — never re-asks these |
| Shelf & Positioning Part 0 (Lane Gates) + contract `NON-NEGOTIABLES`/`FORMAT` | audience lane, market posture, format, constraints | **defers** — never re-asks these |
| intake router | draft stage (full / partial / fragments) | **defers** — never re-asks this |
| **— nothing —** | *is this specific detected ambiguity intentional?* | **this interview's sole niche** |

Because the only thing the interview asks is "did you intend this detected feature?", there is **no contract-capture surface in it at all** — every question is a flavor of *intentional-vs-accidental*, structurally (see the closed `kind` enum). That is a real structural guarantee, not the hollow one the first draft claimed.

## The structured artifact

Generated at the parent-orchestrator's after-Pass-0/1 checkpoint (the one seam where the framework knows what's ambiguous and can talk to the author — see §Timing). A `[Project]_Intake_Interview_[runlabel].md` of `apodictic.intake_query.v1` blocks:

```markdown
<!-- apodictic:intake_query
{
  "schema": "apodictic.intake_query.v1",
  "id": "IQ-03",
  "kind": "timeline-order",
  "ambiguity_ref": "F-P2-04",
  "source_note": "",
  "current_inference": "Non-linear ordering across Ch 4-6 reads as possibly unintentional.",
  "confidence": "LOW",
  "question": "Is the non-linear ordering in Chapters 4-6 a deliberate structure?",
  "answer": "Deliberate — a braided timeline.",
  "treat_as_intended": "Pass 2 assesses the braid as intended structure, on its own terms (it does not pre-suppress any finding)."
}
-->
```

- `kind` — a **closed enum, every value a flavor of detected-ambiguity disambiguation**: `timeline-order` / `pov-choice` / `tonal-shift` / `structural-device` / `register-straddle` / `other-detected-ambiguity`. There is deliberately **no** contract/genre/audience/scope kind — those are owned elsewhere, so the enum cannot express a contract ask.
- `ambiguity_ref` — the framework-detected item being disambiguated. **Referential only when the item is a structured `apodictic.finding.v1`** (resolved via `finding_trace`'s ID resolver); otherwise empty.
- `source_note` — a free-prose pointer used **when the ambiguity is not a structured finding** (a Pass-0 observation or an `### Unresolved Questions` bullet — which have *no ID scheme*). Exactly the escape hatch the [Beta-Reader Instrument](beta-reader-instrument.md) uses for ID-less uncertainties; one of `ambiguity_ref`/`source_note` is required (`I3`).
- `current_inference` + `confidence` (∈ HIGH/MEDIUM/LOW/UNCERTAIN, the finding enum) — what the framework currently believes, so the answer corrects a *stated prior*, and a reader can audit the question was genuinely uncertain.
- `treat_as_intended` — how the answer tells analysis to **treat the feature** (assess on its own terms), **never** "suppress the flag/finding" (`I4`).

## Method & severity compliance

- **Defer, don't duplicate (the no-leak rule, honestly stated).** The interview asks only detected-ambiguity questions; contract/audience/scope capture stays with the intake/Shelf/router. `I2` is a **no-duplication** heuristic — it flags a `question` that re-asks a contract element ("what genre", "what's the controlling idea", "what's the reader promise", "who is this for") — and it is **advisory**, because (a) the structural guarantee (no contract `kind`) already does the heavy lifting, and (b) a phrase blocklist is paraphrase-evadable, so claiming it as a hard structural gate would be the over-claim the first draft made. The subset schema engine allows unknown keys unless a schema opts into `additionalProperties:false` (this one does not — it stays open), so the guarantee rests on the **closed `kind` enum + the validator**, not on the schema rejecting fields.
- **Calibrate the lens, never suppress a finding (the Deficit-Lock guard).** There is a real difference between telling analysis to *treat a feature as intended* ("assess the braid on its own terms" — the same genre/intentionality input the framework already uses) and *suppressing a flag class* (removing a verdict before Triage can lock it). The latter is the [author-editor concession loop](../ROADMAP.md#horizon-capacities) (item 16, *not viable*) through the front door. So `treat_as_intended` may direct *how* a feature is assessed; it may **not** pre-empt whether a finding is raised. `I4` flags suppression phrasing ("suppress", "drop the flag", "don't raise") and is an **ERROR by default** — it protects severity honesty, the framework's central value, so it is not left advisory.
- **Answers calibrate analysis, never set severity.** The author supplies *intent*; the framework still reaches and locks the verdict at Triage.

## Timing & execution model

The interview is a **model-judgment loop** (generate targeted questions, interpret free-text answers) — explicitly *unlike* the mechanical, condition-triggered [Adaptive Mid-Run Escalation](../ROADMAP.md#infrastructure) check (counts and booleans). It borrows only that check's **seam**, not its mechanics: it runs at the **parent orchestrator** between Tier 1 and Tier 2, the one point where (a) Pass 0/1 have surfaced the ambiguities, (b) the parent holds the persisted ledger to reference, and (c) a blocking author handshake is safe across single-agent / sequential / hybrid / swarm modes (in multi-agent modes the parent has the ledger, not the subagents' full reasoning, so `current_inference` is drawn from the ledger entry). It runs **only** on interactive-input-capable hosts; on non-interactive hosts the loop is **skipped** and analysis proceeds with the framework's own intentionality inference (the same fallback posture as the Pass-7 POV question). It never blocks a non-interactive run.

## The `intake-interview` validator

`validate.sh intake-interview <run_folder>` resolves the interview artifact + the Findings Ledger. Delegates to `scripts/intake_interview.py`; degrades to advisory `WARN` without `python3`. Report lines namespaced `intake-interview:<ID>`.

| ID | Severity | Rule |
|---|---|---|
| **I1 — schema** | ERROR | Each `intake_query.v1` parses; `kind` ∈ enum; `confidence` ∈ HIGH/MEDIUM/LOW/UNCERTAIN; `current_inference`/`question` present; `id` matches `IQ-NN`. (Subset-engine-validatable.) |
| **I2 — no contract duplication** | WARN (ERROR under `--strict`) | A `question` re-asks a contract element owned by the intake/Shelf (heuristic blocklist: "what genre", "controlling idea", "reader promise", "who is this for"). Advisory — the closed `kind` enum is the structural guard; this catches a leak smuggled into a detected-ambiguity question's wording. Override `<!-- override: intake-dup IQ-NN — <rationale> -->`. |
| **I3 — grounded ambiguity** | ERROR | Each query is grounded by **at least one** of: an `ambiguity_ref` resolving to a real `apodictic.finding.v1` ID, **or** a non-empty `source_note` (for ID-less Pass-0 / Unresolved-Question ambiguities). A query grounded in neither is manufactured. *(As built: a query that **states** an `ambiguity_ref` which does not resolve is its own error — a dangling reference — even if a `source_note` is also present; the broken ref must be fixed. The two grounding paths are the finding-id route and the prose route; in practice exactly one is filled, but supplying both is permitted as long as a stated ref resolves.)* |
| **I4 — calibrate, not suppress (Deficit-Lock guard)** | ERROR | `treat_as_intended` must not contain suppression phrasing ("suppress", "drop/skip the flag", "don't raise", "remove the finding"). It directs assessment, it does not pre-empt a verdict. ERROR by default because it guards severity honesty. |
| **W1 — coverage** | WARN (ERROR under `--strict`) | A Pass-0/1 LOW/UNCERTAIN ambiguity (scanned from the structured findings **and** the free-prose `### Unresolved Questions` section) that only the author could resolve has no query. Advisory: a focused interview is legitimate. |

**Ownership boundary.** `intake-interview` owns the **detected-ambiguity disambiguation contract**: the no-contract-duplication heuristic, grounded ambiguity, and the calibrate-not-suppress guard — classes no other validator raises. It does **not** capture the contract (the draft-then-validate intake does), capture audience/format (Shelf Part 0 / the contract fields do), run passes, or set severities (analysis does). It is the author-facing sibling of [Beta-Reader Instrument Generation](beta-reader-instrument.md): both turn framework uncertainties into questions — that asks *readers*, this asks the *author* — and both are barred from using the answers to soften a verdict.

## Canonical `--check-all` gate

A worked example — a fixture with a structured `F-P2-04` timeline-ambiguity finding plus an `intake_query.v1` disambiguating it (`kind: timeline-order`, `ambiguity_ref` resolving to the finding, `treat_as_intended` phrased as assessment-direction), and a second query grounded by `source_note` in an `### Unresolved Questions` bullet — is added, and `validate.sh --check-all` runs `intake-interview` against it: proving grounded ambiguity via both paths (`I3`), a clean no-duplication scan (`I2`), and a clean calibrate-not-suppress check (`I4`). It includes two **negatives**: a query re-asking "what is the controlling idea?" (fails `I2` under `--strict`) and a `treat_as_intended` saying "suppress the timeline-drift flag" (fails `I4`). (The "canonical-framework validator runs as release gate" discipline, `ROADMAP.md` §Deferred.)

## Increment plan

**Increment 1 (this spec):** the `apodictic.intake_query.v1` schema (added to `schemas/`, auto-discovered by `known_schema_ids()`), the after-Pass-0/1 interview step (interactive-host-gated, parent-orchestrated, deferring all contract/audience/scope capture to existing surfaces), `scripts/intake_interview.py` + `validate.sh intake-interview`, the worked example, and the `--check-all` gate (run under `--strict`). Adds one validator — registered by appending `intake-interview` to `validate.sh`'s `AGG_VALIDATORS` list (the count is **derived** from that list via `AGG_COUNT`, not a hand-maintained number; 50 → 51) and to the `Commands:` line.

**Future increments (not built):**
- **Answer-driven re-routing automation** — wire `treat_as_intended` outcomes into the runner (a Runner-Governed Execution concern); Increment 1 records the calibration, the analyst applies it.
- **Confidence-ranked question budget** — when many ambiguities exist, ask only the top-N by confidence-gain, to avoid over-interviewing.
- **Shared harvest with Beta-Reader Instruments** — one uncertainty scan, routed two ways: author-resolvable → intake query; reader-resolvable → reader question.

## Self-review (Increment 1)

- *Why the scope had to narrow* — the first draft's safety rested on "the framework never asks the contract," which `run-core.md`'s draft-then-validate intake contradicts. Narrowing the interview to *detected-ambiguity disambiguation* (a niche genuinely owned by nothing) makes the no-leak guarantee structural (the `kind` enum has no contract value) instead of rhetorical, and removes the overlap with the intake / Shelf Part 0 / router that the other proposed kinds had.
- *Why `source_note` is mandatory alongside `ambiguity_ref`* — the ambiguities the interview most needs to reference (LOW/UNCERTAIN Pass-0 observations, Unresolved-Questions bullets) frequently have no structured `F-…` ID (structured blocks are required only for synthesis-bound Must/Should-Fix findings), so a referential-only check would be unsatisfiable. This mirrors the Beta-Reader Instrument's identical fix.
- *Why I4 is an ERROR and "treat_as_intended" replaces "suppress"* — "suppress a flag class" removes a verdict before the Deficit Lock can see it — the concession loop in disguise. Forbidding suppression phrasing and making it a hard gate keeps the author supplying *intent* while the framework keeps reaching the *verdict*.
- *Why no "revival" claim* — there is no evidence in the codebase of a removed fuller intake to revive, and the current intake is already extensive; this is a *new, narrow* loop on top of it, and the spec says so rather than inventing a lineage.
