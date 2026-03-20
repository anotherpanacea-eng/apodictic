# Companion Module: Argument Evidence Deep-Dive (v1.0)
## Nonfiction Argument Engine / APODICTIC
*Drafted: March 19, 2026*
*Status: Thin companion mode for Dialectical Clarity v2.0*
*Consumes: `Argument_State.md`*

---

## Purpose

This mode deepens the evidence dimension of a nonfiction argument **without duplicating** what Dialectical Clarity already diagnoses.

The core audit already handles:

1. support presence and relevance
2. warrant strength
3. burden and scope mismatch
4. evidence laundering as an argument failure
5. false precision and authority overreach at the structural level

This mode goes narrower and deeper on evidentiary legitimacy:

1. provenance chains
2. diversity and distribution of evidence types
3. testimony calibration
4. quantitative integrity
5. verification handoff

---

## Non-Duplication Boundary

### Dialectical Clarity owns

1. `SM` support mapping
2. `WR` warrant analysis
3. `BP` burden and scope
4. pattern-level flags like evidence laundering or false precision

### Argument Evidence Deep-Dive owns

1. where evidence comes from
2. how many removes away it is from origin
3. whether the evidence portfolio is over-dependent or under-balanced
4. whether testimony is carrying the right argumentative weight
5. which claims need factual verification before publication

### Factual Verification owns

1. external reality checking of specific claims
2. source confirmation
3. up-to-date factual validation

This mode should hand off to Factual Verification where appropriate. It does not itself browse or verify.

---

## Activation

Run when:

1. Dialectical Clarity identifies evidence-chain weakness around central claims
2. the manuscript is source-heavy, data-heavy, testimony-heavy, or citation-heavy
3. the user asks for provenance, source quality, testimony calibration, or evidence review
4. publication risk depends on whether evidence is trustworthy rather than merely relevant

---

## Required Inputs

### Precondition

`Argument_State.md` must exist with §§ 1–9 populated by Dialectical Clarity v2.0. If the state is absent or §§ 1–9 are unpopulated, refuse to run and direct the user to run `/audit dialectical` first. Do not silently re-derive the argument graph.

### What this module reads

Read from `Argument_State.md`:

1. § 2 Claim Architecture
2. § 3 Support Map
3. § 4 Warrant and Inference Map
4. § 5 Burden, Scope, and Comparative Assessment
5. § 7 Narrative-as-Evidence Inventory when testimony or anecdote is important
6. § 9 Diagnostic Summary

### What this module writes

1. § 10.1 Evidence Analysis
2. § 10.3 Verification and Research Handoff when external checking is needed

---

## Outputs

This mode produces:

1. `Evidence_Ledger.md`
2. `Argument_State.md` § 10.1 annotations
3. `Argument_State.md` § 10.3 verification handoff notes when needed

---

## Evidence Deep-Dive Dimensions

### 1. Provenance Chain (`EV1`)

How close is the manuscript's support to the primary evidence?

### 2. Evidence Portfolio Balance (`EV2`)

Is the argument over-reliant on one evidence type, source family, or narrative mode?

### 3. Testimony Calibration (`EV3`)

Is personal or witness evidence carrying observational, interpretive, and representative burdens appropriately?

### 4. Quantitative Integrity (`EV4`)

Are numbers, trends, and quantified claims presented with justified precision and methodological humility?

### 5. Verification Queue (`EV5`)

Which specific claims should be handed off for external factual checking before publication?

---

## Named Evidence Flags

| Code | Name | Description |
|---|---|---|
| `AE1` | Provenance Opacity | A support node's origin is unclear or too mediated to assess confidently |
| `AE2` | Secondary Flattening | Commentary or synthesis is treated as if it were the underlying primary evidence |
| `AE3` | Portfolio Narrowness | The argument depends too heavily on one evidence channel even after core support mapping |
| `AE4` | Representative Gap | The evidence is real but not obviously representative of the wider claim it is asked to support |
| `AE5` | Anecdote Glamour | Vivid anecdotal material is carrying more persuasive weight than its evidentiary position warrants |
| `AE6` | Testimony Boundary Blur | Observation, interpretation, and representative claim are not clearly separated |
| `AE7` | Orphaned Statistic | A number is present without enough method, denominator, timeframe, or source clarity |
| `AE8` | Methodless Precision | The precision of the claim exceeds what the underlying method or data granularity can bear |
| `AE9` | Credential Substitution | Institutional or expert authority is standing in for missing underlying support |
| `AE10` | Verification Hotspot Cluster | Multiple central claims require external checking before safe publication |

---

## Procedure

### Step 1: Select the evidence corridor

Do not reopen the whole manuscript. Focus on:

1. supports attached to `C0`
2. supports attached to the highest-severity subclaims
3. any support node flagged by DC codes `SM`, `WR0-3`, or `BP`, or by Red Team codes `RT9` (Evidence Chain Snap) or `RT11` (Standing and Scope Exposure)

### Step 2: Trace provenance

For each critical support node, record:

