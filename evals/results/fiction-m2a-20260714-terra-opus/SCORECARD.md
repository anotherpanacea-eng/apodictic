# Fiction M2a Scorecard — Terra + Opus

**Scored:** 2026-07-14
**Scorer role:** fresh post-run rubric-trained scorer agent; it did not participate in blind inference, and keys / outputs were left unchanged
**Terra run:** `evals/results/fiction-run-20260714-144857`
**Opus run:** `evals/results/fiction-run-20260714-145217`

The raw responses are preserved byte-for-byte in this package under
`outputs/{terra,opus}/<fixture>/output.md`; the run paths above identify their
historical source trees.

## Headline decision

**Lane-1 suite result: FAIL — 3 of 4 matched pairs converge.** The S (orphan
scene), P (POV), and R (unpaid setup) pairs converge. The C (continuity) pair
does not: both models recover both planted contradictions in the broken member,
but Opus also asserts a new timeline/age contradiction on the reconciled clean
member. Under Step 4, a pair fails when either member fails its side, and clean
specificity requires neither run to fire the defect mechanism.

All three standalone intentional-device controls converge on their **Lane-1/A
trap gates**. Neither model pathologizes the registered Yellow Wallpaper voice
deterioration, Gift of the Magi twin reveal, or Christmas Carol five-stave /
compressed-redemption devices at Must/Should-Fix.

Lane-2/B reporting is positive but **not a gate**: both runs recover Scrooge's
five-stave movement inventory and denial → staged confrontation → redemption
arc. Those bands remain `provisional_author` until a ≥3-editor panel licenses
them. No Lane-3 claim is made.

| Unit | Lane-1 result | Reason |
|---|---:|---|
| S — orphan-scene pair | CONVERGES | Both hit locus/mechanism/severity; clean is specific. Repair agreement is the one missing anchor (Terra gives no actionable first repair), leaving the required 3/4 with locus mandatory. |
| P — POV pair | CONVERGES | Both hit all three planted loci, distinguish head-hops/knowledge leak, stay in band, and do not fire POV on clean. |
| R — unpaid-setup pair | CONVERGES | Both identify the brass-key/cabinet unpaid setup, severity, and correct repair fork; both recognize the key as paid in clean. |
| C — continuity pair | **FAILS** | Broken sensitivity is 4/4, but Opus clean `F-P10-01` fires a Should-Fix temporal/age contradiction on reconciled dates. |
| Yellow Wallpaper control (P + S) | CONVERGES | Intentional unreliable first-person deterioration recognized; no registered trap. |
| Gift of the Magi control (R) | CONVERGES | Twin withholding/reveal recognized as fair; no registered trap. |
| Christmas Carol control (S + Lane-2 pilot) | CONVERGES (Lane 1) | Five-stave/compressed-arc traps do not fire; Lane-2 arc/boundaries report only. |
| **Suite** | **FAILS** | Bucket C fails; therefore the four-bucket slice fails. |

## Scoring conventions and matched-pair deltas

The four deltas below were fixed **before** assigning FQ2/FQ4/FQ7.

| Pair | Terra broken → clean delta | Opus broken → clean delta | Delta ruling |
|---|---|---|---|
| Orphan scene | `F-P2-01` on puppet scene → no orphan finding | `F-P2-01` on S4 → no orphan finding | Positive, specific |
| POV break | `F-P7-01` cites two Clara interiors + offstage letter → no POV finding | `F-P7-01` + `F-P7-02` cite the same three access violations → no POV finding | Positive, specific |
| Unpaid setup | `F-P8-01` + `SP-01` unpaid brass key → clean key paid | `F-P8-01` + `SP-01..04` unpaid key/cabinet → clean `SP-01` key paid | Positive, specific. Opus clean flags the *different* locked desk drawer, not the registered paid brass-key plant. |
| Continuity | two Must-Fix contradictions + `CF-01/02` → no registered contradiction | two Must-Fix contradictions → clean Should-Fix date/age lattice | Sensitivity positive; Opus specificity negative |

For FQ4, continuity and reveal findings that also emitted `F-*` blocks were
scored by their finding severity; the CF/SP artifacts corroborate presence.
Clean ceilings were applied separately. For FQ7, fixture-specific traps govern.

## Accuracy summary (not reliability)

Lane-1 in-scope scoring has 38 fixture/model dimensions, maximum 114 points per
model (N/A dimensions excluded; Lane-2 FQ5 excluded).

