# Expected — AI-Prose Calibration unexercised-family fixtures

Pre-registered **before any audit run** (the argument-benchmark ground-truth discipline;
`evals/argument-groundtruth-template.md`). A run is scored against this key; an `expected.md`
written after seeing run output is void.

Reference: `plugins/apodictic/skills/specialized-audits/references/craft/ai-prose-calibration.md`
§Step 2 (Layer B flag scan). Severity bands are Spot / Pattern / Systemic.

---

## `ai-heavy-prose.md` — the four target families MUST fire

### AIC-2 — Velvet Fog — expected **Systemic**

The passage never grounds the reader in a physical world; description is generic and sensory
detail is absent or indefinite. A run **hits** if it fires AIC-2 and quotes at least two of:

- `The apartment was cozy.` (generic space — a "cozy apartment" is the audit's own textbook example of the flag)
- `Outside, the city was bustling.` (generic street — the second textbook example, repeated verbatim later)
- `a kind of quiet ache` / `a kind of something she didn't have words for` / `a kind of something` — **Indefinite-Pronoun Gesture** subtype ("a kind of Y" without specifying Y; "something" + abstract qualifier). The prose outsources specificity to the reader.
- `a wave of sadness moved through her` / `let it wash over her like a wave` (center-of-semantic-field emotion words; the audit's own "she felt a wave of sadness" example).

**Miss** if AIC-2 does not fire, or if it fires without naming the Indefinite-Pronoun Gesture
subtype (the gesture recurs at least three times and is the load-bearing signal).

### AIC-4 — Register Seams — expected **Pattern or higher** (readiness hard gate)

There is a bald seam between Section One (plain, warm, concrete-diction narration) and
Section Two (elevated academic register: "phenomenology of grief," "ontological rupture,"
"mourning-as-hermeneutics," "sedimented residua"). The shift corresponds to no POV change,
emotional shift, or deliberate register choice — it is **bad drift** (serves nothing, breaks
reader trust), not authorial-controlled variation.

A run **hits** if it fires AIC-4 and identifies the Section One → Section Two boundary as the
seam, contrasting the two prose levels. Per the audit's Readiness Impact Note, **AIC-4 at
Pattern or higher is a Hard Gate** (Must-Fix floor); a compliant run flags it as
readiness-gating. **Miss** if the run treats the register shift as an intentional/earned
stylistic choice (the false-positive guardrail does NOT apply — nothing in the text frames
the shift as characterization).

### AIC-6 — Continuity Smear — expected **Systemic**

World-model failures cluster around entity states and temporal sequence. A run **hits** if it
fires AIC-6 and cites at least three distinct breaks:

- **Object teleport / re-grab:** the tea cup is `set … down on the table`, then `lifted … and took a sip, though she had set it down two paragraphs ago and had not picked it up again`; later `The teacup was full, and it was empty, and it had never been there at all.`
- **Spatial contradiction:** Daniel `sat down across from her`, then `leaned back against the wall on the far side of the room, even though he had just sat down across the table from her`; later he `had gone, and also he was still sitting there` and `crosses the room toward her` after leaving.
- **Unrevealed information:** Daniel knows `Your mother left the house to you` although `the reading was still three days away, and no one had opened the envelope yet` — and `she didn't ask how` (a character reacting to information not yet in the world).
- **Temporal smear:** `The morning sun poured through the window, and it was evening.`

**Miss** if AIC-6 does not fire, or if it is downgraded to Spot (the density and clustering
make this Systemic, not an ordinary isolated continuity error).

### AIC-8 — Unearned Fluency — expected **Systemic** (the umbrella verdict)

Unearned Fluency is the meta-category: grammatically competent, logically transitioning prose
in which any sentence can be swapped for a paraphrase with nothing lost. A run **hits** if its
top-line diagnosis / Top-3 Systemic Risks names the manuscript's uniform, consequence-free
competence — e.g. the reader never meets a sentence that could only appear in this passage —
and cites the co-occurrence of AIC-2 + AIC-6 (the audit's Pattern-Synthesis rule: velvet fog
+ continuity smear together indicate generation without a persistent world model). Explicit
tells the run may cite: `some things could not be understood`, `It was a complicated feeling,
one that resisted easy categorization` (metacommentary on difficulty — an Assistant-Frame
adjacent move here serving the unearned-fluency verdict).

**Miss** if the run reports the four flags in isolation without the meta-level Unearned
Fluency verdict, or if it praises the prose's fluency instead of hunting for the absence of
friction (the audit's Deficit-First Diagnostic Rule).

## Adjacent families (not the target; do not penalize either way)

AIC-1 (Generic Hand), AIC-3 (Echo Stack), AIC-5 (Puppet Dialogue), and AIC-7 (Discourse Leak)
may also register on this sample — the dialogue is somewhat puppet-uniform and metacommentary
flirts with Discourse Leak. Those families are already exercised by the F1–F4 canonical
fixtures; scoring for THIS fixture is on AIC-2 / AIC-4 / AIC-6 / AIC-8 only. Firing the
adjacent families is neither a hit nor a miss for coverage of the unexercised set.

## `clean-control.md` — the four target families MUST stay clean

The control is grounded (chipped enamel mug, the number 26 bus, buttoned coat, cold tea),
continuity-consistent (the mug is set on the windowsill and later picked up from the
windowsill; Daniel stays in the doorway throughout; no one knows the will's contents), single
consistent register throughout, and voiced (the mug's hairline crack, "two raps, a pause, one
more"). A run **passes the false-positive control** if it fires **none** of AIC-2 / AIC-4 /
AIC-6 / AIC-8 at Pattern or higher. A Systemic or Pattern hit on any of the four here is an
**over-fire** and fails the control.

Note: the control deliberately includes an *earned* dry-narration move — `He was not going to
be in the area. He lived forty minutes north and hated the drive.` — which is a **Negation /
correctio pattern that IS the cognitive act** (the narrator committing to the truth behind
Daniel's excuse), i.e. earned, not AIC-7 Discourse Leak. A run that flags this as leak is
over-firing on the guardrail.
