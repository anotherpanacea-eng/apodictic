# Field Reconnaissance — Level-Setting Research

**Status:** Research draft
**For:** APODICTIC Nonfiction Argument Engine — Field Reconnaissance research mode
**Last updated:** 2026-03-23

---

## 1. What Problem Does This Solve?

Field Reconnaissance answers: **what's out there that the manuscript doesn't address?** It scouts three things:

1. **Counterevidence** — published work that contradicts or complicates central claims
2. **Literature gaps** — structural holes in the source base (temporal, methodological, perspectival, concentration)
3. **Source ecosystem health** — dead links, retractions, preprints with published updates, predatory venues

This is distinct from citation verification (which checks whether cited sources are real and accurately represented) and from factual verification (which checks whether specific claims are true). Field Recon asks whether the manuscript is *adequately situated* in its literature.

---

## 2. Theoretical Grounding

### Counterevidence retrieval

The core challenge of counterevidence search is **relevance filtering**: the difference between finding a paper that's about the same topic and finding one that genuinely contradicts the manuscript's specific claim.

**Information retrieval literature** distinguishes between topical relevance (about the same subject) and situational relevance (useful for the specific information need). Counterevidence retrieval requires situational relevance — a paper that measures the same variable and gets a different result, not just a paper about the same broad topic.

**Argumentation theory** (Walton, 2006; van Eemeren & Grootendorst, 2004) provides the framework for identifying what counts as a counter-argument vs. merely related work. A genuine counter-argument attacks a premise, disputes evidence, or proposes an alternative explanation for the same phenomenon. Tangentially related work in a different framework is not counterevidence.

