# Structural Prompt Library

**Status:** v1.0
**For:** APODICTIC Revision Coach
**Last updated:** 2026-03-20
**Depends on:** `writers-block-taxonomy.md`, `Diagnostic_State.md`, `Argument_State.md`

---

## Purpose

Seven reusable prompt families for structurally-informed writing experiments. The coach selects from this library based on block diagnosis and corridor identification. The writer does not browse this library directly.

Every prompt generated from these families must pass the 5-part firewall test, include a clinamen clause, and end with a structural self-check.

---

## The Firewall Test (5-Part, Canonical)

Every structural prompt must pass all five conditions. Failure on two or more conditions means the prompt is prescriptive and must be blocked.

| # | Test | Pass condition | Fail condition |
|---|------|----------------|----------------|
| 1 | **State-grounded** | The prompt clearly derives from a diagnosed mechanism in `Diagnostic_State.md` or `Argument_State.md` | The prompt could have been given to almost any writer on almost any project |
| 2 | **Constraint-based** | The prompt specifies a structural requirement, comparison, or lens | The prompt specifies an event, reveal, policy conclusion, or story outcome |
| 3 | **Plural-solution** | Multiple incompatible writer-created answers could satisfy the prompt | Only one obvious plot or argument move could count as "correct" |
| 4 | **Aesthetic-open** | Voice, scene content, imagery, facts, and line-level execution remain the writer's responsibility | The prompt dictates the content-bearing material |
| 5 | **Self-evaluative** | The prompt ends with a structural test, reflection check, or comparison criterion | The prompt asks only for more text, not for judgment about whether the mechanism changed |

### Firewall Examples

| Domain | Verdict | Example | Why |
|--------|---------|---------|-----|
| Fiction | **Pass** | "Draft three versions of [scene corridor] in which the POV character initiates the turn rather than reacting. Which version creates the clearest downstream pressure? If you find a better structural move by breaking the initiation constraint, that counts." | State-grounded, multi-solution, self-evaluative, clinamen clause |
| Fiction | **Edge** | "Rewrite [scene] so [character] reveals the secret they have been hiding." | Structural locus is plausible, but the event is being chosen for the writer |
| Fiction | **Fail** | "Write the breakup scene where [character A] tells [character B] they are leaving town." | Event, content, and outcome are prescribed |
| Argument | **Pass** | "Generate three possible warrants connecting [C1] to [C0] while keeping the evidence fixed. Which warrant survives the strongest logged objection? If a better bridge emerges that doesn't look like any of the three, keep it." | Explores bridge logic without scripting claims |
| Argument | **Edge** | "Draft the counterargument paragraph answering the cost objection with one statistic and one anecdote." | Better than ghostwriting, but specifies paragraph form and evidence recipe too tightly |
| Argument | **Fail** | "Write a conclusion arguing that the policy will protect children and lower taxes." | Chooses the claim content and desired outcome |
| Fiction | **Pass** | "Compress [scene] to one paragraph. Keep only what changes relation, cost, or knowledge. What still matters?" | Pure structural compression test |
| Argument | **Pass** | "Separate [testimony corridor] into observation, interpretation, and recommendation. Which layer is currently carrying more burden than it should?" | Structural separation, not witness scripting |

---

## Prompt Families

### 1. Constraint

**Structural purpose:** Force one structural requirement to become explicit while freezing other variables.

**Best for block types:** Cognitive overload (1), Decisional (4), Stage-mismatch (8), partial structural uncertainty.

**Diagnostic_State patterns:** Agency collapse, unstable turning point, blurred scene function.

**Argument_State patterns:** Blurred claim corridor, objection avoidance, testimony containment.

**Allowed:** Specify who must initiate, which layer must remain fixed, which distinction must hold, which burden must be met.

**Forbidden:** Naming the event, revelation, policy conclusion, relationship outcome, or paragraph content.

**Skeleton:**
```
Using [corridor from state], draft 2–3 variants where [structural requirement] holds
while [other variable] stays fixed. Then test which version best satisfies [diagnostic
condition]. If you find a better move by breaking the constraint, keep it — the
experiment succeeded.
```

