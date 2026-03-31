# Fragment Synthesis Mode

*Reference file for the APODICTIC Development Editor. Loaded when `artifact=fragments` is set by the intake router.*

---

## Purpose

Writers with scattered scenes, notes, character sketches, dialogue experiments, and world-building documents — but no continuous narrative — need a pre-processing step before Core DE can run. Fragment Synthesis clusters the material, identifies what connects and what doesn't, and produces a candidate contract and recommended spine. It bridges fragments to the Pre-Writing Pathway or to a partial manuscript diagnostic.

Fragment Synthesis is not a development edit. It is a pre-diagnostic clustering and mapping step that makes the writer's existing material legible as a potential book.

---

## When This Fires

The intake router sets `artifact=fragments` when:

- Prose exists but lacks continuous narrative
- Disconnected scenes, character sketches, dialogue experiments, world-building documents
- No single thread runs for more than ~2,000 words continuously
- The writer couldn't hand you a chapter order

See `intake-router-runtime.md` §1 for full artifact thresholds.

**Two routes from fragments:**

| Goal | Route |
|------|-------|
| "Figure out what they add up to" | Fragment Synthesis → Pre-Writing Pathway |
| "I know what the book is — help me fill in the gaps" | Core DE (partial-manuscript flag) |

The second route skips Fragment Synthesis — the writer already has a structural vision and treats their fragments as an incomplete draft. Route B sets `artifact=partial` and loads `references/partial-manuscript.md`.

---

## Fragment Intake

Fragment Synthesis runs its own lightweight intake before clustering. This is not the full 25-question intake — it gathers just enough to orient the clustering.

### What to ask:

1. **What do you have?** Ask the writer to describe or provide their fragments. Accept any format: multiple files, a single file with sections, pasted text, verbal description of what exists.

2. **How much material?** Rough word count across all fragments. This determines whether clustering produces a partial-manuscript handoff or stays in pre-writing territory.

3. **Do you see a book in here?** Three possible answers:
   - "Yes — I know roughly what the book is, I just can't make the pieces fit." → Clustering will test the writer's vision against the material.
   - "Maybe — I think there's something here but I can't see it yet." → Clustering will propose candidate structures.
   - "No idea — I just have a pile." → Clustering will work inductively from the material.

4. **Anything you know for certain?** Genre instinct, characters you're committed to, tone, audience, themes. These become constraints on the clustering, not outputs of it.

---

## Clustering Protocol

### Step 1: Fragment Inventory

Read all provided material. For each fragment, record:

```markdown
### Fragment [N]: [working title or first line]
- **Type:** scene / character sketch / dialogue experiment / world-building / backstory / thematic note / outline fragment / other
- **Word count:** [measured]
- **Characters present:** [list]
- **Setting:** [if identifiable]
- **Temporal position:** early / middle / late / unknown
- **Emotional register:** [dominant tone]
- **Narrative energy:** static (description, exposition) / dynamic (conflict, movement, change)
- **Connections:** [list fragment numbers this connects to, with reason]
- **Standalone quality:** Could this fragment anchor a scene in a finished manuscript? [yes / with work / no — it's raw material]
```

### Step 2: Connection Mapping

After inventorying all fragments, build a connection map:

- **Character clusters:** Which fragments share characters? Do any characters appear across multiple fragments?
- **Setting clusters:** Which fragments share locations or world-building?
- **Temporal clusters:** Can any fragments be sequenced? What temporal gaps exist?
- **Tonal clusters:** Which fragments share emotional register?
- **Thematic clusters:** Which fragments seem to explore related ideas?
- **Conflict clusters:** Which fragments involve related tensions, desires, or obstacles?

Identify:
- **Hub fragments:** Fragments with 3+ connections to others (these are likely structural anchors)
- **Satellite fragments:** Fragments with 1-2 connections (supporting material)
- **Orphan fragments:** Fragments with 0 connections to anything else (may not belong to this book)

### Step 3: Candidate Structure

Based on the connection map, propose 1-3 candidate structures. Each candidate should:

