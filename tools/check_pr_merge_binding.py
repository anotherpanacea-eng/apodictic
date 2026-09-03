#!/usr/bin/env python3
"""Fail closed unless CI is testing GitHub's exact PR merge commit."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Sequence


OID_RE = re.compile(r"[0-9a-fA-F]{40}\Z")


class BindingError(ValueError):
    """The checkout does not match the declared pull-request merge binding."""


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _oid(value: object, *, name: str) -> str:
    if not isinstance(value, str) or not OID_RE.fullmatch(value) or set(value) == {"0"}:
        raise BindingError(f"{name} must be a nonzero full 40-hex object id")
    return value.lower()


def _bounded_decimal(value: str, *, name: str, maximum: int) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[1-9][0-9]*", value):
        raise BindingError(f"{name} must be a canonical positive ASCII integer")
    if int(value) > maximum:
        raise BindingError(f"{name} exceeds its bounded maximum")
    return value


def _git(repo: Path, *args: str, text: bool = True) -> str | bytes:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=text,
            encoding="utf-8" if text else None,
            errors="strict" if text else None,
            check=False,
        )
    except UnicodeDecodeError as exc:
        raise BindingError(f"git {' '.join(args)} returned non-UTF-8 output") from exc
    if completed.returncode:
        stderr = completed.stderr if text else completed.stderr.decode("utf-8", "replace")
        raise BindingError(f"git {' '.join(args)} failed: {stderr.strip()}")
    return completed.stdout


def _commit_parents(repo: Path) -> list[str]:
    """Read parent headers without resolving unavailable shallow parent objects."""
    raw = str(_git(repo, "cat-file", "-p", "HEAD"))
    headers = raw.split("\n\n", 1)[0].splitlines()
    parents: list[str] = []
    for line in headers:
        if line.startswith("parent "):
            value = line.removeprefix("parent ")
            if not OID_RE.fullmatch(value):
                raise BindingError("HEAD contains a malformed parent header")
            parents.append(value.lower())
    return parents


def verify_binding(
    repo: Path,
    *,
    repository: str,
    base: str,
    head: str,
    github_sha: str,
    job: str,
    run_id: str,
    run_attempt: str,
) -> dict[str, str]:
    if not isinstance(repository, str) or not re.fullmatch(
        r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository
    ):
        raise BindingError("repository must be an owner/name slug")
    base_oid = _oid(base, name="base")
    head_oid = _oid(head, name="head")
    merge_oid = _oid(github_sha, name="github-sha")
    if job != "validate":
        raise BindingError("job must be exactly validate")
    _bounded_decimal(run_id, name="run-id", maximum=9_223_372_036_854_775_807)
    _bounded_decimal(run_attempt, name="run-attempt", maximum=999_999)

    status = _git(
        repo, "status", "--porcelain=v1", "-z", "--untracked-files=all", text=False,
    )
    if status:
        raise BindingError("checkout is not clean")

    current = str(_git(repo, "rev-parse", "--verify", "HEAD^{commit}")).strip().lower()
    if current != merge_oid:
        raise BindingError(f"HEAD {current} does not equal github-sha {merge_oid}")
    parents = _commit_parents(repo)
    if len(parents) != 2:
        raise BindingError("GitHub checkout HEAD must be a two-parent merge commit")
    if parents != [base_oid, head_oid]:
        raise BindingError(
            "merge parents do not match event order: "
            f"expected base/head {base_oid} {head_oid}, got {' '.join(parents)}"
        )
    return {
        "base_sha": base_oid,
        "head_sha": head_oid,
        "job": job,
        "repository": repository,
        "run_attempt": run_attempt,
        "run_id": run_id,
        "schema": "apodictic-pr-merge-binding/1",
        "synthetic_merge_sha": merge_oid,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--repository", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--github-sha", required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-attempt", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        receipt = verify_binding(
            args.repo,
            repository=args.repository,
            base=args.base,
            head=args.head,
            github_sha=args.github_sha,
            job=args.job,
            run_id=args.run_id,
            run_attempt=args.run_attempt,
        )
    except BindingError as exc:
        print(f"pr-merge-binding: REFUSED: {exc}")
        return 1
    print("pr-merge-binding: " + _canonical(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
