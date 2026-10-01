# Specialized Audit: Punctuation Cadence
## Version 1.0
*Last Updated: May 2026*

---

## Purpose

Diagnose punctuation-rhythm regularization — the kind that AI editing and professional copyediting routinely impose **before** they erase vocabulary. Sentence-final distribution flattens, dash density compresses, parenthetical asides disappear, comma usage standardizes. By the time a lexical-diversity signal (MATTR / MTLD) fires, the punctuation cadence has already shifted.

This is the audit that catches "smoothing that happened in the line edit, not in the draft." It also catches its inverse: writers who never had idiosyncratic punctuation in the first place, where the cadence read as regularized natively.

**Subsumes the territory of the standalone em-dash-reduction skill.** Em-dash density is one signal of six; the audit also reads sentence-final distribution, semicolon usage, parenthetical interruption rate, ellipsis frequency, and punctuation bigrams (adjacent-mark pairs like `,—` or `;-`). Use this audit instead of em-dash-reduction when:

- The writer's full punctuation rhythm matters, not just dash count.
- A baseline is available (the audit gains z-scoring against the writer's own register).
- Multiple punctuation marks are suspected of compression simultaneously.

The em-dash-reduction skill remains useful as a one-mark line tool when the cadence diagnostic isn't needed.

**Substrate.** Shim `scripts/ai_prose_punctuation_cadence.py` → SETEC `punctuation_cadence_audit.py`. Requires SETEC ≥ 1.86.0. See `ai-prose-calibration-distributional.md §Computing the Signals` for the discovery contract and JSON envelope.

---

## When to Activate

- **As a follow-up to AI-Prose Calibration Layer A.** When the variance audit shows lexical compression but the writer wants to know *what* specifically is regularized, this audit names it at the punctuation layer.
- **When the writer reports "the line edit changed something but I can't say what."** This audit translates a vague unease into a list of specific cadence shifts.
- **Before accepting a heavy copyedit.** Run the audit on the marked-up draft against the writer's baseline; surface whatever moved.
- **As a quick scope check on AI-revised prose.** Punctuation cadence is among the earliest signals to fire on AI-edited text, so the audit doubles as a triage tool when AI involvement is suspected but unconfirmed.

## When NOT to Activate

- **No baseline available, and the writer's own punctuation rhythm is unknown.** Without `--baseline-dir`, the audit produces heuristic-tier output (regularization bands against literature priors). Useful but narrower; the personal-baseline z-score is where this signal becomes editorially precise.
- **Manuscript is below ~2000 words.** Punctuation cadence is a distributional signal; small samples produce noisy diagnoses. The audit warns when input is too short, but the warning is the answer: don't act on it.
- **Pre-revision draft.** This audit catches regularization. On a first-draft fresh from the writer's hand, it has nothing to catch except the writer's natural rhythm — which is presumed not to need diagnosis.

---

## Signals Computed

The audit produces:

- **Per-mark density (per 1,000 words):** comma, semicolon, colon, em-dash / en-dash pair, parenthesis-pair, ellipsis, quotation-pair, exclamation, question.
- **Sentence-final distribution:** period vs. question vs. exclamation as fractions of sentence-final marks. AI editing and house-style copyediting both tend to push toward a high period share.
- **Interruption grammar:** rate of mid-sentence asides (parenthetical insertions, em-dash interruptions, comma-bounded appositives). The interruption rate is one of the punctuation properties most reliably flattened in editing passes.
- **Punctuation bigrams:** pairs of adjacent punctuation marks within the same sentence (e.g., `,—`, `;-`, `):`, `,"`, `?"`). Captures multi-clause concession and nested interruption — moves that distinguish a writer's voice from a regularized text.
- **Compression-fraction band:** an aggregate call (Lightly / Moderately / Heavily regularized) across the six rhythm signals.
- **Baseline comparison (when `--baseline-dir` is supplied):** per-signal z-scores plus a Manhattan distance over normalized punctuation distributions.

---

## Interpreting the Output

### JSON envelope (schema_version 1.0)

Read `results` for the per-mark densities and `results.compression` for the band call. When a baseline was supplied, the `results.baseline_comparison` block carries z-scores and the aggregate Manhattan distance.

The `claim_license` block licenses regularization diagnosis against the supplied comparison set. It does NOT license:

- "This manuscript was edited by AI." (Punctuation regularization can come from any house-style copyedit.)
- "This is the writer's natural rhythm." (Without a personal baseline, the diagnosis is heuristic against literature priors.)

### Bands

- **Lightly regularized.** One or two signals compressed against baseline (typically dash density or interruption rate). Likely a targeted copyedit; cadence largely intact. Restoration scope: spot fixes on the named signals.
- **Moderately regularized.** Three or four signals compressed. Sentence-final distribution often included. Indicates a substantive line edit (human or AI). Restoration scope: review the edit-marks against the baseline cadence before accepting.
- **Heavily regularized.** Five or six signals compressed. The text reads in punctuation-house-style, which is fine as a deliberate choice but usually isn't — the writer often didn't intend it. Restoration scope: consider whether the line-edit pass overshot.

### Cross-references

- **AI-Prose Calibration AIC-3 (Echo Stack).** Structural repetition at the sentence/paragraph level often co-occurs with punctuation regularization. When both fire, the prose has lost both rhythmic *and* structural variation; treat as a compound finding.
- **AI-Prose Calibration Layer A (`ai_prose_variance_audit`).** Sentence-length variance and burstiness are the closest analogues. Punctuation cadence regularization often *precedes* variance compression in the editing timeline, so it can fire before Layer A does.
- **Voice Distance (`ai_prose_voice_distance`).** Burrows Delta against baseline includes punctuation features in its function-word fingerprint. Punctuation Cadence isolates the punctuation contribution; Voice Distance aggregates across stylistic dimensions.

---

## Severity / Readiness Impact

Punctuation cadence findings do not gate submission readiness on their own. The audit's value is **diagnostic precision** — naming what shifted — rather than producing a hard gate.

When Punctuation Cadence reports Heavily regularized AND AI-Prose Calibration shows AIC-1 (Generic Hand) at Pattern or higher, the compound finding suggests the line-edit pass eroded the writer's voice layer. In that case, the AI-Prose Calibration Readiness Impact Note governs; this audit's contribution is the evidence trail for *what specifically* needs restoration.

---

## Output Ordering

```
1. Pass-Linked Symptom Summary (Layer A signals from variance audit, AIC flags that fired)
2. Per-mark density table (with baseline comparison column when --baseline-dir was supplied)
3. Interruption-grammar profile (parenthetical / em-dash / appositive rates)
4. Punctuation bigram top-N (highest-divergence pairs against baseline, or top-frequency pairs without baseline)
5. Compression-fraction band call with named signals
6. Restoration scope note (which specific signals to address; not generated prose)
```

---

## Firewall Compliance

This audit:
- Does NOT rewrite passages or generate replacement punctuation.
- Does NOT recommend specific dash-to-comma swaps or similar substitutions.
- Does NOT pass judgment on which punctuation register is "correct" — the diagnosis is regularization against the writer's own baseline, not conformity to a standard.

When a copyedit needs to be revised to restore voice, this audit identifies the targets; the writer or a human copyeditor executes the revision.
