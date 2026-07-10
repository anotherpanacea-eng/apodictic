# Argument Engine Benchmark Suite
## Nonfiction Argument Engine — Validation Spec

*Version: 0.1.0*
*Status: Active — vertical slice landed; corpus expansion in progress*
*Last updated: May 30, 2026*
*Depends on: Dialectical Clarity v2.0, Argument State Schema v0.1.1*

---

## Purpose

The Nonfiction Argument Engine is built: Dialectical Clarity v2.0 is the
diagnostic kernel, `Argument_State.md` is the shared artifact, and eight
companion modules (Red Team, Persuasion, Evidence Deep-Dive, Citation
Verifier, Field Reconnaissance, Adversarial Evidence Review, nonfiction
intake routing, Revision Coach argument mode) read and annotate that
state. What the engine lacks is **evidence that it works on real
argument-shaped nonfiction, not just in theory.**

This spec defines a corpus-based benchmark that answers a single question:
*when a competent editor already knows the correct structural diagnosis of
a piece, does the engine recover it?* It operationalizes the seven test
questions and the convergence success-condition recorded in
[`ROADMAP.md` §Nonfiction Argument Engine → Benchmark Suite](../ROADMAP.md).

**This document defines the benchmark. It does not change the engine.** If
the benchmark surfaces a real engine failure, that is a separate work item
against Dialectical Clarity or a companion module.

---

## Relationship to existing eval infrastructure

The benchmark is a *specialization* of the existing APODICTIC eval harness,
not a parallel system.

| Layer | Source of truth | Lives where |
|-------|-----------------|-------------|
| Shared metrics (0–3 scale), decision rules, binary checks, failure attribution, fixture-provenance policy | `docs/eval-harness-spec.md` (local-only) | gitignored |
| Blind-review packet format + convergence protocol substrate | `docs/blind-review-protocol.md` (local-only) | gitignored |
| Argument-specific scoring, ground-truth schema, corpus design | **this file** | in-repo |
| Argument rubric (dimensions → checks) | `evals/rubrics/argument-benchmark.md` | in-repo |
| Per-fixture ground-truth template | `evals/argument-groundtruth-template.md` | in-repo |
| Vertical-slice fixtures + ground truth | `evals/fixtures/argument-benchmark/` | in-repo (synthetic + public-domain only) |
| Per-fixture manifests (name a manuscript) | `evals/manifests/*.md` | gitignored |

The argument benchmark reuses the shared 0–3 metric scale and the
accept / accept-with-override / revise-and-retest / reject decision rules
defined in `eval-harness-spec.md`. It adds seven argument-specific
dimensions and a ground-truth answer-key schema that the generic rubrics do
not need.

---

## Corpus design

### Buckets

Seven corpus buckets, per the roadmap. Each exercises a different cluster of
the engine's failure modes and a different region of the audience-calibration
matrix.

| # | Bucket | Signature failure modes to exercise | Audience profile bias |
|---|--------|--------------------------------------|------------------------|
| 1 | Op-eds | FM-A6 Warrant Leap, FM-A4 Scope Inflation, OB gaps | GENERAL / MIXED receptivity |
| 2 | Policy briefs | FM-A10 Uncompared Proposal, BP5, FM-A18 Implementation Blindspot | MIXED-EXPERT / HIGH consequence |
| 3 | Testimony (legislative / judicial / administrative) | NE-codes, BP6 testimony overextension, FM-A17 Anecdote-to-Principle | INSTITUTIONAL / HIGH consequence |
| 4 | Personal essays with implicit argument | Distinguish (unconventional form), FM-A1 false-positive risk | GENERAL / SYMPATHETIC |
| 5 | Academic argument | FM-A8 False Precision, FM-A11 Evidence Laundering, WR backing | EXPERT |
| 6 | Advocacy journalism | FM-A3 Persuasion Machine, FM-A9 Concession Without Cost, FM-A14 Epistemic Erasure | MIXED / partisan |
| 7 | Argument-with-embedded-narrative hybrids | NE function classification, dual-audit handoff (Narrative Nonfiction Craft) | MIXED |

### Provenance strategy (four tiers)

Only **public-domain** and **synthetic-or-derived** text may be *stored* in-repo
(`eval-harness-spec.md §Fixture Provenance Policy`). Real modern op-eds,
testimony, and journalism are copyrighted, so their **text is never stored** —
but a *published* work can be *referenced* by public URL with its answer key
(citation + diagnosis, no source text) living in-repo, while *unpublished /
private* manuscripts are referenced only by gitignored manifest. The corpus
draws on four tiers:

