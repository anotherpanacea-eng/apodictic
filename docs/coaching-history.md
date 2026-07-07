# Coaching History & Pattern Recognition — the cross-session process pattern, opt-in and deletable

**Status:** **Built (Increment 1, v1 scope).** Shipped: the `apodictic.coaching_observation.v1` schema, `scripts/coaching_history.py` + `validate.sh coaching-history` (H1–H7 + W1 + the `delete <project_root>` subcommand), the canonical `example-coaching-history/` project fixture wired into `--check-all` under `--strict` (positive + five hostile ethics-gate arms + a delete round-trip), and the `revision-coach` skill contract §9. Self-testable validators count is **derived** from `validate.sh`'s `AGG_VALIDATORS` (not a hand-maintained number). This is APODICTIC's ONE ethically-sensitive surface; the two Fable conditions (2026-07-05) are mechanized as **H5** (writer-visible / no coach-only shadow) and **H6 + `delete`** (deletion honored, recomputed). Roadmap: `ROADMAP.md` → [Coaching Deepening](../ROADMAP.md#coaching-deepening).
<!-- built-when: scripts/coaching_history.py -->

Today each `/coach` session plans in isolation; nothing surfaces the pattern that spans them — "the same finding was set aside three sessions running." Over multiple revision cycles that cross-session pattern is exactly what a good coach remembers. Coaching History surfaces it as a **rolling, opt-in, local-only artifact of provenance-bound, descriptive observations**, each **mechanically derived from recorded session history** (a count over the recorded finding-disposition / revision-arc records — a count, not a vibe), carrying **no editorial severity** (a claim about the writer's *process* is orthogonal to a manuscript defect — no Must/Should/Could token, no `apodictic:finding` block).

## Posture — an observation about process, never a verdict about the writer

A cross-session pattern is a claim about the writer's process, so it is fenced by the same discipline as the [Author Voice/Craft Fingerprint](author-voice-fingerprint.md) ("observations, not judgments," local-only, provenance-bound) and the State Card (rolling, id-tracked, cross-round). The coach **surfaces** a mechanical pattern and lets the writer interpret it — never diagnoses the writer, prescribes, predicts, or softens a manuscript finding.

## What this is not

- **Not** a defect list. A coaching observation is **not** an `apodictic.finding.v1` and carries **no** severity. (`H4`.)
- **Not** a stylometric or content audit. It reads only the recorded workflow records (`finding_disposition` sessions, revision-arc phases), never the manuscript prose.
- **Not** unbidden. Cross-session behavioral observation is sensitive, so it is **opt-in** and produced only under the writer's explicit consent marker (`H0`/opt-in gate).

## The two v1 patterns (mechanically derivable today)

v1 ships **only** the two patterns derivable from data that exists now; `stuck-point-cluster` / `completion-drift` are deferred to v2 (they need a session-plan / stuck-family taxonomy that does not exist).

- **`deferral-recurrence`:** the same finding carries `disposition == "deferred"` across an **unbroken run** of `finding_disposition.session` ordinals (a missing ordinal resets the streak). `count` = streak length (floor **≥3**); `evidence` = `<F-id> deferred @ session <n>` per streak member. **Provenance surfaces + the F2 honesty boundary (H2 reads both):** on **governed** projects H2 reconstructs the full multi-session run from the independent `execution.gate_events[].disposition_deltas` event records (each delta carries its own `session`) — this surface is what makes the anti-fabrication guarantee *fabrication-resistant*. On **non-governed** projects the folded `execution.finding_dispositions` map is last-event-wins, so the multi-session history is the `sessions` list `/coach` **persists at disposition time** — a **self-reported** field, not independently verified (the mode-11 recorded-field-without-verifier antipattern). H2 therefore (a) scopes the guarantee to governed projects (stated in the docstring + here), and (b) requires a **non-governed observation to carry a visible honesty caveat** that its streak is from the coach's own notes (the H2 non-governed-caveat check), so the writer never sees an unverified pattern as if it were checked.
- **`phase-incompletion`:** a `revision_arc` phase stays uncompleted across **≥`count` consecutive sessions** (floor **≥2**); `evidence` = `phase <label> incomplete @ session <n>`. **No governed verification path exists (Codex round-1 P1).** Per-session revision-arc-phase completion is recorded **nowhere**: `finding_states` is a rolling last-write map (no per-session history), `finding_deltas` carry no session ordinal (only `disposition_deltas` do), and the revision arc is a **stateless re-plan that overwrites the prior arc each run** (no history). So a `phase <label> incomplete @ session <n>` reference has **no recorded ground truth to check against on ANY project** — it is inherently **self-reported everywhere**. H2 does the shape + consecutive checks it *can* do and does **not** invent a verification it cannot perform; instead it requires the honesty caveat on **every** phase-incompletion observation (governed or not).

Per-pattern floors were **closed by the Fable verdict** (`deferral-recurrence` ≥3, `phase-incompletion` ≥2). The schema keeps only the global `count ≥ 2`; `H1` enforces the per-pattern floors.

**Pattern-by-pattern verification status (the anti-fabrication class — every pattern is either verified-against-record or self-reported-and-caveated, none shape-checked-only):**

| Pattern | Governed verification path? | Treatment |
| --- | --- | --- |
| `deferral-recurrence` | **Yes** — `gate_events[].disposition_deltas` (independent per-session records). | Governed: verified against the record, no caveat. Non-governed: self-reported → mandatory caveat. |
| `phase-incompletion` | **No** — per-session phase completion is persisted nowhere. | Self-reported on **all** projects → mandatory caveat, always. |

## The checks

| Check | What it catches |
| --- | --- |
| **H1 schema + unique + floor** | bad `pattern` enum / malformed `CH-NN` / missing field / broken JSON / duplicate id within the artifact; a per-pattern count below its floor. |
| **H2 provenance / anti-fabrication** | (deferral-recurrence) an `evidence` reference that does not resolve — the `F-id` must match `^F-[A-Za-z0-9]+-[0-9]{2,}$` **and** a recorded `deferred` disposition must exist at the cited session; `len(evidence) ≥ count`; the cited sessions must be **actually consecutive** (a gap fails). No fabricated streak. **Fabrication-resistant ONLY on governed projects**; phase-incompletion has no record to verify against at all (see the pattern table above). |
| **H2 self-reported caveat** | (Codex F2 + round-1 P1.) A **self-reported** observation must carry a **visible honesty caveat** that its streak is from the coach's own session notes, not an independently verified record. WARN; ERROR `--strict`; per-id override (shares the `coaching-observation` slug). Self-reported = a **non-governed** `deferral-recurrence`, **or a `phase-incompletion` on any project** (no governed verification path exists). |
| **H3 descriptive, not judgmental** | a prescriptive directive (reuses `author_fingerprint._PRESCRIPTIVE_RE`) or a second-person trait-blame construction ("you always / you fail to / you're bad at"). WARN; ERROR `--strict`; per-id override `<!-- override: coaching-observation CH-NN — <why> -->`. **Known limit:** a lexicon gate catches token framing, not passive trait-attribution ("the pattern suggests reluctance") — semantic validation is a v2 item. |
| **H4 no-severity-leak** | any editorial Must/Should/Could-Fix token (`severity_vocab.SEVERITY_TOKEN_RE`, the M8 SSoT) or any `apodictic:finding` block in the artifact. ERROR. |
| **H7 tentative-framing** | (transference-health.) A third-person trait **verdict** ("writer defers endings", "she's an ending-avoider"), a bare-**scoreboard** rendering (a lone `<label>: <int>` tally), or a confident observation with **no invitation** to the writer's reading. WARN; ERROR `--strict`; shares the H3 per-id override. **Enforceable floor only** — the full "confident about the seeing, open about the meaning" voice is a skill-contract obligation (§6a). |
| **W1 local-only** | an external http(s) URL / telemetry reference. Advisory; ERROR `--strict`. |

## The two ethics gates (the load-bearing part)

### H5 — single-home / no coach-only shadow (Fable condition a: writer-visible)

Coaching observations may persist in **exactly one** writer-facing artifact — the file the coach reads is the file the writer holds, no informational asymmetry. H5 scans the **project root + `runs/*` archives** (the `disposition_check` DP2.6 reachable-evidence scope) **plus the machine-facing `Diagnostic_State.meta.json` sidecar**. **ERROR (non-overridable)** on:

- **(i)** a parsed `apodictic:coaching_observation` block (via `apodictic_artifacts.parse_blocks` — a parsed carrier, not a prose mention) anywhere but the one `*_Coaching_History_*.md`;
- **(ii)** the literal schema-id string `apodictic.coaching_observation.v1` outside that artifact;
- **(iii)** an evidence-grammar string (`deferred @ session <n>` / `phase <label> incomplete @ session <n>`) outside it — the `@ session` token is coaching-history-specific and does **not** collide with the pinned finding-disposition marker grammar (`<!-- deferred: F-… until: … -->`), so a legitimate Coaching-Log disposition marker never trips it;
- **(iv)** more than one `*_Coaching_History_*.md` in scope (a second file **is** the shadow artifact);
- **(v)** any coaching material in the sidecar beyond exactly `coaching_history_seq: <int>` — a recursive key/value walk (any `coaching*` key other than the blessed one, or any string value matching the CH-id regex / schema-id / evidence grammar). The machine-facing sidecar is exactly where a coach-only shadow would accumulate invisibly.

**Scan coverage (Codex review F1 — the projection-ban is only as good as its coverage).** A project root has ~46 tool-authored artifact types (`output-structure.md`: the pass artifacts, `SYNTHESIS.md`, `*_Core_DE_Synthesis_*`, `*_Editorial_Letter_*`, `README.md`, session plans, …). An early draft scanned only a handful of globs — so a projection into an **unlisted** type (the editorial letter, the synthesis) would have escaped H5 **and** survived `delete` (a false "deletion honored", breaking *both* Fable gates, since H6 rests entirely on H5's projection ban). The fix:

- **(i) block + (ii) schema-id** are self-identifying apodictic markers with **zero** false-positive risk on any legitimate non-coaching file (no editorial letter / session plan / manuscript legitimately carries a coaching_observation block or the schema-id). They are scanned over **every `*.md` in scope** minus the one Coaching_History artifact — the exhaustive net that catches the real projection.
- **(iii) the evidence-grammar standalone scan + the bare `CH-NN` WARN token** *do* carry manuscript false-positive risk (chapter "CH-12" refs; prose "@ session"), so they scan every `*.md` **minus the positively-identified frozen manuscript snapshot** (`*_Manuscript_Snapshot_*.md`, the intake-persisted copy — `annotation_manifest._SNAPSHOT_GLOB`), **not** an authored-artifact allowlist. A real projection is already caught by (i)/(ii); (iii) is the secondary net for grammar-without-block leakage (the §6a paraphrase class). *(Note: the manuscript snapshot is NOT exempt from (i)/(ii) — a coaching_observation block or the schema-id in the writer's prose is a pasted projection, not legitimate manuscript content.)*

**Depth-completeness (Codex round-1 class sweep, item 3).** "Every `*.md` in scope" means **every depth**: the `.md` signature scan and the Coaching_History enumeration walk the project root **recursively** (`os.walk`), not `glob(root/*.md) + glob(root/runs/*/*.md)`. A projection or a shadow Coaching_History file hidden in a nested subdir (`drafts/ch3/notes.md`, `runs/r2/artifacts/x.md`) must not escape — and `delete` + the H6 recompute reach the same depths. Likewise the **sidecar walk (v) is depth-complete**: the `coaching*`-key check, the `coaching_history_seq`-value-must-be-int check, and the string-value shadow scan all recurse to every depth, and a `coaching_history_seq` at any **non-home** depth (its only legitimate homes are top-level and `execution.*`) is itself flagged as a shadow.

A **bare boundary-guarded `CH-NN` token** elsewhere is **WARN** (ERROR `--strict`; override `<!-- override: coaching-residue <token> — <why> -->`), because a bare token false-positives on chapter shorthand ("CH-12"). The unambiguous signatures (i)–(v) stay non-overridable. The boundary guard (`(?<![\w-])CH-[0-9]{2,}(?![\w-])`, the `FID_RE` style) already excludes a real `F-CH-01` finding id.

### H6 + `delete` — deletion honored, recomputed not trusted (Fable condition b: the record is the writer's)

One command honors the deletion: **`coaching_history.py delete <project_root>`** (or `validate.sh coaching-history delete <project_root>`) — (1) removes every `*_Coaching_History_*.md` from the root **and all subdirs** (recursive); (2) drops `coaching_history_seq` from the sidecar **at every depth** (recursive strip, not just the top-level + `execution.*` homes — Codex round-1 P2); (3) flips the `Diagnostic_State.md` consent marker to `<!-- coaching-history: deleted -->`. **Deletion revokes consent:** the tombstone reads as NOT opted-in; regeneration requires the writer's explicit fresh opt-in, never a silent re-derivation from the still-present disposition records.

Under the tombstone the validator **recomputes deletion from artifacts** rather than trusting the marker (the PR #161 recorded-field rule, `disposition_check` DP2.6, [`disposition-supersedence-recompute.md`](disposition-supersedence-recompute.md)): the full H5 scan must come up empty **and** no `*_Coaching_History_*.md` may survive (at any depth) **and** the sidecar must carry no `coaching_history_seq` **anywhere** (a **depth-complete recursive search**, Codex round-1 P2 — a seq nested under a non-home key had survived the naive two-home strip and the recompute falsely reported "deletion honored"; the recompute's completeness *is* the guarantee, never a trust that `delete` cleaned the known homes). Any residue = **ERROR with no override accepted** (deletion honoring grants no override relief — the laundering-firewall posture). `opted-in` and `deleted` both present = ERROR (contradictory consent state).

The architectural coupling that makes deletion tractable: H5's **always-on projection ban** means observations only ever live in the one deletable artifact, so deleting it is **complete by construction** — and H6 re-verifies anyway.

## Opt-in — consent, discoverable before the artifact exists

The whole artifact is produced only under `<!-- coaching-history: opted-in -->` (the `content_advisory._OPT_IN_RE` precedent). **Marker home: `Diagnostic_State.md`** — writer-visible, and the file the coach already reads at session start, so consent is discoverable before the artifact exists; the artifact also self-carries the marker (`content_advisory` W2 style). No marker anywhere → the validator no-ops (exit 2), like `content-advisory` / `legal-risk`; a tombstone → H6 mode.

## §6a — mechanization limits (stated per the verdict's honesty bar)

H5/H6 guarantee both Fable conditions over **all persisted state**: any tool-written projection necessarily carries the block carrier, schema-id, or evidence grammar (the tool only ever emits observations in that grammar), so it is mechanically caught; the sidecar walk closes the machine-facing channel; the recompute closes the trusted-marker channel. Two residuals terminate in the skill contract, not a validator (the layered-mechanism-plus-human-terminus posture):

1. **In-session ephemeral reasoning.** A live coach session could hold a process observation in conversation without persisting it; no validator scans a conversation. The skill contract (§9) requires the coach to source observations ONLY from the artifact and forbids deriving fresh cross-session patterns outside the opted-in artifact path.
2. **Token-stripped paraphrase.** An observation hand-paraphrased into another artifact with every mechanical token stripped is lexically undetectable. The skill contract forbids projecting observations into any other artifact in any form; H5's WARN-tier bare-token scan catches the careless case; the deliberate case is a contract violation a lexicon cannot police (same class as H3's documented trait-attribution limit and H7's tentative-framing floor).

**Deletion scope, stated plainly:** `delete` removes the observation **layer** and revokes re-derivation consent. The underlying `finding_disposition` records are the project's pre-existing editorial ledger (workflow decisions about findings, not process observations about the writer) and are **not** rewritten — deletion of the coaching record does not falsify editorial history. Git history / backups are the writer's own custody (the surface is local-only, W1).

## The transference-health rule (the presentation is load-bearing)

The count is the coach's **private evidence**; what reaches the writer is the coach's **noticing**, in the coach's voice — never a standalone tally the writer confronts alone. Derive from counts (for the anti-stereotyping honesty), but never *present* as a count/score. Two properties the rendered observation must have: **confident about what was observed** (the count is real attention, stated as such — not hedged into mush) and **tentative about what it means** (the interpretation is handed to the writer as an open question, never asserted as a trait or verdict). The enforceable floor is mechanized (H4 no-severity/no-finding; H7 no-trait-verdict, no-scoreboard, invitation-present); the full voice is the skill-contract obligation. The ledger must **serve** the coaching relationship (the coach's continuity of attention), never **become** it (a scoreboard the writer performs to).

## Files

- `plugins/apodictic/schemas/apodictic.coaching_observation.v1.schema.json` (+ its `_coverage.json` binding row, `closed_keys:true`).
- `scripts/coaching_history.py` + the byte-identical mirror `plugins/apodictic/scripts/coaching_history.py` (`check-mirror`); `validate.sh coaching-history` arm + `AGG_VALIDATORS` + `Commands:` + `--check-all`.
- `plugins/apodictic/skills/core-editor/references/example-coaching-history/` — the canonical opted-in project (Diagnostic_State.md + sidecar + one Coaching History artifact), wired into `--check-all` under `--strict` with five hostile ethics-gate arms + a delete round-trip.
- `revision-coach/SKILL.md` §9 — the skill contract (opt-in gate, single-home / no-projection, read-by-id, tentative-framing, surface-the-delete).
