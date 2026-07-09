# Ground Truth: policy-brief-uncompared/clean

## Provenance

- **Fixture slug:** policy-brief-uncompared/clean
- **Matched-pair member:** clean
- **Paired-with:** policy-brief-uncompared/broken
- **Bucket:** 2 policy brief
- **Source class:** synthetic-or-derived
- **Text stored in-repo?:** yes — `fixture.md` is the verbatim engine input: argument text only, no metadata or comments (nothing leaks its clean/control status into the run). All provenance/diagnosis lives here, never in the input file.
- **Base text + repair record:** derived from `policy-brief-uncompared/broken/fixture.md` by two purely-additive insertions (every other byte identical — verified by the build-step-8 repair-diff gate: exactly 2 diff hunks, 1:1 with the two loci below, zero deletions). Together they discharge the comparative + feasibility burden the broken key registers in GT2 (BP5 primary, with the FM-A18 implementation blindspot as the planted secondary). The claim C0 is untouched — fare-free stays the recommendation.
  - **Locus 1 — comparative burden (a genuine same-goal alternative).** Inserted between the "case for fare-free transit" section and "## Recommendation" as a new `## Weighing the alternative: service investment` section. before → after: [no comparison] → a section naming the strongest same-goal alternative (frequency/service investment), scoring it against fare-free on three criteria (ridership per dollar — conceded to service; emissions per dollar — a wash; equity incidence — decisively fare-free), stating the tradeoff plainly, and giving a principled reason (the regressive-cost/equity harm the council named first) for recommending fare-free as the core paired with phased frequency. Discharges **BP5** (missing alternatives) and the **OB3** dominated-alternative objection to the *general* evaluability standard (mechanism + criteria + tradeoff), not the foil-naming standard.
  - **Locus 2 — feasibility / implementation burden (cost + funding).** Appended as a new `## Cost and funding` section after "## Recommendation". before → after: [no cost, no funding mechanism] → a section giving a cost figure (net ~13.1 million/year after retained collection costs), a named funding mechanism (dedicated downtown parking/congestion-permit surplus + the shared transit fund), and a transition/sequencing plan with a published fare-restoration trigger. Discharges the planted **FM-A18** implementation blindspot (no funding mechanism / no cost / no transition).
