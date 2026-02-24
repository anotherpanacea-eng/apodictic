# Subagent Pass Orchestration — Design Document

**Status:** Available as optional execution mode (v1.0.4+). Default remains single-context.
**Date:** 2026-02-23
**Provenance:** Emerged from A/B comparison of APODICTIC v1.0.3 plugin output vs. blind editorial letter on *A Game of Universe* (Nylund, ~118k words). The comparison revealed that pass artifacts contained stronger analysis than the synthesis captured — root cause: context salience decay across a multi-pass run in a single context.

---

## Problem Statement

APODICTIC runs multiple analytical passes sequentially in a single conversation context. Each pass reads the manuscript, applies its diagnostic lens, and produces a structured artifact. By the time the synthesis step runs, earlier pass details have faded from active context. The Findings Ledger (v1.0.3) mitigates this by capturing notable findings at write-time rather than reconstructing them at synthesis-time, but the underlying architectural constraint remains: all passes share one context window.

Consequences:

1. **Context salience decay.** Earlier pass findings lose specificity by synthesis time. Pass 1's nine belief failures become "several belief failures" in the editorial letter. This may result from raw token pressure, attention allocation failure, or platform-level context compaction (unobservable from within the model).
2. **Output accumulation.** Each pass's artifact consumes context space. By Pass 8, the window holds the manuscript + framework + four prior pass outputs, leaving less room for the current pass's analysis.
3. **Insufficient pass isolation.** A pass can be influenced by prior pass outputs in ways that aren't analytically warranted — e.g., Pass 8 might anchor on Pass 5's character findings rather than independently analyzing information flow. This creates false coherence: findings that appear to converge may simply be echoing each other.

---

## Proposed Architecture

### Core Concept

Each evaluative pass runs as an independent subagent with its own context window. A parent orchestrator manages the run sequence, accumulates the Findings Ledger, and dispatches each pass with the inputs it needs.

### Execution Flow

```
Parent Orchestrator
├── Intake (in parent context)
│   ├── Load SKILL.md + run-core.md
│   ├── Read manuscript (for intake only)
│   ├── Generate contract
│   ├── Resolve pass set from concern
│   └── Initialize Findings Ledger
│
├── Pass 0+1 Subagent [opus]
│   ├── Receives: manuscript + framework + contract
│   ├── Produces: reverse outline + reader experience log + Focus Map
│   ├── Writes: Findings Ledger entries for Pass 0 and Pass 1
│   └── Returns: artifacts + ledger entries to parent
│
├── Pass 2 Subagent [opus]
│   ├── Receives: reverse outline + Focus Map excerpts + framework + ledger
│   ├── Produces: structural mapping artifact
│   ├── Writes: Findings Ledger entry for Pass 2
│   └── Returns: artifact + ledger entry to parent
│
├── Pass 5 Subagent [opus]
│   ├── Receives: reverse outline + Focus Map excerpts + framework + ledger
│   ├── Produces: character audit artifact
│   ├── Writes: Findings Ledger entry for Pass 5
│   └── Returns: artifact + ledger entry to parent
│
├── Pass 8 Subagent [opus]
│   ├── Receives: reverse outline + Focus Map excerpts + framework + ledger
│   ├── Produces: reveal economy artifact
│   ├── Writes: Findings Ledger entry for Pass 8
│   └── Returns: artifact + ledger entry to parent
│
└── Synthesis Subagent [opus]
    ├── Receives: reverse outline + complete Findings Ledger + framework
    │            + selected verification excerpts
    ├── Produces: editorial letter
    └── Writes: final deliverable
```

### The Focus Map (New Artifact)

Produced by the Pass 0+1 subagent. Tells later passes where to look in the manuscript.

**Format:**

