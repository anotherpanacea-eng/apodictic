from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_merge_train import (  # noqa: E402
    TrainError,
    _git_environment,
    load_inventory,
    verify_train,
)


def _git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], check=check, capture_output=True, text=True,
    )
    return result.stdout.strip()


def _commit(repo: Path, name: str, text: str, message: str | None = None) -> str:
    (repo / name).write_text(text, encoding="utf-8")
    _git(repo, "add", name)
    _git(repo, "commit", "-m", message or f"add {name}")
    return _git(repo, "rev-parse", "HEAD")


def _clean_train(tmp_path: Path) -> tuple[Path, dict, dict[str, str]]:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Train Test")
    _git(repo, "config", "user.email", "train@example.invalid")
    base = _commit(repo, "base.txt", "base\n")
    _git(repo, "switch", "-c", "one", base)
    one = _commit(repo, "one.txt", "one\n", "old candidate [skip ci]")
    _git(repo, "switch", "-c", "two", base)
    two = _commit(repo, "two.txt", "two\n")
    _git(repo, "switch", "main")
    _git(repo, "merge", "--no-ff", "one", "-m", "merge one")
    merge_one = _git(repo, "rev-parse", "HEAD")
    integration = _commit(repo, "integration.txt", "integration\n")
    _git(repo, "merge", "--no-ff", "two", "-m", "merge two")
    merge_two = _git(repo, "rev-parse", "HEAD")
    _git(repo, "update-ref", "refs/remotes/origin/main", base)
    inventory = {
        "schema": "apodictic-merge-train/1",
        "base": base,
        "base_ref": "refs/remotes/origin/main",
        "head": merge_two,
        "steps": [
            {"kind": "constituent", "pr": 1, "head": one, "merge": merge_one,
             "tree_mode": "clean", "resolution": None},
            {"kind": "train", "label": "integration", "commit": integration},
            {"kind": "constituent", "pr": 2, "head": two, "merge": merge_two,
             "tree_mode": "clean", "resolution": None},
        ],
    }
    return repo, inventory, {
        "base": base, "one": one, "two": two, "merge_one": merge_one,
        "integration": integration, "head": merge_two,
    }


def test_valid_closed_ordered_clean_train(tmp_path: Path):
    repo, inventory, _ = _clean_train(tmp_path)
    receipt = verify_train(repo, inventory)
    assert receipt["constituent_count"] == 2
    assert receipt["train_commit_count"] == 1
    assert receipt["conflict_resolution_count"] == 0


def test_train_with_only_train_steps_is_refused(tmp_path: Path):
    repo, inventory, ids = _clean_train(tmp_path)
    inventory["head"] = ids["integration"]
    inventory["steps"] = [inventory["steps"][1]]
    with pytest.raises(TrainError, match="at least one constituent"):
        verify_train(repo, inventory)


def test_ambient_git_environment_cannot_rebind_object_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
):
    repo, inventory, _ = _clean_train(tmp_path)
    hostile = {
        "GIT_DIR": str(tmp_path / "attacker.git"),
        "GIT_WORK_TREE": str(tmp_path / "attacker-tree"),
        "GIT_OBJECT_DIRECTORY": str(tmp_path / "attacker-objects"),
        "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(tmp_path / "alternates"),
        "GIT_NAMESPACE": "attacker",
        "GIT_INDEX_FILE": str(tmp_path / "attacker-index"),
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "core.repositoryformatversion",
        "GIT_CONFIG_VALUE_0": "999",
    }
    for name, value in hostile.items():
        monkeypatch.setenv(name, value)

    sanitized = _git_environment()
    for name in hostile:
        assert name not in sanitized
    assert sanitized["GIT_CONFIG_GLOBAL"]
    assert sanitized["GIT_CONFIG_NOSYSTEM"] == "1"
    assert sanitized["GIT_NO_REPLACE_OBJECTS"] == "1"
    assert sanitized["GIT_OPTIONAL_LOCKS"] == "0"
    assert sanitized["GIT_TERMINAL_PROMPT"] == "0"
    assert verify_train(repo, inventory)["constituent_count"] == 2


