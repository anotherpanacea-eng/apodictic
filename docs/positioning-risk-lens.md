# Positioning-Risk Lens — the diagnostic sibling of marketability (mostly already built)

**Status:** Proposed (unbuilt), and **deliberately thin**. Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) "Reconsidered from the boundary," item 14. Proposed implementation surface: a `specialized-audits/references/positioning-risk.md` consolidation module, `apodictic.positioning_risk.v1` blocks, a `[Project]_Positioning_Risk_Register_[runlabel].md` artifact, a `scripts/positioning_risk.py` validator, `validate.sh positioning-risk`, and a worked example.

## The honest framing first: this is mostly already built

`ROADMAP.md` §Not Planned excludes "commercial viability **guarantees**" — not all market reasoning. And most of "positioning risk" already exists in the framework:

- **Pass 11C — Market Reality Check** (Market Evidence Rule, Required Outputs, **Shelf Positioning Gate**).
- **Pass 11D — First-50 Conversion Gate** (**Abandonment Risk Rating**, Promise Clarity Test).
- **Shelf & Positioning audit** — Evident vs. Intended Shelf, comps, Signal-Structure Mismatch / Contract Violation.

So a full new "positioning audit" would duplicate three existing surfaces — the same trap [Promise-Contract Fidelity](promise-contract-audit.md) and [Content-Advisory](content-advisory.md) had to escape. This spec therefore proposes **only the thin net-new residue**: (1) a single **consolidation register** that gathers the positioning-risk signals those surfaces already produce, and (2) a **mechanical risk-not-forecast boundary** that keeps the consolidated view strictly on the diagnostic side of the §Not Planned line. That boundary guard is the layer's real reason to exist; the consolidation is convenience.

If even that feels redundant in practice, the honest fallback is to record "#14 is covered by Pass 11C/11D + Shelf & Positioning" in the roadmap and build nothing — and this spec says so up front rather than inflating a near-duplicate.

## What the thin layer adds

- **One register, one scale.** The positioning-risk signals currently live scattered across Pass 11C, 11D, and the Shelf audit, each in its own prose. The register consolidates them into `apodictic.positioning_risk.v1` blocks on **one orthogonal risk scale** (`watch` / `notable` / `serious`), kept off the editorial Must/Should/Could scale (a positioning risk is not a manuscript defect — the Legal Risk / Content Advisory orthogonality precedent).
- **The risk-not-forecast boundary, made mechanical.** Pass 11 and the Shelf audit reason about the market in prose, which can drift toward prediction ("this won't sell," "agents will pass"). The register's validator (`PR3`) flags forecast/guarantee language, holding the consolidated view to *risk flags* (a structural mismatch with a category expectation) and never *outcomes*. This is the guard that lets market-adjacent reasoning exist without crossing the no-guarantees line.

## Consume-don't-duplicate — prose-only, honestly

Like Content-Advisory, the sources it consolidates (Pass 11C/11D outputs, the Shelf Memo) are **prose with no addressable per-instance IDs**. So Increment 1 consolidation is **prose-citation only**: a register entry names its source in prose (`source: "Pass 11C Shelf Positioning Gate"`), there is **no** structured cross-reference and **no** coverage cross-check that every Pass-11 risk became an entry. The register computes **no new market analysis** — if Pass 11C/the Shelf audit haven't run, it records the gap rather than inventing positioning judgments.

## The artifact

A `[Project]_Positioning_Risk_Register_[runlabel].md` of `apodictic.positioning_risk.v1` blocks:

```markdown
<!-- apodictic:positioning_risk
{
  "schema": "apodictic.positioning_risk.v1",
  "id": "PR-03",
  "source": "Shelf & Positioning — Signal-Structure Mismatch",
  "mismatch": "Inferred contract reads literary; the opening 50pp signal a thriller pace expectation the middle abandons.",
  "risk_level": "notable",
  "hedge": "A risk of reader-expectation mismatch, not a sales prediction; the author may reposition or hold."
}
-->
```

- `risk_level` ∈ `watch` / `notable` / `serious` — orthogonal to editorial severity (`PR2`).
- `mismatch` — the contract-vs-category-expectation gap (the diagnostic content).
- `source` — prose label of the consolidated origin (Pass 11C/11D / Shelf audit).
- `hedge` — the explicit risk-not-forecast caveat (`PR4`).

## Firewall & boundary compliance

