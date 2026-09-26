### Argument benchmark fetch publication

Stage fetched and converted argument text before replacing cached output. Conversion,
extraction, staging and digest failures preserve the previous destination; recorded
digest mismatches no longer overwrite it. Sources without a recorded digest still
publish with an explicitly unverified `GOT` notice. Per-source cleanup retains every
temporary path through ordinary failures and catchable signals. Synthetic offline
regressions cover the PDF converter and shared publication path. This does not claim
power-loss durability or real-manuscript extraction quality.
