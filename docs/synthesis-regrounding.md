# Spec 05 — Synthesis coverage disclosure (M1) + pre-letter re-grounding (M2) (apodictic)

**Status:** **Built** — **M1 Built** (#160 — `synthesis_coverage.py` V1–V5 + step 9b + Appendix C
note + marker + sidecar; Opus build-review READY-WITH-FIXES → V5 letter-family P2 folded; as-built
corrections in §M1.8); **M2 Built** (this PR — `specificity_floor.py` + step 9c;
Opus-build/Fable-review tier-inversion; 3 matcher P2s folded pre-Codex; as-built corrections in
§M2.5). Spec-review pass 1 folded 2026-07-01 (verdict: BUILD-READY-WITH-FIXES, 1 P1 — resolved by
fix 1); expanded from stub 2026-07-01; all anchors grep/read-verified.
**Estimate:** M1 ~2 sessions, M2 ~2–3 sessions. **Owner of the decision:** craft/editorial trust in
the whole-novel deliverable.
**Provenance:** Opus 4.8 pick #3, **trimmed after inventory verification** — the "auto-mode
selection" third of the original pitch already shipped as adaptive mode escalation
(`docs/adaptive-mode-escalation.md`, Increments 1–3 & 5, v2.1.0). What remains unbuilt is
re-grounding and honest degrade disclosure.
**Sequencing:** M1 builds after spec 03 (declined-finding state) lands; M2 builds after spec 04
(finding disconfirmation) lands — both siblings touch the same `run-synthesis.md` Processing
Protocol seam and the same `letter_checks.py`-family validator surface, and stacking in-flight
edits there is how merge trains die. M1 is a **hard dependency of M2 and stays mandatory after
M2 lands** (disclosure is never replaced by remediation).
<!-- built-when: scripts/synthesis_coverage.py -->

---

## Problem & verified evidence

- `docs/subagent-architecture-design.md:15`: "*Context salience decay. Earlier pass findings lose
  specificity by synthesis time. Pass 1's nine belief failures become 'several belief failures' in
  the editorial letter.*" Root-caused from a real A/B on a ~118k-word novel (line 5, *A Game of
  Universe*, Nylund). Line 231 adds that platform-level context compaction is **unobservable from
  within the model** — some decay may be invisible handoffs, not token pressure.
- `ROADMAP.md:319` (§Model-Capacity Exploitation): "long-context re-grounding before synthesis" is
  listed as planned, unbuilt. The section's model-allocation direction (plan compute up front;
  tiered model assignment per `docs/subagent-architecture-design.md` §Tiered Model Assignment,
  design-concept status) is the frame M2's bounded manuscript re-reads lean on.
- `docs/subagent-architecture-design.md:62–66` + `run-core.md:255` + `hybrid-mode.md:130–136,297`:
  in every multi-agent mode the synthesis subagent is dispatched with the **consolidated ledger +
  reverse outline + selected verification excerpts** — *not* the manuscript. Chapters outside
  active context at letter time are the **norm**, not an anomaly, and today nothing tells the
  author which chapters those were or which pass artifacts synthesis actually re-read.
- `docs/subagent-architecture-design.md:407` (§Pass-Driven Re-Targeting, Open Question 1):
  synthesis-initiated retrieval is an acknowledged open design point — synthesis's verification
  excerpts are "selected by the parent orchestrator heuristically."
- The degrade is **silent**: the letter looks complete whether or not Act 1 survived to synthesis.
  `run-synthesis.md:394–439` (Evidence Spot-Check) samples 5 claims for *accuracy*, but no surface
  discloses *coverage* — what synthesis could and couldn't see when it wrote the letter.

### Anchor corrections vs the stub

Verified 2026-07-01; the stub was directionally right with three sharpenings:

1. **Mode escalation is fully built, including de-escalation** (`docs/adaptive-mode-escalation.md`
   line 3; `run-core.md:297–309` §Mid-Run Escalation Check; `scripts/escalation_check.py`). This
   spec proposes **zero** mode-selection work. Escalation also gives the pattern to copy: an
   additive sidecar object (`complexity_signals`, `apodictic.diagnostic-state.v1.schema.json:19–28`,
   `additionalProperties: true`, no version bump, no new schema file — so no `_coverage.json`
   binding row and no meta-lint M4 exposure).
2. **`run-core.md:321–372` already has a built "§Pre-Pass Re-Grounding"** (Blocks A/B/C,
   mode-conditional). M2's step must be named **Pre-Letter Re-Grounding** and must not touch that
   section — different seam (pre-pass vs pre-letter), and a name collision would wreck both.
3. **"Chapters outside active context" needs mode-relative semantics.** In single-agent mode the
   manuscript is nominally fully in context (`run-core.md:175–189`) but attention/compaction is
   unverifiable; in sequential/hybrid/swarm the synthesis context is exactly its dispatch inputs.
   A single absolute "coverage %" would mislead in both directions. The note below is therefore
   defined per mode, with an honest provenance label.

---

## Decision it changes

Whether to trust a whole-novel diagnosis — or hand-chunk the book and stitch letters. Full
manuscripts are the tool's core use case; today their synthesis-time reliability is invisible.
After M1, the author (and any downstream consumer) can see exactly what the letter was written
*from*. After M2, the letter's specificity is restored from disk instead of from decayed context —
and the disclosure proves it rather than asserting it.

---

## Design overview

Two independent milestones, two PRs:

- **M1 — mandatory synthesis coverage disclosure.** At synthesis time, produce a mechanical
  **artifact-read manifest**, render a **coverage note** in the letter (Appendix C) + a
  **`synthesis_coverage`** sidecar object, and gate them with a new `synthesis-coverage`
  validator that reconciles the note against the manifest and the manifest against the
  **filesystem** (the denominator the model cannot invent). Ships alone; changes the trust
  decision even if M2 never builds.
