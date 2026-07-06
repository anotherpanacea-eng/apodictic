#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared editorial-severity-token vocabulary for the APODICTIC validator fleet — the SSoT.

The editorial severity tokens `Must-Fix`, `Should-Fix`, and `Could-Fix` name the three bands of the
Findings Ledger's defect language. Several *descriptive* surfaces are firewalled from ever emitting
that language: they describe the manuscript, they never diagnose it. Their gates therefore scan their
own output for a leaked severity token and FAIL if one appears. The pattern that recognizes the token —

    \\b(?:Must|Should|Could)-Fix\\b

— was hand-copied into every such gate (the A3 Content-Advisory firewall, the X-gate Author-Style /
Author-Voice firewalls, the results-guide navigation-index guard, the setup-payoff / contradiction-state
fact-register guards). Six byte-identical copies had accumulated by 2026-07-06, kept in sync only by
comments that pointed at one another ("copied from content_advisory._SEVERITY_RE") — the exact
hand-synced-copy class the meta-linter exists to prevent (a second copy is the signal to abstract). A
seventh was forming on an open PR. This module is the SINGLE source of truth for that pattern.

`SEVERITY_TOKEN_RE` — the compiled, word-boundary-anchored pattern. It matches ONLY the bare capitalized
token form (`Must-Fix` / `Should-Fix` / `Could-Fix`), which is the A3/X-gate leak vocabulary. It is
DELIBERATELY narrow — case-sensitive, boundary-anchored — and is NOT the pattern for the other
severity-shaped surfaces in the fleet, which need their own grammars and keep their own patterns:
  * `editor_scaffolding.SEVERITY_RE`      — lookaround form with capture groups (parses tokens out)
  * `honesty_check` / `structured_findings.PROSE_SEVERITY_RE` — context-prefixed, Must/Should only
  * `letter_checks` / `disposition_check` — IGNORECASE, multi-word phrase, or caveat-line forms
None of those consumes this constant; M8 does not force them to.

Consumers (import `SEVERITY_TOKEN_RE`, do NOT re-`re.compile` the pattern locally):
  content_advisory.py · results_guide.py · contradiction_state.py · setup_payoff_checks.py ·
  style_explanation.py · author_fingerprint.py

Meta-lint M8 (`meta_lint.py`, `docs/validator-conventions.md`) BANS a local re-definition of this
pattern: any `re.compile` whose literal carries the `(?:Must|Should|Could)` severity alternation is a
violation everywhere except this file. Prose mentions of "Must-Fix" in a docstring / string / comment
do NOT trip it — only a regex-literal re-definition does.
"""
import re

# The editorial-severity leak token, word-boundary-anchored. SINGLE SOURCE OF TRUTH — see module
# docstring. `\b` on both sides so `Must-Fix` is matched but `Not-a-Must-Fixture` is not.
SEVERITY_TOKEN_RE = re.compile(r"\b(?:Must|Should|Could)-Fix\b")
