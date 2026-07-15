# Argument Register & Rhetorical Stance Triage — Build Spec
## APODICTIC Nonfiction Argument Engine Extension
*Date: July 15, 2026 (reworked same day per spec review)*
*Status: Build in progress — shared schema, AT5/GN reference layer, routing/synthesis integration, and the stance-calibration shape gate are implemented; E7 has two convergent preliminary blind reads, but their records need a strict machine-conformant rerun before Built.*
*Origin: Mediocratopia Ch. 7 probe (Rao, 2019). Two distinct gaps identified: a routing register for generative nonfiction, and a per-instance stance axis for productive overstatement. **Premise correction from pilot:** the base audit discriminates better than the origin probe suggested; the gap is aim, not volume — see Appendix B.*
*Depends on: nonfiction-argument-engine skill, Dialectical Clarity v2.1, intake-router-runtime §6, nonfiction-intake-routing fragment, output-policy.md (severity vocabulary + Deficit Lock), apodictic.finding.v1 / apodictic.argument_spine.v1 schemas, Argument_State schema. Precedents: ai-prose-calibration.md Layer C source triage (in-repo), setec-voiceprint craft-restoration (upstream origin).*

*Build clarification (2026-07-15): the initial file map's three optional finding fields
could record a verdict but could not mechanically distinguish a demotion from an earned
verdict recorded without demotion, or join a finding to a prescriptive cash-out. The build
therefore adds `calibration_effect` and `cash_out_ref`, plus exact §1 high-stakes/cash-out
records. This is the minimum data needed for the promised shape gate; it does not expand
the engine's judgment authority.*

---

## What This Document Is

A build specification for two related but **separately shippable** fixes to the argument engine:

1. **Fix 1 — Argument Register (document-level).** A new intake register for generative/exploratory nonfiction — claim-bearing essays whose success condition is fertility, not soundness (Ribbonfarm-style lens essays, aphoristic philosophy, essayistic think-pieces). Closes the routing crack between "persuasive-argument family" and "personal essay without a claim ladder."

2. **Fix 2 — Rhetorical Stance Triage (instance-level).** A per-flag triage layer that classifies overstatement-family findings as earned / unearned / earned-by-frame **at severity-assignment time**, before the Deficit Lock commits them. Gives the engine a vocabulary for productive overstatement, provocation, and strategic misreading — moves the current audits can only see as defects.

The two compose but do not depend on each other. **The central design constraint, stated precisely:** neither fix changes any base severity *criterion*, adds a severity tier, or touches any finding after the Deficit Lock commits it. All calibration operates within the existing three-token severity vocabulary (Must-Fix / Should-Fix / Could-Fix) and executes at Triage, upstream of the lock — exactly where the existing burden floor already operates. Any dial loosened enough to pass Nietzsche also passes genuine fallacy in a policy brief; these fixes add classification upstream of severity commitment, never subtraction downstream of it.

---

## Review Disposition (2026-07-15)

The spec-review swarm (six adversarial lenses + synthesizer, all lenses reported) returned **NEEDS-REWORK**: 2 P1, 6 P2. Disposition of every prioritized fix:

| # | Review finding | Resolution in this version |
|---|----------------|---------------------------|
| 1 | **P1.** Demotion targeted "Observational," a tier the engine cannot represent (canonical vocabulary is exactly Must-Fix/Should-Fix/Could-Fix, enum-enforced; parallel vocabularies forbidden) | Demotion target is now **Could-Fix**. No fourth tier. The `stance`/`stance_verdict`/`register` ledger fields carry the calibration semantics. Pilot ledgers, which used a run-harness-injected 4-band scale, carry a canonical remap note (Appendices A/B). |
| 2 | **P1.** Stance triage at Step 9 runs after the Triage-time Deficit Lock; demotion there is mechanically-detected post-lock softening (`honesty_check.py` ERROR) | Calibration relocated **upstream of the lock**: it runs at Triage severity assignment (run-synthesis §Step 5), so the locked severity IS the post-calibration severity — mirroring the burden floor. Post-lock adjustment uses only the existing ID-scoped `softness-downgrade` override marker + Appendix B entry; no new pathway. |
| 3 | AD4 (document-wide content-triggered gate) contradicted AD3/§1.2 (register covers the journey) on the good-faith hybrid | **Decided: per-cash-out-span** for content-resolved consequence; document-wide only for the intake-declared high-stakes signal. AD4 rewritten; E7 hybrid fixture added to the validation plan. |
| 4 | Content-derived consequence=HIGH is model judgment presented as a codifiable hard gate | Reclassified as a **non-verifiable heuristic** bound to the Argument_State §1 consequence-context field, with a mechanical backstop that does not depend on it (any prescriptive/action-demanding cash-out forces asserted assessment at that span). |
| 5 | Trigger set named a nonexistent "GT" code family; omitted FM-A13; collided with GT8 premise-plausibility axis | Codes corrected throughout: FM-A17 (anecdote-to-principle), FM-A19 (authority overreach), FM-A14 (epistemic erasure), FM-A13 added, CL4 for definitional smuggling. Explicit GT8 exclusion added (§2.5). |
| 6 | New ledger fields and AT5 routed only to a docs file, not the machine-validated schemas | File Map now includes `schemas/apodictic.finding.v1.schema.json` (three optional enum-typed properties, following the `salience` precedent) and `schemas/apodictic.argument_spine.v1.schema.json` (AT5 in the `argument_type` enum + `$comment` mirror). |
| 7 | GN0/GN1/GN3 had no severity mapping; GN1 unbuildable without examples | Severity tokens assigned (§1.3); GN1 worked positive/negative example pair supplied (§1.3). |
| 8 | Ship gates were blind-auditor judgments with no mechanical harness; monotonicity gate had no join key | Gates designated **manual reviewer gates** with a stated reproducibility protocol; expected profiles re-encoded in canonical tokens; monotonicity join key defined (per-code-family maximum-severity comparison); groundtruth-harness wiring listed as a build task (§Validation). |
| 9 | §2.4 called function-under-detection "mechanically checkable," contradicting §Smooths-Over | "Mechanically checkable" struck. The verdict is an operationalized re-reading *candidate returned to the writer*; only ledger shape (field presence + enum membership) is mechanically checkable (§2.4). |
| 10 | Nearer in-repo precedent (ai-prose-calibration source triage) uncited; fork risk | Cross-referenced with an explicit domain boundary (§2.2). |

