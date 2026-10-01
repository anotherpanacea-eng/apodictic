# Research Mode: Factual Verification (v1.0)

## Purpose

Spot-check real-world claims in manuscripts where accuracy matters. This is not exhaustive fact-checking (that's a specialized service); it's a developmental pass to catch errors that would undermine credibility or break reader immersion.

**When to activate:**
- Historical fiction (any period)
- Memoir or autobiographical fiction with verifiable claims
- Works featuring real locations, institutions, or procedures
- Works with scientific or technical premises
- Works featuring real historical figures
- Any manuscript where "getting it wrong" would damage trust

**Core principle:** The goal is *plausibility maintenance*, not pedantry. Flag errors that would make knowledgeable readers lose faith; ignore details only specialists would catch.

---

## Part 1: Verification Triage

Not all facts are equal. Prioritize by reader impact:

| Priority | Type | Example | If Wrong... |
|----------|------|---------|-------------|
| **HIGH** | Structural facts | Major historical events, scientific laws | Breaks the premise |
| **HIGH** | Character-defining details | Real person's documented beliefs/actions | Defamation risk, reader distrust |
| **MEDIUM** | Period texture | Fashion, food, technology availability | Knowledgeable readers wince |
| **MEDIUM** | Procedural accuracy | How courts/hospitals/police actually work | Professional readers bounce |
| **LOW** | Fine detail | Exact street names, minor dates | Only specialists notice |

**Logic Gate: Verification Scope**
```
IF Error would affect plot logic → HIGH priority
IF Error would affect character credibility → HIGH priority
IF Error is atmospheric only → MEDIUM priority (verify if easy, note if uncertain)
IF Error is specialist-level detail → LOW priority (flag for author review, don't research)
```

---

## Part 2: Domain-Specific Protocols

### Historical Fiction

**Automatic checks:**
- Major events: Did [event] happen when/where stated?
- Technology: Was [technology] available in [year]?
- Language: Would [term/phrase] have been used in [period]?
- Social norms: Was [behavior] plausible for [character type] in [period]?

**Search pattern:**
`"[claimed fact]" + [time period] + "history" OR "historical"`

**Common anachronism categories:**
- Words/phrases coined later
- Technology not yet invented
- Social attitudes more modern than period
- Geographic features that changed
- Currency/measurement systems

**Output format:**
```
VERIFICATION: [Claimed fact]
Status: CONFIRMED / UNCONFIRMED / CONTRADICTED / PLAUSIBLE BUT UNVERIFIED
Source: [citation]
If Contradicted: Actual fact was [X]
Recommendation: [Fix / Acknowledge as intentional deviation / Flag for author research]
```

### Memoir / Autobiographical Fiction

**Verification scope:**
- Verifiable public events (dates, locations, news events)
- Institutional details (schools, companies, organizations)
- Geographic accuracy (places that exist, distances, travel times)

**NOT verified (privacy/subjectivity):**
- Private conversations
- Internal experiences
- Other people's motivations
- Family dynamics (unless contradicted by public record)

**Sensitivity note:** Memoir verification is about *external* plausibility, not challenging the author's experience. Flag only where public record contradicts.

### Scientific/Technical Premises

**For hard SF or technical thrillers:**
- Is the core premise scientifically plausible?
- Are technical procedures described accurately?
- Have relevant scientific understandings changed since drafting?

**Search pattern:**
`"[scientific claim]" + "research" OR "study" + [recent year]`

**Output format:**
```
PREMISE CHECK: [Scientific claim]
Current scientific consensus: [X]
Status: ALIGNED / OUTDATED / SPECULATIVE BUT PLAUSIBLE / CONTRADICTED
If Outdated: Field has moved to [X]; manuscript may need update
If Speculative: Flag as "extrapolation from current science" (acceptable for SF)
```

### Real Locations

**Verify:**
- Does location exist as described?
- Are distances/travel times plausible?
- Have significant changes occurred since drafting?

**For fictional locations in real settings:**
- Is the fictional element clearly marked as fictional?
- Does it violate known geography?

### Professional Procedures

**For legal, medical, law enforcement, military, etc.:**
- Would a professional in this field recognize the procedure?
- Are there jurisdiction-specific variations the author might have missed?

**Output format:**
```
PROCEDURE CHECK: [Described process]
Accuracy: ACCURATE / SIMPLIFIED BUT ACCEPTABLE / MISLEADING / WRONG
Common in Fiction: Yes/No (some inaccuracies are genre conventions)
If Wrong: Actual procedure is [X]
Recommendation: [Fix / Accept as genre convention / Consult expert]
```

---

## Part 3: Real Person Protocol

**Extra caution required.** Depicting real people (living or dead) creates legal and ethical considerations.

**Verification questions:**
1. Did this person exist?
2. Are depicted actions/beliefs documented or invented?
3. If invented, are they plausible given documented character?
4. For living persons: Could depiction be construed as defamatory?

**Logic Gate:**
```
IF Real person depicted doing documented actions → PASS (cite source)
IF Real person depicted doing plausible-but-invented actions → FLAG: "Fictionalized Real Person"
IF Real person depicted doing implausible or damaging actions → FLAG: "Real Person Risk"
IF Living person depicted negatively → FLAG: "Potential Defamation Concern"
```

**Output format:**
```
REAL PERSON: [Name]
Depiction Type: Historical figure / Public figure / Private person
Actions Depicted: DOCUMENTED / PLAUSIBLE INVENTION / IMPLAUSIBLE INVENTION
Documentation: [Source, if documented]
Risk Level: LOW / MEDIUM / HIGH
Recommendation: [Proceed / Add author's note / Fictionalize name / Consult legal]
```

---

## Part 4: Verification Output

**Per-manuscript summary:**

```
FACTUAL VERIFICATION REPORT

Manuscript: [Title]
Verification Scope: [Historical / Memoir / Technical / Location / Mixed]
Sample Size: [X claims checked of estimated Y total]

HIGH PRIORITY FINDINGS:
- [Finding 1]: [Status] — [Recommendation]
- [Finding 2]: [Status] — [Recommendation]

MEDIUM PRIORITY FINDINGS:
- [Finding 1]: [Status] — [Recommendation]
- [etc.]

UNVERIFIED (Author Should Check):
- [Item]: [Why not verified]
- [etc.]

REAL PERSON FLAGS:
- [Person]: [Risk level] — [Recommendation]

OVERALL ASSESSMENT:
[ ] Factual foundation solid
[ ] Minor corrections needed
[ ] Significant research gaps
[ ] Structural premise problematic

Notes: [Any context about verification limitations]
```

---

## Part 5: Guardrails

- **Sampling, not exhaustive:** Verify HIGH priority claims and spot-check MEDIUM; don't attempt comprehensive fact-checking
- **Source quality:** Prefer primary sources, reputable reference works, academic sources; note when relying on less authoritative sources
- **Uncertainty is okay:** "Unable to verify" is a valid finding; don't manufacture false confidence
- **Fiction license:** Authors may intentionally deviate from fact; flag but don't assume error
- **Expertise limits:** For specialist domains, recommend expert consultation rather than claiming system authority
- **Living persons:** Extra caution; when in doubt, recommend legal review
- **Cap research:** 3 queries per claim; more suggests the claim is unverifiable or requires expert consultation

---

## Integration

- **Trigger:** During Pass 10 (Entity Tracking) when genre/content warrants
- **Also trigger:** When reader experience pass logs "I don't believe this" for factual claims
- **Output location:** Append to Pass 10 findings or create standalone Factual Verification Report
- **Handoff:** Recommend professional fact-checker for high-stakes nonfiction (memoir, investigative)

---

*Fiction earns trust through the facts it gets right. This module protects that trust.*