1. **Synthetic fixtures (primary).** Argument-shaped pieces authored for the
   benchmark with a *planted, pre-registered* failure. These give
   deterministic ground truth (we know what we put in), are fully shareable
   in-repo, and isolate one diagnostic discriminator at a time. They are the
   backbone of the failure-detection tests (Q1–Q6).

2. **Public-domain exemplars (controls + hard cases).** Real historical
   arguments whose form is well understood. These anchor the
   *don't-penalize-unconventional-form* test (Q7) with genuine cases a naive
   structural audit would misfire on. Mapped exemplars:
   - Swift, *A Modest Proposal* (1729) — satire / sustained irony. The
     hardest Q7 trap: the surface argument is monstrous; the real argument
     emerges through irony. Text not stored; referenced by a pinned immutable
     source (Project Gutenberg eBook #1080) with a boilerplate-independent
     analyzed-text scope and a record-on-first-retrieval checksum — see the
     fixture's `groundtruth.md`.
   - Frederick Douglass, *What to the Slave Is the Fourth of July?* (1852) —
     prophetic address / call-and-response. Bucket 3 (testimony) + Q7.
   - *Federalist* No. 10 (1787) — academic/policy argument with explicit
     warrant structure; a *positive* control (should largely PASS). Bucket 5.

3. **Third-party published works (external validity).** Real, published,
   attributed arguments (op-eds, manifestos, think-tank briefs, academic
   papers) — referenced by public URL; **text never stored** (copyright), but
   the citation + an independently-authored diagnosis live in-repo (paraphrase
   only). These supply contemporary register, live stakes, and a
   *pre-registered, single-editor* ground truth (registered before any run;
   the independence is **temporal, not personal** — the editor is the benchmark
   author, so it is not yet a second-editor cross-check). Most are competent
   arguments with one structural soft spot, so their primary value is
   **severity calibration** (does the engine resist over-pathologizing a
   sound argument?), complementing the synthetic corpus's catastrophic failures.
   Registered in `evals/fixtures/argument-benchmark/CORPUS.md`.

4. **Private / unpublished / client manuscripts.** Referenced by gitignored
   manifest and never named in-repo (confidentiality). Added when external
   validity beyond published sources is needed.

> **Run environment note.** Referenced fixtures (tiers 2–4) require fetching the
> source at run time, so they can only be run where outbound web access is
> available. The build/CI sandbox blocks it; runs happen in a web-enabled
> session.

### Anti-overfit guard: positive controls are mandatory

A benchmark that only contains broken arguments measures sensitivity but not
specificity — it cannot catch an engine that "finds" failures everywhere.
**Every bucket must include at least one positive control**: a
structurally sound (or soundly unconventional) piece whose correct diagnosis
is WARRANTED or UNCONVENTIONAL-BUT-WARRANTED. The Q7 dimension is scored
*primarily* on these controls. Swift's *A Modest Proposal* and the unconventional
personal essay are the slice's positive controls.

---

## Ground-truth answer-key schema

Each fixture ships a pre-registered answer key (`groundtruth.md`) that
encodes "the correct structural diagnosis a competent editor would reach."
Ground truth is **registered before** any engine run is scored, so scoring
cannot be retrofitted to the engine's output. The schema maps each of the
seven roadmap test questions onto fields keyed to `Argument_State.md`
sections and the Dialectical Clarity code namespace.

```markdown
# Ground Truth: <fixture-slug>

## Provenance
- Bucket: <1–7 / bucket name>
- Source class: synthetic-or-derived | public-domain
- Text stored in-repo: yes | no (referenced)
- Authored / adapted by: <name>  | Registered: <date>
- Ground-truth authority: <who established it; adjudication notes>

## GT1 — Main claim (Q1; Argument_State §2 C0)
- Expected C0: <one sentence>
- Acceptable paraphrase band: <what counts as a hit; what does not>

## GT2 — Failure locus (Q2; §3 Support vs §4 Warrant)
- Primary failure layer: SUPPORT | WARRANT | BURDEN | OBJECTION | NONE
- Why this layer and not the adjacent one: <the discriminator>
- Expected codes: <SM* / WR* / BP* / OB*>
- Expected primary FM-A pattern + cluster: <FM-Ax (Architectural/Relational/Quality/Dynamic)>

## GT3 — Strongest real objection (Q3; §6)
- Objection zone: <the strongest objection a careful skeptic raises>
- Expected OB / DI codes: <…>

## GT4 — Audience calibration (Q4; §1 Audience, AC codes)
- Audience profile: Expertise <…> / Receptivity <…> / Consequence <…>
- Calibration must IMPROVE diagnosis by: <what calibration should surface>
- Calibration must NOT distort by: <the over-calibration failure to avoid>

## GT5 — Dangerous weakness for red-team (Q5; §10.4)
- Pre-registered vulnerabilities (the genuinely load-bearing weaknesses): <…>
- Decoy weaknesses (plausible but not load-bearing; red-team should rank below): <…>

## GT6 — Repair order (Q6; §10.5)
- Correct first repair target: <claim | warrant | support | definition | objection>
- Dependency rule the order must respect: <e.g., warrant before support>

## GT7 — Warrant verdict (Q7; §1 Distinguish, Step 9)
- Expected warrant verdict: WARRANTED | UNCONVENTIONAL-BUT-WARRANTED | UNWARRANTED
- If unconventional: form name + which form-dependent codes MUST be downgraded
- False-positive trap: <the structural code a naive audit fires that is WRONG here>

## GT8 — Premise-plausibility flags (Q8; §1 / Step 9 — acceptability axis)
- Expected premise flags: NONE_REGISTERED | P1, P2, … (leading token authoritative; a trailing `(provisional migration default)` is parser-ignored commentary)
- Flag details (one row per registered premise; omit when NONE_REGISTERED):
    P<n>: <premise as used> | <load-bearing role> | <flag type(s), joined by ` + `: CONTESTABLE / UNEARNED / OVERLOADED / EXTERNAL-VERIFY / DEFINITIONAL> | <why flagged> | <Firewall boundary>
- Must not adjudicate: <the truth question the engine must not settle>
```

GT7 (warrant verdict) is the inference axis — whether the reasoning warrants the
conclusion on the text's own terms (Wachsmuth cogency's Local Relevance + Local
Sufficiency). GT8 (premise-plausibility flags) is the acceptability axis (Local
Acceptability), **surfaced but never adjudicated**: the Firewall forbids ruling a
premise true or false, so GT8 is a flag, not a verdict. In M1, GT8 is a required
contract/firewall check (see §Mechanical validator), **not** a scored dimension; a
scored premise-flag dimension is deferred to M2 after keys are second-editor-confirmed.
This is **Argument Benchmark GT schema v0.3.0** (GT1–GT8, plus a required per-anchor
Reliability ledger — below).

