# Pass 10: Entity Tracking + Timeline Architecture

*Reference file for the APODICTIC Development Editor. Loaded by Pass 10 (Entity Tracking) when the resolver activates it.*

**Last updated:** 2026-04-25 (Phase 6 Wave 1 — Timeline artifact added per `docs/review-log/2026-04-25_pass-10-timeline-enhancement-spec.md`).

---

## Purpose

Pass 10 builds the manuscript's entity-and-state model: characters, objects, motifs, locations, rule ledgers (in SFF), and **temporal architecture**. Pass 10 is a Tier 1 read pass — it depends only on the manuscript and runs in parallel with other Tier 1 reads.

Pass 10 is a data-building pass, not an evaluative one. It does not append to the Findings Ledger as a matter of course. It surfaces observations to the ledger only when something detected at this layer warrants flagging (e.g., a Rule Ledger inconsistency in an SFF run, a calendar paradox in any run, a load-bearing entity drift).

---

## Outputs

Pass 10 produces two artifact families:

1. **Run-folder artifact** (existing): `[Project]_Pass10_Entity_Tracking_[runlabel].md` containing the Rule Ledger, Entity Table, Motif Tracker, and the legacy chronology scan. This artifact is run-scoped; it is not designed for cross-run diff.
2. **Project-level rolling artifact** (added Phase 6 Wave 1): `Timeline.md` at the project root. This is a Pass-10-Class Rolling Structured Artifact per `core-editor/SKILL.md §Project Integration`. Eight required sections per the schema below.

The Timeline artifact is **additive**, not a replacement. Existing Pass 10 outputs remain valid. The Rule Ledger / Entity Table / Motif Tracker continue to live in the run-folder artifact; the new Timeline artifact lives at the project root and is diffable across runs.

---

## Timeline.md Schema (Required)

The Timeline artifact is a project-level rolling artifact with eight required sections. The artifact is a data structure, not an editorial finding — it carries no severity, no Must-Fix flags, no recommendation language. Severity emerges from Section 4 (Inconsistency Ledger) and propagates to synthesis via the Canonical Audit-Signal Propagation Rule (`run-synthesis.md §Step 2`).

**Naming convention.** Single rolling artifact: `Timeline.md` at the project root (alongside `Diagnostic_State.md`, `SYNTHESIS.md`, `README.md`). Each Pass 10 run reads the prior `Timeline.md` (if present), diffs against current manuscript-derived state, and writes the updated artifact. A historical preservation convention (`Timeline_YYYY-MM-DD.md`) is permitted but only one canonical filename pattern should be used per project; pick one and apply it uniformly.

**Schema fidelity.** The eight sections below are required. Empty sections must be present with a one-line "n/a — [brief reason]" placeholder rather than omitted. Some manuscripts (fragmentary works, experimental temporal structures) may legitimately leave Section 1 fields marked "n/a"; the schema accommodates this rather than forcing fit.

### Section 1: Event Ledger

Tabular. One row per scene (using the Pass 0 / Pass 6 scene definition: continuous unit of time/space with POV holder, local goal, detectable turn).

| Field | Required | Notes |
|---|---|---|
| Scene ID | Yes | E.g., "Ch N §M" or sequential number |
| Chapter / Section | Yes | Plain reference |
| Line range | Yes | First and last manuscript line |
| Word count | Yes | Measured (not estimated) |
| POV | Yes | Character name or "third-omniscient" etc. |
| Setting | Yes | Place |
| Anchor type | Yes | One of: `explicit-date` / `explicit-day` / `explicit-time` / `relative-to-previous` / `implicit` / `ambiguous` |
| Anchor text | Yes | The specific manuscript phrase establishing time. ≤25 words. Quote budget enforced. |
| Calculated date | Optional | Best-effort absolute date if anchorable; else marker like "Day N" or "Week M" |
| Calculated time-of-day | Optional | If determinable |
| Span | Yes | Implied elapsed time within this scene |
| Gap from previous scene | Yes | Implied elapsed time since previous scene ended |
| Confidence | Yes | `HIGH` / `MEDIUM` / `LOW` / `UNCERTAIN` |

