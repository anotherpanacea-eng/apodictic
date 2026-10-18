### Native validator orchestration

The Python dispatcher now owns gate routes, aggregate self-tests and the full
canonical workflow. POSIX shell entrypoints are compatibility launchers.
`validate.py` dispatches every command through one `ROUTES` table; the runner
inventory and schema-coverage read that table by importing the dispatcher.

CI keeps the Ubuntu `validate` job and adds a `validate-windows` job that runs
`python plugins/apodictic/scripts/validate.py --check-all` with only Python on
`PATH`; the train receipt verifier now expects both jobs.

Two output changes: per-command usage messages now name `validate.py`, including
through the `validate.sh` shims, and `state-lines` prints its count without the
left padding BSD/macOS `wc -l` added under Bash.

Two Bash-era leftovers are gone. `override_marker.py` no longer has the
`--has-override` / `--override-slugs` stdin CLI that only the Bash dispatcher
called; its own `--self-test` covers the same cases. The `--internal-links`
refusal now applies to the four annotation export routes only, instead of to every
route that happened to live in `commands-b.sh`.
