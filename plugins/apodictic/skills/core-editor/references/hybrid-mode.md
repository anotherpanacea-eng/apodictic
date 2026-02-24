# Hybrid Mode — Focus Map Architecture

*Reference file for the APODICTIC Development Editor. Loaded when hybrid execution mode is selected.*

**Status:** Specification (untested)
**Version:** Draft 1
**Date:** 2026-02-24

---

## Overview

Hybrid mode is an execution mode between single-context and full swarm. Pass 0+1 reads the entire manuscript and produces a **focus map** alongside the standard reverse outline and reader experience log. Subsequent passes load the reverse outline (the compressed manuscript) plus only the excerpts the focus map targets — not the full text.

**Cost profile:** Approximately 2–3x the tokens of single-context (~500–690k for a 118k-word manuscript), versus swarm's ~5x (~1.2M).

**Quality profile:** Architectural isolation for later passes (each runs in its own context), with the outline serving as compressed manuscript representation. Later passes see the full structure but deep-read only where the focus map directs them. Risk: the focus map misses something Pass 0+1 didn't recognize as significant from an outliner/reader lens.

---

## Architecture

### Pass Grouping

| Subagent | Passes | Input | Output |
|----------|--------|-------|--------|
| **Triage subagent** | Pass 0 + Pass 1 (combined) | Full manuscript, contract | Reverse outline, reader experience log, **focus map**, initial ledger entries |
| **Pass 2 subagent** | Pass 2: Structural Mapping | Reverse outline, focus map excerpts (structural), contract, accumulated ledger | Beat map, causal chain, structural flags, ledger entry |
| **Pass 5 subagent** | Pass 5: Character Audit | Reverse outline, focus map excerpts (character), contract, accumulated ledger | Character cards, agency timeline, ledger entry |
| **Pass 8 subagent** | Pass 8: Reveal Economy | Reverse outline, focus map excerpts (information), contract, accumulated ledger | Reveal ledger, fairness flags, ledger entry |
| **Synthesis subagent** | Synthesis | Reverse outline, complete Findings Ledger, focus map excerpts (verification) | Editorial letter |

### Why Pass 0+1 Is the Triage Subagent

Both Pass 0 and Pass 1 require full sequential reading. Pass 0 builds the reverse outline by documenting what literally happens in each scene. Pass 1 tracks naive reader experience — boredom, confusion, delight, belief failures — which requires reading the manuscript as a reader reads it: in order, without skipping.

No other pass combination requires the full text in the same way. Passes 2, 5, and 8 analyze *patterns* across the manuscript — structural architecture, character psychology, information flow — which the reverse outline captures in compressed form. What they need beyond the outline is targeted access to specific scenes where the pattern is under pressure.

The triage subagent's dual role — outlining *and* reading — gives it two complementary lenses for focus map construction. The outliner sees structural anomalies (arbitrary breaks, orphan scenes, unusual ratios). The reader sees experiential failures (belief breaks, immersion drops, promise drift). Together these catch more targets than either lens alone.

---

## Focus Map Specification

### What the Focus Map Is

A structured document produced by the triage subagent (Pass 0+1) that tells each subsequent pass which manuscript excerpts to deep-read beyond the reverse outline. It is a targeting instrument, not an analysis — it says *where to look* and *why*, not *what's wrong*.

### What the Focus Map Is Not

- Not a diagnosis. The focus map does not assign severity, root causes, or recommendations. Those are the later passes' jobs.
- Not a filter. Later passes still receive the complete reverse outline and can reason about any scene's structural role. The focus map targets *deep reading* — access to the actual prose, dialogue, interiority — not analytical attention.
- Not exhaustive. The focus map will miss things. The mitigation strategies (confidence tiers, broad-net targets, the outline as safety net) reduce but do not eliminate this risk.

### Output Format

The focus map is saved as `[Project]_Focus_Map_[runlabel].md` alongside the reverse outline.

