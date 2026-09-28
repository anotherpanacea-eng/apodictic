### One copy of the validators

The root `scripts/` mirror of `validate.sh`, `validate.d/`, `preflight.sh`,
and every Python validator is gone; root `scripts/validate.sh` is now a
one-line shim that execs `plugins/apodictic/scripts/validate.sh`, so CI runs
the shipped code. `check-mirror` is removed (83 validators). The approval
session test and the two eval scripts that imported root copies now import
the plugin copies. AGENTS.md and CLAUDE.md describe the single-copy layout.