The schema is deliberately *thin*: it records structure, not a model answer
essay. A fixture's ground truth should fit in well under a page.

### The Reliability ledger (agreement-as-license)

The ground truth carries a trust distinction — GT1–GT3 authoritative, GT4–GT8
provisional on real pieces — that was previously prose-only. v0.3.0 mechanizes it as one
**Reliability ledger line** in each fixture's Provenance block, assigning every GT anchor a
**status** and a **decision-use**:

| Status | Meaning | May `gate`? |
|---|---|---|
| `authoritative` | Licensed **by construction** (synthetic planted defect) or **by the objective-core convention** (a pre-registered GT1–GT3-grade diagnosis, temporally independent of any run; the controls' GT7 against uncontested scholarly readings) | yes |
| `provisional` | One editor's registration on a genuinely-judgment anchor (GT4–GT8 on real pieces); awaiting confirmation | no — `confirm`/`report` only |
| `panel-licensed` | Promoted by measured ≥3-editor agreement (Krippendorff's α over the gate threshold) — the M2 outcome | yes |
| `low-agreement` | The panel measured poor agreement; the construct is unstable — reclassify or widen the band, **never** score the engine against it | no — `report` only |

Decision-use: **`gate`** (a run's miss may be booked an engine failure; requires a licensed
status), **`confirm`** (scored against the key and named in convergence where the class rules
already name it; a disagreement is attributed by direction — see §Convergence), **`report`**
(recorded for completeness; no accuracy claim; never part of convergence).

**Enforcement (parser-checked, Check 6):** `gate` ⇒ status ∈ {`authoritative`,
`panel-licensed`}; `provisional` ⇒ use ∈ {`confirm`, `report`}; `low-agreement` ⇒ use =
`report`. Coverage must be exactly GT1–GT8 with no gaps or overlaps. A heading still marked
`(PROVISIONAL)` whose ledger claims a licensed status is a stale-marker error (the M2-promotion
tripwire). The grammar is section-level; sub-field provisionality (e.g. GT2's authoritative
*locus* vs provisional *codes*) stays a prose convention.

The licensing model is the psychometric frame the fiction benchmark already ships
(`scripts/fiction_groundtruth.py`): inter-rater agreement **licenses** whether a label may
gate; it never scores the engine, and poor agreement means *the construct is unstable*, never
*the engine failed*. The token sets stay domain-honest (argument's `authoritative` names an
objective-core convention fiction has no analog for), mapped here — **documentation only; no
drift guard ships**, and the table is hand-updated if either vocabulary ever changes:

| argument | fiction | note |
|---|---|---|
| `authoritative` | `deterministic` ∪ (no analog) | argument adds the editor-preregistered objective core |
| `provisional` | `provisional_author` | same rung |
| `panel-licensed` | `panel_confirmed` | same rung, same α machinery |
| `low-agreement` | `low_agreement` | same rung |

**Pre-registered promotion thresholds (Krippendorff's own canonical cutoffs, registered before
any panel data exists — registering thresholds after seeing α is the same sin as writing keys
after seeing runs):** α ≥ .800 → promote to `panel-licensed` (may gate); .667 ≤ α < .800 →
remains `provisional` (reportable with a "tentative" caveat); α < .667 → `low-agreement`
(report-only; reclassify/widen/repair the coding scheme). Metric per dimension:
**ordinal-weighted α** for the GT4 sub-scales (three ordinal items), **nominal α** for GT2
layer, GT6 first-repair target, GT7 verdict (three tokens treated as nominal, with a secondary
collapsed warranted-family-vs-`UNWARRANTED` binary reported), and GT8 flag presence. With
small n (10 real-corpus units), license on the **bootstrap-CI lower bound** clearing the
threshold; a multi-subscale section promotes only if **every** in-scope subscale clears (min-of-
subscales). α is computed by the audited `agreement-alpha` CLI (shipped separately); model-run
agreement is a floor, **never** a license — only the M2 editor panel promotes a status.

---

## Scoring: the seven dimensions

Each fixture run is scored on seven argument-specific dimensions, on the
shared 0–3 scale (`eval-harness-spec.md §Core Metrics`). The detailed
band definitions and binary checks live in
`evals/rubrics/argument-benchmark.md`. Summary:

| Dim | Test question | What 3 looks like | What 0 looks like |
|-----|---------------|-------------------|-------------------|
| Q1 | Recovered the actual main claim? | C0 matches GT1 within the paraphrase band | recovered a different or invented claim |
| Q2 | Distinguished support failure from warrant failure? | failure layer + codes match GT2; discriminator named | conflated SM and WR; located the failure in the wrong layer |
| Q3 | Identified the strongest real objection? | objection zone matches GT3 | engaged only weak/decoy objections |
| Q4 | Audience calibration improved rather than distorted? | calibration surfaced GT4's "improve" item without the "distort" failure | calibration produced an audience-pleasing distortion or was ignored |
| Q5 | Red-team surfaced genuinely dangerous weaknesses? | hit ≥1 pre-registered vulnerability, ranked above decoys | surfaced only decoys / cosmetic attacks |
| Q6 | Coaching produced a useful repair order? | first target + dependency rule match GT6 | repair order violates the dependency (e.g., adds evidence before fixing the warrant) |
| Q7 | Avoided penalizing unconventional but effective form? | Warrant verdict matches GT7; trap code downgraded | fired the false-positive trap code as a structural failure |

**Q7 is scored primarily on positive controls** and is the benchmark's
specificity check. A false-positive trap fired on a control is a 0 regardless
of how well Q1–Q6 scored on broken fixtures.

### Binary checks (per fixture, from the shared harness)

- No invented content (Firewall): the engine added no claim, warrant, or
  objection the text does not contain.
- Distinguish protocol ran (Step 9 present) on every fixture.
- `Argument_State.md` emitted and §§1–9 populated.
- Model tag and run-folder naming follow policy.

---

## Convergence protocol (the success condition)

The roadmap's success condition is an inter-rater statement, not a
single-run statement:

> Two serious editors using the engine independently should usually converge
> on the core claim, the top 1–3 structural failures, the main burden
> mismatch, and the strongest objection zone.

Operationalized:

1. **Two independent *engine* runs per fixture.** Convergence is a property of
   two independent *productions* of a diagnosis, not two scorings of one
   production. Independence is achieved by *one* of: (a) two different editors
   each driving the engine on the fixture; (b) two model configurations (e.g.,
   baseline vs. comparator) each producing a full run. The slice uses (b); (a)
   is added when external editors are available. **Two reviewers scoring the
   same single output is _not_ an independence path** — that measures scorer
   reliability (see below), not convergence, and must never be used to pass the
   convergence gate.
2. **Convergence is measured on four anchors (failure-bearing fixtures):** core
   claim (GT1), top 1–3 structural failures (GT2 primary + secondary), main
   burden mismatch (GT2 BURDEN / GT4), strongest objection zone (GT3).
   *Positive controls use a different anchor set — see below.*
3. **Agreement threshold:** the two runs *converge* on a failure-bearing fixture
   when they agree on ≥3 of the 4 anchors, with the core-claim anchor (GT1)
   mandatory among them. "Agree" means both runs land in the same ground-truth
   band.
4. **Suite-level success:** the engine passes a bucket when ≥⅔ of that
   bucket's fixtures converge, with no positive control mis-classified
   (Q7 = 0). Suite passes when every bucket passes.

### Positive-control convergence

Positive controls have no planted failure, so three of the four anchors above
(top failures, burden mismatch, objection zone) are N/A and the ≥3-of-4 rule
cannot be computed. Controls converge on a **control-specific anchor set**:

1. **Claim (GT1)** — both runs recover the claim within the GT1 paraphrase band.
2. **Warrant verdict (GT7)** — both runs return the GT7
   verdict (WARRANTED or UNCONVENTIONAL-BUT-WARRANTED).
3. **No invented failure** — *neither* run fires the GT7 false-positive trap
   code or fabricates a Must-Fix structural failure, objection, or burden gap.

A control **converges only when all three hold.** Anchor 3 is also the
specificity check: a run that violates it scores Q7 = 0 for that fixture and,
per item 4, blocks the bucket regardless of the other run. (The two slice
controls — `personal-essay-narrative-arg` and the referenced
`modest-proposal-satire` — score on this set; their `groundtruth.md` marks
GT2/GT3/GT5/GT6 as N/A.)

**WARRANTED-but-with-a-soft-spot is not a pure control.** The referenced real
fixtures (`CORPUS.md`) are WARRANTED *and carry a registered Should-Fix soft spot* —
their whole purpose is severity calibration. The three-anchor control rule above
is **insufficient** for them: two runs could both say WARRANTED, miss the registered
failure locus and objection, and falsely "converge." They use the
**calibration-fixture convergence rule** instead: agreement on GT1 (claim),
GT2 failure *locus/layer*, GT3 objection zone, a severity check (soft spot named
at Should-Fix with no over-firing), and GT7 = WARRANTED. See
`evals/fixtures/argument-benchmark/RUN-PROTOCOL.md` §Step 4. Pure controls (no
registered soft spot) keep the three-anchor rule.

### Attribution is reliability-aware (asymmetric)

The **convergence criteria above are unchanged** by the Reliability ledger — the anchor sets and
the ≥3-of-4 / calibration rules are byte-stable. What the ledger changes is **attribution**, and
only in one direction, on the real-corpus fixtures during the M1→M2 window (where GT7 and GT4–GT6
are `provisional, confirm`, not licensed):

- A **`gate` (licensed) anchor's** miss is adjudicated as an **engine failure**, as before.
- A **`confirm` anchor's** disagreement is attributed **by direction**. An **over-fire** (an
  `UNWARRANTED` verdict on a WARRANTED-keyed piece; a registered Should-Fix soft spot escalated to
  Must-Fix; a Must-Fix flood) is booked **ENGINE-FAULT** — the specificity gate does **not** soften,
  because catching over-fire is exactly what the calibration fixtures exist to test. A
  **false-negative** (the run misses the registered soft spot, locus, or objection zone) downgrades
  the fixture outcome from ENGINE-FAIL to **KEY-REVIEW**: record `key-suspect (ground-truth
  ambiguity)`, route the anchor to run-blind re-registration or the blind M2 panel, and book no
  engine regression against it.
- A **`report` anchor** never enters convergence.

So M1 weakens the specificity gate **nowhere** and relaxes false-negative attribution on one-editor
labels **only** — deliberately, per the psychometric frame (a one-editor provisional label lacks the
license to convict the engine of a miss). Run agreement is a **floor, not a license**: two runs
agreeing against a one-editor label is evidence the *label* lacks license (key-suspect), never a
promotion — only the M2 editor panel promotes a status. Full mechanics in
`evals/fixtures/argument-benchmark/RUN-PROTOCOL.md` §Step 4, and the one mechanical guard (the
round-record conformance mode) is in §Mechanical validator → Check 6.

### Reviewer reliability is a separate layer, not a convergence path

Inter-rater agreement — two reviewers independently scoring the *same* engine
output against the same ground truth — answers a different question:
*is the rubric and answer key applied consistently?* It does **not** tell you
whether two independent runs of the engine converge. The two are measured and
reported separately:

- **Convergence (engine):** two independent *runs* → do the diagnoses agree on
  the four anchors? (§ items 1–4 above.)
- **Reliability (scoring):** ≥2 reviewers score a *shared* sample of outputs →
  do the scores agree? Systematic reviewer disagreement is the *ground-truth
  ambiguity* cause class: it means the answer key, not the engine, needs
  sharpening, and convergence results are not trusted until reliability is
  acceptable.

A benchmark that lets "two reviewers agreed on one output" stand in for "two
runs converged" can pass while the engine is non-reproducible — the failure
this separation exists to prevent.

Both layers reuse the blind-review packet format from
`blind-review-protocol.md`. Disagreements (in either layer) are logged with a
failure-attribution cause class (`eval-harness-spec.md §Failure Attribution`) —
engine fault vs. ground-truth ambiguity vs. reviewer error.

---

## Run harness

For each fixture:

1. **Input.** The fixture text only — the contents of `fixture.md` (or the
   referenced source for text-not-stored pieces), which is metadata-free by
   construction. Feed it with a **neutral label**, never the descriptive slug;
   `groundtruth.md` is never fed to the engine. (Comments/metadata in the input
   would leak the answer key — see the fixture README's Input hygiene rule.)
2. **Invocation.** Route through nonfiction intake (Franklin Classification 3
   or 4 → Dialectical Clarity), or invoke the audit directly
   (`/audit dialectical-clarity`). Companion modules run per the fixture's GT
   needs: Red Team for GT5, Revision Coach argument mode for GT6.
3. **Captured artifacts.** Editorial letter + `Argument_State.md` (+
   `Red_Team_Memo.md` and the argument session plan when GT5/GT6 are scored).
4. **Scoring.** A reviewer (blind to which run is which, where possible)
   scores the seven dimensions against `groundtruth.md` using the rubric,
   then records convergence anchors.
5. **Storage.** Run outputs land under the gitignored `evals/results/` path
   unless the fixture's provenance permits in-repo storage (synthetic and
   public-domain outputs may be stored; see fixture README).

---

## Mechanical validator (built)

`validate.sh argument-groundtruth-check <groundtruth_file>` is the mechanical-honesty layer
for this benchmark — the 17th self-testable validator (`scripts/argument_groundtruth.py`, with
a no-`python3` advisory degrade path; wired into `--self-test-all` and run over the registered
corpus by `--check-all`). It checks:

- All eight GT sections (GT1–GT8) are **covered** by a heading and non-empty. Corpus fixtures
  legitimately combine sections under one heading (`## GT4–GT8 — *(PROVISIONAL)*`, `## GT7–GT8
  — …`, `## GT5 / GT6 — …`); the parser expands ranges and lists so each number is accounted for.
- Every code referenced resolves to the Dialectical Clarity namespace
  (`AT / CL / SM / WR / BP / OB / DI / NE / AC`) or a valid `FM-Ax` pattern (x ∈ 1–20). The
  `GT` section-label prefix is excluded.
- GT2 locus ↔ code consistency: when the locus names any of the canonical four loci
  (SUPPORT/WARRANT/BURDEN/OBJECTION), at least one named locus's code family is present
  (`WARRANT → WR*`, `SUPPORT → SM*`, `BURDEN → BP*`, `OBJECTION → OB*/DI*`). This catches the
  spec's example error (a warrant break mis-coded as a support break) while tolerating the
  corpus's richer/compound loci (`WARRANT / OBJECTION`, `SCOPE / CLAIM`, `… / FORM`). Positive
  controls (`N/A — positive control`) are exempt.
- GT7's warrant verdict (field `Expected warrant verdict`) is one of WARRANTED /
  UNCONVENTIONAL-BUT-WARRANTED / UNWARRANTED. A GT7 section present but carrying **no** parseable
  verdict field is an **ERROR** (not a silent skip), and residue of **all three** retired v0.1
  encodings is actively rejected — the standalone field label (`Expected classification`), the
  combined-block sub-line (`GT7 Distinguish:`), and the inline variant (case-insensitive
  `expected classification`) — as are the retired tokens
  (SOUND / UNCONVENTIONAL-BUT-EFFECTIVE / UNSOUND), so an unmigrated encoding cannot pass
  vacuously beside a pasted-in new field. An
  UNCONVENTIONAL-BUT-WARRANTED verdict must name ≥1 form-dependent code to downgrade — specific
  (`SM0`, `FM-A1`) or family-level (`DI codes`, `SM/WR on the cost accounting`) references both
  count.
- GT8's premise-plausibility flags (field `Expected premise flags`) are **leading-token parsed**:
  the value is `NONE_REGISTERED` or a `P<n>` id list, with a trailing
  `(provisional migration default)` treated as parser-ignored commentary. The registered path is
  **strict, not advisory** (a firewall nothing cross-checks is vacuous): `NONE_REGISTERED` can
  never combine with any other flag or id and forbids detail rows; a `P<n>` list requires detail
  rows whose ids match the expected list exactly, both directions. Each detail row (bolded ids
  like `- **P1:**` are matched, not skipped) must have **exactly 5** `|`-cells
  (premise | role | flag-type(s) | why flagged | Firewall boundary — a `|` inside the premise
  text is rejected rather than allowed to shift cells past validation), and each ` + `-joined
  part of the flag cell must be **exactly** one of `CONTESTABLE / UNEARNED / OVERLOADED /
  EXTERNAL-VERIFY / DEFINITIONAL` (full-match; `NONE_REGISTERED` is field-level only; leading
  tokens are boundary-checked so `P1a`/`WARRANTEDx` cannot truncate-parse). The flag-type cell
  must not smuggle a truth verdict — a standalone uppercase `TRUE / FALSE / PROVEN / DISPROVEN /
  CORRECT / INCORRECT` fails the Firewall check by name (case-sensitive; the `Why flagged` /
  `Firewall boundary` prose fields, whose natural sentence is lowercase "true or false", are
  exempt — and the full-match enum backstops any lower/mixed-case adjudication smuggled into the
  flag cell). GT8 is a contract/firewall check in M1, not a scored dimension.
- **Check 6 — the Reliability ledger (GT schema v0.3.0).** Exactly one `- **Reliability:**` line
  in Provenance, assigning every GT anchor a status + decision-use (see §GT schema → The
  Reliability ledger). The group grammar (`GT<a>(–GT<b>)?: <status>, <use>`, `(?![0-9])`
  boundary-guarded so `GT10` cannot truncate-parse, `|`/`/`-in-value rejected as copied guidance),
  exact GT1–GT8 coverage (no gaps/overlaps), and the enforcement matrix (`gate` ⇒ licensed;
  `provisional` ⇒ confirm/report; `low-agreement` ⇒ report) are all machine-checked. The
  formerly-dead heading `(PROVISIONAL)` bool is now **consumed**: a licensed status under a
  PROVISIONAL-marked heading is a stale-marker ERROR (the promotion tripwire). A sibling
  **round-record conformance mode** (`--round-record <record.md> --fixtures-dir <dir>`) is the one
  mechanical guard at the run-side seam — every booked ENGINE-fault must cite an anchor whose
  ledger licenses it (`gate`: any booking; `confirm`: only with an explicit `OVER-FIRE` tag — the
  asymmetric ruling; `report`: none); `--check-all` runs it over
  `docs/argument-benchmark-calibration-round.md`.

**Calibration note.** The six checks were tuned against the full registered corpus (16 GT
files across both the Increment-1 full fixtures and the Increment-2 provisional/derive-on-run
fixtures, all migrated to GT schema v0.3.0) so the validator passes every registered ground
truth and catches malformed/edited ones. The original spec assumed a fixed GT2 locus enum and
fully-populated GT7s; the realized corpus is richer, so the checks validate *consistency and
resolution* rather than strict enum membership. GT8 (v0.3.0) is contract-shaped: the whole
registered corpus takes `NONE_REGISTERED` (10 of 16 as the provisional migration default), so the
registered-flag path is exercised by the parser's moon-cheese self-test rather than the corpus.

---

## Increment plan

### Increment 1 — Vertical slice (this landing)

Prove the spec, rubric, ground-truth schema, and scoring loop end-to-end on a
minimal set before scaling. Delivered:

- This spec + `evals/rubrics/argument-benchmark.md` + ground-truth template.
- Three runnable synthetic fixtures with pre-registered ground truth:
  1. **Op-ed, warrant leap** (bucket 1) — isolates Q2 SUPPORT-vs-WARRANT:
     evidence is sound, the bridge is missing. Primary: FM-A6.
  2. **Policy brief, uncompared proposal** (bucket 2) — isolates Q4/Q5/Q6:
     benefit evidence is fine, the comparative burden and implementation are
     unmet. Primary: FM-A10 + BP5 + FM-A18.
  3. **Personal essay, narrative argumentation** (bucket 4) — the Q7
     positive control: argument is recoverable through juxtaposition; the
     no-thesis "failure" must be downgraded, not fired.
- One public-domain referenced ground truth (text not stored): Swift,
  *A Modest Proposal* — the hardest Q7 trap and the demonstration of the
  reference-by-manifest path.

### Increment 2 — Corpus expansion

Fill buckets 3, 5, 6, 7 and add the remaining public-domain exemplars
(Douglass, *Federalist* No. 10). Add a private/permission-cleared real
fixture per bucket (gitignored manifest) for external validity. Each new
bucket needs ≥1 positive control.

**Status (2026-06-04):** Buckets 1, 2, 5, 6, 7 are covered by the referenced
real corpus (`evals/fixtures/argument-benchmark/CORPUS.md`, 10 pieces). Still
to build for the **shippable, zero-fetch public-domain core**: Douglass
(bucket 3 / testimony) and *Federalist* No. 10 (bucket 5 positive control) —
these are the in-repo substitute for the copyrighted contemporary pieces,
which travel only as a fetch-list (URL + anchor + SHA-256), not as text.

### Increment 3 — Mechanical validator + convergence runs

`argument-groundtruth-check` is **built** (see §Mechanical validator above): wired into
`--self-test-all` (17th validator) and run over the registered corpus by `--check-all`; host
workspaces regenerated. **Remaining:** run the two-independent-runs convergence protocol across
the full corpus and record results in the review log.

**Status (2026-06-04):** Convergence runs **done** — Opus + Sonnet across the
full corpus, plus a cross-vendor GPT-4 pass; recorded in
`evals/results/*/SCORECARD.md`. The runs surfaced and fixed a Step-6
decoy-resistance gap (6a two-test procedure + FM-A20). The
`argument-groundtruth-check` validator (17/17 self-test, both host workspaces)
and the `run.sh --fetch` reconstitution mode are now **built** (2026-06-04);
`federalist-10` and `douglass-fourth-of-july` added as fetchable public-domain
controls (bucket 5 + bucket 3 / Q7). Remaining: second-editor confirmation of
GT4–GT8.

---

## Open questions

- **Ground-truth authority.** The slice's synthetic ground truth is
  author-registered (deterministic by construction). For public-domain and
  real fixtures where the diagnosis is interpretive, the authority should be a
  named editor's pre-registration, ideally adjudicated by a second editor.
  Multi-model consensus is a *candidate* generator for ground truth but must
  not be the authority that the engine is then scored against (circularity).
- **Companion-module scoring depth.** Q5 (red-team) and Q6 (coaching) require
  running companion modules, which is more expensive than the core audit.
  Increment 1 scores Q5/Q6 on the policy-brief fixture only; whether every
  bucket needs full companion runs is a cost decision for Increment 2.
- **Hybrid-bucket dual-audit interaction.** Bucket 7 fixtures trigger both
  Dialectical Clarity and Narrative Nonfiction Craft. The benchmark must
  score the *handoff* (NE function classification + which audit owns which
  finding), not just the argument layer. Schema may need an NE-handoff field.

---

*This benchmark is infrastructure for trusting the engine, not a deliverable
for writers. It tells us whether the Nonfiction Argument Engine recovers
diagnoses a competent editor already knows — and, just as importantly,
whether it knows when to leave a warranted but unconventional argument alone.*
