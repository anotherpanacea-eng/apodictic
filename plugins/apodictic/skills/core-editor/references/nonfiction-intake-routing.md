<!-- nonfiction-intake-routing.md — Fragment extracted from intake-router-runtime.md §4a.
     Canonical home for the nonfiction triage routing logic.
     Loaded by the nonfiction-argument-engine skill when constraint=nonfiction fires.
     Source section is marked replaced-with-include in intake-router-runtime.md §4a. -->

# Nonfiction Intake Routing Fragment

*This fragment contains the nonfiction triage branch from `intake-router-runtime.md §4a`. It is loaded
by the nonfiction-argument-engine skill to resolve argument-shaped vs. narrative vs. memoir routing.
The full intake router (Q1/Q2, Table A/B, lifecycle table) remains in `intake-router-runtime.md`.*

---

## §4a. Nonfiction Routing Rules

When `constraint:nonfiction` is active and the user has prose pages rather than an idea-only project,
do not treat nonfiction as a generic gap. Apply this triage:

### Route to the Nonfiction Argument Engine when:

1. the manuscript makes an extractable main claim
2. support, comparison, evaluation, proposal, or testimony dominates the structure
3. the user is working on an op-ed, policy brief, testimony, academic argument, open letter, advocacy argument, recommendation memo, white paper, legal-style brief, or other claim-bearing prose

### Route to the Nonfiction Argument Engine with `register=generative` when:

1. the manuscript makes an extractable claim or offers an organizing lens
2. the dominant mode is exploratory: associative development, metaphor extension,
   thinking-in-public, or aphoristic/essayistic structure
3. the writer confirms the proposed register at intake; it is never silently inferred
4. no intake-declared high-stakes signal is present

Record `Register`, `Register confirmation`, `High-stakes gate`, and consequence context in
Argument_State §1. High-stakes forms force `register=asserted`. In a confirmed generative
run, inventory every cash-out with a stable `CO#`; prescriptions retain asserted burden at
that span.

### Route to Narrative Nonfiction Craft when:

1. the material is primarily scene-led, reportorial, or chronologically narrative
2. the reader's main question is about scene construction, pacing, source integration, and factual storytelling experience

### Route to Memoir & Creative Nonfiction when:

1. first-person witness, memory, truth-craft, and ethical obligation are central
2. experiential authority dominates even if an argument is present

### Hybrid rule

If the manuscript is Franklin Classification 3:

1. choose Dialectical Clarity when argument dominates and narrative is serving evidence or stakes
2. choose Narrative Nonfiction Craft when narrative dominates and the argument is secondary

### Default activation by form

| Form | Default route |
|---|---|
| Op-ed / persuasive essay / open letter | Dialectical Clarity |
| Policy brief / recommendation memo / white paper | Dialectical Clarity; offer Red Team next |
| Testimony | Dialectical Clarity; offer Red Team next |
| Academic argument / review essay / legal brief | Dialectical Clarity |
| Lens essay / exploratory essay / aphoristic sequence / blog-native serial essay | Dialectical Clarity with `register=generative`; offer Red Team on cash-out points only |
| Reported feature / scene-led journalism | Narrative Nonfiction Craft |
| Memoir / personal essay / witness-led CNF | Memoir & CNF; add Dialectical Clarity when explicit claim burden dominates |

### Post-diagnostic offer

After Dialectical Clarity on nonfiction argument work, surface the next likely action:

1. `/audit argument-red-team` for hostile pressure testing
2. `/audit argument-evidence` when evidence legitimacy is the likely bottleneck
3. `/audit argument-persuasion` when audience fit is the likely bottleneck
4. `/coach` for revision sequencing
