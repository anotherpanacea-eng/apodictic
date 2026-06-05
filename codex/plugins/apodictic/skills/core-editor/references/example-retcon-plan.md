# Retcon Plan: The Tide Between Us

<!--
Worked example of a contract-conformant Retcon Plan (Retcon Planning coaching track —
operator: revision-coach; see retcon-planning.md + docs/retcon-planning.md). The author has
made a late structural decision and is planning the retroactive-continuity revision it owes the
earlier draft. APODICTIC plans the retcon and budgets the commitments; the AUTHOR writes the
tissue (the Firewall).

This file is exercised by `validate.sh --check-all` as a canonical release-gate target for
`retcon-plan` (R1 schema, R2 unique ids, R3 no evidential retcon of locked canon, R4 target
referential integrity; W1 blast-radius accounting, W2 firewall drift). It is illustrative, not a
run artifact; keep it passing when the contract or the validator changes. Keep `intervention_class`
fields as CLASSES, never invented prose ("plant a detail", not "write the line where …").
-->

## State Card

- **Controlling-idea hypothesis:** the cost of the silences we keep to protect the people we love.
- **Active promises:** the dual-POV will converge; the sister-relationship arc pays off at the close.
- **Unresolved tensions:** what Maya did not say in Chapter 7; the locket's significance (Ch. 2).
- **Forbidden contradictions:** the close must keep the sisters' warmth *earned*, not retconned cold.
- **Likely next pressures:** the new ending re-weights every sister scene; the prologue's status.

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
