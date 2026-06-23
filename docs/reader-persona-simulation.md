# Reader-Persona Simulation — where the book lands differently by audience

**Status:** **Built (Increment 1), 2026-06-20.** Shipped: the `apodictic.persona.v1` + `apodictic.divergence.v1` schemas, the `specialized-audits/references/craft/persona-divergence.md` Pass-1 overlay, `scripts/persona_divergence.py` + `validate.sh persona-divergence` (D1–D5 + W1), and the canonical `example-persona-divergence-map.md` + `example-persona-divergence-ledger.md` (a target newcomer and a genre-expert diverging on a locked Must-Fix) wired into `--check-all` under `--strict`. Self-testable validators 53 → 54. **Build notes:** the validator count is **derived** from `validate.sh`'s `AGG_VALIDATORS` list (not a hand-maintained number); **D2** resolves an anchor against the Ledger finding ids and the Timeline scene-id set; **D1** additionally checks each `experiences` key is a declared persona id; **D4** scans the visible prose only (HTML comments / blocks stripped) and any `persona-quote` override silences it; **D5** is a non-overridable closed-key ERROR (one of the three #17 guards). Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) Tier 1, item 5.
<!-- built-when: scripts/persona_divergence.py -->

Pass 1 (Reader Dynamics — "does the pacing hold?") maps the experience of **one composite reader**. But a manuscript does not meet one reader; it meets an audience with different tolerances. The Chapter-3 lull a literary reader savors is the lull an impatient thriller reader abandons. A reveal that lands for a genre newcomer is one a genre-savvy reader saw coming in Chapter 1. The single composite map averages these into invisibility. **Persona simulation runs the reader-experience lens through several declared reading dispositions and surfaces where the predicted experience *diverges*** — and divergence is the diagnostic signal, exactly as contract-mismatch is.

This capability sits on the most dangerous firewall edge in the Horizon scan, so the boundary is the first thing specified, not the last.

## The line this must not cross (vs. the non-viable #17)

