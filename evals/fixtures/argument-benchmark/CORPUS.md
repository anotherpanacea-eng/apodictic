# Referenced Corpus — Real Argument Fixtures

Real, published, argument-shaped nonfiction used as benchmark fixtures. The
text is **not stored** (third-party copyright); each piece is *referenced* by
public URL and carries a ground-truth answer key derived from an independent
editor's diagnosis.

- **Ground-truth authority:** Joshua A. Miller (editor) — diagnoses
  **pre-registered 2026-05-30, before any engine run.** The independence here is
  **temporal, not personal**: the editor is also the benchmark author, so this
  is *single-editor pre-registration*, not an external cross-check. A genuine
  external authority requires a second editor — which GT4–GT8 explicitly await.
- **Registered:** 2026-05-30.
- **Source texts:** all 10 fetched + hashed (preparer, 2026-05-30); SHA-256 +
  method + byte count recorded per source in [SOURCES.md](SOURCES.md). Full text
  is cached **outside the git tree** (copyright; never committed). Coates was
  re-extracted from a clean, correctly-ordered copy (superseding an artifacted
  extraction); all 10 are now clean and load-bearing.
- **Run status:** texts staged for blind runs; **no engine runs yet** (this
  sandbox blocks outbound fetches, so runs happen in a web-enabled session per
  [RUN-PROTOCOL.md](RUN-PROTOCOL.md); any re-fetch must reproduce the recorded
  SHA-256).

## Provenance tier (canonical — matches the spec's four-tier scheme)

These fixtures are **tier 3** in the four-tier provenance scheme used across
the spec, the fixtures README, and this file:

| Tier | Class | Text stored in-repo? | Key in-repo? |
|------|-------|----------------------|--------------|
| 1 | Synthetic | yes (authored) | yes |
| 2 | Public-domain | no — referenced | yes |
| **3** | **Third-party published (this file)** | **no — referenced (copyright)** | **yes — citation + diagnosis only, no source text** |
| 4 | Private / unpublished / client | no | gitignored manifest only |

Naming and analyzing *published, attributed* works is ordinary scholarship and
poses no confidentiality issue, so their keys live in-repo. Their **text** is
never stored, and outputs must **paraphrase, not reproduce** (quotation policy:
paraphrase-only).

## Recognition contamination (construct-validity threat)

