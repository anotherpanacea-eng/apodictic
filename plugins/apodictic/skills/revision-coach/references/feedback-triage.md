# Feedback Triage — workflow protocol

*Reference file for the APODICTIC Revision Coach. Loaded by `/triage-feedback` (and `/coach` → Feedback Triage mode). For writers returning with external feedback. Spec + validator: `docs/feedback-triage.md`, `scripts/validate.sh feedback-triage`. Worked example: `../../core-editor/references/example-feedback-triage.md`.*

---

## When to use

A writer comes back after circulating the draft with a pile of **external** feedback — beta readers, a critique group, an agent or editor. The feedback is typically:

- **Contradictory** — one reader says cut the prologue, another says expand it.
- **Uneven** — a sharp structural observation next to a taste preference.
- **Unvalidated** — claims that may or may not survive contact with the manuscript and the diagnosis.

The goal is **not to obey the feedback**. It is to sort it, check each claim, prioritize, and resolve the contradictions — so the writer spends revision time on what is real and decided, not on whoever spoke last.

## Firewall (inherited, restated)

The coach **structures and prioritizes**; it does **not** validate claims by re-diagnosing. Validating "does the midpoint actually sag?" is a **targeted Core Editor pass**, not a coaching act. When a claim needs checking, run or recommend the specific pass (`/diagnose` targeted) and read its result back into the triage. A claim the diagnosis confirms is a **candidate finding** — it enters the Findings Ledger, where its severity is governed normally. This keeps Guidance Without Specification intact: the coach never invents the diagnosis behind a piece of feedback.

## The structured record

Each note becomes one `apodictic.feedback_item.v1` block (HTML-comment envelope, real JSON, same engine as `apodictic.finding.v1`) in `[Project]_Feedback_Triage_[runlabel].md`. Two **orthogonal** axes — keep them separate:

- **`assessment`** (did our analysis confirm the claim?): `validated` · `partly-validated` · `refuted` · `unverifiable` · `pending`.
- **`triage`** (what we'll do): `act-now` · `act-later` · `monitor` · `decline`. **Not** the Must-Fix/Should-Fix/Could-Fix severity scale — severity lives on the finding a validated claim maps to.

Fields: `schema`, `id` (`FB-<NN>`, unique), `source`, `claim`, `assessment`, `triage`, `conflicts_with` (ids this item contradicts), `evidence_refs` (optional), `disposition` (one sentence: what we'll do / why declined). Canonical field set: `schemas/apodictic.feedback_item.v1.schema.json`.

## Protocol

1. **Intake & structure.** Capture every external note verbatim as a `feedback_item` with `source` + `claim`. Start each at `assessment: pending`, `triage: monitor`. Do not pre-judge.
2. **Validate.** For each claim, run/recommend a **targeted** pass to confirm or refute it; set `assessment` from the result. Group near-duplicate notes under one item (keep the sources in `source`).
3. **Map to findings.** A `validated` / `partly-validated` claim that names a real defect becomes (or links to) an `apodictic.finding.v1` in the ledger; record the link in `disposition`.
4. **Resolve conflicts.** For each contradiction, set `conflicts_with` on (at least) one side and **decide**: keep one and `decline` the other, or `monitor` both pending more information. Never leave both sides `act-now`/`act-later` — that is an unresolved conflict (W1).
5. **Triage & sequence.** Set `triage` per item. Don't `act-now` on an item that isn't at least `partly-validated` (W2) unless you're deliberately trusting the source ahead of validation — note why in `disposition`.
6. **Gate & hand off.** Run `scripts/validate.sh feedback-triage <run_folder>` (`--strict` for CI). Resolve ERRORs (broken contract, dangling/self conflict reference); review W1/W2. Hand the **act-now** set to Session Planning (`/coach`) as the next session's targets.

## Output

`[Project]_Feedback_Triage_[runlabel].md`:
- **Author-facing summary** — plain-language recap: what came in, what's confirmed, what's declined and why, what's parked.
- **Triaged feedback** — the prose list, each item carrying its `feedback_item` block. Resolved contradictions are visible (one side declined/parked).
- **Next session targets** — the act-now items, sequenced, ready for `/coach`.

See `../../core-editor/references/example-feedback-triage.md` for a contract-conformant worked example (a resolved prologue contradiction; an unverified note parked at `monitor`).

## Degrade path

Without `python3`, `feedback-triage` is advisory: perform the checks inline — every `conflicts_with` id resolves to a real item, no item conflicts with itself, and no contradiction is left actionable on both sides. The blocks stay human-readable.
