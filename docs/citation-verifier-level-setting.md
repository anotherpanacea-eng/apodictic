# Citation Verifier — Level-Setting Research

**Status:** Research draft
**For:** APODICTIC Nonfiction Argument Engine — Citation Verification module
**Last updated:** 2026-03-23

---

## 1. What Problem Does This Solve?

Citation verification answers a narrow question: **do the sources you cite actually support what you're saying?** This is distinct from:

- **Argument structure** (Dialectical Clarity) — whether the argument is logically sound
- **Evidence structure** (Argument Evidence) — whether the evidence portfolio is balanced and properly weighted
- **Factual accuracy** (Factual Verification) — whether uncited claims are true
- **Literature adequacy** (Field Reconnaissance) — whether the source base is complete

The verification gap exists because writers — and especially AI-assisted writers — routinely produce citations that look correct but fail under inspection. A citation can exist, be accurately formatted, and still misrepresent its source.

---

## 2. Theoretical Grounding

### Citation-claim alignment

The core theoretical problem is **citation-claim fit**: the relationship between what a source says and what a manuscript claims it says. This is not a binary (correct/incorrect) but a spectrum with identifiable failure modes.

Greenberg (2009) showed that citation chains in biomedical literature systematically distort claims through successive paraphrasing. A hedged finding ("may contribute to") becomes certain ("causes") within 3-4 citation hops. This "citation mutation" is the empirical basis for APODICTIC's hedge fidelity analysis.

Simkin & Roychowdhury (2005) estimated that 70-90% of citations in physics papers were copied from reference lists without consulting the cited paper. While the specific percentage is contested, the phenomenon — citing sources you haven't read — is well-documented across fields.

### Verification methodology in existing systems

**SemanticCite** (arxiv 2511.16198) provides the most directly relevant academic framework. It uses a four-stage pipeline:

1. Text preprocessing — extract citations and claims
2. Hybrid retrieval — combine dense and sparse retrieval to find source text
3. Neural reranking — score retrieved passages by relevance to the claim
4. LLM-based analysis — classify the citation-claim relationship

SemanticCite outputs four verdicts: Supported, Partially Supported, Unsupported, Uncertain. APODICTIC's seven-verdict set adds editorial nuance: SUPPORTED WITH CAVEAT, MISREPRESENTED, OUTDATED, and NEEDS EXPERT REVIEW capture distinctions that matter for editorial repair but not for bibliometric analysis.

**Key methodological insight from SemanticCite:** hybrid retrieval (combining dense semantic search with sparse keyword matching, followed by neural reranking) significantly outperforms sequential API fallback. APODICTIC's current spec uses a sequential chain (CrossRef → Semantic Scholar → OpenAlex → Wayback). This works for *existence verification* but may underperform for *content retrieval* when source text is needed for quote/paraphrase checking.

**CiteAudit** (arxiv 2602.23452, checkcitation.com) uses a multi-agent pipeline: claim extraction agent, evidence retrieval agent, passage matching agent, reasoning agent, and calibrated judgment agent. The multi-agent architecture is relevant because APODICTIC already uses subagent parallelism within passes. CiteAudit's human-validated dataset could serve as a benchmark for APODICTIC's verdict accuracy.

**Loki / OpenFactVerification** (MIT-licensed, ACL 2025) demonstrates a five-step pipeline closest to APODICTIC's design: decompose → assess worthiness → generate queries → retrieve evidence → verify. Loki's explicit human-in-the-loop philosophy matches APODICTIC's guardrail that research supplements author knowledge rather than overriding judgment.

### Hedge detection

The hedge fidelity patterns in the APODICTIC spec (certainty inflation, population inflation, geographic inflation, temporal inflation, precision inflation, deflation) are grounded in a well-established NLP subfield.

The CoNLL-2010 Shared Task established benchmark evaluation for hedge detection in biomedical text. More recent work (arxiv 2405.13319, "You should probably read this: Hedge Detection in Text," 2024) surveys transformer-based approaches to detecting uncertainty language (modal verbs, peacock expressions, weasel words).

APODICTIC's innovation is applying hedge detection not to the manuscript's own hedging, but to the *gap between source hedging and manuscript hedging*. This is a comparison task, not a detection task. No existing tool does this systematically.

