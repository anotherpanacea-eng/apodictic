### Fixes — macOS local checks

`/adjudicate` and `/reconstruct` no longer refuse a project whose path passes through a host-level symlink (macOS `/var` → `/private/var`, a symlinked home folder). Links inside the project, and a project folder that is itself a link, are still refused. Three test files no longer use `write_text(newline=...)`, and the link check no longer uses `Path.stat(follow_symlinks=...)`. Both need Python 3.10, so the suite now runs on macOS system Python 3.9.
