# Status-drift lint — `scripts/check-status-drift.mjs` (spec)

**Status:** **Built** (`scripts/check-status-drift.mjs`, wired into CI after the changelog gate). QoL infrastructure; no behavior change to any existing validator, no validator-count change, no schema change.
<!-- built-when: scripts/check-status-drift.mjs -->

> The HTML comment above is a **live** `built-when` marker (see §Marker syntax). When this lint is built, the builder must flip this doc's Status line to **Built** in the same PR — or the lint will flag its own spec. That is intentional: this document is the first production fixture.

## The problem

Spec docs say "unbuilt" after the thing ships. This is not hypothetical — it has recurred across at least three recent trains:

1. **PR #74** (commit `dd7696a`, "P2 — status drift (same class #70 fixed, recurred in this train)"): `docs/manuscript-visualizations.md` still said *Proposed (unbuilt)* and `docs/mirror-parity-check.md` still said *Spec → review → build → review* after both were built and merged; a post-merge review had to flip them.
2. **PR #70**: `docs/beta-reader-instrument.md` carried the same stale *Proposed (unbuilt)* status into review; fixed in-PR (commit `750bc73`, "Built status").
3. **ROADMAP.md Board**: "Framework Overview Dashboard" sits in the **Backlog** column while `plugins/apodictic/overview-dashboard.html` exists (and the v1.0 Done entry itself lists "overview dashboard" as shipped).

Investigating for this spec surfaced **two more live instances, unfixed today**:

4. `docs/followups-batch-spec.md` line 3 still reads "**Status:** Spec, …" though all three follow-ups (finding-trace glob, legal-risk wiring, project dashboard) shipped in the #66/#74 train — `plugins/apodictic/project-dashboard.html` exists, the changelog fragments are in `changelog.d/`.
5. `docs/runner-governed-execution.md` line 3 says increment 5 (structured gate-event records) is "designed …, **not yet built**" — but ROADMAP's v2.1.0 Done entry records increment 5 as built and shipped, and `gate-state` is live in `scripts/validate.sh`.

Stale "unbuilt" statuses are worse than ordinary doc rot: agents in this repo implement *from specs* (`AGENTS.md` § The flow), so a spec that misreports built-ness invites a duplicate build or a wrong scoping decision.

## Feasibility analysis — the false-positive problem, honestly

**A naive lint is unshippable.** "Flag any `docs/*.md` whose status says unbuilt" fires on every genuine future-feature spec — and this repo has many, *correctly* unbuilt: `annotated-manuscript.md`, `author-voice-fingerprint.md`, `content-advisory.md`, `continuity-bible.md`, `draft-regression-testing.md`, `promise-contract-audit.md`, `reader-persona-simulation.md`, `uncertainty-intake-interview.md` all read "Proposed (unbuilt)" and all describe deliverables (e.g. `scripts/persona_divergence.py`, `scripts/continuity_bible.py`) that verifiably do not exist. A lint that flags eight true negatives to catch one stale doc gets disabled within a week.

**Heuristic built-ness inference is also unshippable.** The unbuilt specs each name a "Proposed implementation surface" full of paths — but those lines *mix* not-yet-existing paths with existing ones (`run-core.md`, `Argument_State.md`, existing skill references), so "extract paths from the doc and check existence" false-positives immediately. This repo's own review doctrine warns exactly here: a `*_Revision_Calendar_*` file once satisfied a `*_Revision_*` glob meant for the Report (`AGENTS.md` § Review practices). Lookalike/incidental path matching is the known failure mode; don't build a check on it.

**ROADMAP cross-check: assessed and rejected (as a mechanical check).** The idea — flag a Backlog/Planned entry whose artifact exists — fails on the mapping. ROADMAP Board cells are anchor links to prose sections; per-section statuses are freeform bold annotations ("— **Built (Increment 1)**", "increments 1–3 built … increment 4 remains future"); many Backlog entries name *no* artifact at all (Model-Capacity Exploitation, Episode Cadence, Multi-Party Intake); and the one real ROADMAP instance — Framework Overview Dashboard — never names `overview-dashboard.html` anywhere in its own section. Entry→artifact mapping requires inference, not parsing. A fuzzy matcher here is precisely the cries-wolf lint this spec exists to avoid. Deferred (see §Non-goals); the ROADMAP instance gets a one-time hand adjudication instead (§Seeding).

