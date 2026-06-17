# Annotated-Manuscript Producer — wiring the deliverable into the run flow

**Status:** Proposed (unbuilt). Increments 1–3 of the [Annotated-Manuscript Deliverable](annotated-manuscript.md) shipped the **validators** — the annotation manifest + annotated copy + crosslinked letter, gated by A1–A6 / X1–X4. But **nothing in a real run generates those artifacts**: the deliverable is validator-only, proven on hand-built fixtures. This producer closes that gap so a real `/start` diagnosis ends with a marked-up manuscript + a crosslinked letter the writer can actually open. Two increments, **generation first** (maintainer decision 2026-06-17).

## The gap, named honestly

A development edit run (`/start` → contract → passes 0/1/2/5/8 → audits → synthesis) writes the editorial letter (`*_Core_DE_Synthesis_*.md`), the Findings Ledger, and the rolling state (`run-core.md` / `run-synthesis.md` / `output-structure.md`). But:

- **The manuscript is never persisted.** It is pasted into the conversation and read during intake; the run folder holds no copy (`run-core.md` §Phase 1). `evidence_refs` are *loci* (`["Chapter 9"]`), never linked to a line index.
- **No step invokes `annotation_manifest.py build` or `crosslink render`.** The snapshot, manifest, annotated copy, and crosslinked letter are never produced.

So Increments 1–3 are inert in production: the gates pass on the canonical `example-annotated-manuscript/` fixture, but a writer running `/start` gets a letter that *references* loci, not a marked-up manuscript. This producer is the unlock the deliverable's own spec has flagged as "consumer-only / inert until the producer lands."

## Producer Increment 1 — generation wiring (the unlock)

Make a real run produce the artifacts — **as part of the deliverable, offered in-flow, not behind a command.** Render-only, model-never-authors (the [manuscript-visualizations](../plugins/apodictic/skills/core-editor/references/manuscript-visualizations.md) precedent). Five touchpoints — §1a snapshot at intake, §1b the run-end offer + generation chain, §1c the explicit re-gen affordance, §1d the marker-form pin, §1e (registration, which evaporates):

### 1a. Persist the manuscript at intake (the snapshot's owner)

The deliverable requires a frozen, LF-normalized **snapshot** as the fixed left-hand side for all anchoring + the no-mutation proof ([annotated-manuscript.md §Prerequisite](annotated-manuscript.md)). Today nothing creates it. Producer Increment 1 makes the **intake step own it**: when the orchestrator reads the manuscript (`run-core.md` → "## Intake Protocol (Always Run) → Step 1: Read manuscript"), it writes `[Project]_Manuscript_Snapshot_[runlabel].md` to the run folder — line endings → LF, a trailing newline ensured, **no other transformation** — and records its line count. This both persists the manuscript *and* gives the deliverable its immutable reference.

