# Annotated-Manuscript Producer — wiring the deliverable into the run flow

**Status:** Proposed (unbuilt). Increments 1–3 of the [Annotated-Manuscript Deliverable](annotated-manuscript.md) shipped the **validators** — the annotation manifest + annotated copy + crosslinked letter, gated by A1–A6 / X1–X4. But **nothing in a real run generates those artifacts**: the deliverable is validator-only, proven on hand-built fixtures. This producer closes that gap so a real `/start` diagnosis ends with a marked-up manuscript + a crosslinked letter the writer can actually open. Two increments, **generation first** (maintainer decision 2026-06-17).

## The gap, named honestly

A development edit run (`/start` → contract → passes 0/1/2/5/8 → audits → synthesis) writes the editorial letter (`*_Core_DE_Synthesis_*.md`), the Findings Ledger, and the rolling state (`run-core.md` / `run-synthesis.md` / `output-structure.md`). But:

- **The manuscript is never persisted.** It is pasted into the conversation and read during intake; the run folder holds no copy (`run-core.md` §Phase 1). `evidence_refs` are *loci* (`["Chapter 9"]`), never linked to a line index.
- **No step invokes `annotation_manifest.py build` or `crosslink render`.** The snapshot, manifest, annotated copy, and crosslinked letter are never produced.

So Increments 1–3 are inert in production: the gates pass on the canonical `example-annotated-manuscript/` fixture, but a writer running `/start` gets a letter that *references* loci, not a marked-up manuscript. This producer is the unlock the deliverable's own spec has flagged as "consumer-only / inert until the producer lands."

## Producer Increment 1 — generation wiring (the unlock)

Make a real run produce the artifacts. Render-only, model-never-authors — the [manuscript-visualizations](../plugins/apodictic/skills/core-editor/references/manuscript-visualizations.md) precedent. Four touchpoints:

### 1a. Persist the manuscript at intake (the snapshot's owner)

The deliverable requires a frozen, LF-normalized **snapshot** as the fixed left-hand side for all anchoring + the no-mutation proof ([annotated-manuscript.md §Prerequisite](annotated-manuscript.md)). Today nothing creates it. Producer Increment 1 makes the **intake step own it**: when the orchestrator reads the manuscript (`run-core.md` §Phase 1, before the passes run), it writes `[Project]_Manuscript_Snapshot_[runlabel].md` to the run folder — line endings → LF, a trailing newline ensured, **no other transformation** — and records its line count. This both persists the manuscript *and* gives the deliverable its immutable reference.

- **Why before the passes:** the passes' `evidence_refs` and the Timeline's line ranges then index the same text the snapshot froze, so line numbers align (a one-line boundary difference is the existing W1 advisory, not an error).
- **Firewall:** the orchestrator **copies** the manuscript bytes (LF-normalized), never edits — the snapshot is a verbatim frozen reference. The `sha256` binding is computed later, at `build` time.
- **Optional-by-design:** a run where the writer declines the marked-up copy can skip the snapshot; `/annotate` then reports it's missing and offers to snapshot on the spot (re-reading the manuscript). The recommended path is the intake snapshot.

### 1b. The `/annotate` command (the generator)

A new **post-diagnosis** command produces the deliverable from artifacts that already exist. It is a pure consumer of the run folder:

1. Resolve the bound/active run folder (snapshot + Findings Ledger + editorial letter + optional `Timeline.md`).
2. `scripts/annotation_manifest.py build <run_folder>` → writes the annotation manifest + the annotated copy (anchors resolved from the ledger; comments are **verbatim** finding-field projections).
3. `scripts/validate.sh annotated-manuscript <run_folder>` → the **A1–A6** gate (the firewall, mechanical).
4. `scripts/crosslink.py render <run_folder>` → writes the crosslinked letter (back-links from the letter's `<!-- finding: F-… -->` markers to the manifest anchors).
5. `scripts/validate.sh crosslink <run_folder>` → the **X1–X4** gate.
6. Update the sidecar `next_action` and report the two deliverables (the annotated copy + the crosslinked letter), pointing the writer to the marked-up copy as the revision surface.

`/annotate` is **offered at the end of `/start`** (the letter already ends by pointing onward — add "run `/annotate` for the marked-up copy") and runs standalone on a bound project. It changes **no** core-flow gate and writes no diagnostic state beyond the `next_action` pointer — it consumes existing artifacts, exactly like `/audit` and the Structure-Map visualization. If a gate fails, `/annotate` reports the failure and writes nothing partial (the gates run *after* build; a failing build is a finding-hygiene problem surfaced, not a silent emit).

### 1c. Pin the letter's finding-marker form (so crosslink's parser matches)

The synthesis already cites each delivered finding's ID "in an HTML comment near the finding" (`run-synthesis.md` §Deficit Lock; the Step-10 `softness-check` / `finding-trace` gates read it), and the canonical example letter uses `<!-- finding: F-… -->`. But the *form* is unpinned, while `crosslink`'s `_FINDING_MARKER_RE` parses exactly `<!-- finding: F-… -->`. Producer Increment 1 **pins** the synthesis to emit that canonical marker form for each delivered finding — a one-line clarification in `run-synthesis.md` (+ `output-policy.md`) — so the letter a run produces is crosslink-ready without a separate producer. (This is the whole crosslink "producer": the letter markers already exist; we only make their form canonical.)

### 1d. Registration (the command checklist)

`/annotate` is **registered, not script-mirrored** — command files are single-source in `plugins/apodictic/commands/`; the dual `scripts/` mirror is for `validate.sh` + `*.py` only (the Explore's claim that commands are mirrored to `scripts/` is wrong). The checklist:

- **`release-registry.json`** `commands[]` entry — `command` `/annotate`, `category` (`focused`), `status` (`first_class_shortcut`), `routerEquivalent` (`null`), a plain-language `writerQuestion`, and a `description`. `release-generate.mjs --check` regenerates the README / `marketplace.json` / `plugin.json` command lists from it (auto-discovered — no hand-edit of those).
- **`plugins/apodictic/commands/annotate.md`** — frontmatter (`description`, `argument-hint`, `allowed-tools`) + the procedure in §1b. The `description` must match the registry entry (independent files).
- **No intake-router change** — `/annotate` is post-run supplementary, not a `/start` route.

### Increment-1 gate

Increment 1 adds **no new validator** — it wires the existing generators + gates into a command. The deliverable's `--check-all` fixture already proves the generated artifact shapes; the command registration is gated by `release-generate.mjs --check`, and the generators by their existing self-tests. The Increment-1 "build review" should run `/annotate`'s procedure end-to-end against the canonical example run folder (extended with a snapshot + ledger + letter) and confirm the produced manifest/annotated/crosslinked artifacts pass `annotated-manuscript` + `crosslink`.

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

**Producer Increment 1 (In):** the intake snapshot step (`run-core.md`); the `/annotate` command + registration; the synthesis marker-form pin; the generation→gate chain. **Effect: Increments 1–3 produce real artifacts in a run.**

**Producer Increment 2 (In):** Pass 5 `evidence_quote` attachment + the `findings-ledger-format.md` discipline subsection. **Effect: the quote rung lights up for Pass-5 findings.**

**Not in:** auto-generation *inside* synthesis (Increment 1 keeps `/annotate` explicit/user-invoked — auto-emit is a trivial follow-on once the explicit path is trusted); `evidence_quote` across all passes (demand-gated, per-pass after the pilot); DOCX / Google-Docs export; round-trip re-anchoring.

## Open question for the build (flag for spec-review)

The cleanest way to **gate Increment 1** is unsettled: a command's procedure is prose (model-executed), so there's no `validate.sh` unit-test for "`/annotate` produced the right artifacts." Options: (a) rely on the existing generator self-tests + the `--check-all` fixture (the artifacts' shapes are gated; the *wiring* is not); (b) add a tiny `annotate-selftest`-style harness that runs the build→gate chain over a fixture run folder and asserts exit 0; (c) treat it as eval-tracked like other prompt behavior. Lean (a)+(b): keep the prose command thin, and add a `--check-all` step that runs the full build→annotated-manuscript→crosslink chain over a committed example **run folder** (snapshot + ledger + letter), proving the chain end-to-end on canonical inputs.
