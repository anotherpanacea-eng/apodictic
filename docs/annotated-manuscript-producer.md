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

The deliverable requires a frozen, LF-normalized **snapshot** as the fixed left-hand side for all anchoring + the no-mutation proof ([annotated-manuscript.md §Prerequisite](annotated-manuscript.md)). Today nothing creates it. Producer Increment 1 makes the **intake step own it**: when the orchestrator reads the manuscript (`run-core.md` → "## Intake Protocol (Always Run) → Step 1: Read manuscript"), it writes `[Project]_Manuscript_Snapshot_[runlabel].md` to the run folder — line endings → LF, a trailing newline ensured, **no other transformation** — and records its line count. This both persists the manuscript *and* gives the deliverable its immutable reference.

- **What the snapshot actually buys (don't oversell line-range).** The `line-range` rung fires *only* when an `evidence_refs` token exactly equals a `Timeline.md` scene-id — and the Timeline is a **Pass 10 (Full-DE) artifact**, absent from the default Core baseline (Passes 0/1/2/5/8). Passes never emit raw line numbers; they emit loci (`"Chapter 9"`, `"Ch 1 §1"`). So for a normal Core `/start` run **there is no Timeline and every anchor is chapter / section / document** — *this is expected, not a degradation.* The snapshot-at-intake ordering therefore buys **chapter/section heading alignment** (the heading text the snapshot froze is what the passes reference) — robust to a trailing-newline shift. The line-range rung lights up only on Full-DE runs that produced a Timeline; the producer doesn't change that.
- **Firewall — manuscript→snapshot fidelity is *trust*, not proof.** A2 proves snapshot→annotated is non-mutating and the `sha256` binding proves manifest↔snapshot consistency, but **nothing mechanically proves the snapshot equals the manuscript the passes read** — the orchestrator (a model) does the LF-normalizing copy via prose instruction. This is acceptable for a chapter/section deliverable (a chapter heading survives paste-concatenation), but must be stated, not hidden. Concretely: the snapshot is taken **once at intake, from the same assembled manuscript the contract step already holds** (so a manuscript pasted across several messages, or supplied as a file path, is snapshotted as the *assembled* text the contract was drafted against — not raw message fragments); a **mid-run manuscript revision** requires a new runlabel + a fresh snapshot (the stale-sha rule then fails an old manifest loudly).
- **Partial / fragment runs.** `partial-de` / `fragment-de` runs snapshot the **supplied fragment as-is** — coherent because the snapshot *is* the line index for whatever was supplied; anchoring is chapter/document only (a fragment has no reliable global chapter numbering, and no Timeline). `/annotate` works the same way over the fragment's run folder.
- **Optional-by-design.** A run where the writer declines the marked-up copy can skip the snapshot; `/annotate` then reports it's missing and offers to snapshot on the spot (re-reading the manuscript). The recommended path is the intake snapshot.

### 1b. The `/annotate` command (the generator)

A new **post-diagnosis** command produces the deliverable from artifacts that already exist. It is a pure consumer of the run folder:

1. Resolve the bound/active run folder (snapshot + Findings Ledger + editorial letter + optional `Timeline.md`).
2. `scripts/annotation_manifest.py build <run_folder>` → writes the annotation manifest + the annotated copy (anchors resolved from the ledger; comments are **verbatim** finding-field projections).
3. `scripts/validate.sh annotated-manuscript <run_folder>` → the **A1–A6** gate (the firewall, mechanical).
4. `scripts/crosslink.py render <run_folder>` → writes the crosslinked letter (back-links from the letter's `<!-- finding: F-… -->` markers to the manifest anchors).
5. `scripts/validate.sh crosslink <run_folder>` → the **X1–X4** gate.
6. Report the two deliverables (the annotated copy + the crosslinked letter), pointing the writer to the marked-up copy as the revision surface. Write only a **human-readable next-step pointer**, *not* a new sidecar `next_action` enum value — `next_action` is an enumerated key set (`start.md`) with no `annotate` value, and `/annotate` is post-terminal (after `deliver`); inventing an enum value would break the lifecycle validators.

`/annotate` is **offered at the end of `/start`** (the letter already ends by pointing onward — add "run `/annotate` for the marked-up copy") and runs standalone on a bound project. It changes **no** core-flow gate and writes no diagnostic state — it consumes existing artifacts, exactly like `/audit` and the Structure-Map visualization.

**Ordering / failure semantics (honest):** `build` and `render` write their artifacts to the run folder **before** the gates verify them, so a gate failure leaves the (now-suspect) artifacts on disk. `/annotate` therefore reports *which* gate failed and that the artifacts are **unverified** — it must not present a gate-failing copy as clean. (A finding-hygiene error fails `build` *before* it writes anything; anchor / A2 / A6 / X-violations surface at the gate, after the files exist. The build is deterministic, so re-running after a fix overwrites cleanly.) **Legacy / no-marker letter:** if the editorial letter carries no `<!-- finding: F-… -->` markers (an older run), `crosslink render` produces zero back-links and the X1–X4 gate passes (0 back-links, at most a W1 advisory) — `/annotate` still delivers the annotated copy and a no-op crosslinked letter, gracefully, rather than failing.

### 1c. Pin the letter's finding-marker form (so crosslink's parser matches)

The current instruction is genuinely **loose**: `output-policy.md §Deficit Lock` (the canonical rule; `run-synthesis.md` defers to it as "Canonical rule") says only "cite that ID **in an HTML comment** near the finding." `finding_trace.letter_cited_ids` matches that looseness (any `F-…` token inside any `<!-- … -->`), but `crosslink._FINDING_MARKER_RE` requires exactly `<!-- finding: F-… -->`. So a letter that writes `<!-- F-P5-01 -->` or `<!-- id: F-P5-01 -->` today satisfies `finding-trace` / `softness-check` / `deficit-lock` but yields **zero** crosslink back-links. Producer Increment 1 **pins** the canonical form `<!-- finding: F-… -->`:

- Pin it **in `output-policy.md §Deficit Lock`** (the authority), and have `run-synthesis.md` echo it. The strict form is a **subset** of the loose form `finding_trace` already accepts, so pinning it does **not** break `finding-trace` / the honesty gates.
- **Duplicate-back-link guard:** the Severity-Calibration appendix also cites finding ids in HTML comments (`apodictic:severity_calibration` blocks). The pin must require those to use a **different** comment form than `<!-- finding: F-… -->` (they do in the example — they're `apodictic:severity_calibration` blocks, not `finding:` markers), so a finding doesn't get a second, appendix-sourced back-link. State this explicitly so the build doesn't regress it.

This is the whole crosslink "producer": the letter markers already exist; we only make their form canonical and unambiguous.

### 1d. Registration (the command checklist) — enforced by *two* CI gates, not one

`/annotate` is **registered, not script-mirrored** — command files are single-source in `plugins/apodictic/commands/`; the dual `scripts/` mirror is for `validate.sh` + `*.py` only. Registration is enforced by **two** CI steps; missing either breaks the build:

- **`release-generate.mjs --check`** syncs only the README grouped command list (by `writerQuestion`) and the `commands/audit.md` audit list from `release-registry.json`. It does **not** verify that a `commands[].command` has a matching `commands/<slug>.md`, and does **not** edit the `marketplace.json` / `plugin.json` command lists (those carry only the plugin `description`). *(An earlier draft wrongly said this gate enforces the command file and the marketplace/plugin lists.)*
- **`build-codex.mjs --self-check`** (and **`build-antigravity.mjs --self-check`**) is the gate that actually requires `commands/annotate.md` to exist (`mustExist`) **and** a base-skill mapping — it throws `Missing … commandBaseSkills mapping for command slug: annotate` unless `release-registry.json` carries **`codex.commandBaseSkills["annotate"]`** *and* **`antigravity.commandBaseSkills["annotate"]`**.

So the checklist is:
- **`release-registry.json`:** (a) a `commands[]` entry — `/annotate`, `category` `focused`, `status` `first_class_shortcut`, `routerEquivalent` `null`, a plain-language `writerQuestion`, a `description`; **and** (b) `codex.commandBaseSkills["annotate"] = "core-editor"` **and** `antigravity.commandBaseSkills["annotate"] = "core-editor"` (the base skill `start`/`ready` use).
- **`plugins/apodictic/commands/annotate.md`** — frontmatter (`description` matching the registry, `argument-hint`, `allowed-tools`) + the §1b procedure.
- **No intake-router / marketplace / plugin.json command-list change** — `/annotate` is post-run supplementary, not a `/start` route.

### Increment-1 gate (resolved)

Increment 1 adds **no new validator** — it wires the existing generators + gates into a command. Registration is gated by `release-generate.mjs --check` (README/audit-list sync) **and** `build-codex.mjs` / `build-antigravity.mjs --self-check` (the command file + `commandBaseSkills` mappings — see §1d); the generators are covered by their existing `--self-test`s.

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

**Producer Increment 1 (In):** the intake snapshot step (`run-core.md`); the `/annotate` command + registration; the synthesis marker-form pin; the generation→gate chain. **Effect: Increments 1–3 produce real artifacts in a run.**

**Producer Increment 2 (In):** Pass 5 `evidence_quote` attachment + the `findings-ledger-format.md` discipline subsection. **Effect: the quote rung lights up for Pass-5 findings.**

**Not in:** auto-generation *inside* synthesis (Increment 1 keeps `/annotate` explicit/user-invoked — auto-emit is a trivial follow-on once the explicit path is trusted); `evidence_quote` across all passes (demand-gated, per-pass after the pilot); DOCX / Google-Docs export; round-trip re-anchoring.

**Dependencies.** The producer wires in already-built generators: `annotation_manifest.py` (deliverable Increments 1–2, in `main`) and `crosslink.py` (Increment 3, in flight as PR #103). So the producer branch is based on the crosslinks branch and lands **after** #103 merges. Producer Inc 1 ships without Inc 2 (the quote rung simply stays dark); Inc 2 is independent (it lights up the rung whenever Inc 1's generation runs).

## Gating a prose command (resolved by spec-review)

A command's procedure is prose (model-executed), so there is no `validate.sh` unit-test for "`/annotate` followed its steps." The resolution (see §Increment-1 gate): keep the prose command **thin** and gate the **mechanical chain** it invokes — a `--check-all` step that runs build→gate→render→gate on a **temp copy** of the canonical run folder and asserts exit 0. That proves the generators + gates compose end-to-end on canonical inputs; the prose wiring (the model calling them in order) is eval-tracked like other command behavior, not unit-gated. Not pursued: a heavier `annotate-selftest` harness (redundant with the `--check-all` chain).
