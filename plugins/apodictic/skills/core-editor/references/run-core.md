# Core DE Passes & Synthesis

*Reference file for the APODICTIC Development Editor. Loaded for every Core DE and Full DE run.*

---

## Intake Protocol (Always Run)

### Router Integration

If the user arrived via the `/start` intake router, the router has already classified: `artifact`, `goal`, `concern`, `constraints`, and `operator`. Treat these as pre-filled intake values, skip redundant questions, and calibrate the intake below. See `references/intake-router-runtime.md` for runtime routing behavior.

If the user arrived via `/develop-edit` or direct request, run intake from scratch as described below.

### Draft-Then-Validate Workflow

**Step 1:** Read manuscript and generate DRAFT Contract Schema from text analysis alone.

**Step 2:** Present draft to author: *"This is what I infer from the text. Please correct any misalignments."* Author corrections reveal where text may not communicate intent.

**Step 3:** Ask hypothesis-driven questions. Format: *"My hypothesis is [X]. Is this accurate?"* More efficient than open-ended questions; surfaces interpretive gaps.

### Contract Schema (Draft from Text)

Generate preliminary schema before asking questions:

```
GENRE/SUBGENRE: [inferred from conventions, tropes, structure]
READER PROMISE: [what experience the text appears to offer]
HEAT LEVEL: [if applicable: inferred from content]
DARKNESS LEVEL: [if applicable: inferred from content]
PRIMARY TENSION TYPE: [external / relational / epistemic / moral]
ENDING TYPE: [closed / open / ambiguous / denial-of-catharsis]
TONE COMPS: [works that feel similar]
STRUCTURE COMPS: [works with similar architecture]
NON-NEGOTIABLES: [inferred essential elements]
FORMAT: [novel / novella / collection / composite novel]
```

**For composite works:** Note whether text has unified arc or functions as discrete pieces.

### Controlling Idea

Format: [Value] + [Cause]

**Examples:**
- "Justice prevails when individuals sacrifice personal safety for collective truth."
- "Identity dissolves when the body's responses can no longer be trusted as evidence of self."

**For open endings:** State the pressure applied to a question, not an answer.

### Anti-Idea

State what the book is explicitly NOT arguing. This prevents the system from "correcting" toward unwanted moral clarity.

**Example:**
- Controlling idea: "Identity dissolves when the body's responses can't be trusted."
- Anti-idea: "The body never lies" / "Desire is always authentic"

### Hypothesis-Driven Intake Questions

Ask with explicit hypotheses. Format: *"My hypothesis is [X]. Is this accurate?"*

**Intent and Audience:**
1. **Controlling Idea Hypothesis:** Based on ending and thematic patterns, my hypothesis is: "[inference]." Is this accurate?
2. **Anti-Idea:** What is this book explicitly NOT arguing?
3. **Emotional Landing:** At the end, should reader feel [hypothesis]? (Not understand—*feel*.)
4. **Comps:** I detect similarities to [inferred]. Accurate? What are your tone vs. structure comps?

**Protagonist and Engine:**
5. **POV vs. Protagonist:** [A] is POV holder, but [B] appears to architect change. Whose transformation is the spine?
6. **Narrative Engine:** What drives the story forward? My hypothesis: [inference]. Accurate?
7. **Wants:** On page one, protagonist wants [surface]. Underneath: [deep]. Correct?
8. **Central Obstacle:** What cannot be solved without internal change?
9. **The Lie:** What false belief must protagonist confront?

**Relationship Dynamics:**
10. Why these specific people? Why now?
11. What are the steps of trust, rupture, repair (or corruption)?
12. Where does desire lead before understanding catches up?
13. What is the emotional price of connection in this world?

**Structure:**
14. **Format:** Is this [novel / collection / composite novel with unified arc]?
15. **Inciting Incident Hypothesis:** My scan suggests [moment] functions as inciting incident. Accurate?
16. **Midpoint Hypothesis:** I identify [scene/chapter] as midpoint pivot. Accurate?
17. **Climax:** What is the real moment of no return?
18. **Pacing Instinct:** Where do you feel the draft drags?

**Reader Experience:**
19. What are you deliberately keeping unresolved vs. crystal clear?
20. What should reader suspect early? Realize when?
21. What intended misreading? Is it fair (seeded, playable)?

**Constraints:**
22. Non-negotiables?
23. Draft stage?
24. Known problems?
25. Willing to cut 10-20%? Change POV, tense, order?

If router output already answered any of these, do not ask again unless clarification is required.

### Output: Contract Document

Generate `Contract_and_Controlling_Idea.md` containing:
- Completed schema fields
- Contract paragraph (generated from fields)
- Controlling idea and anti-idea
- Selected genre modules and specialized audits
- Confirmed non-negotiables

### Audit Activation at Contract

After generating the contract, recommend specialized audits based on genre, mode, and content signals. These audits run after core passes (or after expanded pass sets when advanced passes are selected) and produce companion findings that feed the synthesis.

**Contract-driven activation rules:**

