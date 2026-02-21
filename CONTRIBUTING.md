# Contributing to APODICTIC (Development Editor)

Thank you for your interest in improving this plugin. Contributions are welcome under the terms below.

## How to Contribute

**Bug reports and suggestions:** Email anotherpanacea@gmail.com with a clear description of the issue or idea. Include the plugin version and, if relevant, the audit or pass where the problem appeared.

**Audit improvements:** If you've found a false positive pattern, a missing diagnostic, or a calibration gap in a specific audit, describe the manuscript context where it occurred and what the audit missed or misflagged.

**New audit proposals:** Use the `Specialized_Audit_Expansion_Stub_TEMPLATE.md` included in the plugin to sketch your proposal. Send the completed stub to the email above.

## What We're Not Looking For

- Pull requests (this is a plugin, not a repository with PR infrastructure)
- Rewrites of core architecture without prior discussion
- Contributions that include copyrighted manuscript text

## Licensing

All contributions are licensed under the same terms as the plugin: **CC BY-NC-SA 4.0**. By submitting a contribution, you agree that your work may be incorporated under this license. You retain credit for your contribution (attribution will be noted in the changelog).

The copyright holder (Joshua A. Miller, PhD) retains the right to use contributions in commercial contexts. If this is a concern, note it when you submit.

## Style

- Diagnostic flags need detection logic, not just descriptions
- Name your flags (e.g., "EC-4: Static Heat," not "the scenes feel repetitive")
- Distinguish intentional craft choices from failures
- Include false positive warnings for anything that could misfire
- Follow the firewall: diagnostics identify problems; they don't rewrite manuscripts

## Changelog Policy

All changes that alter diagnostic behavior, output format, thresholds, flag definitions, pass logic, or the user-facing contract must be documented in `changelog.md`. Bug fixes, typo corrections, and internal refactoring that don't change behavior are encouraged but not required.

**Entry format:** `## vX.Y.Z - YYYY-MM-DD` with `### Changed`, `### Added`, or `### Fixed` subcategories. Entries should be specific enough to grep — name the file, flag, pass, or threshold that changed.

**Framing:** The changelog is a public document. Entries should describe what changed and how it affects users, not why changes were made.

**Version bumps:**
- Patch (x.y.**Z**): threshold adjustments, flag additions within existing modules, calibration refinements.
- Minor (x.**Y**.0): new audits, new genre modules, structural refactors, new commands.
- Major (**X**.0.0): reserved for architectural changes that break backward compatibility.

## Response Time

This is a solo-maintained project. Expect a response within a few weeks, not a few hours.
