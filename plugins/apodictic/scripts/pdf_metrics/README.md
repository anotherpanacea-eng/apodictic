# Pinned PDF geometry inputs

`generate.py` verifies every retained source checksum and derives
`helvetica-winansi.json` offline. Run `python3 generate.py` in this directory.
Source files are unchanged; the derived table is a modification combining
Helvetica advances/ink bounds with WinAnsi byte-to-glyph names. It excludes
control/undefined CP1252 bytes and maps `nbspace` and `sfthyphen` to the Adobe
Helvetica `space` and `hyphen` metrics, as described by PDF 1.4 Appendix D.
There is no runtime network or platform font dependency.

Sources fetched 2026-10-04 (exact checksums are in the recipe):

- Adobe-authored [Helvetica.afm](https://raw.githubusercontent.com/tecnickcom/tc-font-core14-afms/main/Helvetica.afm),
  distributed with the unchanged [Adobe license](https://raw.githubusercontent.com/tecnickcom/tc-font-core14-afms/main/LICENSE).
  The AFM copyright notices and `ADOBE-LICENSE` must remain with the data.
- Apache PDFBox [WinAnsiEncoding.java](https://raw.githubusercontent.com/apache/pdfbox/trunk/pdfbox/src/main/java/org/apache/pdfbox/pdmodel/font/encoding/WinAnsiEncoding.java),
  retained with [Apache license](https://raw.githubusercontent.com/apache/pdfbox/trunk/LICENSE.txt)
  and [notice](https://raw.githubusercontent.com/apache/pdfbox/trunk/NOTICE.txt).
  The recipe extracts only the explicit encoding table; it does not apply
  PDFBox's fallback assignment of unused bytes to bullet.

The Adobe [PDF 1.4 Reference](https://stuff.mit.edu/afs/sipb/contrib/doc/specs/software/adobe/pdf/PDFReference.pdf)
Appendix D supplies the mapping semantics; the
[AFM specification](https://adobe-type-tools.github.io/font-tech-notes/pdfs/5004.AFM_Spec.pdf)
defines `WX` and `B`. Geometry must use those names, rather than AFM numeric
codes (which describe AdobeStandardEncoding).

The AFM Euro entry has an empty ink box. Keeping that value is deliberate:
navigation geometry must refuse non-whitespace glyphs with empty bounds,
including Euro in mixed text. This table does not assert reader qualification
or change the default PDF exporter.
