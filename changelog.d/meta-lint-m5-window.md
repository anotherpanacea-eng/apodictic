### Faster M5 override-hygiene scan

Anchor validator-conventions' M5 Python scan on literal `<!--` occurrences instead of running the four-alternative override-marker regex from every position of every sibling script. Same verdicts (self-test cases guard the windowed semantics, including whitespace-gap and deep-offset forms); the canonical CI gate drops from ~28s to ~15s locally.