### Section 2: Master Calendar

Day-by-day or week-by-week reconstruction synthesizing the Event Ledger. Each event placed; visible gaps marked; ambiguity zones marked. Format: bulleted day/week headings with scene IDs assigned. The Master Calendar is the human-readable view of the Event Ledger; the Event Ledger is the machine-readable view.

### Section 3: Temporal Marker Inventory

Catalog every explicit temporal marker in the manuscript. Specific dates, days of week, times, holiday/seasonal references, named events ("the half marathon" — use generic phrasing in the schema), duration claims, relative anchors.

For each marker:
- **Location** (chapter/scene/line)
- **Exact text** (≤25 words)
- **Implied temporal claim** (one sentence)

### Section 4: Inconsistency Ledger

Where temporal markers conflict with each other or with derived calculations. This section is the primary input to the synthesis-layer severity propagation (see §Synthesis integration below).

Per inconsistency:
- **Conflicting markers** (cite both by Section 3 location)
- **Implied conflict** (one sentence)
- **Severity classification:**
  - `paradox` — markers cannot both be true (HIGH severity input)
  - `drift` — markers loosely incompatible; contradiction is visible only when calculated (MEDIUM severity input)
  - `ambiguity` — markers under-determined; reader can complete consistently but the manuscript does not commit (LOW severity input, unless load-bearing)
- **Best-guess source:** `revision-induced` / `original-draft` / `ambiguous-by-design`

### Section 5: Ambiguity Ledger

