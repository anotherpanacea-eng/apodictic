import copy
import unittest
import summarize as agg


def cells():
    return {(model, family, member, arm, repeat): {"hit": member == "broken", "continuity_fp": 0, "all_fp": 0, "invention": False}
            for model in agg.score.exp.MODELS for family in agg.score.exp.FAMILIES
            for member in ("clean", "broken") for arm in ("baseline", "corrective") for repeat in (1, 2)}


class SummaryTests(unittest.TestCase):
    def test_ceiling_is_not_improvement(self):
        result = agg.disposition(cells(), agg.score.exp.MODELS[0])
        self.assertEqual(result["disposition"], "no_demonstrated_improvement")
        self.assertEqual(result["delta"], 0)

    def test_primary_improvement_without_guard_loss(self):
        data = cells()
        model = agg.score.exp.MODELS[0]
        data[(model, "continuity-contradiction", "clean", "baseline", 1)]["continuity_fp"] = 1
        result = agg.disposition(data, model)
        self.assertEqual(result["disposition"], "recommend_larger_fresh_test")
        self.assertEqual(result["delta"], 1)

    def test_lost_transfer_hit_blocks_improvement(self):
        data = cells()
        model = agg.score.exp.MODELS[0]
        data[(model, "continuity-contradiction", "clean", "baseline", 1)]["continuity_fp"] = 1
        data[(model, "pov-break", "broken", "corrective", 1)]["hit"] = False
        self.assertEqual(agg.disposition(data, model)["disposition"], "guard_failure_observed")

    def test_missing_cell_is_unresolved(self):
        data = cells()
        model = agg.score.exp.MODELS[0]
        data[(model, "orphan-scene", "broken", "corrective", 2)]["hit"] = None
        self.assertEqual(agg.disposition(data, model)["disposition"], "incomplete_or_unresolved")

    def test_disagreement_is_not_majority_truth(self):
        a = {"hit": True, "continuity_fp": 0}
        b = {"hit": False, "continuity_fp": 0}
        self.assertEqual(agg.agreement([a, b]), {"hit": None, "continuity_fp": 0})


if __name__ == "__main__":
    unittest.main()
