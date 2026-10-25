from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


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