| Signal in Contract | Recommended Audits | Rationale |
|---|---|---|
| Thriller or Suspense | Stakes System, Decision Pressure, Mystery/Thriller Architecture | Thriller contract demands escalating pressure field, credible urgent choices, and information-pressure delivery |
| Mystery or Investigation | Decision Pressure, Mystery/Thriller Architecture, Stakes System | Mystery contract demands evidence-governed choices, clue economy, and consequence architecture |
| Romance | Emotional Craft, Decision Pressure | Romance contract demands felt emotional transmission and credible commitment/withdrawal choices |
| Horror | Stakes System, Emotional Craft, Horror Craft | Horror contract demands consequence delivery, dread transmission, and sustained pressure |
| Literary or Upmarket | Scene Turn, Emotional Craft, Literary Craft, Decision Pressure | Literary mode demands scene-level precision, emotional specificity, prose-as-structure integration, and psychologically precise choices |
| SFF (Science Fiction / Fantasy) | SFF Worldbuilding, Stakes System | SFF contract demands world-rule integrity and system-scale consequence |
| Significant physical conflict present | Force Architecture | Any manuscript where physical confrontation carries narrative weight |
| Memoir, personal essay, creative nonfiction | Memoir/CNF (Gornick Layer), Franklin Pathway | Memoir requires situation/story distinction and narrating intelligence; Franklin tests pre-spine viability |
| Narrative nonfiction, reported feature, profile | Narrative Nonfiction Craft (Hart), Franklin Pathway | Nonfiction with narrative ambitions requires scene construction and source integration diagnostics |
| Composite novel or series | Series/Composite Novel | Multi-part works require standalone function and distance management |
| Heat level > 0 or erotic content present | Erotic Content Tag | Intimate scenes require load-bearing vs. decorative analysis |
| Consent complexity, power dynamics central | Consent Complexity | Works where consent is narratively interrogated, not just present |
| Cozy signaling in marketing or tone | Cozy Tag | Cozy promise requires safety envelope and recovery rhythm diagnostics |
| Philosophical themes, novel of ideas | Philosophical Tag, Dialectical Clarity | Idea-driven work requires question architecture and rhetorical fairness |
| Historical setting (>50 years before composition) | Historical Fiction | Period settings require authenticity and attitude diagnostics |
| Significant female characters in any genre | Female Interiority | Tracks persistent inner life across all scene types; catches interiority thinning |

**Activation is recommendation, not mandate.** Present the recommended audit list to the author at intake. Author can accept, decline, or add audits. Record selections in the contract document.

**Minimum recommendation:** Every manuscript should receive at least Stakes System and Decision Pressure recommendations, since both address universal craft concerns (pressure architecture and choice plausibility).

---

## Pass Resolution (Query-Driven)

Resolve pass scope before running diagnostics:

1. Load `references/pass-dependencies.md`.
2. Resolve user concern to minimum pass set via the concern table.
3. Add upstream dependencies automatically.
4. Order execution by dependency tier.
5. Run synthesis after selected passes complete.
6. If selected set includes Pass 3, 4, 6, 7, 9, or 10, load `references/run-full.md` for those pass specifications.

If concern is absent or ambiguous, default to **General diagnostic** baseline (Passes 0, 1, 2, 5, 8).

Pass specifications below define how each pass runs once selected.

---

## Execution Mode

APODICTIC supports three execution modes. The mode choice affects how passes run, not what they diagnose — the same pass specifications, Findings Ledger protocol, and synthesis format apply in all modes.

### Pre-flight Diagnostics (Required)

Before selecting an execution mode, the parent orchestrator runs a pre-flight metadata scan. Pre-flight is a bash script — not a model call — that gathers manuscript measurements needed for informed dispatch decisions.

**What it does:** Runs `scripts/preflight.sh` on the manuscript file. Produces a metadata packet containing: total lines, estimated word count, section/chapter boundaries, POV and tense detection (pronoun-frequency heuristic on three 200-line samples), dialogue ratio, mean paragraph length, and dispatch recommendations.

**What it computes:**
- **Execution mode recommendation:** <60K words → sequential; 60–100K words → hybrid; >100K words → swarm. These replace the approximate guidance in the mode descriptions below; the parent orchestrator uses the measured word count, not a guess.
- **Triage subagent `max_turns`:** `ceil(total_lines / 500) + 20`. This ensures enough turns for full-manuscript I/O (at 500 lines per read chunk) plus output file generation, with a 20-turn buffer for reasoning, complex structural decisions, and focus map targeting.
- **Conversion artifacts flag:** If the section boundary count is low relative to word count (e.g., 4 breaks in 84K words), the metadata packet notes that chapter structure may have been lost in file conversion. The triage subagent should identify scene boundaries from narrative content rather than relying on headers.

**What it does NOT do:** No scene identification, no structural function tagging, no reader experience tracking, no focus map targeting, no diagnostic flags of any kind, no genre identification. Pre-flight is a tape measure, not a stethoscope.

**Cost:** Zero model tokens. Sub-second execution time. The bash script runs locally.

**How it integrates:** The parent orchestrator runs pre-flight immediately after loading the manuscript path. It reads the metadata packet, selects the execution mode, sets `max_turns` for the triage subagent, and passes relevant metadata (total lines, section boundaries, POV pattern) to subagents so they don't have to rediscover it.

**Script location:** `scripts/preflight.sh`. Usage: `./scripts/preflight.sh <manuscript_path> [output_path]`. If output path is omitted, writes to stdout.

### Subagent Dispatch (All Modes)

**Every pass runs as a subagent.** This is not optional and applies to all three execution modes. The parent orchestrator dispatches each pass via the Task tool and never runs analytical passes in its own context. This protects against unexpected context compaction — if the platform compacts the parent's context mid-run, no analytical work is lost because every pass artifact has already been written to disk by its subagent before returning.

The three modes differ in **what each subagent receives**, not in whether subagents are used.

### Sequential Mode (Default)

Each pass runs as an independent subagent that receives the full manuscript, contract, and accumulated Findings Ledger. Passes run in order — each subagent is dispatched after the previous one returns and its ledger entry is persisted to disk. This is the simplest mode: every pass sees the full manuscript and the full analytical history.

