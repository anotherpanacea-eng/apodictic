# Rhetorical purpose: blind-screen execution brief

Status: **draft for owner freeze.** No readings have run. The two candidate decks require roster, prompt, rubric and decision rule to be frozen before any blind reading ([first increment](../rhetorical-purpose-first-increment/PROTOCOL.md), [constitutive controls](../rhetorical-purpose-constitutive-controls/PROTOCOL.md)). This brief supplies those four things and nothing else. Running it is a separate, owner-authorized step.

## Packets and reads

| Deck | Packets | Prompt and rubric |
|---|---|---|
| First increment | R01–R20, S0, S1 (22) | That deck's PROTOCOL: common neutral prompt and seven-dimension table |
| Constitutive controls | H01–H03, N01–N03, U01–U03 (9) | That deck's PROTOCOL: its prompt and six dimensions |

31 packets, two readers each: 62 reads. The prompts and rubrics are used verbatim. This brief changes neither.

## Roster

- **Reader A:** Claude (current Opus), one fresh context per packet.
- **Reader B:** GPT through Codex, one fresh context per packet.
- **Adjudicator:** a third fresh context that is not the session that dispatched the reads. It sees both saved readings and then the key.
- **Human panel:** the owner. It decides every packet the adjudicator marks disputed.

Each reader receives exactly the deck's prompt followed by one INPUT body, with no tools, files, repository access or browsing. Two model families keep the readers independent of each other; neither sees the other's output.

## Recording

For each read, save the raw output unedited, then fill the deck's rubric table from it: one row per dimension with status, anchor and a one-line reason. No scalar total. Readings are saved before anyone opens `expected.md`.

## Decision rule per packet

The adjudicator compares each reading with the packet's key on two lines only: **Proposed defect/repair** (did the reader reach the same finding or the same absence of a finding, with an anchor?) and **Prohibited outputs** (did the reader produce any?).

| Outcome | When |
|---|---|
| **Retained candidate** | Both readers match the key on defect/repair, neither produces a prohibited output, and the adjudicator agrees. |
| **Disputed** | The readers disagree with each other, or only one matches the key, or the adjudicator doubts the key. Goes to the human panel. |
| **Rejected** | Both readers independently reach the same contrary finding with anchors. The key is revised with a recorded rationale or the packet is dropped. |
| **Invalid read** | Refusal, truncation, or a reader that saw anything beyond prompt and body. It stays in the denominator. One re-dispatch is allowed only for transport failure (empty or cut-off output), never for content. |

Matched pairs (R01/R08, R03/R19, S0/S1 and each H/N/U triad) are compared only after every reading in the pair is saved. The question is whether the conserved commitment drew the same scrutiny and whether a changed undertaking explains a changed finding.

A retained candidate is still a candidate. Model agreement licenses nothing. Gating use needs the reliability ladder in the [roadmap](../../../ROADMAP.md) and the human panel, as both decks already say.

## Output

One results file in this directory: the 31 × 2 rubric tables, the adjudications and a count of retained / disputed / rejected / invalid per deck. Raw outputs sit next to it. All material is invented and public-repo safe.

## Open for the owner

1. Is the roster right (Claude + GPT readers, separate adjudicator, owner as panel)?
2. Is the decision rule right, in particular "both readers must match" for retained?
3. Freeze as written, or with edits?
