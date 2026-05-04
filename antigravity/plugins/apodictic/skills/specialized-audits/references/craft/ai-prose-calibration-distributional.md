# AI-Prose Calibration: Distributional Diagnostics (Layer A)
## APODICTIC Development Editor
*Created: May 2026*
*Status: Computational reference for the AI-Prose Calibration audit (v2.0)*

---

## Purpose

The mathematical layer of the AI-Prose Calibration audit. Measures whether prose has been smoothed into the AI mode-collapsed region of stylometric space, regardless of which specific patterns appear on the surface.

This document specifies the eleven variance signals used by the Layer A pre-scan, the band-classification heuristics, the calibration warnings, and the integration between Layer A magnitudes and Layer B flag predictions.

**See `ai-prose-calibration.md` for the audit's overall structure and the Layer A pre-scan's role.**

---

## The Mode-Collapse Claim

Every working AI-prose detector measures one underlying asymmetry: human writing occupies a high-variance, long-tailed, multi-modal region of stylometric distributions. RLHF-aligned LLM output occupies a narrower sub-region that overlaps the human mode but conspicuously lacks the tails. This compression is not an accident of training data; it is a consequence of policy-gradient optimization against human preference signals that reward "helpful, polished, neutral" prose.

Formally, for any stylometric variable X (sentence length, FKGL, function-word frequency, etc.):

- p_human(X) is approximately log-normal or power-law with high variance and fat tails
- p_LLM(X) is approximately Gaussian, concentrated near the mode of p_human, with variance often an order of magnitude smaller

The detection signal is the variance ratio σ²_LLM / σ²_human < 1, accompanied by reduced kurtosis (thinner tails). The restoration target is the inverse: reintroduce variance, especially in the tails, without losing coherence.

The Layer A pre-scan reports per-document quantiles on each variance signal. The aggregated magnitude (Lightly / Moderately / Heavily smoothed) is a function of how many signals fall in compressed bands and by how much.

---

## The Eleven Signals

### 1. Sentence-Length Variance

**What it measures.** The dispersion of sentence lengths across the document, in tokens.

**Formulas.** Mean μ, standard deviation σ, range. The Goh-Barabási burstiness coefficient normalizes:

```
B = (σ − μ) / (σ + μ),  B ∈ [−1, +1]
```

B < 0 indicates sub-Poisson regularity (mode collapse). B = 0 is Poisson-like. B > 0 is super-Poisson with fat tails (human territory).

**Why LLMs trip it.** Training rewards fluent middle-length sentences. Most outputs cluster 14-22 words. Decoding heuristics (top-k, nucleus) further compress variance.

**Human reference.** Variance in matched-genre human essays runs 80-200 tokens². Matched RLHF-LLM essays run 15-60 tokens² (Muñoz-Ortiz et al., Cognitive Computation 2024).

**Caveat.** Diffusion-based LLMs (LLaDA) produce burstiness much closer to human; this signal is autoregressive-LLM-specific (Tarım & Onan 2025).

**Heuristic interpretation.** σ < 8 and B near 0 is heavily smoothed. σ in 8-12 with B slightly positive is moderately smoothed. σ > 12 with B > 0.2 is human territory for most prose registers. Literary fiction often shows σ > 15. Some essayistic registers can naturally produce B values down to -0.4; calibrate against the writer's own baseline rather than absolute thresholds.

### 2. MATTR (Moving-Average Type-Token Ratio)

**What it measures.** Lexical diversity normalized for length. Window of 50 tokens (configurable), running TTR averaged across windows.

**Formula.**

```
MATTR = (1/(N − w + 1)) · Σ_k V_k / w
```

where w is window size, V_k is unique types in window k, N is total tokens.

**Why LLMs trip it.** RLHF-trained LLMs at default temperature show constrained diversity; they prefer canonical synonym distributions. Reviriego et al. (ACM TIST 2024) show MATTR rises with sampling temperature, meaning the signal is tunable but predictable at default settings.

**Human reference.** MATTR for fluent native-English fiction at window 50: typically 0.70-0.82. LLM outputs at default temperature: 0.62-0.72.

**Heuristic interpretation.** MATTR < 0.65 in narrative prose suggests heavy smoothing or limited vocabulary scope. The signal is genre-sensitive: technical writing runs lower than literary fiction. Some writers' natural MATTR sits in the 0.78-0.82 range across registers; for these, MATTR z-score against personal baseline is more diagnostic than absolute threshold.

