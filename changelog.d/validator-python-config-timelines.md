### Native Python configuration and timeline validators

Added native dispatcher routes for quality-risk triggers, cost floors, audit-tier
criteria, pass headers, argument reconnaissance prerequisites and the three
timeline checks. Existing helpers retain defaults, flags, optional inputs and
file-error behavior; timeline-diff preserves both usage forms. Differential
checks cover eight added self-tests, 15 timeline fixtures, canonical inputs and
temporary default/strict/optional-input cases. Aggregate cutover remains queued.
