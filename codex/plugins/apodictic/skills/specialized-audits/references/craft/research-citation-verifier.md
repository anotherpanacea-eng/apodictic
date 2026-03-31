# Companion Module: Citation Verifier (v1.0)
## Nonfiction Argument Engine / APODICTIC
*Drafted: March 23, 2026 — Revised: March 23, 2026*
*Status: Revised spec — incorporates level-setting research (SemanticCite, CiteAudit, PhilLit, OpenScholar)*
*Consumes: `Argument_State.md` (optional — runs standalone or integrated)*
*Standalone-capable: Yes — packageable separately from APODICTIC*

---

## Purpose

Verify whether explicit citations, hyperlinks, footnotes, endnotes, inline attributions, and quoted authorities:

1. exist and are retrievable
2. are represented faithfully
3. support the claim they are attached to
4. are current enough for the claim type
5. are carrying the right argumentative burden

This is a source-use integrity module. It sits between Argument Evidence (which diagnoses evidence *structure* without browsing) and Factual Verification (which checks broader real-world claims). Its question is narrow: **do your citations actually support what you're saying?**

This is **not** a style formatter and **not** full fact-checking.

---

## Non-Duplication Boundary

### Dialectical Clarity owns

1. claim architecture, warrant logic, burden, and objection map
2. structural support mapping (SM codes)
3. burden and scope assessment (BP codes)
4. pattern-level failures like evidence laundering or false precision

### Argument Evidence owns

1. provenance chains (how many removes from primary)
2. evidence portfolio balance
3. testimony calibration
4. quantitative integrity
5. verification queue (which claims need external checking)

### Citation Verifier owns

1. citation-to-claim fit: does the cited source support the attached claim?
2. quote and paraphrase fidelity: is the source represented accurately?
3. source existence and traceability: can the citation be resolved to a real document?
4. recency and currency: is the source current enough for this claim type?
5. citation metadata sufficiency: is there enough information to find the source?
6. attribution precision: is the claim attributed to the right person, in the right work?

### Factual Verification owns

1. broader real-world truth checking, including uncited factual claims
2. historical plausibility for fiction
3. procedural accuracy in professional contexts
4. real-person protocol

This module hands off to Factual Verification when it encounters uncited claims that need checking. It does not verify claims that lack any citation surface; those belong to the verification queue (Argument Evidence → Factual Verification pipeline).

---

## Activation

Run when:

1. the manuscript is citation-heavy, link-heavy, or source-heavy
2. the user asks for citation checking, source integrity, quote verification, or "are these citations real/current?"
3. Argument Evidence fires provenance or verification-hotspot concerns (AE1, AE2, AE10)
4. the piece is an op-ed, policy brief, white paper, academic article, testimony, reported essay, or investigative CNF
5. the manuscript was drafted with AI assistance (elevated hallucination risk for citations)

---

## Required Inputs

### Precondition

The Citation Verifier runs in two modes:

**Integrated mode** (within APODICTIC): `Argument_State.md` exists with §§ 1–9 populated by Dialectical Clarity v2.0. The verifier uses the claim architecture (§ 2), support map (§ 3), and diagnostic summary (§ 9) to prioritize citations by argumentative centrality. This is the stronger mode.

**Standalone mode**: No `Argument_State.md` required. The verifier parses the citation surface, infers claim attachment from proximity and argument-verb patterns (see Citation Context Extraction below), and classifies load as load-bearing / supporting / passing. Verification proceeds by inferred load, then document order. Note standalone mode in the output.

The module is designed to be packageable independently of APODICTIC.

### What this module reads

From `Argument_State.md` (when available):

1. § 1 Context and Classification (form, audience, consequence context)
2. § 2 Claim Architecture (C0, subclaims, stakes)
3. § 3 Support Map (support nodes and their types)
4. § 5 Burden, Scope, and Comparative Assessment
5. § 9 Diagnostic Summary (severity rankings, hard gate violations)
6. § 10.1 Evidence Analysis (if Argument Evidence has already run)

From the manuscript:

1. inline citations, footnotes, endnotes, bibliography
2. hyperlinks, quoted passages, statistics, tables
3. any attached PDFs, Zotero export, BibTeX, RIS, notes docs

### What this module writes

1. `Citation_Ledger.md`
2. `Argument_State.md` § 10.6 Citation Verification
3. optional escalation into § 10.3 Verification and Research Handoff for unresolved or high-risk items

---