- **M2 — pre-letter re-grounding.** A required step immediately before letter-writing that
  re-reads the consolidated ledger verbatim from disk and re-reads bounded manuscript spans for
  synthesis-bound findings, restoring counts/names/quote anchors. Gated by a **specificity-floor**
  validator (letter vs ledger, per finding ID) and a Firewall-adjacent no-new-findings guard.
  M2 *updates* the M1 manifest (re-read artifacts flip to `verbatim`); it never suppresses the
  note.

The design rule that keeps this honest, everywhere: **the disclosure is computed from the
manifest, and the manifest's denominator is enumerated from disk** (run-folder globs + preflight
section boundaries) — never from the letter's own prose, never from a model's memory of what it
read.

---

## M1 scope — synthesis coverage disclosure (ship first, alone)

### 1. What "active context at synthesis" means, per execution mode

(Modes per `run-core.md:143–293`; synthesis dispatch inputs per `run-core.md:255`,
`docs/subagent-architecture-design.md:62–66`, `hybrid-mode.md §Synthesis: Verification Excerpts`.)

| Mode | Synthesis context actually holds | Manifest provenance | What the validator can really check |
|---|---|---|---|
| **single-agent** | Manuscript + all pass artifacts + ledger, loaded across one long context; active attention/compaction **unobservable** (`subagent-architecture-design.md:231`) | **`declared`** | Completeness vs disk (every artifact/span has a declared status), internal consistency, preflight context-utilization number. **Not** the truth of "verbatim" claims — the spec says so out loud. |
| **sequential** | Dispatch inputs only: consolidated ledger + reverse outline + verification excerpts + prerequisite outputs | **`dispatch-derived`** | Manifest written by the orchestrator **before** dispatch = the strongest evidence available without platform introspection; validator checks it covers the disk enumeration and that the note is its exact projection. |
| **hybrid** | Same as sequential; the focus map already reports coverage statistics (`hybrid-mode.md:162,237,307` — the in-repo precedent for coverage language) | **`dispatch-derived`** | Same as sequential, plus excerpt spans cross-checked against the focus map's Synthesis Verification Excerpts table. |
| **swarm** | Same dispatch shape as sequential (synthesis gets ledger + outline + excerpts, not the full text) | **`dispatch-derived`** | Same as sequential. |

Honesty ladder, stated plainly in the spec and in the note itself: **multi-agent manifests are
real** (dispatch-derived — the orchestrator lists exactly the files it handed the synthesis
subagent, and those are checkable paths); **single-agent manifests are declared** (there is no
read-event log; nothing platform-side records what stayed salient). The validator therefore gates
*hard* on reconciliation + provenance-mode agreement in multi-agent runs, and gates on
completeness + pinned-disclosure-language in single-agent runs. A `declared` manifest in a
multi-agent run **fails** (V4 below) — the cheap lie is blocked; the unavoidable epistemic gap is
labeled instead of laundered.

### 2. The artifact-read manifest (mechanical substrate)

New run-folder artifact: `[Project]_Synthesis_Read_Manifest_[runlabel].md` (naming per
`output-structure.md §Output Naming Convention`), written **before the letter exists**:

- **Multi-agent modes:** written by the parent orchestrator at Execution Protocol step 10
  (`run-core.md:255`) as part of dispatching the synthesis subagent — one row per dispatch input.
- **Single-agent mode:** written by the agent immediately before letter-writing (new Processing
  Protocol step, below) — one row per artifact with the status it declares.

Row vocabulary (closed enum): `verbatim` (full file provided/re-read at synthesis time),
`summary` (represented only via its ledger entry / the reverse outline), `absent` (on disk but
not represented in any synthesis input). Manuscript coverage rows use the **preflight section
boundaries + reverse-outline scene list** as the span denominator: each chapter/scene span is
`in-context` (single-agent nominal / a verification excerpt in multi-agent) or
`outside-active-context`.

The denominator is never model-supplied: pass artifacts are enumerated by the same globs
`artifact-names` already uses (`[Project]_Pass[N]_[Name]_[runlabel].md`, plus the Findings
Ledger, consolidated ledger, contract, audit findings files); manuscript spans come from
`preflight.sh` output (already mechanical, `execution-modes-reference.md:9–25`).

#### Manifest structure (worked example)

The manifest body is a single pipe table; `synthesis_coverage.py` is its **only** parser, and
this is the exact row grammar it parses — four pipe-delimited cells per row, one row per
enumerated item:

```
| kind     | id                           | status                 | annotations      |
|----------|------------------------------|------------------------|------------------|
| artifact | MyBook_Pass1_Triage_r3.md    | verbatim               |                  |
| artifact | MyBook_Pass5_Beliefs_r3.md   | summary                |                  |
| artifact | MyBook_Pass8_Reveals_r3.md   | absent                 |                  |
| span     | Ch 12 (sc. 30–31)            | in-context             |                  |
| span     | Ch 1–2                       | outside-active-context |                  |
```

- `kind ∈ {artifact, span}` (closed). `id` = the artifact file's basename (artifact rows) or a
  preflight/reverse-outline span label (span rows). `status` — artifact rows: `verbatim |
  summary | absent`; span rows: `in-context | outside-active-context`. `annotations` — empty or
  `regrounded: true` (the only annotation M1/M2 define; any other content in the cell ⇒ V3
  parse FAIL, never silently ignored).
- **Disk-enumeration algorithm (the denominator):** glob the run folder with the
  `artifact-names` family (`[Project]_Pass[N]_[Name]_[runlabel].md` + Findings Ledger +
  consolidated ledger + contract + audit findings files); take the chapter/scene span list from
  `preflight.sh` output + the reverse-outline scene list. The union is the **required row set**:
  every enumerated item must have exactly one row (missing ⇒ V2 FAIL), and every row's `id`
  must resolve to an enumerated item (an invented artifact/span row ⇒ V2 FAIL in the other
  direction — the manifest can neither shrink nor pad the denominator).
