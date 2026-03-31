# Research Mode: Field Reconnaissance (v1.0)
*Revised: March 23, 2026*
*Status: Revised spec — incorporates level-setting research (OpenScholar, PhilLit, Litmaps, Inciteful)*
*Standalone-capable: Yes — runs with or without Argument_State.md and Citation_Ledger.md*

## Purpose

Scout the literature around a manuscript's claims for counterevidence, gaps, and ecosystem health. This is not verification (that's the Citation Verifier) and not fact-checking (that's Factual Verification). This module asks: **what's out there that the manuscript doesn't address?**

Three jobs:

1. **Counterevidence**: find published work that contradicts or complicates the manuscript's central claims
2. **Literature gaps**: identify structural gaps in the manuscript's source base (temporal, methodological, perspectival, concentration)
3. **Source ecosystem health**: assess the overall condition of the evidentiary infrastructure (dead links, retractions, preprints, predatory venues)

**When to activate:**
- After Citation Verifier fires CV12 (Hotspot Cluster) and the argument needs a broader literature check
- When Argument Evidence fires AE3 (Portfolio Narrowness) or AE4 (Representative Gap)
- When Red Team fires RT9 (Evidence Chain Snap) or RT11 (Standing and Scope Exposure)
- User asks: "What am I missing?" / "What would a hostile reviewer cite against me?" / "Is my source base adequate?"
- The manuscript makes claims in a fast-moving field where the literature may have shifted since drafting
- Before submitting for peer review, publication, or testimony

**Core principle:** The goal is to arm the author, not to undermine them. Counterevidence is a service: a manuscript that anticipates objections is stronger than one that ignores them. Gaps are opportunities, not failures.

---

## Part 1: Counterevidence Search

For each load-bearing claim (C0 and central subclaims from `Argument_State.md`, or the strongest claims identified during Citation Verifier's run, or inferred from the manuscript if running standalone):

### Search strategy

*Revised to incorporate OpenScholar's self-feedback loop, PhilLit's domain-adaptive hierarchy, and keyword extraction.*

```
1. Extract the claim's core proposition
2. Generate keyword variants (LLM generates 3-5 search-term variants
   capturing terminological variation, synonyms, and disciplinary
   framing differences — e.g., "recidivism" → also "reoffending,"
   "criminal desistance," "post-release outcomes")
3. Generate query variants per keyword set:
   a. Direct negation: "{keywords} contradicts OR challenges OR refutes"
   b. Replication: "{keywords} replication failure OR failed to replicate"
   c. Meta-analysis: "{keywords} meta-analysis OR systematic review"

4. Search domain-priority APIs first:
   | Domain | Start with | Then |
   |--------|-----------|------|
   | Philosophy | PhilPapers (via web search), SEP/IEP | Semantic Scholar, OpenAlex, CORE |
   | Biomedical | PubMed, Semantic Scholar | OpenAlex, CORE |
   | Policy / legal | Government databases, institutional reports | Semantic Scholar, OpenAlex |
   | Social science | Semantic Scholar, OpenAlex | CORE |
   | General | Semantic Scholar, OpenAlex | CORE, web fallback |

5. Citation chain traversal (via Semantic Scholar citations API):
   For each of the manuscript's load-bearing cited sources:
   - Check papers that cite the same source but reach different conclusions
   - Check papers cited BY the manuscript's sources that the manuscript doesn't cite
   (These are strong counterevidence candidates because they're in direct conversation)

6. Filter results:
   REQUIRED (hard gates):
   a. Directly addresses the same question (not merely the same topic)
   b. Not already cited in the manuscript

   SOFT SIGNALS (inform ranking, do not filter):
   c. Published in a peer-reviewed venue or credible institutional source
   d. Citation count (any level — do not use citation counts as a filter;
      philosophy books, court opinions, government reports, and recent work
      may have zero database citations and still be the strongest counterevidence)
   e. Recency (within 10 years preferred, but foundational older work included
      if directly relevant)

7. Rank by: relevance to specific claim (PRIMARY gate), then:
   - venue credibility as tiebreaker
   - citation count as optional confidence signal (not a filter)
   - recency as optional signal
   Cap at 3 results per source paper to prevent over-representation.

8. Self-feedback loop (learned from OpenScholar):
   After initial results, generate 2-3 self-feedback sentences:
   - "What claims did I not find counterevidence for?"
   - "What perspectives or methodologies are missing from results?"
   - "Are there disciplinary framings I haven't searched?"
   Each feedback item triggers a new targeted search.
   Loop terminates when: (a) no new relevant results found, or
   (b) all load-bearing claims have been checked, or
   (c) 3 feedback iterations reached.

9. Return top 3-5 per claim after all iterations.
```

### Relevance filtering

This is the hardest part of the module. The difference between useful counterevidence and noise is whether the found paper addresses the *same question* as the manuscript's claim.

**Relevant counterevidence:**
- Paper that measures the same variable and gets a different result
- Paper that examines the same mechanism and finds it doesn't hold
- Paper that studies the same population/context and reaches opposing conclusions
- Meta-analysis that contradicts a finding the manuscript treats as settled

**Not counterevidence (do not surface):**
- Paper about the same broad topic that doesn't address the specific claim
- Paper that uses different definitions and therefore reaches different conclusions (note as definitional divergence, not as contradiction)
- Paper from a fundamentally different disciplinary frame that isn't in conversation with the manuscript's sources

When relevance is ambiguous, include the result with a note: "Possibly relevant — addresses [related question] rather than [manuscript's specific claim]." Let the author decide.

### Output per claim

```
COUNTEREVIDENCE: [Manuscript claim, truncated]
Location: [section/paragraph in manuscript]
Load: [load-bearing / supporting / passing]

Found: [N] potentially relevant items

1. [Author(s)] ([Year]). "[Title]." [Venue]. [Citations] citations.
   Relevance: [1 sentence — why this challenges the claim]
   Strength: [HIGH / MEDIUM / LOW — based on citations, venue, recency]
   Action: [ADDRESS / ACKNOWLEDGE / SET ASIDE — recommendation]

2. ...

No counterevidence found: [if search returned 0 relevant results, say so]
```

### Action recommendations

| Recommendation | When to use |
|---|---|
| `ADDRESS` | Strong counterevidence (high citations, credible venue, directly on point). The manuscript should engage with this work. |
| `ACKNOWLEDGE` | Moderate counterevidence. A footnote or brief mention would strengthen the manuscript. Ignoring it is defensible but risky. |
| `SET ASIDE` | Weak or tangential counterevidence. The author should know it exists but doesn't need to address it. |

---

## Part 2: Literature Gap Detection

Scan the manuscript's overall source base for structural gaps. This analysis uses the full citation inventory (from Citation Verifier's `Citation_Ledger.md` if available, or parsed independently).

### Temporal gaps

```
Compute:
- Median publication year of all cited sources
- Distribution by decade or 5-year band
- Percentage of sources older than threshold (see below)

Thresholds by field speed:
  Fast-moving (criminal justice policy, AI, tech, public health): >30% older than 5 years → flag
  Moderate (social science, political philosophy, education): >40% older than 10 years → flag
  Slow-moving (history, classical philosophy, literary theory): no temporal flag

Field speed: infer from manuscript's discipline and venue of cited sources.

Output:
  Median source year: {YYYY}
  Age distribution: {histogram or summary}
  Temporal flags: {list, or "none"}
  Recent work possibly missed: {list from counterevidence search, if any}
```

### Methodological gaps

Ask:
1. All theoretical, no empirical? Or vice versa?
2. All quantitative, no qualitative? Or vice versa?
3. All from one disciplinary tradition?
4. No synthesis work (reviews, meta-analyses) in a field where synthesis exists?

```
Output:
  Evidence types cited: {list with counts}
  Methodological skew: {description, or "balanced"}
  Gap: {specific suggestion if skewed — e.g., "The manuscript cites 12 sociological
        studies and 0 legal scholarship on this question."}
```

### Perspectival gaps

Check:
1. Geographic skew: all US/EU sources for a claim framed as universal?
2. Demographic representation in cited research: relevant populations missing?
3. Disciplinary skew: citing only one field for an interdisciplinary question?

```
Output:
  Geographic coverage: {list of jurisdictions/contexts represented}
  Perspectival flags: {list, or "adequate for stated scope"}
```

### Source concentration

Check:
1. Any single author cited more than 3 times? (Not inherently a problem. Note it.)
2. Any section where >50% of claims trace to one source?
3. Self-citation ratio (if the manuscript's author is identifiable).

```
Output:
  Most-cited authors: {list with counts}
  Concentration flags: {list, or "diversified"}
  Self-citation ratio: {N/N, or "author not identifiable"}
```

---

## Part 3: Source Ecosystem Health

Assess the overall condition of the manuscript's evidentiary infrastructure. If Citation Verifier has already run, read its `Citation_Ledger.md` for resolution data. If running standalone, perform basic resolution checks.

### Dead links

```
Count: {N}/{N} URLs checked
Dead: {N} ({percentage})
Wayback available: {N}/{N dead}
Action: Replace dead links with Wayback URLs or updated sources
```

### Retracted or corrected sources

```
For each cited source with a DOI:
  Check CrossRef metadata for "update-to" or "retracted-article" relations
  Check Retraction Watch if available

Retracted: {list, or "none found"}
Corrected: {list, or "none found"}
Action: Remove retracted sources; check whether corrections affect the cited finding
```

### Predatory venues

```
Check cited journals/venues against known predatory publisher indicators:
  - No peer review process documented
  - Excessive APC with rapid acceptance
  - Not indexed in major databases

Flagged: {list, or "none found"}
Action: Replace with equivalent findings from credible venues, if available
```

### Preprint status

```
For each cited preprint or working paper:
  Check CrossRef and Semantic Scholar for published version
  If published: has the published version changed conclusions?

Preprints cited: {N}
  Now published: {N} — {list with links to published versions}
  Still preprint: {N}
Action: Update citations to published versions; note any changes in findings
```

---

## Part 4: Field Reconnaissance Report

```
FIELD RECONNAISSANCE REPORT

Manuscript: {title}
Date: {date}
Argument_State.md: {present/absent}
Citation_Ledger.md: {present/absent}

COUNTEREVIDENCE SUMMARY
Claims checked: {N}
Counterevidence items found: {N}
  ADDRESS (strong): {N}
  ACKNOWLEDGE (moderate): {N}
  SET ASIDE (weak): {N}
No counterevidence found for: {N} claims

Top counterevidence items:
1. [claim] ← [counterevidence source] — [action recommendation]
2. ...
3. ...

LITERATURE GAPS
Temporal: {summary}
Methodological: {summary}
Perspectival: {summary}
Concentration: {summary}
Overall assessment: [ADEQUATE / GAPS IDENTIFIED / SIGNIFICANT GAPS]

SOURCE ECOSYSTEM
Dead links: {N}/{N}
Retracted sources: {N}
Predatory venue flags: {N}
Preprints with published updates: {N}
Overall health: [HEALTHY / SOME MAINTENANCE NEEDED / SIGNIFICANT ISSUES]

RECOMMENDATIONS
{Ordered by impact on the argument. Each with specific action.}
```

---

## Annotation Format

### § 10.7 Field Reconnaissance

```markdown
### 10.7 Field Reconnaissance
_Status: run by Field Reconnaissance (v1.0) on [date/time]_

Counterevidence:
- {N} items found for {N} load-bearing claims
- Strongest challenge: [1-sentence summary of most significant counterevidence]
- Action items: [N] to address, [N] to acknowledge

Literature gaps:
- [Most significant gap identified]
- [Second most significant]

Source health:
- [Summary: dead links, retractions, preprints]

Full results: see Field_Reconnaissance_Report.md
```

### § 10.3 Escalation (when needed)

```markdown
### 10.3 Verification and Research Handoff
_Updated by Field Reconnaissance (v1.0) on [date/time]_

Escalated from field reconnaissance:
1. [claim]: strong counterevidence exists — manuscript should address [source] before publication
2. [source]: retracted — remove or replace
3. [gap]: significant methodological gap may undermine [C-code]

Recommended handoff:
- Revision Coach for counterevidence integration and source replacement decisions
- Citation Verifier for verifying any new sources the author adds
- Domain expert for [specific issue]
```

---

## Guardrails

1. **Counterevidence is a service, not a gotcha.** Present findings as material the author should know about, not as proof that the argument is wrong. The author decides what to address, acknowledge, or set aside.
2. **Relevance over volume.** Three highly relevant counterevidence items are worth more than thirty tangentially related ones. Filter aggressively.
3. Use the self-feedback loop to determine search depth adaptively. The loop terminates after 3 iterations or when no new relevant results appear. For claims where the initial search returns nothing, this likely means the claim is uncontested or the search terms need reframing — not that more queries will help.
4. **Present uncertainty.** When sources conflict, show the range. When relevance is ambiguous, say so. When the search was limited (niche field, few results), note the limitation.
5. **Literature gaps are descriptive, not prescriptive.** Note that all sources are from one jurisdiction; don't insist the author must cite work from every continent. The form and scope of the manuscript determine what counts as a gap.
6. Never surface counterevidence selectively to support a particular political or ideological position. The module searches for the strongest challenges regardless of their direction.
7. **Source ecosystem health is maintenance, not judgment.** Dead links and stale preprints are fixable. Report them matter-of-factly.

---

## Token Budget

**Note:** These are estimates to be tested. The self-feedback loop and citation chain traversal add overhead compared to the original fixed-query design, but produce better coverage.

| Component | Tokens | Notes |
|---|---|---|
| Counterevidence search (with feedback loop) | 15-35K | Keyword generation + domain-priority search + citation chaining + up to 3 feedback iterations |
| Literature gap analysis | 5-10K | Aggregate analysis of citation inventory |
| Source ecosystem health | 3-5K | Resolution checks, retraction lookups |
| Report generation | 3-5K | |
| State annotation (integrated mode) | 1-2K | |
| **Total** | **30-60K** | |

Typical runs (estimates — test empirically):
- Academic article, 30 citations, 5 load-bearing claims: ~40-55K
- Policy brief, 10 citations, 3 load-bearing claims: ~30-40K
- Blog post, 15 citations, 2-3 central claims: ~30-40K

---

## Integration

### Trigger conditions

- After Citation Verifier fires CV12 (Hotspot Cluster)
- After Argument Evidence fires AE3 (Portfolio Narrowness) or AE4 (Representative Gap)
- After Red Team identifies claims with thin evidentiary support
- User request for literature adequacy check
- Pre-submission review

### Relationship to other modules

| Module | Field Recon's relationship |
|---|---|
| Citation Verifier | Reads `Citation_Ledger.md` when available. Does not suggest replacement sources — that's the Revision Coach's job. If the author adds new sources after Field Recon, Citation Verifier can verify them. |
| Argument Evidence | Reads § 10.1 for portfolio balance findings. Deepens AE3 and AE4 with external search. |
| Red Team | Reads § 10.4 for vulnerability rankings. Provides ammunition for the strongest counterarguments. |
| Dialectical Clarity | Reads §§ 2, 3, 5 for claim architecture. Does not modify the argument graph. |
| Factual Verification | Complementary scope. Field Recon searches the literature; Factual Verification checks specific real-world claims. |
| Revision Coach | Hands counterevidence integration strategy to the coach. The coach decides how to sequence the repairs. |

### Output location

`Field_Reconnaissance_Report.md` in the project directory alongside `Citation_Ledger.md` and `Argument_State.md`.

---

*An argument is only as strong as the challenges it survives. This module finds the challenges before the reviewers do.*
