# FR-02 anonymous scoring supplement

This implements PROTOCOL.md without changing its primary outcome or treatment.
Freeze this supplement and scorer implementation before making any scorer call.
Use two independent fresh Codex subscription contexts per sealed diagnosis:
`gpt-5.5` high and `gpt-6-astra` high. This is same-provider scorer reliability,
not cross-vendor confirmation, independent production convergence, or human
licensing. A scorer never receives another scorer's result.

Assembly refuses until all 64 planned productions have sealed valid completion
receipts. It validates the production freeze and every output hash, then packages
one diagnosis with its corresponding submission, registered key, and frozen
rubric/anchors. The packet omits model, prompt arm, repetition, paired sibling
output, historical results, and production request metadata. Random opaque IDs
and order are committed in a private mapping before dispatch. Keys remain local
and are dispatched only to these qualified Codex scoring contexts, never to
production runners. Models are instructed to treat quoted artifacts as evidence,
not instructions. Numeric grading does not override provisional-key uncertainty.

Require structured JSON with a planted-mechanism disposition, cited unsupported
findings classified as continuity/other, fabricated content, mandatory invented
repairs, central key ambiguities, and the seven predeclared component scores.
Mechanism detection requires an in-text locus and a correct mechanism; bare
seam detection is not a hit. Quotes must be verifiable against the supplied
output or submission after whitespace normalization only. Missing or invalid
quotes, malformed JSON, schema mismatch, uncompleted transport, or scorer tool
use make a score invalid/unresolved. There is no automatic re-prompt to obtain
a more convenient grade. Retain raw records and report invalid cells separately.

For each model/arm/repetition, join the clean and broken continuity members only
after individual scores are sealed. A conservative agreed pair succeeds only
when both scorers say the broken mechanism is detected, both identify zero
unsupported clean Must/Should-Fix continuity findings, and neither reports a
central key ambiguity. Scorer disagreement, unclear severity, or invalid score
means unresolved; do not coerce it to a fail or pass. Other clean false positives
and any introduced invention remain visible and feed the protocol transfer guard.

Report per-scorer outcomes alongside consensus/unresolved counts. Compute the
primary treatment threshold and transfer guard separately for each production
model. Compare corresponding repetition indices descriptively, not as a paired
causal estimate: model calls are independent stochastic productions. Do not pool
repetitions into a claim about new independent source works. Two scorer votes
cannot license a disputed key or make a fixture ground truth.

Final independent review may challenge scoring with verbatim evidence. Preserve
both original grades and any explicit advisory resolution as a separate artifact;
do not silently rewrite scores. The original frozen conservative result remains
available even if a later human review settles a dispute.