### 3. MTLD (Measure of Textual Lexical Diversity)

**What it measures.** Length-robust lexical diversity computed as average run-length before TTR drops below the τ = 0.72 plateau, computed forward and backward and averaged.

**Algorithm.** Walk the text. Track running TTR. When it crosses τ = 0.72, increment factor count and reset. Final MTLD = N / number of factors. Repeat backward; average.

**Why LLMs trip it.** Same mechanism as MATTR. Lexical preferences narrow under RLHF.

**Human reference.** Fluent native fiction: MTLD typically 80-130. LLM outputs at default temperature: 60-90.

**Heuristic interpretation.** MTLD < 70 in literary or narrative prose suggests heavy smoothing. Length-sensitive: noisy below ~500 words.

### 4. Yule's K

**What it measures.** Length-invariant vocabulary concentration.

**Formula.**

```
K = 10⁴ · (M₂ − N) / N²
```

where M₂ = Σ i² · f_v(i, N) and f_v(i, N) is the frequency of types occurring i times in a text of length N.

**Why LLMs trip it.** Yule's K detects how concentrated vocabulary use is on a small number of frequent types. LLMs over-rely on safe high-frequency connectives ("furthermore," "moreover," "additionally") which inflates K.

**Human reference.** K for fluent native fiction: 80-150 (lower K = more even distribution). LLM outputs: often 150-220 (more concentrated on frequent terms).

**Heuristic interpretation.** Tanaka-Ishii and Aihara (Computational Linguistics 2015) identify K and Rényi-2 entropy as the best length-constancy measures. K > 200 in fluid narrative prose is suspicious.

### 5. Shannon Entropy of Token Distribution

**What it measures.** Evenness of token usage, not vocabulary size. A text with 100 types each used once has H = log 100. A text with one dominant type has lower H.

**Formula.**

```
H = − Σ_w p(w) · log p(w)
```

**Why LLMs trip it.** RLHF concentrates probability mass on safe connectives and high-register nouns. Entropy drops because the distribution loses evenness even if vocabulary size is preserved.

**Human reference.** Reported in bits per token. Native fiction typically 9.5-10.5 bits/token. LLM outputs typically 9.0-9.8.

**Heuristic interpretation.** Use jointly with Yule's K. Both compressed at once is a strong signal. Some writers' natural entropy sits in the 8.0-9.6 range across registers (focused vocabulary scope, project-specific recurring terms); for these, entropy z-score against personal baseline is more diagnostic than absolute threshold. The signal is also length-sensitive: unreliable below ~1000 words.

### 6. Per-Sentence FKGL Variance

**What it measures.** How much readability fluctuates across sentences within the document.

**Formula.** Compute Flesch-Kincaid Grade Level for each sentence, take standard deviation.

```
FKGL_i = 0.39 · W_i + 11.8 · (Sy_i / W_i) − 15.59
```

per sentence, where W_i = words, Sy_i = syllables.

**Why LLMs trip it.** RLHF compresses readability to a Goldilocks zone, typically FKGL 9-13 with std ≈ 1.0. Human writing shows std ≈ 3-4 on matched material; technical paragraphs spike to grade 14, anecdotes drop to grade 6 (Liu et al., medRxiv 2024).

**Human reference.** Native fluent prose: FKGL std typically 3-5 across sentences. LLM outputs: typically 0.8-1.5.

**Heuristic interpretation.** FKGL std < 1.5 in any genre is a strong smoothing signal. The mean is less informative than the spread.

### 7. Adjacent-Sentence Cosine Similarity

**What it measures.** Cohesion between consecutive sentences via embedding similarity. LLMs maintain tighter topical coherence; humans digress.

**Formula.** Embed each sentence (sentence-transformers, Sentence-BERT, or TF-IDF). Compute cosine similarity for each adjacent pair. Report mean and standard deviation.

```
cos(s_i, s_{i+1}) = e(s_i) · e(s_{i+1}) / (‖e(s_i)‖ · ‖e(s_{i+1})‖)
```

**Why LLMs trip it.** LLMs maintain coherent topic context across long stretches; human prose has natural digressions, examples, and asides. Mean adjacent cosine runs higher for LLMs, and the standard deviation runs lower (consistent tightness).

**Human reference.** Mean adjacent cosine for native fiction: 0.30-0.55. LLM outputs: 0.50-0.70. Std for native fiction: 0.15-0.25. LLM outputs: 0.08-0.15.

