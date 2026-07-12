# Argument Ground-Truth Template

**Schema: Argument Benchmark GT schema v0.3.0** (GT1–GT8; GT7 = Warrant verdict,
GT8 = Premise-plausibility flags; a required per-anchor Reliability ledger in Provenance).

Copy this file to `evals/fixtures/argument-benchmark/<fixture-slug>/groundtruth.md`
and fill in every in-scope field. Ground truth must be registered **before**
any engine run is scored against it (`groundtruth.md` written after seeing the
run output is void). Fields map to the seven scored roadmap test questions
(Q1–Q7) plus the GT8 contract surface, and to
`Argument_State.md` sections; see
[../docs/argument-benchmark-spec.md](../docs/argument-benchmark-spec.md) for
the schema rationale and
[rubrics/argument-benchmark.md](rubrics/argument-benchmark.md) for scoring.

Positive controls (correct diagnosis = WARRANTED or UNCONVENTIONAL-BUT-WARRANTED)
may mark GT2/GT3/GT5/GT6 as `N/A — positive control` and score Q1 + Q4 + Q7
only. State that in §Scope below. GT8 uses `NONE_REGISTERED` unless a load-bearing
premise's acceptability is separately registered. The **clean member of a matched pair** is
itself a positive control (same conventions); it additionally registers the pair's
planted-defect discriminator as its GT7 false-positive trap and carries a
`Base text + repair record` (see the pairing fields in §Provenance and
[../docs/argument-benchmark-spec.md](../docs/argument-benchmark-spec.md) §Matched pairs).

---

## Provenance

- **Fixture slug:** *(for a matched-pair member, deepen to `<pair-slug>/clean` or `<pair-slug>/broken`)*
- **Matched-pair member:** *(OPTIONAL — pairs only. `clean` | `broken` | `n/a (standalone)`. Omit both this field and `Paired-with` for an unpaired fixture; Check 7 requires them together. Leading token is enum-checked.)*
- **Paired-with:** *(OPTIONAL — pairs only. `<pair-slug>/<complement-member>` — a `clean` member names its `broken` twin and vice versa; must match this key's own `Fixture slug` pair. `n/a` for a standalone.)*
- **Base text + repair record:** *(REQUIRED on a `clean` member of a matched pair — the derived twin carries the derivation record. First line non-empty/non-N/A. Enumerate each repair edit: locus + before → after + which registered GT2 defect it discharges. The mutation diff IS the answer key: Check 7 rule 6 + the scripted repair-diff gate require 1:1 hunk↔locus correspondence with the broken member's `fixture.md`. Omit on unpaired fixtures and on the broken member — a derived-broken PD twin would carry `Base text + plant record` instead, fiction spelling, an M2 shape.)*
- **Bucket:** 1 op-ed / 2 policy brief / 3 testimony / 4 personal essay / 5 academic / 6 advocacy journalism / 7 hybrid
- **Source class:** synthetic-or-derived / public-domain
- **Text stored in-repo?:** yes / no (referenced — give citation + where the text is found)
- **Authored or adapted by:**
- **Registered (date):**
- **Ground-truth authority:** who established the diagnosis; adjudication notes if interpretive
- **Scope:** dimensions in scope for this fixture (e.g., "all seven + GT8" or "Q1, Q4, Q7 — positive control")
- **Reliability:** GT1–GT3: authoritative, gate; GT4–GT8: provisional, confirm *(one machine-parsed ledger line, GT schema v0.3.0. Groups split on `;`; each is `GT<a>(–GT<b>)?: <status>, <use>`; status ∈ authoritative | provisional | panel-licensed | low-agreement; use ∈ gate | confirm | report; coverage exactly GT1–GT8, no gaps/overlaps. Enforcement: `gate` requires a licensed status — authoritative or panel-licensed; `provisional` may only confirm/report; `low-agreement` may only report. A `|` or `/` in the ACTUAL value is rejected as copied guidance; a heading marked `(PROVISIONAL)` whose ledger claims a licensed status is a stale-marker error. Inter-rater agreement LICENSES a label — it never scores the engine; see [../docs/argument-benchmark-spec.md](../docs/argument-benchmark-spec.md) §GT schema for the ladder + pre-registered α thresholds.)*

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

## GT7 — Warrant verdict *(Q7; §1 Warrant verdict / Step 9)*

- **Expected warrant verdict:** WARRANTED / UNCONVENTIONAL-BUT-WARRANTED / UNWARRANTED
- **If unconventional:** form name + the form-dependent code(s) that MUST be downgraded to advisory
- **False-positive trap:** the structural code a naive audit fires here that would be WRONG

## GT8 — Premise-plausibility flags *(Q8; §1 / Dialectical Clarity Step 9 — acceptability axis)*

- **Expected premise flags:** NONE_REGISTERED | P1, P2, … *(leading token authoritative; a trailing `(provisional migration default)` is parser-ignored commentary)*
- **Flag details (one row per registered premise; omit entirely when NONE_REGISTERED):**
  - P1: <premise as used + location> | <load-bearing role: C0 / ground / subclaim / warrant / scope limiter / comparison / objection / definition / stakes> | <flag type(s), joined by ` + `: CONTESTABLE / UNEARNED / OVERLOADED / EXTERNAL-VERIFY / DEFINITIONAL> | <why a careful reviewer would not let it pass silently> | <Firewall boundary — the truth question NOT being adjudicated>
  *(Row shape is strict: exactly 5 `|`-cells; each ` + `-joined flag-type part must be exactly one enum token. Under an `UNCONVENTIONAL-BUT-WARRANTED` verdict, flags attach to the premises of the RECOVERED argument, not the surface/ironic one.)*
- **Must not adjudicate:** <the truth question the engine must not settle>

> **Firewall.** GT8 is a paper-reviewer flag, not a truth vote. It records that a load-bearing premise's *acceptability* is contestable; it never rules the premise true or false, and it never changes the GT7 warrant verdict by itself. For M1, GT8 is a required contract/firewall check; a scored premise-flag dimension is deferred to M2 (after keys are second-editor-confirmed).
>
> **Ownership boundary (do not double-register).** A GT8 flag MUST NOT duplicate a phenomenon a Dialectical Clarity code already carries: if the concern is that a premise is smuggled, unbacked, or ill-defined *as a warrant move*, the code owns it (it feeds the warrant verdict) — GT8 registers only the *residual acceptability* concern the codes do not own. When both could apply, the code takes it and GT8 stays `NONE_REGISTERED`.

## Notes

Free-form. Flag interpretive disagreements, dependencies on other fixtures,
and any known scoring ambiguity a reviewer needs to interpret results.
