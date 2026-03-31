# Codex Parity Notes

This file tracks the remaining differences between the original APODICTIC
plugin design and this Codex-specific packaging.

## Fixed for this Codex build

- User-facing runtime docs no longer describe Claude Opus as the required host.
- The Codex manifest is the primary manifest for this build.
- Legacy workflows now exist as namespaced Codex compatibility wrapper skills.

## Known non-parity moments

1. No native slash-command runtime.
   The `commands/` directory remains the compatibility source of truth, but
   Codex consumes APODICTIC through skill selection and plain-language routing,
   not a true slash-command engine.

2. Diagnostic/execution mode is soft-enforced.
   APODICTIC's firewall and handoff protocol depend on instruction adherence and
   `Diagnostic_State.md`, not on a product-level runtime boundary.

3. Historical reference files still mention model lineage.
   Many reference docs include provenance such as Opus/Codex/Gemini synthesis
   notes. These are historical annotations, not live runtime requirements.

4. The source tree still contains the legacy Claude manifest.
   `plugins/apodictic/.claude-plugin/` remains in the working copy for source
   provenance, but it is excluded from the Codex package archive.

5. Local testing is static rather than in-app.
   The package test pass validates manifests, wrapper coverage, archive
   contents, and high-level assumption cleanup. It does not execute an actual
   Codex install flow from the terminal.