**Heuristic interpretation.** Mean > 0.60 with std < 0.15 indicates "too tidy" cohesion. This is the Coh-Metrix signal in modern form.

### 8. Function-Word Distribution

**What it measures.** Frequencies of the top 100-200 function words (articles, prepositions, conjunctions, pronouns, modals).

**Comparison.** Cosine similarity or Burrows' Delta between document distribution and a baseline distribution.

```
Δ(X, Y) = (1/n) · Σᵢ |z_i(X) − z_i(Y)|
```

z-scored against a reference corpus, n = top-200 most frequent words. The Cosine Delta variant (Smith & Aldridge 2011, confirmed by Evert et al. DSH 2017) outperforms classical L1 Delta on long texts.

**Why LLMs trip it.** Function words are deployed below conscious authorial control, but RLHF optimizes the connective layer toward "polished" defaults: heavy use of "furthermore," "moreover," "additionally," "it is important to note," and a narrow set of preferred determiners and prepositions. Authorial idiolect (one writer's preference for "yet" over "but," another's habitual "kind of") gets smoothed away.

**Human reference.** A writer's function-word fingerprint stays remarkably stable across topics and registers. Burrows' Delta between two passages by the same author typically Δ < 0.7. Same author across years still Δ < 0.9. Different authors typically Δ > 1.2.

**Heuristic interpretation.** If the writer has a baseline corpus of their own prior work, Δ > 1.0 between baseline and current draft is a strong smoothing signal.

### 9. POS-Bigram KL Divergence

**What it measures.** Syntactic preferences encoded as part-of-speech bigram distributions. Captures patterns like DT-JJ-NN noun-phrase chains, MD-VB modal-verb usage, RB-JJ adverbial pre-modification.

**Formula.** For document distribution P and reference distribution Q:

```
KL(P‖Q) = Σ_x P(x) · log(P(x) / Q(x))
```

Or symmetric Jensen-Shannon:

```
JSD(P, Q) = ½·KL(P‖M) + ½·KL(Q‖M),  M = ½(P + Q)
```

**Why LLMs trip it.** LLMs concentrate mass on a small set of preferred syntactic templates. KL(human ‖ LLM) tends to be larger than KL(human_a ‖ human_b) in the tails of the bigram distribution. The signal is largely topic-invariant.

**Human reference.** Cross-human KL is typically small (< 0.05) on matched genres. Human-vs-LLM KL on matched genres typically 0.10-0.30.

**Heuristic interpretation.** Requires spaCy or similar POS tagger. KL > 0.15 against a human reference distribution is a meaningful signal.

### 10. Mean Dependency Distance Variance

**What it measures.** Variation in syntactic complexity across sentences, measured through dependency parse distances.

**Formulas.** For a dependency edge from head h to dependent d:

```
DD(h, d) = |pos(h) − pos(d)|
MDD(sentence) = (1/(n−1)) · Σ |DD_i|
```

over n−1 non-root edges. Report MDD per sentence; take SD across sentences.

**Why LLMs trip it.** Liu Haitao (J. Cognitive Science 2008) and Futrell, Mahowald, Gibson (PNAS 2015) established that natural-text MDD is significantly smaller than for random projective linearizations of the same dependency tree (the dependency-distance minimization principle). LLMs do not violate DDM; they cluster MDD in a narrower distribution. Lee et al. (2024) on Wikipedia simplification show human simplification drops MDD by ≈ 0.3 while ChatGPT simplification drops it by ≈ 0.03, a tenfold-smaller effect, consistent with LLMs producing pre-smoothed prose with less optimization headroom.

**Human reference.** Native fluent prose: MDD-SD across sentences typically 0.8-1.4. LLM outputs: typically 0.4-0.7.

**Heuristic interpretation.** Requires spaCy. MDD-SD < 0.7 indicates compressed syntactic variation.

### 11. Connective Density

**What it measures.** Frequency of explicit discourse markers: "furthermore," "moreover," "additionally," "in addition," "however," "therefore," "thus," "consequently," "in conclusion," "to summarize," "it is important to note," "notably," "interestingly."

**Formula.** Count occurrences from a tracked list per 1000 tokens.

**Why LLMs trip it.** RLHF rewards explicit structure. Cohesion gets glued every two or three sentences with a discourse marker, where human writing leaves gaps and trusts the reader.

**Human reference.** Fluent native prose: 5-15 explicit connectives per 1000 tokens. LLM outputs: typically 25-50.

**Heuristic interpretation.** Density > 25 per 1000 tokens is a meaningful signal. Combined with high adjacent-sentence cosine, it confirms "too tidy" cohesion.

