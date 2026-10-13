### Native Python letter signal validators

Added native dispatcher routes for author-facing lint, severity floors, audit
signal propagation and registry checks, underdiagnosis triggers, ledger
consolidation and decision-layer checks. Existing letter parsers retain ownership
of optional inputs, errors and advisory behavior. Differential checks cover every
added self-test, all 42 applicable shipped fixtures and registry/default argument
cases. Aggregate checks and the remaining commands still use `validate.sh`.