## Citation Format Detection

Scan the first 50 lines and last 50 lines of the manuscript to auto-detect format:

| Signal | Format |
|---|---|
| `[^N]:` definitions | Footnote |
| `References` / `Bibliography` section + `(Author, Year)` in text | Author-year |
| `[1]`...`[N]` in text + numbered reference list at end | Numbered |
| `[text](url)` or `<a href>` links throughout | Hyperlinked (blog/web) |
| Mixed signals | Mixed; handle all simultaneously |

### Extraction patterns

**Footnote definitions:**
```
\[\^(\d+)\]:\s*(.+)
```

**Author-year in-text:**
```
\(([A-Z][a-z]+(?:\s(?:&|and)\s[A-Z][a-z]+)*(?:\set\sal\.)?),?\s*(\d{4})[^)]*\)
([A-Z][a-z]+(?:\s(?:&|and)\s[A-Z][a-z]+)?)\s*\((\d{4})[^)]*\)
```

**Hyperlinked claims:**
```
\[([^\]]+)\]\(([^)]+)\)
```

**Inline attributions:**
```
{Proper noun} (argues|claims|shows|demonstrates|found|observed|noted|wrote|contends) (that|in)
According to {Proper noun or Organization}
As {Proper noun} (noted|observed|argued|wrote) in {Title}
```

**Bare statistics (flag for source tracing):**
```
\d+(\.\d+)?%
\d+ (out of|of every) \d+
(roughly|approximately|about|nearly|over|under) (half|a third|a quarter|\d+)
```

**Hedged consensus (flag for specificity check):**
```
(research|studies|evidence|the literature|scholars) (shows?|suggests?|indicates?|demonstrates?|has shown|have found)
```

For footnote-style citations, resolve ibid. and op. cit. chains before proceeding.

---

## Source Trust Hierarchy

Resolve sources in this order. Do not start with generic web search. Do not use model memory as evidence.

### Tier 1: The manuscript package itself

Inline citations, footnotes, endnotes, bibliography, hyperlinks, quoted passages, statistics, tables, any attached PDFs, Zotero export, BibTeX, RIS, notes docs.

### Tier 2: The cited source directly

DOI landing page, publisher page, official report PDF, government or institutional webpage, original article, dataset, transcript, or court opinion.

### Tier 3: Authoritative metadata and index layers

| API | Purpose | Endpoint |
|---|---|---|
| CrossRef | DOI metadata, journal lookup | `api.crossref.org/works/{doi}` or `?query.bibliographic={title}&query.author={author}&rows=3` |
| Semantic Scholar | Paper search, citation counts, citation graph | `api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=3&fields=title,authors,year,externalIds,venue` |
| OpenAlex | Broader coverage (books, non-English, 260M+ records) | `api.openalex.org/works?search={title}&filter=author.search:{author}&mailto=apodictic@example.com` |
| CORE | 431M papers, good for abstracts and full text | `api.core.ac.uk/v3/search/works` |
| Unpaywall | OA PDF access | `api.unpaywall.org/v2/{doi}?email=apodictic@example.com` |
| PubMed | Biomedical papers | `eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax=3&retmode=json` |
| WorldCat / ISBN | Book verification | search by ISBN or title+author |

### Tier 4: Fallback retrieval and archival sources

Internet Archive / Wayback Machine (`web.archive.org/web/{url}`), mirrored institutional copies, reputable database abstracts when full text is unavailable.

**API key notes (updated March 2026):**
- Semantic Scholar now effectively requires a free API key — returns 429 without one from shared IPs. Register at semanticscholar.org/product/api.
- Unpaywall requires a legitimate email address (rejects test@example.com and similar).
- OpenAlex offers a free API key for higher rate limits (100K credits/day) but unauthenticated access with mailto still works.
- All others remain keyless.

### Resolution sequence

```
0. Generate 2-3 keyword variants from the citation metadata
   (LLM generates search terms capturing terminological variation)

1. IF DOI present:
   GET https://api.crossref.org/works/{doi}
   → Confirms existence, returns full metadata
   IF DOI resolves: check Unpaywall for OA PDF access

2. IF no DOI — search by title + author (with fuzzy matching):
   Search domain-priority APIs first (see Domain-Adaptive Source Hierarchy)
   Then fallback cascade:
   a. CrossRef: ?query.bibliographic={title}&query.author={author}&rows=5
   b. Semantic Scholar: /paper/search?query={keywords}&limit=5
   c. OpenAlex: /works?search={keywords}&per_page=5
   d. CORE: /search/works (431M papers, good for abstracts)
   Accept matches at ≥80% title similarity + author surname match + year ±1

3. IF all academic APIs return 0:
   PubMed (if biomedical), WorldCat/ISBN (if book)

4. IF URL source:
   Fetch the URL directly
   IF 404/dead: GET https://web.archive.org/web/{url}

5. Store every API response as JSON intermediate (provenance enforcement)
6. Record result, confidence tier, and any metadata discrepancies
```

