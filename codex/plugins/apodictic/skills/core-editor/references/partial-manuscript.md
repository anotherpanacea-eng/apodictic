# Partial Manuscript Diagnostic

*Reference file for the APODICTIC Development Editor. Loaded when `artifact=partial` is set by the intake router.*

---

## Purpose

Writers stuck mid-draft need structural diagnosis on what exists without being penalized for what doesn't. A partial manuscript is not a failed complete manuscript — it's a work in progress with its own diagnostic needs.

The partial-manuscript flag modifies Core DE behavior across intake, pass execution, and synthesis. It does not create a separate workflow — it calibrates the existing one.

---

## When This Fires

The intake router sets `artifact=partial` when:

- The writer has continuous narrative but the draft is incomplete
- More than ~2,000 words of connected prose with discernible forward movement
- The writer could hand you pages in order but would say "it's not done"

See `intake-router-runtime.md` §1 for full artifact thresholds.

---

## Intake Modifications

### Contract Schema

Generate the contract from available material. Mark uncertain fields explicitly:

```
GENRE/SUBGENRE: [inferred from available material]
READER PROMISE: [inferred — may shift as draft continues]
ENDING TYPE: [UNKNOWN — draft incomplete]
STRUCTURE COMPS: [provisional — based on available arc]
```

**Do not ask the writer to commit to structural decisions they haven't made yet.** If the ending type is unknown, record that. If the midpoint hasn't been written, skip the midpoint hypothesis question. Adapt the 25 intake questions to what exists:

- Questions 15-17 (inciting incident, midpoint, climax): Ask only for beats that exist in the draft. For missing beats, ask "Do you know where this is going?" — record the answer as intent, not commitment.
- Question 18 (pacing instinct): Reframe as "Where does the draft feel stuck or uncertain?"
- Questions 19-21 (reader experience): Ask only about material that exists.

### Controlling Idea

If the writer can articulate a controlling idea, record it. If they can't, that's diagnostic data, not a failure. Record: "Controlling idea not yet crystallized — emergent from draft."

The anti-idea question remains useful even for incomplete work: knowing what the book is NOT arguing helps calibrate analysis of what exists.

---

## Pass Modifications

### Pass 0: Reverse Outline (Modified)

Run on all available material. At the end, add:

**Momentum Report:**
- Where the draft currently stops
- Whether the stopping point is a natural pause (end of scene, chapter, act) or a mid-scene break
- What forward motion exists at the stopping point — is there a pending question, unresolved conflict, or setup waiting for payoff?
- What the draft appears to be building toward (inference, not prescription)

**Do not:** Penalize the draft for lacking resolution, climax, or denouement. Flag structural proportions as provisional ("Act I is currently 45% of available material — this will shift as the draft continues").

### Pass 1: Reader Experience (Modified)

Read as a naive reader of an incomplete work. Track:

- Standard reader experience markers (boredom, confusion, delight, immersion breaks)
- Orientation and belief failures as normal
- Promise tracking — but mark promises as "open" rather than "broken" when they're clearly setup for material not yet written

**Add:**
- **Momentum tracking:** Where does reader engagement peak? Where does it flag?
- **Stall detection:** Identify where the draft's forward energy decreases. Does the writing become more tentative, more effortful, less certain? These often mark the writer's actual stuck point, which may not be where the draft literally stops.
- **"I would keep reading" signals:** What's working well enough that a reader would turn the page? These are the draft's strengths, and the writer needs to hear them.

### Pass 2: Structural Mapping (Modified)

Map available structure without projecting complete architecture:

- Build beat map for existing material only
- Identify which structural beats are present (inciting incident, first threshold, midpoint if reached)
- Note which beats are absent but expected
- Causal chain: map what exists, note where chains are open-ended (not broken — open)

**Do not:** Impose a structural template on incomplete material. If the draft has an inciting incident and rising action but no midpoint, report that — don't diagnose "missing midpoint" as a flaw.

**Add:**
- **Structural trajectory:** Based on available beats and causal chains, what structural shape is emerging? (Not "what should you do" — "what does this appear to be becoming.")
- **Proportional note:** Report word count distribution as current state, not as a proportional problem. "Act I is 30K words" is data. "Act I is too long" is premature when the draft isn't done.