**When to use:** Most runs. Pre-flight recommends sequential for manuscripts under ~60,000 words.

**Tradeoff vs. former single-context:** Slightly higher token cost (each subagent loads the manuscript independently rather than sharing a context window). In exchange: compaction resilience, architectural isolation between passes, and no context salience decay in late passes.

### Hybrid Mode

Pass 0+1 reads the full manuscript as a triage subagent and produces a **focus map** — a targeting document that tells each subsequent pass which scenes to deep-read. Later passes receive the reverse outline (the compressed manuscript) plus only the focus map's targeted excerpts, not the full text.

**What the user should know:** Hybrid mode provides most of swarm's quality gains — architectural isolation, independent analysis, reduced anchoring — at roughly **2–3x the token cost** instead of swarm's 5x. The tradeoff: later passes see targeted excerpts rather than the full manuscript, so they depend on the focus map's accuracy. The focus map errs on inclusion (targeting 30–50% of scenes), and every pass still receives the complete reverse outline for structural context.

**When to use:** The sweet spot for most serious editorial runs. Pre-flight recommends hybrid for manuscripts in the 60–100K word range. Also valuable for:
- Runs where the user wants better-than-default quality without full swarm cost
- Standard editorial workflow (not final-round submission diagnostics)

**When NOT to use:** Manuscripts under ~40,000 words (sequential handles these comfortably), or final-round diagnostics where maximum depth justifies swarm's cost. Pre-flight's mode recommendation can be overridden by the user at intake.

**How to invoke:** The user requests hybrid mode at intake or before pass execution begins. Example: "Run this in hybrid mode" or "Use selective reading." The system confirms mode selection and token cost implications before proceeding.

**Full specification:** See `references/hybrid-mode.md` for the focus map format, targeting grammar, confidence tiers, excerpt extraction protocol, and risk analysis.

### Swarm Mode

Each evaluative pass runs as an independent subagent that receives the full manuscript. Unlike sequential mode, passes 2, 5, and 8 can run **in parallel** since they don't depend on each other's ledger entries — they each receive the same accumulated ledger (from the triage pass only) and produce independent findings.

**What the user should know:** Swarm mode produces roughly **twice as many findings** with **more specific cross-pass connections** and **more consistent counterevidence**, at approximately **5x the token cost**. The quality improvement comes from architectural isolation: each pass genuinely cannot see prior analysis until the reconciliation step, which eliminates anchoring bias and produces multi-perspectival convergence rather than echo.

**When to use:** When maximum analytical quality matters more than token economy. Particularly valuable for:
- Final-round diagnostics before submission
- Cases where prior runs (sequential or hybrid) produced a synthesis that felt thinner than the pass analysis warranted
- Manuscripts where the focus map approach feels insufficient (very dense literary fiction, heavily interwoven plot structures)

**When NOT to use:** Quick diagnostics, partial manuscripts, budget-constrained runs, or manuscripts short enough that sequential handles them comfortably.

**How to invoke:** The user requests swarm mode at intake or before pass execution begins. Example: "Run this in swarm mode" or "Use subagent passes." The system confirms mode selection and token cost implications before proceeding.

#### Execution Protocol (All Modes)

**Parent orchestrator responsibilities:**
1. Run pre-flight (`scripts/preflight.sh`) to get manuscript metadata
2. Run intake in the parent context (load SKILL.md, run-core.md, generate contract, resolve pass set)
3. Initialize the Findings Ledger
4. Dispatch each pass as a subagent (Task tool, `model: opus`, `subagent_type: general-purpose`, `max_turns` per pre-flight)
5. **Persist each subagent's ledger entry to disk immediately upon return** — before dispatching the next subagent
6. Pass the growing Findings Ledger to each subsequent subagent
7. Dispatch the synthesis subagent with the complete ledger

**Turn budgets (from pre-flight):**
- **Triage subagent (Pass 0+1):** `max_turns` = `ceil(total_lines / 500) + 20` (pre-flight computes this). For an 84K-word / 5,759-line manuscript, this yields `max_turns: 32`.
- **Analytical passes (Pass 2, 5, 8):** Default turn budget. In hybrid mode these passes read the reverse outline + targeted excerpts; in sequential/swarm they read the full manuscript. Neither requires elevated budgets because the manuscript is provided as a file path, not pre-loaded into the prompt.
- **Synthesis:** Default turn budget.

**What each pass subagent receives:**

| Input | Sequential | Hybrid | Swarm |
|-------|-----------|--------|-------|
| Manuscript | Full (file path) | Triage: full; later passes: outline + excerpts | Full (file path) |
| Contract | Yes | Yes | Yes |
| Pass specification | Yes | Yes | Yes |
| Accumulated Findings Ledger | All prior passes | All prior passes | Triage only (passes 2/5/8 get same ledger) |
| Focus map | No | Yes (for later passes) | No |

**What each pass subagent returns:**
- Its pass artifact (analysis output), written to disk
- Its Findings Ledger entry (formatted per §Ledger Entry Format), written to disk

**Pass grouping:** Pass 0 and Pass 1 run in a single combined subagent (both are full-read passes with no dependencies). All subsequent passes run as individual subagents. In swarm mode, passes 2, 5, and 8 may run in parallel.

**Staged visibility:** The subagent receives the Findings Ledger but is instructed to complete its own analysis before reading the ledger's Notable Findings. Because every mode now uses subagent dispatch, isolation is architecturally enforced in all modes — no subagent has prior pass artifacts in its context, only the ledger entries provided for reconciliation.

