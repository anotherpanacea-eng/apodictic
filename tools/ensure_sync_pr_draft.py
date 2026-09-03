#!/usr/bin/env python3
"""Force the fixed automated SETEC sync pull request to draft and unarmed."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from typing import Any, Callable, Sequence
from urllib.parse import quote


REPOSITORY_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
SYNC_BRANCH = "chore/sync-setec-contract"


class SyncDraftError(ValueError):
    """The fixed sync pull request could not be uniquely disarmed and verified."""


Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]


def _default_runner(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )


def _call(runner: Runner, *args: str) -> str:
    completed = runner(list(args))
    if completed.returncode:
        raise SyncDraftError(
            f"{' '.join(args)} failed: {completed.stderr.strip()}"
        )
    return completed.stdout


def _json(runner: Runner, *args: str) -> Any:
    raw = _call(runner, *args)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SyncDraftError(f"{' '.join(args)} returned invalid JSON") from exc


def _open_fixed_pulls(
    repository: str, runner: Runner,
) -> list[dict[str, Any]]:
    owner = repository.split("/", 1)[0]
    query = (
        f"repos/{repository}/pulls"
        f"?state=open&base=main&head={owner}:{SYNC_BRANCH}&per_page=100"
    )
    raw = _json(runner, "gh", "api", query)
    if not isinstance(raw, list):
        raise SyncDraftError("pulls query did not return an array")
    matches: list[dict[str, Any]] = []
    for pull in raw:
        if not isinstance(pull, dict):
            raise SyncDraftError("pulls query contains a non-object")
        base = pull.get("base") or {}
        head = pull.get("head") or {}
        head_repo = head.get("repo") or {}
        if (
            isinstance(base.get("ref"), str)
            and base["ref"].casefold() == "main"
            and isinstance(head.get("ref"), str)
            and head["ref"].casefold() == SYNC_BRANCH
            and isinstance(head_repo.get("full_name"), str)
            and head_repo["full_name"].casefold() == repository.casefold()
        ):
            matches.append(pull)
    if len(matches) > 1:
        raise SyncDraftError("refusing ambiguous fixed-branch PR set")
    return matches


def _labels(pull: dict[str, Any]) -> list[str]:
    labels = pull.get("labels")
    if not isinstance(labels, list):
        raise SyncDraftError("pull labels must be an array")
    names: list[str] = []
    for label in labels:
        if not isinstance(label, dict) or not isinstance(label.get("name"), str):
            raise SyncDraftError("pull label must contain a string name")
        names.append(label["name"])
    return names


def ensure_sync_pr_draft(
    repository: str, *, runner: Runner = _default_runner,
) -> dict[str, Any]:
    if not isinstance(repository, str) or not REPOSITORY_RE.fullmatch(repository):
        raise SyncDraftError("repository must be an owner/name slug")
    pulls = _open_fixed_pulls(repository, runner)
    if not pulls:
        return {
            "draft": None,
            "labels": [],
            "pr": None,
            "repository": repository,
            "schema": "apodictic-sync-pr-draft/1",
        }

    pull = pulls[0]
    number = pull.get("number")
    draft = pull.get("draft")
    if not isinstance(number, int) or isinstance(number, bool) or number < 1:
        raise SyncDraftError("pull number must be a positive integer")
    if draft not in {True, False}:
        raise SyncDraftError("pull draft state must be boolean")

    label_names = _labels(pull)
    ci_ready = next(
        (name for name in label_names if name.casefold() == "ci-ready"), None
    )
    if ci_ready is not None:
        _call(
            runner,
            "gh", "api", "--method", "DELETE",
            f"repos/{repository}/issues/{number}/labels/{quote(ci_ready, safe='')}",
        )
    if draft is False:
        _call(
            runner, "gh", "pr", "ready", str(number),
            "--undo", "--repo", repository,
        )

    readback = _open_fixed_pulls(repository, runner)
    if len(readback) != 1 or readback[0].get("number") != number:
        raise SyncDraftError("fixed sync PR changed identity during disarm")
    verified = readback[0]
    if verified.get("draft") is not True:
        raise SyncDraftError("fixed sync PR is not draft after disarm")
    names = _labels(verified)
    if any(name.casefold() == "ci-ready" for name in names):
        raise SyncDraftError("fixed sync PR retains ci-ready after disarm")
    return {
        "draft": True,
        "labels": names,
        "pr": number,
        "repository": repository,
        "schema": "apodictic-sync-pr-draft/1",
    }


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        receipt = ensure_sync_pr_draft(args.repository)
    except SyncDraftError as exc:
        print(f"sync-pr-draft: REFUSED: {exc}")
        return 1
    print("sync-pr-draft: " + _canonical(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
