---
name: pre-writing-pathway
description: >
  Pre-writing pathway for writers without a manuscript. Guide from idea to
  draft-ready structure. Use when the user asks to "plan a story," "outline
  a novel," "develop a premise," "figure out my book," "structure my idea,"
  or any request for help moving from concept to ready-to-draft planning.
version: 1.0.5
---

# Pre-Writing Pathway

## Purpose

Guide a writer from "I have an idea" to "I have enough structure to start drafting." This pathway serves writers who don't yet have a manuscript — the would-be novelist, the writer between projects, the person with a premise but no plan.

The Firewall still applies: the pathway helps the writer discover what they want to write through questions, frameworks, and structural options. It does not invent plot, characters, scenes, or prose.

---

## When to Activate

- Writer has no manuscript (or only scattered notes/fragments)
- Intake router identifies: "I have an idea but haven't started writing"
- Writer asks for help planning, outlining, or "figuring out" a book
- Writer has finished one project and wants to start the next

**Does NOT activate for:** Writers with a complete draft (route to Core DE), writers stuck mid-draft (route to Core DE with partial-manuscript intake flag — see §9 capability gap: "Partial Manuscript Diagnostic"), writers with a draft needing revision (route to Core DE revision round).

---

## Router Integration

When entered via `/start`, accept router output as pre-filled context:

```
artifact: [idea | fragments | partial | full_draft | series]
goal: [draft | repair | submit]
concern: [specific concern or general]
constraints: [list]
operator: [author | editor | facilitator | team]
```

Use prefilled values to skip redundant intake prompts:

- `artifact=idea` + `goal=draft`: run standard Phase 0 -> Phase 6 flow.
- `artifact=fragments`: start at Phase 1 Seed Inventory with fragment consolidation emphasis.
- `artifact=partial` + rethink route: run pre-writing re-entry mode; import known structural decisions before Phase 2+.

Do not re-ask "what do you have?" when router already answered it unless the user indicates the classification is wrong.

---

## Phase 0: Writer Mode Calibration

Before anything else, identify how this writer thinks. The same pathway content applies either way, but the order, pressure, and tolerance for open fields changes.

### Two Modes

| Mode | Signal | Pathway behavior |
|------|--------|-----------------|
| **Architecture-first** | "I need to know where I'm going before I write." Wants structure, outlines, clear endpoints. Uncomfortable starting without a plan. | Run phases in order. Press for specificity. Treat open fields as gaps to close. |
| **Discovery-first** | "I'll figure it out as I write." Resists outlines. Knows the feeling or a scene but not the shape. | Run Phase 1 (Seed Inventory) fully, then offer phases 2–4 as *available* rather than *required*. Mark more fields as exploratory. Don't press for premature closure. |

### Detection

Don't ask "Are you a plotter or a pantser?" — that's a false binary and writers will self-categorize inaccurately. Instead, listen for signals during Phase 1. If unclear, ask:

"When you've written something you're proud of before — did the structure come first, or did you find it afterward?"

### What Changes

- **Architecture-first writers** get the full sequential pathway. Each phase builds on the last. The Structural Plan (Phase 5) should have minimal open fields.
- **Discovery-first writers** get the Seed Inventory and Controlling Idea exploration, then a lighter-touch pass through Phases 3–4 where "exploratory" and "provisional" are expected, not failures. The Structural Plan includes more open questions and the Complexity Budget (Phase 4B) emphasizes what to *leave out* of the first draft rather than what to lock in.

**Record the mode in the Structural Plan header.** It affects how the Re-Entry Diff Protocol interprets divergences: a discovery writer's manuscript *should* diverge significantly from the prospective contract; an architecture writer's divergences are more diagnostically interesting.

---

## Phase 1: What Do You Have?

The writer arrives with *something*, but it's different for each person. The first conversation identifies what's already present and what's missing.

**Don't ask the writer to fill in a form.** Ask them to talk about their idea. Then map what they say onto the schema fields below. Tell them what you heard and what's still open.