```markdown
## Focus Map

### Pass 2: Structural Mapping
- **Chapters 7–8** (lines 4200–5100): Act transition zone. Causal chain unclear.
- **Chapters 14–16** (lines 9800–11400): Midpoint region. Energy drop noted in reader log.
- **Chapter 22** (lines 15600–16200): Climax approach. Promise resolution expected.
- **All chapter openings and closings** (first/last 200 words each): Transition mechanics.

### Pass 5: Character Audit
- **Scenes 12, 15, 31** (lines X–Y): Major character decisions. Motivation visible or absent.
- **Scenes 45–48** (lines X–Y): Agency collapse pattern (reader log: "protagonist disappears").
- **All dialogue-heavy scenes** (>60% dialogue ratio from reverse outline): Voice consistency.

### Pass 8: Reveal Economy
- **Chapters 3, 9, 18, 24** (lines X–Y): Major information reveals.
- **Scenes with POV shifts** (from reverse outline): Knowledge transfer points.
- **Final 3 chapters** (lines X–Y): Resolution and payoff zone.
```

**Design principles:**
- Err on inclusion. A 35k-token excerpt budget is better than a 20k-token budget that misses something.
- Organize by pass, not by manuscript order.
- Include rationale so the receiving pass understands *why* it should look at each section.
- The reverse outline (full scene-by-scene summary) always accompanies the excerpts — it provides the map; the excerpts provide the text.

### Pull-Based Retrieval (Evidence Appeals)

The Focus Map is push-based: Pass 0+1 decides what later passes should see. But even a good Focus Map will sometimes miss the actual diagnostic site. A pass working from the outline might identify a pattern that requires text it wasn't given.

**Mechanism:** Each selective-reading pass can issue a limited number of **evidence pulls** back to the parent orchestrator. The parent retrieves the requested excerpt from the manuscript file and returns it to the pass.

**Constraints:**
- Maximum 2 pulls per pass
- Maximum 5,000 tokens per pull
- Pull requests must specify: what text is needed (line range, scene number, or search term) and why (what hypothesis requires this evidence)
- The parent retrieves the excerpt mechanically — it does not interpret or filter

**Example pull requests:**
- "Need chapter 11, scenes 28–29 (~lines 7400–7800). The reverse outline shows a quiet conversation between X and Y, but the agency timeline suggests Y's motivation shifts here without visible cause. Need the actual dialogue to assess."
- "Need all scenes where [character] is alone (~3 scenes per reverse outline, lines TBD). Interiority pattern can't be assessed from outline summaries alone."

**Why this matters:** Pull-based retrieval converts the Focus Map from a single point of failure into a first-pass routing layer with due process. The Focus Map handles 90% of excerpt selection; evidence pulls handle the cases it missed. Token cost impact is modest: 2 pulls × 5k tokens × 3 selective passes = 30k additional tokens in the worst case.

**The reverse outline as hypothesis layer:** A critical design principle — the reverse outline is a navigation and hypothesis layer, not a substitute evidence layer. Passes should use the outline to identify *where* to look and to form hypotheses, but every substantial finding must ultimately be grounded in raw manuscript text, whether from Focus Map excerpts or evidence pulls. Pass-specific "must quote text" requirements ensure no finding rests solely on the outline's representation of a scene.

### Staged Visibility (Blind Review + Reconciliation)

To prevent cross-pass anchoring while preserving cross-pass learning, passes receive prior findings in two stages rather than all at once.

**Stage 1 — Independent analysis.** The pass receives:
- Contract and controlling idea
- Reverse outline
- Focus Map excerpts (in subagent mode) or full manuscript (in single-context mode)
- Framework instructions for this pass

It does NOT receive the Findings Ledger. The pass conducts its analysis independently and drafts its findings.

**Stage 2 — Reconciliation.** After drafting, the pass receives the relevant portions of the Findings Ledger and reconciles:
- **Confirmation:** "My finding on X aligns with Pass N's finding on Y. These likely share a root cause."
- **Contradiction:** "Pass N flagged X as a problem, but from my analytical lens, X is functioning correctly because Z."
- **Refinement:** "Pass N noted X in general terms. My analysis adds specificity: X occurs because of Y, concentrated in scenes A–C."
- **Integration note:** "Pass N's finding on X, combined with my finding on Y, suggests a cross-pass pattern that neither pass would identify alone."

**Why this works:** The pass generates its own signal before being exposed to prior passes' framing. This prevents false coherence (findings that merely echo earlier passes) while still enabling genuine cross-pass connections. The reconciliation step is where the ledger's cross-pass connections get built — with the pass's independent analysis as a baseline.

