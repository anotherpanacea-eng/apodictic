# Promise-Contract Fidelity: The Cartographer's Grief (literary fiction)

<!--
Worked example of a contract-conformant Promise-Contract Fidelity report (core-editor workflow module;
see promise-contract.md + docs/promise-contract-audit.md). The module diagnoses the author's own
marketing COPY (query / synopsis / blurb / logline) against the inferred Contract — does the pitch
keep the promise the book makes? It CONSUMES Shelf & Positioning (genre/comp/tone); it owns only the
document-fidelity layer (emphasis, disclosure, over/under-promise, cross-document consistency).

This file is exercised by `validate.sh --check-all` as a canonical release-gate target for
`promise-contract`:
  P1 — every F-PCF-NN finding carries a two-sided namespaced ref (>=1 copy: AND >=1 contract:/ms:);
  P2 — an apodictic.pitch_copy.v1 input exists and every doc declares a valid copy_type;
  P3 — the disclosing synopsis must NOT raise a PCF2 reveal leak (the negative assertion);
  W1 — clean firewall scan (no authored multi-sentence quoted block that isn't verbatim copy).

The query here commits PCF1 (emphasis distortion — it leads with a minor subplot) + PCF4 (under-sell —
the controlling idea the book is built on is absent), each with valid two-sided refs. The synopsis
discloses the ending BY DESIGN (a synopsis is meant to) and so must NOT raise PCF2 — that negative is
the P3 form gate proved here. The module FLAGS the gap and names a class of repair; it never drafts
the replacement query (the Firewall — see W1).
-->

## Inferred Contract (excerpt)

The relevant Contract fields the flags below measure against (full schema in
`core-editor/references/contract-template.md`):

```
GENRE/SUBGENRE: Literary fiction
READER PROMISE: A meditation on grief that maps an interior landscape through an unreliable, shifting city
CONTROLLING IDEA: Grief reshapes the self + because we keep redrawing the map rather than reading the loss
ENDING TYPE: open
NON-NEGOTIABLES: the city's instability is the grief, not a fantasy device
```

## Persisted Pitch Copy

<!-- apodictic:pitch_copy
{"schema":"apodictic.pitch_copy.v1","id":"PC-01","copy_type":"query","text":"When the city's tram lines start rerouting overnight, municipal cartographer Yara Sole races to redraw the transit map before the spring festival. A budding romance with the festival's organizer complicates her deadline. A propulsive, plot-forward debut about a woman, a map, and a city that won't sit still."}
-->

<!-- apodictic:pitch_copy
{"schema":"apodictic.pitch_copy.v1","id":"PC-02","copy_type":"synopsis","text":"Yara Sole, six months a widow, maps a city that redraws itself each night. She believes the instability is municipal incompetence until, at the midpoint, she recognizes her own routes home rewriting themselves. In the final chapter she stops correcting the map and lets the city stay illegible; the last image is Yara leaving the cartography office for good, the unfinished map on the wall. The ending is deliberately open — she does not resolve the grief, she stops fighting it."}
-->

## Findings (Promise-Contract Fidelity)

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-PCF-01","mechanism":"PCF1 emphasis distortion: the query foregrounds the tram-rerouting logistics and the festival-organizer romance — both minor threads the manuscript backgrounds — and frames the book as plot-forward, while the manuscript's central conflict (grief rewriting the self, figured as the unstable city) never appears.","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["copy:query¶1","contract:READER PROMISE","contract:CONTROLLING IDEA"],"fix_class":"bring the copy back to the book — lead with the kept promise (the grief made spatial), not the logistics; do not add a subplot to the manuscript to match the query","risk_if_fixed":"a quieter, interiority-forward query reads as less commercial to a plot-seeking agent"}
-->

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-PCF-02","mechanism":"PCF4 under-sell: the manuscript's strongest kept promise — the controlling idea that grief reshapes the self because we keep redrawing the map rather than reading the loss — is the thing the book is built on, and it is entirely absent from the query.","severity":"Should-Fix","confidence":"HIGH","evidence_refs":["copy:query¶1","contract:CONTROLLING IDEA","ms:Ch 11"],"fix_class":"surface the controlling idea the book already delivers; this is a copy gap, never a manuscript gap","risk_if_fixed":"naming the grief up front forfeits the misdirection the current query trades on"}
-->

## Notes

- **Two-sided gaps (P1).** Each `F-PCF` finding cites both the copy side (`copy:query¶1`) and the
  contract side (`contract:READER PROMISE` / `contract:CONTROLLING IDEA`, and a manuscript locus
  `ms:Ch 11` for PCF4) — the namespaced-ref convention that makes a gap a gap.
- **The disclosing synopsis (P3 negative).** PC-02 deliberately discloses the open ending — a synopsis
  is *meant* to. No PCF2 (reveal leak) is raised against it, and the module's form gate (P3) guarantees
  PCF2 cannot fire on a `synopsis`. The reveal-leak flag is reserved for no-spoiler forms (query / blurb
  / logline).
- **Firewall (W1).** The findings name a *class* of repair ("lead with the kept promise"); they never
  draft the replacement query. (Pitch rewriting belongs to Shelf & Positioning's Reframe Protocol; this
  is its diagnostic-only sibling.)
- **Consume, don't duplicate.** Genre / comp / tone mismatch is Shelf & Positioning's territory and is
  not re-flagged here; this module contributes only the document-fidelity layer.
