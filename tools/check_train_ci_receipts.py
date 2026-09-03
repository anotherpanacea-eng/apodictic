#!/usr/bin/env python3
"""Validate one newest complete Apodictic train-CI run and its job receipts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Sequence


OID_RE = re.compile(r"[0-9a-f]{40}\Z")
RUN_NAME_RE = re.compile(
    r"apodictic-ci pr=(?P<pr>[1-9][0-9]*) "
    r"action=(?P<action>opened|synchronize|reopened|ready_for_review|"
    r"converted_to_draft|labeled|unlabeled|closed) "
    r"train=(?P<train>true|false) ci-ready-event=(?P<ci_ready>true|false)\Z"
)
RECEIPT_RE = re.compile(r"pr-merge-binding: (\{[^\r\n]*\})")
WORKFLOW_PATH = ".github/workflows/ci.yml"
EXPECTED_JOBS = frozenset({"validate"})


class ReceiptError(ValueError):
    """Live or fixture evidence is not a complete exact-head clearance."""


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _oid(value: object, *, name: str) -> str:
    if not isinstance(value, str) or not OID_RE.fullmatch(value) or set(value) == {"0"}:
        raise ReceiptError(f"{name} must be a nonzero lowercase 40-hex object id")
    return value


def _exact_keys(value: dict[str, Any], expected: set[str], *, where: str) -> None:
    if set(value) != expected:
        raise ReceiptError(
            f"{where} keys must be exactly {sorted(expected)}; got {sorted(value)}"
        )


def _same(left: str, right: str) -> bool:
    return left.casefold() == right.casefold()


def _workflow_path_matches(value: object) -> bool:
    if value == WORKFLOW_PATH:
        return True
    if not isinstance(value, str) or not value.startswith(WORKFLOW_PATH + "@"):
        return False
    ref = value[len(WORKFLOW_PATH) + 1:]
    return bool(re.fullmatch(r"[A-Za-z0-9_./-]{1,255}", ref))


def _activity(run: dict[str, Any], *, pr: int, current_train: bool) -> dict[str, Any]:
    title = run.get("display_title")
    if not isinstance(title, str) or (match := RUN_NAME_RE.fullmatch(title)) is None:
        raise ReceiptError("workflow run has missing or malformed activity class")
    marked_pr = int(match.group("pr"))
    marked_train = match.group("train") == "true"
    ci_ready_event = match.group("ci_ready") == "true"
    action = match.group("action")
    if marked_pr != pr or marked_train != current_train:
        raise ReceiptError("workflow run activity class disagrees with live PR identity")
    if action not in {"labeled", "unlabeled"} and ci_ready_event:
        raise ReceiptError("non-label activity cannot be a ci-ready label event")
    noise = action in {"labeled", "unlabeled"} and (
        marked_train or not ci_ready_event
    )
    return {"action": action, "ci_ready_event": ci_ready_event, "noise": noise}


def _parse_job_receipt(log: object) -> dict[str, Any]:
    if not isinstance(log, str):
        raise ReceiptError("job log must be text")
    matches = RECEIPT_RE.findall(log)
    if len(matches) != 1:
        raise ReceiptError("job log must contain exactly one binding receipt")
    try:
        receipt = json.loads(matches[0], object_pairs_hook=_reject_duplicates)
    except (json.JSONDecodeError, ReceiptError) as exc:
        raise ReceiptError(f"invalid binding receipt JSON: {exc}") from exc
    if not isinstance(receipt, dict):
        raise ReceiptError("binding receipt must be an object")
    _exact_keys(
        receipt,
        {
            "base_sha", "head_sha", "job", "repository", "run_attempt", "run_id",
            "schema", "synthetic_merge_sha",
        },
        where="binding receipt",
    )
    return receipt


def _validate_noise_jobs(run: dict[str, Any]) -> None:
    if run["status"] != "completed" or run["conclusion"] != "skipped":
        raise ReceiptError("ignored label run is not a completed all-skipped run")
    jobs = run["jobs"]
    if not isinstance(jobs, list):
        raise ReceiptError("ignored label run has no job metadata")
    by_name: dict[str, dict[str, Any]] = {}
    for job in jobs:
        if not isinstance(job, dict):
            raise ReceiptError("ignored label run job must be an object")
        _exact_keys(job, {"name", "status", "conclusion", "log"}, where="noise job")
        name = job["name"]
        if not isinstance(name, str) or name in by_name:
            raise ReceiptError("ignored label run job names must be unique strings")
        by_name[name] = job
    if set(by_name) != EXPECTED_JOBS:
        raise ReceiptError("ignored label run does not contain the exact expected jobs")
    if any(
        job["status"] != "completed" or job["conclusion"] != "skipped" or job["log"] != ""
        for job in by_name.values()
    ):
        raise ReceiptError("ignored label run contains non-skipped work")


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReceiptError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def validate_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    _exact_keys(
        evidence,
        {"schema", "repository", "pr", "base_ref", "base_sha", "head_sha", "current", "runs"},
        where="evidence",
    )
    if evidence["schema"] != "apodictic-train-ci-evidence/1":
        raise ReceiptError("unknown evidence schema")
    repository = evidence["repository"]
    if (
        not isinstance(repository, str)
        or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)
    ):
        raise ReceiptError("repository must be an owner/name slug")
    pr = evidence["pr"]
    if not isinstance(pr, int) or isinstance(pr, bool) or pr < 1:
        raise ReceiptError("pr must be a positive integer")
    if evidence["base_ref"] != "main":
        raise ReceiptError("base_ref must be main")
    base = _oid(evidence["base_sha"], name="base_sha")
    head = _oid(evidence["head_sha"], name="head_sha")
    current = evidence["current"]
    if not isinstance(current, dict):
        raise ReceiptError("current must be an object")
    _exact_keys(
        current,
        {
            "draft", "head_repo", "head_ref", "labels", "merged", "state",
            "base_ref", "base_sha", "head_sha",
        },
        where="current",
    )
    if (
        current["base_ref"] != "main"
        or current["base_sha"] != base
        or current["head_sha"] != head
    ):
        raise ReceiptError("live PR base/head does not match evidence")
    if current["draft"] is not False:
        raise ReceiptError("PR is not currently promoted")
    if current["state"] != "open" or current["merged"] is not False:
        raise ReceiptError("PR is not currently open and unmerged")
    if not isinstance(current["head_repo"], str) or not isinstance(current["head_ref"], str):
        raise ReceiptError("live head repository/ref must be strings")
    if not isinstance(current["labels"], list) or not all(
        isinstance(label, str) for label in current["labels"]
    ):
        raise ReceiptError("live labels must be strings")
    current_train = (
        _same(current["head_repo"], repository)
        and current["head_ref"].casefold().startswith("train/")
    )
    if (
        _same(current["head_repo"], repository)
        and current["head_ref"].casefold() == "chore/sync-setec-contract"
    ):
        raise ReceiptError("fixed sync branch cannot receive standalone authorization")
    if not current_train and not any(
        label.casefold() == "ci-ready" for label in current["labels"]
    ):
        raise ReceiptError("PR is not currently armed")

    runs = evidence["runs"]
    if not isinstance(runs, list) or not runs:
        raise ReceiptError("runs must be a nonempty array")
    seen_ids: set[int] = set()
    clearance: list[dict[str, Any]] = []
    for run in runs:
        if not isinstance(run, dict):
            raise ReceiptError("run must be an object")
        _exact_keys(
            run,
            {
                "id", "attempt", "event", "path", "head_sha", "display_title",
                "status", "conclusion", "jobs",
            },
            where="run",
        )
        run_id = run["id"]
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id < 1:
            raise ReceiptError("run id must be a positive integer")
        if run_id in seen_ids:
            raise ReceiptError("duplicate workflow run id")
        seen_ids.add(run_id)
        if run["event"] != "pull_request" or not _workflow_path_matches(run["path"]):
            raise ReceiptError("workflow run has wrong event or path")
        if run["head_sha"] != head:
            raise ReceiptError("workflow run has wrong head")
        activity = _activity(run, pr=pr, current_train=current_train)
        if activity["noise"]:
            _validate_noise_jobs(run)
            continue
        clearance.append(run)
    if not clearance:
        raise ReceiptError("no clearance run exists for the exact head")
    selected = max(clearance, key=lambda item: item["id"])
    attempt = selected["attempt"]
    if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
        raise ReceiptError("run attempt must be a positive integer")
    if selected["status"] != "completed" or selected["conclusion"] != "success":
        raise ReceiptError("newest clearance run is not successful")
    jobs = selected["jobs"]
    if not isinstance(jobs, list):
        raise ReceiptError("selected run jobs must be an array")
    by_name: dict[str, dict[str, Any]] = {}
    synthetic: str | None = None
    for job in jobs:
        if not isinstance(job, dict):
            raise ReceiptError("job must be an object")
        _exact_keys(job, {"name", "status", "conclusion", "log"}, where="job")
        name = job["name"]
        if not isinstance(name, str) or name in by_name:
            raise ReceiptError("job names must be unique strings")
        by_name[name] = job
    if set(by_name) != EXPECTED_JOBS:
        raise ReceiptError("selected run does not contain the exact expected jobs")
    for name in sorted(EXPECTED_JOBS):
        job = by_name[name]
        if job["status"] != "completed" or job["conclusion"] != "success":
            raise ReceiptError(f"job {name} is not successful")
        receipt = _parse_job_receipt(job["log"])
        if receipt["schema"] != "apodictic-pr-merge-binding/1":
            raise ReceiptError(f"job {name} has wrong receipt schema")
        if receipt["job"] != name:
            raise ReceiptError(f"job {name} receipt names another job")
        if not _same(receipt["repository"], repository):
            raise ReceiptError(f"job {name} receipt names another repository")
        if receipt["run_id"] != str(selected["id"]) or receipt["run_attempt"] != str(attempt):
            raise ReceiptError(f"job {name} receipt has mixed run or attempt")
        if receipt["base_sha"] != base or receipt["head_sha"] != head:
            raise ReceiptError(f"job {name} receipt has wrong base or head")
        merge = _oid(receipt["synthetic_merge_sha"], name="synthetic_merge_sha")
        if synthetic is None:
            synthetic = merge
        elif synthetic != merge:
            raise ReceiptError("job receipts disagree on synthetic merge")
    assert synthetic is not None
    return {
        "base_ref": "main",
        "base_sha": base,
        "head_sha": head,
        "job_count": len(EXPECTED_JOBS),
        "pr": pr,
        "repository": repository,
        "run_attempt": attempt,
        "run_id": selected["id"],
        "schema": "apodictic-train-ci-clearance/1",
        "synthetic_merge_sha": synthetic,
        "workflow_path": WORKFLOW_PATH,
    }


def _run_json(*args: str) -> Any:
    completed = subprocess.run(
        list(args), capture_output=True, text=True, encoding="utf-8", errors="strict",
        check=False,
    )
    if completed.returncode:
        raise ReceiptError(f"{' '.join(args)} failed: {completed.stderr.strip()}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ReceiptError(f"{' '.join(args)} returned invalid JSON") from exc


def collect_live(repository: str, pr: int, *, base: str, head: str) -> dict[str, Any]:
    pull = _run_json("gh", "api", f"repos/{repository}/pulls/{pr}")
    labels = [item["name"] for item in pull.get("labels", [])]
    current = {
        "base_ref": pull.get("base", {}).get("ref"),
        "base_sha": pull.get("base", {}).get("sha"),
        "draft": pull.get("draft"),
        "head_ref": pull.get("head", {}).get("ref"),
        "head_repo": (pull.get("head", {}).get("repo") or {}).get("full_name"),
        "head_sha": pull.get("head", {}).get("sha"),
        "labels": labels,
        "merged": pull.get("merged"),
        "state": pull.get("state"),
    }
    query = (
        f"repos/{repository}/actions/workflows/ci.yml/runs"
        f"?event=pull_request&head_sha={head}&per_page=100"
    )
    raw_runs = _run_json("gh", "api", query).get("workflow_runs", [])
    runs: list[dict[str, Any]] = []
    current_train = (
        isinstance(current["head_repo"], str)
        and _same(current["head_repo"], repository)
        and str(current["head_ref"]).casefold().startswith("train/")
    )
    clearance_ids: list[int] = []
    for raw in raw_runs:
        run = {
            "id": raw.get("id"),
            "attempt": raw.get("run_attempt"),
            "event": raw.get("event"),
            "path": raw.get("path"),
            "head_sha": raw.get("head_sha"),
            "display_title": raw.get("display_title"),
            "status": raw.get("status"),
            "conclusion": raw.get("conclusion"),
            "jobs": [],
        }
        activity = _activity(run, pr=pr, current_train=current_train)
        if activity["noise"]:
            attempt = run["attempt"]
            raw_jobs = _run_json(
                "gh", "api",
                f"repos/{repository}/actions/runs/{run['id']}/attempts/{attempt}/jobs?per_page=100",
            ).get("jobs", [])
            run["jobs"] = [
                {
                    "name": raw_job.get("name"),
                    "status": raw_job.get("status"),
                    "conclusion": raw_job.get("conclusion"),
                    "log": "",
                }
                for raw_job in raw_jobs
            ]
        else:
            clearance_ids.append(run["id"])
        runs.append(run)
    if clearance_ids:
        selected_id = max(clearance_ids)
        selected = next(run for run in runs if run["id"] == selected_id)
        attempt = selected["attempt"]
        raw_jobs = _run_json(
            "gh", "api",
            f"repos/{repository}/actions/runs/{selected_id}/attempts/{attempt}/jobs?per_page=100",
        ).get("jobs", [])
        jobs = []
        for raw_job in raw_jobs:
            completed = subprocess.run(
                ["gh", "run", "view", str(selected_id), "--repo", repository,
                 "--job", str(raw_job["id"]), "--log"],
                capture_output=True, text=True, encoding="utf-8", errors="strict",
                check=False,
            )
            if completed.returncode:
                raise ReceiptError(
                    f"cannot read log for job {raw_job.get('name')}: {completed.stderr.strip()}"
                )
            jobs.append({
                "name": raw_job.get("name"),
                "status": raw_job.get("status"),
                "conclusion": raw_job.get("conclusion"),
                "log": completed.stdout,
            })
        selected["jobs"] = jobs
    return {
        "schema": "apodictic-train-ci-evidence/1",
        "repository": repository,
        "pr": pr,
        "base_ref": "main",
        "base_sha": base,
        "head_sha": head,
        "current": current,
        "runs": runs,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--evidence", type=Path)
    source.add_argument("--repository")
    parser.add_argument("--pr", type=int)
    parser.add_argument("--base")
    parser.add_argument("--head")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.evidence:
            evidence = json.loads(
                args.evidence.read_text(encoding="utf-8"),
                object_pairs_hook=_reject_duplicates,
            )
        else:
            if args.pr is None or args.base is None or args.head is None:
                raise ReceiptError("live mode requires --pr, --base, and --head")
            evidence = collect_live(args.repository, args.pr, base=args.base, head=args.head)
        if not isinstance(evidence, dict):
            raise ReceiptError("evidence root must be an object")
        receipt = validate_evidence(evidence)
    except (OSError, UnicodeError, json.JSONDecodeError, ReceiptError) as exc:
        print(f"train-ci-receipts: REFUSED: {exc}")
        return 1
    print("train-ci-receipts: " + _canonical(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
