# Submission Triage
## Single-Pass Go/No-Go Assessment

**Status:** v1.1
**Trigger:** `constraint:time` flag in intake router
**Requires:** Complete manuscript (artifact = `full_draft`)
**Does not require:** Core DE passes, Pass 11, Shelf Positioning

---

## Purpose

A writer on a deadline asks: "Should I submit this now, or not?" The triage answers that question from a single read-through. It does not diagnose the manuscript comprehensively. It catches what one experienced read can catch and names what it can't see.

**What this is:** A single-pass reader-experience assessment that maps findings to submission-blocking severity and produces a go/no-go verdict.

**What this is not:** A developmental edit. A submission readiness diagnostic. A substitute for the full workflow. The triage cannot assess structural compression, spine integrity, or market positioning because those require passes it doesn't run.

---

## When to Use

- Writer has a deadline and needs a quick answer
- Writer wants to know if it's worth submitting now vs. waiting for a full edit
- Writer wants a sanity check before querying

**When NOT to use:**

- Writer has time for a full edit (route to Core DE)
- Writer wants query/synopsis feedback (route to Submission Readiness Workflow)
- Manuscript is partial (triage requires complete arc to assess)

---

## Procedure

### Step 1: Intake Confirmation

Confirm with the writer:

> "This is a single-pass read — I'll tell you whether to submit now or wait. It catches reader-experience problems but cannot assess structural architecture, market positioning, or how well the manuscript compresses into query materials. If you have time for the full workflow, that's always better. Want to proceed?"

If the writer opts for the full workflow instead, route to Core DE → Pass 11.

### Step 2: Run Pass 1 (Reader Experience)

Execute Pass 1 per `run-core.md` specifications. Read the complete manuscript. Record findings as normal.

### Step 3: Map Findings to Triage Severity

For each Pass 1 finding, classify severity:

| Triage Severity | Meaning | Threshold |
|---|---|---|
| **P1 — Submission-blocking** | An agent or editor would stop reading here. The problem is visible on first read and severe enough to generate a rejection before finishing. | Opening doesn't hook; protagonist unclear or passive for extended stretches; middle collapses into event-listing; ending doesn't resolve; voice breaks character |
| **P2 — Weakness** | Noticeable on first read but wouldn't necessarily stop a reader who's otherwise engaged. Weakens the submission but doesn't kill it. | Pacing drag in specific sections; tonal wobble that self-corrects; stakes that thin in the middle but recover; secondary character flatness |
| **P3 — Minor** | Craft-level issues visible on close read. Not submission-relevant for triage purposes. | Sentence-level rhythm issues; minor continuity gaps; dialogue tics |

**Severity assignment draws on Pass 1 findings only.** Do not infer structural diagnoses that require passes the triage hasn't run. If a finding *suggests* a deeper structural problem but Pass 1 can't confirm it, note it in the blind spots section, not as a P1 finding.

### Step 4: Apply SR Codes (Where Detectable)

Map Pass 1 findings to SR codes where the reader-experience evidence is sufficient. Not all SR codes are detectable from a single pass.

**Detectable from Pass 1:**

| SR Code | Name | What Pass 1 Can See |
|---|---|---|
| SR-1 | Unhookable | Opening fails to establish tension, protagonist, or stakes within first pages |
| SR-2 | Synopsis Sag | Middle section reads as event-list without escalation (reader feels drift) |
| SR-3 | Climax Deflation | Ending doesn't land as structural resolution; feels like it runs out of steam |
| SR-4 | Voice Fracture | Prose register shifts without apparent purpose |
| SR-5 | Stakes Scatter | Multiple stakes compete without hierarchy; reader unsure what to worry about |
| SR-6 | Protagonist Vanishes | Protagonist drops out of driving role; story happens *to* them |
| SR-12 | Tonal Whiplash | Tone shifts that disorient rather than expand |

**Not detectable from Pass 1 (must appear in blind spots):**

| SR Code | Name | Why Pass 1 Can't See It |
|---|---|---|
| SR-7 | Category Blur | Requires Shelf Positioning analysis |
| SR-8 | Better Than It Sounds | Requires compression testing — manuscript may read well but resist pitching |
| SR-9 | Setup Dependency | Partially visible (slow opening), but full diagnosis requires query generation |
| SR-10 | Spine Amnesia | May surface as reader confusion, but structural spine diagnosis requires Pass 0/2 |
| SR-11 | Comp Orphan | Requires market analysis |
| SR-13 | Arc Substitution | Requires compression testing |
| SR-14 | Comp Fragility | Requires compression testing |
| SR-15 | Evidence Thinness | Requires compression testing |

**Partial detection note:** Some undetectable codes may leave reader-experience traces. SR-10 (Spine Amnesia) might surface as "I lost track of what this book was about in the middle." If Pass 1 detects the *symptom*, report the symptom. Do not assert the SR code. Note it as: "This may indicate [SR-10 Spine Amnesia], which requires structural analysis to confirm."