### Citation fabrication and hallucination

GPTZero's Source Checker and RefChecker (open source) both target the specific problem of AI-generated citation hallucination. RefChecker validates references against the same API stack APODICTIC uses (Semantic Scholar, OpenAlex, CrossRef), confirming the API choice is well-validated by the landscape.

The Citation-Hallucination-Detection repo (Vikranth3140) adds an important capability APODICTIC's spec currently lacks: **fuzzy matching** for metadata resolution. Citations in manuscripts are often imprecise — misspelled author names, approximate titles, wrong years. A fuzzy matching layer between the manuscript's citation string and the API response would improve resolution rates.

---

## 3. Landscape Analysis

### What exists and what it does

| Tool | What it does | Open? | Relevance |
|------|-------------|-------|-----------|
| **Scite.ai** | Classifies citation intent (supporting/contrasting/mentioning) across 1.6B citations | No | Simpler verdicts; massive scale APODICTIC can't replicate |
| **SemanticCite** | 4-stage verification pipeline, 4-class output | Paper published | Most relevant academic methodology |
| **CiteAudit** | Multi-agent pipeline with calibrated judgment | Paper + web demo | Human-validated dataset useful for benchmarking |
| **RefChecker** | Validates references against CrossRef/Semantic Scholar/OpenAlex | Open source | Validates APODICTIC's API choice |
| **Citation-Hallucination-Detection** | Hybrid pipeline with fuzzy matching | Open source | Fuzzy matching methodology worth adopting |
| **RefCheckAI** (Sydney Informatics Hub) | Custom model comparing citation statements to source texts | Open source | Content verification methodology |
| **Citely.ai** | 95%+ accuracy on authentic vs. fabricated citations | No | Existence verification only (CV1 scope) |
| **GPTZero Source Checker** | Detects hallucinated sources and poorly supported claims | No | Claim detection methodology |
| **Writefull Cite** | Identifies sentences that should have a citation but don't | No | Validates APODICTIC's architecture split (this is Evidence's job, not Verifier's) |
| **Loki** | 5-step fact verification pipeline, human-in-the-loop | MIT license | Closest architectural parallel |

### What APODICTIC adds that nothing else does

1. **Argument-aware prioritization.** No other tool maps citations to a claim hierarchy (C0, subclaims, support nodes) before deciding which to verify first. Every other tool verifies in document order or by some generic importance metric.

2. **Form-calibrated standards.** No other tool adjusts verification stringency by manuscript type. An op-ed has different citation norms than an academic article. APODICTIC's form calibration table addresses this.

3. **Hedge fidelity comparison.** The systematic comparison of source hedging vs. manuscript hedging is not implemented in any tool found. Hedge *detection* is well-studied; hedge *comparison across citation boundaries* is novel.

4. **Seven-verdict editorial granularity.** Most tools use 3-4 categories. APODICTIC's additional verdicts (SUPPORTED WITH CAVEAT, MISREPRESENTED, OUTDATED, NEEDS EXPERT REVIEW) add editorial nuance needed for revision guidance.

5. **Integration with a full argument engine.** No other citation tool consumes a shared argument state and writes back into it. The Citation Verifier is a module in a composable system, not a standalone checker.

---

## 4. API Infrastructure Assessment

### Current status (tested March 2026)

| API | Status | Auth required? | Notes |
|-----|--------|---------------|-------|
| CrossRef | Working | No (mailto recommended) | Stable. Polite pool with mailto. |
| **Semantic Scholar** | **Rate-limited** | **Free API key now effectively required** | Returns 429 without key from shared IPs |
| OpenAlex | Working | No (mailto recommended) | Stable. 260M+ records, CC0 license. |
| Unpaywall | Working | No key, but **rejects fake emails** | Stricter email validation than before |
| PubMed | Working | No (3 req/sec; 10/sec with free key) | Unchanged |
| Wayback Machine | Working | No | Unchanged |

### Changes needed in spec

