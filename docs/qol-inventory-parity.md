# QoL — inventory-parity check (spec)

**Status:** spec → build (Opus) → review (Fable). Standalone meta-check; **no diagnostic behavior, schema, or validator change; no validator-count bump** (a `.mjs` like `assemble-changelog`/`check-status-drift`). Branches from PR B (`claude/marketing-visual`) because it needs the *refreshed* dashboards/matrix to be green; merges after #81.

## Problem
The display surfaces (`overview-dashboard.html`, `AUDIT_SELECTION_MATRIX.md`) hand-list the audit/research inventory and drift behind the canonical registry — the exact rot PR B (#81) just hand-fixed. We want a mechanical guard so it can't silently recur.

## The honest design decision (read before building)
**Name-by-name coverage matching is NOT the design.** The canonical signal-emitting registry has **42** entries (`audit-routing-table.md` between `<!-- registry:signal-emitting-audits:begin -->`/`:end -->`); the dashboard has 40 audit chips under a different taxonomy, with parenthetical names ("Banister (Epistemic Humility)", "Timeline (Pass 10)"). Matching those across surfaces by normalized name needs a large, brittle allowlist — a false-positive magnet and the regex-fragility the Validator Hardening track forbids. So we do the **#79 status-drift pattern applied to inventory**: a *sync-marker* + a changed-since signal. It catches the **drift event** (registry changed, a surface wasn't re-synced), robustly and with near-zero false positives. **Honest limitation (state it in the AGENTS.md bullet + changelog):** like #79's status flip, it verifies the *signal is consistent*, not that the surface content is actually correct — a maintainer who bumps the marker without re-syncing defeats it. That's an acceptable, transparent trade vs. brittle name-matching, and it's strictly better than today's nothing.

## Mechanism
`scripts/check-inventory-parity.mjs` (stdlib Node only; `--check` default, `--self-test`):

1. **Compute the canonical signature** from the single sources of truth:
   - **audits:** the bullet names between the registry begin/end markers in `plugins/apodictic/skills/core-editor/references/audit-routing-table.md` (the `- Name` lines), trimmed, **sorted**. Signature = `<count>:<short-hash>` where short-hash = first 8 hex of `crypto.createHash("sha256")` over the sorted-names joined by `\n`. (Count is human-glanceable; the hash catches a rename/swap that keeps the count.)
   - **research:** the mode names in `plugins/apodictic/commands/research.md` (the `- **<mode>**` / `- <mode> —` bullets), sorted, same `<count>:<short-hash>`.
2. **Scan opted-in surfaces** for a marker:
   `<!-- inventory-synced: audits=<count>:<hash> research=<count>:<hash> -->`
   A surface without the marker is **skipped** (opt-in). Initial opted-in surfaces: `plugins/apodictic/overview-dashboard.html` and `plugins/apodictic/AUDIT_SELECTION_MATRIX.md`.
3. **Flag** any surface whose recorded `audits=`/`research=` signature ≠ the current canonical signature, with a clear message naming the surface and *both* expected-vs-found signatures, and the remedy: "the canonical audit registry / research modes changed since this surface was last synced — re-verify the surface's inventory and update its `inventory-synced` marker to `<current>`." Exit 1 on any stale surface (it's a hard gate, like assemble-changelog).
4. **Vacuity guard:** if zero surfaces carry the marker, ERROR (the check would be vacuous) — same discipline as `check-status-drift`.
5. **Marker robustness:** ignore a marker inside a fenced code block (```` ``` ````/`~~~`), so docs that *document* the syntax don't self-trip (reuse the `check-status-drift` fence approach). A malformed `inventory-synced` marker (present but unparseable) is a loud ERROR, not a silent skip.

## Seeding (so it's green + non-vacuous on day one)
Add the `<!-- inventory-synced: audits=<current> research=<current> -->` marker to the two surfaces, computed against the refreshed surfaces **on this branch** (PR B's content). The build must compute the real current signatures and embed them, then confirm `check-inventory-parity` is **clean** (the seeds match). Place the marker as an HTML comment near the top of each surface's audit section (`overview-dashboard.html`) and near the top / under the title of `AUDIT_SELECTION_MATRIX.md`.

## Self-test (hermetic, proves non-vacuity)
`--self-test` with temp fixtures: (a) surface marker matching the canonical sig → clean; (b) stale audits sig → flagged (exit 1) naming the surface; (c) stale research sig → flagged; (d) no marker on any surface → vacuity ERROR; (e) marker inside a ``` fence → ignored; (f) malformed marker → ERROR; (g) a surface with a current marker + another without → only the absent-marker one is skipped, clean overall. The build must show the negative cases FAIL if the comparison were stubbed always-pass.

## CI + docs
- Add a CI step in `.github/workflows/ci.yml` running `node scripts/check-inventory-parity.mjs` (and `--self-test`), placed near the other meta-checks (e.g. after the status-drift/changelog steps). **Note:** this branch is off a slightly stale `main`; at merge, reconcile the ci.yml step list with whatever steps `main` has (#79's status-drift step etc.) — don't clobber them.
- `AGENTS.md` § Review practices: one bullet — "when you change the signal-emitting audit registry or the research modes, re-sync the dashboards/matrix inventory and bump their `inventory-synced` marker (the inventory-parity check enforces the *signal*, not the content)."
- `changelog.d/qol-inventory-parity.md` — one `### ` fragment.

## Verification gates (run ALL locally before push)
1. `node scripts/check-inventory-parity.mjs --self-test` → PASS (count the cases).
2. `node scripts/check-inventory-parity.mjs` → clean, exit 0 (both seeds match; prints the surfaces checked + the current signatures).
3. **Prove it bites:** temporarily append a fake `- Fake Audit XYZ` inside the registry markers (do NOT commit) → re-run the scan → both surfaces flagged stale; revert. Report what you saw.
4. `node scripts/assemble-changelog.mjs --check`; `node scripts/build-codex.mjs --self-check`; `node scripts/build-antigravity.mjs --self-check`; `node scripts/release-generate.mjs --check`; `bash scripts/validate.sh --check-all` — all green (this change touches none of their inputs except adding the HTML/MD markers, which must not break the HTML tag-balance or release-generate).
5. Confirm the seeded HTML marker doesn't disturb `overview-dashboard.html` tag-balance / `<script>` (it's an HTML comment) and that `release-generate --check` is unaffected.

## Non-goals
- **No name-by-name coverage** (explicitly rejected as brittle above).
- No new audits/commands; no version bump; no touching PR-A/PR-B content beyond adding the two markers.
- Not a replacement for review — it flags *re-sync needed*, it doesn't verify the surface is correct.
