# Draft-over-Draft Structural Regression Testing — did the fix break something else?

**Status:** **Built (Increment 1, 2026-06-17).** Shipped surface: `scripts/regression_diff.py` (the deterministic cross-round matcher + classifier, `--self-test`), the `validate.sh regression-diff <prior> <this>` validator (R1 + W1–W3; +1 → 44 validators, mirrored), the paired two-round fixture (`example-run-folder-r1/`, `-r2/`) wired into `--check-all`, and the round-close integration in `state-lifecycle.md` §Cross-Round Regression Check. Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) Tier 1, item 6.
<!-- built-when: scripts/regression_diff.py -->

A writer addresses the Act 2 sag the diagnosis flagged — and severs the Act 1 setup that paid off in Act 3. The next diagnostic run will *find* the new break, but it will present it as a fresh finding with no memory that the fix caused it, and no signal that a Must-Fix the writer thought they'd resolved has quietly come back. Software calls this **regression testing**, and APODICTIC has the rolling-diff *pattern* for it (`timeline-diff`, `state-card-diff`). What it does not yet have is a diff of the **whole Findings Ledger across revision rounds**: *did this revision resolve what it claimed, and did it break anything that was working?*

## The honest constraint up front: there are no cross-round finding IDs

A first design assumed finding IDs are stable round-to-round. They are not. `findings-ledger-format.md` defines `F-<ORIGIN>-<NN>` as **unique per run**, where `NN` is a zero-padded sequence *within that origin* (the pass/audit code), assigned per run. Re-diagnosing a revised draft renumbers from 01; nothing pins round N-1's `F-P5-01` to the same *finding* as round N's `F-P5-01`. Likewise there is no `resolved` sidecar state — the lifecycle is `locked → delivered → revised`, and resolution is signalled by `finding_states[id] = "revised"` plus a `<!-- resolved: F-… -->` marker in the round's Revision Report.

This constraint shapes the whole module: **cross-round finding identity is established by heuristic matching, so every regression signal is a candidate for editor judgment, not a mechanical verdict.** That is consistent with the framework's candidate-surfacing discipline (Pass 10 surfaces Timeline candidates for model judgment rather than asserting them) and with the in-house precedent for cross-round identity — `state-card-diff` tracks elements across rounds by a kind-agnostic `SE-NN` *because* prose/ID matching alone is unreliable. A future increment can harden recurrence into a mechanical signal by giving findings the same kind of durable cross-round identity; until then, this module is a disciplined candidate generator.

## What it is — and what already exists

