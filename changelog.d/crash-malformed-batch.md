### Infrastructure — Crash-resistance for malformed block payloads (the non-P1 sweep batch)

Follow-up to the validator-fleet hardening: the 2026-06-20 sweep's recurring **crash-on-malformed** class — a `parse_*`/check path reaching `obj.get()` (or `.lower()`, or char-iterating a string) on a *valid-but-non-dict* JSON block payload (`[1,2,3]`, `"str"`, `42`, `null`-comment) and raising an **uncaught traceback** — is closed across the eight remaining (non-P1) sites the sweep confirmed (the four P1 sites were fixed earlier):

- **viz_manifest** (`manuscript-viz`) — a non-object manifest block now reports a controlled **E1** failure instead of crashing in `check()` (and never passes vacuously).
- **annotation_manifest** (`annotated-manuscript`) — same, a non-object manifest block → controlled **A1** failure.
- **crosslink** — `_anchor_str` tolerates a non-dict `anchor` (covers the X2 back-link path).
- **reanchor** — `reclassify` guards a non-dict annotation / non-dict anchor.
- **registry_check** — a non-object project sidecar is treated as unparseable drift (R3), not a crash.
- **annotation_export** (`obsidian-export`) — the footnote-definition sort filters non-dict entries **before** sorting, and the O3 comparison tolerates a `null` comment.
- **editor_scaffolding** — `_read` tolerates non-UTF-8 bytes (clean "cannot read" / exit 2, not a `UnicodeDecodeError` traceback).
- **regression_diff** — `_mech_tokens` coerces a non-string mechanism before `.lower()`, and `_chapter_of` guards a non-list `evidence_refs` (which was silently char-iterated, demoting a `new-in-quiet-chapter` W2 candidate to a plain `new` with no warning — a silent-loss bug, not just a crash).

Each fix mirrors `apodictic_artifacts.validate_obj`'s own `isinstance(obj, dict)` guard, applied identically to both byte-identical script copies. Reproduced no-crash for all eight; locked with direct-unit regression self-tests for `reanchor`, `regression-diff`, `crosslink`, and `manuscript-viz` (the others are reproduction-verified — crash-resistance is not statically gateable by the `validator-conventions` M1–M4 checks).

A **second, distinct crash class** in the same sweep: a malformed **finding_id** (or ledger id) used as a dict KEY or a SORT key — a non-hashable id (a JSON list/object kept as-is by `parse_*`) raises `unhashable type`, and a mixed `int`/`str` id set raises `sorted()`'s `'<' not supported between instances`. The four P1-era sites (the annotation A1 uniqueness map) were fixed earlier; this batch closes the remaining sibling sites and **centralizes one normalizer — `apodictic_artifacts.fid_key`** (the lowest shared lib, so `finding_trace`/`annotation_*`/`reanchor` all route through it without a circular import; a valid string id is unchanged, a malformed id is `str()`-coerced — matching the `"[^%s]"`-rendered footnote ref so the multiset/provenance join still ties):

- **reanchor** — `_fid` normalizes the `finding_id` at `build_reanchored` (re-anchor map + re-annotation), the orig-comment lookup, and the comment-fidelity check.
- **annotation_manifest** — the A1 uniqueness `seen` map, the comment-provenance `led_obj` lookups, the `manifest_ids` set, and the **ledger-side** index `led_obj[o["id"]]` (a malformed *ledger* finding id) all coerce through `fid_key` (an `art`-None-safe local mirror, since its `apodictic_artifacts` import is best-effort).
- **annotation_export** — both `build_obsidian` sorts (the offset/fid ref sort + the definition-block sort) and the `check_obsidian` O2 `manifest_set` + O3 `comment_of` dict keys.
- **finding_trace** — `ledger_inventory`'s `inv[obj["id"]]` (the authoritative-ID-set index).

`regression_diff` already self-handled non-string ids (it skips them). Locked with non-hashable + mixed-type id regression self-tests (a list/mixed manifest `finding_id` AND a non-hashable ledger id), each raising against the pre-fix code.