- **The `regrounded: true` encoding (what M2 flips):** M2 step 4 rewrites a re-read row's
  `status` to `verbatim` / `in-context` **and** appends `regrounded: true` in the annotations
  cell — e.g. the Pass 5 row above becomes
  `| artifact | MyBook_Pass5_Beliefs_r3.md | verbatim | regrounded: true |`. The annotation
  lets the note (and V3's projection diff) distinguish original synthesis contact from
  restored contact; M1's validator requires only that the annotation be well-formed.

### 3. The coverage note (letter rendering — exact content)

Rendered as a **mandatory subsection of Appendix C (Framework Notes)**: `### Synthesis Coverage`.
Appendix C is already one of the 14 required headings (`run-synthesis.md:262–279`), so the
14-section `synthesis-sections` contract is untouched — no 15th top-level section, no change to
that validator's loose substring matching (the subsection check lives in the new validator
instead). Content, in order:

1. **Mode + provenance sentence** (pinned language): either
   *"This letter was synthesized in `<mode>` mode. The coverage below is dispatch-derived: it
   lists exactly the artifacts and excerpts the synthesis step received."* or (single-agent)
   *"This letter was synthesized in single-agent mode. The coverage below is declared by the
   model, not platform-verified: with a single long context, what remained in active attention
   at letter time cannot be mechanically observed."*
2. **Artifact table** — each pass artifact / ledger / contract with `verbatim | summary | absent`.
3. **Manuscript span coverage** — either *"full manuscript nominally in context (estimated
   context utilization NN% per preflight)"* (single-agent; NN = preflight's estimated token load
   ÷ detected window, both already computed) or the explicit list: *"In active context at letter
   time: Ch 3 (sc. 7–8), Ch 12 (sc. 30–31), Ch 22 (sc. 55) — the verification excerpts. Outside
   active context: Ch 1–2, 4–11, 13–21, 23–24 (represented via the reverse outline and Findings
   Ledger only)."*
4. **Interpretation line** (pinned per mode, in the spirit of `hybrid-mode.md:162`'s coverage
   interpretation note): what this means for trust, ending with the remedy — *"If you want
   broader synthesis-time contact with the text, request more verification excerpts or swarm
   mode"* (post-M2: *"…or note that a pre-letter re-grounding pass ran; see the `regrounded`
   rows above"*).

