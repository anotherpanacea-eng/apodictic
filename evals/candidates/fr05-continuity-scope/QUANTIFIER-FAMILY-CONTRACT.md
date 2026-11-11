# Quantifier family contract: restricted set vs universal claim (draft for owner review)

**Status: preparation only. Nothing here is adjudicated or admitted.** Written 2026-11-06 for fleet card CAM-07 (public benchmark foundry).
- **Owner, 2026-11-05:** prepare clear restricted-set and universal-claim continuity cases first; keep disputed fiction discussion-only ("That sound right").
- **Structure:** this contract answers parts A, B, C and E of the CAM-07 upstream review packet (`fleet-coordination/handoffs/CAM-07-UPSTREAM-REVIEW-2026-10-30.md`), for this one family. Part D, the disputed FR-07 families, does not apply to it.
- **Not authorized:** no model call, scoring, freeze or ground-truth claim is made or authorized here.

**Development material** (public, never a holdout): the FR-05 v1 pair `flint`, the control, and `birch`, the mutation. In the v1 fold its status is RETAIN-CANDIDATE, which is eligible for further review, not a key.

## A. Rubric and evidence sheet

**Construct.** A universal or quantified claim ("every", "all", "none", "each") holds only within its stated referent set. **The defect** is a quantified claim whose referent set, as written, includes a member that the text elsewhere explicitly places outside the claim. It is a continuity defect between two in-text facts. It is not a judgment of style.

**A case is a materially supported defect only when all four hold:**
1. **The universal is the narrator's assertion** (or an unmarked report the text adopts), not a character's speech, thought or focalized perception. Hyperbole in a character's mouth is craft, not error.
2. **The referent set is explicitly enumerable from the text:** an inventory, a count or a named list.
3. **A member of that set is explicitly shown to falsify the claim.** That means a fact in the narration, not an inference or something offstage.
4. **No in-text repair is available without changing words.** For example, no stated exception, and no time window that excludes the member.

**Evidence anchors**, each classed as **checkable** (a string-level fact a reader can point to) or **interpretive**. This family's anchors are meant to be checkable:

| Anchor | Class | Example (`birch`) |
|---|---|---|
| The universal and its scope | checkable | "Every launch in the shed had spent the whole night and morning without an engine" |
| Set enumeration | checkable | the explicit three-launch inventory |
| Falsifying member | checkable | the green launch's never-removed, sealed engine, and the rescue in the same interval |
| Voice of the claim | interpretive at the margin | narrator, not a character |

**Strongest competing reading, recorded per case.** For `birch`: "every launch" might silently exclude the green launch, or an offstage installation occurred. The inventory, the all-morning scope, the service seal and the no-installation statement rule these out, per the v1 intent.
- **If a reasonable competing reading survives,** the case is `disputed` and is never scored as binary.
- **Fields kept separate:**
  - diagnosis: is the defect present;
  - unsupported intervention: did the reader flag something that isn't there;
  - conservation: does a repair keep events, facts and voice.

  **Updating** (withdrawal after evidence) is **deferred to a separate contract.** Evaluating it needs a comparably substantive control that *retains* the target, so that indiscriminate withdrawal can't pass as evidence-sensitive updating. This family's controls remove the target (the clean base) or test specificity (the craft control), so they cannot support it.
- **A clean control has no target,** so its diagnosis is N/A, not a miss.

**Allowed repair scope.** Restore or narrow the restrictor ("red-tagged"). Keep every event, the falsifying member's history and the narrator's voice. A repair that deletes the falsifying fact is unsupported, because it destroys a commitment.

## B. Planted-defect and control policy

- **Base:** each case starts from a clean base story, newly authored and synthetic. In the base, the universal carries an explicit restrictor and the set is enumerated.
- **Mutation:** exactly one contiguous replacement that widens or drops the restrictor. Everything else stays byte-identical. A mutation ledger records the before and after, the loci, the mechanism and the minimal repair, in the `operator/intent.json` form.
- **Control:** the base itself. A **craft control** is also proposed: a character, not the narrator, speaks the same unrestricted universal as an evident overstatement. It is quoted direct speech with a speech tag, never free indirect or focalized narration, so that criterion 1 settles its voice without interpretation. This tests that unreliability or hyperbole is not called a defect.
- **No seam:** the mutated sentence must read as authored prose. Review the whole story, not an excerpt, because whether the falsifying fact is "unpaid" depends on full context.
- **Magnitudes:** report each mutation's word-level edit size. Equal word counts don't establish equal salience, so salience is noted in words by the constructor.
- **No polishing to consensus.** Failed and disputed constructions are kept. As in FR-07, at most one immutable reconstruction per case, made as a v2 with new hashes, never by rewriting v1.

## C. Disjoint holdout plan (proposed, not created)

- **Development:** `flint`, `birch` and anything derived from them, which are public now. Re-reading them never creates holdout evidence.
- **Holdout:** **two new plot families**, each authored fresh as a clean base, a mutation, a craft control and a repair. They use new plots and new restrictor mechanisms, for example restriction by time window or by role, rather than by a tag. They draw on neither the FR-05 stories nor their specific mechanism. They are authored and frozen **before** any prompt is tuned on this family.
- **Custody:**
  - **Creator:** a constructor who doesn't tune prompts for this family.
  - **Custodian:** the owner.
  - **Storage:** the private Dropbox benchmark folder, not this public repo, until scoring.
  - **Records:** SHA-256 and byte length for every file, plus an access log. Keys and adjudications stay scorer-side.
- **Exposure:** any exposure is logged and the claim is limited. A difficult case is never quietly replaced.
- Creating the freeze is a later, bounded action. This section is the plan for it.

## E. Admission checklist (for each holdout case, before any scoring)

1. Provenance, exact bytes and mutation ledgers reconcile (the `verify_packet.py` pattern).
2. Reader inputs carry no keys, condition labels or diagnostic hints, and use neutral filenames.
3. Independent evidence shows the target is material, the control and craft control are clean, and the repair resolves the target while conserving events and voice, with no unresolved confound.
4. A surviving competing reading makes the case `disputed`. Model agreement is not human licensing.
5. **Licensing lane, proposed for this family: Lane 1.** The scope, enumeration and falsifying-member anchors are checkable (A), and construction keeps voice off the margin (a narrator sentence in the mutation, attributed direct speech in the craft control), so the case needs a documented independent check of those anchors, not the three-editor panel that interpretive (Lane-2/B) anchors require. Any case whose voice-of-claim anchor is contested drops to `disputed`. Owner call 1.
6. Scorer fields, denominators, invalid and refusal handling, and completion are frozen first. Related variants of one plot count as one family, not as independent cases.
7. The owner approves this rubric, the planted-defect policy and any ground-truth claim before registration or scoring.

## Owner calls

1. Lane 1 licensing for this family's checkable anchors, as in E5.
2. The craft control: a character's hyperbolic universal, as in B.
3. Holdout size: two plot families as proposed, or more.
4. Who the holdout constructor and adjudicator are.
