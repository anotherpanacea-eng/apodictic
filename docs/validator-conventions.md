# Validator-Conventions — a meta-linter that validates the validator fleet

**Status:** **Built (Increment 1), 2026-06-20.** Shipped: `scripts/meta_lint.py` + `validate.sh validator-conventions` (M1–M4), wired into `--self-test-all` and `--check-all`. A validator that validates the validators.
<!-- built-when: scripts/meta_lint.py -->

APODICTIC's ~54-validator fleet shares a set of structural conventions — every self-testable validator is wired into the dispatcher with a `--self-test`; file resolvers classify inputs on **parsed blocks**, never a raw `"apodictic:<type>" in <text>` substring; the advertised count is **derived** from `AGG_VALIDATORS`, never hand-typed; every schema is actually consumed. Until now these were enforced only by manual review, and the gaps caused real latent bugs: a fleet-wide adversarial sweep (2026-06-20) found a **resolver-substring** class in 12 validators (a file that merely *names* a marker in prose misroutes and silently false-passes), plus crash-on-malformed, lexical-regex over-fire, and override-parse classes. The first two are *structural* and statically checkable — so this validator mechanizes them, and the class cannot silently re-enter.

## The checks

`validate.sh validator-conventions` reads `validate.sh` and the sibling `*.py` from its own directory (and the schemas via the shared resolver). No artifact input.

| ID | Rule |
|---|---|
| **M1 — dispatch + self-test** | Every name in `AGG_VALIDATORS` has a `<name>)` dispatcher case whose body handles `--self-test` (so `--self-test-all` can run it). A missing case or a case that ignores `--self-test` is a violation. |
| **M2 — resolver hygiene** | No validator script classifies inputs by a raw `"apodictic:<type>" in <text>` substring — the anti-pattern that misroutes a file naming the marker in prose. Resolvers must classify on parsed blocks (the `_has_block` / `art.parse_blocks` idiom). The safe `_has_block` degraded fallback uses a `"apodictic:%s" % btype` **format** string, which the literal pattern deliberately does not match. (Infra scripts with no resolver are exempt: `apodictic_artifacts.py`, `meta_lint.py`, `sync_setec.py`, `config_checks.py`.) |
| **M3 — derived count** | `validate.sh` derives the count from `AGG_VALIDATORS` (`AGG_COUNT=$(set -- $AGG_VALIDATORS; echo $#)`) — never a hand-typed integer that can drift (every Horizon spec written before 2026-06-20 wrongly told builders to "bump the 35→36 count string"). |
| **M4 — no orphan schema** | Every `*.schema.json` in `schemas/` has its `$id` referenced by at least one validator script — a schema nothing consumes is dead or mis-wired. |

`meta_lint.py --self-test` exercises each check function against synthetic inputs (always green); the `--check-all` live run validates the actual fleet (gating it at release). It is itself in `AGG_VALIDATORS`, so **M1 checks the meta-linter against its own rule.**

## Not (yet) mechanized

The sweep's other classes are deliberately out of scope for **the meta-linter (M1–M4)** in Increment 1 because they need per-validator semantics, not a structural grep — though several of them are nonetheless **fixed per-validator in this same PR**, just not statically gated. **Crash-on-malformed** (a non-dict block payload reaching `obj.get()`, plus the non-string-`id` variant in `softness-check`) is fixed per-validator with `isinstance(...)` guards (the companion crash work in this PR). **Override-parse** edge cases (the bare-marker gate-bypass in `softness-check` / `timeline_checks`) are likewise **fixed behaviorally in this PR** by ID-/slug-scoping the override parsers (see `changelog.d/softness-override-scoping.md`); they remain un-mechanized by M1–M4 because override scoping is a semantic property no line-level grep can verify. **Lexical-regex over/under-fire** (heuristic-tuning the specs already concede is fuzzy) stays a tracked follow-up. A future increment could add a crash-resistance check (every `parse_*` guards non-dict before `.get()`), but that needs AST-level analysis rather than the line-level greps M1–M4 use.