---

## Architecture Decisions (Binding)

1. **Register is declared, never inferred silently.** The generative register is set at intake by the writer (or confirmed by the writer when the router proposes it from textual signals). The engine may *propose* the register — associative structure, self-flagged play, hedged landings are signals — but a run never silently adopts it. Otherwise every sloppy op-ed becomes "exploratory" retroactively. Register inference without confirmation is a QA failure.

2. **Register and stance change calibration at Triage, not coverage, and never post-lock.** Under the generative register, every existing audit still runs and every finding is still recorded in the Findings Ledger. What changes is the severity assigned *at Triage* (most WR/SM/BP findings on non-cash-out spans floor at **Could-Fix** instead of Should-Fix, with `register`/`stance` fields recording why) plus the addition of register-specific failure codes (GN-codes) that give the audit something *positive* to diagnose. The Deficit Lock then commits the post-calibration severity; nothing in either fix lowers a locked severity except the existing ID-scoped `softness-downgrade` override (output-policy.md §Deficit Lock), which these fixes neither extend nor bypass. A generative run that returns "no findings because nothing applies" is a build failure.

3. **The cash-out principle.** A generative essay carries full burden at every point where the lens is converted into an assertion or prescription, proportional to how hard the conversion is pressed. "You should probably amble along" (light press, self-hedged) carries light burden. "Therefore this agency should adopt X" carries full AT3 burden *regardless of register*. The register covers the journey, never the landing. This is what prevents the register from functioning as a motte (see GN2).

4. **The stakes gate has two mechanisms with two scopes.**
   - **Intake-declared high-stakes (document-wide, mechanically checkable):** the existing high-stakes signal (testimony, expert affidavit, regulatory comment, legal brief, peer-reviewed publication, explicit flag, court/legislature/regulator/panel audience — `argument-audits-routing.md`) forces `register=asserted` for the whole document and blocks all stance demotion everywhere in it. Provocation is not a defense in front of a legislature.
   - **Content-resolved consequence (per-cash-out-span, heuristic):** when the *content* demands real-world action (legislation, institutional decisions, resource allocation), that consequence attaches to the **cash-out span**, not the whole document: the span is assessed at full asserted burden and findings located at it are ineligible for stance demotion, while genuine journey spans elsewhere in the piece remain demotable. This resolves the hybrid case (1,800 words of real lens play landing on one hard prescription) in favor of the journey/landing doctrine (Decision 3). Content-resolution is **model judgment, honestly labeled**: it is bound to the Argument_State §1 consequence-context field (recorded, cross-checkable for presence and consistency against declared form/audience — not for correctness). The mechanical validator proves the backstop only for findings that carry a `cash_out_ref` resolving to a prescriptive row; it cannot infer an omitted join from prose location. Completeness of those joins remains an auditor/E7 obligation until the inventory gains a reverse finding-ID map. (Pilot A4 applied a document-wide version of this heuristic unprompted; the per-span scoping is the deliberate design, and E7 tests it.)
   - Precedence, highest first: **intake-declared gate → per-span content backstop → register defaults → instance stance.**

5. **Stance triage adjudicates the move, never the claim.** The triage classifies a flagged instance's rhetorical register and whether its burden is discharged in-frame. It never rules the provoked or overstated claim true or false. This is the same line the Firewall already draws for premise-plausibility flags (engine QA guardrail 5), extended to rhetorical moves.

6. **Ambiguous verdicts return to the writer.** Following the source-triage precedent: the earned/unearned verdict is irreducibly a writer's call per instance when the tests below (§2.4) do not converge. The engine reports the tests' outputs and the candidate verdict (`stance_verdict: divergent`); it does not manufacture confidence.

7. **Fiction path untouched.** Both fixes live entirely on the argument path (nonfiction-argument-engine + argument-cluster audits). No changes to fiction routing, fiction passes, or fiction severity mapping.

8. **Honest scope: this is a development editor, not a bad-faith detector.** Because register is writer-declared and verdicts defer to the writer, the extended engine serves writers working on their own drafts. It cannot and must not be presented as a neutral instrument for detecting bad-faith argument in third-party texts. Document this limitation in the audit reference.

---

## Fix 1 — Argument Register

### 1.1 The gap

The current delegation contract splits nonfiction three ways: argument-shaped (extractable claim + persuasive form) → argument engine; scene-led → narrative nonfiction; witness-led → memoir/CNF. A lens essay falls in the crack: it **has** an extractable claim ladder (Mediocratopia Ch. 7 lands on an explicit "you should amble"), so it routes to the argument engine — but it **does not accept the burden that ladder implies.** Its success condition is "does the lens do productive work," not "is the conclusion warranted." Run against the asserted-register rubric, the engine dutifully produces WR0 (analogy-as-warrant), CL4 (definitional smuggling — "gait" migrating from biomechanics to life-tempo), FM-A17 (anecdote-to-principle — plantation ambling horses → mediocrity-as-endurance), FM-A8 (false precision — uncited "brain stem" gestures) — all accurate, all measuring an amble against a sprinter's rubric.

The existing burden field (HIGH/MEDIUM/LOW) cannot fix this: it governs severity *floors within* the asserted register; it does not ask the prior question of whether the piece is making the kind of claim that needs warranting at all.

**Premise revision (pilot, 2026-07-15).** A blind run of the current audit on the same chapter (Appendix B, run A1) shows the base engine's personal-essay calibration + Distinguish Protocol already absorb much of the predicted flood: 0 Must-Fix, WR0 capped at Should-Fix as "recoverable-as-metaphor," verdict UNCONVENTIONAL-BUT-WARRANTED. The register's justification is therefore **not** false-positive suppression. It is *aim*: the base run's Should-Fixes target the lens itself (the horse→human analogy, the definitional migration — the essay's *method*, which the writer would rightly refuse to repair), while the machinery run's Should-Fixes target the *cash-outs* (the borrowed-authority landing, the unengaged self-undermining objection — things a good editor would actually ask this writer to fix). Same text; the register redirects the diagnostic from the instrument to the landings. Secondary justification, discovered on the fallacious fixture (run A4): mandatory per-cash-out assessment converts the base audit's evaluability-shaped WARRANTED blind spot into a real defeat detector — see §Validation, E3.

