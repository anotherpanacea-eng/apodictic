### CI

Cut CI that tested CI. Removed the train checker, CI receipts, pull-request merge
binding, sync-PR draft enforcer, status-drift lint and inventory-parity marker check,
with their policy tests. CI now runs on any non-draft PR (drafts start nothing). The
`@claude` workflow safety tests, Windows native gate, SETEC drift gate and validator
inventory check stay.
