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
- On first retrieval the preparer caches the extracted text **outside the git
tree** (sibling of the repo — copyrighted full text is never committed) and
records, in the source's `RECORDED` block below, the SHA-256, byte count,
retrieval date, and method. Format:
`retrieved YYYY-MM-DD | method | N bytes | sha256: <hex>`. The cache is a
convenience; re-fetch at run time is still the default, and any re-fetch must
reproduce the recorded SHA-256.

**Extraction convention used for the recorded hashes (2026-05-30 cache):**
boilerplate (nav, donate/subscribe, footers, social) stripped; **article body,
headings, and footnotes preserved.** This means the recorded hashes include
footnotes even where an `EXCLUDE` line below names a "footnote list" — the
preserve-footnotes convention is authoritative for the hash (footnotes are part
of an argument's support apparatus). `EXCLUDE` still governs nav/CTA/chrome.

---

## Cluster A — abundance

### roosevelt-democratic-abundance
- **Cite:** Roosevelt Institute, "Democratic Abundance: An Abundance That Works for Workers."
- **URL:** https://rooseveltinstitute.org/publications/democratic-abundance/
- **START:** first sentence of the report body after the title/author/date block.
- **BODY_START:** `## Key Takeaways`
- **END:** last sentence before footnotes/citations, "related publications," or site footer.
- **EXCLUDE:** nav, author bios, footnote list, share/related widgets, newsletter CTA.
- **RECORDED:** `retrieved 2026-05-30 | web_fetch | 39013 bytes | sha256: d4d5a70b16012cbc2d9222f4218349519e296adab0ba05318206e75e3915e6bf`

### current-affairs-abandon-abundance
- **Cite:** Current Affairs, "Abandon 'Abundance.'"
- **URL:** https://www.currentaffairs.org/news/abandon-abundance
- **START:** first sentence of the article body after headline/byline/deck.
- **BODY_START:** `Well, it looks like Abundance isn't going away`
- **END:** last sentence before comments, "support us" CTA, or footer.
- **EXCLUDE:** nav, deck/subhead if duplicated, donation/subscription CTAs, comments.
- **RECORDED:** `retrieved 2026-05-30 | web_fetch | 26069 bytes | sha256: 6352c7c92ba244874cd2f602e5366e2a0bcba9be4c74aeeccbf4663c82fd7d95`

### reason-problem-with-abundance-agenda
- **Cite:** Reason, "The Problem With the 'Abundance Agenda.'"
- **URL:** https://reason.com/2023/03/03/the-problem-with-the-abundance-agenda/
- **START:** first sentence of the article body after headline/byline.
- **BODY_START:** `With much fanfare, the Biden administration announced`
- **END:** last sentence before "RELATED," comments, or footer.
- **EXCLUDE:** nav, ad slots, related-links, comments, newsletter CTA.
- **RECORDED:** `retrieved 2026-05-30 | web_fetch | 15890 bytes | sha256: e103ac687a7238207e6720e99b5686ad8415de09c3688a9952bf538aeb312345`

### cato-industrial-policy-bad-idea
- **Cite:** Cato Institute, "Industrial Policy: A Bad Idea Is Back," *Cato Policy Report* (Jul/Aug 2021).
- **URL:** https://www.cato.org/policy-report/july/august-2021/industrial-policy-bad-idea-back
- **START:** first sentence of the essay body after title/author/issue block.
- **BODY_START:** `In the wake of the COVID-19 pandemic`
- **END:** last sentence before endnotes, "about the author," or footer.
- **EXCLUDE:** nav, issue masthead, author bio, endnote list, share widgets.
- **License:** CC BY-NC-SA 4.0 (Cato) — compatible with this repo's license.
- **RECORDED:** `retrieved 2026-05-30 | Chrome render (web_fetch returned a JS shell) | 19718 bytes | sha256: c1f8895c84243d6a5fda8a42ffc9d1d1a69f02886c680ecb383a31fc1f629a7a`

## Cluster B — AI & tech futures

### andreessen-techno-optimist-manifesto
- **Cite:** Marc Andreessen, "The Techno-Optimist Manifesto," a16z (Oct 2023).
- **URL:** https://a16z.com/the-techno-optimist-manifesto/
- **START:** first line of the manifesto body (the opening "We are told…"-type line) after title.
- **END:** last line of the manifesto body before the "patron saints" / credits list and footer.
- **EXCLUDE:** nav, the patron-saints/credits appendix (it is a list, not argument), footer. **Note:** if a run wants to test whether the credits list is argument or ornament, record that as a separate variant; the default analyzed text excludes it.
- **RECORDED:** `retrieved 2026-05-30 | web_fetch | 33619 bytes | sha256: 1ba705936f3b4deb560d8b53a0f08690d40f16a13048a39615a80cf4e55924f3`

### amodei-machines-of-loving-grace
- **Cite:** Dario Amodei, "Machines of Loving Grace" (Oct 2024).
- **URL:** https://darioamodei.com/essay/machines-of-loving-grace
- **START:** first sentence of the essay body after the title.
- **END:** last sentence of the conclusion before any footnotes or site footer.
- **EXCLUDE:** nav, footnote list, footer.
- **RECORDED:** `retrieved 2026-05-30 | web_fetch | 91273 bytes | sha256: c089c0ff8a4345473a1d60b1c01f4380d1ecf940158b9384a718d0e857de3dc5`

### bender-stochastic-parrots
- **Cite:** Bender, Gebru, McMillan-Major, Shmitchell, "On the Dangers of Stochastic Parrots: Can Language Models Be Too Big? 🦜," FAccT '21. DOI 10.1145/3442188.3445922.
- **URL:** https://dl.acm.org/doi/10.1145/3442188.3445922 — **prefer a stable PDF** (ACM may gate); if using an open author copy, record which.
- **START:** the Abstract's first sentence (academic paper: abstract + body are the argument).
- **END:** the last sentence of the Conclusion (section before Acknowledgments).
- **EXCLUDE:** ACM header/citation block, author affiliations, Acknowledgments, References, appendices, page furniture.
- **License:** CC BY 4.0 (open-access FAccT '21 PDF).
- **RECORDED:** `retrieved 2026-05-30 | local PDF + pdftotext (open-access copy) | 69145 bytes | sha256: 1928f4018c264800139b428dcaea851f10cd623091d533ad01cd692585057f9a`
- **Extraction caveats:** bibliography dropped, running headers/footers stripped. Minor two-column artifact at the abstract/intro seam (text complete; a few lines reordered) and Table 1 renders as stacked values. None affect the GT1–GT3 anchors, but a scorer should not read the seam reordering as a structural finding.

## Cluster C — criminal justice

### aecf-eliminate-confinement
- **Cite:** Annie E. Casey Foundation, "Eliminate Confinement as a Response to Probation Rule Violations."
- **URL (landing):** https://www.aecf.org/resources/eliminate-confinement-as-a-response-to-probation-rule-violations — landing page only; the substance is in the linked PDF.
- **SOURCE_PDF (the actual analyzed text):** https://assets.aecf.org/m/resourcedoc/aecf-eliminateconfinementasresponse-2020.pdf
- **START:** first sentence of the report body after title/date.
- **END:** last sentence of the argument before "download," "related," or footer.
- **EXCLUDE:** nav, download CTAs, related-resources, footer.
- **RECORDED:** `retrieved 2026-05-30 | web_fetch (PDF) | 18885 bytes | sha256: 69491f3335858edeae3663331fd873d31c2a451b17ff4c4e7d32705b614b2df9`

### ppi-one-size-fits-none
- **Cite:** Prison Policy Initiative, "One Size Fits None: How 'standard conditions' of probation set people up to fail."
- **URL:** https://www.prisonpolicy.org/reports/probation_conditions.html
- **START:** first sentence of the report body after title/byline/date.
- **BODY_START:** `Table of Contents:`
- **END:** last sentence before the Footnotes/Methodology section or footer.
- **EXCLUDE:** nav, methodology appendix, donation CTA, footer. (Footnotes 1–68 preserved.)
- **RECORDED:** `retrieved 2026-05-30 | web_fetch | 77509 bytes | sha256: 4944b26c9b2392d523530cc6f807e2024052a6b1ca016e83d650bb54fc0ecb4a`
- **Extraction caveat:** footnote 41 was absent from the source (text jumps fn 40 → 42); a bracketed placeholder marks the gap. Immaterial to GT1–GT3.

## Cluster D — long-form hybrid

### coates-case-for-reparations
- **Cite:** Ta-Nehisi Coates, "The Case for Reparations," *The Atlantic* (June 2014).
- **URL:** https://www.theatlantic.com/magazine/archive/2014/06/the-case-for-reparations/361631/ — **paywall likely**; use an accessible/library copy and record which.
- **START:** the Roman-numeral-section "I." opening (the Clyde Ross narrative begins the body); include from the essay's first body sentence after the title/epigraph.
- **END:** the last sentence of the final numbered section before magazine footer/related.
- **EXCLUDE:** magazine chrome, photo captions if not part of the prose, "more stories," footer. Note the essay's section epigraphs are part of the text — keep them.
- **RECORDED:** `retrieved 2026-05-30 | corrected re-extraction (coates-case-for-reparations-corrected.md) | 100281 bytes | sha256: d4407650b3ceafcc5853418e158fa00a1d32aac7979e5d190bd7a27032f987d2`
- **Provenance note:** supersedes a 2026-05-30 extraction (`sha256: 2cce74f1…f457a07`, 98516 bytes) that had two ordering artifacts — an out-of-sequence predatory-lending block at the end and interleaved photo captions / "Auschwitz All Around Us" sidebar. The corrected copy restores the predatory-lending block (Rugh & Massey; Wells Fargo / Beth Jacobson; Bank of America) to sequence and removes the interleaved captions/sidebar. Sections I–X intact; section epigraphs preserved. Caveat lifted — Coates is now a load-bearing fixture.

---

*Adding a referenced fixture: add a metadata block here (never a diagnosis), and
put the answer key in the fixture's `groundtruth.md`. The two files must stay
disjoint — that separation is what keeps blind runs blind.*
