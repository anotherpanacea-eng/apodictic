# Legal-Risk Detection Playbook — level-setting research

**Status:** Level-setting research — **all 4 sources in; synthesis complete and built** into `core-editor/references/legal-risk-register.md` §Detection guidance / §Escalation-trigger taxonomy (lean runtime layer; citations stay here, not in the runtime module). Fed two deferred Legal Risk Register increments — **per-class detection guidance** and the **standardized escalation-trigger taxonomy** (`docs/legal-risk-register.md` future increments; `intake-router-design.md` § remaining gaps). **Firewall: flag, don't practice law.** Everything here informs *detection* heuristics only; nothing is legal advice, and a qualified human lawyer is the final gate.

## Method

Cross-model deep-research elicitation: one prompt (below) run through multiple models (Muse Spark, Claude, GPT, Gemini), synthesized by **triangulation, not averaging** — agreement → high confidence; single-source → flag; divergence → surface (divergences cluster on jurisdiction-dependence, which the tool should itself *flag*, not resolve). Citations are tiered by corroboration; unverifiable ones are marked for the lawyer gate. The synthesis maps onto `apodictic.legal_risk.v1` (`risk_class` · `severity` = base tier raised by documented modifiers · `escalation_trigger` = a coded trigger · `concern` · `disposition` = route to counsel).

## Sources

