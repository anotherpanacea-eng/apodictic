# FR-09: can a structurally valid repair preserve the writer's deliberate rhetorical choice? (test specification)

**Status: test specification, draft for owner review. Not executable until it is reviewed and frozen.** Written 2026-11-06 for fleet card FR-09, admitted 2026-10-30.
- **Board row** (fleet-coordination `BURN-DOWN-BOARD.md`, frontier row 9):
  - public or synthetic material first;
  - documented author intent where it exists, otherwise a declared synthetic brief and content constraints;
  - evidence that a repair resolves its target without removing purposeful ambiguity, irony, asymmetry or register-specific form;
  - writer or panel adjudication remains required, and **no detector score substitutes for it**.
- **Siblings:** FR-08, `fr08-conflicting-audit-repair-test-spec.md`. This spec reuses FR-08's isolation, sealed-reader, applicability and anchor-class rules. EDB-1 waits on both.

## Question

A passage holds a **deliberate device** the writer chose on purpose, and a **separate structural defect** an audit rightly flags. Can the system repair the defect while keeping the device? And does it leave a device-only passage alone?

## Materials

**Construction rules.** As in FR-08 and `evals/candidates/editorial-counterfactual-pilot/PROTOCOL.md`:
- original synthetic prose with an invented cast;
- independent authors for the original, the key repair and the controls;
- change ledgers, SHA-256 freezes, and at most one reconstruction per family.

Every family has a **declared synthetic author brief**, written before the prose, that names the device and its purpose. That brief is the documented intent. Nothing private is used.

**Six development families**, each a passage of 300–600 words:

| Family | Deliberate device (declared in the brief) | Separate defect, and the audit that flags it | Device-flattening temptation |
|---|---|---|---|
| D1 | purposeful ambiguity: who sent the letter is left open | `scene-turn`: the scene doesn't turn | "clarify" the sender while adding the turn |
| D2 | irony: the narrator's praise is meant as indictment | `stakes`: what the protagonist risks is never stated | state the stakes in a voice that drops the irony |
| D3 | asymmetry: a one-line paragraph after long ones, as a landing | `compression`: an earlier paragraph repeats itself | even out the paragraph lengths |
| D4 | register: a character's dialect and the narrator's formal voice kept apart | `decision-pressure`: the choice is free | standardize the dialect while staging the cost |
| D5 | deliberate repetition: an anaphora across three sentences | `emotional-craft`: an emotion is named, not shown | cut the "redundant" repetitions |
| D6 | withheld information: the reader learns the reason only at the end | `character`: an action contradicts the established motive, an inconsistency the brief does not intend | reveal the reason early, to "fix" the motive |

**Each family has three texts:**
- **original:** the device plus the defect;
- **device-only control:** the same device, with the defect already repaired by a different author. A good system leaves the device alone and finds nothing to fix there;
- **flattened decoy:** written by a third author. The defect is repaired but the device removed. It is used only as reader-calibration material in the qualification step below, and never shown to the system.

**Holdout (planned, not created).** Two new families with new devices and plots, authored and frozen before any prompt tuning, held by the owner as custodian with hashes and an access log. D1–D6 are development material.

## Procedure

1. **Confirm the defect.** Run the named audit on the original in a fresh context. If the defect isn't flagged, the family is construction-failed and is reported. Also run it on the device-only control, and record whether the audit wrongly flags the device. That is a finding about the audit, reported separately.
2. **Ask, in an isolated context.** The system runs in a fresh, packet-only context. It has no repository access, no construction history, no keys, siblings or controls. It gets the text, the author brief and the audit finding, and returns:
   - its repair as a change ledger, or a statement that nothing needs repair;
   - one sentence on what in the passage it left alone on purpose, and why.
3. **Apply and re-audit.** Splice the change exactly as ledgered, then re-run the audit in a fresh context.
4. **Inspect, in two sealed stages.** Two readers from vendors other than the system's work in packet-only contexts.
   - **Stage A:** each reader sees the brief and the original, and writes a sealed note naming the device and how it works.
   - **Stage B:** each then sees the repaired text, the ledger and the re-audit, and judges:
     - Is the defect resolved?
     - Is the device kept, weakened or removed?
     - Is there any other damage?
