---
description: Flag legal-exposure areas (defamation, privacy, rights-clearance) for legal review
argument-hint: point to the manuscript, or no argument
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

Legal Risk Register. For memoir, autofiction, or nonfiction that portrays **identifiable real people**, or quotes substantial third-party copyrighted material, and is heading toward publication. Flags the manuscript's legal-exposure areas so the author knows where to get a lawyer's eyes — it does **not** practice law.

Load `../skills/core-editor/SKILL.md` and follow `../skills/core-editor/references/legal-risk-register.md`.

**Firewall — flag, don't practice law.** Name the exposure and the trigger; route serious items to counsel. Never adjudicate ("this is not defamatory", "protected by fair use", "no liability") — that is a legal conclusion only a qualified attorney makes. *I am not a lawyer; this flags areas that may need legal review and is not legal advice.*

**Procedure** (per `../skills/core-editor/references/legal-risk-register.md §Protocol`):

1. Read the manuscript (and the contract / `Diagnostic_State.md` if a project exists, for genre + identifiable-person context).
2. Flag each exposure area as an `apodictic.legal_risk.v1` block — `risk_class` (defamation / privacy / rights-clearance / other), a legal-escalation `severity` (monitor / review-recommended / review-now), the `concern`, the `escalation_trigger`, and a `disposition` that routes serious items to counsel — in `[Project]_Legal_Risk_Register_[runlabel].md`.
3. Carry the not-a-lawyer disclaimer in reader-facing prose.

**Gate before finalizing:** `scripts/validate.sh legal-risk <run_folder>` (add `--strict` for CI). Resolve any ERROR (broken contract, duplicate id, missing disclaimer) and review W1 (a `concern`/`disposition` that reads like a legal conclusion rather than a flag) / W2 (a `review-now` item not routed to counsel). See `docs/legal-risk-register.md`.

**State and output locations** (per `../skills/core-editor/references/output-structure.md` §Folder Architecture):
- Read the manuscript and any `Diagnostic_State.md` from the **project root**
- Write the `[Project]_Legal_Risk_Register_[runlabel].md` to the **project root**; archive into `runs/YYYY-MM-DD_{model}_{type}/` on completion
- Never write to the plugin repo

Also reachable from `/start` via `constraint:risk` ("sensitive or legally risky content"), where it is offered and attached on accept.

If a manuscript path is provided: $ARGUMENTS
