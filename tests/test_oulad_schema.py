import unittest

from student_success.oulad_schema import FEATURE_COLUMNS, assert_feature_contract


class OuladFeatureContractTests(unittest.TestCase):
    def test_model_features_pass(self):
        assert_feature_contract(FEATURE_COLUMNS)

    def test_outcome_is_rejected(self):
        with self.assertRaises(ValueError):
            assert_feature_contract(FEATURE_COLUMNS + ["final_result"])

    def test_sensitive_attribute_is_rejected(self):
        with self.assertRaises(ValueError):
            assert_feature_contract(FEATURE_COLUMNS + ["gender"])


if __name__ == "__main__":
    unittest.main()

