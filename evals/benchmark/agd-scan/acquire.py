#!/usr/bin/env python3
"""acquire.py — R3B §4 Phase-1 ACQUISITION (online, run once, artifacts committed).

For each of the 5 R3A fixtures x 2 vendors (fable = claude-fable-5; codex =
gpt-5.6-sol at extra-high reasoning) x N=2 reps, runs the LIVE judge against the
fixture's ``source.md`` through the consumer channel (the `ai_prose_agd_move_scan`
shim -> SETEC dispatcher -> `agd_move_scan --judge agent_host`, with
``host_judge_cmd.py`` as the blind per-vendor transport) and stores the
run-manifest at ``manifests/<fixture>--<vendor>--rep<1|2>.json``:

    {"fixture_id", "vendor", "model_id", "prompt_fingerprint_sha256",
     "rep", "acquired_at", "values": {"observations": [...]}}

— the schema pinned in README.md and read TOP-LEVEL-first by the producer's
manifest judge, so Phase-2 replays each artifact offline forever
(``--judge manifest --judge-manifest <artifact> --expect-fingerprint <fp>``).

The stored observations are the producer-normalized set (span-integrity drops
already applied); every drop warning from acquisition is appended to
``acquisition-log.md`` so nothing is silently lost. Reps are independent fresh
subprocesses; identical reps are themselves calibration data.

Usage (repo root):
    python3 evals/benchmark/agd-scan/acquire.py [--vendor fable|codex] \
        [--fixture NAME] [--rep 1|2] [--force]

Without filters, acquires every missing cell (existing manifests are SKIPPED
unless --force — acquisition is run-once; re-running must not silently
regenerate committed artifacts).
"""
import argparse
import datetime as _dt
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
SHIM = (REPO / "plugins/apodictic/skills/specialized-audits/scripts/"
        "ai_prose_agd_move_scan.py")
FIXTURES_DIR = REPO / "evals/fixtures/argument-agd"
MANIFESTS = HERE / "manifests"
LOG = HERE / "acquisition-log.md"

FIXTURES = (
    "abusive-cued-assurance",
    "ambiguous",
    "cue-free-structural-discounting",
    "cue-only",
    "legit-guarded-generalization",
)
# vendor -> (SETEC_HOST, SETEC_HOST_MODEL)
VENDORS = {
    "fable": ("claude-code", "claude-fable-5"),
    "codex": ("codex-cli", "gpt-5.6-sol"),
}
REPS = (1, 2)


def acquire_cell(fixture: str, vendor: str, rep: int, scratch: Path) -> dict:
    host, model = VENDORS[vendor]
    src = FIXTURES_DIR / fixture / "source.md"
    if not src.exists():
        raise SystemExit("missing fixture source: %s" % src)
    env = dict(os.environ)
    env.update({
        "JUDGE_VENDOR": vendor,
        "SETEC_HOST": host,
        "SETEC_HOST_MODEL": model,
        "SETEC_HOST_JUDGE_CMD": "python3 %s" % (HERE / "host_judge_cmd.py"),
        "SETEC_HOST_JUDGE_TIMEOUT": "900",
    })
    out_json = scratch / ("%s--%s--rep%d.envelope.json" % (fixture, vendor, rep))
    out_md = scratch / ("%s--%s--rep%d.envelope.md" % (fixture, vendor, rep))
    proc = subprocess.run(
        [sys.executable, str(SHIM), str(src), "--judge", "agent_host", "--json",
         "--out", str(out_json), "--out-md", str(out_md)],
        capture_output=True, text=True, env=env, timeout=1000, cwd=str(REPO))
    if proc.returncode != 0:
        raise RuntimeError("shim failed (%s--%s--rep%d): %s" %
                           (fixture, vendor, rep, (proc.stderr or proc.stdout)[:500]))
    envelope = json.loads(proc.stdout)
    if not envelope.get("available"):
        raise RuntimeError("envelope unavailable (%s--%s--rep%d): %s" %
                           (fixture, vendor, rep, envelope.get("reason")))
    r = envelope["results"]
    ji = r["judge"]["judge_identity"]
    manifest = {
        "fixture_id": fixture,
        "vendor": vendor,
        "model_id": ji.get("model") or model,
        "prompt_fingerprint_sha256": r["prompt_fingerprint_sha256"],
        "rep": rep,
        "acquired_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "values": {"observations": r["judge"]["values"]["observations"]},
    }
    drops = [w for w in envelope.get("warnings", []) if w.startswith("Span integrity:")]
    return {"manifest": manifest, "drops": drops,
            "n_obs": len(manifest["values"]["observations"])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vendor", choices=sorted(VENDORS), default=None)
    ap.add_argument("--fixture", choices=FIXTURES, default=None)
    ap.add_argument("--rep", type=int, choices=REPS, default=None)
    ap.add_argument("--force", action="store_true",
                    help="re-acquire even if the manifest exists (run-once discipline: "
                         "committed artifacts are never silently regenerated)")
    args = ap.parse_args()

    MANIFESTS.mkdir(parents=True, exist_ok=True)
    scratch = HERE / "_scratch"
    scratch.mkdir(exist_ok=True)
    log_lines = []
    done = skipped = 0
    for fixture in FIXTURES:
        if args.fixture and fixture != args.fixture:
            continue
        for vendor in sorted(VENDORS):
            if args.vendor and vendor != args.vendor:
                continue
            for rep in REPS:
                if args.rep and rep != args.rep:
                    continue
                path = MANIFESTS / ("%s--%s--rep%d.json" % (fixture, vendor, rep))
                if path.exists() and not args.force:
                    skipped += 1
                    continue
                print("acquiring %s--%s--rep%d ..." % (fixture, vendor, rep),
                      flush=True)
                cell = acquire_cell(fixture, vendor, rep, scratch)
                path.write_text(json.dumps(cell["manifest"], indent=2) + "\n",
                                encoding="utf-8")
                stamp = cell["manifest"]["acquired_at"]
                log_lines.append("- `%s` — %d observation(s), %d span-integrity drop(s)%s"
                                 % (path.name, cell["n_obs"], len(cell["drops"]),
                                    (":\n" + "\n".join("  - %s" % d for d in cell["drops"]))
                                    if cell["drops"] else ""))
                log_lines.append("  acquired_at %s" % stamp)
                done += 1
    if log_lines:
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(log_lines) + "\n")
    print("acquired %d cell(s), skipped %d existing" % (done, skipped))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
