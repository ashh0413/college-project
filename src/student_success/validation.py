"""Lightweight validation for student snapshot data."""

from __future__ import annotations

import pandas as pd

from .schema import FEATURE_COLUMNS, ID_COLUMNS


PERCENT_COLUMNS = ["attendance_pct", "assignment_completion_pct", "assessment_avg"]
NON_NEGATIVE_COLUMNS = [
    "consecutive_absences",
    "late_submissions",
    "backlog_count",
    "failed_subjects_previous",
    "credits_registered",
]


def validate_snapshot_data(frame: pd.DataFrame, require_outcomes: bool = False) -> list[str]:
    """Return human-readable data issues; do not silently repair source data."""
    issues: list[str] = []
    required = set(ID_COLUMNS + FEATURE_COLUMNS)
    if require_outcomes:
        required.update({"end_term_failed_subjects", "end_term_gpa", "withdrew"})

    missing = sorted(required.difference(frame.columns))
    if missing:
        issues.append(f"Missing required columns: {missing}")
        return issues

    duplicate_count = int(frame.duplicated(["student_id", "snapshot_date"]).sum())
    if duplicate_count:
        issues.append(f"Found {duplicate_count} duplicate student/snapshot rows")

    for column in PERCENT_COLUMNS:
        invalid = frame[column].dropna().between(0, 100, inclusive="both") == False  # noqa: E712
        if invalid.any():
            issues.append(f"{column} contains {int(invalid.sum())} values outside 0–100")

    for column in NON_NEGATIVE_COLUMNS:
        invalid_count = int((frame[column].dropna() < 0).sum())
        if invalid_count:
            issues.append(f"{column} contains {invalid_count} negative values")

    invalid_dates = pd.to_datetime(frame["snapshot_date"], errors="coerce").isna().sum()
    if invalid_dates:
        issues.append(f"snapshot_date contains {int(invalid_dates)} invalid or missing dates")

    return issues

