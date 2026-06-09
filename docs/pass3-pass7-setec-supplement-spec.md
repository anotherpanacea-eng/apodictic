# Handoff Spec: SETEC Supplementation for Pass 3 (Rhythm/Modulation) and Pass 7 (POV/Voice)

**Status:** Draft. Phase 2 follow-on. Not yet implemented.
**Predecessor work:** Phase 2 substrate swap + new audits, 2026-05-17 (see `project_apodictic_setec_integration.md` memory entry; `plugins/apodictic/skills/specialized-audits/scripts/setec_discovery.py` + ai_prose_* shims).
**Required SETEC:** ≥ 1.86.0 (schema_version 1.0 envelope; the `setec_discovery` helper enforces the floor).

---

## 1. Reframing: supplement, not replace

The earlier project-memory entry described Phase 2 as *"Pass 3 (Rhythm/Modulation) and Pass 7 (POV/Voice) substrate replaced with SETEC measurements feeding LLM interpretation."* That framing is wrong in one important way: **passes 3 and 7 already do real craft work the LLM is the right tool for.** The work here is not to swap them out. The work is to **bolster** the LLM with cheap measurements where a Python script does the job better.

The principle: the LLM should be **reading numbers**, not estimating them. Word counts, sentence-length distributions, per-POV stylometric centroids, pairwise voice-distance matrices, punctuation-rhythm densities — these are the cases where a script can give the LLM ground truth to reason against. The LLM still does the reading: is this rhythm regularization a problem given the scene's stakes? are these two POVs collapsed in voice or deliberately psychologically entangled? What earns its place? What doesn't?

A way to keep the line clear when implementing: if the pass already says "measure X" in a way that depends on the LLM's eyeball-estimate of a number, **SETEC measures it instead**. If the pass says "diagnose X" in a way that depends on craft judgment, **the LLM keeps doing it, now with SETEC numbers in evidence**.

---

## 2. Current state of each pass

### Pass 3 — Rhythm and Modulation
Definition: `plugins/apodictic/skills/core-editor/references/run-full.md` §Pass 3.

What the pass measures today (LLM eyeball-estimated):
- Sentence length variation
- Active verb density
- Dialogue-to-prose ratio
- Compression ratio (story time / word count)

What the pass diagnoses (LLM craft work, stays):
- Intensity map (scene-by-scene trajectory)
- Peak-valley pattern, relief ratio
- Sentence-level rhythm sampling at 3+ distributed points
- Title/framing architecture (when present): deepening / counterpoint / coherence tests
- Genre-specific rhythm checks (dread fatigue, clock pressure, etc.)
- Finding-driven audit triggers (Stakes System, Scene Turn, Literary Craft)

Constraint baked in: *"Metrics cannot flag scenes unless Pass 1 also logged an issue."* Pass 3 is investigative, not its own source of complaints. The supplementation does not change this rule — SETEC numbers are evidence the LLM uses to investigate Pass 1's flags more rigorously.

### Pass 7 — POV and Voice
Definition: `plugins/apodictic/skills/core-editor/references/run-full.md` §Pass 7.

What the pass measures today (LLM eyeball-estimated):
- Quantitative POV distribution (word count, % of total, sections, per POV)
- Voice distinctiveness across 6 dimensions per POV: sentence architecture, attention pattern, metaphor source domain, temporal orientation, epistemic style, emotional register
- Second-person word count (flag if >50,000 without variation)

What the pass diagnoses (LLM craft work, stays):
- Perspective slips, head-hopping, voice intrusion, distance inconsistency
- POV-power mismatch
- Under-individuation (4+ shared cognitive dimensions across POVs)
- Selective individuation (surface differentiation without deep)
- Blind Swap test (qualitative cross-POV swappability check)
- Tense consistency log

Constraint baked in: voice distinctiveness is most visible in high-stakes / emotionally charged scenes; supplementation should run on the same chapter slices the LLM is reading, not on aggregate corpora that wash out scene-level signal.

---

## 3. Supplementation plan, per pass

### Pass 3 supplementation

