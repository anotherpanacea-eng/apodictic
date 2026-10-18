from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
CI = WORKFLOWS / "ci.yml"

CI_SHA256 = "faa273ef64ff2518f5888a6914976b8d5aca25372c3440d8a071f8c8014c5f8f"
AUXILIARY_SHA256 = {
    "release.yml": "51fa09c164c47c8346f2cd6e8e2f21d1361f04c99a4996faf3cceddf90bed433",
    "release-readiness.yml": "18c248b2d4e94fb9473d81b3dfd04ccfc58083e39c3937e343d2d618288f3710",
    "sync-setec.yml": "e5f5f7347ef64699fb39f578e9528eca73a6e988cd37c711b422cd9b0c8b0e85",
}
EVENTS = [
    "opened",
    "synchronize",
    "reopened",
    "ready_for_review",
    "converted_to_draft",
    "labeled",
    "unlabeled",
    "closed",
]
ARMABLE_ACTIONS = {"opened", "synchronize", "reopened", "ready_for_review"}
SYNC_BRANCH = "chore/sync-setec-contract"
ACTION_V7_SHA = "22a9089034f40e5a961c8808d113e2c98fb63676"
ACTION_CONTRACT = ROOT / "tests" / "fixtures" / "create-pull-request-v7-action-contract.json"


class StringLoader(yaml.SafeLoader):
    pass


for first, resolvers in list(StringLoader.yaml_implicit_resolvers.items()):
    StringLoader.yaml_implicit_resolvers[first] = [
        item for item in resolvers if item[0] != "tag:yaml.org,2002:bool"
    ]


def _load(text: str) -> dict:
    value = yaml.load(text, Loader=StringLoader)
    assert isinstance(value, dict)
    return value


