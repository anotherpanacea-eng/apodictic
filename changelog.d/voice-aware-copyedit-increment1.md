### Workflows — Voice-Aware Copyedit (Increment 1)

New `/copyedit` command and core-editor module: a style sheet, a voice ledger of the author's
deliberate departures, and a pass that raises queries only (no replacement text; nothing applied to
the manuscript). `scripts/copyedit.py harvest` inventories competing forms (compounds,
mid-sentence capitalization, -ise/-ize, -our/-or) with counts and paragraphs. The new `copyedit`
validator checks `apodictic.copyedit_item.v1` queries and `apodictic.voice_ledger.v1` entries: E1
schema and ids, E2 UTF-8 byte provenance against the snapshot, E3 the ledger guard (a form the
author settled in an enforceable scope is never re-raised; inferred and speaker/zone entries must be
named), and best-effort W1 never-flag reasons. Canonical fixture `example-copyedit/` runs under
`--check-all --strict`.

Review fixes preserve raw byte offsets and paragraph/chapter boundaries with CRLF, whitespace-only
blank lines and UTF-8 BOM snapshots; keep exact capitalization counts in the harvest; reject
replacement fields inside instances; and require possible-voice labels on marked quotations.
