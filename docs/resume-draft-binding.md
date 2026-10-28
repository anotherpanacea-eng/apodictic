# Bind a resumed run to its draft — spec (apodictic)

**Status:** **Proposed (unbuilt).** Waiting for the owner to admit it. Do not build until the owner admits it. When built, the build PR flips this line (`AGENTS.md` § Review practices).
**Estimate:** one small prose-only PR to `commands/start.md`. No script, schema or sidecar field.
**Provenance:** deferred finding 10 of the external Codex framework review of 2026-10-16 (private document; summarized here, not quoted). Burndown card OCA-9. Line references are to `main` after the 2026-10-26 train (#398).

---

## The deferred finding

When `/start` resumes a bound project, it checks the stored contract hash against the **newest** contract file and calls a mismatch "manuscript/contract changed out-of-band." A contract hash cannot see an edit to the manuscript alone. Picking the newest contract is also ambiguous when the project has several runs. The review asks resume to bind the project, the selected run, its contract and the draft. When the draft has changed, the writer should choose between continuing the old snapshot and analyzing the revised draft, with anchors revalidated. The review found this by reading the docs. It did not reproduce a stale-draft failure.

## What `main` does today

- `plugins/apodictic/commands/start.md:37` — the contract-hash precondition: "locate the contract via the newest `runs/*/[Project]_Contract_*.md`", run `contract-check`, and on mismatch say "(manuscript/contract changed out-of-band)".
- `contract-check` hashes only the contract file (`plugins/apodictic/scripts/validate.py:606-611`). `contract_hash` is set from the contract at intake (`skills/core-editor/references/run-core.md:118`; sidecar field `output-structure.md:321`).
- The sidecar already names its run: `last_session.runlabel` (`output-structure.md:311`). Contracts are named `[Project]_Contract_[runlabel].md` (`output-structure.md:143`).
- Core-de and full-de runs already write a frozen, LF-normalized copy of the draft, `[Project]_Manuscript_Snapshot_[runlabel].md`, at intake (`run-core.md:20`; `output-structure.md:144`). `run-core.md:20` also says a mid-run manuscript revision needs a new runlabel and a fresh snapshot. Partial-de and fragment-de runs skip the snapshot.
- `/start` passes a "resolved run folder" to `lifecycle-node` (`start.md:54`, `:56`), but never says how that folder is chosen.
- For the `revising` and `diagnosed` nodes, the round-trip resume offer (`start.md:58`) already re-anchors a prior run's findings onto a revised draft (`reanchor`, `state-lifecycle.md:169-206`).
- The newest-contract glob came from the project-addressability design (`docs/project-addressability.md:110`, `:121`).

## Smallest change

All of it lands in `commands/start.md` Step 0.5, item 1 (`:37`): about 10 lines replacing one paragraph.

0. **Pre-contract projects are unchanged.** When the sidecar has no `contract_hash` (a `pre_writing` minimal sidecar, `skills/pre-writing-pathway/SKILL.md:476`, or a fresh `diagnosing` sidecar), skip items 1–3 and dispatch with no run folder, exactly as `start.md:37` does today.
1. **Select the run by name, not by date.** Resolve the run folder from the sidecar's `last_session.runlabel`: the folder holding `[Project]_Contract_[runlabel].md`. Use that one folder for the contract check, for `lifecycle-node … [run_folder]`, and for the `diagnosed`/round-trip offers. If the runlabel is missing or matches zero or several folders, list the candidate runs and ask which one. Never pick the newest silently.
2. **Say what the hash checks.** On a mismatch, say "the contract changed since intake", not "manuscript/contract".
3. **Compare the draft with the run's snapshot, when both exist.** If the selected run folder holds `[Project]_Manuscript_Snapshot_[runlabel].md` and the writer has supplied a draft in this session, compare the draft (LF-normalized, single trailing newline, the `run-core.md:20` rule) byte-for-byte with the snapshot. Use a shell or Python compare where available. The snapshot is the fingerprint, so nothing new is stored.
   - **Same** → resume as today.
   - **Different** → a two-option prompt:
     - **Continue <runlabel> on its snapshot** — the remaining work reads the snapshot, not the new draft.
     - **Analyze the revised draft** — a new runlabel and a fresh snapshot (the existing `run-core.md:20` rule). On `revising`/`diagnosed` nodes this is the existing round-trip offer (`start.md:58`), which re-anchors the findings.
   - **No draft supplied** → resume on the snapshot and say so in one line.
   - **No snapshot** (partial or fragment run, a project that predates snapshots), or no way to compare (no shell or Python) → say in one line that the draft was not checked, and continue. Never state a comparison that did not run.
4. One `changelog.d/` fragment.

## Behavior it protects

- A writer who edited the manuscript between sessions does not get the rest of an old run silently analyzed against a different text, or findings whose quotes and anchors point at lines that moved.
- A project with several runs resumes the run the sidecar recorded, not whichever contract is newest on disk.

## Deletion test

- **Nothing added.** No draft hash in the sidecar (the snapshot file already is the fingerprint), no new validator, no new `next_action` key, no fail-closed refusal (a missing snapshot is disclosed, and the run continues).
- **Kept:** the existing contract-hash check. It catches the contract edit it was built for. This spec only corrects its wording and fixes which file it reads.

## Acceptance check

A manual walk-through, recorded in the build PR, on a scratch project:

1. Two run folders, where the newer one is not `last_session.runlabel` → resume checks the recorded run's contract.
2. The manuscript is edited and the contract is not → the draft-changed prompt appears, and the contract check passes.
3. An unchanged draft → no prompt.
4. A partial-de run with no snapshot → the one-line "not checked" note.
5. A pre-writing project with only the minimal sidecar → `pre_writing` dispatch with no run question.

No automated test: the change is routing prose, and no validator owns it (`AGENTS.md` § Test value convention).

## Owner questions

1. **Runlabel doesn't resolve to exactly one run:** ask the writer (this spec), or fall back to the newest with a one-line notice?
2. **Runs without a snapshot** (partial-de, fragment-de): accept the "not checked" note (this spec), or start writing snapshots for those runs too (one more file per run)?
3. **"Continue on the snapshot" for `revising`/`diagnosed` nodes:** offer it, or route a changed draft straight to the round-trip offer, since those nodes have no remaining passes to run?
