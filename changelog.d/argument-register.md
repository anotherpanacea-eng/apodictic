### Argument Register

- Add writer-confirmed AT5 generative/lens routing with GN0–GN4 diagnostics, explicit
  high-stakes precedence, and per-cash-out asserted-burden records.
- Version Argument State Schema as v0.3.0 and extend argument-spine/Argument_State
  contracts so register calibration remains inspectable and never silently bypasses the
  Deficit Lock.
- Close the E7 hybrid gate with two independent strict blind records whose canonical cash-out
  joins preserve generative treatment for the journey and full asserted burden for the policy
  landing; both vendored ledger/state pairs pass `stance-calibration` and are exercised by
  `validate.sh --check-all`.
