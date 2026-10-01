# Canonical audit skill families

**Status:** Built; independent review and consumer admission required before release.

The focused-audit catalog is now a dispatcher. Narrative craft, genre/reader
expectations, argument analysis, research/verification and prose/structural
measurements each own their protocols. This is a canonical Claude-plugin change
in `plugins/apodictic/`; generated hosts copy the same source. It is independent
of the OpenAI submission work in PR #280.

## Contract

| Owner | Responsibility |
| --- | --- |
| `narrative-craft-audits` | Stakes, decisions, scenes, character/emotion/interiority, literary craft, compression, short fiction and series structure |
| `genre-reader-audits` | Genre/tag craft, memoir/narrative nonfiction, positioning, reception, reader personas and content advisories |
| `argument-audits` | Dialectical clarity, red team, persuasion, evidence, adversarial evidence and AGD adjudication |
| `research-verification` | Six internet research protocols and scholarly API/caching/provenance/reliability helpers |
| `prose-measurements` | AI-prose/structural calibration and colocated SETEC helpers, including the optional AGD scan |

`specialized-audits` retains discovery and `/audit` dispatch. `/research` loads
research-verification directly. Existing command aliases, registry card IDs,
activation tiers, diagnostic codes, calibration warnings, manuscript-preservation
and output/severity contracts are retained. Shared execution rules live in
`core-editor/references/focused-audit-contract.md`; activation/propagation tables
remain authoritative. Family membership grants no tool permission.

The root `release-registry.json` adds `auditFamilies` and
`auditReferenceAliases`. Legacy `categories[].items[].files`, research and
companion paths remain stable identifiers. `scripts/release-generate.mjs`
validates ownership and generates the shipped
`skills/specialized-audits/catalog.json` from those fields. Aliases are direct,
unique mappings from historical skills-root paths to actual owner paths;
they never duplicate protocol bodies. New resources need a migration identifier.
The SETEC client moves byte-for-byte with its importing helpers; its lock and
external fixtures remain unchanged. Sync/drift tools use the new location.

## Consumer sequencing

1. Admit Gemini's backward-compatible catalog consumer before publishing a
   producer release with this layout. Old plugins without a catalog remain
   supported; malformed or missing split-layout catalogs fail visibly.
2. Land and release the producer through its normal reviewed train. Gemini's
   `scripts/sync-plugin.mjs` mirrors the whole plugin and matching registry from
   that release; regenerate its UI. Do not manually repin its lock or vendor files.
3. Gemini's runtime resolves legacy paths and preserves saved specialized pass
   IDs. Its UI resolves the same aliases before fetching resources.
4. Release Gemini's complete desktop payload. Tauri's existing
   `scripts/sync-gemini-web.mjs` transports and hashes the whole plugin tree,
   including all new family directories. No editorial logic belongs in Tauri,
   and its lock advances only through the established payload-sync flow.

These drafts do not merge, tag, repin, deploy, publish or upload anything to the
OpenAI submission portal. Claude should review ownership, cross-family links,
legacy session compatibility and the consumer-first release sequence.

## Verification

Run the combined validator and release/inventory/status gates; both host builds;
catalog safety/ownership regressions; scholarly helper self-tests; SETEC offline
drift and contract tests; and Python compilation. Consumer tests cover old/split
layouts, canonical and legacy IDs, saved sessions and unsafe aliases. Use only
synthetic or shipped public fixtures. Structural checks do not establish model
routing quality or portal approval.