1. direct vs indirect
2. primary vs secondary
3. whether interpretation is layered through an intermediary

### Step 3: Assess portfolio balance

Ask:

1. is all the weight sitting on testimony?
2. is the case numerically dressed but conceptually thin?
3. are there too many examples and not enough reasons, or vice versa?

### Step 4: Calibrate testimony

For witness-heavy or anecdote-heavy work, separate:

1. what the evidence directly establishes (observation layer)
2. what it plausibly suggests (interpretation layer)
3. what requires broader support to justify (representative layer)

For each testimonial node, ask:

1. Is the witness positioned to know what they claim to know?
2. Is interpretation clearly marked as interpretation, not presented as fact?
3. Is the testimony asked to represent a pattern, population, or trend? If so, is that representative claim supported by anything beyond the testimony itself?
4. Would a hostile reader accept the testimony's observational core even if they rejected its interpretive frame?

If `AE5` and `AE6` co-fire in the same testimony corridor, hand off to the Coaching Protocol's Testimony Containment track (Track 8) rather than attempting to resolve here. The evidence module identifies the problem; the coaching module helps the writer repair it.

### Step 5: Build the verification queue

List the claims that should be handed to Factual Verification before publication.

Prioritize:

1. centrality to `C0`
2. reputational or legal risk
3. likelihood that a factual error would collapse the argument's credibility

---

## Annotation Format

### 10.1 Evidence Analysis

```markdown
### 10.1 Evidence Analysis
_Status: run by Argument Evidence Deep-Dive (v1.0) on [date/time]_

Primary evidence corridor:
- [...]

Key findings:
1. `AE2` Secondary Flattening — affects C1 support chain
2. `AE6` Testimony Boundary Blur — affects witness interpretation in V2
3. `AE8` Methodless Precision — affects quantified claim in body §3

Portfolio note:
- [...]
```

### 10.3 Verification and Research Handoff

```markdown
### 10.3 Verification and Research Handoff
_Status: populated by Argument Evidence Deep-Dive (v1.0) on [date/time]_

Claims requiring external verification:
1. [...]
2. [...]

Why they matter:
- [...]

Recommended handoff:
- Factual Verification research mode
```

---

## Hard Gates

1. If `AE10` fires (Verification Hotspot Cluster), the Evidence Ledger must escalate to the editorial letter — annotation in § 10.1 alone is insufficient.
2. If `AE1` fires on any support node attached to `C0`, provenance must be resolved before persuasion or compression coaching. An argument with an opaque evidentiary foundation for its central claim is not ready for audience recalibration.
3. If `AE5` (Anecdote Glamour) and `AE6` (Testimony Boundary Blur) co-occur, hand off to the Coaching Protocol's Testimony Containment track (Track 8) before continuing evidence analysis.
4. Never upgrade evidence quality based on the author's stated intentions. Assess what is on the page.
5. Never downgrade evidence quality because the form is informal. Op-ed evidence standards differ from academic standards, but provenance and representativeness still apply.

---

## Calibration by Form

| Form | Evidence norm | Signature risk | Watch for |
|---|---|---|---|
| Testimony | Witness position is the evidence; provenance is personal. Interpretation must be clearly separated from observation. | `AE6`, `AE5` | Testimony carrying representative weight it cannot bear |
| Policy brief | Data, comparison, and precedent expected. Sources should be traceable. | `AE7`, `AE8` | Orphaned statistics dressed as decisive proof |
| Op-ed | Compressed evidence acceptable if burden logic survives. One strong example may do more than three weak ones. | `AE3`, `AE4` | Portfolio narrowness disguised by vivid writing |
| Academic article | Primary sources expected. Provenance chain should be short. Method must be visible. | `AE1`, `AE2` | Secondary flattening — treating commentary as primary evidence |
| Open letter | Moral authority and witness position often substitute for data. Acceptable if the form's burden is met. | `AE9` | Credential substitution standing in for absent support |
| Advocacy journalism | Mix of data, testimony, and narrative. Portfolio balance matters more than in pure argument. | `AE3`, `AE5` | Anecdote glamour carrying the whole case |

---

## Handoff Rules

Hand off to Factual Verification when:

1. a central factual claim appears contestable
2. a cited number lacks method or source clarity
3. a chain of mediated authority is doing decisive work
4. publication risk turns on whether an external fact is current or accurate

Do not hand off simply because a reader *might* dislike the evidence base. The handoff should be targeted and claim-specific.

---

## Integration Notes

### With Dialectical Clarity

Use the core audit's map. Do not rebuild the structure.

### With Red Team

If Red Team finds `RT9` Evidence Chain Snap or `RT11` Standing and Scope Exposure`, this mode should often run next.

### With Persuasion

If persuasion guidance depends on foregrounding stronger support, this mode can tell the Persuasion module what the strongest support actually is.

---

## Bottom Line

Argument Evidence Deep-Dive is deliberately thin. Its job is not to become a second dialectical audit. Its job is to deepen the legitimacy of the evidence corridor already identified by the core audit and to hand off verifiable claims cleanly when publication-grade confidence is needed.