Where the manuscript doesn't commit to a temporal anchor when one would be expected. Distinguished from Section 4's `ambiguity` rows by being **structural** (the manuscript chose not to anchor) vs. **accidental** (the manuscript should have anchored but didn't).

Format: per ambiguity, brief location + diagnostic + structural-vs-accidental classification.

### Section 6: Revision-Drift Hot Spots

Scenes/passages most likely to be revision-drift sites. Indicators:
- Concentration of relative-time markers (revisions tend to break absolutes and rebuild with relatives)
- Conflicting markers in proximity
- Anchors depending on chapter ordering that may have changed
- Markers contradicting adjacent scenes

Per hot spot: brief diagnostic + specific repair recommendation **class** (not specific repair content — firewall holds; the framework names the repair pattern, the author owns the prose).

### Section 7: Recommended Anchor Set

A short list (3-7 items) of anchor decisions the author should make to resolve inconsistencies. Each:
- **The decision needed** (abstract: "fix the trial start date")
- **Downstream scenes constrained** (cite by scene ID)
- **Recommended value** (if derivable from majority-evidence; otherwise note "author judgment required")

Once anchors are set, the rest of the calendar reconstructs deterministically.

### Section 8: Diff Notes

If a prior `Timeline.md` exists at the project root, this section records the diff:
- Events added (new rows in Section 1)
- Events removed (rows present in prior, absent in current)
- Events changed (row-level field changes — anchor type, anchor text, span, gap, confidence)
- Anchors changed (Section 3 markers added/removed/edited)
- Calculations changed (Section 2 day/week assignments shifted)
- Paradoxes resolved (rows that left Section 4 since prior run)
- Paradoxes introduced (new rows in Section 4)

This section is the primary input to `validate.sh timeline-diff`. If no prior Timeline exists, this section is empty (one-line placeholder: "n/a — first Timeline run for this project").

---

## Synthesis Integration

Per `run-synthesis.md §Step 2 — Canonical Audit-Signal Propagation Rule`, Pass 10 Inconsistency Ledger counts feed synthesis as numeric severity inputs:

| Section 4 Severity | Trigger Threshold | Synthesis-Layer Effect |
|---|---|---|
| `paradox` | ≥1 | Synthesis Must-Fix candidate (timeline coherence) |
| `drift` | ≥3 | Synthesis Should-Fix candidate (revision-drift hygiene) |
| `ambiguity` | Any tied to load-bearing structural element | Author Decision (climax positioning, intervention windows, character-development arc spans) |

The Pass-10-Class artifact integration is the same pattern used for `Argument_State.md` and `Series_State.md`: structured artifact at project level → mechanical validators surface signals → synthesis layer consumes counts as severity inputs per the canonical propagation rule.

---

## Validator Integration

Three mechanical validators pair with the Timeline artifact. Each has a real capability ceiling — bash cannot do structured Timeline parsing, so the validators are honest about what they actually verify. The Phase 7 Work Items section below documents what a Python helper would add.

1. `scripts/validate.sh timeline-diff <prior_timeline> <current_timeline>` — extracts Section 1 (Event Ledger) pipe-table rows AND Section 3 (Temporal Marker Inventory) bullet items, computes a structural diff across both, and verifies that Section 8 (Diff Notes) bullet-counts cover the structural totals (count-match, not just keyword-presence — v1.7.9 tightening). Sections 2 (Master Calendar) and 4 (Inconsistency Ledger) are largely freeform prose; the bash validator does not item-diff them. Exit 0 if no diff or diff documented in Section 8 with covering counts; exit 1 if undocumented or under-documented.

2. `scripts/validate.sh timeline-arithmetic <timeline_file>` — **marker-hygiene check only** (v1.7.9 honest reframing). Surfaces rows with a negative gap-from-previous numeric value or with a pre-labeled `(conflicts ...)` / `(contradicts ...)` parenthetical. Does NOT independently compute span arithmetic — true arithmetic verification (span sums, anchor-format normalization across heterogeneous markers) requires structured Timeline parsing and is deferred to a Phase 7 Python helper. A model that wrote consistent-looking pipe rows whose spans don't actually sum will pass this validator. Exit 0 if no marker-hygiene candidates; exit 1 if surfaced.

3. `scripts/validate.sh timeline-anchor-conflict <timeline_file>` — **pre-labeled-conflict surfacing only** (v1.7.9 honest reframing). Counts parenthetical `(contradicts ...)`, `(paradox with ...)`, and `(conflicts with ...)` annotations in the Timeline body — i.e., Pass 10 model judgment has already pre-labeled the conflict. Does NOT independently parse temporal anchors per scene/chapter and reason about same-anchor-different-time conflicts; true anchor-format parsing is deferred to a Phase 7 Python helper. A model that wrote inconsistent anchors but didn't notice the conflict will pass this validator. Exit 0 if no candidates; exit 1 if candidates surfaced.

All three validators surface **candidates**, not conclusions. Pass 10 model judgment classifies each candidate (paradox vs. drift vs. ambiguity vs. intentional-feature). Mechanical detection reduces the inference load Pass 10 must carry for the cases the model already noticed; it does not replace Pass 10's classification work, and (per the v1.7.9 honest reframing) it does not catch the cases the model failed to notice.

**Override-marker support.** Each validator honors structured override markers in the Timeline body (not appendix), parallel to the Phase 4 pattern in other validators:

```
<!-- override: timeline-diff-undocumented — <one-sentence rationale> -->
<!-- override: timeline-arithmetic-conflict — <one-sentence rationale> -->
<!-- override: timeline-anchor-conflict — <one-sentence rationale> -->
```

Markers placed inside Section 8 (Diff Notes appendix-equivalent) or anywhere outside the artifact body do not satisfy the override path. **Absence of marker and rationale = validator failure** — the Pass 10 model must either annotate the diff/arithmetic/anchor candidate as legitimate via marker or surface it as an Inconsistency Ledger row.

---

## Phase 7 Work Items

The bash Timeline validators have a documented capability ceiling. The following work items would lift that ceiling; each is deferred to Phase 7 (Python tooling phase) because bash cannot do the work feasibly:

1. **Python-based Timeline parser** — structured parser for Section 1 (Event Ledger) pipe-tables and Section 3 (Temporal Marker Inventory) bullets that produces a normalized scene-by-scene anchor record, including:
   - Anchor-format normalization across heterogeneous markers (`Day N`, `Monday morning`, `March 14`, `the day after the half marathon`, `the following Friday`)
   - Span normalization to a common time unit (minutes / hours / days)
   - Per-scene calculated start-time and end-time derived from span + gap-from-previous

2. **True arithmetic verification** (replaces `timeline-arithmetic` marker-hygiene check) — given the parsed scene records, verify that:
   - Each scene's calculated end-time precedes the next scene's calculated start-time (or that the gap is consistent with the gap-from-previous claim)
   - No pair of scenes occupies overlapping time without explicit POV-split or flashback marker
   - Cumulative span totals match calendar-section claims

3. **True anchor conflict detection** (replaces `timeline-anchor-conflict` pre-labeled surfacing) — given the parsed scene records, detect:
   - Same Scene ID with two different absolute anchors (drift the model failed to pre-label)
   - Anchor-format incompatibilities (e.g., scene anchored "Monday" appears between scenes anchored to specific Tuesday-and-later dates)
   - Calendar-section / Event-Ledger inconsistencies (Section 2 and Section 1 disagreeing on which day a scene falls)

4. **Item-level diff for Sections 2 and 4** (extends `timeline-diff`) — Master Calendar day/week shifts and Inconsistency Ledger row changes parsed and diffed at item level rather than the current section-presence level.

**Migration path.** When the Phase 7 Python helpers exist, the bash validators can call them as shell-out helpers (preserving the existing CLI contract) and the framework prose (this section + the §Validator Integration descriptions above) updates to reflect the now-true mechanical verification. The bash validators remain available as a marker-hygiene fallback for hosts that cannot execute Python. The Phase 7 work also enables a Pass 10 self-verification step: the model can re-read its own Timeline artifact through the parser and surface drift it didn't notice during initial construction.

**Framework-design lesson.** Bash validators have a real ceiling. Future validator work should choose the implementation tool to match the verification kind needed: bash for structural and pattern-presence checks (heading inventory, table-row diff, marker keyword surfacing, count matching); Python (or another structured language) for parsing, normalization, and reasoning over heterogeneous formats. Mixing the two by *claiming* parsing capability in a bash validator produces validators that overclaim and false-pass on the cases that most matter.

---

## Migration / Backward Compatibility

**Existing projects with Pass 10 outputs but no `Timeline.md`:** The next Pass 10 run produces the first `Timeline.md` with Section 8 (Diff Notes) empty. Subsequent runs populate the diff section against the now-existing prior artifact.

**Existing run-folder-scoped Pass 10 outputs:** Remain valid. They were produced under the prior spec. New runs under the enhanced spec produce both the legacy run-folder artifact (Rule Ledger + Entity Table + chronology text) and the new structured `Timeline.md` at project root. The legacy chronology text continues to live in the run-folder artifact for human reference; the structured Timeline supersedes it as the canonical temporal record.

**Cross-volume series continuity:** The Timeline artifact does not subsume `Series_State.md`. Cross-volume continuity remains the Series Continuity audit's territory. Per-volume Timeline artifacts integrate with — but do not subsume — series-level continuity tracking.

---

## Pre-pass Intake Note

A pre-pass intake timeline scaffold is **out of scope** for this reference. Pass 10 happens after intake; the Timeline artifact is built from manuscript-derived state at Pass 10 execution time. Pre-pass intake timeline scaffolding is a separate proposal.

---

*Schema source of truth: `docs/review-log/2026-04-25_pass-10-timeline-enhancement-spec.md`. This reference file lifts that spec into runtime-loadable form.*
