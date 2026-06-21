---
description: Check a worldbuilding bible for self-contradiction (rules, magic costs, geography/timeline)
argument-hint: point to the worldbuilding bible, or no argument
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

Standalone Worldbuilding-Bible Coherence Tool. For an SFF author with a **pre-draft worldbuilding bible** — the rules of the magic/tech and its cost, the geography, the order of events, the factions — checks that *bible* (not a manuscript) for self-contradiction: closed-set rule consistency, magic-system cost accounting, and geography/timeline contradiction. It surfaces the conflicts the bible has already committed to; it does **not** invent world content.

Load `../skills/core-editor/SKILL.md` and follow `../skills/core-editor/references/worldbuilding-bible.md`.

**Firewall — extract the stated, never author the unstated.** Record what the bible asserts (with its locus); surface a contradiction by recording **both** values, never resolving it ("the bible prices blood-magic two ways — reconcile or stage the escalation", not "the cost is one year of life"). Choosing canon is the author's call.

**Procedure** (per `../skills/core-editor/references/worldbuilding-bible.md`):

1. Read the author's worldbuilding bible (their hand-authored prose and tables — not a manuscript).
2. Extract each stated world fact as an `apodictic.world_fact.v1` block — `category` (rule / cost / place / distance / event / faction / entity), `subject`, `attribute`, a string `value` (quote numerics), plus `polarity` (rule), `cost` (cost/rule), or `pair_subject` (distance/event), and ≥1 `loci` — in `[Project]_Worldbuilding_Bible_[runlabel].md`.
3. Build the `## Contradiction Ledger`, pairing the ids of any conflicting facts. Where a contradiction is intended (a staged reveal, a documented cost escalation), add the matching override marker carrying the author's rationale; never adjudicate.

**Gate before finalizing:** `scripts/validate.sh world-bible <run_folder>` (add `--strict` for CI). Resolve any ERROR (broken contract, unknown/misspelled field, duplicate id, WB-R1 rule contradiction, WB-C1 cost contradiction, WB-G1 distance contradiction, WB-G2 chronology cycle / anchor-drift) and review the advisories (WB-C2 free-then-costed, WF firewall prose scan). Mark an intended contradiction with `<!-- override: world-rule|world-cost|world-geo WF-NN/WF-MM — <rationale> -->`. See `docs/worldbuilding-bible.md`.

**State and output locations** (per `../skills/core-editor/references/output-structure.md` §Folder Architecture):
- Read the worldbuilding bible from the **project root**
- Write the `[Project]_Worldbuilding_Bible_[runlabel].md` to the **project root**; archive into `runs/YYYY-MM-DD_{model}_{type}/` on completion
- Never write to the plugin repo

It is usable **before or alongside drafting** (the pre-writing pathway's spirit) — it needs no manuscript, only the author's bible.

If a worldbuilding-bible path is provided: $ARGUMENTS
