# Rhetorical Purpose — Lean Build Spec

**Status:** Proposed (unbuilt). Ready to build as one increment. Documentation only until then.
**Date:** 2026-10-04 (replaces the 2026-10-01 roadmap version of this file; see git history).
**Research basis:** [`rhetorical-purpose-level-setting.md`](rhetorical-purpose-level-setting.md)
(two sources, synthesized). **Decision record:** [ADR 0003](adr/0003-rhetorical-purpose-state-boundary.md).
<!-- built-when: plugins/apodictic/skills/argument-audits/references/craft/dialectical-clarity.md contains "AT6" -->

## Problem

The argument engine asks claim questions (where is the warrant, where is the strongest
objection, is this case representative) of passages that are greeting, bearing witness,
narrating, or commemorating. It then tells those writers only what they failed to prove. The
engine already calibrates burden by type and span (AT1 makes objections optional; AT4 splits
testimony; AT5 judges a lens on coherence and fertility, with asserted burden at each cash-out),
so most of the fix is more of the same. One thing cannot be expressed today: a text whose point
is an address ("we stand with one another") rather than a proposition. `Argument_State`
requires a propositional C0 and a document-level warrant verdict, so the engine invents a thesis
and then faults it.

**Design rule:** a passage's communicative work decides which questions apply; its actual
commitments decide what it stays answerable for.

## Scope

In: AT6, the AT4 extension, a typed C0, an applicability rule, a short list of span rules, the
register-spec amendment that permits them, and an acceptance battery. Out: persisted
purpose/operation/commitment records, per-tradition profiles, capability negotiation between
modules, new validators beyond the parser updates below, and any change to fiction routing.
Those were proposed in the 2026-10-01 version and rejected by both research sources; reopen
them only if a test text defeats this design.

## Changes

### 1. AT table (`dialectical-clarity.md` Step 1)

Add one row and extend AT4:

| Code | Type | Promise to reader | Burden |
|---|---|---|---|
| AT4 | Testimonial | "I witnessed this; recognize or consider it" | Split, as now: **observational** (low; a speaker's act or presence can discharge it for claims about capacity or standing), **interpretive** and **representative** (only where the text undertakes them; a named mandate can ground representation). New **attribution** sub-burden for recorded, translated, reconstructed, or composite speech: who spoke, who recorded, when, through what language chain. |
| **AT6** | Constitutive / relational address | "Here is who we are and what that asks of us" or "Recognize this" | Split: **address coherence** (the collective is identifiable; its scope is stable or visibly widened; the implied reader is one the stated audience can occupy; exclusions are owned); **closure** (the text hands the reader a role or act, or marks recognition as its end); **cash-out** (every factual, causal, quantified, historical, attributive, or prescriptive sentence at asserted burden, wherever it sits). Writer-confirmed, never inferred, same as AT5. Covers solidarity addresses, commemoration and other epideictic, and pledges, dedications, and acknowledgments. |

Add AT6 failure codes alongside GN0–GN2, at most three: unexplained "we" drift where a claim
depends on the narrower scope; an implied reader the stated audience cannot occupy; closure that
contradicts the address. Default Should-Fix.

Change the Open Letter / Manifesto genre note from "AT3" to "AT3 or AT6; confirm at intake."
State in the AT6 row that the grouping is functional and implies no endorsement.

### 2. Typed C0 (`dialectical-clarity.md` Step 2; `docs/argument-state-schema.md`)

C0 stays mandatory and gains one field: `C0 type: ASSERTION | ADDRESS` (default `ASSERTION`).

- An `ADDRESS` C0 reads "the text asks [named audience] to be / recognize / do [X]." It is
  available only under writer-confirmed AT6, or AT4 whose stated purpose is to be heard.
- CL0 still fires when neither form can be stated. That keeps the line between a deliberate
  address and a text that never commits to anything.
- Subclaims are optional under an `ADDRESS` C0. Local claim chains attach to cash-outs.

Warrant verdict gains one permitted value, `ADDRESS-C0 (verdicts at cash-outs)`, used only with
an `ADDRESS` C0. Each cash-out gets its own WARRANTED / UNCONVENTIONAL-BUT-WARRANTED /
UNWARRANTED verdict. Bump the schema to 0.4.0. Existing artifacts stay valid unchanged
(`ASSERTION` is the default).

**Severity for an ADDRESS C0** (Hard Gates § Severity definitions): Must-Fix requires CL0 or a
defeated cash-out. An AT6 coherence failure is Should-Fix by default. Never borrow a fictional
propositional C0 to escalate.

**Downstream modules** that read the claim ladder (red team, persuasion, coaching, pre-draft,
AIF export, reconstruction): when C0 type is `ADDRESS`, operate on the cash-out claims only, or
say plainly that the module does not apply. Never invent a ladder, an antithesis, an inference
edge, or a global WARRANTED. This is a one-paragraph guard per module reference, not an adapter
layer.

### 3. Applicability rule (`dialectical-clarity.md`, Findings; register spec AD2)

Before applying a claim, warrant, evidence, scope, objection, or comparison check to a span,
name the commitment that makes it relevant. **An inapplicable check produces no finding**, not
a demoted Could-Fix. Commitments are inventoried throughout the text, not just at the end.

Span functions a writer can confirm: ADDRESS, OBSERVATION, NARRATIVE, ILLUSTRATION,
SHARED-PREMISE, IRONIC, PARTICIPATORY. Inside one, these checks do not apply: objection handling
and rhetorical fairness (OB), WR0 on the span's internal moves, redundancy, and hasty
generalization (ILLUSTRATION only). Every check switches back on at the span's cash-out.

**Amend register-spec AD2** ("every audit runs, every finding is retained") to: every audit
runs and records an applicability decision for each span it examines; inapplicable questions
produce no finding; applicable findings go through Triage and the Deficit Lock unchanged. A run
that returns "nothing applies" across the whole text is still a build failure. AD4 is unchanged:
an intake-declared high-stakes gate makes every claim a cash-out, but it does not turn an
address span with no claim in it into an assertion.

### 4. Span rules (`dialectical-clarity.md`, the relevant steps)

1. **Never exempt.** Factual, causal, quantified, historical, attributive, and prescriptive
   claims, and dated or quantified predictions, keep their burden under every type, span
   function, and stance verdict. Extend stance triage's existing block on earning prescriptions
   to all of these.
2. **Shared premises.** An unstated warrant that is evaluative, definitional, or traditional
   (a value ranking, a covenant, a proverb), recoverable, and attributable to the declared
   audience produces no finding unless the text contests it. Empirical premises framed as
   shared keep DI0 and AC1 as now.
3. **Example vs. illustration.** A case that follows an independently supported or shared rule
   is an illustration and gets aptness checks only. A case that precedes or solely supports a
   rule is an example and gets representativeness checks (NE1, BP6). A single case may defeat a
   universal claim.
4. **Seams.** AT0 does not fire on a signaled mode switch. It fires when the switch is
   unsignaled and a claim after it borrows the lower burden of the span before it.
5. **Disclosure.** An undisclosed composite or pseudonymous case presented as one real person
   is Must-Fix under any label. A disclosed composite is a representative claim under AT4.
6. **Dissent.** Faithful representation of an opponent, rebuttal, comparison of alternatives,
   and refusal of a frame are separate obligations. Absence of rebuttal is not
   misrepresentation. Under a confirmed agonistic purpose, the steelman question becomes "would
   the adversary recognize their position?"; denial of standing and dehumanization remain
   findings under every label.

### 5. Intake (`intake-router-runtime.md`, nonfiction intake)

Propose AT6 or a span function from textual signals; the writer confirms in plain words ("Is
this piece mainly asking readers to stand with a group, or to accept a claim?"), never by theory
name. Unconfirmed proposals leave the default route in place. Never infer a writer's culture
from text features. Add one intake question: does any quoted speech come through a recorder,
translator, or composite?

### 6. Documentation

Dialectical Clarity's scope statement says what the engine now does: it applies claim-support
standards where a text undertakes claim-support work, supports a bounded set of other
undertakings (AT4, AT5, AT6), and states the basis and limits of its diagnoses. Name the
deliberate commitment that factual and prescriptive claims carry burden in every genre.

## File map

- `plugins/apodictic/skills/argument-audits/references/craft/dialectical-clarity.md`: §1–4, §6.
- `docs/argument-state-schema.md`: C0 type, warrant-verdict value, version 0.4.0.
- `docs/argument-register-stance-triage-spec.md`: AD2 amendment; note on AD4.
- `plugins/apodictic/skills/argument-audits/references/craft/rhetorical-stance-triage.md`:
  never-exempt extension.
- Downstream module references: one guard paragraph each (red team, persuasion,
  revision coach argument path, nonfiction pre-draft, AIF export, reconstruction).
- `plugins/apodictic/skills/core-editor/references/intake-router-runtime.md`: §5.
- Parsers that enumerate warrant verdicts (`grep UNCONVENTIONAL-BUT-WARRANTED
  plugins/apodictic/scripts`): accept the new value where they read live `Argument_State`.
  The argument benchmark's GT7 classes are unaffected; no benchmark fixture is AT6.
- `changelog.d/` fragment; ROADMAP section status.

## Acceptance

Promote the existing candidate decks rather than writing new ones:
`evals/candidates/rhetorical-purpose-first-increment/` and
`evals/candidates/rhetorical-purpose-constitutive-controls/`. Update their `expected.md` where
they assume the rejected branch design (R13–R16 in particular: legacy compatibility now means
"`ASSERTION` default, artifact unchanged"; consumer refusal means the one-paragraph guard).
Add the level-setting doc's matched pair:

- **S0**, a short solidarity greeting: `ADDRESS` C0, coherence checks, no thesis, objection,
  representativeness, or comparison finding.
- **S1**, S0 plus "This gathering will reduce neighborhood evictions by 40% within one year.":
  the same reading of S0 plus exactly one finding at the inserted sentence (causal, quantified,
  time horizon). The same sentence draws the same finding in an ordinary asserted text.

Release-blocking outcomes: an invented thesis or antithesis; a demand to rebut denial for
balance; a commitment defect excused by type or span function; AT6 or a span function applied
without confirmation; a global WARRANTED for an address. Do not score by flag counts. The
existing two-reader blind protocol applies before any of this becomes benchmark ground truth.

Gate: `bash scripts/validate.sh --check-all` green. Keep tests to behavior the battery protects
(`AGENTS.md` § Test value convention).
