# Spec — Disposition supersedence must be recomputed, never trusted (disposition-check DP2.6)

**Status:** **Built** (this PR; spec-review pass 1 folded 2026-07-02, verdict BUILD-READY-WITH-FIXES, 0 P1). Built in `disposition_check.py` (recomputed `active()`, `evidence_texts` corroboration surface, DP2.6) + `validate.sh` hostile arm 4, both mirrored; `docs/finding-dispositions.md` §Schema 2 amendment.
<!-- built-when: scripts/disposition_check.py contains "DP2.6" -->
**Provenance:** sibling-sweep of the PR #161 Codex P1 (fabricated refutation budget, fixed in
`scripts/refutation_check.py` commit `7085daa` — *"recompute, don't trust: the recorded-field rule
applied to an exemption gate"*). This spec applies the same rule to the one other exemption path
the sweep found gated on a self-reported field: `disposition_check.active()`.
**Owner of the decision:** honesty-gate boundary (the spec-03 laundering firewall,
`docs/finding-dispositions.md` §Mechanical guards).

---

## Problem & verified evidence (anchors verified 2026-07-02, main @ `7dd0294`)

`scripts/disposition_check.py:209-211`:

```python
def active(fid):
    # Supersedence (read-time precedence): finding_states is checked FIRST, everywhere.
    return finding_states.get(fid) != "revised"
```

`finding_states` is read from the sidecar (`execution.finding_states`, line 201) and **trusted**.
A sidecar-recorded `"revised"` exempts a declined/deferred Must-Fix from three guards at once:

1. **DP1 caveat teeth** (`:253`): `active_dispo` drops the id → no readiness-caveat line owed —
   "superseded, no caveat" purely on the sidecar's say-so. This is the headline severity-laundering
   channel spec 03 built DP1 to close.
2. **DP2.1 contradiction** (`:290`): a same-report resolved+declined contradiction is suppressed.
3. **DP2.5 marker/sidecar sync** (`:341`, `:349`): both sync directions skip the id entirely.

### Corroboration audit — who could catch a fabricated `"revised"`? (adjudicated: nobody on the enforcement path)

- **Non-governed sidecar** (no `gate_events` — spec 03 calls this "the common case"; the canonical
  fixture is non-governed): `finding_states` is a **direct hand-write by design**
  (`docs/finding-dispositions.md` §Write path). `run_gate --check-state` exits 0 — *"legacy sidecar
  … nothing to check"* (`run_gate.py:711-712`). Nothing recomputes the field. Ever.
- **finding-trace E5 (phantom completion)** is deliberately scoped to ids the *current* completion
  report **mentions** (`finding_trace.py:262-267`; scope pinned by the PR #32 review P1 because
  `finding_states` is a rolling all-session map — self-test `e5_skipped_without_completion`,
  `finding_trace.py:513-514`, asserts *"revised state, no completion → no E5"*). A fabricated
  `"revised"` with **no completion artifact at all** is structurally invisible to E5.
- **finding-trace W3** keys on `<!-- resolved: F-… -->` markers (`:271-276`) — fires only when a
  marker exists without the state, never the reverse. Silent here.
- **finding-trace E3** accepts `"revised"` (a valid enum value); **E2** passes (the id is a real
  ledger finding).
- **Governed sidecar:** `check_state` pointer-drift *would* catch the hand-edit
  (`run_gate.py:843-844` recomputes `finding_states` from the event-log fold) — but `/ready` runs
  **only** `disposition-check` at verdict time (`submission-readiness.md:115`), so the drift check
  is not on the enforcement path DP1 protects; it fires only if someone later runs
  `gate --check-state`.
- **disposition-check itself:** DP2.5 skips inactive ids (both loops are `if active(fid)`-gated),
  so the fabrication *also* silences the sync WARN that would otherwise flag the id.

### The exploit (the repro shape the keystone self-test pins)

