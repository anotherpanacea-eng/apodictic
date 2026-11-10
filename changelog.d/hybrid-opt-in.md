### Execution — Hybrid mode is author opt-in only

Hybrid now runs only when the author asks for it. Pre-flight no longer recommends it for 60–100K
words on standard-context hosts (sequential covers everything under 100K), the intake menu no
longer offers it, and the mid-run escalation check never proposes it. Quality-risk triggers Q1
(consent/governance) and Q2 (argument-shaped + high stakes), whose only target was hybrid, are
retired; Q3 now fires only at six or more POVs (swarm). The finding disconfirmation pass and the
evidence spot-check now run in their own subagent in every mode, single-agent included, because
both depend on the checker not being the author of the findings. The hybrid machinery stays
available. Evidence: a hybrid Full DE on an 86K-word novel cost ~4.3M subagent tokens against a
460K estimate.

Also adds the `fable52` row (Claude Fable 5.2) to the model-tag table.
