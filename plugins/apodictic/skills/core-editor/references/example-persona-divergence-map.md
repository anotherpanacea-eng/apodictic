# Persona Divergence Map — *The Tidewater Braid*

<!--
Worked example of a contract-conformant Persona Divergence Map (see specialized-audits/references/
persona-divergence.md + docs/reader-persona-simulation.md). It runs the reader-experience lens
through declared reading DISPOSITIONS and surfaces where the predicted experience DIVERGES. A persona
is a parameterization of the lens, NEVER a character — it has disposition axes, not a name or a life.

This file is exercised by `validate.sh --check-all` (paired with
`example-persona-divergence-ledger.md`) as a canonical release-gate target for `persona-divergence`,
under `--strict`: D1 schema (incl. the nested `experiences` enum), D2 grounded prediction (D-01
anchors the real Ledger finding F-P1-04), D3 target-severity anchoring (exactly one target; the
asserted Must-Fix does not undercut the locked Must-Fix), D4 no fabricated testimony (the prediction
is structural — no first-person reader-reaction quote), and D5 closed-key personas (only disposition axes, no
character keys). The newcomer is the target; the genre-expert is the contrast.
-->

## Personas (declared dispositions)

<!-- apodictic:persona
{"schema":"apodictic.persona.v1","id":"P-01","target":true,"pace_tolerance":"low","genre_familiarity":"newcomer","content_sensitivity":"medium"}
-->

<!-- apodictic:persona
{"schema":"apodictic.persona.v1","id":"P-02","target":false,"pace_tolerance":"high","genre_familiarity":"expert","content_sensitivity":"low"}
-->

## Divergences

<!-- apodictic:divergence
{"schema":"apodictic.divergence.v1","id":"D-01","anchor":"F-P1-04","experiences":{"P-01":"disengage","P-02":"engaged"},"magnitude":"high","asserted_severity":"Must-Fix"}
-->

## High-Divergence Zones

- **Chapter 3 lull (`D-01`, anchored to `F-P1-04`).** A pace-sensitive newcomer (`P-01`, the target)
  is at elevated disengagement risk across the three sub-median Ch 3 scenes; a genre-expert (`P-02`),
  habituated to a slow midpoint, stays engaged. Spread: high. Because the newcomer **is** the target
  audience, the finding stays **Must-Fix** at full severity — the expert's tolerance does not
  downgrade it (segmentation cannot launder a target-audience defect into "it's fine for someone").

## Notes

- **A persona is a disposition, not a character.** Each block carries only reading-disposition axes —
  no name, job, or backstory (validator D5, a closed-key gate). `P-01` is "a pace-sensitive newcomer,"
  not "Sarah, 34."
- **Every divergence is grounded.** `D-01` cites the real Ledger finding `F-P1-04`; an ungrounded
  prediction would be a fabricated one (validator D2).
- **Predicted structurally, never quoted.** The map reasons about disengagement *risk* from the
  manuscript's structure; it never manufactures a first-person reader quotation presented as reaction
  data (validator D4 — the line against the non-viable Simulated Reader Focus Group).
