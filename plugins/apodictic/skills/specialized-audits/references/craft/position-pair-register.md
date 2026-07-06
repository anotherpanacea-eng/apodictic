# Specialized Audit: Position-Pair Register
## Version 0.1 (consumer of SETEC's `position_pair_register` surface)
*Created: July 2026*
*Status: consumer-pinning contract for SETEC's `position_pair_register` task surface (`handoff: experimental`, `calibration_status: uncalibrated`).*

---

## Purpose

Surface, from ONE long nonfiction argument-shaped work, a **register of passage PAIRS that address the same question Q** — each pair carrying a neutral interrogative `question` and both passages' verbatim loci (`{doc, start_char, end_char, quote}`), in **document order**. It answers a question no other surface reaches: *where in this work do two passages speak to the same question — so the writer can read both and decide for themselves whether they conflict, evolved, or were mischaracterized?*

**This is the fleet's deliberate NON-step across the content-verdict wall.** The surface never asserts a relation between the two passages — not agreement, not conflict, not contradiction, not tension — and it does not rank pairs by disagreement. It points at two passages sharing a question; the **human reads both and owns 100% of the conflict call.** APODICTIC presents the register and adds no severity, disposition, or finding of its own (`disposition: pre_flag` posture). Where ArgScope's consumer derives an editorial signal mechanically from structural counts, this consumer derives **nothing** — it runs gates only, and the human derives everything. That makes the register **more conservative** than ArgScope, not parallel to it.

Like every audit in this framework, this is **not a provenance detector**, **not a soundness verdict**, and **not a claim about which passage is right**. It is a pointer, evidence-bound and relation-free.

---

## Relationship to the argument-shaped-nonfiction family

| Audit | SETEC surface(s) | Measures | Question |
|---|---|---|---|
| **Worldbuilding-Bible / Continuity-Bible** | (`world_fact.v1` / `canon_fact.v1`) | *Fact* contradictions — place/entity/timeline collisions; a fixed world-rule contradicting itself | Does the work break its own established facts? |
| **Dialectical Clarity / Warrant Gap / Banister** | (APODICTIC-native) | *Soundness* — warrants, burden of proof, concession cost | Does **one** argument **hold**? |
| **Argument-Decision (ArgScope)** | `argument_decision_audit` | *Structure* — B1 role-arc + B2 discourse-mode vs. paper means | How is the argument **built**? |
| **Position-Pair Register (this audit)** | `position_pair_register` | *Pointer* — passage pairs addressing the same question Q, relation-free | Where do two passages speak to the same question — **you** read both and decide |

The register is **not** a substitute for any of these. It does not adjudicate a single argument's soundness (dialectical clarity), does not describe how an argument is built (ArgScope), and does not detect a self-contradicting world-rule (the Continuity Bible). It fills the one gap those leave: a **cross-document, same-question pointer** for a stated position across a whole work, where the writer — not the model — makes every call about the relationship.

---

## When to activate

- A long nonfiction argument-shaped work (op-ed / policy brief / testimony / academic argument) where the writer wants a map of where the work returns to the same question, to check for themselves whether a stated position drifts, evolves, or is mischaracterized across the work.
- After a full development edit, as a targeted read-along index the writer can use to re-read their own positions in pairs.

## When NOT to activate

- **You want a verdict that two passages conflict.** The surface refuses it by construction — the human owns that call.
- **Fiction, or a narrator/character's beliefs.** v1 is the **nonfiction-argument register only** — a fiction arc can license a stated change, making false positives severe. Declared in the `claim_license` (F10(d)) and out of scope.
- **A clean-bill-of-health reading.** The register is NOT exhaustive: the absence of a pair is not evidence of consistency.
- **No LLM judge / label manifest.** The same-question pairing comes from a pluggable judge; without one (or a `--judge manifest`) there is nothing to surface.

---

## SETEC delegation

This audit owns no computation. It consumes SETEC Voiceprint's `position_pair_register` task surface through a thin shim and re-verifies + renders the JSON envelope against this contract.

