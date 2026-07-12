# AGD Move Audit — assuring / guarding / discounting, functionally (companion module v1.0)

A companion audit for argument-shaped nonfiction. It inventories the text's **performative argument moves** — ASSURING, GUARDING, DISCOUNTING — identifies them by **function, not cue words**, challenges each with its family's protocol, and records candidate diagnoses **only where a challenge fails**. It writes exclusively into `Argument_State.md` **§10.9 — AGD Move Audit** (the annotation protocol: companions never modify §§1–9).

**The three moves are legitimate and ubiquitous.** Sinnott-Armstrong & Fogelin (9e, ch. 3): arguers *assure* (supply authority/certainty in place of support), *guard* (weaken a claim to shrink its commitment), and *discount* (anticipate an objection and set it aside). None is a defect. The defect — when there is one — is a move doing **load-bearing work it cannot survive being challenged on**: the assurance that papers over absent support (ch. 5), the guard that turns out to be vacuous when pressed (ch. 16's self-sealer), the concession that changes nothing. The audit therefore never codes a move for *being* a move; it challenges the move's function and lets the result speak.

**Why functional, not lexical:** cue lexicons under-determine function — most hedge-cue lemmas also occur as non-cues (Velldal et al. 2012, BioScope; domain-specific but directionally decisive) — and the fleet's own experience concedes a regex cannot run an in-context substitution test. The identification criterion is the **transition**, not the phrase (analogically scaffolded on Inference Anchoring Theory, Budzynska et al. 2016 — a *dialogue* result; the monological transfer is this audit's own claim, validated by its fixtures).

