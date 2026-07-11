# Ground Truth: op-ed-warrant-leap/broken

## Provenance

- **Fixture slug:** op-ed-warrant-leap/broken
- **Matched-pair member:** broken
- **Paired-with:** op-ed-warrant-leap/clean
- **Bucket:** 1 op-ed
- **Source class:** synthetic-or-derived
- **Text stored in-repo?:** yes — `fixture.md` is the verbatim engine input: argument text only, no metadata or comments (so nothing leaks the answer key into the run). All provenance/diagnosis lives here, never in the input file.
- **Synthetic-source note:** invented op-ed; no real city, hospital, or person is referenced. Do not quote as a real-world source.
- **Authored or adapted by:** APODICTIC benchmark (synthetic)
- **Registered (date):** 2026-05-30
- **Ground-truth authority:** author-registered; deterministic by construction (the warrant gap is planted)
- **Scope:** all seven dimensions (Q5/Q6 scored if Red Team + session plan are run; otherwise Q1–Q4, Q7)
- **Reliability:** GT1–GT7: authoritative, gate; GT8: authoritative, report

## GT1 — Main claim *(Q1; §2 C0)*

- **Expected C0:** "Westhaven should ban rental e-scooters from its streets."
- **Acceptable paraphrase band:** any phrasing of *ban / prohibit / shut down the scooter program* as the recommended action counts as a hit. A claim about "scooters are dangerous" *without* the ban recommendation is a partial (the recommendation is the actual C0, the danger claim is a subclaim). Recovering "the council was wrong" as the main claim is a miss.

## GT2 — Failure locus *(Q2; §3 Support vs §4 Warrant)*

- **Primary failure layer:** WARRANT
- **Discriminator (why this layer, not the adjacent one):** The *support* is unusually clean for an op-ed — counted ED visits, a named records source, a confirmatory quote, 911 logs. Step 3 should largely PASS the support map: the data exists and is specific. The break is the inferential bridge. The piece moves from "injuries rose when scooters appeared" to "scooters caused the injuries" to "a ban is the proportionate remedy" with no warrant. Confounders (more riders outdoors, displaced car trips, denominator = rides taken) are never addressed; the causal warrant and the remedy warrant are both leapt. Diagnosing this as a *support* failure ("needs more data") would be wrong — more of the same data cannot close a warrant gap.
- **Expected codes:** **WR0** (warrant gap — the causal premise "scooters *caused* the injuries" and the remedy premise "a ban is the proportionate response" must both be supplied by the reader; this is FM-A6's canonical signature code) + **WR2** (scheme fragility — a causal claim resting only on temporal sequence, the literal WR2 example). SM = PASS (evidence is clean and specific). A scorer earns Q2 = 3 by reporting WR0 (primary) + WR2 and explicitly *not* firing an SM failure.
- **Expected primary FM-A pattern + cluster:** FM-A6 The Warrant Leap (Relational). Signature WR0 with otherwise-clean SM.
- **Secondary patterns (if any):** FM-A4 Scope Inflation (Dynamic) → **BP2** (scope creep — a local ED signal asserted as grounds for a citywide ban); **BP0** also acceptable if the scorer reads the per-rider risk scope as undeclared (raw counts presented without a rate/denominator). BP2 is the primary expected code; BP0 is an accepted-equivalent. **FM-A10 The Uncompared Proposal (Dynamic) → BP5** also co-fires and is registered here as a **real but structurally SUBORDINATE** second defeater: the ban names zero remedy-alternatives (helmet rules, speed caps, geofencing), so rule 2a's zero-comparison FM-A10 defeat legitimately fires — it is *not* an over-fire. It is subordinate to the causal warrant leap per **GT6**: the remedy comparison (L2 — "ban vs. lighter measures") presupposes the causal warrant (L1 — "scooters cause the injuries"), so it is moot until causation is warranted. Its subordinate signature is **BP5** + the missing dominated-alternative objection *in prose, uncoded*. (That objection is **not** coded here: the code for the central objection is reserved by GT3 for the *confounding / base-rate* zone — central precisely *because* the causal warrant leap is the primary failure — and the remedy-comparison objection is a distinct, subordinate referent, left uncoded to keep GT3's central-objection code unambiguous.)
- **Primacy boundary (Q2 scoring — the M1 caveat #1 trap).** Both blind engines (Fable + Codex 5.6, 2026-07-09) returned the correct verdict (UNWARRANTED) but ranked **FM-A10 / BURDEN / the uncompared ban** as the *primary* locus, subordinating the causal warrant leap. That is a **mis-rank**, scored on the rubric's 0–3 Q2 band by whether the run *surfaced the registered primary at all*:
  - **Surfaced WR0 / the WARRANT locus but ranked it *below* FM-A10 / BURDEN → cap Q2 = 2.** It located the warrant layer and its codes but inverted the failure-locus discriminator (naming the subordinate BURDEN defeat as primary), so it does not earn Q2 = 3's "*why this layer and not the adjacent one*" — an *inverted* discriminator (rubric band 2's "discriminator unstated," read to include an inversion) cannot reach band 3. (The two 2026-07-09 runs are here: both fired WR0, both mis-ranked → Q2 = 2 each.)
  - **Omitted the causal warrant leap / never surfaced WR0 or the WARRANT locus → Q2 = 0** ("located in the wrong layer / conflated support and warrant") — a **miss**. Surfacing the WARRANT locus is the **necessary condition** for any partial credit; a warrant-leap-*blind* run earns nothing here. (Deficit-Lock: a locked locus miss is never laundered into charitable partial credit.)
  - This is **not** a GT-as-a-set expansion. FM-A6 is the **sole registered primary**; FM-A10 is a registered **subordinate**. A co-equal *FM-A6-OR-FM-A10* reading is **rejected** under the GT-as-a-set discipline (CORPUS.md; the four guards are numbered in PROPOSAL-gt-sets-20260604.md): guard #1 (a member must be structurally *prior*, not merely salient or reliably-found — FM-A10 is downstream of the causal warrant per GT6) and guard #4 (no expansion that flips a fixture to "pass" by blessing a run's ranking error — it would let a warrant-leap-blind run score Q2 = 3, dissolving the SUPPORT-vs-WARRANT discriminator this fixture exists to isolate). The engine-side fix that makes runs *earn* Q2 = 3 is rule 2a's primacy-override in `dialectical-clarity.md`; this note is the scoring contract that override must satisfy.

