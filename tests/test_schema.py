import unittest

from student_success.schema import FEATURE_COLUMNS, assert_no_leakage


class LeakageTests(unittest.TestCase):
    def test_approved_features_pass(self):
        assert_no_leakage(FEATURE_COLUMNS)

    def test_outcome_feature_fails(self):
        with self.assertRaises(ValueError):
            assert_no_leakage(["attendance_pct", "end_term_gpa"])


if __name__ == "__main__":
    unittest.main()

