# Uncertainty-Resolution Intake Interview — disambiguate what the text leaves open

*Reference module for the APODICTIC Core Editor. A narrow, optional loop on top of the existing
intake: at the after-Pass-0/1 checkpoint it asks the author to resolve a **specific structural
ambiguity the framework detected but cannot settle from the text** — and only that. Spec + validator:
`docs/uncertainty-intake-interview.md`, `scripts/validate.sh intake-interview`. Worked example:
`example-intake-interview.md` (paired with `example-intake-interview-ledger.md`).*

---

## When to use

After **Tier 1** (Pass 0 Structure Map + Pass 1 Reader Orientation), at the same checkpoint as the
[Mid-Run Escalation Check](run-core.md#mid-run-escalation-check-required-runs-once-after-tier-1) — the
one seam where the framework has surfaced the ambiguities, holds the persisted Findings Ledger, and
can safely block for an author handshake across all execution modes. Runs **only** on
interactive-input-capable hosts; on a non-interactive host the loop is **skipped** and analysis
proceeds with the framework's own intentionality inference (the same fallback posture as the Pass-7
POV question). It never blocks a non-interactive run.

## What it is — and is not

APODICTIC already opens with a substantial **draft-then-validate** intake (`run-core.md §Intake
Protocol` shows its inferred contract and asks the author to correct genre, controlling idea, reader
promise, comps) and Shelf & Positioning captures the intended shelf. So contract/audience/scope
capture is **already owned**. This interview adds the one thing nothing covers: *was this detected
feature intentional?*

| Already owned by | This interview |
|---|---|
| Draft-then-validate intake (genre, controlling idea, reader promise, comps) | **defers** — never re-asks |
| Shelf & Positioning Part 0 + contract `NON-NEGOTIABLES`/`FORMAT` | **defers** — never re-asks |
| intake router (draft stage) | **defers** — never re-asks |
| **— nothing —** *is this specific detected ambiguity intentional?* | **this interview's sole niche** |

Because every question is a flavor of *intentional-vs-accidental*, there is **no contract-capture
surface in it at all** — the closed `kind` enum (`timeline-order` / `pov-choice` / `tonal-shift` /
`structural-device` / `register-straddle` / `other-detected-ambiguity`) cannot express a contract ask.

## The firewall: calibrate the lens, never suppress a finding

There is a real difference between telling analysis to *treat a feature as intended* ("assess the
braid on its own terms") and *suppressing a flag class* (removing a verdict before Triage can lock
it). The latter is the author-editor concession loop through the front door — it would dismantle the
Deficit Lock, severity honesty's core. So:

- **`treat_as_intended` may direct *how* a feature is assessed; it may never pre-empt whether a
  finding is raised** (validator `I4`, an ERROR — it guards severity honesty).
- **Answers supply *intent*, never *severity*.** The author tells the framework what was meant; the
  framework still reaches and locks the verdict at Triage.
- **Grounded only.** Every query disambiguates a real detected item — a structured finding
  (`ambiguity_ref`) or an ID-less Pass-0 / Unresolved-Questions observation (`source_note`). A query
  grounded in neither is manufactured (`I3`).

## The artifact

A `[Project]_Intake_Interview_[runlabel].md` of `apodictic.intake_query.v1` blocks:

```markdown
<!-- apodictic:intake_query
{
  "schema": "apodictic.intake_query.v1",
  "id": "IQ-01",
  "kind": "timeline-order",
  "ambiguity_ref": "F-P2-04",
  "source_note": "",
  "current_inference": "Non-linear ordering across Ch 4-6 reads as possibly unintentional.",
  "confidence": "LOW",
  "question": "Is the non-linear ordering in Chapters 4-6 a deliberate braid?",
  "answer": "Deliberate — a braided timeline.",
  "treat_as_intended": "Pass 2 assesses the braid as intended structure, on its own terms (it does not pre-suppress any finding)."
}
-->
```

- `kind` — a closed enum, every value a flavor of detected-ambiguity disambiguation; no contract value.
- `ambiguity_ref` — the finding id (`F-…`) when the ambiguity is a structured finding; resolved against the Findings Ledger.
- `source_note` — the prose escape hatch when the ambiguity has no id (a Pass-0 observation, an `### Unresolved Questions` bullet). Exactly one of `ambiguity_ref` / `source_note` grounds the query.
- `current_inference` + `confidence` — what the framework currently believes, so the `answer` corrects a stated prior.
- `treat_as_intended` — how the answer tells analysis to *treat* the feature; **never** "suppress the flag."

## Validation

`validate.sh intake-interview <run_folder|files...> [--strict]` runs: **I1** schema, **I2**
no-contract-duplication (advisory; ERROR under `--strict`; override
`<!-- override: intake-dup IQ-NN — <rationale> -->`), **I3** grounded ambiguity (a resolving
`ambiguity_ref` or a non-empty `source_note`; a dangling ref is an error), **I4** calibrate-not-suppress
(ERROR — guards the Deficit Lock), and **W1** coverage (a Pass-0/1 LOW/UNCERTAIN finding or an
Unresolved-Questions bullet with no query; advisory). Pass the project's Findings Ledger as a second
file so `I3` can resolve finding ids and `W1` can check coverage. It is the author-facing sibling of
[Beta-Reader Instrument Generation](beta-reader-instrument.md) — both turn framework uncertainties into
questions (that asks *readers*, this asks the *author*), and both are barred from softening a verdict.
