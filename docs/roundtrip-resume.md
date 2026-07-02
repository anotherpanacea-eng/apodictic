# One-Click Round-Trip Resume at `/start`'s `revising` node — build spec (apodictic)

**Status:** **Built** (2026-07-01, this PR — `reanchor.py disposition` + `validate.sh roundtrip-disposition` RT1–RT4/W1 + `rev-a4` + the `/start` revising/diagnosed offers; spec-review pass 1 folded, BUILD-READY-WITH-FIXES 0 P1; Opus build-review READY-TO-PR, 0 P1/P2, 1 P3 folded; Codex review P2 folded — RT4 partition coverage closes the omitted-row hole). **Estimate:** 1–2 build sessions, single PR (two increments as commits). **Owner of the decision:** editorial.
<!-- built-when: plugins/apodictic/skills/core-editor/references/example-roundtrip-disposition.md -->
**Provenance:** merged candidate — Fable "revision-round diff ingestion" re-scoped down after code
verification + Opus 4.8 "close the last mile" (whose scoping the code supports).

---

## Anchor corrections (stub vs repo, verified 2026-07-01)

Every stub anchor was re-verified against the tree. Four refinements; nothing load-bearing was wrong:

1. **`reanchor.py` usage** — the stub compressed three signatures into one. Actual (`plugins/apodictic/scripts/reanchor.py:39-43`): `reanchor <prior_run_folder> <new_snapshot> [--strict]` and `emit <prior_run_folder> <new_snapshot> [-o <out_dir>]` take **two** positional args; only `crossref <prior_run_folder> <new_snapshot> <this_run_folder> [--strict]` takes three. `emit` writes into `-o` (defaulting to the prior folder — so the flow below must always pass `-o <new_run_folder>`).
2. **Build dates** — the `reanchor` **validator** (Increment 1) is 2026-06-17 (ROADMAP.md:404); the **workflow glue** (`emit`/`crossref`, Increment 2) is 2026-06-20 (ROADMAP.md:715-722, `docs/annotated-manuscript-reanchoring.md:3`). The stub dated both as 06-17.
3. **Anchor-fate classes** — the stub's disposition list ("held / moved / vanished / ambiguous") omits the fifth class, **`not-re-anchorable`** (`line-range` only; `reanchor.py:61` `_CLASSES`). RA3 enforces a five-way exhaustive partition; the disposition surface must present all five.
4. **Gate inventory** — the stub said "RA1–RA3 + W1". Actual: `reanchor` = RA1–RA3 + **W1/W2**; `regression-diff` = R1 + **W1–W3**; `crossref` additionally raises **X1** (`crossref:contradicted-resolution`, advisory / ERROR `--strict`). All confirmed in `reanchor.py:20-28`, `docs/draft-regression-testing.md:59-64`.

