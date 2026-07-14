#!/usr/bin/env python3
"""Build the access-controlled shared argument + fiction blind-editor packet."""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
from pathlib import Path

from panel_schema import ARGUMENT_UNITS, FIELDS, FICTION_UNITS

ARGUMENT = (
    ("A01", "piece-1.txt", "cato-industrial-policy-bad-idea", "e4c3a864d98a51147c71e808fa60d8fc4a8a33c05ec694c39de9ac81f3d3b4be"),
    ("A02", "piece-2.txt", "ppi-one-size-fits-none", "7339bdfa3fa3f57ef1e2b1e1a68f9f7e50384ea99b1b0db59d17ad420d1f24b4"),
    ("A03", "piece-3.txt", "roosevelt-democratic-abundance", "b88a1af9c9db35f9c6d766d53d0e2a7344c11a1a36571c603fd9dd325175b573"),
    ("A04", "piece-4.txt", "reason-problem-with-abundance-agenda", "6b8299c2d7b2adbdba0ccea1eaac42b577af62d4ba39faa795f82668820468d9"),
    ("A05", "piece-5.txt", "current-affairs-abandon-abundance", "c9d07a74e2fd2ebc131f1d51e79109f8da2aa72976bb7e014d4410eab337f954"),
)
FICTION = (
    ("F01", "christmas-carol-arc-control", "public-domain"),
    ("F02", "yellow-wallpaper-voice-control", "public-domain"),
    ("F03", "gift-of-magi-reveal-control", "public-domain"),
    ("F04", "orphan-scene-clean", "synthetic"),
    ("F05", "pov-break-clean", "synthetic"),
    ("F06", "unpaid-setup-clean", "synthetic"),
    ("F07", "continuity-contradiction-clean", "synthetic"),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def paragraphs(data: bytes) -> list[str]:
    text = data.decode("utf-8").replace("\r\n", "\n").strip()
    return [" ".join(block.splitlines()) for block in text.split("\n\n") if block.strip()]


def numbered(data: bytes) -> tuple[bytes, int]:
    blocks = paragraphs(data)
    rendered = "\n\n".join(f"[P{i:03d}] {block}" for i, block in enumerate(blocks, 1)) + "\n"
    return rendered.encode(), len(blocks)


def prompt_submission(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8")
    start, end = "<submission>\n", "\n</submission>"
    if text.count(start) != 1 or text.count(end) != 1:
        raise SystemExit("ERROR: fiction prompt must contain exactly one submission block")
    return (text.split(start, 1)[1].split(end, 1)[0] + "\n").encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--argument-source-dir", type=Path, required=True)
    parser.add_argument("--fiction-prompt", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"ERROR: output already exists: {args.output}")
    packet = args.output / "packet"
    sources = packet / "sources"
    operator = args.output / "operator-only"
    sources.mkdir(parents=True)
    operator.mkdir(parents=True)

    rows = []
    for unit, filename, slug, expected in ARGUMENT:
        raw = (args.argument_source_dir / filename).read_bytes()
        if sha(raw) != expected:
            raise SystemExit(f"ERROR: stale/changed source {filename}: {sha(raw)} != {expected}")
        rendered, count = numbered(raw)
        dest = sources / f"{unit}.txt"
        dest.write_bytes(rendered)
        rows.append((unit, "argument", slug, "third-party-access-controlled",
                     "OPERATOR_CONFIRMATION_REQUIRED", expected, sha(rendered), count,
                     f"archived-v0.1-stripped-source/{filename}",
                     f"evals/fixtures/argument-benchmark/{slug}/groundtruth.md"))

    fixture_paths = {
        "F02": args.repo / "evals/fixtures/fiction-benchmark/yellow-wallpaper-voice-control/fixture.md",
        "F03": args.repo / "evals/fixtures/fiction-benchmark/gift-of-magi-reveal-control/fixture.md",
        "F04": args.repo / "evals/fixtures/fiction-benchmark/orphan-scene/clean/fixture.md",
        "F05": args.repo / "evals/fixtures/fiction-benchmark/pov-break/clean/fixture.md",
        "F06": args.repo / "evals/fixtures/fiction-benchmark/unpaid-setup/clean/fixture.md",
        "F07": args.repo / "evals/fixtures/fiction-benchmark/continuity-contradiction/clean/fixture.md",
    }
    fiction_raw = {"F01": prompt_submission(args.fiction_prompt)}
    fiction_raw.update({unit: path.read_bytes() for unit, path in fixture_paths.items()})
    for unit, slug, provenance in FICTION:
        raw = fiction_raw[unit]
        rendered, count = numbered(raw)
        dest = sources / f"{unit}.txt"
        dest.write_bytes(rendered)
        key = (f"evals/fixtures/fiction-benchmark/{slug}/groundtruth.md" if unit in {"F01", "F02", "F03"}
               else f"evals/fixtures/fiction-benchmark/{slug.removesuffix('-clean')}/clean/groundtruth.md")
        route = ("fiction M2a historical prompt submission + fiction SOURCES.md fetch"
                 if unit == "F01" else str(fixture_paths[unit].relative_to(args.repo)))
        rows.append((unit, "fiction", slug, provenance,
                     "PUBLIC_DOMAIN" if provenance == "public-domain" else "ORIGINAL_SYNTHETIC",
                     sha(raw), sha(rendered), count, route, key))

    readme = """# Shared Blind-Editor Panel — sealed packet\n\nYou are one of at least three independent developmental editors. Diagnose every neutral unit from the text supplied. Do not identify or look up a work, consult another editor, use AI assistance, or seek an answer key. Return only your completed `response.csv`; do not rename unit ids.\n\nAll response fields are closed. Use the exact uppercase tokens documented in `RESPONSE-SCHEMA.md`. Paragraph loci are the integer from `[P001]`, without the `P`. Optional notes never enter agreement calculations. Record recognition as `YES` even if it occurs after reading.\n\nArgument: code the primary structural layer/locus, audience profile, load-bearing vulnerability, first repair dependency, warrant verdict, and premise flags. Fiction: code major movements, their boundary paragraph ids in reading order, the recurring boundary pattern, and gross arc.\n\nBy returning the file you attest that your work was individual and sealed, with no AI, consultation, key/run-output access, or prior participation in this benchmark.\n"""
    (packet / "README.md").write_text(readme, encoding="utf-8")
    schema_source = (Path(__file__).with_name("panel_schema.py")).read_text(encoding="utf-8")
    (packet / "RESPONSE-SCHEMA.md").write_text(
        "# Response schema\n\nThe exact token sets and ordinal mappings are frozen in the attached `panel_schema.py`. Do not edit it. Blank fields are permitted only when the domain or conditional flag does not apply. `gt8_flag_types` joins multiple tokens with `;`.\n\n" +
        "```python\n" + schema_source + "```\n", encoding="utf-8")
    shutil.copy2(Path(__file__).with_name("panel_schema.py"), packet / "panel_schema.py")
    with (packet / "response.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for unit in ARGUMENT_UNITS + FICTION_UNITS:
            row = {field: "" for field in FIELDS}
            row.update(unit_id=unit, domain="argument" if unit.startswith("A") else "fiction")
            writer.writerow(row)

    with (operator / "SOURCE-MAP.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("unit_id", "domain", "fixture_slug", "provenance", "distribution_basis",
                         "source_sha256", "packet_sha256", "paragraph_count",
                         "reconstruction_route", "key_path"))
        writer.writerows(rows)
    with (operator / "PANEL-LEDGER.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("editor_id", "qualification_checked", "conflict_checked", "prior_key_or_run_exposure",
                         "packet_sha256", "invited_at", "returned_at", "sealed_individual_attestation",
                         "no_ai_attestation", "recognized_units", "exclusions", "response_sha256"))
        for editor in ("E01", "E02", "E03"):
            writer.writerow((editor,) + ("",) * 11)
    shutil.copy2(Path(__file__).with_name("compile_responses.py"), operator / "compile_responses.py")
    shutil.copy2(Path(__file__).with_name("adjudicate_panel.py"), operator / "adjudicate_panel.py")
    shutil.copy2(Path(__file__).with_name("panel_schema.py"), operator / "panel_schema.py")
    shutil.copy2(Path(__file__).with_name("key-projection.csv"), operator / "KEY-PROJECTION.csv")
    (operator / "RECRUITMENT-NOTE.md").write_text(
        "# Recruitment note\n\nRecruit at least three qualified developmental editors who have not participated in this benchmark. Each editor receives an identical frozen copy of `packet/`, completes both domains without AI or consultation, and returns a sealed individual CSV. Confirm and record the lawful basis for giving each editor access to the five third-party argument texts before sending. Do not send anything in `operator-only/`.\n",
        encoding="utf-8")
    (operator / "SCORING-PROTOCOL.md").write_text(
        "# Scoring protocol\n\n1. Freeze and hash the identical packet per editor. 2. Record eligibility, exposure, recognition, and sealed attestations in PANEL-LEDGER.csv. 3. Run `compile_responses.py --source-map SOURCE-MAP.csv --responses <returns...> --out ratings`. 4. From this operator directory, run `APODICTIC_REPO=/path/to/apodictic python3 adjudicate_panel.py --ratings-dir ratings --key-projection KEY-PROJECTION.csv --output adjudication`; it imports the audited alpha implementation from that clone, computes alpha/CI, unique modes or medians/ranges, min-of-subdimensions, and frozen key compatibility. 5. Run recognition-excluded sensitivity analyses where needed. 6. Independently review the result before changing any ground-truth Reliability ledger.\n",
        encoding="utf-8")
    (args.output / "CURRENT.md").write_text(
        "# Current packet\n\n`packet/` is the only sendable packet. `operator-only/` contains identities, mappings, and scoring machinery and must never be sent. Older sibling packet directories are stale.\n",
        encoding="utf-8")
    print(f"OK: built shared packet with {len(rows)} independent units at {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
