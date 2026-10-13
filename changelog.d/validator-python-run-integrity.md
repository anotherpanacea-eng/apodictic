### Native Python run-integrity validators

Added native routes for escalation, dispatch records and reports, dispositions,
synthesis coverage and specificity floors. Existing helpers retain argument
order, discovery, defaults, strict behavior and blocking read errors. Tests cover
canonical runs and temporary hostile inputs. Specificity's existing self-test
prints random temporary paths, so its independent PASS checks do not claim exact
stdout parity. Gate and gate-state stay deferred until all native child routes
and both nested launchers are ready; aggregate cutover remains queued.
