### SETEC integration — adopt the ArgScope `argument_decision_audit` surface

APODICTIC now consumes SETEC Voiceprint's `argument_decision_audit` task surface
(ArgScope) — the argument-domain sibling of the narrative-decision (StoryScope)
audit. A new thin shim `ai_prose_argument_decision_audit.py` routes the surface
through SETEC's normalized dispatcher (R2) via `run_surface_cli`, like the other
`ai_prose_*` shims; the dispatcher enforces the per-surface version floor at
runtime (R3 `version_floor` on an out-of-floor SETEC), so the shim hardcodes no
version. The surface scores a public-debate / op-ed essay's argumentative
STRUCTURE — the B1 paragraph-role transition arc (support→proposal,
support→support, thesis-opening) + the B2 discourse-mode share — against Kim et
al. 2026's ("Argument Collapse", arXiv:2606.01736) human/LLM group means. It
measures argumentative *diversity*, not quality, soundness, or provenance, ships
`uncalibrated`, and is register-bound to public-debate forums (research / legal /
policy = the consumer's `distant` tier, structural-signals-only).

- **Bumped the vendored SETEC contract pin v1.114.0 → v1.116.0** (`setec-plugin.lock`,
  release pin to the tag carrying the surface). Re-synced the consumer-projected
  manifest (`tests/setec-contract/setec-capabilities.json`, now 13 apodictic
  surfaces incl. `argument_decision_audit` at floor 1.116.0) and the R5 contract
  fixtures via `scripts/sync_setec.py`. Per the script's documented design the
  manifest is consumer-projected while the golden fixtures are copied whole, so
  the bump also vendors the 1.115.0 voicewright-bundle goldens (binoculars /
  general_imposters / mimicry_cosplay / voice_fingerprint) as parser-test data.
- **New audit-level contract** `references/craft/argument-decision-audit.md` (v0.1):
  the envelope shape (4 contributions, B1/B2 bundles, heuristic `reused_signals`,
  the `pre_flag`), the 3-tier register map, the claim-license fields to surface,
  the aggregate posture (pin per-signal `contributions`, NOT the aggregate score),
  judge provenance, and the anti-verdict / framing note. It may PRE-FLAG whether a
  dialectical-clarity (soundness) run is informative; it never adjudicates
  soundness, warrant, or fairness.
- **Registered in the specialized-audits SKILL.md** (triggers, the surfaces table
  row, and the references list).
- **Offline contract test** (`tests/setec-contract/test_setec_contract.py`) now
  expects 10 shim surfaces and pins `argument_decision_audit`'s floor at 1.116.0;
  the drift gate re-derives the shim set, so the new shim joins automatically.
- Pins only the parts SETEC has committed (envelope shape, per-signal
  `contributions`, `claim_license`); the aggregate math, B3/B4 `reused_signals`
  (heuristic, no numeric anchor by design), and the deferred dynamic signals
  remain provisional under the surface's `handoff: experimental` posture.
