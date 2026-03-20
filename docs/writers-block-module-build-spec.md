# Writer's Block & Rut-Breaking Module — Build Spec
## APODICTIC Revision Coach Extension
*Date: March 20, 2026*
*Status: Ready for build*
*Synthesized from: Opus 4.6 research, Gemini research, Codex level-setting (codex54), Codex prompt inventory (codex54), original research spec*
*Depends on: Revision Coach v1.3.0, Coaching Protocol, Session Plan Template, Diagnostic_State.md, Argument_State.md*

---

## What This Document Is

A unified build specification for the Writer's Block & Rut-Breaking module. It integrates theoretical research from three models, resolves tensions between them, and specifies what to build, where it goes, and what constraints govern it. A developer (human or AI) should be able to build the module from this document plus the referenced level-setting research.

This document contains:

1. Architecture decisions (final)
2. Expanded block taxonomy (replaces the current three-way split)
3. Firewall test (canonical, 5-part)
4. Prompt families with specifications and sample skeletons
5. Mapping tables for both `Diagnostic_State.md` and `Argument_State.md`
6. Integration plan with existing coaching infrastructure
7. Hard constraints and no-prompt zones
8. File map

---

## Architecture Decisions (Binding)

These are resolved. They override anything in the research inputs that conflicts.

1. **Delivery model: embedded in session plans.** Structural prompts are delivered as an optional section within session plans when the coach determines a prompt is the right intervention. No standalone `/prompt` or `/exercise` command in v1. The coach selects from the internal prompt-family library. The writer never browses the library directly as a default experience.

2. **One prompt at a time.** The session plan offers one primary prompt per blocked corridor. A second prompt is offered only if the writer explicitly exhausts the first. Never an array.

3. **Prompt suppression is a first-class output.** The module must be able to say "no prompt for this problem." Some states require rest, cutting, research, or reassessment. Generating a prompt when the correct answer is "stop" is a module failure.

4. **Perfectionism is a cross-cutting amplifier, not a separate block type.** It modifies severity across all block types. Track it as a modifier. Do not create a "perfectionism block" category with its own intervention path.

5. **Clinamen clause in every prompt.** Every structural prompt includes implicit permission to break the constraint if the writer discovers something better during the exercise. The prompt is a focusing constraint, not a mandate. The writer who violates the constraint and finds a structural improvement has succeeded, not failed.

6. **Nocebo inoculation on every diagnosis.** When the coaching protocol delivers a block diagnosis or structural problem identification, it must acknowledge that the writer may already be handling this. Frame diagnostics as one possible lens, not the definitive truth about the manuscript. This is a hard constraint, not a style suggestion. Theoretical basis: Sandra et al. (2025) showed that ADHD awareness workshops caused healthy adults to falsely self-diagnose; brief "nocebo education" halved the effect.

7. **Coexistence with existing exercise library.** The current 6 exercises (Name the Resistance, Sit with the Draft, Write Toward the Difficulty, Permission Draft, Inventory What Works, Seek Outside Readers) remain. They serve motivational/emotional blocks. The new prompt families serve structural blocks. They are different intervention types for different block types. The coaching protocol decides which layer to use based on block diagnosis.

8. **Firewall compliance is non-negotiable.** Every prompt must pass the 5-part firewall test. A prompt that fails two or more conditions is prescriptive and must be blocked. No exceptions for "just this once" or "the writer asked for it."

---

## Expanded Block Taxonomy

Replaces the current three-way split (cognitive / motivational / physiological) in the coaching protocol's Stuck-Point Diagnosis section.

### Primary Block Types

