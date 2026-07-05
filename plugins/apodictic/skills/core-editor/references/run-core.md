# Core DE Intake, Execution & Pass Specs

*Reference file for the APODICTIC Development Editor. Loaded for every Core DE and Full DE run.*
*After passes complete, load `run-synthesis.md` for audit integration, synthesis, and deliverables.*

---

## Intake Protocol (Always Run)

### Router Integration

If the user arrived via the `/start` intake router, the router has already classified: `artifact`, `goal`, `concern`, `constraints`, and `operator`. Treat these as pre-filled intake values, skip redundant questions, and calibrate the intake below. See `references/intake-router-runtime.md` for runtime routing behavior.

If the user arrived via a direct request (without the router's prefill), run intake from scratch as described below.

### Draft-Then-Validate Workflow

**Step 1:** Read manuscript and generate DRAFT Contract Schema from text analysis alone.

> **Persist the manuscript snapshot (core-de / full-de runs).** As part of reading the manuscript, write a frozen copy to the run folder — `[Project]_Manuscript_Snapshot_[runlabel].md` — taken from the **assembled** manuscript text (if it was pasted across several messages, or supplied as a file, snapshot the assembled whole the contract is drafted against, not the raw fragments). **Normalize line endings to LF and ensure a single trailing newline; make no other change** — this is a verbatim copy, never an edit — and record its line count. This snapshot is the immutable left-hand side the Annotated-Manuscript deliverable anchors against and proves non-mutation over (see `references/annotated-manuscript.md` §The three artifacts; the run-end offer in `run-synthesis.md §Annotated Manuscript + Crosslinked Letter` consumes it). Taking it **now**, at intake, matters because the manuscript is reliably in context here — after many passes a long run's context may be compacted, so run-end re-reading is less reliable. **Skip it for partial-de / fragment-de runs** (they don't offer the marked-up copy). A mid-run manuscript revision requires a new runlabel + a fresh snapshot (the stale-`sha256` rule then fails an old manifest loudly). An aborted or downgraded run that never writes an editorial letter simply leaves the snapshot unused — a benign provenance copy no gate references.

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
14a. **POV structure:** Is this manuscript multi-POV? If yes, list the POV characters and which chapters belong to each (e.g., "Ada: chs 1, 4, 7, 10; Daphne: chs 2, 5, 8; Makayla: chs 3, 6, 9"). The mapping enables stylometric voice-distinctiveness measurement during Pass 7 (POV/Voice). Accepted answers: (a) author-supplied mapping (preferred — author-confirmed); (b) "I'd rather Pass 7 detect POV transitions automatically" (LLM-detected; results carry an author-not-confirmed caveat); (c) "single POV" (skip POV-specific stylometry); (d) "prefer not to say" (Pass 7 defaults to LLM-only voice-distinctiveness comparison). When the intake step is skipped or the question is unanswered, Pass 7 will ask the equivalent runtime question at pass start when the execution mode supports interactive input, and fall back to LLM detection otherwise.
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

After saving the contract, compute its SHA-256 hash (via `scripts/validate.sh contract-hash <contract_file>` if the script is available, otherwise `shasum -a 256 <contract_file>`) and store the hash in `Diagnostic_State.meta.json` under `contract_hash`. This enables contract drift detection during pre-pass re-grounding.

### Audit Activation at Contract

After generating the contract, recommend specialized audits based on genre, mode, and content signals. Most audits run after core passes (or after expanded pass sets when advanced passes are selected) and produce companion findings that feed the synthesis. Two tiers added in Phase 6 Wave 3 are exceptions: **Hard Prerequisite** audits (currently Field Reconnaissance for high-stakes argument-shaped runs) MUST complete before any Tier 2 evaluative pass can begin, and **Pre-DE Prerequisite** audits (currently Citation Verifier for high-stakes argument-shaped runs) run before the Development Edit begins. The Pre-Pass Prerequisite Resolution step in §Execution Protocol resolves both tiers before pass dispatch. See `references/pass-dependencies.md §4a/§4c/§4f` for tier definitions and decline-path semantics.

The contract-driven activation rules (genre/mode/content signal → recommended audits), the recommendation-not-mandate rule, and the minimum-recommendation floor live in `references/audit-routing-table.md`. Load it at the contract step.

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

APODICTIC supports multiple execution modes. The mode choice affects how passes run, not what they diagnose — the same pass specifications, Findings Ledger protocol, and synthesis format apply in all modes.

### Pre-flight & Context-Window Detection

Pre-flight metadata scanning (`scripts/preflight.sh`: line/word counts, POV/tense heuristics, token-load and mode recommendations, triage `max_turns`) and context-window detection are specified in `references/execution-modes-reference.md`. Pre-flight runs at run start; the orchestrator reads its output to set the token-fit mode floor (see §Execution Protocol) and the triage turn budget.

### Quality-Risk Mode Selection

Token-fit (above) selects the technically viable mode. Quality-risk overlays it: certain manuscript and contract characteristics warrant deeper architectural isolation than token-fit alone would prescribe. When any of the following triggers fires, the orchestrator escalates the recommendation upward from the token-fit floor and surfaces the rationale to the user before dispatch.

**Five enumerated triggers (all detectable from named artifacts — no model judgment):**

