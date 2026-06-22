#!/usr/bin/env python3
"""
test_content_advisory_registration.py — discoverability regression guard for
the Content-Advisory specialized-audit module (apodictic#126).

APODICTIC has no pytest suite (AGENTS.md § CI), so this is a self-contained
runner: `python3 tests/skill-registration/test_content_advisory_registration.py`
exits 0 iff every case passes, nonzero otherwise.

WHY THIS EXISTS
---------------
PR #126 homes the reference module at
`plugins/apodictic/skills/specialized-audits/references/content-advisory.md`
and its docs say it is "homed alongside the Reception-Risk audit." But a
reference module is only DISCOVERABLE if its owning skill (specialized-audits)
registers it on two surfaces, exactly as the author-fingerprint (#9) and
reception-risk siblings are:

  (1) the skill `description` frontmatter — the trigger surface that routes a
      user request to this skill. content-advisory needs its OWN trigger
      phrases ("content advisory" / "content warning" / "content note" /
      "trigger warning"); reusing reception-risk's "sensitivity read" would
      MIS-ROUTE the request to the Reception Risk audit — the very module the
      content-advisory spec says it is "Not."
  (2) the reference-module registry list under "## Reference Files", where the
      sibling `references/craft/reception-risk.md` is listed. The module file
      must also actually exist (no dangling registry pointer).

Against pre-fix origin/feat/content-advisory both (1) and (2) are absent
(grep -ic 'content-advisory' SKILL.md -> 0), so this runner FAILS there and
PASSES after the registration is added. It is a paper-trail/registration
gate, not a behavioral test of content_advisory.py.
"""

from __future__ import annotations

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "plugins" / "apodictic" / "skills" / "specialized-audits"
SKILL_MD = SKILL_DIR / "SKILL.md"
# Path as written in the registry entry, resolved relative to the skill dir.
MODULE_REL = "references/content-advisory.md"
MODULE_ABS = SKILL_DIR / MODULE_REL

# Trigger phrases that MUST appear in the description frontmatter. These route
# specifically to content-advisory and are distinct from reception-risk's
# "sensitivity read" / "cultural sensitivity".
REQUIRED_TRIGGERS = (
    "content advisory",
    "content warning",
    "content note",
    "trigger warning",
)

_failures: list[str] = []


def _check(name: str, ok: bool, detail: str = "") -> None:
    status = "ok  " if ok else "FAIL"
    line = f"  {status} {name}"
    if detail and not ok:
        line += f" -> {detail}"
    print(line)
    if not ok:
        _failures.append(name)


def _frontmatter(text: str) -> str:
    """Return the YAML frontmatter block (between the first two '---' fences)."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        raise AssertionError("SKILL.md has no YAML frontmatter block")
    return m.group(1)


def main() -> int:
    print(f"content-advisory registration guard ({SKILL_MD.relative_to(REPO_ROOT)})")

    _check("SKILL.md exists", SKILL_MD.is_file(), str(SKILL_MD))
    if SKILL_MD.is_file():
        text = SKILL_MD.read_text(encoding="utf-8")
        fm = _frontmatter(text)
        fm_lower = fm.lower()
        body = text[len(fm):]

        # Surface (1): description-frontmatter trigger phrases.
        for phrase in REQUIRED_TRIGGERS:
            _check(
                f"description frontmatter contains trigger {phrase!r}",
                phrase in fm_lower,
                "trigger phrase missing from description: request will not route here",
            )

        # Surface (2): reference-module registry list entry (in the BODY, not
        # the frontmatter), mirroring the reception-risk sibling registration.
        _check(
            f"registry list registers {MODULE_REL!r}",
            MODULE_REL in body,
            "module absent from the '## Reference Files' registry list",
        )

        # Sanity: the sibling we mirror is genuinely registered, so a future
        # whole-list deletion can't make this test vacuously pass.
        _check(
            "sibling references/craft/reception-risk.md still registered (non-vacuity)",
            "references/craft/reception-risk.md" in body,
        )

    # The registry pointer must resolve to a real module file (no dangling ref).
    _check(
        f"registered module file exists ({MODULE_REL})",
        MODULE_ABS.is_file(),
        str(MODULE_ABS),
    )

    print()
    if _failures:
        print(
            f"content-advisory registration guard: FAIL "
            f"({len(_failures)} check(s) failed: {', '.join(_failures)})"
        )
        return 1
    print("content-advisory registration guard: PASS (all surfaces registered)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
