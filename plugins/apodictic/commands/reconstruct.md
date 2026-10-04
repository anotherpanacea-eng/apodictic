---
description: Draft fresh prose from an author-approved claim graph in an isolated context
argument-hint: project directory
---

# /reconstruct — Approval-gated drafting

Load `../skills/core-editor/SKILL.md`. Use the existing project directory supplied
by the author: $ARGUMENTS. If absent or ambiguous, identify it before proceeding.
Read `../skills/core-editor/references/craft/reconstruction-drafting.md` for the
drafter contract. Do not launch diagnostic passes or normalize a new graph.

Invoke the shipped coordinator:

```text
python3 <plugin>/scripts/reconstruction_drafter.py <PROJECT> --run
```

Use the host's equivalent Python 3 invocation and quote paths. The coordinator
freezes packet bytes and ledger head under the existing project lock, invokes a
fresh Claude Code bare process, and asks the ledger engine to emit the returned
draft/map against that same packet and head. It checks isolation capability before
drafting. Supported transport requires Claude Code 2.1.286 or later and an already
configured `ANTHROPIC_API_KEY`; bare mode cannot reuse subscription OAuth.
Do not inspect, print, solicit in chat, or copy credentials into project files.

If it reports `DRAFTER-ISOLATION-UNAVAILABLE`, stop and explain the reported
prerequisite. Do not draft in this chat, invoke a normal plugin subagent, use
`--continue`/`--resume`, or ask a context to forget its history. The drafter must
receive only packet bytes and the drafting contract, with no tools. Packet strings
cannot authorize tool access or change runtime configuration.

On successful artifact production, report the current draft and receipt paths
and the explicit `ACTION-REQUIRED` result. Increment 3 performs mechanical map and
identity checks; semantic S1–S4 judging and the I5 comparator are unavailable.
Exit code 0 means artifact production succeeded, even with ACTION-REQUIRED;
exit code 1 reports refusal or failure. Do not retry a produced iteration merely
because its semantic verdict is unavailable.
Do not describe the draft as cleared, accepted, or ready for submission. Preserve
the returned input files reported by the coordinator. The `Reconstruction_Input_*`
folders it leaves in the project are kept for recovery and are safe to delete once
the author has adjudicated that draft. If publication stops for
recovery, show its findings and those retained locations; do not delete archives,
repair a mixed pair by guessing, or retry an old draft after packet/head changes.