**Genre/argument notes:** Best default family. In argument work, use for claim paths, warrant bridges, or testimony containment rather than sentence drafting.

---

### 2. Inversion

**Structural purpose:** Expose the draft's habitual move by forcing its structural opposite.

**Best for block types:** Cognitive (1), Motivational-avoidance (2, when avoidance is structural), Decisional (4).

**Diagnostic_State patterns:** Habitual reactive scenes, repeatedly deferred confrontation, safe-but-inert pacing.

**Argument_State patterns:** Repeatedly deferred objection, safe claim order, fear-driven repetition.

**Allowed:** Require opposite structural motion — initiate instead of react, concede earlier instead of later, show consequence instead of explanation.

**Forbidden:** Dictating the exact opposite event, naming the revelation, implying the inverted version is the final answer.

**Skeleton:**
```
Draft one version in which the draft's habitual move is reversed: instead of [current
structural habit], the section must [opposite structural move]. Compare what changes
downstream. The inverted version is an experiment, not a replacement — but if you
prefer what it reveals, use it.
```

**Genre/argument notes:** Useful when the writer keeps reproducing the same safe move. In horror or thriller, inversion must still respect contract pressure. In argument work, strong for deferred objections.

---

### 3. Isolation

**Structural purpose:** Separate one layer of work from the others so it can be tested alone.

**Best for block types:** Cognitive overload (1), Aesthetic/execution gap (6), Accumulated complexity.

**Diagnostic_State patterns:** Too many moving parts, mixed scene functions, tone-content entanglement.

**Argument_State patterns:** CL instability, muddled warrants, testimony bleed (observation / interpretation / recommendation mixed).

**Allowed:** Isolate emotion from plot, plot from exposition, claim from evidence, observation from interpretation.

**Forbidden:** Asking for a finished replacement scene or paragraph instead of an isolated layer.

**Skeleton:**
```
Work only on [single layer] in [corridor]. Ignore [other layers] for now. When done,
check whether the isolated layer now makes the next revision decision clearer. If
working on the layer surfaced a different problem than the one diagnosed, follow
that instead.
```

**Genre/argument notes:** High-value for `Argument_State.md` work (respects dependency order). Valuable for tonal drift, mixed-function scenes, and the aesthetic/execution gap where the writer needs to practice one skill without global coherence burden. **Safest family for the accumulated-feedback block** when any prompt is offered at all.

---

### 4. Scale-Shift

**Structural purpose:** Change the size of the unit to reveal what is load-bearing.

**Best for block types:** Cognitive (1), Stage-mismatch (8), Decisional (4), pacing/compression problems.

**Diagnostic_State patterns:** Scene sprawl, overbuilt section, proportional imbalance, summary where dramatization is needed.

**Argument_State patterns:** Diffuse op-ed, bloated objection handling, AC mismatch, verbose warranting.

**Allowed:** Compress to one paragraph / six sentences / one claim ladder, or expand one line into a full structural unit.

**Forbidden:** Requiring final polish in the compressed version, or dictating which sentence/claim must remain.

**Skeleton:**
```
Compress [corridor] to [small unit]. Then expand only the part that still carries
structural load. What turned out to be necessary? If the compressed version is
better than the original, you may already have your revision.
```

**Genre/argument notes:** Excellent for pacing, compression, and opening/closing problems. In argument work, tests whether concession logic or claim sequence survives shorter form. Strong for decisional blocks: compress two competing options to see which retains more energy.

---

### 5. Perspective

**Structural purpose:** Reveal what the current vantage cannot see.

**Best for block types:** Cognitive (1), Identity/vision threat (5), objection pressure.

**Diagnostic_State patterns:** Motivation blind spot, antagonist opacity, character relationship deadlock.

**Argument_State patterns:** Audience mismatch, hostile-reader vulnerability, OB avoidance, witness overreach.

**Allowed:** Switch to another legitimate vantage, reader posture, or witness position while keeping the same structural corridor.

**Forbidden:** Naming what the other character or audience must say, believe, or conclude.

