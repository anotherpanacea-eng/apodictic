# Reader probes of locked findings — spec (apodictic)

**Status:** **Proposed (unbuilt).** Waiting for the owner to admit it. Do not build until the owner admits it. When built, the build PR flips this line (`AGENTS.md` § Review practices).
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
   - Step 5 becomes: returned answers can reopen a locked finding. The `assessment` comes from APODICTIC's re-analysis of the text in light of the report, never from how many readers said what. If the re-analysis finds the mechanism does not operate, the item is `refuted`, and the existing decline offer (`feedback-triage.md:37`) lets the author record it.
4. **Command (3 sentences),** `commands/reader-questions.md:12`, `:20`, `:22` — the same rule.
5. **Design doc (about 10 lines),** `docs/beta-reader-instrument.md` — delete the B5 row and rewrite `:20`, `:64-65`, `:113` to point here.
6. **Example (1 line),** `skills/core-editor/references/example-beta-reader-instrument.md:7` — drop the "does not trip B5" clause.
7. One `changelog.d/` fragment.

In total about 60 lines touched across seven files. It adds no validator, schema id, finding field, override marker or gate.

## Behavior it protects

- A writer can check a costly Must-Fix against real readers before spending a revision on it. When a reader's report shows the mechanism does not operate, that evidence reaches the finding instead of being thrown away.
- Unchanged: questions still may not lead or invent content (B4); readers never vote on a verdict (triage `assessment`); author objection still never refutes (Step 6b).

## Deletion test

- **B5 and the `how-to-fix` override — delete.** B5 guards against softening a verdict by survey. That is already prevented where it would happen: re-analysis sets the assessment, not reader count. The review's own safeguard, neutral wording, is B4. With B5 gone, a probe of a locked finding is the intended behavior, so no silent failure remains.
- **Nothing added.** There is no reopen state, no new status on findings and no reader-evidence ledger. Reopening runs through the existing triage `assessment` and decline offer.

## Not in this spec (owner's call)

- **The `/ready` tally.** A finding refuted at Step 6b leaves the repair list, but its locked severity still counts in the triage tally and verdict caps (`docs/finding-disconfirmation.md:277`). This spec leaves that alone. The card leaves the tally contract to the owner.
- **Reader reports as Step 6b counter-evidence.** `refutation-evidence` checks counter-evidence quotes against the manuscript snapshot (`scripts/refutation_check.py:31-53`). Letting reader reports count there would change `apodictic.refutation.v1` and the tally. Not proposed here.

## Acceptance check

1. Self-test arm (step 2): a ledger with one Must-Fix/HIGH motivation finding and an instrument with an unprompted opener plus a `locked-finding` experiential probe. The probe passes `reader-instrument --strict`. A blocklisted leading version ("Don't you think her departure is unexplained?") still trips B4. That is existing behavior, and the arm confirms it survives.
2. Manual walk-through, recorded in the build PR: (a) a reader names the reason for the departure → re-analysis → `refuted` → the decline offer appears; (b) a reader only dislikes the scene → not refuted, and the finding stands.

## Owner questions

1. **Reverse the Horizon-16 boundary?** Delete B5 and `how-to-fix` (this spec), or keep B5 as a non-strict note? B5 implements a ratified roadmap boundary (`ROADMAP.md:562`), so reversing it is your decision.
2. **How a finding reopens.** (a) Through the triage `refuted` assessment and the existing decline offer (this spec; no tally change), or (b) Step 6b accepts reader reports as counter-evidence (schema change, and it touches the `/ready` tally).
3. **Name** of the new `source_kind`: `locked-finding`, or something else?
4. **Mechanize "don't name the mechanism" and "unprompted first"?** This spec keeps both as prose. B4's blocklist does not catch "did X bother you?", and adding that phrase is a one-line option.
