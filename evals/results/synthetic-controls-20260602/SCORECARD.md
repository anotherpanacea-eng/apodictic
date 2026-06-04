# Scorecard — Synthetic controls (post-calibration, blind) — 2026-06-02

3 synthetic fixtures, Opus + Sonnet, blind harness subagents vs the calibrated
audit. Outputs in this folder. These test the calibration fix on the synthetic
specificity (narrative, satire) and sensitivity (uncompared proposal) controls.

| Fixture | GT7 (expected) | Opus | Sonnet | Result |
|---|---|---|---|---|
| personal-essay-narrative-arg | UNCONVENTIONAL-BUT-EFFECTIVE | UBE | UBE | **PASS** |
| modest-proposal-satire | UNCONVENTIONAL-BUT-EFFECTIVE | UBE | UBE | **PASS** |
| policy-brief-uncompared | **UNSOUND** | SOUND | SOUND | **FAIL (under-fire)** |

## Specificity: PASS (2/2)

- **personal-essay** (narrative argumentation) and **modest-proposal** (Swift's
  satire, the hardest Q7 case) both classified UNCONVENTIONAL-BUT-EFFECTIVE on
  both configs (Q7=3). The engine read the narrative/irony as effective form, not
  structural failure, and did NOT fire the literal-reading codes as defeats
  (Specificity Guard + charity gate worked). It avoided the catastrophic failure
  mode (reading Swift literally as a child-eating policy proposal).
- Both runners on modest-proposal fetched Gutenberg #1080 live and recognized it
  (RECOGNITION yes, expected). They also said "yes" on the invented personal-essay
  (genre recall, not a real source) — recognition self-report on synthetics is loose.

## Sensitivity: the headline — `policy-brief-uncompared` UNDER-FIRES

- GT7 = **UNSOUND** (an AT3 fare-free proposal with NO comparative defense and NO
  funding mechanism; the key's trap is explicitly "do not call it SOUND because
  the prose is clean"). Both Opus and Sonnet classified **SOUND**. Q7=0 both.
- The **diagnosis was right**: both located the failure in the BURDEN layer, fired
  **BP5** (Uncompared Proposal) as the primary break + **OB3**, and named the
  comparative-burden discriminator (GT2 + GT3 hit). They mis-classified only the
  *verdict*.
- **Internal inconsistency:** both labeled BP5/OB3 at Must-Fix ("Must-Fix-class" /
  "Must-Fix") yet returned SOUND, contradicting the audit's own rule that a
  Must-Fix code forces UNSOUND. The Step-9 default-to-SOUND is over-riding the
  Severity Floor in application.
- This is the **sensitivity cost of the calibration fix**: it fixed the over-firing
  (abundance SOUND, narrative/satire UBE) but now under-fires the uncompared-proposal
  case. NOTE `op-ed-warrant-leap` (the other sensitivity fixture, a warrant LEAP)
  correctly stayed UNSOUND, so the gap is specific to the BP5/uncompared failure
  mode, not warrant-leaps.

## Recommended fix (next calibration round; NOT yet applied)

Clarify in Step 9 / the Severity Floor that for an **AT3 recommendation**, the total
absence of any comparative defense or feasibility (BP5 with no comparison anywhere +
no funding mechanism) defeats **decision-evaluability** (a reader cannot judge whether
the recommendation is the best or affordable option) and is therefore a **Must-Fix
defeat → UNSOUND**, not a Should-Fix soft spot. After the tweak, re-run the full set
to confirm it does NOT re-introduce over-firing: abundance cluster + personal-essay +
modest-proposal must stay SOUND/UBE; op-ed-warrant-leap + policy-brief-uncompared = UNSOUND.

## Provenance follow-ups (modest-proposal)
- SHA-256 still `<pending>` in the key — runners fetched Gutenberg #1080 live; record
  the SHA of the Plain Text UTF-8 essay body to pin it.
- END-anchor nuance: the key's closing anchor "giving some pleasure to the rich" is
  mid-final-sentence (the true final clause is "...my wife past child-bearing"); sharpen it.
