# Example — Revision Report (round-trip round-close companion)

<!--
Companion fixture to example-roundtrip-disposition.md: the minimal Revision Report the
`--check-all` step stages as Example_Revision_Report_reanchor-r2.md beside the disposition
record. Its single resolved marker names exactly the one finding the disposition record decides
confirm-resolved (F-RR-01), so RT3 (confirmed-writes-only) passes and W1 has nothing staged.
The hostile arm appends an extra resolved marker for a keep-open finding to prove RT3 FAILS on
an unconfirmed close. Keep gate-valid.
-->

- Flags resolved: F-RR-01 — the Chapter 9 pacing seam was rebuilt; the anchored chapter is gone
  in the revised draft and the operator confirmed the disposition.
  <!-- resolved: F-RR-01 -->
- Flags still present: F-QT-01, F-NEG-01, F-DOC-01 — carried onto the revised draft by the
  re-anchor (held/moved); kept open.
- Needs editor placement: F-QAMB-01 (chapter heading now duplicated), F-LR-01 (line-range —
  not re-anchorable by design).
- New issues introduced: none recorded in this round.
- Ripple effects detected: none recorded in this round.
- Next priority: F-QT-01.
