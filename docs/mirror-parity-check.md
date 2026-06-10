# Mirror-parity check — `validate.sh check-mirror` (spec)

**Status:** **Built** (`validate.sh check-mirror`, wired into `--check-all`). QoL infrastructure; no behavior change to any existing validator.

## The problem

Per `AGENTS.md` § Platform parity, `validate.sh` and every Python validator exist in **two committed copies** — `plugins/apodictic/scripts/` (canonical) and root `scripts/` (**what CI runs**) — that must be kept **byte-identical by hand**. Build/release scripts (`*.mjs`, `release.sh`, `bump-version.sh`) live only at root; `test_fixtures/` lives only in the plugin copy. Those are *not* mirrored.

The failure mode is silent and has bitten us (Project Addressability Increment 2): edit the plugin copy of a validator, pass `--check-all` locally against *that* copy, push — and CI runs the **stale root copy**, green but blind to the change. The only current defense is remembering to run `diff -q` by hand on every touched file. That is exactly the kind of invariant the harness should mechanize.

## The check

A new `check-mirror` validator in `validate.sh`, dispatched like any other:

- **`validate.sh check-mirror`** — locates the repo's two script dirs (from whichever copy is invoked) and asserts every **shared mirrored file** is byte-identical. Reports each drift as `DIFFER: <name>` / `MISSING in <dir>: <name>` and exits non-zero if any. PASS prints a one-line summary.
- **`validate.sh check-mirror <dirA> <dirB>`** — compare two arbitrary dirs (the seam the self-test drives).
- **`validate.sh check-mirror --self-test`** — hermetic temp-dir test: identical pair → PASS; a content drift → caught; a file present in one dir only (either direction) → caught; a root-only-allowlisted file present in one dir only → ignored (PASS).

### The mirrored set (what must match)

`validate.sh`, `preflight.sh`, and every `*.py`. Concretely: the files that exist in **both** dirs, restricted to `{validate.sh, preflight.sh, *.py}`. Explicitly **excluded**: `__pycache__/`, `test_fixtures/`, and the root-only build/release scripts (`*.mjs`, `release.sh`, `bump-version.sh`) — a naive `diff -rq` of the two trees would false-positive on those, so the check enumerates the mirrored set rather than diffing whole trees.

A `.py` (or `validate.sh`/`preflight.sh`) present in **one** dir but not the other is a drift (e.g. a new validator added to the canonical copy but not synced to root) — flagged as `MISSING`.

**Root-only `*.py` utilities — the `CM_ROOT_ONLY` allowlist.** Not every root `*.py` is a mirrored validator: some are repo-infrastructure utilities that live **only** in root `scripts/` (release-engineering, like the `*.mjs` scripts), e.g. `sync_setec.py` (the SETEC vendoring/sync tool). Listing them in `CM_ROOT_ONLY` excludes them from the mirrored set so a deliberately root-only utility is not reported as `MISSING in plugins/apodictic/scripts`. Without this, an unrelated PR that adds such a utility would turn main CI red on its next merge with no git conflict to warn anyone. Keep the list tight — it is an allowlist of *intentional* asymmetry, not a way to skip a validator that genuinely should be mirrored.

### Directory location

`check-mirror` resolves its own dir via `$(cd "$(dirname "$0")" && pwd)` (the established pattern) and probes for the *other* copy at both candidate locations — `$DIR/../plugins/apodictic/scripts` (invoked from root) and `$DIR/../../../scripts` (invoked from the plugin copy) — taking whichever exists and differs from `$DIR`. If the sibling copy can't be located, it WARNs and exits 0 (degraded, like the python3-absent validators), never a false failure.

## Wiring (the standard validator-addition surfaces)

1. The `check-mirror)` case block + its `--self-test`, in `validate.sh`.
2. **Real-file invariant in `--check-all`**: invoke `check-mirror` (real dirs) alongside the other real-file invariants. This is the gate that actually protects CI.
3. **`AGG_VALIDATORS`**: register `check-mirror` so its `--self-test` runs under `--self-test-all`; bump the hard-coded count `37 → 38` at its **exact** surfaces — `validate.sh:169` (`--self-test-all` help banner), `:190` (dispatcher echo), `:203` (PASS line), `:206` (FAIL line), and `.github/workflows/ci.yml:51` (the "37 validator self-tests" comment). **Line ~170 has no count** — it's the prose enumeration; don't look for a number there. Each `validate.sh` occurrence changes in **both** copies (so 4 count edits × 2 copies = 8 validate.sh line edits).
4. **Command list** (line ~168): add `check-mirror`. **Do not** touch the top-of-file `#  <cmd>` usage comment — that convention is abandoned; the recent validators (`registry-check`, `lifecycle-node`, `finding-trace`, …) have zero entries there, so adding one would make `check-mirror` *inconsistent*.
5. **`--check-all` description** (line ~170, prose): add a clause naming the new mirror invariant (no count).
6. **Mirror the edited `validate.sh` to both copies, byte-identical — as the LAST action before running `--check-all`.** The check that enforces mirroring is itself subject to it: between editing root `validate.sh` and syncing the plugin copy, the two `validate.sh` files differ, so the new real-dir `check-mirror` invariant will report `DIFFER: validate.sh` and `--check-all` will be red. That is **expected, not a logic bug** — sync both copies, then re-run. (This is the one bootstrapping gotcha; surface it so the implementer doesn't chase a phantom failure.)
7. **`AGENTS.md`** § Platform parity: replace the manual `diff -q` instruction with `validate.sh check-mirror` as the automated verification (keep the by-hand sync rule; the check only *detects* drift, it does not fix it).
8. Changelog fragment.

## Scope / non-goals

- **Detection only — never auto-syncs.** Mirroring stays a deliberate by-hand `cp`; the check just makes drift loud and CI-blocking. (Auto-sync would hide which copy is intended canonical and could paper over a bad edit.)
- No change to any existing validator's behavior, schema, or output.
- Does not police schemas/manifests (single-sourced, correctly un-mirrored).

## Self-test cases (must catch, proving the check isn't vacuous)

| Case | Setup | Expect |
|---|---|---|
| identical | two temp dirs, same `validate.sh` + `a.py` | PASS |
| content drift | `a.py` differs by one byte | caught (non-zero) |
| missing file | `b.py` only in dirA | caught (non-zero) |

A hostile reviewer should confirm the self-test would **fail if the comparison were stubbed to always-pass** — i.e. the negative cases are real.
