from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
CI = WORKFLOWS / "ci.yml"

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


def _step(steps: list[dict], name: str) -> dict:
    return next(step for step in steps if step.get("name") == name)


def test_ci_stays_bounded_and_runs_the_real_gate():
    workflow = _load(CI.read_text(encoding="utf-8"))
    assert list(workflow["on"]) == ["pull_request"]
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["concurrency"]["cancel-in-progress"] == "true"

    job = workflow["jobs"]["validate"]
    assert job["timeout-minutes"] == 10
    for key in ("matrix", "strategy", "services", "container", "uses", "continue-on-error"):
        assert key not in job
    steps = job["steps"]
    binding = _step(steps, "Bind billed job to the exact pull-request merge")
    assert "tools/check_pr_merge_binding.py" in binding["run"]
    runs = [step.get("run") for step in steps]
    assert "bash scripts/validate.sh --self-test-all" in runs
    assert "bash scripts/validate.sh --check-canonical" in runs

    # Windows runs the native gate under the same admission and binding receipt,
    # with PATH reduced to the Python install directory so no shell is reachable.
    windows = workflow["jobs"]["validate-windows"]
    assert windows["if"] == job["if"]
    assert windows["timeout-minutes"] == 30
    assert _step(windows["steps"], binding["name"])["env"] == binding["env"]
    gate = windows["steps"][-1]["run"].splitlines()
    assert gate[0] == "$env:PATH = Split-Path -Parent $env:PYTHON_EXE"
    assert gate[-1] == "& $env:PYTHON_EXE plugins/apodictic/scripts/validate.py --check-all"


def test_sync_pr_stays_draft_around_the_updater():
    sync = _load((WORKFLOWS / "sync-setec.yml").read_text(encoding="utf-8"))
    steps = sync["jobs"]["sync"]["steps"]
    names = [step.get("name") for step in steps]
    before = names.index("Disarm any existing sync PR before branch update")
    updater = names.index("Open or update draft bump PR")
    after = names.index("Enforce draft state after updater, including no-op updates")
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
