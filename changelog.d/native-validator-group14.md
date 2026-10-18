### Native validator orchestration

The Python dispatcher now owns gate routes, aggregate self-tests and the full
canonical workflow. POSIX shell entrypoints are compatibility launchers.
`validate.py` dispatches every command through one `ROUTES` table; the runner
inventory and schema-coverage read that table by importing the dispatcher.

Package generation excludes Python caches and checks actual archived native
payloads. The single validate job proposes Windows qualification with explicit
UTF-8, immediate native exit checks, and a bounded hosted Bash-absence and
restoration protocol. This is an unarmed draft: combined qualification/review and
an authorized actual hosted full No-Bash receipt remain required for acceptance.
