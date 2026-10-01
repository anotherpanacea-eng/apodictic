# Specialized Audit: Cross-Volume Series Continuity
## Version 0.1.0
*Last Updated: March 2026*

---

## Purpose

This audit diagnoses whether a multi-volume work propagates consequence, canon, and reader promise across books. It targets **serial state amnesia** — the failure mode where earlier volumes create durable change but later volumes treat that change as optional memory rather than binding history.

This audit is a **composer over existing machinery**, not a replacement:
- Pass 10 supplies character/entity state deltas and world rules (within one volume)
- Pass 8 supplies unresolved thread/reveal carry-forward (within one volume)
- Series & Composite Novel audit supplies standalone function, distance management, and hope calibration
- Plot Architecture series types calibrate continuity expectations by series form

This audit adds the **cross-volume persistence layer** — tracking whether those per-volume outputs propagate across the series.

**When to activate:**
- Multi-book series (any genre)
- Composite novels (linked novellas with unified arc)
- Linked story collections with recurring characters, settings, or world rules
- Any work where the router resolves `series | repair (continuity)`

**What this audit is NOT:**
- Not a within-volume consistency check (that's Pass 10)
- Not a within-volume thread tracker (that's Pass 8)
- Not a standalone-function or arc-shape assessment (that's Series & Composite Novel)
- Not a thematic coherence check (that's Pass 9)
- Not a substitute for the author's series bible — the audit diagnoses propagation failures, not missing documentation

---

## Prerequisites

Before running this audit, the following must exist:

1. **Pass 10 output for the current volume** (entity tracking, world rule ledger)
2. **Pass 8 output for the current volume** (reveal economy, thread inventory)
3. **Series_State.md** — the rolling series-level state artifact. If this is the first volume analyzed, initialize from `references/series-state-template.md`. If prior volumes have been analyzed, load the existing state file.

---

## Diagnostic Channels

Five channels, each tracking a distinct persistence layer:

### CS — Character State

Track per-character state across volumes: traits, capabilities, relationships, knowledge, emotional position, institutional standing.

**What to check:**
- Does each character's state at the start of this volume match their state at the end of the prior volume (or account for time-gap changes)?
- Are prior-volume injuries, traumas, relationship changes, and knowledge gains reflected in current behavior?
- When character state has changed between volumes, is the change causally traceable (growth) or unexplained (drift)?

**What to flag:**
- **CS-RESET**: Character behaves as if prior-volume changes didn't happen
- **CS-EVAP**: Prior consequence is acknowledged but carries no weight (decorative backstory)
- **CS-REBOOT**: Relationship replays the same dynamic without retaining prior progression
- **CS-KNOW**: Character doesn't know what prior volumes established they know (knowledge regression)
- **CS-DRIFT**: Character capabilities, personality, or competencies shift without causal architecture
- **CS-RULE**: Character state change is mediated by a world rule (drugs, magic, environmental effects) — flag requires consistency in both CS and WR channels

**Severity guide:**
- Gist-level violations (personality, relationship dynamics, emotional position) are higher severity than detail-level violations (physical descriptions, minor facts)
- Consequence-level violations (trauma vanishes, betrayal is forgotten) are higher severity than state-level violations (eye color changes)

### WR — World Rules

Track established rules, systems, constraints, costs, and scopes. Test whether later volumes preserve implications, not just wording.

**What to check:**
- Are rules established in prior volumes still in effect with the same costs, limits, and scope?
- Do later volumes honor the *implications* of prior rules, not just their verbal formulation?
- When a rule's scope or cost changes, is the change justified in-world?

**What to flag:**
- **WR-ELASTIC**: Rule costs, limits, or scope expand or contract without causal accounting
- **WR-BLIND**: Rule is verbally consistent but later volumes ignore what it should cause (implication blindness)
- **WR-BREAK**: Rule is explicitly violated without in-world justification
- **WR-VECTOR**: A high-implication rule (transmission vector, contagion, cascading institutional effect) is established but its downstream consequences are not tracked in subsequent volumes

**Severity guide:**
- Load-bearing rules (those that constrained prior-volume plot choices) are higher severity than decorative rules
- Rules that depart from genre defaults require more careful re-establishment in later volumes
- High-implication rules (transmission, contagion, cascading effects) require aggressive tracking

### UT — Unresolved Threads

Track thread inventory across volumes: introduced, advanced, dormant, transformed, denied, resolved, abandoned.

**What to check:**
- Is each high-signal thread from prior volumes either advanced, maintained in dormancy, transformed, explicitly denied, or resolved?
- Are dormant threads maintained with signal (referenced obliquely, implied by behavior, pressure-maintained)?
- Is the total thread inventory serviceable — or has promise debt exceeded the reader's tracking capacity?

**What to flag:**
- **UT-DROP**: High-signal thread vanishes without acknowledgment
- **UT-PREMATURE**: Thread resolved too quickly or easily relative to setup investment
- **UT-AMNESIA**: Thread disappears for one or more volumes, then resurfaces without sufficient re-activation
- **UT-SUBSTITUTE**: New thread takes over old thread's structural role without original promise being paid or displaced
- **UT-PILE**: Thread inventory exceeds serviceable capacity (8+ high-signal threads without resolution or maintenance)
- **UT-CONTRADICT**: Thread resolves in a way that contradicts its setup from earlier volumes

**Severity guide:**
- Signal strength determines severity of drops: high-signal drops are readiness-threatening; low-signal drops are local notes
- Thread proliferation without servicing is a systemic failure, higher severity than individual drops

### HC — Hope Calibration

Track per-volume ending hope level, return-to-series signal strength, and specific unanswered questions.

**What to check:**
- Does each volume ending leave at least one specific, emotionally charged, unanswered question?
- Is the hope/damage ratio calibrated to sustain return intention across the reading gap?
- Does the ending tell the truth about the kind of continuation being offered?

**What to flag:**
- **HC-DESPAIR**: Volume ending is so dark that return intention is structurally undermined (despair saturation)
- **HC-PREPAY**: Volume ending resolves so completely that return intention discharges (finale prepayment)
- **HC-DRIFT**: Volume ending leaves worry without a specific question (anxiety without direction)
- **HC-LIE**: Volume ending signals one kind of continuation but the next volume delivers something structurally different

**Severity guide:**
- Hope failures at series midpoints (where the reader must choose to continue) are higher severity than at the start
- The audit flags structural hope failures, not subjective darkness tolerance

### RL — Revision Ledger

Track intentional discontinuities, acknowledged revisions, and recontextualizations. Maintain the retcon credibility budget.

**What to check:**
- When prior-volume state has changed, is the change classifiable as additive (recontextualization), acknowledged (revision), or silent (retcon)?
- Is the cumulative retcon budget healthy — or has the series spent more trust than it has earned?
- Does the original text support the revised reading on reread?

**What to flag:**
- **RL-SILENT**: State change with no acknowledgment and no reread support (silent retcon)
- **RL-WEAK**: Intentional revision with insufficient reread support (undersupported retcon)
- **RL-PATTERN**: Multiple unrelated retcons suggesting systemic tracking failure rather than deliberate revision
- **RL-BUDGET**: Cumulative retcon spending exceeds earned trust

**Severity guide:**
- Silent retcons at the explicit-canon layer are highest severity
- Patterns of retcon across multiple state dimensions elevate to readiness-threatening
- Isolated additive retcons with reread support are local notes at most

### Hard Gates — Must-Fix Floor

The following four cross-volume failures are **audit-internal hard gates**. When any one fires, the finding carries an audit-internal **Must-Fix floor** that propagates to synthesis severity per the canonical Audit-Signal Propagation Rule in `core-editor/references/run-synthesis.md §Step 2`. Synthesis cannot downgrade a hard-gate flag below Must-Fix without an explicit override marker recording rationale. These gates are why Series Continuity is at Auto-run (`pass-dependencies.md §4a`) when series context is flagged: cross-volume canon breaks cannot be diagnosed by within-volume passes and disclosure is non-equivalent to running the audit.

- **SC-Gate-1 (Consequence-Erasure Floor):** Trauma vanishes, betrayal is forgotten, or earned change is reset between volumes without textual acknowledgment. Consequence-level state violations carrying durable plot weight in the prior volume.
- **SC-Gate-2 (Silent-Retcon Floor / RL-SILENT at explicit-canon layer):** Explicit prior-volume canon contradicted with no acknowledgment and no reread support — the highest-severity retcon class.
- **SC-Gate-3 (Reader-Promise Failure Floor):** Series ending breaks the kind-of-continuation promise made earlier; readiness-threatening hope-calibration failure at series midpoints or finales.
- **SC-Gate-4 (High-Signal Thread Drop Floor):** A thread the prior volume marked as load-bearing (explicit reader promise, named cliffhanger, explicit narrator commitment) is silently abandoned without dormancy signaling.

A hard-gate hit produces a Must-Fix floor on the named cross-volume transition regardless of mode (epic series, composite novel, linked collection); the per-channel Severity guides above remain authoritative for non-gate findings.

---

## Decision Tests

Apply these seven tests to each cross-volume transition:

1. **State propagation test:** Does a major prior change alter current behavior or stakes?
2. **Reversal accounting test:** If a prior state is reversed, does the text explain why, how, and at what cost?
3. **Dormancy signal test:** If a thread is inactive, is that inactivity marked or pressure-maintained?
4. **Implication test:** If a rule still holds, do later books acknowledge what it should cause?
5. **Re-entry economy test:** Does the volume orient through changed-state activation instead of recap?
6. **Hope truthfulness test:** Does the ending tell the truth about the kind of continuation being offered?
7. **Architecture-fit test:** Is the apparent irregularity actually licensed by the series form?

### Guardrails

Before flagging, verify:
- Recurrence is not automatically reset
- Absence is not automatically abandonment
- Bleakness is not automatically broken hope
- New protagonist is not automatically broken continuity
- Remembered trivia is not the same as preserved pressure

---

## Mode Calibration

Continuity burden varies by series architecture. Check the Plot Architecture skill's series-type identification and calibrate expectations:

| Series Type | CS Burden | WR Burden | UT Burden | HC Burden | Key Blind Spot |
|-------------|-----------|-----------|-----------|-----------|----------------|
| Sequential saga | Maximum | High | High | High | Accumulation trap (selective state forgetting) |
| Revolving protagonist | Medium | High | Selective | Medium | Handoff gap (prior protagonist freezes) |
| Character web | High | Medium | High | Medium | Parallelism without interdependence |
| Episodic / Seasonal | Medium | Low-Med | Low | Low | Frozen cast / soft reset |
| Mystery-box / Slow burn | High (info) | Medium | Extreme | Medium | Obligation pile-up without conversion |
| Generational / Empire | Variable | High | Medium | Variable | Abstract history without causal inheritance |
| Relationship / Healing arc | Maximum | Low | Medium | Maximum | Recurrence mistaken for depth |
| Expanding quest | High | High | High | Medium | Power creep and forgotten costs |

---

## Three-Way Classification

Classify each finding:

| Classification | Criteria | Editorial Action |
|----------------|----------|------------------|
| **Working Continuity** | Prior changes constrain current action; reversals accounted for; threads maintained | Log in Series_State.md; no revision needed |
| **Intentional but Undersupported** | Discontinuity serves narrative function; text signals awareness; reread partially supports | Targeted revision to strengthen reread support or make rupture more legible |
| **Serial State Amnesia** | Prior changes inert; reversals unaccounted; threads drifting; no narrative function | Revise for consequence propagation; update Series_State.md with required changes |

---

## Procedure

### First Volume Analyzed

1. Initialize `Series_State.md` from template
2. Run Pass 10 (entity tracking) and Pass 8 (reveal economy) on the volume
3. Populate Series_State.md:
   - Character State Ledger (end-of-volume states)
   - World Rule Ledger (rules established, costs defined)
   - Thread Inventory (threads introduced, their signal strength and current state)
   - Hope Ladder (ending assessment)
4. No continuity flags — first volume establishes baseline

### Subsequent Volumes

1. Load existing `Series_State.md`
2. Run Pass 10 and Pass 8 on the current volume
3. For each channel (CS, WR, UT, HC, RL):
   - Compare current volume's state against Series_State.md
   - Apply decision tests to each discrepancy
   - Classify as Working / Undersupported / Amnesia
   - Flag findings with specific evidence (2-4 scene/page references per flag)
4. Update Series_State.md with current volume's contributions
5. Produce audit output

---

## Output

`[Project]_Series_Continuity_Audit_[runlabel].md`

### Structure

1. **Series Profile** — volumes analyzed, series type, controlling idea, reading order
2. **Channel Summaries** — per-channel assessment with flags and evidence
3. **Cross-Volume Transition Analysis** — decision test results for each volume boundary
4. **Thread Inventory Status** — current state of all tracked threads
5. **Hope Ladder** — per-volume ending assessment with cumulative trajectory
6. **Revision Priorities** — flagged issues ranked by severity, with intervention class (not specific fixes)
7. **Series_State.md Updates** — changes made to the rolling state file during this analysis

### Evidence Requirements

- Every flag requires 2-4 specific scene/page references
- Consequence-level flags must cite both the establishing volume and the violating volume
- Thread flags must cite the introduction point, any maintenance signals, and the point of failure
- Hope calibration flags must cite the specific ending passage and the unresolved question (or absence thereof)

---

## Integration with Core Framework

### Activation

- **Router-triggered:** When intake resolves to `series | repair (continuity)`
- **Manual:** Via `/audit series-continuity`
- **Auto-recommend:** When Series & Composite Novel audit is active and cross-volume state discrepancies are detected

### Pass Dependencies

This audit requires Pass 10 (entity tracking) and Pass 8 (reveal economy) for each volume analyzed. These passes must be explicitly included in the run profile when series continuity is in scope — they are not guaranteed by baseline runs.

### Relationship to Adjacent Audits

- **Series & Composite Novel:** Structural/reader-experience audit. Runs alongside or before this audit. Provides standalone-function and hope-calibration data that this audit extends across volumes.
- **Pass 9 (Thematic Coherence):** Within-volume thematic audit. When both are active, Pass 9's cross-volume thematic extension (motif evolution, thematic continuity) feeds into this audit's thread and canon tracking.
- **Pass 10 (Entity Tracking):** Within-volume state audit. Provides the raw data this audit compares across volumes.

---

## Important Distinctions

### What This Audit Is Not

1. **Not a demand for perfect recall.** Series can be loose with details and tight with consequences. The audit prioritizes consequence propagation over fact checking.

2. **Not a prohibition on change.** Characters must change. World rules can evolve. The question is whether changes are accounted for, not whether they occur.

3. **Not a template for all series types.** Episodic series have different obligations than sequential sagas. The mode calibration table exists to prevent false positives from genre-inappropriate expectations.

4. **Not a substitute for the author's judgment.** The audit surfaces discrepancies and classifies them. The author decides whether a discrepancy is a problem, a feature, or irrelevant.

### The Fundamental Question

**Does this series behave as though it truly inherited the reality created by earlier volumes?**

If later books treat prior history as optional — if consequences evaporate, rules stretch, threads drift, and hope is miscalibrated — then the series has a consequence management problem. The audit's job is to find it, name it, and give the author enough evidence to decide what to do about it.

---

*This audit is designed to bolt onto the APODICTIC development editor core framework. Activate during intake when series continuity is the primary concern, or via `/audit series-continuity`.*
