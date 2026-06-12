### SETEC integration — adopt the R2 normalized dispatcher + R3 structured errors

`setec_runner.run_supplement` now routes EVERY SETEC surface through SETEC's
normalized dispatcher (`setec_run.py <surface> [args] --json`, R2) and parses
the `schema_version` 1.0 envelope from **stdout** — including
`pov_voice_profile`, whose private file artifact the dispatcher projects to
stdout. One delivery path. The signature changed from a script filename to a
surface NAME: `run_supplement("variance_audit", args)`, not
`run_supplement("variance_audit.py", args)`.

- **Deleted from `run_supplement`:** the `json_out` parameter, the
  `_caller_json_out_path` helper, the `--json-out` injection + `--json-out=`
  /split-form recovery, the ephemeral `ai-prose-baselines-private/` tempdir +
  `rmtree`, and the `min_version` escape hatch. The dispatcher owns delivery
  and floor/dependency enforcement now.
- **R3 structured errors.** On `available: false`, `run_supplement` branches on
  the envelope's `reason_category` (not stderr scraping): `version_floor` /
  `missing_dependency` → blocking (surface the upgrade/install message);
  `text_too_short` → reliability (preserving the §6.4 reliability-vs-blocking
  semantics); `policy_refused` / `bad_input` / `internal_error` (and any
  unknown category) → blocking with the reason text. New `SupplementResult`
  fields `reason` / `reason_category` carry the structured error.
- **The 9 `ai_prose_*.py` shims are thinned** to a single
  `run_surface_cli(SURFACE, argv)` call (via the shared helper in
  `setec_runner`): they drop the per-shim `resolve_floor` runtime pre-check and
  the `pov` `json_out=True` special-case, route through the dispatcher, emit the
  envelope to stdout, and exit with the dispatcher's exit-code contract.
- **Floor reconciliation.** The dispatcher is the single RUNTIME authority for
  per-surface floor/dependency failures (it returns R3 `version_floor` /
  `missing_dependency`). `setec_capabilities.resolve_floor` + the vendored
  manifest are retained ONLY for the offline drift gate and capability
  introspection (Increment 2's contract role), not a redundant runtime
  pre-check that could drift from the dispatcher.
- **Bootstrap/dispatcher floor.** `run_supplement` fails cleanly with an
  upgrade message if the discovered SETEC predates the R2 dispatcher
  (`setec_run.py` absent) rather than crashing. A `# FINALIZATION:` marker in
  `setec_runner.py` flags raising `BOOTSTRAP_SETEC_VERSION` to the real R2
  release (target ~1.114) once SETEC cuts it.
- **Docs updated:** `run-full.md` Pass 3 + Pass 7 wiring (surface-name calls;
  Pass 7 multi-POV drops `json_out`; POV read keys corrected to the dispatcher's
  projected names `cross_pov_distances_weighted` / `pov_vs_corpus_mean` /
  `voice_collapse_verdict`); `narrative-decision-audit.md`; the contract test
  gains the dispatcher path (T2) + R3 tiering (T2b).
