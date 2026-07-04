### Validators — Architecture Hardening (Increment 8)

Ported the last four bash-regex prose/filename validators onto the shared
parsers, completing the editorial-letter / ledger family. `ledger-check`,
`synthesis-sections`, and `tone-check` now run through `letter_checks.py`
(heading-anchored section matching that kills the mid-heading substring
false-positive; body-only, code-span-stripped, blockquote-skipped superlative
scanning so a superlative quoted in an appendix, a code fence, or an author
blurb no longer false-fails); `artifact-names` runs through `config_checks.py`
with the project/runlabel matched as literals. Each keeps its exact legacy
output contract (verified byte-identical against the pre-port arm) and its bash
implementation as the no-`python3` degrade path, and gains fixture-driven
negative tests.