**Adversarial reading** (related to APODICTIC's Red Team module) generates counterarguments from the manuscript itself. Field Recon's job is different: it finds *external* counterevidence that exists in the published literature. The Red Team constructs the strongest possible objection; Field Recon finds the strongest published objection.

### Literature gap detection

**Bibliometric analysis** provides quantitative methods for assessing source base adequacy:

- **Temporal distribution:** Publication-year histograms reveal whether the source base is current for the field's pace of change. Waltman et al. (2011) established methods for field-normalized citation analysis that inform appropriate currency thresholds by discipline.

- **Methodological diversity:** Mixed-methods research methodology (Creswell & Plano Clark, 2018) provides frameworks for assessing whether a question that warrants multiple methodological approaches has been supported by evidence from multiple approaches.

- **Geographic and perspectival coverage:** Epistemic justice literature (Fricker, 2007; Dotson, 2011) provides theoretical grounding for why perspectival gaps matter — not just as diversity concerns but as epistemic failures that can systematically distort conclusions.

- **Source concentration:** Bibliometric coupling and co-citation analysis (Kessler, 1963; Small, 1973) provide methods for understanding whether a source base represents genuinely independent evidence or a narrow cluster of mutually-citing work.

### Source ecosystem health

**Retraction analysis** (Fang et al., 2012) documented the scope of retraction problems in scientific literature. The Retraction Watch database provides a practical resource for checking cited sources.

**Link rot** (Zittrain et al., 2014, "Perma") documented that ~50% of URLs in Supreme Court opinions were dead within a decade. For any manuscript with web citations, dead link checking is maintenance, not optional.

**Predatory publishing** (Beall's criteria, now maintained in various forms) provides indicators for venues that lack meaningful peer review. Citing predatory journals undermines evidence credibility even if the specific paper is sound.

---

## 3. Landscape Analysis

### Literature discovery and gap analysis tools

| Tool | What it does | Relevance to Field Recon |
|------|-------------|--------------------------|
| **Litmaps** (merged with Research Rabbit) | Citation network visualization, chronological mapping | Discovery tool, not gap assessment. But its ability to overlay maps from different subjects informs interdisciplinary gap detection. |
| **Connected Papers** | Co-citation network clustering | Finds related work the author may have missed. Could inform gap detection by revealing influential uncited papers. |
| **Inciteful** | PageRank-based paper discovery + Literature Connector (bridging two domains) | PageRank ranking is more sophisticated than APODICTIC's "citation count x recency x relevance." Literature Connector maps interdisciplinary bridging. |
| **Elicit** | LLM-based structured literature review | Structured data extraction from papers. Different job (synthesis vs. gap detection) but extraction methodology could inform how counterevidence is presented. |
| **Consensus.app** | Answers research questions by synthesizing findings across studies | "Consensus meter" showing degree of agreement is conceptually related to counterevidence density. |
| **Perplexity (Academic)** | Search with academic filter | Tow Center study found ~37% error rate in source attribution. Validates APODICTIC's design to be honest about confidence levels. |

### Key insight from the landscape

**No existing tool combines counterevidence search, gap detection, and ecosystem health assessment in a single integrated workflow.** Each tool does one piece:

- Litmaps/Connected Papers/Inciteful do *discovery* (find papers you haven't seen)
- Consensus/Elicit do *synthesis* (summarize what papers say)
- Retraction Watch does *health checking* (identify compromised sources)
- Nothing does *counterevidence retrieval calibrated to a specific argument's claim hierarchy*

APODICTIC's Field Recon spec occupies a genuine gap in the landscape. The risk is that it tries to do too much in one module — but the three components (counterevidence, gaps, ecosystem health) share enough infrastructure (API calls, citation inventory parsing) that combining them is efficient.

---

## 4. Counterevidence Retrieval: Methodological Challenges

### The relevance filtering problem

The spec acknowledges this is "the hardest part of the module." The research confirms this assessment. Challenges:

1. **Same topic ≠ same question.** A paper about criminal justice reform and a paper about criminal justice reform may address completely different variables, populations, or mechanisms. Topic-level search returns noise.

2. **Definitional divergence.** Two papers may reach opposite conclusions because they define the key term differently. This is not counterevidence — it's a different conversation. The spec correctly notes this as "not counterevidence (do not surface)" but the LLM needs to detect definitional divergence, which is hard.

3. **Disciplinary framing.** A sociological study and an economic study may address the same phenomenon from incompatible theoretical frameworks. Whether this counts as counterevidence depends on the manuscript's own framing.

4. **Publication bias.** Published counterevidence is biased toward statistically significant results. The absence of counterevidence may reflect publication bias rather than genuine consensus.

### Suggested improvements to search strategy

The spec's current search uses three query variants (direct negation, replication failure, meta-analysis) per claim. Research suggests:

1. **Add synonym expansion.** Academic fields use different terminology for the same concept. A search for "recidivism" may miss relevant papers indexed under "reoffending," "criminal desistance," or "post-release outcomes."

2. **Use OpenAlex's concept hierarchy.** OpenAlex assigns hierarchical concepts to papers. Searching by concept ID rather than keyword can capture terminological variation.

3. **Consider citation network traversal.** Papers that cite the manuscript's sources but reach different conclusions are strong counterevidence candidates. Connected Papers' co-citation methodology does this well.

4. **Add a "consensus check" step.** Before searching for counterevidence on a specific claim, check whether the claim represents established consensus or an active debate. If consensus, counterevidence search is less useful (the manuscript isn't claiming anything controversial). If active debate, counterevidence search is essential.

---

## 5. Gap Detection: Calibration Challenges

### Temporal gaps

The spec's thresholds (fast-moving: >30% older than 5 years; moderate: >40% older than 10 years; slow-moving: no threshold) are reasonable starting points but need field-level calibration.

**Problem:** The categories "fast-moving" and "slow-moving" are themselves subjective. Criminal justice policy is fast-moving in some respects (sentencing reform) and slow-moving in others (constitutional principles). The verifier needs to infer field speed from the manuscript's sources, not from the topic label.

**Suggestion:** Use the median publication year of the manuscript's own sources as a baseline. If the median is 2015 and the field's literature has a median of 2022, the source base is potentially stale. This is a relative measure, not an absolute threshold.

### Methodological gaps

The spec asks: "All theoretical, no empirical? Or vice versa?" This is a useful heuristic but needs refinement. Some arguments are properly supported by theoretical work alone (philosophical arguments, legal analysis). Others require empirical evidence (policy claims, causal claims). The form and claim type should determine what counts as a methodological gap.

### Perspectival gaps

The spec checks for geographic skew and demographic representation. This is important but risks false positives. An argument about DC juvenile justice policy is not weakened by citing only US sources. An argument about universal human behavior *is* weakened by citing only Western samples. The scope of the claim determines whether perspectival limitation is a gap or appropriate focus.

### Source concentration

The spec flags when any single author is cited more than 3 times or any section draws >50% of claims from one source. These are useful signals but need context. A literature review of Author X's body of work will naturally cite them heavily. A section summarizing a single landmark study will naturally draw heavily from it. Concentration is only a problem when it disguises narrow evidence as broad consensus.

---

## 6. Source Ecosystem Health: Practical Considerations

### Dead links

Link rot rates vary by domain:
- Government URLs (.gov) have moderate rot (~20% within 5 years, per studies of Supreme Court citations)
- Academic publisher URLs are relatively stable (DOI system was designed for persistence)
- News media URLs have high rot (~40% within 5 years)
- Personal/blog URLs have the highest rot

The spec's approach (check URL, fall back to Wayback Machine) is correct. One addition: for government sources, check whether the content has moved to a new URL (common during administration transitions) rather than disappeared entirely.

### Retracted sources

Retraction checking via CrossRef metadata ("update-to" or "retracted-article" relations) catches formally retracted papers. But "expressions of concern," corrections, and partial retractions are harder to detect and arguably more common. The spec should note that retraction checking catches the worst cases but not all problematic sources.

### Predatory venues

Detecting predatory venues is itself a contested practice. Beall's List was taken down; its successors are incomplete. APODICTIC should use conservative indicators:
- Journal not indexed in major databases (Scopus, Web of Science, PubMed)
- Publisher on known predatory lists (Cabells, Stop Predatory Journals)
- No documented peer review process

But it should also note that absence from major indexes doesn't automatically mean predatory — many legitimate regional, specialized, or open-access journals aren't indexed everywhere.

---

## 7. False-Positive Risks

| Component | False-positive risk | Mitigation |
|-----------|-------------------|------------|
| Counterevidence | Surfacing tangentially related work as "contradictions" | Strict relevance filtering: same question, same variable, same population |
| Temporal gaps | Flagging appropriate use of foundational sources as "stale" | Distinguish timeless contributions from time-sensitive findings |
| Methodological gaps | Flagging appropriate theoretical arguments as "lacking empirical support" | Calibrate by claim type: normative claims don't need empirical support |
| Perspectival gaps | Flagging appropriate geographic focus as "limited perspective" | Calibrate by claim scope: local claims warrant local sources |
| Source concentration | Flagging appropriate deep engagement with key works as "over-reliance" | Calibrate by intent: literature review vs. original argument |
| Predatory venue flags | Flagging legitimate non-indexed journals as "predatory" | Use conservative indicators; note uncertainty |
| Dead links | Treating all dead links as credibility problems | Dead links are maintenance issues, not argument failures |

---

## 8. Relationship to Red Team

Field Recon and Red Team both generate challenges to the manuscript, but from different directions:

| | Red Team | Field Recon |
|--|---------|-------------|
| **Source of challenge** | Internal (constructed from the argument itself) | External (found in published literature) |
| **Strongest objection** | The best argument a hostile reader could construct | The best published evidence against the claim |
| **When to run** | After Dialectical Clarity, to stress-test the argument | After Evidence or Citation Verifier, to scout the literature |
| **Output** | Red_Team_Memo.md with vulnerability ranking | Field_Reconnaissance_Report.md with counterevidence and gaps |

The two modules are complementary. Red Team may construct an objection that Field Recon can then check for published support ("is there evidence for this hypothetical objection?"). Field Recon may surface counterevidence that Red Team can then use to construct a stronger attack.

**Important boundary:** Field Recon surfaces what exists. Red Team constructs the strongest possible case. Field Recon should never editorialize about whether the counterevidence is "devastating" or "minor" — it rates strength (HIGH/MEDIUM/LOW) and recommends action (ADDRESS/ACKNOWLEDGE/SET ASIDE), but the author decides how to respond.

---

## 9. Unsettled Design Questions

1. **Should Field Recon always require Citation Verifier to have run first?** The spec allows standalone mode (it'll parse the citation surface itself). But the quality of gap detection depends on having an accurate citation inventory. Running without the Citation Ledger means re-doing citation extraction less thoroughly.

2. **How aggressive should counterevidence search be?** The spec caps at 3-5 queries per claim. But a claim in an active debate might need deeper search, while a claim in an established consensus needs none. Adaptive search depth would be better than a fixed cap.

3. **What's the right citation count threshold for counterevidence quality?** The spec uses ≥10 citations as a rough quality filter. But this biases toward established work and against recent findings. In fast-moving fields, important counterevidence may have <10 citations because it's new.

4. **Should ecosystem health checking run on every citation or only on load-bearing ones?** A dead link in a passing citation is low-priority maintenance. A dead link in a load-bearing citation is a credibility problem. The spec currently checks all citations equally.

5. **How should the module handle counterevidence that the author has already considered and rejected?** If the manuscript acknowledges and addresses a counterargument, surfacing the published version is helpful (the author may want to cite it). But the action recommendation should be different from counterevidence the author hasn't considered.

---

## 10. Positive Cases

### What good literature situating looks like

**Strong counterevidence handling:** The manuscript acknowledges the strongest published challenge to its central claim, engages with it substantively (not dismissively), and explains why its position is still warranted despite the counterevidence.

**Strong source ecosystem:** All links work. No cited sources have been retracted. Preprints have been updated to published versions where available. Publication venues are credible and appropriate for the manuscript's audience.

**Strong temporal coverage:** The source base includes foundational work (showing the author knows the field's history) and recent work (showing the author is current). The balance is appropriate to the field's pace of change.

**Strong perspectival coverage:** The scope of cited evidence matches the scope of claims. Universal claims cite diverse evidence. Local claims cite local evidence without claiming universality.

---

## 11. References

### Theoretical grounding
- Walton, D. (2006). *Fundamentals of Critical Argumentation.* Cambridge University Press.
- van Eemeren, F. H., & Grootendorst, R. (2004). *A Systematic Theory of Argumentation.* Cambridge University Press.
- Fricker, M. (2007). *Epistemic Injustice.* Oxford University Press.
- Dotson, K. (2011). "Tracking Epistemic Violence, Tracking Practices of Silencing." *Hypatia*, 26(2).
- Creswell, J. W., & Plano Clark, V. L. (2018). *Designing and Conducting Mixed Methods Research.* 3rd ed.

### Bibliometrics and citation analysis
- Kessler, M. M. (1963). "Bibliographic coupling between scientific papers." *American Documentation*, 14(1).
- Small, H. (1973). "Co-citation in the scientific literature." *Journal of the American Society for Information Science*, 24(4).
- Waltman, L., van Eck, N. J., & Wouters, P. (2011). "Towards a new crown indicator." *Journal of Informetrics*, 5(1).

### Source ecosystem
- Fang, F. C., Steen, R. G., & Casadevall, A. (2012). "Misconduct accounts for the majority of retracted scientific publications." *PNAS*, 109(42).
- Zittrain, J., Albert, K., & Lessig, L. (2014). "Perma: Scoping and Addressing the Problem of Link and Reference Rot in Legal Citations." *Harvard Law Review Forum*, 127.

### Tools examined
- Litmaps (merged with Research Rabbit): litmaps.com
- Connected Papers: connectedpapers.com
- Inciteful: inciteful.xyz
- Elicit: elicit.com
- Consensus: consensus.app
- Retraction Watch database
