# AGD-scan behavioral benchmark (R3B §4)

The producer/consumer AGD seam's two-phase, reproducible behavioral benchmark:
does SETEC's `agd_move_scan` surface (the producer's LOCATED move observations)
agree with the APODICTIC AGD Move Audit's own §10.9 M-record inventory (the
consumer's adjudicated moves)?

- **Phase 1 — ACQUISITION** (online, run once, artifacts committed): `acquire.py`
  runs the live judge per fixture/vendor/rep and commits a **run-manifest** per
  cell under `manifests/`.
- **Phase 2 — SCORING** (offline, deterministic, re-runnable forever): `score.py`
  replays every committed manifest through the consumer channel and compares the
  located observations to the fixture's §10.9 M-records. The report lands in
  `docs/argument-benchmark-calibration-round.md` **§M-AGD**.

**The ownership rule (R4A ADR D5).** The scorer measures scan↔audit **agreement**
only. It never adjudicates argument quality and never treats observation **count**
as a quality signal. There is no aggregate beyond the agreement bookkeeping.
A scan observation is a *pointer*; the audit's M-records are the findings.

```
evals/benchmark/agd-scan/
  README.md              this file
  acquire.py             Phase-1 acquisition driver (online, run-once)
  host_judge_cmd.py      per-vendor blind transport (SETEC_HOST_JUDGE_CMD)
  acquisition-log.md     per-cell acquisition record (obs count + span drops)
  manifests/             the 20 committed run-manifests (READ-ONLY)
  score.py               Phase-2 scoring harness (offline, deterministic)
  _scratch/              acquisition envelopes (gitignored working area)
```

---

## The run-manifest schema (pinned)

Each `manifests/<fixture>--<vendor>--rep<1|2>.json` is exactly:

```json
{
  "fixture_id": "<one of the 5 R3A fixtures, by name>",
  "vendor": "fable" | "codex",
  "model_id": "claude-fable-5" | "gpt-5.6-sol",
  "prompt_fingerprint_sha256": "<the producer's rendered-judge-prompt fingerprint>",
  "rep": 1 | 2,
  "acquired_at": "<UTC ISO-8601 timestamp>",
  "values": { "observations": [
    { "family": "ASSURING" | "GUARDING" | "DISCOUNTING",
      "span": "<substring of source.md, verbatim up to WHITESPACE FOLDING — the
               producer's span-integrity containment folds whitespace runs, so a
               judge's quote may fold the source's line-wrap newlines and still
               anchor; many committed spans do>",
      "paragraph_index": <int, 0-based, blank-line paragraph>,
      "cue": "<surface cue>" | null }
  ] }
}
```

- **20 cells** = 5 fixtures × {`fable`, `codex`} × rep{`1`, `2`}.
- `values.observations` is the **producer-normalized** set (the §1a span-integrity
  drops already applied at acquisition — see the drop counts in
  `acquisition-log.md`). The producer's `manifest` judge reads this
  top-level-first shape (`{"values": {"observations": [...]}}`) and re-emits it
  verbatim, so Phase-2 replays are deterministic.
- `prompt_fingerprint_sha256` is `f07f8f4adafaf9eebb47ff72dca640042c5bc4c576044d9f1d79002733c2bcf5`
  for every cell (the same producer prompt rendered every run). Phase-2 pins it
  with `--expect-fingerprint`; a drift is a scoring ERROR (below).

The manifests are **committed and READ-ONLY** — never regenerate or rewrite
them. Re-acquiring (`acquire.py`) skips existing cells unless `--force`.

---

## Phase 1 — acquisition (online, run once)

Driver: `acquire.py` (repo root). For each cell it runs the **consumer shim**
against the fixture's `source.md` with the producer's `agent_host` judge backend,
whose per-request transport is `host_judge_cmd.py`:

```
python3 evals/benchmark/agd-scan/acquire.py [--vendor fable|codex] [--fixture NAME] [--rep 1|2] [--force]
```

Internally each cell runs (schematically):

```
SETEC_VOICEPRINT_DIR=<producer worktree>/plugins/setec-voiceprint \
JUDGE_VENDOR=<vendor> SETEC_HOST=<claude-code|codex-cli> SETEC_HOST_MODEL=<model> \
SETEC_HOST_JUDGE_CMD="python3 evals/benchmark/agd-scan/host_judge_cmd.py" \
SETEC_HOST_JUDGE_TIMEOUT=900 \
python3 plugins/apodictic/skills/specialized-audits/scripts/ai_prose_agd_move_scan.py \
    evals/fixtures/argument-agd/<fixture>/source.md \
    --judge agent_host --json --out <scratch>.json --out-md <scratch>.md
```

