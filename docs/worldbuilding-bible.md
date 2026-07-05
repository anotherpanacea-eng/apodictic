# Standalone Worldbuilding-Bible Coherence Tool — a pre-draft consistency checker over the author's own bible

**Status:** **Built (M1), 2026-06-21.** Shipped: the `apodictic.world_fact.v1` schema, the `core-editor/references/worldbuilding-bible.md` extraction module, `scripts/world_bible.py` + `validate.sh world-bible` (W1/WD + WB-R1/C1/C2/G1/G2 + WF), the `/world-bible` command, and the canonical `example-worldbuilding-bible.md` wired into `--check-all` under `--strict`. Self-testable validators 50 → 51 (derived from `validate.sh`'s `AGG_VALIDATORS` list — adding `world-bible` is the whole count change). Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) Tier 2, item 13. Homed in core-editor as an optional-artifact **tool/command** (routed like `/legal-risk`, not as a manuscript-pass audit). **Increment (2026-07-05):** the contradiction **State axis** (`conflicting` / `apparent` / `consistent`) on the ledger table, mechanically derived by the shared `scripts/contradiction_state.py` helper, with the `X1` firewall arm on the validator and `conflicting`-row prose-citation into the editorial letter (see §The State axis).
<!-- built-when: scripts/world_bible.py -->

> This doc lives under `docs/` (mirroring `docs/continuity-bible.md`) so `check-status-drift.mjs` — which scans `docs/**/*.md` only — sees the `built-when` marker above and enforces the Status flip in the same PR. (The reviewed spec originally lived in `setec-scratch/`, outside the lint's scope; the build moved it here, per review finding P2.)

A worldbuilding bible is the SFF author's own pre-draft reference document — the rules of the magic/tech, the cost of using it, the geography, the calendar and the order of events, the factions and their commitments. Before a single chapter exists, that bible can already contradict itself: a rule stated two ways, a cost that is sometimes paid and sometimes free, a city that is six days' ride from the capital in one note and two in another, an event that happens "before" and "after" the same anchor. This tool checks a **bible** (not a manuscript) for that class of self-contradiction — closed-set rule consistency, magic-system cost accounting, and geography/timeline contradiction — and emits an optional, locus-anchored coherence artifact. It is usable before or alongside drafting, in the pre-writing pathway's spirit, and it never invents world content: it surfaces the contradictions the bible has already committed to, and leaves the resolution to the author.

This tool deliberately mirrors the framework's existing **consistency** substrate rather than its **integration** substrate (see §Substrate, below), and is structurally templated on the shipped `legal_risk.py` / `continuity_bible.py`-class validators so it lands inside the plugin's established mechanical-validation house.

---

## Substrate (what exists, what this parallels, what is net-new)

Two distinct manuscript-facing prompt references exist, and they do **different** jobs:

| Existing surface (verified path) | What it owns | Relationship to this tool |
|---|---|---|
| **Genre Module: SF/F** — `plugins/apodictic/skills/core-editor/references/genre-sff.md` | *Mechanical consistency* of a **manuscript**: the **Rule Ledger** (Pass 10 physics-engine table), the **Cost Matrix** (Physiological/Material/Psychological/Social/Temporal), **Sanderson's Laws**, **Power Creep**, **Cost Amnesia**, **Retro-Causality**. | **This tool ports the consistency kernel from manuscript-scene scope to bible scope.** The Rule Ledger asks "is the cost paid in *this scene*"; the bible tool asks "does the bible *state* the rule and its cost coherently, before any scene exists." Same vocabulary (cost, closed limits, scaling), different input (a reference doc, not prose). |
| **SFF Worldbuilding Integration** audit — `plugins/apodictic/skills/specialized-audits/references/genre/sff-worldbuilding.md` | *Integration* of a **manuscript**: whether the world does narrative **work** (cognitive, thematic, prose, social, emotional). Its own thesis: **"The core problem is not inconsistency. It is inertness."** | **Out of scope, explicitly.** That audit takes consistency as a *baseline it does not check* and asks the next question. This tool checks the baseline — and pre-draft, where the integration audit has nothing to run on (no prose, no scenes). |
| **`docs/continuity-bible.md`** (Tier 1 item 7, **Built**) | The narrative half of a DE style sheet *extracted from a finished manuscript* — canonical names/ages/facts + a contradiction ledger. | **Sibling, not duplicate.** Continuity Bible extracts *post-draft* from prose the author wrote; this tool ingests the *pre-draft* bible the author wrote *by hand*. The continuity-bible spec is the closest **template** in the repo (block schema + validator-on-`legal_risk` + firewall section + honest-limit disclosure), and this build follows its shape. Distinct artifacts, distinct lifecycle stages. |

**The genuinely net-new territory** is the residue no surface owns: a **structured pre-draft consistency check over a hand-authored bible**, before the framework's manuscript passes have anything to read. The genre module's Rule Ledger and Cost Matrix supply the *vocabulary* (closed limits, cost types, scaling); this tool supplies the *artifact, schema, and mechanical validator* for that vocabulary at bible scope.

**Verified mechanical substrate this build reuses:**
- `scripts/apodictic_artifacts.py` — `parse_blocks(text)`, `load_schema(schema_id)`, `validate_obj(obj, schema, where)` (subset JSON-Schema engine). **Verified limitation:** `validate_obj` silently allows *unknown* keys (a misspelled field passes) — so the closed-set guarantee needs bespoke closed-key checking in `world_bible.py`, which this build adds (`W1`).
- `scripts/legal_risk.py` — the canonical flat-field-schema + `parse_items` + group-by-id + WARN/ERROR/`--strict` + run-folder/explicit-file `resolve()` + `--self-test` validator. **The structural template.**
- `scripts/timeline_checks.py` — the canonical deterministic contradiction detector: `_norm_duration` parse idiom, `_norm_anchor_day` (Day-N anchors), the `<!-- override: timeline-* -->` idiom, degrade-without-python3. **The template for the geo/timeline arms.**
- `scripts/validate.sh` — the dispatcher; `AGG_VALIDATORS` single-source registry (count `AGG_COUNT` **derived**, not hand-maintained); `--self-test-all`; `--check-all`; `check-mirror` (the `scripts/` ↔ `plugins/apodictic/scripts/` byte-identical gate). **Note (review finding P3):** `validate.sh` also keeps two *hand-maintained* human-readable strings — the `Commands:` echo and the `Aggregate: --check-all (…)` description — that enumerate every arm by hand and would drift if not updated; this build updates both in addition to `AGG_VALIDATORS`.
- `plugins/apodictic/schemas/*.schema.json` — single-sourced (not mirrored), resolved from either script dir.
- `release-registry.json` — the capability catalog `APODICTIC-Gemini` pulls.

---

## The unit of work

**One bible → one coherence pass → one optional artifact.** The input is a single worldbuilding-bible document (the author's prose-and-tables notes, or a lightly structured version of them). The output is a `[Project]_Worldbuilding_Bible_[runlabel].md` artifact of `apodictic.world_fact.v1` blocks grouped into author-facing sections, plus a contradiction ledger. The mechanical guarantee is delivered by `validate.sh world-bible <run_folder|files>`, which checks the artifact's structural integrity and **surfaces** detectable contradictions — it never resolves them.

"Optional-artifact workflow" means: the tool runs only when invoked (it is not part of any core pass), produces nothing if there is no bible, and an empty/absent artifact is a clean no-op — the same optionality `legal_risk.py` has.

---

## Data shapes

### The extracted fact: `apodictic.world_fact.v1`

One block per extracted world fact. Flat-field, string-valued, locus-cited — the `legal_risk.v1` / `canon_fact.v1` shape.

```markdown
<!-- apodictic:world_fact
{
  "schema": "apodictic.world_fact.v1",
  "id": "WF-014",
  "category": "rule",
  "subject": "blood-magic",
  "attribute": "limit",
  "value": "raise the dead",
  "polarity": "cannot",
  "cost": null,
  "loci": ["Bible §Magic ¶3"]
}
-->
```

Field contract (all of `schema`, `id`, `category`, `subject`, `attribute`, `value`, `loci` are **both** `required` and in `properties`, so the subset engine guards them):

| Field | Type | Notes |
|---|---|---|
| `schema` | const `apodictic.world_fact.v1` | block-type guard |
| `id` | string `^WF-[0-9]{2,}$` | unique within the artifact (WD duplicate check) |
| `category` | enum `rule` / `cost` / `place` / `distance` / `event` / `faction` / `entity` | **closed set** — drives which contradiction arm applies |
| `subject` | string | the named element the fact is about — the **grouping key** for cross-fact contradiction detection |
| `attribute` | string | what about the subject (`"limit"`, `"cost"`, `"distance-to"`, `"happens-before"`) |
| `value` | string | **always a string** (numerics quoted: `"6 days"`, not `6`) so the validator can type-check and parse it |
| `polarity` | optional enum `can` / `cannot` / `requires` / `n/a` | for `category=rule`: the closed-set/capability assertion the WB-R1 arm pairs on |
| `cost` | optional string \| null | for `category=cost`/`rule`: the stated price (`"one year of life"`, `"none"`, `null` if unstated); **omit the field** for a forbidden action that has no price to state |
| `pair_subject` | optional string | for `category=distance`/`event`: the *other* endpoint of the edge |
| `loci` | array of string, ≥1 | where the bible states it — the firewall's mechanical proxy |

Because the subset engine admits *unknown* keys, `world_bible.py` adds a bespoke **closed-key** pass (a misspelled field like `polairty` fails `W1`), or the closed-set guarantee would be hollow. `polarity` and `cost` are optional — but when present, the schema engine still checks `polarity`'s enum membership; `cost` is intentionally not type-constrained (the subset engine cannot express a `string|null` union), so its free-vs-real reading is done in `world_bible.py`. For the same reason `world_bible.py` adds a bespoke **`cost` value-type** check to the same `W1` pass: a non-string, non-null `cost` (an unquoted `5`, a list, a bool) fails `W1` with a clean ERROR rather than reaching the cost arm and crashing `_norm_value` — closing the one un-schema'd-field gap in the "string fields are type-checked so the arms can safely parse them" guarantee.

### The artifact

`[Project]_Worldbuilding_Bible_[runlabel].md`: the `world_fact.v1` blocks grouped under author-facing headings (`## Rules`, `## Costs`, `## Places & Distances`, `## Chronology`, `## Factions`), followed by a `## Contradiction Ledger` markdown table. Each ledger row pairs the conflicting `WF-NN` ids and cites both loci. That table is plain markdown, **not** an `apodictic:*` block. A contradiction is recorded as the conflicting `world_fact.v1` blocks (one per stated value — both retained, neither deleted) **plus** a ledger row pairing their ids. The tool records both values; it never picks a winner.

### The State axis (contradiction axis — added 2026-07-05)

The ledger table carries a **`State` column** — the contradiction *fact-state* axis, orthogonal to the editorial Must/Should/Could severity scale (a self-contradiction is a fact-state, not a defect). It rides the existing plain-markdown ledger; **no new schema**. Values (the shared `scripts/contradiction_state.py` helper, imported by both bibles):

- `conflicting` — a live, un-explained collision (the default for any written row).
- `apparent` — a collision the author marks intentional via a matching `world-rule` / `world-cost` / `world-geo` override marker (the same per-pair markers that silence the arm).
- `consistent` — no collision; **never written as a row**.

The state is **mechanically derived** from the literal collision + the override presence (`derive_state`), never model-judged. The `X1` firewall (a new arm on the existing `world-bible` validator) proves: the `State` token is a valid enum AND matches the derivation (an author-asserted state that disagrees with the override reality FAILs); the register carries no editorial-severity token and no `apodictic:finding` block (the Content-Advisory A3 precedent). `conflicting` rows are surfaced for the editorial letter to cite in prose (Stage A wiring — the Legal-Risk / Setup–Payoff precedent); an `apparent` row is intentional and is not cited. Anchored on ConStory-Bench (arXiv:2603.05890) + DOME (arXiv:2412.13575) — the taxonomy/benchmark only; detection stays mechanical.

---

## The three consistency checks (the mechanical core)

All arms are **deterministic, stdlib-only, conservative** (they fire only on confidently parseable facts; ambiguous/unparseable facts are left to the author and never become a hard failure). Each is overridable per-pair with a body marker, mirroring `timeline_checks.py`.

### 1. Closed-set rule consistency (`category=rule`)

The check groups `rule` facts by `subject` and fires on a **direct polarity contradiction**: the same `subject` asserted both `can <value>` and `cannot <value>` (normalized: case-folded, leading-article-stripped, whitespace-collapsed `value` match across opposite `polarity`). A `requires` paired with a `cannot` on the same value is also a contradiction.

- **WB-R1 rule contradiction** — same subject, same normalized value, `can` vs `cannot` (or `requires` vs `cannot`). ERROR unless overridden.
- Conservative by design: it does **not** infer implied contradictions ("can fly" vs "is bound to the earth" — different `value` strings). The check fires only on literal closed-set collisions.

### 2. Magic-system cost accounting (`category=cost` / `rule` with `cost`)

Ports the genre module's **Cost Amnesia** at bible scope. Groups cost-bearing facts by `subject` and fires on:

- **WB-C1 cost contradiction** — the same `subject` assigned two different non-null, non-`"none"` `cost` values, with neither a documented escalation. ERROR unless overridden.
- **WB-C2 free-then-costed (advisory)** — the same `subject` stated as `cost: "none"`/`null` in one fact and a real cost in another (the pre-draft form of Cost Amnesia). Advisory `WARN`; ERROR under `--strict`. Override `<!-- override: world-cost WF-NN/WF-MM — <reason> -->`.

The tool reads the *stated* cost strings; it does not adjudicate whether a cost is *dramatically sufficient* (that is the SFF Worldbuilding Integration audit's `TI-2 Passive Physics Engine`, out of scope).

### 3. Geography / timeline contradiction (`category=distance` / `event`)

Two sub-arms, both templated on `timeline_checks.py`'s anchor-drift and arithmetic detectors:

- **WB-G1 distance contradiction** — the same unordered pair `{subject, pair_subject}` assigned two different parsed distances **within one commensurable unit class**. `_norm_distance` normalizes to two **disjoint axes**: a **spatial** axis (`mile`/`league`=3 mi/`km`≈0.621 mi/`furlong`=0.125 mi → miles) and a **temporal-travel** axis (`hour`/`day`=24 h/`week`=168 h → hours). A stated travel-TIME and a stated spatial DISTANCE are **never compared against each other** (a 6-day ride and 120 miles can both be true for one edge) — review finding P3: the WB-G1 arm collide-checks only *within* an axis; cross-axis pairs are exempt, left to the author, consistent with the tool's own "distinct units that cannot be normalized to a common base are not compared" conservatism. Two distinct values for one edge on one axis → contradiction. ERROR unless overridden.
- **WB-G2 chronology contradiction** — build the partial order from `event` facts (`subject` happens-before `pair_subject`). Fire on a **cycle** (X before Y, Y before Z, Z before X) detected by a stdlib DFS over the stated edges; an override silencing any two of the cycle's edges marks the loop intentional. **Anchored-day drift** — the same event stated at two absolute `Day N` anchors (via `_norm_anchor_day`) — fires as a second WB-G2 form. ERROR unless overridden.

Override markers (per-pair, body): `<!-- override: world-rule WF-NN/WF-MM — <reason> -->`, `<!-- override: world-cost … -->`, `<!-- override: world-geo … -->` (order-insensitive: `WF-01/WF-02` ≡ `WF-02/WF-01`) — the `timeline_checks.py` override idiom.

### The firewall scan (`WF`)

A reader-facing prose scan (HTML comments and the `world_fact` blocks stripped first, the `legal_risk` L3 idiom): a resolution/invention verb leaking into the bible's prose ("the true rule is", "the canonical cost is", "should be N miles", "we pick WF-NN") means the prose **resolved** a conflict or **invented** canon instead of surfacing it. Advisory `WARN`; ERROR under `--strict`. Override `<!-- override: world-firewall — <reason> -->`. This is the firewall's artifact-level proof (no resolution verbs, both values retained); see §Honest limit for what it does *not* prove.

---

## M1 scope vs the model seam

**M1 (this build — entirely in-plugin, deterministic, gated by `validate.sh --check-all`):** the `apodictic.world_fact.v1` schema (single-sourced), `scripts/world_bible.py` (extractor-validator: schema + closed-key, WD id-uniqueness, the five contradiction arms + the WF firewall scan, with run-folder/explicit-file `resolve()`, WARN/ERROR/`--strict`, `--self-test`, degrade-without-python3), the `validate.sh world-bible` dispatch arm + `AGG_VALIDATORS` registration + the `Commands:`/`--check-all` help strings, the canonical `example-worldbuilding-bible.md` `--check-all` invariant (clean under `--strict`, with staged contradictions overridden), the hand-mirrored `plugins/apodictic/scripts/world_bible.py` (verified byte-identical via `check-mirror`), the `core-editor/references/worldbuilding-bible.md` prompt module, the `/world-bible` command, and the registration/docs-freshness steps below.

**The model seam (NOT in M1's mechanical gate):** the *extraction* step — reading a free-prose bible and emitting well-formed `world_fact.v1` blocks — is an LLM/agent task (the prompt module), not a parser. M1's **mechanical guarantee covers only the structured artifact**: given `world_fact.v1` blocks, the validator deterministically finds the closed-set/cost/geo/timeline contradictions. The tool also accepts a *pre-structured* bible (the author writes the blocks directly) as a first-class path — this is what makes M1 fully testable without the model and matches the "structured artifact is what CI gates" boundary (review open-question 3, resolved: yes).

---

## Honest limit

- **The firewall is not yet *mechanically* proven at the extraction boundary.** A fabricated locus or a mis-extracted `value` passes the validator (the locus is checked for presence/shape, not truth). Resolving each locus into the source bible waits on a shared snapshot layer (the same deferral continuity-bible makes). M1 enforces the firewall at the *artifact* level (the `WF` scan: no resolution verbs, both values retained) and leaves extraction-fidelity to author/QA.
- **Mechanical detection is conservative and will miss semantic contradictions** ("can fly" vs "earthbound" across different value strings). Intentional — those are the prompt module's and the author's job; the gate fires only on literal collisions to keep false positives near zero.
- **Distance/chronology parsing covers the common, normalizable cases** (mile/league/km on the spatial axis; day/hour on the temporal axis; Day-N anchors). Exotic or unit-less notations are exempt (left to the author), never a false ERROR. Cross-axis pairs (travel-time vs mileage) are never compared.
- **No external API, no model in the gate.** M1 is stdlib-only and CI-runnable; the model touches only the (out-of-gate) extraction step.
- **Subgenre calibration is the author's, surfaced not enforced.** Some "contradictions" are deliberate (a staged cost escalation, a rule that changes after a world event). The override markers carry that intent; the tool does not encode subgenre tables in M1.

---

## Acceptance criteria (mapped to the build)

1. **Schema lands single-sourced.** `plugins/apodictic/schemas/apodictic.world_fact.v1.schema.json` exists with `$id`/`title`/`$comment`/`required`/`properties` per the repo's schema house style, declares the closed `category` (and `polarity`) enums, and is resolvable from both script dirs. **Done.**
2. **`world_bible.py --self-test` passes** with hermetic fixtures covering: a clean bible; each of WB-R1, WB-C1, WB-C2 (advisory + `--strict` ERROR), WB-G1 (within-axis + cross-axis exemption + unparseable exemption), WB-G2 (cycle + anchor-drift); the WF firewall scan; WD id-uniqueness; the closed-key check (a misspelled field is caught despite the subset engine); the `cost` value-type check (a non-string/non-null `cost` — numeric, list, bool — fails `W1` instead of crashing the cost arm); each override marker silencing its pair; run-folder vs explicit-file `resolve()`; empty/absent artifact = clean no-op. **Done.**
3. **`validate.sh world-bible` dispatches and self-tests** — exit codes 0/1/2 matching the `legal-risk`/`timeline` arms; `--self-test` degrades to a PASS message without python3. **Done.**
4. **Registered in `AGG_VALIDATORS`** so `validate.sh --self-test-all` includes it and `$AGG_COUNT` increments by one (re-enumerated from the list — 50 → 51 — not a hand-maintained literal), AND the two hand-maintained help strings (`Commands:` echo + `Aggregate: --check-all (…)` blob) name `world-bible` (review finding P3). **Done.**
5. **`--check-all` real-file invariant** — the committed `example-worldbuilding-bible.md` is validated clean by `world-bible --strict`; the per-arm firing cases are proven by the in-code self-test fixtures. CI (`validate.sh --check-all`) is green. **Done.**
6. **Mirror integrity** — `scripts/world_bible.py` and `plugins/apodictic/scripts/world_bible.py` are byte-identical; `validate.sh check-mirror` passes; the mirror was synced by hand as the **last** step before `--check-all`. **Done.**
7. **Firewall holds** — the prompt module instructs *extract the stated, never fill the unstated*; contradictions are recorded with **both** values and **never resolved**; recommendations are abstract-structural, never invented world content; the `WF` `--check-all` scan confirms no resolution/invention verb leaks into the example artifact's prose. **Done.**
8. **Docs-freshness mechanically enforced** — this doc resides under `docs/` so `check-status-drift.mjs` (which scans `docs/**/*.md` only) sees the `built-when: scripts/world_bible.py` marker; its Status reads **Built** in the same PR (review finding P2). `assemble-changelog.mjs --check` passes over the new `changelog.d/` fragment. **Done.** *Route-dependent gates (review finding P3): because this registers as a `/world-bible` **command** (not an audit), it touches `release-registry.json`'s `commands` array + a command file (re-synced by `release-generate.mjs`), and does **not** touch `audit-routing-table.md` — so `check-inventory-parity` is correctly a no-op for this route, matching the `/legal-risk` precedent.*
9. **Release-gate clean** — full CI set green: `validate.sh --check-all`, `release-generate.mjs --check`, `build-codex.mjs --self-check`, `build-antigravity.mjs --self-check`, `assemble-changelog.mjs --check`, `check-status-drift.mjs`, `check-inventory-parity.mjs`. The PR carries the spec-status flip and goes through the Codex 5.5 review gate (this is code, not docs-only).

---

## Load-bearing design calls (resolved)

1. **Consistency, not integration.** The tool checks the baseline the SFF Worldbuilding Integration audit *assumes*. It is the genre module's consistency kernel, lifted to bible scope and pre-draft.
2. **Bible input, not manuscript input.** Distinct from continuity-bible (which *extracts from* a finished manuscript). Same block-and-validator machinery, different lifecycle stage and input.
3. **It's a tool/command, not a core pass.** Optional-artifact, invoked on demand, no-op when absent — the `legal_risk` optionality. Routed as the `/world-bible` command (review open-question 1, resolved to the command route to keep the gate set minimal and match the `/legal-risk` precedent).
4. **Closed-set contradiction is literal, not inferred.** The arms fire only on literal collisions; implied/semantic contradictions are model/author judgment, explicitly out of the mechanical gate — this keeps false positives near zero and the firewall clean.
5. **`value` is always a string; closed-key check is bespoke.** Both forced by the verified `apodictic_artifacts` engine behavior (string type-checking needs quoted numerics; the engine admits unknown keys, so closed-set integrity needs an explicit pass).
6. **Single fact schema, not per-category schemas.** One `world_fact.v1` with a closed `category` discriminator (review open-question 2, resolved: matches the engine's flat-field idiom; keeps the validator and `--check-all` invariant simple).
7. **Contradictions surfaced, never resolved.** Both conflicting facts are retained; the ledger pairs them; the author chooses canon. Picking a winner would be invention-by-adjudication — forbidden by the Firewall.

---

## Future increments (not built)

- **Snapshot-anchored locus resolution** — once a shared bible-snapshot layer lands, upgrade the firewall from author-enforced to mechanically proven (resolve each `loci` entry into the source bible), shared with the Continuity Bible / Annotated-Manuscript anchor resolver.
- **Subgenre calibration tables** — mirror the genre module's calibration tables so a New Weird bible that *means* to contradict itself is calibrated, not just overridden case-by-case.
- **Contradiction → finding promotion** — promote a Contradiction-Ledger row into an `apodictic.finding.v1` so a bible contradiction can enter the editorial loop once the author has a manuscript.
- **Semantic contradiction assist (model-side)** — surface *candidate* implied contradictions ("can fly" vs "earthbound") as advisory prompts for the author, kept out of the mechanical gate.
