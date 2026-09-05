"""Verify this frozen development packet's custody, not its semantic validity."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes())


def local(root, relative):
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()), f"Path escapes packet: {relative}")
    return path


def verify_version(root, expected_inputs):
    freeze = read_json(root / "freeze.json")
    frozen = {item["path"]: item for item in freeze["files"]}
    require(len(frozen) == len(freeze["files"]), "Duplicate frozen paths")
    for relative, item in frozen.items():
        data = local(root, relative).read_bytes()
        require(len(data) == item["bytes"] and digest(data) == item["sha256"],
                f"Frozen bytes changed: {relative}")
    entries = {entry["id"]: entry for entry in freeze["entries"]}
    require(len(entries) == len(freeze["entries"]) == expected_inputs,
            "Missing or duplicate input entries")
    require(set(entries) == {p.stem for p in (root / "inputs").glob("*.md")},
            "Unaccounted input")
    common = (root / "common-prompt.txt").read_bytes()
    receipts = read_json(root / "screening/receipts.json")
    require(receipts["freeze_sha256"] == digest((root / "freeze.json").read_bytes()),
            "Receipt freeze binding changed")
    rows = {row["neutral_id"]: row for row in receipts["receipts"]}
    require(len(rows) == len(receipts["receipts"]) and set(rows) == set(entries),
            "Missing or duplicate receipt")
    require(set(entries) == {p.stem for p in (root / "screening/responses").glob("*.json")},
            "Unaccounted response")
    for name, entry in entries.items():
        story = local(root, entry["input"]).read_bytes()
        prompt = local(root, entry["dispatch_prompt"]).read_bytes()
        require(entry["input"] in frozen and entry["dispatch_prompt"] in frozen,
                "Input or dispatch was not frozen")
        require(prompt == common + f"\nNeutral label: {name}\n\nSTORY\n\n".encode() + story,
                f"Dispatch reconstruction differs: {name}")
        row = rows[name]
        require(row["input_sha256"] == digest(story) and row["prompt_sha256"] == digest(prompt),
                f"Receipt input binding differs: {name}")
        response_bytes = local(root, row["response_path"]).read_bytes()
        response = json.loads(response_bytes)
        require(response["neutral_id"] == name and isinstance(response["text"], str)
                and response["text"].strip(), f"Empty or mismatched response: {name}")
        require(row["response_file_sha256"] == digest(response_bytes)
                and row["captured_text_sha256"] == digest(response["text"].encode()),
                f"Response binding differs: {name}")
    intent = read_json(root / "operator/intent.json")
    accounted = []
    for pair in intent["pairs"]:
        control = (root / f"inputs/{pair['control']}.md").read_bytes()
        mutation = (root / f"inputs/{pair['mutation']}.md").read_bytes()
        before, after = pair["before"].encode(), pair["after"].encode()
        require(control.count(before) == 1 and before != after
                and control.replace(before, after, 1) == mutation,
                f"Surgical mutation differs: {pair['pair']}")
        accounted.extend([pair["control"], pair["mutation"]])
    require(len(accounted) == len(entries) and set(accounted) == set(entries),
            "Pair accounting differs")
    return {"version": freeze["version"], "frozen_files": len(frozen),
            "inputs": len(entries), "responses": len(rows), "pairs": len(intent["pairs"]),
            "freeze_sha256": digest((root / "freeze.json").read_bytes())}


def main():
    versions = [verify_version(ROOT, 8), verify_version(ROOT / "identity-v2", 2)]
    v2 = ROOT / "identity-v2"
    intent = read_json(v2 / "operator/intent.json")
    require(intent["parent_freeze_sha256"] == digest((ROOT / "freeze.json").read_bytes()),
            "Parent freeze binding differs")
    require((ROOT / "common-prompt.txt").read_bytes() == (v2 / "common-prompt.txt").read_bytes(),
            "Assistance changed in v2")
    repair = intent["shared_repair"]
    for child, parent in intent["parent_mapping"].items():
        source = (ROOT / f"inputs/{parent}.md").read_bytes()
        require(intent["parent_inputs"][parent] == digest(source), "Parent input binding differs")
        before, after = repair["before"].encode(), repair["after"].encode()
        require(source.count(before) == 1 and source.replace(before, after, 1)
                == (v2 / f"inputs/{child}.md").read_bytes(), "Shared repair differs")
    print(json.dumps({"status": "PASS", "scope": "custody-and-mutation-conservation-only",
                      "versions": versions, "total_preserved_responses": 10}, indent=2))


if __name__ == "__main__":
    main()
