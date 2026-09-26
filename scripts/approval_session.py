#!/usr/bin/env python3
"""Author session adapter for the approval ledger (stdlib only)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from approval_graph import ApprovalGraphError, adjudicate, session_snapshot


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate request key: {key}")
        value[key] = item
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--show", action="store_true", help="recover and present current author state")
    operation.add_argument("--decision", type=Path, help="UTF-8 JSON request for one explicit author decision")
    args = parser.parse_args(argv)
    try:
        if args.show:
            result = session_snapshot(args.project)
        else:
            request = json.loads(args.decision.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
            result = adjudicate(args.project, request)
    except ApprovalGraphError as exc:
        result = {"error": exc.code, "message": exc.message, "committed": exc.committed, "record_id": exc.record_id}
    except (OSError, UnicodeError, ValueError) as exc:
        result = {"error": "INVALID-REQUEST", "message": str(exc), "committed": False, "record_id": None}
    # ASCII transport is intentional: console encodings must not turn a durable
    # decision into a spurious UnicodeEncodeError acknowledgement failure.
    print(json.dumps(result, ensure_ascii=True, allow_nan=False))
    return 1 if "error" in result else 0


if __name__ == "__main__":
    raise SystemExit(main())
