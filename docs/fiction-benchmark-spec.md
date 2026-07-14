# Fiction Structural Fault-Injection & Specificity Benchmark

## Core Development Editor — Validation Spec (fiction wing)

In-repo distillation of the full design spec. Sibling of
[argument-benchmark-spec.md](argument-benchmark-spec.md) — the fiction wing of
the same eval harness, not a parallel system. The shared 0–3 metric scale,
decision rules, blind-review packet format, and fixture-provenance policy live
in the local-only `docs/eval-harness-spec.md` / `docs/blind-review-protocol.md`;
this file adds the fiction-specific scoring, the multi-lane ground-truth schema,
the matched clean/broken corpus design, and the α-licensing frame.

> **The construct this benchmark measures.** Not "recovers the correct
> structural diagnosis of a fiction manuscript" — that overreaches to
> whole-novel, theme, and reader-help scale it cannot support. The honest
> construct is: **can the Core DE, under a fixed run protocol, reliably produce
> evidence-grounded findings that recover pre-registered LOCAL structural
> defects, name the correct mechanism, calibrate severity and repair target, and
> avoid false positives on registered intentional devices?** A defensible
> *proxy* for editor competence on structural fault detection — explicitly NOT
> reader-help, theme-correctness, market-taste, or whole-manuscript-scale
> diagnosis.

**This document defines the benchmark. It does not change the engine.** Fixture
texts and answer keys are never cited, quoted, or paraphrased inside any pass
reference, audit reference, or prompt the engine runs with. If a benchmark run
surfaces a real pass/audit failure, that is a separate work item against the
pass or audit.

---

## The validity architecture: three lanes

Fiction developmental diagnosis is not uniformly objective. "Act 2 sags," "the
theme doesn't land" are genuine editorial judgments on which competent editors
legitimately disagree — a benchmark that pretends otherwise manufactures false
authority. But a POV break in an established third-limited chapter, a continuity
contradiction between two stated facts, a setup planted with emphasis and never
paid off, a scene removable without breaking causality are **locatable,
near-objective structural facts**. The benchmark scores only the second kind.

Every scored anchor carries five tags — `gt_class` plus four orthogonal fields:

| Field | Values | Declares |
|---|---|---|
| `gt_class` | `A` \| `B` \| `C` | **Ontology.** A = mechanical/planted; B = structural-consensus (banded); C = interpretive. |
| `construct_lane` | `fault_injection` \| `consensus_alignment` \| `reader_effect` \| `editorial_preference` | Which validity lane. |
| `evidence_basis` | `planted_diff` \| `public_domain_control` \| `editor_panel` \| `reader_study` \| `preference_pair` | Where the ground truth comes from. |
| `decision_use` | `gate` \| `report` \| `exploratory` | What the benchmark does with the anchor. |
| `reliability_status` | `deterministic` \| `provisional_author` \| `panel_confirmed` \| `low_agreement` | How trustworthy the label is now. |

1. **Lane 1 — fault-injection detection (Class A, gates).** A planted local
   defect with an exact locus, deterministic by construction (the mutation diff
   *is* the answer key). A miss is a sensitivity failure; a false fire on the
   clean member is a specificity failure. No inter-editor disagreement is
   credible — the fact was inserted.
2. **Lane 2 — consensus alignment (Class B, gates ONLY after human agreement).**
   Near-objective judgments where editors converge to a *band*, not a point:
   act/movement boundary placement (± one scene), gross arc shape, scene
   segmentation. Starts `decision_use: report` / `reliability_status:
   provisional_author` and is *promoted* to `gate` / `panel_confirmed` only when
   a ≥3-editor panel demonstrates adequate agreement (D-2).
3. **Lane 3 — utility / reader-effect / preference (Class C, never gates).**
   Thematic resonance, emotional weight, pacing feel, market readiness.
   `decision_use: exploratory` permanently. Recording a Class-C observation
   descriptively in a run log is permitted; gating on it is a schema error the
   validator rejects (Check 2).

