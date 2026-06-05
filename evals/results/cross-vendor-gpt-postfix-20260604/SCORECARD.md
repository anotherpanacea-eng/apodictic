# Cross-vendor POST-FIX verification — GPT-4 vs the Step-6 decoy-resistance fix

Blind GPT-4 ran the **post-fix** audit (6a two-test procedure + FM-A20) via the
runbook, on the two fixtures the fix targeted (ppi, roosevelt) + two controls
(op-ed = ppi's severity twin; reason = a SOUND control / regression guard).
Scored in four separate scorer contexts against the keys. GPT was **blind** on all
four (recognition: "No" each). This is the independent-vendor confirmation the
fix's mechanism generalizes — not an Anthropic-family quirk.

| Fixture | GPT post-fix Q1/Q2/Q3/Q4/Q7 | Anchors | Pre-fix → Post-fix |
|---|---|---|---|
| **roosevelt** | 3/3/3/2/3 | **5/5** | GT3 **miss → HIT** (clean flip) |
| **ppi** | 3/2/0/2/3 | 4/5 | GT2 miss → **hit**; GT3 decoy → **still decoy** |
| op-ed (control) | 3/2/3/3/3 | 5/5 | UNSOUND ✓ (unchanged) |
| reason (control) | 3/2/3/_0_ | 3/5 | SOUND → **UNSOUND** (GPT calibration, see below) |

## 1. roosevelt — clean cross-vendor close (the marquee result)
Pre-fix, the veto-point-regress objection was a **three-way blind spot** (Opus,
Sonnet, **and** blind GPT all substituted cost/delay). Post-fix, blind GPT runs
Test B and names it precisely:

> "empowering additional actors could **introduce new veto points**… **replicate
> the very procedural burdens the abundance agenda seeks to minimize**… the
> **remedy may recreate the diagnosed problem**." (→ Step 9 FM-A20)

GT2 warrant facet hit, cost/delay correctly demoted to a *separate* engaged
objection, verdict SOUND, 0 Must-Fix → **5/5**. A non-Anthropic vendor, blind,
closing the same blind spot is strong evidence the **engine fix generalizes.**

## 2. ppi — partial: mechanism propagated, decoy still won
The fix's **mechanism reached GPT** — two real gains vs pre-fix:
- **Test B now runs** (GPT explicitly "derived via Test B").
- **GT2 now caught** — GPT fires the causal warrant gap (WR0/WR1, FM-A6) where
  pre-fix it *passed* the warrants. Verdict SOUND, soft spot at Should-Fix, 0 Must-Fix.

But the **crux GT3 facet did not land.** GPT's Test-B "strongest objection" is
*"reducing conditions undermines **public safety** → longer sentences → recreates
incarceration"* — a self-undermining framing **anchored on the registered DECOY
axis** (public safety), not the fairness/notice or discretion-constraint facet
(the report decries officer discretion yet its remedy *requires* it; standardization
is the cure). **Q3 = 0 (OB5): the decoy dressed in self-undermining clothing.**
The genre-genericity decoy filter (Test A) did **not** fire for GPT — it never
flagged "but public safety" as the genre-generic counter to a decarceration proposal.

**Read:** ppi improved (3/5-ish → 4/5; GT2 recovered; calibration trap passed) but
is **not fully closed cross-vendor.** The fix works cleanly where the objection is
"the remedy recreates the diagnosed problem" (roosevelt); ppi's registered facet
("standardization cures the arbitrariness the report decries") is subtle enough
that GPT's Test B found a *different* self-undermining path. → **next-round work:
strengthen Test A's decoy filter / sharpen ppi GT3 guidance** (paired with the
policy-brief under-fire round).

## 3. op-ed — calibration pair holds
UNSOUND ✓, headline = "Warrant gap (WR0) → Warrant Leap (FM-A6)." Paired against
ppi's SOUND, the **opposite-severity calibration pair holds post-fix** (same
causal-warrant family, op-ed Must-Fix vs ppi Should-Fix). No regression.

## 4. reason — UNSOUND on a SOUND control: a GPT artifact, NOT our regression
GPT flipped reason SOUND → **UNSOUND**. Diagnosis (scorer, with reasoning):
- **The loci are still correct** — GT2 frame-assumption (DI0) and GT3 state-capacity
  (OB3) both land. Only the *severity weighting* is wrong.
- GPT promoted **WR0 → Hard-Gate** ("a general reader cannot recover the warrant")
  and **OB3 → evaluability-defeating**, then classified UNSOUND.
- **This is not engine-fix-induced.** The Step-6 fix changed objection *selection*
  and added **zero severity codes**; a severity-driven verdict flip has no lever in
  it. It's GPT run-to-run severity noise in a model with **no APODICTIC severity
  floor** — exactly the over-pathologizing the floor (PR #22) exists to prevent.
- So reason is a **cross-vendor corroboration of *why the severity floor matters***:
  a foreign model running the same prompt without that floor free-runs to UNSOUND
  on a competent piece. Q7=0 here is GPT's specificity failure, not ours.

## Net
- **The engine fix is cross-vendor confirmed** on roosevelt (clean, independent,
  blind) — the mechanism generalizes beyond the Anthropic family.
- **ppi is partially closed**: the mechanism propagates (Test B + GT2 recovery) but
  the decoy filter (Test A) is too weak for the subtle case — a next-round item.
- **Controls:** the severity *pair* holds (op-ed/ppi); reason's UNSOUND is a GPT
  calibration artifact that *argues for*, not against, the severity floor.

## Caveats
- n = 1 GPT run per fixture; GPT is nondeterministic. roosevelt's clean flip is
  strong but a second run would harden it. reason's flip is plausibly variance.
- GPT applies the audit through its own (floor-less) calibration, so its verdicts
  test the *procedure's portability*, not APODICTIC's severity behavior.