**Applicability in single-context mode:** This pattern doesn't require subagents. In single-context execution, the instruction is procedural: "Complete your pass analysis before reading the Findings Ledger. Then read the ledger and add a reconciliation section to your ledger entry." The model may not achieve perfect isolation (prior pass artifacts are still in context), but the explicit instruction to analyze first and reconcile second reduces anchoring.

**Applicability to synthesis:** The same pattern applies. The synthesis step drafts the editorial diagnosis from the Findings Ledger, then verifies against selected manuscript excerpts, then revises. This prevents the synthesis from overfitting to the ledger's framing.

### What the Findings Ledger Becomes

In single-context mode, the Findings Ledger solves context decay — it's a memory aid within one window. In subagent mode, it becomes the **inter-agent communication protocol**. Each subagent reads the accumulated ledger before starting its pass, writes its entry after finishing, and returns the entry to the parent for accumulation.

The ledger's cross-pass connections become more valuable in this architecture because the subagents genuinely can't see each other's full analysis. A cross-pass connection like "Pass 8's reveal timing issue at chapter 18 connects to Pass 5's motivation gap at scene 45" is information that neither subagent could generate alone — it requires the synthesis step (or a later pass reading the ledger) to connect them.

The retroactive promotion mechanism (v1.0.3) also gains importance: Pass 8 might read Pass 1's ledger entry and realize a "minor" belief failure is actually a symptom of the information flow problem Pass 8 just diagnosed. In single-context mode, the model might make this connection from residual context. In subagent mode, the ledger is the *only* way it happens.

---

## Token Cost Analysis

Estimates for a 118k-word manuscript (~157k tokens). Framework load ~23k tokens.

### Current Architecture (Single Context)

| Component | Tokens |
|-----------|--------|
| Manuscript (loaded once, persists) | 157,000 |
| Framework (persists) | 23,000 |
| Pass outputs (accumulating) | 15,000–40,000 |
| Conversation overhead | 5,000 |
| **Total context at synthesis** | **~200,000–225,000** |
| Output tokens (all passes + synthesis) | ~40,000 |
| **Total billed** | **~240,000** |

Cheap. But quality degrades as context fills.

### Naive Subagent (Every Pass Full Read)

Each pass loads the full manuscript independently.

| Step | Input tokens |
|------|-------------|
| Pass 0+1 | 180,000 |
| Pass 2 | 183,000 |
| Pass 5 | 184,000 |
| Pass 8 | 185,000 |
| Synthesis | 195,000 |
| **Total input** | **~927,000** |
| Output tokens | ~60,000 |
| **Total billed** | **~987,000** |

4x the current cost. Clean context per pass, but expensive.

### Hybrid (Recommended)

Pass 0+1 reads the full manuscript. Later passes read the reverse outline + Focus Map excerpts.

| Step | Input tokens | Notes |
|------|-------------|-------|
| Pass 0+1 (full read) | 180,000 | Produces outline + Focus Map |
| Pass 2 (selective) | 66,000 | Outline + ~30k excerpts |
| Pass 5 (selective) | 72,000 | Outline + ~35k excerpts |
| Pass 8 (selective) | 68,000 | Outline + ~30k excerpts |
| Synthesis | 61,000 | Ledger + outline + verification excerpts |
| **Total input** | **~447,000** |
| Output tokens | ~60,000 |
| **Total billed** | **~507,000** |

2.1x the current cost. Each pass has clean context. Later passes work from curated excerpts.

---

## Risks and Mitigations

### Pass 0+1 as single point of failure

The Focus Map determines what later passes see. If Pass 0+1 misjudges which sections matter for a specific analytical lens, that analysis is degraded.

**Mitigation:** Focus Map errs on inclusion. Budget 30–35k tokens of excerpts per pass rather than trying to minimize. The reverse outline (which always accompanies the excerpts) provides enough context for the pass to identify gaps and flag "I would need to see chapter X to confirm this."

### Loss of cross-pass context

In single-context mode, Pass 5 can "remember" what Pass 1 felt like reading. In subagent mode, it can only read Pass 1's structured output.

