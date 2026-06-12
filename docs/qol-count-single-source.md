# QoL refactor spec: derive the self-testable-validator count from `AGG_VALIDATORS`

**Status:** spec (not yet implemented)
**Scope:** `scripts/validate.sh`, `plugins/apodictic/scripts/validate.sh`, `.github/workflows/ci.yml`

## Problem

The count of self-testable validators (currently **40**) is hard-coded as a literal in five
places. Every PR that adds a validator must hand-edit all five, which has repeatedly caused
merge conflicts: two validator PRs each bump 37→38 independently, the second to merge
conflicts on these exact strings, and `--self-test-all` reports a stale denominator.

The single source of truth is the `AGG_VALIDATORS` space-separated list (currently 40
entries, verified by `set -- $AGG_VALIDATORS; echo $#`). The count should be **derived**
from that list, never duplicated.

The five sites (verified against the current tree; line numbers refer to
`scripts/validate.sh`, and apply identically to the mirror copy
`plugins/apodictic/scripts/validate.sh`):

| Site | What it is today |
|---|---|
| `scripts/validate.sh:169` | usage/help echo: `...runs --self-test on all 40 self-testable validators...` — inside `usage()`, which is **defined at :166 and first called at :174**, before `AGG_VALIDATORS` is defined at :186 |
| `scripts/validate.sh:186` | `AGG_VALIDATORS="contract-hash contract-check ... manuscript-viz check-mirror"` — the source of truth, currently defined **inside** the `--self-test-all` branch |
| `scripts/validate.sh:190` | dispatcher echo: `running --self-test on all 40 validators:` |
| `scripts/validate.sh:203` | `Aggregate self-test: PASS ($AGG_PASS_COUNT/40 validators)` |
| `scripts/validate.sh:206` | `Aggregate self-test: FAIL ($AGG_FAIL_COUNT/40 validators failed; rerun individually with --self-test for details)` |
| `.github/workflows/ci.yml:51` | a YAML **comment**: `# --check-all subsumes --self-test-all (the 40 validator self-tests) and` |

A repo-wide grep for `40 (self-testable )?validator` confirms these are the only sites
(plus the byte-identical mirror copies of the first five).

## The single source + derivation approach

### Hoist location

There is **no existing top-of-file constants region**: the script is ~160 lines of comment
header, then `set -euo pipefail` (line 164), then `usage()` (lines 166–172), then the
`$# -lt 1` guard (line 174), then the `--self-test-all` branch (lines 176–209).

**Hoist `AGG_VALIDATORS` and a derived `AGG_COUNT` to immediately after
`set -euo pipefail` (between current lines 164 and 166), before the `usage()` function
definition.** This becomes the script's de-facto constants region:

```bash
set -euo pipefail

# Single source of truth for the self-testable validator set. The displayed
# count everywhere below is DERIVED from this list — never hard-code it.
AGG_VALIDATORS="contract-hash contract-check ledger-check artifact-names synthesis-sections tone-check state-lines severity-floor audit-signal-propagation underdiagnosis-triggers ledger-consolidation decision-layer-check quality-risk-triggers timeline-diff timeline-arithmetic timeline-anchor-conflict audit-tier-criterion argument-recon-prerequisite structured-findings softness-check deficit-lock artifacts-schema gate gate-state finding-trace escalation-check feedback-triage editor-scaffolding diagnostic-vocabulary retcon-plan state-card-diff legal-risk argument-spine scene-ethics argument-groundtruth-check registry-check lifecycle-node reader-instrument manuscript-viz check-mirror"
# shellcheck disable=SC2086  # intentional word-splitting to count entries
AGG_COUNT=$(set -- $AGG_VALIDATORS; echo $#)
```

The list content must be copied **verbatim** from current line 186 (40 entries,
`contract-hash` through `check-mirror`) — do not reorder, add, or drop entries.

Ordering note (why this works): shell functions resolve variables at **call** time, not
definition time, so strictly the constant only needs to exist before `usage()` is first
*called* (line 174 for missing args; line ~4711 in the `*)` unknown-command fallback).
Placing it before the `usage()` *definition* is nonetheless the right call — it reads as a
constants block, and nobody has to remember the call-time subtlety. Under `set -u`, an
unset `$AGG_COUNT` inside `usage()` would abort the script, so the hoist must land before
line 174 in any case; this placement satisfies that with margin.

### Derivation mechanism

Use `AGG_COUNT=$(set -- $AGG_VALIDATORS; echo $#)` rather than `wc -w`:

- `wc -w` pads its output with leading spaces on macOS/BSD, which would corrupt the
  displayed string (`( 40 validators)`); the plugin copy runs on user machines, not just
  Linux CI.
- The `set --` positional-parameter count is pure shell, exact, and unpadded.
- `$AGG_VALIDATORS` must stay **unquoted** inside the `set --` (intentional word
  splitting — same idiom the existing `for v in $AGG_VALIDATORS` loop already relies on).
  Keep the `shellcheck disable=SC2086` comment so a future lint pass doesn't "fix" it.