---

## Computing the Signals

The script `ai_prose_variance_audit.py` computes all eleven signals where dependencies are available. The script handles graceful degradation:

- **Tier 1 (always works):** sentence-length stats, MATTR, MTLD, Yule's K, Shannon entropy, FKGL stats, connective density. Requires only Python + textstat + nltk.
- **Tier 2 (requires spaCy):** POS-bigram KL, MDD variance.
- **Tier 3 (requires sentence-transformers or scikit-learn):** adjacent-sentence cosine similarity. Falls back to TF-IDF cosine if no sentence embedder is available.

Output is JSON plus a human-readable summary. The script accepts an optional baseline corpus directory; with one supplied, it reports per-signal quantiles relative to the baseline. Without one, it reports absolute values that the auditor interprets against genre baselines.

The cross-chapter version (`ai_prose_manuscript_audit.py`) detects chapter boundaries and runs variance_audit logic on each chapter, producing a chapters × signals dashboard plus manuscript-wide pattern detection (signals fired on >50% of chapters) and outlier-chapter ranking.

The vocabulary-level version (`ai_prose_repetition_audit.py`) surfaces words a writer is using more than expected against a baseline, plus within-document clustering. Useful when Layer A flags lexical compression and the auditor wants specific candidates for restoration.

---

## Interpreting the Bands

The aggregate magnitude (Lightly / Moderately / Heavily smoothed) is a function of how many signals fall in the compressed band and by how much.

**Lightly smoothed.** One or two signals show meaningful compression; most signals fall in the human-reference range. Typical of human-drafted prose lightly polished by AI for grammar, with most original variance preserved. Restoration scope: targeted variance reinjection on the compressed signals.

**Moderately smoothed.** Three to five signals show meaningful compression. Sentence-length variance and FKGL std almost certainly compressed. Adjacent-sentence cosine elevated. Typical of human-drafted prose moderately revised by AI, or AI-drafted prose with light human editing. Restoration scope: variance reinjection at the document level, plus pattern-flag work at Layer B.

**Heavily smoothed.** Six or more signals show meaningful compression. Sentence-length distribution narrow, lexical diversity low, FKGL clustered tightly, function-word distribution close to LLM defaults, connective density high, adjacent-sentence cosine high with low std. Typical of fully AI-drafted prose, or human-supervised AI rewriting. Restoration scope: rebuild from the bottom up; treat the draft as outline rather than text.

These bands are calibrated against genre baselines. A literary fiction draft and a policy-brief draft can both score "Lightly smoothed" despite very different absolute statistics, because the relevant comparison is against the writer's own register.

---

## What Compressed Variance Predicts

Layer A signals predict which Layer B flags are likely to fire:

| Compressed Layer A signal | Likely Layer B flag |
|---|---|
| Sentence-length variance | AIC-3 (Echo Stack), AIC-1 (Generic Hand) |
| MATTR / MTLD / Yule's K | AIC-1, AIC-7 (Lexical Convergence subtype) |
| FKGL std | AIC-1, AIC-3 |
| Adjacent-sentence cosine high, std low | AIC-7 (Cohesion that's too tidy), AIC-2 (Velvet Fog) |
| Function-word distribution near LLM default | AIC-7 (Discourse Leak), AIC-1 |
| POS-bigram KL high | AIC-7, AIC-3 |
| MDD-SD compressed | AIC-3 (sentence-level uniformity) |
| Connective density high | AIC-7 (Cohesion-too-tidy) |

If Layer A flags compression and the predicted Layer B flags don't fire, the writer probably has unusual register conventions. Note this and run Layer C if voice attribution is supplied.

If Layer A is clean and Layer B flags fire, the smoothing is below the variance signals' detection threshold. This happens with sophisticated paraphrase or careful AI editing that preserves variance while imposing pattern.

---

## Calibration Warnings

**Genre matters.** Technical writing has tighter natural variance than literary fiction. Policy briefs run higher in connective density than essays. The genre baseline is the reference, not "human writing in general."

**Short text degrades the diagnostic.** Below 200 words, variance estimates become noisy. Below 50 words they are meaningless. Layer A is unreliable for paragraphs and short passages; use Layer B and C only.

**ESL writing.** Lower lexical diversity, lower MATTR, lower text perplexity, narrower sentence-length variance are typical of fluent non-native English. This places ESL writing in the same low-variance region as LLM output. Do not run this audit on ESL-authored text as if its compressed variance were AI provenance. Pangram's hard-negative mining on ESL corpora handles this for production detection; this audit defers to the writer's judgment about whether ESL conventions explain the signature.

**Diffusion LLMs.** Burstiness signal weakens for diffusion-based models (LLaDA). The other ten signals remain valid.

**Domain shift.** Baselines built on contemporary literary fiction will mis-calibrate for historical pastiche, experimental prose, or genre-marked work (epistolary, found-document, dialect). When the writer is working in such a register, ask for a custom baseline (their own prior work in the same register).

**Heavy paraphrase ceiling.** As paraphraser quality approaches the human distribution, all stylometric signals converge toward 0.5 AUROC (Sadasivan et al. 2023). Layer A operates well below that asymptote with current LLMs but cannot exceed it. When Layer A is clean and the writer suspects AI involvement anyway, source triage at Layer C is the remaining tool.

**Writer-specific calibration.** Some writers — those with focused vocabularies, fragment-heavy fiction styles, or essayistic long-sentence registers — produce pre-AI prose that triggers Layer A heuristic flags by absolute thresholds. Empirical observation: some pre-AI essayistic prose can register burstiness B values down to -0.40 (deep into LLM-mode-collapse territory by absolute thresholds) while being clearly human-authored. Heuristic thresholds in the variance audit have been tightened (B at -0.4 rather than -0.2; Shannon entropy threshold 7.0 with a length floor of 2000 words; sentence-length SD heuristic effectively disabled below 5000 words) so that they fire only on substantially compressed prose. For writers whose natural register sits in the suspect region, even tightened heuristics will be unreliable; the personal-baseline z-score is the operative diagnostic.

**Personal baseline z-scores tell a different story than absolute heuristics.** Empirical observation on a real writer's manuscript: against a personal pre-AI fiction baseline, an AI-assisted chapter scored multiple |z| > 1.0 in the compression direction (MATTR z ≈ -3.6, MTLD z ≈ -2.6, FKGL std z ≈ -1.3, Shannon entropy z ≈ -1.2, sentence-length SD z ≈ -1.2, connective density z ≈ +1.1). The chapter scored "Lightly smoothed" by absolute heuristics (because all values fell within the writer's natural region), but clearly compressed against the writer's own baseline. The signal exists; it requires the personal reference frame to surface.

---

## What Layer A Cannot Do

Layer A measures variance compression in the surface form. It cannot determine:

- Whether the human or the AI contributed the ideas
- Whether a flagged passage is earned (Sebald hedges as a formal strategy; the variance signals don't distinguish that from AI smoothing)
- Whether the writer's natural style happens to fall in the compressed region (some writers genuinely produce uniform sentence lengths and bland connective layers; the diagnostic flags this but cannot adjudicate it)
- Anything below 50 words

Layers B and C handle these questions. Layer A's job is to magnitude the smoothing and predict which patterns to look for.

---

## References

- Liu Haitao (2008). Dependency distance as a metric of language comprehension difficulty. *Journal of Cognitive Science* 9(2).
- Futrell, Mahowald, Gibson (2015). Large-scale evidence of dependency length minimization in 37 languages. *PNAS* 112(33).
- Tanaka-Ishii and Aihara (2015). Computational constancy measures of texts. *Computational Linguistics* 41(3).
- Reviriego et al. (2024). Beware of words: Evaluating the lexical diversity of conversational LLMs. *ACM Transactions on Intelligent Systems and Technology*.
- Muñoz-Ortiz, Gómez-Rodríguez, Vilares (2024). Contrasting linguistic patterns in human and LLM-generated news text. *Cognitive Computation*.
- Lee et al. (2024). Comparing dependency distance in human and ChatGPT-simplified texts.
- Liu et al. (2024). Readability variance in GPT-4 lay summaries. medRxiv preprint.
- Tarım and Onan (2025). Burstiness signal robustness against diffusion LLMs. arXiv 2507.10475.
- Xu and Zubiaga (2025). RLHF-induced readability mode collapse. arXiv 2503.17965.
- Sadasivan, Kumar, Balasubramanian, Wang, Feizi (2023). Can AI-generated text be reliably detected? arXiv 2303.11156.
- Evert et al. (2017). Understanding and explaining Delta measures for authorship attribution. *Digital Scholarship in the Humanities*.
- Burrows (2002). Delta: A measure of stylistic difference and a guide to likely authorship. *Literary and Linguistic Computing* 17(3).
