# Development Edit: The Tide Between Us — Blind-Spot Ordering

<!--
Worked example: an EDITOR SCAFFOLDING letter whose "What You Might Have Missed" section is
RANKED (carries the <!-- blindspot-ranked --> marker). Exercised by `validate.sh --check-all`
as the canonical release-gate target for the blind-spot ordering path (B1-B4) on the
editor-scaffolding validator, run over THIS FOLDER (the letter + its co-located Findings
Ledger) under --strict. The order is the declared key — severity band descending, then the
model's `salience` (subtle first — the serious-but-easy-to-miss finding leads its band), then
evidence-ref footprint, then finding-id: F-P2-01 (Must-Fix, subtle) before F-P5-02 (Must-Fix,
moderate) before F-P1-03 (Should-Fix, subtle) — salience orders within the Must-Fix band, and
band dominance keeps the Should-Fix last. Keep it passing when the validator changes.
Illustrative, not a run artifact; keep the body free of author-directed prescriptions (W1 lexicon).
-->

<!-- mode: editor-scaffolding -->

### Maya Okonkwo | 78,000 words | Complete draft
*APODICTIC Development Editor — addressed to the editor, not the author.*

## Editor Brief

A dual-timeline literary novel with a strong voice and a structurally soft middle. Verdict
class: targeted revision, not reconception. Where our reads most diverge: the polished Part I
prose papers over a missing causal beat at the Chapter 9 turn, and a confident first read
tends to carry Part I's goodwill through the middle.

## What Needs Work

- **Must-Fix:** the middle third compresses its emotional aftermath into summary (Chapter 9).

## What You Might Have Missed

<!-- blindspot-ranked -->
- F-P2-01 — the causal link the polished Part I prose masks; it surfaces once, so a confident read skims past it.
- F-P5-02 — the setup debt diffused across three chapters, easy to under-weight because no single scene carries it.
- F-P1-03 — a tonal echo in the second timeline that slightly flattens the POV contrast.

## Intervention Menu — editor's discretion

- Option: restore a transit beat at the Chapter 9 turn, or seed an explicit time marker.
- Option: consolidate the diffuse setup into one load-bearing scene before the climax.

## Appendix A — Diagnostic Detail

The full pass findings, with severities and evidence, are in the companion Findings Ledger.
