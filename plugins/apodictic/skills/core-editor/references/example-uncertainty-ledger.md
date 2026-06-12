# Findings Ledger — *The Lighthouse Year* (uncertainty fixture)

*A minimal fixture Findings Ledger carrying genuine uncertainty — one `LOW`-confidence finding and
one Unresolved-Questions bullet — so the canonical `reader-instrument` `--check-all` gate has real
provenance to resolve. (The shipped `example-findings-ledger.md` carries a single HIGH-confidence
Must-Fix and `### Unresolved Questions: none`, which would correctly trip `B5` and offers no UQ to
test — hence this dedicated fixture.) Not a full Ledger; it exists only to anchor the worked
Beta-Reader Instrument.*

### Notable Findings

- A LOW-confidence Pass 5 suspicion about the midpoint, and an open question Pass 8 surfaced but
  could not settle from the text alone.

   <!-- apodictic:finding
   {
     "schema": "apodictic.finding.v1",
     "id": "F-P5-01",
     "mechanism": "the midpoint reversal may under-land — the lead's change of course mid-book reads as quiet, but it is unclear whether readers register it as a turn at all",
     "severity": "Should-Fix",
     "confidence": "LOW",
     "evidence_refs": ["Chapter 12"],
     "fix_class": "consider sharpening the external marker of the lead's decision at the midpoint",
     "risk_if_fixed": "a louder turn could overstate a change the book wants to keep understated"
   }
   -->

### Unresolved Questions

- Does the ending's final image read as hope or as resignation? The text holds both; the pass could not settle which dominates on a first read.
