# APODICTIC Evals

Fixture manifests, rubrics, and comparison protocols for testing prompt and harness changes.

## Layout

- `manifests/` — fixture metadata. Each manifest describes a fixture, names its source class and permission status, and points to where the fixture content lives. Manifests are in-repo.
- `rubrics/` — scoring references for core developmental-edit output, synthesis, and audit routing. In-repo.
- `fixtures/` — public fixture content (rare). Private fixture content lives under gitignored paths (`Outputs/Hybrid_Test/`, `Outputs/blind-review/`, etc.) and is referenced by manifest only.
- `results/` — eval run outputs. Currently gitignored by default; move specific results in-repo only after the fixture-provenance policy for that fixture permits it.

Eval mechanics (metrics, decision rules, binary checks, failure attribution) are defined in [../docs/eval-harness-spec.md](../docs/eval-harness-spec.md). Blind-review packet format is in [../docs/blind-review-protocol.md](../docs/blind-review-protocol.md). Both are gitignored per the 2026-04-24 review planning; see [../docs/review-log/](../docs/review-log/) for phase-transition entries.

## Adding A Fixture

1. Copy `fixture-manifest-template.md` to `manifests/<fixture-slug>.md`.
2. Fill in every field. Empty fields block fixture use.
3. Confirm source class and permission status match the [fixture provenance policy](../docs/eval-harness-spec.md#fixture-provenance-policy).
4. If the fixture is private, do not store text in `evals/fixtures/`. Store locally under `Outputs/` or reference external storage in the manifest.
5. Add the fixture to the review log with source class and intended use.