Confirmed as stated: ROADMAP.md:727 ("*round-trip is reachable today via the Revision Round Protocol, but not yet a one-click resume offer*" — inside "Toward truly great" #2, ROADMAP.md:704-730); `plugins/apodictic/commands/start.md:50` (the `revising` row dispatches to revision-coach §Loop Dispatch only); the round-trip glue chain `--check-all` gate (`plugins/apodictic/scripts/validate.sh:597-647`); `state-lifecycle.md` §Round-Trip Re-Anchoring (`plugins/apodictic/skills/core-editor/references/state-lifecycle.md:137-167`).

## Problem & verified evidence

The round-trip revision loop is **built but not surfaced**. A returning writer's revision intake is still author-reported (`state-lifecycle.md:82-87` — "What changed? Which flags were addressed?"), and the machinery that answers those questions mechanically is reachable only by knowing to run the multi-step Revision Round Protocol by hand.

- `plugins/apodictic/scripts/reanchor.py` — `reanchor` (classify: held / moved / vanished / ambiguous / not-re-anchorable), `emit` (write the re-anchored manifest + revision-aware annotated copy, RA1–RA3 re-gated before any write), `crossref` (join anchor classes × `regression-diff` finding classes by `finding_id`). Built; wired into `--check-all` (`round-trip glue chain`, validate.sh:597-647).
- `plugins/apodictic/scripts/regression_diff.py` — W1 recurrence-candidate / W2 new-in-quiet-chapter / W3 unexplained-drop, advisory (ROADMAP.md:462).
- `plugins/apodictic/commands/start.md:50` — the `revising` node's dispatch: "the revision-loop dispatcher — §Loop Dispatch … the stored `next_action` (`revision_round`/`coaching`) is its default." **No round-trip offer.**
- ROADMAP.md:727 — the maintainer's own framing: reachable via the protocol, "*but not yet a one-click resume offer*."
- The gap has a proven in-repo template: the `diagnosed` node already carries a **conditional sibling offer** ("regenerate the marked-up copy from this run?", start.md:55) keyed on a **file glob, not a new `next_action` enum** — the exact shape this spec reuses.

## The decision it changes

Which findings get marked resolved and which sections get re-diagnosed, each revision round — decided from **anchor ground truth + regression candidates presented for confirmation**, instead of from author memory. And whether the writer returns for round 2 in-tool at all: "a one-shot letter is a product; a revision loop in the writer's tool is a habit" (ROADMAP.md:722).

## What it is — the resumed flow (M1)

At the **bound-project `revising` node** (derived by `lifecycle_node.py:84-87`, `revision_progress.steps_complete > 0`), before entering Loop Dispatch, `/start` checks **round-trip eligibility** and, when eligible, adds the offer to the node's prompt.

**The offer ALSO appears at the bound-project `diagnosed` node** (same eligibility predicate, same chain). A writer who took the letter away and revised offline returns with `revision_progress.steps_complete == 0` and derives `diagnosed`, not `revising` — exactly the "came back with a new draft" case this feature targets. The `diagnosed` node already hosts a conditional sibling offer on this pattern (start.md:55), so this is a two-line start.md extension of the proven conditional-offer shape. **Operator call (default folded 2026-07-01, reviewers recommend; override before build if disagreed).**

**Eligibility predicate (mechanical, no new state):** `python3` is available **and** a prior run folder under the project root holds a `*_Annotation_Manifest_*.md` (the glob `annotation_manifest._MANIFEST_GLOB` — the `Reanchored_` infix is excluded by name, by the Increment-2 design, so a carried-over manifest never masquerades as a prior diagnosis). If **several** run folders qualify, list them and let the author pick (the start.md:55 multiple-runs rule); never diff against an unnamed run silently.

**The node prompt** (start.md two-option discipline — never a bare yes/no) becomes, when eligible:

- **"Returning with a revised draft?"** → the round-trip resume chain below.
- **"Continuing to work the plan?"** → §Loop Dispatch exactly as today (the stored `next_action` stays its default).

(When ineligible — no prior annotated run, or no `python3` — the row behaves exactly as today; see §Degrade paths.)

**The chain (on accept — every step is an existing, gated surface; the offer only sequences them):**

1. **Reset check first.** Run the Revision Round Intake questions' reset triggers (`state-lifecycle.md:169-176` §When to Reset): >40% structural change, POV/tense/timeline change, "I basically rewrote it," or a >6-month-old diagnostic → route to fresh full analysis, not the round-trip.
2. **New run folder + snapshot.** Create `runs/<runlabel>/` (runlabel = date_model, per output-structure) and snapshot the revised draft as `[Project]_Manuscript_Snapshot_[runlabel].md` (LF, trailing newline, no other change — `state-lifecycle.md:143`).
3. **Classify, show, emit.** `validate.sh reanchor <prior_run_folder> <new_snapshot>` — present the five-class partition ("N held, N moved, N vanished — candidate wins; N need your placement"). On accept: `scripts/reanchor.py emit <prior_run_folder> <new_snapshot> -o <new_run_folder>` (RA1–RA3 re-gated before writing; refuses to write otherwise). **Exit (a) — carry-only:** the writer may stop here with the revision-aware marked-up copy and keep revising; nothing has touched finding state.
4. **Targeted re-diagnosis (optional continuation).** The Revision Round Protocol's targeted pass sequence (`state-lifecycle.md:102-109`) into the new run folder — a fresh ledger with renumbered `F-…` ids.
5. **Cross-round evidence.** `validate.sh regression-diff <prior_run_folder> <new_run_folder>` + `scripts/reanchor.py crossref <prior_run_folder> <new_snapshot> <new_run_folder>` (the §Q2 orchestrator join — W1/W2/W3 + X1).
6. **Disposition proposals → operator confirmation → governed writes.** Present a **per-finding disposition table** (schema below): each prior-round finding with its anchor class, its regression class when matched, and a **proposed** disposition. The operator confirms/overrides each. Only then: write the disposition record (with the confirmation token), write `<!-- resolved: <id> -->` markers into the Revision Report **for confirmed findings only**, and advance lifecycle state through the existing writers — the `revision_round` gate (`validate.sh gate revision_round <run_folder>` → `gate --attest`) for runner-governed projects, the scoped direct write for non-governed (`state-lifecycle.md:120-125`, `docs/revision-round-gate.md`). **Exit (b) — round-close.**

The model **proposes; the operator disposes** (the Loop Dispatch motto, revision-coach/SKILL.md:91). A `vanished` anchor or a `resolved-and-held` regression class is evidence *presented*, never a resolution *asserted*.

## Exact touch-points

| File | Change |
|---|---|
| `plugins/apodictic/commands/start.md` | `:50` `revising` row **and** `:51` `diagnosed` row gain the conditional round-trip offer (the `diagnosed` extension is the folded operator call above — two lines on the proven :55 conditional-offer pattern); a new note block below the table — "**`revising`/`diagnosed` — Round-trip resume (no new command).**" — mirrors the `diagnosed` note (:55): eligibility glob + python3 check, multiple-prior-runs listing, the 6-step chain by reference to `state-lifecycle.md` §Round-Trip Re-Anchoring, the two exits, and the no-new-`next_action` rule. |
| `plugins/apodictic/skills/core-editor/references/state-lifecycle.md` | §Round-Trip Re-Anchoring gains **step 4 — Disposition & round-close**: the disposition table, the **hard-sequenced** confirmation token (written ONLY after every row has been presented and confirmed — sequencing, not a soft checkpoint), confirmed-only resolved markers, then the existing governed/direct lifecycle-advance path (:120-125) unchanged. A pointer line notes `/start` now surfaces the flow at the `revising` and `diagnosed` nodes. |
| `plugins/apodictic/skills/revision-coach/SKILL.md` | §Loop Dispatch (:81): one pointer sentence — at the `revising` node, `/start`'s round-trip offer precedes the ladder when the writer returns with a new draft; the ladder remains the decider otherwise. |
| `plugins/apodictic/scripts/reanchor.py` (+ root `scripts/` mirror) | New `disposition <prior_run_folder> <new_snapshot> <this_run_folder>` subcommand (RT1–RT3 + W1 below) + `--self-test` cases. Already in the `check-mirror` set — both copies byte-identical. |
| `plugins/apodictic/scripts/validate.sh` (+ root mirror) | New `roundtrip-disposition` arm delegating to `reanchor.py disposition`; `AGG_VALIDATORS` +1 (**count is derived — no literal to bump**, per validator-conventions M3); `Commands:` usage list; `--check-all` description string; the `--check-all` fixture step (§Fixture plan). Byte-identical mirror (check-mirror). |
| `plugins/apodictic/execution-gates.v1.json` | `revision_round.entry_requires.attested` += **`rev-a4`**: "when a `*_Roundtrip_Disposition_*` record exists in the run folder, every disposition was confirmed by the author — no vanished-anchor auto-close." Per-event `attested_contract` recording means existing fixture events stay valid (run_gate.py's contract is event-scoped); only new clears pick up the new item. **No `entry_requires.checks` addition** — the check plumbing targets single-folder artifacts and `run_checks` treats validator WARNs as gate-WARNs (the `docs/revision-round-gate.md` build lesson); the standalone validator covers it. |
| `docs/annotated-manuscript-reanchoring.md` | Status line gains Increment 3 (this spec) on build; §The artifacts gains the `disposition` subcommand row. |
| `ROADMAP.md` | :727 remaining-note resolved on build ("surfaced as the `/start` `revising`-node resume offer, <date>"). |
| `changelog.d/` | Fragment (repo convention — dir verified present). |

**No new command, no new `next_action` enum value, no schema file.** The eligibility condition is a file glob (the `diagnosed`-node precedent, start.md:55: "the condition is this glob, **not** a `next_action` value (do not invent one)").

## New artifact — the Roundtrip Disposition record

`[Project]_Roundtrip_Disposition_[runlabel].md`, orchestrator-written into the **new** run folder at step 6. Marker-based (the `<!-- resolved: … -->` / override-marker family), **not** an `apodictic.*.v1` JSON block — no schemas/ file, no schema-coverage binding row (deliberate: this is a per-round operator record, not a diagnostic artifact; adding a schema would drag M4/schema-coverage machinery for no diagnostic payload).

```markdown
# Roundtrip Disposition — [Project] [runlabel]
compares: <prior runlabel> → <this runlabel>

| finding | anchor class | regression class | proposed | decision |
|---|---|---|---|---|
| F-P5-01 | vanished | resolved-and-held | confirm-resolved | confirm-resolved |
...

<!-- disposition: F-P5-01 anchor=vanished regression=resolved-and-held decision=confirm-resolved -->
<!-- disposition: F-P2-03 anchor=held regression=recurrence-candidate decision=keep-open -->
<!-- disposition: F-P7-02 anchor=ambiguous regression=none decision=needs-placement -->
<!-- disposition-confirmed: operator 2026-07-01T14-30 -->
```

- **Row grammar:** `<!-- disposition: <finding_id> anchor=<held|moved|vanished|ambiguous|not-re-anchorable> regression=<persisted|resolved-and-held|recurrence-candidate|new|new-in-quiet-chapter|none> decision=<confirm-resolved|keep-open|needs-placement|declined|pending> -->`. `regression=none` when the finding had no crossref join (carry-only rounds have no ledger yet — the record can still capture anchor-class dispositions for `needs-placement` triage). The human table is presentation; the markers are the machine record (the finding-trace precedent).
- **The `compares:` header is derived, never hand-typed:** the `disposition` subcommand computes both runlabels from its folder arguments via `_runlabel_of()` (`reanchor.py:286`) — the same derivation `emit` already uses — so the header always names the actual inputs RT1 recomputes against.
- **The confirmation token** `<!-- disposition-confirmed: operator <ISO-8601, minutes, hyphenated> -->` is **hard-sequenced**: it is written ONLY after every row has been presented to the operator and confirmed — never alongside, never before, never on a partially reviewed table (the orchestrator instruction lives in state-lifecycle.md step 4, worded as this sequencing rule, not as a soft "after review"). It is the recorded precondition RT2 checks.
- `decision=declined` is a **per-round record only** (there is no engine-level declined finding state — revision-coach/SKILL.md:91 stalled off-ramp); a durable declined channel is a named future increment, not M1.

## Mechanical gates

**Existing gates — unchanged:** RA1–RA3 + W1/W2 (`reanchor`), R1 + W1–W3 (`regression-diff`), X1 (`crossref`), A-gates on the emitted copy, the `revision_round` gate rev-a1–a3, and the `--check-all` `round-trip glue chain` must all still pass.

**New validator: `validate.sh roundtrip-disposition <prior_run_folder> <new_snapshot> <this_run_folder>`** → `reanchor.py disposition` (the partition + crossref logic already live there). Exit 0 with "no disposition record — nothing to check" when the artifact is absent (the `check_state` early-return precedent), so it is safe anywhere. Gate IDs (prefix `RT` — grep-verified unused in scripts/ + docs/):

| ID | Severity | Rule |
|---|---|---|
| **RT1 — recompute alignment** | ERROR | Every disposition row's `finding_id` exists in the prior manifest's RA3 partition (recomputed live, never trusted from the record), and its recorded `anchor=` class equals the recomputed class; `regression=` (when not `none`) equals the recomputed crossref class. No stale or fabricated evidence classes. The `compares:` header names the actual prior/this runlabels. |
| **RT2 — confirmation record present** | ERROR | Any row with a decision other than `pending` requires the file-level `<!-- disposition-confirmed: … -->` token. **This is the disposition-write gate the stub demands:** no confirmed disposition exists on the record without the recorded token. Validator output wording (per the Honesty note): "record of confirmation present and consistent" — the validator must **never** print "operator confirmed". |
| **RT3 — confirmed-writes-only** | ERROR | When a disposition record exists in the run folder, every `<!-- resolved: F-… -->` marker in that folder's Revision Report(s) corresponds to a `decision=confirm-resolved` row. The aggregation mechanism is `finding_trace.resolved_cited_ids()` (`finding_trace.py:130`) accumulated over completion artifacts (the `resolved_ids |= resolved_cited_ids(ct)` loop, `finding_trace.py:202-203`). **Integration contract: import/reuse `resolved_cited_ids` (or the module's `_RESOLVED_RE` marker regex) — do not reimplement the marker parse.** A resolved marker whose finding the record left `pending`/`keep-open` — i.e. an auto-close — is the ERROR this whole spec exists to prevent. |
| **RT4 — partition coverage** | WARN (ERROR `--strict`) | Every finding id in the recomputed RA3 partition has a disposition row, missing ids reported by id. A record that **exists** is a round-close record (carry-only exit (a) writes no record at all), so a row omitted from it is a finding silently dropped from round-close review — without this check a partial record validates clean even under `--strict` (Codex review P2). WARN by default (a record may be drafted incrementally within a session, the W1 staging posture); `--strict` gates it at round close. |
| **W1 — unadjudicated / staged** | WARN (ERROR `--strict`) | Rows still `pending`, or `confirm-resolved` rows not yet reflected as resolved markers (work stages across sessions — the finding-trace advisory lesson). `--strict` gates them at round close. |

**Honesty note (bash-validator ceiling):** RT2 cannot prove a human confirmed — it proves the *record* of confirmation exists and is consistent. The human-in-the-loop enforcement layers: the orchestrator instruction (token only after per-row review), rev-a4 (the operator personally attests it at `gate --attest`, the existing attestation surface for exactly this kind of claim), and RT3 (the write-path consistency check). This matches the repo's attestation posture — `gate --attest` is already the operator-confirmation mechanism of record.

## Firewall & governed writes

- **Diagnose, never author:** the flow is pure projection + presentation. Comments are carried **byte-identical** (RA2); `ambiguous`/`not-re-anchorable` notes surface as "these N notes need your placement" — never silently placed, never re-worded to fit revised prose.
- **Runner-governed state writes:** lifecycle advancement goes through the existing two writers only (`revision_round` gate fold for governed projects; scoped direct write for non-governed — `state-lifecycle.md:120-125`). This spec adds **no third writer**; it adds a confirmation precondition upstream of both.
- `revised` stays terminal-per-id; a regressed finding gets a fresh id via re-`run_synthesis` (`docs/revision-round-gate.md` Blocker 2) — the disposition record never demotes.

## Degrade paths

- **No `python3`:** the offer is **not shown** (eligibility includes `command -v python3`); the `revising`/`diagnosed` nodes behave exactly as today, and the manual Revision Round Protocol remains the documented path (a documented degrade, not a shim). `validate.sh roundtrip-disposition` degrades to advisory WARN without python3, matching `reanchor` — coherent, since no disposition record can have been produced on such a host.
- **Non-governed project:** identical flow through step 6; the write is the scoped direct `finding_states[<id>] = "revised"` instead of the gate fold. RT1–RT3 apply identically (they read files, not gate logs). rev-a4 simply never comes up (no gate).
- **No prior annotated run:** ineligible; the node behaves as today (Loop Dispatch at `revising`, `/coach` + the :55 sibling offer at `diagnosed`).

## Fixture / self-test plan

- **`reanchor.py disposition --self-test` cases** (join `--self-test-all` via the existing dispatcher): absent-record no-op PASS; aligned record PASS; RT1 wrong-class + unknown-id FAIL; RT2 decided-rows-no-token FAIL; RT3 resolved-marker-without-confirm-resolved FAIL; RT4 omitted-row WARN naming the missing id, ERROR under `--strict`; W1 pending rows WARN, ERROR under `--strict`.
- **Canonical fixture:** `example-roundtrip-disposition.md` + a companion minimal Revision Report, committed under `plugins/apodictic/skills/core-editor/references/` beside the fixtures the glue chain already uses. Its rows must be **recompute-consistent** with `example-annotated-manuscript` × `example-reanchor-revised.md` (anchor classes) and `example-run-folder-r2` (crossref classes) — build it by running the chain once and confirming by hand.
- **`--check-all` step (extends the round-trip glue chain temp-copy block, validate.sh:597-647):** copy the fixture pair into the temp folder, run `roundtrip-disposition`, assert PASS; then the **hostile arms** (AGENTS.md review practice): a token-stripped copy must FAIL RT2, a copy with an extra unconfirmed `<!-- resolved: … -->` marker must FAIL RT3, and a copy with one finding's disposition row dropped must WARN RT4 by default (exit 0, missing id named) and FAIL under `--strict`. Assert exit codes + grep the RT ids in stdout (the reanchor-fixture pattern at validate.sh:584-591).
- Full gate: `bash scripts/validate.sh --check-all` green, both mirrors byte-identical (`check-mirror`).

## Failure modes & guards

| Failure | Guard |
|---|---|
| Silent auto-resolution — vanished anchor ⇒ finding closed, inverting the regression validator's purpose | Proposals-only flow; RT2 token; RT3 confirmed-writes-only; rev-a4 attestation |
| Wrong prior round diffed (stale or wrong manifest) | Newest-manifest resolution (`_resolve_inputs`), list-and-pick on multiple candidates, `compares:` header validated by RT1 |
| Reanchored manifest mistaken for a fresh diagnosis in a later round | Already solved by the `Reanchored_` infix / glob exclusion (Increment 2) — unchanged, and the reason the eligibility glob is safe |
| `crossref`/dispositions attempted before a re-diagnosis exists | The two-exit flow: step 6 requires the step-4 ledger; carry-only rounds record at most `needs-placement` rows with `regression=none` |
| Round-trip run on a rewrite that needs fresh analysis | Step 1 reset check (the §When to Reset triggers) runs **before** the chain |
| `emit` clobbering prior-round artifacts | Always `-o <new_run_folder>` (anchor correction #1); emit's own realpath escape guard stays |
| Model self-confirms the token | Layered: orchestrator instruction + rev-a4 human attestation + RT3 consistency (see §Honesty note) |
| Partial record — inconvenient findings omitted from the table validate clean | RT4 partition coverage: every recomputed RA3 partition id must have a row, missing ids named; WARN default, ERROR `--strict` at round close (Codex review P2 fold) |

## Non-goals

- **No auto-close.** A `vanished` anchor is a proposal; the problem may survive the text that anchored it.
- **No comment re-authoring** (Firewall). RA2 byte-identity stands; refused re-anchors go to the operator.
- **Python-less degrade unchanged** — the manual protocol is the documented path, not a bash reimplementation.
- **No new `next_action` enum, no new command, no `apodictic.*.v1` schema.**
- **No durable cross-round finding identity** and no engine-level `declined` state — both stay named future increments (`docs/draft-regression-testing.md` §Future; revision-coach stalled off-ramp).
- **No auto-selected prior run** when several qualify; no offer at lifecycle nodes other than `revising` and `diagnosed` in M1 (see Resolved questions).

## Increment plan, sessions, PR shape

- **Increment 1 — surfacing + record convention (markdown):** start.md `revising` row + note block; state-lifecycle.md step 4; revision-coach pointer; docs/ROADMAP/changelog updates.
- **Increment 2 — the gate:** `reanchor.py disposition` + self-tests; `validate.sh roundtrip-disposition` arm + `--check-all` step (+ hostile arm); `rev-a4`; the committed fixture pair; both mirrors.

**Single PR — atomicity is non-negotiable.** Increment 2 lands WITH Increment 1's surfacing in the same PR, never after it. Concretely, the PR is incomplete without ALL of: the `reanchor.py` `disposition` subcommand + RT1–RT3/W1 + self-test cases; the `validate.sh` `roundtrip-disposition` arm + the `--check-all` step **including the hostile arm**; `rev-a4` in `execution-gates.v1.json`; the committed fixture pair; and byte-identical mirrors (`check-mirror`). **Never ship the `/start` offer without the gate** — that would make step 6 an unguarded write path. ~1 session to build both, ~0.5–1 session for fixture hardening + review fold. Codex gate applies (authored logic).

## Refuted review claims (do not act on)

Two review-pass claims were checked against the tree and are **wrong** — the builder should not act on them:

- **(a) "disposition is pre-built in reanchor.py" — FALSE.** `reanchor.py` has `reanchor`/`emit`/`crossref` only (grep `disposition` in `plugins/apodictic/scripts/reanchor.py`: no subcommand). Build the `disposition` subcommand fresh, per the touch-points table.
- **(b) "the eligibility glob self-matches carried-over manifests" — FALSE; the glob is TRUE as written (§M1 eligibility predicate).** `emit` writes `[Project]_Reanchored_Manifest_[runlabel].md` / `[Project]_Reanchored_Annotated_Manuscript_[runlabel].md` (`reanchor.py:368-369`), which `*_Annotation_Manifest_*.md` (`annotation_manifest._MANIFEST_GLOB`, `annotation_manifest.py:104`) cannot match. No self-match filter is needed — do not add one.

## Resolved questions

1. **Should the offer also appear at the `diagnosed` node? → YES — folded into M1** (see §What it is and the touch-points table). A writer who took the letter away and revised offline returns with `revision_progress.steps_complete == 0` — deriving `diagnosed`, not `revising` (`lifecycle_node.py:84-87`) — so a `revising`-only offer would miss exactly the "came back with a new draft" case the feature targets. The `diagnosed` node already hosts a conditional sibling offer (start.md:55), so the mechanism is proven; the cost (a busier node prompt) is accepted. It is a two-line start.md change. **Operator call (default folded 2026-07-01, reviewers recommend; override before build if disagreed).**
