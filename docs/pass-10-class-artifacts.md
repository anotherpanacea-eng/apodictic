# Pass-10-Class rolling structured artifacts

Authoring notes for framework maintainers, moved out of `core-editor/SKILL.md` (which keeps a short definition under §Project Integration). Nothing at run time reads this file.

A recognized class of project-level rolling artifacts the framework uses to track manuscript state across runs. Pass-10-class artifacts share these properties:

- **Project-level**, not run-folder-scoped (lives at the project root, persists across runs)
- **Structured**, machine-readable or near-machine-readable (schema specified per artifact)
- **Diffable** across runs (subsequent runs produce a diff section showing what changed)
- **Validator-paired** (each instance has a mechanical validator that surfaces drift, conflicts, or schema violations)
- **Synthesis-layer integrated** (the synthesis step consumes the artifact and may treat numeric drift as severity input)

This contrasts with run-folder-scoped pass artifacts (e.g., individual pass reports, audit findings files), which are run-specific and not designed for cross-run diff.

Recognized instances:
- `Diagnostic_State.md` — rolling diagnostic state at project root (already exists)
- `SYNTHESIS.md` — master revision plan at project root (already exists)
- `Argument_State.md` — argument-shaped nonfiction state at project root (already exists; see argument-state-schema)
- `Series_State.md` — cross-volume continuity at series root (already exists)
- `Timeline.md` — temporal architecture for fiction with Pass 10 (live; schema in `references/pass-10.md`; three mechanical validators in `scripts/validate.py`: `timeline-diff`, `timeline-arithmetic`, `timeline-anchor-conflict`)
- `Plot_Spine.md` — spine-driven fiction state (future; intersects Plot Architecture skill)

When adding a new project-level rolling artifact, instantiate it against this class: define its schema, pair it with a validator, specify the synthesis-layer integration. `Timeline.md` (Phase 6 Wave 1) is the first live instance added under the named pattern; `Plot_Spine.md` is the next planned instance.