```markdown
# Focus Map

## Manuscript Information
**Title:** [Title]
**Triage subagent date:** [Date]
**Total scenes:** [N]
**Scenes targeted:** [N] ([%] of total)

---

## Targeting by Pass

### Pass 2: Structural Mapping

#### High-Confidence Targets
[Scenes where structural analysis clearly needs the actual prose.]

| Scene | Location | Targeting Rationale | What to Examine |
|-------|----------|-------------------|-----------------|
| [#] | [Ch/section] | [Why this scene needs deep reading for structural analysis] | [Specific structural question the prose can answer] |

#### Broad-Net Targets
[Scenes where something structural *might* be happening that the outline can't fully capture.]

| Scene | Location | Signal Detected | Confidence Note |
|-------|----------|----------------|-----------------|
| [#] | [Ch/section] | [What Pass 0/1 noticed] | [Why this might or might not matter structurally] |

---

### Pass 5: Character Audit

#### High-Confidence Targets

| Scene | Location | Targeting Rationale | What to Examine |
|-------|----------|-------------------|-----------------|
| [#] | [Ch/section] | [Why this scene needs deep reading for character analysis] | [Specific character question the prose can answer] |

#### Broad-Net Targets

| Scene | Location | Signal Detected | Confidence Note |
|-------|----------|----------------|-----------------|
| [#] | [Ch/section] | [What Pass 0/1 noticed] | [Why this might or might not matter for character] |

---

### Pass 8: Reveal Economy

#### High-Confidence Targets

| Scene | Location | Targeting Rationale | What to Examine |
|-------|----------|-------------------|-----------------|
| [#] | [Ch/section] | [Why this scene needs deep reading for information flow] | [Specific information-flow question the prose can answer] |

#### Broad-Net Targets

| Scene | Location | Signal Detected | Confidence Note |
|-------|----------|----------------|-----------------|
| [#] | [Ch/section] | [What Pass 0/1 noticed] | [Why this might or might not matter for information flow] |

---

### Synthesis: Verification Excerpts

[Scenes the synthesis subagent should have access to for verifying specific editorial letter claims. Populated during the run as passes identify key evidence scenes — the triage subagent seeds this with scenes it expects will be cited.]

| Scene | Location | Expected Relevance |
|-------|----------|--------------------|
| [#] | [Ch/section] | [Why synthesis might need to verify a claim against this scene's prose] |

---

## Cross-Pass Targets

[Scenes flagged for multiple passes. These are often the most analytically productive excerpts — the intersection of structural, character, and information concerns.]

| Scene | Location | Passes | Signal |
|-------|----------|--------|--------|
| [#] | [Ch/section] | [2, 5] | [What makes this scene relevant to both] |

---

## Coverage Statistics

| Pass | High-Confidence Scenes | Broad-Net Scenes | Total Unique Scenes | Est. Token Load |
|------|----------------------|------------------|--------------------|-----------------|
| Pass 2 | [N] | [N] | [N] | [~Nk] |
| Pass 5 | [N] | [N] | [N] | [~Nk] |
| Pass 8 | [N] | [N] | [N] | [~Nk] |
| Synthesis | [N] | — | [N] | [~Nk] |
| **Total unique** | | | [N] ([%] of manuscript) | [~Nk] |
```

### Targeting Grammar

Each focus map entry answers three questions:

1. **Where?** Scene number and location in manuscript (matching the reverse outline's scene numbering).
2. **Why?** What the triage subagent detected that makes this scene worth deep-reading for a specific pass. This is a signal description, not a diagnosis.
3. **What to look for?** The specific analytical question the later pass should bring to the prose. This frames the deep reading — not "analyze this scene" but "check whether the protagonist's decision here is motivated by the setup in Scene 12 or comes from nowhere."

### Targeting Rationale Categories

The triage subagent should draw from these signal types when building the focus map. Not every category will fire for every manuscript; this is a recognition vocabulary, not a checklist.

**From Pass 0 (Outliner Lens):**

| Signal | What It Looks Like | Relevant Passes |
|--------|-------------------|-----------------|
| Arbitrary scene break | Scene ends without conflict resolution, decision, or natural break | 2 (causal chain), 5 (agency) |
| Unusual ratio | Scene has extreme dialogue/action/interiority skew vs. manuscript average | 2 (pacing), 5 (interiority), 8 (information delivery) |
| Word count anomaly | Scene is 2x+ or 0.5x average length without clear structural reason | 2 (pacing, proportional analysis) |
| Information density spike | Scene delivers 3+ new pieces of information | 8 (reveal economy, information overload) |
| Information vacuum | Scene advances time without delivering new information | 2 (orphan scene test), 8 (pacing of reveals) |
| Transition mechanism unclear | How the scene connects to the next is ambiguous from outline alone | 2 (causal chain gaps) |
| POV shift | Scene changes POV character | 5 (voice consistency), 8 (knowledge management) |

**From Pass 1 (Reader Lens):**

| Signal | What It Looks Like | Relevant Passes |
|--------|-------------------|-----------------|
| Belief failure | "I don't believe this decision/reaction/coincidence" | 5 (motivation, agency), 8 (information the character has) |
| Orientation failure | "Where am I? When? Who's speaking?" | 2 (structural anchoring), 8 (information management) |
| Boredom signal | "I would skim or skip" | 2 (pacing, orphan scene), 5 (low-agency passage) |
| Emotional spike | Strong positive or negative reader response | 5 (character craft), 8 (reveal timing) |
| Promise drift | What the book seems to offer shifts from what the contract says | 2 (structural alignment), 5 (character arc alignment) |
| Immersion break | Something pulls the reader out of the fictional world | 5 (voice drift), 8 (unfair misdirection) |
| "I would stop reading" | Strongest negative signal — something is actively driving the reader away | All passes (cross-pass target) |

**Composite Signals (both lenses together):**

| Signal | What It Looks Like | Relevant Passes |
|--------|-------------------|-----------------|
| Structural pivot + belief failure | A major turning point where the reader doesn't buy what happens | 2 + 5 (cross-pass target) |
| Information spike + emotional flatness | A lot is revealed but nothing lands | 8 + 5 (cross-pass target) |
| Arbitrary break + orientation failure | Scene ends abruptly and the next scene's opening is disorienting | 2 + 8 (cross-pass target) |

---

## Confidence Tiers

### High-Confidence Targets

Scenes where the triage subagent can articulate a specific analytical question that requires the actual prose to answer. The signal is clear and the relevant pass is obvious.

**Inclusion threshold:** The triage subagent can complete the sentence: "Pass [N] needs to read this scene because [specific question] cannot be answered from the outline alone."

**Examples:**
- "Pass 5 needs to read Scene 31 because the protagonist makes a major decision with no visible motivation in the outline — the prose may contain interiority that explains it, or may confirm the motivation gap."
- "Pass 8 needs to read Scene 18 because the outline shows three revelations in one scene — the prose will reveal whether they're sequenced effectively or pile up."

### Broad-Net Targets

Scenes where the triage subagent detected a signal but can't articulate a precise analytical question. Something seems worth examining, but the triage subagent's lenses (outliner + reader) aren't the right tools to say exactly what.

**Inclusion threshold:** The triage subagent can complete the sentence: "Something about this scene made me [notice/pause/flag it], but the specific diagnostic question is for Pass [N] to determine."

**Examples:**
- "Scene 11 reads fine as a reader and outlines normally, but the protagonist's dialogue feels different here — Pass 5 may want to check voice consistency."
- "Scene 22 has normal information delivery but the emotional temperature drops to zero between two high-emotion scenes — Pass 5 or Pass 8 may find this significant."

### The Inclusion Bias

**When in doubt, include the scene as a broad-net target.** The cost of including an unnecessary scene is marginal (a few hundred extra tokens per scene). The cost of missing a scene that a later pass needed is an analytical blind spot that can't be recovered.

The focus map should target roughly **30–50% of the manuscript's scenes** across all passes combined. If targeting falls below 25%, the triage subagent is being too conservative. If it exceeds 60%, the hybrid mode's token savings are diminishing and the user should consider full swarm instead.

---

## Excerpt Extraction Protocol

When the parent orchestrator dispatches a later-pass subagent, it constructs the subagent's input by:

1. **Loading the full reverse outline.** Every later pass receives the complete outline — this is the compressed manuscript representation and is always included.

2. **Extracting targeted scenes.** For each scene in the pass's focus map (both high-confidence and broad-net), extract the full scene text from the manuscript file. Use the reverse outline's scene boundaries (location markers) for extraction.

3. **Formatting the excerpt package.** Present excerpts in manuscript order with clear scene markers:

```markdown
## Targeted Excerpts for Pass [N]

*These excerpts were selected by the triage subagent's focus map.
The full reverse outline provides structural context for all scenes;
these excerpts provide the actual prose for targeted deep reading.*

### Scene [#] — [Location] (High-Confidence)
**Targeting rationale:** [From focus map]
**What to examine:** [From focus map]

[Full scene text]

---

### Scene [#] — [Location] (Broad-Net)
**Signal detected:** [From focus map]
**Confidence note:** [From focus map]

[Full scene text]

---

[Continue for all targeted scenes]
```

4. **Calculating token load.** Report the estimated token count for the excerpt package in the subagent dispatch. If the excerpt package exceeds 80k tokens for a single pass, flag this to the user — it suggests the manuscript may be better served by full swarm mode.

---

## Risk and Mitigation

### Primary Risk: Missed Scenes

The focus map is built from two analytical lenses (outliner + reader), but later passes bring different lenses (structural architect, character psychologist, information-flow analyst). A scene that reads fine and outlines normally may contain a subtle character motivation break that only Pass 5's lens would recognize.

**Mitigations (in order of implementation priority):**

1. **The reverse outline as safety net.** Every later pass sees the full outline. If the outline's scene summary suggests something worth investigating, the pass can flag it in its findings even without the prose. The finding would note: "Scene [N] may warrant closer examination — the outline suggests [X] but prose-level analysis was not available in this run." This creates a record of the gap, even if it can't fill it.

2. **Broad-net inclusion bias.** The focus map errs on inclusion (see §Confidence Tiers). Targeting 30–50% of scenes means the majority of analytically productive scenes are covered. The scenes most likely to be missed are ones that seem unremarkable from *every* available lens — which are, by definition, the scenes least likely to contain significant findings.

3. **Cross-pass targets.** Scenes flagged for multiple passes are often the most analytically productive. The focus map's cross-pass target section ensures these scenes aren't accidentally omitted from any relevant pass.

4. **Synthesis verification excerpts.** The synthesis subagent receives a small set of scenes identified during the run as key evidence. If a pass's finding depends on a specific scene's prose, the synthesis can verify the claim directly rather than relying on the pass's characterization alone.

### Secondary Risk: Focus Map Quality Variance

The quality of the focus map depends on the triage subagent's analytical sensitivity. A less attentive triage run produces a thinner focus map, which cascades into thinner later passes.

**Mitigations:**

1. **Structured targeting vocabulary.** The targeting rationale categories (§Targeting Grammar) provide a recognition vocabulary that reduces the chance of the triage subagent overlooking a signal type. It doesn't have to generate the categories — it recognizes and records them.

2. **Coverage statistics as self-check.** The focus map includes a coverage table. If targeting falls below 25% of scenes, the triage subagent is prompted to reconsider whether it's being too conservative. This is a soft guardrail, not a hard constraint.

3. **Single-context fallback.** If the focus map produces fewer than 10 targets across all passes, the parent orchestrator should flag this to the user and suggest single-context mode may be more appropriate for this manuscript (the manuscript may not have enough complexity to benefit from hybrid mode's analytical separation).

### Tertiary Risk: Excerpt Boundary Errors

Scene extraction depends on the reverse outline's location markers being accurate enough to extract clean scene boundaries from the manuscript file.

**Mitigation:** The reverse outline already records scene locations as part of Pass 0's standard output. Hybrid mode depends on these being precise enough for extraction (chapter/section markers, ideally with line number ranges). If the manuscript lacks clear scene breaks, the triage subagent should note this in the focus map metadata and the parent orchestrator should fall back to chapter-level extraction.

---

## Token Cost Model

Estimates for a 118,000-word manuscript (~180k tokens of raw text).

| Component | Single-Context | Hybrid | Full Swarm |
|-----------|---------------|--------|------------|
| Triage (Pass 0+1) | — | ~250k (full read + focus map generation) | ~250k |
| Pass 2 input | (shared context) | ~80k (outline 40k + excerpts ~40k) | ~220k (full manuscript) |
| Pass 5 input | (shared context) | ~95k (outline 40k + excerpts ~55k) | ~220k (full manuscript) |
| Pass 8 input | (shared context) | ~90k (outline 40k + excerpts ~50k) | ~220k (full manuscript) |
| Synthesis input | (shared context) | ~70k (outline 40k + ledger + verification excerpts) | ~80k (ledger + excerpts) |
| **Estimated total** | **~240k** | **~500–690k** | **~1,000–1,200k** |
| **Cost multiplier** | **1x** | **~2–3x** | **~5x** |

These estimates assume:
- Reverse outline compresses the manuscript to ~20–25% of original token count (~40k tokens)
- Focus map targets 30–50% of scenes per pass (with overlap across passes)
- Each targeted scene averages ~1,500 tokens of prose
- Output tokens (analysis, ledger entries, focus map) add ~15–20% overhead per subagent

---

## Integration with Existing Modes

Hybrid mode uses the same pass specifications, Findings Ledger protocol, staged visibility rules, and synthesis format as single-context and swarm modes. The only differences are:

1. **The focus map is a new output** from Pass 0+1, produced only in hybrid mode.
2. **Later passes receive excerpts instead of the full manuscript.** Their analytical instructions are identical; their input is narrower.
3. **The parent orchestrator performs excerpt extraction** — a step that doesn't exist in swarm mode (where each subagent loads the full manuscript) or single-context mode (where the manuscript is already in context).

The intake router presents hybrid as a third execution mode option. The recommendation logic:
- **Single-context:** Default. Manuscripts under ~60k words, budget-constrained runs, quick diagnostics.
- **Hybrid:** Manuscripts over ~60k words where the user wants better-than-single-context quality without full swarm cost. The sweet spot for most serious editorial runs.
- **Swarm:** Maximum depth. Final-round diagnostics before submission, or when prior runs felt thin.

---

## Open Questions for Testing

1. **Optimal scene targeting percentage.** The spec says 30–50%. Does this hold across manuscript lengths and genres? A 40k-word novella may need 60% targeting to be useful; a 150k-word novel may work fine at 25%.

2. **Focus map quality across genres.** The targeting rationale categories are genre-agnostic. Do genre-specific signals (e.g., horror dread architecture, mystery clue placement) require genre-tuned focus map categories, or does the broad vocabulary capture them adequately?

3. **Outline compression ratio.** The spec assumes the reverse outline compresses to ~20–25% of manuscript tokens. Does this hold? If it's closer to 30–35%, the token savings are smaller.

4. **Broad-net signal value.** How often do broad-net targets (low-confidence signals) produce findings that high-confidence targets miss? If the answer is "rarely," the broad-net tier is insurance with minimal analytical payoff. If "often," the inclusion bias is essential.

5. **Synthesis verification adequacy.** Does the synthesis subagent have enough access to prose to write a credible editorial letter, or does it need more excerpts than the focus map anticipates?
