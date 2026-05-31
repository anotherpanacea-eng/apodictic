# SOURCES — Metadata-Only Manifest (referenced fixtures)

**Purpose:** give the input preparer everything needed to fetch and pin a
referenced fixture's text — **without exposing any answer key.** This file
contains URLs, analyzed-text extraction anchors, and hash fields only. It
contains **no** GT1–GT7, no claim, no diagnosis.

**Why it exists (leak prevention):** the blind runner must never see
`groundtruth.md`. If the preparer had to open `groundtruth.md` to find the URL,
the answer key could enter the model's context before diagnosis. So fetch
metadata lives here instead. The preparer reads **only this file**; the scorer
reads `groundtruth.md`; the blind runner sees **only the extracted text** (see
[RUN-PROTOCOL.md](RUN-PROTOCOL.md) Step 1).

## Extraction discipline

For each source: fetch the URL, then keep only the text between the **START** and
**END** anchors, dropping everything in **EXCLUDE**. Because these are dynamic /
gated / mirrored pages whose boilerplate varies by retrieval, the **exact**
anchor strings and the SHA-256 are *recorded on first authoritative retrieval*
(same pattern as the Swift fixture) and then pinned — every later run must match
the recorded hash. The structural anchors below make that first pin deterministic
and reproducible rather than arbitrary.

- **START anchor** = the first sentence of the argument body (after title/byline/
  abstract-metadata as noted per source).
- **END anchor** = the last sentence of the argument body (before notes /
  references / comments / site footer).
- On first retrieval, record the exact first ~8 and last ~8 words actually
  present, the retrieval date, and the SHA-256 of the extracted text in the
  `RECORDED` block for that source.

---

## Cluster A — abundance

### roosevelt-democratic-abundance
- **Cite:** Roosevelt Institute, "Democratic Abundance: An Abundance That Works for Workers."
- **URL:** https://rooseveltinstitute.org/publications/democratic-abundance/
- **START:** first sentence of the report body after the title/author/date block.
- **END:** last sentence before footnotes/citations, "related publications," or site footer.
- **EXCLUDE:** nav, author bios, footnote list, share/related widgets, newsletter CTA.
- **RECORDED:** `<first-words … last-words | retrieved YYYY-MM-DD | sha256: …>` (pending first run)

### current-affairs-abandon-abundance
- **Cite:** Current Affairs, "Abandon 'Abundance.'"
- **URL:** https://www.currentaffairs.org/news/abandon-abundance
- **START:** first sentence of the article body after headline/byline/deck.
- **END:** last sentence before comments, "support us" CTA, or footer.
- **EXCLUDE:** nav, deck/subhead if duplicated, donation/subscription CTAs, comments.
- **RECORDED:** `<pending first run>`

### reason-problem-with-abundance-agenda
- **Cite:** Reason, "The Problem With the 'Abundance Agenda.'"
- **URL:** https://reason.com/2023/03/03/the-problem-with-the-abundance-agenda/
- **START:** first sentence of the article body after headline/byline.
- **END:** last sentence before "RELATED," comments, or footer.
- **EXCLUDE:** nav, ad slots, related-links, comments, newsletter CTA.
- **RECORDED:** `<pending first run>`

### cato-industrial-policy-bad-idea
- **Cite:** Cato Institute, "Industrial Policy: A Bad Idea Is Back," *Cato Policy Report* (Jul/Aug 2021).
- **URL:** https://www.cato.org/policy-report/july/august-2021/industrial-policy-bad-idea-back
- **START:** first sentence of the essay body after title/author/issue block.
- **END:** last sentence before endnotes, "about the author," or footer.
- **EXCLUDE:** nav, issue masthead, author bio, endnote list, share widgets.
- **RECORDED:** `<pending first run>`

## Cluster B — AI & tech futures

### andreessen-techno-optimist-manifesto
- **Cite:** Marc Andreessen, "The Techno-Optimist Manifesto," a16z (Oct 2023).
- **URL:** https://a16z.com/the-techno-optimist-manifesto/
- **START:** first line of the manifesto body (the opening "We are told…"-type line) after title.
- **END:** last line of the manifesto body before the "patron saints" / credits list and footer.
- **EXCLUDE:** nav, the patron-saints/credits appendix (it is a list, not argument), footer. **Note:** if a run wants to test whether the credits list is argument or ornament, record that as a separate variant; the default analyzed text excludes it.
- **RECORDED:** `<pending first run>`

### amodei-machines-of-loving-grace
- **Cite:** Dario Amodei, "Machines of Loving Grace" (Oct 2024).
- **URL:** https://darioamodei.com/essay/machines-of-loving-grace
- **START:** first sentence of the essay body after the title.
- **END:** last sentence of the conclusion before any footnotes or site footer.
- **EXCLUDE:** nav, footnote list, footer.
- **RECORDED:** `<pending first run>`

### bender-stochastic-parrots
- **Cite:** Bender, Gebru, McMillan-Major, Shmitchell, "On the Dangers of Stochastic Parrots: Can Language Models Be Too Big? 🦜," FAccT '21. DOI 10.1145/3442188.3445922.
- **URL:** https://dl.acm.org/doi/10.1145/3442188.3445922 — **prefer a stable PDF** (ACM may gate); if using an open author copy, record which.
- **START:** the Abstract's first sentence (academic paper: abstract + body are the argument).
- **END:** the last sentence of the Conclusion (section before Acknowledgments).
- **EXCLUDE:** ACM header/citation block, author affiliations, Acknowledgments, References, appendices, page furniture.
- **RECORDED:** `<pending first run — also record which copy (ACM vs. open PDF) was used>`

## Cluster C — criminal justice

### aecf-eliminate-confinement
- **Cite:** Annie E. Casey Foundation, "Eliminate Confinement as a Response to Probation Rule Violations."
- **URL:** https://www.aecf.org/resources/eliminate-confinement-as-a-response-to-probation-rule-violations
- **START:** first sentence of the brief body after title/date.
- **END:** last sentence of the argument before "download," "related," or footer.
- **EXCLUDE:** nav, download CTAs, related-resources, footer.
- **RECORDED:** `<pending first run>`

### ppi-one-size-fits-none
- **Cite:** Prison Policy Initiative, "One Size Fits None: How 'standard conditions' of probation set people up to fail."
- **URL:** https://www.prisonpolicy.org/reports/probation_conditions.html
- **START:** first sentence of the report body after title/byline/date.
- **END:** last sentence before the Footnotes/Methodology section or footer.
- **EXCLUDE:** nav, footnotes, methodology appendix, donation CTA, footer.
- **RECORDED:** `<pending first run>`

## Cluster D — long-form hybrid

### coates-case-for-reparations
- **Cite:** Ta-Nehisi Coates, "The Case for Reparations," *The Atlantic* (June 2014).
- **URL:** https://www.theatlantic.com/magazine/archive/2014/06/the-case-for-reparations/361631/ — **paywall likely**; use an accessible/library copy and record which.
- **START:** the Roman-numeral-section "I." opening (the Clyde Ross narrative begins the body); include from the essay's first body sentence after the title/epigraph.
- **END:** the last sentence of the final numbered section before magazine footer/related.
- **EXCLUDE:** magazine chrome, photo captions if not part of the prose, "more stories," footer. Note the essay's section epigraphs are part of the text — keep them.
- **RECORDED:** `<pending first run — record which copy was used>`

---

*Adding a referenced fixture: add a metadata block here (never a diagnosis), and
put the answer key in the fixture's `groundtruth.md`. The two files must stay
disjoint — that separation is what keeps blind runs blind.*
