---
description: Copyedit a manuscript without flattening its voice (style sheet, voice ledger, queries only)
argument-hint: style-sheet | pass, optionally a manuscript or snapshot path
---

Voice-Aware Copyedit, Increment 1. Builds a style sheet and a voice ledger of the author's deliberate departures, then raises copyedit **queries** only: no replacement text, and nothing is ever applied to the manuscript. Fiction and nonfiction.

Load `../skills/core-editor/SKILL.md` and follow `../skills/core-editor/references/voice-aware-copyediting.md`.

**Firewall.** Ask, never correct. The never-flag list (sentence-initial conjunctions, split infinitives, sentence-final prepositions, singular *they*, fragments, contractions) is never raised. A form the author settled on the ledger is never raised again in its scope.

**Modes:**

- `style-sheet` (Phase 1): snapshot the manuscript, run `python scripts/copyedit.py harvest <snapshot>`, give the author one style-sheet review, and write `[Project]_Style_Sheet.md` with `apodictic.voice_ledger.v1` blocks.
- `pass` (Phase 2): read the style sheet and ledger, then write `[Project]_Copyedit_Queries_[runlabel].md` with one `apodictic.copyedit_item.v1` query per item. Run `style-sheet` first if no style sheet exists.

With no mode, run `style-sheet` when the project has no style sheet, otherwise `pass`.

**Gate before finalizing:** `python scripts/validate.py copyedit <run_folder>` (add `--strict` for CI). Resolve every ERROR: E1 schema, E2 byte provenance against the snapshot, E3 the voice-ledger guard. Review W1, a reason that invokes a never-flag rule. See `docs/voice-aware-copyediting.md`.

**State and output locations** (per `../skills/core-editor/references/output-structure.md` §Folder Architecture): read the manuscript from the project root and write the snapshot, style sheet and queries file there; archive into `runs/YYYY-MM-DD_{model}_{type}/` on completion. Never write to the plugin repo.

If arguments are provided: $ARGUMENTS
