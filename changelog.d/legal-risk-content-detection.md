### Workflows — Legal Risk Register content-detection auto-recommend

The Legal Risk Register is now **auto-offered** for memoir / autofiction / nonfiction
portraying identifiable real people **without** an explicit `constraint:risk` flag. The
model reads the manuscript for the memoir / real-people signals (a mode signal — first-person
lived-experience retrospective, autofictional author-surrogate, or nonfiction naming/depicting
identifiable living people — plus at least one real-people content signal drawn from the module's
§Detection guidance: a reputational statement of fact about a living person; intimate private facts
about an identifiable private person; recognizable changed-name portrayal; quoted
lyrics/poetry/unpublished third-party writing; NDA/settlement-covered disclosure) and **offers**
the register. Per the maintainer's decision this is **prompt/router-only** — model-side detection
in the synthesis/routing prose, deliberately **not** a mechanical validator arm (no new validator,
no validator-count change). Offer-then-attach with an explicit confirm, and the
**flag-don't-practice-law** firewall is intact end to end: it flags/offers, never adjudicates, and
never auto-produces the register without confirm. Prose homes: `run-synthesis.md`
§Content-detection auto-recommend, `references/legal-risk-register.md` §Auto-recommend,
`intake-router-runtime.md` §3 D / §6 Table B, `pass-dependencies.md` §4a.
