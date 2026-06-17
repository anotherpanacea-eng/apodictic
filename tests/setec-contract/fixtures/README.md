# Contract fixtures (R5 — golden envelopes + reference fake)

Producer-owned golden `schema_version: 1.0` envelopes, one per consumer
surface, plus a stdlib-only reference fake. Implements R5 of
[`../setec-normalized-entrypoint-spec.md`](../setec-normalized-entrypoint-spec.md) §6.

## What's here

| File | Purpose |
|---|---|
| `<surface>.json` × 14 | One canonical envelope per consumer surface — the pinned contract. |
| `fake_setec.py` | Stdlib-only CLI that prints a surface's golden envelope. The consumer vendors a pinned copy to test its parser without SETEC's heavy deps. |
| `README.md` | This file. |

The fourteen surfaces (the `capabilities.d/` fragments carrying
`min_setec_version` + a non-empty `consumers:` list — ten consumed by
apodictic, four added for setec-voicewright; `voice_distance` and
`idiolect_detector` serve both):

```
variance_audit  manuscript_audit  repetition_audit       (task_surface: smoothing_diagnosis)
voice_distance  voice_profile  pov_voice_profile
punctuation_cadence_audit  idiolect_detector
mimicry_cosplay_audit  general_imposters                 (task_surface: voice_coherence)
narrative_decision_audit                                 (task_surface: narrative_decision_audit)
argument_decision_audit                                  (task_surface: argument_decision_audit)
voice_fingerprint                                        (task_surface: authorship_embedding)
binoculars_audit                                         (task_surface: binoculars_discrimination)
```

> The golden filename is the **surface id** (the `capabilities.d/<id>.yaml`
> stem and the script module name), not the `task_surface`. Several surfaces
> share a `task_surface` but each script emits its own envelope, so there is
> one golden per script.

## How the goldens are produced (faithfulness)

The goldens are **not hand-written JSON**. The generator
[`../../scripts/gen_contract_fixtures.py`](../../scripts/gen_contract_fixtures.py)
imports each surface's *own* envelope-assembly path
(`build_audit_payload` / `render_json` / `compose_envelope`) and feeds it a
canonical fixture input that mirrors the real internal `result` / `audit` /
`output` dict that surface emits at runtime. Therefore:

* envelope keys, key order, and nesting come from
  `output_schema.build_output` — the same call the script makes;
* the `claim_license` block comes from each script's own `_claim_license(...)`
  builder plus the per-surface fragment registry in
  `scripts/claim_license_surfaces/`, so the license text is never typed here
  and auto-updates when a surface's license changes;
* `task_surface` is the surface's own `TASK_SURFACE` constant;
* the `results` payload uses representative *values* but the real top-level
  and nested *keys*.

No heavy audit is run — no spaCy / torch / scipy / sentence-transformers. The
envelope is constructed directly from the fixture input, so generation is
deterministic and dependency-free. (`narrative_decision_audit` is driven
through its own deterministic, dependency-free **mock judge**, so its
feature contributions and aggregate are the real ones the script emits.)

## Normalization (volatile fields)

Volatile fields would change every release or run, so the generator and the
drift check replace them with sentinels before writing/comparing. The
**same** normalization is applied on both sides, so a freshly generated
envelope is byte-stable against the committed golden.

| Field | Sentinel | Why volatile |
|---|---|---|
| `version` | `"<fixture>"` | the script's `SCRIPT_VERSION`; bumps per release |
| `target.path` | `"<fixture>"` | absolute input path |
| `baseline.path` | `"<fixture>"` | idiolect reference path |
| `baseline.files[].path` | `"<fixture>"` | per-file absolute paths |
| `results.*.files[].path` | `"<fixture>"` | `corpus_summary` file paths |
| `results.inputs.manifest` | `"<fixture>"` | `pov_voice_profile` manifest path |
| `results.run_timestamp_utc` | `"<fixture-timestamp>"` | wall-clock run time |
| `results.prompt_fingerprint_sha256` | `"<fixture-sha256>"` | prompt hash |

A consumer parser tested against these goldens must tolerate the sentinel
values exactly as it tolerates real runtime values.

## Regenerating / checking

```bash
# regenerate every golden (after a faithful envelope change)
python3 plugins/setec-voiceprint/scripts/gen_contract_fixtures.py --write

# fail if any golden drifted from build_output (CI gate)
python3 plugins/setec-voiceprint/scripts/gen_contract_fixtures.py --check

# enumerate surfaces
python3 plugins/setec-voiceprint/scripts/gen_contract_fixtures.py --list
```

`tools/check_capabilities_drift.py` runs the same `--check` logic as **Check 9
(`fixture_drift`)** so envelope drift fails SETEC pre-merge. If a surface's
real envelope changes intentionally, run `--write` and commit the updated
golden in the same change.

## Consumer use (OQ5 — fixture ownership)

Per spec §6 OQ5, the contract's author is its fixture's author: these fixtures
are **producer-owned** here, and **each consumer (apodictic, setec-voicewright)
vendors a pinned copy** (pinned copy / git-subtree, refreshed on
`schema_version` or manifest bumps). Neither
repo imports the other; both compare against the same JSON, avoiding a
circular build dependency. The consumer runs `fake_setec.py <surface>` (or
reads `<surface>.json` directly) to exercise its parser with no SETEC deps:

```bash
python3 fake_setec.py variance_audit | python3 -m json.tool   # valid JSON
python3 fake_setec.py --list
```
