# Legal Risk Register — a workflow

**Status:** Increment 1 **built**. Roadmap: `ROADMAP.md` → Workflows → Legal Risk Register. Home: **core-editor** (manuscript-content analysis), reference `core-editor/references/legal-risk-register.md`. Artifact: `[Project]_Legal_Risk_Register_[runlabel].md`. Validator: `validate.sh legal-risk`.

## Purpose

Memoir, autofiction, and nonfiction that portrays **identifiable real people** carry legal exposure the structural edit otherwise ignores: **defamation** (a false statement of fact that harms reputation), **privacy / disclosure** (private facts about an identifiable person, disclosed without consent), and **rights-clearance** (quoted lyrics, images, or substantial copyrighted text needing permission). The Legal Risk Register **flags** these areas with a severity and an escalation trigger so the author knows where to get a lawyer's eyes before publication.

## The firewall: flag, don't practice law

APODICTIC is not a lawyer, and this module never pretends to be one. It **flags areas that may warrant legal review**; it does **not** adjudicate — no "this is not defamatory," "you're protected by fair use," "no liability here." Those are legal conclusions only a qualified attorney should make. The register names the *exposure* and the *trigger*, and routes the high-severity items to counsel. This is the analogue of the Core Firewall (diagnose, don't rewrite): here it is *flag, don't advise*.

Two checks mechanize it: every register must carry a **not-a-lawyer disclaimer** (validator L3), and a `concern`/`disposition` that reads like a legal **conclusion** rather than a flag is surfaced as **legal-advice drift** (validator W1).

## Artifact: `[Project]_Legal_Risk_Register_[runlabel].md`

A not-a-lawyer disclaimer plus a set of `apodictic.legal_risk.v1` blocks — one per flagged area:

```json
{
  "schema": "apodictic.legal_risk.v1",
  "id": "LR-01",
  "risk_class": "defamation",            // defamation | privacy | rights-clearance | other
  "severity": "review-now",              // monitor | review-recommended | review-now (legal-escalation tier)
  "subject": "the narrator's former manager (named, identifiable)",
  "locations": ["Ch. 4", "Ch. 9 (p. 212)"],
  "concern": "a stated-as-fact assertion that a named living person committed financial wrongdoing",
  "escalation_trigger": "any retained statement of fact alleging a crime by a named living person",
  "disposition": "route to legal counsel before publication; substantiate or reframe as disclosed opinion"
}
```

**`severity` is a legal-escalation tier**, deliberately kept **orthogonal** to the editorial Must/Should/Could scale (the v2.0.0 severity-orthogonality discipline): `monitor` (track it) → `review-recommended` (raise it with the author) → `review-now` (route to counsel before publication). A legal flag is not an editorial defect; it is a different axis.

`concern` and `disposition` are **flags**, never legal conclusions. `escalation_trigger` is the condition that should send the item to a lawyer. Field set canonical in `schemas/apodictic.legal_risk.v1.schema.json`.

## The `legal-risk` validator

`validate.sh legal-risk <run_folder|files>` (parses the `legal_risk` blocks via the shared `apodictic_artifacts` engine). Degrades to an advisory `WARN` without `python3`.

| ID | Severity | Rule |
|---|---|---|
| **L1 — invalid item** | ERROR | A `legal_risk` block fails its schema (bad `risk_class`/`severity` enum, malformed `LR-NN` id, missing required field, broken JSON). |
| **L2 — duplicate id** | ERROR | Two items share an `LR-NN` id. |
| **L3 — missing disclaimer** | ERROR | The register has `legal_risk` items but no not-a-lawyer / not-legal-advice disclaimer **in reader-facing prose** (HTML comments and the `legal_risk` blocks are stripped before the check, so an implementation note can't satisfy it). **The signature gate** — the register must never read as legal advice. |
| **W1 — legal-advice drift** | WARN (ERROR `--strict`) | A `concern`/`disposition` states a legal **conclusion** ("not defamatory", "protected by", "is fair use", "no liability", "can't be sued", "is legal") rather than flagging for review. **The module firewall.** Override (per id): `<!-- override: legal-advice-drift LR-NN — <rationale> -->`. |
| **W2 — unrouted high risk** | WARN (ERROR `--strict`) | A `review-now` item whose `disposition` does not route to legal review / counsel — a top-tier flag must point to a lawyer. |

**The signature checks are L3 and W1** — together they keep the register a *flagging* tool, never legal advice.

**Ownership boundary.** `legal-risk` owns the register's contract — id/enum integrity, the disclaimer gate, the flag-don't-adjudicate firewall, and high-risk routing. It does **not** judge editorial severity (that stays with the finding/severity validators), assess whether a concern is *correct* (that is the lawyer's call), or re-diagnose the manuscript.

## Workflow

1. **Identify** identifiable real people and quoted third-party material in the manuscript.
2. **Flag** each exposure as a `legal_risk` block — name the `risk_class`, the `concern`, the `escalation_trigger`, and a `disposition` that *routes*, never *adjudicates*.
3. **Tier** each by legal-escalation severity; `review-now` items must route to counsel.
4. **Disclaim** — the register carries the not-a-lawyer statement.
5. Validate with `validate.sh legal-risk` (`--strict` in CI). A canonical worked example (`core-editor/references/example-legal-risk-register.md`) is gated by `validate.sh --check-all`.

## Increment boundaries

**Increment 1 (this):** the workflow contract, the `[Project]_Legal_Risk_Register_[runlabel].md` artifact, the `apodictic.legal_risk.v1` block + schema, the `legal-risk` validator (L1–L3 + W1–W2), the worked example, the `--check-all` gate, and the core-editor reference.

**Future increments:**
- **Intake routing + a first-class entry point — built (explicit-flag path).** The `/legal-risk` command (`commands/legal-risk.md`) and the `constraint:risk` synthesis hook (offer-then-attach, `run-synthesis.md §Constraint mode`) are wired. *Still future:* a content-detection branch that auto-recommends the register for memoir/autofiction portraying identifiable real people *without* the explicit `constraint:risk` flag.
- **Per-class detection guidance** — named detection patterns per `risk_class` (e.g. fact-vs-opinion framing for defamation; public-vs-private and newsworthiness for privacy; substantiality/permission heuristics for rights-clearance), so the flag is grounded in a specific, citable manuscript signal.
- **Escalation-trigger taxonomy** — a small library of standard triggers per class the author can adopt rather than re-author.
