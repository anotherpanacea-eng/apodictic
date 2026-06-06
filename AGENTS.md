# Agent workflow — apodictic

APODICTIC is solo-maintained (`anotherpanacea-eng`) but multi-agent: Claude,
Codex, and Antigravity sessions all contribute. This document records the
internal workflow they follow. External contributions are email-based — see
`CONTRIBUTING.md`; this file governs the maintainer's own agent sessions, not
outside PRs.

## The flow

```
spec  →  review  →  write  →  review  →  fix  →  merge
            ▲                    ▲
         reviewer             reviewer
```

1. **Spec.** What the change should do. Strategic/scheduled work lives in
   `ROADMAP.md`; non-trivial ad-hoc work gets a GitHub Issue (see below);
   trivial work can be a chat brief.
2. **Spec review.** A second agent surfaces gaps, dependency issues, or scope
   creep before writing starts.
3. **Write.** One agent implements against the canonical source in `plugins/`
   (the Claude plugin). Never hand-edit `codex/` or `antigravity/` — those are
   generated (see "Platform parity").
4. **Code review.** The other agent reads the diff and flags issues.
5. **Fix.** The writing agent applies fixes and regenerates parity.
6. **Merge.** Via PR + merge commit (see "PRs and merges").

## Where work comes from: roadmap, briefs, and Issues

Every change implements from a written contract, never from an unscoped
instruction like "improve the argument audit." Agents are prone to
plausible-adjacent work, and this plugin's audit surface is wide enough to make
that easy. The contract comes from, in order of formality:

1. **A `ROADMAP.md` item** — strategic/scheduled work; the entry is the brief.
2. **A GitHub Issue** (`Task brief` template: Goal / Acceptance criteria /
   Out of scope / Constraints) — the home for non-trivial ad-hoc work that
   isn't on the roadmap. The acceptance criteria are what the second reviewer
   checks the diff against; the PR closes the Issue (`Closes #N`).
3. **A chat brief** — for trivial changes that also qualify for direct push.

Roadmap and Issues do different jobs and should not duplicate each other: the
roadmap is strategic and narrative; an Issue is one bounded work order with a
definition of done. Diagnostic-flag constraints — name the flag, include a
false-positive warning, keep the diagnostic/rewrite firewall (`CONTRIBUTING.md`
→ Style) — belong in an Issue's acceptance criteria where the reviewer enforces
them, not only in a comment the review might skim past.

## Platform parity

`plugins/` is canonical (the Claude plugin). `codex/` and `antigravity/` are
**generated** by `node scripts/build-codex.mjs` — do not edit them by hand.
After any change to `plugins/`, regenerate parity and commit the result in the
same PR so all three platforms stay in sync. CI does not yet verify parity;
until it does, regeneration is a reviewer checklist item (see the PR template).

## PRs and merges

- **Default to PR-per-change with a merge commit** (`gh pr merge <N> --merge`),
  not squash — this preserves the spec-review-fix structure on `main`.
- **Delete the branch on merge** (`--delete-branch`).
- **Bump the version at merge, not in the PR** — open PRs merge in unknown
  order. Version + `changelog.md` follow the patch/minor/major rules in
  `CONTRIBUTING.md`.

### Branch naming

- `feat/<surface>` for new audits/modules
- `fix/<short-description>` for fixes
- `chore/<short-description>` or `docs/<short-description>` for ancillary work
- `codex/<short-description>` for Codex-authored proposals

### When to skip the PR

Direct push to `main` is fine for typo fixes, `changelog.md` touch-ups, and
single-line non-behavioral corrections. Anything that changes diagnostic
behavior, output format, thresholds, flag definitions, or pass logic lands via
PR.

## CI

`.github/workflows/ci.yml` byte-compiles `plugins/` + `scripts/` (syntax gate)
and validates that the plugin / marketplace / release-registry manifests parse.
There is no pytest suite — the plugin is prompt/skill-based; the `evals/`
fixtures are the behavioral ground-truth track. Adding a smoke test is a roadmap
follow-up.

## Co-authorship

Commits authored end-to-end by one agent carry that agent's trailer; pair-
authored commits carry both. Example:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

## When this document is wrong

Update it. It's a working document, not a contract. The goal is for any future
agent session to read this file and know what shape the work should take.
