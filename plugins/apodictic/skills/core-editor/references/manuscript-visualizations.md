# Manuscript-Structure Visualizations — render the diagnosis, invent nothing

*Reference module for the APODICTIC Core Editor. A presentation layer that adds **no analysis**: a deterministic render of data the passes already produced. Spec + validator: `docs/manuscript-visualizations.md`, `scripts/validate.sh manuscript-viz`. Worked example: `example-structure-map-manifest.md` (paired with `example-timeline.md` + `example-findings-ledger.md`).*

---

## When to use

After a development edit, when a structural *picture* would help the author see the shape the editorial letter describes in prose — where the draft expands and compresses, whether a POV vanishes for stretches, where the findings cluster. The editorial letter remains the artifact of record; this is a companion.

## The firewall: render-only, provenance-closed

This capability **runs no pass and reaches no conclusion the letter did not already reach.** It is firewall-safe by construction:

- **Render-only.** The renderer consumes a manifest and emits SVG. No model call, no prose, no interpretation — it cannot add a plot event, a character, or a "the problem here is…" gloss, because it never reasons.
- **Provenance-closed.** Every visual element traces to a manifest entry, and every manifest entry is copied **verbatim** from a structured source — the Timeline Event-Ledger (scenes) or an `apodictic.finding.v1` block (findings). A chart cannot show a value those sources did not contain (validator `E2`/`E4`).
- **No annotation invention.** Labels are the author's scene IDs, the findings' own IDs/severities, the Timeline's POV names — never new copy.

## The artifact + manifest

A single self-contained `[Project]_Structure_Map_[runlabel].html` (no network, no deps, no telemetry — the local/no-telemetry commitment), a **pure function of an `apodictic.viz_manifest.v1` manifest**. The manifest holds only:

- **`scenes[]`** — `scene_id, chapter, line_range, word_count, pov, span, gap`, copied verbatim from `Timeline.md` Section 1.
- **`findings[]`** — `id, severity, confidence, chapter`, where `chapter` is the **conservative** parse of the finding's `evidence_refs` (`Chapter N` / `Ch N` → `Ch N`, else the literal `unplaced` — the render never guesses a position).

The manifest carries **no visual-style fields** — color/size/emphasis live in the renderer, fixed, so a run cannot recolor a finding to soften it (`E1` fails if a style field appears).

## The chart set (Increment 1)

1. **Pacing / word-count curve** — `word_count` over scene order.
2. **POV time-share** — `word_count` summed by `pov` (a join *within* the Timeline, not the stylometric `pov-voice` audit).
3. **Finding-severity-by-chapter** — findings binned by the conservative chapter parse, severity as the dominant channel.

Future (each gated on its upstream artifact becoming machine-readable): reveal/tension timeline, character co-presence network, scene-function heatmap, and a validated `evidence_ref → scene_id` resolution for scene-precise placement.

## Severity honesty

- **Severity is the dominant, size-independent channel.** Must-Fix renders most salient; the `{Must-Fix, Should-Fix, Could-Fix} → encoding` map is **hardcoded in the renderer**, not the manifest.
- **Confidence never suppresses severity.** The renderer encodes severity only; it does **not** shrink, mute, or recolor a marker for low confidence. A LOW-confidence Must-Fix stays visually loud (full salience).
- **Every locked Must-Fix appears** (`E3`) — the visual analogue of `softness-check`'s locked→delivered rule.
- **Companion, not replacement** — the HTML header states the editorial letter is the artifact of record.

## Protocol

1. **Build the manifest** — copy the Timeline Event-Ledger rows into `scenes[]` (verbatim) and the findings into `findings[]` (id/severity/confidence verbatim; `chapter` from the conservative `evidence_refs` parse, else `unplaced`). Add no style fields.
2. **Gate** — `scripts/validate.sh manuscript-viz <run_folder>`. Resolve E1–E4; review W1 (an under-rendered Timeline) and W2 (scenes[] out of Timeline order). The `--check-all` gate runs the canonical example with `--require-block`, so a missing or unparseable manifest is a hard failure rather than a silent pass; add `--strict` to make the W advisories blocking too.
3. **Render** — `scripts/viz_manifest.py render <manifest> <timeline> <ledger> -o [Project]_Structure_Map_[runlabel].html`. `render` runs the provenance gate first and **refuses** on an ERROR-level failure (`--force` to override). The HTML is offline, self-contained, and labels itself *partial* when the draft is incomplete.

## Mechanical check

`scripts/validate.sh manuscript-viz <run_folder>`: E1 manifest schema + no-visual-style allowlist (a present-but-unparseable block is an E1 failure, not a no-op; `--require-block` also fails an absent block), E2 provenance closure (scene/finding/chapter), E3 Must-Fix completeness, E4 byte-equal copy fidelity; W1 coverage + W2 scene order (advisory, ERROR `--strict`). Ownership boundary: `manuscript-viz` owns manifest↔source provenance only — it does not re-check the letter (`finding-trace`/`softness-check`) or the Timeline's arithmetic/anchors (`timeline-*`); it consumes already-validated rows. Lineage: [`docs/manuscript-visualizations.md`](../../../../../docs/manuscript-visualizations.md).