- **Not** `finding-trace` (within-run). It traces a finding across one run's ledger → letter → revision-plan and checks the `<!-- resolved: F-… -->` marker against the rolling `finding_states` (E5). It does **not** re-diagnose a new draft or compare across rounds. Regression testing is the **cross-round** complement.
- **Not** `state-card-diff` (the State Card's curated `SE-NN` elements) or `timeline-diff` (the Timeline). Same Pass-10-class rolling-diff *pattern*, broader artifact: the full finding set.

It is the missing member of the rolling-diff family — the one that diffs *findings* — built honestly on heuristic matching rather than an ID stability the schema doesn't provide.

## Cross-round matching (heuristic) and classification

For each round N-1 finding, the diff seeks a round N match by a **concrete, deterministic** rule — a fuzzy or order-dependent matcher would make the `--check-all` output unstable, so the rule is pinned (and is the matcher's whole contract):

- **Match predicate:** same `origin` code **AND** equal chapter token (`apodictic_artifacts.chapter_token`; chapter-less findings bin to `unplaced` and match only other `unplaced`) **AND** ≥1 shared `mechanism` token after normalization (lowercase, strip punctuation, drop a small fixed stopword set). `mechanism` is free-text with no controlled vocabulary, so token-overlap is inherently fuzzy — hence every match is a candidate.
- **Score:** the count of shared normalized `mechanism` tokens.
- **Assignment (deterministic, one-to-one):** iterate round N-1 findings in ascending id order; each takes its highest-scoring eligible round-N finding; ties break by lowest round-N `NN`, then lexical id. A round-N finding, once matched, is **consumed** and cannot match another (greedy, stable).

The report records each match's **basis** (the shared origin / chapter / mechanism tokens) so the editor can confirm or reject it. Classification (all match-dependent, hence all candidates):

| Class | Meaning | Status |
|---|---|---|
| `persisted` | matched both rounds, unresolved | expected mid-revision |
| `resolved-and-held` | round N-1 finding carried a `<!-- resolved -->` marker / `revised` state **and** no round-N match | the win — candidate (the match-absence is heuristic) |
| **`recurrence-candidate`** | round N-1 finding was marked resolved/`revised` but a round-N finding **matches** it | the resolution may not have held — a regression **candidate** |
| `new` | a round-N finding with no round N-1 match, in a chapter that already had findings | ordinary new finding |
| **`new-in-quiet-chapter`** | a round-N finding in a chapter that carried **zero findings on the round N-1 record** | candidate fix-induced breakage |

Two naming/scoping honesties the review forced: the breakage class is **`new-in-quiet-chapter`**, not "clean-zone" — a ledger records findings that *exist*; it never certifies a chapter examined-and-clean, so the most it can prove is *quiet on the record* (which is indistinguishable from "examined at coarser granularity"). And it applies only to findings with a parseable chapter; `unplaced` findings cannot be classified this way and are reported as such. Neither regression class is asserted as causal — `new-in-quiet-chapter` flags a coincidence worth investigating; `recurrence-candidate` flags a heuristic match worth confirming.

## The artifact (orchestrator-written; the validator prints)

Matching the diff-validator precedent (`timeline-diff` / `state-card-diff` print to stdout and persist nothing — the `cmp -s` byte-identity machinery in `--check-all` is reserved for the *producer chain*, not for diff validators), **the `regression-diff` validator writes no file** — it emits the classification + candidates to stdout. The **`[Project]_Regression_Report_[runlabel].md`** is an **orchestrator-written deliverable** at round-close (the prose layer — exactly as the editorial letter is model-written and validator-checked), consuming the validator's output: a round-linkage header (`compares: <prior runlabel> → <this runlabel>`); the per-finding classification table with each row's **match basis**; a ranked **Regression Candidates** section (recurrence then quiet-chapter); and a verdict line (clean only when there are no unadjudicated regression candidates). So `--check-all` exercises the validator's **stdout + exit code**, not a byte-identical report file (no new fixture-diff machinery). The validator's stdout is still deterministically ordered (classification by `(chapter-token, id)`; candidates by class then id) so its output is stable to diff by eye.

## Severity honesty — resolution is falsifiable by re-diagnosis

The point is that a revision cannot *quietly* lose ground, even though the signals are heuristic:

- **A confirmed `recurrence-candidate` reverts to the round N-1 ledger severity.** There is no durable "locked severity" store across rounds; the validator reads the matched finding's severity from **round N-1's ledger** (live, the way `softness-check` reads severity within a run) and, if the editor confirms the match, the finding re-enters at that severity rather than as a fresh low-severity note. The reversion inherits the heuristic-match caveat — it is a candidate until confirmed.
- **Resolution is a claim the re-run tests.** A `<!-- resolved -->` marker says the writer believes they fixed it; a matching round-N finding is evidence they didn't. The marker is not self-certifying.
- **No silent disappearance — advisory.** A round N-1 finding with no round-N match *and* no resolution marker is an **unexplained drop candidate** (`W3`), surfaced for review — but advisory, because re-diagnosing a *changed* manuscript can legitimately drop a finding whose structure no longer exists, and per-run renumbering makes "dropped vs. renumbered" itself a heuristic call.

## The `regression-diff` validator

`validate.sh regression-diff <prior_run_folder> <this_run_folder>` (mirroring the existing `state-card-diff <prior> <current>` / `timeline-diff <prior> <current>` dispatch — `state_card_diff.py`'s `resolve()` is the two-snapshot scaffolding to copy). Delegates to `scripts/regression_diff.py`; degrades to advisory `WARN` without `python3`. It **prints** classification lines to stdout namespaced `regression-diff:<ID>` like the sibling diff validators — it does **not** persist a file (see §The artifact).

**Reuse, corrected against the tree (spec-review 2026-06-17):** parse each round's findings via `apodictic_artifacts.parse_blocks` to get `{id, mechanism, severity, evidence_refs}` per finding — **not** `finding_trace.ledger_inventory`, which returns only `{id: severity}` and is insufficient for the matcher; reuse `finding_trace.resolved_cited_ids()` for the `<!-- resolved: F-… -->` markers, and `apodictic_artifacts.chapter_token` for the chapter parse (the single shared normalizer, already used by viz + annotation).

| ID | Severity | Rule |
|---|---|---|
| **R1 — round linkage** | ERROR | The report names both rounds, both ledgers resolve and parse, and the prior round is the immediate predecessor (no skipped round silently merged). The one genuinely mechanical (non-heuristic) invariant. |
| **W1 — recurrence candidate** | WARN (ERROR under `--strict`) | One or more `recurrence-candidate` findings (a resolved/`revised` round N-1 finding heuristically matched in round N). Advisory because the match is heuristic and a writer may knowingly defer; `--strict`/round-close gates. Each carries its match basis + the round N-1 severity it would revert to. |
| **W2 — quiet-chapter breakage candidate** | WARN (ERROR under `--strict`) | One or more `new-in-quiet-chapter` findings, unadjudicated (`<!-- override: regression-cleared <runlabel>:<chapter> — investigated, not fix-induced -->`). Surfaces candidate fix-induced breakage; never asserts causation. |
| **W3 — unexplained-drop candidate** | WARN (ERROR under `--strict`) | A round N-1 finding with no round-N match and no resolution marker. Advisory (legitimate on a changed manuscript; matches `finding-trace` W1/W2/W3 and `state-card-diff` W1 posture). |

Demoting the coverage/severity checks to advisory is deliberate: `finding-trace` learned the same lesson (its coverage checks are advisory, ERROR only under `--strict`, because writes lag and work stages across sessions). Only R1 — a structural contract about the diff's two sides — is a hard error.

**Ownership boundary.** `regression-diff` owns the **cross-round findings-ledger diff**: round linkage, the heuristic match + classification, and the regression candidates — classes no other validator raises. It does **not** re-run the diagnosis (the Core Editor passes do), trace within a single run or check the sidecar-vs-Revision-Report resolution consistency (`finding-trace` E5 — distinct input: E5 is sidecar-vs-report *within* a run; `regression-diff` is report-vs-re-diagnosis *across* rounds), diff the State Card (`state-card-diff`) or Timeline (`timeline-diff`), or re-check letter severity fidelity (`softness-check`).

## Canonical `--check-all` gate

A worked example — two committed fixture run folders (`example-run-folder-r1/`, `example-run-folder-r2/`) where r1 marks a finding `revised` and r2's re-diagnosis contains a finding whose `mechanism`/chapter **heuristically match** it (a `recurrence-candidate`), plus an r2 finding in a chapter r1 left quiet (`new-in-quiet-chapter`) — is added, and `validate.sh --check-all` runs `regression-diff` across them, asserting the validator's **exit + stdout** (round linkage `R1` clean; the matcher raises the two candidates `W1`/`W2` under `--strict`, with correct match bases and severity reversion) — **not** a byte-identical report. The fixture demonstrates **heuristic matching**, not ID equality (which the framework does not guarantee), keeping the fixture honest. **The fixture is net-new authoring** — the existing `example-run-folder/` has a single locked finding and no revision artifacts, so it cannot be "extended"; the precedent to copy is the committed `example-state-card.md` + `example-state-card-round2.md` pair already wired into `--check-all`. Both new round folders must themselves stay gate-valid (`ledger-check` / `structured-findings` / `deficit-lock` pass), as the existing fixture headers demand.

## Increment plan

**Increment 1 (this spec):** `scripts/regression_diff.py` (the deterministic cross-round matcher + classifier of §Cross-round matching, parsing via `apodictic_artifacts.parse_blocks` + reusing `finding_trace.resolved_cited_ids` and the `state_card_diff.resolve` two-snapshot scaffolding), `validate.sh regression-diff` (+ a `regression-diff --self-test` so it joins `--self-test-all`), the orchestrator-written Regression Report, round-close integration in `state-lifecycle.md`, the net-new paired two-round fixture, and the `--check-all` gate. **Validators +1 → 44**: a lockstep bump in **both** `scripts/validate.sh` and `plugins/apodictic/scripts/validate.sh` (check-mirror enforces byte-identity) of `AGG_VALIDATORS`, the `Commands:` usage list, and the `--check-all` description string, plus the new dispatch arm.

**Future increments (not built):**
- **Cross-round finding identity (the hardening prerequisite).** Give material findings a durable cross-round identity (the `SE-NN`/State-Card precedent), so `recurrence-candidate` can become a mechanical `recurred` signal and the matcher's heuristics become a confirmation aid rather than the basis. This is the increment that would let regression testing assert rather than suggest.
- **Visual regression diff** — render the two ledgers' severity maps side by side via [Manuscript-Structure Visualizations](manuscript-visualizations.md).
- **Causal-candidate ranking** — rank `new-in-quiet-chapter` findings by structural proximity to the round's *addressed* findings (prioritization, still never an asserted cause).

## Self-review (Increment 1)

- *Why everything is a candidate* — per-run IDs mean cross-round identity is heuristic; honesty requires that recurrence and quiet-chapter breakage both be candidates for judgment, and that only R1 (the diff's structural contract) be a hard error. The earlier draft called recurrence "hard, mechanical, no judgment" — exactly backwards, since recurrence is the signal most dependent on the unreliable ID-equality assumption.
- *Why the coverage gates are advisory* — re-diagnosing a changed manuscript legitimately drops findings; an ERROR there would false-fail ordinary revision, the lesson `finding-trace` already encodes.
- *Why it still earns its place* — even as a candidate generator, nothing else in the framework looks across rounds at the full finding set; surfacing "this might have come back" and "this chapter was quiet and now isn't" is real signal a single-round diagnosis structurally cannot produce. The hardening increment makes it sharper later without changing its shape.
