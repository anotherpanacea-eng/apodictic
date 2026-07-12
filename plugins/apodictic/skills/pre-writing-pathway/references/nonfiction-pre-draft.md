# Nonfiction Pre-Draft (pre-writing mode)

**Status:** v1 (Increments 1–3 — argument spine + source/evidence map + warrant pre-check)
**When:** the writer has an argument-shaped idea (op-ed, policy brief, essay, white paper, testimony, open letter) but no draft — and the structure is **thesis-driven**, not character-driven. Route here instead of the fiction pre-writing flow when intake/`Franklin` classifies the idea as nonfiction / argument-shaped.
**Inherits:** the Pre-Writing Firewall (`pre-writing-pathway/SKILL.md`) — help the writer plan structure; never invent claims, fabricate evidence, or write prose.

---

## Purpose

Capture the **argument spine** before drafting — the thesis, the claim ladder that builds to it, and the strongest opposing view it must defeat — and **seed the shared `Argument_State.md`** so the Dialectical Clarity audit and the companion modules later consume one contract. Design + lineage: [`docs/nonfiction-pre-draft.md`](../../../../docs/nonfiction-pre-draft.md).

---

## The artifact: a pre-draft `Argument_State.md`, seeded from the spine

Plan the spine as one `apodictic.argument_spine.v1` block, then write the §1/§2 (+ §6 Objection 1) markdown it seeds:

```markdown
<!-- apodictic:argument_spine
{"schema":"apodictic.argument_spine.v1","form":"op-ed",
 "goal":"persuade the council to fund curb-cut ramps citywide",
 "argument_type":"AT3","burden_level":"HIGH",
 "audience_expertise":"MIXED","audience_receptivity":"HOSTILE",
 "thesis":"the city should fund curb-cut ramps on every downtown corner",
 "subclaims":["C1: missing curb cuts are a daily mobility barrier",
              "C2: the phased cost fits the existing budget"],
 "anti_thesis":"limited dollars are better spent on road resurfacing"}
-->
```

- **`thesis`** → §2 **C0 (main claim)**; **`subclaims`** → §2 claim ladder; **`anti_thesis`** → §6 **Objection 1** (optionally typed via the flat siblings `anti_thesis_target` / `anti_thesis_relation` — Argument_State §6's Target/Relation vocabulary; R2).
- **`argument_type`** AT0–AT4 · **`burden_level`** LOW/MEDIUM/HIGH · **`audience_expertise`** GENERAL/MIXED/EXPERT · **`audience_receptivity`** SYMPATHETIC/MIXED/HOSTILE → §1.
- Leave the **draft-dependent** sections (§§3–5, 7–9) pending — the Dialectical Clarity audit fills them once a draft exists.

Field set canonical in `schemas/apodictic.argument_spine.v1.schema.json`. Worked example: `core-editor/references/example-argument-state-predraft.md`.

### The source/evidence map (Increment 2) — seeds §3

Per subclaim, plan the **intended support** as an `apodictic.support_plan.v1` block (under a `## 3. Support Map` heading). A subclaim with none is a **bare assertion** the validator surfaces (W2) before drafting.

```markdown
<!-- apodictic:support_plan
{"schema":"apodictic.support_plan.v1","subclaim_id":"C1","support_type":"DATA",
 "planned_support":"the city accessibility audit's count of non-compliant corners",
 "scheme_hint":"SIGN","status":"to-acquire"}
-->
```

- **`subclaim_id`** — a `Cn` declared in the spine's ladder. **`support_type`** — REASON/EXAMPLE/DATA/AUTHORITY/EXPERIENCE (§3's five). **`status`** — in-hand / to-acquire. **`scheme_hint`** (optional) — one of §3's eight schemes. The Firewall holds: plan which evidence to bring; never invent or fabricate it.

### The warrant pre-check (Increment 3) — seeds §4

Per subclaim, plan the **warrant** (the principle connecting support to claim) as an `apodictic.warrant_plan.v1` block (under a `## 4. Warrant and Inference Map` heading):