**Vendor transports (`host_judge_cmd.py`).** The producer's `agent_host` backend
pipes a request JSON (`{system, no_verdict, content}`) to the transport's stdin
and reads the model's JSON text back from stdout:

- `codex` → `codex exec -m gpt-5.6-sol -c model_reasoning_effort="xhigh"
  -s read-only --skip-git-repo-check`, run with **cwd = an empty temp dir**
  (never the repo). *This is the transport that produced the committed codex
  cells.*
- `fable` → `claude -p --model claude-fable-5 --tools ""` (Claude Code CLI, all
  built-in tools disabled). **This branch could NOT produce the committed fable
  cells**: `claude` refuses to launch nested inside a running Claude Code
  session, so the 2026-07-12 fable cells were acquired through the **host's
  subagent adapter** instead — one fresh Claude-Code subagent per rep
  (spec 35's host-adapter case), each given the identical assembled judge input
  plus a do-not-use-tools/do-not-read-files preface, its raw JSON output then
  normalized through the producer's own `normalize_observations` before the
  manifest was written (drops logged; all cells recorded 0). The
  `host_judge_cmd.py` fable branch is the standalone/headless path for any
  future re-acquisition.

**Blindness measures — stated exactly.** Neither judge's prompt contains the
fixture's §10.9 keys (`argument-state.md`), any file path, or any mention of a
repository — the prompt is the producer's rendered judge input plus a minimal
transport preface, nothing else. Mechanically: the codex sandbox is read-only
with an **empty cwd**, so nothing key-shaped is in reach without a deliberate
absolute-path hunt the prompt gives no basis for; the fable subagents HAD tools
available but were instructed not to use them, and **0 tool uses were observed
on every rep** (the per-rep usage counters; recorded here because an
instruction is not an enforcement — the future CLI path closes this with
`--tools ""`). Reps are independent fresh processes; identical reps are
themselves calibration data.

Every span-integrity drop from acquisition is appended to `acquisition-log.md`,
so nothing is silently lost. (All 20 committed cells recorded **0 drops**.)

---

## Phase 2 — scoring (offline, deterministic, re-runnable forever)

Harness: `score.py` (stdlib-only). It reuses the §10.9 validator's parsing and
Source-anchor normalization from `scripts/argument_agd.py` (`extract_section`,
`parse_block`, `_norm`, `anchor_resolves`) — imported, never forked.

### Offline replay (per cell)

`score.py` replays each manifest through the **same consumer channel** an
APODICTIC audit would use, with the producer's `manifest` judge:

```
SETEC_VOICEPRINT_DIR=<producer worktree>/plugins/setec-voiceprint \
python3 plugins/apodictic/skills/specialized-audits/scripts/ai_prose_agd_move_scan.py \
    evals/fixtures/argument-agd/<fixture>/source.md \
    --judge manifest --judge-manifest manifests/<cell>.json \
    --expect-fingerprint <the manifest's own prompt_fingerprint_sha256> --json
```

`SETEC_VOICEPRINT_DIR` is taken from the environment; a scoring run **errors
loudly and exits 2** if it is unset. `results.observations` is taken from the
returned schema_version 1.0 envelope. A **non-available envelope** or a
**fingerprint-drift refusal** (`available: false`, `reason: judge prompt
fingerprint drift …`) is a **scoring ERROR** for that cell — loudly reported,
never silently skipped, and it fails the hard gate if it hits a gate cell.

### The comparison coordinate (§1b, made mechanical)

An M-record's machine-resolvable coordinate is its **`Source anchor`**, resolved
this way (the §1b dedup rule):

1. Extract the anchor's verbatim quote (the `"<quote>" @ <locus>` grammar, mirrors
   `argument_agd` Check 4).
2. Confirm it **resolves** in `source.md` under `argument_agd` normalization
   (whitespace runs folded; smart quotes and en/em dashes normalized;
   **case-sensitive**). It must resolve — it does under `--check-all`; a
   non-resolving anchor is a **loud error**.
