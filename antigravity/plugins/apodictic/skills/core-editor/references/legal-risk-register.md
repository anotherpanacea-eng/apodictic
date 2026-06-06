# Legal Risk Register (workflow)

**Status:** v1 (Increment 1)
**When:** memoir, autofiction, or nonfiction that portrays **identifiable real people**, or that quotes substantial third-party copyrighted material. Run after the structural read, when the author is heading toward publication.
**Home:** core-editor (manuscript-content analysis). Design + lineage: [`docs/legal-risk-register.md`](../../../../docs/legal-risk-register.md).

---

## Purpose & firewall

Flag the manuscript's **legal-exposure areas** — defamation, privacy/disclosure, rights-clearance — so the author knows where to get a lawyer's eyes before publishing. **The firewall: flag, don't practice law.** Name the exposure and the trigger; route the serious items to counsel. Never adjudicate ("this is not defamatory", "protected by fair use", "no liability") — that is a legal conclusion only a qualified attorney makes. *I am not a lawyer; this flags areas that may need legal review and is not legal advice.*

---

## The artifact: `[Project]_Legal_Risk_Register_[runlabel].md`

A **not-a-lawyer disclaimer** plus a set of `apodictic.legal_risk.v1` blocks — one per flagged area:

```markdown
<!-- apodictic:legal_risk
{"schema":"apodictic.legal_risk.v1","id":"LR-01","risk_class":"defamation",
 "severity":"review-now","subject":"a named, identifiable living person",
 "locations":["Ch. 4"],
 "concern":"a stated-as-fact assertion of misconduct by a named living person",
 "escalation_trigger":"any retained statement of fact alleging a crime by a named living person",
 "disposition":"route to legal counsel before publication; substantiate or reframe as opinion"}
-->
```

- **`risk_class`** — `defamation` (false statement of fact harming reputation) | `privacy` (private facts about an identifiable person, disclosed without consent) | `rights-clearance` (quoted lyrics/images/substantial text needing permission) | `other`.
- **`severity`** — a **legal-escalation tier**, separate from the editorial Must/Should/Could scale: `monitor` → `review-recommended` → `review-now`.
- **`concern` / `disposition`** — flags, never legal conclusions. `escalation_trigger` is the condition that should route the item to a lawyer.

Field set canonical in `schemas/apodictic.legal_risk.v1.schema.json`. Worked example: `core-editor/references/example-legal-risk-register.md`.

---

## Protocol

1. **Identify** the identifiable real people and quoted third-party material.
2. **Flag** each exposure as a `legal_risk` block — `risk_class`, `concern`, `escalation_trigger`, and a `disposition` that *routes*, never *adjudicates*.
3. **Tier** by legal-escalation severity; every `review-now` item must route to counsel.
4. **Disclaim** — carry the not-a-lawyer statement at the top of the register.

## Mechanical check

`scripts/validate.sh legal-risk <run_folder>`: L1 schema, L2 unique ids, **L3 not-a-lawyer disclaimer present** (the signature gate); **W1 legal-advice drift** (a conclusion where a flag belongs — the firewall; override `<!-- override: legal-advice-drift LR-NN — … -->`), W2 a review-now item not routed to counsel. W1/W2 advisory, ERROR under `--strict`. Ownership boundary + lineage: [`docs/legal-risk-register.md`](../../../../docs/legal-risk-register.md).
