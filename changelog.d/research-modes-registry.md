### Registry — research modes 4 → 6

`release-registry.json`'s `researchModes` array was missing two of the six modes it
claims in `counts.researchModes` and lists in `commands/research.md`: **Citation
Verification** (`citation-verifier`) and **Field Reconnaissance** (`field-recon`).
Added both (their backing reference docs already shipped), so the array matches the
count and the registry-derived web-app UI surfaces all six research modes.