| Pass 3 measurement | SETEC script | What changes |
|---|---|---|
| Sentence-length variation | `variance_audit.py` (Tier 1: sentence-length stats + burstiness) | Replace LLM eyeball-estimate with reported mean / SD / burstiness B. |
| Compression ratio is **scene-by-scene** | `variance_audit.py --window-size N` | Per-window variance localization — feeds the intensity map directly. |
| Rhythm sampling at 3+ distributed points | `variance_audit.py` invoked once per sampled slice | Each sample carries SETEC numbers; the LLM still picks the samples. |
| Active verb density | (no SETEC equivalent; LLM keeps doing this) | — |
| Dialogue-to-prose ratio | (no SETEC equivalent; LLM keeps doing this — could be future work) | — |
| Punctuation rhythm (new) | `punctuation_cadence_audit.py` | Adds a new measurement the pass didn't have: catches house-style regularization the rhythm-by-sentence-length view misses. |
| Sliding-window pacing diagnosis | `sliding_window_heatmap.py` | Optional advanced output — visualizes variance localization across a long manuscript. Render only when manuscript ≥ 50,000 words. |

Where the supplementation runs in the pass: as **Step 1, before** the LLM produces the intensity map. The pass becomes:

> 1. Run SETEC measurements via `ai_prose_variance_audit.py` (two invocations by default per §6.1: one manuscript-aggregate, one window-mode at `--window-size 2000`) and `ai_prose_punctuation_cadence.py`. Use `--baseline-dir` only when a writer-project baseline is already in contract state (no intake prompt; per §6.3). Parse the schema_version 1.0 envelope; classify warnings into the three tiers from §6.4.
> 2. **Honor the Pass 1 gate.** If Pass 1 logged no issues, treat SETEC output as evidence to investigate; do not flag a scene Pass 1 did not flag.
> 3. Generate the intensity map and pacing diagnosis, citing SETEC numbers where they support a claim ("sentence-length SD compressed to 4.2 against baseline mean 9.1 in Ch 7; the rhythm flatness Pass 1 flagged is measurable here"). When SETEC and the LLM contradict, **name the contradiction** per §6.5 — surface to the writer, do not adjudicate.
> 4. If specific Pass-1-flagged scenes don't fall cleanly within a token window, escalate to per-scene variance_audit invocations on those scenes (bounded by §6.1).
> 5. Title/framing architecture, audit triggers, output table: unchanged.
> 6. If Pass 1 flagged rhythm issues AND SETEC ran heuristic-tier AND the diagnosis would tighten meaningfully with a personal baseline, append the §6.3 post-hoc baseline advisory.

Output document changes: the existing `[Project]_Pass3_Rhythm_Modulation_[runlabel].md` gains a small "Layer A measurements" section near the top with the SETEC numbers, a one-line band call, and any reliability-affecting warnings inline next to the measurements they qualify. The intensity map, finding-driven triggers, and audit recommendations are unchanged.

### Pass 7 supplementation

| Pass 7 measurement | SETEC script | What changes |
|---|---|---|
| POV word count distribution | (no SETEC needed; basic Python counting in the pass is fine) | The 15% threshold and word-count math are simple counts, not stylometry. **Do NOT route this through SETEC**; just count. The principle is "let Python do what Python does better" — but plain text-processing for word counts is already Python; SETEC adds nothing here. |
| Voice distinctiveness — sentence architecture | `pov_voice_profile.py` (per-POV centroids report sentence-shape features) | Replace eyeball-estimate with per-POV mean sentence length, length SD, clause-nesting indicators. |
| Voice distinctiveness — full 6-dimension comparison | `pov_voice_profile.py` + `voice_distance.py` per POV | The pairwise distance matrix is the empirical version of the 6-dimension comparison table. SETEC adds Burrows-Delta and per-feature cosine; the LLM still reads the metaphor-domain / temporal-orientation / epistemic-style dimensions that aren't fully captured by stylometry. |
| Voice-collapse verdict | `pov_voice_profile.py --collapse-threshold` | Empirical companion to the Blind Swap test. The LLM still runs the Blind Swap; SETEC's verdict goes in the evidence column. |
| Signature features per POV (new) | `idiolect_detector.py` per POV slice (target = single-POV documents in manifest) | Adds a layer the existing pass doesn't have: per-POV preservation candidates (the specific words / phrases that distinguish each POV). |
| Voice drift across the manuscript timeline (advanced) | `voice_drift_tracker.py` | Optional; only when the manuscript is a long-arc work where the writer drafted across many months and drift is a suspected confounder. |