### The Seed Inventory

Listen for which of these the writer already has:

| Seed | What it sounds like | What it implies |
|------|-------------------|-----------------|
| **Premise** | "What if a woman discovered her therapist was editing her memories?" | Central tension, possibly genre, possibly controlling idea direction |
| **Character** | "I want to write about a retired detective who can't stop investigating" | Protagonist, want, possibly lie, possibly spine family |
| **World** | "It's set in a space station where gravity is rationed" | Setting, possibly novum, possibly genre (SFF), possibly constraint spine |
| **Feeling** | "I want the reader to feel like the ground keeps shifting" | Reader promise, possibly tension type (epistemic), possibly genre (horror, literary) |
| **Scene** | "I keep imagining this dinner party where everything goes wrong" | A structural moment without a surrounding architecture |
| **Theme** | "I want to write about how institutions make people complicit" | Controlling idea direction, possibly spine (corruption), possibly anti-idea |
| **Genre instinct** | "I want to write a cozy mystery" | Genre, reader promise, contract constraints, relevant modules |
| **Comp** | "Something like Gone Girl but from the husband's perspective" | Tone, structure, genre, reader expectations |

Most writers arrive with 1-3 of these. Some arrive with fragments of several. The inventory tells the pathway which phases to emphasize and which to abbreviate.

**After the inventory, report back:**

"Here's what I hear in your idea: [restate in structural terms]. The pieces we'd need to develop before you start drafting are: [list the empty schema fields that matter for their genre/spine]. Want to work through those?"

### Uncertainty/Assumption Ledger

From Phase 1 onward, maintain a running ledger that tracks the confidence level of every structural decision. Each field in the eventual Structural Plan gets one of three tags:

| Tag | Meaning | Implication |
|-----|---------|-------------|
| **Decided** (High confidence) | Writer has committed to this; it's load-bearing | Treat as fixed unless writer explicitly revisits |
| **Provisional** (Medium confidence) | Best current hypothesis; may change with drafting | Test against early pages; revisit at 10K-word checkpoint |
| **Unknown** (Low confidence) | Writer doesn't know yet, and that's fine | Don't press. Flag for discovery during drafting. |

**Dependencies:** When a provisional or unknown field is load-bearing for another decision, note the dependency. Example: "Spine selection is provisional because controlling idea is still exploratory — if the controlling idea shifts, the spine may need to change."

The ledger appears in the Structural Plan output (Phase 5) and feeds the Re-Entry Diff Protocol (Phase 6) — it tells the future diagnostic which divergences were *expected* and which are surprises.

---

## Phase 2: Controlling Idea

This is the most important phase. A writer who knows their controlling idea can make structural decisions; a writer who doesn't will wander.

**Don't ask "What's your theme?" — that's too abstract.** Ask:

1. "When the reader finishes your book, what should they believe about [the topic/world/relationship] that they didn't believe before?" → This surfaces the *value* half of the controlling idea.

2. "Why does that turn out to be true in your story? What causes it?" → This surfaces the *cause* half.

3. "What's the opposite claim — what does your book argue *against*?" → This is the anti-idea. It's often easier for writers to articulate what they're pushing back against than what they're asserting.

**Format:** [Value] + [Cause]

**Examples to offer if the writer is stuck:**
- "Justice prevails when individuals sacrifice personal safety for collective truth."
- "Love fails when the lovers refuse to be known."
- "Power corrupts when accountability exists only as performance."
- "Identity dissolves when the body's responses can no longer be trusted as evidence of self."

**For writers who genuinely don't know yet:** That's fine. Record the controlling idea as **Unknown** in the ledger: "writer is discovering through the material." Flag for revisit at 10,000+ words. Some writers find their controlling idea by writing, not by planning. The pathway should accommodate this without treating it as a failure.

**For open or ambiguous endings:** State the pressure applied to a question, not an answer. "The book asks whether compliance obtained through institutional pressure is real cooperation, and refuses to resolve the question."

