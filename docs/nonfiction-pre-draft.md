# Nonfiction Pre-Draft Pathway — a workflow

**Status:** Increment 1 (**argument spine**) built. Roadmap: `ROADMAP.md` → Workflows → Nonfiction Pre-Draft. Home: **pre-writing-pathway** (thesis-driven mode), reference `pre-writing-pathway/references/nonfiction-pre-draft.md`. Seeds: `Argument_State.md` (`docs/argument-state-schema.md`). Validator: `validate.sh argument-spine`.

## Purpose

Fiction pre-writing is character-driven; nonfiction is **thesis-driven**. Before a draft exists, an argument-shaped writer needs to plan the *spine* of the argument — the thesis, the claim ladder that builds to it, and the strongest opposing view it must defeat. This pathway captures that plan and **seeds the shared `Argument_State.md`** so the rest of the nonfiction engine (Dialectical Clarity + the companion modules) consumes one contract instead of rebuilding the argument once a draft arrives.

## The Firewall

Inherits the pre-writing Firewall: the pathway helps the writer *discover and structure* their argument through questions and frameworks. It does **not** invent claims, fabricate evidence, or write prose. The spine is the writer's plan, made explicit and checkable — not generated content.

## Why seed Argument_State (not a standalone artifact)

`Argument_State.md` is the Nonfiction Argument Engine's single source of truth (§§1–10, populated by the Dialectical Clarity audit and annotated by companion modules). The pre-draft spine populates the **plannable** sections up front:

| Spine field | Seeds Argument_State |
|---|---|
| `thesis` | §2 **C0 (main claim)** |
| `subclaims` | §2 claim ladder (C1, C2, …) |
| `anti_thesis` | §6 **Objection 1** (the opposing view the argument must defeat) |
| `form` / `goal` / `argument_type` / `burden_level` / `audience_*` | §1 Context and Classification |
| `stakes` / `stakes_type` | §2 Stakes |

The draft-dependent sections (§3 Support Map, §4 Warrant, §5 Burden/Scope, §7 Narrative-as-Evidence, §8 Cross-Section, §9 Diagnostic Summary) are **left pending** — the Dialectical Clarity audit fills them once a draft exists. Seeding (rather than a separate pre-writing artifact that later converts) means there is no parallel schema and no conversion step: the writer plans into the same file the engine will later diagnose.

## The artifact: `Argument_State.md` (pre-draft), seeded from the spine

A pre-draft `Argument_State.md` carries an `apodictic.argument_spine.v1` block plus the §1/§2 (+ §6 Objection 1) markdown it seeds:

```json
{
  "schema": "apodictic.argument_spine.v1",
  "form": "op-ed",
  "goal": "persuade the council to fund curb-cut ramps citywide",
  "argument_type": "AT3",                 // AT0–AT4
  "burden_level": "HIGH",                 // LOW / MEDIUM / HIGH
  "audience_expertise": "MIXED",          // GENERAL / MIXED / EXPERT
  "audience_receptivity": "HOSTILE",      // SYMPATHETIC / MIXED / HOSTILE
  "thesis": "the city should fund curb-cut ramps on every downtown corner",
  "subclaims": ["C1: missing curb cuts are a daily mobility barrier", "C2: the phased cost fits the existing budget"],
  "anti_thesis": "limited dollars are better spent on road resurfacing that benefits more residents",
  "stakes": "residents with mobility needs are excluded from downtown until the gaps close",
  "stakes_type": "MORAL"
}
```

Enums mirror Argument_State §1/§2. `thesis`/`anti_thesis`/`form`/`goal` are strings; `subclaims` is an array (≥1). Field set canonical in `schemas/apodictic.argument_spine.v1.schema.json`.

## The `argument-spine` validator

`validate.sh argument-spine <run_folder|files>` (parses the `argument_spine` block via the shared `apodictic_artifacts` engine). Degrades to an advisory `WARN` without `python3`.

| ID | Severity | Rule |
|---|---|---|
| **A1 — invalid spine** | ERROR | The `argument_spine` block fails its schema (bad `argument_type`/`burden_level`/`audience_*`/`stakes_type` enum, missing required field, fewer than one subclaim, broken JSON). |
| **A2 — unseeded** | ERROR | A spine block is present but the artifact is **not** a seeded `Argument_State` — it lacks the canonical `## 1. Context and Classification` / `## 2. Claim Architecture` headings. **Signature check:** the spine must seed the shared artifact, not float free. |
| **A3 — thesis/C0 drift** | ERROR | The seeded §2 `C0 (main claim):` line does not carry the spine's `thesis`. **Signature check:** the structured spine and the human-readable Argument_State must agree. |
| **W1 — anti-thesis echo** | WARN (ERROR `--strict`) | The `anti_thesis` is empty or a normalized echo of the `thesis` — a pre-draft plan must name a **genuine** opposing view, not a restatement (the nonfiction analogue of fiction's anti-idea). Override: `<!-- override: argument-spine-antithesis — <rationale> -->`. |

**A2 and A3 are the signature checks** — together they mechanize the *seed-Argument_State* integration (the chosen design over a standalone artifact). **Ownership boundary.** `argument-spine` owns the pre-draft contract and the seeding integrity; it does not diagnose the argument (that is the Dialectical Clarity audit, once a draft exists), judge severity, or fill the draft-dependent sections.

## Workflow

1. **Classify** the piece: form, goal, argument type (AT0–AT4), burden level, audience.
2. **State the thesis** (C0) and the **claim ladder** (the necessary subclaims that build to it).
3. **Name the anti-thesis** — the strongest opposing view the argument must defeat.
4. **Seed `Argument_State.md`** — write the spine block and the §1/§2 (+ §6 Objection 1) it populates; leave the draft-dependent sections pending.
5. Validate with `validate.sh argument-spine` (`--strict` in CI). A canonical worked example (`core-editor/references/example-argument-state-predraft.md`) is gated by `validate.sh --check-all`.

## Increment boundaries

**Increment 1 (this):** the argument spine — `apodictic.argument_spine.v1` block + schema, the seed-into-`Argument_State` integration, the `argument-spine` validator (A1–A3 + W1), the worked example, the `--check-all` gate, and the pre-writing-pathway nonfiction mode.

**Future increments:**
- **Source/evidence map** — plan, per subclaim, the intended support and which claims are still bare assertions (seeds §3 Support Map). The user-chosen scope deferred this from Increment 1.
- **Scene-ethics plan** — for narrative nonfiction / memoir with real people: a pre-draft consent/disclosure plan (pairs with the **Legal Risk Register**).
- **Warrant pre-check** — surface the load-bearing warrants the draft will need to make explicit for a HOSTILE audience (seeds §4).