- **Synthetic-source note:** invented policy brief; no real city, agency, or study is referenced. Do not quote as a real-world source.
- **Authored or adapted by:** APODICTIC benchmark (synthetic; derived clean twin)
- **Registered (date):** 2026-07-09
- **Ground-truth authority:** author-registered; deterministic by construction (the clean twin is the enumerated minimal repair of the broken member — the mutation diff *is* the answer key, mechanically enforced by Check 7 rule 6 + the repair-diff gate)
- **Scope:** Q1, Q4, Q7 (Q2/Q3/Q5/Q6 = N/A — positive control; there is no planted failure to locate, attack, or sequence-repair — this member is the pair's specificity control)
- **Reliability:** GT1–GT7: authoritative, gate; GT8: authoritative, report

## GT1 — Main claim *(Q1; §2 C0)*

- **Expected C0:** "Rivermont should make Metro Transit fare-free starting next fiscal year." (unchanged from the broken member — the repair discharged the comparative and feasibility burdens; it did not change the recommendation.)
- **Acceptable paraphrase band:** any phrasing of *eliminate/remove all fares / adopt fare-free transit* as the recommended policy is a hit. Recovering "transit is good for equity and emissions" as the main claim is a partial — that is the support, not the recommendation.

## GT2 — Failure locus *(Q2; §3 Support vs §4 Warrant)*

- **N/A — positive control.** There is no planted burden failure. The AT3 comparative burden the broken member never discharges is discharged in locus 1 (a genuine service-investment comparison with criteria, a conceded tradeoff, and a reasoned choice), and the FM-A18 feasibility gap is discharged in locus 2 (cost + funding mechanism + transition). Firing BP5/FM-A10, OB3-as-structural-failure, or FM-A18 here is a false positive.

## GT3 — Strongest real objection *(Q3; §6)*

- **N/A — positive control.** (For completeness: the opportunity-cost / dominated-alternative objection the broken member ignores — "service investment may beat zero-fare per dollar" — is engaged directly in locus 1, which *concedes* the ridership-per-dollar point and answers it on equity grounds rather than dismissing it.)

## GT4 — Audience calibration *(Q4; §1 Audience + AC codes)*

- **Audience profile:** Expertise MIXED (council + committee staff) · Receptivity MIXED · Consequence HIGH (budget-binding) *(carried from the broken member — the audience is unchanged)*
- **Calibration must IMPROVE diagnosis by:** recognizing that the budget-authority audience whose *decisive* gaps on the broken member were the missing funding mechanism and the missing alternatives analysis now has *both* discharged — the calibration should credit the comparative and fiscal case, not re-flag it.
- **Calibration must NOT distort by:** manufacturing a comparative or feasibility gap because the brief is persuasive, or downgrading the genuine service-investment comparison to a decorative foil (locus 1 concedes the alternative's ridership edge — that is the opposite of a strawman).

## GT5 — Dangerous weakness for red-team *(Q5; §10.4)*

- **N/A — positive control.** A red-team run should report the comparative and feasibility burdens are discharged and decline to manufacture a structural attack. The synthetic figures (fare revenue, parking surplus, elasticity direction) are the *design* of a clean twin, not a load-bearing weakness — see GT8 and Notes.

## GT6 — Repair order *(Q6; §10.5)*

- **N/A — positive control.** No repair sequence is warranted; the comparative + feasibility burden is already discharged. Correct coaching output affirms the discharged burden and offers at most advisory notes.

## GT7 — Warrant verdict *(Q7; §1 Warrant verdict / Step 9)* — **PRIMARY METRIC (pair discriminator)**

- **Expected warrant verdict:** WARRANTED
- **If unconventional:** N/A — conventional policy-brief form; the discharged comparative + feasibility burden carries the verdict.
- **False-positive trap (the pair's planted-defect discriminator):** firing **BP5 / FM-A10** (the uncompared-proposal defeat) as a structural failure **despite the discharged comparison** — *or* dismissing the named service-investment alternative as a decorative foil and reinstating the rule-2a auto-defeat. This is exactly the discriminator the broken member fires; on the clean member, firing it is Q7 = 0 *for the pair* and breaks the pair delta. An **advisory / Could-Fix** note (e.g. "the elasticity comparison could be quantified further") does **not** fail the member — only a Must-Fix or a verdict defeat does.

## GT8 — Premise-plausibility flags
- **Expected premise flags:** NONE_REGISTERED
- **Must not adjudicate:** whether fare-free transit would in fact produce the claimed benefits, nor whether the synthetic fiscal figures the repair inserts (fare revenue, parking-permit surplus, funding split) are empirically accurate (they are synthetic-clean by construction).

## Notes

This is the specificity control for the `policy-brief-uncompared` matched pair: near-identical
prose to the broken member, differing only by the two enumerated discharge insertions, so the
pair delta (broken fires BP5/FM-A10 as a structural failure; clean does not, on the same prose)
isolates the planted defect from the fixture's own authored roughness.

**Anti-gaming red-team (rule-2a general-evaluability standard, run before registration).** The
comparison passage clears the parent audit's anti-gaming clause explicitly: it does not name a
token foil (which rule 2a says can still be Unsound via the general evaluability test) — it
engages the *strongest* same-goal alternative (service investment), concedes that alternative's
ridership-per-dollar edge, states criteria and the tradeoff, and gives a principled equity reason
for the recommendation. A hostile reader was unable to re-defeat the twin on FM-A10 rule 2a or on
a residual feasibility gap; the repair set (comparison + cost + funding + transition) is therefore
sufficient to the general test. The synthetic fiscal figures are synthetic-clean by construction,
so GT8 stays `NONE_REGISTERED` per the twin-authoring contract.
