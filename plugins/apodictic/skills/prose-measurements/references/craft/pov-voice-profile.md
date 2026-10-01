# Specialized Audit: POV Voice Profile (Opt-In)
## Version 1.0
*Last Updated: May 2026*

---

## Purpose

For multi-POV fiction, build per-POV-character voiceprints and report whether the POV voices are stylometrically distinct or have collapsed into the writer's neutral default. Produces:

- **Per-POV voiceprint summary** — feature centroids (function-word distribution, sentence-shape stats, punctuation cadence) per POV.
- **Pairwise POV voice-distance matrix** — Burrows Delta + cosine, per feature family + weighted aggregate.
- **POV-vs-corpus-mean distance** — how far each POV sits from the writer's overall voice.
- **Top distinguishing features per POV** — where this POV's centroid most diverges from the mean of the other POVs.
- **Voice-collapse verdict** — POV pairs whose pairwise Burrows Delta falls below a heuristic threshold are flagged as potentially indistinct.

This is the third question in the voice-coherence suite. `ai_prose_voice_distance` answers "how far is this draft from the writer's overall baseline?" `voice_drift_tracker` (SETEC) answers "has the writer's voice changed across time?" POV Voice Profile answers "are this writer's POV characters voice-distinct, or has the writer's neutral default collapsed multiple characters into one voice?"

**This audit is opt-in.** Two reasons: (1) it requires a JSONL manifest with `pov` annotations on selected entries (per-POV stylometric fit is non-trivial to assemble); (2) the diagnostic is most useful for manuscripts with 2+ POV characters where voice-distinctness is a suspected risk. Running it on single-POV work, or on multi-POV work where the POVs are deliberately voice-aligned (e.g., a chorus narrator), wastes effort.

**Substrate.** Shim `scripts/ai_prose_pov_voice_profile.py` → SETEC `pov_voice_profile.py`. Requires SETEC ≥ 1.86.0. See `ai-prose-calibration-distributional.md §Computing the Signals` for the discovery contract and JSON envelope.

---

## When to Activate

- **Multi-POV fiction AND Pass 7 Blind Swap fails.** When characters sound interchangeable in the swap test, this audit shows the magnitude of the collapse and which POV pairs are closest.
- **Multi-POV fiction AND AI-Prose Calibration shows AIC-1 (Generic Hand) + AIC-5 (Puppet Dialogue) co-occurring.** That compound flag predicts voice collapse at the POV layer; this audit measures it directly.
- **Author specifically asks "do my POVs sound different?"** — request-driven activation. Some writers want the empirical answer before they trust the Blind Swap.
- **Series consistency check.** When a multi-POV series is mid-publication, this audit can verify that the POV voices in a new book match the POV voices in earlier books (run separately per book; compare centroids).

## When NOT to Activate

- **Single-POV work.** No comparison set; the audit cannot produce signal.
- **Multi-POV work below ~3,000 words per POV.** Per-POV stylometric fits are noisy at small sizes; results are unreliable.
- **POVs are deliberately voice-aligned.** Chorus narration, single-narrator multi-perspective (where the narrator is the same voice describing different characters), or specific literary forms where POV voices are *meant* to converge. The audit will fire a collapse verdict that's a false positive; running it would force the auditor to defend a non-finding.
- **No JSONL manifest with POV annotations exists.** The audit can't run without one. Building a manifest takes editorial effort (label each document or chapter by POV); only worth the effort when the diagnostic question is real.

---

## Inputs

The shim forwards CLI arguments verbatim. Required and operative inputs:

- **`--manifest MANIFEST`** — JSONL manifest, one entry per document/chapter, with a `pov` field naming the POV character on each entry that the audit should fit. Other fields per SETEC manifest conventions (`text` or `path`, optional `use`, `register`, `split`).
- **`--use USE`** — manifest `use` tag to filter entries (default `voice_profile`). Lets the same manifest serve multiple audit purposes.
- **`--min-docs-per-pov N`** — minimum documents per POV to fit a centroid. Below this, the POV is dropped from the analysis. Default applies the SETEC heuristic; raise it for noisy short-fiction corpora.
- **`--top-distinguishing N`** — how many distinguishing features to report per POV.
- **`--collapse-threshold T`** — Burrows-Delta value below which a POV pair is flagged as collapsed. SETEC's default is a calibrated heuristic; the SETEC notes call out that it is heuristic and on a calibration roadmap. Treat collapse verdicts at borderline distances as advisory.

Privacy: POV voiceprints are voice-cloning input. SETEC's default-private output policy applies (outputs outside `ai-prose-baselines-private/` are refused unless `--allow-public-output` is passed; safe override only for non-personal corpora like Federalist).

---

## Interpreting the Output

### JSON envelope (schema_version 1.0)

Relevant blocks:

- **`results.povs`** — per-POV summary (n_docs, n_words, centroid, top distinguishing features).
- **`results.pairwise_distances`** — Burrows Delta + cosine matrix across POVs.
- **`results.pov_vs_corpus`** — distance from each POV to the writer's overall corpus mean.
- **`results.collapse_verdict`** — list of POV pairs below the collapse threshold, with their pairwise distances and a brief note. THIS is the operative artifact for the Pass 7 cross-reference.
- **`claim_license`** — licenses "pairwise stylometric distance between POV centroids in the supplied manifest." Does NOT license:
  - "Character X has weak voice." (The audit measures *distance between centroids*, not voice strength.)
  - "These POVs were written by the same model / writer / drafting method." (Provenance is out of scope.)
  - "POV pair X-Y must be rewritten." (The audit identifies candidates; revision is the author's call.)

### Reading a collapse verdict

A collapse verdict is a **diagnostic finding**, not a sentence:

1. **Check distance magnitude.** A pair at 0.4 (well below threshold) is a strong collapse signal. A pair at the threshold ± 5% is borderline; treat as "investigate, don't conclude."
2. **Check distinguishing features.** When the audit reports the top distinguishing features per POV, a collapse-flagged pair will share most features (their centroids are near). Look at *which* features distinguish them, however weakly — this tells the author where the voice differentiation that exists already lives, and where it could be amplified.
3. **Cross-reference upstream findings.** Did Pass 7 Blind Swap also fail on these characters? Did AI-Prose Calibration flag AIC-5 (Puppet Dialogue) in scenes featuring these POVs? Convergent signal from multiple audits raises confidence.
4. **Consider deliberate voice convergence.** Some narratives intentionally collapse POVs (e.g., two characters becoming psychologically entangled; a chorus structure; a confined first-person narrator who never modulates). When the convergence is deliberate, the audit's flag is correct in its measurement but inert in its recommendation.

### Cross-references

- **Pass 7 (Voice/POV) Blind Swap.** The qualitative test. POV Voice Profile is the quantitative measurement that pairs with the Blind Swap's reader-trust signal.
- **AI-Prose Calibration AIC-1 + AIC-5.** Generic Hand + Puppet Dialogue together predict POV voice collapse. POV Voice Profile is the confirming measurement.
- **`voice_drift_tracker`** (SETEC standalone). When the writer's overall voice has drifted, a POV collapse may reflect that drift (everyone now sounds like the writer's recent neutral default) rather than character-specific collapse.

---

## Severity / Readiness Impact

POV Voice Profile findings interact with Pass 7 (Voice/POV) severity. The propagation rules below are operationalized in §4e of `core-editor/references/pass-dependencies.md`; the rows there are marked **provisional 2026-05-18** pending validation against a real multi-POV fixture.

- **Voice-collapse verdict on 2+ POV pairs AND Pass 7 Blind Swap fails on the same pairs** → propagates as a Must-Fix floor at synthesis. The empirical and qualitative signals are convergent; the manuscript's POV layer needs work.
- **Voice-collapse verdict on 1 POV pair AND Pass 7 Blind Swap fails on that pair** → propagates as Should-Fix (provisional). Convergent on a single pair; pattern-level signal.
- **Voice-collapse verdict on 1 POV pair AND Pass 7 Blind Swap passes** → Could-Fix; the measurement is below threshold but reader-experience doesn't track it. Note for the author; don't gate.
- **Voice-collapse verdict (any pair count) AND Blind Swap passes broadly** → Could-Fix; stylometry-only signal. The Pass 7 contradiction-reporting convention surfaces the divergence to the writer without adjudicating.
- **No collapse verdict; all pairs well above threshold** → POV differentiation is present at the stylometric level. If Pass 7 still has reader-trust concerns, the issue lives somewhere other than voice register (psychology, agency, narrative role).

**Two severity modifiers (provisional, both downshift one tier):**

- **Threshold-borderline (within 5% of SETEC cutoff).** The collapse threshold is a SETEC heuristic on a calibration roadmap. When the threshold call is borderline AND the qualitative Blind Swap is the deciding signal, downshift the synthesis severity by one tier (Must-Fix → Should-Fix; Should-Fix → Could-Fix; Could-Fix stays Could-Fix with an advisory note).
- **LLM-detected POV mapping (cascade step 3 in `run-full.md` §Pass 7).** When the POV-to-chapter mapping came from LLM detection rather than author confirmation, the stylometry was fit on possibly-incorrect segmentation. Downshift one tier; author confirmation at any later point restores base tier.

The audit's `claim_license` block carries the explicit `additional_caveats` for the threshold-heuristic limitation; downstream synthesis honors that caveat through the modifiers above.

---

## Output Ordering

```
1. Pass-Linked Symptom Summary (Pass 7 Blind Swap result, AIC flags)
2. Per-POV centroid summary (n_docs, n_words, top distinguishing features)
3. Pairwise distance matrix
4. POV-vs-corpus-mean table
5. Voice-collapse verdict (if any pairs flagged) with named pairs and distances
6. Cross-reference notes (Pass 7, AIC-1/AIC-5)
7. Readiness Impact Note (Pass 11 interaction)
8. Synthesis translation (severity mapping for revision checklist)
```

---

## Firewall Compliance

This audit:
- Does NOT generate POV voices for characters whose voices are flagged as collapsed.
- Does NOT recommend specific verbal tics, sentence shapes, or vocabulary moves to differentiate POVs.
- Does NOT adjudicate whether a deliberate voice convergence is "earned" — the audit measures distance; the author and editor read the measurement against narrative intent.
- Does NOT publish per-POV centroids outside the project (default-private output policy).

When POV differentiation needs to be amplified, this audit identifies which pairs and at what distance; the writer executes the differentiation work, often with Pass 7 (Voice/POV) and AI-Prose Calibration AIC-5 (Puppet Dialogue) as the prose-level companions.