**Token cost estimate (118k-word manuscript):**

| Mode | Estimated total tokens | Quality |
|------|----------------------|---------|
| Sequential (full manuscript per pass) | ~400,000–500,000 | Strong; no context decay, compaction-safe |
| Hybrid (selective reading) | ~500,000–690,000 | Strong; architectural isolation + targeted excerpts |
| Swarm (full manuscript, parallel) | ~1,000,000–1,200,000 | Best; no cross-pass influence, parallel execution |

Note: Sequential mode's cost estimate is higher than the former single-context mode (~240,000) because each subagent loads the manuscript independently. The increase buys compaction resilience and eliminates context salience decay in late passes.

For full architecture details, cost analysis, and risk discussion: see `docs/subagent-architecture-design.md`.

---

### Pre-Pass Re-Grounding (Required)

Before beginning each evaluative pass (Passes 1, 2, 5, 8, and any Full DE passes), re-read the contract and the Findings Ledger. This counteracts context salience drift — as conversation context grows, the most important analytical anchors (what the book promises, what earlier passes found) lose salience relative to more recent content. Re-grounding refreshes these anchors.

**For Pass 0:** No re-grounding needed (first pass; no ledger yet).
**For all subsequent passes:** Re-read (1) the contract's controlling idea, anti-idea, and non-negotiables, and (2) the accumulated Findings Ledger. Do not re-read full prior pass artifacts — the ledger is the compressed representation; the pass artifacts are reference material for specific claims, not re-reading material.

### Staged Visibility (Recommended)

To reduce cross-pass anchoring while preserving cross-pass learning, each evaluative pass should analyze independently before consulting prior findings:

1. **Draft findings** from the pass's own analytical lens, without reference to the Findings Ledger's Notable Findings or Cross-Pass Connections.
2. **Then read** the relevant Findings Ledger entries and reconcile: confirm, contradict, refine, or integrate.
3. **Record reconciliation** in the pass's Cross-Pass Connections section of its ledger entry.

Because all modes now use subagent dispatch, isolation is architecturally enforced in every run — no subagent has prior pass artifacts in its context, only the ledger entries provided at reconciliation time. A/B testing confirmed that architecturally enforced isolation produces more independent findings and genuine cross-pass complication. The pass still re-grounds on the contract and ledger's existence before starting (see §Pre-Pass Re-Grounding), but defers reading the ledger's substantive findings until after drafting its own.

## Core DE Pass Specifications

### Pass 0: Reverse Outline

Generate an objective summary of what exists on the page—not what the author intends.

**For each scene, document:**
- Scene number and location in manuscript
- What literally happens (action, not interpretation)
- Word count (measured, not estimated)
- Ratio: dialogue / action / interiority
- What information the reader gains
- **Mechanism of transition:** Does scene end because conflict resolved, decision made, or arbitrarily? (Flag arbitrary breaks.)

**Word Count Verification:**
At the end of Pass 0, measure and report:
1. Total manuscript word count (`wc -w`)
2. Word count per major part/act (extract and measure each)
3. Use these measured values for all subsequent proportional analysis

**Output:** `Reverse_Outline.md` with verified word counts

**Hybrid mode additional output:** When running in hybrid mode, Pass 0+1 (combined triage subagent) also produces `[Project]_Focus_Map_[runlabel].md` — a targeting document that directs later passes to specific scenes for deep reading. See `references/hybrid-mode.md` for the focus map specification, targeting grammar, and confidence tiers.

### Pass 1: Reader Experience

Read as a naive reader. Track emotional and cognitive response only.

**Track:**
- Boredom, confusion, delight, emotional spikes
- "I would stop reading here" points
- Immersion breaks

**Tag specifically:**

**Orientation Failures:** "Where am I? When? Who's speaking? What changed?"
→ Maps to craft/anchoring fixes

**Belief Failures:** "I don't believe this decision / reaction / coincidence."
→ Maps to motivation/pressure/cost fixes

**Promise Tracking (from page 1):**
- What questions does the reader believe the book will answer?
- What kind of ride do they think they're on by page 5? Page 20?
- Where do felt promises drift from the contract?

**Output:** Reader experience log with tagged failures and promise drift warnings.

**Finding-driven audit triggers:**
- 3+ belief failures ("I don't buy this decision/reaction") → recommend **Decision Pressure** audit if not already activated
- Emotional flatness or melodrama logged at 3+ scenes → recommend **Emotional Craft** audit
- "Stakes feel low" or "I don't care what happens" at 2+ points → recommend **Stakes System** audit
- Action/fight scenes that break immersion → recommend **Force Architecture** audit

### Pass 2: Structural Mapping

Map the narrative architecture.

**Build:**
- Scene outline: location, time, POV, goal, conflict, outcome, new information
- Plot beats: inciting incident, first threshold, midpoint, crisis, climax, resolution
- Causal chain: "because X, therefore Y" connections
- Word count distribution by chapter, scene, **and part**
- **Proportional analysis:** % of total per act/part

**Verification Checkpoint (Required):**
Before calculating any proportions, measure word counts programmatically:
1. Total manuscript: `wc -w [file]`
2. Each part/act: extract lines and count separately
3. Report measured values, not estimates from line ranges

**Detect:**
- Orphan scenes (removable without breaking causality)
- Repeated beats
- Missing causal links ("and then" instead of "therefore")
- Causal gaps (unclear transition mechanisms)
- Structural anomalies
- **Proportional imbalance:** Parts >40% of total (potential "stuck" signal) or <10% (potential underdevelopment)

