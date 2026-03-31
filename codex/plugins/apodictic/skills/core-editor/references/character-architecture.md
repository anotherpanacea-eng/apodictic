# Character Architecture — Pass Reference

*Compact reference for Pass 5 (Character Audit) execution. For the full deep-dive audit with genre tuning packs, named flags, and severity levels, see the specialized-audits skill: `references/craft/character-architecture.md`.*

---

## Purpose

Build Psychology Engine for each major character. Identify Arc Type. Calculate Agency. Apply Genre Tuning.

---

## Arc Types

| Arc Type | Movement | Logic Gate |
|----------|----------|------------|
| **Positive Change** | Lie → Truth | "Lie Collapse" — do they choose vulnerability over defense? |
| **Negative Change** | Truth → Lie | "Moral Event Horizon" — do they cross a stated line? |
| **Flat** | Tested → Reaffirmed | "Doubt Moment" — are they genuinely tempted to change? |
| **Disillusionment** | Innocence → Knowledge | "Irreversible Knowledge" — does truth cost comfort? |
| **Testing** | Belief Tested → Confirmed/Broken | "Genuine Trial" — is outcome uncertain until crisis? |

**Arc Selection Shortcut:**
- "I'm better now" → Positive | "I'm worse now (my choice)" → Negative
- "I was right, but it hurt" → Flat | "I can't go back" → Disillusionment | "I survived, barely" → Testing

---

## Psychology Engine (per character)

```
WOUND: [Formative trauma] → Does it cause a mistake?
LIE: [False belief] → Do they articulate it?
WANT: [Conscious goal] → Do they pursue it?
NEED: [Unconscious requirement] → Does Want obstruct Need?
FEAR: [What they avoid] → Does antagonist force them to face it?
TELL (Optional): [Self-justifying story about harm] → Is it contradicted by consequences?
```

**Want-Need Logic Gate:**
- Want and Need in tension → PASS
- Can easily have both → FLAG: "Low Internal Conflict"

---

## Trauma Physics

**Trauma Loop:** TRIGGER → APPRAISAL → SOMATIC RESPONSE → BEHAVIOR → COST → REINFORCEMENT

**Manifestation Gate:**
- IF wound exists AND behavioral cost = 0 → STRUCTURAL BREAK: "Trauma Window Dressing"

---

## Agency Quotient (AQ)

```
AQ = Active Decisions / Total Scenes

Thresholds:
- Protagonist: AQ > 0.40
- Antagonist: AQ > 0.30
- Love Interest: AQ > 0.25
```

**Puppet Detection:** Character acts against psychology because plot needs it
- 2+ puppet moments → FLAG: "Plot-Serving Behavior"

---

## Constraint Quotient (CQ) — Agency Under Coercion

```
CQ = Constrained Choices / Total Scenes
```

**For erotic horror, dark romance, captivity narratives.** A coerced protagonist can be dramatically active if choosing within a trap.

**Stance Check (Anti-Exploitation Gate):**
For scenes with high CQ:
1. Does text register the constraint?
2. Is there aftereffect (shame, rage, dissociation)?
3. Does narrative avoid framing arousal as exculpation?

IF "No" to 2+ → FLAG: "Ethics Leak"

---

## Voice Distinctiveness

**Blind Swap Test:** Take 10 dialogue lines from A, 10 from B. Can you tell who's speaking?
- Attribution >70% correct → PASS
- Attribution <50% → FLAG: "Generic Voice"

**Interiority Markers:** Sentence length, filter words, attention focus, taboo topics, metaphor family, sensory bias under stress

---

## Diagnostic Flags

- **"Sexy Lamp":** Character has no want independent of protagonist
- **"Informed Attribute":** Told smart/dangerous, never shown
- **"Personality Transplant":** Opposite behaviors without cause
- **"Trauma Window Dressing":** Wound stated, never causes mistake
- **"Retroactive Motivation":** Reason invented after action
- **"Maid and Butler":** Characters exist only for exposition
- **"Therapeutic Alibi"** *(genre-specific):* Harm laundered through care-language without contradiction
- **"Authorial Collusion"** *(genre-specific):* Prose grants manipulator unchallenged rhetorical dominance

---

## Ensemble Balance

- POV character <15% → FLAG: "Underweight POV"
- >20% Act I presence, <5% Act III → FLAG: "Dropped Thread"
- >20% word count but arc incomplete → FLAG: "Unresolved Major Character"

---

## Genre Tuning Packs

Adjust thresholds and add specialized tracking by genre:
- **Sci-Fi/Action:** AQ > 0.50; add SQ (Solution Quotient); Competence Display Gate
- **Mystery:** AQ > 0.45; add IQ (Inference Quotient); Inference Chain Map
- **Rom-Com:** Both leads AQ > 0.35; add VQ (Vulnerability Quotient); Bid/Repair Rhythm
- **Epic Fantasy:** AQ > 0.45; add MQ (Moral Quotient); Power Cost Ledger
- **Horror:** AQ 0.25-0.35 acceptable if CQ rising; Fear Manifestation Gate; Survival Logic Gate

See full module for detailed tuning packs.
