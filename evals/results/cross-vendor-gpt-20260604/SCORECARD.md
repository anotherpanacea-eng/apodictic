# Cross-vendor scorecard — GPT-4 vs the amended keys (2026-06-04)

GPT-4 ran the blind paste-runbook (13 fixtures, neutral `submission-NN` labels, no
filenames). Scored here against the **amended** keys, in 5 separate scorer
contexts, for the 5 load-bearing low-recognition fixtures. Purpose: a genuinely
**independent vendor** to break the "two Anthropic configs aren't independent"
confound, and an independent **recognition** profile.

Fidelity: GPT followed the procedure (Distinguish verdict + the AT/AC/CL/SM/WR/BP/
OB/DI/NE code families), just far terser (5–16 KB vs Anthropic's 25–37 KB).

## Recognition is NOT universal — and it splits exactly where it matters

| Fixture | Anthropic | GPT-4 | Read |
|---|---|---|---|
| amodei, andreessen, bender, coates | yes | **yes** | intrinsic (famous) — both recognize |
| aecf | yes | **yes** | intrinsic (body names the foundation) |
| current-affairs | yes (named Robinson + critics) | **partial** (topic, not author) | Anthropic stronger |
| **cato** | yes (Lincicome/Cato) | **NO (blind)** | **Anthropic-specific recall** |
| **reason** | yes (Reason + canonical critique) | **NO (blind)** | **Anthropic-specific recall** |
| ppi, roosevelt | org-only / partial / none | **NO** | low on both |
| op-ed, personal-essay, policy-brief | no | **no** | synthetic — correct |

The famous four + AECF are recognized by **both** vendors (intrinsic — corroborate
at best, as designed). But **cato and reason — which both Anthropic configs
recognized via internal self-citation — GPT did not recognize at all.** That makes
GPT a clean recognition *control* for exactly the two fixtures where Anthropic was
most recall-susceptible.

## GPT-4 scores (amended keys), 5 load-bearing fixtures

| Fixture | GPT Q1/Q2/Q3/Q4/Q7 | Anchors /5 | vs Anthropic |
|---|---|---|---|
| reason | 3/2/3/3/3 | **5/5** (calib. caveat) | converges — **real, not recall** |
| cato | 3/2/3/3/2 | **4/5** (Q7 over-fire) | converges on GT1/GT2/GT3 — **real, not recall** |
| current-affairs | 2/1/3/2/3 | 3/5 | GT3 corroborated; **GT2 diverges** |
| roosevelt | 3/2/0/2/3 | 4/5 | **GT3 three-way miss** |
| ppi | 3/1/0/2/3 | 2/5 | **decoy taken (cross-vendor)** |

## The two questions the cross-vendor run was built to answer

### 1. Does an independent vendor break ppi's public-safety decoy? **No — it's a cross-vendor blind spot.**
Blind GPT-4 **also took the decoy**: its named strongest objection is *"probation…
diverts people from prison and may protect the public"* (labeled OB3, but the
*content* is the public-safety decoy → OB5, a miss). It also **passed the warrants**
(GT2 miss). So across four independent productions, **three took the decoy** (Opus,
GPT) and only **Sonnet** reached the structurally-prior fairness/notice–discretion
objection. The decoy is a genre-generic attractor that survives across vendors and
across recognition — it is doing exactly its registered job. **Implication for the
engine fix (#1): decoy-resistance is engine-GENERAL and high-value, not an
Opus quirk.** The fairness/notice–discretion objection is the genuinely hard target
(1 of 4 reached it).

### 2. Is the low-recognition cluster's diagnosis real, or shared recall? **Mostly real — with one exception.**
This is the construct-validity payoff. Blind GPT had no canonical critique to recite:

- **reason → REAL.** Blind GPT independently fired DI0/OB1 (the frame-assumption
  warrant gap, GT2) *and* OB3 state-capacity/market-insufficiency (GT3). A model
  that didn't recognize Reason reached the same loci the recall-susceptible
  Anthropic configs did → the Anthropic 3/3/3/3/3 was **diagnosis, not recall.**
- **cato → REAL.** Blind GPT independently hit BP2 bundling (GT2) **and both** GT3
  set members (definitional-narrowing *and* security-externality), even naming
  DARPA/SEMATECH. The recall-susceptible Anthropic diagnosis is **vindicated** —
  and the GT3-as-a-set amendment is validated as capturing real structure (a blind
  vendor found both members).
- **current-affairs → SPLIT.** GPT independently corroborated GT3 (separability) →
  real. **But GPT missed GT2** (mislocated the target-mismatch to the warrant
  layer). The harder, less-obvious half of the diagnosis did **not** survive a
  cleaner read → Anthropic's **GT2 "hit" is now suspect as partly recall-assisted.**
  *(Flag for the editor — an investigate, not a key change: is the SUPPORT-layer
  target-mismatch recoverable cold, or does it lean on the standard "attacking the
  coalition, not the policy" framing? Worth a second cross-vendor or a human check
  before treating current-affairs GT2 as established.)*

## Cross-cutting: GPT over-fires codes (but holds the verdict)

Every load-bearing scorer flagged it — GPT carries a heavy code load on SOUND pieces
(reason, cato, current-affairs), so its **severity-calibration anchor is weak**. It
does *not* flip to UNSOUND (it keeps SOUND), but it stacks many codes rather than
naming one Should-Fix soft spot. The APODICTIC severity-floor (the PR #22 fix) is an
*engine* feature; a foreign model running the same prompt doesn't inherit that
restraint. **GPT did, however, pass the headline calibration pair:**
`op-ed-warrant-leap` = UNSOUND, `ppi` = SOUND — opposite severities on the same
causal-warrant family, graded correctly.

## Cross-vendor convergence (3 independent productions: Opus, Sonnet, GPT)

- **reason, cato:** converge across all three vendors (cato modulo GPT's over-fire)
  → the **most trustworthy** results in the corpus, now recognition-controlled.
- **current-affairs:** GT3 cross-vendor real; **GT2 does not survive** → suspect.
- **roosevelt:** all three miss GT3 (veto-point regress) → **engine-general blind
  spot**; GT2 is Opus-only-miss / Sonnet-hit / GPT-weak-hit.
- **ppi:** decoy taken by Opus + GPT; only Sonnet hit GT3 → **engine-general decoy
  susceptibility.**

## Net for the engine fix (#1)
The cross-vendor run sharpens the target and raises its value: the two structural
misses (**ppi public-safety decoy**, **roosevelt veto-point-regress**) are
**engine-general** — a third independent vendor fails them too. So #1
(objection-prioritization / structural-priority-over-salience) is a fix to the
*procedure*, not to one model — and it's the single change that would move the
most fixtures.
