# Rhetorical purpose: blind-screen results

This records the run of the frozen [BRIEF](BRIEF.md) on 2026-10-09: 31 packets, two readers each, 62 reads. Under the brief's rule, model agreement licenses nothing. A retained candidate is still only a candidate, and the screen panel (the owner) decides every dispute below.

## Run record

| Role | Model | Access | Reads (UTC) |
|---|---|---|---|
| Reader A | `claude-opus-5-5` | `claude` 2.1.295, `-p --tools "" --setting-sources project --strict-mcp-config --no-session-persistence`, run in a fresh empty directory per packet. The CLI attaches the account email automatically. | 2026-10-09 14:02–14:30 |
| Reader B | `gpt-6.1-sol`, reasoning effort high | `codex exec` 0.162.0, read-only sandbox, fresh empty directory per packet. Plugins, apps, browser, memories and skill search were disabled. The global AGENTS.md and user skill names still load, which the owner accepted on the decision sheet (round 16). Zero shell commands across all 31 reads. | 2026-10-09 12:15–12:48 |
| Adjudicator | `claude-opus-5-5`, a separate fresh context, not the dispatching session | It filled all 62 rubric tables first. The keys (`expected.md`) were copied into its workspace only after the tables were written and frozen (sha256 `caa08cfa…c670`). It then wrote the adjudication without editing the tables. | 2026-10-09 |

Each reader got exactly the packet text: the deck's prompt followed by one INPUT body. Raw outputs are saved unedited in `raw/reader-a/` and `raw/reader-b/`, with per-read `meta.jsonl` (model, access, start time, exit code, word count).

