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

This is not the same as the §6 rejection memo. The rejection memo states the strongest *structural* case against the manuscript in 1-2 paragraphs. The stress test inhabits specific hostile reader types and surfaces what each would attack.

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

**For each finding:**

| Field | Description |
|-------|-------------|
| **Adversarial Claim** | State the criticism as a low-charity reader would phrase it |
| **Evidence** | Specific textual locations supporting the claim |
| **Confidence** | `[HIGH]` / `[MEDIUM]` / `[LOW]` — per standard confidence calibration |
| **Severity** | `Fatal` (rejection/abandonment) / `Damaging` (significant weakness) / `Irritating` (noticeable but survivable) |
| **Prevalence** | `Rare` / `Some` / `Many` — what portion of target readers would this bother? |
| **Steelman Defense** | Best counter-argument available — what the author or a sympathetic reader would say |
| **Net Risk** | After considering defense, does the claim still land? |

**Note on Steelman Defense:** The defense exists to test the claim's strength, not to dismiss it. If the defense is stronger than the claim, the claim's severity should be downgraded or the finding dropped. If the claim survives the defense, it stands. Do not use the defense as an escape hatch to soften every finding.

---

## Output Format

The stress test appears in the editorial letter as §7 (after the rejection memo). Author-facing language throughout — no framework codes in the body.

```markdown
## Adversarial Reader Stress Test

*What would an uncharitable reader find wrong with this manuscript?*

### [Claim Title]

**The claim:** "[Low-charity reader phrasing]"

**Where:** [Specific scenes/chapters]

**How serious:** [Fatal / Damaging / Irritating] — would bother [Rare / Some / Many] readers

**Best defense:** [Steelman counter-argument]

**Does it land?** [Yes / Partially / No — with reasoning]

---

[Repeat for findings 2-5]

---

### Stress Test Summary

**Would this manuscript survive hostile scrutiny?**

- Yes: Core strengths absorb the hits
- Partially: Some claims land, but compensating strengths exist
- No: Claims would define reader response

**Which claims to address vs. accept as trade-offs:**
[Brief guidance — which findings are worth revising for, which are acceptable costs of the manuscript's choices]
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
