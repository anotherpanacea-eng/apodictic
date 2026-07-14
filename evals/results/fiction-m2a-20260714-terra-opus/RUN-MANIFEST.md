# Fiction M2a Run Manifest — Terra + Opus

**Run date:** 2026-07-14
**Repository base:** `05711df1109b80475ffc7e3608edf7740b9c89e8`
**Package status:** reconstructable committed evidence; 22/22 nonempty outputs, 22/22 terminal recognition probes, prompt identity verified per fixture

## Source trees

- Terra: `evals/results/fiction-run-20260714-144857`
- Opus: `evals/results/fiction-run-20260714-145217`
- Score package: `evals/results/fiction-m2a-20260714-terra-opus`

The arms ran separately because authenticated provider availability was resolved
between launches. This manifest binds them into one M2a package. The corresponding
Terra and Opus prompt hashes below are byte-identical for every fixture.

## Packaged layout

- `SCORECARD.md` — human scoring rationale and convergence decision.
- `SCORES.csv` — 38 Lane-1 dimensions per model plus one report-only FQ5 row
  per model.
- `outputs/{terra,opus}/<fixture>/output.md` — the 22 historical raw model
  responses, copied byte-for-byte from the source run trees.
- `verify_package.py` — stdlib-only integrity, score, and reconstruction checks.

Prompts, provider stderr, and fixture/source bytes are deliberately excluded.
Where committed fixture bodies are locally available, the verifier rebuilds the
blind prompt from `run.sh` and checks it against the historical prompt hash. The
referenced Dickens prompt can additionally be checked by passing a source cache:

```bash
python3 evals/results/fiction-m2a-20260714-terra-opus/verify_package.py
python3 evals/results/fiction-m2a-20260714-terra-opus/verify_package.py \
  --source-dir "/path/to/fiction-benchmark-sources"
```

## Provider identity

| Config | Concrete model | Effort / mode | CLI |
|---|---|---|---|
| Terra | `gpt-5.6-terra` | `high` reasoning | `codex-cli 0.144.0` |
| Opus | `claude-opus-4-8` | standard, fast mode off | `Claude Code 2.1.209` |

The Opus arm was invoked with the rolling `opus` alias. A post-run JSON identity
probe on the same authenticated CLI resolved that alias to `claude-opus-4-8`;
future runner invocations pin the concrete id directly.

## Artifact hashes

SHA-256 columns are prompt, Terra output, and Opus output.

| Fixture | Prompt | Terra output | Opus output |
|---|---|---|---|
| christmas-carol-arc-control | `ec0116e30973d14b516bd54b3dd5ea97072209918c9b2a5115a52898035cf08f` | `54f1b0c061fb421ff82c54b0828299c6356886fddebf74ba73ba53cab30d1e31` | `98f981b9e058c8b5f199ae2dacc35ec875ed3795f8035aca9701ecb03c4e5781` |
| yellow-wallpaper-voice-control | `85da2ed384b82f330eee668003ed6c579869d09388b3a1f1f60283956683377d` | `ddc860c53cca4e47e267a9e151a17770c8305aa73dedce06307436edb322b6be` | `898b0afaba8bbe2e11390da324469e2a123491501315a50e90de384536e98475` |
| gift-of-magi-reveal-control | `ac149dc3ac1d57dda2478a5ef367a9c83b837d67e056c14af21ce3b4b049a0f8` | `f22e511dd9a4b492dcdd9c5d8fb7b24320c11694533262fb15f3ea13113c5ee1` | `a5c9542684398597d5026ec6b1cba4be8d5cfd49fa07fd213a1748d4a86b2ca4` |
| pov-break-clean | `9da65a5f2b0974a2b99ccc2b7308219cc735b5c77ad1938c84bd2862c0c56888` | `3ff93ccc41be4711564bd721b628e53bf6fe1829c7ffce4a4025ff1cccd9062c` | `4a4498de37fa7dbee33a70d3225e23cf1f17f1a6d9258f1d8c530ba24ea38deb` |
| pov-break-broken | `94b5cde15e4d59418d1c910d6997e06d4bc9ddac844aa5f54a44d3185f913472` | `a6caaaa6d2db2b68cceddf3f5cb89d3fb1c2e63f60909908eed99c78e866a237` | `9e461654f21a9d1be0ba0cd5f87cb2a4f80db6fd07db48a9042f84bcd52feb5f` |
| continuity-contradiction-clean | `fc6513808dce7a85cdbc0f2cc618670bdce1c9f162cc6e8b7bdcbc5a716a3920` | `f59f9b8dcd4f425e71e583e4c929fd3908251e5e2092cdc0adb6f408d57ef784` | `e72d345dc5845635e0c67b44b73faec5f3d27c35bb0db0ed506d18cff8fa67fb` |
| continuity-contradiction-broken | `179e2472149a609b65e2b1009a0dcd380b6c4bbf0ad74ec294f1dc721655d945` | `b4964267f467c2818976c4fbdffd0a632db15fdbf1b872d1d5c0b6af23151308` | `082591210b7f5f024efb65b85f1d13267c32f17fa94ab86a301f6a3204848b88` |
| unpaid-setup-clean | `9049017acaadcfd1c94b561323e8b9568663ae7c47b789aca9ce3ed4d425bd08` | `113210b1f5379fc82fe4d7b28166b948b85ed0bebd50f1df2228b4566e56baf8` | `8cd6335adc32f4c01bc82ba785ff51cf88f5abdf255cad1c58aa34eba485ef78` |
| unpaid-setup-broken | `a9969561d7d61e41c0d964a6e7468b1fe2c5e5eb0e4db24716cbe9097095c0c5` | `4bdefbfbab8541f0e1f777acf337beb2fcd2a7d32878d1afc45ed5cb80fdac65` | `bd70a66000fc6739fc1640bc0b6e87f270749fb46e386def331ac9c406410467` |
| orphan-scene-clean | `500d77beaf1b15b966eae39e02c1276479b335ccc59b57f9801aa4e7c80929b8` | `8b6a9b758af61c41ec393ce0b90a1f52d451efe9dc7e5301005ec0f711526526` | `271993136544fdbc123cd69ee0a25cc0b928f6a85662f8bee24346f840ec5318` |
| orphan-scene-broken | `9e0263dda7fa5115bcc73cc0f225e2921e3f69b3a19e18099a697912ffbdb48c` | `bef1a8065d91e3b51cc0cc539f4a488a522ac91ac44a765336a7da2c5db1083f` | `4eda7bdc263698fe99ca334e7570b4c9ed05afd26b0199f2d533d1b33da8c7c7` |

## Validation and caveats

- Committed package verifier: 11 unique fixtures; 22/22 output hashes; 76
  Lane-1 score rows + 2 report-only FQ5 rows; no packaged prompt/stderr files;
  local prompt reconstruction for every available fixture body.
- Strict fixture verification: 11/11.
- Prompt identity: 11/11 pairs byte-identical.
- Output contract: 22/22 nonempty; 22/22 final nonblank lines are `RECOGNITION:` probes.
- Full repository gate: `scripts/validate.sh --check-all` PASS, including 82/82 validator self-tests.
- Published controls were recognized by both models and are recall-susceptible corroborating evidence, as preregistered. Synthetic pair members were not recognized.
- The Terra wrapper printed a shell syntax error only after all 11 provider calls had completed because `run.sh` was edited concurrently. Direct artifact checks verified every provider transcript ended in a Codex token total and every output passed its contract. No Terra result was rerun or replaced.
- One Terra stderr transcript contains a harmless shell-snapshot cleanup warning; it does not affect the model response.