**Mitigation:** The Findings Ledger and the reader experience log. These are designed to capture the analytically relevant signal, not the full experience. Some nuance will be lost. Whether that nuance was actually contributing to better analysis (vs. just creating anchoring bias) is an empirical question.

### Platform dependency

Subagent orchestration depends on the Claude Code Task tool's model specification and file system access working reliably. These are confirmed functional as of February 2026 but could change.

**Mitigation:** The architecture is opt-in, not default. Single-context execution remains the primary mode. Subagent mode is an alternative for users who need maximum analytical quality and are willing to spend the tokens.

### Platform-level context compaction (unobservable) — First-Class Variable

The execution platform may be performing its own context management (compaction, summarization) below the model's level of awareness. User observation suggests this may already be happening — behavior patterns consistent with subagent dispatch or context handoffs have been noted during long runs. If so, some of the apparent "context salience decay" is not about token count — it's about which artifacts the platform chooses to preserve or compress during invisible handoffs.

**Implication:** This is unobservable from within the model but should be treated as a first-class experimental variable, not just a risk factor. The Findings Ledger helps regardless — whether salience decay comes from raw capacity limits, attention allocation failure, or invisible compaction, capturing findings at write-time prevents loss. But it means:

1. The subagent architecture might be solving a problem that improves without any framework changes as platforms mature.
2. Some of the quality benefit of the Findings Ledger may come from giving the platform's compaction algorithm something structured and concise to preserve, rather than forcing it to compress verbose pass artifacts.
3. Single-context hardening strategies (see below) may capture most of the subagent quality benefit at near-zero additional cost by making the existing context more compaction-resistant.

### Single-context hardening strategies (v1.x, low cost)

Before building subagent orchestration, these strategies may close most of the quality gap within the current architecture:

- **Write-time ledgering** — already shipped (v1.0.3)
- **Pass output minimization** — store terse, structured pass artifacts rather than verbose commentary. The artifact is a revision tool, not a narrative.
- **Artifact offloading** — write full pass artifacts to files, keep only ledger summaries in conversation context. Reduces context pressure without losing data.
- **Periodic re-grounding** — re-read the Findings Ledger and contract before each pass. Counteracts salience drift by refreshing the most important context.
- **Staged visibility** — analyze independently before reading prior pass findings (see §Staged Visibility above). Reduces anchoring in single-context mode.

These should be evaluated empirically before committing to the subagent architecture's token cost.

---

## Dependencies

| Dependency | Status | Notes |
|-----------|--------|-------|
| Findings Ledger | ✅ Shipped (v1.0.3) | Inter-pass communication protocol |
| Subagent model specification | ✅ Confirmed | Task tool accepts `model: opus` |
| Subagent file system access | ✅ Confirmed | Tested: read, write, bash all functional |
| Token budget visibility | ❌ Not available | No API to check remaining budget before starting a run |
| Pre-skill compaction hook | ❌ Not available | Would need platform support |
| Stable token pricing/budgeting | ⚠️ Uncertain | Weekly Cowork budgets make multi-read expensive |

---

## Decision Record

**2026-02-23:** Researched and prototyped. Confirmed subagent file system access and model inheritance work in Cowork sandbox. Decided NOT to build yet — token cost (2–5x current) is prohibitive given weekly Cowork budgets. Filed as v2.0+ roadmap item. The Findings Ledger (v1.0.3) addresses the quality problem at near-zero token cost and should be evaluated first.

**2026-02-24:** Ran controlled A/B test on "Coda: The Headboard" (~4,000 words). Results: Run B (swarm) produced 20 findings vs. Run A (single-context) 9; 10 cross-pass connections vs. 4; counterevidence on every finding vs. 1; synthesis preserved finding-level detail vs. aggressive compression. Swarm mode passes *complicated* each other's findings (analytically valuable) rather than merely *confirming* them (potential anchoring). Token cost: ~160k (swarm) vs. ~30k (single-context) — approximately 5x. Quality delta is real and attributable to architectural isolation, not just context capacity relief (manuscript was too short to stress context limits). Decision: ship as optional execution mode in v1.0.4, not a future item. Default remains single-context. Swarm mode is user-invoked for runs where maximum analytical quality justifies the token cost. See `Outputs/Swarm_Test/TEST_RESULTS.md` for full comparison.

