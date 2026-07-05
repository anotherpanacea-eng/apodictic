# Setup–Payoff Ledger — referential completeness for foreshadowing

**Status:** **Built (Stage A), 2026-07-05.** Shipped: the `apodictic.setup_payoff.v1` (foreshadow) + `apodictic.payoff.v1` (resolving payoff) schemas, the `core-editor/references/setup-payoff-ledger.md` extraction module, `scripts/setup_payoff_checks.py` + `validate.sh setup-payoff` (SP1–SP4 + X1), and the canonical `example-setup-payoff-ledger.md` (three valid states, an abandoned row surfaced for prose citation) wired into `--check-all` under `--strict`. Self-testable validators count is **derived** from `validate.sh`'s `AGG_VALIDATORS` list — adding `setup-payoff` to that list is the whole count change. Homed in core-editor as a **derived deliverable** (like the Continuity Bible), not a routed audit. Anchor paper: *Codified Foreshadowing-Payoff Text Generation* (Yun, Zhou, Hou, Peng, Shang), **arXiv:2601.07033**.
<!-- built-when: scripts/setup_payoff_checks.py -->

## Why

The ConStory-Bench taxonomy triage (arXiv:2603.05890) surfaced the one contradiction/craft row APODICTIC had no mechanical home for: **"Abandoned Plot Elements"** — introduced narrative elements never resolved (setup without payoff). Every other ConStory row rides an existing surface (world-bible facts, the Timeline, the continuity ledger). This closes that gap with a mechanical Setup–Payoff Ledger, anchored on the foreshadowing-payoff literature.

**Anchor paper — arXiv:2601.07033.** *Codified Foreshadowing-Payoff Text Generation* defines the **Foreshadow → Trigger → Payoff (F→T→P) triple**: F = the initial setup / narrative anomaly that establishes a **"causal debt"**; T = the prerequisite narrative condition that activates it; P = the concluding event that **fulfils** the commitment. A commitment left with its payoff never realized is **abandoned** — the defect. (Corpus: 629 validated foreshadow-payoff pairs from 148 BookSum-derived books; code at github.com/LongfeiYun17/CFPG.)

**Posture caveat — cite the concept, do NOT adopt the method.** CFPG's *detection* is LLM-judged (GPT-4.1 extraction + verifier models) despite its "executable predicates" framing. APODICTIC's Firewall is mechanical / no-model, so we take the **F→T→P schema** and the **causal-debt / abandoned framing**, but the validator gate does **referential-completeness only** — the model authors the *extraction* (marks the triples), never the *verdict*. This is the exact line drawn for StoryScope, homogenization, and ConStory.

## The firewall: extract the marked triple, never author the verdict

