# Contract and Controlling Idea: The Salt Year (literary fiction)

<!--
Canonical CLEAN Contract worked example (core-editor workflow; schema in
core-editor/references/contract-template.md). This is the release-gate target for the
`quality-risk-triggers` validator (run-core.md §Quality-Risk Mode Selection): five pre-pass
triggers (Q1-Q5) raise an escalation ceiling (none < hybrid < swarm) before a diagnostic run.
A well-formed, low-risk manuscript contract must raise NONE of them and exit 0
("No quality-risk triggers fired. Token-fit recommendation applies.").

Exercised by `validate.sh --check-all` as the canonical target for that validator:
  * clean arm  — the validator over this file exits 0 (no trigger raised);
  * hostile arm — a throwaway copy with the darkness rating flipped from Moderate to the top
                  setting raises the Q1 consent/governance trigger and exits 1, proving the
                  gate has teeth.

Why each trigger stays silent (see run-core.md for the authoritative rules; this note is itself
part of the scanned artifact, so it deliberately paraphrases rather than quoting any trigger
literal that would trip the validator against its own documentation):
  Q1 consent/governance — literary fiction (not a horror/erotic genre line); the darkness rating
     is Moderate, below the top setting that trips it; the sisters' authority imbalance is a
     texture, not the book's engine; and the contract names none of the consent/reception audit
     escalators.
  Q2 argument-shaped nonfiction — this is fiction with no nonfiction/argument constraint and no
     argument-clarity audit lens, so the claim/evidence/audience escalator does not apply.
  Q3 many POVs / broken chronology — a single close-third narrator and a strictly chronological
     structure (no fragmentation, nesting, braiding, or out-of-order time).
  Q4 prior under-diagnosed round — a first diagnostic round: no prior-run sidecar flag and no
     note that an earlier pass came back too shallow.
  Q5 pre-send stakes — the goal is a mid-draft developmental pass, not a pre-send readiness gate:
     no submit goal, no eleventh-pass readiness stage.
-->

## Contract Schema

```
GENRE/SUBGENRE: Literary fiction / family drama
READER PROMISE: A quiet, close story about a daughter emptying her late mother's house across one summer, and the year of grief that reshapes what she thought she owed
CONTROLLING IDEA: Grief clarifies love + because loss forces us to weigh what we actually did against what we always meant to do
HEAT LEVEL: Low
DARKNESS LEVEL: Moderate
PRIMARY TENSION TYPE: relational
ENDING TYPE: closed
TONE COMPS: Marilynne Robinson's Gilead; Jenny Offill's Dept. of Speculation
STRUCTURE COMPS: a single chronological summer, chapter-per-week
NON-NEGOTIABLES: the mother never appears in flashback; the grief is carried in present-tense scene, not exposition
POV: single close third (Della, the younger daughter)
POV count: 1
STRUCTURE: linear / strictly chronological across one summer, one week per chapter
GOAL: structural revision (mid-draft developmental pass; opening act and midpoint)
RECOMMENDED AUDITS: Scene Turn, Emotional Craft, Interiority Calibration
```

## Contract Statement

*The Salt Year* is a literary family drama that promises a quiet, interior reckoning: over one
coastal summer, Della sorts and empties the house her mother has left behind, and the ordinary
labor of it — deciding what to keep, what to give away, what to admit she never understood —
becomes the vehicle for a year of grief. The relational tension is between Della and her older
sister Ruth, who disagree about the estate without ever quite disagreeing about the mother. The
book keeps a low heat and a moderate darkness: the losses are real but domestic, and the ending
closes rather than dissolves.

---

## Controlling Idea

*This section elaborates the `CONTROLLING IDEA:` schema field above — the one-line field is the
canonical, validator-readable form; this section restates and develops it.*

**Format:** [Value] + [Cause]

**Statement:** Grief clarifies love — because loss forces us to weigh what we actually did for
someone against what we always told ourselves we meant to do.

---

## Anti-Idea

**What this book is explicitly NOT arguing:**

- Not that grief is redemptive or that mourning "teaches a lesson."
- Not that the sisters' reconciliation resolves the loss; the loss is not a problem to be solved.
- Not that memory is reliable — but the book stays inside one honest narrator rather than staging
  competing accounts.

---

## Selected Modules

**Genre calibration:**
- [x] Literary Fiction
- [ ] Thriller / Suspense
- [ ] Other: ___________

**Specialized audits:**
- [x] Female Interiority
- [ ] Banister (Epistemic Humility)

*(No governance-tier audit signals are selected — this is a low-risk domestic drama, so the
consent/reception escalator lane stays empty by design.)*

---

## Key Intake Answers

### Protagonist and Engine
- **Protagonist:** Della, mid-thirties, the daughter who stayed local.
- **Surface want:** to finish clearing the house before the season ends and the sale closes.
- **Underlying want:** to be told, retroactively, that she was a good enough daughter.
- **Central obstacle:** every object in the house is a claim on her attention and her guilt.
- **Cost of success:** letting the house — and the version of herself who lived there — go.
- **Cost of failure:** carrying the unfinished accounting into the rest of her life.
- **The lie:** that she was too busy, rather than too afraid, to visit more often.

### Relationship Dynamics (if applicable)
- **Why these people collide:** Della stayed and Ruth left; each read the other's choice as a verdict.
- **Steps of trust/rupture/repair:** a shared task, a discovered letter, a fight over a keepsake, a
  quiet repair that stops short of full understanding.
- **Emotional price of connection:** admitting that neither of them knew the mother as well as they
  performed to each other.

### Structure
- **First irreversible change:** Della accepts the key and agrees to clear the house alone.
- **Midpoint shift:** a box of the mother's unsent letters reframes what Della thought she owed.
- **Real climax:** the sisters decide, together, what single thing to keep.

### Reader Experience Intent
- **Intentionally ambiguous:** whether the mother knew she was dying.
- **Should be crystal clear:** the sisters love each other even while they wound each other.
- **Reader should suspect early:** the unsent letters exist.
- **Reader should realize when:** at the midpoint, what the letters actually say.
- **Intended misinterpretation:** that Ruth is the cold one.

---

## Non-Negotiables (Detailed)

- **No flashback.** The mother is present only through objects, letters, and the sisters' talk.
  The grief must be carried in present-tense scene; the moment we cut away to a living-mother
  scene, the book becomes a different, softer book.
- **One narrator.** The whole novel stays in Della's close third. Ruth is never given a chapter;
  the reader only ever infers her from the outside — that limitation is the point.
- **A closed ending.** The house is sold and the one kept object is named. No epilogue, no
  time-jump, no dissolve into ambiguity about whether the sisters "made it."

---

*Framework: APODICTIC Development Editor (APDE)*
*Draft stage: structural revision (mid-draft)*
*Diagnostic posture: first round — no prior-run sidecar; baseline token-fit mode applies.*
