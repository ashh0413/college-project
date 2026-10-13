"""Dataset contract and leakage safeguards."""

ID_COLUMNS = ["student_id", "snapshot_date", "academic_year"]

NUMERIC_FEATURES = [
    "semester",
    "attendance_pct",
    "attendance_change_4w",
    "consecutive_absences",
    "assessment_avg",
    "assessment_change",
    "assignment_completion_pct",
    "late_submissions",
    "previous_gpa",
    "cumulative_gpa",
    "gpa_change",
    "backlog_count",
    "failed_subjects_previous",
    "credits_registered",
]

CATEGORICAL_FEATURES = ["programme"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES

OUTCOME_COLUMNS = [
    "end_term_failed_subjects",
    "end_term_gpa",
    "withdrew",
]

TARGET_COLUMN = "risk_label"
RISK_LEVELS = ["Low", "Medium", "High"]


def assert_no_leakage(feature_columns):
    """Fail if an end-of-term outcome or target is selected as a feature."""
    forbidden = set(OUTCOME_COLUMNS + [TARGET_COLUMN])
    leaked = sorted(forbidden.intersection(feature_columns))
    if leaked:
        raise ValueError(f"Outcome leakage detected in model features: {leaked}")

