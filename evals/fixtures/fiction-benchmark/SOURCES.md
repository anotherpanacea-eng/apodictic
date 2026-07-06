# Fiction Benchmark — Source Manifest (metadata only)

The fetch/pin list for the fiction slice. **No copyrighted or base bytes live in
this repo.** This file records, per source: the provenance tier, the retrieval
URL (public-domain Gutenberg only), the body-carve anchors, and — recorded **on
first retrieval by the preparer** — the SHA-256 of the extracted/derived text.
`run.sh --fetch` reconstitutes the *referenced* sources from their pinned URLs
and verifies the recorded hash.

Discipline (mirrors the argument benchmark's SOURCES.md):

- The preparer reads **only this file** (URL + anchors + hash), never any
  `groundtruth.md`, derives the text, records the hash in that source's
  `RECORDED:` line, and hands only the extracted/mutated text to the blind
  runner.
- **Recorded hashes are blank until first retrieval** — a SHA-256 is written the
  first time the preparer derives the text on their machine. A blank `RECORDED:`
  is expected in-repo; it is not a defect.
- The Gutenberg book IDs below are marked *verify at pin time* — confirm the ID
  resolves to the named text before recording the hash (IDs occasionally shift).

Derived-broken fixtures are **not** fetched from a URL: they are produced from
their bucket's clean base by applying the mutation registry in the broken
member's `groundtruth.md §Base text + plant record`. The preparer applies the
recorded edits, records the resulting hash here, and the mutation stays out of
this metadata file (it lives only in the never-run `groundtruth.md`).

---

## Referenced public-domain sources (fetched by `run.sh --fetch`)

### christmas-carol-arc-control
- **Provenance tier:** 2 public-domain (referenced — novella length, not stored)
- **Text:** Charles Dickens, *A Christmas Carol* (1843)
- **URL:** https://www.gutenberg.org/cache/epub/46/pg46.txt  *(Gutenberg #46 — verify at pin time)*
- **BODY_START:** `MARLEY was dead: to begin with.`
- **BODY_END:** `*** END OF THE PROJECT GUTENBERG EBOOK A CHRISTMAS CAROL ***`
- **RECORDED:** _(sha256: pending first retrieval)_

---

## Stored public-domain bases (preparer derives `fixture.md` locally; short, PD)

These are short enough to store, but to keep pre-pinned base bytes out of the
repo the preparer derives each `fixture.md` at pin time from the URL below and
records the hash here. The clean-member text is the carved body verbatim; the
broken-member text is that body with the mutation registry applied.

### yellow-wallpaper-voice-control
- **Provenance tier:** 2 public-domain (stored after pin)
- **Text:** Charlotte Perkins Gilman, *The Yellow Wallpaper* (1892, ~6k words)
- **URL:** https://www.gutenberg.org/cache/epub/1952/pg1952.txt  *(Gutenberg #1952 — verify at pin time)*
- **BODY_START:** `It is very seldom that mere ordinary people`
- **BODY_END:** `*** END OF THE PROJECT GUTENBERG EBOOK THE YELLOW WALLPAPER ***`
- **RECORDED:** _(sha256: pending first retrieval)_

### gift-of-magi-reveal-control
- **Provenance tier:** 2 public-domain (stored after pin)
- **Text:** O. Henry, *The Gift of the Magi* (1905, ~2.1k words; in *The Four Million*)
- **URL:** https://www.gutenberg.org/cache/epub/2776/pg2776.txt  *(Gutenberg #2776 — The Four Million; verify at pin time, carve the single story)*
- **BODY_START:** `One dollar and eighty-seven cents.`
- **BODY_END:** `And here I have lamely related to you`
- **RECORDED:** _(sha256: pending first retrieval)_

---

## Derived-broken bases (low-recognition PD; final pick made at build/pin time)

The four matched pairs draw their base from low-recognition public-domain short
fiction (a lesser-known Gutenberg short story — e.g. Mary E. Wilkins Freeman,
W. W. Jacobs). The **final base pick is made at pin time** and recorded here by
the preparer, subject to a recognition probe (prefer MODERATE→LOW recognition).
Each pair's clean member is the carved base verbatim; the broken member applies
that pair's `groundtruth.md` mutation registry. Record BOTH hashes (clean and
broken) once the base is pinned.

### pov-break-clean / pov-break-broken
- **Provenance tier:** 1 synthetic-or-derived
- **Base:** low-recognition PD short story, established third-limited *(pin at build)*
- **URL:** _(recorded at pin time)_
- **BODY_START / BODY_END:** _(recorded at pin time)_
- **RECORDED (clean):** _(sha256: pending)_ · **RECORDED (broken):** _(sha256: pending)_

### continuity-contradiction-clean / continuity-contradiction-broken
- **Provenance tier:** 1 synthetic-or-derived
- **Base:** low-recognition PD base with two entity-fact statements + a datable event *(pin at build)*
- **URL:** _(recorded at pin time)_
- **BODY_START / BODY_END:** _(recorded at pin time)_
- **RECORDED (clean):** _(sha256: pending)_ · **RECORDED (broken):** _(sha256: pending)_

### unpaid-setup-clean / unpaid-setup-broken
- **Provenance tier:** 1 synthetic-or-derived
- **Base:** low-recognition PD base with an emphatic early object/plant + a later payoff scene *(pin at build)*
- **URL:** _(recorded at pin time)_
- **BODY_START / BODY_END:** _(recorded at pin time)_
- **RECORDED (clean):** _(sha256: pending)_ · **RECORDED (broken):** _(sha256: pending)_

### orphan-scene-clean / orphan-scene-broken
- **Provenance tier:** 1 synthetic-or-derived
- **Base:** low-recognition PD base with a clean causal chain *(pin at build)*
- **URL:** _(recorded at pin time)_
- **BODY_START / BODY_END:** _(recorded at pin time)_
- **RECORDED (clean):** _(sha256: pending)_ · **RECORDED (broken):** _(sha256: pending)_
