<!--
Canonical worked-example Findings Ledger for the annotated-manuscript validator. Paired with the
snapshot + Timeline in this folder and exercised by `validate.sh --check-all`. The findings
exercise every anchor rung: F-RR-01 chapter (Chapter 9), F-LR-01 line-range (exact Timeline scene-id),
F-NEG-01 chapter-DEGRADE (shares Chapter 1 with scene "Ch 1 §1" but is chapter-only — proving the
resolver does NOT fabricate a line-range), F-DOC-01 document (a Pass-artifact ref), F-QT-01 quote
(Increment 2 — a verbatim unique evidence_quote anchored to the exact sentence, gated by A6), and
F-QAMB-01 quote-DEGRADE (an evidence_quote that appears twice — ambiguous, so it degrades to its
chapter ref rather than fabricating a sentence anchor). See docs/annotated-manuscript.md.
-->

# Findings Ledger — Example

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-RR-01","mechanism":"the middle third's pacing collapses — three days pass in two sentences at Chapter 9, reading as a continuity break","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Chapter 9"],"fix_class":"restore a transit beat or an explicit time marker","risk_if_fixed":"a too-explicit marker could slow the chapter's momentum"}
-->

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-LR-01","mechanism":"the opening scene states the want but never shows a cost, so the stakes stay abstract","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Ch 1 §1"],"fix_class":"give the want a price the reader can see","risk_if_fixed":"may slow the opening"}
-->

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-NEG-01","mechanism":"the chapter's POV discipline wavers in one paragraph","severity":"Should-Fix","confidence":"MEDIUM","evidence_refs":["Ch. 1"],"fix_class":"hold the POV or mark the break","risk_if_fixed":"none"}
-->

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-DOC-01","mechanism":"the orientation pass flags a soft genre signal with no single manuscript locus","severity":"Could-Fix","confidence":"LOW","evidence_refs":["Pass 1 §Orientation"],"fix_class":"sharpen the opening promise","risk_if_fixed":"none"}
-->

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-QT-01","mechanism":"the reveal of the unlit lighthouse lands as a stated fact rather than a felt beat","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Chapter 12"],"evidence_quote":"The lighthouse had stood unlit for the first time in forty years.","fix_class":"stage the reveal through a character's noticing","risk_if_fixed":"could over-explain the image"}
-->

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-QAMB-01","mechanism":"the repeated phrase reads as an unearned refrain","severity":"Should-Fix","confidence":"MEDIUM","evidence_refs":["Chapter 12"],"evidence_quote":"used to the dark","fix_class":"vary or cut the echo","risk_if_fixed":"none"}
-->
