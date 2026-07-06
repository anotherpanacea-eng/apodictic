# Roosevelt — Cross-Vendor GPT Pass 2 (n=1 → n=2)

**Status: READY-TO-RUN, NOT YET RUN.** This is a recorded operator packet. The
GPT run itself is operator-driven (paste a prompt into a GPT chat box and save
the reply); it is not executable from an automated session here — there is no
OpenAI harness in this repo and no credentials are wired in. Do **not** hunt for
API keys; run it by hand per the steps below.

## Why this run exists

`roosevelt-democratic-abundance` is a load-bearing, low-recognition calibration
fixture (SOUND with one registered Should-Fix soft spot). Its cross-vendor result
so far is **n=1**: one blind GPT-4 pass (2026-06-04), which independently — with
**no recognition** — classified the piece **SOUND** and located the failure in the
**warrant** layer, exactly where the registered key puts it. That is a strong
result, but a single draft leaves the "it was just variance / a lucky sample"
objection open. A **second independent GPT pass** kills that objection: if pass 2
reproduces the pass-1 anchor pattern, the roosevelt cross-vendor read is stable,
not a one-off draw.

This does not need a *new* vendor — it needs a *second sample from the same
independent vendor* to establish within-vendor reliability for this one fixture.

## Pass-1 baseline (what we are trying to reproduce or overturn)

Source of record:
`evals/results/cross-vendor-gpt-20260604/roosevelt-democratic-abundance__gpt4.md`
and its `SCORECARD.md` (both in-repo). Scored against the amended key:

| Anchor | Key (GT) | GPT-4 pass 1 | Score |
|---|---|---|---|
| **Q1 / GT1 claim** | rebuild abundance around democracy + labor + public capacity, vs deregulation | recovered (C0) | **3** |
| **Q2 / GT2 locus** | unearned **WARRANT**: labor-as-it-is delivers democratic abundance (participation↔speed reconciliation, or current↔reformed motte-and-bailey) | fired WR3 warrant-under-articulated + FM-A6 Warrant Leap → correct **warrant layer**, weak/partial hit | **2** |
| **Q3 / GT3 objection** | safeguards **recreate the procedural veto points** the abundance critique targets (remedy reintroduces the diagnosed problem) | **missed** — named BP5 missing-alternatives / OB2 evasion (a downstream burden issue, not veto-point regress) | **0** |
| **Q4 / GT4 audience** | foreground participation-vs-speed reconciliation; don't accept the reframe just because it's congenial | partial | **2** |
| **Q7 / GT7 Distinguish** | **SOUND** (competent reframe, real internal tension = Should-Fix; not UNSOUND) | **SOUND** | **3** |

- **Anchors hit: 4/5.** Recognition: **NO** (GPT did not recognize author/title/critique).
- The one clean miss (GT3 veto-point regress) is an **engine-general blind spot** —
  Opus, Sonnet, and GPT all missed it (per the cross-vendor SCORECARD). Pass 2 is
  **not** expected to fix that; it tests the *stability of the SOUND + warrant-hit*
  result.

## The fixture, prompt, and procedure

- **Fixture slug:** `roosevelt-democratic-abundance` = **`submission-04`** in the
  blind-upload map (`argument-benchmark-runbook/SUBMISSION-MAP.csv`).
- **Prompt to paste (verbatim, one message):**
  `~/Library/CloudStorage/Dropbox/Cowork/Development Editor/argument-benchmark-runbook/prompts/roosevelt-democratic-abundance.txt`
  This file is byte-identical to what Opus/Sonnet/GPT-pass-1 saw: the same header,
  the full inlined `dialectical-clarity.md` audit reference, and the stripped
  submission body under the neutral label "Submission X". **It contains
  third-party copyrighted text and stays in Dropbox — never commit it to git.**
  (If uploading a zip instead of pasting, use `submission-04` from
  `argument-benchmark-runbook-blind-upload.zip`, whose filenames are scrambled to
  hint-free labels; never hand over `-full.zip`, whose slug names leak the source.)
