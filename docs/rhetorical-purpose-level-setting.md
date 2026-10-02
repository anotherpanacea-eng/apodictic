# Rhetorical Purpose & Plural Standards — level-setting research

**Status:** Level-setting research. **Prompt issued; no sources in yet.** Answers whether the
argument engine's claim-and-support model misreads rhetoric whose success is something other
than a warranted conclusion, and what the *smallest* change to Dialectical Clarity would fix
it. Feeds a go/no-go on the proposed spec in PR #288
(`docs/rhetorical-purpose-pluralism-spec.md`) versus a lean edit to the existing argument-type
(AT) table. **Firewall unchanged:** diagnose, never write content; empirical truth adjudication
stays out of the engine.

## Why this research

A communication scholar criticized APODICTIC for treating evaluable claim-and-support as the
standard for all persuasive writing. PR #288 answers with a parallel purpose layer (new state
version, six record types, seven profiles, four phases). The engine already calibrates burden by
argument type and by span (AT1 makes objections optional; AT4 splits testimony; AT5 assesses a
lens on coherence and fertility, with asserted burden only at cash-outs). The open question is
whether the critique exposes failures the AT mechanism cannot express, or failures it can
express with a few new rows and one applicability rule.

## Method

Cross-model deep-research elicitation: one prompt (below) run through several models,
synthesized by **triangulation, not averaging**. Agreement → high confidence; single source →
flag; divergence → surface. Divergences about what a tradition counts as success are recorded,
not resolved. Citations are tiered by corroboration; unverifiable ones are dropped. The
synthesis must end in a classification of each tradition as *already covered*, *new AT row or
burden split*, *applicability rule*, or *needs more than that*, with the last category carrying
the burden of proof.

## Sources

| # | Model | File | Shape |
|---|---|---|---|
| 1 | *(pending)* | | |

## Synthesis

*Pending.*

## The elicitation prompt (as issued)

The critique below is a ChatGPT reading of the public README and a published sample, relayed
by the scholar on 2026-10-02 and pasted by the maintainer.

````text
# Deep-research request: does a claim-and-support editing engine misread non-deliberative rhetoric, and what is the smallest fix?

## Role & context
You are advising on the argument engine of a developmental-editing tool for persuasive
nonfiction (op-eds, policy briefs, testimony, open letters, academic arguments, advocacy,
manifestos, lens essays). The tool diagnoses structure and never writes prose. A communication
scholar has criticized it for assuming that every persuasive text should be judged as
evaluable claim-and-support. Your job is to test that criticism against the tool's actual
design and the rhetorical literature, then recommend the **leanest** change that fixes real
misdiagnoses. Extra architecture is a cost, not a deliverable.

## The critique
The scholar relayed this ChatGPT reading of the tool's public README and one published sample:

> My read is: yes, this is substantially a liberal-rationalist model of argument, though a
> considerably more sophisticated and self-aware one than I expected. It is not merely "logic
> checking," and it does make some moves toward rhetorical situatedness. But those moves happen
> inside a fairly determinate normative picture of what argument ought to be.
>
> The clearest evidence is its own definition of Dialectical Clarity. APODICTIC says the audit
> maps a "claim ladder," identifies "missing warrants," checks "rhetorical fairness" by asking
> whether the text engages the strongest version of the opposition, and flags scope drift. It
> defines burden as what a writer has committed themselves to proving and treats stronger
> claims as generating higher burdens. That is already much closer to Toulmin-plus-steelmanning
> than to anything recognizably agonistic, constitutive, Burkean, Foucauldian, or even
> Perelmanian.
>
> And the actual sample makes the normative machinery considerably more explicit.

Note that the reading is based on public-facing documentation and a sample, not the engine's
full rules. Part of your task is to say which of its claims are about the engine and which are
about how the engine presents itself.

## How the engine works now (summary)
The engine reconstructs a claim ladder (core claim C0, subclaims, warrants, evidence, scope,
objections) and assigns each finding a severity: Must-Fix, Should-Fix, or Could-Fix. Before
that, it classifies the piece's argument type, which sets the burden:

| Code | Type | Promise to reader | Burden |
|---|---|---|---|
| AT1 | Explanatory | "Here's how this works" | Low; clear and accurate; objection handling optional |
| AT2 | Evaluative | "Here's whether this is good/bad" | Medium; show criteria and apply them |
| AT3 | Propositional | "Here's what we should do" | High; problem, solution, tradeoffs, why alternatives fail |
| AT4 | Testimonial | "I witnessed this; here's what it means" | Split: observational (low), interpretive (high), representative (whether a personal account stands for a population) |
| AT5 | Generative / lens | "Look through this lens" | Split: coherence and fertility across the piece; asserted burden only at each "cash-out" where the lens becomes an assertion or prescription |

