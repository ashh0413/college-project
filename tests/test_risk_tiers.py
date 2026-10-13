import unittest

import numpy as np

from student_success.train_oulad import capacity_threshold, tier_probabilities


class RiskTierTests(unittest.TestCase):
    def test_capacity_threshold_respects_limit(self):
        probability = np.array([0.1, 0.2, 0.3, 0.8, 0.9])
        target = np.array([0, 0, 1, 1, 1])
        result = capacity_threshold(probability, target, max_rate=0.4)
        self.assertLessEqual(result["selection_rate"], 0.4)
        self.assertEqual(result["recall"], 2 / 3)

    def test_tier_order(self):
        tiers = tier_probabilities(np.array([0.1, 0.5, 0.9]), 0.3, 0.7)
        self.assertEqual(tiers.tolist(), ["Low", "Medium", "High"])


if __name__ == "__main__":
    unittest.main()