**For Composite Novels:**
- Unity assessment: single arc or discrete pieces?
- Part-level beat mapping: internal arc per part
- Seam analysis: what changes at each transition?
- Generate proportional distribution table

**Output:** Beat map, causal chain, structural flags, **proportional distribution table**.

**Finding-driven audit triggers:**
- Scene-level causal gaps or arbitrary breaks at 3+ scenes → recommend **Scene Turn** audit (Bickham) if not already activated
- Nonfiction manuscript with situation overwhelming story → recommend **Franklin Pathway** if not already activated

### Pass 5: Character Audit

Model character psychology and track through manuscript.

**For each major character:**
- Explicit want / hidden want
- Fear/avoidance patterns
- Tactics
- Arc: what they learn / refuse / become
- Their "lie"

**Track:**
- Agency per act: who causes movement vs. who reacts?
- Decision points: where do they choose?
- Voice consistency
- Motivation consistency

**Reference project character portraits for consistency checking.**

**Detect:**
- Puppet moments
- Agency collapse
- Voice drift
- Motivation discontinuity

**For detailed character architecture (psychology engine, arc types, agency quotient, genre tuning packs):** See `references/character-architecture.md`.

**Output:** Character cards, agency timeline.

**Finding-driven audit triggers:**
- Motivation discontinuity or puppet moments at 2+ major decisions → recommend **Decision Pressure** audit if not already activated
- Agency collapse in Act III → recommend **Stakes System** audit (pressure field may not be converting)
- Character wants/fears under-specified → recommend full **Character Architecture** specialized audit (Truby Part 9: moral argument coupling)

### Pass 8: Reveal Economy

Track information flow.

**Build:**
- "Who knows what when" matrix (characters + reader)
- Reveal timeline
- Suspense architecture: open questions at each point
- Dramatic irony map

**Detect:**
- Premature reveals
- Delayed clarifications (confusion as attrition)
- Missing signposts
- Dropped threads
- Unfair misdirection (apply fairness tests)

**Fairness Tests:**
1. Are diegetic cues available on first read that justify the twist?
2. Does narration withhold what POV character would notice?
3. Does the story change what was "true" vs. recontextualize?

**Output:** Reveal ledger, fairness flags.

