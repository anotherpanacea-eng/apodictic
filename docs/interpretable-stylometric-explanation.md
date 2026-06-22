# Interpretable Stylometric Explanation — descriptive style-feature labels over the Author Voice Fingerprint

**Status:** **Built (M1), 2026-06-21.** Shipped: the `apodictic.style_label.v1` schema, the `core-editor/references/interpretable-stylometric-explanation.md` overlay module, `scripts/style_explanation.py` + `validate.sh style-explanation` (X1–X6 + W1), and the canonical `example-author-style-explanation.md` (a local-only profile with three same-register `function-words` labels forming one coordinating cluster, plus one out-of-cluster punctuation label) wired into `--check-all` under `--strict`. **Build notes:** the validator count is **derived** from `validate.sh`'s `AGG_VALIDATORS` list (not a hand-maintained number — the spec/PR state it as "derived," never an `N→N+1` literal); the module is homed in **core-editor** (a derived reading aid on the author voice profile, like #9 — not a craft audit), with the worked example in `core-editor/references/` where `--check-all` resolves fixtures; **X4** prose-level prescription (not id-addressable) is silenced ONLY by the bare `style-frame` override while a label-level match is silenced per-id with `style-frame SL-NN` (a per-id override never suppresses unrelated prose — the content-advisory W1 split); the resolver classifies on parsed blocks (`_has_block`), not raw substrings, and prefers the file that actually carries `style_label` blocks when both an `Author_Voice_Profile.md` and an `Author_Style_Explanation.md` sit in one author-root. The label-*generating* embedding/scoring model is a deferred **M2** lazy-import + `skipif` seam — this M1 validator never calls a model. Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities), item 19.

<!-- built-when: scripts/style_explanation.py -->

**Source paper.** *Latent Space Interpretation for Stylistic Analysis and Explainable Authorship Attribution*, arXiv:2409.07072 — <https://arxiv.org/abs/2409.07072>. The method identifies anchor points in a style-embedding space and uses an LLM to attach natural-language style descriptions, precomputable offline. This capability is the **descriptive, firewall-safe** M1 slice of that idea: the *labels* (and their binding to a measured feature) are the artifact; the embedding/LLM that *generates* them is the deferred M2 seam. Cited in the build PR + the `changelog.d/` fragment per the standing fleet rule.

---

## 1. What this is (and what it is NOT)

APODICTIC's Author Voice Fingerprint (#9, `apodictic.voice_fingerprint.v1`) measures *how distinctive*
an author's voice is and persists it across a career — but only as **numbers** (scalar z-scores like
`mattr_z`, `burrows_to_author_centroid`). A writer reading that profile learns *that* their voice sits
0.7 from their author centroid; they do not learn **which measured features** carry that distance, in
plain language.

This capability is the **labelling layer**: it attaches a **natural-language description** to an
**already-measured** stylistic feature — "the prose leans hard on the definite article", "function-word
profile concentrated in *the / and / but*", "high character-n-gram repetition in the `-ing` family" —
each label **bound by provenance** (`feature_ref`) to the exact measured feature it describes. It is a
**reading aid for the fingerprint**, not a new measurement and **not advice**.

- It introduces **no new stylometry**. Like #9, it CONSUMES the SETEC `voice_profile` per-family
  feature inventory (`families.<family>.top_features[].{feature, mean, sd, cv}`). The only new thing it
  produces is the *label text* plus its binding back to a measured feature.
- It does **not duplicate #9**. #9's unit is *one work's position* in stylometric space (a scalar
  `metrics` map); this unit is *one feature's natural-language gloss* (a `label` string + closed
  descriptive enums). They compose; neither subsumes the other (see §4).
- It is **strictly descriptive**. It *names* a measured feature; it **never** prescribes a voice change
  ("vary your function-word profile") and **never** names a model to emulate ("write more like X").

### The load-bearing firewall (why this is the riskiest of its wave)

This capability is **one preposition** from a Firewall breach. "Your prose leans on the definite
article" is a measured description (in-bounds). "Write more like Author X" is a prescriptive directive
(out of bounds). The whole design is built so the **data shape itself cannot express the prescriptive
sentence**, and the validator catches any that leaks into prose:

1. **No imperative/target field exists.** There is no `recommendation`, `target`, `goal`, `should`,
   `action`, `rewrite`, or `compare_to_author` field. There is **nowhere in the shape** to put "write
   more like X." A fabricator would have to smuggle it into `label` free text — exactly what X4 scans.