- **Q1 — Consent/governance risk.** Detectable predicate: contract genre includes Horror, Erotic, or content where power-dynamics are central; OR contract has `Consent Complexity` audit on the recommended/auto-recommend list; OR contract has `Reception Risk` audit on the recommended/auto-recommend list; OR contract notes `darkness level: HIGH` or equivalent. **Default escalation:** single-agent → hybrid (or hybrid → swarm if final-round). **Rationale:** Consent-architecture and reception-risk diagnoses benefit from architectural isolation between the structural lens (does the consent system function on the page) and the reception lens (what audiences perceive); a single-agent context risks the lenses anchoring on each other.

- **Q2 — Argument-shaped nonfiction with high stakes.** Detectable predicate: intake `constraint:nonfiction` is set AND the form is policy brief, testimony, white paper, op-ed for publication, academic argument, or open letter (router §2 / §4a Form table); OR contract has `Dialectical Clarity` audit on the recommended list with submission readiness signaled. **Default escalation:** single-agent → hybrid; if a Field Reconnaissance prerequisite is also required (per Phase 6 CR-4 work, when wired), hybrid → swarm. **Rationale:** Argument-shaped work with external stakes warrants independent stress-testing of claim ladder, evidence weight, and audience fit; anchoring across these lenses produces softer red-team than the work demands.

- **Q3 — Many POVs or non-linear structure.** Detectable predicate: contract POV count ≥3 (per intake schema POV field); OR intake explicitly flags non-linear chronology, fragmented structure, or nested narratives in the structural notes. **Default escalation:** single-agent → hybrid; ≥6 POVs → hybrid → swarm. **Rationale:** Cross-POV character coherence and information-flow tracking degrades when one context tries to hold all voices simultaneously; per-pass isolation lets each lens hold its own subset cleanly.

- **Q4 — Prior thin synthesis.** Detectable predicate: a prior run's `Diagnostic_State.meta.json` is present AND its `underdiagnosis_flag` field (or equivalent log of `validate.sh underdiagnosis-triggers` output) shows the Underdiagnosis Retry Loop fired ≥1 time in prior runs without an editorial-override resolution; OR the user explicitly states "last round felt thin / soft / underdiagnosed." **Default escalation:** sequential or single-agent → swarm. **Rationale:** A prior thin synthesis is direct evidence that this manuscript class produces weaker analysis under the previously selected mode; escalation to architectural isolation is the canonical response. Q4's flag is consumed by the next run that produces a non-thin synthesis (cleared automatically on success).

- **Q5 — Submission readiness.** Detectable predicate: intake goal = `submit` per router §2; OR Pass 11 (Submission Readiness) is in the resolved pass set; OR contract notes "final round before submission." **Default escalation:** any baseline → swarm. **Rationale:** Submission-readiness is the single highest-stakes diagnosis class APODICTIC produces; the cost differential is justified by the consequence of a missed finding before query/submission.

**Stacking and ceiling.** Multiple triggers stack, but the ceiling is swarm. If Q1 + Q5 fire, the result is swarm (ceiling), not "swarm + swarm." Quality-risk only escalates upward — never downgrades the token-fit floor.

**Override path.** The user may explicitly decline an escalation with named acknowledgment ("I understand the [trigger] risk; proceed with [baseline]"). The override is recorded in run metadata as `quality_risk_override: Q[n] — <user rationale>`. Override rationale should reference a specific reason (exploratory run, budget constraint, time pressure) rather than a generic acknowledgment. An unenumerated risk pattern may be flagged by the orchestrator as a Q6+ candidate with rationale recorded for later framework expansion.

**Validator.** `scripts/validate.sh quality-risk-triggers <contract_file> [diagnostic_state_meta_file]` enumerates fired Q1-Q5 triggers and reports the recommended escalation target. It does not select the mode; the orchestrator owns selection (token-fit floor + validator output + user override path). The validator complements `validate.sh underdiagnosis-triggers` (synthesis-time) by detecting pre-pass mode-selection triggers — different artifacts, different timing.

**Override marker syntax (in run metadata or intake notes):** `<!-- override: quality-risk-Q[1-5] — <rationale> -->`. The validator honors body markers and reports per-trigger override status.

### Single-Agent Mode (Default — Large Context)

The parent orchestrator dispatches **one subagent** that runs all passes sequentially in a single context. The manuscript loads once and remains in context throughout. The subagent runs Pass 0 → Pass 1 → Pass 2 → Pass 5 → Pass 8 → synthesis (or whatever pass set the intake resolved), writing each pass artifact and Findings Ledger entry to disk as it goes.

**When to use:** The default mode when the parent orchestrator has ≥1M context tokens available and pre-flight's estimated single-agent load is under 600K tokens. This covers most manuscripts up to approximately 200,000 words. *See §Quality-Risk Mode Selection for triggers (Q1-Q5) that may override this default upward.*

**Why it works now:** In a 200K-token window, running five analytical passes on a 120K-word novel left roughly 20K tokens of headroom by synthesis — enough for compaction to trigger and salience to decay. In a 1M window, the same manuscript leaves ~750K tokens of headroom. Context compaction is unlikely; salience decay across passes is negligible because the full analytical history remains within the window's active attention.

**What stays:** The Findings Ledger is still written to disk after each pass (compaction insurance, even if compaction is unlikely). Staged visibility is procedurally enforced: the subagent completes each pass's analysis before reading the accumulated ledger for reconciliation. Pre-pass re-grounding still applies.

**What changes vs. per-pass subagents:** The manuscript loads once instead of per-pass (~2–5x token savings). Cross-pass context is richer because the subagent retains residual memory of earlier pass analysis beyond what the ledger captures. The tradeoff: passes are not architecturally isolated, so anchoring bias is procedurally managed rather than structurally eliminated.

