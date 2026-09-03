from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_pr_merge_binding import BindingError, verify_binding  # noqa: E402


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def _commit(repo: Path, name: str, text: str) -> str:
    (repo / name).write_text(text, encoding="utf-8")
    _git(repo, "add", name)
    _git(repo, "commit", "-m", f"add {name}")
    return _git(repo, "rev-parse", "HEAD")


def _merge(tmp_path: Path) -> tuple[Path, str, str, str]:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "CI Test")
    _git(repo, "config", "user.email", "ci@example.invalid")
    base = _commit(repo, "base.txt", "base\n")
    _git(repo, "switch", "-c", "candidate")
    head = _commit(repo, "candidate.txt", "candidate\n")
    _git(repo, "switch", "main")
    _git(repo, "merge", "--no-ff", "candidate", "-m", "synthetic merge")
    return repo, base, head, _git(repo, "rev-parse", "HEAD")


def _verify(repo: Path, base: str, head: str, merge: str):
    return verify_binding(
        repo, repository="owner/repo", base=base, head=head, github_sha=merge,
        job="validate", run_id="123", run_attempt="2",
    )


def test_exact_clean_two_parent_binding_emits_receipt(tmp_path: Path):
    repo, base, head, merge = _merge(tmp_path)
    assert _verify(repo, base, head, merge) == {
        "base_sha": base,
        "head_sha": head,
        "job": "validate",
        "repository": "owner/repo",
        "run_attempt": "2",
        "run_id": "123",
        "schema": "apodictic-pr-merge-binding/1",
        "synthetic_merge_sha": merge,
    }


def test_shallow_checkout_needs_no_parent_objects(tmp_path: Path):
    source, base, head, merge = _merge(tmp_path)
    bare = tmp_path / "remote.git"
    _git(tmp_path, "clone", "--bare", str(source), str(bare))
    shallow = tmp_path / "shallow"
    _git(
        tmp_path, "clone", "--no-local", "--depth=1", "--branch", "main",
        bare.as_uri(), str(shallow),
    )
    assert _git(shallow, "rev-parse", "HEAD") == merge
    assert subprocess.run(
        ["git", "-C", str(shallow), "cat-file", "-e", base], capture_output=True,
    ).returncode != 0
    assert subprocess.run(
        ["git", "-C", str(shallow), "cat-file", "-e", head], capture_output=True,
    ).returncode != 0
    assert _verify(shallow, base, head, merge)["synthetic_merge_sha"] == merge


def test_dirty_nonmerge_octopus_and_wrong_order_are_refused(tmp_path: Path):
    repo, base, head, merge = _merge(tmp_path / "normal")
    (repo / "dirty.txt").write_text("dirty", encoding="utf-8")
    with pytest.raises(BindingError, match="not clean"):
        _verify(repo, base, head, merge)
    (repo / "dirty.txt").unlink()
    with pytest.raises(BindingError, match="parents do not match"):
        _verify(repo, head, base, merge)
    _git(repo, "reset", "--hard", head)
    with pytest.raises(BindingError, match="two-parent"):
        _verify(repo, base, head, head)

    octo = tmp_path / "octopus"
    octo.mkdir()
    _git(octo, "init", "-b", "main")
    _git(octo, "config", "user.name", "CI Test")
    _git(octo, "config", "user.email", "ci@example.invalid")
    octo_base = _commit(octo, "base.txt", "base\n")
    heads = []
    for index in (1, 2):
        _git(octo, "switch", "-c", f"c{index}", octo_base)
        heads.append(_commit(octo, f"c{index}.txt", f"{index}\n"))
    _git(octo, "switch", "main")
    octo_merge = _git(
        octo, "commit-tree", f"{octo_base}^{{tree}}",
        "-p", octo_base, "-p", heads[0], "-p", heads[1], "-m", "octopus",
    )
    _git(octo, "reset", "--hard", octo_merge)
    with pytest.raises(BindingError, match="two-parent"):
        _verify(octo, octo_base, heads[0], octo_merge)


@pytest.mark.parametrize(
    ("field", "value"),
    [("base", "f" * 40), ("head", "0" * 40), ("github_sha", "short")],
)
def test_wrong_or_malformed_declared_oid_is_refused(
    tmp_path: Path, field: str, value: str,
):
    repo, base, head, merge = _merge(tmp_path)
    values = {"base": base, "head": head, "github_sha": merge}
    values[field] = value
    with pytest.raises(BindingError):
        verify_binding(
            repo, repository="owner/repo", **values,
            job="validate", run_id="1", run_attempt="1",
        )


def test_metadata_is_strict_and_preinstall_import_is_application_free(tmp_path: Path):
    repo, base, head, merge = _merge(tmp_path)
    with pytest.raises(BindingError, match="run-attempt"):
        verify_binding(
            repo, repository="owner/repo", base=base, head=head, github_sha=merge,
            job="validate", run_id="1", run_attempt="0",
        )

    with pytest.raises(BindingError, match="repository"):
        verify_binding(
            repo, repository="wrong-shape", base=base, head=head,
            github_sha=merge, job="validate", run_id="1", run_attempt="1",
        )

    for field, value in (
        ("job", "pytest"),
        ("run_id", "0"),
        ("run_id", "01"),
        ("run_id", "9223372036854775808"),
        ("run_attempt", "01"),
        ("run_attempt", "1000000"),
    ):
        metadata = {"job": "validate", "run_id": "1", "run_attempt": "1"}
        metadata[field] = value
        with pytest.raises(BindingError):
            verify_binding(
                repo, repository="owner/repo", base=base, head=head,
                github_sha=merge, **metadata,
            )
    tool = Path(__file__).resolve().parents[1] / "tools" / "check_pr_merge_binding.py"
    probe = (
        "import runpy,sys;"
        f"runpy.run_path({str(tool)!r},run_name='preinstall_probe');"
        "loaded=[n for n in sys.modules if n == 'setec_voiceprint' "
        "or n.startswith('setec_voiceprint.')];assert not loaded,loaded"
    )
    result = subprocess.run(
        [sys.executable, "-S", "-c", probe], capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
