# Findings Ledger — Entry Format

*Reference file for the APODICTIC Development Editor. Loaded when writing or validating per-pass ledger entries. Holds the ledger entry template and the Structured Findings Block, extracted from `run-core.md` §Findings Ledger Protocol. The protocol purpose, when-to-write rule, consolidation requirement, and Ledger Discipline remain in `run-core.md`.*

---

#### Ledger Entry Format

Each pass appends a section using this structure:

```markdown
---

## Pass [N]: [Name] — Ledger Entry

### Notable Findings

[Numbered list. Each entry: one sentence stating the finding, one sentence
stating why it matters for the editorial letter, a pointer to the
specific location in the pass artifact, and optionally, the best case
against the finding.]

1. **[Finding name].** [What it is.] [Why it matters.]
   *(See Pass N, §[Section], [table/paragraph name].)*
   *Counterevidence:* [Optional. The strongest case that this finding is
   wrong, overstated, or explained by authorial intent. Omit if no
   plausible countercase exists. When present, helps synthesis calibrate
   severity and prevents the ledger from reading as a list of assertions.]

### Data Artifacts for Letter Reference

[List of tables, inventories, matrices, or other structured data in the
pass artifact that the editorial letter should direct the author to.
One sentence per artifact describing what it shows and why it's useful
for revision.]

- **[Artifact name]** — [What it shows, in one sentence.]
  *(Pass N, §[Section].)*

### Cross-Pass Connections

[Findings from this pass that connect to earlier ledger entries. These
are pre-built hypotheses about shared root causes — the synthesis step
evaluates them. Format: what this pass found, what it connects to,
and why the connection matters.]

- [Connection description.]
  *(Connects to: Pass M, Finding N.)*

### Unresolved Questions

[Observations this pass surfaced but couldn't fully analyze within its
scope. These may become stress test material, deferred audit triggers,
or items for the "Additional Observations" section of the editorial
letter.]

- [Question.]

### Audit Triggers

[Migrated here from pass artifact. The pass artifact retains its own
audit triggers section for standalone readability, but the ledger
consolidates them for the synthesis step.]

| Trigger | Evidence | Recommendation |
|---------|----------|----------------|
```

#### Structured Findings Block (`apodictic.finding.v1` — required for synthesis-bound findings)

Each Notable Finding that propagates to synthesis (any Must-Fix or Should-Fix) **must** carry a structured block after its prose. The block is a machine-parseable *index* — the prose stays primary and author-facing; the block lets the synthesis step and `scripts/validate.sh structured-findings` integrate findings across independently-run passes without re-parsing prose. Purely local Could-Fix observations may omit it.

The block is **real JSON** inside an HTML comment, validated by a real parser (`scripts/structured_findings.py`) — not shell regex on colon-lines. `severity` and `confidence` use the canonical tokens (`output-policy.md §Canonical Severity Scale` / §Confidence Calibration):

```markdown
1. **[Finding name].** [What it is.] [Why it matters.]
   *(See Pass N, §[Section], [table/paragraph name].)*
   *Counterevidence:* [If applicable.]

   <!-- apodictic:finding
   {
     "schema": "apodictic.finding.v1",
     "id": "F-P4-01",
     "mechanism": "One sentence: the craft mechanism that produces the problem",
     "severity": "Must-Fix",
     "confidence": "HIGH",
     "evidence_refs": ["Pass 4 §Scene Turns", "Ch. 12"],
     "fix_class": "redistribute dramatic weight",
     "risk_if_fixed": "What the fix might harm"
   }
   -->
```

**Fields (all required):** `schema` (pinned `apodictic.finding.v1`), **`id`** (Finding Lifecycle ID — `F-<ORIGIN>-<NN>`, e.g. `F-P5-01` / `F-DP-02`; unique per run), `mechanism`, `severity` (Must-Fix | Should-Fix | Could-Fix), `confidence` (HIGH | MEDIUM | LOW | UNCERTAIN), `evidence_refs` (non-empty array), `fix_class`, `risk_if_fixed`. The field set is canonical in `plugins/apodictic/schemas/apodictic.finding.v1.schema.json` (validated by `scripts/apodictic_artifacts.py`), not in this prose.