3. Split `source.md` into **blank-line paragraphs** using the **producer
   convention** (`re.split(r"\n\s*\n", text.strip())`, then strip + drop empties
   — a verbatim mirror of the producer's `split_paragraphs`), so the paragraph
   index space matches the observations' `paragraph_index`.
4. Find the **one** normalized paragraph whose normalized text contains the
   normalized anchor — that is the record's **derived paragraph**. Zero paragraphs
   (unreachable given step 2) or **more than one** (ambiguous) is a **loud error**,
   never a guess.
5. Locate the anchor at its **first occurrence** in that normalized paragraph as
   a half-open interval `[start, end)`.

The prose **locus label is never a comparison operand** (M-records carry no
paragraph index; in `legit-guarded-generalization` M1 the label and the anchor
sit in different paragraphs — matching on the label would flip the verdict).

### The match rule + taxonomy (exactly as implemented)

A scan observation **matches** an M-record iff **all three**:

- **same derived paragraph** — `observation.paragraph_index` equals the record's
  derived paragraph; **and**
- **same family** — `observation.family` equals the record's AGD family; **and**
- **normalized-span interval overlap** — each span is located at its first
  occurrence in that same normalized paragraph, and the two half-open intervals
  **intersect non-emptily** (`a.start < b.end and b.start < a.end`;
  **adjacent-but-disjoint** spans like `[0,5)` and `[5,10)` do **not** overlap).

Per-M-record outcome (§4 rep-outcome taxonomy):

| Outcome | Condition |
|---|---|
| **CORRECT**   | ≥1 observation overlaps the record's coordinate with the **same** family |
| **INCORRECT** | ≥1 observation overlaps the coordinate with a **different** family, and **none** with the same family |
| **SOFT**      | **no** observation overlaps the coordinate at all |

Per cell the harness also enumerates:

- **misses** — M-records with no same-family overlapping observation (i.e. SOFT
  or INCORRECT records).
- **extras** — observations overlapping **no** M-record coordinate (same
  paragraph + interval overlap, family-independent). Extras are **CALIBRATION
  DATA**, never an error — the audit's decline path exists for exactly these
  (an observation the audit inventories at no locus, e.g. a legitimate cited
  data report with no strippable assurance span).

### The one hard gate (§4 pass criteria — the wedge claim)

Fixture **`cue-free-structural-discounting`**, **M1** (family **DISCOUNTING**):

- **≥1 CORRECT rep per vendor** (fable *and* codex each have at least one CORRECT
  rep on M1), **and**
- **0 INCORRECT reps** on M1 across **all** reps of that fixture.

`score.py` **exits 1** if the gate fails and prints the failing per-vendor /
INCORRECT lines. Everything else in the report is calibration data, not gated.

### Running Phase 2

```
export SETEC_VOICEPRINT_DIR=<producer worktree>/plugins/setec-voiceprint   # setec-voiceprint v1.124.0

# 1. matcher self-test (synthetic, in-memory, no file IO):
python3 evals/benchmark/agd-scan/score.py --self-test

# 2. score all 20 cells; print the table + hard-gate verdict; exit 1 iff the gate fails:
python3 evals/benchmark/agd-scan/score.py

# 3. emit the §M-AGD markdown to stdout:
python3 evals/benchmark/agd-scan/score.py --report

# 4. append/replace the §M-AGD section in docs/argument-benchmark-calibration-round.md:
python3 evals/benchmark/agd-scan/score.py --write-report
```

The §M-AGD report is **generated by running the scorer** — its result cells are
never hand-written. Re-running Phase 2 needs only the committed manifests, the
fixtures, and a `setec-voiceprint` checkout at the pinned tag; it is fully
offline and deterministic.

---

## Provenance (pinned)

- **Producer:** `setec-voiceprint` **v1.124.0** (the `agd_move_scan` surface,
  `handoff: experimental`, `calibration_status: heuristic`).
- **Prompt fingerprint:** `f07f8f4adafaf9eebb47ff72dca640042c5bc4c576044d9f1d79002733c2bcf5`.
- **Consumer base:** `apodictic` **v2.9.0** (the R3B A-1 consumer shim + validator).
- **Vendors:** `fable` = **claude-fable-5** via fresh Claude-Code subagents (no
  tools, prompt-only); `codex` = **gpt-5.6-sol** at `model_reasoning_effort=xhigh`
  via `codex exec` in an empty-cwd read-only sandbox. Both received the producer's
  exact rendered judge prompt plus a minimal transport preface.
- **Acquisition:** 2026-07-12 (per-cell record in `acquisition-log.md`).
