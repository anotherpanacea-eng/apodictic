# Shared Blind-Editor Panel

This directory contains the committed, copyright-safe machinery for the joint
Argument Benchmark M2 / Fiction Benchmark M2b panel. The generated packet and
third-party source bytes live in access-controlled Dropbox, never here.

Build from the existing stripped argument sources and the historical Dickens
prompt (or an equivalently reconstructed prompt):

```bash
python3 evals/panels/shared-blind-editor/build_packet.py \
  --repo "$PWD" \
  --argument-source-dir "/path/to/stale-packet/packet/submissions" \
  --fiction-prompt evals/results/fiction-run-20260714-144857/christmas-carol-arc-control/prompt-terra.txt \
  --output "/access-controlled/path/current"
```

The builder refuses changed copies of the five argument inputs, paragraph-
numbers every unit, emits the closed response schema, and creates the private
source map and reliability ledger. `compile_responses.py` validates at least
three complete sealed returns and emits one `rater,unit,value` CSV per alpha
dimension without semantic judgment. `adjudicate_panel.py` then computes the
audited alpha/CI, derives unique modes or medians/ranges, applies the frozen key
projection, and emits a per-anchor license candidate / provisional /
low-agreement / key-review ruling for independent review.

Hermetic schema/transform check:

```bash
python3 evals/panels/shared-blind-editor/panel_self_test.py
```

The governing contract is
[`docs/shared-blind-editor-panel-spec.md`](../../../docs/shared-blind-editor-panel-spec.md).
