# Proposal — Engine fix: objection structural-priority / decoy resistance (Step 6)

**Status:** RATIFIED + APPLIED in `4d350ec` (6a two-test + FM-A20 + OB5 in `dialectical-clarity.md`; verified by the post-fix blind re-run, `evals/results/run-20260604-174301`). Retained as the design record. *(Original status: DRAFT for ratification.)*
**Target file:** `plugins/apodictic/skills/specialized-audits/references/craft/dialectical-clarity.md` (Step 6), + its codex/antigravity mirrors.
**Driver:** the two structural objection-misses in the benchmark — **ppi** (took
the public-safety decoy) and **roosevelt** (missed the veto-point-regress
objection) — are **engine-general**, not a model quirk: Opus, Sonnet, **and blind
GPT-4** all fail them (cross-vendor scorecard, `../../results/cross-vendor-gpt-20260604/`).

---

## Diagnosis — the machinery exists but is too soft to flip behavior

Step 6 already has the **6a** round (PR #22): "prefer **text-internal** objections
over **canonical imported**," and **OB5** = "decoy strongest objection." Yet all
three vendors still took the decoy — and GPT/Opus even labeled it **OB3** ("central
objection unaddressed"), never self-catching it as a decoy. Two reasons:

1. **6a is a *preference*, not a *procedure*.** "Prefer text-internal" gives the
   model no way to *find* the text-internal objection, so it defaults to the easy,
   available move — "what would a hostile reader say first?" — which surfaces the
   genre-generic counter.
2. **No named pattern for the structure these objections share.** The FM-A
   taxonomy has nothing for *"the remedy recreates the diagnosed problem / the cure
   for the decried harm is the very thing the argument opposes."* That is exactly
   both misses:
   - **ppi:** the report decries officer-discretion arbitrariness; **standardization
     is the cure** for that arbitrariness → text-internal objection. Models grab the
     genre-generic *"but public safety."*
   - **roosevelt:** the piece critiques procedural veto points; its **safeguards
     recreate** them → text-internal objection. Models grab the genre-generic
     *"but unions cost/delay."*

---

## The fix (localized to Step 6 + one new pattern; severity logic untouched)

### Part 1 — Turn 6a into a two-test procedure

**Test A — Genre-genericity (decoy) filter.** Before naming any objection "the
strongest," ask: *would this same objection apply, almost verbatim, to most
arguments in this genre or on this topic?* Templates:
- "but public safety / but it protects the public" → **any** decarceration argument
- "but cost / inefficiency / delay" → **any** pro-regulation or pro-labor argument
- "but government failure" → **any** pro-intervention argument

If **yes** → it is a **canonical-imported** objection = a **decoy candidate**. A
hostile reader may raise it first, but it is not text-internal. **Downrank it**
(keep it in the inventory, never as the *strongest*) **unless no text-internal
objection exists.** Naming a genre-generic objection as strongest while a
text-internal one is available fires **OB5**.
*Guard against over-correction: downrank, don't delete. If the piece is novel
enough that the genre-generic objection genuinely is the crux and no text-internal
objection exists, it may be the strongest.*

**Test B — Self-undermining derivation (constructive — this is the missing move).**
To *find* the text-internal objection, run the argument's own machinery against
itself. Ask:
- Does the proposed **remedy recreate** the very problem the argument diagnoses?
- Is the standard **cure** for the harm the argument decries exactly the mechanism
  the argument **opposes**?
- Does the conclusion **depend on** the thing it condemns?

The strongest objection is usually the one the argument's own warrant / cure /
value generates against itself. Name it as `STRONGEST OBJECTION`.

**Sequence:** run **Test B first** (derive the text-internal candidate), then
**Test A** on whatever you're tempted to call strongest. Text-internal beats
genre-generic.

### Part 2 — New named pattern **FM-A20: Self-Undermining Remedy**

> Signature: OB3/OB5 + DI (often DI2). The argument's proposed remedy reintroduces,
> or structurally depends on, the very condition it diagnoses as the problem; or the
> standard cure for the harm it decries is exactly the mechanism it opposes. The
> strongest objection is text-internal: the argument defeats itself on its own
> terms. Distinct from FM-A10 (Uncompared Proposal — about *alternatives*) and
> FM-A13 (Motte-and-Bailey — about *claim oscillation*).

Gives the engine a recognizable template and a label Step 9 can cite.

### Part 3 — OB5 self-check (closes the "mislabeled OB3" gap)

Add to OB5's description: *"If your named strongest objection passes the
genre-genericity test (Test A) and you did not run the self-undermining derivation
(Test B), you are likely holding a decoy — fire OB5, not OB3."* This catches the
exact failure (GPT and Opus labeled the public-safety decoy OB3).

---

## Validation — would it flip the failing cases without breaking the working ones?

| Case | Under the fix | Result |
|---|---|---|
| **ppi** | Test A flags "public safety" as genre-generic (any decarceration arg) → decoy; Test B derives "standardization cures the discretion-arbitrariness it decries" → text-internal GT3 | **flips to GT3 hit** ✓ |
| **roosevelt** | Test A flags "cost/delay" as genre-generic; Test B derives "safeguards recreate the veto points it critiques" → text-internal GT3 | **flips to GT3 hit** ✓ |
| **SOUND cluster** (cato, reason, current-affairs, the famous pieces) | no severity codes added; only *which* objection is named strongest changes | **calibration preserved** ✓ |
| over-correction risk | "downrank, don't delete" + "genre-generic may be strongest if no text-internal exists" | guarded ✓ |

## What it deliberately does NOT touch
- **Step 9 severity / Hard Gates / Severity Floor** — the working PR #22
  calibration that held SOUND across the whole cluster with zero over-firing.
  Untouched. (The fix changes objection *selection*, not severity.)
- OB/DI code *definitions* — only OB5 gains a self-check note.

---

## Implementation plan (on ratification)
1. Edit Step 6 (6a two-test procedure + OB5 self-check note) and add **FM-A20** in
   the source `dialectical-clarity.md`.
2. Regenerate mirrors: `node scripts/build-codex.mjs && node scripts/build-antigravity.mjs`.
3. **Verify (blind):** re-run `ppi` + `roosevelt` via `run.sh` (4 model calls —
   needs the Mac on AC power) to confirm the flip; score in a separate context.
4. **Regression:** re-run one SOUND control (cato or reason) to confirm no new
   over-firing.

## Ratification questions
1. Approve the **two-test 6a** (genre-genericity filter + self-undermining derivation)?
2. Approve **FM-A20: Self-Undermining Remedy** as a new named pattern?
3. Approve the **OB5 self-check** note?
4. Do you want the **verification re-run** (ppi + roosevelt blind) after implementing — or implement now and verify on the next batch?

---

## Separate flag (not part of this engine change)
**current-affairs GT2** is suspect-as-recall: blind GPT corroborated GT3
(separability) but **missed GT2** (target-mismatch), mislocating it to the warrant
layer. Recommend a one-line note in the scorecard and a second cross-vendor/human
check before treating current-affairs GT2 as established. This is an *investigate*,
not an engine or key change.
