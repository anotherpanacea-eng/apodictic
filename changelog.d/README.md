# changelog.d/ — changelog fragments

Instead of editing the big append-only changelog directly (which collides across
parallel branches and is triplicated into the generated `codex/` + `antigravity/`
trees), **each change drops one fragment file here.** The release pipeline
assembles them into a single dated section. (Design: GitHub #51.)

## How to add an entry

Create `changelog.d/<slug>.md` with **one freeform thematic `### ` section**:

```markdown
### Validators

23 → 35 self-testable validators. Added `retcon-plan`, `legal-risk`, …
```

Rules (the assembler enforces them, and CI runs `assemble-changelog.mjs --check`):

- The **first non-blank line** is a single `### ` header — no prose before it.
- **One `### ` section per fragment** (multiple thematic sections = multiple files).
- The header must have a **non-empty body**.
- Match the house style: freeform thematic headers (`### Validators`,
  `### Workflows — Retcon Planning`), **not** `### Added/Changed/Fixed`.
- Name the file for what changed (`retcon-planning.md`, `legal-risk-register.md`);
  an optional numeric prefix (`10-foo.md`) gives explicit ordering — fragments are
  concatenated in filename order.

## What happens at release

`scripts/release.sh` runs `node scripts/assemble-changelog.mjs <version>` after the
version bump and before the host builds. It prepends a new
`## vX.Y.Z - YYYY-MM-DD` section (these fragments concatenated) to the canonical
`plugins/apodictic/skills/core-editor/references/changelog.md`, **deletes the
consumed fragments**, and the host builds regenerate the `codex/` + `antigravity/`
copies. Adoption is forward-only: this directory holds only the *unreleased*
fragments.

Do **not** put this directory under `plugins/` — repo-root placement is what keeps
it out of the generated host trees (the builds copy only `plugins/apodictic/`).