**Open question:** The user observes behavior suggesting the platform may already dispatch subagents internally. If so, the framework's context decay may be partly caused by invisible orchestration handoffs — and the Findings Ledger may be solving a problem created by infrastructure, not just by context limits. This is unobservable from within the model but worth tracking as platform documentation improves.

---

## Future Architecture: Pass-Driven Re-Targeting

**Status:** Design concept (not built)
**Depends on:** Hybrid mode (v1.0.5)

### Problem

The hybrid mode focus map is locked at triage time. Pass 0+1 decides what later passes should see, and that decision is final — the only recourse is evidence pulls (2 per pass, reactive, limited to 5k tokens each). But analytical passes routinely discover things the triage subagent couldn't anticipate, because the triage subagent runs a reader-and-outliner lens, not a character lens or a reveal-economy lens.

**Concrete example from the 83k test:** Pass 5 (character audit) identifies a motivation discontinuity in Chapter 12. The character's decision doesn't follow from their established psychology. But the scene where the motivation was *established* — Chapter 7 — wasn't targeted by the focus map for Pass 5 because it looked structurally inert from the triage lens. Pass 5 can note the discontinuity and hypothesize about Chapter 7 using the reverse outline, but it can't read the actual prose. The finding is weaker than it would be with direct textual evidence.

Evidence pulls partially solve this — Pass 5 could spend one of its two pulls on Chapter 7. But evidence pulls are reactive and limited. The pass has to notice the gap, formulate the request, and receive the text mid-analysis. More importantly, two pulls per pass is a hard cap chosen for token economy, not analytical completeness.

### Proposed Mechanism: Appendable Focus Map

The focus map becomes a living document. After each analytical pass completes, the parent orchestrator checks whether the pass's findings imply re-targeting needs for subsequent passes.

**Execution flow:**

```
Parent Orchestrator
├── Pass 0+1 Subagent
│   └── Produces: Focus Map v1 (initial targeting)
│
├── Pass 2 Subagent (receives Focus Map v1 excerpts)
│   └── Returns: artifact + ledger entry + [optional] Re-Targeting Requests
│
├── Re-Targeting Check (parent, mechanical)
│   ├── Reads Pass 2's re-targeting requests
│   ├── Extracts requested excerpts from manuscript
│   └── Appends to Focus Map → Focus Map v2
│
├── Pass 5 Subagent (receives Focus Map v2 excerpts)
│   └── Returns: artifact + ledger entry + [optional] Re-Targeting Requests
│
├── Re-Targeting Check (parent, mechanical)
│   └── Focus Map v2 → Focus Map v3
│
├── Pass 8 Subagent (receives Focus Map v3 excerpts)
│   └── Returns: artifact + ledger entry + [optional] Re-Targeting Requests
│
└── Synthesis Subagent (receives final Focus Map excerpts)
```

### Re-Targeting Request Format

Each analytical pass may include a re-targeting section in its return payload:

```markdown
## Re-Targeting Requests

### For Pass 5 (Character Audit)
- **Chapter 7, scenes 18–19** (~lines 4200–4600): Motivation establishment site for
  [character]'s decision in Chapter 12. Need actual dialogue/interiority to assess
  whether the discontinuity I found is real or an outline compression artifact.
  **Reason:** My finding on motivation discontinuity (Ledger entry P2-F3) cannot be
  confirmed or dismissed without this text.

### For Pass 8 (Reveal Economy)
- **Chapter 4, scenes 9–10** (~lines 2100–2500): The structural mapping shows an
  information deposit here that doesn't pay off until Chapter 19. The outline suggests
  it's a plant, but the actual prose may reveal whether the plant is visible or buried.
  **Reason:** Reveal timing assessment requires knowing how conspicuously the
  information is presented, not just that it's present.
```

### Design Principles

