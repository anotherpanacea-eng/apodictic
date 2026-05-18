# Specialized Audit: Idiolect Preservation List
## Version 1.0
*Last Updated: May 2026*

---

## Purpose

Surface the words and collocations that are unusually characteristic of the writer's prose against a reference corpus — and produce a **preservation list** that downstream revision work treats as "do not normalize."

The diagnostic answers a narrow, useful question: which moves are *signature* and which are *habit*? Line-editing passes (whether human, copyedit, or AI-assisted) routinely flatten exactly the words and phrases that distinguish a writer's voice. The preservation list intercepts that flattening before it happens.

**This audit is voice preservation, not provenance detection.** It does not flag prose as AI-generated or human-written. It does not adjudicate whether a given recurrence is convergence (a problem) or signature (a feature) — that judgment requires source context the audit cannot supply. It surfaces keyness-distinctive material with the auditor's and author's judgment in the loop.

**Substrate.** Shim `scripts/ai_prose_idiolect_detector.py` → SETEC `idiolect_detector.py`. Requires SETEC ≥ 1.86.0. See `ai-prose-calibration-distributional.md §Computing the Signals` for the discovery contract and JSON envelope.

---

## When to Activate

- **Default for `apodictic-coach`.** When a revision session plan is being built, run this audit on the writer's prior work (or on the manuscript itself if no separate baseline corpus exists) so the coach can show the preservation list before the writer starts cutting. Goal: prevent revision from sanding off the moves the writer is actually known for.
- **After AIC-7 (Discourse Leak) Lexical Convergence fires in AI-Prose Calibration.** The Lexical Convergence subtype flags words the writer is using too often relative to context. The idiolect preservation list flags words the writer is using *characteristically* relative to a reference. Cross-reference: a word on both lists is a hard case; a word on the idiolect list but not the convergence list is signature, full stop.
- **Before a heavy copyedit pass.** Hand the preservation list to a human copyeditor (or attach it to the system prompt of an AI line-edit pass) as a "do not change without asking" register.
- **When the writer reports "my editor flattened me."** The list gives concrete evidence of what's at stake.

## When NOT to Activate

- **No reference corpus available.** The audit's signal depends on contrast with a reference. SETEC accepts `--reference-corpus brown` for a generic English fallback, but the preservation list is most useful when the reference is the writer's *register* (e.g., contemporary literary fiction) — Brown English will surface a different and less editorially useful set of keyness candidates.
- **Manuscript-level voice diagnosis is the goal.** This audit is feature-level (words, collocations); for register-level diagnosis use `ai_prose_voice_distance` (distance from baseline) or `ai_prose_voice_profile` (the baseline itself).

---

## Inputs

The shim forwards CLI arguments verbatim to SETEC. The required inputs:

- **Target.** Either `--target-dir DIR` (a directory of `.txt` / `.md` files) or `--manifest MANIFEST` (a JSONL corpus manifest with an optional `--filter FILTER` selector).
- **Reference.** One of:
  - `--reference-dir DIR` — a baseline corpus directory.
  - `--reference-manifest MANIFEST` — a JSONL manifest, optionally filtered.
  - `--reference-corpus brown` — built-in generic English fallback (lowest editorial signal; use when no register-matched reference is available).
- **Keyness method.** `--keyness-method {log_likelihood, chi_square, pmi, fisher_exact}` (default log_likelihood). Log-likelihood is the standard for corpus keyness; PMI surfaces low-frequency idiosyncrasies more aggressively.
- **N-gram sizes.** Default 1, 2, 3. Most of the preservation-list value is in bigrams and trigrams; unigram keyness frequently surfaces topical nouns rather than voice moves.
- **Preservation output.** `--preservation-output PATH` writes the preservation list as JSON to PATH. `--preservation-quotas A,B,C` controls how many candidates per n-gram size (default 20,20,10).
- **Collocation filter.** `--min-collocation-lr` / `--min-collocation-pmi` / `--no-collocation-filter` shape how aggressively multiword candidates are pruned.

