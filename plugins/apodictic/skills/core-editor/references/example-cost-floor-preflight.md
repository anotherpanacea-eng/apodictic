# APODICTIC Pre-flight Metadata (cost-floor worked example)

<!--
Canonical preflight packet paired with example-cost-floor-contract.md for the `cost-floor`
validator. It represents a ~118K-word standard-context manuscript: the standard-context token-fit
floor is swarm (so the recorded sequential cap sits BELOW it — the below-floor tradeoff the cap
discloses, surfaced by the CF3 below-floor WARN), while the estimated single-agent load is well
under the 600K bound. `cost-floor` reads the `Estimated single-agent load:` line (CF3 single-agent
load bound) and the standard-context floor line (CF3 below-floor WARN). This packet is a static
fixture, not a generated one; the per-mode cost estimate section that `preflight.sh` now emits is
exercised separately in the build's preflight verification step.
-->

## Manuscript
- **File:** the-salt-year.md
- **Estimated words:** 118000

## Token Load Estimate
- **Estimated manuscript tokens:** 157000
- **Estimated single-agent load:** 232000 (manuscript + ~75K overhead)

## Dispatch Recommendations
- **Large-context mode (>=1M tokens):** single-agent
- **Standard-context mode (<1M tokens):** swarm
- **Triage subagent max_turns:** 34
- **Large-context threshold:** single-agent if estimated load < 600K tokens; sequential otherwise
- **Standard-context thresholds:** <60K words → sequential; 60-100K → hybrid; >100K → swarm