**Run on:** full draft, after a Dialectical Clarity run has produced `Argument_State.md` (the audit reads §1 audience, the §2 claim ladder, and §6's objection inventory; if no `Argument_State.md` exists, run Dialectical Clarity first).

---

## Layer 1 — MOVE inventory (neutral; never a code)

Identify moves **functionally at a locus**. **Identification requires an independently identifiable transition/span** — a segment whose removal or transformation leaves the surrounding argument intact enough to compare. That requirement is what makes the Layer-2 challenge well-defined, and it is the firewall against vibes-identification. Cues are evidence, never criteria: identify cue-free moves wherever a transition is identifiable without a cue word; never inventory a cue word that is not performing the function.

| Family | The move | Canonical cues (NON-criterial) |
|---|---|---|
| **ASSURING** | authority/certainty supplied in place of support — there must be a **strippable span** (a cited-authority phrase, a credential appositive, a stated-as-known basis). No strippable span → not an ASSURING move | "studies show," "clearly," "everyone knows," "no one disputes" |
| **GUARDING** | a claim weakened to shrink its commitment | "some," "may," "tends to," "suggests," "arguably" |
| **DISCOUNTING** | an objection anticipated and set aside — including **structural** dismissal: an objection surfaced in a subordinate or narrative clause and proceeded past, with no concessive marker | "although," "admittedly … but," "to be sure," "of course … yet" |

## Layer 2 — CHALLENGE (per-family protocols; total result matrix)

Challenge every inventoried move with its family's protocol, or record it `NOT-CHALLENGED` (inventory-only). Results are **total and family-specific**:

| Family | Challenge | Legal results |
|---|---|---|
| ASSURING | **STRIP** (ch. 5): delete the assurance span; does independent support for the claim remain? | `SURVIVES` / `COLLAPSES` / `INDETERMINATE` |
| GUARDING | **COMMITMENT** (ch. 16): force the claim to a specific falsifiable commitment; does anything remain? | `SURVIVES` / `COLLAPSES` / `SELF-SEALS` / `INDETERMINATE` |
| DISCOUNTING | **ENGAGEMENT**, two prongs: (i) is the discounted objection the strongest text-internal one, or a decoy? — **reuse Step 6a Test A/B and the §6 record's `Basis`; cross-reference, never re-derive** — and (ii) does the concession change anything downstream? | `SURVIVES` / `COLLAPSES-DECOY` / `COLLAPSES-COSTLESS` / `INDETERMINATE` |
| any | (not run) | `NOT-CHALLENGED` |

- `SELF-SEALS` is **GUARDING-only**: the ch. 16 tell — vacuous when pressed, significant when unchallenged.
- `INDETERMINATE` means the challenge **was run** and adjudication is genuinely unresolved; document the disagreement in the assessment basis. Never use `NOT-CHALLENGED` for a run challenge.
- `COLLAPSES-COSTLESS`: the concession changes nothing downstream. Engagement *quality* grading stays Step 6's (`Engaged` × `Quality`) — the record cross-refs the §6 objection; it does not re-grade.
- GUARDING records also carry **`Trajectory: STABLE / DISAPPEARING (early locus → late locus)`** — a guard can survive its commitment test and still silently vanish by the conclusion; the trajectory is its own observation (S&F's "disappearing guard").

**Construction constraints (Firewall):**
- **STRIP is purely subtractive** — delete the span, change nothing else.
- **COMMITMENT is de-hedge-only** — the forced commitment is the DE-HEDGED form of the text's own claim: strip the guard/qualifier and add **no** new specificity, threshold, mechanism, or quantity the text lacks.
- **ENGAGEMENT constructs no text** — it references §6 records (see the cross-ref contract below).

## Layer 3 — CANDIDATE diagnoses (flag-only; licensed by failed function)

`Candidates: NONE` is REQUIRED when `Result ∈ {SURVIVES, NOT-CHALLENGED, INDETERMINATE}` — an intact or unresolved function licenses nothing. **One whitelist exception:** a GUARDING record with `Trajectory: DISAPPEARING` may carry candidates from exactly **{FM-A16, WR3, BP4}** at any result — the trajectory is itself the failed function.

| Move × result | Candidate codes (existing codes only; adjudicated via the reconciliation contract) |
|---|---|
| ASSURING × COLLAPSES | WR1, DI0, FM-A19, SM4, FM-A11 |
| GUARDING × COLLAPSES | DI3, WR3 |
| GUARDING × SELF-SEALS | DI3, BP0 (ch. 16 vacuity routes via Step 9, not as a candidate) |
| GUARDING × Trajectory DISAPPEARING (any result) | FM-A16, WR3, BP4 — the exception whitelist |
| DISCOUNTING × COLLAPSES-DECOY | OB5, OB1 |
| DISCOUNTING × COLLAPSES-COSTLESS | OB4 — requires a resolving `Discounted:` cross-ref |
| any × INDETERMINATE | NONE |

Candidates are **flags for adjudication, never verdicts**, drawn from the existing 62-code namespace (the Dialectical Clarity codes minus the AT1–AT4 type labels, plus FM-A1–20). This audit adds **no new codes** and its records **never enter severity propagation directly** — a candidate becomes a real code only through reconciliation.

**Reconciliation contract:** every candidate is born `PENDING`. It becomes `CONFIRMED (— adjudicator, target ref)` or `DECLINED (— basis)` only via a re-entry pass that is not this companion: **in the current increment the reconciliation writer is the human editor** (or the engine on a full re-run that regenerates §§1–9); automated engine-refresh adjudication is future scope. Updating a candidate's status line in §10.9 is an annotation-layer state change by the adjudicating writer — an explicit, documented carve-out to per-module subsection ownership (it touches §10.9 status fields only, never §§1–9).

---

## The §10.9 record format (machine-validated — `validate.sh argument-agd`)

```markdown
### 10.9 AGD Move Audit

Span: C0 — [locus]
Span: C1.warrant — [locus]
Excluded: [span] — [one-clause reason]        (only when Completion: PARTIAL)
Move count: [N]
Completion: [COMPLETE | PARTIAL]

M1: [ASSURING | GUARDING | DISCOUNTING] at [locus]
  Source anchor: ["<verbatim quote>" @ locus]
  Cue: [surface cue | NONE]
  Challenge: [STRIP | COMMITMENT | ENGAGEMENT]
  Result: [per the family's legal set]
  Constructed challenge: [the stripped sentence / de-hedged commitment — engine-CONSTRUCTED; omit for ENGAGEMENT and NOT-CHALLENGED]
  Assessment basis: [why this result, ≤2 clauses]
  Trajectory: [GUARDING only — STABLE | DISAPPEARING (early locus → late locus)]
  Discounted: [DISCOUNTING only — → Objection N | NOT-INVENTORIED]
  Displaced strongest: [DISCOUNTING × COLLAPSES-DECOY only — → the §6 STRONGEST OBJECTION]
  Candidates: [NONE | CODE (PENDING); CODE (CONFIRMED — <adjudicator>, <target ref>); CODE (DECLINED — <basis>)]

M2: ...
```

- **Coverage manifest** heads the section: one `Span:` line per included span (`C0` + each `Cn`'s warrant/support locus, matching the §2 claim ladder), `Excluded:` lines with reasons, `Move count:`, `Completion:`. `PARTIAL` = ≥1 ladder span deliberately excluded (each with a reason); an audit whose records fall outside its declared spans is invalid.
- **`Source anchor` must resolve** in the source text (normalized substring: whitespace runs folded, quote characters/dashes normalized, otherwise case-sensitive). The **constructed challenge is NOT expected in the source** — it is a construction.
- **Cross-ref contract (DISCOUNTING):** `COLLAPSES-DECOY` requires `Displaced strongest:` resolving to §6's recorded STRONGEST OBJECTION (6a records it even when the piece never raises it). `COLLAPSES-COSTLESS` requires `Discounted:` to resolve to an inventoried §6 objection — if not yet inventoried, Step 6's sweep adds it (the append-after-core rule), because the grading delegation must have a target. `NOT-INVENTORIED` is legal only on `SURVIVES`/`INDETERMINATE` records.

---

## Firewall (mirrors the Argument Red Team posture for constructed adversarial content)

**Allowed:** identifying moves at loci with verbatim anchors; constructing the subtractive STRIP and de-hedge-only COMMITMENT forms of the text's own sentences; referencing §6 objection records; recording challenge results with assessment bases; flagging candidate codes `PENDING` for adjudication; documenting genuine indeterminacy.

**Not allowed:** coding a move for being a move; inventing an assurance, guard, or objection the text lacks; adding specificity, thresholds, mechanisms, or quantities the text lacks to any constructed challenge; asserting a constructed challenge as a standard the argument must meet (it is engine-surfaced, author-adjudicated diagnosis); re-grading §6 engagement quality; writing anything outside §10.9; promoting a candidate to a code (that is the reconciliation writer's act, never this audit's); treating `NONE`-candidate records as praise or `INDETERMINATE` as a defect.

**Output:** the §10.9 block (coverage manifest + typed M-records), signed `argument-agd-audit` with timestamp per the annotation protocol.