**Author-visible degrade surfacing:** a machine marker `<!-- coverage: ok -->` or
`<!-- coverage: degraded -->` **immediately after the title block, on its own line** (exact
placement + parse regex pinned in §5's V5 truth table), plus — when degraded — one plain sentence at
the end of "The Short Version" (body is canonical; appendices hold evidence, per the repo's
standing marker doctrine). "Degraded" is defined mechanically, **relative to the mode's own
baseline**, as any of: an `absent` artifact row; a synthesis-bound (Must-Fix/Should-Fix) finding
whose `evidence_refs` span is covered by no `verbatim` row and no excerpt; (single-agent)
estimated context utilization > 60% of the detected window (the same viability threshold family
preflight already uses, `execution-modes-reference.md:15`); zero verification excerpts in a
multi-agent run whose letter carries ≥1 Must-Fix. Normal multi-agent outline-mediated coverage is
**not** degraded — that is the architecture working as designed, and the note says so rather than
crying wolf.

### 4. Sidecar field schema

Additive object in `Diagnostic_State.meta.json`, following the `complexity_signals` precedent
exactly (property + `$comment` in `apodictic.diagnostic-state.v1.schema.json`, field in
`diagnostic-state-meta-template.json`, documented in `output-structure.md §Machine-Readable
Sidecar`; no version bump, **no new schema file** — so no `_coverage.json` binding row and no
meta-lint M4 exposure):

```jsonc
"synthesis_coverage": {
  "provenance": "dispatch-derived",        // or "declared" (single-agent only)
  "execution_mode": "hybrid",
  "coverage": "degraded",                  // "ok" | "degraded" — must equal the letter marker
  "manifest": "runs/.../MyBook_Synthesis_Read_Manifest_r3.md",
  "artifacts_verbatim": 4, "artifacts_summary": 2, "artifacts_absent": 0,
  "spans_outside_active_context": ["Ch 1-2", "Ch 4-11", "Ch 13-21", "Ch 23-24"],
  "verification_excerpt_count": 3,
  "estimated_context_utilization": null    // number, single-agent only
}
```

### 5. Validator — `validate.sh synthesis-coverage <run_folder>`

New Python helper `scripts/synthesis_coverage.py` behind a thin dispatcher arm (the
validator-hardening posture, `ROADMAP.md:311`: **no new bash-regex validators** — bash is the
degrade path only). Checks:

- **V1 (presence):** a run that wrote a full letter (`*_Core_DE_Synthesis_*` /
  `*_Full_DE_Synthesis_*` exists — the same detection the annotated-manuscript offer uses,
  `run-synthesis.md:445`) must have the manifest file, the Appendix C subsection, the title-block
  marker, and the sidecar object. Missing any ⇒ FAIL. (Partial/fragment/triage runs are out of
  scope — no full letter, no coverage obligation.)
- **V2 (completeness — the can't-be-fiction floor):** every pass artifact / ledger file the
  run-folder glob enumerates appears in the manifest with an enum status; every preflight
  chapter/scene span is assigned. An on-disk artifact missing from the manifest ⇒ FAIL. The
  model cannot shrink the denominator.
- **V3 (reconciliation):** the Appendix C note is parsed and diffed against the manifest — the
  note is a **projection** of the manifest (statuses, span lists, counts), and the letter may
  never claim broader coverage than the manifest records. The sidecar counts must tally with
  the manifest rows, and `coverage` must equal the letter marker. Any divergence ⇒ FAIL (the
  anti-self-report tooth: prose can only restate the mechanical record).
- **V4 (provenance/mode agreement):** sidecar `execution_mode` ∈ {sequential, hybrid, swarm} ⇒
  `provenance` must be `dispatch-derived`; `declared` ⇒ FAIL. Single-agent ⇒ `declared` allowed,
  and the pinned declared-not-verified sentence must appear verbatim in the note.
- **V5 (degrade disclosure):** the validator recomputes ok/degraded from the manifest per §3;
  if degraded, the `<!-- coverage: degraded -->` marker and the Short Version sentence must be
  present. A run that computes degraded but declares `ok` ⇒ FAIL — **masking fails louder than
  degrading.** V2/V3/V5 have **no override markers** (disclosure is not overridable); the only
  legitimate escape is fixing the manifest.

#### V5 degrade truth table (the complete condition set)

`coverage = degraded` iff **any applicable row fires**; otherwise `ok`. There are no other
degraded conditions — this table is exhaustive, and the validator recomputes it from the
manifest + sidecar only (never from letter prose):

| # | Condition (recomputed mechanically) | single-agent | multi-agent (seq/hybrid/swarm) |
|---|---|---|---|
| D1 | any artifact row `status: absent` | degraded | degraded |
| D2 | a synthesis-bound (Must-Fix/Should-Fix) ledger finding whose `evidence_refs` span is covered by no `verbatim` artifact row and no `in-context` span row | degraded | degraded |
| D3 | `estimated_context_utilization` > 60% of the detected window (preflight's viability threshold family, `execution-modes-reference.md:15`) | degraded | n/a (field is `null`) |
| D4 | `verification_excerpt_count: 0` while the letter carries ≥ 1 Must-Fix | n/a (no excerpt machinery) | degraded |
| — | all manuscript spans `outside-active-context` with ledger/outline at `summary` + excerpts present | — | **ok** — outline-mediated coverage is the architecture working as designed, not a degrade |

**Marker placement (exact):** the first non-blank line **immediately after the title block**, on
its own line — nothing else on the line. **Parse regex** (applied to raw lines, not inside a
code fence; marker matching follows the repo's `override_marker` discipline — no local
code-span stripper, meta-lint M6): `^<!-- coverage: (ok|degraded) -->$`. First match wins;
a second coverage marker anywhere in the letter ⇒ V3 FAIL (one declaration, one place).

**Minimal degraded pair (fixture-sized):** manifest = the §M1.2 worked-example table with the
single row `| artifact | MyBook_Pass8_Reveals_r3.md | absent | |` among otherwise-`verbatim`
rows ⇒ D1 fires ⇒ computed `degraded`. Letter A: title block, then
`<!-- coverage: degraded -->`, plus the Short Version sentence ⇒ V5 pass. Letter B: identical
but `<!-- coverage: ok -->` ⇒ V5 FAIL (this is fixture M1-2).

Conventions honored (all verified in-repo): dispatcher case + `--self-test` with synthetic
fixtures (meta-lint **M1**); input classification via parsed blocks / globs, never marker
substrings (**M2**); count derived from `AGG_VALIDATORS`, never a hand-typed integer (**M3** —
no "N→N+1 bump" instruction anywhere in this spec); no bare override-substring scans (**M5**,
moot — no overrides); **dual script mirror** — `synthesis_coverage.py` + the `validate.sh` edit
land byte-identical in `plugins/apodictic/scripts/` and root `scripts/`, verified by
`validate.sh check-mirror` as the last pre-`--check-all` step (`AGENTS.md:106–117`); degrade to
advisory WARN without `python3` (the model performs the checks inline per `run-core.md`
§Mechanical Validation Protocol).

### 6. Integration points (M1 files touched)

- `run-synthesis.md`: new Processing Protocol step between Step 9 and Step 10 — **"Synthesis
  Coverage Manifest (required)"** (write/receive the manifest before any letter prose); the
  Presentation Format's Appendix C spec gains the `### Synthesis Coverage` subsection; Step 12's
  checklist points at the new validator. Builder note (anchor-verify rule): re-read the live
  step numbering before editing — spec 03/04 builds may have shifted it.
- `run-core.md` §Execution Protocol step 10: the orchestrator writes the manifest at synthesis
  dispatch (multi-agent modes).
- `schemas/execution-gates.v1.json`: add `synthesis-coverage` to the `run_spot_check` gate's
  mechanical check set (builder: read that manifest's format first — anchor-verify; launch
  posture per the defaulted operator call in §Open questions — V2/V3/V4 blocking day one,
  overall gate advisory-first for one release).
- `apodictic.diagnostic-state.v1.schema.json` + `diagnostic-state-meta-template.json` +
  `output-structure.md`: the `synthesis_coverage` object.
- `scripts/synthesis_coverage.py` + `validate.sh` arm (×2, mirrored); `changelog.d/<slug>.md`
  fragment; this spec's `**Status:**` line flips in the build PR (status-drift rule).

### 7. Fixture / self-test plan (M1)

`--self-test` synthetic fixtures (the repo's validator pattern), at minimum:

1. **Green dispatch-derived run** — hybrid-shaped fixture folder; manifest, note, sidecar all
   consistent ⇒ exit 0.
2. **Degraded-synthesis fixture (the note must fire):** a Pass 5 artifact exists on disk with an
   `absent` manifest row while the letter marker says `ok` ⇒ V5 FAIL; same fixture with the
   `degraded` marker + Short Version sentence ⇒ pass. This fixture is reused by M2.
3. **Self-reported-fiction fixture:** note claims "all artifacts re-read verbatim," manifest rows
   say `summary` ⇒ V3 FAIL.
4. **Shrunk-denominator fixture:** artifact on disk, no manifest row ⇒ V2 FAIL.
5. **Provenance-laundering fixture:** `execution_mode: swarm` + `provenance: declared` ⇒ V4 FAIL.
6. Hostile shapes per AGENTS.md review practice: a lookalike filename satisfying the manifest
   glob (`*_Synthesis_Read_Manifest_Draft_*`), malformed-but-valid JSON sidecar (bare-string
   `synthesis_coverage`), empty manifest, manifest naming a nonexistent path.

### 8. As-built corrections (M1 build PR)

Where shipped M1 deviates from the letter of this spec — recorded so nobody "fixes" the build
back toward stale spec text:

- **(a) Step number: 9b, not a renumber.** §M1.6 said "new Processing Protocol step between
  Step 9 and Step 10"; the build inserts it as **step 9b** and leaves Steps 10–13 unrenumbered,
  so every existing cross-reference to the Step 10 pre-output gate and the Step 12 checklist
  (here, in `run-synthesis.md`, and in the sibling specs) stays valid.
- **(b) Span-dimension honesty: spans have no disk denominator — by design.** §M1.2's
  "manuscript spans come from `preflight.sh` output" over-promised: preflight persists no span
  artifact, so there is nothing on disk to enumerate a span denominator from, and the span half
  of V2 is **not** a bijection. The teeth that remain are mechanical: V2 requires ≥ 1 span row
  (the manuscript dimension cannot be omitted), V3 forces three-way agreement (manifest = note
  table = sidecar span lists/counts), and D2 anchors coverage on the **ledger's `evidence_refs`
  chapters**, which the manifest cannot edit. Build-review attack trace: a consistently-shrunk
  span set cannot hide an uncovered Must-Fix, because shrinking the in-context set makes D2 fire
  *more*, not less. The surviving hole is a false `in-context` **padding** claim in a `declared`
  single-agent manifest — exactly the §M1.1 honesty ladder's acknowledged
  labeled-not-laundered gap, not a new one.
- **(c) The pinned degrade sentence is backtick-free.** Marker/sentence scanning runs on
  code-span-stripped text (shared `override_marker.strip_code_spans`); a pinned sentence
  containing backticks could never match post-strip. The shipped `SENT_DEGRADED` carries none —
  keep it that way if the wording is ever revised.
- **(d) Manifest resolved by exact derived name (lookalike-proof).** V1 does not glob for
  manifest-shaped filenames; it constructs the one legal
  `[Project]_Synthesis_Read_Manifest_[runlabel].md` name from the letter's own project/runlabel
  and checks that exact file — a `*_Synthesis_Read_Manifest_Draft_*` lookalike (hostile fixture,
  §M1.7 item 6) cannot satisfy presence.
- **(e) V5 letter-family branch (build-review P2, folded).** Editor-scaffolding letters
  (`run-synthesis.md` §Operator mode) replace "The Short Version" with an **Editor Brief**, so
  V5's degrade-sentence anchor branches on the letter's `<!-- mode: editor-scaffolding -->`
  marker (the same marker `editor_scaffolding.py` keys on) and scopes to the Editor Brief in
  that family. The check stays **section-scoped** rather than searching the whole body: the
  sentence's job is to surface the degrade in the reader-facing summary paragraph, and a
  body-wide match would let it hide in Appendix C — where coverage prose already lives —
  defeating "body is canonical; appendices hold evidence" (§M1.3).

---

## M2 scope — pre-letter re-grounding (builds on M1; M1 stays mandatory)

### 1. The step — "Pre-Letter Re-Grounding (Required)"

New Processing Protocol step in `run-synthesis.md`, immediately **after** the M1 manifest step
and **before** the Step 10 pre-output gate and Step 11 letter-writing (the drafted root causes,
triage, and stress test exist; the prose does not). Named to avoid collision with the built
`run-core.md §Pre-Pass Re-Grounding` — this spec does not touch that section.

1. **Re-read the consolidated Findings Ledger verbatim from disk** (all modes — even
   single-agent, where the disk copy is the canonical record and the re-read is cheap).
2. **For each synthesis-bound (Must-Fix/Should-Fix) locked finding**, re-read the manuscript
   text its `evidence_refs` anchor: single-agent — direct targeted re-reads (the manuscript is a
   file); multi-agent — from the verification excerpts where covered, else **bounded synthesis
   pulls**: ≤ 2 spans per finding, ≤ 5k tokens per span, retrieved mechanically by the parent
   (the evidence-pull constraints, `subagent-architecture-design.md:107–111`, applied at the
   synthesis seam — deliberately resolving that doc's §Re-Targeting Open Question 1 in the
   affirmative, bounded). This is the ROADMAP §Model-Capacity "long-context re-grounding before
   synthesis" item, sized ~10–30k tokens per run.

   **The bounded-pull seam, pinned.** The pull interface lives in `run-core.md`'s Execution
   Protocol as an extension of step 10 (`run-core.md:255` — the synthesis-subagent dispatch):
   the synthesis step may request, and the parent orchestrator services, per-finding retrievals.
   **Input:** the `finding_id` + that finding's locked `evidence_refs` anchors (plus the
   what/why pull-request format `subagent-architecture-design.md:110` already specifies).
   **Output:** the excerpt text + its token count (so the ≤ 5k/span bound is mechanically
   checkable and the manifest span row can flip). **Which modes implement it:** sequential,
   hybrid, and swarm — the modes where the parent orchestrator exists and retrieval is
   mechanical; single-agent needs no pull (the manuscript is a file; step 2 re-reads directly).
   **Explicit Increment-1 scope-down:** the evidence-pull mechanism is design-doc-only today
   (grep: zero "evidence pull" hits in `run-core.md`/`hybrid-mode.md`), and Runner-Governed
   Execution Increment 4 — the orchestrator as an external host entity — is unbuilt
   (`ROADMAP.md:301`: "Increment 4 (external host orchestrator) remains future"). So this ships
   **prompt-level**: the pulls are step-text instructions executed by the orchestrating model,
   backstopped by the mechanical floors (specificity-floor + M1's V1–V5 verify the *results* on
   disk — restored counts, updated manifest rows — not the pull transcript). The step text
   carries a deferred marker (`<!-- deferred: orchestrator-pull-interface (Runner-Governed
   Execution Increment 4) -->`) recording that a mechanically enforced pull API lands with
   Increment 4, if ever.
3. **Restore specificity into the draft claims:** exact counts, names, quote anchors, from
   ledger + text. Re-grounding may only **add** specificity — it may not add findings, change
   any severity (Deficit Lock is untouched), remove counterevidence, or soften wording
   (softness-check still applies downstream). Write a `<!-- regrounding: done -->` marker on its
   own line directly after the coverage marker (which sits immediately after the title block —
   §M1.5 V5 table) when the letter is written.
4. **Update the M1 manifest:** artifacts/spans re-read here flip to `verbatim` / `in-context`
   with a `regrounded: true` row annotation. The coverage note then reflects post-re-grounding
   reality — disclosure improves because contact with the text actually happened, never because
   the note was edited. M1's validator runs unchanged on the updated manifest.

### 2. Specificity-floor fidelity gate — `validate.sh specificity-floor <letter> <ledger>`

New Python helper `scripts/specificity_floor.py` (letter_checks family; reuses the finding-ID
window rule — from each `<!-- finding: F-… -->` marker to the next marker or `^##` header, the
evidence-density window precedent, `run-synthesis.md:214`). The checkable floor, honestly
partitioned:

- **Count floor (Python-checkable):** for each delivered finding ID, collect count tokens
  (digits 2–99 and number-words two…ninety-nine; **matching is case-insensitive** — a
  sentence-initial "Nine" satisfies a ledger "nine") from that finding's ledger entry (Notable
  Finding sentence + structured block). FAIL when the ledger entry has ≥1 count token AND the
  letter window contains a vague quantifier from the pinned list AND the window contains
  **none** of the ledger's count tokens. "Nine belief failures" may not degrade to "several
  belief failures." **The pinned list is the module-level constant `VAGUE_QUANTIFIERS` at the
  top of `scripts/specificity_floor.py`** (mirrored byte-identical in
  `plugins/apodictic/scripts/specificity_floor.py`, per the dual-mirror rule), initial value
  exactly: `("several", "some", "many", "a few", "numerous", "various", "multiple",
  "a number of", "a handful", "repeated", "repeatedly")` — tunable in that one place only.
  **Match scope (pinned):** count tokens and vague quantifiers are matched over the finding's
  letter window as defined by the evidence-density window rule — `run-synthesis.md:214`
  ("Evidence-density window (v1.8.0 calibration)": from the finding's line until the next
  finding occurrence OR the next `^##` section header at column 0), applied here from each
  `<!-- finding: F-… -->` marker. Override: ID-scoped
  `<!-- override: specificity-floor F-… — <rationale> -->` via the shared
  `override_marker.has_override` helper (meta-lint M5) + an Appendix B entry — for findings
  that are legitimately non-countable.
- **Anchor floor (Python-checkable):** each delivered Must-Fix window must contain at least one
  evidence reference that token-matches one of that finding's locked `evidence_refs`
  (`apodictic.finding.v1` requires `minItems: 1`). This ties evidence-density's "≥2 references"
  to the *ledger's* references, and it bounds count-hallucination: a restored number must ride a
  ledger-matching anchor.
- **Bash-checkable (degrade path):** presence checks only — the `<!-- regrounding: done -->`
  marker and the manifest's `regrounded` annotation. No bash reimplementation of the floors
  (bash-validator ceiling; advisory WARN without `python3`).
- **Prompt-level (named as such, not pretend-mechanical):** name restoration, quote selection,
  and the add-only discipline itself are step-text instructions, backstopped by the mechanical
  guards above and by the existing Evidence Spot-Check (`run-synthesis.md:394`), which now
  samples post-re-grounding claims.

Same conventions as M1's validator: dispatcher arm + `--self-test` (M1), parsed-block resolvers
(M2), derived count (M3), shared override helper (M5), dual mirror ×2 + `check-mirror`,
changelog fragment.

### 3. Firewall-adjacent guard — re-grounding may not introduce findings

The repo Firewall (`CONTRIBUTING.md:31`: diagnostics identify problems, they don't rewrite) has a
projection-discipline sibling in the annotated-manuscript A-gates; this is the synthesis-side
analog: **the letter is a projection of the ledger, and re-grounding is read-only on the ledger.**

- Mechanical — **already owned; this spec adds nothing here.** The letter-ID-must-exist-in-ledger
  check is `finding-trace` **E1** ("dangling reference: a letter citation to an F-… ID that is not
  in the ledger" — `plugins/apodictic/scripts/finding_trace.py:12` docstring; check at
  `finding_trace.py:212–216`, matching `_ID_RE` tokens inside HTML comments per
  `letter_cited_ids`, `finding_trace.py:112–121` — exactly the pinned `<!-- finding: F-… -->`
  citation form). E1 is default-ERROR, exit 1 (`finding_trace.py:36,301–309`); `finding-trace` is
  in `AGG_VALIDATORS` (`validate.sh:181`) and runs in both directions against the canonical
  ledger↔letter pair at `--check-all` (`validate.sh:345–348`), with the E1 case pinned in its own
  `--self-test` (`e1_dangling_ref`, `finding_trace.py:442–443`). **finding-trace E1 is the sole
  owner of this check.** `specificity-floor` implements no reverse-direction ID check — two
  enforcers with subtly different ID grammars (E1's `_ID_RE` is exact-boundary, comment-scoped)
  is precisely the drift risk single ownership exists to prevent. The Pre-Letter Re-Grounding
  step text simply names `validate.sh finding-trace <run_folder>` as the smuggled-finding gate.
- Anything genuinely new noticed during re-grounding goes to §4b Additional Observations,
  without a finding ID and without a Must-Fix/Should-Fix label, flagged "surfaced post-ledger;
  awaits pass-level confirmation" (the demotion path Step 10's findings-integration check
  already defines).
- Severity writes from this step are forbidden outright; Deficit Lock + softness-check remain
  the enforcement (they run downstream of the step, so a violation is caught by existing gates
  — no new severity machinery).

### 4. Fixture / self-test plan (M2)

1. **Salience-decay fixture (the headline):** ledger locks "nine belief failures" (F-P1-01 with
   count token + evidence_refs); letter window says "several belief failures," no count, no
   override ⇒ count-floor FAIL; corrected letter ⇒ pass.
2. **Anchor-drift fixture:** a Must-Fix window cites two references, neither matching the locked
   `evidence_refs` ⇒ anchor-floor FAIL.
3. **Smuggled-finding coverage — owned by finding-trace E1, not re-fixtured here:** a letter
   carrying `<!-- finding: F-P5-99 -->` absent from the ledger already FAILS via
   `finding_trace.py` E1, whose own `--self-test` pins exactly this shape (`e1_dangling_ref`,
   `finding_trace.py:442–443`, ledger F-P5-01/02 + letter citing F-P5-99). `specificity_floor.py`
   carries **no** duplicate fixture; M2's step text and `--check-all` run finding-trace on the
   pair (§3 above).
4. **Masking fixture (reuses M1 fixture 2):** `<!-- regrounding: done -->` present, manifest
   still shows the Pass 5 artifact `absent`, letter marker `ok` ⇒ M1's V5 still FAILS — proving
   the note cannot be silenced by M2's existence.
5. **Legitimate-vagueness fixture:** ID-scoped override marker + Appendix B entry ⇒ pass.
6. **Casing fixture ("Nine"/"nine"):** ledger locks "nine belief failures"; letter window opens
   a sentence with "Nine belief failures" ⇒ count-floor **pass** (number-word matching is
   case-insensitive — a sentence-initial capital must not read as a missing count).
7. Hostile shapes: suffixed override slug (`specificity-floor-extra`), a marker quoted inside a
   code fence (must not be honored — M5 helper), a count token that
   appears only inside a manuscript quote in the window (counts — define token match on the
   window's full text, documented).

### 5. As-built corrections (M2 build PR)

Where shipped M2 deviates from the letter of this spec (or of sibling docs) — recorded, per the
§M1.8 precedent, so nobody "fixes" the build back toward stale text:

- **(a) Step placement: 9c — after the manifest, and therefore after Step 6b.** §M2.1's
  "immediately after the M1 manifest step and before the Step 10 pre-output gate" is exactly what
  shipped: **step 9c**, following the step-9b manifest it must update (M2 step 4 flips manifest
  rows — the step cannot run before the manifest exists). `docs/finding-disconfirmation.md`
  used to claim re-grounding "precedes Step 6b" — a stale pre-rework claim from before this spec
  pinned the seam, now reconciled in that doc (its §3 and §14). The imagined loss ("re-grounded
  specificity improves refutation quality") is phantom: Step 6b consumes the locked ledger + the
  intake manuscript snapshot — both verbatim disk artifacts, neither subject to context-salience
  decay — so no refutation input is degraded by running 6b first.
- **(b) Window direction: backward from the marker, not forward.** §M2.2's phrasing ("from each
  `<!-- finding: F-… -->` marker to the next marker or `^##` header") reads forward, but the
  pinned citation convention places the marker at the END of a finding's descriptive prose
  (`example-editorial-letter.md`: "…two sentences. <!-- finding: F-RR-01 -->"). A forward window
  would capture the NEXT finding's prose and miss the very sentence the marker terminates. As
  built, the window runs from the nearest preceding boundary (the prior marker's end or a
  `^##`/`###` header) up to and including the marker — the same evidence-density rule,
  direction-corrected.
- **(c) Known window edges (fail-closed; the override is the escape).** Three constructed edge
  shapes can false-positive at window boundaries: (1) **trailing prose after a marker** —
  discussion continuing past a finding's own marker attaches to the NEXT finding's window;
  (2) a **mid-discussion `###` sub-header** truncates a window early; (3) **shared-section
  siblings** — section-lead prose before the first of two co-sectioned findings lands in the
  first finding's window only. All three fail CLOSED (a spurious count/anchor FAIL, never a
  silent pass), and the ID-scoped `<!-- override: specificity-floor F-… — <rationale> -->` +
  Appendix B entry is the documented, actionable escape. The window is deliberately NOT
  redesigned around them: each is rare under the pinned letter format, and a smarter window
  (paragraph inference, sub-header classification) would trade a loud, overridable false
  positive for quiet misattribution.
- **(d) Regrounding-trace advisory: letter marker only — the manifest half is a scope-down.**
  §M2.2's degrade-path bullet names two presence surfaces: the `<!-- regrounding: done -->`
  letter marker and the manifest's `regrounded` annotation. As built, `specificity_floor.py`
  surfaces only the LETTER marker as its advisory W (`--strict` promotes). The manifest half is
  deliberately not checked here, and the §M2.2 text supports that reading: the bullet defines the
  **bash degrade path's ceiling** ("presence checks only… advisory WARN without `python3`"), not
  a Python-validator obligation; the spec's own CLI signature (`validate.sh specificity-floor
  <letter> <ledger>`) hands the validator no manifest or run-folder path to check; and the
  step-9b row grammar pins `synthesis_coverage.py` as the manifest's **only** parser, whose V3
  already enforces the annotation's well-formedness on every run — a second manifest reader
  inside specificity-floor would recreate exactly the dual-enforcer drift risk §M2.3's single-
  ownership stance exists to prevent.
- **(e) Malformed-ledger refusal (never a vacuous pass).** A ledger in which ≥ 1
  `apodictic:finding` block appears but ZERO parse to a valid finding REFUSES with a named
  blocking error (`malformed-ledger refusal`) instead of the vacuous "no ledger findings" pass —
  an all-malformed ledger must not silently disarm the floor. Single-ownership stance for
  PARTIAL malformation: when some blocks parse, the floor proceeds on the parsed subset and does
  not police the broken siblings — per-block schema repair is `structured-findings`' gate, and
  refusing on a partial would double-enforce it.
- **(f) Matcher hardening (pre-Codex build-review fold, this PR).** The build-review's
  constructed attacks landed three P2s + cheap P3s in the count-extraction cluster, all fixed
  and pinned in `--self-test`: integers **10–19** now count (the digit regex missed teens — a
  ledger "12 belief failures" could decay to "several" unpunished); locator keywords accept
  **plurals** ("scenes 30-31" is as much a locator as "sc. 30-31"); **number-words normalize to
  digit strings** at extraction, so a ledger "nine" and a letter "9" satisfy each other in BOTH
  directions (no blocking false FAIL on a faithful word→digit restoration) and a spelled-out
  "Chapter Nine" becomes a strippable locator (no over-credit); a **locator/count collision**
  ("…in the confession scene 9 belief failures cluster…") is rescued via a ledger↔window shared
  (count, plural-head) phrase — the rescue never ARMS the floor, it only un-eats a real
  restoration, so bare locators still credit nothing; and the anchor floor's
  **chapter-surface-form independence** ("Chapter 12" / "Ch.12" / "Chapter Twelve" against a
  ledger "Ch 12") is self-test-pinned. Accepted residuals, on record: a locator-eaten count in
  the LEDGER's own prose does not arm the floor (phrases never arm — arming on them would let
  s-ending verbs after locators, "Ch 3 opens", spuriously widen enforcement), and a collision
  rescue requires the window to reuse the ledger's count-noun head (a paraphrased noun after a
  collision is not rescued; the ID-scoped override is the escape).

---

## Non-goals

- **No mode-selection work** — escalation/de-escalation shipped (`docs/adaptive-mode-escalation.md`);
  this spec neither re-proposes nor modifies it and does not touch `escalation_check.py`.
- **No pass re-runs.** M2 re-reads artifacts + text; it never re-dispatches a pass (the same
  constraint the escalation check honors at its seam).
- **No changes to `run-core.md §Pre-Pass Re-Grounding`** (Blocks A/B/C) — different seam, built.
- **No new execution mode**, no focus-map format changes, no general re-targeting mechanism
  beyond the bounded synthesis pulls defined in M2 step 2.
- **No `/ready` / coach / spec-03 integration** in these PRs — the sidecar object is the
  published seam; consumers wire in later.
- **No new `*.schema.json`** — the sidecar extension follows the `complexity_signals` additive
  precedent; no `_coverage.json` row, no `finding.v1` field changes.
- **No 15th required letter section** and no change to the `synthesis-sections` validator — the
  note lives inside Appendix C; its checks live in the new validator.

## Failure modes if built badly

- **Masking instead of disclosing (the headline).** M2 restores confident-sounding specificity
  while coverage was still degraded — the "silent wrong answer" class the ROADMAP flags as worse
  than a visible failure. Guards: M1 is a hard dependency and stays mandatory after M2; the note
  is computed from the manifest (never from the letter); V5 has no override; fixture M2-4 pins
  the ordering.
- **Self-reported fiction.** The note claims verbatim re-reads that never happened. Guards: V2's
  filesystem denominator + V3's projection diff + V4's provenance gate; single-agent's residual
  epistemic gap is labeled in pinned language rather than hidden.
- **Count hallucination under gate pressure.** The count floor pushes the model to fabricate
  exact numbers. Guards: the anchor floor (numbers ride ledger-matching refs), the Evidence
  Spot-Check samples the restored claims, and the ID-scoped override exists for genuinely
  non-countable findings.
- **Boy-who-cried-degraded.** If normal multi-agent outline-mediated coverage were labeled
  degraded, authors would learn to ignore the note. Guard: mode-relative baselines (§M1.3) —
  degraded means *below the mode's own design*, not *below omniscience*.

## PR shape & estimated sessions

- **M1 — `feat/synthesis-coverage` (~2 sessions).** `synthesis_coverage.py` + dispatcher arm
  (mirrored ×2), gate wiring, prose edits (`run-synthesis.md`, `run-core.md` step 10,
  `output-structure.md`), sidecar schema/template, self-test fixtures, changelog fragment,
  status flip. Builds after spec 03's PR merges.
- **M2 — `feat/pre-letter-regrounding` (~2–3 sessions).** `specificity_floor.py` + arm
  (mirrored ×2), the Pre-Letter Re-Grounding step, manifest-update wiring, self-test fixtures,
  changelog fragment, status flip. Builds after spec 04's PR merges **and** after M1 is on main
  (hard dependency).
- Both PRs follow the standard flow (this doc goes through /spec-review; build → Codex 5.5 PR
  gate; merge commit, version bump at merge; `validate.sh --check-all` + `check-mirror` green
  before requesting review).

## Open questions (operator calls — none open; 1 defaulted at fold)

1. **Gate strictness at launch:** **Operator call (default folded 2026-07-01): V2/V3/V4
   fiction-checks blocking day one; the overall synthesis-coverage gate advisory-first for one
   release, then blocking; override before build if disagreed**. (Advisory-first = the
   `escalation-check` posture: exit 0 by default, `--strict` to halt; flips to blocking once a
   few real runs confirm the §M1.3 degrade thresholds don't over-fire.)

*(Everything else the stub left open is decided above: note placement = Appendix C subsection +
title-block marker + conditional Short Version sentence; no new schema file; the
vague-quantifier list is pinned and tunable in one constant; single-agent = declared-with-
pinned-language, multi-agent = dispatch-derived-or-fail; M2's step name and seam; bounded pull
limits ≤2×5k per finding.)*