Batch strategy: process in groups of 10. 1-second delay between API calls to respect rate limits. For Semantic Scholar, use the free API key (required since March 2026).

---

## Two-Phase Verification Design

The module operates in two distinct phases. Phase 1 is automated and fast; Phase 2 requires LLM editorial judgment and is where the hard verification work happens.

### Phase 1: Automated Resolution (catches CV1, CV2, CV3, CV9)

API-based existence and metadata verification. For each citation:

1. **Parse** citation from manuscript
2. **Normalize** metadata (author names, title, year, DOI, URL)
3. **Generate keyword variants** from the citation (learned from OpenScholar: the LLM generates 2-3 search-term variants before hitting APIs, capturing terminological variation — e.g., "recidivism" → also search "reoffending," "criminal desistance")
4. **Resolve** to source-of-record via trust hierarchy with fuzzy matching
5. **Check currency** (date comparison against claim-type thresholds)
6. **Record** resolution result and confidence level

Phase 1 produces a resolution map: which citations exist, which are dead, which have metadata gaps, which are stale. This phase is fast and deterministic.

### Phase 2: Editorial Verification (catches CV4, CV5, CV6, CV7, CV8, CV10, CV11, CV12)

LLM-based content comparison for citations where source text is accessible. For each citation with full-text or abstract access:

1. **Extract manuscript characterization** using citation context extraction (see below)
2. **Read source content** (full text, abstract, or metadata — record which)
3. **Compare** manuscript characterization to source's actual argument
4. **Apply hedge fidelity patterns** (see below)
5. **Assess citation-claim fit** and assign verdict
6. **Record** verdict, flags, and structured annotation (CORE ARGUMENT / RELEVANCE / POSITION)

Phase 2 is where the editorial value lives. The easy failures (ghost citations, dead links, stale sources) are caught in Phase 1. The hard failures (paraphrase inflation, scope lift, secondary laundering, authority masking) require reading the source and understanding what it actually says.

---

## Citation Context Extraction

*Learned from PhilLit's citation_context.py*

Before comparing a citation to its source, extract *how the manuscript characterizes* the cited work. Use argument-verb patterns to identify the claim attributed to the source:

```
{Author} (argues|claims|shows|demonstrates|found|observed|noted|wrote|contends|maintains|holds|suggests|concludes|establishes|reveals|confirms) (that|in)
According to {Author or Organization}
As {Author} (noted|observed|argued|wrote|showed|demonstrated) in {Title}
{Author}'s (argument|claim|finding|position|view|thesis|conclusion) (is|was) that
```

For each citation, record:
- **Manuscript says source argues:** [extracted characterization]
- **Source actually argues:** [from source text, abstract, or metadata]
- **Gap:** [match / inflation / deflation / misrepresentation / none detected]

This operationalizes CV4 (Quote Drift) and CV5 (Paraphrase Inflation) detection systematically rather than relying on holistic LLM judgment.

---

## Fuzzy Matching for Metadata Resolution

*Learned from Citation-Hallucination-Detection repo*

Citations in manuscripts are often imprecise — misspelled author names, approximate titles, wrong years. The resolution step must tolerate metadata variation:

1. **Title matching**: Accept matches at ≥80% similarity (Levenshtein or cosine on word tokens). Academic APIs often return slightly different title formats (subtitle inclusion, capitalization, punctuation).
2. **Author matching**: Match on surname + first initial. Handle name variations (van/von prefixes, transliterated names, middle initials present/absent).
3. **Year matching**: Accept ±1 year tolerance (online-first vs. print publication dates commonly differ).
4. **Ambiguous matches**: When multiple API results match at similar confidence, record all candidates and flag for manual disambiguation.

When fuzzy matching resolves a citation that exact matching would miss, note the discrepancy in the ledger (the metadata in the manuscript may need correction even though the source is real).

---

## Domain-Adaptive Source Hierarchy