**Token cost estimate (118K-word manuscript):** ~240,000–300,000 tokens (manuscript loaded once + analytical overhead). Approximately 0.5–0.6x the cost of sequential mode.

**How to invoke:** This is the automatic default when context and manuscript size qualify. No user action needed. The user can override to sequential, hybrid, or swarm at intake.

### Sequential Mode

Each pass runs as an independent subagent that receives the full manuscript, contract, and accumulated Findings Ledger. Passes run in order — each subagent is dispatched after the previous one returns and its ledger entry is persisted to disk. Every pass sees the full manuscript and the full analytical history.

**When to use:** The default mode when operating in a standard-context window (<1M tokens) with manuscripts under ~60,000 words. Also the fallback for large-context models when the estimated single-agent load exceeds 600K tokens (manuscripts roughly >200K words). *See §Quality-Risk Mode Selection for triggers that may escalate sequential to hybrid or swarm.*

**Tradeoff vs. single-agent:** Higher token cost (each subagent loads the manuscript independently). In exchange: compaction resilience, architectural isolation between passes, and no context salience decay in late passes. These benefits matter most when context headroom is tight.

### Hybrid Mode

Pass 0+1 reads the full manuscript as a triage subagent and produces a **focus map** — a targeting document that tells each subsequent pass which scenes to deep-read. Later passes receive the reverse outline (the compressed manuscript) plus only the focus map's targeted excerpts, not the full text.

**What the user should know:** Hybrid mode provides most of swarm's quality gains — architectural isolation, independent analysis, reduced anchoring — at roughly **2–3x the token cost** instead of swarm's 5x. The tradeoff: later passes see targeted excerpts rather than the full manuscript, so they depend on the focus map's accuracy. The focus map errs on inclusion (targeting 30–50% of scenes), and every pass still receives the complete reverse outline for structural context.

**When to use:** In standard-context mode, pre-flight recommends hybrid for manuscripts in the 60–100K word range. In large-context mode, hybrid is dormant by default (single-agent handles this range), but the user can invoke it if they want the focus map's targeted-reading approach for its own sake. Also valuable for:
- Runs where the user wants better-than-default quality without full swarm cost
- Standard editorial workflow (not final-round submission diagnostics)

**When NOT to use:** Manuscripts under ~40,000 words (sequential or single-agent handles these comfortably), or final-round diagnostics where independent-lens verification justifies swarm's cost. Pre-flight's mode recommendation can be overridden by the user at intake. *See §Quality-Risk Mode Selection for triggers that may escalate hybrid to swarm.*

**How to invoke:** The user requests hybrid mode at intake or before pass execution begins. Example: "Run this in hybrid mode" or "Use selective reading." The system confirms mode selection and token cost implications before proceeding.

**Full specification:** See `references/hybrid-mode.md` for the focus map format, targeting grammar, confidence tiers, excerpt extraction protocol, and risk analysis.

### Swarm Mode

Each evaluative pass runs as an independent subagent that receives the full manuscript. Unlike sequential mode, passes 2, 5, and 8 can run **in parallel** since they don't depend on each other's ledger entries — they each receive the same accumulated ledger (from the triage pass only) and produce independent findings.