- Name the structural form it suggests (novel, novella, composite novel, linked collection, other)
- Identify which fragments would anchor the structure
- Identify which fragments would support it
- Identify which fragments don't fit (orphans)
- Estimate how much new material would need to be written
- Name what the structure would make the book "about" (thematic center)
- Name what the structure would sacrifice (fragments or possibilities it wouldn't use)

**If the writer stated a vision in intake question 3:** The first candidate should test whether the material supports that vision. If it does, say so. If it doesn't, say why — name what's missing, what contradicts, or what the material suggests instead.

**If multiple candidates are viable:** Rank by how much of the existing material each structure uses. The writer has already written these fragments for a reason; structures that waste less existing work are preferable, all else being equal.

---

## Output Artifacts

Fragment Synthesis produces three artifacts:

### 1. Fragment Map

`[Project]_Fragment_Map_[runlabel].md`

The full inventory (Step 1) plus the connection map (Step 2), formatted as a readable document. This is the writer's first clear view of what they actually have.

### 2. Candidate Contract (Provisional)

`[Project]_Contract_[runlabel].md` (marked as provisional)

A draft contract generated from the strongest candidate structure. Uses the standard contract schema but marks uncertain fields:

```
GENRE/SUBGENRE: [inferred from fragment clusters]
READER PROMISE: [provisional — based on strongest candidate]
ENDING TYPE: [UNKNOWN — fragments do not resolve]
STRUCTURE COMPS: [provisional]
FORMAT: [candidate form: novel / composite novel / linked collection]
FRAGMENT BASIS: [list of hub and satellite fragments informing this contract]
COVERAGE: [estimated % of final manuscript represented by existing fragments]
```

### 3. Recommended Spine

`[Project]_Recommended_Spine_[runlabel].md`

A provisional structural spine showing:

- Proposed sequence of existing fragments
- Gaps between fragments (what needs to be written)
- Which fragments need significant revision to fit the spine
- Which fragments are raw material (not scenes yet) that inform the spine without occupying a structural position
- Estimated total word count range for the finished work

**The spine is a proposal, not a prescription.** It shows the writer one credible path through their material. The Pre-Writing Pathway will refine or replace it.

---

## Handoff

After producing the three artifacts, Fragment Synthesis hands off to one of two destinations:

### → Pre-Writing Pathway (default)

If the fragments don't yet constitute a partial draft (total connected material < ~10,000 words, or no continuous narrative thread exceeds ~2,000 words), hand off to the Pre-Writing Pathway with:

- The candidate contract as pre-filled input
- The recommended spine as a starting point for Phase 4 (Spine Selection)
- The fragment map as reference material

The Pre-Writing Pathway runs in **re-entry mode** — it imports the decisions already made rather than starting from scratch.

### → Partial Manuscript Diagnostic

If the fragments, once sequenced, constitute enough connected material to analyze as a partial draft (~10,000+ words with identifiable forward movement), offer the writer a choice:

> "Your fragments sequence into roughly [X]K words of connected narrative. I can either:
> - **Continue to Pre-Writing** to plan the full structure before you draft more, or
> - **Run a partial manuscript diagnostic** on the sequenced material to see what's working and what's stalling.
>
> Which would be more useful right now?"

If the writer chooses diagnostic, set `artifact=partial` and load `references/partial-manuscript.md`.

---

## What Fragment Synthesis Does NOT Do

- **Generate plot.** The firewall applies. Fragment Synthesis maps what exists and proposes structures — it does not invent scenes, plot events, or character decisions.
- **Replace the writer's vision.** If the writer knows what their book is, the candidate structure should test that vision, not override it.
- **Force coherence.** If the fragments genuinely don't cohere into a single book, say so. "These fragments suggest two different projects" is a valid diagnostic finding.
- **Run passes.** Fragment Synthesis is pre-diagnostic. Passes run after the material has been sequenced into something analyzable.

---

## Interaction with AI-Prose Calibration

If `constraint:ai` is set (fragments were partially written with AI), note this in the fragment inventory but do not run AI-Prose Calibration during Fragment Synthesis. Calibration runs after the material is sequenced and analyzed as a partial or complete manuscript.

---

*This file defines a pre-processing step. It does not modify Core DE passes — it precedes them.*
