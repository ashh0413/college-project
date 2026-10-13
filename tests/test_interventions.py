import unittest

from student_success.interventions import suggest_oulad_interventions


class InterventionTests(unittest.TestCase):
    def test_multiple_support_options_are_transparent(self):
        options = suggest_oulad_interventions({
            "days_since_last_activity": 20,
            "assessment_completion_rate": 0.5,
            "assessment_score_mean": 40,
            "click_trend_7d": -60,
            "num_of_prev_attempts": 1,
        })
        self.assertEqual(len(options), 5)
        self.assertTrue(all("indicator" in item and "suggestion" in item for item in options))

    def test_no_trigger_does_not_invent_problem(self):
        options = suggest_oulad_interventions({
            "days_since_last_activity": 2,
            "assessment_completion_rate": 1.0,
            "assessment_score_mean": 80,
            "click_trend_7d": 10,
            "num_of_prev_attempts": 0,
        })
        self.assertEqual(options[0]["indicator"], "No rule-based support trigger")


if __name__ == "__main__":
    unittest.main()