- **Procedure** (this is the blind **runner** role only — see
  `evals/fixtures/argument-benchmark/RUN-PROTOCOL.md` §Step 2):
  1. Open a **fresh** GPT chat — new conversation, no memory / custom
     instructions, **web browsing / tools OFF** (hardens against the model looking
     the piece up instead of diagnosing it).
  2. Paste the entire prompt file as the first message. It is large (~120 KB,
     audit reference inlined); if the box rejects it, use file-upload / long-context
     mode — it must arrive intact in one turn.
  3. Let it produce the full 9-step Dialectical Clarity diagnosis: code families
     AT/AC/CL/SM/WR/BP/OB/DI/NE, named patterns FM-A1..FM-A20, ending with a
     Step-9 Distinguish verdict (SOUND / UNCONVENTIONAL-BUT-EFFECTIVE / UNSOUND)
     and a priority diagnosis (primary structural break, FM-A pattern, severity
     ranking, first repair target).
  4. It should end with a `RECOGNITION:` line. If it omits it, paste
     `argument-benchmark-runbook/recognition-probe.txt` as a **second** message and
     append the answer to the saved file. (The recognition line is data, not a
     flaw — we expect **no** recognition on roosevelt and want to confirm it.)
  5. **Do not score in the run chat**, and never paste any `groundtruth.md`,
     `SOURCES.md`, `CORPUS.md`, the rubric, or the spec.

## What to record

Save the model's **entire** reply, unedited, as:

```
evals/results/roosevelt-gpt-pass-2/roosevelt-democratic-abundance__<modeltag>.txt
```

Use a distinct `<modeltag>` for the model actually used (e.g. `gpt4-pass2`,
`gpt5`) so the scorer can tell pass 2 from pass 1. If the reply contains
copyrighted submission text, keep it Dropbox-side and commit only the scorecard
(force-add per `evals/results/README.md`); a pure diagnosis (codes + prose about
the argument, no reproduced source) is a permitted, force-addable artifact.

Then **score in a separate session with repo access** against
`evals/fixtures/argument-benchmark/roosevelt-democratic-abundance/groundtruth.md`
on the rubric's 0–3 bands, and write a `SCORECARD.md` in this directory recording:

- Q1/Q2/Q3/Q4/Q7 for pass 2, and anchors-hit /5.
- The `RECOGNITION:` line verbatim.
- A pass-1-vs-pass-2 reliability line: on how many of the five anchors do the two
  GPT passes make the **same** call (both hit or both miss)?

## Kill vs confirm — the variance objection

The objection under test: *"roosevelt's clean blind-GPT SOUND + warrant-hit was a
single sample; maybe a re-draw lands elsewhere — it was variance, not signal."*

- **CONFIRMS (variance objection dies):** pass 2, still blind (`RECOGNITION: no`),
  again returns **GT7 = SOUND** *and* locates GT2 in the **warrant** layer
  (WR-family / FM-A6-style warrant-leap on the labor→abundance bridge), i.e. it
  reproduces the pass-1 Q1=3 / Q2≈2 / Q7=3 spine. Two independent GPT draws
  agreeing on claim + warrant-locus + SOUND ⇒ the roosevelt cross-vendor read is
  **reliable within vendor**, not a lucky single sample. (GT3 veto-point-regress
  may still be missed — that's the known engine-general blind spot, not part of
  this test.)
- **KILLS / weakens (objection has teeth):** pass 2 diverges on the load-bearing
  anchors — e.g. flips **GT7 to UNSOUND** (over-pathologizing the tension), or
  **mislocates GT2 off the warrant layer** (routes the primary break to the
  burden/objection layer, BP/OB, which the key marks as *not* a GT2 hit), or newly
  **recognizes** the piece (`RECOGNITION: yes`, which would make pass 1's blindness
  the anomaly). Any of these means the pass-1 result was **not** stable and the
  variance objection stands — record it honestly and treat roosevelt's
  cross-vendor read as unsettled (candidate for a third pass or a human editor).

Report the outcome on the two axes from RUN-PROTOCOL §Step 4 (Accuracy = pass-2
vs key; Reliability = pass-1 vs pass-2), not a single "converged?" binary.

## Pointers

- Protocol: `evals/fixtures/argument-benchmark/RUN-PROTOCOL.md`
- Cross-vendor paste runbook (Dropbox, copyright-bearing prompts):
  `~/Library/CloudStorage/Dropbox/Cowork/Development Editor/argument-benchmark-runbook/README.md`
- Pass-1 result + scorecard: `evals/results/cross-vendor-gpt-20260604/`
- Key: `evals/fixtures/argument-benchmark/roosevelt-democratic-abundance/groundtruth.md`
- Rubric: `evals/rubrics/argument-benchmark.md`
