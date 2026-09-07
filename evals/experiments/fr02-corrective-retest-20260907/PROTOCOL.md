# FR-02 continuity corrective retest

Status: independently reviewed for execution on 2026-09-07; immutable packet freeze precedes model runs.

## Question and scope

Does a generic constraint-grounding instruction reduce unsupported continuity
findings while preserving detection of explicit contradictions and unrelated
structural faults? Compare the current benchmark projection with that projection
plus one fixed instruction. This is an exploratory re-test, not a production
prompt change, a whole-suite M2 pass, or human-licensed benchmark promotion.

Source pin: Apodictic `20b8ca6219e649b2743866b9ffaba0e77ab208a5`.
Use only the eight already-public original synthetic fixtures in
`evals/fixtures/fiction-benchmark/{continuity-contradiction,pov-break,orphan-scene,unpaid-setup}/{clean,broken}/fixture.md`.
Verify each logical body against its recorded `SOURCES.md` SHA-256. Fail on a
mismatch. No reconstructed modern work, private manuscript, existing FR-05
candidate, or remembered source is an input.

The continuity pair is exposed development evidence: its prior false positive
informed this correction. The other three registered pairs are transfer controls
reserved before viewing their keys or outputs in this session. They are public
and previously benchmarked, so they are not a novel or contamination-free holdout.
No case or output may be used to change the frozen instruction within this run.

## Treatment and production

Baseline is the exact `HEADER` heredoc in the pinned `run.sh`, followed by the
same neutral `<submission>` wrapper and logical fixture body. Corrective is
baseline with the following paragraph inserted immediately before submission:

> Before asserting a continuity contradiction, identify the manuscript commitments,
> their textual loci, referents, and relevant story times. Separate explicit facts
> and necessary calculations from plausible but unstated assumptions. Require an
> asserted contradiction to survive removing those assumptions. A consistent
> assignment compatible with the stated text defeats an impossibility claim;
> invented events or unestablished narrator unreliability cannot rescue an explicit
> collision. Preserve contradictions established by explicit facts or necessary
> calculation. Leave any choice of canon or repair to the author.

Fresh, independent contexts for each input; no tools, sibling cases, file paths,
descriptive slugs, keys, expected outcomes, prior outputs, or model comparisons
in the model-visible prompt. Preserve the projection's recognition question.
Do not claim the projection delivers the full canonical references.

Primary candidate: `gpt-6-astra`, high reasoning. Mid-tier control:
`gpt-5.6-terra`, high reasoning. Both use the authenticated Codex subscription,
the same CLI version, configuration, bytes, and access path. No fallback model.
This isolates requested configuration rather than weights or hidden service state.
Record requested model and any machine-returned served identity separately;
do not infer a served identity from the model's text.

Matrix: 8 inputs x 2 prompts x 2 models x 2 independent repetitions = 64
planned productions. Deterministically shuffle the complete matrix before
dispatch, with its order saved and hashed. At most two productions run
concurrently; all artifacts are per-invocation. Stop launching by 21:00 local
time to leave scoring and custody time before the owner's 22:00 deadline.
Missing cells remain missing. Transport failures may be retried once in a new
attempt directory with the original failure retained; never regenerate to improve
an answer. Unexpected tool use contaminates a run and is reported separately.

Optional cross-vendor replication is a separate frozen supplement, not silently
added to the primary denominator. It requires verified seat posture and enough
time. No paid API, GPU, training or cloud budget is authorized by this protocol.

## Freeze and custody

Before the first production, save and SHA-256-bind this protocol, runner version,
CLI version, baseline and corrective templates, logical bodies, exact delivered
prompts, randomized order and manifest. Save a preregistration receipt with UTC
time. Preserve all frozen bytes; later changes require a new run ID.

Each completion records UTC start/end, return code, prompt/output hash, exact
command/settings, JSON event log, stderr, final text, and token usage when exposed.
Record unavailable max_tokens, service identity or cost as null with a reason.
Subscription usage is not a zero-cost API claim. Append atomic completion receipts
only after output is on disk; a resume validates its saved hashes before skipping.
All model outputs, scorer packets, run order and case mapping stay in ignored local
results. The tracked experiment contains tools, protocol and aggregate findings.

