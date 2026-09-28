### Plugin folder fits the Claude plugin directory's review limits

The plugin folder now meets the Claude plugin directory's automated file checks, which would
otherwise hold every version for a manual review. `validate.sh` is split into a short entry script
plus three sourced parts under `scripts/validate.d/`, so no file exceeds 256 KiB; commands, output
and exit codes are unchanged, and `check-mirror`, `validator-conventions` and `schema-coverage`
read the parts together. The changelog moved to the repo-root `CHANGELOG.md`, the `.docx`/`.pdf`
export goldens moved to `evals/fixtures/annotation-export/`, and nine unreferenced images moved
to `docs/assets/`, bringing the plugin to 509 files with no binary documents.