- **Risk-flag, never forecast.** A register entry flags a *mismatch with a market expectation*; it never predicts sales, acquisition, or reception outcomes. `PR3` is the mechanical guard (forecast/guarantee phrase blocklist), and it is the layer's signature.
- **Never "chase the market."** The register flags the mismatch; it does **not** tell the author to change the book to fit the category (that is the author's call, and prescribing manuscript changes for market fit would brush the Firewall). It surfaces; the author decides to reposition or hold.
- **Orthogonal severity.** A positioning risk is not a defect; `PR2` guards against a Must/Should/Could token leaking in.

## The `positioning-risk` validator

`validate.sh positioning-risk <run_folder>` resolves the `*_Positioning_Risk_Register_*.md` artifact; no-ops with exit 2 if absent (the `legal_risk` pattern). Delegates to `scripts/positioning_risk.py`; degrades to advisory `WARN` without `python3`. Report lines namespaced `positioning-risk:<ID>`. Structurally a near-clone of `legal_risk.py` (flat-field schema, orthogonal severity, in-artifact phrase guards).

| ID | Severity | Rule |
|---|---|---|
| **PR1 — schema** | ERROR | Each `positioning_risk.v1` parses; `risk_level` ∈ {watch, notable, serious}; `source`/`mismatch`/`hedge` present. (Subset-engine enum + presence; non-empty-string is Python.) |
| **PR2 — no editorial-severity leak** | ERROR | No entry carries a Must/Should/Could token (positioning risk is orthogonal to editorial severity). |
| **PR3 — no forecast/guarantee (signature boundary)** | WARN (ERROR under `--strict`) | An entry matches a forecast/guarantee phrase set ("will/won't sell", "agents will pass/reject", "bestseller", "no market for", "guaranteed"). Holds the register to risk flags, not outcomes — the §Not Planned commercial-guarantees line made mechanical. Override `<!-- override: positioning-forecast PR-NN — quoting external market data, attributed -->`. Heuristic (narrow `_ADVICE_RE`-style regex), so advisory with `--strict` as the gate. |
| **PR4 — hedge present** | WARN (ERROR under `--strict`) | An entry lacks a `hedge` caveat. The explicit risk-not-forecast framing is part of the discipline; advisory. |

**Ownership boundary.** `positioning-risk` owns the **consolidated positioning-risk register + the risk-not-forecast boundary** — classes no other validator raises. It does **not** compute market reality (Pass 11C), abandonment risk (Pass 11D), shelf placement/comps (Shelf & Positioning), or pitch fidelity (`promise-contract`). It consolidates their prose outputs and enforces the boundary; it derives no new market analysis.

## Canonical `--check-all` gate

A worked example — a register with two entries citing Pass 11C and the Shelf audit in prose, each on the orthogonal scale with a hedge — is added, and `validate.sh --check-all` runs `positioning-risk` against it: proving schema/enum (`PR1`), no severity leak (`PR2`), a clean forecast scan (`PR3`), and hedge presence (`PR4`). It includes a **negative**: an entry saying "this won't sell" (fails `PR3` under `--strict`) and one carrying "Should-Fix" (fails `PR2`). (The "canonical-framework validator runs as release gate" discipline, `ROADMAP.md` §Deferred.)

## Increment plan

**Increment 1 (this spec):** the `apodictic.positioning_risk.v1` schema (added to `schemas/`, auto-discovered by `known_schema_ids()`), the `positioning-risk.md` consolidation module (gather Pass 11C/11D + Shelf risk signals in prose; no new market analysis), `scripts/positioning_risk.py` + `validate.sh positioning-risk`, the worked example, and the `--check-all` gate. Adds one validator (hand-maintained count bumped). **Gate before build:** if review finds the consolidation adds no value over Pass 11C/11D + Shelf, ship *only* the `PR3` boundary guard as a check on the existing Pass-11/Shelf prose, or record "#14 covered" and build nothing.

**Future increments (not built):**
- **Structured consolidation** — once Pass 11C/11D and the Shelf Memo emit ID-bearing risk blocks, add a real `source` ref + a coverage cross-check (every Pass-11 positioning risk became a register entry).
- **Positioning-risk visualization** — a category-expectation-vs-evident-signal chart via [Manuscript-Structure Visualizations](manuscript-visualizations.md).

## Self-review (Increment 1)

- *Why this is deliberately thin* — Pass 11C/11D and the Shelf audit already produce the positioning analysis; a full new audit would triplicate it. The only net-new is the single register + the mechanical risk-not-forecast boundary, and the spec says so rather than padding a near-duplicate into a "new capability."
- *Why `PR3` is the reason it exists* — market-adjacent reasoning is allowed (it's not a guarantee), but it drifts toward forecasting easily; a mechanical guard is what keeps a positioning register on the right side of §Not Planned. That guard is reusable even if the consolidation register isn't built.
- *Why consolidation is prose-only* — the sources are prose with no instance IDs (the Rule Ledger / sibling-audit problem), so structured consolidation would assert references they can't supply. Honesty over completeness, as with Content-Advisory.
- *Why severity is orthogonal* — a positioning mismatch is not a manuscript defect; mapping it onto Must/Should/Could would mislabel a deliberate market position as a flaw.