---

## Phase 3: Protagonist Engine

Build the minimum viable character architecture. Not a full character portrait — just enough to generate scenes.

### Core Questions (in order of usefulness)

**The Want:** "What does your protagonist want at the start of the story — the thing they'd say out loud if you asked them?"

**The Need:** "What do they actually need that they can't see yet?" (If the writer doesn't know: "What would make them a more complete person, even if getting it would terrify them?")

**The Lie:** "What false belief lets them function? What would fall apart if they stopped believing it?"

**The Fear:** "What are they organized around avoiding? Not a phobia — a life-organizing fear."

**Want-Need tension check:** If the writer can easily have both want and need satisfied simultaneously, there's no engine. Flag it: "Right now your protagonist can get what they want AND what they need without conflict. That usually means either the want needs to obstruct the need, or the need isn't deep enough yet."

### What You're Building

```
PROTAGONIST: [name or placeholder]
SURFACE WANT: [conscious goal]
DEEP NEED: [unconscious requirement]
THE LIE: [false belief that organizes their life]
THE FEAR: [what they're built around avoiding]
WANT-NEED TENSION: [how pursuing the want blocks the need]
```

**This is NOT a character sheet.** Don't ask about hair color, occupation, backstory, or personality traits. Those are content. This is structural: what drives the character, what blocks them, what must change.

**For ensemble casts:** Build the engine for the protagonist only. If the writer insists on multiple POV characters, build engines for up to 3 and identify whose transformation is the spine. ("Both" is a valid answer only if the book has a clear structural mechanism for weaving two arcs — flag the complexity.)

### Readiness Gate 1: Storyable

Before proceeding to spine selection, test whether the raw materials cohere into something that can generate scenes. The **storyable gate** requires:

1. **Premise + Protagonist Engine + Core Tension are minimally coherent.** The protagonist's want/need conflict connects to the premise in a way that produces situations, not just a static condition.
2. **At least one of:** a controlling idea (even provisional), OR a clear anti-idea, OR an ending instinct ("I know it ends with...").
3. **The idea is *storyable*, not just *thinkable*.** Test: "Can you imagine a scene where this tension plays out between characters?" If the writer can only articulate the idea as an essay thesis, it may not yet be a story.

**If the gate fails:** Don't proceed to spine selection. Instead, diagnose what's missing. Common failure modes: the premise is a situation without conflict ("interesting world, but what goes wrong?"), the protagonist has no engine ("interesting person, but what do they want that they can't easily have?"), or the tension is intellectual but not dramatic ("the theme is clear, but where's the human cost?").

**If the gate passes:** Proceed to Phase 4. The writer has enough to start making structural choices.

---

## Phase 4: Spine Selection

Route the writer toward a structural shape for their story. This uses the Plot Selection & Coaching framework but with a gentler vocabulary.

### The Entry Question

Don't say "What's your narrative spine?" Say:

"What kind of *experience* do you want this to be for the reader? Pick the closest:"

| Experience | Maps to spine family | Follow-up |
|------------|---------------------|-----------|
| "A building sense of dread / things getting worse" | Spiral, Fichtean, Pressure Cooker | "Does the protagonist lose ground each round, or do the crises just keep coming?" |
| "A mystery — figuring something out" | Mystery, Revelatory, Conspiracy, Puzzle Box | "Does the reader solve it alongside the character, or ahead of them?" |
| "A relationship — two people pulled together and pushed apart" | Courtship, Seduction, Betrayal-of-Self | "Does it end in union, separation, or transformation?" |
| "A journey or quest — moving toward a goal" | Quest, Hero's Journey, Save the Cat | "Does the destination matter, or does the protagonist change along the way?" |
| "A moral fall or rise — someone becoming better or worse" | Corruption, Redemption, Bildungsroman | "Is the change chosen or inflicted?" |
| "Something that loops or repeats — patterns and variations" | Fugue, Loop, Wave/Pulse | "Does the reader's understanding change each time, or does the character's?" |
| "I don't know — I just have this feeling" | Start from genre and controlling idea | Route to diagnostic: "Let's work backward from your ending instinct." |

### Option Architecture: Don't Converge Too Early

Once a spine family is identified, **present 2–3 viable structural candidates** with their tradeoffs — not a single recommendation. For each candidate, state:

1. **What it does well** for this particular story's materials
2. **What it costs** — the structural tradeoff or risk
3. **What it demands** of the writer (e.g., "This spine requires you to know the ending before you start" or "This spine works by accumulation, so it needs patience in the first third")

Example for a writer with a corruption premise:

> **Option A: Spiral** — The protagonist returns to similar situations with less each time. *Good for:* showing gradual degradation the reader sees before the character does. *Cost:* Risk of monotony if degradation doesn't escalate in kind, not just degree. *Demands:* You need to know the bottom — how far does the fall go?
>
> **Option B: Pressure Cooker** — External constraints tighten while the protagonist's options shrink. *Good for:* building dread through environment. *Cost:* The protagonist can feel passive if the constraints do all the work. *Demands:* A clear external mechanism that tightens believably.
>
> **Option C: Betrayal-of-Self** — The protagonist chooses each step of their own corruption. *Good for:* moral complexity — no one to blame but the protagonist. *Cost:* Risks reader alienation if the choices aren't psychologically legible. *Demands:* Deep interiority — the reader needs to understand why each choice felt rational at the time.

**Let the writer sit with options.** Don't push for an immediate decision. If they can't choose, that's diagnostic: they may need to draft some material before the spine reveals itself. Record "Spine: exploratory" and move to Phase 4B.

### For Writers Who Resist Structure

Some writers will say "I don't want to be constrained by a formula." Respond honestly:

"The spine isn't a formula — it's a description of what your story is already trying to do. Every story has a shape; naming it lets you build scenes that serve it instead of fighting it. You can always change the spine once you're drafting. This is a starting hypothesis, not a commitment."

If they still resist, respect it. Skip to Phase 4B with whatever structural fragments exist. Some writers need to discover structure through drafting, and that's a legitimate creative process. The pathway should accommodate it.

### Phase 4B: Complexity Budget

Before moving to the Structural Plan, set explicit scope caps for the first draft. This prevents the common failure mode where a pre-writing plan generates more complexity than a writer can execute.

**Ask directly:**

"For your first draft, let's set some boundaries. These aren't permanent — they're guardrails to keep the first draft from collapsing under its own weight."

| Dimension | Cap | Why it matters |
|-----------|-----|---------------|
| **POV characters** | Recommend 1–2 for a first novel; flag 3+ as high complexity | Each POV needs its own engine, voice, and arc. More POVs = more structural plates to spin. |
| **Subplots** | Recommend 1–2 that serve the main spine; flag 3+ | Subplots that don't test, mirror, or complicate the controlling idea are structural weight without structural function. |
| **Timeline complexity** | Linear default; flag non-linear as a deliberate choice that needs structural justification | Non-linear timelines double the reader's cognitive load and require the juxtaposition itself to create meaning. |
| **World-building scope** | Flag when world-building threatens to displace character and plot | SFF writers especially: the novum should generate story, not replace it. |

**For discovery-first writers:** Frame the budget as "what to leave out of the first draft" rather than "what to plan." The point is the same — reduce scope to executable size — but the framing respects their process.

**Record the complexity budget in the Structural Plan.** It becomes a checkpoint during the Re-Entry Diff: if the manuscript exceeds the budget, that's either intentional expansion (good — the writer found more story) or scope creep (check whether the structure can bear the weight).

---

## Phase 5: Structural Plan

Produce a document the writer can draft against. Not a prescriptive beat sheet — a structural skeleton that names what the story needs without filling in content.

### Readiness Gate 2: Draftable

Before generating the Structural Plan, test whether the writer has enough to start writing. The **draftable gate** requires:

1. **A spine candidate** (even if provisional or one of 2–3 options under consideration)
2. **An ending instinct** — not a detailed ending, but a directional sense: "It ends in separation," "She chooses the lie," "The question stays open." If the writer has no ending instinct at all, flag this as a structural risk.
3. **Arc states** — at minimum: starting state → one turning point → ending state. The full state sequence can have gaps, but the trajectory must be discernible.
4. **Known unknowns are identified and accepted.** The writer knows what they don't know yet and has a plan for discovering it (usually: "I'll figure it out by writing").

**If the gate fails:** Don't produce a hollow Structural Plan. Instead, identify what's missing and either work through it (architecture-first writer) or send the writer to draft with a Minimal Viable Plan.

### Minimal Viable Plan (Discovery-First Fallback)

When the draftable gate fails for a discovery-first writer who has enough to start writing but not enough for a full Structural Plan, produce a short prose document — not a structured template. The MVP should read like a conversation summary, not a form.

**Contents (in prose, not schema):**

1. What the writer has so far — restate the protagonist engine components, controlling idea direction, and core tension in the writer's own language where possible.
2. What the writer is looking for — the open questions they expect drafting to answer.
3. Scope guardrails — any complexity caps from Phase 4B, stated as practical advice ("Start with one POV; add a second only if the first 10K words demand it").
4. When to come back — the three return triggers (10K-word checkpoint, stuck, complete draft).

**File format:** Save as `[Project]_MVP_[runlabel].md` in `Outputs/[Project]/`, following Core DE naming conventions. Header line: `APDE | Pre-Writing MVP | [Date]`. Footer line: `Discovery scaffold — not a prospective contract.`

The MVP is *not* a prospective contract. It doesn't feed the Re-Entry Diff Protocol directly — when the writer returns, standard intake runs from scratch, but the MVP file provides context for what the writer was trying to find.

**If the gate passes:** Generate the full Structural Plan below.

### Output: Pre-Drafting Structural Plan

Save as `[Project]_Structural_Plan_[runlabel].md` in `Outputs/[Project]/`.

```markdown
# Pre-Drafting Structural Plan: [Title or Working Title]

## Writer Mode: [Architecture-first / Discovery-first]

## The Contract (Prospective)

GENRE/SUBGENRE: [from intake]
READER PROMISE: [from intake]
PRIMARY TENSION TYPE: [external / relational / epistemic / moral]
ENDING TYPE: [closed / open / ambiguous / denial-of-catharsis]
TONE COMPS: [from intake]
STRUCTURE COMPS: [from intake]
NON-NEGOTIABLES: [from intake]

## Controlling Idea

[Value] + [Cause]

**Anti-idea:** [What the book is NOT arguing]

**Status:** [Decided / Provisional / Unknown — if Unknown, revisit after 10K words]

## Protagonist Engine

PROTAGONIST:
SURFACE WANT:
DEEP NEED:
THE LIE:
THE FEAR:
WANT-NEED TENSION:

## Structural Shape

PRIMARY SPINE: [name] — [one-sentence description of how it works]

**Alternative considered:** [name] — [why it was set aside, and under what conditions it might be revisited]

**Key structural moments this spine requires:**
- [Moment 1]: [functional description, not content]
- [Moment 2]: [functional description]
- [Moment 3]: [functional description]
- [Moment 4]: [functional description]

**Logic gates to test while drafting:**
- [Gate 1 as a question the writer can ask of their own pages]
- [Gate 2]

**Arc expressed as state sequence:**
[Believes lie] → [Lie challenged by ___] → [Lie fails when ___] → [Confronts truth] → [Chooses ___]

## Complexity Budget

POV CHARACTERS: [count and names/roles]
SUBPLOTS: [count and structural function of each]
TIMELINE: [linear / non-linear — if non-linear, structural justification]
WORLD-BUILDING SCOPE: [contained / expansive — if expansive, how it serves story]

## Uncertainty Ledger

| Field | Status | Confidence | Dependencies |
|-------|--------|------------|-------------|
| Controlling idea | [Decided/Provisional/Unknown] | [H/M/L] | [what depends on this] |
| Spine | [Decided/Provisional/Unknown] | [H/M/L] | [what depends on this] |
| Ending type | [Decided/Provisional/Unknown] | [H/M/L] | [what depends on this] |
| Protagonist engine | [Decided/Provisional/Unknown] | [H/M/L] | [what depends on this] |
| [other fields as needed] | | | |

## Hard Risks

**The strongest structural case against this plan:**
- [Risk 1 — the thing most likely to make this story fail, stated without softening]
- [Risk 2 — the second most dangerous structural vulnerability]

This section is required even when the plan feels solid. If the pathway cannot identify hard risks, that itself is a risk — it means the analysis isn't deep enough.

## Open Questions

- [Things the writer still needs to figure out]
- [Decisions deferred until drafting reveals more]
- [Structural risks specific to this spine/genre combination]

## What to Watch For

**Structural risks for this combination:**
- [Risk 1 — e.g., "Spiral stories risk monotony if degradation doesn't escalate in kind, not just degree"]
- [Risk 2]

**When to come back for diagnosis:**
- After 10,000 words: revisit controlling idea and spine selection
- After completing a draft: run Core DE with this contract as baseline

## Genre Modules and Audits (Pre-Selected)

**Genre calibration:** [selected]
**Tag audits:** [if applicable]
**Specialized audits to run on the completed draft:** [pre-selected based on genre/content]

---

*Framework: APODICTIC Development Editor (APDE)*
*Pathway: Pre-Writing*
*Writer mode: [Architecture-first / Discovery-first]*
*Status: Prospective contract — not yet validated against manuscript text*
*Date: [DATE]*
```

---

## Phase 6: Exit Ramp

The pathway ends when the writer has a structural plan (or, for discovery writers who don't pass the draftable gate, a Minimal Viable Plan). The next step is drafting — which the DE does not do.

**Closing message pattern:**

"You have a structural plan. The next step is writing. Some things to keep in mind:

- The plan is a hypothesis, not a cage. If the story pulls in a different direction, follow it. You can always come back and we'll diagnose what changed.
- The logic gates in your plan are checkpoints you can test as you draft. After a few chapters, ask yourself those questions.
- Check the Uncertainty Ledger — the fields marked Provisional and Unknown are where the plan *expects* you to discover something new. When you do, that's not failure; it's the plan working.
- When you have a complete draft — or when you're stuck — come back and we'll run the full diagnostic. The prospective contract you built today becomes the baseline we measure the manuscript against."

### Re-Entry Diff Protocol

When a writer returns with a draft after using the pre-writing pathway:

1. **Load the prospective contract** from the Pre-Drafting Structural Plan, including the Uncertainty Ledger and Complexity Budget.

2. **Run standard intake** (Draft-Then-Validate), but use the prospective contract as the starting hypothesis rather than inferring from scratch.

3. **Divergence classification:** For every field where the manuscript departs from the prospective contract, classify the divergence:

| Category | What it means | Diagnostic value |
|----------|--------------|-----------------|
| **Intentional evolution** | The writer found something better. The manuscript's version is stronger than the plan's. | Low concern. Update the contract to match the manuscript. Note what the writer discovered. |
| **Signal loss** | The plan had something the manuscript lost — a tension, an engine component, a reader promise that the draft doesn't deliver. | High concern. The writer may not realize they dropped it. Surface it: "Your plan promised X, but the manuscript does Y instead. Was that a deliberate choice?" |
| **Structural drift** | The manuscript wandered from the plan without clear intention — neither improving on it nor consciously abandoning it. | Medium concern. Common with discovery writers. Diagnose whether the drift found a better shape or whether the manuscript needs to choose a direction. |
| **Expected discovery** | The field was tagged Unknown or Provisional in the Uncertainty Ledger, and the manuscript filled it in. | No concern — this is the system working as designed. Record the writer's discovery. |

4. **Complexity Budget check:** Compare the manuscript's actual complexity (POV count, subplot count, timeline structure) against the budget. Flag overruns without assuming they're problems — the writer may have intentionally expanded scope.

5. **Update the contract** based on what the manuscript actually does, then proceed with Core DE.

This makes the pre-writing pathway's output directly useful to the post-writing diagnostic, creating a through-line from idea to revision. The Uncertainty Ledger prevents the diagnostic from treating every divergence as a problem — it distinguishes planned flexibility from unplanned drift.

---

## Design Notes

### Relationship to Existing Components

- **Plot Selection & Coaching** (plot-architecture skill): Phase 4 draws heavily on this. The pre-writing pathway adds a gentler vocabulary layer, option architecture (2–3 candidates instead of converging to one), and a complete workflow context. Plot-coach remains available as a standalone tool for writers who know they want structural help specifically.
- **Contract Schema** (core-editor skill): The pre-writing pathway produces a prospective version of the same contract, augmented with the Uncertainty Ledger and Complexity Budget. Same fields, different source (intent vs. text analysis).
- **Character Architecture** (specialized audit): Phase 3 uses a subset of the psychology engine. The full character architecture audit runs on a completed manuscript; this is the minimum viable version for pre-writing.
- **Intake Protocol**: The Re-Entry Diff Protocol (Phase 6) modifies standard intake by seeding it with the prospective contract and providing divergence classification.

### Output Artifact Conventions

The pre-writing pathway follows Core DE's existing naming convention: `[Project]_Artifact_[runlabel].md` stored in `Outputs/[Project]/`.

| Artifact | Filename pattern | Notes |
|----------|-----------------|-------|
| Full Structural Plan | `[Project]_Structural_Plan_[runlabel].md` | Prospective contract embedded within |
| Minimal Viable Plan | `[Project]_MVP_[runlabel].md` | Prose document; explicitly not a contract |
| Re-Entry Diff | `[Project]_Reentry_Diff_[runlabel].md` | Generated only when a full Structural Plan exists; MVP returns skip the diff and run standard intake |

The `[runlabel]` follows the same convention as Core DE outputs: date-based (`YYYY-MM-DD`), optionally with agent tag (e.g., `opus46_2026-02-20`).

When a writer returns with a draft and Core DE runs intake:
1. The structural plan / MVP file is read as context, not overwritten.
2. Core DE generates its own `[Project]_Contract_[runlabel].md` from the manuscript via standard intake.
3. The Re-Entry Diff compares the prospective contract (embedded in the structural plan) against the inferred contract and produces the diff artifact.

### What This Pathway Does NOT Replace

- The full intake protocol (which reads a manuscript and infers the contract)
- The full character architecture audit (which tracks characters through a completed text)
- Plot-coach as a standalone tool (for writers who want structural help without the full pathway)

### Firewall Compliance

The pathway asks questions and offers frameworks. It does not:
- Suggest plot events, scenes, or specific story content
- Write outlines with narrative content filled in
- Create character descriptions beyond structural architecture
- Recommend what the writer "should" write

Every output is structural: what the story needs to *do*, not what it should *contain*.

### Anti-Sycophancy Controls

The pathway must resist the pressure to validate every idea the writer brings. Specifically:

- **The Hard Risks section is required** in every Structural Plan, even when the plan feels solid. If the pathway cannot identify hard risks, that itself is a flag — it means the analysis isn't probing deeply enough.
- **Readiness gates are real gates**, not rubber stamps. If the storyable or draftable gate fails, the pathway says so and diagnoses why, rather than producing a polished plan around a hollow center.
- **Option Architecture prevents premature validation.** Presenting 2–3 candidates with honest tradeoffs is harder to sycophantically endorse than presenting one "perfect" spine.
- **The Uncertainty Ledger prevents false confidence.** Marking fields as Unknown or Provisional is more honest than filling them with plausible-sounding guesses.