### Pass 5: Character Audit (Modified)

Run on available material. Standard tracking applies:

- Character wants, fears, tactics, arc direction (not arc completion)
- Agency tracking for available scenes
- Motivation consistency across available material

**Do not:** Flag incomplete character arcs as failures. A character whose arc hasn't resolved yet is a character in progress, not a broken character.

**Add:**
- **Arc trajectory:** Where is each major character heading based on available evidence? What transformation appears to be in progress?
- **Sufficiency check:** Does the draft establish enough about each character for the reader to invest? This is a valid partial-manuscript question — you don't need a complete arc to judge whether setup is working.

### Pass 8: Reveal Economy (Modified)

Run on available material. Build the who-knows-what-when matrix for existing scenes.

- Track open questions, planted information, dramatic irony
- Note reveals that have been set up but not yet delivered — these are assets, not problems
- Apply fairness tests only to reveals that have already fired

**Do not:** Flag unresolved setups as "dropped threads." In a partial manuscript, an unresolved setup is a promise, not a failure.

**Add:**
- **Setup inventory:** List all planted information, open questions, and dramatic irony positions that the remaining draft will need to address. This is a service to the writer — it shows them what their own draft has committed to.

---

## Synthesis Modifications

The synthesis for a partial manuscript produces a **Diagnostic Letter** (not a full editorial letter). The framing shifts from "what's wrong and how to fix it" to "what's working, what's stalling, where to go next."

### Required Sections (Partial Manuscript)

**1. Title Block.** Same format as standard synthesis. Note: "Partial Manuscript Diagnostic."

**2. What's Working.** Lead with this. In a partial manuscript, the writer needs to know what to protect and build on. Identify:
- Strongest scenes, characters, dynamics
- Effective setups and promises
- Voice and tonal consistency
- Momentum peaks

**3. What's Stalling.** Where the draft's energy flags, and why. This is the core diagnostic for a stuck writer. Diagnose the most likely stall cause from textual evidence — name one or two, not all six.

