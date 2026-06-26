<!-- synthesis-argument.md — Fragment extracted from run-synthesis.md §Step 8, paragraph on Argument-DE class.
     Canonical home for the Argument-DE parallel decision-layer schema.
     Loaded by the nonfiction-argument-engine skill at synthesis time.
     Source paragraph is marked replaced-with-include in run-synthesis.md §Step 8. -->

# Synthesis — Argument-DE Class Fragment

*This fragment contains the Argument-DE class paragraph from `run-synthesis.md §Step 8`. It defines
the parallel decision-layer schema for argument-shaped editorial letters. The `decision-layer-check`
validator already accepts argument-DE markers (implemented prior to this extraction); this fragment
makes the schema discoverable and owned by the nonfiction-argument-engine skill.*

---

## Argument-DE class (v1.8.0 calibration)

Argument-shaped letters (detected by markers: "Coalition-Partner Ground-Truth Recommendations",
"Editorial-Dispute Territory", "Argument_State", "Claim Ladder", "Argument Engine") use a parallel
decision-layer schema. The validator accepts variant heading names:

- "Coalition-Partner Ground-Truth Recommendations" **or** "Strengths / Protected Elements" → maps to Protected Elements (Check 1; 3–6 items)
- "Editorial-Dispute Territory" → maps to Author Decisions (Check 2; 3–7 list items)

The validator **skips** Check 3 (Control Questions) and Check 4 (Mandatory Appendices A/B/C) for
argument-DE class letters — argument-DE class is not held to the fiction-DE structural contract.

*Closes Phase 4 Wave 3 eval-coverage finding C3.*

### Argument-DE detection markers

The `decision-layer-check` validator detects argument-DE class when the letter body contains at least
one of:

- `"Editorial-Dispute Territory"` (heading)
- `"Argument_State"` (word)
- `"Claim Ladder"` (phrase)
- `"Argument Engine"` (phrase)
- `"Coalition-Partner Ground-Truth Recommendations"` (heading)

If none of these markers are present, the validator applies the standard fiction-DE schema (Protected
Elements / Author Decisions / Control Questions / Appendices A/B/C).

### Argument-DE decision-layer structure

**§ Strengths / Protected Elements** (3–6 items, Check 1)
Named load-bearing strengths in the argument — evidence quality, framing, strategic structural choices,
or specific subclaims the revision must not damage. Equivalent to Protected Elements in the fiction-DE
schema; the validator accepts either heading.

**§ Editorial-Dispute Territory** (3–7 list items, Check 2)
Named open editorial questions where the author's choice materially affects the argument's posture,
scope, or audience fit. Each item is a genuine choice (not a correction) — the engine presents the
trade-off and recommends a direction, but the author decides. Equivalent to Author Decisions in the
fiction-DE schema.

**Not required for argument-DE class:**
- Control Questions (Check 3) — skipped
- Mandatory Appendices A/B/C (Check 4) — skipped

The argument-DE class may include appendices (e.g., an Argument State Update, a Revision Checklist)
but these are not mechanically required by the validator.

### Override path

Override markers work the same as the fiction-DE schema:
- `<!-- override: decision-layer-protected-elements -->` — in letter body, deviates from 3–6 count
- `<!-- override: decision-layer-author-decisions -->` — in letter body, deviates from 3–7 count

Markers in appendix bodies are non-canonical (synthesis body is canonical; appendices hold evidence).

### Validator source reference

The `decision-layer-check` validator implementation: `scripts/letter_checks.py` — `_ARGUMENT_DE_RE`,
`decision_layer_check()`, `_count_decision_entries()`.
