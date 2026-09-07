# Withdrawal and retention candidates

Four original synthetic families test whether an editor withdraws a specific
criticism when relevant textual evidence changes, while retaining that criticism
after an irrelevant edit. Each family has baseline, relevant, and irrelevant texts.
These are development candidates, not registered or human-licensed ground truth.

The initial screen is complete. A fresh Astra-high context diagnosed each baseline;
mechanical severity/order selection chose one finding per story. Independent
Codex5.5-high review accepted all four selected findings as grounded, relevant,
and appropriately severe. **No followup has run**, so withdrawal/retention behavior
has not been measured. Work paused at the owner's requested session boundary.

See [PROTOCOL.md](PROTOCOL.md) for the frozen design, [mutations.json](mutations.json)
for exact independently proposed replacements and superseded controls, and
[CONSTRUCTION-SUMMARY.json](CONSTRUCTION-SUMMARY.json) for machine accounting and
whole-artifact identities. Raw model outputs, selected findings, eligibility
records and machine-local commands remain in ignored results.

| Family | Intended logical distinction | Relevant/control token edit distances |
|---|---|---|
| reference-clocks | Clock-reference relation changes arrival time | 9 / 6 |
| object-identity | A replica separates two object referents | 5 / 6 |
| epistemic-authority | Limited belief differs from narrator assertion | 13 / 10 |
| quantifier-scope | Before-eleven absence differs from all-day absence | 3 / 3 |

Each intervention replaces exactly one sentence. Extent is approximately matched,
not equal. The texts use conspicuous explicit constraints and anti-escape clauses;
they do not establish naturalistic fiction validity. Independent model agreement
is advisory, and one initial call per family does not establish reliability.

## Resume contract

Preserve the frozen initial sources, prompts, schemas and selected findings. The
independent eligibility record is already sealed before any followup dispatch.
For each eligible finding, create three fresh-context packets containing that
finding unchanged and exactly one current text: baseline, relevant, or irrelevant.
Randomize opaque row IDs and never expose variant labels or sibling packets.
Use the same frozen common followup prompt and model/effort settings. Account for
all twelve cells, failures and disagreements. Do not substitute findings or retry
answer quality. Independently inspect the retained evidence before reporting an
intended retain/withdraw/retain pattern; do not promote candidates automatically.

The machine-local handoff retains exact freeze and runner commands. No production
plugin, registered fixture, benchmark key or other candidate package changes here.