*Learned from PhilLit's prioritized search*

The source trust hierarchy is not flat. Start with the most authoritative sources for the manuscript's domain, inferred from `Argument_State.md` § 1 (Context and Classification) or from the manuscript itself:

| Domain | Priority sources | Then |
|--------|-----------------|------|
| Philosophy | PhilPapers, SEP, IEP | Semantic Scholar, OpenAlex, CORE |
| Biomedical | PubMed, Semantic Scholar | CrossRef, OpenAlex |
| Policy / legal | Government databases, official reports, court opinions | CrossRef, OpenAlex |
| Social science | Semantic Scholar, OpenAlex | CORE, CrossRef |
| General / interdisciplinary | CrossRef, Semantic Scholar, OpenAlex | CORE, web fallback |

For all domains, CrossRef remains the DOI resolution authority. The domain-adaptive layer affects *search priority* when resolving citations without DOIs.

---

## Provenance Enforcement

*Learned from PhilLit's anti-hallucination hooks*

Every API response used during resolution must be stored as a JSON intermediate. The verifier's verdicts and claims about sources must trace back to stored API responses. Specifically:

1. When an API returns metadata (title, authors, year, venue), store the raw response.
2. When the verifier claims a source "exists" or "says X," that claim must reference a stored response.
3. When the verifier claims a source is "unretrievable," the stored responses must show failed resolution at every tier.
4. "Unable to verify" is always preferable to a verdict that doesn't trace to evidence.

This converts the guardrail "never bluff verification" from a prompt instruction to an auditable constraint. In tool-capable environments, this can be enforced with a pre-write guard on Citation Ledger updates.

---

## Verification Data Pipeline (Summary)

Phase 1 + Phase 2 combined:

### Confidence levels

| Level | Meaning | When it applies |
|---|---|---|
| `full-text verified` | Read the actual source content | OA PDF retrieved, URL fetched, or full text available |
| `abstract-only verified` | Checked against abstract | Source exists, metadata matches, but full text behind paywall |
| `metadata-only verified` | Confirmed existence and metadata | Source resolves in API but no content accessible |
| `unretrievable` | Cannot access source at any tier | Dead link, no API match, insufficient metadata |

When the verifier cannot get enough source access, it says so explicitly. It does not bluff verification.

---

## Citation Types

| Type | What to verify | Key risk |
|---|---|---|
| `quote` | Verbatim accuracy, context fidelity | CV4 Quote Drift |
| `paraphrase` | Faithful representation, scope preservation | CV5 Paraphrase Inflation |
| `statistic` | Number, denominator, timeframe, population, method | CV10 Unsupported Statistic |
| `background` | Source exists, is relevant, is current | CV9 Currency Mismatch |
| `authority mention` | Person holds attributed position, in attributed work | CV8 Authority Mask |

---

## Source Types

| Type | Description | Verification standard |
|---|---|---|
| `primary` | Original research, data, testimony, court opinion, statute | Highest: verify against source directly |
| `secondary` | Analysis, commentary, review of primary sources | Check whether secondary is standing in for primary (CV7) |
| `tertiary` | Encyclopedias, textbooks, handbooks | Acceptable for background; flag if carrying argumentative weight |
| `journalism` | News reports, investigative pieces | Verify against original reporting where possible |
| `institutional` | Government reports, NGO publications, org data | Verify against official source; check for updates |
| `testimony` | Witness accounts, personal communication | Limited verifiability; note as such |

---

## Named Flags

| Code | Name | Description |
|---|---|---|
| `CV1` | Ghost Citation | Source cannot be found as cited. No match in any database or at any URL. Possible fabrication or hallucination. |
| `CV2` | Dead or Opaque Source | Link broken, reference too incomplete to retrieve cleanly. Source may exist but cannot be confirmed. |
| `CV3` | Metadata Gap | Insufficient author/title/date/source information to resolve. Citation string is too vague to verify. |
| `CV4` | Quote Drift | Quoted language does not match source, or context around the quote changes its meaning. |
| `CV5` | Paraphrase Inflation | Paraphrase claims more than the source supports. Source hedges; manuscript doesn't. Source is narrow; manuscript generalizes. |
| `CV6` | Scope Lift | Narrow source used for broader claim than it warrants. Geographic, temporal, or population inflation. |
| `CV7` | Secondary Laundering | Secondary summary or commentary is treated as if it were the underlying primary evidence. |
| `CV8` | Authority Mask | Prestige of source or author is standing in for actual reasoning. Citation adds credibility without adding evidence. |
| `CV9` | Currency Mismatch | Source too old for a time-sensitive claim. Finding may have been superseded, retracted, or significantly updated. |
| `CV10` | Unsupported Statistic | Number lacks traceable method, denominator, timeframe, or source clarity. |
| `CV11` | Citation Padding | References create apparent density without real support. Multiple citations that all trace to the same underlying evidence, or citations that don't actually address the claim. |
| `CV12` | Hotspot Cluster | Multiple citation failures hit C0 or major subclaims. The argument's evidentiary foundation has a structural problem, not just isolated errors. |