**Chosen signal: the opt-in deliverable marker.** A spec doc *declares* its build artifact in a machine-readable HTML comment. The lint flags a doc **only if** (a) it carries a marker, (b) the marker's condition is now true (the deliverable exists), **and** (c) the doc's Status line still reads unbuilt. The false-positive argument is structural, not statistical:

- **Un-marked docs are never flagged.** Every legacy spec, research draft, decision record, and level-setting doc is out of scope until someone opts it in. Zero false positives by construction on the existing corpus.
- **The marker is authored by the spec writer at spec time**, who knows the deliverable path — every Horizon-Tier-1 spec already names it in its own Status line ("Proposed implementation surface: … `scripts/annotation_manifest.py` …"), so the marker is derivable verbatim, today, for every seeded doc.
- **The condition is binary and mechanical** (path exists; optionally, file contains a literal). No globs, no inference.

**Would it have caught the real instances?** Scored honestly against all six above:

| Instance | Caught? | How / why not |
|---|---|---|
| `manuscript-visualizations.md` (#74) | **Yes** | marker → `scripts/viz_manifest.py`; path named in the spec since its unbuilt draft |
| `mirror-parity-check.md` (#74) | **Yes** — but only via the `contains` form | deliverable is a *subcommand inside* `scripts/validate.sh`, not a new file; plain path-existence is always-true there |
| `beta-reader-instrument.md` (#70) | **Yes** | marker → `scripts/reader_instrument.py`; caught pre-review instead of in-review |
| `followups-batch-spec.md` (#66 train) | **Yes** | marker → `plugins/apodictic/project-dashboard.html` |
| ROADMAP "Framework Overview Dashboard" | **No** | ROADMAP out of mechanical scope (above) |
| `runner-governed-execution.md` incr 5 | **No** | partial-built status ("1–3 built … 5 not yet built"); the conservative built-guard (§Failure condition) deliberately stands down on mixed statuses |

4 of 6, at ~150 lines of stdlib Node and zero false positives on the current tree. **Verdict: worth building — in this small form and no bigger.** The two misses are not solvable mechanically without fuzzy matching (ROADMAP) or per-increment status grammar (RGE) — both rejected as false-positive factories. They are covered instead by the lighter companion deliverable: a one-line review-checklist addition to `AGENTS.md` (§The lighter half) plus one-time hand-fixes in the seeding PR. If the reviewer judges even the 4/6 mechanical half not worth a CI step, the fallback is the AGENTS.md line + seeded markers with no script — but the self-test cost is low and the marker without an enforcer is just documentation, so this spec recommends shipping the script.

## Form: standalone `scripts/check-status-drift.mjs`

A standalone Node script, **not** a `validate.sh` validator. Three repo-specific reasons, each verified:

1. **Self-testable-count entanglement.** `validate.sh --self-test-all` hardcodes its count ("all 40 self-testable validators", `scripts/validate.sh` lines 169/190/203/206), and a concurrent PR is single-sourcing that count. A new validator arm would bump it and collide. A `.mjs` changes nothing in `validate.sh`.
2. **The dual-script mirror.** Every `validate.sh`/`*.py` validator must exist byte-identical in `scripts/` and `plugins/apodictic/scripts/` (`AGENTS.md` § Platform parity). `*.mjs` build/repo tooling is root-only and explicitly excluded from the mirrored set (`docs/mirror-parity-check.md` § The mirrored set) — no sync burden, no `check-mirror` interaction.
3. **It polices repo docs, not editorial artifacts.** `validate.sh` validators check manuscript-run artifacts and canonical framework files; this lint checks repo documentation hygiene, the same class as `assemble-changelog.mjs --check` — which is the template.

**Template** (confirmed against `scripts/assemble-changelog.mjs` and `ci.yml`): plain `#!/usr/bin/env node`, stdlib-only (`node:fs`, `node:path`), `repoRoot` resolved from `import.meta.url`, a `fail(message)` that prints `check-status-drift failed: …` and exits 1, argv-flag dispatch in `main()`, exit 0 with a one-line PASS summary. Self-test follows the `build-codex.mjs --self-check` / `check-mirror --self-test` house pattern: hermetic temp-dir fixtures, no repo mutation.

### CLI

```
node scripts/check-status-drift.mjs              # scan the repo; exit 0 clean / 1 stale or error
node scripts/check-status-drift.mjs --check      # synonym for the default (uniformity with sibling CI steps)
node scripts/check-status-drift.mjs --root <dir> # override the scan root (the self-test seam)
node scripts/check-status-drift.mjs --self-test  # hermetic fixture suite (temp dir); exit 0 only if all pass
```

No write mode exists; the default *is* the check.

## Marker syntax

An HTML comment (invisible in rendered markdown), one marker per line, anywhere in the doc — recommended placement: immediately below the Status line. Two forms:

```
<!-- built-when: <repo-relative-path> -->
<!-- built-when: <repo-relative-path> contains "<literal>" -->
```

- **Form 1** is true when `<repo-relative-path>` exists (file or directory). Use when the deliverable is a new file (`scripts/annotation_manifest.py`) — the overwhelmingly common case here.
- **Form 2** is true when the path exists **and** its content includes the exact literal (plain substring, no regex). Use when the deliverable lands *inside* an existing file — the `mirror-parity-check` case (`scripts/validate.sh contains "check-mirror"`). The spec author should pick a string that can only exist post-build (a dispatch case, a function name).

**Grammar, exactly:** `<!--` optional-spaces `built-when:` spaces PATH [ spaces `contains` spaces `"` LITERAL `"` ] optional-spaces `-->`, all on one line. PATH contains no whitespace, no glob characters (`*` `?` `[`), is not absolute, and contains no `..` segment — resolved against the repo root only. LITERAL contains no `"`. Multiple markers per doc are allowed (multi-deliverable specs); the doc's condition is true if **any** marker's condition is true.

**Fenced-code immunity:** markers inside ``` fenced blocks are ignored (a simple line-based fence toggle). Without this, any doc quoting the syntax — including this one — becomes a false positive. A self-test fixture covers it.

## Status line and unbuilt patterns

**Status line:** the first line in the doc that, after stripping leading whitespace and `*`/`_` emphasis, starts with `Status:` (case-insensitive). Both house styles match: `**Status:** …` and `*Status: Active*`. Only this single line is pattern-scanned — body prose discussing built-ness is never matched.

**Unbuilt patterns** (case-insensitive, against the Status line only — each attested by a real doc in `docs/` today):

| Pattern | Attested by |
|---|---|
| `unbuilt` | "Proposed (unbuilt)" — eight Horizon specs |
| `not yet built` / `not built` | `runner-governed-execution.md`, `subagent-architecture-design.md` |
| `not yet implemented` | `pass3-pass7-setec-supplement-spec.md` |
| `spec` + `→`/`->` + `review` + `build` (arrows, optional spaces) | old `mirror-parity-check.md`, `followups-batch-spec.md` |
| `ready for build` | `writers-block-module-build-spec.md` |

**Must NOT match** (verified against every current Status line): "**Built**", "Increment 1 built", "Increments 1–3 built", "Will not build" (matches no pattern: "not build" ≠ "not built"), "Research draft", "Active", "Accepted", "accepted decision note", "Design concept" alone.

**The built-guard (conservative tie-breaker):** after removing all matched unbuilt-pattern spans from the Status line, if the remainder still matches `\b(built|shipped|implemented)\b` (case-insensitive), the doc is treated as *partially built* and **not flagged**, even if a marker is true. This is what makes "Increments 1–3 built; increment 5 … not yet built" green — a deliberate false **negative** (it costs us the RGE instance) bought to guarantee no multi-increment doc is ever falsely flagged. Per-increment drift is out of mechanical scope (§Non-goals). Note the guard uses word boundaries: "buildable" does not trip it, so `followups-batch-spec.md` ("buildable + safe" in its Status line) is still correctly flaggable.

## Failure condition, exactly

For each marker-bearing doc:

- **STALE** (exit 1): at least one marker's condition is true, AND the Status line matches an unbuilt pattern, AND the built-guard does not stand down. Message names the doc, the Status excerpt, and the satisfied marker path: `STALE: docs/foo.md — Status says "Proposed (unbuilt)" but deliverable exists: scripts/foo.py`.
- **ERROR** (exit 1), the hard config failures that keep the check non-vacuous: a malformed marker (unparseable tail after `built-when:`, glob char, absolute path, `..`); a marker-bearing doc with no detectable Status line.
- **Vacuity guard** (exit 1): zero markers found across the whole scope. Seeding (below) lands in the same PR, so a zero-marker state can only mean the markers were refactored away — the lint must not pass silently as a no-op.
- Everything else is **green**: marker false + unbuilt status (the normal pre-build state — these docs are the tripwires); marker true + built status; no marker at all.

## File scope

**Initial scope: `docs/**/*.md` only** (recursive, so the eval-pilot and sources subdirectories are included; markers are opt-in, so the recursion is free). **Deferred:** `ROADMAP.md` (mapping is prose-fuzzy — §Feasibility; a possible later extension is markers placed inside ROADMAP sections, but section-scoped status semantics are genuinely mixed per-increment, so it needs its own design); module status lines under `plugins/apodictic/**/references/*.md` (no uniform Status convention there); `README.md`/`CONTRIBUTING.md`; reverse drift (status "Built" but deliverable deleted).

## Seeding — useful on day one, exit-0 on day one

Ship the mechanism **with markers seeded**, not adopt-going-forward; an enforcer with nothing to enforce proves nothing in CI. All seeds verified green against the current tree:

**Built specs** (marker true + Status already says built → green; these prove the marker plumbing reads real files):

| Doc | Marker | Verified |
|---|---|---|
| `docs/manuscript-visualizations.md` | `built-when: scripts/viz_manifest.py` | exists; Status "**Increment 1 built**" |
| `docs/beta-reader-instrument.md` | `built-when: scripts/reader_instrument.py` | exists; Status "**Built.**" |
| `docs/mirror-parity-check.md` | `built-when: scripts/validate.sh contains "check-mirror"` | present; Status "**Built**" |

**Unbuilt specs** (marker false → green; these are the actual tripwires for the next Horizon-Tier-1 build train — the recurrence the lint exists to stop). All eight paths verified absent from `scripts/` today:

| Doc | Marker target |
|---|---|
| `docs/annotated-manuscript.md` | `scripts/annotation_manifest.py` |
| `docs/continuity-bible.md` | `scripts/continuity_bible.py` |
| `docs/draft-regression-testing.md` | `scripts/regression_diff.py` |
| `docs/reader-persona-simulation.md` | `scripts/persona_divergence.py` |
| `docs/author-voice-fingerprint.md` | `scripts/author_fingerprint.py` |
| `docs/uncertainty-intake-interview.md` | `scripts/intake_interview.py` |
| `docs/promise-contract-audit.md` | `scripts/promise_contract.py` |
| `docs/content-advisory.md` | `scripts/content_advisory.py` |

Plus this doc's own live marker (`scripts/check-status-drift.mjs`), whose Status the builder flips to Built.

**Hand-fixes in the same PR** (the lighter half doing the work the lint can't; required so a seeded marker on #1 stays green):

1. `docs/followups-batch-spec.md` — flip Status to Built (all three follow-ups shipped); optionally seed `built-when: plugins/apodictic/project-dashboard.html`.
2. `docs/runner-governed-execution.md` — Status line: increment 5 → built (matching ROADMAP v2.1.0).
3. ROADMAP "Framework Overview Dashboard" Backlog entry — **flag for maintainer adjudication, don't silently move it**: `overview-dashboard.html` shipped in v1.0, but the Backlog entry ("Build after command restructuring is settled") may intend a redesign. Annotate the entry with whichever the maintainer confirms.

## CI wiring

One new step in `.github/workflows/ci.yml`, after "Changelog fragments parse" (its closest sibling — both are repo-doc hygiene gates on Node 22, already set up):

```yaml
      - name: Status-drift lint (spec Status vs shipped deliverables)
        run: |
          node scripts/check-status-drift.mjs --self-test
          node scripts/check-status-drift.mjs
```

Exit-0 on the current repo is guaranteed by the seeding table above (every seeded marker is either true-with-built-status or false) plus the two hand-fixes. The build must verify this by running the step's exact commands before opening the PR — do not land a red check.

## Self-test (non-vacuity proof)

`--self-test` builds hermetic fixtures in a temp dir and runs the engine via `--root`. Each case asserts the **exit code and the specific finding** (file named, right reason) — a check that fails for the wrong reason is the house anti-pattern. Minimum fixture set:

1. marker + existing path + Status "Proposed (unbuilt)" → **STALE**, names the doc and path (proves the lint can fire at all)
2. marker + missing path + unbuilt Status → clean (the normal pre-build spec)
3. no marker + unbuilt Status → clean (legacy specs never flagged)
4. marker + existing path + Status "**Built**" → clean
5. `contains` form: literal present + unbuilt Status → **STALE**; literal absent (file exists) → clean
6. partial status "Increments 1–3 built. Increment 5 not yet built." + true marker → clean (pins the built-guard, documents the deliberate miss)
7. marker inside a fenced code block + existing path + unbuilt Status → clean (fence immunity)
8. malformed marker (glob char; `..` path; absolute path; unparseable tail) → **ERROR**
9. marker-bearing doc with no Status line → **ERROR**
10. zero markers in scope → **ERROR** (vacuity guard)

## The lighter half — AGENTS.md convention line

The two mechanical misses (ROADMAP board, per-increment status) are covered by convention, where the reviewer already works. Add one bullet to `AGENTS.md` § Review practices:

> - **Flip the status when you build.** A build PR flips its spec doc's `**Status:**` line and its ROADMAP entry in the same PR — and new specs declare their deliverable with a `built-when` marker (syntax: `docs/qol-status-drift-lint.md` §Marker syntax) so `scripts/check-status-drift.mjs` catches the miss mechanically (status drift recurred across #66/#70/#74).
>
> (Wording note for the builder: inside the scanned scope (`docs/**/*.md`), keep any literal `built-when` HTML-comment *example* inside a fenced code block, or it will itself parse as a marker. `AGENTS.md` is outside the scan scope, but the same hygiene keeps the convention copy-paste-safe.)

## Verification gates (all green before PR)

1. `node scripts/check-status-drift.mjs --self-test` — all fixtures pass
2. `node scripts/check-status-drift.mjs` — exit 0 on the seeded repo
3. `bash scripts/validate.sh --check-all` — the real CI gate, run first per `AGENTS.md`; **self-testable count unchanged at 40/40** (the non-entanglement claim, re-enumerated, not assumed)
4. `node scripts/assemble-changelog.mjs --check` — the build adds a `changelog.d/<slug>.md` fragment (single `### ` thematic header; suggest `### Tooling`)
5. `node scripts/release-generate.mjs --check`
6. `node scripts/build-codex.mjs --self-check && node scripts/build-antigravity.mjs --self-check`
7. No mirror sync required (`.mjs` is root-only) — but `validate.sh check-mirror` still green as part of (3)

## Non-goals

- **No ROADMAP board parsing or fuzzy entry→artifact matching** — rejected in §Feasibility; deferred pending a marker-in-ROADMAP design if drift recurs there.
- **No per-increment status grammar.** One doc, one binary built/unbuilt judgment; mixed statuses are conservatively green.
- **No reverse-drift detection** (Status "Built" but artifact deleted) — different failure class, no observed instance.
- **No auto-fixing.** Detection only, like `check-mirror`; the status flip stays a deliberate human/agent edit.
- **No mandatory markers.** Opt-in stays opt-in; un-marked docs are never flagged and never will be — that is the false-positive guarantee, not a gap to close later.
- **No `validate.sh` integration**, now or later-by-default — re-homing it would re-create the count/mirror entanglements this form avoids.
