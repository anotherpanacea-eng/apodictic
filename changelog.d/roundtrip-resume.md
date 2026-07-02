### Workflows — One-Click Round-Trip Resume at `/start`

The built round-trip revision loop (reanchor → emit → crossref) is now **surfaced**, not just
reachable: at the bound-project `revising` **and** `diagnosed` nodes, `/start` checks round-trip
eligibility (a prior run folder holding a `*_Annotation_Manifest_*.md` + `python3` — a file glob,
no new command, no new `next_action`) and, when eligible, offers **"Returning with a revised
draft?"** alongside the existing dispatch. On accept it sequences the existing gated surfaces —
reset check, snapshot, `reanchor` classify, `emit -o <new_run_folder>` (exit (a): carry-only),
optional targeted re-diagnosis, `regression-diff` + `crossref` — and closes the round with a new
step 4: a per-finding **disposition table** the operator confirms row by row (the model proposes;
the operator disposes). The record (`[Project]_Roundtrip_Disposition_[runlabel].md`, marker-based)
carries a **hard-sequenced** confirmation token written only after every row is confirmed, and
resolved markers are written for `confirm-resolved` rows only.

New `roundtrip-disposition` validator (`reanchor.py disposition`, joined into `--self-test-all` /
`--check-all` with a canonical fixture pair + hostile arms): **RT1** recompute alignment (row
classes and the derived `compares:` header must equal a live reanchor/crossref recompute — no
stale or fabricated evidence), **RT2** confirmation record present (no decided row without the
token; the validator proves the record, never the human — that layer is the new **rev-a4**
attested item on the `revision_round` gate), **RT3** confirmed-writes-only (a resolved marker
without a confirmed disposition — the vanished-anchor auto-close — is an ERROR), **RT4**
partition coverage (every finding id in the recomputed RA3 partition must have a disposition
row, missing ids named — a partial record never reads round-close clean; WARN, ERROR
`--strict`), **W1**
unadjudicated/staged (advisory; ERROR `--strict`). Existing gates (RA1–RA3, R1, W1–W3, X1,
rev-a1–a3) and both lifecycle writers are unchanged — the disposition record is a confirmation
precondition upstream, never a third writer. Closes ROADMAP "Toward truly great" #2's last mile.