## Scoring and decision rule (frozen before outputs)

The scorer is separate from each blind production. Seal final outputs before
opening keys. Each scorer packet contains one anonymous output ID, the output,
its corresponding submission and fixture-specific scoring key, plus the rubric.
The key necessarily identifies the expected mechanism and source condition; this
is scorer knowledge, never runner knowledge. Hide model, prompt arm, repeat,
paired sibling output and historical results. Join pairs and unblind only afterward.
An independent reviewer challenges the scored evidence and disposition. Two scorers
of one output measure reliability, not independent production convergence.

Use the registered fiction rubric and keys as the existing scoring reference,
preserving their Lane-1 versus provisional Lane-2 distinction. Do not amend keys.
For each output retain cited evidence for: (a) unsupported continuity findings on
clean text, by severity; (b) detection of the registered planted mechanism on broken
text, with in-text loci and a correct mechanism; (c) fabricated facts or mandatory
rewrites; (d) recognition and abstention. A vague seam flag is not a mechanism hit.
Ambiguous scoring is unresolved, not a pass. Save dissent instead of majority truth.

Primary outcome per model: number of independent repetitions where the continuity
pair both avoids an unsupported Must/Should-Fix continuity allegation on the clean
member and detects the registered contradiction mechanism on the broken member.
Minimum meaningful treatment delta: at least one additional pair success of two,
without losing any baseline broken-member mechanism hit. The direction must be
reported for each model separately; do not pool correlated model/configuration runs.

Transfer guard: no loss of an existing baseline planted-mechanism hit in the other
three pairs at the same model/repetition, and no increase in clean Must/Should-Fix
false-positive count. A treatment-induced fabrication or mandatory invented repair
is a hard failure. Historical baseline counts are context, never denominator cells.

Decision: if the primary threshold and transfer guard are met, recommend a larger
fresh independently adjudicated test. If baseline is already at ceiling, report
no demonstrated improvement, even if corrected performance is perfect. If a guard
fails, recommend revising or rejecting this corrective. If any necessary cell or
scoring disposition is missing, report incomplete rather than silently shrinking
the matrix. Two repetitions provide descriptive evidence, not a powered superiority
claim, and model agreement cannot confer human ground-truth authority.

The board's 100-point rubric is secondary and descriptive. Score each component
at zero, half, or full weight with a cited rationale, using the anchors below.
It cannot overrule the named primary outcome or hard failures. A provisional
key disagreement is unresolved and not numerically graded as model error.

| Component | Weight | Full | Half | Zero |
| --- | ---: | --- | --- | --- |
| Correctness | 30 | All applicable licensed key mechanisms correctly handled | At least one handled, another missed or wrong | None handled or central diagnosis contradicted by text |
| Grounding | 15 | Every material finding cites supporting in-text evidence | Some supported, some weak/unlocated | No supported material evidence or fabricated quotation |
| Specificity | 15 | No unsupported Must/Should-Fix finding | Only unsupported Could-Fix suggestions | Any unsupported Must/Should-Fix finding |
| Cross-artifact reasoning | 15 | Timeline, outline and findings agree on applicable explicit commitments | Incomplete reconciliation without contradiction | Internal artifact conflict or incompatible explicit commitments |
| Uncertainty | 10 | Assumptions separated from facts and ambiguity acknowledged where needed | Some ambiguity acknowledged, one assumption overstated | Central unsupported assumption treated as certain |
| Minimality | 10 | Diagnosis stays within text, proportional optional repair direction | Redundant or broad advice without invented content | Mandatory invented content or rewriting |
| Reproducibility | 5 | Pinned inputs/settings plus sealed valid output and usage receipt | Output sealed but a disclosed receipt field unavailable | Input/output binding missing or contamination |

An output with no material finding may receive full grounding when its clean-text
abstention is supported by a text-specific account. Empty, truncated or nonresponsive
outputs receive zero correctness/grounding. These anchors describe this frozen
experiment, not a reusable calibrated scale.
