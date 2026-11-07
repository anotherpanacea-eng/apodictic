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
| F5 | `literary-craft` (a motif is load-bearing) vs `compression` (its repetitions are expendable) | **competing obligations**: the brief caps length *and* requires the motif's three returns | abstain and name the tradeoff, or make the one cut the brief's tradeoff list permits |
| F6 | `scene-turn` vs `stakes` | **competing obligations**: the brief requires the scene to end unresolved (an act-one hook), and the only turn available resolves it | abstain and ask the writer |

**Controls.** Each family has a **resolved variant**, in which a different author has already fixed the cause. Both audits should then agree, or at least not conflict. A system that intervenes on a resolved variant scores an unsupported intervention there; its diagnosis is N/A, not a miss.

**Holdout (planned, not created).**
- Two further families, using neither these plots nor these causes, are authored and frozen **before** any prompt tuning on FR-08.
- They are held by the owner as custodian, outside the repo until scoring, with hashes and an access log.
- F1–F6 and their descendants are development material, published once made.

## Procedure, per family and per system under test

1. **Confirm the conflict.** Run the two named audits on the original, each in a fresh context, with APODICTIC as shipped. If the expected conflict doesn't appear, the family is **construction-failed**: it is reported, and is not rescued by prompting. One reconstruction is allowed.
2. **Ask.** The system gets the text, the writer brief, the tradeoff list and the two audits' findings, and no key. It returns:
   - a causal explanation (one cause, with evidence);
   - either the smallest intervention it justifies, as a change ledger, or an abstention with its reason;
   - a predicted consequence for each audit after the change.
3. **Apply.** The intervention is spliced exactly as ledgered, and the edit magnitude is recorded.
4. **Re-audit.** The same two audits run on the repaired text, in fresh contexts.
5. **Inspect.** Two readers from vendors other than the system's each see the brief, the tradeoff list, the original, the repaired text and the ledger, and no key. Each judges independently:
   - Does the repair resolve the cause?
   - Are the writer's goals and the stated tradeoffs kept?
   - Is there collateral damage elsewhere?

## Rubric (each field reported on its own; no composite score)

| Field | Values | Anchor type |
|---|---|---|
| Cause | match (key or key-listed alternative) / partial / miss / disputed | interpretive: `disputed` when the readers reject the key |
| Intervention | within scope / overreach / missing (none where one was needed) / N/A (abstained) | checkable against the key's scope and the ledger |
| Abstention | correct (F5, F6, or where no in-scope repair exists) / wrong (abstained where a resolvable repair exists) | checkable against the key's kind |
| Prediction | per audit: the predicted direction matches or misses the observed re-audit | checkable |
| Conservation | the readers' judgment: goals and tradeoffs kept / not kept / disputed | interpretive |
| Resulting audits | observed re-audit outcome per audit: conflict resolved / one satisfied at the other's cost / unchanged | checkable |

- **Interpretive anchors** (cause, conservation) report in Lane 2 under `docs/fiction-benchmark-spec.md`. They do not gate until the editor panel licenses them.
- **Checkable anchors** may gate once the owner admits them.

## Keys and custody

- **Kept scorer-side:** keys, causal statements, repair scopes and expected directions. They are never dispatched to the system or the readers.
- **Public:** prompts, briefs, texts and hashes, published after the run.
- **Private:** the private condition map, which says which file is a control.

## Completion criteria

1. **Construction is complete when:**
   - all six families and their controls are frozen;
   - step 1 confirms the conflict in at least four families;
   - every construction failure is reported.
2. **Execution is complete when** every family and control has one system run, one re-audit and two reader judgments. Invalid outputs and refusals stay in the denominators.
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
