# Native argument readings of the baseline passes — spec (apodictic)

**Status:** **Proposed (unbuilt).** Waiting for the owner to admit it. Do not build until the owner admits it. When built, the build PR flips this line (`AGENTS.md` § Review practices).
**Estimate:** one prose-and-routing PR, about 30 lines across three files. No new pass, validator or schema.
**Provenance:** deferred finding 3 of the external Codex framework review of 2026-10-16 (private document; summarized here, not quoted). Burndown card OCA-9. Line references are to `main` after the 2026-10-26 train (#398).

---

## The deferred finding

Argument-shaped runs use the fiction baseline passes (0, 1, 2, 5, 8). The pass specs talk about scenes, POV, inciting incidents, thresholds, midpoint/crisis/climax, character wants, fears and "lies", and who-knows-what-when. Nothing tells the pass what those mean for an argument, so the model has to improvise the translation. Separately, Dialectical Clarity is described as always applying to argument runs, but its tier is "auto-recommend before synthesis", which the writer can decline. So a run can take the argument path without the analysis that defines it. The review calls this an instruction-contract problem: it does not show that outputs fail today. Its suggestion is to keep the shared ledger, contract, synthesis and state, define the argument reading of each pass directly, make a compact Dialectical Clarity kernel part of every full argument diagnosis, and leave address and testimony with their existing non-propositional handling.

## What `main` does today

- `plugins/apodictic/skills/nonfiction-argument-engine/SKILL.md:154-158` — "the SAME pass set as the fiction path (Passes 0, 1, 2, 5, 8 …). Argument-specific passes are handled by the audit cluster, not by new passes."
- `nonfiction-argument-engine/SKILL.md:151` — "Auto-recommend before synthesis: Dialectical Clarity (always for argument-shaped runs)". That statement exists only here. The argument routing fragment has no unconditional Dialectical Clarity row: its only rows are the pre-draft route (`skills/core-editor/references/argument-audits-routing.md:22`) and the Pass 9 finding trigger (`:48`).
- Tier meanings are in `skills/core-editor/references/pass-dependencies.md` §4c (`:214-223`). **Auto-run** (`:220`) loads without confirmation and must finish before synthesis. **Auto-recommend before synthesis** (`:222`) can be declined, and a decline is recorded as a blind spot.
- The floor is `pass-dependencies.md:74` and `:99`, and `run-core.md:130`. The fiction semantics are in `skills/core-editor/references/run-core.md`: Pass 0 "For each scene" `:416`; Pass 2 scene outline and plot beats `:469-470`; Pass 5 want, fear and "lie" `:504-508`; Pass 8 who-knows-what matrix `:537`.
- Pass subagents get the manuscript, contract and ledger (`run-core.md:186`). The run-core pass specs never point an argument run to the engine skill, which is loaded only on delegation (`skills/core-editor/SKILL.md:156`).
- Dialectical Clarity steps that already exist and that the kernel reuses: Step 1, type and audience (`argument-audits/references/craft/dialectical-clarity.md:132`); Step 2, claim ladder (`:222`); Step 3, support map (`:277`); Step 4, warrant (`:334`). Step 4 runs on the subclaim-support pairings Step 3 produces (`:338`), so a kernel with warrant analysis needs Step 3. Its applicability and span-function rules (`:117-130`) already protect address, testimony and illustration spans.

## Smallest change

1. **Argument readings, in the engine skill (about 15 lines).** Replace `nonfiction-argument-engine/SKILL.md:154-158` with a five-row table that keeps each pass's number, artifact name and ledger format but defines what it builds and detects on an argument:

   | Pass | Argument reading |
   |---|---|
   | 0 Reverse Outline | Per section: the rhetorical move and the claim it makes; measured word counts kept |
   | 1 Reader Experience | Comprehension, relevance and uptake by the contract's declared audience; orientation failures = where the reader loses the claim; belief failures = a step the audience would not accept |
   | 2 Structural Mapping | Claim-dependency map: which claims rest on which, where warrants are missing, how far each claim extends (scope), where objections are placed; proportional analysis kept |
   | 5 Character Audit | The argument's commitments and burdens; character analysis only for embedded narrative (Dialectical Clarity Step 7 handles narrative-as-evidence) |
   | 8 Reveal Economy | When definitions, evidence, qualifications and necessary context arrive relative to the claims that need them |

   Add two sentences. First: the fiction terms in the run-core specs (scene, beat, inciting incident, midpoint, climax, want/fear/lie, who-knows-what) do not apply, and their absence is never a finding. Second: under an `ADDRESS` C0 (`SKILL.md:138-141`) or a confirmed span function, Passes 2 and 5 do not impose a proposition ladder.
2. **Point the passes at it (1 line).** In `run-core.md` §Pass Resolution (`:128-132`), add: on argument-shaped runs, each pass also reads its row in `nonfiction-argument-engine/SKILL.md` §3, and that row goes into the pass's dispatch. This is the one addition to an always-loaded file.
3. **Kernel on the floor (about 3 lines).** Change `SKILL.md:151` to: **Auto-run: Dialectical Clarity kernel (Steps 1–4)**, with the full audit still available on request or by trigger. Add the matching §4a row to `argument-audits-routing.md` (`:20-24`) so the routing table, not just the skill, states it.
4. One `changelog.d/` fragment.

## Behavior it protects

- A short policy memo with no characters gets an argument diagnosis. The run does not invent an arc, ask for a climax, or log "no inciting incident" as a finding.
- Every full argument diagnosis includes the warrant analysis that defines the route; a decline at the auto-recommend prompt can no longer drop it.
- Address and heard testimony keep their existing non-propositional treatment.

## Deletion test

- **Nothing added.** No new pass number, validator, Argument_State field or gate. The readings reuse existing artifacts and existing Dialectical Clarity steps.
- **Moving the kernel from Auto-recommend to Auto-run** changes a tier and adds no mechanism. Without it, the decline path stays open, and a declined run is an argument diagnosis with no warrant analysis. That gap is disclosed as a blind spot, but it is the gap the review names.

## Acceptance check

A manual run on two public fixtures, read by hand and recorded in the build PR:

1. A short policy-style argument from `evals/fixtures/argument-benchmark/` → the pass artifacts contain no fiction vocabulary and no findings about missing arcs or climaxes, and the ledger carries kernel output (AT/AC, CL, SM, WR codes) before synthesis.
2. An address or heard-testimony text → `ADDRESS` C0 handling as today, with no proposition ladder imposed.

The routing change is a table edit, so if any registry or dashboard reads that table, run `release-generate.mjs --check` and `validate.py --check-all` (`AGENTS.md` § Review practices).

## Owner questions

1. **Kernel steps:** 1–4 (this spec; Step 3 is there because Step 4 consumes its support pairings), or also 5 (burden and scope) or 6 (objections)? A smaller option is Steps 1, 2 and 4, with the argument reading of Pass 2 producing the subclaim-support pairs Step 4 needs. That pairing would come without Step 3's scheme hints.
2. **Kernel tier:** Auto-run (this spec; cannot be declined), or keep auto-recommend before synthesis and add only the missing routing row (smaller, but the decline stays)?
3. **Where the readings live:** in the engine skill (this spec; fiction runs never load it, plus one pointer line in `run-core.md`), or as an "Argument run:" line under each pass in `run-core.md` (grows the always-loaded file OCA-5 just trimmed)?
4. **Pass 5 on arguments with no embedded narrative:** read it as commitments and burdens (this spec, the review's mapping), or drop Pass 5 from the argument floor? Dropping is smaller, and it overlaps Dialectical Clarity Step 5.