### 1.2 New argument type: AT5 (Generative / Lens-Offering)

Add to Dialectical Clarity Step 1's type table **and to the `argument_type` enum in `schemas/apodictic.argument_spine.v1.schema.json` (with its `$comment` mirror and the docs/argument-state-schema.md §1 table)** — until the enum is extended, AT5 fails spine validation identically to any unknown token:

| Code | Type | Promise to Reader | Burden Level |
|------|------|-------------------|--------------|
| **AT5** | Generative | "Here's a lens; look through it and see what it reveals" | Split — see below |

**AT5 burden split** (mirroring the AT4 precedent: do not create free-floating looseness, diagnose *within* the type):

1. **Coherence burden** — the lens must survive its own development. Internal consistency of the metaphor/frame as it extends. LOW-MEDIUM.
2. **Fertility burden** — the lens must do generative work: reveal, reframe, or connect something not visible without it. This *replaces* soundness as the success criterion. It is a real burden — an inert lens fails it (GN1).
3. **Cash-out burden** — every conversion of lens into assertion or prescription carries burden at the asserted level, scaled to press (Architecture Decision 3). The audit must locate every cash-out point and assess each one at asserted-register standards.

**Why not a document-level "exploratory mode" instead of an AT-code?** Because the type system is already where every downstream step calibrates ("all later steps calibrate by type"), and because real essays are hybrid — an essay can be AT5 for 1,800 words and AT3 for its final paragraph. Locating the register in the type system, with cash-out points assessed at their own type, handles hybridity without a second parallel mechanism.

### 1.3 New failure codes: GN namespace

The register must generate findings, not suppress them. New codes, Dialectical Clarity, with severity tokens in the canonical vocabulary:

