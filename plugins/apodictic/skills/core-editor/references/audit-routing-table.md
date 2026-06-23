# Audit Routing Table

*Reference file for the APODICTIC Development Editor. Loaded at the contract step. Holds the contract-driven audit-activation rules extracted from `run-core.md`. The signal-emitting-audit registry (Phase 2) is homed here.*

---

**Contract-driven activation rules:**

| Signal in Contract | Recommended Audits | Rationale |
|---|---|---|
| Thriller or Suspense | Stakes System, Decision Pressure, Mystery/Thriller Architecture | Thriller contract demands escalating pressure field, credible urgent choices, and information-pressure delivery |
| Mystery or Investigation | Decision Pressure, Mystery/Thriller Architecture, Stakes System | Mystery contract demands evidence-governed choices, clue economy, and consequence architecture |
| Romance | Emotional Craft, Decision Pressure | Romance contract demands felt emotional transmission and credible commitment/withdrawal choices |
| Horror | Stakes System, Emotional Craft, Horror Craft | Horror contract demands consequence delivery, dread transmission, and sustained pressure |
| Literary or Upmarket | Scene Turn, Emotional Craft, Literary Craft, Decision Pressure | Literary mode demands scene-level precision, emotional specificity, prose-as-structure integration, and psychologically precise choices |
| SFF (Science Fiction / Fantasy) | SFF Worldbuilding, Stakes System | SFF contract demands world-rule integrity and system-scale consequence |
| Significant physical conflict present | Force Architecture | Any manuscript where physical confrontation carries narrative weight |
| Memoir, personal essay, creative nonfiction | Memoir/CNF (Gornick Layer), Franklin Pathway | Memoir requires situation/story distinction and narrating intelligence; Franklin tests pre-spine viability |
| Narrative nonfiction, reported feature, profile | Narrative Nonfiction Craft (Hart), Franklin Pathway | Nonfiction with narrative ambitions requires scene construction and source integration diagnostics |
| Composite novel or series | Series/Composite Novel | Multi-part works require standalone function and distance management |
| Series continuity concern | Series Continuity | Cross-volume consequence propagation, state tracking, thread inventory; requires Pass 10 + Pass 8 |
| Heat level > 0 or erotic content present | Erotic Content Tag | Intimate scenes require load-bearing vs. decorative analysis |
| Consent complexity, power dynamics central | Consent Complexity | Works where consent is narratively interrogated, not just present |
| Cozy signaling in marketing or tone | Cozy Tag | Cozy promise requires safety envelope and recovery rhythm diagnostics |
| Philosophical themes, novel of ideas | Philosophical Tag, Dialectical Clarity | Idea-driven work requires question architecture and rhetorical fairness |
| Historical setting (>50 years before composition) | Historical Fiction | Period settings require authenticity and attitude diagnostics |
| Significant female characters in any genre | Female Interiority | Tracks persistent inner life across all scene types; catches interiority thinning |

**Activation is recommendation, not mandate.** Present the recommended audit list to the author at intake. Author can accept, decline, or add audits. Record selections in the contract document.

**Minimum recommendation:** Every manuscript should receive at least Stakes System and Decision Pressure recommendations, since both address universal craft concerns (pressure architecture and choice plausibility).

---

## Signal-Emitting Audit Registry (v2.0.0)

Audits that emit internal severity signals — Must-Fix floors, hard gates, HIGH/Alert ratings, named flags, or Pass-10 inconsistency counts — and therefore **must** carry an explicit row in `pass-dependencies.md` §4e, so the signal propagates onto the Canonical Severity Scale (`output-policy.md §Canonical Severity Scale`) rather than dying in the audit findings file. `scripts/validate.sh audit-signal-propagation --check-registry` fails if any entry below lacks a §4e row.

Intentionally **excluded** (no severity signals — they need no §4e row): purely advisory audits — Idiolect Preservation, Punctuation Cadence — and research audits whose priority-flagged findings propagate under the §4e default mapping (Factual Verification, Comp Validation, Genre Currency, Representation Context). When adding a signal-emitting audit, add it here **and** add its §4e row in the same change.

<!-- registry:signal-emitting-audits:begin -->
- Stakes System
- Decision Pressure
- Scene Turn
- Compression
- Reception Risk
- Content Advisory
- Banister (Epistemic Humility)
- AI-Prose Calibration
- Female Interiority
- Interiority Preservation
- Dialectical Clarity
- Argument Red Team
- Argument Persuasion
- Argument Evidence
- Adversarial Evidence Review
- Field Reconnaissance
- Citation Verifier
- Character Architecture
- Emotional Craft
- Literary Craft Deep Dive
- Force Architecture
- Series Continuity
- Series & Composite Novel
- Shelf Positioning
- Short Fiction
- Narrative-Decision (StoryScope)
- Argument-Decision (ArgScope)
- POV Voice Profile
- Reader-Persona Simulation
- Comedy & Satire
- Historical Fiction
- Memoir / Creative NF
- Narrative Nonfiction
- Fan Fiction Conversion
- SFF Worldbuilding Integration
- Horror Craft Integration
- Supernatural Horror
- Grimdark / Dark Fantasy
- Mystery / Thriller Architecture
- Consent Complexity
- Erotic Content
- Queer Romance / Erotica
- Cozy Tag
- Philosophical Tag
- Timeline (Pass 10)
<!-- registry:signal-emitting-audits:end -->

