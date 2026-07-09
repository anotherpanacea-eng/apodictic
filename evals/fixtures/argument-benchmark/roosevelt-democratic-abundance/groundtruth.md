# Ground Truth: roosevelt-democratic-abundance

## Provenance

- **Fixture slug:** roosevelt-democratic-abundance
- **Bucket:** 2 policy brief · **Cluster:** A (abundance debate) · stance: pro-reframe (left)
- **Source class:** third-party published — **referenced (text NOT stored; copyright)**
- **Work:** Roosevelt Institute, "Democratic Abundance: An Abundance That Works for Workers."
- **Pinned source:** https://rooseveltinstitute.org/publications/democratic-abundance/ (record retrieval date + a content hash of the fetched text on first authoritative run; analyzed-text extraction anchors (START / END / EXCLUDE) in [../SOURCES.md](../SOURCES.md)).
- **Quotation policy:** paraphrase only — do not reproduce the source text.
- **Ground-truth authority:** Joshua A. Miller (editor), independent diagnosis registered 2026-05-30, before any engine run.
- **Scope:** GT1–GT3 are authoritative (from the registered diagnosis). **GT4–GT8 are PROVISIONAL** (benchmark-author mapping; confirm on run or by a second editor).
- **Reliability:** GT1–GT3: authoritative, gate; GT4–GT6: provisional, confirm; GT7: provisional, confirm; GT8: provisional, report

## GT1 — Main claim *(Q1)*

- **Expected C0:** "Abundance politics should be rebuilt around democracy, labor, and public capacity rather than deregulation."
- **Acceptable paraphrase band:** any recovery of *redefine/reclaim abundance around democratic participation + workers + public capacity (against a deregulatory version)* is a hit. Recovering "we need more housing/energy" as the claim is a miss — that's the shared premise, not this piece's claim.

## GT2 — Failure locus *(Q2)*

- **Main structural problem (authority):** an unearned warrant that **organized labor as it actually is** can deliver *democratic abundance* (democratic participation + speed/scale + worker power) at once. The load-bearing bridge from "center labor" to "get abundance" is asserted more than earned.
- **Primary failure layer:** WARRANT.
- **Acceptable locus set (any ONE is a GT2 hit — facets of the one unearned warrant):**
  1. **Participation ↔ speed reconciliation:** the principle reconciling "more participation" with "faster delivery" is asserted, not earned.
  2. **Current ↔ reformed labor (motte-and-bailey):** the support describes an idealized/reformed, internally-democratic labor movement, while the conclusion must hold for labor as it is (which carries the cost/veto behavior the abundance critique targets). Bailey: "organized labor delivers abundance"; motte: "a reformed labor movement could."
- **Provisional codes:** WR1 (contested warrant, thin backing) / WR0; DI4 where the current/reformed oscillation is named; FM-A13 (Structural Motte-and-Bailey) candidate, Relational.
- **Boundary (NOT a GT2 hit):** routing the primary structural break to the objection/burden layer — e.g. "the moderate alternative is uncompared" (BP/OB) — locates a real but downstream issue, not the warrant gap. The locus must be the WARRANT bridge from labor to abundance-outcomes.
- **Amended 2026-06-04 (ratified, post-run):** original single-answer registration (participation↔speed) preserved as set member #1; member #2 + boundary added per [../PROPOSAL-gt-sets-20260604.md](../PROPOSAL-gt-sets-20260604.md).

## GT3 — Strongest real objection *(Q3)*

- **Objection zone (authority):** the proposed safeguards may **recreate the procedural veto points** that abundance critiques target — the remedy reintroduces the diagnosed problem.
- **Provisional codes:** OB3 (the strongest self-undermining objection is the one the piece most needs to engage).

## GT4 — Audience calibration *(Q4 — PROVISIONAL)*

- **Audience profile:** Expertise MIXED-EXPERT · Receptivity SYMPATHETIC→MIXED (progressive policy readers) · Consequence MEDIUM-HIGH.
- **Improve:** attending to a sympathetic-but-skeptical-of-feasibility audience should foreground the participation-vs-speed reconciliation as the decisive burden.
- **Distort:** do not accept the reframe as established because it is congenial to the audience (AC3 risk).

## GT5 / GT6 — *(PROVISIONAL — derive on run)*

- **GT5 red-team:** load-bearing vulnerability = the safeguards/veto-point regress (GT3). Decoy = quibbles over specific program names.
- **GT6 repair order:** first target = the reconciling **warrant** (how participation and speed coexist) before adding more benefit/feasibility evidence.

## GT7 — Warrant verdict *(Q7 — PROVISIONAL; calibration anchor)*

- **Expected warrant verdict:** WARRANTED (a competent reframe with a real internal tension = Should-Fix), **not UNWARRANTED.**
- **Calibration trap:** over-pathologizing — firing the participation/speed tension as a systemic Must-Fix or declaring the argument incoherent. The tension is a genuine soft spot, not a collapse.

## GT8 — Premise-plausibility flags
- **Expected premise flags:** NONE_REGISTERED (provisional migration default)
- **Must not adjudicate:** whether abundance can, in practice, be delivered by centering democracy, labor, and public capacity rather than deregulation.

## Notes

Cluster-A contrast: this is the *constructive/pro* stance and its weakness is a **warrant tension**, distinct from the support-mismatch (Current Affairs), frame-assumption (Reason), and scope-bundling (Cato) weaknesses in the other three. An engine that reports the same failure on all four has not recovered the structure.
