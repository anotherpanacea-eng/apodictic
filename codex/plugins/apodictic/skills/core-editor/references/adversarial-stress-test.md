# Adversarial Reader Stress Test

*Reference file for the APODICTIC Development Editor. Loaded during every editorial letter synthesis.*

---

## Purpose

Identify what skeptical, uncharitable readers would criticize — not to wound, but to stress-test the manuscript before anyone else reads it. This element runs as part of every editorial letter, not only when publication intent is stated. "What would a hostile reader attack?" is a craft question, not a market question.

**History:** Extracted from Pass 11F (v1.0.0) to core synthesis (v1.0.1). The stress test applies to all manuscripts receiving editorial letters, regardless of whether Pass 11 is triggered.

---

## Fairness Guardrail

The stress test operates under strict constraints:
- **Low-charity:** Assumes the least favorable interpretation a reasonable reader could hold
- **Evidence-bound:** Every claim must point to specific textual evidence
- **No invented problems:** Cannot fabricate issues not present in the manuscript
- **No ad hominem tone:** Critiques the work, not the author; professional register throughout

---

## The Low-Charity Reader Frame

This is not the same as the §7 rejection memo. The rejection memo states the strongest *structural* case against the manuscript in 1-2 paragraphs. The stress test inhabits specific hostile reader types and surfaces what each would attack.

**Frame the reading as:**

> "Read this manuscript as someone who isn't predisposed to like it. You're looking for reasons to stop reading, reasons a review might cite, reasons an agent might pass. You're not unfair — you're not inventing problems — but you're not charitable either. Every weakness is noted. Every stumble logged. What claims would a hostile reader make?"

---

## Reader Profiles

The stress test considers multiple low-charity reader types:

| Reader Type | What They'd Attack | Example Claim |
|-------------|-------------------|---------------|
| **The Impatient** | Pacing, slow openings, delayed payoff | "Nothing had happened by page 30." |
| **The Skeptic** | Plot logic, character motivation, coincidences | "Why didn't she just call the police?" |
| **The Disappointed** | Promise vs. delivery, contract violations | "The cover promised romance. She dies." |
| **The Unforgiving** | Prose tics, repetition, craft failures | "The phrase 'let out a breath' appears twelve times." |
| **The Bored** | Lack of tension, predictability, low stakes | "I knew exactly how this would end by chapter 3." |

Not every reader type will produce findings for every manuscript. Use the profiles that apply. Minimum 3 findings, maximum 5.

---

## Assessment Structure

**Lock-then-test protocol:** For each finding, commit to severity and prevalence *before* generating the steelman defense. The defense cannot retroactively downgrade a severity rating — it can only note that the author has a counter-argument available. This ordering exists because LLMs reliably talk themselves out of hard findings when asked to generate both sides simultaneously.

**For each finding:**

| Field | Order | Description |
|-------|-------|-------------|
| **Adversarial Claim** | 1st | State the criticism as a low-charity reader would phrase it |
| **Evidence** | 2nd | Specific textual locations supporting the claim |
| **Confidence** | 3rd | `[HIGH]` / `[MEDIUM]` / `[LOW]` — per standard confidence calibration |
| **Severity** | 4th (LOCKED) | `Fatal` (rejection/abandonment) / `Damaging` (significant weakness) / `Irritating` (noticeable but survivable) |
| **Prevalence** | 5th (LOCKED) | `Rare` / `Some` / `Many` — what portion of target readers would this bother? |
| **Steelman Defense** | 6th | Best counter-argument the author or a sympathetic reader could make |
| **Does the claim survive?** | 7th | Restate the original severity. The defense may contextualize but cannot reduce it. If real readers have already reacted this way, the claim survives regardless of how good the defense sounds. |

**Anti-softening rule:** If a finding reaches this section, it has already passed the evidence and confidence thresholds. The steelman defense is informational — it tells the author what argument is available to them. It does not give the system permission to walk back the diagnosis. A finding with a strong defense is still a finding; it's just a finding the author can choose to accept as a trade-off. At least one finding in every stress test must survive with its full severity intact. If the system cannot produce a stress test where any claim lands, the stress test has failed — return to the low-charity frame and try again.

---

## Output Format

The stress test appears in the editorial letter as §8 (after the rejection memo). Author-facing language throughout — no framework codes in the body.

```markdown
## Adversarial Reader Stress Test

*What would an uncharitable reader find wrong with this manuscript?*

### [Claim Title]

**The claim:** "[Low-charity reader phrasing]"

**Where:** [Specific scenes/chapters]

**How serious:** [Fatal / Damaging / Irritating] — would bother [Rare / Some / Many] readers

**Best defense available:** [Steelman counter-argument the author could make]

**Verdict:** [Claim stands / Claim stands with caveat] — [reasoning]. Severity: [restate locked severity].

---

[Repeat for findings 2-5]

---

### Stress Test Summary

**How much damage would hostile scrutiny do?**

- Minor: Claims are real but unlikely to define reader response for most of the target audience
- Moderate: At least one claim would significantly affect reader experience for a meaningful portion of the audience
- Severe: Multiple claims would define reader response; manuscript is vulnerable to the readings described above

**Trade-off map:**
[For each finding: state whether it's worth revising for or is an acceptable cost of the manuscript's choices — but do not use "acceptable cost" to dismiss Fatal or Damaging findings with Many prevalence]
```

---

## Integration with Editorial Letter

- Stress test findings may overlap with §4 (What Needs Work) findings. This is expected — it means the adversarial framing confirms the structural diagnosis.
- New issues surfaced only by the stress test should be noted as such. They represent vulnerabilities that sympathetic reading missed.
- Stress test findings do NOT automatically escalate severity of existing findings. They provide a different lens, not a trump card.
- Fatal-severity + Many-prevalence findings that weren't already flagged in §4 should be flagged as potential additions to the revision checklist (§5).

---

## Firewall Compliance

The stress test maintains the Firewall:
- **ALLOWED:** Identifying what low-charity readers would claim, phrasing critiques as they would, assessing severity and prevalence
- **FORBIDDEN:** Rewriting passages, generating "better" versions, inventing fixes, proposing specific content changes

The stress test says "this is what they'd claim and why" — not "here's how to fix it." Fix guidance belongs in §4 and §5.