**Skeleton:**
```
Rework [corridor] from the vantage of [other legitimate perspective / audience].
Focus only on what this position wants, knows, contests, or fears. Then check what
this exposes in the original. If the new vantage makes a better scene or argument
than the original, follow it.
```

**Genre/argument notes:** Strong in argument revision for objections, audience recalibration, and testimony containment. In fiction, use only perspectives the draft has already earned. **Easiest family to let drift into content invention** — the coach must monitor for prescribed dialogue or beliefs attributed to the alternate perspective.

---

### 6. Deletion

**Structural purpose:** Discover what survives when non-load-bearing matter is removed.

**Best for block types:** Cognitive (1), Stage-mismatch (8), overbuild, scope creep.

**Diagnostic_State patterns:** Scene bloat, overexplained stakes, unnecessary subplot matter, compression needs.

**Argument_State patterns:** Verbose warranting, redundant evidence, overexplained concessions.

**Allowed:** Require cutting a percentage, keeping only what changes relation / cost / claim, or rebuilding from what remains.

**Forbidden:** Prescribing what must be cut by content, or treating the deletion experiment as the final editorial verdict.

**Skeleton:**
```
Cut [portion] from [corridor]. Keep only what still changes the structural situation.
Then identify what, if anything, must be rebuilt. This is an experiment — what you
cut in the exercise is not necessarily what you cut in the manuscript.
```

**Genre/argument notes:** Best for overbuild and scope creep. Should not be used when a direct cut decision is already obvious and accepted — in that case, the intervention is "cut," not a prompt. No prompt needed.

---

### 7. Temporal

**Structural purpose:** Use time movement to expose commitment, consequence, or missing preparation.

**Best for block types:** Cognitive (1), partial-manuscript uncertainty, consequence fog.

**Diagnostic_State patterns:** Weak aftermath, unclear setup debt, inert reveal timing, absent downstream cost.

**Argument_State patterns:** Unclear testimony consequence, missing claim obligation, abstract downstream burden.

**Allowed:** Move briefly to immediate aftermath, later memory, prior setup moment, or downstream implication while staying abstract.

**Forbidden:** Naming the future event that must happen, or inventing sequel content as if it were already chosen.

**Skeleton:**
```
Move to [earlier / later] relative to [corridor] and track only what changed in cost,
knowledge, relationship, or burden. Then return and ask what the current draft must
earn. If the temporal exercise produces material you want to keep, you can — it's
yours.
```

**Genre/argument notes:** Useful when the writer cannot tell what a scene or claim corridor is obligating. In argument work, temporal prompts are better for consequence chains than for evidence gathering. **Riskiest family for inventing future canon** — the coach must frame the temporal move as hypothetical, not as draft material.

---

## Mapping: Diagnostic_State.md to Prompt Families

| Diagnosed pattern | Best-fit families | Prompt or suppress? |
|-------------------|-------------------|---------------------|
| Character agency collapse | Constraint, Inversion, Perspective | Prompt often useful |
| Pacing drag from scene sprawl | Scale-shift, Deletion | Prompt often useful |
| Tonal drift | Isolation, Constraint | Prompt useful when energy is available |
| Reveal flatness / inert information flow | Temporal, Perspective | Prompt useful |
| Scope creep / subplot overload | Deletion | Sometimes useful; often cutting is enough |
| Partial-manuscript structural uncertainty | Temporal, Constraint | Prompt useful |
| Fear of commitment to the hard scene | Existing exercise library first; then Constraint or Inversion | Conditional |
| Exhaustion or burnout | None | **No prompt** |
| Accumulated-feedback saturation | None or one very low-load Isolation | **Usually no prompt** |
| Straightforward cut decision already accepted | None | **No prompt — just cut** |
| Factual or continuity error | None | **No prompt — fix directly** |

---

## Mapping: Argument_State.md to Prompt Families