| # | Model | File | Shape |
|---|---|---|---|
| 1 | Muse Spark | `sources/muse-spark.md` | 6 classes; US-centric; strong core citations; leanest |
| 2 | Claude | `sources/claude.md` | 13 classes; coded taxonomy + tier-raising modifiers; rich UK/AU/EU (contempt, breach of confidence, religious-hatred) |
| 3 | GPT | `sources/gpt.md` | 10 classes; most operational + most current (Warhol/Jack Daniel's 2023, AU 2025); most citation-disciplined; adds trade secrets, life-rights, restricted-info/publication-process |
| 4 | Gemini | `sources/gemini.md` | Deep-Research with live source URLs (most verifiable — the citation anchor); adds **incitement / instructional liability** (Rice v. Paladin) + Bonome, Haynes, Suntrust (parody), de Havilland (docudrama), Coco v. Clark |

## Synthesis (complete — all 4 sources)

### Convergence → high-confidence backbone
- **US core, identical across the first three sources (Gemini corroborates — see below):** defamation (Sullivan actual-malice; Gertz private-figure); fair use as a non-mechanical four-factor test (§107) with *no safe word count*; strong (fact-specific) protection for truthful public-record info (Cox; Florida Star); GDPR Art 9 / Art 85 for EU; lyrics/poetry/unpublished material as the perennial copyright trap.
- **Severity model converges:** Claude's *tier-raising modifiers* and GPT's *"tier is a default, raised/lowered only through documented answers"* are the same computational shape — **base-class tier + documented modifiers**. Adopt this as the `severity` mechanism (maps cleanly to monitor / review-recommended / review-now).

### Corrections surfaced by triangulation
- **False light = Restatement §652E** (Muse cited only §§652B–D; Claude + GPT correct). Use §652E.
- **CA post-mortem publicity is §3344.1, not §3344** — Muse and Claude both say "70 years" but mis-attribute the section; **GPT avoids the error** (cites NY §50-f for post-mortem, Comedy III for CA's transformative test, doesn't over-specify the CA section). Net: term corroborated, section to fix; flag for lawyer.
- **Recognition is not universal:** false light and public-disclosure torts are *not recognized in every US state* (Muse implied near-universality; Claude + GPT both flag NY/NC/CO etc.). Treat both as jurisdiction-contingent — a `+US-State-variation` modifier.

### Coverage (union of classes; GPT + Claude expand well past Muse)
Defamation · Privacy: private-facts / intrusion / false-light (split) · Copyright · Trademark/trade-dress/false-endorsement · Right of publicity / misappropriation · Contracts/NDAs/confidentiality · **Trade secrets** (GPT) · **Life rights / releases** (GPT) · **Restricted info & publication-process** — sealed/gag/grand-jury/classified/sub-judice (GPT + Claude) · IIED · Breach of confidence (Claude, UK/AU) · Contempt/sub-judice (Claude) · Religious-hatred/blasphemy non-US (Claude).

### Backbone to build on
GPT's `UPPER_SNAKE_CASE` trigger taxonomy (operational, tier-tagged) **×** Claude's tier-raising modifiers **×** GPT's class granularity (trade-secret / restricted-info split out) → the escalation-trigger taxonomy. Muse corroborates the US core.

### Citation posture (preliminary triage)
- **Corroborated across ≥2, high confidence:** Sullivan, Gertz, Cox, Florida Star, Hustler v. Falwell, Campbell v. Acuff-Rose, Harper & Row, Zacchini, Rogers v. Grimaldi, Jack Daniel's (2023), Snepp, §107, §1125(a), GDPR Art 9, UK Defamation Act 2013 s1, AU serious-harm + 2025 privacy tort, Restatement §§652B–E.
- **Single-source, verify at merge:** GPT-only — Milkovich (497 U.S. 1), Bartnicki (532 U.S. 514), **Andy Warhol v. Goldsmith (598 U.S. 508, 2023)**, Dastar (539 U.S. 23), Cohen v. Cowles Media (501 U.S. 663), Comedy III (25 Cal. 4th 387), NY Civ. Rights L. §§50/51/50-f, Lachaux [2019] UKSC 27, DTSA (18 U.S.C. §§1833(b)/1836/1839), 28 C.F.R. §17.18; Claude-only — Berisha v. Lawson (141 S. Ct. 2424), PJS [2016] UKSC 26, Irvine v Talksport, Contempt of Court Act 1981. (Most look real on inspection; the Warhol/Jack Daniel's 2023 pair materially updates fair-use + trademark posture and should be kept.)
- **To verify:** Claude's "Bindrim *contract* count failed" nuance (single-source); GPT's 28 C.F.R. §17.18 pinpoint; any UK pinpoint quotes (both flagged self-uncertain).

### What Gemini added / confirmed (4th source)
- **New class — Incitement / instructional liability** (none of the others had it): *Rice v. Paladin* (4th Cir. 1997, the "Hit Man" murder-manual case) + the *Brandenburg* imminent-lawless-action line. Add it (step-by-step how-to-commit-a-violent-crime manuals → `review-now`).
- **Strong corroboration with verifiable URLs** (Gemini is a Deep-Research output with clickable sources, so it anchors the citation check): parody fair use (*Suntrust v. Houghton Mifflin* / *The Wind Done Gone*, corroborating *Campbell*); public-record/newsworthiness (*Haynes v. Knopf*, corroborating *Cox*/*Florida Star*); false-light-not-universal (*Renwick* / NC, corroborating Claude+GPT on state variance); right-of-publicity-for-expressive-works strongly protected (*Olivia de Havilland v. FX* — "clearance culture" rejected — corroborating *Rogers*/*Comedy III* as a false-positive guard); UK breach of confidence elements (*Coco v. A.N. Clark*); memoir intimate-disclosure (*Bonome v. Kaysen*).
- **Confirms the §3344.1 finding:** Gemini (like GPT) does *not* repeat the §3344-vs-§3344.1 mis-attribution — so the error is **Muse + Claude only (2 of 4)**; the underlying fact (CA 70-yr / NY 40-yr post-mortem) is corroborated by all four.

### Finalized class set (union, deduplicated → the increment's `risk_class` list)
Defamation · Privacy: private-facts · Privacy: intrusion · Privacy: false-light · Copyright · Trademark / trade-dress / false-endorsement · Right of publicity / misappropriation · Contracts / NDAs / confidentiality · Trade secrets · Life rights / releases · IIED & dignitary · **Incitement / instructional liability** (Gemini) · Breach of confidence (UK/AU) · Contempt / sub-judice (UK/AU) · Religious-hatred / blasphemy (non-US) · Restricted info & publication-process (sealed/gag/grand-jury/classified). (The existing schema's `risk_class` enum is `defamation | privacy | rights-clearance | other`; the increment can either widen that enum or keep it and carry the finer class as a sub-tag — a spec decision for the build.)

### Recommendation (next step, through the normal loop)
The synthesis is ready to become the **Legal Risk Register detection increment**: (1) per-class detection guidance = the merged 7-field entries, severity computed as *base-class tier + documented modifiers* (the GPT×Claude convergence); (2) the escalation-trigger taxonomy = GPT's `UPPER_SNAKE` codes × Claude's modifiers; (3) a citations appendix tiered by corroboration, with the 2-of-4 §3344.1 fix applied and the single-source items (esp. GPT-only *Warhol*/*Dastar*/DTSA, Claude-only *PJS*/*Irvine*, Gemini-only *Rice*/*Suntrust*/*de Havilland*) marked for the lawyer gate. Spec → review → build → review, like everything else; a qualified lawyer remains the final gate.

## The elicitation prompt (as issued)

````text
# Deep-research request: a legal-risk DETECTION playbook for a manuscript-editing tool

## Role & context
You are advising on the *detection* layer of an editorial tool's "Legal Risk Register." The tool is run by a writer/editor (NOT a lawyer). Its firewall is **flag, don't practice law**: it must spot *candidate* areas of legal exposure in a book manuscript and route serious ones to a qualified attorney. It must NEVER render a legal conclusion ("this is not defamatory," "this is fair use," "no liability"). I need a research-grounded **detection playbook**: the textual signals that should make the tool flag exposure, organized by risk class, with escalation cues and route-to-counsel thresholds.

This is for memoir, autofiction, narrative/reported nonfiction, and fiction that draws on real people or copyrighted material — heading toward publication.

## What I need (the deliverable)
A per-class playbook. For **each risk class** below, provide:
1. **Detectable textual signals** — concrete things *in the prose* that should trigger a flag.
2. **Clarifying questions** the tool should ask the author to refine the flag.
3. **Escalation cues** — what moves a flag across `monitor` → `review-recommended` → `review-now`.
4. **Route-to-counsel threshold** — the bright line where human legal review is mandatory.
5. **False-positive traps** — what *looks* risky but usually isn't, with the reason.
6. **Jurisdiction caveats** — default US, but flag where UK / EU / Australia diverge materially.
7. **Genre nuance** — memoir/autofiction vs. reported nonfiction vs. fiction-with-real-people vs. satire/parody.

## Risk classes (cover all; propose any missing)
Defamation; Privacy (private facts / intrusion / false light); Rights-clearance (copyright esp. lyrics/poetry/excerpts/epigraphs/images + fair-use factors, trademark, contracts/NDAs, life-rights/releases); Right of publicity / misappropriation; and any **other** classes a publishing/media lawyer would add.

## Hard constraints
- **Cite only real, verifiable sources** (statutes with section, leading cases with correct citation + jurisdiction, recognized practitioner guides). **Do not invent** case names, citations, or statute numbers; if unsure a source is real, say so.
- **State jurisdictional assumptions up front**; mark every jurisdiction-dependent claim.
- **Flag uncertainty / unsettled law**, and where other expert sources or models would disagree.
- Keep the **per-class structure identical** (the 7 fields, same order) for comparison/merging.
- Stay in the **detection** lane: signals + escalation, never adjudication.

## Output format
Per class: the 7 numbered fields. Then **"Escalation-trigger taxonomy"** (consolidated, each tagged with its default tier). End with **"Sources"** (deduplicated, jurisdiction noted) and **"Confidence & gaps."**
````

---

*Level-setting research, complete. All four sources synthesized and built into `core-editor/references/legal-risk-register.md` (§Detection guidance / §Escalation-trigger taxonomy) as the Legal Risk Register detection layer — through the normal spec→review→build→review loop. Citations stay here, not at runtime. A human lawyer remains the final gate — the tool flags, tiers, and routes; it never clears.*
