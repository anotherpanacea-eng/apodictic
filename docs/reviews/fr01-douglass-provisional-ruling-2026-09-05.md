# FR-01: Douglass's provisional audience and repair anchors

**Status:** completed advisory ruling; proposed calibration wording only.
**Basis:** APODICTIC `20b8ca6219e649b2743866b9ffaba0e77ab208a5` and the exact
public-domain source body pinned for `douglass-fourth-of-july`.

**Ruling:** retain the constitutional subargument as the default red-team
pressure point, but revise GT6's unconditional repair target. The key offers
"explicitly flag as deferred" as a repair even though the speech already does
so repeatedly. Acknowledging a limitation is not demonstrating the contested
claim; neither does a demonstrated limitation automatically require expanding
an oration into a constitutional argument. GT4 also needs an explicit
distinction between an audience's sympathy with abolition and its agreement
with every subsidiary claim.

This is a **source-and-key-informed judgment**, not a blind discovery or an
engine run. The author read the public key before interpreting the source.
The work reviewed here is recognizable; no unseen-text, recall-resistance,
model-comparison, or accuracy claim follows. GT4–GT6 remain
`provisional, report`. This document changes no key, Reliability ledger,
production prompt, or score. Independent review of this ruling cannot replace
the benchmark's required human-panel licensing.

## 1. Scope, source, and evidence convention

