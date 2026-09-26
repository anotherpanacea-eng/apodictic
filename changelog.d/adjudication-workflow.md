### Author adjudication workflow (partial Increment 2)

Add `/adjudicate` with verified progress/history presentation, explicit author
approval/rejection/revision, reasoned un-rejection and Inclusion changes, atomic
edge cascades, and head-bound crash-safe resume. All writes reuse the existing
ledger engine. Nonempty exclusions fail closed while compatible semantic
screening is unavailable; the workflow does not draft or certify acceptance.
