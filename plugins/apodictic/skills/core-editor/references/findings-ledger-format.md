# Findings Ledger — Entry Format

*Reference file for the APODICTIC Development Editor. Loaded when writing or validating per-pass ledger entries. Holds the ledger entry template and the Structured Findings Block, extracted from `run-core.md` §Findings Ledger Protocol. The protocol purpose, when-to-write rule, consolidation requirement, and Ledger Discipline remain in `run-core.md`.*

---

#### Ledger Entry Format

Each pass appends a section using this structure:

```markdown
---

## Pass [N]: [Name] — Ledger Entry

### Notable Findings

[Numbered list. Each entry: one sentence stating the finding, one sentence
stating why it matters for the editorial letter, a pointer to the
specific location in the pass artifact, and optionally, the best case
against the finding.]

1. **[Finding name].** [What it is.] [Why it matters.]
   *(See Pass N, §[Section], [table/paragraph name].)*
   *Counterevidence:* [Optional. The strongest case that this finding is
   wrong, overstated, or explained by authorial intent. Omit if no
   plausible countercase exists. When present, helps synthesis calibrate
   severity and prevents the ledger from reading as a list of assertions.]

### Data Artifacts for Letter Reference

[List of tables, inventories, matrices, or other structured data in the
pass artifact that the editorial letter should direct the author to.
One sentence per artifact describing what it shows and why it's useful
for revision.]

- **[Artifact name]** — [What it shows, in one sentence.]
  *(Pass N, §[Section].)*

### Cross-Pass Connections

[Findings from this pass that connect to earlier ledger entries. These
are pre-built hypotheses about shared root causes — the synthesis step
evaluates them. Format: what this pass found, what it connects to,
and why the connection matters.]

- [Connection description.]
  *(Connects to: Pass M, Finding N.)*

### Unresolved Questions

[Observations this pass surfaced but couldn't fully analyze within its
scope. These may become stress test material, deferred audit triggers,
or items for the "Additional Observations" section of the editorial
letter.]

- [Question.]

### Audit Triggers

[Migrated here from pass artifact. The pass artifact retains its own
audit triggers section for standalone readability, but the ledger
consolidates them for the synthesis step.]

| Trigger | Evidence | Recommendation |
|---------|----------|----------------|
```

#### Structured Findings Block (Optional — Recommended for Hybrid/Swarm)

When running in hybrid or swarm mode, each Notable Finding in the ledger entry may include an optional structured metadata block after the prose description. This block provides machine-parseable fields that help the synthesis subagent integrate findings across independently-run passes without relying solely on prose interpretation.

The structured block is *supplementary*, not a replacement for the prose finding. The prose is the primary record; the structured block is an index.

```markdown
1. **[Finding name].** [What it is.] [Why it matters.]
   *(See Pass N, §[Section], [table/paragraph name].)*
   *Counterevidence:* [If applicable.]

   <!-- structured-finding
   mechanism: [One sentence: the craft mechanism that produces the problem]
   severity: [Must-Fix | Should-Fix | Could-Fix]
   confidence: [HIGH | MEDIUM | LOW | UNCERTAIN]
   evidence-refs: [Scene X (ch Y), Scene Z (ch W)]
   fix-class: [Class of intervention — e.g., "redistribute dramatic weight," "add interiority at decision point"]
   risk-if-fixed: [What the fix might harm]
   -->
```

**Usage rules:**
- In sequential mode, the structured block is optional — the synthesis step has the full ledger in context and prose is sufficient.
- In hybrid and swarm modes, the structured block is strongly recommended because the synthesis subagent may receive ledger entries from passes it didn't witness. The structured fields make cross-pass clustering faster and more reliable.
- The `mechanism` field is the most important. If two findings from different passes name the same mechanism, the synthesis step should investigate whether they share a root cause.
- Never let the structured block contradict the prose. If they diverge, the prose governs.

---