| Model | Lane-1 points | Accuracy note |
|---|---:|---|
| Terra | **111 / 114** | Only loss: orphan-scene FQ6 = 0 because it diagnoses causal inertness but supplies no first repair action. |
| Opus | **111 / 114** | Only loss: continuity-clean FQ7 = 0 for a spurious Should-Fix continuity/timeline fire on the reconciled control. |

The equal totals conceal qualitatively different behavior: Terra has a repair-
guidance omission on a correctly detected defect; Opus has a specificity error
on sound control material. The latter blocks convergence; the former does not,
because the orphan pair still agrees on locus, mechanism, and severity (3/4).

**Reliability is not estimated.** This artifact contains one scorer's judgments
over two independent engine productions. That is an accuracy/convergence read,
not two scorers independently rating one output. A second scorer would be needed
for reliability; the future ≥3-editor panel has the separate Lane-2 licensing
role.

## Per-fixture FQ scores

Scores are `0–3`; `—` means out of scope. FQ1 here scores the Lane-1 scene/unit
inventory. Any boundary judgment is reported separately as Lane 2.

### Terra

| Fixture | FQ1 | FQ2 | FQ3 | FQ4 | FQ5 | FQ6 | FQ7 | Lane-1 verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| continuity broken | 3 | 3 | 3 | 3 | — | 3 | 3 | Hit |
| continuity clean | 3 | — | — | — | — | — | 3 | Specific |
| orphan broken | 3 | 3 | 3 | 3 | — | **0** | 3 | Hit; repair omitted |
| orphan clean | 3 | — | — | — | — | — | 3 | Specific |
| POV broken | 3 | 3 | 3 | 3 | — | 3 | 3 | Hit |
| POV clean | 3 | — | — | — | — | — | 3 | Specific |
| unpaid setup broken | 3 | 3 | 3 | 3 | — | 3 | 3 | Hit |
| unpaid setup clean | 3 | — | — | — | — | — | 3 | Specific to registered plant |
| Yellow Wallpaper | 3 | — | — | — | — | — | 3 | Trap clear |
| Gift of the Magi | 3 | — | — | — | — | — | 3 | Trap clear |
| Christmas Carol | 3 | — | — | — | **3 report** | — | 3 | Trap clear; Lane-2 positive |

### Opus

| Fixture | FQ1 | FQ2 | FQ3 | FQ4 | FQ5 | FQ6 | FQ7 | Lane-1 verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| continuity broken | 3 | 3 | 3 | 3 | — | 3 | 3 | Hit |
| continuity clean | 3 | — | — | — | — | — | **0** | False continuity fire |
| orphan broken | 3 | 3 | 3 | 3 | — | 3 | 3 | Hit |
| orphan clean | 3 | — | — | — | — | — | 3 | Specific |
| POV broken | 3 | 3 | 3 | 3 | — | 3 | 3 | Hit |
| POV clean | 3 | — | — | — | — | — | 3 | Specific |
| unpaid setup broken | 3 | 3 | 3 | 3 | — | 3 | 3 | Hit |
| unpaid setup clean | 3 | — | — | — | — | — | 3 | Registered key plant correctly marked paid |
| Yellow Wallpaper | 3 | — | — | — | — | — | 3 | Trap clear |
| Gift of the Magi | 3 | — | — | — | — | — | 3 | Trap clear |
| Christmas Carol | 3 | — | — | — | **3 report** | — | 3 | Trap clear; Lane-2 positive |

## Pair audits

### C — continuity contradiction: FAILS on clean specificity

**Broken sensitivity (both runs: 4/4 anchors).** Terra locates the 1832/1841
arithmetic at lines 18–24 and the younger/elder conflict at lines 27–33; its
Pass-10 table repeats both at lines 92 and 101 and emits `CF-01/02` at lines
109–110. Opus likewise gives separate Must-Fix `F-P10-01` and `F-P10-02` blocks
at lines 50–79. Both name continuity (not reveal), cite both sides, use in-band
severity, and keep canon selection open while prioritizing reconciliation.

**Clean specificity.** Terra explicitly records the ages and 1832→1838 arithmetic
as consistent and says “No chronology contradiction” (lines 75–82): FQ7 = 3.
Opus instead creates `F-P10-01` (lines 34–55), deriving a Should-Fix impossibility
from assumed minimum marriage age and maximum “schoolboy” age; its own analysis
admits a university-age reading can close the gap. This is not the registered
deterministic arithmetic conflict, because 1832 + 6 = 1838 is correct and the
two sibling-age statements agree. It is a same-family continuity false positive
on the clean member: FQ7 = 0 and pair FAIL.