Other relevant rules: AT5 must be confirmed by the writer, never inferred. A high-stakes setting
(testimony to a legislature, legal brief, regulatory comment) forces full asserted burden on the
whole document. A separate stance triage can mark overstatement as earned (provocation,
strategic misreading) before severity is locked, but never for prescriptions. Existing
grounding includes Perelman & Olbrechts-Tyteca (audience), Bitzer (rhetorical situation), and
Fricker (testimonial injustice). A proposed alternative would add a full "purpose layer" with
profiles for deliberative, agonistic, constitutive, Burkean identification, genealogical,
witness, and exploratory rhetoric.

## Research questions
1. **What exactly does the critique claim?** Separate (a) an epistemic claim (claim-and-support
   is one genre among several), (b) a political claim (deliberative norms privilege some
   speakers or styles), and (c) a practical claim (the tool gives bad editorial advice on some
   texts). Which of these can a software change address, and which are disagreements to
   acknowledge rather than fix? The critique names Perelman as a tradition the tool is far
   from, although the engine cites Perelman for audience-relative reasonableness: is that a
   real gap (e.g. no treatment of presumption, values, or loci) or a documentation gap?
2. **Where would the current engine misfire?** For each tradition below, name the concrete
   misdiagnosis the AT table would produce, and classify it: wrong question applied, right
   question at wrong severity, or a positive success criterion the engine cannot see at all.
3. **What does each tradition count as success and failure?** Cover at least: constitutive
   rhetoric (Charland; Black's "second persona"; McGee on "the people"); agonism (Mouffe);
   Burkean identification and division; invitational rhetoric (Foss & Griffin); witness and
   testimony (Fricker; Dotson on testimonial smothering; trauma-testimony literature);
   genealogy and critique (Foucault); Iris Marion Young's critique of deliberative democracy
   (greeting, rhetoric, narrative); the American jeremiad; and the adversary-method critique of
   argument-as-combat (Moulton). Add any tradition a rhetoric scholar would consider a glaring
   omission, including non-Western or Indigenous oratorical forms, and say where your knowledge
   is thin.
4. **What can an editor detect in the text?** For each tradition, list failures that are
   visible on the page (not dependent on audience-reception data), with a false-positive guard
   for each.
5. **What is the minimum change?** Classify each tradition as: (A) already handled by AT1–AT5;
   (B) needs a new AT row or burden split; (C) needs a rule that a diagnostic question does not
   apply to a span and therefore produces no finding; (D) needs architecture beyond A–C. Any
   (D) must show a specific text the A–C version would still misdiagnose.
6. **What must never be exempted?** Factual, causal, quantified, and prescriptive claims keep
   their burdens inside any purpose. How should the engine avoid becoming a tool that excuses
   propaganda, bad faith, or fabricated testimony under a purpose label?
7. **Would the critic be satisfied?** Where would the lean version still fall short of the
   critique, and is each remaining gap a reason to change the tool or a disagreement to record
   in its documentation?

## Test texts
Use public-domain texts and state the expected behavior of a correct engine on each:
Frederick Douglass, "What to the Slave Is the Fourth of July?" (1852); Sojourner Truth's 1851
Akron speech (note the competing transcriptions); the Gettysburg Address (1863); the Seneca
Falls Declaration of Sentiments (1848); Chief Joseph's 1877 surrender speech (note provenance
doubts). Add one constructed pair: a solidarity address that makes no policy claim, and the same
address with one unsupported quantified prediction inserted.

## Hard constraints
- **Cite only real, verifiable sources** (author, title, year; page or chapter where you can).
  Do not invent works or quotations. If unsure a source says what you attribute to it, say so.
- **Do not grade the critique by agreement with the tool**, and do not assume the critic is
  right. Steelman both.
- **Prefer the smallest change.** Recommendations that add schemas, state versions, or new
  subsystems need a concrete misdiagnosis that nothing smaller fixes.
- **Stay in the diagnostic lane.** No generated prose, no political verdicts on texts, no
  predictions of actual audience uptake.
- Keep the **per-tradition structure identical** (fields below, same order) for merging.

## Output format
Per tradition, five fields: (1) success criteria; (2) characteristic page-visible failures;
(3) current-engine misfire and its class; (4) false-positive guards; (5) A/B/C/D
classification with one-line justification. Then: **"Answer to the critique"** (Q1, Q7);
**"Minimum viable change"** (the concrete edits to the AT table and finding rules, as short as
possible); **"Test-text expectations"**; **"Sources"** (deduplicated); **"Confidence & gaps."**
````
