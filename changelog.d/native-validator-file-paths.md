### Native validator utility file paths

On Windows, early validator utilities now reject regular-file arguments ending
in `/.` or `\.` with the existing file-not-found diagnostic and status 2,
matching Bash preflight. Directory arguments and ordinary file inputs retain
their existing handling.