def test_clean_merge_with_arbitrary_tree_edit_is_refused(tmp_path: Path):
    repo, inventory, ids = _clean_train(tmp_path)
    _git(repo, "reset", "--hard", ids["integration"])
    _git(repo, "merge", "--no-ff", "two", "--no-commit")
    (repo / "unreviewed.txt").write_text("hidden\n", encoding="utf-8")
    _git(repo, "add", "unreviewed.txt")
    _git(repo, "commit", "-m", "correct parents, wrong tree")
    wrong = _git(repo, "rev-parse", "HEAD")
    inventory["head"] = wrong
    inventory["steps"][2]["merge"] = wrong
    with pytest.raises(TrainError, match="tree differs"):
        verify_train(repo, inventory)


def test_replacement_ref_cannot_hide_the_actual_merge_tree(tmp_path: Path):
    repo, inventory, ids = _clean_train(tmp_path)
    expected_tree = _git(repo, "rev-parse", f"{ids['head']}^{{tree}}")
    _git(repo, "reset", "--hard", ids["integration"])
    _git(repo, "merge", "--no-ff", "two", "--no-commit")
    (repo / "unreviewed.txt").write_text("hidden\n", encoding="utf-8")
    _git(repo, "add", "unreviewed.txt")
    _git(repo, "commit", "-m", "actual wrong tree")
    actual = _git(repo, "rev-parse", "HEAD")
    parents = _git(repo, "rev-list", "--parents", "-n", "1", actual).split()[1:]
    replacement = _git(
        repo, "commit-tree", expected_tree,
        "-p", parents[0], "-p", parents[1], "-m", "replacement view",
    )
    _git(repo, "replace", actual, replacement)
    inventory["head"] = actual
    inventory["steps"][2]["merge"] = actual
    with pytest.raises(TrainError, match="replacement refs"):
        verify_train(repo, inventory)
    _git(repo, "replace", "-d", actual)
    grafts = repo / ".git" / "info" / "grafts"
    grafts.write_text(f"{actual} {' '.join(parents)}\n", encoding="ascii")
    with pytest.raises(TrainError, match="grafts file"):
        verify_train(repo, inventory)


def test_real_conflict_requires_explicit_resolution_mode(tmp_path: Path):
    repo = tmp_path / "conflict"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Train Test")
    _git(repo, "config", "user.email", "train@example.invalid")
    base = _commit(repo, "shared.txt", "base\n")
    _git(repo, "switch", "-c", "candidate")
    candidate = _commit(repo, "shared.txt", "candidate\n")
    _git(repo, "switch", "main")
    prior = _commit(repo, "shared.txt", "train-side\n")
    _git(repo, "merge", "--no-ff", "candidate", "--no-commit", check=False)
    (repo / "shared.txt").write_text("reviewed resolution\n", encoding="utf-8")
    _git(repo, "add", "shared.txt")
    _git(repo, "commit", "-m", "resolve candidate conflict")
    merge = _git(repo, "rev-parse", "HEAD")
    _git(repo, "update-ref", "refs/remotes/origin/main", base)
    inventory = {
        "schema": "apodictic-merge-train/1", "base": base,
        "base_ref": "refs/remotes/origin/main", "head": merge,
        "steps": [
            {"kind": "train", "label": "prior integration", "commit": prior},
            {"kind": "constituent", "pr": 8, "head": candidate, "merge": merge,
             "tree_mode": "conflict-resolution",
             "resolution": "resolved shared.txt using combined behavior"},
        ],
    }
    assert verify_train(repo, inventory)["conflict_resolution_count"] == 1
    inventory["steps"][1]["tree_mode"] = "clean"
    inventory["steps"][1]["resolution"] = None
    with pytest.raises(TrainError, match="conflicting"):
        verify_train(repo, inventory)


