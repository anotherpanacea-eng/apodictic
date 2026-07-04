# Genre-Specific Tag-Audit fixtures

Ground-truth fixtures for three tag audits that had **no** canonical fixture invoking them:

- Queer Romance / Erotica — `plugins/apodictic/skills/specialized-audits/references/tag/queer-romance-erotica.md`
- Cozy — `plugins/apodictic/skills/specialized-audits/references/tag/cozy-tag.md`
- Philosophical — `plugins/apodictic/skills/specialized-audits/references/tag/philosophical-tag.md`

All fixture text is **synthetic** (authored for this eval, no permission constraints;
provenance tier 1). Each scene is a self-contained ~500-word passage authored to exercise its
audit's activation path and give a run real signal to diagnose. A **no-tag baseline** is
included so a run can confirm each audit's findings against a scene where the audit should NOT
activate at all (per the ROADMAP corpus-expansion item).

| File | Audit exercised | Planted signals |
|------|-----------------|-----------------|
| `queer-romance-scene.md` | Queer Romance / Erotica | Same-pronoun clarity strain; "explaining queerness" audience-orientation flag; Bury-Your-Gays / tragic-queer trope; authentic queer-space community texture (a strength to protect) |
| `cozy-scene.md` | Cozy | Cruelty Leak (CZ-2); Comfort Prop (CZ-5 / Axis B); Trapdoor safety-envelope breach with absent recovery (CZ-2 / CZ-3) |
| `philosophical-scene.md` | Philosophical | Seminar Scene (PH-4); Topic Fog (PH-1); Decoration Philosophy (PH-5); Explanatory Reflex / Closed Loop (PH-7) |
| `no-tag-baseline.md` | none — negative control | A grounded logistics scene; no queer central relationship, no cozy promise, no philosophical claim. No tag audit should activate. |

## What this tests (and what it does not)

These are **behavioral** eval fixtures. Tag audits are model-interpreted experience-layer
diagnostics; there is no `validate.sh` arm that parses tag-audit scenes, and the
`argument-groundtruth-check` gate walks only `evals/fixtures/argument-benchmark/*/`, not this
directory. These fixtures are therefore **pure data**. A run activates the relevant tag audit
on each scene, produces the audit's flag table, and is scored against `expected.md`; then it
runs all three audits' trigger checks against `no-tag-baseline.md` and confirms none fires.

The model-run coverage-confirmation report (per the corpus-expansion survey) is a separate,
**deferred** deliverable — these files are the fixtures only.
