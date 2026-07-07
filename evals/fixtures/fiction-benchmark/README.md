# Fiction Benchmark — Fixtures

Corpus-based validation for the Core Development Editor's fiction structural
passes. Each fixture pairs a short fiction text with a **pre-registered
ground-truth answer key** encoding the local structural diagnosis a competent
developmental editor already knows. Scoring uses
[../../rubrics/fiction-benchmark.md](../../rubrics/fiction-benchmark.md); the
design, corpus plan, multi-lane validity architecture, and convergence protocol
are in [../../../docs/fiction-benchmark-spec.md](../../../docs/fiction-benchmark-spec.md).

## Provenance rule

Fixtures fall in four provenance tiers (the same numbering used in the spec):

1. **Synthetic-or-derived** — text stored in-repo. The *derived-broken* fixtures
   are a low-recognition public-domain base with one pre-registered defect
   planted by minimal surgical edits; the clean member is the same base with no
   mutation. Provenance and the mutation registry live in `groundtruth.md`
   (**not** in `fixture.md` — see input hygiene). No copyrighted bytes, ever.
2. **Public-domain** — stored if short (Gilman, O. Henry), *referenced* by a
   pinned Gutenberg source + `run.sh --fetch` if long (Dickens). Key in-repo.
3. **Third-party published** — never stored; referenced by URL, key-only.
4. **Private / unpublished** — never stored, never named; gitignored manifest.

## Input hygiene (do not leak the answer key)

`fixture.md` is the **verbatim engine input: fiction text only, with no
provenance, mutation markers, slug, or diagnosis pointers.** Markdown/HTML
comments are still raw input — anything in a comment leaks the answer key (and,
for controls / clean members, their control status), so the benchmark could
"pass" by reading metadata instead of diagnosing. Therefore:

- All provenance and ground truth live in `groundtruth.md`, **never** fed to the engine.
- Feed the engine the *contents* of `fixture.md` plus a **neutral label** — do
  **not** pass the descriptive slug (`pov-break-broken` encodes the diagnosis).
- **The seam threat (craft-clean-splice review criterion):** a derived-broken
  `fixture.md` must read as *authored prose*, not a visible splice. If the graft
  scar / deletion roughness is detectable as a seam, a model can score a "hit" by
  detecting the surgery, not the developmental mechanism — measuring nothing. A
  build-time reviewer must confirm each mutation reads clean before the fixture
  is registered. (The matched-pair delta is the runtime backstop; craft-clean
  surgery is the design-time one.)
- **Fixtures must read complete.** Every fixture (clean and broken) presents as a
  complete short work and runs in complete-manuscript mode. Under
  `artifact=partial`, Pass 8 marks unresolved setups as *assets, not failures* —
  which would silently un-plant the unpaid-setup defect. An excerpt-shaped
  fixture cannot fail.

## Preparer step (deriving `fixture.md` at pin time)

To keep the repo free of pre-pinned base bytes, the **stored** members ship the
pre-registered `groundtruth.md` now; the preparer derives each `fixture.md` at
first retrieval, records the SHA-256 in `SOURCES.md`, and hands only the
extracted/mutated text to the blind runner — the same discipline the argument
benchmark uses for referenced fixtures. `groundtruth.md` is never opened by the
preparer or runner, only by the scorer, afterward. See
[SOURCES.md](SOURCES.md) for the base pins and
[RUN-PROTOCOL.md](RUN-PROTOCOL.md) for the three-role blindness discipline, the
canonical pass-set, the recognition probe, and the matched-pair delta.

## The slice (Increment 1: 4 matched pairs + 3 standalone controls = 11 members)

**Sensitivity — 4 matched pairs (8 members, tier-1 derived):**

| Pair | Bucket | Role | Planted defect (broken member) |
|------|--------|------|--------------------------------|
| `pov-break/` | P | sensitivity + its own control | POV break / head-hop / knowledge-leak in established third-limited |
| `continuity-contradiction/` | C | sensitivity + its own control | dual-mutated entity-fact contradiction + a timeline-arithmetic error |
| `unpaid-setup/` | R | sensitivity + its own control | emphatic setup, payoff scene excised (dropped thread) |
| `orphan-scene/` | S | sensitivity + its own control | one causally-inert scene inserted (removable without causal break) |

**Specificity — 3 standalone intentional-device controls:**

| Slug | Bucket(s) | Role | Registered trap (FQ7) |
|------|-----------|------|------------------------|
| `yellow-wallpaper-voice-control/` | P (+S) | positive control, stored | intentional unreliable-narrator voice deterioration — not a POV/voice defect |
| `gift-of-magi-reveal-control/` | R | positive control, stored | fair twin-reveal — not unfair misdirection |
| `christmas-carol-arc-control/` | S + arc pilot | positive control, **referenced** | five-stave episodic structure + compressed arc — not "missing act structure" / "rushed arc"; FGT5 arc pilot (Lane-2/B) |

The clean member of each matched pair **is** that bucket's positive control (a
better control than a separate work — byte-for-byte the broken member minus one
mutation). The three standalone controls add intentional-device traps a clean
base cannot exercise. A false-positive trap fired as Must-Fix on any control (or
a clean member) is FQ7 = 0 and blocks the bucket.

## Layout per fixture

```
<pair-slug>/
  clean/
    groundtruth.md    # pre-registered answer key — records "no mutation"; the control
    fixture.md        # (preparer-derived at pin time) verbatim engine input, no metadata
  broken/
    groundtruth.md    # pre-registered answer key + mutation registry
    fixture.md        # (preparer-derived) the base minus/plus one mutation
<control-slug>/
  groundtruth.md      # pre-registered answer key
  fixture.md          # (stored controls) or omitted (referenced control — see SOURCES.md)
```

## Adding fixtures

Copy [../../fiction-groundtruth-template.md](../../fiction-groundtruth-template.md)
to `<slug>/groundtruth.md` and fill every in-scope field **before** scoring any
run. Every derived-broken fixture ships a matched clean member (D-1). Run
`scripts/validate.sh fiction-groundtruth-check <slug>/groundtruth.md` to
key-conformance-check it (`--check-all` runs the whole registered corpus).
