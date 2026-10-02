# Alternative Argument Approaches — level-setting research

**Status:** Level-setting research. **1 source in; synthesis waits on at least one more.** Asks how the argument
engine can recognize, diagnose, and coach effective approaches to argument other than the
claim-and-support model, and what the *smallest* change to Dialectical Clarity would support
them. Feeds a decision between the proposed spec in PR #288
(`docs/rhetorical-purpose-pluralism-spec.md`) and a lean edit to the existing argument-type (AT)
table. **Firewall unchanged:** diagnose, never write content; empirical truth adjudication stays
out of the engine.

## Why this research

The engine is good at claim ladders, warrants, evidence, and objections, and it already
calibrates burden by argument type and span (AT1 makes objections optional; AT4 splits
testimony; AT5 judges a lens on coherence and fertility, with asserted burden only at
cash-outs). It has little to say about why a constitutive address, a narrative, an act of
witness, or a jeremiad *works*, so it can only tell those writers what they failed to prove. A
communication scholar's critique (quoted in the prompt) sharpened the point. The research goal
is constructive: identify approaches that demonstrably work, what doing them well looks like on
the page, and how an editor helps a writer do them better.

## Method

Cross-model deep-research elicitation: one prompt (below) run through several models,
synthesized by **triangulation, not averaging**. Agreement → high confidence; single source →
flag; divergence → surface. Citations are tiered by corroboration; unverifiable ones are dropped.
The synthesis ends in a short list of approaches worth supporting, each classified as *already
covered*, *new AT row or burden split*, *applicability rule*, or *needs more than that*, with the
last category carrying the burden of proof.

## Sources

| # | Model | File | Shape |
|---|---|---|---|
| 1 | Not recorded | `rhetorical-purpose-sources/source-1.md` | 18 approaches; lean + one narrow no-C0 schema change; proposes AT6 Relational/constitutive and an AT4 recognition extension; schema claim verified |

## Synthesis

*Pending a second source.* Source 1's headline to test: everything fits AT6, an AT4
extension, and an applicability rule, except that `Argument_State` must allow a text with no
global C0 or global warrant verdict.

## The elicitation prompt (as issued)

````text
# Deep-research request: how should a developmental-editing tool support effective approaches to argument beyond claim-and-support?

## Role & context
You are advising on the argument engine of a developmental-editing tool for persuasive
nonfiction (op-eds, policy briefs, testimony, open letters, speeches, academic arguments,
advocacy, manifestos, lens essays). The tool diagnoses structure and coaches revision; it never
writes prose. It handles claim-and-support argument well. I want to expand it so it can
recognize and strengthen other approaches to argument that are effective in their own terms,
and stop treating them only as failed claim-and-support. Recommend the **leanest** change that
does this well. Extra architecture is a cost, not a deliverable.

## Background: the critique that prompted this
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
full rules. It is background, not the main question; address it briefly at the end.

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
1. **Which alternative approaches are effective, and what is the evidence?** Survey approaches
   to argument and persuasion that succeed without (or alongside) an explicit claim ladder.
   Cover at least: constitutive rhetoric (Charland; Black's "second persona"; McGee on "the
   people"); Burkean identification; narrative argument (Fisher's narrative paradigm; narrative
   transportation research such as Green & Brock); witness and testimony (Fricker; Dotson);
   invitational rhetoric (Foss & Griffin); agonism (Mouffe); Iris Marion Young's greeting,
   rhetoric, and narrative; the American jeremiad; Perelman & Olbrechts-Tyteca's techniques
   beyond audience (presence, values and hierarchies, loci, dissociation); enthymeme and shared
   premises; exemplum and analogy; satire and irony; genealogy (Foucault); call-and-response
   and other communal forms; and non-Western or Indigenous oratorical forms. Add omissions a
   rhetoric scholar would consider glaring, and drop any approach with no credible case for
   effectiveness. Say what "effective" means for each (changed belief, mobilization,
   recognition, formed identity, reframed debate) and what evidence supports it (empirical
   persuasion research, rhetorical criticism, historical cases), marking where evidence is thin.
2. **What does doing it well look like on the page?** For each approach, the moves a writer
   makes and the textual signals an editor can check without audience-reception data.
3. **What does doing it badly look like, and how does an editor help?** Characteristic
   failures, each with a false-positive guard, and the kind of revision advice a skilled editor
   would give to strengthen the approach without writing the content.
4. **How do these approaches combine with claim-and-support?** Most strong texts mix modes.
   How do successful texts move between them, and what goes wrong at the seams?
5. **How should the tool recognize which approach a writer is using?** Signals that suggest an
   approach (so the tool can propose it and the writer can confirm), and the risk of
   mislabeling.
6. **What is the minimum change?** Classify each approach as: (A) already handled by AT1–AT5;
   (B) needs a new AT row or burden split; (C) needs a rule that a diagnostic question does not
   apply to a span and therefore produces no finding; (D) needs architecture beyond A–C. Any
   (D) must show a specific text the A–C version would still handle badly. Then rank the
   approaches by value to working writers of op-eds, testimony, speeches, and advocacy.
7. **What must never be exempted?** Factual, causal, quantified, and prescriptive claims keep
   their burdens inside any approach. How does the tool avoid excusing propaganda, bad faith,
   or fabricated testimony under an approach label?
8. **The critique, briefly.** Which of its points does your recommendation answer, and which
   remain as honest disagreements to state in the tool's documentation?

## Test texts
Use public-domain texts. For each, name the approaches it uses and what a strong editorial note
would and would not say about it:
Frederick Douglass, "What to the Slave Is the Fourth of July?" (1852); Sojourner Truth's 1851
Akron speech (note the competing transcriptions); the Gettysburg Address (1863); the Seneca
Falls Declaration of Sentiments (1848); Chief Joseph's 1877 surrender speech (note provenance
doubts). Add one constructed pair: a solidarity address that makes no policy claim, and the same
address with one unsupported quantified prediction inserted.

## Hard constraints
- **Cite only real, verifiable sources** (author, title, year; page or chapter where you can).
  Do not invent works or quotations. If unsure a source says what you attribute to it, say so.
- **Steelman both sides.** Do not assume the claim-and-support model or the critique is right.
- **Prefer the smallest change.** Recommendations that add schemas, state versions, or new
  subsystems need a concrete misdiagnosis that nothing smaller fixes.
- **Stay in the diagnostic lane.** No generated prose, no political verdicts on texts, no
  predictions of actual audience uptake.
- Keep the **per-approach structure identical** (fields below, same order) for merging.

## Output format
Per approach, seven fields: (1) what it does, what "effective" means, and the evidence;
(2) page-visible moves and signals; (3) success criteria; (4) characteristic failures with
false-positive guards; (5) the class of editorial advice that strengthens it; (6) how the
current engine would misread it; (7) A/B/C/D classification with one-line justification. Then:
**"Combining modes"** (Q4); **"Recognition"** (Q5); **"Minimum viable change"** (the concrete
edits to the AT table and finding rules, as short as possible, plus the value ranking);
**"Guardrails"** (Q7); **"The critique"** (Q8); **"Test-text expectations"**; **"Sources"**
(deduplicated); **"Confidence & gaps."**
````