2. **`frame` is a closed *descriptive* enum** (`describes-feature` / `describes-cluster` /
   `describes-baseline-position`). There is no `prescribes-*` / `recommends-*` member.
3. **`direction` is descriptive, relative to the author's OWN baseline** (`elevated` / `typical` /
   `reduced`) — the indicative mood, never the imperative. The schema cannot carry "increase" /
   "decrease".
4. **`feature_ref` is required and provenance-bound** (X2). A label is a gloss on a number that already
   exists — it cannot invent a feature the corpus does not exhibit.
5. **No comparison author can be named as a model.** `register` is a comparability class, used only to
   keep a cluster's labels within one register (X5) — never "be like author Y."
6. **No editorial severity.** No `severity` field; X3 rejects any Must/Should/Could token.

The worst a malformed/hostile block can do is put a prescriptive sentence in the `label` free-text
string — and that single residual surface is precisely what X4 exists to catch.

---

## 2. The block + schema (`apodictic.style_label.v1`)

One `apodictic.style_label.v1` block per *salient* measured feature (or feature cluster) the overlay
glosses — not every feature in the SETEC inventory. The blocks are HTML-comment-wrapped JSON carriers
(`<!-- apodictic:style_label … -->`) parsed by `apodictic_artifacts.parse_blocks`; the visible markdown
summarizes them for the author.

