# Rhetorical purpose: blind-screen execution brief

Status: **frozen by the owner on 2026-10-09** (burndown decision sheet, round 14: roster as drafted; freeze, and Claude may run it). No readings have run yet. Both candidate decks require the design to be frozen before any blind reading: roster, prompt, rubric, thresholds and provenance, with human adjudication of contested readings ([first increment](../rhetorical-purpose-first-increment/PROTOCOL.md), [constitutive controls](../rhetorical-purpose-constitutive-controls/README.md)). This brief supplies them. Running it is a separate, owner-authorized step.

## Packets and reads

| Deck | Packets | Prompt and rubric |
|---|---|---|
| First increment | R01–R20, S0, S1 (22) | That deck's PROTOCOL: common neutral prompt and seven-dimension table |
| Constitutive controls | H01–H03, N01–N03, U01–U03 (9) | That deck's PROTOCOL prompt; the six-dimension table below |

31 packets, two readers each: 62 reads. Both prompts are used verbatim.

The constitutive PROTOCOL names its six dimensions but gives no statuses. This brief adds them, reusing the first-increment vocabulary:

| Dimension | Record |
|---|---|
| Source-grounding | Evidenced / contradicted / unresolved, anchor and explanation |
| Purpose fit | Evidenced / contradicted / unresolved, counter-reading |
| Retained commitments | Covered / missed / uncertain, commitment named |
| False-positive avoidance | Present / absent / uncertain, demand named |
| Normative transparency | Declared / undeclared / uncertain, basis named |
| Repair usefulness | Supported / unsupported / uncertain; no replacement prose |

## Roster and provenance

- **Reader A:** `claude-opus-5-5`.
- **Reader B:** `gpt-6.1-sol/high` through Codex.
- **Adjudicator:** a third fresh context, not the session that dispatched the reads.
- **Screen panel:** the owner. It decides screen disputes only; it is not the reliability-ladder panel.

Each reader gets exactly the deck's prompt followed by one INPUT body, in a fresh context per packet. The call has no tools and no file or repository access: an API call without tools, or a CLI session started with tools off in an empty directory outside the repository. Readers never see each other's output; that, not the different model families, is what makes the reads independent. Each read records the model ID, access path and date.

## Recording

Save each raw output unedited. The adjudicator then fills the deck's rubric table for each reading (status, anchor, one-line reason per dimension, no scalar total) **before** opening `expected.md`.

## Decision rule per packet

After filling the tables, the adjudicator compares each reading with the packet's key on two lines: the finding line (**Proposed defect/repair**; **Proposed behavior** for R12, R13, R15, R16 and R18; **Proposed repair class** for H01–U03) and **Prohibited outputs**.

| Outcome | When |
|---|---|
| **Retained candidate** | Both readings reach the key's finding (or its absence of a finding) with an anchor, neither produces a prohibited output, and the adjudicator agrees. |
| **Disputed** | Every other packet, including: the readers disagree; only one matches; a reading produces a prohibited output; both readers reach the same contrary finding; the adjudicator doubts the key or the match; any read is invalid. Goes to the screen panel. |
| **Rejected** | Only the screen panel rejects. If it rules the key wrong, it records the rationale and either revises the key (the packet stays a candidate) or drops the packet. |

A read is **invalid** if it is a refusal, truncated or empty, or if the reader saw anything beyond prompt and body. Invalid reads are listed and stay in the denominator. There is no re-dispatch.

Matched pairs are compared only after every reading in the pair is saved: R01/R08, R03/R19, R09/R20, S0/S1, S1 with R05/R06, and each H/N/U triad. The question is whether the conserved commitment drew the same scrutiny and whether a changed undertaking explains a changed finding.

A retained candidate is still a candidate. Model agreement licenses nothing; gating use needs the reliability ladder in the [roadmap](../../../ROADMAP.md), as both decks say.

## Output

One results file in this directory: the 62 rubric tables, the adjudications and, per deck, a count of retained / disputed / rejected / invalid. Counts are reported, not compared with any cutoff; there is no deck-level pass threshold. Raw outputs sit next to it. All material is invented and public-repo safe.
