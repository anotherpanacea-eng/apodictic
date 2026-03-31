---
description: Run a research mode or list available modes
argument-hint: [mode-name] or no argument to list all
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

Run a research mode from the APODICTIC Development Editor framework. Research modes are internet-enabled investigations that supplement structural analysis.

Load `../skills/specialized-audits/SKILL.md`.

**If no argument is provided** (or argument is "list" or "help"):
Display the available research modes:

- **citation-verifier** — Citation Verification: verify source existence, accuracy, and fit against attached claims. Produces `Citation_Ledger.md`
- **comp** — Comp Validation: verify comps are current, correctly positioned, query-ready
- **fact-check** — Factual Verification: spot-check real-world claims in historical fiction, memoir, technical works
- **field-recon** — Field Reconnaissance: scout for counterevidence, literature gaps, and source ecosystem health. Produces `Field_Reconnaissance_Report.md`
- **genre** — Genre Contract Currency: verify genre expectations reflect current market
- **representation** — Representation Context: surface community discourse for writing outside author's experience

**If an argument is provided:**
Load the named research mode's reference file from `../skills/specialized-audits/references/` and execute it. Follow research mode principles:
1. Research supplements structural judgment; it doesn't replace it
2. Cap queries: 3-5 per question
3. Present uncertainty: show the range when sources conflict
4. Note limitations: "unable to verify" is a valid output
5. Recommend experts when research scope is exceeded

All claims labeled `[SOURCE-VERIFIED: date]` or `[INFERENCE]`.

Research context: $ARGUMENTS
