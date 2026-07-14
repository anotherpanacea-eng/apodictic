#!/usr/bin/env python3
"""Verify the reconstructable fiction M2a Terra/Opus evidence package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[2]
MANIFEST = PACKAGE / "RUN-MANIFEST.md"
SCORES = PACKAGE / "SCORES.csv"
RUNNER = REPO / "evals/fixtures/fiction-benchmark/run.sh"
SOURCES = REPO / "evals/fixtures/fiction-benchmark/SOURCES.md"
FIXTURE_ROOT = REPO / "evals/fixtures/fiction-benchmark"
MODELS = ("terra", "opus")
EXPECTED_TOP_LEVEL = {
    "RUN-MANIFEST.md",
    "SCORECARD.md",
    "SCORES.csv",
    "outputs",
    "verify_package.py",
}
EXPECTED_SCORES_SHA256 = "963e9fa8247c0c78e336f743cfc7d16eeb7a283655adcc495f2823a04819bf24"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    raise ValueError(message)


def parse_manifest() -> dict[str, tuple[str, str, str]]:
    rows: dict[str, tuple[str, str, str]] = {}
    pattern = re.compile(
        r"^\| ([a-z0-9-]+) \| `([0-9a-f]{64})` \| `([0-9a-f]{64})` \| `([0-9a-f]{64})` \|$"
    )
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if not match:
            continue
        fixture, prompt_hash, terra_hash, opus_hash = match.groups()
        if fixture in rows:
            fail(f"duplicate manifest fixture: {fixture}")
        rows[fixture] = (prompt_hash, terra_hash, opus_hash)
    if len(rows) != 11:
        fail(f"manifest fixture count is {len(rows)}, expected 11")
    return rows


def check_package_shape(fixtures: set[str]) -> None:
    # Running Python verification may create an ignored bytecode cache; package
    # shape is about publishable artifacts, not interpreter-local residue.
    actual_top = {path.name for path in PACKAGE.iterdir() if path.name != "__pycache__"}
    if actual_top != EXPECTED_TOP_LEVEL:
        fail(f"unexpected package entries: {sorted(actual_top ^ EXPECTED_TOP_LEVEL)}")
    forbidden = re.compile(r"(^|[-_.])(prompt|err|stderr)([-_.]|$)", re.IGNORECASE)
    for path in PACKAGE.rglob("*"):
        if path.is_file() and forbidden.search(path.name):
            fail(f"forbidden prompt/stderr artifact included: {path.relative_to(PACKAGE)}")
    expected_outputs = {
        PACKAGE / "outputs" / model / fixture / "output.md"
        for model in MODELS
        for fixture in fixtures
    }
    actual_outputs = set((PACKAGE / "outputs").rglob("*.md"))
    if actual_outputs != expected_outputs:
        missing = sorted(str(p.relative_to(PACKAGE)) for p in expected_outputs - actual_outputs)
        extra = sorted(str(p.relative_to(PACKAGE)) for p in actual_outputs - expected_outputs)
        fail(f"output layout mismatch; missing={missing}, extra={extra}")


def check_outputs(manifest: dict[str, tuple[str, str, str]]) -> None:
    for fixture, (_prompt_hash, terra_hash, opus_hash) in manifest.items():
        for model, wanted in (("terra", terra_hash), ("opus", opus_hash)):
            path = PACKAGE / "outputs" / model / fixture / "output.md"
            data = path.read_bytes()
            if not data:
                fail(f"empty output: {path.relative_to(PACKAGE)}")
            if sha256(data) != wanted:
                fail(f"output hash mismatch: {path.relative_to(PACKAGE)}")
            nonblank = [line for line in data.decode("utf-8").splitlines() if line.strip()]
            if not nonblank or not nonblank[-1].startswith("RECOGNITION:"):
                fail(f"missing terminal recognition probe: {path.relative_to(PACKAGE)}")


def check_scores(fixtures: set[str]) -> None:
    # Freeze canonical fixture×FQ identity and metadata, not only aggregates; a
    # moved zero or invented FQ can preserve 111/114 while changing the result.
    if sha256(SCORES.read_bytes()) != EXPECTED_SCORES_SHA256:
        fail("SCORES.csv differs from the independently reviewed canonical score ledger")
    with SCORES.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 78:
        fail(f"score row count is {len(rows)}, expected 78 (2 x (38 Lane-1 + 1 FQ5))")
    if {row["fixture"] for row in rows} != fixtures:
        fail("score fixtures do not exactly match manifest fixtures")
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        key = (row["model"], row["fixture"], row["fq"])
        if key in seen:
            fail(f"duplicate score dimension: {key}")
        seen.add(key)
        if row["model"] not in MODELS:
            fail(f"unknown score model: {row['model']}")
        if row["score"] not in {"0", "1", "2", "3"} or row["max_score"] != "3":
            fail(f"invalid score scale: {key}")
    for model in MODELS:
        model_rows = [row for row in rows if row["model"] == model]
        lane1 = [row for row in model_rows if row["in_lane1_total"] == "true"]
        excluded = [row for row in model_rows if row["in_lane1_total"] == "false"]
        if len(model_rows) != 39 or len(lane1) != 38:
            fail(f"{model}: expected 39 rows with 38 Lane-1 rows")
        if len(excluded) != 1 or excluded[0]["fq"] != "FQ5" or excluded[0]["lane"] != "2":
            fail(f"{model}: only report-only Lane-2 FQ5 may be excluded")
        total = sum(int(row["score"]) for row in lane1)
        maximum = sum(int(row["max_score"]) for row in lane1)
        if (total, maximum) != (111, 114):
            fail(f"{model}: Lane-1 total is {total}/{maximum}, expected 111/114")


def parse_source_metadata() -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    hashes: dict[str, str] = {}
    anchors: dict[str, dict[str, str]] = {}
    slug = ""
    for line in SOURCES.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^### ([a-z0-9-]+)$", line)
        if heading:
            slug = heading.group(1)
            anchors.setdefault(slug, {})
            continue
        if not slug:
            continue
        recorded = re.search(r"sha256: ([0-9a-f]{64})", line)
        if recorded:
            hashes[slug] = recorded.group(1)
        anchor = re.match(r"- \*\*(BODY_START|BODY_END):\*\* `(.+)`", line)
        if anchor:
            anchors[slug][anchor.group(1)] = anchor.group(2)
    return hashes, anchors


def fixture_path(slug: str, source_dir: Path | None) -> Path | None:
    if source_dir:
        for suffix in (".md", ".txt"):
            candidate = source_dir / f"{slug}{suffix}"
            if candidate.is_file():
                return candidate
    direct = FIXTURE_ROOT / slug / "fixture.md"
    if direct.is_file():
        return direct
    for member in ("clean", "broken"):
        suffix = f"-{member}"
        if slug.endswith(suffix):
            candidate = FIXTURE_ROOT / slug[: -len(suffix)] / member / "fixture.md"
            if candidate.is_file():
                return candidate
    return None


def extract_body(path: Path, slug: str, anchors: dict[str, dict[str, str]]) -> str:
    text = path.read_text(encoding="utf-8").replace("\r", "")
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        closing = next((index for index, line in enumerate(lines[1:40], 1) if line.strip() == "---"), None)
        if closing is not None:
            lines = lines[closing + 1 :]
    body = "\n".join(lines).rstrip("\n")
    start = anchors.get(slug, {}).get("BODY_START")
    if start and start in body:
        body = body[body.index(start) :]
    end = anchors.get(slug, {}).get("BODY_END")
    if end and end in body:
        body = body[: body.index(end)]
    return body.rstrip("\n")


def runner_header() -> str:
    text = RUNNER.read_text(encoding="utf-8")
    match = re.search(r"read -r -d '' HEADER <<'EOF'\n(.*?)\nEOF", text, re.DOTALL)
    if not match:
        fail("could not extract blind prompt header from run.sh")
    return match.group(1)


def check_reconstruction(
    manifest: dict[str, tuple[str, str, str]], source_dir: Path | None
) -> tuple[int, list[str]]:
    source_hashes, anchors = parse_source_metadata()
    header = runner_header()
    checked = 0
    skipped: list[str] = []
    for slug, (wanted_prompt, _terra, _opus) in manifest.items():
        path = fixture_path(slug, source_dir)
        if path is None:
            skipped.append(slug)
            continue
        body = extract_body(path, slug, anchors)
        body_bytes = (body + "\n").encode("utf-8")
        wanted_body = source_hashes.get(slug)
        if not wanted_body or sha256(body_bytes) != wanted_body:
            fail(f"fixture body hash mismatch during reconstruction: {slug}")
        prompt = f"{header}\n\n<submission>\n{body}\n</submission>\n".encode("utf-8")
        if sha256(prompt) != wanted_prompt:
            fail(f"reconstructed prompt hash mismatch: {slug}")
        checked += 1
    return checked, skipped


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-dir",
        type=Path,
        help="optional cache containing christmas-carol-arc-control.md/.txt",
    )
    args = parser.parse_args()
    try:
        manifest = parse_manifest()
        fixtures = set(manifest)
        check_package_shape(fixtures)
        check_outputs(manifest)
        check_scores(fixtures)
        reconstructed, skipped = check_reconstruction(manifest, args.source_dir)
    except (OSError, UnicodeError, ValueError, csv.Error) as error:
        print(f"FAILED: {error}", file=sys.stderr)
        return 1
    print("OK: 11 unique fixtures; 22 hashed outputs; no prompt/stderr artifacts")
    print("OK: 76 Lane-1 score rows = 111/114 per model; 2 FQ5 rows report-only")
    print(f"OK: reconstructed and hash-verified {reconstructed}/11 fixture prompts")
    if skipped:
        print("SKIP: source bytes unavailable for " + ", ".join(sorted(skipped)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
