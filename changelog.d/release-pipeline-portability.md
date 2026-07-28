### Release safety and portability

- Build Codex and Antigravity ZIP assets with a fail-closed, stdlib-only Node packager instead of requiring external Unix `zip` and `unzip` binaries.
- Force validator-launched Python processes to emit UTF-8, keeping hostile-output assertions and release verification deterministic on Windows consoles.
- Preflight both host package builders before mutating release files; the staging pipeline never creates tags, refuses when Git state cannot be inspected, and the separate owner-only tag helper only cuts from a clean `main` at freshly fetched `origin/main`.
