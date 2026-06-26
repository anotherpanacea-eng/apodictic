<!-- argument-audits-routing.md — Fragment extracted from pass-dependencies.md §4a + §4b.
     Canonical home for argument-cluster audit routing rows (router-triggered and finding-triggered).
     Loaded by the nonfiction-argument-engine skill when constraint=nonfiction fires.
     Source rows are marked replaced-with-include in pass-dependencies.md §4a and §4b. -->

# Argument Audits — Routing Fragment

*This fragment contains the argument-cluster rows from `pass-dependencies.md §4a` (router-triggered)
and `pass-dependencies.md §4b` (finding-triggered). It is loaded by the nonfiction-argument-engine
skill for argument-shaped runs. The fiction routing tables remain in `pass-dependencies.md`.*

---

## §4a rows (router-triggered, argument cluster)

Activated by intake answers before passes run. These rows fire when the run resolves as
argument-shaped (constraint=nonfiction + persuasive-argument form per §4a Argument-shaped routing
definition in `pass-dependencies.md`).

| Router signal | Audit(s) | Policy | Reference file |
|---------------|----------|--------|----------------|
| Constraint = nonfiction (idea-stage) | (Nonfiction Pre-Draft Pathway — idea-stage gap) | Note gap; offer closest. Prose-stage nonfiction engines (argument / narrative / memoir) are built — see `intake-router-runtime.md` §6 Table A | — |
| Argument-shaped run (constraint=nonfiction + intake hint at white paper / policy brief / testimony / op-ed / academic article / regulatory comment / expert affidavit) | Field Reconnaissance | **Hard Prerequisite** when high-stakes signal present (testimony, expert affidavit, regulatory comment, peer-reviewed publication, or `constraint=high-stakes` flag); otherwise **Auto-recommend before synthesis** | `craft/research-field-recon.md` |
| Argument-shaped run (constraint=nonfiction + high-stakes intake hint: testimony / expert affidavit / regulatory comment / peer-reviewed publication) | Citation Verifier | **Pre-DE Prerequisite** (runs before passes; not a DE-internal audit — see audit reference) | `craft/research-citation-verifier.md` |

**Argument-shaped routing definition (Phase 6 Wave 3 / CR-4 closure).** A run is "argument-shaped" when intake produces `constraint=nonfiction` AND the intake hint, declared form, or contract draft places it in the persuasive-argument family: white paper, policy brief, testimony (oral or written), op-ed, academic article, grant proposal, legal brief, book review, advocacy journalism, open letter, regulatory comment, expert affidavit, or peer-reviewed publication. Memoir, narrative nonfiction, and creative-nonfiction forms are nonfiction but *not* argument-shaped; they route via their own §4a rows in `pass-dependencies.md`.

**High-stakes signal definition.** "High-stakes" applies when the manuscript's literature provenance is dispositive — i.e., a counterevidence miss could carry legal, regulatory, professional, or publication consequences the author cannot absorb post-hoc. The signal fires when any of the following hold: (a) intake declares the form as testimony, expert affidavit, regulatory comment, or peer-reviewed publication; (b) the contract carries an explicit `constraint=high-stakes` flag; (c) the intake hint identifies the audience as a court, legislative body, regulatory agency, or peer-review panel. Op-eds, academic articles, and policy briefs that lack these hooks default to the Auto-recommend before synthesis tier; the user can request Hard Prerequisite escalation at intake.

**Why argument-shaped runs get a prerequisite tier.** F4 Stage 2 (`docs/review-log/2026-04-24_tay-stage-2-comparative.md`) documented seven literature-counterevidence blind spots that the Stage 1 development edit missed because Field Reconnaissance was not prerequisited — Wave 2 audits operate on manuscript-as-written, so competing studies, replication failures, and meta-analytic counterevidence the author had documented privately (or that exist in the literature but were not surfaced) never entered the Findings Ledger. The Hard Prerequisite tier closes this gap by routing literature-counterevidence surfacing **before** the argument engine fires, so downstream passes (Dialectical Clarity, Argument Red Team, Argument Evidence Deep-Dive) operate against a literature-aware claim graph rather than a manuscript-internal one. The Auto-recommend before synthesis tier provides the same routing for lower-stakes argument runs with an opt-out (and mandatory blind-spot disclosure if declined — see `run-synthesis.md` Step 3 Blind Spot / Absence Inventory and Step 11 Appendix A).

---

## §4b rows (finding-triggered, argument cluster)

Activated by pass results during a diagnostic run. These rows fire on argument-shaped runs when the
relevant pass produces the listed finding pattern. Tier precedence follows §4f in `pass-dependencies.md`.

| Pass | Finding pattern | Audit(s) | Policy |
|------|----------------|----------|--------|
| 9 (Thematic Coherence) | Thematic argument under-structured, didacticism | Dialectical Clarity | Recommend |
| Any pass | Consent ambiguity, governance legibility failure, coercion aestheticization risk, or aftercare / repair incoherence in intimate or power-dynamic material | Consent Complexity | Auto-recommend before synthesis |
| Any pass | Representation contestation, screenshot risk, extractability, hostile-reader portability, or culturally volatile framing | Reception Risk | Auto-recommend before synthesis |

*Note: Consent Complexity and Reception Risk also fire on fiction runs; they are listed here because
they also fire on argument-shaped runs. Their canonical tier entries remain in `pass-dependencies.md §4b`.
This fragment lists them here for completeness of the argument routing picture.*
