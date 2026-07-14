# Shared Blind-Editor Panel — Build Contract

**Status:** **Built** for the 2026-07 M2 panel packet and fiction M2a evidence publication
<!-- built-when: evals/panels/shared-blind-editor/build_packet.py -->
**Owners:** Argument Benchmark M2 + Fiction Benchmark M2b
**Privacy boundary:** copyrighted third-party source bytes stay outside git;
metadata, hashes, keys, protocols, response schemas, permitted synthetic/public-
domain fixtures, and copyright-safe result artifacts may ship

## Problem

The existing Dropbox argument packet is not usable for the current benchmark. It asks one editor for open prose, uses the retired `SOUND / UNSOUND` verdict vocabulary, omits GT8 and the Reliability ledger, and cannot produce the closed, tidy ratings required by `agreement-alpha`. Fiction M2b separately requires a three-or-more-editor panel for its Lane-2 boundary and arc bands. These must be one panel protocol, not two incomparable exercises.

The fiction M2a run also exists only under the default gitignored results policy. Its scorecard, manifest, keys, prompts/protocol, fixture hashes, and source reconstruction path must become independently inspectable without committing copyrighted source bytes.

## Deliverables

### A. Shared panel packet (Dropbox, not git)

Regenerate the packet at `Cowork/Development Editor/argument-benchmark-second-editor-packet/current/` and mark every older packet copy stale. The sendable `packet/` contains only:

- neutral source files `A01`–`A05` (argument) and at least four independent
  fiction works `F01`–`F<n>`; the initial packet uses the seven distinct works
  already in the fiction slice (the three standalone controls plus the four
  clean synthetic bases; broken twins are excluded because they are not
  independent units);
- editor instructions and a closed-response form;
- a response CSV with fixed enums and one pseudonymous `editor_id`;
- no titles, authors, fixture slugs, answer keys, source URLs, expected values, or prior run outputs.

The operator-only side contains:

- the neutral-id map, source SHA-256 values, provenance class, and repo-key path;
- a panel ledger tracking pseudonymous editor id, qualifications/conflicts,
  benchmark or key exposure, sealed-return status, AI/consultation attestation,
  invitation/return status, exclusions, per-piece recognition, packet hash, and
  response-file hash;
- dimension-specific tidy CSV templates (`rater,unit,value`) accepted by `validate.sh agreement-alpha`;
- scoring/reconstruction instructions and the pre-registered metric/threshold table;
- a recruitment note that requires at least three qualified, mutually independent editors and asks each recruited editor to complete both domains.

Existing third-party argument source bytes are reused exactly and re-hashed.
`F01` is the SHA-pinned public-domain Dickens fixture reconstructed through the
fiction runner; the remaining fiction units are the copyright-safe stored
public-domain and synthetic clean works. Packet source bytes are never copied
into git. Before any third-party bytes are sent, the operator records the lawful
access/distribution basis and applies access control; “outside git” is not
treated as permission to redistribute.

### B. Closed response contract

Every rating uses a listed token; explanatory notes are optional and never enter alpha.

Argument units (`A01`–`A05`) collect:

| Anchor | Closed value | α metric |
|---|---|---|
| GT2 primary layer + locus | layer `CLAIM / SUPPORT / WARRANT / SCOPE / BURDEN / OBJECTION / NONE`; paragraph id(s) from the packet's closed paragraph index | nominal layer + ordinal normalized locus |
| GT4 expertise | `GENERAL / MIXED / SPECIALIST` | ordinal |
| GT4 receptivity | `HOSTILE / MIXED / SYMPATHETIC` | ordinal |
| GT4 consequence | `LOW / MEDIUM / HIGH` | ordinal |
| GT5 load-bearing vulnerability | family `CLAIM / SUPPORT / WARRANT / SCOPE / BURDEN / OBJECTION / DEFINITION / AUDIENCE / IMPLEMENTATION / NONE` + paragraph id(s) | nominal family + ordinal normalized locus |
| GT6 first repair target | same family enum + paragraph id(s) + dependency `BEFORE_SUPPORT / BEFORE_SCOPE / BEFORE_OBJECTION / BEFORE_IMPLEMENTATION / INDEPENDENT / NONE` | nominal family + ordinal normalized locus + nominal dependency |
| GT7 warrant verdict | `WARRANTED / UNCONVENTIONAL-BUT-WARRANTED / UNWARRANTED` | nominal; also report warranted-family vs `UNWARRANTED` |
| GT8 premise flag | `NONE_REGISTERED / FLAG_PRESENT`; when present, paragraph id(s) identifying the load-bearing premise | nominal presence + ordinal normalized locus |
| GT8 flag type, when present | one or more of `CONTESTABLE / UNEARNED / OVERLOADED / EXTERNAL-VERIFY / DEFINITIONAL` | nominal binary column per type |

