# Ground Truth: personal-essay-narrative-arg

## Provenance

- **Fixture slug:** personal-essay-narrative-arg
- **Bucket:** 4 personal essay with implicit argument
- **Source class:** synthetic-or-derived
- **Text stored in-repo?:** yes — `fixture.md` is the verbatim engine input: argument text only, no metadata or comments. Critically for a positive control, the input carries **no hint of its control status** (an earlier draft leaked "this is a positive control" in a comment header — removed). All provenance/diagnosis lives here, never in the input file.
- **Synthetic-source note:** not a memoir of any real person; events and figures are invented. Do not quote as a real-world source.
- **Authored or adapted by:** APODICTIC benchmark (synthetic)
- **Registered (date):** 2026-05-30
- **Ground-truth authority:** author-registered; this is a **positive control** for the Q7 specificity gate
- **Scope:** Q1, Q4, Q7 (Q2/Q3/Q5/Q6 = N/A — positive control; there is no planted structural failure to locate, attack, or sequence-repair)
- **Reliability:** GT1–GT7: authoritative, gate; GT8: authoritative, report

## GT1 — Main claim *(Q1; §2 C0)*

- **Expected C0 (recovered, not stated):** "The social script for mourning — the 'casserole logic' of large early support that tapers on a schedule — is false to the actual shape of grief, which does not run on that clock."
- **Acceptable paraphrase band:** any recovery of *grief does not follow the prescribed/social timeline* or *the way we are taught to mourn mismatches lived grief* is a hit. The essay never states a thesis sentence; the claim is built by juxtaposition (casserole schedule vs. month-five bookshelf; the pamphlet chart vs. the floor). Recovering a claim *is the test* — a reader who finishes unable to state the claim indicates a real failure; a reader who recovers it confirms the form works. "An essay about losing a spouse" is a miss (that is the subject, not the claim).

## GT2 — Failure locus *(Q2)*

- **N/A — positive control.** There is no planted support/warrant/burden failure. The vignettes *are* the evidence and they do argumentative work (the chart, the manager's question, the unused foil pan each carry a step of the argument). Any SM0/WR failure reported here is a false positive.

## GT3 — Strongest real objection *(Q3)*

- **N/A — positive control.** (For completeness: the essay implicitly concedes the opposing view — "as a kindness to the living who must keep living" grants why the social script exists — which is itself dialectically fair handling, not a gap.)

## GT4 — Audience calibration *(Q4; §1 Audience + AC codes)*

- **Audience profile:** Expertise GENERAL · Receptivity SYMPATHETIC · Consequence LOW
- **Calibration must IMPROVE diagnosis by:** recognizing that for a general/sympathetic literary audience, an argument carried by image and juxtaposition is the *appropriate* form — explicitness would damage it. The audience can recover the claim; that is the relevant bar.
- **Calibration must NOT distort by:** demanding a thesis paragraph, a "counterargument section," or formal citations because some abstract template expects them. That demand would be a calibration *distortion* — penalizing effective form for a HOSTILE/EXPERT register the piece is not written for.

## GT5 — Dangerous weakness for red-team *(Q5)*

- **N/A — positive control.** A red-team run on this fixture should report that the argument is sound-as-form and decline to manufacture structural attacks. Manufacturing "weaknesses" here is itself the failure.

## GT6 — Repair order *(Q6)*

- **N/A — positive control.** No repair sequence is warranted. Correct coaching output is to affirm the form and (at most) offer advisory, non-prescriptive notes.

## GT7 — Warrant verdict *(Q7; §1 Warrant verdict / Step 9)* — **PRIMARY METRIC**

- **Expected warrant verdict:** UNCONVENTIONAL-BUT-WARRANTED
- **Form name:** narrative argumentation (conclusion emerges through juxtaposition of events and thematic reflection rather than an explicit thesis; recognized form per Dialectical Clarity Step 9).
- **Form-dependent codes that MUST be downgraded to advisory:** FM-A1 The Drive-By Thesis (no early thesis sentence), SM0 (no formal evidence units), and any "missing concession paragraph" finding. Step 9's decision tests pass: claim-accessibility ✓ (recoverable), evidence-evaluability ✓ (the vignettes), warrant-recoverability ✓ (two-clocks principle is stated), objection-awareness ✓ (the "kindness to the living" concession). Form-fit ✓ — the form does real work; it is not shielding weakness.
- **False-positive trap:** firing FM-A1 / SM0 as *structural failures* because the essay has no thesis sentence and no citations. That is the exact over-diagnosis the Distinguish protocol exists to prevent. An engine that fails this essay for "no clear thesis" scores **Q7 = 0** and blocks the bucket.

## GT8 — Premise-plausibility flags
- **Expected premise flags:** NONE_REGISTERED
- **Must not adjudicate:** whether grief in fact does not run on the socially prescribed "casserole logic" timeline.

## Notes

This fixture is the slice's specificity check. It is paired conceptually with
the public-domain `modest-proposal-satire` ground truth (text-not-stored): both
are unconventional forms a naive structural audit misfires on, one through
narrative juxtaposition and one through sustained irony. An engine can score
well on the two broken fixtures (op-ed, policy brief) and still fail the
benchmark here by being trigger-happy. Sensitivity without specificity is not
a passing engine.
