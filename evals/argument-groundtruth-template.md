# Argument Ground-Truth Template

**Schema: Argument Benchmark GT schema v0.2.0** (GT1–GT8; GT7 = Warrant verdict,
GT8 = Premise-plausibility flags).

Copy this file to `evals/fixtures/argument-benchmark/<fixture-slug>/groundtruth.md`
and fill in every in-scope field. Ground truth must be registered **before**
any engine run is scored against it (`groundtruth.md` written after seeing the
run output is void). Fields map to the eight roadmap test questions and to
`Argument_State.md` sections; see
[../docs/argument-benchmark-spec.md](../docs/argument-benchmark-spec.md) for
the schema rationale and
[rubrics/argument-benchmark.md](rubrics/argument-benchmark.md) for scoring.

Positive controls (correct diagnosis = WARRANTED or UNCONVENTIONAL-BUT-WARRANTED)
may mark GT2/GT3/GT5/GT6 as `N/A — positive control` and score Q1 + Q4 + Q7
only. State that in §Scope below. GT8 uses `NONE_REGISTERED` unless a load-bearing
premise's acceptability is separately registered.

---

## Provenance

- **Fixture slug:**
- **Bucket:** 1 op-ed / 2 policy brief / 3 testimony / 4 personal essay / 5 academic / 6 advocacy journalism / 7 hybrid
- **Source class:** synthetic-or-derived / public-domain
- **Text stored in-repo?:** yes / no (referenced — give citation + where the text is found)
- **Authored or adapted by:**
- **Registered (date):**
- **Ground-truth authority:** who established the diagnosis; adjudication notes if interpretive
- **Scope:** dimensions in scope for this fixture (e.g., "all eight" or "Q1, Q4, Q7 — positive control")

## GT1 — Main claim *(Q1; `Argument_State` §2 C0)*

- **Expected C0:** [one sentence — extractable from the text, not invented]
- **Acceptable paraphrase band:** [what wording counts as a hit; what counts as a miss]

## GT2 — Failure locus *(Q2; §3 Support vs §4 Warrant)*

- **Primary failure layer:** SUPPORT / WARRANT / BURDEN / OBJECTION / NONE
- **Discriminator (why this layer, not the adjacent one):**
- **Expected codes:** [SM* / WR* / BP* / OB* / DI*]
- **Expected primary FM-A pattern + cluster:** [FM-Ax — Architectural / Relational / Quality / Dynamic]
- **Secondary patterns (if any):**

## GT3 — Strongest real objection *(Q3; §6)*

- **Objection zone:** [the strongest objection a careful skeptic raises]
- **Expected OB / DI codes:**

## GT4 — Audience calibration *(Q4; §1 Audience + AC codes)*

- **Audience profile:** Expertise GENERAL/MIXED/EXPERT · Receptivity SYMPATHETIC/MIXED/HOSTILE · Consequence LOW/MEDIUM/HIGH
- **Calibration must IMPROVE diagnosis by:** [what attending to this audience should surface]
- **Calibration must NOT distort by:** [the over-calibration / audience-pleasing failure to avoid]

## GT5 — Dangerous weakness for red-team *(Q5; §10.4)*

- **Pre-registered vulnerabilities (load-bearing weaknesses):**
- **Decoy weaknesses (plausible but not load-bearing; should rank below):**

## GT6 — Repair order *(Q6; §10.5)*

- **Correct first repair target:** claim / warrant / support / definition / objection
- **Dependency rule the order must respect:** [e.g., warrant repair before evidence acquisition]

## GT7 — Warrant verdict *(Q7; §1 Distinguish / Step 9)*

- **Expected warrant verdict:** WARRANTED / UNCONVENTIONAL-BUT-WARRANTED / UNWARRANTED
- **If unconventional:** form name + the form-dependent code(s) that MUST be downgraded to advisory
- **False-positive trap:** the structural code a naive audit fires here that would be WRONG

## GT8 — Premise-plausibility flags *(Q8; §1 / Dialectical Clarity Step 9 — acceptability axis)*

- **Expected premise flags:** NONE_REGISTERED | P1, P2, … *(leading token authoritative; a trailing `(provisional migration default)` is parser-ignored commentary)*
- **Flag details (one row per registered premise; omit entirely when NONE_REGISTERED):**
  - P1: <premise as used + location> | <load-bearing role: C0 / subclaim / warrant / scope limiter / comparison / objection / definition / stakes> | <flag type(s), joined by ` + `: CONTESTABLE / UNEARNED / OVERLOADED / EXTERNAL-VERIFY / DEFINITIONAL> | <why a careful reviewer would not let it pass silently> | <Firewall boundary — the truth question NOT being adjudicated>
- **Must not adjudicate:** <the truth question the engine must not settle>

> **Firewall.** GT8 is a paper-reviewer flag, not a truth vote. It records that a load-bearing premise's *acceptability* is contestable; it never rules the premise true or false, and it never changes the GT7 warrant verdict by itself. For M1, GT8 is a required contract/firewall check; a scored premise-flag dimension is deferred to M2 (after keys are second-editor-confirmed).

## Notes

Free-form. Flag interpretive disagreements, dependencies on other fixtures,
and any known scoring ambiguity a reviewer needs to interpret results.
