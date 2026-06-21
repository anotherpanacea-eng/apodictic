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