**What the user should know:** Swarm runs each pass in **architectural isolation** — no pass sees prior analysis until the reconciliation step — which eliminates anchoring bias and gives an independent-lens read, at roughly **5x the token cost** of single-agent mode (a long-fiction re-test measured the gap at ~8.5× or more — the swarm figure excludes orchestration overhead). Its defensible everyday value is that isolation — a writer/verifier separation on a final pass — **as verification insurance, not a higher raw yield.** An earlier validation reported ~2× findings; a 2026-06 N=1 pilot on a 130K-word manuscript did **not** reproduce a recall advantage (single-agent tied-or-edged swarm on real-issue recall at a fraction of the cost; swarm's edge was tighter severity-banding, a directional N=1 read), so do not advertise "deeper analysis" as the everyday rationale. Reserve swarm for **final submission prep** and the verifier-isolation spot-check. *Last re-validated: 2026-06 (N=1, directional — not a verdict; see `docs/swarm-vs-single-eval-pilot/`).*

**When to use:** When independent-lens verification matters more than token economy — final-round insurance, not the everyday default. Valuable regardless of context window size because the benefit comes from architectural isolation, not compaction resilience. Particularly valuable for:
- Final-round diagnostics before submission
- Cases where prior runs produced a synthesis that felt thinner than the pass analysis warranted
- Manuscripts where the single-agent approach produced findings that echo rather than complicate each other

**When NOT to use:** Quick diagnostics, partial manuscripts, budget-constrained runs, or manuscripts short enough that single-agent handles them comfortably. *See §Quality-Risk Mode Selection — Q4 (prior thin synthesis) and Q5 (submission readiness) typically default to swarm.*

**How to invoke:** The user requests swarm mode at intake or before pass execution begins. Example: "Run this in swarm mode" or "Use subagent passes." The system confirms mode selection and token cost implications before proceeding.

#### Execution Protocol

**Parent orchestrator responsibilities:**
1. Run pre-flight (`scripts/preflight.sh`) to get manuscript metadata and token load estimate
2. Determine context window size (model identifier check)
3. Select execution mode using the layered rule:
   - **(a) Token-fit floor.** Use pre-flight's large-context recommendation if ≥1M tokens available, standard-context recommendation otherwise. This establishes the baseline mode (the technically viable floor).
   - **(b) Quality-risk overlay.** Run `scripts/validate.sh quality-risk-triggers <contract_file> [diagnostic_state_meta_file]` (or perform the equivalent inline check per §Quality-Risk Mode Selection). For each fired Q1-Q5 trigger, raise the recommendation toward its escalation target. Stacking triggers cap at swarm. Quality-risk only escalates upward; it never demotes the floor.
   - **(c) Final mode = max(token-fit-mode, quality-risk-recommendation).** Surface the rationale to the user before dispatch. Explicit user override takes precedence (recorded in run metadata as `quality_risk_override`).
4. Run intake in the parent context (load SKILL.md, run-core.md, generate contract, resolve pass set)
5. Initialize the Findings Ledger
6. **Pre-Pass Prerequisite Resolution (Phase 6 Wave 3 / wired in v1.7.9).** Before pass dispatch, walk `references/pass-dependencies.md §4a` for any audit at **Hard Prerequisite** or **Pre-DE Prerequisite** tier, given the resolved contract:
   - **Pre-DE Prerequisite audits** (currently Citation Verifier for high-stakes argument-shaped runs) run BEFORE the Development Edit begins. Their output (e.g., `Citation_Ledger.md`) is consumed by argument-cluster passes but is not part of the pass dependency graph. Dispatch the audit per its reference file's pre-DE handoff protocol; persist its output artifact to the project root.
   - **Hard Prerequisite audits** (currently Field Reconnaissance for high-stakes argument-shaped runs) run BEFORE any Tier 2 evaluative pass. Their output (e.g., `Field_Reconnaissance_Report.md`) materially changes what the passes evaluate against — they must complete and append to the Findings Ledger before dispatch step 7 begins.
   - **Decline path** (per `pass-dependencies.md §4c` + §4f edge cases 8-9). If the user declines either tier, present the explicit fork: (a) terminate the run with the tier's "cannot proceed" advisory, OR (b) downgrade to Auto-recommend before synthesis with a body-of-letter blind-spot disclosure recorded at synthesis (per `run-synthesis.md §Step 3 Blind Spot / Absence Inventory`). Silent omission is forbidden at these tiers. Record the resolution in the Audit Invocation Log with rationale (`prerequisite-declined; downgrade-with-disclosure` or `prerequisite-declined; run-terminated`).
   - **Tier resolution invariant.** The Pre-Pass Prerequisite Resolution step honors the §4f Audit Tier Precedence Rule: when an audit is surfaced through multiple paths, the highest tier wins. A finding-trigger at Auto-recommend before synthesis cannot promote an audit to Hard Prerequisite — Hard Prerequisite is reserved for router-triggered prerequisite policy on argument-shaped runs with high-stakes signal (per `pass-dependencies.md §4a` argument-shaped routing definition + high-stakes signal definition).

**If single-agent mode:**
7. Dispatch one subagent using the host platform's delegated-agent facility with a frontier reasoning/editorial model and instructions to run passes sequentially, writing each artifact and ledger entry to disk as it completes each pass. The subagent inherits the Pre-Pass Prerequisite outputs (Field Recon report, Citation Ledger) as analytical inputs; they are read alongside the contract before the first Tier 1 pass.
8. The single subagent runs all passes and synthesis, persisting each ledger entry to disk before beginning the next pass

**If sequential, hybrid, or swarm mode:**
7. Dispatch each pass as a subagent using the host platform's delegated-agent facility, with turn budget sized per pre-flight where supported. Pre-Pass Prerequisite outputs (Field Recon report, Citation Ledger) are passed to each pass subagent as analytical context alongside the contract.
8. **Persist each subagent's ledger entry to disk immediately upon return** — before dispatching the next subagent
9. Pass the growing Findings Ledger to each subsequent subagent
10. Dispatch the synthesis subagent with the complete ledger and the Pre-Pass Prerequisite outputs. **As part of this dispatch, write the Synthesis Coverage Manifest** (`[Project]_Synthesis_Read_Manifest_[runlabel].md` — row grammar and denominator in `run-synthesis.md` §Processing Protocol step 9b): one `artifact` row per enumerated run-folder item (`verbatim` for files handed to the synthesis subagent, `summary` for artifacts represented only via the ledger / reverse outline, `absent` for on-disk artifacts in no synthesis input), plus `span` rows from the preflight section boundaries — in hybrid mode the focus map's Synthesis Verification Excerpts are the `in-context` spans. Written by the parent **before** the subagent runs, the manifest is `dispatch-derived` — the strongest coverage evidence available without platform introspection — and `validate.sh synthesis-coverage` later reconciles the letter's coverage note, marker, and sidecar object against it

   **Pre-Letter Re-Grounding bounded pulls (`docs/synthesis-regrounding.md` M2).** In sequential / hybrid / swarm, the synthesis step's Pre-Letter Re-Grounding (`run-synthesis.md` §Processing Protocol step 9c) may request, and the parent orchestrator services, per-finding retrievals to restore specificity before the letter is written. **Input:** the `finding_id` + that finding's locked `evidence_refs` anchors (plus the what/why pull-request format already specified in `docs/subagent-architecture-design.md:110`). **Output:** the excerpt text + its token count (so the ≤ 5k-tokens/span, ≤ 2-spans/finding bound is mechanically checkable and the manifest span row can flip to `in-context` / `regrounded: true`). **Increment-1 scope-down:** the orchestrator-governed pull *API* is unbuilt — Runner-Governed Execution Increment 4 (external host orchestrator) remains future (§Runner-Governed Execution, `ROADMAP.md`) — so this ships **prompt-level**: the pulls are step-text instructions the orchestrating model executes, backstopped by the mechanical floors (`specificity-floor` + `synthesis-coverage` verify the *results* on disk, not the pull transcript). Single-agent needs no pull (the manuscript is a file; step 9c re-reads it directly).

   <!-- deferred: orchestrator-pull-interface (Runner-Governed Execution Increment 4) -->

**Turn budgets (from pre-flight):**
- **Triage subagent (Pass 0+1):** `max_turns` = `ceil(total_lines / 500) + 20` (pre-flight computes this). For an 84K-word / 5,759-line manuscript, this yields `max_turns: 32`.
- **Analytical passes (Pass 2, 5, 8):** Default turn budget. In hybrid mode these passes read the reverse outline + targeted excerpts; in sequential/swarm they read the full manuscript. Neither requires elevated budgets because the manuscript is provided as a file path, not pre-loaded into the prompt.
- **Synthesis:** Default turn budget.

**What each pass receives:**

| Input | Single-Agent | Sequential | Hybrid | Swarm |
|-------|-------------|-----------|--------|-------|
| Manuscript | Full (in context, loaded once) | Full (file path, per subagent) | Triage: full; later passes: outline + excerpts | Full (file path, per subagent) |
| Contract | Yes | Yes | Yes | Yes |
| Pass specification | All passes provided upfront | One pass per subagent | One pass per subagent | One pass per subagent |
| Accumulated Findings Ledger | In context (growing) + on disk | All prior passes (from disk) | All prior passes (from disk) | Triage only (passes 2/5/8 get same ledger) |
| Focus map | No | No | Yes (for later passes) | No |

**What each pass subagent returns:**
- Its pass artifact (analysis output), written to disk — **beginning with the §3-sourced pass header** (see below)
- Its Findings Ledger entry (formatted per `references/findings-ledger-format.md` §Ledger Entry Format), written to disk

**Pass-artifact header (first line of every Core DE pass artifact).** Emit one blockquote line at the very top of each pass artifact:

```
> **Macro block:** <one of the 8, from §3> · **Writer question:** <the §3 User Question for this pass> · **Legacy pass id:** Pass <N>
```

The three values are **read from `references/pass-dependencies.md §3` (Macro Block Definitions), never authored** — §3 is the single source of truth for the 8 blocks, the pass→block map, and each block's User Question. The block is the pass's **own canonical §3 block by pass id**, even in a concern-driven run that pulls a dependency pass outside its usual block (e.g., Pass 0/1 in a Characters-concern run still declares Structure Map / Reader Dynamics — the map is by pass, not by run). This makes a directly-opened file legible without framework knowledge. `scripts/validate.sh pass-header <pass_artifact> [pass-dependencies.md]` checks it (H1 present — a header-less legacy artifact WARNs, not ERRORs; H2 block ∈ the 8 + block↔pass + question all agree with §3; H3 non-empty). Canonical example: `references/example-pass-artifact-header.md`.

**Post-pass validation (all modes):** After each pass writes its ledger entry, verify the entry contains all 5 required subsection headings: Notable Findings, Data Artifacts for Letter Reference, Cross-Pass Connections, Unresolved Questions, Audit Triggers (use `scripts/validate.sh ledger-check` if available, otherwise check inline). If any section is missing, fix before dispatching the next pass. A structurally incomplete ledger degrades synthesis quality. Additionally verify that each synthesis-bound (Must-Fix/Should-Fix) Notable Finding carries an `apodictic:finding` structured block (`scripts/validate.sh structured-findings <ledger>`; see `references/findings-ledger-format.md`) — the block is required, not optional, for findings that propagate to synthesis.

**Pass grouping:** In multi-agent modes (sequential, hybrid, swarm), Pass 0 and Pass 1 run in a single combined subagent (both are full-read passes with no dependencies). All subsequent passes run as individual subagents. In swarm mode, passes 2, 5, and 8 may run in parallel. In single-agent mode, all passes run sequentially in one subagent context.

**Staged visibility:** In multi-agent modes, isolation is architecturally enforced — no subagent has prior pass artifacts in its context, only the ledger entries provided for reconciliation. In single-agent mode, isolation is procedurally enforced: the agent completes each pass's analysis before reading the accumulated Findings Ledger for reconciliation. Prior pass artifacts remain in context, so the agent must actively compartmentalize its analysis. The explicit instruction to "analyze first, reconcile second" reduces anchoring, though it cannot fully eliminate it the way architectural isolation does.

**Token cost estimate (118k-word manuscript):**

| Mode | Estimated total tokens | Quality | Context requirement |
|------|----------------------|---------|--------------------|
| Single-agent (all passes, one context) | ~240,000–300,000 | Strong; procedural isolation, ledger on disk | ≥1M tokens |
| Sequential (full manuscript per pass) | ~400,000–500,000 | Strong; architectural isolation, compaction-safe | Any |
| Hybrid (selective reading) | ~500,000–690,000 | Strong; architectural isolation + targeted excerpts | Any |
| Swarm (full manuscript, parallel) | ~1,000,000–1,200,000 | Best; no cross-pass influence, parallel execution | Any |

Note: Single-agent mode restores the token efficiency of the pre-v1.0.4 single-context approach while retaining the Findings Ledger protocol and staged visibility. It is viable only when the context window is large enough that compaction and salience decay are non-issues. Sequential and higher modes remain available for standard-context models or user preference.

For full architecture details, cost analysis, and risk discussion: see `docs/subagent-architecture-design.md`.

---

### Mid-Run Escalation Check (Required, runs once after Tier 1)

The execution mode is chosen at preflight from coarse heuristics (word count, a pronoun-frequency POV guess). After **Tier 1** (Pass 0 Structure Map + Pass 1 Reader Orientation) the manuscript's actual complexity is known and may exceed that estimate. Run this checkpoint **once, after Tier 1 completes and before dispatching the first Tier 2 pass** — the only safe point to switch (never re-run completed passes; the Tier-1 Findings Ledger entries carry forward unchanged, only the Tier-2 dispatch method changes).

1. **Detect.** Run `scripts/validate.sh escalation-check <run_folder>` (or, on a no-shell host, evaluate the triggers inline). It reads the sidecar's current `last_session.execution_mode` and `complexity_signals`, and computes the Tier-1 finding count directly from the ledger (`F-P0-…` / `F-P1-…` blocks). The triggers are **condition-triggered, not model-emergent** — each is a count or a boolean, so the check fires identically across models:
   - `pov_count > 3` (preflight's pronoun heuristic underestimated)
   - `nonlinear_timeline` (non-linear or nested-frame structure)
   - `belief_failures > 5` **or** `orientation_failures > 3` (higher-than-expected analytical density)
   - `tier1_finding_count > 20` (a complex synthesis ahead)
   A signal the sidecar doesn't carry is reported **unevaluable** (never fires) — assess that dimension by hand. Record the signals you discovered into the sidecar's `complexity_signals` so the check is mechanical (see the Pass 0/1 output note).
2. **Recommend (never automatic).** If `escalation-check` recommends a switch (single-agent → sequential; sequential → hybrid/swarm), present the author a brief summary — *"Tier 1 found [fired triggers]. I'd recommend switching from [current] to [recommended] for the remaining passes (cost difference ~[N]K tokens). Proceed?"* — and switch **only on confirmation**, writing the new `execution_mode` to the sidecar. **De-escalation** is symmetric but conservative: when no trigger fires *and* every complexity signal is in the clearly-simple band, the check recommends dropping an over-provisioned `hybrid`/`swarm` down to `sequential` (a missing or malformed signal blocks it — wrongly stripping isolation off a complex manuscript risks wrong analysis, worse than wasted tokens). Same author-confirmed handshake.

See `docs/adaptive-mode-escalation.md` for the trigger / recommendation matrix and the `complexity_signals` contract.

### Uncertainty-Resolution Intake Interview (Optional, interactive hosts only)

At this same after-Tier-1 seam — and **only** on an interactive-input-capable host — you may run a narrow disambiguation loop for any structural ambiguity Pass 0/1 *detected but could not settle from the text* ("is the non-linear ordering in Ch 4-6 a deliberate braid, or drift?"). It is **distinct** from the mechanical, count-triggered Escalation Check above: it is a model-judgment loop (generate targeted questions, interpret free-text answers), and it borrows only the *seam*, not the mechanics.

- **Ask only detected-ambiguity questions.** Every question is a flavor of *intentional-vs-accidental*. Never re-ask the contract (genre / controlling idea / reader promise / who it's for) — the draft-then-validate intake and Shelf & Positioning already own that.
- **Calibrate, never suppress.** An answer may tell analysis to *treat a feature as intended* (assess it on its own terms); it may **never** suppress a flag class or pre-empt a verdict before Triage locks it — that is the concession loop the Deficit Lock forbids.
- **Record** each query as an `apodictic.intake_query.v1` block in a `[Project]_Intake_Interview_[runlabel].md`, then validate with `scripts/validate.sh intake-interview <run_folder>`. On a non-interactive host, **skip** the loop and proceed with the framework's own intentionality inference (it never blocks a run). Full protocol: `references/intake-interview.md`, spec `docs/uncertainty-intake-interview.md`.

---

### Pre-Pass Re-Grounding (Required, Mode-Conditional)

Before beginning each evaluative pass (Passes 1, 2, 5, 8, and any Full DE passes), re-ground on the contract and Findings Ledger. The protocol has three named blocks: Block A is universal (mechanical invariant), Blocks B and C are mode-conditional (model-compensation behavior). The original failure mode — context salience decay across passes — is real on standard-context models but negligible in single-agent large-context runs; the mode-conditional structure preserves the compensation where it is needed and lightens it where the underlying failure does not occur. The contract-drift check in Block A is mode-independent: it is a Tool-invocable mechanical check, not model compensation, and must fire in all modes.

**For Pass 0:** No re-grounding needed (first pass; no ledger yet). Block A still fires once at run start to record the contract hash.

**For all subsequent passes:**

#### Block A — Contract Integrity Check (Universal, all modes)

Mechanical, low-cost, mode-independent. This block is the Tool-invocable-check role of pre-pass re-grounding and runs in single-agent, sequential, hybrid, and swarm modes alike.

1. Compute the current SHA-256 hash of the contract file.
2. Compare against the `contract_hash` stored in `Diagnostic_State.meta.json`.
3. Use `scripts/validate.sh contract-check <file> <hash>` if available; otherwise `shasum -a 256 <file>` and compare manually. See §Mechanical Validation Protocol → contract drift for the canonical entry.
4. On drift: warn the user before proceeding. If intentional (author-requested revision), update the stored hash; if unintentional, investigate before continuing.

Block A is mandatory regardless of mode. The contract-drift check exists to catch out-of-band file modification, which can happen in any execution architecture.

#### Block B — Full Re-Grounding (Standard-context modes: sequential, hybrid, swarm)

In sequential, hybrid, and swarm modes, each evaluative pass runs in its own subagent context. The contract and ledger must be re-loaded from disk because the prior subagent's context did not persist. Salience decay — the model's attention drifting from earlier-loaded anchors as new content accrues — is the original failure mode this protocol was designed to counteract.

1. Run Block A (contract integrity check).
2. Re-read the contract's controlling idea, anti-idea, and non-negotiables in full.
3. Re-read the accumulated Findings Ledger in full.
4. Do not re-read prior pass artifacts — the ledger is the compressed representation; pass artifacts are reference material for specific claims, not re-reading material.

#### Block C — Anchor Confirmation (Single-agent large-context mode)

In single-agent mode, the contract and ledger are already in active context (loaded once at run start, updated on disk after each pass). With a 1M-token context window holding a typical novel (~180K tokens) plus all analytical overhead, salience decay across passes is negligible — the anchors remain in attention. Re-loading the same text would be decorative and wasteful.

Block C preserves the salience benefit of re-grounding without the redundant token cost:

1. Run Block A (contract integrity check) — same mechanical check as Blocks A/B.
2. **Anchor confirmation:** before beginning the pass's analysis, the agent re-states the contract's controlling idea + anti-idea + non-negotiables in its own words from active context (a one-line restatement is sufficient). This refreshes salience without re-loading the contract text.
3. **Ledger awareness:** the agent reviews the most recent ledger entry it wrote (already in active context) for cross-pass connections; no fresh re-load.

If single-agent salience drift is later detected on very long manuscripts (>200K words), Block C may be strengthened (e.g., add "scan the most recent ledger entry for cross-pass connections") without becoming Block B. If a quality-risk trigger (per §Quality-Risk Mode Selection) escalates a single-agent run to hybrid or swarm mid-selection, Block B applies for the run instead of Block C.

#### Block selection

Block selection is locked at run start based on the selected execution mode:

| Mode | Block A | Block B | Block C |
|------|---------|---------|---------|
| Single-agent (large-context) | Yes | — | Yes |
| Sequential | Yes | Yes | — |
| Hybrid | Yes | Yes | — |
| Swarm | Yes | Yes | — |

If mid-run mode escalation lands as a future capability (per ROADMAP), the escalation handler is responsible for re-running this selection table.

### Mechanical Validation Protocol

APODICTIC uses `scripts/validate.sh` for lightweight, zero-token invariant checks when the script is available. These enforce structure mechanically rather than relying on prompt-level instructions alone.

**Availability:** `scripts/validate.sh` and `scripts/preflight.sh` are bundled inside the plugin directory (`plugins/apodictic/scripts/`), so they ship with both the local repo and the installed Codex package. When the script is not available (e.g., on hosts that cannot execute local shell scripts, such as ChatGPT), the system must perform the equivalent checks inline — the invariants are required regardless of whether the script exists. The script is an optimization (zero-token, sub-second), not a dependency.

**When to run each check:**

| Checkpoint | Script Command (if available) | Inline Fallback | When |
|---|---|---|---|
| Contract integrity | `validate.sh contract-hash <file>` | `shasum -a 256 <file>` | At intake — store hash in sidecar |
| Contract drift | `validate.sh contract-check <file> <hash>` | Compare `shasum -a 256` output to stored hash | Before each pre-pass re-grounding |
| Ledger structure | `validate.sh ledger-check <file>` | Verify each pass entry contains 5 required subsection headings (see `references/findings-ledger-format.md` §Ledger Entry Format) | After each pass appends to the ledger |
| Artifact naming | `validate.sh artifact-names <dir> <project> <runlabel>` | Check each pass artifact filename matches `[Project]_Pass[N]_[Name]_[runlabel].md` | Before synthesis |
| Synthesis sections | `validate.sh synthesis-sections <file>` | Check for all 14 required section headings as markdown headings (see below) | After writing editorial letter |
| State size | `validate.sh state-lines <file>` | `wc -l` | At resume gate |

**On failure:**
- **Contract drift:** Warn the user. If intentional (author-requested revision), update the hash. If unintentional, investigate before proceeding.
- **Ledger structure:** Fix the missing section before dispatching the next pass. A ledger entry missing "Cross-Pass Connections" means synthesis loses its highest-value input.
- **Artifact naming:** Rename before synthesis so the Results Guide points to correct files.
- **Synthesis sections:** Fix before delivering to the author. A letter missing "Protected Elements" or "Control Questions" is incomplete.

**Design principle:** These checks encode taste mechanically. They cost zero tokens when the script is available, and minimal tokens as inline checks when it isn't. When the system detects a pattern of failures, the fix should go into the script or the protocol — not into longer prompts.

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

**Output:** `[Project]_Pass0_Reverse_Outline_[runlabel].md` with verified word counts (naming per `output-structure.md`)

**Mid-run escalation signals (record to the sidecar):** Write the discovered POV-character count and whether the timeline is non-linear / nested-frame into `complexity_signals.pov_count` and `complexity_signals.nonlinear_timeline` in `Diagnostic_State.meta.json`. The §Mid-Run Escalation Check reads these (plus Pass 1's failure counts and the Tier-1 finding count) after Tier 1 to recommend a mode escalation before Tier 2.

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

**Mid-run escalation signals (record to the sidecar):** Record the **counts** of Orientation Failures and Belief Failures into `complexity_signals.orientation_failures` and `complexity_signals.belief_failures` in `Diagnostic_State.meta.json` — the §Mid-Run Escalation Check reads them after Tier 1 (a high analytical density argues for a higher execution mode for the remaining passes).

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
- Cultural register mismatch or tone-deaf moments on identity/power content at 2+ scenes → recommend **Reception Risk** audit if not already activated

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
- Orphan scenes ≥3, or proportional imbalance >40% in any part → recommend **Compression** audit if not already activated

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

**`evidence_quote` (Annotated-Manuscript quote rung — Pass 5 pilot).** When a Pass-5 finding is about a **specific sentence or line** (a flat-affect beat, a puppet-moment decision line, a voice-drift sentence), attach that span verbatim as `evidence_quote` in the finding's structured block — a **single line copied** from the manuscript, never composed. It lets the marked-up copy anchor the margin note at that exact sentence. **Omit it** for a chapter/arc-level finding (motivation arc, agency-across-acts) — the note then anchors at the chapter, as today. A two-line exchange contains a newline and won't light the rung: pick the single most diagnostic line, or omit. The copy is firewall-safe by construction — the build-time locator emits a quote anchor only when the span occurs in the manuscript verbatim and exactly once, so a non-verbatim or non-unique quote is dropped and the note falls back to the chapter rung (the **A6** gate is the validate-time backstop against a forged quote anchor). See `findings-ledger-format.md` §"When to populate `evidence_quote`".

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

**What to include:** See `references/findings-ledger-format.md` §Ledger Entry Format.

**What NOT to include:** The full pass analysis. The ledger is an extraction, not a copy. If a finding is in the ledger, the evidence is in the pass artifact; the ledger points to it.

**Consolidation requirement.** After pass dispatch completes and before synthesis begins, the raw per-pass Ledger Snippets must be consolidated into a by-mechanism ledger per the Findings Ledger Consolidation Contract in `run-synthesis.md §Step 2 — Findings Ledger Consolidation Contract`. Consolidation is mandatory, not optional. Validator: `scripts/validate.sh ledger-consolidation`.

**Pass 0 and Pass 10 exception:** These are data-building passes. They do not require ledger entries unless they surface an observation that warrants it (e.g., a Rule Ledger inconsistency detected during outline construction, or an entity continuity error noticed during tracking). When a genre module adds analytical tracking to Pass 0 (such as the SFF Rule Ledger), notable patterns in that tracking should generate a ledger entry.

#### Ledger Entry Format & Structured Findings Block

The per-pass ledger entry template (the five required subsections: Notable Findings, Data Artifacts for Letter Reference, Cross-Pass Connections, Unresolved Questions, Audit Triggers) and the optional machine-parseable Structured Findings Block live in `references/findings-ledger-format.md`. Load it when writing or validating ledger entries.

---

#### Ledger Discipline

- **Notable findings are not all findings.** Include only findings that should appear in or inform the editorial letter. A belief failure rated "minor" that doesn't connect to a pattern is pass-level data, not a ledger entry. A belief failure rated "moderate" that connects to a root cause is a ledger entry.
- **When in doubt, include.** A finding whose notability is uncertain should go in the ledger rather than be left out. The synthesis step can ignore a noisy ledger entry; it cannot recover a finding that was never recorded. Err on the side of inclusion for any finding that *might* connect to a pattern — the next pass may confirm or disconfirm its importance.
- **Cross-pass connections are the ledger's highest-value output.** These are the observations that fall between passes — the synthesis step can't make them if it can't see the earlier pass data. Write them explicitly: "Pass 8 found X, which connects to Pass 5 Finding Y because Z."
- **Retroactive promotion.** A later pass may reveal that an earlier pass's finding is more important than it originally appeared. When this happens, the later pass should: (1) note the connection in its own Cross-Pass Connections section, and (2) append a brief **Retroactive Addition** to the earlier pass's ledger section, promoting the finding and explaining why it now matters. Format: `**[Retroactive — added by Pass N]:** Pass M's finding on [X] is more significant than initially assessed because [reason]. Promotes to notable.` This ensures the synthesis step sees the upgraded finding in the context of the pass that generated it, not only in the pass that recognized its importance.
- **Unresolved questions feed the stress test.** If a pass surfaces something that feels like a vulnerability but doesn't fit the pass's diagnostic categories, log it here. The stress test step will draw from these.
- **Data artifacts are revision tools.** The editorial letter is an argument; the pass artifacts contain tools the author can use during revision (agency timelines, competence inventories, reveal timelines). The ledger tells the synthesis step which tools exist so the letter can point to them.

---

## After Pass Execution → Synthesis

When all selected passes and their dependencies are complete, load `references/run-synthesis.md` for the audit integration point, synthesis processing protocol, editorial letter format, deliverables (diagnostic state, sidecar, evidence spot-check).

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

## After Synthesis → State Lifecycle

For revision rounds and state management, load `references/state-lifecycle.md`. That file covers:
- **State Gardening Protocol** — threshold-triggered archival of completed sessions, resolved handoffs, and answered control questions
- **Revision Round Protocol** — delta scan, ripple check, resolution verification for re-analyzed manuscripts
