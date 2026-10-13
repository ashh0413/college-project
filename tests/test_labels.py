import unittest

import pandas as pd

from student_success.labels import assign_risk_labels


POLICY = {
    "high_failed_subjects_min": 2,
    "high_end_term_gpa_below": 4.0,
    "medium_failed_subjects_min": 1,
    "medium_gpa_decline_at_least": 0.75,
}


class RiskLabelTests(unittest.TestCase):
    def test_assigns_expected_levels(self):
        frame = pd.DataFrame({
            "previous_gpa": [7.0, 7.0, 7.0, 7.0],
            "end_term_failed_subjects": [0, 1, 2, 0],
            "end_term_gpa": [7.2, 6.8, 5.0, 3.5],
            "withdrew": [False, False, False, False],
        })
        self.assertEqual(
            assign_risk_labels(frame, POLICY).tolist(),
            ["Low", "Medium", "High", "High"],
        )

    def test_withdrawal_is_high_risk_proxy(self):
        frame = pd.DataFrame({
            "previous_gpa": [7.0],
            "end_term_failed_subjects": [0],
            "end_term_gpa": [7.0],
            "withdrew": [True],
        })
        self.assertEqual(assign_risk_labels(frame, POLICY).iloc[0], "High")


if __name__ == "__main__":
    unittest.main()

