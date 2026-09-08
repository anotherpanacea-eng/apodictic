# Withdrawal and retention candidates

Four original synthetic families test whether an editor withdraws a specific
criticism when relevant textual evidence changes, while retaining that criticism
after an irrelevant edit. Each family has baseline, relevant, and irrelevant texts.
These are development candidates, not registered or human-licensed ground truth.

The candidate experiment is complete: four initial diagnoses, four independent
eligibility decisions, and twelve fresh-context followups are sealed. All four
families retained the criticism on baseline and irrelevant-control text and
withdrew it on the relevant counterfactual. All twelve followups passed exact-quote
checks; independent Codex 5.5-high review found the explanations supported that
pattern. See [RESULTS.md](RESULTS.md) for the bounded conclusion and limitations.

The tested behavior already worked in these explicit probes. This experiment
justifies no production prompt or runtime change and does not promote candidates
to registered ground truth.

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

## Custody and future use

The initial selection and independent eligibility decisions were sealed before
followup dispatch. Each followup received that finding unchanged and exactly one
current text. Opaque IDs and fresh contexts kept variant labels, sibling packets
and adjudicator notes out of model inputs. No answer-quality retries were made.

Keep all original candidates and outcomes as exposed development evidence.
Naturalistic transfer or reliability claims require new untouched families and
prospective acceptance rules. Human or otherwise licensed acceptance is still
required for any groundtruth promotion. No production plugin, registered fixture,
benchmark key or other candidate package changes here.
