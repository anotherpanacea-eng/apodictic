# Argument Engine Benchmark — Fixtures

Corpus-based validation for the Nonfiction Argument Engine. Each fixture pairs
argument-shaped text with a **pre-registered ground-truth answer key**
encoding the diagnosis a competent editor already knows. Scoring uses
[../../rubrics/argument-benchmark.md](../../rubrics/argument-benchmark.md);
the design, corpus plan, and convergence protocol are in
[../../../docs/argument-benchmark-spec.md](../../../docs/argument-benchmark-spec.md).

## Provenance rule

Fixtures fall in four provenance tiers (the same numbering used in
[CORPUS.md](CORPUS.md) and the spec):

1. **Synthetic** — text authored here and stored in-repo. Synthetic provenance
   and the "do not quote as a real-world source" note live in each fixture's
   `groundtruth.md` (**not** in `fixture.md` — see input hygiene below);
   synthetic fixtures reference no real person, place, or source.
2. **Public-domain** — text not stored; *referenced* by a pinned source (e.g.,
   Swift via Project Gutenberg); key in-repo.
3. **Third-party published** (Coates, a16z, Cato, …) — text **never stored**
   (copyright); *referenced* by public URL, key (citation + diagnosis, no source
   text) in-repo. Naming and analyzing published, attributed works is ordinary
   scholarship. Quotation policy: **paraphrase only**. Registered in
   [CORPUS.md](CORPUS.md).
4. **Private / unpublished / client manuscripts** — never stored and never named
   in-repo; referenced by gitignored manifest (`evals/manifests/*.md`).

## Input hygiene (do not leak the answer key)

`fixture.md` is the **verbatim engine input: argument text only, with no
provenance, synthetic markers, slug, or diagnosis pointers.** Markdown/HTML
comments are still raw input — if the file is fed to the engine, anything in a
comment leaks the answer key (and, for positive controls, their control status),
so the benchmark could "pass" by reading metadata instead of diagnosing.
Therefore:

- All provenance and ground truth live in `groundtruth.md`, which is **never**
  fed to the engine.
- Feed the engine the *contents* of `fixture.md` plus a **neutral label** — do
  **not** pass the descriptive fixture slug (e.g., `warrant-leap`) to the engine
  as a title or prompt, since the slug also encodes the diagnosis.
- When adding a fixture, keep `fixture.md` metadata-free from the start.

## Vertical slice (Increment 1)

| Fixture | Bucket | Role | Planted diagnosis (primary) |
|---------|--------|------|------------------------------|
| `op-ed-warrant-leap/` | 1 op-ed | failure detection | FM-A6 Warrant Leap — support is sound, the **bridge** is missing (Q2: SUPPORT vs WARRANT) |
| `policy-brief-uncompared/` | 2 policy brief | failure detection + Q5/Q6 anchor | FM-A10 Uncompared Proposal + BP5 + FM-A18 — benefits evidenced, **comparative burden** unmet |
| `personal-essay-narrative-arg/` | 4 personal essay | **positive control** | UNCONVENTIONAL-BUT-WARRANTED — argument recoverable through juxtaposition; no-thesis "failure" must be downgraded |
| `modest-proposal-satire/` | 6 / Q7 hard case | **positive control, referenced** | UNCONVENTIONAL-BUT-WARRANTED — Swift, *A Modest Proposal* (1729); sustained irony; text not stored |

The two broken fixtures test **sensitivity** (does the engine catch real
failures and locate them in the right layer?). The two positive controls test
**specificity** (does it leave sound-but-unconventional arguments alone?). A
false-positive trap fired on a control is Q7 = 0 and blocks the bucket.

### Referenced real corpus (severity calibration)

Ten published arguments (Coates, Andreessen, Amodei, Bender et al., AECF, PPI,
and the four-way abundance debate) are registered in [CORPUS.md](CORPUS.md) with
an independent editor's diagnoses as ground truth. Text is not stored
(referenced by URL); they test whether the engine resists *over-pathologizing* a
competent argument. To run them, follow [RUN-PROTOCOL.md](RUN-PROTOCOL.md) in a
web-enabled session.

[`run.sh`](run.sh) automates the blind-runner step (Protocol §1–2): point `SRC`
at your local cache of the source texts, and it inlines each argument + the audit
reference into a tools-disabled prompt and runs two model configs (the two
independent runs). It never touches `groundtruth.md` — scoring stays a separate
step. `./run.sh --verify` just checks the cache against the SOURCES.md hashes;
`./run.sh <slug>...` runs a subset. Read the header comment before first use —
two vars (`SRC`, and possibly `CLAUDE_TOOL_FLAGS`/`STRIP_CMD`) may need matching
to your setup.

## Layout per fixture

```
<fixture-slug>/
  fixture.md       # verbatim engine input: argument text ONLY, no metadata/comments
                   #   (omitted when text is referenced, not stored)
  groundtruth.md   # pre-registered answer key + provenance — GT1–GT7; never fed to the engine
                   #   see ../../argument-groundtruth-template.md
```

## Running a fixture

1. Route the text through nonfiction intake (→ Dialectical Clarity) or invoke
   `/audit dialectical-clarity` directly. Feed the engine the *contents* of
   `fixture.md` with a neutral label (not the slug) — see Input hygiene above.
   For referenced fixtures (text not stored), follow [RUN-PROTOCOL.md](RUN-PROTOCOL.md):
   the **preparer** reads only [SOURCES.md](SOURCES.md) (URL + extraction anchors
   + hash — never `groundtruth.md`), extracts the analyzed text, records the
   SHA-256 in that source's `RECORDED` block in `SOURCES.md`, and hands **only
   the extracted text** to the blind runner. `groundtruth.md` is never opened by
   the preparer or runner — only by the scorer, afterward.
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