```markdown
<!-- apodictic:warrant_plan
{"schema":"apodictic.warrant_plan.v1","subclaim_id":"C1",
 "warrant":"removing a documented barrier is a legitimate use of public funds",
 "warrant_status":"EXPLICIT","backing":"PRESENT","qualifier":"MATCHED"}
-->
```

- **`warrant_status`** EXPLICIT/RECOVERABLE/MISSING/CONTESTED · **`backing`** PRESENT/THIN/ABSENT · **`qualifier`** MATCHED/OVERCONFIDENT/UNDERCLAIMED. For a **HOSTILE** audience (per the spine), a non-EXPLICIT or ABSENT-backed warrant is flagged (W3) to make explicit before drafting.

### The scene-ethics plan (Increment 4) — a distinct artifact

For narrative nonfiction / memoir depicting **identifiable real people**, plan each depiction's ethics in a *separate* artifact, `[Project]_Scene_Ethics_Plan_[runlabel].md` (not in `Argument_State`). One `apodictic.scene_ethics.v1` block per person — the writer's **ethical** plan, cross-referencing the **Legal Risk Register** (which owns *legal* exposure) via `legal_ref`:

```markdown
<!-- apodictic:scene_ethics
{"schema":"apodictic.scene_ethics.v1","id":"EP-01",
 "subject":"the narrator's former manager (named, identifiable)",
 "depiction":"portrayed making a dismissive remark in a meeting",
 "consent_status":"not-sought","handling":"anonymize",
 "fairness_check":"role and remark kept; identifying details changed"}
-->
```

- **`consent_status`** obtained/sought-pending/not-sought/not-applicable · **`handling`** as-is/anonymize/composite/seek-consent/omit · optional `fairness_check`, `legal_ref` (an `LR-NN`). The Firewall holds: the writer makes the ethical calls; the plan surfaces unresolved depictions. Not ethical adjudication, not legal advice. Validated by a **separate** validator: `scripts/validate.sh scene-ethics <run_folder>` — E1 schema, E2 unique `EP-NN` ids; **W1 unresolved depiction** (as-is + consent not-sought + no fairness rationale; override `scene-ethics-unresolved EP-NN`), W2 no legal cross-check (as-is + no `legal_ref`; override `scene-ethics-legalcheck EP-NN`). W1/W2 advisory, ERROR `--strict`.

---

## Protocol

1. **Classify** — form, goal, argument type, burden level, audience (the §1 fields).
2. **Thesis + ladder** — state C0 and the *necessary* subclaims that build to it (≥1).
3. **Anti-thesis** — name the strongest opposing view the argument must defeat (a genuine one, not a restatement of the thesis). This is the nonfiction analogue of fiction's anti-idea.
4. **Seed** — write the spine block and the §1/§2 (+ §6 Objection 1) markdown into `Argument_State.md`; mark the rest pending.
5. **Hand off** — when a draft exists, the Dialectical Clarity audit populates the remaining sections from this seed.

## Mechanical check

`scripts/validate.sh argument-spine <run_folder>`: A1 schema, **A2 seeds Argument_State §1/§2**, **A3 the C0 main claim carries the thesis** (A2/A3 are the signature seed-integration checks); W1 anti-thesis echo (name a genuine opposing view; override `<!-- override: argument-spine-antithesis — … -->`). Increment 2: A4 support-plan schema, A5 each support plan attaches to a declared subclaim, A6 the support map seeds §3; **W2 bare assertion** (a declared subclaim with no planned support, once planning has started). Increment 3: A7 warrant-plan schema, A8 each warrant attaches to a declared subclaim, A9 the warrant map seeds §4; **W3 implicit warrant** (for a HOSTILE audience, a non-EXPLICIT or unbacked warrant; override `<!-- override: argument-spine-warrant — … -->`). W1/W2/W3 advisory, ERROR under `--strict`. Ownership boundary + lineage: [`docs/nonfiction-pre-draft.md`](../../../../docs/nonfiction-pre-draft.md).