### The psychometric frame

**Inter-rater agreement (Krippendorff's α) is not ground truth — it is evidence
that a label may responsibly be *used* as ground truth.** α *licenses* whether a
Class-B anchor's band may `gate`; it never scores the engine. If a ≥3-editor
panel shows poor agreement on a Class-B band, the ruling is "the construct is
unstable / the band is too tight ⇒ reclassify to C, or widen the band" — *never*
"the engine failed." Use **ordinal-weighted α** for band/location items and
**nominal α** for category items; the key records which per anchor.

---

## Scope: the vertical slice

**The canonical slice pass-set (pin this exact line — anti-leak).** Every
fixture — broken *and* clean — runs the identical set: **{0, 1, 2, 5, 7, 8, 10}
+ Synthesis** (the §2a baseline floor {0,1,2,5,8} + Pass 7 POV + Pass 10
entity/timeline). Pass 1 is carried (it costs nothing to the leak surface); Pass
9 is excluded (thematic coherence is Lane 3 / Class C — out of construct). The
pass list is byte-identical across all fixtures so it leaks zero information
about which defect a given fixture carries.

Four sensitivity buckets, each a **matched clean/broken pair**, plus one Class-B
arc pilot anchor:

| Bucket | Macro block | Class-A defect (broken member) | Its own control (clean member) |
|---|---|---|---|
| **S — Structure Map** | Structure Map (0+2) | Orphan scene (removable without causal break) | clean base — no inert scene |
| **P — POV mechanics** | Character Architecture (7, +5 arc pilot) | Planted POV break / head-hop / knowledge-leak | clean base — POV discipline intact |
| **R — Reveal Economy** | Reveal Economy (8) | Emphatic setup with its payoff scene excised | clean base — setup *and* payoff present |
| **C — Continuity** | Theme & Continuity (10 + continuity-bible) | Entity-fact contradiction (dual-mutated) + a timeline-arithmetic error | clean base — the same two facts made mutually consistent |

Deferred with reasons: Emotional Dynamics (Pass 4, Class C), Reader Dynamics
(Pass 1+3, wide bands + SETEC cross-repo), Scene Delivery (Pass 6, Increment 2),
Theme (Pass 9, Class C), Submission Readiness (Pass 11, no stable ground truth).

### The two scope dials (accepted)

- **D-1 — matched clean/broken pairs are MANDATORY** for every derived-broken
  sensitivity fixture. Makes FQ7 specificity airtight (the clean member is a
  same-prose, same-length control), gives every bucket a positive control for
  free, and is the only mechanism that closes **mutation-seam confounding**
  (§Validity threats). The carve-out clause survives in the template for a
  future fixture where a clean base is genuinely impossible — such a fixture
  must state the reason explicitly, never silently drop the pairing.
- **D-2 — Class-B anchors are LICENSED by ≥3-editor agreement (α)**, not a
  single second editor. You cannot compute α from n=2, so a single editor cannot
  license a band to gate. Poor α ⇒ reclassify to C or widen the band, never
  "engine failed."

### The seven fiction test questions (FQ1–FQ7)

| # | Test question | Lane / gt_class |
|---|---|---|
| FQ1 | Did Pass 0/2 recover the actual structure (inventory; boundaries within band)? | inventory Lane-1/A; boundaries Lane-2/B |
| FQ2 | Did the engine locate the planted defect at the registered locus, on in-text evidence? | Lane-1 / A |
| FQ3 | Did it name the right *mechanism* (POV break vs continuity vs dropped thread vs orphan scene)? | Lane-1 / A |
| FQ4 | Did severity land in band, without over-firing on the clean member? | Lane-1 / A |
| FQ5 | Did Pass 5 recover the gross arc on the arc-legible control? | Lane-2 / B |
| FQ6 | Did the repair guidance target the mechanism, not a symptom? | Lane-1 / A |
| FQ7 | Did it avoid pathologizing intentional craft — and NOT fire on the clean member? | Lane-1 / A (the specificity gate) |

Every FQ is a **human scorer judgment against the key**, per
[the rubric](../evals/rubrics/fiction-benchmark.md). The mechanical validator
(below) touches *keys only*, never runs. **FQ7 is the specificity gate**: a
registered trap fired as Must-Fix on a positive control (or the clean member)
scores FQ7 = 0 for that fixture regardless of FQ1–FQ6 and blocks the bucket.

---

## Corpus design

### The load-bearing fiction move: derived-broken fixtures

Hand-writing a novella around a planted defect risks the fixture being globally
bad prose (in which case flagging everything is correct behavior, and the
fixture measures nothing). The sensitivity backbone is therefore **matched and
fault-injected**: take an original synthetic or low-recognition public-domain
base and plant one pre-registered defect via minimal surgical edits.
Deterministic ground truth (the mutation diff *is* the answer-key locus), fully
shippable (tier-1 synthetic-or-derived), realistic surround, one defect family
per fixture. Increment 1 uses original synthetic bases, pinned 2026-07-14; this
removes source-recall risk while retaining the recognition probe.

### Validity threats (two)

- **Threat 1 — recognition / recall-assisted detection.** A model that
  recognizes the base may flag the mutation as a deviation from the remembered
  original rather than detecting an internal contradiction.
- **Threat 2 — mutation-seam confounding.** The surgery leaves artifacts (a graft
  scar, deletion roughness, tonal discontinuity). A model may detect *the seam*
  without engaging the intended developmental mechanism. Bites hardest on
  orphan-scene / unpaid-setup / pov-break plants.

**Mitigations (all mandatory for derived fixtures):** (1) **matched-pair delta
scoring** (D-1, closes Threat 2) — a hit requires the defect flagged in `broken`
AND NOT flagged for that mechanism in `clean`; score the delta, not the bare
hit; the surgery must be **craft-clean** (a build-time review criterion); (2)
**dual mutation** for continuity (both loci to novel values, so recall of the
original is no shortcut); (3) prefer **original synthetic or low-recognition
bases**; (4) **recognition
probe** after every run (recall-susceptible runs weighted lightly); (5)
**evidence-grounding requirement** — an FQ2 hit requires in-text loci AND a named
mechanism; out-of-text justification = miss (recall), bare seam-detection = miss
(seam).

**Fixtures must read complete.** Under `artifact=partial`, Pass 8 marks
unresolved setups as *assets, not failures* — which would un-plant the
unpaid-setup defect. Every fixture must present as a **complete short work** and
run in complete-manuscript mode. A hard design rule: an excerpt-shaped fixture
cannot fail.

### The slice fixture set (Increment 1: 4 matched pairs + 3 standalone controls = 11 members)

**Sensitivity — 4 matched pairs (8 members, tier-1 derived):**

| Pair | Bucket | Mutation planted in `*-broken` | Expected engine surface |
|---|---|---|---|
| `pov-break/{clean,broken}` | P | 2 head-hops + 1 POV-knowledge leak at registered ¶ loci | Pass 7 finding (`F-P7-*`) |
| `continuity-contradiction/{clean,broken}` | C | Entity fact at X contradicted at Y (both novel; dual mutation) + one timeline-arithmetic error | `F-P10-*` and/or a continuity-bible `CF-NN` row |
| `unpaid-setup/{clean,broken}` | R | Emphatic Chekhov-gun setup, its payoff scene excised; still reads complete | `F-P8-*` and/or a setup-payoff `SP-NN` row |
| `orphan-scene/{clean,broken}` | S | One causally-inert scene inserted (removable, in-register) | Pass 2 finding (`F-P2-*`) |

**Specificity — 3 standalone intentional-device controls:**

| Slug | Bucket(s) | Text | Stored? | Registered trap (FQ7) |
|---|---|---|---|---|
| `yellow-wallpaper-voice-control` | P (+S) | Gilman, *The Yellow Wallpaper* (1892; Gutenberg — pin ID at first retrieval) | yes | Deliberate voice deterioration + unreliable first person is the point. A naive Pass 5 voice-drift / Pass 7 distance-inconsistency Must-Fix is the trap. |
| `gift-of-magi-reveal-control` | R | O. Henry, *The Gift of the Magi* (1905; Gutenberg) | yes | Dual withheld knowledge resolving in the twin reveal is *fair* — the Pass 8 fairness tests pass. A "withheld information / unfair misdirection" flag is the trap. |
| `christmas-carol-arc-control` | S + arc pilot (Lane-2/B) | Dickens, *A Christmas Carol* (1843; Gutenberg — verify ID at pin time) | **no — referenced** (SOURCES.md + `run.sh --fetch`) | Five-stave episodic structure must not fire "missing conventional act structure"; the compressed one-night arc must not fire "rushed arc." FGT5 registers the gross-arc band (Lane-2/B). |

Every *derived-broken* fixture is paired; the intentional-device controls are
not (their "correct diagnosis is PASS" needs no mutation). The referenced Carol
exercises the fetch path (SHA-pinned, no bytes in-repo). Increment 2 adds an
obscure PD positive control and Bierce's *An Occurrence at Owl Creek Bridge* as
the nonlinear-timeline / twist-fairness hard trap.

---

## Ground-truth answer-key schema (FGT1–FGT7)

Each fixture ships a pre-registered `groundtruth.md` (registered **before** any
run is scored — a key written after seeing a run is void). Each anchor carries
the five multi-lane tags on the line under its heading; the full field-by-field
template is [evals/fiction-groundtruth-template.md](../evals/fiction-groundtruth-template.md).

FGT7 uses `SOUND / INTENTIONAL-AND-EFFECTIVE / DEFECT-AS-PLANTED` (a deliberate
divergence from the argument schema's verdict enum — historically
`SOUND / UNCONVENTIONAL-BUT-EFFECTIVE / UNSOUND`, since renamed to
`WARRANTED / UNCONVENTIONAL-BUT-WARRANTED / UNWARRANTED` in Argument Benchmark GT
schema v0.2.0; the fiction enum is unaffected by that rename — "unsound"/"unwarranted"
are argument predicates; "defect-as-planted" says what a
broken fiction fixture is). The middle token keeps the FQ7 downgrade role. The
validator's Check 6 is parameterized on the three tokens, so reuse is a one-line
switch if a later reviewer prefers it.

### Continuity/reveal scoreability: the severity-free artifact path

A continuity or reveal plant may legitimately surface **only** as a companion
artifact row — a continuity-bible `CF-NN` contradiction or a setup-payoff `SP-NN`
abandoned/open row — which by design carries **no severity token** (the firewall
on those artifacts). A single rule keeps all four convergence anchors defined:

- **FGT2 (locus):** satisfied by an `F-P10-*`/`F-P8-*` finding **OR** a
  well-formed `CF-NN`/`SP-NN` row at the registered locus. Either is a hit.
- **FGT3 (mechanism):** the CF row's paired-fact conflict / the SP row's
  abandoned state *is* the mechanism statement.
- **FGT4 (severity):** when the plant surfaces **only** as a severity-free CF/SP
  row, FGT4 is scored as a **presence-delta** — the row present in `broken`,
  absent in `clean` — not a band. When it *also* surfaces as an `F-<ORIGIN>`
  finding, FGT4 scores that finding's severity. The key's FGT4 states which
  regime applies (`severity band` vs `presence-delta`).
- **FGT6 (repair):** unchanged — the repair target is the mechanism regardless of
  which surface reported it.

CF/SP rows are **first-class evidence of a hit**, never a second-class signal,
while never pretending a firewalled artifact carries a severity it does not have.

---

## Mechanical validator: `fiction-groundtruth-check`

The key-conformance gate, mirroring `scripts/argument_groundtruth.py` in role and
shape: a **mechanical-honesty layer over the answer keys — never a semantic
judge**. Stdlib-only Python (`scripts/fiction_groundtruth.py`), no third-party
deps, no model calls, WARN:/ERROR:/OK:/FAILED: output contract, exit codes
0/1/2, hermetic `--self-test`.

**Scope (honesty header).** Every check operates on **KEY TEXT ONLY** — the
pre-registered `groundtruth.md`. The validator never sees a run, never scores the
engine. FQ2/FQ3/FQ6 run-fidelity, FQ7's "no severity token attached," the
anti-recall / anti-seam reads, and the matched-pair delta are all **human M2
rubric work with zero mechanical backstop**.

### Checks

1. **Section coverage.** FGT1–FGT7 each covered by a heading and non-empty
   (range/list heading expansion + PROVISIONAL semantics).
2. **Multi-lane tag discipline.** Every in-scope FGT heading carries the five
   tags with values from the enums. Compound `gt_class` (`B/A`) splits on `/` and
   validates each. Mechanical rules: `gt_class: C` may never carry
   `decision_use: gate`; `decision_use: gate` requires `reliability_status ∈
   {deterministic, panel_confirmed}`; a `consensus_alignment` anchor must carry a
   band and an `[alpha_metric]`. The tag *vocabulary* is checked; the *judgment*
   that an anchor is really Class A vs B is author-registered and
   convergence-tested, not mechanized.
3. **Defect-fixture completeness.** A `broken` member (FGT2 not N/A) must have a
   non-empty plant record, registered loci with a well-shaped locus token
   (chapter/scene/§/¶/line — borrow the continuity-bible C2 locus-shape wording:
   a coarse token, a precondition, NOT a firewall proof), a defect family ∈
   {POV, CONTINUITY, REVEAL, STRUCTURE}, and a `Paired-with` sibling. A `broken`
   member with no `Paired-with` is an ERROR (D-1). A `clean` member records "no
   mutation" and marks FGT2 N/A.
4. **Expected-surface shape + family consistency (the OPEN-namespace rule —
   closed-enum port = defect).** FGT2's Expected engine surface must name a
   surface whose *shape* is recognized and whose *family* matches the defect
   family. `F-<ORIGIN>-<NN>` is an **open** namespace (finding pattern
   `^F-[A-Za-z0-9]+-[0-9]{2,}$`), validated by shape + family-prefix, never a
   closed set. `CF-`/`SP-`/`PO-` are **DISJOINT** namespaces firewalled from
   being findings; validated as cross-artifact block ids by their own shape,
   recognized only for CONTINUITY/REVEAL. A well-shaped CF/SP with no
   accompanying `F-<ORIGIN>` is **CONFORMANT** for continuity/reveal. The
   Increment-1 accept-set:

   | Defect family | Accepted surface shapes |
   |---|---|
   | `POV` | `F-P7-<NN>` (or a P5 voice-mechanism `F-P5-<NN>`) |
   | `CONTINUITY` | `F-P10-<NN>` **or** a continuity-bible `CF-<NN>` row |
   | `REVEAL` | `F-P8-<NN>` **or** a setup-payoff `SP-<NN>` row |
   | `STRUCTURE` | `F-P0-<NN>` / `F-P2-<NN>` / `F-P6-<NN>` |

   The negated/PASS decoy masks are **ADAPTED to the fiction grammar**
   (`F-P<n>(-<NN>)?`, `CF-<NN>`, `SP-<NN>`), not ported — the argument regexes are
   hardcoded to `[A-Z]{2}[0-9]+` (WR0) and match zero fiction origins, so a
   literal port masks nothing (self-test arm 9 proves it).
5. **Severity tokens.** Every severity mentioned in FGT4 must be one of the three
   canonical tokens — matched via `severity_vocab.SEVERITY_TOKEN_RE` import, never
   a local regex (validator-conventions M8). A `presence-delta` FGT4 legitimately
   carries no severity token.
6. **FGT7 classification.** One of SOUND / INTENTIONAL-AND-EFFECTIVE /
   DEFECT-AS-PLANTED (leading-token parse, gloss-tolerant); an
   INTENTIONAL-AND-EFFECTIVE key must name the device and the trap; a control /
   clean member (FGT2 N/A) claiming DEFECT-AS-PLANTED is an ERROR, as is a
   `broken` member claiming SOUND.

### Registration

`scripts/fiction_groundtruth.py` + a byte-identical hand-copy at
`plugins/apodictic/scripts/fiction_groundtruth.py` (`check-mirror`); a dispatcher
case `fiction-groundtruth-check)` with `--self-test` + a no-python3 advisory
degrade path; the token appended to `AGG_VALIDATORS=` (`AGG_COUNT` is DERIVED —
no literal to bump); the help line; a `--check-all` block iterating
`evals/fixtures/fiction-benchmark/*/groundtruth.md` (resolve-and-skip-when-absent
— `evals/` is not shipped to host workspaces). No new schema file (GT keys are
markdown, so schema-coverage M4 is unaffected).

---

## M1 / M2 split (honest boundary)

- **M1 — buildable now (this landing, CI-gated, no humans / no model runs / no
  web):** this spec doc, the template, the rubric, the 11-member fixture set +
  `SOURCES.md` / `RUN-PROTOCOL.md` / `README.md` / `run.sh --fetch`, the
  validator + full registration + both mirrors + `--check-all` green. The
  **pre-registration of all 11 keys** (including the 4 clean-member "no
  mutation" keys) is deliberately in M1: registration is a dated text artifact
  and the validator gates its form. The slice's fixtures are **single-POV**, so
  they do NOT trigger Pass 7's SETEC voice-distinctiveness supplement (whose own
  validation lives in the voiceprint repo) — no cross-repo dependency in
  Increment 1.
- **M2a — model-convergence runs (web + tokens, no editor panel):** the
  two-config convergence protocol over the slice, scored afterward by a
  separate rubric-trained scorer/session. The 2026-07-14 Terra/Opus run is
  published as a committed reconstructable package at
  `evals/results/fiction-m2a-20260714-terra-opus/`. Outcomes feed engine work items — never
  in-flight edits to keys to make runs pass. This scorer separation is not the
  ≥3-editor reliability/licensing panel reserved for M2b.
- **M2b — the human gate (not buildable without editors):** a **≥3-editor
  panel** (D-2) that α-licenses every Lane-2/B band (FGT1 boundaries, FGT5 arc)
  and supplies independent-editor convergence runs. Because three editors on
  one work are still only one reliability unit, the shared closed-response
  packet measures the coding dimensions across the seven independent works in
  this slice (three standalone controls + four clean synthetic bases; no broken
  twins), then reconciles the panel-derived Carol value to its frozen key
  projection. Exact transforms and promotion rules live in
  `docs/shared-blind-editor-panel-spec.md`. Until M2b, Lane-2/B anchors
  report but do not gate; the benchmark's public claims are scoped to Lane 1.
  Lane 3 / Class C requires a reader/preference study and is not unlocked by M2b
  either — it stays a named gap.

## Non-goals

- **No engine changes.** No pass reference, audit reference, prompt, or validator
  that gates *manuscript* runs is touched. The only `validate.sh` additions gate
  benchmark answer keys.
- **No semantic judge.** `fiction-groundtruth-check` validates keys, not runs.
- **No private bytes.** No copyrighted text, client manuscripts, or human-labeled
  private corpora in-repo — tiers 3/4 stay key-only / manifest-only behind the
  existing gitignore walls.
- **No gating on unlicensed labels.** Lane-2/B anchors report until α-licensed;
  Lane-3/C anchors never gate — the architecture, not a promise, enforces it
  (validator Check 2).
