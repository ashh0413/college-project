"""Feature contract for the OULAD day-cutoff experiment."""

NUMERIC_FEATURES = [
    "num_of_prev_attempts",
    "studied_credits",
    "date_registration",
    "assessments_due",
    "assessments_submitted",
    "late_assessments",
    "assessment_weight_submitted",
    "assessment_score_mean",
    "assessment_score_min",
    "weighted_assessment_score",
    "assessment_completion_rate",
    "assessment_weight_completion_rate",
    "total_clicks",
    "active_days",
    "clicks_last_7d",
    "clicks_previous_7d",
    "clicks_last_14d",
    "active_days_last_14d",
    "days_since_last_activity",
    "click_trend_7d",
    "has_no_vle_activity",
]

CATEGORICAL_FEATURES = ["code_module", "presentation_season"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET_COLUMN = "adverse_outcome"

IDENTIFIER_COLUMNS = ["code_module", "code_presentation", "id_student"]
AUDIT_COLUMNS = ["gender", "age_band", "disability", "highest_education", "imd_band"]

FORBIDDEN_MODEL_COLUMNS = {
    "final_result",
    "adverse_outcome",
    "date_unregistration",
    "id_student",
    "gender",
    "age_band",
    "disability",
    "highest_education",
    "imd_band",
    "region",
}


def assert_feature_contract(columns) -> None:
    leaked = sorted(set(columns).intersection(FORBIDDEN_MODEL_COLUMNS))
    if leaked:
        raise ValueError(f"Forbidden or outcome columns selected as features: {leaked}")