**1. Re-targeting is forward-only.** A pass can request additional excerpts for *subsequent* passes, not for itself. This prevents the re-targeting mechanism from becoming an unlimited evidence pull. Pass 2 can say "Pass 5 should also look at Chapter 7" but cannot request Chapter 7 for its own re-analysis. (The pass's own evidence pulls serve the immediate need.)

**2. The parent orchestrator is mechanical.** It extracts the requested text and appends it to the focus map. It does not evaluate whether the request is analytically justified — that judgment belongs to the requesting pass. This keeps the orchestrator stateless and simple.

**3. Re-targeting requests are bounded.**

| Constraint | Limit | Rationale |
|-----------|-------|-----------|
| Max requests per pass | 3 | Prevents scope creep toward full manuscript re-read |
| Max tokens per request | 8,000 | Larger than evidence pulls (5k) because these target another pass's needs, which may span a longer scene |
| Max total re-targeting tokens per run | 40,000 | Hard ceiling. At this point, the manuscript is densely interconnected enough that swarm mode is the right choice |
| Requests must name the target pass | Required | Ensures excerpts are routed to the pass that needs them, not broadcast |

**4. Re-targeting is informational, not directional.** The request says "Pass 5 should have access to Chapter 7 because of finding P2-F3." It does *not* say "Pass 5 should find a motivation discontinuity in Chapter 7." The receiving pass gets the text and the cross-reference to the requesting pass's finding, but conducts its own analysis. This preserves staged visibility — the excerpt is delivered, not the conclusion.

**5. The focus map logs all re-targeting.** Each appended excerpt is tagged with its source:

```markdown
### [Appended by Pass 2 re-targeting — for Pass 5]
**Chapter 7, scenes 18–19** (lines 4200–4600)
**Requesting finding:** P2-F3 (motivation discontinuity, Chapter 12)
[excerpt text]
```

This creates an audit trail. Synthesis can see which passes drove re-targeting and whether the re-targeted excerpts actually produced findings — useful for evaluating whether the mechanism is adding signal or noise.

### How This Differs from Evidence Pulls

| Dimension | Evidence Pulls | Re-Targeting |
|-----------|---------------|-------------|
| **Timing** | During the pass's own analysis | After the pass completes, for future passes |
| **Beneficiary** | The requesting pass itself | A subsequent pass |
| **Limit** | 2 per pass, 5k tokens each | 3 per pass, 8k tokens each |
| **Mechanism** | Synchronous (pass pauses, parent retrieves, pass continues) | Asynchronous (appended to focus map between passes) |
| **Analytical direction** | Pass identifies its own gap | Pass identifies another lens's gap |

Both mechanisms serve the same principle: the focus map is a first-pass routing layer, not a final authority. Evidence pulls handle within-pass gaps; re-targeting handles cross-pass gaps.

### Token Cost Impact

Re-targeting adds excerpts to the focus map, increasing the input size for subsequent passes.

**Worst case (all passes use all 3 requests at max size):**
- 3 analytical passes × 3 requests × 8k tokens = 72k additional tokens
- But the 40k run ceiling caps total re-targeting at ~40k tokens
- Distributed across 2–3 receiving passes: ~13–20k additional tokens per pass

**Expected case (based on 83k test patterns):**
- Pass 2 re-targets 1–2 scenes for Pass 5 (~10k tokens)
- Pass 5 re-targets 1 scene for Pass 8 (~6k tokens)
- Pass 8 re-targets nothing (last analytical pass before synthesis)
- Total: ~16k additional tokens, increasing hybrid cost by ~3–5%

This is modest. The mechanism's value proposition is not token savings — it's analytical completeness on the specific findings that matter most.

### When Re-Targeting Becomes Swarm

The 40k-token ceiling on total re-targeting exists because beyond a certain point, the manuscript is too densely interconnected for selective reading. If every pass re-targets 3 scenes and the focus map is growing 30%+ per pass, the targeting architecture is fighting the manuscript rather than serving it.

**Diagnostic signal:** If total re-targeting tokens exceed 30k on a run, the focus map's coverage interpretation note should flag this: "This manuscript's analytical passes consistently needed text beyond the initial focus map. Swarm mode — where every pass reads the full manuscript — may be more appropriate."

### Open Questions

1. **Should synthesis also be able to re-target?** The synthesis subagent reads the ledger and reverse outline. It might identify a pattern that requires verification from manuscript text not in the focus map. Currently, synthesis gets "selected verification excerpts" (per the execution flow diagram above), but the selection is done by the parent orchestrator heuristically. Synthesis-initiated re-targeting would let the synthesis subagent request specific text for its own verification step. Risk: synthesis already has the most context of any step; adding re-targeting might push it toward context limits.

2. **Should the receiving pass know *why* it was re-targeted?** Current design: yes, the cross-reference to the requesting finding is included. Alternative: blind re-targeting, where the excerpt appears in the focus map without the requesting pass's interpretation. Blind re-targeting is purer (no anchoring from the cross-reference), but loses the navigational value of knowing why this scene matters to another lens. Current design favors navigation over purity, consistent with the focus map's existing rationale-included approach.

3. **Interaction with evidence pulls.** A pass that receives re-targeted excerpts may also use evidence pulls. Should re-targeted excerpts count against the evidence pull budget? Current design: no. Re-targeting and evidence pulls serve different functions (cross-pass vs. within-pass gaps) and have separate budgets. But total token growth needs monitoring.

---

## Future Architecture: Tiered Model Assignment

**Status:** Design concept (not built)
**Depends on:** Subagent orchestration (v1.0.4+)

### Problem

The current architecture assumes every subagent runs at the same model capability level (opus-class). But not every task in the pipeline requires frontier-level reasoning. Some tasks are mechanical text manipulation; some are narrow diagnostics; some require the full weight of synthesis, judgment, and editorial voice. Running everything at opus cost inflates the token bill without proportional quality benefit.

### Task Classification

Every step in the pipeline falls into one of three capability tiers:

#### Tier 1: Frontier (opus-class)

Tasks requiring judgment, synthesis, editorial voice, or resistance to sycophancy.

| Task | Why frontier |
|------|-------------|
| **Triage / Pass 0+1** | Reads full manuscript, builds reverse outline, produces focus map. Errors here propagate to every subsequent pass. Requires the reader-experience sensitivity that cheaper models lack. |
| **Synthesis** | Root cause analysis, cross-pass integration, adversarial stress test, editorial letter writing. The highest-judgment step in the pipeline. Also the step most vulnerable to sycophancy — cheaper models soften findings. |
| **Adversarial stress test** (within synthesis) | Must generate genuine attacks on the editorial argument, not token objections. Requires the model to argue against its own prior output. |

#### Tier 2: Analytical (sonnet-class)

Tasks requiring focused diagnostic reasoning within a constrained lens, but not full editorial synthesis or voice.

| Task | Why analytical tier may suffice | Risk if downtiered |
|------|-------------------------------|-------------------|
| **Pass 2 (structural mapping)** | Narrow lens: causal chains, scene function, act structure. Well-defined diagnostic categories. | May miss subtle structural effects that require reading between the lines of the outline. |
| **Pass 5 (character audit)** | Narrow lens: motivation, agency, arc coherence. Pass spec constrains the analysis. | May lose counterevidence quality — cheaper models find problems but don't stress-test their own findings. The 92% counterevidence rate from the 83k hybrid test is the benchmark to protect. |
| **Pass 8 (reveal economy)** | Narrow lens: information flow, reveal timing, knowledge management. | Same counterevidence risk as Pass 5. |
| **Full DE passes (3, 4, 6, 7, 9, 10)** | Each has a specific diagnostic lens. | These passes are less tested in subagent mode. Downtiering adds a second variable to an already uncertain equation. |

**Key uncertainty:** Whether counterevidence quality degrades at sonnet-tier. The framework's value proposition depends on findings that include "here's why I might be wrong." If cheaper models produce findings without counterevidence, the editorial letter loses its intellectual honesty — which is the thing that distinguishes APODICTIC output from generic AI feedback. This needs empirical testing before deployment.

#### Tier 3: Mechanical (haiku-class)

Tasks requiring text manipulation, formatting, or extraction with no analytical judgment.

| Task | Why mechanical tier suffices |
|------|----------------------------|
| **Excerpt extraction** | Pulling targeted scenes from the manuscript based on focus map line ranges. Pure text slicing — no interpretation, no judgment. |
| **Ledger formatting** | Compiling pass findings into the ledger's required format. The analytical content comes from the pass; the ledger formatter just structures it. |
| **Focus map re-targeting extraction** | Same as excerpt extraction: parent orchestrator identifies the text, haiku-tier model retrieves and formats it. |
| **Artifact file writing** | Writing pass outputs to disk in the correct naming convention. |
| **Token counting / cost estimation** | Estimating token usage for the run. Arithmetic, not analysis. |

### Proposed Assignment

```
Parent Orchestrator [frontier]
├── Intake + Contract                    [frontier]
├── Pass 0+1 (triage + focus map)        [frontier]
├── Excerpt Extraction                   [mechanical]
├── Pass 2 (structural mapping)          [analytical — pending test]
├── Ledger Formatting                    [mechanical]
├── Re-Targeting Extraction              [mechanical]
├── Pass 5 (character audit)             [analytical — pending test]
├── Ledger Formatting                    [mechanical]
├── Re-Targeting Extraction              [mechanical]
├── Pass 8 (reveal economy)              [analytical — pending test]
├── Ledger Formatting                    [mechanical]
├── Synthesis                            [frontier]
└── Artifact File Writing                [mechanical]
```

### Cost Impact Estimate

For an 83k manuscript in hybrid mode (current: all-opus at ~337k tokens):

| Step | Current (all frontier) | Tiered | Savings |
|------|----------------------|--------|---------|
| Pass 0+1 | ~126k opus tokens | ~126k opus | None |
| Excerpt extraction | (included in pass cost) | ~15k haiku | Minimal cost |
| Pass 2 | ~52k opus tokens | ~52k sonnet | ~60% on this step |
| Pass 5 | ~55k opus tokens | ~55k sonnet | ~60% on this step |
| Pass 8 | ~48k opus tokens | ~48k sonnet | ~60% on this step |
| Ledger formatting | (included in pass cost) | ~5k haiku × 3 | Negligible |
| Synthesis | ~56k opus tokens | ~56k opus | None |
| **Total cost reduction** | | | **~30–40%** (depending on per-model pricing ratios) |

The savings come almost entirely from downtiering the three analytical passes. The mechanical tasks are cheap at any tier.

### Testing Protocol

Before deploying tiered assignment, run the following comparison:

1. **Baseline:** Hybrid mode, all passes at opus. (Already have this from the 83k test.)
2. **Tiered:** Same manuscript, same focus map, analytical passes at sonnet.
3. **Comparison metrics:**
   - Finding count per pass
   - Counterevidence rate (% of findings with substantive "why I might be wrong")
   - Cross-pass complication rate (findings that genuinely challenge another pass's conclusions)
   - Synthesis quality (does the editorial letter preserve finding-level specificity?)
   - False positive rate (findings that, on re-read, are not actually problems)

**Pass/fail criterion:** If counterevidence rate drops below 75% (from the 92% baseline) at sonnet-tier, the quality loss outweighs the cost savings. Analytical passes stay at frontier.

**Intermediate option:** If sonnet-tier passes lose counterevidence but maintain finding count and accuracy, add an explicit counterevidence step: run the pass at sonnet, then run a counterevidence check on each finding at frontier. This costs less than running the full pass at frontier because the counterevidence step works from the pass's structured output, not the full manuscript.

### Open Questions

1. **Model-specific or tier-generic?** This design uses capability tiers (frontier/analytical/mechanical) rather than model names (opus/sonnet/haiku). The tier mapping changes as models improve — today's sonnet may handle counterevidence fine in six months. The framework should specify tiers and let the user (or a configuration file) map tiers to current models.

2. **Parent orchestrator tier.** The parent orchestrator currently runs at frontier because it handles intake and contract generation. But between dispatching passes, it does mechanical work (accumulating ledger entries, running re-targeting extraction). A split-tier parent — frontier for intake/synthesis, mechanical for inter-pass orchestration — would require the platform to support mid-conversation model switching, which is not currently available.

3. **Discovery-during-downtiering.** A sonnet-tier pass might miss a finding that an opus-tier pass would catch. Unlike counterevidence degradation (which is measurable on the same findings), missed findings are invisible — you can't measure what wasn't found. The testing protocol partially addresses this by comparing finding counts, but finding count alone doesn't capture finding *importance*. Need a qualitative assessment of whether the sonnet-tier findings are the *same* findings or just the *easy* findings.