def _normalized_digest(text: str) -> str:
    normalized = "\n".join(
        line.rstrip()
        for line in text.replace("\r\n", "\n").split("\n")
        if line.strip() and not line.lstrip().startswith("#")
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def test_operator_policy_forbids_unreviewed_landing_bytes() -> None:
    policy = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "version bumps at merge" not in policy
    assert "reviewed train-only commits made before the train freezes" in policy
    assert "Do not add bytes during landing" in policy


def _workflow_names(directory: Path) -> set[str]:
    return {
        path.name
        for pattern in ("*.yml", "*.yaml")
        for path in directory.glob(pattern)
    }


def _current_train(*, same_repo: bool, branch: str) -> bool:
    return same_repo and branch.casefold().startswith("train/")


def _armed(
    *,
    draft: bool,
    same_repo: bool,
    branch: str,
    action: str,
    labels: set[str] = frozenset(),
    event_label: str | None = None,
) -> bool:
    if draft:
        return False
    train = _current_train(same_repo=same_repo, branch=branch)
    if train:
        return action in ARMABLE_ACTIONS
    if same_repo and branch.casefold() == SYNC_BRANCH:
        return False
    return (
        any(label.casefold() == "ci-ready" for label in labels)
        and (
            action in ARMABLE_ACTIONS
            or (
                action == "labeled"
                and isinstance(event_label, str)
                and event_label.casefold() == "ci-ready"
            )
        )
    )


def _canonical_group(
    *,
    pr: int,
    same_repo: bool,
    branch: str,
    action: str,
    event_label: str | None,
    run_id: int,
) -> str:
    train = _current_train(same_repo=same_repo, branch=branch)
    canonical = action not in {"labeled", "unlabeled"} or (
        isinstance(event_label, str) and event_label.casefold() == "ci-ready" and not train
    )
    suffix = "clearance" if canonical else str(run_id)
    return f"apodictic-ci-{pr}-{suffix}"


def _step_id(step: dict) -> str:
    return step.get("name") or step.get("uses") or ""


def test_current_workflow_holds_closed_policy():
    assert _workflow_names(WORKFLOWS) == {
        "ci.yml",
        "claude.yml",
        "release.yml",
        "release-readiness.yml",
        "sync-setec.yml",
    }
    text = CI.read_text(encoding="utf-8")
    assert _normalized_digest(text) == CI_SHA256
    workflow = _load(text)

    assert set(workflow) == {
        "name", "run-name", "on", "permissions", "concurrency", "jobs"
    }
    assert workflow["name"] == "ci"
    assert workflow["on"] == {"pull_request": {"types": EVENTS}}
    assert workflow["permissions"] == {"contents": "read"}
    assert set(workflow["concurrency"]) == {"group", "cancel-in-progress"}
    assert workflow["concurrency"]["cancel-in-progress"] == "true"

    assert set(workflow["jobs"]) == {"validate"}
    job = workflow["jobs"]["validate"]
    assert set(job) == {"if", "runs-on", "timeout-minutes", "steps", "defaults", "env"}
    assert job["runs-on"] == "windows-latest"
    assert job["defaults"] == {"run": {"shell": "pwsh"}}
    assert job["env"] == {"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    assert job["timeout-minutes"] == 10
    assert "matrix" not in job
    assert "strategy" not in job
    assert "services" not in job
    assert "container" not in job
    assert "uses" not in job
    assert "continue-on-error" not in job

    steps = job["steps"]
    assert [_step_id(step) for step in steps] == [
        "actions/checkout@v4",
        "Bind billed job to the exact pull-request merge",
        "actions/setup-python@v5",
        "actions/setup-node@v4",
        "Install policy test dependencies",
        "Draft-first train policy self-tests",
        "Byte-compile canonical Python (syntax gate)",
        "Validate plugin + marketplace manifests parse as JSON",
        "Version parity across manifests",
        "Research reliability self-tests",
        "Changelog fragments parse",
        "Status-drift lint (spec Status vs shipped deliverables)",
        "Inventory-parity sync-marker check",
        "Registry-derived docs are up to date",
        "Codex + Antigravity builds self-check",
        "SETEC contract drift gate (self-consistency)",
        "SETEC contract tests (floors + vendored-golden parse)",
        "Full native validator gate with Bash absent",
    ]
    assert steps[0] == {"uses": "actions/checkout@v4"}
    binding = steps[1]
    assert set(binding) == {"name", "env", "run"}
    assert set(binding["env"]) == {
        "BASE_SHA", "HEAD_SHA", "MERGE_SHA", "JOB_NAME", "REPOSITORY",
        "RUN_ID", "RUN_ATTEMPT"
    }
    assert "tools/check_pr_merge_binding.py" in binding["run"]
    assert "'plugins/apodictic/scripts/validate.py', '--check-all'" in steps[-1]["run"]
    assert 'finally {' in steps[-1]["run"]
    regression = next(step for step in steps if step.get("name") == "Draft-first train policy self-tests")
    assert regression["run"].split() == [
        "python", "-m", "pytest", "tests/test_ci_train_policy.py",
        "tests/test_merge_train.py", "tests/test_pr_merge_binding.py",
        "tests/test_sync_pr_draft.py", "tests/test_train_ci_receipts.py",
        "tests/test_validate_native_aggregates.py", "-q",
    ]


def test_auxiliary_workflows_are_closed_and_sync_remains_draft():
    for name, digest in AUXILIARY_SHA256.items():
        text = (WORKFLOWS / name).read_text(encoding="utf-8")
        assert _normalized_digest(text) == digest

    release = _load((WORKFLOWS / "release.yml").read_text(encoding="utf-8"))
    readiness = _load(
        (WORKFLOWS / "release-readiness.yml").read_text(encoding="utf-8")
    )
    assert release["on"] == {"push": {"tags": ["v*"]}}
    assert set(release["jobs"]) == {"publish"}
    assert set(readiness["jobs"]) == {"readiness"}

    sync = _load((WORKFLOWS / "sync-setec.yml").read_text(encoding="utf-8"))
    assert set(sync) == {"name", "on", "permissions", "env", "jobs"}
    assert sync["permissions"] == {"contents": "write", "pull-requests": "write"}
    steps = sync["jobs"]["sync"]["steps"]
    ids = [_step_id(step) for step in steps]
    before = ids.index("Disarm any existing sync PR before branch update")
    updater = ids.index("Open or update draft bump PR")
    after = ids.index("Enforce draft state after updater, including no-op updates")
    assert before < updater < after
    action = steps[updater]
    assert action["uses"] == (
        "peter-evans/create-pull-request@" + ACTION_V7_SHA
    )
    assert action["with"]["draft"] == "always-true"
    expected_guard = (
        'python tools/ensure_sync_pr_draft.py --repository "$GITHUB_REPOSITORY"'
    )
    assert steps[before]["run"] == expected_guard
    assert steps[after]["run"] == expected_guard

    contract = json.loads(ACTION_CONTRACT.read_text(encoding="utf-8"))
    assert contract == {
        "schema": "github-action-contract/1",
        "repository": "peter-evans/create-pull-request",
        "commit": ACTION_V7_SHA,
        "path": "action.yml",
        "git_blob_sha": "9d28570cb5eeba6ff4850b6ea9a4bbe21bdbe46f",
        "draft_input": {
            "default": False,
            "accepted_values": ["true", "always-true", "false"],
            "always_true_behavior": "on create and update",
        },
    }


@pytest.mark.parametrize(
    "case",
    [
        dict(draft=True, same_repo=True, branch="train/week", action="opened"),
        dict(draft=False, same_repo=True, branch="feature/x", action="opened"),
        dict(
            draft=False,
            same_repo=True,
            branch=SYNC_BRANCH,
            action="opened",
            labels={"ci-ready"},
        ),
        dict(
            draft=False,
            same_repo=True,
            branch="CHORE/SYNC-SETEC-CONTRACT",
            action="opened",
            labels={"CI-READY"},
        ),
        dict(
            draft=False,
            same_repo=True,
            branch="train/week",
            action="labeled",
            labels={"ci-ready"},
            event_label="ci-ready",
        ),
        dict(
            draft=False,
            same_repo=False,
            branch="train/week",
            action="opened",
        ),
        dict(
            draft=False,
            same_repo=False,
            branch="feature/x",
            action="labeled",
            labels={"ci-ready"},
            event_label="unrelated",
        ),
        dict(
            draft=False,
            same_repo=True,
            branch="feature/x",
            action="unlabeled",
            labels=set(),
            event_label="ci-ready",
        ),
        dict(
            draft=False,
            same_repo=True,
            branch="feature/x",
            action="closed",
            labels={"ci-ready"},
        ),
    ],
)
def test_unauthorized_states_are_unarmed(case):
    assert not _armed(**case)


@pytest.mark.parametrize(
    "case",
    [
        dict(draft=False, same_repo=True, branch="train/week", action="opened"),
        dict(draft=False, same_repo=True, branch="TRAIN/week", action="opened"),
        dict(
            draft=False,
            same_repo=False,
            branch="feature/x",
            action="opened",
            labels={"ci-ready"},
        ),
        dict(
            draft=False,
            same_repo=True,
            branch="feature/x",
            action="labeled",
            labels={"ci-ready"},
            event_label="ci-ready",
        ),
        dict(
            draft=False,
            same_repo=True,
            branch="feature/x",
            action="labeled",
            labels={"CI-READY"},
            event_label="CI-READY",
        ),
    ],
)
def test_exact_authorizations_arm(case):
    assert _armed(**case)


def test_concurrency_state_table_is_closed():
    common = dict(pr=17, same_repo=True, branch="feature/x", run_id=901)
    for action in ARMABLE_ACTIONS | {"converted_to_draft", "closed"}:
        assert _canonical_group(
            **common, action=action, event_label=None
        ) == "apodictic-ci-17-clearance"
    for action in ("labeled", "unlabeled"):
        assert _canonical_group(
            **common, action=action, event_label="ci-ready"
        ) == "apodictic-ci-17-clearance"
        assert _canonical_group(
            **common, action=action, event_label="other"
        ) == "apodictic-ci-17-901"
    assert _canonical_group(
        pr=17,
        same_repo=True,
        branch="train/week",
        action="labeled",
        event_label="ci-ready",
        run_id=901,
    ) == "apodictic-ci-17-901"


def test_workflow_inventory_includes_yaml_extension(tmp_path: Path):
    (tmp_path / "ci.yml").write_text("name: ci\n", encoding="utf-8")
    (tmp_path / "hidden.yaml").write_text("name: hidden\n", encoding="utf-8")
    assert _workflow_names(tmp_path) == {"ci.yml", "hidden.yaml"}


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("timeout-minutes: 10", "timeout-minutes: 100"),
        ("  pull_request:", "  pull_request_target:"),
        ("jobs:\n  validate:", "jobs:\n  hidden:\n    runs-on: ubuntu-latest\n  validate:"),
        ("actions/checkout@v4", "actions/checkout@main"),
        ("'plugins/apodictic/scripts/validate.py', '--check-all'", "'skipped.py'"),
        ("github.event.action == 'labeled'", "github.event.action != 'labeled'"),
        (SYNC_BRANCH, "chore/other"),
    ],
)
def test_ci_cost_or_authorization_mutation_fails_closed(old: str, new: str):
    text = CI.read_text(encoding="utf-8")
    assert old in text
    assert _normalized_digest(text.replace(old, new, 1)) != CI_SHA256


