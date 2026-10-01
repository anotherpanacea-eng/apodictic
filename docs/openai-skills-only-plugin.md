# Skills-only OpenAI plugin

APODICTIC's OpenAI directory package reuses the generated Codex skills and
namespaced command wrappers. Editorial reasoning runs in the user's host model;
bundled helpers supply checks and exports where the host can execute them.
There is no MCP server, hosted manuscript store, or author-operated backend.

## Build

From the repository root with Node.js 22:

```bash
node scripts/build-codex.mjs
node scripts/build-codex.mjs --self-check
```

The build produces two different archives:

| Archive | Purpose |
| --- | --- |
| `dist/apodictic-codex-marketplace.zip` | Local workspace marketplace installation; unzip and open `codex/`. |
| `dist/apodictic-openai-plugin.zip` | Upload a single plugin to the OpenAI submission portal. |

The submission archive has `.codex-plugin/plugin.json`, `skills/`, `commands/`,
`scripts/`, `schemas/`, assets, README, LICENSE and PRIVACY.md directly at its
root. Wrapper skills retain their relative references to the command files and
base skills. It excludes the Claude manifest. The generated onboarding skill is
`skills/apodictic-start/SKILL.md`. Do not edit generated files: change canonical
`plugins/`, the authored `packaging/codex/` overrides, or the generator.

`--self-check` builds both archives in a temporary directory, checks the
generated workspace, submission listing text limits, referenced files, root
layout, executable modes and absence of MCP/app/hook wiring, then removes the
temporary output. These checks do not prove in-app installation or editorial
quality. Tagged releases publish both ZIPs as GitHub assets; they do not submit
or publish a plugin in the OpenAI directory.

## Submit and test

Use the current [OpenAI submission guide](https://developers.openai.com/plugins/deploy/submission).
The publisher needs an eligible organization/project role and a verified
developer identity. Upload `apodictic-openai-plugin.zip`, resolve metadata and
skill scan findings, and complete the applicable review. Skills-only plugins
do not require MCP connection setup, MCP review test cases or an MCP demo.
Public approval and publication are separate steps; this build performs neither.

The listing's `interface.privacyPolicyURL` points to a publicly accessible GitHub
commit permalink for the host-neutral policy included in this package. Update
that pinned URL when the policy changes, and verify that anonymous visitors can
read the policy and that its content matches the bundled `PRIVACY.md`.

The package selects `Creativity` because its main task is developmental
editing of manuscripts and arguments. This is a supported category in the
[OpenAI submission reference](https://developers.openai.com/plugins/deploy/submission-errors#listing-and-interface-errors).
The listing name, subtitle, capabilities and starter prompts describe that
task. Rerun the portal scan after uploading the revised package; local
validation does not establish that a category finding has cleared.

Before claiming host compatibility, install in a clean target host and exercise:

1. Plain-language intake and `apodictic-start` with a short synthetic fiction draft.
2. An argument-shaped draft that routes to the Nonfiction Argument Engine.
3. A focused audit and revision coaching that preserve the no-rewrite firewall.
4. Saved-project resume if persistent workspace files are available.
5. Actual validation and annotated export if shell/Python execution is available.

Use synthetic or public-domain material for review. Confirm skill reference
resolution after installation, not just in the source checkout. Local static
validation cannot establish that ChatGPT exposes the same file, web, execution,
or delegation facilities as Codex.

## Host-dependent behavior

- Mechanical validation requires execution of the bundled scripts. On a host
  without shell execution, follow the existing inline protocols and label their
  provenance honestly; an inline check is not a mechanically executed check.
- Annotated exports and author adjudication need their Python helpers and file
  access. Approval-ledger writes must go through the existing engine; never
  replace them with manual JSON or Markdown edits.
- Saved projects require persistent file storage. The plugin does not provide
  cross-device synchronization or its own storage service.
- Independent pass agents require host delegation. Installation does not add
  that capability or the deferred external orchestrator.
- Citation research requires network tools or executable scholarly lookup
  helpers. SETEC measurements require a separate compatible SETEC installation;
  unavailable measurements must be disclosed rather than invented.

Your host provider handles supplied manuscript content and workspace storage
under its own terms. See [PRIVACY.md](../PRIVACY.md). No manuscript data goes to
the plugin author as part of this package.
