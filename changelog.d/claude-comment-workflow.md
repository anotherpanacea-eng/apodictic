### CI: comment-triggered `@claude` workflow

Add `.github/workflows/claude.yml`: a comment, review, or new issue that mentions
`@claude` from a repository owner, member, or collaborator starts one
claude-code-action run. Pull requests from forks are refused before checkout,
both actions are pinned to commit SHAs, and the workflow's own `GITHUB_TOKEN`
stays read-only apart from `id-token: write`. The policy suite admits the new
file to the closed workflow set and guards those safety boundaries.
