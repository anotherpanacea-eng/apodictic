### Nonfiction & Argument — First-Class Front Door

Restructured README, plugin description, and browser-facing materials to surface fiction and argument-shaped nonfiction as co-equal pillars.

**README.md (root):** Tagline updated to "a development editor for fiction and argument-shaped nonfiction." The `/start` mermaid promotes nonfiction from a Q3 constraint modifier to a Q1 fork (argument-shaped piece alongside manuscript). "How It Works" adds the argument contract framing (claim / audience / burden / stakes) and the Nonfiction Argument Engine's diagnostic role. "See It in Action" adds a nonfiction samples section (marked-up op-ed + Dialectical Clarity letter, marked available at first release — no sample files exist yet). "Beyond Full Edits" restructured into two co-equal headed blocks: Fiction and Nonfiction & Argument. "Key Terms" expanded with argument terms: argument contract, claim ladder, warrant, burden, Dialectical Clarity, scope drift.

**Plugin description (registry-derived):** Updated tagline across `plugin.json`, `marketplace.json`, and `.claude-plugin/marketplace.json` to lead with "fiction and argument-shaped nonfiction."

**Registry commands:** `/start` writerQuestion updated to "manuscript or argument"; `/audit` writerQuestion surfaces argument-specific audits (dialectical, argument-decision).

**`plugins/apodictic/README.md`:** Tagline, "What It Does," "Intended Audience," and "Components > Workflows" restructured into Fiction and Nonfiction & Argument pillars, with the Nonfiction Argument Engine and its Dialectical Clarity / Red-Team / Persuasion / Evidence companions called out as a top-level workflow group.

**`overview-dashboard.html`:** Header tagline updated. New "Nonfiction Argument Engine" section added as a top-level subsystem (before Specialized Audits) listing the engine, Dialectical Clarity, Red-Team, Persuasion, Evidence, and ArgScope. Argument workflow promoted to first position in Common Workflows.

**`route-explorer.html` + `route-explorer.codex.html`:** Added `argument` as a Q1 artifact option ("An argument-shaped piece — op-ed, brief, testimony, essay") with four goals (diagnose, dialectical, red_team, pre_draft) and corresponding ROUTES entries routing to the Nonfiction Argument Engine, Dialectical Clarity Audit, Argument Red Team, and argument pre-draft pathway.