**Usage rules:**
- The prose finding is canonical. If the block and prose diverge, the prose governs — fix the block.
- `mechanism` is the highest-value field: two findings from different passes naming the same mechanism are a root-cause-cluster candidate for synthesis.
- The block is versioned via `schema`. If the field set changes, bump the version (`apodictic.finding.v2`); the validator keys off the `schema` value.
- **Finding Lifecycle ID (`id`).** Assign once at finding creation as `F-<ORIGIN>-<NN>` (ORIGIN = pass/audit code; NN = zero-padded sequence within that origin) — e.g. `F-P5-01`, `F-DP-02`. The ID is durable and unique per run, and follows the finding through its whole lifecycle: pass output → this ledger block → the **Deficit Lock** → the **editorial letter** (cited in an HTML comment near the delivered finding and in the Severity Calibration appendix — never in author-facing prose) → the **revision plan / coaching** (where a confirmed-resolved finding advances to `finding_states[id] = "revised"`, the third lifecycle state). This lets `softness-check` / `deficit-lock` match a locked finding to its delivery **by ID (exact)** instead of prose heuristics. `scripts/validate.sh structured-findings` checks ID presence, format, and per-run uniqueness; `scripts/validate.sh finding-trace <run_folder>` traces the ID *across* artifacts — every ID cited in the letter (and in revision plans) resolves to a ledger finding, `execution.finding_states` keys are real ledger IDs, and a `revised` state is reconciled against the completed-revision artifacts (referential integrity + sidecar lifecycle coherence; see `docs/finding-lifecycle-ids.md`).

#### When to populate `evidence_quote` (optional — the Annotated-Manuscript quote rung)

`apodictic.finding.v1` carries an **optional** `evidence_quote` field. When present and valid it lets the [Annotated-Manuscript deliverable](annotated-manuscript.md) anchor a finding's margin note to the **exact sentence** (the finest `quote` rung) instead of the chapter; when absent the note anchors by `evidence_refs` (line/chapter/document), exactly as before. It is **demand-gated and adopted per pass** — today only **Pass 5 (Character Audit)** populates it (its findings are the most sentence-precise of the Core baseline). No finding is ever forced to carry one.

- **Sentence-precision criterion.** Populate `evidence_quote` **only** when the finding is about a specific line or exchange (a flat-affect beat, a telling-not-showing sentence, a continuity seam at a named line). A finding about a whole chapter or arc **omits** it — the anchor degrades to the chapter/line rung, which is correct, not a loss.
- **Firewall — copy, never author.** The value is **manuscript bytes copied verbatim** from the span the finding cites; the system never composes one. This is enforced *by identity* downstream: the **A6** gate requires the quote to occur in the manuscript snapshot **verbatim and exactly once**, so a non-verbatim, non-unique, or fabricated quote fails the gate (or degrades before it) and never reaches the margin. The quote is provenance used to *locate* the note; the margin comment itself is the fixed finding-field template, never the quoted text.
- **Located by its own bytes, not by `evidence_refs`.** The note anchors at the snapshot's unique occurrence of the quoted span, independent of the finding's `evidence_refs` locus (the quote rung is finest, so it wins). Copy the span you actually mean the note to sit on — not a sentence from elsewhere that merely matches the cited chapter.
- **Single line only.** `evidence_quote` must contain no `\n` or `\r`. A multi-line span (e.g. a two-line dialogue exchange) or an empty string is **silently degraded** by `annotation_manifest build` to the non-quote ladder — so don't waste the field on one: pick the single most diagnostic line, or omit.

```markdown
   <!-- apodictic:finding
   {
     "schema": "apodictic.finding.v1",
     "id": "F-P5-01",
     "mechanism": "Protagonist states feeling instead of enacting it — flat affect at the turn",
     "severity": "Should-Fix",
     "confidence": "HIGH",
     "evidence_refs": ["Ch. 7"],
     "evidence_quote": "\"I am very angry,\" she said calmly.",
     "fix_class": "dramatize through action/subtext",
     "risk_if_fixed": "May slow the scene's pace"
   }
   -->
```

A companion arc-level finding (e.g. "the protagonist's want never sharpens across Acts II–III") correctly **omits** `evidence_quote` and anchors at its `evidence_refs` chapter. The field is canonical (optional) in `apodictic.finding.v1.schema.json`; populating it requires **no** schema change.

#### Companion structured blocks (same envelope)

The same `<!-- apodictic:<type> { ... } -->` envelope carries two companion record types, validated by the same helper:

- **`apodictic.audit_trigger.v1`** — for the Audit Triggers section. Fields: `schema`, `audit` (use the registry name in `audit-routing-table.md` where applicable), `evidence`, `recommendation` (run | recommend | defer).
- **`apodictic.readiness.v1`** — for readiness verdicts (Pass 11 / submission readiness). Fields: `schema`, `dimension`, `verdict`, `rationale`.

The **ledger entry** as a whole has no separate JSON wrapper: its structured representation is the set of finding / audit-trigger blocks it contains, mirrored into the `findings[]` / `audit_triggers[]` / `readiness[]` arrays of `Diagnostic_State.meta.json` (where `findings[]` severities must tally to `triage_summary`). This pairs the artifact with a mechanical validator per the Pass-10-Class discipline.

---
