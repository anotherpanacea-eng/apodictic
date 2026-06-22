# Author Style Explanation — J. Marsh

<!-- author-style-explanation: local-only -->

<!--
Worked example of a contract-conformant Author Style Explanation (see
docs/interpretable-stylometric-explanation.md). The DESCRIPTIVE labelling layer ON TOP of the Author
Voice Fingerprint (#9): #9 measures HOW distinctive a voice is and persists it as scalar z-scores;
this overlay attaches a natural-language gloss to a handful of the salient MEASURED features, each
bound by provenance (`feature_ref`) to the exact SETEC voice_profile feature it describes
(families.<family>.top_features[].{feature, mean, sd, cv}). It does no new stylometry and offers no
advice — it NAMES a measured feature, it never prescribes a voice change ("write more like X",
"vary your function-word profile") and never fabricates a style claim.

This file is exercised by `validate.sh --check-all` as a canonical release-gate target for
`style-explanation`, under `--strict`:
  X1 schema           — every block is a well-formed apodictic.style_label.v1 (closed enums, SL-NN id).
  X2 provenance       — every label cites a non-empty `feature_ref` into a consumed measurement.
  X3 no-severity      — no Must/Should/Could token in the prose or a label; no apodictic:finding block.
  X4 descriptive      — the prose and every label are descriptive, never a directive or a model to
                        emulate (the indicative "elevated use of the definite article", never the
                        imperative "elevate your diction").
  X5 same-register    — the one describes-cluster claim (SL-03) references only the two
                        `literary-fiction` labels; no cross-register cluster.
  X6 local-only       — the local-only marker is present; no external URL.
  W1 seed/coverage    — three features are glossed (>= 2), so the overlay is not thin.
One label sits WITHIN the same-register coordinating-function-word cluster (SL-01/SL-02 → SL-03); a
third (SL-04) sits just OUTSIDE it (a punctuation feature, not part of the function-word cluster).
These are observations only — the author reads which measured features characterize the voice.
-->

## Style labels

<!-- apodictic:style_label
{"schema":"apodictic.style_label.v1","id":"SL-01","feature_family":"function-words","frame":"describes-feature","direction":"elevated","magnitude":"marked","feature_ref":"families.function_words.top_features[the] (cv 0.077, mean 0.052)","feature_tokens":["the"],"label":"The prose leans markedly on the definite article — 'the' is the most stable, most frequent function word in the baseline.","register":"literary-fiction"}
-->

<!-- apodictic:style_label
{"schema":"apodictic.style_label.v1","id":"SL-02","feature_family":"function-words","frame":"describes-feature","direction":"elevated","magnitude":"moderate","feature_ref":"families.function_words.top_features[and] (cv 0.097)","feature_tokens":["and","but"],"label":"Short coordinating runs recur — the function-word profile is concentrated in 'and' and 'but'.","register":"literary-fiction"}
-->

<!-- apodictic:style_label
{"schema":"apodictic.style_label.v1","id":"SL-03","feature_family":"function-words","frame":"describes-cluster","direction":"elevated","magnitude":"moderate","feature_ref":"families.function_words coordinating cluster (SL-01, SL-02)","label":"Taken together, SL-01 and SL-02 read as a coordinating-function-word signature: a definite-article lean paired with short 'and'/'but' runs, both within the literary-fiction baseline.","register":"literary-fiction"}
-->

<!-- apodictic:style_label
{"schema":"apodictic.style_label.v1","id":"SL-04","feature_family":"punctuation","frame":"describes-feature","direction":"reduced","magnitude":"slight","feature_ref":"families.punctuation.top_features[em-dash]","feature_tokens":["—"],"label":"Slightly reduced em-dash use relative to the author baseline — punctuation runs plainer here, outside the coordinating-function-word cluster above.","register":"literary-fiction"}
-->

## Reading the overlay (observations — the author judges)

- **Definite-article lean (SL-01).** The most stable function-word feature in the baseline; the prose
  rests on `the` more than on any other closed-class word. A signature, not a defect — the overlay
  names where the distinctiveness lives.
- **Coordinating runs (SL-02).** `and`/`but` carry the short coordinating cadence the voice is known
  for. The label glosses the measured feature; it does not ask the author to change it.
- **The cluster (SL-03).** SL-01 and SL-02 form one same-register coordinating signature. The cluster
  claim stays within `literary-fiction` — a cross-register cluster would be a comparability error.
- **Plainer punctuation (SL-04).** Em-dash use sits slightly below the author baseline. `reduced` is
  the indicative direction (where the feature sits vs the author's own prior corpus), never an
  instruction to change it.

## Notes

- **No new stylometry.** Every label consumes an existing SETEC `voice_profile` feature via
  `feature_ref`; the overlay adds only the natural-language gloss, never a new measurement.
- **Descriptive, no severity.** These are descriptions of measured features, never prescriptions and
  never findings — the overlay carries no Must/Should/Could severity. It reports where the measured
  features sit; the author alone decides whether any of it is worth acting on.
- **Local-only.** A labelled voice profile is voice-cloning-adjacent; it carries the local-only
  marker, makes no external call, and is never transmitted.