**Finding-driven audit triggers:**
- Knowledge errors (character acts on information they shouldn't have) → recommend **Decision Pressure** audit (IS channel)
- Information timing issues affecting character decision credibility → coordinate Decision Pressure IS flags with Reveal Economy findings

---

### Findings Ledger Protocol

After completing each pass artifact, immediately append a ledger entry to `[Project]_Findings_Ledger_[runlabel].md`. The ledger is a running document that accumulates pass findings for the synthesis step.

**Purpose:** Solve context salience decay. By the time the synthesis runs, earlier pass details have faded from active context. The ledger preserves notable findings, data artifact pointers, and cross-pass connections while they're fresh — each entry is written immediately after its pass, not reconstructed later.

**When to write:** Immediately after the pass artifact is saved — while the pass content is still in active context. Do not defer ledger entries to the synthesis step.

**What to include:** See §Ledger Entry Format below.

**What NOT to include:** The full pass analysis. The ledger is an extraction, not a copy. If a finding is in the ledger, the evidence is in the pass artifact; the ledger points to it.

**Pass 0 and Pass 10 exception:** These are data-building passes. They do not require ledger entries unless they surface an observation that warrants it (e.g., a Rule Ledger inconsistency detected during outline construction, or an entity continuity error noticed during tracking). When a genre module adds analytical tracking to Pass 0 (such as the SFF Rule Ledger), notable patterns in that tracking should generate a ledger entry.

#### Ledger Entry Format

Each pass appends a section using this structure:

```markdown
---

## Pass [N]: [Name] — Ledger Entry

### Notable Findings

[Numbered list. Each entry: one sentence stating the finding, one sentence
stating why it matters for the editorial letter, a pointer to the
specific location in the pass artifact, and optionally, the best case
against the finding.]

1. **[Finding name].** [What it is.] [Why it matters.]
   *(See Pass N, §[Section], [table/paragraph name].)*
   *Counterevidence:* [Optional. The strongest case that this finding is
   wrong, overstated, or explained by authorial intent. Omit if no
   plausible countercase exists. When present, helps synthesis calibrate
   severity and prevents the ledger from reading as a list of assertions.]

### Data Artifacts for Letter Reference

[List of tables, inventories, matrices, or other structured data in the
pass artifact that the editorial letter should direct the author to.
One sentence per artifact describing what it shows and why it's useful
for revision.]

- **[Artifact name]** — [What it shows, in one sentence.]
  *(Pass N, §[Section].)*

### Cross-Pass Connections

[Findings from this pass that connect to earlier ledger entries. These
are pre-built hypotheses about shared root causes — the synthesis step
evaluates them. Format: what this pass found, what it connects to,
and why the connection matters.]

- [Connection description.]
  *(Connects to: Pass M, Finding N.)*

### Unresolved Questions

[Observations this pass surfaced but couldn't fully analyze within its
scope. These may become stress test material, deferred audit triggers,
or items for the "Additional Observations" section of the editorial
letter.]

- [Question.]

### Audit Triggers

[Migrated here from pass artifact. The pass artifact retains its own
audit triggers section for standalone readability, but the ledger
consolidates them for the synthesis step.]

| Trigger | Evidence | Recommendation |
|---------|----------|----------------|
```

#### Ledger Discipline

- **Notable findings are not all findings.** Include only findings that should appear in or inform the editorial letter. A belief failure rated "minor" that doesn't connect to a pattern is pass-level data, not a ledger entry. A belief failure rated "moderate" that connects to a root cause is a ledger entry.
- **When in doubt, include.** A finding whose notability is uncertain should go in the ledger rather than be left out. The synthesis step can ignore a noisy ledger entry; it cannot recover a finding that was never recorded. Err on the side of inclusion for any finding that *might* connect to a pattern — the next pass may confirm or disconfirm its importance.
- **Cross-pass connections are the ledger's highest-value output.** These are the observations that fall between passes — the synthesis step can't make them if it can't see the earlier pass data. Write them explicitly: "Pass 8 found X, which connects to Pass 5 Finding Y because Z."
- **Retroactive promotion.** A later pass may reveal that an earlier pass's finding is more important than it originally appeared. When this happens, the later pass should: (1) note the connection in its own Cross-Pass Connections section, and (2) append a brief **Retroactive Addition** to the earlier pass's ledger section, promoting the finding and explaining why it now matters. Format: `**[Retroactive — added by Pass N]:** Pass M's finding on [X] is more significant than initially assessed because [reason]. Promotes to notable.` This ensures the synthesis step sees the upgraded finding in the context of the pass that generated it, not only in the pass that recognized its importance.
- **Unresolved questions feed the stress test.** If a pass surfaces something that feels like a vulnerability but doesn't fit the pass's diagnostic categories, log it here. The stress test step will draw from these.
- **Data artifacts are revision tools.** The editorial letter is an argument; the pass artifacts contain tools the author can use during revision (agency timelines, competence inventories, reveal timelines). The ledger tells the synthesis step which tools exist so the letter can point to them.

---

### Audit Integration Point

After all core passes are complete and before writing the synthesis:

1. **Review accumulated audit triggers.** Compile all finding-driven recommendations from Passes 1, 2, 5, and 8.
2. **Compare against contract-activated audits.** If a finding-driven trigger recommends an audit already activated at contract, confirm it should run. If it recommends an audit not activated at contract, present the recommendation to the author with evidence.
3. **Run activated audits.** Load the full specialized audit module from `specialized-audits/references/` and apply to the manuscript. Each audit produces its own findings document.
4. **Write the Audit Invocation Log.** Before synthesis, produce a log artifact tracking every audit considered during this run. Format:

```
## Audit Invocation Log

| Audit | Source | Status | Reason |
|-------|--------|--------|--------|
| Stakes System | universal | run | Recommended at intake |
| Decision Pressure | universal | run | Recommended at intake |
| Scene Turn | universal | run | Recommended at intake |
| [audit name] | contract | run/skipped | [why] |
| [audit name] | finding-driven | run/skipped | [trigger evidence or skip reason] |
```

**Source** = `universal` (always recommended), `contract` (genre/mode-driven at intake), or `finding-driven` (triggered by pass findings).
**Status** = `run`, `skipped` (author declined), or `deferred` (postponed to Full DE).
Save as `[Project]_Audit_Invocation_Log_[runlabel].md`.

5. **Feed audit findings into synthesis.** Specialized audit findings integrate into the editorial letter's "What Needs Work" sections — organized by problem, not by audit name. The author reads about the book's needs, not about which framework found the issue.

**Minimum audit recommendations for every manuscript:**
- **Stakes System** — universal pressure architecture diagnostic
- **Decision Pressure** — universal choice plausibility diagnostic
- **Scene Turn** (Bickham) — universal scene-level mechanics diagnostic

These three audits address craft concerns that apply regardless of genre. They should be recommended at intake and confirmed by the author.

---

## Core DE Synthesis

The synthesis is the author-facing editorial letter. It must read as one informed voice talking about a book — not as a framework generating output.

### Processing Protocol

**Processing order (what the LLM does internally):**

1. **Intent Check Loop.** Before finalizing any flag, verify against stated intent: "I detect [observation] in [location]. Is this the [stated intentional element], or unintentional?" Do not flag elements that align with contract, controlling idea, or stated non-negotiables.

2. **Audit Finding Consolidation.** Before root cause analysis, integrate supplementary audit findings with pass findings. Consolidation rules:
   - **Map audit flags to pass findings.** Each audit flag should connect to the pass finding(s) that triggered or support it. Audit flags that duplicate a pass finding are evidence for that finding, not separate items.
   - **Cluster by problem, not by audit.** If Stakes System flags STX-2 (Abstract Risk Persistence) and Decision Pressure flags AV-1 (Option Suppression) at the same decision point, they describe one problem (the decision fails because stakes are too abstract to generate real options), not two.
   - **Preserve audit-specific diagnosis when distinct.** If an audit surfaces a problem that no pass detected (e.g., Decision Pressure identifies a pattern of deferred consequence erasure that passes didn't flag), it enters root cause analysis as a distinct finding.
   - **Count consolidated problems, not individual flags.** A single root cause may have 8 audit flags supporting it. The flags are evidence; the root cause is what enters triage.
   - **Carry audit artifacts forward.** Audit-specific tracking artifacts (Decision Event Map, Stakes Ladder Map, Scene Turn code inventory, etc.) become appendix material. They support the editorial letter's arguments but don't appear in the letter body.

3. **Root Cause Analysis.** Read the Findings Ledger as the primary input for root cause analysis. The ledger's cross-pass connections are pre-built hypotheses about shared root causes — evaluate each. Identify 3-5 root causes (maximum 5) from the ledger's notable findings, cross-pass connections, and consolidated audit findings. If more than 5 seem present, flag that manuscript may need reconception. Audit findings that cluster under the same root cause strengthen the diagnosis; they don't multiply the root cause count. For any ledger finding that doesn't cluster under a root cause, carry it forward to the "Additional Observations" section (§4b) of the editorial letter.

4. **Triage.** Assign severity to each finding:
   - **Must-Fix:** Book-breaking (max 10)
   - **Should-Fix:** Significant diminishment (max 15)
   - **Could-Fix:** Polish (no cap, deprioritized)

5. **Adversarial Self-Check (required before writing the letter).** Re-evaluate findings in both directions — test whether each severity is too soft (under-diagnosed) or too harsh (over-escalated). Adjust if the adversarial case is stronger than the original assignment. Record the results.

   **Upward pressure (testing for softening):** For each Should-Fix flag, state in one sentence why it should be Must-Fix. If the Must-Fix case is stronger, upgrade. For each Mixed axis, state in one sentence why it should be Weak. If the Weak case is stronger, downgrade.

   **Downward pressure (testing for over-escalation):** For each Must-Fix flag, state in one sentence the best case for Should-Fix. If the Should-Fix case is stronger, downgrade. For each Weak axis, state in one sentence the best case for Mixed. If the Mixed case is stronger, upgrade.

   **Evidence check (both directions):** For each Must-Fix flag, confirm you have 2+ specific scene/line references. If not, either find them or downgrade your confidence (not the severity).

6. **Adversarial Reader Stress Test (required).** Before writing the letter, run the stress test per `references/adversarial-stress-test.md`. **Begin the stress test by setting aside the pass findings and the Findings Ledger.** Inhabit the low-charity reader profiles and generate 3-5 adversarial claims from a holistic reading of the manuscript — what would a hostile reader attack regardless of what the passes found? Draw also from the Findings Ledger's "Unresolved Questions" entries, which may contain vulnerabilities the passes noticed but couldn't fully analyze. After generating the independent claims, reconcile them with the pass findings: which attacks are already covered by editorial letter findings? Which are new? New attacks enter the stress test section of the letter. Attacks already covered by the editorial argument are noted as convergent evidence but not duplicated. This is a separate exercise from the adversarial self-check (step 5) — the self-check tests severity calibration of existing findings; the stress test surfaces what hostile readers would attack, which may include issues not flagged by the passes.

7. **Write the editorial letter** using the presentation format below. The self-check informs the letter's severities; the stress test becomes §7 of the letter.

**Key principle:** Processing order ≠ presentation order. The self-check must happen before writing, but in the output document it belongs in an appendix. The author reads findings; the framework owner reads methodology.

### Presentation Format (Editorial Letter)

The synthesis is structured as a letter with scannable reference material. Prose carries the argument; headings, bold thesis statements, and a revision table provide scannability. Framework shorthand (severity labels, pass numbers, protocol stamps) stays out of the main text — it belongs in the appendices only.

**Required sections, in order:**

**1. Title Block**
```
# Development Edit: [Title]
### [Author] | [Word count] words | [Draft stage]
*APODICTIC Development Editor v[X] — [Date]*
```

**2. The Short Version.** One paragraph. Names both the primary asset and the primary liability. States the verdict class (reconception vs. targeted revision vs. polish). Names the revision's core ask. The author should be able to read this paragraph alone and know where they stand.

**3. What the Book Does Best.** Prose. Specific scenes and line references embedded naturally. Explain *why* each strength matters — not just that it exists, but what it does for the reader. If one scene exemplifies the book's highest capacity, name it and explain why. This section establishes what the revision must protect.

Discipline: Maximum 3 major strengths for manuscripts needing significant revision. Maximum max(leaks, 3) for manuscripts needing only polish. Every strength must cite specific evidence.

**4. What Needs Work.** Headed subsections. Each heading is a **bolded thesis statement** that names the problem in plain language (e.g., "**Pacing: Part I has room Part III needs.**" — not "Priority Leak #1: Dramatic Density Imbalance"). Prose argument underneath with line references embedded naturally. The argument should make the reader understand *why* the issue matters for their book specifically, not just that a structural rule has been violated.

Group related issues under a single heading when they share a root cause (e.g., four underdeveloped secondary characters become one section about the pattern, not four separate flags).

**4b. Additional Observations from the Diagnostic Passes.** This section draws from the Findings Ledger — specifically from notable findings and cross-pass connections that didn't make it into §3 or §4 but that the author should know about. Brief prose paragraphs with cross-references to the pass artifacts.

**Inclusion criteria:**
- Any ledger finding rated "notable" that isn't already discussed in §3 or §4
- Any cross-pass connection that reveals a pattern not covered by the root causes
- Any data artifact that would be useful for revision even though it doesn't correspond to a "problem" (e.g., a competence-cost inventory that confirms the author's consistency, a suspense architecture table that shows strong question density)
- Structural characteristics of the manuscript worth noting even when they aren't flaws (e.g., "the novel runs on almost zero dramatic irony — this is a structural characteristic, not necessarily a problem, but it has these specific implications for revision")

**Exclusion criteria:**
- Findings already covered in §3 or §4 (no duplication)
- Raw data without interpretive value
- Audit triggers (these stay in Appendix A)

This section serves two purposes: it prevents the synthesis from compressing away pass findings that the author needs, and it teaches the author how to use the pass artifacts as revision tools. Every item should include a cross-reference pointing the author to the relevant pass artifact.

**5. Revision Checklist.** A table the author can tape to the wall. Priority ordered. Columns:

| # | What | Why it matters | Effort |
|---|------|---------------|--------|

"Effort" replaces severity labels — Low / Medium / High communicates what the author needs to know (how much work) without framework jargon. Map roughly: continuity fixes → Low; single-scene additions → Low–Medium; multi-scene redistribution → Medium; structural reconception → High.

Maximum 10 items in the table. If more than 10 issues exist, the prose sections carry the rest; the table holds only the actionable priorities.

**Traceability rule:** Every item in the revision checklist must correspond to a finding already discussed with rationale in the prose sections above (§3 or §4). The checklist is a summary tool, not a place to introduce new findings. If an issue isn't important enough to discuss in the letter body, it isn't important enough for the checklist.

Follow the table with:
- **What to protect:** One sentence listing the scenes, elements, and qualities that must survive revision.
- **What to be cautious about:** One sentence identifying the risk that revision introduces.

**6. The Strongest Case Against.** The rejection memo, reframed for the author. Write it as: "If I were arguing for passing on this manuscript..." State the case in 1-2 paragraphs. Reference findings from the letter — no new uncited claims.

**Do not render a verdict on whether the case wins or loses.** The author assesses that. The framework's job is to make the strongest honest case for rejection and let it stand on its own evidence. If the case is weak, its weakness will be self-evident; if the case is strong, dismissing it is a disservice. End with the case, not with reassurance.

**7. Adversarial Reader Stress Test.** Required for every editorial letter. Format and methodology per `references/adversarial-stress-test.md`. This section presents 3-5 adversarial claims from low-charity reader perspectives, each with evidence, severity, steelman defense, and net risk assessment. The stress test complements §6 — where §6 states the structural case against the manuscript in 1-2 paragraphs, §7 inhabits specific hostile reader types and surfaces what each would attack.

**8. Appendices.**
- **Appendix A: Diagnostic Detail.** Pointers to companion pass files and supplementary audit findings with brief descriptions of what each contains. For each supplementary audit that ran, list its companion findings file and any tracking artifacts produced (e.g., Decision Event Map, Stakes Ladder Map, Scene Turn code inventory). Group pass files first, then audit findings.
- **Appendix B: Severity Calibration.** Compressed summary of the adversarial self-check — which findings were tested, in which direction, whether any severities were adjusted.
- **Appendix C: Framework Notes.** Analysis version, model, run date, passes completed, protocol flags, prior analyses on file, cross-version stability notes (if applicable).

---

## Core DE Deliverables

**Reminder:** All outputs must follow the Author-Facing Language requirement (see `references/output-policy.md`). Translate all framework shorthand on first use.

### Editorial Letter (Core Synthesis)

The primary deliverable. Format specified in §Core DE Synthesis above.

### Diagnostic State

After writing the editorial letter, update `Diagnostic_State.md` with:
- Findings from this session
- Keep / Cut / Unsure decisions
- Change log

If `Diagnostic_State.md` does not exist in the project output context, create it from `references/diagnostic-state-template.md` first.

---

## Scene-Level Handoff (Optional)

When a diagnosis is complete for a clearly scoped scene and the writer wants help executing the fix, run `references/handoff-protocol.md`.

- Require explicit confirmation before mode switch.
- Append a new entry to `Handoff History` (never overwrite prior entries).
- Set `Mode.Current` to `execution` and set `Active scene scope`.
- In execution mode, diagnostic constraints are suspended; prose-level collaboration is allowed.
- Return to diagnostic mode via phrase trigger ("back to editor", "resume editor", "check this fix") or the `/start` resume gate.
- On re-entry, run a targeted delta check for the active scope, close the handoff entry, and reset mode to `diagnostic`.

---

## Revision Round Protocol

When re-analyzing a manuscript after author revision, use this protocol instead of starting fresh.

### Revision Round Intake

Before running passes, gather:

1. **What changed?** — List major revisions since last analysis (structural changes, added/cut scenes, character modifications)
2. **Which flags were addressed?** — Mark which previous flags the author attempted to fix
3. **Which flags were declined?** — Note which previous flags the author intentionally chose not to address (and why, if provided)
4. **New concerns?** — What does the author now suspect isn't working?

### Revision Round Constraints

**DO NOT:**
- Re-flag issues the author explicitly declined to address (respect their choices)
- Run full fresh analysis unless structural changes exceed 40% of manuscript
- Apply stricter standards to revised sections than to original analysis

**DO:**
- Focus analysis on changed material + ripple effects
- Check whether addressed flags are now resolved
- Track whether fixes created new problems
- Compare current state to previous Diagnostic State

### Revision Round Passes

**Targeted Pass Sequence:**
1. **Delta Scan:** Identify all changed sections (author-reported + text comparison if available)
2. **Ripple Check:** For each major change, trace downstream effects (Does cutting Chapter 3 break setup for Chapter 12?)
3. **Resolution Verification:** For each "addressed" flag, confirm fix landed (Did the added motivation scene actually establish motivation?)
4. **New Issue Detection:** Run standard passes ONLY on changed sections
5. **Integration Check:** Verify changed sections integrate with unchanged material

### Revision Round Output

**Revision Report** (not full diagnostic):
- Flags resolved: [list with verification notes]
- Flags still present: [list with updated evidence]
- New issues introduced: [list with locations]
- Ripple effects detected: [list with severity]
- Next priority: [single most important remaining issue]

### When to Reset to Full Analysis

Abandon Revision Round Protocol and run fresh full analysis when:
- Structural changes exceed 40% of manuscript
- POV, tense, or timeline has changed
- Core contract has shifted
- Author reports "I basically rewrote it"
- Previous diagnostic is >6 months old
