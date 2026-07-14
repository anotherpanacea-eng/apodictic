### Faster CI without weaker gates

Run validator self-tests, canonical-framework checks, and static/build checks in parallel behind the existing required `validate` result. The aggregate validator also avoids executing the shared `gate`/`gate-state` self-test suite twice.