---

## Verdict Set

For each citation node:

| Verdict | Meaning |
|---|---|
| `SUPPORTED` | Source exists, is accurately represented, and supports the attached claim. |
| `SUPPORTED WITH CAVEAT` | Source supports the claim but with qualifications the manuscript omits or understates. |
| `PARTIAL / OVERCLAIMED` | Source partially supports the claim, but the manuscript extends beyond what the source warrants. |
| `MISREPRESENTED` | Source says something different from what the manuscript attributes to it. |
| `UNRETRIEVABLE` | Source cannot be located or accessed at any tier. |
| `OUTDATED` | Source existed and was accurate at time of publication, but the finding has since been superseded or the field has moved. |
| `NEEDS EXPERT REVIEW` | Verification exceeds what API resolution and available text can determine. Recommend domain expert or professional fact-checker. |

---

## Procedure

### Step 1: Parse the citation surface

Detect citation format(s). Extract every citation, hyperlink, inline attribution, quoted passage, and bare statistic. Record location in manuscript (line, paragraph, section). Extract citation context using argument-verb patterns (see Citation Context Extraction above).

### Step 2: Map citations to claims or claim corridors

**Integrated mode**: Map each citation to the claim or subclaim it supports, using `Argument_State.md` § 2 (Claim Architecture) and § 3 (Support Map). Inherit argumentative load from the state.

**Standalone mode**: Infer claim attachment from proximity and argument-verb context.

**In both modes**, classify each citation by **relation type** and **load**:

Citation relation types (assign one per citation):

| Relation | What it means | Verification scope |
|----------|--------------|-------------------|
| `direct support` | Source is cited as evidence for the claim | Full verification: existence + fit + hedge fidelity |
| `background` | Source provides framing or context, not evidence | Existence + currency only; skip fit verification |
| `counterposition` | Source is cited as the opposing view | Verify it actually opposes; do not flag fit mismatch |
| `method/definition` | Source provides a tool, term, or framework | Verify attribution accuracy; skip fit |
| `see also` | Pointer to related work, often in citation stacks | Existence only; skip fit and hedge analysis |

Load classification (assign one per citation):

- **Load-bearing**: citation supports a premise the argument depends on
- **Supporting**: reinforces a point but the argument survives without it
- **Passing**: color, context, or aside

The relation type determines *what* to verify. The load determines *priority*. A `direct support` / `load-bearing` citation gets full Phase 2 verification. A `see also` / `passing` citation gets existence checking only. This prevents false positives on legitimate citation stacks where multiple "see also" references appear alongside one direct-support citation.

### Step 3: Prioritize

Verify in this order:

1. Citations attached to C0 or central subclaims
2. Citations in consequence contexts (legal risk, policy-critical, living-person)
3. Citations flagged by Argument Evidence (AE1, AE2, AE7, AE10) — integrated mode only
4. Remaining citations in document order

For manuscripts drafted with AI assistance, elevate all citations to at least priority 2 (hallucination risk).

### Step 4 (Phase 1): Resolve sources

Follow the domain-adaptive trust hierarchy. For each citation:
1. Generate keyword variants from the citation metadata
2. Attempt resolution at each tier in order, using fuzzy matching
3. Store every API response as a JSON intermediate (provenance enforcement)
4. Check currency against claim-type thresholds
5. Record which tier succeeded and the confidence level achieved

Phase 1 catches CV1, CV2, CV3, CV9.

### Step 5 (Phase 2): Verify content

For citations where source content is accessible (full-text or abstract):

**Quote verification**: Compare quoted text to source. Check for truncation, elision, or context stripping that changes meaning.

**Paraphrase verification**: Compare the manuscript's characterization (extracted in Step 1) to the source's actual argument. Apply hedge fidelity patterns (see below). Record: what manuscript says source argues, what source actually argues, and the gap.