GT5's family+locus metric and GT6's dependency metric are registered here before
panel data because the older argument spec omitted them. Paragraph ids are
closed integers printed into each neutral text. For cross-work α, a paragraph
id is deterministically mapped to `round(100 * (id - 1) / (paragraph_count -
1))`; a one-paragraph unit maps to `0`. Multiple loci become separate ranked
slots (`locus_1`, `locus_2`) and are never joined into an ad-hoc string. GT8 may
produce `alpha=UNDEFINED (D_e=0)` if every editor selects one constant value;
that non-clearing rule applies to every dimension, not only GT8.

The frozen key-projection table defines which collected subdimensions are
gating for each anchor. `locus_2` is supplementary unless that key has a second
registered locus row. GT8 locus/type rows are required only for a key with
`FLAG_PRESENT`; the current five argument keys register `NONE_REGISTERED`, so
their projection contains presence only. The adjudicator supports both locus
slots and every GT8 binary type and includes every projection row in the
anchor's min-of-subdimensions gate; it may not infer an omitted projection after
returns exist.

Ordinal token transforms are fixed before collection: GT4 expertise maps
`GENERAL=1`, `MIXED=2`, `SPECIALIST=3`; receptivity maps `HOSTILE=1`,
`MIXED=2`, `SYMPATHETIC=3`; consequence maps `LOW=1`, `MEDIUM=2`, `HIGH=3`.
Movement count is already numeric. Normalized loci use the `0..100` transform
above. The packet transformer must reject, not guess at, any unlisted token.

Every independent fiction unit collects:

| Anchor | Closed value | α metric |
|---|---|---|
| FGT1 major-movement count | integer `1`–`9` | ordinal numeric as entered |
| FGT1 boundary loci | up to eight paragraph ids, in reading order | ordinal normalized locus per ranked slot |
| FGT1 boundary pattern | `FORMAL_DIVISIONS / VISITATION_OR_ENCOUNTER / CAUSAL_TURNS / HYBRID / OTHER_RECURRENT / NO_STABLE_PATTERN` | nominal |
| FGT5 gross arc | `DENIAL_STAGED_CONFRONTATION_REVERSAL / STEADY_GROWTH / FALL / CIRCULAR_RETURN / FLAT_NO_REVERSAL / OTHER` | nominal |

This supplies multiple reliability units per fiction dimension; three raters on
one text would not. The fiction key continues to score its registered band, but
the packet does not disclose keyed choices. A dimension cannot promote merely
because editors agree with one another: after α clears, its panel-derived value
must also be reconciled to the pre-registered key under the adjudication rule
below.

### C. Reliability and promotion

- Minimum panel: three participating qualified editors, each rating every unit
  in both domains unless a documented exclusion applies; report attrition and
  missingness. Returns are individual and sealed. Editors attest that they did
  not consult one another, use AI assistance, inspect keys/run outputs, or
  previously participate in this benchmark; conflicts and prior recognition are
  recorded rather than silently waived.
- Minimum reliability base: at least **four pairable units** per α dimension.
  Fewer than four is non-clearing even when the point estimate is defined; this
  freezes the calculator's small-n warning as a promotion rule before returns.
- Thresholds: bootstrap 95% CI lower bound `>= .800` licenses; `.667 <= lower bound < .800` remains provisional; `< .667` becomes low-agreement/report-only.
- Argument GT4 promotes only if every subscale clears. GT5, GT6, GT8, and FGT1
  promote only if every registered categorical/locus/dependency subdimension
  clears. Multi-token GT8 types are computed as separate nominal binary
  dimensions.