Privacy note: idiolect output is voice-cloning input. SETEC enforces a default-private output policy — outputs that would land outside an `ai-prose-baselines-private/` directory are refused unless `--allow-public-output` is passed (override only for non-personal corpora like Federalist).

---

## Interpreting the Output

### JSON envelope (schema_version 1.0)

The audit emits the canonical SETEC envelope. The relevant blocks:

- **`results`** — keyness tables per n-gram (`unigrams`, `bigrams`, `trigrams`), each with the keyness score, target count, reference count, and a `preservation` flag. Collocations carry log-likelihood + PMI scores.
- **`results.preservation`** (when `--preservation-output` was passed) — the curated "do not normalize" list. This is the operative artifact for revision work.
- **`baseline`** — corpus metadata for the reference (`n_files`, `words`, optional `register` / `split`).
- **`claim_license`** — licenses the use ("voice preservation; not provenance detection"); explicitly does NOT license "this manuscript was written by writer X" or "this passage is in-voice."

### The auditor's three reads

For each candidate on the preservation list:

1. **Is this a topical anchor?** A character's name, a recurring setting, a thematic noun. These are preserved by definition — don't flag them, don't analyze them, don't cut them.
2. **Is this a signature move?** A phrase, sentence shape, or syntactic habit the writer reaches for repeatedly across registers (literary fiction *and* essays, dialogue *and* narration). Mark for preservation; revision should pause before touching it.
3. **Is this a habit the writer would want to know about?** A tic that may be earned or unearned. The audit does not adjudicate; the author and editor do. Surface it; let the author decide.

These three categories are not mutually exclusive. The preservation list is a starting point for conversation, not a verdict.

### Cross-references

- **AIC-7 Lexical Convergence (AI-Prose Calibration).** A word that appears on BOTH the idiolect list AND the convergence flag is the hard case: the writer uses it characteristically, AND it appears across contexts where a human writer would normally differentiate. Treat as the writer's call after seeing both signals. Don't pre-empt with a Recast.
- **Voice Distance (`ai_prose_voice_distance`).** When voice distance shows a draft has drifted from baseline, the idiolect preservation list shows which specific features carry the writer's voice — useful for targeted restoration rather than blanket "rewrite in voice."

---

## Output Conventions for Revision Coaching

When `apodictic-coach` integrates the preservation list into a session plan, the recommended presentation:

```
**Signature moves to preserve through this revision:**

Bigrams: [3-5 highest-keyness items]
Trigrams: [3-5 highest-keyness items]
Single-word habits: [3-5 highest-keyness items]

These showed up in your prior work at rates an English baseline would not predict. If a revision pass (yours, an editor's, or an AI line-edit's) wants to change any of them, that's a conversation — not an automatic accept.
```

The list is presentational, not prescriptive: the author decides what to keep. The coach's job is to make the cost of accidental flattening *visible* before the revision starts.

---

## Severity / Readiness Impact

The idiolect preservation list does not produce severity findings. It is an *advisory* artifact, not a diagnostic that gates submission readiness.

When integrated with AIC-7 Lexical Convergence findings, the cross-reference can MODIFY a Convergence severity: a Convergence flag on a word that the idiolect detector also surfaces as signature should be source-triaged (Step 5 of AI-Prose Calibration) before a Recast call is made. This is a guardrail against the audit fix-flattening the very voice the writer is asking the audit to protect.

---

## Output Ordering

```
1. Pass-Linked Symptom Summary (per-passage if drawn from upstream flag; otherwise corpus-level)
2. Preservation list (top-N by n-gram size; each item with keyness score and brief context)
3. Author-facing reads (topical anchor / signature move / habit-worth-knowing) — only if the auditor has surveyed the list
4. Cross-references (AIC-7, Voice Distance) — only if those audits have run
```

No "synthesis translation" block: this audit doesn't fire severities.

---

## Firewall Compliance

This audit:
- Does NOT generate replacement prose.
- Does NOT recommend specific edits to flagged or preserved items.
- Does NOT adjudicate which entries on the list are signature vs. habit.
- Does NOT publish the preservation list outside the project (default-private output policy).

The audit produces *data* the author and editor use to make revision calls. The conversation that follows is the work; the list is the precondition.