# The @claude workflow hands a write-capable App token and the Claude OAuth
# token to a model acting on comment text. These tests guard the boundaries a
# later edit must not loosen: only trusted authors start a run, fork pull
# requests are refused before checkout, every action is pinned to a commit,
# and the workflow's own GITHUB_TOKEN carries no write scope beyond OIDC.
CLAUDE = WORKFLOWS / "claude.yml"
TRUSTED_AUTHOR = """contains(fromJSON('["OWNER","MEMBER","COLLABORATOR"]'),"""


def _claude_job() -> dict:
    return _load(CLAUDE.read_text(encoding="utf-8"))["jobs"]["claude"]


def test_claude_workflow_pins_every_action_to_a_commit():
    uses = [step["uses"] for step in _claude_job()["steps"] if "uses" in step]
    assert uses
    for ref in uses:
        assert re.search(r"@[0-9a-f]{40}$", ref), f"{ref} is not pinned to a commit SHA"


def test_claude_workflow_requires_a_trusted_author_on_every_trigger():
    workflow = _load(CLAUDE.read_text(encoding="utf-8"))
    gate = workflow["jobs"]["claude"]["if"]
    events = re.findall(r"github\.event_name == '(\w+)'", gate)
    assert sorted(events) == sorted(workflow["on"])
    assert gate.count(TRUSTED_AUTHOR) == len(events)
    assert gate.count("'@claude')") >= len(events)


