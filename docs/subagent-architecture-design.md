# Subagent Pass Orchestration — Design Document

**Status:** Future (v2.0+)
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

**Open question:** The user observes behavior suggesting the platform may already dispatch subagents internally. If so, the framework's context decay may be partly caused by invisible orchestration handoffs — and the Findings Ledger may be solving a problem created by infrastructure, not just by context limits. This is unobservable from within the model but worth tracking as platform documentation improves.