- **Shim:** `scripts/ai_prose_position_pair_register.py` → SETEC `position_pair_register.py`. All CLI arguments forward unchanged; pass `--help` for SETEC's full surface (judge backend — `manifest` / `mock` / `anthropic` / `openai` / `gemini` / `agent_host` — plus `--judge-manifest` / `--judge-model` and the pair caps `--cap-per-question` / `--cap-per-work`).
- **Version floor:** SETEC plugin-version **≥ 1.121.0** — read from the surface's `min_setec_version` in SETEC's capabilities manifest, not hardcoded. 1.121.0 is the plugin-version at which the surface shipped, and the first release tag carrying it is `v1.121.0` (the first-tag convention, mirroring ArgScope's 1.116.0). The floor is **enforced by SETEC's normalized dispatcher at runtime (R2)**: an out-of-floor SETEC comes back as an R3 `version_floor` error envelope (`available: false`, naming the required minimum), not a missing-script error. The consumer runs **no** redundant `resolve_floor` pre-check; `resolve_floor` + the vendored manifest are the offline drift gate and capability introspection only.
- **Calibration status:** `uncalibrated`. An LLM extraction surface is not bit-deterministic; there is **no run-to-run determinism guarantee for live backends** (CI determinism rides the mock/manifest backend, deterministic by construction). Human re-review absorbs the drift — the whole design assumes it.
- **Handoff:** `experimental`. The envelope shape and the `target` / `results` / `claim_license` block are committed; the judge-prompt pipeline and pair-selection heuristics may evolve before v0.2. APODICTIC pins the `results.pairs` array + the refusal/cap disclosures and the `claim_license`; it never pins a verdict, a relation, or an aggregate (there is no aggregate for this surface, by design).

### The envelope (schema_version 1.0)

The surface emits the same top-level envelope APODICTIC already parses (`available`, `claim_license`, `claim_license_rendered`, `results`, `schema_version`, `target`, `task_surface`, …). The load-bearing keys inside `results`:

```jsonc
"results": {
  "calibration_status": "uncalibrated",
  "pairs": [                                  // THE payload — in DOCUMENT ORDER
    { "question": "What is the author's position on carbon pricing?",
      "a": { "doc": "target", "start_char": 0,   "end_char": 85,  "quote": "…" },
      "b": { "doc": "target", "start_char": 170, "end_char": 253, "quote": "…" } },
    …
  ],
  "pairs_refused_q_gate": 0,                   // DISCLOSURE — pairs whose Q failed the producer's F4 gate
  "pairs_refused_q_gate_reasons": [ … ],       // each rejected question + reason (echoed for audit)
  "pairs_dropped_cap": 0,                      // DISCLOSURE — pairs over the per-question/per-work cap
  "pairs_dropped_cap_loci": [ … ],             // the dropped loci (document-order truncation)
  "caps": { "per_question": 12, "per_work": 60 },
  "judge": { "judge_identity": { "kind": "mock" } },
  "prompt_fingerprint_sha256": "…",
  "run_timestamp_utc": "…"
}
```

There is **no relation key anywhere** — no `stance`, `tension`, `conflict`, `polarity`, `verdict`, `label`, `score`. That is enforced at the producer (a runtime banned-key gate) AND re-checked at the consumer (Q1 below).

### `claim_license` fields to surface

Bound every presentation by the envelope's `claim_license` block. Surface, at minimum:

- `licenses` — a same-question pointer, relation-free, verbatim loci, document order. *Only* the observation that two passages speak to the same question.
- `does_not_license` — **load-bearing; quote it.** Four refusals (F10): (a) does NOT license that the passages ARE in conflict; (b) does NOT license which is correct; (c) NOT exhaustive — absence of a pair is not consistency; (d) does NOT license fiction/narrator application (v1 register scope). Plus the honest downgrade: the producer's Q-string gate is **syntax only** — zero protection against a loaded/presuppositional question; the human terminus is the guarantee.
- `comparison_set.judge_kind` / `judge_model` / `prompt_fingerprint_sha256` — provenance + cross-run parity. `mock` is a test stub (infer nothing); `manifest` is only as good as its labels.
- `additional_caveats` — the determinism caveat, the cap-is-a-disclosure note, the substring-scan over-refusal note, and the backend caveat.

---

## Consumer-side mechanical gates — the `position-pair-register` validator

APODICTIC renders the envelope to a markdown register artifact and presents it. The claims that artifact makes are **enforced mechanically** by `position_pair_gates.py` (`validate.sh position-pair-register <artifact.md> <envelope.json> <manuscript>`), the "claim-surface-asserts-it" firewall for this consumer:

- **Q1 — no-relation register.** A two-layer recursive banned-KEY walk over the parsed envelope (walk shape from PR #298's `test_envelope_carries_no_verdict_keys_recursive` in setec-voiceprint — the shape, not its key list; the stance set is net-new). (i) **RELATION keys** (`contradiction`, `contradicts`, `opposes`, `opposition`, `conflict`, `conflicting`, `tension`, `stance`, `stance_delta`, `polarity`, `agreement`, `disagreement`, `inconsistent`, `inconsistency`) — case-folded substring, never legitimate ANYWHERE (whole-envelope walk). (ii) **GENERIC verdict keys** (`verdict`, `label`, `score`, `decision`, `prediction`, `classification`, `relation`) — exact key, scoped to the `results.pairs` subtree only (a whole-envelope ban would false-ERROR on calibration/judge metadata that legitimately carries `label`/`score`). **KEYS only** — the `claim_license` VALUES legitimately contain relation words (the F10 refusals name them), so scanning values would guarantee a false ERROR. Any hit → ERROR.
- **Q2 — verbatim (drift) re-check.** Every `quote` must be a verbatim substring of the manuscript **the consumer holds** (a drift catch — the producer quoted the manuscript it saw; the consumer confirms against its copy). Match = exact substring after the **F1 punctuation-fold** on BOTH sides: NFC → curly/typographic quotes to straight → all Unicode dashes (en/em/horizontal-bar/minus) to `-` → `…` to `...` → every Zs-category space (NBSP/thin/…) to U+0020 → newline to space → whitespace-run collapse. A failed match **DROPS the pair** with an **inspectable log line** (the offending quote verbatim + its claimed locus) and a counted disclosure `pairs_dropped_quote_mismatch`; ≥1 drop **WARNs** (a drop is a disclosure, not an error — it clears by default and FAILs only under `--strict`). A fabricated or paraphrased quote can therefore never reach the human as evidence.
- **A3 / X-gate (Firewall).** The register artifact must carry no editorial severity (`Must/Should/Could-Fix`) and no `apodictic:finding` block (reusing content_advisory's `_SEVERITY_RE` and the `_has_block` parsed-block idiom). The register never diagnoses. ERROR.
- **F5 — presentation-prose gate.** The consumer's OWN framing text must carry no relation vocabulary — a case-folded substring scan (the F4 stem set incl. v5 stems: `tension`, `contradict`, `conflict`, `inconsisten`, `incompatib`, `at odds`, `versus`, ` vs `, `flip-flop`, `disagree`, `oppos`, `revers`, `undercut`, `undermin`, `counter`, `repudiat`, `recant`, `backtrack`, `diverg`, `discrepanc`, `at variance`, `square with`). The scan **exempts a `>`-blockquote line ONLY when its text (after an optional `A:`/`B:` side label) is a verbatim — punctuation-folded — substring of the manuscript**: the quotes are the author's evidence and may legitimately carry these words, but a `>` line that is NOT verbatim manuscript text is framing dressed as evidence and falls back into the scan. The exemption is verbatim-bound, never merely structural and never a per-token allowlist. ERROR.
- **Order.** The artifact presents pairs in the SAME order the envelope does. Any re-ranking is an ERROR — truncation/selection by anything but document order is a ranking channel the posture forbids. When the artifact carries no parseable `### <n>. Q:` headings, the order is **unverifiable → WARN** (never a silent skip; FAILs under `--strict`) — render with the canonical heading form.

An unreadable artifact / envelope / manuscript **fails closed** with a named error, never a false PASS.

---

## The register-artifact template

Render one register artifact per run: `[Project]_Position_Pair_Register_[runlabel].md`. **Rendering rules:**

- **Framing text — neutral, relation-free, VERBATIM.** The obvious framing ("…whether they conflict…") would trip F5's own scan (`conflict` is banned). Use this honest framing, which passes F5 by construction:

  > **These passages address the same question. Read both — the reading is yours.** This register points at two passages that speak to one question; it makes no claim about how they relate. You read both and own the entire reading.

  (Verified against the F5 banned-stem list: no `tension / contradict / conflict / inconsisten / incompatib / at odds / versus / vs / flip-flop / disagree / oppos / revers / undercut / undermin / counter / repudiat / recant / backtrack / diverg / discrepanc / at variance / square with` appears.)
- **Pairs in DOCUMENT ORDER**, one `### <n>. Q: <question>` heading per pair, matching the envelope's `pairs[]` order exactly. No re-ranking.
- **Quotes as `>` blockquotes, loci on their own plain lines.** Each side's verbatim `quote` is rendered on its own `>`-prefixed line carrying ONLY the quote text (an optional `A:`/`B:` side label is allowed; the `[start_char:end_char]` locus goes on the plain line above, as in the canonical example — never inside the blockquote, where it would break the verbatim match). A `>` line is F5-exempt only because its text IS verbatim manuscript evidence (fold-matched); never inline a quote into the framing prose, and never put framing inside a blockquote.
- **Do NOT present SETEC's `render_markdown` output as the register artifact.** The producer's `--out-md` report is a producer-side convenience whose framing legitimately names the refused relation vocabulary (and renders quotes inline) — it will trip F5 and A3-adjacent expectations by design. The consumer renders its OWN artifact per this template.
- **Disclosures section.** Surface `pairs_refused_q_gate`, `pairs_dropped_cap` (+ dropped loci), and the consumer-side `pairs_dropped_quote_mismatch` (if any) as disclosures, never as judgments.
- **No-severity / `pre_flag` posture.** The register carries no `Must/Should/Could-Fix` token, no `apodictic:finding` block, no disposition beyond `pre_flag`. A3 enforces this.

The canonical worked example lives at `references/example-position-pair-register/` (`manuscript.txt` + `envelope.json` + `Example_Position_Pair_Register_run.md`), wired into `validate.sh --check-all` under `--strict`.

---

## Anti-verdict discipline (firewall alignment)

This audit sits behind the same firewall as the rest of APODICTIC, and further from the wall than any other consumer: it **derives nothing**. It renders a relation-free pointer and runs gates; the human makes every call about the relationship between the two passages. Route any "do these conflict / which is right / is my book consistent" question back to the human — no part of this surface licenses any of them. The surface ships `uncalibrated`, `handoff: experimental`; honor that.

---

## References

- Li, Raheja & Kumar (2023). *ContraDoc: Understanding Self-Contradictions in Documents with Large Language Models.* arXiv:2311.09182. (The contradiction-type taxonomy informs what "same question" pairing must catch; the gold-label source + difficulty taxonomy.)
- Myakala, Agrawal & Manche (2026). *BeliefShift* (opinion-drift / belief-consistency benchmark). arXiv:2603.23848. (The position-drift framing + metrics.)
- SETEC Voiceprint capabilities manifest: `position_pair_register` task surface, `uncalibrated` calibration status, `handoff: experimental`, `min_setec_version: 1.121.0`.
- `argument-decision-audit.md` — the sibling consumer (ArgScope; the shim / floor-from-manifest / drift-gate precedent this audit mirrors).
- `content-advisory.md` (SETEC/APODICTIC) — the A3 severity-leak + finding-block firewall this validator reuses.
