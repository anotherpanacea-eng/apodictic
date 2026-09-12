### Repo maintenance — pre-rewrite branch archive

Record that `main`'s history was rebuilt around 2026-07-06 and that nineteen
branches descend from the original root with no common ancestor, so they can
never enter a merge train while holding the only copy of 795 pre-rewrite
commits. Add a fail-closed tool that tags that lineage, confirms the tags
reached the remote, and only then prunes four provably dead branches.
