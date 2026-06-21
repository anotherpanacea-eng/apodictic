# Content Advisory: *The Tidewater Braid* (literary fiction)

<!-- content-advisory: opted-in -->

<!--
Worked example of a contract-conformant Content Advisory (see specialized-audits/references/
content-advisory.md + docs/content-advisory.md). A reader/marketing-facing map of where the
manuscript depicts intense material, at what intensity, on- or off-page — generated ONLY under the
opt-in marker above. It is DESCRIPTIVE, never evaluative: each note records *that* content is
depicted and how, never that it is gratuitous and never that it should be cut. A content note is not
a defect — it carries no Must/Should/Could severity (the intensity scale is orthogonal).

This file is exercised by `validate.sh --check-all` as a canonical release-gate target for
`content-advisory`, under `--strict`: A1 schema, A2 locus shape, A3 no editorial-severity leak (no
Must/Should/Could token, no apodictic:finding block), W1 descriptive-not-prescriptive (no
"should cut/soften …"), and W2 opt-in marker present.
-->

## Content notes

<!-- apodictic:content_note
{"schema":"apodictic.content_note.v1","id":"CN-01","category":"violence","intensity":"high","depiction":"on-page","label":"","loci":["Ch 7 ¶12-18"]}
-->

<!-- apodictic:content_note
{"schema":"apodictic.content_note.v1","id":"CN-02","category":"death-grief","intensity":"medium","depiction":"referenced","label":"","loci":["Ch 2 §1","Ch 11"]}
-->

<!-- apodictic:content_note
{"schema":"apodictic.content_note.v1","id":"CN-03","category":"self-harm-suicide","intensity":"low","depiction":"off-page","label":"","loci":["Ch 9 ¶4"]}
-->

<!-- apodictic:content_note
{"schema":"apodictic.content_note.v1","id":"CN-04","category":"other","intensity":"medium","depiction":"on-page","label":"a drowning, depicted from inside the drowning character's POV","loci":["Ch 6 §3"]}
-->

## Summary (descriptive)

- **Violence** — one on-page graphic sequence (Ch 7); intense but contained to a single chapter.
- **Death & grief** — referenced throughout; the inciting death is off-page, its aftermath on-page.
- **Self-harm** — referenced off-page only (Ch 9); no depicted act.
- **Other** — a first-person drowning sequence (Ch 6), flagged for readers sensitive to it.

## Notes

- **Descriptive, not evaluative.** Each note records what is depicted and how — on- vs off-page,
  at what intensity — for a reader's informed choice. The advisory makes no craft judgment and
  recommends no cut; that is the [Reception Risk audit](../specialized-audits/references/craft/reception-risk.md)'s
  separate job, and even it never appears here as a finding.
- **Off the editorial severity scale.** Depicted content is not a defect. The intensity scale
  (low/medium/high) is orthogonal to the editorial severity scale — and this artifact carries no
  severity token and no `apodictic:finding` block (validator A3).
- **Opt-in.** Generated only under the `content-advisory: opted-in` marker — content warnings are
  contested, and an unbidden one imposes a stance.
