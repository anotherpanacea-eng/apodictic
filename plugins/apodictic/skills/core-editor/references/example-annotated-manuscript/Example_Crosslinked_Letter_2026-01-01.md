# Example — Editorial Letter

<!--
Canonical worked editorial letter for the `crosslink` validator (Annotated-Manuscript Increment 3).
HAND-AUTHORED: it carries a `<!-- finding: F-... -->` marker for each finding in the paired annotation
manifest, so `crosslink render` can inject a back-link to each finding's manuscript anchor and the
`crosslink` gate proves bidirectional integrity + no letter mutation. The shipped synthesis does not yet
emit a letter whose finding markers match this manifest — see docs/annotated-manuscript.md §Increment 3
(consumer-only / inert on the real corpus until the producer lands). Keep the finding-marker set in sync
with the manifest's annotations, or W1 (annotated-but-uncited) fires.
-->

## What Needs Work

The middle third's pacing collapses — three days pass in two sentences. <!-- finding: F-RR-01 -->{>>→ marked-up copy: F-RR-01 @ chapter:Ch 9<<}

The opening scene states the want but never shows a cost. <!-- finding: F-LR-01 -->{>>→ marked-up copy: F-LR-01 @ line-range:3-4<<}

The chapter's POV discipline wavers in one paragraph. <!-- finding: F-NEG-01 -->{>>→ marked-up copy: F-NEG-01 @ chapter:Ch 1<<}

The orientation read flags a soft genre signal with no single locus. <!-- finding: F-DOC-01 -->{>>→ marked-up copy: F-DOC-01 @ document:<<}

The unlit-lighthouse reveal lands as a stated fact rather than a felt beat. <!-- finding: F-QT-01 -->{>>→ marked-up copy: F-QT-01 @ quote:250-315<<}

The repeated phrase reads as an unearned refrain. <!-- finding: F-QAMB-01 -->{>>→ marked-up copy: F-QAMB-01 @ chapter:Ch 12<<}