| Code | Name | Description | Severity |
|------|------|-------------|----------|
| **GN0** | Register instability | The piece oscillates between lens-offering and asserting without signaling; reader can't calibrate whether they're being invited to play or asked to believe. (Parallel to AT0.) | Should-Fix default; Could-Fix when the wobble is local and the dominant register stays legible |
| **GN1** | Inert lens | The lens is introduced, developed, decorated — and never does work. Nothing is revealed that was not visible without it. Fertility burden unmet. | Should-Fix when fertility is the piece's operative success criterion (an AT5 run with no other warrant); Could-Fix when the inert lens is ornamental to a piece that also argues |
| **GN2** | Concealed cash-out | An assertion or prescription is delivered at full force under exploratory cover — the register functioning as a motte. Cross-reference DI4/FM-A13: GN2 is its register-level form. **GN2 findings are never demoted; they are what the register exists to catch.** | Floors at the severity the equivalent asserted-register finding would carry (Must-Fix when it defeats a decision test, per the base audit's rules) |
| **GN3** | Broken lens | The metaphor contradicts its own terms when extended; the frame fails coherence burden. | Should-Fix (a coherence failure of the piece's own instrument) |
| **GN4** | Borrowed authority unreturned | Technical precision is imported (neuroscience, control theory, statistics) and ends up doing *warrant* work at a cash-out point rather than illustrative work in the lens. Texture is fine; load-bearing borrowed authority at the landing is not. | Floors at the severity the equivalent asserted-register finding would carry |

**GN1 worked example pair.** *Positive (fertile — GN1 does not fire):* Mediocratopia Ch. 7's gait lens — it converts "one day at a time" from platitude to mechanism (time as multi-threaded behavioral tempo), connects four domains, and yields a reframing (amble-as-endurance-strategy) not statable without it. *Negative (inert — GN1 fires):* a "city as organism" essay that renames traffic "circulation," housing "cells," and governance "the nervous system," then concludes cities need all three to work — the lens relabels; every conclusion was available pre-lens. The diagnostic question: state the essay's conclusions with the lens vocabulary deleted; if nothing is lost, the lens is inert.

**Severity mapping under `register=generative` (applied at Triage, before the Deficit Lock):**

- GN2 and GN4 floor at the severity the equivalent asserted-register finding would carry.
- WR / SM / BP findings on non-cash-out spans floor at **Could-Fix**, recorded with `register: generative` in the finding block, with a note naming what a reader who rejects the lens loses.
- CL4 / definitional-drift findings: a term migrating from technical to metaphorical sense is the METHOD of a lens essay, not automatically smuggling. Flag only when the migration is concealed at a cash-out point (the borrowed precision is still being spent as if technical).
- All cash-out points must be individually located, listed, and assessed at asserted burden; findings located at prescriptive/action-demanding cash-outs are ineligible for any register or stance calibration (Architecture Decision 4).

### 1.4 Routing changes

**`nonfiction-intake-routing.md`** — add a fourth route:

> **Route to the Nonfiction Argument Engine with `register=generative` when:**
> 1. the manuscript makes an extractable claim or offers an organizing lens, AND
> 2. the dominant mode is exploratory: associative development, metaphor extension, thinking-in-public, aphoristic or essayistic structure, AND
> 3. the writer confirms the register at intake (proposed-then-confirmed; never silently inferred), AND
> 4. no intake-declared high-stakes signal is present (Architecture Decision 4; high-stakes forms cannot take this register).

Add to the Default activation table:

| Form | Default route |
|---|---|
| Lens essay / exploratory essay / aphoristic sequence / blog-native serial essay | Dialectical Clarity with `register=generative`; offer Red Team on cash-out points only |

**`intake-router-runtime.md` §6 Table A** — add the corresponding form row(s).

**`nonfiction-argument-engine/SKILL.md`** — add `register` to the run-shape fields passed from core-editor (`asserted` default | `generative`), and QA guardrails: *"Register confirmation before calibration. A generative-register run must record the writer's confirmation at intake and a consequence-context value in Argument_State §1. Register inferred without confirmation is a QA failure. Intake-declared high-stakes signal present → register forcibly `asserted`."*

**`dialectical-clarity.md` §By Argument Form** — new entry:

> **Lens Essay / Exploratory Essay:** AT5 primary, often with an AT2/AT3 tail at the landing. The claim ladder exists but is load-tested only at cash-out points. GN2 and GN4 are the signature risks: the register invites smuggling. Definitional migration (a term drifting from technical to metaphorical sense) is *the method*, not automatically CL4 — flag it only when the migration is concealed at a cash-out point. WR0 on analogy spans: Could-Fix, with the note naming what a reader who rejects the analogy loses. NE-codes: vignettes in lens essays are lens-fodder, not evidence; flag NE only at cash-out. The Distinguish Protocol applies aggressively; the essay may legitimately decline every objection that targets the lens as if it were a thesis — but not objections that target a cash-out.

**`argument-audits-propagation.md` / `synthesis-argument.md` / Argument_State schema** — `register` field propagates into the Argument_State spine block and the Argument-DE letter's opening frame (the letter must *say* which rubric it applied). Finding blocks gain the optional fields specified in §File Map.

---

## Fix 2 — Rhetorical Stance Triage

### 2.1 The gap

Every overstatement-family audit — CL4 (definitional smuggling), FM-A8 (false precision), FM-A17 (anecdote-to-principle), FM-A19 (authority overreach), FM-A12 (emotional inflation), DI4/FM-A13 (motte-and-bailey), FM-A14 (epistemic erasure / straw man) — is built to catch overstatement **as a defect.** There is no axis for overstatement **as technique.** The engine can already *see* the moves (extraction catches Rao's mock-heroic "the mediocrity revolution for horsekind," the self-flagged pun, the audience-segmenting asides); it has no vocabulary to score them as earned vs. symptomatic. The hard case is the philosophers: a writer who deliberately misreads — Rortyan redescription, Nietzschean polemic, Bloomian strong misprision — trips the audits *precisely because the misreading is the productive move.* The engine currently flags its most valuable inputs hardest.

This cannot be fixed by loosening: deliberate misreading is a *hard* violation of the audits' criteria. It needs a new construct — an intent/register axis per instance — not a dial.

### 2.2 Prior art and domain boundary

Two precedents, one boundary:

- **In-repo (nearer):** `specialized-audits/references/craft/ai-prose-calibration.md` Layer C source triage, with earned/unearned illustrations per named pattern in `ai-prose-calibration-level-setting.md`. Same verdict vocabulary (earned / unearned / earned-by-frame), same "the verdict is irreducibly the writer's call per instance" doctrine, same honesty posture (most flags resolve as earned; the framework's authority rests on saying so).
- **Upstream origin:** setec-voiceprint craft-restoration, from which the in-repo calibration derives.

**Domain boundary (deliberate, not a fork):** prose-pattern source triage adjudicates *voice and craft patterns* (AIC flag families — is this uniformity a smoothing artifact or a drumbeat?); rhetorical stance triage adjudicates *argumentative moves* (overstatement-family codes — is this exaggeration doing concealed warrant work?). Distinct flag families, distinct tests (source triage leans on voice attribution and callback knowledge; stance triage leans on function-under-detection), no shared verdict storage. The shared vocabulary is intentional — writers should meet one earned/unearned concept across the toolchain — and the two constructs must be cross-referenced in both reference files so neither drifts into the other's domain.

### 2.3 Stance taxonomy

New reference file `specialized-audits/references/craft/rhetorical-stance-triage.md`. Per-instance stance codes:

| Code | Stance | Description | Canonical example |
|------|--------|-------------|-------------------|
| **S1** | Sincere assertion | Default. The move is offered as straight argument. | — (all current audit behavior assumes S1) |
| **S2** | Marked play | Irony, mock-heroic, bathos, self-flagged pun or wink; the text marks the move as play. | Rao: "the mediocrity revolution for horsekind"; "(hehe!)" |
| **S3** | Productive overstatement | Deliberate strong-form claim intended to be pushed against; the exaggeration is the engine of the piece. | Nietzschean polemic; the deliberately too-strong opening thesis |
| **S4** | Strategic misreading | Deliberate or indifferent misprision of a source that generates a new position. | Rortyan redescription; strong misreading of a canonical figure |
| **S5** | Performative provocation | The move's function is the reaction it provokes, not its content. | Trolling proper |

S5 is recognized but largely **not served**: a development editor can name it and assess whether it is doing what the writer wants, but the engine offers no earned-verdict pathway that demotes severity for S5 in any form with real consequence context. Document this boundary in the reference.

### 2.4 The verdict and its tests

Verdicts (ported): **earned / unearned / earned-by-frame**, plus **divergent** (tests disagree; verdict returns to the writer).

Core principle — **function under detection**: *a move is earned if and only if it retains its function when the reader sees it for what it is.* Productive overstatement and strategic misreading survive detection — Nietzsche's polemic still works on a reader who knows it's polemic; a Rortyan redescription is *offered* as redescription. Deception requires non-detection — a motte-and-bailey collapses the moment the reader sees both positions; laundered evidence stops working when its provenance is visible.

**Enforcement honesty:** the test is *operationalized* — re-read the span as if the move were explicitly labeled, and ask whether the argumentative work still happens — but it is model/reader judgment, not a mechanical check. The verdict is a **candidate returned to the writer** (Architecture Decision 6), never an adjudication. The only mechanically checkable surface is ledger shape: field presence and enum membership (`validate.sh` — see §File Map). Any build that treats the model's verdict as authoritative fails this spec.

Supporting tests (run all three; convergence → the candidate verdict carries; divergence → `stance_verdict: divergent`, tests' outputs reported, writer decides):

1. **Signaling test** — does the text mark the move (register shift, bathos, self-flag, explicit hedge, genre convention the audience demonstrably shares)? Marked → earned-by-frame candidate.
2. **Payoff test** (ported from the source-triage precedent) — does the overstatement pay off in the piece's economy? Is something built on the provocation that could not be built on the hedged version? A provocation that funds nothing downstream is unearned regardless of intent.
3. **Function-under-detection test** — as above. This is the decisive test when the first two disagree.

**Stakes-gate interaction:** under an intake-declared high-stakes gate the triage still runs and the stance is still recorded — the record is diagnostic gold for the writer — but no verdict demotes severity. An earned S3 in draft testimony records `calibration_effect: blocked-high-stakes`; unearned/divergent records keep full severity without a block effect because no demotion was attempted. A natively Could-Fix finding may still carry the block record: the committed finding stores post-triage severity, not a before/after pair, so `Could-Fix` alone is not proof that a demotion occurred. Findings joined to prescriptive cash-out spans are likewise ineligible (Architecture Decision 4), regardless of register or verdict.

### 2.5 Integration points

- **Triage severity assignment (run-synthesis §Step 5), upstream of the Deficit Lock** — the mandatory location. Before any overstatement-family code (CL4, SM4, WR-on-analogy, BP4, DI4/FM-A13, FM-A8, FM-A12, FM-A14, FM-A17, FM-A19) is committed to the ledger, run the triage; the committed severity is the post-triage severity. Earned or earned-by-frame → **Could-Fix**, with `stance`/`stance_verdict` recorded. Unearned or divergent → severity unchanged. **Explicit exclusion:** stance triage never touches the GT8 premise-plausibility axis — premise flags record contestability, are Firewall-walled from adjudication, and have no stance dimension.
- **Step 9 (Distinguish Protocol)** — retains its existing false-positive role; it may *surface* stance evidence, but any severity consequence discovered post-lock routes exclusively through the existing ID-scoped `softness-downgrade` override marker + Appendix B (Severity Calibration) entry. No new post-lock pathway.
- **Argument Red Team** — a red-team reader must attack S3/S4 material *as its strongest sincere reconstruction*, not as the surface overstatement (attacking the surface of a deliberate provocation is the red-team version of a false positive). Add one calibration paragraph to `argument-red-team.md`.
- **Firewall (engine QA guardrails)** — add guardrail: *"Stance verdicts classify the move, never the claim. Any output that treats an 'earned' verdict as evidence the overstated claim is true — or 'unearned' as evidence it is false — fails the Firewall check."*
- **Interaction with Fix 1** — orthogonal, composable. Register sets document-level Triage calibration defaults; stance triage adjudicates instances. Register-floor is therefore independent of the instance verdict: an unearned/divergent annotation can coexist with a generative register floor, while `stance-demotion` still requires an earned verdict. A sincere policy brief can contain one earned mock-heroic flourish (S2, earned-by-frame, Could-Fix). A generative essay can contain an unearned concealed cash-out (GN2, full severity). Precedence per Architecture Decision 4.

---

## What This Spec Smooths Over

Named per house practice; these are accepted costs, not open questions.

1. **Function-under-detection is a judgment call wearing a test's clothes.** It is *more* operational than "is this earned?" asked cold, but a sophisticated reviewer and a motivated writer can still disagree about whether a detected move "still works." The fallback (verdict returns to the writer) is honest but means the construct disciplines the conversation rather than settling it. §2.4 now states the enforcement limit explicitly.
2. **Writer-declared register means the engine trusts the writer.** Right trade for a development editor whose client is the writer; it forecloses using the engine as a neutral detector of bad-faith argument (Architecture Decision 8). GN2 and joined per-span cash-out records partially compensate — but only partially.
3. **Hybrid essays stay noisy.** An essay that is genuinely half-asserted, half-generative will produce a ledger with two calibration regimes in it. The per-cash-out mechanism handles this structurally, but the editorial letter will be harder to write; letter-synthesis guidance for mixed-register, high-count ledgers is a named pre-merge carry-forward (Appendix B).
4. **Fertility burden (GN1) is the least testable burden in the system.** The worked example pair (§1.3) and the lens-deletion diagnostic question give it a floor; the audit reference should extend both. It will never have a checklist.
5. **The S-taxonomy will leak.** Real moves blend S2/S3/S4. The codes are for ledger legibility, not ontology; instruct auditors to pick the dominant stance and move on.
6. **Content-resolved consequence is a heuristic and always will be.** The mechanical backstop catches a prescriptive cash-out only after a finding is joined to its `CO#`; omission of that optional join is not mechanically observable. A piece whose consequence is real but implicit (self-help with no imperative sentence), or whose finding omits the join, can still slip the heuristic. The intake-declared gate exists for forms where slipping is unacceptable; E7 audits join completeness.
7. **The shape gate proves recorded calibration, not undeclared behavior.** A native Could-Fix finding with no stance fields is indistinguishable from a silent demotion unless the mechanism family itself supplies a complete reverse inventory. The validator therefore guarantees that recorded earned verdicts demote honestly and recorded blocks/joins are coherent; it does not prove that every eligible finding was declared. Auditor protocol and E7 cover that boundary in this increment.
8. **Committed severity is not a before/after severity pair.** For an asserted finding under a blocking gate, `severity: Could-Fix` may be native or may be an illicit pre-commit demotion; the current finding schema cannot distinguish them. Rejecting every blocked Could-Fix record would make the legitimate native case unrepresentable. The validator rejects mechanically visible floor signatures (for example explicit generative register at a prescriptive join), while the blind protocol compares the pre-triage analysis to the committed ledger. A future before-severity field could close this boundary, but this increment does not pretend the post-triage token proves history.

---

## Validation Plan

**Gate type: manual reviewer gates, honestly labeled.** Every gate below is evaluated by a blind strong-tier auditor (pinned model, fresh context, no access to this spec or to other runs), because the machinery under test is itself judgment-dense — there is no mechanical oracle for "did the triage aim correctly." Reproducibility protocol: the auditor prompt templates and the blinded machinery addendum are vendored in `evals/register-stance-pilot/`; expected outcomes are encoded as severity profiles in the canonical three-token vocabulary; calibration gates accept N=1, ship gates require N=2 concordant runs on any re-validation after machinery changes. **Build task:** wire E1–E7 into the existing groundtruth/fixture-manifest harness (`evals/fixture-manifest-template.md`) with the encoded expected profiles, so re-validation is a checklist, not an improvisation.

**Expectations are written against ledger severity profiles, not verdict lines.** Pilot lesson: the base warrant verdict measures *evaluability* (can a careful reader identify, test, and judge the claims), so a deliberately fallacious piece whose manipulations are visible on the page returns WARRANTED (pilot A2 did exactly this). Verdicts under-discriminate by design; severity distributions and finding *aim* carry the signal.

**Severity-token note:** pilot runs (Appendix B) used a run-harness-injected 4-band scale (Must-Fix / Should-Fix / Consider / Observational). Canonical remap for all expectations below and all future runs: **Consider → Could-Fix; Observational → Could-Fix** (the pilot's C/O distinction collapses into Could-Fix, with the `stance`/`register` fields carrying the "calibrated, structurally clean" semantics the pilot's O-band expressed). Pilot tables are preserved unremapped as historical record.

| # | Fixture | Run shape | Must produce | Status |
|---|---------|-----------|--------------|--------|
| E1 | Mediocratopia Ch. 7 | `register=generative` (confirmed) | ≤1 Must-Fix. Lens-method findings (WR-on-analogy, definitional migration) calibrated to Could-Fix at Triage with stance recorded. Every cash-out individually located and assessed; GN4 live on the brain-stem span at asserted severity. | **PASS** (A3: 0 MF; GN4 on the predicted span; bonus real finding OB3) |
| E2 | Same chapter | `register=asserted` (default) | Base behavior unchanged: Should-Fix findings aimed at the lens/method spans, severity distribution materially softer than E3-baseline. **Proof that the register shifts aim without any base threshold moving.** | **PASS-as-revised** (A1; predicted "flood" was wrong — expectation rewritten to aim-shift) |
| E3 | Fallacious op-ed fixture whose intake answers *claim* the generative register | `register=generative` (claimed) | Register-integrity check REJECTS the claim from structure; GN2 at Must-Fix on the concealed cash-outs; machinery run at least as severe as the base run on the same text (monotonicity gate below). | **PASS, exceeded** (A4: 4 MF, UNWARRANTED via disowned-causal-bridge defeat the base run missed) |
| E4 | Testimony fixture with one self-flagged mock-heroic flourish | asserted, intake-declared high-stakes | Stance triage runs; S2/earned-by-frame recorded; **no demotion** (document-wide gate), with the block recorded, not silently applied. | **PASS** (B4: demotion explicitly blocked-and-recorded; gate moot for unearned findings; planted superlative caught) |
| E5 | Nietzsche, "The Problem of Socrates" (public-domain, vendored) | `register=asserted`, low consequence | S3/S4 earned verdicts on the misprision spans via function-under-detection; overstatement findings calibrated to Could-Fix with stance recorded; sincere load-bearing claims audited at full severity (no halo). | **PASS** (B5: 4 demotions with deciding tests named; master warrant and self-undermining structure held at Should-Fix; divergent-verdict protocol exercised) |
| E6 | Bare motte-and-bailey fixture ("The Willpower Myth"): sincere register, low consequence so demotion is *available*, bailey styled to tempt an S3 reading | `register=asserted` (default) | DI4/FM-A13 at full severity; function-under-detection explicitly fails (the move requires concealment); stance triage must *not* rescue it. | **PASS** (B6: DI4/FM-A13 at Must-Fix with the oscillation structure named; UNWARRANTED on scope-honesty; S3 rescue considered and refused — "a genuine S3 polemic survives detection; this collapses on it") |
| E7 | Good-faith hybrid fixture: ~1,500 words of genuine, fertile lens play landing on ONE hard, high-consequence prescription | `register=generative` (confirmed) | Journey findings calibrated per the register; the prescription cash-out span assessed at full asserted burden with its findings ineligible for demotion (per-span backstop, Architecture Decision 4); no document-wide re-flood of the journey. | **PRELIMINARY PASS ONLY** — two blind reads converge on behavior, but their records are not machine-conformant. A strict rerun must use canonical `CO#` joins and warrant-verdict tokens, vendor a validator-passing ledger/state pair, and pass before this draft PR merges. |

**Monotonicity gate:** on any fixture whose structure is asserted, the machinery run's severity profile must be ≥ the base run's. **Join key:** per code family (the base audit's two-letter/FM prefixes), compare maximum assigned severity: machinery-max ≥ base-max for every family present in the base run; GN-family additions are permitted (they only add). This is deliberately a family-level check — finding-for-finding joins across non-deterministic runs are not reproducible, and the family-max comparison catches the failure the gate exists for (a demotion pathway leaking severity on bad texts). A4 vs. A2 satisfies it.

**Doctrinal finding from E5 (ratified for build, 2026-07-15):** the machinery draws the earned/unearned line at **evidentiary function, not intent or productivity**. It demoted Nietzsche's provocations while returning *unearned* on his reading of Socrates' dying words — a strategic misreading that is arguably the chapter's most productive move, but which the text presents unmarked, as settled, and as its load-bearing evidentiary bookend. Misreading-as-provocation demotes; misreading-as-*evidence* carries full burden no matter how fertile. This is the cash-out principle applied at instance level: an editor *should* tell the writer where the polemic is spending unearned evidence, and the Firewall leaves the call with the writer. Named as a scope boundary, not a defect: the engine audits drafts for writers, not canons for posterity.

**The paired discriminator (E5+E6), the construct's sharpest validation:** two texts with near-identical surface boldness — "there is no willpower" and Nietzsche's eliminative polemic against Socrates — drew opposite verdicts for articulated reasons. The B6 auditor stated the discriminator unprompted: relabel the willpower essay's central claim as deliberate overstatement and the moral indictment *evaporates*, because the conclusion needs the literal eliminative claim; relabel Nietzsche's polemic as polemic and it still works. The signaling test also inverted correctly: Nietzsche's provocations are marked as provocation; the willpower essay marks its bailey as *sincere and settled* — the opposite of play-signaling. Function-under-detection is operational as a reviewer protocol (not, per §2.4, as a mechanical check).

---

## File Map

| File | Change |
|------|--------|
| `plugins/apodictic/skills/specialized-audits/references/craft/rhetorical-stance-triage.md` | **New.** Stance taxonomy, three tests, verdict rules (incl. `divergent`), stakes-gate and cash-out ineligibility, S5 boundary, GT8 exclusion, domain boundary vs. ai-prose-calibration source triage, worked examples (Rao spans as S2; Nietzsche polemic as S3/S4 earned vs. dying-words reading unearned; motte-and-bailey as the canonical detection-failure). |
| `plugins/apodictic/skills/specialized-audits/references/craft/dialectical-clarity.md` | AT5 + burden split (Step 1); GN codes with severity tokens (new subsection); Lens Essay entry (§By Argument Form); Triage-time stance-triage integration with Step 9 boundary (§2.5); GT8 exclusion. |
| `plugins/apodictic/skills/specialized-audits/references/craft/argument-red-team.md` | One calibration paragraph: attack the strongest sincere reconstruction of S3/S4 material. |
| `plugins/apodictic/skills/specialized-audits/references/craft/ai-prose-calibration.md` | Cross-reference paragraph: stance triage as the argument-domain sibling of Layer C source triage; domain boundary. |
| `plugins/apodictic/schemas/apodictic.finding.v1.schema.json` | Five **optional** properties, following the `salience` precedent: `register` (enum: `asserted`, `generative`), `stance` (enum: `S1`–`S5`), `stance_verdict` (enum: `earned`, `unearned`, `earned-by-frame`, `divergent`), `calibration_effect` (enum: `register-floor`, `stance-demotion`, `blocked-high-stakes`, `blocked-cash-out`), and `cash_out_ref` (`CO#`). Absent fields = pre-extension findings/no calibration effect. Precedence: high-stakes > cash-out > register > stance. |
| `plugins/apodictic/schemas/apodictic.argument_spine.v1.schema.json` | Extend `argument_type` enum with `AT5`; update the AT0–AT4 `$comment` mirror. |
| `plugins/apodictic/scripts/` (validate.sh + supporting script) | New `stance-calibration` check: (a) earned verdicts must actually demote unless blocked; (b) a calibration effect has its required register/stance/verdict fields; (c) supplied `cash_out_ref` values resolve and prescriptive joins force `blocked-cash-out`; (d) an active high-stakes gate blocks would-be demotions while retaining unearned/divergent stance records; (e) premise flags identified by the authoritative GT8 flag tokens or a `GT8` mechanism prefix cannot carry stance calibration; (f) enum membership. Shape checks only — it verifies recorded honesty, never verdict correctness, pre-commit severity history, or omitted joins. |
| `core-editor/references/nonfiction-intake-routing.md` | Fourth route (generative); default-activation row; register-confirmation + consequence-context-recording rule. |
| `core-editor/references/intake-router-runtime.md` | §6 Table A form row(s) for lens/exploratory essay. |
| `core-editor/references/argument-audits-routing.md` | `register` pass-through note; two-mechanism stakes-gate interaction (intake-declared document-wide; content-resolved per-span). |
| `core-editor/references/synthesis-argument.md` | Letter opening frame states applied register; mixed-register ledger note (carry-forward flagged). |
| `core-editor/references/run-synthesis.md` | §Step 5 Triage: register/stance calibration ordered before the Deficit Lock commit, mirroring the burden floor's position. |
| `docs/argument-state-schema.md` + Argument_State examples | `register` + confirmation and exact `High-stakes gate` fields in §1 (with AT5 row); consequence-context recording; exact `CO# | Location | Kind | Press | Consequence` cash-out inventory for generative runs. |
| `plugins/apodictic/skills/nonfiction-argument-engine/SKILL.md` | Run-shape field `register`; QA guardrails (register confirmation; consequence-context recording; stance-verdict Firewall line). |
| `evals/register-stance-pilot/` + fixture manifest | E1–E7 fixtures + expected profiles in canonical tokens; auditor prompt templates; groundtruth-harness wiring. |
| `changelog.d/` | Two entries (one per fix); minor version bump per plugin.json conventions. |

---

## Appendix A: Rao Ch. 7 Findings Re-Adjudicated

*(Severity labels below predate the review and use the pilot's 4-band scale; canonical remap: Consider/Observational → Could-Fix. Preserved as written for the historical record.)*

The probe's six findings under the new machinery (`register=generative`, stance triage on):

| Original finding | New adjudication |
|------------------|------------------|
| WR0 — biomechanical gait → life-posture analogy carries the conclusion | Observational (AT5 lens span, not a cash-out). Note names what a reader who rejects the analogy loses. |
| Definitional smuggling — "gait" migrates technical → metaphorical | Not flagged as CL4: migration is the method. Checked once at cash-out for concealment → clean (the landing doesn't spend the technical sense). |
| Anecdote-to-principle (FM-A17) — plantation ambling horses → mediocrity-as-endurance | S2 (mock-heroic, "the mediocrity revolution for horsekind"), earned-by-frame. Observational. |
| False precision (FM-A8) — uncited brain-stem / "muscle-maintenance circuits" | **GN4 candidate** — the one live finding. Is the neuroscience texture, or is it doing warrant work at the landing? Borderline; verdict to the writer. |
| Scope-dodge — "to some extent it doesn't matter" waves off philosophy of time | S2 marked deflation, earned (signaled, and the essay's economy doesn't need the question). Observational. |
| Hedged normative landing — "you should probably learn to amble" | Cash-out point, located and assessed at asserted burden. Light press (modal hedge, self-application framing) → light burden → passes, with a note that pressing harder would raise it. |

Net: six Must-Fix-adjacent findings become one genuine open question (GN4) plus a clean cash-out assessment — which matches a competent human editor's read of the chapter. That correspondence, not leniency, is the target.

*Pilot confirmation (A3): the blind machinery run reproduced this table nearly exactly — GN4 fired on the predicted span at Should-Fix, the mock-heroic and definitional-migration findings demoted as earned-by-frame, GN2 was assessed and correctly not fired (no motte-retreat move; defect routed to GN4), and the "you should amble" cash-out passed at light press. The run also surfaced a real finding this appendix missed: OB3, the essay's prescription presupposes gait is choosable while its own definition grants only "semi-controllable."*

---

## Appendix B: Pilot Runs (2026-07-15)

Seven blind Opus auditors across three waves; none saw this spec, the expected outcomes, or each other. Machinery-arm auditors received a blinded addendum (this spec's Parts 1–2 stripped of examples and expectations). Fixture texts, the addendum, and the run summary are vendored in `evals/register-stance-pilot/`; the full historical ledgers are not present in this checkout. *(All pilot severity labels use the run-harness-injected 4-band scale — see §Validation for the canonical remap. The addendum predates the review rework: it placed triage at Step 9 and used "Observational"; those two mechanics are superseded by this spec's Triage-time/Could-Fix design, which is behaviorally equivalent for everything the pilot measured — the pilot tested aim, refusal, gating, and halo, none of which depend on the lock position or the band name.)*

### Wave 1 — contrast pair (2×2)

| Run | Text | Rubric | MF/SF/C/O | Verdict |
|-----|------|--------|-----------|---------|
| A1 | Rao Ch. 7 | base | 0/4/7/5 | WARRANTED (unconventional-but-warranted) |
| A2 | Fixture op-ed | base | 0/14/2/1 | WARRANTED (evaluability) |
| A3 | Rao Ch. 7 | + machinery, register confirmed | 0/2/2/5 | Succeeds as AT5; GN4 + OB3 are the repair agenda |
| A4 | Fixture op-ed | + machinery, register *claimed* | 4/21/4/4 | UNWARRANTED; register rejected from structure |

1. **Separation widened in both directions.** The machinery softened-and-redirected on the good text and hardened on the bad text simultaneously. No threshold moved; the register and the cash-out inventory did all the work.
2. **The cash-out inventory is the load-bearing mechanism** — more than the GN codes or the stance taxonomy. Forcing per-landing assessment is what flipped the fixture from WARRANTED (A2, evaluability) to UNWARRANTED (A4, disowned causal bridge = unrecoverable defeat). The base audit *saw* every individual manipulation and still returned WARRANTED; the machinery's contribution was structural, not perceptual.
3. **Function-under-detection performed as designed at both poles**: demoted Rao's self-flagged play, returned unearned on every fixture move, including reading the fixture's "just a thought experiment" frame as an S2 costume over S1 assertion.
4. **The GN2/GN4 boundary is workable**: A3 assessed GN2 and declined to fire it (no motte-retreat), routing the defect to GN4; A4 fired GN2 on a true motte structure. Two blind auditors drew the same line this spec draws.
5. **Content-resolved consequence** was applied document-wide by A4 unprompted; the reworked Architecture Decision 4 deliberately narrows it to per-span (E7 tests the difference).
6. **Convergent bonus signal:** three of four runs independently surfaced self-undermining-remedy objections the original probe missed (A1: the amble is recommended on optimizing grounds; A3: gaits are only semi-controllable; A4: the ban is itself the uncontrolled experiment the piece condemns).

### Wave 2 — E4/E5

| Run | Text | Rubric | MF/SF/C/O | Verdict |
|-----|------|--------|-----------|---------|
| B4 | Testimony fixture | + machinery, register forced asserted, stakes gate ACTIVE | 0/2/2/2 | WARRANTED; flourish held with demotion blocked-and-recorded |
| B5 | Nietzsche, "Problem of Socrates" | + machinery, asserted, demotion available | 0/5/3/4 | WARRANTED as polemic; 4 earned demotions, 3 unearned refusals, no halo |

1. **The stakes gate is precise, not blunt** (B4): blocked exactly one demotion with the block recorded in the ledger, stayed moot for unearned findings, did not perturb the rest of the run.
2. **No halo effect** (B5): earned rhetoric did not launder sincere assertion — the physiology-of-decadence master warrant and the self-undermining structure (the chapter uses sustained dialectic to convict dialectic) held at Should-Fix.
3. **Function-under-detection discriminates *within* a single author's moves** (B5): "Socrates was mob" demotes; the dying-words reading does not. See the doctrinal finding in §Validation.
4. **Register discipline held under temptation** (B5): the auditor considered AT5 for a text that invites it and rejected it for want of a writer declaration.
5. **Test-divergence protocol exercised** (B5): one finding recorded tests diverging with an unearned-lean rather than manufactured confidence.
6. **Fixture-transcending findings, again** (B4): the aggregate-vs-subset composition gap in the cost-per-visit figure, unprompted.

### Wave 3 — E6

| Run | Text | Rubric | MF/SF/C/O | Verdict |
|-----|------|--------|-----------|---------|
| B6 | Motte-and-bailey fixture | + machinery, asserted, demotion available | 3/8/4/0 | UNWARRANTED (scope-honesty defeat); S3 rescue refused |

1. **DI4/FM-A13 fired at Must-Fix with the full structure named** — bailey as C0, retreats under pressure, silent re-expansion powering the moral conclusion.
2. **The S3 rescue was explicitly considered and refused with demotion available.** All three tests converged unearned; the construct's central failure mode (stance triage as a fallacy-laundering pathway) did not occur under deliberately tempting conditions.
3. **The specificity guard composed correctly with the machinery**: three Must-Fix codes recognized as one structural break refracted through three lenses; UNWARRANTED confirmed, not softened.
4. **Fixture-transcending finding** (six of seven runs): FM-A20 — the essay's prescription ("train the reflex to ask instead") presupposes exactly the self-directed agency the piece denies exists.

### Carry-forwards (pre-merge, tracked)

1. **E7 hybrid fixture strict rerun — PR merge blocker**: preliminary blind reads converge, but the rerun must use canonical `CO#` joins and warrant-verdict tokens and vendor a validator-passing ledger/state pair before this draft PR merges.
2. **Letter-synthesis clustering guidance** for mixed-register / high-count ledgers (A4 produced 33 findings; the Argument-DE letter needs cluster-first guidance).
3. **Abbreviated triage under an active document-wide gate**: both gated runs spent effort fully documenting verdicts that could not demote; the reference should permit a compact record form (stance + verdict + one-line rationale) when no demotion is possible.
