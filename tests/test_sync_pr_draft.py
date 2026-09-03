from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from ensure_sync_pr_draft import (  # noqa: E402
    SyncDraftError,
    ensure_sync_pr_draft,
)


REPOSITORY = "Owner/Repo"


def _pull(*, number: int = 7, draft: bool = False, labels: tuple[str, ...] = ("ci-ready",)):
    return {
        "number": number,
        "draft": draft,
        "labels": [{"name": name} for name in labels],
        "base": {"ref": "main"},
        "head": {
            "ref": "chore/sync-setec-contract",
            "repo": {"full_name": "owner/repo"},
        },
    }


class FakeGh:
    def __init__(self, pulls: list[dict], *, fail_query: bool = False):
        self.pulls = copy.deepcopy(pulls)
        self.fail_query = fail_query
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        self.calls.append(args)
        if args[:2] == ["gh", "api"] and "/pulls?" in args[-1]:
            if self.fail_query:
                return subprocess.CompletedProcess(args, 1, "", "query failed")
            return subprocess.CompletedProcess(args, 0, json.dumps(self.pulls), "")
        if args[:4] == ["gh", "api", "--method", "DELETE"]:
            for pull in self.pulls:
                pull["labels"] = [
                    label
                    for label in pull["labels"]
                    if label["name"].casefold() != "ci-ready"
                ]
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[:3] == ["gh", "pr", "ready"]:
            for pull in self.pulls:
                if pull["number"] == int(args[3]):
                    pull["draft"] = True
            return subprocess.CompletedProcess(args, 0, "", "")
        return subprocess.CompletedProcess(args, 1, "", "unexpected command")


def test_ready_labeled_sync_pr_is_disarmed_before_success():
    fake = FakeGh([_pull()])
    receipt = ensure_sync_pr_draft(REPOSITORY, runner=fake)
    assert receipt == {
        "draft": True,
        "labels": [],
        "pr": 7,
        "repository": REPOSITORY,
        "schema": "apodictic-sync-pr-draft/1",
    }
    assert [call[:3] for call in fake.calls] == [
        ["gh", "api", "repos/Owner/Repo/pulls?state=open&base=main&head=Owner:chore/sync-setec-contract&per_page=100"],
        ["gh", "api", "--method"],
        ["gh", "pr", "ready"],
        ["gh", "api", "repos/Owner/Repo/pulls?state=open&base=main&head=Owner:chore/sync-setec-contract&per_page=100"],
    ]


def test_no_content_updater_case_is_post_enforced_without_new_mutation():
    fake = FakeGh([_pull()])
    ensure_sync_pr_draft(REPOSITORY, runner=fake)
    split = len(fake.calls)

    # Model create-pull-request reporting no operation: it leaves the existing
    # PR untouched. The post-updater invocation must still read and prove state.
    receipt = ensure_sync_pr_draft(REPOSITORY, runner=fake)
    assert receipt["draft"] is True
    assert receipt["labels"] == []
    later = fake.calls[split:]
    assert len(later) == 2
    assert all(call[:2] == ["gh", "api"] for call in later)


def test_mixed_case_identity_and_label_follow_github_semantics():
    pull = _pull(labels=("CI-READY",))
    pull["base"]["ref"] = "MAIN"
    pull["head"]["ref"] = "CHORE/SYNC-SETEC-CONTRACT"
    fake = FakeGh([pull])
    assert ensure_sync_pr_draft(REPOSITORY, runner=fake)["draft"] is True


def test_zero_pr_is_an_explicit_clean_state():
    receipt = ensure_sync_pr_draft(REPOSITORY, runner=FakeGh([]))
    assert receipt["pr"] is None
    assert receipt["draft"] is None


def test_ambiguous_fixed_branch_set_refuses():
    fake = FakeGh([_pull(number=7), _pull(number=8)])
    with pytest.raises(SyncDraftError, match="ambiguous"):
        ensure_sync_pr_draft(REPOSITORY, runner=fake)


def test_failed_resolver_command_is_not_treated_as_zero_prs():
    fake = FakeGh([], fail_query=True)
    with pytest.raises(SyncDraftError, match="query failed"):
        ensure_sync_pr_draft(REPOSITORY, runner=fake)


def test_failed_readback_refuses_after_mutation():
    fake = FakeGh([_pull()])

    original = fake.__call__
    queries = 0

    def disappear(args: list[str]) -> subprocess.CompletedProcess[str]:
        nonlocal queries
        result = original(args)
        if args[:2] == ["gh", "api"] and "/pulls?" in args[-1]:
            queries += 1
            if queries == 2:
                return subprocess.CompletedProcess(args, 0, "[]", "")
        return result

    with pytest.raises(SyncDraftError, match="changed identity"):
        ensure_sync_pr_draft(REPOSITORY, runner=disappear)
