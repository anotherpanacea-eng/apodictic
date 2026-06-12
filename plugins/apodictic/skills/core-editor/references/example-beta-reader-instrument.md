# Beta-Reader Instrument — *The Lighthouse Year* (worked example)

*Canonical worked example for the `reader-instrument` validator (Beta-Reader Instrument Generation,
revision-coach). Paired with [`example-uncertainty-ledger.md`](example-uncertainty-ledger.md): each
question is seeded from that ledger's genuine uncertainty. Demonstrates `B3` provenance integrity on
a real `LOW` finding and a `source_note`-only Unresolved Question, a clean non-leading / content-neutral
`B4`, and an uncertainty-targeted question that does **not** trip `B5`. Validate with
`scripts/validate.sh reader-instrument <this file> example-uncertainty-ledger.md` (run by `--check-all`).*

**These are questions for readers, not the author.** They probe the reader's *experience* of what is
already on the page — they never name a fix, smuggle a verdict, or introduce anything not in the book.
A confirming vs. refuting answer re-enters the loop through Feedback Triage as a `feedback_item`.

---

<!-- apodictic:reader_question
{
  "schema": "apodictic.reader_question.v1",
  "id": "RQ-01",
  "source_kind": "low-confidence-finding",
  "targets": "F-P5-01",
  "source_note": "",
  "uncertainty": "Pass 5 suspects the midpoint reversal under-lands, but confidence is LOW.",
  "probe_type": "experiential",
  "question": "About halfway through, where (if anywhere) did you feel the main character change course — and once you noticed it, what did you expect to happen next?",
  "expected_signal": "Readers who can't locate any mid-book change, or who report no shift in what they expected, corroborate the under-landing; readers who name the turn and describe a changed expectation refute it."
}
-->

<!-- apodictic:reader_question
{
  "schema": "apodictic.reader_question.v1",
  "id": "RQ-02",
  "source_kind": "unresolved-question",
  "targets": "",
  "source_note": "Unresolved Questions bullet: whether the ending's final image reads as hope or resignation.",
  "uncertainty": "A pass surfaced the open question of how the closing image lands, but could not settle it from the text.",
  "probe_type": "experiential",
  "question": "When you finished, what feeling did the last scene leave you with? Say it in your own words before reading on.",
  "expected_signal": "A spread clustering toward 'hopeful' vs. 'resigned' shows which reading dominates on a first pass; a near-even split suggests the image is genuinely holding both."
}
-->
