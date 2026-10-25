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

Open the letter by naming the rubric actually applied: `register=asserted` or
writer-confirmed `register=generative`, plus any active high-stakes gate. For a mixed-
register ledger, cluster findings by mechanism and explicitly separate journey findings
from asserted cash-out findings; never make the author reverse-engineer why two similar
flags received different Triage treatment.

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

## Prerequisite blind spots

*Moved from `run-synthesis.md` Step 3 and Appendix A.*

When a run is argument-shaped (constraint=nonfiction + persuasive-argument form per `pass-dependencies.md §4a`) AND Field Reconnaissance was not run — whether because the user declined the Hard Prerequisite or Auto-recommend before synthesis invocation, the user opted out at intake, or the run pre-dates the prerequisite policy — the synthesis layer MUST record "literature-counterevidence not surveyed" as a confidence-limiting blind spot in this Absence Inventory and carry it forward to Appendix A (Diagnostic Detail). The disclosure must name what is unsurveyed (competing studies, counter-citations, replication failures, opposing scholarly positions) and what the absence implies for synthesis confidence (Dialectical Clarity, Argument Red Team, and Argument Evidence Deep-Dive operated against a manuscript-internal claim graph rather than a literature-aware one). This disclosure is not optional for argument-shaped runs without Field Recon coverage; the §4c Auto-recommend before synthesis decline policy treats it as the canonical confidence limiter for this audit-class. For Pre-DE Prerequisite Citation Verifier declines on high-stakes argument-shaped runs, additionally name "citation provenance not verified" as the parallel confidence limit. Fiction runs and non-argument nonfiction runs do not require this disclosure (Field Recon is not prerequisited for those forms; absence is not a blind spot).

**Appendix A.** name "literature-counterevidence not surveyed" as a blind spot and state the implication (the argument engine operated against a manuscript-internal claim graph; competing studies / counter-citations / replication failures / opposing scholarly positions in the literature were not surfaced; synthesis confidence on counterevidence completeness is bounded). For high-stakes argument-shaped runs without Pre-DE Citation Verifier coverage, additionally name "citation provenance not verified" with the same disclosure pattern.
