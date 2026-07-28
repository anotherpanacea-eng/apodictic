### SETEC contract safety

- Gate the vendored `voice_distance` fixture on SETEC's `register_families/v2` register-family contract: both taxonomy markers, a `strength` drawn from the closed `strong`/`moderate`/`weak`/`mismatch` vocabulary, and no legacy `verdict`. The check is unconditional, so a sync that re-vendored a pre-v2 fixture fails rather than passing on a grandfather clause. Rejection cases run against a hand-built payload, never the vendored golden — a negative arm fed by a producer artifact goes vacuous the moment that artifact legitimately changes.