**Statistical verification**: Compare number, denominator, timeframe, and population. Check whether the method supports the precision claimed.

**Attribution verification**: Confirm the attributed author holds the attributed position in the attributed work. Check whether they're the originator or citing someone else. Check whether the position is their own or one they're reporting.

Phase 2 catches CV4, CV5, CV6, CV7, CV8, CV10, CV11, CV12.

### Step 6: Annotate per citation

For each verified citation, record structured annotation:

- **CORE ARGUMENT**: what the source actually argues (from source text)
- **MANUSCRIPT CHARACTERIZATION**: what the manuscript claims it argues (from Step 1 extraction)
- **FIT**: match / inflation / deflation / misrepresentation / none detected
- **RELEVANCE**: how the source connects to the manuscript's claim
- **VERDICT**: one of the 7 verdicts
- **FLAGS**: any CV codes fired
- **CONFIDENCE**: full-text / abstract-only / metadata-only / unretrievable
- **LINK**: resolved URL (DOI link, institutional repository, publisher page, or Wayback URL)

### Step 6a: Normalize citations with links

When repairing metadata errors, always include the resolved link alongside the corrected citation. For academic sources, use the DOI URL (`https://doi.org/{doi}`). For institutional reports, use the official URL. For law review articles, use the institutional repository URL. This makes every citation independently verifiable by the reader without repeating the resolution process.

Format: append the link to the footnote text, or embed as a markdown hyperlink on the title. The manuscript's existing citation style determines the format.

*Annotation structure learned from PhilLit's CORE ARGUMENT / RELEVANCE / POSITION pattern.*

### Step 7: Write the ledger

Produce `Citation_Ledger.md` with the full results.

### Step 8: Annotate Argument_State.md (integrated mode only)

Write the highest-risk findings and repair order into § 10.6. Escalate to § 10.3 for unresolved or high-risk items that need deeper research.

---

## Hedge Fidelity Patterns

When comparing manuscript hedging to source hedging, flag any mismatch in either direction:

| Pattern | Source says | Manuscript says | Flag |
|---|---|---|---|
| Certainty inflation | "may contribute to" | "causes" | CV5 |
| Population inflation | "in a sample of 200 undergraduates" | "people tend to" | CV6 |
| Geographic inflation | "in the US context" | "globally" | CV6 |
| Temporal inflation | "between 2015-2018" | "consistently" | CV6 |
| Precision inflation | "our findings suggest" | "research proves" | CV5 |
| Deflation | States without hedge | "merely suggests" | CV5 (note: deflation is also a problem) |

---

## Hard Gates

1. Any `CV1` (Ghost Citation), `CV4` (Quote Drift), or `CV10` (Unsupported Statistic) on C0 or a central subclaim is **Must-Fix**.
2. Any living-person, legal-risk, or policy-critical citation failure escalates immediately. Do not bury these in the ledger.
3. If three or more central citations fail in one corridor, escalate from spot-check findings to **CV12** cluster warning. The argument has a structural evidence problem.
4. If source access is blocked or paywalled, say so explicitly. Record as `metadata-only verified` or `unretrievable`. Do not bluff verification.
5. Never upgrade a citation verdict based on the author's stated intentions. Verify what is on the page.

---

## Calibration by Form

| Form | Citation norm | Signature risk | Watch for |
|---|---|---|---|
| Op-ed | Low citation density tolerated, but central stats and policy claims must be clean. | CV10, CV5 | Central statistic that doesn't check out |
| Policy brief / white paper | Primary-source burden high. Recency matters. Government and institutional sources expected. | CV7, CV9 | Secondary laundering of government data; stale policy citations |
| Academic article | Support-fit and quote fidelity high. Full bibliographic metadata expected. | CV1, CV4, CV5 | Ghost citations, quote drift, paraphrase inflation |
| Testimony | Don't overpenalize sparse apparatus. Do verify high-stakes external assertions. | CV10, CV1 | Unsupported statistics in sworn or legislative testimony |
| Memoir / CNF | Verify public/external claims, not subjective memory or interior experience. | CV4, CV9 | Inaccurate quotes from public figures; outdated institutional claims |
| Blog post (scholarly) | Hyperlinked claims acceptable. Source-fit still matters. Dead links common. | CV2, CV5, CV9 | Dead links, paraphrase inflation, stale sources |

---

## Citation Ledger Schema

`Citation_Ledger.md` records every citation node checked:

