# Reader-Persona Simulation — where the book lands differently by audience

*Reference module for the APODICTIC specialized audits — an overlay on Pass 1 (Reader Dynamics). Pass
1 maps one composite reader; this runs the *same* lens through several declared reading dispositions
and reports the **delta**. Spec + validator: `docs/reader-persona-simulation.md`,
`scripts/validate.sh persona-divergence`. Worked example: `core-editor/references/example-persona-divergence-map.md`
(paired with `example-persona-divergence-ledger.md`).*

---

## When to use

After Pass 1, when the question is not "does the pacing hold?" but "for *which reader* does the
structure deliver, and where do those readers part ways?" The Chapter-3 lull a literary reader savors
is the one an impatient thriller reader abandons; a reveal that lands for a newcomer is one a
genre-savvy reader saw coming. The single composite map averages these into invisibility. Persona
simulation surfaces the **divergence** — and divergence is the diagnostic signal, exactly as
contract-mismatch is.

## The line this must not cross (the #17 boundary)

The [Simulated Reader Focus Group](../../../../docs/reader-persona-simulation.md) (Horizon item 17) is
non-viable because **fabricated reader reactions are invented data**. Persona simulation is viable
only because it stays a **lens**, not a focus group, enforced by three mechanical guards:

| Forbidden (#17 — fabricated testimony) | Allowed (#5 — structural prediction) |
|---|---|
| "Reader A: *'I got bored in chapter 3 and put it down.'*" | "A pace-sensitive disposition is at elevated disengagement risk across Ch 3 (anchored to `F-P1-04`)." |
| Inventing a person, a backstory, a quote | Parameterizing the lens by a declared *disposition* and predicting from grounded structure |

- **A persona is a disposition, not a character** — only disposition axes, never a name/job/life
  (validator `D5`, a closed-key ERROR; the real guarantee, since the subset engine allows unknown keys).
- **Every divergence is grounded** in a real finding or Timeline locus (`D2`).
- **No fabricated testimony** — a first-person reader-reaction quote presented as data is scanned (`D4`).

## Personas as declared dispositions

An `apodictic.persona.v1` block carries a closed set of disposition axes (each a top-level enum), plus
`id` and a boolean `target` — **no other keys**:

- `pace_tolerance` (low / medium / high)
- `genre_familiarity` (newcomer / regular / expert)
- `content_sensitivity` (low / medium / high)
- `thematic_receptivity` (`SYMPATHETIC` / `MIXED` / `HOSTILE`) — the **verbatim** Argument-Engine
  `Audience.Receptivity` enum, so the reuse is literal
- `continuity_attention` (casual / tracking)

The model infers the **target persona** (the reader the book is *for*) from genre + reader-promise and
asserts `target: true` on exactly one; it adds a small library of contrasting dispositions (the
genre-expert, the impatient reader). The validator checks target **cardinality** (exactly one), not
its provenance.

## Severity honesty — the target persona anchors severity

The danger is *persona-shopping*: softening a real defect by finding some disposition for which it
"works." So **severity is locked against the target persona before the divergence reframing**: an
`apodictic.divergence.v1` block whose optional `asserted_severity` is *lower* than the anchored
finding's locked Ledger severity fails `D3`. "Works for the expert, fails for the newcomer" is recorded
as divergence; if the newcomer *is* the target, it is a defect at full severity.

## The artifact

A `[Project]_Persona_Divergence_Map_[runlabel].md` holding the `persona.v1` blocks (exactly one
`target: true`), `divergence.v1` blocks (one per anchored beat/finding — `anchor` + nested
per-persona `experiences` ∈ engaged/neutral/friction/disengage + `magnitude`, optional
`asserted_severity`), and a ranked **High-Divergence Zones** summary.

## Validation

`validate.sh persona-divergence <run_folder|files...> [--strict]` runs: **D1** schema (incl. the
nested `experiences` enum + that each key is a declared persona), **D2** grounded prediction (anchor
resolves to a Ledger finding or a Timeline scene id), **D3** target-severity anchoring (exactly one
target; no `asserted_severity` below the locked severity), **D4** no fabricated testimony (advisory;
ERROR `--strict`; override `<!-- override: persona-quote D-NN — quoting the manuscript -->`), **D5**
closed-key persona (ERROR, non-overridable), and **W1** coverage (≥2 personas with at least one
varying disposition axis). Pass the Findings Ledger (and optionally the Timeline) as additional files
so `D2`/`D3` resolve. See `docs/reader-persona-simulation.md`.
