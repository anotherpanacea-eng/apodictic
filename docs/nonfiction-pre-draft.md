# Nonfiction Pre-Draft Pathway — a workflow

**Status:** Increments 1 (**argument spine**) + 2 (**source/evidence map**) + 3 (**warrant pre-check**) built. Roadmap: `ROADMAP.md` → Workflows → Nonfiction Pre-Draft. Home: **pre-writing-pathway** (thesis-driven mode), reference `pre-writing-pathway/references/nonfiction-pre-draft.md`. Seeds: `Argument_State.md` (`docs/argument-state-schema.md`). Validator: `validate.sh argument-spine`.

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

### The source/evidence map (Increment 2) — seeds §3

Per subclaim, the writer plans the **intended support** — and the validator surfaces which subclaims are still **bare assertions** (no support planned). Each planned support unit is an `apodictic.support_plan.v1` block that seeds §3 Support Map:

```json
{
  "schema": "apodictic.support_plan.v1",
  "subclaim_id": "C1",                    // a Cn declared in the spine's claim ladder
  "support_type": "DATA",                 // REASON / EXAMPLE / DATA / AUTHORITY / EXPERIENCE (§3's five)
  "planned_support": "the city accessibility audit's count of non-compliant corners",
  "scheme_hint": "SIGN",                  // optional: one of §3's eight argument schemes
  "status": "to-acquire"                  // in-hand (already have it) / to-acquire (plan to get it)
}
```

A subclaim with **no** `support_plan` block is a **bare assertion** — once support planning has started, the validator flags it (W2) so unsupported claims surface *before* drafting. The Firewall holds: the writer plans which evidence to bring; the engine never invents or fabricates evidence. Field set canonical in `schemas/apodictic.support_plan.v1.schema.json`.

### The warrant pre-check (Increment 3) — seeds §4

Per subclaim, the writer plans the **warrant** — the principle that connects the support to the claim — as an `apodictic.warrant_plan.v1` block that seeds §4 Warrant and Inference Map:

```json
{
  "schema": "apodictic.warrant_plan.v1",
  "subclaim_id": "C1",
  "warrant": "removing a documented barrier is a legitimate use of public funds",
  "warrant_status": "EXPLICIT",     // EXPLICIT / RECOVERABLE / MISSING / CONTESTED
  "backing": "PRESENT",             // PRESENT / THIN / ABSENT
  "qualifier": "MATCHED"            // MATCHED / OVERCONFIDENT / UNDERCLAIMED
}
```

