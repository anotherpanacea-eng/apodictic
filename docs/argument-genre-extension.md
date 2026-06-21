# Argument-Engine Extension to Grant Proposals / Academic Papers / Pitch Decks — the genre layer

**Status:** **M1 (Increment 1 / genre layer) built** (this PR). Roadmap: `ROADMAP.md` → Horizon Capacities → Tier 2, item 11. Home doc: [`docs/nonfiction-pre-draft.md`](nonfiction-pre-draft.md) § The genre layer (Increment 5). Anchor engine: `scripts/argument_spine.py` (the Nonfiction Pre-Draft validator) + the Dialectical Clarity audit (`plugins/apodictic/skills/specialized-audits/references/craft/dialectical-clarity.md`) over the shared `Argument_State.md` artifact (`docs/argument-state-schema.md`). This is a **calibration extension on an existing engine, not new architecture** (the roadmap's own framing).
<!-- built-when: scripts/argument_spine.py contains "parse_genre_profiles" -->

> **Build record.** This doc is the on-repo home for the reviewed spec, with the spec-review findings folded into the text. The canonical status-drift marker lives on the home doc (`docs/nonfiction-pre-draft.md` § The genre layer); this doc carries a mirror marker so its own Status cannot silently drift. The original spec + findings were authored in `setec-scratch/apodictic-spec-wave/` (outside the repo and outside `check-status-drift.mjs`'s `docs/**/*.md` scan root — which is exactly why the enforcing marker had to move into `docs/`; see the folded P2 below).

---

## 1. Framing

The Nonfiction Argument Engine already diagnoses argument-shaped nonfiction across a dozen forms (op-ed, policy brief, testimony, academic article, grant proposal, white paper, legal brief, book review, open letter, crisis comms) — it classifies the form at Step 1, populates the shared `Argument_State.md`, and calibrates every downstream code by form and audience. What it did **not** yet do is hold a genre to its *genre-required argument structure*: a grant proposal is a near-contract with named, reviewer-scored sections (Specific Aims / Significance / Innovation / Approach); an academic paper must stake a *contribution claim* and *position it against related work*; a pitch deck must run the problem → solution → traction narrative or the reader bounces. This extension (the **genre layer**, Nonfiction Pre-Draft **Increment 5**) teaches the engine those three genres' **structural skeletons** and the **evaluator each is written for** — as a pre-draft scaffold (an optional `genre_profile` block that seeds `Argument_State` with the genre's required sections, validated exactly like today's `argument_spine`/`support_plan`/`warrant_plan` increments) plus genre-calibration audit prose for Dialectical Clarity. It invents nothing the writer didn't supply; it surfaces *which genre-required section is missing or unseeded* before drafting, and gives the audit a per-genre reviewer lens.

## 2. What shipped in M1

One increment, this PR. The buildable, model-free core:

1. **`apodictic.genre_profile.v1.schema.json`** — single-sourced schema (`plugins/apodictic/schemas/`, **not** mirrored), stdlib-validatable via `apodictic_artifacts`.
2. **`parse_genre_profiles()` + the B1–B4 + W4 check block in `argument_spine.py`** (pure stdlib; staged-off when the block is absent).
3. **The "pitch deck" form-enum value** added to `docs/argument-state-schema.md` §1 prose + the genre-canonical-section table in the validator.
4. **Extended `--self-test`** cases (the behavioral track — no pytest).
5. **Three canonical worked fixtures** (`example-argument-state-genre-{grant,academic,pitch}.md`) wired into `validate.sh --check-all` under `--strict`.
6. **Genre-calibration audit prose** — a Pitch Deck entry + a Reviewer-Anticipation Lens (grant / academic / pitch) in `dialectical-clarity.md` § Genre & Audience Calibration, and the contribution/related-work + Specific-Aims/Approach structural signals folded into the existing Academic + Grant entries.
7. **The byte-identical mirror** of `argument_spine.py` and `validate.sh` into root `scripts/` and `plugins/apodictic/scripts/` (the schema is single-sourced, not mirrored).

**Not in M1 (honestly flagged):** the draft-time diagnosis (actually reading a grant proposal and emitting findings) runs through the LLM-driven Dialectical Clarity audit — M1 ships the model-free structure contract + the genre-calibration prose the audit reads, not a deterministic scorer. Reviewer-anticipation generation (**W5**: the writer pre-lists evaluator objections, the validator surfaces an empty required class) is scoped as the genre layer's **Increment 2**, not this build; it checks the writer's list and never authors objections.

## 3. The genre structures

| Genre | `form` | Required sections (roles) | AT | Evaluator | Signature risk |
|---|---|---|---|---|---|
| **Grant proposal** | `grant-proposal` | specific-aims · significance · innovation · approach | AT3 | panel-reviewer | FM-A18 (Implementation Blindspot) |
| **Academic paper** | `academic-article` | contribution · related-work · method · limitations | AT2/AT1 | peer-reviewer (strictest; CL0 disqualifying) | a contribution with no related-work positioning |
| **Pitch deck** | `pitch-deck` | problem · solution · traction | AT3 (compressed) | investor | FM-A8 (False Precision Theater — vanity traction) |

`required_sections` are **writer-declared** (D2: an NIH R01, an NSF proposal, and a foundation LOI all work) — the engine validates the writer's structure, not a hardcoded template; **W4** carries the genre-canonical advisory, overridably.

## 4. The schema: `apodictic.genre_profile.v1`

One block per pre-draft `Argument_State`. Fields: `schema` (const), `genre` (enum: grant-proposal / academic-article / pitch-deck), `required_sections` (array, minItems 1, of `{role, heading, seeded_by}`; `seeded_by` ∈ C0+ladder / stakes / subclaim / support_plan / warrant_plan / objection / none), `evaluator` (enum: panel-reviewer / peer-reviewer / investor), `reviewer_objections` (optional array; Increment 2). The per-section `{role, heading, seeded_by}` shape — including the `seeded_by` enum — is enforced in `argument_spine.py`'s `parse_genre_profiles`, because the stdlib subset validator (`apodictic_artifacts.validate_obj`) type-checks array items but does **not** recurse into object items. Both the schema `$comment` and the validator document this.

Genre sections seed the existing `Argument_State` as `### ` sub-headings under §1–§6 (D3) — **no** new top-level numbered section, so `docs/argument-state-schema.md` stays at v0.1.1.

## 5. Validator checks (the `argument-spine` extension)

| ID | Severity | Rule |
|---|---|---|
| **B1 — invalid genre profile** | ERROR | A `genre_profile` block fails its schema (bad `genre`/`evaluator`/`seeded_by` enum, empty `required_sections`, missing field, bad per-section shape, broken JSON). |
| **B2 — section unseeded** | ERROR | A declared `required_sections[].heading` has no matching heading present in the artifact. **Signature check** (parallel to A2/A6/A9). |
| **B3 — genre/form mismatch** | ERROR | `genre_profile.genre` is incompatible with `argument_spine.form`. **Only fires when a spine block is present** (a genre profile may precede the full spine). Comparison is **normalized** (lowercase, collapse runs of whitespace/hyphens to a single separator), so `grant proposal` matches `grant-proposal`. |
| **B4 — duplicate genre profile** | ERROR | More than one `genre_profile` block (the piece is one genre). Parallels scene-ethics E2. |
| **W4 — thin genre skeleton** | WARN (ERROR `--strict`) | A declared genre's *canonical* required section is missing from `required_sections`. Override: `<!-- override: argument-spine-genre <genre> — <rationale> -->`. |

Staged off when absent: an `Argument_State` with no `genre_profile` block behaves exactly as before. A/W exit discipline unchanged (`errs` → exit 1; `warns` → exit 0 unless `--strict`, which CI uses).

## 6. Design calls (resolved)

- **D1 — extend `argument-spine`, not a new validator.** The genre profile is part of the same pre-draft contract on the same `Argument_State`; splitting it would duplicate the parse/seed machinery and bump the count for no separation benefit. Scene-ethics earned a *new* validator because its artifact and concern are genuinely separate; the genre profile is the spine's genre lens. **Count stays 49** (verified against `validate.sh` `AGG_VALIDATORS` → derived `AGG_COUNT`).
- **D2 — writer-declared sections + a canonical W4 advisory** (Firewall-clean; no hardcoded NIH template).
- **D3 — `### ` sub-headings under §1–§6** (no schema-version bump; `argument-state-schema.md` stays v0.1.1).
- **D4 — three worked genres.** Shipped as **three sibling fixture files** (one per genre), each clean-passing under `--strict`, rather than one all-three file — because B4 forbids more than one `genre_profile` per artifact, so all-three-in-one-file would self-trip B4. This is the "trivial variation" the spec's D4 allowed for `--check-all` isolation; the gate coverage is identical.
- **D5 — hard pitch-deck firewall boundary** (diagnose the argument, never design/tactics; cited the audit's existing not-rhetoric-coaching line).
- **D6 — reviewer-anticipation checks the writer's list only** (W5, Increment 2; never authors objections).

## 7. Spec-review findings folded (every one)

- **[P2] Inventory-parity precedent citation re-pathed.** The precedent — *workflow/pre-draft modules are not registry audits and must not be added to `audit-routing-table.md` lest they trip `check-inventory-parity`* — is real and on-point, and lives at **`docs/promise-contract-audit.md:102`** (root `docs/`), not in the skills tree. The genre layer adds **no** `audit-routing-table.md` entry and **no** `release-registry.json` capability edit (no new `/command`, no new signal-emitting audit); `check-inventory-parity` needs no marker bump. (The same precedent line independently confirms **apodictic has no `_golden_capabilities.json`** — validating the no-golden-bump stance.)
- **[P2] `built-when` marker moved onto a `docs/` home doc.** `check-status-drift.mjs` scans **`docs/**/*.md` only**; the scratch spec was outside that root, so a marker there had no CI force. The enforcing marker now lives on `docs/nonfiction-pre-draft.md` § The genre layer (its Status line is the one the linter reads); this doc carries a mirror marker.
- **[P3] Drifted line numbers — re-verified against the live repo.** The dispatch is the stable `argument-spine)` **case label** in `validate.sh` (the spec's 4844 and the findings' 4883 are both stale at different times — referencing the case label avoids the drift). Other cited lines re-verified: `AGG_VALIDATORS` and the `--check-all` argument-spine fixture block are present; `dialectical-clarity.md` FM-A18, the Grant entry, the Academic entry, the not-rhetoric-coaching line, and the objections-Not-Allowed line all present verbatim; `argument-state-schema.md`'s schema-versioning rules confirm D3.
- **[P3] B3 normalization pinned.** The spine schema's `form` is a free `{"type":"string"}` and the human-facing form enum uses spaced lowercase (`grant proposal`) while `genre_profile.genre` uses hyphenated tokens (`grant-proposal`). B3 normalizes **both sides** (lowercase, collapse whitespace/hyphens) before comparing, with a self-test case for the `grant proposal` vs `grant-proposal` pair (`b3_spaced_form_ok`) so the build doesn't ship a brittle exact-match.
- **[P3] Increment numbering reconciled.** The home doc numbers Increments 1–4 sequentially, where Increment 4 (scene-ethics) is a *distinct* validator. The genre layer is **"Increment 5 of the pathway"** by sequential position, but it **rides the `argument-spine` validator** (like Increments 1–3) — so its codes are the **B-family (B1–B4) + W4**, not A-codes, and the home doc states this lineage explicitly (a note under the Status line + in the Increment-boundaries section).

## 8. Acceptance (all backed by a gate or self-test that FAILS if violated)

1. Schema present + valid + loadable by `apodictic_artifacts.load_schema("apodictic.genre_profile.v1")` (and in `known_schema_ids`).
2. Validator extended, **count unchanged** (`AGG_VALIDATORS` derives `AGG_COUNT`; `--self-test-all` reports 49/49).
3. Self-test green + extended: clean (all three genres), B1 (each bad enum + bad JSON + empty `required_sections` + missing per-section field), B2 (declared heading absent, incl. a prose-not-heading lookalike), B3 (genre≠form, the spine-absent skip path, and the spaced-spelling compatibility pair), B4 (two genre blocks), W4 (missing canonical role, advisory + `--strict` ERROR + override silences, + the academic no-related-work signature), and the staged-OFF no-op.
4. `--check-all` green, including the three genre fixtures under `--strict`.
5. Mirror byte-identical (`check-mirror`).
6. Generators/parity green (`release-generate.mjs --check`, `assemble-changelog.mjs --check`, both build `--self-check`s, `check-status-drift.mjs`).
7. Docs freshness: the home-doc Status flip + this doc + the ROADMAP item 11 flip, all in this PR.
8. Inventory parity NOT tripped (no `audit-routing-table.md` edit).
9. Changelog fragment (`changelog.d/argument-genre-extension.md`), stating the count-unchanged fact. (Not paper-rooted — this is calibration on an existing engine — so the arXiv-citation fleet rule is N/A.)
10. Firewall preserved: the genre layer extracts/validates the writer's declared structure and surfaces absence; it invents no aims, contribution claim, objection text, or traction numbers, and the pitch-deck entry coaches no design/tactics.