def test_modify_delete_conflict_may_resolve_to_materialized_side(tmp_path: Path):
    repo = tmp_path / "modify-delete"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Train Test")
    _git(repo, "config", "user.email", "train@example.invalid")
    base = _commit(repo, "shared.txt", "base\n")
    _git(repo, "switch", "-c", "candidate")
    candidate = _commit(repo, "shared.txt", "candidate version\n")
    _git(repo, "switch", "main")
    _git(repo, "rm", "shared.txt")
    _git(repo, "commit", "-m", "train side deletes shared")
    prior = _git(repo, "rev-parse", "HEAD")
    _git(repo, "merge", "--no-ff", "candidate", "--no-commit", check=False)
    _git(repo, "add", "shared.txt")
    _git(repo, "commit", "-m", "keep candidate version")
    merge = _git(repo, "rev-parse", "HEAD")
    _git(repo, "update-ref", "refs/remotes/origin/main", base)
    inventory = {
        "schema": "apodictic-merge-train/1", "base": base,
        "base_ref": "refs/remotes/origin/main", "head": merge,
        "steps": [
            {"kind": "train", "label": "prior integration", "commit": prior},
            {"kind": "constituent", "pr": 8, "head": candidate, "merge": merge,
             "tree_mode": "conflict-resolution",
             "resolution": "kept the constituent version of shared.txt"},
        ],
    }
    assert verify_train(repo, inventory)["conflict_resolution_count"] == 1


def test_modify_delete_conflict_cannot_introduce_standard_markers(tmp_path: Path):
    repo = tmp_path / "modify-delete-markers"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Train Test")
    _git(repo, "config", "user.email", "train@example.invalid")
    base = _commit(repo, "shared.txt", "base\n")
    _git(repo, "switch", "-c", "candidate")
    candidate = _commit(repo, "shared.txt", "candidate version\n")
    _git(repo, "switch", "main")
    _git(repo, "rm", "shared.txt")
    _git(repo, "commit", "-m", "train side deletes shared")
    prior = _git(repo, "rev-parse", "HEAD")
    _git(repo, "merge", "--no-ff", "candidate", "--no-commit", check=False)
    (repo / "shared.txt").write_text(
        "<<<<<<< train\n(deleted)\n=======\ncandidate version\n>>>>>>> candidate\n",
        encoding="utf-8",
    )
    _git(repo, "add", "shared.txt")
    _git(repo, "commit", "-m", "retain hand-authored conflict markers")
    merge = _git(repo, "rev-parse", "HEAD")
    _git(repo, "update-ref", "refs/remotes/origin/main", base)
    inventory = {
        "schema": "apodictic-merge-train/1", "base": base,
        "base_ref": "refs/remotes/origin/main", "head": merge,
        "steps": [
            {"kind": "train", "label": "prior integration", "commit": prior},
            {"kind": "constituent", "pr": 8, "head": candidate, "merge": merge,
             "tree_mode": "conflict-resolution",
             "resolution": "claimed a resolution containing marker text"},
        ],
    }
    with pytest.raises(TrainError, match="retains standard conflict markers"):
        verify_train(repo, inventory)


