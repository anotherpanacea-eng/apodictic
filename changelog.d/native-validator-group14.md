### Native validator orchestration

The Python dispatcher now owns gate routes, aggregate self-tests and the full
canonical workflow. POSIX shell entrypoints are compatibility launchers.
`validate.py` dispatches every command through one `ROUTES` table; the runner
inventory and schema-coverage read that table by importing the dispatcher.

CI keeps the Ubuntu `validate` job and adds a `validate-windows` job that runs
`python plugins/apodictic/scripts/validate.py --check-all` with only Python on
`PATH`; the train receipt verifier now expects both jobs. A static test keeps
shipped Python from launching Bash or `sh`.

Two output changes: per-command usage messages from a direct
`python validate.py <command>` launch now name `validate.py` (the `validate.sh`
shims still print their own path), and `state-lines` prints its count without
the left padding BSD/macOS `wc -l` added under Bash.
