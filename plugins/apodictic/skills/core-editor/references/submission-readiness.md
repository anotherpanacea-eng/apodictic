# Submission Readiness Workflow
## Unified Diagnostic + Verdict + Query/Synopsis Assessment

**Status:** v1.1
**Entry point:** `/ready` command or `full_draft + submit` route via `/start`
**Requires:** Complete manuscript (artifact = `full_draft`)
**Runs:** Core DE (Passes 0, 1, 2, 5, 8) → Synthesis → Pass 11 (11A, 11B, 11C, 11D; 11E conditional)

---

## Purpose

A writer with a finished draft asks: "Is this ready to submit?" The Submission Readiness Workflow answers that question comprehensively. It runs the full diagnostic, renders an honest verdict, and assesses whether the manuscript's identity survives compression into query materials.

This is the thorough path. For deadline-constrained writers, Submission Triage (`references/submission-triage.md`) provides a single-pass go/no-go.

---

## When to Use

- Writer states submission, querying, or publication readiness as a goal
- Writer asks "is this ready?" without time constraints
- Writer wants query/synopsis diagnostic alongside structural feedback
- `/start` routes here when artifact = `full_draft`, goal = `submit`, no `constraint:time`

**When NOT to use:**

- Writer is on a deadline → Submission Triage
- Writer wants craft diagnosis without market intent → Core DE
- Manuscript is partial → Core DE only; this workflow requires complete arc

---

## Procedure

### Phase 1: Abbreviated Intake

The standard intake axis model applies, but with pre-filled values:
- **Artifact:** `full_draft` (confirmed)
- **Goal:** `submit` (confirmed)
- **Constraint:** check for `time` (if present, redirect to Submission Triage)

**Additional questions (submission-specific):**

1. **Publication path:** "Are you aiming for traditional publishing, self-publishing, or hybrid? This affects how I evaluate market positioning and query materials."
   - Traditional → activates 11C (Market Reality Check) with agent/editor frame, 11D (First-50 Conversion Gate)
   - Self-pub → activates 11C with reader-direct frame, 11D with Amazon preview frame
   - Hybrid → activates 11C with dual frame
   - Unsure → activates 11C with traditional frame as default, notes uncertainty