Failure cause: **specificity / over-inference**, not recall, seam detection, or
ground-truth ambiguity. The model converts unstated demographic assumptions into
a contradiction after the planted contradiction has been removed.

### S — orphan scene: CONVERGES

Terra's `F-P2-01` (lines 22–32) identifies the puppet-theatre scene and explains
that neither the repair, ribbon, nor puppeteer changes access to bronze, wheel
completion, inspection, or attribution. Opus's `F-P2-01` (lines 31–39) makes the
same cut-test: bronze enters and leaves unchanged. Both severity calls are
Should-Fix, inside the key's Should-Fix..Could-Fix band. Both clean outputs say
no orphan scene (Terra line 25; Opus lines 25–29).

FQ6 differs. Opus says to braid an outcome back into the spine or retire the
vestigial props (broken lines 37–39, 118): mechanism-targeted, FQ6 = 3. Terra
offers diagnosis and synthesis but no first repair action (lines 31, 88): FQ6 =
0, cause **repair-guidance omission**. Convergence still has locus + mechanism +
severity agreement (3/4, locus mandatory) and clean specificity.

### P — POV break: CONVERGES

Terra `F-P7-01` (broken lines 62–74) combines the two Clara-interiority sentences
and the across-town unopened letter, identifying unannounced access shifts in a
Jonah-close narration. Opus separates the two head-hops (`F-P7-01`, lines
107–120) from the omniscient camera cut (`F-P7-02`, lines 124–134). This covers
all three registered loci, names narrative-access/POV rather than voice style or
continuity, and uses accepted Should/Must severity. Both direct repair at the POV
contract (Terra synthesis lines 124–126; Opus lines 116–120, 131–134).

Both clean outputs explicitly find Jonah-close discipline and no perspective
slip (Terra lines 54–55; Opus lines 70–72). The many non-POV findings shared by
clean and broken do not erase the POV delta. All four broken anchors agree and
clean specificity holds.

### R — unpaid setup: CONVERGES

Terra broken `F-P8-01` (lines 23–36) cites the protected brass key, half-fitting
drawer, hidden cabinet, and absent return; `SP-01` at line 38 records the unpaid
thread. Opus traces the same promise through S2/S4 (lines 10–26), marks SP-01..04
unpaid (lines 68–75), and emits Must-Fix `F-P8-01` (lines 98–115). Both target
the right mechanism and repair fork: restore/pay the setup or consciously reduce
it (Terra lines 32–36, Opus lines 168–170).

In clean, both runs acknowledge that the key opens the mantel cabinet and pays
the central setup (Terra outline lines 7–11 and setup table; Opus `SP-01` line
142). Terra's Should-Fix is about earlier spatial preparation; Opus's Should-Fix
is a separate locked-desk-drawer loop (`SP-03`, line 144). Neither labels the
registered brass-key plant abandoned after its on-page payoff, and neither emits
a Must-Fix dropped-thread finding against it. The registered delta therefore
holds. This distinction is necessary: treating every same-family advisory on
different material as a key-trap fire would make FQ7 broader than its fixture
contract.

## Standalone controls and Lane-2 report

### Yellow Wallpaper (P + S)

Terra calls the narrator a single first-person journal perspective and says the
instability is interpretive rather than an accidental breach (lines 52–55).
Opus says reliability degrades intentionally with zero POV leakage (lines
34–35). Neither attaches Must/Should-Fix to voice drift, unreliability, or POV
distance. Their Jane/Jennie ambiguity notes are Could-Fix and outside the
registered trap. FQ1 inventory recovers the entry-by-entry deterioration in
both; FQ7 = 3/3. Control converges.

### Gift of the Magi (R)

Terra's Pass 8 calls the paired sacrifice/reveal clear and fair (lines 35–45).
Opus calls the central engine fully wired, the concealment legitimate, and the
manuscript acceptable as-is (lines 19–24, 77–115, 147–156). Its Could-Fix notes
about intrusive narration and late comb setup explicitly classify those devices
as coherent/deliberate; it does not fire withheld-information or unfair-
misdirection Must/Should-Fix. FQ7 = 3/3. Control converges.

### Christmas Carol (S + Lane-2 pilot)

