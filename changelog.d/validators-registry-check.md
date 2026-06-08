### Validators

35 → 36 self-testable validators. Added `registry-check` (project-registry integrity over a workspace-relative `.apodictic/registry.json`: R1 envelope + per-entry schema, R2 root + sidecar resolution, R3 cache-vs-sidecar drift with the sidecar canonical, R4 duplicate id), backed by the new `apodictic.project_registry.v1` + `apodictic.project_entry.v1` schemas. Mirrored into the root `scripts/` harness that CI runs.
