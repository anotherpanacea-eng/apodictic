# Positioning-Risk Lens — finding: covered by existing surfaces, do not build

**Status:** **Will not build (Increment 1).** Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) "Reconsidered from the boundary," item 14. This document records *why* — it is a decision record, not a build spec. (It began as a thin-layer spec; adversarial review found even the thin layer is redundant and its one net-new guard non-viable. Recording the finding so the question stays closed until a forcing function reopens it.)

## The decision

**Positioning risk is already covered**, three times over, by surfaces that ship today:

- **Pass 11C — Market Reality Check** produces a **Submission Friction List** (top objections) + a Commercial Snapshot, behind the **Shelf Positioning Gate** (`pass-11.md §Sub-Pass 11C`).
- **Pass 11D — First-50 Conversion Gate** produces an **Abandonment Risk Rating** + Promise Clarity Test (`pass-11.md §Sub-Pass 11D`).
- **Shelf & Positioning audit** produces a **Risks & Considerations** section, a **Flags Raised** checklist, and a **Risk Profile** table (`shelf-positioning.md` Shelf Memo / Acquisition Brief).

A new consolidation register would be a fourth, prose-only restatement of risks already surfaced in three deliverable sections — convenience at best, and (per below) net-negative.

## Why the one net-new idea is non-viable

The thin layer's stated reason to exist was a **risk-not-forecast boundary guard** (`PR3`): a blocklist firing on "agents will pass/reject", "won't sell", etc., to keep market reasoning on the diagnostic side of `ROADMAP.md` §Not Planned. Review showed this is built on a false premise:

1. **The §Not Planned line is *guarantees*, not *predictions*.** It excludes "commercial viability **guarantees**"; item 14 itself says "flags *risk*, never promises *outcomes*." Predictions and likelihood statements are **not** over that line.
2. **The framework deliberately produces acquisition-style predictions as canonical, firewall-approved output.** Pass 11 is framed around "Would it sell?"; its "Hard Truths" model output includes *"Most agents would stop reading by page 20"*; its Non-Negotiable Consequence format is literally *"Agents will reject because…", "Readers will abandon at…"*; and its ALLOWED list includes "Commercial viability analysis."
3. **Therefore `PR3` would flag the framework's own approved output.** A register entry faithfully consolidating a Pass-11C/11D finding would trip the forecast blocklist — and the "fallback" of pointing `PR3` at the existing Pass-11/Shelf prose is the worst option: it would generate false-positive WARNs against the canonical examples and could break `--check-all` if those were ever gated.

`PR3` polices *predictions*; the actual boundary is *guarantees*. It overshoots, and it overshoots onto sanctioned output.

## The only defensible salvage (folded elsewhere, not built here)

The narrow, real boundary — outright **guarantees** ("guaranteed bestseller", "guaranteed to sell", "no market for X, period") — is so small and so close to the phrase set [Promise-Contract Fidelity](promise-contract-audit.md) already specifies for its `W2` market-prediction-drift guard that, if wanted, it belongs as a one-or-two-phrase **extension to `promise-contract` W2**, not as a new validator + schema + register + module + worked example + validator-count bump. No standalone capability is warranted.

## What would reopen this

Build only if a forcing function appears that the three existing surfaces genuinely cannot serve — e.g., a demand to *aggregate positioning risk across many manuscripts* (a portfolio view), which is a different artifact from any single-manuscript Pass-11/Shelf output. Absent that, item 14 stays closed.

## Process note

This is the disciplined outcome of the spec→review loop working as intended: the review's BUILD-vs-DON'T-BUILD gate caught a capability that *sounded* near-buildable (it was flagged "not that far away from things we'd build") but, on inspection, was already built and whose one novel guard contradicted the framework's own approved behavior. Recording the don't-build keeps the idea from being re-proposed from scratch.