Both reverse outlines use the five staves as the movement inventory (Terra
lines 3–10; Opus lines 9–13). Terra explicitly says panoramic Present scenes
are not orphans and widen the social claim (lines 41–43); Opus calls the remote
triptych detachable only at Could-Fix and “intentional atmosphere” (lines
24–30, 67–70). Neither fires the registered missing-three-act or rushed-
redemption Must/Should trap. FQ7 = 3/3.

Lane-2 FQ5 = 3 report-only for both: Terra identifies Scrooge's past/present/
future escalation and action-tested reversal (lines 12–21, 45–58); Opus names a
single Scrooge conversion arc across the three vision movements (lines 3, 17–20,
25–29). The band is not α-licensed and does not affect bucket or suite status.

## Recognition / recall and seam flags

| Fixture class | Terra | Opus | Weighting |
|---|---|---|---|
| Four synthetic matched pairs (8 members) | All `RECOGNITION: no` | All `RECOGNITION: no` | No recall flag; full sensitivity/specificity weight |
| Yellow Wallpaper | yes, title + author | yes, title + author | Recall-susceptible corroborating control |
| Gift of the Magi | yes, title + author | yes, title + author | Recall-susceptible corroborating control |
| Christmas Carol | yes, title + author | yes, title + author | Recall-susceptible corroborating control |

No scored broken-member hit relies on “the original says...” or on remembered
text. No bare seam-only diagnosis was counted: every sensitivity hit names the
registered developmental mechanism and cites its in-text locus. The matched
deltas also rule out seam-only scoring for all four pairs.

## Binary/protocol checks

| Check | Result | Audit note |
|---|---:|---|
| Complete-manuscript mode | PASS | Every prompt declares “a complete short work”; no `artifact=partial` appears. Several outputs restate complete mode. |
| Recognition probe | PASS | 22/22 outputs end with a recognition answer. |
| Matched-pair delta before FQ2/FQ4/FQ7 | PASS | Recorded above for all four pairs. |
| Canonical pass coverage | PASS | All outputs cover Passes 0, 1, 2, 5, 7, 8, 10 plus a concluding synthesis/read. Opus Carol lacks a literal `Synthesis` heading but supplies the complete diagnostic conclusion/artifacts before recognition; treated as content conformance, with a format warning. |
| Structured material findings | PASS with format warning | Material findings carry `apodictic.finding.v1` labels and F-* ids; CF/SP artifacts are present where relevant. Serialization varies (fenced YAML, bare block, XML-like tags), so this is human-readable but not uniformly machine-parseable. |
| Consolidated ledger / synthesis | PASS with warning | Each output is a consolidated diagnostic. Opus Carol has no explicit Synthesis heading. |
| No invented score-bearing content | PASS | All evidence used for benchmark scoring is quoted/referenced from the submitted fixture and matches the registered loci. No invented scene/fact/quote affected an FQ verdict. |
| Folder/model naming | PASS | Timestamped source trees and `output-terra.md` / `output-opus.md` naming follow policy. `RUN-MANIFEST.md` records the concrete model ids, CLI versions, prompt hashes, and output hashes. |

## Failure ledger (all FQ scores 0/1)

| Model / fixture / FQ | Score | Cause class | Evidence and ruling |
|---|---:|---|---|
| Terra / orphan broken / FQ6 | 0 | repair-guidance omission | Causal inertness is diagnosed accurately, but the output never gives the first repair target (cut the scene or make it causally load-bearing). Accuracy on FQ2/3/4 remains intact. |
| Opus / continuity clean / FQ7 | 0 | specificity / over-inference | `F-P10-01` manufactures a Should-Fix date/age lattice by assuming marriage/school age ceilings despite reconciled explicit facts. Same-family fire on clean blocks C. |

No 0/1 is attributed to recall contamination, mutation-seam detection, or
ground-truth ambiguity. The only scoring subtlety is the R-clean distinction
between the **registered paid brass-key plant** and Opus's different locked-
drawer setup; the key text is specific enough to resolve it without escalation.

## Decision and next use

Per the benchmark decision rules, this is **revise-and-retest**, scoped to the
continuity specificity failure. The evidence does not support a Lane-1 suite
pass. Engine work should prevent plausibility assumptions from being promoted
to continuity contradictions on explicitly reconciled control facts. A retest
must reuse the locked keys and clean/broken delta; keys must not be edited to
fit these outputs.

The Terra orphan FQ6 omission is a secondary output-quality work item: detected
mechanisms should carry an explicit first repair target. It did not block pair
convergence in this run because the protocol requires 3/4 broken anchors with
locus mandatory, not 4/4.