Where the supplementation runs: as **Step 1 for multi-POV manuscripts**, before the voice-distinctiveness comparison. Single-POV manuscripts skip the POV-specific SETEC step but can still benefit from `voice_distance.py` against a writer's baseline if one is available (to test for register drift within a single POV).

POV manifest acquisition follows the §6.2 cascade — intake answer → runtime interactive question → LLM POV-shift detection — never auto-segment silently.

> 1. Determine POV mapping via the §6.2 cascade. Confirm whether the source is intake (author-confirmed), runtime input (author-confirmed), or LLM detection (NOT author-confirmed — record the caveat).
> 2. If multi-POV: build the in-memory manifest from the POV mapping; run `ai_prose_pov_voice_profile.py --manifest MANIFEST`. Parse the envelope; read `results.pairwise_distances`, `results.pov_vs_corpus`, `results.collapse_verdict`. Classify warnings per §6.4 and render inline.
> 3. If single-POV: skip POV stylometry. Optionally run `voice_distance.py` against the writer's baseline (when present in contract state) for register-drift signal within the single POV.
> 4. Run the Blind Swap test, the 6-dimension comparison, and the under-individuation / selective-individuation flags as written.
> 5. Where SETEC has spoken, **cite numbers in the comparison table**. Where SETEC is silent (metaphor domain, temporal orientation, etc.), the LLM is the source of truth. Where SETEC and the LLM contradict, name the contradiction per §6.5.
> 6. If Pass 7 ran with an LLM-detected POV mapping (cascade step 3), all stylometric findings in the output carry an "author-not-confirmed POV mapping" caveat near the citations.

Output document changes: the existing voice-distinctiveness comparison table gains a "Stylometric distance (Burrows Delta)" column when SETEC ran; the under-individuation / selective-individuation flags can cite SETEC's collapse-verdict as supporting evidence; a new advisory subsection lists per-POV signature features if `idiolect_detector` was run (per POV); when POV mapping came from LLM detection (cascade step 3), the head of the output records the source explicitly.

---

## 4. Implementation steps (suggested order)

1. **Read this spec, the `project_apodictic_setec_integration.md` memory, and the existing `setec_discovery.py` + ai_prose_* shims** (5 substrate shims, 3 new audit shims, all in `plugins/apodictic/skills/specialized-audits/scripts/`).
2. **Confirm pass output document formats** by reading `plugins/apodictic/skills/core-editor/references/run-full.md` §Pass 3 and §Pass 7 (and any sample output the project has — check `Outputs/` and `dist/` for shipped examples).
3. **Pass 3 (lighter; do first).**
   - Edit `run-full.md` §Pass 3 to add Step 0 (SETEC measurements) and update Output description to include the Layer A measurements section.
   - Specify the exact SETEC invocations in the pass (which scripts, what args, how to thread `--baseline-dir` when the writer has supplied one).
   - Decide where in the output Markdown to print SETEC numbers (suggested: a small table right after the H2 heading, before the intensity map).
   - Specify the citation convention: "SETEC tool=variance_audit, schema_version 1.0, band=Moderately smoothed, …" — terse, traceable, doesn't break the prose.
4. **Pass 7.**
   - Edit `run-full.md` §Pass 7. Make the manifest-gated execution explicit (single-POV path skips POV-specific stylometry; multi-POV path requires the manifest; no auto-segmentation).
   - Decide how the Blind Swap test reads SETEC's collapse verdict: is the verdict a *signal* the LLM weighs, or does it *modify* the under-individuation threshold? My recommendation: signal only — the existing 4+/6 cognitive-dimension threshold stays; SETEC adds an empirical confirmation column.
   - Add the per-POV signature-features advisory subsection structure to the output template.
