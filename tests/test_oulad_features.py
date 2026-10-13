import tempfile
import unittest
from pathlib import Path

import pandas as pd

from student_success.oulad_features import build_base_cohort, build_assessment_features


class OuladFeatureTests(unittest.TestCase):
    def test_excludes_withdrawal_known_before_cutoff(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pd.DataFrame({
                "code_module": ["AAA", "AAA"],
                "code_presentation": ["2014J", "2014J"],
                "id_student": [1, 2],
                "final_result": ["Withdrawn", "Fail"],
            }).to_csv(root / "studentInfo.csv", index=False)
            pd.DataFrame({
                "code_module": ["AAA", "AAA"],
                "code_presentation": ["2014J", "2014J"],
                "id_student": [1, 2],
                "date_registration": [-10, -10],
                "date_unregistration": [20, None],
            }).to_csv(root / "studentRegistration.csv", index=False)

            cohort = build_base_cohort(root, cutoff_day=40)
            self.assertEqual(cohort["id_student"].tolist(), [2])

    def test_uses_only_due_and_observed_assessments(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pd.DataFrame({
                "code_module": ["AAA", "AAA"],
                "code_presentation": ["2014J", "2014J"],
                "id_assessment": [10, 11],
                "assessment_type": ["TMA", "TMA"],
                "date": [20, 60],
                "weight": [10.0, 20.0],
            }).to_csv(root / "assessments.csv", index=False)
            pd.DataFrame({
                "id_assessment": [10, 11],
                "id_student": [1, 1],
                "date_submitted": [21, 30],
                "is_banked": [0, 0],
                "score": [80.0, 99.0],
            }).to_csv(root / "studentAssessment.csv", index=False)

            features = build_assessment_features(root, cutoff_day=40)
            self.assertEqual(features.loc[0, "assessments_submitted"], 1)
            self.assertEqual(features.loc[0, "assessment_score_mean"], 80.0)
            self.assertEqual(features.loc[0, "late_assessments"], 1)


if __name__ == "__main__":
    unittest.main()

