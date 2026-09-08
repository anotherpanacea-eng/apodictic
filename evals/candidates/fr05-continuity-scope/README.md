# FR-05: continuity-scope development candidates

Four original synthetic short-story pairs explore when an apparent continuity
error is a real incompatible fact, a restricted claim, or an intentional
narrative device. Each pair differs by one contiguous replacement; a proposed
repair preserves the story's events and voice. These are unregistered public
development candidates, not accepted benchmark ground truth.

Ten fresh model readings challenged the construction: one intended error
remained ambiguous, and an adjacent material clue prompted a separately frozen
revision of another pair. Three latest-version pairs are retained for further
fixture adjudication. No production engine or model comparison was run, and
neither benchmark difficulty nor frontier advantage has been established.

## Candidate map — operator material

This table and the intent files expose author hypotheses. Never give them to
a reader whose independent assessment you intend to preserve.

| Family | Control / mutation | Distinction | Current construction disposition |
|---|---|---|---|
| Testimony v1 | sable / reed | Official account versus narrator-established fact | AMBIGUOUS-CANDIDATE |
| Quantifier v1 | flint / birch | Restricted set versus universal claim | RETAIN-CANDIDATE |
| Identity v1 | moss / wren | Shared design versus same physical object | REWORK-CANDIDATE; history preserved |
| Identity v2 | glen / marsh | Same distinction, shared paint shortcut removed | RETAIN-CANDIDATE |
| Time v1 | larch / cove | Narrative order versus explicitly fixed event time | RETAIN-CANDIDATE |

Read [the v1 fold](operator/FOLD-v1.md) and
[the identity v2 fold](identity-v2/operator/FOLD.md) for all disagreements,
collateral observations, and the author's reasons for accepting or declining
them. Retention is not a binary answer-key license. In particular, testimony
must not become a scored binary gate on these readings.

## How the screen was conducted

Author intent, the disposition rules, eight inputs, the common prompt, and
eight exact dispatch prompts were frozen in commit `6d039919d98a5bc88007e5c9dbdba85e008f450a`.
Responses were preserved in `6d99c37` before the v1 fold in `46d66d3`.
Identity v2 was separately frozen in `d1d8bd6`; its two new responses were
preserved in `1132a99` before its fold. The original files were not rewritten.

Each input received one fresh agent with no inherited conversation and only
the exact text in its `screening/prompts/<neutral-id>.txt`. The dispatch
arguments were `model=gpt-5.5`, `reasoning_effort=xhigh`, `fork_turns=none`.
Each prompt instructed the reader to use no tools or other sources. Visible
responses used no tools. Same-host agents are instructionally separated;
this is not filesystem access control or a sealed evaluation environment.

The common prompt explicitly teaches evidence-scoping distinctions. These are
**assisted construction screens**, not unassisted production-engine tests.
One response per input gives no estimate of repeatability, variance, accuracy,
or comparative model quality. The author made the recorded fold; independent
package review checks that judgment but does not supply human ground-truth
licensing. All stories were newly authored for this task, not adapted from
existing benchmark prose.

The two `screening/receipts.json` files bind captured response text to frozen
input/prompt hashes. They are dispatcher-owned records, not reviewer-certified
invocation attestations. Full responses are JSON strings to preserve Markdown
whitespace. Unavailable token, budget, elapsed-time, and cost telemetry is
explicitly null; no cost or superiority claim follows from this packet.

## Files and appropriate reuse

- `inputs/*.md`: complete story bodies only, with neutral filenames.
- `common-prompt.txt` and `screening/prompts/*.txt`: the assisted screen and
  exact dispatched text; replaying these repeats that assistance.
- `operator/intent.json` and `operator/criteria.md`: pre-screen hypotheses,
  surgical edits, loci, alternatives, and the ordered fold rules.
- `freeze.json`: SHA-256 and byte lengths for the pre-screen artifacts.
- `screening/responses/*.json` and `screening/receipts.json`: preserved readings
  and their recorded bindings.
- `identity-v2/`: separate repair with the same structure, ancestry hashes,
  new neutral labels, two fresh screens, and its own fold.
- `operator/verify_packet.py`: package-only custody/conservation verification;
  run `python operator/verify_packet.py` from this directory. It does not judge
  prose, truth, or model quality, and is not registered as a production gate.

For a new independent story assessment, supply only the selected story and a
separately specified task prompt. Do not supply this directory, keys, twin,
folds, receipts, or previous responses. The inputs and keys are now public:
future use must disclose that exposure and cannot claim a sealed holdout.

Before any registration, obtain independently licensed fixture adjudication
under the existing [fiction fixture conventions](../../fixtures/fiction-benchmark/README.md)
and [run protocol](../../fixtures/fiction-benchmark/RUN-PROTOCOL.md), inspected
at APODICTIC base `20b8ca6219e649b2743866b9ffaba0e77ab208a5`. Registration,
groundtruth schemas, scoring changes, and production-prompt changes are outside
this packet. In particular, FR-02 corrective retesting remains separate.
