# Legal Risk Register (workflow)

**Status:** v1 + detection layer (per-class detection guidance + escalation-trigger taxonomy)
**When:** memoir, autofiction, or nonfiction that portrays **identifiable real people**, or that quotes substantial third-party copyrighted material. Run after the structural read, when the author is heading toward publication.
**Home:** core-editor (manuscript-content analysis). Design + lineage: [`docs/legal-risk-register.md`](../../../../../docs/legal-risk-register.md).

---

## Purpose & firewall

Flag the manuscript's **legal-exposure areas** — defamation, privacy/disclosure, rights-clearance — so the author knows where to get a lawyer's eyes before publishing. **The firewall: flag, don't practice law.** Name the exposure and the trigger; route the serious items to counsel. Never adjudicate ("this is not defamatory", "protected by fair use", "no liability") — that is a legal conclusion only a qualified attorney makes. *I am not a lawyer; this flags areas that may need legal review and is not legal advice.*

---

## The artifact: `[Project]_Legal_Risk_Register_[runlabel].md`

A **not-a-lawyer disclaimer** plus a set of `apodictic.legal_risk.v1` blocks — one per flagged area:

```markdown
<!-- apodictic:legal_risk
{"schema":"apodictic.legal_risk.v1","id":"LR-01","risk_class":"defamation",
 "severity":"review-now","subject":"a named, identifiable living person",
 "locations":["Ch. 4"],
 "concern":"a stated-as-fact assertion of misconduct by a named living person",
 "escalation_trigger":"any retained statement of fact alleging a crime by a named living person",
 "disposition":"route to legal counsel before publication; substantiate or reframe as opinion"}
-->
```

- **`risk_class`** — `defamation` (false statement of fact harming reputation) | `privacy` (private facts about an identifiable person, disclosed without consent) | `rights-clearance` (quoted lyrics/images/substantial text needing permission) | `other`.
- **`severity`** — a **legal-escalation tier**, separate from the editorial Must/Should/Could scale: `monitor` → `review-recommended` → `review-now`.
- **`concern` / `disposition`** — flags, never legal conclusions. `escalation_trigger` is the condition that should route the item to a lawyer.

Field set canonical in `schemas/apodictic.legal_risk.v1.schema.json`. Worked example: `core-editor/references/example-legal-risk-register.md`.

---

## Detection guidance

What to flag, by `risk_class`. Scan for these signals; the finer categories (intrusion, false light, trade secrets, incitement, …) sit under the four schema classes. **Detection only — flag and route, never adjudicate.** The research + citations behind this guidance live in [`docs/legal-risk-detection-level-setting.md`](../../../../../docs/legal-risk-detection-level-setting.md) (not loaded at runtime).

- **`defamation`** — a *factual* assertion (verifiable, not opinion) lowering an identifiable **living** person's or active entity's reputation: crime, fraud, sexual misconduct, professional incompetence, addiction, financial wrongdoing. Identifiable even if unnamed (role + place + a unique event). Watch rumor/hearsay framing ("everyone knew", "allegedly" — repeating an allegation can carry its own exposure) and changed-name fiction that stays recognizable. **Lower exposure:** the dead and government bodies are generally not flaggable here; pure opinion/hyperbole with no embedded fact is `DEF_OPINION` (monitor at most).
- **`privacy`** — true-but-intimate facts about an identifiable **living private** person (medical/psychiatric, sexual, addiction, abuse, finances, family secrets); **intrusion** admissions (secret recording, hacking, trespass — flag the *method*); **false light** (invented/embellished scene creating an offensive false impression). **Lower exposure:** facts lawfully in the public record are `PRIV_PUBLIC_RECORD` (monitor); facts about a public figure germane to their public role are generally not flaggable.
- **`rights-clearance`** — quoted **song lyrics (any length)**, poetry, **epigraphs**, unpublished letters/diaries, images, or substantial prose excerpts without permission; a brand in the **title/cover/marketing** or implying endorsement; an admitted **NDA / settlement / confidentiality** covering the disclosed material; operative **trade-secret** detail; a real person's identity in **advertising/merchandise**. **Lower exposure:** titles/short phrases and uncopyrightable facts are not flaggable; a nominative brand mention in narrative is `TM_NOMINATIVE` (monitor); writing *about* a real person in expressive content is `ROP_EXPRESSIVE` (monitor) — the flagged risk is the marketing/merch/advertising use, not the storytelling.
- **`other`** — exposure outside the three: **incitement** (step-by-step instructions to commit a violent crime); **contempt / sub-judice** — commentary on an active proceeding (UK/AU — no direct US analogue); **breach of a court / suppression / sealing order** (`RESTRICTED_RECORD_OR_ORDER`, which *includes* US sealed / gag / grand-jury material); **IIED**-grade targeted humiliation of a private person.

