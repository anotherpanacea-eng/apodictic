# Source 3 — GPT

**Provenance:** GPT output, pasted by the maintainer 2026-06-09, answering the elicitation prompt in `../legal-risk-detection-level-setting.md`. Structured capture (distinctive content + all citations); the maintainer's original paste is canonical. **Not legal advice.**

## Shape
**10 risk classes** — Defamation; Privacy (private facts / intrusion / false light); Copyright; Trademark/trade-dress/false-endorsement; **Contracts/NDAs/confidentiality** (separate); **Trade secrets** (separate, DTSA); **Life rights / releases** (separate); Right of publicity / misappropriation; IIED & dignitary claims; **Legally restricted information & publication-process violations** (sealed/gag/grand-jury/classified/sub-judice/unlawful-acquisition). Each with the 7 fields. **Most operational:** explicit tier semantics ("`monitor` = record + preserve; `review-recommended` = prepublication legal read; `review-now` = publication hold"), and a large `UPPER_SNAKE_CASE` escalation-trigger taxonomy whose tiers are "default... raised or lowered only through documented answers." **Most current + most citation-disciplined of the four** (avoids the §3344/§3344.1 error).

## Citations (as given)
- US — defamation/privacy/IIED: *Sullivan* 376 U.S. 254 (1964); *Gertz* 418 U.S. 323 (1974); *Milkovich v. Lorain Journal* 497 U.S. 1 (1990); *Bindrim v. Mitchell* 92 Cal. App. 3d 61 (1979); *Time, Inc. v. Hill* 385 U.S. 374 (1967); *Cox Broadcasting* 420 U.S. 469 (1975); *Florida Star* 491 U.S. 524 (1989); *Bartnicki v. Vopper* 532 U.S. 514 (2001); *Hustler v. Falwell* 485 U.S. 46 (1988).
- US — copyright: 17 U.S.C. §107; *Harper & Row v. Nation* 471 U.S. 539 (1985); *Campbell v. Acuff-Rose* 510 U.S. 569 (1994); **_Andy Warhol Foundation v. Goldsmith_ 598 U.S. 508 (2023)** (transformative-purpose narrowed) — *only GPT cites this*; US Copyright Office Fair Use Index.
- US — trademark/publicity: 15 U.S.C. §1125(a); *Rogers v. Grimaldi* 875 F.2d 994 (2d Cir. 1989); **_Jack Daniel's v. VIP Products_ 599 U.S. 140 (2023)**; *Dastar v. Fox* 539 U.S. 23 (2003); *Zacchini* 433 U.S. 562 (1977); *Comedy III v. Saderup* 25 Cal. 4th 387 (2001); NY Civ. Rights Law §§50, 51, 50-f.
- US — promises/secrecy/trade secrets: *Cohen v. Cowles Media* 501 U.S. 663 (1991); *Snepp* 444 U.S. 507 (1980); 28 C.F.R. §17.18; 18 U.S.C. §§1833(b), 1836, 1839 (DTSA).
- UK/EU/AU: Defamation Act 2013 ss.1–4; *Lachaux* [2019] UKSC 27; *Campbell v MGN* [2004] UKHL 22; CDPA 1988 ss.30, 30A; ECHR Arts 8/10; GDPR Art 85; Defamation Act 2005 (NSW) s.10A; Privacy & Other Legislation Amendment Act 2024 (Cth) Sch 2 (statutory privacy tort, commenced 10 June 2025).
- Practitioner: Reporters Committee First Amendment Handbook; Authors Guild guidance; US Copyright Office materials.

## Confidence/gaps it self-flagged
Highest on the content detectors + statutory/case anchors. Unsettled: mechanical identifiability threshold; defamatory implication; public/private-figure classification (never auto-assign); newsworthiness; **fair use after *Warhol*** (contested); fictionalization/composites; AI likeness/voice (fast-moving); AU 2025 tort immature; GDPR Art 85 member-state variance; UK/AU reporting restrictions can't be inferred from text; professional privileges need per-profession modules; publisher warranties/insurance are separate. Central limit stated: "the tool can identify risk-bearing combinations... a lawyer must determine legal elements, defenses, choice of law, evidentiary sufficiency, and acceptable residual risk."

> Triangulation notes live in `../legal-risk-detection-level-setting.md` §Synthesis.
