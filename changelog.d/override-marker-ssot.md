### Validators — override-marker hardening

Closed the code-span-decoy override bypass fleet-wide. Eighteen validators
(`content-advisory`, `persona-divergence`, `intake-interview`, `author-fingerprint`,
`world-bible`, `continuity-bible`, `legal-risk`, `scene-ethics`, `retcon-plan`,
`state-card-diff`, `annotation-manifest`, `crosslink`, `argument-spine`,
`reader-instrument`, `promise-contract`, `regression-diff`, `style-explanation`,
`honesty-check`) carried their own `re.compile(r"<!--\s*override: …")` — seventeen
of them matching on **raw text**, so an override marker quoted inside a ``` fence or
an inline `code span` (a documentation example) was honored as a live directive.
They now route through the shared `override_marker` SSoT: new `override_targets`
(id- / pair- / presence-scoped) and `override_payloads` (free-text) helpers strip
code spans first and boundary-match the slug, so one module owns both stripping and
marker-matching. The meta-linter gains two gates so the class cannot re-enter: **M5**
now flags the compiled / inline override-marker regex form (not just the bare
substring), and **M6** flags a local code-span / fence stripper (delegate to
`override_marker.strip_code_spans`). The shared helpers match `override:` case-
sensitively (the old per-validator regexes were `re.IGNORECASE`); every shipped and
documented marker is lowercase, so this is a deliberate, inert tightening in the
fail-closed direction — an off-spec mixed-case marker no longer silences a finding.
