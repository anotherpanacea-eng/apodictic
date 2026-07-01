# Roundtrip Disposition — Example reanchor-r2

<!--
Canonical fixture for the `roundtrip-disposition` validator (RT1-RT3 + W1), paired with
example-roundtrip-revision-report.md. The `--check-all` step stages it as
Example_Roundtrip_Disposition_reanchor-r2.md in a temp "this round" folder beside a copy of
../example-run-folder-r2's ledger, with a temp prior folder holding ../example-annotated-manuscript's
manifest + ledger and example-reanchor-revised.md as the revised snapshot. Every row below is
RECOMPUTE-CONSISTENT with those inputs (built by running the chain once and confirming by hand):
the anchor classes are what `reanchor` classifies against the revised snapshot (a held chapter and
a held document note, a moved quote, a vanished chapter, a duplicated-chapter ambiguity, and a
not-re-anchorable line-range), and the regression classes are what `regression_diff.crossref_classes`
returns for the prior ledger against the round-2 ledger (no origin/chapter/mechanism match and no
prior resolution claim, so every prior finding classes as unexplained-drop). The dispositions are the
operator's: one vanished anchor confirmed resolved (and reflected in the companion Revision Report),
the surviving notes kept open, the two refused re-anchors sent to placement. The human table is
presentation; the HTML-comment rows are the machine record; the file-level confirmation token is
written only after every row has been presented and confirmed (state-lifecycle.md §Round-Trip
Re-Anchoring, step 4). Keep gate-valid: `validate.sh roundtrip-disposition` must PASS with no W1.
-->

compares: 2026-01-01 → reanchor-r2

| finding | anchor class | regression class | proposed | decision |
|---|---|---|---|---|
| F-RR-01 | vanished | unexplained-drop | confirm-resolved | confirm-resolved |
| F-QT-01 | moved | unexplained-drop | keep-open | keep-open |
| F-NEG-01 | held | unexplained-drop | keep-open | keep-open |
| F-DOC-01 | held | unexplained-drop | keep-open | keep-open |
| F-QAMB-01 | ambiguous | unexplained-drop | needs-placement | needs-placement |
| F-LR-01 | not-re-anchorable | unexplained-drop | needs-placement | needs-placement |

<!-- disposition: F-RR-01 anchor=vanished regression=unexplained-drop decision=confirm-resolved -->
<!-- disposition: F-QT-01 anchor=moved regression=unexplained-drop decision=keep-open -->
<!-- disposition: F-NEG-01 anchor=held regression=unexplained-drop decision=keep-open -->
<!-- disposition: F-DOC-01 anchor=held regression=unexplained-drop decision=keep-open -->
<!-- disposition: F-QAMB-01 anchor=ambiguous regression=unexplained-drop decision=needs-placement -->
<!-- disposition: F-LR-01 anchor=not-re-anchorable regression=unexplained-drop decision=needs-placement -->
<!-- disposition-confirmed: operator 2026-07-01T09-00 -->