5. **`pass-dependencies.md` updates.** §4e Audit-Signal Propagation Table currently routes audit findings into synthesis severity. Pass 3 and Pass 7 are core passes, not audits, so the propagation rule already covers them indirectly via the existing audit triggers. Confirm no §4e change is required for SETEC-bolstered measurements (they feed the pass's own finding, not a separate audit signal).
6. **Sample output regeneration.** Pick one fixture manuscript with the writer's baseline available. Run Pass 3 and Pass 7 manually following the new instructions and produce sample outputs. Diff against the previous output template to confirm the Markdown is still readable and the supplemental sections sit naturally.
7. **Regenerate codex + antigravity host workspaces** via `scripts/release.sh` (do NOT hand-edit those; they're regenerated copies of `plugins/apodictic/`).

Total effort estimate: ~1 session for Pass 3 (smaller surface), ~1.5–2 sessions for Pass 7 (manifest path + collapse-verdict interaction + per-POV signature-feature subsection).

---

## 5. Verification

What counts as "supplementation is wired in":

- **Pass 3:** `run-full.md` §Pass 3 names the SETEC scripts and their arg sets. The output document template shows where SETEC numbers appear. A sample run on a fixture manuscript produces an intensity map that cites SETEC measurements in at least one finding statement.
- **Pass 7:** `run-full.md` §Pass 7 has the multi-POV / single-POV branch explicit. The Blind Swap + 6-dimension comparison output shows a "Stylometric distance" column when run on a multi-POV fixture with a manifest. Single-POV runs do not error or fabricate; they note the gap.
- **No regressions:** Pass 1 gate on Pass 3 still binds (no flagging of unflagged scenes). Pass 7's under-individuation flag still requires the LLM's 4+/6 dimension reading; SETEC's collapse verdict is a co-signal, not a replacement.
- **Failure-mode test:** SETEC discovery fails (env var unset, no marketplace install). Pass 3 / Pass 7 print the discovery error and proceed with LLM-only analysis. The pass output should record "SETEC unavailable; Layer A measurements not run" near the head, so downstream readers know which signals were qualitative-only.

---

## 6. Resolved decisions

Decisions made 2026-05-17 with project owner. The five open questions in the draft are answered:

### 6.1 Per-window invocation cost — manuscript + windowed by default

Default cadence for Pass 3 is **two SETEC invocations**:
1. One manuscript-aggregate `variance_audit.py` run (Tier 1 always; Tier 2/3 when deps available).
2. One window-mode run with `--window-size 2000` (default; tune by manuscript length).

Token windows do not align with scene boundaries; the LLM projects windowed measurements onto scene positions when reading. This is the accepted limitation.

**Escalation rule:** when Pass 1 flagged specific scenes for rhythm issues AND the window-mode run's coverage doesn't fall cleanly within a flagged scene, escalate to a per-scene variance_audit invocation on that scene only. Bound: at most N invocations where N = count(Pass-1-flagged rhythm scenes). For typical manuscripts this is 0–5; for unusually bad pacing it may be 10+ but is still bounded.

**Open caveat (architectural):** very long manuscripts (200K+ words) may make even one variance_audit run slow enough to disrupt pass flow. If that becomes a real problem, the answer is "run SETEC once at intake, cache the output, all passes read the cache" — but that's a bigger architectural choice and is **not in scope for this spec**. Flag it as a follow-on if it surfaces during implementation.

### 6.2 POV manifest cascade for Pass 7

Three-step cascade, in priority order:

1. **Contract intake question (preferred).** Add to the intake protocol: "Is this manuscript multi-POV? If yes, list the POV characters and their chapter ranges." Answer is stored in contract state; Pass 7 reads it. This is symmetrical to existing structural intake questions (drafting method, contract type) and is properly the writer's call.
2. **Runtime interactive question (fallback when intake didn't capture it).** Single ad-hoc question at the moment Pass 7 begins. 30 seconds of writer time; the answer becomes an in-memory manifest. Used when the intake stage was skipped or didn't include POV info.
3. **LLM POV-shift detection (non-interactive fallback).** When neither intake answer nor interactive question is available — pipeline/headless modes — the LLM detects POV transitions from the prose itself and builds the manifest from the detection. The LLM is competent at POV-shift detection; this is a legitimate fallback, not a corner-cutting move.

**Output caveat when (3) was used:** the Pass 7 output records "POV mapping detected by LLM; not author-confirmed." The voice-distinctiveness comparison cites SETEC numbers with this caveat alongside, so a downstream reader (including a synthesis pass) knows the per-POV centroids were fit on LLM-segmented data. Auto-segmentation that occasionally goes wrong is acceptable when the limitation is disclosed; silent mis-segmentation is the failure mode to avoid.

### 6.3 Baseline corpus — no intake question; post-hoc offer

Pass 3 (and any other SETEC-supplemented pass) runs variance audit **heuristically by default** — no `--baseline-dir` unless the writer has already supplied one. The contract intake does **not** add a baseline-corpus question; we don't burden intake with infrastructure setup.

**Post-hoc offer convention.** After the pass runs and produces its diagnosis, if (and only if) BOTH of the following hold:

- Pass 1 flagged rhythm issues that Pass 3's SETEC heuristic-tier output corroborates (compression band ≥ Moderately smoothed, or specific signals z-score-equivalent past the heuristic threshold on multiple counts), AND
- The diagnosis would tighten meaningfully against a personal baseline (the `claim_license.additional_caveats` block flags the heuristic limit)

then the pass output appends an advisory: *"This diagnosis is heuristic against literature priors. If you have prior unedited work in this register, a personal-baseline run would tighten the claim. See [SETEC baseline-acquisition tooling] for setup."* The advisory is informational; the pass does not require the writer to act on it.

When the writer has already supplied a baseline (via contract setup or a previous run), the pass threads `--baseline-dir` automatically and the offer is irrelevant. Baseline state, when present, is a property of the writer-project, not a per-pass parameter.

### 6.4 Warnings handled in three tiers

The schema_version 1.0 `warnings` array is parsed and classified:

- **Blocking** (`available: false`). SETEC N/A for this run; pass falls back to LLM-only analysis. Output records the gap at the head of the pass document: *"SETEC measurement not run: [reason]. Diagnosis below is LLM-qualitative only."*
- **Reliability-affecting.** SETEC ran, but the measurement is noisy or partial. Examples: "text too short — Tier 1 signal noisy below 2000 words," "Tier 2 skipped: spaCy not installed; POS-bigram KL unavailable," "Tier 3 fell back to TF-IDF: sentence-transformers not installed." Render inline near the measurement, so the LLM (and the reader) weight the number against the warning. Don't bury these in a footer.
- **Cosmetic.** Filename anonymization notices, baseline-file-count info, default-private-output reminders. Silent in pass output; available to the auditor on drill-in.

**Implementation hook:** a small `warnings_classifier.py` (or a function in the `setec_runner.py` helper proposed in §6.6) holds the mapping from warning-string-prefix to tier. SETEC's schema spec does not itself classify; APODICTIC owns the rendering decision.

### 6.5 Synthesis propagation — no special treatment

SETEC-cited findings do NOT get special synthesis severity treatment. The pass author weighs SETEC numbers when assigning severity to a finding; synthesis reads the pass's verdict; numbers travel as supporting citation. Re-reading at synthesis would double-count.

Confirmed against `core-editor/references/run-synthesis.md §Step 2` Canonical Audit-Signal Propagation Rule: Must-Fix floors and hard gates are the propagation primitives; SETEC numbers don't produce floors directly.

**Related convention (new — not strictly synthesis, but pass-output):** when SETEC's measurement and the LLM's qualitative reading **contradict** within a single pass, the pass output should **name the contradiction**, not silently choose a side. Format:

> *Qualitative reading (Pass 3):* rhythm sustained across Ch 7's high-intensity sequence; sentence variety registers as deliberate.
> *Quantitative measurement (SETEC variance_audit, schema_version 1.0):* sentence-length SD compressed to 4.2 (writer baseline mean 9.1, z = −1.4); Layer A band = Moderately smoothed.
> *Reconciliation:* the compression may be earned (close third in a controlled emotional register often suppresses variance); surface to the writer for review rather than flagging as a defect.

Contradictions are real diagnostic findings. The writer wants to know when the reader-experience signal and the stylometric measurement diverge, because either (a) the stylometry caught what the LLM missed, or (b) the prose is doing controlled craft work that registers as compression. The pass does not adjudicate; it surfaces.

### 6.6 Implementation helper to bundle the plumbing

The decisions above imply a per-call wrapper that does: discover SETEC → invoke the right surface → parse the envelope → classify warnings → return a structured result the pass can read. Rather than reimplementing that flow in each pass, a small `setec_runner.py` in `plugins/apodictic/skills/specialized-audits/scripts/` bundles it. As implemented (R2/R3 adoption), it takes the SETEC **surface name** and routes through SETEC's normalized dispatcher (`setec_run.py <surface> --json`), which guarantees a stdout envelope for every surface and enforces the per-surface floor/dependencies:

```python
result = run_supplement(
    "variance_audit",                                   # SETEC surface NAME (not a script filename)
    [manuscript_path, "--baseline-dir", baseline_dir,   # the SETEC arg list the caller builds;
     "--window-size", "2000", "--no-tier2"],            #   --json is added by the dispatcher
)
# result.envelope            — schema_version 1.0 dict
# result.results             — the surface-specific payload
# result.available           — False on an R3 error envelope
# result.reason_category     — R3 enum on error (version_floor / missing_dependency / …)
# result.blocking_warnings   — list[str] (blocking tier — incl. the R3 reason on a hard error)
# result.reliability_warnings — list[str] (reliability tier, ready to render inline)
# result.claim_license       — structured dict
# result.claim_license_rendered — claim_license_rendered Markdown string
```

The runner does not invent functionality; it bundles `setec_discovery` + the dispatcher call plus the warnings classifier, the R3 `reason_category` → tier mapping, and a thin parse layer. It removes the boilerplate from each pass and keeps the supplementation contract in one place. Recommended but not strictly required.

---

## 6½. Contract intake amendment (Pass 7 dependency)

The cascade in §6.2 lands a single new question on contract intake. Add to the existing intake protocol:

> **Is this manuscript multi-POV?**
> - No, single POV (default; skip POV-specific stylometry)
> - Yes — please list POV characters and which chapters belong to each
> - Yes, but I'd rather Pass 7 detect POV transitions automatically (LLM-detected mapping; results carry an "author-not-confirmed" caveat)
> - Prefer not to say (Pass 7 defaults to LLM-only voice-distinctiveness comparison)

This is a structural intake question — the writer is the source of truth about manuscript structure — and parallels the existing drafting-method question. Implementation: edit `plugins/apodictic/skills/core-editor/references/intake-questions.md` to add the POV question; thread the answer through to Pass 7's preamble.

No baseline-corpus intake question. Baseline is offered post-hoc per §6.3.

---

## 7. Out of scope by design

- **Auto-segmenting by POV without a manifest.** Pass 7 should not attempt to detect POV transitions in raw prose to feed `pov_voice_profile.py`. That's a manuscript-preparation task the author owns.
- **Replacing the Blind Swap test.** SETEC's collapse verdict is a co-signal, not a replacement. The Blind Swap reads what an actual reader's reading experience does; the stylometry reads centroids. Both stay.
- **Promoting Pass 3 above its Pass 1 gate.** The constraint that Pass 3 cannot flag scenes unflagged by Pass 1 remains. SETEC numbers are *investigative*, not their own source of complaint.
- **Tier 4 surprisal signals by default.** SETEC's `--tier4` is opt-in for a reason (heavy install: transformers + torch; provisional bands). Pass 3 supplementation should NOT enable it by default. Document it as available; let advanced users opt in.
- **Publishing per-POV centroids outside the project.** SETEC enforces a default-private output policy for voice-cloning-input artifacts; the supplementation honors it.
- **Pass 3 active-verb density / dialogue-to-prose ratio supplementation.** SETEC has no current signal for these; flag as potential future work but do not block on it.

---

## 8. Cross-references

- `plugins/apodictic/skills/core-editor/references/run-full.md` §Pass 3, §Pass 7
- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` §4e Audit-Signal Propagation Table
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` §Step 2 Canonical Audit-Signal Propagation Rule
- `plugins/apodictic/skills/specialized-audits/scripts/setec_discovery.py` — discovery contract
- `plugins/apodictic/skills/specialized-audits/references/craft/ai-prose-calibration-distributional.md` §Computing the Signals — schema_version 1.0 envelope spec
- `plugins/apodictic/skills/specialized-audits/references/craft/pov-voice-profile.md` — opt-in audit; will be the Pass 7 stylometry companion
- `plugins/apodictic/skills/specialized-audits/references/craft/punctuation-cadence.md` — Pass 3 punctuation-rhythm companion
- `plugins/apodictic/skills/specialized-audits/references/craft/idiolect-preservation.md` — Pass 7 per-POV signature-feature companion
- SETEC spec: `setec-voiceprint/internal/SPEC_output_schema_unification.md`
- Memory: `project_apodictic_setec_integration.md`
