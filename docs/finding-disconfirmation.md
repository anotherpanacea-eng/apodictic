# Adversarial finding disconfirmation: HIGH means "survived" (apodictic) — build spec

**Status:** **Built** (this PR — Step 6b + the `[Project]_Refutation_Record_` artifact +
`refutation_check.py` three-arm validator + the behavioral eval fixtures; spec-review pass 1 folded
2026-07-01 BUILD-READY-WITH-FIXES 0 P1; Opus build-review READY-WITH-FIXES — the only P2 was this
Status flip, every constructed attack failed closed). **Estimate:** 2–3 sessions, one PR
(split point named in §Build). **Owner of the decision:** craft (the writer's revision-triage call).
<!-- built-when: scripts/refutation_check.py -->
**Provenance:** Opus 4.8 pick #1 — a genuine miss in the Fable list; evidence verified against the
code 2026-07-01. Expanded to a full spec 2026-07-01; every anchor below re-verified by grep/read
against the repo at expansion time.
**Sequencing (wave ROADMAP, Lane A):** build after stub 03 (declined-finding state) and stub 05-M1
(coverage disclosure) land, before stub 05-M2 — all three touch `run-synthesis.md`; sequencing keeps
the synthesis-time edits out of one PR. Interactions with 03 and 05 are pinned in §Interactions.
**Build-PR convention:** the build PR copies this spec to `docs/finding-disconfirmation.md`, flips
this Status line to **Built**, and carries a live `built-when` marker per
`docs/qol-status-drift-lint.md` §Marker syntax (this scratch copy is outside the lint's `docs/**`
scan scope; the in-repo copy is what the lint watches).

---

## 1. Problem & verified evidence

- `plugins/apodictic/skills/core-editor/references/output-policy.md:47`:
  "*[HIGH CONFIDENCE] — Multiple passes converge on same diagnosis; textual evidence clear*" —
  HIGH is defined by **convergence**, not survival. Correlated passes from one model reasoning the
  same wrong way inflate to HIGH. The usage guideline (`output-policy.md:54`, "HIGH requires
  evidence from 2+ passes or unambiguous textual proof") is more agreement, from the same reasoner.
- `output-policy.md:106`: lens verdicts are "*convergence indicators that feed confidence*" — more
  agreement machinery, no refutation machinery.
- `ROADMAP.md:38` (§V1 — Finding correctness): "*None of it can tell whether a finding is right,
  relevant, or helpful — that is editorial judgment, and a system asked to hunt structural defects
  can always name one.*" The maintainer's own statement that no validator tests finding truth.
- Grep `disconfirm|falsif` across `references/` and `scripts/`: the only hit is `run-core.md:597`
  ("the next pass may confirm or disconfirm its importance" — a when-in-doubt-include note about
  ledger inclusion, not a refutation mechanism). Grep `refutation` repo-wide: **zero hits** —
  greenfield surface, no naming collision.
- `references/adversarial-stress-test.md` — **verified: it targets the manuscript, not the tool's
  findings.** Its purpose line (§Purpose, line 9) is "identify what skeptical, uncharitable readers
  would criticize" — it *generates* claims against the book; §Integration (line 116) even says
  stress-test findings "do NOT automatically escalate severity of existing findings." It is a
  finding **generator**. The Adversarial Self-Check (`run-synthesis.md` §Step 6) tests severity
  *calibration* in one sentence per direction — it never re-contacts the manuscript. The Evidence
  Spot-Check (`run-synthesis.md` §Evidence Spot-Check) verifies 5 sampled citations *exist and
  match* — it confirms the letter's evidence, it does not hunt **counter**-evidence. Nothing in the
  flow attempts refutation before findings ship.

**Net:** every existing adversarial surface either attacks the manuscript or checks the letter's
internal consistency. No surface attacks the *findings*.

## 2. Decision it changes

Which findings the writer spends a revision session on. Today a rock-solid Must-Fix and an
over-eager one look identical, so the writer either over-trusts (revises what was fine) or
under-trusts (ignores the letter). A HIGH that means "survived a recorded disconfirmation attempt"
re-ranks the act-on list — and a refuted finding arrives *labeled as refuted, with the
counter-evidence quoted*, instead of silently shipping at full confidence.

## 3. Design overview

A synthesis-time **Finding Disconfirmation Pass** — new **Step 6b** in the
`run-synthesis.md` §Processing Protocol (lettered, not renumbered: Steps 7–13 are cross-referenced
by validators and other reference files; a renumber ripples for no benefit; the `§4b` letter
section is the in-repo precedent for lettered insertion).

**Ordering within the protocol:** after Step 5 (Triage + **Deficit Lock** — severities are already
structurally locked, so this pass physically cannot be the softening vector) and after Step 6
(Adversarial Self-Check — so the pass supplements, not duplicates, the one-sentence calibration
test), before Step 7. Steps 8–10 then consume the re-mapped confidences; the letter (Step 11) is
written with refutation outcomes already known. 05-M2's Pre-Letter Re-Grounding is built as
**step 9c** — after the step-9b coverage manifest it must update, and therefore *after* Step 6b
(`docs/synthesis-regrounding.md` §M2.5a; this paragraph's earlier "runs before Step 6b" was a
stale pre-rework claim). Nothing is lost by the ordering: Step 6b consumes the locked ledger +
the intake manuscript snapshot, both verbatim disk artifacts that do not decay; 05-M1's coverage
note discloses any context degradation independently.

**What the pass does, per eligible finding:** an adversarial attempt to refute the diagnosis
against the manuscript text — hunt counter-evidence spans, generate alternative explanations, then
judge `survived | weakened | refuted`. It records the attempt in a new, separate artifact (the
**Refutation Record**), and the synthesis agent then transcribes only the confidence consequences
into the ledger. It never touches severity — mechanically enforced (§8, V3).

**Execution modes** (per `references/execution-modes-reference.md` + the two in-flow precedents,
`run-synthesis.md` §Step 2 "Single-agent vs. swarm" and §Evidence Spot-Check "Execution mode
considerations"):

- **Single-agent / sequential:** the pass runs inline after Step 6, in the same context. The
  manuscript is already loaded; cost is targeted re-reads + the record (~2–5K tokens per finding,
  ~30–75K at the cap — same order as the spot-check's disclosed overhead).
- **Hybrid / swarm:** dispatch a dedicated **disconfirmation subagent** that receives the locked
  Findings Ledger (mechanism + severity + `evidence_refs`/`evidence_quote` per finding), the
  manuscript snapshot path, and the prompt contract in §6 — and writes the Refutation Record. This
  is the stronger form (architectural isolation: the refuter is not the author of the findings —
  the same "writer cannot verify its own claims" principle the spot-check §Design principle states).
  Recommended whenever the run is already hybrid/swarm; the subagent's input deliberately
  **excludes** the letter draft and each finding's confidence token (anti-anchoring, §6).

## 4. The Refutation Record (new artifact + schema)

**Artifact:** `[Project]_Refutation_Record_[runlabel].md` in the run folder (narrow name — the
`*_Refutation_Record_*` token can't be satisfied by a lookalike, per the `*_Revision_Calendar_*`
glob lesson in `AGENTS.md` §Review practices). Prose-first (author-auditable rationale per
attempt), with one machine-parseable block per finding in the established
`<!-- apodictic:<type> { ... } -->` envelope family (`findings-ledger-format.md` §Companion
structured blocks), validated by the same stdlib subset-schema helper (`apodictic_artifacts.py`).

**Schema:** `plugins/apodictic/schemas/apodictic.refutation.v1.schema.json` (single-sourced —
schemas resolve from either script dir and don't need mirroring, per `AGENTS.md` §Platform parity):

```json
{
  "schema": "apodictic.refutation.v1",
  "id": "F-P5-01",
  "attempted": true,
  "outcome": "survived",
  "counter_evidence_quotes": ["\"I am very angry,\" she said calmly."],
  "alternative_explanations": ["Flat affect may be the POV character's established dissociation register (Ch. 2, Ch. 9)."],
  "rationale": "Why the outcome, arguing FROM the quotes; names what evidence would have refuted and whether it was found.",
  "confidence_after": "HIGH",
  "snapshot_path": "[Project]_Manuscript_Snapshot_[runlabel].md",
  "snapshot_sha256": "…64 lowercase hex…"
}
```

Required: `schema` (const), `id` (same `^F-[A-Za-z0-9]+-[0-9]{2,}$` pattern as
`apodictic.finding.v1`; must resolve to a locked ledger finding), `attempted` (boolean, explicit),
`outcome` (enum `survived | weakened | refuted`), `counter_evidence_quotes` (array, **minItems 1**,
each a **verbatim, single-line** manuscript-snapshot substring — see V2), `alternative_explanations`
(array, **minItems 1** — the pass must consider at least one rival reading; this is the second
anti-restate tooth), `rationale` (string), `confidence_after` (enum HIGH | MEDIUM | LOW |
UNCERTAIN), `snapshot_path` (string — the intake-snapshot filename the quotes were verified
against) + `snapshot_sha256` (string, `^[0-9a-f]{64}$` — the same binding-field pair
`apodictic.annotation.v1` carries), so V2 can assert **record-vs-snapshot identity** (the quotes
were checked against *these* bytes, not some other draft — see V2). **There is no `severity`
property, by design** — see V3.

One **budget block** per record (`apodictic.refutation_budget.v1`, schema file
`plugins/apodictic/schemas/apodictic.refutation_budget.v1.schema.json` — same single-sourced
location as the finding schema): fields `schema` (const `apodictic.refutation_budget.v1`), `cap`
(integer), `eligible` (integer), `processed` (integer), `bound` (boolean) — **all required**. It is
the mechanical basis for cap-bound disclosure (§5). Its schema-coverage binding row, alongside
`apodictic.refutation.v1`'s, is pinned in §8 Wiring.

**Deliberately a separate artifact, not new fields on the ledger blocks** (a correction to the
stub, which said "ledger sidecar"): write-scope isolation is what makes V3 mechanical. The pass's
entire write surface is this one artifact; the ledger's locked blocks are only touched by the
synthesis agent's transcription step, whose legal delta is exactly `confidence` (cross-checked by
V3). `Diagnostic_State.meta.json` mirroring of outcomes is **out of M1** (the record is the source
of truth; a sidecar `findings[].refutation_outcome` mirror can ride spec 03's consumer work later).

## 5. Scope & cost bounds

**Eligible set (bounded by construction):** locked, synthesis-bound findings where
`severity == Must-Fix` (any confidence) **or** (`severity == Should-Fix` **and**
`confidence == HIGH` at lock). Could-Fix and MEDIUM/LOW Should-Fix are out (non-goal §10). Findings
carrying a spec-03 `declined`/`deferred` disposition are skipped (the author already ruled; don't
spend budget re-litigating) — noted in the record's prose, not counted against the cap.

**Cap:** **15 findings per run**, processed Must-Fix first (ledger order), then HIGH Should-Fix
(ledger order). The Must-Fix ceiling is 10 (`output-policy.md` §Output Constraints), so **every
Must-Fix is always processed** — the cap can only ever bind on HIGH Should-Fix.

**When the cap binds — disclose, never silently skip:**
- The budget block records `bound: true`, `eligible`, `processed`.
- Each unprocessed HIGH Should-Fix keeps its HIGH **only** with a near-finding marker
  `<!-- refutation: not-attempted-budget F-<ORIGIN>-<NN> -->` in the letter body plus an Appendix B
  narrative line, and its author-facing confidence language must say *convergence-only, not
  stress-tested* (two grades of HIGH, visibly distinct — §7).
- V1 honors the marker **only when the recomputed budget actually binds** — the eligible set
  recomputed from the locked ledger exceeds the cap — AND the budget block says `bound: true` AND
  the marked id has no record (a marker on a processed finding, under an unbound budget, or under
  a `bound: true` the ledger recompute does not corroborate, is an ERROR — the marker is a
  disclosure, not an exemption you can reach for; the block's `bound` is a claim to verify, never
  an input — see the §8 as-built correction). Marker detection reuses the hardened
  boundary-matched, code-span-stripping helper discipline (`override_marker.py`; meta-lint M5
  class, `docs/validator-conventions.md`).

**Cost per mode:** single-agent ≈ 2–5K tokens/finding (targeted re-reads; manuscript in context) →
30–75K worst case; hybrid/swarm ≈ one subagent turn-set sized like a spot-check dispatch, plus the
record write. Zero cost when the eligible set is empty (record still written with an empty budget
block `eligible: 0` — absence-vs-skip stays distinguishable). **Implementation note:** the 30–75K
estimate assumes **snippet-scoped re-reads** (~2–5K/finding — the finding's `evidence_refs`
neighborhoods plus targeted counter-evidence hunts), *not* full-manuscript re-reads per finding; a
build that re-reads the whole manuscript for each finding has blown this bound by design, not by
overrun.

## 6. Prompt-design requirements (the disconfirmation pass contract)

The pass is a **finding killer, not a finding restater**. Normative requirements for the Step 6b
prose (and the subagent dispatch packet in hybrid/swarm):

1. **Adversarial stance, stated as the goal.** The pass's job is to *refute* the finding: "argue
   that this diagnosis is wrong, overstated, or better explained by something else — against the
   text." Success is a kill or a weakening; a survival must be *earned*, not defaulted. ("Kill"
   here means **demote, never delete**: a refuted finding ships at its locked severity with
   LOW/UNCERTAIN confidence — it is never removed from the letter; §7.)
2. **Quote-first ordering (hunt-then-judge).** Gather candidate counter-evidence spans from the
   manuscript **before** writing the outcome — the disconfirmation mirror of the stress test's
   lock-then-test discipline. An outcome written before the quotes exist is malformed.
3. **Counter-evidence, not the finding's evidence.** The pass receives the finding's `mechanism`,
   `severity`, `evidence_refs`, and `evidence_quote` — and must hunt spans that *contradict* the
   mechanism (the pressure-tested beat the pass missed, the scene where the arc does move, the
   qualifier the argument does state). Re-quoting the finding's own evidence is not an attempt.
4. **Alternative explanations are mandatory** (schema minItems 1): intentional craft choice, genre
   convention (`genre-*.md` calibration), POV/register design, evidence elsewhere in the text. A
   bare "could be intentional" without a quote or a named textual basis does not count — each
   alternative must point at text or at a contract/intent statement. **Mechanical floor (cheap V2
   heuristic):** each `alternative_explanations` entry must contain a quote mark, a `Ch.`/`p.`
   locator, or a contract-artifact reference → WARN if none. Deeper grounding — does the
   alternative actually engage the mechanism, or just gesture? — is **prompt-side**, audited by the
   rubber-stamp eval fixture (§12), not by a validator.
5. **Anchoring blinds.** The pass is **not shown** the finding's confidence token, the lens-verdict
   convergence count, or the letter draft. It judges the mechanism against the text, not against
   how sure the system already was.
6. **Strict outcome semantics (anti-performative-humility):**
   - `refuted` requires counter-evidence that the **mechanism does not operate** — "mechanism"
     meaning the finding's `mechanism` field, the one-sentence causal claim of what produces the
     problem (`findings-ledger-format.md` §Fields: "the craft mechanism that produces the
     problem"); the counter-evidence must contradict *that causal claim* — not show that the book
     has compensating strengths, and not that the author probably meant it.
   - "Author intent" alone never refutes: intent questions route to the existing Intent Check Loop
     (Step 1) and author verification; the record may say *survived* with an intent note.
   - `weakened` = the mechanism operates but the counter-evidence materially narrows its scope or
     force.
   - The `rationale` must name **what evidence would have refuted the finding and whether it was
     found** — a rubber stamp cannot answer that question honestly.
7. **Firewall** (`references/firewall.md`): the record contains quotes (manuscript bytes) and
   diagnosis-of-why — never fixes, never rewritten prose, never invented content. Naming a rival
   *reading* is diagnosis (allowed); scripting what the author should write instead is invention
   (forbidden).
8. **Author-facing language** (`output-policy.md` §Author-Facing Language): outcome tokens never
   appear raw in the letter body — "this diagnosis held up when we deliberately tried to knock it
   down" / "a deliberate counter-check found evidence that cuts against this — quoted below."
9. **Confidence transcription (synthesis agent, not the pass).** After the record is written and
   **before Step 7**, the synthesis agent transcribes each processed finding's `confidence_after`
   into that finding's locked ledger block (`apodictic.finding.v1` `confidence`), per the §7 caps
   table. This is the flow's only ledger write and it belongs to the transcriber — the pass never
   touches the ledger. V3 fails the run on any ledger-vs-record mismatch. Note the enforcement
   posture: V3 is a **pre-delivery fail-the-run gate, not a write-prevention mechanism** — nothing
   physically stops a bad transcription from being written; the run just cannot ship with one.

## 7. Confidence re-map & letter integration

**The new meaning of HIGH (edit to `output-policy.md` §Confidence Calibration):** for
synthesis-bound Must-Fix and HIGH-candidate findings, HIGH requires the existing bar (2+ passes or
unambiguous textual proof) **and** a recorded refutation attempt with `outcome == survived`.
Survival is a **necessary condition for HIGH, never a confidence-raising event**: a `survived`
outcome leaves confidence exactly where the ledger already had it — the pass can only lower or
hold, never lift (re-map table below). Convergence still *feeds* confidence
(`output-policy.md:106` unchanged) — it is no longer *sufficient* for HIGH. Update the §Author-Facing Language example
(`output-policy.md:19`): ✅ becomes "All three evaluative lenses agree on this point, and the
diagnosis survived a deliberate attempt to refute it against the text."

**Re-map rules (transcribed by the synthesis agent from `confidence_after`, enforced by V3):**

| Outcome | Confidence consequence |
|---|---|
| `survived` | Unchanged (survival is **necessary for HIGH, never sufficient** — the pass may never *raise* confidence; `confidence_after` must equal the ledger's current value) |
| `weakened` | Capped at MEDIUM |
| `refuted` | LOW; or UNCERTAIN when the counter-evidence supports a rival interpretation rather than negating the mechanism (conflicting signals, per the existing UNCERTAIN semantics) |

**Severity is never remapped** — a refuted Must-Fix is still a locked Must-Fix (V3 + Deficit Lock).

**How outcomes appear in the letter:**

- **Survived:** no body change beyond the honest HIGH language; the finding now carries earned
  confidence.
- **Weakened:** delivered at locked severity, MEDIUM confidence, with the strongest counter-evidence
  quoted inline near the finding (≤25 words per excerpt — the standing quote budget,
  `output-policy.md` §Output Constraints) so the author sees *why* it was weakened.
- **Refuted:** **not silently dropped** (the Deficit Lock forbids that, and rightly). Delivered at
  locked severity with LOW/UNCERTAIN confidence, framed per the existing rule ("never present LOW
  or UNCERTAIN findings as definitive diagnoses" — `output-policy.md:59`): the diagnosis, the
  counter-evidence quote, and an explicit author-verification ask. If the synthesis judges a
  refuted finding shouldn't ship at its locked tier at all, that is exactly the existing ID-scoped
  `<!-- override: softness-downgrade F-… -->` + Appendix B path — a legible human-auditable act,
  never this pass's write.
- **Appendix B (Severity Calibration)** gains a compact **Refutation Summary**: per processed
  finding — id, outcome, pointer to the record. One line per finding, format template:
  `- F-<ORIGIN>-<NN> — <survived|weakened|refuted> — <one-clause reason> (record:
  [Project]_Refutation_Record_[runlabel].md)`. (Appendix B already summarizes the adversarial
  self-check; this is its refutation sibling. `decision-layer-check` validates appendix *presence*,
  not content — no change to it.)
- **Cap-bound HIGHs:** marker + Appendix B disclosure per §5; body language says convergence-only.

## 8. Mechanical gates — three named validators

One new Python module `scripts/refutation_check.py` backing three new `validate.sh` arms, in the
established `honesty_check.py` delegation pattern (bash arm delegates to python3; **no-python3
degrade = WARN + exit 0 advisory**, matching `softness-check` — the verbatim-quote check is exactly
the "bash-validator capability ceiling" class that `ROADMAP.md:563` says belongs in a Python module,
so the bash side stays a thin dispatcher).

**V1 — `refutation-coverage`** (`<editorial_letter> <findings_ledger> <refutation_record>`):
*no HIGH without survived refutation.*
- Every synthesis-bound ledger finding carrying `confidence: HIGH` must have a record block with
  `attempted: true && outcome == "survived"` — **or** a valid cap-bound disclosure marker (honored
  only when the budget **recomputes** as binding — as-built correction below — under `bound: true`,
  id-not-processed; else ERROR).
- Every Must-Fix (any confidence) must have a record block (Must-Fix always fits under the cap).
- Every record `id` must resolve to a locked ledger finding (dangling record = ERROR).

**V2 — `refutation-evidence`** (`<refutation_record> <manuscript_snapshot>`):
*attempts without quote-anchored counter-evidence don't count.*
- Every record needs `counter_evidence_quotes` minItems 1 and `alternative_explanations`
  minItems 1; violation voids the attempt (which cascades into a V1 failure for a HIGH).
- Each quote must occur **verbatim** in the intake manuscript snapshot
  (`*_Manuscript_Snapshot_*`), checked against the as-is snapshot bytes, and be **single-line**
  (no `\n`/bare `\r`) — the same locator semantics the A6 quote-integrity gate proved out
  (`docs/annotated-manuscript.md` §A6; share/lift the check from the `annotation_manifest.py` /
  `apodictic_artifacts.py` surface rather than re-implementing). **Honest divergence from A6,
  stated here because the reuse claim must not overclaim:** A6 additionally requires *uniqueness*
  and *offset pinning* because it anchors a margin note to one span; a counter-evidence quote is
  evidence, not an anchor — a span occurring three times is still real counter-evidence — so V2
  requires verbatim presence (`count >= 1`) + single-line only. A fabricated quote (count 0) is an
  ERROR — the anti-rubber-stamp tooth: you cannot claim an attempt without touching real text.
- Quote length > 25 words → WARN (quote-budget hygiene, not a hard fail). **WARN semantics, stated
  once for all V2 warns:** advisory and non-blocking per the standing `validate.sh` convention —
  the arm reports and still exits 0; only ERRORs fail the run. The 25-word budget applies to
  `counter_evidence_quotes` entries only, **not** to `alternative_explanations` (those are
  rationale prose, not quote fields — the letter's own inline excerpts remain governed by
  `output-policy.md` §Output Constraints as always).
- Each `alternative_explanations` entry must contain a quote mark, a `Ch.`/`p.` locator, or a
  contract-artifact reference → WARN if none (the §6.4 grounding floor; deeper grounding is
  prompt-side, audited by the §12 rubber-stamp fixture).
- **Snapshot handling — split by what the flow actually requires.** Verified: the intake snapshot
  is **mandatory for core-de/full-de runs** (`run-core.md` §Intake Protocol → Step 1: "Persist the
  manuscript snapshot (core-de / full-de runs)"; skipped by design only for partial-de/fragment-de)
  and `run-synthesis.md` §"No snapshot?" repeats it ("it shouldn't [be missing], for core/full-de").
  So:
  - **Core-de/full-de — ERROR (option a).** The Step 10 invocation passes `--require-snapshot`
    whenever the run wrote a `*_Core_DE_Synthesis_*`/`*_Full_DE_Synthesis_*` letter (the same
    run-shape detection the annotated-manuscript offer uses — `run-synthesis.md` §Annotated
    Manuscript + Crosslinked Letter, "Offer it" paragraph); under the
    flag, snapshot missing = **ERROR** — a missing snapshot on these runs is a broken intake, not a
    degrade case.
  - **Elsewhere — WARN but demotions VOID (option b):** legacy folders and ad-hoc invocations
    without the flag get a WARN, **and every demotion in the record is void** — outcomes
    `weakened`/`refuted` may NOT be transcribed into the ledger without verified quotes: confidence
    stays unchanged, plus a mandatory letter disclosure line ("counter-evidence quotes unverified —
    no intake snapshot; demotions withheld"). Never a silent pass, never an unverifiable demotion.
    Mechanically: the void rule binds the §6.9 transcription step; V3 skips its
    `confidence_after`-equality assertion for voided records (the expected ledger≠record delta *is*
    the withheld demotion, re-derived from the record's `snapshot_path` resolved beside the
    record). Stated honestly: full write-prevention isn't claimable off the golden path without a
    pre-pass ledger copy — which is exactly why (a) is the in-flow default; core-de/full-de runs
    always have the snapshot.
  - **Record-vs-snapshot identity:** each record block's `snapshot_path`/`snapshot_sha256` must
    match the snapshot file actually on disk (as-is bytes, hashed); mismatch = **ERROR** — the
    record was written against different bytes (the stale-`sha256` loud-fail class the intake note
    in `run-core.md` establishes for annotation manifests).
- Budget-block consistency: `processed == min(eligible, cap)`, `bound == (eligible > processed)`,
  every marker-carrying id absent from the record; `cap` equals the §5 spec constant 15, and
  `processed` equals the count of schema-valid refutation blocks in the record (as-built
  correction: blocking ERRORs, promoted from WARN).

**V3 — `refutation-write-scope`** (`<findings_ledger> <refutation_record>`):
*the pass may write only `refutation.*` + confidence; any severity write fails the run.*
- Schema-clean records only; a `severity` key — or any canonical severity token
  (`Must-Fix|Should-Fix|Could-Fix`) used as a field value — inside an `apodictic:refutation` block
  is an ERROR. (The schema omits the property; V3 enforces it against the subset checker's
  tolerance for unknown keys.)
- For every processed id: ledger `confidence` == record `confidence_after`, and `confidence_after`
  obeys the outcome caps table (§7). Mismatch = ERROR (except records V2 voided for a missing
  snapshot in the no-flag case — §V2 snapshot handling — where the equality assertion is skipped
  because the withheld demotion is the *correct* state). V3 is a **pre-delivery fail-the-run gate,
  not a write-prevention mechanism**: it cannot stop a bad transcription from being written, it
  stops the run from shipping with one — the same posture as deficit-lock/softness-check.
- **Division of labor, stated so the claim stays honest:** V3 proves the *record* carries no
  severity channel and the confidence transcription is exact; "the letter cannot deliver below the
  locked severity" remains owned by the existing `deficit-lock` + `softness-check` pair
  (`output-policy.md` §Deficit Lock), which this pass runs entirely downstream of. Together the two
  layers make severity untouchable by mechanism, not convention. V3 does not duplicate
  softness-check (the same no-duplication note softness-check itself carries for severity-floor).

**As-built correction (WARN → ERROR promotion; Codex P1 on the build PR #161,
discussion_r3512685648):** the budget cross-checks originally shipped as advisory WARNs and the
cap-bound exemption trusted the block's `bound: true` — so a fabricated budget block
(`bound: true` plus invented `eligible`/`processed`) could ship an untested HIGH as "cap-bound"
with zero real refutation work, bypassing the HIGH-means-survived gate. Corrected at build time
to **recompute, don't trust** (the recorded-field rule applied to an exemption gate):

- **V1** recomputes `eligible` from the locked ledger (Must-Fix ∪ HIGH Should-Fix, dispositions
  excluded) and derives `bound` from that recompute vs the cap — mismatch on either is a blocking
  ERROR, and the disclosure marker is honored **only when the recomputed budget actually binds**;
  a marker riding a `bound: true` the recompute does not corroborate is an ERROR naming the
  finding.
- **V2** pins `processed` to the count of schema-valid refutation blocks actually in the record —
  mismatch is a blocking ERROR (promoted from WARN; a processed count with no blocks behind it is
  fabricated work).
- **Both arms** pin `cap` to the §5 spec constant 15 — a lowered cap manufactures a "binding"
  budget, the same fabrication class as a lied `bound: true`.

The `--check-all` hostile arm 4 (fabricated budget: invented `bound:true/eligible:16/processed:15`
plus a disclosure marker on an untested HIGH) locks the fail-closed behavior in CI.

**Wiring (all in the build PR):**
- Register all three arms in `AGG_VALIDATORS` (`validate.sh:181`) — the validator count is
  **derived** (`AGG_COUNT`, line 183); no count literal anywhere.
- Add the three checks + a `refutation_record` artifact key to the `run_spot_check` entry in
  `schemas/execution-gates.v1.json` (same shape as the existing `softness-check` check row), and
  cite them in the `run-synthesis.md` Step 10 check list next to the deficit-lock/softness bullets.
- Self-tests (`--self-test` per arm, aggregated by `--self-test-all`) per §12.
- **Dual script mirror:** `refutation_check.py` + the `validate.sh` edit land in both committed
  copies (`plugins/apodictic/scripts/` canonical, root `scripts/` CI), synced by hand as the last
  step, verified by `validate.sh check-mirror` then `--check-all` (`AGENTS.md` §Platform parity).
- Register both schemas in the `schema-coverage` binding table
  (`plugins/apodictic/schemas/_coverage.json` `bindings[]`) so the coverage gate stays green —
  exact rows:

  ```json
  {"schema": "apodictic.refutation.v1", "validators": ["refutation-coverage", "refutation-evidence", "refutation-write-scope"], "canonical_gate": "example-run-folder", "closed_keys": false},
  {"schema": "apodictic.refutation_budget.v1", "validators": ["refutation-coverage", "refutation-evidence"], "canonical_gate": "example-run-folder", "closed_keys": true}
  ```

  `canonical_gate` is the §12 extended `example-run-folder` fixture (same dirname-token shape as
  `apodictic.gate_event.v1`'s row). `closed_keys: false` on `refutation.v1` because the
  severity-key kill is V3's, enforced against the subset checker's unknown-key tolerance (above);
  `closed_keys: true` on the budget block (fixed five-field set — the misspelled-field kill is
  free there).
- `changelog.d/finding-disconfirmation.md` fragment (never edit `changelog.md`).

## 9. Repo-norm compliance summary

- **Firewall:** quotes are manuscript bytes, rationale is diagnosis; no fixes, no invented content
  (§6.7). The record's only "creative" field is `alternative_explanations`, which names rival
  *readings* — diagnosis-class, explicitly allowed by `firewall.md` ("naming a need is not
  inventing content").
- **Confidence/severity split** (`output-policy.md:102–106`) **preserved mechanically:** severity
  channel absent from the schema + V3 token guard + Deficit Lock ordering (pass runs post-lock) +
  softness-check downstream. "A real problem with thin evidence keeps its severity and loses
  confidence, never the reverse" — this pass is that rule's refutation-side enforcement.
- **Dual script mirror + bash ceiling:** §8 Wiring; Python module owns the logic, bash arms
  degrade to advisory WARN without python3.
- **Status drift:** build PR flips this spec's Status + carries the `built-when` marker.
- **Author-facing language:** §6.8, §7.

## 10. Non-goals

- **Severity is untouchable by this pass** — enforced by schema + V3 + Deficit Lock, not by
  convention.
- **No second opinion on MEDIUM/LOW findings** (cost cap; they're already triaged lower and framed
  as needing corroboration/verification by the existing confidence guidelines).
- **Not a replacement for the Evidence Spot-Check** — the spot-check verifies the letter's own
  citations exist and match (confirmation); this pass hunts counter-evidence (disconfirmation).
  Both stay.
- **Not a truth benchmark.** ROADMAP §V1 stays open — this narrows the "convergence masquerading
  as verification" leak at synthesis time; it does not prove findings correct.
- **No pass re-runs, no new execution mode, no sidecar mirror in M1** (§4).

## 11. Failure modes if built badly — and the guards

Two symmetric failures, each with a named mechanical tooth plus a prompt-side guard:

- **(a) Self-agreeing rubber stamp** — a second pass that nods HIGH through. Mechanical: V2's
  verbatim-quote requirement (an attempt with no real manuscript spans is void, cascading to a V1
  failure); `alternative_explanations` minItems 1; the `rationale` must answer "what would have
  refuted this, and did you find it." Prompt-side: quote-first ordering, adversarial goal framing,
  anchoring blinds (§6.1/2/5). Behavioral: the rubber-stamp eval fixture (§12) fails a pass that
  can't kill a deliberately wrong finding.
- **(b) Performative humility** — demoting real findings to look rigorous, nuking the Deficit
  Lock's point. Mechanical: severity is out of reach (V3 + lock); confidence demotion requires a
  record whose quotes are real spans (V2) and whose outcome obeys the strict semantics (§6.6) — a
  "refuted" with quotes that don't negate the mechanism is visible in the record for `/spec-review`
  and Codex to attack, and the demotion-abuse eval fixture (§12) fails a pass that demotes a
  bulletproof finding. Prompt-side: `refuted` requires mechanism-negation, intent alone never
  refutes. Residual risk (an eloquent-but-specious refutation with real quotes) is judgment-class,
  not validator-class — that is exactly the prompt-design surface `/spec-review` must stress.

## 12. Fixtures & self-test plan

**Module self-tests** (`refutation_check.py --self-test`, wired into `--self-test-all` /
`--check-all`), hostile-fixture discipline per `AGENTS.md` §Review practices (including
malformed-but-valid JSON and wrong-shaped blocks):

1. Valid record, survived HIGH Must-Fix → all three arms PASS.
2. HIGH finding, no record, budget unbound → V1 ERROR (the headline gate).
3. HIGH finding, no record, genuinely binding budget (as-built: 16 eligible > cap 15, recomputed
   from the ledger) + `bound: true` + valid disclosure marker → V1 PASS-with-note; same marker
   with `bound: false` → ERROR; marker under a `bound: true` whose ledger recompute does NOT bind
   → ERROR naming the finding (the §8 as-built correction); fabricated `eligible` → ERROR;
   lowered `cap` → ERROR; marker on a *processed* id → ERROR.
4. Record with empty `counter_evidence_quotes` / empty `alternative_explanations` → V2 ERROR,
   attempt void.
5. Fabricated quote (absent from snapshot) → V2 ERROR; multi-line quote → V2 ERROR; 30-word quote
   → V2 WARN (advisory, exit 0); `snapshot_sha256` mismatch vs. on-disk snapshot → V2 ERROR;
   missing snapshot under `--require-snapshot` → V2 ERROR; missing snapshot without the flag →
   V2 WARN + demotions void + disclosure demanded (and V3 skips equality for the voided record);
   `alternative_explanations` entry with no quote mark / locator / contract reference → V2 WARN.
6. `severity` key (or severity token as value) in a refutation block → V3 ERROR.
7. `outcome: weakened` with ledger confidence still HIGH (transcription miss) → V3 ERROR;
   `refuted` with `confidence_after: HIGH` (cap violation) → V3 ERROR.
8. Dangling record id (no ledger finding) → V1 ERROR. Non-dict block payload → clean error, no
   crash (isinstance guards per `docs/validator-conventions.md` crash-on-malformed class).

**Behavioral evals** (`evals/` — the repo's ground-truth track; CI has no pytest, per `AGENTS.md`
§CI):

- **Rubber-stamp fixture:** a fixture manuscript + a deliberately wrong locked finding (e.g.
  "protagonist never acts under pressure" where a quotable line shows her doing exactly that). The
  pass must return `outcome != survived` with the disconfirming line among
  `counter_evidence_quotes`. A survived outcome fails the eval.
- **Demotion-abuse fixture:** a bulletproof locked finding (e.g. a timeline paradox where both
  contradicting lines are quotable — unambiguous textual proof). The pass must return `survived`;
  any weakened/refuted outcome fails the eval.
- **Budget fixture:** eligible set of 17 (10 Must-Fix + 7 HIGH Should-Fix) → 15 processed, 2
  marked + disclosed, letter language distinguishes the two HIGH grades.

**Canonical fixture:** extend the committed `--check-all` run-folder fixture
(`example-run-folder`) with a small Refutation Record so all three arms run against real fixture
bytes in CI, mirroring how softness-check/deficit-lock are exercised.

## 13. Build increments, sessions, PR shape

Builder carries the lean anchor-verify rule (grep before asserting; stop if absent); the full
preflight checklist is the reviewer's.

- **Session 1 — mechanics (inert, consumer-only):** schema(s), `refutation_check.py` + three
  arms + self-tests, `AGG_VALIDATORS` registration, schema-coverage row, canonical-fixture
  extension, hand-mirror + `check-mirror` + `--check-all` green. Inert-by-construction (nothing
  produces a record yet) — the same consumer-first landing the annotated-manuscript increments
  used.
- **Session 2 — flow wiring:** `run-synthesis.md` Step 6b (the pass contract, §5–§7 prose +
  mode-dispatch note) **including the explicit confidence-transcription step** (the synthesis agent
  transcribes `confidence_after` into each processed ledger block per the §7 caps table, before
  Step 7; V3 fails the run on mismatch — §6.9) + Step 10 check bullets; `execution-gates.v1.json`
  `run_spot_check` rows +
  `refutation_record` artifact key; `output-policy.md` §Confidence Calibration amendment +
  author-facing example + a one-line cross-pointer at §Canonical Severity Scale's lens-verdict
  bullet; `findings-ledger-format.md` companion-block pointer; changelog fragment; spec →
  `docs/finding-disconfirmation.md` with Status flip + `built-when` marker.
- **Session 3 — behavioral hardening:** the three eval fixtures; self-review against §11; Codex
  front-run hardening (first-pass-clean discipline — one build→PR→review→fix round per window).

**PR shape:** default **one PR** (`feat/finding-disconfirmation`), merge commit, version bump at
merge; Codex 5.5 gate applies (authored logic — not a docs-skip). Permitted split if a Codex window
forces it: **PR A** = session 1 (inert validators + fixtures, green alone), **PR B** = sessions
2–3 (wiring + evals). Never ship B before A.

## 14. Interactions (pinned, not open)

- **Stub 03 (declined-finding state):** declined/deferred findings are budget-exempt (§5). If 03
  slips, the exemption clause is inert prose — no hard dependency.
- **Stub 05-M1 (coverage disclosure):** independent; both edit `run-synthesis.md`, hence the
  sequencing, not a logic dependency. A coverage note disclosing degraded context makes V2's
  snapshot-anchored quotes *more* valuable, not less.
- **Stub 05-M2 (re-grounding):** BUILT as **step 9c** — re-grounding runs *after* Step 6b, not
  before it as this row once claimed (stale pre-rework text): it must follow the step-9b coverage
  manifest, which it updates (`docs/synthesis-regrounding.md` §M2.5a). The ordering costs Step 6b
  nothing — the pass reads the locked ledger + the intake manuscript snapshot, neither of which
  decays. No change to this spec's contracts.

## 15. Open Questions (operator)

1. **Should downstream consumers act on refutation outcomes in M1+1?** `/ready` verdict bands and
   the revision-coach Loop Dispatch could treat a refuted-LOW Must-Fix distinctly (e.g. a named
   caveat line, or deprioritized session planning) — the same consumer pattern spec 03 builds for
   dispositions. M1 deliberately stops at letter + Appendix B surfacing; wiring consumers changes
   verdict semantics and is an operator call, not a default.
