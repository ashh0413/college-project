"""Transparent support suggestions for faculty review."""

from __future__ import annotations


def suggest_interventions(student: dict) -> list[dict[str, str]]:
    """Map observable indicators to non-punitive support options."""
    suggestions: list[dict[str, str]] = []

    if student.get("attendance_pct") is not None and student["attendance_pct"] < 75:
        suggestions.append({
            "indicator": "Low attendance",
            "suggestion": "Review attendance records and arrange a supportive faculty check-in.",
        })
    if student.get("assignment_completion_pct") is not None and student["assignment_completion_pct"] < 70:
        suggestions.append({
            "indicator": "Incomplete assignments",
            "suggestion": "Discuss workload, deadlines, and access to study-planning support.",
        })
    if student.get("assessment_avg") is not None and student["assessment_avg"] < 50:
        suggestions.append({
            "indicator": "Low assessment average",
            "suggestion": "Consider subject tutoring, remedial material, or an academic-advisor meeting.",
        })
    if student.get("assessment_change") is not None and student["assessment_change"] <= -15:
        suggestions.append({
            "indicator": "Recent performance decline",
            "suggestion": "Verify the data and privately ask whether academic or wellbeing support is needed.",
        })

    return suggestions or [{
        "indicator": "No configured intervention trigger",
        "suggestion": "Continue routine monitoring; faculty judgement remains decisive.",
    }]


def suggest_oulad_interventions(student: dict) -> list[dict[str, str]]:
    """Return transparent OULAD support options for faculty consideration."""
    suggestions: list[dict[str, str]] = []

    if student.get("days_since_last_activity") is not None and student["days_since_last_activity"] >= 14:
        suggestions.append({
            "indicator": "No recent online learning activity",
            "suggestion": "Check whether access, study-planning, or module-engagement support is needed.",
        })
    completion = student.get("assessment_completion_rate")
    if completion is not None and completion == completion and completion < 1:
        suggestions.append({
            "indicator": "A due assessment was not completed by the cutoff",
            "suggestion": "Review the assessment record and discuss deadlines and academic support options.",
        })
    score = student.get("assessment_score_mean")
    if score is not None and score == score and score < 50:
        suggestions.append({
            "indicator": "Low available assessment score",
            "suggestion": "Offer subject-specific feedback, tutoring, or a study-skills referral.",
        })
    if student.get("click_trend_7d") is not None and student["click_trend_7d"] <= -50:
        suggestions.append({
            "indicator": "Recent online engagement decline",
            "suggestion": "Verify the activity pattern and consider a supportive check-in.",
        })
    if student.get("num_of_prev_attempts") is not None and student["num_of_prev_attempts"] > 0:
        suggestions.append({
            "indicator": "Previous module attempt recorded",
            "suggestion": "Consider an academic-advisor review of the student's current study plan.",
        })

    return suggestions or [{
        "indicator": "No rule-based support trigger",
        "suggestion": "Use the broader academic context and faculty judgement; continue routine monitoring.",
    }]