### Step 5: Render Verdict

**Go/no-go logic:**

| P1 Count | Verdict | Meaning |
|---|---|---|
| 0 | **GO** | No submission-blocking problems detected on single read. Blind spots still apply. |
| 1–3 | **GO — FIX THESE FIRST** | Submission-blocking problems detected, but the list is short enough to address before deadline. Prioritized action items follow. |
| 4+ | **NO GO** | Too many submission-blocking problems for a quick fix. Recommend full diagnostic when time allows. |

**Verdict confidence disclaimer (mandatory):** This verdict is based on a single read-through. It assesses reader experience only. Structural architecture, market positioning, and compression viability have not been tested. A GO verdict means "no obvious dealbreakers on first read" — not "the manuscript is ready."

### Step 6: Produce Triage Memo

Use the output template below.

---

## Output Template

```markdown
# Submission Triage Memo

**Project:** [TITLE]
**Date:** [YYYY-MM-DD]
**Genre:** [as stated by writer]
**Word Count:** [approximate]
**Assessment Type:** Single-pass reader experience (Pass 1 only)

---

## Verdict: [GO / GO — FIX THESE FIRST / NO GO]

[1-2 sentence plain-language summary of the verdict and why.]

---

## P1 Findings (Submission-Blocking)

[List each P1 finding. For each:]

### [Finding title]
- **What I noticed:** [reader-experience description — what the reading felt like]
- **Where:** [chapter/section reference]
- **SR code:** [if detectable] or "Reader-experience finding; structural diagnosis requires full edit"
- **Fix direction:** [1-2 sentences on what to address, not how to rewrite]

---

## P2 Findings (Weaknesses)

[Brief list. No action items — these are noted but not blocking.]

- [Finding]: [location] — [one line]
- [Finding]: [location] — [one line]

---

## What This Triage Cannot See

This assessment ran Pass 1 (Reader Experience) only. The following dimensions were **not tested** and may contain issues this triage could not detect:

- **Structural spine integrity** — whether the manuscript's causal architecture holds under analysis (requires Pass 0, 2)
- **Character arc completion** — whether arcs resolve structurally, not just emotionally (requires Pass 5)
- **Compression viability** — whether the manuscript's identity survives query/synopsis compression (requires Submission Readiness Workflow)
- **Market positioning** — whether the manuscript has a clear shelf and viable comps (requires Pass 11C, Shelf Positioning)
- **Subplot load-bearing** — whether subplots are structurally necessary or removable (requires Pass 2, 6)
- **Information flow** — whether reveals land in the right order and at the right pace (requires Pass 8)
- **Entity continuity** — whether names, places, and facts stay consistent (requires Pass 10)

A GO verdict with blind spots means: "Nothing stopped me on first read, but I couldn't check the foundation."

---

## Recommendation

[If GO:] Submit. Address P2 weaknesses if time permits.
[If GO — FIX THESE FIRST:] Fix the P1 items above, then submit. Estimated scope: [brief].
[If NO GO:] Do not submit yet. When your deadline passes, run the full diagnostic to understand the structural picture. The P1 findings above are symptoms; the causes may be deeper.

---

*Submission Triage — APODICTIC Development Editor v1.1*
*This is a single-pass read, not a full diagnostic.*
```

---

## Integration Notes

### Router wiring
- `constraint:time` + artifact `full_draft` + goal `submit` → Submission Triage
- `constraint:time` + artifact `full_draft` + goal `repair` → Submission Triage (same tool; if they're on a deadline and want a repair assessment, triage is what they get)
- `constraint:time` + artifact `partial` → Gap: triage requires complete manuscript. Acknowledge; offer targeted `/diagnose` as fallback.

### Command shortcut
No dedicated command. Triage is accessed via `constraint:time` in the router or by stating "I'm on a deadline" during intake. Power users who know the framework can say "run triage" or "just Pass 1."

### Relationship to Submission Readiness Workflow
The triage is the fast path; the full Submission Readiness Workflow is the thorough path. They share SR codes but differ in:

| | Triage | Full SR Workflow |
|---|---|---|
| Passes run | 1 | All + Pass 11 |
| SR codes available | 7 of 15 (reader-experience detectable) | All 15 |
| Generates query/synopsis | No | Yes (annotated reference materials) |
| Stress tests | None | 10 (5 query, 5 synopsis) |
| Distinguish framework | Not available | Full 6-test classification |
| Blind spots | Named explicitly | N/A (comprehensive) |
| Output | Triage memo (1-2 pages) | Full scorecard + reference materials |

### Re-entry path
If triage produces a NO GO verdict, the natural next step is the full diagnostic when the writer has time. Triage findings should be saved as `Triage_Memo_[date].md` in the active project output context beside the manuscript so they're available as context if the writer returns for a full edit. The full edit does not consume triage findings as formal input — it runs fresh — but the triage memo provides useful context for the writer's conversation with the editor about priorities.
