### Tooling — decoupled web-app UI generation

`release-generate.mjs` no longer reaches into the private APODICTIC-Gemini sibling
to write its `App.tsx` / `LandingPage.tsx`. That generation now lives in the app,
which **pulls** this repo's `release-registry.json` (vendored alongside the plugin)
and runs its own generator. apodictic's generator produces only its own docs;
removed the now-dead TS-emit helpers (−175 lines). Fixes the silent drift that
occurred whenever the sibling wasn't checked out during a release.
