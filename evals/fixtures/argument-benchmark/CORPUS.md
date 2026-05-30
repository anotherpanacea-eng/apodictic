# Referenced Corpus — Real Argument Fixtures

Real, published, argument-shaped nonfiction used as benchmark fixtures. The
text is **not stored** (third-party copyright); each piece is *referenced* by
public URL and carries a ground-truth answer key derived from an independent
editor's diagnosis.

- **Ground-truth authority:** Joshua A. Miller (editor) — independent
  diagnoses provided 2026-05-30. This is the external authority the synthetic
  fixtures lack: the diagnoses below were registered *before* any engine run
  and are not the benchmark author's own key.
- **Registered:** 2026-05-30.
- **Run status:** no engine runs yet — the build sandbox blocks outbound web
  fetches (a16z/Atlantic/Reason/Gutenberg all 403 / domain-blocked). Runs must
  happen in a web-enabled environment; see [README.md](README.md) §Running.

## Provenance tier for this corpus (third-party published)

These are a distinct tier from the synthetic and public-domain fixtures:

| Tier | Example | Text stored in-repo? | Key in-repo? |
|------|---------|----------------------|--------------|
| Synthetic / public-domain | `op-ed-warrant-leap`, Swift | yes (synthetic) / no (PD, referenced) | yes |
| **Third-party published (this file)** | Coates, a16z, Cato | **no — referenced (copyright)** | **yes — citation + diagnosis only, no source text** |
| Private / unpublished / client | (none here) | no | gitignored manifest only |

Naming and analyzing *published, attributed* works is ordinary scholarship and
poses no confidentiality issue, so their keys live in-repo. Their **text** is
never stored, and outputs must **paraphrase, not reproduce** (quotation policy:
paraphrase-only).

## Why these are mostly calibration tests, not failure-detection tests

Unlike the synthetic fixtures (which plant a catastrophic, unambiguous
failure), these are competent published arguments with *one* identifiable
structural soft spot. Their primary benchmark value is **severity calibration /
not over-pathologizing**: the engine should diagnose a SOUND argument with a
Should-Fix weakness, not a flood of Must-Fix codes. This is the real-world
analog of the Q7 specificity gate.

---

## The corpus (10 pieces, 4 clusters)

`✓ key built` = full `groundtruth.md` exists. `▢ queued` = diagnosis registered
below; full key to be built.

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
| `andreessen-techno-optimist-manifesto` | Marc Andreessen, "The Techno-Optimist Manifesto" — https://a16z.com/the-techno-optimist-manifesto/ | 6 manifesto | **Claim:** technological acceleration + markets is the central path to human flourishing. **Main structural problem:** manifesto cadence substitutes for argument at key moments. **Strongest objection:** many harms are governance/distribution/externality problems, not shortages of technology. ▢ queued |
| `amodei-machines-of-loving-grace` | Dario Amodei, "Machines of Loving Grace" — https://darioamodei.com/essay/machines-of-loving-grace | 6 visionary essay | **Claim:** powerful AI, if made safe, could produce radical gains across health, poverty, governance, and meaning. **Main structural problem:** confessed speculation still functions like a roadmap. **Strongest objection:** corporate futurism can launder institutional authority through benevolent scenario-building. ▢ queued |
| `bender-stochastic-parrots` | Bender, Gebru et al., "On the Dangers of Stochastic Parrots" — https://dl.acm.org/doi/10.1145/3442188.3445922 | 5 academic | **Claim:** scaling language models produces serious environmental, bias, opacity, and misuse risks. **Main structural problem:** several distinct risk arguments are gathered under one "too big?" frame. **Strongest objection:** the piece develops harms more fully than benefit tradeoffs or institutional alternatives. ▢ queued |

### Cluster C — Criminal justice / probation (2 policy briefs)

| Slug | Piece | Bucket | Registered diagnosis (authority: J. Miller) |
|------|-------|--------|---------------------------------------------|
| `aecf-eliminate-confinement` | Annie E. Casey Foundation, "Eliminate Confinement as a Response to Probation Rule Violations" — https://www.aecf.org/resources/eliminate-confinement-as-a-response-to-probation-rule-violations | 2 policy brief | **Claim:** youth should not be confined for noncriminal probation violations. **Main structural problem:** harm, adolescent development, racial disparity, and efficacy arguments are compressed into one policy ask. **Strongest objection:** what to do with repeated high-risk noncriminal violations short of confinement. ▢ queued |
| `ppi-one-size-fits-none` | Prison Policy Initiative, "One Size Fits None" — https://www.prisonpolicy.org/reports/probation_conditions.html | 2 policy brief / report | **Claim:** standardized probation conditions manufacture technical violations and revocation risk. **Main structural problem:** proving that overbreadth itself (vs. supervision culture or client need) drives outcomes. **Strongest objection:** some standardization may protect fairness and notice. ▢ queued |

### Cluster D — Long-form advocacy + embedded narrative (standalone)

| Slug | Piece | Bucket | Registered diagnosis (authority: J. Miller) |
|------|-------|--------|---------------------------------------------|
| `coates-case-for-reparations` | Ta-Nehisi Coates, "The Case for Reparations" — https://www.theatlantic.com/magazine/archive/2014/06/the-case-for-reparations/361631/ | 7 hybrid (advocacy + narrative) | **Claim:** reparations are owed as a national reckoning for legally structured theft, not merely as compensation for slavery. **Main structural problem:** the leap from concrete housing predation to national remedy. **Strongest objection:** the essay proves *debt* more clearly than it specifies *institutional design*. ▢ queued |

---

## Notes for whoever runs this corpus

1. **Blind runs only.** Feed the engine the source text (fetched from the URL)
   with a neutral label. Do **not** show the engine this file or the
   `groundtruth.md` keys.
2. **Score against the registered diagnosis**, which fixes GT1 (claim),
   GT2 (main structural problem → failure locus), and GT3 (strongest
   objection). GT4–GT7 in each built key are *provisional* mappings pending a
   run or a second editor's confirmation.
3. **Watch the calibration dimension.** For these competent published pieces,
   a correct run names the single structural soft spot at Should-Fix severity
   and resists over-firing. Over-generation (many Must-Fix codes on a sound
   argument) is the characteristic failure to catch here.