2. **Query materials:** "Do you have a query letter or synopsis draft? If so, I can assess those alongside the manuscript."
   - If yes → include in Pass 11 assessment; test compression fidelity
   - If no → generate compression test from manuscript (can the book's identity be captured in pitch-length form?)

3. **Execution mode:** Offer per §2b of `intake-router-runtime.md`. For submission readiness, the large-context version defaults to single-agent with swarm mentioned as upgrade; the standard-context version recommends hybrid or swarm.

### Phase 2: Core DE

Run the baseline pass set per `run-core.md`:
- **Pass 0:** Reverse Outline
- **Pass 1:** Reader Experience
- **Pass 2:** Structural Mapping
- **Pass 5:** Character Audit
- **Pass 8:** Reveal Economy

All standard execution protocols apply (Findings Ledger, staged visibility, pre-pass re-grounding). Execution mode follows Phase 1 selection.

### Phase 3: Synthesis

Run synthesis per `run-core.md`: root cause analysis (max 5), triage, adversarial self-check, adversarial reader stress test (§10), editorial letter.

The editorial letter is a standalone artifact, written to the active project output context beside the manuscript as usual. It does not change format for submission readiness; it's the same editorial letter as any Core DE run.

**Blind-spot rule:** If the Audit Invocation Log or editorial letter names a deferred or declined high-risk audit (especially AI-Prose Calibration, Consent Complexity, Reception Risk, or Series Continuity), carry that forward into the readiness assessment as an explicit confidence limiter. Do not present a blind-spot-limited run as fully de-risked.

### Phase 4: Pass 11

Run Pass 11 per `references/pass-11.md` with the following sub-pass activation:

| Sub-Pass | Name | Activation |
|----------|------|------------|
| **11A** | Writing Quality Diagnostic | Always |
| **11B** | Critical Verdict Protocol | Always |
| **11C** | Market Reality Check | Always (publication path determines frame) |
| **11D** | First-50 Conversion Gate | Always |
| **11E** | Revision Economics | Conditional: activates if verdict is CONDITIONALLY VIABLE or NOT READY |

Pass 11 consumes the Findings Ledger and editorial letter from Phase 3. It does not re-diagnose structural issues; it evaluates whether the diagnosed state is competitive.

### Phase 5: Compression Test

This phase is unique to the Submission Readiness Workflow. It does not exist in standalone Pass 11 runs.

**Purpose:** Test whether the manuscript's identity survives compression into query/pitch materials. A manuscript that reads well but resists pitching has a submission problem even if the prose is strong.

**If the writer provided query materials:**
- Read the query letter/synopsis
- Compare against the manuscript's actual controlling idea, structural spine, and arc resolution (from Passes 0, 2, 5)
- Flag mismatches: does the query promise what the manuscript delivers? Does the synopsis capture the actual spine or a simplified version?
- Assess pitch clarity: could an agent reconstruct the book's appeal from the query alone?

**If no query materials provided:**
- Attempt to compress the manuscript's identity into a one-sentence pitch, a two-paragraph query hook, and a one-page synopsis skeleton
- Assess compression friction: where does the manuscript resist compression? What gets lost?
- Flag SR codes from the compression attempt (see SR Code Integration below)

**Compression output:** Included in the unified readiness assessment, not as a standalone artifact.

### Phase 6: Unified Readiness Assessment

Produce the combined output per the template below. This is the primary deliverable of the Submission Readiness Workflow, distinct from the editorial letter (which is also produced but covers craft diagnosis, not submission readiness).

**Confidence and ceiling rule:** If a high-risk blind spot remains unresolved at the end of the run, confidence cannot exceed `MEDIUM`. If the blind spot materially affects ethics/governance legibility, category/reception exposure, or cross-volume consequence coherence, the verdict cannot exceed `CONDITIONALLY VIABLE` without an explicit rationale.

---

## SR Code Integration

The full Submission Readiness Workflow has access to all 15 SR codes (unlike Submission Triage, which sees only 7). Codes are populated from Core DE findings and the compression test:

| SR Code | Name | Source |
|---------|------|--------|
| SR-1 | Unhookable | Pass 1, 11D |
| SR-2 | Synopsis Sag | Pass 1, 2, compression test |
| SR-3 | Climax Deflation | Pass 1, 2, 8 |
| SR-4 | Voice Fracture | Pass 1, 11A |
| SR-5 | Stakes Scatter | Pass 1, 5, 8 |
| SR-6 | Protagonist Vanishes | Pass 1, 5 |
| SR-7 | Category Blur | 11C (Shelf Positioning) |
| SR-8 | Better Than It Sounds | Compression test |
| SR-9 | Setup Dependency | 11D, compression test |
| SR-10 | Spine Amnesia | Pass 0, 2, compression test |
| SR-11 | Comp Orphan | 11C |
| SR-12 | Tonal Whiplash | Pass 1 |
| SR-13 | Arc Substitution | Pass 5, compression test |
| SR-14 | Comp Fragility | 11C, compression test |
| SR-15 | Evidence Thinness | Compression test |

**Detection rule:** An SR code is populated only when the relevant source pass has run and produced evidence. Do not infer SR codes from passes that weren't executed.

---

## Output Template

```markdown
# Submission Readiness Assessment

**Project:** [TITLE]
**Date:** [YYYY-MM-DD]
**Genre:** [as stated by writer]
**Word Count:** [approximate]
**Publication Path:** [Traditional / Self-pub / Hybrid / Unsure]
**Assessment Type:** Full diagnostic (Core DE + Pass 11 + Compression Test)

---

## Readiness Verdict: [READY / CONDITIONALLY VIABLE / NOT READY]

[2-3 sentence plain-language summary. What this verdict means for the writer's next step.]

**Confidence:** [HIGH / MEDIUM] — [brief basis for confidence level]

**Blind Spots:** [None, or 1-3 bullets naming deferred/declined high-risk audits and how they limit readiness confidence]

---

## The Short Version

[One paragraph: the honest assessment a trusted mentor would give. No framework jargon. What's working, what isn't, and what the writer should do next. This paragraph should be quotable — something the writer could read to a friend and get useful clarity.]

---

## Diagnostic Summary

[3-5 sentences synthesizing the editorial letter's root causes. Reference the editorial letter for full analysis; don't repeat it here. Focus on how the diagnostic findings affect submission readiness specifically.]

**Editorial letter:** See `[Project]_Editorial_Letter_[date].md` for full diagnostic.

---

## Writing Quality (Pass 11A)

**Prose Tier:** [P0 / P1 / P2 / P3] — [plain-language translation]
**Voice:** [DISTINCTIVE / DEVELOPING / GENERIC]
**Scene Voltage:** [Consistent / Uneven / Low]

[3-5 sentence summary. What's strong at the prose level, what needs work, and how it affects submission readiness.]

---

## Critical Verdict (Pass 11B)

| Lens | Verdict | Key Observation |
|------|---------|-----------------|
| Acquiring Editor | [ACQUIRE / R&R / PASS] | [1-2 sentences] |
| Category Super-Reader | [RECOMMEND / MIXED / WNF] | [1-2 sentences] |
| Skeptical Critic | [NOTABLE / COMPETENT / DERIVATIVE] | [1-2 sentences] |

**Lens Agreement:** [3/3 / 2/3 / Split]
[Note significant disagreements and what they mean.]

### Hard Truths

1. [CONFIDENCE] [Direct statement + consequence]
2. [CONFIDENCE] [Direct statement + consequence]
3. [CONFIDENCE] [Direct statement + consequence]
[4-5 if applicable]

---

## Market Reality (Pass 11C)

**Commercial Snapshot:** [1 paragraph]

**Submission Frictions:**
1. [Friction + evidence basis]
2. [Friction + evidence basis]
3. [Friction + evidence basis]

**Path Recommendation:** [Traditional-first / Hybrid / Self-pub-first]
**Rationale:** [2-3 sentences]

**Shelf Gate:** [CLEAR / BLOCKED — reason]

---

## Opening Assessment (Pass 11D)

**Conversion Gate:** [PASS / BORDERLINE / FAIL]
**Abandonment Risk:** [LOW / MEDIUM / HIGH]

[Summary with specific page references. Where would an agent stop? Where would a reader stop?]

---

## Compression Test

**Pitch clarity:** [CLEAR / MUDDY / RESISTANT]

[Does the manuscript's identity survive compression? Can its appeal be captured in query-length form?]

**SR Codes Detected:**

| Code | Name | Severity | Source | Evidence |
|------|------|----------|--------|----------|
| [SR-X] | [Name] | [P1/P2/P3] | [Pass] | [Brief] |

[If writer provided query materials:]
### Query Assessment
- **Fidelity:** Does the query match what the manuscript delivers?
- **Hook strength:** Would an agent request pages?
- **Gaps:** What's missing or misrepresented?

[If no query materials:]
### Compression Friction
- **One-sentence pitch attempt:** [pitch]
- **Where compression resists:** [what gets lost or distorted]
- **SR-8 (Better Than It Sounds):** [present / absent — assessment]

---

## Revision Economics (Pass 11E) [If verdict is not READY]

| Issue | Effort | Blast Radius | Payoff | Priority |
|-------|--------|--------------|--------|----------|
| [...] | [...] | [...] | [...] | [...] |

**Quick Wins:** [3-5 items]

**Dependencies:** [ordering constraints]

---

## Non-Negotiables [If CONDITIONALLY VIABLE or NOT READY]

**#1:** [Issue]
- Evidence: [specific locations]
- Blast Radius: [Local / Multi-scene / Systemic]
- Consequence: [what happens if unfixed — commercial or craft/reader frame per publication path]
- Lens Agreement: [which lenses flagged this]

[Repeat for #2-5 as needed]

---

## Pre-READY Verification [Required for READY verdict]

| Check | Status | Notes |
|-------|--------|-------|
| Chapter/section numbering | ✓/✗ | |
| Timeline math | ✓/✗ | |
| Thread resolution | ✓/✗ | |
| Arc bridge beats | ✓/✗ | |
| Prose consistency (distributed sample) | ✓/✗ | |
| Adversarial critique completed | ✓/✗ | |

[If any ✗, verdict cannot be READY]

---

## What to Do Next

[Concrete, prioritized guidance based on the verdict:]

[If READY:]
- Submit. The manuscript is competitive for [stated path].
- [Any polish items from the editorial letter, framed as "while you query" tasks.]

[If CONDITIONALLY VIABLE:]
- Address the non-negotiables above before submitting.
- Estimated revision scope: [brief assessment].
- Recommended sequence: [dependency-ordered list].
- Consider re-running submission triage after revisions to confirm fix.

[If NOT READY:]
- This manuscript needs revision before it's competitive.
- The editorial letter identifies root causes. Start there.
- [If structural:] The issues are architectural, not surface-level. Budget for a substantial revision pass.
- [If prose:] The structural foundation is sound, but prose quality needs development. This is fixable.
- When you've revised, run `/ready` again or a targeted `/diagnose` on the specific concerns.

---

*Submission Readiness Assessment — APODICTIC Development Editor v1.1*
*Full diagnostic: Core DE (Passes 0, 1, 2, 5, 8) + Synthesis + Pass 11 + Compression Test*
```

---

## Integration Notes

### Router wiring
- `full_draft + submit + —` → Submission Readiness Workflow (this file)
- `full_draft + submit + time` → Submission Triage (`references/submission-triage.md`)
- `full_draft + submit + hybrid/swarm` → Submission Readiness Workflow with specified execution mode

### Command shortcut
`/ready` invokes this workflow directly, bypassing the `/start` router's Q1-Q3 sequence. The command pre-fills artifact = `full_draft` and goal = `submit`, then runs the abbreviated intake (publication path, query materials, execution mode).

### Relationship to Submission Triage

| Dimension | Triage | This Workflow |
|-----------|--------|---------------|
| Passes run | 1 only | All Core DE + Pass 11 |
| SR codes available | 7 of 15 | All 15 |
| Generates query/synopsis diagnostic | No | Yes (compression test) |
| Stress tests | None | Adversarial (editorial letter §10) + compression |
| Blind spots | Named explicitly | Named when present; high-risk blind spots cap confidence |
| Output | Triage memo (1-2 pages) | Full assessment + editorial letter |
| Time | ~15 min | Full diagnostic run |

### Relationship to standalone Core DE + Pass 11

A writer can reach roughly the same analytical coverage by running Core DE with goal = `submit`, which routes to Core DE → Pass 11. The Submission Readiness Workflow adds:

1. **The compression test** — standalone Core DE + Pass 11 does not test whether the manuscript's identity survives pitching
2. **The unified readiness assessment** — a single document that synthesizes diagnostic findings, verdict, market reality, and next steps instead of requiring the writer to cross-reference the editorial letter and Pass 11 output
3. **SR code population** — the full 15-code submission readiness vocabulary, mapped across all passes and the compression test
4. **Abbreviated intake** — pre-filled axes reduce friction for writers who know they want submission assessment

### Artifact locations

All artifacts go to the active project output context beside the manuscript:
- `[Project]_Editorial_Letter_[date].md` — standard editorial letter from synthesis
- `Submission_Readiness_Assessment_[date].md` — the unified output from this workflow
- Pass artifacts and Findings Ledger in their standard locations
- `Diagnostic_State.md` — updated with QF flags and SR codes from Pass 11

### Re-entry

If the writer revises and returns, they can:
- Run `/ready` again for a full re-assessment
- Run Submission Triage for a quick re-check
- Run a targeted `/diagnose` on specific concerns from the non-negotiables
