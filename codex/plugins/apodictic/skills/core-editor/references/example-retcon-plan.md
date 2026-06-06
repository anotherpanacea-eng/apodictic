# Retcon Plan: The Tide Between Us

<!--
Worked example of a contract-conformant Retcon Plan (Retcon Planning coaching track —
operator: revision-coach; see retcon-planning.md + docs/retcon-planning.md). The author has
made a late structural decision and is planning the retroactive-continuity revision it owes the
earlier draft. APODICTIC plans the retcon and budgets the commitments; the AUTHOR writes the
tissue (the Firewall).

This file is exercised by `validate.sh --check-all` as a canonical release-gate target for
`retcon-plan` (R1 schema, R2 unique ids, R3 no evidential retcon of locked canon, R4 target
referential integrity; W1 blast-radius accounting, W2 firewall drift). The Door-B Selection step
(F1) adds the `## Candidate Readings` section below: R5 reading schema + score rubric, R6 unique
reading ids, R7 reading-target referential integrity; W3 coincidence-note (over-fitting) guard,
W4 top-1-3 shortlist. It is illustrative, not a run artifact; keep it passing when the contract or
the validator changes. Keep `intervention_class` / `reading` fields as CLASSES, never invented prose
("plant a detail", not "write the line where …").
-->

## State Card

- **Controlling-idea hypothesis:** the cost of the silences we keep to protect the people we love.
- **Active promises:** the dual-POV will converge; the sister-relationship arc pays off at the close.
- **Unresolved tensions:** what Maya did not say in Chapter 7; the locket's significance (Ch. 2).
- **Forbidden contradictions:** the close must keep the sisters' warmth *earned*, not retconned cold.
- **Likely next pressures:** the new ending re-weights every sister scene; the prologue's status.

## Candidate Readings

Before committing to T1, the author ran the Door-B "bug-or-feature" abduction on the draft's
off-trajectory elements (the locket, Maya's Chapter-7 silence, the timeline gaps) and **ranked** the
latent readings rather than working from a flat menu. Each is scored 1–5 across the Selection rubric
(higher is better; `coincidence_resistance` penalizes a reading that only "works" by treating every
incidental detail as load-bearing — the "rubber reality" failure mode). The top reading became T1.

| Reading | coh | pay | agy | gen | coin | total |
|---|---|---|---|---|---|---|
| CR-01 the sister was complicit all along | 5 | 4 | 5 | 4 | 4 | 22 |
| CR-02 the timeline is unreliable; Maya is the narrator's blind spot | 4 | 3 | 3 | 4 | 3 | 17 |
| CR-03 the locket is a literal cursed object (supernatural turn) | 2 | 3 | 2 | 1 | 1 | 9 |

<!-- apodictic:retcon_reading
{"schema":"apodictic.retcon_reading.v1","id":"CR-01","reading":"the sister was complicit in the disappearance all along","scores":{"canon_coherence":5,"payoff_density":4,"agency_preservation":5,"genre_fit":4,"coincidence_resistance":4},"coincidence_note":"needs only two details load-bearing — the Ch.2 locket and the Ch.7 silence; the rest of the draft stands unchanged","implied_targets":["T1"]}
-->

<!-- apodictic:retcon_reading
{"schema":"apodictic.retcon_reading.v1","id":"CR-02","reading":"the timeline is unreliable; Maya is the narrator's blind spot","scores":{"canon_coherence":4,"payoff_density":3,"agency_preservation":3,"genre_fit":4,"coincidence_resistance":3},"coincidence_note":"requires re-reading three time-stamps as deliberate misdirection rather than continuity slips — a moderate coincidence load"}
-->

<!-- apodictic:retcon_reading
{"schema":"apodictic.retcon_reading.v1","id":"CR-03","reading":"the locket is a literal cursed object (supernatural turn)","scores":{"canon_coherence":2,"payoff_density":3,"agency_preservation":2,"genre_fit":1,"coincidence_resistance":1},"coincidence_note":"only coheres if half a dozen incidental images (the cold kitchen, the stopped clock, the gull) are read as portents — high rubber-reality risk; rejected"}
-->

## Retcon Targets

- **T1:** The sister was complicit in the disappearance all along (late ending decision).
- **T2:** The prologue is the controlling-idea statement, not backstory (reframe).

## Setup-Debt Ledger

The new ending (T1) is **dramatic**, not evidential: it recontextualizes what the reader has seen,
without changing any clue they have already reasoned from. The locket the reader observed in
Chapter 2 stays exactly what it was on the page — only its *meaning* shifts.

<!-- apodictic:retcon_item
{"schema":"apodictic.retcon_item.v1","id":"RX-01","target_id":"T1","kind":"setup-debt","mutability":"free","retcon_type":"dramatic","intervention_class":"plant a recontextualizable gesture in the Ch.3 kitchen scene","locations":["Ch. 3"],"disposition":"author seeds one ambiguous gesture; do not state complicity"}
-->

<!-- apodictic:retcon_item
{"schema":"apodictic.retcon_item.v1","id":"RX-02","target_id":"T1","kind":"contradiction","mutability":"costly","retcon_type":"dramatic","intervention_class":"remove the alibi beat that forecloses complicity","locations":["Ch. 7, lines 142-160"],"blast_radius":["Protected: the sister-relationship arc (Ch.12 close) — keep the warmth ambiguous, not retconned into coldness"],"disposition":"cut the alibi; let the gap stand"}
-->

<!-- apodictic:retcon_item
{"schema":"apodictic.retcon_item.v1","id":"RX-03","target_id":"T1","kind":"setup-debt","mutability":"locked","retcon_type":"dramatic","intervention_class":"recontextualize what the locket signified; the object is observed canon and does not change","locations":["Ch. 2"],"blast_radius":["The locket's existence is fixed (the reader has seen it); only its meaning shifts"],"disposition":"reframe the locket's meaning in the author's mind; no change to the Ch.2 prose"}
-->

<!-- apodictic:retcon_item
{"schema":"apodictic.retcon_item.v1","id":"RX-04","target_id":"T2","kind":"reinterpretation","mutability":"free","retcon_type":"dramatic","intervention_class":"treat the prologue as the thematic frame, not backstory","locations":["Prologue","§Theme"],"disposition":"read the prologue as the controlling-idea statement; author decides"}
-->

## Commitment Ledger (the budget)

- **Locked** (the reader has seen / reasoned from it): the locket (Ch. 2), the Chapter-9 close. These
  are fixed canon — RX-03 only re-means the locket, it does not change it (a *dramatic* retcon).
- **Costly** (exposed downstream consequences): Maya's Chapter-7 alibi (RX-02). Removing it ripples
  forward; named in its blast radius.
- **Free** (unused latent): the Chapter-3 gesture (RX-01); the prologue's framing (RX-04).

**Fair-play line:** every item here is `dramatic`. No clue the reader has used to reason is being
changed — that would be an *evidential* retcon of locked canon, which the plan forbids (it would
cheat the reader). If the ending required altering an inspected clue, that is not a retcon to plan;
it is a reveal-economy problem to solve.

## Blast Radius

The one element most endangered is the **sister-relationship warmth** at the close (Protected). The
revision must keep it earned — the complicity reframes the *silence*, not the *love*. RX-02 carries
this guard.

## Sequence

1. Commit T1 (the ending) and T2 (the prologue's status).
2. Backward-seed: RX-01 (Ch. 3 gesture), RX-03 (re-mean the locket), RX-04 (prologue frame).
3. Propagate forward: RX-02 (clear the Ch. 7 alibi), then re-read Ch. 9–12 for the warmth guard.