The biggest threat to these fixtures is **recognition, not leakage.** The blind
protocol withholds the answer-key *file*, but an LLM engine has very likely seen
the famous pieces — and their *canonical critiques* — in training. A neutral
label does not stop the model from recognizing the text and reciting the
standard objection. Coates GT3 ("proves the debt more clearly than it specifies
institutional design") *is* the textbook critique of that essay, so a "hit"
there may measure **recall, not diagnosis**. This caps construct validity for
the most prominent fixtures.

**Recognition-risk tags** (how memorizable the piece + its standard critique are):

| Risk | Fixtures | Interpretation |
|------|----------|----------------|
| HIGH | Coates, Andreessen, Amodei, Bender et al. | Famous; canonical critiques likely memorized. Treat hits as **recall-susceptible**; weight lightly. |
| MODERATE→LOW | abundance cluster (Roosevelt, Current Affairs, Reason, Cato), AECF, PPI | Real but niche; far less likely to have a memorized canonical critique. **These carry the construct validity.** |

**Mitigations:**
1. **Weight by tag.** Lower-recognition fixtures are the load-bearing evidence;
   HIGH-recognition results are corroborating at best.
2. **Recognition probe (required).** The run must report whether it recognized
   the author/title (see [RUN-PROTOCOL.md](RUN-PROTOCOL.md) Step 2b). If it
   names them, flag the score recall-susceptible.
3. **Optional input perturbation.** Run on a lightly-excerpted / paraphrased
   input to defeat verbatim recognition — with the caveat that paraphrase can
   itself alter structure, so prefer representative excerpting over rewriting.
4. **Future: held-out obscure controls.** Add an obscure piece per cluster (no
   public critique) as a recognition control; convergence between an obscure
   control and its famous sibling separates diagnosis from recall.

## Scope convention (what is authoritative vs. provisional)

For these referenced fixtures, the editor's **prose diagnosis is authoritative**
— GT1 (claim), GT2's *named structural problem* and failure *locus*, and GT3's
*objection zone*. The **code and layer mappings** under GT2 (e.g., "Provisional
codes: …") and **all of GT4–GT8** are provisional benchmark-author scaffolding
pending a run or a second editor. **Score Q2 on the failure locus/layer, not the
exact code** for these fixtures (see RUN-PROTOCOL Step 3).

**GT-as-a-set convention (2026-06-04).** Where a competent argument has more than
one genuinely *structurally-prior* objection or locus, GT2/GT3 may register an
**acceptable set** (any one member, correctly coded, is a hit) rather than a
single answer — under a strict discipline: members must be structurally prior (not
merely salient), **decoys stay registered as misses**, inclusion is earned by a
written structural reason (not by a run finding it), and an expansion is rejected
if it flips a non-converging fixture to "pass" only by blessing a run's error.
Currently applied to roosevelt-GT2, cato-GT3, ppi-GT3 (clarification) — see
[PROPOSAL-gt-sets-20260604.md](PROPOSAL-gt-sets-20260604.md).

## Why these are mostly calibration tests, not failure-detection tests

Unlike the synthetic fixtures (which plant a catastrophic, unambiguous
failure), these are competent published arguments with *one* identifiable
structural soft spot. Their primary benchmark value is **severity calibration /
not over-pathologizing**: the engine should diagnose a WARRANTED argument with a
Should-Fix weakness, not a flood of Must-Fix codes. This is the real-world
analog of the Q7 specificity gate.

**Pairing N/A.** These 10 tier-3 fixtures **cannot** be given matched clean/broken twins — by
construction, not by deferral: a real published op-ed has no authorable clean base (you cannot
un-break someone's argument without writing a derivative of copyrighted text, and neither the
original nor a "repaired" derivative may be stored in-repo). They stay **single-fixture**, carry
their specificity value through the WARRANTED-real-calibration five-anchor rule
([RUN-PROTOCOL.md §Step 4](RUN-PROTOCOL.md)), and take the reliability-tier treatment from the
agreement-as-license ledger. Matched pairs are a property of the *synthetic planted-defect*
fixtures (`op-ed-warrant-leap`, `policy-brief-uncompared`); the referenced PD positive control
`modest-proposal-satire` is likewise unpaired (a control has no planted defect to twin against).

---

## The corpus (10 pieces, 4 clusters)

`✓ key built` = full `groundtruth.md` exists for the slug. All ten keys are
built; GT1–GT3 are authoritative from the registered diagnosis, GT4–GT8 are
provisional pending a run or a second editor.

### Cluster A — The "abundance" debate (topic-controlled; 4 stances)

Same subject, four different argument forms and four different failure loci —
the cluster tests whether the engine recovers *distinct* claims and *distinct*
structural weaknesses while topic is held constant.

| Slug | Piece | Bucket | Status |
|------|-------|--------|--------|
| `roosevelt-democratic-abundance` | Roosevelt Institute, "Democratic Abundance" | 2 policy | ✓ key built |
| `current-affairs-abandon-abundance` | Current Affairs, "Abandon 'Abundance'" | 6 advocacy | ✓ key built |
| `reason-problem-with-abundance-agenda` | Reason, "The Problem With the 'Abundance Agenda'" | 6 advocacy/opinion | ✓ key built |
| `cato-industrial-policy-bad-idea` | Cato, "Industrial Policy: A Bad Idea Is Back" | 2 policy essay | ✓ key built |

### Cluster B — AI & technology futures (3 stances)

| Slug | Piece | Bucket | Registered diagnosis (authority: J. Miller) |
|------|-------|--------|---------------------------------------------|
| `andreessen-techno-optimist-manifesto` | Marc Andreessen, "The Techno-Optimist Manifesto" — https://a16z.com/the-techno-optimist-manifesto/ | 6 manifesto | **Claim:** technological acceleration + markets is the central path to human flourishing. **Main structural problem:** manifesto cadence substitutes for argument at key moments. **Strongest objection:** many harms are governance/distribution/externality problems, not shortages of technology. ✓ key built |
| `amodei-machines-of-loving-grace` | Dario Amodei, "Machines of Loving Grace" — https://darioamodei.com/essay/machines-of-loving-grace | 6 visionary essay | **Claim:** powerful AI, if made safe, could produce radical gains across health, poverty, governance, and meaning. **Main structural problem:** confessed speculation still functions like a roadmap. **Strongest objection:** corporate futurism can launder institutional authority through benevolent scenario-building. ✓ key built |
| `bender-stochastic-parrots` | Bender, Gebru et al., "On the Dangers of Stochastic Parrots" — https://dl.acm.org/doi/10.1145/3442188.3445922 | 5 academic | **Claim:** scaling language models produces serious environmental, bias, opacity, and misuse risks. **Main structural problem:** several distinct risk arguments are gathered under one "too big?" frame. **Strongest objection:** the piece develops harms more fully than benefit tradeoffs or institutional alternatives. ✓ key built |

### Cluster C — Criminal justice / probation (2 policy briefs)

| Slug | Piece | Bucket | Registered diagnosis (authority: J. Miller) |
|------|-------|--------|---------------------------------------------|
| `aecf-eliminate-confinement` | Annie E. Casey Foundation, "Eliminate Confinement as a Response to Probation Rule Violations" — https://www.aecf.org/resources/eliminate-confinement-as-a-response-to-probation-rule-violations | 2 policy brief | **Claim:** youth should not be confined for noncriminal probation violations. **Main structural problem:** harm, adolescent development, racial disparity, and efficacy arguments are compressed into one policy ask. **Strongest objection:** what to do with repeated high-risk noncriminal violations short of confinement. ✓ key built |
| `ppi-one-size-fits-none` | Prison Policy Initiative, "One Size Fits None" — https://www.prisonpolicy.org/reports/probation_conditions.html | 2 policy brief / report | **Claim:** standardized probation conditions manufacture technical violations and revocation risk. **Main structural problem:** proving that overbreadth itself (vs. supervision culture or client need) drives outcomes. **Strongest objection:** some standardization may protect fairness and notice. ✓ key built |

### Cluster D — Long-form advocacy + embedded narrative (standalone)

| Slug | Piece | Bucket | Registered diagnosis (authority: J. Miller) |
|------|-------|--------|---------------------------------------------|
| `coates-case-for-reparations` | Ta-Nehisi Coates, "The Case for Reparations" — https://www.theatlantic.com/magazine/archive/2014/06/the-case-for-reparations/361631/ | 7 hybrid (advocacy + narrative) | **Claim:** reparations are owed as a national reckoning for legally structured theft, not merely as compensation for slavery. **Main structural problem:** the leap from concrete housing predation to national remedy. **Strongest objection:** the essay proves *debt* more clearly than it specifies *institutional design*. ✓ key built |

---

## Notes for whoever runs this corpus

1. **Blind runs only.** Feed the engine the source text (fetched from the URL)
   with a neutral label. Do **not** show the engine this file or the
   `groundtruth.md` keys.
2. **Score against the registered diagnosis**, which fixes GT1 (claim),
   GT2 (main structural problem → failure locus), and GT3 (strongest
   objection). GT4–GT8 in each built key are *provisional* mappings pending a
   run or a second editor's confirmation.
3. **Watch the calibration dimension.** For these competent published pieces,
   a correct run names the single structural soft spot at Should-Fix severity
   and resists over-firing. Over-generation (many Must-Fix codes on a sound
   argument) is the characteristic failure to catch here.