- Recognition is recorded per unit. Primary α includes all eligible blind returns; a recognition-excluded sensitivity analysis is reported when any unit is recognized.
- Panel-derived value: nominal dimensions use the unique mode; ordinal
  dimensions use the median and the inclusive observed `[min,max]` range of
  eligible non-missing ratings. A tie, an undefined
  α/CI, insufficient pairable units, or a non-unique mode is non-clearing.
  Compatibility is mechanical against a frozen, committed key-projection table:
  a nominal mode must be in that anchor's `accepted_tokens`; an ordinal median
  must fall in its inclusive `accepted_min..accepted_max`; every ranked locus
  median must fall in its corresponding normalized interval; and each required
  subdimension must clear. The projection table is written from the existing
  key before any returns, including explicit token sets for range-valued key
  prose (for example `SYMPATHETIC->MIXED` projects to `{2,3}`). Missing or
  ambiguous projection data is non-clearing. Fiction calibration units without
  a pre-existing key contribute to α but cannot themselves promote; the Carol
  anchor promotes only if its panel-derived values satisfy its frozen
  projection. Clearing α plus compatibility licenses the anchor/band. Clearing
  α but an incompatible panel value is
  `KEY-REVIEW`, never automatic key rewriting: a qualified adjudicator who has
  not seen engine outputs reviews the sealed panel data and source, records the
  ruling, and either revises the key with provenance or leaves it provisional.
- No Reliability ledger or fiction decision-use field changes until the panel
  is complete and the measured result and any key reconciliation have been
  independently reviewed.
- The five argument units can promote only their own GT4–GT8 anchors (and the
  separately named current-affairs GT2 check). Every unpanelled argument fixture
  remains unchanged and provisional; this packet does not complete the entire
  ten-unit argument corpus.

### D. Committed reconstructable M2a evidence

Commit the fiction M2a `SCORECARD.md` and `RUN-MANIFEST.md` as the scoring outputs. They must identify concrete providers, repository base, fixture/prompt/output hashes, recognition results, score denominators, per-fixture scores, exclusions, reliability limits, and the 3/4 Lane-1 failure. Commit or retain in git every copyright-safe dependency needed to reconstruct the prompts: synthetic/public-domain permitted fixtures, keys, rubric, runner, source manifests, SHA-pinned fetch/carve instructions, and protocol.

Commit the 22 historical raw model outputs because every fiction input in this
slice is original synthetic or public domain and the result policy permits
those outputs. Do not commit stderr/provider reasoning transcripts. An auditor
can therefore verify the historical evidence classifications and scores, while
also reconstructing the pinned inputs and byte-identical prompts locally.

Add a verifier that checks the committed evidence package for:

1. all 11 manifest fixture rows and unique ids;
2. prompt hashes matching locally generated `--prompt-only` prompts;
3. fixture hashes matching stored or fetched/derived bytes;
4. committed raw-output hashes matching the manifest;
5. score totals and exclusions matching a committed tidy score table;
6. no forbidden copyrighted source or provider-stderr files in the published
   package.

## Acceptance gates

- A fresh operator can identify one current packet and cannot accidentally send the stale one.
- The sendable response CSV is schema-closed and can be transformed without judgment into one tidy CSV per α dimension.
- `agreement-alpha` accepts each populated template shape; the templates themselves contain no fabricated ratings.
- The packet manifest verifies every included source hash and names the reconstruction route.
- The committed M2a evidence verifier passes from a clean checkout after fetching the one referenced Dickens source; offline mode must still verify all committed evidence and report the fetch-dependent check as skipped, not passed.
- `bash scripts/validate.sh --check-all`, changelog assembly, status drift, and mirror checks pass.
- An independent spec review and an independent implementation review have no unresolved findings.

## Non-goals

- Recruiting or impersonating human editors.
- Fabricating panel ratings or α results.
- Promoting any Reliability ledger before measured panel data exists.
- Repairing the continuity-specificity engine failure or rerunning M2a.
- Publishing copyrighted argument source bytes or provider stderr/reasoning
  transcripts.
