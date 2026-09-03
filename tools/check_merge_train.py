#!/usr/bin/env python3
"""Validate a Apodictic merge train against a closed ordered inventory."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Sequence


OID_RE = re.compile(r"[0-9a-fA-F]{40}\Z")
SKIP_RE = re.compile(
    r"\[(?:skip ci|ci skip|no ci|skip actions|actions skip)\]|^skip-checks:\s*true\s*$",
    re.IGNORECASE | re.MULTILINE,
)
AUTHORITATIVE_BASE_REF = "refs/remotes/origin/main"


class TrainError(ValueError):
    """The proposed train does not satisfy its closed inventory."""


def _git_environment() -> dict[str, str]:
    environment = {
        key: value for key, value in os.environ.items()
        if not key.upper().startswith("GIT_")
    }
    environment.update({
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_TERMINAL_PROMPT": "0",
    })
    return environment


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise TrainError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def _exact_keys(value: dict[str, Any], expected: set[str], *, where: str) -> None:
    if set(value) != expected:
        raise TrainError(
            f"{where} keys must be exactly {sorted(expected)}; got {sorted(value)}"
        )


def _oid(value: object, *, name: str) -> str:
    if not isinstance(value, str) or not OID_RE.fullmatch(value) or set(value) == {"0"}:
        raise TrainError(f"{name} must be a nonzero full 40-hex object id")
    return value.lower()


def _git_result(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "--no-replace-objects", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            check=False,
            env=_git_environment(),
        )
    except UnicodeDecodeError as exc:
        raise TrainError(f"git {' '.join(args)} returned non-UTF-8 output") from exc


def _git(repo: Path, *args: str) -> str:
    completed = _git_result(repo, *args)
    if completed.returncode:
        raise TrainError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return completed.stdout


def _resolve(repo: Path, value: str, *, name: str) -> str:
    if value.startswith("-") or any(ch in value for ch in "\r\n\0"):
        raise TrainError(f"unsafe {name}")
    return _git(repo, "rev-parse", "--verify", f"{value}^{{commit}}").strip().lower()


def _parents(repo: Path, commit: str) -> list[str]:
    fields = _git(repo, "rev-list", "--parents", "-n", "1", commit).split()
    if not fields or fields[0].lower() != commit:
        raise TrainError(f"could not inspect exact commit {commit}")
    return [field.lower() for field in fields[1:]]


def _tree(repo: Path, commit: str) -> str:
    return _git(repo, "rev-parse", "--verify", f"{commit}^{{tree}}").strip().lower()


def _refuse_object_rewrites(repo: Path) -> None:
    replacements = _git(repo, "for-each-ref", "--format=%(refname)", "refs/replace")
    if replacements.strip():
        raise TrainError("repository contains replacement refs")
    graft_path_text = _git(repo, "rev-parse", "--git-path", "info/grafts").strip()
    graft_path = Path(graft_path_text)
    if not graft_path.is_absolute():
        graft_path = repo / graft_path
    if graft_path.exists():
        raise TrainError("repository contains a grafts file")


def _automatic_merge(repo: Path, first: str, second: str) -> tuple[bool, str, set[bytes]]:
    result = subprocess.run(
        [
            "git", "--no-replace-objects", "-C", str(repo),
            "merge-tree", "--write-tree",
            "--name-only", "-z", "--messages", first, second,
        ],
        capture_output=True,
        check=False,
        env=_git_environment(),
    )
    if result.returncode not in {0, 1}:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise TrainError(f"git merge-tree failed: {detail}")
    fields = result.stdout.split(b"\0")
    try:
        tree = fields[0].decode("ascii").lower()
    except UnicodeDecodeError as exc:
        raise TrainError("git merge-tree emitted a non-ASCII tree object id") from exc
    if not OID_RE.fullmatch(tree):
        raise TrainError("git merge-tree did not emit an exact tree object id")
    try:
        boundary = fields.index(b"", 1)
    except ValueError as exc:
        raise TrainError("git merge-tree did not terminate its conflict-path list") from exc
    conflict_paths = set(fields[1:boundary])
    if b"" in conflict_paths:
        raise TrainError("git merge-tree emitted an empty conflict path")
    clean = result.returncode == 0
    if clean and conflict_paths:
        raise TrainError("clean git merge-tree unexpectedly emitted conflict paths")
    if not clean and not conflict_paths:
        raise TrainError("conflicting git merge-tree emitted no conflict paths")
    return clean, tree, conflict_paths


def _tree_diff_paths(repo: Path, first_tree: str, second_tree: str) -> set[bytes]:
    result = subprocess.run(
        [
            "git", "--no-replace-objects", "-C", str(repo),
            "diff-tree", "--no-commit-id",
            "--name-only", "-r", "-z", first_tree, second_tree,
        ],
        capture_output=True,
        check=False,
        env=_git_environment(),
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise TrainError(f"git diff-tree failed: {detail}")
    return {field for field in result.stdout.split(b"\0") if field}


def _git_bytes(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "--no-replace-objects", "-C", str(repo), *args],
        capture_output=True,
        check=False,
        env=_git_environment(),
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise TrainError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def _tree_blob_ids(
    repo: Path, commit: str, wanted_paths: set[bytes],
) -> dict[bytes, bytes]:
    entries: dict[bytes, bytes] = {}
    for record in _git_bytes(
        repo, "ls-tree", "-r", "-z", "--full-tree", commit,
    ).split(b"\0"):
        if not record:
            continue
        try:
            metadata, path = record.split(b"\t", 1)
            _mode, object_type, object_id = metadata.split(b" ", 2)
        except ValueError as exc:
            raise TrainError("git ls-tree emitted malformed output") from exc
        if path in wanted_paths and object_type == b"blob":
            entries[path] = object_id
    return entries


def _blob(repo: Path, object_id: bytes) -> bytes:
    try:
        oid = object_id.decode("ascii")
    except UnicodeDecodeError as exc:
        raise TrainError("git ls-tree emitted a non-ASCII object id") from exc
    return _git_bytes(repo, "cat-file", "blob", oid)


def _automatic_marker_widths(content: bytes) -> set[int]:
    starts = {
        len(match.group(1))
        for match in re.finditer(rb"(?m)^(<+)(?: .*)?\r?$", content)
    }
    middles = {
        len(match.group(1))
        for match in re.finditer(rb"(?m)^(=+)\r?$", content)
    }
    ends = {
        len(match.group(1))
        for match in re.finditer(rb"(?m)^(>+)(?: .*)?\r?$", content)
    }
    return starts & middles & ends


def _contains_marker_width(content: bytes, width: int) -> bool:
    start = re.compile(
        rb"(?m)^" + re.escape(b"<" * width) + rb"(?!<)(?: .*)?\r?$",
    )
    middle = re.compile(
        rb"(?m)^" + re.escape(b"=" * width) + rb"(?![=])\r?$",
    )
    end = re.compile(
        rb"(?m)^" + re.escape(b">" * width) + rb"(?!>)(?: .*)?\r?$",
    )
    return bool(start.search(content) and middle.search(content) and end.search(content))


def _marker_bearing_conflict_paths(
    repo: Path, commit: str, automatic_tree: str, conflict_paths: set[bytes],
) -> set[bytes]:
    automatic_entries = _tree_blob_ids(repo, automatic_tree, conflict_paths)
    final_entries = _tree_blob_ids(repo, commit, conflict_paths)
    bearing: set[bytes] = set()
    for path in automatic_entries.keys() & final_entries.keys():
        widths = {7} | _automatic_marker_widths(
            _blob(repo, automatic_entries[path])
        )
        final_content = _blob(repo, final_entries[path])
        if any(_contains_marker_width(final_content, width) for width in widths):
            bearing.add(path)
    return bearing


def load_inventory(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise TrainError(f"cannot read inventory: {exc}") from exc
    try:
        value = json.loads(raw, object_pairs_hook=_no_duplicate_object)
    except (json.JSONDecodeError, TrainError) as exc:
        raise TrainError(f"invalid inventory JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise TrainError("inventory root must be an object")
    return value


def verify_train(repo: Path, inventory: dict[str, Any]) -> dict[str, Any]:
    _refuse_object_rewrites(repo)
    _exact_keys(
        inventory, {"schema", "base", "base_ref", "head", "steps"}, where="inventory",
    )
    if inventory["schema"] != "apodictic-merge-train/1":
        raise TrainError("unknown inventory schema")
    if inventory["base_ref"] != AUTHORITATIVE_BASE_REF:
        raise TrainError(f"base_ref must be exactly {AUTHORITATIVE_BASE_REF}")
    if not isinstance(inventory["steps"], list) or not inventory["steps"]:
        raise TrainError("steps must be a nonempty array")
    base = _oid(inventory["base"], name="base")
    head = _oid(inventory["head"], name="head")
    if _resolve(repo, base, name="base") != base or _resolve(repo, head, name="head") != head:
        raise TrainError("base and head must resolve to exact declared commits")
    live_base = _git(
        repo, "show-ref", "--verify", "--hash", AUTHORITATIVE_BASE_REF,
    ).strip().lower()
    if live_base != base:
        raise TrainError("base_ref moved after the inventory was sealed")
    if SKIP_RE.search(_git(repo, "log", "-1", "--format=%B", head)):
        raise TrainError("train HEAD commit message contains a CI skip instruction")

    normalized: list[dict[str, Any]] = []
    prs: set[int] = set()
    heads: set[str] = set()
    commits: set[str] = set()
    labels: set[str] = set()
    for index, raw in enumerate(inventory["steps"]):
        if not isinstance(raw, dict):
            raise TrainError(f"step {index} must be an object")
        if raw.get("kind") == "constituent":
            _exact_keys(
                raw,
                {"kind", "pr", "head", "merge", "tree_mode", "resolution"},
                where=f"step {index}",
            )
            pr = raw["pr"]
            if not isinstance(pr, int) or isinstance(pr, bool) or pr < 1:
                raise TrainError(f"step {index} pr must be a positive integer")
            candidate = _oid(raw["head"], name=f"step {index} head")
            merge = _oid(raw["merge"], name=f"step {index} merge")
            mode = raw["tree_mode"]
            resolution = raw["resolution"]
            if mode == "clean":
                if resolution is not None:
                    raise TrainError("clean merge resolution must be null")
            elif mode == "conflict-resolution":
                if (
                    not isinstance(resolution, str)
                    or not resolution.strip()
                    or any(ch in resolution for ch in "\r\n")
                ):
                    raise TrainError("conflict resolution must be a nonempty single line")
            else:
                raise TrainError(f"step {index} has unknown tree_mode")
            if pr in prs or candidate in heads or merge in commits or candidate in commits:
                raise TrainError("constituent PRs, heads, and merge commits must be unique")
            if _resolve(repo, candidate, name=f"step {index} head") != candidate:
                raise TrainError(f"constituent {pr} did not resolve exactly")
            if _resolve(repo, merge, name=f"step {index} merge") != merge:
                raise TrainError(f"constituent merge {pr} did not resolve exactly")
            ancestor = _git_result(repo, "merge-base", "--is-ancestor", candidate, base)
            if ancestor.returncode == 0:
                raise TrainError(f"constituent {pr} is already an ancestor of the train base")
            if ancestor.returncode != 1:
                raise TrainError(f"could not compare constituent {pr} with the train base")
            prs.add(pr)
            heads.add(candidate)
            commits.add(merge)
            normalized.append({
                "kind": "constituent", "pr": pr, "head": candidate,
                "merge": merge, "tree_mode": mode, "resolution": resolution,
            })
        elif raw.get("kind") == "train":
            _exact_keys(raw, {"kind", "label", "commit"}, where=f"step {index}")
            label = raw["label"]
            if not isinstance(label, str) or not label or any(ch in label for ch in "\r\n"):
                raise TrainError(f"step {index} label must be a nonempty single line")
            commit = _oid(raw["commit"], name=f"step {index} commit")
            if label in labels or commit in commits or commit in heads:
                raise TrainError("train labels and inventoried commits must be unique")
            if _resolve(repo, commit, name=f"step {index} commit") != commit:
                raise TrainError(f"train-only step {label!r} did not resolve exactly")
            labels.add(label)
            commits.add(commit)
            normalized.append({"kind": "train", "label": label, "commit": commit})
        else:
            raise TrainError(f"step {index} has unknown kind {raw.get('kind')!r}")

    if not heads:
        raise TrainError("train must contain at least one constituent step")

    current = head
    conflicts = 0
    for index, step in reversed(list(enumerate(normalized))):
        if step["kind"] == "constituent":
            if current != step["merge"]:
                raise TrainError(
                    f"constituent step {index} merge is {current}, expected {step['merge']}"
                )
            parents = _parents(repo, current)
            if len(parents) != 2:
                raise TrainError(f"constituent step {index} is not a two-parent merge")
            if parents[1] != step["head"]:
                raise TrainError(
                    f"constituent step {index} second parent is {parents[1]}, "
                    f"expected {step['head']}"
                )
            clean, automatic_tree, conflict_paths = _automatic_merge(
                repo, parents[0], parents[1],
            )
            if step["tree_mode"] == "clean":
                if not clean:
                    raise TrainError(f"constituent step {index} is conflicting, not clean")
                if _tree(repo, current) != automatic_tree:
                    raise TrainError(
                        f"constituent step {index} tree differs from automatic clean merge"
                    )
            else:
                if clean:
                    raise TrainError(
                        f"constituent step {index} claims a conflict but merges cleanly"
                    )
                resolution_paths = _tree_diff_paths(
                    repo, automatic_tree, _tree(repo, current),
                )
                if not resolution_paths.issubset(conflict_paths):
                    raise TrainError(
                        f"constituent step {index} resolution may change only paths "
                        "reported conflicting by git merge-tree"
                    )
                if _marker_bearing_conflict_paths(
                    repo, current, automatic_tree, conflict_paths,
                ):
                    raise TrainError(
                        f"constituent step {index} retains standard conflict markers"
                    )
                unresolved_paths = conflict_paths - resolution_paths
                if unresolved_paths:
                    automatic_vs_first = _tree_diff_paths(
                        repo, automatic_tree, _tree(repo, parents[0]),
                    )
                    automatic_vs_second = _tree_diff_paths(
                        repo, automatic_tree, _tree(repo, parents[1]),
                    )
                    if any(
                        path in automatic_vs_first and path in automatic_vs_second
                        for path in unresolved_paths
                    ):
                        raise TrainError(
                            f"constituent step {index} leaves a conflict path at "
                            "Git's unmaterialized automatic entry"
                        )
                conflicts += 1
            current = parents[0]
        else:
            if current != step["commit"]:
                raise TrainError(
                    f"train-only step {index} is {current}, expected {step['commit']}"
                )
            parents = _parents(repo, current)
            if len(parents) != 1:
                raise TrainError(f"train-only step {index} must have exactly one parent")
            current = parents[0]
    if current != base:
        raise TrainError(f"first-parent inventory ends at {current}, not declared base {base}")
    return {
        "base": base,
        "base_ref": AUTHORITATIVE_BASE_REF,
        "conflict_resolution_count": conflicts,
        "constituent_count": len(heads),
        "head": head,
        "schema": "apodictic-merge-train-receipt/1",
        "step_count": len(normalized),
        "train_commit_count": len(labels),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--inventory", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        receipt = verify_train(args.repo, load_inventory(args.inventory))
    except TrainError as exc:
        print(f"merge-train: REFUSED: {exc}")
        return 1
    print("merge-train: " + _canonical(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