def test_claude_workflow_refuses_fork_prs_before_checkout():
    steps = _claude_job()["steps"]
    guard = next(
        i for i, step in enumerate(steps) if "isCrossRepository" in step.get("run", "")
    )
    checkout = next(
        i for i, step in enumerate(steps)
        if step.get("uses", "").startswith("actions/checkout@")
    )
    assert guard < checkout
    assert 'if [ "$cross" != "false" ]' in steps[guard]["run"]


def test_claude_workflow_token_has_no_write_scope_but_oidc():
    workflow = _load(CLAUDE.read_text(encoding="utf-8"))
    assert "permissions" not in workflow or all(
        value != "write" for value in workflow["permissions"].values()
    )
    scopes = workflow["jobs"]["claude"]["permissions"]
    assert {name for name, value in scopes.items() if value == "write"} == {"id-token"}


def _no_bash_probe():
    # Exercise only the child probe with mocked process creation. The hosted
    # executable rename/restore protocol is never executed on a developer host.
    run = _load(CI.read_text(encoding="utf-8"))["jobs"]["validate"]["steps"][-1]["run"]
    return run.split("$probe = @'\n", 1)[1].split("\n'@", 1)[0]


@pytest.mark.parametrize("failure", ["returned-zero", "returned-nonzero", "permission", "timeout", "bad-image"])
def test_no_bash_probe_requires_process_creation_absence(monkeypatch, failure):
    import subprocess
    import sys
    monkeypatch.setattr(sys, "argv", ["probe", "[]"])
    monkeypatch.setenv("PATH", "")
    def launch(argv, **kwargs):
        assert kwargs["shell"] is False
        if failure == "permission": raise PermissionError("denied")
        if failure == "timeout": raise subprocess.TimeoutExpired(argv, 10)
        if failure == "bad-image": raise OSError("bad executable")
        return subprocess.CompletedProcess(argv, 0 if failure == "returned-zero" else 127)
    monkeypatch.setattr(subprocess, "run", launch)
    with pytest.raises(RuntimeError):
        exec(compile(_no_bash_probe(), "ci-no-bash-child", "exec"), {})


@pytest.mark.parametrize("aggregate_status", [0, 7])
def test_no_bash_probe_rechecks_absence_and_preserves_aggregate_status(monkeypatch, aggregate_status):
    import subprocess
    import sys
    monkeypatch.setattr(sys, "argv", ["probe", '["C:/fixed/bash.exe"]'])
    monkeypatch.setenv("PATH", "")
    calls = []
    def launch(argv, **kwargs):
        calls.append(argv)
        assert kwargs["shell"] is False
        if '--check-all' in argv:
            assert argv[0] == sys.executable
            return subprocess.CompletedProcess(argv, aggregate_status)
        error = FileNotFoundError("missing executable")
        error.winerror = 2
        raise error
    monkeypatch.setattr(subprocess, "run", launch)
    with pytest.raises(SystemExit) as result:
        exec(compile(_no_bash_probe(), "ci-no-bash-child", "exec"), {})
    assert result.value.code == aggregate_status
    assert len(calls) == 11
    assert '--check-all' in calls[5]
    assert calls[:5] == calls[6:]
