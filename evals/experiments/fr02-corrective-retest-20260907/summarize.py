"""Conservative FR-02 aggregation: preserve disagreement and missing cells."""
import argparse
from pathlib import Path
import json
import score

DECISION_VERSION = "fr02-decision/1"


def metrics(grade):
    if grade is None or grade["central_key_ambiguity"]:
        return {"hit": None, "continuity_fp": None, "all_fp": None, "invention": None}
    unclear = any(f["severity"] == "unclear" for f in grade["unsupported_findings"])
    severe = [f for f in grade["unsupported_findings"] if f["severity"] in ("Must-Fix", "Should-Fix")]
    hit = {"yes": True, "no": False, "unresolved": None, "not_applicable": None}[grade["planted_mechanism"]]
    return {"hit": hit, "continuity_fp": None if unclear else sum(f["kind"] == "continuity" for f in severe),
            "all_fp": None if unclear else len(severe),
            "invention": bool(grade["fabricated_content"] or grade["mandatory_invention"])}


def agreement(values):
    return {key: values[0][key] if all(v[key] == values[0][key] for v in values) else None for key in values[0]}


def pair_success(clean, broken):
    if clean["continuity_fp"] is None or broken["hit"] is None:
        return None
    return clean["continuity_fp"] == 0 and broken["hit"]


def disposition(cells, model):
    def get(family, member, arm, repeat):
        return cells[(model, family, member, arm, repeat)]
    primary = {arm: [pair_success(get("continuity-contradiction", "clean", arm, n),
                                  get("continuity-contradiction", "broken", arm, n)) for n in (1, 2)]
               for arm in ("baseline", "corrective")}
    losses, new_fp, invention, unresolved = [], [], [], []
    for family in score.exp.FAMILIES:
        for repeat in (1, 2):
            baseline_hit = get(family, "broken", "baseline", repeat)["hit"]
            corrective_hit = get(family, "broken", "corrective", repeat)["hit"]
            if baseline_hit is None or corrective_hit is None:
                unresolved.append({"family": family, "repeat": repeat, "guard": "mechanism_hit"})
            elif baseline_hit and not corrective_hit:
                losses.append({"family": family, "repeat": repeat})
            if family != "continuity-contradiction":
                b = get(family, "clean", "baseline", repeat)["all_fp"]
                c = get(family, "clean", "corrective", repeat)["all_fp"]
                if b is None or c is None:
                    unresolved.append({"family": family, "repeat": repeat, "guard": "clean_false_positives"})
                elif c > b:
                    new_fp.append({"family": family, "repeat": repeat, "baseline": b, "corrective": c})
            for member in ("clean", "broken"):
                b = get(family, member, "baseline", repeat)["invention"]
                c = get(family, member, "corrective", repeat)["invention"]
                if b is None or c is None:
                    unresolved.append({"family": family, "member": member, "repeat": repeat, "guard": "invention"})
                elif c and not b:
                    invention.append({"family": family, "member": member, "repeat": repeat})
    primary_complete = all(v is not None for values in primary.values() for v in values)
    counts = {arm: {"success": values.count(True), "failure": values.count(False), "unresolved": values.count(None)}
              for arm, values in primary.items()}
    delta = counts["corrective"]["success"] - counts["baseline"]["success"] if primary_complete else None
    if invention:
        result = "hard_failure_observed"
    elif losses or new_fp:
        result = "guard_failure_observed"
    elif not primary_complete or unresolved:
        result = "incomplete_or_unresolved"
    elif delta >= 1:
        result = "recommend_larger_fresh_test"
    else:
        result = "no_demonstrated_improvement"
    return {"primary": primary, "counts": counts, "delta": delta, "disposition": result,
            "lost_baseline_hits": losses, "increased_transfer_false_positives": new_fp,
            "new_invention_flags": invention, "unresolved_guards": unresolved}


def summarize(root):
    manifest = score.verify(root)
    summarizer_hash = score.exp.digest(Path(__file__).read_bytes())
    if summarizer_hash != manifest["artifacts"]["frozen/summarize.py"]:
        raise ValueError("Run the frozen summarizer; implementation differs from scoring freeze")
    by_id = {r["id"]: r for r in manifest["mapping"]}
    grades = {}
    invalid = []
    receipt_hashes = {}
    for row in manifest["runs"]:
        grade, error = score.grade_receipt(root, row)
        grades[(row["anonymous_id"], row["model"])] = grade
        if error:
            invalid.append({"id": row["id"], "error": error})
        folder = score.exp.selected_folder(root, row)
        if (folder / "receipt.json").exists():
            receipt_hashes[row["id"]] = score.exp.digest((folder / "receipt.json").read_bytes())
    if len(receipt_hashes) != len(manifest["runs"]):
        raise ValueError("Final aggregation requires every scorer call to have a sealed terminal receipt")
    existing = root / "aggregate.json"
    if existing.exists():
        prior = score.exp.read_json(existing)
        if prior.get("summarizer_sha256") != summarizer_hash or prior.get("decision_version") != DECISION_VERSION or prior.get("score_receipt_sha256") != receipt_hashes or prior.get("scorer_manifest_sha256") != score.exp.digest((root / "manifest.json").read_bytes()):
            raise ValueError("Existing aggregate belongs to different inputs or implementation; never overwrite")
        print(json.dumps({"unchanged_aggregate": str(existing), "valid_scores": prior["valid_scores"]}))
        return prior
    profiles = {model: {} for model in score.SCORERS}
    profiles["agreement"] = {}
    disagreements = []
    component_scores = {scorer: {} for scorer in score.SCORERS}
    for anonymous, record in by_id.items():
        key = tuple(record[k] for k in ("model", "family", "member", "arm", "repeat"))
        observations = []
        for scorer in score.SCORERS:
            grade = grades[(anonymous, scorer)]
            value = metrics(grade)
            profiles[scorer][key] = value
            observations.append(value)
            if grade:
                component_scores[scorer][anonymous] = {"components": grade["components"], "total": sum(grade["components"].values())}
        profiles["agreement"][key] = agreement(observations)
        if observations[0] != observations[1]:
            disagreements.append({"id": anonymous, "metrics": dict(zip(score.SCORERS, observations))})
    decisions = {profile: {model: disposition(cells, model) for model in score.exp.MODELS}
                 for profile, cells in profiles.items()}
    result = {"schema": "fr02-aggregate/1", "decision_version": DECISION_VERSION,
              "summarizer_sha256": summarizer_hash, "created_utc": score.exp.now(),
              "scorer_manifest_sha256": score.exp.digest((root / "manifest.json").read_bytes()),
              "score_receipt_sha256": receipt_hashes,
              "planned_productions": len(by_id), "planned_scores": len(manifest["runs"]),
              "valid_scores": len(manifest["runs"]) - len(invalid), "invalid_or_missing_scores": invalid,
              "decisions": decisions, "disagreements": disagreements,
              "component_scores": component_scores,
              "limits": ["same-provider advisory scoring", "two repetitions of four existing synthetic pairs",
                         "no human key license or whole-suite M2 pass", "descriptive matched-index comparisons, not a causal estimate"]}
    score.exp.write_json(root / "aggregate.json", result)
    print(json.dumps({"valid_scores": result["valid_scores"], "planned_scores": result["planned_scores"],
                      "agreement": decisions["agreement"], "disagreements": len(disagreements)}, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    summarize(args.root.resolve())
