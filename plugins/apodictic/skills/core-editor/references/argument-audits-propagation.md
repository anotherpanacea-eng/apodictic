<!-- argument-audits-propagation.md — Fragment extracted from pass-dependencies.md §4e.
     Canonical home for argument-cluster audit-signal propagation rows.
     Loaded by audit-signal-propagation validator alongside the main §4e table.
     Source rows are marked replaced-with-include in pass-dependencies.md §4e. -->

# Argument Audits — Signal Propagation Fragment

*This fragment contains the argument-cluster rows from `pass-dependencies.md §4e` (Audit-Signal
Propagation Table). The `audit-signal-propagation` validator loads both the main §4e table in
`pass-dependencies.md` and this fragment when checking argument-shaped runs.*

*The content below is byte-identical to the rows that appeared in `pass-dependencies.md §4e`
before the Phase A carve. The §4e before/after diff at `evals/fixtures/argument-carve/4e-before-after.diff`
confirms this — only location changed.*

---

#### Argument cluster (Dialectical Clarity, Argument Red Team, Argument Persuasion, Argument Evidence, Adversarial Evidence Review, Field Recon, Citation Verifier)

| Audit | Audit-internal signal | Synthesis severity | Context modifier | Source | Override |
|---|---|---|---|---|---|
| Dialectical Clarity | WR0 (warrant gap) at HIGH burden audience | Must-Fix | Burden level HIGH from §Step 1 (policy brief, expert testimony) | `craft/dialectical-clarity.md` §Step 4 WR codes + §Step 1 burden | Refines default (audience-calibrated) |
| Dialectical Clarity | WR0 (warrant gap) at MEDIUM burden audience | Should-Fix | Burden level MEDIUM | `craft/dialectical-clarity.md` §Step 4 WR codes | — |
| Dialectical Clarity | WR1 (missing backing for contested warrant) | Must-Fix | Always | `craft/dialectical-clarity.md` §Step 4 WR codes | — |
| Dialectical Clarity | CL2 (subclaim gap) | Must-Fix | Always | `craft/dialectical-clarity.md` §CL codes | — |
| Dialectical Clarity | OB4 (concession without cost) | Should-Fix | Pattern-level concession theater | `craft/dialectical-clarity.md` §OB codes | — |
| Dialectical Clarity | BP2 (scope creep) | Should-Fix | Always; upgrade to Must-Fix if BP2 in conclusion | `craft/dialectical-clarity.md` §BP codes | Refines default (location-sensitive) |
| Argument Red Team | RT-flag at Fatal severity | Must-Fix | Adversary can defeat the argument entirely | `craft/argument-red-team.md` §Severity Scale | — |
| Argument Red Team | RT-flag at Major severity | Should-Fix | Real vulnerability; argument needs reinforcement | `craft/argument-red-team.md` §Severity Scale | — |
| Argument Red Team | RT-flag at Manageable severity | Could-Fix | Limited blast radius | `craft/argument-red-team.md` §Severity Scale | — |
| Argument Persuasion | PS-flag fortification failure (audience-posture mismatch) | Should-Fix | Pattern across ≥2 audience postures | `craft/argument-persuasion.md` §PS signals | — |
| Argument Persuasion | PS-flag at hard-rule violation | Must-Fix | Hard rule fires (e.g., concession-without-cost convergence) | `craft/argument-persuasion.md` §7 Hard Rules | — |
| Argument Evidence | AE10 (Verification Hotspot Cluster) | Must-Fix | Always; per Hard Gate #1 (Evidence Ledger escalates) | `craft/argument-evidence.md` §Hard Gates | — |
| Argument Evidence | AE1 on C0 support (provenance opaque on central claim) | Must-Fix | Always; per Hard Gate #2 | `craft/argument-evidence.md` §Hard Gates | — |
| Argument Evidence | AE2 (Secondary Flattening) | Should-Fix | Pattern across ≥2 supports; Must-Fix if confirmed via Citation Verifier | `craft/argument-evidence.md` §Named flags | Refines default (verification-conditional) |
| Argument Evidence | AE5 + AE6 co-occurrence (testimony boundary) | Must-Fix | Per Hard Gate #3 (handoff to Coaching Track 8) | `craft/argument-evidence.md` §Hard Gates | — |
| Argument Evidence | AE3 / AE4 / AE7 / AE8 / AE9 isolated | Should-Fix | Pattern-level; upgrade to Must-Fix on convergence | `craft/argument-evidence.md` §Named flags | — |
| Adversarial Evidence Review | HX-class survivability failure (claim cannot survive hostile expert scrutiny) | Must-Fix | Survivability judgment = Vulnerable across multiple protocols | `craft/adversarial-evidence-review.md` §HX/LX/SX | — |
| Adversarial Evidence Review | LX-class limited-survival failure | Should-Fix | Survives some protocols; not all | `craft/adversarial-evidence-review.md` §HX/LX/SX | — |
| Adversarial Evidence Review | SX-class stable-claim flag | Could-Fix | Survives all protocols; flag for documentation | `craft/adversarial-evidence-review.md` §HX/LX/SX | — |
| Field Reconnaissance | Counterevidence surfaced post-Field-Recon contradicting C0 | Must-Fix | Direct contradiction of central claim | `craft/research-field-recon.md` §Output | — |
| Field Reconnaissance | Counterevidence surfaced post-Field-Recon weakening subclaim | Should-Fix | Subclaim weakened, central claim stands | `craft/research-field-recon.md` §Output | — |
| Field Reconnaissance | Literature-gap flag (no counterevidence found despite expected adversarial pressure) | Could-Fix | Documents the search; no actionable finding | `craft/research-field-recon.md` §Output | — |
| Citation Verifier | Ghost citation (CV-class verdict: source does not exist) | Must-Fix | Always | `craft/research-citation-verifier.md` §Verdict tiers | — |
| Citation Verifier | Misquoted / misattributed citation | Should-Fix | Source exists but quote/attribution inaccurate | `craft/research-citation-verifier.md` §Verdict tiers | — |
| Citation Verifier | Stale or unverifiable citation | Could-Fix | Source unreachable but no evidence of fabrication | `craft/research-citation-verifier.md` §Verdict tiers | — |