1. Add note: Semantic Scholar now effectively requires a free API key for reliable use. Register at semanticscholar.org/product/api.
2. Add note: Unpaywall requires a legitimate email address (not test@example.com).
3. Consider adding: OpenAlex now offers a free API key (100K credits/day) for higher rate limits, though unauthenticated access still works.

### Resolution strategy assessment

The spec's sequential fallback chain (DOI → CrossRef → Semantic Scholar → OpenAlex → Wayback) is adequate for **existence verification** (is this source real?). But for **content verification** (does the source support the claim?), the chain needs access to source text, not just metadata.

The realistic access hierarchy:
- **Full text available:** OA papers (via Unpaywall), government/institutional reports (direct URL fetch), blog posts and web content (direct URL fetch)
- **Abstract only:** Most paywalled journal articles (via API metadata)
- **Metadata only:** Books, older papers, institutional reports behind login walls
- **Unretrievable:** Sources with insufficient metadata, dead links without Wayback copies

The spec correctly handles this with its four confidence levels. The gap is that the spec doesn't specify how to maximize full-text access. Adding Unpaywall as an early step in the resolution sequence (check for OA PDF before falling back to abstract-only) would improve content verification rates.

---

## 5. Failure Taxonomy

### Citation-level failures

| Failure mode | Code | Frequency | Detection difficulty |
|-------------|------|-----------|---------------------|
| Ghost citation (source doesn't exist) | CV1 | Elevated with AI drafting; rare in human-written | Easy — API resolution |
| Dead link | CV2 | Common in web-heavy work | Easy — URL fetch |
| Metadata gap (can't resolve) | CV3 | Moderate | Easy — resolution failure |
| Quote drift (misquotation) | CV4 | Common | Hard — requires source text |
| Paraphrase inflation | CV5 | Very common | Hard — requires hedge comparison |
| Scope lift (overgeneralization) | CV6 | Very common | Hard — requires source context |
| Secondary laundering | CV7 | Common in policy writing | Medium — requires provenance tracing |
| Authority mask | CV8 | Common in op-eds | Medium — requires argumentative judgment |
| Currency mismatch | CV9 | Common in fast-moving fields | Easy — date comparison |
| Unsupported statistic | CV10 | Common | Medium — requires method tracing |
| Citation padding | CV11 | Moderate | Medium — requires cluster analysis |
| Hotspot cluster | CV12 | Rare but high-impact | Hard — requires cross-citation pattern recognition |

### Key observation

The easy-to-detect failures (CV1, CV2, CV3, CV9) are the ones existing tools already catch well. The hard-to-detect failures (CV4, CV5, CV6, CV7, CV8) are where APODICTIC's editorial judgment layer adds value. These failures require reading the source, understanding what it actually says, and comparing that to what the manuscript claims — tasks that depend on LLM comprehension, not API lookup.

This suggests the module should be designed as two phases:
1. **Automated resolution phase** — API-based existence and metadata verification (catches CV1-CV3, CV9)
2. **Editorial verification phase** — LLM-based content comparison for citations where source text is accessible (catches CV4-CV8, CV10-CV12)

---

## 6. False-Positive Risks by Form

| Form | Likely false positives | Why |
|------|----------------------|-----|
| Op-ed | CV8 (Authority Mask) | Op-eds legitimately invoke authority for brevity. Not every name-drop is a mask. |
| Testimony | CV10 (Unsupported Statistic) | Oral testimony conventions differ from written. Statistics may be sourced in supporting documents not in the transcript. |
| Academic article | CV5 (Paraphrase Inflation) | Disciplinary conventions allow compressed paraphrase that looks like inflation but is understood by the audience. |
| Blog post | CV2 (Dead Link) | Web links die. A dead link is maintenance, not a credibility failure. |
| Memoir/CNF | CV4 (Quote Drift) | Memory-based quotes are not meant as verbatim transcription. Flagging them as "drift" misunderstands the form. |
| Policy brief | CV7 (Secondary Laundering) | Policy writing legitimately cites secondary analyses of government data. The secondary source is the interpretive contribution. |

### Calibration principle

The verifier should adjust thresholds by form, not apply academic-article standards to every manuscript type. The form calibration table in the spec addresses this, but the level-setting research reveals that the *false-positive risk* is as important as the *detection sensitivity*. A citation verifier that over-flags legitimate form conventions will lose author trust.

---

## 7. Unsettled Design Questions

1. **Should the verifier run standalone or always require Argument_State.md?** The current spec allows standalone mode with "lower-confidence prioritization." But standalone mode means verifying in document order without knowing which citations are argumentatively central. This may produce a ledger that's accurate but unhelpful — flagging a passing citation while missing a load-bearing one.

2. **How should fuzzy matching work?** The Citation-Hallucination-Detection repo shows that metadata variations (misspellings, format differences, partial titles) are common. The spec doesn't specify a fuzzy matching threshold. Options: Levenshtein distance on title strings, cosine similarity on title embeddings, or delegating to the APIs' built-in fuzzy search.

3. **What about non-English sources?** The API stack is English-heavy. OpenAlex has broader international coverage, but quote/paraphrase verification of non-English sources requires language-specific LLM capability. The spec is silent on this.

4. **How to handle self-citation?** Self-citation is common and often legitimate. But it creates a verification gap: the author knows what their own earlier work says, so they may paraphrase from memory rather than re-reading. The verifier should check self-citations with the same rigor but interpret them differently.

5. **Token budget for content verification.** The spec estimates 20-50K tokens total. But content verification of a 30-citation academic article where 15 have accessible full text could easily consume 50K+ tokens just in source reading. The budget may need to distinguish between "quick verification" (existence + metadata) and "deep verification" (content comparison).

---

## 8. Positive Cases

### What good citation practice looks like

**Strong citation-claim alignment (academic):** Each claim is supported by a source that directly addresses it. Hedging in the manuscript matches hedging in the source. Scope of the claim matches scope of the evidence.

**Strong citation practice in policy writing:** Government data cited to primary source (not secondary analysis). Statistics include method, denominator, and timeframe. Legal citations include specific sections, not just case names.

**Strong citation practice in op-eds:** Few citations, but each one carries weight. The cited source is the strongest available authority for the specific claim. No padding — every citation does work.

**Strong citation practice in testimony:** External factual claims are sourced. Personal experience and observation are clearly distinguished from cited evidence. Statistics come with traceable methodology even if citations are sparse.

---

## 9. Cross-Form Success Signals

These markers indicate citation integrity regardless of form:

1. **Hedge fidelity** — source hedging is preserved in the manuscript's characterization
2. **Scope discipline** — claims don't extend beyond what their sources warrant
3. **Provenance transparency** — the reader can trace any claim back to its origin
4. **Recency awareness** — time-sensitive claims use current sources; timeless claims cite foundational work
5. **Load-bearing clarity** — the reader can tell which citations are doing argumentative work and which are background

---

## 10. References

### Academic papers
- Greenberg, S. A. (2009). "How citation distortions create unfounded authority." *BMJ*, 339, b2680.
- Simkin, M. V., & Roychowdhury, V. P. (2005). "Stochastic modeling of citation slips." *Scientometrics*, 62(3), 367-384.
- SemanticCite (2025). arxiv 2511.16198. Four-stage citation verification pipeline.
- CiteAudit (2026). arxiv 2602.23452. Multi-agent verification pipeline.
- Loki / OpenFactVerification (2025). ACL 2025 Demos. Five-step fact verification.
- CiteME (2024). NeurIPS 2024. Benchmark for citation attribution by LLMs.
- "Assessing citation integrity in biomedical publications" (2024). *Bioinformatics*, 40(7).
- "You should probably read this: Hedge Detection in Text" (2024). arxiv 2405.13319.
- CoNLL-2010 Shared Task. Hedge detection benchmark.

### Open-source implementations
- RefChecker: github.com/markrussinovich/refchecker
- Citation-Hallucination-Detection: github.com/Vikranth3140/Citation-Hallucination-Detection
- RefCheckAI: github.com/Sydney-Informatics-Hub/RefCheckAI
- Loki: github.com/Libr-AI/OpenFactVerification

### Tools examined
- Scite.ai — citation intent classification
- Citely.ai — citation authenticity verification
- GPTZero Source Checker — hallucinated source detection
- Writefull Cite — missing citation detection
- Recite — citation format checking (not relevant to APODICTIC's scope)
