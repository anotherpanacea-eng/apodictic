### Annotated-Manuscript Export — PDF Proofing Target (`pdf-export`, P1–P3)

Added a **4th projection** of the gated annotation manifest beside the shipped Obsidian / HTML / DOCX
targets: a self-contained, **byte-deterministic `.pdf`** (`scripts/annotation_export.py pdf`) the writer
opens in any PDF reader — the proofing/annotation deliverable. Written **by hand from raw PDF objects,
stdlib only** (no reportlab/fpdf): a `%PDF-1.4` header, numbered `/Catalog` → `/Pages` → per-page
`/Page` + uncompressed `/Contents` objects, a base-14 `/Helvetica` `/WinAnsiEncoding` font, an `xref`
table, and a trailer. The snapshot prose renders as text with a `[<finding_id>]` marker spliced at each
anchor locus (the HTML `<sup>` precedent, via the same `_insertion_offset` splice) and each verbatim
comment lands in a trailing **Findings** section, char-wrapped so the chunks concatenate back exactly.

**Byte-determinism** (the DOCX discipline, for a different binary): **no `/Info` dict** (so no
`/CreationDate`/`/ModDate`), **no `/ID`** array, **no stream compression** (no zlib drift), all shown
text emitted as **octal-escaped ASCII** (`\247` → §, interpreted by `/WinAnsiEncoding`), fixed object
order, xref offsets from byte lengths — no wall clock, no random. Two renders are byte-identical.

New **`pdf-export`** validator gating the on-disk artifact: **P1** artifact integrity (on-disk == fresh
build byte-for-byte — the authoritative lock), **P2** text round-trip (manuscript runs, markers stripped,
reproduce the snapshot), **P3** marker resolution + comment fidelity (markers ↔ manifest set bijection;
each Findings chunk group concatenates to the verbatim comment). Ships the canonical
`example-annotated-manuscript/pdf/` fixture wired into `--check-all` (byte-identical to a fresh render;
`*.pdf binary` added to `.gitattributes`), a `--self-test` with a hostile `( ) \ §` escape/offset case,
and the degrade-to-`WARN`-without-python3 arm. **Validators +1 → 68** (the count stays DERIVED from
`AGG_VALIDATORS`). Docs: `docs/annotated-manuscript-export.md` §Increment 5.