[Simulated Reader Focus Group](../ROADMAP.md#horizon-capacities) (Horizon item 17, *surfaced but not viable*) is forbidden because **fabricated reader reactions are invented data** — the Firewall's spirit applied to evidence. Persona simulation is viable **only** if it stays on the right side of a hard line:

| Forbidden (#17 — fabricated testimony) | Allowed (#5 — structural prediction) |
|---|---|
| "Reader A: *'I got bored in chapter 3 and put it down.'*" | "A pace-sensitive disposition is at elevated disengagement risk across Ch 3: the Timeline shows three consecutive scenes under [N] words with no tension beat (`F-P1-04`)." |
| Inventing a person, a backstory, a quote | Parameterizing the reader-experience lens by a declared *disposition* and predicting from manuscript-grounded structure |
| Reaction as manufactured fact | Prediction as a cited, structural inference |

A persona is **a parameterization of the existing reader-experience lens, never a character.** It has *reading dispositions* (declared, finite, closed), not a name, a job, or a life. Two mechanical guards keep it there: every divergence claim must cite a manuscript-grounded anchor (`D2`), and a persona block may carry **only** disposition axes — the validator rejects any other key (`D5`, a closed-key ERROR, not a defeasible heuristic). A first-person reader quote presented as data is the signature violation (`D4`). This is what makes #5 a lens and #17 a fabrication.

## What it is — and what already exists

- **Not** Pass 1 itself. Pass 1 runs one composite reader; this runs the *same* analysis under several dispositions and reports the **delta**. It consumes Pass 1's findings (the `F-P1-…` blocks in the shared Findings Ledger — Pass 1's own log is prose); it does not replace the pass.
- **Not** the [Reception Risk audit](../plugins/apodictic/skills/specialized-audits/references/craft/reception-risk.md). Reception Risk *does* segment by audience — its §5 subject-position test ("would affected readers experience this differently than the implied reader?") and its §6 Mode Calibration Matrix both vary by audience — but along the **affected-group harm-sensitivity** axis (what a hostile reader screenshots). Persona simulation segments along the **engagement/comprehension disposition** axis (where the book holds one reader and loses another). Different axis, adjacent neighbor; the subject-position test is the near-neighbor this must not duplicate. They compose — a divergence zone may also be a reception-risk zone — but neither subsumes the other.
- **Not** Pass 11 (Market Viability). Pass 11 asks "is this commercially viable"; this asks "for which reader does the *structure* deliver, and where do those readers part ways." Experience divergence is a structural diagnostic, not a market forecast.

## Personas as declared dispositions

A persona is an `apodictic.persona.v1` block: a small, **closed** set of reading-disposition axes, each a top-level string enum (so the subset schema engine *can* validate each one), plus `id` and a boolean `target`. No other keys are permitted (`D5`). No free narrative, no biography field — and, crucially, the guarantee is enforced by the validator's closed-key check, **not** by relying on the schema alone (the subset engine allows unknown properties unless a schema opts into `additionalProperties:false`, so "the schema has no such field" would, on its own, be a false guarantee).

- `pace_tolerance` (low / medium / high)
- `genre_familiarity` (newcomer / regular / expert)
- `content_sensitivity` (low / medium / high)
- `thematic_receptivity` (`SYMPATHETIC` / `MIXED` / `HOSTILE`) — the argument-side disposition, the **verbatim** enum from the Argument Engine's `Audience.Receptivity` (`argument-state-schema.md §1`), so the reuse is literal, not aspirational.
- `continuity_attention` (casual / tracking)

The persona set is **derived from the contract** — but by model judgment, not a field lookup: the fiction contract has `GENRE/SUBGENRE` and a prose `READER PROMISE`, **no structured audience field**. The model infers the **target persona** (the reader the book is *for*) from genre + reader-promise, asserts `target: true` on it, and adds a small canonical library of contrasting dispositions (the genre-expert, the impatient reader, the skeptical reader). The validator checks target **cardinality** (exactly one), not its provenance.

## The artifact

A `[Project]_Persona_Divergence_Map_[runlabel].md` holding:
1. The `apodictic.persona.v1` blocks (the dispositions tested), exactly one with `target: true`.
2. `apodictic.divergence.v1` blocks — one per beat/finding where predicted experience differs across personas:
   - `anchor` — a finding ID (`F-…`) or Timeline locus (the grounding that makes it a prediction, `D2`).
   - `experiences` — the per-persona predicted experience, each ∈ `engaged` / `neutral` / `friction` / `disengage`. This is a **nested** map (persona-id → enum), so its per-element enum membership is enforced in `persona_divergence.py` (the subset engine cannot descend into nested objects — same situation as `retcon_plan.py`'s `scores` field, which the schema types only as `object`); the schema types the container as `object`.
   - `magnitude` — the spread across personas.
   - `asserted_severity` *(optional, enum `Must-Fix`/`Should-Fix`/`Could-Fix`)* — present only if the map restates the anchored finding's severity for an audience; this is the field `D3` reads.
3. A ranked **High-Divergence Zones** summary.

Structured blocks + a generated map: the Harness Contracts v2 posture (contract is source of truth; the readable map is a function of it).

## Severity honesty — the target persona anchors severity

The danger is *persona-shopping*: softening a real defect by finding some disposition for which it "works." The discipline mirrors the canonical Severity Honesty Protocol (`output-policy.md §Deficit Lock` / `§Severity Honesty Protocol`):

- **Severity is anchored to the `target` persona.** A finding Must-Fix for the target audience stays Must-Fix; a non-target persona for whom it reads `engaged` does **not** downgrade it. Mechanically: a `divergence.v1` block whose **optional `asserted_severity`** *differs from* the anchored finding's **locked** severity in the Ledger fails `D3` — the overlay is descriptive, so segmentation may neither downgrade nor inflate the verdict. A severity may be asserted **only against a Ledger finding**: an `asserted_severity` on a Timeline-locus anchor (which has no locked verdict to equal) also fails, since the overlay carries no severity of its own. (The locked side is retrievable — `honesty_check.py`'s locked-findings parse reads `apodictic.finding.v1` severities by ID, exactly as `softness-check` does. The block side only exists when the map chooses to assert a severity, the only case where a deviation — down or up — is even expressible.)
- **Non-target divergence is informational**, not exculpatory. "Works for the expert, fails for the newcomer" is recorded as a divergence; if the newcomer *is* the target, it is a defect at full severity.
- **Lock-then-segment.** Severity is locked against the target persona *before* the divergence reframing, so segmentation cannot launder a target-audience defect into "it's fine for someone."

## The `persona-divergence` validator

`validate.sh persona-divergence <run_folder>` resolves the Persona Divergence Map + the Findings Ledger (for anchor resolution and locked severities) + `Timeline.md` (for locus anchors). Delegates to `scripts/persona_divergence.py`; degrades to advisory `WARN` without `python3`. Report lines namespaced `persona-divergence:<ID>`.

| ID | Severity | Rule |
|---|---|---|
| **D1 — schema** | ERROR | `persona.v1` blocks parse with each **top-level disposition axis** ∈ its enum (subset-engine-validatable); `divergence.v1` blocks parse with `anchor`/`magnitude` present. The **nested** per-persona `experiences` enum membership is checked in `persona_divergence.py` (not the subset engine), mirroring `retcon_plan.py`'s `scores`. |
| **D2 — grounded prediction (signature firewall gate)** | ERROR | Every `divergence.v1` `anchor` resolves to a real `apodictic.finding.v1` ID in the Ledger or a real Timeline locus. An ungrounded prediction is a fabricated one. (Reuses `finding_trace.py`'s ID/locus resolver.) |
| **D3 — target-severity anchoring** | ERROR | Exactly one persona is `target: true`; and every `divergence.v1` block's optional `asserted_severity` **equals** its anchored finding's locked Ledger severity (any deviation — lower OR higher — fails), and is asserted **only against a Ledger finding** — a Timeline-locus anchor has no locked verdict to equal, so a severity asserted on one also fails. The overlay is descriptive: segmentation may neither downgrade nor inflate the target-audience verdict, and carries no severity of its own. |
| **D4 — no fabricated testimony (the #17 boundary)** | WARN (ERROR under `--strict`) | The map contains a first-person reader quotation presented as reaction data (heuristic: quoted `"I …"` reaction strings attributed to a persona). Override `<!-- override: persona-quote D-NN — quoting the manuscript, not a fabricated reader -->`. |
| **D5 — persona is a disposition, not a character** | ERROR | A `persona.v1` block carries **any key outside** the closed set {`id`, `target`, the five disposition axes}. A closed-key check (the inverse of the open subset engine) — non-overridable, because this is one of the three guards against the non-viable #17, and a defeasible WARN is too weak to carry that. |
| **W1 — coverage** | WARN (ERROR under `--strict`) | The set lacks a contrasting persona for a disposition the genre plainly implies matters (e.g., a thriller with no pace-sensitive persona). Advisory: a focused two-persona contrast is legitimate. |

**Ownership boundary.** `persona-divergence` owns the **divergence-prediction contract**: persona-as-disposition discipline (closed-key), prediction groundedness, the anti-fabrication boundary, and target-severity anchoring — classes no other validator raises. It does **not** re-run Pass 1, judge reception/harm (`reception-risk`), forecast market (Pass 11), or re-check letter severity fidelity (`softness-check`). It consumes the Ledger + Timeline; it does not re-derive them.

## Canonical `--check-all` gate

A worked example — a small Findings Ledger fixture (with an `F-P1-…` finding and a locked Must-Fix) and a Persona Divergence Map with two personas (a `target` newcomer and a genre-expert) diverging on one anchored finding — is added, and `validate.sh --check-all` runs `persona-divergence` against it: proving grounded predictions (`D2`), exactly-one-target with no downgrade (`D3`), a clean anti-fabrication scan (`D4`), and a closed-key persona (`D5`) on canonical artifacts (the "canonical-framework validator runs as release gate" discipline, `ROADMAP.md` §Deferred). It includes two **negatives**: a `divergence.v1` whose `asserted_severity` undercuts a locked Must-Fix (must fail `D3`), and a persona block with a stray `name` key (must fail `D5`).

## Increment plan

**Increment 1 (this spec):** the `apodictic.persona.v1` + `apodictic.divergence.v1` schemas (added to `schemas/`, auto-discovered by `known_schema_ids()`), the Pass-1 overlay reference, `scripts/persona_divergence.py` (closed-key + nested-enum + anchor-resolution + severity-anchoring) + `validate.sh persona-divergence`, the model-inferred target persona + canonical contrast library, the worked example, and the `--check-all` gate. Validators +1 (running total fixed at build).

**Future increments (not built):**
- **Persona-targeted instruments** — feed the High-Divergence Zones into [Beta-Reader Instrument Generation](beta-reader-instrument.md) so readers from the divergent segment are asked exactly where the prediction is uncertain (closing the predict→test loop without fabricating the answer).
- **Divergence visualization** — render per-persona experience curves into [Manuscript-Structure Visualizations](manuscript-visualizations.md).
- **Full argument-audience reuse** — extend `thematic_receptivity` into the Argument Engine's complete three-dimension audience model (Expertise / Receptivity / Consequence) for persuasive nonfiction.

## Self-review (Increment 1)

- *Why this is a lens, not a focus group* — the viability argument is the #17 line, and all three guards are now **mechanical**, not aspirational: predictions are grounded (`D2`, ID/locus resolution), testimony is scanned (`D4`), and personas are closed-key disposition vectors (`D5`, an ERROR enforced in Python because the subset schema engine allows unknown keys). The earlier draft leaned on "the schema has no biography field," which was false; the closed-key check is the real guarantee.
- *Why severity anchoring needs an explicit field* — `D3` can only fire on something the block actually asserts, so deviation-detection (downgrade OR inflation) lives on an optional `asserted_severity` compared **for equality** against the locked Ledger severity; without that field there was nothing to read and the anti-persona-shopping claim was empty. Equality (not just "not lower") is what keeps the overlay descriptive — an upshift would be a new severity the §4e propagation table must account for, so the contract forbids it.
- *Why disposition axes are a closed enum set* — open-ended description is the door to invented characters; a finite axis set keeps the persona a parameterization, keeps `D1`'s top-level checks subset-validatable, and makes `D5` a clean closed-key test.
- *Why it overlays Pass 1 rather than becoming a new pass* — the analysis is identical; only the reader parameter changes. The machine-readable Pass-1 surface it builds on is the `F-P1-…` findings in the shared Ledger, not Pass 1's prose log.