- **The model marks; the validator derives.** The model authors each Foreshadow → (Trigger) → Payoff extraction. The validator resolves `payoff_ref` and **derives** the `state` deterministically (§Derivation) — an author-written `state` that disagrees with the derivation FAILs (SP4). No model judgment enters the gate.
- **Never invents a payoff.** The tool records the author-marked `payoff_ref` and checks it resolves; it does not decide whether a given passage "counts" as a payoff. That semantic call is the deferred SETEC-consumer job (see §Out of scope).
- **No severity in the register (X1).** The Ledger carries no `apodictic:finding` block and no Must/Should/Could-Fix token (the Content-Advisory A3 firewall applied here, scanning the raw artifact like world-bible's firewall). Severity, if any, is owned downstream by promise-contract.

## The artifact

A `[Project]_Setup_Payoff_Ledger_[runlabel].md` of `apodictic.payoff.v1` and `apodictic.setup_payoff.v1` blocks, plus a `## Setup–Payoff Ledger` markdown table for the reader-facing rollup. Each foreshadow block:

```markdown
<!-- apodictic:setup_payoff
{"schema":"apodictic.setup_payoff.v1","id":"SP-01","foreshadow":"…","anchor":["Ch 1 §2"],"trigger":"…","payoff_ref":"PO-03","state":"paid_off"}
-->
```

and each resolving payoff:

```markdown
<!-- apodictic:payoff
{"schema":"apodictic.payoff.v1","id":"PO-03","payoff":"…","anchor":["Ch 9 ¶4"]}
-->
```

`trigger` is **optional free-text** — CFPG's activation condition, recorded but **not gated** (completeness is F↔P; T is context). `payoff_ref` is a `PO-NN` id or the empty string. `open_rationale` is **required (non-empty) when `state` is `open`** (SP3).

## The three-state axis

Each foreshadow carries a mechanically-derived **state**, orthogonal to editorial severity (mirrors the Continuity Bible's `consistent/conflicting` axis):

- **`paid_off`** — a resolving payoff block exists and the foreshadow references it.
- **`open`** — deliberately unresolved, carrying a rationale (a series thread, an intentional ambiguity). Flagged, not a defect.
- **`abandoned`** — no resolving payoff **and** no `open` rationale. The causal debt left unpaid — the "Abandoned Plot Elements" signal.

## Derivation (§D4 truth table — no model in the gate)

The validator DERIVES `state` from the resolved refs; SP2 resolves `payoff_ref` *before* derivation runs.

| `payoff_ref` | `open_rationale` | derived `state` |
|---|---|---|
| non-empty **and resolves** (SP2 pass) | any | **`paid_off`** |
| non-empty **but phantom** (SP2 FAIL) | any | *validation error (SP2), state not derived* |
| empty | non-empty | **`open`** |
| empty | empty | **`abandoned`** |

(`paid_off` with a non-empty `open_rationale` is legal — the rationale is ignored once a payoff resolves.)

## The checks

- **SP1 schema** — every `setup_payoff.v1` / `payoff.v1` block validates (SP-NN / PO-NN ids, required fields, `state` enum, unique ids, valid JSON, closed-key) **and its `anchor` entries are coarse manuscript loci** (a chapter / §section / ¶ / line / page token — not a blank or a prose description; the schema alone accepts `[""]` / `["the kitchen"]`, and the abandoned-row report cites `anchor[0]` as the prose locus). Mirrors the Continuity Bible's C2.
- **SP2 referential integrity** — a non-empty `payoff_ref` must id-match an existing `payoff.v1` block in the same run. Forward-only; **N:1 allowed** (many foreshadows → one payoff); a payoff with no foreshadow is not flagged here (the inverse is deferred Stage B). A phantom ref FAILs.
- **SP3 open rationale** — an `open` state must carry a non-empty `open_rationale`.
- **SP4 derived state** — the declared `state` must match the derived state (§Derivation). SP2 owns a phantom ref, so a paid_off with a phantom ref reports SP2 only, never a double SP4 mismatch.
- **X1 firewall** — the artifact carries no `apodictic:finding` block and no Must/Should/Could-Fix token.

An `abandoned` row is a **surfaced fact, not a validation failure** — the validator emits it (id + short foreshadow + locus) for the editorial letter to cite in prose (Stage A wiring — the Legal-Risk / Content-Advisory precedent).

## Out of scope (deferred)

- **The semantic "does this passage actually pay off the setup?" judgment** — a SETEC-consumer surface (mirror narrative-decision / argument-decision: voiceprint computes an LLM-judge `foreshadow_payoff_audit`, apodictic consumes via a shim). Gated on a voiceprint surface that does not yet exist.
- **Promoting `abandoned` to a promise-contract Should-Fix `finding`** (D3 Stage B). This requires a real input port + parser change to `promise_contract.py` (verified absent today). The Ledger stays orthogonal — it records the state; promise-contract would *read* it and own any severity call. The Ledger never asserts severity.

## Cross-repo sibling

voicewright `specs/31-foreshadow-payoff-checker.md` is the **generation-side** sibling — same CFPG root (arXiv:2601.07033), different consumer. voicewright: an estate/series operator **declares** plant/payoff threads pinned to their own outline units. This spec: the editor **extracts** F/T/P from a finished third-party manuscript and feeds the editorial letter. The split (generate vs. audit) is deliberate. voicewright's "deliberate dangling thread (sequel hook, red herring) vs. accidental dropped plant" is this Ledger's `open` (rationaled) vs. `abandoned` axis.