On a non-governed project with a declined Must-Fix `F-X` (record + Coaching-Log marker present,
caveat currently owed): edit **one JSON field** — `execution.finding_states["F-X"]: "delivered"` →
`"revised"` — and strip `F-X` from the assessment's caveat line. Result today: `disposition-check
<sidecar> <assessment>` exits **0** (id reported as "superseded"), DP2.5 says nothing, and the
`/ready` verdict ships with the declined Must-Fix absorbed. Every other validator stays green.
**Verdict: exploitable in practice — same class as the PR #161 P1 (an exemption gate trusting a
recorded field), and it defeats the exact guard (DP1) spec 03 names as its headline teeth.**

Scope note: the mechanical exemption consumers of `finding_states[id] == "revised"` were swept
repo-wide; `disposition_check.active()` is the only one (`regression_diff` W1 *fires on* revised
priors rather than exempting; the revision-coach ladder skip is LLM prose, not a gate;
`run_gate._disposition_deltas`' revised-is-a-no-op write filter is governed write-side and is
covered by the same fix's fail-closed direction).

---

## Fix — recompute the supersedence evidence (the `7085daa` rule)

**Design rule (normative, amends spec 03 §Schema 2):** `finding_states[id] == "revised"` supersedes
a disposition **only when corroborated** by a `<!-- resolved: F-id -->` marker in a reachable
completion artifact (`*_Revision_Report_*.md`). The sidecar state is a claim to verify, never an
input. Uncorroborated `"revised"` **fails closed**: the disposition stays ACTIVE everywhere in
`disposition-check` — DP1 still owes the caveat, DP2.5 still audits sync — and the mismatch is
surfaced (DP2.6 below).

This is sound because the markers are already the canonical source and the sidecar the mechanical
mirror (spec 03 §Schema 3, citing `docs/project-addressability.md:138`): every *legitimate* path to
`"revised"` produces the marker — the governed fold derives its `revised` deltas *from* the
report's resolved markers (`run_gate.py:457-476`), and the non-governed round-trip flow confirms
resolved markers before writing (`roundtrip-disposition` RT3, confirmed-writes-only). A `"revised"`
with no marker anywhere is either fabrication or a destroyed audit trail; neither may waive a
Must-Fix caveat silently.

### 1. `active()` recomputes (in `check()`)

```python
corroborated = set(resolved_ids)                  # the run's own completion artifacts (already read)
for t in (evidence_texts or []):                  # NEW: archived completion artifacts (see §2)
    corroborated |= ft.resolved_cited_ids(t)

def active(fid):
    # Supersedence (read-time precedence): finding_states is checked FIRST, everywhere — but
    # RECOMPUTED, never trusted (the PR #161 recorded-field rule applied to an exemption gate):
    # a sidecar 'revised' supersedes only when a <!-- resolved: fid --> marker corroborates it
    # in some reachable completion artifact. Uncorroborated 'revised' leaves the disposition
    # ACTIVE (fail-closed; DP2.6 surfaces the mismatch).
    return not (finding_states.get(fid) == "revised" and fid in corroborated)
