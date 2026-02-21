# Inline Genre Calibrations

These are the detailed pass-modification instructions for each genre, as used during core DE runs. They supplement the standalone genre module files with specific pass-level adjustments.

---

## Romance / Erotic

**Core contract:** Readers buy Emotional & Physical Consummation. Primary failure mode is not "too explicit" but **"Unearned Intimacy"** or **"Static Heat."**

**Subgenre calibration:** False positives vary by subgenre:
- **Historical:** Don't flag "passive" heroines (agency looks different in 1815)
- **Dark Romance:** Don't flag "toxic" behavior (this is the feature)
- **High Erotica:** Don't flag "unrealistic" stamina or logistics
- **Poly/WhyChoose:** Don't flag lack of "The One"
- **Slow Burn:** Don't flag extended anticipation

**The Consent Calculus (Pass 10):**
For each intimate scene, log: Stated Desire → Enacted Boundary → Aftermath State
```
IF Enacted > Stated AND Aftermath = Positive → CNC/Awakening (valid)
IF Enacted > Stated AND Aftermath = Negative → Violation (flag)
```
Check result against Contract. Dark Romance expects different outcomes than Sweet Romance.

**The Sync Check (Pass 4):**
Track Emotional Valence (love↔hate) and Physical Intimacy (distant↔consummated) separately.
- Physical ↑ but Emotional ↓ → Flag unless angry sex/manipulation is intent
- 3+ chapters with no movement on either axis → "Static Relationship"

**Escalation Stages:**
Glimpse → Graze → Collision → Retreat → Surrender
- Skip the Retreat (vulnerability hangover) → Flag as "Rushed Intimacy"
- Skip the Glimpse → Flag as "Chemistry not seeded"

**Named Diagnostic Flags:**
- **"Magic Wand" Orgasm:** Sex resolves emotional conflict without conversation → unearned
- **"Idiot Ball":** Conflict solvable by one text message → fragile
- **"Body Betrayal" Overuse:** "I hate him / I want him" >5 times → diminishes agency
- **"Decorative Kink":** Kink reveals nothing about psychology → unintegrated

**Escalation vs. Repetition Audit (for multiple intimate scenes):**
- Catalog scene mechanics: physical activity, psychological dynamic, technique used
- Build escalation map: new element introduced? Character growth?
- Detect: same mechanic/same outcome, denial cycle redundancy (>3 cycles), missing escalation
- Escalation ≠ higher intensity; can mean deeper vulnerability, role reversal, new context

**False positive warning:** Slow burn is not a pacing problem. Repetition can serve ritual/anchoring if intentional.

---

## Horror (Psychological)

**Reader expects:** Escalating dread, reality destabilization, cost (psychological, physical, or moral), either catharsis or deliberate denial of catharsis.

**Additional intake:**
- Source of horror: external threat / internal dissolution / epistemological uncertainty?
- Should horror resolve, remain ambiguous, or escalate to end?
- Relationship between dread and catharsis?

**Pass modifications:**
- Track certainty axis carefully (epistemic horror)
- Track normalization (have strange elements lost power?)
- Track reality anchoring (where does reader lose footing?)

**False positive warning:** Ambiguity is often the point, not a flaw.

---

## Science Fiction / Fantasy

**Core contract:** "A world that works differently, but works." Primary failure mode is not "unrealistic" but **inconsistent**.

**Subgenre calibration:**
- **Hard SF:** Don't flag "dry" technical dialogue
- **Space Opera:** Don't flag "unrealistic" physics
- **Epic Fantasy:** Don't flag slow Act I (world establishment expected)
- **New Weird:** Don't flag unexplained phenomena
- **Grimdark:** Don't flag unlikable protagonists or pyrrhic victories
- **Progression/LitRPG:** Don't flag "video game" logic

**Contract additions:**
```
NOVUM: [The central speculative element]
MAGIC/TECH HARDNESS: [Hard / Soft / Hybrid]
COST OF POWER: [What is paid?]
EXPOSITION TOLERANCE: [High / Medium / Low]
```

**Sanderson's Laws:** Hard magic (rules known) → can solve problems. Soft magic (mysterious) → creates problems, shouldn't solve them.

**The Rule Ledger (Priority Pass 10):**
Track every magic/tech usage: Scene | Action | Established Cost | Payment Shown

**Integration Tests:**
1. "Replace with Cellphone" Test
2. "Salt vs. Meal" Test
3. Social Impact Test

**Key flags:** Wikipedia Dialogues, Sanderson Violation, Floating Head, Power Creep, Retro-Causality.

---

## Literary Fiction

**Reader expects:** Psychological depth, thematic resonance, voice that rewards attention, ambiguity, recognition of human truth.

**Recalibrations:**
- Pass 1: "Slow" pacing may be essential; track recognition moments
- Pass 2: Plot structure optional; track thematic organization
- Pass 3: Metrics have LOW authority
- Pass 5: Characters may not have clear goals; assess specificity
- Pass 9: PRIORITY PASS

**Three key audits:** Thematic Embodiment Audit, Interiority Function Audit, "Nothing Happens" Assessment (seven valid functions for plotless scenes).

**Stillness vs. Stasis:** Still = deliberate pause, pressure held. Stasis = nothing accumulates, scene removable.

---

## Genre-Bending and Literary Mode

When Literary Fiction is Primary with other genre modules active, activate Literary Mode.

### Module Hierarchy
- **Primary:** Which genre governs the contract?
- **Secondary:** Which genres provide tools/texture?
- **Interrogated:** Which genres are being examined as material?

### Literary Mode Effects
Genre conventions → available tools, not requirements. Genre "failures" → ask "Is this serving theme?" before flagging. Literary norms govern.

### Genre Convention Treatment
For any genre element: Satisfied / Used / Subverted / Examined / Refused. All valid if intentional.

### Register Uncertainty (Multi-Genre Diagnostic)

**Four Registers example (Literary Erotic Horror Romance):**

| Register | Reader Should Feel | Interiority Focuses On |
|----------|-------------------|------------------------|
| Erotica | Aroused | Sensation, desire |
| Romance | Invested in the couple | Connection, vulnerability |
| Horror | Disturbed, unsettled | Wrongness, loss of control |
| Literary | Insight, recognition | Meaning, consciousness |

**Primary Register Question:** Which register is primary, and are others serving or fighting it?

Best scenes achieve all registers simultaneously.
