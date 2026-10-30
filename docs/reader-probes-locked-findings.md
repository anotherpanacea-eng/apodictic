# Reader probes of locked findings — spec (apodictic)

**Status:** **Admitted spec, 2026-10-29 (owner, as written). Unbuilt.** The owner questions below are resolved as this spec proposes. When built, the build PR flips this line (`AGENTS.md` § Review practices).
**Estimate:** one small PR. The validator change is a net deletion.
**Provenance:** deferred finding 2 of the external Codex framework review of 2026-10-16 (private document; summarized here, not quoted). Burndown card OCA-9. Line references are to `main` after the 2026-10-26 train (#398).

---

## The deferred finding

The Beta-Reader Instrument (`/reader-questions`) will not ask readers about a locked finding (Must-Fix or Should-Fix at HIGH or MEDIUM confidence). It also says a locked verdict stays locked whatever readers report. The review argues the priority runs the other way. High-impact, high-confidence findings drive the most expensive revisions, and a real reader's experience is evidence the model does not have. The review's safeguards are neutral wording, unprompted answers collected before targeted ones, a reader's reported experience kept apart from their explanation and proposed fix, and a reasoned re-analysis (never a vote) before anything about the finding changes.

## What `main` does today

The refusal:

- `plugins/apodictic/skills/revision-coach/references/beta-reader-instrument.md:20-31` — "Severity honesty — the hard boundary": draw only from LOW/UNCERTAIN findings, Unresolved Questions and tradeoffs. Step 2 (`:49`) says to skip locked targets. Step 5 (`:52`) says "a locked verdict stays locked regardless of the answers." The degrade path (`:64`) repeats the check.
- `plugins/apodictic/commands/reader-questions.md:12`, `:20`, `:22` — the same boundary in the command.
- `plugins/apodictic/scripts/reader_instrument.py` — B5: docstring `:25-28`, lock constants `:73-74`, the `how-to-fix` override `:231`, the check `:291-297`, the report line `:324`, and five self-test arms `:487-503`. B5 is a WARN, and an ERROR under `--strict`.
- `docs/beta-reader-instrument.md:20`, `:64-65`, `:78` (the B5 row), `:113`.
- The source of the boundary is `ROADMAP.md:562`, Horizon item 16: a loop where the author contests a finding and the editor downgrades it would undo the Deficit Lock.

Already on `main`, and reused here rather than rebuilt:

- **B4** flags leading constructions and invented content (`reader_instrument.py:21-24`, blocklist `:79-83`).
- **Feedback Triage** sets `assessment` by APODICTIC's own targeted re-analysis, not by reader count (`skills/revision-coach/references/feedback-triage.md:25`, `:33`). Step 6 (`:37`) offers to record a `declined` finding disposition when an item cites an `F-…` id.
- **Step 6b** in `skills/core-editor/references/run-synthesis.md:189-194`: author objection or compensating strengths never refute a finding. Refutation needs evidence that the mechanism does not operate.

Horizon item 16 is about severity softened by **author objection**. A reader reporting what they experienced is not an author objection, and a re-analysis that reads that report is not a vote. B5 blocks both the case item 16 targets and the case the review wants opened.

## Smallest change

1. **Schema (1 line).** Add `locked-finding` to the `source_kind` enum in `plugins/apodictic/schemas/apodictic.reader_question.v1.schema.json`. Add it to `_FROM_FINDING` (`reader_instrument.py:71`) so B3 requires `targets` and resolves it against the Ledger. Like `tradeoff`, it is exempt from B3's label-mismatch advisory (`:251-256`).
2. **Validator (net about −25 lines).** Delete B5 completely: the docstring entry, `_LOCKED_SEVERITY`/`_LOCKED_CONFIDENCE`, the `how-to-fix` override parse, the check, the B5 mention in the report line, and the five B5 self-test arms. Add one arm: a `locked-finding` probe of a Must-Fix/HIGH finding passes `--strict`. Drop "anti-relitigation" from the canonical-check label (`scripts/validate_canonical.py:373`).
3. **Reference (about 20 lines rewritten),** `beta-reader-instrument.md:20-31`, `:48-52`, `:64`:
   - Replace the hard boundary with **What to probe**. Any consequential finding may be probed. Rank by impact, uncertainty and revision cost; this is prose judgment, with no score.
   - For a locked finding, ask what the reader experienced at that point. Never ask whether the problem exists, and never name the finding's mechanism in the question. Example, for a motivation finding: "What did you understand to be the reason she left?", not "Did her unexplained departure bother you?"
   - **Unprompted first.** The instrument opens with one or two open questions (for example "Where, if anywhere, did you lose interest? What confused you?"), answered before the targeted ones.
   - `expected_signal` reads the reported experience, not the reader's explanation or fix.
   - Step 5 becomes: returned answers can reopen a locked finding. Feedback Triage assesses the reader's claim as it does today: re-analysis of the text, never a count of readers. A reader who names the reason she left makes a claim about what the text conveys, and re-analysis can `validate` it. The answer bears on the finding when that validated claim contradicts the finding's mechanism.
4. **Feedback Triage (2 lines),** `skills/revision-coach/references/feedback-triage.md` step 3 (`:34`). When a `validated`/`partly-validated` item cites an `F-…` id in `evidence_refs` and contradicts that finding's mechanism, say so and offer the author the existing finding-disposition record (`{disposition: declined, source: triage, reason: …}`, the same dual-writer path as step 6, `:37`). The author decides; nothing changes on its own. The item itself is not declined, so W3 (`scripts/feedback_triage.py:20`) is unaffected. No validator change.
5. **Command (3 sentences),** `commands/reader-questions.md:12`, `:20`, `:22` — the same rule.
6. **Design doc (about 10 lines),** `docs/beta-reader-instrument.md` — delete the B5 row and rewrite `:20`, `:64-65`, `:113` to point here.
7. **Example (1 line),** `skills/core-editor/references/example-beta-reader-instrument.md:7` — drop the "does not trip B5" clause.
8. One `changelog.d/` fragment.

In total about 60 lines touched across eight files. It adds no validator, schema id, finding field, override marker or gate.

## Behavior it protects

- A writer can check a costly Must-Fix against real readers before spending a revision on it. When a reader's report shows the mechanism does not operate, that evidence reaches the finding instead of being thrown away.
- Unchanged: questions still may not lead or invent content (B4); readers never vote on a verdict (triage `assessment`); author objection still never refutes (Step 6b).

## Deletion test

- **B5 and the `how-to-fix` override — delete.** B5 guards against softening a verdict by survey. That is already prevented where it would happen: re-analysis sets the assessment, not reader count. The review's own safeguard, neutral wording, is B4. With B5 gone, a probe of a locked finding is the intended behavior, so no silent failure remains.
- **Nothing added.** There is no reopen state, no new status on findings and no reader-evidence ledger. Reopening runs through the existing triage `assessment` and the existing finding-disposition record, offered from one more triage step.

## Not in this spec (owner's call)

- **The `/ready` tally.** A finding refuted at Step 6b leaves the repair list, but its locked severity still counts in the triage tally and verdict caps (`docs/finding-disconfirmation.md:277`). A declined disposition keeps its existing `/ready` treatment too. This spec changes no count or cap. The card leaves the tally contract to the owner, as a decision separate from anything here.
- **Reader reports as Step 6b counter-evidence.** `refutation-evidence` checks counter-evidence quotes against the manuscript snapshot (`scripts/refutation_check.py:31-53`). Admitting reader reports there would change that evidence rule in `apodictic.refutation.v1`. It would not by itself change the tally: Step 6b keeps locked severity, counts and caps (`run-synthesis.md:199-209`). Not proposed here.

## Acceptance check

1. Self-test arm (step 2): a ledger with one Must-Fix/HIGH motivation finding and an instrument with an unprompted opener plus a `locked-finding` experiential probe. The probe passes `reader-instrument --strict`. A blocklisted leading version ("Don't you think her departure is unexplained?") still trips B4. That is existing behavior, and the arm confirms it survives.
2. Manual walk-through, recorded in the build PR: (a) a reader names the reason for the departure → re-analysis validates that claim → the item cites the finding and contradicts its mechanism → the disposition offer appears; (b) a reader only dislikes the scene → the claim does not bear on the mechanism, so no offer appears and the finding stands.

## Owner questions

1. **Reverse the Horizon-16 boundary?** Delete B5 and `how-to-fix` (this spec), or keep B5 as a non-strict note? B5 implements a ratified roadmap boundary (`ROADMAP.md:562`), so reversing it is your decision.
2. **How reader evidence reaches a finding.** (a) A validated triage item contradicts the finding, and the author is offered the existing disposition record (this spec), or (b) Step 6b also admits reader reports as counter-evidence (an evidence-rule change to `apodictic.refutation.v1`). Either route keeps today's counts and caps.
5. **The `/ready` tally** for refuted or declined findings is a separate decision. Neither route above needs it changed.
3. **Name** of the new `source_kind`: `locked-finding`, or something else?
4. **Mechanize "don't name the mechanism" and "unprompted first"?** This spec keeps both as prose. B4's blocklist does not catch "did X bother you?", and adding that phrase is a one-line option.
