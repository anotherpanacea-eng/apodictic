### Validators — the contradiction State axis (world-bible + continuity-bible)

Both bible Contradiction Ledgers now carry a **`State` column** — the contradiction *fact-state*
axis, orthogonal to the editorial Must/Should/Could severity scale: a self-contradiction is a
fact-state, not a defect, so it is never forced onto the severity scale (the same discipline Legal
Risk's escalation tier and Content Advisory's intensity follow). Values: `conflicting` (a live,
un-explained collision), `apparent` (a collision an override marks intentional), `consistent` (no
collision — never written as a row). **No new schema** — the column rides the existing plain-markdown
`## Contradiction Ledger`, parsed like continuity-bible's bespoke `C3` table parse.

The state is **mechanically derived, never model-judged**: a new shared helper
`scripts/contradiction_state.py` (`derive_state` — no collision → `consistent`; collision + matching
override → `apparent`; else → `conflicting`), imported by both `world_bible.py` and
`continuity_bible.py`. World-bible reuses its live `world-rule` / `world-cost` / `world-geo` per-pair
override markers; continuity-bible gains a new `bible-contradiction CF-NN/CF-MM` pair override (order-
insensitive, code-span-hardened via the `override_marker` SSoT; distinct from the `bible-rederive` C4
escape hatch). A new **`X1` firewall arm on the existing `world-bible` / `continuity-bible` validators**
(no new `AGG_VALIDATORS` entry) proves the register carries no `apodictic:finding` block and no
editorial-severity token, and that each `State` value is a valid enum token that **matches** the
mechanical derivation — an author-asserted state disagreeing with the fire/override reality FAILs
(ERROR). `conflicting` rows are surfaced for the editorial letter to cite **in prose** (Stage A wiring
— the Legal-Risk / Content-Advisory / Setup–Payoff precedent), so an unresolved self-contradiction
reaches the author's revision plan; an `apparent` (overridden) row is intentional and is not cited.

Both canonical `--check-all` fixtures now exercise the axis: `example-continuity-bible.md` carries a
`conflicting` Mara-age row and an `apparent` overridden kitchen-repaint row;
`example-worldbuilding-bible.md`'s two staged rows both derive `apparent`. Hostile self-test negatives
on both validators: a planted severity token (X1 FAIL), a planted `apodictic:finding` block (X1 FAIL),
an author-asserted State contradicting the derivation (FAIL), a `consistent` row written at all (FAIL),
a bad enum token (FAIL), and a code-span-quoted override that must not silence (FAIL). Dual-script
mirror byte-identical; the self-testable validator count is unchanged (arms-on-existing, not a new
validator).

**Fold hardening (review + code-scan follow-up).** The `X1` arm now also enforces **ledger-row
referential integrity**: over every ledger data row (all rows, pre-axis included), each row must pair
at least two *distinct* `WF-NN` / `CF-NN` ids that each resolve to a real, well-formed `world_fact` /
`canon_fact` block — a fabricated id or a single-id row FAILs (`X1 ledger integrity`) and, crucially,
never reaches the `conflicting`-row prose rollup, so a phantom contradiction can no longer be cited
into the editorial letter. **Codex-P1 hardening (world-bible), R1(b″):** the `X1` ledger-integrity
check now runs a single **identity** leg as a pure field recompute over the parsed `world_fact` blocks —
a row FAILs only when its cited facts all record the SAME normalized `(subject, value, polarity, cost)`
tuple (Codex's exact repro: two identical `place` facts labeled `conflicting`, which previously passed
clean and rolled up a phantom contradiction into the letter; it now FAILs `X1 ledger integrity` and
never reaches the rollup). **A world's collision universe is arm-defined, not subject-defined**, so
**cross-subject rows are LEGAL** — the geo arm already collides facts about different subjects (WB-G1's
reversed-distance edge `A→B` vs `B→A`, WB-G2's chronology cycle `A→B→C→A`). Round-1 (R1(b′)) added a
same-subject leg that wrongly imported continuity C3's schema and rejected both of those legitimate geo
shapes; R1(b″) **drops the same-subject leg entirely** (a round-2 Codex P1 — the round-1 fix's own
tests had encoded the overcorrection by pinning cross-subject-FAILs). Identity is the only relation
that mechanically precludes a collision; every non-identical pairing is the author's declared tension.
No arm restructuring and no semantic judgment — the register-neutral leg does not adjudicate whether
the facts truly collide (that stays the author's call). A ledger with data rows
but **no `State` column** is now a **loud pre-axis WARN** (ERROR under `--strict`) rather than silent —
the additive column is nudged, not forced. And the shared `contradiction_state.py --self-test` (the
truth-table / State-column-parse / `Statement`-decoy / X1-regex cases), previously invoked by nothing
in CI, is now wired into `continuity-bible --self-test`, so it runs under `--self-test-all`.

Anchors the axis on *Lost in Stories: Consistency Bugs in Long Story Generation by LLMs*
(Li, Guo, Wu, Lee, Li, Xie), **arXiv:2603.05890** (ConStory-Bench / ConStory-Checker — the
factual/temporal, mid-narrative contradiction taxonomy that confirms a contradiction is a locatable
fact-state) and *DOME* (**arXiv:2412.13575**) — taxonomy and benchmark only: APODICTIC's detection
stays mechanical (literal collision + override), never LLM-as-judge, the same "cite the benchmark,
don't glassbox the method" line drawn for StoryScope and Setup–Payoff. Stage B (single-substrate
merge, one fact schema, a structured `contradiction_ref` on `finding.v1`) and Stage C (the Timeline
fold) are explicitly deferred — the pre-draft *intent* vs post-draft *reality* split is load-bearing,
and Timeline's model-authored LOW/UNCERTAIN confidence rows do not fit a mechanical register.
