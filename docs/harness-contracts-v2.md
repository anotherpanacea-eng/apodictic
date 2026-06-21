# Harness Contracts v2 — schema-coverage gate + closed-key enforcement

**Status:** **Built, 2026-06-21.** Shipped: the `schema-coverage` validator (`scripts/schema_coverage.py`) + the declarative `schemas/_coverage.json` binding table + its two schemas (`apodictic.schema_coverage.v1`, `apodictic.schema_binding.v1`); opt-in closed-key (`additionalProperties:false`) enforcement in the shared engine (`apodictic_artifacts.py`) with the six flat const-tagged blocks closed; and an advisory docs-no-re-list prose lint (`--check-docs`). Wired into `validate.sh --check-all` against the real `schemas/` dir, and added to `AGG_VALIDATORS`. Self-testable validators **50 → 51** (derived from `AGG_VALIDATORS`, not a hand-maintained literal). Roadmap: [`ROADMAP.md` → Harness Contracts v2](../ROADMAP.md#harness-contracts-v2).
<!-- built-when: scripts/schema_coverage.py -->
<!-- built-when: scripts/validate.sh contains "schema-coverage" -->

> This doc is the canonical description of the coverage manifest. Per the schema-`$comment`
> discipline it does **not** re-list the `_coverage.json` field set in prose beyond §3 — §3 points
> at the schemas, which are canonical.

## 0. Framing — the brief was half-shipped

The roadmap line asks to "make JSON Schema the source of truth for every structured artifact …
generalize the v2.0.0 `apodictic.finding.v1` move from one block type to the whole artifact set."
Grounding in the repo shows most of that generalization already shipped:

- `plugins/apodictic/schemas/` holds **22 hand-authored `apodictic.*.schema.json` artifact
  schemas** — not just `finding.v1` but `audit_trigger.v1`, `readiness.v1`, `diagnostic-state.v1`,
  `severity_calibration.v1`, `gate_event.v1`, `state_card.v1`, `legal_risk.v1`, `argument_spine.v1`,
  `support_plan.v1`, `warrant_plan.v1`, `pitch_copy.v1`, `viz_manifest.v1`, `annotation.v1`,
  `project_registry.v1`/`project_entry.v1`, `feedback_item.v1`, `reader_question.v1`,
  `retcon_item.v1`/`retcon_reading.v1`, `scene_ethics.v1`, and `canon_fact.v1`. (A 23rd
  `*.schema.json`, `execution-gates.v1.json`, is the gate *manifest* read by `run_gate.py`, not an
  `apodictic.*` artifact schema — see §2.)
- `scripts/apodictic_artifacts.py` is the shared stdlib subset JSON-Schema engine; every one of the
  22 is bound to a Python validator that loads it through that engine.

> **Count note (folds spec-review P2 #1).** The original spec said "22 schemas"; the disk count
> at build time is **22 `apodictic.*` artifact schemas** — the spec's table of 21 plus the
> `canon_fact.v1` schema that landed with the Continuity Bible (2026-06-20) after the spec was
> written. The coverage gate **re-enumerates from disk** rather than trusting any literal, so the
> count is mechanical, not asserted. Two further `*.schema.json` files describe the coverage
> manifest itself (`schema_coverage.v1`, `schema_binding.v1`) — 24 `*.schema.json` total — and are
> excluded from the orphan check because they describe the table rather than being carried in it.

So "enumerate the set, define a schema per artifact, generate a Python validator, wire each into the
gate" is largely done. What was **not** done — the genuine prose↔schema-drift surface this
capability kills — is three holes:

1. **No coverage gate.** Nothing asserted the invariant the system rests on: *every
   `*.schema.json` on disk stays bound to a validator and stays exercised against a real canonical
   file by `--check-all`.* A new/renamed/orphaned schema could land with no validator and no gate
   teeth, and CI would stay green.
2. **Prose re-lists schema fields, unguarded.** Author-facing reference docs re-enumerate field sets
   the schema `$comment` says docs "must not re-list," and nothing checked it.
3. **Closed-key (`additionalProperties:false`) declared but ignored.** The subset engine ignored the
   key, so a misspelled `severty`/`recomendation` validated clean.

This is the drift-kill layer that completes Harness Contracts v2: a coverage manifest +
`schema-coverage` validator wired into `--check-all`, opt-in closed-key enforcement, and a
docs-no-re-list lint. It does **not** re-author the 22 schemas or invent a YAML→schema generator —
the schemas already *are* the single source of truth; the gap was that nothing forced them to *stay*
the only source. A generator was considered and **rejected**: it would add a second source (the
YAML) and *create* the drift this capability removes.

No model seam — pure stdlib harness mechanics, so the Firewall is irrelevant here (nothing diagnoses
or rewrites prose; this is contract enforcement).

## 1. Unit of work

- **New** `scripts/schema_coverage.py` (mirrored byte-identical to `plugins/apodictic/scripts/`).
- **New** `plugins/apodictic/schemas/_coverage.json` — the binding table the gate reads
  (single-sourced under `schemas/`, resolved via `apodictic_artifacts.schema_dir()`; **not**
  mirrored, matching the schema/manifest convention).
- **New** `apodictic.schema_coverage.v1` + `apodictic.schema_binding.v1` schemas (the manifest
  dogfoods its own discipline).
- **Engine extension** in `apodictic_artifacts.py`: honor `additionalProperties:false` in
  `validate_obj` (opt-in), plus a `schema_field_names(schema_id)` helper for the docs lint.
- **`validate.sh`**: a `schema-coverage` dispatch arm; `schema-coverage` added to `AGG_VALIDATORS`;
  a `--check-all` block running it against the real `schemas/` dir; the `Commands:` and
  `Aggregate: --check-all` strings updated to name it.

## 2. The enumerated artifact set (made load-bearing)

`schemas/_coverage.json` encodes the binding table machine-readably: every `apodictic.*.schema.json`
maps to its `validators[]` (the `validate.sh` dispatch arm(s) that load it), a `canonical_gate` (the
exact filename/dirname token `--check-all` exercises it against, or the literal `self-test-only`),
and `closed_keys`. The gate proves disk reality matches the table.

> **`execution-gates.v1.json` (folds spec-review P2 #3).** It is a `*.schema.json`-named file but
> *not* an `apodictic.*` artifact schema — its name is `execution-gates.v1.json`, **not**
> `*.schema.json`. `known_schema_ids()` globs `*.schema.json`, so it is **already excluded** from the
> orphan check and can never be flagged an orphan. Therefore it is **not** listed in `non_artifact[]`
> — listing it would trip W1 (which requires a `non_artifact` entry to be a real `*.schema.json` on
> disk). `non_artifact[]` ships empty; the mechanism remains for any future `*.schema.json` that is
> genuinely non-artifact.

## 3. Data shapes

`_coverage.json` validates against `apodictic.schema_coverage.v1` (envelope: `schema`,
`non_artifact[]`, `bindings[]`), whose `bindings[]` items each validate against
`apodictic.schema_binding.v1` (`schema`, `validators[]` minItems 1, `canonical_gate`, optional
`closed_keys`). Both envelope and item schemas are themselves `additionalProperties:false` — a stray
key in the manifest is a typo the gate catches. The field sets are canonical in those two schema
files; this doc does not restate them.

Two adds to `apodictic_artifacts.py`, both backward-compatible:

- `validate_obj` honors `additionalProperties:false` — every key not in `properties` is an error.
  Schemas default to absent/`true` (the permissive behavior the open schemas — the sidecar,
  `gate_event` — rely on), so closing is strictly opt-in.
- `schema_field_names(schema_id)` → `frozenset` of declared `properties` keys (or `None` if absent),
  the single source the docs lint reads.

## 4. The gate — `schema-coverage`

`validate.sh schema-coverage [<schemas_dir>] [--strict] [--check-docs]`, default dir via
`apodictic_artifacts.schema_dir()`. Reuses the shared engine for all schema loading. Checks:

- **C1 manifest validity.** `_coverage.json` parses and validates against the coverage + binding
  schemas (incl. the closed-envelope stray-key check). ERROR.
- **C1' closed-key agreement.** For each binding, the schema file's `additionalProperties` agrees
  with the table's `closed_keys` (`true`→`false`-in-file; `false`/absent→open). A table↔file drift
  is an ERROR — the table can't claim a closure the schema file doesn't carry, or vice-versa.
- **C2 no orphan schema.** Every `*.schema.json` on disk (via `known_schema_ids()`), minus
  `non_artifact[]` and the two self schemas, appears in `bindings[]`. The core anti-drift assertion.
  ERROR, names the orphan.
- **C3 no phantom binding.** Every `bindings[].schema` exists on disk. ERROR.
- **C4 binding proven, not asserted.** For each binding, ≥1 named `validators[]` command is a real
  `validate.sh` dispatch arm **and** the schema `$id` literal is grep-reachable in a `.py` that the
  **bound arm** delegates to (the gate parses the arm's case block for its `.py` references and greps
  *those*, not an arbitrary script). The "distrust count-shaped claims" discipline, mechanized.
  ERROR. *(Folds spec-review P2 #4: C4 greps the bound script.)*
- **C5 canonical-gate reachability.** For each binding whose `canonical_gate` is a filename/dirname
  (not `self-test-only`), the **exact token** appears in `validate.sh`'s `--check-all` region **and**
  the named file/dir exists under `core-editor/references/`. `self-test-only` rows (the two registry
  schemas, with no shipped canonical instance) are exempt from the file check but the bound validator
  must be in `AGG_VALIDATORS`, so *some* real check runs. ERROR. *(Folds spec-review P2 #4: exact
  tokens, not prose. The `--check-all` region is extracted from apodictic's
  `if [ "$1" = "--check-all" ]; then … fi` block, not a case arm.)*
- **W1 non_artifact integrity.** Every `non_artifact[]` entry exists on disk as a `*.schema.json`
  (else the exclusion is dead). WARN; ERROR under `--strict`.

Exit: 0 clean / WARN-only; 1 on any ERROR (or WARN under `--strict`); 2 usage. Degrades to advisory
PASS without `python3`, like every other Python-backed arm.

### 4.3 Closed-key enforcement (the misspelled-field kill)

`closed_keys:true` is set — and the schema file flipped to `additionalProperties:false` — only for
the **flat embedded-block schemas with a `const schema` and every legitimate field declared**:
`audit_trigger.v1`, `readiness.v1`, `severity_calibration.v1`, `feedback_item.v1`,
`reader_question.v1`, `scene_ethics.v1`. Their optional fields (`severity_calibration.rationale`;
`feedback_item.conflicts_with`/`evidence_refs`; `reader_question.targets`/`source_note`;
`scene_ethics.fairness_check`/`legal_ref`) are all **declared in `properties`**, so closing rejects
only *undeclared* keys — a typo, never a legitimate optional. **Explicitly NOT** closed:
`finding.v1` (forward-extended per pass — `evidence_quote` and future per-pass fields),
`diagnostic-state.v1` / `gate_event.v1` (intentionally `additionalProperties:true`), or the nested
schemas the Python validators already police. The engine self-test proves a `severty`-typo block now
fails and an open schema still permits the stray key; every closed schema re-verified clean against
its canonical file.

### 4.4 Docs-no-re-list lint (the prose-drift kill)

`schema-coverage --check-docs` scans the author-facing reference docs that **opt in** by carrying a
defer-marker (a line stating the field set is canonical in the schema) and WARNs if a line that
**labels a field-set re-listing** (`Fields:` / `**Fields (…):**` / `field set`) enumerates a field
name not declared by any mentioned schema. Narrow by construction: it fires only on labelled
re-listing lines on opt-in docs, so it never polices arbitrary prose (a line that merely *mentions* a
field — "the finest `quote` rung" — carries no label and is skipped). It catches **divergence**, not
list-existence; a faithful re-listing is allowed. **Advisory (WARN, never fails the gate) in
increment 1.**

> **Doc locations (folds spec-review P2 #2).** The reference docs the lint covers live under
> `plugins/apodictic/skills/core-editor/references/` (e.g. `findings-ledger-format.md`), **not**
> `docs/`. The live `finding.v1` field re-listing is at `findings-ledger-format.md:94`; the
> `audit_trigger.v1` / `readiness.v1` re-listings at `:133` / `:134`. The lint resolves the
> references dir from either mirrored script dir.

## 5. Structural guards (apodictic's own)

- **Dual script mirror (CI-blocking).** `schema_coverage.py` and the `apodictic_artifacts.py` edit
  land byte-identical in both `scripts/` and `plugins/apodictic/scripts/`, proven by `check-mirror`.
  `_coverage.json` + the two schemas live under `schemas/` and are single-sourced (not mirrored).
- **Self-test in `--self-test-all`.** `schema-coverage` is in `AGG_VALIDATORS`; the count line is
  computed (`AGG_COUNT`), so adding the arm is the whole count change (50 → 51).
- **Real-file invariant in `--check-all`.** The gate runs against the **real** `schemas/` dir, not
  only its self-test — C2/C5/C1' only have teeth against disk reality.
- **Hostile fixtures.** The self-test builds tmp fixtures for an orphan schema (C2), a phantom
  binding (C3), an unproven binding — no real arm and a real arm whose bound `.py` lacks the id (C4),
  a canonical gate `--check-all` doesn't run and a missing canonical file and an unbacked
  `self-test-only` (C5), a closed-key table↔file drift (C1'), a manifest stray key + missing required
  field (C1), a dead `non_artifact` exclusion (W1), a `severty`-typo block (§4.3), and the docs-lint
  drift/faithful/honest-seam triad (§4.4) — each with a matching negative. Hermetic (tmp dirs).

## 6. Acceptance criteria — all met

1. `schema-coverage --self-test` passes (C1, C1', C2, C3, C4×2, C5×3, W1×2, closed-key typo, docs
   lint ×3). ✓
2. `schema-coverage` (real `schemas/`) passes — `_coverage.json` complete, every binding proven,
   every canonical gate real. ✓
3. `--self-test-all` passes with `schema-coverage` present; `AGG_COUNT` = 51 (re-enumerated). ✓
4. `--check-all` passes and includes the `== schema-coverage (real schemas dir) ==` block;
   `check-mirror` confirms the new `.py` files are byte-identical. ✓
5. `apodictic_artifacts.py --self-test` passes the new closed-key + `schema_field_names` cases. ✓
6. After the §4.3 flip, `structured-findings`/`finding-trace`/`feedback-triage`/`reader-instrument`/
   `scene-ethics` still pass on every shipped canonical file (no real artifact carried a stray key). ✓
7. Degradation: with `python3` masked, the arm prints the degraded WARN/PASS and exits 0. ✓
8. No behavioral regression — the full prior `--check-all` set stays green. ✓

## 7. Assumptions / limits

- Subset-engine scope is unchanged beyond the `additionalProperties:false` add (no `$ref`, no
  `oneOf`, no nested recursion — nested validation stays in the per-artifact Python validators).
- C4 is a binding *proof* (the id literal appears in a bound `.py`), not a call-graph analysis —
  sufficient to catch orphaning/renaming and false claims.
- The docs lint is narrow (opt-in labelled re-listings only) and advisory in increment 1 — it
  reduces, not eliminates, prose drift. Physically removing the re-listings is an author's prose edit
  (out of mechanical scope), flaggable as a docs-only follow-up (no Codex gate per the
  docs-PRs-skip-Codex rule).
- No pytest — verification is via `validate.sh --self-test` / `--check-all`, matching the suite.
- Version bump at merge (minor — new validator + engine behavior change), not in the PR.
