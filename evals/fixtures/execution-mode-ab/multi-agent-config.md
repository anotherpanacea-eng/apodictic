# Mode B — Multi-Agent (Swarm) config

The **multi-agent / swarm** arm of the A/B pair. The editor orchestrator fans the same
`manuscript.md` out to independent reading lenses, collects a Findings Ledger, and runs a
consolidation step to produce one final output.

- **Input:** `manuscript.md` (verbatim, whole — identical to Mode A).
- **Execution mode:** swarm (`run-core.md §Execution Mode`) — subagent fan-out + Findings
  Ledger + consolidation.
- **Pre-Pass Re-Grounding / Staged Visibility:** run in their **multi-agent** form (the more-
  observable mode). The A/B contrast against Mode A is the point of the pair.
- **Output artifact:** one scorer-readable **consolidated** findings list, same schema as
  Mode A (finding id, severity band, failure locus, one-line rationale).
- **Cost capture:** log tokens in/out; the swarm arm is expected to cost materially more (the
  "~5×" claim under test). Report cost-adjusted; do not fabricate the multiplier if capture
  is unavailable.

**Honest scoping (`docs/swarm-vs-single-eval.md`):** this arm bundles independent-lens reading
**and** a consolidation step — the comparison cannot isolate "independent-lens reading" as the
mechanism, and swarm outputs carry structural tells (consolidation seam, length) that make
blind scoring only partially achievable. Reduce scoring to the mechanical GT-band match in
`expected.md` where possible; pre-register and dual-rate any defensibility judgment.
