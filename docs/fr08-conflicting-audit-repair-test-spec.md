# FR-08: which repair resolves the cause when several audits disagree? (test specification)

**Status: test specification, draft for owner review. Not executable until it is reviewed and frozen.** Written 2026-11-06 for fleet card FR-08, admitted 2026-10-30 ("advance to spec, not idea").
- **Board row** (fleet-coordination `BURN-DOWN-BOARD.md`, frontier row 8):
  - public or synthetic material;
  - frozen writer goals, acceptable tradeoffs, and a case with genuinely competing obligations;
  - adjudicator keys are never dispatched;
  - required: a causal explanation, the smallest justified intervention or a reason to abstain, predicted cross-audit consequences, and independent inspection of the repaired text and its resulting audit consequences.
- **Dependent work:** EDB-1, the editorial intervention benchmark pilot, waits on this spec and on FR-09.

## Question

When two APODICTIC audits give conflicting diagnoses of the same passage, can the system name the **single cause** behind both? Can it make the **smallest repair** that resolves that cause, or abstain when no repair can honor the writer's goals? And can it predict what each audit will then say?

A system that satisfies one audit by breaking the other, or that edits when it should ask, fails the question even if one audit improves.

## Materials

**Construction rules.** Everything follows the editorial-counterfactual pilot's protocol (`evals/candidates/editorial-counterfactual-pilot/PROTOCOL.md`):
- original synthetic prose with an invented cast, and no imitation of a named writer;
- separate authors for the original, the repair key and the control;
- change ledgers, SHA-256 freezes, and at most one immutable reconstruction per family.

All material is public or synthetic. Nothing is private.

**Six development families.** Each is one scene of 400–700 words, or two linked scenes, with:
- a **writer brief**: genre, intended effect and outcome, non-spoiling, frozen;
- a list of **acceptable tradeoffs**: what the writer would give up and what not;
- the **two audits** expected to conflict, named below;
- a scorer-side **key**: the single cause, a key-listed competing explanation, the permitted repair scope, and the expected re-audit direction for each audit.