## GT3 — Strongest real objection *(Q3; §6)*

- **Objection zone:** confounding / base-rate — the injury rise could reflect more riders, displaced (more dangerous) car trips avoided, or simply usage volume with no per-trip risk increase; the piece offers raw counts, not a rate. The strongest skeptic asks "injuries *per ride*?" The op-ed engages no objection at all.
- **Expected OB / DI codes:** **OB0** (no objections engaged — the piece proceeds as if no reasonable person could disagree) + **OB3** (the *central* confounding/base-rate objection is the one a well-informed skeptic raises first and it is missing entirely). Either code alone is a partial; Q3 = 3 requires naming the confounding/base-rate zone and classifying it OB3 (with OB0 as the general condition).

## GT4 — Audience calibration *(Q4; §1 Audience + AC codes)*

- **Audience profile:** Expertise GENERAL · Receptivity MIXED · Consequence MEDIUM
- **Calibration must IMPROVE diagnosis by:** recognizing this is an AT3 policy recommendation to a general/voter audience, where the burden is causal + comparative, not merely "show the numbers went up." Audience awareness should *raise*, not lower, the warrant burden.
- **Calibration must NOT distort by:** excusing the warrant leap as acceptable op-ed rhetoric ("op-eds are allowed to be punchy"). Genre tolerance for brevity is not tolerance for an absent causal warrant on a HIGH-consequence ban.

## GT5 — Dangerous weakness for red-team *(Q5; §10.4)*

- **Pre-registered vulnerabilities (load-bearing):** (1) no denominator — counts without ride-volume make the "222 percent" uninterpretable as risk; (2) post hoc causal claim with unexamined confounders; (3) ban is never compared to lighter remedies (helmet rules, speed caps, geofencing), so the remedy is unjustified even if causation held.
- **Decoy weaknesses (should rank below):** the snide tone toward the council; the rhetorical "nobody voted for it" line. These are stylistic, not load-bearing — a red-team that leads with tone has missed the argument.

## GT6 — Repair order *(Q6; §10.5)*

- **Correct first repair target:** warrant (establish causation with a rate/denominator and address confounders) before anything else.
- **Dependency rule the order must respect:** warrant repair precedes both adding evidence and defending the remedy. Adding more raw-count data first (support acquisition) is the wrong move; comparing remedies is moot until causation is warranted.

## GT7 — Warrant verdict *(Q7; §1 Warrant verdict / Step 9)*

- **Expected warrant verdict:** UNWARRANTED
- **If unconventional:** N/A — this is conventional thesis-evidence op-ed form; the form does not explain the failure.
- **False-positive trap:** do *not* downgrade the warrant finding by mistaking confident, well-sourced prose for inferential soundness. The piece reads rigorous (real data, named sources) precisely where it is weakest. The trap is calling it WARRANTED because it cites evidence.

## GT8 — Premise-plausibility flags
- **Expected premise flags:** NONE_REGISTERED
- **Must not adjudicate:** whether rental e-scooters are in fact the cause of Westhaven's rising ED injury counts.

## Notes

This fixture isolates the Q2 SUPPORT-vs-WARRANT discriminator. A correct run
should *praise* the evidence specificity and still fail the argument on the
warrant — the two findings must coexist. An engine that fails the support
("not enough data") has mislocated the break.
