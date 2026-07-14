# Fiction Benchmark — Source Manifest (metadata only)

The fetch/pin list for the fiction slice. **No copyrighted bytes live in this
repo.** Short public-domain and synthetic fixtures are stored after pinning;
the referenced Dickens novella remains external. This file records, per source:
the provenance tier, the retrieval
URL (public-domain Gutenberg only), the body-carve anchors, and — recorded **on
first retrieval by the preparer** — the SHA-256 of the extracted/derived text.
`run.sh --fetch` reconstitutes the *referenced* sources from their pinned URLs
and prints the derived hash. The preparer records that value here; subsequent
`--verify` and model-run modes enforce it.

Discipline (mirrors the argument benchmark's SOURCES.md):

- The preparer reads this file (URL + anchors + hash) and, for a broken member
  only, the mutation registry in that member's `groundtruth.md`. No other key
  material is used. The preparer derives the text, records its hash in that
  source's `RECORDED:` line, and hands only the text to the blind runner.
- A recorded hash is mandatory once a fixture is pinned. Blank `RECORDED:`
  fields are permitted only while designing a future, unregistered fixture.
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
- **BODY_START:** `STAVE I:  MARLEY'S GHOST`
- **BODY_END:** `*** END OF THE PROJECT GUTENBERG EBOOK A CHRISTMAS CAROL IN PROSE; BEING A GHOST STORY OF CHRISTMAS ***`
- **RECORDED:** sha256: 8963153e2cf14522823c6c85cc7be800c58fe8b8cb151ed98b09f48d58892114

---

## Stored public-domain bases (preparer derives `fixture.md` locally; short, PD)

These are short enough to store. The preparer derives each `fixture.md` at pin
time from the URL below and records the hash here.

### yellow-wallpaper-voice-control
- **Provenance tier:** 2 public-domain (stored after pin)
- **Text:** Charlotte Perkins Gilman, *The Yellow Wallpaper* (1892, ~6k words)
- **URL:** https://www.gutenberg.org/cache/epub/1952/pg1952.txt  *(Gutenberg #1952 — verify at pin time)*
- **BODY_START:** `It is very seldom that mere ordinary people`
- **BODY_END:** `*** END OF THE PROJECT GUTENBERG EBOOK THE YELLOW WALLPAPER ***`
- **RECORDED:** sha256: 4534cbc34da17443fd8fd2bccff70dffda20d036baf8f54765d5957721ddabe2

### gift-of-magi-reveal-control
- **Provenance tier:** 2 public-domain (stored after pin)
- **Text:** O. Henry, *The Gift of the Magi* (1905, ~2.1k words; in *The Four Million*)
- **URL:** https://www.gutenberg.org/cache/epub/2776/pg2776.txt  *(Gutenberg #2776 — The Four Million; verify at pin time, carve the single story)*
- **BODY_START:** `One dollar and eighty-seven cents.`
- **BODY_END:** `A COSMOPOLITE IN A CAFÉ`
- **RECORDED:** sha256: 2f1c963abe16e6341f7fb6640d3436636cbdddcf83f3835987ee4998df38ea1c

---

## Synthetic matched-pair bases (stored, pinned 2026-07-14)

The four matched pairs use original synthetic Tier-1 short works created for
this benchmark. This eliminates source recall while preserving the recognition
probe. Each clean member is the base work; its broken mate applies only the
registered mutation class. Each member has its own block because the runner's
manifest contract is one slug and one hash per block.

### pov-break-clean
- **Provenance tier:** 1 synthetic-or-derived (original synthetic)
- **Base:** Jonah Vale quarry story; established third-limited
- **RECORDED:** sha256: 55fe256d39a61fd31542e5d48bebf399ceb2cd6cfe0c0c3ea44c5d611e86dd6e

### pov-break-broken
- **Provenance tier:** 1 synthetic-or-derived (original synthetic)
- **Base:** `pov-break-clean` plus the registered POV mutations
- **RECORDED:** sha256: 49e860f4185c0cad797f79d4721b36f602709f0585ceecde07187691e995d6d1

### continuity-contradiction-clean
- **Provenance tier:** 1 synthetic-or-derived (original synthetic)
- **Base:** Miriam Aster / Bellweather orchard story
- **RECORDED:** sha256: 52c7c419e909a8f9eaaa197806499f1ba44c6ac695170a692aedd53e89386ccf

### continuity-contradiction-broken
- **Provenance tier:** 1 synthetic-or-derived (original synthetic)
- **Base:** `continuity-contradiction-clean` plus the registered fact and timeline mutations
- **RECORDED:** sha256: 9afe4550f3c2e75fec78cc6f2cb404d591dfec93baa1b3df8f0bae6b44372ee8

### unpaid-setup-clean
- **Provenance tier:** 1 synthetic-or-derived (original synthetic)
- **Base:** Elin Ward / Saint Brannoc schoolhouse story
- **RECORDED:** sha256: 0cd49ea857b2612f9bbf78f4654fee7641f454822594ee45aead6f414f9985fe

### unpaid-setup-broken
- **Provenance tier:** 1 synthetic-or-derived (original synthetic)
- **Base:** `unpaid-setup-clean` with the registered payoff scene excised
- **RECORDED:** sha256: 09d8e1e6b38cff6af8a65fb945635066e87ae898329b6ccebf3fb2b0ed22131e

### orphan-scene-clean
- **Provenance tier:** 1 synthetic-or-derived (original synthetic)
- **Base:** Nessa Rook bridge-clock story
- **RECORDED:** sha256: a0189d6ce339cb1a9cb5b0d68c4b350e85610fa532d52828e57ac2b86cec0531

### orphan-scene-broken
- **Provenance tier:** 1 synthetic-or-derived (original synthetic)
- **Base:** `orphan-scene-clean` plus the registered causally inert scene
- **RECORDED:** sha256: 069a33f0b8787d0d90fd50ec6867a9230eee322cc4d1718352d6f3e52b5033f7