def test_content_conflict_markers_are_not_a_resolution(tmp_path: Path):
    repo = tmp_path / "unresolved-markers"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Train Test")
    _git(repo, "config", "user.email", "train@example.invalid")
    base = _commit(repo, "shared.txt", "base\n")
    _git(repo, "switch", "-c", "candidate")
    candidate = _commit(repo, "shared.txt", "candidate\n")
    _git(repo, "switch", "main")
    prior = _commit(repo, "shared.txt", "train-side\n")
    _git(repo, "merge", "--no-ff", "candidate", "--no-commit", check=False)
    marker_text = (repo / "shared.txt").read_text(encoding="utf-8")
    assert "<<<<<<<" in marker_text and ">>>>>>>" in marker_text
    _git(repo, "add", "shared.txt")
    _git(repo, "commit", "-m", "commit unresolved markers")
    merge = _git(repo, "rev-parse", "HEAD")
    _git(repo, "update-ref", "refs/remotes/origin/main", base)
    inventory = {
        "schema": "apodictic-merge-train/1", "base": base,
        "base_ref": "refs/remotes/origin/main", "head": merge,
        "steps": [
            {"kind": "train", "label": "prior integration", "commit": prior},
            {"kind": "constituent", "pr": 8, "head": candidate, "merge": merge,
             "tree_mode": "conflict-resolution",
             "resolution": "claimed resolution without changing conflict markers"},
        ],
    }
    with pytest.raises(TrainError, match="retains standard conflict markers"):
        verify_train(repo, inventory)


def test_configured_width_conflict_markers_are_not_a_resolution(tmp_path: Path):
    repo = tmp_path / "configured-markers"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Train Test")
    _git(repo, "config", "user.email", "train@example.invalid")
    (repo / ".gitattributes").write_text(
        "shared.txt conflict-marker-size=10\n", encoding="ascii",
    )
    (repo / "shared.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", ".gitattributes", "shared.txt")
    _git(repo, "commit", "-m", "base with custom marker width")
    base = _git(repo, "rev-parse", "HEAD")
    _git(repo, "switch", "-c", "candidate")
    candidate = _commit(repo, "shared.txt", "candidate\n")
    _git(repo, "switch", "main")
    prior = _commit(repo, "shared.txt", "train-side\n")
    _git(repo, "merge", "--no-ff", "candidate", "--no-commit", check=False)
    marker_text = (repo / "shared.txt").read_text(encoding="utf-8")
    assert "<<<<<<<<<<" in marker_text and ">>>>>>>>>>" in marker_text
    (repo / "shared.txt").write_text(
        marker_text.replace("train-side", "train-side edited", 1), encoding="utf-8",
    )
    _git(repo, "add", "shared.txt")
    _git(repo, "commit", "-m", "retain configured-width conflict markers")
    merge = _git(repo, "rev-parse", "HEAD")
    _git(repo, "update-ref", "refs/remotes/origin/main", base)
    inventory = {
        "schema": "apodictic-merge-train/1", "base": base,
        "base_ref": "refs/remotes/origin/main", "head": merge,
        "steps": [
            {"kind": "train", "label": "prior integration", "commit": prior},
            {"kind": "constituent", "pr": 8, "head": candidate, "merge": merge,
             "tree_mode": "conflict-resolution",
             "resolution": "claimed edit retaining custom markers"},
        ],
    }
    with pytest.raises(TrainError, match="retains standard conflict markers"):
        verify_train(repo, inventory)


def test_conflict_resolution_cannot_smuggle_an_unrelated_tree_edit(tmp_path: Path):
    repo = tmp_path / "conflict-smuggle"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Train Test")
    _git(repo, "config", "user.email", "train@example.invalid")
    base = _commit(repo, "shared.txt", "base\n")
    _commit(repo, "untouched.txt", "reviewed\n")
    base = _git(repo, "rev-parse", "HEAD")
    _git(repo, "switch", "-c", "candidate")
    candidate = _commit(repo, "shared.txt", "candidate\n")
    _git(repo, "switch", "main")
    prior = _commit(repo, "shared.txt", "train-side\n")
    _git(repo, "merge", "--no-ff", "candidate", "--no-commit", check=False)
    (repo / "shared.txt").write_text("reviewed resolution\n", encoding="utf-8")
    (repo / "untouched.txt").write_text("smuggled\n", encoding="utf-8")
    _git(repo, "add", "shared.txt", "untouched.txt")
    _git(repo, "commit", "-m", "resolve with unrelated edit")
    merge = _git(repo, "rev-parse", "HEAD")
    _git(repo, "update-ref", "refs/remotes/origin/main", base)
    inventory = {
        "schema": "apodictic-merge-train/1", "base": base,
        "base_ref": "refs/remotes/origin/main", "head": merge,
        "steps": [
            {"kind": "train", "label": "prior integration", "commit": prior},
            {"kind": "constituent", "pr": 8, "head": candidate, "merge": merge,
             "tree_mode": "conflict-resolution",
             "resolution": "resolved shared.txt using combined behavior"},
        ],
    }
    with pytest.raises(TrainError, match="only paths"):
        verify_train(repo, inventory)


