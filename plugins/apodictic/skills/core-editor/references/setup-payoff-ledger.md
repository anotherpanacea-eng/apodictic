# Setup–Payoff Ledger — check every setup resolves, surface the abandoned ones

*Reference module for the APODICTIC Core Editor. The referential-completeness half of a
developmental-edit style sheet: a locus-anchored record of the manuscript's Foreshadow → Trigger →
Payoff triples and a mechanical check that every foreshadow resolves. Spec + validator:
`docs/setup-payoff-ledger.md`, `scripts/validate.sh setup-payoff`. Worked example:
`example-setup-payoff-ledger.md`. Anchor paper: arXiv:2601.07033 (CFPG).*

---

## When to use

During a development edit, when the author wants the answer a human editor gives about **dropped
threads**: which planted expectations the manuscript sets up and never resolves. A planted gun, a
prophecy, a withheld backstory, a foreshadowed reunion — a "setup" is any committed narrative
expectation. The Ledger catalogues each one as a **Foreshadow → Trigger → Payoff** triple and checks
the debt is paid. It is a companion to the editorial letter, not a replacement: the letter judges,
the Ledger catalogues.

This is the mechanical home for the one ConStory-Bench craft row — **"Abandoned Plot Elements"** —
that no other APODICTIC surface owns.

## The firewall: extract the marked triple, never author the verdict

This module **decides no verdict.** It is firewall-safe by construction:

- **The model marks; the validator derives.** The model authors the extraction (marks each F, its
  optional T, and the `payoff_ref`); the validator resolves the ref and **derives** the state
  (`paid_off` / `open` / `abandoned`) deterministically. An author may write `state` into a block,
  but the validator confirms it matches the derivation (SP4) — the register never overrides the
  mechanics.
- **Never invents a payoff.** The tool records the author-marked `payoff_ref` and checks it resolves
  to a real payoff block; it does **not** decide whether a given passage "counts" as payoff. That
  semantic call is the deferred SETEC-consumer job.
- **No severity in the register.** The Ledger carries no `apodictic:finding` block and no
  Must/Should/Could-Fix token (X1). An `abandoned` setup is a **surfaced fact**, not a defect
  verdict; whether it rises to an editorial severity band is a downstream call (promise-contract).

## The three states

- **`paid_off`** — a resolving payoff block exists and the foreshadow references it.
- **`open`** — deliberately unresolved, carrying a **rationale** (a series thread deferred to a later
  book, an intentional ambiguity). Flagged, not a defect.
- **`abandoned`** — no resolving payoff **and** no rationale. The causal debt left unpaid — the
  signal the editorial letter cites in prose.

## The artifact

A `[Project]_Setup_Payoff_Ledger_[runlabel].md` of `apodictic.payoff.v1` (resolving payoffs) and
`apodictic.setup_payoff.v1` (foreshadows) blocks, plus a `## Setup–Payoff Ledger` markdown table for
the reader-facing rollup. Each foreshadow block:

```markdown
<!-- apodictic:setup_payoff
{"schema":"apodictic.setup_payoff.v1","id":"SP-01","foreshadow":"Mara pockets the revolver","anchor":["Ch 1 §2"],"trigger":"when Jon arrives","payoff_ref":"PO-03","state":"paid_off"}
-->
```

and each payoff:

```markdown
<!-- apodictic:payoff
{"schema":"apodictic.payoff.v1","id":"PO-03","payoff":"The revolver is fired in the climax","anchor":["Ch 9 ¶4"]}
-->
```

- `id` — `SP-NN` (foreshadow) / `PO-NN` (payoff); ids unique within their kind.
- `anchor` — the manuscript loci (≥1 coarse chapter / §section / ¶ / line / page token).
- `trigger` — optional free-text (CFPG's activation condition); **recorded, not gated** — completeness
  is F↔P, T is context.
- `payoff_ref` — the id of the resolving payoff, or the empty string.
- `state` — `paid_off` / `open` / `abandoned` (validator-derived; SP4 confirms).
- `open_rationale` — **required (non-empty) when `state` is `open`.**

**N:1 is allowed** — many foreshadows may resolve to one payoff. A payoff with no foreshadow is not
flagged (that inverse is deferred Stage B).

## Feeding the letter (Stage A — prose citation)

When the Ledger runs inside a dev-edit, the editorial letter references each `abandoned` foreshadow
**by prose citation** (the Legal-Risk / Content-Advisory precedent), so a dropped promise reaches the
author's revision plan. The validator emits the abandoned rows (id + short foreshadow + locus) for
the letter to cite. **No other validator consumes the register** — whether an `abandoned` row should
*become* a promise-contract finding is deferred Stage B (it needs a parser change to
`promise_contract.py` that does not exist today).

## The validator

`scripts/validate.sh setup-payoff <run_folder|files...> [--strict]` runs SP1 schema, SP2 referential
integrity (a phantom `payoff_ref` FAILs), SP3 open rationale, SP4 derived-state agreement, and X1
firewall. It takes a run folder (globs `*_Setup_Payoff_Ledger_*.md`) or explicit files. The worked
example `example-setup-payoff-ledger.md` is wired into `--check-all`.