| # | Block type | What is stuck | Signals | Prompt suitability | Intervention layer |
|---|-----------|---------------|---------|-------------------|--------------------|
| 1 | **Cognitive overload** | The writer cannot hold the moving parts or causal dependencies in mind | "Every time I fix one thing, another breaks." "I know what's wrong but I can't figure out how." | High | Structural prompts (Constraint, Isolation, Scale-shift) |
| 2 | **Motivational / avoidance** | The writer is avoiding exposure, failure, or effort | "I hate this scene." "I keep starting and stopping." "I don't know if I can pull this off." | Conditional | Existing exercise library first (Name the Resistance, Permission Draft). Structural prompts only after motivational intervention fails or if the avoidance is specifically about a structural decision. |
| 3 | **Physiological / environmental** | The writer is too depleted to benefit from more cognitive work | "I can't focus." "I've been at this for weeks." "Life stuff." | Low | Usually no prompt. Coach away from the desk. Adjust session scope. |
| 4 | **Decisional / equipoise** | The writer sees multiple viable options and cannot choose | "I could go either way." "Both versions work." "I've been going back and forth for days." Three valid restructuring options with no clear winner. | High | Structural prompts (Scale-shift, Temporal, Constraint). The intervention is satisficing heuristics: prototype briefly, commit to the one with more energy, treat the decision as reversible. |
| 5 | **Identity / vision threat** | The revision threatens the writer's self-concept or the book they set out to write | "If I cut this, it's not the book I wanted." "This revision betrays my vision." "I can't write a book that does that." Defensive framing that sounds like aesthetic disagreement but is actually grief or self-protection. | Conditional | Reframe first (externalize the manuscript from the self; name the grief for the version being revised away). Then low-stakes Constraint or Perspective prompts framed as temporary experiments the writer can reject. Clinamen clause is especially critical here. |
| 6 | **Aesthetic / execution gap** | The writer can diagnose the structural fix but cannot execute it at the quality they want | "I know the scene needs X but I can't make it work." "I hear it in my head but it won't come out right." Attempts and restarts, not avoidance. | Conditional | Isolation prompts to practice the specific craft skill without global coherence burden. Permission Draft if perfectionism is amplifying. Not cognitive restructuring (they understand), not motivational coaching (they're trying). |
| 7 | **Accumulated-feedback / overmediated** | Too much input has destroyed the writer's compass; every sentence arrives pre-tagged with problems | "I can't read my own work anymore." "I keep hearing all the notes." "I don't know what I think." Diagnostic overlay replaces direct encounter with the text. | Low | **Highest-risk block type for APODICTIC.** Prompts usually worsen it. Preferred: strip back support, reread without notes (Sit with the Draft), Inventory What Works, outside reader, short break. If anything is offered, one very low-load Isolation prompt only. |
| 8 | **Stage-mode mismatch** | The writer is applying the wrong level of attention to the draft's current stage | Polishing structural-draft prose. Structural critique on near-finished work. Premature editing. | Moderate | Often solved by reframing before prompting: "This is a structural draft; polish is premature." "The structure is stable; you're in polish mode now." If prompting, Scale-shift to recalibrate the unit of work. |

### Perfectionism Modifier

Perfectionism is not a block type. It is a severity amplifier that cross-cuts all eight types. When present, it makes aesthetic blocks more painful, decisional blocks more paralyzing, identity blocks more threatening, and feedback saturation more destabilizing.

**Detection signals:** Excessive self-criticism disproportionate to actual draft quality. Repeated restarts. "It has to be perfect." Reluctance to commit to any version. Chronic comparison to published work or idealized internal standard.

**Intervention modifier:** When perfectionism is detected as an amplifier, adjust the primary intervention:

- Add Permission Draft framing ("this is disposable") to structural prompts
- Lower the stakes language in the session plan
- Emphasize the clinamen clause more heavily
- Consider whether the perfectionism itself, rather than the structural problem, is what needs addressing first

### Two-Step Diagnosis Protocol

The expanded taxonomy requires a two-step diagnosis:

1. **Gate question:** Is this cognitive, motivational, physiological, or something else?
2. **Refinement question:** *What kind* of cognitive / motivational / other block is this?

The refinement step determines whether a structural prompt is appropriate, which family to use, or whether to suppress prompting entirely. Prompt selection happens only after refinement.

---

## The Firewall Test (Canonical, 5-Part)

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

Seven families. Each is a reusable structural operation on a diagnosed mechanism. The families are organized by what they do to the draft, not by genre, mood, or scene type. Genre calibration modifies a family but never replaces it.

### 1. Constraint

**Structural purpose:** Force one structural requirement to become explicit while freezing other variables.

**Target block types:** Cognitive overload, decisional, stage-mismatch, partial structural uncertainty.

**Target state patterns:** Agency collapse, unstable turning point, blurred claim corridor, objection avoidance, testimony containment.

**Allowed constraint logic:** May specify who must initiate, which layer must remain fixed, which distinction must hold, or which burden must be met.

**Forbidden / prescriptive drift signs:** Naming the event, revelation, policy conclusion, relationship outcome, or paragraph content.

**Prompt skeleton:**
```
Using [corridor from state], draft 2–3 variants where [structural requirement] holds
while [other variable] stays fixed. Then test which version best satisfies [diagnostic
condition]. If you find a better move by breaking the constraint, keep it — the
experiment succeeded.
```

**Genre/argument notes:** Best default family. In argument work, use for claim paths, warrant bridges, or testimony containment rather than sentence drafting.

### 2. Inversion

**Structural purpose:** Expose the draft's habitual move by forcing its structural opposite.

**Target block types:** Cognitive, motivational-avoidance, decisional.

**Target state patterns:** Habitual reactive scenes, repeatedly deferred objection, safe-but-inert claim order, fear-driven repetition.

**Allowed constraint logic:** May require opposite structural motion: initiate instead of react, concede earlier instead of later, show consequence instead of explanation.

**Forbidden / prescriptive drift signs:** Dictating the exact opposite event, naming the revelation, or implying that the inverted version is the final answer.

**Prompt skeleton:**
```
Draft one version in which the draft's habitual move is reversed: instead of [current
structural habit], the section must [opposite structural move]. Compare what changes
downstream. The inverted version is an experiment, not a replacement — but if you
prefer what it reveals, use it.
```

**Genre/argument notes:** Useful when the writer keeps reproducing the same safe move. In horror or thriller, inversion must still respect contract pressure. In argument work, strong for deferred objections.

### 3. Isolation

**Structural purpose:** Separate one layer of work from the others so it can be tested alone.

**Target block types:** Cognitive overload, aesthetic/execution gap, accumulated complexity.

**Target state patterns:** Too many moving parts, mixed scene functions, muddled warrants, tone-content entanglement.

**Allowed constraint logic:** May isolate emotion from plot, plot from exposition, claim from evidence, observation from interpretation.

**Forbidden / prescriptive drift signs:** Asking for a finished replacement scene or paragraph instead of an isolated layer.

**Prompt skeleton:**
```
Work only on [single layer] in [corridor]. Ignore [other layers] for now. When done,
check whether the isolated layer now makes the next revision decision clearer. If
working on the layer surfaced a different problem than the one diagnosed, follow
that instead.
```

**Genre/argument notes:** High-value for `Argument_State.md` work (respects dependency order). Also valuable for tonal drift, mixed-function scenes, and the aesthetic/execution gap where the writer needs to practice one skill without global coherence burden. **Safest family for the accumulated-feedback block** when any prompt is offered at all.

### 4. Scale-Shift

**Structural purpose:** Change the size of the unit to reveal what is load-bearing.

**Target block types:** Cognitive, stage-mismatch, pacing/compression problems.

**Target state patterns:** Scene sprawl, overbuilt section, diffuse op-ed, bloated objection handling, summary where dramatization is needed.

**Allowed constraint logic:** May compress to one paragraph / six sentences / one claim ladder, or expand one line into a full structural unit.

**Forbidden / prescriptive drift signs:** Requiring final polish in the compressed version, or dictating exactly which sentence/claim must remain.

**Prompt skeleton:**
```
Compress [corridor] to [small unit]. Then expand only the part that still carries
structural load. What turned out to be necessary? If the compressed version is
better than the original, you may already have your revision.
```

**Genre/argument notes:** Excellent for pacing, compression, and opening/closing problems. In argument work, tests whether concession logic or claim sequence survives shorter form. Strong for decisional blocks: compress two competing options to see which retains more energy.

### 5. Perspective

**Structural purpose:** Reveal what the current vantage cannot see.

**Target block types:** Cognitive, identity/vision threat, objection pressure.

**Target state patterns:** Motivation blind spot, antagonist opacity, audience mismatch, hostile-reader vulnerability, witness overreach.

**Allowed constraint logic:** May switch to another legitimate vantage, reader posture, or witness position while keeping the same structural corridor.

**Forbidden / prescriptive drift signs:** Naming what the other character or audience must say, believe, or conclude.

**Prompt skeleton:**
```
Rework [corridor] from the vantage of [other legitimate perspective / audience].
Focus only on what this position wants, knows, contests, or fears. Then check what
this exposes in the original. If the new vantage makes a better scene or argument
than the original, follow it.
```

**Genre/argument notes:** Strong in argument revision for objections, audience recalibration, and testimony containment. In fiction, use only perspectives the draft has already earned. **Easiest family to let drift into content invention** — the coach must monitor for prescribed dialogue or beliefs attributed to the alternate perspective.

### 6. Deletion

**Structural purpose:** Discover what survives when non-load-bearing matter is removed.

**Target block types:** Cognitive, stage-mismatch, overbuild, scope creep.

**Target state patterns:** Scene bloat, overexplained stakes, unnecessary subplot matter, verbose warranting, compression needs.

**Allowed constraint logic:** May require cutting a percentage, keeping only what changes relation / cost / claim, or rebuilding from what remains.

**Forbidden / prescriptive drift signs:** Prescribing what must be cut by content, or treating the deletion experiment as the final editorial verdict.

**Prompt skeleton:**
```
Cut [portion] from [corridor]. Keep only what still changes the structural situation.
Then identify what, if anything, must be rebuilt. This is an experiment — what you
cut in the exercise is not necessarily what you cut in the manuscript.
```

**Genre/argument notes:** Best for overbuild and scope creep. Often the right answer is simply to cut, so this family should not be used when a direct cut decision is already obvious and accepted. In that case, the intervention is "cut" — no prompt needed.

### 7. Temporal

**Structural purpose:** Use time movement to expose commitment, consequence, or missing preparation.

**Target block types:** Cognitive, partial-manuscript uncertainty, consequence fog.

**Target state patterns:** Weak aftermath, unclear setup debt, inert reveal timing, absent downstream cost, unclear testimony consequence.

**Allowed constraint logic:** May move briefly to immediate aftermath, later memory, prior setup moment, or downstream implication while staying abstract.

**Forbidden / prescriptive drift signs:** Naming the future event that must happen, or inventing sequel content as if it were already chosen.

**Prompt skeleton:**
```
Move to [earlier / later] relative to [corridor] and track only what changed in cost,
knowledge, relationship, or burden. Then return and ask what the current draft must
earn. If the temporal exercise produces material you want to keep, you can — it's
yours.
```

**Genre/argument notes:** Useful when the writer cannot tell what a scene or claim corridor is obligating. In argument work, temporal prompts are better for consequence chains than for evidence gathering. **Riskiest family for inventing future canon** — the coach must frame the temporal move as hypothetical, not as draft material.

---

## Mapping: Diagnostic_State.md → Prompt Families

| Diagnosed pattern | Best-fit families | Why | Prompt or suppress? |
|-------------------|-------------------|-----|---------------------|
| Character agency collapse | Constraint, Inversion, Perspective | Writer must see how to make the character drive the turn | Prompt often useful |
| Pacing drag from scene sprawl | Scale-shift, Deletion | Issue is proportion and load-bearing matter | Prompt often useful |
| Tonal drift | Isolation, Constraint | Writer needs to separate contract from local scene habit | Prompt useful when energy is available |
| Reveal flatness / inert information flow | Temporal, Perspective | Writer needs to test what changes when information lands differently | Prompt useful |
| Scope creep / subplot overload | Deletion | Issue is usually trimming, not discovering more | Sometimes useful; often cutting is enough |
| Partial-manuscript structural uncertainty | Temporal, Constraint | Writer needs a bounded next move, not a global plan | Prompt useful |
| Fear of commitment to the hard scene | Existing exercise library first; then Constraint or Inversion | Writer may need Permission Draft before structural prompting | Conditional |
| Exhaustion or burnout | None | More mediation worsens the state | **No prompt** |
| Accumulated-feedback saturation | None or one very low-load Isolation | Writer needs less overlay, not more | **Usually no prompt** |
| Straightforward cut decision already accepted | None | Discovery is over; execution is straightforward | **No prompt — just cut** |
| Factual or continuity error | None | Issue is correction, not invention | **No prompt — fix directly** |

---

## Mapping: Argument_State.md → Prompt Families

| Diagnosed pattern | Best-fit families | Why | Prompt or suppress? |
|-------------------|-------------------|-----|---------------------|
| `CL` instability / blurred C0 | Isolation, Constraint | Writer needs to stabilize one claim corridor at a time | Prompt often useful |
| `WR` gap / weak inferential bridge | Isolation, Perspective, Constraint | Writer must explore why the evidence should count, not just restate the claim | Prompt often useful |
| `OB` avoidance / red-team vulnerability | Perspective, Inversion | Writer needs a hostile-reader or objection-facing lens without sentence drafting | Prompt useful |
| `AC` mismatch / persuasion sequence problem | Scale-shift, Perspective | Writer needs to test order and audience pressure, not content invention | Prompt useful |
| Testimony containment problem | Isolation, Constraint | Writer must separate observation, interpretation, and recommendation | Prompt useful |
| Evidence corridor too thin | None or minimal planning prompt | Work is evidence acquisition, verification, or narrowing claim | **Usually no writing prompt** |
| Pure compression in a sound piece | Deletion, Scale-shift | Task is to keep logic while reducing surface volume | Prompt useful |
| Warrant gap in hostile-audience context | Constraint, Perspective | Writer must test whether the bridge holds under adversarial pressure | Prompt useful |
| `DI` failure / dialectical integrity breakdown | Isolation, Inversion | Writer must separate their strongest case from their weakest engagement with opposition | Prompt useful |

---

## No-Prompt Zones

These states explicitly suppress prompt generation. The module must recognize them.

| State | Why prompting is wrong | Better move |
|-------|----------------------|-------------|
| Physiological depletion / burnout | More structure becomes more pressure | Rest, rescope, lighter task, deadline honesty |
| Clear evidence-acquisition gap | Work is research, not writing | Evidence queue, verification, narrowing claim |
| Accepted cut decision | Discovery is over; execution is straightforward | Cut and propagate consequences |
| Factual or continuity error | Issue is correction, not invention | Fix directly |
| Accumulated-feedback saturation | Another layer of mediation worsens the state | Strip back support, reread, outside reader |
| Locked Keep/Cut decision writer has not reopened | Prompting would quietly relitigate a settled choice | Respect the lock |
| State file missing or empty | No diagnostic basis for structural prompts | Route to `/start` or `/diagnose` |

---

## Hard Constraints

Any build of this module must enforce these. They are not optional niceties.

1. `Diagnostic_State.md` or `Argument_State.md` must exist before structurally informed prompts are offered. No state, no prompt.
2. One prompt per corridor by default. Two only when the first is explicitly exhausted.
3. No prompt when the correct next step is rest, cutting, evidence gathering, or reassessment.
4. No prompt may specify new plot events, relationship outcomes, policy claims, factual assertions, or paragraph-level wording.
5. Every prompt must pass the 5-part firewall test. Failure on two or more conditions blocks the prompt.
6. Every prompt must include a clinamen clause: explicit permission to break the constraint if the writer finds something better.
7. Every prompt must end with a structural self-check or comparison criterion.
8. Every prompt must be framed as low-stakes and disposable unless the writer chooses otherwise.
9. Prompts must respect locked Keep/Cut decisions unless the writer explicitly reopens them.
10. Overmediated states should trigger prompt suppression or prompt minimization, not prompt escalation.
11. **Nocebo inoculation:** Every block diagnosis or structural problem identification must acknowledge the writer may already be handling this. Frame diagnostics as one possible lens, not definitive truth. (Basis: Sandra et al. 2025; expertise reversal effect, Kalyuga et al. 2003.)
12. Prompt families should be internally curated; the writer should not browse a giant menu as the default experience.
13. The coach must be allowed to say "you do not need a prompt for this problem."
14. The module must not generate text-work just because it can. Prompt generation is justified only when it reduces the specific blockage mechanism.

---

## Integration with Existing Coaching Infrastructure

### What changes in the coaching protocol

The Stuck-Point Diagnosis section currently has a three-way split (cognitive / motivational / physiological) with interventions by type and a 6-exercise library. The build replaces this with:

1. **Expanded 8-type taxonomy** with the two-step diagnosis protocol (gate question → refinement question)
2. **Prompt suitability assessment** after block-type refinement
3. **Structural prompt insertion** as a new intervention class alongside reframe, decompose, and the existing exercise library
4. **Perfectionism modifier** detection and adjustment protocol

The existing 6 exercises remain unchanged. They become the primary intervention for motivational/emotional blocks (types 2, 5 partially, 7 partially). Structural prompts become the primary intervention for cognitive, decisional, aesthetic, and stage-mismatch blocks (types 1, 4, 6, 8).

### Intervention selection flow

```
Writer reports stuck
    │
    ▼
Gate diagnosis: cognitive? motivational? physiological? other?
    │
    ▼
Refinement: which sub-type? (decisional? identity? aesthetic? feedback-saturated? stage-mismatch?)
    │
    ▼
Perfectionism modifier check: is perfectionism amplifying?
    │
    ▼
Intervention selection:
    ├─ Physiological/environmental → coach away from desk (no prompt)
    ├─ Accumulated-feedback → strip support, Sit with Draft, outside reader (usually no prompt)
    ├─ Motivational/avoidance → existing exercise library (Name Resistance, Permission Draft, etc.)
    ├─ Identity/vision threat → reframe first, then low-stakes prompt if needed (clinamen critical)
    ├─ Cognitive overload → structural prompt (Constraint, Isolation, Scale-shift)
    ├─ Decisional/equipoise → structural prompt (Scale-shift, Temporal, Constraint)
    ├─ Aesthetic/execution gap → Isolation prompt to practice specific skill
    └─ Stage-mode mismatch → reframe first, then Scale-shift if needed
    │
    ▼
If prompt selected: generate from family + corridor + state
    │
    ▼
Verify: 5-part firewall test
    │
    ▼
Embed in session plan (Structural Experiment section)
```

### What changes in the session plan template

Add an optional section after "What it needs" and before "What 'done' looks like":

```markdown
### Structural Experiment (optional — included when coach diagnoses a block amenable to prompting)

**Block diagnosis:** [type + refinement, e.g., "Cognitive overload — too many interdependent variables in the Act 2 restructuring"]

**Prompt family:** [e.g., Isolation]

**Prompt:**
[Full prompt text, satisfying all 5 firewall conditions, including clinamen clause and self-check]

**Framing:** This is low-stakes exploration, not new canonical draft material. The exercise is disposable. If it moves you, keep it. If it doesn't, the information about what didn't work is the value.

**Note:** You may already be handling this structural problem through your own process. This prompt is one possible way in, not the only one.
```

The section appears only when a structural prompt is warranted. Most session plans will not include it. The "Note" line is the nocebo inoculation, present every time.

### What changes in the argument coaching protocol

The argument coaching protocol (`argument-coaching-protocol.md`) gets the same expansion: 8-type taxonomy applied to argument revision, prompt families mapped from `Argument_State.md` codes, and the same session-plan insertion point.

---

## Family Validation Matrix

For implementation QA. Each family is screened against three design tests.

| Family | Diagnostic specificity | Firewall compliance | Cognitive load | Notes |
|--------|----------------------|---------------------|----------------|-------|
| Constraint | Strong | Strong | Conditional | Excellent when the corridor is sharp; overwhelming if the corridor is too broad |
| Inversion | Medium to strong | Strong | Strong | Best when the draft's habitual move is already visible |
| Isolation | Strong | Strong | Strong | Safest family for complex states and argument work |
| Scale-shift | Strong | Strong | Strong | Usually lowers load quickly |
| Perspective | Medium | Conditional | Conditional | High value, but easiest family to drift into content invention |
| Deletion | Strong | Strong | Strong | Best when the issue is excess, not absence |
| Temporal | Medium | Conditional | Conditional | Powerful for consequence fog, risky for inventing future canon |

**Selection rule:** If a family rates only "medium" on specificity and "conditional" on load for the current state, the coach should prefer a reframe or no prompt unless the writer explicitly wants an experiment.

---

## Scenario Validation Set

The build should be tested against these minimum scenarios.

### 1. Fiction structural blockage
- **Input:** `Diagnostic_State.md` with agency collapse in Act 2
- **Expected:** Coach diagnoses cognitive overload, selects Constraint family, embeds prompt in session plan, prompt passes all 5 firewall tests
- **Suppress check:** If the writer also reports exhaustion, prompt should be suppressed

### 2. Partial-manuscript forward-writing block
- **Input:** Incomplete draft, stall diagnosis is structural uncertainty
- **Expected:** Coach selects Temporal or Constraint, frames as exploratory, ties to next drafting decision
- **Suppress check:** If uncertainty is deep (writer can't name any next scene), hand off to Pre-Writing

### 3. Argument revision blockage
- **Input:** `Argument_State.md` with WR gap and OB avoidance
- **Expected:** Coach selects Isolation for WR gap, Perspective for OB avoidance, embeds one per session plan (not both simultaneously)
- **Suppress check:** If evidence corridor is thin, no writing prompt

### 4. Accumulated-feedback / overmediated writer
- **Input:** Writer says "I can't read my own work anymore without hearing the diagnosis"
- **Expected:** Coach diagnoses accumulated-feedback block, suppresses all structural prompts, offers Sit with the Draft or Inventory What Works from existing library
- **Failure mode:** Generating a structural prompt for this writer

### 5. Decisional block with perfectionism amplifier
- **Input:** Writer stuck between two valid restructuring options, also showing perfectionism signals
- **Expected:** Coach diagnoses decisional block + perfectionism modifier, selects Scale-shift (compress both options), adds Permission Draft framing, clinamen clause emphasized
- **Suppress check:** If the writer has been through multiple rounds of the same decision, check for accumulated-feedback saturation

### 6. Identity block during revision
- **Input:** Writer resists cutting a subplot because "it's the heart of the book"
- **Expected:** Coach diagnoses identity/vision threat, reframes first (externalize manuscript from self, name grief), then offers low-stakes Perspective prompt only if reframe is insufficient
- **Failure mode:** Jumping to a structural prompt without reframing first

### 7. Testimony containment in argument work
- **Input:** `Argument_State.md` with testimony bleed (observation, interpretation, recommendation layers mixed)
- **Expected:** Coach selects Isolation prompt: "Separate [testimony corridor] into observation, interpretation, and recommendation. Which layer is carrying more burden than it should?"
- **Suppress check:** If the writer needs to acquire more evidence, no writing prompt

---

## Theoretical Grounding (Summary)

Full research is in the companion documents. This section names the key findings that govern design decisions.

### Findings that justify the module

- **Constraint-based creativity:** Moderate constraints optimize creativity; too few cause paralysis, too many cause rigidity (Acar, Tarakci, van Knippenberg, 2019: 145-study review; Stokes, 2005/2025: paired preclude-promote constraints; Tromp, 2022: focusing > exclusionary constraints).
- **Heuristics define problem spaces, not products:** Flower and Hayes (1977/1981); Lauer on invention heuristics; Burns on computer-assisted writing instruction.
- **Carryover effect:** Writers under constraints continued producing more creative output after constraints were removed (Haught-Tromp, 2016/2017). Suggests structural prompts build permanent capacity.

### Findings that constrain the module

- **Expertise reversal effect:** Instructional techniques effective for novices can harm experienced learners by forcing reconciliation with redundant external guidance (Kalyuga et al., 2003). APODICTIC's users are intermediate-to-advanced. Detailed prescriptive scaffolding will be counterproductive.
- **CISD parallel:** Critical Incident Stress Debriefing worsened outcomes by forcing premature contact with trauma (Bisson et al., 1997: 26% PTSD vs. 9% controls). Parallel: APODICTIC risks deepening awareness of structural problems and solidifying blocks rather than enabling resolution.
- **Nocebo effect:** Awareness workshops caused false self-diagnosis (Sandra et al., 2025). Nocebo education halved the effect. Direct implication: pair every diagnosis with acknowledgment that the writer may already be handling this.
- **Choice overload:** 6 options produced 10× more engagement than 24 (Iyengar and Lepper, 2000). One prompt, not a menu.
- **Satisfaction ≠ effectiveness:** Writers may like prompts while prompts impair manuscript work (Kagee, 2002 on CISD satisfaction reports).
- **Over-scaffolding:** Fisher and Frey: "students who have been over-scaffolded may acquire information sufficiently to pass a test, but they don't have the means to knowledge-seek and problem-solve in new and novel situations." Three layers of mediation (diagnosis + session plan + exercise) is the maximum before scaffolding becomes noise.

### Findings about gaps

- **Revision-specific prompt design is virtually unstudied.** Nearly all heuristic research addresses first-draft generation.
- **No empirical taxonomy of writer's block exists for creative fiction writers in revision.**
- **The aesthetic block is technically not writer's block** under Rose's (1984) definition (which excludes skill deficits). This matters for intervention design: the treatment is craft instruction, not cognitive restructuring.
- **Workshop damage is documented but never empirically measured.**

---

## File Map

All paths relative to the apodictic repo root.

### Files to create

| File | What it is |
|------|-----------|
| `plugins/apodictic/skills/revision-coach/references/writers-block-taxonomy.md` | Expanded 8-type taxonomy with diagnosis protocol, perfectionism modifier, intervention selection flow. Referenced by coaching protocol. |
| `plugins/apodictic/skills/revision-coach/references/structural-prompt-library.md` | Internal prompt-family library: 7 families with specifications, skeletons, firewall test, validation matrix, no-prompt zones. The coach reads this; the writer does not browse it directly. |

### Files to patch

| File | What changes |
|------|-------------|
| `plugins/apodictic/skills/revision-coach/references/coaching-protocol.md` | Replace three-way Stuck-Point Diagnosis section with expanded taxonomy reference. Add structural prompt as a new intervention class. Add nocebo inoculation requirement. Keep existing exercise library intact. |
| `plugins/apodictic/skills/revision-coach/references/session-plan-template.md` | Add optional "Structural Experiment" section to session plan template. |
| `plugins/apodictic/skills/revision-coach/references/argument-coaching-protocol.md` | Add argument-specific prompt mapping and expanded taxonomy for argument revision blocks. |
| `plugins/apodictic/skills/revision-coach/references/argument-session-plan-template.md` | Add optional "Structural Experiment" section to argument session plan template. |
| `plugins/apodictic/skills/revision-coach/SKILL.md` | Add trigger words: "writer's block," "stuck," "blocked," "can't write," "prompt," "exercise," "rut," "stalled," "paralyzed," "choice paralysis," "execution gap," "too much feedback." |

### Research files (already exist, do not modify)

| File | What it is |
|------|-----------|
| `docs/writers-block-rut-breaking-level-setting-codex54.md` | Level-setting research (Codex) |
| `docs/writers-block-prompt-inventory-codex54.md` | Prompt inventory and firewall matrix (Codex) |
| `docs/research-spec-writers-block.md` | Original problem statement with codex54 completion status |

### Research files (to archive in docs/)

| File | What it is |
|------|-----------|
| `docs/writers-block-research-opus46.md` | Opus 4.6 research (the uploaded file, should be archived for reference) |
| `docs/writers-block-research-gemini.md` | Gemini research (the uploaded file, should be archived for reference) |

---

## Build Order

1. Create `writers-block-taxonomy.md` (the expanded taxonomy, diagnosis protocol, intervention selection flow)
2. Create `structural-prompt-library.md` (the 7 families, skeletons, firewall test, mapping tables, no-prompt zones, validation matrix)
3. Patch `coaching-protocol.md` (replace three-way section, add structural prompt intervention class, add nocebo inoculation)
4. Patch `session-plan-template.md` (add Structural Experiment section)
5. Patch `argument-coaching-protocol.md` (add argument-specific taxonomy and prompt mapping)
6. Patch `argument-session-plan-template.md` (add Structural Experiment section)
7. Patch `revision-coach/SKILL.md` (add trigger words)
8. Archive research files in `docs/`

Steps 1 and 2 are independent. Steps 3–7 depend on 1 and 2. Step 8 is independent.

---

## What This Module Does NOT Do

For avoidance of doubt:

- Does not provide a standalone `/prompt` or `/exercise` command
- Does not expose the prompt library directly to the writer as a browsable menu
- Does not generate prompts without a diagnostic state
- Does not prescribe plot events, argument content, or aesthetic choices
- Does not replace the existing 6-exercise library for motivational blocks
- Does not track prompt "effectiveness" through satisfaction ratings (satisfaction ≠ effectiveness)
- Does not attempt to detect or treat clinical conditions (depression, anxiety, ADHD)
- Does not cross the firewall. Ever.