| Family | Audits expected to conflict | The single cause (key) | Kind |
|---|---|---|---|
| F1 | `compression` (cut the walk-and-talk) vs `stakes` (it holds the only statement of what she risks) | the stake is delivered in an expendable vehicle | resolvable: move the stake line into the confrontation, then cut the walk |
| F2 | `scene-turn` (the scene doesn't turn) vs `emotional-craft` (its quiet grief beat is the point) | the turn exists but is internal and unsignaled | resolvable: one externalized beat that makes the turn visible |
| F3 | `decision-pressure` (the choice is free) vs `character` (the alternative contradicts her established habit) | the cost of choosing is offstage | resolvable: put the cost onstage |
| F4 | `interiority` (interiority vanishes under action) vs `compression` (the thought passage is expendable) | the interiority is placed after the action, not inside it | resolvable: relocate it, without adding words |
| F5 | `literary-craft` (a motif is load-bearing) vs `compression` (its repetitions are expendable) | a tradeoff: the brief caps length and values the motif, and its tradeoff list permits trimming one return | resolvable within a stated tradeoff: trim one return and keep two |
| F6 | `scene-turn` vs `stakes` | **competing-obligation candidate**: the brief requires the scene to end unresolved (an act-one hook), and every turn the authors can find resolves it | abstain and ask the writer, **only if** the feasibility check below confirms no in-scope repair exists |

**Feasibility check before any abstention label is frozen.** Two independent authors, who have not seen each other's work, each try to write an in-scope repair that satisfies the whole brief and tradeoff list. Two readers then judge each attempt.
- **If any attempt is accepted,** the family is relabeled resolvable and that repair joins its key.
- **If none is,** the family is labeled **competing**, and abstention is the correct answer.
- **At least one competing family must survive.** If F6 is relabeled, one more competing candidate is constructed under the one-reconstruction rule. If none survives, the report says so and the abstention field is reported as untested.

Note that `scene-turn` accepts reversals and revelations that raise uncertainty. A turn that keeps the hook open is therefore a live candidate repair, and the check must try it.

**Controls.** Each family has a **resolved variant**, in which a different author has already fixed the cause. Both audits should then agree, or at least not conflict. On a control, the system is scored on two things separately:
- **target persistence:** whether it claims the resolved conflict is still there (unsupported if it does);
- **new concerns:** any other edit it proposes, which readers judge supported or unsupported.

A supported new concern is valid criticism, as the editorial-counterfactual protocol permits, not an error. The diagnosis field is N/A on controls.

**Holdout (planned, not created).**
- Two further families, using neither these plots nor these causes, are authored and frozen **before** any prompt tuning on FR-08.
- They are held by the owner as custodian, outside the repo until scoring, with hashes and an access log.
- F1–F6 and their descendants are development material, published once made.

## Procedure, per family and per system under test

1. **Confirm the conflict.** Run the two named audits on the original, each in a fresh context, with APODICTIC as shipped. If the expected conflict doesn't appear, the family is **construction-failed**: it is reported, and is not rescued by prompting. One reconstruction is allowed.
2. **Ask, in an isolated context.** The system runs in a fresh, packet-only context. It has no access to this repository, this spec, construction history, keys, sibling variants or controls. It gets only the text, the writer brief, the tradeoff list and the two audits' findings, and returns:
   - a causal explanation (one cause, with evidence);
   - either the smallest intervention it justifies, as a change ledger, or an abstention with its reason;
   - a predicted consequence for each audit after the change.
3. **Apply.** The intervention is spliced exactly as ledgered, and the edit magnitude is recorded.
4. **Re-audit.** The same two audits run on the repaired text, in fresh contexts.
5. **Inspect, in two sealed stages.** Two readers from vendors other than the system's work in fresh, packet-only contexts, with the same isolation as step 2.
   - **Stage A:** each reader sees the original, the brief, the tradeoff list and the two audits' findings, and writes a sealed **causal account** of their own.
   - **Stage B:** each then sees the system's explanation, the ledger, the repaired text and the step-4 re-audit findings, and judges:
     - Does the repair resolve the cause?
     - Are goals and tradeoffs kept?
     - Is there collateral damage?
     - Is each new concern (on controls) supported?
6. **Score, separately.** A scorer who neither constructed the family nor read it compares the system's explanation and the readers' sealed accounts with the key. Where both readers' accounts converge on a cause other than the key, the cause field is `disputed`.

## Rubric (each field reported on its own; no composite score)

| Field | Values | Anchor type |
|---|---|---|
| Field | Values | Anchor class |
|---|---|---|
| Cause | match (key or a key-listed alternative) / partial / miss / disputed | B: gates only after the editor panel's agreement |
| Intervention | within scope / overreach / missing / N/A (abstained) / invalid (unspliceable ledger) | A for the mechanical part (the ledger stays inside its declared span; edit magnitude); B for "within scope" |
| Abstention | correct abstention (on a competing family) / correct repair (repaired a resolvable family) / wrong (abstained on a resolvable family) / missed (repaired a competing family, and Stage B rejects the repair) / label disputed (repaired a competing family, and **both** Stage-B readers accept the repair as in scope) | B: the label rests on the feasibility check's readers. A `label disputed` result withholds the abstention judgment for that family from **every** system until the owner or panel adjudicates the construction label. |
| Unsupported intervention | none / target persistence claimed / unsupported new concern / supported new concern | B |
| Prediction | per audit: the predicted direction matches or misses the observed re-audit | A against the recorded re-audit output (one audit run; its variance is unmeasured) |
| Conservation | goals and tradeoffs kept / not kept / disputed | B, except where the kept thing is emotional weight (F2's grief beat) or thematic resonance (F5's motif): those are **C, never gating** |
| Resulting audits | per audit: conflict resolved / one satisfied at the other's cost / unchanged | A against the recorded re-audit output |

- **Classes follow `docs/fiction-benchmark-spec.md`.** Class A is Lane 1: it may gate once the owner admits it. Class B is Lane 2: it gates only after the editor panel's documented agreement. Class C is Lane 3: it never gates, and is exploratory only.

**Field applicability.** This table is frozen with the spec. Every report gives **attempted / eligible / scored** counts for each field.

| Case state | Cause | Intervention | Abstention | Unsupported intervention | Prediction | Conservation | Resulting audits |
|---|---|---|---|---|---|---|---|
| ordinary repair (a spliceable repair on a resolvable family) | scored | scored | scored (correct repair) | N/A | scored | scored | scored |
| repair on a competing family | scored | scored | scored (missed, or label disputed) | N/A | scored | scored | scored |
| construction-failed family | not eligible (counted) | not eligible | not eligible | not eligible | not eligible | not eligible | not eligible |
| control | N/A | N/A | N/A | scored | scored if an edit was made | scored if an edit was made | scored if an edit was made |
| abstention | scored | N/A | scored | N/A | N/A | N/A | N/A (no re-audit) |
| refusal or malformed output | scored **invalid** | invalid | invalid | invalid | invalid | invalid | invalid |
| unspliceable ledger | scored | invalid | scored | scored | invalid | invalid | invalid (no re-audit) |

## Keys and custody

- **Kept scorer-side:** keys, causal statements, repair scopes and expected directions. They are never dispatched to the system or the readers.
- **Public:** prompts, briefs, texts and hashes, published after the run.
- **Private:** the private condition map, which says which file is a control.

## Completion criteria

1. **Construction is complete when:**
   - all six families and their controls are frozen;
   - step 1 confirms the conflict in at least four families;
   - every construction failure is reported.
2. **Execution is complete when** every eligible family and control has one system run, and the re-audit and both reader stages wherever the applicability table says they apply. Invalid outputs and refusals stay in the attempted counts.
3. **The report:**
   - gives per-field counts by family and kind (resolvable or competing);
   - lists every disputed case;
   - makes no aggregate accuracy claim;
   - treats every result as development evidence.

## Sizing (before any call; template from voicewright `docs/spec-template.md`)

- **Level of the claim:** future work. FR-08 shows whether the cases can be built and read, not a measured accuracy.
- **Noise floor:** unmeasured. There is one run per system per family.
- **Headroom:** the key's repair, re-audited, is the oracle. Applying the key repair to each resolvable family should resolve the conflict in step 4. If it doesn't, the family is malformed.
- **Budget, per system:** about nine calls per family (two audits, the ask, two re-audits, two readers, plus retries). Twelve texts, six families and six controls, come to about 110 calls, all on existing seats with no paid spend.

## Owner calls

1. Approve the six blueprints, or replace any.
2. Choose the reader vendors (proposed: whichever two vendors did not make the system's repair).
3. Confirm controls for all six families, or only the resolvable four.