The check is **audience-calibrated** (per the spine's `audience_receptivity`): for a **HOSTILE** audience, a warrant that is not `EXPLICIT` or has `ABSENT` backing must be made explicit and backed before drafting (validator W3) — a hostile reader won't grant an implicit or unsupported connecting principle. Field set canonical in `schemas/apodictic.warrant_plan.v1.schema.json`.

## The `argument-spine` validator

`validate.sh argument-spine <run_folder|files>` (parses the `argument_spine` block via the shared `apodictic_artifacts` engine). Degrades to an advisory `WARN` without `python3`.

| ID | Severity | Rule |
|---|---|---|
| **A1 — invalid spine** | ERROR | The `argument_spine` block fails its schema (bad `argument_type`/`burden_level`/`audience_*`/`stakes_type` enum, missing required field, fewer than one subclaim, broken JSON). |
| **A2 — unseeded** | ERROR | A spine block is present but the artifact is **not** a seeded `Argument_State` — it lacks the canonical `## 1. Context and Classification` / `## 2. Claim Architecture` headings. **Signature check:** the spine must seed the shared artifact, not float free. |
| **A3 — thesis/C0 drift** | ERROR | The seeded §2 `C0 (main claim):` line does not carry the spine's `thesis`. **Signature check:** the structured spine and the human-readable Argument_State must agree. |
| **W1 — anti-thesis echo** | WARN (ERROR `--strict`) | The `anti_thesis` is empty or a normalized echo of the `thesis` — a pre-draft plan must name a **genuine** opposing view, not a restatement (the nonfiction analogue of fiction's anti-idea). Override: `<!-- override: argument-spine-antithesis — <rationale> -->`. |
| **A4 — invalid support plan** | ERROR | A `support_plan` block fails its schema (bad `support_type`/`scheme_hint`/`status` enum, malformed `subclaim_id`, missing required field, broken JSON). *(Increment 2)* |
| **A5 — dangling subclaim_id** | ERROR | A `support_plan`'s `subclaim_id` is not a `Cn` declared in the spine's claim ladder. *(Increment 2)* |
| **A6 — support unseeded** | ERROR | `support_plan` blocks are present but the artifact has no `## 3. Support Map` heading — the support map must seed §3 (parallel to A2). *(Increment 2)* |
| **W2 — bare assertion** | WARN (ERROR `--strict`) | Once support planning has started (≥1 `support_plan`), a declared subclaim with **no** planned support — a bare assertion to address before drafting. **Staged**, so a spine-only (Increment 1) artifact is never flagged. *(Increment 2)* |
| **A7 — invalid warrant plan** | ERROR | A `warrant_plan` block fails its schema (bad `warrant_status`/`backing`/`qualifier` enum, malformed `subclaim_id`, missing field, broken JSON). *(Increment 3)* |
| **A8 — dangling subclaim_id** | ERROR | A `warrant_plan`'s `subclaim_id` is not a `Cn` declared in the spine's ladder. *(Increment 3)* |
| **A9 — warrant unseeded** | ERROR | `warrant_plan` blocks present but no `## 4. Warrant and Inference Map` heading (parallel to A2/A6). *(Increment 3)* |
| **W3 — implicit warrant (hostile)** | WARN (ERROR `--strict`) | For a `HOSTILE` audience, a warrant that is not `EXPLICIT` or has `ABSENT` backing — make it explicit and back it before drafting. **Audience-calibrated** (no-op for non-hostile audiences). Override: `<!-- override: argument-spine-warrant — <rationale> -->`. *(Increment 3)* |

**A2 and A3 are the signature checks** — together they mechanize the *seed-Argument_State* integration (the chosen design over a standalone artifact); A6 extends that discipline to §3 and **W2** is the source/evidence map's signature (surfacing bare assertions before drafting). **Ownership boundary.** `argument-spine` owns the pre-draft contract and the seeding integrity; it does not diagnose the argument (that is the Dialectical Clarity audit, once a draft exists), judge severity, or fill the draft-dependent sections.

## Workflow

1. **Classify** the piece: form, goal, argument type (AT0–AT4), burden level, audience.
2. **State the thesis** (C0) and the **claim ladder** (the necessary subclaims that build to it).
3. **Name the anti-thesis** — the strongest opposing view the argument must defeat.
4. **Map the support (Increment 2)** — per subclaim, add a `support_plan` block naming the intended support and its type (seeds §3). A subclaim with none is a bare assertion to resolve before drafting.
5. **Pre-check the warrants (Increment 3)** — per subclaim, add a `warrant_plan` block naming the connecting principle and its status/backing (seeds §4). For a HOSTILE audience, make implicit or unbacked warrants explicit.
6. **Seed `Argument_State.md`** — write the spine, support, and warrant blocks and the §1–§4 (+ §6 Objection 1) they populate; leave the remaining draft-dependent sections pending.
7. Validate with `validate.sh argument-spine` (`--strict` in CI). A canonical worked example (`core-editor/references/example-argument-state-predraft.md`) is gated by `validate.sh --check-all`.

## Increment boundaries

**Increment 1:** the argument spine — `apodictic.argument_spine.v1` block + schema, the seed-into-`Argument_State` integration, the `argument-spine` validator (A1–A3 + W1), the worked example, the `--check-all` gate, and the pre-writing-pathway nonfiction mode.

**Increment 2:** the source/evidence map — `apodictic.support_plan.v1` block + schema (one per planned support unit, linked to a spine subclaim, seeding §3 Support Map), the `argument-spine` validator extended with A4–A6 + W2 (the **bare-assertion** surfacing being the signature), and the worked example extended with §3. Same validator (no count change).

**Increment 3:** the warrant pre-check — `apodictic.warrant_plan.v1` block + schema (one per subclaim, seeding §4 Warrant and Inference Map), the `argument-spine` validator extended with A7–A9 + W3 (the **audience-calibrated** implicit-warrant flag for a HOSTILE audience being the signature), and the worked example extended with §4. Same validator (no count change). With Increments 1–3, the pre-draft seeds the Toulmin core of the argument — claims (§2), grounds (§3), and warrants (§4).

**Future increments:**
- **Scene-ethics plan** — for narrative nonfiction / memoir with real people: a pre-draft consent/disclosure plan (pairs with the **Legal Risk Register**). *Needs a design pass — taxonomy and the boundary with Legal Risk.*