| Stall cause | What it looks like in the text | Textual markers |
|---|---|---|
| **Structural uncertainty** — the writer doesn't know what happens next | The draft's causal chain weakens near the stopping point. Scenes become episodic rather than consequential. New subplots or characters appear late as if the writer is casting around for material. | (1) Causal connectors ("because," "therefore") replaced by temporal ones ("then," "later," "meanwhile") in the final third of available material. (2) Scene goals become vague or absent — characters are present in scenes without wanting anything specific. (3) New elements introduced near the end that don't connect to established throughlines. |
| **Character motivation gap** — the writer doesn't know why the character would do X | A character approaches a decision point and the draft stalls, or the draft writes around the decision (showing aftermath without showing the choice). Scenes near the stopping point describe the character's situation repeatedly without advancing it. | (1) The same character state is restated across multiple scenes without change — circling rather than progressing. (2) Scenes end before the character commits to action. (3) Interiority increases near the stopping point (the writer is thinking through the character's psychology on the page instead of dramatizing it). |
| **Tonal drift** — the draft is becoming a different book than it started | The voice, pacing, or emotional register shifts measurably between early and late material. The draft may start as one genre and evolve toward another without acknowledging the transition. | (1) Sentence rhythm changes significantly (e.g., early material is tight and propulsive, later material becomes reflective and discursive, or vice versa). (2) The ratio of dialogue to interiority shifts by more than 20% between the first and last quarter. (3) Genre markers from a different genre appear (e.g., a thriller starts including romance-paced relationship scenes without thriller tension). |
| **Scope creep** — the draft is trying to do too much | The manuscript's active throughlines multiply as it progresses. New promises are opened faster than existing ones are advanced. The word count per chapter increases as the writer tries to service more storylines simultaneously. | (1) The number of named characters with active roles increases by more than 50% between the first and last quarter. (2) Scene count per chapter increases to accommodate parallel storylines. (3) The setup inventory shows a growing ratio of opened-to-advanced threads. |
| **Fear of commitment** — the draft avoids the hard scene it's building toward | The draft builds toward a confrontation, revelation, or irreversible choice — then diverts. New subplots, flashbacks, or secondary scenes appear right before the moment the main throughline demands. The causal chain points clearly toward a scene the draft hasn't written. | (1) A clear structural setup (confrontation seeded, stakes established, characters positioned) followed by deflection to a different scene or storyline. (2) Flashbacks or backstory insertions increase near the stopping point — the writer retreats to known territory. (3) The Momentum Report shows strong forward energy that abruptly stops or redirects. |
| **Exhaustion** — writing quality drops, suggesting fatigue rather than structural failure | The structural logic remains intact but the prose quality degrades. The writer knows where the story goes but has run out of energy to execute it. The draft may become more tell-than-show, more summary-than-scene. | (1) Scene-to-summary ratio shifts — later material summarizes events that earlier material would have dramatized. (2) Sensory detail and interiority thin out while plot events continue at the same pace. (3) Dialogue becomes more expository (characters tell each other things for the reader's benefit rather than speaking in character). |

**4. Where to Go Next.** Not "what should happen in the plot" — that would violate the firewall. Instead:
- What structural questions the draft needs to answer (not the answers)
- What the setup inventory commits the draft to
- What decisions the writer needs to make before continuing
- What the draft's own momentum suggests about its trajectory

**5. Revision Notes (Available Material Only).** Standard triage format (Must-Fix / Should-Fix / Could-Fix) but scoped exclusively to existing pages. These are things the writer could address in the current material before writing forward.

**6. Appendices.** Standard diagnostic detail, severity calibration, framework notes.

### What the Synthesis Does NOT Do

- Prescribe plot events, scenes, or endings
- Diagnose the absence of unwritten material as a structural flaw
- Apply complete-manuscript standards to incomplete work
- Tell the writer what their book is about (that's their job)

---

## Output Naming

Partial manuscript diagnostics use the standard naming convention with a `partial` modifier:

- `[Project]_Contract_[runlabel].md` (marked as provisional)
- `[Project]_Pass0_Reverse_Outline_[runlabel].md` (includes Momentum Report)
- `[Project]_Pass1_Reader_Experience_[runlabel].md` (includes stall detection)
- `[Project]_Pass2_Structural_Mapping_[runlabel].md` (trajectory, not template)
- `[Project]_Pass5_Character_Audit_[runlabel].md` (trajectory, not arc completion)
- `[Project]_Pass8_Reveal_Economy_[runlabel].md` (includes Setup Inventory)
- `[Project]_Findings_Ledger_[runlabel].md`
- `[Project]_Partial_Diagnostic_[runlabel].md` (replaces `Core_DE_Synthesis`)

---

## Diagnostic State

Initialize `Diagnostic_State.md` from template as normal, but set:

```
Mode.Current: diagnostic
Mode.Artifact: partial
```

The coaching skill (`apodictic-coach`) can read this flag and adjust session planning accordingly — revision sessions for partial manuscripts focus on unblocking and forward momentum, not systematic revision of completed material.

---

## Interaction with Other Workflows

- **Revision Coach:** Available — and actively recommended — after partial manuscript diagnostic. Sessions focus on forward-writing momentum rather than systematic revision. The coaching protocol includes stall-cause-specific interventions matched to the six stall causes diagnosed in §3 of the Partial Diagnostic Letter. Post-synthesis offer: *"Diagnostic complete. Run `apodictic-coach` to plan your next writing session and work through what's stalling."*
- **Pre-Writing Pathway (re-entry):** If the diagnostic reveals fundamental structural uncertainty, recommend stepping back to Pre-Writing Pathway with re-entry mode (imports existing decisions from the contract).
- **Submission Triage:** Not available for partial manuscripts. If the writer selects `constraint:time`, offer targeted `apodictic-diagnose` instead.
- **Full DE:** Not available until the draft is complete. When the writer returns with a finished draft, run a Revision Round (if the partial diagnostic is recent) or a fresh full analysis.

---

*This file modifies Core DE behavior. It does not replace `run-core.md` — it layers on top of it.*
