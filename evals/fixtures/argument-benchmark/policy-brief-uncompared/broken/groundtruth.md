# Ground Truth: policy-brief-uncompared/broken

## Provenance

- **Fixture slug:** policy-brief-uncompared/broken
- **Matched-pair member:** broken
- **Paired-with:** policy-brief-uncompared/clean
- **Bucket:** 2 policy brief
- **Source class:** synthetic-or-derived
- **Text stored in-repo?:** yes — `fixture.md` is the verbatim engine input: argument text only, no metadata or comments (so nothing leaks the answer key into the run). All provenance/diagnosis lives here, never in the input file.
- **Synthetic-source note:** invented policy brief; no real city, agency, or study is referenced. Do not quote as a real-world source.
- **Authored or adapted by:** APODICTIC benchmark (synthetic)
- **Registered (date):** 2026-05-30
- **Ground-truth authority:** author-registered; deterministic by construction (the comparative-burden and implementation gaps are planted; benefit evidence is intentionally adequate)
- **Scope:** all seven dimensions. This is the slice's designated Q5/Q6 fixture — Red Team and the argument session plan should be run.
- **Reliability:** GT1–GT7: authoritative, gate; GT8: authoritative, report

## GT1 — Main claim *(Q1; §2 C0)*

- **Expected C0:** "Rivermont should make Metro Transit fare-free starting next fiscal year."
- **Acceptable paraphrase band:** any phrasing of *eliminate/remove all fares / adopt fare-free transit* as the recommended policy is a hit. Recovering "transit is good for equity and emissions" as the main claim is a partial — that is the support, not the recommendation.

## GT2 — Failure locus *(Q2; §3 Support vs §4 Warrant)*

- **Primary failure layer:** BURDEN
- **Discriminator (why this layer, not the adjacent one):** The support for the *benefits* is adequate for the form — ridership, emissions, equity, and boarding-speed claims are each plausibly evidenced and point the same way. The break is not "the benefits are unproven" (support) and not a single missing inference (warrant). It is that an AT3 proposal carries a *comparative* burden the brief never discharges: it never compares fare-free transit to alternatives that target the same goals (fare-capping, means-tested free passes, congestion pricing, frequency/service investment), never costs the policy or names a funding mechanism, and never addresses opportunity cost (revenue forgone could buy more service). The benefits being real does not establish that *this* policy is the best use of the funds. Locating the failure in support ("add more benefit data") would deepen the actual error.
- **Expected codes:** **BP5** (missing alternatives — an AT3 proposal not comparatively defended; FM-A10's canonical signature code) + **OB3** (the dominated-alternative objection is unaddressed; FM-A10 fires "frequently with OB3" per the framework). **BP1** (evidence type mismatch — benefit data offered for a normative "should" recommendation) is an accepted-equivalent secondary if the scorer locates the scope gap there. Q2 = 3 requires BP5 as primary with the comparative-burden discriminator named.
- **Expected primary FM-A pattern + cluster:** FM-A10 The Uncompared Proposal (Dynamic). Signature AT3 + BP5, frequently with OB3.
- **Secondary patterns (if any):** FM-A18 Implementation Blindspot (no funding mechanism, no cost, no transition plan); FM-A2 The Evidence Pile (benefits accumulate in one direction with no countervailing analysis).

## GT3 — Strongest real objection *(Q3; §6)*

- **Objection zone:** opportunity cost / dominated alternative — the same forgone fare revenue could fund *more service* (frequency, coverage), which several analyses find raises ridership more per dollar than zero fares; fare-free may also induce low-value trips and crowd out paying riders' service quality. The brief engages no alternative and no objection.
- **Expected OB / DI codes:** **OB3** (the central objection for an AT3 recommendation — the dominated-alternative / opportunity-cost case — is missing entirely) + **OB0** (no objection of any kind is engaged). OB3 is the primary expected code; the proposal is not comparatively defended.

## GT4 — Audience calibration *(Q4; §1 Audience + AC codes)*

- **Audience profile:** Expertise MIXED (council + committee staff) · Receptivity MIXED · Consequence HIGH (budget-binding)
- **Calibration must IMPROVE diagnosis by:** recognizing that a *decision-making* audience with budget authority needs the comparative and fiscal case most of all — for this audience the missing funding mechanism and the missing alternatives analysis are the *decisive* gaps, not peripheral ones.
- **Calibration must NOT distort by:** treating the brief as adequate because it is persuasive and well-organized for a sympathetic reader. Polish and one-directional momentum are exactly the FM-A2/FM-A3 risk; audience calibration must not reward them.

## GT5 — Dangerous weakness for red-team *(Q5; §10.4)*

- **Pre-registered vulnerabilities (load-bearing):** (1) no funding mechanism / cost figure — the recommendation is unactionable and may be fiscally impossible; (2) dominated-alternative risk — service investment may beat zero-fare per dollar, which would defeat the recommendation even if every stated benefit holds; (3) the "20–60 percent ridership" range is borrowed from unnamed peer systems with unstated comparability to Rivermont.
- **Decoy weaknesses (should rank below):** quibbles with the exact emissions percentage; the rhetorical "deserve a system built around access" closing line. Real but not load-bearing.

## GT6 — Repair order *(Q6; §10.5)*

- **Correct first repair target:** burden — discharge the comparative + feasibility burden (cost the policy, name a funding source, compare to ≥1 alternative aimed at the same goals) before strengthening the benefit case.
- **Dependency rule the order must respect:** comparative/feasibility burden before further support acquisition. Adding more benefit evidence first leaves the decisive gap (is this the *best* use of the money, and can the city pay for it?) untouched.

## GT7 — Warrant verdict *(Q7; §1 Warrant verdict / Step 9)*

- **Expected warrant verdict:** UNWARRANTED
- **If unconventional:** N/A — conventional policy-brief form; the form does not explain the failure.
- **False-positive trap:** do not call this WARRANTED because the prose is competent, the structure is clean, and every benefit claim is supported. The one-directional evidence pile is the tell, not a strength.

## GT8 — Premise-plausibility flags
- **Expected premise flags:** NONE_REGISTERED
- **Must not adjudicate:** whether fare-free transit would in fact produce the claimed ridership, emissions, and equity benefits for Rivermont.

## Notes

This fixture isolates the *comparative burden* that AT3 proposals carry and is
the slice's Q5/Q6 anchor. Note the deliberate contrast with
`op-ed-warrant-leap`: there the support is the strong part and the *warrant*
breaks; here the support is the strong part and the *burden* breaks. An engine
that lumps both into "weak evidence" has failed Q2 on both fixtures for the
same reason.