The target is [GT4–GT6 in the existing key](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/evals/fixtures/argument-benchmark/douglass-fourth-of-july/groundtruth.md#gt4--audience-calibration-q4-1-audience--ac-codes--provisional--advisory).
GT2/GT3 and GT7 constrain this interpretation; their registered status and
scoring latitude are unchanged. GT8 expressly excludes deciding whether the
Constitution actually warrants the anti-slavery reading. This ruling observes
that boundary throughout: it describes what the address asserts and supports,
not whether its constitutional conclusion is legally or historically correct.

An independent preparer read only source metadata and verified the existing
cache byte for byte against [SOURCES.md](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/evals/fixtures/argument-benchmark/SOURCES.md).
No new extraction, normalization, or source substitution was used.

| Source binding | Value |
|---|---|
| Work | Frederick Douglass, *Oration, Delivered in Corinthian Hall, Rochester, July 5th, 1852* |
| Referenced OCR | [Archive.org pinned file](https://archive.org/download/Douglass_July_Oration/ocm30553533_V_0_djvu.txt) |
| Analyzed body SHA-256 | `56191e5ee2eff46d38d5e3a18f8c8cf46dd8d48098468b2c39368bfc37185308` |
| Analyzed body length | 62,326 bytes |
| Provenance | Metadata records retrieval on 2026-06-04; exact cache reverified on 2026-09-05 |
| Scope | The address proper, through the closing Garrison poem; no prefatory meeting proceedings |

The full source stays outside Git under the existing source-cache convention.
All `E` locations below are **one-based lines of the verified UTF-8 body**, using
`splitlines()` without dropping blank lines or OCR page numbers. There are
1,559 lines. Quotations collapse whitespace only; OCR spelling is not silently
corrected. Locations bind to these bytes, not a different modern transcription.
The manifest's salutation description is shorthand: the verified body includes
the preceding "Mr. President" on its first line. Starting at the literal
"Friends" inside that line would change the hash and is not this packet.

| ID | Body lines | Exact fragment, whitespace collapsed | Evidentiary use |
|---|---|---|---|
| E01 | `20-27` | "their familiar faces" | Some listeners are familiar to the speaker; not a census of agreement |
| E02 | `387-399` | "You could instruct me in regard to them." | Claimed shared knowledge of independence history |
| E03 | `253-259` | "Stand by those principles, be true to them" | Affirmed standard for judging present conduct |
| E04 | `552-576` | "from the slave’s point of view." | The declared standpoint of the indictment |
| E05 | `596-609` | "Would you argue more, and denounce less" | A staged objection about rhetorical method |
| E06 | `626-638` | "is a moral, intellectual and responsible being." | The inference drawn from slaveholders' own practices |
| E07 | `659-680` | "You have already declared it." | Liberty is invoked as an acknowledged standard |
| E08 | `709-721` | "The feeling of the nation must be quickened" | The declared purpose of the rhetoric |
| E09 | `1128-1148` | "the whole system of crime and blood would be scattered to the winds" | A separate institutional-capacity assertion, not this ruling's priority target |
| E10 | `1182-1203` | "There are exceptions, and I thank God that there are." | The indictment expressly distinguishes allies from the general institutional target |
| E11 | `1334-1355` | "your fathers stooped, basely stooped." | Consequence of provisionally granting the constitutional defense |
| E12 | `1354-1371` | "There is not time now to argue" | Explicit disclosure that the extended constitutional case is deferred |
| E13 | `1373-1403` | "While I do not intend to argue this question on the present occasion" | Repeated deferral alongside a compressed affirmative case |
| E14 | `1392-1427` | "every American citizen has a right to form an opinion" | Claimed lay access to constitutional interpretation |
| E15 | `1429-1438` | "I have detained my audience entirely too long" | The closing limit on the constitutional discussion, followed by an offer of a future full discussion |
| E16 | `1440-1455` | "I do not despair of this country." | Hope follows the indictment; denunciation is not simple national repudiation |

The author read the complete pinned body, not just these excerpts. The table
exposes the decisive evidence for checking this ruling; it is not a substitute
for the complete source in a new assessment.

## 2. Reconstruct the dependency before assigning a repair

The address supplies several connected claims. Collapsing them into a single
constitutional syllogism changes what counts as a decisive objection.

1. **The normative standard:** the nation's professed principles deserve
   allegiance (E03), and the audience has already declared the entitlement
   to liberty (E07).
2. **The inconsistency:** the enslaved do not share the celebrated liberty;
   their standpoint exposes what national celebration omits (E04 and body
   lines 480–533). The subsequent testimony and institutional indictment
   make that disparity concrete.
3. **The constitutional addition:** the Constitution, on the reading Douglass
   advocates, supplies a further resource against slavery. Its short case
   invokes purposes, wording, interpretive rules, named authorities, and
   citizens' interpretive standing (E12–E15). It is not support-free, and its
   complete defense is expressly reserved.

**The decisive counterfactual is in the text itself.** At E11 the speech first
states the reply that slaveholding and slave-hunting are constitutionally
sanctioned. Its immediate conditional response is that the founders would
then have betrayed their professed promise. Douglass subsequently rejects
that constitutional interpretation. Thus, provisionally granting the reply
would alter the judgment of the founders and remove his affirmative
constitutional resource; it would not reconcile slavery with the previously
invoked moral standard.

This is an inference about the argument's dependency, not a resolution of
constitutional meaning. It also does not make the constitutional branch
dispensable in every rhetorical respect: that branch matters to the speech's
affirmative account of national institutions and to the audience's available
responses. **Nonessential to the core indictment is not the same as
unimportant.** The existing GT2 already says the primary argument stands
without this subargument. The proposed GT5/GT6 wording should preserve that
distinction consistently.

The [audit's Step 9 and Severity Floor](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/plugins/apodictic/skills/specialized-audits/references/craft/dialectical-clarity.md)
require an identified defeat of C0 before Must-Fix/UNWARRANTED. A disputed
subsidiary warrant is insufficient by itself. The existing GT7 allowance for
either WARRANTED or UNCONVENTIONAL-BUT-WARRANTED, with no form-dependent
structural failure left firing, remains appropriate to this limited ruling.

## 3. GT4: preserve the audience distinction, qualify what it proves

**Retain:** the split between immediate listeners and the nation/institutions
addressed through them. The pronoun shift and declared standpoint perform
argumentative work. E08 identifies the purpose as awakening feeling and
conscience; E05 is not a confession that the speech contains no reasoning.
The answer proceeds through the recognition of responsibility in slaveholders'
own practices (E06) and the audience's declared standard (E07). Replacing that
sequence with a generic demand for "more argument, less rebuke" would erase
the method being examined.

**Refine:** receptivity is relative to a proposition. Agreement that slavery
is wrong does not establish agreement with the anti-slavery constitutional
interpretation or with the speech's claim about the church's capacity to end
slavery. Conversely, disagreement about constitutional interpretation does
not establish hostility to abolition. E10 expressly identifies institutional
exceptions and allies, including someone on the platform. E01/E02 show
familiarity and presumed civic knowledge, not universal assent in the room.

The current key's description of an abolitionist host and broader readership
is historical/contextual metadata. It is not independently established by a
roster inside the analyzed body. This ruling uses it as declared benchmark
context, while limiting its new evidentiary claims to what the address itself
supports. The imagined objection at E05 is likewise **staged by the speaker**;
it is not evidence that an attendee actually uttered those words.

**Proposed calibration wording:**

> Distinguish immediate listeners, the national/institutional addressee, and
> the enslaved standpoint the speaker represents. Preserve the pronoun split
> and earned rebuke. Treat receptivity as MIXED across the speech's claims:
> sympathy with abolition does not settle constitutional interpretation.
> Identify which claim and audience make a warrant contested; do not invent
> a uniformly hostile or uniformly assenting audience to force a diagnosis.

Confidence is high in the textual distinctions; it is lower in any claim
about the unrecorded attitudes of particular historical listeners. This
proposal specifies no new factual audience census or schema enum.

## 4. GT5: retain the pressure point, bound its force and its evidence

**Retain the constitutional branch as the default priority.** The speech
raises the opposing claim itself and postpones its full response. The
strongest supported diagnosis is that the confident affirmative constitutional
claim receives a compressed case, with a still-contested reading left for
another occasion. That is more specific than attacking emotional heat,
demanding an abolition implementation plan, or treating OCR as authorial prose.

**Clarify "load-bearing."** GT5 calls this the "single load-bearing soft spot."
Read against GT2, that can mean the key's selected red-team target. It must not
mean that defeating this branch defeats the entire indictment. E11 supplies
the reason, and Section 2 states the counterfactual consequence. This is a
cross-anchor ambiguity to remove, not a claim that the existing key already
orders a whole-speech failure.

**Distinguish text from an informed adversary's import.** The analyzed speech
names the pro-slavery constitutional defense, but does not individually name
the three-fifths, fugitive-slave, and slave-trade clauses listed by the key.
Those clause names are the key's specification of the informed challenge,
not quotations or enumerated anchors in this body. A diagnosis may identify
the existing constitutional locus without pretending those names occur on
the page. Do not reward a familiar clause list as evidence of fresh discovery.
This ruling neither tests the legal force of those clauses nor changes GT3's
registered objection zone.

**Strongest competing candidate considered:** E09's claim that the churches'
opposition would scatter the system of slavery. A critic could distinguish
institutional complicity from sufficient power to end the system. The address
does offer backing, including Barnes's assertion and the English-church
comparison at lines 1209–1230; it is not a missing-support case. Treating the
quoted "an hour" at lines 1137–1139 as a literal deadline would also confuse
oratorical emphasis with an operational forecast. On the existing calibration
scope, I do not elevate this above the explicitly staged constitutional
dispute or propose a new accepted key. It remains a reason not to generalize
"selected first target" into proof that the speech permits no other substantive
pressure. Relative ranking is a judgment for further adjudication.

**Proposed calibration wording:**

> Prioritize the expressly contested constitutional subclaim and its deferred
> full backing. State the local consequence of that challenge without
> converting it into a defeat of the core indictment. Distinguish the defense
> actually stated in the speech from particular clause names supplied by the
> evaluator. Genre-generic tone, implementation, and OCR objections do not
> substitute for this constitutional locus.

## 5. GT6: a disclosed limitation is not an outstanding disclosure task

The present target offers two branches: supply the textual backing **or**
explicitly flag its deferral. E12, E13, and E15 establish that the second branch
is already fulfilled. The named authorities are also openly identified; the
speech is not presenting their full arguments as if it had demonstrated them
on this page. Recommending another disclosure without naming a residual
communication failure manufactures work.

The strongest defense of the existing key is that the disjunction already
permits leaving the source as it stands. That is a charitable and workable
reading. But "Correct first repair target" does not currently make the
already-satisfied branch explicit, and can reward a generic "add a caveat"
answer which has overlooked the actual caveats. The proposed wording removes
that ambiguity while preserving the first branch when the task calls for it.

The remaining backing issue is real on the speech's affirmative constitutional
claim; deferral does not prove that claim. Under the registered calibration it
can remain a Should-Fix-at-most soft spot, with Could-Fix defensible when
additional rigor would not change the oration's central work. **Severity and
the decision to commission expansion are different questions.** Reporting the
limitation need not produce a mandatory revision inside this address.

| Declared editorial purpose | Defensible first-target judgment |
|---|---|
| Assess this bounded oration on its own terms | Recognize the existing disclosure; preserve it. Report the constitutional limitation without inventing a missing caveat or mandatory insertion. |
| An explicitly requested fuller treatment must carry the constitutional case independently | Backing for that contested subclaim is the upstream target. Describe the unresolved requirement; do not supply Douglass with a newly written legal argument. |
| Ask whether additional disclosure alone fixes the limited backing | No: the disclosure already exists and the evidentiary limitation remains. |

The second row is a conditional change of editorial brief, not a task secretly
assigned to the historical address. No present author preference is inferred.
The [argument coaching protocol](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/plugins/apodictic/skills/revision-coach/references/argument-coaching-protocol.md)
puts warrants before objection handling in its usual dependency order. That
ordering applies **when the repair is undertaken**; it does not establish
that every named warrant limitation must become a new writing assignment.
Backing and response quality describe the same local work here, rather than
two independent edits whose order can be mechanically reversed.

**Proposed calibration wording:**

> The full constitutional demonstration is expressly deferred. Give credit
> for recognizing that existing disclosure; do not prescribe it as missing.
> If the declared task requires a self-contained defense of the constitutional
> subclaim, identify its backing as the first substantive target, coupled to
> the already-raised opposing interpretation. Otherwise preserve the bounded
> deferral and report the residual soft spot without requiring expansion.
> Neither path licenses rewriting the prophetic form or adjudicating the
> Constitution's actual meaning.

Confidence is high that disclosure already exists, and moderate that this
conditional wording is the best calibration policy. The latter depends on
the benchmark's intended meaning of "repair" and requires independent
adjudication before any key change.

## 6. Disposition and follow-through

| Anchor | Recommended disposition | Remaining uncertainty |
|---|---|---|
| GT4 | Retain form protection; refine audience calibration by claim and distinguish source evidence from contextual audience metadata | Historical attitudes are not measured here |
| GT5 | Retain the constitutional priority; clarify local dependency and evaluator-supplied clause detail | Exclusive ranking beyond this calibration scope is not established |
| GT6 | Revise the proposed repair wording to recognize completed disclosure and make further backing conditional on the editorial brief | Final acceptance of conditional/no-insertion answers needs a licensed policy decision |
| GT2/GT3/GT7/GT8 | No change proposed in this slice | Existing scoring and premise-truth boundaries continue to govern |

Three useful questions for a later adjudicator are: does the response notice
the existing deferral; does it state what the constitutional challenge would
and would not defeat; and does it preserve the speech's rhetorical method
without using cultural charity to excuse an unidentified inferential gap?
These are review questions, not newly registered scoring anchors or executable
acceptance tests.

For any future key amendment, use the existing
[benchmark handoff and licensing process](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/evals/fixtures/argument-benchmark/HANDOFF.md).
Do not reinterpret earlier engine scores using this proposal, convert model
agreement into a Reliability promotion, or present this report as completing
the separate modern-source recall-suspect check. This delivers the public-domain
provisional-anchor slice of FR-01 only.
