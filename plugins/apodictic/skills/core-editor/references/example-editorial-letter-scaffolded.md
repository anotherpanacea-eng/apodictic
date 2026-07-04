# Development Edit: The Tide Between Us — Editor Scaffolding

<!--
Worked example of a contract-conformant Development Edit synthesis letter in EDITOR
SCAFFOLDING mode (operator:editor — see editor-scaffolding.md + run-synthesis.md §Operator
Mode: Editor Scaffolding). It is a SUPERSET overlay on the standard author-facing example
(example-editorial-letter.md): the mandatory decision-layer sections (Protected Elements,
Author Decisions, Control Questions, Appendices A/B/C) and the per-Must-Fix evidence density
are all preserved, so the standard gates still pass — and on top of them the three scaffolding
shifts (Editor Brief, What You Might Have Missed, Intervention Menu) are added.

This file is exercised by `validate.sh --check-all` as a canonical release-gate target for
THREE validators at once — `editor-scaffolding`, `decision-layer-check`, and `severity-floor`
— proving the overlay COMPOSES with the standard gates, not merely that the new validator
passes its own fixtures. It is illustrative, not a run artifact; keep it passing when the
letter contracts or the validators change. Keep the body free of author-directed
prescriptions ("you should rewrite ...") — in scaffolding mode those belong to the human
editor, and the W1 lexicon flags them.
-->

<!-- mode: editor-scaffolding -->

### Maya Okonkwo | 78,000 words | Complete draft
*APODICTIC Development Editor — addressed to the editor, not the author.*

## Editor Brief

A dual-timeline literary novel with a genuinely strong voice and a structurally soft middle.
Asset: the dual-POV voice holds across both timelines and the close earns its restraint.
Liability: the middle third compresses its emotional aftermath into summary. Verdict class:
targeted revision, not reconception.

**Where your read and mine are most likely to diverge:** a confident first read tends to
credit the polished Part I prose and carry that goodwill through the middle — the prose is
good enough to paper over a missing causal beat at the Chapter 9 turn. The blind-spot section
below is where I'd focus a second pass.

## What the Book Does Best

The dual-POV voice holds across both timelines, and the close earns its restraint. The
sister-relationship arc carries the emotional spine without ever stating it outright.

## What Needs Work

- **Must-Fix:** Pacing collapse in the middle third. The aftermath compression recurs in
  Chapter 7 (lines 142-160) and again in Chapter 9 (line 220), where three days pass in two
  sentences and the consequence of the central choice is summarized rather than dramatized.
- **Should-Fix:** The prologue's frame competes with Chapter 1 for the reader's first
  orientation (Chapter 1, lines 1-40).

## What You Might Have Missed

Two findings are easy to under-weight on a first read because the prose carries you past them.
They are ordered by **blind-spot gap** — how far a finding's structural severity outruns its
surface salience (how easy it is to miss) — largest gap first, so the finding most likely to slip
a confident read leads. The machine-checkable ranking blocks below carry that order; the editor
owns the judgment, the validator only checks the gap arithmetic and sort order.

- The Chapter 9 turn has no on-page causal link between the choice and its consequence
  (Chapter 9, line 220) — the polish of the surrounding scene masks the missing beat. This is
  the mechanism behind the pacing finding above, not a separate problem. <!-- finding: F-P2-01 -->
<!-- apodictic:blind_spot_ranking
{"schema":"apodictic.blind_spot_ranking.v1","finding_id":"F-P2-01","severity":"Must-Fix","salience":"subtle"}
-->
- The novel runs on almost zero dramatic irony (see Reverse Outline, §Reader Knowledge). That
  is a structural characteristic, not a flaw — but it means the middle third has no secondary
  tension to lean on while the primary line compresses, which is *why* the compression reads
  as flatness rather than restraint (see Reader Dynamics, §Tension Sources). <!-- finding: F-P5-02 -->
<!-- apodictic:blind_spot_ranking
{"schema":"apodictic.blind_spot_ranking.v1","finding_id":"F-P5-02","severity":"Should-Fix","salience":"subtle"}
-->

(Blind-spot gaps: F-P2-01 Must-Fix/subtle = 2, ranked first; F-P5-02 Should-Fix/subtle = 1.)

## Intervention Menu — editor's discretion

Option-classes for the middle third, for you to adopt, sequence, or set aside with the author:

- Restore the Chapter 9 causal beat on-page (single-scene addition, not a restructure).
- Redistribute the aftermath across the existing Chapter 7-9 span rather than summarizing it.
- If the dramatic-irony absence is intentional, source the middle-third tension elsewhere
  (a secondary-thread question left open across the span).

## Protected Elements

- Voice consistency across Part I — the most load-bearing strength; revision pressure on the
  middle third must not flatten it.
- The dual-POV architecture between Maya and Jonah.
- The sister-relationship arc through the close.
- The final image of Chapter 12.

## Author Decisions

### Keep

- Keep the dual POV.
- Keep the unreliable-narrator frame.

### Cut

- The prologue: fold its one load-bearing detail into Chapter 1, then let it go.

### Unsure

- Unsure whether Chapter 5 stays in Part I or moves to Part II — surface this with the author;
  the decision changes the middle-third pacing plan.

## Control Questions

1. What does the protagonist learn in the final third?
2. Whose POV closes Part II?
3. Does the prologue earn its place, or is its one detail recoverable in Chapter 1?
4. What is the cost of Chapter 7's choice, and is it paid on-page?
5. Is Chapter 5 working in its current position?
6. Does the final image land as the close intends?
7. If the dramatic-irony absence is intentional, what carries middle-third tension?

## The Strongest Case Against

If I were arguing for passing on this manuscript: the middle third asks the reader to feel the
weight of a choice the book never dramatizes, and a confident voice is doing the work that
structure should. The risk is a reader who finishes Part I engaged and drifts through the
middle before the close recovers them.

## Adversarial Reader Stress Test

A low-charity literary reader would attack the Chapter 9 turn (line 220) as "told, not
earned," and would read the dramatic-irony absence as thinness rather than restraint. Net
risk: moderate, concentrated in the middle third; the close defends itself.

## Appendix A — Diagnostic Detail

Reverse Outline (§Reader Knowledge), Reader Dynamics (§Tension Sources), and the Pacing pass
companion file carry the evidence behind the middle-third finding. No high-risk audit was
deferred.

## Appendix B — Severity Calibration

The middle-third finding was stress-tested upward and downward and held at Must-Fix in both
directions; the prologue finding held at Should-Fix.

## Appendix C — Framework Notes

Run metadata, model, run date, and pass-set provenance. Operator mode: editor scaffolding.