@pytest.mark.parametrize("mutation", ["reorder", "missing", "moved", "extra", "skip"])
def test_closed_topology_refuses_mutations(tmp_path: Path, mutation: str):
    repo, inventory, ids = _clean_train(tmp_path)
    if mutation == "reorder":
        inventory["steps"][0], inventory["steps"][2] = (
            inventory["steps"][2], inventory["steps"][0],
        )
    elif mutation == "missing":
        del inventory["steps"][0]
    elif mutation == "moved":
        _git(repo, "update-ref", "refs/remotes/origin/main", ids["one"])
    elif mutation == "extra":
        inventory["extra"] = True
    else:
        _git(repo, "commit", "--amend", "-m", "train head [skip ci]")
        inventory["head"] = _git(repo, "rev-parse", "HEAD")
        inventory["steps"][2]["merge"] = inventory["head"]
    with pytest.raises(TrainError):
        verify_train(repo, inventory)


def test_duplicate_json_and_malformed_or_unresolvable_ids_fail(tmp_path: Path):
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text(
        '{"schema":"apodictic-merge-train/1","schema":"again"}', encoding="utf-8",
    )
    with pytest.raises(TrainError, match="duplicate JSON"):
        load_inventory(duplicate)
    repo, inventory, _ = _clean_train(tmp_path / "train")
    inventory["steps"][0]["head"] = "f" * 40
    with pytest.raises(TrainError):
        verify_train(repo, inventory)


def test_exact_base_lease_rejects_movement_and_accepts_unchanged(tmp_path: Path):
    remote = tmp_path / "remote.git"
    work = tmp_path / "work"
    _git(tmp_path, "init", "--bare", str(remote))
    _git(tmp_path, "clone", str(remote), str(work))
    _git(work, "config", "user.name", "Lease Test")
    _git(work, "config", "user.email", "lease@example.invalid")
    base = _commit(work, "base.txt", "base\n")
    _git(work, "push", "origin", "HEAD:main")
    _git(work, "switch", "-c", "candidate")
    candidate = _commit(work, "candidate.txt", "candidate\n")
    _git(work, "switch", "main")
    _git(work, "merge", "--no-ff", "candidate", "-m", "landing")
    landing = _git(work, "rev-parse", "HEAD")
    tested_tree = _git(work, "rev-parse", "HEAD^{tree}")
    assert _git(work, "rev-list", "--parents", "-n", "1", landing).split()[1:] == [base, candidate]
    assert _git(work, "rev-parse", f"{landing}^{{tree}}") == tested_tree

    _git(work, "push", "origin", f"{candidate}:refs/heads/main")
    rejected = subprocess.run(
        ["git", "-C", str(work), "push", "--atomic",
         f"--force-with-lease=refs/heads/main:{base}", "origin",
         f"{landing}:refs/heads/main"], capture_output=True, text=True,
    )
    assert rejected.returncode != 0
    _git(work, "push", "origin", f"{base}:refs/heads/control")
    accepted = subprocess.run(
        ["git", "-C", str(work), "push", "--atomic",
         f"--force-with-lease=refs/heads/control:{base}", "origin",
         f"{landing}:refs/heads/control"], capture_output=True, text=True,
    )
    assert accepted.returncode == 0, accepted.stderr
