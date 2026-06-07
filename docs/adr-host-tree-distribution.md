# ADR: Stop committing the generated host trees; publish them as release assets

**Status:** Accepted (2026-06-07). Implements GitHub #52 (Option B) and #51.
**Context issues:** #52 (this decision), #51 (`changelog.d/` fragments).

## Decision

Stop committing the generated `codex/` and `antigravity/` workspaces. Build them
from the canonical `plugins/` source and **publish them as release assets** on each
`v*` tag, alongside `apodictic.plugin`. This is **Option B** from #52.

## Why

The committed host trees were the dominant parity-churn multiplier: every
release-touching change edited the canonical file **and** both generated copies
(×3), which collided during parallel branch waves. But the trees were never the
*consumer's* documented install path — the README already told Codex/Antigravity
users to **build** after cloning. So committing them was a contributor cost without
a matching consumer benefit.

Publishing prebuilt per-host bundles instead makes the three target hosts **more**
readily usable (download-and-open: no clone, no Node), while removing the churn.

- **Codex** → `apodictic-codex-marketplace.zip`
- **Antigravity** → `apodictic-antigravity.zip` (new; `build-antigravity.mjs` now
  emits it, mirroring `build-codex.mjs`)
- **Claude / Cowork** → `apodictic.plugin`
- **Custom GPT** → unchanged; served by manually uploaded instructions/knowledge,
  decoupled from the repo trees (a separate follow-up if it should track releases).

## Options considered (from #52)

- **A — keep committing.** Zero infra, but keeps the ×3 churn; no consumer upside.
- **B — un-commit; CI publishes release assets.** *Chosen.* Removes churn, improves
  install UX. Cost: CI publish step + doc updates + `release-verify` rework.
- **C — un-commit; users build locally.** Cheapest, but worst UX (everyone needs
  Node) — works against the "readily usable" goal.
- **D — orphan `*-dist` branches.** Preserves clone-and-go, no feature-PR churn, but
  adds branch-management machinery; artifacts are simpler for non-technical users.

## Consequences

- `codex/` + `antigravity/` are `.gitignore`d; feature PRs touch only `plugins/`
  (and `changelog.d/`). No parity tree to regenerate and commit.
- Verification shifts from "committed == regenerated" to **regenerate-and-self-check**:
  `build-*.mjs --self-check` (temp build + internal validation, incl. the archive),
  wired into `release-verify.mjs` and CI. This also closes the prior silent-drift
  gap (CI never ran parity before).
- `.github/workflows/release.yml` builds the bundles on tag and creates/updates the
  GitHub release, taking notes from the assembled changelog section when available.
- Distribution now lags `main` by a release (artifacts are cut at tag time), which
  is the intended stable-release model for non-technical users.

## Related: #51 (changelog fragments)

Independent but landed together. The append-only changelog moves to a repo-root
`changelog.d/` fragment directory; `scripts/assemble-changelog.mjs` cuts the
fragments into a dated section during `release.sh` (after the version bump, before
the host builds). Removes the single worst per-PR collision regardless of the #52
decision.