```markdown
# Citation Ledger: {manuscript title}
_Generated by Citation Verifier v1.0 on {date/time}_
_Argument_State.md: {present/absent}_
_Citation format detected: {footnote/author-year/hyperlinked/mixed}_

## Summary
Citations parsed: {N}
  Load-bearing: {N}
  Supporting: {N}
  Passing: {N}
Resolved: {N}/{N}
  Full-text verified: {N}
  Abstract-only: {N}
  Metadata-only: {N}
  Unretrievable: {N}
Verdicts: {N} supported, {N} supported with caveat, {N} partial/overclaimed,
          {N} misrepresented, {N} unretrievable, {N} outdated, {N} needs expert review
Flags fired: {list CV codes}

## Critical Issues (Must-Fix)
{Ordered by severity. Only items hitting hard gates.}

## Flagged Citations
| Ref ID | Location | Claim | Citation | Type | Source Type | Confidence | Fit Verdict | Currency | Flags | Severity | Repair Note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | §2, ¶3 | "23% of YRA cases..." | CJCC 2022 Report | statistic | institutional | full-text | SUPPORTED | current | — | — | — |
| 2 | §4, ¶1 | "Schiraldi argues..." | Schiraldi 2021 | paraphrase | primary | abstract-only | PARTIAL | current | CV5 | Should-Fix | Source hedges more than manuscript suggests |
| ... | | | | | | | | | | | |

## Citation Detail (per flagged citation)
For each citation with flags or non-SUPPORTED verdicts, include:

```
### Ref 2: Schiraldi 2021
Manuscript says source argues: "Schiraldi argues that community-based alternatives reduce recidivism by 40%"
Source actually argues: "Our findings suggest community-based programs may contribute to modest reductions in rearrest rates (12-18%) in the studied jurisdictions"
Gap: Certainty inflation (suggests → argues), precision inflation (modest → 40%), scope lift (studied jurisdictions → general)
Flags: CV5 (Paraphrase Inflation), CV6 (Scope Lift)
Resolution: CrossRef DOI match → Unpaywall OA PDF → full-text verified
Provenance: stored API response ref #2-CR, #2-UP
```

## Repair Queue
{Ordered by: Must-Fix first, then severity × centrality.
Each item: what to fix, why, and suggested approach.}
```

---

## Annotation Format

### § 10.6 Citation Verification

```markdown
### 10.6 Citation Verification
_Status: run by Citation Verifier (v1.0) on [date/time]_
_Confidence: [full-text / mixed / metadata-only]_
_Argument_State.md consulted: [yes/no]_

Citation surface: [N] citations parsed across [format types]
Resolution rate: [N]/[N] ([percentage])

Critical findings:
1. `CV1` Ghost Citation — [Ref ID]: [citation string] attached to [C-code]
2. `CV5` Paraphrase Inflation — [Ref ID]: [source hedges, manuscript doesn't] on [C-code]
3. ...

Must-Fix items: [N]
Should-Fix items: [N]

Full results: see Citation_Ledger.md

Repair order:
1. [Ref ID]: [what to fix] — [why it matters for the argument]
2. [Ref ID]: [what to fix]
3. ...
```

### § 10.3 Escalation (when needed)

```markdown
### 10.3 Verification and Research Handoff
_Updated by Citation Verifier (v1.0) on [date/time]_

Escalated from citation verification:
1. [Ref ID]: [unretrievable / needs expert review] — [why]
2. [Ref ID]: [claim requires deeper factual checking than citation verification covers]

Recommended handoff:
- Factual Verification research mode for items [N, N]
- Field Reconnaissance research mode for counterevidence on [C-code]
- Domain expert consultation for items [N]
```

---

## Handoff Rules

### From Argument Evidence

When Argument Evidence fires:
- `AE1` (Provenance Opacity) on a cited source → Citation Verifier should resolve the source
- `AE2` (Secondary Flattening) → Citation Verifier should check whether the secondary accurately represents the primary
- `AE10` (Verification Hotspot Cluster) → Citation Verifier should run on the full hotspot corridor

### To Factual Verification