## Each of the 5 sites and what it becomes

1. **`:169` (usage echo)** — replace the literal:
   `...runs --self-test on all $AGG_COUNT self-testable validators; exit 0 only if every validator's self-test passes...`
2. **`:186` (`AGG_VALIDATORS=` inside the `--self-test-all` branch)** — **delete this
   line**; the branch now references the hoisted top-level `AGG_VALIDATORS`. Do not leave
   a second copy of the list anywhere. (The branch's existing comment block at lines
   176–184 contains no count and needs no change.)
3. **`:190` (dispatcher echo)** —
   `echo "Aggregate self-test dispatcher (v1.8.4) — running --self-test on all $AGG_COUNT validators:"`
4. **`:203` (PASS line)** —
   `echo "Aggregate self-test: PASS ($AGG_PASS_COUNT/$AGG_COUNT validators)"`
5. **`:206` (FAIL line)** —
   `echo "Aggregate self-test: FAIL ($AGG_FAIL_COUNT/$AGG_COUNT validators failed; rerun individually with --self-test for details)"`
6. **`.github/workflows/ci.yml:51`** — a comment cannot reference a shell variable, so
   **de-number it** so it can never go stale:
   `# --check-all subsumes --self-test-all (the validator self-tests) and`

### Denominator decision (sites 4–5)

Use **`$AGG_COUNT` (the list length)**, not the runtime sum
`$AGG_PASS_COUNT + $AGG_FAIL_COUNT`. They are equal today, but the list length is the
*advertised* total: if a future loop bug ever skipped entries, `PASS (38/40)` would be
visibly wrong, whereas a runtime-sum denominator (`38/38`) would silently mask the skip.
The denominator is a cross-check, not just a label. Decision made — the builder should not
revisit this.

## Constraints / gotchas

- **Mirror both copies.** `validate.sh` exists as two committed, byte-identical copies:
  `scripts/validate.sh` (what CI runs) and `plugins/apodictic/scripts/validate.sh`
  (canonical). Apply the identical edit to **both** — in practice, edit one and `cp` it
  over the other — and confirm with `cmp` and the `check-mirror` validator. A
  `DIFFER: validate.sh` from `check-mirror` after editing only one copy means the copies
  aren't synced, not a logic bug.
- **`set -u` ordering.** The hoist must precede the first `usage()` call (line 174);
  the placement above (immediately after `set -euo pipefail`) guarantees it.
- **Keep the list one line.** Keep `AGG_VALIDATORS` as a single long line, as today.
  Future validator-add PRs will still touch this one line (that's a real semantic merge,
  unavoidable), but the four count sites no longer conflict — that is the win.
- **Quoting discipline.** `$AGG_VALIDATORS` stays unquoted in both the `set --` count and
  the existing `for v in $AGG_VALIDATORS` loop. Quoting either breaks word splitting.
- **No behavior change.** `--self-test-all` and `--check-all` keep identical pass/fail
  semantics and exit codes; only the mechanism producing the displayed count changes. The
  number shown must still be exactly `40` today.

## Verification gates (run after building, in order)

1. `bash scripts/validate.sh` (no args) and `bash scripts/validate.sh bogus-command` —
   both must print the usage text with `all 40 self-testable validators` (derived, exit 2).
2. `bash scripts/validate.sh --self-test-all` — header says `all 40 validators:`, final
   line says `PASS (40/40 validators)`, exit 0.
3. `cmp scripts/validate.sh plugins/apodictic/scripts/validate.sh` — no output (byte-identical).
4. `bash scripts/validate.sh check-mirror` — PASS.
5. `bash scripts/validate.sh --check-all` — full CI gate, exit 0.
6. `grep -rnE '\b40 (self-testable )?validators?' scripts/ plugins/apodictic/scripts/ .github/`
   — zero hits (no literal count survives).

## Non-goals

- **Do not change the validator set** — same 40 entries, same order, same names.
- **Do not touch the dual-script-mirror discipline** — the two copies remain
  hand-mirrored committed files enforced by `check-mirror`; no symlinking, generation,
  or sourcing tricks.
- **Do not refactor the command list at `:168`** (the `echo "Commands: ..."` line in
  `usage()`). It is a sibling hand-maintained duplication (and is not even the same set —
  it omits `gate-state`/`escalation-check`), but deriving it is out of scope here.
- **Do not renumber/reword the `(v1.8.4)` dispatcher tag** or any other version strings.

## Known uncertainties

- None blocking. The one subtlety (usage runs before the old definition site) is fully
  resolved by the hoist; function call-time variable resolution makes the placement safe.
- ShellCheck is not currently wired into CI (only `bash`/`compileall`/manifest gates), so
  the `disable=SC2086` comment is defensive, not required for the gates to pass.