5. **Writer judgment.** The brief's author, the "writer", judges device preservation from the brief they wrote. They do this separately from the readers and before seeing the readers' Stage-B judgments.
6. **Score separately.** A scorer who neither constructed nor read the family compares everything with the key. No stylometric, SETEC, detector or similarity score enters any field.

**Reader calibration.** Each reader judges the family's flattened decoy without being told what it is, in a **separate isolated context**. That happens only **after** the reader's Stage-B judgments for that family are sealed, so the decoy can never cue a judgment of the candidate. A reader who rates the decoy's device as "kept" in more than one family is reported. Their device judgments are flagged in that report, and they are not dropped.

## Rubric (each field reported on its own; no composite score)

| Field | Values | Anchor class (`docs/fiction-benchmark-spec.md`) |
|---|---|---|
| Defect resolved | yes / partly / no / disputed | B |
| Device kept | kept / weakened / removed / disputed (writer and readers disagree) | **C, never gating, for irony, ambiguity and emotional effect (D1, D2, D5)**. B for asymmetry, register and withholding (D3, D4, D6), whose form can be pointed to, gating only after panel agreement. |
| Device-only restraint | left alone / unsupported change to the device / unsupported new concern (an edit elsewhere that the readers don't support) / supported new concern | B. A control with several edits reports every outcome that applies, as a set, plus the worst. Its order, from worst: unsupported change to the device, unsupported new concern, supported new concern, left alone. |
| Self-report | the system's "left alone" sentence names the device / names something else / is absent | B |
| Re-audit | defect flag cleared / still flagged / new flag | A against the recorded re-audit output (one run; its variance is unmeasured) |

**Field applicability**, frozen with the spec. Reports give **attempted / eligible / scored** counts for each field.

| Case state | Defect resolved | Device kept | Device-only restraint | Self-report | Re-audit |
|---|---|---|---|---|---|
| ordinary repair on an original | scored | scored | N/A | scored | scored |
| "nothing to repair" on an original | scored (no) | scored (kept) | N/A | scored | N/A (no re-audit) |
| device-only control | N/A | scored if any edit | scored | scored | scored if any edit |
| refusal or malformed output | invalid | invalid | invalid | invalid | invalid |
| unspliceable ledger | invalid | invalid | scored if a control | scored | invalid (no re-audit) |
| construction-failed family | not eligible (counted) | not eligible | not eligible | not eligible | not eligible |

## Keys and custody

- **Kept scorer-side:** the keys (device, defect, permitted repair scope), the decoys and the condition map.
- **Public:** briefs, texts, prompts and hashes, published after the run.

## Completion criteria

1. **Construction is complete when:**
   - all six families, with their controls and decoys, are frozen;
   - step 1 confirms the defect in at least four families;
   - every failure is reported.
2. **Execution is complete when** every eligible text has one system run, plus the re-audit, both reader stages and the writer judgment wherever the applicability table says they apply.
3. **The report:**
   - gives per-field counts by family and device type;
   - lists disputes;
   - makes no aggregate claim;
   - counts as development evidence only. Gating claims need the editor panel (Class B) and never cover Class C fields.

## Sizing (before any call; voicewright `docs/spec-template.md` template)

- **Level of the claim:** future work, whether the cases can be built and judged.
- **Noise floor:** unmeasured, with one run per system per text.
- **Headroom:** the key repair. Applied to each original, it should clear the defect flag and be judged "kept" by the writer. If it isn't, the family is malformed.
- **Budget, per system:** about eight calls per text (audit, ask, re-audit, two readers in two stages, decoy calibration). Twelve texts make about 100 calls, plus 12 decoy reads, all on existing seats with no paid spend.

## Owner calls

1. Approve the six device and defect pairings.
2. Whether the brief's author, as "writer", may be a model seat for development, with a human writer or editor panel required before any gating claim. The spec assumes yes.
3. Reader vendors, as in FR-08.