**Severity = base tier + modifiers.** Set `severity` to the trigger's base tier (below), then **raise** one step per modifier that fires (cap `review-now`; never silently lower), and name the modifiers in `escalation_trigger`: `+identifiable-living-private-person` · `+serious-allegation` (crime/sexual/professional-ruin) · `+weak-or-no-documentation` · `+international-distribution` (UK/EU/AU) · `+author-signed-agreement` · `+marketing/cover/merchandise-use` · `+minor-or-vulnerable-subject`. A modifier already baked into a code's own condition (e.g. `DEF_SERIOUS_ALLEGATION_PRIVATE` already implies `+serious-allegation`) does **not** raise the tier a second time. Lowering is allowed only with a documented reason in the `escalation_trigger`/`disposition` — **never silently**.

**Route-to-counsel (`review-now`) bright lines.** The `review-now` rows of the §Escalation-trigger taxonomy *are* the bright lines — any one of them mandates counsel. The recurring shapes: an unsupported allegation of serious fact about an identifiable living person · intimate non-public facts about a private person (esp. a minor/victim/patient) without consent · unlicensed lyrics/poetry/unpublished writing/images · NDA- or settlement-covered disclosure · identity in advertising/merchandise · material obtained unlawfully · breach of a court/suppression order · instructions enabling a violent crime.

**Jurisdiction — flag, don't resolve.** Default US, but **flag** divergence, never resolve it: UK/AU are claimant-friendlier (serious-harm threshold; robust privacy / breach-of-confidence; contempt/sub-judice with no US equivalent); EU has GDPR and no open-ended fair use. For international distribution, flag against the stricter regime — choice of law is the lawyer's call.

## Escalation-trigger taxonomy

A controlled vocabulary for `escalation_trigger` (recommended, not schema-enforced). Use one code plus the modifiers that fired; raise the tier per §Detection guidance.

| Code | Default | Condition |
|---|---|---|
| `DEF_SERIOUS_ALLEGATION_PRIVATE` | review-now | crime/sexual/professional-ruin fact, identifiable living person, thin support |
| `DEF_FACT_PRIVATE` | review-recommended | reputational fact about a private person |
| `DEF_FICTION_IDENTIFIABLE` | review-recommended | defamatory content believable as fact about a recognizable model |
| `DEF_OPINION` | monitor | subjective characterization, no embedded fact |
| `PRIV_INTIMATE_PRIVATE` | review-now | intimate fact (health/sex/abuse), identifiable private person, no public concern |
| `PRIV_UNLAWFUL_ACQUISITION` | review-now | secret recording / hacking / trespass / restricted record |
| `PRIV_FALSE_LIGHT` | review-recommended | invented/embellished offensive false impression |
| `PRIV_PUBLIC_RECORD` | monitor | already lawfully public |
| `CR_LYRICS_POETRY_UNPUB` | review-now | song lyric / poetry / unpublished third-party writing, no licence |
| `CR_IMAGE` | review-now | photograph / artwork / chart without licence |
| `CR_EXCERPT_SUBSTANTIAL` | review-recommended | substantial prose excerpt / epigraph |
| `TM_TITLE_COVER_OR_ENDORSE` | review-now | mark in title/cover/marketing or implied endorsement |
| `TM_NOMINATIVE` | monitor | ordinary brand mention in narrative |
| `ROP_ADVERTISING_MERCH` | review-now | real person's identity in advertising / merchandise |
| `ROP_EXPRESSIVE` | monitor | identity within expressive content (lower-risk; the flag is marketing/merch use) |
| `NDA_DISCLOSES_COVERED` | review-now | discloses matter within a signed agreement |
| `TRADESECRET_OPERATIVE` | review-now | operative proprietary detail |
| `INCITEMENT_INSTRUCTIONAL` | review-now | how-to for a violent crime |
| `RESTRICTED_RECORD_OR_ORDER` | review-now | sealed / gag / grand-jury / sub-judice |
| `IIED_PRIVATE_OUTRAGEOUS` | review-now | targeted humiliation of a private person |

A few researched classes are deliberately **code-less** for now — *life rights / releases*, *breach of confidence* (non-contractual, UK/AU), and *religious-hatred / blasphemy* (non-US). Flag these under the nearest schema `risk_class` (usually `other` or `rights-clearance`) with a prose `escalation_trigger`; a dedicated code can be added later if they recur.

---

## Protocol

1. **Identify** the identifiable real people and quoted third-party material.
2. **Flag** each exposure (per §Detection guidance) as a `legal_risk` block — `risk_class`, `concern`, an `escalation_trigger` code from §Escalation-trigger taxonomy, and a `disposition` that *routes*, never *adjudicates*.
3. **Tier** by legal-escalation severity; every `review-now` item must route to counsel.
4. **Disclaim** — carry the not-a-lawyer statement at the top of the register.

## Mechanical check

`scripts/validate.sh legal-risk <run_folder>`: L1 schema, L2 unique ids, **L3 not-a-lawyer disclaimer present** (the signature gate); **W1 legal-advice drift** (a conclusion where a flag belongs — the firewall; override `<!-- override: legal-advice-drift LR-NN — … -->`), W2 a review-now item not routed to counsel. W1/W2 advisory, ERROR under `--strict`. Ownership boundary + lineage: [`docs/legal-risk-register.md`](../../../../../docs/legal-risk-register.md).