| Field | Shape | Notes |
|---|---|---|
| `schema` | const `apodictic.style_label.v1` | |
| `id` | `^SL-[0-9]{2,}$` | unique per artifact (X1) |
| `feature_family` | enum | `function-words`, `char-ngrams`, `pos-trigrams`, `dependency-ngrams`, `sentence-length`, `lexical-diversity`, `punctuation` (mirrors SETEC's families) |
| `frame` | enum | `describes-feature` / `describes-cluster` / `describes-baseline-position` — all descriptive stances |
| `direction` | enum | `elevated` / `typical` / `reduced` — within-author indicative, never an instruction |
| `magnitude` | enum | `marked` / `moderate` / `slight` |
| `feature_ref` | string | provenance into the consumed measurement; non-emptiness is X2 |
| `feature_tokens` | string[] (optional) | the concrete tokens the feature ranks over |
| `label` | string | the natural-language gloss; the single free-text surface X4 scans |
| `register` | string (optional) | comparability class; used only by X5 |

The shared subset schema engine (`apodictic_artifacts.validate_obj`) honors only
`required`/`const`/`enum`/`type`/array-`minItems`+item-`type`/`pattern`. The firewall's schema half is
carried entirely by those keywords; any residue (the X4 label-prose scan, `feature_ref` non-emptiness,
X5 same-register comparability) is enforced in `style_explanation.py` — the `content_advisory.py`
precedent where a conditional lives in Python because the engine cannot express it.

---

## 3. The validator + numbered gates

`validate.sh style-explanation <author_root|files...> [--strict]`, delegating to
`scripts/style_explanation.py` (mirrored byte-identically to `plugins/apodictic/scripts/`). Reuses
`apodictic_artifacts` (block grammar + schema engine); classifies on **parsed blocks**, never a raw
`"apodictic:style_label" in text` substring.

- **X1 — schema.** A block fails its schema (bad `feature_family`/`frame`/`direction`/`magnitude` enum,
  malformed `SL-NN` id, missing required field, broken JSON, or a duplicate id). **ERROR.**
- **X2 — provenance / anti-fabrication.** A label whose `feature_ref` is empty or absent — a style
  claim with no measured feature behind it is treated as **fabricated** and rejected. **ERROR.**
  (Mirrors #9 F2.)
- **X3 — no editorial-severity leak.** The reader-facing prose or any `label` carries a
  Must/Should/Could-Fix token, OR an `apodictic:finding` block is present. A style label is not a
  defect. **ERROR.**
- **X4 — descriptive, not prescriptive (the signature firewall gate).** A `label` or the visible prose
  matches a **prescriptive construction aimed at the voice** (a modal/imperative verb governing a style
  change) OR a **comparison-to-emulate** construction (`write/sound more like …`, `emulate …`, `model
  your prose on …`). The bare descriptive adjective ("*elevated* use of the definite article") does NOT
  fire — only the directive. The adjective-ambiguous `direction` words (`reduced`/`lower`/`elevated`)
  read as indicative unless they govern a possessive object ("reduce **your** reliance …"). **Advisory;
  ERROR under `--strict`.** Override per id: `<!-- override: style-frame SL-NN — <rationale> -->`
  (label-level matches, the legitimate case being *quoting the author's own stated revision goal*); the
  bare `<!-- override: style-frame — <rationale> -->` silences prose-level (non-id) matches.
- **X5 — same-register cluster.** A `describes-cluster` label referencing ≥2 labels must have all
  referenced labels share a `register` — a cross-register cluster is a comparability error the AI-prose
  domain-shift caution forbids. A dangling SL-ref in a cluster is an integrity error, not a silent skip.
  **ERROR.**
- **X6 — local-only hygiene.** The artifact lacks a `<!-- author-style-explanation: local-only -->`
  marker, or references an external `http(s)` URL — a labelled voice profile is voice-cloning-adjacent
  and must never be transmitted. **Advisory WARN ONLY, never escalated under `--strict`** (the binding
  guarantee is the module's runtime no-external-call rule, exactly as #9 W2).
- **W1 — seed/coverage.** No `style_label` blocks resolved → no-op; only one feature glossed → the
  overlay is thin. **Advisory; ERROR under `--strict` for the thin case only**, never the no-op.

`--self-test` provides built-in cases for every gate (incl. the **decoy** resolver case — a file that
only NAMES `apodictic:style_label` in prose must not win resolution over the real profile).

---

## 4. Distinct from Author Voice Fingerprint #9 (no duplication)

| | #9 `voice_fingerprint` (BUILT) | this `style_label` (NEW) |
|---|---|---|
| Unit | one *work's* position in stylometric space | one measured *feature's* natural-language gloss |
| Payload | flat scalar `metrics` map (z-scores) | a `label` string + closed descriptive enums |
| Question | *how far has the voice moved across works* | *which measured features, in plain words, characterize the voice* |
| New data | none (persists consumed scalars) | none (labels consumed features) |
| Provenance ref | `centroid_ref` → consumed audit output | `feature_ref` → consumed per-feature measurement |
| Validator | `author_fingerprint.py` (F1–F4, W1–W2) | `style_explanation.py` (X1–X6, W1) |
| Schema | `apodictic.voice_fingerprint.v1` | `apodictic.style_label.v1` |

They **compose** (a profile can carry both block types; a `style_label` may gloss a feature a
`voice_fingerprint` aggregates into a z-score) but neither subsumes the other. The labels live in #9's
existing `Author_Voice_Profile.md` (composing with `voice_fingerprint` blocks) OR a sibling
`Author_Style_Explanation*.md`; the resolver handles both.

---

## 5. M1 scope vs the M2 model seam

This candidate is **model-CPU** (it needs an embedding/scoring LLM to *produce* the labels). The split
keeps M1 stdlib + CI-runnable:

- **M1 (this build).** The descriptive scaffolding: the schema, the `style-explanation` validator
  (X1–X6 + `--self-test` + `--check-all` wiring), the dual-script mirror, this module reference, and the
  canonical fixture. M1 validates over **injected** feature-label records — `style_label` blocks already
  present in the artifact (authored by the operator by hand, or, in M2, by the model). M1 proves the
  **firewall holds on the data shape** regardless of who produced the labels. No model, no network.
- **M2 (deferred seam).** The embedding/scoring model that *generates* the labels from the SETEC
  `voice_profile` feature inventory. A **lazy-import + `skipif`** seam: the generator imports the
  backend only when invoked, and the model-dependent eval is `skipif`-guarded so CI stays green without
  the model. The firewall is enforced by the M1 validator regardless of the generator — the model can
  only emit labels that pass X1–X6, and X4 catches any prescriptive label it hallucinates.

---

## 6. Assumptions & limits

- M1 cannot *verify* that a `feature_ref` resolves to a real measured feature (the external value cannot
  be re-resolved here — the #9 `centroid_ref` limit). X2 checks presence/non-emptiness as the
  anti-fabrication floor; full resolution is an M2 concern.
- X4's prescription scan is a heuristic regex over English prose (the `content_advisory.py` /
  `author_fingerprint.py` precedent). It is advisory (ERROR only under `--strict`) with an ID-scoped
  override precisely because prose-level matching is imperfect; the **structured** firewall (no target
  field) is the binding guarantee, the regex is the backstop. A negator separated from the directive
  verb by a clause is a known heuristic limit (shared with content-advisory); the fixture is worded to
  read cleanly rather than rely on an override.
- The natural-language *quality* of the labels is an M2 model concern; M1 makes no claim about label
  usefulness, only about label *shape and firewall-safety*.
- No `maxLength` on `label` is enforceable by the engine; a length cap, if ever needed, is a Python
  check in `style_explanation.py`, not a schema keyword.
