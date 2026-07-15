# Register & Stance Triage — Pilot Runs (2026-07-15)

Pilot runs for `docs/argument-register-stance-triage-spec.md` (see its Appendix B for the full
results synthesis). Seven blind Opus auditors across three waves; none saw the spec, the expected
outcomes, or each other.

## Contents

- `fixture-oped.txt` — "The Feed Experiment," purpose-built fallacious op-ed (E3-shape: declares
  the lens register in ¶1, then commits fabricated precision, anecdote-to-principle, evidence
  laundering, motte-and-bailey, ad-hominem-as-rebuttal, and a full-press federal-ban cash-out
  under exploratory cover). Synthetic; all statistics and studies within are invented.
- `fixture-testimony.txt` — E4 fixture: competent municipal budget testimony (AT3 through AT4
  voice) containing one self-flagged mock-heroic flourish (the stakes-gate probe) and one planted
  unearned superlative (the gate-mootness control). Synthetic; all figures invented.
- `nietzsche-socrates.txt` — E5 fixture: "The Problem of Socrates," *Twilight of the Idols*
  (Nietzsche, 1889), public-domain Ludovici translation via Project Gutenberg (#52263), translator
  footnote stripped. A real canonical polemic, used instead of a pastiche to break the
  same-author confound on the earned side.
- `fixture-motte.txt` — E6 fixture: "The Willpower Myth," bare motte-and-bailey (sincere register,
  no lens cover, cultural cash-out keeping consequence context LOW so stance demotion stays
  available and must be refused on the merits). Bailey deliberately styled to tempt an S3
  productive-overstatement reading. Synthetic.
- `machinery-addendum.md` — the blinded candidate machinery (spec Parts 1–2 stripped of worked
  examples and expected outcomes) given to every machinery-arm auditor. Validated as
  auditor-followable across four runs; this is the artifact to evolve into the real
  dialectical-clarity.md changes.

## Not vendored

- Mediocratopia Ch. 7 (Venkatesh Rao) — fetch from
  https://books.venkateshrao.com/mediocratopia/read/mediocratopia-7.html at run time; strip nav
  chrome to the ~1,005-word body. Copyrighted; analysis input only, do not commit the text.

## Results

Wave 1 (2×2 contrast pair):

| Run | Text | Rubric | MF/SF/C/O | Verdict |
|-----|------|--------|-----------|---------|
| A1 | Rao Ch. 7 | base | 0/4/7/5 | WARRANTED (unconventional) |
| A2 | fixture-oped | base | 0/14/2/1 | WARRANTED (evaluability) |
| A3 | Rao Ch. 7 | + machinery, register confirmed | 0/2/2/5 | succeeds as AT5; GN4 + OB3 live |
| A4 | fixture-oped | + machinery, register claimed | 4/21/4/4 | UNWARRANTED; register rejected |

Wave 2 (E4/E5):

| Run | Text | Rubric | MF/SF/C/O | Verdict |
|-----|------|--------|-----------|---------|
| B4 | fixture-testimony | + machinery, stakes gate ACTIVE | 0/2/2/2 | WARRANTED; demotion blocked-and-recorded |
| B5 | nietzsche-socrates | + machinery, asserted, demotion available | 0/5/3/4 | WARRANTED as polemic; 4 demotions, no halo |

Wave 3 (E6):

| Run | Text | Rubric | MF/SF/C/O | Verdict |
|-----|------|--------|-----------|---------|
| B6 | fixture-motte | + machinery, asserted, demotion available | 3/8/4/0 | UNWARRANTED (scope-honesty); S3 rescue refused |

Headlines: separation widened in both directions (A3 vs A4); the cash-out inventory, not the GN
codes or stance taxonomy, is the load-bearing mechanism (it flipped the fixture from
evaluability-WARRANTED to a disowned-causal-bridge defeat); the stakes gate blocked exactly one
demotion and recorded the block (B4); no halo effect on Nietzsche — earned rhetoric demoted while
the sincere master warrant and the self-undermining structure held at Should-Fix (B5). Doctrinal
finding: the construct draws the earned/unearned line at evidentiary function, not intent —
Nietzsche's dying-words misreading audits unearned because it is unmarked, load-bearing evidence,
however productive. Five of six runs surfaced a genuine finding beyond the fixture design.

The E5+E6 pair is the construct's sharpest validation: two texts with near-identical surface
boldness ("there is no willpower" vs. Nietzsche's eliminativism about Socrates) drew opposite
verdicts for articulated reasons — the polemic survives being seen as polemic; the motte-and-bailey
needs its literal claim and collapses under detection. The S3 rescue was explicitly considered and
refused with demotion available (B6), so the construct's central failure mode — stance triage as a
fallacy-laundering pathway — did not occur under deliberately tempting conditions.

Eval-gate status: E1–E6 green; **E7 (good-faith hybrid, per-span stakes gate) specified in the
spec's §Validation and must run before the reference-file merge.**

**Post-review notes (2026-07-15).** The spec passed through the adversarial spec-review swarm
(NEEDS-REWORK → reworked; see spec §Review Disposition). Two consequences for this directory:
(1) all pilot ledgers use a run-harness-injected 4-band severity scale (MF/SF/Consider/Observational);
the engine's canonical vocabulary is exactly Must-Fix/Should-Fix/Could-Fix — remap Consider and
Observational to **Could-Fix** when comparing against future runs. (2) `machinery-addendum.md`
predates the rework: it places stance triage at Step 9 and demotes to "Observational"; the reworked
spec relocates calibration to Triage (upstream of the Deficit Lock) and demotes to Could-Fix. The
addendum remains valid as the historical pilot artifact; derive build language from the spec, not
the addendum. The evidentiary-function doctrine was ratified for build 2026-07-15.
