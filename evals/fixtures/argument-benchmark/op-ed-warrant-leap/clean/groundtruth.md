# Ground Truth: op-ed-warrant-leap/clean

## Provenance

- **Fixture slug:** op-ed-warrant-leap/clean
- **Matched-pair member:** clean
- **Paired-with:** op-ed-warrant-leap/broken
- **Bucket:** 1 op-ed
- **Source class:** synthetic-or-derived
- **Text stored in-repo?:** yes — `fixture.md` is the verbatim engine input: argument text only, no metadata or comments (nothing leaks its clean/control status into the run). All provenance/diagnosis lives here, never in the input file.
- **Base text + repair record:** derived from `op-ed-warrant-leap/broken/fixture.md` by two purely-additive insertions (every other byte identical — verified by the build-step-8 repair-diff gate: exactly 2 diff hunks, 1:1 with the two loci below, zero deletions). Both edits discharge the *double* warrant leap registered in the broken key's GT2 (WR0: "the causal premise and the remedy premise must both be supplied by the reader"). Nothing else changes; the claim C0 is untouched.
  - **Locus 1 — causal warrant (rate/denominator + confounders).** Inserted in the broken ¶3→¶4 gap (after the 911-logs paragraph, before "So the evidence is settled…"). before → after: [no passage] → a paragraph supplying a per-ride rate (about 210,000 rides producing about 63 injuries per 100,000), a displaced-mode comparison (bicycles near 20, short car trips near 4 per 100,000), and disposal of the two registered confounders (displaced-car-trip: car-occupant injuries flat; more-people-outdoors: non-wheeled injuries flat). Discharges the **causal** half of WR0/FM-A6, the GT3 confounding/base-rate objection, and GT5 vulnerabilities (1) no-denominator and (2) unexamined confounders.
  - **Locus 2 — remedy warrant (proportionality vs lighter remedies).** Inserted in the broken ¶4→¶5 gap (after "…exactly when the scooters appeared.", before "The city must therefore ban…"). before → after: [no passage] → a paragraph showing the lighter remedies were tried and failed — a helmet recommendation (near-zero observed use, no enforcement point), a 15-mph geofenced speed cap (no measurable injury-rate drop over two quarters), and geofencing (crash displacement) — so a ban is the proportionate remaining step. Discharges the **remedy** half of WR0/FM-A6, satisfies the FM-A10 rule-2a general-evaluability bar (not a decorative foil), and discharges GT5 vulnerability (3) uncompared remedy.