```

All three `active()` call sites (DP1, DP2.1, DP2.5) and the per-id report line inherit the
recompute from the one definition — no per-site divergence. **DP2.1 semantics are unchanged by
construction:** DP2.1 only examines ids in `resolved_ids` (`:289`), and every such id is
corroborated by definition, so `active()` reduces to the old expression there — the
`dp2_1_supersedence_not_contradiction` case still passes untouched.

### 2. Evidence surface — reachable completion artifacts (`evidence_texts`)

The rolling-map reality E5's scoping honors (a finding legitimately revised in an *earlier* round
has its resolved marker in an *archived* report) is handled by **widening the evidence, not the
check**: corroboration reads resolved markers from the run's own `report_texts` **plus** an
`evidence_texts` set gathered from the project root and its `runs/*/` archives.

- **`_resolve` (both dir-mode and sidecar-mode):** when a sidecar was located, additionally glob
  `_REPORT_GLOB` over `dirname(sidecar)` + `dirname(sidecar)/runs/*` → the evidence path list,
  returned as an **8th tuple element** (`…, assessment, evidence_paths`); explicit-files mode (no
  sidecar) returns `[]`. `run()`'s 7-tuple unpack (`:383`) updates to match, reads the evidence
  files, and passes `evidence_texts=` through. In sidecar/project-root mode (the `/ready`
  invocation shape, `:136-137`) this is a no-op superset of the existing scan; in run-folder mode
  it is what makes an earlier round's legitimate revision corroborable. Explicit-files mode gathers
  no extra evidence — the caller controls the surface; the module docstring states the remediation
  (pass the archived report as an argument, or invoke via the project root/sidecar).
- **Evidence is corroboration-only.** It must NOT feed `report_texts` / `report_marker_ids` /
  `resolved_ids` / the marker homes — DP2.1's *same-run* contradiction scoping (`:283-289`) and
  DP2.5 stay exactly as they are. A new **keyword-only** `check(…, evidence_texts=None)` parameter
  (after `sidecar_parse_ok`) keeps every existing caller and self-test signature valid (additive,
  the 4a lesson). The `corroborated` set is computed immediately after the `resolved_ids` block
  (`:226-228`), before the first `active()` consumer (`:253`).
- Primary artifact resolution (newest ledger/letter/assessment selection) is untouched — the
  widened glob feeds evidence only.
- **Trust-model depth (stated in the module docstring, spec-review firewall item):** corroboration
  accepts any regex-matched `<!-- resolved: F-id -->` marker in a reachable completion artifact —
  evidence artifacts are **not** schema-validated or provenance-checked (`resolved_cited_ids` is a
  pure marker scan). This is by design, not oversight: markers are the canonical record (spec 03
  §Schema 3), and the fix's job is raising the fabrication bar from *one JSON field edit* to
  *forging a completion artifact* — the same artifact-forgery floor every marker-canonical surface
  in the repo shares.

### 3. DP2.6 — uncorroborated supersedence (WARN; ERROR under `--strict`)

New DP2 sub-assertion, placed **directly after the DP2.5 block** (`:335-351`): loop
`for fid in sorted(dispositioned)`, firing only when `finding_states.get(fid) == "revised"` and
`fid not in corroborated` (so it fires only where an exemption would be consumed, never on
undispositioned revised ids), appending to `warns` — the existing `--strict` escalation machinery
(`:368-369`) provides the ERROR promotion with no new plumbing:

```
DP2.6 uncorroborated supersedence: finding_states[F-X]=revised but no <!-- resolved: F-X -->
marker in any reachable completion artifact — supersedence is not corroborated; the disposition
is treated as ACTIVE (DP1 caveat still owed, DP2.5 sync still audited). If this finding was
genuinely revised, make its completion report reachable (run folder, project root, or runs/
archives).
```

Severity: **WARN by default, ERROR under `--strict`** — the DP2.5 family convention for
coherence signals. The *teeth* stay with DP1's fail-closed ERROR (the caveat is owed the moment
corroboration is absent); DP2.6 exists so the mismatch is named even when no assessment is present
(no verdict to launder yet) or the caveat is already over-disclosed. Rationale for not making
DP2.6 a flat ERROR: the one legitimate trigger is a pruned/unreachable archive, and the remediation
(restore the report, or run from the project root) is stated in the message; a flat ERROR would
false-fail archive-pruned projects that are already disclosing honestly.

### 4. What deliberately does NOT change

- **finding-trace E5/W3 scope is untouched.** Widening E5 to disposition-exempting ids was
  considered and rejected: it would re-introduce the rolling-map false-positive class the PR #32
  P1 scoping exists to prevent, it would couple `finding_trace` to dispositions (it reads them
  nowhere today), and it would not protect the enforcement path anyway — `/ready` runs only
  `disposition-check` at verdict time. The recompute belongs where the exemption is consumed
  (the `7085daa` precedent).
- **No log-side corroboration arm.** For governed sidecars the artifact evidence necessarily
  exists whenever the fold legitimately produced `revised` (the fold derives it *from* the report),
  so accepting gate-event corroboration would only widen trust surface (a non-clearing event's
  deltas are exactly what `check_state` rejects) for zero legitimate coverage. `gate --check-state`
  remains the log-side audit (the existing ownership split).
- **`run_gate.py`, schemas, the sidecar template, and the caveat grammar are untouched.** This is a
  read-side hardening of one validator plus its docs/fixtures.

---

## Self-test plan (`disposition_check.py --self-test`; additive except one fixture repair)

1. **Keystone (the exploit repro):** `dp1_fabricated_supersedence_still_owes_caveat` — declined
   Must-Fix, `finding_states` fabricated to `revised`, **no completion artifact**, assessment
   without the caveat line → exit 1 with the DP1 ERROR naming the id, plus the DP2.6 WARN. (This
   exact shape exits 0 today.)
2. `dp2_6_uncorroborated_warns` — same fabrication with the caveat present → exit 0 + DP2.6 WARN;
   `dp2_6_strict_escalates` → exit 1 under `--strict`.
3. `dp2_6_corroborated_clean` — revised + a report carrying the resolved marker → no DP2.6,
   exemption honored.
4. `dp1_archived_evidence_exempt` — resolved marker supplied via `evidence_texts` only (the
   earlier-round shape) → DP1 exempt, no DP2.6.
5. `dp2_5_not_suppressed_by_fabricated_revised` — record-without-marker desync + fabricated
   revised → the DP2.5 WARN still fires (today it is silenced).
6. **Fixture repair (semantic, called out per the never-edit-cases rule):** the existing
   `dp1_superseded_exempt` case (`:507-509`) encodes the pre-fix trust — revised state with **no**
   corroborating report. Under the new rule that is the attack shape, so the case gains its
   corroborating report via the `go()` helper's existing parameter —
   `reports=["<!-- resolved: F-P5-01 -->\n"]` — keeping the test name and assertion. No other
   existing case changes (`dp2_1_supersedence_not_contradiction` already carries its resolving
   report and passes as-is).
7. **Corroboration-only boundary pinned by outcome:** `dp2_1_evidence_not_leaked` — a resolved
   marker present **only** in `evidence_texts`, with a same-run disposition marker for the same id
   in the report home → **no** DP2.1 error (evidence never enters `resolved_ids`), exemption still
   honored where due.
8. **End-to-end (tempdir):** a project root (sidecar + `runs/old/` archived report resolving F-X)
   with a current run folder — run-folder mode finds the archived evidence → exempt; the same tree
   with the archived report deleted → DP1 fails + DP2.6 warns.

## Hostile arm 4 (`validate.sh --check-all`, canonical `example-run-folder-dispositions`)

On a temp copy of the canonical fixture (which today carries all-`delivered` states — untouched),
added after arm 3 (`~:773`): set `execution.finding_states["F-P5-01"] = "revised"` (python3, the
arm-2/3 json idiom) **and** strip the `**Declined Must-Fixes:**` line from the assessment →
`disposition-check` must **FAIL** with `DP1 declined Must-Fix F-P5-01` and the output must carry
`DP2.6`. Pre-fix this arm exits 0 — the fabricated-supersedence laundering attempt, fail-closed.
The `--check-all` description string (`validate.sh:233`) gains the new arm in its
disposition-check clause.

## Touched files (dual mirror applies)

`plugins/apodictic/scripts/disposition_check.py` + root mirror; `plugins/apodictic/scripts/validate.sh`
+ root mirror (hostile arm 4 + the `--check-all` description string); `docs/finding-dispositions.md`
(amend §Schema 2 Supersedence + DP1's `active =` definition + a dated as-built correction bullet
pointing here); this spec; `changelog.d/disposition-supersedence-recompute.md`. Mirror `cp` last,
then `validate.sh check-mirror` inside `bash scripts/validate.sh --check-all` (root copy — what CI
runs) as the exit gate. Codex gate applies (authored logic). Merge via merge commit. No version
bump in-PR.

**Builder anchor rule:** every line-number citation in this spec is pinned to main @ `7dd0294` —
re-grep each anchor before editing (the lean anchor-verify rule); never trust offsets after any
restructure.

**Spec-review:** pass 1 run 2026-07-02, verdict **BUILD-READY-WITH-FIXES** (0 P1, 5 P2 — evidence
plumbing concreteness, DP2.6 placement, fixture-repair mechanics, corroboration-boundary negative
test, trust-model docstring); all folded above.

## Failure modes if built badly

- **Evidence leaks into DP2.1** (same-run scoping broken → cross-round false contradictions):
  prevented by the corroboration-only `evidence_texts` parameter; self-test 3/4 + the untouched
  `dp2_1_*` cases pin it.
- **False DP1 on legitimately-archived revisions:** prevented by the `runs/*` evidence widening
  (self-tests 4/7); residual (archive actually deleted) degrades to an honest DP2.6 WARN + a caveat
  the author can over-disclose (subset-legal by design, `:270-272`).
- **The recompute forgets a call site:** impossible by construction — one `active()` definition,
  all consumers inherit.