- **What the snapshot actually buys (don't oversell line-range).** The `line-range` rung fires *only* when an `evidence_refs` token exactly equals a `Timeline.md` scene-id — and the Timeline is a **Pass 10 (Full-DE) artifact**, absent from the default Core baseline (Passes 0/1/2/5/8). Passes never emit raw line numbers; they emit loci (`"Chapter 9"`, `"Ch 1 §1"`). So for a normal Core `/start` run **there is no Timeline and every anchor is chapter / section / document** — *this is expected, not a degradation.* The snapshot-at-intake ordering therefore buys **chapter/section heading alignment** (the heading text the snapshot froze is what the passes reference) — robust to a trailing-newline shift. The line-range rung lights up only on Full-DE runs that produced a Timeline; the producer doesn't change that.
- **Firewall — manuscript→snapshot fidelity is *trust*, not proof.** A2 proves snapshot→annotated is non-mutating and the `sha256` binding proves manifest↔snapshot consistency, but **nothing mechanically proves the snapshot equals the manuscript the passes read** — the orchestrator (a model) does the LF-normalizing copy via prose instruction. This is acceptable for a chapter/section deliverable (a chapter heading survives paste-concatenation), but must be stated, not hidden. Concretely: the snapshot is taken **once at intake, from the same assembled manuscript the contract step already holds** (so a manuscript pasted across several messages, or supplied as a file path, is snapshotted as the *assembled* text the contract was drafted against — not raw message fragments); a **mid-run manuscript revision** requires a new runlabel + a fresh snapshot (the stale-sha rule then fails an old manifest loudly).
- **Conditioned on workflow.** The intake snapshot is taken **only for full-draft-edit runs** — the workflow where the marked-up copy is offered (§1b). **Quick-triage** and **fragment** runs skip it (they don't offer the deliverable). If the author later wants it for one of those runs, the re-gen affordance (§1c) snapshots **on demand**: a `fragment-de` run is snapshotted **as-is** (the snapshot *is* the line index for whatever was supplied; chapter/document anchoring only, no Timeline), and a quick-triage run re-reads its manuscript. Taking the snapshot at *intake* (not run-end) matters for the full-draft path because the manuscript is reliably in context then — after many passes / subagents a long run's context may be compacted, so run-end re-reading is less reliable.

### 1b. Offer the deliverable at run-end (the primary path — *not* a command)

The marked-up manuscript + crosslinked letter should arrive **with the edit**, because they *are* the deliverable (the #1 thing a human DE hands back) — not behind a command the author must discover, remember, and invoke (which would leave the #1 deliverable undiscovered, i.e. the feature inert even after it ships). But a marked-up copy is **not always wanted** (a quick triage doesn't need one), so generation is **offered, conditioned on workflow, and the author is asked** (maintainer decision, 2026-06-17). At the end of a **full-draft-edit** run (the synthesis/output stage, after the letter is written), the orchestrator asks: *"Want your manuscript marked up — each finding in the margin — plus the letter crosslinked to it?"* On the author's **yes**, it runs the generation chain over the run folder (a pure consumer of artifacts that already exist):

1. Resolve the bound/active run folder (snapshot + Findings Ledger + editorial letter + optional `Timeline.md`).
2. `scripts/annotation_manifest.py build <run_folder>` → writes the annotation manifest + the annotated copy (anchors resolved from the ledger; comments are **verbatim** finding-field projections).
3. `scripts/validate.sh annotated-manuscript <run_folder>` → the **A1–A6** gate (the firewall, mechanical).
4. `scripts/crosslink.py render <run_folder>` → writes the crosslinked letter (back-links from the letter's `<!-- finding: F-… -->` markers to the manifest anchors).
5. `scripts/validate.sh crosslink <run_folder>` → the **X1–X4** gate.
6. Report the two deliverables (the annotated copy + the crosslinked letter), pointing the writer to the marked-up copy as the revision surface. Generation changes **no** core-flow gate and writes no diagnostic state beyond a **human-readable** pointer — *not* a new sidecar `next_action` enum value (`next_action` is an enumerated key set in `start.md`; generation runs after the `deliver` state, so inventing an enum value would break the lifecycle validators).

**Conditioning (maintainer's call, 2026-06-17):** the offer fires only for **full-draft-edit** runs; **quick-triage** and **fragment** runs do *not* offer it (a marked-up copy is less useful there). The offer is the **only** automatic surface — there is **no headline command**, so an author never has to discover one; the marked-up copy is part of the deliverable, generated in-flow and gated like any other artifact (the precedent is the post-synthesis rolling-state write, not a separate command).

**Ordering / failure semantics (honest):** `build` and `render` write their artifacts to the run folder **before** the gates verify them, so a gate failure leaves the (now-suspect) artifacts on disk. The orchestrator therefore reports *which* gate failed and that the artifacts are **unverified** — it must not present a gate-failing copy as clean. (A finding-hygiene error fails `build` *before* it writes anything; anchor / A2 / A6 / X-violations surface at the gate, after the files exist. The build is deterministic, so re-running after a fix overwrites cleanly.) **Legacy / no-marker letter:** if the editorial letter carries no `<!-- finding: F-… -->` markers, `crosslink render` produces zero back-links and the X1–X4 gate passes (0 back-links, at most a W1 advisory) — the deliverable is still the annotated copy + a no-op crosslinked letter, gracefully, rather than a failure.

### 1c. The explicit re-generation affordance (existing run folders)

The one legitimate case for an *explicit* invocation is **"annotate a run I didn't annotate"** — the author declined the offer at the time, or it's a **prior session's** run folder (or a run made before this producer shipped). This is a **thin secondary affordance, not a headline command**: it is surfaced through **`/start`'s existing state-driven dispatch** on a bound project — when `/start` resumes a project with a completed run that has a Findings Ledger + editorial letter but no annotated copy, it offers *"regenerate the marked-up copy from this run?"* and runs the §1b chain on **yes**. No new command, no `release-registry.json` `commands[]` entry, no `commandBaseSkills` mappings. If the run folder has **no snapshot** (a quick-triage run, or a pre-producer run), the re-gen re-reads the manuscript to snapshot on the spot before building; if the manuscript isn't available, it says so rather than guessing. (A standalone flag/command is possible but unnecessary given the dispatch hook already owns project re-entry.)

### 1d. Pin the letter's finding-marker form (so crosslink's parser matches)

The current instruction is genuinely **loose**: `output-policy.md §Deficit Lock` (the canonical rule; `run-synthesis.md` defers to it as "Canonical rule") says only "cite that ID **in an HTML comment** near the finding." `finding_trace.letter_cited_ids` matches that looseness (any `F-…` token inside any `<!-- … -->`), but `crosslink._FINDING_MARKER_RE` requires exactly `<!-- finding: F-… -->`. So a letter that writes `<!-- F-P5-01 -->` or `<!-- id: F-P5-01 -->` today satisfies `finding-trace` / `softness-check` / `deficit-lock` but yields **zero** crosslink back-links. Producer Increment 1 **pins** the canonical form `<!-- finding: F-… -->`:

- Pin it **in `output-policy.md §Deficit Lock`** (the authority), and have `run-synthesis.md` echo it. The strict form is a **subset** of the loose form `finding_trace` already accepts, so pinning it does **not** break `finding-trace` / the honesty gates.
- **Duplicate-back-link guard:** the Severity-Calibration appendix also cites finding ids in HTML comments (`apodictic:severity_calibration` blocks). The pin must require those to use a **different** comment form than `<!-- finding: F-… -->` (they do in the example — they're `apodictic:severity_calibration` blocks, not `finding:` markers), so a finding doesn't get a second, appendix-sourced back-link. State this explicitly so the build doesn't regress it.

This is the whole crosslink "producer": the letter markers already exist; we only make their form canonical and unambiguous.

### 1e. Registration — mostly evaporates (no new command)

Because the primary path is an **in-flow offer** (§1b) and the re-gen is a **`/start` dispatch action** (§1c), **there is no new command** — so the command-registration burden the spec-review flagged **does not apply**: no `plugins/apodictic/commands/annotate.md`, no `release-registry.json` `commands[]` entry, and **no `codex.commandBaseSkills` / `antigravity.commandBaseSkills` mappings** (the `build-codex` / `build-antigravity --self-check` gates that enforce those only fire for *registered commands*). This is the chief simplification of dropping the command: the two registration P0s the spec-review caught are gone.

Producer Increment 1 is therefore **prompt edits** (single-source in `plugins/`, no `scripts/` mirror — prose isn't mirrored): the intake snapshot step (`run-core.md`), the run-end offer + generation chain (`run-synthesis.md` / `output-structure.md`), the re-gen dispatch (`start.md`), the marker-form pin (`output-policy.md`, §1d) — **plus one mechanical change**, the `--check-all` chain gate (§Increment-1 gate), which *is* a `validate.sh` edit and so *is* mirrored.

### Increment-1 gate (resolved)

Increment 1 adds **no new validator** — it wires the existing generators + gates into the run-end offer + the `/start` re-gen dispatch. There is **no command**, so the command-registration gates don't apply (§1e); the generators are covered by their existing `--self-test`s.

The *wiring* (build→gate→render→gate) gets one new `--check-all` step that runs the full chain end-to-end on canonical inputs. **It must run `build` / `render` on a `mktemp` copy of the example run folder, never in place** — `annotation_manifest.py build` and `crosslink render` *write* `*_Annotation_Manifest_*.md` / `*_Annotated_Manuscript_*.md` / `*_Crosslinked_Letter_*.md`, so running in place would overwrite the committed fixtures every CI run (a dirty-tree, non-idempotent gate). This follows the existing gate-engine precedent in `validate.sh` (the only mutating run-folder arm already does `CA_TMP=$(mktemp -d); cp "$CA_RUNDIR"/* "$CA_TMP"/` "to keep the committed fixture immutable"). The chain copies the canonical `example-annotated-manuscript/` folder (snapshot + ledger + letter already present) to a temp dir, runs build → `annotated-manuscript` → crosslink render → `crosslink`, and asserts exit 0. Because `build` regenerates the committed outputs **byte-identically** (the committed manifest/annotated/crosslinked files are exactly what a fresh build emits — verified), the committed fixtures double as the expected outputs.

## Producer Increment 2 — `evidence_quote` pass-attachment (light up the quote rung)

Increment 1 produces the annotated copy, but the **`quote` rung stays dark** until a pass emits `evidence_quote` (the deliverable's Increment-2 is consumer-only). This increment pilots **one** pass — demand-gated, per-pass.

### 2a. The pilot pass

**Pass 5 (Character Audit)** is the cleanest first adopter — its findings frequently point at a specific beat/exchange, the most sentence-precise of the baseline passes (`run-core.md` §Pass 5). The pilot adds to Pass 5's spec: *when a finding cites a specific sentence or exchange, attach it verbatim as `evidence_quote` — a single-line substring **copied** from the manuscript snapshot, never composed; omit it for a chapter/arc-level finding.* No other pass adopts in the pilot.

### 2b. The discipline (where it's written)

`findings-ledger-format.md` gains a **"When to populate `evidence_quote`"** subsection:
- the **sentence-precision criterion** — populate only when the finding is about a specific line, not a chapter/arc;
- the **firewall** — copy the cited span **verbatim**; never author one. A6 enforces this *by identity* downstream: a non-verbatim or non-unique quote fails A6 and the anchor degrades to the line/chapter rung — so a pass physically cannot smuggle authored text;
- a worked example (a Pass-5 character beat).

The schema field already exists (`apodictic.finding.v1.evidence_quote`, optional); no schema change.

### 2c. Gate

No new mechanical gate: **A6** (the deliverable's quote-integrity gate) already enforces verbatim+unique downstream. The pilot's correctness — that a Pass-5 finding which *should* carry a quote does — is **behavioral**, tracked by the `evals/` fixtures, not a unit gate. The canonical `--check-all` fixture already proves the consumer (F-QT-01 with `evidence_quote` → quote anchor → A6 pass).

## Increment boundary

**Producer Increment 1 (In):** the intake snapshot step (`run-core.md`, full-draft only); the **run-end offer** + generation chain (`run-synthesis.md` / `output-structure.md`); the **explicit re-gen** via `/start` dispatch (`start.md`); the marker-form pin (`output-policy.md`); the `--check-all` chain gate. **No new command.** **Effect: a full-draft run offers, and produces on accept, the marked-up manuscript + crosslinked letter (deliverable Increments 1–3).**

**Producer Increment 2 (In):** Pass 5 `evidence_quote` attachment + the `findings-ledger-format.md` discipline subsection. **Effect: the quote rung lights up for Pass-5 findings.**

**Not in:** **unconditional** auto-generation (the offer is conditioned on full-draft workflow *and* asks the author — not silent/always-on; a quick-triage/fragment run isn't offered it); a standalone `/annotate` command (dropped — the in-flow offer + the `/start` re-gen dispatch cover it without a command); `evidence_quote` across all passes (demand-gated, per-pass after the pilot); DOCX / Google-Docs export; round-trip re-anchoring.

**Dependencies.** The producer wires in already-built generators: `annotation_manifest.py` (deliverable Increments 1–2, in `main`) and `crosslink.py` (Increment 3, in flight as PR #103). So the producer branch is based on the crosslinks branch and lands **after** #103 merges. Producer Inc 1 ships without Inc 2 (the quote rung simply stays dark); Inc 2 is independent (it lights up the rung whenever Inc 1's generation runs).

## Gating prose wiring (resolved by spec-review)

The offer + generation steps are prose (model-executed), so there is no `validate.sh` unit-test for "the orchestrator followed the steps." The resolution (see §Increment-1 gate): keep the prose **thin** and gate the **mechanical chain** it invokes — a `--check-all` step that runs build→gate→render→gate on a **temp copy** of the canonical run folder and asserts exit 0. That proves the generators + gates compose end-to-end on canonical inputs; the prose wiring (the model offering, then calling them in order) is eval-tracked like other command/prompt behavior, not unit-gated. Not pursued: a heavier dedicated harness (redundant with the `--check-all` chain).