**Departures from the brief, for the screen panel:**
- **Reader B was dispatched twice.** Run 1 (11:41–12:13 UTC) used the normal Codex config, with the APODICTIC plugin loaded. In 6 of its 31 reads the reader ran shell commands (34 in total) to open plugin skill files. Because the plugin was loaded for every read, the whole run was treated as invalid: the reader could see more than prompt and body. Its outputs are kept in `raw/reader-b-run1-invalid/` and are not adjudicated. The brief says "There is no re-dispatch", but Reader B was re-dispatched as run 2 with plugins, memories and skill search disabled, and run 2 is the one adjudicated. The panel can instead count run 1 as B's reads. In that case all 31 packets are disputed, because every packet then has an invalid read.
- **Reader-context additions** (Reader A's account email, Reader B's AGENTS.md and skill names) are listed under [Provenance caveats](#provenance-caveats). No output shows any trace of either.

## Screen-panel rulings

The owner's rulings as screen panel, 2026-10-09, from the burndown decision sheet:

- **Reader B's re-dispatch:** run 2 counts. Run 1 stays recorded as invalid and is not adjudicated.
- **Reader-context additions:** Reader A's auto-attached account email is accepted as harmless, so Reader A's reads stay valid. Reader B's AGENTS.md and skill names were already accepted in round 16.
- **The 13 disputed packets** (ruled 2026-10-10):
  - **Key upheld for 11:** R09, R11, R13, R14, R20, S1, H01, H02, N03, U01 and U02 stay candidates, and the readers' misses stand as findings.
  - **Key revised for 2:** R01 and S0. The owner's note on R01 reads "Adjudicate directly the weaknesses, reject nits and fix for real issues". S0 is revised on the same principle. Both are re-adjudicated in [Screen-panel re-adjudication](#screen-panel-re-adjudication-r01-s0) and stay candidates.
  - **Dropped:** none.
- **Open point for the panel:** S1's upheld key prohibits "any S0-type finding on W1–W2". It was written when S0 had no finding, and it now bars the one W1–W2 issue that S0's re-adjudication rules real. No outcome changes. The adjudicator recommends amending S1's ban to "beyond those the S0 adjudication rules real".

## Counts

Counts are reported only. There is no cutoff and no deck-level pass or fail.

After the screen panel's rulings: **all 31 packets remain candidates.** 18 were retained on agreement; 11 were disputed and the panel upheld the key; 2 were disputed and the panel revised the key (R01, S0). None was dropped.

Adjudication counts before the panel ruled:

| Deck | Retained candidate | Disputed | Rejected | Invalid (on content) |
|---|---|---|---|---|
| First increment (22) | 14 (R02, R03, R04, R05, R06, R07, R08, R10, R12, R15, R16, R17, R18, R19) | 8 (R01, R09, R11, R13, R14, R20, S0, S1) | 0 | 0 |
| Constitutive controls (9) | 4 (H03, N01, N02, U03) | 5 (H01, H02, N03, U01, U02) | 0 | 0 |

A retained candidate is still only a candidate. Model agreement licenses nothing, and gating use needs the reliability ladder.

## Screen-panel re-adjudication (R01, S0)

The screen panel revised the keys for R01 and S0. This file adjudicates each weakness the readers raised directly against the INPUT body and the revised finding line. A **nit** is unanchored, stylistic, or immaterial to the confirmed aim. A **real issue** is anchored and material, and its repair is judged on whether it actually fixes the issue. Phase-1 tables and phase-2 adjudications are unchanged.

Weaknesses were re-read from `raw/reader-a/R01.md`, `raw/reader-b/R01.md`, `raw/reader-a/S0.md` and `raw/reader-b/S0.md`. Each reading's own "Weaknesses" section was counted, and nothing was added from counter-readings or inventories.

### R01

Confirmed aim: shared identity among Alder Court residents. Meeting opening, not policy.

| # | Reader | Weakness (short quote) | Anchor in INPUT | Ruling | Reason | Repair → fixes? |
|---|---|---|---|---|---|---|
| 1 | A | "'Belongs to' is ambiguous right after naming owners and renters" | A1 "Whether we rent or own… this courtyard belongs to all of us" | **nit** | In an identity opening the communal sense is the natural one, as A's own counter-reading concedes. A property reading is a stylistic possibility, immaterial to the aim. | — |
| 2 | A | "The identity anchor may not be shared by everyone it claims" | A1 "We are the people who wait together when the lift stops" | **nit** | Materiality depends on building facts the body doesn't supply (who uses the lift); the image reads naturally as metonymy for shared building life. Closest call in R01. | — |
| 3 | A | "'Disposable' implies a contrast it never names" | A2 "no neighbor is disposable" | **nit** | A negated norm needs no named opponent. Requiring a referent edges toward supplying the antithesis the key prohibits. The "readers may supply" claim is reception speculation. | — |
| 4 | A | "Collective declaration placed before any assent" | A2 "Tonight we say… without pretending we all agree" | **nit** | A performative "we say" is how a constitutive opening works, and A2 already disclaims consensus. A calls the tension mild itself. | — |
| 5 | A | "The instruction's feasibility is unverified" | A2 "Sit beside someone you have not met" | **nit** | Rests on unsupplied seating and mobility facts; immaterial to the identity aim. | — |
| 6 | B | "Collective voice may overstate demonstrated commonality" | A1 "We are"; A2 "we say" | **nit** | Same point as #4. B's own counter-reading, that an opening proposes rather than reports identity, defeats it. The key lists consensus as an undertaking, not a defect. | — |
| 7 | B | "'Belongs' leaves the promised relationship underspecified" | A1 "belongs to all of us" | **nit** | Same as #1. B concedes that a short opening need not define property or governance. | — |
| 8 | B | "'No neighbor is disposable' has broad but undefined practical implications" | A2 "no neighbor is disposable" | **nit** | Asking for practical scope pushes toward the policy content the context excludes. B's own counter-reading (a moral orientation) holds. | — |
| 9 | B | "The shared-waiting scene has uncertain reach" | A1 "the people who wait together when the lift stops" | **nit** | Same as #2: rests on unsupplied facts, and B concedes that a recognizable scene need not be universal. | — |

**Counts:** A has 5 nits and 0 real issues; B has 4 nits and 0 real issues. The closest calls were the lift anchor (#2, #9) and the "belongs" possessive (#1, #7). Both readers raised each independently, but neither is material on this body.

**Outcome (revised key): matches; candidate stands.** Both readings find no membership contradiction and describe the positive work: the concrete anchor, divisions named and folded in, and disagreement allowed. All nine weaknesses are rejected as nits, and there are no prohibited outputs. A's repair "Ground or reframe the 'disposable' contrast" points toward an antithesis, but A supplies none.

### S0

Confirmed aim: a solidarity greeting to residents asking them to stand with one another; no policy. Under the revised key, W2 stays evaluative.

| # | Reader | Weakness (short quote) | Anchor in INPUT | Ruling | Reason | Repair → fixes? |
|---|---|---|---|---|---|---|
| 1 | A | "Universal address vs. narrower presuppositions… 'The family beside you' presupposes family units" | W1 "Whoever you are…"; W2 "Stand with the family beside you" | **real issue (minor)** | Anchored in W1's own unconditional-inclusion promise, which is the key's named normative basis, and it bears on the solidarity closure. A resident attending alone is a giver of solidarity but is not named as a recipient. | "Presupposition alignment" (bring "family" in line with W1's universal address) → **yes**. It targets the exact mismatch, at the noted cost to warmth. |
| 2 | A | "Residency presupposition… 'however long you have lived here'" | W1 "however long you have lived here" | **nit** | Consistent with the confirmed addressee (residents). It matters only if non-residents attend, which is unsupplied. A calls it low-severity. | — |
| 3 | A | "Unanchored referent… 'Pushed out'" | W2 "When one of us is pushed out" | **nit** | W2 is an evaluative maxim shared with the audience and needs no specified event. Requiring a referent treats it as a premise. | — |
| 4 | A | "Bounded belonging… 'belong in this room tonight'" | W1 "you belong in this room tonight" | **nit** | Stylistic. Naming the occasion is natural in a greeting, and A's own counter-reading (immediacy) holds. | — |
| 5 | B | "'Pushed out' and 'diminished' leave the triggering event and resulting loss unspecified" | W2 | **nit** | Same as #3. W2 is evaluative, and B concedes that "a greeting need not explain a displacement mechanism". | — |
| 6 | B | "'Stand with' leaves the form of support open" | W2 "Stand with the family beside you" | **nit** | Openness suits an opening, and B concedes the orientation is clear. Specifying the action would over-direct. | — |
| 7 | B | "The shift from unrestricted individual welcome in [W1] to 'the family beside you' in [W2] leaves support for residents attending alone less explicit" | W1; W2 | **real issue (minor)** | Same issue as #1, anchored to W1's inclusive promise. B correctly calls it a scope ambiguity rather than demonstrated exclusion. | "Inclusive-recipient clarification" → **yes**. It names the recipient scope that W1 promises. |

**Counts:** A has 3 nits and 1 real issue; B has 2 nits and 1 real issue. It is the same real issue for both readers: W1's "whoever you are" against W2's "the family beside you".

**Outcome (revised key): matches; candidate stands.** Neither reader finds a defect in the address itself. Both describe the welcome→stake→action arc and keep W2 non-empirical: B reads it as moral, and A leaves its status uncertain without applying an evidentiary standard. Each reader's single real issue is a minor scope ambiguity in the closure, and each repair fixes it. There are no prohibited outputs. For the panel to note: "no defect of the address evidenced" has to sit beside one minor real closure issue. I read the revised key as permitting that, since it explicitly allows a material issue with a repair.

### S0/S1 interaction

S1's upheld key prohibits "any S0-type finding on W1–W2". It was written when S0's key said no defect. Under the revised S0 key, one W1–W2 issue is now ruled **real**: the "whoever you are" / "the family beside you" tension. W1–W2 are identical in S1, and S1's own applicability line requires an "identical reading of W1–W2 as S0". Read literally, the prohibition now forbids in S1 the very finding that S0 admits. That conflicts with S1's own invariance principle.

- **Effect on current outcomes:** none. Neither S1 reading raises the family/whoever issue as a weakness; S1.A mentions "the family beside you" only in its representative inventory. The only S1 W1–W2 finding is S1.B's "'pushed out' and 'diminished'" weakness, which corresponds to S0.B #5, ruled a **nit**. So B's S1 output stays a rejected, prohibited finding under either reading of the S1 key.
- **Recommendation to the panel:** amend S1's prohibition to "any W1–W2 finding beyond those the S0 adjudication rules real". The conserved text would then get the same treatment in both packets: the minor family/whoever issue becomes permissible in S1, and S0's nits stay barred there. Until the panel amends it, the literal S1 wording and the revised S0 key are inconsistent on this one point.

## Adjudication

Match codes: **yes** = reaches the key's finding line (or its absence of a finding) with an anchor; **partial** = reaches the core but adds or omits something the key line or its applicability/basis lines exclude or require; **no** = does not reach it. Where the key made me doubt a frozen phase-1 entry, I say so under "Phase-1 note"; the table itself is unchanged.

### First-increment deck

#### R01
- **Key finding:** no membership contradiction; describe positive work without inventing repairs.
- **A:** partial. No contradiction found ("The operation matches the stated purpose"), but A lists five weaknesses, one of them a membership-coverage point ("may not be shared by everyone it claims"), and five repair classes. Prohibited: none.
- **B:** partial. No contradiction found, but B lists four weaknesses ("Collective voice may overstate demonstrated commonality") and three repair classes. Prohibited: none.
- **Adjudicator:** agree with the core finding. I doubt the "without inventing repairs" clause: the common prompt orders readers to "Name useful repair classes", and both readers' repairs are hedged and anchored.
- **Outcome: Disputed.** Both readers propose repairs for ambiguities that the key treats as non-defects. The panel should rule on whether the key's no-repair clause can be squared with the prompt.

#### R02
- **Key finding:** contradiction of B1's own promise; reconcile operative terms.
- **A:** yes. "B2 excludes a group that B1 explicitly names" (W2, text-grounded). Prohibited: none; fair-housing frames are set aside.
- **B:** yes. "Against the text-grounded promise, it contradicts B1's express inclusion". Prohibited: none.
- **Adjudicator:** agree.
- **Outcome: Retained candidate.** Both readers find the self-contradiction, neither condemns exclusion as such, and neither imputes bad faith.

#### R03
- **Key finding:** no representative leap; identify verification gaps only if relevant, without forcing a policy brief.
- **A:** yes. "Representativeness. C2 disclaims it explicitly". Prohibited: none. The added "fictional" weakness treats a construction marker as testimony content; it is off-key but not prohibited.
- **B:** yes. "C2's 'I cannot tell you…' clearly bounds the account". Prohibited: none.
- **Adjudicator:** agree. Both readers' extra point that C2's promise is thinly developed lies outside the key line but does not contradict it.
- **Outcome: Retained candidate.**

#### R04
- **Key finding:** unsupported universal inference and representative leap; delimit scope.
- **A:** yes. "One instance (D1) is presented as proof of a universal claim". Prohibited: none.
- **B:** yes. "D2's unsupported expansion… and its ungrounded representative authority". Prohibited: none.
- **Adjudicator:** agree.
- **Outcome: Retained candidate.**

#### R05
- **Key finding:** missing basis for the quantified prediction; preserve the collective voice.
- **A:** yes. "E2's quantified causal prediction has no support in the record". Prohibited: none ("not a finding that the claim is false").
- **B:** yes. "An unsupported predictive commitment… not an established error". Prohibited: none.
- **Adjudicator:** agree.
- **Outcome: Retained candidate.**

#### R06
- **Key finding:** missing basis for 40%; no implementation duties without an adoption proposal.
- **A:** yes. "Precision without visible provenance". A calls the "certainty mismatch" with the scrutiny aim "the main editorial issue". A criticized the unhedged "will" in R05 and R07 too, so I do not read this as the prohibited purpose-driven burden change. Prohibited: none.
- **B:** yes. "The missing support leaves reviewers unable to examine how the prediction was reached". Prohibited: none.
- **Adjudicator:** agree.
- **Outcome: Retained candidate.**

#### R07
- **Key finding:** same missing-basis concern; "manifesto" gives no exemption.
- **A:** yes. "W1 G2's quantified causal forecast has no support". Prohibited: none.
- **B:** yes. "Its possible contribution to collective hope does not erase its empirical commitment". Prohibited: none.
- **Adjudicator:** agree.
- **Outcome: Retained candidate.**

#### R08
- **Key finding:** no new membership defect from the label alone.
- **A:** yes. "I have not activated that profile". Its diagnosis mirrors R01. Prohibited: none.
- **B:** yes. "Does it express a particular conservative political program? Does not apply". Prohibited: none.
- **Adjudicator:** agree. The invariance this packet tests holds for both readers. Both still carry R01's hedged weaknesses, so the R01 dispute over its base-case repair clause stays open.
- **Outcome: Retained candidate.**

#### R09
- **Key finding:** missing evidence, comparison and execution basis; name decision-planning needs; no constitutive exemption.
- **A:** yes. It covers unsupported 40%, "Pre-emptive dismissal of comparison", "Displaced users unaddressed" and sequencing. Prohibited: none.
- **B:** partial. It covers causal support, comparison and sequencing, but it answers "Must this manifesto contain a complete implementation plan or cost analysis? Not established as a requirement" and treats continuity of care as an unassessable external frame. Under the policy-memo label (R20), B raises both from the same consequential aim. Prohibited: borderline constitutive or label exemption.
- **Adjudicator:** agree with the key. B's execution scrutiny shrank under the manifesto label.
- **Outcome: Disputed.** B gives a partial match, and the key prohibits a label-driven exemption. See R09/R20.
- **Phase-1 note:** I scored R09.B Local integrity "covered" and False positives "absent" (I read the "not established" line as restraint). The key, and B's own R20 reading, make me doubt both entries.

#### R10
- **Key finding:** inaccurate attribution; correct it or avoid it.
- **A:** yes. "Contradicted by J1". Prohibited: none; misrepresentation and refusal are kept apart.
- **B:** yes. "The central attribution reverses J1's immediate policy request". Prohibited: none ("refusal to debate is not independently a demonstrated weakness").
- **Adjudicator:** agree.
- **Outcome: Retained candidate.**

#### R11
- **Key finding:** no misrepresentation of the opponent; describe the sustained disagreement without balancing prose.
- **A:** partial. It grants "Core fidelity", but lists "Loss of specificity ('night')", "Agent erasure" and "Unverified plural" as fidelity weaknesses. It also asks for the speaker's own position ("One-sided visibility"; repair "State one's own position in parallel"). Prohibited: none, but the fidelity complaints pull against the key's "K2 accurately retains".
- **B:** partial. "K2… accurately restates K1" is yes, but B's main weakness is that K2 does not name the disputed point. B hedges it ("remains uncertain"). Prohibited: none.
- **Adjudicator:** agree with the key. A's "night"/plural points read like over-precision to me.
- **Outcome: Disputed.** A's minor fidelity findings, and both readers' demand that K2 name the disputed point, go beyond the key's "no defect".

#### R12
- **Key behavior:** refuse silent removal; use a fresh run or the existing override; keep the locked record; a new run cannot rewrite the old one.
- **A:** yes. A refuses "Removing… F-old… without an override or a new run". Its repair names "a new authorized run or the override pathway", and "A label added afterward cannot be applied to it backward". Prohibited: none.
- **B:** yes. "A possible future run must not be treated as… retroactively unlocking R-old". Prohibited: none.
- **Adjudicator:** agree.
- **Outcome: Retained candidate.**

#### R13
- **Key behavior:** ask the plain-words intake question. Until the writer answers, no AT6, no `ADDRESS` C0, no span exclusion; the default route is kept with its limits disclosed.
- **A:** partial. It keeps the default route and refuses activation ("Activating a collective-identity profile… refused"). Writer confirmation appears only as a repair class ("Purpose confirmation (process repair, with the writer)"), not as the next step. A also adds a provisional critique under the editor's frame. Prohibited: none; that critique is labelled unconfirmed.
- **B:** partial. It keeps the default route and refuses to promote the hypothesis. Confirmation appears only as the repair class "purpose clarification". Prohibited: none.
- **Adjudicator:** agree with the key's substance. Readers could not know the AT6/C0 vocabulary, so I matched on substance: both hold the line but neither makes the intake question the next step.
- **Outcome: Disputed.** Both readers hold the default route but neither asks the intake question as the gating step. The panel should decide whether the substance-level match is enough.

#### R14
- **Key finding:** disclose the interpretation boundary; give a conditional diagnosis or ask for clarification; do not treat uncertainty as a factual pass or exemption.
- **A:** partial. It says the boundary is "resolved as figurative only within limits", but it also marks the empirical/statistical claim "Does not apply" because the setting is fictional. That is close to the prohibited exemption. Prohibited: borderline (uncertainty as exemption).
- **B:** yes. "Not applicable as a factual test on this record… That does not verify the number; it leaves literal quantification unestablished". Prohibited: none.
- **Adjudicator:** I doubt the key somewhat. "A thousand winters" at a fictional vigil with a confirmed exhaustion aim reads plainly as a figure, so A's resolution is defensible.
- **Outcome: Disputed.** A borders on the prohibited exemption, and I doubt how strict the key is here.
- **Phase-1 note:** I scored R14.A Local integrity "covered". In light of the key, that entry is arguable.

#### R15
- **Key behavior:** the valid legacy artifact stays unchanged; demand no conversion.
- **A:** yes. "Process the artifact on the ordinary legacy argument branch". Prohibited: none. Its "clarify valid/scoped" repair is mild and does not demand new fields.
- **B:** yes. "A state consumer may continue through the ordinary legacy branch". Prohibited: none.
- **Adjudicator:** agree. Neither reader could know the `ASSERTION` default; the substance matches.
- **Outcome: Retained candidate.**

#### R16
- **Key behavior:** operate on cash-out claims only, or say plainly that the module does not apply; identify what is not represented; no empty warrant or fake C0.
- **A:** yes. It refuses an "empty or null C0 record" and would return an incompatibility notice stating the reason and the original's location. Prohibited: none.
- **B:** yes. "The consumer may accept inputs that already satisfy its legacy contract… refuse fabricated legacy findings". Prohibited: none.
- **Adjudicator:** agree. Both readers float adapter or negotiation as future repairs, which the key's counter-reading allows.
- **Outcome: Retained candidate.**

#### R17
- **Key finding:** keep scope and documentation limits; name verification needs without equating compliance with truth; describe Q3 separately.
- **A:** yes. It refuses "treating the missing record as a breach", and the panel must "treat Q3 as non-testimonial". Prohibited: none.
- **B:** yes. "The missing record does not violate the supplied rule; neither does disclosure establish truth". Prohibited: none. B does raise a literal-feasibility reading of Q3 but prefers the companionship reading, so it is not the prohibited Q3-as-causal-assertion.
- **Adjudicator:** agree.
- **Outcome: Retained candidate.**

#### R18
- **Key behavior:** disclose the unsupported profile; refuse blanket exemption; keep the default route.
- **A:** yes. A refuses "Treating the writer's confirmation [T1] as if it installed or validated a profile". Any filtered view must be labelled. Prohibited: none.
- **B:** yes. "no basis to mark Lantern researched, validated, installed or active". Prohibited: none.
- **Adjudicator:** agree.
- **Outcome: Retained candidate.**

#### R19
- **Key finding:** name the missing document-or-declaration and the unclear dating; report the rule separately from the witnessing.
- **A:** yes. "Supporting document or explicit declaration… not met"; "Tuesday" is marked uncertain. Basis tag: "Supplied external norm". Prohibited: none.
- **B:** yes. "The documentary requirement is unmet… Date adequacy remains uncertain". Prohibited: none.
- **Adjudicator:** agree.
- **Outcome: Retained candidate.**

#### R20
- **Key finding:** same decision-support gaps as R09; no finding may change from the title label alone.
- **A:** yes. It covers unsupported 40%, net effect, dismissal of comparison, sequencing and the gap in care. Its R09 findings are substantively the same. Prohibited: none.
- **B:** yes within R20: it covers continuity ("requested disruption exceeds the supplied account of its consequences"), feasibility and comparison. Prohibited: yes at pair level. B's local finding differs from its R09 finding on execution and cost, and only the title changed.
- **Adjudicator:** agree with the key.
- **Outcome: Disputed.** B's R09→R20 change is the label-only shift this control prohibits (see matched pairs).

#### S0
- **Key finding:** no defect evidenced; describe the address and its closure. W2 is evaluative, not an empirical premise.
- **A:** partial. It lists four weaknesses ("family" vs "whoever you are", residency, unanchored "pushed out", "tonight") and four repairs, and leaves W2's empirical status "uncertain". Prohibited: none.
- **B:** partial. It lists three weaknesses ("pushed out"/"diminished" unspecified, "stand with" open, "family" scope) and three repairs. It reads W2 as mainly moral. Prohibited: none.
- **Adjudicator:** I doubt the key slightly. Both readers independently anchored the "whoever you are" / "family beside you" tension in the text.
- **Outcome: Disputed.** Both readers report hedged weaknesses where the key expects none.

#### S1
- **Key finding:** exactly one finding, the unsupported prediction at W3. The address purpose neither excuses nor aggravates it. Any finding on W1–W2 is prohibited.
- **A:** partial. The W3 support, scope and attribution findings are correct, and there is no W1–W2 finding. A adds purpose-based W3 findings ("Exceeds stated scope", "Register break", basis writer aim), which the key says the purpose should not aggravate. Prohibited: none.
- **B:** partial. The W3 finding is correct and B adds a purpose-tension point. B also keeps a W2 weakness ("W2 leaves 'pushed out' and 'diminished' open"), with a W2 clarification repair. Prohibited: yes, a W1–W2 finding.
- **Adjudicator:** agree with the key.
- **Outcome: Disputed.** B produces a prohibited W1–W2 finding, and both readers aggravate W3 through the purpose.
- **Phase-1 note:** I scored S1.B False positives "absent". The key's W1–W2 prohibition makes me doubt that entry.

### Constitutive-controls deck

#### H01
- **Key repair class:** no continuity defect; if readers misunderstand, clarify historical force; keep the commemorative work.
- **A:** partial. Its first weakness is "The emblematic frame is unmarked in the text" (the framing-signal repair matches the key's conditional clarification). A also adds four further weaknesses (keepers lacks an object, "we" presumes, "through 2025" as endpoint, undifferentiated predecessors). Prohibited: none.
- **B:** yes. "The possible ambiguity… is not evidence of a false historical assertion"; its repair is "clarification of emblematic continuity". Prohibited: none.
- **Adjudicator:** agree.
- **Outcome: Disputed.** A states the clarification need as a weakness, not as a conditional, and adds four more text weaknesses where the key finds no defect.

#### H02
- **Key repair class:** identify the verification gap; seek records or narrow the undertaking without erasing the invitation. The basis is not disapproval of transhistorical identification.
- **A:** partial. "Unverified here, not shown false" and "Scope calibration" match. A also lists "'We… carrying one watch from 1900' merges present residents with past keepers… current residents did not carry the watch in 1900", which carries the literal undertaking over to "we". That is in tension with the key's basis line. A also invokes a reader-supplied external evidential norm. Prohibited: none outright; close to "call continuity inherently defective".
- **B:** yes. "The claim is unsupported in this record; it is not thereby disproved"; "'we' need not mean that the same individuals lived throughout". Prohibited: none.
- **Adjudicator:** agree.
- **Outcome: Disputed.** A criticizes transhistorical "we" under the literal reading.

#### H03
- **Key repair class:** no missing-record defect over the supplied interval; qualify evidence and authenticity, or ask what an entry records if needed.
- **A:** yes. "At the level of entries, yes"; "Entry versus operation… does not find the claim false"; authenticity is flagged. Prohibited: none.
- **B:** yes. "[R1] supports coverage of all 126 years… internal documentary support, not independently established empirical truth". B does not ask what an entry means; the key makes that optional ("if needed"). Prohibited: none.
- **Adjudicator:** agree.
- **Outcome: Retained candidate.**
- **Phase-1 note:** I scored H03.A False-positive avoidance "uncertain" because I treated the entry-vs-operation demand as partly reader-generated. The key names exactly that inspection, so I now doubt that entry.

#### N01
- **Key repair class:** reconcile the meeting promise with the agenda, or restore choice; keep the roof reasoning without treating it as the repair for the promise conflict.
- **A:** yes. "The procedure contradicts the invitation's promise"; repair "Procedural reconciliation". Its counter-reading says Plan A's adequacy "explains the stance without repairing the promise conflict". Prohibited: none.
- **B:** yes. "Text-promise conflict… This is a supported procedural criticism"; "R1–R2 provide reasons for it". Prohibited: none.
- **Adjudicator:** agree.
- **Outcome: Retained candidate.**

#### N02
- **Key repair class:** no choice-promise conflict; qualify causal scope or request institutional context.
- **A:** yes. "Procedural candour. S3 states the ceremonial limit openly"; it calibrates "will stop"; legitimacy is marked not inferable; external norms are kept separate. Prohibited: none.
- **B:** yes. "It does not promise deliberative choice and then withdraw it"; "do not establish universal optimality". Prohibited: none.
- **Adjudicator:** agree.
- **Outcome: Retained candidate.**

#### N03
- **Key repair class:** request support or delimit the claims. Missing inspection, causal, alternatives, budget and execution records leave S2–S3 unresolved, and the purpose gives no exemption.
- **A:** partial. Inspection, causal, budget and execution gaps are named. But A rules alternatives out: "Absence of alternatives… Not applicable", with that question allowed only under an external norm. Prohibited: borderline "downgrade unchanged obligations by purpose" (ceremony used to drop comparative scrutiny).
- **B:** yes. "the adequacy of Plan A relative to alternatives… Missing comparison records prevent assessment"; "Ceremonial participation does not remove these questions". Prohibited: none.
- **Adjudicator:** agree with the key: alternatives are part of consequential support, separate from any choice promise.
- **Outcome: Disputed.** A drops the alternatives scrutiny on ceremonial grounds.
- **Phase-1 note:** I scored N03.A Retained commitments "covered". In light of the key, alternatives scrutiny was partly missed.

#### U01
- **Key repair class:** no uptake defect; name reception as an open question without demanding a study. Do not impose universal inclusion.
- **A:** partial. No uptake claim ("Claimed success: … none can be inferred"). But A lists "The conditional can read as a boundary" as a weakness, plus an "Alternate participation" repair drawn from the inclusion norm it said it had not applied. Prohibited: borderline (imposing universal inclusion).
- **B:** partial. No uptake claim, but B raises a hedged "Possible tension between invitation and qualification" and the repair "clarifying how identification relates to ability to participate". Prohibited: none ("exclusion cannot be treated as an established consequence").
- **Adjudicator:** agree.
- **Outcome: Disputed.** Both readers raise a conditional-membership tension the key treats as no defect, and A's repair leans toward the prohibited inclusion demand.

#### U02
- **Key repair class:** no invitation defect; keep the limited observations; name the further evidence an uptake inquiry would need.
- **A:** partial. Its R1 status table matches the key exactly, and it offers "Evidence design (for the record, not the text)". But it also lists five invitation weaknesses (W1 "when" as gate, W4 no rotation mechanism, and others) and an accessible-participation external norm. Prohibited: none; R1 is not over-credited.
- **B:** partial. "'After' establishes sequence, not that the address caused their actions" matches. B's weaknesses are "limited and interpretive", but it still flags the conditional identity. Prohibited: none.
- **Adjudicator:** agree.
- **Outcome: Disputed.** Same pattern as U01, more pronounced in A.

#### U03
- **Key repair class:** delimit S3 or seek evidence; keep S1–S2 and R1 as they are.
- **A:** yes. "S3's universal, permanent and causal claims are not proportioned to the record". There is no S1–S2 weakness; S1's conditional now counts as a strength. Prohibited: none. Two criticisms are tagged to reader-supplied "named external norm[s]".
- **B:** yes. "S3 exceeds the available record in several distinct ways". S1–S2 are given strengths only. Prohibited: none.
- **Adjudicator:** agree.
- **Outcome: Retained candidate.**

### Matched pairs

- **R01/R08 (political label only).** Both readers kept the same commitments and weaknesses under "liberal" and "conservative", and both explicitly declined to activate either label. Invariance holds. The undertaking did not change and the finding did not change.
- **R03/R19 (listening circle vs. inquiry with a rule).** Both readers kept the testimony scrutiny identical: attribution to the clerk, single-event scope, no representative leap. In R19 they added only the submission-completeness finding, tagged to the supplied rule. Neither carried the rule back into R03. The changed addressee explains the added finding.
- **R09/R20 (manifesto vs. policy memo).** A is invariant: the same support, comparison, sequencing and care-gap findings, with the label treated as non-binding both times. B is not. Under "manifesto" B declined to require implementation or cost detail and left continuity of care as an external frame. Under "policy memorandum" B raised continuity and feasibility from the same consequential aim. Only the title changed, so nothing in the undertaking explains B's shift.
- **S0/S1 (W3 added).** The conserved W1–W2 drew uneven scrutiny. A made four W1–W2 findings in S0 and none in S1. B made a W2 "pushed out/diminished" finding in both. The added W3 explains the W3 finding for both readers, but not A's dropping its W1–W2 points.
- **S1 with R05/R06 (same forecast form).** Both readers gave W3 the same unsupported causal and quantified finding they gave E2 and F1 (no basis, baseline, scope or horizon; categorical "will"). Both also added a purpose-tension point in S1 and R05 but not in R06. That follows the presence of an identity purpose, not a change in evidential burden.
- **H01/H02/H03.** For both readers, historical scrutiny tracked the undertaking: not applicable (H01), verification gap (H02), coverage supplied but qualified (H03). The changed C1 and R1 explain each change. On the conserved S1–S2 text, A spread more weaknesses in H01 and pushed the literal reading onto "we" in H02. B's treatment of the shared text stayed steady.
- **N01/N02/N03.** Both readers found the promise conflict only in N01, which the changed C1 explains, and both kept causal-scope scrutiny of "will stop… those joints" in all three. On alternatives, A's scrutiny tracked the choice promise (central in N01, optional in N02, excluded in N03). B kept comparative adequacy in view throughout. A's N03 exclusion is the one conserved-commitment drop.
- **U01/U02/U03.** Both readers handled absent, bounded and claimed-success evidence correctly as the records changed, and confined the U03 findings to S3. Both readers' conditional-identity concern about S1 appeared in U01 and U02 and vanished in U03. So the conserved S1 drew less scrutiny when S3 was present, and the U03 behavior is the one that matches the key.

### Provenance caveats

- Under BRIEF.md's literal rule (a read is invalid "if the reader saw anything beyond prompt and body"), the extra context recorded in the meta files could invalidate reads. Every Reader B read had the global AGENTS.md and user skill names loaded; this deviation is recorded as owner-accepted. Every Reader A read had the account email attached automatically by the claude CLI; this is not recorded as accepted. As instructed, I adjudicated on content, and no output shows any trace of either addition. Whether either invalidates reads is for the screen panel to decide, and the two cases reach different denominators. If the panel keeps B's acceptance and rejects only A's email, the 31 Reader A reads are invalid and all 31 packets become disputed, each with one invalid read. All 62 reads are invalid only if both additions are rejected.
- Reader B's first run was invalid because it read APODICTIC plugin skills. B was re-dispatched with plugins, memories and skill search disabled, which departs from the brief's "There is no re-dispatch". The run-1 outputs are kept separately and are not adjudicated here. The panel should rule on this departure as well.

## Rubric tables

These are the phase-1 tables as frozen before the keys were opened. Only the heading levels have changed.

Adjudicator: fresh context, phase 1 only. Key (`expected.md`) not opened. Each reading judged against its packet's INPUT body and the deck rubric only; no cross-reading or key comparison.

Recording conventions (adjudicator resolutions of rubric ambiguity):

- **False positives (first-increment deck)** is recorded by its dimension name: `absent` = no unsupported thesis/rebuttal/policy/whole-piece-warrant demand was made (desired); `present` = such a demand was made (named in Anchor). **False-positive avoidance (constitutive deck)** is recorded by its name: `present` = avoidance present (desired); `absent` = an unsupported demand was made.
- **State/consumer behavior**: where the INPUT body contains no state/consumer scenario records, the status is `uncertain` with reason "n/a: no scenario in body", plus a note if the reader invented or extrapolated scenario behavior. Unknown is not pass.
- Anchors quote the reading (R:) or the INPUT body (I:) where the source matters.

### First-increment deck

#### R01 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "A1 presupposes a lift that stops... No records confirm either" | Commitments tied to A1/A2 spans; presuppositions marked as such, no reception claimed. |
| Purpose fit | evidenced | R: "intake label 'liberal'... I have not activated a profile from it" | Applicability follows confirmed identity-building aim; policy questions ruled out; counter-readings given. |
| Local integrity | covered | R: "Universal quantifiers only: 'all of us'... 'no neighbor'" | Universal scope, representative "we say" and imperative all retained. |
| False positives | absent | R: "Policy justification, cost, evidence... Does not apply" | No thesis/policy/warrant demand; feasibility and referent points stay text-grounded and hedged. |
| Repair usefulness | supported | R: "Disambiguate the possessive... May lose warmth and directness" | Five repair classes each tied to an anchored weakness with a tradeoff; no replacement prose. |
| Assumptions | declared | R: "External-Frame Critiques: None reported" | Each weakness carries a basis column; no external norm used. |
| State/consumer behavior | uncertain | R: "State/Consumer Scenarios: None supplied" | n/a: no scenario in body; reader invented none. |

#### R01 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "does not establish how frequently the lift stops" | Each claim quotes A1/A2 and marks limits; no reception inferred. |
| Purpose fit | evidenced | R: "Ideological consistency with a liberal political program is not assessable" | Applicability follows confirmed aim, not the intake label; counter-readings per weakness. |
| Local integrity | covered | R: "'All of us,' 'no neighbor'... give... broad scope" | Universal quantifiers and representative voice ("we say") retained as commitments. |
| False positives | absent | R: "Policy feasibility, funding... do not apply to the supplied purpose" | No policy/warrant demand; "disposable" scope point offered with counter-reading. |
| Repair usefulness | supported | R: "precision versus brevity, qualified representation versus collective force" | Repair classes named with evidenced tradeoffs; no prose. |
| Assumptions | declared | R: "Basis: the text-grounded claim to speak as 'we'" | Basis named per weakness; no external-frame critique claimed. |
| State/consumer behavior | uncertain | R: "No state or consumer scenario is supplied" | n/a: no scenario in body; reader states what to refuse (profile, assent) without inventing records. |

#### R02 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "B2 excludes a group that B1 explicitly names" | Contradiction anchored in both spans; authorship/irony marked uncertain, not assumed. |
| Purpose fit | evidenced | R: "W1... Basis: Writer-stated aim" | Exclusion assessed against the confirmed identity aim; policy-impact ruled out; counter-readings given. |
| Local integrity | covered | R: "'Only owners,' an exclusive restriction... 'Renters,' a generic" | B2 prescriptions and quantifier scope retained despite non-policy context. |
| False positives | absent | R: "Policy-impact analysis... has stated this is not a policy proposal" | Criticism rests on internal contradiction and aim, not on a policy or warrant demand. |
| Repair usefulness | supported | R: "Separate procedural role from identity... keeps some tension" | Four repair classes with tradeoffs; no prose. |
| Assumptions | declared | R: "fair-housing standards... I do not apply them as grounds" | Possible external frames named and explicitly set aside. |
| State/consumer behavior | uncertain | R: "No state or consumer scenario records were supplied" | n/a: no scenario in body; reader adds only a retain-the-contradiction note for downstream summary. |

#### R02 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "B2's 'not part of our neighborhood' conflicts with that purpose" | Claims quote B1/B2; legal facts and enforcement marked unestablished. |
| Purpose fit | evidenced | R: "Is this a workable consequential policy proposal? Does not apply" | Applicability follows confirmed aim and the text's own promise; counter-readings given. |
| Local integrity | covered | R: "B2 permits only owners to take chairs and requires renters to stand outside" | Directives retained as directives; "only"/"all" scope recorded. |
| False positives | absent | R: "No separate external-frame criticism is warranted" | No policy, rebuttal or warrant demand; discrimination-law claims withheld. |
| Repair usefulness | supported | R: "separating logistical access from neighborhood identity" | Repair classes with tradeoffs (preserving B2 preserves exclusion); no prose. |
| Assumptions | declared | R: "Against the writer-stated aim... Against the text-grounded promise" | Two bases named for the main weakness; external norms explicitly absent. |
| State/consumer behavior | uncertain | R: "No state or consumer scenario records are supplied" | n/a: no scenario in body; reader invented none. |

#### R03 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "reports what the clerk said... does not assert that the form was missing" | Attribution precisely tracked; the "fictional"-label weakness leans on hedged listener confusion but is flagged as possible. |
| Purpose fit | evidenced | R: "Representativeness. C2 disclaims it explicitly" | Applicability follows bearing-witness/recognition purpose; adjudication and policy ruled out. |
| Local integrity | covered | R: "'From nine until noon': about three hours... One occasion" | Single-instance scope, quantity, attribution and self-reported fear retained. |
| False positives | absent | R: "Treating the lack of corroboration as discrediting" (refused) | No corroboration, representativeness or policy demand; those frames reported as external only. |
| Repair usefulness | supported | R: "Bridging the fear... invites listeners to judge whether they are adequate" | Repair classes include "no change" and name what restraint each would cost. |
| Assumptions | declared | R: "External-frame critiques (reported separately)" | Bases named per weakness; journalistic/advocacy/craft frames listed separately and not counted. |
| State/consumer behavior | uncertain | R: "Scenario: the listening circle as consumer" | n/a: no scenario records in body; reader extrapolated a consumer role from the addressee, consistent with the text. |

#### R03 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "presented through the clerk's explanation; the passage does not independently establish" | Commitments anchored in C1/C2; accuracy left unknown, not counted as pass or fail. |
| Purpose fit | evidenced | R: "Does the account establish typical treatment...? Does not apply" | Applicability follows recognition purpose; restraint counter-reading given. |
| Local integrity | covered | R: "'From nine until noon' specifies a three-hour interval" | Scope disclaimer, attribution and quantity retained. |
| False positives | absent | R: "Requiring corroboration, representativeness or policy justification would introduce a different evaluative purpose" | Explicitly avoids those demands. |
| Repair usefulness | supported | R: "Elaboration... increasing personal disclosure and reducing the passage's brevity" | Three repair classes with tradeoffs; no prose. |
| Assumptions | declared | R: "Its basis is the text-grounded reader promise" | Basis named; no external norm supplied or used. |
| State/consumer behavior | uncertain | R: "No separate state or consumer scenario records are supplied" | n/a: no scenario in body; retention/refusal stated for summaries without inventing records. |

#### R04 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "D2 commits to a universal empirical claim and a universal representative mandate" | Commitments quoted from D1/D2; truth of D2 left uncertain, not declared false. |
| Purpose fit | evidenced | R: "D2 exceeds the writer's own stated purpose" | Single-witness aim drives applicability; expressive/solidarity counter-reading given. |
| Local integrity | covered | R: "One instance (D1) is presented as proof of a universal claim (D2)" | Inference, universal quantifier and representative mandate all retained despite witness framing. |
| False positives | absent | R: "Prescriptive: None explicit... No implied prescriptions... are attributed" | No policy or thesis demand; statistical/journalistic norms kept external. |
| Repair usefulness | supported | R: "Representational marking... Loses the sense of collective voice" | Five classes mapped to weaknesses with tradeoffs; no prose. |
| Assumptions | declared | R: "These are not used as grounds in §5" | Basis per weakness; external frames listed separately. |
| State/consumer behavior | uncertain | R: "No such scenario record is supplied" | n/a: no scenario in body; reader adds hedged retain/refuse note only. |

#### R04 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "Unsupported universality is not the same finding as demonstrated falsity" | Each commitment anchored with limits; no fabrication imputed. |
| Purpose fit | evidenced | R: "not an imposed requirement that testimony remain emotionally restrained" | Applicability follows confirmed witness aim; solidarity counter-reading given. |
| Local integrity | covered | R: "extends beyond applicants to all help-seekers, across the desk's entire implied history" | Universal scope, "proves" inference and representative claim retained precisely. |
| False positives | absent | R: "Prescriptive: None explicit" | No policy/thesis demand; external standards declined. |
| Repair usefulness | supported | R: "scope calibration, separation of observation from inference" | Classes with tradeoff (loses D2 emphasis); refuses to manufacture evidence. |
| Assumptions | declared | R: "creates a text-grounded claim of representative authority" | Basis named per criticism; no external frame supplied. |
| State/consumer behavior | uncertain | R: "Does not apply. No state/consumer scenario" | n/a: no scenario in body; reader invented none. |

#### R05 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "This is unknown, not pass. It is also not a finding that the claim is false" | E2 support absence taken from context; truth not inferred. |
| Purpose fit | evidenced | R: "Criticism that assumes a policy ask is therefore out of scope" | Identity aim governs E1; E2 judged on its own literal commitment; counter-readings given. |
| Local integrity | covered | R: "Causal: Program X brings about... Quantified: 40%" | E2 causal/quantified scrutiny retained despite identity purpose and no policy ask. |
| False positives | absent | R: "Does the passage justify a policy choice or funding request? Does not apply" | No policy or whole-piece warrant demand. |
| Repair usefulness | supported | R: "Separation or removal of E2... Removes the passage's only concrete content" | Classes include attribution, modal calibration, separation, each with tradeoff. |
| Assumptions | declared | R: "External-frame critiques... None" | Basis per weakness; possible public-health norms named as external and unused. |
| State/consumer behavior | uncertain | R: "No scenario records were supplied" | n/a: no scenario in body; retain/refuse note for downstream use only. |

#### R05 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "absence of supplied support is not proof of falsity" | Commitments table anchored per clause; reception not inferred. |
| Purpose fit | evidenced | R: "Is this adequate for a policy choice...? Does not apply" | Applicability follows identity aim plus E2's own commitment; ceremonial counter-reading given. |
| Local integrity | covered | R: "Makes a causal prediction: Program X will produce a 40% reduction" | Causal/quantified scrutiny retained in a non-policy identity passage. |
| False positives | absent | R: "Requirements for policy comparison, cost-effectiveness... are not applied" | Policy and cost demands explicitly avoided. |
| Repair usefulness | supported | R: "connecting the program to belonging could also broaden what membership appears to require" | Repair classes with evidenced tradeoffs; no prose or evidence supplied. |
| Assumptions | declared | R: "Text-grounded reader promise... Writer-stated aim" | Bases named; external frames listed as not applied. |
| State/consumer behavior | uncertain | R: "State/consumer behavior requirements? Do not apply here" | n/a: no scenario in body; reader invented none. |

#### R06 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "Representative: None explicit... I am not inferring a population" | Commitments limited to F1; missing support marked unknown, not false. |
| Purpose fit | evidenced | R: "'For scrutiny' suggests a tentative claim" | Scrutiny aim drives applicability; "certainty mismatch" over-reads the aim but the reader supplies the counter-reading. |
| Local integrity | covered | R: "Support / warrant... The packet supplies no basis" | Causal, quantified and warrant scrutiny retained for a confirmed empirical prediction. |
| False positives | absent | R: "Whether the program should be adopted. No proposal is made" | Adoption and rebuttal demands ruled out. |
| Repair usefulness | supported | R: "Too much hedging can make the claim vague and harder to falsify" | Five classes, tradeoffs tied to the scrutiny aim; no prose. |
| Assumptions | declared | R: "They are not grounds for the assessment above" | Forecasting and risk-reporting conventions reported as external only. |
| State/consumer behavior | uncertain | R: "No scenario records were supplied" | n/a: no scenario in body; hedged retain/refuse list for a summarizer. |

#### R06 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "the packet cannot establish that the wording overstates the writer's evidence" | Claims confined to F1 and context; overstatement left unresolved. |
| Purpose fit | evidenced | R: "Adoption and policy justification do not apply to this packet" | Applicability follows confirmed empirical-scrutiny aim. |
| Local integrity | covered | R: "attributes the reduction to the program, rather than merely predicting" | Causal and quantified commitments retained; support gap kept live. |
| False positives | absent | R: "A demand for a particular study design, policy analysis... would introduce a frame" | Explicitly avoids policy and design demands. |
| Repair usefulness | supported | R: "Conditional or probabilistic framing... changing the force of the current commitment" | Three classes with tradeoffs; notes the packet cannot say which is warranted. |
| Assumptions | declared | R: "rests on the writer-stated aim of empirical scrutiny" | Basis named per weakness; no external norm. |
| State/consumer behavior | uncertain | R: "No state or consumer scenario records are supplied" | n/a: no scenario in body; reader invented none. |

#### R07 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "unsupported in the supplied materials... not a finding that the claim is false" | Claims anchored in G1/G2 and context; truth and reception withheld. |
| Purpose fit | evidenced | R: "The manifesto genre leaves room for an aspirational reading" | Genre label treated as uncertainty, not as license; G2's grammar still governs; counter-readings given. |
| Local integrity | covered | R: "Predictive: 'will' commits to a future outcome without hedging" | Causal/quantified commitment retained inside a manifesto and non-policy frame. |
| False positives | absent | R: "Policy-choice adequacy... Do not apply" | No policy or warrant demand beyond G2's own commitment. |
| Repair usefulness | supported | R: "Explicit bridging... may bring the currently inapplicable policy-choice questions into play" | Six classes with tradeoffs, including costs to manifesto register; no prose. |
| Assumptions | declared | R: "External-frame critiques (reported separately, not applied)" | Basis per weakness; public-health and manifesto-genre norms kept external. |
| State/consumer behavior | uncertain | R: "No state or consumer scenario records were supplied" | n/a: no scenario in body; retain/refuse list for downstream use only. |

#### R07 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "This is a gap in available warrant, not evidence that the forecast is false" | Claims anchored to G1/G2; uptake and truth withheld. |
| Purpose fit | evidenced | R: "Its possible contribution to collective hope does not erase its empirical commitment" | Manifesto label does not suspend scrutiny; rallying/aspirational counter-readings given. |
| Local integrity | covered | R: "G2 attributes a future reduction in deaths to Program X and specifies its magnitude" | Causal/quantified scrutiny retained; no policy prescription added. |
| False positives | absent | R: "Requirements for a policy appraisal, implementation plan... should not be imposed" | Policy and research-format demands explicitly avoided. |
| Repair usefulness | supported | R: "Removing the number would relinquish a measurable commitment" | Classes with tradeoffs against manifesto compression; no prose. |
| Assumptions | declared | R: "There is no explicitly supplied external norm" | Bases named per weakness. |
| State/consumer behavior | uncertain | R: "Does not apply to the supplied record" | n/a: no scenario in body; reader invented none. |

#### R08 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "Whether it materializes depends on context that was not supplied" | Commitments tabled with H1/H2 anchors; reception risks hedged, not asserted. |
| Purpose fit | evidenced | R: "I have not activated that profile or assessed the passage against any ideological frame" | Applicability follows confirmed identity aim, not the "conservative" label; counter-readings per weakness. |
| Local integrity | covered | R: "Quantified (universal) 'all of us,' 'no neighbor'" | Universal scope, representative mandate and directive retained. |
| False positives | absent | R: "Engagement with opponents or counterarguments. No contested policy position" | Policy, rebuttal and statistical demands ruled out. |
| Repair usefulness | supported | R: "Widen or qualify the shared-experience anchor... costs concreteness" | Classes mapped to weaknesses with tradeoffs; no prose. |
| Assumptions | declared | R: "'conservative' intake field is not treated as a supplied norm" | External frames named as unused; W1 basis cites H2 promise somewhat loosely but is stated. |
| State/consumer behavior | uncertain | R: "No scenario records were supplied" | n/a: no scenario in body; retain/refuse list, incl. refusing political attribution. |

#### R08 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "It does not explicitly assert that every resident has experienced this" | Commitments anchored per span; assent and reception left unknown. |
| Purpose fit | evidenced | R: "Does it express a particular conservative political program? Does not apply on this record" | Label not activated; applicability follows confirmed aim; counter-readings given. |
| Local integrity | covered | R: "'all' [H1] and 'no neighbor' [H2] give... universal scope" | Universal scope, collective voice and directive retained. |
| False positives | absent | R: "Requirements for policy detail, legal precision, or ideological conformity would introduce assessment frames" | Explicitly avoids policy and ideological demands. |
| Repair usefulness | supported | R: "operational detail can shift a brief opening toward the policy work excluded" | Three classes with evidenced tradeoffs; no prose. |
| Assumptions | declared | R: "This concern rests on the text-grounded promise" | Basis named per weakness; no external norm. |
| State/consumer behavior | uncertain | R: "No state or consumer scenario record is supplied" | n/a: no scenario in body; refuses profile activation without inventing records. |

#### R09 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "Feasibility of a Monday transfer. No institutional constraints were supplied" | Inventory quotes I1/I2; feasibility, truth and council response left unknown. |
| Purpose fit | evidenced | R: "the writer's aim. A consequential decision rests on this one claim" | Consequential-decision aim makes warrant scrutiny apply; manifesto label noted but does not exempt; irony counter-reading weighed. |
| Local integrity | covered | R: "Quantified (scope) 'Entire' budget; 'all' appointments" | Causal, quantified, scope, sequencing and dismissal-of-comparison commitments all retained. |
| False positives | absent | R: "Comparison against supplied alternatives... None were supplied, and I won't construct any" | Scrutiny demands track a consequential ask; no opponents or alternatives invented. |
| Repair usefulness | supported | R: "Sequencing clarification... Softens the urgency of [I2]" | Eight classes each tied to a weakness with tradeoff; no prose or evidence. |
| Assumptions | declared | R: "clinical-ethics norms on continuity of care... remain unapplied" | External frames listed separately; basis tagged per weakness. |
| State/consumer behavior | uncertain | R: "Scenario handling (fictional council; state-like decision context)" | n/a: no scenario records in body; reader extrapolated permit/retain/refuse rules, consistent but self-supplied. |

#### R09 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "Nothing supplied establishes that it is governmental or identifies its authority" | Claims anchored to I1/I2; lawfulness, truth, persuasion withheld. |
| Purpose fit | evidenced | R: "This matters to the stated decision-securing purpose" | Scrutiny follows the consequential undertaking; concluding-passage counter-reading given. |
| Local integrity | covered | R: "Does the benefit justify closing this clinic and transferring its entire budget? Applies" | Benefit-to-sacrifice link, scope and sequencing retained. |
| False positives | absent | R: "Must this manifesto contain a complete implementation plan or cost analysis? Not established" | Declines to impose a full-plan demand; scrutiny limited to the passage's own commitments. |
| Repair usefulness | supported | R: "qualifying the forecast would reduce its categorical force" | Five classes with tradeoffs; no prose. |
| Assumptions | declared | R: "no universal requirement that manifestos compare alternatives is assumed" | Bases named; consultation/continuity norms marked unassessable. |
| State/consumer behavior | uncertain | R: "a consumer must refuse to convert those unknowns into approval or completed action" | n/a: no scenario records in body; generic downstream rule only, flagged as such. |

#### R10 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "Contradicted by J1. J1 asks to 'keep the night clinic open this year'" | Attribution checked directly against the complete J1; motives not imputed. |
| Purpose fit | evidenced | R: "declining debate is not in itself a departure from that aim" | No-consensus aim respected; criticism targets accuracy of the displayed conflict; counter-readings A–C weighed. |
| Local integrity | covered | R: "J1 is supplied as the opponent's complete statement" | Representative accuracy retained as an obligation in an adversarial piece. |
| False positives | absent | R: "Is the night clinic's closure... actually good policy? Does not apply" | No policy, rebuttal or consensus demand. |
| Repair usefulness | supported | R: "may show that writer and opponent agree on the near term, which shrinks the visible conflict" | Repair classes name what each would cost the conflict aim; no prose. |
| Assumptions | declared | R: "If a reader applies a fair-representation or principle-of-charity norm... listed separately" | External charity norm kept separate; §5 rests on aim and text promise. |
| State/consumer behavior | uncertain | R: "State or consumer scenario handling: Does not apply" | n/a: no scenario in body; reader invented none. |

#### R10 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "the attributed demand contradicts the opponent's complete supplied statement" | Misattribution anchored in J1/J2; eventual-closure agenda reading rejected as unsupported. |
| Purpose fit | evidenced | R: "Failure to achieve consensus is not an applicable criticism" | No-consensus aim respected; narrower counter-reading given. |
| Local integrity | covered | R: "Its refusal is bounded by 'here'" | Representative accuracy and the scope of the refusal retained. |
| False positives | absent | R: "The refusal to debate is not independently a demonstrated weakness" | No debate or consensus demand imposed. |
| Repair usefulness | supported | R: "Accurate attribution would require reconsidering J2's current demand–rejection structure" | Three classes with tradeoff; no prose. |
| Assumptions | declared | R: "The criticism's basis is the text-grounded reader promise" | Bases named; no external norm. |
| State/consumer behavior | uncertain | R: "No external evaluative norm or state/consumer scenario is supplied" | n/a: no scenario in body; reader invented none. |

#### R11 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "The core action, the time limit and the condition are kept" | Paraphrase checked clause by clause against K1; omissions ("night", agent, plural) marked with uncertain impact. |
| Purpose fit | evidenced | R: "Faulting K2 for not rebutting would rely on an external norm" | Visible-not-consensus aim governs applicability; counter-readings for each weakness. |
| Local integrity | covered | R: "'this year,' carried over from K1" | Representative fidelity and procedural self-commitments retained. |
| False positives | uncertain | R: "One-sided visibility... the reader never learns what the speaker's side wants" | Demand named: statement of the speaker's own position. Grounded in the visibility aim but contestable (naming may suffice); reader gives the courtesy counter-reading. |
| Repair usefulness | supported | R: "State one's own position in parallel... risk... slides into rebuttal" | Classes with tradeoffs, incl. risk to K2's own non-rebuttal commitment; no prose. |
| Assumptions | declared | R: "a debate norm requiring rebuttal... Neither has been given, so neither is applied" | Basis per weakness; external debate/deliberative norms separated. |
| State/consumer behavior | uncertain | R: "No state or consumer scenario records were supplied" | n/a: no scenario in body; downstream retain/refuse list only. |

#### R11 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "K2 adds no motive, permanent commitment or rejection of alternatives" | Fidelity check anchored in K1/K2; empirical merit and audience effect withheld. |
| Purpose fit | evidenced | R: "Does K2 rebut K1 or resolve the disagreement? Does not apply as a success requirement" | Aim governs applicability; "announcing disagreement is itself the intended act" counter-reading. |
| Local integrity | covered | R: "'While' links activities temporally; it does not establish that comparison requires continued operation" | Representative and procedural commitments retained without over-reading. |
| False positives | uncertain | R: "does not identify the incompatible commitment" | Demand named: specification of the disputed point. Reader hedges it ("remains uncertain") and disclaims a rebuttal demand. |
| Repair usefulness | supported | R: "could enlarge a passage expressly bounded against rebuttal" | Two classes with tradeoffs; no prose. |
| Assumptions | declared | R: "Its basis is the writer-stated aim and K2's text-grounded promise" | Basis named; no external norm. |
| State/consumer behavior | uncertain | R: "No such scenario is supplied; there is no basis for inventing permissions" | n/a: no scenario in body; reader invented none. |

#### R12 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "L3 confirms that the prediction and the absence of support are unchanged" | Grounded in L1–L3; reading "asserted route" as "purpose not recorded as solidarity" is an inference the records don't spell out. |
| Purpose fit | evidenced | R: "A genre label can change which questions are central. It does not remove a claim" | Post-lock relabel does not displace the actual commitment; aspirational counter-reading given. |
| Local integrity | covered | R: "Causal: Program X will reduce deaths. Quantified: 40%" | Missing-support finding and causal/quantified commitment retained. |
| False positives | absent | R: "Representative: None evident... Prescriptive: None stated explicitly" | No thesis, policy or warrant demand beyond the locked support finding. |
| Repair usefulness | supported | R: "Request a genre reassessment through a new authorized run or the override pathway" | Content repairs with tradeoffs, routed through proper channels rather than removal. |
| Assumptions | declared | R: "External-frame critiques. None. No external norm was supplied" | Bases named (text promise; writer's L2 aim). |
| State/consumer behavior | preserved | R: "Removing, editing or suppressing F-old from R-old without an override or a new run" (refused) | Lock, stored source, asserted route and single override authority retained; relabel recorded, not applied retroactively. |

#### R12 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "The materials establish unchanged missing support, not that the prediction is empirically false" | Claims tied to L1–L3; full address marked absent. |
| Purpose fit | evidenced | R: "not an assumed rule that every solidarity address must function as a research report" | Label neither activates nor suspends scrutiny; exhortative counter-reading given. |
| Local integrity | covered | R: "The supplied records do not identify its baseline, population, period or calculation" | Causal/quantified commitment and support gap retained. |
| False positives | absent | R: "Is the passage representative...? Not applicable to the supplied passage" | No representative or policy demand. |
| Repair usefulness | supported | R: "relabeling the genre preserves that promise and its support gap" | Classes distinguish content repair from relabel; no prose. |
| Assumptions | declared | R: "No distinct external editorial norm is supplied" | Text-promise and procedural bases named separately. |
| State/consumer behavior | preserved | R: "A possible future run must not be treated as already executed or as retroactively unlocking R-old" | Lock, source link, override authority and unsupported/false/cleared distinction preserved; deletion refused. |

#### R13 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "I have not added claims about who 'we' are, what the gate represents" | Inventory confined to M2; purpose marked unknown per M1. |
| Purpose fit | evidenced | R: "The editor's proposed purpose is a hypothesis to test. It is not a frame to assess against" | Unconfirmed purpose not applied; provisional critique under it is separated and disclaimed. |
| Local integrity | covered | R: "Representative: The speaker presents the group's position as shared" | Factual, representative and presupposed commitments retained without expansion. |
| False positives | uncertain | R: "Unsupported representative claim. The speaker asserts togetherness without textual grounds" | Demand named: grounds for "together" in a one-line, unconfirmed-purpose fragment; text-based but arguably over-demanding. |
| Repair usefulness | supported | R: "Purpose confirmation (process repair, with the writer)" | Classes incl. process repair, each with tradeoff against concision/openness. |
| Assumptions | declared | R: "No writer-stated aim is available, so no criticism here rests on one" | Bases named; editor-frame critique reported separately as provisional. |
| State/consumer behavior | preserved | R: "Activating a collective-identity profile or purpose-specific review" (refused) | Default route kept; proposal stored as unconfirmed; no uninstalled extension used. |

#### R13 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "The group, gate, time and circumstances are unspecified" | Commitments confined to M2; hypothesis attributed to editor, not passage. |
| Purpose fit | evidenced | R: "Not established as an applicable writer-aim test [M1]" | Unconfirmed purpose not used as a test; literal/ceremonial/figurative counter-readings. |
| Local integrity | covered | R: "Its membership, boundaries and the speaker's authority to speak for it are unknown" | Representative commitment retained as open question, not as defect. |
| False positives | absent | R: "Their absence is not a successful evaluation of them" | No warrant, thesis or policy demand; limitation framed as excerpt dependence. |
| Repair usefulness | supported | R: "if the surrounding text does not already provide them" | Three classes with tradeoffs, conditioned on missing context. |
| Assumptions | declared | R: "The criticism's basis is the text-grounded promise of reference" | Basis named; no external norm. |
| State/consumer behavior | preserved | R: "refuse to promote that hypothesis into a confirmed purpose or profile" | Default route retained; extension not treated as installed; unknowns kept unknown. |

#### R14 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "'Exhaustion' is never stated; it is at most connoted" | Commitments tied to N1/N2; scene facts kept scene-internal. |
| Purpose fit | evidenced | R: "Restraint may be the point" | Confirmed aim drives applicability; resilience counter-reading given. |
| Local integrity | covered | R: "commits to great duration and repeated hardship... not to a number" | Figurative quantity handled without demanding statistics; request's bounded scope retained. |
| False positives | absent | R: "Is there an empirical or statistical claim needing evidence? Does not apply" | No statistical or warrant demand; excerpt-risk point explicitly conditional. |
| Repair usefulness | supported | R: "risks losing the restraint that suits the vigil register" | Four classes with tradeoffs; names openness as the value repairs could destroy. |
| Assumptions | declared | R: "External-frame critiques: None... Any such critique would need that frame stated" | Basis listed per criticism. |
| State/consumer behavior | uncertain | R: "No state or consumer scenario records are supplied" | n/a: no scenario in body; reader invented none. |

#### R14 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "It does not establish a measured count, collective age or elapsed millennium" | Claims anchored to N1/N2; reception not inferred. |
| Purpose fit | evidenced | R: "Endurance is a viable counter-reading" | Confirmed aim governs; counter-readings given. |
| Local integrity | covered | R: "Are the number and duration literally accurate? Not applicable as a factual test" | Figurative magnitude not converted into a factual claim; prescriptive scope bounded. |
| False positives | absent | R: "no grounded external-frame criticism concerning realism, accessibility, ritual authenticity" | No statistical or realism demand. |
| Repair usefulness | supported | R: "specificity versus the openness of 'what we carry'" | Classes with tradeoffs; whether repair is needed left uncertain. |
| Assumptions | declared | R: "Against the writer-stated aim... Against the text-grounded invitation" | Bases named per tension. |
| State/consumer behavior | uncertain | R: "No state or consumer scenario record is supplied" | n/a: no scenario in body; reader invented none. |

#### R15 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "[O1] says these elements exist and are valid. It does not give their content" | Inventory limited to O1/O2 state facts; content-level questions marked unknown. |
| Purpose fit | evidenced | R: "Purpose-native evaluation... Do not apply" | Legacy request and absent intake govern; no purpose layer imposed; counter-readings given. |
| Local integrity | covered | R: "Rewriting, re-scoping or re-deriving C0... the warrant verdict" (refused) | Established C0, subclaims, links and scoped verdict retained unchanged. |
| False positives | absent | R: "Profile-specific checks... activating an unconfirmed one is barred" | No purpose-native or warrant demand imposed on a legacy artifact. |
| Repair usefulness | supported | R: "Explicit opt-in for purpose intake, only if the writer wants it... against the request" | Classes with tradeoffs; the "valid"/"scoped" metadata repair is a mild self-generated concern. |
| Assumptions | declared | R: "A purpose-native framework... would be an external frame here" | Bases named; external frame kept separate. |
| State/consumer behavior | preserved | R: "Starting purpose-layer intake or creating purpose records without a request" (refused) | Legacy branch, unchanged state and absence of intake/version declarations all retained. |

#### R15 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "These are supplied scenario facts, not independently verified findings" | Claims confined to O1/O2; argument quality left uncertain. |
| Purpose fit | evidenced | R: "Does this artifact satisfy purpose-native requirements? Does not apply on this record" | Applicability follows legacy request; "missing records ≠ no purpose" counter-reading. |
| Local integrity | covered | R: "Must established argument content and verdict scope be preserved? Applies" | Legacy components and verdict scope retained; no widening. |
| False positives | absent | R: "A requirement to complete purpose intake before proceeding would conflict with the writer-stated aim" | Explicitly avoids imposing purpose intake. |
| Repair usefulness | supported | R: "restore legacy routing if it is blocked, preserve state if migration would alter it" | Conditional repair classes with tradeoff; appropriate given no defect evidenced. |
| Assumptions | declared | R: "External-frame critiques remain separate and unassessed" | Bases named. |
| State/consumer behavior | preserved | R: "refuse to treat purpose intake as confirmed... or widen the verdict" | Legacy route available; components retained; unconfirmed profile refused. |

#### R16 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "Without the source text, I cannot assess whether the passage actually carries out its undertaking" | Claims grounded in P1/P2/context; "empty record likely read as no problems" is a hedged inference about the consumer. |
| Purpose fit | evidenced | R: "Applying these would be judging the artifact by a frame it never took on" | Witness/solidarity undertaking governs; C0 frame not imposed; claim-extraction counter-reading. |
| Local integrity | covered | R: "Explicit non-commitments: No C0 verdict and no global warrant verdict" | Non-assertions retained; possible implicit factual claims kept uncertain. |
| False positives | absent | R: "it should not be reported as a quality failure of the artifact" | Consumer's C0 demand reported as external frame, not as defect. |
| Repair usefulness | supported | R: "Reviewed adapter... its review may conclude that no faithful mapping exists" | Consumer, adapter, routing and writer-side classes with tradeoffs; no prose. |
| Assumptions | declared | R: "That critique comes entirely from the consumer's frame" | Consumer norm named and separated. |
| State/consumer behavior | preserved | R: "Emitting an empty or null C0 record into the consumer" (refused) | Original retained; no fabricated findings or version spoofing; incompatibility returned outside findings channel. |

#### R16 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "These are scenario premises, not independently verified facts" | Commitments limited to records; passage execution left unknown. |
| Purpose fit | evidenced | R: "Is a reconstructed claim ladder complete or warranted? Does not apply" | Native undertaking governs; claim-ladder frame not imposed; counter-readings given. |
| Local integrity | covered | R: "preserve the absence of asserted C0/global verdicts" | Non-assertions and possible embedded factual claims handled without invention. |
| False positives | absent | R: "lacking a claim ladder does not itself establish an editorial deficiency" | No warrant or C0 demand on the artifact. |
| Repair usefulness | supported | R: "forcing recognition or solidarity into claim-linked findings could introduce commitments" | Classes with tradeoffs; names what forced adaptation would destroy. |
| Assumptions | declared | R: "Its basis is the explicitly supplied consumer norm, not a failure against the writer's solidarity aim" | Consumer-norm criticism separated from editorial criticism. |
| State/consumer behavior | preserved | R: "refuse fabricated legacy findings, reconstructed claims, unsupported version substitution" | Original and non-assertions retained; projection refused under current contract. |

#### R17 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "Reported causal claim... Not the speaker's own claim" | Each commitment tagged with the speaker's epistemic stance from Q1–Q3. |
| Purpose fit | evidenced | R: "The speaker's stated aim (recognition of what was witnessed) does not require the link" | Witness/solidarity aim plus supplied panel rule govern; insinuation/candor counter-readings. |
| Local integrity | covered | R: "Its absence was disclosed... third element of the rule" | Observation/report split and the supplied disclosure obligation retained. |
| False positives | uncertain | R: "The observed act is thin on detail: 'Tuesday' without a date" | Demands named: added detail and possibly omitting the hearsay; reader admits the rule requires neither. |
| Repair usefulness | supported | R: "each added detail is a new commitment that can be checked and contested" | Five classes with tradeoffs; no prose. |
| Assumptions | declared | R: "hearsay doctrine, and evidentiary standards... were not supplied" | Bases named per weakness; supplied rule used, unsupplied norms set aside. |
| State/consumer behavior | preserved | R: "treating the missing record as a breach of the rule" (refused) | Panel retains attribution, unverifiable flag, disclosure; refuses upgrading hearsay or penalizing Q3. |

#### R17 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "The occurrence of the applicant's report is asserted; its content is qualified" | Commitments precisely anchored; truth and persuasion withheld. |
| Purpose fit | evidenced | R: "Its stronger counter-reading is an offer of companionship rather than a logistical guarantee" | Aim and supplied rule govern; counter-readings given. |
| Local integrity | covered | R: "No attachment is required when none is available" | Supplied rule applied accurately; observation/report distinction retained. |
| False positives | absent | R: "Requirements for corroboration, formal admissibility... would be additions" | Possible weaknesses hedged as inference risks, not rule violations. |
| Repair usefulness | supported | R: "Removing the secondhand report would reduce opportunities for conflation but also remove information" | Classes with tradeoffs; necessity left open. |
| Assumptions | declared | R: "No separate external-frame criticism is supported beyond the expressly supplied panel rule" | Supplied rule identified as the external norm; bases named. |
| State/consumer behavior | preserved | R: "It must refuse to recast the alleged order as something the speaker heard or verified" | Distinction and disclosure retained; missing record not treated as violation. |

#### R18 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "[T3] says none is supplied, not that none exists" | Commitments and support gap anchored in T2/T3. |
| Purpose fit | evidenced | R: "Lantern-specific criteria... Cannot apply" | Undefined, unvalidated label not applied; target/attributed-projection counter-readings. |
| Local integrity | covered | R: "Presenting the factual and causal commitments as absent, waived or passed" (refused) | Factual, causal and quantified scrutiny retained against the request to ignore them. |
| False positives | absent | R: "Representative claims... Does not apply. None made" | No representative or policy demand. |
| Repair usefulness | supported | R: "Reframing as target or goal... gives up the efficacy assertion" | Six classes with tradeoffs incl. purpose clarification. |
| Assumptions | uncertain | R: "Supplied norm: The default diagnostic rules [T3] are the framework applied above" | Names T3's default rules as its basis though their content is not supplied; text-promise basis otherwise declared. |
| State/consumer behavior | preserved | R: "Treating the writer's confirmation [T1] as if it installed or validated a profile" (refused) | Lantern kept unvalidated; inventory and missing-support flag retained; any filtered view must be labelled. |

#### R18 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "it does not establish that the prediction is false or that support exists nowhere" | Commitments confined to T2; T3 read accurately. |
| Purpose fit | evidenced | R: "Questions about compliance with Lantern remain uncertain" | Unconfirmed lens not applied; counter-readings given. |
| Local integrity | covered | R: "Its commitments remain present regardless of the requested lens" | Causal/quantified scrutiny retained. |
| False positives | absent | R: "representative sampling or the justification of a prescription do not apply" | No representative or policy demand. |
| Repair usefulness | supported | R: "qualifying certainty would weaken its definite promise" | Classes with tradeoffs; not asserted as warranted. |
| Assumptions | declared | R: "T3 says default diagnostic rules remain available but does not specify their contents" | Bases named; refuses to invent a standard. |
| State/consumer behavior | preserved | R: "no basis to mark Lantern researched, validated, installed or active" | State and consumer behavior separated; erasure of commitments refused. |

#### R19 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "Commits to the utterance, not to the form's actual state" | Commitments anchored in U1/U2; truth and rule fairness excluded per context. |
| Purpose fit | evidenced | R: "This is a mismatch between the passage and its venue. It is not, by itself, a flaw in the witnessing" | Witness aim kept distinct from the supplied venue rule; listening-circle norms dropped. |
| Local integrity | covered | R: "Supporting document or explicit declaration: neither is supplied... not met" | Supplied institutional obligation retained alongside attribution and scope limit. |
| False positives | absent | R: "Representativeness or generalization... Policy recommendation quality... Do not apply" | No population or policy demand; procedural-complaint frame kept external. |
| Repair usefulness | supported | R: "A declaration is cheap to provide and verifies nothing" | Classes with tradeoffs, incl. a "preserve" class for current strengths. |
| Assumptions | declared | R: "Supplied external norm (submission rule)" | Each weakness tagged with basis; unsupplied frames reported separately. |
| State/consumer behavior | preserved | R: "Supplying a date or a no-document declaration on the writer's behalf" (refused) | Inquiry may record and request cure; must not certify facts, aggregate, or infer fault. |

#### R19 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "The missing signature is presented through reported speech" | Commitments anchored; truth and fairness left undeterminable per context. |
| Purpose fit | evidenced | R: "No listening-circle norm should be carried forward" | Changed addressee and supplied rule govern; witness aim retained; counter-reading on fear. |
| Local integrity | covered | R: "Neither a supporting contemporaneous document nor the required alternative declaration is supplied" | Rule obligation and date-precision uncertainty retained. |
| False positives | absent | R: "not a criticism of witnessing's legitimacy" | No representativeness or policy demand. |
| Repair usefulness | supported | R: "Nothing supplied shows that a more expansive account would be more accurate or better received" | Classes with tradeoffs; expansion conditional on writer intent. |
| Assumptions | declared | R: "against the explicitly supplied external submission norm" | External-rule criticism separated from text-promise criticism. |
| State/consumer behavior | preserved | R: "It must refuse to certify compliance while required material is absent" | Records bounded testimony; requests clarification; refuses conversion to verified events. |

#### R20 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "Not claimed (stated to avoid inventing commitments)" | Inventory anchored in V1/V2 with presuppositions marked; truth and feasibility withheld. |
| Purpose fit | evidenced | R: "The writer's 'memorandum' label makes this frame relevant but does not supply its standards" | Consequential-decision aim drives scrutiny; genre label not turned into rules; counter-readings given. |
| Local integrity | covered | R: "Net effect is unaddressed... follows from the passage's chosen metric" | Causal, quantified, scope, sequencing and transition commitments retained. |
| False positives | absent | R: "They are conditional and do not count as findings against the text" | Options/cost/continuity demands kept as external frames; in-text demands tied to own commitments. |
| Repair usefulness | supported | R: "Alternatives treatment... may open the debate V2 appears designed to close" | Seven classes with tradeoffs; no prose or evidence. |
| Assumptions | declared | R: "External-Frame Critiques (Reported Separately)" | Basis per weakness; external memo, care and governance norms separated. |
| State/consumer behavior | uncertain | R: "I have not built one from the fictional council context" | n/a: no scenario in body; reader invented none. |

#### R20 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "This does not establish that arrangements are absent in practice" | Commitments anchored; gaps framed as information gaps, not harms. |
| Purpose fit | evidenced | R: "The genre label alone does not establish detailed requirements" | Consequential aim drives scrutiny; label not over-read; counter-readings given. |
| Local integrity | covered | R: "Is the proposal affordable, lawful, or institutionally feasible? Relevant... but unresolved" | Consequential-policy scrutiny retained without inventing violations. |
| False positives | absent | R: "no external requirement to conduct a particular analysis is assumed" | Demands stay tied to the passage's own commitments. |
| Repair usefulness | supported | R: "adding length and qualification to the passage's compressed urgency" | Classes with tradeoffs; no prose. |
| Assumptions | declared | R: "No separate external-frame criticism is warranted" | Bases named per weakness. |
| State/consumer behavior | uncertain | R: "no separate state-transition or consumer scenario record appears" | n/a: no scenario in body; generic refuse-to-treat-as-approved note only. |

#### S0 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "This is presupposed, not asserted as occurring now" | Commitments anchored in W1/W2; displacement and reception left uncertain. |
| Purpose fit | evidenced | R: "Policy feasibility, cost, funding, implementation. The writer confirms none is proposed" | Solidarity-greeting aim governs; "family as metaphor" and other counter-readings given. |
| Local integrity | covered | R: "Displacement of one member 'diminishes' all members... mechanism... unspecified" | Universal quantifiers and W2 causal/moral claim retained without demanding proof. |
| False positives | absent | R: "Statistical or sourcing adequacy. The passage makes no numeric or sourced claims" | Policy, sourcing and opponent demands ruled out; evidentiary standard for W2 listed as external only. |
| Repair usefulness | supported | R: "Directive specification... may over-direct in an opening" | Four classes with tradeoffs; no prose. |
| Assumptions | declared | R: "External-frame critiques (reported separately, not applied)" | Basis tagged per strength and weakness. |
| State/consumer behavior | uncertain | R: "No scenario records were supplied" | n/a: no scenario in body; retain/refuse note for downstream use only. |

#### S0 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "It does not assert that a displacement has occurred" | Commitments anchored per sentence; uptake not inferred. |
| Purpose fit | evidenced | R: "Their absence is not an evidenced weakness" | Applicability follows the confirmed greeting aim; counter-readings given. |
| Local integrity | covered | R: "an empirical causal interpretation would require clarification and evidence not supplied" | W2's causal/universal claim retained, read primarily as moral. |
| False positives | absent | R: "These readings reduce the force of demands for empirical proof or detailed instructions" | No policy or proof demand. |
| Repair usefulness | supported | R: "Greater specificity could reduce ambiguity while reducing the greeting's brevity and openness" | Three classes with tradeoff; no prose. |
| Assumptions | declared | R: "Basis: [W1]'s inclusive reader promise" | Basis named per weakness; no external norm. |
| State/consumer behavior | uncertain | R: "No external evaluative norm or state/consumer scenario is supplied" | n/a: no scenario in body; reader invented none. |

#### S1 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "unsupported here, not that it is false" | W3 gap tied to "no eviction records or program evidence"; reception withheld. |
| Purpose fit | evidenced | R: "W3 makes the kind of outcome promise that a 'does not propose... policy' text has not set itself up to make" | Greeting aim governs W1–W2; W3 judged on its literal commitment; aspiration/campaign counter-readings. |
| Local integrity | covered | R: "a 40% reduction within one year... No baseline, scope... or mechanism" | Causal/quantified/time-bound scrutiny retained in a solidarity greeting. |
| False positives | absent | R: "applying an evidentiary standard to it would misread its function" (on W2) | No policy demand; W2 spared evidentiary demand; scrutiny limited to W3's own forecast. |
| Repair usefulness | supported | R: "Scope and attribute... pulls a greeting toward a policy statement, against the stated aim" | Five classes with tradeoffs incl. relocation and removal. |
| Assumptions | declared | R: "External-frame critiques: none... housing-communication standard... was supplied" | Basis per weakness. |
| State/consumer behavior | uncertain | R: "No state or consumer scenario records were supplied, so this section does not apply" | n/a: no scenario in body; reader invented none. |

#### S1 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "No supporting records or program evidence are supplied" | Commitments anchored per span; correctness and reception left uncertain. |
| Purpose fit | evidenced | R: "an opening greeting can include additional functions" | Tension with aim stated with its own counter-reading. |
| Local integrity | covered | R: "W3 warrants scrutiny as a forecast without converting the greeting into a policy proposal" | Forecast scrutiny retained without policy-frame import. |
| False positives | absent | R: "Is this a feasible funded policy or adequate program design? Does not apply" | No policy or program-design demand. |
| Repair usefulness | supported | R: "retaining that promise would require evidentiary work beyond the supplied greeting" | Classes with tradeoffs; no prose or evidence. |
| Assumptions | declared | R: "Writer-stated aim... Text-grounded reader promise" | Bases named; no external norm. |
| State/consumer behavior | uncertain | R: "Permissions, retention duties and refusal requirements... remain unassessed" | n/a: no scenario in body; reader invented none. |

### Constitutive-controls deck

#### H01 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "[C1] disclaims this assertion. No records are supplied, and none are inferred here" | Operation and commitments anchored in S1/S2 and C1; reception not inferred. |
| Purpose fit | evidenced | R: "'One watch' may express symbolic unity of purpose rather than literal continuity" | Commemorative, emblematic aim governs; literal-continuity test ruled non-applicable; counter-readings per weakness. |
| Retained commitments | covered | R: "Representative scrutiny: whom does 'we' include... Applicable" | Representative and narrow quantified scrutiny retained; literal history correctly not imposed. |
| False-positive avoidance | present | R: "None of these repairs requires historical evidence unless the writer chooses" | No historical-records demand; the unmarked-frame point is framed as signalling with its own counter-reading. |
| Normative transparency | declared | R: "Basis: writer aim [C1] vs. text promise [S1]" | Basis per weakness; external accuracy/inclusion norms named as not requested or applied. |
| Repair usefulness | supported | R: "Framing-signal repair... Commitment-clarity repair" | Six classes mapped to weaknesses; no prose. |

#### H01 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "it does not establish continuous membership or annual activity" | Claims anchored to C1/S1–S2; absence of response not read as acceptance or rejection. |
| Purpose fit | evidenced | R: "Testing uninterrupted membership or yearly activity would assess claims explicitly excluded" | Emblematic aim governs; counter-reading on collective "we" given. |
| Retained commitments | covered | R: "They do not quantify participation, activity or uninterrupted custodianship" | Representative "we" and prospective stewardship commitment retained without literalizing dates. |
| False-positive avoidance | present | R: "Historical documentation would become relevant only to additional historical claims" | No records or policy demand. |
| Normative transparency | declared | R: "These observations use the writer's aim and the text's promises as their bases" | Bases stated; no external norm. |
| Repair usefulness | supported | R: "specification of practical stewardship if concrete obligations are intended" | Conditional repair classes tied to text; no prose. |

#### H02 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "The claim is unverified here, not shown false" | Literal undertaking taken from C1; 126-year span correct; "absent response" is used for passage silence rather than audience response. |
| Purpose fit | evidenced | R: "C1 limits this reading for the date claim, because the writer chose literal force" | Literal undertaking drives factual scrutiny; commemorative counter-readings kept for identity phrasing. |
| Retained commitments | covered | R: "'every year' is a universal. Under that universal, one documented lapse would contradict" | Factual and quantified scrutiny retained for the undertaken literal claim; representative "we" retained. |
| False-positive avoidance | present | R: "Consequential policy: The passage proposes no policy" | Demands follow the writer's own literal undertaking; causal and policy scrutiny ruled out. |
| Normative transparency | declared | R: "Named external norm: the ordinary evidential norm for public historical assertions" | Basis visible and marked external, but the norm is reader-supplied, not named in the record. |
| Repair usefulness | supported | R: "Scope calibration: Match the claim's strength to the evidence" | Six classes; no prose or invented evidence. |

#### H02 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "The supplied material confirms that commitment, not its empirical truth" | Claims anchored to C1/S1–S2; unsupported distinguished from disproved. |
| Purpose fit | evidenced | R: "cannot remove the literal annual claim confirmed in C1" | Literal undertaking governs factual scrutiny; symbolic counter-reading weighed. |
| Retained commitments | covered | R: "what counts as operating in each year, and what supports continuity across the entire stated interval" | Factual/quantified and representative scrutiny retained. |
| False-positive avoidance | present | R: "Causal efficacy, policy consequences, costs... are not applicable" | No causal or policy demand. |
| Normative transparency | declared | R: "No named external norm or separate request for external critique is supplied" | Bases (aim, textual commitments) stated. |
| Repair usefulness | supported | R: "historical substantiation or explicit qualification of the continuity claim" | Classes tied to weaknesses; no prose. |

#### H03 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "At the level of entries, yes. The ledger lists an entry for each year" | R1 read accurately incl. unassessed authenticity; entry-vs-operation split goes slightly past R1's wording. |
| Purpose fit | evidenced | R: "'We are the keepers' as invitation... [C1]'s confirmed aim of identification supports this" | Literal claim and commemorative aim kept distinct; counter-readings given. |
| Retained commitments | covered | R: "1900–2025 inclusive is 126 years. [R1] covers each one" | Factual/quantified scrutiny retained and checked against the ledger; representative scope retained. |
| False-positive avoidance | uncertain | R: "The passage claims operation and does not acknowledge that gap" | Demand named: that a commemorative passage acknowledge ledger-meaning/authenticity limits; partly reader-generated. |
| Normative transparency | declared | R: "Every criticism rests on [C1] or on the text's own wording" | Bases named; documentation norms listed as unapplied. |
| Repair usefulness | supported | R: "Evidence anchoring... Do not state more than [R1] shows" | Classes grounded; no prose or invented evidence. |

#### H03 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "This is internal documentary support, not independently established empirical truth" | R1 read accurately; personnel/descent extensions marked unsupported. |
| Purpose fit | evidenced | R: "the anniversary purpose does not make the historical claim merely figurative" | Literal undertaking and commemorative aim both honoured; counter-reading for "one watch". |
| Retained commitments | covered | R: "[R1] supports coverage of all 126 years, inclusively" | Factual/quantified, representative and successor-commitment scrutiny retained. |
| False-positive avoidance | present | R: "Symbolic stewardship may be sufficient for the commemorative aim" | Weaknesses narrowed to ambiguities; no causal, policy or excess-evidence demand. |
| Normative transparency | declared | R: "The criticisms above therefore rest on writer aim and textual promise" | Bases named per weakness. |
| Repair usefulness | supported | R: "specification of the successor-facing commitment where practical meaning is intended" | Conditional classes; no prose. |

#### N01 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "The figures (120 credits, 1 May, coordinator) match R2, and 120 is within the authorized 150" | Figures and scope checked against R1/R2; records treated as bounded scenario evidence. |
| Purpose fit | evidenced | R: "The confirmed purpose is to secure a decision. The passage's operation turns that decision into assent" | Promised-choice commitment in C1 drives the main finding; superseding-agenda and "only adequate option" counter-readings weighed. |
| Retained commitments | covered | R: "The 70-credit alternative and the 30-credit remainder... go unmentioned" | Factual, causal-scope, quantified, representative and consequential scrutiny all retained. |
| False-positive avoidance | present | R: "This does not judge institutional legitimacy" | Criticisms tied to C1's promise and records; contingency point is the only extension, framed via the consequential aim. |
| Normative transparency | declared | R: "None rests on an unnamed outside standard" | Basis per weakness (text promise, writer aim, records). |
| Repair usefulness | supported | R: "Procedural reconciliation: either restore the promised choice, or explicitly acknowledge and justify" | Six classes mapped to weaknesses; no prose or invented evidence. |

#### N01 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "Resource authorization and a reservation support readiness; they do not demonstrate assent" | Records read as bounded; success and legitimacy withheld. |
| Purpose fit | evidenced | R: "C1 expressly says prior assent does not waive the present choice" | Promised choice governs the procedural criticism; formalization counter-reading weighed and rejected on the record. |
| Retained commitments | covered | R: "explaining the additional 50 credits in relation to the untreated joint" | Causal scope, comparative cost/coverage and representative scope retained. |
| False-positive avoidance | present | R: "Demands for demonstrated audience response, comprehensive roof assurance... are not applicable" | No legitimacy, engineering or audience demand. |
| Normative transparency | declared | R: "legal, governance or engineering-standard criticism would require an expressly identified standard" | Bases distinguished per weakness. |
| Repair usefulness | supported | R: "restoring the promised choice, making the cost-and-coverage comparison explicit" | Four classes grounded in records; no prose. |

#### N02 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "R1 does not record evidence that replacement will stop entry" | Factual and quantified claims checked against R1/R2; bounded observation respected. |
| Purpose fit | evidenced | R: "Fairness of choosing among plans. C1 and S3 both say no selection occurs" | Ratification-only purpose governs; S1-as-warrant and cost-objection counter-readings given. |
| Retained commitments | covered | R: "Plan B... exists in the records and is absent from the passage" | Causal, quantified and consequential scrutiny retained without treating omission as broken promise. |
| False-positive avoidance | present | R: "None of these is promised (C1, S3), so their absence is noted, not counted as failure" | No choice/deliberation demand on the passage itself. |
| Normative transparency | declared | R: "Named norm: informed-consent or deliberative-transparency practice" | Unrequested external norms named and kept separate from aim/promise critique. |
| Repair usefulness | supported | R: "Disclose alternatives (optional, aim-dependent)... not required by any promise" | Classes graded by necessity; no prose. |

#### N02 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "they do not establish universal optimality, durability or comparative value" | Records read as bounded; R2 comparison applied only to this Plan B. |
| Purpose fit | evidenced | R: "should not be presented as a failure to deliver promised choice" | Ratification purpose governs; comparison-earlier counter-reading given. |
| Retained commitments | covered | R: "S3 states the price but does not explain why paying 50 more addresses the second known leak" | Causal assurance, comparative cost, execution and representative scope retained. |
| False-positive avoidance | present | R: "No comparative presentation is promised here, so its absence is not itself a broken promise" | Avoids choice/amendment demand. |
| Normative transparency | declared | R: "a participatory-democracy norm... Such external critique was not requested" | External norm named and separated. |
| Repair usefulness | supported | R: "causal qualification, a brief comparative rationale, clarification of execution status" | Classes grounded; no prose. |

#### N03 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "The claim is stated but unverified in the record. That does not make it false" | Absence of R1 records reflected throughout; legitimacy not inferred. |
| Purpose fit | evidenced | R: "Faulting the lack of a comparison between plans is therefore not grounded in the writer's aim" | Ratification purpose governs; ceremonial-has-effect counter-reading given. |
| Retained commitments | covered | R: "S3 assigns money, a date and a responsible person. R1 says no contractor or execution record exists" | Factual, causal, quantified, representative and consequential scrutiny retained. |
| False-positive avoidance | present | R: "Even under that norm, I am not concluding that the process is illegitimate" | Alternatives and legitimacy demands confined to a separate external frame. |
| Normative transparency | declared | R: "Under a deliberative-legitimacy norm... That judgment comes from the external norm" | Basis per weakness; external norm named and separated. |
| Repair usefulness | supported | R: "Dissent pathway: relevant only under the external norm in §5" | Classes mapped to weaknesses and to the norm they depend on. |

#### N03 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "Missing comparison records... do not prove that no comparison occurred" | Claims anchored; absence of records not converted to falsity or illegitimacy. |
| Purpose fit | evidenced | R: "Their absence therefore does not breach a promise of choice" | Ratification purpose governs; symbolic-ratification reading given. |
| Retained commitments | covered | R: "Ceremonial participation does not remove these questions" | Factual, causal, quantified and consequential scrutiny retained despite ceremonial framing. |
| False-positive avoidance | present | R: "these records neither establish institutional legitimacy nor establish illegitimacy" | No choice or legitimacy demand. |
| Normative transparency | declared | R: "Those norms are not supplied as governing requirements" | Bases named per question; external norms kept separate. |
| Repair usefulness | supported | R: "corroborating the inspection and mechanism, clarifying the figure's coverage" | Classes grounded; no invented evidence. |

#### U01 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "Bounded observation: none is possible. Nothing is recorded" | Operation read from S1/S2; absence of records not read as outcome. |
| Purpose fit | evidenced | R: "Counter-reading: the 'when' describes an ongoing practice that is always open to join" | Invitation aim governs; counter-reading per weakness. |
| Retained commitments | covered | R: "The passage does not undertake any of these, so there is nothing of these kinds to keep" | Correctly finds no factual/causal/quantified/policy commitment; representative "we" noted. |
| False-positive avoidance | present | R: "the intended readers may already share this knowledge... ordinary insider shorthand" | Logistics point hedged; external participation/surveillance norms kept separate. |
| Normative transparency | declared | R: "External-norm critique (separate; not requested)" | Bases named per weakness; unrequested norms labeled. |
| Repair usefulness | supported | R: "Framing the conditional: signal that the identity is open to anyone who joins" | Classes tied to weaknesses; "alternate participation" repair leans on the unapplied external norm. |

#### U01 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "They are not evidence that anyone accepted a duty, joined a watch or prepared the doorway" | Commitments limited to text; absent records read neutrally. |
| Purpose fit | evidenced | R: "it does not establish an aim to recruit people beyond the current neighbors" | Invitation aim governs; insider-routine counter-reading given. |
| Retained commitments | covered | R: "Consequential scrutiny remains applicable to the conduct proposed" | Absent claim types correctly not scrutinized; proposed conduct kept in scope. |
| False-positive avoidance | present | R: "It does not establish that the burden is unfair or impracticable" | Weaknesses hedged; no exclusion or burden finding asserted. |
| Normative transparency | declared | R: "The criticisms above rest on the confirmed writer aim or the passage's own requested conduct" | Bases named; no external norm. |
| Repair usefulness | supported | R: "Evaluating achieved purpose would require response evidence" | Conditional classes; separates text repairs from evidence needs. |

#### U02 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "R1 records participation, but C1's aim is identification" | R1 read accurately: sequence not cause, invented scenario evidence. |
| Purpose fit | evidenced | R: "Against W1: 'When' can mean 'on the occasions that'" | Identification aim governs; counter-reading per weakness. |
| Retained commitments | covered | R: "R1 should not be used to supply representativeness after the fact" | Scrutiny limited to commitments actually present; observation not over-credited. |
| False-positive avoidance | present | R: "They are offered as optional additions and do not count as failures" | No unsupported demand on the text; rotation-mechanism point grounded in S2's own "tomorrow". |
| Normative transparency | declared | R: "Accessible participation in civic calls... Clear calls to action" | Unrequested external norms named and separated from aim/promise bases. |
| Repair usefulness | supported | R: "Evidence design (for the record, not the text)" | Classes distinguish text repairs from record-keeping; no prose. |

#### U02 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "'After' establishes sequence, not that the address caused their actions" | R1 bounded correctly; no denominator or representativeness inferred. |
| Purpose fit | evidenced | R: "This question rests on [C1], not an external requirement that belonging be unconditional" | Aim governs; counter-reading on conditional identity. |
| Retained commitments | covered | R: "Tonight's participation has some recorded support [R1]; tomorrow's readiness has no recorded follow-up" | Observation, absence and claimed-success categories kept distinct. |
| False-positive avoidance | present | R: "No explicit factual generalization, causal claim, quantified target, or policy outcome claim appears" | No unsupported demand. |
| Normative transparency | declared | R: "No external norm or requested external critique is supplied" | Bases named. |
| Repair usefulness | supported | R: "identity reports for identification, follow-up for tomorrow's request, and comparative evidence for causation" | Repairs matched to the question each would answer. |

#### U03 — Reader A

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "R1 establishes only a sequence ('after this address') and explicitly records no causal comparison" | S3 checked against R1; presence of Ivo/Mira at the address flagged as unknown. |
| Purpose fit | evidenced | R: "Epideictic/ceremonial reading... The internal tension with S1 and S2 remains" | Invitation aim governs; ceremonial counter-reading weighed. |
| Retained commitments | covered | R: "'Every neighbor,' 'for life,' and 'every future turn' are universal" | Factual, quantified, causal and representative scrutiny of S3 retained. |
| False-positive avoidance | present | R: "Consequential policy scrutiny in the formal sense... Non-applicable" | Demands follow S3's own claims; no policy or legitimacy demand. |
| Normative transparency | declared | R: "Named external norm: proportioning claims to available evidence" | Bases visible; two criticisms tagged to reader-supplied external norms rather than to S3's own promise. |
| Repair usefulness | supported | R: "Mood/tense shift: recast S3 from report to hope or invitation, consistent with C1" | Five classes; no prose or invented evidence. |

#### U03 — Reader B

| Dimension | Status | Anchor | Reason |
|---|---|---|---|
| Source-grounding | evidenced | R: "This does not prove S3 false within the fiction" | S3 measured against R1's bounded observation; empirical truth not inferred. |
| Purpose fit | evidenced | R: "shifts from inviting identification to announcing its universal completion" | Invitation aim governs; celebratory counter-reading weighed. |
| Retained commitments | covered | R: "Occurrence after the address does not establish occurrence because of it" | Factual, quantified, durational and causal scrutiny of S3 retained. |
| False-positive avoidance | present | R: "Are broader policy benefits... established? Non-applicable on these materials" | No unsupported demand. |
| Normative transparency | declared | R: "The criticism rests on S3's own universal claim, not an external norm" | Bases named per weakness. |
| Repair usefulness | supported | R: "distinguish invitation from achieved identification, align quantified claims with recorded coverage" | Classes grounded; no invented findings. |

### Invalid reads

**No read is invalid on its content.** All 62 outputs are complete (each ends in a finished closing statement; word counts match both meta files), none refuses, none is empty, and none mentions tools, files, repositories, skills, sibling packets, keys or prior context. The word "packet" in R06.A/R06.B comes from R06's own INPUT body ("The packet contains no adoption proposal").

**Context deviations recorded in the meta files (flagged for the screen panel, not ruled invalid here):**

- All 31 Reader B reads: `raw/reader-b/meta.jsonl` records that "global AGENTS.md and user skill names still loaded (owner-accepted deviation)". Read literally, the brief's rule (a read is invalid "if the reader saw anything beyond prompt and body") covers this. The meta file marks it owner-accepted, and no B output shows any trace of that context.
- All 31 Reader A reads: `raw/reader-a/meta.jsonl` records "account email attached automatically". The same literal rule covers this. Unlike B's deviation, the meta file does not mark it owner-accepted. No A output shows any trace of it.

Neither deviation exposed sibling packets, keys or prior responses. Whether either one invalidates reads under the frozen brief is a screen-panel ruling. If the literal rule applies, it reaches all 62 reads equally.
