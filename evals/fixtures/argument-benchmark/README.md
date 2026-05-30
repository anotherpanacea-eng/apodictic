# Argument Engine Benchmark — Fixtures

Corpus-based validation for the Nonfiction Argument Engine. Each fixture pairs
argument-shaped text with a **pre-registered ground-truth answer key**
encoding the diagnosis a competent editor already knows. Scoring uses
[../../rubrics/argument-benchmark.md](../../rubrics/argument-benchmark.md);
the design, corpus plan, and convergence protocol are in
[../../../docs/argument-benchmark-spec.md](../../../docs/argument-benchmark-spec.md).

## Provenance rule

In-repo fixture *text* is **synthetic-or-derived** or **public-domain** only,
per the fixture-provenance policy. Synthetic fixtures are clearly marked in an
HTML comment header and reference no real person, place, or source. Real
modern manuscripts are never stored here — they are referenced by gitignored
manifest (`evals/manifests/*.md`).

## Vertical slice (Increment 1)

| Fixture | Bucket | Role | Planted diagnosis (primary) |
|---------|--------|------|------------------------------|
| `op-ed-warrant-leap/` | 1 op-ed | failure detection | FM-A6 Warrant Leap — support is sound, the **bridge** is missing (Q2: SUPPORT vs WARRANT) |
| `policy-brief-uncompared/` | 2 policy brief | failure detection + Q5/Q6 anchor | FM-A10 Uncompared Proposal + BP5 + FM-A18 — benefits evidenced, **comparative burden** unmet |
| `personal-essay-narrative-arg/` | 4 personal essay | **positive control** | UNCONVENTIONAL-BUT-EFFECTIVE — argument recoverable through juxtaposition; no-thesis "failure" must be downgraded |
| `modest-proposal-satire/` | 6 / Q7 hard case | **positive control, referenced** | UNCONVENTIONAL-BUT-EFFECTIVE — Swift, *A Modest Proposal* (1729); sustained irony; text not stored |

The two broken fixtures test **sensitivity** (does the engine catch real
failures and locate them in the right layer?). The two positive controls test
**specificity** (does it leave sound-but-unconventional arguments alone?). A
false-positive trap fired on a control is Q7 = 0 and blocks the bucket.

## Layout per fixture

```
<fixture-slug>/
  fixture.md       # the argument text (omitted when text is referenced, not stored)
  groundtruth.md   # pre-registered answer key — GT1–GT7; see ../../argument-groundtruth-template.md
```

## Running a fixture

1. Route the text through nonfiction intake (→ Dialectical Clarity) or invoke
   `/audit dialectical-clarity` directly. For referenced fixtures, fetch the
   source named in `groundtruth.md` first.
2. Run the companion modules the fixture's GT scope requires (Red Team for
   Q5, Revision Coach argument mode for Q6).
3. Capture the editorial letter + `Argument_State.md` (+ companion artifacts).
4. Score the seven dimensions against `groundtruth.md` using the rubric.
5. Synthetic and public-domain run outputs may be stored in-repo; private-fixture
   outputs go to the gitignored `evals/results/` path.

## Adding fixtures

Copy [../../argument-groundtruth-template.md](../../argument-groundtruth-template.md)
to `<slug>/groundtruth.md` and fill every in-scope field **before** scoring any
run. Each bucket must include at least one positive control. Register the
fixture in the review log with its bucket, source class, and intended use.