| Diagnosed pattern | Best-fit families | Prompt or suppress? |
|-------------------|-------------------|---------------------|
| CL instability / blurred C0 | Isolation, Constraint | Prompt often useful |
| WR gap / weak inferential bridge | Isolation, Perspective, Constraint | Prompt often useful |
| OB avoidance / red-team vulnerability | Perspective, Inversion | Prompt useful |
| AC mismatch / persuasion sequence problem | Scale-shift, Perspective | Prompt useful |
| Testimony containment problem | Isolation, Constraint | Prompt useful |
| Evidence corridor too thin | None or minimal planning prompt | **Usually no writing prompt** |
| Pure compression in a sound piece | Deletion, Scale-shift | Prompt useful |
| Warrant gap in hostile-audience context | Constraint, Perspective | Prompt useful |
| DI failure / dialectical integrity breakdown | Isolation, Inversion | Prompt useful |

---

## No-Prompt Zones

These states explicitly suppress prompt generation. The coach must recognize them and not generate a structural prompt.

| State | Why prompting is wrong | Better move |
|-------|----------------------|-------------|
| Physiological depletion / burnout | More structure becomes more pressure | Rest, rescope, lighter task, deadline honesty |
| Clear evidence-acquisition gap | Work is research, not writing | Evidence queue, verification, narrowing claim |
| Accepted cut decision | Discovery is over; execution is straightforward | Cut and propagate consequences |
| Factual or continuity error | Issue is correction, not invention | Fix directly |
| Accumulated-feedback saturation | Another layer of mediation worsens the state | Strip back support, reread, outside reader |
| Locked Keep/Cut decision (not reopened) | Prompting would quietly relitigate a settled choice | Respect the lock |
| State file missing or empty | No diagnostic basis for structural prompts | Route to `apodictic-start` or `apodictic-diagnose` |

---

## Family Validation Matrix

For implementation QA. Each family screened against three design tests.

| Family | Diagnostic specificity | Firewall compliance | Cognitive load | Notes |
|--------|----------------------|---------------------|----------------|-------|
| Constraint | Strong | Strong | Conditional | Excellent when the corridor is sharp; overwhelming if too broad |
| Inversion | Medium to strong | Strong | Strong | Best when the draft's habitual move is already visible |
| Isolation | Strong | Strong | Strong | Safest family for complex states and argument work |
| Scale-shift | Strong | Strong | Strong | Usually lowers load quickly |
| Perspective | Medium | Conditional | Conditional | High value, but easiest to drift into content invention |
| Deletion | Strong | Strong | Strong | Best when the issue is excess, not absence |
| Temporal | Medium | Conditional | Conditional | Powerful for consequence fog, risky for inventing future canon |

**Selection rule:** If a family rates only "medium" on specificity and "conditional" on load for the current state, prefer a reframe or no prompt unless the writer explicitly wants an experiment.

---

## Clinamen Clause

Every structural prompt must include implicit or explicit permission to break the constraint if the writer discovers something better during the exercise.

The prompt is a focusing constraint, not a mandate. A writer who violates the constraint and finds a structural improvement has succeeded, not failed.

**Standard clinamen patterns:**
- "If you find a better move by breaking the constraint, keep it — the experiment succeeded."
- "The inverted version is an experiment, not a replacement — but if you prefer what it reveals, use it."
- "If working on the layer surfaced a different problem than the one diagnosed, follow that instead."
- "If the temporal exercise produces material you want to keep, you can — it's yours."

---

## Prompt Delivery Rules

1. **One prompt per corridor.** A second prompt is offered only if the writer explicitly exhausts the first. Never an array.
2. **Prompts are embedded in session plans,** not delivered standalone. They appear in the optional "Structural Experiment" section.
3. **Prompt suppression is a first-class output.** The coach saying "no prompt for this problem" is a valid and often correct intervention.
4. **The writer does not browse this library.** The coach selects internally based on block diagnosis, corridor, and state.
5. **Every prompt is framed as low-stakes and disposable** unless the writer chooses otherwise.
6. **Three layers of mediation is the maximum** (diagnosis + session plan + prompt). If the writer already has a diagnosis and a session plan, the prompt is the last thing added, not the first.

---

*This file is a reference for the coaching protocol. The writer does not see it directly. The coach reads it to select and generate structurally-informed prompts.*