Hand off when:
- a claim lacks any citation surface but is factually verifiable (uncited claims are Factual Verification's domain)
- verification requires domain expertise beyond API resolution
- a historical claim in fiction needs period-specific checking

### To Field Reconnaissance

Hand off when:
- citation verification surfaces a claim where counterevidence may exist
- the source ecosystem shows temporal or perspectival gaps worth investigating
- CV12 (Hotspot Cluster) fires and the argument needs a broader literature check

### To Revision Coach

The Citation Verifier identifies problems. The Revision Coach sequences repairs. The verifier should never rewrite citations or suggest replacement sources. It records what's wrong and hands the repair queue to the coach.

---

## Integration Notes

### With Dialectical Clarity

Use the core audit's claim architecture and support map. Do not rebuild. If the verifier encounters a citation not mapped to any claim in the state, add it to the ledger as `unmapped` and note the gap.

### With Argument Evidence

Citation Verifier deepens Evidence's provenance analysis with external resolution. If Evidence has already run, read its findings (§ 10.1) before verifying to avoid duplicating work. If Evidence flags `AE7` (Orphaned Statistic), the Citation Verifier should check whether the statistic has a traceable source.

### With Red Team

If Red Team identifies `RT9` (Evidence Chain Snap), the Citation Verifier should check whether the snap is caused by a citation failure (ghost citation, misrepresentation) or an argumentative failure (the citation is accurate but doesn't support the claim). The former is CV territory; the latter is DC territory.

---

## Token Budget

**Empirically tested.** First real-world run: a 155-citation policy white paper (TAY transition services). Results:

| Component | Estimated | Actual | Notes |
|---|---|---|---|
| Main conversation (parsing, mapping, editing, ledger) | 30-75K | ~200K | Manuscript reading, fix application, ledger writes, coordination |
| Subagent verification (7 parallel agents) | — | ~474K | 7 agents averaging ~68K each; ran in parallel so wall-clock time was ~3 min/batch |
| **Total** | **30-75K** | **~675K** | ~4,350 tokens per citation verified |

The original estimates were ~10x too low. The main cost drivers:

1. **Subagent overhead.** Each agent loads its own context, makes multiple API calls, and produces structured results. Parallel execution keeps wall-clock time fast (~3 minutes per batch of 15 citations) but token cost is high.
2. **Fix application.** When errors are found, correcting them requires reading surrounding context, editing precisely, and checking for body-text references that also need updating. Content-level errors (e.g., a study cited as "confirming" a finding it actually disconfirmed) require tracing every in-text reference.
3. **Iterative verification.** Some citations require multiple API calls (CrossRef miss → Semantic Scholar miss → OpenAlex miss → web search) before resolving.

### Recommended batching strategy

For manuscripts with 50+ citations, use parallel subagents grouped by citation type:
- Academic citations with author/year/journal: batch of 15, resolve via CrossRef/OpenAlex
- Legal/statutory citations: batch of 15, resolve via web search
- Institutional/government reports: batch of 15, resolve via URL check + web search
- WSIPP/database citations: single agent for all, resolve via wsipp.wa.gov
- Gray literature/quotes: batch of 15, resolve via web search

Each batch runs as a background agent (~60-80K tokens, ~3 minutes). Seven agents covering 155 citations completed in ~10 minutes of wall-clock time.

### Revised estimates by manuscript type

- Policy white paper, 155 citations: ~675K tokens (~10 min with parallel agents)
- Academic article, 30 footnotes: ~150-200K tokens (~5 min)
- Policy brief, 10 citations: ~75-100K tokens (~3 min)
- Blog post, 15 hyperlinks: ~75-100K tokens (~3 min)

---

## Guardrails

1. Research supplements author knowledge; it doesn't override author judgment about which sources to use.
2. Cap API queries per citation by phase:
   - **Resolution** (Phase 1): up to 5 API calls (DOI lookup + Unpaywall + up to 3 fallback searches). More suggests the citation is unresolvable — flag as `CV3`.
   - **Content verification** (Phase 2): 1-2 source reads (full text or abstract). Do not fetch multiple versions of the same source.
   - **Escalation**: 1 handoff per unresolved item.
3. "Unable to verify" is a valid output. Say so clearly rather than manufacturing false confidence.
4. Never downgrade citation quality because the form is informal. A hyperlinked blog post can have excellent citation integrity; an academic article can have terrible citation integrity. Judge the citation-to-claim fit, not the citation format.
5. Never claim full-text verification when working from abstracts or metadata. The confidence level must match the access level.
6. For manuscripts drafted with AI assistance, note elevated hallucination risk but do not assume all citations are fabricated. Verify normally; the flags will catch the problems.

---

*Citations are promises to the reader that someone else checked your work. This module checks whether those promises are kept.*