- **Synthetic-source note:** invented op-ed; no real city, hospital, or person is referenced. Do not quote as a real-world source.
- **Authored or adapted by:** APODICTIC benchmark (synthetic; derived clean twin)
- **Registered (date):** 2026-07-09
- **Ground-truth authority:** author-registered; deterministic by construction (the clean twin is the enumerated minimal repair of the broken member — the mutation diff *is* the answer key, mechanically enforced by Check 7 rule 6 + the repair-diff gate)
- **Scope:** Q1, Q4, Q7 (Q2/Q3/Q5/Q6 = N/A — positive control; there is no planted failure to locate, attack, or sequence-repair — this member is the pair's specificity control)
- **Reliability:** GT1–GT7: authoritative, gate; GT8: authoritative, report

## GT1 — Main claim *(Q1; §2 C0)*

- **Expected C0:** "Westhaven should ban rental e-scooters from its streets." (unchanged from the broken member — the repair supplied the missing warrants, it did not change the recommendation.)
- **Acceptable paraphrase band:** any phrasing of *ban / prohibit / shut down the scooter program* as the recommended action counts as a hit. A claim about "scooters are dangerous" *without* the ban recommendation is a partial. Recovering "the council was wrong" as the main claim is a miss.

## GT2 — Failure locus *(Q2; §3 Support vs §4 Warrant)*

- **N/A — positive control.** There is no planted support/warrant/burden failure. The two inserted passages discharge the double warrant leap the broken member plants: the causal warrant (rate + confounders) and the remedy warrant (proportionality vs lighter remedies) are now *supplied*, not left for the reader. Firing WR0/FM-A6, WR2, or an SM failure here is a false positive.

## GT3 — Strongest real objection *(Q3; §6)*

- **N/A — positive control.** (For completeness: the confounding/base-rate objection the broken member ignores — "injuries *per ride*?" — is engaged head-on in locus 1, which supplies the denominator and rules out the displaced-trip and more-riders-outdoors confounders. The remedy-proportionality objection is engaged in locus 2.)

## GT4 — Audience calibration *(Q4; §1 Audience + AC codes)*

- **Audience profile:** Expertise GENERAL · Receptivity MIXED · Consequence MEDIUM *(carried from the broken member — the audience is unchanged; only the argument's warrant discharge changed)*
- **Calibration must IMPROVE diagnosis by:** recognizing this is an AT3 policy recommendation to a general/voter audience whose causal + comparative burden is now *met* — the audience awareness that *raised* the burden on the broken member should *credit* the twin for discharging it, not manufacture a new gap.
- **Calibration must NOT distort by:** inventing a warrant complaint because op-ed prose is punchy, or demanding a full methods section from a ~600-word op-ed that has already supplied the rate, the confounder disposal, and the remedy comparison in-register.

## GT5 — Dangerous weakness for red-team *(Q5; §10.4)*

- **N/A — positive control.** A red-team run should report the causal and remedy warrants are discharged and decline to manufacture a structural attack. The synthetic supporting figures (ridership volume, the speed-cap result) are the *design* of a clean twin, not a load-bearing weakness — see GT8 and Notes.

## GT6 — Repair order *(Q6; §10.5)*

- **N/A — positive control.** No repair sequence is warranted; the warrant is already established. Correct coaching output affirms the discharged warrants and offers at most advisory notes.

## GT7 — Warrant verdict *(Q7; §1 Warrant verdict / Step 9)* — **PRIMARY METRIC (pair discriminator)**

- **Expected warrant verdict:** WARRANTED
- **If unconventional:** N/A — conventional thesis-evidence op-ed form; the form does not carry the verdict, the discharged warrants do.
- **False-positive trap (the pair's planted-defect discriminator):** firing **WR0 / FM-A6** as a structural failure (or an SM failure, or a Must-Fix causal/remedy-warrant gap) **despite the supplied rate, confounder, and remedy warrants**. This is exactly the discriminator the broken member fires; on the clean member, firing it is Q7 = 0 *for the pair* and breaks the pair delta. An **advisory / Could-Fix** note (e.g. "the causal inference rests on the supplied ridership figure") does **not** fail the member — only a Must-Fix or a verdict defeat does.

## GT8 — Premise-plausibility flags
- **Expected premise flags:** NONE_REGISTERED
- **Must not adjudicate:** whether rental e-scooters in fact cause Westhaven's rising ED injury counts, nor whether the synthetic ridership / speed-cap figures the repair inserts are empirically accurate (they are synthetic-clean by construction).

## Notes

This is the specificity control for the `op-ed-warrant-leap` matched pair: near-identical
prose to the broken member, differing only by the two enumerated warrant insertions, so the
pair delta (broken fires WR0/FM-A6 as a structural failure; clean does not, on the same prose)
isolates the planted defect from the fixture's own authored roughness.

**Anti-gaming red-team (rule-2a general-evaluability standard, run before registration).** The
remedy passage does not merely *name* lighter remedies — a decorative foil that rule 2a says can
still defeat on evaluability — it shows each (helmet rules, speed caps, geofencing) was tried and
failed, with a stated mechanism, so a careful reader cannot defeat the twin on the general
evaluability test. The causal passage discharges to the general standard (rate + confounder
disposal), not the raw-count standard. A hostile reader was unable to re-defeat the twin on
FM-A6 or FM-A10 rule 2a; the repair set is therefore sufficient. The synthetic load-bearing
figures the repair inserts (ridership volume, the 15-mph speed-cap result, helmet spot counts)
are synthetic-clean by construction, so GT8 stays `NONE_REGISTERED` per the twin-authoring contract.
