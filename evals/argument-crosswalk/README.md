# Argument-taxonomy crosswalk (R4A + R4B)

`crosswalk.json` maps APODICTIC's internal argument-taxonomy codes to external
argumentation vocabularies, with explicit **mapping cardinality**. It is the machine-readable
companion to [`docs/adr/0001-argument-layer-boundary.md`](../../docs/adr/0001-argument-layer-boundary.md).

Version 0.2.0 preserves the exact 82-code `entries` set and adds a separately
drift-bound `concept_entries` layer: five R2 objection relations and three R3 AGD
moves. Concepts are not diagnostic codes. `ALTERNATIVE` and all three AGD moves
remain AIF-unmapped where the source does not license a conflict/inference node.
The 48 code rows left `unmapped` in v0.1 remain explicit present-tense conclusions,
not a quota to force into false equivalences.

## What it covers

The **82** argumentation *code-layer* entries: 46 Dialectical Clarity codes + 20 FM-A patterns
+ 8 scheme hints + 3 warrant-verdict values + 5 premise-plausibility flag **types**. Benchmark
scaffolding (GT1–GT8 anchors, `Argument_State` section numbers, severity tiers) is **out of scope
by design** (ADR D6).

## Reference vocabularies

- **AIF** — Argument Interchange Format node ontology (`I-node` / `RA-node` / `CA-node` / `PA-node`); an *optional serialization adapter*, not the editorial vocabulary (ADR D2).
- **TOULMIN** — claim / grounds / warrant / backing / qualifier / rebuttal, used for the reviewed R2 warrant-defeater analogy.
- **WALTON** — argumentation schemes + critical questions (Walton, Reed & Macagno, *Argumentation Schemes*, 2008).
- **SF** — S&F, *Understanding Arguments*, 9th ed.: the four fallacy families, the validity/strength/soundness axis, and the p.333 four-way refutation taxonomy.
- **WACHSMUTH** — logic/rhetoric/dialectic argument-quality dimensions (Wachsmuth et al. 2017, ACL P17-2039; GAQCorpus, Lauscher et al. 2020) — the vocabulary voiceprint's `argquality` emits.

## Cardinality legend

`exact` (same thing) · `broader` (internal ⊃ external) · `narrower` (internal ⊂ external) ·
`related` (related, neither) · `unmapped` (no reference-set target applies — **rationale required**).

An `unmapped` row is a reviewed present-tense conclusion that no confident target in the
reference set denotes that diagnostic failure. It is visible rather than silently blank, but it
is not a quota or an instruction to force a future equivalence.

## What "valid" means — and what it does not

`argument-crosswalk-check` (in `scripts/argument_crosswalk.py`, run by
`validate.sh --check-all`) certifies **shape**: membership completeness against a set *derived*
from the live registry (never a hardcoded copy — the verdict/flag/FM-A slices import
`argument_groundtruth.py`'s owners, the DC codes + schemes are parsed structurally from
`dialectical-clarity.md`), family well-typing, the cardinality enum, the `unmapped ⇔ no-targets`
equivalence, a non-empty rationale on every `unmapped` row, a provenance locator on every
populated target, a global non-injectivity floor, and the closed external-ref value-spaces.

It **does not** certify that a mapping is *scholarly correct* — whether a scheme, critical-question
number, S&F family, or Wachsmuth dimension is the *right* one, whether a cardinality is accurate
rather than over-strong, or whether a `prov` citation is real. That is **human/Codex-adjudicated**.
Downstream work (R2–R5) must treat the crosswalk content as **reviewed, not proven** — cite the
PR review, not "CI is green." See the ADR "firewall" section.

## Extending it

Edit `crosswalk.json` directly (it is a hand-maintained answer key, not generated). Adding a
target: give it a `vocab` from the four above, a `ref` inside that vocab's closed value-space
(see `scripts/argument_crosswalk.py` §3a constants), a per-target `cardinality`, and a `prov`
`{work, loc, id}` locator. Set the row `cardinality` to the strongest target's. To resolve an
`unmapped` row, replace `targets: []` + `rationale` with real targets. Re-run
`python3 scripts/argument_crosswalk.py argument-crosswalk-check` before committing.
